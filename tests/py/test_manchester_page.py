"""The Manchester city page, rebuilt from its approved outline and board (page-run row 12).

What must hold once the scaffold is replaced:
  - no scaffold marker, no scaffold line and no migrated body: Manchester is a rebuilt page;
  - the H1 is the approved outline's H1, and every body H2/H3 is a question (header Style 2);
  - every board section is one labelled <section> in <main>, with the board's id, in order;
  - the three FAQ blocks hold the board's questions (the nine STOP 3 wordings in place), and
    the question file's covered_by records each one;
  - facts come from data: no hand-typed £, parents Maggie and Jones, the tests named and no
    result stated, nothing about a licence, no video call, no rescue wording;
  - the deposit appears only with its refund clause, never plainly "refundable";
  - every board link is on the page except the two HELD ones, and no other external link;
  - the page stays noindex until the user approves it (Task 54).
"""
import html as H
import json
import pathlib
import re

import pytest

from test_manchester_board import REWORDED

ROOT = pathlib.Path(__file__).resolve().parents[2]
SLUG = "blue-staffy-puppies-manchester-uk"
SRC = ROOT / "src/pages/uk-locations" / f"{SLUG}.astro"
BUILT = ROOT / "dist/uk-locations" / SLUG / "index.html"
OUTLINE = json.loads((ROOT / "data/outlines" / f"{SLUG}.json").read_text(encoding="utf-8"))
BOARD = json.loads((ROOT / "data/boards" / f"{SLUG}.json").read_text(encoding="utf-8"))
QUERIES = json.loads((ROOT / "data/queries" / f"{SLUG}.json").read_text(encoding="utf-8"))
SETTINGS = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
FAQ_BAND = {"faq-top": 6, "faq-middle": 7, "faq-bottom": 7}
NODE_Q = re.compile(r"^Q:\s*(.+?)\s+—")
HELD = "HELD: built only once the deposit-order correction (STOP 2 q05 a) has landed on both pages"
ADOPTED = {old: new for old, (new, _) in REWORDED.items()}


def built():
    if not BUILT.exists():
        pytest.skip("run npm run -s build first")
    return BUILT.read_text(encoding="utf-8")


def text(fragment):
    """Visible words: an inline <span> breaks no word (src/lib/cityKit.ts `keepRuns` wraps a
    price or a test name in one), every other tag is a space."""
    fragment = re.sub(r"</?span\b[^>]*>", "", fragment)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def main_html(html):
    return html.split("<main", 1)[1].split("</main>", 1)[0]


def main_text(html):
    return text(main_html(html))


def labelled_sections(html):
    """[(id, html)] for every <section data-section-label> in <main>, each running to the next."""
    main = main_html(html)
    tags = list(re.finditer(r"<section\b[^>]*\bdata-section-label=[^>]*>", main))
    out = []
    for i, m in enumerate(tags):
        sid = re.search(r'\bid="([^"]+)"', m.group(0))
        end = tags[i + 1].start() if i + 1 < len(tags) else len(main)
        out.append((sid.group(1) if sid else f"#{i}", main[m.start():end]))
    return out


def board_faq_questions(section_id):
    sec = next(s for s in BOARD["sections"] if s["id"] == section_id)
    return [NODE_Q.match(n["intent"]).group(1) for n in sec["tree"]]


def board_links():
    return [(s["id"], kind, l) for s in BOARD["sections"] for kind in ("internal", "external")
            for l in s.get("links", {}).get(kind, [])]


def test_manchester_is_no_longer_a_scaffold():
    html = built()
    for mark in ("data-city-scaffold", "data-scaffold-tree", "prose-migrated", "Scaffold line, not copy."):
        assert mark not in html, mark


def test_the_h1_is_the_approved_outline_h1():
    assert OUTLINE["approval"], "STOP 2 is recorded"
    h1s = [text(h) for h in re.findall(r"<h1[^>]*>(.*?)</h1>", built(), re.S)]
    assert h1s == [OUTLINE["h1"]]


def test_every_body_h2_and_h3_is_a_question():
    heads = [text(h) for h in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", main_html(built()), re.S)]
    assert heads
    assert [h for h in heads if not h.endswith("?")] == []


def test_every_board_section_is_one_labelled_section_with_the_boards_id_in_order():
    ids = [sid for sid, _ in labelled_sections(built())]
    assert ids == [s["id"] for s in BOARD["sections"]], ids


def test_three_faq_blocks_holding_the_boards_questions_and_covered_by_records_them():
    html = built()
    secs = dict(labelled_sections(html))
    assert html.count('data-faq-block="') == 3
    shown = []
    for sid, n in FAQ_BAND.items():
        want = board_faq_questions(sid)
        got = [text(q) for q in re.findall(r"<h3[^>]*data-faq-q[^>]*>(.*?)</h3>", secs[sid], re.S)]
        assert got == want and len(got) == n, (sid, got)
        shown += got
    assert set(ADOPTED.values()) <= set(shown) and not set(ADOPTED) & set(shown)
    covered = {q["covered_by"]["text"] for q in QUERIES["questions"]
               if q.get("covered_by") and q["covered_by"]["where"] == "faq"}
    assert covered == set(shown)
    assert not [q["id"] for q in QUERIES["questions"] if q["must_answer"] and not q.get("covered_by")]


def test_no_price_is_typed_in_the_page_source():
    assert "£" not in SRC.read_text(encoding="utf-8")


def test_the_parents_are_maggie_and_jones():
    body = main_text(built())
    assert "Maggie" in body and "Jones" in body


def test_the_tests_are_named_and_no_result_is_stated():
    body = main_text(built())
    for name in ("L-2-HGA", "HC-HSF4"):
        assert name in body, name
    for m in re.finditer(r"L-2-HGA|HC-HSF4", body):
        window = body[max(0, m.start() - 80): m.end() + 80].lower()
        assert not re.search(r"\bclear\b|\bcertified\b|will not be affected", window), window


def test_nothing_about_a_licence_a_video_call_or_a_rescue():
    body = main_text(built()).lower()
    for word in ("licence", "license", "video call", "rescue"):
        assert word not in body, word


def test_the_deposit_is_never_plainly_refundable():
    body = main_text(built()).lower()
    clause = SETTINGS["deposit_refund_clause"].lower()
    assert body.count("refundable") == body.count(clause) > 0


def test_no_research_placeholder_ships():
    body = main_text(built())
    for mark in ("NOT FETCHED", "PHONE_PLACEHOLDER", "LICENCE_CLAIM_PLACEHOLDER", "LEGAL_CLAIM_PLACEHOLDER"):
        assert mark not in body, mark


def test_every_enquiry_cta_points_at_the_board_id():
    html = built()
    assert 'id="enquiry"' in html and 'href="#enquire"' not in html
    assert main_html(html).count('href="#enquiry"') >= 3


def test_every_board_link_is_on_the_page_but_the_held_two_and_no_other_external_link():
    main = main_html(built())
    anchors = {(H.unescape(h), text(a)) for h, a in re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', main, re.S)}
    rows = board_links()
    held = [l for _, _, l in rows if HELD in l["why"]]
    assert sorted(l["href"] for l in held) == ["/blue-staffy-pup-sale-uk/", "/buy-blue-staffy-puppies-uk/"]
    missing = [(l["href"], l["anchor"]) for _, _, l in rows if HELD not in l["why"]
               and not any(h == l["href"] and a.startswith(l["anchor"]) for h, a in anchors)]
    assert missing == []
    assert not [l["href"] for l in held if any(h == l["href"] for h, _ in anchors)], "a held link was built"
    external = {h for h, _ in anchors if h.startswith("http")}
    assert external <= {l["href"] for _, kind, l in rows if kind == "external"}, sorted(external)


def test_the_schema_names_greater_manchester_and_carries_no_telephone():
    html = built()
    nodes = []
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        data = json.loads(block)
        for n in data if isinstance(data, list) else [data]:
            nodes += n.get("@graph", [n])
    local = [n for n in nodes if n.get("@type") == "LocalBusiness"]
    # The layout's site-wide node and the page's own share one @id: one business, described twice.
    assert local and len({n.get("@id") for n in local}) == 1
    assert any("Manchester" in json.dumps(n.get("areaServed")) for n in local)
    assert not [n for n in local if "telephone" in n]
    faq = [n for n in nodes if n.get("@type") == "FAQPage"]
    assert len(faq) == 1 and len(faq[0]["mainEntity"]) == sum(FAQ_BAND.values())


def test_noindex_until_the_user_approves_the_page():
    assert re.findall(r'<meta name="robots" content="([^"]*)"', built()) == ["noindex, follow"]
    assert 'robots="noindex, follow"' in SRC.read_text(encoding="utf-8")
