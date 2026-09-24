#!/usr/bin/env python3
"""build_search_index.py — public/search-index.json for the header's site search.

Spec §11 amendment 3b: the header carries a search pill backed by an index built HERE, at
build time, from this repo's own data. No third-party search service is contacted at build
time or at run time; the whole index is one static JSON file the page fetches once.

Run after `astro build` (it is in the `postbuild` chain, after the sitemaps):

    python3 scripts/build_search_index.py

WHAT GOES IN. One row per BUILT, INDEXABLE page — the same `noindex` rule the sitemaps use,
read off the built HTML, so the design canvas, the search page itself and the thank-you page
are excluded here for exactly the reason they are excluded there. Every row's TITLE is the
`<title>` the built page prints (entities decoded); `data/page-map.json`'s title is only the
fallback for a page that prints none. Kinds come from the page map for the pages it knows;
the pages it does not know (the puppy pages from `data/puppies.json`, the blog posts from
`src/content/blog/*.md`, and the three index routes) take a kind derived from the route, the
same `shard_for` the sitemap generator uses.

The UI groups results under Puppy, Guide, Location, Blog and Page. `Guide` is a group the
header script supports and this index does not currently emit: `data/page-map.json` has
three kinds — `location`, `blog` and `rich` — and inventing a `Guide` class by sniffing
slugs would put pages in a bucket no data file says they belong to. When the page map grows
a guide kind, add it to KIND_LABEL and the group appears on its own.

TITLES ARE COPIED, NOT WRITTEN. A search result whose title does not match the page it opens
is its own defect, so the index copies the title the page prints and never writes one. Until
2026-09-23 it copied the page map's MIGRATED titles, so the eleven pages project 4 rebuilt
were offered under their old WordPress titles — one of them naming the breeder's former city
(Known Issue 16). A row that still names that city does so because its page does; the count
is printed on every run.

Deterministic: rows are sorted by url, so the committed file only changes when the site does.
"""
import json
import pathlib
import re
import sys
from html import unescape

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from generate_sitemaps import _meta, _pages, blog_slugs_from_content, shard_for  # noqa: E402

DIST = ROOT / "dist"
OUT = ROOT / "public/search-index.json"

#: page-map `kind` → the label the header groups results under.
KIND_LABEL = {"location": "Location", "blog": "Blog", "rich": "Page", "page": "Page"}
#: sitemap shard → the same labels, for the routes the page map does not list.
SHARD_LABEL = {"location": "Location", "post": "Blog", "puppy": "Puppy", "page": "Page"}

TITLE_TAG = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
HEAD = re.compile(r"<head\b[^>]*>(.*?)</head>", re.S | re.I)
WORD = re.compile(r"[a-z0-9]+")


def _title(html):
    """The document's <title>, read inside <head> only (an inline SVG's <title> in the body is
    an icon's name), entities decoded BEFORE the whitespace collapses, so an &nbsp; run
    collapses like any other space."""
    head = HEAD.search(html)
    m = TITLE_TAG.search(head.group(1) if head else html)
    return " ".join(unescape(m.group(1)).split()) if m else ""


def keywords(title, url):
    """Title words plus slug words, lowercased, de-duplicated, first-seen order."""
    words = WORD.findall(title.lower()) + WORD.findall(url.lower())
    seen, out = set(), []
    for w in words:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return " ".join(out)


def build(dist=DIST, page_map=None, blog_slugs=None):
    page_map = page_map if page_map is not None else json.loads((ROOT / "data/page-map.json").read_text())["pages"]
    by_url = {p["url"]: p for p in page_map}
    blog_slugs = blog_slugs if blog_slugs is not None else blog_slugs_from_content()
    rows = []
    for url, text in _pages(dist):
        if "noindex" in (_meta(text, "robots") or ""):
            continue
        shard = shard_for(url, blog_slugs)
        if shard is None:
            continue
        row = by_url.get(url)
        title = _title(text) or (row or {}).get("title") or ""
        kind = KIND_LABEL.get((row or {}).get("kind"), SHARD_LABEL.get(shard, "Page"))
        if not title:
            continue
        rows.append({"url": url, "title": title, "kind": kind, "keywords": keywords(title, url)})
    rows.sort(key=lambda r: r["url"])
    return rows


def main(argv=None):
    if not DIST.exists():
        print("no dist/ — run `npm run build` first")
        return 1
    rows = build()
    body = json.dumps(rows, indent=1, ensure_ascii=False) + "\n"
    # BOTH copies. `public/` is the committed source of the file; `dist/` is what the built
    # site actually serves — and Astro copies `public/` into `dist/` BEFORE postbuild runs,
    # so writing only to `public/` ships an index that is one build out of date. Every page
    # added in a build would be missing from its own build's search results.
    for out in (OUT, DIST / OUT.name):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
    kinds = {}
    for r in rows:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    carried = sum(1 for r in rows if "Glasgow" in r["title"])
    print(f"search index: {len(rows)} rows -> {OUT.relative_to(ROOT)} and dist/{OUT.name}")
    print("  " + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())))
    if carried:
        print(f"  {carried} title(s) carry the former city because their built page prints it "
              "(Known Issue 16; not rewritten here)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
