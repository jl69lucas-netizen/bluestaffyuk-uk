"""Lisa Bright's question sheet (user ruling R6, 2026-09-23; Known Issues 41, 7 and 54).

The sheet is what the breeder reads, so it says each question once, in plain English, and
under each one where the website keeps her answer. Those lines are a promise about files,
so they are checked against the files: a row the sheet calls existing exists, a row it calls
new does not (yet), and every file it names is on disk.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import placeholder_check  # noqa: E402

SHEET = ROOT / "docs" / "reference" / "questions-for-lisa.md"
QUESTION = re.compile(r"^(\d+)\. \*\*(.+?)\*\*(.*?)(?=^\d+\. \*\*|^## |\Z)", re.M | re.S)
GOES = "**Where it goes:**"
LEDGER = ROOT / "data" / "quality" / "evidence-ledger.json"
# An existing faq row is named either alone — "the `a` row in `data/faq.json`" — or in a list,
# "the `a`, `b` and `c` rows in `data/faq.json`"; every id in the list is checked.
OLD_ONE = r"the `([\w-]+)` row in `data/faq\.json`"
OLD_LIST = r"the (`[\w-]+`(?:, `[\w-]+`)*,? and `[\w-]+`) rows in `data/faq\.json`"  # Oxford comma or not


def existing_rows(text):
    ids = re.findall(OLD_ONE, text)
    for group in re.findall(OLD_LIST, text):
        ids += re.findall(r"`([\w-]+)`", group)
    return ids


def test_the_row_list_reader_takes_an_oxford_comma():
    for text in ("the `a`, `b` and `c` rows in `data/faq.json`",
                 "the `a`, `b`, and `c` rows in `data/faq.json`"):
        assert existing_rows(text) == ["a", "b", "c"], text


def questions():
    return [(int(n), " ".join(q.split()), " ".join(body.split()))
            for n, q, body in QUESTION.findall(SHEET.read_text(encoding="utf-8"))]


def test_twenty_one_questions_numbered_in_order():
    assert [n for n, _, _ in questions()] == list(range(1, 22))


def test_every_question_says_where_the_answer_goes_and_names_a_real_file():
    for n, q, body in questions():
        assert GOES in body, (n, q)
        where = body.split(GOES, 1)[1]
        files = re.findall(r"`(data/[\w./-]+\.json)`", where)
        assert files, (n, "names no data file")
        for f in files:
            assert (ROOT / f).is_file(), (n, f)


def test_faq_rows_called_existing_exist_and_new_ones_do_not():
    ids = {r["id"] for r in json.loads((ROOT / "data/faq.json").read_text(encoding="utf-8"))}
    text = " ".join(SHEET.read_text(encoding="utf-8").split())
    new = re.findall(r"a new row `([\w-]+)` in `data/faq\.json`", text)
    old = existing_rows(text)
    assert new and old
    assert [i for i in new if i in ids] == [], "a row the sheet calls new already exists"
    assert [i for i in old if i not in ids] == [], "a row the sheet calls existing is missing"


def test_q8_names_every_faq_row_the_dna_clear_ledger_row_matches():
    # The ledger's own pattern for the unproven "parents are DNA clear" claim, applied the way
    # scripts/evidence_audit.py applies it (re.I), to each faq row's question and answer.
    pattern = next(c["pattern"] for c in json.loads(LEDGER.read_text(encoding="utf-8"))["claims"]
                   if c["id"] == "parents-dna-clear")
    rows = json.loads((ROOT / "data/faq.json").read_text(encoding="utf-8"))
    claiming = {r["id"] for r in rows if re.search(pattern, r["q"] + " " + r["a"], re.I)}
    # Answered (answer board q01, 2026-09-29): the breeder holds no DNA certificates, so every
    # row Q8 named was reworded to name the tests only, and no row may claim a clear result.
    assert claiming == set(), f"a faq row states the parents' DNA result again: {sorted(claiming)}"
    q8 = next(body for n, _, body in questions() if n == 8)
    named = set(existing_rows(q8.split(GOES, 1)[1]))
    assert named, "Q8 no longer names the rows it sent to the ledger"


def test_settings_keys_called_existing_exist_and_new_ones_do_not():
    keys = set(json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8")))
    text = " ".join(SHEET.read_text(encoding="utf-8").split())
    new = set()
    for m in re.finditer(r"new keys? (?:in `data/settings\.json`: )?(.*?)(?:\.|$)", text):
        new |= set(re.findall(r"`([a-z_]+)`", m.group(1)))
    named = set(re.findall(r"`([a-z_]+)`(?: and `([a-z_]+)`)? in `data/settings\.json`", text))
    old = {k for pair in named for k in pair if k} - new
    assert {"kc_assured_breeder", "breeding_licence_number", "lucys_law_wording"} <= new
    assert new.isdisjoint(keys), sorted(new & keys)
    assert old and old <= keys, sorted(old - keys)


def test_the_sheet_carries_no_stand_in_token():
    text = SHEET.read_text(encoding="utf-8")
    assert [t for t in placeholder_check.PLACEHOLDERS if t in text] == []
