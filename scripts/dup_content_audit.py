#!/usr/bin/env python3
"""Cross-page duplicate-copy auditor.

Finds word-for-word copy shared between built pages in dist/ — the "same
template, same paragraphs" failure the breeder keeps catching (shipping
sections, available-now intros, repeated anchor texts). Compares visible
body text only (scripts/styles/JSON-LD stripped) using word shingles.

Usage:
  python3 scripts/dup_content_audit.py                 # audit all dist pages
  python3 scripts/dup_content_audit.py slugA slugB ... # audit only these slugs
  python3 scripts/dup_content_audit.py --min-words 15  # change shingle length
  python3 scripts/dup_content_audit.py --headers       # heading-crossover mode:
      flags any H1-H6 whose exact text (or template with species names swapped)
      appears on 2+ pages — catches the "29 crossover headers" failure that the
      12-word shingle check is blind to (most headings are < 12 words).

Exit 1 if any duplicate run >= MIN_WORDS (or duplicate heading in --headers
mode) is found between two different pages. Boilerplate that legitimately
repeats (nav, footer, the canonical shipping cost line, doc-badge lists,
site-standard section headers) is whitelisted below.
"""
import re, sys, itertools
from pathlib import Path
from html.parser import HTMLParser
from _slugs import page_key

MIN_WORDS = 12
WHITELIST_SNIPPETS = [
    "ships nationwide $185 airport $350 home",
    "pbfd pcr screening avian polyomavirus pcr dna sexing certificate avian vet health certificate hatch certificate closed band",
    "cites cert pcr dna sexed vet certified pbfd apv screened fully weaned",
    # canonical price-matrix data repeated in comparison-table Grey columns
    "typical price $1 700 $3 500 our greys",
    # mandated CTA-band trust bullets (deposit / guarantee / IATA — CLAUDE.md)
    "$200 deposit reserves your bird 3 day health guarantee iata compliant shipping nationwide",
    # canonical inquiry invitation line above the CTA band
    "hand raised cites documented and dna sexed reach out to start the conversation we reply within 24 hours",
    # credential badge strip (NAP + trust set — mandated identical)
    "since 2014 usda awa cites docs dna sexing pcr screened",

    # ── 2026-07-26, for-sale cluster ────────────────────────────────────────
    # Each entry below is one of the categories CLAUDE.md names as the ONLY text
    # allowed to match a sibling verbatim. Kept as short distinctive stems rather
    # than full runs, since substring matching covers every phrasing variant.

    # shipping line — the canonical cost line, mandated on every card and section
    "$185 airport $350 home",
    "midland tx within 2 3 hours",

    # counter strip
    "12 yrs aviary in midland tx 24h we answer personally",
    "verify our license app i cites documented 0 wild caught ever",

    # doc-badge lists — the certificate enumerations
    "dna pbfd apv pcr paperwork cites app i usda",
    "the dna certificate the vet health record the hatch record and the care guide",
    # anchored mid-phrase: the shingle window slides, so a stem that starts at the
    # first word of the list gets missed as soon as the reported run starts later
    "avian vet health record a care guide a welcome kit",
    "closed leg band an avian vet health record",

    # CTA button labels
    "book a video call first read the full scam guide",

    # ── 2026-09-12, near-me router ─────────────────────────────────────────
    # Two data-rendered furniture blocks the for-sale kit prints from
    # data/clutch-inventory.json on every page that ships Avail-B + the kit form:
    # the browse-by-kind filter rail with live counts (no quotes here: the harness
    # reader takes any quoted string in this block as a stem), and the form-side list of
    # every reservable bird with its price. Identical by construction, like the
    # counter strip; not prose.
    "browse by kind all birds 6 congo 3 timneh 2 companion pair 1",
    "bery congo $1 700 amie congo $2 500 roys congo $2 300 jins jeni congo $3 500 elad timneh $1 600 evie timneh $1 500",
]

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
# many headings by design (`african grey parrot for sale` is in 46 live pages' headings).
# A shared run that is nothing but one of these is not a crossover. Read by the Page Board
# header pre-check as well as this gate — one data list, two gates.
# Precedent: sessions/2026-08-10-two-pages-outline-gate.md §C2.
HEAD_TERMS = [
    "african grey parrot for sale",
    "african grey parrots for sale",
    "african grey for sale",
    "african grey parrot",
    "african grey parrots",
]

# Headings allowed to repeat on every page (site-standard sections).
HEADER_WHITELIST = [
    "frequently asked questions",
    "shipping & delivery",
    "reserve your bird",
    "get in touch",
    "join our newsletter",
    # Footer.astro 5-column headings (site chrome not wrapped in <footer>)
    "shop african greys",
    "by location",
    "resources & trust",
    "contact",
    # Owner card (the breeder's name is the breeder's name)
    "mark & teri benjamin",
    # Bird-name card headings — sync with data/clutch-inventory.json when
    # inventory changes; a bird's name legitimately repeats wherever its
    # card renders.
    "amie", "bery", "roys", "elad", "evie", "jins", "jeni",
]
# Species/variant tokens normalized in --headers mode so that templated
# headers ("Is a Macaw Right for You?" vs "Is a Cockatoo Right for You?")
# are caught as template-for-template crossovers, not just exact matches.
SPECIES_TOKENS = re.compile(
    r"\b(congo|timneh|macaw|cockatoo|amazon(?: parrot)?|eclectus|african grey|grey)\b")

def headers_mode(pages):
    """Flag exact + templated H1-H6 crossovers between pages."""
    hpat = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>", re.S | re.I)
    strip = re.compile(r"<[^>]+>")
    exact, templ = {}, {}
    for slug, p in pages.items():
        html = p.read_text(errors="ignore")
        for lvl, raw in hpat.findall(html):
            import html as _h
            text = _h.unescape(re.sub(r"\s+", " ", strip.sub("", raw)).strip().lower())
            if not text or any(w in text for w in HEADER_WHITELIST):
                continue
            exact.setdefault(text, set()).add(slug)
            templ.setdefault(SPECIES_TOKENS.sub("{species}", text), set()).add(slug)
    bad = 0
    for text, slugs in sorted(exact.items()):
        if len(slugs) > 1:
            bad += 1
            print(f"EXACT header crossover on {sorted(slugs)}:\n  \"{text}\"\n")
    for text, slugs in sorted(templ.items()):
        if len(slugs) > 1 and text not in exact:
            bad += 1
            print(f"TEMPLATE header crossover on {sorted(slugs)}:\n  \"{text}\"\n")
    if bad:
        print(f"FAIL — {bad} crossover headers across {len(pages)} pages."); sys.exit(1)
    print(f"PASS — no crossover headers in {len(pages)} pages.")

def main():
    args=[a for a in sys.argv[1:] if not a.startswith("--")]
    global MIN_WORDS
    if "--min-words" in sys.argv:
        MIN_WORDS=int(sys.argv[sys.argv.index("--min-words")+1])
    dist=Path("dist")
    pages={page_key(p, dist): p for p in dist.rglob("index.html")}
    if args: pages={k:v for k,v in pages.items() if k in args}
    if "--headers" in sys.argv:
        headers_mode(pages); return
    shingled={}
    for slug,p in pages.items():
        ws=words(p)
        shingled[slug]=(ws,shingles(ws))
    bad=0
    for (a,(wa,sa)),(b,(wb,sb)) in itertools.combinations(shingled.items(),2):
        for seg in crossovers(wa, sa, sb):
            bad+=1
            run=norm(seg)
            print(f"DUPLICATE ({len(seg)} words) between /{a}/ and /{b}/:\n  \"{run[:220]}{'…' if len(run)>220 else ''}\"\n")
    if bad:
        print(f"FAIL — {bad} duplicated passages ≥{MIN_WORDS} words."); sys.exit(1)
    print(f"PASS — no cross-page duplicate runs ≥{MIN_WORDS} words in {len(pages)} pages.")

if __name__=="__main__":
    main()
