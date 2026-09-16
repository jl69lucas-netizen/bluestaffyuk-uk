#!/usr/bin/env python3
"""
Generate data/page-dates.json — the truthful per-page freshness map.

WHY A COMMITTED MAP AND NOT A BUILD-TIME `git log`:
BSUK has no deploy workflow until project 6; the honest-date problem this solves is the same
one Foundation recorded for sitemap lastmod. CI checkouts are shallow, so a build-time git
lookup stamps a fake `dateModified` of *today* onto every page on every deploy — the
visible-date rule's dishonesty moved into JSON-LD, which is worse, not better: it would tell
AI crawlers every page changed today, every day.

So: compute real dates HERE, from full local history, and commit the result.

datePublished = the first commit that touched the page file.
dateModified  = the most recent commit that touched it.

Run after adding pages or before a freshness-relevant deploy, then commit the JSON.

Usage:
  python3 scripts/generate_page_dates.py            # write data/page-dates.json
  python3 scripts/generate_page_dates.py --check    # non-zero if the committed map is stale
  python3 scripts/generate_page_dates.py --dry-run  # print the summary, write nothing

Pages are `src/pages/**/*.astro|html` plus `src/content/blog/*.md` — BSUK's posts are a
content collection and would otherwise carry no date at all.

Exit: 0 current/written, 1 ran and found the map stale (or produced 0 routes), 2 cannot run.
"""
import argparse, json, re, subprocess, sys, glob, pathlib

OUT = pathlib.Path("data/page-dates.json")


def route_for(path):
    """src/pages/foo/index.astro -> /foo/ ; src/pages/index.astro -> / ;
    src/content/blog/x.md -> the post's own frontmatter `slug`, which is what
    src/pages/blog/index.astro links to (`/${p.data.slug}/`) — a top-level route, not a
    path derived from the filename. Deriving it would invent a route that is never built."""
    if path.startswith("src/content/blog/"):
        m = re.search(r"^slug:\s*['\"]?([^'\"\n]+)", pathlib.Path(path).read_text(encoding="utf-8"), re.M)
        if not m:
            return None
        return "/" + m.group(1).strip().strip("/") + "/"
    parts = path.split("/")
    if parts[-1] in ("index.astro", "index.html"):
        seg = parts[2:-1]
    else:
        seg = parts[2:-1] + [parts[-1].rsplit(".", 1)[0]]
    return "/" + "/".join(seg) + "/" if seg else "/"


def git_dates(path):
    """(first, last) commit dates for a path as YYYY-MM-DD, or (None, None)."""
    try:
        out = subprocess.run(
            ["git", "log", "--follow", "--format=%cs", "--", path],
            capture_output=True, text=True, check=True).stdout.split()
    except subprocess.CalledProcessError:
        return None, None
    if not out:
        return None, None
    return out[-1], out[0]


def build():
    pages = sorted(glob.glob("src/pages/**/*.astro", recursive=True)) + \
            sorted(glob.glob("src/pages/**/*.html", recursive=True)) + \
            sorted(glob.glob("src/content/blog/*.md"))
    routes, skipped = {}, []
    for p in pages:
        first, last = git_dates(p)
        if not last:
            skipped.append(p)          # never committed yet — no honest date exists
            continue
        # Does the page already emit its own dateModified? Many pages build their
        # schema inline in the BODY (`<script type="application/ld+json"
        # set:html={JSON.stringify(articleSchema)} />`) rather than passing it via the
        # schemaJson prop, so BaseLayout cannot detect it from props — 36 pages ended
        # up with TWO contradicting dates on the first attempt. Detect it here, at the
        # source, and let the layout honour the flag.
        route = route_for(p)
        if route is None:
            skipped.append(p)          # a blog post with no slug has no route to date
            continue
        self_dated = "dateModified" in pathlib.Path(p).read_text(encoding="utf-8")
        routes[route] = {
            "datePublished": first,
            "dateModified": last,
            "selfDated": self_dated,
        }
    return routes, skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate data/page-dates.json from git history.")
    ap.add_argument("--check", action="store_true", help="exit non-zero if the committed map is stale")
    ap.add_argument("--dry-run", action="store_true", help="print the summary, write nothing")
    args = ap.parse_args(argv)

    routes, skipped = build()
    payload = {
        "_meta": {
            "description": ("Truthful per-page freshness map for JSON-LD "
                            "dateModified/datePublished. Generated from git history by "
                            "scripts/generate_page_dates.py — NOT at build time, because "
                            "CI runs a shallow checkout and would stamp today's date on "
                            "every page. Regenerate and commit after content changes."),
            "generated_by": "scripts/generate_page_dates.py",
            "pages": len(routes),
        },
        "routes": routes,
    }
    new = json.dumps(payload, indent=2, sort_keys=False) + "\n"

    if args.check:
        old = OUT.read_text() if OUT.exists() else ""
        old_r = json.loads(old)["routes"] if old else {}
        if old_r != routes:
            drift = set(old_r) ^ set(routes)
            changed = {k for k in set(old_r) & set(routes) if old_r[k] != routes[k]}
            print(f"STALE — {len(drift)} route(s) added/removed, {len(changed)} changed. "
                  "Run: python3 scripts/generate_page_dates.py")
            return 1
        print(f"page-dates.json current — {len(routes)} routes")
        return 0

    if not args.dry_run:
        OUT.write_text(new)
    print(f"{'would write' if args.dry_run else 'wrote'} {OUT} — {len(routes)} routes, "
          f"{len(skipped)} page(s) omitted (never committed)")
    if skipped:
        print(f"  no honest date exists for: {skipped[:4]}")
    if not routes:
        print("0 routes — THIS IS NOT A PASS. Check the glob and that git history exists.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
