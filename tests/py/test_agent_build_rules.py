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
# A variable written at runtime is defined too: BaseLayout's inline script sets
# `--hdr-measured` with style.setProperty from the header's real height.
DEFINED_VARS |= set(re.findall(r"setProperty\(\s*['\"](--[a-z0-9-]+)", SRC_TEXT))
TOKEN_HEXES = {h.lower() for h in re.findall(
    r"#[0-9A-Fa-f]{3,8}\b", (ROOT / "src/styles/tokens.css").read_text(encoding="utf-8"))}
# A whole hex, longest form first: `#abc` is not "in the tokens" because `#abcdef` is.
HEX = re.compile(r"(?<![\w&])#(?:[0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3,4})\b")
# A grep's quoted search pattern SEARCHES for bad values — detection, not a template — so
# only the pattern is set aside, never the rest of the line.
GREP_PATTERN = re.compile(r"""\bgrep\b(?:\s+-\w+)*\s+(["']).*?\1""")


def undefined_names(line):
    """bsuk-* classes (in class="…" or written as a `.bsuk-x` selector) and var(--x) names
    that src/ never defines."""
    names = [c for attr in re.findall(r'class="([^"]*)"', line) for c in attr.split()
             if c.startswith("bsuk-")]
    names += re.findall(r"(?<![\w-])\.(bsuk-[a-z0-9-]+)", line)
    bad = ["class " + c for c in dict.fromkeys(names) if c not in SRC_TEXT]
    return bad + ["var(%s)" % v for v in re.findall(r"var\((--[a-z0-9-]+)", line)
                  if v not in DEFINED_VARS]


def template_hexes(line):
    """Whole hex colours a template line spells outside a grep pattern that tokens.css lacks."""
    return [h for h in HEX.findall(GREP_PATTERN.sub("grep", line)) if h.lower() not in TOKEN_HEXES]


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_agent_templates_use_only_classes_and_variables_src_defines(agent):
    bad = [f"{agent.name}:{n}  {x}" for n, l in numbered(agent) for x in undefined_names(l)]
    assert bad == [], ("the template names a class or variable src/ never defines — use the "
                       "kit component (src/components/kit/) or a token from "
                       "src/styles/tokens.css:\n  " + "\n  ".join(bad))


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_agent_templates_spell_no_hex_the_tokens_do_not_define(agent):
    bad = [f"{agent.name}:{n}  {h}" for n, l in numbered(agent) for h in template_hexes(l)]
    assert bad == [], ("a hex colour outside src/styles/tokens.css — name the token instead "
                       "(CLAUDE.md bans a hex anywhere in src/ but tokens.css):\n  " + "\n  ".join(bad))


def test_the_class_variable_and_hex_guards_fire_and_spare():
    six = sorted(h for h in TOKEN_HEXES if len(h) == 7)[0]
    short = six[:4]
    assert short not in TOKEN_HEXES
    assert template_hexes("color: %s;" % short) == [short], "a prefix of a token is not a token"
    assert template_hexes("color: %s;" % six) == []
    assert template_hexes('grep -i "#aaa\\|#bbb" dist/x/index.html') == []
    assert template_hexes('grep -c x dist/a.html; style="color:#123456"') == ["#123456"]
    assert undefined_names("the `.bsuk-ghost-rail` rule") == ["class bsuk-ghost-rail"]
    assert undefined_names('<div class="bsuk-ghost-rail">') == ["class bsuk-ghost-rail"]
    assert undefined_names("top: var(--hdr-measured)") == []
    assert undefined_names("top: var(--ghost-var)") == ["var(--ghost-var)"]


SECTION_BUILDER = ROOT / ".claude/agents/bsuk-section-builder.md"


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


INSTRUCTIONS = sorted([*AGENTS, *(ROOT / ".claude/skills").glob("*/SKILL.md"),
                       *(ROOT / ".claude/commands").glob("*.md")])


@pytest.mark.parametrize("doc", INSTRUCTIONS, ids=lambda p: p.parent.name if p.name == "SKILL.md" else p.stem)
def test_the_legacy_contact_form_is_named_only_as_retired(doc):
    # No page imports src/components/ContactForm.astro; ContactFormKit replaced it in project 4.
    # `ContactForm.astro` catches the full path and the bare file name; ContactFormKit.astro
    # does not contain it.
    bad = [f"{doc.relative_to(ROOT)}:{n}  {l.strip()[:100]}" for n, l in numbered(doc)
           if "ContactForm.astro" in l and "retired" not in l]
    assert bad == [], "the legacy form is retired — name ContactFormKit:\n  " + "\n  ".join(bad)
