"""scripts/outline_matrix.py — the outline deliverable, as a section matrix (STOP 2).

It carries the approval status, the word target and its source, the heading census (one H1,
no skipped level) and the distribution matrix: #, Section with its H2–H6 tree, Framework,
Words, Keywords, Cat A/B/C, Why (grounded in the research board), Image. The known-bad
fixture (`tests/py/fixtures/outline_matrix/known_bad.json`) must fail: a row with no Cat, a
row with no Why, a heading that skips from H2 to H4, and a census with no H3 at all.
"""
import copy
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import outline_matrix as OM  # noqa: E402

FIX = ROOT / "tests/py/fixtures/outline_matrix"


def _load(name):
    return json.loads((FIX / name).read_text(encoding="utf-8"))


def _research():
    return OM.research_for(_load("good.json"))


def test_the_good_fixture_passes():
    assert OM.validate(_load("good.json"), _research()) == []


def test_the_known_bad_fixture_fails_on_each_planted_defect():
    problems = OM.validate(_load("known_bad.json"), _research())
    assert any("section 3: no Cat" in p for p in problems), problems
    assert any("section 4: no Why" in p for p in problems), problems
    assert any("sits under an H2 — a skipped heading level" in p for p in problems), problems
    assert any("heading census: skips H3" in p for p in problems), problems


def test_the_cli_exits_1_on_the_known_bad_fixture(capsys):
    assert OM.main(["fixture-city", "--record", str(FIX / "known_bad.json"), "--check"]) == 1
    assert capsys.readouterr().out.count("  FAIL ") >= 4


def test_exactly_one_h1():
    rec = _load("good.json")
    rec["sections"][2]["headings"].append({"level": 1, "text": "A Second H1", "children": []})
    assert any("exactly one H1" in p for p in OM.validate(rec, _research()))


def test_a_b_or_c_why_resolves_on_the_research_board():
    rec = _load("good.json")
    rec["sections"][2]["why_source"] = "universal_gaps[9]"
    assert any("does not resolve" in p for p in OM.validate(rec, _research()))
    rec = _load("good.json")
    rec["sections"][3]["why_source"] = "content_gap[0]"          # a B row must cite a competitor
    assert any("a B row (competitor-match)" in p for p in OM.validate(rec, _research()))
    rec = _load("good.json")
    rec["sections"][2]["why"] = "—"
    assert any("grounded in the research board" in p for p in OM.validate(rec, _research()))


def test_keywords_come_from_the_research_boards_universe():
    rec = _load("good.json")
    rec["sections"][3]["keywords"]["primary"] = ["an invented keyword"]
    assert any("not in the research board's keyword universe" in p
               for p in OM.validate(rec, _research()))


def test_a_heading_carries_an_image_and_a_primary_keyword():
    rec = _load("good.json")
    rec["sections"][3]["image"] = "—"
    rec["sections"][2]["keywords"] = {}
    problems = OM.validate(rec, _research())
    assert any("section 4: a section with a heading carries an image" in p for p in problems)
    assert any("section 3: a section with a heading has a primary keyword" in p for p in problems)


def test_the_word_target_has_a_source_and_the_matrix_sums_inside_it():
    rec = _load("good.json")
    rec["word_target"] = {"min": 2000, "max": 3000}
    problems = OM.validate(rec, _research())
    assert any("word_target.source" in p for p in problems)
    assert any("sums to 1100 words, outside the target" in p for p in problems)


def test_the_outline_waits_for_an_approved_research_board(tmp_path):
    research = json.loads((ROOT / "tests/py/fixtures/research_board/record.json").read_text())
    research["approval"] = None
    path = tmp_path / "research.json"
    path.write_text(json.dumps(research))
    rec = _load("good.json")
    rec["research_board"] = str(path)
    with pytest.raises(OM.OutlineError, match="unapproved"):
        OM.research_for(rec)


def test_the_matrix_renders_every_column_with_copy_buttons_and_a_md_download(tmp_path):
    html_path, md_path = OM.build(_load("good.json"), _research(), tmp_path)
    md = md_path.read_text(encoding="utf-8")
    assert "Status: **AWAITING APPROVAL — STOP 2**" in md
    assert "**Target:** 900–1,400 words (source: " in md and "the matrix sums to 1,100 words" in md
    assert "**Heading census:** 1 H1 · 3 H2 · 2 H3 · 1 H4 · 1 H5 · 1 H6" in md
    assert "| # | Section | Framework | Words | Keywords | Cat | Why | Image |" in md
    assert "H2 How Do We Deliver to Fixture City? (H3 What Does Delivery Cost? (H4" in md
    assert "(from `serp.results[1]`)" in md
    for n in range(1, 6):
        assert f"\n## §{n} " in md, n
    page = html_path.read_text(encoding="utf-8")
    assert "Copy section" in page and 'id="dl-md"' in page
    assert page.count('type="text/markdown" data-title=') == 1 + 1 + 5 + 1


def test_approval_is_stamped_with_the_hash_and_goes_stale_on_an_edit():
    rec = copy.deepcopy(_load("good.json"))
    assert OM.approval_state(rec) == "unapproved"
    rec = OM.approve(rec, "tests/py/fixtures/outline_matrix/answers.json", today="2026-09-29")
    assert OM.approval_state(rec) == "approved"
    assert rec["approval"]["research_hash"] == OM.RB.current_hash(_research())
    assert "APPROVED 2026-09-29" in OM.status_line(rec)
    rec["sections"][2]["words"] += 1
    assert OM.approval_state(rec) == "stale"


def test_the_outline_is_not_approved_with_the_research_boards_answers():
    with pytest.raises(OM.OutlineError, match="same answers"):
        OM.approve(_load("good.json"), "tests/py/fixtures/research_board/answers.json")
