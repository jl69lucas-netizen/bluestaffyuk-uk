import json
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import faq_layout as FL
import query_augment as QA

FS = "data/faq.json"
SPREAD_QS = [{"text": t, "fact_source": FS} for t in (
    "How much does a puppy cost?", "How do you deliver to London?", "Are they health tested?",
    "Are blue Staffies aggressive?", "Are they good with children?", "How do I crate train a puppy?")]
BUYING = SPREAD_QS[:2]
DOG = SPREAD_QS[2:4]
LIVING = SPREAD_QS[4:]


def test_fixture_texts_hit_the_expected_topics():
    assert [QA.topic_of(q["text"])[0] for q in SPREAD_QS] == [
        "price", "delivery", "health", "temperament", "family", "training"]


def test_intent_groups_cover_every_topic():
    assert set(FL.INTENT_GROUPS) == {t for t, _, _ in QA.TOPICS}
    assert set(FL.INTENT_GROUPS.values()) == set(FL.GROUPS) == {"buying", "dog", "living"}
    assert "other" not in FL.INTENT_GROUPS


def test_option_a_three_blocks_when_intents_spread_and_long():
    r = FL.decide(SPREAD_QS, words=2400, page_type="blog", method="A")
    assert r["groups"] == {"buying": 2, "dog": 2, "living": 2}
    assert r["layout"] == "top-middle-bottom"


def test_option_a_bottom_only_when_short():
    assert FL.decide(SPREAD_QS, words=1200, page_type="location", method="A")["layout"] == "bottom"


def test_care_blog_with_only_dog_and_living_is_bottom():
    r = FL.decide(DOG + LIVING + DOG, words=3000, page_type="blog", method="A")
    assert r["groups"]["buying"] == 0
    assert r["layout"] == "bottom"


def test_group_with_one_question_does_not_count():
    r = FL.decide(BUYING + DOG + LIVING[:1], words=3000, page_type="blog", method="A")
    assert r["groups"] == {"buying": 2, "dog": 2, "living": 1}
    assert r["layout"] == "bottom"


def test_option_b_by_type():
    assert FL.decide([], words=0, page_type="location", method="B")["layout"] == "top-middle-bottom"
    assert FL.decide([], words=0, page_type="for-sale", method="B")["layout"] == "top-middle-bottom"
    assert FL.decide([], words=5000, page_type="blog", method="B")["layout"] == "bottom"


def test_own_topic_key_wins_over_regex():
    qs = [{"text": "How much does a puppy cost?", "topic": "health", "fact_source": FS}]
    assert FL.decide(qs, words=0, page_type="blog", method="A")["groups"]["dog"] == 1


def test_unmatched_text_is_other_and_in_no_group():
    assert FL.topic_of({"text": "Zebra crossing?"}) == "other"
    assert FL.group_counts([{"text": "Zebra crossing?", "fact_source": FS}]) == {
        "buying": 0, "dog": 0, "living": 0}


def test_question_without_fact_source_key_is_ignored():
    qs = list(SPREAD_QS)
    qs[5] = {"text": qs[5]["text"]}
    assert FL.decide(qs, words=3000, page_type="blog", method="A")["groups"]["living"] == 1


def test_decide_returns_why_for_both_methods():
    a = FL.decide(SPREAD_QS, words=2400, page_type="location", method="A")
    b = FL.decide(SPREAD_QS, words=2400, page_type="location", method="B")
    assert a["why"].startswith("buying 2 · dog 2 · living 2; 2,400 words")
    assert "page type `location` is one of" in b["why"] and "buying 2" in b["why"]
    assert "buying" not in FL.decide(None, words=0, page_type="blog", method="B")["why"]


def test_questions_without_a_fact_source_are_ignored_picked_or_not():
    qs = [dict(q, fact_source="data/faq.json", faq=None) for q in SPREAD_QS]
    qs[5] = dict(qs[5], fact_source=None, faq="bottom")
    r = FL.decide(qs, words=3000, page_type="blog", method="A")
    assert r["groups"] == {"buying": 2, "dog": 2, "living": 1}
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
    qs = [{"question": q["text"], "fact_source": "data/faq.json", "faq": None} for q in SPREAD_QS]
    sections = [{"id": "body", "words": {"min": 1900, "max": 2100}}, {"id": "faq-bottom", "words": 200}]
    out = FL.block(_fixture(tmp_path, qs, sections), root=tmp_path)
    assert "| Method | Result for this page | Why |" in out
    assert "A · intent spread (Recommended) | top-middle-bottom" in out
    assert "buying 2 · dog 2 · living 2; 2,200 words" in out
    assert "every fact-backed question" in out
    assert "outline currently has **bottom**" in out
    assert "Mismatch" in out  # A says top-middle-bottom, outline has one bottom block


def test_block_no_mismatch_when_outline_agrees(tmp_path):
    qs = [{"question": SPREAD_QS[0]["text"], "fact_source": "data/faq.json"}]
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
