"""`scripts/page_run_record.py` + `schemas/page-run-record.schema.json` — the three passes
the user ruled mandatory on every project 5 page (2026-09-26): `impeccable:impeccable` and
`frontend-design:frontend-design` in Harden, `superpowers:verification-before-completion`
before any "page done" claim. No test, no rule: each pass leaves a key in
`data/page-runs/<slug>.json`, and `npm run gate:page -- <slug>` fails the page until all
three are there, complete and current.

Controller amendments (2026-09-27, binding; revised by the Task 25 review):
- Freshness: the verification commit is in HEAD's history and nothing the page is built from
  changed between it and HEAD (`git diff --quiet <verify> HEAD -- <sources>`, plus the
  page's own row of data/locations.json). The page's sources include its facts and verbatim
  files. `impeccable` precedes `frontend_design`, and the page did not change between the
  frontend-design pass and verification — a fix between the two Harden passes stales
  nothing. A pass whose visual change waits for the breeder records it under `deferred`.
- A `session_open` key proves the run opened with `grill-me`, then
  `superpowers:writing-plans`, then the page-type builder skill, in that order.

The record tests run in a throwaway git repository in tmp_path, because freshness is a
question about commits. `tests/py/fixtures/page-runs/known-broken.json` is the record that
must never validate.
"""
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import page_run_record as PRR  # noqa: E402

BROKEN = ROOT / "tests/py/fixtures/page-runs/known-broken.json"
KEY = "newtown"


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def repo(tmp_path):
    """A git repo holding one city page: its row, its board record and the city route."""
    (tmp_path / "data/boards").mkdir(parents=True)
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": KEY}]), encoding="utf-8")
    (tmp_path / "data/boards" / f"{KEY}.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "src/pages/uk-locations").mkdir(parents=True)
    (tmp_path / "src/pages/uk-locations/[slug].astro").write_text("route\n", encoding="utf-8")
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@example.invalid")
    git(tmp_path, "config", "user.name", "t")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "page")
    return tmp_path


VERIFY_RUN = ["npm run -s check:all", "npm run -s build",
              f"npm run gate:page -- {KEY} --skip-record"]


def commit(root, msg="record"):
    """Commit the page-run record (the gate refuses an uncommitted one)."""
    git(root, "add", "data/page-runs")
    git(root, "commit", "-qm", msg)


def verify(root, run=None, claims=("done",)):
    PRR.write_pass(KEY, "verification", root, run=run or VERIFY_RUN, claims=list(claims))


def full_record(root):
    PRR.write_pass(KEY, "session-open", root, builder="bsuk-location-page-builder")
    PRR.write_pass(KEY, "impeccable", root, findings=2, fixed=1, deferred=["token change"])
    PRR.write_pass(KEY, "frontend-design", root, findings=0, fixed=0)
    verify(root, claims=["the page passes every gate twice"])
    commit(root)


def fake_npm(root, exit_code=0, examined=7):
    """`npm run ...` answered by a script on PATH, so verification can run in a tmp repo."""
    bin_dir = root / "bin"
    bin_dir.mkdir(exist_ok=True)
    npm = bin_dir / "npm"
    npm.write_text(f"#!/bin/sh\necho 'examined {examined} pages; 0 problems'\nexit {exit_code}\n",
                   encoding="utf-8")
    npm.chmod(0o755)
    return bin_dir


@pytest.fixture
def page(tmp_path, monkeypatch):
    root = repo(tmp_path)
    monkeypatch.setenv("PATH", str(fake_npm(root)) + ":" + os.environ["PATH"])
    return root


# ── the schema ────────────────────────────────────────────────────────────────────────────

def test_the_known_broken_record_breaks_the_schema_in_every_way_it_was_broken():
    errs = PRR.schema_errors(json.loads(BROKEN.read_text(encoding="utf-8")))
    joined = "\n".join(errs)
    for where in ("session_open/skills/0", "session_open/skills/1", "impeccable/widths", "impeccable/findings", "impeccable/commit",
                  "frontend_design/ran_on", "frontend_design/deferred/0",
                  "verification_before_completion/commands/0",
                  "verification_before_completion/claims_verified"):
        assert any(e.startswith(where) for e in errs), f"{where} not reported:\n{joined}"


def test_the_gate_reports_the_known_broken_record_as_a_schema_failure(tmp_path):
    root = repo(tmp_path)
    target = PRR.record_path(KEY, root)
    target.parent.mkdir(parents=True)
    broken = json.loads(BROKEN.read_text(encoding="utf-8"))
    broken["slug"] = KEY
    target.write_text(json.dumps(broken), encoding="utf-8")
    found = PRR.findings(KEY, root)
    assert found and all("breaks the schema" in f for f in found), found


def test_a_complete_record_written_by_the_writer_passes(page):
    full_record(page)
    assert PRR.findings(KEY, page) == []
    rec = PRR.load(KEY, page)
    assert rec["impeccable"]["widths"] == [375, 768, 1280]
    assert rec["session_open"]["skills"] == ["grill-me", "superpowers:writing-plans",
                                             "bsuk-location-page-builder"]
    assert rec["verification_before_completion"]["commands"][0] == {
        "cmd": "npm run -s check:all", "exit": 0, "examined": 7}
    assert PRR.schema_errors(rec) == []


# ── what the gate fails on ────────────────────────────────────────────────────────────────

def test_no_record_fails(tmp_path):
    root = repo(tmp_path)
    assert PRR.findings(KEY, root) == [
        f"no data/page-runs/{KEY}.json — record the session open, the impeccable and "
        "frontend-design passes and verification-before-completion "
        "(docs/reference/page-run.md rows 1, 14, 15, 18)"]


def test_a_missing_pass_fails(page):
    PRR.write_pass(KEY, "impeccable", page, findings=0, fixed=0)
    found = PRR.findings(KEY, page)
    assert any("the frontend_design pass is missing" in f for f in found), found
    assert any("the verification_before_completion pass is missing" in f for f in found), found
    assert any("the session_open key is missing" in f for f in found), found


def test_a_finding_neither_fixed_nor_deferred_fails(page):
    full_record(page)
    rec = PRR.load(KEY, page)
    rec["impeccable"]["fixed"] = 0
    PRR.record_path(KEY, page).write_text(json.dumps(rec), encoding="utf-8")
    assert any("found 2 but fixed 0 and deferred 1" in f for f in PRR.findings(KEY, page))


def test_a_verification_older_than_the_last_source_change_stales_the_record(page):
    full_record(page)
    (page / "src/pages/uk-locations/[slug].astro").write_text("changed\n", encoding="utf-8")
    git(page, "commit", "-qam", "template edit after the passes")
    found = PRR.findings(KEY, page)
    stale = [f for f in found if "older than the page's last source change" in f]
    assert len(stale) == 1 and "verification_before_completion" in stale[0], found
    # the change also lies between the frontend-design pass and verification: once verified
    # again, that pass is the stale one
    verify(page)
    commit(page)
    found = PRR.findings(KEY, page)
    assert any("the page changed after the frontend-design pass; re-run it" in f
               for f in found), found
    PRR.write_pass(KEY, "frontend-design", page, findings=0, fixed=0)
    verify(page)
    commit(page)
    assert PRR.findings(KEY, page) == []


def test_a_harden_fix_committed_after_a_pass_does_not_stale_it(page):
    PRR.write_pass(KEY, "session-open", page, builder="bsuk-location-page-builder")
    PRR.write_pass(KEY, "impeccable", page, findings=1, fixed=1)
    git(page, "add", "-A")
    git(page, "commit", "-qm", "impeccable record")
    (page / "src/pages/uk-locations/[slug].astro").write_text("frontend-design fix\n",
                                                              encoding="utf-8")
    git(page, "commit", "-qam", "frontend-design fix")
    PRR.write_pass(KEY, "frontend-design", page, findings=1, fixed=1)
    verify(page)
    commit(page)
    assert PRR.findings(KEY, page) == []


def test_an_impeccable_pass_after_the_frontend_design_pass_fails(page):
    full_record(page)
    PRR.write_pass(KEY, "impeccable", page, findings=0, fixed=0)
    commit(page)
    found = PRR.findings(KEY, page)
    assert any("the impeccable pass ran at" in f and "after the frontend-design pass" in f
               for f in found), found


def test_an_edit_after_the_frontend_design_pass_stales_it(page):
    PRR.write_pass(KEY, "session-open", page, builder="bsuk-location-page-builder")
    PRR.write_pass(KEY, "impeccable", page, findings=0, fixed=0)
    PRR.write_pass(KEY, "frontend-design", page, findings=0, fixed=0)
    commit(page)
    (page / "data/boards" / f"{KEY}.json").write_text('{"late": true}\n', encoding="utf-8")
    git(page, "commit", "-qam", "edit after the frontend-design pass")
    verify(page)
    commit(page)
    found = PRR.findings(KEY, page)
    assert found == [f"data/page-runs/{KEY}.json: the page changed after the frontend-design "
                     f"pass; re-run it (changed: data/boards/{KEY}.json)"], found


def test_a_city_row_edit_after_verification_stales_the_record(page):
    full_record(page)
    (page / "data/locations.json").write_text(json.dumps([{"slug": KEY, "h1": "new"}]),
                                              encoding="utf-8")
    git(page, "commit", "-qam", "row edit")
    found = PRR.findings(KEY, page)
    assert any("older than the page's last source change" in f and "data/locations.json" in f
               for f in found), found


def test_another_citys_row_edit_does_not_stale_the_record(page):
    full_record(page)
    (page / "data/locations.json").write_text(json.dumps([{"slug": KEY}, {"slug": "elsewhere"}]),
                                              encoding="utf-8")
    git(page, "commit", "-qam", "another city")
    assert PRR.findings(KEY, page) == []


def test_a_facts_file_edit_after_verification_stales_the_record(page):
    full_record(page)
    (page / "data/facts").mkdir()
    (page / "data/facts" / f"{KEY}.json").write_text("{}\n", encoding="utf-8")
    git(page, "add", "-A", "data/facts")
    git(page, "commit", "-qm", "facts")
    found = PRR.findings(KEY, page)
    assert any("older than the page's last source change" in f and f"data/facts/{KEY}.json" in f
               for f in found), found


def test_a_merge_brought_source_change_stales_the_record(page):
    main = subprocess.run(["git", "-C", str(page), "rev-parse", "--abbrev-ref", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    git(page, "checkout", "-qb", "side")
    (page / "src/pages/uk-locations/[slug].astro").write_text("side edit\n", encoding="utf-8")
    git(page, "commit", "-qam", "an edit made before verification, merged after it")
    git(page, "checkout", "-q", main)
    full_record(page)
    git(page, "merge", "-q", "--no-edit", "side")
    found = PRR.findings(KEY, page)
    assert any("older than the page's last source change" in f for f in found), found


def test_a_verification_off_heads_history_is_stale(page):
    full_record(page)
    rec = PRR.load(KEY, page)
    rec[PRR.VERIFY]["commit"] = "0" * 40
    PRR.record_path(KEY, page).write_text(json.dumps(rec), encoding="utf-8")
    commit(page)
    assert any("not in HEAD's history" in f for f in PRR.findings(KEY, page))


def test_the_record_must_be_committed(page):
    full_record(page)
    rec = PRR.load(KEY, page)
    rec[PRR.VERIFY]["claims_verified"].append("an edit nobody committed")
    PRR.record_path(KEY, page).write_text(json.dumps(rec), encoding="utf-8")
    assert any(f"commit data/page-runs/{KEY}.json" in f for f in PRR.findings(KEY, page))


def test_the_session_open_must_not_postdate_the_impeccable_pass(page):
    full_record(page)
    rec = PRR.load(KEY, page)
    rec["session_open"]["ran_on"] = "2999-01-01"
    PRR.record_path(KEY, page).write_text(json.dumps(rec), encoding="utf-8")
    commit(page)
    assert any("session_open ran on 2999-01-01, after the impeccable pass" in f
               for f in PRR.findings(KEY, page))


def test_a_command_that_examined_nothing_fails(page, monkeypatch):
    full_record(page)
    monkeypatch.setenv("PATH", str(fake_npm(page, examined=0)) + ":" + os.environ["PATH"])
    verify(page)
    commit(page)
    assert any("examined 0" in f for f in PRR.findings(KEY, page))


def test_verification_must_build_before_the_gate(page):
    full_record(page)
    verify(page, run=["npm run -s check:all", f"npm run gate:page -- {KEY} --skip-record",
                      "npm run -s build"])
    commit(page)
    assert any("did not run `npm run -s build` before" in f for f in PRR.findings(KEY, page))


def test_verification_refuses_while_tracked_files_are_dirty(page):
    full_record(page)
    (page / "data/locations.json").write_text(json.dumps([{"slug": KEY}, {"slug": "x"}]),
                                              encoding="utf-8")
    with pytest.raises(PRR.RecordError, match="commit everything first"):
        verify(page)


def test_harden_passes_refuse_a_page_with_no_sources_yet(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": KEY}]), encoding="utf-8")
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@example.invalid")
    git(tmp_path, "config", "user.name", "t")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "row only")
    with pytest.raises(PRR.RecordError, match="no sources yet"):
        PRR.write_pass(KEY, "impeccable", tmp_path, findings=0, fixed=0)


def test_a_session_open_out_of_order_fails_the_schema(page):
    full_record(page)
    rec = PRR.load(KEY, page)
    rec["session_open"]["skills"] = ["superpowers:writing-plans", "grill-me",
                                     "bsuk-location-page-builder"]
    PRR.record_path(KEY, page).write_text(json.dumps(rec), encoding="utf-8")
    found = PRR.findings(KEY, page)
    assert any("breaks the schema at session_open/skills/0" in f for f in found), found
    rec["session_open"]["skills"] = ["grill-me", "superpowers:writing-plans"]
    PRR.record_path(KEY, page).write_text(json.dumps(rec), encoding="utf-8")
    assert any("session_open/skills" in f for f in PRR.findings(KEY, page))


def test_a_missing_session_open_fails(page):
    full_record(page)
    rec = PRR.load(KEY, page)
    del rec["session_open"]
    PRR.record_path(KEY, page).write_text(json.dumps(rec), encoding="utf-8")
    commit(page)
    assert PRR.findings(KEY, page) == [
        f"data/page-runs/{KEY}.json: the session_open key is missing — record "
        "grill-me, superpowers:writing-plans and the builder skill (page-run.md row 1)"]


def test_a_deferred_visual_change_is_allowed(page):
    full_record(page)
    rec = PRR.load(KEY, page)
    assert rec["impeccable"]["deferred"] == ["token change"]
    assert PRR.findings(KEY, page) == []


def test_uncommitted_source_changes_fail(page):
    full_record(page)
    (page / "data/boards" / f"{KEY}.json").write_text('{"edited": true}\n', encoding="utf-8")
    assert any("uncommitted changes" in f for f in PRR.findings(KEY, page))


def test_verification_must_run_check_all_and_the_gate_and_pass_them(page, monkeypatch):
    PRR.write_pass(KEY, "impeccable", page, findings=0, fixed=0)
    PRR.write_pass(KEY, "frontend-design", page, findings=0, fixed=0)
    verify(page, run=["npm run -s check:placeholders"])
    found = PRR.findings(KEY, page)
    assert any("did not run `npm run -s check:all`" in f for f in found), found
    assert any(f"did not run `npm run gate:page -- {KEY}`" in f for f in found), found

    monkeypatch.setenv("PATH", str(fake_npm(page, exit_code=1)) + ":" + os.environ["PATH"])
    verify(page, run=["npm run -s check:all", "npm run -s build", f"npm run gate:page -- {KEY}"])
    found = PRR.findings(KEY, page)
    assert any("`npm run -s check:all` and it exited 1" in f for f in found), found


def test_the_twelve_pages_built_before_the_rule_are_exempt(tmp_path):
    root = repo(tmp_path)
    assert PRR.findings("privacy-policy-uk", root) == []


# ── the writer ────────────────────────────────────────────────────────────────────────────

def test_the_writer_refuses_while_the_sources_are_dirty(page):
    (page / "data/boards" / f"{KEY}.json").write_text('{"x": 1}\n', encoding="utf-8")
    with pytest.raises(PRR.RecordError, match="commit the page's sources first"):
        PRR.write_pass(KEY, "impeccable", page, findings=0, fixed=0)


def test_the_cli_writes_a_pass_and_checks_a_page(page, capsys):
    assert PRR.main([KEY, "impeccable", "--findings", "1", "--fixed", "1"], root=page) == 0
    assert "wrote data/page-runs/newtown.json — impeccable at" in capsys.readouterr().out
    assert PRR.main([KEY, "--check"], root=page) == 1
    assert "4 problem(s)" in capsys.readouterr().out
    assert PRR.main([KEY, "session-open", "--builder", "bsuk-location-page-builder"],
                    root=page) == 0
    assert "session_open" in capsys.readouterr().out


def test_the_page_sources_of_a_city_are_its_record_and_its_route_file(tmp_path):
    root = repo(tmp_path)
    assert PRR.page_sources(KEY, root) == [f"data/boards/{KEY}.json",
                                           "src/pages/uk-locations/[slug].astro"]
