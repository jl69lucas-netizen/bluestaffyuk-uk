"""build_design_canvas.py turns one built preview section into one Design-type artboard."""
import json, pathlib, sys

import pytest
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_design_canvas as B

FIX = ROOT / "tests/py/fixtures/canvas-section.html"


def test_sections_are_found_by_component():
    secs = B.find_sections(FIX.read_text())
    assert [s.component for s in secs] == ["buttons", "puppy-card"]
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


def test_component_scripts_are_stripped_from_sections():
    """A component's own <script> points at a /_astro bundle that does not exist on the
    canvas. An artboard is a static rendering, so the tag is dropped rather than shipped as
    a 404 — and dropped in find_sections, so the missing-asset scan never sees it either."""
    html = ('<section data-component="buttons" data-width="640">'
            '<p>x</p><script type="module" src="/_astro/a.js"></script></section>')
    secs = B.find_sections(html)
    assert "<script" not in secs[0].inner and "<p>x</p>" in secs[0].inner


def test_artboard_width_can_be_overridden_for_the_responsive_boards():
    """Spec §11 amendment 3d: the same built section becomes a 375 and a 768 board."""
    sec = B.find_sections(FIX.read_text())[0]
    html = B.artboard(sec, css="", fonts_link="", height=300, assets={}, width=375)
    assert '"$preview":{"width":375,"height":300}' in html
    assert "width: 375px" in html


ROWS = [{"id": "buttons", "title": "3 · Buttons", "board_width": 640},
        {"id": "faq", "title": "9 · FAQ", "board_width": 640}]
HEIGHTS = {"buttons": 120, "faq": 160,
           "buttons-m375": 200, "faq-m375": 220,
           "buttons-t768": 180, "faq-t768": 190}


def test_canvas_index_lays_out_one_board_per_component_in_three_rows():
    """Task 19 pruned the kit, so a row is one board per component rather than five per
    component: no board name carries a letter, and the three rows are the component's own
    width, then 375, then 768."""
    idx = B.canvas_index("BlueStaffyUK Design Canvas", ROWS, HEIGHTS, existing=None)
    assert idx["v"] == 3 and "createdOnFiles" in idx
    assert len(idx["boards"]) == 6 and len(idx["order"]) == 6
    for suffix, row_w, title in B.BOARD_ROWS:
        files = [B.board_name(cid, suffix) for cid in ("buttons", "faq")]
        w = row_w or 640
        for f in files:
            assert f in idx["boards"] and f in idx["order"], f
            assert idx["boards"][f]["w"] == w
        # one board per component, in components.json order, 80px gap
        assert [idx["boards"][f]["x"] for f in files] == [0, w + B.GAP]
        assert idx["boards"][files[0]]["y"] == idx["boards"][files[1]]["y"]
        note = idx["notes"][f"row-{suffix or 'kit'}"]
        assert note["text"] == title and note["kind"] == "title1"
        # the faq board stays interactive at every width
        assert idx["boards"][B.board_name("faq", suffix)]["is_interactive"] is True
    # the rows stack downwards in BOARD_ROWS order
    ys = [idx["boards"][B.board_name("buttons", s)]["y"] for s, _, _ in B.BOARD_ROWS]
    assert ys == sorted(ys) and len(set(ys)) == 3


def test_every_board_takes_its_measured_height():
    """A board whose frame does not match what was measured crops or pads the rendering,
    and the canvas is then judged on a box rather than on the component."""
    idx = B.canvas_index("t", ROWS, HEIGHTS, existing=None)
    for suffix, _, _ in B.BOARD_ROWS:
        for cid in ("buttons", "faq"):
            assert idx["boards"][B.board_name(cid, suffix)]["h"] == HEIGHTS[B.height_key(cid, suffix)]
    # an unmeasured board falls back rather than failing the build
    assert B.canvas_index("t", ROWS, {}, existing=None)["boards"]["buttons.dc.html"]["h"] == 200


def test_the_real_canvas_carries_thirteen_boards_in_each_of_the_three_rows():
    """The built canvas.json, not a fixture: 13 components x 3 widths = 39 boards, and no
    board name carries a variant letter any more."""
    idx_path = ROOT / "docs/artifacts/canvas/project/canvas.json"
    if not idx_path.exists():
        pytest.skip("run npm run canvas:build first")
    idx = json.loads(idx_path.read_text())
    rows = json.loads((ROOT / "data/design/components.json").read_text())
    assert len(idx["boards"]) == 39, len(idx["boards"])
    for suffix, row_w, title in B.BOARD_ROWS:
        files = [B.board_name(r["id"], suffix) for r in rows]
        assert all(f in idx["boards"] for f in files), suffix
        widths = [row_w or r["board_width"] for r in rows]
        assert [idx["boards"][f]["w"] for f in files] == widths, suffix
        xs, x = [], 0
        for w in widths:
            xs.append(x)
            x += w + B.GAP
        assert [idx["boards"][f]["x"] for f in files] == xs, suffix
        assert idx["notes"][f"row-{suffix or 'kit'}"]["text"] == title
    # every board file the index names was actually written
    project = idx_path.parent
    for f in idx["boards"]:
        assert (project / f).exists(), f
