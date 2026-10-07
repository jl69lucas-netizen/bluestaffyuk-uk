"""FAQ near-copy check (Manchester plan, Phase F gap G15; STOP 2 q03 (b), 2026-10-07).

The collision gate (`PB.header_precheck`, `PB.faq_hits`) passes a question that differs from a
live one by a single word: "How Much Is Your Deposit?" is not an exact, template or five-token
shingle copy of "How Much Is the Deposit?", yet a reader and a search engine read it as the same
question. `PB.near_copy_hits(questions, corpus)` reads each question as its CONTENT tokens
(`PB.tokens()` with `keyword_metrics.STOP` and the pronouns dropped) and calls it a near-copy when:

  * its content-token set is within two tokens of another question's (symmetric difference <= 2),
    or
  * it shares a run of five content tokens with one, in either order: a spent run that a stop
    word was slipped into ("L-2-HGA and for HC-HSF4") or that was turned round ("HC-HSF4 and
    L-2-HGA") is still the same run.

The corpus is every live heading (`PB.live_headings()`), every board's FAQ questions
(`PB.faq_block_questions`) and every `data/faq.json` question (`PB.near_copy_corpus()`). The board
shows a hit as a WARN in block 3.
"""
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import pageboard as PB  # noqa: E402

MANCHESTER = "/uk-locations/blue-staffy-puppies-manchester-uk/"
OWN = (MANCHESTER, "board:blue-staffy-puppies-manchester-uk")

DEPOSIT = "How Much Is Your Deposit?"
DELIVER = "Do You Deliver Puppies Across the UK?"
DNA = "Are Both Parents DNA Tested Clear for L-2-HGA and for HC-HSF4?"


@pytest.fixture(scope="module")
def corpus():
    if not (ROOT / "dist" / "index.html").is_file():
        pytest.skip("run npm run -s build first")
    return PB.near_copy_corpus()


def _hit(hits, question):
    found = [h for h in hits if h["heading"] == question]
    assert found, f"no near-copy hit for {question!r}"
    return found[0]


def test_the_corpus_is_live_headings_board_faqs_and_the_faq_bank(corpus):
    assert "How Much Is the Deposit?" in corpus["/uk-blue-staffy-breeders-contact/"]
    assert any(k.startswith("board:") for k in corpus)
    assert "Do you deliver across the UK?" in corpus["data/faq.json"]


def test_the_thin_deposit_wording_is_a_near_copy_of_how_much_is_the_deposit(corpus):
    hit = _hit(PB.near_copy_hits([DEPOSIT], corpus, exclude_page=OWN), DEPOSIT)
    assert hit["with"] == "How Much Is the Deposit?"
    assert hit["kind"] == "near-copy"


def test_the_thin_delivery_wording_is_a_near_copy_of_do_you_deliver_across_the_uk(corpus):
    hit = _hit(PB.near_copy_hits([DELIVER], corpus, exclude_page=OWN), DELIVER)
    assert PB.tokens(hit["with"]) == PB.tokens("Do You Deliver Across the UK?")


def test_the_thin_dna_wording_repeats_the_spent_test_name_run(corpus):
    hit = _hit(PB.near_copy_hits([DNA], corpus, exclude_page=OWN), DNA)
    assert hit["kind"] == "near-run"
    assert set(hit["run"].split()) == {"l", "2", "hga", "hc", "hsf4"}
    pages = {p for p, _ in hit["matches"]}
    # London's "What Are L-2-HGA and HC-HSF4, …" and the health page's "HC-HSF4 and L-2-HGA Tested
    # Staffy Breeders" (the run turned round) are both found.
    assert "/uk-locations/blue-staffy-puppies-london/" in pages
    assert "/blue-staffy-health-uk/" in pages


def test_the_page_being_built_is_never_its_own_near_copy(corpus):
    hits = PB.near_copy_hits([DEPOSIT, DELIVER, DNA], corpus, exclude_page=OWN)
    assert all(p not in OWN for h in hits for p, _ in h["matches"])


def test_no_hit_against_an_unrelated_corpus():
    unrelated = {"/care/": ["How Often Should I Walk a Staffy?", "What Should a Puppy Eat at Eight Weeks?"]}
    assert PB.near_copy_hits(["How Much Is the Deposit?"], unrelated) == []


def test_three_words_apart_is_not_a_near_copy():
    live = {"/x/": ["How Much Is the Deposit for a Blue Staffy Puppy?"]}
    assert PB.near_copy_hits(["How Much Is the Deposit?"], live) == []


def test_a_question_of_stop_words_alone_is_never_a_hit():
    assert PB.near_copy_hits(["Is It?"], {"/x/": ["Are They?"]}) == []


def test_the_board_warns_in_block_3():
    import build_page_board as BPB
    ont, ledger = PB.load_ontology(), PB.load_ledger()
    board = PB.load_board("blue-staffy-puppies-london")
    q = PB.faq_block_questions(board)[0]
    live = {"/elsewhere/": [q.rstrip("?") + " Now?"]}     # one word added: a near-copy
    hits = PB.board_near_copy_hits(board, live, boards={}, bank=[])
    assert hits and hits[0]["kind"] == "near-copy"
    html = BPB.render(board, ont, ledger, live, {}, "blue-staffy-puppies-london", layout="flat")
    assert "FAQ question(s) are near-copies" in html and q in html
