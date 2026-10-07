"""Gap G19 (Manchester page run, 2026-10-07): the image tools never offer an untruthful photo.

Manchester's board was offered two photos the page may not show:

  - kc-registered-staffy-puppies.webp, an AI picture of a puppy beside printed "Certificate of
    Health" sheets we do not hold: lessons.md lesson 7, swapped out of London at its Asset Gate
    (docs/reports/asset-gate-london/README.md A1);
  - breeder-sitting-blue-staffy-puppy-home.webp, whose served alt says "L-2-HGA clear": a
    health RESULT the evidence ledger holds at NOT FETCHED (`parents-dna-clear`), which no
    page may state (tests/py/test_no_health_result_stated.py).

Two rules, both read by image_candidates.untruthful(), which the candidate pools (block 7)
and original_slots' photo inventory (block 7d) both apply:

  1. BY RULE, from data/quality/evidence-ledger.json: an image whose served alt matches a
     claim the ledger does not prove — the `pattern` of a NOT FETCHED row that is not
     naming-only, or the vocabulary pattern of a claim id that no proved row and no
     naming-only row covers.
  2. BY NAME, data/quality/image-deny.json: the images lessons.md marks false (an image's
     words are copy, lessons 7), each with its reason and the lesson that marks it.
"""
import copy
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import image_candidates as IC  # noqa: E402
import original_slots as OS  # noqa: E402
import pageboard as PB  # noqa: E402

SLUG = "blue-staffy-puppies-manchester-uk"
CERT = "/images/kc-registered-staffy-puppies.webp"
L2HGA = "/images/breeder-sitting-blue-staffy-puppy-home.webp"
LEDGER = json.loads((ROOT / "data/quality/evidence-ledger.json").read_text(encoding="utf-8"))
DENY = json.loads((ROOT / "data/quality/image-deny.json").read_text(encoding="utf-8"))
LESSONS = (ROOT / "docs/reference/lessons.md").read_text(encoding="utf-8")


# ── the rule ────────────────────────────────────────────────────────────────────────────────
def test_the_live_tree_marks_both_files_and_says_why():
    bad = IC.untruthful(ROOT)
    assert CERT in bad and "lesson 7" in bad[CERT], bad.get(CERT)
    assert L2HGA in bad and "parents-dna-clear" in bad[L2HGA], bad.get(L2HGA)


def test_the_ledger_rule_reads_the_ledger_not_a_list():
    alts = {"/images/a.webp": ["Our dam, L-2-HGA clear."],
            "/images/b.webp": ["Both parents DNA tested for L-2-HGA."],      # naming: allowed
            "/images/c.webp": ["A puppy beside its Kennel Club registration form."],
            "/images/d.webp": ["Parents tested clear of HC-HSF4."]}
    got = IC.claim_hits(alts, LEDGER)
    assert set(got) == {"/images/a.webp", "/images/d.webp"}, got
    # Prove the result on file and the same alts pass: the ledger decides, not the tool.
    proved = copy.deepcopy(LEDGER)
    row = next(c for c in proved["claims"] if c["id"] == "parents-dna-clear")
    row["proof"], row["confirmed"] = "/docs/some-certificate.pdf", "2026-10-07"
    assert IC.claim_hits(alts, proved) == {}


def test_a_claim_no_row_holds_is_unproven_too():
    alts = {"/images/e.webp": ["Puppies from a council licensed breeder."]}
    got = IC.claim_hits(alts, LEDGER)
    assert list(got) == ["/images/e.webp"] and "licensed-breeder" in got["/images/e.webp"]


def test_the_vocabulary_sees_a_result_written_after_the_test_name():
    """`L-2-HGA clear` (the served alt) is the dna-clear claim; the vocabulary missed it."""
    pat = re.compile(LEDGER["vocabulary"]["dna-clear"], re.I)
    for text in ("L-2-HGA clear", "HC-HSF4: clear", "PHPV clear", "tested clear"):
        assert pat.search(text), text
    for text in ("L-2-HGA tested", "clear the table", "a clear view of the parents"):
        assert not pat.search(text), text


# ── the deny list ───────────────────────────────────────────────────────────────────────────
def test_every_denied_file_is_served_and_carries_its_reason_and_lesson():
    rows = DENY["files"]
    assert rows, "the deny list is empty: the check examined nothing"
    lessons = {int(n) for n in re.findall(r"^(\d+)\. \*\*", LESSONS, re.M)}
    for r in rows:
        assert set(r) == {"file", "reason", "lesson", "source"}, r
        assert (ROOT / "public" / r["file"].lstrip("/")).is_file(), r["file"]
        assert r["reason"].strip() and r["lesson"] in lessons, r
        assert (ROOT / r["source"].split("#")[0]).is_file(), r["source"]
    assert len({r["file"] for r in rows}) == len(rows)
    assert CERT in {r["file"] for r in rows}


# ── the tools apply it ──────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def manchester():
    return PB.load_board(SLUG)


def _offered(report):
    return {c["file"] for s in report["slots"] for c in s["candidates"] if c.get("file")}


def test_the_candidate_pools_never_offer_an_untruthful_photo(manchester):
    report = IC.candidates(manchester, ROOT, None)
    offered = _offered(report)
    assert offered, "no candidate at all: the check examined nothing"
    bad = IC.untruthful(ROOT)
    assert not offered & set(bad), sorted(offered & set(bad))


def test_the_written_candidates_file_offers_neither(manchester):
    f = ROOT / "data/boards/candidates" / f"{SLUG}.json"
    text = f.read_text(encoding="utf-8")
    assert CERT not in text and L2HGA not in text


def test_block_7d_never_proposes_an_untruthful_photo(manchester):
    OS._site_photos.cache_clear()
    inv = {p["path"] for p in OS.inventory(ROOT, manchester)}
    assert inv and not inv & set(IC.untruthful(ROOT))
    props = {o["photo"] for o in OS.propose(manchester, root=ROOT)}
    assert CERT not in props and L2HGA not in props


def _block(html, bid):
    i = html.index(f'data-id="{bid}"')
    j = html.find(' data-id="', i + 10)
    return html[i:j if j > 0 else len(html)]


def test_the_rendered_board_offers_neither():
    """No pick on the board names either file, and blocks 7 and 7d never show them. (The
    record's papers-checklist prompt names the certificate image to say why none is used.)"""
    html = (ROOT / f"docs/artifacts/boards/{SLUG}.html").read_text(encoding="utf-8")
    for f in (CERT, L2HGA):
        assert f"file:{f}" not in html, f
        name = f.rsplit("/", 1)[-1]
        for bid in ("7", "7d"):
            # The one mention allowed is the record's own reason for using none of them.
            block = _block(html, bid).replace(f"({name} props a", "")
            assert name not in block, (bid, f)
