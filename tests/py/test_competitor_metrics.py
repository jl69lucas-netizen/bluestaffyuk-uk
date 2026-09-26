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
        {"h2": "Our Puppies", "words": 16, "h3": ["Current Litter"]},
        {"h2": "Health Testing", "words": 6, "h3": ["Hips"]},
        {"h2": "Delivery", "words": 5, "h3": []},
    ],
    "h3_count": 3,
    "images": 2,
    "videos": 2,
    "tables": 1,
    "schema_types": ["FAQPage", "ItemPage", "Organization", "Question", "WebPage"],
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
    assert d["pages"][1]["metrics"]["sections"] == [{"h2": "Only", "words": 3, "h3": []}]
    assert "2 of 2 pages" in r.stdout


def test_competitor_metrics_skips_a_page_whose_cache_file_is_missing(tmp_path):
    root = _repo(tmp_path, [_record("https://a.example/", PAGE, 1),
                            _record("https://b.example/", PAGE, 2)], {1: PAGE})
    r = _metrics_cli(root)
    assert r.returncode == 0, r.stderr
    d = json.loads((root / f"data/queries/raw/{SLUG}/competitors.json").read_text())
    assert "metrics" in d["pages"][0] and "metrics" not in d["pages"][1]
    assert "1 of 2 pages" in r.stdout and "https://b.example/" in r.stdout


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
    pages = [dict(_record(f"https://{i}.example/", PAGE, i + 1),
                  metrics=dict(EXPECTED, word_count=n)) for i, n in enumerate((100, 300, 900))]
    pages.append(dict(_record("https://blocked.example/", PAGE, 9), blocked=True,
                      metrics=dict(EXPECTED, word_count=5000)))
    assert Q.word_target(pages) == {"median": 300, "from": 3, "of": 4}


def test_word_target_without_metrics_names_its_barrier():
    wt = Q.word_target([_record("https://a.example/", PAGE, 1)])
    assert wt["median"] is None and wt["from"] == 0 and wt["of"] == 1
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
    assert data["word_target"] == {"median": 59, "from": 1, "of": 2}
    assert [r.get("words") for r in data["competitors"]] == [59, None]
