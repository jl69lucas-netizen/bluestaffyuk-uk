"""scripts/build_board_previews.py — the cutter that turns the built preview route into
the board's per-style blocks, and the style-option rule the record has to satisfy first."""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_board_previews as P   # noqa: E402
import pageboard as PB             # noqa: E402


def test_style_blocks_are_cut_per_section_and_style():
    html = ('<section data-section="hero" data-style="S1">A</section>'
            '<section data-section="hero" data-style="S2">B</section>'
            '<section data-section="faq" data-style="S1">C</section>')
    blocks = P.cut(html)
    assert set(blocks) == {("hero", "S1"), ("hero", "S2"), ("faq", "S1")}
    assert blocks[("hero", "S2")] == "B"


def test_record_without_three_styles_is_refused():
    rec = {"sections": [{"id": "hero", "styles": ["S1", "S2"]}]}
    with pytest.raises(P.StyleError) as e:
        P.validate_styles(rec)
    assert "hero" in str(e.value)


def test_a_record_with_no_styles_and_one_with_all_three_are_both_accepted():
    assert P.validate_styles({"sections": [{"id": "a", "styles": []},
                                           {"id": "b", "styles": ["S1", "S2", "S3"]}]})


def test_a_fourth_style_is_refused_as_loudly_as_a_missing_one():
    with pytest.raises(P.StyleError):
        P.validate_styles({"sections": [{"id": "a", "styles": ["S1", "S2", "S3", "S4"]}]})


def test_the_cutter_keeps_a_nested_kit_section_inside_its_block():
    """The kit's Hero, TrustStrip, CounterStrip and Testimonial each render a <section>, so
    a non-greedy regex would end the block at the CHILD's closing tag and drop the rest."""
    html = ('<section data-section="hero" data-style="S1">'
            '<section class="kit-hero">inner</section>tail</section>'
            '<section data-section="hero" data-style="S2">B</section>')
    blocks = P.cut(html)
    assert blocks[("hero", "S1")] == '<section class="kit-hero">inner</section>tail'
    assert blocks[("hero", "S2")] == "B"


def test_a_section_without_both_attributes_is_not_a_block():
    blocks = P.cut('<section class="bp-page"><section data-section="a" data-style="S1">X</section></section>')
    assert set(blocks) == {("a", "S1")}


def test_the_demo_record_loads_and_offers_three_styles_on_every_styled_section():
    """`_demo` is the fixture the route, the cutter and the board builder all render. It is
    never a page: the leading underscore is what keeps it out of every page consumer."""
    rec = PB.load_board("_demo")
    assert rec["meta"]["preview"] is True and rec["meta"]["status"] == "draft"
    assert P.validate_styles(rec)
    assert [s["styles"] for s in rec["sections"]] == [["S1", "S2", "S3"]] * len(rec["sections"])


def test_main_refuses_a_slug_with_no_built_preview(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    assert P.main(["_demo"]) == 2
    assert "no built preview" in capsys.readouterr().out


def test_main_writes_css_and_blocks_from_the_built_page(tmp_path, monkeypatch):
    rec = PB.load_board("_demo")
    ids = [s["id"] for s in rec["sections"]]
    body = "".join(f'<section data-section="{i}" data-style="{s}">x{i}{s}</section>'
                   for i in ids for s in ("S1", "S2", "S3"))
    page = tmp_path / "dist" / "board-preview" / "_demo" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text(f"<html><style>.a{{color:red}}</style>{body}</html>", encoding="utf-8")
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    monkeypatch.setattr(P, "OUT", tmp_path / "previews")
    assert P.main(["_demo"]) == 0
    out = json.loads((tmp_path / "previews" / "_demo.json").read_text())
    assert out["css"] == ".a{color:red}"
    assert out["blocks"][f"{ids[0]}|S2"] == f"x{ids[0]}S2"
    assert len(out["blocks"]) == 3 * len(ids)


def test_main_reports_a_styled_section_the_built_page_did_not_render(tmp_path, monkeypatch, capsys):
    """A gate that examined nothing is not a pass: a block the record asked for and the
    page did not produce is named, not silently written out as an empty iframe."""
    rec = PB.load_board("_demo")
    first = rec["sections"][0]["id"]
    page = tmp_path / "dist" / "board-preview" / "_demo" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text(f'<section data-section="{first}" data-style="S1">x</section>', encoding="utf-8")
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    monkeypatch.setattr(P, "OUT", tmp_path / "previews")
    assert P.main(["_demo"]) == 1
    assert f"{first}|S2" in capsys.readouterr().out


# --- the gate rule and the board's style fieldset ----------------------------------------

def _styled():
    """MIN_BOARD with its one section offering the three styles, approved with no pick."""
    import json as _json
    from test_page_board import MIN_BOARD, _approved
    b = _json.loads(_json.dumps(MIN_BOARD))
    b["sections"][0]["styles"] = ["S1", "S2", "S3"]
    return _approved(b)


def test_gate_fails_style_unpicked_on_an_approved_record_and_skips_a_draft():
    from test_page_board import ONT_OK, LEDGER_EMPTY
    b = _styled()
    b["approval"]["picks"] = {}
    b["approval"]["record_hash"] = PB.record_hash(b)
    live = {"/other/": ["Where Do We Deliver Each Week?"],
            "/uk-locations/staffy-puppies-for-sale-glasgow/": []}
    f = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live=live, stage="build")
    assert [x for x in f if x["check"] == "style-unpicked"], f

    # A draft has not been answered yet, so it is not yet in default on the answer.
    b["meta"]["status"] = "draft"
    f = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY, live=live, stage="build")
    assert [x for x in f if x["check"] == "style-unpicked"] == []


def test_gate_passes_once_the_approval_names_a_style():
    from test_page_board import ONT_OK, LEDGER_EMPTY
    b = _styled()
    b["approval"]["picks"] = {b["sections"][0]["id"]: "S2"}
    b["approval"]["record_hash"] = PB.record_hash(b)
    f = PB.gate_findings(b, ONT_OK, LEDGER_EMPTY,
                         live={"/other/": ["Where Do We Deliver Each Week?"],
                               "/uk-locations/staffy-puppies-for-sale-glasgow/": []},
                         stage="build")
    assert [x for x in f if x["check"] == "style-unpicked"] == []


def test_the_board_renders_one_radio_group_of_three_styles_and_no_component_cards():
    """The style fieldset REPLACES the ledger option cards: both wrote `pick-<id>`, and two
    controls on one radio name is a board that can save a pick nobody made."""
    import build_page_board as BPB
    from test_page_board import ONT_OK, LEDGER_EMPTY
    b = _styled()
    sid = b["sections"][0]["id"]
    previews = {"css": ".x{color:red}", "images": {},
                "blocks": {f"{sid}|S1": "<p>one</p>", f"{sid}|S2": "<p>two</p>", f"{sid}|S3": "<p>three</p>"},
                "names": {f"{sid}|S1": "First", f"{sid}|S2": "Second", f"{sid}|S3": "Third"}}
    html = BPB.render(b, ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x", previews=previews)
    assert html.count(f'name="pick-{sid}"') == 3
    assert 'value="S1"' in html and 'value="S3"' in html and "Second" in html
    assert "nothumb" not in html.split("6. Component options")[1].split("</script>")[0]
    # three widths per style, nine frames for the one section
    assert html.count(f'data-block="{sid}|') == 9
    for w in BPB.PREVIEW_W:
        assert f'width="{w}"' in html


def test_the_board_says_so_when_a_style_has_not_been_rendered_yet():
    import build_page_board as BPB
    from test_page_board import ONT_OK, LEDGER_EMPTY
    b = _styled()
    html = BPB.render(b, ONT_OK, LEDGER_EMPTY, live={}, thumbs={}, slug="x")
    assert "build_board_previews.py" in html and "data-block=" not in html


def test_picked_sections_covers_a_styled_standard_section():
    import build_page_board as BPB
    b = _styled()
    b["sections"][0]["shape"] = "standard"
    assert BPB.picked_sections(b) == [b["sections"][0]["id"]]


def test_board_preview_slugs_nest_and_stay_out_of_the_field_contract():
    import form_contract_audit as F
    assert "board-preview" in F.NON_CONTENT_ROUTES
    assert F.contract_keys("board-preview/_demo") == []
    assert F.contract_keys("board-preview") == []
    # Not a loosening: a sibling slug that merely starts with the same letters is content.
    assert [k[0] for k in F.contract_keys("board-preview-notes")] == [k[0] for k in F.KEYS]
