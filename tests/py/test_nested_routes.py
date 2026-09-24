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
