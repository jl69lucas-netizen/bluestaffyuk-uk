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
import pathlib

import pytest

import dup_content_audit as d
from _slugs import page_key
from measure_chrome import _contains

REPO = pathlib.Path(__file__).resolve().parents[2]
DIST = REPO / "dist"
MIN_PAGES = 3

pytestmark = pytest.mark.skipif(not DIST.is_dir(), reason="no dist/ — run the build first")


@pytest.fixture(scope="module")
def pages():
    return {page_key(p, DIST): d.words(p) for p in DIST.rglob("index.html")}


def _carrying(pages, stem):
    toks = d.re.findall(r"[a-z0-9$']+", stem.lower())
    return sorted(s for s, ws in pages.items() if _contains(ws, toks))


@pytest.mark.parametrize("stem", d.WHITELIST_SNIPPETS)
def test_every_whitelist_stem_is_really_repeated_chrome(pages, stem):
    on = _carrying(pages, stem)
    assert len(on) >= MIN_PAGES, (
        f"whitelist stem appears on {len(on)} page(s) {on}, below the {MIN_PAGES}-page "
        f"chrome threshold — re-measure with scripts/measure_chrome.py: {stem!r}")


@pytest.mark.parametrize("stem", d.WHITELIST_SNIPPETS)
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
