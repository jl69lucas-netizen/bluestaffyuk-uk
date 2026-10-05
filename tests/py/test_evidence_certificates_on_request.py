"""The certificates sentence on the London page is ledgered, states no result, and leaves the
naming-only exemption for the tests working.

Ruling: the breeder in the build session's chat, 2026-10-05
(docs/reference/answer-board/answers/chat-2026-10-05-certificates-on-request.md): the parents'
certificates and DNA test results are shared on request and kept off the website. The London
health-tests lede carries it word for word, straight after the sentence that names the tests:

  "We share the parents' health certificates and DNA test results with you directly when you get
   in touch. We keep them off the website so they can't be copied or passed off as someone
   else's."

Two things could go wrong, and each has a test here:
  - the first sentence uses the dna-test and health-tested vocabulary, so it needs a ledger row
    (`certificates-on-request`), scoped to the sentence so it can never clear a result claim;
  - both sentences carry a word in evidence_audit.RESULT_WORDS ("results", "certificates",
    "passed"), so they must never be read as a REPEAT of the naming-only row
    `tests-named-no-result`, or its exemption (2026-10-05 london-gate-findings q04) would void.
    They are not: the exemption judges only the sentences that row's pattern matches, and these
    are separate sentences. The result check itself is not loosened.
"""
import copy
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_audit as ea  # noqa: E402

LIVE = json.loads((ROOT / "data/quality/evidence-ledger.json").read_text(encoding="utf-8"))
ROW_ID = "certificates-on-request"
NAMING_ID = "tests-named-no-result"
RULING = "docs/reference/answer-board/answers/chat-2026-10-05-certificates-on-request.md"
BUILT = ROOT / "dist/uk-locations/blue-staffy-puppies-london/index.html"

NAMING = "A health tested Staffy breeder names each parent's tests: L-2-HGA, HC-HSF4, eye screening and elbow screening."
SHARE = "We share the parents' health certificates and DNA test results with you directly when you get in touch."
KEEP = "We keep them off the website so they can't be copied or passed off as someone else's."
OTHER_NAMING = "DNA tests for two inherited conditions: L-2-HGA, a neurological disorder, and HC-HSF4, an inherited cataract."


def _row(ledger, cid):
    return next(c for c in ledger["claims"] if c["id"] == cid)


def _page(*paras):
    return "<html><body><main>" + "".join(f"<p>{p}</p>" for p in paras) + "</main></body></html>"


def test_the_row_cites_the_ruling_and_covers_no_result():
    row = _row(LIVE, ROW_ID)
    assert row["proof"].lstrip("/") == RULING and (ROOT / RULING).is_file()
    assert row["confirmed"] == "2026-10-05" and row["anchor"] == "health-tests"
    assert set(row["covers"]) == {"dna-test", "health-tested"}, "never dna-clear: no result is on file"
    assert not row.get("naming_only") and not row.get("repeat_ruling"), "a normal row, not an exemption"


def test_the_pattern_matches_the_ruled_sentence_and_nothing_wider():
    pat = _row(LIVE, ROW_ID)["pattern"]
    assert re.search(pat, SHARE, flags=re.I)
    for result in (
        "We share the parents' clear health certificates and DNA test results with you directly when you get in touch.",
        "We share the parents' health certificates and clear DNA test results with you directly when you get in touch.",
        "Both parents' DNA test results came back clear.",
        "We share the parents' health certificates.",
    ):
        assert not re.search(pat, result, flags=re.I), result


def test_the_ruled_sentences_raise_no_unledgered_claim():
    assert ea.unledgered_claims(_page(f"{NAMING} {SHARE} {KEEP}"), LIVE) == []


def test_without_the_row_the_sentence_is_an_unledgered_claim():
    """The row is what clears it: the vocabulary still sees the sentence."""
    ledger = copy.deepcopy(LIVE)
    ledger["claims"] = [c for c in ledger["claims"] if c["id"] != ROW_ID]
    ids = {vid for vid, s in ea.unledgered_claims(_page(SHARE), ledger) if s == SHARE}
    assert ids == {"dna-test", "health-tested"}


def test_a_result_added_to_the_sentence_gets_no_proof_from_this_row():
    """A result folded into the sentence is not this row's claim: the only row that covers it is
    `parents-dna-clear`, whose proof is NOT FETCHED, so the result stays unproven."""
    stated = "We share the parents' clear DNA results with you directly when you get in touch."
    covering = [c for c in LIVE["claims"]
                if "dna-clear" in (c.get("covers") or []) and re.search(c["pattern"], stated, flags=re.I)]
    assert [c["id"] for c in covering] == ["parents-dna-clear"]
    assert covering[0]["proof"] == "NOT FETCHED"


def test_the_naming_exemption_survives_the_result_words_next_to_it():
    """The naming row repeats (twice on this page) with the certificates sentences beside it: still
    no finding, because RESULT_WORDS is applied only to the sentences that repeat the naming row."""
    assert ea.RESULT_WORDS.search(SHARE) and ea.RESULT_WORDS.search(KEEP), "the premise of this test"
    html = _page(f"{NAMING} {SHARE} {KEEP}", OTHER_NAMING)
    assert NAMING_ID not in [cid for cid, _, _ in ea.claim_binding(html, LIVE)]


def test_a_naming_sentence_that_states_a_result_still_voids_the_exemption():
    """The result check is not loosened: fold a result into a repeated naming sentence and the row
    is judged like any other, so the repeat WARNs again."""
    stated = "DNA tests for two inherited conditions: L-2-HGA and HC-HSF4, with results we share."
    pat = _row(LIVE, NAMING_ID)["pattern"]
    ledger = copy.deepcopy(LIVE)
    _row(ledger, NAMING_ID)["pattern"] = pat.split("(?!", 1)[0]   # drop the row's own result guard
    html = _page(NAMING, stated, SHARE)
    assert NAMING_ID in [cid for cid, _, _ in ea.claim_binding(html, ledger)]


def test_the_built_page_carries_the_sentences_after_the_naming_one():
    if not BUILT.exists():
        pytest.skip("run npm run -s build first")
    sents = ea.sentences(BUILT.read_text(encoding="utf-8"))
    i = sents.index(NAMING)
    assert sents[i + 1:i + 3] == [SHARE, KEEP]
    html = BUILT.read_text(encoding="utf-8")
    assert not [r for r in ea.unledgered_claims(html, LIVE) if SHARE in r[1]]
    assert NAMING_ID not in [cid for cid, _, _ in ea.claim_binding(html, LIVE)]
