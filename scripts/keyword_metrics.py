#!/usr/bin/env python3
"""keyword_metrics.py — our page against the top five competitors, in numbers (CAG §7a).

Parity build, Task 18. One row per page: body words, how many of the board's keyword terms the
body carries (unique and total mentions), how many of its `variation` terms, the primary
keyword's exact matches per tag (title, H1, H2s, image alts, meta description), whether it
sits in the first 100 words of <main>, and whether the title is front-loaded with it.

  ours         the built page (dist/) once data/facts/rebuilt.json lists the slug; before
               that, the board's planned tags only (title, description, H1, section H2s)
  competitors  the first five unblocked pages of data/queries/raw/<slug>/competitors.json
               (Google order, then Bing), measured from the HTML --extract-h2 already saved
               in data/queries/cache/<slug>/<n>.html; with no cache file, the tag columns come
               from the page's saved `metrics` and the body columns are NOT FETCHED.
               A listing page (Task 17: query_augment._prose_problem, a card grid or listing
               JSON-LD) keeps its row but is marked `listing` and its note says LISTING: its
               body columns count marketplace card text, not a competitor's prose

Matching is by words: case and the small words (a, an, the, in, for, of, to, and, at, on,
with, from, by, is, are) are ignored, so "Blue Staffy Puppies in Manchester" matches
"blue staffy puppies manchester". No stemming: "puppy" is not "puppies".

Two checks fail a NEW page (family_rules scope; FAIL from `boarded` on, WARN on a draft):
  title-front-load   the picked title does not begin with the primary keyword (Rule 21 step 1)
  first-100-words    the rebuilt, built page does not carry the primary keyword in the first
                     100 words of <main> (a page not yet rebuilt measures nothing)

Usage:
  python3 scripts/keyword_metrics.py <board slug> [--json] [--out PATH]
      prints the markdown table (or the JSON with --json) and writes the JSON to --out,
      default docs/reports/keyword-metrics/<key>.json (gitignored).
      exit 0 · 1 a FAIL finding · 2 bad usage or an unreadable board
"""
import argparse
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import page_sections as PS  # noqa: E402  (imports nothing from the board scripts)
import query_augment as QA  # noqa: E402  (stdlib only; Task 17's prose-vs-listing classifier)

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORTS = ROOT / "docs" / "reports" / "keyword-metrics"
TOP = 5
FIRST_WORDS = 100
STOP = frozenset({"a", "an", "the", "in", "for", "of", "to", "and", "at", "on", "with", "from",
                  "by", "is", "are"})
TOKEN = re.compile(r"[a-z0-9£]+(?:'[a-z]+)?")
SKIP = {"script", "style", "template", "noscript", "svg", "nav", "footer", "aside", "form",
        "head", "title", "select"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source",
        "track", "wbr"}
_BOARDED_OR_LATER = PS.statuses_from("boarded")


# ── matching ────────────────────────────────────────────────────────────────────────────────
def words(text):
    return TOKEN.findall((text or "").replace("’", "'").lower())


def key_words(text):
    return [w for w in words(text) if w not in STOP]


def phrase_count(phrase, text):
    """How many times `phrase` occurs in `text`, small words and case ignored."""
    p, t = key_words(phrase), key_words(text)
    if not p:
        return 0
    return sum(1 for i in range(len(t) - len(p) + 1) if t[i:i + len(p)] == p)


def front_loaded(primary, title):
    p = key_words(primary)
    return bool(p) and key_words(title)[:len(p)] == p


# ── one page ────────────────────────────────────────────────────────────────────────────────
class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.title = None
        self.description = None
        self.h1, self.h2, self.alts = [], [], []
        self.body, self.main = [], []
        self._title = None
        self._head = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title" and self.title is None and "svg" not in self.stack:
            self._title = []
        if tag == "meta" and (a.get("name") or "").lower() == "description" and self.description is None:
            self.description = a.get("content") or ""
        if tag == "img" and not any(t in SKIP for t in self.stack):
            self.alts.append(a.get("alt") or "")
        if tag in ("h1", "h2") and self._head is None:
            self._head = (tag, [])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "title" and self._title is not None:
            self.title, self._title = "".join(self._title), None
        if self._head is not None and tag == self._head[0]:
            text = " ".join("".join(self._head[1]).split())
            if not any(t in SKIP for t in self.stack):
                (self.h1 if tag == "h1" else self.h2).append(text)
            self._head = None
        if tag in self.stack:
            del self.stack[len(self.stack) - 1 - self.stack[::-1].index(tag):]

    def handle_data(self, data):
        if self._title is not None:
            self._title.append(data)
        if any(t in SKIP for t in self.stack):
            return
        if self._head is not None:
            self._head[1].append(data)
        self.body.append(data)
        if "main" in self.stack:
            self.main.append(data)


def measure_html(html, primary, terms, variations):
    """The row numbers for one page. Body = <main> when the page has one, else every visible
    word outside navigation, footer, aside, form and the <head>."""
    p = _Page()
    p.feed(html)
    p.close()
    body = " ".join(p.main) if p.main else " ".join(p.body)
    found = {t: phrase_count(t, body) for t in dict.fromkeys(terms) if key_words(t)}
    title = p.title or ""
    return {
        "words": len(words(body)),
        "unique_terms": sum(1 for n in found.values() if n),
        "mentions": sum(found.values()),
        "variations": sum(1 for v in dict.fromkeys(variations) if phrase_count(v, body)),
        "exact": {"title": phrase_count(primary, title),
                  "h1": sum(phrase_count(primary, h) for h in p.h1),
                  "h2": sum(1 for h in p.h2 if phrase_count(primary, h)),
                  "alt": sum(1 for a in p.alts if phrase_count(primary, a)),
                  "description": phrase_count(primary, p.description or "")},
        "first_100": phrase_count(primary, " ".join(words(body)[:FIRST_WORDS])) > 0,
        "title_front": front_loaded(primary, title),
    }


# ── the board ───────────────────────────────────────────────────────────────────────────────
def board_terms(board):
    """(every keyword term on the board, its `variation` terms), first spelling kept."""
    terms, variations = [], []
    for s in board["sections"]:
        for kind, vals in s["keywords"].items():
            for t in vals:
                if t.strip():
                    terms.append(t.strip())
                    if kind == "variation":
                        variations.append(t.strip())
    return list(dict.fromkeys(terms)), list(dict.fromkeys(variations))


def board_row(board):
    """Our row before the page is built: the tags the board has picked, body columns empty."""
    import pageboard as PB   # lazy: pageboard imports family_rules, which imports this module
    primary = board["brief"]["primary_keyword"]
    title, desc = PB.meta_pick(board)
    h2s = [s["heading"] for s in board["sections"] if s.get("shape") != "hero"]
    return {"who": "ours (board)", "words": None, "unique_terms": None, "mentions": None,
            "variations": None,
            "exact": {"title": phrase_count(primary, title),
                      "h1": phrase_count(primary, PB.picked_h1(board)),
                      "h2": sum(1 for h in h2s if phrase_count(primary, h)),
                      "alt": None, "description": phrase_count(primary, desc)},
            "first_100": None, "title_front": front_loaded(primary, title),
            "note": "not built — the board's picked title, description, H1 and section H2s"}


def _rel(path):
    try:
        return pathlib.Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _bare(slug):
    return slug.strip("/").rsplit("/", 1)[-1]


def ours_row(board, dist=None, rebuilt=None):
    """The built page when the slug is rebuilt and built, else the board row."""
    import pageboard as PB
    slug = board["meta"]["slug"]
    rebuilt = PB.rebuilt_slugs() if rebuilt is None else rebuilt
    page = PB.built_page(slug, dist)
    if _bare(slug) in rebuilt and page.exists():
        terms, variations = board_terms(board)
        row = measure_html(page.read_text(encoding="utf-8", errors="ignore"),
                           board["brief"]["primary_keyword"], terms, variations)
        return dict({"who": "ours (built)"}, **row, note=_rel(page))
    return board_row(board)


# ── competitors ─────────────────────────────────────────────────────────────────────────────
def _rank(item):
    _, p = item
    return (p.get("google_pos") or 99, p.get("bing_pos") or 99, p.get("url", ""))


def _listing(p, html=None):
    """Why Task 17 reads this competitor page as a listing, or None. A cached page is
    classified from its own HTML (query_augment.page_metrics), else from its saved metrics."""
    if html is not None:
        p = dict(p, metrics=QA.page_metrics(html))
    why = QA._prose_problem(p) or ""
    return why[len("listing: "):] if why.startswith("listing: ") else None


def _mark(row, listing):
    row["listing"] = listing
    if listing:
        row["note"] = f"LISTING — {listing}; body columns count card text, not prose · {row['note']}"
    return row


def competitor_rows(slug, primary, terms, variations, root=ROOT):
    """Rows for the first TOP unblocked pages of raw/<slug>/competitors.json."""
    bare = _bare(slug)
    path = pathlib.Path(root) / "data/queries/raw" / bare / "competitors.json"
    try:
        pages = json.loads(path.read_text(encoding="utf-8"))["pages"]
    except (OSError, ValueError, KeyError, TypeError):
        return [{"who": "competitors", "note": f"NOT FETCHED — no readable data/queries/raw/{bare}/"
                                               "competitors.json (bsuk-query-augmentation Step 3)"}]
    ranked = sorted(((n, p) for n, p in enumerate(pages, 1) if not p.get("blocked")), key=_rank)
    rows = []
    for n, p in ranked[:TOP]:
        cached = pathlib.Path(root) / "data/queries/cache" / bare / f"{n}.html"
        if cached.exists():
            html = cached.read_text(encoding="utf-8", errors="replace")
            row = measure_html(html, primary, terms, variations)
            rows.append(_mark(dict({"who": p["url"]}, **row, note="measured from data/queries/cache"),
                              _listing(p, html)))
            continue
        m = p.get("metrics") if isinstance(p.get("metrics"), dict) else {}
        title = m.get("title") or ""
        h2s = [s.get("h2", "") for s in m.get("sections", [])] or p.get("h2", [])
        rows.append(_mark({
            "who": p["url"], "words": m.get("word_count"), "unique_terms": None,
            "mentions": None, "variations": None,
            "exact": {"title": phrase_count(primary, title) if m else None, "h1": None,
                      "h2": sum(1 for h in h2s if phrase_count(primary, h)), "alt": None,
                      "description": phrase_count(primary, m.get("meta_description") or "") if m else None},
            "first_100": None, "title_front": front_loaded(primary, title) if m else None,
            "note": f"NOT FETCHED — data/queries/cache/{bare}/{n}.html is not on this machine; "
                    "tag columns from the saved metrics"}, _listing(p)))
    return rows


# ── checks (registered in family_rules) ────────────────────────────────────────────────────
def findings(board, dist=None, rebuilt=None):
    """[(check, severity, message)] for the two placement rules. Scope is the caller's:
    family_rules runs this on new location, comparison and blog pages only."""
    import pageboard as PB
    out = []
    primary = board["brief"]["primary_keyword"]
    sev = "FAIL" if board["meta"]["status"] in _BOARDED_OR_LATER else "WARN"
    title, _ = PB.meta_pick(board)
    if not front_loaded(primary, title):
        out.append(("title-front-load", sev,
                    f"the picked title {title!r} does not begin with the primary keyword "
                    f"{primary!r} (Rule 21 step 1; small words and case are ignored)"))
    slug = board["meta"]["slug"]
    rebuilt = PB.rebuilt_slugs() if rebuilt is None else rebuilt
    page = PB.built_page(slug, dist)
    if _bare(slug) in rebuilt and page.exists():
        m = measure_html(page.read_text(encoding="utf-8", errors="ignore"), primary, [], [])
        if not m["first_100"]:
            out.append(("first-100-words", "FAIL",
                        f"the built page does not carry {primary!r} in the first {FIRST_WORDS} "
                        f"words of <main> ({_rel(page)})"))
    return out


# ── the table ───────────────────────────────────────────────────────────────────────────────
def table(board, root=ROOT, dist=None, rebuilt=None):
    terms, variations = board_terms(board)
    primary = board["brief"]["primary_keyword"]
    return {"slug": board["meta"]["slug"], "primary_keyword": primary, "terms": len(terms),
            "rows": [ours_row(board, dist, rebuilt)]
            + competitor_rows(board["meta"]["slug"], primary, terms, variations, root)}


COLUMNS = ["Page", "Words", "Unique terms", "Mentions", "Variations", "Title", "H1", "H2",
           "Alt", "Description", "First 100", "Title front", "Note"]


def _cell(v):
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "yes" if v else "no"
    return str(v)


def cells(r):
    """One row as display strings, in COLUMNS order."""
    e = r.get("exact") or {}
    return [_cell(c) for c in (r["who"], r.get("words"), r.get("unique_terms"), r.get("mentions"),
                               r.get("variations"), e.get("title"), e.get("h1"), e.get("h2"),
                               e.get("alt"), e.get("description"), r.get("first_100"),
                               r.get("title_front"), r.get("note"))]


def markdown(t):
    lines = ["| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    for r in t["rows"]:
        lines.append("| " + " | ".join(c.replace("|", "\\|") for c in cells(r)) + " |")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--json", action="store_true", help="print the JSON instead of the table")
    ap.add_argument("--out", help="where to write the JSON (default docs/reports/keyword-metrics/<key>.json)")
    a = ap.parse_args(argv)
    import pageboard as PB
    try:
        board = PB.load_board(a.slug)
    except PB.BoardError as e:
        print(f"keyword-metrics ERROR {e}")
        return 2
    t = table(board)
    # The two checks bind new pages only (family_rules scope); the table is for any page.
    found = findings(board) if PB.FR.applies(board) else []
    t["findings"] = [{"check": c, "sev": s, "msg": m} for c, s, m in found]
    out = pathlib.Path(a.out) if a.out else REPORTS / (PB.slug_file(a.slug) + ".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(t, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(t, indent=2, ensure_ascii=False) if a.json else markdown(t))
    for f in t["findings"]:
        print(f"  {f['sev']:4s} {f['check']:18s} {f['msg']}")
    print(f"keyword-metrics {a.slug}: {len(t['rows'])} rows, {t['terms']} terms examined → {out}")
    return 1 if any(f["sev"] == "FAIL" for f in t["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
