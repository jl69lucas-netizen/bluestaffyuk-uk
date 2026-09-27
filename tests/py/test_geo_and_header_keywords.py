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

GOOD_DESC = ("Home-raised blue Staffy puppies for Manchester families, from our house in "
             "Carlisle, with delivery or collection and first-week support.")


def _board(page_type="location", heading="How We Raise Blue Staffy Puppies for Manchester",
           desc=GOOD_DESC, geo=("manchester",), lsi=("home-raised puppies",)):
    b = copy.deepcopy(json.loads((ROOT / "data/boards/_demo.json").read_text()))
    b["meta"].update(slug="blue-staffy-puppies-testcity", page_type=page_type, status="boarded")
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


def test_a_location_page_with_geo_in_an_h2_and_the_description_passes():
    assert _ours(_board()) == []


def test_no_geo_term_in_any_body_h2_warns():
    got = _ours(_board(heading="How We Raise Blue Staffy Puppies"), ("geo-token-missing",))
    assert [f[:2] for f in got] == [("geo-token-missing", "WARN")]
    assert "H2" in got[0][2] and "manchester" in got[0][2]


def test_no_geo_term_in_the_picked_description_warns():
    desc = ("Home-raised blue Staffy puppies from our house in Carlisle, with delivery or "
            "collection, first-week support and a written guarantee for every pup.")
    got = _ours(_board(desc=desc), ("geo-token-missing",))
    assert [f[:2] for f in got] == [("geo-token-missing", "WARN")]
    assert "description" in got[0][2]


def test_uk_counts_as_a_geo_token():
    desc = GOOD_DESC.replace("Manchester families", "UK families")
    assert _ours(_board(heading="How We Raise Blue Staffy Puppies in the UK", desc=desc,
                        geo=()), ("geo-token-missing",)) == []


def test_the_geo_rule_binds_location_pages_only():
    assert _ours(_board(page_type="blog", heading="How We Raise Blue Staffy Puppies"),
                 ("geo-token-missing",)) == []


def test_a_body_section_with_one_keyword_type_warns():
    got = _ours(_board(geo=(), lsi=()), ("two-keyword-header",))
    assert [f[:2] for f in got] == [("two-keyword-header", "WARN")]
    assert "how-we-raise" in got[0][2] and "1 keyword type" in got[0][2]


def test_a_heading_that_carries_none_of_its_sections_terms_warns():
    got = _ours(_board(heading="Life In Our Kitchen"), ("two-keyword-header",))
    assert [f[:2] for f in got] == [("two-keyword-header", "WARN")]
    assert "carries none" in got[0][2]


def test_frame_sections_are_not_headers_the_rule_reads():
    b = _board()
    b["sections"][1]["keywords"] = {k: [] for k in b["sections"][1]["keywords"]}   # stats
    assert _ours(b, ("two-keyword-header",)) == []


def test_the_twelve_built_pages_are_never_read():
    b = _board(heading="Life In Our Kitchen", desc="x" * 150)
    b["meta"]["slug"] = "blue-staffy-uk-breeders"
    assert _ours(b) == []
