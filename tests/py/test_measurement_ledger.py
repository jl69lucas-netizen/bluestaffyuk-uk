"""`scripts/measurement_ledger.py` — the brief's measurement ledger as numbers at close.

The brief lists eighteen measurements "that must appear in the close-out, not boxes that get
ticked". BlueStaffyUK held the data for most of them and printed none together. The unit tests
build a small tree in tmp_path — two checks, one scorecard run, two built pages and their
gate:page reports, committed in a throwaway git repository — so they pin how each row is
computed; the last test runs the ledger on this repo. A row that measured nothing is never a
pass, and an input that judged another build or another commit is STALE, not evidence.
"""
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import measurement_ledger as ML  # noqa: E402
import rendered_changes as RC  # noqa: E402

OTHER = "fedcba9876543210fedcba9876543210fedcba98"
ROUTES = {"newtown": "uk-locations/newtown", "comp": "comp"}
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, env=GIT_ENV,
                          capture_output=True, text=True).stdout.strip()


def commit(root, message="x"):
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", message)
    return git(root, "rev-parse", "HEAD")


def head(root):
    return git(root, "rev-parse", "HEAD")

CHECKS_TS = """
register({ id: 'layout-min-font-size', family: 'LAYOUT', severity: 'blocking', describe: 'x' });
register({ id: 'sem-title-case', family: 'SEM', severity: 'advisory', describe: 'y' });
"""


def card(slug, examined, details=()):
    return {"slug": slug, "examined_by_check": examined,
            "details": [{"viewport": 375, "checkId": c, "count": 1, "message": "m"} for c in details]}


def gate_report(verdict="PASS", runs=2, identical=True, dup=(0, 0), head="@HEAD", pages=40,
                steps=("dup-body", "dup-headers"), error=(), page_hash="@HASH"):
    """A gate:page report; "@HEAD" is the fixture's commit, "@HASH" the built page's hash."""
    def ev(step):
        return {"error": "exit 1 and no JSON report"} if step in error else {"pages": pages,
                                                                              "findings": []}
    problems = {"dup-body": dup[0], "dup-headers": dup[1]}
    return {"head": head, "page_hash": page_hash, "runs": runs, "verdict": verdict, "identical": identical,
            "steps": [{"step": s, "ok": [True] * runs, "problems": [problems[s]] * runs,
                       "identical": True} for s in steps],
            "evidence": [[{"step": s, "evidence": ev(s)} for s in steps] for _ in range(runs)]}


def write(path, data, mtime=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
    if mtime is not None:
        os.utime(path, (mtime, mtime))


BUILT = time.time() - 1000  # the built pages are older than every input written after them


def tree(tmp_path, cards=None, reports=None, families=("LAYOUT", "SEM"),
         rendered_head="@HEAD12"):
    """The sources, committed; then (as on a real close) the git-ignored reports for that commit."""
    write(tmp_path / ".gitignore", "dist/\ndocs/reports/\n")
    write(tmp_path / "src/pages/comp.astro", "---\n---\n<main>comp</main>\n")
    write(tmp_path / "src/pages/uk-locations/[slug].astro", "---\n---\n<main>city</main>\n")
    write(tmp_path / "tests/render/checks/all.ts", CHECKS_TS)
    write(tmp_path / "tests/render/targets.json", {
        "families_by_page_type": {"location": list(families)}, "deferred_checks": {},
        "pages": [{"slug": "uk-locations/newtown"}, {"slug": "comp"}]})
    for route in ("uk-locations/newtown", "comp"):
        write(tmp_path / "dist" / route / "index.html", "<main></main>", BUILT)
    sc = tmp_path / "data/quality/scorecards"
    sc.mkdir(parents=True)
    for c in cards if cards is not None else [
            card("uk-locations/newtown", {"layout-min-font-size": 50, "sem-title-case": 4},
                 details=["sem-title-case"]),
            card("comp", {"layout-min-font-size": 30, "sem-title-case": 0})]:
        write(sc / (c["slug"].replace("/", "__") + "-2026-09-27.json"), c)
    write(tmp_path / "data/quality/rule-index.json", {"rules": [
        {"id": "a", "enforced": "test"}, {"id": "b", "enforced": "untested"}]})
    write(tmp_path / "data/quality/rework-ledger.json", {"windows": []})
    write(tmp_path / "data/locations.json", [{"slug": "newtown", "region": "north"}])
    write(tmp_path / "docs/research/llm-intel/newtown-2026-09-25.json", {"fetched": {"status": "ok"}})
    git(tmp_path, "init", "-q")
    sha = commit(tmp_path, "sources")
    gp = tmp_path / "docs/reports/gate-page"
    gp.mkdir(parents=True)
    for key, rep in (reports if reports is not None else
                     {"newtown": gate_report(), "comp": gate_report()}).items():
        if isinstance(rep, dict):
            rep = dict(rep)
            if isinstance(rep.get("head"), str):
                rep["head"] = rep["head"].replace("@HEAD", sha)
            if rep.get("page_hash") == "@HASH":
                rep["page_hash"] = page_hash(tmp_path, key)
        write(gp / f"{key}.json", rep)
    write(tmp_path / "docs/reports/rendered-changes.json",
          {"base": "abc", "head": rendered_head.replace("@HEAD12", sha[:12]),
           "changed": ["uk-locations/newtown", "comp"]})
    return tmp_path


def page_hash(root, key):
    return RC.content_hash((root / "dist" / ROUTES[key] / "index.html").read_text(encoding="utf-8"))


def led(root, slugs=("newtown", "comp")):
    return ML.ledger("p5", list(slugs), root)


def rows(ledger):
    return {r["id"]: r for r in ledger["rows"]}


def test_the_ledger_has_the_ten_rows_in_order(tmp_path):
    out = led(tree(tmp_path))
    assert [r["id"] for r in out["rows"]] == ["M1", "M2", "M3", "M6", "M8", "M9", "M10", "M12",
                                              "M13", "M18"]
    assert out["scope"] == ["newtown", "comp"] and out["failed"] == [] and out["empty"] == []


def test_every_row_is_a_number_or_a_named_barrier(tmp_path):
    root = tree(tmp_path)
    r = rows(led(root))
    assert r["M1"]["value"] == "2 checks, 0 at zero (run 2026-09-27, 2 pages)"
    assert r["M2"]["value"] == "registered 2 · wired 2 · difference ∅"
    assert r["M3"]["value"] == "blocking 0 · advisory 1 (run 2026-09-27; never summed)"
    assert r["M6"]["value"] == "2 of 2 pages clean (run 2026-09-27)" and r["M6"]["status"] == "PASS"
    assert r["M8"]["value"] == "2 of 2 pages: >= 2 runs, both clean"
    assert r["M9"]["value"].startswith("NOT FETCHED — ")
    assert r["M10"]["value"] == "body 0 · headers 0 across 2 pages"
    assert r["M12"]["value"] == "1 / 2 (one engine, one query per page)"
    assert r["M12"]["detail"] == "comp: no llm-intel file"
    assert r["M13"]["value"] == ("2 (base abc → head %s) · IndexNow submitted: "
                                 "NOT FETCHED — project 6" % head(root)[:12])
    assert r["M13"]["status"] == "REPORTED"
    assert r["M18"]["value"] == "1 of 2 rules" and r["M18"]["detail"] == "b"


# --- M1 / M3: the scorecards --------------------------------------------------------------

def test_a_check_that_examined_zero_nodes_fails_m1(tmp_path):
    root = tree(tmp_path, cards=[card("comp", {"layout-min-font-size": 3, "sem-title-case": 0})])
    out = led(root, ["comp"])
    assert rows(out)["M1"]["status"] == "FAIL" and rows(out)["M1"]["detail"] == "sem-title-case"
    assert "M1" in out["failed"]


def test_a_check_absent_from_every_card_is_reported_not_failed(tmp_path):
    # tests/render/lib/examined.ts: a registered check with no key in any card is "not yet
    # measured" (registered since the last page run) — named, never a FAIL; measured-zero fails.
    root = tree(tmp_path, cards=[card("comp", {"layout-min-font-size": 3})])
    r = rows(led(root, ["comp"]))
    assert r["M1"]["status"] == "PASS"
    assert r["M1"]["value"] == "2 checks, 0 at zero, 1 not yet measured (run 2026-09-27, 1 pages)"
    assert r["M1"]["detail"] == "not yet measured: sem-title-case"


def test_a_page_rerun_alone_keeps_the_other_pages_newest_cards(tmp_path):
    root = tree(tmp_path)
    write(root / "data/quality/scorecards/comp-2026-09-28.json",
          card("comp", {"layout-min-font-size": 30, "sem-title-case": 2}))
    r = rows(led(root))
    assert r["M1"]["value"] == "2 checks, 0 at zero (runs 2026-09-27 to 2026-09-28, 2 pages)"


def test_a_card_for_a_page_no_longer_targeted_is_ignored(tmp_path):
    root = tree(tmp_path)
    write(root / "data/quality/scorecards/gone-2026-09-27.json",
          card("gone", {"layout-min-font-size": 0, "sem-title-case": 0}))
    r = rows(led(root))
    assert r["M1"]["status"] == "PASS" and r["M1"]["value"].endswith("2 pages)")


def test_a_broken_card_fails_m1_by_name(tmp_path):
    root = tree(tmp_path)
    write(root / "data/quality/scorecards/comp-2026-09-26.json", "{not json")
    r = rows(led(root))
    assert r["M1"]["status"] == "FAIL"
    assert "unreadable scorecard comp-2026-09-26.json" in r["M1"]["detail"]


def test_no_scorecards_is_a_named_barrier_and_a_fail(tmp_path):
    r = rows(led(tree(tmp_path, cards=[]), ["comp"]))
    assert r["M1"]["status"] == "FAIL" and r["M1"]["value"].startswith("NOT FETCHED — ")


# --- M2 ---------------------------------------------------------------------------------

def test_a_family_registered_but_not_wired_fails_m2(tmp_path):
    r = rows(led(tree(tmp_path, families=("LAYOUT",)), ["comp"]))
    assert r["M2"]["status"] == "FAIL" and r["M2"]["value"].endswith("difference {SEM}")


# --- M6 ---------------------------------------------------------------------------------

def test_a_page_with_small_text_fails_m6(tmp_path):
    root = tree(tmp_path, cards=[card("comp", {"layout-min-font-size": 3, "sem-title-case": 1},
                                      details=["layout-min-font-size"])])
    r = rows(led(root, ["comp"]))
    assert r["M6"]["status"] == "FAIL" and r["M6"]["detail"] == "comp"


def test_a_scorecard_older_than_the_built_page_is_stale(tmp_path):
    root = tree(tmp_path)
    os.utime(root / "dist/comp/index.html", None)  # rebuilt after the render run
    os.utime(root / "data/quality/scorecards/comp-2026-09-27.json", (BUILT, BUILT))
    out = led(root)
    r = rows(out)
    assert r["M6"]["status"] == "STALE" and "comp: scorecard older than dist/comp/index.html" \
        in r["M6"]["detail"]
    assert "M6" in out["failed"]


# --- M8 / M10: the gate:page reports ----------------------------------------------------

def test_a_gate_run_once_or_unstable_fails_m8_and_a_crossover_fails_m10(tmp_path):
    root = tree(tmp_path, reports={"newtown": gate_report(runs=1),
                                   "comp": gate_report(verdict="FAIL", identical=False, dup=(2, 1))})
    r = rows(led(root))
    assert r["M8"]["status"] == "FAIL" and "newtown: 1 runs" in r["M8"]["detail"]
    assert r["M10"]["status"] == "FAIL" and r["M10"]["value"] == "body 2 · headers 1 across 2 pages"


def test_a_page_with_no_gate_report_fails_m8_and_m10(tmp_path):
    r = rows(led(tree(tmp_path, reports={"comp": gate_report()})))
    assert r["M8"]["status"] == "FAIL" and r["M10"]["status"] == "FAIL"
    assert r["M10"]["detail"] == "newtown: no gate:page report"


def test_a_report_gated_on_a_dirty_tree_is_stale(tmp_path):
    out = led(tree(tmp_path, reports={"newtown": gate_report(head="@HEAD-dirty"),
                                      "comp": gate_report()}))
    r = rows(out)
    assert r["M8"]["status"] == "STALE" and r["M10"]["status"] == "STALE"
    assert "newtown: gated on a dirty tree — re-gate after commit" in r["M8"]["detail"]
    assert "newtown: gated on a dirty tree — re-gate after commit" in r["M10"]["detail"]
    assert {"M8", "M10"} <= set(out["failed"])


def test_a_report_for_a_commit_not_behind_head_is_stale(tmp_path):
    r = rows(led(tree(tmp_path, reports={"newtown": gate_report(head=OTHER),
                                         "comp": gate_report(head=None)})))
    assert r["M8"]["status"] == "STALE"
    assert f"newtown: report is for {OTHER}, not an ancestor of HEAD" in r["M8"]["detail"]
    assert "comp: report is for None, not an ancestor of HEAD" in r["M8"]["detail"]


def test_an_older_commit_with_the_page_unchanged_is_fresh_for_m8_but_not_m10(tmp_path):
    # M8 is the page's own gate: a later commit that does not touch the page leaves it
    # judged. M10 is site-wide — any page's edit can create a crossover — so only HEAD counts.
    root = tree(tmp_path)
    gated = head(root)
    write(root / "README.md", "unrelated")
    now = commit(root, "unrelated")
    r = rows(led(root))
    assert r["M8"]["status"] == "PASS", r["M8"]
    assert r["M10"]["status"] == "STALE"
    assert f"comp: report is for {gated}, HEAD is {now}" in r["M10"]["detail"]


def test_an_older_commit_with_the_page_changed_is_stale(tmp_path):
    root = tree(tmp_path)
    gated = head(root)
    write(root / "src/pages/comp.astro", "---\n---\n<main>comp, edited</main>\n")
    write(root / "data/locations.json", [{"slug": "newtown", "region": "south"}])
    commit(root, "edit")
    r = rows(led(root))
    assert r["M8"]["status"] == "STALE"
    assert f"comp: sources changed since {gated[:12]}: src/pages/comp.astro" in r["M8"]["detail"]
    assert f"newtown: sources changed since {gated[:12]}: data/locations.json (the newtown row)" \
        in r["M8"]["detail"]


def test_a_rebuilt_page_that_differs_from_the_gated_one_is_stale(tmp_path):
    root = tree(tmp_path, reports={"newtown": gate_report(page_hash=None), "comp": gate_report()})
    write(root / "dist/comp/index.html", "<main>changed</main>")
    out = led(root)
    r = rows(out)
    assert r["M8"]["status"] == "STALE" and r["M10"]["status"] == "STALE"
    for d in (r["M8"]["detail"], r["M10"]["detail"]):
        assert "comp: built page differs from the one gated (dist/comp/index.html)" in d
        assert "newtown: built page differs from the one gated" in d


def test_a_page_never_built_fails_m8(tmp_path):
    root = tree(tmp_path)
    (root / "dist/comp/index.html").unlink()
    r = rows(led(root))
    assert r["M8"]["status"] == "FAIL" and "comp: not built (dist/comp/index.html)" in r["M8"]["detail"]


def test_m10_fails_on_a_missing_step_an_empty_audit_or_a_crash(tmp_path):
    root = tree(tmp_path, reports={"newtown": gate_report(steps=("dup-body",)),
                                   "comp": gate_report(pages=0)})
    r = rows(led(root))
    assert r["M10"]["status"] == "FAIL"
    assert "newtown: missing step dup-headers" in r["M10"]["detail"]
    assert "comp: dup-body examined nothing" in r["M10"]["detail"]
    r = rows(led(tree(tmp_path / "b", reports={"newtown": gate_report(error=("dup-headers",)),
                                               "comp": gate_report()})))
    assert r["M10"]["status"] == "FAIL" and "newtown: dup-headers audit error" in r["M10"]["detail"]


def test_a_malformed_report_is_a_named_barrier_not_a_traceback(tmp_path):
    root = tree(tmp_path, reports={"newtown": ["not", "a", "report"],
                                   "comp": {"head": "@HEAD", "steps": "x", "evidence": 3}})
    r = rows(led(root))
    assert r["M8"]["status"] == "FAIL" and "newtown: malformed gate:page report" in r["M8"]["detail"]
    assert r["M10"]["status"] == "FAIL" and "newtown: malformed gate:page report" in r["M10"]["detail"]
    assert "comp: missing step dup-body" in r["M10"]["detail"]


# --- M9 / M12 / M13 / M18 ---------------------------------------------------------------

def test_m9_reads_the_latest_window(tmp_path):
    root = tree(tmp_path)
    write(root / "data/quality/rework-ledger.json", {"windows": [
        {"window": "2026-09", "page_rate": 0.1, "harness_rate": 0.3},
        {"window": "2026-10", "page_rate": 0.2, "harness_rate": 0.05}]})
    assert rows(led(root))["M9"]["value"] == "page 0.2 · harness 0.05 (window 2026-10)"


def test_m12_matches_the_key_and_a_date_only(tmp_path):
    root = tree(tmp_path)
    write(root / "docs/research/llm-intel/comp-extra-2026-09-25.json", {"fetched": {"status": "ok"}})
    write(root / "docs/research/llm-intel/available-puppies--roman-2026-09-25.json",
          {"fetched": {"status": "ok"}})
    r = rows(led(root, ["newtown", "comp", "available-puppies/roman"]))
    assert r["M12"]["value"].startswith("2 / 3")
    assert r["M12"]["detail"] == "comp: no llm-intel file"


def test_m13_a_report_for_another_commit_is_stale(tmp_path):
    root = tree(tmp_path, rendered_head=OTHER[:12])
    r = rows(led(root))
    assert r["M13"]["status"] == "STALE"
    assert r["M13"]["detail"].startswith(
        f"rendered-changes.json is for {OTHER[:12]}, HEAD is {head(root)} — re-run "
        "rendered_changes.py --base <ref> --json")


def test_m13_a_dirty_head_is_labelled(tmp_path):
    root = tree(tmp_path, rendered_head="@HEAD12-dirty")
    r = rows(led(root))
    assert r["M13"]["status"] == "REPORTED"
    assert f"head {head(root)[:12]}-dirty (built from a dirty tree)" in r["M13"]["value"]


def test_m18_a_malformed_rule_index_is_a_barrier(tmp_path):
    root = tree(tmp_path)
    write(root / "data/quality/rule-index.json", {"rules": "x"})
    assert rows(led(root))["M18"]["value"].startswith("NOT FETCHED — ")


# --- scope, empty rows and the command --------------------------------------------------

def test_default_scope_is_the_new_pages_in_rebuilt(tmp_path):
    root = tree(tmp_path)
    write(root / "data/facts/rebuilt.json", ["index", "privacy-policy-uk", "_demo", "comp"])
    assert ML.default_slugs(root) == ["comp"]


def test_an_empty_scope_is_never_a_pass(tmp_path, capsys):
    root = tree(tmp_path)
    write(root / "data/facts/rebuilt.json", ["index"])
    out = ML.ledger("p5", None, root)
    assert {r["id"] for r in out["rows"] if r["status"] == "EMPTY"} == {"M6", "M8", "M10", "M12"}
    assert out["empty"] == ["M6", "M8", "M10", "M12"] and out["failed"] == []
    assert ML.main(["p5"], root=root) == 0
    assert "empty: M6, M8, M10, M12 — nothing measured" in capsys.readouterr().out
    assert ML.main(["p5", "--require-pages"], root=root) == 1
    assert "--require-pages" in capsys.readouterr().out


def test_main_writes_the_json_and_the_table_and_exits_on_failure(tmp_path, capsys):
    root = tree(tmp_path, families=("LAYOUT",))
    md = tmp_path / "ledger.md"
    assert ML.main(["p5", "--slugs", "newtown", "comp", "--md", str(md)], root=root) == 1
    data = json.loads((root / "docs/reports/p5-ledger.json").read_text(encoding="utf-8"))
    assert data["failed"] == ["M2"] and data["head"] == head(root)
    lines = md.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("Measurement ledger — p5 · ") and f"HEAD {head(root)}" in lines[0]
    assert "scope newtown, comp" in lines[0] and "failed: M2" in lines[0]
    assert "stale: none" in lines[0] and "empty: none" in lines[0]
    assert lines[2] == "| # | Measurement | Value | Status | Detail |"
    assert [l.split(" | ")[0] for l in lines[4:]] == ["| M1", "| M2", "| M3", "| M6", "| M8",
                                                     "| M9", "| M10", "| M12", "| M13", "| M18"]
    assert "| M2 | Families registered vs families wired | registered 2 · wired 1 · difference " \
           "{SEM} | FAIL | — |" in lines
    assert "failed: M2" in capsys.readouterr().out


def test_a_project_name_that_is_not_a_slug_exits_2(tmp_path, capsys):
    root = tree(tmp_path)
    assert ML.main(["../x"], root=root) == 2
    assert "measurement-ledger ERROR" in capsys.readouterr().out
    assert not (root / "docs/x-ledger.json").exists()


def test_the_real_repo_ledger_runs():
    out = ML.ledger("p5", ["index"])
    r = rows(out)
    assert r["M2"]["status"] == "PASS", r["M2"]
    assert r["M18"]["value"].endswith(" rules")
    assert all(x["value"] for x in out["rows"])
