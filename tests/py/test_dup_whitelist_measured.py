"""Every whitelist stem must be a line the built site really repeats.

The whitelist is an EXEMPTION list: each entry silences a passage the DUP gate would
otherwise report. An entry that no longer matches the built pages is dead weight that reads
as evidence, and an entry written too greedily (the longest run on ONE page rather than the
invariant core shared by all pages carrying that chrome) exempts nothing on the pages that
carry the shorter variant — that is how the 2026-09-17 first draft left the CTA fragment
reported nine times and the delivery line eight.

So: measure, do not assert from memory. These tests run against the real `dist/` and skip
when it is absent, because a stale or missing build must not be able to turn the check green.
Reproduce the measurement with `python3 scripts/measure_chrome.py`.
"""
import json
import pathlib
import re

import pytest

import dup_content_audit as d
from _slugs import page_key
from measure_chrome import _contains

REPO = pathlib.Path(__file__).resolve().parents[2]
DIST = REPO / "dist"
MIN_PAGES = 3

# The review quotes are whitelisted on a different ground from the chrome stems, so they
# are measured on different terms (spec §5 "Reviews", project 4 Task 6). A chrome stem
# earns its exemption by being carried by three or more pages; a review quote earns it by
# being a row of data/reviews.json that CLAUDE.md mandates be reused verbatim wherever a
# board places it. Not every quote is placed on three pages today, and a page-count floor
# would report the site's own review data as dead weight. What IS measured: the entries
# match the data file token for token, so an edited quote cannot leave a stale stem
# behind, and a quote a built page does carry is carried whole.
REVIEW_STEMS = [" ".join(re.findall(r"[a-z0-9$']+", r["quote"].lower()))
                for r in json.loads((REPO / "data/reviews.json").read_text(encoding="utf-8"))]
CHROME_STEMS = [s for s in d.WHITELIST_SNIPPETS if s not in set(REVIEW_STEMS)]

pytestmark = pytest.mark.skipif(not DIST.is_dir(), reason="no dist/ — run the build first")


@pytest.fixture(scope="module")
def pages():
    return {page_key(p, DIST): d.words(p) for p in DIST.rglob("index.html")}


def _carrying(pages, stem):
    toks = d.re.findall(r"[a-z0-9$']+", stem.lower())
    return sorted(s for s, ws in pages.items() if _contains(ws, toks))


@pytest.mark.parametrize("stem", CHROME_STEMS)
def test_every_whitelist_stem_is_really_repeated_chrome(pages, stem):
    on = _carrying(pages, stem)
    assert len(on) >= MIN_PAGES, (
        f"whitelist stem appears on {len(on)} page(s) {on}, below the {MIN_PAGES}-page "
        f"chrome threshold — re-measure with scripts/measure_chrome.py: {stem!r}")


@pytest.mark.parametrize("stem", CHROME_STEMS)
def test_no_whitelist_stem_is_greedier_than_its_invariant_core(pages, stem):
    """Trimming a word off either end must not reach MORE pages than the stem itself.

    A stem that grows its page count when shortened is longer than the chrome it is meant
    to exempt, and the remainder gets reported on every page carrying the shorter variant.
    """
    toks = d.re.findall(r"[a-z0-9$']+", stem.lower())
    if len(toks) <= d.MIN_WORDS:
        pytest.skip("already at the minimum shingle length; nothing to trim")
    here = len(_carrying(pages, stem))
    for shorter in (toks[1:], toks[:-1]):
        reach = sum(1 for ws in pages.values() if _contains(ws, shorter))
        assert reach <= here, (
            f"trimming to {' '.join(shorter)!r} reaches {reach} pages vs {here} — the stem "
            f"is greedier than the chrome it exempts: {stem!r}")


def test_the_whitelist_does_not_exempt_the_migrated_content_baseline():
    """The templated city pages' about and health blocks are prose, not chrome.

    They repeat across nine location pages and MUST keep being reported: whitelisting them
    would hide the very duplication project 4 exists to fix.
    """
    baseline = [
        "we are passionate about breeding staffordshire bull terriers the right way",
        "our breeding dogs undergo full health testing for l 2 hga and hc hsf4",
    ]
    for run in baseline:
        toks = d.re.findall(r"[a-z0-9$']+", run)
        assert d.unwhitelisted_segments(toks) == [toks], f"baseline prose is whitelisted: {run!r}"


@pytest.mark.parametrize("stem", REVIEW_STEMS)
def test_every_review_quote_is_whitelisted(stem):
    """data/reviews.json is the source; the whitelist must carry each row token for token.

    An edited quote that is not carried over here silently un-exempts the new wording and
    leaves the old stem exempting nothing.
    """
    assert stem in d.WHITELIST_SNIPPETS, (
        "a review quote is missing from WHITELIST_SNIPPETS in scripts/dup_content_audit.py "
        f"— add it as a literal so tests/render/lib/dupCorpus.ts reads it too: {stem!r}")


@pytest.mark.parametrize("stem", REVIEW_STEMS)
def test_a_review_quote_a_page_carries_is_carried_whole(pages, stem):
    """Where a review renders, the whole quote renders.

    A slot that renders half a quote would leave the other half reported as page prose —
    the exemption would look present and do nothing. Zero pages is a legitimate state: a
    quote no board has placed yet is still the site's review data.
    """
    toks = d.re.findall(r"[a-z0-9$']+", stem)
    on = _carrying(pages, stem)
    half = " ".join(toks[: max(d.MIN_WORDS, len(toks) // 2)])
    partial = [s for s, ws in pages.items()
               if _contains(ws, d.re.findall(r"[a-z0-9$']+", half)) and s not in on]
    assert not partial, (
        f"these pages carry the opening of a review quote but not the whole of it, so the "
        f"remainder is reported as prose: {partial} — {stem!r}")
