#!/usr/bin/env python3
"""Outline provenance gate — a new-family page is built from its approved outline, and from
nothing else (system-gaps build, 2026-09-24).

The user's ruling: "Build from outline; never from crossovers, siblings, or duplicates."
`rules/copy.md` `write-from-outline-never-from-sibling` states the method and stays a
judgment rule — nobody can see HOW a page was written. This gate checks what the method
leaves behind on a built page, for location, comparison and blog pages only
(`scripts/family_rules.py`; the twelve pages built before this build are never examined):

  outline-unapproved        the page is in data/facts/rebuilt.json but its board record is
                            not approved (meta.status approved, built or released)
  outline-no-board          a named slug has no board record
  outline-no-main           the built page has no <main> holding <section data-section-label>
                            blocks (one problem, in place of a missing-heading line each)
  outline-not-found         a named slug, or one data/facts/rebuilt.json lists while dist/ is
                            built, has no built page where its route resolves
  outline-extra             a body H2/H3 the approved outline does not carry
  outline-missing           an outline H2/H3 the built page does not carry
  outline-order             the shared headings are in a different order from the outline
  outline-unknown-section   a <section data-section-label> in <main> whose id is not a
                            section of the board record
  outline-duplicate-heading the same heading twice on the page (H1 and body H2-H6)
  outline-heading-crossover a body heading equal to a heading on another built page —
                            exactly, with the breed words swapped (dup_content_audit's
                            template), or with a city name swapped (data/locations.json)
  outline-copy-crossover    a body passage of 12+ words shared with another built page
                            (dup_content_audit.crossovers, its whitelist)
  outline-sentence-crossover a body sentence of 6+ words equal to a sentence on another built
                            page, the city name swapped or not, outside the whitelist and
                            outside every passage already reported as a copy crossover

Each shared passage or sentence is ONE line, naming every page it is also on.

BODY means the page's top-level `<section data-section-label>` blocks inside <main> whose id
names a board section of a body shape. The frame is never body: a section whose board shape
is in FRAME_SHAPES (hero, takeaways, stats, reviews, FAQ, form, trust strip, puppy grid,
divider and the chrome shapes), a section whose id is in query_coverage_check.FRAME_IDS
(#top, #key-takeaways, #newsletter), and anything inside a frame component
(query_coverage_check.FRAME_CLASSES), a <form>, a <details> or a <nav>. The outline compared
is each body section's H2 and the level-3 nodes of its tree, in record order. H4-H6 are the
ladder written at P5 and are not in an approved tree, so they are compared for duplicates and
crossovers only.

WHICH PAGES. With no slug, every board record `family_rules.applies()` accepts whose page is
built AND listed in data/facts/rebuilt.json (bare key or full route, the convention
query_coverage_check.py uses). A new-family page whose migrated original is still in dist/ is
awaiting rebuild and is not examined. Named slugs are examined whenever they are built, listed
or not — the builder runs this on its own page before adding it to rebuilt.json. A named slug
out of family scope is reported and skipped, never failed.

Routes: a board key is the bare slug; a city page is built at dist/uk-locations/<slug>/.
scripts/page_sections.resolve_page resolves that from data/page-map.json (and defers to
`_slugs.resolve_page` once p5-readiness Task 43, F2a, adds it).

  python3 scripts/outline_provenance_check.py [slug ...] [--root DIR]

Exit 1 on any problem, 0 otherwise. Prints every page it examined.
"""
import argparse
import html as _h
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dup_content_audit as DUP  # noqa: E402  (whitelists, crossovers, specimen routes)
import family_rules as FR  # noqa: E402
from _slugs import page_key  # noqa: E402
from query_coverage_check import FRAME_CLASSES, FRAME_IDS  # noqa: E402
import page_sections as PS  # noqa: E402  (the route resolver image_candidates shares)

ROOT = Path(__file__).resolve().parents[1]
APPROVED = ("approved", "built", "released")
# Board shapes that render the fixed frame (docs/reference/location-page-template.md, "The
# fixed frame") or site chrome, never prose written from the outline.
FRAME_SHAPES = frozenset({"hero", "takeaways", "stats", "trust", "reviews", "faq", "form",
                          "puppies", "divider", "dial", "sheet", "strip", "nav"})
SKIP_TAGS = {"script", "style", "template", "noscript", "form", "details", "nav"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "source", "track", "wbr"}
HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")
BLOCK = {"p", "li", "dt", "dd", "td", "th", "div", "section", "article", "aside", "figure",
         "figcaption", "blockquote", "summary", "ul", "ol", "table", "tr", "main",
         "header", "footer", "br"} | set(HEADINGS)
SENTENCE_MIN_WORDS = 6
TOKEN = re.compile(r"[a-z0-9$']+")   # dup_content_audit's tokeniser
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


# ── routes ────────────────────────────────────────────────────────────────────────────────
resolve_page = PS.resolve_page


def built_path(slug, root):
    _, route = resolve_page(slug, root)
    base = Path(root) / "dist"
    return base / route / "index.html" if route else base / "index.html"


# ── normalisation ─────────────────────────────────────────────────────────────────────────
def norm(text):
    """Lowercase token string: curly apostrophes folded, entities and case ignored, so a
    heading the build title-cases still matches the record it came from."""
    return " ".join(TOKEN.findall(_h.unescape(text).replace("’", "'").lower()))


def city_pattern(root):
    """One regex over every city in data/locations.json (as tokens), longest first. "UK" is
    left out: it is the country, and swapping it would template half the site's headings.
    The words of a name match across a space OR a hyphen: prose is tokenised (hyphens become
    spaces) but a heading keeps them ("Delivery to Newcastle-under-Lyme"). Whole words only."""
    f = Path(root) / "data" / "locations.json"
    if not f.is_file():
        return None
    names = set()
    for row in json.loads(f.read_text(encoding="utf-8")):
        name = norm(re.sub(r"\(.*?\)", "", row.get("city") or ""))
        if name and name != "uk":
            names.add(name)
    if not names:
        return None
    alts = "|".join(r"[\s-]+".join(re.escape(w) for w in n.split())
                    for n in sorted(names, key=len, reverse=True))
    return re.compile(rf"\b(?:{alts})\b")


def templated(text, cities):
    return cities.sub("{city}", text) if cities is not None else text


# ── the board side ────────────────────────────────────────────────────────────────────────
def outline(board):
    """[(section id, level, normalised heading, heading)] for the body sections, in record
    order: each section's H2, then the level-3 nodes of its tree, depth-first."""
    out = []

    def walk(sid, nodes):
        for n in nodes or []:
            if n.get("level") == 3:
                out.append((sid, 3, norm(n["heading"]), n["heading"]))
            walk(sid, n.get("children"))
    for s in board.get("sections", []):
        if s.get("shape") in FRAME_SHAPES or s.get("id") in FRAME_IDS:
            continue
        out.append((s["id"], 2, norm(s["heading"]), s["heading"]))
        walk(s["id"], s.get("tree"))
    return out


def board_section_ids(board):
    return {s.get("id"): s.get("shape") for s in board.get("sections", [])}


# ── the built page ────────────────────────────────────────────────────────────────────────
class BuiltPage(HTMLParser):
    """Top-level labelled sections inside <main>, with their headings and prose; the H1; and
    any H2/H3 in <main> outside every labelled section (`stray`)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []        # {"tag", "sec", "skip"}
        self.sections = []     # {"id", "frame", "headings": [(level, text)], "text": [str]}
        self.h1 = []
        self.stray = []
        self._heading = None   # [level, [parts], section index or None]

    def _sec(self):
        for e in reversed(self.stack):
            if e["sec"] is not None:
                return e["sec"]
        return None

    def _skipping(self):
        return any(e["skip"] for e in self.stack)

    def _in_main(self):
        return any(e["tag"] == "main" for e in self.stack)

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            if tag == "br":
                self._text("\n")
            return
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        entry = {"tag": tag, "sec": None, "skip": tag in SKIP_TAGS or bool(classes & FRAME_CLASSES)}
        if (tag == "section" and "data-section-label" in a and self._in_main()
                and self._sec() is None):
            self.sections.append({"id": a.get("id") or "",
                                  "frame": (a.get("id") in FRAME_IDS) or bool(classes & FRAME_CLASSES),
                                  "headings": [], "text": []})
            entry["sec"] = len(self.sections) - 1
            entry["skip"] = False   # a frame section is dropped whole, below
        if tag in BLOCK:
            self._text("\n")
        self.stack.append(entry)
        if tag in HEADINGS and (tag == "h1" or not self._skipping()):
            self._heading = [int(tag[1]), [], self._sec()]   # the H1 sits in the hero frame

    def handle_endtag(self, tag):
        if tag in HEADINGS and self._heading is not None:
            level, parts, sec = self._heading
            text = " ".join("".join(parts).split())
            self._heading = None
            if level == 1:
                self.h1.append(text)
            elif sec is not None:
                self.sections[sec]["headings"].append((level, text))
            elif self._in_main() and level in (2, 3):
                self.stray.append((level, text))
        if tag in BLOCK:
            self._text("\n")
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break

    def _text(self, data):
        sec = self._sec()
        if sec is not None and not self._skipping():
            self.sections[sec]["text"].append(data)

    def handle_data(self, data):
        if self._heading is not None and (self._heading[0] == 1 or not self._skipping()):
            self._heading[1].append(data)
        elif not self._skipping():
            self._text(data)


def parse(html):
    p = BuiltPage()
    p.feed(html)
    p.close()
    return p


def sentences(text):
    """{normalised sentence} of SENTENCE_MIN_WORDS+ words, split on block boundaries and
    sentence ends."""
    out = set()
    for line in text.split("\n"):
        for piece in SENTENCE_END.split(line):
            toks = TOKEN.findall(piece.lower())
            if len(toks) >= SENTENCE_MIN_WORDS:
                out.add(" ".join(toks))
    return out


class _BlockText(DUP.Text):
    """dup_content_audit's visible-text walker, with a line break at every block edge so a
    heading and the paragraph under it are two sentences, not one."""

    def handle_starttag(self, t, attrs):
        if t in BLOCK:
            self.parts.append("\n")
        super().handle_starttag(t, attrs)

    def handle_endtag(self, t):
        if t in BLOCK:
            self.parts.append("\n")
        super().handle_endtag(t)


HEADING_RE = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.S | re.I)
TAG_RE = re.compile(r"<[^>]+>")


def corpus_page(path):
    """What another built page contributes: its dup shingles, its sentences and its headings
    (normalised)."""
    html = Path(path).read_text(encoding="utf-8", errors="ignore")
    ws = DUP.words(Path(path))
    t = _BlockText()
    t.feed(html)
    heads = {DUP._norm_heading(_h.unescape(TAG_RE.sub("", raw))).replace("’", "'")
             for _, raw in HEADING_RE.findall(html)}
    return {"shingles": DUP.shingles(ws),
            "sentences": sentences("".join(t.parts).lower()), "headings": heads - {""}}


def corpus(dist):
    """{page key: corpus_page} for every built page except the specimen routes. Read once per
    run; each examined page is compared with every entry but its own."""
    dist = Path(dist)
    out = {}
    for p in sorted(dist.rglob("index.html")):
        k = page_key(p, dist)
        if not DUP.is_specimen(k):
            out[k] = corpus_page(p)
    return out


# ── the checks ────────────────────────────────────────────────────────────────────────────
def _whitelisted_heading(text):
    return text in DUP.HEADER_WHITELIST or text in DUP.PUPPY_CARD_HEADINGS


def _whitelisted_sentence(s):
    """A head term; a sentence that is a stretch of one whitelisted stem (the delivery band
    split before its prices); or one with no stretch of SENTENCE_MIN_WORDS+ words that the
    whitelist leaves uncovered."""
    if s in DUP.HEAD_TERMS:
        return True
    if any(f" {s} " in f" {' '.join(stem)} " for stem in DUP.WHITELIST_STEMS):
        return True
    return all(len(seg) < SENTENCE_MIN_WORDS for seg in DUP.unwhitelisted_segments(s.split()))


def check_page(board, html, others, cities=None):
    """Every problem on one built page: [(check id, message)]. `others` is corpus()."""
    problems = []
    page = parse(html)
    if not page.sections:
        return [("outline-no-main", "no <main> with <section data-section-label> blocks found")]
    shapes = board_section_ids(board)
    body = []
    for s in page.sections:
        if s["frame"]:
            continue
        if s["id"] not in shapes:
            problems.append(("outline-unknown-section",
                             f"section #{s['id'] or '(no id)'} is not a section of the board record"))
            continue
        if shapes[s["id"]] in FRAME_SHAPES or s["id"] in FRAME_IDS:
            continue
        body.append(s)

    # (b) the outline, heading for heading
    want = [(lvl, key) for _, lvl, key, _ in outline(board)]
    shown = {(lvl, key): text for _, lvl, key, text in outline(board)}
    got, got_text = [], {}
    for s in body:
        for lvl, text in s["headings"]:
            if lvl in (2, 3):
                got.append((lvl, norm(text)))
                got_text[(lvl, norm(text))] = text
    for lvl, text in page.stray:
        problems.append(("outline-extra", f"H{lvl} \"{text}\" sits in <main> outside every "
                                          "board section"))
    for k in got:
        if k not in want:
            problems.append(("outline-extra", f"H{k[0]} \"{got_text[k]}\" is not in the approved outline"))
    for k in want:
        if k not in got:
            problems.append(("outline-missing", f"H{k[0]} \"{shown[k]}\" from the approved outline "
                                                "is not on the page"))
    common_got = [k for k in got if k in want]
    common_want = [k for k in want if k in got]
    if common_got != common_want:
        # The first position where the two lists part; when the shared part agrees, the one
        # just past it (a repeated heading makes one list longer).
        first = next((i for i, (x, y) in enumerate(zip(common_got, common_want)) if x != y),
                     min(len(common_got), len(common_want)))
        at = common_got[first] if first < len(common_got) else common_want[first]
        msg = f"headings are out of outline order from H{at[0]} \"{got_text.get(at) or shown.get(at)}\""
        if first < len(common_got) and first < len(common_want):
            exp = common_want[first]
            msg += f" (the outline has H{exp[0]} \"{shown.get(exp)}\" there)"
        problems.append(("outline-order", msg))

    # (d) duplicate headings within the page
    seen = {}
    for text in page.h1 + [t for s in body for _, t in s["headings"]]:
        seen.setdefault(norm(text), []).append(text)
    for key, texts in seen.items():
        if key and len(texts) > 1:
            problems.append(("outline-duplicate-heading",
                             f"\"{texts[0]}\" is a heading {len(texts)} times on this page"))

    # (c)/(d) headings shared with another built page
    other_exact, other_templ = {}, {}
    for k, o in others.items():
        for t in o["headings"]:
            if _whitelisted_heading(t):
                continue
            other_exact.setdefault(t, k)
            other_templ.setdefault(templated(DUP.SPECIES_TOKENS.sub("{breed}", t), cities), k)
    for s in body:
        for lvl, text in s["headings"]:
            t = DUP._norm_heading(_h.unescape(text)).replace("’", "'")
            if not t or _whitelisted_heading(t):
                continue
            if t in other_exact:
                problems.append(("outline-heading-crossover",
                                 f"H{lvl} \"{text}\" is also a heading on /{other_exact[t]}/"))
                continue
            tt = templated(DUP.SPECIES_TOKENS.sub("{breed}", t), cities)
            if tt in other_templ:
                problems.append(("outline-heading-crossover",
                                 f"H{lvl} \"{text}\" is a template of a heading on "
                                 f"/{other_templ[tt]}/ (\"{tt}\")"))

    # (c) body prose shared with another built page
    prose = "".join(p for s in body for p in s["text"]).lower()
    ws = TOKEN.findall(prose)
    sh = DUP.shingles(ws)
    mine = sorted(s for s in sentences(prose) if not _whitelisted_sentence(s))
    runs = {}                                  # passage -> [pages], first-seen order
    for k, o in others.items():
        for seg in DUP.crossovers(ws, sh, o["shingles"]):
            runs.setdefault(" ".join(seg), []).append(k)
    for run, keys in runs.items():
        problems.append(("outline-copy-crossover",
                         f"{len(run.split())} words shared with {_pages(keys)}: \"{run[:160]}\""))
    exact, swapped = {}, {}                    # sentence -> [pages]
    # Each sentence's city template, kept only when a city was actually swapped out.
    swaps = {x: t for x in mine if (t := templated(x, cities)) != x}
    for k, o in others.items():
        theirs = {templated(x, cities) for x in o["sentences"]} if swaps else set()
        for sent in mine:
            if sent in o["sentences"]:
                exact.setdefault(sent, []).append(k)
            elif sent in swaps and swaps[sent] in theirs:
                swapped.setdefault(sent, []).append(k)
    for sent in mine:
        if sent not in exact and sent not in swapped:
            continue
        if any(f" {sent} " in f" {run} " for run in runs):
            continue                           # already reported inside its passage
        parts = []
        if sent in exact:
            parts.append(f"also on {_pages(exact[sent])}")
        if sent in swapped:
            parts.append(f"a city swap of one on {_pages(swapped[sent])}")
        problems.append(("outline-sentence-crossover",
                         f"sentence {'; '.join(parts)}: \"{sent[:160]}\""))
    return problems


def _pages(keys, show=2):
    """"/a/, /b/ (+3 more)": the pages a shared passage or sentence is also on."""
    head = ", ".join(f"/{k}/" for k in keys[:show])
    return head + (f" (+{len(keys) - show} more)" if len(keys) > show else "")


# ── the run ───────────────────────────────────────────────────────────────────────────────
def boards(root):
    for f in sorted((Path(root) / "data" / "boards").glob("*.json")):
        if f.name.startswith("_"):
            continue
        yield json.loads(f.read_text(encoding="utf-8"))


def rebuilt(root):
    f = Path(root) / "data" / "facts" / "rebuilt.json"
    return set(json.loads(f.read_text(encoding="utf-8"))) if f.is_file() else set()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("slugs", nargs="*", help="board keys to examine (default: every "
                    "new-family page listed in data/facts/rebuilt.json)")
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    root = Path(a.root)
    listed = rebuilt(root)
    # A slug may be named as its board key or as its route (uk-locations/<slug>).
    named = set(a.slugs) | {resolve_page(s, root)[0] for s in a.slugs}
    by_key = {}
    for b in boards(root):
        by_key[b["meta"]["slug"]] = b
    problems, examined = [], []
    out_of_scope = not_built = awaiting = 0
    for slug in sorted(a.slugs):
        if not {slug, resolve_page(slug, root)[0]} & set(by_key):
            problems.append(f"{slug}: [outline-no-board] no board record for this slug in data/boards/")
    cities = city_pattern(root)
    built = None   # the corpus, read on the first page examined; never read when none is
    for slug, board in sorted(by_key.items()):
        if named and slug not in named:
            continue
        if not FR.applies(board):
            out_of_scope += 1
            if slug in named:
                print(f"{slug}: not a new-family page (family_rules.applies) — skipped")
            continue
        key, route = resolve_page(slug, root)
        page = built_path(slug, root)
        if not page.is_file():
            # A page the builder names, or one rebuilt.json lists while the site IS built,
            # must resolve: a silent skip here is how a route the resolver cannot find
            # (a post under /blog/, say) would never be examined at all.
            if slug in named or ({key, route, slug} & listed
                                 and (root / "dist" / "index.html").is_file()):
                problems.append(f"{slug}: [outline-not-found] no built page at "
                                f"{page.relative_to(root).as_posix()}")
            else:
                not_built += 1
            continue
        if not named and not ({key, route, slug} & listed):
            awaiting += 1
            continue
        examined.append(f"/{route}/")
        if board["meta"].get("status") not in APPROVED:
            problems.append(f"{slug}: [outline-unapproved] board status is "
                            f"'{board['meta'].get('status')}', not approved — no approved "
                            "outline to have built from")
        if built is None:
            built = corpus(root / "dist")
        own = page_key(page, root / "dist")
        others = {k: v for k, v in built.items() if k != own}
        for cid, msg in check_page(board, page.read_text(encoding="utf-8"), others, cities):
            problems.append(f"{slug}: [{cid}] {msg}")
    for p in problems:
        print(p)
    print(f"examined {len(examined)} new-family pages{': ' + ', '.join(examined) if examined else ''} "
          f"({out_of_scope} boards out of family scope, {not_built} not built, "
          f"{awaiting} awaiting rebuild); {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
