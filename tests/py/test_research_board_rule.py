"""A research board the user picks from comes before every project 5 page's outline.

The user's ruling (2026-09-27), asked when they get to choose the page, the angles, the
frameworks, the keyword universe and its distribution and the strategy: "a research board
first" — "Its a must on all pages, starting from research, fan-out query, all sprints, etc".

Before it, `docs/reference/page-run.md` row 8 made STOP 1 apply "only for a page with no row
in the approved strategy", so a city with a strategy row reached the page board with its angle
already decided. These tests pin the opposite: row 8 is STOP 1 on every page, the research board
carries the research and the options, the picks are recorded before row 9, rows 9 and 10 cite
them, every routing point sends a page through it, and the rule has its row in rules/gates.md
and data/quality/rule-index.json.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/reference/page-run.md"
RULE_ID = "research-board-before-outline"
THIS_TEST = "tests/py/test_research_board_rule.py"
RULING = "Its a must on all pages"
# The wording of an exemption: any of these on row 8, or anywhere a page is routed, lets a
# page with a strategy row skip the board.
EXEMPTION = re.compile(
    r"only (?:for|to) a page (?:with|that)|no row in the approved|strategy does not name"
    r"|skip(?:s|ped)? (?:the )?research board|research board[^.\n]{0,40}\bunless\b",
    re.I)
ROUTING = (
    ".claude/skills/bsuk-location-page-builder/SKILL.md",
    ".claude/skills/bsuk-comparison-page-builder/SKILL.md",
    ".claude/skills/bsuk-blog-post/SKILL.md",
    ".claude/skills/grill-me/SKILL.md",
    ".claude/agents/bsuk-location-builder.md",
    "docs/reference/WORKFLOW.md",
)
# What the research board carries (the controller's brief, Task 12b).
CARRIES = (
    "top 5 on Google and Bing", "section count", "word target", "NOT FETCHED",
    "PAA", "Reddit", "LLM intel",
    "grouped by intent", "four extra keyword types", "entities",
    "3 angle options", "`bsuk-angle-agent`",
    "2–3 strategy directions", "`bsuk-strategy-synthesizer`",
    "`framework-*`", "`bsuk-content-architect`",
    "(Recommended)", "trade-off", "working rule 4",
)


def _norm(text):
    return " ".join(text.split())


def _run_rows():
    lines = DOC.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("| # | Brief step"))
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


def _row(n):
    return _run_rows()[n - 1]


def _section(head):
    text = DOC.read_text(encoding="utf-8")
    assert head in text, f"page-run.md has no {head!r} section"
    return re.split(r"\n#{2,3} ", text[text.index(head) + len(head):], maxsplit=1)[0]


def test_row_8_is_stop_1_the_research_board_on_every_page():
    row = _row(8)
    assert row[5].startswith("STOP 1"), row[5]
    assert "research board" in row[5] and "every project 5 page" in row[5], row[5]
    assert "research board" in row[2], row[2]


def test_no_exemption_for_a_page_with_a_strategy_row():
    row = " | ".join(_row(8))
    assert not EXEMPTION.search(row), f"row 8 still exempts a page: {EXEMPTION.search(row)[0]!r}"
    diffs = _norm(DOC.read_text(encoding="utf-8").split("## Deliberate differences")[1])
    assert "applies only to a page with no row" not in diffs, "the old exemption is still recorded"
    assert "STOP 1 (the research board) applies to every project 5 page" in diffs, diffs


def test_the_strategy_row_is_an_option_on_the_board_never_a_reason_to_skip_it():
    body = _norm(_row(8)[2] + " " + _section("### Row 8 steps"))
    assert "docs/superpowers/sessions/2026-09-25-location-pages-strategy.md" in body
    assert "one of the strategy directions" in body, body


def test_the_research_board_carries_the_research_and_the_options():
    body = _norm(_row(8)[2] + " " + _row(8)[3] + " " + _section("### Row 8 steps"))
    missing = [tok for tok in CARRIES if tok not in body]
    assert missing == [], f"the research board does not name: {missing}"


def test_the_picks_are_recorded_before_row_9_and_the_board_is_built_by_its_script():
    row = _row(8)
    steps = _norm(_section("### Row 8 steps"))
    assert "scripts/answer_board_batch.py" in steps, steps
    assert "docs/reference/answer-board/answers/" in row[3], row[3]
    # the tooling exists now (2026-09-29): the board is built from its record by a script
    assert "python3 scripts/research_board.py <slug>" in steps, steps
    assert "tooling: built with the first page" not in _norm(" ".join(row) + " " + steps)
    assert "comes after row 8's picks" in _norm(_row(9)[2]), _row(9)[2]


def test_the_outline_and_the_page_board_cite_the_picks():
    for n in (9, 10):
        cells = _norm(" ".join(_row(n)[2:4]))
        assert "research-board picks" in cells, f"row {n} does not cite the picks: {cells}"


def test_every_routing_point_sends_the_page_through_the_research_board():
    bad = []
    for rel in ROUTING:
        text = _norm((ROOT / rel).read_text(encoding="utf-8"))
        if not ("research board" in text and "`docs/reference/page-run.md` row 8" in text
                and "before the outline" in text):
            bad.append(f"{rel}: does not route through the research board")
        if EXEMPTION.search(text):
            bad.append(f"{rel}: exemption {EXEMPTION.search(text)[0]!r}")
    assert bad == [], "\n  ".join(bad)


def test_the_rule_is_written_in_the_gates_pack():
    text = (ROOT / "rules/gates.md").read_text(encoding="utf-8")
    m = re.search(rf"---\nid: {RULE_ID}\n(.*?)---\n\n(.*?)(?=\n---\n|\Z)", text, re.S)
    assert m, f"rules/gates.md has no {RULE_ID} block"
    head, body = m.group(1), _norm(m.group(2))
    assert "enforced: test" in head and f"test: {THIS_TEST}" in head, head
    assert RULING in body and "every project 5 page" in body, body


def test_the_rule_is_indexed_as_tested_by_this_file():
    index = json.loads((ROOT / "data/quality/rule-index.json").read_text(encoding="utf-8"))
    rows = [r for r in index["rules"] if r["id"] == RULE_ID]
    assert len(rows) == 1, rows
    assert rows[0]["enforced"] == "test" and rows[0]["test"] == THIS_TEST, rows[0]
    assert rows[0]["pack"] == "rules/gates.md", rows[0]
