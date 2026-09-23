# tests/py/test_query_augment.py — scripts/query_augment.py (spec 2026-09-23 §4, §6, §8).
# Every test builds its own repo root under tmp_path; nothing here calls a paid service.
import json
import pathlib
import subprocess
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import query_augment as Q  # noqa: E402

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "query_augment.py"

SETTINGS = {"delivery_min_gbp": 200, "guarantee_days": None,
            "query_budget_usd": 0.5, "query_total_budget_usd": 1.0,
            "query_typical_call_usd": 0.05}

TOP = ["How much does a puppy cost?", "How much is the deposit?",
       "Do you deliver across the UK?", "Can I collect my puppy?",
       "How do I reserve a puppy?", "Is there a waiting list?", "What payment do you take?"]
MIDDLE = ["What paperwork comes with the puppy?", "Is the puppy microchipped?",
          "Are the parents health tested?", "Can I visit before buying?",
          "How many weeks old is the puppy when it leaves?", "Can I meet the mother?"]
BOTTOM = ["Is a Staffy good in a flat?", "Are Staffies good with children?",
          "Are Staffies easy to train?", "What is the Staffy lifespan?", "Do Staffies shed?",
          "Are Staffies good with cats?", "Is a Staffy an aggressive dog?",
          "Do Staffies need a garden?"]


def make_root(tmp_path, bank=None, settings=None):
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data/settings.json").write_text(json.dumps(settings or SETTINGS))
    rows = bank if bank is not None else TOP + MIDDLE + BOTTOM
    faq = [{"id": f"b{i}", "q": q, "a": "…", "source": "data/settings.json"}
           for i, q in enumerate(rows)]
    (tmp_path / "data/faq.json").write_text(json.dumps(faq))
    return tmp_path


def write_raw(root, slug, name, payload):
    d = root / "data/queries/raw" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps(payload))


# --- normalise / topic / fact -------------------------------------------------------

def test_normalise_merges_staffy_spellings_and_punctuation():
    assert Q.normalise("How much are Staffie pups?") == Q.normalise("how much are staffy puppies")
    # the apostrophe goes before the synonyms run, so "terrier's" is "terriers" -> "staffy"
    assert Q.normalise("Staffordshire Bull Terrier's coat") == "staffy coat"


@pytest.mark.parametrize("text,topic,block", [
    ("How much does a blue Staffy cost?", "price", "top"),
    ("Do you deliver to Manchester?", "delivery", "top"),
    ("Is the puppy microchipped?", "paperwork", "middle"),
    ("Are the parents health tested?", "health", "middle"),
    ("Is a Staffy good in a flat?", "home", "bottom"),
    ("What is the Staffy lifespan?", "lifespan", "bottom"),
])
def test_topic_of_assigns_topic_and_block(text, topic, block):
    assert Q.topic_of(text) == (topic, block)


def test_topic_of_unknown_is_none():
    assert Q.topic_of("What is your favourite film?") == (None, None)


@pytest.mark.parametrize("text,topic", [
    ("How long does a Staffordshire Bull Terrier live?", "lifespan"),
    ("When can puppies leave their mother?", "age"),
    ("How old should a blue Staffy puppy be before it comes home?", "age"),
    ("When will my puppy come home?", "age"),
    ("What personal information does BlueStaffyUK collect?", None),
    ("Do you ship to Scotland?", "delivery"),
    ("Are blue Staffies more expensive?", "price"),
    ("Is a Staffy good for a first-time owner?", "temperament"),
    ("How long do I have to wait for a puppy?", "reserve"),
])
def test_topic_of_routes_real_bank_questions(text, topic):
    assert Q.topic_of(text)[0] == topic


@pytest.mark.parametrize("text,not_topic", [
    ("How much exercise does a Staffordshire Bull Terrier need each day?", "price"),
    ("Do you post photos of the litter?", "delivery"),
    ("Do you have testimonials?", "health"),
])
def test_topic_of_does_not_misroute(text, not_topic):
    assert Q.topic_of(text)[0] != not_topic


def test_topic_of_skip_rule_returns_no_block():
    assert Q.topic_of("What personal information does BlueStaffyUK collect?") == (None, None)


# Exact data/faq.json wording for the buyer questions that had no topic.
@pytest.mark.parametrize("text,topic", [
    ("What should I ask a blue Staffy breeder before I buy?", "trust"),
    ("How do I tell an ethical breeder from a puppy farm?", "trust"),
    ("How do I know I’m buying from reputable blue Staffy breeders?", "trust"),
    ("What makes BlueStaffyUK an ethical breeder?", "trust"),
    ("What makes BlueStaffyUK ethical as a blue Staffy breeder?", "trust"),
    ("How can I avoid buying from a puppy farm?", "trust"),
    ("Do you offer support after I take my puppy home?", "trust"),
    ("Is a Staffy a pitbull?", "breed"),
    ("What is the difference between a Staffy and a Pit Bull?", "breed"),
    ("What is the difference between an Amstaff and a Staffordshire Terrier (English)?", "breed"),
    ("How can I tell if my puppy is an American or an English Staffy?", "breed"),
    ("What two breeds make a Staffy?", "breed"),
    ("What are Staffies prone to?", "health"),
    ("Why do Staffies scratch so much?", "health"),
    ("What should I feed my new Staffy puppy for the best diet?", "care"),
    ("How long do Staffies sleep at night?", "care"),
    ("What has a puppy had before it comes home?", "paperwork"),
    ("What are the downsides of Staffies?", "temperament"),
    ("Is a male or female Staffy better?", "temperament"),
    ("Do Staffies get attached to one person?", "temperament"),
    ("Where can I find blue staffy breeders in the UK?", "reserve"),
    ("I’m looking into getting a Staffy puppy. Where should I start?", "reserve"),
])
def test_topic_of_routes_faq_bank_buyer_questions(text, topic):
    assert Q.topic_of(text)[0] == topic


@pytest.mark.parametrize("text", [
    "How long will you take to reply to my enquiry?",
    "Does this website use cookies?",
    "How often do you add a new guide?",
    "What can I read while I wait for your reply?",
])
def test_topic_of_leaves_site_questions_untopicked(text):
    assert Q.topic_of(text) == (None, None)


def test_normalise_folds_possessive_puppy():
    assert Q.normalise("puppy's price") == Q.normalise("puppy price")


def test_fact_exists_resolves_file_and_json_key(tmp_path):
    root = make_root(tmp_path)
    assert Q.fact_exists("data/settings.json", root)
    assert Q.fact_exists("data/settings.json#delivery_min_gbp", root)
    assert not Q.fact_exists("data/settings.json#guarantee_days", root)   # null is not a fact
    assert not Q.fact_exists("data/settings.json#nope", root)
    assert not Q.fact_exists("data/missing.json", root)
    assert not Q.fact_exists("../etc/passwd", root)
    assert not Q.fact_exists("/etc/passwd", root)
    assert not Q.fact_exists(None, root)


def test_fact_exists_non_json_file_with_key_is_false(tmp_path):
    (tmp_path / "notes.txt").write_text("not json")
    assert not Q.fact_exists("notes.txt#key", tmp_path)


def test_fact_exists_nested_key_and_zero_value(tmp_path):
    (tmp_path / "f.json").write_text(json.dumps({"a": {"b": {"c": 1}}, "zero": 0}))
    assert Q.fact_exists("f.json#a.b.c", tmp_path)
    assert Q.fact_exists("f.json#zero", tmp_path)
    assert not Q.fact_exists("f.json#a.b.x", tmp_path)


def test_fact_exists_unreadable_file_is_false(tmp_path, monkeypatch):
    (tmp_path / "f.json").write_text(json.dumps({"k": 1}))

    def boom(*a, **k):
        raise OSError("unreadable")

    monkeypatch.setattr(pathlib.Path, "read_text", boom)
    assert not Q.fact_exists("f.json#k", tmp_path)


def test_fit_weighs_breed_on_comparison_pages():
    assert Q.FIT["comparison"]["breed"] == 2


# --- merge / score ------------------------------------------------------------------

def test_merge_keeps_every_source_and_the_first_phrasing(tmp_path):
    root = make_root(tmp_path)
    cands = [("How much are Staffie pups?", "serp_google", "serp_google_paa", None),
             ("how much are staffy puppies", "threads", "thread:r/x/1", None),
             ("How much are staffy puppies?", "bank", "bank:b0", "data/settings.json")]
    m = Q.merge(cands, root)
    assert len(m) == 1
    (only,) = m.values()
    assert only["question"] == "How much are Staffie pups?"
    assert only["types"] == {"serp_google", "threads", "bank"}
    assert only["found_in"] == ["serp_google_paa", "thread:r/x/1", "bank:b0"]
    assert only["fact_source"] == "data/settings.json"


def test_merge_ignores_a_fact_source_that_does_not_resolve(tmp_path):
    root = make_root(tmp_path)
    m = Q.merge([("Is there a guarantee?", "serp_google", "serp_google_paa",
                  "data/settings.json#guarantee_days")], root)
    assert next(iter(m.values()))["fact_source"] is None


def test_score_is_distinct_source_types_plus_page_fit():
    assert Q.score({"serp_google", "bank"}, "delivery", "location") == 2 + 3
    assert Q.score({"bank"}, "coat", "location") == 1 + 1
    assert Q.score({"bank"}, None, "blog") == 1 + 1


# --- competitors ----------------------------------------------------------------------

def test_clean_h2s_strips_non_content_and_duplicates():
    h2 = ["Our Puppies", "Related Posts", "Frequently Asked Questions About Staffies",
          "Reviews", "Contact Us", "Our Puppies", "Health Testing", ""]
    assert Q.clean_h2s(h2) == ["Our Puppies", "Health Testing"]


def page(url, n, g=None, b=None):
    return {"url": url, "google_pos": g, "bing_pos": b, "h2": [f"Section {i}" for i in range(n)]}


def test_section_target_matches_the_highest_clean_count():
    target, rows = Q.section_target([page("a", 8, g=1), page("b", 11, b=2), page("c", 14, g=3)])
    assert target == {"matched": 14, "set_by": "c", "extra": 3, "total": 17}
    assert [r["h2_clean"] for r in rows] == [8, 11, 14]
    assert not any(r["outlier"] for r in rows)


def test_section_target_outlier_matches_the_next_highest():
    target, rows = Q.section_target([page("a", 10, g=1), page("b", 30, g=2)])
    assert target["matched"] == 10 and target["set_by"] == "a" and target["total"] == 13
    assert [r["outlier"] for r in rows] == [False, True]


def test_section_target_with_no_pages_is_zero_plus_three():
    target, rows = Q.section_target([])
    assert target == {"matched": 0, "set_by": None, "extra": 3, "total": 3} and rows == []


def test_covered_topics_reads_competitor_headings():
    pages = [{"url": "a", "h2": ["Delivery Across the North West", "Our Prices"]}]
    assert Q.covered_topics(pages) == {"delivery", "price"}


# --- picks --------------------------------------------------------------------------

def q(qid, text, sc, fact="data/settings.json"):
    topic, block = Q.topic_of(text)
    return {"id": qid, "question": text, "score": sc, "topic": topic, "block": block,
            "fact_source": fact, "faq": None}


def bank_questions():
    out = []
    for i, t in enumerate(TOP + MIDDLE + BOTTOM):
        out.append(q(f"q-{i:02d}", t, 10 - (i % 5)))
    return out


def test_pick_faq_fills_minimums_then_by_score_to_twenty():
    qs = bank_questions()
    Q.pick_faq(qs)
    counts = {b: sum(1 for x in qs if x["faq"] == b) for b in Q.BLOCKS}
    assert sum(counts.values()) == 20
    for b in Q.BLOCKS:
        assert Q.FAQ_MIN[b] <= counts[b] <= Q.FAQ_MAX[b]


def test_pick_faq_never_picks_an_unbacked_question():
    qs = bank_questions() + [q("q-zz", "How much is a puppy in Leeds?", 99, fact=None)]
    Q.pick_faq(qs)
    assert next(x for x in qs if x["id"] == "q-zz")["faq"] is None


def test_pick_faq_raises_short_naming_the_block():
    qs = [x for x in bank_questions() if x["block"] != "middle"][:] + \
         [q("q-m1", MIDDLE[0], 5), q("q-m2", MIDDLE[1], 5)]
    with pytest.raises(Q.Short) as e:
        Q.pick_faq(qs)
    assert e.value.blocks == {"middle": (2, 5)}


def test_pick_extra_prefers_topics_no_competitor_covers():
    qs = bank_questions()
    Q.pick_faq(qs)
    extras = Q.pick_extra(qs, covered={"price", "delivery", "reserve", "home", "family"})
    assert len(extras) == 3
    assert all(e["uncovered"] for e in extras)
    assert not {e["topic"] for e in extras} & {"price", "delivery", "reserve", "home", "family"}
    assert all(e["heading"] is None for e in extras)


# --- fact-source rule: non-bank candidates cite "path#key" or "bank:<id>" only ------------

@pytest.mark.parametrize("ref,expected", [
    ("data/settings.json", None),                                      # bare path: ignored
    ("bank:b0", "data/settings.json"),                                 # resolves to the row's source
    ("data/settings.json#delivery_min_gbp", "data/settings.json#delivery_min_gbp"),
    ("bank:nope", None),                                               # no such bank row
])
def test_merge_non_bank_fact_source_rule(tmp_path, ref, expected):
    root = make_root(tmp_path)
    m = Q.merge([("Do you deliver to Leeds?", "serp_google", "serp_google_paa", ref)], root)
    assert next(iter(m.values()))["fact_source"] == expected


def test_merge_bank_candidate_keeps_a_bare_path(tmp_path):
    root = make_root(tmp_path)
    m = Q.merge([("Do you deliver to Leeds?", "bank", "bank:b0", "data/settings.json")], root)
    assert next(iter(m.values()))["fact_source"] == "data/settings.json"


# --- regex gaps from the Task 2 review ----------------------------------------------

@pytest.mark.parametrize("text,topic", [
    ("Can I see the health test data?", "health"),
    ("What data do you collect?", None),
    ("How long do I need to wait for a puppy?", "reserve"),
    ("Is there a wait for puppies?", "reserve"),
    ("When does the puppy come home?", "age"),
])
def test_topic_of_task2_review_gaps(text, topic):
    assert Q.topic_of(text)[0] == topic


# --- quality review: usable competitors, furniture headings, extras, ordering --------

def test_merge_real_order_keeps_serp_wording_and_takes_the_bank_fact(tmp_path):
    # build() loads the fetched candidates first and appends the bank last.
    root = make_root(tmp_path)
    m = Q.merge([("How much are Staffie pups?", "serp_google", "serp_google_paa", "data/settings.json"),
                 ("How much are staffy puppies?", "bank", "bank:b0", "data/settings.json")], root)
    (only,) = m.values()
    assert only["question"] == "How much are Staffie pups?"
    assert only["fact_source"] == "data/settings.json"
    assert only["found_in"] == ["serp_google_paa", "bank:b0"]


@pytest.mark.parametrize("counts,matched", [
    ([12, 0], 12), ([12, 0, 0], 12), ([0, 0], 0), ([10, 30], 10), ([2, 9], 9),
])
def test_section_target_ignores_unusable_competitors(counts, matched):
    pages = [page(f"u{i}", n, g=i + 1) for i, n in enumerate(counts)]
    target, rows = Q.section_target(pages)
    assert target["matched"] == matched and target["total"] == matched + 3
    assert [r["h2_clean"] for r in rows] == counts          # every page still reported
    if matched == 0:
        assert target["set_by"] is None


def test_section_target_outlier_only_against_a_usable_second_page():
    target, rows = Q.section_target([page("a", 30, g=1), page("b", 2, g=2)])
    assert target["matched"] == 30 and not any(r["outlier"] for r in rows)


def test_section_target_tie_resolves_by_google_then_bing_then_url():
    target, _ = Q.section_target([page("z", 10, g=4), page("y", 10, g=2), page("x", 10, b=1)])
    assert target["set_by"] == "y"
    target, _ = Q.section_target([page("z", 10, b=3), page("y", 10, b=2)])
    assert target["set_by"] == "y"
    target, _ = Q.section_target([page("z", 10), page("y", 10)])
    assert target["set_by"] == "y"


FURNITURE = ["Contact Us Today", "Customer Reviews", "Google Reviews", "Reviews From Happy Owners",
             "What Our Customers Say", "Our Testimonials", "Get In Touch With Us", "Contact",
             "Call Us", "Enquire Today", "Follow Us On Instagram", "Share This Post",
             "Sign Up To Our Newsletter", "Latest News", "Useful Links", "Quick Links"]
CONTENT = ["Why Choose Us", "Our Puppies For Sale", "About Us", "Health Testing",
           "Delivery Across the North West"]


def test_clean_h2s_strips_realistic_furniture_and_keeps_content():
    assert Q.clean_h2s(FURNITURE + CONTENT) == CONTENT


# Richer than bank_questions(): after the FAQ takes 20, several topics still have questions.
EXTRA_BANK = ["What should I ask a blue Staffy breeder before I buy?",
              "How can I avoid buying from a puppy farm?",
              "Is a Staffy a pitbull?", "What two breeds make a Staffy?",
              "What are Staffies prone to?", "Why do Staffies scratch so much?",
              "What should I feed my new Staffy puppy for the best diet?",
              "How long do Staffies sleep at night?", "Is a male or female Staffy better?",
              "Do Staffies get attached to one person?", "What are the downsides of Staffies?",
              "How long does a Staffordshire Bull Terrier live?"]


def real_shaped_questions():
    qs = bank_questions()
    qs += [q(f"q-x{i:02d}", t, 4 - (i % 3)) for i, t in enumerate(EXTRA_BANK)]
    return qs


def test_pick_extra_weighs_only_questions_the_faq_left():
    qs = real_shaped_questions()
    Q.pick_faq(qs)
    extras = Q.pick_extra(qs, covered=set())
    assert len(extras) == 3
    assert all(e["question_ids"] for e in extras)
    left = {x["topic"] for x in qs if x["fact_source"] and x["topic"] and not x["faq"]}
    assert {e["topic"] for e in extras} <= left


def test_pick_extra_skips_a_topic_whose_questions_are_all_faq():
    qs = [dict(q("a1", "Do you deliver to Leeds?", 50), faq="top"),
          dict(q("a2", "Can I collect my puppy?", 50), faq="top"),
          q("c1", "Do Staffies shed?", 1), q("t1", "Are Staffies easy to train?", 1),
          q("h1", "Are the parents health tested?", 1)]
    extras = Q.pick_extra(qs, covered={"health"})
    assert [e["topic"] for e in extras] == ["coat", "training", "health"]
    assert all(e["question_ids"] for e in extras)


def test_pick_faq_crowded_block_stops_at_max_fill_by_score_then_id():
    def mk(qid, block, sc):
        return {"id": qid, "question": qid, "score": sc, "topic": "x", "block": block,
                "fact_source": "data/settings.json", "faq": None}
    qs = ([mk(f"t{i:02d}", "top", 9) for i in range(15)] +
          [mk(f"m{i:02d}", "middle", 1) for i in range(6)] +
          [mk(f"b{i:02d}", "bottom", 5) for i in range(10)])
    assert len(qs) >= 30
    Q.pick_faq(qs)
    got = {b: sorted(x["id"] for x in qs if x["faq"] == b) for b in Q.BLOCKS}
    assert got["top"] == [f"t{i:02d}" for i in range(7)]          # crowded: stops at max 7
    assert got["middle"] == [f"m{i:02d}" for i in range(5)]
    assert got["bottom"] == [f"b{i:02d}" for i in range(8)]       # next by score, then id
    assert sum(len(v) for v in got.values()) == 20


def test_clean_h2s_keeps_content_headings_that_contain_a_furniture_word():
    content = ["When to Contact a Vet", "Contact Your Vet", "Contact With Other Dogs",
               "Our Reviews and Health Guarantee", "Health Testing Reviews", "Reviews of Puppy Food"]
    assert Q.clean_h2s(content) == content
    assert Q.clean_h2s(FURNITURE + ["How to Enquire About a Puppy"]) == []
