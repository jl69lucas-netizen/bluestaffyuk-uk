import json, pathlib
from extract_wp import parse_page
from extract_writers import write_rich_page, write_locations, write_page_map, astro_frontmatter
FIX = pathlib.Path(__file__).parent / "fixtures"

def test_write_rich_page_creates_astro_with_props(tmp_path):
    page = parse_page(FIX / "birmingham.html", "/uk-locations/blue-staffy-puppies-birmingham/")
    page.kind = "rich"; page.url_path = "/demo-page/"
    out = write_rich_page(page, tmp_path)
    assert out == tmp_path / "src/pages/demo-page/index.astro"
    text = out.read_text()
    assert text.startswith("---\nimport BaseLayout")
    assert 'title={meta.title}' in text
    assert "<Fragment set:html={body} />" in text
    assert "447490" not in text

def test_write_locations_json(tmp_path):
    page = parse_page(FIX / "birmingham.html", "/uk-locations/blue-staffy-puppies-birmingham/")
    p = write_locations([page], tmp_path)
    data = json.loads(p.read_text())
    assert data[0]["slug"] == "blue-staffy-puppies-birmingham"
    assert data[0]["city"] == "Birmingham"
    assert "empty-h1" in data[0]["defects"] and "stub" in data[0]["defects"]

def test_page_map_records_baseline_not_fetched(tmp_path):
    page = parse_page(FIX / "birmingham.html", "/uk-locations/blue-staffy-puppies-birmingham/")
    pm = json.loads(write_page_map([page], tmp_path).read_text())
    row = pm["pages"][0]
    assert row["baseline_gsc"] == "NOT FETCHED — GSC property unverified (domain expired); no exports on disk"
    assert row["kind"] == "location" and row["word_count"] == 4

def test_city_names():
    from extract_writers import city_from_slug
    assert city_from_slug("blue-staffy-puppies-birmingham") == "Birmingham"
    assert city_from_slug("staffy-puppies-for-sale-cornwall") == "Cornwall"
    assert city_from_slug("blue-staffies-newcastle-under-lyme") == "Newcastle under Lyme"
    assert city_from_slug("staffy-puppies-cardiff-wales") == "Cardiff Wales"
    assert city_from_slug("blue-staffy-puppies-manchester-uk") == "Manchester"
    assert city_from_slug("buy-blue-staffy-puppy-coventry-area") == "Coventry"
    assert city_from_slug("blue-staffy-puppies-for-sale-in-leicester") == "Leicester"
    assert city_from_slug("staffy-breeding-dogs-glasgow") == "Glasgow"
    assert city_from_slug("blue-staffy-puppies-uk") == "UK"
    assert city_from_slug("uk-staffordshire-bull-terrier-breeder") == "UK"
