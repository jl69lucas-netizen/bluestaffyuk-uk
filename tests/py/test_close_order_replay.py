"""The documented close order, replayed end to end in a throwaway git repository.

Learning loop 2026-09-27 (docs/reports/learning-loop-2026-09-27.md, B1 / shortlist #4). Nine
brief-parity commits repaired "gated on a dirty tree" and "the close order reads STALE on a clean
run". Each round was unit-tested one function at a time (dirty_tracked, git_head, the M8
staleness rule), and each next round found the interaction those tests could not see: the tree
the DOCUMENTED ORDER leaves behind, where the build has rewritten two tracked files. The bug lived
at the level of the sequence, so this test runs the sequence.

docs/reference/page-run.md row 21: `npm run -s build` -> render -> `npm run gate:page -- <slug>`
-> `rendered_changes.py --json` -> `measurement_ledger.py <project>` -> commit. Here the build is
a stub that does what the real prebuild and postbuild do to TRACKED files — it rewrites
data/page-dates.json (same routes, new bytes) and public/search-index.json — and writes the
git-ignored dist/. The gate report is stamped with the real `gate_page.git_head` and
`gate_page.page_hash`, and the real `measurement_ledger` M8 and M10 read it.

CLOSE_ORDER_SCRIPTS=<dir> replays the sequence against another revision's scripts/ (the proof
that this test fails at 769465d, before dd29aec set the build outputs aside).
"""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = pathlib.Path(os.environ.get("CLOSE_ORDER_SCRIPTS") or ROOT / "scripts")
sys.path.insert(0, str(SCRIPTS))

import gate_page as GP  # noqa: E402
import measurement_ledger as ML  # noqa: E402
import rendered_changes as RC  # noqa: E402


def _head_module(name):
    """The stub build derives page dates with THIS revision's generate_page_dates, whatever
    CLOSE_ORDER_SCRIPTS names: the build is the fixture, the close-order scripts are under test."""
    spec = importlib.util.spec_from_file_location(f"_close_order_{name}", ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GPD = _head_module("generate_page_dates")
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
KEY, ROUTE = "newtown", "uk-locations/newtown"
CHECKS_TS = "register({ id: 'layout-min-font-size', family: 'LAYOUT', severity: 'blocking', describe: 'x' });\n"


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, env=GIT_ENV,
                          capture_output=True, text=True).stdout.strip()


def commit(root, message):
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", message)
    return git(root, "rev-parse", "HEAD")


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")


def sources(root, body="city"):
    write(root / ".gitignore", "dist/\ndocs/reports/\n")
    write(root / "src/pages/uk-locations/[slug].astro", f"---\n---\n<main>{body}</main>\n")
    write(root / "data/locations.json", [{"slug": KEY, "region": "north"}])
    write(root / "tests/render/checks/all.ts", CHECKS_TS)
    write(root / "tests/render/targets.json", {
        "families_by_page_type": {"location": ["LAYOUT"]}, "deferred_checks": {},
        "pages": [{"slug": ROUTE}]})
    write(root / "data/quality/rule-index.json", {"rules": [{"id": "a", "enforced": "test"}]})
    write(root / "data/quality/rework-ledger.json", {"windows": []})


def build(root, body="city"):
    """What `npm run -s build` does to the tree: prebuild re-derives data/page-dates.json from
    committed history (the same routes, written afresh), postbuild rewrites
    public/search-index.json from dist/, and the pages land in git-ignored dist/."""
    routes = GPD.derive_routes(root)
    write(root / "data/page-dates.json", json.dumps({"routes": routes}, indent=2) + "\n")
    write(root / "dist" / ROUTE / "index.html", f"<main>{body}</main>")
    write(root / "public/search-index.json", {"pages": [ROUTE], "body": body})


def gate(root):
    """`npm run gate:page -- newtown`, as far as the ledger reads it: the report's `head` and
    `page_hash` are stamped by gate_page's own functions."""
    steps = ("dup-body", "dup-headers")
    rep = {"head": GP.git_head(root), "page_hash": GP.page_hash(ROUTE, root), "runs": 2,
           "verdict": "PASS", "identical": True,
           "steps": [{"step": s, "ok": [True, True], "problems": [0, 0], "identical": True}
                     for s in steps],
           "evidence": [[{"step": s, "evidence": {"pages": 40, "findings": []}} for s in steps]
                        for _ in range(2)]}
    write(root / "docs/reports/gate-page" / f"{KEY}.json", rep)
    return rep


def ledger_rows(root):
    led = ML.ledger("p5", [KEY], root)
    return {r["id"]: r for r in led["rows"]}


@pytest.fixture
def tree(tmp_path, monkeypatch):
    sources(tmp_path)
    git(tmp_path, "init", "-q")
    commit(tmp_path, "sources")
    build(tmp_path)                                     # the committed state of the build outputs
    commit(tmp_path, "the build's tracked outputs, as the last close committed them")
    monkeypatch.setattr(RC, "ROOT", tmp_path)
    return tmp_path


def test_the_documented_close_order_is_clean_and_current(tree):
    build(tree)                                         # build: rewrites two tracked files
    (tree / "data/page-dates.json").write_text(
        (tree / "data/page-dates.json").read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert git(tree, "status", "--porcelain", "--untracked-files=no"), \
        "the stub build must leave the two tracked outputs rewritten, as the real one does"
    rep = gate(tree)                                    # gate:page
    assert not rep["head"].endswith("-dirty"), rep["head"]
    assert not RC.head_sha().endswith("-dirty")         # rendered_changes.py --json
    rows = ledger_rows(tree)                            # measurement_ledger.py
    assert (rows["M8"]["status"], rows["M10"]["status"]) == ("PASS", "PASS"), \
        (rows["M8"], rows["M10"])
    commit(tree, "close")                               # the close's commit carries the outputs
    assert git(tree, "status", "--porcelain", "--untracked-files=no") == ""


def test_a_source_changed_after_gating_reads_stale(tree):
    build(tree)
    gate(tree)
    sources(tree, body="city, edited")                  # a page change after the gate …
    commit(tree, "edit")
    build(tree, body="city, edited")                    # … committed and rebuilt
    rows = ledger_rows(tree)
    assert rows["M8"]["status"] == "STALE", rows["M8"]
    assert rows["M10"]["status"] == "STALE", rows["M10"]


def test_gating_before_the_commit_reads_stale(tree):
    sources(tree, body="city, uncommitted")             # the page is edited …
    build(tree, body="city, uncommitted")
    rep = gate(tree)                                    # … and gated before it is committed
    assert rep["head"].endswith("-dirty"), rep["head"]
    rows = ledger_rows(tree)
    assert rows["M8"]["status"] == "STALE", rows["M8"]
    assert rows["M10"]["status"] == "STALE", rows["M10"]
