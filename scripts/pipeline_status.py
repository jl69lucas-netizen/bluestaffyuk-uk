#!/usr/bin/env python3
"""pipeline_status.py — where a project 5 page stands in docs/reference/page-run.md.

Read-only. Each of the 21 rows is `done` only when a file on disk proves it (the record a
row leaves behind); the first row without proof is `now`; the rest are `todo`. A row whose
proof this repo does not record yet says so in `evidence` rather than being guessed done.
The four STOPs are rows 8, 9, 10 and 11. The Claude Code pipeline mod draws this JSON and
nothing else, so the mod never decides anything itself.

  python3 scripts/pipeline_status.py blue-staffy-puppies-london        # JSON
  python3 scripts/pipeline_status.py                                   # the newest page board
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: (row, short name, phase). Names follow docs/reference/page-run.md's row table.
ROWS = [
    (1, "Session open", "Research"),
    (2, "Target block", "Research"),
    (3, "URL decision", "Research"),
    (4, "Research inventory", "Research"),
    (5, "Competitors and fan-out", "Research"),
    (6, "Keyword deliverables", "Research"),
    (7, "Entities", "Research"),
    (8, "Research board", "Plan"),
    (9, "Outline", "Plan"),
    (10, "Page board", "Plan"),
    (11, "Images and Asset Gate", "Plan"),
    (12, "Build from the outline", "Build"),
    (13, "Render gates", "Build"),
    (14, "Harden: impeccable", "Build"),
    (15, "Harden: frontend-design", "Build"),
    (16, "Static scan", "Build"),
    (17, "Gates, run twice", "Close"),
    (18, "Verification", "Close"),
    (19, "Measurement ledger", "Close"),
    (20, "LLM visibility", "Close"),
    (21, "Deploy and close", "Close"),
]
STOPS = {8: 1, 9: 2, 10: 3, 11: 4}
BOARDS = "https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf"


def _json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _approved(record, key):
    a = (record or {}).get("approval")
    return bool(isinstance(a, dict) and a.get(key))


def evidence(slug, root=ROOT):
    """{row: (proved, evidence text)} from the files a row leaves on disk."""
    d = root / "data"
    run = _json(d / "page-runs" / f"{slug}.json") or {}
    queries = _json(d / "queries" / f"{slug}.json")
    research = _json(d / "research-boards" / f"{slug}.json")
    outline = _json(d / "outlines" / f"{slug}.json")
    board = _json(d / "boards" / f"{slug}.json")
    rebuilt = _json(d / "facts" / "rebuilt.json") or []
    raw = d / "queries" / "raw" / slug
    answers = root / "docs" / "reference" / "answer-board" / "answers"
    scorecards = list((d / "quality" / "scorecards").glob(f"{slug}-*.json"))
    src = next(iter(sorted((root / "src" / "pages").rglob(f"{slug}.astro"))), None)
    if src is None:
        idx = root / "src" / "pages" / slug / "index.astro"
        src = idx if idx.exists() else None
    src_text = src.read_text(encoding="utf-8") if src else ""
    built = bool(src_text) and "data-city-scaffold" not in src_text and "prose-migrated" not in src_text
    asset_gate = any(answers.glob(f"*asset-gate-{slug}*.md"))
    rb = research or {}
    return {
        1: ("session_open" in run, "data/page-runs session_open"),
        2: (queries is not None, "data/queries/<slug>.json"),
        3: (queries is not None and bool(queries.get("route")), "route in the question file"),
        4: (queries is not None, "question file on disk"),
        5: ((raw / "serp_google.json").exists() or (raw / "serp_bing.json").exists(), "raw SERP files"),
        6: (bool(rb.get("keywords")), "research board keywords"),
        7: (bool(rb.get("entities")), "research board entities"),
        8: (_approved(research, "approved_on"), "research board approval"),
        9: (_approved(outline, "approved_on"), "outline approval"),
        10: (_approved(board, "approved_at"), "page board approval"),
        11: (asset_gate, "Asset Gate answers saved"),
        12: (built and slug in rebuilt, "page source rebuilt and registered"),
        13: (bool(scorecards), "render scorecard"),
        14: ("impeccable" in run, "page-run record impeccable"),
        15: ("frontend-design" in run or "frontend_design" in run, "page-run record frontend-design"),
        16: (False, "not recorded on disk yet: run page_hardening_scan.py"),
        17: ("verification" in run, "page-run record verification"),
        18: ("verification" in run, "page-run record verification"),
        19: (False, "not recorded on disk yet: measurement ledger"),
        20: (False, "not recorded on disk yet: aeo audit"),
        21: (False, "the user approves the page"),
    }, {"page_written": built}


def status(slug, root=ROOT):
    ev, extra = evidence(slug, root)
    rows, now = [], None
    for n, name, phase in ROWS:
        proved, why = ev[n]
        state = "done" if proved and now is None else ("now" if now is None else "todo")
        if state == "now":
            now = n
        rows.append({"row": n, "name": name, "phase": phase, "state": state,
                     "stop": STOPS.get(n), "evidence": why})
    stops_done = sum(1 for r in rows if r["stop"] and r["state"] == "done")
    open_batches = _open_batches(root)
    return {
        "slug": slug,
        "branch": _git(root, "rev-parse", "--abbrev-ref", "HEAD"),
        "commit": _git(root, "log", "-1", "--format=%h %s"),
        "rows": rows,
        "now": now,
        "now_name": next((r["name"] for r in rows if r["row"] == now), None),
        "stops_done": stops_done,
        "page_written": extra["page_written"],
        "needs_you": [f"answer board: {b}" for b in open_batches],
        "answer_board": BOARDS,
    }


def _open_batches(root):
    """Batch ids posted from this repo with no saved answers file yet."""
    base = root / "docs" / "reference" / "answer-board"
    saved = {p.name for p in (base / "answers").glob("*")}
    out = []
    for b in sorted((base / "batches").glob("*.json")):
        if not any(name.startswith(b.stem) for name in saved):
            out.append(b.stem)
    return out


def _git(root, *args):
    try:
        return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                              timeout=10).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def newest_board(root=ROOT):
    boards = [p for p in (root / "data" / "boards").glob("*.json") if not p.stem.startswith("_")]
    return max(boards, key=lambda p: p.stat().st_mtime).stem if boards else None


def main(argv):
    slug = argv[1] if len(argv) > 1 else newest_board()
    if not slug:
        print(json.dumps({"error": "no page board on disk"}))
        return 2
    print(json.dumps(status(slug), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
