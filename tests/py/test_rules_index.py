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


def test_evidence_ledger_is_empty_and_readable_by_evidence_audit():
    e = _load("evidence-ledger.json")
    # scripts/evidence_audit.py claim_binding() iterates ledger["claims"].
    assert e["claims"] == []


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
        for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            marked = any(m in line for m in MARKERS)
            for tok in BACKTICKED.findall(line):
                p = _path_like(tok)
                if p is None or (ROOT / p).exists() or marked:
                    continue
                bad.append(f"{f.name}:{lineno}  {p}")
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


def _unmarked_missing_paths(f: pathlib.Path):
    bad = []
    for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if any(m in line for m in MARKERS):
            continue
        for tok in BACKTICKED.findall(line):
            p = _path_like(tok)
            if p is None or (ROOT / p).exists():
                continue
            bad.append(f"{f.name}:{lineno}  {p}")
    return bad


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


@pytest.mark.parametrize("skill", sorted(SKILLS_DIR.glob("bsuk-*/SKILL.md")),
                         ids=lambda p: p.parent.name)
def test_every_repo_path_cited_in_a_skill_exists_or_is_marked(skill):
    bad = _unmarked_missing_paths(skill)
    assert bad == [], (
        f"{skill.parent.name} cites a path that does not exist and does not say when it "
        "will. Either fix the path, or mark the line '(arrives in Task N)' / "
        "'(deferred to project N)' / '(not ported — source repo only)':\n  "
        + "\n  ".join(bad))


def test_there_are_skills_to_check():
    # The port wrote 25 system skills; a glob that stopped matching would make the
    # parametrised test above vacuous.
    assert len(list(SKILLS_DIR.glob("bsuk-*/SKILL.md"))) >= 25
