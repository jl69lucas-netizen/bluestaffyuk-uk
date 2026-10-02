"""Block 7c: which sections need an infographic, which IG type, three styles each."""
import json
import re
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


def test_three_styles_each():
    for p in IP.plan(BOARD, root=None):
        assert [s["id"] for s in p["styles"]] == ["plate", "ruled", "card"]


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
            assert "<script src" not in html.lower()
            assert not re.search(r'(src|href)="https?://', html)
            assert ":root{" in html and "--color-steel-700" in html


def test_block_markdown_lists_slots_and_previews():
    md = IP.block(BOARD)
    assert "| Section | Heading | IG type | Why it triggered |" in md
    assert "| delivery |" in md and "IG-5" in md
    for style in ("plate", "ruled", "card"):
        assert f"docs/artifacts/boards/ig/blue-staffy-puppies-london/delivery-route-{style}.html" in md
    assert "pick-ig:delivery-route" in md


def test_breed_split_subjects_on_the_real_london_heading():
    board = json.loads((IP.ROOT / "data/boards/blue-staffy-puppies-london.json").read_text())
    p = [p for p in IP.plan(board) if p["section"] == "breed"][0]
    assert p["facts"]["subjects"] == ["English Staffy", "American Staffy"]
    assert p["alt"] == "English Staffy compared with American Staffy"


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
