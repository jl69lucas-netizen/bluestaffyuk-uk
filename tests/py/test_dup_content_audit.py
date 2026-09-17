"""The DUP gate's whitelists: exact heading match, and a measured body-stem list.

The header whitelist used to be a SUBSTRING test (`any(w in text for w in HEADER_WHITELIST)`),
so the one-word entry `contact` silently whitelisted every heading containing the string —
"Contact Us Today", "Contacting the Breeder", and any real crossover that happened to use the
word. The gate stopped being evidence. These tests pin the exact-match behaviour and the shape
of the measured list, so the substring trap cannot be reintroduced without a red test.
"""
import json
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
    findings = d.headers_mode(pages)
    assert [f["text"] for f in findings] == ["get in touch with our glasgow breeder today"]


def test_header_whitelist_still_exempts_the_exact_heading(tmp_path, capsys):
    page = '<h2>Get in Touch</h2>'
    for slug in ("a", "b"):
        f = tmp_path / slug
        f.mkdir()
        (f / "index.html").write_text(page, encoding="utf-8")
    pages = {s: tmp_path / s / "index.html" for s in ("a", "b")}
    assert d.headers_mode(pages) == []
    assert "PASS — no crossover headers in 2 pages." in capsys.readouterr().out


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


def test_the_typescript_parse_reads_entries_only_and_never_comment_prose():
    """Mirrors loadWhitelist() in tests/render/lib/dupCorpus.ts, anchor and all.

    The block's comments quote a phrase on purpose (see the fixture note there). An
    unanchored regex reads that quote as a whitelist entry — an exemption nobody wrote.
    """
    src = (REPO / "scripts/dup_content_audit.py").read_text(encoding="utf-8")
    start = src.index("WHITELIST_SNIPPETS")
    block = src[start:src.index("\n]", start)]
    anchored = re.findall(r'^\s*"([^"]{8,})",?\s*$', block, re.M)
    assert anchored == list(d.WHITELIST_SNIPPETS)

    unanchored = [m[0] or m[1] for m in re.findall(r'"([^"]{8,})"|\'([^\']{8,})\'', block)]
    assert len(unanchored) > len(anchored), (
        "the comment fixture that proves the anchor matters has been removed")


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


# ── the body path: unwhitelisted_segments() and crossovers() ──────────────────────────────
# These carry the rule the whitelist actually implements — the whitelist exempts LINES, not
# the runs they sit in — and until now only the TypeScript mirror in tests/render had tests
# for it. A stem fused into a longer shared run must be CUT OUT, with each side judged alone:
# skipping a run that merely CONTAINED a stem exempted the passage next to it (the 2026-09-11
# finding), and re-joining the sides after the cut glues two short shared phrases into one
# false passage.

def _toks(s):
    return re.findall(r"[a-z0-9$']+", s.lower())


STEM = "deposit 500 refundable"          # a real whitelist entry, 3 tokens


def test_a_stem_mid_passage_returns_both_sides_and_the_stem_in_neither():
    left = _toks("before a puppy leaves we record its weight every single morning and send")
    right = _toks("tell us which puppy you are asking about and when you would like to bring")
    segs = d.unwhitelisted_segments(left + _toks(STEM) + right)
    assert segs == [left, right]
    assert all(not any(t in seg for t in ("refundable",)) for seg in segs)
    assert sum(len(s) for s in segs) == len(left) + len(right)


def test_cutting_a_stem_out_does_not_rejoin_two_short_sides():
    """Six words each side: neither reaches MIN_WORDS, so the run is silent.

    Re-joining them instead would report one 12-word passage that exists on neither page.
    """
    left, right = _toks("questions about delivery days are welcome"), _toks("we send a photo the moment")
    assert len(left) == 6 and len(right) == 6
    segs = d.unwhitelisted_segments(left + _toks(STEM) + right)
    assert segs == [left, right]
    assert [s for s in segs if len(s) >= d.MIN_WORDS] == []


def test_a_run_that_is_only_a_whitelisted_stem_yields_nothing():
    assert d.unwhitelisted_segments(_toks(STEM)) == []


def test_every_occurrence_of_a_stem_is_cut_not_just_the_first():
    mid = _toks("and also")
    segs = d.unwhitelisted_segments(_toks(STEM) + mid + _toks(STEM))
    assert segs == [mid]


def test_crossovers_reports_the_unwhitelisted_passage_and_not_the_stem():
    shared_a = _toks("before a puppy leaves we record its weight every single morning and send the log")
    shared_b = _toks("tell us which puppy you are asking about and when you would like to bring one")
    wa = _toks("alpha bravo charlie") + shared_a + _toks(STEM) + shared_b + _toks("delta echo foxtrot")
    wb = _toks("golf hotel india") + shared_a + _toks(STEM) + shared_b + _toks("juliet kilo lima")
    found = d.crossovers(wa, d.shingles(wa), d.shingles(wb))
    assert [len(f) for f in found] == [len(shared_a), len(shared_b)]
    assert all("refundable" not in f for f in found)


def test_crossovers_is_silent_when_the_only_shared_run_is_whitelisted():
    wa = _toks("alpha bravo charlie delta") + _toks(STEM) + _toks("echo foxtrot golf hotel")
    wb = _toks("india juliet kilo lima") + _toks(STEM) + _toks("mike november oscar papa")
    assert d.crossovers(wa, d.shingles(wa), d.shingles(wb)) == []


def test_crossovers_is_silent_when_nothing_is_shared():
    wa = _toks("the quick brown fox jumps over the lazy dog again and again today")
    wb = _toks("a slow green turtle walks beneath the sleepy cat once or twice tonight")
    assert d.crossovers(wa, d.shingles(wa), d.shingles(wb)) == []


# ── the CLI contract (Tasks 6-8 convention) ───────────────────────────────────────────────
# Task 20 consumes these gates programmatically and must not scrape stdout, so the auditor
# offers the same surface every other audit script does: `--dist`, `--fail-on-error`, and
# `--json [PATH]` writing docs/reports/dup_content_audit.json by default.

def _fixture_dist(tmp_path, pages):
    for slug, body in pages.items():
        d_ = tmp_path / slug if slug != "index" else tmp_path
        d_.mkdir(parents=True, exist_ok=True)
        (d_ / "index.html").write_text(f"<main>{body}</main>", encoding="utf-8")
    return tmp_path


SHARED = ("Every puppy we place leaves our Glasgow home microchipped, vet-checked and fully "
          "vaccinated, with the paperwork in the folder before the pup ever travels.")


def test_dist_flag_replaces_the_hard_coded_dist_directory(tmp_path):
    dist = _fixture_dist(tmp_path, {"index": f"<p>{SHARED}</p>", "b": f"<p>{SHARED}</p>"})
    out = subprocess.run(
        [sys.executable, "scripts/dup_content_audit.py", "--dist", str(dist)],
        cwd=REPO, capture_output=True, text=True, timeout=60)
    assert out.returncode == 1
    assert "FAIL — 1 duplicated passages" in out.stdout


def test_json_report_has_the_documented_shape(tmp_path):
    dist = _fixture_dist(tmp_path, {"index": f"<p>{SHARED}</p>", "b": f"<p>{SHARED}</p>"})
    report = tmp_path / "report.json"
    subprocess.run(
        [sys.executable, "scripts/dup_content_audit.py", "--dist", str(dist),
         "--json", str(report)],
        cwd=REPO, capture_output=True, text=True, timeout=60)
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["mode"] == "body"
    assert data["pages"] == 2
    assert data["min_words"] == d.MIN_WORDS
    assert data["problems"] == len(data["findings"]) == 1
    f = data["findings"][0]
    assert set(f) == {"a", "b", "words", "run"}
    assert sorted((f["a"], f["b"])) == ["b", "index"]
    assert f["words"] == 25 and "microchipped" in f["run"]


def test_json_defaults_to_the_reports_directory(tmp_path):
    dist = _fixture_dist(tmp_path, {"index": "<p>nothing shared here at all</p>"})
    default = REPO / "docs/reports/dup_content_audit.json"
    before = default.read_text(encoding="utf-8") if default.exists() else None
    try:
        out = subprocess.run(
            [sys.executable, "scripts/dup_content_audit.py", "--dist", str(dist), "--json"],
            cwd=REPO, capture_output=True, text=True, timeout=60)
        assert out.returncode == 0
        assert str(default.relative_to(REPO)) in out.stdout
        assert json.loads(default.read_text(encoding="utf-8"))["problems"] == 0
    finally:
        if before is None:
            default.unlink(missing_ok=True)
        else:
            default.write_text(before, encoding="utf-8")


def test_headers_mode_writes_its_own_json_shape(tmp_path):
    page = "<h2>Meet the Proud Parents Behind Every Litter</h2>"
    dist = _fixture_dist(tmp_path, {"index": page, "b": page})
    report = tmp_path / "h.json"
    out = subprocess.run(
        [sys.executable, "scripts/dup_content_audit.py", "--dist", str(dist),
         "--headers", "--json", str(report)],
        cwd=REPO, capture_output=True, text=True, timeout=60)
    assert out.returncode == 1
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["mode"] == "headers" and data["problems"] == 1
    assert data["findings"][0]["kind"] == "exact"
    assert sorted(data["findings"][0]["pages"]) == ["b", "index"]


def test_fail_on_error_is_documented_in_the_docstring():
    """Exit-code semantics must be stated where the operator reads them."""
    doc = d.__doc__
    assert "--fail-on-error" in doc
    assert "Exit" in doc
