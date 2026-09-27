"""scripts/build_component_canvas.py — the London component canvas page (Plan 1, Task 4).

The builder is tested on a synthetic canvas of fifteen components × three minimal fragments
written to tmp_path, so these tests run before any real variant exists.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_component_canvas as B  # noqa: E402
from city_components import COMPONENT_IDS  # noqa: E402

CLIENT = ROOT / "scripts" / "component_canvas_client.js"
HARNESS = ROOT / "tests" / "py" / "fixtures" / "component_canvas"
FAKE = ROOT / "tests" / "py" / "fixtures" / "answer_board" / "harness" / "fake.js"


def _canvas(tmp_path, n=15):
    root = tmp_path / "london"
    for cid in COMPONENT_IDS[:n]:
        d = root / cid
        d.mkdir(parents=True)
        for v in "abc":
            (d / f"{v}.html").write_text(
                f'<style>.x{{color:var(--color-brand)}}</style><section data-component="{cid}" '
                f'data-variant="{v}"><img src="/images/ethical-staffy-puppy-london-delivery.webp" '
                f'alt="London" width="4" height="3"><p class="x">London {cid} {v} </script></p></section>',
                encoding="utf-8")
        (d / "meta.json").write_text(json.dumps({"component": cid, "variants": {
            v: {"name": f"{cid} {v}", "description": "One line.", "idea_sources": ["/x/y/idea.png"],
                "differs_from": "Differs from every built page.",
                "axes": {"layout": v, "media": "none", "density": "airy", "framing": "plain"}}
            for v in "abc"}}), encoding="utf-8")
    return root


def page(tmp_path, final=False):
    frags, metas = B.load_canvas(_canvas(tmp_path))
    return B.render_page(frags, metas, B.frame_tokens(), final=final)


def test_the_page_has_fifteen_sections_in_city_page_order(tmp_path):
    html = page(tmp_path)
    got = re.findall(r'<section class="comp" id="c-([a-z-]+)"', html)
    assert got == list(COMPONENT_IDS)


def test_forty_five_lazy_frames_and_no_srcdoc_in_the_markup(tmp_path):
    html = page(tmp_path)
    keys = re.findall(r'<iframe [^>]*data-key="([a-z-]+/[abc])"', html)
    assert len(keys) == 45 and len(set(keys)) == 45
    assert "srcdoc=" not in html  # set by the client, one section at a time
    blob = html.split('<script type="application/json" id="frames">', 1)[1].split("</script>", 1)[0]
    frames = json.loads(blob)
    assert sorted(frames) == sorted(keys)
    doc = frames["hero/a"]
    assert doc.startswith("<!doctype html>") and ":root {" in doc and "@theme" not in doc
    assert 'src="images/ethical-staffy-puppy-london-delivery.webp"' in doc  # relative to the page
    assert "</script></p>" in doc  # the blob round-trips a closing tag safely


def test_every_component_has_a_four_way_pick_and_a_note(tmp_path):
    html = page(tmp_path)
    for cid in COMPONENT_IDS:
        radios = re.findall(rf'name="pick-{cid}" value="(\w+)"', html)
        assert radios == ["a", "b", "c", "redesign"], cid
        assert f'data-note="{cid}"' in html
    assert 'id="general-notes"' in html and 'id="send-picks"' in html and 'id="copy-picks"' in html


def test_the_sticky_components_scroll_inside_a_device_high_frame(tmp_path):
    html = page(tmp_path)
    device = re.findall(r'id="c-([a-z-]+)"[^>]*data-frame="device"', html)
    assert device == ["desktop-dial", "jump-links"]
    assert "DEVICE_H = { 375: 812, 768: 1024, 1280: 800 }" in CLIENT.read_text(encoding="utf-8")


def test_the_width_switch_defaults_to_phone(tmp_path):
    html = page(tmp_path)
    assert html.count('data-width="375" aria-pressed="true"') == 16  # 15 sections + the global one
    assert 'data-width="1280" aria-pressed="false"' in html
    assert all(f'data-component="{c}" data-width="375"' in html for c in COMPONENT_IDS)


def test_the_artifact_contract(tmp_path):
    html = page(tmp_path)
    assert "<title>London Component Canvas</title>" in html
    assert 'name="viewport"' in html and "body{margin:0;background:var(--ground)" in html
    assert '@media (prefers-color-scheme: dark){:root:not([data-theme="light"])' in html
    assert ':root[data-theme="dark"]' in html
    assert "padding:24px clamp(16px,3vw,40px)" in html and "overflow-x:hidden" in html
    hosts = set(re.findall(r'(?:src|href)="https?://([^/"]+)', html))
    assert hosts <= {"fonts.googleapis.com"}, hosts


def test_no_colour_literal_outside_a_root_block(tmp_path):
    html = page(tmp_path)
    stripped = re.sub(r":root[^{]*\{[^}]*\}", "", html)
    assert not re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{8}\b", stripped)


def test_the_client_is_inlined_and_wired_to_the_db_and_comments(tmp_path):
    html = page(tmp_path)
    js = CLIENT.read_text(encoding="utf-8")
    assert js.split("\n", 1)[1][:200] in html
    for needle in ('use.call(window.claude, "db")', 'use.call(window.claude, "comments")',
                   'db.collection("picks")', 'db.collection("notes")', 'db.collection("submissions")',
                   "sendToClaude", "anchorFor", "onSnapshot", "localStorage", "IntersectionObserver",
                   "Read-only view"):
        assert needle in js, needle


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_the_client_is_valid_javascript():
    run = subprocess.run(["node", "--check", str(CLIENT)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr


def test_final_disables_every_control(tmp_path):
    html = page(tmp_path, final=True)
    assert 'data-final="true"' in html and "Final — these picks are frozen" in html
    assert html.count(" disabled>") >= 15 * 4


def test_the_files_map_lists_each_used_image_once(tmp_path):
    frags, _m = B.load_canvas(_canvas(tmp_path))
    assert B.files_map(frags) == {
        "images/ethical-staffy-puppy-london-delivery.webp":
            "public/images/ethical-staffy-puppy-london-delivery.webp"}


def test_inline_images_embeds_the_repo_file(tmp_path):
    frags, metas = B.load_canvas(_canvas(tmp_path, n=1))
    html = B.render_page(frags, metas, B.frame_tokens(), inline=True)
    frames = json.loads(html.split('<script type="application/json" id="frames">', 1)[1].split("</script>", 1)[0])
    assert 'src="data:image/webp;base64,' in frames["hero/a"]
    assert "images/ethical-staffy" not in frames["hero/a"]


def test_emit_frames_removes_what_the_last_index_listed(tmp_path):
    out = ROOT / "docs" / "artifacts" / "canvas" / "frames-pytest-stale"
    try:
        frags, _m = B.load_canvas(_canvas(tmp_path / "one", n=2))
        B.emit_frames(frags, out, B.frame_tokens())
        assert (out / "counter-strip" / "a.html").is_file()
        frags, _m = B.load_canvas(_canvas(tmp_path / "two", n=1))
        B.emit_frames(frags, out, B.frame_tokens())
        assert not (out / "counter-strip" / "a.html").exists()
        assert (out / "hero" / "a.html").is_file()
    finally:
        shutil.rmtree(out, ignore_errors=True)


def test_emit_frames_writes_served_paths_and_an_index(tmp_path):
    frags, _m = B.load_canvas(_canvas(tmp_path, n=2))
    out = ROOT / "docs" / "artifacts" / "canvas" / "frames-pytest"
    try:
        index = B.emit_frames(frags, out, B.frame_tokens())
        assert [(r["component"], r["variant"]) for r in index] == [
            (c, v) for c in COMPONENT_IDS[:2] for v in "abc"]
        doc = (out / "hero" / "a.html").read_text(encoding="utf-8")
        assert 'src="/public/images/ethical-staffy-puppy-london-delivery.webp"' in doc
        assert json.loads((out / "index.json").read_text(encoding="utf-8")) == index
    finally:
        shutil.rmtree(out, ignore_errors=True)


def test_the_cli_refuses_a_partial_canvas_unless_asked(tmp_path, monkeypatch):
    _canvas(tmp_path, n=3)
    monkeypatch.setattr(B, "CANVAS_ROOT", tmp_path)
    assert B.main(["--out", str(tmp_path / "p.html")]) == 1
    assert B.main(["--out", str(tmp_path / "p.html"), "--allow-partial"]) == 0
    assert (tmp_path / "p.html").is_file()


def test_the_build_is_byte_identical(tmp_path, monkeypatch):
    _canvas(tmp_path)
    monkeypatch.setattr(B, "CANVAS_ROOT", tmp_path)
    B.main(["--out", str(tmp_path / "1.html")])
    B.main(["--out", str(tmp_path / "2.html")])
    assert (tmp_path / "1.html").read_bytes() == (tmp_path / "2.html").read_bytes()


def _node_path():
    paths = [ROOT / "node_modules"]
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()
    if common:
        paths.append((ROOT / common).resolve().parent / "node_modules")
    return ":".join(str(p) for p in paths if p.is_dir())


def test_the_client_in_a_browser_against_a_fake_db(tmp_path):
    if shutil.which("node") is None:
        pytest.skip("node not installed")
    env = dict(os.environ, NODE_PATH=_node_path())
    probe = subprocess.run(["node", "-e", "require('playwright')"], cwd=ROOT, env=env,
                           capture_output=True, text=True)
    if probe.returncode != 0:
        pytest.skip("playwright is not installed (node_modules here or in the main checkout)")
    target = tmp_path / "canvas.html"
    target.write_text(page(tmp_path), encoding="utf-8")
    run = subprocess.run(["node", str(HARNESS / "run.cjs"), str(target), str(FAKE)],
                         cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
    if run.stdout.startswith("SKIP"):
        pytest.skip(run.stdout.strip())
    assert run.returncode == 0, run.stderr
    res = json.loads(run.stdout.split("RESULT ", 1)[1])
    assert res["errors"] == [], res
    assert res["framesBefore"] == 0 and res["framesAfter"] >= 3, res   # lazy, then loaded
    assert res["pickDoc"] == {"pick": "b", "note": "keep the band"}, res
    assert res["picked"] == "1", res
    assert res["sent"] == 1 and res["submission"]["picks"]["hero"]["pick"] == "b", res
    assert res["status"].startswith("Sent to Claude Code (copy s-"), res
    assert res["readOnly"]["disabled"] is True, res
    assert res["readOnly"]["status"].startswith("Read-only view"), res
    assert res["seeded"] == "c", res                                    # a stored pick is shown
