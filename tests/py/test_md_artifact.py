"""The markdown Artifact page (scripts/_md_artifact.py) that the research board and the outline
matrix ship as: its `.md` download goes through the viewer's `downloads` capability.

The claude.ai Artifact viewer never grants a page download permission, so an `<a download>` or
a blob-URL click does nothing there (the publish warning of 2026-10-07). The page declares
`downloads`, saves with `downloads.save({filename, data})`, hides the button when the runtime
cannot save, and keeps "Copy all as Markdown" as the fallback that always works.
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
import _md_artifact as MA  # noqa: E402

HARNESS = ROOT / "tests" / "py" / "fixtures" / "md_artifact"
SECTIONS = [("One", "Alpha **bold**\n\n| a | b |\n|---|---|\n| 1 | 2 |"), ("Two & more", "Beta </script> end")]


def _page():
    return MA.page("T", "E", "Head & Tail", "s", "d", "r", SECTIONS, "head-tail.md")


def test_the_page_declares_the_downloads_capability_for_its_publish():
    assert MA.CAPABILITIES == {"downloads": True}
    hint = MA.publish_hint("docs/artifacts/research/x.html")
    assert "docs/artifacts/research/x.html" in hint and '{"downloads": true}' in hint


def test_the_download_saves_through_the_runtime_never_a_link():
    page = _page()
    assert 'use.call(window.claude,"downloads")' in page
    assert "downloads.save({filename:name,data:whole})" in page
    for dead in ("createObjectURL", ".download=", " download=", "a.click()"):
        assert dead not in page, dead
    # Hidden until the runtime says it can save; copy-all is always there.
    assert re.search(r'<button class="btn ghost" id="dl-md" hidden>Download \.md</button>', page)
    assert '<button class="btn" id="copy-all">Copy all as Markdown</button>' in page


def test_the_generators_print_the_capability_with_the_publish_step():
    for script in ("research_board.py", "outline_matrix.py"):
        src = (ROOT / "scripts" / script).read_text(encoding="utf-8")
        assert "MA.publish_hint(html_path)" in src, script
        assert 'capabilities={"downloads": true}' in src, script


def _node_path():
    """node_modules of this checkout, then of the main checkout when this is a worktree."""
    paths = [ROOT / "node_modules"]
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()
    if common:
        paths.append((ROOT / common).resolve().parent / "node_modules")
    return ":".join(str(p) for p in paths if p.is_dir())


def test_the_download_in_a_browser_against_a_fake_runtime(tmp_path):
    if shutil.which("node") is None:
        pytest.skip("node not installed")
    env = dict(os.environ, NODE_PATH=_node_path())
    probe = subprocess.run(["node", "-e", "require('playwright')"], cwd=ROOT, env=env,
                           capture_output=True, text=True)
    if probe.returncode != 0:
        pytest.skip("playwright is not installed (node_modules here or in the main checkout)")
    page = tmp_path / "board.html"
    page.write_text(_page(), encoding="utf-8")
    run = subprocess.run(["node", str(HARNESS / "run.cjs"), str(page)],
                         cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
    if run.stdout.startswith("SKIP"):
        pytest.skip(run.stdout.strip())
    assert run.returncode == 0, run.stderr
    res = json.loads(run.stdout.split("RESULT ", 1)[1])
    for mode in res.values():
        assert mode["errors"] == [] and mode["copyAllVisible"] and mode["sections"] == 2, res
    # A saved copy outside the viewer, and a viewer that cannot save: no button, copy-all stays.
    assert res["none"]["hiddenBefore"] and res["nullNs"]["hiddenBefore"], res
    # The viewer can save: the button shows and hands over the exact markdown under its name.
    s = res["save"]
    assert not s["hiddenBefore"] and not s["hiddenAfter"] and s["status"] == "Downloaded", res
    assert s["saves"] == [{"filename": "head-tail.md", "data": MA.markdown("Head & Tail", SECTIONS)}], res
    # The viewer said no: nothing retried, the button stays for another go.
    d = res["declined"]
    assert len(d["saves"]) == 1 and not d["hiddenAfter"] and "cancelled" in d["status"], res
    # The runtime cannot save after all: the button goes and the page points at copy-all.
    u = res["unavailable"]
    assert u["hiddenAfter"] and "Copy all as Markdown" in u["status"], res
