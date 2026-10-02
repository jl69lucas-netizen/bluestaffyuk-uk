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
  phrases     1–3 word phrases on at least `min_domains` distinct competitor domains (a
              competitor is a domain: five pages of one marketplace are one voice) that no
              board term (nor board entity name) already covers; domains, pages, of which
              prose, and total mentions are the evidence. Shown as two tables, phrases of 2–3
              words first, then single words. Generic words may not open or close a phrase,
              and marketplace UI words, numbers, prices and single letters may not appear in it
  entities    ontology entities only (name or any alias as a whole key-word phrase) that no
              board section lists and at least one competitor page names. A Place that is
              another city of data/locations.json (or a county or region the ontology marks
              with place_type) is never proposed; it is named on one line under the table
  relations   the ontology's `relations`, filtered to ends on the board or in the gaps; the
              ontology has no `relations` key yet, which is written NOT FETCHED

    python3 scripts/term_gap.py <slug>
"""
import json
import pathlib
import re
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import keyword_metrics as KM  # noqa: E402
import query_augment as QA  # noqa: E402
import term_density as TD  # noqa: E402

ROOT = KM.ROOT
LIMIT = 30
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


def domain_of(url):
    """The url's host without "www.", lower-cased ("" when there is none)."""
    host = (urlsplit(url or "").netloc or "").lower().split("@")[-1].split(":")[0]
    return host[4:] if host.startswith("www.") else host


def body(html, listing=False, **extra):
    """One competitor body: its key-word tokens, its sentence chunks, its listing label and
    its domain (from extra["url"])."""
    text = TD._body_text(html)
    return dict(extra, listing=bool(listing), domain=domain_of(extra.get("url", "")),
                tokens=KM.key_words(text), chunks=_chunks(text))


def _bodies(pages):
    """body() dicts for html strings or dicts; a page with no domain counts as its own
    domain, so bare html fixtures are distinct competitors."""
    out = []
    for i, p in enumerate(pages):
        b = p if isinstance(p, dict) else body(p)
        if not b.get("domain"):
            b = dict(b, domain=f"page-{i + 1}")
        out.append(b)
    return out


def competitor_bodies(slug, root=ROOT):
    """Every non-blocked competitor page with a cache file, in keyword_metrics._rank order:
    [{"n", "rank", "url", "domain", "listing", "tokens", "chunks"}]. rank is 1-based over the
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


def phrase_gaps(pages, board_terms, min_domains=2, limit=None):
    """Phrases (1–MAX_N key words) found on at least `min_domains` distinct competitor domains
    and not inside any board term. `pages` are html strings or body() dicts. Each gap is
    {"term", "words", "domains", "pages", "prose", "mentions"}, sorted by domains, prose
    pages, mentions (all descending), then term; `limit` cuts the list (None keeps all). A
    shorter phrase is dropped when a longer one containing it has the same pages and
    mentions (it adds nothing)."""
    bodies = _bodies(pages)
    covered = [KM.key_words(t) for t in board_terms]
    covered = [c for c in covered if c]
    seen = {}       # gram -> {"domains": set, "pages", "prose", "mentions"}
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
            st = seen.setdefault(g, {"domains": set(), "pages": 0, "prose": 0, "mentions": 0})
            st["domains"].add(b["domain"])
            st["pages"] += 1
            st["prose"] += 0 if b.get("listing") else 1
            st["mentions"] += c
    keep = {g: st for g, st in seen.items()
            if len(st["domains"]) >= min_domains
            and not any(_contains(c, list(g)) for c in covered)}
    redundant = set()
    for g, st in keep.items():
        for n in range(1, len(g)):
            for i in range(len(g) - n + 1):
                sub = g[i:i + n]
                if (sub in keep and keep[sub]["pages"] == st["pages"]
                        and keep[sub]["mentions"] == st["mentions"]):
                    redundant.add(sub)
    rows = [{"term": " ".join(g), "words": len(g), "domains": len(st["domains"]),
             "pages": st["pages"], "prose": st["prose"], "mentions": st["mentions"]}
            for g, st in keep.items() if g not in redundant]
    rows.sort(key=lambda r: (-r["domains"], -r["prose"], -r["mentions"], r["term"]))
    return rows if limit is None else rows[:limit]


def _names(e):
    return [x for x in [e.get("name")] + list(e.get("aliases") or []) if (x or "").strip()]


def _entity_rows(pages, ont, board_entity_ids):
    bodies = _bodies(pages)
    listed = set(board_entity_ids or [])
    out = []
    for e in (ont or {}).get("entities", []):
        if not e.get("id") or e["id"] in listed:
            continue
        forms = [KM.key_words(x) for x in _names(e)]
        forms = [f for f in forms if f]
        domains, seen, prose, mentions = set(), 0, 0, 0
        for b in bodies:
            c = max((_count(f, b["tokens"]) for f in forms), default=0)
            if c:
                domains.add(b["domain"])
                seen += 1
                prose += 0 if b.get("listing") else 1
                mentions += c
        if seen:
            out.append({"id": e["id"], "name": e.get("name", e["id"]),
                        "class": e.get("class", ""), "place_type": e.get("place_type", ""),
                        "domains": len(domains), "seen_on": seen, "prose": prose,
                        "mentions": mentions})
    out.sort(key=lambda r: (-r["domains"], -r["seen_on"], -r["prose"], -r["mentions"],
                            r["name"]))
    return out


def _is_other_place(row, other_places):
    if row["class"] != "Place":
        return False
    return (row["name"].strip().lower() in other_places
            or (row.get("place_type") or "").lower() in ("county", "region"))


def entity_gaps(pages, ont, board_entity_ids, other_places=()):
    """Ontology entities no board section lists that at least one page names (its name or any
    alias as a whole key-word phrase): [{"id", "name", "class", "domains", "seen_on",
    "prose", "mentions"}], sorted by domains, pages, prose pages, mentions (descending), then
    name. A Place in `other_places` (lower-case names), or one the ontology marks
    place_type county or region, is left out: see other_places_named()."""
    others = {o.lower() for o in other_places}
    return [r for r in _entity_rows(pages, ont, board_entity_ids)
            if not _is_other_place(r, others)]


def other_places_named(pages, ont, board_entity_ids, other_places=()):
    """The Place rows entity_gaps() leaves out, most pages first, then name."""
    others = {o.lower() for o in other_places}
    rows = [r for r in _entity_rows(pages, ont, board_entity_ids) if _is_other_place(r, others)]
    return sorted(rows, key=lambda r: (-r["seen_on"], r["name"]))


def other_cities(slug, root=ROOT):
    """Lower-case city names of data/locations.json other than this slug's own ("Glasgow
    (breeding dogs)" read as Glasgow; the national "UK" rows are not a city)."""
    try:
        rows = json.loads((pathlib.Path(root) / "data/locations.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    bare = KM._bare(slug)
    own = {re.sub(r"\s*\(.*\)\s*$", "", r.get("city") or "").strip().lower()
           for r in rows if r.get("slug") == bare}
    names = {re.sub(r"\s*\(.*\)\s*$", "", r.get("city") or "").strip().lower() for r in rows}
    return {n for n in names if n and n != "uk"} - own


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
    bodies = _bodies(pages)
    rows = []
    for kind, terms in _types(board).items():
        found = sum(1 for t in terms
                    if any(_count(KM.key_words(t), b["tokens"]) for b in bodies))
        rows.append({"type": kind, "ours": len(terms), "found": found})
    return rows


def relations_lines(ont, ids):
    """One line per ontology relation whose both ends are in `ids`; NOT FETCHED when the
    ontology carries no `relations` key.

    The shape is GUESSED: data/bsuk-ontology.json has no `relations` key yet, so the field
    names read here ({from|subject|source, type|predicate|relation, to|object|target}) are
    an assumption to check against the real key when it lands."""
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


def _domain_line(bodies):
    groups = {}
    for b in bodies:
        groups.setdefault(b["domain"], []).append(b)
    parts = []
    for d, bs in groups.items():
        lst = sum(1 for b in bs if b["listing"])
        kind = ("listing" if lst == len(bs) else "prose" if not lst
                else f"{lst} listing, {len(bs) - lst} prose")
        parts.append(f"{d} ×{len(bs)} ({kind})")
    return len(groups), "; ".join(parts)


def _phrase_table(rows, empty):
    if not rows:
        return empty
    return TD._md(["Phrase", "Domains", "Pages", "Prose pages", "Mentions"],
                  [[g["term"], g["domains"], g["pages"], g["prose"], g["mentions"]]
                   for g in rows])


def block(board, ont, root=ROOT):
    """Block 5c as markdown."""
    slug = board["meta"]["slug"]
    bodies = competitor_bodies(slug, root)
    prose = sum(1 for b in bodies if not b["listing"])
    head = (f"Measured on {len(bodies)} competitor pages ({prose} prose, "
            f"{len(bodies) - prose} listing)")
    if bodies:
        n_dom, line = _domain_line(bodies)
        head += (f" on {n_dom} domains: {line}. Ranks "
                 + ", ".join(str(b["rank"]) for b in bodies) + ".")
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
    gaps = phrase_gaps(bodies, covered, min_domains=2)
    none = NO_PAGES if not bodies else "None — nothing on two domains is missing."
    out.append("**Phrases two or more competitors use and our board does not**")
    out.append("Phrases (2–3 words)")
    out.append(_phrase_table([g for g in gaps if g["words"] > 1][:LIMIT], none))
    out.append("Single words")
    out.append(_phrase_table([g for g in gaps if g["words"] == 1][:LIMIT], none))

    out.append("**Entities competitors name that no section lists (ontology only)**")
    others = other_cities(slug, root)
    egaps = entity_gaps(bodies, ont, ids, others)
    out.append(TD._md(["Entity", "Class", "Domains", "Pages", "Prose pages"],
                      [[e["name"], e["class"], e["domains"], e["seen_on"], e["prose"]]
                       for e in egaps])
               if egaps else (NO_PAGES if not bodies else "None — every ontology entity a "
                              "competitor names is already on a section."))
    named = other_places_named(bodies, ont, ids, others)
    if named:
        out.append("Other places named on competitor pages (not proposed for this page): "
                   + ", ".join(f"{e['name']} ({e['seen_on']})" for e in named))
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
