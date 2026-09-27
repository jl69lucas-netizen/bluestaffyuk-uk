# tests/py/test_not_fetched_lint.py — scripts/not_fetched_lint.py (parity build Task 21; audit
# rows 1f.2, 5d): a NOT FETCHED in a new or changed board, query or research file names its
# barrier. Files that already carried a bare one are grandfathered by content hash in
# data/quality/not-fetched-baseline.json; editing one ends its exemption.
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import not_fetched_lint as L  # noqa: E402

SCRIPT = ROOT / "scripts" / "not_fetched_lint.py"


@pytest.mark.parametrize("text", [
    "GSC: NOT FETCHED — the property is unverified.",
    "GSC: NOT FETCHED – the property is unverified.",
    "GSC: `NOT FETCHED` — the property is unverified.",
    "**NOT FETCHED**: no raw HTML was saved.",
    "Word target NOT FETCHED (no competitor scan yet).",
])
def test_a_named_barrier_passes_in_text(text):
    assert L.bare_in_text(text) == []


@pytest.mark.parametrize("text", [
    "GSC: NOT FETCHED.",
    "GSC is NOT FETCHED until project 6.",
    "| Bing | NOT FETCHED |",
    "NOT FETCHED —",
])
def test_a_bare_token_is_found_in_text(text):
    assert len(L.bare_in_text(text)) == 1


def test_json_accepts_an_inline_barrier_or_a_sibling_reason():
    ok = {"a": "NOT FETCHED — the host timed out",
          "b": {"status": "NOT FETCHED", "reason": "homepage timed out"},
          "c": {"status": "NOT FETCHED", "barrier": "login wall"},
          "d": [{"proof": "NOT FETCHED — certificate not on file"}]}
    assert L.bare_in_json(ok) == []


def test_json_finds_every_bare_value_with_its_path():
    bad = {"sources": {"ai_engines": "NOT FETCHED", "bank": "ok"},
           "pages": [{"status": "NOT FETCHED", "reason": ""}]}
    assert L.bare_in_json(bad) == ["$.sources.ai_engines", "$.pages[0].status"]


def _root(tmp_path, files, baseline=None):
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    if baseline is not None:
        q = tmp_path / "data/quality"
        q.mkdir(parents=True, exist_ok=True)
        (q / "not-fetched-baseline.json").write_text(json.dumps(baseline))
    return tmp_path


def test_a_new_file_with_a_bare_token_fails(tmp_path):
    root = _root(tmp_path, {"docs/research/new.md": "Bing: NOT FETCHED.\n"}, {"files": {}})
    probs, examined, kept = L.lint(root)
    assert probs == ["docs/research/new.md:1  a bare NOT FETCHED — name the barrier: "
                     "`NOT FETCHED — <barrier>`"]
    assert examined == 1 and kept == 0


def test_an_unchanged_grandfathered_file_passes_and_an_edited_one_fails(tmp_path):
    text = "Bing: NOT FETCHED.\n"
    root = _root(tmp_path, {"docs/research/old.md": text},
                 {"files": {"docs/research/old.md": L.sha(text.encode())}})
    assert L.lint(root) == ([], 1, 1)
    (root / "docs/research/old.md").write_text(text + "More notes.\n")
    probs, _, kept = L.lint(root)
    assert len(probs) == 1 and kept == 0


def test_the_scope_is_boards_queries_and_research_only(tmp_path):
    root = _root(tmp_path, {"docs/reference/x.md": "NOT FETCHED.\n",
                            "data/queries/cache/s/1.html": "NOT FETCHED.\n",
                            "data/boards/inbox/x.json": '{"a": "NOT FETCHED"}',
                            "data/boards/x.json": '{"a": "NOT FETCHED"}',
                            "data/queries/raw/s/threads.json": '{"status": "NOT FETCHED"}'},
                 {"files": {}})
    probs, examined, _ = L.lint(root)
    assert examined == 2
    assert sorted(p.split("  ")[0] for p in probs) == ["data/boards/x.json:$.a",
                                                       "data/queries/raw/s/threads.json:$.status"]


def test_an_unreadable_json_file_is_a_problem(tmp_path):
    root = _root(tmp_path, {"data/queries/x.json": "{NOT FETCHED"}, {"files": {}})
    probs, _, _ = L.lint(root)
    assert probs and "not valid JSON" in probs[0]


def test_write_baseline_refuses_to_overwrite(tmp_path):
    root = _root(tmp_path, {"docs/research/old.md": "NOT FETCHED.\n"}, {"files": {}})
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--write-baseline"],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "exists" in r.stderr


def test_write_baseline_then_check_passes(tmp_path):
    root = _root(tmp_path, {"docs/research/old.md": "NOT FETCHED.\n",
                            "docs/research/clean.md": "NOT FETCHED — named.\n"})
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--write-baseline"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    base = json.loads((root / "data/quality/not-fetched-baseline.json").read_text())
    assert list(base["files"]) == ["docs/research/old.md"]
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)], capture_output=True, text=True)
    assert r.returncode == 0 and "examined 2 files (1 grandfathered); 0 problems" in r.stdout


def test_a_missing_baseline_is_not_a_pass(tmp_path):
    root = _root(tmp_path, {"docs/research/clean.md": "NOT FETCHED — named.\n"})
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)], capture_output=True, text=True)
    assert r.returncode == 2 and "baseline" in r.stdout + r.stderr


def test_the_real_tree_passes():
    probs, examined, _ = L.lint(ROOT)
    assert examined > 0 and probs == []


def test_the_question_file_query_augment_writes_names_every_barrier(tmp_path):
    import query_augment as Q
    from test_query_augment import make_root, seed, write_raw
    root = make_root(tmp_path)
    seed(root)
    write_raw(root, "m", "threads", {"source": "threads", "status": "NOT FETCHED",
                                     "reason": "reddit refused the headless browser",
                                     "questions": []})
    data, _ = Q.build("m", "location", "blue staffy puppies manchester", "/uk-locations/m/",
                      root, "2026-09-26")
    assert L.bare_in_json(data) == []
    assert data["sources"]["threads"] == "NOT FETCHED — reddit refused the headless browser"
    assert data["sources"]["ai_engines"] == "NOT FETCHED — no data/queries/raw/m/ai_engines.json"
