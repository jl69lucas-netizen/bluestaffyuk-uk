# tests/py/test_evidence_unledgered.py — evidence_audit.py `claim-unledgered` (parity build
# Task 20; audit row 1d.1): a health or credential claim on a page must match a row of
# data/quality/evidence-ledger.json in the same sentence, or be a claim placeholder. ERROR on
# a new location, comparison or blog page; WARN on every other page.
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_audit as E  # noqa: E402

REAL_LEDGER = json.loads((ROOT / "data/quality/evidence-ledger.json").read_text(encoding="utf-8"))
LEDGER = {"claims": [
    {"id": "parents-dna-clear", "pattern": r"(?:certified|tested)\s+clear", "proof": "NOT FETCHED",
     "anchor": "dna-tests", "confirmed": None, "covers": ["dna-clear", "dna-test"]}],
    "vocabulary": REAL_LEDGER["vocabulary"]}


def page(main):
    return f"<html><head><title>T</title></head><body><main>{main}</main></body></html>"


@pytest.mark.parametrize("sentence,vocab", [
    ("<p>Our DNA-tested parents live with us.</p>", "dna-test"),
    ("<p>Both parents are hip scored by the BVA.</p>", "hip-elbow-score"),
    ("<p>Every puppy is KC registered.</p>", "kc-registered"),
    ("<p>We are a licensed breeder.</p>", "licensed-breeder"),
    ("<p>Each pup leaves vet checked.</p>", "vet-checked"),
    ("<p>Our dogs are health tested.</p>", "health-tested"),
])
def test_an_unledgered_claim_is_found(sentence, vocab):
    got = E.unledgered_claims(page(sentence), LEDGER)
    assert [v for v, _ in got] == [vocab]


def test_a_sentence_the_ledger_covers_passes():
    html = page("<p>Both parents are DNA tested clear of L-2-HGA and HC-HSF4.</p>")
    assert E.unledgered_claims(html, LEDGER) == []


def test_the_ledger_must_match_in_the_same_sentence():
    html = page("<p>The parents were tested clear. Our DNA-tested parents live with us.</p>")
    assert [v for v, _ in E.unledgered_claims(html, LEDGER)] == ["dna-test"]


def test_a_heading_is_its_own_sentence():
    html = page("<h2>Our DNA-Tested Parents</h2><p>They were tested clear in spring.</p>")
    assert [v for v, _ in E.unledgered_claims(html, LEDGER)] == ["dna-test"]


def test_questions_and_placeholders_are_not_claims():
    html = page("<h3>Are the parents health tested?</h3>"
                "<p>We are a LICENCE_CLAIM_PLACEHOLDER licensed breeder.</p>")
    assert E.unledgered_claims(html, LEDGER) == []


def test_a_species_statement_is_not_a_credential():
    html = page("<p>The Staffordshire Bull Terrier is a KC-recognised breed.</p>")
    assert E.unledgered_claims(html, LEDGER) == []


def test_json_ld_is_not_prose():
    html = page('<script type="application/ld+json">{"d": "DNA tested parents"}</script><p>Hi.</p>')
    assert E.unledgered_claims(html, LEDGER) == []


def test_a_ledger_without_vocabulary_checks_nothing():
    assert E.unledgered_claims(page("<p>Our DNA-tested parents.</p>"), {"claims": []}) == []


def test_audit_errors_on_a_new_page_and_warns_elsewhere():
    html = page("<p>Our DNA-tested parents live with us.</p>")
    budgets = {"budgets": {}, "terms": {}}
    new = E.audit("blue-staffy-first-week-at-home", html, "blog", budgets, LEDGER, new_page=True)
    old = E.audit("blue-staffy-health-uk", html, "interior", budgets, LEDGER)
    assert [s for s, m in new if "un-ledgered" in m] == ["ERROR"]
    assert [s for s, m in old if "un-ledgered" in m] == ["WARN"]


def test_new_page_is_a_rebuilt_family_page_outside_the_frozen_twelve():
    rebuilt = {"blue-staffy-puppies-leeds", "blue-staffy-health-uk", "blue-staffy-blog-guides"}
    assert E.is_new_page("uk-locations/blue-staffy-puppies-leeds", "location", rebuilt)
    assert not E.is_new_page("uk-locations/blue-staffy-puppies-york", "location", rebuilt)
    assert not E.is_new_page("blue-staffy-health-uk", "interior", rebuilt)
    assert not E.is_new_page("blue-staffy-blog-guides", "blog", rebuilt)


def test_the_real_ledger_vocabulary_compiles_and_the_check_id_is_registered():
    import re
    for vid, pat in REAL_LEDGER["vocabulary"].items():
        re.compile(pat)
    assert {"id": "claim-unledgered"} in E.CHECK_IDS
    index = json.loads((ROOT / "data/quality/rule-index.json").read_text())
    row = next(r for r in index["rules"] if r["id"] == "claim-unledgered")
    assert row["test"] == "scripts/evidence_audit.py::claim-unledgered"


def test_the_cli_exits_1_on_a_new_page_with_an_unledgered_claim(tmp_path):
    q = tmp_path / "data/quality"
    q.mkdir(parents=True)
    (q / "evidence-budgets.json").write_text(json.dumps({"budgets": {}, "terms": {}}))
    (q / "evidence-ledger.json").write_text(json.dumps(LEDGER))
    dist = tmp_path / "dist" / "uk-locations" / "blue-staffy-puppies-leeds"
    dist.mkdir(parents=True)
    (dist / "index.html").write_text(page("<p>Our DNA-tested parents live with us.</p>"))
    rebuilt = tmp_path / "rebuilt.json"
    rebuilt.write_text(json.dumps(["blue-staffy-puppies-leeds"]))
    r = subprocess.run([sys.executable, str(ROOT / "scripts/evidence_audit.py"),
                        "uk-locations/blue-staffy-puppies-leeds", "--dist", str(tmp_path / "dist"),
                        "--budgets", str(q / "evidence-budgets.json"),
                        "--ledger", str(q / "evidence-ledger.json"), "--rebuilt", str(rebuilt)],
                       capture_output=True, text=True)
    assert r.returncode == 1, r.stdout
    assert "ERROR un-ledgered claim" in r.stdout


# ── Task 20 review: covers, every hit, finer sentences, wider recall, precision ──────────────
def ids(html, ledger=LEDGER):
    return [v for v, _ in E.unledgered_claims(html, ledger)]


def test_a_ledger_row_clears_only_the_vocabulary_it_covers_and_every_hit_is_reported():
    html = page("<p>Parents tested clear, KC registered and vet checked.</p>")
    assert ids(html) == ["kc-registered", "vet-checked"]


def test_an_unrelated_ledger_row_cannot_clear_a_claim():
    ledger = {"claims": [{"id": "vet-travel", "pattern": r"vet\s+cleared\s+for\s+travel",
                          "proof": "NOT FETCHED", "covers": ["vet-checked"]}],
              "vocabulary": REAL_LEDGER["vocabulary"]}
    assert ids(page("<p>Every puppy is KC registered and vet cleared for travel.</p>"), ledger) \
        == ["kc-registered"]


def test_a_row_without_covers_clears_nothing():
    ledger = {"claims": [{"id": "x", "pattern": r"tested\s+clear", "proof": "NOT FETCHED"}],
              "vocabulary": REAL_LEDGER["vocabulary"]}
    assert ids(page("<p>Parents tested clear.</p>"), ledger) == ["dna-clear"]


def test_the_real_ledger_row_covers_the_dna_vocabulary():
    row = next(c for c in REAL_LEDGER["claims"] if c["id"] == "parents-dna-clear")
    assert row["covers"] == ["dna-clear", "dna-test"]


def test_a_question_excuses_only_the_claim_inside_it():
    html = page("<p>Why does it matter? Every puppy is KC registered.</p>")
    assert ids(html) == ["kc-registered"]
    html = page('<p>Buyers ask \u201cAre they health tested?\u201d and every puppy is KC registered.</p>')
    assert ids(html) == ["kc-registered"]


def test_a_placeholder_excuses_only_its_own_claim():
    html = page("<p>We are a LICENCE_CLAIM_PLACEHOLDER licensed breeder and every pup is KC registered.</p>")
    assert ids(html) == ["kc-registered"]
    html = page("<p>LEGAL_CLAIM_PLACEHOLDER Every puppy is KC registered.</p>")
    assert ids(html) == ["kc-registered"]


@pytest.mark.parametrize("html,expected", [
    ('<div class="card">Our pups are KC registered</div><div class="card">DNA tests</div>',
     [("kc-registered", "Our pups are KC registered"), ("dna-test", "DNA tests")]),
    ("<ul><li>KC registered<li>Vet checked</ul>",
     [("kc-registered", "KC registered"), ("vet-checked", "Vet checked")]),
    ("<p>KC registered<br>Vet checked</p>",
     [("kc-registered", "KC registered"), ("vet-checked", "Vet checked")]),
])
def test_block_boundaries_split_sentences(html, expected):
    assert E.unledgered_claims(page(html), LEDGER) == expected


@pytest.mark.parametrize("sentence,vocab", [
    ("Both parents are hip-scored.", "hip-elbow-score"),
    ("Both parents have elbow-graded results.", "hip-elbow-score"),
    ("Every pup has a vet check before leaving.", "vet-checked"),
    ("Every pup is checked by our vet.", "vet-checked"),
    ("Each litter has a veterinary check at eight weeks.", "vet-checked"),
    ("Every puppy is registered with the Kennel Club.", "kc-registered"),
    ("Every puppy is registered with the KC.", "kc-registered"),
    ("We are licensed by the local council.", "licensed-breeder"),
    ("Both parents are DNA screened.", "dna-test"),
    ("The BVA hip scores are on file.", "hip-elbow-score"),
    ("No puppy leaves without being vet checked.", "vet-checked"),
])
def test_wider_recall(sentence, vocab):
    assert ids(page(f"<p>{sentence}</p>")) == [vocab]


@pytest.mark.parametrize("sentence", [
    "Our puppies are not KC registered.",
    "Our pups have never been DNA tested.",
    "We are not a licensed breeder.",
    "Ask to see the DNA test results for both parents.",
    "Ask for the vet check paperwork.",
    "The registry's own page on the L-2-HGA DNA test says what it screens.",
    "The registry's page for the HC-HSF4 DNA test explains it.",
    "Our dogs undergo BVA/KC eye examinations.",
    "The BVA's own description of the eye scheme sets out who may carry one out.",
])
def test_precision_denial_advice_reference_and_bva_eye_scheme(sentence):
    assert ids(page(f"<p>{sentence}</p>")) == []


@pytest.mark.parametrize("html,expected", [
    ('<p>She said \u201cthey are KC registered.\u201d Then we met Dr. Smith. Our pups are vet checked.</p>',
     ["She said \u201cthey are KC registered.\u201d", "Then we met Dr. Smith.",
      "Our pups are vet checked."]),
])
def test_splitter_quotes_and_abbreviations(html, expected):
    assert E.sentences(page(html)) == expected


def test_a_question_in_closing_quotes_is_still_a_question():
    assert ids(page('<p>\u201cAre the pups KC registered?\u201d</p>')) == []


def test_preview_pages_are_not_claim_checked():
    html = page("<p>Our DNA-tested parents live with us.</p>")
    budgets = {"budgets": {}, "terms": {}}
    for slug in ("board-preview/index", "kit-preview"):
        f = E.audit(slug, html, "interior", budgets, LEDGER)
        assert not [m for _, m in f if "un-ledgered" in m]


def test_a_missing_rebuilt_file_warns_on_stderr(tmp_path, capsys):
    assert E.rebuilt_slugs(tmp_path / "nope.json") == set()
    assert "rebuilt" in capsys.readouterr().err


# ── Task 20 re-review: no claim hides behind another clause's question, negation or advice ──
@pytest.mark.parametrize("sentence,expected", [
    ("Every puppy is KC registered — want to know why?", ["kc-registered"]),
    ("Every puppy is KC registered, want to know why?", ["kc-registered"]),
    ("Every puppy is KC registered; is that rare?", ["kc-registered"]),
    ("No hidden fees, KC registered and vet checked.", ["kc-registered", "vet-checked"]),
    ("Not only KC registered, our pups are health tested.", ["kc-registered", "health-tested"]),
    ("Read all about the KC registered puppies we breed.", ["kc-registered"]),
    ("Ask for details: every pup is KC registered.", ["kc-registered"]),
])
def test_no_bypass_through_another_clause(sentence, expected):
    assert ids(page(f"<p>{sentence}</p>")) == expected


@pytest.mark.parametrize("sentence", [
    "Want to know why every pup is KC registered?",
    "Every puppy is healthy — but is it KC registered?",
    "Read more about the KC registered scheme on the registry site.",
    "The registry's page about the DNA test explains it.",
])
def test_clause_scoped_exclusions_still_hold(sentence):
    assert ids(page(f"<p>{sentence}</p>")) == []
