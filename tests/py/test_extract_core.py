import json, pathlib, re
import pytest
from extract_wp import (parse_page, classify, RICH_SLUGS, drop_placeholder_telephones)
FIX = pathlib.Path(__file__).parent / "fixtures"
SITE = pathlib.Path("/Users/apple/bluestaffyuk-site")


@pytest.fixture(scope="module")
def synth():
    return parse_page(FIX / "synthetic.html", url_path="/synthetic/")


def test_parse_page_meta_and_body():
    page = parse_page(FIX / "birmingham.html", url_path="/uk-locations/blue-staffy-puppies-birmingham/")
    assert page.title == "Blue Staffy Puppies Birmingham"
    assert page.description == "Blue Staffy Puppies Birmingham"
    assert page.canonical == "/uk-locations/blue-staffy-puppies-birmingham/"
    assert page.robots.startswith("follow, index")
    assert page.h1 == ""                      # known defect, recorded not fixed
    assert "empty-h1" in page.defects
    assert "stub" in page.defects
    assert "<script" not in page.body_html
    assert "wp-json" not in page.body_html and "/feed/" not in page.body_html
    # Fixture is a real 4-word stub page in the old export (entry-content holds one
    # paragraph only); recorded as-is, not padded. Verbatim extraction must keep it.
    assert page.word_count == 4
    assert "Blue Staffy Puppies Birmingham" in page.body_html


@pytest.mark.skipif(not SITE.exists(), reason="live WP clone not present")
def test_schema_phone_is_scrubbed():
    page = parse_page(SITE / "index.html", url_path="/")
    assert "447490" not in json.dumps(page.schema)
    assert page.phone_hits >= 1


def test_classify():
    assert classify("/") == "rich"
    assert classify("/uk-locations/blue-staffy-puppies-birmingham/") == "location"
    assert classify("/blue-staffy-blog-guides/") == "blog"
    assert classify("/category/training/") == "skip"
    assert classify("/form/2029/") == "skip"
    assert classify("/bluestaffyuk-uk/iiashymongmail-com/") == "skip"
    assert "/buy-staffy-puppies-for-sale-uk/" in RICH_SLUGS


def test_body_is_inner_html_without_wrapper(synth):
    assert not synth.body_html.startswith('<div class="entry-content')
    assert "Synthetic Heading One" in synth.body_html


def test_column_header_table_labels(synth):
    labels = re.findall(r'<td data-label="([^"]*)"', synth.body_html)
    # thead table: two data rows labelled by column; row-header table: labelled by its own th
    assert labels[:4] == ["Sex", "Price", "Sex", "Price"]


def test_row_header_table_labels(synth):
    labels = re.findall(r'<td data-label="([^"]*)"', synth.body_html)
    assert labels[4:] == ["Weight", "Height"]


def test_tables_wrapped_and_classed(synth):
    assert synth.body_html.count('class="table-wrap"') == 2
    assert synth.body_html.count("stack-table") == 2


def test_dead_href_unwrap_keeps_spacing(synth):
    assert "hi feed there" in synth.body_html
    assert "hifeedthere" not in synth.body_html
    assert "/feed/" not in synth.body_html


def test_phone_scrubbed_in_body_and_schema(synth):
    assert "PHONE_PLACEHOLDER" in synth.body_html
    assert "447490" not in synth.body_html + json.dumps(synth.schema)
    # href, anchor text, and the ld+json telephone are three distinct occurrences;
    # dropping the dead telephone key must not lose the hit that produced it
    assert synth.phone_hits == 3


def test_placeholder_telephone_dropped_from_schema(synth):
    """No placeholder telephone ships in the migrated JSON-LD."""
    dump = json.dumps(synth.schema)
    assert "telephone" not in dump
    assert "PHONE_PLACEHOLDER" not in dump


def test_drop_placeholder_telephones_walks_nested_lists_and_dicts():
    block = {"@graph": [
        {"@type": "Organization", "telephone": "PHONE_PLACEHOLDER",
         "location": {"telephone": "call PHONE_PLACEHOLDER now", "name": "Glasgow"}},
        {"@type": "Person", "telephone": "+441234567890"},
        [{"telephone": "PHONE_PLACEHOLDER"}],
    ]}
    cleaned, removed = drop_placeholder_telephones(block)
    assert removed == 3
    assert "PHONE_PLACEHOLDER" not in json.dumps(cleaned)
    # a real number is untouched, and unrelated keys survive
    assert cleaned["@graph"][1]["telephone"] == "+441234567890"
    assert cleaned["@graph"][0]["location"]["name"] == "Glasgow"


def test_wp_attributes_stripped(synth):
    assert "data-section" not in synth.body_html
    assert 'id="uagb' not in synth.body_html
    assert "style=" not in synth.body_html
    assert "spectra wrapper content" in synth.body_html


def test_media_headings_and_flags(synth):
    assert len(synth.images) == 1 and synth.images[0]["alt"] == "Blue staffy puppy sitting"
    assert len(synth.embeds) == 1 and "youtube.com/embed" in synth.embeds[0]
    assert synth.headings == [("h1", "Synthetic Heading One"), ("h2", "Synthetic Heading Two")]
    assert "old-price:£1,200" in synth.refresh_flags
    assert synth.canonical == "/synthetic/"


def test_dead_wp_form_removed(synth):
    # The old export embeds a dead WordPress enquiry form listing the sold pups.
    assert "<form" not in synth.body_html
    assert "wpforms-container" not in synth.body_html
    assert "KANE" not in synth.body_html and "Select Puppy Name" not in synth.body_html
    assert "wp-form-removed" in synth.refresh_flags


def test_legacy_in_body_links_are_rewritten(synth):
    # Both legacy paths only resolved through a 301; the extractor is where that is fixed,
    # so the built body must carry the live paths and the fragment must survive.
    assert "/buy-blue-staffy-puppies-uk/" in synth.body_html
    assert "buy-blue-staffy-puppies-for-sale-uk" not in synth.body_html
    assert 'href="/blog/#top"' in synth.body_html
    assert "category/puppy-buying-guide-uk" not in synth.body_html
    # Untouched links stay untouched, and the rewrite is counted.
    assert '"/uk-blue-staffy-breeders-contact/"' in synth.body_html
    assert "legacy-links-rewritten:2" in synth.refresh_flags


def test_rewrite_is_exact_path_not_prefix():
    from extract_wp import rewrite_legacy_href
    assert rewrite_legacy_href("/category/puppy-buying-guide-uk/deeper/") is None
    assert rewrite_legacy_href("/blog/") is None


def test_rewrite_preserves_query_and_accepts_the_slash_less_form():
    from extract_wp import rewrite_legacy_href
    assert (rewrite_legacy_href("/buy-blue-staffy-puppies-for-sale-uk/?utm_source=x")
            == "/buy-blue-staffy-puppies-uk/?utm_source=x")
    assert (rewrite_legacy_href("/category/puppy-buying-guide-uk?page=2#list")
            == "/blog/?page=2#list")
    # WordPress served both spellings; the rewrite lands on the canonical trailing slash.
    assert (rewrite_legacy_href("/buy-blue-staffy-puppies-for-sale-uk")
            == "/buy-blue-staffy-puppies-uk/")
    assert (rewrite_legacy_href("https://www.bluestaffyuk.com/category/puppy-buying-guide-uk")
            == "/blog/")


def test_same_page_fragment_link_never_opens_a_new_tab():
    # A WordPress button carried `target="_blank"` on an in-page `#fragment` link. Clicking it
    # opened a second copy of the page and left the reader where they were, so the jump never
    # happened (nav-jump-target-lands, Known Issues 31 and 81: `#Staffy-adoption` on the UK hub
    # and `#Staffies-adoption` on Glasgow). A same-page link loses the target; a link that
    # leaves the page keeps it.
    from bs4 import BeautifulSoup
    from extract_wp import clean_content_node
    soup = BeautifulSoup(
        '<div><a href="#Staffy-adoption" rel="follow noopener" role="button" target="_blank">Adopt</a>'
        '<a href="https://www.gov.uk/" target="_blank" rel="noopener">GOV.UK</a>'
        '<a href="/uk-locations/#list" target="_blank">Cities</a>'
        '<span id="Staffy-adoption"></span></div>', "lxml")
    node, _, _ = clean_content_node(soup.div)
    jump, external, other_page = node.find_all("a")
    assert "target" not in jump.attrs
    assert jump["href"] == "#Staffy-adoption"        # the link itself is untouched otherwise
    assert external["target"] == "_blank"
    assert other_page["target"] == "_blank"
