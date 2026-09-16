# tests/test_quality_report.py
#
# The report is what makes "no test, no rule" enforceable rather than aspirational:
# it is the thing that prints the deletion-candidate list every run. If it can
# silently report an empty list, the constraint stops existing.
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import quality_report as Q


CHECKS_TS = """
register({
  id: 'img-srcset-within-2x',
  family: 'IMG',
});
register({
  id: "nav-anchors-resolve",
  family: 'NAV',
});
"""


def test_extracts_check_ids_from_typescript_single_and_double_quoted():
    assert Q.check_ids_from_source(CHECKS_TS) == {"img-srcset-within-2x", "nav-anchors-resolve"}


def test_a_source_with_no_register_calls_yields_nothing_not_a_crash():
    assert Q.check_ids_from_source("// nothing here") == set()


def test_a_test_backed_rule_pointing_at_a_missing_check_is_a_broken_link():
    index = {"judgment_cap": 12, "rules": [
        {"id": "ghost", "enforced": "test", "test": "tests/render/checks/img.ts::ghost"},
    ]}
    assert Q.broken_test_links(index, {"img-srcset-within-2x"}) == ["ghost"]


def test_a_test_backed_rule_pointing_at_a_real_check_is_not_broken():
    index = {"judgment_cap": 12, "rules": [
        {"id": "img-srcset-within-2x", "enforced": "test",
         "test": "tests/render/checks/img.ts::img-srcset-within-2x"},
    ]}
    assert Q.broken_test_links(index, {"img-srcset-within-2x"}) == []


def test_the_delta_follows_the_number_that_is_printed():
    """After the split the headline is page_rate, so the delta must come from page_rate.

    Taking it from the union `rate` would print a movement next to a figure it does not
    describe: in the real 2026-08-03 window the union rose 4.0 points while page rework
    FELL 0.8, so the report would have shown a decline annotated as a regression.
    """
    led = {"windows": [
        {"from": "2026-06-01", "to": "2026-07-01", "rate": 0.228, "page_rate": 0.145},
        {"from": "2026-07-04", "to": "2026-08-03", "rate": 0.267, "page_rate": 0.137},
    ]}
    cur, delta = Q.trend(led)
    assert cur["from"] == "2026-07-04"
    assert delta < 0, "page rework fell; the delta must say so"
    assert abs(delta - (0.137 - 0.145)) < 1e-9


def test_a_pre_split_window_pair_still_gets_a_delta_from_the_union_rate():
    """Windows recorded before the split carry no page_rate. Falling back beats crashing."""
    led = {"windows": [
        {"from": "2026-05-01", "to": "2026-06-01", "rate": 0.248},
        {"from": "2026-06-01", "to": "2026-07-01", "rate": 0.228},
    ]}
    _, delta = Q.trend(led)
    assert abs(delta - (0.228 - 0.248)) < 1e-9


def test_a_rule_backed_by_a_real_TEST_FILE_is_not_a_broken_link():
    """Not every rule is enforced by a render check.

    `no-test-no-rule` is held up by this very file. Before the file branch existed the
    validator only knew render-check ids, so a rule pointing at a real, passing pytest
    file was reported BROKEN and quality_report.py exited non-zero — which would have
    pushed the next person to either delete the rule or fake a check id for it.
    """
    index = {"judgment_cap": 12, "rules": [
        {"id": "no-test-no-rule", "enforced": "test", "test": "tests/py/test_quality_report.py"},
    ]}
    assert Q.broken_test_links(index, set()) == []


def test_a_rule_pointing_at_a_test_file_that_does_NOT_exist_is_still_broken():
    """The file branch must be able to fail, or it is an exemption rather than a check."""
    index = {"judgment_cap": 12, "rules": [
        {"id": "phantom", "enforced": "test", "test": "tests/py/test_deleted_months_ago.py"},
    ]}
    assert Q.broken_test_links(index, set()) == ["phantom"]


def test_a_rule_with_neither_a_test_nor_a_judgment_class_is_a_deletion_candidate():
    index = {"judgment_cap": 12, "rules": [
        {"id": "orphan", "family": "SEM"},
        {"id": "kept", "enforced": "judgment", "why": "because"},
    ]}
    assert Q.deletion_candidates(index) == ["orphan"]


def test_a_judgment_rule_with_no_why_is_a_deletion_candidate():
    """The `why` is the whole cap. A judgment class you can join without stating
    why a test cannot exist is an exemption anyone can grant themselves."""
    index = {"judgment_cap": 12, "rules": [{"id": "lazy", "enforced": "judgment"}]}
    assert Q.deletion_candidates(index) == ["lazy"]


def test_the_judgment_cap_is_reported_when_exceeded():
    index = {"judgment_cap": 2, "rules": [
        {"id": f"j{i}", "enforced": "judgment", "why": "w"} for i in range(3)
    ]}
    assert Q.judgment_overflow(index) == (3, 2)
    ok = {"judgment_cap": 3, "rules": [
        {"id": f"j{i}", "enforced": "judgment", "why": "w"} for i in range(3)
    ]}
    assert Q.judgment_overflow(ok) is None


def test_worst_family_ranks_by_rows_not_instances():
    """Rows are comparable across families; instances are not. Ranking by instances
    would put whichever check happens to enumerate the most nodes on top forever."""
    cards = [
        {"defects": {"NAV": 1, "IMG": 3}, "instances": {"NAV": 400, "IMG": 3}},
        {"defects": {"NAV": 1, "IMG": 3}, "instances": {"NAV": 400, "IMG": 3}},
    ]
    assert Q.worst_family(cards)[0] == "IMG"


def test_open_overrides_are_collected_with_their_page():
    cards = [
        {"slug": "a", "overrides": [{"checkId": "img-srcset-within-2x", "reason": "regen queued"}]},
        {"slug": "b", "overrides": []},
    ]
    assert Q.open_overrides(cards) == [("a", "img-srcset-within-2x", "regen queued")]


def test_latest_card_per_slug_wins(tmp_path):
    """Two dated scorecards for one page must contribute once, most recent."""
    d = tmp_path / "scorecards"
    d.mkdir()
    (d / "x-2026-07-31.json").write_text(json.dumps({"slug": "x", "date": "2026-07-31", "total": 9}))
    (d / "x-2026-08-01.json").write_text(json.dumps({"slug": "x", "date": "2026-08-01", "total": 2}))
    cards = Q.load_scorecards(d)
    assert [c["total"] for c in cards] == [2]


def test_trend_reports_the_delta_between_the_two_most_recent_windows():
    ledger = {"windows": [
        {"from": "2026-05-01", "to": "2026-07-31", "rate": 0.248},
        {"from": "2026-07-02", "to": "2026-08-01", "rate": 0.200},
    ]}
    cur, delta = Q.trend(ledger)
    assert cur["rate"] == 0.200
    assert round(delta, 3) == -0.048


def test_trend_with_one_window_has_no_delta():
    ledger = {"windows": [{"from": "a", "to": "b", "rate": 0.3}]}
    cur, delta = Q.trend(ledger)
    assert cur["rate"] == 0.3
    assert delta is None


def test_registry_check_ids_include_python_audit_ids(tmp_path):
    import quality_report as Q
    ids = Q.registry_check_ids()
    assert "term-budget-per-page" in ids, "evidence_audit.py ids must count as backing tests"
    assert "review-attribution-unique" in ids
