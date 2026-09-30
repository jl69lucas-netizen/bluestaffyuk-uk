"""Every `check:*` gate refuses to pass on nothing — and says so.

Learning loop 2026-09-27 (docs/reports/learning-loop-2026-09-27.md, B2 / shortlist #7). Six
brief-parity commits each taught ONE gate not to pass on zero input (the ledger, board_gate
--all, rendered_changes, the hardening scan, targets coverage, the meta guard), and every new
gate re-learned it in review. The render harness has one zero-examined guard for every check;
the Python gates had none in common. This is that guard.

Each gate runs in a throwaway copy of the committed tree (scripts/ from the working tree) in
which ITS OWN input is present but empty — a page map with no pages, a dist/ with no built page,
a registry with no entries, a canvas folder with no fragments, a threads folder with no threads
file — and everything else it reads is intact. The contract is exact: exit non-zero AND print
"not a pass". A traceback is not a refusal (the review of 2026-09-28 found three gates "passing"
this test by crashing on a missing file, and three failing for reasons unrelated to their input).

check:outline and check:queries judge only project 5 (new-family) pages. While no approved
new-family board exists, they examine 0 on this repo by design and must exit 0, or check:all
would fail; their rows are a strict xfail ONLY while that holds (family_rules.is_new_page over
data/boards), so the day the first city board is approved the xfail lifts and they must refuse.
"""
import json
import pathlib
import shlex
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
sys.path.insert(0, str(ROOT / "scripts"))
import family_rules  # noqa: E402


def _write(root, rel, data):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")


def _empty_dir(root, rel):
    p = root / rel
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True)


def _no_rebuilt(root):
    _write(root, "data/facts/rebuilt.json", "[]\n")


def _empty_dist(root):
    _empty_dir(root, "dist")


def _no_pages(root):
    doc = json.loads((root / "data/page-map.json").read_text(encoding="utf-8"))
    doc["pages"] = []
    _write(root, "data/page-map.json", doc)


def _no_competitors(root):
    doc = json.loads((root / "data/competitors.json").read_text(encoding="utf-8"))
    for k in ("competitors", "entries"):
        if isinstance(doc.get(k), list):
            doc[k] = []
    if isinstance(doc.get("_meta"), dict) and "total" in doc["_meta"]:
        doc["_meta"]["total"] = 0
    _write(root, "data/competitors.json", doc)


def _no_reports(root):
    _empty_dir(root, "docs/research/competitors")


def _no_refs(root):
    for rel in ("docs/reference/WORKFLOW.md", "docs/reference/quick-start.md",
                "docs/reference/page-run.md"):
        _write(root, rel, "# Empty\n")


def _no_research(root):
    _write(root, "data/quality/not-fetched-baseline.json", {})
    for rel in ("data/boards", "data/queries", "docs/research"):
        _empty_dir(root, rel)


def _no_threads(root):
    _empty_dir(root, "data/queries/raw")
    subprocess.run([sys.executable, "scripts/thread_ledger.py", "--root", str(root), "--write"],
                   cwd=root, capture_output=True, check=True)


def _no_fragments(root):
    _empty_dir(root, "design/city-canvas/london")


def _no_marker_roots(root):
    for rel in ("CLAUDE.md", "package.json", "scripts/dup_content_audit.py"):
        (root / rel).unlink()
    for rel in ("rules", "docs/reference", "tests/render", ".claude"):
        shutil.rmtree(root / rel, ignore_errors=True)
    _write(root, "data/port-manifest.json", "[]")


#: gate -> how its own input is made present-but-empty. A new check:* script fails
#: test_every_gate_is_classified until it is added here.
SEED = {
    "check:parity": _no_pages,
    "check:facts": _no_rebuilt,
    "check:links": _no_rebuilt,
    "check:verbatim": _no_rebuilt,
    "check:redirects": _empty_dist,
    "check:schema": _empty_dist,
    "check:queries": _no_rebuilt,
    "check:competitors": _no_competitors,
    "check:gaps": _no_reports,
    "check:sitemaps": _empty_dist,
    "check:placeholders": _empty_dist,
    "check:retired": _empty_dist,
    "check:boards": _no_rebuilt,
    "check:markers": _no_marker_roots,
    "check:outline": _no_rebuilt,
    "check:workflow": _no_refs,
    "check:barriers": _no_research,
    "check:threads": _no_threads,
    "check:canvas": _no_fragments,
}


def no_approved_new_family_board(root=ROOT):
    """True while no data/boards/<slug>.json is an approved project 5 (new-family) board."""
    for f in sorted((pathlib.Path(root) / "data" / "boards").glob("*.json")):
        try:
            board = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if board.get("approval") and family_rules.is_new_page(f.stem):
            return False
    return True


#: Pass on zero input by design, but only while the condition holds.
KNOWN_ZERO_PASS = {
    "check:outline": "judges new-family (project 5) pages only, and no approved new-family "
                     "board exists yet",
    "check:queries": "judges built project 5 pages only, and no approved new-family board "
                     "exists yet",
}


def test_every_gate_is_classified():
    gates = sorted(k for k in SCRIPTS if k.startswith("check:") and k != "check:all")
    assert gates == sorted(SEED), "seed the new gate's present-but-empty input in SEED"


@pytest.fixture(scope="module")
def committed(tmp_path_factory):
    base = tmp_path_factory.mktemp("committed")
    archive = subprocess.run(["git", "-C", str(ROOT), "archive", "HEAD"], capture_output=True,
                             check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(base)], input=archive, check=True)
    shutil.rmtree(base / "scripts")
    shutil.copytree(ROOT / "scripts", base / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    if (ROOT / "dist").is_dir():   # every gate but the dist/ ones reads an intact build
        shutil.copytree(ROOT / "dist", base / "dist")
    return base


def _params():
    for gate in sorted(SEED):
        marks = []
        if gate in KNOWN_ZERO_PASS:
            marks = [pytest.mark.xfail(no_approved_new_family_board(), strict=True,
                                       reason=KNOWN_ZERO_PASS[gate])]
        yield pytest.param(gate, marks=marks, id=gate)


@pytest.mark.parametrize("gate", _params())
def test_a_gate_refuses_its_zero_input(gate, committed, tmp_path):
    tree = tmp_path / "tree"
    shutil.copytree(committed, tree, symlinks=True)
    SEED[gate](tree)
    r = subprocess.run(shlex.split(SCRIPTS[gate]), cwd=tree, capture_output=True, text=True,
                       timeout=600)
    out = (r.stdout + r.stderr).strip()
    tail = "\n".join(out.splitlines()[-4:])
    assert "Traceback" not in out, f"{gate} crashed instead of refusing:\n{tail}"
    assert r.returncode != 0 and "not a pass" in out, \
        f"{gate} (exit {r.returncode}) did not refuse its zero input:\n{tail}"


def test_the_xfail_condition_reads_the_boards(tmp_path):
    """No board -> condition holds; an approved new-family board -> it lifts."""
    assert no_approved_new_family_board(tmp_path)
    city = next(s for s in ("blue-staffy-puppies-london", "staffy-puppies-london")
                if family_rules.is_new_page(s))
    _write(tmp_path, f"data/boards/{city}.json", {"approval": None})
    assert no_approved_new_family_board(tmp_path)
    _write(tmp_path, f"data/boards/{city}.json", {"approval": {"by": "user"}})
    assert not no_approved_new_family_board(tmp_path)


#: The same gates with their input MISSING, not empty: each died with a traceback in the first
#: version of this test (a crash is not a refusal).
MISSING = {
    "check:canvas": lambda t: shutil.rmtree(t / "design"),
    "check:gaps": lambda t: shutil.rmtree(t / "docs/research/competitors"),
    "check:workflow": lambda t: (t / "docs/reference/page-run.md").unlink(),
    "check:threads": lambda t: (shutil.rmtree(t / "data/queries/raw", ignore_errors=True),
                                (t / "data/queries/thread-ledger.json").unlink()),
}


@pytest.mark.parametrize("gate", sorted(MISSING))
def test_a_gate_refuses_a_missing_input_without_a_traceback(gate, committed, tmp_path):
    tree = tmp_path / "tree"
    shutil.copytree(committed, tree, symlinks=True)
    MISSING[gate](tree)
    r = subprocess.run(shlex.split(SCRIPTS[gate]), cwd=tree, capture_output=True, text=True,
                       timeout=600)
    out = (r.stdout + r.stderr).strip()
    tail = "\n".join(out.splitlines()[-4:])
    assert "Traceback" not in out, f"{gate} crashed instead of refusing:\n{tail}"
    assert r.returncode != 0, f"{gate} exited 0 with its input missing:\n{tail}"
