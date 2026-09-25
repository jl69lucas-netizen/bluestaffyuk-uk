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

from test_agent_snippets import page_type_block  # noqa: E402 — the one block extractor

REPO = pathlib.Path(__file__).resolve().parents[2]
AGENT = REPO / ".claude/agents/bsuk-competitor-intel.md"
CLASSIFIER = re.compile(r'python3 - "\$MAP_LIST"[^\n]*<<\'EOF\'\n(.*?)\nEOF\n', re.S)
HOMEPAGE = re.compile(r'python3 - "\$RAW_HTML"[^\n]*<<\'EOF\'\n(.*?)\nEOF\n', re.S)
MOBILE = re.compile(r'```js\n// the mobile check[^\n]*\n(.*?)\n```\n', re.S)


@pytest.fixture
def kind(monkeypatch):
    """intel's `kind(path)`: the shared page-type table, run against the real data/locations.json."""
    monkeypatch.chdir(REPO)
    ns = {"json": json, "re": re}
    exec(page_type_block(AGENT.name), ns)
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
    ("/breeds/staffordshire-bull-terrier/", "breed-guide"),  # a breed word is still a breed guide ...
    ("/dog-breeds/", "breed-guide"),
    ("/staffy-breed-guide/", "breed-guide"),
    ("/breed-standard-12/", "breed-guide"),                # a short number is not an advert id
    ("/classifieds/4-trvdqjx-pure-breed-ragdoll-stafford", None),  # ... but never 'pure-breed' (pets4homes' Ragdoll advert)
    ("/cross-breed-puppies/", "listing"),                  # nor 'cross-breed': an adjective, not a guide
    ("/classifieds/nq4wdhrql-full-breed-blue-british-shorthair-erith", None),  # nor 'full-breed'
    ("/sale/puppies/mixed-breed/fife", "listing"),         # nor 'mixed-breed'
    ("/en/support/solutions/folders/47000447542", None),   # a bare id segment is not an advert
    ("/staffy-breed-puppies-for-sale/", "listing"),        # a sale advert is a listing, not a guide
    ("/classifieds/ragdoll-breed-kittens/", "listing"),
    ("/classifieds/staffy-breed-info-1234567/", "listing"),  # a trailing numeric id: an advert
    ("/kittens/", "listing"),
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


def test_a_paginated_url_listed_twice_is_one_page_of_the_list(tmp_path):
    # the same page of a list, a slash apart, is one URL: normalised before it is counted
    x = "https://x.co.uk"
    d = classify(tmp_path, [f"{x}/blog/page/2", f"{x}/blog/page/2/", f"{x}/blog?page=3", f"{x}/blog/?page=3",
                            f"{x}/blog/?page=4", f"{x}/puppies/page/2/"])
    assert d["pagination"] == 4               # blog 2, blog 3, blog 4 and puppies 2


def test_www_and_the_bare_host_are_one_site_for_the_classifier(tmp_path):
    d = classify(tmp_path, ["https://x.co.uk/blog/rex/", "https://www.x.co.uk/blog/rex", "https://www.x.co.uk/blog/page/2/",
                            "https://x.co.uk/blog/page/2"])
    assert (d["page_types"], d["posts"], d["pagination"]) == ({"blog": 1}, 1, 1)


def test_the_blog_word_makes_a_post_only_as_a_whole_path_segment(tmp_path):
    x = "https://x.co.uk"
    d = classify(tmp_path, [f"{x}/blog-guides/", f"{x}/staffy-news/", f"{x}/news/litter-due/", f"{x}/articles/",
                            f"{x}/blog-guides/staffy-care-tips/"])
    assert d["page_types"] == {"blog": 5}     # the table still types every one as blog ...
    assert d["posts"] == 1                    # ... but only /news/litter-due/ sits under a blog-word folder
    d = classify(tmp_path, [f"{x}/blog-guides/", f"{x}/blog-guides/staffy-care-tips/"], "--post-folder=blog-guides")
    assert d["posts"] == 1                    # a folder named with the blog word is named with --post-folder


def test_the_real_city_rule_is_written_once(tmp_path):
    # the UK hub and the breeding-dogs outreach row are never cities: one helper, used by both checks
    block = CLASSIFIER.findall(AGENT.read_text(encoding="utf-8"))[0]
    assert block.count('"(" not in') == 1 and block.count('!= "UK"') == 1, "the real-city test is repeated"
    assert "real_city(" in page_type_block(AGENT.name)


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


P4H = "https://www.pets4homes.co.uk"
MARKETPLACE = [  # a multi-species marketplace in pets4homes' URL shapes (the G1 map picked every key page a cat page)
    f"{P4H}/", f"{P4H}/sale/kittens/", f"{P4H}/sale/puppies/", f"{P4H}/sale/puppies/staffordshire-bull-terrier/",
    f"{P4H}/classifieds/k2x9q-blue-staffy-puppies-for-sale-12345678/",  # a Staffy advert
    f"{P4H}/classifieds/4-trvdqjx-pure-breed-ragdoll-stafford",         # a Ragdoll advert: 'pure-breed', no guide
    f"{P4H}/dog-care/", f"{P4H}/cat-care/", f"{P4H}/dog-breeds/staffordshire-bull-terrier/",
    f"{P4H}/sale/kittens/london/", f"{P4H}/sale/puppies/staffordshire-bull-terrier/manchester/",
    f"{P4H}/pricing/cats/", f"{P4H}/faq/",
]


def test_a_marketplaces_key_pages_are_the_breeds_pages(tmp_path):
    d = classify(tmp_path, MARKETPLACE)
    assert d["key_pages"] == {
        "listing": f"{P4H}/classifieds/k2x9q-blue-staffy-puppies-for-sale-12345678/",  # a Staffy page, never /sale/kittens/;
        # among the breed's pages the old tie-break decides: the advert has two segments, the Staffy listing three
        "price-or-faq": f"{P4H}/faq/",       # the only price page names cats: nothing for price, so the FAQ
        "guide": f"{P4H}/dog-breeds/staffordshire-bull-terrier/",  # the breed's own guide before a generic care guide
        "city": f"{P4H}/sale/puppies/staffordshire-bull-terrier/manchester/",  # not the London kittens page
        "about": None,
    }
    assert d["page_types"]["breed-guide"] == 1  # the Ragdoll advert is not a breed guide


def test_without_the_breeds_pages_another_species_is_never_a_key_page(tmp_path):
    x = P4H
    d = classify(tmp_path, [f"{x}/sale/kittens/", f"{x}/sale/puppies/", f"{x}/cat-care/", f"{x}/rabbit-care/",
                            f"{x}/sale/kittens/london/", f"{x}/horses-for-sale/", f"{x}/guinea-pigs-for-sale/",
                            f"{x}/fish-care-guide/", f"{x}/hamster-guide/", f"{x}/sale/puppies/cocker-spaniel/leeds/"])
    assert d["key_pages"] == {
        "listing": f"{x}/sale/puppies/",     # another dog page may stay in the fallback
        "price-or-faq": None,
        "guide": None,                       # every care and breed guide names another species: nothing
        "city": f"{x}/sale/puppies/cocker-spaniel/leeds/",
        "about": None,
    }
    d = classify(tmp_path, [f"{x}/sale/kittens/", f"{x}/cats/london/"])
    assert d["key_pages"]["listing"] is None and d["key_pages"]["city"] is None


@pytest.mark.parametrize("path", ["/staffies-for-sale/", "/sbt-puppies/", "/blue-staffords-for-sale/", "/staffordshire-puppies/",
                                  "/sale/puppies/staffordshire-bull-terrier/", "/staffys-available/"])
def test_a_breed_path_is_picked_before_a_shorter_page(tmp_path, path):
    x = "https://x.co.uk"
    assert classify(tmp_path, [f"{x}/puppies/", f"{x}{path}"])["key_pages"]["listing"] == f"{x}{path}"


def test_stafford_the_town_is_not_the_breed(tmp_path):
    x = "https://x.co.uk"
    d = classify(tmp_path, [f"{x}/puppies/", f"{x}/puppies-stafford/", f"{x}/staff-puppies/"])
    assert d["key_pages"]["listing"] == f"{x}/puppies/"


def test_a_breeder_site_with_no_breed_words_picks_as_before(tmp_path):
    # no breed word and no other species: the fallback is today's rule, unchanged
    x = "https://www.example-kennels.co.uk"
    d = classify(tmp_path, [f"{x}/", f"{x}/puppies/", f"{x}/available-litters/", f"{x}/puppies/rex/", f"{x}/prices/",
                            f"{x}/faq/", f"{x}/aftercare/", f"{x}/breed-guide/", f"{x}/leeds/", f"{x}/york/",
                            f"{x}/about-us/", f"{x}/about/", f"{x}/post/our-new-litter"])
    assert d["key_pages"] == {
        "listing": f"{x}/puppies/",
        "price-or-faq": f"{x}/prices/",  # (today's picks, verified on the classifier before the breed rule)
        "guide": f"{x}/aftercare/",
        "city": f"{x}/york/",
        "about": f"{x}/about/",
    }


def test_the_about_page_is_the_sites_own_not_a_breed_page(tmp_path):
    # trojanstaffuk's map: its about page is /about-1, not the breed-information page typed about
    t = "https://www.trojanstaffuk.com"
    d = classify(tmp_path, [f"{t}/about-1", f"{t}/about-the-staffordshire-bull-terrier", f"{t}/staffy-puppies"])
    assert d["key_pages"]["about"] == f"{t}/about-1"
    assert d["key_pages"]["listing"] == f"{t}/staffy-puppies"


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


def measure(tmp_path, page, name="home.html", url=None):
    """intel's homepage measures, run in a scratch root on `page` (raw HTML or markdown); `url` is
    the homepage's own URL (HOME_URL), when given."""
    (tmp_path / "tests/py").mkdir(parents=True, exist_ok=True)
    shutil.copy(REPO / "tests/py/test_no_third_party_contacts.py", tmp_path / "tests/py")
    (tmp_path / name).write_text(page, encoding="utf-8")
    found = HOMEPAGE.findall(AGENT.read_text(encoding="utf-8"))
    assert len(found) == 1, f"expected one homepage-measures block, found {len(found)}"
    run = subprocess.run([sys.executable, "-", name, *([url] if url else [])], input=found[0], cwd=tmp_path,
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    LAST_STDERR[0] = run.stderr
    return json.loads(run.stdout)


LAST_STDERR = [""]  # the homepage measures' last stderr


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


def test_one_image_however_its_source_is_written(tmp_path):
    # scheme, the page's own host and the query are not part of an image's identity
    page = ('<html><body><img src="/a.jpg" alt="Blue Staffy puppy Rex at eight weeks"><img src="https://site.co.uk/a.jpg">'
            '<img src="/a.jpg?w=300"><img src="//site.co.uk/a.jpg#top"><img src="http://SITE.co.uk/a.jpg">'
            '<img src="a.jpg"><img src="https://cdn.other.com/a.jpg"></body></html>')
    d = measure(tmp_path, page, url="https://site.co.uk/")
    assert d["homepage_images"] == 2          # site.co.uk/a.jpg (the first alt kept) and the CDN's own copy
    assert (d["alt_missing"], d["alt_text"]) == (1, "missing")
    d = measure(tmp_path, '<html><body><img src="/a.jpg"><img src="/a.jpg?w=300"><img src="/a.jpg?w=600"></body></html>')
    assert d["homepage_images"] == 1          # no HOME_URL: a query still never makes a second image


def test_an_image_behind_a_proxy_keeps_its_query(tmp_path):
    # /images?url=… and Next.js /_next/image?url=… name the real image in the query: never one image
    page = '<html><body><img src="/images?url=a.jpg&w=1"><img src="/_next/image?url=%2Fb.jpg&w=640"></body></html>'
    assert measure(tmp_path, page.replace("</body>", '<img src="/images?url=b.jpg&w=1"></body>'),
                   url="https://site.co.uk/")["homepage_images"] == 3
    page = '<html><body><img src="/a.jpg?w=300"><img src="/a.jpg"><img src="https://www.site.co.uk/a.jpg"></body></html>'
    d = measure(tmp_path, page, url="https://site.co.uk/")
    assert d["homepage_images"] == 1          # an image file: the query dropped, www. folded
    assert d["home_url"] == "https://site.co.uk/"


def test_measures_without_home_url_say_so(tmp_path):
    d = measure(tmp_path, '<html><body><img src="/a.jpg"></body></html>')
    assert d["home_url"] is None              # a relative source could not be put on the site's host
    assert "HOME_URL" in LAST_STDERR[0]


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


def test_scripts_and_comments_hold_no_homepage_images_or_contact_links(tmp_path):
    page = ('<!DOCTYPE html><html><body><script type="text/html"><img src="{{x}}" alt=""></script>'
            '<!-- <img src="/c.jpg"> <a href="tel:+447700900123">Ring</a> <a href="mailto:a@example.co.uk">x</a> -->'
            '<img src="/d.jpg" alt="Two blue puppies asleep in the garden"></body></html>')
    d = measure(tmp_path, page)
    assert (d["homepage_images"], d["alt_missing"], d["alt_text"]) == (1, 0, "descriptive")
    assert (d["phone_shown"], d["email_shown"]) == (False, False)


def test_a_page_with_no_images_has_no_alt_class(tmp_path):
    d = measure(tmp_path, "<!doctype html><html><body><p>Puppies soon.</p></body></html>")
    assert (d["homepage_images"], d["alt_missing"], d["alt_text"]) == (0, 0, None)


def test_markdown_with_inline_html_is_still_markdown(tmp_path):
    d = measure(tmp_path, '# Home\n\n<div class="hero"><img src="/rex.jpg" alt="Rex"></div>\n', "home.md")
    assert d["contact_source"] == "markdown-only" and d["homepage_images"]["status"] == "NOT FETCHED"


PHONE = {"innerWidth": 375, "clientWidth": 375, "scrollWidth": 375, "screenWidth": 375, "maxTouchPoints": 5,
         "ua": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 Mobile Safari/537.36"}


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
@pytest.mark.parametrize("change,ok", [
    ({}, True),                                                    # fits the phone
    ({"innerWidth": 908, "scrollWidth": 908}, False),              # a 900px box: the phone zooms out to show it
    ({"innerWidth": 980, "clientWidth": 980, "scrollWidth": 980}, False),  # no device-width viewport
    ({"screenWidth": 1440, "maxTouchPoints": 0,
      "ua": "Mozilla/5.0 (Macintosh) Chrome/140"}, None),          # a desktop browser resized: NOT FETCHED
    ({"ua": "Mozilla/5.0 (Macintosh) Chrome/140"}, None),          # a phone size without a phone's user agent
    ({"maxTouchPoints": 0}, None),                                 # nor without touch
])
def test_the_mobile_check_measures_what_a_phone_sees_and_proves_emulation(change, ok):
    found = MOBILE.findall(AGENT.read_text(encoding="utf-8"))
    assert len(found) == 1, f"expected one mobile-check block, found {len(found)}"
    v = {**PHONE, **change}
    stub = (f"const window = {{innerWidth: {v['innerWidth']}}};"
            f"const document = {{documentElement: {{clientWidth: {v['clientWidth']}, scrollWidth: {v['scrollWidth']}}}}};"
            f"const screen = {{width: {v['screenWidth']}}};"
            f"const navigator = {{maxTouchPoints: {v['maxTouchPoints']}, userAgent: {json.dumps(v['ua'])}}};"
            f"console.log(JSON.stringify(({found[0]})()));")
    run = subprocess.run(["node", "-e", stub], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    d = json.loads(run.stdout)
    assert d["mobile_layout_ok"] is ok
    assert {"innerWidth", "clientWidth", "scrollWidth", "screenWidth", "maxTouchPoints", "mobileUA"} <= set(d)
