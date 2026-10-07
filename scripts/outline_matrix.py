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
  the heading census         H1–H6 counts over the whole outline, held to BSUK's own rule
                             (rules/headings.md `heading-hierarchy-outline-gate`): exactly one
                             H1, all six levels, no skipped level anywhere; at least 5 H5 and
                             5 H6, a hard FAIL on every project 5 page — location, comparison
                             and blog (user ruling 2026-09-30, STOP 2 of London), as the source
                             system required on every page; advisory (a WARN on the census
                             line) only on the homepage and the pre-rule location pages
  the distribution matrix    one row per section: #, Section with its H2–H6 tree inline,
                             Framework, Words, Keywords (primary / secondary, from the research
                             board's keyword universe), Cat (A mandatory core · B competitor-match
                             · C our moat), Why, Image
  one block per section      the same row laid out, so each has its own copy button; when
                             the row carries them (all optional, rendering only): its fear,
                             CTA, opener hint, table, H4 image slots, and a body H2's numbered
                             variants with the (Recommended) one's why and trade-off
  page-level sections        when present (optional): opener rule, heading crossover (tool,
                             examined count, hits), heading changes, parked keywords (flagged
                             for the user's decision), planned tests, build notes
  schema and component notes

The rows are held to the research board:
  - framework is one of the board's framework picks or a named standard framework (a
    `.claude/skills/framework-*` skill); `—` only on a row with no H2 or deeper heading
  - a C row's `why_source` is a research finding: `how_we_win[i]`, `content_gap[i]`,
    `universal_gaps[i]` or `serp.results[i].weakness`, fetched (never NOT FETCHED)
  - a B row cites a competitor (`serp.results[i]`, or `reverse_engineering[i]`) whose
    why-it-ranks was fetched
  - `h1` equals the tree's H1
  - every keyword the board's `keywords.distribution` placed in a section sits in that
    section's row (matched by section name), and every row keyword is in the universe
  - a section with a heading carries an image (CLAUDE.md working rule 17) unless it is the
    FAQ block (`faq: true`)

THE GATE. `--approve --answers <file>` reads the answers file (an answer-board answers file
naming this slug and `outline`, never the research board's own answers file) and stamps the
record's `approval` with its hash and the research board's hash. `approval_refusal(slug)` is
what scripts/build_page_board.py (exit 2), scripts/board_gate.py (FAIL `outline-unapproved`),
scripts/board_approve.py and scripts/build_board_previews.py call for every new page
(scripts/family_rules.py `is_new_page`). It refuses when the outline is missing, is another
page's record, is unapproved or edited after its approval, or when its research board is not
approved as it stands or has changed since the outline was approved.

Usage:
  python3 scripts/outline_matrix.py <slug>                 validate, write the matrix
  python3 scripts/outline_matrix.py <slug> --check         validate only
  python3 scripts/outline_matrix.py <slug> --approve --answers <answers.json>
  options: --record PATH  --out DIR                        (a fixture, or a scratch run)
Writes docs/artifacts/outlines/<slug>.html and .md; publish the .html as an Artifact with
capabilities={"downloads": true} (scripts/_md_artifact.py: the .md download needs it).
Exit 0 clean · 1 the outline breaks a rule or is malformed (every problem printed) · 2 no
record, no approved research board, a bad call or a refused approval.
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
import family_rules as FR  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECORDS = "data/outlines"
OUT = "docs/artifacts/outlines"
CATS = {"A": "mandatory core", "B": "competitor-match", "C": "our moat"}
DASH = ("—", "-", "")
C_SOURCES = re.compile(r"^(?:(?:how_we_win|content_gap|universal_gaps)\[\d+\]|serp\.results\[\d+\]\.weakness)$")
B_SOURCES = re.compile(r"^(?:serp\.results\[(\d+)\](?:\.(?:why_ranks|weakness))?|reverse_engineering\[(\d+)\])$")
# rules/headings.md heading-hierarchy-outline-gate: the 5-per-level minimum is advisory on
# these page types only for a page that is not a project 5 page (the homepage, the pre-rule
# location stubs); on a project 5 page it is a hard FAIL (user ruling 2026-09-30, STOP 2 of
# London). family_rules.h5h6_floor_severity is the one predicate.
ADVISORY_MIN_H5H6 = FR.H5H6_ADVISORY_PAGE_TYPES
MIN_H5H6 = 5


class OutlineError(Exception):
    pass


def _norm_fw(name):
    return re.sub(r"[^A-Z0-9]", "", str(name).upper())


def standard_frameworks(root=None):
    """The named frameworks: one per `.claude/skills/framework-*` skill that is a framework."""
    base = pathlib.Path(ROOT if root is None else root) / ".claude/skills"
    names = {d.name[len("framework-"):] for d in base.glob("framework-*") if d.is_dir()}
    names -= {"heading-hierarchy", "library"}
    if not names:                       # a scratch root with no skills: the repo's own list
        names = {d.name[len("framework-"):] for d in (ROOT / ".claude/skills").glob("framework-*")
                 if d.is_dir()} - {"heading-hierarchy", "library"}
    return {_norm_fw(n) for n in names}


def record_hash(record):
    body = {k: v for k, v in record.items() if k != "approval"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False, default=str)
                          .encode("utf-8")).hexdigest()[:16]


def approval_state(record):
    a = record.get("approval") if isinstance(record, dict) else None
    if not isinstance(a, dict) or not a:
        return "unapproved"
    return "approved" if a.get("record_hash") == record_hash(record) else "stale"


def record_path(slug, root=None):
    if not isinstance(slug, str) or not RB.SLUG.match(slug):
        raise OutlineError(f"not a slug: {slug!r}")
    return pathlib.Path(ROOT if root is None else root) / RECORDS / f"{slug}.json"


def load(path):
    path = pathlib.Path(path)
    if not path.is_file():
        raise OutlineError(f"no outline record at {path}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise OutlineError(f"{path}: not JSON — {e}") from None
    if not isinstance(doc, dict):
        raise OutlineError(f"{path}: an outline record is a JSON object")
    return doc


def research_for(record, root=None, require_approved=True):
    root = ROOT if root is None else root
    rel = record.get("research_board") if isinstance(record, dict) else None
    if not isinstance(rel, str) or not rel:
        raise OutlineError("research_board: name the page's research-board record")
    path = pathlib.Path(rel)
    path = path if path.is_absolute() else pathlib.Path(root) / path
    try:
        research = RB.load(path)
    except RB.RecordError as e:
        raise OutlineError(f"{e} — the research board (STOP 1) comes before the outline") from None
    state = RB.approval_state(research, root=root)
    if require_approved and state != "approved":
        raise OutlineError(f"the research board {rel} is {state} — its picks (STOP 1) are recorded "
                           f"before the outline is written")
    return research


def approval_refusal(slug, root=None):
    """None when the page's outline is approved as it stands, on the research board as it
    stands; otherwise why the page board must wait. STOP 2 of docs/reference/page-run.md."""
    root = ROOT if root is None else root
    try:
        path = record_path(slug, root)
    except OutlineError as e:
        return str(e)
    rel = f"{RECORDS}/{slug}.json"
    if not path.is_file():
        return (f"no outline record at {rel} — the outline (STOP 2) is approved before the page "
                f"board is built (python3 scripts/outline_matrix.py {slug})")
    try:
        record = load(path)
    except OutlineError as e:
        return str(e)
    if record.get("slug") != slug:                                   # B1
        return (f"the outline at {rel} is for {record.get('slug')!r}, not {slug!r} — an approval "
                f"clears only its own page")
    state = approval_state(record)
    if state == "unapproved":
        return (f"the outline {rel} is not approved — STOP 2 comes before the page board "
                f"(python3 scripts/outline_matrix.py {slug} --approve --answers <file>)")
    if state == "stale":
        return (f"the outline {rel} changed after its approval of "
                f"{record['approval'].get('approved_on')} — approve it again (STOP 2)")
    try:                                                              # B2
        research = research_for(record, root)
    except OutlineError as e:
        return f"the outline {rel} stands on a research board that is not approved: {e}"
    if research.get("slug") != slug:
        return f"the outline {rel} names the research board of {research.get('slug')!r}"
    if record["approval"].get("research_hash") != RB.current_hash(research, root):
        return (f"the research board {record.get('research_board')} changed after the outline was "
                f"approved — review the outline against it and approve it again (STOP 2)")
    return None


# --- the heading tree ------------------------------------------------------------------

def walk(nodes, parent_level, where, problems, counts, h1s=None):
    if nodes is None:
        return
    if not isinstance(nodes, list):
        problems.append(f"{where}: headings is a list of {{level, text, children}}")
        return
    for node in nodes:
        if not isinstance(node, dict):
            problems.append(f"{where}: a heading is an object {{level, text, children}}")
            continue
        lvl = node.get("level")
        if not isinstance(lvl, int) or isinstance(lvl, bool) or not 1 <= lvl <= 6:
            problems.append(f"{where}: heading {node.get('text')!r} has no level 1–6")
            continue
        if not isinstance(node.get("text"), str) or not node["text"].strip():
            problems.append(f"{where}: an H{lvl} with no text")
        if parent_level is not None and lvl != parent_level + 1:
            problems.append(f"{where}: H{lvl} {node.get('text')!r} sits under an H{parent_level} — "
                            f"a skipped heading level (it must be an H{parent_level + 1})")
        if parent_level is None and lvl not in (1, 2):
            problems.append(f"{where}: a section opens with an H{lvl} {node.get('text')!r} — "
                            f"sections open with the H1 or an H2")
        counts[lvl] = counts.get(lvl, 0) + 1
        if lvl == 1 and h1s is not None:
            h1s.append(node.get("text"))
        walk(node.get("children"), lvl, where, problems, counts, h1s)


def _sections(record):
    secs = record.get("sections") if isinstance(record, dict) else None
    return [s for s in secs if isinstance(s, dict)] if isinstance(secs, list) else []


def census(record, h1s=None):
    """({level: count}, problems) over every section's tree, held to rules/headings.md."""
    problems, counts = [], {}
    for s in _sections(record):
        walk(s.get("headings"), None, f"section {s.get('n')}", problems, counts, h1s)
    if counts.get(1, 0) != 1:
        problems.append(f"heading census: exactly one H1, found {counts.get(1, 0)}")
    top = max(counts) if counts else 0
    missing = [lv for lv in range(1, top + 1) if not counts.get(lv)]
    if missing:
        problems.append("heading census: skips " + ", ".join(f"H{lv}" for lv in missing)
                        + f" — levels run H1 to H{top} with none missing")
    absent = [lv for lv in range(1, 7) if not counts.get(lv)]
    if absent:
        problems.append("heading census: all six levels are required (rules/headings.md "
                        "heading-hierarchy-outline-gate) — no " + ", ".join(f"H{lv}" for lv in absent))
    return counts, problems


def _h5h6_sev(record):
    return FR.h5h6_floor_severity(record.get("page_type"), record.get("slug"))


def _h5h6_short(record, counts):
    return [f"H{lv}" for lv in (5, 6) if counts.get(lv, 0) < MIN_H5H6]


def warnings(record):
    """Advisory findings: the 5-per-level H5/H6 minimum on the homepage or a pre-rule
    location page. On a project 5 page the same shortfall is a problem, not a warning."""
    counts, _ = census(record)
    short = _h5h6_short(record, counts)
    if short and _h5h6_sev(record) == "WARN":
        return [f"heading census: fewer than {MIN_H5H6} " + " and ".join(short)
                + f" — advisory on a pre-rule {record.get('page_type')} page (rules/headings.md, "
                  "2026-09-09); never add a heading to hit the count"]
    return []


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


def _deep(nodes):
    """True when the tree holds an H2 or deeper heading."""
    return any(isinstance(n, dict) and (n.get("level", 0) >= 2 or _deep(n.get("children")))
               for n in (nodes if isinstance(nodes, list) else []))


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


def _serp_row_for(research, src):
    m = B_SOURCES.match(src or "")
    if not m:
        return None
    results = RB._l(RB._d(research.get("serp")).get("results"))
    if m.group(1) is not None:
        i = int(m.group(1))
        return results[i] if i < len(results) and isinstance(results[i], dict) else None
    rows = RB._l(research.get("reverse_engineering"))
    i = int(m.group(2))
    if i >= len(rows) or not isinstance(rows[i], dict):
        return None
    url = RB._norm_url(rows[i].get("url"))
    return next((r for r in results if isinstance(r, dict) and RB._norm_url(r.get("url")) == url), None)


def validate(record, research, root=None):
    """Every problem with the outline, as strings. A malformed shape is a problem (B8)."""
    if not isinstance(record, dict):
        return ["the outline record is not a JSON object"]
    p = []
    try:
        _validate(record, research if isinstance(research, dict) else {}, root, p)
    except (TypeError, AttributeError, KeyError, ValueError) as e:
        p.append(f"malformed outline: {type(e).__name__}: {e}")
    return p


def _validate(record, research, root, p):
    if record.get("page_type") not in RB.PAGE_TYPES:
        p.append(f"page_type: one of {', '.join(RB.PAGE_TYPES)} — the census's H5/H6 rule "
                 f"depends on it")
    if record.get("slug") != research.get("slug"):
        p.append(f"slug {record.get('slug')!r} does not match the research board's "
                 f"{research.get('slug')!r}")
    wt = record.get("word_target")
    if not isinstance(wt, dict):
        p.append("word_target: an object {min, max, source}")
        wt = {}
    wmin, wmax = wt.get("min"), wt.get("max")
    target_ok = RB._int(wmin) and RB._int(wmax) and 0 < wmin <= wmax
    if not target_ok:
        p.append("word_target: min and max, whole words, min ≤ max")
    if not RB._s(wt.get("source")):
        p.append("word_target.source: where the target comes from (the query file's median, "
                 "the breeder's answer, …)")
    kw = RB._d(research.get("keywords"))
    universe = {k["keyword"] for k in RB._l(kw.get("universe"))
                if isinstance(k, dict) and RB._s(k.get("keyword"))}
    picks = {_norm_fw(g.get("recommended")) for g in RB._l(research.get("frameworks"))
             if isinstance(g, dict) and RB._s(g.get("recommended"))}
    allowed_fw = picks | standard_frameworks(root)
    raw = record.get("sections")
    if not isinstance(raw, list) or not raw:
        p.append("sections: the distribution matrix has no rows (a list of section objects)")
        raw = []
    if any(not isinstance(s, dict) for s in raw):
        p.append("sections: every row is an object")
    total, seen_n, by_name = 0, set(), {}
    for s in _sections(record):
        where = f"section {s.get('n', '?')}"
        n = s.get("n")
        if not isinstance(n, (str, int)) or n in ("", None) or n in seen_n:
            p.append(f"{where}: every row has its own number")
        else:
            seen_n.add(n)
        name = s.get("section")
        if not RB._s(name):
            p.append(f"{where}: no section name")
        else:
            by_name[name.strip().lower()] = s
        heads = s.get("headings")
        if heads is not None and not isinstance(heads, list):
            p.append(f"{where}: headings is a list")
            heads = []
        fw = s.get("framework")
        if not RB._s(fw):
            p.append(f"{where}: no framework (write — for furniture with no H2)")
        elif fw.strip() in DASH:
            if _deep(heads):
                p.append(f"{where}: a row with an H2 names its framework")
        elif _norm_fw(fw) not in allowed_fw:
            p.append(f"{where}: framework {fw!r} is neither a research-board pick nor a named "
                     f"standard framework (.claude/skills/framework-*)")
        w = s.get("words")
        if not RB._int(w) or w < 0:
            p.append(f"{where}: words — a whole number")
        else:
            total += w
        cat = s.get("cat")
        if cat not in CATS:
            p.append(f"{where}: no Cat — A (mandatory core), B (competitor-match) or C (our moat)")
        why = s.get("why")
        if not isinstance(why, str) or why == "":
            p.append(f"{where}: no Why — a B or C row cites the research board; an A row writes —")
        elif cat in ("B", "C"):
            if why.strip() in DASH:
                p.append(f"{where}: a {cat} row's Why is grounded in the research board — not —")
            src = s.get("why_source")
            if not RB._s(src):
                p.append(f"{where}: a {cat} row names its `why_source` on the research board")
            elif cat == "C":
                value = resolve(research, src)
                if not C_SOURCES.match(src):
                    p.append(f"{where}: a C row (our moat) cites a research finding — how_we_win[i], "
                             f"content_gap[i], universal_gaps[i] or serp.results[i].weakness — not {src!r}")
                elif not RB._s(value) or RB.is_nf(value):
                    p.append(f"{where}: a C row's why_source {src!r} does not resolve to a fetched finding")
            else:
                row = _serp_row_for(research, src)
                if row is None:
                    p.append(f"{where}: a B row (competitor-match) cites a competitor — "
                             f"serp.results[i] or reverse_engineering[i] — and {src!r} is not one")
                elif not RB._s(row.get("why_ranks")) or RB.is_nf(row.get("why_ranks")):
                    p.append(f"{where}: a B row cites a competitor with a fetched why-it-ranks; "
                             f"{src!r} is NOT FETCHED")
        kws = s.get("keywords", {})
        if kws is None:
            kws = {}
        if not isinstance(kws, dict):
            p.append(f"{where}: keywords is an object {{primary, secondary}}")
            kws = {}
        pri, sec = kws.get("primary") or [], kws.get("secondary") or []
        if not isinstance(pri, list) or not isinstance(sec, list):
            p.append(f"{where}: keywords.primary and keywords.secondary are lists")
            pri, sec = [], []
        if heads and not pri:
            p.append(f"{where}: a section with a heading has a primary keyword")
        for k in pri + sec:
            if k not in universe:
                p.append(f"{where}: keyword {k!r} is not in the research board's keyword universe")
        img = s.get("image")
        if heads and not s.get("faq") and (not RB._s(img) or img.strip() in DASH):
            p.append(f"{where}: a section with a heading carries an image (working rule 17)")
    h1s = []
    counts, cp = census(record, h1s)
    p += cp
    short = _h5h6_short(record, counts)
    if short and _h5h6_sev(record) == "FAIL":
        p.append(f"heading census: at least {MIN_H5H6} H5 and {MIN_H5H6} H6 on a project 5 "
                 f"{record.get('page_type')} page (rules/headings.md, user ruling 2026-09-30) — "
                 "short: " + ", ".join(short))
    if record.get("h1") is not None and h1s and record.get("h1") != h1s[0]:
        p.append(f"h1 {record.get('h1')!r} is not the tree's H1 {h1s[0]!r}")
    if target_ok and raw and not wmin <= total <= wmax:
        p.append(f"the matrix sums to {total} words, outside the target {wmin}–{wmax}")
    # the research board placed each keyword in a section; the outline keeps it there
    for i, d in enumerate(RB._l(kw.get("distribution"))):
        if not isinstance(d, dict) or not RB._s(d.get("section")):
            continue
        row = by_name.get(d["section"].strip().lower())
        placed = [k for k in RB._l(d.get("primary")) + RB._l(d.get("secondary")) if RB._s(k)]
        if row is None:
            p.append(f"the research board places {placed} in section {d['section']!r}, and the "
                     f"outline has no row of that name")
            continue
        have = RB._d(row.get("keywords"))
        mine = set(RB._l(have.get("primary"))) | set(RB._l(have.get("secondary")))
        for k in placed:
            if k not in mine:
                p.append(f"keyword {k!r} is placed in section {d['section']!r} on the research board "
                         f"and missing from that row")


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


def _txt(v):
    """A value of any shape as one line of markdown — the optional fields are free-form."""
    if v is None:
        return "—"
    if isinstance(v, str):
        return v or "—"
    if isinstance(v, list):
        return "; ".join(_txt(x) for x in v) or "—"
    if isinstance(v, dict):
        return " · ".join(f"{k}: {_txt(x)}" for k, x in v.items()) or "—"
    return str(v)


def _row_extras(s):
    """The optional per-row fields — fear, CTA, opener hint, table, H4 image slots — as
    bullet lines; none of them is required, and a row without them adds nothing."""
    out = []
    if s.get("fear"):
        out.append(f"- **Fear:** {_txt(s['fear'])}"
                   + (f" (source: `{_txt(s['fear_source'])}`)" if s.get("fear_source") else ""))
    cta = s.get("cta")
    if isinstance(cta, dict) and cta:
        line = f"- **CTA:** [{_txt(cta.get('anchor'))}]({_txt(cta.get('href'))})"
        bits = [f"{k}: {_txt(cta[k])}" for k in ("anchor_type", "placement") if cta.get(k)]
        if bits:
            line += " — " + " · ".join(bits)
        if cta.get("note"):
            line += f". {_txt(cta['note'])}"
        out.append(line)
    elif cta:
        out.append(f"- **CTA:** {_txt(cta)}")
    if s.get("opener"):
        out.append(f"- **Opener hint:** {_txt(s['opener'])}")
    t = s.get("table")
    if isinstance(t, dict) and t:
        out.append(f"- **Table** ({_txt(t.get('shape', 'table'))}"
                   + (f", under {_txt(t['under'])}" if t.get("under") else "") + "):")
        if t.get("caption"):
            out.append(f"  - Caption: {_txt(t['caption'])}")
        cols = t.get("columns")
        if isinstance(cols, list) and cols:
            out.append("  - Columns: " + "; ".join(
                (f"{_txt(c.get('label'))} ← {_txt(c.get('source'))}" if isinstance(c, dict) else _txt(c))
                for c in cols))
        for k in ("rows", "mobile", "why", "note"):
            if t.get(k):
                out.append(f"  - {k.capitalize()}: {_txt(t[k])}")
    elif t:
        out.append(f"- **Table:** {_txt(t)}")
    imgs = s.get("h4_images")
    if isinstance(imgs, list) and imgs:
        out.append("- **H4 image slots:**")
        for im in imgs:
            if isinstance(im, dict):
                line = f"  - H4 \"{_txt(im.get('h4'))}\": `{_txt(im.get('image'))}`"
                if im.get("alt"):
                    line += f" — alt: \"{_txt(im['alt'])}\""
                if im.get("alt_source"):
                    line += f" ({_txt(im['alt_source'])})"
                out.append(line)
            else:
                out.append(f"  - {_txt(im)}")
    return out


def _variants_block(s):
    """A body H2's alternative wordings, numbered, the recommended one marked — the user picks
    among them at STOP 2."""
    vs = s.get("variants")
    if not isinstance(vs, list) or not vs:
        return []
    out = ["", "**H2 variants** (pick one at STOP 2):", ""]
    for i, v in enumerate(vs, 1):
        if not isinstance(v, dict):
            out.append(f"{i}. {_txt(v)}")
            continue
        line = f"{i}. {_txt(v.get('text'))}"
        if v.get("recommended"):
            line += " **(Recommended)**"
        bits = []
        if v.get("keywords"):
            bits.append("keywords: " + _txt(v["keywords"]))
        if v.get("related_term"):
            bits.append("related term: " + _txt(v["related_term"]))
        if bits:
            line += " — " + " · ".join(bits)
        out.append(line)
        if v.get("why"):
            out.append(f"   - Why: {_txt(v['why'])}")
        if v.get("trade_off"):
            out.append(f"   - Trade-off: {_txt(v['trade_off'])}")
    return out


def _page_level(record):
    """The optional outline-level sections: opener rule, heading crossover, heading changes,
    parked keywords, planned tests and build notes."""
    out = []
    if record.get("opener_rule"):
        out.append(("Opener Rule", _txt(record["opener_rule"])))
    hc = record.get("header_crossover")
    if isinstance(hc, dict) and hc:
        lines = []
        for k in ("date", "tool", "corpus"):
            if hc.get(k):
                lines.append(f"- **{k.capitalize()}:** {_txt(hc[k])}")
        ex = hc.get("examined")
        if ex:
            lines.append(f"- **Examined:** {_txt(ex)}")
        hits = hc.get("hits") if isinstance(hc.get("hits"), list) else []
        counts = [f"{k.replace('_', ' ')}: {hc[k]}" for k in ("body_hits", "faq_hits") if k in hc]
        lines.append(f"- **Hits:** {len(hits)}" + (f" ({', '.join(counts)})" if counts else ""))
        if hc.get("fixed_before_record"):
            lines.append(f"- **Fixed before the record:** {_txt(hc['fixed_before_record'])}")
        body = "\n".join(lines)
        if hits:
            rows = [[h.get("severity", "—"), h.get("heading", "—"), h.get("kind", "—"),
                     _txt(h.get("shingles")), h.get("with_page", "—"), h.get("with_heading", "—"),
                     h.get("note", "—")] if isinstance(h, dict) else ["—", _txt(h), "", "", "", "", ""]
                    for h in hits]
            body += "\n\n" + MA.table(["Severity", "Heading", "Kind", "Shingles", "With page",
                                        "With heading", "Note"], rows)
        out.append(("Heading Crossover", body))
    elif hc:
        out.append(("Heading Crossover", _txt(hc)))
    ch = record.get("heading_changes")
    if isinstance(ch, list) and ch:
        rows = [[c.get("row", "—"), f"H{c['level']}" if c.get("level") else "—", c.get("was", "—"),
                 c.get("now", "—"), c.get("reason", "—")] if isinstance(c, dict)
                else ["—", "—", "—", _txt(c), "—"] for c in ch]
        out.append(("Heading Changes", MA.table(["Row", "Level", "Was", "Now", "Reason"], rows)))
    pk = record.get("parked_keywords")
    if isinstance(pk, list) and pk:
        lines = ["**NEEDS YOUR DECISION** — these keywords are parked, not placed on the page:", ""]
        for k in pk:
            if isinstance(k, dict):
                lines.append(f"- **{_txt(k.get('keyword'))}** — {_txt(k.get('status'))}")
                for f in ("seen_in", "decision"):
                    if k.get(f):
                        lines.append(f"  - {f.replace('_', ' ').capitalize()}: {_txt(k[f])}")
            else:
                lines.append(f"- {_txt(k)}")
        out.append(("Parked Keywords — Your Decision", "\n".join(lines)))
    for key, title in (("planned_tests", "Planned Tests"), ("build_notes", "Build Notes")):
        v = record.get(key)
        if isinstance(v, list) and v:
            out.append((title, "\n".join(f"- {_txt(x)}" for x in v)))
        elif v:
            out.append((title, _txt(v)))
    return out


def sections(record, research):
    counts, _ = census(record)
    wt = record["word_target"]
    total = sum(s["words"] for s in record["sections"])
    ra = research.get("approval") or {}
    warn = warnings(record)
    census_md = (f"**Heading census:** {census_line(counts)} — exactly one H1, all six levels, no "
                 f"skipped level (BSUK: rules/headings.md `heading-hierarchy-outline-gate`). At least "
                 f"{MIN_H5H6} H5 and {MIN_H5H6} H6 is a hard rule on every project 5 page — location, "
                 f"comparison and blog (user ruling 2026-09-30) — as the source system required on "
                 f"every page; it stays advisory only on the homepage and the pre-rule location "
                 f"pages.")
    if warn:
        census_md += "\n\n" + "\n".join(f"- WARN {w}" for w in warn)
    head = [
        status_line(record),
        f"**Target:** {wt['min']:,}–{wt['max']:,} words (source: {wt['source']}), "
        f"{len(record['sections'])} sections; the matrix sums to {total:,} words.",
        census_md,
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
        body += _row_extras(s)
        if s.get("headings"):
            body += ["", "**Headings:**", ""] + tree_list(s["headings"])
        body += _variants_block(s)
        out.append((f"§{s['n']} {s['section']}", "\n".join(body)))
    out += _page_level(record)
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
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path, md_path = out_dir / f"{slug}.html", out_dir / f"{slug}.md"
    html_path.write_text(MA.page(f"Outline {slug}", "BlueStaffyUK · project 5 · STOP 2",
                                 heading, approval_state(record), record.get("date", ""),
                                 f"{RECORDS}/{slug}.json", secs, f"{slug}-outline.md"),
                         encoding="utf-8")
    md_path.write_text(MA.markdown(heading, secs), encoding="utf-8")
    return html_path, md_path


def approve(record, answers, today=None, root=None):
    """The record with its approval stamped, with the research board's hash. Refuses an
    unapproved research board, the research board's own answers file, and a file that is not
    this page's STOP 2 answers (B3)."""
    root = ROOT if root is None else root
    research = research_for(record, root)
    ra = research.get("approval") or {}
    if pathlib.PurePath(str(answers)).as_posix().lstrip("./") == \
            pathlib.PurePath(str(ra.get("answers", ""))).as_posix().lstrip("./"):
        raise OutlineError(f"{answers} is the same answers file as the research board's approval — "
                           f"the outline (STOP 2) is approved on its own batch")
    try:
        RB.check_answers(answers, record.get("slug"), "outline", root)
    except RB.RecordError as e:
        raise OutlineError(str(e)) from None
    out = dict(record)
    out["approval"] = {"approved_on": today or datetime.date.today().isoformat(),
                       "answers": str(answers), "record_hash": record_hash(record),
                       "research_hash": RB.current_hash(research, root)}
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
    print(f"outline-matrix {a.slug}: examined {len(_sections(record))} sections, "
          f"{sum(counts.values())} headings ({census_line(counts)}) — {len(problems)} problems")
    for x in problems:
        print(f"  FAIL {x}")
    for w in warnings(record) if not problems else []:
        print(f"  WARN {w}")
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
    print("  " + MA.publish_hint(html_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
