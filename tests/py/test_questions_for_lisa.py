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
    old = re.findall(r"the `([\w-]+)` row in `data/faq\.json`", text)
    assert new and old
    assert [i for i in new if i in ids] == [], "a row the sheet calls new already exists"
    assert [i for i in old if i not in ids] == [], "a row the sheet calls existing is missing"


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
