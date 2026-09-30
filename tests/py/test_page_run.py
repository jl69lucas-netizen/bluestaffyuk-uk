"""`docs/reference/page-run.md` — the ordered per-page run for project 5 pages.

The page-build brief is a workflow run before every page: a target block, the research, the
plan, the Asset Gate, the build, the gates, the close. BlueStaffyUK had every part of it
spread over a dozen files and no single run. Project 5 walks that run for 30-odd pages, and
a run that lives across twelve files is the one that gets skipped on page 14.

These tests pin the SHAPE of the run rather than its prose: every brief step it must cover,
in order; a command and a failing gate on every row; exactly four approval stops (the research
board, the outline, the page board, the Asset Gate — the user's ruling, 2026-09-29); a builder,
route and profile per page type that the scripts actually accept; and the checker that
keeps every name in it real.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_audit  # noqa: E402
import final_page_audit  # noqa: E402
import workflow_ref_check as wrc  # noqa: E402

DOC = ROOT / "docs/reference/page-run.md"
HEADER = ("#", "Brief step", "BSUK command, skill or board block", "Deliverable",
          "Gate that fails", "Approval stop")
# The brief sections a page run walks through. §1 and §3 are standing law and the sprint list
# (CLAUDE.md, rules/, WORKFLOW.md); §2 is routing, whose session-open row opens the run; §23 is
# the deliverables list below the table; §24–§26 are the reference library, open flags and the
# web tool — none of them is a step of one page's run.
STEPS = [0, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
# Global plugin skills the user ruled mandatory on every project 5 page (2026-09-26), and the
# session-open skill the brief's routing names. Invoked by exactly these names.
HARDEN_SKILLS = ("impeccable:impeccable", "frontend-design:frontend-design")
VERIFY_SKILL = "superpowers:verification-before-completion"
PLAN_SKILL = "superpowers:writing-plans"
BUILDER_SKILLS = (".claude/skills/bsuk-location-page-builder/SKILL.md",
                  ".claude/skills/bsuk-comparison-page-builder/SKILL.md",
                  ".claude/skills/bsuk-blog-post/SKILL.md")
RUNNABLE = re.compile(r"npm run [\w:-]+|scripts/\w+\.py|\bbsuk-[a-z-]+|grill-me"
                      r"|session-closer|board block|block \d")
GATE = re.compile(r"npm run [\w:-]+|python3 scripts/\w+\.py|tests/py/test_\w+\.py"
                  r"|scripts/\w+\.py")


def _rows(text, header):
    """The body rows of the first markdown table whose header row is `header`."""
    lines = text.splitlines()
    want = "| " + " | ".join(header) + " |"
    start = lines.index(want)
    out = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        out.append([c.strip() for c in line.strip().strip("|").split("|")])
    return out


def _run_rows():
    return _rows(DOC.read_text(encoding="utf-8"), HEADER)


def _sections(cell):
    """§9–§10 -> [9, 10]; §0 Target Block -> [0]."""
    m = re.match(r"§(\d+)(?:\s*[–-]\s*§(\d+))?", cell)
    assert m, f"a Brief step cell must open with its § number: {cell!r}"
    lo = int(m.group(1))
    hi = int(m.group(2) or lo)
    return list(range(lo, hi + 1))


def test_the_run_table_exists_with_six_columns():
    rows = _run_rows()
    assert len(rows) >= 15, f"only {len(rows)} rows — the run table stopped parsing"
    bad = [r for r in rows if len(r) != len(HEADER) or not all(r)]
    assert bad == [], f"every row needs all six cells filled: {bad}"


def test_rows_are_numbered_one_to_n():
    assert [int(r[0]) for r in _run_rows()] == list(range(1, len(_run_rows()) + 1))


def test_the_run_opens_with_the_session_open_row():
    first = _run_rows()[0]
    assert first[1].startswith("§2 Session open"), first[1]
    assert "grill-me" in first[2] and f"`{PLAN_SKILL}`" in first[2], first[2]
    assert "builder skill" in first[2], first[2]


def test_every_brief_step_is_covered_in_brief_order():
    rows = _run_rows()
    seen = []
    for r in rows[1:]:
        seen += _sections(r[1])
    assert seen == sorted(seen), f"after the session opens, the run walks the brief out of order: {seen}"
    missing = sorted(set(STEPS) - set(seen) - set(_sections(rows[0][1])))
    assert missing == [], f"brief steps with no row in the run: {missing}"


def test_every_row_names_something_to_run():
    bad = [r[0] for r in _run_rows() if not RUNNABLE.search(r[2])]
    assert bad == [], f"rows whose command cell names no command, skill or board block: {bad}"


# A gate cell is honest about WHEN its gate fires: a command the row runs itself that nothing
# re-runs is "advisory:"; a check that fires later in the run says "enforced at row N by".
LABEL = re.compile(r"^(advisory: |enforced at row (\d+) by )")
LABELLED_ROWS = (1, 2, 3, 7, 8, 11)


def test_every_row_names_the_gate_that_fails():
    bad = [r[0] for r in _run_rows() if not GATE.search(r[4])]
    assert bad == [], f"rows with no failing gate — a step nothing checks is optional: {bad}"


def test_a_gate_that_does_not_fire_at_its_own_row_says_so():
    rows = _run_rows()
    unlabelled = [n for n in LABELLED_ROWS if not LABEL.match(rows[n - 1][4])]
    assert unlabelled == [], f"gate cells that must say 'advisory:' or 'enforced at row N by': {unlabelled}"
    for r in rows:
        m = LABEL.match(r[4])
        if m and m.group(2):
            assert int(m.group(2)) > int(r[0]), f"row {r[0]} is enforced at an earlier row: {r[4]!r}"


def test_exactly_four_approval_stops_in_order():
    stops = []
    for r in _run_rows():
        cell = r[5]
        m = re.match(r"STOP (\d)\b", cell)
        if m:
            stops.append(int(m.group(1)))
        else:
            assert cell.startswith(("none", "PREVIEW")), (
                f"row {r[0]}: a stop is 'none', 'PREVIEW' or 'STOP n': {cell!r}")
    assert stops == [1, 2, 3, 4], (
        f"the run stops for the breeder exactly four times, in order (WORKFLOW.md): {stops}")


def test_the_two_harden_passes_are_named_mandatory_rows_that_preview_only_a_visual_change():
    preview = [r for r in _run_rows() if r[5].startswith("PREVIEW")]
    assert [r[1].split(" ")[0] for r in preview] == ["§18", "§18"], preview
    for row, skill in zip(preview, HARDEN_SKILLS):
        assert f"`{skill}`" in row[2], f"row {row[0]} does not invoke {skill} by name"
        assert "375 / 768 / 1280" in row[2] or "same three widths" in row[2], row[2]
        assert "painting browser" in row[2], row[2]
        assert "data/page-runs/<slug>.json" in row[3], row[3]
        assert "working rule 6" in row[5] and "palette" in row[5], row[5]


def test_verification_before_completion_closes_the_gates_and_the_session():
    rows = [r for r in _run_rows() if f"`{VERIFY_SKILL}`" in r[2]]
    assert [r[1].split(" ")[0] for r in rows] == ["§19", "§22"], [r[1] for r in rows]
    gate_row = rows[0]
    steps = " ".join(_steps(int(gate_row[0])))
    assert "npm run -s check:all" in steps and "npm run gate:page -- <slug>" in steps, steps
    assert "verification_before_completion" in gate_row[3], gate_row[3]


def test_the_four_stops_are_the_research_board_the_outline_the_board_and_the_asset_gate():
    """The user's ruling (2026-09-29): "yes, separate approval, i must see all angles,
    framework, keywords, why each competitors rank, full distribution section by section".
    The outline is its own stop, between the research board and the page board."""
    rows = {int(re.match(r"STOP (\d)", r[5]).group(1)): r for r in _run_rows()
            if r[5].startswith("STOP")}
    cells = {n: r[5] for n, r in rows.items()}
    assert "research board" in cells[1] and "brief" in cells[1], cells[1]
    assert "outline" in cells[2] and "section matrix" in cells[2], cells[2]
    assert "board" in cells[3] and "outline" not in cells[3].split("—")[0], cells[3]
    assert "Asset Gate" in cells[4], cells
    assert [int(r[0]) for _, r in sorted(rows.items())] == [8, 9, 10, 11], rows.keys()


def test_the_outline_stop_is_recorded_and_gated_before_the_page_board():
    row9, row10 = _run_rows()[8], _run_rows()[9]
    for tok in ("scripts/outline_matrix.py", "data/outlines/<slug>.json", "--approve"):
        assert tok in row9[2] + row9[3] + " ".join(_steps(9)), (tok, row9)
    assert "scripts/build_page_board.py" in row9[4] and "outline-unapproved" in row9[4], row9[4]
    assert "after STOP 2" in row10[2], row10[2]


def test_the_research_board_is_built_by_its_script_and_recorded():
    row8 = _run_rows()[7]
    body = row8[2] + row8[3] + " ".join(_steps(8))
    for tok in ("scripts/research_board.py", "data/research-boards/<slug>.json", "--approve"):
        assert tok in body, (tok, body)


PAGE_TYPE_HEADER = ("Page type", "Builder skill", "`<route>`", "Final-audit and evidence profile",
                    "Rule packs to read")


def test_each_project_5_page_type_has_a_builder_a_route_and_a_real_profile():
    rows = _rows(DOC.read_text(encoding="utf-8"), PAGE_TYPE_HEADER)
    assert [r[0] for r in rows] == ["location", "comparison", "blog"]
    for page_type, skill, _route, profile, packs in rows:
        path = re.search(r"`([^`]+SKILL\.md)`", skill).group(1)
        assert (ROOT / path).is_file(), path
        name = profile.strip("`")
        assert name in final_page_audit.PROFILES, f"{page_type}: no final-audit profile {name!r}"
        assert name in evidence_audit.PAGE_TYPES, f"{page_type}: no evidence type {name!r}"
        for pack in (p.strip() for p in packs.split(",")):
            assert (ROOT / "rules" / f"{pack}.md").is_file(), f"{page_type}: no pack {pack}"


def test_the_location_route_is_the_one_the_audits_resolve():
    rows = _rows(DOC.read_text(encoding="utf-8"), PAGE_TYPE_HEADER)
    assert rows[0][2].startswith("`uk-locations/<slug>`")


def test_the_run_is_guarded_by_check_workflow():
    assert "docs/reference/page-run.md" in wrc.DOCS
    problems, examined = wrc.check(ROOT)
    page_run = [p for p in problems if p.startswith("page-run.md")]
    assert page_run == [], page_run
    assert examined > 50


def test_the_run_is_linked_from_claude_md_and_workflow():
    for doc in ("CLAUDE.md", "docs/reference/WORKFLOW.md"):
        text = (ROOT / doc).read_text(encoding="utf-8")
        assert "docs/reference/page-run.md" in text, f"{doc} does not point at the page run"


def test_the_mandatory_skills_are_routed_where_a_page_is_built_and_closed():
    """The user's rulings (2026-09-26): impeccable and frontend-design harden every project 5
    page, verification-before-completion precedes every done claim, and writing-plans opens
    the session. A skill named only in page-run.md is a skill a builder reading its own
    SKILL.md never meets, so each routing point names them too."""
    want = {
        "CLAUDE.md": HARDEN_SKILLS + (VERIFY_SKILL, PLAN_SKILL),
        "docs/reference/WORKFLOW.md": HARDEN_SKILLS + (VERIFY_SKILL,),
        ".claude/skills/session-closer/SKILL.md": (VERIFY_SKILL,),
    }
    for skill in BUILDER_SKILLS:
        want[skill] = HARDEN_SKILLS + (VERIFY_SKILL,)
    missing = [f"{doc}: {name}" for doc, names in want.items()
               for name in names
               if f"`{name}`" not in (ROOT / doc).read_text(encoding="utf-8")]
    assert missing == [], "a routing point does not name a mandatory skill:\n  " + "\n  ".join(missing)


def test_workflow_names_verification_at_the_gates_and_at_close():
    text = (ROOT / "docs/reference/WORKFLOW.md").read_text(encoding="utf-8")
    gates = text[text.index("## Sprint 4"):text.index("## Sprint 5")]
    close = text[text.index("## Sprint 6"):]
    assert f"`{VERIFY_SKILL}`" in gates and f"`{VERIFY_SKILL}`" in close


# The user's image rulings (2026-09-26, rules/images.md): an in-body image's bleed is a design
# colour (bone), never grey or black, and a new portrait bakes contain (`--og-style A`), never
# blurfill. Pinned as tokens, not a sentence, so a re-wrap cannot break it.
BLEED_TOKENS = ("bone", "never blurfill", "`--og-style A`")
SESSION_OPEN = re.compile(r"grill-me\W[^\n]{0,80}?superpowers:writing-plans\W[^\n]{0,60}?builder skill")
ROUTED = ("docs/reference/WORKFLOW.md",) + BUILDER_SKILLS
# grill-me is where row 1 starts, so its handoff names the rest of the order too (Task 28a).
SESSION_ROUTED = ROUTED + (".claude/skills/grill-me/SKILL.md",)


def _norm(text):
    return " ".join(text.split())


def _steps(n):
    """The numbered sub-list under `### Row n steps`, below the run table."""
    text = DOC.read_text(encoding="utf-8")
    head = f"### Row {n} steps"
    assert head in text, f"no {head!r} sub-list"
    body = re.split(r"\n#{2,3} ", text[text.index(head) + len(head):], maxsplit=1)[0]
    return [line for line in body.splitlines() if re.match(r"\d+\. ", line)]


def test_every_page_type_reads_the_images_pack():
    rows = _rows(DOC.read_text(encoding="utf-8"), PAGE_TYPE_HEADER)
    bad = [r[0] for r in rows if "images" not in (p.strip() for p in r[4].split(","))]
    assert bad == [], f"page types that do not read rules/images.md: {bad}"


def test_claude_md_and_the_run_agree_on_the_rule_packs():
    run = {r[0]: {p.strip() for p in r[4].split(",")}
           for r in _rows(DOC.read_text(encoding="utf-8"), PAGE_TYPE_HEADER)}
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    for page_type, packs in run.items():
        m = re.search(rf"^\| {page_type} \| [^|]+ \| ([^|]+) \|$", claude, re.M)
        assert m, f"CLAUDE.md has no page-type row for {page_type}"
        assert {p.strip() for p in m.group(1).split(",")} == packs, (page_type, m.group(1))


def test_the_image_bleed_ruling_is_routed_everywhere_a_page_is_built():
    row11 = next(r for r in _run_rows() if r[1].startswith("§15"))
    assert all(tok in row11[3] for tok in BLEED_TOKENS), row11[3]
    assert "reframe_og.py --style" not in DOC.read_text(encoding="utf-8")
    missing = [f"{doc}: {tok}" for doc in ROUTED for tok in BLEED_TOKENS
               if tok not in _norm((ROOT / doc).read_text(encoding="utf-8"))]
    assert missing == [], f"the image-bleed ruling is not routed: {missing}"


def test_the_session_open_order_is_routed_everywhere_a_page_is_built():
    assert SESSION_OPEN.search(_run_rows()[0][2]), _run_rows()[0][2]
    missing = [doc for doc in SESSION_ROUTED
               if not SESSION_OPEN.search(_norm((ROOT / doc).read_text(encoding="utf-8")))]
    assert missing == [], f"the session-open order is not routed in: {missing}"


def test_the_keyword_metrics_gate_names_every_fail():
    row6 = next(r for r in _run_rows() if r[1].startswith("§7"))
    for tok in ("any FAIL", "title-front-load", "first-100-words", "primary keyword"):
        assert tok in row6[4], (tok, row6[4])


MULTI_COMMAND_ROWS = (5, 8, 9, 11, 12, 17, 18)


def test_multi_command_rows_point_to_a_numbered_sub_list():
    rows = _run_rows()
    for n in MULTI_COMMAND_ROWS:
        assert f"row {n} steps below" in rows[n - 1][2], f"row {n} does not point to its steps"
        assert len(_steps(n)) >= 2, f"row {n}'s sub-list has fewer than two steps"


def test_an_existing_page_is_extracted_before_it_is_boarded():
    steps = "\n".join(_steps(9))
    board = steps.index("scripts/build_page_board.py <slug>")
    assert steps.index("scripts/facts_preserved_check.py --extract <slug>") < board
    assert steps.index("scripts/verbatim_set_check.py --extract <slug>") < board
    row12 = _run_rows()[11][2] + "\n".join(_steps(12))
    assert "--extract" not in row12, "row 12 still extracts — it happens at row 9, before the board"


def test_the_record_is_fresh_against_head_and_the_harden_passes_are_ordered():
    # Task 25 review: freshness is judged against HEAD by diffing the page's sources, the
    # impeccable pass precedes frontend-design, an edit after frontend-design stales it, and
    # the full gate re-runs check:all rather than trusting a recorded exit code.
    rows = _run_rows()
    assert "ancestor of the `frontend_design` commit" in rows[13][4], rows[13][4]
    assert ("the page changed after the frontend-design pass; re-run it" in rows[14][4]
            and "verification" in rows[14][4]), rows[14][4]
    ver = rows[17][4]
    for tok in ("in HEAD's history", "unchanged between it and HEAD", "`data/locations.json` row",
                "re-runs `npm run -s check:all`", "`npm run -s build`", "rebuild first"):
        assert tok in ver, (tok, ver)


def test_a_visual_change_with_the_breeder_away_is_previewed_and_deferred_not_applied():
    text = DOC.read_text(encoding="utf-8")
    para = text[text.index("## The run"):text.index("| # | Brief step")]
    rows = _run_rows()
    for where in (para, rows[13][3] + rows[13][5], rows[14][3] + rows[14][5]):
        for tok in ("away", "`deferred`", "Open Flags", "not applied"):
            assert tok in where, (tok, where)


def test_the_strategy_stop_is_explained_as_a_deliberate_difference():
    # The user's ruling (2026-09-27) replaced the old exemption: STOP 1 is the research board
    # on every page (tests/py/test_research_board_rule.py pins the rest).
    text = DOC.read_text(encoding="utf-8")
    diffs = _norm(text[text.index("## Deliberate differences"):])
    assert "STOP 1 (the research board) applies to every project 5 page" in diffs
    assert "applies only to a page with no row" not in diffs


def test_every_arrival_marker_cites_the_path_that_ends_it():
    """tests/py/test_claude_md.py expires an `(arrives in Task N)` marker once every backticked
    path on its line exists. A marked line that cites no path the guard recognises (a
    `python3 scripts/x.py <slug>` command reads as no path) never expires, so the marker
    would outlive the script and keep disarming check:workflow on that line."""
    sys.path.insert(0, str(ROOT / "tests/py"))
    from test_rules_index import BACKTICKED, _path_like
    bad = [f"page-run.md:{n}" for n, line in enumerate(DOC.read_text(encoding="utf-8").splitlines(), 1)
           if wrc.ARRIVES.search(line)
           and not any(_path_like(tok) for tok in BACKTICKED.findall(line))]
    assert bad == [], f"marked lines citing no path that would expire the marker: {bad}"


def test_grill_me_hands_a_project_5_page_to_the_plan_the_builder_and_the_record():
    text = _norm((ROOT / ".claude/skills/grill-me/SKILL.md").read_text(encoding="utf-8"))
    handoff = text[text.index("### Step 3"):]
    plan = handoff.index(f"`{PLAN_SKILL}`")
    builder = handoff.index("builder skill", plan)
    record = handoff.index("scripts/page_run_record.py <slug> session-open --builder", builder)
    assert plan < builder < record


def test_the_ported_agents_and_skill_sit_at_their_rows():
    """Task 10c (2026-09-29): the six ports run at fixed rows, so a page run cannot skip one.
    Pinned here, in the page run's own tests, so deleting a line from a row fails this file."""
    rows = _run_rows()
    text = DOC.read_text(encoding="utf-8")

    def block(n):
        head = f"### Row {n} steps"
        return re.split(r"\n#{2,3} ", text[text.index(head) + len(head):], maxsplit=1)[0]

    want = {
        7: (rows[6][2], ("bsuk-entity-incorporation-agent",)),
        9: (block(9), ("bsuk-entity-incorporation-agent", "bsuk-external-link-agent")),
        12: (block(12), ("bsuk-coat-variant-builder", "bsuk-scam-trust-agent", "bsuk-video-seo-agent")),
        16: (rows[15][2], ("bsuk-visual-intelligence",)),
        20: (rows[19][2], ("bsuk-visual-intelligence",)),
    }
    missing = [f"row {n}: {name}" for n, (cell, names) in want.items() for name in names
               if name not in cell]
    assert missing == [], "a ported agent or skill left its page-run row:\n  " + "\n  ".join(missing)
