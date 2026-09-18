"""build_design_canvas.py turns one built section into one Design-type artboard."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_design_canvas as B

FIX = ROOT / "tests/py/fixtures/canvas-section.html"


def test_sections_are_found_by_component_and_variant():
    secs = B.find_sections(FIX.read_text())
    assert [(s.component, s.variant) for s in secs] == [("buttons", "a"), ("buttons", "b")]
    assert secs[0].width == 640


def test_artboard_has_required_skeleton():
    secs = B.find_sections(FIX.read_text())
    html = B.artboard(secs[0], css=".kit-btn{min-height:44px}", fonts_link=B.FONTS_LINK, height=120, assets={})
    assert html.startswith("<!doctype html>")
    assert '<script src="./support.js"></script>' in html
    assert "<x-dc>" in html and "</x-dc>" in html
    assert 'data-dc-script' in html and '"$preview":{"width":640,"height":120}' in html
    assert "class Component extends DCLogic" in html
    assert "<iframe" not in html and "<script src=\"/" not in html


def test_assets_are_rewritten_to_blob_urls():
    secs = B.find_sections(FIX.read_text())
    html = B.artboard(secs[1], css="", fonts_link="", height=100, assets={"/_astro/roman.abc.jpg": "/_blob/deadbeef"})
    assert "/_blob/deadbeef" in html and "/_astro/roman.abc.jpg" not in html


def test_canvas_index_lays_out_rows():
    rows = [{"id": "buttons", "title": "3 · Buttons", "board_width": 640}]
    boards = [("buttons", v, 120) for v in "abcde"]
    idx = B.canvas_index("BlueStaffyUK Design Canvas", rows, boards, existing=None)
    assert idx["v"] == 3 and "createdOnFiles" in idx
    assert len(idx["boards"]) == 5 and len(idx["order"]) == 5
    xs = [idx["boards"][f"buttons-{v}.dc.html"]["x"] for v in "abcde"]
    assert xs == [0, 720, 1440, 2160, 2880]           # 640 wide + 80 gap
    assert list(idx["notes"].values())[0]["kind"] == "title1"
