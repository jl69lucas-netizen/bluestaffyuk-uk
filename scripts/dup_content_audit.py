#!/usr/bin/env python3
"""Cross-page duplicate-copy auditor.

Finds word-for-word copy shared between built pages in dist/ — the "same
template, same paragraphs" failure the breeder keeps catching (delivery
sections, available-now intros, repeated anchor texts). Compares visible
body text only (scripts/styles/JSON-LD stripped) using word shingles.

Usage:
  python3 scripts/dup_content_audit.py                 # audit all dist pages
  python3 scripts/dup_content_audit.py slugA slugB ... # audit only these slugs
  python3 scripts/dup_content_audit.py --dist build    # audit a different built tree
  python3 scripts/dup_content_audit.py --min-words 15  # change shingle length
  python3 scripts/dup_content_audit.py --json          # also write the JSON report
  python3 scripts/dup_content_audit.py --headers       # heading-crossover mode:
      flags any H1-H6 whose exact text (or template with breed names swapped)
      appears on 2+ pages — catches the crossover-header failure that the
      12-word shingle check is blind to (most headings are < 12 words).

Exit codes, same convention as the other audit scripts (evidence_audit.py,
aeo_audit.py): 1 when any duplicate passage or heading was found, 0 otherwise.
Every finding this gate makes is an ERROR — there is no WARN level here — so
--fail-on-error is accepted and changes nothing; it exists so a caller can pass
the same flags to every audit without special-casing this one.

--json [PATH] writes the machine-readable result (default
docs/reports/dup_content_audit.json) so callers never scrape stdout:
  {"mode": "body"|"headers", "dist", "pages", "min_words", "problems",
   "findings": [{"a","b","words","run"} | {"kind","text","pages"}]}

Boilerplate that legitimately
repeats (nav, footer, the canonical delivery band, the £500 deposit line,
the puppy-grid card data, site-standard section headers) is whitelisted below,
and every whitelist entry was measured on dist/ rather than guessed.
"""
import argparse, html as _h, itertools, json, re, sys
from pathlib import Path
from html.parser import HTMLParser
from _slugs import page_key

MIN_WORDS = 12
WHITELIST_SNIPPETS = [
    # ── 2026-09-17, measured on the BSUK dist/ build (49 pages) ─────────────
    # Every entry below was MEASURED, not guessed, by scripts/measure_chrome.py — run it
    # to reproduce or re-measure after a redesign. It merges shingles shared by 3+ built
    # pages into maximal runs, reduces each to its invariant core (the sub-run carried by
    # the most pages), and prints the carrying pages; each core was then classified as
    # chrome (a component rendered across page types) or as page prose. Whitelist the CORE,
    # never the longest run on one page — the longer stem exempts nothing on the pages that
    # carry the shorter variant. Only chrome is listed here.
    #
    # This comment deliberately quotes a phrase — "the delivery band, the deposit line" —
    # as a live fixture: tests/render/lib/dupCorpus.ts parses this list with a regex, and
    # an unanchored one read quoted prose out of these comments and silently widened the
    # whitelist. tests/py/test_dup_content_audit.py mirrors the anchored parse and asserts
    # it returns exactly WHITELIST_SNIPPETS, so removing the anchor turns that test red.
    # Location-page prose that repeats across the nine templated city pages — the
    # passionate-about-breeding about-block, the L-2-HGA / HC-HSF4 health-testing
    # block — is deliberately ABSENT: that is the migrated-content baseline and it
    # belongs in the gate report, not in the exemption list.

    # CTA band + enquiry-form intro — one component, rendered on nine page types. The stem
    # is the INVARIANT CORE (10 pages), not the longest run on one page: the heading above
    # it varies, and a stem starting `reserve your blue staffy puppy` left the 13-word
    # remainder reported nine times.
    "fill in your details below and we'll be in touch within 24 hours",
    "complete our short enquiry form choose your puppy and we'll be in touch within 24 hours start your enquiry",
    "reserve your puppy today kc aware ethical breeders full health tested",

    # delivery band — the canonical delivery terms, mandated identical wherever they render
    "delivery note delivery begins 24 48 hours after payment confirmation train station pickup is our default method free",
    # invariant core (9 pages): the trailing `in glasgow` is present on six of them only,
    # and including it left the 15-word remainder reported eight times
    "uk home delivery by defra approved transport priced by distance 200 to 350 or collect",
    "train station handover free we meet you at your nearest mainline station",
    "ground transport 100 defra approved delivery to your front door",
    "halfway meet up 100 we meet you at a convenient midpoint location",

    # deposit line — the one deposit figure the site is allowed to state
    "deposit 500 refundable",

    # trust strip under the hero
    "family raised puppies lifetime support available blue staffy puppies delivery options",

    # newsletter block
    "get blue staffy updates new litters breeder tips puppy availability straight to your inbox",

    # puppy-grid card data — name, sex, colour, price read straight off the litter
    # record; sync with data/puppies.json when the litter changes
    "roman male blue and white 1 500 byrd male white 1 500 ince male blue 1 500 vennie female blue and white 1 700 christa female blue 1 700 cheryl female blue with white blaze 1 700",

    # document-title + skip-link chrome that leaks into the text stream
    "blue staffy puppy for sale blue staffy uk skip to content",

    # ── review quotes (spec §5 "Reviews", added 2026-09-19, project 4 Task 6) ──────
    # The three rows of data/reviews.json, tokenised. They are the only real buyer quotes
    # the site has, every page's board picks which of them fill its review slots, and
    # CLAUDE.md mandates they be reused VERBATIM — so the same sentences render on several
    # pages by design, and the gate reporting them trains everyone to ignore it. Sitewide
    # lines, not page prose.
    #
    # Written out as literals, not read from data/reviews.json at import, because
    # tests/render/lib/dupCorpus.ts parses this list with a regex over the source and a
    # computed entry would be invisible to the harness — the two gates would then disagree
    # about the same passage. tests/py/test_dup_whitelist_measured.py holds them in step
    # with the data file and measures them against the built pages.
    "we couldn t be happier with our beautiful blue staffy from bluestaffyuk uk from the first enquiry to bringing her home the process was seamless and incredibly professional she s got the most wonderful temperament playful loving and fantastic with our kids it s clear she was raised with so much care and early socialisation she truly is the heart of our family",
    "after extensive research we chose bluestaffyuk uk and we re so glad we did our blue staffy puppy arrived happy and healthy with all his papers and medical records meticulously organized their commitment to ethical breeding and health testing truly shines through he s exactly what we wanted loyal intelligent and incredibly affectionate we highly recommend them if you re looking to buy a staffordshire bull terrier in the uk",
    "the health checks the communication and the home raised environment everything was top notch i wouldn t go anywhere else for a staffy",
]

# Routes that render a SPECIMEN of another page's content rather than a page of their own.
# `/board-preview/<slug>/` renders a board record's own sections three styles over, and
# `/kit-preview/` renders every kit component against demo data — including the FAQ
# accordion, which loads every row in data/faq.json. Both are noindex scaffolding and
# neither competes for anything, so a passage shared with one is not duplicate content: it
# is one passage rendered twice, once as the page and once as the specimen of it.
#
# Defined HERE rather than in pageboard.py because pageboard imports this module for its
# chrome-skipping walker, and the dependency must not run both ways. pageboard's
# `live_headings()` reads the same list.
SPECIMEN_PREFIXES = ("board-preview/", "kit-preview/")


def is_specimen(key):
    """True for a specimen route's page key, at any depth. The prefix is anchored, so a real
    slug that merely CONTAINS "kit-preview" further down its path is not caught."""
    return (key + "/").startswith(SPECIMEN_PREFIXES)


SKIP_TAGS = {"script", "style", "noscript", "header", "footer", "nav", "form"}
VOID_TAGS = {"br", "img", "hr", "input", "meta", "link", "source", "track", "wbr", "area", "base", "col", "embed"}
# chrome elements not wrapped in a semantic tag: jump rails, TOC card grids,
# section-directory blocks, breadcrumbs.
#
# 2026-07-26: added review/testimonial and read-card blocks. Both are syndicated
# components rather than page prose — the reviews are real buyer quotes that
# CLAUDE.md mandates be reused verbatim, and a read-card's title and sub are the
# link label for the page it points at, also whitelisted. Leaving them in meant
# the gate reported 23 crossovers on the for-sale cluster that were all
# legitimate, which trains everyone to ignore the gate. Body prose, including the
# cross-sell strip, is still compared in full.
CHROME_RE = re.compile(r"jump|toc|rail|msp-|crumb|review|testimonial|read-c|quote-c", re.I)

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.stack=[]
    def handle_starttag(self,t,attrs):
        if t in VOID_TAGS: return
        skipping = bool(self.stack and self.stack[-1][1])
        if not skipping:
            blob = " ".join(v for k,v in attrs if v and k in ("class","id","aria-label"))
            skipping = t in SKIP_TAGS or bool(CHROME_RE.search(blob))
        self.stack.append((t, skipping))
    def handle_endtag(self,t):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == t:
                del self.stack[i:]; break
    def handle_data(self,d):
        if not (self.stack and self.stack[-1][1]): self.parts.append(d)

def words(path: Path):
    p=Text(); p.feed(path.read_text(errors="ignore"))
    txt=" ".join(p.parts).lower()
    return re.findall(r"[a-z0-9$']+", txt)

def norm(ws): return " ".join(ws)

# Tokenised once, with the same tokeniser as the page text, so a stem matches whole words.
WHITELIST_STEMS = [re.findall(r"[a-z0-9$']+", w) for w in WHITELIST_SNIPPETS]

def unwhitelisted_segments(run):
    """The stretches of a shared run (a word list) that no whitelisted stem covers.

    The whitelist exempts LINES, not the runs they sit in. Growth fuses a whitelisted line
    with any shared passage touching it, and skipping a run that merely CONTAINED a stem
    exempted the passage along with it (found 2026-09-11: a 17-word <legend> right after the
    shipping line never fired). So every stem occurrence is cut out and each side is judged
    on its own. Re-joining the sides instead would glue two short shared phrases into one
    false 12-word passage. Mirrors unwhitelistedSegments() in tests/render/checks/dup.ts.
    """
    covered = [False] * len(run)
    for stem in WHITELIST_STEMS:
        n = len(stem)
        for k in range(len(run) - n + 1):
            if run[k:k+n] == stem:
                covered[k:k+n] = [True] * n
    segments, cur = [], []
    for w, c in zip(run, covered):
        if c:
            if cur: segments.append(cur); cur = []
        else:
            cur.append(w)
    if cur: segments.append(cur)
    return segments

def shingles(ws):
    sh = {}
    for i in range(len(ws)-MIN_WORDS+1):
        sh.setdefault(norm(ws[i:i+MIN_WORDS]), i)
    return sh

def crossovers(wa, sa, sb):
    """Every non-whitelisted passage >= MIN_WORDS that page A shares with page B, as word lists.

    Runs grow from the FIRST shared shingle, whitelisted or not. The old per-shingle
    whitelist skip made growth start mid-stem ("airport $350 home ..."), leaving a stem
    fragment glued to the passage that no whole-stem cut can remove.
    """
    reported = set()
    found = []
    for s in sorted(set(sa) & set(sb), key=lambda s: sa[s]):
        if any(s in r for r in reported): continue
        i = sa[s]; j = i + MIN_WORDS
        while j < len(wa) and norm(wa[j-MIN_WORDS+1:j+1]) in sb: j += 1
        run = wa[i:j]; reported.add(norm(run))
        found += [seg for seg in unwhitelisted_segments(run) if len(seg) >= MIN_WORDS]
    return found

# The site's head terms: phrases a page is trying to rank for, which therefore appear in
# many headings by design (`blue staffy puppies` is in 16 of the 49 live pages' headings).
# A shared run that is nothing but one of these is not a crossover. Read by the Page Board
# header pre-check as well as this gate — one data list, two gates.
# Precedent: sessions/2026-08-10-two-pages-outline-gate.md §C2.
HEAD_TERMS = [
    "blue staffy puppies for sale",
    "blue staffy puppies for sale uk",
    "staffy puppies for sale",
    "staffordshire bull terrier puppies for sale",
    "blue staffy puppies",
    "blue staffy",
]

# Headings allowed to repeat on every page (site-standard sections). Matched EXACTLY
# against the normalised heading text — see `_norm_heading` below. It used to be a
# substring test (`any(w in text ...)`), which meant the one-word entry "contact"
# whitelisted every heading containing the string "contact" and the gate quietly stopped
# reporting real collisions. Exact match, one entry per heading that really repeats.
HEADER_WHITELIST = frozenset((
    "frequently asked questions",
    "get in touch",
    "join our newsletter",
    # Footer.astro column headings (site chrome not wrapped in <footer>)
    "blue staffy uk",
    "quick pages",
    "cities we serve",
    # syndicated chrome blocks measured on dist/ 2026-09-17: the newsletter card
    # (3 pages) and the puppy-grid section heading (12 pages)
    "blue staffy news: join 500+ readers!",
    "\U0001f4ec get blue staffy updates",
    "available blue staffy puppies",
    "\U0001f43e reserve your blue staffy puppy",
    # Owner card (the breeder's name is the breeder's name)
    "lisa bright",
))

# Puppy-name card headings, kept SEPARATE from HEADER_WHITELIST — sync with
# data/puppies.json when the litter changes.
#
# A card heading is a whole heading, never a phrase inside one: a puppy's name legitimately
# repeats wherever its card renders, and nowhere else. Kept apart because scripts/pageboard.py
# matches HEADER_WHITELIST as a contiguous token SUB-RUN, and a one-word entry in that list
# exempts every board heading containing the word ("Roman Roads of Glasgow"). Both lists are
# matched exactly today; the split keeps that true if sub-run matching ever comes back for
# phrases.
PUPPY_CARD_HEADINGS = frozenset(("roman", "byrd", "ince", "vennie", "christa", "cheryl"))
# Breed/variant tokens normalised in --headers mode so that templated headers
# ("Is a Blue Staffy Right for You?" vs "Is a Staffordshire Bull Terrier Right for You?")
# are caught as template-for-template crossovers, not just exact matches.
SPECIES_TOKENS = re.compile(
    r"\b(blue staffy|staffy|staffordshire bull terrier|staffordshire bull terriers|staffies)\b")


def _norm_heading(text):
    """Heading text reduced to the form HEADER_WHITELIST is written in: lowercase, single
    spaces, no leading/trailing space. Exact comparison happens on this form."""
    return re.sub(r"\s+", " ", text).strip().lower()


def headers_mode(pages):
    """Flag exact + templated H1-H6 crossovers between pages. Returns the findings list."""
    hpat = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.S | re.I)
    strip = re.compile(r"<[^>]+>")
    exact, templ = {}, {}
    for slug, p in pages.items():
        html = p.read_text(errors="ignore")
        for lvl, raw in hpat.findall(html):
            text = _norm_heading(_h.unescape(strip.sub("", raw)))
            if not text or text in HEADER_WHITELIST or text in PUPPY_CARD_HEADINGS:
                continue
            exact.setdefault(text, set()).add(slug)
            templ.setdefault(SPECIES_TOKENS.sub("{breed}", text), set()).add(slug)
    findings = []
    for text, slugs in sorted(exact.items()):
        if len(slugs) > 1:
            findings.append({"kind": "exact", "text": text, "pages": sorted(slugs)})
            print(f"EXACT header crossover on {sorted(slugs)}:\n  \"{text}\"\n")
    for text, slugs in sorted(templ.items()):
        if len(slugs) > 1 and text not in exact:
            findings.append({"kind": "template", "text": text, "pages": sorted(slugs)})
            print(f"TEMPLATE header crossover on {sorted(slugs)}:\n  \"{text}\"\n")
    if findings:
        print(f"FAIL — {len(findings)} crossover headers across {len(pages)} pages.")
    else:
        print(f"PASS — no crossover headers in {len(pages)} pages.")
    return findings

DEFAULT_JSON = Path(__file__).resolve().parent.parent / "docs/reports/dup_content_audit.json"


def _write_json(path, payload):
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        shown = out.relative_to(Path.cwd())
    except ValueError:
        shown = out
    print(f"JSON report → {shown}")


def main(argv=None):
    global MIN_WORDS
    ap = argparse.ArgumentParser(
        prog="dup_content_audit.py",
        description="Audit a built site for cross-page duplicate body copy (and, with "
                    "--headers, duplicate headings).",
        epilog="Exits 1 when a duplicate is found. Whitelisted chrome is listed in "
               "WHITELIST_SNIPPETS / HEADER_WHITELIST at the top of this file; reproduce "
               "the measurement behind it with scripts/measure_chrome.py.")
    ap.add_argument("slugs", nargs="*",
                    help="page keys to audit (default: every page in the dist tree)")
    ap.add_argument("--dist", default="dist", help="built site directory (default dist)")
    ap.add_argument("--min-words", type=int, default=MIN_WORDS,
                    help=f"shingle length in words (default {MIN_WORDS})")
    ap.add_argument("--headers", action="store_true",
                    help="heading-crossover mode instead of the body-copy audit")
    ap.add_argument("--fail-on-error", action="store_true",
                    help="accepted for symmetry with the other audit scripts; every "
                         "finding here is already an ERROR, so this changes nothing")
    ap.add_argument("--json", nargs="?", const=str(DEFAULT_JSON), default=None,
                    metavar="PATH",
                    help=f"write the machine-readable result (default {DEFAULT_JSON})")
    ns = ap.parse_args(sys.argv[1:] if argv is None else argv)
    args = ns.slugs
    MIN_WORDS = ns.min_words
    dist = Path(ns.dist)
    pages = {k: v for k, v in ((page_key(p, dist), p) for p in dist.rglob("index.html"))
             if not is_specimen(k)}
    if args:
        pages = {k: v for k, v in pages.items() if k in args}
    base = {"mode": "headers" if ns.headers else "body", "dist": str(dist),
            "pages": len(pages), "min_words": MIN_WORDS}
    if ns.headers:
        findings = headers_mode(pages)
        if ns.json:
            _write_json(ns.json, {**base, "problems": len(findings), "findings": findings})
        return 1 if findings else 0

    shingled = {}
    for slug, p in pages.items():
        ws = words(p)
        shingled[slug] = (ws, shingles(ws))
    findings = []
    for (a, (wa, sa)), (b, (wb, sb)) in itertools.combinations(shingled.items(), 2):
        for seg in crossovers(wa, sa, sb):
            run = norm(seg)
            findings.append({"a": a, "b": b, "words": len(seg), "run": run})
            print(f"DUPLICATE ({len(seg)} words) between /{a}/ and /{b}/:\n"
                  f"  \"{run[:220]}{'…' if len(run) > 220 else ''}\"\n")
    if findings:
        print(f"FAIL — {len(findings)} duplicated passages ≥{MIN_WORDS} words.")
    else:
        print(f"PASS — no cross-page duplicate runs ≥{MIN_WORDS} words in {len(pages)} pages.")
    if ns.json:
        _write_json(ns.json, {**base, "problems": len(findings), "findings": findings})
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
