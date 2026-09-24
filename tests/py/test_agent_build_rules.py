"""Agents build the way this repo builds.

Two things the source repo did that this one never does, and that the agents still told a
builder to do (project-5 readiness audit, 2026-09-23):

1. **Edit the build output.** The source site was a WordPress static export, so its agents
   `sed -i`'d, `perl -i`'d and `git add`ed HTML in place. Here `dist/` is rebuilt by
   `npm run build` and is gitignored: an edit there is lost on the next build and a
   `git add dist/` stages nothing. Pages ship from `src/pages/`, posts from
   `src/content/blog/`, sitemaps from `scripts/generate_sitemaps.py`. Reading `dist/` — every
   gate does — is fine; writing it is not.

2. **Hand-write markup against a design system that no longer exists.** The agents' templates
   emit classes (`bsuk-faq-item`, `bsuk-btn`, `bsuk-footer-v1`), variables (`var(--primary)`,
   `var(--font-heading)`) and hex colours (`#F8F9FA`) that `src/` has never defined, while
   project 3's kit (`src/components/kit/*.astro`, tokens in `src/styles/tokens.css`) sits
   unused beside them. A builder that follows the template ships unstyled HTML and a hex
   literal that CLAUDE.md bans from `src/`.
"""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
AGENTS = sorted((ROOT / ".claude/agents").glob("bsuk-*.md"))

WRITES_DIST = re.compile(
    r"\b(?:sed|perl) -i\b[^\n]*(?<![\w/.-])dist/"
    r"|\bmkdir -p (?<![\w/.-])dist/"
    r"|\bgit add\b[^\n]*(?<![\w/.-])dist/"
    r"|open\(\s*['\"]dist/[^'\"]*['\"]\s*,\s*['\"]w"
    r"|[Ww]rite (?:[\w ]{0,20} )?to `?dist/"
    # prose that sends the fix to the build output: "operate on `dist/` output", "edit it in dist/"
    r"|\b(?:[Oo]perate|[Ee]dit|[Pp]atch|[Mm]odify|[Ff]ix)(?: it| them| the page)? (?:on|in) `?dist/")


def numbered(agent):
    return enumerate(agent.read_text(encoding="utf-8").splitlines(), 1)


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_no_agent_writes_into_dist(agent):
    bad = [f"{agent.name}:{n}  {l.strip()[:120]}" for n, l in numbered(agent)
           if WRITES_DIST.search(l) and "never" not in l.lower()]
    assert bad == [], ("dist/ is rebuilt by `npm run build` and gitignored — edit src/ and "
                       "rebuild:\n  " + "\n  ".join(bad))


def test_the_dist_detector_fires_on_writes_and_spares_reads():
    for hit in ("sed -i '' 's|a|b|' dist/x/index.html", "mkdir -p dist/homepage-rebuild",
                "git add dist/", "open('dist/x/index.html', 'w')",
                "assemble → write to `dist/blue-staffy-uk-breeders/index.html`",
                "Confirm the target page is built — operate on `dist/` output, then mirror it",
                "edit it in dist/x/index.html", "patch the page in `dist/`"):
        assert WRITES_DIST.search(hit), hit
    for ok in ("grep -n '<h1' dist/x/index.html", "`dist/` is the built output",
               "python3 scripts/final_page_audit.py", "cp -R dist/ /tmp/x",
               "make every fix in `src/`, rebuild, and re-measure `dist/`",
               "verify the rendered result in `dist/` after `npm run build`"):
        assert not WRITES_DIST.search(ok), ok


# ── templates: the kit, not the source repo's design system ─────────────────
SRC_TEXT = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                     for p in (ROOT / "src").rglob("*")
                     if p.is_file() and p.suffix in (".astro", ".css", ".ts", ".tsx", ".js"))
DEFINED_VARS = set(re.findall(r"(--[a-z0-9-]+)\s*:", SRC_TEXT))
TOKENS = (ROOT / "src/styles/tokens.css").read_text(encoding="utf-8").lower()


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_agent_templates_use_only_classes_and_variables_src_defines(agent):
    bad = []
    for n, l in numbered(agent):
        for attr in re.findall(r'class="([^"]*)"', l):
            bad += [f"{agent.name}:{n}  class {c}" for c in attr.split()
                    if c.startswith("bsuk-") and c not in SRC_TEXT]
        bad += [f"{agent.name}:{n}  var({v})" for v in re.findall(r"var\((--[a-z0-9-]+)", l)
                if v not in DEFINED_VARS]
    assert bad == [], ("the template names a class or variable src/ never defines — use the "
                       "kit component (src/components/kit/) or a token from "
                       "src/styles/tokens.css:\n  " + "\n  ".join(bad))


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_agent_templates_spell_no_hex_the_tokens_do_not_define(agent):
    # A grep pattern that SEARCHES for bad hex values is detection, not a template.
    bad = [f"{agent.name}:{n}  {h}" for n, l in numbered(agent) if "grep" not in l
           for h in re.findall(r"(?<![\w&])#[0-9A-Fa-f]{3,6}\b", l) if h.lower() not in TOKENS]
    assert bad == [], ("a hex colour outside src/styles/tokens.css — name the token instead "
                       "(CLAUDE.md bans a hex anywhere in src/ but tokens.css):\n  " + "\n  ".join(bad))


SECTION_BUILDER = ROOT / ".claude/agents/bsuk-section-builder.md"
CONTACT_FORM_UPDATER = ROOT / ".claude/agents/bsuk-contact-form-updater.md"


def test_the_section_builder_hero_row_passes_the_whole_arrangement():
    # Rule 16: the board's hero pick is four axes Hero.astro reads as props, not `layout` alone.
    row = next(l for l in SECTION_BUILDER.read_text(encoding="utf-8").splitlines()
               if l.startswith("| `hero` |"))
    missing = [p for p in ("`layout`", "`align`", "`media`", "`ledge`", "src/lib/boardStyles.ts")
               if p not in row]
    assert missing == [], "the hero row must pass the board's whole arrangement: missing %s" % missing


def test_the_section_builder_hand_writes_no_class():
    # Hero H1, FAQ H3, eyebrows and quotes are styled inside the kit components; a class string
    # in the section builder is a template the kit has already replaced.
    bad = [f"{n}  {l.strip()[:100]}" for n, l in numbered(SECTION_BUILDER) if 'class="' in l]
    assert bad == [], "the section builder mounts kit components; no hand-written class:\n  " + "\n  ".join(bad)


def test_the_legacy_contact_form_is_named_only_as_retired():
    # No page imports src/components/ContactForm.astro; ContactFormKit replaced it in project 4.
    bad = [f"{n}  {l.strip()[:100]}" for n, l in numbered(CONTACT_FORM_UPDATER)
           if "src/components/ContactForm.astro" in l and "retired" not in l]
    assert bad == [], "the legacy form is retired — name ContactFormKit:\n  " + "\n  ".join(bad)
