import json, pathlib
import pytest
from bs4 import BeautifulSoup
from extract_wp import parse_page, OLD_PUP_IMAGES
from extract_writers import strip_old_pups
FIX = pathlib.Path(__file__).parent / "fixtures"
SITE = pathlib.Path("/Users/apple/bluestaffyuk-site")
SALE = SITE / "buy-blue-staffy-puppies-uk/index.html"


def text_words(html):
    return len(BeautifulSoup(html, "lxml").get_text(" ", strip=True).split())


def test_homepage_old_pups_gone_but_prose_kept():
    page = parse_page(FIX / "home.html", "/")
    before = page.word_count
    body, removed, _notes = strip_old_pups(page.body_html)
    assert removed >= 4
    low = body.lower()
    assert "meet kane" not in low and "meet kobe" not in low
    assert "meet beth" not in low and "meet alis" not in low
    assert not any(img in body for img in OLD_PUP_IMAGES)
    assert "Meet Our Affordable Blue Staffy Puppies" in body       # section heading kept
    assert "Maggie" in body and "Jones" in body                    # parents kept
    # Only the four cards go: measured 0.924 of the body text survives.
    assert 0.88 < text_words(body) / before < 0.97
    assert page.phone_hits >= 1 and "07490" not in body and "447490" not in body


@pytest.mark.skipif(not SALE.exists(), reason="live WP clone not present")
def test_sale_page_old_pups_gone():
    page = parse_page(SALE, "/buy-blue-staffy-puppies-uk/")
    before = page.word_count
    assert "kane’s overview" in page.body_html.lower()              # the phrasing this page uses
    body, removed, _notes = strip_old_pups(page.body_html)
    assert removed >= 4
    low = body.lower()
    for n in ("kane", "kobe", "beth", "alis"):
        assert ("%s’s overview" % n) not in low and ("%s's overview" % n) not in low
    assert not any(img in body for img in OLD_PUP_IMAGES)
    assert "Your Adoption Journey" in body                          # later section kept
    # Measured 0.906 of the body text survives.
    assert 0.876 < text_words(body) / before < 0.936


def test_noop_when_nothing_to_strip():
    html = "<p>Nothing about old pups here.</p><h2>Maggie and Jones</h2>"
    assert strip_old_pups(html) == (html, 0, [])


def test_prose_only_block_without_image_or_labelled_name_is_kept():
    # "Beth is" in ordinary copy, no <img> and no heading/strong naming a pup: keep it.
    html = ('<div class="wp-block-uagb-container"><p>Our vet nurse Beth is on call for '
            'every litter we raise.</p></div>')
    assert strip_old_pups(html) == (html, 0, [])


def test_prose_only_block_with_named_heading_is_removed():
    html = ('<div class="wp-block-uagb-container"><h4>Meet KANE</h4>'
            '<p>Kane is a confident boy.</p></div>')
    body, removed, notes = strip_old_pups(html)
    assert removed == 1 and "kane" not in body.lower()


def test_wp_block_group_not_removed_on_prose_only_path():
    html = '<div class="wp-block-group"><h4>Meet KANE</h4><p>Kane is here.</p></div>'
    assert strip_old_pups(html) == (html, 0, [])


def test_image_match_uses_srcset_data_src_and_ignores_query():
    img = sorted(OLD_PUP_IMAGES)[0]
    for attrs in ('src="/wp-content/uploads/%s?v=2"' % img,
                  'data-src="/wp-content/uploads/%s"' % img,
                  'srcset="/wp-content/uploads/%s 780w, /other.jpg 360w"' % img):
        html = '<div class="wp-block-uagb-image"><img %s></div>' % attrs
        body, removed, notes = strip_old_pups(html)
        assert removed == 1, attrs
        assert img not in body


YORK = SITE / "uk-locations/blue-staffy-puppies-york/index.html"


@pytest.mark.skipif(not YORK.exists(), reason="live WP clone not present")
def test_theme_puppy_cards_stripped_on_location_page():
    page = parse_page(YORK, "/uk-locations/blue-staffy-puppies-york/")
    body, removed, _notes = strip_old_pups(page.body_html)
    assert removed == 4
    assert not any(img in body for img in OLD_PUP_IMAGES)
    assert "bsuk-puppy-card" not in body


def test_emptied_card_grid_wrapper_is_removed():
    img = sorted(OLD_PUP_IMAGES)[0]
    html = ('<div class="bsuk-loc-section"><h2>Available Blue Staffy Puppies</h2>'
            '<div class="bsuk-puppies-grid">'
            '<div class="bsuk-puppy-card"><img src="/wp-content/uploads/%s"><div>BETH</div></div>'
            '</div></div>' % img)
    body, removed, notes = strip_old_pups(html)
    assert removed == 1 and notes == ["puppy-grid-emptied"]
    assert "bsuk-puppies-grid" not in body and "bsuk-puppy-card" not in body
    assert "Available Blue Staffy Puppies" in body


def test_card_grid_kept_when_it_still_has_children():
    img = sorted(OLD_PUP_IMAGES)[0]
    html = ('<div class="bsuk-puppies-grid">'
            '<div class="bsuk-puppy-card"><img src="/wp-content/uploads/%s"><div>BETH</div></div>'
            '<div class="keeper">Maggie, our mum</div></div>' % img)
    body, removed, notes = strip_old_pups(html)
    assert removed == 1 and notes == []
    assert "bsuk-puppies-grid" in body and "Maggie, our mum" in body


def test_old_pup_mentions_counts_remaining_names():
    from extract_writers import old_pup_mentions
    assert old_pup_mentions("<p>Nothing here.</p>") == 0
    assert old_pup_mentions("<p>Ask about Kane or KOBE.</p><p>beth too.</p>") == 3
    assert old_pup_mentions("<p>Early socialisation matters.</p>") == 0


def test_york_cards_fixture_is_stripped_hermetically():
    page = parse_page(FIX / "york-cards.html", "/uk-locations/blue-staffy-puppies-york/")
    body, removed, notes = strip_old_pups(page.body_html)
    assert removed == 4 and notes == ["puppy-grid-emptied"]
    assert not any(img in body for img in OLD_PUP_IMAGES)
    assert "bsuk-puppy-card" not in body
    assert "Available Blue Staffy Puppies" in body                  # section <h2> kept


def test_scrub_schema_drops_only_old_pup_image_nodes():
    from extract_writers import scrub_schema_old_pups
    graph = {"@graph": [
        {"@type": "ImageObject", "@id": "#pup",
         "url": "https://bluestaffyuk.uk/wp-content/uploads/tan-white-staffy-puppy-uk.jpg",
         "contentUrl": "https://bluestaffyuk.uk/wp-content/uploads/tan-white-staffy-puppy-uk.jpg"},
        {"@type": "ImageObject", "@id": "#logo",
         "url": "https://bluestaffyuk.uk/wp-content/uploads/blue-staffy-uk-official-logo0.png"},
        {"@type": "WebPage", "name": "Reference holder",
         "image": {"@id": "https://bluestaffyuk.uk/wp-content/uploads/tan-white-staffy-puppy-uk.jpg"}},
        {"@type": "WebPage", "name": "York",
         "primaryImageOfPage": {"@type": "ImageObject",
                                "url": "/wp-content/uploads/blue-staffy-puppy-uk-sale-300x200.jpg"},
         "image": {"@type": "ImageObject", "url": "/wp-content/uploads/staffy-parents.jpg"}},
    ]}
    out, n = scrub_schema_old_pups(graph)
    assert n == 3
    ids = [d.get("@id") for d in out["@graph"] if isinstance(d, dict)]
    assert "#pup" not in ids and "#logo" in ids
    holder = [d for d in out["@graph"] if d.get("name") == "Reference holder"][0]
    assert "image" not in holder                                     # dangling @id stub dropped
    page = [d for d in out["@graph"] if d.get("name") == "York"][0]
    assert "primaryImageOfPage" not in page                          # key went with its only value
    assert page["image"]["url"] == "/wp-content/uploads/staffy-parents.jpg"
    assert "tan-white-staffy-puppy-uk" not in json.dumps(out)


def test_scrub_schema_is_a_no_op_without_old_pups():
    from extract_writers import scrub_schema_old_pups
    graph = {"@graph": [{"@type": "ImageObject", "url": "/wp-content/uploads/maggie-mum.jpg"}]}
    assert scrub_schema_old_pups(graph) == (graph, 0)


def test_recount_refreshes_old_price_flags():
    from extract_writers import recount
    page = parse_page(FIX / "york-cards.html", "/uk-locations/blue-staffy-puppies-york/")
    page.refresh_flags.append("old-price:£999")                      # stale, not in the new text
    body, _removed, _notes = strip_old_pups(page.body_html)
    recount(page, body)
    assert not [f for f in page.refresh_flags if f.startswith("old-price:")]


def test_img_names_matches_resized_srcset_candidates():
    """A card whose only reference to a sold pup's photo is a resized srcset candidate
    must still be recognised: WP size suffixes are normalised away."""
    from extract_writers import _img_names
    html = ('<div class="wp-block-uagb-info-box"><img src="/wp-content/uploads/placeholder.png" '
            'srcset="/wp-content/uploads/x-300x200.jpg 300w, '
            '/wp-content/uploads/blue-staffy-puppy-uk-sale-768x512.jpg 768w"/>'
            '<h3>Puppy Info</h3></div>')
    box = BeautifulSoup(html, "lxml").select_one(".wp-block-uagb-info-box")
    assert "blue-staffy-puppy-uk-sale.jpg" in _img_names(box)
    assert _img_names(box) & OLD_PUP_IMAGES
    body, removed, _notes = strip_old_pups(html)
    assert removed == 1 and "blue-staffy-puppy-uk-sale" not in body
