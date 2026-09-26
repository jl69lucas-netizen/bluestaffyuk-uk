# tests/py/test_competitor_metrics.py — query_augment.py keeps competitor page metrics
# (parity build Task 17; audit rows 6.7, 6.15, 6.17, 9.3). Every page is a saved fixture under
# tests/py/fixtures/competitor-pages/; nothing here fetches.
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import query_augment as Q  # noqa: E402

SCRIPT = ROOT / "scripts" / "query_augment.py"
FIX = ROOT / "tests" / "py" / "fixtures" / "competitor-pages"
PAGE = (FIX / "breeder-sections.html").read_text(encoding="utf-8")
SLUG = "blue-staffy-puppies-testcity"

EXPECTED = {
    "title": "Blue Staffy Puppies Manchester | Example Kennels",
    "meta_description": "Blue staffy puppies in Manchester, raised at home.",
    "word_count": 59,
    "intro_words": 7,
    "sections": [
        {"h2": "Our Puppies", "words": 16, "h3_count": 2, "h3": ["Current Litter"]},
        {"h2": "Health Testing", "words": 6, "h3_count": 1, "h3": ["Hips"]},
        {"h2": "Delivery", "words": 5, "h3_count": 0, "h3": []},
    ],
    "h3_count": 3,
    "images": 2,
    "videos": 2,
    "tables": 1,
    "schema_types": ["FAQPage", "ItemPage", "Organization", "Question", "WebPage"],
    "scope": "main",
    "grid_share": 11,
    "section_share": 71,
    "listing": None,
    "scrubbed": 1,
}


def test_page_metrics_reads_the_saved_page():
    assert Q.page_metrics(PAGE) == EXPECTED


def test_metrics_sections_are_exactly_the_content_h2s_in_order():
    m = Q.page_metrics(PAGE)
    assert [s["h2"] for s in m["sections"]] == Q.extract_h2s(PAGE)


def test_a_contact_detail_never_reaches_the_metrics():
    text = json.dumps(Q.page_metrics(PAGE))
    assert "07700" not in text and "900123" not in text


def test_a_page_with_no_head_and_no_h2_measures_zero_sections():
    m = Q.page_metrics("<main><p>Just five words of prose.</p><img src=x></main>")
    assert m["title"] is None and m["meta_description"] is None
    assert m["word_count"] == 5 and m["intro_words"] == 5 and m["sections"] == []
    assert m["images"] == 1 and m["schema_types"] == []


def test_cli_extract_h2_prints_the_metrics_beside_the_h2s(tmp_path):
    f = tmp_path / "1.html"
    f.write_text(PAGE, encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPT), "--extract-h2", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["h2"] == ["Our Puppies", "Health Testing", "Delivery"]
    assert out["h2_all"] == 7 and out["blocked"] is False
    assert out["metrics"] == EXPECTED


def _repo(tmp_path, pages, cached):
    """A repo root with raw/<slug>/competitors.json and cache/<slug>/<n>.html files."""
    raw = tmp_path / "data/queries/raw" / SLUG
    raw.mkdir(parents=True)
    (raw / "competitors.json").write_text(json.dumps(
        {"status": "ok", "fetched": "2026-09-26", "pages": pages}), encoding="utf-8")
    cache = tmp_path / "data/queries/cache" / SLUG
    cache.mkdir(parents=True)
    for n, html in cached.items():
        (cache / f"{n}.html").write_text(html, encoding="utf-8")
    return tmp_path


def _record(url, html, g):
    rep = Q.page_report(html)
    return {"url": url, "google_pos": g, "bing_pos": None, "h2": rep["h2"],
            "h2_all": rep["h2_all"], "blocked": rep["blocked"]}


def _metrics_cli(root):
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root),
                           "--competitor-metrics", SLUG], capture_output=True, text=True)


def test_competitor_metrics_backfills_every_cached_page(tmp_path):
    other = "<main><h2>Only</h2><p>three words here</p></main>"
    root = _repo(tmp_path, [_record("https://a.example/", PAGE, 1),
                            _record("https://b.example/", other, 2)], {1: PAGE, 2: other})
    r = _metrics_cli(root)
    assert r.returncode == 0, r.stderr
    d = json.loads((root / f"data/queries/raw/{SLUG}/competitors.json").read_text())
    assert d["pages"][0]["metrics"] == EXPECTED
    assert d["pages"][1]["metrics"]["sections"] == [
        {"h2": "Only", "words": 3, "h3_count": 0, "h3": []}]
    assert "2 of 2 pages" in r.stdout


def test_competitor_metrics_skips_a_page_whose_cache_file_is_missing(tmp_path):
    root = _repo(tmp_path, [_record("https://a.example/", PAGE, 1),
                            _record("https://b.example/", PAGE, 2)], {1: PAGE})
    r = _metrics_cli(root)
    assert r.returncode == 0, r.stderr
    d = json.loads((root / f"data/queries/raw/{SLUG}/competitors.json").read_text())
    assert "metrics" in d["pages"][0] and "metrics" not in d["pages"][1]
    assert "1 of 2 pages" in r.stdout and "https://b.example/" in r.stdout


def test_competitor_metrics_drops_stale_metrics_when_the_cache_file_is_gone(tmp_path):
    page = dict(_record("https://b.example/", PAGE, 1), metrics=EXPECTED)
    root = _repo(tmp_path, [page], {})
    r = _metrics_cli(root)
    assert r.returncode == 0, r.stderr
    d = json.loads((root / f"data/queries/raw/{SLUG}/competitors.json").read_text())
    assert "metrics" not in d["pages"][0]
    assert "dropped stale metrics" in r.stdout and "https://b.example/" in r.stdout


def test_competitor_metrics_refuses_a_cache_file_that_is_not_the_recorded_page(tmp_path):
    other = "<main><h2>Something Else</h2></main>"
    root = _repo(tmp_path, [_record("https://a.example/", PAGE, 1)], {1: other})
    before = (root / f"data/queries/raw/{SLUG}/competitors.json").read_text()
    r = _metrics_cli(root)
    assert r.returncode == Q.EXIT_BAD_INPUT
    assert "1.html" in r.stderr and "does not match" in r.stderr
    assert (root / f"data/queries/raw/{SLUG}/competitors.json").read_text() == before


def test_competitor_metrics_without_a_competitors_file_is_bad_input(tmp_path):
    r = _metrics_cli(tmp_path)
    assert r.returncode == Q.EXIT_BAD_INPUT
    assert "competitors.json" in r.stderr


@pytest.mark.parametrize("bad", [
    "not an object",
    {"word_count": -1},
    {"word_count": 5, "sections": [{"h2": "x", "words": "many", "h3": []}]},
])
def test_load_competitors_refuses_malformed_metrics(tmp_path, bad):
    page = _record("https://a.example/", PAGE, 1)
    page["metrics"] = bad
    root = _repo(tmp_path, [page], {})
    with pytest.raises(Q.BadInput, match="metrics"):
        Q.load_competitors(SLUG, root)


def test_load_competitors_accepts_a_file_with_no_metrics(tmp_path):
    root = _repo(tmp_path, [_record("https://a.example/", PAGE, 1)], {})
    assert Q.load_competitors(SLUG, root)["pages"][0]["url"] == "https://a.example/"


def test_word_target_is_the_median_of_the_measured_pages():
    pages = [dict(_record(f"https://site{i}.example/", PAGE, i + 1),
                  metrics=dict(EXPECTED, word_count=n)) for i, n in enumerate((100, 300, 400))]
    pages.append(dict(_record("https://blocked.example/", PAGE, 9), blocked=True,
                      metrics=dict(EXPECTED, word_count=5000)))
    wt = Q.word_target(pages)
    assert (wt["median"], wt["from"], wt["of"]) == (300, 3, 4)
    assert wt["used"] == ["https://site0.example/", "https://site1.example/",
                          "https://site2.example/"]
    assert wt["excluded"] == [{"url": "https://blocked.example/",
                               "reason": "blocked (a bot challenge)"}]


def test_word_target_rounds_an_even_median_half_up():
    pages = [dict(_record(f"https://s{i}.example/", PAGE, i + 1),
                  metrics=dict(EXPECTED, word_count=n)) for i, n in enumerate((101, 102))]
    assert Q.word_target(pages)["median"] == 102   # 101.5 -> 102, never banker's 102/101


def _measured(url, g, words, **over):
    return dict(_record(url, PAGE, g), metrics={**EXPECTED, "word_count": words, **over})


def test_word_target_counts_each_site_once_keeping_the_best_ranked_url():
    pages = [_measured("https://www.a.co.uk/x", 3, 400), _measured("https://a.co.uk/y", 1, 500),
             _measured("https://shop.a.co.uk/z", 2, 450), _measured("https://b.example/", 4, 420)]
    wt = Q.word_target(pages)
    assert wt["used"] == ["https://a.co.uk/y", "https://b.example/"]
    assert {e["url"] for e in wt["excluded"]} == {"https://www.a.co.uk/x", "https://shop.a.co.uk/z"}
    assert all(e["reason"] == "same site as https://a.co.uk/y" for e in wt["excluded"])
    assert wt["median"] == 460


@pytest.mark.parametrize("over,reason", [
    ({"word_count": 0}, "no words measured"),
    ({"sections": []}, "no content H2"),
    ({"schema_types": ["ItemList", "WebPage"], "grid_share": 45},
     "listing: JSON-LD ItemList, card grid holds 45% of the prose"),
    ({"schema_types": ["SearchResultsPage"], "grid_share": 41},
     "listing: JSON-LD SearchResultsPage, card grid holds 41% of the prose"),
    ({"schema_types": ["OfferCatalog"], "grid_share": 90},
     "listing: JSON-LD OfferCatalog, card grid holds 90% of the prose"),
    ({"listing": "card grid holds 80% of the prose"}, "listing: card grid holds 80% of the prose"),
])
def test_word_target_excludes_what_is_not_prose(over, reason):
    pages = [_measured("https://a.example/", 1, 300, **over),
             _measured("https://b.example/", 2, 310), _measured("https://c.example/", 3, 330)]
    wt = Q.word_target(pages)
    assert wt["used"] == ["https://b.example/", "https://c.example/"] and wt["median"] == 320
    assert wt["excluded"] == [{"url": "https://a.example/", "reason": reason}]


def test_word_target_drops_an_outlier_like_section_target():
    pages = [_measured("https://a.example/", 1, 2000), _measured("https://b.example/", 2, 400),
             _measured("https://c.example/", 3, 300)]
    wt = Q.word_target(pages)
    assert wt["used"] == ["https://b.example/", "https://c.example/"] and wt["median"] == 350
    assert wt["excluded"] == [{"url": "https://a.example/",
                               "reason": "outlier: 2000 words > 1.5 × the next (400)"}]


def test_word_target_without_metrics_names_its_barrier():
    wt = Q.word_target([_record("https://a.example/", PAGE, 1)])
    assert wt["median"] is None and wt["from"] == 0 and wt["of"] == 1
    assert wt["used"] == [] and wt["excluded"] == [{"url": "https://a.example/",
                                                    "reason": "not measured"}]
    assert wt["status"].startswith("NOT FETCHED — ")


def test_the_real_competitor_files_still_load():
    for f in sorted((ROOT / "data/queries/raw").glob("*/competitors.json")):
        Q.load_competitors(f.parent.name, ROOT)


def test_build_writes_the_word_target_and_each_rows_words(tmp_path):
    import jsonschema
    from test_query_augment import make_root, seed, write_raw
    root = make_root(tmp_path)
    seed(root)
    measured = dict(_record("https://a.example", PAGE, 1), metrics=EXPECTED)
    write_raw(root, "m", "competitors", {"status": "ok", "pages": [
        measured, _record("https://b.example", PAGE, 2)]})
    data, _ = Q.build("m", "location", "blue staffy puppies manchester",
                      "/uk-locations/m/", root, "2026-09-26")
    jsonschema.validate(data, json.loads((ROOT / "schemas/queries.schema.json").read_text()))
    wt = data["word_target"]
    assert (wt["median"], wt["from"], wt["of"], wt["used"]) == (None, 1, 2, ["https://a.example"])
    assert wt["status"] == "NOT FETCHED — fewer than two prose competitor pages (1 used)"
    assert [r.get("words") for r in data["competitors"]] == [59, None]


# ── Task 17 review: what counts as prose ──────────────────────────────────────────────────────
def _section_words(html):
    return [(s["h2"], s["words"]) for s in Q.page_metrics(html)["sections"]]


def test_a_consent_dialog_inside_a_section_is_not_prose():
    html = ("<main><h2>Care</h2><p>Two words.</p><div id='onetrust-banner-sdk'>"
            "<p>We use cookies to improve your visit here</p></div></main>")
    assert _section_words(html) == [("Care", 2)]


@pytest.mark.parametrize("attr", ["hidden", "aria-hidden='true'", "role='dialog'",
                                  "aria-modal='true'", "class='cookie-notice'"])
def test_hidden_and_dialog_subtrees_are_not_prose(attr):
    html = (f"<main><h2>Care</h2><p>Two words.</p><div {attr}><p>six more words sit in here</p>"
            "</div></main>")
    m = Q.page_metrics(html)
    assert _section_words(html) == [("Care", 2)] and m["word_count"] == 3


def test_only_main_is_counted_when_the_page_has_one():
    html = ("<body><header><p>Site header words</p></header>"
            "<div><p>Sidebar promo words here</p></div>"
            "<main><h2>Care</h2><p>Two words.</p><img src=a></main><img src=b></body>")
    m = Q.page_metrics(html)
    assert m["scope"] == "main" and m["word_count"] == 3 and m["images"] == 1


def test_role_main_counts_as_main():
    html = "<div><p>outside words</p></div><div role='main'><h2>Care</h2><p>Two words.</p></div>"
    m = Q.page_metrics(html)
    assert m["scope"] == "main" and m["word_count"] == 3


def test_a_single_article_is_the_scope_when_there_is_no_main():
    html = ("<body><div><p>outside words here</p></div><article><h2>Care</h2><p>Two words.</p>"
            "</article></body>")
    m = Q.page_metrics(html)
    assert m["scope"] == "article" and m["word_count"] == 3


def test_without_main_or_one_article_the_body_counts_but_not_its_header():
    html = ("<body><header><p>Logo strap line</p></header><article><h2>A</h2><p>one</p></article>"
            "<article><h2>B</h2><p>two</p></article></body>")
    m = Q.page_metrics(html)
    assert m["scope"] == "body" and "Logo" not in json.dumps(m) and m["word_count"] == 4


def test_a_page_wrapped_in_a_form_is_still_measured():
    html = ("<body><form id='aspnetForm' method='post'><div><h1>Staffy pups</h1>"
            "<p>We raise blue staffy puppies at home.</p><select><option>Choose one</option>"
            "</select><textarea>typed text</textarea></div></form></body>")
    m = Q.page_metrics(html)
    assert m["word_count"] == 9   # h1 2 + prose 7; option and textarea text never count


def test_card_h3s_are_counted_but_never_kept():
    cards = "".join(f"<li><h3>Advert {i} <a href='/a{i}'>Staffy For Sale</a></h3><p>Pup.</p></li>"
                    for i in range(3))
    arts = "".join(f"<article><a href='/l{i}'><h3>Litter ad {i}</h3></a></article>"
                   for i in range(2))
    html = (f"<main><h2>Pups</h2><p>Intro.</p><h3>Real heading</h3><ul>{cards}</ul>{arts}"
            "<h3><a href='/x'>Linked title</a></h3></main>")
    s = Q.page_metrics(html)["sections"][0]
    assert s["h3_count"] == 7 and s["h3"] == ["Real heading"]


def test_a_section_with_more_than_12_h3s_keeps_only_the_count():
    h3s = "".join(f"<h3>Heading {i}</h3><p>word</p>" for i in range(13))
    s = Q.page_metrics(f"<main><h2>Many</h2>{h3s}</main>")["sections"][0]
    assert s["h3_count"] == 13 and s["h3"] == []


def test_a_card_grid_holding_most_of_the_prose_marks_a_listing():
    cards = "".join(f"<li><a href='/p/{i}'><h3>Pup {i}</h3><p>Lovely blue boy ready now with papers"
                    "</p></a></li>" for i in range(6))
    html = (f"<main><h2>Staffies for sale</h2><ul>{cards}</ul><h2>About</h2>"
            "<p>Short note.</p></main>")
    m = Q.page_metrics(html)
    assert m["listing"] and m["listing"].startswith("card grid holds ")


def test_a_breeder_page_with_a_small_card_grid_is_not_a_listing():
    assert Q.page_metrics(PAGE)["listing"] is None


@pytest.mark.parametrize("attr", ['type="application/ld+json; charset=utf-8"',
                                  'type="Application/LD+JSON"'])
def test_json_ld_type_attribute_may_carry_parameters(attr):
    html = f'<script {attr}>{{"@type":"http://schema.org/ItemList"}}</script><main></main>'
    assert Q.page_metrics(html)["schema_types"] == ["ItemList"]


def test_schema_org_url_types_are_normalised():
    html = ('<script type="application/ld+json">{"@type":["https://schema.org/FAQPage",'
            '"schema:Thing","Offer"]}</script>')
    assert Q.page_metrics(html)["schema_types"] == ["FAQPage", "Offer", "schema:Thing"]


@pytest.mark.parametrize("text", [
    "Call 07700 900123", "+44 (0)161 496 0000", "0161-496-0000", "0161.496.0000",
    "07700.900.123", "tel: +44 7700 900123", "mail jo@example.co.uk", "jo (at) example.com",
    "jo at example dot com", "wa.me/447700900123", "WhatsApp us",
])
def test_contactish_catches_contact_details(text):
    assert Q.CONTACTISH.search(text), text


@pytest.mark.parametrize("text", [
    "Staffies @ home", "Microchip 977200000123456", "Born 23/09/2026", "2026-09-23",
    "£1,500 each", "Price 1500.00", "Litter of 6 @ 8 weeks", "Chip 900 164 001 234 567",
    "Meet us at the park",
])
def test_contactish_leaves_ordinary_text_alone(text):
    assert not Q.CONTACTISH.search(text), text


def test_word_target_when_every_measured_page_is_a_listing_says_so():
    wt = Q.word_target([_measured("https://a.example/", 1, 300, schema_types=["ItemList"],
                                  grid_share=70)])
    assert wt["median"] is None and wt["used"] == []
    assert wt["status"] == "NOT FETCHED — fewer than two prose competitor pages (0 used)"


def test_accordion_faq_h3s_in_a_list_are_kept():
    qs = "".join(f"<li><button><h3>Question {i}?</h3></button><div>Answer.</div></li>"
                 for i in range(4))
    s = Q.page_metrics(f"<main><h2>FAQs</h2><ul>{qs}</ul></main>")["sections"][0]
    assert s["h3"] == [f"Question {i}?" for i in range(4)]



# ── Task 17 re-review: FAQ lists are prose ────────────────────────────────────────────────────
def _words(n, w="word"):
    return " ".join([w] * n)


def test_a_plain_faq_list_is_prose_and_keeps_its_questions():
    qs = "".join(f"<li><h3>Question {i}?</h3><p>{_words(60)}</p></li>" for i in range(6))
    html = (f"<main><p>{_words(80)}</p><h2>About us</h2><p>{_words(80)}</p>"
            f"<h2>FAQs</h2><ul>{qs}</ul></main>")
    m = Q.page_metrics(html)
    assert m["listing"] is None and m["grid_share"] == 0
    assert m["sections"][1]["h3"] == [f"Question {i}?" for i in range(6)]


def test_plain_text_h3_items_without_links_are_not_cards():
    items = "".join(f"<li><h3>Step {i}</h3><p>{_words(20)}</p></li>" for i in range(5))
    m = Q.page_metrics(f"<main><h2>How it works</h2><ul>{items}</ul></main>")
    assert m["listing"] is None and m["sections"][0]["h3"] == [f"Step {i}" for i in range(5)]


def test_every_h3_is_kept_on_a_page_with_faqpage_json_ld():
    ld = '<script type="application/ld+json">{"@type":"FAQPage"}</script>'
    items = "".join(f"<li><a href='/q{i}'><h3>Ask {i}</h3></a><p>answer</p></li>" for i in range(4))
    m = Q.page_metrics(f"{ld}<main><h2>FAQs</h2><ul>{items}</ul></main>")
    assert m["sections"][0]["h3"] == [f"Ask {i}" for i in range(4)] and m["listing"] is None


def test_a_linked_30_card_grid_is_still_a_listing_and_drops_its_titles():
    cards = "".join(f"<li><a href='/pup/{i}'><h3>Blue Staffy Pup {i}</h3>"
                    f"<p>{_words(20)}</p></a></li>" for i in range(30))
    m = Q.page_metrics(f"<main><h2>30 puppies found</h2><p>{_words(10)}</p><ul>{cards}</ul></main>")
    assert m["listing"] and m["listing"].startswith("card grid holds ")
    assert m["sections"][0]["h3"] == [] and m["sections"][0]["h3_count"] == 30


def test_listing_json_ld_with_a_small_grid_is_kept_with_a_note():
    pages = [_measured("https://a.example/", 1, 300, schema_types=["ItemList"], grid_share=12),
             _measured("https://b.example/", 2, 320)]
    wt = Q.word_target(pages)
    assert wt["used"] == ["https://a.example/", "https://b.example/"] and wt["excluded"] == []
    assert wt["notes"] == [{"url": "https://a.example/",
                            "reason": "has ItemList JSON-LD (kept: grid share 12%, 71% of the "
                                      "prose in sections)"}]


def test_listing_json_ld_with_a_large_grid_is_excluded():
    pages = [_measured("https://a.example/", 1, 300, schema_types=["ItemList"], grid_share=55),
             _measured("https://b.example/", 2, 320), _measured("https://c.example/", 3, 340)]
    wt = Q.word_target(pages)
    assert wt["used"] == ["https://b.example/", "https://c.example/"] and wt["notes"] == []
    assert wt["excluded"] == [{"url": "https://a.example/",
                               "reason": "listing: JSON-LD ItemList, card grid holds 55% of "
                                         "the prose"}]


def test_site_of_documents_its_hand_kept_suffix_list():
    assert "Public Suffix List" in Q.site_of.__doc__
    assert Q.site_of("https://www.pets4homes.co.uk/x") == "pets4homes.co.uk"



# ── Task 17: listing pages need prose in sections; the target needs two pages ────────────────
def test_section_share_is_the_prose_inside_content_sections():
    assert Q.page_metrics(PAGE)["section_share"] == 71   # 27 of 38 prose words
    html = f"<main><p>{_words(90)}</p><h2>About</h2><p>{_words(10)}</p></main>"
    assert Q.page_metrics(html)["section_share"] == 10


def test_listing_json_ld_with_little_prose_in_sections_is_excluded():
    # puppies.co.uk's shape: ItemList, headless div cards, 1168 of 1349 words before any H2
    cards = "".join(f"<div class='card'><img src='/{i}.jpg'><p>{_words(20)}</p></div>"
                    for i in range(40))
    ld = '<script type="application/ld+json">{"@type":"ItemList"}</script>'
    html = f"{ld}<main>{cards}<h2>Recommended for you</h2><p>{_words(60)}</p></main>"
    m = Q.page_metrics(html)
    assert m["grid_share"] == 0 and m["section_share"] == 7
    pages = [dict(_record("https://a.example/", html, 1), metrics=m),
             _measured("https://b.example/", 2, 300), _measured("https://c.example/", 3, 320)]
    wt = Q.word_target(pages)
    assert wt["excluded"] == [{"url": "https://a.example/", "reason":
                               "listing: JSON-LD ItemList, only 7% of the prose sits in content "
                               "sections"}]


def test_a_breeder_page_with_item_list_and_prose_in_sections_is_kept_with_a_note():
    ld = '<script type="application/ld+json">{"@type":"ItemList"}</script>'
    html = (f"{ld}<main><p>{_words(20)}</p><h2>Our dogs</h2><p>{_words(100)}</p>"
            f"<h2>Health</h2><p>{_words(80)}</p></main>")
    m = Q.page_metrics(html)
    assert m["section_share"] == 90 and m["listing"] is None
    pages = [dict(_record("https://a.example/", html, 1), metrics=m),
             _measured("https://b.example/", 2, 300)]
    wt = Q.word_target(pages)
    assert "https://a.example/" in wt["used"] and wt["excluded"] == []
    assert wt["notes"] == [{"url": "https://a.example/",
                            "reason": "has ItemList JSON-LD (kept: grid share 0%, 90% of the "
                                      "prose in sections)"}]


@pytest.mark.parametrize("n", [0, 1])
def test_word_target_needs_two_prose_pages(n):
    pages = [_measured(f"https://s{i}.example/", i + 1, 300 + i) for i in range(n)]
    pages.append(dict(_record("https://blocked.example/", PAGE, 9), blocked=True,
                      metrics=EXPECTED))
    wt = Q.word_target(pages)
    assert wt["median"] is None and wt["from"] == n and len(wt["used"]) == n
    assert wt["status"] == f"NOT FETCHED — fewer than two prose competitor pages ({n} used)"


def test_word_target_with_two_prose_pages_has_a_median():
    wt = Q.word_target([_measured("https://a.example/", 1, 300),
                        _measured("https://b.example/", 2, 400)])
    assert wt["median"] == 350 and "status" not in wt


def test_load_competitors_refuses_a_bad_section_share(tmp_path):
    page = _record("https://a.example/", PAGE, 1)
    page["metrics"] = dict(EXPECTED, section_share=-3)
    root = _repo(tmp_path, [page], {})
    with pytest.raises(Q.BadInput, match="section_share"):
        Q.load_competitors(SLUG, root)



# ── Task 17: cards linked beside the title; the measure-first hint ────────────────────────────
def _view_items(tag, n=8):
    return "".join(f"<{tag}><img src='/{i}.jpg'><h3>Pup {i}</h3><p>{_words(20)}</p>"
                   f"<a href='/pup/{i}'>View</a></{tag}>" for i in range(n))


@pytest.mark.parametrize("wrap,tag", [("ul", "li"), ("div", "article")])
def test_cards_linked_beside_the_title_are_a_listing(wrap, tag):
    html = (f"<main><h2>Puppies for sale</h2><p>{_words(10)}</p>"
            f"<{wrap}>{_view_items(tag)}</{wrap}></main>")
    m = Q.page_metrics(html)
    assert m["listing"] and m["listing"].startswith("card grid holds ")
    assert m["sections"][0]["h3"] == [] and m["sections"][0]["h3_count"] == 8


def test_a_faq_list_with_inline_links_in_its_answers_is_prose():
    qs = "".join(f"<li><h3>{q}</h3><p>{_words(30)} see <a href='/g{i}'>our guide</a> "
                 f"{_words(20)}</p></li>"
                 for i, q in enumerate(["Feeding", "Worming", "Vaccines", "Insurance",
                                        "Is a staffy good with kids?", "Microchips"]))
    html = f"<main><p>{_words(80)}</p><h2>FAQs</h2><ul>{qs}</ul></main>"
    m = Q.page_metrics(html)
    assert m["listing"] is None and m["grid_share"] == 0
    assert m["sections"][0]["h3"] == ["Feeding", "Worming", "Vaccines", "Insurance",
                                      "Is a staffy good with kids?", "Microchips"]


def test_word_target_with_nothing_measured_says_to_measure_first():
    wt = Q.word_target([_record("https://a.example/", PAGE, 1),
                        dict(_record("https://b.example/", PAGE, 2), blocked=True)])
    assert wt["median"] is None and wt["status"] == (
        "NOT FETCHED — no competitor page measured yet; run python3 scripts/query_augment.py "
        "--competitor-metrics <slug>")


def test_word_target_with_some_metrics_keeps_the_two_page_wording():
    wt = Q.word_target([_measured("https://a.example/", 1, 300),
                        _record("https://b.example/", PAGE, 2)])
    assert wt["status"] == "NOT FETCHED — fewer than two prose competitor pages (1 used)"
