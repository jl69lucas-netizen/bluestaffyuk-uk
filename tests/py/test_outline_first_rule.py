"""The outline comes before any component: the user sees it first (the user's ruling, 2026-09-29).

The user must see the research, the research board (angles, strategy, frameworks, the keyword
universe and its distribution) and the full section-by-section outline (every H2 and H3 with its
keywords, word count and purpose) before any component is selected or built for a page. For a
city, the component design pass comes AFTER the outline and only for the sections the outline
needs; for London, the built kit is a menu: the outline decides the sections and the page board
maps each section to a component.

These tests pin that order in `docs/reference/page-run.md` (rows 8, 9 and 10), give the rule its
row in rules/gates.md and data/quality/rule-index.json, and keep CLAUDE.md's project-5 paragraph
naming it. The three approval stops stay three (tests/py/test_page_run.py): showing the outline
is a hold before row 10, approved with the board at STOP 2.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/reference/page-run.md"
RULE_ID = "outline-before-components"
THIS_TEST = "tests/py/test_outline_first_rule.py"
RULING_DATE = "2026-09-29"


def _norm(text):
    return " ".join(text.split())


def _row(n):
    lines = DOC.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("| # | Brief step"))
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        rows.append([_norm(c) for c in line.strip().strip("|").split("|")])
    return rows[n - 1]


def test_the_research_board_shows_the_keyword_universe_and_its_distribution():
    row = " ".join(_row(8))
    assert "keyword universe and its distribution" in row, row


def test_the_outline_lists_every_heading_with_its_keywords_word_count_and_purpose():
    row = _row(9)
    body = " ".join(row[2:4])
    assert "every H2 and H3 with its keywords, word count and purpose" in body, body


def test_the_user_sees_the_outline_before_any_component_is_selected():
    row = _row(9)
    cells = " ".join(row)
    assert "shown to the user before row 10" in cells, cells
    assert "no component is selected or built" in cells, cells
    # a hold, not a fourth approval stop: the stop column keeps its 'none' shape
    assert row[5].startswith("none"), row[5]
    assert "STOP 2" in row[5], row[5]


def test_the_component_row_comes_after_the_outline_and_only_for_its_sections():
    row = _row(10)
    cells = " ".join(row[2:4])
    assert "after the user has seen the outline of row 9" in cells, cells
    assert "only for the sections the outline needs" in cells, cells
    assert "the kit is a menu" in cells, cells
    assert "the outline decides the sections" in cells, cells
    assert "maps each section to a component" in cells, cells


def test_the_rule_is_written_in_the_gates_pack():
    text = (ROOT / "rules/gates.md").read_text(encoding="utf-8")
    m = re.search(rf"---\nid: {RULE_ID}\n(.*?)---\n\n(.*?)(?=\n---\n|\Z)", text, re.S)
    assert m, f"rules/gates.md has no {RULE_ID} block"
    head, body = m.group(1), _norm(m.group(2))
    assert "enforced: test" in head and f"test: {THIS_TEST}" in head, head
    assert RULING_DATE in body and "every project 5 page" in body, body
    assert "page-run.md" in body and "rows 8" in body, body


def test_the_rule_is_indexed_as_tested_by_this_file():
    index = json.loads((ROOT / "data/quality/rule-index.json").read_text(encoding="utf-8"))
    rows = [r for r in index["rules"] if r["id"] == RULE_ID]
    assert len(rows) == 1, rows
    assert rows[0]["enforced"] == "test" and rows[0]["test"] == THIS_TEST, rows[0]
    assert rows[0]["pack"] == "rules/gates.md", rows[0]


def test_claude_md_names_the_rule_in_the_project_5_paragraph():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    para = text[text.index("**Every project 5 page"):]
    para = _norm(para[:para.index("\n\n")])
    assert f"`{RULE_ID}`" in para, para
    assert "outline" in para and "component" in para, para


def test_the_rule_count_is_stated_the_same_everywhere():
    n = len(json.loads((ROOT / "data/quality/rule-index.json").read_text(encoding="utf-8"))["rules"])
    claude = _norm((ROOT / "CLAUDE.md").read_text(encoding="utf-8"))
    quick = _norm((ROOT / "docs/reference/quick-start.md").read_text(encoding="utf-8"))
    assert f"`data/quality/rule-index.json`'s {n} (of which" in claude, n
    assert f"the machine-readable ledger: {n} rules" in quick, n
