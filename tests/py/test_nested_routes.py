# tests/py/test_nested_routes.py — the content gates read and write a city page at
# /uk-locations/<slug>/ (Known Issue 39, the project 5 prerequisite).
#
# One resolver, scripts/_slugs.py::resolve_page, turns a slug into (key, route) through
# data/page-map.json: a bare city slug keeps its bare KEY (the name of its data/facts,
# data/boards and data/verbatim files and its data/facts/rebuilt.json entry, as
# migration_parity.py and query_coverage_check.py already key it) and gets its nested ROUTE
# (dist/uk-locations/<slug>/index.html). Every fixture is its own root under tmp_path.
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import _slugs as S  # noqa: E402

LEEDS = "blue-staffy-puppies-for-sale-leeds"
NESTED = f"uk-locations/{LEEDS}"
TITLE = "Blue Staffy Puppies For Sale Leeds"
MIGRATED = ('<article class="container prose-migrated"><h1>Blue Staffy Puppies Leeds</h1>'
            "<p>Our puppies cost £1,200 and are DNA tested.</p>"
            '<img src="/images/leeds-pup.jpg" alt="A blue puppy in Leeds"></article>')


def site(tmp_path):
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data/page-map.json").write_text(json.dumps({"generated_from": "/old", "pages": [
        {"url": "/", "kind": "rich", "title": "Home"},
        {"url": "/blue-staffy-health-uk/", "kind": "rich", "title": "Blue Staffy Health UK"},
        {"url": f"/{NESTED}/", "kind": "location", "title": TITLE}]}))
    (tmp_path / "data/puppies.json").write_text("[]")
    (tmp_path / "data/settings.json").write_text(json.dumps({"address": {"city": "Carlisle"}}))
    return tmp_path


def put(root, route, html):
    p = root / "dist" / route / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html)
    return p


def write(root, rel, data):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data))


# --- the one resolver ------------------------------------------------------------------------

@pytest.mark.parametrize("slug, want", [
    (LEEDS, (LEEDS, NESTED)),                        # a bare city slug takes its mapped route
    (NESTED, (LEEDS, NESTED)),                       # the route itself keys by its bare slug
    (f"/{NESTED}/", (LEEDS, NESTED)),
    ("blue-staffy-health-uk", ("blue-staffy-health-uk", "blue-staffy-health-uk")),
    ("index", ("index", "")),
    ("/", ("index", "")),
    ("available/roys", ("available/roys", "available/roys")),   # not in the map: as given
    ("new-page", ("new-page", "new-page")),
    (f"other/{LEEDS}", (f"other/{LEEDS}", f"other/{LEEDS}")),   # another parent is not rewritten
    ("_demo", ("_demo", "_demo")),                              # pageboard's demo record
])
def test_resolve_page(tmp_path, slug, want):
    assert S.resolve_page(slug, site(tmp_path)) == want


def test_built_page_is_the_nested_index_html(tmp_path):
    root = site(tmp_path)
    assert S.built_page(LEEDS, root) == root / "dist" / NESTED / "index.html"
    assert S.built_page("index", root) == root / "dist" / "index.html"
    assert S.built_page(LEEDS, root, dist=tmp_path / "d") == tmp_path / "d" / NESTED / "index.html"


@pytest.mark.parametrize("slug", ["../x", "a/../b", "A B", "a//b", "a/./b"])
def test_resolve_page_refuses_a_path_that_is_not_a_slug(tmp_path, slug):
    with pytest.raises(ValueError):
        S.resolve_page(slug, site(tmp_path))


def test_two_routes_with_one_last_segment_are_refused(tmp_path):
    root = site(tmp_path)
    pm = json.loads((root / "data/page-map.json").read_text())
    pm["pages"].append({"url": f"/elsewhere/{LEEDS}/", "kind": "rich", "title": "x"})
    (root / "data/page-map.json").write_text(json.dumps(pm))
    with pytest.raises(ValueError, match="two routes"):
        S.resolve_page(LEEDS, root)


def test_without_a_page_map_a_slug_keeps_its_own_path(tmp_path):
    assert S.resolve_page(LEEDS, tmp_path) == (LEEDS, LEEDS)


def test_the_real_page_map_resolves_every_city_slug():
    rows = json.loads((REPO / "data/locations.json").read_text())
    assert len(rows) == 28
    for r in rows:
        assert S.built_page(r["slug"], REPO) == REPO / "dist/uk-locations" / r["slug"] / "index.html"


# --- the four gates (Task F2b) ---------------------------------------------------------------

import facts_preserved_check as FACTS  # noqa: E402
import link_parity_check as LP  # noqa: E402
import pageboard as PB  # noqa: E402
import verbatim_set_check as V  # noqa: E402


# --- facts_preserved_check.py ----------------------------------------------------------------

@pytest.mark.parametrize("arg", [LEEDS, NESTED])
def test_facts_extract_reads_the_city_page_and_writes_its_bare_key(tmp_path, monkeypatch, capsys, arg):
    root = site(tmp_path)
    monkeypatch.setattr(FACTS, "ROOT", root)
    put(root, NESTED, f"<html><body>{MIGRATED}</body></html>")
    assert FACTS.main(["--extract", arg]) == 0
    facts = json.loads((root / f"data/facts/{LEEDS}.json").read_text())
    assert facts["prices"] == ["£1,200"] and "/images/leeds-pup.jpg" in facts["images"]
    assert f"extracted facts for {LEEDS}" in capsys.readouterr().out


def test_facts_extract_makes_the_subfolder_an_unmapped_nested_slug_needs(tmp_path, monkeypatch):
    root = site(tmp_path)
    monkeypatch.setattr(FACTS, "ROOT", root)
    put(root, "available/roys", f"<html><body>{MIGRATED}</body></html>")
    assert FACTS.main(["--extract", "available/roys"]) == 0
    assert (root / "data/facts/available/roys.json").is_file()


def test_facts_check_judges_a_rebuilt_city_page(tmp_path, monkeypatch, capsys):
    root = site(tmp_path)
    monkeypatch.setattr(FACTS, "ROOT", root)
    put(root, NESTED, f"<html><body>{MIGRATED}</body></html>")
    FACTS.main(["--extract", LEEDS])
    write(root, "data/facts/rebuilt.json", [LEEDS])
    rebuilt = ("<html><body><main><h1>Blue Staffy Puppies Leeds</h1>"
               "<p>Our puppies cost {price} and are DNA tested.</p>"
               '<img src="/images/leeds-pup.jpg" alt="x"></main></body></html>')
    put(root, NESTED, rebuilt.format(price="£1,200"))
    capsys.readouterr()
    assert FACTS.main(["--check"]) == 0
    assert "examined 1 rebuilt pages; 0 problems" in capsys.readouterr().out
    put(root, NESTED, rebuilt.format(price="£950"))
    assert FACTS.main(["--check"]) == 1
    assert f"{LEEDS}: missing prices '£1,200'" in capsys.readouterr().out
    # the board record, keyed by the bare slug, is where a deliberate drop is read from
    write(root, f"data/boards/{LEEDS}.json", {"dropped": {
        "prices": ["£1,200 — the price moved to the listing page"],
        "text": ["Our puppies cost £1,200 and are DNA tested — the price moved"]}})
    assert FACTS.main(["--check"]) == 0


# --- link_parity_check.py --------------------------------------------------------------------

def record(hrefs):
    return {"meta": {"slug": LEEDS, "page_type": "location"},
            "sections": [{"shape": "prose", "links": {
                "internal": [{"href": h} for h in hrefs], "external": []}}]}


def point_lp(monkeypatch, root):
    monkeypatch.setattr(LP, "ROOT", root)
    monkeypatch.setattr(LP, "DIST", root / "dist")
    monkeypatch.setattr(LP, "BOARDS", root / "data/boards")


def test_link_parity_reads_the_city_page_and_its_bare_key_board(tmp_path, monkeypatch):
    root = site(tmp_path)
    point_lp(monkeypatch, root)
    put(root, NESTED, '<main><p><a href="/buy-blue-staffy-puppies-uk/">Buy</a></p></main>')
    write(root, f"data/boards/{LEEDS}.json", record(["/buy-blue-staffy-puppies-uk/"]))
    assert LP.check(LEEDS) == ([], 1)
    assert LP.check(NESTED) == ([], 1)
    write(root, f"data/boards/{LEEDS}.json", record(["/available-puppies/"]))
    problems, _ = LP.check(LEEDS)
    assert f"{LEEDS}: /buy-blue-staffy-puppies-uk/ is on the page and in no section's `links`" in problems


def test_link_parity_names_the_nested_path_of_a_missing_city_page(tmp_path, monkeypatch):
    root = site(tmp_path)
    point_lp(monkeypatch, root)
    problems, n = LP.check(LEEDS)
    assert n == 0 and problems == [f"{LEEDS}: no built page at dist/{NESTED}/index.html — run the build"]


# --- verbatim_set_check.py -------------------------------------------------------------------

def test_verbatim_page_title_reads_the_city_row(tmp_path, monkeypatch):
    root = site(tmp_path)
    monkeypatch.setattr(V, "ROOT", root)
    assert V.page_title(LEEDS) == TITLE
    assert V.page_title(NESTED) == TITLE
    assert "leeds" in V.target_keywords(LEEDS)


def test_verbatim_extract_and_check_a_city_page(tmp_path, monkeypatch, capsys):
    root = site(tmp_path)
    monkeypatch.setattr(V, "ROOT", root)
    monkeypatch.setattr(V, "migrated_body", lambda slug: MIGRATED)
    assert V.main(["--extract", NESTED]) == 0
    vset = json.loads((root / f"data/verbatim/{LEEDS}.json").read_text())
    assert vset["h1"] == "Blue Staffy Puppies Leeds"
    write(root, "data/facts/rebuilt.json", [LEEDS])
    write(root, "data/verbatim/applies.json", {"slugs": [LEEDS]})
    put(root, NESTED, "<main><h1>Blue Staffy Puppies Leeds</h1>"
                      '<img src="/images/leeds-pup.jpg" alt="A blue puppy in Leeds"></main>')
    capsys.readouterr()
    assert V.main(["--check"]) == 0
    assert "examined 1 applicable pages; 0 problems" in capsys.readouterr().out
    put(root, NESTED, "<main><h1>Somewhere Else</h1></main>")
    assert V.main(["--check"]) == 1


def test_verbatim_load_record_reads_the_bare_key_board(tmp_path, monkeypatch):
    root = site(tmp_path)
    monkeypatch.setattr(V, "ROOT", root)
    write(root, f"data/boards/{LEEDS}.json", {"verbatim": {"changed": []}})
    assert V.load_record(NESTED) == {"verbatim": {"changed": []}}


def test_verbatim_migrated_body_of_a_city_page_is_its_frozen_locations_row():
    # data/locations.json at the migration commit holds every city body; git history is frozen
    body = V.migrated_body("blue-staffy-puppies-aberdeen")
    assert len(body) > 3000 and "<" in body
    assert "Blue Staffy Puppies Manchester UK" in V.migrated_body("uk-locations/blue-staffy-puppies-manchester-uk")


# --- pageboard.py ----------------------------------------------------------------------------

def test_own_live_key_of_a_city_board_is_its_nested_route(tmp_path, monkeypatch):
    root = site(tmp_path)
    monkeypatch.setattr(PB, "ROOT", root)
    board = {"meta": {"slug": LEEDS, "page_type": "location"}}
    assert PB.own_live_key(board) == f"/{NESTED}/"
    board["meta"]["slug"] = "blue-staffy-health-uk"
    assert PB.own_live_key(board) == "/blue-staffy-health-uk/"
    board["meta"]["slug"] = "index"
    assert PB.own_live_key(board) == "/"


def test_the_own_live_key_matches_the_live_headings_key(tmp_path, monkeypatch):
    # the whole point: the page being rebuilt is excluded from its own collision check
    root = site(tmp_path)
    monkeypatch.setattr(PB, "ROOT", root)
    put(root, NESTED, "<main><h2>Delivery To Leeds</h2></main>")
    live = PB.live_headings(root / "dist")
    assert PB.own_live_key({"meta": {"slug": LEEDS, "page_type": "location"}}) in live


def test_dist_schema_types_reads_the_nested_city_page(tmp_path, monkeypatch):
    root = site(tmp_path)
    monkeypatch.setattr(PB, "ROOT", root)
    put(root, NESTED, '<script type="application/ld+json">{"@type": "FAQPage"}</script>')
    types, unparsed = PB.dist_schema_types(LEEDS, dist=root / "dist")
    assert types == {"FAQPage"} and unparsed == 0


def test_the_real_city_boards_key_their_live_pages():
    for r in json.loads((REPO / "data/locations.json").read_text()):
        assert PB.own_live_key({"meta": {"slug": r["slug"], "page_type": "location"}}) \
            == f"/uk-locations/{r['slug']}/"
