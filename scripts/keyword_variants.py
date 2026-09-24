#!/usr/bin/env python3
"""keyword_variants.py SLUG [--also DIR ...] [--root DIR]

Proposes the four optional keyword types a new location, comparison or blog board carries
(`variation`, `related`, `cooccurring`, `similar`) from the query files
bsuk-query-augmentation has ALREADY cached under data/queries/. It reads files only: no
network, no DataForSEO, no Firecrawl, so it costs nothing to run as often as a board is
redrafted.

  variation    surface forms of the page's head term that the cached text actually uses
               ("blue staffie puppies", "blue Staffordshire Bull Terrier puppies"), never
               the primary keyword itself. Attested, not generated: a spelling nobody
               searched or wrote is not a variation worth a sentence.
  related      the search engine's own related-searches box, verbatim, deduplicated.
  cooccurring  phrases of one to three words that appear in two or more cached documents
               (ranking titles and snippets, People Also Ask, the AI answer, competitor H2s,
               thread titles, the question file). Marketplace names and URLs are dropped.
  similar      how the pages that rank for the same query word it: organic titles and
               competitor H2s that share at least two content words with the primary.

The output is a PROPOSAL. The builder places each term in the section where it reads
naturally; family_rules' `keyword-variants-missing` check only asks that each type has at
least one term somewhere on the page.

--also DIR folds in one more folder under data/queries/raw/ (repeatable) — a neighbouring
keyword's cached SERP, e.g. registry-staffy-puppies-for-sale-leeds for Leeds, whose own SERP
was saved as URLs only. Its texts join the corpus; the primary keyword stays SLUG's.

Prints JSON: {"slug", "primary", "buckets": {type: [{"term", "sources", "df"}]}, "examined"}.
`df` is a count whose unit differs by bucket: for `variation` it is how many times the
surface form occurs across the cached texts; for `related` and `similar` it is how many
times the same term was listed (duplicates across files merged into one entry); for
`cooccurring` it is how many distinct cached documents contain the phrase (always >= 2).
Exit 0 printed · 2 bad usage (a slug outside [a-z0-9-]) · 6 no cached query data for SLUG,
or a cache folder with nothing readable in it (run bsuk-query-augmentation first).
"""
import argparse
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from query_augment import SYNONYMS, normalise  # noqa: E402  one spelling per thing, shared

EXIT_OK, EXIT_USAGE, EXIT_NO_CACHE = 0, 2, 6
SLUG = re.compile(r"^[a-z0-9-]+$")
BUCKET_CAP = {"variation": 8, "related": 10, "cooccurring": 12, "similar": 8}

STOP = frozenset("""a an the and or of to in on for with is are be can do does did i you your my
it its at by from as that this these those what how where when which who whom why if not no yes
we our us they their them there here any all more most than about before after up out get got so
just will would should could may might must s has have had was were been being into over under
also very much many such only own same other some each per via vs versus please near find found
see look looking one two three""".split())

# Words that make a phrase a page-furniture heading rather than a query ("Frequently Asked
# Questions", "Refine your results"). A title or H2 made only of these and stopwords is dropped.
FURNITURE = frozenset("frequently asked questions faq faqs refine results result featured ads latest "
                      "advice buyers buyer page menu contact home filter sort".split())

# Words that say nothing a primary keyword does not already say on a for-sale page, plus our
# own brand: a phrase made only of these (and stopwords, the primary's words and place names)
# is not a co-occurring term.
TRIVIAL = frozenset("sale buy buying bluestaffyuk".split())

WORD = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
URL = re.compile(r"\(?https?://[^\s)]+\)?")


def _load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _read(path):
    """A cached JSON object, or None: a missing, unreadable or non-object file reads as absent."""
    data = _load(path)
    return data if isinstance(data, dict) else None


def _list(x, key):
    """x[key] when x is an object and the value is a list, else []."""
    v = x.get(key) if isinstance(x, dict) else None
    return v if isinstance(v, list) else []


def _text(x, key):
    """An item's text whatever shape the cache saved it in: a bare string is itself, an
    object gives x[key] (when that is a string), anything else is empty."""
    if isinstance(x, str):
        return x
    if isinstance(x, dict) and isinstance(x.get(key), str):
        return x[key]
    return ""


def _canon(text):
    """Lowercase, curly quotes and trailing ellipses gone, one space."""
    t = (text or "").replace("’", "'").replace("…", " ").replace("...", " ")
    return re.sub(r"\s+", " ", t).strip().lower()


def _merge_spelling(tokens):
    """Apply the shared synonym table token-wise, keeping hyphens (so L-2-HGA survives)."""
    out = " ".join(tokens)
    for pat, rep in SYNONYMS:
        out = re.sub(pat, rep, out)
    return out.split()


def _tokens(text):
    return _merge_spelling(WORD.findall(URL.sub(" ", _canon(text))))


def _title_core(title):
    """A ranking page's title or H2 as a query: the site name after ` - ` / ` | ` dropped, a
    leading listing count ("12 Staffy Puppies…") dropped, trailing punctuation dropped."""
    t = re.split(r"\s[-|–—]\s", _canon(title))[0]
    t = re.sub(r"^\d+\s+", "", t).strip(" ,.:;!?&")
    words = t.split()
    while words and words[-1] in STOP:          # a title cut off at "...for sale in"
        words.pop()
    return " ".join(words)


def _domains(urls):
    """The registrable label of every ranking URL (`pets4homes`, `gumtree`, `staffie-owners`)
    — a phrase that names a marketplace is not a phrase a breeder's page should write. Only
    the WHOLE label is banned, in its hyphenated and joined forms (`staffy-owners`,
    `staffieowners`), normalised the way text tokens are; the words inside a hyphenated label
    (`owners`) stay usable. Each form is one token, since tokens keep their hyphens."""
    out = set()
    for u in urls:
        try:
            host = urlsplit(u if isinstance(u, str) else "").hostname or ""
        except ValueError:
            continue
        parts = [p for p in host.split(".") if p not in ("www", "co", "uk", "com", "org", "net")]
        if parts:
            for form in (parts[0], parts[0].replace("-", "")):
                out.add(" ".join(_tokens(form)))
    return {d for d in out if len(d) > 2}


def load_corpus(slug, root=ROOT):
    """Every cached text for SLUG, labelled by where it came from. None when nothing is cached."""
    root = Path(root)
    raw = root / "data" / "queries" / "raw" / slug
    qfile = _read(root / "data" / "queries" / f"{slug}.json")
    if not raw.is_dir() and qfile is None:
        return None
    related, titles, docs, urls = [], [], [], []

    def doc(label, text):
        if text and text.strip():
            docs.append((label, text))

    # Every read goes through _list/_text: a cache file saved as a list, or an item saved as
    # a bare string (the registry folders save People Also Ask that way), reads without a crash.
    g = _read(raw / "serp_google.json") or {}
    for q in _list(g, "questions"):
        detail = _text(q, "detail") if isinstance(q, dict) else ""
        if detail == "serp_google_related":
            related.append(("serp_google_related", _text(q, "text")))
        else:
            doc(detail or "serp_google", _text(q, "text"))
    for r in _list(g, "results"):
        urls.append(_text(r, "url"))
    resp = _read(raw / "serp_google.response.json") or {}
    for it in _list(resp, "items"):
        kind = it.get("type") if isinstance(it, dict) else None
        if kind == "organic":
            urls.append(_text(it, "url"))
            titles.append(("organic_title", _text(it, "title")))
            doc("organic_title", _text(it, "title"))
            doc("organic_snippet", _text(it, "description"))
        elif kind == "people_also_ask":
            for e in _list(it, "items"):
                doc("paa", _text(e, "title"))
        elif kind == "related_searches":
            for s in _list(it, "items"):
                related.append(("serp_google_related", _text(s, "text")))
        elif kind == "ai_overview":
            doc("ai_overview", _text(it, "text") or _text(it, "markdown"))
    b = _read(raw / "serp_bing.json") or {}
    for q in _list(b, "questions"):
        doc("serp_bing", _text(q, "text"))
    for r in _list(b, "results"):
        urls.append(_text(r, "url"))
    a = _read(raw / "ai_engines.json") or {}
    for q in _list(a, "questions"):
        doc("ai_question", _text(q, "text"))
    ar = _read(raw / "ai_engines.response.json") or {}
    for p in _list(ar, "answer_points"):
        doc("ai_answer", _text(p, "text"))
    for it in _list(ar, "items"):
        # One long answer is one document to the df count, however many paragraphs it has —
        # split it by paragraph and a phrase repeated in one answer would read as consensus.
        doc("ai_answer", _text(it, "markdown") or _text(it, "text"))
    t = _read(raw / "threads.json") or {}
    for th in _list(t, "threads"):
        doc("thread_title", _text(th, "title"))
    for q in _list(t, "questions"):
        doc("thread_question", _text(q, "text"))
    c = _read(raw / "competitors.json") or {}
    for p in _list(c, "pages"):
        urls.append(_text(p, "url"))
        for h in _list(p, "h2"):
            h = _text(h, "text")
            titles.append(("competitor_h2", h))
            doc("competitor_h2", h)
    for q in _list(qfile, "questions"):
        doc("question_file", _text(q, "question"))
    primary = _text(qfile, "primary_keyword") or slug.replace("-", " ")
    return {"primary": _canon(primary), "related": related, "titles": titles, "docs": docs,
            "domains": _domains(urls)}


def _geo_words(root):
    rows = _load(Path(root) / "data" / "locations.json")       # a list of {"city": ...}
    words = {"uk", "england", "scotland", "wales"}
    for r in rows if isinstance(rows, list) else []:
        words.update(WORD.findall(_canon(re.sub(r"\(.*?\)", "", _text(r, "city")))))
    return words


def _bucket(items):
    """[(term, source)] -> [{"term", "sources", "df"}], first spelling wins, order kept."""
    out = OrderedDict()
    for term, src in items:
        key = normalise(term)
        if not key:
            continue
        if key not in out:
            out[key] = {"term": term, "sources": [], "df": 0}
        out[key]["df"] += 1
        if src not in out[key]["sources"]:
            out[key]["sources"].append(src)
    return list(out.values())


def _related(corpus):
    return _bucket([(_canon(t), src) for src, t in corpus["related"] if _canon(t)])


def _variations(corpus, geo):
    """Word windows (2-6 words) whose normalised form is the head term, the head term plus the
    place, or the head minus `puppy` — and whose surface differs from the primary's."""
    pnorm = normalise(corpus["primary"])
    head = " ".join(w for w in pnorm.split() if w not in geo and w not in ("for", "sale"))
    core = " ".join(w for w in head.split() if w != "puppy")
    targets = {pnorm, head} | ({core} if len(core.split()) >= 2 else set())
    seen = Counter()
    first = {}
    for src, text in corpus["docs"] + corpus["titles"]:
        words = re.findall(r"[a-z0-9]+(?:['-][a-z0-9]+)*", URL.sub(" ", _canon(text)))
        for n in range(2, 7):
            for i in range(len(words) - n + 1):
                surface = " ".join(words[i:i + n])
                if normalise(surface) in targets and surface != corpus["primary"]:
                    seen[surface] += 1
                    first.setdefault(surface, src)
    ranked = sorted(seen, key=lambda s: (-seen[s], s))
    return [{"term": s, "sources": [first[s]], "df": seen[s]} for s in ranked][:BUCKET_CAP["variation"]]


def _similar(corpus, related):
    pwords = {w for w in normalise(corpus["primary"]).split() if w not in STOP}
    taken = {normalise(r["term"]) for r in related} | {normalise(corpus["primary"])}
    items = []
    for src, title in corpus["titles"]:
        core = _title_core(title)
        words = set(normalise(core).split())
        if not words or words <= (FURNITURE | STOP):
            continue
        if len(words & pwords) >= 2 and normalise(core) not in taken:
            items.append((core, src))
    return _bucket(items)[:BUCKET_CAP["similar"]]


def _cooccurring(corpus, geo):
    pwords = set(normalise(corpus["primary"]).split())
    # A label that normalises to a word of the primary (puppies.co.uk -> `puppy`) cannot be
    # told apart from the word itself; banning it would drop every phrase that says puppy.
    banned = {d for d in corpus["domains"] if d not in pwords}
    df, where = Counter(), {}
    for src, text in corpus["docs"]:
        toks = _tokens(text)
        grams = set()
        for n in (1, 2, 3):
            for i in range(len(toks) - n + 1):
                g = toks[i:i + n]
                if g[0] in STOP or g[-1] in STOP:
                    continue
                if any(t.isdigit() for t in g) or any(t == "bluestaffyuk" for t in g):
                    continue
                # A marketplace's whole label, matched as a phrase: tokens keep their hyphens,
                # so `staffy-owners` is one token and plain `owners` never matches it.
                if any(f" {d} " in f" {' '.join(g)} " for d in banned):
                    continue
                if all(t in pwords or t in geo or t in STOP or t in TRIVIAL for t in g):
                    continue
                # A lone word is a term only when it is a coined one (L-2-HGA, HC-HSF4);
                # "health" or "parents" alone is vocabulary, not a keyword.
                if n == 1 and "-" not in g[0]:
                    continue
                grams.add(" ".join(g))
        for g in grams:
            df[g] += 1
            where.setdefault(g, [])
            if src not in where[g]:
                where[g].append(src)
    keep = {g: c for g, c in df.items() if c >= 2}
    # A shorter phrase that only ever appears inside a longer kept one says nothing the
    # longer one does not ("kennel" inside "kennel club"): drop it.
    for g in list(keep):
        if any(g != h and f" {g} " in f" {h} " and keep[h] == keep[g] for h in keep):
            del keep[g]
    ranked = sorted(keep, key=lambda g: (-keep[g], -len(g.split()), g))
    return [{"term": g, "sources": where[g], "df": keep[g]} for g in ranked][:BUCKET_CAP["cooccurring"]]


def propose(slug, root=ROOT, also=()):
    corpus = load_corpus(slug, root)
    if corpus is None:
        return None
    for extra in also:
        more = load_corpus(extra, root)
        if more is None or not (Path(root) / "data" / "queries" / "raw" / extra).is_dir():
            return None
        for key in ("related", "titles", "docs"):
            corpus[key] += more[key]
        corpus["domains"] |= more["domains"]
    geo = _geo_words(root)
    related = _related(corpus)[:BUCKET_CAP["related"]]
    return {
        "slug": slug,
        "primary": corpus["primary"],
        "buckets": {
            "variation": _variations(corpus, geo),
            "related": related,
            "cooccurring": _cooccurring(corpus, geo),
            "similar": _similar(corpus, related),
        },
        "examined": {"documents": len(corpus["docs"]), "titles": len(corpus["titles"]),
                     "related": len(corpus["related"])},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--also", action="append", default=[], metavar="DIR")
    ap.add_argument("--root", default=str(ROOT))
    args = ap.parse_args(argv)
    bad = [s for s in [args.slug, *args.also] if not SLUG.match(s)]
    if bad:
        print(f"keyword_variants: not a slug: {bad[0]!r}", file=sys.stderr)
        return EXIT_USAGE
    out = propose(args.slug, Path(args.root), args.also)
    if out is None:
        print(f"keyword_variants: no cached query data for {' / '.join([args.slug, *args.also])} under data/queries/ — "
              "run bsuk-query-augmentation first", file=sys.stderr)
        return EXIT_NO_CACHE
    if not any(out["examined"].values()):
        print(f"keyword_variants: the cache for {' / '.join([args.slug, *args.also])} under data/queries/ holds "
              "nothing readable (empty or unparseable files) — re-run bsuk-query-augmentation", file=sys.stderr)
        return EXIT_NO_CACHE
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
