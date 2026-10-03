"""The London city page, rebuilt from its approved outline and board (page-run row 12).

What must hold once the scaffold is replaced:
  - no scaffold marker and no migrated body: London is a rebuilt page;
  - the H1 is the approved outline's H1, and every body H2/H3 is a question;
  - facts come from data: no hand-typed £ in the page source, parents Maggie and Jones,
    the tests named and no result stated, nothing about a licence;
  - the deposit is never called plainly "refundable": the word appears only inside the refund
    clause data/settings.json `deposit_refund_clause` carries (the user's rulings, 2026-09-27
    and 2026-09-30);
  - three FAQ blocks holding exactly the approved questions, and the page stays noindex until
    the user approves it;
  - at least three in-page enquiry CTAs (outline planned_tests, M2), a divider before every
    section of the main column (outline build_notes, M5: seams = sections), and every link the
    board lists, with no external link the board does not list (working rule 12).

WHERE THIS DIFFERS FROM THE PLAN'S TASK 26 TEXT (written 2026-09-30; the approved board wins):
  - "every H2/H3 is a question" is held on the BODY sections (scripts/page_sections.py
    body_sections) and on the three FAQ blocks. The approved board gives the frame rows (trust
    strip, takeaways, the three letters, the newsletter, the enquiry form, the contents) their
    own short labels, which are not questions, and the components render them as their H2.
  - the FAQ count is not hard-coded at 15-20. The board approved 21 questions (top 6, middle 7,
    bottom 8, after the breeder added "How Rare Are Blue Staffies?" on 2026-10-02, q04), so the
    expected set is read from the board's FAQ trees and must equal every FAQ `covered_by` text in
    data/queries/blue-staffy-puppies-london.json; each block stays inside its own 5-7 / 5-7 /
    7-10 band.
"""
import html as H
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import page_sections as PS  # noqa: E402

SLUG = "blue-staffy-puppies-london"
SRC = ROOT / "src/pages/uk-locations" / f"{SLUG}.astro"
BUILT = ROOT / "dist/uk-locations" / SLUG / "index.html"
OUTLINE = ROOT / "data/outlines" / f"{SLUG}.json"
BOARD = json.loads((ROOT / "data/boards" / f"{SLUG}.json").read_text(encoding="utf-8"))
QUERIES = json.loads((ROOT / "data/queries" / f"{SLUG}.json").read_text(encoding="utf-8"))
SETTINGS = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
FAQ_BAND = {"faq-top": (5, 7), "faq-middle": (5, 7), "faq-bottom": (7, 10)}


def built():
    if not BUILT.exists():
        pytest.skip("run npm run build first")
    return BUILT.read_text(encoding="utf-8")


def text(fragment):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def norm(s):
    return re.sub(r"\s+", " ", s.replace("’", "'")).strip().lower()


def main_html(html):
    return html.split("<main", 1)[1].split("</main>", 1)[0]


def main_text(html):
    return text(main_html(html))


def labelled_sections(html):
    """{id: html} for every <section data-section-label> on the page, each running to the next."""
    tags = list(re.finditer(r"<section\b[^>]*\bdata-section-label=[^>]*>", html))
    out = {}
    for i, m in enumerate(tags):
        sid = re.search(r'\bid="([^"]+)"', m.group(0))
        end = tags[i + 1].start() if i + 1 < len(tags) else len(html)
        out[sid.group(1) if sid else f"#{i}"] = html[m.start():end]
    return out


def board_faq_questions(section_id):
    sec = next(s for s in BOARD["sections"] if s["id"] == section_id)
    return [re.match(r"Q: (.*?) —", n["intent"]).group(1) for n in sec["tree"]]


def test_london_is_no_longer_a_scaffold():
    html = built()
    assert "data-city-scaffold" not in html
    assert "prose-migrated" not in html


def test_the_h1_is_the_approved_outline_h1():
    outline = json.loads(OUTLINE.read_text())
    assert outline["approval"], "STOP 2 is recorded"
    h1s = [text(h) for h in re.findall(r"<h1[^>]*>(.*?)</h1>", built(), re.S)]
    assert h1s == [outline["h1"]]


def test_every_body_h2_and_h3_is_a_question():
    secs = labelled_sections(built())
    ids = [s["id"] for s in PS.body_sections(BOARD)] + list(FAQ_BAND)
    heads = []
    for sid in ids:
        assert sid in secs, f"no labelled section #{sid} on the page"
        heads += [text(h) for h in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", secs[sid], re.S)]
    assert len(heads) >= 30
    assert [h for h in heads if not h.endswith("?")] == []


def test_no_price_is_typed_in_the_page_source():
    assert "£" not in SRC.read_text(encoding="utf-8")


def test_the_parents_are_maggie_and_jones():
    body = main_text(built())
    assert "Maggie" in body and "Jones" in body


def test_the_tests_are_named_and_no_result_is_stated():
    body = main_text(built())
    for name in ("L-2-HGA", "HC-HSF4"):
        assert name in body, name
    for m in re.finditer(r"L-2-HGA|HC-HSF4|eye screening|elbow screening", body, re.I):
        window = body[max(0, m.start() - 80): m.end() + 80].lower()
        assert not re.search(r"\bclear\b|\bcertified\b|will not be affected", window), window


def test_nothing_about_a_licence():
    body = main_text(built()).lower()
    assert "licence" not in body and "license" not in body


def test_the_deposit_is_never_plainly_refundable():
    body = main_text(built())
    clause = SETTINGS["deposit_refund_clause"]
    assert "70%" in clause, "the clause the test leans on still carries its percentage"
    for m in re.finditer(r"refundable", body, re.I):
        window = body[max(0, m.start() - 60): m.end() + 60]
        assert "70%" in window, window


def test_no_research_placeholder_ships():
    assert "NOT FETCHED" not in main_text(built())


def test_three_faq_blocks_holding_exactly_the_approved_questions():
    html = built()
    assert html.count('data-faq-block="') == 3
    secs = labelled_sections(html)
    expected_all = []
    for sid, (lo, hi) in FAQ_BAND.items():
        want = board_faq_questions(sid)
        got = [text(q) for q in re.findall(r"<h3[^>]*data-faq-q[^>]*>(.*?)</h3>", secs[sid], re.S)]
        assert [norm(g) for g in got] == [norm(w) for w in want], sid
        assert lo <= len(got) <= hi, (sid, len(got))
        expected_all += want
    covered = {norm(q["covered_by"]["text"]) for q in QUERIES["questions"]
               if q.get("covered_by") and q["covered_by"]["where"] == "faq"}
    assert covered == {norm(q) for q in expected_all}
    qs = re.findall(r"<h3[^>]*data-faq-q[^>]*>", html)
    assert len(qs) == len(expected_all)


def test_the_bottom_faq_answers_stay_short():
    secs = labelled_sections(built())
    answers = [text(a) for a in re.findall(r"</summary>\s*<p[^>]*>(.*?)</p>", secs["faq-bottom"], re.S)]
    assert len(answers) == len(board_faq_questions("faq-bottom"))
    assert sum(len(a.split()) for a in answers) / len(answers) <= 29


def test_at_least_three_enquiry_ctas():
    assert main_html(built()).count('href="#enquiry"') >= 3
    assert 'id="enquiry"' in built()


def test_a_divider_sits_before_every_section_of_the_main_column():
    """M5: seams = sections. The hero, counter and trust strip open the page above the column
    (PageShell's hero slot) and the contents panel sits under them; every other section has a
    divider before it."""
    html = main_html(built())
    secs = labelled_sections(html)
    column = [sid for sid in secs if sid not in {"top", "counter", "trust", "contents"}]
    assert len(column) == len(BOARD["sections"]) - 4
    assert html.count('class="kit-divider') == len(column)
    for sid, chunk in secs.items():
        if sid in column:
            before = html[: html.index(chunk)]
            last_divider = before.rfind('class="kit-divider')
            last_section = before.rfind("data-section-label=")
            assert last_divider > last_section, f"no divider before #{sid}"


def test_every_board_link_is_on_the_page_and_no_other_external_link():
    html = main_html(built())
    anchors = {(H.unescape(h), text(a)) for h, a in re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S)}
    listed = [l for s in BOARD["sections"] for kind in ("internal", "external")
              for l in s.get("links", {}).get(kind, [])]
    missing = [(l["href"], l["anchor"]) for l in listed
               if not any(h == l["href"] and a.startswith(l["anchor"]) for h, a in anchors)]
    assert missing == []
    external = {h for h, _ in anchors if h.startswith("http")}
    assert external <= {l["href"] for l in listed}, sorted(external)


def test_the_schema_names_london_and_carries_no_telephone():
    html = built()
    blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
    nodes = [n for b in blocks for n in (b if isinstance(b, list) else [b])]
    local = [n for n in nodes if n.get("@type") == "LocalBusiness"]
    assert len(local) == 1
    assert "London" in json.dumps(local[0].get("areaServed"))
    assert "telephone" not in local[0]


def test_noindex_until_the_user_approves_the_page():
    assert re.search(r'<meta name="robots" content="noindex[^"]*"', built())
