import json
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import faq_layout as FL
import query_augment as QA

SPREAD_QS = [{"text": "How much does a puppy cost?"}, {"text": "How do you deliver to London?"},
             {"text": "Are they health tested?"}]


def test_fixture_texts_hit_three_distinct_topics():
    assert [QA.topic_of(q["text"])[0] for q in SPREAD_QS] == ["price", "delivery", "health"]


def test_option_a_three_blocks_when_intents_spread_and_long():
    assert FL.decide(SPREAD_QS, words=2400, page_type="blog", method="A")["layout"] == "top-middle-bottom"


def test_option_a_bottom_only_when_short():
    assert FL.decide(SPREAD_QS, words=1200, page_type="location", method="A")["layout"] == "bottom"


def test_option_b_by_type():
    assert FL.decide([], words=0, page_type="location", method="B")["layout"] == "top-middle-bottom"
    assert FL.decide([], words=5000, page_type="blog", method="B")["layout"] == "bottom"


def test_one_topic_repeated_is_not_spread():
    qs = [{"text": "How much does a puppy cost?"}, {"text": "Is there a deposit?"},
          {"text": "What is the price?"}, {"text": "Can I pay in instalments?"}]
    r = FL.decide(qs, words=3000, page_type="blog", method="A")
    assert r["topics"] == ["price"]
    assert r["layout"] == "bottom"


def test_own_topic_key_wins_over_regex():
    qs = [{"text": "How much does a puppy cost?", "topic": "health"}]
    assert FL.decide(qs, words=0, page_type="blog", method="A")["topics"] == ["health"]


def test_unmatched_text_is_other():
    assert FL.topic_of({"text": "Zebra crossing?"}) == "other"


def test_unpicked_questions_are_ignored():
    qs = [dict(SPREAD_QS[0], faq="top"), dict(SPREAD_QS[1], faq=False),
          dict(SPREAD_QS[2], faq=None)]
    r = FL.decide(qs, words=3000, page_type="blog", method="A")
    assert r["topics"] == ["price"]
    assert r["layout"] == "bottom"


def test_word_target_is_sum_of_midpoints():
    board = {"sections": [{"id": "a", "words": {"min": 90, "max": 110}}, {"id": "b", "words": 50}]}
    assert FL.word_target(board) == 150


def test_outline_layout_counts_faq_sections():
    three = {"sections": [{"id": "faq-top"}, {"id": "x"}, {"id": "faq-middle"}, {"id": "faq-bottom"}]}
    one = {"sections": [{"id": "x"}, {"id": "faq-bottom"}]}
    assert FL.outline_layout(three) == "top-middle-bottom"
    assert FL.outline_layout(one) == "bottom"
    assert FL.outline_layout({"sections": [{"id": "x"}]}) == "none"


def _fixture(tmp_path, qs, sections, page_type="blog", write_queries=True):
    slug = "test-page"
    if write_queries:
        (tmp_path / "data/queries").mkdir(parents=True)
        (tmp_path / "data/queries" / f"{slug}.json").write_text(
            json.dumps({"slug": slug, "questions": qs}), encoding="utf-8")
    return {"meta": {"slug": slug, "page_type": page_type}, "sections": sections}


def test_block_on_fixture_board(tmp_path):
    qs = [{"question": q["text"], "faq": "bottom"} for q in SPREAD_QS]
    sections = [{"id": "body", "words": {"min": 1900, "max": 2100}}, {"id": "faq-bottom", "words": 200}]
    out = FL.block(_fixture(tmp_path, qs, sections), root=tmp_path)
    assert "| Method | Result for this page | Why |" in out
    assert "A · intent spread (Recommended)" in out
    assert "3 topics (delivery, health, price)" in out
    assert "2,200 words" in out
    assert "outline currently has **bottom**" in out
    assert "Mismatch" in out  # A says top-middle-bottom, outline has one bottom block


def test_block_no_mismatch_when_outline_agrees(tmp_path):
    qs = [{"question": SPREAD_QS[0]["text"], "faq": "bottom"}]
    sections = [{"id": "body", "words": 800}, {"id": "faq-bottom", "words": 200}]
    out = FL.block(_fixture(tmp_path, qs, sections), root=tmp_path)
    assert "Mismatch" not in out
    assert "agrees" in out


def test_block_question_file_missing(tmp_path):
    board = _fixture(tmp_path, [], [{"id": "faq-bottom", "words": 200}], write_queries=False)
    out = FL.block(board, root=tmp_path)
    assert "NOT FETCHED — no data/queries/test-page.json" in out
    assert "Mismatch" not in out


def test_cli_usage(capsys):
    assert FL.main([]) == 2
    assert "usage" in capsys.readouterr().err
    assert FL.main(["no-such-page-xyz"]) == 2
