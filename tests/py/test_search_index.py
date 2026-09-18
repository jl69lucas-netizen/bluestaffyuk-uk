"""public/search-index.json is the whole of the site's search (spec §11 amendment 3b).

There is no search service: if a page is missing from this file it cannot be found from the
header at all, and no 404 or redirect check would ever notice. So the file is asserted
against the three sources it is built from — data/page-map.json, data/puppies.json and the
built pages themselves — rather than against a snapshot of itself.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_search_index as B  # noqa: E402

INDEX = ROOT / "public/search-index.json"
DIST = ROOT / "dist"
KINDS = {"Puppy", "Guide", "Location", "Blog", "Page"}


def rows():
    if not INDEX.exists():
        pytest.skip("run npm run build first")
    return json.loads(INDEX.read_text(encoding="utf-8"))


def page_map():
    return json.loads((ROOT / "data/page-map.json").read_text())["pages"]


def built_urls():
    if not DIST.exists():
        pytest.skip("run npm run build first")
    return {url for url, _ in B._pages(DIST)}


def indexable_built_urls():
    """Built pages the robots meta lets in — the same rule the sitemaps use."""
    out = set()
    for url, html in B._pages(DIST):
        if "noindex" not in (B._meta(html, "robots") or ""):
            out.add(url)
    return out


def test_every_row_has_the_four_fields_and_a_known_kind():
    for r in rows():
        assert set(r) == {"url", "title", "kind", "keywords"}, r
        assert r["url"].startswith("/") and r["url"].endswith("/")
        assert r["title"].strip()
        assert r["kind"] in KINDS, r
        assert r["keywords"].strip()


def test_every_built_indexable_page_map_url_is_present():
    """Every page the page map lists, that this repo actually builds and does not mark
    noindex, is findable. Page-map urls with no page in dist yet (the location cluster is
    still being ported) are not the index's problem and are excluded here deliberately."""
    if not DIST.exists():
        pytest.skip("run npm run build first")
    want = {p["url"] for p in page_map()} & indexable_built_urls()
    have = {r["url"] for r in rows()}
    assert not (want - have), sorted(want - have)


#: indexable built urls that are deliberately NOT in the search index, each with its reason.
#: Empty today, and that is the point: the coverage test below is written so that adding a
#: route which is indexable but unfindable costs a line here and a sentence defending it.
#: The only legitimate entry is a page with no sitemap shard — `shard_for` returns None and
#: the builder skips it — and such a page should usually be given a shard instead.
UNINDEXED_BUT_INDEXABLE: dict[str, str] = {}


def test_every_indexable_built_page_is_findable():
    """The inverse of the page-map test above, and the one that actually bites.

    That test checks the pages the PAGE MAP knows are in the index. Nothing checked the
    other direction, so a whole route family the page map does not list — the puppy pages,
    the blog posts, the three index routes, anything project 4 adds — could fall out of the
    index with every other gate still green: it is in the sitemaps, it returns 200, it is
    simply unreachable from the site's own search. This asserts the complement, against an
    allowlist that has to be written down and justified."""
    if not DIST.exists():
        pytest.skip("run npm run build first")
    missing = indexable_built_urls() - {r["url"] for r in rows()} - set(UNINDEXED_BUT_INDEXABLE)
    assert not missing, (
        "indexable built pages the site's own search cannot find: "
        f"{sorted(missing)} — index them, mark them noindex, or add them to "
        "UNINDEXED_BUT_INDEXABLE with a reason")
    stale = set(UNINDEXED_BUT_INDEXABLE) - indexable_built_urls()
    assert not stale, f"allowlist entries that are no longer indexable built pages: {sorted(stale)}"


def test_every_available_puppy_is_present():
    puppies = json.loads((ROOT / "data/puppies.json").read_text())
    available = [p for p in puppies if str(p.get("status", "")).lower() == "available"]
    assert available, "no available puppies in data/puppies.json — the fixture changed"
    have = {r["url"] for r in rows()}
    missing = [p["slug"] for p in available if f"/available-puppies/{p['slug']}/" not in have]
    assert not missing, missing
    by_url = {r["url"]: r for r in rows()}
    for p in available:
        assert by_url[f"/available-puppies/{p['slug']}/"]["kind"] == "Puppy"


def test_no_duplicate_urls():
    urls = [r["url"] for r in rows()]
    dupes = sorted({u for u in urls if urls.count(u) > 1})
    assert dupes == [], dupes


def test_noindex_routes_are_absent():
    have = {r["url"] for r in rows()}
    for url in ("/design-canvas/", "/search/", "/thank-you-blue-staffy-puppies-journey/"):
        assert url not in have, url


def test_the_former_city_is_carried_verbatim_and_never_introduced():
    """Known Issue 16. Three page-map titles still name the breeder's former city. They are
    copied through rather than rewritten, because a result whose title does not match the
    page it opens is its own defect — but the index must not be where a NEW one appears."""
    from_map = {p["title"] for p in page_map() if "Glasgow" in p["title"]}
    carried = [r for r in rows() if "Glasgow" in r["title"]]
    assert all(r["title"] in from_map for r in carried), \
        [r["url"] for r in carried if r["title"] not in from_map]
    # the count is a record, not a target: it falls to zero when the page map is cleaned up
    assert len(carried) <= len(from_map)


def test_keywords_are_title_words_plus_slug_words():
    assert B.keywords("Roman — Male Blue Staffy", "/available-puppies/roman/") == \
        "roman male blue staffy available puppies"


def test_the_index_is_deterministic_and_sorted():
    current = rows()
    assert [r["url"] for r in current] == sorted(r["url"] for r in current)
    if not DIST.exists():
        pytest.skip("run npm run build first")
    assert B.build() == current, "public/search-index.json is stale — rerun the postbuild"
