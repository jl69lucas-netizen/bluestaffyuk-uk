import pathlib, re
import pytest
from extract_wp import parse_page, OLD_PUP_IMAGES
from extract_writers import strip_old_pups
FIX = pathlib.Path(__file__).parent / "fixtures"
SITE = pathlib.Path("/Users/apple/bluestaffyuk-site")
SALE = SITE / "buy-blue-staffy-puppies-uk/index.html"


def test_homepage_old_pups_gone_but_prose_kept():
    page = parse_page(FIX / "home.html", "/")
    before = page.word_count
    body, removed = strip_old_pups(page.body_html)
    assert removed >= 4
    low = body.lower()
    assert "meet kane" not in low and "kobe’s overview" not in low and "meet beth" not in low and "meet alis" not in low
    assert not any(img in body for img in OLD_PUP_IMAGES)
    assert "Meet Our Affordable Blue Staffy Puppies" in body       # section heading kept
    assert "Maggie" in body and "Jones" in body                    # parents kept
    assert len(body.split()) > before * 0.85
    assert page.phone_hits >= 1 and "07490" not in body and "447490" not in body


@pytest.mark.skipif(not SALE.exists(), reason="live WP clone not present")
def test_sale_page_old_pups_gone():
    page = parse_page(SALE, "/buy-blue-staffy-puppies-uk/")
    body, removed = strip_old_pups(page.body_html)
    assert removed >= 4
    low = body.lower()
    for n in ("kane", "kobe", "beth", "alis"):
        assert ("%s’s overview" % n) not in low and ("%s's overview" % n) not in low
    assert not any(img in body for img in OLD_PUP_IMAGES)
    assert "Your Adoption Journey" in body                          # later section kept


def test_noop_when_nothing_to_strip():
    html = "<p>Nothing about old pups here.</p><h2>Maggie and Jones</h2>"
    assert strip_old_pups(html) == (html, 0)


def test_prose_only_block_without_image_or_labelled_name_is_kept():
    # "Beth is" in ordinary copy, no <img> and no heading/strong naming a pup: keep it.
    html = ('<div class="wp-block-uagb-container"><p>Our vet nurse Beth is on call for '
            'every litter we raise.</p></div>')
    assert strip_old_pups(html) == (html, 0)


def test_prose_only_block_with_named_heading_is_removed():
    html = ('<div class="wp-block-uagb-container"><h4>Meet KANE</h4>'
            '<p>Kane is a confident boy.</p></div>')
    body, removed = strip_old_pups(html)
    assert removed == 1 and "kane" not in body.lower()


def test_wp_block_group_not_removed_on_prose_only_path():
    html = '<div class="wp-block-group"><h4>Meet KANE</h4><p>Kane is here.</p></div>'
    assert strip_old_pups(html) == (html, 0)


def test_image_match_uses_srcset_data_src_and_ignores_query():
    img = sorted(OLD_PUP_IMAGES)[0]
    for attrs in ('src="/wp-content/uploads/%s?v=2"' % img,
                  'data-src="/wp-content/uploads/%s"' % img,
                  'srcset="/wp-content/uploads/%s 780w, /other.jpg 360w"' % img):
        html = '<div class="wp-block-uagb-image"><img %s></div>' % attrs
        body, removed = strip_old_pups(html)
        assert removed == 1, attrs
        assert img not in body
