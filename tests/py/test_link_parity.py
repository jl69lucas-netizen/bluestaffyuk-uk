"""link_parity_check.py — a rebuilt page links where its board record says, and nowhere else.

`facts_preserved_check.py` asks what a rebuilt page LOST. This asks what it ADDED, which is
the half working rule 12 is about: the breeder approves a link table per page, and a
destination that never appeared on the board is one nobody agreed to send a buyer to.

The unit tests below use fixtures rather than dist/, so they say what the rule IS; the
last two run against the real build and skip when it is absent, so a stale tree cannot turn
the check green.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import link_parity_check as L

DIST = ROOT / "dist"

PAGE = """
<html><body>
<header><a href="/header-nav/">nav</a></header>
<main>
  <aside class="kit-dial"><nav><ol><li><a href="#top">Top</a></li></ol></nav></aside>
  <div class="kit-sheet">
    <nav class="kit-tabbar"><a href="/">Home</a><a href="/available-puppies/">Puppies</a></nav>
    <dialog class="sheet"><ol><li><a href="#top">Top</a></li></ol></dialog>
  </div>
  <nav class="kit-strip"><ol><li><a href="#top">01 Top</a></li></ol></nav>
  <section id="top"><p>Real <a href="/blue-staffy-health-uk/">health</a> prose,
     and a <a href="#top">jump</a>.</p></section>
</main>
<footer><a href="/footer-link/">footer</a></footer>
</body></html>
"""


def test_chrome_same_page_jumps_header_and_footer_are_not_page_links():
    assert L.page_links(PAGE) == ["/blue-staffy-health-uk/"]


def test_a_chrome_subtree_is_cut_at_its_matching_close_tag():
    """The regression the walker exists for: `<div class="kit-sheet">.*?</div>` stops at the
    first nested close tag, which would leave the tab bar's links in the corpus AND eat the
    prose after it. Nesting a real link inside the sheet proves the depth count."""
    nested = ('<main><div class="kit-sheet"><div><div>'
              '<a href="/swallowed/">x</a></div></div></div>'
              '<p><a href="/kept/">y</a></p></main>')
    assert L.page_links(nested) == ["/kept/"]


def test_mailto_is_a_link_and_is_not_exempt():
    page = '<main><p>Write to <a href="mailto:x@example.com">x</a>.</p></main>'
    assert L.page_links(page) == ["mailto:x@example.com"]


def test_dropped_links_are_read_off_the_front_of_the_line():
    rec = {"dropped": {"links": [
        '/uk-locations/staffy-breeding-dogs-glasgow/ ("meet our breeders") — the outreach '
        'page for the city the business has left.']}}
    assert L.dropped_links(rec) == {"/uk-locations/staffy-breeding-dogs-glasgow/"}


def test_the_puppy_grid_is_allowed_only_where_the_record_has_that_shape():
    slugs = [p["slug"] for p in json.loads((ROOT / "data/puppies.json").read_text())]
    with_grid = {"sections": [{"shape": "puppies"}]}
    without = {"sections": [{"shape": "standard"}]}
    assert L.puppy_hrefs(with_grid) == {f"/available-puppies/{s}/" for s in slugs}
    assert L.puppy_hrefs(without) == set()


def _collection_slugs():
    """Every slug a post file on disk claims, read the way the exemption reads it."""
    out = set()
    for f in sorted((ROOT / "src/content/blog").glob("*.md")):
        m = L._POST_SLUG.search(f.read_text(encoding="utf-8"))
        if m:
            out.add(m.group(1).strip().strip("/"))
    return out


def test_the_blog_hubs_post_cards_are_allowed_only_on_a_blog_page_type():
    """The blog hub's card hrefs are rows of src/content/blog, not anchors on a board — the
    puppy grid's argument, one collection over. It is scoped the same way: a `blog` record
    gets the exemption and nothing else does."""
    slugs = _collection_slugs()
    assert slugs, "src/content/blog holds no post with a frontmatter slug"
    hub = {"meta": {"page_type": "blog"}, "sections": []}
    not_a_hub = {"meta": {"page_type": "guide"}, "sections": []}
    assert L.post_hrefs(hub) == {f"/{s}/" for s in slugs}
    assert L.post_hrefs(not_a_hub) == set()
    assert L.post_hrefs({"sections": []}) == set()


def test_the_post_slug_comes_from_the_frontmatter_and_not_from_the_filename():
    """A post's route is its `slug:`, which is what src/pages/[...post].astro builds and what
    the hub's cards link. Deriving it from the filename would exempt a url nothing serves."""
    for f in sorted((ROOT / "src/content/blog").glob("*.md")):
        assert L._POST_SLUG.search(f.read_text(encoding="utf-8")), f"{f.name} has no slug"


def test_no_post_claims_the_blog_hubs_own_url():
    """The defect project 4 Task 14 fixed, kept fixed. While a post's slug was
    `blue-staffy-blog-guides` the hub URL was served by src/pages/[...post].astro — the index
    WAS one post's body — and src/pages/blue-staffy-blog-guides/index.astro could not exist
    beside it."""
    assert "blue-staffy-blog-guides" not in _collection_slugs()


# --- against the real build ----------------------------------------------------------------

REBUILT = json.loads((ROOT / "data/facts/rebuilt.json").read_text())

pytestmark_dist = pytest.mark.skipif(not DIST.is_dir(), reason="no dist/ — run the build first")


@pytestmark_dist
@pytest.mark.parametrize("slug", REBUILT)
def test_every_rebuilt_page_is_in_link_parity_with_its_record(slug):
    problems, examined = L.check(slug)
    assert not problems, "\n".join(problems)
    # A gate that examined nothing is not a pass: every rebuilt page carries body links.
    assert examined > 0, f"{slug}: no body links examined at all"


@pytestmark_dist
def test_the_gate_refuses_an_empty_run():
    assert L.main([]) == 2
