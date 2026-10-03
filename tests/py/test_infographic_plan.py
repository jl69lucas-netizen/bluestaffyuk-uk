"""Block 7c: which sections need an infographic, which IG type, three styles each."""
import json
import re

import pytest
import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import infographic_plan as IP

SECS = [{"id": "delivery", "heading": "How Will My Puppy Get From Carlisle to London?", "tree": []},
        {"id": "litter-prices", "heading": "What Do They Cost?", "tree": []},
        {"id": "london-life", "heading": "Will a Blue Staffy Be Happy Living in London?", "tree": []}]
BOARD = {"meta": {"slug": "blue-staffy-puppies-london"}, "sections": SECS, "assets": []}


def _data(tmp_path, settings=None, matrix=None, puppies=None, locations=None):
    d = tmp_path / "data"
    d.mkdir()
    (d / "settings.json").write_text(json.dumps(settings if settings is not None else {
        "address": {"city": "Testford"}, "deposit_gbp": 321, "delivery_min_gbp": 111,
        "delivery_max_gbp": 222, "delivery_note": "by test van",
        "deposit_refund_clause": "some back if you ask nicely",
        "guarantee_label": "Test guarantee"}))
    (d / "price-matrix.json").write_text(json.dumps(matrix if matrix is not None else {
        "male_gbp": 1234, "female_gbp": 1357}))
    (d / "puppies.json").write_text(json.dumps(puppies if puppies is not None else [
        {"name": "Aa", "sex": "male", "price_gbp": 1234, "status": "Available"},
        {"name": "Bb", "sex": "female", "price_gbp": 1357, "status": "Available"}]))
    (d / "locations.json").write_text(json.dumps(locations if locations is not None else [
        {"slug": "blue-staffy-puppies-london", "city": "Londinium"}]))
    return tmp_path


def test_triggers_are_pinned():
    assert [ig for ig, _ in IP.TRIGGERS] == ["IG-5", "IG-1", "IG-3", "IG-2", "IG-4"]
    pats = dict(IP.TRIGGERS)
    assert re.search(pats["IG-5"], "from carlisle") and re.search(pats["IG-5"], "travel")
    assert re.search(pats["IG-1"], "how much") and re.search(pats["IG-1"], "£")
    assert re.search(pats["IG-3"], "pit bulls or american staffies")
    assert not re.search(pats["IG-3"], "aggressive, or just very attached")
    assert re.search(pats["IG-2"], "how to") and re.search(pats["IG-2"], "timeline")
    assert re.search(pats["IG-4"], "paperwork") and re.search(pats["IG-4"], "health tested")


def test_triggers_pick_ig_type():
    got = {p["section"]: p["ig"] for p in IP.plan(BOARD, root=None)}
    assert got == {"delivery": "IG-5", "litter-prices": "IG-1"}


def test_trigger_order_delivery_mentioning_cost_is_a_route():
    sec = {"id": "x", "heading": "What Does Delivery Cost?", "tree": []}
    assert IP.plan({"sections": [sec], "assets": []}, root=None)[0]["ig"] == "IG-5"


def test_h3_in_tree_triggers():
    sec = {"id": "x", "heading": "About Our Litter", "tree": [
        {"level": 3, "heading": "How Much Is Each Puppy?", "children": []}]}
    p = IP.plan({"sections": [sec], "assets": []}, root=None)[0]
    assert p["ig"] == "IG-1" and p["node"] == "How Much Is Each Puppy?"


def test_frame_and_faq_sections_are_skipped():
    frames = [
        {"id": "top", "shape": "hero", "heading": "Delivery From Carlisle", "tree": []},
        {"id": "counter", "shape": "stats", "heading": "Prices and Costs", "tree": []},
        {"id": "trust", "shape": "trust", "heading": "Health tested", "tree": []},
        {"id": "contents", "shape": "dial", "heading": "Cost and delivery", "tree": []},
        {"id": "key-takeaways", "shape": "takeaways", "heading": "Cost", "tree": []},
        {"id": "faq-top", "shape": "faq", "heading": "How much?", "tree": []},
        {"id": "review-top", "shape": "reviews", "heading": "Delivered to London", "tree": []},
        {"id": "newsletter", "shape": "standard", "heading": "Price alerts", "tree": []},
        {"id": "enquiry", "shape": "form", "heading": "Ask about delivery", "tree": []},
    ]
    assert IP.plan({"sections": frames, "assets": []}, root=None) == []


def test_existing_slot_kept_via_section_key():
    assets = [{"slot": "deposit-steps", "kind": "infographic", "infographic_style": "IG-2",
               "section": "deposit-viewing"}]
    plan = IP.plan({"sections": [{"id": "deposit-viewing", "heading": "Delivery and cost",
                                  "tree": []}], "assets": assets}, root=None)
    assert plan[0]["slot"] == "deposit-steps" and plan[0]["ig"] == "IG-2"


def test_existing_slot_kept_via_tree_image():
    sec = {"id": "deposit-viewing", "heading": "Do I Pay Before Delivery?", "tree": [
        {"level": 3, "heading": "What Does the Deposit Do?", "children": [],
         "images": [{"slot": "deposit-steps", "kind": "infographic", "infographic_style": "IG-2",
                     "prompt": "IG-2 — video call → deposit → viewing → collection or delivery"}]}]}
    plan = IP.plan({"sections": [sec], "assets": [
        {"slot": "deposit-steps", "kind": "infographic", "alt": "Four steps"}]}, root=None)
    assert len(plan) == 1
    p = plan[0]
    assert (p["slot"], p["ig"], p["node"]) == ("deposit-steps", "IG-2", "What Does the Deposit Do?")
    assert p["alt"] == "Four steps"


def test_styles_are_pinned():
    # breeder q08, 2026-10-02: "nice, playful, cartoonish" — plate / ruled / card retired.
    assert [s["id"] for s in IP.STYLES] == ["sticker", "chalk", "comic"]
    assert set(IP.STYLE_CSS) == {"sticker", "chalk", "comic"}


def test_three_styles_each():
    for p in IP.plan(BOARD, root=None):
        assert [s["id"] for s in p["styles"]] == ["sticker", "chalk", "comic"]


def test_london_board_plans_the_deposit_slot_and_a_route():
    board = json.loads((IP.ROOT / "data/boards/blue-staffy-puppies-london.json").read_text())
    got = {p["section"]: (p["slot"], p["ig"]) for p in IP.plan(board)}
    assert got["deposit-viewing"] == ("deposit-steps", "IG-2")
    assert got["delivery"][1] == "IG-5"
    assert not {"temperament", "london-life", "everyday-health"} & set(got)


def _render_all(p, root):
    facts = IP.facts_for(p, root)
    tokens = IP.load_tokens(IP.ROOT)
    return {s["id"]: IP.render_preview(p, s["id"], facts, tokens) for s in p["styles"]}


def test_facts_come_only_from_data(tmp_path):
    root = _data(tmp_path)
    plan = {p["section"]: p for p in IP.plan(BOARD, root=root)}
    for sid, html in _render_all(plan["litter-prices"], root).items():
        assert "£1,234" in html and "£1,357" in html and "£321" in html, sid
        assert "£1,500" not in html and "£1,700" not in html and "£500" not in html, sid
    for sid, html in _render_all(plan["delivery"], root).items():
        assert "£111" in html and "£222" in html and "Testford" in html and "Londinium" in html
        assert "£200" not in html and "£350" not in html and "Carlisle</" not in html


def test_not_fetched_is_rendered_when_a_fact_is_missing(tmp_path):
    root = _data(tmp_path, settings={"address": {"city": "Testford"}})
    p = [p for p in IP.plan(BOARD, root=root) if p["section"] == "delivery"][0]
    assert any(str(v).startswith("NOT FETCHED") for v in json.dumps(p["facts"]).split('"'))
    for html in _render_all(p, root).values():
        assert "NOT FETCHED — data/settings.json delivery_min_gbp missing" in html
        assert 'class="nf"' in html


def test_deposit_is_never_plainly_refundable(tmp_path):
    root = _data(tmp_path)
    sec = {"id": "deposit-viewing", "heading": "Deposit", "tree": [
        {"level": 3, "heading": "What Does the Deposit Do?", "children": [],
         "images": [{"slot": "deposit-steps", "kind": "infographic", "infographic_style": "IG-2",
                     "prompt": "IG-2 — video call → deposit → viewing → collection or delivery"}]}]}
    p = IP.plan({"meta": {"slug": "blue-staffy-puppies-london"}, "sections": [sec], "assets": []},
                root=root)[0]
    assert [s["title"] for s in p["facts"]["steps"]] == [
        "Video call", "Deposit", "Viewing", "Collection or delivery"]
    for html in _render_all(p, root).values():
        assert "£321" in html and "some back if you ask nicely" in html
        assert not re.search(r"(?<!% )\brefundable\b", html.replace("some back", ""))


def test_preview_has_aria_label_and_no_external_script():
    for p in IP.plan(BOARD):
        for sid, html in _render_all(p, IP.ROOT).items():
            assert html.startswith("<!doctype html>")
            assert 'role="img"' in html and f'aria-label="{IP.esc(p["alt"])}"' in html
            assert "<script" not in html.lower()          # no script at all, inline or not
            assert not re.search(r"\son[a-z]+=", html)      # and no inline handler
            assert not re.search(r'(src|href)="https?://', html)
            assert ":root{" in html and "--color-steel-700" in html


def test_block_markdown_lists_slots_and_previews():
    md = IP.block(BOARD)
    assert "| Section | Heading | IG type | Why it is here |" in md
    assert "| delivery |" in md and "IG-5" in md
    for style in ("sticker", "chalk", "comic"):
        assert f"docs/artifacts/boards/ig/blue-staffy-puppies-london/delivery-route-{style}.html" in md
    assert "pick-ig:delivery-route" in md


def test_breed_split_subjects_on_the_real_london_heading():
    board = json.loads((IP.ROOT / "data/boards/blue-staffy-puppies-london.json").read_text())
    p = [p for p in IP.plan(board) if p["section"] == "breed"][0]
    assert p["facts"]["subjects"] == ["English Staffy", "American Staffy"]
    assert p["alt"] == "English Staffy compared with American Staffy"


BREED_SEC = {"id": "breed", "heading": "Are Blue Staffies Pit Bulls or American Staffies?",
             "tree": [{"level": 3, "heading": "How Can I Tell an English Staffy From an American One?",
                       "children": []}]}


def _sourced(value, src="https://www.royalkennelclub.com/x"):
    return {"value": value, "quote": value, "source": src, "fetched": "2026-10-03"}


def _breeds(tmp_path, standards):
    root = _data(tmp_path)
    if standards is not None:
        (root / "data" / "breed-standards.json").write_text(json.dumps(standards))
    board = {"meta": {"slug": "blue-staffy-puppies-london"}, "sections": [BREED_SEC], "assets": []}
    # The tmp root holds no board file, so hand facts_for the section (and its H3) directly.
    return root, {**IP.plan(board, root=root)[0], "_sec": BREED_SEC}


TEST_STANDARDS = {"fetched": "2026-10-03", "breeds": {
    "staffordshire-bull-terrier": {
        "height": _sourced("31–37 cm"), "weight": _sourced("9–12 kg"),
        "colours": _sourced("Teal or mauve"), "uk_legal_status": _sourced("Fine everywhere")},
    "american-staffordshire-terrier": {
        "height": _sourced("51 in", "https://images.akc.org/x"),
        "weight": {"value": "NOT FETCHED — the test standard gives no weight figure"},
        "colours": _sourced("Plaid", "https://images.akc.org/x"),
        "uk_legal_status": _sourced("Fine here too", "https://www.gov.uk/x")}},
    "comparison_verdict": {"value": "Two test breeds.", "clauses": [
        {"text": "Two test breeds.", "source": "https://www.gov.uk/x"}]}}


def test_breed_split_facts_come_from_the_breed_standards_file(tmp_path):
    root, p = _breeds(tmp_path, TEST_STANDARDS)
    f = IP.facts_for(p, root)
    assert [r["attr"] for r in f["rows"]] == ["Height", "Coat colours", "UK law"]
    assert f["rows"][0] == {"attr": "Height", "a": "31–37 cm", "b": "51 in"}
    assert f["verdict"] == "Two test breeds."
    assert f["credit"] == ("Source: Royal Kennel Club / AKC / GOV.UK — figures as each "
                           "standard states them")
    for html in _render_all(p, root).values():
        assert "31–37 cm" in html and "Plaid" in html and "Source: Royal Kennel Club" in html
        # Weight is NOT FETCHED for one subject, so the row is left out, never half-shown.
        assert "9–12 kg" not in html and "NOT FETCHED" not in html


def _figure_text(html):
    fig = html[html.index("<figure"):html.index("</figure>")]
    import html as _html
    return _html.unescape(re.sub(r"<[^>]+>", " ", fig))   # an entity's digits are not content


def test_no_number_or_pound_amount_outside_the_file_renders(tmp_path):
    root, p = _breeds(tmp_path, TEST_STANDARDS)
    allowed = set(re.findall(r"\d+(?:\.\d+)?", json.dumps(TEST_STANDARDS, ensure_ascii=False)))
    for sid, html in _render_all(p, root).items():
        text = _figure_text(html)
        assert "£" not in text, sid
        for n in re.findall(r"\d+(?:\.\d+)?", text):
            assert n in allowed, (sid, n)
    # And on the real London board, against the real file.
    board = json.loads((IP.ROOT / "data/boards/blue-staffy-puppies-london.json").read_text())
    real = [q for q in IP.plan(board) if q["slot"] == "breed-split"][0]
    data = (IP.ROOT / "data/breed-standards.json").read_text()
    allowed = set(re.findall(r"\d+(?:\.\d+)?", data))
    for sid, html in _render_all(real, IP.ROOT).items():
        text = _figure_text(html)
        assert "£" not in text and "NOT FETCHED" not in text, sid
        assert ("Source: Royal Kennel Club / AKC / GOV.UK — figures as each standard "
                "states them") in text, sid
        for n in re.findall(r"\d+(?:\.\d+)?", text):
            assert n in allowed, (sid, n)


@pytest.mark.parametrize("subject,key", [
    ("English Staffy", "staffordshire-bull-terrier"),
    ("Staffordshire Bull Terriers", "staffordshire-bull-terrier"),
    ("American Staffy", "american-staffordshire-terrier"),
    ("American Staffies", "american-staffordshire-terrier"),
    ("Pit Bulls", "american-pit-bull-terrier"),
    ("American Bully", None), ("French Bulldog", None), ("Boxer", None)])
def test_breed_key_names_only_the_three_breeds(subject, key):
    assert IP._breed_key(subject) == key


def test_an_unknown_subject_renders_not_fetched_never_staffy_data(tmp_path):
    sec = {**BREED_SEC, "heading": "Is a Blue Staffy a Boxer or a Bully?",
           "tree": [{"level": 3, "heading": "English Staffy vs French Bulldog?", "children": []}]}
    root, p = _breeds(tmp_path, TEST_STANDARDS)
    p = {**p, "_sec": sec}
    f = IP.facts_for(p, root)
    assert f["subjects"][1] == "French Bulldog"
    assert f["rows"][0]["b"].startswith("NOT FETCHED")
    for html in _render_all(p, root).values():
        assert "31–37 cm" not in html and "Teal or mauve" not in html
        assert ("NOT FETCHED — data/breed-standards.json breed for 'French Bulldog'"
                in _figure_text(html))


def test_breed_split_without_the_file_renders_not_fetched(tmp_path):
    root, p = _breeds(tmp_path, None)
    for html in _render_all(p, root).values():
        assert "NOT FETCHED — data/breed-standards.json breeds missing" in html
        assert 'class="nf"' in html


def test_an_unsourced_field_never_renders(tmp_path):
    std = json.loads(json.dumps(TEST_STANDARDS))
    std["breeds"]["staffordshire-bull-terrier"]["colours"] = {"value": "Unsourced colour"}
    root, p = _breeds(tmp_path, std)
    for html in _render_all(p, root).values():
        assert "Unsourced colour" not in html


def test_unknown_existing_style_is_rematched_or_refused():
    img = {"slot": "x-ig", "kind": "infographic", "infographic_style": "IG-9"}
    sec = {"id": "s", "heading": "What Does Delivery Cost?", "tree": [], "images": [img]}
    p = IP.plan({"sections": [sec], "assets": []}, root=None)[0]
    assert (p["slot"], p["ig"]) == ("x-ig", "IG-5")
    bare = {"id": "s", "heading": "Will a Staffy Be Happy?", "tree": [],
            "images": [{"slot": "x-ig", "kind": "infographic"}]}
    import pytest
    with pytest.raises(ValueError, match="x-ig"):
        IP.plan({"sections": [bare], "assets": []}, root=None)


def test_checklist_alt_is_capped():
    checks = [{"text": f"Check number {i} with some words?", "icon": "check"} for i in range(10)]
    alt = IP._alt({"ig": "IG-4", "facts": {"checks": checks}})
    assert alt.endswith("; and 4 more") and len(alt) < 300


def test_block_escapes_pipes():
    sec = {"id": "x", "heading": "Cost | Price?", "tree": []}
    md = IP.block({"meta": {"slug": "s"}, "sections": [sec], "assets": []}, root=None)
    assert "Cost \\| Price?" in md


# ── breeder q08 (2026-10-02): each infographic gets its own H3 ─────────────────────────────
LONDON_IG = {"deposit-viewing": "deposit-steps", "delivery": "delivery-route",
             "litter-prices": "litter-prices-figures", "health-tests": "health-tests-checklist",
             "paperwork": "paperwork-checklist", "breed": "breed-split"}


def _london():
    return json.loads((IP.ROOT / "data/boards/blue-staffy-puppies-london.json").read_text())


def test_london_keeps_all_six_slots_each_on_its_own_h3():
    board = _london()
    plan = {p["section"]: p for p in IP.plan(board)}
    assert {s: p["slot"] for s, p in plan.items()} == LONDON_IG
    changes = {c["section"]: c for c in board["outline_changes_since_stop2"]}
    for sid, p in plan.items():
        assert p["node_level"] == "H3" and p["node_path"].startswith("tree["), p
        assert p["node"] == changes[sid]["heading"] and p["node_path"] == changes[sid]["node"]
        assert p["node"] != p["heading"]                       # not the H2
        assert "q08" in p["why"]


def test_an_infographic_h3_carries_only_its_infographic():
    board = _london()
    for s in board["sections"]:
        for n in s["tree"]:
            if IP._is_ig_node(n):
                assert [i["kind"] for i in n["images"]] == ["infographic"], n["heading"]
                assert n["words"] == {"min": 40, "max": 60}


def test_a_checklist_never_lists_its_own_heading():
    board = _london()
    for p in IP.plan(board):
        if p["ig"] == "IG-4":
            texts = [c["text"] for c in p["facts"]["checks"]]
            assert p["node"] not in texts and texts, p["slot"]


def test_an_infographic_h3_is_not_a_subject_or_trigger():
    sec = {"id": "x", "heading": "About Our Litter", "tree": [
        {"level": 3, "heading": "How Can I Tell an English Staffy From an American One?", "children": []},
        {"level": 3, "heading": "Labrador or Poodle Figures Side by Side?", "children": [],
         "images": [{"slot": "x-split", "kind": "infographic", "infographic_style": "IG-3",
                     "prompt": ""}]}]}
    assert IP._h2_h3(sec) == ["About Our Litter",
                              "How Can I Tell an English Staffy From an American One?"]
    p = IP.plan({"sections": [sec], "assets": []}, root=None)[0]
    assert p["slot"] == "x-split" and p["node"] == "Labrador or Poodle Figures Side by Side?"


# ── playful styles (breeder q08, 2026-10-02) ──────────────────────────────────────────────

def _london_previews():
    board = json.loads((IP.ROOT / "data/boards/blue-staffy-puppies-london.json").read_text())
    tokens = IP.load_tokens(IP.ROOT)
    for p in IP.plan(board):
        for s in IP.STYLES:
            yield p, s["id"], IP.render_preview(p, s["id"], p["facts"], tokens)


def test_every_style_draws_the_doodle_dog_inline():
    assert 'aria-hidden="true"' in IP.DOG and "collar" not in IP.DOG.lower()
    for p, sid, html in _london_previews():
        assert '<svg class="dog"' in html, (p["slot"], sid)
        # the dog is decoration inside the caption: the caption text is still the title
        assert f'<span class="cap-t">{IP.t(p["facts"]["title"])}</span>' in html


def test_previews_use_the_site_palette_only():
    """No colour outside the tokens: below the inlined :root, no hex, rgb() or hsl()
    literal — the drawn SVG decorations are stroked in the token steel itself."""
    tokens = IP.load_tokens(IP.ROOT)
    steel = tokens["--color-steel-700"].replace("#", "%23")
    for p, sid, html in _london_previews():
        css = html.split("<style>", 1)[1].split("</style>", 1)[0]
        rest = css[css.index(":root{"):]
        rest = rest[rest.index("}") + 1:]
        assert not re.search(r"#[0-9a-fA-F]{3,8}\b", rest), (p["slot"], sid)
        assert not re.search(r"\b(rgba?|hsla?)\(", rest), (p["slot"], sid)
        for enc in re.findall(r"%23[0-9a-fA-F]{6}", rest):
            assert enc == steel, (p["slot"], sid, enc)
        assert "STEELHEX" not in html


def test_no_text_below_14px():
    """Readable at 375: every font size the previews set is at least 14px, and the 13px
    --text-xs token is never used for text."""
    for sid in IP.STYLES:
        css = IP.BASE_CSS + IP.STYLE_CSS[sid["id"]]
        assert "var(--text-xs)" not in css, sid
        for px in re.findall(r"font-size:\s*(\d+(?:\.\d+)?)px", css):
            assert float(px) >= 14, (sid, px)


def test_chalk_wobble_is_on_lines_never_on_text():
    css = IP.STYLE_CSS["chalk"]
    rules = re.findall(r"([^{}]+)\{[^}]*filter:url\(#wob\)", css)
    assert len(rules) >= 3                               # the outlines, the numbers, the dog
    for rule in rules:
        sels = [x.strip() for x in rule.split(",")]
        assert all("::before" in x or x in (".k", ".cap .dog") for x in sels), sels
    for p, sid, html in _london_previews():
        assert ('id="wob"' in html) == (sid == "chalk")


def test_route_stacks_vertically_at_375():
    """IG-5 at phone width is one column: the base rule and no style overriding it."""
    assert re.search(r"@media \(max-width:767px\)\{[^@]*\.route\{grid-template-columns:1fr", IP.BASE_CSS)
    for sid, css in IP.STYLE_CSS.items():
        mobile = css.split("@media (max-width:767px)", 1)[-1]
        assert ".route{grid-template-columns" not in mobile, sid


# ── measured frame heights (the v2 "Card" clipping fix) ─────────────────────────────────────

LONDON = "blue-staffy-puppies-london"


def test_heights_json_covers_every_slot_style_and_width():
    board = json.loads((IP.ROOT / f"data/boards/{LONDON}.json").read_text())
    stored = json.loads((IP.ROOT / IP.heights_path(LONDON)).read_text())
    assert stored["widths"] == list(IP.PREVIEW_WIDTHS)
    h = stored["heights"]
    for p in IP.plan(board):
        for s in IP.STYLES:
            for w in IP.PREVIEW_WIDTHS:
                v = h[p["slot"]][s["id"]][str(w)]
                assert isinstance(v, int) and v > 100, (p["slot"], s["id"], w)
    assert IP.load_heights(LONDON) == h
    assert IP.load_heights("no-such-page") == {}


needs_browser = pytest.mark.skipif(not IP.browser_available(),
                                   reason="node or Playwright's Chromium is unavailable")


@needs_browser
def test_stored_heights_match_a_fresh_measurement(tmp_path):
    """Re-measure every London preview in Chromium (fonts served) into a scratch root and
    hold heights.json to it: a preview edited without re-measuring fails here, because its
    board frame could now be shorter than its document."""
    import shutil
    board = json.loads((IP.ROOT / f"data/boards/{LONDON}.json").read_text())
    ig = tmp_path / IP.OUT_DIR / LONDON
    ig.parent.mkdir(parents=True)
    shutil.copytree(IP.ROOT / IP.OUT_DIR / LONDON, ig)
    (tmp_path / "public").mkdir()
    shutil.copytree(IP.ROOT / "public/fonts", tmp_path / "public/fonts")
    shutil.copytree(IP.ROOT / "data", tmp_path / "data")
    shutil.copytree(IP.ROOT / "src/styles", tmp_path / "src/styles")
    fresh = IP.measure_heights(board, root=tmp_path)["heights"]
    stored = IP.load_heights(LONDON)
    for slot, styles in fresh.items():
        for style, per in styles.items():
            for w, h in per.items():
                assert stored[slot][style][w] >= h, (slot, style, w, stored[slot][style][w], h)
                assert stored[slot][style][w] - h <= 2, (slot, style, w, "stale: re-measure")


@needs_browser
def test_bake_infographic_writes_the_two_webps(tmp_path):
    """A tiny fixture preview baked to the asset row size and the 760 sibling."""
    from PIL import Image
    slug, slot, style = "fx", "tiny-steps", "sticker"
    p = {"slot": slot, "ig": "IG-2", "page": slug, "node": "Tiny", "heading": "Tiny",
         "alt": "Two steps: one, then two"}
    facts = {"title": "Tiny", "steps": [
        {"n": "01", "title": "One", "value": "£1", "note": "first", "icon": "check"},
        {"n": "02", "title": "Two", "value": "", "note": "second", "icon": "eye"}]}
    f = tmp_path / IP.preview_path(slug, slot, style)
    f.parent.mkdir(parents=True)
    f.write_text(IP.render_preview(p, style, facts, IP.load_tokens(IP.ROOT)))
    out = tmp_path / "out"
    got = IP.bake_infographic(slug, slot, style, out, root=tmp_path)
    full, sib = out / f"{slug}-{slot}-{style}.webp", out / f"{slug}-{slot}-{style}-760.webp"
    assert got["full"] == str(full) and got["sib"] == str(sib)
    with Image.open(full) as a, Image.open(sib) as b:
        assert a.format == b.format == "WEBP"
        assert a.width == IP.BAKE_BOX[0] and a.height >= IP.BAKE_BOX[1]
        assert b.width == IP.BAKE_SIB_W
    assert sorted(x.name for x in out.iterdir()) == sorted([full.name, sib.name])


def test_bake_refuses_a_missing_preview(tmp_path):
    with pytest.raises(FileNotFoundError):
        IP.bake_infographic("fx", "nope", "sticker", tmp_path / "out", root=tmp_path)
