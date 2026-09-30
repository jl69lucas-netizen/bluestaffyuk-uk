# tests/py/test_spend_guard_sources.py — the two paid sources added for London's page run
# (user, 2026-09-30, chat: "SERP + volumes + backlinks"). keyword_volume and backlinks are
# guarded like serp_google and ai_engines, each with a conservative per-call estimate that
# the guard never counts below, and the caps ($0.50 per page per day, $1.00 total) stand.
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import query_augment as Q  # noqa: E402

SETTINGS = {"query_budget_usd": 0.5, "query_total_budget_usd": 1.0, "query_typical_call_usd": 0.01}
DAY = "2026-09-30"
NOW = f"{DAY}T10:00:00Z"
NEW = ("keyword_volume", "backlinks")


def make_root(tmp_path, log=None):
    (tmp_path / "data/queries").mkdir(parents=True)
    (tmp_path / "data/settings.json").write_text(json.dumps(SETTINGS))
    (tmp_path / "data/queries/spend.json").write_text(json.dumps(log or []))
    return tmp_path


def run(root, *args):
    return subprocess.run([sys.executable, str(REPO / "scripts/query_augment.py"),
                           "--root", str(root), *args], capture_output=True, text=True)


def test_the_new_sources_are_paid_and_the_old_ones_stay():
    for s in ("serp_google", "ai_engines") + NEW:
        assert s in Q.PAID_SOURCES
    assert "serp_bing" not in Q.PAID_SOURCES and "threads" not in Q.PAID_SOURCES


def test_the_new_sources_are_not_question_sources():
    # Volumes and backlinks never feed the question merge.
    for s in NEW:
        assert s not in Q.CANDIDATE_SOURCES


@pytest.mark.parametrize("source", NEW)
def test_each_new_source_has_a_conservative_estimate(source):
    est = Q.SOURCE_ESTIMATE_USD[source]
    assert isinstance(est, float) and 0.01 < est <= 0.25


@pytest.mark.parametrize("source", NEW)
def test_the_guard_never_counts_a_new_source_below_its_estimate(tmp_path, source):
    root = make_root(tmp_path)
    _, typical, _ = Q.spend_basis(source, root)
    assert typical == Q.SOURCE_ESTIMATE_USD[source]
    # a cheaper logged call does not lower it; a dearer one raises it
    Q.record("x", source, "e", 0.001, root, now=NOW)
    assert Q.spend_basis(source, root)[1] == Q.SOURCE_ESTIMATE_USD[source]
    Q.record("x", source, "e", 0.3, root, now=NOW)
    assert Q.spend_basis(source, root)[1] == 0.3


def test_serp_google_keeps_its_typical_call(tmp_path):
    root = make_root(tmp_path)
    assert Q.spend_basis("serp_google", root)[1] == 0.01


@pytest.mark.parametrize("source", NEW)
def test_preflight_proceeds_then_is_cached_by_a_saved_response(tmp_path, source):
    root = make_root(tmp_path)
    assert Q.preflight("m", source, root, today=DAY) == Q.EXIT_OK
    d = root / "data/queries/raw/m"
    d.mkdir(parents=True)
    (d / f"{source}.response.json").write_text("{}")
    assert Q.preflight("m", source, root, today=DAY) == Q.EXIT_CACHED


@pytest.mark.parametrize("source", NEW)
def test_preflight_refuses_over_the_page_cap_at_the_estimate(tmp_path, source):
    # 0.46 spent today: a 0.01 SERP call still fits the 0.50 page cap, the estimate does not
    root = make_root(tmp_path, [{"ts": NOW, "slug": "m", "source": "ai_engines",
                                 "endpoint": "e", "cost_usd": 0.46}])
    assert Q.preflight("m", "serp_google", root, today=DAY) == Q.EXIT_OK
    assert Q.preflight("m", source, root, today=DAY) == Q.EXIT_BUDGET


@pytest.mark.parametrize("source", NEW)
def test_preflight_refuses_over_the_total_cap_at_the_estimate(tmp_path, source):
    root = make_root(tmp_path, [{"ts": "2026-09-01T00:00:00Z", "slug": "a",
                                 "source": "ai_engines", "endpoint": "e", "cost_usd": 0.96}])
    assert Q.preflight("m", "serp_google", root, today=DAY) == Q.EXIT_OK
    assert Q.preflight("m", source, root, today=DAY) == Q.EXIT_BUDGET


@pytest.mark.parametrize("source", NEW)
def test_cli_preflight_record_and_budget_accept_the_new_sources(tmp_path, source):
    root = make_root(tmp_path)
    assert run(root, "--preflight", "m", "--source", source, "--today", DAY).returncode == 0
    r = run(root, "--record", "m", "--source", source, "--endpoint", "e", "--cost", "0.02")
    assert r.returncode == 0, r.stderr
    assert json.loads((root / "data/queries/spend.json").read_text())[0]["source"] == source
    b = run(root, "--budget", source)
    assert b.returncode == 0, b.stderr
    assert f"typical call {Q.SOURCE_ESTIMATE_USD[source]}" in b.stdout


def test_cli_record_still_refuses_an_unknown_source(tmp_path):
    root = make_root(tmp_path)
    r = run(root, "--record", "m", "--source", "volumes", "--endpoint", "e", "--cost", "0.02")
    assert r.returncode == 2
    assert json.loads((root / "data/queries/spend.json").read_text()) == []


def test_the_repo_caps_are_unchanged():
    s = json.loads((REPO / "data/settings.json").read_text())
    assert s["query_budget_usd"] == 0.5 and s["query_total_budget_usd"] == 1.0
