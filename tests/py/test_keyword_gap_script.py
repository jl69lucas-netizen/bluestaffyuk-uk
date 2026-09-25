# tests/py/test_keyword_gap_script.py — runs the script embedded in
# .claude/agents/bsuk-competitive-keyword-gap-agent.md on small inputs.
#
# The agent's gap list is only as good as that script: it names topics, decides coverage and
# scores every row, and two readers must get the same list. So the heredoc is extracted from
# the agent file exactly as a reader would run it, and run here on the Task 7 fixture, a tiny
# BSUK profile and a tiny page map (with one migrated noindex stub).
import json
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import competitor_registry_check as C  # noqa: E402 — the registry's root-domain rule
AGENT = REPO / ".claude/agents/bsuk-competitive-keyword-gap-agent.md"
FIXTURE = REPO / "tests/py/fixtures/competitors/report-example-breeder.json"
HEREDOC = re.compile(r"<<'EOF'\n(.*?)\nEOF\n", re.S)
STUB = "/uk-locations/blue-staffy-puppies-manchester-uk/"
P = "https://SITE_URL_PLACEHOLDER"


def script():
    found = HEREDOC.findall(AGENT.read_text(encoding="utf-8"))
    assert len(found) == 1, f"expected exactly one <<'EOF' block, found {len(found)}"
    return found[0]


def page(url, title, h1=None):
    return {"url": url, "title": title, "h1": title if h1 is None else h1, "h2": []}


def report(rid, pages, fetched_on="2026-09-24", root_domain=None):
    """A competitor report; its root domain is the registrable domain of the first page's URL (the
    registry's rule) unless given."""
    nf = {"status": "NOT FETCHED", "reason": "test"}
    root_domain = root_domain or (C.root_domain(pages[0]["url"]) if pages else f"{rid}.co.uk")
    r = {"id": rid, "root_domain": root_domain, "analysed_on": "2026-09-24",
         "keywords": nf, "page_types": nf, "cities": nf, "schema_types": nf,
         "pages": {"status": "ok", "fetched_on": fetched_on, "values": pages},
         "trust": nf, "content": nf, "blog": nf, "visual": nf, "conversion": nf,
         "technical": nf, "key_insight": "test"}
    return r


@pytest.fixture
def root(tmp_path):
    (tmp_path / "data").mkdir()
    shutil.copy(REPO / "data/locations.json", tmp_path / "data/locations.json")
    (tmp_path / "scripts").mkdir()
    shutil.copy(REPO / "scripts/competitor_registry_check.py", tmp_path / "scripts")
    pmap = {"pages": [
        {"url": STUB, "title": "Blue Staffy Puppies Manchester UK", "h1": "",
         "defects": ["stub"], "refresh_flags": ["stub-noindexed"]},
        {"url": "/uk-locations/blue-staffy-puppies-for-sale-leeds/", "title": "Blue Staffy Puppies For Sale Leeds",
         "h1": "", "defects": ["stub"], "refresh_flags": ["stub-noindexed"]},
        {"url": "/uk-locations/blue-staffies-newcastle-under-lyme/", "title": "Blue Staffies Newcastle Under Lyme",
         "h1": "", "defects": ["stub"], "refresh_flags": ["stub-noindexed"]},
        {"url": "/uk-locations/blue-staffy-puppies-york/", "title": "Blue Staffy Puppies For Sale in York",
         "h1": "Blue Staffy Puppies For Sale in York, Yorkshire", "defects": [], "refresh_flags": []},
        {"url": "/buy-staffy-puppies-for-sale-uk/", "title": "Buy Staffy Puppies For Sale UK",
         "h1": "Buy Staffy Puppies for Sale UK", "defects": [], "refresh_flags": []},
    ]}
    (tmp_path / "data/page-map.json").write_text(json.dumps(pmap))
    (tmp_path / "gap.py").write_text(script())
    return tmp_path


def write(root, name, data):
    path = root / name
    path.write_text(json.dumps(data))
    return str(path)


def profile(root, extra=()):
    pages = [page(f"{P}/blue-staffy-pup-sale-uk/", "Blue Staffy Puppy Prices UK | Deposit",
                  "What A Blue Staffy Puppy Costs With Us"),
             page(f"{P}/uk-locations/blue-staffy-puppies-york/", "Blue Staffy Puppies For Sale in York",
                  "Blue Staffy Puppies For Sale in York, Yorkshire"),
             page(f"{P}/uk-blue-staffy-breeders-contact/", "Contact Blue Staffy UK"),
             *extra]
    r = report("bsuk", pages, "2026-09-25")
    return write(root, "bsuk.json", r)


def run(root, src, *reports, env=None):
    out = subprocess.run([sys.executable, "gap.py", src, *reports], cwd=root, capture_output=True,
                         text=True, env={"TODAY": "2026-09-25", "PATH": "/usr/bin:/bin", **(env or {})})
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def row(rows, topic):
    found = [r for r in rows if r["topic"] == topic]
    assert len(found) == 1, (topic, [r["topic"] for r in rows])
    return found[0]


def test_page_map_mode_labels_the_noindex_stub_and_keeps_the_comparison(root):
    d = run(root, "data/page-map.json", str(FIXTURE))
    assert d["bsuk_source"] == "data/page-map.json"
    man = row(d["gaps"], "blue staffy puppies in manchester")
    assert (man["score"], man["band"], man["noindex_pages"]) == (10, "high", [STUB])
    vs = row(d["gaps"], "blue staffy vs american bully")
    assert vs["type"] == "comparison" and vs["urls"] == [
        "https://example-breeder.co.uk/blue-staffy-vs-american-bully/"]
    assert row(d["gaps"], "staffy puppy prices")["noindex_pages"] == []


def test_profile_mode_covers_price_and_labels_a_stub_absent_from_the_profile(root):
    d = run(root, profile(root), str(FIXTURE))
    assert row(d["covered"], "staffy puppy prices")["bsuk_page"] == f"{P}/blue-staffy-pup-sale-uk/"
    assert row(d["gaps"], "blue staffy puppies in manchester")["noindex_pages"] == [STUB]


def test_a_rebuilt_page_at_a_stub_route_is_coverage_in_profile_mode(root):
    src = profile(root, [page(f"{P}{STUB}", "Blue Staffy Puppies Manchester", "")])
    d = run(root, src, str(FIXTURE))
    assert row(d["covered"], "blue staffy puppies in manchester")["bsuk_page"] == f"{P}{STUB}"


def test_a_profile_without_pages_falls_back_to_the_page_map_by_name(root):
    nf = report("bsuk", [])
    nf["pages"] = {"status": "NOT FETCHED", "reason": "test"}
    d = run(root, write(root, "bsuk.json", nf), str(FIXTURE))
    assert d["bsuk_source"].startswith("data/page-map.json (fallback:")
    assert row(d["gaps"], "blue staffy puppies in manchester")["noindex_pages"] == [STUB]


def test_pages_with_no_keyword_topic_or_no_content_words_are_skipped(root):
    r = report("alpha", [
        page("https://alpha.co.uk/", "Alpha | Home", "Welcome to Alpha"),
        page("https://alpha.co.uk/about-us/", "About Us"),
        page("https://alpha.co.uk/for-sale/", "For Sale"),
        page("https://alpha.co.uk/buy/", "Buy"),
        page("https://alpha.co.uk/terms/", None, None),
    ])
    d = run(root, profile(root), write(root, "alpha.json", r))
    why = {s["url"].split("/")[3]: s["why"] for s in d["skipped"]}
    assert why == {"": "no keyword topic", "about-us": "no keyword topic",
                   "for-sale": "no content words", "buy": "no content words",
                   "terms": "no title or H1"}
    assert d["gaps"] == [] and d["covered"] == []


def test_contact_and_faq_are_covered_by_page_type(root):
    r = report("alpha", [page("https://alpha.co.uk/contact/", "Get In Touch", "Get In Touch")])
    d = run(root, profile(root), write(root, "alpha.json", r))
    assert d["skipped"] and d["skipped"][0]["why"] == "no keyword topic"
    r = report("beta", [page("https://beta.co.uk/faq/", "Frequently Asked Questions")])
    d = run(root, profile(root), write(root, "beta.json", r))
    faq = row(d["gaps"], "frequently asked questions")      # BSUK has no faq page
    assert (faq["dedicated"], faq["key"], faq["intent"], faq["score"]) == (0, 2, 0, 5)
    d = run(root, profile(root, [page(f"{P}/faq/", "Questions About Our Puppies")]),
            write(root, "beta.json", r))
    assert row(d["covered"], "frequently asked questions")["bsuk_page"] == f"{P}/faq/"


def test_a_city_stays_in_the_topic_and_only_the_same_city_covers_it(root):
    r = report("gamma", [
        page("https://g.co.uk/k/", "Blue Staffy Puppies for Sale in Newcastle-under-Lyme"),
        page("https://g.co.uk/y/", "Staffy Puppies Yorkshire"),
        page("https://g.co.uk/d/", "Blue Staffy Leeds"),
    ])
    d = run(root, profile(root), write(root, "gamma.json", r))
    ncl = row(d["gaps"], "blue staffy puppies for sale in newcastle under lyme")
    assert ncl["dedicated"] == 3 and ncl["intent"] == 2
    york = row(d["gaps"], "staffy puppies yorkshire")        # the York page is not coverage
    assert york["dedicated"] == 0
    leeds = row(d["gaps"], "blue staffy leeds")
    assert (leeds["intent"], leeds["score"], leeds["band"]) == (2, 8, "high")
    assert leeds["noindex_pages"] == ["/uk-locations/blue-staffy-puppies-for-sale-leeds/"]
    assert ncl["noindex_pages"] == ["/uk-locations/blue-staffies-newcastle-under-lyme/"]   # same city, not same words


def test_a_whole_h1_topic_scores_no_dedicated_point_and_can_be_low(root):
    r = report("delta", [page("https://d.co.uk/blog/right-for-you/", "Is a Blue Staffy Right for You?")])
    d = run(root, profile(root), write(root, "delta.json", r))
    g = row(d["gaps"], "is a blue staffy right for you")
    assert (g["dedicated"], g["key"], g["no_bsuk_page"], g["intent"], g["score"], g["band"]) == (
        0, 0, 3, 0, 3, "low")


def test_licence_and_health_testing_are_always_high_by_word(root):
    r = report("eps", [page("https://e.co.uk/health-testing/", "DNA Health Testing", "Our DNA Health Testing"),
                       page("https://e.co.uk/health-and-safety/", "Health and Safety Policy"),
                       page("https://e.co.uk/licence/", "Our Staffy Licence")])
    d = run(root, profile(root), write(root, "eps.json", r))
    assert row(d["gaps"], "our dna health testing")["band"] == "high"
    assert row(d["gaps"], "our staffy licence")["always_high"] is True
    hs = row(d["gaps"], "health and safety policy")
    assert hs["always_high"] is False and hs["band"] == "low"


def test_the_output_does_not_depend_on_report_order(root):
    a = write(root, "a.json", report("aaa", [
        page("https://aaa.com/health/", "Staffy Wellbeing"),
        page("https://aaa.com/blue-staffy-puppies-for-sale-leeds/", "x", "Blue Staffy Puppies For Sale in Leeds"),
        page("https://aaa.com/blue-staffy-puppies-for-sale-leeds/", "x", "Blue Staffy Puppies For Sale in Leeds")]))
    z = write(root, "z.json", report("zzz", [
        page("https://zzz.com/wellbeing-licence/", "Staffy Wellbeing"),
        page("https://zzz.com/leeds/", "Staffy Puppies Leeds")]))
    src = profile(root)
    one, two = run(root, src, a, z), run(root, src, z, a)
    assert one == two
    well = row(one["gaps"], "staffy wellbeing")
    assert well["types"] == ["health"] and well["type"] == "health"
    leeds = [r for r in one["gaps"] if "leeds" in r["topic"]]
    assert len(leeds) == 1 and len(leeds[0]["urls"]) == 2     # one row, URLs deduped


def test_comparison_topics_take_the_x_vs_y_core_and_versus_folds_to_vs(root):
    r = report("zeta", [
        page("https://z.co.uk/staffy-vs-pitbull/", "Staffy vs Pitbull: Which Is Right? | Z",
             "Staffy vs Pitbull: Which Is Right For Your Family And Home In The UK Today"),
        page("https://z.co.uk/staffy-versus-pitbull/", "Staffy Versus Pitbull")])
    d = run(root, profile(root), write(root, "zeta.json", r))
    vs = row(d["gaps"], "staffy vs pitbull")
    assert len(vs["urls"]) == 2 and vs["type"] == "comparison"


def test_cut_names_and_tier_5(root):
    (root / "data/competitors.json").write_text(json.dumps(
        {"competitors": [{"id": "t5", "tier": 5}, {"id": "old", "tier": 1}, {"id": "old5", "tier": 5}]}))
    t5 = write(root, "t5.json", report("t5", [
        page("https://t5.com/licence/", "Our Staffy Licence"),
        page("https://t5.com/kennel/", "Smith Kennels", "Smith Kennels"),
        page("https://t5.com/from/", "Blue Staffy Puppies from Smith Kennels")]))
    old = write(root, "old.json", report("old", [], "2026-08-01"))
    old5 = write(root, "old5.json", report("old5", [], "2026-08-01"))
    d = run(root, profile(root), t5, old, old5, env={"CUT": "smith kennels,smi"})
    lic = row(d["gaps"], "our staffy licence")
    assert lic["urls"] == [] and lic["tier5_urls"] == ["https://t5.com/licence/"] and lic["tier5_only"]
    assert any(s["why"] == "name only" for s in d["skipped"])
    assert row(d["covered"], "blue staffy puppies")["tier5_urls"] == ["https://t5.com/from/"]  # cut, then covered
    assert [s["id"] for s in d["stale"]] == ["old"] and [s["id"] for s in d["stale_tier5"]] == ["old5"]


def test_a_trust_word_anywhere_in_the_heading_makes_the_row_always_high(root):
    h = ("Staffy Puppies for Sale UK Breeder Blue KC Registered Licensed Health Tested "
         "Champion Bloodline Family Raised Pets")
    d = run(root, profile(root), write(root, "j.json", report("jay", [page("https://probe.com/j/", h)])))
    g = row(d["gaps"], "staffy puppies for sale uk breeder")    # the words sit outside the topic
    assert g["always_high"] is True and g["band"] == "high"


def test_a_city_topic_is_covered_by_a_bsuk_city_page_naming_the_same_cities(root):
    r = report("york", [page("https://y.co.uk/staffy-pups-york/", "Staffy Pups York"),
                        page("https://y.co.uk/blue-staffy-breeder-york/", "Blue Staffy Breeder York")])
    d = run(root, profile(root), write(root, "york.json", r))
    york = row(d["covered"], "staffy pups york")                      # one city, one row
    assert york["bsuk_page"] == f"{P}/uk-locations/blue-staffy-puppies-york/" and len(york["urls"]) == 2
    assert d["gaps"] == []


def test_one_city_is_one_row_with_its_urls_merged(root):
    r = report("leeds", [page("https://l.co.uk/leeds/", "Staffy Puppies for Sale in Leeds"),
                         page("https://l.co.uk/leeds-and-bradford/", "Blue Staffy Puppies Leeds and Bradford")])
    d = run(root, profile(root), write(root, "leeds.json", r))
    rows = [g for g in d["gaps"] if "leeds" in g["topic"]]
    assert len(rows) == 1 and len(rows[0]["urls"]) == 2
    assert rows[0]["noindex_pages"] == ["/uk-locations/blue-staffy-puppies-for-sale-leeds/"]


def test_a_comparison_core_is_a_dedicated_page(root):
    d = run(root, profile(root), str(FIXTURE))
    vs = row(d["gaps"], "blue staffy vs american bully")
    assert (vs["dedicated"], vs["score"], vs["band"]) == (3, 6, "medium")


def test_tested_alone_is_not_a_trust_word(root):
    r = report("tips", [page("https://t.co.uk/training-tips/", "Tried and Tested Staffy Training Tips"),
                        page("https://t.co.uk/tips/", "Tried and Tested Staffy Training Tips")])
    d = run(root, profile(root), write(root, "tips.json", r))
    g = row(d["gaps"], "tried and tested staffy training tips")   # care-guide; the untyped copy is skipped
    assert g["always_high"] is False and g["band"] == "medium" and g["urls"] == ["https://t.co.uk/training-tips/"]
    assert d["skipped"] == [{"url": "https://t.co.uk/tips/", "why": "no keyword topic"}]


def test_the_city_rule_is_only_for_breed_and_buyer_words(root):
    r = report("york2", [
        page("https://y.co.uk/staffy-pups-york/", "Staffy Pups York"),
        page("https://y.co.uk/staffy-training-york/", "Staffy Training York"),
        page("https://y.co.uk/staffy-rescue-york/", "Staffy Rescue York"),
        page("https://y.co.uk/rescue/", "Staffy Rescue York"),
        page("https://y.co.uk/blue-staffy-vs-pitbull-london/", "Blue Staffy vs Pitbull London"),
        page("https://y.co.uk/staffy-vet-aberdeen/", "Staffy Vet Aberdeen")])
    d = run(root, profile(root), write(root, "york2.json", r))
    assert row(d["covered"], "staffy pups york")["urls"] == ["https://y.co.uk/staffy-pups-york/"]
    training = row(d["gaps"], "staffy training york")
    assert training["type"] == "care-guide" and training["noindex_pages"] == []
    rescue = row(d["gaps"], "staffy rescue york")                  # its own row, not the puppy row
    assert rescue["urls"] == ["https://y.co.uk/rescue/", "https://y.co.uk/staffy-rescue-york/"]
    assert rescue["type"] is None
    vs = [g for g in d["gaps"] if "pitbull" in g["topic"]]
    assert len(vs) == 1 and vs[0]["type"] == "comparison" and vs[0]["dedicated"] == 3
    vet = row(d["gaps"], "staffy vet aberdeen")                    # a city is intent only on a city topic
    assert (vet["intent"], vet["score"], vet["band"]) == (0, 6, "medium")
    assert (training["intent"], rescue["intent"]) == (0, 0)


def test_every_licence_spelling_is_always_high_like_llm_intels_safety_list(root):
    # the same spellings llm-intel's "licence" entity matches: licence, license, licensed, licenced, licensing
    pages = [page(f"https://l.co.uk/{w}/", f"Staffy {w.title()} Info") for w in
             ("licence", "license", "licensed", "licenced", "licensing")]
    d = run(root, profile(root), write(root, "l.json", report("lic", pages)))
    for w in ("licence", "license", "licensed", "licenced", "licensing"):
        assert row(d["gaps"], f"staffy {w} info")["always_high"] is True, w


def test_a_vs_post_under_a_blog_base_is_a_comparison_as_in_intel(root):
    # Known Issue 52: one table for both agents, comparison first
    r = report("vsb", [page("https://vsb.co.uk/blog/staffy-vs-pitbull/", "Staffy vs Pitbull")])
    d = run(root, profile(root), write(root, "vsb.json", r))
    assert row(d["gaps"], "staffy vs pitbull")["type"] == "comparison"


def test_a_path_word_inside_a_longer_word_does_not_type_the_page(root):
    # Known Issue 51: "costofliving" holds "cost" but not as a word, so the calculator is untyped
    r = report("rsp", [page("https://rsp.org.uk/adviceandwelfare/costofliving/petcalculator",
                            "Pet Cost Calculator", "How much will a pet cost?")])
    d = run(root, profile(root), write(root, "rsp.json", r))
    assert d["skipped"] == [{"url": "https://rsp.org.uk/adviceandwelfare/costofliving/petcalculator",
                             "why": "no keyword topic"}]


def test_a_page_on_another_domain_is_flagged_and_never_a_gap(root):
    # Known Issue 52: a report's pages must sit on its own root domain (subdomains count)
    r = report("own", [page("https://www.own.co.uk/staffy-care/", "Staffy Care Guide"),
                       page("https://help.own.co.uk/staffy-grooming/", "Staffy Grooming Guide"),
                       page("https://other-site.com/staffy-training/", "Staffy Training Guide")],
               root_domain="own.co.uk")
    d = run(root, profile(root), write(root, "own.json", r))
    assert d["foreign_urls"] == [{"id": "own", "url": "https://other-site.com/staffy-training/",
                                  "root_domain": "own.co.uk"}]
    assert [g["topic"] for g in d["gaps"]] == ["staffy care guide", "staffy grooming guide"]


def test_the_report_helper_takes_the_first_page_s_registrable_domain():
    assert report("x", [page("https://shop.x.co.uk/a/", "A")])["root_domain"] == "x.co.uk"
    assert report("x", [page("https://www.x.co.uk/a/", "A")])["root_domain"] == "x.co.uk"
    assert report("x", [])["root_domain"] == "x.co.uk"


def test_the_same_page_written_two_ways_in_two_reports_is_one_duplicate(root):
    # a trailing slash, www., the scheme and utm_ parameters never make a second page
    a = write(root, "a.json", report("aaa", [page("https://www.shared.co.uk/staffy-care/", "Staffy Care Guide")]))
    b = write(root, "b.json", report("bbb", [page("http://shared.co.uk/staffy-care?utm_source=fb", "Staffy Care Guide")]))
    d = run(root, profile(root), a, b)
    assert d["duplicate_urls"] == [{"url": "http://shared.co.uk/staffy-care?utm_source=fb", "ids": ["aaa", "bbb"]}]
    assert row(d["gaps"], "staffy care guide")["urls"] == ["http://shared.co.uk/staffy-care?utm_source=fb"]  # counted once


def test_the_same_url_in_two_reports_is_flagged(root):
    u = "https://shared.co.uk/staffy-care/"
    a = write(root, "a.json", report("aaa", [page(u, "Staffy Care Guide")], root_domain="shared.co.uk"))
    b = write(root, "b.json", report("bbb", [page(u, "Staffy Care Guide"),
                                             page("https://shared.co.uk/care/", "Staffy Care Guide")],
                                     root_domain="shared.co.uk"))
    d = run(root, profile(root), a, b)
    assert d["duplicate_urls"] == [{"url": u, "ids": ["aaa", "bbb"]}]
    assert row(d["gaps"], "staffy care guide")["urls"] == ["https://shared.co.uk/care/", u]   # still one row
    assert run(root, profile(root), b)["duplicate_urls"] == []     # twice in one report is not two reports


@pytest.mark.parametrize("recorded", ["www.own.co.uk", "Own.co.uk"])
def test_a_report_s_own_domain_is_normalised_before_the_foreign_check(root, recorded):
    # a report that records its domain with www. or capitals still owns its pages
    r = report("own", [page("https://www.own.co.uk/staffy-care/", "Staffy Care Guide"),
                       page("https://other-site.com/staffy-training/", "Staffy Training Guide")],
               root_domain=recorded)
    d = run(root, profile(root), write(root, "own.json", r))
    assert d["foreign_urls"] == [{"id": "own", "url": "https://other-site.com/staffy-training/",
                                  "root_domain": recorded}]
    assert [g["topic"] for g in d["gaps"]] == ["staffy care guide"]


GM = "https://p.co.uk/sale/puppies/staffordshire-bull-terrier/united-kingdom/england/greater-manchester/manchester/"


def test_greater_before_a_city_is_that_city(root):
    # Known Issue 52: the pets4homes Manchester listing names "Manchester, Greater Manchester"
    h = "Staffordshire Bull Terrier Puppies for sale in Manchester, Greater Manchester"
    d = run(root, profile(root), write(root, "p.json", report("p", [page(GM, h)])))
    g = row(d["gaps"], "staffordshire bull terrier puppies for sale in manchester greater manchester")
    assert (g["type"], g["noindex_pages"], g["score"], g["band"]) == ("city", [STUB], 10, "high")


def test_a_two_city_page_gets_each_citys_stub(root):
    r = report("two", [page("https://two.co.uk/leeds-manchester/", "Blue Staffy Puppies Leeds and Manchester")])
    d = run(root, profile(root), write(root, "two.json", r))
    g = row(d["gaps"], "blue staffy puppies leeds and manchester")
    assert g["noindex_pages"] == ["/uk-locations/blue-staffy-puppies-for-sale-leeds/", STUB]


def test_a_place_outside_the_location_list_never_becomes_a_topic_or_a_stub_label(root):
    # The decision (Known Issue 52): data/locations.json is the city list. A page for Scotland or
    # Newcastle upon Tyne keeps only its breed and buyer words, so it joins the national row; it
    # never names a new place and never borrows the Newcastle-under-Lyme stub.
    r = report("off", [page("https://off.co.uk/staffy-puppies-newcastle-upon-tyne/",
                            "Staffy Puppies for Sale in Newcastle upon Tyne"),
                       page("https://off.co.uk/staffy-puppies-scotland/", "Staffy Puppies for Sale in Scotland")])
    d = run(root, profile(root), write(root, "off.json", r))
    assert [c["topic"] for c in d["covered"]] == ["staffy puppies for sale"]
    assert d["covered"][0]["urls"] == ["https://off.co.uk/staffy-puppies-newcastle-upon-tyne/",
                                       "https://off.co.uk/staffy-puppies-scotland/"]
    assert d["gaps"] == []


def test_greater_before_no_city_is_just_a_word(root):
    # "greater" joins a city only when a data/locations.json city follows it; elsewhere it is an
    # ordinary word, so the page is no city topic and borrows no stub. (The H1 has no 3-word run, so
    # the whole H1 is the topic and "greater" stays in it; "Greater Staffy Puppies Leeds" would give
    # the run "staffy puppies leeds" and drop the word.)
    r = report("gs", [page("https://gs.co.uk/greater-staffy-puppies-leeds/", "Greater Staffy Leeds")])
    d = run(root, profile(root), write(root, "gs.json", r))
    g = row(d["gaps"], "greater staffy leeds")
    assert (g["type"], g["noindex_pages"]) == ("listing", [])


def test_no_location_city_sits_inside_another_as_whole_words():
    # stubs() looks each city of a multi-city topic up on its own; a city whose words sit inside
    # another city's words ("york" in "north york") would match both and borrow the wrong stub.
    words = lambda t: re.findall(r"[a-z0-9]+", t.lower())
    towns = {tuple(words(r["city"])) for r in json.loads((REPO / "data/locations.json").read_text(encoding="utf-8"))
             if "(" not in r["city"]} - {("uk",)}
    inside = [(a, b) for a in towns for b in towns if a != b
              and any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1))]
    assert inside == []
