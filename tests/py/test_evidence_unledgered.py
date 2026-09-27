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
     "anchor": "dna-tests", "confirmed": None}],
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
