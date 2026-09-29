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


def typed_facts(rel):
    return [f"{rel}:{n}  {line.strip()[:100]}" for n, line in enumerate(_text(rel).splitlines(), 1)
            if TYPED.search(line)]


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
