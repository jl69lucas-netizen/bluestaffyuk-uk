"""Board block 3d: the London areas the page could name, and their keywords, from data only."""
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import neighbourhoods as NB  # noqa: E402

SLUG = "blue-staffy-puppies-x"


def _board(slug=SLUG, research="docs/research/x-page-run/keyword-variants.json"):
    return {"meta": {"slug": slug, "page_type": "location",
                     "sources": [{"path": research, "fetched": "2026-09-30"}]}}


def _items(rows):
    return {"status_code": 20000, "total_count": len(rows),
            "items": [{"keyword": k, "keyword_info": {"search_volume": v}} for k, v in rows]}


def _write(root, rel, doc):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc), encoding="utf-8")


RESPONSE_ROWS = [
    ("staffy puppies for sale london", 320),
    ("staffies for sale london", 320),
    ("blue staffy puppies for sale london", 40),
    ("staffy puppies for sale in enfield", 10),
    ("staffy puppies for sale sutton surrey", 10),
    ("staffy pups for sale croydon", None),
    ("staffordshire puppys in croydon", None),
    ("staffy pups in east london", None),
    ("blue staffy puppies for sale south east london", None),
    ("staff puppies for sale bromley", None),
    ("staffordshire bull terriers puppies for sale in camden nw1", None),
    ("staffy barking", 50),
    ("staffordshire bull terrier barking", 50),
    ("staffy puppies for sale in barking", None),
    ("staffordshire bull terrier westminster 2022", 10),
    ("staffy for sale sutton in ashfield", None),
    ("english bull terrier for sale london", 50),
    ("bull terrier puppies for sale croydon", None),
    ("american staffy barking", 10),
    ("staffordshire bull terrier for sale near brentwood", None),
    ("how to stop staffy barking", None),
]


@pytest.fixture
def root(tmp_path):
    raw = f"data/queries/raw/{SLUG}"
    _write(tmp_path, f"{raw}/neighbourhood_keywords.response.json", _items(RESPONSE_ROWS))
    _write(tmp_path, f"{raw}/serp_google.json", {"results": [
        {"url": "https://www.staffie-owners.co.uk/staffies-for-sale/barnet-london"},
        {"url": "https://www.staffie-owners.co.uk/staffies-for-sale/camden-town-london?colour=blue"},
        {"url": "https://www.tiktok.com/@puppyyogaclublondon/video/1"}]})
    _write(tmp_path, f"{raw}/competitors.json", {"pages": [
        {"url": "https://www.staffie-owners.co.uk/staffies-for-sale/uxbridge-london?colour=blue",
         "metrics": {"title": "Blue Staffordshire Bull Terrier puppies for sale in Uxbridge, London"}}]})
    _write(tmp_path, "docs/research/x-page-run/keyword-variants.json", {"buckets": {"related": [
        {"term": "staffy puppies peckham"}, {"term": "staffy puppies, peckham"}]}})
    _write(tmp_path, "docs/research/x-page-run/keyword-universe.json", {"universe": [
        {"keyword": "blue staffy puppies london", "volume": "NOT FETCHED — x"}]})
    return tmp_path


def _by_area(rows):
    return {r["area"]: r for r in rows}


# ── the gazetteer ─────────────────────────────────────────────────────────────────────────

def test_gazetteer_carries_the_32_boroughs_and_the_city():
    assert len(NB.BOROUGHS) == 32
    for b in ("Barking and Dagenham", "Croydon", "Enfield", "Sutton", "Westminster",
              "Kingston upon Thames", "Tower Hamlets", "Waltham Forest"):
        assert b in NB.BOROUGHS
    assert NB.lookup("staffy puppies city of london") == [("City of London", "City of London")]


def test_compass_areas_match_longest_first():
    assert NB.lookup("blue staffy puppies south east london") == [
        ("South East London", NB.COMPASS_BOROUGH)]
    assert NB.lookup("staffy pups in east london") == [("East London", NB.COMPASS_BOROUGH)]
    for c in ("north", "south", "east", "west", "central", "south east", "south west",
              "north east", "north west"):
        assert f"{c} london" in NB.COMPASS


@pytest.mark.parametrize("district,borough", [
    ("croydon", "Croydon"), ("enfield", "Enfield"), ("sutton", "Sutton"),
    ("romford", "Havering"), ("ilford", "Redbridge"), ("walthamstow", "Waltham Forest"),
    ("uxbridge", "Hillingdon"), ("camden town", "Camden"), ("brixton", "Lambeth"),
    ("peckham", "Southwark"), ("tottenham", "Haringey"), ("wimbledon", "Merton"),
    ("stratford", "Newham"), ("woolwich", "Greenwich"), ("catford", "Lewisham"),
    ("edmonton", "Enfield"), ("dagenham", "Barking and Dagenham"),
    ("southall", "Ealing"), ("paddington", "Westminster"),
])
def test_districts_map_to_their_borough(district, borough):
    hits = NB.lookup(f"staffy puppies for sale in {district}")
    assert len(hits) == 1 and hits[0][1] == borough, hits


def test_barking_counts_only_as_a_place():
    assert NB.lookup("staffy puppies for sale in barking") == [("Barking", "Barking and Dagenham")]
    assert NB.lookup("staffy barking") == []
    assert NB.lookup("staffordshire bull terrier barking") == []
    assert NB.lookup("how to stop staffy barking") == []


def test_westminster_dog_show_and_sutton_in_ashfield_are_not_london():
    assert NB.lookup("staffordshire bull terrier westminster 2022") == []
    assert NB.lookup("staffy for sale sutton in ashfield") == []
    assert NB.lookup("staffy puppies for sale sutton surrey") == [("Sutton", "Sutton")]


def test_only_staffy_phrases_count():
    for kw in ("staffy pups for sale croydon", "staffordshire puppys in croydon",
               "staff puppies for sale bromley", "staffies for sale london",
               "staffordshire bull terriers for sale in croydon"):
        assert NB.is_staffy(kw), kw
    for kw in ("bull terrier puppies for sale croydon", "english bull terrier for sale london",
               "american staffy barking", "american pit bull terrier barking"):
        assert not NB.is_staffy(kw), kw


# ── areas() ───────────────────────────────────────────────────────────────────────────────

def test_areas_take_volumes_from_the_response_file_only(root):
    rows = _by_area(NB.areas(_board(), root))
    assert rows["Enfield"]["keywords"] == [{"kw": "staffy puppies for sale in enfield", "volume": 10}]
    assert rows["Enfield"]["total_volume"] == 10
    assert rows["Sutton"]["total_volume"] == 10
    croydon = rows["Croydon"]
    assert {k["kw"] for k in croydon["keywords"]} == {
        "staffy pups for sale croydon", "staffordshire puppys in croydon"}
    assert all(k["volume"] is None for k in croydon["keywords"])
    assert croydon["total_volume"] is None
    assert rows["Camden"]["borough"] == "Camden"


def test_excluded_phrases_never_make_a_row(root):
    rows = _by_area(NB.areas(_board(), root))
    assert set(rows["Barking"]["keywords"][i]["kw"] for i in range(len(rows["Barking"]["keywords"]))) == {
        "staffy puppies for sale in barking"}
    assert "Westminster" not in rows
    all_kws = {k["kw"] for r in rows.values() for k in r["keywords"]}
    assert "bull terrier puppies for sale croydon" not in all_kws
    assert "staffy for sale sutton in ashfield" not in all_kws


def test_serp_and_competitor_areas_are_seen_with_no_volume(root):
    rows = _by_area(NB.areas(_board(), root))
    barnet = rows["Barnet"]
    assert barnet["keywords"] == [] and barnet["total_volume"] is None
    assert "https://www.staffie-owners.co.uk/staffies-for-sale/barnet-london" in barnet["seen_in"]
    camden_town = rows["Camden Town"]
    assert camden_town["borough"] == "Camden"
    assert any("camden-town-london" in s for s in camden_town["seen_in"])
    assert any("uxbridge-london" in s for s in rows["Uxbridge"]["seen_in"])
    # A keyword-list phrase not in the keyword data carries the barrier, never a number.
    peckham = rows["Peckham"]
    assert peckham["keywords"] == [{"kw": "staffy puppies peckham", "volume": NB.NOT_IN_DATA}]
    assert peckham["total_volume"] is None
    assert "docs/research/x-page-run/keyword-variants.json" in peckham["seen_in"]


def test_keyword_data_is_named_as_a_source(root):
    rows = _by_area(NB.areas(_board(), root))
    assert NB.KEYWORD_SOURCE in rows["Enfield"]["seen_in"]


def test_rows_sort_by_volume_then_name(root):
    rows = NB.areas(_board(), root)
    assert [r["area"] for r in rows[:2]] == ["Enfield", "Sutton"]


def test_missing_response_file_is_not_fetched(root):
    (root / f"data/queries/raw/{SLUG}/neighbourhood_keywords.response.json").unlink()
    rows = _by_area(NB.areas(_board(), root))
    assert "Enfield" not in rows
    assert rows["Barnet"]["total_volume"] is None
    out = NB.block(_board(), root)
    assert "NOT FETCHED" in out


# ── suggested use and block() ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("vol,use", [(50, "h3"), (120, "h3"), (49, "faq"), (10, "faq"),
                                     (9, "line"), (0, "line"), (None, "line")])
def test_suggested_use_is_mechanical(vol, use):
    assert NB.use_of(vol) == use


def test_block_renders_the_table_target_and_not_shown(root):
    out = NB.block(_board(), root)
    assert "| Area | Borough | Keywords found | Monthly searches | Where seen | Suggested use |" in out
    assert "DataForSEO" in out and "2026-10-03" in out
    assert "London as a whole" in out and "staffy puppies for sale london" in out and "320" in out
    assert "≥ 50/mo" in out and "10–49" in out
    target = [ln for ln in out.splitlines() if ln.startswith("**Target")]
    assert len(target) == 1
    assert "Enfield" in target[0] and "Sutton" in target[0]
    assert "London-wide" in target[0]
    not_shown = [ln for ln in out.splitlines() if ln.startswith("**Not shown")]
    assert len(not_shown) == 1
    for phrase in ("staffy barking", "staffordshire bull terrier westminster 2022",
                   "staffy for sale sutton in ashfield", "bull terrier puppies for sale croydon"):
        assert phrase in not_shown[0], phrase
    assert "Nottinghamshire" in not_shown[0] and "dog show" in not_shown[0]
    assert NB.NOT_IN_DATA in out


def test_block_has_no_invented_volume(root):
    out = NB.block(_board(), root)
    for row in [ln for ln in out.splitlines() if ln.startswith("| Barnet")]:
        assert NB.NOT_IN_DATA in row


def test_cli_usage_exits_2(capsys):
    assert NB.main([]) == 2
    assert "usage" in capsys.readouterr().err
    assert NB.main(["no-such-board-slug"]) == 2
