import json
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import term_gap as TG

A = "<html><body><main><p>Our puppies are microchipped and vaccinated. Kennel Club registered.</p></main></body></html>"
B = "<html><body><main><p>Each pup is microchipped, wormed and vaccinated by our vet.</p></main></body></html>"
C = "<html><body><main><p>Puppies leave at eight weeks with a puppy pack.</p></main></body></html>"
# Four linked card titles holding nearly all the prose: query_augment reads it as a listing.
LISTING = "<html><body><main><p>intro words here</p>" + "".join(
    '<h2><a href="/p%d">Puppy %d</a></h2><p>' % (i, i) + "microchipped vaccinated lovely pup " * 20
    + "</p>" for i in range(4)) + "</main></body></html>"
SLUG = "uk-locations/test-city"


def test_ngram_needs_two_competitors():
    gaps = TG.phrase_gaps([A, B, C], board_terms=["kennel club"], min_pages=2)
    terms = {g["term"] for g in gaps}
    assert "microchipped" in terms and "vaccinated" in terms
    assert "puppy pack" not in terms
    assert "kennel club" not in terms


def test_a_phrase_inside_a_board_term_is_not_a_gap():
    gaps = TG.phrase_gaps([A, B], board_terms=["microchipped and vaccinated puppies"], min_pages=2)
    assert "microchipped" not in {g["term"] for g in gaps}


def test_listing_and_prose_split_counts():
    pages = [TG.body(A), TG.body(B), TG.body(LISTING, listing=True)]
    gaps = {g["term"]: g for g in TG.phrase_gaps(pages, board_terms=[], min_pages=2)}
    g = gaps["microchipped"]
    assert g["pages"] == 3 and g["prose"] == 2 and g["mentions"] == 2 + 80


def test_sort_pages_then_prose_then_mentions():
    pages = [TG.body(A), TG.body(B), TG.body(LISTING, listing=True)]
    gaps = TG.phrase_gaps(pages, board_terms=[], min_pages=2)
    keys = [(-g["pages"], -g["prose"], -g["mentions"], g["term"]) for g in gaps]
    assert keys == sorted(keys)


def test_ui_stop_set_is_pinned():
    # Every word here was seen on the London pool (staffie-owners, pets4homes, freeads).
    assert TG.STOP_UI == frozenset(
        "ad ads advert adverts ago click cookie cookies details filter filters hours listings menu "
        "miles next page posted premium prev results save search show sign sort view".split())


def test_boilerplate_filter():
    ui = ("<html><body><main><p>View details. Save advert. Posted 3 days ago. 12 results. "
          "Sort by price. Filter results. 5 miles away. Premium listings. £1,500. 2024. x</p></main></body></html>")
    gaps = TG.phrase_gaps([ui, ui], board_terms=[], min_pages=2)
    terms = {g["term"] for g in gaps}
    for w in ("view", "save", "ago", "posted", "results", "sort", "filter", "miles", "premium", "listings",
              "£1", "500", "2024", "x", "3", "12"):
        assert w not in terms, w
    for g in gaps:
        toks = g["term"].split()
        assert toks[0] not in TG.STOP_GENERIC and toks[-1] not in TG.STOP_GENERIC, g


def test_entity_gap_uses_ontology_names_only():
    ont = {"entities": [{"id": "ont:kc", "name": "Kennel Club", "aliases": [], "class": "Organization"},
                        {"id": "ont:dogs-trust", "name": "Dogs Trust", "aliases": [], "class": "Organization"}]}
    gaps = TG.entity_gaps([A, B], ont, board_entity_ids=[])
    assert [g["id"] for g in gaps] == ["ont:kc"]
    assert gaps[0]["seen_on"] == 1


def test_entity_gap_matches_aliases_and_skips_board_entities():
    ont = {"entities": [{"id": "ont:kc", "name": "The Royal Kennel Club", "aliases": ["Kennel Club"],
                         "class": "Organization"},
                        {"id": "ont:vet", "name": "Veterinarian", "aliases": ["vet"], "class": "Role"}]}
    pages = [TG.body(A), TG.body(B, listing=True)]
    gaps = TG.entity_gaps(pages, ont, board_entity_ids=["ont:vet"])
    assert [(g["id"], g["seen_on"], g["prose"]) for g in gaps] == [("ont:kc", 1, 1)]


def test_by_type_view():
    board = {"sections": [{"keywords": {"primary": ["microchipped"], "lsi": ["puppy pack", "wormed"],
                                        "geo": []}}]}
    rows = {r["type"]: r for r in TG.by_type(board, [TG.body(A), TG.body(B)])}
    assert (rows["primary"]["ours"], rows["primary"]["found"]) == (1, 1)
    assert (rows["lsi"]["ours"], rows["lsi"]["found"]) == (2, 1)
    assert (rows["geo"]["ours"], rows["geo"]["found"]) == (0, 0)


def test_relations_not_fetched_without_key():
    assert TG.relations_lines({"entities": []}, set()) == [TG.NO_RELATIONS]
    assert TG.NO_RELATIONS.startswith("NOT FETCHED")


def test_relations_filtered_to_known_ends():
    ont = {"entities": [], "relations": [{"from": "ont:a", "type": "partOf", "to": "ont:b"},
                                         {"from": "ont:a", "type": "near", "to": "ont:z"}]}
    lines = TG.relations_lines(ont, {"ont:a", "ont:b"})
    assert len(lines) == 1 and "ont:a" in lines[0] and "ont:b" in lines[0]


def _fixture(tmp_path):
    bare = SLUG.rsplit("/", 1)[-1]
    raw = tmp_path / "data/queries/raw" / bare
    cache = tmp_path / "data/queries/cache" / bare
    raw.mkdir(parents=True)
    cache.mkdir(parents=True)
    pages = [{"url": "https://blocked.example/", "blocked": True, "google_pos": 1},
             {"url": "https://a.example/", "google_pos": 2},
             {"url": "https://missing.example/", "google_pos": 3},
             {"url": "https://list.example/", "google_pos": 4},
             {"url": "https://b.example/", "google_pos": 5}]
    (raw / "competitors.json").write_text(json.dumps({"pages": pages}), encoding="utf-8")
    (cache / "1.html").write_text(A, encoding="utf-8")
    (cache / "2.html").write_text(A, encoding="utf-8")
    (cache / "4.html").write_text(LISTING, encoding="utf-8")
    (cache / "5.html").write_text(B, encoding="utf-8")
    return tmp_path


def test_competitor_bodies_skips_blocked_and_missing_and_labels_listings(tmp_path):
    root = _fixture(tmp_path)
    bodies = TG.competitor_bodies(SLUG, root)
    assert [(b["n"], b["rank"], b["listing"]) for b in bodies] == [(2, 1, False), (4, 3, True),
                                                                   (5, 4, False)]
    assert bodies[0]["url"] == "https://a.example/" and "microchipped" in bodies[0]["tokens"]


def test_competitor_bodies_no_file_is_empty(tmp_path):
    assert TG.competitor_bodies(SLUG, tmp_path) == []


def test_block_has_every_section(tmp_path):
    root = _fixture(tmp_path)
    board = {"meta": {"slug": SLUG},
             "sections": [{"keywords": {"primary": ["kennel club"]}, "entities": []}]}
    ont = {"entities": [{"id": "ont:kc", "name": "Kennel Club", "aliases": [], "class": "Organization"},
                        {"id": "ont:vet", "name": "Veterinarian", "aliases": ["vet"], "class": "Role"}]}
    md = TG.block(board, ont, root)
    assert md.startswith("Measured on 3 competitor pages (2 prose, 1 listing): ranks 1, 3, 4")
    for h in ("**Your keyword types against theirs**",
              "**Phrases two or more competitors use and our board does not**",
              "**Entities competitors name that no section lists (ontology only)**",
              "**Entity relationships on this page**"):
        assert h in md
    assert "| microchipped | 3 | 2 |" in md
    assert "| Veterinarian | Role | 1 | 1 |" in md
    assert "scripts/ontology_seed.py" in md
    assert TG.NO_RELATIONS in md


def test_block_with_no_competitors_says_not_fetched(tmp_path):
    board = {"meta": {"slug": SLUG}, "sections": [{"keywords": {"primary": ["x"]}, "entities": []}]}
    md = TG.block(board, {"entities": []}, tmp_path)
    assert md.startswith("Measured on 0 competitor pages") and "NOT FETCHED" in md


def test_cli_usage(capsys):
    assert TG.main([]) == 2
    assert TG.main(["no-such-slug-anywhere"]) == 2
    assert "usage" in capsys.readouterr().err
