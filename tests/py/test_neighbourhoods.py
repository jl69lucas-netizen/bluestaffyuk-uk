"""Board block 3d: the London areas the page could name, and their keywords, from data only."""
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import neighbourhoods as NB  # noqa: E402

SLUG = "blue-staffy-puppies-x"
UNIVERSE_BARRIER = ("NOT FETCHED — the DataForSEO Google Ads search-volume call (UK, en, 2026-09-30) "
                    "was sent this keyword but its response listed only the first 10 of 30")


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
    ("staffies for sale barking", None),
    ("staffy puppy barking", None),
    ("staffy barking #sounds", 10),
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
    _write(tmp_path, f"{raw}/neighbourhood_keywords.request.json", {"fetched": "2026-10-03"})
    _write(tmp_path, "docs/research/x-page-run/keyword-variants.json", {"buckets": {
        "related": [{"term": "staffy puppies peckham", "sources": ["serp_google_related"]},
                    {"term": "staffy puppies, peckham", "sources": ["serp_google_related"]}],
        "similar": [{"term": "staffie puppies for sale in barnet, london", "sources": ["organic_title"]},
                    {"term": "male (dog) blue staffie puppies for sale in southall, london",
                     "sources": ["competitor_h2"]}]}})
    _write(tmp_path, "docs/research/x-page-run/keyword-universe.json", {"universe": [
        {"keyword": "blue staffy puppies london", "volume": "NOT FETCHED — x"},
        {"keyword": "staffie puppies for sale in barnet london", "volume": UNIVERSE_BARRIER,
         "source": "keyword variants (similar: how the ranking pages word the query)"}]})
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
    place = [("Barking", "Barking and Dagenham")]
    for kw in ("staffy puppies for sale in barking", "staffy puppies for sale barking",
               "staffies for sale barking", "staffy puppies barking", "staffy pups barking",
               "staffy puppies near barking"):
        assert NB.lookup(kw) == place, kw
    for kw in ("staffy puppy barking", "blue staffy barking", "staffy barking #sounds",
               "staffy puppies for sale barking sounds", "how to stop staffy puppies barking"):
        assert NB.lookup(kw) == [], kw
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
    assert {k["kw"] for k in rows["Barking"]["keywords"]} == {
        "staffy puppies for sale in barking", "staffies for sale barking"}
    assert "Westminster" not in rows
    all_kws = {k["kw"] for r in rows.values() for k in r["keywords"]}
    assert "bull terrier puppies for sale croydon" not in all_kws
    assert "staffy for sale sutton in ashfield" not in all_kws


def test_serp_and_competitor_areas_are_seen_with_no_volume(root):
    rows = _by_area(NB.areas(_board(), root))
    barnet = rows["Barnet"]
    assert barnet["keywords"] == [] and barnet["total_volume"] is None
    # The ranking pages' wording is a competitor heading, never a keyword found, and it keeps
    # its own recorded barrier, merged across both list files.
    assert barnet["headings"] == [{
        "heading": "staffie puppies for sale in barnet london",
        "sources": ["keyword-universe.json: keyword variants (similar: how the ranking pages word the query)",
                    "keyword-variants.json: organic_title"],
        "volume": UNIVERSE_BARRIER}]
    southall = rows["Southall"]
    assert southall["keywords"] == []
    assert southall["headings"][0]["sources"] == ["keyword-variants.json: competitor_h2"]
    assert southall["headings"][0]["volume"].startswith("NOT FETCHED — keyword-variants.json")
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


def test_fetch_date_comes_from_the_sidecar(root):
    (root / f"data/queries/raw/{SLUG}/neighbourhood_keywords.request.json").unlink()
    assert NB.keyword_data(_board(), root)["fetched"] == NB.NO_SIDECAR
    assert "fetched NOT FETCHED" in NB.block(_board(), root)


@pytest.mark.parametrize("kw,hit", [
    ("staffy puppies for sale richmond london", [("Richmond", "Richmond upon Thames")]),
    ("staffy puppies kingston surrey", [("Kingston", "Kingston upon Thames")]),
    ("staffy puppies kingston upon thames", [("Kingston upon Thames", "Kingston upon Thames")]),
    ("staffy puppies richmond upon thames", [("Richmond upon Thames", "Richmond upon Thames")]),
    ("staffy puppies for sale richmond", []),
    ("staffy puppies kingston", []),
])
def test_richmond_and_kingston_need_london_or_surrey(kw, hit):
    assert NB.lookup(kw) == hit


def test_target_line_is_its_own_builder():
    rows = [{"area": "A", "total_volume": 60}, {"area": "B", "total_volume": 12},
            {"area": "C", "total_volume": None}]
    t = NB.target_line(rows, [("staffy puppies for sale london", 320)])
    assert t.startswith("**Target:** give A its own H3.")
    assert "Name B in the delivery section copy" in t and "C show no measurable volume" in t
    assert "320/mo against 60/mo" in t


def test_malformed_board_exits_2(tmp_path, monkeypatch, capsys):
    (tmp_path / "data/boards").mkdir(parents=True)
    (tmp_path / "data/boards/bad.json").write_text("{not json", encoding="utf-8")
    (tmp_path / "data/boards/nometa.json").write_text("[]", encoding="utf-8")
    monkeypatch.setattr(NB, "ROOT", tmp_path)
    assert NB.main(["bad"]) == 2
    assert NB.main(["nometa"]) == 2
    assert "usage" in capsys.readouterr().err


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
    assert ("| Area | Borough | Keywords found | Competitor headings | Monthly searches | Where seen "
            "| Suggested use |") in out
    assert "DataForSEO" in out and "fetched 2026-10-03" in out
    assert f"{len(RESPONSE_ROWS)} of {len(RESPONSE_ROWS)} rows held (DataForSEO total_count)" in out
    barnet = [ln for ln in out.splitlines() if ln.startswith("| Barnet")][0]
    cells = [c.strip() for c in barnet.strip("|").split(" | ")]
    assert cells[2] == "—"
    assert "staffie puppies for sale in barnet london" in cells[3] and UNIVERSE_BARRIER in cells[3]
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


# ── Task 20 (G6): one gazetteer per city, chosen by the board's own city ──────────────────
import hashlib  # noqa: E402
import re  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
MAN_SLUG = "blue-staffy-puppies-manchester-uk"
SIGNALS = REPO / "docs/research/manchester-page-run/free-keyword-signals.json"
MAN = "Manchester"


def _man_board():
    return {"meta": {"slug": MAN_SLUG, "page_type": "location", "sources": [
        {"path": "docs/research/manchester-page-run/keyword-variants.json", "fetched": "2026-10-07"}]}}


def _planner_ranges():
    doc = json.loads(SIGNALS.read_text(encoding="utf-8"))
    return {r["keyword"]: r["avg_monthly_searches_range"]
            for run in doc["keyword_planner"]["runs"] for r in run["rows"]}


def test_greater_manchester_gazetteer_holds_the_ten_boroughs():
    gm = NB.GAZETTEERS[MAN]
    assert set(gm.boroughs) == {"Bolton", "Bury", "Oldham", "Rochdale", "Salford", "Stockport",
                                "Tameside", "Trafford", "Wigan"}
    assert gm.city_area == "City of Manchester"
    assert len(gm.boroughs) + 1 == 10
    assert gm.region == "Greater Manchester"
    assert NB.lookup("staffy puppies city of manchester", MAN) == [
        ("City of Manchester", "City of Manchester")]
    assert NB.lookup("staffy puppies manchester city centre", MAN) == [
        ("Manchester City Centre", "City of Manchester")]


def test_gazetteers_hold_names_only_never_volumes():
    for gaz in NB.GAZETTEERS.values():
        for name, (area, borough) in gaz.names.items():
            assert isinstance(name, str) and isinstance(area, str) and isinstance(borough, str)
            assert not re.search(r"\d", name + area + borough), (name, area, borough)


def test_bare_manchester_is_never_an_area():
    for kw in ("staffy puppies manchester", "staffy puppies for sale manchester",
               "staffy puppies for sale greater manchester", "blue staffy manchester uk"):
        assert NB.lookup(kw, MAN) == [], kw


def test_sale_is_the_town_only_after_a_location_word():
    assert NB.lookup("staffy puppies for sale manchester", MAN) == []
    assert NB.lookup("staffy puppies for sale", MAN) == []
    assert NB.lookup("staffy puppies sale near me", MAN) == []
    for kw in ("staffy puppies for sale in sale", "staffy puppies near sale",
               "staffy pups around sale", "staffy puppies delivered to sale"):
        assert NB.lookup(kw, MAN) == [("Sale", "Trafford")], kw


def test_bury_is_a_place_only_after_a_location_word_or_beside_manchester():
    for kw in ("staffy puppies for sale near bury", "staffy puppies in bury",
               "staffy puppies bury manchester", "staffy puppies bury greater manchester",
               "staffy puppies manchester bury"):
        assert NB.lookup(kw, MAN) == [("Bury", "Bury")], kw
    for kw in ("staffy puppies bury", "staffy puppies for sale bury", "staffy puppies bury a bone",
               "staffy puppies for sale near bury st edmunds bury saint edmunds"):
        assert NB.lookup(kw, MAN) == [], kw
    assert "Suffolk" in NB.exclusion_reason(
        "staffy puppies for sale near bury st edmunds bury saint edmunds", MAN)
    assert NB.exclusion_reason("staffy puppies bury", MAN) == NB.GAZETTEERS[MAN].reasons["bury"]


def test_leigh_on_sea_is_outside_greater_manchester():
    assert NB.lookup("staffy puppies for sale leigh-on-sea", MAN) == []
    assert "Essex" in NB.exclusion_reason("staffy puppies for sale leigh-on-sea", MAN)
    assert NB.lookup("staffy puppies for sale in leigh", MAN) == [("Leigh", "Wigan")]


@pytest.mark.parametrize("district,borough", [
    ("altrincham", "Trafford"), ("sale", "Trafford"), ("stretford", "Trafford"),
    ("stalybridge", "Tameside"), ("ashton-under-lyne", "Tameside"), ("cheadle", "Stockport"),
    ("eccles", "Salford"), ("wythenshawe", "City of Manchester"),
    ("didsbury", "City of Manchester"), ("leigh", "Wigan"), ("prestwich", "Bury"),
])
def test_greater_manchester_districts_map_to_their_borough(district, borough):
    hits = NB.lookup(f"staffy puppies for sale in {district}", MAN)
    assert len(hits) == 1 and hits[0][1] == borough, hits


def test_the_district_map_is_pinned():
    assert NB.GAZETTEERS[MAN].districts == {
        "Altrincham": "Trafford", "Sale": "Trafford", "Stretford": "Trafford",
        "Stalybridge": "Tameside", "Ashton-under-Lyne": "Tameside", "Cheadle": "Stockport",
        "Eccles": "Salford", "Swinton": "Salford", "Wythenshawe": "City of Manchester",
        "Didsbury": "City of Manchester", "Leigh": "Wigan", "Prestwich": "Bury"}


def test_swinton_needs_manchester_or_salford_in_the_phrase():
    assert NB.lookup("staffy puppies for sale near swinton manchester", MAN) == [
        ("Swinton", "Salford")]
    assert NB.lookup("staffy puppies for sale swinton", MAN) == []


def test_compass_areas_of_manchester():
    assert NB.lookup("staffy pups south manchester", MAN) == [("South Manchester", NB.COMPASS_BOROUGH)]
    assert NB.lookup("staffy pups north manchester", MAN) == [("North Manchester", NB.COMPASS_BOROUGH)]


def test_the_two_gazetteers_do_not_leak():
    assert NB.lookup("staffy puppies for sale in wigan") == []          # London is the default
    assert NB.lookup("staffy puppies for sale in croydon", MAN) == []


def test_the_gazetteer_is_chosen_by_the_boards_own_city():
    assert NB.gazetteer_for(_man_board()) is NB.GAZETTEERS[MAN]
    london = json.loads((REPO / "data/boards/blue-staffy-puppies-london.json").read_text(encoding="utf-8"))
    assert NB.gazetteer_for(london) is NB.GAZETTEERS["London"]
    assert NB.gazetteer_for(_board()) is NB.GAZETTEERS["London"]          # no locations row
    glasgow = {"meta": {"slug": "staffy-puppies-for-sale-glasgow", "page_type": "location"}}
    assert NB.gazetteer_for(glasgow) is None


def test_a_city_with_no_gazetteer_shows_no_other_citys_areas():
    out = NB.block({"meta": {"slug": "staffy-puppies-for-sale-glasgow", "page_type": "location"}})
    assert "NOT FETCHED" in out and "Glasgow" in out
    assert "London" not in out and "borough" not in out


# ── Task 20 (G6): Planner ranges and autocomplete ─────────────────────────────────────────

@pytest.mark.parametrize("rng,low,use", [("100 – 1K", 100, "h3"), ("10 – 100", 10, "faq"),
                                         ("0 – 10", 0, "line"), ("1K – 10K", 1000, "h3")])
def test_a_planner_range_is_kept_as_recorded_and_the_use_rule_reads_its_lower_bound(rng, low, use):
    r = NB.Range(rng)
    assert str(r) == rng and r.low == low
    assert NB.use_of(r) == use


def test_manchester_volumes_come_from_the_planner_rows_as_recorded():
    kd = NB.keyword_data(_man_board())
    planner = _planner_ranges()
    got = {kw: v for kw, v in kd["rows"] if isinstance(v, NB.Range)}
    assert got == {kw.lower(): rng for kw, rng in planner.items()}
    assert kd["fetched"] == "2026-10-07"
    ac = {kw for kw, v in kd["rows"] if v == NB.ATTESTED}
    assert "staffy puppies for sale near wythenshawe manchester" in ac
    assert not ac & set(got)                     # a Planner row is never re-listed as autocomplete


def test_manchester_block_shows_ranges_never_narrowed():
    out = NB.block(_man_board())
    recorded = set(_planner_ranges().values())
    shown = set(re.findall(r"\b\d+K? – \d+K?\b", out))
    assert shown and shown <= recorded
    assert "| staffy puppies for sale manchester | 100 – 1K |" in out
    wigan = [ln for ln in out.splitlines() if ln.startswith("| Wigan |")][0]
    assert "staffy puppies for sale wigan (10 – 100)" in wigan
    assert "| 10 – 100 |" in wigan and "Delivery copy + one FAQ answer" in wigan
    salford = [ln for ln in out.splitlines() if ln.startswith("| Salford |")][0]
    assert "staffy puppies salford (0 – 10)" in salford and "if at all" in salford
    assert "lower bound" in out


def test_manchester_autocomplete_is_attested_with_no_volume():
    out = NB.block(_man_board())
    wy = [ln for ln in out.splitlines() if ln.startswith("| Wythenshawe |")][0]
    assert "staffy puppies for sale near wythenshawe manchester (attested, no volume)" in wy
    assert "City of Manchester" in wy and "autocomplete" in wy
    assert "attested, no volume" in out


def test_manchester_block_names_greater_manchester_never_london():
    out = NB.block(_man_board())
    assert "Greater Manchester" in out
    assert "London" not in out
    assert "**Manchester as a whole**" in out
    assert "We deliver across Greater Manchester, including" in out
    assert "Sale, Trafford" in out and "NOT FETCHED" in out     # the planner's recorded not_run


def test_manchester_not_shown_lists_bury_and_the_word_sale():
    out = NB.block(_man_board())
    ns = [ln for ln in out.splitlines() if ln.startswith("**Not shown")][0]
    assert "“staffy puppies bury”" in ns
    assert "Bury St Edmunds" in ns
    assert "“staffy puppies sale near me”" in ns
    assert "“staffy puppies for sale manchester”" not in ns     # "for sale" is never the town


# ── Task 20 (G6): London renders byte-for-byte as before ─────────────────────────────────

LONDON_GOLDEN = "12024635c85d197f3c67a9514574af4fc41bc65d79ec0413e4633f6c4845f4cb"
FIXTURE_GOLDEN = "6a046d9c0b5db4beb3e159c0c92b639ecca82ee1a0d23a53afd8988c6dba9e3f"


def test_london_board_block_is_byte_for_byte_unchanged():
    board = json.loads((REPO / "data/boards/blue-staffy-puppies-london.json").read_text(encoding="utf-8"))
    out = NB.block(board)
    assert hashlib.sha256(out.encode("utf-8")).hexdigest() == LONDON_GOLDEN


def test_fixture_block_is_byte_for_byte_unchanged(root):
    out = NB.block(_board(), root)
    assert hashlib.sha256(out.encode("utf-8")).hexdigest() == FIXTURE_GOLDEN
