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
  15 the AI Overview (present or not, what it says, whom it cites) · 16 the heading-type
                     analysis (the heading shapes the ranking pages use, and which wins) ·
                     17 the SERP schema audit · 18 authority and links (referring domains and
                     authority, where fetched)

NOTHING IS INFERRED (working rule 9). A value is either grounded or it is written
`NOT FETCHED — <barrier>`, naming what was tried and what stopped it; a bare `NOT FETCHED`
is refused anywhere in the record. A competitor's why and weakness are grounded by its
`evidence`: a saved fetch — a file inside the repo under data/queries/cache/, data/queries/
or docs/research/ (never a directory, an absolute path or a path out of the repo) — or a URL
other than the result's own, with the date it was `fetched`. The fields the query file does
record are read from it, never retyped: a competitor's `words`, and its H2 count
(`h2_clean`) when the record gives no heading census.

THE APPROVAL. The user's picks come back from the answer board as
`docs/reference/answer-board/answers/<batchId>-<date>.json`; `--approve --answers <file>`
reads that file — an answer-board answers file with at least one answered question, whose
batch id (or a question) names this slug and `research-board` — and records it in the
record's `approval` with the record's hash. The hash covers the query-file values the board
renders, so a changed query file, like an edited record, reads as stale. scripts/outline_matrix.py
refuses an outline whose research board is not approved as it stands.

Usage:
  python3 scripts/research_board.py <slug>                 validate, write the board
  python3 scripts/research_board.py <slug> --check         validate only
  python3 scripts/research_board.py <slug> --approve --answers <answers.json>
  options: --record PATH  --queries PATH  --out DIR        (a fixture, or a scratch run)
Writes docs/artifacts/research/<slug>.html and .md; publish the .html as an Artifact.
Exit 0 clean · 1 the record is incomplete or malformed (every problem printed) · 2 no record,
an unreadable record or query file, a bad call, or a refused approval.
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
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# `NOT FETCHED — <barrier>`: the barrier is at least two words (scripts/not_fetched_lint.py).
NOT_FETCHED = re.compile(r"^NOT FETCHED\s*(?:—|–|:)\s*(\S+\s+\S+.*)$", re.S)
PAGE_TYPES = ("location", "comparison", "blog")
INTENTS = ("transactional", "commercial", "informational", "navigational", "local")
HEADING_KEYS = ("h1", "h2", "h3", "h4", "h5", "h6")
# Where a saved fetch may live (B5): a file in the repo, under one of these.
EVIDENCE_DIRS = ("data/queries/cache/", "data/queries/", "docs/research/")
# What an answers file must name for each stop (B3), besides the slug.
STOP_TOKENS = {"research-board": ("research-board", "research board"),
               "outline": ("outline",)}

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
    "ai_overview": "`bsuk-paa-agent` on the live SERP (Playwright), capturing the AI Overview text and citations",
    "says": "`bsuk-paa-agent` on the live SERP (Playwright), capturing the AI Overview text",
    "cites": "`bsuk-paa-agent` on the live SERP (Playwright), listing the AI Overview's citations",
    "heading_types": "`bsuk-framework-agent` on each saved page, classing its heading shapes",
    "serp_schema": "`bsuk-framework-agent` on each saved page (its JSON-LD types)",
    "authority": "`mcp__…__backlinks_summary` through the spend guard, per competitor domain",
    "referring_domains": "`mcp__…__backlinks_summary` through the spend guard",
}


class RecordError(Exception):
    pass


def is_nf(value):
    return isinstance(value, str) and value.startswith("NOT FETCHED")


def nf_ok(value):
    return isinstance(value, str) and bool(NOT_FETCHED.match(value))


def _d(v):
    return v if isinstance(v, dict) else {}


def _l(v):
    return v if isinstance(v, list) else []


def _s(v):
    return isinstance(v, str) and v.strip() != ""


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _norm_url(u):
    return (u if isinstance(u, str) else "").strip().rstrip("/").lower()


def _competitors(queries):
    """The query file's competitor rows that are objects with a URL string."""
    return [c for c in _l(_d(queries).get("competitors"))
            if isinstance(c, dict) and isinstance(c.get("url"), str)]


def top_competitors(queries, n=TOP_N):
    """The query file's competitors in the top n on either engine, in pool order."""
    def pos(v):
        return v if _int(v) else 99
    return [c for c in _competitors(queries)
            if min(pos(c.get("google_pos")), pos(c.get("bing_pos"))) <= n]


def merged(record, queries):
    """The reverse-engineering rows with what the query file knows filled in: word counts,
    and the H2 count when the record gives no census. The record's own value wins."""
    by_url = {_norm_url(c["url"]): c for c in _competitors(queries)}
    rows = []
    for r in _l(_d(record).get("reverse_engineering")):
        if not isinstance(r, dict):
            rows.append(r)
            continue
        r = dict(r)
        q = by_url.get(_norm_url(r.get("url")), {})
        if r.get("words") is None and _int(q.get("words")):
            r["words"] = q["words"]
        if r.get("headings") is None and _int(q.get("h2_clean")):
            r["headings"] = {"h2": q["h2_clean"],
                             "note": "NOT FETCHED — H1 and H3–H6: query_augment.py "
                                     "--extract-h2 records H2s only"}
        rows.append(r)
    return rows


def record_hash(record, queries=None):
    """The record's hash, over the record and every query-file value the board renders (B9):
    positions, H2 counts, word counts, and the merged reverse-engineering rows."""
    body = {k: v for k, v in _d(record).items() if k != "approval"}
    q = [{k: c.get(k) for k in ("url", "google_pos", "bing_pos", "h2_clean", "words")}
         for c in _competitors(queries)]
    doc = {"record": body, "queries": q, "merged": merged(record, queries or {})}
    return hashlib.sha256(json.dumps(doc, sort_keys=True, ensure_ascii=False, default=str)
                          .encode("utf-8")).hexdigest()[:16]


def current_hash(record, root=None):
    try:
        queries = load_queries(record, root=root)
    except RecordError:
        queries = {}
    return record_hash(record, queries)


def approval_state(record, queries=None, root=None):
    """'approved', 'stale' (the record or its query-file values changed since) or 'unapproved'."""
    a = _d(record).get("approval")
    if not isinstance(a, dict) or not a:
        return "unapproved"
    h = record_hash(record, queries) if queries is not None else current_hash(record, root)
    return "approved" if a.get("record_hash") == h else "stale"


def record_path(slug, root=None):
    if not isinstance(slug, str) or not SLUG.match(slug):
        raise RecordError(f"not a slug: {slug!r}")
    return pathlib.Path(ROOT if root is None else root) / RECORDS / f"{slug}.json"


def load(path):
    path = pathlib.Path(path)
    if not path.is_file():
        raise RecordError(f"no research-board record at {path}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise RecordError(f"{path}: not JSON — {e}") from None
    if not isinstance(doc, dict):
        raise RecordError(f"{path}: a record is a JSON object")
    return doc


def load_queries(record, override=None, root=None):
    root = pathlib.Path(ROOT if root is None else root)
    rel = override or _d(record).get("queries_file") or f"data/queries/{_d(record).get('slug')}.json"
    path = pathlib.Path(rel)
    path = path if path.is_absolute() else root / path
    if not path.is_file():
        raise RecordError(f"no query file at {rel} — run {FETCH['serp']} first")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise RecordError(f"{rel}: the query file is not JSON — {e}") from None


# --- the answers file (B3) -------------------------------------------------------------

def _inside(root, rel):
    """The resolved path of a repo-relative `rel`, or None when it is absolute, empty, '.',
    or resolves outside `root`."""
    if not _s(rel) or rel.strip() in (".", "./"):
        return None
    p = pathlib.Path(rel)
    if p.is_absolute():
        return None
    root = pathlib.Path(root).resolve()
    full = (root / p).resolve()
    try:
        full.relative_to(root)
    except ValueError:
        return None
    return full


def check_answers(rel, slug, stop, root=None):
    """The parsed answers of an answer-board answers file that approves `stop` for `slug`;
    raises RecordError when it is not one."""
    root = ROOT if root is None else root
    full = _inside(root, rel)
    if full is None or not full.is_file():
        raise RecordError(f"no answers file at {rel!r} inside the repo — the picks come back from "
                          f"the answer board (docs/reference/answer-board/README.md)")
    try:
        doc = json.loads(full.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise RecordError(f"{rel} is not an answer-board answers file (not JSON)") from None
    data = doc.get("data") if isinstance(doc, dict) and isinstance(doc.get("data"), dict) else doc
    answers = _l(_d(data).get("answers"))
    batch = _d(data).get("batchId")
    if not _s(batch) or not answers or not all(isinstance(a, dict) for a in answers):
        raise RecordError(f"{rel} is not an answer-board answers file (it needs a batchId and "
                          f"its answers)")
    if not any(a.get("status") == "answered" for a in answers):
        raise RecordError(f"{rel}: no question in the batch is answered")
    tokens = STOP_TOKENS[stop]

    def names(text):
        t = (text or "").lower() if isinstance(text, str) else ""
        return slug in t and any(tok in t for tok in tokens)
    if not (names(batch) or any(names(a.get("question")) for a in answers)):
        raise RecordError(f"{rel}: the batch {batch!r} does not name this page ({slug}) and this "
                          f"stop ({stop}) — post the stop's own batch")
    return answers


def approve(record, answers, today=None, root=None, queries=None):
    """The record with its approval stamped. Refuses a file that is not this page's STOP 1
    answers."""
    root = ROOT if root is None else root
    check_answers(answers, _d(record).get("slug"), "research-board", root)
    if queries is None:
        queries = load_queries(record, root=root)
    out = dict(record)
    out["approval"] = {"approved_on": today or datetime.date.today().isoformat(),
                       "answers": str(answers), "record_hash": record_hash(record, queries)}
    return out


# --- validation ------------------------------------------------------------------------

def _bare_nf(record, p):
    """B7: a bare `NOT FETCHED` anywhere in the record is refused."""
    def walk(v, path):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, f"{path}.{k}" if path else str(k))
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, f"{path}[{i}]")
        elif is_nf(v) and not nf_ok(v):
            p.append(f"{path}: a bare NOT FETCHED — name the barrier "
                     f"(`NOT FETCHED — <what was tried and what stopped it>`)")
    walk({k: v for k, v in record.items() if k != "approval"}, "")


def _evidence(where, row, root, p):
    ev = row.get("evidence")
    if not _s(ev):
        p.append(f"{where}: evidence — a finding cites the saved fetch or the URL it was read "
                 f"from, or is `NOT FETCHED — <barrier>` (rule 9)")
        return
    if ev.startswith(("http://", "https://")):
        if _norm_url(ev) == _norm_url(row.get("url")):
            p.append(f"{where}: evidence is the result's own URL — cite the saved fetch, or "
                     f"another URL the finding was read from")
        elif not (isinstance(row.get("fetched"), str) and DATE.match(row["fetched"])):
            p.append(f"{where}: evidence URL {ev!r} has no `fetched` date (YYYY-MM-DD)")
        return
    full = _inside(root, ev)
    rel = ev.strip().lstrip("./") if full is not None else ev
    if full is None:
        p.append(f"{where}: evidence {ev!r} is not a path inside the repo")
    elif not any(rel.startswith(d) for d in EVIDENCE_DIRS):
        p.append(f"{where}: evidence {ev!r} is not a saved fetch under "
                 f"{', '.join(EVIDENCE_DIRS)}")
    elif not full.is_file():
        p.append(f"{where}: evidence {ev!r} is not a saved file on disk")


def _grounded(where, row, field, root, p):
    value = row.get(field)
    if not _s(value):
        p.append(f"{where}: {field} missing — write it from the fetched page, or "
                 f"`NOT FETCHED — <barrier>`")
    elif not is_nf(value):
        _evidence(f"{where}: {field}", row, root, p)


def _metric(where, value, kinds, p):
    if value is None:
        p.append(f"{where}: missing — the fetched value or `NOT FETCHED — <barrier>`")
    elif is_nf(value):
        return
    elif not isinstance(value, kinds) or (isinstance(value, bool) and bool not in kinds):
        names = "/".join(k.__name__ for k in kinds)
        p.append(f"{where}: {value!r} is not a {names} or NOT FETCHED — <barrier>")


def _text(where, value, p):
    if not _s(value):
        p.append(f"{where}: missing (a finding, or `NOT FETCHED — <barrier>`)")


def _choice(where, options, key, n_min, n_max, p):
    if not isinstance(options, list) or not (n_min <= len(options) <= n_max):
        want = str(n_min) if n_min == n_max else f"{n_min}–{n_max}"
        p.append(f"{where}: {want} options expected, found "
                 f"{len(options) if isinstance(options, list) else 0}")
        return
    if not all(isinstance(o, dict) for o in options):
        p.append(f"{where}: every option is an object")
        return
    rec = [o for o in options if o.get("recommended")]
    if len(rec) != 1:
        p.append(f"{where}: exactly one option marked (Recommended), found {len(rec)}")
    for i, o in enumerate(options):
        if not _s(o.get(key)):
            p.append(f"{where}[{i}]: no {key}")
    for o in rec:
        for f in ("why", "trade_off"):
            if not _s(o.get(f)):
                p.append(f"{where}: the (Recommended) option has no {f} (working rule 4)")


def _nf_or(where, value, check, p):
    """A field that is `NOT FETCHED — <barrier>` or passes `check`."""
    if is_nf(value):
        return
    check(where, value, p)


def _check_aio(where, v, p):
    if not isinstance(v, dict) or not isinstance(v.get("present"), bool):
        p.append(f"{where}: {{present: true|false, says, cites}} or `NOT FETCHED — <barrier>`")
        return
    if v["present"]:
        if not _s(v.get("says")):
            p.append(f"{where}.says: what the AI Overview says, or `NOT FETCHED — <barrier>`")
        c = v.get("cites")
        if not (is_nf(c) or (isinstance(c, list) and c and all(_s(x) for x in c))):
            p.append(f"{where}.cites: whom it cites, or `NOT FETCHED — <barrier>`")


def _check_heading_types(where, v, p):
    rows = _d(v).get("rows")
    if not (isinstance(rows, list) and rows
            and all(isinstance(r, dict) and _s(r.get("source")) and _s(r.get("style")) for r in rows)):
        p.append(f"{where}.rows: each ranking page's heading style ({{source, style}})")
    if not _s(_d(v).get("winning_shape")):
        p.append(f"{where}.winning_shape: the shape that wins")


def _check_schema(where, v, p):
    if not (isinstance(v, list) and v
            and all(isinstance(r, dict) and _s(r.get("url")) and _s(r.get("schema")) for r in v)):
        p.append(f"{where}: one {{url, schema}} per ranking page (the schema types found)")


def _check_authority(where, v, p):
    if not (isinstance(v, list) and v and all(isinstance(r, dict) and _s(r.get("url")) for r in v)):
        p.append(f"{where}: one {{url, referring_domains, authority, source}} per competitor")
        return
    for i, r in enumerate(v):
        _metric(f"{where}[{i}].referring_domains", r.get("referring_domains"), (int,), p)
        _metric(f"{where}[{i}].authority", r.get("authority"), (int, str), p)
        fetched = [k for k in ("referring_domains", "authority")
                   if r.get(k) is not None and not is_nf(r.get(k))]
        if fetched and not _s(r.get("source")):
            p.append(f"{where}[{i}]: a fetched figure names its `source` (the tool and date)")


def validate(record, queries, root=None):
    """Every problem with the record, as strings. Empty means the board may be shown. A
    malformed shape is a problem, never a crash (B8)."""
    root = ROOT if root is None else root
    p = []
    if not isinstance(record, dict):
        return ["the record is not a JSON object"]
    if not isinstance(queries, dict):
        p.append("the query file is not a JSON object")
    elif not isinstance(queries.get("competitors"), list):
        p.append("the query file's competitors is not a list")
    elif any(not isinstance(c, dict) or not isinstance(c.get("url"), str)
             for c in queries["competitors"]):
        p.append("the query file has a competitor that is not an object with a url")
    try:
        _validate(record, queries if isinstance(queries, dict) else {}, root, p)
    except (TypeError, AttributeError, KeyError, ValueError) as e:  # a shape not foreseen
        p.append(f"malformed record: {type(e).__name__}: {e}")
    return p


def _validate(record, queries, root, p):
    _bare_nf(record, p)
    if record.get("page_type") not in PAGE_TYPES:
        p.append(f"page_type: one of {', '.join(PAGE_TYPES)}")
    if not DATE.match(str(record.get("date", ""))):
        p.append("date: YYYY-MM-DD")
    if not _s(record.get("method")):
        p.append("method: say how and when the research was fetched")

    serp = record.get("serp")
    if not isinstance(serp, dict):
        p.append("serp: an object with query, results and structural_read")
        serp = {}
    results = serp.get("results")
    if not isinstance(results, list):
        p.append("serp.results: a list, one row per top competitor")
        results = []
    _text("serp.query", serp.get("query"), p)
    _text("serp.structural_read", serp.get("structural_read"), p)
    rows = [r for r in results if isinstance(r, dict)]
    if len(rows) != len(results):
        p.append("serp.results: every row is an object")
    by_url = {_norm_url(r.get("url")): r for r in rows}
    top = top_competitors(queries)
    if not top:
        p.append(f"the query file has no competitor in the top {TOP_N} — run {FETCH['serp']} first")
    for c in top:
        if _norm_url(c["url"]) not in by_url:
            p.append(f"serp.results: {c['url']} ranks in the top {TOP_N} and has no row — "
                     f"every top competitor gets a why-it-ranks and a weakness")
    for i, r in enumerate(rows):
        where = f"serp.results[{i}] {r.get('url', '?')}"
        if not _s(r.get("type")):
            p.append(f"{where}: no type (marketplace, directory, breeder, rescue, forum, article…)")
        for f in ("why_ranks", "weakness"):
            _grounded(where, r, f, root, p)

    intent = record.get("intent")
    if not isinstance(intent, dict):
        p.append("intent: an object with dominant, secondary, emotional and local")
        intent = {}
    for f in ("dominant", "secondary", "emotional", "local"):
        if not _s(intent.get(f)):
            p.append(f"intent.{f}: missing (write `none` when a layer is absent)")

    if not isinstance(record.get("reverse_engineering"), list):
        p.append("reverse_engineering: a list, one row per top competitor")
    re_rows = merged(record, queries)
    good = [r for r in re_rows if isinstance(r, dict)]
    if len(good) != len(re_rows):
        p.append("reverse_engineering: every row is an object")
    re_urls = {_norm_url(r.get("url")) for r in good}
    for c in top:
        if _norm_url(c["url"]) not in re_urls:
            p.append(f"reverse_engineering: {c['url']} has no row")
    for i, r in enumerate(good):
        where = f"reverse_engineering[{i}] {r.get('url', '?')}"
        _metric(f"{where}: words", r.get("words"), (int,), p)
        h = r.get("headings")
        if isinstance(h, dict):
            bad = [k for k in h if k not in HEADING_KEYS + ("note",)]
            if bad:
                p.append(f"{where}: headings: unknown keys {bad}")
            for k in HEADING_KEYS:
                if k in h and not (_int(h[k]) and h[k] >= 0):
                    p.append(f"{where}: headings.{k}: {h[k]!r} is not a whole number")
        else:
            _metric(f"{where}: headings", h, (dict,), p)
        _metric(f"{where}: tables", r.get("tables"), (int,), p)
        _metric(f"{where}: faq", r.get("faq"), (bool,), p)
        _metric(f"{where}: byline", r.get("byline"), (str,), p)
        _metric(f"{where}: schema", r.get("schema"), (str,), p)

    for f in ("universal_gaps", "how_we_win", "content_gap"):
        v = record.get(f)
        if not (isinstance(v, list) and v and all(_s(x) for x in v)):
            p.append(f"{f}: a non-empty list of findings")
    _text("why_competitors_rank", record.get("why_competitors_rank"), p)

    ol = record.get("owner_language")
    if isinstance(ol, str) and is_nf(ol):
        pass
    elif isinstance(ol, list) and ol:
        for i, q in enumerate(ol):
            if not (isinstance(q, dict) and _s(q.get("quote"))
                    and str(q.get("source", "")).startswith(("http://", "https://"))):
                p.append(f"owner_language[{i}]: a quote and the URL it was read from")
    else:
        p.append("owner_language: real quotes with their source, or `NOT FETCHED — <barrier>`")

    fan = record.get("fanout")
    if not isinstance(fan, dict):
        p.append("fanout: an object with paa, threads and llm_intel")
        fan = {}
    for f in ("paa", "threads", "llm_intel"):
        v = fan.get(f)
        if v in (None, "", []) or not isinstance(v, (str, list)):
            p.append(f"fanout.{f}: missing — the fetched list, or `NOT FETCHED — <barrier>`")

    ents = record.get("entities")
    if not (isinstance(ents, list) and ents
            and all(isinstance(e, dict) and _s(e.get("id")) and _s(e.get("class")) for e in ents)):
        p.append("entities: a non-empty list of {id, class} from data/bsuk-ontology.json")

    _choice("angles", record.get("angles"), "hook", 3, 3, p)
    _choice("strategies", record.get("strategies"), "direction", 2, 3, p)
    fws = record.get("frameworks")
    if not (isinstance(fws, list) and fws and all(isinstance(g, dict) for g in fws)):
        p.append("frameworks: the framework options per planned section group")
    else:
        for i, g in enumerate(fws):
            opts = g.get("options")
            if not (isinstance(opts, list) and all(_s(o) for o in opts)):
                p.append(f"frameworks[{i}]: options is a list of framework names")
                opts = []
            if not _s(g.get("group")) or len(opts) < 2:
                p.append(f"frameworks[{i}]: a group and at least two options")
            if g.get("recommended") not in opts:
                p.append(f"frameworks[{i}]: the (Recommended) framework is not one of its options")
            for f in ("why", "trade_off"):
                if not _s(g.get(f)):
                    p.append(f"frameworks[{i}]: the (Recommended) pick has no {f} (working rule 4)")

    _keywords(record.get("keywords"), p)

    for f, check in (("ai_overview", _check_aio), ("heading_types", _check_heading_types),
                     ("serp_schema", _check_schema), ("authority", _check_authority)):
        if f not in record:
            p.append(f"{f}: missing — the finding, or `NOT FETCHED — <barrier>`")
        else:
            _nf_or(f, record[f], check, p)


def _keywords(kw, p):
    if not isinstance(kw, dict):
        p.append("keywords: an object with universe and distribution")
        return
    uni = kw.get("universe")
    if not (isinstance(uni, list) and uni):
        p.append("keywords.universe: the keyword universe, grouped by intent")
        uni = []
    names = set()
    for i, k in enumerate(uni):
        if not isinstance(k, dict) or not _s(k.get("keyword")):
            p.append(f"keywords.universe[{i}]: no keyword")
            continue
        names.add(k["keyword"])
        if k.get("intent") not in INTENTS:
            p.append(f"keywords.universe[{i}] {k['keyword']!r}: intent one of {', '.join(INTENTS)}")
        _metric(f"keywords.universe[{i}] {k['keyword']!r}: volume", k.get("volume"), (int,), p)
    dist = kw.get("distribution")
    if not (isinstance(dist, list) and dist):
        p.append("keywords.distribution: the keywords placed section by section")
        dist = []
    placed = set()
    for i, d in enumerate(dist):
        if not isinstance(d, dict):
            p.append(f"keywords.distribution[{i}]: an object")
            continue
        pri, sec = d.get("primary"), d.get("secondary", [])
        if not (isinstance(pri, list) and pri and all(_s(x) for x in pri)):
            p.append(f"keywords.distribution[{i}]: a section and at least one primary keyword (a list)")
            pri = []
        if not (isinstance(sec, list) and all(_s(x) for x in sec)):
            p.append(f"keywords.distribution[{i}]: secondary is a list of keywords")
            sec = []
        if not _s(d.get("section")):
            p.append(f"keywords.distribution[{i}]: no section")
        for k in pri + sec:
            placed.add(k)
            if k not in names:
                p.append(f"keywords.distribution[{i}]: {k!r} is not in the keyword universe")
    for k in uni:
        if isinstance(k, dict) and _s(k.get("keyword")) and k["keyword"] not in placed \
                and not k.get("parked"):
            p.append(f"keywords.universe: {k['keyword']!r} is placed in no section "
                     f"(place it, or give it a `parked` reason)")


# --- rendering -------------------------------------------------------------------------

def _v(value):
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, dict):
        counts = " + ".join(f"{value[k]} {k.upper()}" for k in HEADING_KEYS if k in value)
        return counts + (f" ({value['note']})" if value.get("note") else "")
    return str(value)


def _rec(o):
    return " **(Recommended)**" if o.get("recommended") else ""


def sections(record, queries, root=None):
    qpos = {_norm_url(c["url"]): c for c in _competitors(queries)}
    serp = record["serp"]
    out = [("Status", f"{approval_line(record, queries)}\n\nResearch method: {record['method']}\n\n"
                      f"Query file: `{record.get('queries_file', 'data/queries/' + record['slug'] + '.json')}` "
                      f"(fetched {queries.get('fetched', 'NOT FETCHED — no fetch date in the query file')})")]
    rows = []
    for i, r in enumerate(serp["results"], 1):
        q = qpos.get(_norm_url(r["url"]), {})
        ev = r.get("evidence") or "—"
        rows.append([i, r["url"], r["type"], q.get("google_pos") or "—", q.get("bing_pos") or "—",
                     q.get("h2_clean", "—"), r["why_ranks"], r["weakness"],
                     ev + (f" (fetched {r['fetched']})" if r.get("fetched") else "")])
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
        return "\n".join(f"  - {x if isinstance(x, str) else str(x.get('title', '')) + ' — ' + str(x.get('url', ''))}"
                         for x in v)
    qs = [q for q in _l(queries.get("questions")) if isinstance(q, dict) and q.get("must_answer")]
    out.append(("5. Query Fan-Out",
                f"- **PAA:**\n{lst(fan['paa'])}\n- **Threads:**\n{lst(fan['threads'])}\n"
                f"- **LLM intel:** {fan['llm_intel']}\n- **Question file:** "
                f"{len(_l(queries.get('questions')))} questions, {len(qs)} must-answer"))
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
    aio = record["ai_overview"]
    if isinstance(aio, str):
        aio_md = aio
    elif not aio["present"]:
        aio_md = "No AI Overview is shown for this query."
    else:
        cites = aio["cites"] if isinstance(aio["cites"], str) else ", ".join(aio["cites"])
        aio_md = f"An AI Overview is shown.\n\n> {aio['says']}\n\n**Cites:** {cites}"
        if aio.get("implication"):
            aio_md += f"\n\n**GEO implication:** {aio['implication']}"
    out.append(("15. AI Overview", aio_md))
    ht = record["heading_types"]
    out.append(("16. Heading-Type Analysis", ht if isinstance(ht, str) else
                MA.table(["Source", "Heading style"], [[r["source"], r["style"]] for r in ht["rows"]])
                + f"\n\n**What shape wins:** {ht['winning_shape']}"))
    sc = record["serp_schema"]
    out.append(("17. SERP Schema Audit", sc if isinstance(sc, str) else
                MA.table(["Page", "Schema found"], [[r["url"], r["schema"]] for r in sc])))
    au = record["authority"]
    out.append(("18. Authority and Links", au if isinstance(au, str) else
                MA.table(["Competitor", "Referring domains", "Authority", "Source"],
                         [[r["url"], _v(r.get("referring_domains")), _v(r.get("authority")),
                           r.get("source") or "—"] for r in au])))
    gaps = fetch_plan(record, queries)
    out.append(("19. What Is NOT FETCHED and How to Fetch It",
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


def approval_line(record, queries=None):
    state = approval_state(record, queries if queries is not None else {})
    a = record.get("approval") or {}
    if state == "approved":
        return (f"Status: **APPROVED {a['approved_on']}** (STOP 1 cleared) — picks: "
                f"`{a['answers']}`")
    if state == "stale":
        return (f"Status: **CHANGED AFTER APPROVAL** — approved {a.get('approved_on')}, the record "
                f"or its query file changed since; approve again (STOP 1)")
    return "Status: **AWAITING THE USER'S PICKS — STOP 1**"


def build(record, queries, out_dir):
    slug = record["slug"]
    secs = sections(record, queries)
    heading = f"Research board — {record.get('route', slug)}"
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path, md_path = out_dir / f"{slug}.html", out_dir / f"{slug}.md"
    html_path.write_text(MA.page(f"Research Board {slug}", "BlueStaffyUK · project 5 · STOP 1",
                                 heading, approval_state(record, queries), record["date"],
                                 f"{RECORDS}/{slug}.json", secs, f"{slug}-research-board.md"),
                         encoding="utf-8")
    md_path.write_text(MA.markdown(heading, secs), encoding="utf-8")
    return html_path, md_path


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
    serp = _d(record.get("serp"))
    print(f"research-board {a.slug}: examined {len(_l(serp.get('results')))} "
          f"competitors ({len(top_competitors(queries))} in the top {TOP_N}), "
          f"{len(_l(_d(record.get('keywords')).get('universe')))} keywords, "
          f"{len(_l(record.get('angles')))} angles — {len(problems)} problems")
    for x in problems:
        print(f"  FAIL {x}")
    if problems:
        return 1
    if a.approve:
        if not a.answers:
            print("research-board ERROR --approve needs --answers <the answers file>")
            return 2
        try:
            record = approve(record, a.answers, queries=queries)
        except RecordError as e:
            print(f"research-board ERROR {e}")
            return 2
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"approved {a.slug} — {record['approval']['answers']} "
              f"(hash {record['approval']['record_hash']})")
    if a.check:
        print(f"state: {approval_state(record, queries)}")
        return 0
    html_path, md_path = build(record, queries, pathlib.Path(a.out) if a.out else ROOT / OUT)
    print(f"wrote {html_path} and {md_path} — state: {approval_state(record, queries)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
