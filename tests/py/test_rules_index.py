"""The rule ledger and the quality ledgers are load-bearing files, not documentation.

`data/quality/rule-index.json` is what `scripts/quality_report.py` §5 reads to decide
whether a rule is enforced, a deletion candidate, or an unearned judgment exemption. A
row pointing at a pack file that does not exist is the same defect the report exists to
catch, one level up: the ledger itself lying about what holds the rules up.

The three quality ledgers are asserted here for SHAPE, not content. All three are empty at
the system transfer, and an empty file that does not load is the failure mode that would
take `evidence_audit.py` and `quality_report.py` down with it.
"""
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
QUALITY = ROOT / "data" / "quality"
RULES_DIR = ROOT / "rules"


def _load(name):
    return json.loads((QUALITY / name).read_text(encoding="utf-8"))


def index():
    return _load("rule-index.json")


# ── the rule ledger ─────────────────────────────────────────────────────────
def test_every_pack_path_exists_under_rules():
    missing = sorted({r["pack"] for r in index()["rules"] if "pack" in r}
                     - {p.relative_to(ROOT).as_posix() for p in RULES_DIR.glob("*.md")})
    assert missing == [], f"rule-index names pack files that do not exist: {missing}"


def test_rule_ids_are_unique():
    ids = [r["id"] for r in index()["rules"]]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    assert dupes == [], f"duplicate rule ids: {dupes}"


def test_judgment_cap_is_nine():
    # 12 minus CAG rules 2 (CITES), 11 (Verified-Claim Ledger) and 12 (brand-owned method
    # labels). A cap left at 12 over 9 rules is not a cap; it is three free exemptions.
    assert index()["judgment_cap"] == 9


def test_exactly_nine_judgment_rules():
    j = [r["id"] for r in index()["rules"] if r.get("enforced") == "judgment"]
    assert len(j) == 9, f"judgment class is {len(j)}: {j}"


def test_every_judgment_rule_states_why_a_test_cannot_exist():
    bare = [r["id"] for r in index()["rules"]
            if r.get("enforced") == "judgment" and not (r.get("why") or "").strip()]
    assert bare == [], f"judgment with no `why` is an exemption anyone can grant: {bare}"


def test_no_id_or_path_carries_the_source_repo_vocabulary():
    bad = []
    for r in index()["rules"]:
        blob = " ".join(str(r.get(k, "")) for k in ("id", "pack", "test"))
        if "cag" in blob.lower() or "for-sale" in blob.lower():
            bad.append(r["id"])
    assert bad == [], f"rows still naming the source repo or the renamed pack: {bad}"


# ── the three quality ledgers ───────────────────────────────────────────────
def test_evidence_budgets_shape():
    b = _load("evidence-budgets.json")
    assert isinstance(b["terms"], dict) and b["terms"]
    assert isinstance(b["budgets"], dict) and b["budgets"]
    assert isinstance(b["title_max_chars"], int)
    assert isinstance(b.get("superlatives", []), list)
    assert isinstance(b.get("title_max_chars_by_slug", {}), dict)
    assert isinstance(b.get("budgets_by_slug", {}), dict)
    # every capped term must be resolvable to a pattern, or the ceiling silently never fires
    for page_type, caps in b["budgets"].items():
        unknown = sorted(set(caps) - set(b["terms"]))
        assert unknown == [], f"budgets[{page_type}] caps terms with no pattern: {unknown}"


def test_rework_ledger_is_empty_and_readable_by_quality_report():
    r = _load("rework-ledger.json")
    # scripts/quality_report.py trend() reads `windows`, not `entries`.
    assert r["windows"] == []


def test_evidence_ledger_rows_are_well_formed_and_readable_by_evidence_audit():
    e = _load("evidence-ledger.json")
    # scripts/evidence_audit.py claim_binding() iterates ledger["claims"]. Empty at the system
    # transfer; Known Issue 40 added the first row, the parents' clear DNA results, at proof
    # NOT FETCHED — recorded as unproven, never as proven.
    ids = [c["id"] for c in e["claims"]]
    assert len(ids) == len(set(ids)), ids
    for c in e["claims"]:
        assert set(c) >= {"id", "pattern", "proof", "anchor", "confirmed"}, c
        re.compile(c["pattern"])
        # A proof is a site path to the redacted document, or the literal NOT FETCHED; a row
        # at NOT FETCHED has, by definition, no breeder confirmation date.
        assert c["proof"] == "NOT FETCHED" or c["proof"].startswith("/"), c
        if c["proof"] == "NOT FETCHED":
            assert c["confirmed"] is None, c


def test_the_gates_actually_load_all_three():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import evidence_audit, quality_report  # noqa: E402

    assert quality_report.trend(_load("rework-ledger.json")) == (None, None)
    assert evidence_audit.claim_binding("<main>anything at all</main>",
                                        _load("evidence-ledger.json")) == []
    assert quality_report.broken_test_links(index(), quality_report.registry_check_ids()) == []
    assert quality_report.judgment_overflow(index()) is None


def test_enforced_is_one_of_the_three_known_classes():
    bad = [(r["id"], r.get("enforced")) for r in index()["rules"]
           if r.get("enforced") not in {"test", "judgment", "untested"}]
    assert bad == [], f"unknown `enforced` class (quality_report.py knows only three): {bad}"


# ── packs and ledger must not drift apart ───────────────────────────────────
import re  # noqa: E402

FRONTMATTER_ID = re.compile(r"^id: ([\w-]+)$", re.M)


def pack_ids():
    """{rule id: pack path} for every front-matter block in rules/*.md."""
    out = {}
    for f in sorted(RULES_DIR.glob("*.md")):
        for m in FRONTMATTER_ID.finditer(f.read_text(encoding="utf-8")):
            out[m.group(1)] = f.relative_to(ROOT).as_posix()
    return out


def test_every_pack_rule_is_in_the_index():
    # The reverse does not hold: the index also registers harness check ids, which are
    # checks rather than written rules and live in tests/render/checks/, not in a pack.
    missing = sorted(set(pack_ids()) - {r["id"] for r in index()["rules"]})
    assert missing == [], f"rules written in a pack but absent from the ledger: {missing}"


def test_index_pack_field_points_at_the_file_that_holds_the_rule():
    actual = pack_ids()
    wrong = [(r["id"], r["pack"], actual[r["id"]]) for r in index()["rules"]
             if "pack" in r and r["id"] in actual and r["pack"] != actual[r["id"]]]
    assert wrong == [], f"rule-index `pack` disagrees with where the rule is written: {wrong}"


# ── the recurrence guard ────────────────────────────────────────────────────
# A pack that cites `docs/reference/seo-rules.md` before Task 13 writes it sends a reader
# to a path that does not exist and reads as a bug in their checkout rather than as work
# that has not happened yet. A forward reference is allowed; an UNMARKED one is not.
BACKTICKED = re.compile(r"`([^`\n]+)`")
PATH_EXT = (".py", ".md", ".json", ".ts", ".sh", ".css", ".mjs")
MARKERS = ("(arrives in", "(deferred", "(not ported", "(source repo only")
TOP_LEVEL = {p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")} | {".claude"}


def _path_like(tok: str):
    """The path a backticked token names, or None when it is not a repo path.

    Deliberately narrow. Prose in these packs backticks CSS (`width/height="1em"`), HTML
    (`</h3>`), URLs, route paths (`/available-puppies/`), bare extensions (`.astro`) and
    stop-word lists (`of/the/and/for/with`). Treating any of those as a missing file would
    make this test noise, and a noisy test gets deleted rather than obeyed.
    """
    tok = tok.strip()
    # `python3 scripts/x.py` is a command whose SECOND word is the cited path. Before this
    # strip, the space made `_path_like` return None and the guard never looked at it — so
    # WORKFLOW.md could prescribe `python3 scripts/apply_model_tiers.py`, a script that was
    # never ported, and pass. `npm run x` is deliberately absent: its argument is a package
    # script name, not a file.
    for word in ("python3 ", "python ", "bash ", "sh ", "node "):
        if tok.startswith(word):
            tok = tok[len(word):].strip()
            break
    if tok.startswith(("http", "/", "<", "@", "-", "$")):
        return None
    if any(c in tok for c in '<>"*= ') or tok.count("`"):
        return None
    if re.fullmatch(r"\.[a-z]+", tok):          # a bare extension, e.g. `.astro`
        return None
    tok = tok.split("::")[0].split("#")[0].rstrip(".,;:")
    if not (tok.endswith(PATH_EXT) or tok.split("/")[0] in TOP_LEVEL):
        # `of/the/and/for/with` is a stop-word list, not a directory. A token only counts
        # as a path when it carries a source extension or starts at a real repo directory.
        return None
    return tok


def test_every_repo_path_cited_in_a_pack_exists_or_is_marked():
    bad = []
    for f in sorted(RULES_DIR.glob("*.md")):
        bad += _unmarked_missing_paths(f)
    assert bad == [], (
        "a pack cites a path that does not exist and does not say when it will. Either "
        "fix the path, or mark the line '(arrives in Task N)' / '(deferred to project N)' "
        "/ '(not ported — source repo only)':\n  " + "\n  ".join(bad))


# The agents are loaded the same way the packs are — into a working session, as
# instructions — so the same forward-reference rule applies to them. An agent that tells a
# builder to `Read data/image-specs.json` when that file was never ported sends the builder
# looking for a file nobody will ever create, and the first symptom is a failed run rather
# than a failed test. Parametrised so the report names the offending agent.
AGENTS_DIR = ROOT / ".claude/agents"


# A command line inside a fenced block: `python3 scripts/x.py --flag`. Backticks are the
# only thing the guard used to read, and a fenced runbook has none — so a whole pipeline of
# scripts that do not exist could be prescribed in a ``` block and nothing would notice.
FENCED_CMD = re.compile(r"^\s*(?:\d+\.\s*|[-*]\s*|[→>]\s*)?"
                        r"(?:python3|python|bash|sh|node)\s+([A-Za-z0-9_./-]+)")


def _cited_paths(f: pathlib.Path):
    """[(lineno, path, marked)] for every repo path this document cites.

    Two sources: backticked tokens anywhere, and interpreter commands inside fenced code
    blocks. `marked` carries the line's own forward-reference marker, because the marker
    suppresses the missing-path check for that line.
    """
    out = []
    for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        marked = any(m in line for m in MARKERS)
        for tok in BACKTICKED.findall(line):
            p = _path_like(tok)
            if p is not None:
                out.append((lineno, p, marked))
        m = FENCED_CMD.match(line)
        if m:
            p = _path_like(m.group(1))
            if p is not None:
                out.append((lineno, p, marked))
    return out


def _unmarked_missing_paths(f: pathlib.Path):
    return [f"{f.name}:{lineno}  {p}"
            for lineno, p, marked in _cited_paths(f)
            if not marked and not (ROOT / p).exists()]


@pytest.mark.parametrize("agent", sorted(AGENTS_DIR.glob("bsuk-*.md")), ids=lambda p: p.stem)
def test_every_repo_path_cited_in_an_agent_exists_or_is_marked(agent):
    bad = _unmarked_missing_paths(agent)
    assert bad == [], (
        f"{agent.name} cites a path that does not exist and does not say when it will. "
        "Either fix the path, or mark the line '(arrives in Task N)' / "
        "'(deferred to project N)' / '(not ported — source repo only)':\n  "
        + "\n  ".join(bad))


def test_there_are_agents_to_check():
    # A glob that silently stopped matching would make the parametrised test above vacuous.
    assert list(AGENTS_DIR.glob("bsuk-*.md"))


# A skill is loaded into a session exactly the way an agent is, so it gets the same rule.
# Task 12 brought 25 system skills across from the source repo, every one of them full of
# paths that existed THERE — `scripts/rework_ledger.py`, `site/content/`, a session log
# nobody ported. A skill that sends a builder to one of those has the same failure mode as
# an agent that does: the first symptom is a failed run rather than a failed test.
SKILLS_DIR = ROOT / ".claude/skills"


# Every skill, not only the `bsuk-*` set. The generic writing, framework and session skills
# are loaded into a session exactly the way the system skills are, and project 5 runs them on
# every city page — yet until 2026-09-23 this guard read only `bsuk-*`, and 14 of the other
# 28 cited paths the source repo had (`docs/reference/top-pages.md`, `data/structure.json`,
# `scripts/interior_29_audit.py`). The four `openspec-*` skills are the one exclusion, and it
# is structural: they are vendored from upstream OpenSpec, their `proposal.md` / `tasks.md`
# are relative to the `openspec/changes/<name>/` folder the CLI creates rather than repo
# paths, and rewriting a vendored file breaks the next re-sync (the same scoping as
# `tests/py/test_skills_frontmatter.py`'s key-set test).
VENDORED_SKILLS = ("openspec-",)
INSTRUCTION_SKILLS = sorted(p for p in SKILLS_DIR.glob("*/SKILL.md")
                            if not p.parent.name.startswith(VENDORED_SKILLS))


@pytest.mark.parametrize("skill", INSTRUCTION_SKILLS, ids=lambda p: p.parent.name)
def test_every_repo_path_cited_in_a_skill_exists_or_is_marked(skill):
    bad = _unmarked_missing_paths(skill)
    assert bad == [], (
        f"{skill.parent.name} cites a path that does not exist and does not say when it "
        "will. Either fix the path, or mark the line '(arrives in Task N)' / "
        "'(deferred to project N)' / '(not ported — source repo only)':\n  "
        + "\n  ".join(bad))


# The reference docs are cited by name in almost every agent and pack, and they cite back.
# Task 13 wrote them, so they get the same forward-reference rule: a path either exists or
# says when it arrives.
REFERENCE_DIR = ROOT / "docs/reference"


@pytest.mark.parametrize("doc", sorted(REFERENCE_DIR.glob("*.md")), ids=lambda p: p.stem)
def test_every_repo_path_cited_in_a_reference_doc_exists_or_is_marked(doc):
    bad = _unmarked_missing_paths(doc)
    assert bad == [], (
        f"{doc.name} cites a path that does not exist and does not say when it will. "
        "Either fix the path, or mark the line '(arrives in Task N)' / "
        "'(deferred to project N)' / '(not ported — source repo only)':\n  "
        + "\n  ".join(bad))


def test_there_are_reference_docs_to_check():
    # Task 13 wrote six. A glob that stopped matching would make the test above vacuous.
    assert len(list(REFERENCE_DIR.glob("*.md"))) >= 6


def test_there_are_skills_to_check():
    # The port wrote 25 system skills; a glob that stopped matching would make the
    # parametrised test above vacuous.
    assert len(list(SKILLS_DIR.glob("bsuk-*/SKILL.md"))) >= 25
    assert len(INSTRUCTION_SKILLS) >= 50, "the widened glob must reach the generic skills too"


# ── source-repo roots that do not exist here (Known Issue 56) ───────────────
# `_path_like` only reads a token as a path when it has a source extension or starts at a
# real top-level directory, so a root this repo never had is invisible to the guard above:
# `sessions/`, `site/content/` and `content/social/` were the source repo's session folder,
# page tree and social folder, and a skill that says "save to `sessions/…`" or "Content root:
# `site/content/`" sends a builder to a directory nobody will create. Named here, because a
# guard cannot infer which absent directory is a typo and which is a leftover. Session docs
# live in `docs/superpowers/sessions/`; pages in `src/pages/` and, built, in `dist/`.
# Scope: every non-vendored skill, every command and every agent: one guard for the three
# trees a session loads as instructions. The agents joined on 2026-09-24 for the `sessions/`
# root (Known Issue 56's agent half: 84 lines in 33 agents named it), and for every other
# root once the WordPress-era recipes that named `site/content` were gone.
DEAD_ROOTS = (
    ("bare `sessions/` (use `docs/superpowers/sessions/`)", re.compile(r"(?<![\w/.-])sessions/")),
    ("`site/content` (pages are `src/pages/`, built `dist/`)", re.compile(r"\bsite/content\b")),
    ("`site/system` (the source repo's system folder)", re.compile(r"\bsite/system\b")),
    ("`content/…` (the source repo's content folder)",
     re.compile(r"(?<![\w/.-])content/(?:social|prompts)/")),
)
COMMANDS_DIR = ROOT / ".claude/commands"
AGENT_ROOTS = DEAD_ROOTS
ROOTS_FOR = {**{p: DEAD_ROOTS for p in INSTRUCTION_SKILLS + sorted(COMMANDS_DIR.rglob("*.md"))},
             **{p: AGENT_ROOTS for p in sorted(AGENTS_DIR.glob("bsuk-*.md"))}}


def dead_root_hits(f: pathlib.Path, roots=DEAD_ROOTS):
    out = []
    for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        for why, rx in roots:
            if rx.search(line):
                out.append(f"{f.name}:{lineno}  {why}  |  {line.strip()[:110]}")
    return out


@pytest.mark.parametrize("doc", list(ROOTS_FOR),
                         ids=lambda p: p.parent.name if p.name == "SKILL.md" else p.stem)
def test_no_skill_command_or_agent_names_a_source_repo_root(doc):
    bad = dead_root_hits(doc, ROOTS_FOR[doc])
    assert bad == [], (
        "a directory the source repo had and this repo does not — a builder told to write "
        "there creates a stray folder or fails:\n  " + "\n  ".join(bad))


def test_the_dead_root_guard_actually_fires(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("Save to `sessions/2026-01-01-x.md`.\n"
                 "> **Content root:** `site/content/`\n"
                 "Captions live in `content/social/x.md`.\n"
                 "Save to `docs/superpowers/sessions/2026-01-01-x.md`.\n"   # the real folder: silent
                 "Build into `src/pages/` and read `dist/`.\n",            # silent
                 encoding="utf-8")
    assert [h.split("  ")[0] for h in dead_root_hits(p)] == [
        "SKILL.md:1", "SKILL.md:2", "SKILL.md:3"], dead_root_hits(p)


# ── source-repo files named in prose (follow-up to Known Issue 56) ──────────
# `_path_like` reads backticked paths; these three were named bare in prose and so slipped past
# it. `scripts/interior_29_audit.py` (the source repo's 29-check auditor), `docs/reference/
# top-pages.md` (its search-console export) and `data/structure.json` (its architecture
# manifest) were never ported. The auditors here are `scripts/final_page_audit.py`,
# `scripts/page_hardening_scan.py` and `scripts/evidence_audit.py`; the route list is
# `data/page-map.json`; search-console data is NOT FETCHED until project 6 (Known Issue 14),
# so a line may still name top-pages only to say it is not fetched.
DEAD_FILES = (
    ("`interior_29_audit.py` (use `scripts/final_page_audit.py`)",
     re.compile(r"interior_29_audit"), None),
    ("`top-pages.md` (search-console data is NOT FETCHED until project 6)",
     re.compile(r"top-pages(?:\.md)?\b"), re.compile(r"NOT FETCHED|project 6")),
    ("`structure.json` (the route list is `data/page-map.json`)",
     re.compile(r"\bstructure\.json\b"), None),
)


def dead_file_hits(f: pathlib.Path):
    out = []
    for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        for why, rx, excuse in DEAD_FILES:
            if rx.search(line) and not (excuse and excuse.search(line)):
                out.append(f"{f.name}:{lineno}  {why}  |  {line.strip()[:110]}")
    return out


@pytest.mark.parametrize("doc", INSTRUCTION_SKILLS + sorted(COMMANDS_DIR.rglob("*.md")),
                         ids=lambda p: p.parent.name if p.name == "SKILL.md" else p.stem)
def test_no_skill_or_command_names_a_source_repo_file(doc):
    bad = dead_file_hits(doc)
    assert bad == [], (
        "a file the source repo had and this repo does not — a builder told to read or run "
        "it stops or guesses:\n  " + "\n  ".join(bad))


def test_the_dead_file_guard_actually_fires(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("RUN FIRST: python3 scripts/interior_29_audit.py\n"
                 "Check top-pages.md first.\n"
                 "1. Is this page in data/structure.json?\n"
                 "top-pages.md is NOT FETCHED until project 6.\n"       # excused: silent
                 "Read data/page-map.json and run scripts/final_page_audit.py.\n",  # silent
                 encoding="utf-8")
    assert [h.split("  ")[0] for h in dead_file_hits(p)] == [
        "SKILL.md:1", "SKILL.md:2", "SKILL.md:3"], dead_file_hits(p)


def test_the_root_guard_reads_all_three_trees():
    # A glob that silently stopped matching would make the parametrised guard vacuous.
    trees = {p.relative_to(ROOT).parts[1] for p in ROOTS_FOR}
    assert trees == {"skills", "commands", "agents"}, trees
    assert sum(1 for p in ROOTS_FOR if p.parent == AGENTS_DIR) >= 41


def test_the_bare_sessions_root_spares_the_real_folder():
    bare = DEAD_ROOTS[0][1]
    for hit in ("Save to `sessions/2026-09-23-x.md`", "ls sessions/ | head",
                "tracks completion via sessions/batch-1.json", "**Sessions:** `sessions/`"):
        assert bare.search(hit), hit
    for ok in ("Save to `docs/superpowers/sessions/<YYYY-MM-DD>-x.md`",
               "ls docs/superpowers/sessions/", "**Sessions:** `docs/superpowers/sessions/`"):
        assert not bare.search(ok), ok


# ── what a pack names (project-5 readiness, 2026-09-23) ─────────────────────
# rules/copy.md named `@bsuk-entity-incorporation-agent` as "the active engine" of the entity
# loop; no such agent was ever ported, so a builder following the pack called nothing. The
# same pack had Lisa Bright "writing from Carlisle, Carlisle": a find-and-replace of the old
# city (Known Issue 16) that doubled the town where the county belongs.
PACK_AGENT = re.compile(r"@(bsuk-[a-z0-9-]*[a-z0-9])")
TOWN_TWICE = re.compile(r"\bCarlisle,\s+Carlisle\b")


@pytest.mark.parametrize("pack", sorted((ROOT / "rules").glob("*.md")), ids=lambda p: p.stem)
def test_every_agent_a_pack_calls_exists(pack):
    bad = [f"{pack.name}:{n}  @{a}"
           for n, l in enumerate(pack.read_text(encoding="utf-8").splitlines(), 1)
           if not any(m in l for m in MARKERS)
           for a in PACK_AGENT.findall(l)
           if not (AGENTS_DIR / f"{a}.md").exists() and not (SKILLS_DIR / a).is_dir()]
    assert bad == [], "a pack calls an agent or skill that does not exist:\n  " + "\n  ".join(bad)


def test_no_instruction_file_writes_the_town_twice():
    files = [ROOT / "CLAUDE.md", *sorted((ROOT / "rules").glob("*.md")),
             *sorted(REFERENCE_DIR.glob("*.md")), *ROOTS_FOR]
    bad = [f"{f.relative_to(ROOT)}:{n}" for f in files
           for n, l in enumerate(f.read_text(encoding="utf-8").splitlines(), 1)
           if TOWN_TWICE.search(l)]
    assert bad == [], ("the breeder is in Carlisle, Cumbria (Known Issue 16):\n  "
                       + "\n  ".join(bad))


# ── CLAUDE.md working rules 10–17 have ledger rows (user ruling R5, 2026-09-23) ────────────
#: What each of the eight is held up by. The ones with a mechanical backstop name the pytest
#: file that exercises it — the same `test` form `design-system-nine` uses — and the others
#: are `untested`, which scripts/quality_report.py lists in §5 as deletion candidates. Rule 10
#: governs how a decision is SHOWN, rule 11 what a page may do to a served file (only the two
#: legacy logo rasters are guarded, tests/py/test_images.py), and rule 13's board half has only
#: a partial check (tests/py/test_board_previews.py: the `table` shape's three styles — nothing
#: requires a table section to use that shape). Rule 16 gained its gate with the user's
#: ruling R12 (tests/py/test_rule16_gate.py). Rule 17 arrived with the system-gaps build, whose
#: approval refusal is its gate (tests/py/test_family_rules_on_board.py); its row was added when
#: `foundation` was merged into p5-readiness.
CLAUDE_MD_RULES = {
    10: ("untested", None),
    11: ("untested", None),
    12: ("test", "tests/py/test_link_parity.py"),
    13: ("untested", None),
    14: ("test", "tests/py/test_facts_preserved.py"),
    15: ("test", "tests/py/test_verbatim_set.py"),
    16: ("test", "tests/py/test_rule16_gate.py"),
    17: ("test", "tests/py/test_family_rules_on_board.py"),
}
WORKING_RULE = re.compile(r"^(1[0-7])\. \*\*", re.M)


def _claude_md_rows():
    return {r["claude_md"]: r for r in index()["rules"] if "claude_md" in r}


def test_claude_md_numbers_working_rules_10_to_17():
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert sorted(int(n) for n in WORKING_RULE.findall(text)) == list(range(10, 18))


def test_every_working_rule_10_to_17_has_one_ledger_row():
    rows = _claude_md_rows()
    assert sorted(rows) == list(range(10, 18)), sorted(rows)
    for n, (enforced, test) in CLAUDE_MD_RULES.items():
        r = rows[n]
        assert r["enforced"] == enforced, (n, r)
        assert r.get("test") == test, (n, r)
        assert "pack" not in r, (n, "a CLAUDE.md rule is not written in a pack")
        if test:
            assert (ROOT / test).is_file(), (n, test)


def test_quality_report_reads_the_eight_rows_as_ruled():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import quality_report  # noqa: E402

    rows = _claude_md_rows()
    ids = {rows[n]["id"]: n for n in rows}
    assert quality_report.broken_test_links(index(), quality_report.registry_check_ids()) == []
    orphans = {ids[i] for i in quality_report.deletion_candidates(index()) if i in ids}
    assert orphans == {n for n, (e, _) in CLAUDE_MD_RULES.items() if e == "untested"}, orphans
    assert quality_report.judgment_overflow(index()) is None
