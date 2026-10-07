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


def test_an_href_is_read_as_the_url_it_encodes_not_its_html_escaping():
    """An attribute value is HTML: `&amp;` in an href IS `&` in the URL. The London map's
    <noscript> link (CityMapFacade, 2026-10-06) is a query string with four `&`s, which Astro
    writes `&amp;`; read raw, the page's link and the record's link were two different strings,
    and the gate reported the one link twice, as an extra and as a missing one."""
    page = '<main><p><a href="https://maps.google.com/maps?q=London%2C%20UK&amp;z=10&amp;t=m">x</a></p></main>'
    assert L.page_links(page) == ["https://maps.google.com/maps?q=London%2C%20UK&z=10&t=m"]


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


# --- the exemption is POSITIONAL, not page-wide ----------------------------------------------

POST = "/how-to-choose-the-right-blue-staffy-puppy-for-your-family/"
HUB_PAGE = """
<main>
  <section id="latest-guides">
    <div class="bl-cards">
      <article class="kit-card post-card"><h3><a href="%s">The post</a></h3></article>
    </div>
  </section>
  <section id="talk-to-us"><p><a href="/uk-blue-staffy-breeders-contact/">write</a></p></section>
</main>
""" % POST
HUB_PAGE_WITH_PROSE_LINK = HUB_PAGE.replace(
    '<p><a href="/uk-blue-staffy-breeders-contact/">write</a></p>',
    '<p><a href="/uk-blue-staffy-breeders-contact/">write</a> and '
    '<a href="%s">the post again</a></p>' % POST)


def test_a_card_link_leaves_the_corpus_and_a_prose_link_to_the_same_post_does_not():
    """The whole point of cutting the cards rather than allowing the href page-wide: the two
    are the same destination and only one of them is a decision somebody took. A page-wide
    allowance cannot tell them apart, so the prose link would ship unapproved."""
    assert L.page_links(HUB_PAGE, cut_cards=True) == ["/uk-blue-staffy-breeders-contact/"]
    assert L.card_links(HUB_PAGE) == [POST]
    # And with the same href ALSO written into a sentence, the sentence's copy survives the cut.
    assert L.page_links(HUB_PAGE_WITH_PROSE_LINK, cut_cards=True) == [
        "/uk-blue-staffy-breeders-contact/", POST]


def test_cut_cards_is_off_by_default_so_a_non_hub_is_judged_on_every_anchor():
    assert POST in L.page_links(HUB_PAGE)


def test_a_card_subtree_is_cut_at_its_matching_close_tag():
    """The nesting regression `_strip_chrome` was written for, on the card walker: a card holds
    a heading inside a div, and `.*?</...>` would stop at the first close tag and leave the
    rest of the page cut out with it."""
    page = ('<main><article class="post-card"><div><div>'
            '<a href="/swallowed/">x</a></div></div></article>'
            '<p><a href="/kept/">y</a></p></main>')
    assert L.page_links(page, cut_cards=True) == ["/kept/"]
    assert L.card_links(page) == ["/swallowed/"]


def test_a_card_carrying_something_that_is_not_a_collection_row_is_reported():
    """Cutting the cards must not become a hole: what a card contains is checked, not trusted.
    A `.post-card` with an arbitrary href in it would otherwise be a link the board never
    showed anybody, invisible to the gate."""
    record = {"meta": {"page_type": "blog"}, "sections": [], "dropped": {"links": []}}
    collection = L.post_hrefs(record)
    assert POST in collection, "the moved post should be a row of the collection"
    assert "/some-other-page/" not in collection


def test_the_real_hub_exercises_the_card_cut():
    """A rule nothing on the built site reaches is a rule nobody is testing. The hub must
    actually carry at least one card link, or the two assertions above are theatre."""
    page = DIST / "blue-staffy-blog-guides" / "index.html"
    if not page.is_dir() and not page.exists():
        pytest.skip("no dist/ — run the build first")
    html = page.read_text(encoding="utf-8")
    cards = L.card_links(html)
    assert cards, "the hub built no .post-card links"
    assert set(cards) <= L.collection_hrefs()
    assert not (set(cards) & set(L.page_links(html, cut_cards=True))), (
        "a card href is still in the page corpus — the cut did not happen")


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


def test_a_same_page_fragment_in_the_record_is_not_owed_to_the_page():
    """The page side drops `#section` jumps (nav-anchors-resolve owns them), so the record side
    must drop them too, or every in-page CTA a board lists reads as missing (London, 2026-10-03)."""
    record = {"sections": [{"links": {"internal": [{"href": "#enquiry"}, {"href": "/available-puppies/"}],
                                      "external": []}}]}
    assert L.record_links(record) == {"/available-puppies/"}


# ── a HELD link (the Manchester page run, STOP 3 q12) ─────────────────────────────────────────
# The breeder approved two links on Manchester's board and held them: their `why` says "HELD:
# built only once …", and the page leaves them unbuilt until the condition lands. A held link
# is on the board, so it is never an extra; it is not owed to the page while held, and building
# it early is a defect of its own.

HELD_RECORD = {"sections": [{"shape": "standard", "links": {"internal": [
    {"href": "/held-page/", "why": "Row 8. HELD: built only once the correction has landed on both pages."},
    {"href": "/live-page/", "why": "Row 7."}], "external": []}}]}


def test_a_held_link_is_not_owed_to_the_page():
    assert L.record_links(HELD_RECORD) == {"/live-page/"}
    assert L.held_links(HELD_RECORD) == {"/held-page/"}


def test_a_held_link_built_early_is_reported(tmp_path, monkeypatch):
    page = tmp_path / "dist" / "p" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text('<main><section id="s"><p><a href="/live-page/">live</a> and '
                    '<a href="/held-page/">held</a></p></section></main>', encoding="utf-8")
    boards = tmp_path / "boards"
    boards.mkdir()
    (boards / "p.json").write_text(json.dumps({**HELD_RECORD, "dropped": {"links": []},
                                               "meta": {"page_type": "location"}}), encoding="utf-8")
    monkeypatch.setattr(L, "BOARDS", boards)
    monkeypatch.setattr(L, "DIST", tmp_path / "dist")
    monkeypatch.setattr(L, "built_page", lambda slug, root, dist: dist / slug / "index.html")
    monkeypatch.setattr(L, "resolve_page", lambda slug, root: (slug, None))
    problems, _ = L.check("p")
    assert problems == ["p: /held-page/ is HELD on the record and already on the page"]
