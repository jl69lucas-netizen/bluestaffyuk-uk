#!/usr/bin/env python3
"""Sitemap shards + index from dist/. Every indexable page in exactly one shard; noindex excluded.

Run after `astro build`: python3 scripts/generate_sitemaps.py

lastmod is today's date for every URL in Foundation; real per-page lastmod derived
from git history comes in a later task.
"""
import datetime, html, os, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BASE = (os.environ.get("SITE_URL") or "https://SITE_URL_PLACEHOLDER").rstrip("/")
TODAY = datetime.date.today().isoformat()
SHARDS = ("page", "post", "location", "puppy", "video")


def blog_slugs_from_content():
    out = set()
    for f in (ROOT / "src/content/blog").glob("*.md"):
        m = re.search(r'^slug:\s*"?([^"\n]+)"?\s*$', f.read_text(encoding="utf-8"), re.M)
        if m:
            out.add(m.group(1).strip())
    return out


def shard_for(url_path, blog_slugs=frozenset()):
    if url_path.startswith("/thank-you"):
        return None
    if url_path.startswith("/uk-locations/") and url_path != "/uk-locations/":
        return "location"
    if url_path.startswith("/available-puppies/") and url_path != "/available-puppies/":
        return "puppy"
    if url_path.strip("/") in blog_slugs:
        return "post"
    return "page"


def _pages(dist):
    for f in sorted(dist.rglob("index.html")):
        rel = f.parent.relative_to(dist).as_posix()
        yield ("/" if rel == "." else "/%s/" % rel), f.read_text(encoding="utf-8", errors="ignore")


def _meta(text, name):
    m = re.search(r'<meta name="%s" content="([^"]*)"' % name, text)
    return html.unescape(m.group(1)) if m else ""


def build_shards(dist, base, blog_slugs):
    out = {s: [] for s in SHARDS}
    for url_path, text in _pages(dist):
        if "noindex" in _meta(text, "robots"):
            continue
        s = shard_for(url_path, blog_slugs)
        if s is None:
            continue
        out[s].append((base + url_path, TODAY))
        vids = list(dict.fromkeys(re.findall(r'youtube\.com/embed/([A-Za-z0-9_-]{6,})', text)))
        if vids:
            t = re.search(r"<title>(.*?)</title>", text, re.S)
            title = html.unescape(t.group(1)).strip() if t else url_path
            out["video"].append((base + url_path, [
                {"id": v, "title": title, "description": _meta(text, "description")} for v in vids
            ]))
    return out


def _url_sitemap(entries):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod in entries:
        lines += ["  <url>", "    <loc>%s</loc>" % html.escape(loc),
                  "    <lastmod>%s</lastmod>" % html.escape(lastmod), "  </url>"]
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def _video_sitemap(entries):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">']
    for loc, vids in entries:
        lines += ["  <url>", "    <loc>%s</loc>" % html.escape(loc)]
        for v in vids:
            lines += [
                "    <video:video>",
                "      <video:thumbnail_loc>https://i.ytimg.com/vi/%s/hqdefault.jpg</video:thumbnail_loc>" % html.escape(v["id"]),
                "      <video:title>%s</video:title>" % html.escape(v["title"]),
                "      <video:description>%s</video:description>" % html.escape(v["description"] or v["title"]),
                "      <video:player_loc>https://www.youtube.com/embed/%s</video:player_loc>" % html.escape(v["id"]),
                "    </video:video>",
            ]
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def _rewrite_robots(path, base):
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    line = "Sitemap: %s/sitemap_index.xml" % base
    if re.search(r"(?m)^Sitemap:.*$", text):
        text = re.sub(r"(?m)^Sitemap:.*$", line, text)
    else:
        text = text.rstrip("\n") + "\n\n" + line + "\n"
    path.write_text(text, encoding="utf-8")


def write(shards, dist=DIST, base=BASE):
    written = []
    for name in SHARDS:
        entries = shards[name]
        if not entries:
            continue
        body = _video_sitemap(entries) if name == "video" else _url_sitemap(entries)
        fn = "%s-sitemap.xml" % name
        (dist / fn).write_text(body, encoding="utf-8")
        written.append(fn)
    idx = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for fn in written:
        idx += ["  <sitemap>", "    <loc>%s/%s</loc>" % (html.escape(base), fn),
                "    <lastmod>%s</lastmod>" % TODAY, "  </sitemap>"]
    idx.append("</sitemapindex>")
    (dist / "sitemap_index.xml").write_text("\n".join(idx) + "\n", encoding="utf-8")
    _rewrite_robots(dist / "robots.txt", base)
    _rewrite_robots(ROOT / "public/robots.txt", base)
    return written


if __name__ == "__main__":
    slugs = blog_slugs_from_content()
    shards = build_shards(DIST, BASE, slugs)
    written = write(shards)
    for name in SHARDS:
        print("%-9s %d" % (name, len(shards[name])))
    print("index: %s" % ", ".join(written))
