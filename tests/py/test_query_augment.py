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
