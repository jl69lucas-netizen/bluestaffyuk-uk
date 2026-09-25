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
    ("/dog-breeds/manchester-terrier/", "breed-guide"),    # a city word before -terrier is a breed (pdsa), not a city
    ("/manchester-terriers/", None),
    ("/aberdeen-terrier/", None),                          # the Scottish Terrier's old name
    ("/staffy-puppies-manchester/", "city"),               # the city itself still is one
    ("/manchester-terrier-rescue-manchester/", "city"),
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
    f"{P4H}/classifieds/q7zz1-staffy-pups-leeds",           # pets4homes' real advert shape: a short id prefix,
    f"{P4H}/classifieds/k2x9qab-blue-staffy-puppies-wigan",  # shallower than the Staffy hubs
]


def test_a_marketplaces_key_pages_are_the_breeds_pages(tmp_path):
    d = classify(tmp_path, MARKETPLACE)
    assert d["key_pages"] == {
        "listing": f"{P4H}/sale/puppies/staffordshire-bull-terrier/",  # the breed hub: never /sale/kittens/, and
        # never the shallower Staffy advert, which is the listing's last resort
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


@pytest.mark.parametrize("path", ["/staffies-for-sale/", "/sbt-puppies/", "/blue-staffords-for-sale/",
                                  "/staffordshire-bull-terrier-puppies/", "/sale/puppies/staffordshire-bull-terrier/",
                                  "/staffys-available/", "/puppies/staffordshire_bull_terrier/",
                                  "/puppies/blue+staffy/", "/puppies/blue%20staffy/",  # + and %20 split breed words
                                  "/puppies/staffordshire%20bull%20terrier/", "/puppies/blue%20staffordshire/"])
def test_a_breed_path_is_picked_before_a_shorter_page(tmp_path, path):
    x = "https://x.co.uk"
    assert classify(tmp_path, [f"{x}/puppies/", f"{x}{path}"])["key_pages"]["listing"] == f"{x}{path}"


@pytest.mark.parametrize("path", ["/dogs-for-sale/staffordshire/",                  # the county
                                  "/american-staffordshire-terrier-puppies/",        # an AmStaff
                                  "/american-staffordshire-bull-terrier-puppies/",
                                  "/english-bull-terrier-puppies/", "/miniature-bull-terrier-puppies/",
                                  "/american-pit-bull-terrier-puppies/", "/bull-terrier-puppies/",
                                  "/puppies/american%20staffordshire%20bull%20terrier/"])
def test_the_county_and_the_breeds_cousins_are_not_the_breed(tmp_path, path):
    x = "https://x.co.uk"
    assert classify(tmp_path, [f"{x}/puppies/", f"{x}{path}"])["key_pages"]["listing"] == f"{x}/puppies/"


def test_the_staffy_hub_beats_a_cousins_hub_at_the_same_depth(tmp_path):
    x = "https://x.co.uk"
    d = classify(tmp_path, [f"{x}/dogs/bull-terrier/for-sale/", f"{x}/dogs/staffordshire-bull-terrier/for-sale/"])
    assert d["key_pages"]["listing"] == f"{x}/dogs/staffordshire-bull-terrier/for-sale/"
    d = classify(tmp_path, [f"{x}/american-pit-bull-terrier-puppies/", f"{x}/staffordshire-bull-terrier-puppies/"])
    assert d["key_pages"]["listing"] == f"{x}/staffordshire-bull-terrier-puppies/"


def test_an_advert_is_never_a_key_page_but_the_listings_last_resort(tmp_path):
    x = "https://x.co.uk"
    # gumtree: an id segment; typed breed guide by 'breed' (page_types unchanged), never the guide pick
    d = classify(tmp_path, [f"{x}/p/dogs/staffy-breed/1498765433", f"{x}/dog-breeds/"])
    assert d["page_types"] == {"breed-guide": 2} and d["key_pages"]["guide"] == f"{x}/dog-breeds/"
    assert classify(tmp_path, [f"{x}/p/dogs/staffy-breed/1498765433"])["key_pages"]["guide"] is None
    # preloved: an id segment mid-path, .html; the breed hub is the listing however deep
    hub = f"{x}/classifieds/pets/dogs/staffordshire-bull-terrier/for-sale/uk"
    d = classify(tmp_path, [f"{x}/adverts/show/123456789/blue-staffy-puppies.html", hub])
    assert d["key_pages"]["listing"] == hub
    # freeads: an id joined to the slug before .html; alone, the advert is the listing's last resort
    ad = f"{x}/dogs/staffy-puppies-for-sale-12345678.html"
    assert classify(tmp_path, [ad, f"{x}/dogs/staffordshire-bull-terrier/for-sale/"])["key_pages"]["listing"] \
        == f"{x}/dogs/staffordshire-bull-terrier/for-sale/"
    assert classify(tmp_path, [ad])["key_pages"]["listing"] == ad
    # an advert ending in a town is a city page by type, never the city pick
    leeds = f"{x}/dogs/staffordshire-bull-terrier/uk/england/leeds/"
    d = classify(tmp_path, [f"{x}/ad/blue-staffy-pups-leeds-1234567", leeds])
    assert d["page_types"] == {"city": 2} and d["key_pages"]["city"] == leeds
    assert classify(tmp_path, [f"{x}/ad/blue-staffy-pups-leeds-1234567"])["key_pages"]["city"] is None
    # 'temperament' in an advert: typed breed guide, never the guide pick
    d = classify(tmp_path, [f"{x}/ad/staffy-pups-lovely-temperament-1234567"])
    assert d["page_types"] == {"breed-guide": 1} and d["key_pages"]["guide"] is None
    # 'price' in an advert: typed price, never the price pick
    d = classify(tmp_path, [f"{x}/ad/reduced-price-staffy-pups-7654321", f"{x}/prices/"])
    assert d["page_types"] == {"price": 2} and d["key_pages"]["price-or-faq"] == f"{x}/prices/"
    # a help-centre page with a numeric id is not an advert
    assert classify(tmp_path, [f"{x}/help/puppy-faq-1234567"])["key_pages"]["price-or-faq"] == f"{x}/help/puppy-faq-1234567"


@pytest.mark.parametrize("advert,hub,slot", [
    ("/classifieds/q7zz1-staffy-pups-leeds", "/sale/puppies/staffordshire-bull-terrier/leeds/", "city"),
    ("/classifieds/k2x9qab-blue-staffy-puppies-wigan", "/sale/puppies/staffordshire-bull-terrier", "listing"),
    ("/classifieds/c-aa6p71l-staffy-puppies", "/sale/puppies/staffordshire-bull-terrier", "listing"),  # no id rule: the folder
    ("/ad/blue-staffy-pups-available", "/dogs/staffordshire-bull-terrier/for-sale/", "listing"),
    ("/adverts/staffy-litter.html", "/dogs/staffordshire-bull-terrier/for-sale/", "listing"),
    ("/staffy-pups/q7zz1-staffy-pups-leeds", "/sale/puppies/staffordshire-bull-terrier/leeds/", "city"),  # an id prefix anywhere
])
def test_an_advert_with_an_id_prefix_or_in_an_advert_folder_is_an_advert(tmp_path, advert, hub, slot):
    x = P4H
    assert classify(tmp_path, [f"{x}{advert}", f"{x}{hub}"])["key_pages"][slot] == f"{x}{hub}"


@pytest.mark.parametrize("path,slot,other", [
    ("/about-us/", "about", None),
    ("/staffy-puppies/", "listing", "/puppies/staffy/litters/"),      # an advert would rank after the deeper page
    ("/2024-guide/", "guide", None),                                  # a year is not an id: under 5 characters
    ("/classifieds/staffordshire-bull-terrier-puppies/", "listing", "/sale/puppies/staffordshire-bull-terrier/"),  # a breed hub
    ("/classifieds/leeds/", "city", "/sale/puppies/leeds/"),                  # a city hub, before a deeper city page
    ("/support/solutions/q7zz1-puppy-faq", "price-or-faq", None),     # help-centre pages are never adverts
    ("/classifieds/staffy-puppies-uk", "listing", "/sale/puppies/staffordshire-bull-terrier/"),  # uk, in and near are
    ("/classifieds/dogs-for-sale-in-leeds", "city", "/sale/puppies/leeds/"),                      # hub words
    ("/classifieds/puppies-near-york", "city", "/sale/puppies/york/"),
    ("/covid19-puppy-buying-guide/", "guide", None),                  # an id prefix interleaves letters and digits:
    ("/staffy2-care-guide/", "guide", None),                          # a word with a number on the end is not one,
    ("/202425-staffy-prices/", "price-or-faq", None),                 # nor digits alone
])
def test_ordinary_pages_and_hubs_are_not_adverts(tmp_path, path, slot, other):
    x = "https://x.co.uk"
    urls = [f"{x}{path}"] + ([f"{x}{other}"] if other else [])
    assert classify(tmp_path, urls)["key_pages"][slot] == f"{x}{path}"


def test_a_multi_species_site_falls_back_to_a_dog_page_first(tmp_path):
    x = P4H
    d = classify(tmp_path, [f"{x}/classifieds/gz4krku3k-bombay-london", f"{x}/sale/puppies/cocker-spaniel/leeds/",
                            f"{x}/sale/kittens/"])
    assert d["key_pages"]["city"] == f"{x}/sale/puppies/cocker-spaniel/leeds/"  # not the shallower Bombay advert
    # a site naming no other species keeps today's order: the shortest page, dog word or not
    y = "https://www.example-kennels.co.uk"
    d = classify(tmp_path, [f"{y}/litters/", f"{y}/puppies/available/", f"{y}/leeds/", f"{y}/puppies/leeds/"])
    assert (d["key_pages"]["listing"], d["key_pages"]["city"]) == (f"{y}/litters/", f"{y}/leeds/")


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


def test_the_about_pick_is_an_about_segment_not_a_slug_that_mentions_about(tmp_path):
    # rspca: a privacy notice was picked as the about page by the word 'about' mid-slug (it 404ed: a wasted credit)
    x = "https://www.rspca.org.uk"
    notice = f"{x}/privacy-notice-about-your-data"
    d = classify(tmp_path, [notice])
    assert d["page_types"] == {"about": 1} and d["key_pages"]["about"] is None  # typed about as before; never the pick
    d = classify(tmp_path, [notice, f"{x}/who-we-are/about/"])
    assert d["key_pages"]["about"] == f"{x}/who-we-are/about/"   # a whole about segment, however deep
    for page in ("/aboutus/", "/our-story/", "/about-us/", "/about-us.html", "/about-our-charity", "/about-1"):
        assert classify(tmp_path, [notice, f"{x}{page}"])["key_pages"]["about"] == f"{x}{page}"
    # the about word must be the last segment (or start it): rspca's pages under an aboutus folder are not its about page
    d = classify(tmp_path, [f"{x}/utilities/aboutus/stayinformed", f"{x}/local/aboutus/-/rspca/solent-branch-cio",
                            f"{x}/about-us/team/"])
    assert d["page_types"] == {"about": 3} and d["key_pages"]["about"] is None


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


# --- the map list: one search map when the first map misses the breed; the homepage's own breed links ---
MAPLIST = re.compile(r'python3 - "\$MAP_RAW"[^\n]*<<\'EOF\'\n(.*?)\nEOF\n', re.S)
DT = "https://www.dogstrust.org.uk"


def map_list(tmp_path, first, root="dogstrust.org.uk", search=None, home=None, refused=False):
    """intel's map-list script on a first map (and a search map, and a homepage): its JSON, and the list it wrote."""
    found = MAPLIST.findall(AGENT.read_text(encoding="utf-8"))
    assert len(found) == 1, f"expected one map-list block, found {len(found)}"
    (tmp_path / "first.json").write_text(json.dumps(first), encoding="utf-8")
    args = [str(tmp_path / "first.json"), root]
    if home is not None:
        (tmp_path / "home.html").write_text(home, encoding="utf-8")
        args += ["--home", str(tmp_path / "home.html"), DT + "/"]
    if search is not None:
        (tmp_path / "search.json").write_text(json.dumps(search), encoding="utf-8")
        args += ["--search", str(tmp_path / "search.json")]
    args += ["--out", str(tmp_path / "list.json")]
    run = subprocess.run([sys.executable, "-", *args], input=found[0], cwd=REPO, capture_output=True, text=True)
    if refused:
        return run
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout), json.loads((tmp_path / "list.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("first,want", [
    ([f"{DT}/page-{i}/" for i in range(500)], True),                                     # at the cap
    ([f"{DT}/page-{i}/" for i in range(499)] + [f"{DT}/dog-breeds/staffordshire-bull-terrier/"], True),  # at the cap
    ([f"{DT}/page-{i}/" for i in range(40)] + [f"{DT}/staffy-rescue/"], False),         # under it, with a breed page
    ([f"{DT}/page-{i}/" for i in range(40)], True),                                      # under it, no breed page
    ([f"{DT}/page-{i}/" for i in range(40)] + [f"{DT}/dogs/stafford/"], True),           # the town is not the breed
])
def test_a_map_at_the_cap_or_without_the_breed_asks_for_one_search_map(tmp_path, first, want):
    d, _ = map_list(tmp_path, first)
    assert d["search_map"] is want and d["url_count"] == len(first)
    assert d["search_term"] == ("staffordshire bull terrier" if want else None)  # never the county alone


def test_the_search_map_is_merged_once_per_page_and_only_from_the_site(tmp_path):
    first = [f"{DT}/", f"{DT}/rehoming/dogs/", f"{DT}/about-us/"]
    search = [f"https://dogstrust.org.uk/rehoming/dogs", f"{DT}/about-us/?utm_source=x",   # already there
              f"{DT}/dog-breeds/staffordshire-bull-terrier/", f"{DT}/dog-breeds/staffordshire-bull-terrier",
              "https://shop.dogstrust.org.uk/staffy-toys/",                                  # a subdomain: the same site
              "https://www.example-breeder.co.uk/staffy-puppies/"]                          # another site: never
    d, merged = map_list(tmp_path, first, search=search)
    assert merged == first + [f"{DT}/dog-breeds/staffordshire-bull-terrier/", "https://shop.dogstrust.org.uk/staffy-toys/"]
    assert (d["search_added"], d["search_breed_urls"], d["map_list"]) == (2, 2, 5)


DT_HOME = f"""<html><body><nav>
<a href="/dog-breeds/staffordshire-bull-terrier">Staffies</a>
<a href='/rehoming/dogs'>Rehome a dog</a>
<a href="{DT}/dog-breeds/staffordshire-bull-terrier/#care">Staffy care</a>
<a href="{DT}/contact-us/staffy-enquiry">Ask about a Staffy</a>
<a href="https://www.example-breeder.co.uk/staffy-puppies/">A breeder</a>
<a href="mailto:staffy@dogstrust.org.uk">Email</a><a href="tel:+440000000000">Call</a>
<a href="">Empty</a>
</nav><script>var t = '<a href="/staffy-in-a-script/">';</script><!-- <a href="/staffy-in-a-comment/"> -->
<p>Staffordshire Bull Terriers need homes.</p></body></html>"""


def test_the_homepages_own_breed_links_join_the_list_at_no_cost(tmp_path):
    # Dogs Trust: the Staffy breed page is in the homepage menu but not in the map
    first = [f"{DT}/", f"{DT}/rehoming/dogs/"]
    d, merged = map_list(tmp_path, first, home=DT_HOME)
    assert merged == first + [f"{DT}/dog-breeds/staffordshire-bull-terrier"]  # same site, a breed path, once
    assert d["home_added"] == 1                     # never another site, a contact page, mailto/tel, a script or a comment
    d, merged = map_list(tmp_path, first + [f"{DT}/dog-breeds/staffordshire-bull-terrier/"], home=DT_HOME)
    assert d["home_added"] == 0 and len(merged) == 3  # already in the map: one page however written


def test_the_search_term_is_the_sites_own_word_for_the_breed(tmp_path):
    first = [f"{DT}/page-{i}/" for i in range(5)]
    assert map_list(tmp_path, first, home=DT_HOME)[0]["search_term"] == "staffordshire bull terrier"
    staffy_only = "<html><body><h1>Blue Staffy puppies</h1><a href='/puppies/'>Puppies</a></body></html>"
    assert map_list(tmp_path, first, home=staffy_only)[0]["search_term"] == "staffy"


def test_the_map_list_uses_the_classifiers_breed_test_line_for_line():
    text = AGENT.read_text(encoding="utf-8")
    lines = lambda block: [ln for ln in block.splitlines() if ln.startswith(("S, J = ", "BREED = "))]
    ours, theirs = lines(MAPLIST.findall(text)[0]), lines(CLASSIFIER.findall(text)[0])
    assert len(theirs) == 2 and ours == theirs, "the breed test differs: change it in the classifier, then copy it"


def test_the_ceiling_is_two_maps_and_six_scrapes():
    text = AGENT.read_text(encoding="utf-8")
    assert "(8 × N)" in text and "7 × N" not in text
    gap = (REPO / ".claude/agents/bsuk-competitive-keyword-gap-agent.md").read_text(encoding="utf-8")
    assert "8 × N" in gap and "7 × N" not in gap and "Ceiling 7" not in gap
    assert "without `--home`" in gap  # its homepage scrape is markdown only: no homepage links


# --- another host never outranks the site's own; one search map, enforced; files are not pages ---
GT = "https://www.gumtree.com"
FORUM, BLOG = "https://forum.gumtree.com/threads/staffy-puppies.12345/", "https://blog.gumtree.com/staffy-puppy-price-guide/"


@pytest.mark.parametrize("flags", [(), (f"--home={GT}/",)])
def test_a_subdomains_page_counts_but_never_outranks_the_sites_own(tmp_path, flags):
    urls = [f"{GT}/", f"{GT}/dogs-for-sale/staffordshire-bull-terrier", f"{GT}/pricing/", FORUM, BLOG]
    d = classify(tmp_path, urls, *flags)
    assert d["page_types"] == {"listing": 2, "price": 2}          # subdomains stay in the counts
    assert d["key_pages"]["listing"] == f"{GT}/dogs-for-sale/staffordshire-bull-terrier"
    assert d["key_pages"]["price-or-faq"] == f"{GT}/pricing/"    # the site's own page, breed or not
    d = classify(tmp_path, [f"{GT}/", f"{GT}/cars/", BLOG], *flags)
    assert d["key_pages"]["price-or-faq"] == BLOG                 # alone, another host's page is still a pick


def test_a_forum_threads_dot_id_is_an_advert_id(tmp_path):
    x = "https://www.x.co.uk"
    d = classify(tmp_path, [f"{x}/threads/staffy-puppies.12345/", f"{x}/dogs/staffordshire-bull-terrier/for-sale/"])
    assert d["key_pages"]["listing"] == f"{x}/dogs/staffordshire-bull-terrier/for-sale/"


def test_the_classifier_counts_the_search_maps_adverts(tmp_path):
    x = "https://www.x.co.uk"
    (tmp_path / "search.json").write_text(json.dumps([
        f"{x}/dogs/staffordshire-bull-terrier/for-sale/", f"{x}/ad/blue-staffy-pups-leeds-1234567",
        f"{x}/classifieds/q7zz1-staffy-pups-leeds", f"{x}/threads/staffy-puppies.12345/"]), encoding="utf-8")
    d = classify(tmp_path, [f"{x}/", f"{x}/puppies/"], "--search=search.json")
    assert d["search_adverts"] == 3
    assert "search_adverts" not in classify(tmp_path, [f"{x}/", f"{x}/puppies/"])


def test_a_search_map_the_script_did_not_ask_for_is_refused(tmp_path):
    first = [f"{DT}/page-{i}/" for i in range(40)] + [f"{DT}/staffy-rescue/"]   # under the cap, with a breed page
    run = map_list(tmp_path, first, search=[f"{DT}/dog-breeds/staffordshire-bull-terrier/"], refused=True)
    assert run.returncode != 0 and "search map" in run.stderr


def test_homepage_links_to_files_are_not_pages(tmp_path):
    home = """<html><body>
<a href="/images/staffy-puppy.jpg">x</a><a href="/docs/staffy-care.pdf">x</a><a href="/css/staffy.css">x</a>
<a href="/js/staffy.js">x</a><a href="/media/staffy-video.mp4">x</a><a href="/feeds/staffy.xml">x</a>
<a href="/staffy-rescue.html">x</a><a href="/staffy-puppies.php">x</a><a href="/dog-breeds/staffordshire-bull-terrier">x</a>
</body></html>"""
    d, merged = map_list(tmp_path, [f"{DT}/"], home=home)
    assert merged[1:] == [f"{DT}/staffy-rescue.html", f"{DT}/staffy-puppies.php", f"{DT}/dog-breeds/staffordshire-bull-terrier"]
    assert d["home_added"] == 3


def test_a_homepage_link_differing_only_in_case_is_the_same_page(tmp_path):
    home = '<html><body><a href="/dog-breeds/staffordshire-bull-terrier">x</a></body></html>'
    d, merged = map_list(tmp_path, [f"{DT}/", f"{DT}/Dog-Breeds/Staffordshire-Bull-Terrier/"], home=home)
    assert (d["home_added"], d["map_list"]) == (0, 2)
