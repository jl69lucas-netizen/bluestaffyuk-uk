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
    assert PB.shared_per_page_picks(boards) == []
