"""data/faq.json is the FAQ's one source, and every row has to be able to name what backs it.

An FAQ is the easiest surface on the site to answer a question with something plausible
that nobody has checked, which rule 9 forbids. So each row carries a `source`, and this
file makes that claim falsifiable: the file has to exist, and when the source is a page,
the facts the answer leans on have to be words that page actually says.
"""
import json
from html import unescape
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
    # The three enquiry rows are verified against the REBUILT thank-you page's prose, the
    # same way the privacy rows below are: the migrated body's wording ("personally review
    # and respond", "ready to find their forever home", "contact our purebred Blue Staffy
    # breeders") went with the migrated body, and a phrase list left pointing at it would
    # be asserting rule 9 against a page that no longer exists (project 4 Task 8).
    "enquiry-reply-time": ["read and answered personally", "24-48 business hours", "spam or junk folder"],
    "enquiry-while-you-wait": ["Staffy breed guide", "health and care", "here today"],
    "enquiry-follow-up": ["Writing again", "privacy policy"],
    # The three privacy rows are verified against the REBUILT page's prose (the accordion
    # that renders them is cut out first), so the phrases are the ones that page uses.
    "privacy-data-collected": ["email address, phone number and postal address", "IP address"],
    "privacy-cookies": ["Essential cookies", "Google Analytics"],
    "privacy-delete-data": ["Right to erasure", "within one month"],
    "contact-visit": ["walk-in facility", "by appointment only"],
    # Verified against the REBUILT contact page (project 4 Task 9), the same way the
    # enquiry and privacy rows are. "As much detail as possible" was the migrated body's
    # phrase; the rebuilt page says which detail instead, field by field, which is the
    # thing the answer actually leans on.
    "contact-what-to-say": ["your household", "24-48 business hours"],
}


REBUILT = set(json.loads((ROOT / "data/facts/rebuilt.json").read_text()))
_FAQ_BLOCK = re.compile(r'<div[^>]*class="[^"]*kit-faq[^"]*"[^>]*>.*?</div>', re.S)
_TAG = re.compile(r"<[^>]+>")
_SCRIPTY = re.compile(r"<(script|style)\b.*?</\1>", re.S)


def _slug_of(path):
    """`src/pages/<slug>/index.astro` -> `<slug>`; `src/pages/index.astro` -> `index`.
    Nested slugs keep their full path, the same key every other gate uses."""
    m = re.fullmatch(r"src/pages/(?:(.+)/)?index\.astro", path)
    assert m, path
    return m.group(1) or "index"


def _built_text(slug):
    """The visible text of a REBUILT page, with the FAQ accordion cut out.

    Cutting it is the whole point. The accordion renders these very answers, so a phrase
    checked against a page that includes it would be checking the answer against itself and
    would pass for any wording at all. What the rule-9 assertion actually asks is whether
    the PAGE'S OWN PROSE still says the thing the answer leans on, so the block the answers
    are rendered into comes out before the text is read."""
    html = (ROOT / "dist" / slug / "index.html").read_text(encoding="utf-8")
    html = _SCRIPTY.sub(" ", html)
    html = _FAQ_BLOCK.sub(" ", html)
    return re.sub(r"\s+", " ", unescape(_TAG.sub(" ", html)))


def _page_text(path):
    """The text a page-sourced answer is verified against.

    A MIGRATED page is read from its `const body` string — the source file is the page. A
    REBUILT page (listed in data/facts/rebuilt.json) is hand-written Astro with the prose in
    markup, so there is no body string to read and the source file is the wrong artefact
    anyway: what the reader is told is what the BUILD emits. So the built page is read
    instead, and the switch is keyed on the same list every other rebuilt-page gate uses."""
    slug = _slug_of(path)
    if slug in REBUILT:
        return _built_text(slug)
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
