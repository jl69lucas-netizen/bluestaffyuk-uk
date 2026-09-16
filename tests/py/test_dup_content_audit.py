"""The DUP gate's whitelists: exact heading match, and a measured body-stem list.

The header whitelist used to be a SUBSTRING test (`any(w in text for w in HEADER_WHITELIST)`),
so the one-word entry `contact` silently whitelisted every heading containing the string —
"Contact Us Today", "Contacting the Breeder", and any real crossover that happened to use the
word. The gate stopped being evidence. These tests pin the exact-match behaviour and the shape
of the measured list, so the substring trap cannot be reintroduced without a red test.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

import dup_content_audit as d

REPO = Path(__file__).resolve().parents[2]


def test_header_whitelist_is_matched_exactly_not_as_a_substring(tmp_path):
    """A heading that merely CONTAINS a whitelisted phrase is still a crossover."""
    assert "get in touch" in d.HEADER_WHITELIST
    page = '<h2>Get in Touch With Our Glasgow Breeder Today</h2>'
    for slug in ("a", "b"):
        f = tmp_path / slug
        f.mkdir()
        (f / "index.html").write_text(page, encoding="utf-8")
    pages = {s: tmp_path / s / "index.html" for s in ("a", "b")}
    with pytest.raises(SystemExit) as e:
        d.headers_mode(pages)
    assert e.value.code == 1


def test_header_whitelist_still_exempts_the_exact_heading(tmp_path):
    page = '<h2>Get in Touch</h2>'
    for slug in ("a", "b"):
        f = tmp_path / slug
        f.mkdir()
        (f / "index.html").write_text(page, encoding="utf-8")
    pages = {s: tmp_path / s / "index.html" for s in ("a", "b")}
    d.headers_mode(pages)  # must not raise


def test_heading_normalisation_is_case_and_whitespace_insensitive():
    assert d._norm_heading("  Blue   Staffy News: Join 500+ Readers! ") == (
        "blue staffy news: join 500+ readers!")


def test_no_whitelist_entry_is_a_bare_common_word():
    """The trap that made the substring match dangerous: one-word entries."""
    short = [w for w in d.HEADER_WHITELIST if len(w.split()) == 1]
    assert set(short) <= {"roman", "byrd", "ince", "vennie", "christa", "cheryl"}


def test_whitelist_snippets_clear_the_typescript_floor():
    """tests/render/lib/dupCorpus.ts refuses to run below its FLOOR; keep them in step."""
    ts = (REPO / "tests/render/lib/dupCorpus.ts").read_text(encoding="utf-8")
    floor = int(re.search(r"const FLOOR = (\d+);", ts).group(1))
    assert len(d.WHITELIST_SNIPPETS) >= floor


def test_head_terms_are_the_sites_own_head_terms():
    assert "blue staffy puppies for sale" in d.HEAD_TERMS
    assert all("staff" in t for t in d.HEAD_TERMS)


def test_argparse_help_exits_without_running_an_audit():
    """--help used to fall through to a full dist/ audit (and exit 1 on findings)."""
    out = subprocess.run(
        [sys.executable, "scripts/dup_content_audit.py", "--help"],
        cwd=REPO, capture_output=True, text=True, timeout=60)
    assert out.returncode == 0
    assert "usage: dup_content_audit.py" in out.stdout
    assert "DUPLICATE" not in out.stdout
