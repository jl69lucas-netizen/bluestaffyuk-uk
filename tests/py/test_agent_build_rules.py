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
