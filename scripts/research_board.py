#!/usr/bin/env python3
"""research_board.py — the research board, STOP 1 of a project 5 page run (page-run row 8).

The user's ruling (2026-09-29): "i must see all angles, framework, keywords, why each
competitors rank, full distribution section by section". This script builds the research
board from its record, `data/research-boards/<slug>.json`, and the page's query file,
`data/queries/<slug>.json` (row 5), and refuses a record that does not carry the whole
research deliverable:

  1  SERP snapshot   every competitor in the top 5 on Google or Bing (the query file's
                     `competitors`) with its type, WHY IT RANKS and its WEAKNESS (our wedge),
                     and a structural read of the SERP
  2  search intent   dominant, secondary, emotional and local layers
  3  reverse engineering   per competitor: words, heading counts, tables, FAQ, byline,
                     schema; then the universal gaps every fetched competitor misses
  4  owner language  real quotes, each with its source URL
  5  query fan-out   PAA, threads, the LLM-intel file
  6  why competitors rank (summary) · 7 how we win · 8 the content gap (build list)
  9  entities · 10 three angles · 11 two or three strategy directions · 12 the framework
                     options per section group — exactly one (Recommended) per choice, with
                     its why and trade-off (CLAUDE.md working rule 4)
  13 the keyword universe by intent · 14 its distribution, section by section

NOTHING IS INFERRED (working rule 9). A value is either grounded — a competitor's why and
weakness carry an `evidence` (the saved fetch, or the URL read) — or it is written
`NOT FETCHED — <barrier>`, naming what was tried and what stopped it. A bare `NOT FETCHED`
is refused. The two fields the query file does record are read from it, never retyped: a
competitor's `words`, and its H2 count (`h2_clean`) when the record gives no heading census.

THE APPROVAL. The user's picks come back from the answer board as
`docs/reference/answer-board/answers/<batchId>-<date>.json`; `--approve --answers <file>`
records them in the record's `approval` with the record's hash, so an edit after approval
reads as stale and must be approved again. scripts/outline_matrix.py refuses to build or
approve an outline whose research board is not approved as it stands.

Usage:
  python3 scripts/research_board.py <slug>                 validate, write the board
  python3 scripts/research_board.py <slug> --check         validate only
  python3 scripts/research_board.py <slug> --approve --answers <answers.json>
  options: --record PATH  --queries PATH  --out DIR        (a fixture, or a scratch run)
Writes docs/artifacts/research/<slug>.html and .md; publish the .html as an Artifact.
Exit 0 clean · 1 the record is incomplete (every problem printed) · 2 no record, bad call.
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

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECORDS = "data/research-boards"
OUT = "docs/artifacts/research"
TOP_N = 5
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# `NOT FETCHED — <barrier>`: the barrier is at least two words (scripts/not_fetched_lint.py).
NOT_FETCHED = re.compile(r"^NOT FETCHED\s*(?:—|–|:)\s*(\S+\s+\S+.*)$")
PAGE_TYPES = ("location", "comparison", "blog")
INTENTS = ("transactional", "commercial", "informational", "navigational", "local")

# How to fetch what a record leaves NOT FETCHED: page-run rows 4–7 by field.
FETCH = {
    "serp": "`bsuk-query-augmentation` <slug> (row 5): the top 5 on Google and Bing, merged",
    "why_ranks": "`bsuk-framework-agent` on the competitor URL (row 5), reading the saved page",
    "weakness": "`bsuk-framework-agent` on the competitor URL (row 5), reading the saved page",
    "words": "`python3 scripts/query_augment.py --competitor-metrics <slug>` (row 5 step 3)",
    "headings": "`python3 scripts/query_augment.py --extract-h2 <file>` for H2s; H1 and H3–H6 "
                "by reading the saved page (`bsuk-framework-agent`)",
    "tables": "`bsuk-framework-agent` on the saved page",
    "faq": "`bsuk-framework-agent` on the saved page",
    "byline": "`bsuk-framework-agent` on the saved page",
    "schema": "`bsuk-framework-agent` on the saved page (its JSON-LD types)",
    "owner_language": "`bsuk-reddit-threads` (row 5 step 4), quoting each thread with its URL",
    "paa": "`bsuk-paa-agent` for the primary keyword",
    "threads": "`bsuk-reddit-threads` against `python3 scripts/thread_ledger.py --known <url>`",
    "llm_intel": "`bsuk-llm-keyword-intel` <slug> (row 5 step 5)",
    "volume": "`python3 scripts/keyword_metrics.py <slug>` or the keyword tool the spend guard allows",
}


class RecordError(Exception):
    pass


def is_nf(value):
    return isinstance(value, str) and value.startswith("NOT FETCHED")


def nf_ok(value):
    return isinstance(value, str) and bool(NOT_FETCHED.match(value))


def record_hash(record):
    body = {k: v for k, v in record.items() if k != "approval"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()[:16]


def approval_state(record):
    """'approved', 'stale' (edited after approval) or 'unapproved'."""
    a = record.get("approval")
    if not a:
        return "unapproved"
    return "approved" if a.get("record_hash") == record_hash(record) else "stale"


def record_path(slug, root=ROOT):
    if not SLUG.match(slug or ""):
        raise RecordError(f"not a slug: {slug!r}")
    return root / RECORDS / f"{slug}.json"


def load(path):
    path = pathlib.Path(path)
    if not path.is_file():
        raise RecordError(f"no research-board record at {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RecordError(f"{path}: not JSON — {e}") from None


def top_competitors(queries, n=TOP_N):
    """The query file's competitors in the top n on either engine, in pool order."""
    def pos(v):
        return v if isinstance(v, int) else 99
    return [c for c in queries.get("competitors", [])
            if min(pos(c.get("google_pos")), pos(c.get("bing_pos"))) <= n]


def _norm_url(u):
    return (u or "").strip().rstrip("/").lower()


def _grounded(where, value, evidence, problems, root):
    """A value is `NOT FETCHED — <barrier>`, or text with an evidence that exists."""
    if value in (None, ""):
        problems.append(f"{where}: missing — write it from the fetched page, or "
                        f"`NOT FETCHED — <barrier>`")
    elif is_nf(value):
        if not nf_ok(value):
            problems.append(f"{where}: a bare NOT FETCHED — name the barrier "
                            f"(`NOT FETCHED — <what was tried and what stopped it>`)")
    elif not evidence:
        problems.append(f"{where}: has no `evidence` — a finding cites the saved fetch or the "
                        f"URL it was read from, or is `NOT FETCHED — <barrier>` (rule 9)")
    elif not str(evidence).startswith(("http://", "https://")) and not (root / evidence).exists():
        problems.append(f"{where}: evidence {evidence!r} is not on disk")


def _metric(where, value, kind, problems):
    if value is None:
        problems.append(f"{where}: missing — the fetched value or `NOT FETCHED — <barrier>`")
    elif is_nf(value):
        if not nf_ok(value):
            problems.append(f"{where}: a bare NOT FETCHED — name the barrier")
    elif not isinstance(value, kind) or isinstance(value, bool) and kind is int:
        problems.append(f"{where}: {value!r} is not a {kind.__name__} or NOT FETCHED — <barrier>")


def _choice(where, options, key, n_min, n_max, problems):
    if not isinstance(options, list) or not (n_min <= len(options) <= n_max):
        want = str(n_min) if n_min == n_max else f"{n_min}–{n_max}"
        problems.append(f"{where}: {want} options expected, found "
                        f"{len(options) if isinstance(options, list) else 0}")
        return
    rec = [o for o in options if o.get("recommended")]
    if len(rec) != 1:
        problems.append(f"{where}: exactly one option marked (Recommended), found {len(rec)}")
    for i, o in enumerate(options):
        if not o.get(key):
            problems.append(f"{where}[{i}]: no {key}")
    for o in rec:
        for f in ("why", "trade_off"):
            if not o.get(f):
                problems.append(f"{where}: the (Recommended) option has no {f} (working rule 4)")


def merged(record, queries):
    """The record with what the query file knows filled in: competitor positions, H2
    counts and word counts. The record's own value wins where it has one."""
    by_url = {_norm_url(c["url"]): c for c in queries.get("competitors", [])}
    rows = []
    for r in record.get("reverse_engineering", []):
        r = dict(r)
        q = by_url.get(_norm_url(r.get("url")), {})
        if r.get("words") is None and isinstance(q.get("words"), int):
            r["words"] = q["words"]
        if r.get("headings") is None and isinstance(q.get("h2_clean"), int):
            r["headings"] = {"h2": q["h2_clean"],
                             "note": "NOT FETCHED — H1 and H3–H6: query_augment.py "
                                     "--extract-h2 records H2s only"}
        rows.append(r)
    return rows


def validate(record, queries, root=ROOT):
    """Every problem with the record, as strings. Empty means the board may be shown."""
    p = []
    if record.get("page_type") not in PAGE_TYPES:
        p.append(f"page_type: one of {', '.join(PAGE_TYPES)}")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(record.get("date", ""))):
        p.append("date: YYYY-MM-DD")
    if not record.get("method"):
        p.append("method: say how and when the research was fetched")

    serp = record.get("serp") or {}
    results = serp.get("results") or []
    if not serp.get("query"):
        p.append("serp.query: the query searched")
    if not serp.get("structural_read"):
        p.append("serp.structural_read: what the shape of the SERP says")
    by_url = {_norm_url(r.get("url")): r for r in results}
    top = top_competitors(queries)
    if not top:
        p.append(f"the query file has no competitor in the top {TOP_N} — run "
                 f"{FETCH['serp']} first")
    for c in top:
        if _norm_url(c["url"]) not in by_url:
            p.append(f"serp.results: {c['url']} ranks in the top {TOP_N} and has no row — "
                     f"every top competitor gets a why-it-ranks and a weakness")
    for i, r in enumerate(results):
        where = f"serp.results[{i}] {r.get('url', '?')}"
        if not r.get("type"):
            p.append(f"{where}: no type (marketplace, directory, breeder, rescue, forum, article…)")
        for f in ("why_ranks", "weakness"):
            _grounded(f"{where}: {f}", r.get(f), r.get("evidence"), p, root)

    intent = record.get("intent") or {}
    for f in ("dominant", "secondary", "emotional", "local"):
        if not intent.get(f):
            p.append(f"intent.{f}: missing (write `none` when a layer is absent)")

    re_rows = merged(record, queries)
    re_urls = {_norm_url(r.get("url")) for r in re_rows}
    for c in top:
        if _norm_url(c["url"]) not in re_urls:
            p.append(f"reverse_engineering: {c['url']} has no row")
    for i, r in enumerate(re_rows):
        where = f"reverse_engineering[{i}] {r.get('url', '?')}"
        _metric(f"{where}: words", r.get("words"), int, p)
        h = r.get("headings")
        if isinstance(h, dict):
            bad = [k for k in h if k not in ("h1", "h2", "h3", "h4", "h5", "h6", "note")]
            if bad:
                p.append(f"{where}: headings: unknown keys {bad}")
            if "note" in h and not nf_ok(h["note"]) and is_nf(h["note"]):
                p.append(f"{where}: headings.note: a bare NOT FETCHED — name the barrier")
        else:
            _metric(f"{where}: headings", h, dict, p)
        _metric(f"{where}: tables", r.get("tables"), int, p)
        _metric(f"{where}: faq", r.get("faq"), bool, p)
        _metric(f"{where}: byline", r.get("byline"), str, p)
        _metric(f"{where}: schema", r.get("schema"), str, p)

    for f in ("universal_gaps", "how_we_win", "content_gap"):
        v = record.get(f)
        if not (isinstance(v, list) and v and all(isinstance(x, str) and x for x in v)):
            p.append(f"{f}: a non-empty list of findings")
    if not record.get("why_competitors_rank"):
        p.append("why_competitors_rank: the summary of why the top results rank")

    ol = record.get("owner_language")
    if isinstance(ol, str):
        if not nf_ok(ol):
            p.append("owner_language: real quotes with their source, or `NOT FETCHED — <barrier>`")
    elif isinstance(ol, list) and ol:
        for i, q in enumerate(ol):
            if not q.get("quote") or not str(q.get("source", "")).startswith(("http://", "https://")):
                p.append(f"owner_language[{i}]: a quote and the URL it was read from")
    else:
        p.append("owner_language: real quotes with their source, or `NOT FETCHED — <barrier>`")

    fan = record.get("fanout") or {}
    for f in ("paa", "threads", "llm_intel"):
        v = fan.get(f)
        if v in (None, "", []):
            p.append(f"fanout.{f}: missing — the fetched list, or `NOT FETCHED — <barrier>`")
        elif is_nf(v) and not nf_ok(v):
            p.append(f"fanout.{f}: a bare NOT FETCHED — name the barrier")

    ents = record.get("entities")
    if not (isinstance(ents, list) and ents and all(e.get("id") and e.get("class") for e in ents)):
        p.append("entities: a non-empty list of {id, class} from data/bsuk-ontology.json")

    _choice("angles", record.get("angles"), "hook", 3, 3, p)
    _choice("strategies", record.get("strategies"), "direction", 2, 3, p)
    fws = record.get("frameworks")
    if not (isinstance(fws, list) and fws):
        p.append("frameworks: the framework options per planned section group")
    else:
        for i, g in enumerate(fws):
            opts = g.get("options") or []
            if not g.get("group") or len(opts) < 2:
                p.append(f"frameworks[{i}]: a group and at least two options")
            if g.get("recommended") not in opts:
                p.append(f"frameworks[{i}]: the (Recommended) framework is not one of its options")
            for f in ("why", "trade_off"):
                if not g.get(f):
                    p.append(f"frameworks[{i}]: the (Recommended) pick has no {f} (working rule 4)")

    kw = record.get("keywords") or {}
    uni = kw.get("universe") or []
    if not uni:
        p.append("keywords.universe: the keyword universe, grouped by intent")
    names = set()
    for i, k in enumerate(uni):
        if not k.get("keyword"):
            p.append(f"keywords.universe[{i}]: no keyword")
            continue
        names.add(k["keyword"])
        if k.get("intent") not in INTENTS:
            p.append(f"keywords.universe[{i}] {k['keyword']!r}: intent one of {', '.join(INTENTS)}")
        _metric(f"keywords.universe[{i}] {k['keyword']!r}: volume", k.get("volume"), int, p)
    dist = kw.get("distribution") or []
    if not dist:
        p.append("keywords.distribution: the keywords placed section by section")
    placed = set()
    for i, d in enumerate(dist):
        if not d.get("section") or not d.get("primary"):
            p.append(f"keywords.distribution[{i}]: a section and at least one primary keyword")
        for k in (d.get("primary") or []) + (d.get("secondary") or []):
            placed.add(k)
            if k not in names:
                p.append(f"keywords.distribution[{i}]: {k!r} is not in the keyword universe")
    for k in uni:
        if k.get("keyword") and k["keyword"] not in placed and not k.get("parked"):
            p.append(f"keywords.universe: {k['keyword']!r} is placed in no section "
                     f"(place it, or give it a `parked` reason)")
    return p


# --- rendering -------------------------------------------------------------------------

def _v(value):
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, dict):
        counts = " + ".join(f"{value[k]} {k.upper()}" for k in ("h1", "h2", "h3", "h4", "h5", "h6")
                            if k in value)
        return counts + (f" ({value['note']})" if value.get("note") else "")
    return str(value)


def _rec(o):
    return " **(Recommended)**" if o.get("recommended") else ""


def sections(record, queries):
    qpos = {_norm_url(c["url"]): c for c in queries.get("competitors", [])}
    serp = record["serp"]
    status = approval_line(record)
    out = [("Status", f"{status}\n\nResearch method: {record['method']}\n\nQuery file: "
                      f"`{record.get('queries_file', 'data/queries/' + record['slug'] + '.json')}` "
                      f"(fetched {queries.get('fetched', 'NOT FETCHED — no fetch date in the query file')})")]
    rows = []
    for i, r in enumerate(serp["results"], 1):
        q = qpos.get(_norm_url(r["url"]), {})
        rows.append([i, r["url"], r["type"], q.get("google_pos") or "—", q.get("bing_pos") or "—",
                     q.get("h2_clean", "—"), r["why_ranks"], r["weakness"],
                     r.get("evidence") or "—"])
    out.append(("1. SERP Snapshot", f"Query: **{serp['query']}** (Google and Bing, top {TOP_N}, merged)\n\n"
                + MA.table(["#", "Result", "Type", "Google", "Bing", "H2s", "Why it ranks",
                            "Weakness (our wedge)", "Evidence"], rows)
                + f"\n\n**Structural read:** {serp['structural_read']}"))
    it = record["intent"]
    out.append(("2. Search Intent", "\n".join(
        f"- **{k.capitalize()}:** {it[k]}" for k in ("dominant", "secondary", "emotional", "local"))
        + (f"\n\nEvidence: {it['evidence']}" if it.get("evidence") else "")))
    re_rows = [[r["url"], _v(r["words"]), _v(r["headings"]), _v(r["tables"]), _v(r["faq"]),
                _v(r["byline"]), _v(r["schema"]) + (f"; {r['notes']}" if r.get("notes") else "")]
               for r in merged(record, queries)]
    out.append(("3. Competitor Reverse Engineering",
                MA.table(["Competitor", "Words", "Headings", "Tables", "FAQ", "Byline",
                          "Schema / notes"], re_rows)
                + "\n\n**Universal competitor gaps (every fetched competitor misses these):**\n\n"
                + "\n".join(f"- {g}" for g in record["universal_gaps"])))
    ol = record["owner_language"]
    out.append(("4. Owner Language", ol if isinstance(ol, str) else
                "\n".join(f"- \"{q['quote']}\" — {q['source']}" for q in ol)))
    fan = record["fanout"]

    def lst(v):
        if isinstance(v, str):
            return f"  - {v}"
        return "\n".join(f"  - {x if isinstance(x, str) else x.get('title', '') + ' — ' + x.get('url', '')}"
                         for x in v)
    qs = [q for q in queries.get("questions", []) if q.get("must_answer")]
    out.append(("5. Query Fan-Out",
                f"- **PAA:**\n{lst(fan['paa'])}\n- **Threads:**\n{lst(fan['threads'])}\n"
                f"- **LLM intel:** {fan['llm_intel']}\n- **Question file:** "
                f"{len(queries.get('questions', []))} questions, {len(qs)} must-answer"))
    out.append(("6. Why Competitors Rank", record["why_competitors_rank"]))
    out.append(("7. How We Win", "\n".join(f"- {x}" for x in record["how_we_win"])))
    out.append(("8. Content Gap (build list)", "\n".join(f"- {x}" for x in record["content_gap"])))
    out.append(("9. Entities", MA.table(["Entity", "Class"],
                                        [[e["id"], e["class"]] for e in record["entities"]])))
    out.append(("10. Angles", "\n".join(
        f"- **{a.get('id', i)}** — {a['hook']}{_rec(a)}" + (f"\n  - Angle: {a['angle']}" if a.get("angle") else "")
        + (f"\n  - Why: {a['why']}\n  - Trade-off: {a['trade_off']}" if a.get("recommended") else "")
        for i, a in enumerate(record["angles"], 1))))
    out.append(("11. Strategy Directions", "\n".join(
        f"- **{s.get('id', i)}** — {s['direction']}{_rec(s)}" + (f" (source: {s['source']})" if s.get("source") else "")
        + (f"\n  - Why: {s['why']}\n  - Trade-off: {s['trade_off']}" if s.get("recommended") else "")
        for i, s in enumerate(record["strategies"], 1))))
    out.append(("12. Frameworks per Section Group", MA.table(
        ["Section group", "Options", "(Recommended)", "Why", "Trade-off"],
        [[g["group"], ", ".join(g["options"]), g["recommended"], g["why"], g["trade_off"]]
         for g in record["frameworks"]])))
    uni = sorted(record["keywords"]["universe"], key=lambda k: INTENTS.index(k["intent"]))
    out.append(("13. Keyword Universe", MA.table(
        ["Keyword", "Intent", "Type", "Volume", "Parked"],
        [[k["keyword"], k["intent"], k.get("type", "—"), _v(k["volume"]), k.get("parked", "—")]
         for k in uni])))
    out.append(("14. Keyword Distribution", MA.table(
        ["Section", "Primary", "Secondary"],
        [[d["section"], ", ".join(d["primary"]), ", ".join(d.get("secondary") or []) or "—"]
         for d in record["keywords"]["distribution"]])))
    gaps = fetch_plan(record, queries)
    out.append(("15. What Is NOT FETCHED and How to Fetch It",
                MA.table(["Field", "Barrier", "How to fetch it"], gaps) if gaps
                else "Nothing: every field on this board was fetched."))
    return out


def fetch_plan(record, queries):
    """[field, barrier, command] for every NOT FETCHED on the board."""
    rows = []

    def walk(v, path, key):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, f"{path}.{k}", k)
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, f"{path}[{i}]", key)
        elif is_nf(v):
            leaf = "headings" if key == "note" else key
            rows.append([path.lstrip("."), v.split("—", 1)[-1].strip(),
                         FETCH.get(leaf, "the row 4–7 step that owns this field (page-run.md)")])
    body = {k: v for k, v in record.items() if k != "approval"}
    body["reverse_engineering"] = merged(record, queries)
    walk(body, "", "")
    return rows


def approval_line(record):
    state = approval_state(record)
    a = record.get("approval") or {}
    if state == "approved":
        return (f"Status: **APPROVED {a['approved_on']}** (STOP 1 cleared) — picks: "
                f"`{a['answers']}`")
    if state == "stale":
        return (f"Status: **CHANGED AFTER APPROVAL** — approved {a.get('approved_on')}, edited since; "
                f"approve again (STOP 1)")
    return "Status: **AWAITING THE USER'S PICKS — STOP 1**"


def build(record, queries, out_dir):
    slug = record["slug"]
    secs = sections(record, queries)
    heading = f"Research board — {record.get('route', slug)}"
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path, md_path = out_dir / f"{slug}.html", out_dir / f"{slug}.md"
    html_path.write_text(MA.page(f"Research Board {slug}", "BlueStaffyUK · project 5 · STOP 1",
                                 heading, approval_state(record), record["date"],
                                 f"{RECORDS}/{slug}.json", secs, f"{slug}-research-board.md"),
                         encoding="utf-8")
    md_path.write_text(MA.markdown(heading, secs), encoding="utf-8")
    return html_path, md_path


def load_queries(record, override=None, root=ROOT):
    rel = override or record.get("queries_file") or f"data/queries/{record.get('slug')}.json"
    path = pathlib.Path(rel)
    path = path if path.is_absolute() else root / path
    if not path.is_file():
        raise RecordError(f"no query file at {rel} — run {FETCH['serp']} first")
    return json.loads(path.read_text(encoding="utf-8"))


def approve(record, answers, today=None, root=ROOT):
    """The record with its approval stamped. Refuses an incomplete record or a missing
    answers file."""
    path = pathlib.Path(answers)
    if not (path if path.is_absolute() else root / path).is_file():
        raise RecordError(f"no answers file at {answers} — the picks come back from the answer "
                          f"board (docs/reference/answer-board/README.md)")
    out = dict(record)
    out["approval"] = {"approved_on": today or datetime.date.today().isoformat(),
                       "answers": str(answers), "record_hash": record_hash(record)}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--record")
    ap.add_argument("--queries")
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--approve", action="store_true")
    ap.add_argument("--answers")
    a = ap.parse_args(argv)
    try:
        path = pathlib.Path(a.record) if a.record else record_path(a.slug)
        record = load(path)
        if record.get("slug") != a.slug:
            raise RecordError(f"the record at {path} is for {record.get('slug')!r}, not {a.slug!r}")
        queries = load_queries(record, a.queries)
    except RecordError as e:
        print(f"research-board ERROR {e}")
        return 2
    problems = validate(record, queries)
    print(f"research-board {a.slug}: examined {len(record.get('serp', {}).get('results', []))} "
          f"competitors ({len(top_competitors(queries))} in the top {TOP_N}), "
          f"{len(record.get('keywords', {}).get('universe', []))} keywords, "
          f"{len(record.get('angles', []))} angles — {len(problems)} problems")
    for x in problems:
        print(f"  FAIL {x}")
    if problems:
        return 1
    if a.approve:
        if not a.answers:
            print("research-board ERROR --approve needs --answers <the answers file>")
            return 2
        try:
            record = approve(record, a.answers)
        except RecordError as e:
            print(f"research-board ERROR {e}")
            return 2
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"approved {a.slug} — {record['approval']['answers']} "
              f"(hash {record['approval']['record_hash']})")
    if a.check:
        print(f"state: {approval_state(record)}")
        return 0
    html_path, md_path = build(record, queries, pathlib.Path(a.out) if a.out else ROOT / OUT)
    print(f"wrote {html_path} and {md_path} — state: {approval_state(record)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
