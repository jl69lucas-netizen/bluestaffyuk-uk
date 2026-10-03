"""The outline provenance gate (system-gaps Task 6): a new-family page is built from its own
approved outline and from nothing else.

Every case builds a throwaway site under tmp_path — a board record for a fake location page,
data/page-map.json, data/locations.json, data/facts/rebuilt.json and a dist/ holding the
page and one sibling — and runs the gate's main() against it with --root. The clean page
passes; each defect is added to it one at a time and must fire its own check id.
"""
import copy
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import outline_provenance_check as OP  # noqa: E402

SLUG = "blue-staffy-puppies-testtown"
SIBLING = "blue-staffy-puppies-othertown"

BOARD = {
    "meta": {"slug": SLUG, "page_type": "location", "status": "approved"},
    "sections": [
        {"id": "top", "shape": "hero", "heading": "Blue Staffy Puppies In Testtown", "tree": []},
        {"id": "takeaways", "shape": "takeaways", "heading": "The Short Version",
         "tree": [{"level": 3, "heading": "Four Points", "children": []}]},
        {"id": "travel", "shape": "standard", "heading": "The Road From Carlisle To Testtown",
         "tree": [{"level": 3, "heading": "Setting Off Before Breakfast", "children": []},
                  {"level": 3, "heading": "A Stop Above Shap Summit", "children": [
                      {"level": 4, "heading": "Water Bowl In The Footwell", "children": []}]}]},
        {"id": "homes", "shape": "standard", "heading": "Terraced Streets And Small Gardens",
         "tree": [{"level": 3, "heading": "Fencing A Yard For A Terrier", "children": []}]},
        {"id": "questions", "shape": "faq", "heading": "Questions From Testtown Families",
         "tree": [{"level": 3, "heading": "deposit", "children": []}]},
    ],
}

TRAVEL = ("<section id='travel' data-section-label='Travel'>"
          "<h2>The Road from Carlisle to Testtown</h2>"
          "<p>Most handovers here start with a kettle on at five and a crate in the back seat.</p>"
          "<h3>Setting Off Before Breakfast</h3>"
          "<p>Leaving early keeps the motorway quiet and the puppy asleep for the first hour.</p>"
          "<h3>A Stop Above Shap Summit</h3>"
          "<h4>Water Bowl in the Footwell</h4>"
          "<p>A shallow bowl wedged under the seat stops spills on the steep bends.</p>"
          "</section>")
HOMES = ("<section id='homes' data-section-label='Homes'>"
         "<h2>Terraced Streets and Small Gardens</h2>"
         "<p>Plenty of owners in town have a yard rather than a lawn, and that works well.</p>"
         "<h3>Fencing a Yard for a Terrier</h3>"
         "<p>Check the gap under the gate first; a curious pup finds it within a morning.</p>"
         "</section>")
# The frame: FAQ answers and takeaway headings repeat on the sibling and are not outline.
FRAME = ("<section id='takeaways' data-section-label='Takeaways'><h2>The Short Version</h2>"
         "<h3>Four Points</h3><h3>Delivery Across the North</h3></section>"
         "<section id='questions' data-section-label='FAQ'><h2>Questions From Testtown Families</h2>"
         "<div class='kit-faq'><details><summary><h3>How Much Is the Deposit?</h3></summary>"
         "<p>The deposit is a fixed sum that holds your puppy until collection day arrives.</p>"
         "</details></div></section>")


def page(body=None, stray="", h1="Blue Staffy Puppies in Testtown"):
    body = TRAVEL + HOMES if body is None else body
    return ("<html><body><header><nav>Home</nav></header><main>"
            f"<section id='top' data-section-label='Hero'><section class='kit-hero'><h1>{h1}</h1>"
            "</section></section>" + FRAME + stray + body + "</main>"
            "<footer>Blue Staffy UK</footer></body></html>")


SIBLING_HTML = ("<html><body><main><section id='top' data-section-label='Hero'><h1>Blue Staffy "
                "Puppies in Othertown</h1></section>"
                "<section id='about' data-section-label='About'><h2>Delivery to Othertown</h2>"
                "<p>Families in Othertown often ask us about the long drive north.</p>"
                "<p>We walk every puppy along the river path at dawn.</p>"
                "<p>Our breeding programme is small, careful and built around one family home "
                "in the countryside where every puppy is handled daily.</p>"
                "<h3>Rain Gear For The School Run</h3>"
                "<p>UK home delivery by DEFRA approved transport, priced by distance: £200 to "
                "£350.</p></section>"
                "<section id='questions' data-section-label='FAQ'><h2>Questions From Othertown "
                "Families</h2><div class='kit-faq'><details><summary><h3>How Much Is the "
                "Deposit?</h3></summary><p>The deposit is a fixed sum that holds your puppy "
                "until collection day arrives.</p></details></div></section>"
                "</main></body></html>")


def site(tmp_path, html=None, board=None, rebuilt=(SLUG,)):
    root = tmp_path
    (root / "data" / "boards").mkdir(parents=True)
    (root / "data" / "facts").mkdir(parents=True)
    (root / "data" / "boards" / f"{SLUG}.json").write_text(json.dumps(board or BOARD))
    (root / "data" / "facts" / "rebuilt.json").write_text(json.dumps(list(rebuilt)))
    (root / "data" / "page-map.json").write_text(json.dumps({"pages": [
        {"url": f"/uk-locations/{SLUG}/"}, {"url": f"/uk-locations/{SIBLING}/"}]}))
    (root / "data" / "locations.json").write_text(json.dumps([
        {"slug": SLUG, "city": "Testtown"}, {"slug": SIBLING, "city": "Othertown"},
        {"slug": "uk", "city": "UK"}]))
    for slug, text in ((SLUG, page() if html is None else html), (SIBLING, SIBLING_HTML)):
        d = root / "dist" / "uk-locations" / slug
        d.mkdir(parents=True)
        (d / "index.html").write_text(text, encoding="utf-8")
    return root


def run(root, capsys, *args):
    code = OP.main([*args, "--root", str(root)])
    return code, capsys.readouterr().out


# ── the clean page, and which pages are examined ───────────────────────────────────────────
def test_a_page_built_from_its_outline_passes(tmp_path, capsys):
    code, out = run(site(tmp_path), capsys)
    assert code == 0, out
    assert f"examined 1 new-family pages: /uk-locations/{SLUG}/" in out
    assert "0 problems" in out


def test_the_frame_is_never_compared_with_the_outline_or_the_siblings(tmp_path, capsys):
    # FRAME carries an H3 the takeaways tree lacks and an FAQ answer the sibling repeats.
    code, out = run(site(tmp_path), capsys)
    assert "Delivery Across the North" not in out and "deposit is a fixed sum" not in out


def test_a_page_not_yet_in_rebuilt_json_is_awaiting_rebuild(tmp_path, capsys):
    """Counted as awaiting rebuild and not examined. The fixture's only board is approved, so
    the run examined nothing it owed a judgment and refuses (2026-10-03: London's approval
    lifted tests/py/test_gates_refuse_nothing.py's xfail; zero examined is not a pass)."""
    code, out = run(site(tmp_path, rebuilt=()), capsys)
    assert "examined 0 new-family pages" in out and "1 awaiting rebuild" in out
    assert code == 1 and "not a pass" in out


def test_a_named_slug_is_examined_before_it_is_listed(tmp_path, capsys):
    code, out = run(site(tmp_path, rebuilt=()), capsys, SLUG)
    assert code == 0 and "examined 1 new-family pages" in out


def test_a_slug_may_be_named_by_its_route_and_an_unknown_one_fails(tmp_path, capsys):
    root = site(tmp_path, rebuilt=())
    code, out = run(root, capsys, f"uk-locations/{SLUG}")
    assert code == 0 and "examined 1 new-family pages" in out
    code, out = run(root, capsys, "blue-staffy-puppies-nowhere")
    assert code == 1 and "[outline-no-board]" in out


def test_a_board_out_of_family_scope_is_never_examined(tmp_path, capsys):
    board = copy.deepcopy(BOARD)
    board["meta"]["page_type"] = "interior"
    code, out = run(site(tmp_path, board=board), capsys)
    assert code == 0 and "examined 0 new-family pages" in out and "1 boards out of family scope" in out


def test_the_real_repo_passes(capsys):
    code = OP.main([])
    out = capsys.readouterr().out
    # Only the exit code: the count changes the day project 5 lists its first page.
    assert code == 0, out


def test_a_listed_page_that_does_not_resolve_fails_once_the_site_is_built(tmp_path, capsys):
    root = site(tmp_path)
    (root / "dist" / "uk-locations" / SLUG / "index.html").unlink()
    code, out = run(root, capsys)
    # no dist/index.html: not built yet, so not an outline-not-found; but the one approved
    # board was judged by nothing, so the run is not a pass (test_gates_refuse_nothing.py)
    assert code == 1 and "1 not built" in out and "[outline-not-found]" not in out
    assert "not a pass" in out
    (root / "dist" / "index.html").write_text("<html><main><h1>Home</h1></main></html>")
    code, out = run(root, capsys)
    assert code == 1 and "[outline-not-found]" in out


def test_a_bare_key_resolves_to_its_nested_route(tmp_path):
    root = site(tmp_path)
    assert OP.resolve_page(SLUG, root) == (SLUG, f"uk-locations/{SLUG}")
    assert OP.resolve_page(f"uk-locations/{SLUG}", root) == (SLUG, f"uk-locations/{SLUG}")
    assert OP.built_path(SLUG, root) == root / "dist" / "uk-locations" / SLUG / "index.html"


# ── (a) approval ───────────────────────────────────────────────────────────────────────────
def test_an_unapproved_board_fails(tmp_path, capsys):
    board = copy.deepcopy(BOARD)
    board["meta"]["status"] = "boarded"
    code, out = run(site(tmp_path, board=board), capsys)
    assert code == 1 and "[outline-unapproved]" in out


# ── (b) the outline tree ───────────────────────────────────────────────────────────────────
def test_an_extra_heading_fails(tmp_path, capsys):
    html = page(TRAVEL + HOMES.replace("</section>", "<h3>Parks Within A Short Walk</h3></section>"))
    code, out = run(site(tmp_path, html), capsys)
    assert code == 1 and "[outline-extra]" in out and "Parks Within A Short Walk" in out


def test_a_heading_outside_every_board_section_fails(tmp_path, capsys):
    html = page(stray="<div><h2>Why Families Pick Us</h2></div>")
    code, out = run(site(tmp_path, html), capsys)
    assert code == 1 and "[outline-extra]" in out and "outside every board section" in out


def test_a_missing_heading_fails(tmp_path, capsys):
    html = page(TRAVEL + HOMES.replace("<h3>Fencing a Yard for a Terrier</h3>", ""))
    code, out = run(site(tmp_path, html), capsys)
    assert code == 1 and "[outline-missing]" in out and "Fencing A Yard For A Terrier" in out


def test_a_reordered_outline_fails(tmp_path, capsys):
    code, out = run(site(tmp_path, page(HOMES + TRAVEL)), capsys)
    assert code == 1 and "[outline-order]" in out
    assert "[outline-extra]" not in out and "[outline-missing]" not in out


def test_a_section_the_board_does_not_have_fails(tmp_path, capsys):
    extra = "<section id='parks' data-section-label='Parks'><p>Green space.</p></section>"
    code, out = run(site(tmp_path, page(TRAVEL + HOMES + extra)), capsys)
    assert code == 1 and "[outline-unknown-section]" in out and "#parks" in out


def test_out_of_order_names_the_first_heading_that_differs(tmp_path, capsys):
    code, out = run(site(tmp_path, page(HOMES + TRAVEL)), capsys)
    line = next(l for l in out.splitlines() if "[outline-order]" in l)
    assert "Terraced Streets and Small Gardens" in line
    assert "The Road From Carlisle To Testtown" in line      # what the outline has there


def test_out_of_order_past_the_shared_part_names_the_first_extra_item(tmp_path, capsys):
    # The repeat of the last H3 makes the page's list longer; the shared part agrees, so the
    # message points at the item just past it, not at the first heading on the page.
    html = page(TRAVEL + HOMES.replace("</section>", "<h3>Fencing a Yard for a Terrier</h3></section>"))
    code, out = run(site(tmp_path, html), capsys)
    line = next(l for l in out.splitlines() if "[outline-order]" in l)
    assert "Fencing a Yard for a Terrier" in line and "Road" not in line


def test_a_page_with_no_labelled_sections_is_one_problem(tmp_path, capsys):
    code, out = run(site(tmp_path, "<html><body><p>Coming soon.</p></body></html>"), capsys)
    assert code == 1
    assert out.count("[outline-no-main]") == 1 and "[outline-missing]" not in out
    assert "no <main> with <section data-section-label> blocks found" in out


def test_headings_with_inline_markup_and_entities_match_the_outline(tmp_path, capsys):
    travel = (TRAVEL.replace("<h3>Setting Off Before Breakfast</h3>",
                             "<h3>Setting Off <em>Before</em> Breakfast</h3>")
              .replace("<h3>A Stop Above Shap Summit</h3>", "<h3>A Stop Above Shap&nbsp;Summit</h3>")
              .replace("<h4>Water Bowl in the Footwell</h4>",
                       "<h4>Water Bowl in the <strong>Footwell</strong></h4>"))
    code, out = run(site(tmp_path, page(travel + HOMES)), capsys)
    assert code == 0, out


def test_a_crossover_heading_with_inline_markup_and_entities_fails(tmp_path, capsys):
    html = page(TRAVEL + HOMES.replace(
        "</section>", "<h4>Rain Gear <em>for</em> the School&nbsp;Run</h4></section>"))
    code, out = run(site(tmp_path, html), capsys)
    assert code == 1 and "[outline-heading-crossover]" in out


# ── (d) duplicates within the page ─────────────────────────────────────────────────────────
def test_a_heading_repeated_on_the_page_fails(tmp_path, capsys):
    html = page(TRAVEL + HOMES.replace("</section>", "<h4>Terraced Streets and Small Gardens</h4></section>"))
    code, out = run(site(tmp_path, html), capsys)
    assert code == 1 and "[outline-duplicate-heading]" in out


# ── (c)/(d) crossovers with another built page ─────────────────────────────────────────────
def test_a_heading_shared_with_a_sibling_fails(tmp_path, capsys):
    html = page(TRAVEL + HOMES.replace("</section>", "<h4>Rain Gear for the School Run</h4></section>"))
    code, out = run(site(tmp_path, html), capsys)
    assert code == 1 and "[outline-heading-crossover]" in out and SIBLING in out


def test_an_h2_that_is_a_sibling_h2_with_the_city_swapped_fails(tmp_path, capsys):
    board = copy.deepcopy(BOARD)
    board["sections"][3]["heading"] = "Delivery To Testtown"
    html = page(TRAVEL + HOMES.replace("Terraced Streets and Small Gardens", "Delivery to Testtown"))
    code, out = run(site(tmp_path, html, board=board), capsys)
    assert code == 1 and "[outline-heading-crossover]" in out and "template" in out


def test_a_passage_shared_with_a_sibling_fails(tmp_path, capsys):
    para = ("<p>Our breeding programme is small, careful and built around one family home in "
            "the countryside where every puppy is handled daily.</p>")
    code, out = run(site(tmp_path, page(TRAVEL + HOMES.replace("</section>", para + "</section>"))), capsys)
    assert code == 1 and "[outline-copy-crossover]" in out


def test_a_sentence_shared_with_a_sibling_fails(tmp_path, capsys):
    para = "<p>We walk every puppy along the river path at dawn.</p>"
    code, out = run(site(tmp_path, page(TRAVEL + HOMES.replace("</section>", para + "</section>"))), capsys)
    assert code == 1 and "[outline-sentence-crossover]" in out
    assert "[outline-copy-crossover]" not in out   # ten words: below the shingle floor


def test_a_sibling_sentence_with_the_city_swapped_fails(tmp_path, capsys):
    para = "<p>Families in Testtown often ask us about the long drive north.</p>"
    code, out = run(site(tmp_path, page(TRAVEL + HOMES.replace("</section>", para + "</section>"))), capsys)
    assert code == 1 and "[outline-sentence-crossover]" in out and "city swap" in out


def _hyphen_site(tmp_path, sibling_h2):
    """The test site with real city names: this page is Newcastle-under-Lyme's, the sibling
    carries `sibling_h2`."""
    board = copy.deepcopy(BOARD)
    board["sections"][3]["heading"] = "Delivery To Newcastle-under-Lyme"
    html = page(TRAVEL + HOMES.replace("Terraced Streets and Small Gardens",
                                       "Delivery to Newcastle-under-Lyme"))
    root = site(tmp_path, html, board=board)
    (root / "data" / "locations.json").write_text(json.dumps([
        {"slug": SLUG, "city": "Newcastle-under-Lyme"}, {"slug": SIBLING, "city": "Leeds"},
        {"slug": "blue-staffy-puppies-hull", "city": "Hull"}]))
    sib = root / "dist" / "uk-locations" / SIBLING / "index.html"
    sib.write_text(SIBLING_HTML.replace("Delivery to Othertown", sibling_h2), encoding="utf-8")
    return root


def test_a_hyphenated_city_swapped_heading_fails(tmp_path, capsys):
    code, out = run(_hyphen_site(tmp_path, "Delivery to Leeds"), capsys)
    assert code == 1 and "[outline-heading-crossover]" in out and "template" in out


def test_the_city_pattern_takes_either_separator_and_whole_words_only(tmp_path):
    root = _hyphen_site(tmp_path, "Delivery to Leeds")
    cities = OP.city_pattern(root)
    assert OP.templated("delivery to newcastle-under-lyme", cities) == "delivery to {city}"
    assert OP.templated("delivery to newcastle under lyme", cities) == "delivery to {city}"
    assert OP.templated("delivery to hull", cities) == "delivery to {city}"
    assert OP.templated("a hullabaloo in leedsway", cities) == "a hullabaloo in leedsway"


def test_a_sentence_shared_with_five_pages_is_one_problem_line(tmp_path, capsys):
    root = site(tmp_path)
    para = "<p>We walk every puppy along the river path at dawn.</p>"
    (root / "dist" / "uk-locations" / SLUG / "index.html").write_text(
        page(TRAVEL + HOMES.replace("</section>", para + "</section>")), encoding="utf-8")
    for i in range(4):
        d = root / "dist" / f"extra-{i}"
        d.mkdir(parents=True)
        (d / "index.html").write_text(SIBLING_HTML, encoding="utf-8")
    code, out = run(root, capsys)
    lines = [l for l in out.splitlines() if "[outline-sentence-crossover]" in l]
    assert code == 1 and len(lines) == 1, out
    assert "(+3 more)" in lines[0]


def test_a_sentence_inside_a_reported_passage_is_not_reported_again(tmp_path, capsys):
    para = ("<p>Our breeding programme is small, careful and built around one family home in "
            "the countryside where every puppy is handled daily.</p>")
    code, out = run(site(tmp_path, page(TRAVEL + HOMES.replace("</section>", para + "</section>"))), capsys)
    assert out.count("[outline-copy-crossover]") == 1
    assert "[outline-sentence-crossover]" not in out


def test_a_whitelisted_line_shared_with_a_sibling_passes(tmp_path, capsys):
    para = "<p>UK home delivery by DEFRA approved transport, priced by distance: £200 to £350.</p>"
    code, out = run(site(tmp_path, page(TRAVEL + HOMES.replace("</section>", para + "</section>"))), capsys)
    assert code == 0, out


# ── wiring ─────────────────────────────────────────────────────────────────────────────────
def test_check_all_runs_the_gate():
    scripts = json.loads((ROOT / "package.json").read_text())["scripts"]
    assert scripts["check:outline"] == "python3 scripts/outline_provenance_check.py"
    chain = scripts["check:all"]
    assert "npm run check:verbatim && npm run check:outline && " in chain


def test_the_rule_is_written_and_indexed():
    text = (ROOT / "rules" / "copy.md").read_text(encoding="utf-8")
    assert "id: outline-provenance-gate\nenforced: test\n" in text
    rows = {r["id"]: r for r in json.loads(
        (ROOT / "data" / "quality" / "rule-index.json").read_text())["rules"]}
    row = rows["outline-provenance-gate"]
    assert row["enforced"] == "test" and row["pack"] == "rules/copy.md"
    assert (ROOT / row["test"]).is_file()
    # The method rule stays judgment: the gate checks what the method leaves behind.
    assert rows["write-from-outline-never-from-sibling"]["enforced"] == "judgment"


@pytest.mark.parametrize("skill", ["bsuk-location-page-builder", "bsuk-comparison-page-builder",
                                   "bsuk-blog-post"])
def test_each_builder_skill_names_the_gate(skill):
    text = (ROOT / ".claude" / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    block = text.split("## Build from the approved outline (system-gaps)", 1)
    assert len(block) == 2, f"{skill}: the system-gaps block is missing"
    assert "scripts/outline_provenance_check.py" in block[1]
    assert "outline-provenance-gate" in block[1]


# ── the board-time half (Task 6b): family_rules refuses an outline that repeats a heading ──
import family_rules as FR  # noqa: E402


def _demo_location():
    b = json.loads((ROOT / "data" / "boards" / "_demo.json").read_text())
    b["meta"]["slug"] = SLUG
    b["meta"]["page_type"] = "location"
    return b


def _repeat(board):
    return [f for f in FR.findings(board, {"entities": []}) if f[0] == "outline-heading-repeat"]


def test_an_outline_without_a_repeated_heading_passes():
    assert _repeat(_demo_location()) == []


def test_an_outline_that_repeats_a_heading_fails():
    b = _demo_location()
    body = next(s for s in b["sections"] if s["tree"] and s["shape"] != "faq")
    body["tree"].append({"level": 3, "heading": body["heading"].upper(), "intent": "", "children": []})
    hits = _repeat(b)
    assert len(hits) == 1 and hits[0][1] == "FAIL"


def test_a_hero_heading_equal_to_the_h1_is_one_heading():
    # The build renders such a hero's H1 alone (the blog hub, contact and thank-you pages).
    b = _demo_location()
    h1 = b["h1"]["variants"][b["h1"]["pick"] if b["h1"].get("pick") is not None else b["h1"]["recommended"]]
    next(s for s in b["sections"] if s["shape"] == "hero")["heading"] = h1
    assert _repeat(b) == []


def test_the_faq_tree_is_row_ids_not_headings():
    b = _demo_location()
    faq = next(s for s in b["sections"] if s["shape"] == "faq")
    faq["tree"].append(dict(faq["tree"][0]))
    assert _repeat(b) == []


def test_no_built_record_trips_the_board_check():
    import glob
    for f in glob.glob(str(ROOT / "data" / "boards" / "*.json")):
        assert list(FR.outline_heading_repeat(json.loads(pathlib.Path(f).read_text()), None)) == [], f


def _section(board, sid):
    return next(s for s in board["sections"] if s["id"] == sid)


def test_an_h2_and_an_h3_differing_by_apostrophe_and_question_mark_fail_naming_both_sections():
    b = _demo_location()
    _section(b, "at-a-glance")["heading"] = "Why we don't rush the litter"
    _section(b, "how-we-raise")["tree"][0]["heading"] = "Why We Don’t Rush the Litter?"
    hits = _repeat(b)
    assert len(hits) == 1 and hits[0][1] == "FAIL"
    assert "section 'at-a-glance' H2" in hits[0][2] and "section 'how-we-raise' H3" in hits[0][2]


def test_two_sections_with_the_same_h2_fail_naming_both():
    b = _demo_location()
    _section(b, "owners")["heading"] = _section(b, "at-a-glance")["heading"]
    hits = _repeat(b)
    assert len(hits) == 1 and hits[0][1] == "FAIL"
    assert "section 'at-a-glance'" in hits[0][2] and "section 'owners'" in hits[0][2]


def test_a_non_hero_h2_equal_to_the_h1_fails():
    b = _demo_location()
    _section(b, "owners")["heading"] = b["h1"]["variants"][b["h1"]["recommended"]]
    hits = _repeat(b)
    assert len(hits) == 1 and hits[0][1] == "FAIL"
    assert "H1 " in hits[0][2] and "section 'owners' H2" in hits[0][2]


def test_pound_signs_and_accents_are_part_of_the_heading():
    b = _demo_location()
    _section(b, "at-a-glance")["heading"] = "A £500 Deposit"
    _section(b, "owners")["heading"] = "A 500 Deposit"
    _section(b, "how-we-raise")["tree"][0]["heading"] = "The Café Visit"
    _section(b, "how-we-raise")["tree"][1]["heading"] = "The Caf Visit"
    assert _repeat(b) == []
    assert FR._heading_key("Our Café Mornings") == "our café mornings"


def test_a_node_with_no_level_prints_h_question_mark():
    b = _demo_location()
    node = _section(b, "how-we-raise")["tree"][0]
    node.pop("level", None)
    node["heading"] = _section(b, "at-a-glance")["heading"]
    hits = _repeat(b)
    assert len(hits) == 1 and "section 'how-we-raise' H? " in hits[0][2] and "HNone" not in hits[0][2]
