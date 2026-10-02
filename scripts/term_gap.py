#!/usr/bin/env python3
"""Board block 5c: what competitors say that we do not — with the evidence for every term.

The pool is every non-blocked, cached competitor page for the slug
(data/queries/cache/<slug>/<n>.html, n the 1-based index into raw/<slug>/competitors.json),
listings included, because listing card text is also what Google ranks for the query. Each
page is labelled listing or prose (query_augment.listing_reason) and ranked in
keyword_metrics._rank order. Four views, nothing proposed that a competitor page does not
carry:

  by type     for each board keyword type, how many of our terms of that type at least one
              competitor body contains (matched like block 4c: key_words phrase starts)
  phrases     1–3 word phrases on at least `min_pages` distinct competitor pages that no
              board term (nor board entity name) already covers; pages, of which prose, and
              total mentions are the evidence. Generic words may not open or close a phrase,
              and marketplace UI words, numbers, prices and single letters may not appear in it
  entities    ontology entities only (name or any alias as a whole key-word phrase) that no
              board section lists and at least one competitor page names
  relations   the ontology's `relations`, filtered to ends on the board or in the gaps; the
              ontology has no `relations` key yet, which is written NOT FETCHED

    python3 scripts/term_gap.py <slug>
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import keyword_metrics as KM  # noqa: E402
import query_augment as QA  # noqa: E402
import term_density as TD  # noqa: E402

ROOT = KM.ROOT
LIMIT = 60
MAX_N = 3
NO_RELATIONS = "NOT FETCHED — data/bsuk-ontology.json carries no `relations` key yet"
NO_PAGES = "NOT FETCHED — no cached competitor page"
SEED_NOTE = ("Only ontology entities are proposed. A new entity goes into data/bsuk-ontology.json "
             "through `scripts/ontology_seed.py`, with a source, before any page names it.")
# Words that may not open or close a phrase: they say nothing on their own.
STOP_GENERIC = frozenset(
    "we our you your puppy puppies dog dogs page here more can will very also all one two get any "
    "i it its this that these those be been was were has have had not no or but if so as up out "
    "about just than then them they their there what when where which who how my me us "
    # function words and filler that topped the London pool's unigrams
    "both other others well new first find feel now around she he her his him old read based "
    "highest full free looking only own each every some most many much make made see go come "
    "know need like still even really may might would could should do does did being per via "
    "into over under after before off again too same such".split())
# Marketplace and site-chrome words seen on the London pool (staffie-owners, pets4homes,
# freeads): a phrase holding any of them is page furniture, not something to say.
STOP_UI = frozenset(
    "ad ads advert adverts ago click cookie cookies details filter filters hours listings menu "
    "miles next page posted premium prev results save search show sign sort view".split())
JUNK = re.compile(r"^(?:\d+|£.*|\d+(?:st|nd|rd|th|k|km|mi|am|pm|s)|[a-z])$")
SPLIT = re.compile(r"[.!?;:|•·\n\r\t()\[\]\"“”]+")


def _chunks(text):
    """Key-word token lists, one per sentence-ish run, so no phrase spans a full stop."""
    out = []
    for part in SPLIT.split(text or ""):
        toks = KM.key_words(part)
        if toks:
            out.append(toks)
    return out


def body(html, listing=False, **extra):
    """One competitor body: its key-word tokens, its sentence chunks and its listing label."""
    text = TD._body_text(html)
    return dict(extra, listing=bool(listing), tokens=KM.key_words(text), chunks=_chunks(text))


def _as_body(p):
    return p if isinstance(p, dict) else body(p)


def competitor_bodies(slug, root=ROOT):
    """Every non-blocked competitor page with a cache file, in keyword_metrics._rank order:
    [{"n", "rank", "url", "listing", "tokens", "chunks"}]. rank is 1-based over the
    non-blocked pages (a missing cache file keeps its rank and is skipped)."""
    bare = KM._bare(slug)
    path = pathlib.Path(root) / "data/queries/raw" / bare / "competitors.json"
    try:
        pages = json.loads(path.read_text(encoding="utf-8"))["pages"]
    except (OSError, ValueError, KeyError, TypeError):
        return []
    ranked = sorted(((n, p) for n, p in enumerate(pages, 1) if not p.get("blocked")),
                    key=KM._rank)
    out = []
    for rank, (n, p) in enumerate(ranked, 1):
        cached = pathlib.Path(root) / "data/queries/cache" / bare / f"{n}.html"
        if not cached.exists():
            continue
        html = cached.read_text(encoding="utf-8", errors="replace")
        listing = bool(QA.listing_reason(QA.page_metrics(html)))
        out.append(body(html, listing, n=n, rank=rank, url=p.get("url", "")))
    return out


def _count(ptoks, toks):
    return len(KM._starts(ptoks, toks, KM._index(toks))) if ptoks else 0


def _contains(big, small):
    n = len(small)
    return any(big[i:i + n] == small for i in range(len(big) - n + 1))


def _ok(gram):
    if gram[0] in STOP_GENERIC or gram[-1] in STOP_GENERIC:
        return False
    return not any(t in STOP_UI or JUNK.match(t) for t in gram)


def phrase_gaps(pages, board_terms, min_pages=2, limit=LIMIT):
    """Phrases (1–MAX_N key words) found on at least `min_pages` distinct pages and not inside
    any board term. `pages` are html strings or body() dicts. Each gap is
    {"term", "pages", "prose", "mentions"}, sorted by pages, prose pages, mentions (all
    descending), then term. A shorter phrase is dropped when a longer one containing it has
    the same pages and mentions (it adds nothing)."""
    bodies = [_as_body(p) for p in pages]
    covered = [KM.key_words(t) for t in board_terms]
    covered = [c for c in covered if c]
    seen = {}       # gram -> [pages, prose, mentions]
    for b in bodies:
        local = {}
        for ch in b["chunks"]:
            for n in range(1, MAX_N + 1):
                for i in range(len(ch) - n + 1):
                    g = tuple(ch[i:i + n])
                    local[g] = local.get(g, 0) + 1
        for g, c in local.items():
            if not _ok(g):
                continue
            s = seen.setdefault(g, [0, 0, 0])
            s[0] += 1
            s[1] += 0 if b.get("listing") else 1
            s[2] += c
    keep = {g: s for g, s in seen.items()
            if s[0] >= min_pages and not any(_contains(c, list(g)) for c in covered)}
    redundant = set()
    for g, s in keep.items():
        for n in range(1, len(g)):
            for i in range(len(g) - n + 1):
                sub = g[i:i + n]
                if sub in keep and keep[sub][0] == s[0] and keep[sub][2] == s[2]:
                    redundant.add(sub)
    rows = [{"term": " ".join(g), "pages": s[0], "prose": s[1], "mentions": s[2]}
            for g, s in keep.items() if g not in redundant]
    rows.sort(key=lambda r: (-r["pages"], -r["prose"], -r["mentions"], r["term"]))
    return rows[:limit]


def _names(e):
    return [x for x in [e.get("name")] + list(e.get("aliases") or []) if (x or "").strip()]


def entity_gaps(pages, ont, board_entity_ids):
    """Ontology entities no board section lists that at least one page names (its name or any
    alias as a whole key-word phrase): [{"id", "name", "class", "seen_on", "prose",
    "mentions"}], sorted by pages, prose pages, mentions (descending), then name."""
    bodies = [_as_body(p) for p in pages]
    listed = set(board_entity_ids or [])
    out = []
    for e in (ont or {}).get("entities", []):
        if not e.get("id") or e["id"] in listed:
            continue
        forms = [KM.key_words(x) for x in _names(e)]
        forms = [f for f in forms if f]
        seen = prose = mentions = 0
        for b in bodies:
            c = max((_count(f, b["tokens"]) for f in forms), default=0)
            if c:
                seen += 1
                prose += 0 if b.get("listing") else 1
                mentions += c
        if seen:
            out.append({"id": e["id"], "name": e.get("name", e["id"]),
                        "class": e.get("class", ""), "seen_on": seen, "prose": prose,
                        "mentions": mentions})
    out.sort(key=lambda r: (-r["seen_on"], -r["prose"], -r["mentions"], r["name"]))
    return out


def _types(board):
    types = {}
    for s in board.get("sections", []):
        for kind, vals in (s.get("keywords") or {}).items():
            bucket = types.setdefault(kind, [])
            for t in vals:
                if t.strip() and t.strip() not in bucket:
                    bucket.append(t.strip())
    return types


def by_type(board, pages):
    """[{"type", "ours", "found"}] per board keyword type, in board order: how many of our
    terms of that type, and how many of them at least one competitor body contains."""
    bodies = [_as_body(p) for p in pages]
    rows = []
    for kind, terms in _types(board).items():
        found = sum(1 for t in terms
                    if any(_count(KM.key_words(t), b["tokens"]) for b in bodies))
        rows.append({"type": kind, "ours": len(terms), "found": found})
    return rows


def relations_lines(ont, ids):
    """One line per ontology relation whose both ends are in `ids`; NOT FETCHED when the
    ontology carries no `relations` key."""
    rels = (ont or {}).get("relations")
    if rels is None:
        return [NO_RELATIONS]
    out = []
    for r in rels if isinstance(rels, list) else []:
        a = r.get("from") or r.get("subject") or r.get("source")
        b = r.get("to") or r.get("object") or r.get("target")
        kind = r.get("type") or r.get("predicate") or r.get("relation") or "related to"
        if a in ids and b in ids:
            out.append(f"- {a} — {kind} → {b}")
    return out or ["No ontology relation joins two entities on this board or in its gaps."]


def _board_entity_ids(board):
    return list(dict.fromkeys(i for s in board.get("sections", [])
                              for i in (s.get("entities") or [])))


def block(board, ont, root=ROOT):
    """Block 5c as markdown."""
    slug = board["meta"]["slug"]
    bodies = competitor_bodies(slug, root)
    prose = sum(1 for b in bodies if not b["listing"])
    head = (f"Measured on {len(bodies)} competitor pages ({prose} prose, "
            f"{len(bodies) - prose} listing)")
    if bodies:
        head += ": ranks " + ", ".join(str(b["rank"]) for b in bodies) + " — " + ", ".join(
            f"{b['rank']} {b['url']}{' (listing)' if b['listing'] else ''}" for b in bodies)
    else:
        head += f": {NO_PAGES}"
    out = [head]

    out.append("**Your keyword types against theirs**")
    out.append(TD._md(["Type", "Our terms", "Found on a competitor"],
                      [[r["type"], r["ours"], r["found"] if bodies else NO_PAGES]
                       for r in by_type(board, bodies)]))

    ids = _board_entity_ids(board)
    ents = {e["id"]: e for e in (ont or {}).get("entities", []) if e.get("id")}
    covered, _ = KM.board_terms({"sections": [{"keywords": s.get("keywords") or {}}
                                              for s in board.get("sections", [])]})
    covered = covered + [n for i in ids if i in ents for n in _names(ents[i])]
    out.append("**Phrases two or more competitors use and our board does not**")
    gaps = phrase_gaps(bodies, covered, min_pages=2)
    out.append(TD._md(["Phrase", "Pages", "Prose pages", "Mentions"],
                      [[g["term"], g["pages"], g["prose"], g["mentions"]] for g in gaps])
               if gaps else (NO_PAGES if not bodies else "None — no phrase on two pages is missing."))

    out.append("**Entities competitors name that no section lists (ontology only)**")
    egaps = entity_gaps(bodies, ont, ids)
    out.append(TD._md(["Entity", "Class", "Pages", "Prose pages"],
                      [[e["name"], e["class"], e["seen_on"], e["prose"]] for e in egaps])
               if egaps else (NO_PAGES if not bodies else "None — every ontology entity a "
                              "competitor names is already on a section."))
    out.append(SEED_NOTE)

    out.append("**Entity relationships on this page**")
    out.append("\n".join(relations_lines(ont, set(ids) | {e["id"] for e in egaps})))
    return "\n\n".join(out)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    usage = "usage: python3 scripts/term_gap.py <slug>"
    if len(argv) != 1:
        print(usage, file=sys.stderr)
        return 2
    path = ROOT / "data/boards" / f"{KM._bare(argv[0])}.json"
    if not path.is_file():
        print(f"{usage} — no board at {path.relative_to(ROOT)}", file=sys.stderr)
        return 2
    board = json.loads(path.read_text(encoding="utf-8"))
    ont = json.loads((ROOT / "data/bsuk-ontology.json").read_text(encoding="utf-8"))
    print(block(board, ont))
    return 0


if __name__ == "__main__":
    sys.exit(main())
