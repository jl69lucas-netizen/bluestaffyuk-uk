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


def test_is_specimen_matches_the_two_preview_routes_and_nothing_else():
    """`/board-preview/<slug>/` and `/kit-preview/` render other pages' content as
    specimens — the board preview shows a record's own sections three styles over, and the
    kit preview renders the FAQ accordion over every row in data/faq.json. A passage shared
    with one of them is one passage rendered twice, not duplicate content, and both routes
    are noindex. The prefix is anchored so a real slug is never caught by containing one."""
    assert d.is_specimen("kit-preview")
    assert d.is_specimen("board-preview/privacy-policy-uk")
    assert d.is_specimen("board-preview/a/b")
    assert not d.is_specimen("index")
    assert not d.is_specimen("privacy-policy-uk")
    # anchored: a real page may not be excluded because its path mentions one
    assert not d.is_specimen("guides/kit-preview-notes")
    assert not d.is_specimen("kit-previewer")


def test_the_audit_drops_the_specimen_routes_from_its_corpus(tmp_path):
    """End to end: the same passage on a real page and on a specimen route is NOT a
    finding, while the same passage on two real pages still is."""
    shared = " ".join(["staffy"] * 6 + ["puppies raised in a family home with children"])
    for key in ("real-a", "kit-preview", "board-preview/real-a"):
        p = tmp_path / key / "index.html"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"<html><body><main><p>{shared}</p></main></body></html>", encoding="utf-8")
    out = tmp_path / "r.json"
    d.main(["--dist", str(tmp_path), "--json", str(out)])
    res = json.loads(out.read_text())
    assert res["pages"] == 1, res["pages"]
    assert res["problems"] == 0, res["findings"]

    (tmp_path / "real-b").mkdir()
    (tmp_path / "real-b" / "index.html").write_text(
        f"<html><body><main><p>{shared}</p></main></body></html>", encoding="utf-8")
    d.main(["--dist", str(tmp_path), "--json", str(out)])
    res = json.loads(out.read_text())
    assert res["pages"] == 2 and res["problems"] >= 1, res


# ── a board section's id is not a chrome marker ────────────────────────────────────────────

def _chrome(tag, attrs):
    """Whether `Text` would treat this element, and everything in it, as site chrome."""
    p = d.Text()
    p.handle_starttag(tag, attrs)
    return p.stack[-1][1]


def test_a_board_sections_own_id_is_not_read_as_chrome():
    """`paperwork-review` and `owner-review` are what two sections are ABOUT.

    CHROME_RE is a substring test, so the breeder's own section id put the whole section —
    prose, headings and a real buyer quote — outside the dup corpus and outside the word
    count, which read one of them as 0 prose words against a 35-50 band.
    """
    section = [("id", "paperwork-review"), ("data-section-label", "One owner on the paperwork"),
               ("class", "bl-box bl-frame-plain bl-cols-2 bl-head-inline")]
    assert _chrome("section", section) is False
    assert _chrome("section", [("id", "owner-review"), ("data-section-label", "x")]) is False


def test_a_chrome_class_is_still_chrome_wherever_the_token_sits():
    """The fix is about the ATTRIBUTE, not the position, and it has to be: the kit ships
    `page-toc`, where the token is the tail of a hyphenated name exactly as it is in
    `paperwork-review`. Anchoring the alternatives would have taken the table of contents out
    of the chrome set along with the false positive."""
    for cls in ("review-rail", "kit-nav page-toc", "toc", "msp-card", "read-card", "crumbs"):
        assert _chrome("div", [("class", cls)]) is True, cls


def test_a_section_id_is_still_chrome_when_it_is_not_a_board_section():
    """`data-section-label` is what a rebuilt page writes on a section of its record. Without
    it this is an ordinary element and its id is read as it always was."""
    assert _chrome("section", [("id", "paperwork-review")]) is True
    assert _chrome("div", [("id", "jump-list")]) is True


# ── headers mode reads the page, not the site chrome (London gate:page, 2026-10-05) ──────────
# The body path has always skipped <header>, <footer>, <nav> and <form> (SKIP_TAGS); headers
# mode ran one regex over the whole file. The kit footer (src/components/kit/SiteFooterKit.astro)
# renders three <h2> column headings — Explore, Contact, Follow — on every page that mounts it,
# so `--headers` reported all three on 23 pages, and gate:page failed every rebuilt page on
# chrome. HEADER_WHITELIST carries the OLD footer's headings for that reason ("site chrome not
# wrapped in <footer>"); the kit footer IS wrapped in <footer>, so the fix is structural.

KIT_FOOTER = ('<footer class="kit-footer"><h2>Explore</h2><h2>Contact</h2><h2>Follow</h2>'
              '</footer>')


def _pages(tmp_path, bodies):
    out = {}
    for slug, html in bodies.items():
        f = tmp_path / slug
        f.mkdir(parents=True, exist_ok=True)
        (f / "index.html").write_text(html, encoding="utf-8")
        out[slug] = f / "index.html"
    return out


def test_headers_mode_ignores_headings_inside_the_footer(tmp_path):
    page = f"<main><h2>{{}}</h2></main>{KIT_FOOTER}"
    pages = _pages(tmp_path, {"a": page.format("Where Our Litters Grow Up"),
                              "b": page.format("How the Deposit Works for You")})
    assert d.headers_mode(pages) == []


def test_headers_mode_ignores_header_nav_and_form_headings(tmp_path):
    chrome = ("<header><h2>Site Menu Heading</h2></header><nav><h2>Jump To</h2></nav>"
              "<form><h2>Enquire About a Puppy</h2></form>")
    pages = _pages(tmp_path, {"a": chrome + "<main><h2>One</h2></main>",
                              "b": chrome + "<main><h2>Two</h2></main>"})
    assert d.headers_mode(pages) == []


def test_a_real_body_duplicate_still_fails_beside_the_footer(tmp_path):
    """The known-broken case: same footer AND the same FAQ question in <main> on both pages.
    Only the body heading is reported — the chrome exclusion is not a hole for page content."""
    page = ('<main><section class="city-faq has-rail"><details><summary>'
            '<h3 data-faq-q>Are Staffies Hard to Train?</h3></summary></details></section>'
            f'</main>{KIT_FOOTER}')
    pages = _pages(tmp_path, {"a": page, "b": page})
    texts = [(f["kind"], f["text"]) for f in d.headers_mode(pages)]
    assert texts == [("exact", "are staffies hard to train?"),
                     ("template", "are {breed} hard to train?")]


def test_headers_mode_keeps_the_heading_text_as_the_regex_read_it(tmp_path):
    """Entities decoded, inner tags dropped without a space, as before the walker."""
    page = "<main><h3><span>Q</span>uestions &amp; Answers on <em>Blue</em> Staffies</h3></main>"
    pages = _pages(tmp_path, {"a": page, "b": page})
    assert [f["text"] for f in d.headers_mode(pages)][0] == "questions & answers on blue staffies"


# ── a `has-*` state class is not a chrome marker (London gate:page, 2026-10-05) ──────────────
# CHROME_RE is a substring test, and CityFaqLedger writes `has-rail` on the FAQ SECTION when it
# carries a photo rail. The whole top FAQ block of /uk-locations/blue-staffy-puppies-london/ —
# its H2, lede, questions and answers — was read as site chrome: the body gate never compared
# it, and pageboard counted "faq-top: 0 prose words". `has-rail` says the section HAS a rail;
# the rail itself is the child `<div class="rail">`, which is still chrome.

def test_a_has_rail_section_is_compared_but_its_rail_child_is_not():
    p = d.Text()
    p.feed('<section class="city-faq has-rail"><div class="rail">rail caption words</div>'
           '<div class="blk"><h2>FAQ heading words</h2><p>answer prose words</p></div></section>')
    text = " ".join(p.parts)
    assert "FAQ heading words" in text and "answer prose words" in text
    assert "rail caption words" not in text


def test_a_has_class_never_hides_a_real_chrome_token_beside_it():
    p = d.Text()
    p.feed('<div class="has-rail toc">jump links</div><p>kept</p>')
    assert " ".join(p.parts).split() == ["kept"]


# ── the guarantee cover is one data field with two spellings (London gate:page, 2026-10-05) ──
# data/settings.json `guarantee_cover` is mandated wording: CLAUDE.md "a page states that only as
# guarantee_cover words it". The whitelist carried only the spelling printed under a heading that
# already names the length (no "for two years"); the full clause, printed by a guarantee
# sentence (the homepage FAQ row home-health-guarantee and London's FAQ), was reported as a
# crossover — so no wording of a guarantee answer could ever pass the gate.

def test_the_full_guarantee_cover_clause_is_whitelisted_as_data():
    cover = json.loads((REPO / "data/settings.json").read_text(encoding="utf-8"))["guarantee_cover"]
    assert re.findall(r"[a-z0-9$']+", cover.lower()) in d.WHITELIST_STEMS


def test_the_guarantee_clause_is_cut_and_the_shared_question_beside_it_still_fails():
    cover = json.loads((REPO / "data/settings.json").read_text(encoding="utf-8"))["guarantee_cover"]
    shared = _toks("do you offer health guarantees for your blue staffy puppies yes every puppy "
                   "leaves with our written health guarantee which")
    wa = _toks("alpha bravo") + shared + _toks(cover) + _toks("charlie delta echo")
    wb = _toks("foxtrot golf") + shared + _toks(cover) + _toks("hotel india juliet")
    found = d.crossovers(wa, d.shingles(wa), d.shingles(wb))
    assert found == [shared]
