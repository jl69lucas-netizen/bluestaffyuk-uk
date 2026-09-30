"""Working rule 16's uniqueness half, as a gate (Known Issues 33 and 35; user ruling R12,
2026-09-23).

"No two pages share the same hero layout or the same counter strip" had no check: the three
guides all took H-GD3 and the three utility pages all took H-UT1 without anything failing,
because `ledger-tuple-owned` signs hero + faq + table + takeaway together and the pages
differed elsewhere. `pageboard.shared_per_page_picks()` reads every record's hero and counter
pick IN FORCE — the pick the built page renders — and reports any arrangement two pages share.
The user exempted the three utility pages by name: they may share with each other, never with
any other page.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import pageboard as PB  # noqa: E402

UTILITY = ("privacy-policy-uk", "thank-you-blue-staffy-puppies-journey",
           "uk-blue-staffy-breeders-contact")


def rec(hero=None, counter=None, layout="interior-guide", live=None, prev=None, status="approved"):
    sections = [{"id": "top", "shape": "hero", "options": {"pick": hero}}]
    if counter is not None:
        sections.append({"id": "stats", "shape": "stats", "options": {"pick": counter}})
    return {"meta": {"layout_type": layout, "status": status}, "sections": sections,
            "approval": {"picks": live} if live is not None else None,
            "approval_previous": {"picks": prev} if prev is not None else None}


def test_two_pages_sharing_a_hero_are_reported():
    out = PB.shared_per_page_picks({"a": rec("H-GD3"), "b": rec("H-GD3"), "c": rec("H-GD1")})
    assert out == [("hero", "H-GD3", ["a", "b"])]


def test_two_pages_sharing_a_counter_are_reported():
    out = PB.shared_per_page_picks({"a": rec("H-GD1", "C-GD1"), "b": rec("H-GD2", "C-GD1")})
    assert out == [("stats", "C-GD1", ["a", "b"])]


def test_the_exempt_utility_pages_may_share_with_each_other():
    boards = {s: rec("H-UT1", "C-UT1", layout="interior-utility") for s in UTILITY}
    assert PB.shared_per_page_picks(boards) == []


def test_an_exempt_page_sharing_with_any_other_page_is_reported():
    boards = {UTILITY[0]: rec("H-UT1", layout="interior-utility"),
              "about": rec("H-UT1", layout="interior-about")}
    assert PB.shared_per_page_picks(boards) == [("hero", "H-UT1", ["about", UTILITY[0]])]


def test_a_draft_and_a_record_before_rule_16_are_not_judged():
    boards = {"a": rec("S1", layout=None), "b": rec("S1", layout=None),
              "c": rec("H-GD3", status="draft"), "d": rec("H-GD3")}
    assert PB.shared_per_page_picks(boards) == []


def test_the_pick_in_force_is_the_one_the_page_renders():
    # pickedStyle()'s order: the live approval, the section's own pick, the carried approval.
    assert PB.pick_in_force(rec("H-GD2", live={"top": "H-GD1"}, prev={"top": "H-GD3"}), "top") == "H-GD1"
    assert PB.pick_in_force(rec("H-GD2", prev={"top": "H-GD3"}), "top") == "H-GD2"
    assert PB.pick_in_force(rec(None, prev={"top": "H-GD3"}), "top") == "H-GD3"


def test_the_exemption_is_the_three_utility_pages_by_name():
    assert tuple(PB.RULE16_EXEMPT) == UTILITY
    rule = re.search(r"^16\. \*\*.*?(?=^### |\Z)", (ROOT / "CLAUDE.md").read_text(encoding="utf-8"),
                     re.M | re.S).group(0)
    flat = " ".join(rule.split())
    for slug in UTILITY:
        assert f"/{slug}/" in flat, slug
    assert "tests/py/test_rule16_gate.py" in flat


def test_no_two_real_pages_share_a_hero_or_a_counter():
    boards = {}
    for f in sorted((ROOT / "data" / "boards").glob("*.json")):
        b = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(b, dict) and "sections" in b and "meta" in b:
            boards[f.stem] = b
    judged = [s for s, b in boards.items() if b["meta"].get("layout_type")
              and b["meta"].get("status") != "draft"]
    assert len(judged) >= 12, judged
    shared = PB.shared_per_page_picks(boards)
    assert shared == [], ("working rule 16: these hero/counter arrangements are worn by more than "
                          "one page outside the utility exemption — re-board one of each pair:\n  "
                          + "\n  ".join(f"{shape} {pick}: {', '.join(slugs)}"
                                         for shape, pick, slugs in shared))


# ── the same rule at the board gate and at approval (R12 review) ────────────────────────────
#
# pytest alone catches a shared pick only when someone runs the suite; the board gate is what
# a page is built behind, and board_approve.py is where a pick first becomes the approval.

def named(slug, *a, **k):
    r = rec(*a, **k)
    r["meta"]["slug"] = slug
    return r


def test_the_board_gate_fails_a_record_that_wears_another_pages_hero():
    boards = {"a": named("a", "H-GD3", "C-GD1"), "b": named("b", "H-GD3", "C-GD2")}
    f = PB.rule16_findings(boards["b"], boards)
    assert [(x["check"], x["sev"]) for x in f] == [("rule16-shared", "FAIL")]
    assert f[0]["msg"] == "hero H-GD3 is already worn by a; re-board one of them (working rule 16)"


def test_the_record_under_the_gate_stands_in_for_its_own_file():
    # The file on disk says H-GD2; the record being gated says H-GD3, which `a` wears.
    boards = {"a": named("a", "H-GD3"), "b": named("b", "H-GD2")}
    assert [x["msg"].split(" is")[0] for x in PB.rule16_findings(named("b", "H-GD3"), boards)] \
        == ["hero H-GD3"]
    assert PB.rule16_findings(named("b", "H-GD1"), boards) == []


def test_the_board_gate_passes_an_exempt_page_and_fails_it_beside_any_other():
    boards = {s: named(s, "H-UT1", "C-UT1", layout="interior-utility") for s in UTILITY}
    assert PB.rule16_findings(boards[UTILITY[2]], boards) == []
    boards["about"] = named("about", "H-UT1", layout="interior-about")
    msgs = [x["msg"] for x in PB.rule16_findings(boards[UTILITY[2]], boards)]
    assert msgs == [f"hero H-UT1 is already worn by about, {UTILITY[0]}, {UTILITY[1]}; "
                    "re-board one of them (working rule 16)"]


def test_board_gate_cli_prints_the_rule16_fail_and_exits_1(monkeypatch, capsys):
    import pytest
    import board_gate as BG
    boards = {"a": named("a", "H-GD3"), "b": named("b", "H-GD3")}
    board = dict(boards["b"], assets=[])
    monkeypatch.setattr(PB, "load_board", lambda slug: board)
    monkeypatch.setattr(PB, "load_all_boards", lambda: boards)
    monkeypatch.setattr(PB, "load_ontology", lambda: {})
    monkeypatch.setattr(PB, "load_ledger", lambda: {"pages": {}})
    monkeypatch.setattr(PB, "live_headings", lambda: {})
    monkeypatch.setattr(PB, "gate_findings", lambda *a, **k: [])
    monkeypatch.setattr(PB, "all_headings", lambda b: [])
    # "b" is a new-page slug, so the STOP 2 gate would add outline-unapproved: these tests
    # are about rule 16, so the outline is taken as approved (tests/py/test_outline_approval.py).
    monkeypatch.setattr(BG, "outline_findings", lambda slug: [])
    monkeypatch.setattr(sys, "argv", ["board_gate.py", "b"])
    for s in board["sections"]:
        s.setdefault("entities", [])
    with pytest.raises(SystemExit) as e:
        BG.main()
    out = capsys.readouterr().out
    assert e.value.code == 1, out
    assert "FAIL rule16-shared" in out and "hero H-GD3 is already worn by a" in out, out
    assert "rule 16: 2 records judged" in out.splitlines(), out
    assert out.rstrip().endswith("1 FAIL · 0 WARN"), out


def test_board_gate_cli_says_when_rule16_judged_nothing(monkeypatch, capsys):
    """A gate that examines nothing is not a pass (bsuk-gate-integrity): with every record a
    draft, the rule-16 line says so instead of printing a bare zero beside 0 FAIL."""
    import pytest
    import board_gate as BG
    boards = {"a": named("a", "H-GD3", status="draft"), "b": named("b", "H-GD3", status="draft")}
    board = dict(boards["b"], assets=[])
    monkeypatch.setattr(PB, "load_board", lambda slug: board)
    monkeypatch.setattr(PB, "load_all_boards", lambda: boards)
    monkeypatch.setattr(PB, "load_ontology", lambda: {})
    monkeypatch.setattr(PB, "load_ledger", lambda: {"pages": {}})
    monkeypatch.setattr(PB, "live_headings", lambda: {})
    monkeypatch.setattr(PB, "gate_findings", lambda *a, **k: [])
    monkeypatch.setattr(PB, "all_headings", lambda b: [])
    # "b" is a new-page slug, so the STOP 2 gate would add outline-unapproved: these tests
    # are about rule 16, so the outline is taken as approved (tests/py/test_outline_approval.py).
    monkeypatch.setattr(BG, "outline_findings", lambda slug: [])
    monkeypatch.setattr(sys, "argv", ["board_gate.py", "b"])
    for s in board["sections"]:
        s.setdefault("entities", [])
    with pytest.raises(SystemExit) as e:
        BG.main()
    out = capsys.readouterr().out
    assert e.value.code == 0, out
    assert "rule 16: 0 records judged — examined nothing, not a pass" in out.splitlines(), out


def test_rule16_judged_counts_what_the_gate_judges():
    boards = {"a": named("a", "H-GD3"), "b": named("b", "H-GD1", status="draft"),
              "c": named("c", "H-GD2", layout=None)}
    assert PB.rule16_judged(boards) == ["a"]
    assert PB.rule16_judged(boards, named("b", "H-GD1")) == ["a", "b"]


def test_every_real_record_passes_the_rule16_gate():
    boards = PB.load_all_boards()
    judged = {s: b for s, b in boards.items()
              if b["meta"].get("layout_type") and b["meta"].get("status") != "draft"}
    assert len(judged) >= 12, sorted(judged)
    bad = {s: [x["msg"] for x in PB.rule16_findings(b, boards)] for s, b in judged.items()}
    assert {s: m for s, m in bad.items() if m} == {}


def test_approval_refuses_a_pick_that_creates_a_share():
    import board_approve as BA
    boards = {"a": named("a", "H-GD3", "C-GD1"), "b": named("b", None, None, status="draft")}
    after = named("b", "H-GD3", "C-GD2")
    assert BA.rule16_refusals(boards["b"], after, boards) == [
        "hero H-GD3 is already worn by a; re-board one of them (working rule 16)"]
    assert BA.rule16_refusals(boards["b"], named("b", "H-GD1", "C-GD2"), boards) == []


def test_approval_does_not_refuse_a_share_that_was_already_there():
    # A share the record already had is the gate's to fail, not a new pick's to refuse:
    # re-running an approval must not become impossible because of an older finding.
    import board_approve as BA
    boards = {"a": named("a", "H-GD3"), "b": named("b", "H-GD3", live={"top": "H-GD3"})}
    assert BA.rule16_refusals(boards["b"], named("b", "H-GD3", live={"top": "H-GD3"}), boards) == []


def test_a_reboarded_page_may_not_repick_the_arrangement_it_was_reboarded_to_leave():
    # A re-board clears the live approval and carries the old picks in `approval_previous`;
    # the carried H-GD3 is the share the re-board exists to END, not one the page may keep.
    import board_approve as BA
    boards = {"a": named("a", "H-GD3"),
              "b": named("b", None, prev={"top": "H-GD3"}, status="boarded")}
    assert PB.pick_in_force(boards["b"], "top") == "H-GD3"
    assert BA.rule16_refusals(boards["b"], named("b", "H-GD3", live={"top": "H-GD3"}), boards) == [
        "hero H-GD3 is already worn by a; re-board one of them (working rule 16)"]
    assert BA.rule16_refusals(boards["b"], named("b", "H-GD1", live={"top": "H-GD1"}), boards) == []


def test_approval_lets_the_utility_pages_share_with_each_other():
    import board_approve as BA
    boards = {s: named(s, "H-UT1", "C-UT1", layout="interior-utility") for s in UTILITY[:2]}
    boards[UTILITY[2]] = named(UTILITY[2], None, None, layout="interior-utility", status="draft")
    after = named(UTILITY[2], "H-UT1", "C-UT1", layout="interior-utility")
    assert BA.rule16_refusals(boards[UTILITY[2]], after, boards) == []
