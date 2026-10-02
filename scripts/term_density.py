#!/usr/bin/env python3
"""Board block 4c: per-term density on each competitor body, and two target bands for us.

Counts every board keyword term (keyword_metrics.board_terms) plus every board entity name
(the ontology `name` for each id in the sections' "entities") on each of the top five
non-blocked, non-listing competitor bodies cached under data/queries/cache/<slug>/. Per term
it reports min / median / mean / max occurrences and two targets scaled to OUR word target
(the sum of the sections' "words", the midpoint of each {min, max}), per 1,000 words:

  median band = [p25, p75] of competitor density x our_words / 1000
  leader band = [p75, max] of competitor density x our_words / 1000

Counting uses keyword_metrics' matching (key_words + _starts over the _Page body), so the
numbers in 4b and 4c mean the same thing. A competitor with no cache file is skipped, never
counted as zero; no competitor body at all is "NOT FETCHED — <reason>".

    python3 scripts/term_density.py <slug>
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import keyword_metrics as KM  # noqa: E402
import query_augment as QA  # noqa: E402

ROOT = KM.ROOT
TOP = KM.TOP
NOT_FETCHED = "NOT FETCHED — no cached competitor page"


def _body_text(html):
    p = KM._Page()
    p.feed(html)
    p.close()
    return " ".join(r[0] for r in p.body())


def _body_tokens(html):
    return KM.key_words(_body_text(html))


def count_terms(html, terms):
    """{"counts": {term: occurrences in the body}, "words": the body's word count}.

    The word count is every word (small words included) of the same _Page body the terms
    are counted in, so a density never divides by a different scope: query_augment's
    page_metrics word_count can read a far smaller scope (51 words against a 600-word body on
    englishbluestaffypuppies.com), which would inflate that page's density tenfold."""
    text = _body_text(html)
    toks = KM.key_words(text)
    idx = KM._index(toks)
    counts = {}
    for term in dict.fromkeys(terms):
        tt = KM.key_words(term)
        counts[term] = len(KM._starts(tt, toks, idx)) if tt else 0
    words = len(KM.words(text))
    return {"counts": counts, "words": words}


def _pct(vals, q):
    """Linear-interpolated percentile, q in [0, 1]."""
    s = sorted(vals)
    if not s:
        return 0.0
    pos = (len(s) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def term_row(term, pages, our_words):
    """One table row for `term` over the counted competitor `pages`."""
    if not pages:
        return {"term": term, "note": NOT_FETCHED}
    counts = [p["counts"].get(term, 0) for p in pages]
    dens = [c / p["words"] * 1000 for c, p in zip(counts, pages) if p.get("words")]
    scale = (our_words or 0) / 1000.0

    def band(a, b):
        return (int(round(a * scale)), int(round(b * scale)))

    return {
        "term": term,
        "min": min(counts), "max": max(counts),
        "median": _pct(counts, 0.5),
        "mean": round(sum(counts) / len(counts), 1),
        "seen_on": sum(1 for c in counts if c), "of": len(counts),
        "target_median": band(_pct(dens, 0.25), _pct(dens, 0.75)) if dens else (0, 0),
        "target_leader": band(_pct(dens, 0.75), max(dens)) if dens else (0, 0),
        "note": "",
    }


def competitor_pages(slug, terms, root=ROOT):
    """count_terms() for the top TOP non-blocked, cached, non-listing competitor pages."""
    bare = KM._bare(slug)
    path = pathlib.Path(root) / "data/queries/raw" / bare / "competitors.json"
    try:
        pages = json.loads(path.read_text(encoding="utf-8"))["pages"]
    except (OSError, ValueError, KeyError, TypeError):
        return []
    ranked = sorted(((n, p) for n, p in enumerate(pages, 1) if not p.get("blocked")),
                    key=KM._rank)
    out = []
    for n, p in ranked:
        if len(out) >= TOP:
            break
        cached = pathlib.Path(root) / "data/queries/cache" / bare / f"{n}.html"
        if not cached.exists():
            continue
        html = cached.read_text(encoding="utf-8", errors="replace")
        if QA.listing_reason(QA.page_metrics(html)):
            continue
        out.append(dict(count_terms(html, terms), url=p.get("url", "")))
    return out


def board_entity_names(board, ont):
    names = {e["id"]: e["name"] for e in (ont or {}).get("entities", []) if e.get("id")}
    ids = [i for s in board.get("sections", []) for i in (s.get("entities") or [])]
    return list(dict.fromkeys(names[i] for i in ids if i in names))


def _section_words(sec):
    """A section's word target: an int, or the midpoint of a board's {"min", "max"}."""
    w = sec.get("words") or 0
    if isinstance(w, dict):
        return (int(w.get("min") or 0) + int(w.get("max") or 0)) // 2
    return int(w)


def rows(board, ont, root=ROOT):
    """(one term_row per board term and entity name, the competitor pages counted)."""
    terms, _ = KM.board_terms(board)
    terms = list(dict.fromkeys(terms + board_entity_names(board, ont)))
    our_words = sum(_section_words(s) for s in board.get("sections", []))
    pages = competitor_pages(board["meta"]["slug"], terms, root)
    return [term_row(t, pages, our_words) for t in terms], pages


def _md(head, body):
    def esc(v):
        return str(v).replace("|", "\\|")
    lines = ["| " + " | ".join(esc(h) for h in head) + " |",
             "|" + "|".join("---" for _ in head) + "|"]
    lines += ["| " + " | ".join(esc(c) for c in r) + " |" for r in body]
    return "\n".join(lines)


def table(board, ont, root=ROOT):
    rs, pages = rows(board, ont, root)
    head = ["Term", "Seen on", "Min", "Median", "Mean", "Max",
            "Target · median band", "Target · leader band"]
    body = []
    for r in rs:
        if r.get("note"):
            body.append([r["term"], r["note"], "", "", "", "", "", ""])
            continue
        body.append([r["term"], f"{r['seen_on']}/{r['of']}", r["min"], r["median"], r["mean"],
                     r["max"], "{}–{}".format(*r["target_median"]),
                     "{}–{}".format(*r["target_leader"])])
    urls = ", ".join(p["url"] for p in pages)
    return f"Counted on {len(pages)} competitor bodies: {urls or 'NOT FETCHED'}\n\n" + _md(head, body)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python3 scripts/term_density.py <slug>", file=sys.stderr)
        return 2
    bare = KM._bare(argv[0])
    board = json.loads((ROOT / "data/boards" / f"{bare}.json").read_text(encoding="utf-8"))
    ont = json.loads((ROOT / "data/bsuk-ontology.json").read_text(encoding="utf-8"))
    print(table(board, ont))
    return 0


if __name__ == "__main__":
    sys.exit(main())
