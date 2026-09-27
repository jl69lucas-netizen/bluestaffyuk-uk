"""`scripts/measurement_ledger.py` — the brief's measurement ledger as numbers at close.

The brief lists eighteen measurements "that must appear in the close-out, not boxes that get
ticked". BlueStaffyUK held the data for most of them and printed none together. The unit tests
build a small tree in tmp_path — two checks, one scorecard run, two gate:page reports — so they
pin how each row is computed; the last test runs the ledger on this repo.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import measurement_ledger as ML  # noqa: E402

CHECKS_TS = """
register({ id: 'layout-min-font-size', family: 'LAYOUT', severity: 'blocking', describe: 'x' });
register({ id: 'sem-title-case', family: 'SEM', severity: 'advisory', describe: 'y' });
"""


def card(slug, examined, details=()):
    return {"slug": slug, "examined_by_check": examined,
            "details": [{"viewport": 375, "checkId": c, "count": 1, "message": "m"} for c in details]}


def gate_report(verdict="PASS", runs=2, identical=True, dup=(0, 0)):
    return {"runs": runs, "verdict": verdict, "identical": identical, "steps": [
        {"step": "dup-body", "ok": [True, True], "problems": [dup[0], dup[0]], "identical": True},
        {"step": "dup-headers", "ok": [True, True], "problems": [dup[1], dup[1]], "identical": True}]}


def tree(tmp_path, cards=None, reports=None, families=("LAYOUT", "SEM")):
    (tmp_path / "tests/render/checks").mkdir(parents=True)
    (tmp_path / "tests/render/checks/all.ts").write_text(CHECKS_TS, encoding="utf-8")
    (tmp_path / "tests/render/targets.json").write_text(json.dumps(
        {"families_by_page_type": {"location": list(families)}, "deferred_checks": {}}),
        encoding="utf-8")
    sc = tmp_path / "data/quality/scorecards"
    sc.mkdir(parents=True)
    for c in cards if cards is not None else [
            card("uk-locations/newtown", {"layout-min-font-size": 50, "sem-title-case": 4},
                 details=["sem-title-case"]),
            card("comp", {"layout-min-font-size": 30, "sem-title-case": 0})]:
        (sc / (c["slug"].replace("/", "__") + "-2026-09-27.json")).write_text(json.dumps(c),
                                                                             encoding="utf-8")
    (tmp_path / "data/quality/rule-index.json").write_text(json.dumps({"rules": [
        {"id": "a", "enforced": "test"}, {"id": "b", "enforced": "untested"}]}), encoding="utf-8")
    (tmp_path / "data/quality/rework-ledger.json").write_text(json.dumps({"windows": []}),
                                                              encoding="utf-8")
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "newtown"}]), encoding="utf-8")
    gp = tmp_path / "docs/reports/gate-page"
    gp.mkdir(parents=True)
    for key, rep in (reports if reports is not None else
                     {"newtown": gate_report(), "comp": gate_report()}).items():
        (gp / f"{key}.json").write_text(json.dumps(rep), encoding="utf-8")
    llm = tmp_path / "docs/research/llm-intel"
    llm.mkdir(parents=True)
    (llm / "newtown-2026-09-25.json").write_text(json.dumps({"fetched": {"status": "ok"}}),
                                                 encoding="utf-8")
    (tmp_path / "docs/reports/rendered-changes.json").write_text(json.dumps(
        {"base": "abc", "head": "0123456789ab-dirty", "changed": ["uk-locations/newtown", "comp"]}),
        encoding="utf-8")
    return tmp_path


def rows(led):
    return {r["id"]: r for r in led["rows"]}


def test_the_ledger_has_the_ten_rows_in_order(tmp_path):
    led = ML.ledger("p5", ["newtown", "comp"], tree(tmp_path))
    assert [r["id"] for r in led["rows"]] == ["M1", "M2", "M3", "M6", "M8", "M9", "M10", "M12",
                                              "M13", "M18"]
    assert led["scope"] == ["newtown", "comp"] and led["failed"] == []


def test_every_row_is_a_number_or_a_named_barrier(tmp_path):
    r = rows(ML.ledger("p5", ["newtown", "comp"], tree(tmp_path)))
    assert r["M1"]["value"] == "2 checks, 0 at zero (run 2026-09-27, 2 pages)"
    assert r["M2"]["value"] == "registered 2 · wired 2 · difference ∅"
    assert r["M3"]["value"] == "blocking 0 · advisory 1 (run 2026-09-27; never summed)"
    assert r["M6"]["value"] == "2 of 2 pages clean (run 2026-09-27)" and r["M6"]["status"] == "PASS"
    assert r["M8"]["value"] == "2 of 2 pages: >= 2 runs, both clean"
    assert r["M9"]["value"].startswith("NOT FETCHED — ")
    assert r["M10"]["value"] == "body 0 · headers 0 across 2 pages"
    assert r["M12"]["value"] == "1 / 2 (one engine, one query per page)"
    assert r["M12"]["detail"] == "comp: no llm-intel file"
    assert r["M13"]["value"] == "2 (base abc → head 0123456789ab-dirty)"
    assert r["M18"]["value"] == "1 of 2 rules" and r["M18"]["detail"] == "b"


def test_a_check_that_examined_zero_nodes_fails_m1(tmp_path):
    root = tree(tmp_path, cards=[card("comp", {"layout-min-font-size": 3, "sem-title-case": 0})])
    r = rows(ML.ledger("p5", ["comp"], root))
    assert r["M1"]["status"] == "FAIL" and r["M1"]["detail"] == "sem-title-case"
    assert "M1" in ML.ledger("p5", ["comp"], root)["failed"]


def test_a_check_absent_from_every_card_is_reported_not_failed(tmp_path):
    # tests/render/lib/examined.ts: a registered check with no key in any card is "not yet
    # measured" (registered since the last page run) — named, never a FAIL; measured-zero fails.
    root = tree(tmp_path, cards=[card("comp", {"layout-min-font-size": 3})])
    r = rows(ML.ledger("p5", ["comp"], root))
    assert r["M1"]["status"] == "PASS"
    assert r["M1"]["value"] == "1 checks, 0 at zero, 1 not yet measured (run 2026-09-27, 1 pages)"
    assert r["M1"]["detail"] == "not yet measured: sem-title-case"


def test_a_page_rerun_alone_keeps_the_other_pages_newest_cards(tmp_path):
    root = tree(tmp_path)
    one = card("comp", {"layout-min-font-size": 30, "sem-title-case": 2})
    (root / "data/quality/scorecards/comp-2026-09-28.json").write_text(json.dumps(one),
                                                                       encoding="utf-8")
    r = rows(ML.ledger("p5", ["newtown", "comp"], root))
    assert r["M1"]["value"] == "2 checks, 0 at zero (runs 2026-09-27 to 2026-09-28, 2 pages)"


def test_a_family_registered_but_not_wired_fails_m2(tmp_path):
    r = rows(ML.ledger("p5", ["comp"], tree(tmp_path, families=("LAYOUT",))))
    assert r["M2"]["status"] == "FAIL" and r["M2"]["value"].endswith("difference {SEM}")


def test_a_page_with_small_text_fails_m6(tmp_path):
    root = tree(tmp_path, cards=[card("comp", {"layout-min-font-size": 3, "sem-title-case": 1},
                                      details=["layout-min-font-size"])])
    r = rows(ML.ledger("p5", ["comp"], root))
    assert r["M6"]["status"] == "FAIL" and r["M6"]["detail"] == "comp"


def test_a_gate_run_once_or_unstable_fails_m8_and_a_crossover_fails_m10(tmp_path):
    root = tree(tmp_path, reports={"newtown": gate_report(runs=1),
                                   "comp": gate_report(verdict="FAIL", identical=False, dup=(2, 1))})
    r = rows(ML.ledger("p5", ["newtown", "comp"], root))
    assert r["M8"]["status"] == "FAIL" and "newtown: 1 runs" in r["M8"]["detail"]
    assert r["M10"]["status"] == "FAIL" and r["M10"]["value"] == "body 2 · headers 1 across 2 pages"


def test_a_page_with_no_gate_report_fails_m8_and_m10(tmp_path):
    r = rows(ML.ledger("p5", ["newtown", "comp"], tree(tmp_path, reports={"comp": gate_report()})))
    assert r["M8"]["status"] == "FAIL" and r["M10"]["status"] == "FAIL"
    assert r["M10"]["detail"] == "no gate:page report for newtown"


def test_no_scorecards_is_a_named_barrier_and_a_fail(tmp_path):
    r = rows(ML.ledger("p5", ["comp"], tree(tmp_path, cards=[])))
    assert r["M1"]["status"] == "FAIL" and r["M1"]["value"].startswith("NOT FETCHED — ")


def test_main_writes_the_json_and_the_table_and_exits_on_failure(tmp_path, capsys):
    root = tree(tmp_path, families=("LAYOUT",))
    md = tmp_path / "ledger.md"
    assert ML.main(["p5", "--slugs", "newtown", "comp", "--md", str(md)], root=root) == 1
    data = json.loads((root / "docs/reports/p5-ledger.json").read_text(encoding="utf-8"))
    assert data["failed"] == ["M2"]
    table = md.read_text(encoding="utf-8")
    assert table.startswith("| # | Measurement | Value | Status | Detail |")
    assert "failed: M2" in capsys.readouterr().out


def test_the_real_repo_ledger_runs():
    led = ML.ledger("p5", ["index"])
    r = rows(led)
    assert r["M2"]["status"] == "PASS", r["M2"]
    assert r["M18"]["value"].endswith(" rules")
    assert all(x["value"] for x in led["rows"])
