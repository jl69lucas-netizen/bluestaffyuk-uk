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
import re
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
    # A scorecard is named by route ("uk-locations__<slug>-<date>.json") or by slug for a root page.
    scorecards = [p for p in (d / "quality" / "scorecards").glob("*.json")
                  if p.stem.rsplit("-", 3)[0].split("__")[-1] == slug]
    gate = _json(root / "docs" / "reports" / "gate-page" / f"{slug}.json") or {}
    steps = {s.get("step"): s for s in gate.get("steps", [])}
    head = _git(root, "rev-parse", "HEAD")
    gated = gate.get("head") or ""
    # A gate run stays current while only reports and docs changed after it (lessons, entry 21):
    # committing the gate report itself must not make the gate look stale.
    since = _git(root, "diff", "--name-only", gated, "HEAD") if gated and head and gated != head else ""
    at_head = bool(head) and (gated == head or (bool(gated) and _git(root, "merge-base", gated, "HEAD") == gated
                                                 and all(f.startswith("docs/") for f in since.splitlines() if f.strip())))
    ledger = _json(root / "docs" / "reports" / "p5-ledger.json") or {}
    final_ok = any(answers.glob(f"final-approval-{slug}-*.md"))

    def _step(name):
        st = steps.get(name)
        return bool(st) and all(st.get("ok") or [False])
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
        13: (bool(scorecards), f"render scorecard ({len(scorecards)} on disk)" if scorecards else "no render scorecard yet"),
        14: ("impeccable" in run, "page-run record: impeccable"),
        15: ("frontend-design" in run or "frontend_design" in run, "page-run record: frontend-design"),
        16: (_step("hardening"), "static scan clean in the gate report" if _step("hardening") else "static scan not yet clean in a gate report"),
        17: (gate.get("verdict") == "PASS" and bool(gate.get("identical")) and at_head,
             f"gate:page {gate.get('verdict', 'not run')}, runs identical {bool(gate.get('identical'))}, at {str(gate.get('head', ''))[:8]}{'' if at_head else ' (not HEAD)'}"),
        18: ("verification_before_completion" in run, "page-run record: verification before completion"),
        19: (bool(ledger) and slug in json.dumps(ledger), "measurement ledger docs/reports/p5-ledger.json" if ledger else "measurement ledger not written yet"),
        20: (_step("aeo"), "AEO audit clean, both gate runs" if _step("aeo") else "AEO audit not yet clean in a gate report"),
        21: (final_ok, "the breeder approved the page" if final_ok else "waiting on the breeder's final approval"),
    }, {"page_written": built}


PLUGIN_SKILL = re.compile(r"`((?:superpowers|impeccable|frontend-design|compound-engineering):[a-z0-9-]+)`")
BACKTICK = re.compile(r"`@?([a-z][a-z0-9-]*[a-z0-9])(\*)?`")
BSUK_NAME = re.compile(r"(?<![\w./-])@?(bsuk-[a-z0-9_-]*[a-z0-9])(?![\w-])(?!\.\w|/)")
SCRIPT_PATH = re.compile(r"(?<![\w./-])scripts/([\w.-]+\.(?:py|mjs|sh|js))")
NPM_NAME = re.compile(r"\bnpm run (?:(?:-s|--silent) )?([\w:-]+)")


def row_tools(root=ROOT):
    """{row: {skills, agents, scripts, npm}} read from docs/reference/page-run.md.

    A row's text is its table line plus its "### Row N steps" section, so the map shows what
    the run doc names and nothing else; check:workflow already proves each name exists."""
    doc = root / "docs" / "reference" / "page-run.md"
    try:
        lines = doc.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    agents = {p.stem for p in (root / ".claude" / "agents").glob("*.md")}
    skills = {p.name for p in (root / ".claude" / "skills").iterdir() if (p / "SKILL.md").is_file()} \
        if (root / ".claude" / "skills").is_dir() else set()
    text = {n: [] for n, _, _ in ROWS}
    section = None
    for line in lines:
        m = re.match(r"\| (\d+) \|", line)
        if m and int(m.group(1)) in text:
            text[int(m.group(1))].append(line)
            continue
        h = re.match(r"### Row (\d+) steps", line)
        if h:
            section = int(h.group(1))
            continue
        if line.startswith("## ") or line.startswith("### "):
            section = None
        elif section in text:
            text[section].append(line)
    out = {}
    for n, chunk in text.items():
        body = "\n".join(chunk)
        found_skills, found_agents = [], []

        def add(lst, name):
            if name not in lst:
                lst.append(name)
        for name in PLUGIN_SKILL.findall(body):
            add(found_skills, name)
        names = [b + ("*" if star else "") for b, star in BACKTICK.findall(body)] + BSUK_NAME.findall(body)
        names += [stem + "*" for stem in re.findall(r"`([a-z][a-z0-9-]*-)\*`", body)]
        for name in names:
            if name in agents:
                add(found_agents, name)
            elif name in skills:
                add(found_skills, name)
            elif name.endswith("*") and any(s.startswith(name[:-1]) for s in skills):
                add(found_skills, name)
        out[n] = {
            "skills": found_skills,
            "agents": found_agents,
            "scripts": list(dict.fromkeys(SCRIPT_PATH.findall(body))),
            "npm": list(dict.fromkeys(NPM_NAME.findall(body))),
        }
    return out


BUILDERS = {"location": "bsuk-location-page-builder", "comparison": "bsuk-comparison-page-builder",
            "blog": "bsuk-blog-post"}


def page_type(slug, root=ROOT):
    """location, blog or comparison, from the data that knows the slug (page-run.md's builder table)."""
    locs = _json(root / "data" / "locations.json") or []
    if any(isinstance(x, dict) and x.get("slug") == slug for x in locs):
        return "location"
    if (root / "src" / "content" / "blog" / f"{slug}.md").exists():
        return "blog"
    return "comparison"


def status(slug, root=ROOT):
    ev, extra = evidence(slug, root)
    tools = row_tools(root)
    # Rows 1 and 12 name "the builder skill from the table above": show this page's one.
    builder = BUILDERS[page_type(slug, root)]
    for n in (1, 12):
        if n in tools:
            others = set(BUILDERS.values()) - {builder}
            tools[n]["skills"] = [s for s in tools[n]["skills"] if s not in others]
            if builder not in tools[n]["skills"]:
                tools[n]["skills"].append(builder)
    rows, now = [], None
    for n, name, phase in ROWS:
        proved, why = ev[n]
        state = "done" if proved and now is None else ("now" if now is None else "todo")
        if state == "now":
            now = n
        rows.append({"row": n, "name": name, "phase": phase, "state": state,
                     "stop": STOPS.get(n), "evidence": why,
                     "tools": tools.get(n, {"skills": [], "agents": [], "scripts": [], "npm": []})})
    stops_done = sum(1 for r in rows if r["stop"] and r["state"] == "done")
    open_batches = _open_batches(root)
    return {
        "slug": slug,
        "branch": _git(root, "rev-parse", "--abbrev-ref", "HEAD"),
        "commit": _git(root, "log", "-1", "--format=%h %s"),
        "recent": [dict(zip(("hash", "ts", "subject"), line.split("\t", 2)))
                   for line in _git(root, "log", "-6", "--format=%h%x09%ct%x09%s").splitlines() if line.count("\t") == 2],
        "dirty": len([l for l in _git(root, "--no-optional-locks", "status", "--porcelain").splitlines() if l.strip()]),
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
    """The page in progress: the newest page-run record, research board, outline or page board.

    A page-run record is written at row 1 (session open), so a new page takes the map over from
    its first row, before it has a board."""
    found = []
    for sub in ("page-runs", "research-boards", "outlines", "boards"):
        found += [p for p in (root / "data" / sub).glob("*.json") if not p.stem.startswith("_")]
    return max(found, key=lambda p: p.stat().st_mtime).stem if found else None


def main(argv):
    slug = argv[1] if len(argv) > 1 else newest_board()
    if not slug:
        print(json.dumps({"error": "no page board on disk"}))
        return 2
    print(json.dumps(status(slug), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
