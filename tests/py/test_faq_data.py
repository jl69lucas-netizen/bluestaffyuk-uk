"""data/faq.json is the FAQ's one source, and every row has to be able to name what backs it.

An FAQ is the easiest surface on the site to answer a question with something plausible
that nobody has checked, which rule 9 forbids. So each row carries a `source`, and this
file makes that claim falsifiable: the file has to exist, and when the source is a page,
the facts the answer leans on have to be words that page actually says.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
FAQ = json.loads((ROOT / "data/faq.json").read_text())
SETTINGS = json.loads((ROOT / "data/settings.json").read_text())

# Every substitution src/lib/faq.ts knows. Kept here deliberately rather than imported:
# this is the second opinion, and a token added to the loader and forgotten in the data
# (or the reverse) should show up as a disagreement between two lists, not vanish.
TOKENS = {
    "deposit_gbp": str(SETTINGS["deposit_gbp"]),
    "delivery_min_gbp": str(SETTINGS["delivery_min_gbp"]),
    "delivery_max_gbp": str(SETTINGS["delivery_max_gbp"]),
    "delivery_note": SETTINGS["delivery_note"],
    "deposit_terms": "refundable" if SETTINGS["deposit_refundable"] else "non-refundable",
}

# The phrases an answer asserts that are NOT a settings value — the part a reader would
# treat as a promise. Each must appear on the page that row names.
FACT_PHRASES = {
    "puppy-package": ["first vaccinations", "microchip", "puppy pack"],
}


def _page_text(path):
    """The visible-ish text of a migrated page: the escaped `body` string, unescaped."""
    src = (ROOT / path).read_text()
    m = re.search(r'const body = "(.*?)";\n', src, re.S)
    assert m, f"{path} has no migrated body string"
    return m.group(1).encode().decode("unicode_escape").encode("latin-1").decode("utf-8")


def test_rows_have_unique_ids_and_the_four_fields():
    assert FAQ, "data/faq.json is empty"
    ids = [r["id"] for r in FAQ]
    assert len(ids) == len(set(ids)), ids
    for r in FAQ:
        assert set(r) == {"id", "q", "a", "source"}, r
        assert r["q"].endswith("?"), r["id"]
        assert r["a"].strip(), r["id"]


def test_every_placeholder_in_an_answer_is_one_the_loader_resolves():
    """An unknown `{token}` survives interpolation and ships in the answer as literal
    braces. That is the loudest failure mode available at runtime and still a bad one to
    find on the page, so it fails here first."""
    for r in FAQ:
        for token in re.findall(r"\{([a-z_]+)\}", r["a"]):
            assert token in TOKENS, (r["id"], token)


def test_every_source_exists_and_a_settings_source_is_actually_used():
    for r in FAQ:
        assert (ROOT / r["source"]).exists(), (r["id"], r["source"])
        if r["source"] == "data/settings.json":
            assert re.search(r"\{[a-z_]+\}", r["a"]), (
                f"{r['id']} names settings as its source but interpolates nothing from it")


def test_page_backed_answers_say_what_their_page_says():
    """The rule-9 assertion. A row sourced to a page must lean only on words that page
    uses; a phrase that has quietly left the page takes its answer with it."""
    checked = 0
    for r in FAQ:
        if r["source"] == "data/settings.json":
            continue
        assert r["source"].startswith("src/pages/"), (r["id"], r["source"])
        text = _page_text(r["source"]).lower()
        phrases = FACT_PHRASES.get(r["id"])
        assert phrases, f"{r['id']} is page-sourced but names no fact phrases to verify"
        for phrase in phrases:
            assert phrase.lower() in text, (r["id"], r["source"], phrase)
        checked += 1
    assert checked, "no page-backed row was verified — this test examined nothing"
