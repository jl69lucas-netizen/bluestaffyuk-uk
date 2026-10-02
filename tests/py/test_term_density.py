import json
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import pytest
import query_augment as QA
import term_density as TD

PAGE_A = "<html><body><main><p>Blue staffy puppies in London. Blue staffy puppies are kind.</p>" \
         "<p>Kennel Club papers.</p></main></body></html>"
PAGE_B = "<html><body><main><p>Blue staffy puppies here. Kennel Club registered.</p></main></body></html>"
# Four linked card titles holding nearly all the prose: query_augment reads it as a listing.
LISTING = "<html><body><main><p>intro words here</p>" + "".join(
    '<h2><a href="/p%d">Puppy %d</a></h2><p>' % (i, i) + "blue staffy puppy lovely " * 20 + "</p>"
    for i in range(4)) + "</main></body></html>"
SLUG = "uk-locations/test-city"


def test_counts_each_term_on_each_page():
    c = TD.count_terms(PAGE_A, ["blue staffy puppies", "kennel club", "pedigree"])
    assert c["counts"] == {"blue staffy puppies": 2, "kennel club": 1, "pedigree": 0}
    assert c["words"] == 13


def test_a_shorter_term_also_counts_inside_a_longer_one():
    c = TD.count_terms(PAGE_A, ["blue staffy", "blue staffy puppies"])
    assert c["counts"] == {"blue staffy": 2, "blue staffy puppies": 2}


def test_stats_and_two_targets():
    pages = [TD.count_terms(PAGE_A, ["kennel club"]), TD.count_terms(PAGE_B, ["kennel club"])]
    row = TD.term_row("kennel club", pages, our_words=2000)
    assert row["min"] == 1 and row["max"] == 1 and row["median"] == 1
    # densities 1/13 and 1/7 per word -> 76.9 and 142.9 per 1,000; x2 for a 2,000-word page
    assert row["target_median"] == (187, 253)
    assert row["target_leader"] == (253, 286)
    assert row["seen_on"] == 2 and row["of"] == 2 and row["mean"] == 1.0


def test_zero_competitor_pages_is_not_fetched():
    row = TD.term_row("x", [], our_words=2000)
    assert row["note"].startswith("NOT FETCHED")


def test_a_page_with_no_words_does_not_divide_by_zero():
    empty = TD.count_terms("<html><body><main></main></body></html>", ["kennel club"])
    assert empty["words"] == 0
    row = TD.term_row("kennel club", [empty, TD.count_terms(PAGE_B, ["kennel club"])], 1000)
    assert row["seen_on"] == 1 and row["min"] == 0 and row["max"] == 1
    assert row["target_median"] == row["target_leader"] == (143, 143)


def test_pct():
    assert TD._pct([5], 0.25) == 5 and TD._pct([5], 0.75) == 5
    assert TD._pct([], 0.5) == 0.0
    assert TD._pct([0, 10], 0.25) == 2.5


def test_section_words():
    assert TD.section_words({"words": {"min": 99, "max": 121}}) == 110
    assert TD.section_words({"words": 300}) == 300
    assert TD.section_words({}) == 0


def test_board_entity_names():
    ont = {"entities": [{"id": "ont:a", "name": "Alpha"}, {"id": "ont:b", "name": "Beta"}]}
    board = {"sections": [{"entities": ["ont:b", "ont:a"]}, {"entities": ["ont:a", "ont:zzz"]}, {}]}
    assert TD.board_entity_names(board, ont) == ["Beta", "Alpha"]


def _root(tmp_path, pages, caches):
    raw = tmp_path / "data/queries/raw/test-city"
    raw.mkdir(parents=True)
    (raw / "competitors.json").write_text(json.dumps({"pages": pages}))
    cache = tmp_path / "data/queries/cache/test-city"
    cache.mkdir(parents=True)
    for n, html in caches.items():
        (cache / f"{n}.html").write_text(html)
    return tmp_path


def test_unreadable_competitors_json_is_empty(tmp_path):
    assert TD.competitor_pages(SLUG, ["x"], root=tmp_path) == []
    raw = tmp_path / "data/queries/raw/test-city"
    raw.mkdir(parents=True)
    (raw / "competitors.json").write_text("{not json")
    assert TD.competitor_pages(SLUG, ["x"], root=tmp_path) == []


def test_skips_blocked_missing_cache_and_listing_pages(tmp_path):
    assert QA.listing_reason(QA.page_metrics(LISTING))
    pages = [{"url": "u1", "google_pos": 1},
             {"url": "u2", "google_pos": 2, "blocked": True},
             {"url": "u3", "google_pos": 3},                      # no cache file
             {"url": "u4", "google_pos": 4},                      # a listing
             {"url": "u5", "google_pos": 5}]
    root = _root(tmp_path, pages, {1: PAGE_A, 2: PAGE_A, 4: LISTING, 5: PAGE_B})
    got = TD.competitor_pages(SLUG, ["kennel club"], root=root)
    assert [(p["url"], p["rank"], p["of"]) for p in got] == [("u1", 1, 4), ("u5", 4, 4)]
    assert got[0]["counts"] == {"kennel club": 1}


def test_top_caps_the_bodies_counted(tmp_path, monkeypatch):
    monkeypatch.setattr(TD, "TOP", 2)
    pages = [{"url": f"u{n}", "google_pos": n} for n in range(1, 4)]
    root = _root(tmp_path, pages, {1: PAGE_A, 2: PAGE_B, 3: PAGE_A})
    assert [p["url"] for p in TD.competitor_pages(SLUG, ["x"], root=root)] == ["u1", "u2"]


def test_table_renders_ranks_thin_pool_dash_and_overlap_note(tmp_path):
    pages = [{"url": "u1", "google_pos": 1}, {"url": "u2", "google_pos": 2}]
    root = _root(tmp_path, pages, {1: PAGE_A, 2: PAGE_B})
    board = {"meta": {"slug": SLUG},
             "sections": [{"keywords": {"primary": ["kennel club"], "secondary": ["pedigree"]},
                           "entities": ["ont:a"], "words": {"min": 1900, "max": 2100}}]}
    ont = {"entities": [{"id": "ont:a", "name": "Blue Staffy"}]}
    out = TD.table(board, ont, root=root)
    lines = out.splitlines()
    # No listing page was in the pool, so the "differs from block 4b" clause is not said.
    assert lines[0] == "Counted on 2 non-listing competitor bodies (ranks 1, 2 of 2): u1, u2"
    assert "**Thin pool:** fewer than three bodies — the bands are indicative only." in lines
    assert "| kennel club | 2/2 | 1 | 1 | 1.0 | 1 | 187–253 | 253–286 |" in lines
    assert ("| pedigree | 0/2 | 0 | 0 | 0.0 | 0 | — (no competitor uses it) "
            "| — (no competitor uses it) |") in lines
    assert "| Blue Staffy | 2/2 | 1 | 1.5 | 1.5 | 2 |" in out
    assert lines[-1] == TD.OVERLAP_NOTE


def test_table_says_it_differs_from_4b_only_when_a_listing_was_skipped(tmp_path):
    pages = [{"url": "u1", "google_pos": 1}, {"url": "u2", "google_pos": 2},
             {"url": "u3", "google_pos": 3}]
    root = _root(tmp_path, pages, {1: PAGE_A, 2: LISTING, 3: PAGE_B})
    board = {"meta": {"slug": SLUG}, "sections": [{"keywords": {"primary": ["kennel club"]}}]}
    first = TD.table(board, {"entities": []}, root=root).splitlines()[0]
    assert first == ("Counted on 2 non-listing competitor bodies (ranks 1, 3 of 3; listing pages "
                     "skipped, so this differs from block 4b's five): u1, u3")


def test_skipped_collects_the_listing_urls(tmp_path):
    pages = [{"url": "u1", "google_pos": 1}, {"url": "u2", "google_pos": 2}]
    root = _root(tmp_path, pages, {1: LISTING, 2: PAGE_A})
    skipped = []
    TD.competitor_pages(SLUG, ["x"], root=root, skipped=skipped)
    assert skipped == ["u1"]


def test_the_old_private_aliases_are_gone():
    assert not hasattr(TD, "_md") and not hasattr(TD, "_section_words")


def test_table_with_no_bodies_is_not_fetched(tmp_path):
    board = {"meta": {"slug": SLUG}, "sections": [{"keywords": {"primary": ["kennel club"]}}]}
    out = TD.table(board, {"entities": []}, root=tmp_path)
    assert out.startswith("Counted on 0 non-listing competitor bodies: NOT FETCHED")
    assert "| kennel club | NOT FETCHED — no cached competitor page |" in out


def test_cli_needs_a_known_slug(capsys):
    assert TD.main([]) == 2
    assert TD.main(["no-such-board-slug"]) == 2
    assert "usage" in capsys.readouterr().err
