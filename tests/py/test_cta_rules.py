"""scripts/cta_rules.py — working rule 12, CTAs included (breeder, 2026-10-08): every call to
action on a page boarded from today on is a slot on the board with three options, the breeder
picks one per slot, and the picks never repeat a text or a style."""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import cta_rules as CR      # noqa: E402
import pageboard as PB      # noqa: E402

SLUG = "uk-locations/blue-staffy-puppies-leeds"


def _record(status="boarded"):
    """The demo record as a new location page boarded after the CTA rule."""
    b = copy.deepcopy(json.loads((ROOT / "data" / "boards" / "_demo.json").read_text()))
    b["meta"].update({"slug": SLUG, "page_type": "location", "status": status})
    return b


def _ids(b):
    return [s["id"] for s in b["sections"]]


def _slot(slot, section, typ, texts, styles, target="#x"):
    opts = []
    for oid, t, st in zip("abc", texts, styles):
        o = {"id": oid, "text": t, "style": st}
        if st == "sub":
            o["sub"] = "Collection in Carlisle or UK delivery"
        if st == "tag":
            o["tag"] = "Carlisle"
        opts.append(o)
    out = {"slot": slot, "section": section, "type": typ, "why": "w", "options": opts}
    if typ != "submit":
        out["target"] = target
    return out


def _three_spaced(b):
    """Three body slots with a section between each, distinct texts and styles."""
    ids = _ids(b)
    t = f"#{ids[-1]}"
    return [
        _slot("hero", ids[0], "ask", ["Start with a question about a puppy", "Tell us what you want", "Ask us anything first"],
              ["down", "chip", "sub"], t),
        _slot("litter", ids[2], "ask", ["Ask which puppy suits your home", "Tell us which puppy you like", "Ask about this litter"],
              ["arrow", "tag", "caps"], t),
        _slot("terms", ids[4], "ask", ["Ask us for the full terms", "Ask to read the contract", "Ask what is covered"],
              ["wide", "solid", "arrow"], t),
    ]


def _codes(b):
    return sorted({c for c, sev, m in CR.findings(b) if sev == "FAIL"})


def test_demo_record_has_enough_sections_for_the_fixtures():
    assert len(_ids(_record())) >= 5


# ── where the rule binds ────────────────────────────────────────────────────────────────
def test_a_new_location_board_with_no_ctas_fails_and_a_draft_warns():
    assert _codes(_record()) == ["cta-board-missing"]
    assert [sev for c, sev, m in CR.findings(_record("draft"))] == ["WARN"]


def test_london_and_manchester_were_approved_before_the_rule():
    for slug in ("blue-staffy-puppies-london", "blue-staffy-puppies-manchester-uk"):
        b = PB.load_board(slug)
        assert not CR.applies(b) and CR.findings(b) == [] and CR.slots_needing_pick(b) == []


# ── the record ──────────────────────────────────────────────────────────────────────────
def test_three_spaced_distinct_slots_pass():
    b = _record()
    b["ctas"] = _three_spaced(b)
    assert _codes(b) == [], CR.findings(b)


def test_a_slot_offers_exactly_three_different_buttons():
    b = _record()
    b["ctas"] = _three_spaced(b)
    b["ctas"][0]["options"][1]["text"] = "Start with a question about the puppy"     # a twin of option a
    b["ctas"][1]["options"] = b["ctas"][1]["options"][:2]
    msgs = [m for c, sev, m in CR.findings(b)]
    assert any("say the same thing" in m for m in msgs) and any("exactly three" in m for m in msgs)


def test_a_typed_figure_and_a_long_label_are_refused():
    b = _record()
    b["ctas"] = _three_spaced(b)
    b["ctas"][0]["options"][0]["text"] = "Reserve with a £500 deposit"
    b["ctas"][1]["options"][0]["text"] = "Ask us which of the puppies in this litter would suit your home"
    msgs = " ".join(m for c, sev, m in CR.findings(b))
    assert "types a figure" in msgs and "word(s)" in msgs


def test_count_band_and_neighbouring_sections():
    b = _record()
    ids = _ids(b)
    b["ctas"] = _three_spaced(b)[:2]                                                    # 2 < location min 3
    assert "cta-count-out-of-band" in _codes(b)
    b["ctas"] = _three_spaced(b)
    b["ctas"][1]["section"] = ids[1]                                                   # next to the hero
    assert any("neighbouring" in m for c, sev, m in CR.findings(b))


# ── the picks ───────────────────────────────────────────────────────────────────────────
def test_every_slot_needs_a_pick_on_the_approve_button():
    b = _record()
    b["ctas"] = _three_spaced(b)
    assert CR.slots_needing_pick(b) == ["cta:hero", "cta:litter", "cta:terms"]
    assert CR.validate_cta_picks(b, {"cta:hero": "a"}) == [
        "CTA slot 'litter' has no pick", "CTA slot 'terms' has no pick"]


def test_picks_never_repeat_a_style_or_say_the_same_thing():
    b = _record()
    b["ctas"] = _three_spaced(b)
    assert CR.validate_cta_picks(b, {"cta:hero": "a", "cta:litter": "a", "cta:terms": "a"}) == []
    same_style = CR.validate_cta_picks(b, {"cta:hero": "a", "cta:litter": "a", "cta:terms": "c"})   # arrow twice
    assert any("both pick style arrow" in e for e in same_style)
    b["ctas"][2]["options"][1]["text"] = "Ask which puppy suits your household"
    twins = CR.validate_cta_picks(b, {"cta:hero": "a", "cta:litter": "a", "cta:terms": "b"})
    assert any("near-identical" in e for e in twins)


def test_a_pick_naming_no_slot_or_option_is_refused():
    b = _record()
    b["ctas"] = _three_spaced(b)
    errs = CR.validate_cta_picks(b, {"cta:hero": "d", "cta:nowhere": "a"})
    assert any("'d' is not one of a, b, c" in e for e in errs) and any("no CTA slot 'nowhere'" in e for e in errs)


# ── the shared rules agree with the render check ─────────────────────────────────────────
def test_near_identical_matches_the_render_check_cases():
    assert CR.near_identical("Ask about a puppy", "Ask us about a puppy")            # Manchester, 2026-10-08
    assert CR.near_identical("Send enquiry", "Send my enquiry")                     # buy page vs contact
    assert not CR.near_identical("Ask about Roman", "Ask about Byrd")
    assert not CR.near_identical("Send me the litter note", "Send my enquiry")


def test_the_style_catalog_is_the_same_in_python_css_and_the_component():
    css = (ROOT / "src/styles/cta.css").read_text()
    comp = (ROOT / "src/components/kit/CtaButton.astro").read_text()
    assert f"export const CTA_STYLES = [{', '.join(repr(s) for s in CR.STYLES)}]" in comp
    for s in CR.STYLES:
        if s != "solid":
            assert f'data-cta-style="{s}"' in css, s
    schema = json.loads((ROOT / "schemas/board.schema.json").read_text())
    assert schema["properties"]["ctas"]["items"]["properties"]["options"]["items"]["properties"]["style"]["enum"] == list(CR.STYLES)


# ── a proposal is a valid starting point ────────────────────────────────────────────────
def test_the_proposal_is_valid_and_its_first_options_can_be_approved_together():
    b = _record()
    b["ctas"] = CR.propose(b)
    problems = [m for c, m in CR.slot_problems(b) if c == "cta-slot-invalid"]
    assert problems == [], problems
    picks = {f"cta:{s['slot']}": "a" for s in b["ctas"]}
    assert CR.validate_cta_picks(b, picks) == []


def test_the_board_block_paints_each_option_and_is_absent_before_the_rule():
    b = _record()
    b["ctas"] = _three_spaced(b)
    html = CR.board_block(b)
    assert html.count('name="pick-cta:hero"') == 3 and 'data-cta-style="caps"' in html
    assert "--color-cta:" in html                                                      # tokens inlined
    assert CR.board_block(PB.load_board("blue-staffy-puppies-london")) == ""


def test_the_catalog_preview_paints_every_style_and_a_board_block():
    b = _record()
    b["ctas"] = CR.propose(b)
    page = CR.catalog_html(b)
    for s in CR.STYLES:
        assert f'data-cta-style="{s}"' in page, s
    assert 'name="pick-cta:hero"' in page and "<title>BSUK CTA Styles</title>" in page
