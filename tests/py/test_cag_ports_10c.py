"""Task 10c (2026-09-29): six pieces of the source operating system ported before the London run.

The user's ruling before the London page run: the page-communication audit (Known Issue 44),
the external-link agent, the entity-incorporation agent, a coat-colour variant builder, a
scam-and-trust agent and the site-side video SEO agent all cross over now, re-based, rather
than waiting for project 6. A port is only real when four things hold, and each is a test here:

1. the file exists with the frontmatter its loader needs (a skill whose `name:` is not its
   directory never loads; an agent without Purpose / On Startup / Rules is incomplete by the
   `bsuk-agent-system-qa` checks);
2. every repo path, agent, skill and npm script it names exists — or the line says
   `NOT AVAILABLE — <reason>`, the port's marker for a source tool with no BSUK equivalent;
3. it types no price, no deposit, no delivery band and no guarantee length: those live in
   `data/*.json` and the file must send the reader there (CLAUDE.md working rule 9);
4. it is wired into `docs/reference/page-run.md` at the row where it runs, so a page run
   cannot skip it, and `data/port-manifest.json` records it as ported, at its real path.
"""
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests/py"))

import marker_check  # noqa: E402
from test_page_run import _run_rows, _steps  # noqa: E402

SKILL = ".claude/skills/bsuk-visual-intelligence/SKILL.md"
AGENTS = {
    "bsuk-external-link-agent": ".claude/agents/cag-external-link-agent.md",
    "bsuk-entity-incorporation-agent": ".claude/agents/cag-entity-incorporation-agent.md",
    "bsuk-coat-variant-builder": ".claude/agents/cag-variant-specialist.md",
    "bsuk-scam-trust-agent": ".claude/agents/cag-scam-specialist.md",
    "bsuk-video-seo-agent": ".claude/agents/cag-video-seo-agent.md",
}
PORTS = {SKILL: ".claude/skills/cag-visual-intelligence/SKILL.md",
         **{f".claude/agents/{n}.md": src for n, src in AGENTS.items()}}
FILES = sorted(PORTS)
EFFORTS = {"low", "medium", "high", "xhigh", "max"}


def _text(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def _frontmatter(rel):
    lines = _text(rel).splitlines()
    assert lines and lines[0].strip() == "---", f"{rel}: no frontmatter"
    out = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return out
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"')
    raise AssertionError(f"{rel}: frontmatter never closed")


# ── 1. the files exist with valid frontmatter ─────────────────────────────────────────────
@pytest.mark.parametrize("rel", FILES)
def test_the_port_exists(rel):
    assert (ROOT / rel).is_file(), f"{rel} has not been ported"


def test_the_skill_frontmatter_loads():
    fm = _frontmatter(SKILL)
    assert fm.get("name") == "bsuk-visual-intelligence"
    assert fm.get("description", "").startswith("Use when"), "a skill description says when to use it"


@pytest.mark.parametrize("name", sorted(AGENTS))
def test_the_agent_frontmatter_and_sections(name):
    rel = f".claude/agents/{name}.md"
    fm = _frontmatter(rel)
    assert fm.get("name") == name
    assert fm.get("description"), f"{name}: empty description"
    assert fm.get("model") == "inherit", f"{name}: model must be inherit"
    assert fm.get("effort") in EFFORTS, f"{name}: effort {fm.get('effort')!r}"
    body = _text(rel)
    for section in ("## Golden Rule", "## Purpose", "## On Startup", "## Rules"):
        assert section in body, f"{name}: missing {section}"


# ── 2. every name it cites exists, or is marked NOT AVAILABLE ────────────────────────────
MARK = "NOT AVAILABLE"
PATH = re.compile(r"(?<![\w/.-])((?:\.claude|scripts|data|docs|src|rules|tests|schemas|public)/[\w./-]*[\w/]"
                  r"|IMAGE-DESIGNS\.md|CLAUDE\.md|WORKFLOW\.md)(?![\w-])")
NAME = re.compile(r"(?<![\w./-])@?(bsuk-[a-z0-9-]*[a-z0-9])(?![\w-])(?!\.\w|/)")
NPM = re.compile(r"\bnpm run (?:-s )?([\w:-]+)")
PLACEHOLDER = re.compile(r"[<\[*{]|YYYY|\.\.\.")
KNOWN = ({p.stem for p in (ROOT / ".claude/agents").glob("*.md")}
         | {p.parent.name for p in (ROOT / ".claude/skills").glob("*/SKILL.md")})
# CSS-class and schema-id shaped `bsuk-` tokens are not agents or skills.
NOT_A_NAME = re.compile(r"bsuk-(?:ontology)$")


def missing_refs(rel):
    npm = set(json.loads(_text("package.json"))["scripts"])
    bad = []
    for n, line in enumerate(_text(rel).splitlines(), 1):
        if MARK in line:
            continue
        for p in PATH.findall(line):
            p = p.rstrip("./")
            if PLACEHOLDER.search(p):
                # `data/boards/<slug>.json`: the directory before the placeholder must exist
                p = PLACEHOLDER.split(p)[0].rsplit("/", 1)[0]
            if not (ROOT / p).exists():
                bad.append(f"{rel}:{n}  path {p}")
        for name in NAME.findall(line):
            if name not in KNOWN and not NOT_A_NAME.search(name):
                bad.append(f"{rel}:{n}  name {name}")
        for s in NPM.findall(line):
            if s not in npm:
                bad.append(f"{rel}:{n}  npm run {s}")
    return bad


@pytest.mark.parametrize("rel", FILES)
def test_the_port_names_nothing_that_does_not_exist(rel):
    bad = missing_refs(rel)
    assert bad == [], ("the port names something BSUK does not have — use the real BSUK tool, or "
                       "write `NOT AVAILABLE — <reason>` on the line:\n  " + "\n  ".join(bad))


def test_the_reference_check_fires(tmp_path):
    p = tmp_path / "probe.md"
    p.write_text("Run `scripts/seam_parity.py` and ask @bsuk-conversion-tracker; npm run nope.\n"
                 "The seam check: NOT AVAILABLE — `scripts/seam_parity.py`, no seams here.\n"
                 "Read `data/boards/<slug>.json`, `data/nowhere/<slug>.json` and "
                 "`data/settings.json`.\n", encoding="utf-8")
    bad = missing_refs(str(p))
    assert [b.split("  ")[1] for b in bad] == [
        "path scripts/seam_parity.py", "name bsuk-conversion-tracker", "npm run nope",
        "path data/nowhere"]


# ── 3. it types no price, deposit, delivery band or guarantee length ─────────────────────
TYPED = re.compile(r"£\s?\d|\$\s?\d|(?<![\w.,-])(?:1500|1700|1,500|1,700)(?![\w,])"
                   r"|\b730\b|\btwo[- ]years?\b|\b(?:72|24)-hour\b|\b3-day\b")
# A bare figure with no currency sign is still a typed fact when it sits near the word it
# prices: "a 500 deposit", "delivery 200–350", "the guarantee runs 730" (review, 2026-09-29).
FACT_WORD = re.compile(r"(?i)\b(deposit|delivery|price[sd]?|pric(?:e|ing)|guarantee|cost)\b")
BARE = re.compile(r"(?<![\w.,£$-])(?:500|1500|1700|1,500|1,700|200\s*[–—-]\s*350|200|350|730)(?![\w,%])")
WINDOW = 40


def _bare_near_word(line):
    for m in BARE.finditer(line):
        lo, hi = max(0, m.start() - WINDOW), m.end() + WINDOW
        if FACT_WORD.search(line[lo:hi]):
            return True
    return False


def typed_facts(rel):
    return [f"{rel}:{n}  {line.strip()[:100]}" for n, line in enumerate(_text(rel).splitlines(), 1)
            if TYPED.search(line) or _bare_near_word(line)]


@pytest.mark.parametrize("rel", FILES)
def test_the_port_types_no_price_or_guarantee(rel):
    bad = typed_facts(rel)
    assert bad == [], ("a price, deposit, delivery figure or guarantee length is typed — name its "
                       "key in data/price-matrix.json, data/puppies.json or data/settings.json "
                       "(`guarantee_label`) instead:\n  " + "\n  ".join(bad))


def test_the_typed_fact_scan_fires():
    for hit in ("a £500 deposit", "priced at 1,700", "the 72-hour window", "a two-year cover",
                "{ low: 1500 }", "730 days", "$185 airport"):
        assert TYPED.search(hit), hit
    for ok in ("`deposit_gbp` in data/settings.json", "`male_gbp`", "the 1280 viewport",
               "`guarantee_label`", "ten years of data"):
        assert not TYPED.search(ok), ok
    for hit in ("a 500 deposit", "delivery costs 200–350 by distance", "the guarantee runs 730",
                "price: 1500"):
        assert _bare_near_word(hit), hit
    for ok in ("a 500ms delay", "the 200 status from curl", "at most 350 words", "70% of the deposit",
               "delivery_min_gbp and delivery_max_gbp"):
        assert not _bare_near_word(ok), ok


@pytest.mark.parametrize("rel", FILES)
def test_the_port_carries_no_source_vocabulary(rel):
    assert marker_check.hits_in(ROOT / rel) == [], rel


# ── 4. wired into the page run, the routing docs and the manifest ────────────────────────
def _block(n):
    """The whole `### Row n steps` block, sub-bullets included."""
    text = _text("docs/reference/page-run.md")
    head = f"### Row {n} steps"
    return re.split(r"\n#{2,3} ", text[text.index(head) + len(head):], maxsplit=1)[0]


def _row(section):
    return next(r for r in _run_rows() if r[1].startswith(section))


def test_visual_intelligence_runs_in_the_harden_sprint_after_the_static_scan():
    rows = _run_rows()
    scan = next(i for i, r in enumerate(rows) if "page_hardening_scan.py" in r[2])
    aeo = next(i for i, r in enumerate(rows) if r[1].startswith("§21"))
    at = [i for i, r in enumerate(rows) if "bsuk-visual-intelligence" in r[2]]
    assert at, "no page-run row runs bsuk-visual-intelligence"
    assert all(scan <= i <= aeo for i in at), "it runs after the static scan and before or with AEO"


def test_the_link_and_entity_agents_run_at_the_research_and_outline_rows():
    assert "bsuk-entity-incorporation-agent" in _row("§8 Entities")[2]
    outline = _row("§11–§12")[2] + "\n".join(_steps(9))
    assert "bsuk-external-link-agent" in outline and "bsuk-entity-incorporation-agent" in outline


def test_video_variant_and_scam_run_where_their_pages_are_built():
    build = _row("§16")[2] + _block(12)
    for name in ("bsuk-video-seo-agent", "bsuk-coat-variant-builder", "bsuk-scam-trust-agent"):
        assert name in build, f"row 12 does not route {name}"
    assert "youtube_embeds" in build


def test_quick_start_routes_every_port():
    qs = _text("docs/reference/quick-start.md")
    for name in ["bsuk-visual-intelligence", *AGENTS]:
        assert name in qs, f"quick-start.md does not route {name}"


@pytest.mark.parametrize("dst", FILES)
def test_the_manifest_records_the_port(dst):
    rows = json.loads(_text("data/port-manifest.json"))
    row = next((r for r in rows if r["src"] == PORTS[dst]), None)
    assert row, f"no manifest row for {PORTS[dst]}"
    assert row["mode"] == "rebase", row
    assert row["dst"] == dst, row
    assert "ported 2026-09-29" in row["notes"], row


def test_known_issue_44_is_closed():
    log = _text("docs/reference/session-log.md")
    ki = re.search(r"^44\. \*\*.*?(?=^\d+\. \*\*)", log, re.M | re.S).group(0)
    assert re.search(r"CLOSED in `[0-9a-f]{7,}`", ki), ki[:200]


# ── review round 1 (2026-09-29) ─────────────────────────────────────────────────────────────
SCAM = ".claude/agents/bsuk-scam-trust-agent.md"
RULING = "docs/reference/answer-board/answers/2026-09-24-questions-for-lisa-bright-followup-2026-09-27.md"
CONFIRM = "NEEDS BREEDER CONFIRMATION — never print until the answer board records it"


def _lines(rel):
    return list(enumerate(_text(rel).splitlines(), 1))


def unqualified_refundable(rel):
    """Lines that would let a writer print the deposit as plainly "refundable". A line may name
    the word only to forbid it, or to state the ruling's condition (up to 70%, a visitor who fails
    to show)."""
    ok = re.compile(r"(?i)never|not |no page|plainly|unqualified|up to 70%|fails? to show")
    return [f"{rel}:{n}" for n, l in _lines(rel)
            if re.search(r"(?i)(?<!non-)refundable", l) and not ok.search(l)]


def test_the_scam_agent_never_tells_a_writer_to_print_refundable_unqualified():
    assert unqualified_refundable(SCAM) == []
    assert RULING in _text(SCAM), "the scam agent must point at the breeder's deposit ruling"
    bad = [f"{n}" for n, l in _lines(SCAM) if "data/faq.json` `deposit`" in l
           and not re.search(r"(?i)never|not |do not", l)]
    assert bad == [], "data/faq.json `deposit` renders a plain 'refundable'; it is not the wording source"


def test_the_refundable_scan_fires(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("Our answer: the deposit, refundable, books the viewing.\n"
                 "No page calls the deposit plainly refundable.\n"
                 "Refundable up to 70% only when a visitor fails to show.\n"
                 "A non-refundable fee is a red flag.\n", encoding="utf-8")
    assert unqualified_refundable(str(p)) == [f"{p}:1"]


def test_red_flags_our_process_cannot_pass_are_held_for_the_breeder():
    bad = [f"{n}  {l.strip()[:90]}" for n, l in _lines(SCAM)
           if re.search(r"(?i)video call|bank transfer|gift card", l) and CONFIRM not in l]
    assert bad == [], "a red flag BSUK's own process may fail is marked:\n  " + "\n  ".join(bad)


def test_the_take_back_is_the_ruling_and_names_no_contract():
    lines = [l for _, l in _lines(SCAM) if re.search(r"(?i)take-back|take back|taken back", l)]
    assert lines, "the scam agent states the take-back ruling"
    for l in lines:
        assert "contract" not in l.lower(), l
    assert any("our fault" in l and "no longer" in l for l in lines), lines


def test_the_scam_agent_restores_safe_payment_and_the_cross_link_section():
    t = _text(SCAM)
    assert "NOT FETCHED — payment method not confirmed by the breeder" in t
    assert "Ready to Buy From a Breeder You Can Check?" in t
    for route in ("/available-puppies/", "/buy-blue-staffy-puppies-uk/", "/uk-blue-staffy-puppy-buying-guide/"):
        assert route in t, route
        assert (ROOT / "src/pages" / route.strip("/")).is_dir(), route
    assert "SectionDivider" not in t


# the visual-intelligence scorecard can reach PASS
SCORE_HEADER = ("#", "Score", "Class", "Rule")
CLASSES = {"measured", "derived", "judgment", "report", "gate"}


def _score_rows():
    lines = _text(SKILL).splitlines()
    head = "| " + " | ".join(SCORE_HEADER) + " |"
    i = lines.index(head)
    rows = []
    for l in lines[i + 2:]:
        if not l.startswith("|"):
            break
        rows.append([c.strip() for c in l.strip().strip("|").split("|")])
    return rows


def test_every_score_row_has_a_class_and_a_rule():
    rows = _score_rows()
    assert len(rows) >= 18
    for r in rows:
        cls = r[2].strip("`* ")
        assert cls in CLASSES, r
        if cls in ("measured", "derived"):
            assert re.search(r"10 ×|÷|=", r[3]), f"a scored row needs its formula: {r}"
    gates = [r[1] for r in rows if r[2].strip("`* ") == "gate"]
    assert any("Coverage" in g for g in gates) and any("Authorization" in g for g in gates)
    assert sum(r[2].strip("`* ") in ("measured", "derived") for r in rows) >= 8


def _verdict(t):
    v = t[t.index("**Verdict:**"):]
    return v[:v.index("\n\n")]


def pass_clause_classes(t):
    """The classes the PASS clause of the verdict rule depends on."""
    v = _verdict(t)
    clause = v[v.index("`PASS`"):v.index("`PASS-WITH-WARNINGS`")]
    return set(re.findall(r"`(%s)`" % "|".join(sorted(CLASSES)), clause))


def test_a_page_can_pass_on_measured_and_derived_rows_alone():
    """Structural (re-review minor 5): the PASS clause names only the scored classes, and the
    table has scored rows for it to read — so PASS is reachable without a judgment call."""
    t = _text(SKILL)
    rows = _score_rows()
    classes = {r[2].strip("`* ") for r in rows}
    assert {"measured", "derived"} <= classes
    assert pass_clause_classes(t) == {"measured", "derived"}, pass_clause_classes(t)
    assert "never change the verdict" in _verdict(t)
    assert "### Worked example" in t


def test_the_pass_clause_check_fires():
    bad = ("**Verdict:** `PASS` — both gates pass, every `measured`, `derived` and `judgment` row "
           "scores 6. `PASS-WITH-WARNINGS` — else.\n\n")
    assert pass_clause_classes(bad) == {"measured", "derived", "judgment"}


# ── re-review 2 (2026-09-29): a ruling never stands in for a result's proof ─────────────────
RESULT_RULE = "A test result or score always needs its ledger `proof`"


def _section(t, start, end):
    return t[t.index(start):t.index(end)]


def ruling_exempts_a_result(t):
    """True when the skill lets a breeder ruling excuse a health RESULT from the §5b FAIL, or
    lets a ruling count without the rulings file's own "What the pages do" column saying it."""
    five_b = _section(t, "**5b. Hard FAIL", "**5c.")
    health = next(l for l in five_b.splitlines() if "health result" in l)
    ruled = _section(t, "**Ruled by the breeder", "**5b. Hard FAIL")
    return bool(re.search(r"(?i)ruling behind it|ruled claim is a ledger update", health)
                or RESULT_RULE not in health
                or "What the pages do" not in ruled
                or not re.search(r"(?i)blanket", ruled))


def test_a_ruling_never_exempts_a_health_result():
    assert not ruling_exempts_a_result(_text(SKILL))
    assert "What the pages do" in _text(RULING)


def test_the_ruling_exemption_check_fires_on_the_old_wording():
    """Mutation: put back the round-1 health bullet and the check must fire."""
    t = _text(SKILL)
    five_b = _section(t, "**5b. Hard FAIL", "**5c.")
    health = next(l for l in five_b.splitlines() if "health result" in l)
    old = ("- a health result, or a health outcome stated as a certainty (\"will not develop\"), "
           "without its ledger proof (`scripts/evidence_audit.py`, check `claim-bound-to-proof`) and "
           "without a breeder ruling behind it (a ruled claim is a ledger update, above);")
    assert ruling_exempts_a_result(t.replace(health, old))
    ruled = _section(t, "**Ruled by the breeder", "**5b. Hard FAIL")
    assert ruling_exempts_a_result(t.replace(ruled, "**Ruled by the breeder.** Any answer counts.\n\n"))


def test_the_agents_agree_a_result_needs_its_proof():
    for rel in (SKILL, SCAM, ".claude/agents/bsuk-entity-incorporation-agent.md"):
        assert RESULT_RULE in _text(rel), rel


def _functions(cell):
    return [f for f in cell.split(" · ") if f.strip()]


def test_the_worked_example_counts_the_city_required_set():
    t = _text(SKILL)
    rows = {r[0]: r[1] for r in (
        [c.strip() for c in l.strip().strip("|").split("|")]
        for l in _section(t, "### 4a.", "### 4b.").splitlines() if l.startswith("| **"))}
    need = len(_functions(rows["**location**"])) + len(_functions(rows["**every page**"]))
    m = re.search(r"Coverage (\d+) of (\d+) required", _section(t, "### Worked example", "## 7."))
    assert m and int(m.group(2)) == need, (m and m.group(0), need)


def test_one_line_length_rule_counted_once():
    t = _text(SKILL)
    assert "70ch" not in t and "65ch" in t
    rows = {r[0]: r[3] for r in _score_rows()}
    assert "ch" not in re.sub(r"`ch`", "", rows["2"]).replace("check", ""), rows["2"]
    assert "75ch" in rows["9"]


def test_differentiation_and_hero_and_schema_rows_are_defined():
    rows = {r[0]: r[3] for r in _score_rows()}
    assert "worst pair" in rows["12"] and "same role" in rows["12"]
    assert "0 shared image files" not in rows["12"]
    assert re.search(r"(?i)hero[^|]*1280 only", rows["1"]), rows["1"]
    assert re.search(r"(?i)filtered to (?:the|this) page", rows["10"]), rows["10"]


# one owner per job (items 5–7)
def test_coat_pairings_have_one_owner():
    for rel in (".claude/skills/bsuk-comparison-page-builder/SKILL.md", ".claude/agents/bsuk-comparison-builder.md"):
        fm = _frontmatter(rel)
        assert "bsuk-coat-variant-builder" in fm["description"], rel
        bad = [f"{rel}:{n}" for n, l in _lines(rel)
               if re.search(r"(?i)blue[- ](?:vs|or|and|against)[- ](?:blue-and-white|black)", l)
               and "bsuk-coat-variant-builder" not in l]
        assert bad == [], "a coat pairing is claimed without handing it to the coat agent: " + str(bad)


def test_the_4_move_loop_has_one_owner():
    for rel in (".claude/skills/bsuk-entity-graph/SKILL.md",
                ".claude/skills/bsuk-comprehensive-page-audit-system/SKILL.md", "rules/copy.md"):
        for n, l in _lines(rel):
            if re.search(r"4-Move|entity-4-move-loop", l) and not l.startswith("id: "):
                assert "bsuk-entity-incorporation-agent" in l, f"{rel}:{n}"
    rule = _text("rules/copy.md").split("id: entity-4-move-loop", 1)[1].split("\n---", 2)[1]
    assert "its vocabulary" not in rule, "name whose vocabulary it is"


def test_outbound_citations_have_one_owner():
    t = _text(".claude/skills/internal-link-agent/SKILL.md")
    assert "§Authority Citations" not in t
    assert "bsuk-external-link-agent" in t


def test_claude_md_and_the_copy_pack_carry_the_wiring():
    claude = _text("CLAUDE.md")
    for tok in ("`@bsuk-coat-variant-builder`", "`@bsuk-scam-trust-agent`", "`bsuk-visual-intelligence`"):
        assert tok in claude, tok
    assert "`@bsuk-entity-incorporation-agent`" in _text("rules/copy.md")


def test_the_youtube_skill_hands_schema_and_sitemap_to_the_video_agent():
    t = _text(".claude/skills/bsuk-youtube/SKILL.md")
    assert "bsuk-video-seo-agent" in _frontmatter(".claude/skills/bsuk-youtube/SKILL.md")["description"]
    assert "<video:duration>" not in t
    d = _text(".claude/agents/bsuk-video-seo-agent.md")
    d = d[d.index("## Protocol D"):d.index("## Rules")]
    for tok in ("Tags", "Thumbnail brief", "no licence detail", "no unproven health result"):
        assert tok in d, tok
