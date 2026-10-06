"""The London city page, rebuilt from its approved outline and board (page-run row 12).

What must hold once the scaffold is replaced:
  - no scaffold marker and no migrated body: London is a rebuilt page;
  - the H1 is the approved outline's H1, and every body H2/H3 is a question;
  - facts come from data: no hand-typed £ in the page source, parents Maggie and Jones,
    the tests named and no result stated, nothing about a licence;
  - the deposit is never called plainly "refundable": the word appears only inside the refund
    clause data/settings.json `deposit_refund_clause` carries (the user's rulings, 2026-09-27
    and 2026-09-30);
  - three FAQ blocks holding exactly the approved questions, and, since the breeder approved the
    page on 2026-10-06 (docs/reference/answer-board/answers/
    final-approval-blue-staffy-puppies-london-2026-10-06.md), the page is indexable and listed in
    the sitemap;
  - at least three in-page enquiry CTAs (outline planned_tests, M2), a divider before every
    section of the main column (outline build_notes, M5: seams = sections), and every link the
    board lists, with no external link the board does not list (working rule 12).

WHERE THIS DIFFERS FROM THE PLAN'S TASK 26 TEXT (written 2026-09-30; the approved board wins):
  - "every H2/H3 is a question" is held on the BODY sections (scripts/page_sections.py
    body_sections) and on the three FAQ blocks. The approved board gives the frame rows (trust
    strip, takeaways, the three letters, the newsletter, the enquiry form, the contents) their
    own short labels, which are not questions, and the components render them as their H2.
  - the FAQ questions are the board's, each in the wording the question file records for the
    page (`covered_by.text`); two differ from the board's words because those collided with
    headings on other live pages (2026-10-03, check:boards header-collision).
  - the FAQ count is not hard-coded at 15-20. The expected set is read from the board's FAQ trees
    and must equal every FAQ `covered_by` text in data/queries/blue-staffy-puppies-london.json;
    each block stays inside its own 5-7 / 5-7 / 7-10 band. Since the London close proposals (answer
    board 2026-10-05 london-close-proposals q01 (a)) the board carries 19: top 5, middle 7,
    bottom 7, none of them a question another built page carries.
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


def page_wording(board_q):
    """The wording the question file records for a board question on the page (`covered_by`):
    the board's own words, or a recorded change where they collide with another live page's
    heading (scripts/pageboard.py header-collision)."""
    faq = [q for q in QUERIES["questions"] if q.get("covered_by") and q["covered_by"]["where"] == "faq"]
    hit = next((q for q in faq if norm(q["covered_by"]["text"]) == norm(board_q)), None) \
        or next((q for q in faq if norm(q["question"]) == norm(board_q)), None)
    assert hit, f"the question file covers no FAQ question {board_q!r}"
    return hit["covered_by"]["text"]


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
        want = [page_wording(q) for q in board_faq_questions(sid)]
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
    """Every bottom answer is one short paragraph. The bound was an average of 29 words while
    the block's answers were the old two-sentence set; the replacements the breeder approved
    (answer board 2026-10-05 london-close-proposals q01 (a),
    docs/reports/london-close-proposals-2026-10-05/) are written to the brief's 40-80 words, so
    the bound is now the brief's ceiling on each answer."""
    secs = labelled_sections(built())
    answers = [text(a) for a in re.findall(r"</summary>\s*<p[^>]*>(.*?)</p>", secs["faq-bottom"], re.S)]
    assert len(answers) == len(board_faq_questions("faq-bottom"))
    assert max(len(a.split()) for a in answers) <= 80


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
    # An EMBED row (the London map, answer board 2026-10-06-london-map q01-q02) is not a body
    # link: its anchor is the iframe's title, which the tap-to-load facade carries as data-title
    # beside the URL in data-src (CityMapFacade). Its <noscript> fallback link is the same href.
    embeds = {(H.unescape(h), H.unescape(t)) for h, t in
              re.findall(r'<figure\b[^>]*data-city-map[^>]*data-src="([^"]+)"[^>]*data-title="([^"]+)"', html)}
    assert len(embeds) == 1, embeds
    missing = [(l["href"], l["anchor"]) for l in listed
               if not any(h == l["href"] and a.startswith(l["anchor"]) for h, a in anchors)
               and not (l["why"].startswith("EMBED") and (l["href"], l["anchor"]) in embeds)]
    assert missing == []
    external = {h for h, _ in anchors if h.startswith("http")}
    assert external <= {l["href"] for l in listed}, sorted(external)


def test_the_map_note_keeps_both_disclosures_in_its_trimmed_wording():
    """The facade's note (CityMapFacade) was trimmed by two words on 2026-10-06 ("which sets its
    own cookies" -> "which sets cookies") to bring the delivery section back inside its 171-209
    band (the user's chat instruction, "fix the still open"; board revision 43). It is component UI
    copy, counted as the section's prose because the board gate excludes no widget text. What the
    trim must never lose: nothing is asked of Google before the tap, and the map sets cookies."""
    html = main_html(built())
    notes = re.findall(r'<p class="note" id="map-note-[^"]*"[^>]*>(.*?)</p>', html, re.S)
    assert len(notes) == 1, notes
    note = text(notes[0])
    assert "Nothing loads from Google until you tap" in note
    assert re.search(r"Google Maps, which sets cookies\.", note), note


def test_the_schema_names_london_and_carries_no_telephone():
    html = built()
    blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
    nodes = [n for b in blocks for n in (b if isinstance(b, list) else [b])]
    local = [n for n in nodes if n.get("@type") == "LocalBusiness"]
    # The layout's site-wide node (src/components/Schema.astro) and the page's own, which
    # shares its @id and adds areaServed: one business, described twice, never two.
    assert local and len({n.get("@id") for n in local}) == 1
    assert any("London" in json.dumps(n.get("areaServed")) for n in local)
    assert not [n for n in local if "telephone" in n]


def test_indexable_and_in_the_sitemap_since_the_breeder_approved_it():
    """The breeder approved the page on 2026-10-06 (docs/reference/answer-board/answers/
    final-approval-blue-staffy-puppies-london-2026-10-06.md), so `noindex, follow` came off: the
    page prints the layout default, one robots meta, and a page sitemap shard lists its URL."""
    html = built()
    robots = re.findall(r'<meta name="robots" content="([^"]*)"', html)
    assert robots == ["index, follow"], robots
    shards = [s.read_text(encoding="utf-8") for s in (ROOT / "dist").glob("*sitemap*.xml")]
    assert shards, "no sitemap shard in dist/"
    route = f"/uk-locations/{SLUG}/<"
    assert [s for s in shards if route in s], "London is in no sitemap shard"


# --------------------------------------------------------------------------- the board revision
# London's board revision (answer board 2026-10-03-london-board-revision q01-q09; the record's
# `subcomponents`, block 6b, and `board_revisions`, block 1c).

PLACES = json.loads((ROOT / "data/city-places" / f"{SLUG}.json").read_text(encoding="utf-8"))
PUPPIES = [p for p in json.loads((ROOT / "data/puppies.json").read_text(encoding="utf-8")) if p["status"] == "Available"]
RUN = json.loads((ROOT / "data/page-runs" / f"{SLUG}.json").read_text(encoding="utf-8"))


def test_the_byline_sits_under_the_h1_and_claims_no_read_the_record_lacks():
    secs = labelled_sections(built())
    hero = secs["top"]
    h1 = hero.index("</h1>")
    by = re.search(r'<div[^>]*data-byline[^>]*>(.*?)</div>', hero[h1:], re.S)
    assert by and hero.index("data-byline") < hero.index('class="lede"'), "the byline is under the H1, above the lead"
    assert text(by.group(1)).replace(" ,", ",").startswith(f"Written by {SETTINGS['breeder_name']}, breeder, {SETTINGS['address']['city']}")
    assert re.search(rf'href="/blue-staffy-uk-breeders/"[^>]*>{SETTINGS["breeder_name"]}</a>', by.group(1))
    assert ("data-byline-read" in hero) == bool(RUN.get("breeder_review")), "line 2 only with the breeder's read"
    assert "Lisa Bright, BlueStaffyUK." not in text(hero), "the lead's sign-off is dropped (q07)"


def test_the_ticket_strip_follows_the_takeaways_one_ticket_per_puppy():
    """The puppy cards, CARD-3 "the steel pass" (answer board 2026-10-04 q08 (c)): their own band
    straight after the takeaways section, not inside it; one card per available puppy, its name the
    one link to its own page, with the price, the breeder's approved line (q07 (a)), the trust
    signs and the guarantee label from data/settings.json, and the delivery band."""
    from_settings = SETTINGS["puppy_trust_signs"] + [SETTINGS["guarantee_label"]]
    sec = labelled_sections(built())["key-takeaways"]
    assert sec.index("data-takeaway") < sec.index("data-ticket-strip")
    ledger_end = sec.index("data-ticket-strip")
    assert "</section>" in sec[:ledger_end], "the strip is its own band, after the takeaways section closes"
    strip = sec[ledger_end:]
    cards = re.findall(r'<article class="pc"[^>]*data-ticket="([a-z-]+)"[^>]*>(.*?)</article>', strip, re.S)
    assert [s for s, _ in cards] == [p["slug"] for p in PUPPIES]
    for (slug, body), p in zip(cards, PUPPIES):
        links = re.findall(r'<a\b[^>]*href="([^"]+)"', body)
        assert links == [f"/available-puppies/{slug}/"], links
        words = text(body)
        assert words.startswith(p["name"]) and p["colour"] in words and f"£{p['price_gbp']:,}" in words, words
        assert p["personality"] in H.unescape(words).replace("’", "'"), words
        for sign in from_settings:
            assert sign in words, (slug, sign)
        assert f"£{SETTINGS['delivery_min_gbp']}–£{SETTINGS['delivery_max_gbp']}" in words and SETTINGS["address"]["city"] in words
    body = strip.split('class="kit-divider', 1)[0]
    assert "<img" not in body and not re.search(r"<h[1-6]", body)


def test_the_call_checklist_is_eight_native_checkboxes_under_the_h5():
    sec = labelled_sections(built())["deposit-viewing"]
    h5 = sec.index("<h5")
    ck = re.search(r'<div[^>]*data-call-checklist.*?</ul>\s*</div>\s*</div>\s*</div>', sec[h5:], re.S).group(0)
    assert ck.count('type="checkbox"') == 8 and "<script" not in ck and "<a " not in ck
    words = text(ck)
    assert f"£{SETTINGS['deposit_gbp']}, paid by bank transfer: {SETTINGS['deposit_refund_clause']}." in words
    assert SETTINGS["guarantee_label"] in words and SETTINGS["guarantee_note"] in words
    assert "L-2-HGA, HC-HSF4, eye screening and elbow screening" in words
    assert sec.index("data-call-checklist") < sec.index("<h6"), "under the H5, before the H6"


def test_the_london_places_quote_the_file_and_link_each_source_once():
    sec = labelled_sections(built())["london-life"]
    pl = sec[sec.index("data-city-places"):]
    words = text(pl)
    shown = 0
    for place in PLACES["places"]:
        for f in place["facts"]:
            if re.search(r"\bhectares?\b|\btoilets\b|^Address\b|\blicen[cs]e\b", f["value"], re.I):
                assert f["value"] not in words, f["value"]
            else:
                assert H.escape(f["value"], quote=False) in pl or f["value"] in words, f["value"]
                shown += 1
    assert shown >= 20
    hrefs = [H.unescape(h) for h in re.findall(r'<a\b[^>]*href="(https?://[^"]+)"', pl)]
    assert len(hrefs) == len(set(hrefs)) == 8 and PLACES["vets"]["source"] in hrefs


def test_the_breeders_london_answers_and_nothing_she_did_not_give():
    body = main_text(built())
    assert "Croydon, Edmonton and Ilford" in body and "handovers are by request" in body
    assert "Chadwell" not in body and "Dartford" not in body


def test_the_phone_source_serves_each_approved_phone_layout_at_its_real_size():
    """Below 640px each infographic serves its phone layout — the `img:<slot>-phone` pick the
    breeder approved at the Asset Gate (2026-10-04 q01), published byte-identical beside the box
    — at the size the manifest measured, and never the older `-760` file (kept on disk, rule 11)."""
    html = built()
    manifest = json.loads((ROOT / "data/image-manifest.json").read_text(encoding="utf-8"))
    picks = BOARD["approval"]["picks"]
    sources = re.findall(r'<source media="\(max-width: 639px\)" srcset="([^"]+)"[^>]*'
                         r'width="(\d+)" height="(\d+)"', html)
    rows = [a for a in BOARD["assets"] if a["kind"] == "infographic"]
    assert len(rows) == 6 and len(sources) == 6
    for a in rows:
        stem = a["file"][len("/images/"):-len(".webp")]
        assert f"img:{a['slot']}-phone" in picks, a["slot"]
        m = manifest[stem]
        want = (f"/images/{stem}-phone.webp {m['phone_w']}w", str(m["phone_w"]), str(m["phone_h"]))
        assert want in sources, (a["slot"], sources)
        assert (ROOT / "public/images" / f"{stem}-760.webp").exists(), "rule 11: kept on disk"
    assert "infographic-760" not in html
