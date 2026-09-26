# tests/py/test_keyword_metrics.py — scripts/keyword_metrics.py, the ours-vs-top-5 keyword
# table (parity build Task 18; CAG §7a, audit rows 7a.1, 7a.2, 7a.5, 7a.7, 7d.6). Competitor
# pages are saved fixtures; nothing here fetches.
import copy
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import keyword_metrics as KM  # noqa: E402
import family_rules as FR     # noqa: E402

SCRIPT = ROOT / "scripts" / "keyword_metrics.py"
PAGE = (ROOT / "tests/py/fixtures/competitor-pages/breeder-sections.html").read_text(encoding="utf-8")
PRIMARY = "blue staffy puppies manchester"
TERMS = [PRIMARY, "raised in the house", "deliver across the uk", "health testing",
         "blue staffies manchester"]
SLUG = "blue-staffy-puppies-testcity"


def test_measure_html_counts_the_saved_competitor_page():
    m = KM.measure_html(PAGE, PRIMARY, TERMS, ["blue staffies manchester"])
    assert m == {"words": 59, "unique_terms": 4, "mentions": 4, "variations": 0,
                 "exact": {"title": 1, "h1": 1, "h2": 0, "alt": 0, "description": 1},
                 "first_100": True, "title_front": True}


def test_matching_ignores_small_words_and_case():
    assert KM.phrase_count("blue staffy puppies for sale", "Blue Staffy Puppies FOR Sale") == 1
    assert KM.phrase_count("blue staffy puppies for sale", "blue staffy puppies sale") == 1
    assert KM.phrase_count("puppies manchester", "Puppies in Manchester and puppies at Manchester") == 2
    assert KM.front_loaded("blue staffy puppies manchester", "Blue Staffy Puppies in Manchester | X")
    assert not KM.front_loaded("blue staffy puppies manchester", "Home-Raised Blue Staffy Puppies Manchester")


def test_first_100_words_is_measured_on_main_only():
    filler = " ".join(["word"] * 100)
    late = f"<nav>{PRIMARY}</nav><main><p>{filler}</p><p>{PRIMARY}</p></main>"
    early = f"<main><p>Our {PRIMARY} are home raised.</p><p>{filler}</p></main>"
    assert KM.measure_html(late, PRIMARY, [], [])["first_100"] is False
    assert KM.measure_html(early, PRIMARY, [], [])["first_100"] is True


def _board(status="boarded", title="Blue Staffy Puppies Manchester | BlueStaffyUK",
           slug="blue-staffy-first-week-at-home", page_type="blog"):
    b = copy.deepcopy(json.loads((ROOT / "data/boards/_demo.json").read_text()))
    b["meta"].update(slug=slug, page_type=page_type, status=status)
    b["brief"]["primary_keyword"] = PRIMARY
    b["meta_set"]["titles"][0] = title
    b["meta_set"]["pick"]["title"] = 0
    b["h1"]["variants"][0] = "Blue Staffy Puppies in Manchester"
    b["h1"]["pick"] = 0
    b["sections"][2]["heading"] = "How Our Blue Staffy Puppies in Manchester Are Raised"
    b["sections"][2]["keywords"]["variation"] = ["blue staffies manchester"]
    return b


def test_board_row_measures_the_planned_tags_before_the_page_is_built():
    row = KM.board_row(_board())
    assert row["who"] == "ours (board)" and row["title_front"] is True
    assert row["exact"] == {"title": 1, "h1": 1, "h2": 1, "alt": None, "description": 0}
    assert row["words"] is None and row["first_100"] is None
    assert row["note"].startswith("not built")


def test_title_not_front_loaded_fails_a_boarded_new_page_and_warns_a_draft():
    late = "Home-Raised Blue Staffy Puppies Manchester | BlueStaffyUK"
    assert [f[:2] for f in KM.findings(_board(title=late), rebuilt=set())] == [
        ("title-front-load", "FAIL")]
    assert [f[:2] for f in KM.findings(_board("draft", title=late), rebuilt=set())] == [
        ("title-front-load", "WARN")]
    assert KM.findings(_board(), rebuilt=set()) == []


def test_first_100_words_fails_a_rebuilt_new_page(tmp_path):
    slug = "blue-staffy-first-week-at-home"
    page = tmp_path / slug / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text("<main><p>" + " ".join(["word"] * 120) + f" {PRIMARY}</p></main>")
    got = KM.findings(_board(), dist=tmp_path, rebuilt={slug})
    assert [f[:2] for f in got] == [("first-100-words", "FAIL")]
    page.write_text(f"<main><p>{PRIMARY} " + " ".join(["word"] * 120) + "</p></main>")
    assert KM.findings(_board(), dist=tmp_path, rebuilt={slug}) == []
    # not in rebuilt.json: the built page is the migrated body, not this record's page
    page.write_text("<main><p>" + " ".join(["word"] * 120) + "</p></main>")
    assert KM.findings(_board(), dist=tmp_path, rebuilt=set()) == []


def test_family_rules_carries_the_placement_checks_on_new_pages_only():
    late = "Home-Raised Blue Staffy Puppies Manchester | BlueStaffyUK"
    ids = [c for c, _, _ in FR.findings(_board(title=late), ont={})]
    assert "title-front-load" in ids
    built = _board(title=late, slug="blue-staffy-uk-breeders", page_type="interior")
    assert "title-front-load" not in [c for c, _, _ in FR.findings(built, ont={})]


def _repo(tmp_path):
    raw = tmp_path / "data/queries/raw" / SLUG
    raw.mkdir(parents=True)
    pages = [
        {"url": "https://blocked.example/", "google_pos": 1, "bing_pos": None, "h2": [],
         "h2_all": 0, "blocked": True},
        {"url": "https://cached.example/", "google_pos": 2, "bing_pos": None, "h2": [],
         "h2_all": 0, "blocked": False},
        {"url": "https://metrics-only.example/", "google_pos": None, "bing_pos": 1, "h2": [],
         "h2_all": 0, "blocked": False,
         "metrics": {"title": "Blue Staffy Puppies Manchester", "meta_description": None,
                     "word_count": 900, "sections": [{"h2": "Blue Staffy Puppies in Manchester",
                                                      "words": 10, "h3": []}]}},
    ]
    (raw / "competitors.json").write_text(json.dumps({"status": "ok", "pages": pages}))
    cache = tmp_path / "data/queries/cache" / SLUG
    cache.mkdir(parents=True)
    (cache / "2.html").write_text(PAGE)
    return tmp_path


def test_competitor_rows_come_from_the_cache_then_the_saved_metrics(tmp_path):
    rows = KM.competitor_rows(SLUG, PRIMARY, TERMS, ["blue staffies manchester"], _repo(tmp_path))
    assert [r["who"] for r in rows] == ["https://cached.example/", "https://metrics-only.example/"]
    assert rows[0]["unique_terms"] == 4 and rows[0]["note"] == "measured from data/queries/cache"
    tag_only = rows[1]
    assert tag_only["exact"] == {"title": 1, "h1": None, "h2": 1, "alt": None, "description": 0}
    assert tag_only["title_front"] is True and tag_only["words"] == 900
    assert tag_only["unique_terms"] is None
    assert tag_only["note"].startswith("NOT FETCHED — ") and "3.html" in tag_only["note"]


def test_no_competitor_file_is_one_named_barrier(tmp_path):
    rows = KM.competitor_rows(SLUG, PRIMARY, TERMS, [], tmp_path)
    assert len(rows) == 1 and rows[0]["who"] == "competitors"
    assert rows[0]["note"].startswith("NOT FETCHED — ")


def test_table_markdown_names_every_column():
    t = {"slug": "x", "primary_keyword": PRIMARY, "terms": 5,
         "rows": [KM.board_row(_board())]}
    md = KM.markdown(t)
    for col in ("Page", "Words", "Unique terms", "Mentions", "Variations", "Title", "H1",
                "H2", "Alt", "Description", "First 100", "Title front"):
        assert col in md.splitlines()[0]
    assert "ours (board)" in md


def test_cli_prints_the_table_and_writes_the_json(tmp_path):
    out = tmp_path / "km.json"
    r = subprocess.run([sys.executable, str(SCRIPT), "blue-staffy-uk-breeders", "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "| Page |" in r.stdout
    data = json.loads(out.read_text())
    assert data["slug"] == "blue-staffy-uk-breeders"
    assert data["rows"][0]["who"].startswith("ours") and data["findings"] == []


def test_cli_refuses_an_unknown_board():
    r = subprocess.run([sys.executable, str(SCRIPT), "no-such-board-xyz"], capture_output=True, text=True)
    assert r.returncode == 2 and "no board" in r.stdout + r.stderr


def test_the_board_shows_the_table_on_new_pages_only():
    import build_page_board as BPB
    from test_page_board import ONT_OK, LEDGER_EMPTY
    html = BPB.render(_board(), ONT_OK, LEDGER_EMPTY, live={}, thumbs={},
                      slug="blue-staffy-first-week-at-home")
    assert "4b. Keyword metrics" in html and "ours (board)" in html
    demo = json.loads((ROOT / "data/boards/_demo.json").read_text())
    assert "4b. Keyword metrics" not in BPB.render(demo, ONT_OK, LEDGER_EMPTY, live={},
                                                    thumbs={}, slug="_demo")


def test_listing_competitors_are_marked_not_read_as_prose(tmp_path, monkeypatch):
    # Task 17 classifies competitor pages prose vs listing (query_augment._prose_problem); a
    # marketplace's card text is not a competitor's copy, so the row says so.
    root = _repo(tmp_path)
    raw = root / "data/queries/raw" / SLUG / "competitors.json"
    data = json.loads(raw.read_text())
    data["pages"][2]["metrics"]["listing"] = "card grid holds 90% of the prose"
    raw.write_text(json.dumps(data))
    rows = KM.competitor_rows(SLUG, PRIMARY, TERMS, [], root)
    assert rows[0]["listing"] is None and not rows[0]["note"].startswith("LISTING")
    assert rows[1]["listing"] == "card grid holds 90% of the prose"
    assert rows[1]["note"].startswith("LISTING — card grid holds 90% of the prose; ")
    # a cached page is classified from its own HTML, the way --extract-h2 measures it
    real = KM.QA.page_metrics
    monkeypatch.setattr(KM.QA, "page_metrics",
                        lambda html: dict(real(html), listing="card grid holds 80% of the prose"))
    cached = KM.competitor_rows(SLUG, PRIMARY, TERMS, [], root)[0]
    assert cached["listing"] == "card grid holds 80% of the prose"
    assert cached["note"] == ("LISTING — card grid holds 80% of the prose; body columns count "
                              "card text, not prose · measured from data/queries/cache")
