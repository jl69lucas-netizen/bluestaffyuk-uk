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


def test_score_weighs_buyer_sources_twice_the_bank_plus_page_fit():
    assert Q.score({"serp_google", "bank"}, "delivery", "location") == 2 + 1 + 3
    assert Q.score({"bank"}, "delivery", "location") == 1 + 3
    assert Q.score({"bank"}, "coat", "location") == 1 + 1
    assert Q.score({"bank"}, None, "blog") == 1 + 1
    assert Q.score({"serp_google", "serp_bing", "threads"}, "coat", "blog") == 6 + 1


# --- competitors ----------------------------------------------------------------------

def test_clean_h2s_strips_non_content_and_duplicates():
    h2 = ["Our Puppies", "Related Posts", "Frequently Asked Questions About Staffies",
          "Reviews", "Contact Us", "Our Puppies", "Health Testing", ""]
    assert Q.clean_h2s(h2) == ["Our Puppies", "Health Testing"]


def page(url, n, g=None, b=None):
    return {"url": url, "google_pos": g, "bing_pos": b, "h2": [f"Section {i}" for i in range(n)]}


def test_section_target_matches_the_highest_clean_count():
    target, rows = Q.section_target([page("a", 8, g=1), page("b", 11, b=2), page("c", 14, g=3)])
    assert target == {"matched": 14, "set_by": "c", "extra": 3, "floor": 9, "total": 17}
    assert [r["h2_clean"] for r in rows] == [8, 11, 14]
    assert not any(r["outlier"] for r in rows)


def test_section_target_outlier_matches_the_next_highest():
    target, rows = Q.section_target([page("a", 10, g=1), page("b", 30, g=2)])
    assert target["matched"] == 10 and target["set_by"] == "a" and target["total"] == 13
    assert [r["outlier"] for r in rows] == [False, True]


def test_section_target_with_no_pages_is_the_floor():
    target, rows = Q.section_target([])
    assert target == {"matched": 0, "set_by": None, "extra": 3, "floor": 9, "total": 9}
    assert rows == []


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
    qs = real_shaped_questions()   # the two-per-topic cap leaves questions behind
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
    assert target["matched"] == matched and target["total"] == max(matched + 3, 9)
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


# --- spend / preflight --------------------------------------------------------------

NOW = "2026-09-23T10:00:00Z"


def test_record_appends_to_the_spend_log(tmp_path):
    root = make_root(tmp_path)
    Q.record("m", "serp_google", "serp_organic_live_advanced", 0.002, root, now=NOW)
    Q.record("m", "ai_engines", "llm_response", 0.01, root, now=NOW)
    log = json.loads((root / "data/queries/spend.json").read_text())
    assert [e["cost_usd"] for e in log] == [0.002, 0.01]
    assert log[0] == {"ts": NOW, "slug": "m", "source": "serp_google",
                      "endpoint": "serp_organic_live_advanced", "cost_usd": 0.002}


def test_preflight_cached_makes_no_call(tmp_path):
    root = make_root(tmp_path)
    write_raw(root, "m", "serp_google", {"source": "serp_google", "status": "ok", "questions": []})
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_CACHED
    assert Q.preflight("m", "serp_google", root, refresh=True, today="2026-09-23") == Q.EXIT_OK


def test_preflight_refuses_over_the_page_budget(tmp_path):
    root = make_root(tmp_path)
    Q.record("m", "ai_engines", "llm_response", 0.46, root, now=NOW)
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_BUDGET
    # another day is another run
    assert Q.preflight("m", "serp_google", root, today="2026-09-24") == Q.EXIT_OK


def test_preflight_refuses_over_the_total_budget(tmp_path):
    root = make_root(tmp_path)
    for slug in ("a", "b", "c"):
        Q.record(slug, "ai_engines", "llm_response", 0.32, root, now=NOW)
    assert Q.preflight("d", "serp_google", root, today="2026-09-30") == Q.EXIT_BUDGET


def test_preflight_uses_the_largest_observed_cost_for_that_source(tmp_path):
    root = make_root(tmp_path)
    Q.record("x", "ai_engines", "llm_response", 0.30, root, now=NOW)
    # page m has spent nothing, but one ai_engines call has been seen to cost 0.30
    Q.record("m", "serp_google", "serp", 0.25, root, now=NOW)
    assert Q.preflight("m", "ai_engines", root, today="2026-09-23") == Q.EXIT_BUDGET


def test_preflight_free_source_is_never_budget_limited(tmp_path):
    root = make_root(tmp_path)
    Q.record("m", "ai_engines", "llm_response", 0.9, root, now=NOW)
    assert Q.preflight("m", "threads", root, today="2026-09-23") == Q.EXIT_OK


def test_preflight_without_a_budget_setting_fails_closed(tmp_path):
    root = make_root(tmp_path, settings={"delivery_min_gbp": 200})
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_BUDGET


# --- spend guard hardening ------------------------------------------------------------

def test_preflight_a_saved_response_alone_counts_as_cached(tmp_path):
    root = make_root(tmp_path)
    d = root / "data/queries/raw/m"
    d.mkdir(parents=True)
    (d / "serp_google.response.json").write_text("{}")
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_CACHED


@pytest.mark.parametrize("cost", [float("nan"), float("inf"), -0.002])
def test_record_refuses_a_bad_cost(tmp_path, cost):
    root = make_root(tmp_path)
    with pytest.raises(ValueError):
        Q.record("m", "serp_google", "serp", cost, root, now=NOW)
    assert not (root / "data/queries/spend.json").exists()


@pytest.mark.parametrize("cost", ["NaN", "Infinity"])
def test_preflight_refuses_a_log_with_a_non_finite_cost(tmp_path, cost):
    root = make_root(tmp_path)
    (root / "data/queries").mkdir(parents=True)
    (root / "data/queries/spend.json").write_text(
        '[{"ts": "%s", "slug": "x", "source": "serp_google", "endpoint": "serp", "cost_usd": %s}]'
        % (NOW, cost))
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_BUDGET


def test_a_damaged_spend_log_blocks_calls_and_is_never_overwritten(tmp_path, capsys):
    root = make_root(tmp_path)
    Q.record("m", "serp_google", "serp", 0.01, root, now=NOW)
    path = root / "data/queries/spend.json"
    damaged = path.read_text()[:-10]
    path.write_text(damaged)
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_BUDGET
    assert capsys.readouterr().err.strip()
    with pytest.raises(ValueError):
        Q.record("m", "serp_google", "serp", 0.01, root, now=NOW)
    assert path.read_text() == damaged


@pytest.mark.parametrize("log", ['[{"slug": "x"}]', '{"a": 1}', '[1]'])
def test_a_malformed_spend_log_blocks_calls(tmp_path, log):
    root = make_root(tmp_path)
    (root / "data/queries").mkdir(parents=True)
    (root / "data/queries/spend.json").write_text(log)
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_BUDGET


def test_damaged_settings_block_calls(tmp_path):
    root = make_root(tmp_path)
    (root / "data/settings.json").write_text('{"query_budget_usd": 0.5,')
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_BUDGET


def test_record_leaves_no_temp_file_behind(tmp_path):
    root = make_root(tmp_path)
    Q.record("m", "serp_google", "serp", 0.01, root, now=NOW)
    assert [p.name for p in (root / "data/queries").iterdir()] == ["spend.json"]


def test_preflight_rejects_a_malformed_day(tmp_path):
    root = make_root(tmp_path)
    with pytest.raises(ValueError):
        Q.preflight("m", "serp_google", root, today="23-09-2026")


def test_an_observed_zero_cost_does_not_lower_the_estimate(tmp_path):
    root = make_root(tmp_path)
    Q.record("m", "ai_engines", "llm_response", 0.47, root, now=NOW)
    Q.record("x", "serp_google", "serp", 0.0, root, now=NOW)
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_BUDGET


def test_spend_plus_typical_exactly_at_the_cap_proceeds(tmp_path):
    root = make_root(tmp_path)
    Q.record("m", "ai_engines", "llm_response", 0.45, root, now=NOW)
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_OK


def test_the_settings_typical_overrides_the_default(tmp_path):
    root = make_root(tmp_path, settings={**SETTINGS, "query_typical_call_usd": 0.2})
    Q.record("m", "ai_engines", "llm_response", 0.35, root, now=NOW)
    assert Q.preflight("m", "serp_google", root, today="2026-09-23") == Q.EXIT_BUDGET


# --- build / CLI --------------------------------------------------------------------

import jsonschema  # noqa: E402

SCHEMA = json.loads((pathlib.Path(__file__).resolve().parents[2]
                     / "schemas/queries.schema.json").read_text())
ROUTE = "/uk-locations/m/"          # the last segment must equal the slug


def run(root, *args):
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), *args],
                          capture_output=True, text=True)


def seed(root, slug="m"):
    write_raw(root, slug, "serp_google", {"source": "serp_google", "status": "ok", "questions": [
        {"text": "Do you deliver Staffy puppies to Manchester?", "detail": "serp_google_paa",
         "fact_source": "data/settings.json#delivery_min_gbp"},
        {"text": "Is there a Staffy puppy guarantee?", "detail": "serp_google_paa",
         "fact_source": "data/settings.json#guarantee_days"}]})
    write_raw(root, slug, "competitors", {"status": "ok", "pages": [
        {"url": "https://a.example", "google_pos": 1, "bing_pos": None,
         "h2": ["Our Prices", "Delivery to Manchester", "Health Testing",
                "Our Puppies For Sale", "Reviews"]}]})


def test_build_writes_a_schema_valid_file(tmp_path):
    root = make_root(tmp_path); seed(root)
    r = run(root, "m", "--page-type", "location", "--keyword", "blue staffy puppies manchester",
            "--route", ROUTE, "--today", "2026-09-23")
    assert r.returncode == 0, r.stderr
    data = json.loads((root / "data/queries/m.json").read_text())
    jsonschema.validate(data, SCHEMA)
    assert data["sources"]["serp_google"] == "ok"
    assert data["sources"]["serp_bing"] == "NOT FETCHED"
    assert data["sources"]["bank"] == "ok"
    assert data["section_target"] == {"matched": 4, "set_by": "https://a.example",
                                      "extra": 3, "floor": 9, "total": 9}
    faq = [x for x in data["questions"] if x["faq"]]
    assert 17 <= len(faq) <= 20
    assert all(x["must_answer"] for x in faq)


def test_build_never_makes_an_unbacked_question_must_answer(tmp_path):
    root = make_root(tmp_path); seed(root)
    run(root, "m", "--page-type", "location", "--keyword", "k", "--route", ROUTE,
        "--today", "2026-09-23")
    data = json.loads((root / "data/queries/m.json").read_text())
    g = next(x for x in data["questions"] if "guarantee" in x["question"].lower())
    assert g["must_answer"] is False and g["blocked"] == "unverified fact"


def test_build_carries_over_covered_by_and_headings(tmp_path):
    root = make_root(tmp_path); seed(root)
    args = ("m", "--page-type", "location", "--keyword", "k", "--route", ROUTE,
            "--today", "2026-09-23")
    run(root, *args)
    f = root / "data/queries/m.json"
    data = json.loads(f.read_text())
    first = next(x for x in data["questions"] if x["faq"])
    first["covered_by"] = {"where": "faq", "text": first["question"]}
    data["extra_sections"][0]["heading"] = "A Heading We Wrote"
    f.write_text(json.dumps(data))
    run(root, *args)
    again = json.loads(f.read_text())
    assert next(x for x in again["questions"] if x["id"] == first["id"])["covered_by"] == \
        first["covered_by"]
    assert again["extra_sections"][0]["heading"] == "A Heading We Wrote"


def test_build_short_exits_5_and_lists_what_is_blocked(tmp_path):
    root = make_root(tmp_path, bank=TOP + BOTTOM)          # no middle questions at all
    seed(root)
    r = run(root, "m", "--page-type", "location", "--keyword", "k", "--route", ROUTE,
            "--today", "2026-09-23")
    assert r.returncode == Q.EXIT_SHORT
    assert "middle: 0/5" in r.stdout
    assert not (root / "data/queries/m.json").exists()


def test_cli_preflight_and_record(tmp_path):
    root = make_root(tmp_path)
    assert run(root, "--preflight", "m", "--source", "serp_google",
               "--today", "2026-09-23").returncode == 0
    assert run(root, "--record", "m", "--source", "serp_google", "--endpoint", "serp",
               "--cost", "0.002").returncode == 0
    assert json.loads((root / "data/queries/spend.json").read_text())[0]["cost_usd"] == 0.002


def test_cli_rejects_an_unknown_page_type(tmp_path):
    root = make_root(tmp_path)
    r = run(root, "m", "--page-type", "hub", "--keyword", "k", "--route", ROUTE)
    assert r.returncode == 2


@pytest.mark.parametrize("cost", ["nan", "inf", "-0.002"])
def test_cli_record_refuses_a_bad_cost_cleanly(tmp_path, cost):
    root = make_root(tmp_path)
    r = run(root, "--record", "m", "--source", "serp_google", "--endpoint", "serp",
            "--cost", cost)
    assert r.returncode == Q.EXIT_USAGE
    assert "Traceback" not in r.stderr
    assert len(r.stderr.strip().splitlines()) == 1
    assert not (root / "data/queries/spend.json").exists()


def test_cli_preflight_rejects_a_malformed_today_cleanly(tmp_path):
    root = make_root(tmp_path)
    r = run(root, "--preflight", "m", "--source", "serp_google", "--today", "23-09-2026")
    assert r.returncode == Q.EXIT_USAGE
    assert "Traceback" not in r.stderr
    assert "YYYY-MM-DD" in r.stderr


# --- quality review: stable ids, bad input, slug/route, short re-runs -----------------

MANC = "How much does a blue Staffy puppy cost in Manchester?"
# Same first 8 words and sorts first; different enough (Jaccard 2/7) not to collapse into MANC.
LEEDS = "How much does a blue Staffy puppy cost in Leeds including vaccinations and food?"
BUILD = ("m", "--page-type", "location", "--keyword", "k", "--route", ROUTE,
         "--today", "2026-09-23")


def add_raw_question(root, source, text, slug="m"):
    f = root / "data/queries/raw" / slug / f"{source}.json"
    d = json.loads(f.read_text()) if f.exists() else {"source": source, "status": "ok",
                                                       "questions": []}
    d["questions"].append({"text": text, "detail": f"{source}_paa",
                           "fact_source": "data/settings.json#delivery_min_gbp"})
    f.write_text(json.dumps(d))


def test_ids_survive_a_new_question_that_sorts_first(tmp_path):
    root = make_root(tmp_path); seed(root)
    add_raw_question(root, "serp_google", MANC)
    assert run(root, *BUILD).returncode == 0
    f = root / "data/queries/m.json"
    first = json.loads(f.read_text())
    manc = next(x for x in first["questions"] if x["question"] == MANC)
    manc["covered_by"] = {"where": "heading", "text": "Staffy puppy prices in Manchester"}
    f.write_text(json.dumps(first))
    add_raw_question(root, "serp_bing", LEEDS)
    r = run(root, *BUILD)
    assert r.returncode == 0, r.stderr
    again = json.loads(f.read_text())
    by_q = {x["question"]: x for x in again["questions"]}
    assert by_q[MANC]["covered_by"] == manc["covered_by"]
    assert by_q[LEEDS]["covered_by"] is None
    old_ids = {x["question"]: x["id"] for x in first["questions"]}
    assert all(by_q[t]["id"] == i for t, i in old_ids.items())
    assert len({x["id"] for x in again["questions"]}) == len(again["questions"])


def test_question_id_is_a_pure_function_of_the_text():
    n = Q.normalise(MANC)
    assert Q._question_id(n) == Q._question_id(n)
    assert Q._question_id(n) != Q._question_id(Q.normalise(LEEDS))
    assert len(Q._question_id(n)) <= 50


def test_the_write_message_counts_kept_and_dropped_fills(tmp_path):
    root = make_root(tmp_path); seed(root)
    run(root, *BUILD)
    f = root / "data/queries/m.json"
    data = json.loads(f.read_text())
    data["questions"][0]["covered_by"] = {"where": "faq", "text": "x"}
    data["questions"].append({**data["questions"][1], "id": "q-gone", "question": "A gone question?",
                              "covered_by": {"where": "faq", "text": "y"}})
    data["extra_sections"][0]["heading"] = "Kept Heading"
    f.write_text(json.dumps(data))
    r = run(root, *BUILD)
    assert "kept 1 covered_by and 1 headings, dropped 1" in r.stdout


@pytest.mark.parametrize("name,payload", [
    ("serp_google", {"status": "ok", "questions": [{"detail": "serp_google_paa"}]}),
    ("serp_google", [{"text": "Is a list at the top level ok?"}]),
    ("serp_google", {"status": "ok", "questions": [{"text": 7}]}),
    ("serp_google", "BROKEN"),
    ("competitors", {"status": "ok"}),
    ("competitors", {"status": "ok", "pages": [{"url": "https://a.example", "google_pos": "1",
                                                "bing_pos": None, "h2": []}]}),
])
def test_bad_input_exits_6_with_one_line_and_writes_nothing(tmp_path, name, payload):
    root = make_root(tmp_path); seed(root)
    f = root / "data/queries/raw/m" / f"{name}.json"
    f.write_text('{"status": "ok", "questions": [' if payload == "BROKEN" else json.dumps(payload))
    r = run(root, *BUILD)
    assert r.returncode == Q.EXIT_BAD_INPUT == 6
    lines = r.stderr.strip().splitlines()
    assert len(lines) == 1 and lines[0].startswith("query_augment.py: bad input: ")
    assert f"{name}.json" in lines[0]
    assert not (root / "data/queries/m.json").exists()


def test_an_unparseable_previous_file_is_bad_input(tmp_path):
    root = make_root(tmp_path); seed(root)
    (root / "data/queries/m.json").write_text("{not json")
    r = run(root, *BUILD)
    assert r.returncode == Q.EXIT_BAD_INPUT
    assert (root / "data/queries/m.json").read_text() == "{not json"


EVIL = "../../evil"


@pytest.mark.parametrize("args", [
    ("--preflight", EVIL, "--source", "serp_google", "--today", "2026-09-23"),
    ("--record", EVIL, "--source", "serp_google", "--endpoint", "serp", "--cost", "0.01"),
    (EVIL, "--page-type", "location", "--keyword", "k", "--route", "/uk-locations/evil/"),
])
def test_a_path_like_slug_is_refused_in_every_mode(tmp_path, args):
    root = make_root(tmp_path / "repo")
    before = sorted(p for p in tmp_path.rglob("*"))
    r = run(root, *args)
    assert r.returncode == 2
    assert "slug" in r.stderr
    assert sorted(p for p in tmp_path.rglob("*")) == before


@pytest.mark.parametrize("route", ["/uk-locations/other/", "/uk-locations/m", "uk-locations/m/",
                                   "/UK/m/"])
def test_a_route_that_does_not_end_in_the_slug_is_refused(tmp_path, route):
    root = make_root(tmp_path); seed(root)
    r = run(root, "m", "--page-type", "location", "--keyword", "k", "--route", route)
    assert r.returncode == 2
    assert not (root / "data/queries/m.json").exists()


def test_the_modes_are_mutually_exclusive(tmp_path):
    root = make_root(tmp_path)
    r = run(root, "m", "--preflight", "m", "--source", "serp_google")
    assert r.returncode == 2
    r = run(root, "--preflight", "m", "--record", "m", "--source", "serp_google",
            "--endpoint", "serp", "--cost", "0.01")
    assert r.returncode == 2
    assert not (root / "data/queries/spend.json").exists()


def test_a_short_rerun_leaves_the_existing_file_unchanged(tmp_path):
    root = make_root(tmp_path); seed(root)
    assert run(root, *BUILD).returncode == 0
    f = root / "data/queries/m.json"
    before = f.read_text()
    make_root(tmp_path, bank=TOP + BOTTOM)
    r = run(root, *BUILD)
    assert r.returncode == Q.EXIT_SHORT
    assert "existing data/queries/m.json left unchanged" in r.stdout
    assert f.read_text() == before


def test_short_carries_the_blocked_list(tmp_path):
    root = make_root(tmp_path, bank=TOP + BOTTOM); seed(root)
    add_raw_question(root, "serp_google", "Is the puppy vaccinated?")
    (root / "data/queries/raw/m/threads.json").write_text(json.dumps(
        {"status": "ok", "questions": [{"text": "Are the puppy's parents health tested here?"}]}))
    with pytest.raises(Q.Short) as e:
        Q.build("m", "location", "k", ROUTE, root, "2026-09-23")
    assert ("middle", "Are the puppy's parents health tested here?") in e.value.blocked


def test_a_missing_bank_is_not_fetched(tmp_path):
    root = make_root(tmp_path)
    (root / "data/faq.json").unlink()
    assert Q.bank_candidates(root) == ([], "NOT FETCHED")
    assert Q.bank_candidates(make_root(tmp_path))[1] == "ok"


def test_a_bank_row_without_a_string_q_is_bad_input(tmp_path):
    root = make_root(tmp_path)
    (root / "data/faq.json").write_text(json.dumps([{"id": "b1", "q": None}]))
    with pytest.raises(Q.BadInput):
        Q.bank_candidates(root)


def test_a_built_dict_that_breaks_the_schema_is_an_internal_error(tmp_path, monkeypatch, capsys):
    root = make_root(tmp_path); seed(root)
    monkeypatch.setattr(Q, "build", lambda *a, **k: ({"slug": "m"},
                                                     {"kept": 0, "dropped": 0}))
    assert Q.main(["--root", str(root), *BUILD]) == 1
    err = capsys.readouterr().err.strip().splitlines()
    assert len(err) == 1 and "internal error" in err[0] and "Traceback" not in err[0]
    assert not (root / "data/queries/m.json").exists()


def test_build_default_today_is_the_utc_date(tmp_path, monkeypatch):
    root = make_root(tmp_path); seed(root)
    data, _ = Q.build("m", "location", "k", ROUTE, root)
    import datetime as dt
    assert data["fetched"] == dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")



def test_build_returns_the_file_and_its_fill_counts(tmp_path):
    root = make_root(tmp_path); seed(root)
    data, fills = Q.build("m", "location", "k", ROUTE, root, "2026-09-23")
    assert "_fills" not in data
    jsonschema.validate(data, SCHEMA)
    assert fills["kept"] == 0 and fills["dropped"] == 0


@pytest.mark.parametrize("where,value", [
    ("covered_by", {"where": "body", "text": "x"}),
    ("covered_by", "yes"),
    ("covered_by", {"where": "faq", "text": ""}),
    ("covered_by", {"where": "faq", "text": "x", "extra": 1}),
    ("heading", 5),
])
def test_a_bad_builder_fill_is_bad_input(tmp_path, where, value):
    root = make_root(tmp_path); seed(root)
    assert run(root, *BUILD).returncode == 0
    f = root / "data/queries/m.json"
    data = json.loads(f.read_text())
    if where == "heading":
        data["extra_sections"][0]["heading"] = value
    else:
        data["questions"][0]["covered_by"] = value
    f.write_text(json.dumps(data))
    before = f.read_text()
    r = run(root, *BUILD)
    assert r.returncode == Q.EXIT_BAD_INPUT
    lines = r.stderr.strip().splitlines()
    assert len(lines) == 1 and "bad input" in lines[0] and "m.json" in lines[0]
    assert f.read_text() == before


# --- Task 7a: real competitor headings from saved pages, and the nine-section floor ----

GUMTREE_LIKE = """<html><body><header><h2>Site search</h2></header><main><ul>
<li><article class="standard-card"><a href="/p/1"><div><h2 data-q="tile-title">Staffy £450</h2>
</div></a></article></li>
<li><article class="standard-card"><a href="/p/2"><h2>Pablo</h2></a></article></li></ul>
<section><h2 data-q="nearby-results-title">Results from outside your search</h2></section>
</main></body></html>"""

STAFFIE_OWNERS_LIKE = """<main><header class="grid-head"><h2>21 Staffie Puppies For Sale In
  Manchester</h2></header>
<ul class="adverts"><li><article><h2><a href="/classified/1">Kc red chunky staffy males</a></h2>
</article></li><li><article><h2><a href="/classified/2">Staffy x</a></h2></article></li></ul>
<section class="content"><h2>Buyer&#39;s   Advice</h2><p>...</p></section></main>"""

FURNITURE_LIKE = """<body><nav><h2>Menu</h2></nav><aside><h2>Recommended</h2></aside>
<form><h2>Search puppies</h2></form><button><h2>Load more</h2></button>
<footer><h2>Useful links</h2></footer><template><h2>Hidden card</h2></template>
<main><section><h2>Health Testing</h2></section>
<section><h2>Why <a href="/blue">Blue Staffies</a> Are Rare</h2></section>
<section><h2><a href="/card">Only A Link</a></h2></section>
<section><h2> <a href="/x">Two</a> <a href="/y">Links</a> </h2></section>
<section><h2>   </h2><h2>Tail<script>var h = "<h2>x</h2>";</script><style>h2{}</style> End</h2>
</section></main></body>"""


def test_extract_h2s_drops_advert_cards_inside_links_and_articles():
    assert Q.extract_h2s(GUMTREE_LIKE) == ["Results from outside your search"]


def test_extract_h2s_drops_advert_cards_and_keeps_the_grid_header_for_clean_h2s():
    got = Q.extract_h2s(STAFFIE_OWNERS_LIKE)
    assert got == ["21 Staffie Puppies For Sale In Manchester", "Buyer's Advice"]
    assert Q.clean_h2s(got) == ["Buyer's Advice"]


def test_extract_h2s_keeps_content_and_drops_navigation_and_link_only_headings():
    assert Q.extract_h2s(FURNITURE_LIKE) == ["Health Testing", "Why Blue Staffies Are Rare",
                                             "Tail End"]


def test_extract_h2s_survives_unclosed_and_stray_tags():
    html = "<main><p>para<h2>Kept <br> Here</h2></a></li><ul><li>item<h2>Also kept</h2></main>"
    assert Q.extract_h2s(html) == ["Kept Here", "Also kept"]


def test_cli_extract_h2_prints_the_json_list(tmp_path):
    f = tmp_path / "page.html"
    f.write_text(STAFFIE_OWNERS_LIKE, encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPT), "--extract-h2", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout) == {"h2": ["21 Staffie Puppies For Sale In Manchester",
                                           "Buyer's Advice"], "h2_all": 4, "blocked": False}
    assert r.stderr == ""


def test_cli_extract_h2_missing_file_is_bad_input(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), "--extract-h2", str(tmp_path / "nope.html")],
                       capture_output=True, text=True)
    assert r.returncode == Q.EXIT_BAD_INPUT
    lines = r.stderr.strip().splitlines()
    assert len(lines) == 1 and "bad input" in lines[0] and "nope.html" in lines[0]
    assert r.stdout == ""


def test_cli_extract_h2_is_its_own_mode(tmp_path):
    f = tmp_path / "page.html"
    f.write_text("<h2>x</h2>")
    r = run(make_root(tmp_path / "repo"), "m", "--extract-h2", str(f))
    assert r.returncode == 2


MARKETPLACE_FURNITURE = ["Refine your results", "You might also like near Manchester",
                         "Latest featured ads in Staffordshire Bull Terrier", "Other pets",
                         "Results from outside your search", "Recommended for you",
                         "Nearest towns and cities",
                         "Fetch the latest puppy news by joining our pack", "30 Puppies found",
                         "21 Staffie Puppies For Sale In Manchester"]


def test_clean_h2s_strips_marketplace_furniture_and_keeps_content():
    kept = ["Buyer's Advice", "Blue Staffy Puppies in Manchester UK", "Health Testing"]
    assert Q.clean_h2s(MARKETPLACE_FURNITURE + kept) == kept


@pytest.mark.parametrize("counts,total", [([4], 9), ([6], 9), ([7], 10), ([10], 13), ([], 9)])
def test_section_target_never_falls_below_the_floor(counts, total):
    target, _ = Q.section_target([page(f"u{i}", n, g=i + 1) for i, n in enumerate(counts)])
    assert Q.SECTION_FLOOR == 9 and target["floor"] == 9 and target["total"] == total


def test_the_schema_requires_the_floor(tmp_path):
    root = make_root(tmp_path); seed(root)
    data, _ = Q.build("m", "location", "k", ROUTE, root, "2026-09-23")
    del data["section_target"]["floor"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(data, SCHEMA)


# --- quality review: page wrappers, line breaks, anchored furniture, blocked pages -------

def test_extract_h2s_keeps_a_wordpress_single_article_page():
    html = ("<main><article class='page'><h2>Our Puppies</h2><p>a</p><h2>Health Testing</h2>"
            "<h2>Delivery</h2></article></main>")
    assert Q.extract_h2s(html) == ["Our Puppies", "Health Testing", "Delivery"]


def test_extract_h2s_keeps_squarespace_sections_inside_one_article():
    html = ("<main><article class='sections'><section><h2>About Us</h2></section>"
            "<section><h2>Our Parents</h2></section></article></main>")
    assert Q.extract_h2s(html) == ["About Us", "Our Parents"]


def test_extract_h2s_keeps_a_header_inside_a_section_and_drops_the_site_header():
    html = ("<header class='site'><h2>Menu</h2></header><main>"
            "<section><header><h2>Our Puppies</h2></header></section></main>")
    assert Q.extract_h2s(html) == ["Our Puppies"]


def test_extract_h2s_keeps_accordion_list_items():
    html = ("<main><ul class='accordion'><li><h2>Feeding</h2><p>x</p></li>"
            "<li><h2>Exercise</h2></li></ul></main>")
    assert Q.extract_h2s(html) == ["Feeding", "Exercise"]


def test_extract_h2s_with_one_article_still_drops_a_link_card():
    html = "<main><article><a href='/x'><h2>Staffy £450</h2></a></article><h2>Kept</h2></main>"
    assert Q.extract_h2s(html) == ["Kept"]


def test_extract_h2s_separates_words_at_line_breaks_and_blocks():
    html = ("<main><h2>Blue<br>Staffy Puppies</h2><h2><span>Welcome</span><div>to Us</div></h2>"
            "<h2>Blue<b>Staffy</b></h2></main>")
    assert Q.extract_h2s(html) == ["Blue Staffy Puppies", "Welcome to Us", "BlueStaffy"]


@pytest.mark.parametrize("heading", [
    "Over 20 years breeding - puppies for sale in Manchester",
    "Why our 3 generations of staffies for sale in Cheshire are different",
    "2024 Litter: blue staffy puppies for sale in Salford",
    "Nearest towns to our kennel",
    "Puppies found in rescue centres",
    "What we recommended for you last year",
])
def test_clean_h2s_anchored_furniture_keeps_content(heading):
    assert Q.clean_h2s([heading]) == [heading]


CLOUDFLARE_LIKE = ("<!DOCTYPE html><html><head><title>Just a moment...</title></head><body>"
                   "<div class='main-content'><h1>www.example.com</h1><noscript>Enable "
                   "JavaScript and cookies to continue</noscript></div></body></html>")


@pytest.mark.parametrize("html,blocked", [
    (CLOUDFLARE_LIKE, True),
    ("<html><title>Attention Required! | Cloudflare</title><main><h1>x</h1></main></html>", True),
    ("<div id='cf-browser-verification'><h1>x</h1></div>", True),
    ("<html><body><p>tiny page, no main, no heading</p></body></html>", True),
    ("<html><body><main><h2>Real</h2></main></body></html>", False),
    ("<html><body><h1>Small but real</h1></body></html>", False),
    ("<html><body>" + "<p>long page</p>" * 1000 + "</body></html>", False),
], ids=["cloudflare", "attention", "cf-verify", "tiny", "main", "h1", "long"])
def test_page_report_flags_challenge_pages(html, blocked):
    assert Q.page_report(html)["blocked"] is blocked


def test_page_report_counts_every_h2_before_filtering():
    rep = Q.page_report(STAFFIE_OWNERS_LIKE)
    assert rep == {"h2": ["21 Staffie Puppies For Sale In Manchester", "Buyer's Advice"],
                   "h2_all": 4, "blocked": False}


def test_cli_extract_h2_warns_on_a_blocked_page_and_exits_0(tmp_path):
    f = tmp_path / "cf.html"
    f.write_text(CLOUDFLARE_LIKE)
    r = subprocess.run([sys.executable, str(SCRIPT), "--extract-h2", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert json.loads(r.stdout) == {"h2": [], "h2_all": 0, "blocked": True}
    lines = r.stderr.strip().splitlines()
    assert len(lines) == 1 and "blocked" in lines[0] and "cf.html" in lines[0]


def test_cli_extract_h2_decodes_by_the_meta_charset(tmp_path):
    f = tmp_path / "w.html"
    html = ('<html><head><meta charset="windows-1252"></head><body><main>'
            '<h2>Prices from \u00a3450</h2>' + "<p>x</p>" * 1000 + "</main></body></html>")
    f.write_bytes(html.encode("cp1252"))
    r = subprocess.run([sys.executable, str(SCRIPT), "--extract-h2", str(f)],
                       capture_output=True, text=True)
    assert json.loads(r.stdout)["h2"] == ["Prices from \u00a3450"]


def test_decode_html_falls_back_to_utf8_with_replacement():
    assert Q.decode_html('<meta charset="no-such-codec"><h2>\u00a3</h2>'.encode()) \
        == '<meta charset="no-such-codec"><h2>\u00a3</h2>'
    assert Q.decode_html(b"<h2>\xff</h2>") == "<h2>\ufffd</h2>"


def test_a_blocked_page_never_sets_or_blocks_the_number():
    blocked = dict(page("cf", 20, g=1), h2_all=40, blocked=True)
    target, rows = Q.section_target([blocked, page("b", 10, g=2), page("c", 7, g=3)])
    assert target["set_by"] == "b" and target["matched"] == 10
    assert rows[0]["blocked"] is True and rows[0]["h2_raw"] == 40
    assert not rows[0]["outlier"] and rows[1]["blocked"] is False


def test_h2_raw_is_h2_all_when_present():
    _, rows = Q.section_target([dict(page("a", 3), h2_all=12), page("b", 3)])
    assert [r["h2_raw"] for r in rows] == [12, 3]


def test_build_accepts_blocked_and_h2_all_and_stays_schema_valid(tmp_path):
    root = make_root(tmp_path); seed(root)
    f = root / "data/queries/raw/m/competitors.json"
    d = json.loads(f.read_text())
    d["pages"].append({"url": "https://cf.example", "google_pos": 2, "bing_pos": None,
                       "h2": [], "h2_all": 0, "blocked": True})
    f.write_text(json.dumps(d))
    data, _ = Q.build("m", "location", "k", ROUTE, root, "2026-09-23")
    jsonschema.validate(data, SCHEMA)
    assert [c["blocked"] for c in data["competitors"]] == [False, True]


@pytest.mark.parametrize("extra", [{"h2_all": "3"}, {"h2_all": -1}, {"h2_all": True},
                                   {"blocked": "yes"}, {"blocked": 1}])
def test_bad_h2_all_or_blocked_is_bad_input(tmp_path, extra):
    root = make_root(tmp_path); seed(root)
    f = root / "data/queries/raw/m/competitors.json"
    d = json.loads(f.read_text())
    d["pages"][0].update(extra)
    f.write_text(json.dumps(d))
    r = run(root, *BUILD)
    assert r.returncode == Q.EXIT_BAD_INPUT
    assert "competitors.json" in r.stderr and next(iter(extra)) in r.stderr


# --- re-review: blocked by title or Cloudflare markers; card grids counted by headings ---

REAL_BODY = "<main><h1>Blue Staffies</h1>" + "<p>copy</p>" * 1000 + "</main>"


@pytest.mark.parametrize("html,blocked", [
    ("<html><head><title>Our dogs</title></head><body><main><h1>Hi</h1><p>Just a moment of "
     "your time to meet our dogs.</p><h2>Our Dogs</h2></main></body></html>", False),
    ("<html><body><noscript>Please enable JavaScript and cookies</noscript><main>"
     "<h2>Health</h2><h2>Delivery</h2></main></body></html>", False),
    ("<html><head><title>Kennel</title><script>var s = 'Just a moment...';</script></head>"
     "<body>" + REAL_BODY + "</body></html>", False),
    ("<html><body><div><h2>One</h2><h2>Two</h2><h2>Three</h2></div></body></html>", False),
    ("<html><head><title>  ACCESS DENIED</title></head><body>" + REAL_BODY + "</body></html>",
     True),
    ("<html><body>" + REAL_BODY + "<script>window._cf_chl_opt={}</script></body></html>", True),
    ("<html><body>" + REAL_BODY + "<script src='/cdn-cgi/challenge-platform/x.js'></script>"
     "</body></html>", True),
    ("<html><body><p>Enable JavaScript and cookies to continue</p>" + REAL_BODY
     + "</body></html>", True),
], ids=["body-moment", "noscript-with-h2s", "script-moment", "small-with-h2s", "access-denied",
        "cf-chl-opt", "cdn-cgi", "enable-js-no-h2"])
def test_blocked_by_title_or_cloudflare_markers(html, blocked):
    assert Q.page_report(html)["blocked"] is blocked


def test_the_cloudflare_fixture_is_blocked_by_its_title():
    assert Q.page_report(CLOUDFLARE_LIKE)["blocked"] is True


def test_one_h2_article_among_h3_related_posts_is_a_page_wrapper():
    html = ("<main><article class='page'><h2>Our Puppies</h2><h2>Health Testing</h2>"
            "<h2>Delivery</h2></article>"
            "<aside class='related'><article><h3>Post one</h3></article>"
            "<article><h3>Post two</h3></article></aside></main>")
    assert Q.extract_h2s(html) == ["Our Puppies", "Health Testing", "Delivery"]


def test_related_articles_outside_aside_with_h3s_still_keep_the_page_article():
    html = ("<main><article><h2>A</h2><h2>B</h2><h2>C</h2></article>"
            "<article><h3>Post one</h3></article><article><h3>Post two</h3></article></main>")
    assert Q.extract_h2s(html) == ["A", "B", "C"]


def test_a_list_grid_of_three_h2_cards_is_dropped():
    html = ("<main><ul class='grid'>" + "".join(
        f"<li><div class='card'><h2>Advert {i}</h2></div></li>" for i in range(3))
        + "</ul><section><h2>Buying Advice</h2></section></main>")
    assert Q.extract_h2s(html) == ["Buying Advice"]


def test_an_accordion_of_two_h2_items_is_kept():
    html = ("<main><ul class='accordion'><li><h2>Feeding</h2></li><li><h2>Exercise</h2></li>"
            "<li><p>no heading</p></li></ul></main>")
    assert Q.extract_h2s(html) == ["Feeding", "Exercise"]


# --- Task 7b: buyer wording wins, near-duplicates collapse, two per topic per block -----

def test_merge_folds_a_bank_citing_buyer_question_into_that_bank_row(tmp_path):
    root = make_root(tmp_path)        # bank row b0 is "How much does a puppy cost?"
    m = Q.merge([("How much does a blue Staffy puppy cost?", "serp_google", "serp_google_paa",
                  "bank:b0"),
                 ("How much does a puppy cost?", "bank", "bank:b0", "data/settings.json")], root)
    (only,) = m.values()
    assert only["question"] == "How much does a blue Staffy puppy cost?"
    assert only["types"] == {"serp_google", "bank"}
    assert only["found_in"] == ["serp_google_paa", "bank:b0"]
    assert only["fact_source"] == "data/settings.json"


def test_merge_buyer_wording_wins_even_when_the_bank_row_comes_first(tmp_path):
    root = make_root(tmp_path)
    m = Q.merge([("How much does a puppy cost?", "bank", "bank:b0", "data/settings.json"),
                 ("What do blue Staffy pups cost?", "ai_engines", "ai:chatgpt", "bank:b0"),
                 ("Blue staffy price Manchester?", "serp_bing", "serp_bing_paa", "bank:b0")],
                root)
    (only,) = m.values()
    assert only["question"] == "What do blue Staffy pups cost?"
    assert only["types"] == {"bank", "ai_engines", "serp_bing"}


def test_merge_an_unresolved_bank_citation_stays_its_own_entry(tmp_path):
    root = make_root(tmp_path)
    m = Q.merge([("How much does a blue Staffy puppy cost?", "serp_google", "serp_google_paa",
                  "bank:nope"),
                 ("How much does a puppy cost?", "bank", "bank:b0", "data/settings.json")], root)
    assert len(m) == 2


def entry(text, types=("bank",), found=None, fact="data/settings.json"):
    return {"question": text, "types": set(types), "found_in": list(found or [f"bank:{text}"]),
            "fact_source": fact}


def collapse(texts, **kw):
    merged = {Q.normalise(t): entry(t, **kw) for t in texts}
    return Q.collapse_near_duplicates(merged)


HEALTH_VARIANTS = ["Are the parents of your blue Staffy puppies health-tested?",
                   "Are your puppies\u2019 parents health-tested?",
                   "Are your Staffordshire Bull Terrier puppies health-tested?",
                   "Are your puppies health tested for genetic diseases?",
                   "Can I see the health test results for both parents?"]
FIRST_TIME = ["Are Staffordshire Bull Terriers good for first-time owners?",
              "Are blue Staffies suitable for first-time dog owners?",
              "Are Staffordshire Bull Terriers good for first-time dog owners?"]


def test_content_words_drop_stop_words_and_stem():
    assert Q.content_words("Do you deliver across the UK?") == {"deliver", "across"}
    assert Q.content_words("How do you ensure the safe delivery of Staffies across the UK?") \
        == {"ensure", "safe", "deliver", "across"}
    assert Q.content_words("Are the parents health tested?") == {"parents", "health", "test"}
    assert Q.content_words("Good for first-time owners, trained?") \
        == {"good", "first", "time", "owner", "train"}


def test_the_five_health_test_variants_collapse_to_one():
    out = collapse(HEALTH_VARIANTS + ["Do you offer health guarantees for your puppies?"])
    assert len(out) == 2
    kept = [m for m in out.values() if "guarantee" not in m["question"]]
    assert len(kept) == 1 and len(kept[0]["found_in"]) == 5


def test_the_three_first_time_owner_variants_collapse_to_one():
    out = collapse(FIRST_TIME + ["What should a first-time dog owner know before getting a blue "
                                 "Staffy?"])
    assert len(out) == 2


def test_uk_delivery_and_safe_delivery_collapse_by_the_rule():
    # {deliver, across} vs {ensure, safe, deliver, across}: Jaccard 2/4 = 0.5 -> duplicates
    out = collapse(["Do you deliver across the UK?",
                    "How do you ensure the safe delivery of Staffies across the UK?",
                    "Can you deliver a Blue Staffy puppy to my location in the UK?"])
    assert sorted(m["question"] for m in out.values()) == [
        "Can you deliver a Blue Staffy puppy to my location in the UK?",
        "Do you deliver across the UK?"]


def test_collapse_is_led_by_a_fact_backed_question_and_unions_sources():
    # Ruling: a lead's visible question must be answerable by its own fact.
    merged = {"a": entry("Are the parents health tested?", types=("bank",), found=["bank:x"]),
              "b": entry("Are both parents health tested?", types=("serp_google", "bank"),
                         found=["serp_google_paa", "bank:y"], fact=None)}
    (only,) = Q.collapse_near_duplicates(merged).values()
    assert only["question"] == "Are the parents health tested?"
    assert only["types"] == {"serp_google", "bank"}
    assert only["found_in"] == ["bank:x", "serp_google_paa", "bank:y"]
    assert only["fact_source"] == "data/settings.json"


def test_an_unbacked_phrasing_that_sorts_first_does_not_lead():
    merged = {"a": entry("Any chance to see the parents\u2019 health-test certificates?",
                         types=("ai_engines",), found=["ai_chatgpt"], fact=None),
              "b": entry("Can I see the parents\u2019 health test certificates?",
                         found=["bank:certs"], fact="src/pages/index.astro")}
    (only,) = Q.collapse_near_duplicates(merged).values()
    assert only["question"] == "Can I see the parents\u2019 health test certificates?"
    assert only["fact_source"] == "src/pages/index.astro"


def test_an_unbacked_entry_with_two_buyer_sources_does_not_lead_a_backed_bank_row():
    merged = {"a": entry("Are both parents health tested?", types=("serp_google", "ai_engines"),
                         found=["serp_google_paa", "ai_chatgpt"], fact=None),
              "b": entry("Are the parents health tested?", found=["bank:x"])}
    (only,) = Q.collapse_near_duplicates(merged).values()
    assert only["question"] == "Are the parents health tested?"
    assert only["fact_source"] == "data/settings.json"
    assert only["types"] == {"bank", "serp_google", "ai_engines"}


def test_a_group_with_no_fact_keeps_the_best_evidenced_phrasing_and_stays_unbacked():
    merged = {"a": entry("Are the parents health tested?", types=("threads",),
                         found=["thread:1"], fact=None),
              "b": entry("Are both parents health tested?", types=("serp_google", "ai_engines"),
                         found=["serp_google_paa", "ai_chatgpt"], fact=None)}
    (only,) = Q.collapse_near_duplicates(merged).values()
    assert only["question"] == "Are both parents health tested?"
    assert only["fact_source"] is None


def test_collapse_never_joins_different_topics():
    out = collapse(["Do Staffies shed their coat?", "Do Staffies need a garden?"])
    assert len(out) == 2
    out = collapse(["How much does delivery cost?", "Do you deliver across the UK?"])
    assert len(out) == 2        # price vs delivery


def test_collapse_is_deterministic_whatever_the_input_order():
    a = collapse(HEALTH_VARIANTS)
    b = collapse(list(reversed(HEALTH_VARIANTS)))
    assert [m["question"] for m in a.values()] == [m["question"] for m in b.values()]


def capped_pool():
    top = [q(f"t-d{i}", f"Do you deliver to town {i}?", 20 - i) for i in range(6)] + \
          [q("t-p0", "How much does a puppy cost?", 1)]
    mid = [q(f"m-{i}", t, 5) for i, t in enumerate(MIDDLE)]
    bot = [q(f"b-{i}", t, 5) for i, t in enumerate(BOTTOM)]
    return top + mid + bot


def test_pick_faq_takes_two_per_topic_then_lifts_the_cap_for_a_short_block():
    qs = capped_pool()
    Q.pick_faq(qs)
    top = sorted((x for x in qs if x["faq"] == "top"), key=Q._rank)
    ids = [x["id"] for x in top]
    assert ids[:2] == ["t-d0", "t-d1"] and "t-p0" in ids
    assert len(top) >= 5
    assert set(ids) >= {"t-d0", "t-d1", "t-d2", "t-d3", "t-p0"}   # cap lifted, rest by score


def test_pick_faq_caps_each_topic_at_two_when_the_block_can_fill():
    qs = bank_questions()
    Q.pick_faq(qs)
    from collections import Counter
    for b in Q.BLOCKS:
        per = Counter(x["topic"] for x in qs if x["faq"] == b)
        assert max(per.values()) <= Q.FAQ_TOPIC_CAP == 2


def test_pick_faq_short_only_for_too_few_fact_backed_questions():
    qs = capped_pool()
    for x in qs:
        if x["block"] == "top" and x["id"] != "t-p0":
            x["fact_source"] = None
    with pytest.raises(Q.Short) as e:
        Q.pick_faq(qs)
    assert e.value.blocks == {"top": (1, 5)}


def test_build_puts_buyer_wording_in_the_faq(tmp_path):
    root = make_root(tmp_path); seed(root)
    add_raw_question(root, "serp_google", "How much does a blue Staffy puppy cost in Manchester?")
    f = root / "data/queries/raw/m/serp_google.json"
    d = json.loads(f.read_text())
    d["questions"][-1]["fact_source"] = "bank:b0"
    f.write_text(json.dumps(d))
    data, _ = Q.build("m", "location", "k", ROUTE, root, "2026-09-23")
    by_q = {x["question"]: x for x in data["questions"]}
    buyer = by_q["How much does a blue Staffy puppy cost in Manchester?"]
    assert "How much does a puppy cost?" not in by_q
    assert buyer["faq"] == "top" and buyer["score"] == 2 + 1 + 2
    assert buyer["found_in"] == ["serp_google_paa", "bank:b0"]


# --- extractor: page wrapper vs card, unclosed list items, the challenge script ----------

def test_the_challenge_platform_script_alone_does_not_block_a_real_page():
    html = ("<html><head><title>Kennel</title><script src='/cdn-cgi/challenge-platform/h/b/"
            "scripts/jsd/main.js'></script></head><body><main><h2>Our Puppies</h2>"
            "<h2>Health Testing</h2></main></body></html>")
    assert Q.page_report(html)["blocked"] is False


def test_a_squarespace_wrapper_keeps_its_h2s_and_its_summary_cards_drop():
    html = ("<main><article class='sections'><section><h2>About Us</h2></section>"
            "<section><h2>Our Parents</h2></section><section><h2>Delivery</h2>"
            "<div class='summary-block'><article class='summary-item'><h2>Blog card one</h2>"
            "</article><article class='summary-item'><h2>Blog card two</h2></article></div>"
            "</section></article></main>")
    assert Q.extract_h2s(html) == ["About Us", "Our Parents", "Delivery"]


def test_unclosed_list_items_close_at_the_next_item():
    html = "<main><ul><li><h2>Pablo</h2><li><h2>Rex</h2><li><h2>Staffy £500</h2></ul></main>"
    assert Q.extract_h2s(html) == []


def test_a_nested_list_inside_an_unclosed_item_is_its_own_list():
    html = ("<main><ul><li><h2>Feeding</h2><ul><li>a<li>b</ul><li><h2>Exercise</h2></ul>"
            "</main>")
    assert Q.extract_h2s(html) == ["Feeding", "Exercise"]
