"""The breeder's answer (answer board q01, 2026-09-29): she holds no DNA certificates for Maggie
and Jones, so a page may NAME the tests (L-2-HGA, HC-HSF4, eye and elbow screening) and never
state a RESULT. "Tested clear", "certified clear", "clear for", "clear DNA results", "results on
request", "a clear pair", "will not be genetically affected" and every other stated result are
gone from the built site (Known Issue 98). The evidence ledger's `parents-dna-clear` row stays at
proof NOT FETCHED, and now records why: the breeder confirms none is held.

This holds every built file in dist/ (HTML text, meta and alt attributes, JSON-LD, llms.txt,
sitemaps) and the FAQ data to it. Board previews render the approved board records, which stay
as history. One migrated page is named below with its reason; it is not a pattern exemption.
"""
import html
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]

TEST = r"(?:L-?2-?HGA|L2HGA|HC-?HSF4|\bHC\b|PHPV)"
RESULT = [
    # "DNA tested clear", "certified clear", "recorded clear", "screened and certified clear"
    r"\b(?:tested|certified|recorded|screened|cleared|proven|confirmed)\s+(?:and\s+certified\s+)?clear\b",
    # "clear of L-2-HGA", "clear for key hereditary conditions", "clear of both", "are clear of"
    r"\bclear\s+(?:of|for)\s+(?:" + TEST + r"|key|both|the\s+(?:same|two)|common|hereditary|inherited|these|two|each|either)",
    r"\bare\s+clear\s+of\b",
    r"\bgenetically\s+affected\b",
    # "clear DNA results", "a clear result", "clear test results"
    r"\bclear\s+(?:DNA\s+)?(?:test\s+)?results?\b",
    r"\bclearances?\b",
    r"\bcleared\s+for\b",
    # "two clear parents", "a clear pair", "clear dam"
    r"\bclear\s+(?:parents?|pair|dam|sire)\b",
    # "L-2-HGA clear", "HC-HSF4 Clear", "(…Aciduria): CLEAR"
    TEST + r"\)?\s*:?\s*clear\b",
    TEST + r"[^.:]{0,60}:\s*clear\b",
    r"\bnon-?carriers?\b",
    # a result or certificate on offer implies one is held
    r"\bresults?\s+on\s+request\b",
    r"\b(?:we|we'll|we\s+will)\s+(?:send|show|hand\s+over|share)\b[^.]{0,40}\bcertificates?\b",
    r"\bthe\s+results\s+we\s+hand\s+over\b",
    r"\b(?:send|show)\s+(?:you\s+)?(?:the|our|both|its)\s+(?:two\s+)?certificates?\b",
    # "records both parents clear of", "Maggie and Jones are clear", a counter tile "Clear both parents"
    r"\b(?:parents?|both|dam|sire|Maggie|Jones)\s+(?:are\s+|is\s+)?clear\b",
    r"\bclear\s+both\s+parents\b",
    # our own results or certificates offered, which the breeder does not hold
    r"[‘'\"]clear[’'\"]\s+results?",
    r"\b(?:two|both(?:\s+parents['’]?)?)\s+DNA\s+(?:screening\s+)?results\b",
    r"\bboth\s+DNA\s+certificates\b",
    r"\bthe\s+certificates\s+are\s+yours\b",
    r"\bask\s+us\s+(?:for|to\s+see)\s+the\s+certificates\b",
    r"\b(?:with\s+their|their\s+health)\s+results\b",
    r"\bwhat\s+the\s+results\s+were\b",
    # a hip or elbow score stated as a figure
    r"\b(?:hip|elbow)\s+(?:score|grade)s?\s+(?:of|is|are|was)\s+\d",
]
RESULT_RE = re.compile("(?i)" + "|".join(RESULT))

# One migrated page, by name. /uk-locations/staffy-breeding-dogs-glasgow/ is the old WordPress
# body, rendered verbatim from data/locations.json (a generated file, never hand-edited), and its
# only route to a fix without dating 26 unchanged location pages is its project 5 rebuild.
# Known Issue 98 carries it as open. Nothing else is excused.
MIGRATED_OPEN = {"uk-locations/staffy-breeding-dogs-glasgow/index.html"}

# General advice to a buyer about ANY breeder, which names no dog of ours and states no result of
# ours: what a good answer sounds like, and what an unbacked claim is worth. Exact sentences, by
# page, so a new sentence is never excused by a pattern.
GENERAL_ADVICE = {
    "uk-blue-staffy-puppy-buying-guide/index.html": [
        "Told the parents are clear but shown no certificate, you have been told nothing you can check.",
        "Both parents clear, or carrier to clear",
    ],
    "uk-staffordshire-bull-terrier-guide/index.html": [
        "A breeder who says the parents are clear and cannot produce the paper has told you nothing at all.",
    ],
}

ATTR = re.compile(r'\b(?:content|alt|aria-label|title)="([^"]*)"')


def visible(raw):
    """Text of a built file as a reader or a crawler meets it: tags gone, attributes that carry
    words kept (meta descriptions, alts), entities decoded, whitespace folded. Style sheets are
    dropped; JSON-LD is kept (it is text inside a script tag)."""
    raw = re.sub(r"<style[^>]*>.*?</style>", " ", raw, flags=re.S)
    attrs = " | ".join(ATTR.findall(raw))
    text = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(text + " | " + attrs))


def result_lines(text):
    return [text[max(0, m.start() - 70):m.end() + 40] for m in RESULT_RE.finditer(text)]


def built_files():
    dist = ROOT / "dist"
    if not dist.exists():
        pytest.skip("run npm run -s build first")
    return dist, [p for p in dist.rglob("*") if p.suffix in (".html", ".txt", ".xml", ".json")
                  and "board-preview" not in p.parts]


def test_no_built_page_states_a_dna_or_health_test_result():
    dist, files = built_files()
    assert len(files) > 50, "examined too few built files to be a pass"
    bad = []
    for p in files:
        rel = str(p.relative_to(dist))
        if rel in MIGRATED_OPEN:
            continue
        text = visible(p.read_text(errors="ignore"))
        for sentence in GENERAL_ADVICE.get(rel, []):
            assert sentence in text, f"{rel}: the excused sentence is gone, drop it: {sentence}"
            text = text.replace(sentence, " ")
        bad += [f"{rel}: …{l}…" for l in result_lines(text)]
    assert bad == [], "\n".join(bad)


def test_the_migrated_exception_still_needs_it():
    """The named page is excused only while it still states a result; once its rebuild lands,
    this fails and the name comes out of MIGRATED_OPEN."""
    dist, _ = built_files()
    for rel in MIGRATED_OPEN:
        f = dist / rel
        assert f.exists(), rel
        assert result_lines(visible(f.read_text(errors="ignore"))), f"{rel} is clean: drop it from MIGRATED_OPEN"


def test_no_faq_row_states_a_result():
    rows = json.loads((ROOT / "data/faq.json").read_text(encoding="utf-8"))
    bad = [(r["id"], l) for r in rows for l in result_lines(r["q"] + " " + r["a"])]
    assert bad == [], bad


def test_the_patterns_fire_on_the_old_lines_and_spare_the_test_names():
    for old in ["Both parents are DNA tested clear of L-2-HGA and HC-HSF4.",
                "are extensively DNA tested and certified clear for key hereditary conditions",
                "Maggie and Jones carry clear DNA results for L-2-HGA and HC-HSF4",
                "your KC registered Staffy puppies will not be genetically affected",
                "Dam and sire clear of L-2-HGA and HC-HSF4, results on request.",
                "Both are screened and certified clear of L-2-HGA",
                "Which genetic tests are the parents cleared for?",
                "including clearances for common Staffy conditions (HC, L2HGA)",
                "Responsible breeders of blue Staffies L-2-HGA clear.",
                "L-2-HGA (Hereditary L-2-Hydroxyglutaric Aciduria): CLEAR",
                "and a clear pair cannot hand either one down",
                "Both ours are recorded clear of both.",
                "we send the certificates on request",
                "The first the table above records both parents clear of.",
                "Ask us to send the two certificates before you travel.",
                "Clear both parents, L-2-HGA",
                "A ‘clear’ result means your puppy will not develop it.",
                "Each claim above names a document: a registration, two DNA results, a vaccination card",
                "Four documents stand behind that: both parents' DNA screening results",
                "Both live here and both are on the health page with their results beside their names.",
                "Ask us for the certificates whenever you would like to see them.",
                "Our health page sets out every test we run and what the results were"]:
        assert result_lines(old), old
    for named in ["Maggie and Jones are DNA tested for L-2-HGA and HC-HSF4, and both have their eyes and elbows screened.",
                  "Ask to see the certificate for each test before you pay a deposit.",
                  "it is not a test result and not a grade",
                  "We quote no score or grade.",
                  "A puppy needs two copies of the gene to be affected."]:
        assert result_lines(named) == [], named


def test_the_ledger_row_records_that_no_certificate_is_held():
    """The evidence ledger's schema (tests/py/test_rules_index.py) allows a proof that is a site
    path or the literal NOT FETCHED, and a NOT FETCHED row has no `confirmed` date. "No proof;
    the breeder confirms none is held" is therefore NOT FETCHED with `confirmed` null, and the
    row's `barrier` says why, so nobody goes looking for a certificate that does not exist."""
    ledger = json.loads((ROOT / "data/quality/evidence-ledger.json").read_text(encoding="utf-8"))
    row = next(c for c in ledger["claims"] if c["id"] == "parents-dna-clear")
    assert row["proof"] == "NOT FETCHED" and row["confirmed"] is None, row
    assert "answer board q01" in row["barrier"] and "no DNA certificates" in row["barrier"], row
