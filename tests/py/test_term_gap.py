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
    gaps = TG.phrase_gaps([A, B, C], board_terms=["kennel club"], min_domains=2)
    terms = {g["term"] for g in gaps}
    assert "microchipped" in terms and "vaccinated" in terms
    assert "puppy pack" not in terms
    assert "kennel club" not in terms


def test_a_phrase_inside_a_board_term_is_not_a_gap():
    gaps = TG.phrase_gaps([A, B], board_terms=["microchipped and vaccinated puppies"], min_domains=2)
    assert "microchipped" not in {g["term"] for g in gaps}


def test_a_phrase_on_three_pages_of_one_domain_is_not_a_gap():
    pages = [TG.body(h, url="https://www.one.example/p%d" % i) for i, h in enumerate((A, B, A))]
    assert "microchipped" not in {g["term"] for g in TG.phrase_gaps(pages, [], min_domains=2)}


def test_a_phrase_on_two_domains_is_a_gap():
    pages = [TG.body(A, url="https://www.one.example/a"), TG.body(A, url="https://one.example/b"),
             TG.body(B, url="https://two.example/")]
    g = {g["term"]: g for g in TG.phrase_gaps(pages, [], min_domains=2)}["microchipped"]
    assert (g["domains"], g["pages"], g["prose"]) == (2, 3, 3)


def test_domain_of():
    assert TG.domain_of("https://www.Pets4Homes.co.uk/sale/?x=1") == "pets4homes.co.uk"
    assert TG.domain_of("") == ""


def test_listing_and_prose_split_counts():
    pages = [TG.body(A), TG.body(B), TG.body(LISTING, listing=True)]
    gaps = {g["term"]: g for g in TG.phrase_gaps(pages, board_terms=[], min_domains=2)}
    g = gaps["microchipped"]
    assert g["domains"] == 3 and g["pages"] == 3 and g["prose"] == 2 and g["mentions"] == 2 + 80


def test_sort_domains_then_prose_then_mentions():
    pages = [TG.body(A), TG.body(B), TG.body(LISTING, listing=True)]
    gaps = TG.phrase_gaps(pages, board_terms=[], min_domains=2)
    keys = [(-g["domains"], -g["prose"], -g["mentions"], g["term"]) for g in gaps]
    assert keys == sorted(keys)


def test_ui_stop_set_is_pinned():
    # Every word here was seen on the London pool (staffie-owners, pets4homes, freeads).
    assert TG.STOP_UI == frozenset(
        "ad ads advert adverts ago click cookie cookies details filter filters hours listings menu "
        "miles next page posted premium prev results save search show sign sort view "
        "accept browser consent data partners personal policy preferences privacy processing "
        "purposes tag tags".split())


def test_generic_stop_set_is_pinned():
    assert TG.STOP_GENERIC == frozenset(
        "we our you your puppy puppies dog dogs page here more can will very also all one two get any "
        "i it its this that these those be been was were has have had not no or but if so as up out "
        "about just than then them they their there what when where which who how my me us "
        "both other others well new first find feel now around she he her his him old read based "
        "highest full free looking only own each every some most many much make made see go come "
        "know need like still even really may might would could should do does did being per via "
        "into over under after before off again too same such".split())


def test_boilerplate_filter():
    ui = ("<html><body><main><p>View details. Save advert. Posted 3 days ago. 12 results. "
          "Sort by price. Filter results. 5 miles away. Premium listings. £1,500. 2024. x</p></main></body></html>")
    gaps = TG.phrase_gaps([ui, ui], board_terms=[], min_domains=2)
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
    gaps = TG.entity_gaps([A, B], ont, board_entity_ids=[], min_domains=1)
    assert [g["id"] for g in gaps] == ["ont:kc"]
    assert gaps[0]["seen_on"] == 1


def test_entity_gap_matches_aliases_and_skips_board_entities():
    ont = {"entities": [{"id": "ont:kc", "name": "The Royal Kennel Club", "aliases": ["Kennel Club"],
                         "class": "Organization"},
                        {"id": "ont:vet", "name": "Veterinarian", "aliases": ["vet"], "class": "Role"}]}
    pages = [TG.body(A), TG.body(B, listing=True)]
    gaps = TG.entity_gaps(pages, ont, board_entity_ids=["ont:vet"], min_domains=1)
    assert [(g["id"], g["seen_on"], g["prose"]) for g in gaps] == [("ont:kc", 1, 1)]


def test_other_cities_are_named_not_proposed(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text(json.dumps([
        {"slug": "blue-staffy-puppies-london", "city": "London"},
        {"slug": "staffy-breeding-dogs-glasgow", "city": "Glasgow (breeding dogs)"},
        {"slug": "staffy-puppies-for-sale-essex", "city": "Essex"},
        {"slug": "blue-staffy-puppies-uk", "city": "UK"}]), encoding="utf-8")
    others = TG.other_cities("uk-locations/blue-staffy-puppies-london", tmp_path)
    assert others == {"glasgow", "essex"}
    page = "<html><body><main><p>Pups in Glasgow, Essex and Kent, from London. Vet checked.</p></main></body></html>"
    ont = {"entities": [{"id": "ont:glasgow", "name": "Glasgow", "aliases": [], "class": "Place"},
                        {"id": "ont:essex", "name": "Essex", "aliases": [], "class": "Place"},
                        {"id": "ont:kent", "name": "Kent", "aliases": [], "class": "Place",
                         "place_type": "county"},
                        {"id": "ont:london", "name": "London", "aliases": [], "class": "Place"},
                        {"id": "ont:vet", "name": "Vet", "aliases": [], "class": "Role"}]}
    gaps = TG.entity_gaps([page], ont, ["ont:london"], others, min_domains=1)
    assert [g["id"] for g in gaps] == ["ont:vet"]
    named = TG.other_places_named([page], ont, ["ont:london"], others)
    assert {g["id"] for g in named} == {"ont:glasgow", "ont:essex", "ont:kent"}


def test_an_entity_needs_two_domains():
    ont = {"entities": [{"id": "ont:kc", "name": "Kennel Club", "aliases": [], "class": "Organization"},
                        {"id": "ont:vet", "name": "Vet", "aliases": [], "class": "Role"}]}
    pages = [TG.body(A, url="https://one.example/a"), TG.body(A, url="https://www.one.example/b"),
             TG.body(B, url="https://one.example/c"), TG.body(B, url="https://two.example/")]
    assert TG.MIN_DOMAINS == 2
    gaps = TG.entity_gaps(pages, ont, [])
    assert [(g["id"], g["domains"], g["seen_on"]) for g in gaps] == [("ont:vet", 2, 2)]


def test_phrases_never_carry_another_place():
    page = ("<html><body><main><p>Staffy puppies Manchester ready. Birmingham pups vet checked. "
            "Kent breeder. Vet checked.</p></main></body></html>")
    ont = {"entities": [{"id": "ont:man", "name": "Manchester", "aliases": ["Manc"], "class": "Place"},
                        {"id": "ont:kent", "name": "Kent", "aliases": [], "class": "Place",
                         "place_type": "county"}]}
    places = TG.place_names(ont, {"manchester", "birmingham"})
    assert places == ["birmingham", "kent", "manc", "manchester"]
    terms = {g["term"] for g in TG.phrase_gaps([page, page], [], places=places)}
    assert "vet checked" in terms
    assert not any(w in t.split() for t in terms for w in ("manchester", "birmingham", "kent"))


def test_london_tables_carry_no_other_city():
    import keyword_metrics as KM
    board = json.loads((KM.ROOT / "data/boards/blue-staffy-puppies-london.json").read_text())
    ont = json.loads((KM.ROOT / "data/bsuk-ontology.json").read_text())
    md = TG.block(board, ont)
    tables = md.split("**Phrases two or more")[1].split("**Entities competitors name")[0]
    assert "| " in tables
    for city in ("manchester", "birmingham"):
        assert city not in tables.lower()


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
    assert md.startswith("Measured on 3 competitor pages (2 prose, 1 listing) on 3 domains: "
                         "a.example ×1 (prose); list.example ×1 (listing); b.example ×1 (prose). "
                         "Ranks 1, 3, 4.")
    for h in ("**Your keyword types against theirs**",
              "**Phrases two or more competitors use and our board does not**",
              "**Entities competitors name that no section lists (ontology only)**",
              "**Entity relationships on this page**"):
        assert h in md
    assert "Phrases (2–3 words)" in md and "Single words" in md
    assert md.index("Phrases (2–3 words)") < md.index("Single words")
    assert "| microchipped | 3 | 3 | 2 |" in md
    ent = md.split("**Entities competitors name")[1].split("**Entity relationships")[0]
    assert "None." in ent and "Veterinarian" not in ent   # one domain only
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
