#!/usr/bin/env python3
"""Gate: migration parity between the old WordPress export and the built site.

Three numbers per page, so a drop can be attributed rather than argued about:

  raw      — the old `.entry-content` as WordPress shipped it, including the dead enquiry
             form and the four sold pups' cards.
  expected — what the extractor *promised*: the same page put through the extractor's own
             cleaning (extract_wp.parse_page + extract_writers.strip_old_pups), so every
             deliberate removal is already subtracted.
  built    — what the built page actually renders inside `article.prose-migrated`.

The gate compares built against expected, not against raw: raw is reported so a reviewer
can see the size of the deliberate removals, and is floor-checked so the extractor cannot
quietly delete most of a page. The 2% band exists for lxml re-serialisation whitespace,
not for content loss — a real drop must be fixed in the extractor or the page template,
never absorbed by widening the allowance.

Usage: python3 scripts/migration_parity.py
"""
import json
import pathlib
import re
import sys

from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

DROP_TAGS = ("script", "style", "noscript", "header", "footer", "nav", "form")
HEADING_RE = re.compile("^h[1-6]$")

RICH_SCOPE = "article.prose-migrated"
ARCHIVE_SCOPE = "article"
ARCHIVE_MIN_WORDS = 100
# Floor on expected/raw: below this the extractor has taken most of the page, which is a
# bug to investigate rather than a removal to accept.
MIN_KEPT_RATIO = 0.60
# Pages too short for that ratio to mean anything (stubs, empty placeholder locations).
RATIO_MIN_RAW_WORDS = 100


def visible_stats(html_text, scope=None, require_scope=False):
    """Visible-content stats for one HTML fragment or document.

    Site chrome and dead forms are dropped before counting, so the same function can be
    pointed at the raw export, the extractor's cleaned body, or a built page. `scope` is a
    CSS selector; when it matches nothing the whole document is measured, unless
    `require_scope` is set, in which case None is returned. Built pages always require
    their scope — silently measuring a whole built document (nav, hero, PuppyList and all)
    would let a missing article wrapper pass the gate.
    """
    soup = BeautifulSoup(html_text or "", "lxml")
    for tag in soup.find_all(DROP_TAGS):
        tag.decompose()
    found = soup.select_one(scope) if scope else None
    if found is None and require_scope:
        return None
    node = found or soup
    text = node.get_text(" ", strip=True)
    return {
        "words": len(text.split()),
        "headings": ["%s:%s" % (t.name, t.get_text(" ", strip=True))
                     for t in node.find_all(HEADING_RE)],
        "images": len(node.find_all("img")),
        "embeds": len(node.find_all(["iframe", "video"])),
    }


def compare(old, new, allowance=0, image_allowance=0):
    """Gate one page's built stats against its expected stats.

    `allowance` is a word budget for content the comparison side legitimately lacks and
    `image_allowance` the same for images; main() passes neither, because `expected` has
    already had every deliberate removal subtracted from it, so built must match it
    outright. Words get a further 2% band for whitespace re-serialisation. Headings must
    match exactly, and embeds must never decrease.
    """
    failures = {}
    if new["words"] < (old["words"] - allowance) * 0.98:
        failures["words"] = (old["words"], new["words"])
    if list(old["headings"]) != list(new["headings"]):
        failures["headings"] = (len(old["headings"]), len(new["headings"]))
    if new["images"] < old["images"] - image_allowance:
        failures["images"] = (old["images"], new["images"])
    if new["embeds"] < old["embeds"]:
        failures["embeds"] = (old["embeds"], new["embeds"])
    return {"pass": not failures, "failures": failures}


def dist_path(row, dist):
    """Where the built page for a page-map row lives under dist/."""
    url = row["url"]
    if row.get("kind") == "location":
        slug = url.strip("/").split("/")[-1]
        return dist / "uk-locations" / slug / "index.html"
    rel = url.strip("/")
    return (dist / rel / "index.html") if rel else (dist / "index.html")


def source_path(row, src):
    """The old export file backing a page-map row."""
    rel = row["url"].strip("/")
    return (src / rel / "index.html") if rel else (src / "index.html")


def expected_stats(path, url):
    """Stats for the body the extractor promised, plus what it removed.

    Returns (stats, cards_removed, notes) where notes are strip_old_pups' own remarks
    (e.g. "puppy-grid-emptied").
    """
    from extract_wp import parse_page
    from extract_writers import strip_old_pups
    page = parse_page(path, url)
    body, removed, notes = strip_old_pups(page.body_html)
    return visible_stats(body), removed, notes


def _fail_row(url, verdict):
    return (url, "—", "—", "—", "—", "—", verdict)


def _page_row(row, old_file, built_file):
    """One report row for one page-map entry. Returns (row_tuple, ok)."""
    url = row["url"]
    archive = row.get("kind") == "blog"

    if not old_file.is_file():
        return _fail_row(url, "FAIL no source"), False
    if not built_file.is_file():
        return _fail_row(url, "FAIL not built"), False

    raw = visible_stats(old_file.read_text(encoding="utf-8", errors="ignore"),
                        ".entry-content")
    try:
        exp, cards, notes = expected_stats(old_file, url)
    except Exception as exc:                      # a broken page must fail, not crash
        return _fail_row(url, "FAIL extractor error: %s" % exc), False

    scope = ARCHIVE_SCOPE if archive else RICH_SCOPE
    built = visible_stats(built_file.read_text(encoding="utf-8", errors="ignore"),
                          scope, require_scope=True)
    if built is None:
        return _fail_row(url, "FAIL no %s" % scope), False

    problems, tags = [], list(notes)
    if archive:
        # The archive page's body is rendered markdown, so the heading list and word count
        # come from the produced post, not from `.entry-content` (which the old export
        # left empty). Floor-check the rendered body instead.
        tags.append("archive")
        if built["words"] < ARCHIVE_MIN_WORDS:
            problems.append("words<%d" % ARCHIVE_MIN_WORDS)
    else:
        result = compare(exp, built)
        problems += ["%s %s→%s" % (k, v[0], v[1])
                     for k, v in sorted(result["failures"].items())]
        # Raw→expected floor: the deliberate removals must not swallow the page. Stubs and
        # near-empty placeholders are exempt; so is the archive, whose raw is 0 by design.
        if (raw["words"] >= RATIO_MIN_RAW_WORDS and "stub" not in row.get("defects", [])
                and exp["words"] < raw["words"] * MIN_KEPT_RATIO):
            problems.append("over-removal %d→%d" % (raw["words"], exp["words"]))

    verdict = ("FAIL " + ", ".join(problems)) if problems else "PASS"
    if tags:
        verdict += " (%s)" % ", ".join(tags)
    return (url,
            "%d→%d→%d" % (raw["words"], exp["words"], built["words"]),
            "%d→%d" % (len(exp["headings"]), len(built["headings"])),
            "%d→%d" % (exp["images"], built["images"]),
            "%d→%d" % (exp["embeds"], built["embeds"]),
            str(cards),
            verdict), not problems


HEADER = [
    "# Migration parity", "",
    "Built pages measured against what the extractor promised. `raw` is the old",
    "`.entry-content` before the extractor's deliberate removals (dead WordPress forms,",
    "the four sold pups' cards); `expected` is the same page after them; `built` is what",
    "`article.prose-migrated` renders. Note that `raw` is itself measured after site",
    "chrome and dead forms are stripped, so it slightly understates the WordPress body.",
    "The gate compares expected → built with a 2% whitespace band; headings must match",
    "exactly, embeds must never decrease, a built page missing its article scope fails,",
    "and expected must keep at least 60% of raw's words. Pages listed in",
    "`data/facts/rebuilt.json` are no longer migrated bodies and are skipped here:",
    "`scripts/facts_preserved_check.py` is their gate.", "",
    "| URL | words raw→expected→built | headings exp→built | images exp→built | embeds exp→built | cards removed | result |",
    "| --- | --- | --- | --- | --- | --- | --- |",
]


def slug_of(row):
    """A page-map row's slug: the url with its slashes off, and `index` for the site root.
    The same key scripts/facts_preserved_check.py names its fact sets by."""
    return row["url"].strip("/").split("/")[-1] or "index"


def rebuilt_slugs(root=ROOT):
    """Slugs project 4 has REWRITTEN. Their bodies are no longer the migrated body, so this
    gate has nothing true to say about them and scripts/facts_preserved_check.py takes over.
    Empty until the first page task lands, and the handover is one-way: a slug added here
    must already have a committed data/facts/<slug>.json, or it is a page with no content
    gate at all."""
    path = pathlib.Path(root) / "data" / "facts" / "rebuilt.json"
    return set(json.loads(path.read_text(encoding="utf-8"))) if path.exists() else set()


def main(root=ROOT, src=None, dist=None):
    root = pathlib.Path(root)
    page_map = json.loads((root / "data" / "page-map.json").read_text(encoding="utf-8"))
    src = pathlib.Path(src) if src else pathlib.Path(page_map["generated_from"])
    dist = pathlib.Path(dist) if dist else root / "dist"
    rebuilt = rebuilt_slugs(root)

    rows, failing, skipped = [], 0, 0
    for row in page_map["pages"]:
        if slug_of(row) in rebuilt:
            skipped += 1
            continue
        tup, ok = _page_row(row, source_path(row, src), dist_path(row, dist))
        rows.append(tup)
        failing += 0 if ok else 1

    # `skipped` is printed even when it is zero: a page that quietly left this gate and never
    # arrived at the other one is the one failure mode the handover can have.
    summary = "examined %d pages, %d failing, skipped %d rebuilt" % (len(rows), failing, skipped)
    report = "\n".join(HEADER + ["| %s | %s | %s | %s | %s | %s | %s |" % r for r in rows]
                       + ["", summary, ""])
    out = root / "docs" / "reports" / "parity.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(summary)
    if failing:
        sys.exit(1)


if __name__ == "__main__":
    main()
