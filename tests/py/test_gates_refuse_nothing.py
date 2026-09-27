"""Every `check:*` gate refuses to pass on nothing.

Learning loop 2026-09-27 (docs/reports/learning-loop-2026-09-27.md, B2 / shortlist #7). Six
brief-parity commits each taught ONE gate not to pass on zero input (the ledger, board_gate
--all, rendered_changes, the hardening scan, targets coverage, the meta guard), and every new
gate re-learned it in review. The render harness has one zero-examined guard for every check;
the Python gates had none in common. This is that guard.

Each gate in package.json runs against its own zero input, in a throwaway copy of the repo:
  pages — the committed tree (git archive HEAD, scripts/ from the working tree) with
          data/facts/rebuilt.json = [] and an empty
          dist/: the gates whose scope is the built or rebuilt pages;
  tree  — scripts/ alone and an empty dist/: the gates whose input is a data file or a folder.
The contract: exit non-zero, or print "not a pass". A traceback on missing input counts as a
refusal here (it never reads as a pass); a clean exit 0 over nothing is what this test catches.

A gate that cannot refuse its zero input today is a named, strict xfail below, so the gap is
visible and the test goes red the day it is closed (remove the row then).
"""
import json
import pathlib
import shlex
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]

#: gate -> which zero input is its own. A new check:* script fails
#: test_every_gate_is_classified until it is added here.
RECIPE = {
    "check:parity": "pages", "check:facts": "pages", "check:links": "pages",
    "check:verbatim": "pages", "check:redirects": "pages", "check:schema": "pages",
    "check:queries": "pages", "check:sitemaps": "pages", "check:retired": "pages",
    "check:boards": "pages", "check:outline": "pages",
    "check:competitors": "tree", "check:gaps": "tree", "check:placeholders": "tree",
    "check:markers": "tree", "check:workflow": "tree", "check:barriers": "tree",
    "check:threads": "tree", "check:canvas": "tree",
}

#: Gates that pass on zero input BY DESIGN today. Both judge only project 5 pages, and no
#: project 5 page exists yet, so on this repo they examine 0 and must still exit 0 or
#: check:all would fail. The first city page gives them a scope; then they should refuse zero.
KNOWN_ZERO_PASS = {
    "check:outline": "judges new-family (project 5) pages only; none is built yet "
                     "(outline_provenance_check.py prints `examined 0 new-family pages`)",
    "check:queries": "judges built project 5 pages only; none is built yet "
                     "(query_coverage_check.py prints `examined 0 pages`)",
}


def test_every_gate_is_classified():
    gates = sorted(k for k in SCRIPTS if k.startswith("check:") and k != "check:all")
    assert gates == sorted(RECIPE), "classify the new gate's zero input in RECIPE"


@pytest.fixture(scope="module")
def zero(tmp_path_factory):
    """{'pages': tree, 'tree': tree} — the two zero inputs, built once."""
    pages = tmp_path_factory.mktemp("pages")
    archive = subprocess.run(["git", "-C", str(ROOT), "archive", "HEAD"], capture_output=True,
                             check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(pages)], input=archive, check=True)
    shutil.rmtree(pages / "scripts")                    # the gates under test: the working tree's
    shutil.copytree(ROOT / "scripts", pages / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    (pages / "data" / "facts" / "rebuilt.json").write_text("[]\n", encoding="utf-8")
    (pages / "dist").mkdir(exist_ok=True)
    tree = tmp_path_factory.mktemp("tree")
    shutil.copytree(ROOT / "scripts", tree / "scripts",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (tree / "dist").mkdir()
    return {"pages": pages, "tree": tree}


def _params():
    for gate in sorted(RECIPE):
        marks = [pytest.mark.xfail(strict=True, reason=KNOWN_ZERO_PASS[gate])] \
            if gate in KNOWN_ZERO_PASS else []
        yield pytest.param(gate, marks=marks, id=gate)


@pytest.mark.parametrize("gate", _params())
def test_a_gate_refuses_its_zero_input(gate, zero):
    cwd = zero[RECIPE[gate]]
    r = subprocess.run(shlex.split(SCRIPTS[gate]), cwd=cwd, capture_output=True, text=True,
                       timeout=600)
    out = (r.stdout + r.stderr).strip()
    tail = "\n".join(out.splitlines()[-3:])
    assert r.returncode != 0 or "not a pass" in out, \
        f"{gate} exited 0 on {RECIPE[gate]}-zero input:\n{tail}"
