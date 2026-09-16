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

from test_rules_index import BACKTICKED, MARKERS, _path_like

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLAUDE_MD = ROOT / "CLAUDE.md"
RULES_DIR = ROOT / "rules"


def lines():
    return CLAUDE_MD.read_text(encoding="utf-8").splitlines()


def test_every_repo_path_cited_in_claude_md_exists_or_is_marked():
    bad = []
    for lineno, line in enumerate(lines(), 1):
        marked = any(m in line for m in MARKERS)
        for tok in BACKTICKED.findall(line):
            p = _path_like(tok)
            if p is None or (ROOT / p).exists() or marked:
                continue
            bad.append(f"CLAUDE.md:{lineno}  {p}")
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
    # empty rules/ and fail loudly against a real one; assert the shape too.
    assert len(routed_packs()) == 10


# ── no push ─────────────────────────────────────────────────────────────────
DEPLOY_SECTION = "## Deploy — inactive until project 6"
NEXT_SECTION = re.compile(r"^## ")
# "never push", "unpushed", "must not get one" — a line that FORBIDS pushing is the point.
FORBIDS = ("never push", "not push", "no push", "unpushed", "until project 6")


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
