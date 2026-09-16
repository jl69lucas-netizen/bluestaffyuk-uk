import json, pathlib
from extract_wp import parse_page
from extract_writers import (write_rich_page, write_locations, write_page_map,
                             astro_frontmatter, city_from_slug, SLUG_CITY,
                             meta_dict, NOINDEX_PATHS)
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
    pm = json.loads(write_page_map([page], tmp_path, "/Users/apple/bluestaffyuk-site").read_text())
    row = pm["pages"][0]
    assert row["baseline_gsc"] == "NOT FETCHED — GSC property unverified (domain expired); no exports on disk"
    assert row["kind"] == "location" and row["word_count"] == 4

def test_city_names():
    from extract_writers import city_from_slug
    assert city_from_slug("blue-staffy-puppies-birmingham") == "Birmingham"
    assert city_from_slug("staffy-puppies-for-sale-cornwall") == "Cornwall"
    assert city_from_slug("blue-staffies-newcastle-under-lyme") == "Newcastle-under-Lyme"
    assert city_from_slug("staffy-puppies-cardiff-wales") == "Cardiff"
    assert city_from_slug("blue-staffy-puppies-manchester-uk") == "Manchester"
    assert city_from_slug("buy-blue-staffy-puppy-coventry-area") == "Coventry"
    assert city_from_slug("blue-staffy-puppies-for-sale-in-leicester") == "Leicester"
    assert city_from_slug("staffy-breeding-dogs-glasgow") == "Glasgow (breeding dogs)"
    assert city_from_slug("blue-staffy-puppies-uk") == "UK"
    assert city_from_slug("uk-staffordshire-bull-terrier-breeder") == "UK"


def test_city_name_falls_back_to_heuristic_for_unmapped_slug():
    assert "blue-staffy-puppies-plymouth" not in SLUG_CITY
    assert city_from_slug("blue-staffy-puppies-plymouth") == "Plymouth"


def test_page_map_generated_from_comes_from_src(tmp_path):
    page = parse_page(FIX / "birmingham.html", "/uk-locations/blue-staffy-puppies-birmingham/")
    pm = json.loads(write_page_map([page], tmp_path, "/tmp/some-clone").read_text())
    assert pm["generated_from"] == "/tmp/some-clone"


def test_nested_slug_layout_depth(tmp_path):
    page = parse_page(FIX / "birmingham.html", "/uk-locations/blue-staffy-puppies-birmingham/")
    page.url_path = "/a/b/"
    out = write_rich_page(page, tmp_path)
    assert out == tmp_path / "src/pages/a/b/index.astro"
    assert "import BaseLayout from '../../../layouts/BaseLayout.astro';" in out.read_text()


def test_frontmatter_meta_is_valid_json_with_defaults():
    page = parse_page(FIX / "birmingham.html", "/uk-locations/blue-staffy-puppies-birmingham/")
    page.robots = ""; page.og_type = ""
    line = [l for l in astro_frontmatter(page, "x.astro").splitlines()
            if l.startswith("const meta = ")][0]
    meta = json.loads(line[len("const meta = "):].rstrip(";"))
    assert meta["robots"] == "index, follow"
    assert meta["ogType"] == "article"
    assert meta["canonical"].startswith("/")


def test_locations_row_has_og_type_and_robots_defaults(tmp_path):
    page = parse_page(FIX / "birmingham.html", "/uk-locations/blue-staffy-puppies-birmingham/")
    page.robots = ""; page.og_type = ""
    row = json.loads(write_locations([page], tmp_path).read_text())[0]
    assert row["robots"] == "index, follow" and row["og_type"] == "article"


def test_recount_refreshes_counts_and_clears_stub():
    from extract_writers import recount
    page = parse_page(FIX / "birmingham.html", "/uk-locations/blue-staffy-puppies-birmingham/")
    assert "stub" in page.defects
    recount(page, "<p>%s</p><h2>Head</h2><img src='a.jpg' alt='a'>" % (" word" * 60))
    assert page.word_count > 50 and "stub" not in page.defects
    assert len(page.images) == 1 and page.headings == [("h2", "Head")]


def test_noindex_paths_override_old_robots():
    """The thank-you page must be noindex even though Rank Math tagged it index, follow."""
    page = parse_page(FIX / "birmingham.html", "/uk-locations/blue-staffy-puppies-birmingham/")
    page.robots = "follow, index, max-snippet:-1"
    assert meta_dict(page)["robots"] == "follow, index, max-snippet:-1"
    page.canonical = NOINDEX_PATHS[0]
    assert meta_dict(page)["robots"] == "noindex, follow"


def test_thank_you_page_is_in_noindex_paths():
    assert "/thank-you-blue-staffy-puppies-journey/" in NOINDEX_PATHS
