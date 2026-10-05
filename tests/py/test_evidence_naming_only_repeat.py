"""claim-bound-to-proof accepts the repeated NAMING of the tests under the breeder's ruling,
and still warns on a repeated unproven RESULT claim.

Rulings: answer board 2026-09-29 q01 (name the tests, never state a result) and 2026-10-05
london-gate-findings q04 (a) ("Yes, the check accepts the repeats under your ruling"). The
acceptance lives in the check (scripts/evidence_audit.py claim_binding), keyed on the ledger
row's `naming_only` + `repeat_ruling`; the WARN is not deleted globally.
"""
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_audit as ea  # noqa: E402

LIVE = json.loads((ROOT / "data/quality/evidence-ledger.json").read_text(encoding="utf-8"))
NAMING_ID = "tests-named-no-result"


def _row(ledger, cid):
    return next(c for c in ledger["claims"] if c["id"] == cid)


def _page(*paras):
    return "<html><body><main>" + "".join(f"<p>{p}</p>" for p in paras) + "</main></body></html>"


# The London page's own naming sentences (dist, 2026-10-05), each a hit for the naming row.
NAMING = (
    "A health tested Staffy breeder names each parent's tests: L-2-HGA, HC-HSF4, eye screening and elbow screening.",
    "DNA tests for two inherited conditions: L-2-HGA, a neurological disorder, and HC-HSF4, an inherited cataract.",
    "Eye screening looks for inherited eye disease a DNA test misses, and elbow screening belongs on the same list.",
    "Six things, one per line: the two DNA tests, eye and elbow checks, the warning signs and how to check it.",
)


def _ids(html, ledger):
    return [cid for cid, _, _ in ea.claim_binding(html, ledger)]


def test_the_live_row_carries_the_ruling_and_its_files_exist():
    row = _row(LIVE, NAMING_ID)
    assert row["naming_only"] is True
    rulings = row["repeat_ruling"]
    assert any("2026-09-29-lisa-bright-five-facts" in r and r.endswith("#q01") for r in rulings)
    assert any("2026-10-05-london-gate-findings" in r and r.endswith("#q04") for r in rulings)
    assert ea.accepted_repeat_rulings(row) == rulings


def test_only_the_naming_row_is_excused():
    """No result row may carry the acceptance: the fields belong to naming rows only."""
    excused = [c["id"] for c in LIVE["claims"] if ea.accepted_repeat_rulings(c)]
    assert excused == [NAMING_ID]


def test_repeated_naming_under_the_ruling_is_not_a_finding():
    html = _page(*NAMING)
    assert NAMING_ID not in _ids(html, LIVE)


def test_without_the_ruling_the_same_repeats_still_warn():
    """The ruling is what earns it: strip the fields and the row warns as it did before q04."""
    ledger = copy.deepcopy(LIVE)
    row = _row(ledger, NAMING_ID)
    del row["naming_only"], row["repeat_ruling"]
    out = ea.claim_binding(_page(*NAMING), ledger)
    assert [(c, p) for c, _, p in out if c == NAMING_ID] == [(NAMING_ID, "NOT FETCHED")]


def test_a_missing_ruling_file_voids_the_acceptance(capsys):
    ledger = copy.deepcopy(LIVE)
    _row(ledger, NAMING_ID)["repeat_ruling"] = ["docs/reference/answer-board/answers/no-such-file.md#q04"]
    assert NAMING_ID in _ids(_page(*NAMING), ledger)
    assert "no-such-file.md" in capsys.readouterr().err


def test_a_naming_sentence_that_states_a_result_voids_the_acceptance():
    """A result word BEFORE the match escapes the pattern's own lookahead; the check reads the
    whole sentence, so the repeat is judged as a result claim and warns."""
    result = "Clear results on file: a health tested Staffy breeder names each parent's tests, L-2-HGA and HC-HSF4."
    html = _page(result, *NAMING[1:])
    out = ea.claim_binding(html, LIVE)
    assert [(c, p) for c, _, p in out if c == NAMING_ID] == [(NAMING_ID, "NOT FETCHED")]


def test_a_repeated_unproven_result_claim_still_warns():
    """parents-dna-clear carries no ruling: two result claims warn exactly as before q04."""
    html = _page("Both parents were tested clear of L-2-HGA.", "Jones is certified clear of HC-HSF4.")
    out = ea.claim_binding(html, LIVE)
    assert ("parents-dna-clear", 2, "NOT FETCHED") in out
    f = ea.audit("uk-locations/x", html, "location", {"budgets": {}, "terms": {}}, LIVE)
    assert any(s == "WARN" and "parents-dna-clear" in m for s, m in f)


@pytest.mark.parametrize("word", ["passed", "negative", "unaffected", "certificates", "free of"])
def test_each_result_word_voids_it(word):
    s = f"Both DNA tests for two inherited conditions {word} the board's list, L-2-HGA and HC-HSF4."
    sent = ea.sentences(_page(s))
    assert sent and ea._states_result(sent[0], LIVE)


def test_the_built_london_page_has_no_naming_finding():
    built = ROOT / "dist/uk-locations/blue-staffy-puppies-london/index.html"
    if not built.exists():
        pytest.skip("run npm run build first")
    assert NAMING_ID not in _ids(built.read_text(encoding="utf-8"), LIVE)
