"""`scripts/gate_page.py` — `npm run gate:page -- <slug>`: every page gate, run twice, diffed.

The brief's gate-integrity rule: one clean run proves nothing, because the same input has
produced different verdicts. BlueStaffyUK ran its gates twice only at project close, by hand;
project 5 has ~30 pages, each its own gate target. This runner makes "twice" the default and a
disagreement a failure (rules/gates.md `run-every-gate-twice` is backed by this file).

The orchestration tests replace the audits with a scripted runner so they pin behaviour, not
today's pages. The last test runs the real audits twice on a real built page and asserts only
what must hold on any page: two runs, recorded, and identical.
"""
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import gate_page as GP  # noqa: E402

CLEAN = {
    "dup-body": (1, {"pages": 40, "findings": [{"a": "other", "b": "another", "words": 20, "run": "x"}]}),
    "dup-headers": (1, {"pages": 40, "findings": [{"kind": "exact", "text": "h", "pages": ["a", "b"]}]}),
    "final-audit": (0, {"pages": [{"slug": "p", "status": "PASS", "checks": []}]}),
    "hardening": (0, {"pages": [{"slug": "p/", "status": "OK", "checks": []}]}),
    "aeo": (0, {"pages": [{"slug": "p", "findings": []}], "errors": 0, "warns": 0}),
    "evidence": (0, {"pages": [{"slug": "p", "findings": []}], "errors": 0, "warns": 0}),
    "board": (0, {"exit": 0, "lines": ["board-gate p [build] — 9 sections examined", "0 FAIL · 0 WARN"]}),
}


def scripted(overrides=None, second=None):
    """A runner answering from CLEAN, with per-step overrides, and different answers on the
    second call of a step when `second` names it."""
    calls = {}

    def runner(step, route, profile):
        calls[step] = calls.get(step, 0) + 1
        if second and step in second and calls[step] == 2:
            return second[step]
        return (overrides or {}).get(step, CLEAN[step])
    return runner


def passing_check_all(root):
    return 0, []


def step(report, name):
    return next(s for s in report["steps"] if s["step"] == name)


def run(runner, record=False):
    return GP.gate("p", "p", "location", runner=runner, record=record)


def test_a_clean_page_passes_both_runs():
    report = run(scripted())
    assert report["verdict"] == "PASS" and report["runs"] == 2 and report["identical"] is True
    # "p" is a new page, so the board gate runs after the six audits (Task 28a).
    assert [s["step"] for s in report["steps"]] == list(GP.AUDIT_STEPS) + [GP.BOARD_STEP]
    assert all(s["ok"] == [True, True] for s in report["steps"])


def test_the_site_wide_dup_audit_judges_only_findings_that_name_the_page():
    # The audit exits 1 on the pair (other, another); that pair is theirs, not this page's.
    report = run(scripted())
    dup = {s["step"]: s for s in report["steps"]}
    assert dup["dup-body"]["ok"] == [True, True] and dup["dup-headers"]["ok"] == [True, True]
    mine = {"dup-body": (1, {"pages": 40, "findings": [{"a": "p", "b": "x", "words": 14, "run": "r"}]}),
            "dup-headers": (1, {"pages": 40, "findings": [{"kind": "exact", "text": "t", "pages": ["p", "q"]}]})}
    report = run(scripted(mine))
    steps = {s["step"]: s for s in report["steps"]}
    assert steps["dup-body"]["problems"] == [1, 1] and steps["dup-headers"]["problems"] == [1, 1]
    assert report["verdict"] == "FAIL"


def test_the_report_records_the_commit_it_judged():
    report = run(scripted())
    sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True,
                         text=True).stdout.strip()
    assert report["head"] in (sha, sha + "-dirty")
    assert GP.gate("p", "p", "location", runner=scripted(), record=False, head="abc")["head"] == "abc"


def test_the_report_records_the_content_hash_of_the_page_it_judged(tmp_path):
    import rendered_changes as RC
    html = "<main><p>page</p></main><style>x{}</style>"
    (tmp_path / "dist/p").mkdir(parents=True)
    (tmp_path / "dist/p/index.html").write_text(html, encoding="utf-8")
    report = GP.gate("p", "p", "location", runner=scripted(), record=False, root=tmp_path,
                     head="abc")
    assert report["page_hash"] == RC.content_hash(html)
    assert GP.gate("q", "q", "location", runner=scripted(), record=False, root=tmp_path,
                   head="abc")["page_hash"] is None


def test_git_head_marks_a_dirty_tree_and_is_none_outside_git(tmp_path):
    assert GP.git_head(tmp_path) is None
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    git = lambda *a: subprocess.run(["git", "-C", str(tmp_path), *a], check=True, env=env,
                                    capture_output=True)
    git("init", "-q")
    (tmp_path / "f").write_text("1", encoding="utf-8")
    git("add", "f")
    git("commit", "-qm", "x")
    sha = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], capture_output=True,
                         text=True).stdout.strip()
    assert GP.git_head(tmp_path) == sha
    (tmp_path / "f").write_text("2", encoding="utf-8")
    assert GP.git_head(tmp_path) == sha + "-dirty"


def test_git_head_counts_tracked_changes_only_as_page_run_record_does(tmp_path):
    # One definition of dirty (page_run_record.dirty_tracked): a stray untracked file, a new
    # dated scorecard, a same-day scorecard re-written by the render suite, a page-run record
    # or a report is not a change to the page the gate judged.
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    git = lambda *a: subprocess.run(["git", "-C", str(tmp_path), *a], check=True, env=env,
                                    capture_output=True)
    cards = tmp_path / "data/quality/scorecards"
    cards.mkdir(parents=True)
    (cards / "comp-2026-09-27.json").write_text("{}", encoding="utf-8")
    (tmp_path / "src.astro").write_text("1", encoding="utf-8")
    git("init", "-q")
    git("add", "-A")
    git("commit", "-qm", "x")
    sha = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], capture_output=True,
                         text=True).stdout.strip()
    (tmp_path / "stray.txt").write_text("x", encoding="utf-8")
    (cards / "comp-2026-09-28.json").write_text("{}", encoding="utf-8")
    (cards / "comp-2026-09-27.json").write_text('{"rerun": 1}', encoding="utf-8")
    assert GP.git_head(tmp_path) == sha
    (tmp_path / "src.astro").write_text("2", encoding="utf-8")
    assert GP.git_head(tmp_path) == sha + "-dirty"


def test_a_failing_audit_fails_the_page():
    report = run(scripted({"aeo": (1, {"pages": [{"slug": "p", "findings": [
        {"severity": "WARN", "message": "no binomial"}]}], "errors": 0, "warns": 1})}))
    aeo = next(s for s in report["steps"] if s["step"] == "aeo")
    assert aeo["ok"] == [False, False] and aeo["problems"] == [1, 1] and aeo["identical"]
    assert report["verdict"] == "FAIL"


def test_a_step_that_answers_differently_the_second_time_fails_even_when_both_pass():
    flip = {"evidence": (0, {"pages": [{"slug": "p", "findings": []}], "errors": 0, "warns": 0,
                             "note": "a different answer"})}
    report = run(scripted(second=flip))
    ev = next(s for s in report["steps"] if s["step"] == "evidence")
    assert ev["ok"] == [True, True] and ev["identical"] is False
    assert report["verdict"] == "FAIL" and report["identical"] is False


def test_an_audit_that_writes_no_report_is_a_failure_not_a_pass():
    report = run(scripted({"hardening": (0, None)}))
    h = next(s for s in report["steps"] if s["step"] == "hardening")
    assert h["ok"] == [False, False]


def test_the_page_run_record_is_a_step_unless_skipped(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "p"}]), encoding="utf-8")
    report = GP.gate("p", "uk-locations/p", "location", runner=scripted(), record=True,
                     root=tmp_path, check_all=passing_check_all)
    rec = step(report, GP.RECORD_STEP)
    assert rec["ok"] == [False, False]
    assert report["verdict"] == "FAIL", "a page with no data/page-runs record never passes the full gate"
    assert GP.gate("p", "uk-locations/p", "location", runner=scripted(), record=False,
                   root=tmp_path)["verdict"] == "PASS"


def test_a_new_page_whose_session_open_is_out_of_order_fails_the_gate(tmp_path):
    (tmp_path / "data/page-runs").mkdir(parents=True)
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "p"}]), encoding="utf-8")
    (tmp_path / "data/page-runs/p.json").write_text(json.dumps({
        "slug": "p", "session_open": {"ran_on": "2026-09-27", "skills": [
            "bsuk-location-page-builder", "grill-me", "superpowers:writing-plans"]}}),
        encoding="utf-8")
    report = GP.gate("p", "uk-locations/p", "location", runner=scripted(), record=True,
                     root=tmp_path, check_all=passing_check_all)
    rec = step(report, GP.RECORD_STEP)
    assert rec["ok"] == [False, False] and report["verdict"] == "FAIL"
    found = next(e for e in report["evidence"][0] if e["step"] == GP.RECORD_STEP)["evidence"]["findings"]
    assert any("session_open/skills/0" in f for f in found), found


def test_the_full_gate_re_runs_check_all_once_and_fails_on_non_zero(tmp_path):
    # Exit codes in the record are informational; the full gate re-verifies check:all itself.
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "p"}]), encoding="utf-8")
    calls = []

    def failing(root):
        calls.append(root)
        return 1, ["check-facts: 1 problem"]
    report = GP.gate("privacy-policy-uk", "privacy-policy-uk", "interior", runner=scripted(),
                     record=True, root=tmp_path, check_all=failing)
    ca = step(report, GP.CHECK_ALL_STEP)
    assert len(calls) == 1 and ca["ok"] == [False] and ca["stderr"] == [["check-facts: 1 problem"]]
    assert step(report, GP.RECORD_STEP)["ok"] == [True, True], "a frozen page is record-exempt"
    assert report["verdict"] == "FAIL"
    ok = GP.gate("privacy-policy-uk", "privacy-policy-uk", "interior", runner=scripted(),
                 record=True, root=tmp_path, check_all=passing_check_all)
    assert ok["verdict"] == "PASS"
    skipped = GP.gate("privacy-policy-uk", "privacy-policy-uk", "interior", runner=scripted(),
                      record=False, root=tmp_path, check_all=failing)
    assert GP.CHECK_ALL_STEP not in [s["step"] for s in skipped["steps"]] and len(calls) == 1


def test_a_timeout_is_a_failed_step_with_exit_124(monkeypatch):
    def slow(*a, **kw):
        raise subprocess.TimeoutExpired(cmd=a[0], timeout=kw.get("timeout"), stderr=b"line\nstuck")
    monkeypatch.setattr(GP.subprocess, "run", slow)
    code, payload, tail = GP.run_audit("aeo", "p", "location")
    assert code == 124 and payload is None and tail[-1].startswith("timed out after 600")
    report = run(scripted({"aeo": (124, None, ["timed out after 600 s"])}))
    aeo = step(report, "aeo")
    assert aeo["ok"] == [False, False] and aeo["stderr"][0] == ["timed out after 600 s"]
    assert report["verdict"] == "FAIL"


def test_a_crash_keeps_its_stderr_beside_the_evidence_not_inside_it():
    tail = ["Traceback (most recent call last):", "ZeroDivisionError: boom"]
    report = run(scripted({"final-audit": (1, None, tail)}))
    fa = step(report, "final-audit")
    assert fa["ok"] == [False, False] and fa["stderr"] == [tail, tail] and fa["identical"]
    ev = next(e for e in report["evidence"][0] if e["step"] == "final-audit")
    assert "Traceback" not in json.dumps(ev)


def test_the_stderr_tail_is_the_last_twenty_lines():
    assert GP.tail("\n".join(str(i) for i in range(50))) == [str(i) for i in range(30, 50)]


def _built_city(tmp_path):
    (tmp_path / "data/boards").mkdir(parents=True)
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "p"}]), encoding="utf-8")
    (tmp_path / "data/boards/p.json").write_text("{}\n", encoding="utf-8")
    built = tmp_path / "dist/uk-locations/p/index.html"
    built.parent.mkdir(parents=True)
    built.write_text("<html></html>", encoding="utf-8")
    for f in (tmp_path / "data/locations.json", tmp_path / "data/boards/p.json"):
        os.utime(f, (1_000_000, 1_000_000))
    os.utime(built, (2_000_000, 2_000_000))
    return built


def test_edit_then_build_then_commit_is_not_stale(tmp_path):
    # File times, not commit times: a commit made after the build does not stale it.
    _built_city(tmp_path)
    def git(*args):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)
    git("init", "-q")
    git("config", "user.email", "t@example.invalid")
    git("config", "user.name", "t")
    git("add", "data")
    git("commit", "-qm", "committed after the build")
    assert GP.stale_build("p", "uk-locations/p", tmp_path) is None


def test_a_source_edited_after_the_build_fails_rebuild_first(tmp_path):
    _built_city(tmp_path)
    os.utime(tmp_path / "data/boards/p.json", (3_000_000, 3_000_000))
    msg = GP.stale_build("p", "uk-locations/p", tmp_path)
    assert msg and "rebuild first" in msg and "data/boards/p.json" in msg


def test_a_city_row_edit_after_the_build_fails_rebuild_first(tmp_path):
    _built_city(tmp_path)
    os.utime(tmp_path / "data/locations.json", (3_000_000, 3_000_000))
    msg = GP.stale_build("p", "uk-locations/p", tmp_path)
    assert msg and "rebuild first" in msg and "data/locations.json" in msg


@pytest.mark.parametrize("shared", ["src/components/kit/Hero.astro", "src/layouts/PageShell.astro",
                                    "src/lib/globalCta.ts", "src/styles/tokens.css"])
def test_a_kit_edit_after_the_build_fails_rebuild_first(tmp_path, shared):
    # The shared shell renders every page (pageboard.FRESHNESS_SHARED): a kit edit with no
    # rebuild would gate a page nobody built (Task 28a review).
    _built_city(tmp_path)
    f = tmp_path / shared
    f.parent.mkdir(parents=True)
    f.write_text("x", encoding="utf-8")
    os.utime(f, (1_500_000, 1_500_000))
    assert GP.stale_build("p", "uk-locations/p", tmp_path) is None
    os.utime(f, (3_000_000, 3_000_000))
    msg = GP.stale_build("p", "uk-locations/p", tmp_path)
    assert msg and "rebuild first" in msg and shared in msg


def test_a_record_error_is_a_failed_record_step_not_a_traceback(tmp_path):
    # A repo with no HEAD: head_commit() raises RecordError inside findings().
    (tmp_path / "data/page-runs").mkdir(parents=True)
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "p"}]), encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True, capture_output=True)
    sha = "0" * 40
    (tmp_path / "data/page-runs/p.json").write_text(json.dumps({
        "slug": "p",
        "session_open": {"ran_on": "2026-09-27", "skills": [
            "grill-me", "superpowers:writing-plans", "bsuk-location-page-builder"]},
        "verification_before_completion": {
            "ran_on": "2026-09-27", "commit": sha, "claims_verified": ["x"],
            "commands": [{"cmd": "npm run -s check:all", "exit": 0, "examined": 3}]}}),
        encoding="utf-8")
    report = GP.gate("p", "uk-locations/p", "location", runner=scripted(), record=True,
                     root=tmp_path, check_all=passing_check_all)
    rec = step(report, GP.RECORD_STEP)
    assert rec["ok"] == [False, False] and report["verdict"] == "FAIL"
    found = next(e for e in report["evidence"][0] if e["step"] == GP.RECORD_STEP)["evidence"]["findings"]
    assert any("no git history" in f for f in found), found


def test_the_profile_must_be_one_both_audits_know():
    assert {"location", "comparison", "blog"} <= set(GP.PROFILES)


def test_evidence_fails_on_warnings_only_on_a_new_page():
    # A migrated or frozen page carries expected WARNs (an unledgered claim is an ERROR only on
    # a new page), so --fail-on-error, which also fails on WARN, is passed only for a new page.
    new = GP.argv_for("evidence", "uk-locations/x", "location", "o.json", new=True)
    old = GP.argv_for("evidence", "privacy-policy-uk", "interior", "o.json", new=False)
    assert "--fail-on-error" in new and "--fail-on-error" not in old
    for step in ("final-audit", "hardening", "aeo"):
        assert "--fail-on-error" in GP.argv_for(step, "privacy-policy-uk", "interior", "o.json",
                                                new=False)


def test_an_unknown_slug_exits_2(capsys):
    assert GP.main(["no-such-page-anywhere"]) == 2
    assert "gate-page ERROR" in capsys.readouterr().out


def test_the_npm_script_runs_this_file():
    scripts = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
    assert scripts["gate:page"] == "python3 scripts/gate_page.py"
    assert "gate:page" not in scripts["check:all"], "a per-page gate is never chained into check:all"


def test_the_run_twice_rule_is_in_the_gates_pack_and_the_ledger():
    pack = (ROOT / "rules/gates.md").read_text(encoding="utf-8")
    assert "id: run-every-gate-twice" in pack
    rows = json.loads((ROOT / "data/quality/rule-index.json").read_text(encoding="utf-8"))["rules"]
    row = next(r for r in rows if r["id"] == "run-every-gate-twice")
    assert row == {"id": "run-every-gate-twice", "family": "GATE", "enforced": "test",
                   "test": "tests/py/test_gate_page.py", "pack": "rules/gates.md"}


@pytest.mark.skipif(not (ROOT / "dist/privacy-policy-uk/index.html").exists(),
                    reason="needs a built dist/ (npm run build)")
def test_the_real_audits_run_twice_on_a_built_page_and_agree(tmp_path):
    out = tmp_path / "report.json"
    # --skip-record: the full gate would also re-run check:all, which the suite does not nest
    code = GP.main(["privacy-policy-uk", "--skip-record", "--json", str(out)])
    report = json.loads(out.read_text(encoding="utf-8"))
    assert code in (0, 1)
    assert report["runs"] == 2 and len(report["evidence"]) == 2
    assert [s["step"] for s in report["steps"]] == list(GP.AUDIT_STEPS)
    assert report["identical"] is True, [s for s in report["steps"] if not s["identical"]]


# ---- the board gate and the rebuilt/targets barrier (Task 28a) ------------------------------
def test_the_board_gate_is_a_step_on_a_new_page_only():
    seen = []

    def runner(step, route, profile):
        seen.append(step)
        return CLEAN[step]
    GP.gate("blue-staffy-health-uk", "blue-staffy-health-uk", "guide", runner=runner,
            record=False, head="abc")
    assert GP.BOARD_STEP not in seen, "a frozen page keeps its six audits"
    seen.clear()
    report = GP.gate("p", "p", "location", runner=runner, record=False, head="abc")
    assert seen.count(GP.BOARD_STEP) == 2
    assert step(report, GP.BOARD_STEP)["ok"] == [True, True]


def test_the_board_step_runs_board_gate_on_the_key():
    # board_gate.py takes the board's key (a city's bare slug), not the route the audits take
    argv = GP.argv_for(GP.BOARD_STEP, "uk-locations/x", "location", "o.json", key="x")
    assert argv[0].endswith("scripts/board_gate.py") and argv[1:] == ["x"]


def test_a_failing_board_gate_fails_the_page():
    bad = {GP.BOARD_STEP: (1, {"exit": 1, "lines": ["  FAIL asset-required-missing hero", "1 FAIL · 0 WARN"]})}
    report = run(scripted(bad))
    b = step(report, GP.BOARD_STEP)
    assert b["ok"] == [False, False] and b["problems"] == [1, 1] and report["verdict"] == "FAIL"


def _approved_board(root, key):
    (root / "data/boards").mkdir(parents=True, exist_ok=True)
    (root / f"data/boards/{key}.json").write_text(json.dumps(
        {"meta": {"slug": key}, "approval": {"approved_at": "x"}}), encoding="utf-8")


def _lists(root, rebuilt, targets):
    (root / "data/facts").mkdir(parents=True, exist_ok=True)
    (root / "data/facts/rebuilt.json").write_text(json.dumps(rebuilt), encoding="utf-8")
    (root / "tests/render").mkdir(parents=True, exist_ok=True)
    (root / "tests/render/targets.json").write_text(
        json.dumps({"pages": [{"slug": s, "page_type": "location"} for s in targets]}),
        encoding="utf-8")


def test_a_new_page_with_an_approved_board_must_be_in_rebuilt_and_targets(tmp_path):
    _approved_board(tmp_path, "p")
    _lists(tmp_path, [], [])
    report = GP.gate("p", "uk-locations/p", "location", runner=scripted(), record=False,
                     root=tmp_path, head="abc")
    listed = step(report, GP.LISTED_STEP)
    assert listed["ok"] == [False, False] and report["verdict"] == "FAIL"
    found = next(e for e in report["evidence"][0] if e["step"] == GP.LISTED_STEP)["evidence"]["findings"]
    assert any("data/facts/rebuilt.json" in f for f in found), found
    assert any("tests/render/targets.json" in f for f in found), found
    # listed under its key in the ledger and under its route in the render targets: passes
    _lists(tmp_path, ["p"], ["uk-locations/p"])
    report = GP.gate("p", "uk-locations/p", "location", runner=scripted(), record=False,
                     root=tmp_path, head="abc")
    assert step(report, GP.LISTED_STEP)["ok"] == [True, True] and report["verdict"] == "PASS"


def test_the_listing_barrier_leaves_a_page_with_no_approved_board_and_a_frozen_page_alone(tmp_path):
    _lists(tmp_path, [], [])
    report = GP.gate("p", "p", "location", runner=scripted(), record=False, root=tmp_path,
                     head="abc")
    assert GP.LISTED_STEP not in [s["step"] for s in report["steps"]]
    _approved_board(tmp_path, "blue-staffy-health-uk")
    report = GP.gate("blue-staffy-health-uk", "blue-staffy-health-uk", "guide",
                     runner=scripted(), record=False, root=tmp_path, head="abc")
    assert GP.LISTED_STEP not in [s["step"] for s in report["steps"]]
