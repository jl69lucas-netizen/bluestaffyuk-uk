# tests/py/test_geo_and_header_keywords.py — family_rules geo-token-missing and
# two-keyword-header (parity build Task 19; CAG §7b geo token rule, §12 two-keyword headers;
# audit rows 7b.9, 7a.8, 12.6). Both are advisory (WARN) on new pages.
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import family_rules as FR  # noqa: E402

CITY_SLUG = "uk-locations/blue-staffy-puppies-manchester-uk"     # data/locations.json: Manchester
NATIONAL_SLUG = "uk-locations/blue-staffy-puppies-uk"             # data/locations.json: UK
GOOD_DESC = ("Home-raised blue Staffy puppies for Manchester families, from our house in "
             "Carlisle, with delivery or collection and first-week support.")


def _board(page_type="location", heading="How We Raise Blue Staffy Puppies for Manchester",
           desc=GOOD_DESC, geo=("manchester",), lsi=("home-raised puppies",),
           slug=CITY_SLUG):
    b = copy.deepcopy(json.loads((ROOT / "data/boards/_demo.json").read_text()))
    b["meta"].update(slug=slug, page_type=page_type, status="boarded")
    b["meta_set"]["descriptions"][0] = desc
    b["meta_set"]["pick"]["description"] = 0
    body = b["sections"][2]                      # how-we-raise: the one body section
    body["heading"] = heading
    body["keywords"]["primary"] = ["blue staffy puppies"]
    body["keywords"]["geo"] = list(geo)
    body["keywords"]["lsi"] = list(lsi)
    return b


def _ours(board, ids=("geo-token-missing", "two-keyword-header")):
    return [f for f in FR.findings(board, ont={}) if f[0] in ids]


def _geo(board):
    return _ours(board, ("geo-token-missing",))


# ── geo-token-missing ───────────────────────────────────────────────────────────────────────
def test_a_location_page_with_geo_in_an_h2_and_the_description_passes():
    assert _ours(_board()) == []


def test_no_geo_term_in_any_body_h2_warns_and_lists_the_h2s_read():
    got = _geo(_board(heading="How We Raise Blue Staffy Puppies"))
    assert [f[:2] for f in got] == [("geo-token-missing", "WARN")]
    assert "H2" in got[0][2] and "Manchester" in got[0][2]
    assert "'How We Raise Blue Staffy Puppies'" in got[0][2]


def test_the_h2_list_in_the_warning_is_truncated():
    b = _board(heading="How We Raise Blue Staffy Puppies " + "and more " * 20)
    msg = _geo(b)[0][2]
    assert "…" in msg and len(msg) < 400


def test_no_geo_term_in_the_picked_description_warns():
    desc = ("Home-raised blue Staffy puppies from our house in Carlisle, with delivery or "
            "collection, first-week support and a written guarantee for every pup.")
    got = _geo(_board(desc=desc))
    assert [f[:2] for f in got] == [("geo-token-missing", "WARN")]
    assert "the picked (or recommended) meta description" in got[0][2]


def test_with_no_pick_the_recommended_description_is_read():
    b = _board()
    b["meta_set"]["pick"]["description"] = None
    b["meta_set"]["recommended"]["description"] = 1
    b["meta_set"]["descriptions"][1] = "Blue Staffy puppies raised indoors, delivered with care."
    got = _geo(b)
    assert [f[:2] for f in got] == [("geo-token-missing", "WARN")]
    assert "description" in got[0][2]
    b["meta_set"]["descriptions"][1] = "Blue Staffy puppies for Manchester, raised indoors."
    assert _geo(b) == []


def test_a_city_page_is_not_satisfied_by_the_brand_or_the_breeders_home():
    b = _board(heading="How Blue Staffy UK Raises Puppies in Carlisle",
               desc="BlueStaffyUK raises blue Staffy puppies at home in Carlisle, Cumbria, "
                    "with delivery, collection and first-week support for every family.",
               geo=("carlisle", "uk"))
    got = _geo(b)
    assert [f[:2] for f in got] == [("geo-token-missing", "WARN")] * 2
    assert all("Manchester" in m for _, _, m in got)
    assert "Carlisle" in got[0][2]           # the home geo is named as not counting


def test_uk_does_not_satisfy_a_city_page():
    b = _board(heading="How We Raise Blue Staffy Puppies in the UK",
               desc=GOOD_DESC.replace("Manchester families", "UK families"))
    assert len(_geo(b)) == 2


def test_uk_counts_on_a_national_page():
    desc = GOOD_DESC.replace("Manchester families", "UK families")
    assert _geo(_board(slug=NATIONAL_SLUG, heading="How We Raise Blue Staffy Puppies in the UK",
                       desc=desc, geo=())) == []


def test_dotted_u_k_counts_as_uk():
    desc = GOOD_DESC.replace("Manchester families", "U.K. families")
    assert _geo(_board(slug=NATIONAL_SLUG, heading="How We Raise Staffy Puppies in the U.K.",
                       desc=desc, geo=())) == []


def test_the_brand_alone_does_not_count_as_uk_on_a_national_page():
    b = _board(slug=NATIONAL_SLUG, heading="How Blue Staffy UK Raises Puppies",
               desc="BlueStaffyUK raises blue Staffy puppies at home, with delivery, "
                    "collection and first-week support for every family we place.", geo=())
    assert len(_geo(b)) == 2


def test_the_geo_rule_binds_location_pages_only():
    assert _geo(_board(page_type="blog", heading="How We Raise Blue Staffy Puppies")) == []


# ── two-keyword-header ──────────────────────────────────────────────────────────────────────
def test_a_body_section_with_one_keyword_type_warns():
    got = _ours(_board(geo=(), lsi=()), ("two-keyword-header",))
    assert [f[:2] for f in got] == [("two-keyword-header", "WARN")]
    assert "how-we-raise" in got[0][2] and "1 keyword type" in got[0][2]


def test_blank_only_type_lists_count_zero():
    got = _ours(_board(geo=(" ",), lsi=("",)), ("two-keyword-header",))
    assert "1 keyword type" in got[0][2]


def test_duplicate_terms_across_types_count_once():
    got = _ours(_board(geo=(), lsi=("Blue Staffy Puppy",)), ("two-keyword-header",))
    assert [f[:2] for f in got] == [("two-keyword-header", "WARN")]
    assert "1 keyword type" in got[0][2]


def test_the_brand_type_is_not_a_header_keyword_type():
    b = _board(geo=(), lsi=())
    b["sections"][2]["keywords"]["brand"] = ["blue staffy uk"]
    got = _ours(b, ("two-keyword-header",))
    assert "1 keyword type" in got[0][2]


def test_a_heading_that_carries_none_of_its_sections_terms_warns():
    got = _ours(_board(heading="Life In Our Kitchen"), ("two-keyword-header",))
    assert [f[:2] for f in got] == [("two-keyword-header", "WARN")]
    assert "carries none" in got[0][2]


def test_the_heading_matches_like_the_title_gate():
    # "Puppy" in the H2 carries the planned "blue staffy puppies"
    assert _ours(_board(heading="Blue Staffy Puppy Care", geo=()), ("two-keyword-header",)) == []


def test_the_header_rule_binds_blog_and_comparison_pages():
    for page_type, slug in (("blog", "blog/new-post"), ("comparison", "blue-vs-red-staffy")):
        got = _ours(_board(page_type=page_type, slug=slug, heading="Life In Our Kitchen"),
                    ("two-keyword-header",))
        assert [f[:2] for f in got] == [("two-keyword-header", "WARN")], page_type


def test_frame_sections_are_not_headers_the_rule_reads():
    b = _board()
    b["sections"][1]["keywords"] = {k: [] for k in b["sections"][1]["keywords"]}   # stats
    assert _ours(b, ("two-keyword-header",)) == []


def test_the_twelve_built_pages_are_never_read():
    b = _board(heading="Life In Our Kitchen", desc="x" * 150)
    b["meta"]["slug"] = "blue-staffy-uk-breeders"
    assert _ours(b) == []
