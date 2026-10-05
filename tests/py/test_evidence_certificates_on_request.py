"""The certificates sentences are ledgered, state no result, and leave the naming-only exemption
for the tests working. London's came first; ten more pages carry the same two facts in their own
words (answer board 2026-10-05 certificates-and-london-tweaks q01 (a)), and one row,
`certificates-on-request`, covers all eleven, each sentence spelled to its full stop.

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


# ── the eleven sentences (answer board 2026-10-05 certificates-and-london-tweaks q01 (a)) ─────
TWEAKS = "docs/reference/answer-board/answers/2026-10-05-certificates-and-london-tweaks-2026-10-05.md"
# page (dist path) -> its one certificates sentence, word for word to its full stop.
ELEVEN = {
    "uk-locations/blue-staffy-puppies-london/index.html": SHARE,
    "index.html": "Write to us and the certificates for Maggie and Jones are yours to read.",
    "blue-staffy-health-uk/index.html":
        "The DNA results behind that table are Maggie's and Jones's own, and we hand them to you "
        "privately once you have contacted us.",
    "blue-staffy-uk-breeders/index.html":
        "The real two are written up in each parent's own certificates, which every family receives "
        "after its first message and which we leave off this site so they cannot be reused.",
    "buy-staffy-puppies-for-sale-uk/index.html": "Their certificates reach you after you make contact.",
    "buy-blue-staffy-puppies-uk/index.html": "Their test papers are for buyers rather than browsers.",
    "blue-staffy-pup-sale-uk/index.html":
        "Seeing their DNA paperwork costs nothing: ask once you are in contact with us and we hand it "
        "over, though never on this page, where a stranger could copy it.",
    "uk-blue-staffy-puppy-buying-guide/index.html":
        "Their certificates are yours to see in private after you write, and never on this guide, "
        "since anything posted here could be pinned to some other litter.",
    "uk-staffordshire-bull-terrier-guide/index.html":
        "The paper itself is what we hold back from the internet: contact us and you can read it, but "
        "a certificate published online can be copied onto any dog.",
    "blue-staffy-blog-guides/index.html":
        "No guide here carries the certificates themselves: they come to you after you write, which "
        "keeps them out of reach of anyone who would copy them.",
    "uk-blue-staffy-breeders-contact/index.html":
        "Ask in your message to read the parents' DNA and health certificates and we will pass them "
        "on; none of them is posted here, which stops anyone cloning them.",
}
# The buy page's sentence is data/faq.json `whyus-evidence`, which /kit-preview/ also renders as a
# specimen; evidence_audit.py does not audit the preview (PREVIEW_PREFIXES), so it is named here.
PREVIEW_ALSO = {"kit-preview/index.html": ELEVEN["buy-staffy-puppies-for-sale-uk/index.html"]}


def _pat():
    return re.compile(_row(LIVE, ROW_ID)["pattern"])


def _results(sentence):
    """Ways a result could be folded into a ruled sentence: inserted, appended, or prefixed."""
    body = sentence.rstrip(".")
    word = re.search(r"\b(?:DNA|certificates?|papers|paperwork|paper)\b", sentence)
    assert word, sentence
    inserted = sentence[:word.start()] + "clear " + sentence[word.start():]
    return [inserted,
            sentence.replace(" own", " clear", 1) if " own" in sentence else inserted.replace("clear ", "passed "),
            body + ", and both came back clear.",
            body + ", all of them passed.",
            body + " with clear results.",
            "Clear: " + sentence,
            "Both tested clear, " + sentence[0].lower() + sentence[1:],
            "Maggie passed; " + sentence]


def test_the_row_cites_both_rulings_and_records_what_the_documents_hold():
    row = _row(LIVE, ROW_ID)
    assert TWEAKS in row["basis"] and (ROOT / TWEAKS).is_file()
    # q03 (b): the certificates name the laboratory and give grades or scores. A fact ABOUT the
    # documents: the row says so and states none of it.
    notes = row["notes"]
    assert "q03" in notes and "name the testing laboratory and give grades or scores" in notes
    assert "no laboratory name, grade or score is in the repository" in notes


@pytest.mark.parametrize("rel", sorted(ELEVEN))
def test_the_pattern_matches_each_sentence_whole(rel):
    sentence = ELEVEN[rel]
    m = _pat().search(sentence)
    assert m and m.group(0) == sentence, sentence
    curly = sentence.replace("'", "\u2019")
    assert _pat().search(curly), "a typographic apostrophe is the same sentence"


@pytest.mark.parametrize("rel", sorted(ELEVEN))
def test_a_result_appended_inserted_or_prefixed_is_not_covered(rel):
    sentence = ELEVEN[rel]
    for worse in _results(sentence):
        assert worse != sentence, worse
        assert not _pat().search(worse), f"the row would cover a result: {worse}"


def test_a_result_sentence_beside_a_ruled_one_stays_unledgered():
    """A separate result sentence next to a ruled one is its own claim: the ruled sentence is
    still covered, and the result is caught as an unledgered dna-clear claim, never cleared."""
    for sentence in ELEVEN.values():
        stated = "Both parents tested clear."
        out = ea.unledgered_claims(_page(f"{sentence} {stated}"), LIVE)
        assert not [r for r in out if r[1] == sentence], sentence
        covering = [c["id"] for c in LIVE["claims"] if re.search(c["pattern"], stated, flags=re.I)]
        assert ROW_ID not in covering and "parents-dna-clear" in covering


def test_each_page_carries_its_one_sentence_and_no_other_page_carries_one():
    dist = ROOT / "dist"
    if not dist.exists():
        pytest.skip("run npm run -s build first")
    pat, found, examined = _pat(), {}, 0
    for f in dist.rglob("*.html"):
        rel = str(f.relative_to(dist))
        if "board-preview" in f.parts:
            continue
        examined += 1
        hits = [s for s in ea.sentences(f.read_text(encoding="utf-8")) if pat.search(s)]
        if hits:
            found[rel] = hits
    assert examined > 50, f"examined only {examined} built pages"
    want = {rel: [s] for rel, s in {**ELEVEN, **PREVIEW_ALSO}.items()}
    assert found == want, found
    for rel in ELEVEN:
        html = (dist / rel).read_text(encoding="utf-8")
        assert not [r for r in ea.unledgered_claims(html, LIVE) if r[1] == ELEVEN[rel]], rel
