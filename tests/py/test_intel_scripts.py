# tests/py/test_intel_scripts.py — runs the code embedded in .claude/agents/bsuk-competitor-intel.md.
#
# The intel reports are only as good as the snippets that count them: the page-type table (shared
# line for line with bsuk-competitive-keyword-gap-agent, see test_agent_snippets.py), the map
# classifier and the homepage measures. Each is extracted from the agent file exactly as a reader
# would run it, and run here on small inputs (Known Issue 51).
import json
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
AGENT = REPO / ".claude/agents/bsuk-competitor-intel.md"
CLASSIFIER = re.compile(r'python3 - "\$MAP_LIST"[^\n]*<<\'EOF\'\n(.*?)\nEOF\n', re.S)
HOMEPAGE = re.compile(r'python3 - "\$RAW_HTML"[^\n]*<<\'EOF\'\n(.*?)\nEOF\n', re.S)
BLOCK = re.compile(r'^rows = json\.load\(open\("data/locations\.json"\)\)\n.*?^kind = lambda path: [^\n]*\n',
                   re.M | re.S)


@pytest.fixture
def kind(monkeypatch):
    """intel's `kind(path)`: the shared page-type table, run against the real data/locations.json."""
    monkeypatch.chdir(REPO)
    ns = {"json": json, "re": re}
    exec(BLOCK.findall(AGENT.read_text(encoding="utf-8"))[0], ns)
    return ns["kind"]


@pytest.mark.parametrize("path,want", [
    ("/careers/", None),                                   # not care-guide: whole words only
    ("/about-us/careers/", "about"),
    ("/preview/", None),                                   # not reviews
    ("/reviews/", "reviews"),
    ("/customer-testimonials/", "reviews"),
    ("/adviceandwelfare/costofliving/petcalculator", None),  # not price
    ("/puppy-prices/", "price"),
    ("/pricing/", "price"),
    ("/healthy-treats/", None),                            # not health
    ("/health-testing/", "health"),
    ("/pet-advice/staffy-care.html", "care-guide"),        # a dot ends a word
    ("/staffy_grooming/", "care-guide"),                   # so does an underscore
    ("/contact-us/", "contact"),
    ("/contactus/", "contact"),
    ("/enquiry-form/", "contact"),
    ("/faqs/", "faq"),
    ("/breeders/", None),                                  # breed is a whole word, never breeders
    ("/breed-guide/", "breed-guide"),
    ("/litters/", "listing"),
    ("/pups/", "listing"),
    ("/2025/09/our-news/", "blog"),
    ("/post/staffy-health-guide", "blog"),                 # a post folder ...
    ("/post/", "blog"),
    ("/posts/", "blog"),
    ("/post-a-puppy/", "listing"),                         # ... but never a 'post-' page: hyphens split words
    ("/post-an-advert/", None),
    ("/post-op-care/", "care-guide"),
    ("/uk-locations/blue-staffy-puppies-leeds/", "city"),
    ("/uk-locations/blue-staffies-newcastle-under-lyme/", "city"),
])
def test_page_types_match_whole_words(kind, path, want):
    assert kind(path) == want


@pytest.mark.parametrize("path", ["/blog/staffy-vs-pitbull/", "/staffy-versus-pitbull/",
                                  "/blue-staffy-vs-pitbull-london/", "/news/2025/staffy-vs-bully/"])
def test_a_comparison_path_is_a_comparison_before_any_other_row(kind, path):
    # one rule for both agents: the keyword-gap agent no longer puts comparison first on its own
    assert kind(path) == "comparison"


def test_the_keyword_gap_agent_has_no_comparison_override_of_its_own():
    gap = (REPO / ".claude/agents/bsuk-competitive-keyword-gap-agent.md").read_text(encoding="utf-8")
    assert 're.search(r"-vs-|versus", path)' not in gap


def classify(tmp_path, urls, *flags):
    """intel's map classifier, run in a scratch root on `urls`: its printed JSON."""
    (tmp_path / "data").mkdir(exist_ok=True)
    shutil.copy(REPO / "data/locations.json", tmp_path / "data/locations.json")
    (tmp_path / "map.json").write_text(json.dumps(urls), encoding="utf-8")
    found = CLASSIFIER.findall(AGENT.read_text(encoding="utf-8"))
    assert len(found) == 1, f"expected one classifier block, found {len(found)}"
    run = subprocess.run([sys.executable, "-", "map.json", *flags], input=found[0], cwd=tmp_path,
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


def test_pagination_is_never_a_page_or_a_post_and_each_url_counts_once(tmp_path):
    x = "https://x.co.uk"
    d = classify(tmp_path, [f"{x}/blog/", f"{x}/blog/page/2/", f"{x}/blog/page/3", f"{x}/blog?page=4",
                            f"{x}/blog/my-first-post/", f"{x}/blog/my-first-post", f"{x}/blog/category/health/",
                            f"{x}/2025/09/", f"{x}/2025/09/litter-news/", f"{x}/puppies/page/2/", f"{x}/puppies/"])
    assert d["page_types"] == {"blog": 5, "listing": 1}
    assert d["posts"] == 2          # my-first-post and litter-news: not the index, a category or a month
    assert d["pagination"] == 4


def test_key_pages_are_picked_by_script_with_a_fixed_tie_break(tmp_path):
    x = "https://x.co.uk"
    d = classify(tmp_path, [f"{x}/", f"{x}/puppies/rex/", f"{x}/available/", f"{x}/puppies/",
                            f"{x}/faq/", f"{x}/prices/staffy/", f"{x}/breed-guide/",
                            f"{x}/staffy-york/", f"{x}/staffy-hull/", f"{x}/staffy-leeds/", f"{x}/puppies/page/2/"])
    assert d["key_pages"] == {
        "listing": f"{x}/puppies/",               # fewest segments, then the shortest path
        "price-or-faq": f"{x}/prices/staffy/",    # a price page before an FAQ page
        "guide": f"{x}/breed-guide/",             # care guide first, else breed guide
        "city": f"{x}/staffy-hull/",              # same depth and length as York: the URL's order
        "about": None,
    }


def test_bsuk_location_rows_count_as_cities_only_for_a_real_city(tmp_path):
    b = "https://SITE_URL_PLACEHOLDER/uk-locations"
    urls = [f"{b}/blue-staffy-puppies-aberdeen/", f"{b}/staffy-puppies-for-sale-glasgow/",
            f"{b}/blue-staffy-puppies-uk/", f"{b}/staffy-breeding-dogs-glasgow/"]
    assert classify(tmp_path, urls, "--bsuk")["page_types"] == {"city": 2, "listing": 1}  # the UK hub is a listing
    assert classify(tmp_path, urls)["page_types"] == {"city": 3, "listing": 1}  # a competitor's paths: no row rule


def test_a_comparison_post_is_still_a_post(tmp_path):
    x = "https://x.co.uk"
    d = classify(tmp_path, [f"{x}/blog/staffy-vs-pitbull/", f"{x}/2024/05/12/staffy-vs-bully/"])
    assert d["page_types"] == {"comparison": 2}   # typed by the first row that matches ...
    assert d["posts"] == 2                        # ... but a post by the blog row's own patterns


def test_post_folders_count_and_help_centre_articles_do_not(tmp_path):
    # URL shapes from docs/research/competitors/trojanstaffuk.json and pets4homes.json
    trojan = "https://www.trojanstaffuk.com"
    d = classify(tmp_path, [f"{trojan}/post/staffordshire-bull-terrier-health-wellbeing-a-comprehensive-guide",
                            f"{trojan}/post/", f"{trojan}/staffy-puppies", f"{trojan}/post-a-puppy/"])
    assert d["page_types"] == {"blog": 2, "listing": 2}  # /post-a-puppy/ is a listing, not a post folder
    assert d["posts"] == 1                        # /post/ itself is the index
    p4h = "https://www.pets4homes.co.uk"
    urls = [f"{p4h}/pet-advice/homemade-dog-deterrents-that-are-safe-for-your-dog.html", f"{p4h}/pet-advice/",
            f"{p4h}/sale/puppies/staffordshire-bull-terrier/",
            "https://support.pets4homes.co.uk/en/support/solutions/articles/47001254375-advice-for-buying-and-advertising-pets"]
    d = classify(tmp_path, urls)
    assert d["posts"] == 0                        # the help-centre article is never a post; the folder is unseen
    d = classify(tmp_path, urls, "--post-folder=pet-advice")
    assert d["page_types"] == {"blog": 3, "listing": 1}  # the named folder is blog before the table
    assert d["posts"] == 1                        # its index is not a post; the help-centre article still is not


def measure(tmp_path, page, name="home.html"):
    """intel's homepage measures, run in a scratch root on `page` (raw HTML or markdown)."""
    (tmp_path / "tests/py").mkdir(parents=True, exist_ok=True)
    shutil.copy(REPO / "tests/py/test_no_third_party_contacts.py", tmp_path / "tests/py")
    (tmp_path / name).write_text(page, encoding="utf-8")
    found = HOMEPAGE.findall(AGENT.read_text(encoding="utf-8"))
    assert len(found) == 1, f"expected one homepage-measures block, found {len(found)}"
    run = subprocess.run([sys.executable, "-", name], input=found[0], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


HOME = """<html><head><script type="application/ld+json">{"email": "hidden@example.co.uk"}</script></head><body>
<header><img src="/logo.png" alt="Logo"></header>
<img src="data:image/gif;base64,R0lGOD" data-src="/rex.jpg" alt="Blue Staffy puppy Rex at eight weeks">
<img src="/a.jpg"><img src="/b.jpg" alt=""><img src="/c.jpg" alt="IMG_2034.jpg">
<img src="/d.jpg" alt="Two blue puppies asleep in the garden">
<img src="/pixel.gif" width="1" height="1" alt="">
<noscript><img src="/rex.jpg"></noscript>
<picture><source srcset="/hero@2x.PNG 2x"><img src="/hero.jpg" srcset="/hero@2x.PNG 2x" alt="Photo"></picture>
<p>Call us today. Logo file: x@y.PNG</p>
<footer><img src="/logo.png" alt="Logo"></footer></body></html>"""


def test_homepage_images_are_distinct_sources_and_alt_text_is_the_largest_class(tmp_path):
    d = measure(tmp_path, HOME)
    # logo, rex (its data-src), a, b, c, d, hero: the pixel, the noscript copy and the second logo are not counted
    assert d["homepage_images"] == 7
    assert d["alt_missing"] == 2                  # no alt, and an empty alt
    assert d["alt_text"] == "generic"             # Logo, IMG_2034.jpg, Photo: 3 generic, 2 missing, 2 descriptive
    assert d["contact_source"] == "raw-html"


def test_a_tie_between_alt_classes_goes_to_the_worse_one(tmp_path):
    page = '<html><body><img src="/a.jpg"><img src="/b.jpg" alt="A blue Staffy puppy on the sofa"></body></html>'
    assert measure(tmp_path, page)["alt_text"] == "missing"


def test_an_image_name_is_not_an_email_and_call_us_is_not_a_phone(tmp_path):
    d = measure(tmp_path, HOME)
    assert (d["email_shown"], d["phone_shown"]) == (False, False)   # JSON-LD is not printed on the page


def test_links_and_printed_contacts_are_shown(tmp_path):
    page = ('<html><body><a href="mailto:hello@example.co.uk">Email us</a>'
            '<a href="tel:+447700900123">Ring</a></body></html>')
    d = measure(tmp_path, page)
    assert (d["email_shown"], d["phone_shown"]) == (True, True)
    d = measure(tmp_path, "<html><body><p>Ring 01228 496 000 or write to hello@example.co.uk</p></body></html>")
    assert (d["email_shown"], d["phone_shown"]) == (True, True)


def test_markdown_only_gives_contact_signals_but_no_visual_measures(tmp_path):
    d = measure(tmp_path, "# Home\n\n[Call us](tel:01228496000) or email.\n\n![Rex](/rex.jpg)", "home.md")
    assert d["contact_source"] == "markdown-only" and d["phone_shown"] is True and d["email_shown"] is False
    for k in ("homepage_images", "alt_text", "alt_missing"):
        assert d[k]["status"] == "NOT FETCHED"
