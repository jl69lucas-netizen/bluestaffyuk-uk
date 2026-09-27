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
    assert [s["step"] for s in report["steps"]] == list(GP.AUDIT_STEPS)
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


def test_a_built_page_older_than_its_sources_fails_rebuild_first(tmp_path):
    def git(*args):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)
    (tmp_path / "data/boards").mkdir(parents=True)
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "p"}]), encoding="utf-8")
    (tmp_path / "data/boards/p.json").write_text("{}\n", encoding="utf-8")
    built = tmp_path / "dist/uk-locations/p/index.html"
    built.parent.mkdir(parents=True)
    built.write_text("<html></html>", encoding="utf-8")
    git("init", "-q")
    git("config", "user.email", "t@example.invalid")
    git("config", "user.name", "t")
    git("add", "data")
    git("commit", "-qm", "page")
    os.utime(built, (1_000_000, 1_000_000))
    msg = GP.stale_build("p", "uk-locations/p", tmp_path)
    assert msg and "rebuild first" in msg
    os.utime(built, None)
    assert GP.stale_build("p", "uk-locations/p", tmp_path) is None


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
