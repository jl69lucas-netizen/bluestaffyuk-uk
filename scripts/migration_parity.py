#!/usr/bin/env python3
"""Gate: migration parity between the old WordPress export and the built site.

Three numbers per page, so a drop can be attributed rather than argued about:

  raw      — the old `.entry-content` exactly as WordPress shipped it, including the
             dead enquiry form and the four sold pups' cards.
  expected — what the extractor *promised*: the same page put through the extractor's
             own cleaning (extract_wp.parse_page + extract_writers.strip_old_pups), so
             every deliberate removal is already subtracted.
  built    — what the built page actually renders inside `article.prose-migrated`.

The gate compares built against expected, not against raw: raw is reported only so a
reviewer can see the size of the deliberate removals. The 2% band exists for lxml
re-serialisation whitespace, not for content loss — a real drop must be fixed in the
extractor or the page template, never absorbed by widening the allowance.

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


def visible_stats(html_text, scope=None):
    """Visible-content stats for one HTML fragment or document.

    Site chrome and dead forms are dropped before counting, so the same function can be
    pointed at the raw export, the extractor's cleaned body, or a built page. `scope` is a
    CSS selector; when it matches nothing the whole document is measured.
    """
    soup = BeautifulSoup(html_text or "", "lxml")
    for tag in soup.find_all(DROP_TAGS):
        tag.decompose()
    node = (soup.select_one(scope) if scope else None) or soup
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

    `allowance` is a word budget for content the comparison side legitimately lacks;
    `image_allowance` the same for images. Words get a further 2% band for whitespace
    re-serialisation. Headings must match exactly, and embeds must never decrease.
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
    url, kind = row["url"], row["kind"]
    if kind == "location":
        slug = url.strip("/").split("/")[-1]
        return dist / "uk-locations" / slug / "index.html"
    rel = url.strip("/")
    return (dist / rel / "index.html") if rel else (dist / "index.html")


def source_path(row, src):
    """The old export file backing a page-map row."""
    rel = row["url"].strip("/")
    return (src / rel / "index.html") if rel else (src / "index.html")


def expected_stats(path, url):
    """Stats for the body the extractor promised: parse_page + strip_old_pups."""
    from extract_wp import parse_page
    from extract_writers import strip_old_pups
    page = parse_page(path, url)
    body, _removed, _notes = strip_old_pups(page.body_html)
    return visible_stats(body)


def fmt_headings(exp, built):
    return "%d→%d" % (len(exp["headings"]), len(built["headings"]))


def main():
    page_map = json.loads((ROOT / "data" / "page-map.json").read_text(encoding="utf-8"))
    src = pathlib.Path(page_map["generated_from"])
    dist = ROOT / "dist"
    rows, failing = [], 0

    for row in page_map["pages"]:
        url = row["url"]
        old_file = source_path(row, src)
        built_file = dist_path(row, dist)
        notes = []
        if not built_file.is_file():
            rows.append((url, "—", "—", "—", "—", "FAIL not built"))
            failing += 1
            continue
        built_html = built_file.read_text(encoding="utf-8", errors="ignore")
        if not old_file.is_file():
            rows.append((url, "—", "—", "—", "—", "FAIL no source"))
            failing += 1
            continue
        raw = visible_stats(old_file.read_text(encoding="utf-8", errors="ignore"),
                            ".entry-content")
        exp = expected_stats(old_file, url)

        if row["kind"] == "blog":
            # The archive page's body is rendered markdown, so the heading list and word
            # count come from the produced post, not from `.entry-content` (which the old
            # export left empty). Floor-check the rendered body instead.
            built = visible_stats(built_html, ARCHIVE_SCOPE)
            ok = built["words"] >= ARCHIVE_MIN_WORDS
            notes.append("archive")
            rows.append((url,
                         "%d→%d→%d" % (raw["words"], exp["words"], built["words"]),
                         fmt_headings(exp, built),
                         "%d→%d" % (exp["images"], built["images"]),
                         "%d→%d" % (exp["embeds"], built["embeds"]),
                         ("PASS" if ok else "FAIL words<%d" % ARCHIVE_MIN_WORDS)
                         + " (archive)"))
            failing += 0 if ok else 1
            continue

        built = visible_stats(built_html, RICH_SCOPE)
        result = compare(exp, built)
        if not result["pass"]:
            failing += 1
            detail = ", ".join("%s %s→%s" % (k, v[0], v[1])
                               for k, v in sorted(result["failures"].items()))
            verdict = "FAIL " + detail
        else:
            verdict = "PASS"
        if notes:
            verdict += " (%s)" % ", ".join(notes)
        rows.append((url,
                     "%d→%d→%d" % (raw["words"], exp["words"], built["words"]),
                     fmt_headings(exp, built),
                     "%d→%d" % (exp["images"], built["images"]),
                     "%d→%d" % (exp["embeds"], built["embeds"]),
                     verdict))

    lines = ["# Migration parity", "",
             "Built pages measured against what the extractor promised. `raw` is the old",
             "`.entry-content` before the extractor's deliberate removals (dead WordPress",
             "forms, the four sold pups' cards); `expected` is the same page after them;",
             "`built` is what `article.prose-migrated` renders. The gate compares",
             "expected → built with a 2% whitespace band; headings must match exactly and",
             "embeds must never decrease.", "",
             "| URL | words raw→expected→built | headings exp→built | images exp→built | embeds exp→built | result |",
             "| --- | --- | --- | --- | --- | --- |"]
    lines += ["| %s | %s | %s | %s | %s | %s |" % r for r in rows]
    lines += ["", "examined %d pages, %d failing" % (len(rows), failing), ""]
    report = "\n".join(lines)

    out = ROOT / "docs" / "reports" / "parity.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print("examined %d pages, %d failing" % (len(rows), failing))
    if failing:
        sys.exit(1)


if __name__ == "__main__":
    main()
