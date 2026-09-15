import json, pathlib
from extract_wp import parse_page, classify, RICH_SLUGS
FIX = pathlib.Path(__file__).parent / "fixtures"


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


def test_schema_phone_is_scrubbed():
    home = pathlib.Path("/Users/apple/bluestaffyuk-site/index.html")
    page = parse_page(home, url_path="/")
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
