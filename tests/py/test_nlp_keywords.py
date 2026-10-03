"""Board block 4e: NLP keywords — named entities, core concepts, semantic attributes.

The rule under test is CLAUDE.md working rule 9 applied to keywords: every proposed term is
ATTESTED, on two or more competitor DOMAINS or in one of our own data files. The lexicons in
scripts/nlp_keywords.py only decide which lens a term sits in; a lexicon word nobody wrote
is never a row.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import nlp_keywords as NLP  # noqa: E402


def _page(text, url):
    return NLP.body(f"<html><body><main><p>{text}</p></main></body></html>", url=url)


A = "https://one.example/a"
A2 = "https://www.one.example/b"
B = "https://two.example/"
C = "https://three.example/"


def _terms(rows):
    return {r["term"].lower() for r in rows}


def _row(rows, term):
    return next(r for r in rows if r["term"].lower() == term.lower())


# ── attestation ─────────────────────────────────────────────────────────────────────────────
def test_a_term_on_one_domain_is_never_proposed_and_two_domains_is():
    pages = [_page("Crate training helps a puppy settle. Bite inhibition matters.", A),
             _page("We start crate training early. Bite inhibition is taught at home.", A2),
             _page("Crate training is how we begin.", B)]
    rows = NLP.core_concepts(pages)
    assert "crate training" in _terms(rows)
    # bite inhibition sits on two PAGES of one domain: one competitor, never a row
    assert "bite inhibition" not in _terms(rows)
    r = _row(rows, "crate training")
    assert r["domains"] == 2 and sorted(r["domain_list"]) == ["one.example", "two.example"]


def test_a_lexicon_word_in_no_text_is_never_proposed():
    pages = [_page("Lovely puppies raised at home.", A), _page("Lovely puppies raised at home.", B)]
    every = (NLP.core_concepts(pages) + NLP.semantic_attributes(pages)
             + NLP.named_entities(pages, {"entities": []}))
    terms = _terms(every)
    for word in ("deposit", "contract", "guarantee", "microchip", "insurance", "coat",
                 "temperament", "build"):
        assert word not in terms, word
    assert {"deposit", "contract", "guarantee", "microchip", "insurance"} <= NLP.TOPIC_NOUNS
    assert {"coat", "temperament", "build"} <= NLP.TRAIT_NOUNS


def test_a_term_only_in_our_data_is_ours_only():
    pages = [_page("Puppies raised at home.", A), _page("Puppies raised at home.", B)]
    docs = [("data/faq.json#deposit.a", "A refundable deposit secures your puppy.")]
    rows = NLP.core_concepts(pages, data_docs=docs)
    r = _row(rows, "refundable deposit")
    assert r["status"] == NLP.OURS_ONLY and r["domains"] == 0
    assert r["data_sources"] == ["data/faq.json#deposit.a"]


def test_status_gap_and_on_our_page():
    pages = [_page("Crate training and puppy socialisation.", A),
             _page("Crate training and puppy socialization.", B)]
    rows = NLP.core_concepts(pages, our_text="Our crate training starts at six weeks.")
    assert _row(rows, "crate training")["status"] == NLP.ON_PAGE
    assert _row(rows, "crate training")["ours"] == 1
    soc = _row(rows, "puppy socialisation")      # UK and US spellings fold to one row
    assert soc["status"] == NLP.GAP and soc["domains"] == 2


# ── the three lenses ────────────────────────────────────────────────────────────────────────
def test_crate_training_is_a_concept_blue_coat_an_attribute_rkc_an_entity():
    text = ("Every pup is registered with the Royal Kennel Club. "
            "We use crate training from day one. Each has a gleaming blue coat.")
    pages = [_page(text, A), _page(text, B)]
    concepts = _terms(NLP.core_concepts(pages))
    attrs = _terms(NLP.semantic_attributes(pages))
    ents = NLP.named_entities(pages, {"entities": []})
    assert "crate training" in concepts and "crate training" not in attrs
    assert "blue coat" in attrs and "blue coat" not in concepts
    assert "royal kennel club" in _terms(ents)
    assert _row(ents, "Royal Kennel Club")["type"] == "Organisation"
    assert _row(NLP.core_concepts(pages), "crate training")["type"] == "training"


def test_an_ontology_entity_gets_its_ner_type():
    ont = {"entities": [
        {"id": "ont:the-kennel-club", "name": "The Kennel Club", "aliases": ["Royal Kennel Club"],
         "class": "Organization"},
        {"id": "ont:l-2-hga-dna-test", "name": "L-2-HGA DNA test", "aliases": ["L-2-HGA"],
         "class": "Health"},
        {"id": "ont:lisa-bright", "name": "Lisa Bright", "aliases": [], "class": "People"},
        {"id": "ont:staffordshire-bull-terrier", "name": "Staffordshire Bull Terrier",
         "aliases": ["Staffy"], "class": "Organism"},
    ]}
    pages = [_page("Royal Kennel Club registered. Parents clear for L-2-HGA. A Staffy.", A),
             _page("Kennel Club papers. L-2-HGA clear. Staffordshire Bull Terrier pups.", B)]
    # on the research board but in no section: a candidate, not yet on our page
    rows = NLP.named_entities(pages, ont, also_ids=["ont:lisa-bright"])
    assert _row(rows, "The Kennel Club")["type"] == "Organisation"
    assert _row(rows, "L-2-HGA DNA test")["type"] == "Condition / test"
    assert _row(rows, "Staffordshire Bull Terrier")["type"] == "Breed / animal"
    lisa = _row(rows, "Lisa Bright")
    assert lisa["type"] == "Person" and lisa["status"] == NLP.OURS_ONLY
    assert lisa["data_sources"] == ["data/bsuk-ontology.json#ont:lisa-bright"]
    assert _row(rows, "The Kennel Club")["domains"] == 2
    listed = NLP.named_entities(pages, ont, board_entity_ids=["ont:lisa-bright"])
    assert _row(listed, "Lisa Bright")["status"] == NLP.ON_PAGE


def test_an_ontology_entity_on_one_domain_and_not_on_the_board_is_not_a_row():
    ont = {"entities": [{"id": "ont:pdsa", "name": "PDSA", "aliases": [], "class": "Organization"}]}
    pages = [_page("PDSA advice.", A), _page("Nothing here.", B)]
    assert NLP.named_entities(pages, ont) == []


def test_a_sentence_initial_capital_is_not_a_proper_noun():
    pages = [_page("Puppy Socialisation starts early. Blue staffy puppies love blue staffy puppies.", A),
             _page("Puppy Socialisation is our focus. We raise blue staffy puppies.", B)]
    terms = _terms(NLP.named_entities(pages, {"entities": []}))
    # sentence-initial "Puppy" leaves one capitalised word: not a multi-word name
    assert "puppy socialisation" not in terms


def test_a_title_case_phrase_written_lower_case_more_often_is_not_a_name():
    pages = [_page("<h2>Blue Staffy Puppies</h2> We breed blue staffy puppies, blue staffy puppies.", A),
             _page("<h2>Blue Staffy Puppies</h2> Our blue staffy puppies go home at eight weeks.", B)]
    assert "blue staffy puppies" not in _terms(NLP.named_entities(pages, {"entities": []}))


# ── drops ───────────────────────────────────────────────────────────────────────────────────
def test_a_marketplace_name_and_another_city_are_dropped_on_a_location_board():
    text = ("Seen on Preloved Classifieds before. Collection from Manchester City Centre. "
            "We offer manchester collection and london collection. Pets4Homes delivery offered.")
    pages = [_page(text, A), _page(text, B)]
    places = ["manchester"]
    ents = _terms(NLP.named_entities(pages, {"entities": []}, places=places))
    concepts = _terms(NLP.core_concepts(pages, places=places))
    assert not any("preloved" in t or "manchester" in t for t in ents), ents
    assert not any("manchester" in t or "pets4homes" in t for t in concepts), concepts
    assert "london collection" in concepts


def test_matching_is_on_word_boundaries():
    assert NLP.mentions("og walking", "Our dog-walking service runs daily.") == 0
    assert NLP.mentions("dog walking", "Our dog-walking service runs daily.") == 1
    pages = [_page("A dog-friendly flat.", A), _page("A dog-friendly flat.", B)]
    assert "og friendly" not in _terms(NLP.core_concepts(pages) + NLP.semantic_attributes(pages))


def test_spelling_fold_is_uk_us_only():
    assert NLP.fold_tokens(["socialisation", "colour", "behaviour"]) == \
        NLP.fold_tokens(["socialization", "color", "behavior"])
    assert NLP.fold_tokens(["our"]) == ["our"]          # short words are never folded


def test_an_adjective_before_the_breed_is_an_attribute():
    pages = [_page("A loyal Staffy is a joy.", A), _page("The loyal staffy waits by the door.", B)]
    r = _row(NLP.semantic_attributes(pages), "loyal staffy")
    assert r["type"] == "temperament" and r["domains"] == 2


# ── the board block ─────────────────────────────────────────────────────────────────────────
TITLE = "4e. NLP keywords: entities, concepts, attributes"


def test_block_4e_is_on_a_new_family_board():
    import build_page_board as BPB
    from test_page_board import LEDGER_EMPTY
    slug = "blue-staffy-puppies-london"
    london = json.loads((ROOT / "data/boards" / f"{slug}.json").read_text())
    ont = json.loads((ROOT / "data/bsuk-ontology.json").read_text())
    html = BPB.render(london, ont, LEDGER_EMPTY, live={}, thumbs={}, slug=slug)
    assert f'data-title="{TITLE}"' in html
    i_d, i_e, i_5 = (html.index(f'data-title="{t}"') for t in
                     ("4d. FAQ placement", TITLE, "5. Entities"))
    assert i_d < i_e < i_5
    assert NLP.METHOD_NOTE.split(";")[0] in html


def test_block_4e_is_absent_on_a_pre_rule_board():
    import build_page_board as BPB
    from test_page_board import MIN_BOARD, ONT_OK, LEDGER_EMPTY, _approved
    old = BPB.render(_approved(MIN_BOARD), ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert TITLE not in old and "NLP keywords" not in old


def test_block_markdown_has_three_tables_and_the_method_note():
    text = "Registered with the Royal Kennel Club. We do crate training. A blue coat."
    pages = [_page(text, A), _page(text, B)]
    md = NLP.render({"entities": NLP.named_entities(pages, {"entities": []}),
                     "concepts": NLP.core_concepts(pages),
                     "attributes": NLP.semantic_attributes(pages)},
                    pool_line="Pool: 2 pages on 2 domains.")
    assert md.count("| Term |") == 3
    assert NLP.METHOD_NOTE in md
    for t in ("Royal Kennel Club", "crate training", "blue coat"):
        assert t in md


def test_cli_rejects_bad_usage(capsys):
    assert NLP.main([]) == 2
    assert NLP.main(["no-such-board-anywhere"]) == 2


def test_a_phrase_never_crosses_a_comma_or_a_dropped_and():
    text = "Kennel Club registered, health tested. Puppies are registered and health checked."
    pages = [_page(text, A), _page(text, B)]
    assert not any(t.startswith("registered") for t in _terms(NLP.core_concepts(pages)))
