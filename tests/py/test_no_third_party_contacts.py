# tests/py/test_no_third_party_contacts.py — saved competitor and SERP responses under
# data/queries/raw/ must never carry third-party contact details (advertisers' phone numbers,
# emails, WhatsApp links, street postcodes). The skill drops them before saving and notes what
# it dropped in "_saved_note" (spec 2026-09-23 §14.8).
import pathlib
import re
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = "data/queries/raw"

PATTERNS = {
    # UK mobile (07… / +44 7…) and any +44 number: 9–10 digits after the prefix
    "phone": re.compile(r"(?<![\w+])(?:\+44[\s-]?(?:\(0\)[\s-]?)?|0)7(?:[\s-]?\d){8,9}(?!\d)"
                        r"|\+44[\s-]?(?:\(0\)[\s-]?)?[1-9](?:[\s-]?\d){8,9}(?!\d)"),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"),
    "whatsapp": re.compile(r"wa\.me/\+?\d+"),
    "postcode": re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}\b"),
}


def find_contacts(text):
    """[(line number, kind, match)] for every contact detail in `text`."""
    return [(i, kind, m.group(0)) for i, line in enumerate(text.splitlines(), 1)
            for kind, pat in PATTERNS.items() for m in pat.finditer(line)]


def committed_raw_files():
    out = subprocess.run(["git", "ls-files", "-z", RAW], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout
    return [ROOT / p for p in out.split("\0") if p]


@pytest.mark.parametrize("text,kind", [
    ("call 07712 345678 today", "phone"),
    ("tel +44 7712 345 678", "phone"),
    ("+44 (0)161 496 0000", "phone"),
    ("07712345678", "phone"),
    ("mail breeder.name@example.co.uk", "email"),
    ("https://wa.me/447712345678", "whatsapp"),
    ("Deansgate, Manchester M3 4LZ", "postcode"),
    ("Leeds LS1 4DY", "postcode"),
])
def test_the_detector_finds_each_kind(text, kind):
    assert [k for _, k, _ in find_contacts(text)] == [kind]


@pytest.mark.parametrize("text", [
    "L2-HGA and HC tests", "price £1,500 deposit £500", "2026-09-23T10:00:00Z",
    "cost_usd 0.0725", "id 76328", "serp position 7", "M62 motorway", "page 0161",
])
def test_the_detector_ignores_ordinary_data(text):
    assert find_contacts(text) == []


def test_committed_raw_query_files_carry_no_third_party_contacts():
    hits = []
    for f in committed_raw_files():
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        hits += [f"{f.relative_to(ROOT)}:{i}: {kind} {m!r}" for i, kind, m in find_contacts(text)]
    assert hits == [], ("third-party contact details in saved query files — drop them and note "
                        "it in _saved_note:\n" + "\n".join(hits))
