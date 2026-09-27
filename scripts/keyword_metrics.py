#!/usr/bin/env python3
"""keyword_metrics.py — our page against the top five competitors, in numbers (CAG §7a).

Parity build, Task 18. One row per page: body words, how many of the board's keyword terms the
body carries (unique and total mentions), how many of its `variation` terms, the primary
keyword's exact matches per tag (title, H1, H2s, image alts, meta description), whether it
sits in the page's opening 100 words, and whether the title is front-loaded with it.

  ours         the built page (dist/) once data/facts/rebuilt.json lists the slug; before
               that, the board's planned tags only (title, description, H1, section H2s and
               the block-7 image alts in `assets`)
  competitors  the first five unblocked pages of data/queries/raw/<slug>/competitors.json
               (Google order, then Bing), measured from the HTML --extract-h2 already saved
               in data/queries/cache/<slug>/<n>.html; with no cache file, the tag columns come
               from the page's saved `metrics` and the body columns are NOT FETCHED.
               A listing page (query_augment.listing_reason: a card grid or listing JSON-LD)
               keeps its row but is marked `listing` and its note says LISTING: its body
               columns count marketplace card text, not a competitor's prose

Columns:
  Words          query_augment.page_metrics' word_count, the one definition the word target
                 uses (scope <main>, else the one <article>, else <body>; furniture, consent
                 dialogs and hidden subtrees out); the board row has none
  Unique terms   board keyword terms found at least once in the body (<main>, else <body>)
  Mentions       term matches in the body, the longest match only where terms overlap
                 ("blue staffy puppies manchester" is one mention, not also "puppies manchester")
  Variations     the board's `variation` terms found at least once
  Title, H1, Description   occurrences of the primary keyword in that text
  H2, Alt        elements (H2 headings, image alts) that carry the primary keyword
  First 100      the primary keyword in the first 100 words of opening copy: body text after
                 the H1 inside <main> (else <body>), headings, eyebrows, a later <header>,
                 furniture and hidden subtrees skipped; a page with no H1 counts from the start
  Title front    the title gate below

Count columns match by words: case and the small words (a, an, the, in, for, of, to, and, at,
on, with, from, by, is, are) are ignored, so "Blue Staffy Puppies in Manchester" matches
"blue staffy puppies manchester". No stemming there: "puppy" is not "puppies".

The title gate normalises instead (query_augment.normalise: plurals and synonyms, so
"Staffies Puppy" is "staffy puppy"): the title's first word is the primary keyword's first
word, and every primary keyword word appears in order within the title's first
len(primary) + TITLE_SLACK words, so "Blue Staffy Puppies for Sale in Manchester" passes for
"blue staffy puppies manchester" and "Manchester Blue Staffy Puppies" does not.

Checks on a NEW page (family_rules scope):
  primary-keyword    FAIL: the board has no primary keyword (nothing else can be measured)
  title-front-load   the picked title fails the title gate (Rule 21 step 1); FAIL from
                     `boarded` on, WARN on a draft
  first-100-words    FAIL: the rebuilt, built page does not carry the primary keyword in its
                     first 100 words of opening copy (a page not yet rebuilt measures nothing)

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
import query_augment as QA  # noqa: E402  (stdlib only: normalise, page_metrics, listing_reason)

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORTS = ROOT / "docs" / "reports" / "keyword-metrics"
TOP = 5
FIRST_WORDS = 100
TITLE_SLACK = 3          # connector words the title gate allows ("for sale in")
STOP = frozenset({"a", "an", "the", "in", "for", "of", "to", "and", "at", "on", "with", "from",
                  "by", "is", "are"})
TOKEN = re.compile(r"[a-z0-9£]+(?:'[a-z]+)?")
SKIP = {"script", "style", "template", "noscript", "svg", "nav", "footer", "aside", "form",
        "head", "title", "select"}
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source",
        "track", "wbr"}
HIDDEN_STYLE = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden", re.I)
_BOARDED_OR_LATER = PS.statuses_from("boarded")


# ── matching ────────────────────────────────────────────────────────────────────────────────
def words(text):
    return TOKEN.findall((text or "").replace("’", "'").lower())


def key_words(text):
    return [w for w in words(text) if w not in STOP]


def _index(toks):
    idx = {}
    for i, w in enumerate(toks):
        idx.setdefault(w, []).append(i)
    return idx


def _starts(ptoks, toks, idx):
    n = len(ptoks)
    return [i for i in idx.get(ptoks[0], ()) if toks[i:i + n] == ptoks] if ptoks else []


def phrase_count(phrase, text):
    """How many times `phrase` occurs in `text`, small words and case ignored."""
    t = key_words(text)
    return len(_starts(key_words(phrase), t, _index(t)))


def _gate_words(text):
    return QA.normalise(text).split()


def front_load_problem(primary, title):
    """Why `title` is not front-loaded with `primary` (the title gate), or None."""
    p = [w for w in _gate_words(primary) if w not in STOP]
    if not p:
        return "no primary keyword"
    t = _gate_words(title)
    window = t[:len(p) + TITLE_SLACK]
    why = []
    if not t or t[0] != p[0]:
        why.append(f"it starts with {(t[0] if t else '')!r}, not {p[0]!r}")
    j, late = 0, []
    for w in p:
        if w in window[j:]:
            j = window.index(w, j) + 1
        else:
            late.append(w)
    order = [w for w in late if w in window]
    gone = [w for w in late if w not in window]
    if order:
        why.append("out of order: " + ", ".join(order))
    if gone:
        why.append(f"not within its first {len(p) + TITLE_SLACK} words: " + ", ".join(gone))
    return "; ".join(why) or None


def front_loaded(primary, title):
    return front_load_problem(primary, title) is None


# ── one page ────────────────────────────────────────────────────────────────────────────────
def _hidden(a):
    return ("hidden" in a or (a.get("aria-hidden") or "").lower() == "true"
            or bool(HIDDEN_STYLE.search(a.get("style") or "")))


class _Page(HTMLParser):
    """Tags and text for one page. Each text run is kept with (in <main>, after the H1, part
    of the opening copy), so the body and the opening 100 words are cut after the parse."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []             # [(tag, skipped, not opening copy)]
        self.title = None
        self.description = None
        self.h1, self.h2, self.alts = [], [], []
        self.runs = []              # (text, in_main, after_h1, opening)
        self.has_main = False
        self.after_h1 = False
        self._title = None
        self._head = None

    def _skipped(self):
        return bool(self.stack) and self.stack[-1][1]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title" and self.title is None and "svg" not in [s[0] for s in self.stack]:
            self._title = []
        if tag == "meta" and (a.get("name") or "").lower() == "description" and self.description is None:
            self.description = a.get("content") or ""
        if tag == "img" and not self._skipped():
            self.alts.append(a.get("alt") or "")
        if tag == "main":
            self.has_main = True
        if tag in ("h1", "h2") and self._head is None:
            self._head = (tag, [])
        if tag in VOID:
            return
        parent_skip = self._skipped()
        parent_closed = bool(self.stack) and self.stack[-1][2]
        skip = parent_skip or tag in SKIP or _hidden(a)
        not_opening = (parent_closed or tag in HEADINGS
                       or "eyebrow" in (a.get("class") or "").split()
                       or (tag == "header" and self.after_h1))
        self.stack.append((tag, skip, not_opening))

    def handle_endtag(self, tag):
        if tag == "title" and self._title is not None:
            self.title, self._title = "".join(self._title), None
        if self._head is not None and tag == self._head[0]:
            text = " ".join("".join(self._head[1]).split())
            if not self._skipped():
                (self.h1 if tag == "h1" else self.h2).append(text)
                if tag == "h1":
                    self.after_h1 = True
            self._head = None
        tags = [s[0] for s in self.stack]
        if tag in tags:
            del self.stack[len(tags) - 1 - tags[::-1].index(tag):]

    def handle_data(self, data):
        if self._title is not None:
            self._title.append(data)
        if self._skipped():
            return
        if self._head is not None:
            self._head[1].append(data)
        in_main = any(s[0] == "main" for s in self.stack)
        opening = not (self.stack and self.stack[-1][2])
        self.runs.append((data, in_main, self.after_h1, opening))

    def body(self):
        return [r for r in self.runs if r[1]] if self.has_main else list(self.runs)

    def opening(self):
        scope = self.body()
        after = [r for r in scope if r[2]]
        return [r[0] for r in (after if self.h1 and after else scope) if r[3]]


def measure_html(html, primary, terms, variations, metrics=None):
    """The row numbers for one page. `metrics` is query_augment.page_metrics(html) when the
    caller already has it (the Words column is its word_count)."""
    p = _Page()
    p.feed(html)
    p.close()
    metrics = QA.page_metrics(html) if metrics is None else metrics
    toks = key_words(" ".join(r[0] for r in p.body()))
    idx = _index(toks)
    spans, found = [], {}
    for term in dict.fromkeys(terms):
        tt = key_words(term)
        if not tt:
            continue
        starts = _starts(tt, toks, idx)
        found[term] = bool(starts)
        spans.extend((i, i + len(tt)) for i in starts)
    taken, mentions = set(), 0
    for a, b in sorted(spans, key=lambda s: (s[0] - s[1], s[0])):   # longest first
        if not taken.intersection(range(a, b)):
            taken.update(range(a, b))
            mentions += 1
    title = p.title or ""
    return {
        "words": metrics.get("word_count"),
        "unique_terms": sum(found.values()),
        "mentions": mentions,
        "variations": sum(1 for v in dict.fromkeys(variations) if _starts(key_words(v), toks, idx)),
        "exact": {"title": phrase_count(primary, title),
                  "h1": sum(phrase_count(primary, h) for h in p.h1),
                  "h2": sum(1 for h in p.h2 if phrase_count(primary, h)),
                  "alt": sum(1 for a in p.alts if phrase_count(primary, a)),
                  "description": phrase_count(primary, p.description or "")},
        "first_100": phrase_count(primary, " ".join(words(" ".join(p.opening()))[:FIRST_WORDS])) > 0,
        "title_front": front_loaded(primary, title),
    }


def primary_of(board):
    return ((board.get("brief") or {}).get("primary_keyword") or "").strip()


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
    primary = primary_of(board)
    title, desc = PB.meta_pick(board)
    h2s = [s["heading"] for s in board["sections"] if s.get("shape") != "hero"]
    alts = [a["alt"] for a in board.get("assets") or [] if (a.get("alt") or "").strip()]
    return {"who": "ours (board)", "words": None, "unique_terms": None, "mentions": None,
            "variations": None,
            "exact": {"title": phrase_count(primary, title),
                      "h1": phrase_count(primary, PB.picked_h1(board)),
                      "h2": sum(1 for h in h2s if phrase_count(primary, h)),
                      "alt": sum(1 for a in alts if phrase_count(primary, a)) if alts else None,
                      "description": phrase_count(primary, desc)},
            "first_100": None, "title_front": front_loaded(primary, title),
            "note": "not built — the board's picked title, description, H1, section H2s and "
                    "block-7 image alts"}


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
                           primary_of(board), terms, variations)
        return dict({"who": "ours (built)"}, **row, note=_rel(page))
    return board_row(board)


# ── competitors ─────────────────────────────────────────────────────────────────────────────
def _rank(item):
    _, p = item
    return (p.get("google_pos") or 99, p.get("bing_pos") or 99, p.get("url", ""))


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
            metrics = QA.page_metrics(html)      # one parse: the Words column and the listing test
            row = measure_html(html, primary, terms, variations, metrics)
            rows.append(_mark(dict({"who": p["url"]}, **row, note="measured from data/queries/cache"),
                              QA.listing_reason(metrics)))
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
                    "tag columns from the saved metrics"}, QA.listing_reason(m)))
    return rows


# ── checks (registered in family_rules) ────────────────────────────────────────────────────
def findings(board, dist=None, rebuilt=None):
    """[(check, severity, message)] for the placement rules. Scope is the caller's:
    family_rules runs this on new location, comparison and blog pages only."""
    import pageboard as PB
    primary = primary_of(board)
    if not primary:
        return [("primary-keyword", "FAIL", "board has no primary keyword")]
    out = []
    sev = "FAIL" if board["meta"]["status"] in _BOARDED_OR_LATER else "WARN"
    title, _ = PB.meta_pick(board)
    why = front_load_problem(primary, title)
    if why:
        out.append(("title-front-load", sev,
                    f"the picked title {title!r} is not front-loaded with the primary keyword "
                    f"{primary!r}: {why} (Rule 21 step 1; plurals and synonyms normalised, up "
                    f"to {TITLE_SLACK} connector words allowed)"))
    slug = board["meta"]["slug"]
    rebuilt = PB.rebuilt_slugs() if rebuilt is None else rebuilt
    page = PB.built_page(slug, dist)
    if _bare(slug) in rebuilt and page.exists():
        m = measure_html(page.read_text(encoding="utf-8", errors="ignore"), primary, [], [],
                         metrics={})           # only first_100 is read: skip the word count
        if not m["first_100"]:
            out.append(("first-100-words", "FAIL",
                        f"the built page does not carry {primary!r} in the first {FIRST_WORDS} "
                        f"words of its opening copy, after the H1 in <main> ({_rel(page)})"))
    return out


# ── the table ───────────────────────────────────────────────────────────────────────────────
def table(board, root=ROOT, dist=None, rebuilt=None):
    terms, variations = board_terms(board)
    primary = primary_of(board)
    return {"slug": board["meta"]["slug"], "primary_keyword": primary, "terms": len(terms),
            "rows": [ours_row(board, dist, rebuilt)]
            + competitor_rows(board["meta"]["slug"], primary, terms, variations, root)}


# Title, H1 and Description count occurrences of the primary keyword; H2 and Alt count the
# elements (H2 headings, image alts) that carry it. CAPTION says so under the table.
COLUMNS = ["Page", "Words", "Unique terms", "Mentions", "Variations", "Title", "H1", "H2",
           "Alt", "Description", "First 100", "Title front", "Note"]


CAPTION = ("Title / H1 / Description count occurrences of the primary keyword; H2 / Alt count "
           "the elements (H2 headings, image alts) that carry it. Words is page_metrics' word "
           "count; Mentions keeps the longest match where terms overlap; First 100 reads the "
           "opening copy after the H1. A dash is not measured.")


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
    print(json.dumps(t, indent=2, ensure_ascii=False) if a.json else markdown(t) + "\n\n" + CAPTION)
    for f in t["findings"]:
        print(f"  {f['sev']:4s} {f['check']:18s} {f['msg']}")
    print(f"keyword-metrics {a.slug}: {len(t['rows'])} rows, {t['terms']} terms examined → {out}")
    return 1 if any(f["sev"] == "FAIL" for f in t["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
