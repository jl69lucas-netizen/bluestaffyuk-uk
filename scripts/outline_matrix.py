#!/usr/bin/env python3
"""outline_matrix.py — the outline as a section matrix, STOP 2 of a project 5 page run (row 9).

The user's ruling (2026-09-29): "yes, separate approval, i must see all angles, framework,
keywords, why each competitors rank, full distribution section by section". The research board
(scripts/research_board.py, STOP 1) shows the angles, the frameworks, the keywords and why each
competitor ranks; this is the full distribution, section by section, and the user approves it
on its own, before any component is selected and before the page board is built.

The record is `data/outlines/<slug>.json`. It names its research board, and it is refused
unless that board is approved as it stands. The deliverable carries:

  the approval status line   APPROVED <date> with the answers file, or AWAITING — STOP 2
  the word target            its min–max and its source, and what the matrix sums to
  the heading census         H1–H6 counts over the whole outline; exactly one H1, and no
                             skipped level anywhere (an H4 sits under an H3, never an H2)
  the distribution matrix    one row per section: #, Section with its H2–H6 tree inline,
                             Framework, Words, Keywords (primary / secondary, from the research
                             board's keyword universe), Cat (A mandatory core · B competitor-match
                             · C our moat), Why, Image
  one block per section      the same row laid out, so each has its own copy button
  schema and component notes

A B or C row's Why is grounded: `why_source` points at the research-board finding it comes
from (`serp.results[1]`, `universal_gaps[0]`, `content_gap[2]`, …) and must resolve there; a B
row (competitor-match) cites the SERP or the reverse-engineering table. A section with a
heading carries an image (CLAUDE.md working rule 17) unless it is the FAQ block (`faq: true`).

THE GATE. `--approve --answers <file>` stamps the record's `approval` with its hash;
`approval_refusal(slug)` is what scripts/build_page_board.py (exit 2) and
scripts/board_gate.py (FAIL `outline-unapproved`) call for every new page
(scripts/family_rules.py `is_new_page`): no outline record, no approval, or an outline edited
after its approval refuses the page board.

Usage:
  python3 scripts/outline_matrix.py <slug>                 validate, write the matrix
  python3 scripts/outline_matrix.py <slug> --check         validate only
  python3 scripts/outline_matrix.py <slug> --approve --answers <answers.json>
  options: --record PATH  --out DIR                        (a fixture, or a scratch run)
Writes docs/artifacts/outlines/<slug>.html and .md; publish the .html as an Artifact.
Exit 0 clean · 1 the outline breaks a rule (every problem printed) · 2 no record, no approved
research board, bad call.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _md_artifact as MA  # noqa: E402
import research_board as RB  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECORDS = "data/outlines"
OUT = "docs/artifacts/outlines"
CATS = {"A": "mandatory core", "B": "competitor-match", "C": "our moat"}
# A B row matches a competitor, so it cites one.
B_SOURCES = ("serp", "reverse_engineering")
DASH = ("—", "-", "")


class OutlineError(Exception):
    pass


def record_hash(record):
    body = {k: v for k, v in record.items() if k != "approval"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()[:16]


def approval_state(record):
    a = record.get("approval")
    if not a:
        return "unapproved"
    return "approved" if a.get("record_hash") == record_hash(record) else "stale"


def record_path(slug, root=ROOT):
    if not RB.SLUG.match(slug or ""):
        raise OutlineError(f"not a slug: {slug!r}")
    return pathlib.Path(root) / RECORDS / f"{slug}.json"


def load(path):
    path = pathlib.Path(path)
    if not path.is_file():
        raise OutlineError(f"no outline record at {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise OutlineError(f"{path}: not JSON — {e}") from None


def approval_refusal(slug, root=None):
    """None when the page's outline is approved as it stands; otherwise why the page board
    must wait. STOP 2 of docs/reference/page-run.md."""
    root = ROOT if root is None else root
    try:
        path = record_path(slug, root)
    except OutlineError as e:
        return str(e)
    if not path.is_file():
        return (f"no outline record at {RECORDS}/{slug}.json — the outline (STOP 2) is approved "
                f"before the page board is built (python3 scripts/outline_matrix.py {slug})")
    try:
        record = load(path)
    except OutlineError as e:
        return str(e)
    state = approval_state(record)
    if state == "unapproved":
        return (f"the outline {RECORDS}/{slug}.json is not approved — STOP 2 comes before the page "
                f"board (python3 scripts/outline_matrix.py {slug} --approve --answers <file>)")
    if state == "stale":
        return (f"the outline {RECORDS}/{slug}.json changed after its approval of "
                f"{record['approval'].get('approved_on')} — approve it again (STOP 2)")
    return None


# --- the heading tree ------------------------------------------------------------------

def walk(nodes, parent_level, where, problems, counts):
    for node in nodes or []:
        lvl = node.get("level")
        if not isinstance(lvl, int) or not 1 <= lvl <= 6:
            problems.append(f"{where}: heading {node.get('text')!r} has no level 1–6")
            continue
        if not node.get("text"):
            problems.append(f"{where}: an H{lvl} with no text")
        if parent_level is not None and lvl != parent_level + 1:
            problems.append(f"{where}: H{lvl} {node.get('text')!r} sits under an H{parent_level} — "
                            f"a skipped heading level (it must be an H{parent_level + 1})")
        if parent_level is None and lvl not in (1, 2):
            problems.append(f"{where}: a section opens with an H{lvl} {node.get('text')!r} — "
                            f"sections open with the H1 or an H2")
        counts[lvl] = counts.get(lvl, 0) + 1
        walk(node.get("children"), lvl, where, problems, counts)


def census(record):
    """({level: count}, problems) over every section's tree."""
    problems, counts = [], {}
    for s in record.get("sections", []):
        walk(s.get("headings"), None, f"section {s.get('n')}", problems, counts)
    if counts.get(1, 0) != 1:
        problems.append(f"heading census: exactly one H1, found {counts.get(1, 0)}")
    top = max(counts) if counts else 0
    missing = [lv for lv in range(1, top + 1) if not counts.get(lv)]
    if missing:
        problems.append("heading census: skips " + ", ".join(f"H{lv}" for lv in missing)
                        + f" — levels run H1 to H{top} with none missing")
    return counts, problems


def census_line(counts):
    return " · ".join(f"{counts.get(lv, 0)} H{lv}" for lv in range(1, 7))


def tree_inline(nodes):
    parts = []
    for n in nodes or []:
        s = f"H{n['level']} {n['text']}"
        if n.get("children"):
            s += " (" + " · ".join(tree_inline([c]) for c in n["children"]) + ")"
        parts.append(s)
    return " · ".join(parts)


def tree_list(nodes, depth=0):
    out = []
    for n in nodes or []:
        out.append("  " * depth + f"- **H{n['level']}** {n['text']}")
        out += tree_list(n.get("children"), depth + 1)
    return out


# --- grounding -------------------------------------------------------------------------

def resolve(research, pointer):
    """The research-board value at `serp.results[1]`, `universal_gaps[0]`, `intent.local`…"""
    cur = research
    for part in (pointer or "").split("."):
        m = re.fullmatch(r"([a-z_]+)(?:\[(\d+)\])?", part)
        if not m or not isinstance(cur, dict) or m.group(1) not in cur:
            return None
        cur = cur[m.group(1)]
        if m.group(2) is not None:
            i = int(m.group(2))
            if not isinstance(cur, list) or i >= len(cur):
                return None
            cur = cur[i]
    return cur


def research_for(record, root=ROOT, require_approved=True):
    rel = record.get("research_board")
    if not rel:
        raise OutlineError("research_board: name the page's research-board record")
    path = pathlib.Path(rel)
    path = path if path.is_absolute() else pathlib.Path(root) / path
    try:
        research = RB.load(path)
    except RB.RecordError as e:
        raise OutlineError(f"{e} — the research board (STOP 1) comes before the outline") from None
    state = RB.approval_state(research)
    if require_approved and state != "approved":
        raise OutlineError(f"the research board {rel} is {state} — its picks (STOP 1) are recorded "
                           f"before the outline is written")
    return research


def validate(record, research):
    p = []
    if record.get("slug") != research.get("slug"):
        p.append(f"slug {record.get('slug')!r} does not match the research board's "
                 f"{research.get('slug')!r}")
    wt = record.get("word_target") or {}
    if not (isinstance(wt.get("min"), int) and isinstance(wt.get("max"), int)
            and 0 < wt["min"] <= wt["max"]):
        p.append("word_target: min and max, whole words, min ≤ max")
    if not wt.get("source"):
        p.append("word_target.source: where the target comes from (the query file's median, "
                 "the breeder's answer, …)")
    universe = {k["keyword"] for k in (research.get("keywords") or {}).get("universe", [])}
    secs = record.get("sections") or []
    if not secs:
        p.append("sections: the distribution matrix has no rows")
    total = 0
    seen_n = set()
    for s in secs:
        where = f"section {s.get('n', '?')}"
        if s.get("n") in seen_n or s.get("n") in (None, ""):
            p.append(f"{where}: every row has its own number")
        seen_n.add(s.get("n"))
        if not s.get("section"):
            p.append(f"{where}: no section name")
        if not s.get("framework"):
            p.append(f"{where}: no framework (write — for furniture with no prose)")
        w = s.get("words")
        if not isinstance(w, int) or isinstance(w, bool) or w < 0:
            p.append(f"{where}: words — a whole number")
        else:
            total += w
        cat = s.get("cat")
        if cat not in CATS:
            p.append(f"{where}: no Cat — A (mandatory core), B (competitor-match) or C (our moat)")
        why = s.get("why")
        if why is None or why == "":
            p.append(f"{where}: no Why — a B or C row cites the research board; an A row writes —")
        elif cat in ("B", "C"):
            if why in DASH:
                p.append(f"{where}: a {cat} row's Why is grounded in the research board — not —")
            src = s.get("why_source")
            if not src:
                p.append(f"{where}: a {cat} row names its `why_source` on the research board")
            elif resolve(research, src) in (None, "", []):
                p.append(f"{where}: why_source {src!r} does not resolve on the research board")
            elif cat == "B" and src.split(".")[0].split("[")[0] not in B_SOURCES:
                p.append(f"{where}: a B row (competitor-match) cites the SERP or the "
                         f"reverse-engineering table, not {src!r}")
        has_heading = bool(s.get("headings"))
        kw = s.get("keywords") or {}
        if has_heading and not kw.get("primary"):
            p.append(f"{where}: a section with a heading has a primary keyword")
        for k in (kw.get("primary") or []) + (kw.get("secondary") or []):
            if k not in universe:
                p.append(f"{where}: keyword {k!r} is not in the research board's keyword universe")
        img = s.get("image")
        if has_heading and not s.get("faq") and (not img or img in DASH):
            p.append(f"{where}: a section with a heading carries an image (working rule 17)")
    counts, cp = census(record)
    p += cp
    if isinstance(wt.get("min"), int) and isinstance(wt.get("max"), int) and secs:
        if not wt["min"] <= total <= wt["max"]:
            p.append(f"the matrix sums to {total} words, outside the target "
                     f"{wt['min']}–{wt['max']}")
    return p


# --- rendering -------------------------------------------------------------------------

def status_line(record):
    state, a = approval_state(record), record.get("approval") or {}
    if state == "approved":
        return (f"Status: **APPROVED {a['approved_on']}** (STOP 2 cleared — the outline gate) — "
                f"answers: `{a['answers']}`")
    if state == "stale":
        return (f"Status: **CHANGED AFTER APPROVAL** — approved {a.get('approved_on')}, edited since; "
                f"approve again (STOP 2)")
    return ("Status: **AWAITING APPROVAL — STOP 2** (no component is selected and no page board "
            "is built until this outline is approved)")


def _kw(s):
    kw = s.get("keywords") or {}
    pri, sec = kw.get("primary") or [], kw.get("secondary") or []
    if not pri and not sec:
        return "—"
    return "P: " + (", ".join(pri) or "—") + ("; S: " + ", ".join(sec) if sec else "")


def sections(record, research):
    counts, _ = census(record)
    wt = record["word_target"]
    total = sum(s["words"] for s in record["sections"])
    ra = research.get("approval") or {}
    head = [
        status_line(record),
        f"**Target:** {wt['min']:,}–{wt['max']:,} words (source: {wt['source']}), "
        f"{len(record['sections'])} sections; the matrix sums to {total:,} words.",
        f"**Heading census:** {census_line(counts)} — exactly one H1, no skipped levels.",
        f"**Research board:** `{record['research_board']}` (approved {ra.get('approved_on', '—')}, "
        f"picks `{ra.get('answers', '—')}`).",
    ]
    if record.get("h1"):
        head.insert(1, f"**H1:** {record['h1']}")
    out = [("Status and Target", "\n\n".join(head))]
    rows = [[s["n"], (s["section"] + (" — " + tree_inline(s["headings"]) if s.get("headings") else "")),
             s["framework"], s["words"], _kw(s), s["cat"], s["why"]
             + (f" (from `{s['why_source']}`)" if s.get("why_source") else ""), s.get("image") or "—"]
            for s in record["sections"]]
    out.append(("Distribution Matrix",
                "A = mandatory core · B = competitor-match · C = our moat\n\n"
                + MA.table(["#", "Section", "Framework", "Words", "Keywords", "Cat", "Why", "Image"],
                           rows)))
    for s in record["sections"]:
        body = [f"- **Framework:** {s['framework']} · **Words:** {s['words']} · **Cat:** {s['cat']} "
                f"({CATS[s['cat']]})",
                f"- **Keywords:** {_kw(s)}",
                f"- **Why:** {s['why']}" + (f" (research board: `{s['why_source']}`)" if s.get("why_source") else ""),
                f"- **Image:** {s.get('image') or '—'}"]
        if s.get("headings"):
            body += ["", "**Headings:**", ""] + tree_list(s["headings"])
        out.append((f"§{s['n']} {s['section']}", "\n".join(body)))
    notes = []
    if record.get("schema"):
        notes.append(f"**Schema:** {record['schema']}")
    if record.get("components"):
        notes.append(f"**Components:** {record['components']}")
    if notes:
        out.append(("Schema and Component Notes", "\n\n".join(notes)))
    return out


def build(record, research, out_dir):
    slug = record["slug"]
    secs = sections(record, research)
    heading = f"Section matrix and H1–H6 outline — {record.get('route', slug)}"
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path, md_path = out_dir / f"{slug}.html", out_dir / f"{slug}.md"
    html_path.write_text(MA.page(f"Outline {slug}", "BlueStaffyUK · project 5 · STOP 2",
                                 heading, approval_state(record), record.get("date", ""),
                                 f"{RECORDS}/{slug}.json", secs, f"{slug}-outline.md"),
                         encoding="utf-8")
    md_path.write_text(MA.markdown(heading, secs), encoding="utf-8")
    return html_path, md_path


def approve(record, answers, today=None, root=ROOT):
    path = pathlib.Path(answers)
    if not (path if path.is_absolute() else pathlib.Path(root) / path).is_file():
        raise OutlineError(f"no answers file at {answers} — the approval comes back from the "
                           f"answer board (docs/reference/answer-board/README.md)")
    out = dict(record)
    out["approval"] = {"approved_on": today or datetime.date.today().isoformat(),
                       "answers": str(answers), "record_hash": record_hash(record)}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--record")
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--approve", action="store_true")
    ap.add_argument("--answers")
    a = ap.parse_args(argv)
    try:
        path = pathlib.Path(a.record) if a.record else record_path(a.slug)
        record = load(path)
        if record.get("slug") != a.slug:
            raise OutlineError(f"the record at {path} is for {record.get('slug')!r}, not {a.slug!r}")
        research = research_for(record)
    except OutlineError as e:
        print(f"outline-matrix ERROR {e}")
        return 2
    problems = validate(record, research)
    counts, _ = census(record)
    print(f"outline-matrix {a.slug}: examined {len(record.get('sections', []))} sections, "
          f"{sum(counts.values())} headings ({census_line(counts)}) — {len(problems)} problems")
    for x in problems:
        print(f"  FAIL {x}")
    if problems:
        return 1
    if a.approve:
        if not a.answers:
            print("outline-matrix ERROR --approve needs --answers <the answers file>")
            return 2
        try:
            record = approve(record, a.answers)
        except OutlineError as e:
            print(f"outline-matrix ERROR {e}")
            return 2
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"approved {a.slug} — {record['approval']['answers']} "
              f"(hash {record['approval']['record_hash']})")
    if a.check:
        print(f"state: {approval_state(record)}")
        return 0
    html_path, md_path = build(record, research, pathlib.Path(a.out) if a.out else ROOT / OUT)
    print(f"wrote {html_path} and {md_path} — state: {approval_state(record)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
