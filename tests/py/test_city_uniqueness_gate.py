"""Working rule 16 for the city pages: the `city` family and the city pool (Known Issue 60;
the London component design pass, Plan 1 Task 12).

A city page takes all fifteen components from its own component pass. Its picks are saved in
data/design/city-picks/<slug>.json, and the gate refuses a pick that another city wears, one
within one structural axis of another city's pick, or one within one axis of an arrangement a
built page wears. The unpicked variants sit in data/design/city-pool.json.
"""
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import pageboard as PB  # noqa: E402
from city_components import COMPONENT_IDS  # noqa: E402

TS = ROOT / "src" / "lib" / "boardStyles.ts"

AXES = {
    "london/hero/a": {"layout": "ticket", "media": "top", "density": "airy", "framing": "inset"},
    "london/hero/b": {"layout": "postcard", "media": "left", "density": "regular", "framing": "rule"},
    "leeds/hero/a": {"layout": "ticket", "media": "top", "density": "compact", "framing": "inset"},
    "leeds/hero/b": {"layout": "arch", "media": "right", "density": "compact", "framing": "band"},
}


def axes_of(key):
    return AXES.get(key)


def picks_doc(slug, canvas, hero):
    doc = {"slug": slug, "canvas": canvas, "canvas_url": "https://claude.ai/artifact/abc",
           "approved_at": "2026-09-28T10:00:00Z",
           "picks": {c: f"{canvas}/{c}/a" for c in COMPONENT_IDS}}
    doc["picks"]["hero"] = hero
    return doc


def only_hero(findings):
    return [f for f in findings if f["msg"].startswith("hero")]


def test_the_city_family_is_named_on_both_sides():
    src = TS.read_text(encoding="utf-8")
    union = src.split("export type LayoutType =", 1)[1].split(";", 1)[0]
    assert "'city'" in union
    assert re.search(r"^\s*location: 'city',$", src, re.M)
    schema = json.loads((ROOT / "schemas/board.schema.json").read_text(encoding="utf-8"))
    assert "city" in schema["properties"]["meta"]["properties"]["layout_type"]["enum"]
    assert PB.CITY_FAMILY == "city"


def test_the_city_family_cuts_no_hero_or_counter_trio_here():
    """The eighteen per-page defs stay six families × three; a city is not a seventh trio."""
    src = TS.read_text(encoding="utf-8")
    for const in ("HERO_STYLES_BY_PAGE_TYPE", "COUNTER_STYLES_BY_PAGE_TYPE"):
        body = src.split("export const " + const, 1)[1].split("\n};", 1)[0]
        assert "city" not in re.findall(r"^  '?([a-z-]+)'?:\s*\[\s*$", body, re.M)
        assert body.startswith(": Record<PerPageFamily,")


def test_a_hero_another_city_wears_fails():
    picks = {"london": picks_doc("london", "london", "london/hero/a"),
             "leeds": picks_doc("leeds", "london", "london/hero/a")}
    f = only_hero(PB.city_pick_findings("leeds", picks, {}, axes_of))
    assert [(x["check"], x["msg"]) for x in f] == [
        ("city-pick-shared", "hero london/hero/a is already worn by london (working rule 16)")]


def test_a_hero_one_axis_from_another_citys_pick_fails():
    picks = {"london": picks_doc("london", "london", "london/hero/a"),
             "leeds": picks_doc("leeds", "leeds", "leeds/hero/a")}
    f = only_hero(PB.city_pick_findings("leeds", picks, {}, axes_of))
    assert [x["check"] for x in f] == ["city-pick-too-close"], f


def test_a_hero_two_axes_from_every_other_pick_passes():
    picks = {"london": picks_doc("london", "london", "london/hero/a"),
             "leeds": picks_doc("leeds", "leeds", "leeds/hero/b")}
    assert only_hero(PB.city_pick_findings("leeds", picks, {}, axes_of)) == []


def test_a_hero_one_axis_from_a_worn_built_style_fails_and_an_unworn_one_does_not():
    worn = {"id": "H-GD2", "name": "Magazine", "used_by": ["uk-blue-staffy-puppy-buying-guide"],
            "axes": {"layout": "ticket", "media": "top", "density": None, "framing": "card"}}
    unworn = dict(worn, id="H-AB3", used_by=[])
    picks = {"london": picks_doc("london", "london", "london/hero/a")}
    f = only_hero(PB.city_pick_findings("london", picks, {"hero": [worn]}, axes_of))
    assert [x["check"] for x in f] == ["city-pick-matches-built"], f
    assert "worn by uk-blue-staffy-puppy-buying-guide" in f[0]["msg"]
    assert only_hero(PB.city_pick_findings("london", picks, {"hero": [unworn]}, axes_of)) == []


def test_an_unknown_or_misfiled_pick_fails():
    picks = {"london": picks_doc("london", "london", "london/hero/c")}
    assert [x["check"] for x in only_hero(PB.city_pick_findings("london", picks, {}, axes_of))] \
        == ["city-pick-unknown"]
    picks = {"london": picks_doc("london", "london", "london/tables/a")}
    assert [x["check"] for x in only_hero(PB.city_pick_findings("london", picks, {}, axes_of))] \
        == ["city-pick-malformed"]


def test_a_pool_entry_a_city_picked_fails():
    picks = {"london": picks_doc("london", "london", "london/hero/a")}
    pool = {"available": {c: [] for c in COMPONENT_IDS}}
    pool["available"]["hero"] = ["london/hero/a", "london/hero/b"]
    f = PB.city_pool_findings(pool, picks, axes_of)
    assert [(x["check"], x["msg"]) for x in f] == [
        ("city-pool-picked", "hero: london/hero/a is in the pool and picked by london")]


def _city_board(slug="uk-locations/london"):
    return {"meta": {"slug": slug, "layout_type": "city", "status": "approved"}, "sections": []}


def test_a_city_board_is_judged_by_its_picks_file():
    picks = {"london": picks_doc("london", "london", "london/hero/a"),
             "leeds": picks_doc("leeds", "london", "london/hero/a")}
    pool = {"available": {c: [] for c in COMPONENT_IDS}}
    f = PB.city_rule16_findings(_city_board("uk-locations/leeds"), picks=picks, pool=pool,
                                must_differ={}, axes_of=axes_of)
    assert "city-pick-shared" in [x["check"] for x in f]


def test_a_city_board_without_a_picks_file_fails_and_other_families_are_untouched():
    f = PB.city_rule16_findings(_city_board(), picks={}, pool={"available": {}},
                                must_differ={}, axes_of=axes_of)
    assert [x["check"] for x in f] == ["city-picks-missing"]
    guide = {"meta": {"slug": "x", "layout_type": "interior-guide", "status": "approved"}, "sections": []}
    assert PB.city_rule16_findings(guide, picks={}, pool={}, must_differ={}, axes_of=axes_of) == []


def test_rule16_findings_carries_the_city_findings(monkeypatch):
    monkeypatch.setattr(PB, "load_city_picks", lambda folder=None: {})
    f = PB.rule16_findings(_city_board(), {})
    assert [x["check"] for x in f] == ["city-picks-missing"]


def test_the_picks_schema_refuses_a_missing_or_unknown_component():
    doc = picks_doc("london", "london", "london/hero/a")
    PB._validate(doc, "city-picks.schema.json")
    bad = json.loads(json.dumps(doc))
    del bad["picks"]["newsletter"]
    with pytest.raises(PB.BoardError):
        PB._validate(bad, "city-picks.schema.json")
    bad = json.loads(json.dumps(doc))
    bad["picks"]["carousel"] = "london/carousel/a"
    with pytest.raises(PB.BoardError):
        PB._validate(bad, "city-picks.schema.json")


def test_the_schemas_name_the_fifteen_components():
    for name, path in (("city-picks.schema.json", ("properties", "picks")),
                       ("city-pool.schema.json", ("properties", "available"))):
        node = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
        for k in path:
            node = node[k]
        assert node["required"] == list(COMPONENT_IDS) == node["propertyNames"]["enum"], name


def test_the_real_pool_and_picks_validate_and_pass():
    picks = PB.load_city_picks()
    pool = PB.load_city_pool()
    assert sorted(pool["available"]) == sorted(COMPONENT_IDS)
    assert PB.city_pool_findings(pool, picks, PB.canvas_axes) == []
    md = json.loads(PB.CITY_MUST_DIFFER.read_text(encoding="utf-8"))["components"]
    for slug in picks:
        assert PB.city_pick_findings(slug, picks, md, PB.canvas_axes) == [], slug
