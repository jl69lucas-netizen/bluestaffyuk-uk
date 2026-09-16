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


BLOG_DIR = "src/content/blog"
# The three dynamic templates and the data that decides what they build. A template is not
# a page: `[...post].astro` is ONE file that builds every blog post, so dating the template
# path would put `/[...post]/` in the map and leave all its pages undated. The sources whose
# git history define a generated page's dates are the template PLUS the row or post that
# fills it — a location page changes when either moves.
DYNAMIC = {
    "src/pages/[...post].astro": "blog",
    "src/pages/uk-locations/[slug].astro": ("data/locations.json", "/uk-locations/"),
    "src/pages/available-puppies/[slug].astro": ("data/puppies.json", "/available-puppies/"),
}


def post_slug(path):
    """A blog post's route comes from its frontmatter `slug` — that is what
    src/pages/blog/index.astro links to (`/${p.data.slug}/`) and what `[...post].astro`
    builds. Deriving it from the filename would invent a route nothing ever serves."""
    m = re.search(r"^slug:\s*['\"]?([^'\"\n]+)", pathlib.Path(path).read_text(encoding="utf-8"), re.M)
    return m.group(1).strip().strip("/") if m else None


def rows_with_slugs(path):
    """Every `slug` in a data file, in file order. A row without one builds no page."""
    try:
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [r["slug"] for r in data if isinstance(r, dict) and r.get("slug")]


def expand(template):
    """(route, [source paths]) for every page `template` builds."""
    kind = DYNAMIC[template]
    if kind == "blog":
        out = []
        for md in sorted(glob.glob(f"{BLOG_DIR}/*.md")):
            slug = post_slug(md)
            out.append((f"/{slug}/" if slug else None, [template, md]))
        return out
    data_file, base = kind
    return [(f"{base}{slug}/", [template, data_file]) for slug in rows_with_slugs(data_file)]


def route_for(path):
    """src/pages/foo/index.astro -> /foo/ ; src/pages/index.astro -> /"""
    parts = path.split("/")
    if parts[-1] in ("index.astro", "index.html"):
        seg = parts[2:-1]
    else:
        seg = parts[2:-1] + [parts[-1].rsplit(".", 1)[0]]
    return "/" + "/".join(seg) + "/" if seg else "/"


def span(paths):
    """(earliest first-commit, latest last-commit) across every source of one page."""
    firsts, lasts = [], []
    for p in paths:
        first, last = git_dates(p)
        if last:
            firsts.append(first)
            lasts.append(last)
    return (min(firsts), max(lasts)) if lasts else (None, None)


def coverage(routes, dist="dist"):
    """(dated, built, {built, undated}) — the built pages this map fails to date.

    dist/ is the only honest list of what exists. Without this comparison the map can be
    internally consistent and still miss thirty pages, which is exactly what it did."""
    built = set()
    for f in sorted(glob.glob(f"{dist}/**/index.html", recursive=True)):
        rel = f[len(dist):].rsplit("index.html", 1)[0]
        built.add(rel if rel.startswith("/") else "/" + rel)
    undated = sorted(built - set(routes))
    return len(routes), len(built), {"built": len(built), "undated": undated}


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
    """(routes, skipped, undatable). Static pages by their own path; dynamic templates by
    what they build. No emitted route may contain `[` — that would be an unexpanded
    template, the defect this function exists to prevent."""
    static = [p for p in sorted(glob.glob("src/pages/**/*.astro", recursive=True))
              + sorted(glob.glob("src/pages/**/*.html", recursive=True))
              if p not in DYNAMIC]
    pages = [(route_for(p), [p]) for p in static if "[" not in p]
    for template in sorted(DYNAMIC):
        if pathlib.Path(template).exists():
            pages += expand(template)

    routes, skipped = {}, []
    for route, sources in pages:
        if route is None:
            skipped.append(f"{sources[-1]} (no frontmatter slug — no route to date)")
            continue
        if "[" in route or "]" in route:
            raise AssertionError(f"unexpanded template route {route!r} from {sources}")
        first, last = span(sources)
        if not last:
            skipped.append(sources[-1])     # never committed yet — no honest date exists
            continue
        # Does the page already emit its own dateModified? A page that builds its schema
        # inline in the BODY rather than passing it via the schemaJson prop cannot be
        # detected from props, and would end up with TWO contradicting dates. Detect it at
        # the source and let the layout honour the flag.
        self_dated = any("dateModified" in pathlib.Path(p).read_text(encoding="utf-8", errors="ignore")
                         for p in sources)
        routes[route] = {
            "datePublished": first,
            "dateModified": last,
            "selfDated": self_dated,
        }
    return routes, skipped, None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate data/page-dates.json from git history.")
    ap.add_argument("--check", action="store_true", help="exit non-zero if the committed map is stale")
    ap.add_argument("--dry-run", action="store_true", help="print the summary, write nothing")
    args = ap.parse_args(argv)

    routes, skipped, _ = build()
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
    dated, n_built, cov = coverage(routes)
    print(f"{'would write' if args.dry_run else 'wrote'} {OUT}")
    print(f"routes: {dated} dated, {n_built} built, {len(cov['undated'])} built-but-undated"
          + (f" {cov['undated']}" if cov["undated"] else ""))
    if skipped:
        print(f"  no honest date exists for {len(skipped)} source(s): {skipped[:4]}")
    if not routes:
        print("0 routes — THIS IS NOT A PASS. Check the glob and that git history exists.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
