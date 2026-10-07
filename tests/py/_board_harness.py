"""Run a built board page in a real browser (tests/py/fixtures/board_style/run.cjs) and return
what it measured, or skip when node, Playwright or its browser is missing."""
import json
import os
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HARNESS = ROOT / "tests" / "py" / "fixtures" / "board_style" / "run.cjs"


def _node_path():
    """node_modules of this checkout, then of the main checkout when this is a worktree."""
    paths = [ROOT / "node_modules"]
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()
    if common:
        paths.append((ROOT / common).resolve().parent / "node_modules")
    return ":".join(str(p) for p in paths if p.is_dir())


def run(page):
    if shutil.which("node") is None:
        pytest.skip("node not installed")
    env = dict(os.environ, NODE_PATH=_node_path())
    probe = subprocess.run(["node", "-e", "require('playwright')"], cwd=ROOT, env=env,
                           capture_output=True, text=True)
    if probe.returncode != 0:
        pytest.skip("playwright is not installed (node_modules here or in the main checkout)")
    res = subprocess.run(["node", str(HARNESS), str(page)], cwd=ROOT, env=env,
                         capture_output=True, text=True, timeout=180)
    if res.stdout.startswith("SKIP"):
        pytest.skip(res.stdout.strip())
    assert res.returncode == 0, res.stderr
    return json.loads(res.stdout.split("RESULT ", 1)[1])
