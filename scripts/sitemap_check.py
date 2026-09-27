#!/usr/bin/env python3
"""Gate: the generated sitemap shards and their index, against the built site.

A sitemap is the one artefact whose errors Google reports back weeks later, so the shape
is checked here rather than in Search Console:

  index integrity — sitemap_index.xml parses and every shard it lists exists under dist/;
                    conversely every `*-sitemap.xml` in dist/ is listed, because an
                    unlisted shard is a file nobody will ever fetch.
  shard integrity — every shard parses as XML, every `<loc>` starts with the site base,
                    and no URL is listed twice within one shard.
  listed => built — each `<loc>` must resolve to a built page (or a served asset) that is
                    not `noindex`. A noindex page in a sitemap is a direct contradiction:
                    it asks Google to crawl what the page then tells it to drop, which is
                    how the thank-you page and the redirect stubs would leak in.
  built => listed — each indexable built page must appear in exactly one URL shard. Zero
                    means the page is invisible; two means duplicate submission and an
                    ambiguous canonical signal. `video-sitemap.xml` is supplementary — it
                    annotates pages already listed elsewhere, so it is excluded from that
                    exclusivity count.
  embed => video  — a built page that CARRIES a YouTube embed must appear in the video
                    shard. This is the counterpart of the rule above, and it exists because
                    nothing had it: `generate_sitemaps.py` matched `youtube.com/embed/`
                    while the kit's `VideoEmbed` serves `youtube-nocookie.com/embed/`, so
                    four already-ranking ids left the video sitemap and every gate stayed
                    green (e963c53). The generator's regex is now the one this gate reads,
                    so a host the builder cannot see is a host this cannot see either — but
                    a page whose embed the builder DROPS for any other reason now fails
                    here, which is the half that was missing. Working rule 14 keeps an id
                    that already ranks; a url nobody submits is that id lost by another
                    route.
  robots          — robots.txt must point at exactly `<base>/sitemap_index.xml`; a stale
                    Sitemap line sends crawlers to the previous host.

Usage: python3 scripts/sitemap_check.py   (after `npm run build && npm run sitemaps`)
"""
import os
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

from generate_sitemaps import EMBED_SRC, _meta

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = (os.environ.get("SITE_URL") or "https://SITE_URL_PLACEHOLDER").rstrip("/")

# A shard that only annotates URLs listed elsewhere, so it does not count toward
# "exactly one shard".
SUPPLEMENTARY = ("video-sitemap.xml",)

ASSET_EXTS = {".xml", ".txt", ".webp", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".mp4",
              ".css", ".js", ".json", ".pdf", ".kml"}


def _tag(el):
    """Local name of an element, with any XML namespace stripped."""
    return el.tag.rsplit("}", 1)[-1]


def _locs(path):
    """Every `<loc>` text in a sitemap file, in document order, or None if unparseable."""
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8", errors="ignore"))
    except ET.ParseError:
        return None
    return [(el.text or "").strip() for el in root.iter() if _tag(el) == "loc"]


def built_pages(dist):
    """{url path: html} for every built page under dist/."""
    out = {}
    for f in sorted(dist.rglob("index.html")):
        rel = f.parent.relative_to(dist).as_posix()
        url = "/" if rel == "." else "/%s/" % rel
        out[url] = f.read_text(encoding="utf-8", errors="ignore")
    return out


def _is_asset(url_path):
    return pathlib.PurePosixPath(url_path).suffix.lower() in ASSET_EXTS


def _robots_problem(dist, base):
    robots = dist / "robots.txt"
    want = "%s/sitemap_index.xml" % base
    if not robots.is_file():
        return "FAIL robots.txt missing from dist"
    lines = [l.split(":", 1)[1].strip() for l in robots.read_text(encoding="utf-8").splitlines()
             if re.match(r"(?i)^\s*Sitemap\s*:", l)]
    if not lines:
        return "FAIL robots.txt has no Sitemap line (want %s)" % want
    if lines != [want]:
        return "FAIL robots.txt Sitemap line is %s, want %s" % (", ".join(lines), want)
    return None


def audit(dist, base):
    """Problems with the sitemaps under `dist`, as a list of strings (empty when clean)."""
    dist, base = pathlib.Path(dist), base.rstrip("/")
    problems = []
    pages = built_pages(dist)

    index = dist / "sitemap_index.xml"
    listed_locs = _locs(index) if index.is_file() else None
    if listed_locs is None:
        problems.append("FAIL sitemap_index.xml missing or unparseable")
        listed_locs = []

    listed = []
    for loc in listed_locs:
        name = loc.rsplit("/", 1)[-1]
        if not loc.startswith(base + "/"):
            problems.append("FAIL index entry %s is outside %s" % (loc, base))
        if not (dist / name).is_file():
            problems.append("FAIL %s listed in index but missing from dist" % name)
        else:
            listed.append(name)
    for f in sorted(dist.glob("*-sitemap.xml")):
        if f.name not in listed:
            problems.append("FAIL %s is in dist but not listed in the index" % f.name)

    shard_paths = {}                     # url path -> shards counting toward exclusivity
    shards_read = 0
    urls_seen = 0
    for name in sorted(set(listed) | {f.name for f in dist.glob("*-sitemap.xml")}):
        shard = dist / name
        if not shard.is_file():
            continue
        locs = _locs(shard)
        if locs is None:
            problems.append("FAIL %s is unparseable XML" % name)
            continue
        shards_read += 1
        urls_seen += len(locs)
        seen = set()
        for loc in locs:
            if not loc.startswith(base + "/") and loc != base + "/":
                problems.append("FAIL %s lists %s, outside %s" % (name, loc, base))
                continue
            url_path = loc[len(base):] or "/"
            if url_path in seen:
                problems.append("FAIL %s is listed twice in %s" % (url_path, name))
                continue
            seen.add(url_path)
            if url_path in pages:
                if "noindex" in _meta(pages[url_path], "robots"):
                    problems.append("FAIL %s is noindex but listed in %s" % (url_path, name))
            elif not (_is_asset(url_path) and (dist / url_path.lstrip("/")).is_file()):
                problems.append("FAIL %s not built but listed in %s" % (url_path, name))
            if name not in SUPPLEMENTARY:
                shard_paths.setdefault(url_path, []).append(name)

    # embed => video. Read from the page's own markup with the generator's own pattern, so
    # the two can never disagree about what counts as an embed. `video_locs` is the shard as
    # written; a page carrying an id and absent from it is the defect.
    video_shard = dist / "video-sitemap.xml"
    video_locs = {(loc[len(base):] or "/")
                  for loc in ((_locs(video_shard) or []) if video_shard.is_file() else [])}
    for url_path, text in sorted(pages.items()):
        if "noindex" in _meta(text, "robots"):
            continue
        ids = sorted(set(EMBED_SRC.findall(text)))
        if ids and url_path not in video_locs:
            problems.append("FAIL %s carries embed(s) %s and is in no video shard"
                            % (url_path, ", ".join(ids)))

    indexable = [u for u, text in pages.items() if "noindex" not in _meta(text, "robots")]
    for url_path in indexable:
        where = shard_paths.get(url_path, [])
        if not where:
            problems.append("FAIL %s is built and indexable but in no shard" % url_path)
        elif len(where) > 1:
            problems.append("FAIL %s in %d shards: %s"
                            % (url_path, len(where), ", ".join(where)))

    robots = _robots_problem(dist, base)
    if robots:
        problems.append(robots)

    return problems


HEADER = [
    "# Sitemaps", "",
    "Every indexable built page appears in exactly one URL shard; `video-sitemap.xml` is",
    "supplementary and excluded from that count. Every `<loc>` must be a built page (or a",
    "served asset) that is not `noindex`, must start with the site base, and must not",
    "repeat within its shard. The index must list every shard in dist/ and nothing else,",
    "and robots.txt must point at exactly `<base>/sitemap_index.xml`. A built page that",
    "carries a YouTube embed must also appear in `video-sitemap.xml`.", "",
]


def main(root=ROOT, dist=None, base=BASE):
    root = pathlib.Path(root)
    dist = pathlib.Path(dist) if dist else root / "dist"
    base = base.rstrip("/")

    if not (dist / "index.html").is_file() or not (dist / "sitemap_index.xml").is_file():
        print("FAIL dist or sitemap_index.xml missing: examined 0 built pages — not a pass "
              "(run npm run build && npm run sitemaps)")
        sys.exit(1)

    pages = built_pages(dist)
    indexable = [u for u, t in pages.items() if "noindex" not in _meta(t, "robots")]
    shards = sorted(f.name for f in dist.glob("*-sitemap.xml"))
    urls = sum(len(_locs(dist / s) or []) for s in shards)
    problems = audit(dist, base)

    summary = ("examined %d built pages, %d shards, %d sitemap urls; %d problems"
               % (len(pages), len(shards), urls, len(problems)))

    lines = list(HEADER)
    lines += ["## Problems", ""]
    lines += ["- %s" % p for p in problems] if problems else ["None.", ""]
    lines += ["", "## Shards", "", "| shard | urls |", "| --- | --- |"]
    lines += ["| %s | %d |" % (s, len(_locs(dist / s) or [])) for s in shards]
    lines += ["", "%d of %d built pages are indexable; each must appear in exactly one "
              "URL shard." % (len(indexable), len(pages)), "", summary, ""]

    out = root / "docs" / "reports" / "sitemaps.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(summary)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    if "SITE_URL_PLACEHOLDER" in BASE:
        print("WARNING: SITE_URL not set — auditing against %s" % BASE)
    main()
