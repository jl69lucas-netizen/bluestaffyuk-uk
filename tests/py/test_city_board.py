"""A CITY page's board (meta.layout_type "city"): its components were picked in the city's
component design pass (data/design/city-picks/<slug>.json) and the City kit takes no style
prop, so (1) approval keeps the city tuple instead of deriving generic kit shells from S1–S3
picks, (2) no section owes a `signature-no-pick` answer, and (3) a same-page link may be a
bare fragment that names a section of the record. London is the first such board.
"""
import copy
import json
import pathlib
import sys

import jsonschema
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import pageboard as PB  # noqa: E402
import board_approve as BA  # noqa: E402
import build_page_board as BPB  # noqa: E402
from city_components import KIT_OF_VARIANT  # noqa: E402

LONDON = "blue-staffy-puppies-london"
SCHEMA = json.loads((ROOT / "schemas/board.schema.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def london():
    return PB.load_board(LONDON)


def _expected_city_tuple():
    picks = PB.load_city_picks()[LONDON]["picks"]
    return {"hero": KIT_OF_VARIANT[picks["hero"]], "dial": KIT_OF_VARIANT[picks["desktop-dial"]],
            "rail": "", "toc": KIT_OF_VARIANT[picks["contents-list"]],
            "table": KIT_OF_VARIANT[picks["tables"]], "faq": KIT_OF_VARIANT[picks["faq-blocks"]],
            "stepper": KIT_OF_VARIANT[picks["jump-links"]],
            "takeaway": [KIT_OF_VARIANT[picks["key-takeaways"]]]}


def _inbox(board):
    return {"record_hash": PB.record_hash(board), "approved_at": "2026-09-30T00:00:00Z",
            "h1": 0, "meta": {"title": 0, "description": 0}, "notes": {},
            "canvas_version": None,
            "picks": {**{"img:" + i["slot"]: "ig:" + i["infographic_style"]
                         for _, _, i in BA.IR.IC.iter_slots(board)
                         if i.get("source") == "infographic"},
                      # board v2 block 7c: every required infographic slot needs a style
                      **{sid: "plate" for sid in PB.ig_slots_required(board)}}}


def test_a_city_board_approves_with_its_city_tuple_intact(london):
    out = BA.apply_approval(london, _inbox(london), PB.load_ontology(), PB.load_ledger())
    t = out["board"]["tuple"]
    want = _expected_city_tuple()
    for k, v in want.items():
        assert t[k] == v, (k, t[k], v)
    assert t["toc"] != BA.FIXED_TOC
    row = out["ledger"]["pages"][LONDON]
    assert {k: row[k] for k in ("hero", "dial", "rail", "toc", "table", "faq", "takeaway")} == \
        {k: want[k] for k in ("hero", "dial", "rail", "toc", "table", "faq", "takeaway")}
    # The authored tuple already IS the city tuple, so approval changed nothing on it.
    assert out["board"]["approval"]["tuple_before"] == london["tuple"] == t


def test_a_non_city_board_still_derives_its_tuple_from_the_picks():
    b = PB.load_board("index")
    base = b["approval"]["tuple_before"]
    assert not BA.is_city(b)
    assert BA.tuple_for(b, base) == BA.derive_tuple(b, base)
    assert BA.tuple_for(b, base)["toc"] == BA.FIXED_TOC


def test_city_tuple_refuses_a_city_with_no_picks(london):
    b = copy.deepcopy(london)
    b["meta"]["slug"] = "blue-staffy-puppies-nowhere"
    with pytest.raises(PB.BoardError, match="city-picks"):
        BA.city_tuple(b, b["tuple"])


def test_signature_no_pick_is_not_raised_for_city_sections(london):
    f = PB.gate_findings(london, PB.load_ontology(), PB.load_ledger(), {})
    assert not [x for x in f if x["check"] == "signature-no-pick"]
    # …and still is for a kit-shaped section that names no component and has no pick.
    b = copy.deepcopy(london)
    hero = next(s for s in b["sections"] if s["shape"] == "hero")
    del hero["component"]
    f = PB.gate_findings(b, PB.load_ontology(), PB.load_ledger(), {})
    assert [x for x in f if x["check"] == "signature-no-pick" and hero["id"] in x["msg"]]


def test_the_board_offers_no_style_trio_for_a_city_section(london):
    kit = [s for s in london["sections"] if s["shape"] != "standard"]
    assert kit and all(s.get("component") and not s.get("styles") for s in kit)
    assert BPB.picked_sections(london, PB.load_ledger(), LONDON) == []


def test_schema_exempts_only_a_section_that_names_its_component(london):
    b = copy.deepcopy(london)
    jsonschema.validate(b, SCHEMA)
    hero = next(s for s in b["sections"] if s["shape"] == "hero")
    del hero["component"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(b, SCHEMA)


def test_a_bare_same_page_fragment_is_allowed_and_must_name_a_section(london):
    hrefs = [l["href"] for s in london["sections"] for l in s["links"]["internal"]]
    assert hrefs.count("#enquiry") == 4 and "#health-tests" in hrefs
    b = copy.deepcopy(london)
    link = next(l for s in b["sections"] for l in s["links"]["internal"] if l["href"] == "#enquiry")
    link["href"] = "#Not A Fragment"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(b, SCHEMA)
    link["href"] = "#nowhere"
    jsonschema.validate(b, SCHEMA)
    f = PB.gate_findings(b, PB.load_ontology(), PB.load_ledger(), {})
    assert [x for x in f if x["check"] == "links-fragment-dead" and "#nowhere" in x["msg"]]
    f = PB.gate_findings(london, PB.load_ontology(), PB.load_ledger(), {})
    assert not [x for x in f if x["check"] == "links-fragment-dead"]
