# tests/py/test_no_third_party_contacts.py — saved competitor and SERP responses under
# data/queries/raw/, and the competitor research under docs/research/ (intel reports in
# docs/research/competitors/, proposals, gap matrices), must never carry third-party contact
# details (advertisers' and sellers' phone numbers, emails, WhatsApp links, street postcodes).
# The skill drops them before saving and notes what it dropped in "_saved_note"; the intel
# agent records contact signals as yes/no only (spec 2026-09-23 §14.8).
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = "data/queries/raw"
RESEARCH = "docs/research"
SCANNED = (RAW, RESEARCH)

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


def committed_files(root=ROOT, dirs=SCANNED):
    out = subprocess.run(["git", "ls-files", "-z", "--", *dirs], cwd=root, capture_output=True,
                         text=True, check=True).stdout
    return [pathlib.Path(root) / p for p in out.split("\0") if p]


def contact_hits(root=ROOT, dirs=SCANNED):
    """["path:line: kind 'match'"] for every contact detail in a committed file under `dirs`."""
    hits = []
    for f in committed_files(root, dirs):
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        hits += [f"{f.relative_to(root).as_posix()}:{i}: {kind} {m!r}"
                 for i, kind, m in find_contacts(text)]
    return hits


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


def main(argv=None):
    """Scan files or folders given on the command line: exit 1 naming each hit, else 0."""
    hits = []
    for arg in (sys.argv[1:] if argv is None else argv):
        base = pathlib.Path(arg)
        if not base.exists():
            print(f"contacts: {arg} does not exist")
            return 2
        for f in sorted([base] if base.is_file() else base.rglob("*")):
            if not f.is_file():
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            hits += [f"{f}:{i}: {kind} {m!r}" for i, kind, m in find_contacts(text)]
    for h in hits:
        print(f"contacts: {h}")
    print(f"contacts: {len(hits)} third-party contact detail{'' if len(hits) == 1 else 's'}")
    return 1 if hits else 0


def _git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def test_a_planted_phone_number_in_a_committed_research_report_is_caught(tmp_path):
    report = tmp_path / RESEARCH / "competitors/example-breeder.json"
    report.parent.mkdir(parents=True)
    report.write_text('{"trust": {"status": "ok", "values": {"phone": "07712 345678"}}}\n',
                      encoding="utf-8")
    clean = tmp_path / RESEARCH / "gap-matrix-2026-09-23.md"
    clean.write_text("| Leeds | 1/1 | 0 | no | high |\n", encoding="utf-8")
    elsewhere = tmp_path / "docs/other/notes.md"
    elsewhere.parent.mkdir(parents=True)
    elsewhere.write_text("call 07712 345678\n", encoding="utf-8")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", ".")
    assert contact_hits(tmp_path) == [
        "docs/research/competitors/example-breeder.json:1: phone '07712 345678'"]


def test_committed_raw_query_and_research_files_carry_no_third_party_contacts():
    hits = contact_hits()
    assert hits == [], ("third-party contact details in saved query files or competitor "
                        "research — drop them (reports record yes/no only; raw responses note "
                        "it in _saved_note):\n" + "\n".join(hits))


def test_the_scan_command_checks_uncommitted_reports_before_hand_off(tmp_path, capsys):
    # The intel agent writes reports it does not commit; the committed-file test above only
    # sees them later. `python3 tests/py/test_no_third_party_contacts.py <path>...` scans
    # files or folders now: exit 1 naming each hit, exit 0 when clean.
    dirty = tmp_path / "competitors/example-breeder.md"
    dirty.parent.mkdir()
    dirty.write_text("Phone shown: yes\nmail breeder.name@example.co.uk\n", encoding="utf-8")
    assert main([str(tmp_path)]) == 1
    assert "example-breeder.md:2: email" in capsys.readouterr().out
    dirty.write_text("Phone shown: yes\n", encoding="utf-8")
    assert main([str(tmp_path)]) == 0
    assert main([str(tmp_path / "missing")]) == 2


if __name__ == "__main__":
    sys.exit(main())
