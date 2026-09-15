import json, pathlib, re
import pytest
from extract_wp import parse_page, classify, RICH_SLUGS
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
    assert "PHONE_PLACEHOLDER" in json.dumps(synth.schema)
    assert "447490" not in synth.body_html + json.dumps(synth.schema)
    # href, anchor text, and the ld+json telephone are three distinct occurrences
    assert synth.phone_hits == 3


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
