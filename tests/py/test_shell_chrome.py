"""One header, one footer, and the right one — measured on the built site.

Project 4 moves pages onto the kit shell a few at a time, which makes two failures possible
that nothing else would catch:

  * TWO headers. `src/layouts/BaseLayout.astro` renders the legacy pair as the FALLBACK of
    its `header`/`footer` slots. A page that fills the slot gets the kit; a page that renders
    a header inside its own body as well would get both, and the duplicate is invisible in a
    screenshot of the top of the page. The migrated export carried exactly this defect
    (Known Issue: duplicate headers) and it is the reason the slots exist rather than a prop.

  * The WRONG one. A page that was supposed to move and did not is a page nobody looks at
    again, and it silently keeps the legacy chrome for the rest of the project.

So the expectation is written down per route here, and `data/facts/rebuilt.json` decides the
second half of it: a slug listed there has been rewritten on PageShell and must be on the
kit; a rich page that has not been rebuilt yet must still be on the legacy pair, unchanged.
"""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"

HEADER_TAG = re.compile(r"<header\b")
FOOTER_TAG = re.compile(r"<footer\b")

# The hubs and the puppy pages moved onto PageShell in project 4 task 3 — chrome only, no
# content change. The puppy pages are one template, so the whole directory is named.
KIT_ROUTES = {"/available-puppies/", "/uk-locations/", "/blog/"}
KIT_PREFIXES = ("/available-puppies/",)

# Internal preview routes, noindex, which RENDER header specimens as their CONTENT:
# /kit-preview/ demos the header component below its own, and every /board-preview/<slug>/
# shows three styles of several sections at once (a hero section is three header specimens
# by itself). Their pages are on BaseLayout, so they also carry the legacy header for real —
# a page that is simultaneously on the legacy chrome and showing a kit header to look at is
# the one place where "both headers" is the correct answer. Counting specimens as page
# chrome would make this a test about the previews. The prefix, not a fixed set: the route
# builds one page per DRAFT record, so the set grows with every page board (task 7 onward).
PREVIEW_PREFIXES = ("/board-preview/",)
PREVIEWS = {"/kit-preview/"}


def _is_preview(route):
    return route in PREVIEWS or route.startswith(PREVIEW_PREFIXES)


def _routes():
    if not DIST.is_dir():
        pytest.skip("no dist/ — run `npm run build` first")
    out = {}
    for html in sorted(DIST.rglob("index.html")):
        rel = html.parent.relative_to(DIST).as_posix()
        out["/" if rel == "." else f"/{rel}/"] = html.read_text(encoding="utf-8")
    return out


def _expected_kit(route, rebuilt):
    if route in KIT_ROUTES or (route.startswith(KIT_PREFIXES) and route not in KIT_ROUTES):
        return True
    return route.strip("/") in rebuilt


def test_every_built_page_has_exactly_one_header_and_one_footer():
    bad = []
    for route, html in _routes().items():
        headers = len(HEADER_TAG.findall(html))
        footers = len(FOOTER_TAG.findall(html))
        if _is_preview(route):
            if headers < 1 or footers < 1:
                bad.append(f"{route}: {headers} header(s), {footers} footer(s)")
            continue
        if headers != 1 or footers != 1:
            bad.append(f"{route}: {headers} header(s), {footers} footer(s)")
    assert not bad, "; ".join(bad)


def test_no_page_mounts_both_the_legacy_header_and_the_kit_one():
    """The slot fallback either fired or it did not. Both is the duplicate-header defect."""
    both = [route for route, html in _routes().items()
            if not _is_preview(route)
            and 'class="site-header' in html and 'class="kit-hdr' in html]
    assert not both, "pages carrying both headers: " + ", ".join(both)


def test_each_page_carries_the_header_its_layout_is_supposed_to_give_it():
    rebuilt = set(json.loads((ROOT / "data/facts/rebuilt.json").read_text()))
    wrong = []
    for route, html in _routes().items():
        if _is_preview(route):
            continue
        kit = 'class="kit-hdr' in html
        legacy = 'class="site-header' in html
        if not (kit or legacy):
            wrong.append(f"{route}: no header at all")
        elif _expected_kit(route, rebuilt) != kit:
            wrong.append(f"{route}: {'legacy' if legacy else 'none'}, expected "
                         f"{'kit' if _expected_kit(route, rebuilt) else 'legacy'}")
    assert not wrong, "; ".join(wrong)


def test_a_rich_page_that_has_not_been_rebuilt_yet_is_still_on_the_legacy_chrome():
    """Stated separately from the sweep above so the un-rebuilt half cannot quietly become
    an empty set: if this list ever empties, project 4 is finished and the assertion should
    be deleted along with the legacy components, not left passing vacuously."""
    rebuilt = set(json.loads((ROOT / "data/facts/rebuilt.json").read_text()))
    routes = _routes()
    remaining = [r for r in routes if r.strip("/") and r.strip("/") not in rebuilt
                 and not r.startswith("/available-puppies/") and not r.startswith("/uk-locations/")
                 and r not in {"/blog/", "/kit-preview/"} and not r.startswith("/board-preview/")]
    assert remaining, "no un-rebuilt rich pages left — retire this test with the legacy header"
    assert all('class="site-header' in routes[r] for r in remaining), remaining
