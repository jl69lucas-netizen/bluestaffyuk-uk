"""`CLAUDE.md` is loaded into every session, so a wrong line in it is a wrong line in
every build. It gets the same guards the rule packs get, plus two of its own.

1. The backticked-path guard from `tests/py/test_rules_index.py`, run over `CLAUDE.md`:
   a cited repo path either exists or says when it arrives.
2. The rule-pack pointer table names every file in `rules/` and nothing else — a pack
   missing from the router is a pack nobody reads, and a router row pointing at a pack
   that was renamed is a dead link at the top of the system.
3. No line tells anyone to push. The repo has no remote until project 6; the only place
   that may discuss pushing is the deploy section that says it is inactive, and lines that
   forbid it.
"""
import pathlib
import re

from test_rules_index import BACKTICKED, MARKERS, _cited_paths, _path_like,\
    _unmarked_missing_paths

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLAUDE_MD = ROOT / "CLAUDE.md"
RULES_DIR = ROOT / "rules"


def lines():
    return CLAUDE_MD.read_text(encoding="utf-8").splitlines()


def test_every_repo_path_cited_in_claude_md_exists_or_is_marked():
    bad = _unmarked_missing_paths(CLAUDE_MD)
    assert bad == [], (
        "CLAUDE.md cites a path that does not exist and does not say when it will. Either "
        "fix the path, or mark the line '(arrives in Task N)' / '(deferred to project N)' "
        "/ '(not ported — source repo only)':\n  " + "\n  ".join(bad))


# ── the rule-pack router ────────────────────────────────────────────────────
TABLE_ROW = re.compile(r"^\|\s*\[`(rules/[^`]+)`\]")


def routed_packs():
    return {m.group(1) for m in (TABLE_ROW.match(l) for l in lines()) if m}


def test_pointer_table_names_every_pack_and_nothing_else():
    on_disk = {p.relative_to(ROOT).as_posix() for p in RULES_DIR.glob("*.md")}
    routed = routed_packs()
    assert routed == on_disk, (
        f"router and rules/ disagree — missing from CLAUDE.md: {sorted(on_disk - routed)}; "
        f"named but absent from rules/: {sorted(routed - on_disk)}")


def test_the_router_actually_has_rows():
    # A table that silently stopped matching would make the test above pass against an
    # empty rules/; assert the router is non-empty rather than pinning a count that every
    # new pack would have to come here to bump.
    assert routed_packs()


# ── no push ─────────────────────────────────────────────────────────────────
DEPLOY_SECTION = "## Deploy — inactive until project 6"
NEXT_SECTION = re.compile(r"^## ")
# A line that FORBIDS pushing is the point; anything else that mentions it is not.
FORBIDS = ("never push", "not push", "no push", "unpushed")


def deploy_section_bounds():
    ls = lines()
    start = ls.index(DEPLOY_SECTION)
    for i, l in enumerate(ls[start + 1:], start + 1):
        if NEXT_SECTION.match(l):
            return start, i
    return start, len(ls)


def test_no_line_instructs_a_push_outside_the_inactive_section():
    start, end = deploy_section_bounds()
    bad = []
    for lineno, line in enumerate(lines(), 1):
        if "push" not in line.lower():
            continue
        if start < lineno <= end:          # inside "Deploy — inactive until project 6"
            continue
        if any(f in line.lower() for f in FORBIDS):
            continue
        bad.append(f"CLAUDE.md:{lineno}  {line.strip()}")
    assert bad == [], (
        "CLAUDE.md mentions pushing outside the 'inactive until project 6' section and "
        "without forbidding it. This repo has no remote:\n  " + "\n  ".join(bad))


# ── the stale-marker guard ──────────────────────────────────────────────────
# The forward-reference marker is a promise with an expiry date. Once Task N lands and the
# path exists, the marker stops being honest and starts telling readers that a file they
# can open is not there yet — worse than no marker at all, because it is load-bearing
# elsewhere: the guard above SUPPRESSES the missing-path check on any marked line, so a
# stale marker silently disarms it for every other path on that line.
# A Phase 3b task is named by its ruling (`Task R3`), so the marker reads that form too.
ARRIVES = re.compile(r"\(arrives in Task (?:\d+[a-z]?|R\d+)\)")
# `(not ported — source repo only)` expires the same way, and worse: it asserts the file
# will NEVER exist here. Task 13 left one on a line citing `docs/reference/system-registry.md`
# minutes after writing that file. Same rule, same report.
NEVER = re.compile(r"\(not ported[^)]*\)")
EXPIRING = (ARRIVES, NEVER)


def stale_markers(root: pathlib.Path):
    """Lines carrying '(arrives in Task N)' where every backticked path already exists.

    `root` is a parameter so the test can prove the checker FIRES, by pointing it at a
    copy of the docs where one marked path has been created.
    """
    # The agents and skills are loaded into a session exactly the way CLAUDE.md and the
    # packs are, and Task 12's own arrivals are the proof this matters: 31 lines said
    # "(arrives in Task 12)" about files Task 12 then created. A marker left behind in an
    # agent or a skill disarms the missing-path guard on that line for every other path on
    # it, which is the failure this checker exists to catch.
    docs = ([root / "CLAUDE.md"]
            + sorted((root / "rules").glob("*.md"))
            + sorted((root / ".claude/agents").glob("*.md"))
            + sorted((root / ".claude/skills").glob("*/SKILL.md"))
            # Task 13's own reference docs, for the same reason: a stale marker there
            # disarms the missing-path guard on that line for every other path on it.
            + sorted((root / "docs/reference").glob("*.md")))
    stale = []
    for f in docs:
        if not f.exists():
            continue
        for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not any(rx.search(line) for rx in EXPIRING):
                continue
            paths = [p for p in (_path_like(t) for t in BACKTICKED.findall(line))
                     if p is not None]
            if paths and all((root / p).exists() for p in paths):
                stale.append(f"{f.name}:{lineno}  {line.strip()}")
    return stale


def test_no_arrives_in_task_marker_is_stale():
    stale = stale_markers(ROOT)
    assert stale == [], (
        "marker is stale, delete it — every path on these lines now exists, so the "
        "'(arrives in Task N)' / '(not ported — source repo only)' marker is telling "
        "readers a file is missing that is not:\n  "
        + "\n  ".join(stale))


def test_the_stale_marker_checker_actually_fires(tmp_path):
    """Copy the docs to a fake root, create one marked path, expect exactly that line."""
    import shutil

    shutil.copy(CLAUDE_MD, tmp_path / "CLAUDE.md")
    shutil.copytree(RULES_DIR, tmp_path / "rules")
    assert stale_markers(tmp_path) == [], "the copy should start clean, like the real root"

    # Task 13's markers are gone now that its six reference docs exist, and the one
    # surviving marker in CLAUDE.md sits on a line whose backticked token carries a `<slug>`
    # argument, so `_path_like` correctly refuses to read it as a path. The proof therefore
    # supplies its own marked pack rather than depending on whichever real marker happens to
    # be live this week.
    pack = tmp_path / "rules" / "zz-fixture.md"
    pack.write_text("Read `docs/reference/quick-start.md` (arrives in Task 13)\n",
                    encoding="utf-8")
    assert stale_markers(tmp_path) == [], "the marked path does not exist yet — not stale"

    target = tmp_path / "docs" / "reference" / "quick-start.md"
    target.parent.mkdir(parents=True)
    target.write_text("arrived\n", encoding="utf-8")

    fired = stale_markers(tmp_path)
    assert fired, "creating a marked path must make the checker fire"
    assert all("zz-fixture.md" in row for row in fired), fired


def test_the_not_ported_marker_expires_too(tmp_path):
    """The second expiring marker gets its own proof, or a regex typo silences it."""
    pack = tmp_path / "rules" / "zz-never.md"
    pack.parent.mkdir(parents=True)
    pack.write_text("See `docs/reference/system-registry.md` (not ported — source repo only)\n",
                    encoding="utf-8")
    assert stale_markers(tmp_path) == [], "the path does not exist yet — not stale"

    target = tmp_path / "docs" / "reference" / "system-registry.md"
    target.parent.mkdir(parents=True)
    target.write_text("arrived\n", encoding="utf-8")
    fired = stale_markers(tmp_path)
    assert fired and all("zz-never.md" in row for row in fired), fired


def test_the_checker_walks_agents_and_skills_too(tmp_path):
    """A glob typo in the walked roots would silently stop checking 89 loaded documents."""
    agent = tmp_path / ".claude" / "agents" / "bsuk-x.md"
    skill = tmp_path / ".claude" / "skills" / "bsuk-y" / "SKILL.md"
    for f in (agent, skill):
        f.parent.mkdir(parents=True)
        f.write_text("Read `data/here.json` (arrives in Task 12)\n", encoding="utf-8")
    assert stale_markers(tmp_path) == [], "the path does not exist yet — not stale"

    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "here.json").write_text("{}\n", encoding="utf-8")
    fired = stale_markers(tmp_path)
    assert len(fired) == 2, fired
    assert {r.split(":")[0] for r in fired} == {"bsuk-x.md", "SKILL.md"}, fired


def test_a_lettered_task_marker_expires_too(tmp_path):
    """`(arrives in Task 18b)` sat on working rule 15 after Task 18b wrote the script: the
    marker regex read only digits, so the stale marker was invisible and disarmed the
    missing-path guard on that line."""
    pack = tmp_path / "rules" / "zz-lettered.md"
    pack.parent.mkdir(parents=True)
    pack.write_text("`scripts/x.py` (arrives in Task 18b) proves it\n", encoding="utf-8")
    assert stale_markers(tmp_path) == [], "the path does not exist yet — not stale"
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/x.py").write_text("# arrived\n", encoding="utf-8")
    fired = stale_markers(tmp_path)
    assert fired and all("zz-lettered.md" in row for row in fired), fired


# ── the working rules ───────────────────────────────────────────────────────
WORKING_RULE = re.compile(r"^(\d+)\. \*\*")


def test_working_rules_are_numbered_without_gaps():
    # Agents, skills and plans cite these by number ("working rule 15"); a skipped or
    # repeated number sends a reader to the wrong rule.
    nums = [int(m.group(1)) for m in (WORKING_RULE.match(l) for l in lines()) if m]
    assert len(nums) >= 9, f"the numbered rule list stopped matching: {nums}"
    assert nums == list(range(1, len(nums) + 1)), f"working rules are not 1..N: {nums}"


def test_an_r_task_marker_expires_too(tmp_path):
    """`(arrives in Task R3)` is the Phase 3b form; ARRIVES must read it, or it never expires."""
    assert ARRIVES.search("(arrives in Task R3)") and ARRIVES.search("(arrives in Task 12)")
    assert ARRIVES.search("(arrives in Task 18b)")
    skill = tmp_path / ".claude" / "skills" / "zz-fonts" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("fonts self-hosted from `public/fonts/` (arrives in Task R3)\n", encoding="utf-8")
    assert stale_markers(tmp_path) == [], "the folder does not exist yet — not stale"
    (tmp_path / "public" / "fonts").mkdir(parents=True)
    fired = stale_markers(tmp_path)
    assert fired and all("SKILL.md" in row for row in fired), fired
