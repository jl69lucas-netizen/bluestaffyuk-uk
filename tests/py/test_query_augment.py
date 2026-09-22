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
    ("How long do Staffies sleep at night?", "lifespan"),
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
