"""build_design_canvas.py turns one built section into one Design-type artboard."""
import json, pathlib, sys

import pytest
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


def test_component_scripts_are_stripped_from_sections():
    """A component's own <script> points at a /_astro bundle that does not exist on the
    canvas. An artboard is a static rendering, so the tag is dropped rather than shipped as
    a 404 — and dropped in find_sections, so the missing-asset scan never sees it either."""
    html = ('<section data-component="buttons" data-variant="a" data-width="640">'
            '<p>x</p><script type="module" src="/_astro/a.js"></script></section>')
    secs = B.find_sections(html)
    assert "<script" not in secs[0].inner and "<p>x</p>" in secs[0].inner


def test_artboard_width_can_be_overridden_for_the_responsive_boards():
    """Spec §11 amendment 3d: the same built section becomes a 375 and a 768 board."""
    sec = B.find_sections(FIX.read_text())[0]
    html = B.artboard(sec, css="", fonts_link="", height=300, assets={}, width=375)
    assert '"$preview":{"width":375,"height":300}' in html
    assert "width: 375px" in html


PICKED_ROWS = [{"id": "buttons", "title": "3 · Buttons", "board_width": 640},
               {"id": "faq", "title": "9 · FAQ", "board_width": 640}]


def test_canvas_index_adds_the_picked_mobile_and_tablet_rows():
    boards = [(cid, "a", 120) for cid in ("buttons", "faq")]
    picked = [(cid, "a", suffix, 200) for cid in ("buttons", "faq") for suffix in ("m375", "t768")]
    idx = B.canvas_index("BlueStaffyUK Design Canvas", PICKED_ROWS,
                         [(cid, v, 120) for cid in ("buttons", "faq") for v in "abcde"],
                         existing=None, picked=picked)
    assert boards  # the five-variant rows are unchanged
    for suffix, w, title in B.RESPONSIVE_ROWS:
        files = [f"buttons-a-{suffix}.dc.html", f"faq-a-{suffix}.dc.html"]
        for f in files:
            assert f in idx["boards"] and f in idx["order"], f
            assert idx["boards"][f]["w"] == w
        # one board per component, in components.json order, 80px gap
        assert [idx["boards"][f]["x"] for f in files] == [0, w + 80]
        assert idx["boards"][files[0]]["y"] == idx["boards"][files[1]]["y"]
        note = idx["notes"][f"row-picked-{suffix}"]
        assert note["text"] == title and note["kind"] == "title1"
    # the faq board stays interactive at every width
    assert idx["boards"]["faq-a-m375.dc.html"]["is_interactive"] is True
    # the two new rows sit below every five-variant row
    variant_y = max(idx["boards"][f"{cid}-e.dc.html"]["y"] for cid in ("buttons", "faq"))
    assert min(idx["boards"][f"buttons-a-{s}.dc.html"]["y"] for s, _, _ in B.RESPONSIVE_ROWS) > variant_y


def test_the_real_canvas_carries_thirteen_boards_in_each_picked_row():
    """The built canvas.json, not a fixture: one picked board per component at each width."""
    idx_path = ROOT / "docs/artifacts/canvas/project/canvas.json"
    if not idx_path.exists():
        pytest.skip("run npm run canvas:build first")
    idx = json.loads(idx_path.read_text())
    picks = json.loads((ROOT / "data/design/picks.json").read_text())["picks"]
    for suffix, w, title in B.RESPONSIVE_ROWS:
        files = [f for f in idx["boards"] if f.endswith(f"-{suffix}.dc.html")]
        assert len(files) == len(picks) == 13, (suffix, len(files))
        assert {idx["boards"][f]["w"] for f in files} == {w}
        xs = sorted(idx["boards"][f]["x"] for f in files)
        assert xs == [i * (w + 80) for i in range(13)], (suffix, xs)
        assert idx["notes"][f"row-picked-{suffix}"]["text"] == title
        for cid, p in picks.items():
            assert f"{cid}-{p['variant']}-{suffix}.dc.html" in idx["boards"], (cid, suffix)
