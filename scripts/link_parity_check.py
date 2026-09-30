#!/usr/bin/env python3
"""link_parity_check.py — a rebuilt page links where its board record says, and nowhere else.

  python3 scripts/link_parity_check.py --check        # every slug in data/facts/rebuilt.json
  python3 scripts/link_parity_check.py <slug> [...]   # named slugs
  python3 scripts/link_parity_check.py --check --list # also print the reconciled set per page

WHY THIS EXISTS. `facts_preserved_check.py` asks whether the rebuilt page still carries the
facts the migrated page carried. It says nothing about what the page ADDED. Working rule 12
(spec §9 amendment 3a) is the other direction: every link on a rebuilt page is one the
breeder approved on the board, and every link they approved is on the page. Without a gate
the drift is silent and cheap — a component's hard-coded CTA, a second link to a source
already cited, a `mailto:` nobody signed off — and each one is a destination the board never
showed anyone.

WHAT COUNTS AS A LINK ON THE PAGE. Every `<a href>` inside `<main>`, minus:

  * CHROME. The in-page nav set (`kit-dial`, `kit-sheet`, `kit-tabbar`, `kit-strip`, the
    sections `<dialog>`) renders inside `<main>` and links only to the page's own sections
    and to three fixed site routes. It is furniture, it is identical on every page that
    mounts it, and no board record describes it. The header, the footer and the breadcrumb
    are outside `<main>` already and never reach this walker.
  * SAME-PAGE FRAGMENTS. `#section-id` is a jump, not a destination; `nav-anchors-resolve`
    is the gate that owns those.
  * THE PUPPY GRID'S OWN CARDS. A section of shape `puppies` IS the grid: its cards are rows
    of data/puppies.json rendered by `PuppyCard`, and each row links to that puppy's page.
    Those hrefs are DATA, not prose the breeder wrote an anchor for — a record that listed
    them would go stale the day a litter changed, which is the thing the shape exists to
    avoid. So `/available-puppies/<slug>/` is allowed on a page whose record has a
    `puppies`-shaped section, and ONLY for slugs that are actually in data/puppies.json.
    Every other href on such a page is judged normally.
  * THE BLOG HUB'S OWN POST CARDS. The same argument, one collection over: a record whose
    `meta.page_type` is `blog` is an index of src/content/blog, and its cards' hrefs are
    rows of that collection rendered at build rather than anchors anybody wrote on a board.
    The exemption is POSITIONAL, not page-wide — a `.post-card` subtree on such a page is
    cut from the corpus the way a dial is, so a link the CARD LIST generated is exempt and
    the same href written into a sentence three sections down is still reported as an extra.
    A page-wide allowance could not tell those two apart, and the second one is a
    destination somebody chose and nobody approved. What the cards carry is then checked
    rather than trusted: every href cut this way must be a slug a post file on disk
    actually claims, and anything else in a card is reported.

`mailto:` is NOT exempt. An email address is a channel the board can list and did not, so a
`mailto:` reports as an extra until a record names it — which is the honest outcome: the
address can still be written as text, and linking it is a decision somebody should take.

WHAT THE RECORD ALLOWS. The union of `sections[].links.internal[].href` and
`sections[].links.external[].href`, and nothing else. `dropped.links` is the opposite: an
href listed there is one the record says the page must NOT carry, so finding it is a
failure of its own kind rather than a plain extra — the reason it was dropped is in the
record beside it.

Exit: 0 clean, 1 any page out of parity, 2 cannot run (no dist/, no record).
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _slugs import built_page, resolve_page  # noqa: E402  (one route convention, shared)

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BOARDS = ROOT / "data" / "boards"
REBUILT = ROOT / "data" / "facts" / "rebuilt.json"

MAIN = re.compile(r"<main\b[^>]*>(.*?)</main>", re.S | re.I)
ANCHOR = re.compile(r"""<a\b[^>]*?\shref\s*=\s*["']([^"']*)["']""", re.I)

# The in-page nav set, by the class each component puts on its own root. Kept as a literal
# list rather than a regex over "nav|dial|sheet": a page section could legitimately carry a
# class with one of those words in it, and this gate silently dropping a real link would be
# worse than it reporting one.
CHROME_CLASSES = ("kit-dial", "kit-sheet", "kit-tabbar", "kit-strip")
# `<dialog class="sheet">` is SectionSheet's bottom sheet; it sits inside `.kit-sheet`
# (`display: contents`) but is cut here too so the walker does not depend on nesting.
CHROME_TAGS = ("dialog",)


#: The blog hub's generated post card. One class, on the card's own root, so the positional
#: exemption below has something to key on that the page cannot spread over a section.
CARD_CLASSES = ("post-card",)


def _cut(html, classes, tags=()):
    """(html without those subtrees, [each removed subtree]) — walked, not regexed.

    A regex cannot do this: the subtrees nest, and `.*?</div>` stops at the first close tag
    rather than the matching one — which would leave half a dial's links in the corpus and
    cut a real paragraph out of the middle of a section.

    The removed subtrees are RETURNED rather than dropped on the floor, because the post-card
    caller has to judge what was in them: a chrome subtree is furniture nobody has to account
    for, and a card list is data that must still be data.
    """
    out, taken = [], []
    pos = 0
    depth = 0        # nesting depth inside a cut subtree, 0 = not in one
    open_tag = None  # the tag name that opened the subtree we are in
    start = 0
    for m in re.finditer(r"<(/?)([a-zA-Z][\w-]*)([^>]*)>", html):
        close, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if depth == 0:
            out.append(html[pos:m.start()])
            pos = m.start()
            cls = " ".join(re.findall(r"""(?:class|id)\s*=\s*["']([^"']*)["']""", attrs))
            starts = (not close) and not attrs.rstrip().endswith("/") and (
                tag in tags or any(c in cls.split() for c in classes))
            if starts:
                depth, open_tag, start = 1, tag, m.start()
                pos = m.end()
        elif tag == open_tag:
            depth += -1 if close else 1
            if depth == 0:
                taken.append(html[start:m.end()])
                pos = m.end()
    out.append(html[pos:])
    return "".join(out), taken


def _strip_chrome(html):
    """`html` with every chrome subtree removed. The old name, kept: it is what the tests and
    the walker's own regression case call."""
    return _cut(html, CHROME_CLASSES, CHROME_TAGS)[0]


def _hrefs(html):
    """Every destination href in a fragment. Same-page jumps are not destinations."""
    return [h for h in (a.strip() for a in ANCHOR.findall(html))
            if h and not h.startswith("#")]


def page_links(html, cut_cards=False):
    """Every href a rebuilt page's own body offers, chrome and same-page jumps removed.

    `cut_cards` additionally removes the generated post-card subtrees, for a blog hub — see
    the positional exemption in the header. Off by default, so a page that is not an index of
    the collection is judged on every anchor it carries.
    """
    body = MAIN.search(html)
    inner = _strip_chrome(body.group(1) if body else html)
    if cut_cards:
        inner = _cut(inner, CARD_CLASSES)[0]
    return _hrefs(inner)


def card_links(html):
    """Every href inside a `.post-card` subtree of a page's body, chrome already removed."""
    body = MAIN.search(html)
    inner = _strip_chrome(body.group(1) if body else html)
    return [h for sub in _cut(inner, CARD_CLASSES)[1] for h in _hrefs(sub)]


# `<the fact> — <the reason>`, the same shape facts_preserved_check.py reads. Em or en dash
# only: a hyphen is part of a slug, and splitting on one cut `/uk-locations/...` in half.
_DROP_SPLIT = re.compile(r"\s+[—–]\s+")


def dropped_links(record):
    """The hrefs the record says the page must not carry, read off the front of each line."""
    out = set()
    for line in (record.get("dropped") or {}).get("links", []) or []:
        if not isinstance(line, str):
            continue
        head = _DROP_SPLIT.split(line.strip(), 1)[0].strip()
        # The entry usually reads `/path/ ("the old anchor")`; the href is the first token.
        out.add(head.split()[0] if head.split() else head)
    return out


def record_links(record):
    """Every href the record's sections list, internal and external."""
    out = set()
    for s in record["sections"]:
        for side in ("internal", "external"):
            for l in s["links"][side]:
                out.add(l["href"].strip())
    return out


def puppy_hrefs(record):
    """`/available-puppies/<slug>/` for every row of data/puppies.json — allowed only on a
    page whose record has a `puppies`-shaped section (see the note at the top)."""
    if not any(s["shape"] == "puppies" for s in record["sections"]):
        return set()
    rows = json.loads((ROOT / "data/puppies.json").read_text(encoding="utf-8"))
    return {f"/available-puppies/{p['slug']}/" for p in rows}


#: The `slug:` line of a blog post's frontmatter — the route the post actually builds at.
#: Deriving it from the FILENAME would invent a url nothing serves, the same trap
#: scripts/generate_page_dates.py::post_slug records.
_POST_SLUG = re.compile(r"^slug:\s*[\"']?([^\"'\n]+)", re.M)


def collection_hrefs():
    """`/<post slug>/` for every entry of the `blog` content collection, read off disk."""
    out = set()
    for f in sorted((ROOT / "src/content/blog").glob("*.md")):
        m = _POST_SLUG.search(f.read_text(encoding="utf-8"))
        if m:
            out.add(f"/{m.group(1).strip().strip('/')}/")
    return out


def is_blog_hub(record):
    """True for a record that IS an index of the `blog` collection, which is the only kind of
    page whose generated post cards are exempt (see the header)."""
    return (record.get("meta") or {}).get("page_type") == "blog"


def post_hrefs(record):
    """`/<post slug>/` for every collection entry — on a BLOG HUB record and nowhere else.

    THE PUPPY GRID'S ARGUMENT, ONE COLLECTION OVER. The hub's post cards are rows of
    src/content/blog rendered at build: their hrefs are DATA, not anchors the breeder wrote
    on a board, and a record that listed them would go stale the day a post was published —
    which is the thing a generated card list exists to avoid. So
    data/boards/blue-staffy-blog-guides.json's `latest-guides` section carries no `links`
    rows and says so in its own note, and this is the exemption that note points at.

    THIS IS THE RECORD HALF OF THE RULE AND NOT THE WHOLE OF IT. `check()` also cuts the
    `.post-card` subtrees out of the page corpus, so the exemption is positional: what a card
    generated is exempt, and the same href written into a sentence elsewhere on the page is
    reported like any other extra. What this function decides is what a CARD is allowed to
    contain — a slug a post file on disk actually claims, and nothing else.
    """
    return collection_hrefs() if is_blog_hub(record) else set()


def check(slug):
    """(problems, examined) for one rebuilt slug. `problems` are printable strings."""
    # A city page's bare slug is built at dist/uk-locations/<slug>/ and its record is
    # data/boards/<slug>.json (scripts/_slugs.py, Known Issue 39).
    page = built_page(slug, ROOT, DIST)
    rec_path = BOARDS / f"{resolve_page(slug, ROOT)[0]}.json"
    if not page.exists():
        return [f"{slug}: no built page at dist/{page.relative_to(DIST)} — run the build"], 0
    if not rec_path.exists():
        return [f"{slug}: no board record at {rec_path.relative_to(ROOT)}"], 0
    record = json.loads(rec_path.read_text(encoding="utf-8"))

    html = page.read_text(encoding="utf-8", errors="ignore")
    # A BLOG HUB's generated post cards come OUT of the corpus, the way the dial does, so the
    # exemption is positional rather than page-wide: a prose link to a post slug is still on
    # `on_page` and still has to be on the board. What the cards carried is judged on its own
    # terms below.
    hub = is_blog_hub(record)
    on_page = page_links(html, cut_cards=hub)
    in_cards = card_links(html) if hub else []
    allowed = record_links(record)
    data_ok = puppy_hrefs(record)
    banned = dropped_links(record)

    problems = []
    # A card may carry a row of the collection and nothing else. Without this the positional
    # exemption would be a hole: anything at all inside a `.post-card` would leave the corpus.
    collection = post_hrefs(record)
    for h in sorted(set(in_cards)):
        if h in banned:
            problems.append(f"{slug}: {h} is listed in the record's `dropped.links` and is in a post card")
        elif h not in collection:
            problems.append(f"{slug}: {h} is in a post card and is not a row of the `blog` "
                            "collection — a card's href is collection data, and anything else "
                            "in one is a link the board never showed anybody")
    for h in sorted(set(on_page)):
        if h in banned:
            problems.append(f"{slug}: {h} is listed in the record's `dropped.links` and is on the page")
        elif h not in allowed and h not in data_ok:
            problems.append(f"{slug}: {h} is on the page and in no section's `links`")
    for h in sorted(allowed - set(on_page)):
        problems.append(f"{slug}: {h} is in the record's `links` and not on the page")
    # The card hrefs count toward `examined`: they were judged, and a gate's examined count is
    # what it looked at (.claude/skills/bsuk-gate-integrity).
    return problems, len(set(on_page) | set(in_cards))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("slugs", nargs="*", help="check these slugs")
    ap.add_argument("--check", action="store_true", help="check every slug in data/facts/rebuilt.json")
    ap.add_argument("--list", action="store_true", help="print each page's reconciled href set")
    ns = ap.parse_args(sys.argv[1:] if argv is None else argv)

    slugs = ns.slugs or (json.loads(REBUILT.read_text(encoding="utf-8")) if ns.check and REBUILT.exists() else [])
    if not slugs:
        print("link-parity ERROR examined 0 rebuilt pages, not a pass — pass a slug or --check "
              "with a non-empty data/facts/rebuilt.json")
        return 2

    total, links = 0, 0
    for slug in slugs:
        problems, n = check(slug)
        links += n
        for p in problems:
            print(f"  {p}")
        total += len(problems)
        if ns.list:
            page = built_page(slug, ROOT, DIST)
            if page.exists():
                for h in sorted(set(page_links(page.read_text(encoding="utf-8", errors="ignore")))):
                    print(f"    {slug}  {h}")
    # A gate that examined nothing is not a pass (.claude/skills/bsuk-gate-integrity).
    print(f"examined {len(slugs)} rebuilt page(s), {links} distinct body link(s); {total} problems")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
