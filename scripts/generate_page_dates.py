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

Run after adding pages or before a freshness-relevant deploy, then commit the JSON. It is
also `prebuild` in package.json, so every `npm run build` refreshes the map first and no
build can ship a page dated by a map that predates it. Two guards exist because of that —
nobody reads a diff a build wrote:
  * no git on PATH is exit 2 with a sentence saying so, not a FileNotFoundError traceback;
  * a run that dates FEWER routes than the committed map refuses to write (exit 1). A map
    that shrank by itself is a shallow checkout or a broken glob, and overwriting would
    delete the honest dates of pages that still exist.
Note that the dates come from COMMITTED history: an uncommitted edit does not move a page's
date, which is the point — an unpushed working tree has changed nothing a crawler can see.

Usage:
  python3 scripts/generate_page_dates.py            # write data/page-dates.json
  python3 scripts/generate_page_dates.py --check    # non-zero if the committed map is stale
  python3 scripts/generate_page_dates.py --dry-run  # print the summary, write nothing

Pages are `src/pages/**/*.astro|html` plus `src/content/blog/*.md` — BSUK's posts are a
content collection and would otherwise carry no date at all.

Exit: 0 current/written, 1 ran and found the map stale, produced 0 routes, or refused to
shrink it, 2 cannot run (no git, or the committed map is unreadable under --check).
"""
import argparse, json, os, re, subprocess, sys, glob, pathlib, tempfile

# Every path is anchored to the repo root and every git call runs there. Relative globs
# and a bare `git log` made the map a fact about the shell's cwd: run from anywhere else
# it produced zero routes and reported that as if the repo were empty.
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "page-dates.json"


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


def _rel(pattern):
    """Repo-root-relative paths matching `pattern`, whatever the cwd is."""
    n = len(str(ROOT)) + 1
    return [f[n:] for f in glob.glob(str(ROOT / pattern), recursive=True)]


def post_slug(path):
    """A blog post's route comes from its frontmatter `slug` — that is what
    src/pages/blog/index.astro links to (`/${p.data.slug}/`) and what `[...post].astro`
    builds. Deriving it from the filename would invent a route nothing ever serves."""
    m = re.search(r"^slug:\s*['\"]?([^'\"\n]+)", (ROOT / path).read_text(encoding="utf-8"), re.M)
    return m.group(1).strip().strip("/") if m else None


def rows_with_slugs(path):
    """Every `slug` in a data file, in file order. A row without one builds no page."""
    try:
        data = json.loads((ROOT / path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [r["slug"] for r in data if isinstance(r, dict) and r.get("slug")]


def expand(template):
    """(route, [source paths]) for every page `template` builds."""
    kind = DYNAMIC[template]
    if kind == "blog":
        out = []
        for md in sorted(_rel(f"{BLOG_DIR}/*.md")):
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
    for f in sorted(_rel(f"{dist}/**/index.html")):
        rel = f[len(dist):].rsplit("index.html", 1)[0]
        built.add(rel if rel.startswith("/") else "/" + rel)
    undated = sorted(built - set(routes))
    return len(routes), len(built), {"built": len(built), "undated": undated}


class NoGit(Exception):
    """git itself is not on PATH. Distinct from "this path has no history": every date in
    the map would be missing rather than one, and this now runs inside `prebuild`, where a
    bare FileNotFoundError traceback in the middle of a build reads as a build failure with
    no cause attached."""


def git_dates(path):
    """(first, last) commit dates for a path as YYYY-MM-DD, or (None, None)."""
    try:
        out = subprocess.run(
            ["git", "log", "--follow", "--format=%cs", "--", path],
            cwd=str(ROOT), capture_output=True, text=True, check=True).stdout.split()
    except FileNotFoundError as exc:
        raise NoGit(exc) from exc
    except subprocess.CalledProcessError:
        return None, None
    if not out:
        return None, None
    return out[-1], out[0]


def build():
    """(routes, skipped, undatable). Static pages by their own path; dynamic templates by
    what they build. No emitted route may contain `[` — that would be an unexpanded
    template, the defect this function exists to prevent."""
    static = [p for p in sorted(_rel("src/pages/**/*.astro")) + sorted(_rel("src/pages/**/*.html"))
              if p not in DYNAMIC]
    pages = [(route_for(p), [p]) for p in static if "[" not in p]
    for template in sorted(DYNAMIC):
        if (ROOT / template).exists():
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
        self_dated = any("dateModified" in (ROOT / p).read_text(encoding="utf-8", errors="ignore")
                         for p in sources)
        routes[route] = {
            "datePublished": first,
            "dateModified": last,
            "selfDated": self_dated,
        }
    return routes, skipped, None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate data/page-dates.json from git history.")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="exit non-zero if the committed map is stale")
    mode.add_argument("--dry-run", action="store_true", help="print the summary, write nothing")
    args = ap.parse_args(argv)

    try:
        routes, skipped, _ = build()
    except NoGit:
        print("cannot run: `git` is not on PATH, so no date in this map would be a real one. "
              "Install git, or check out with history — do NOT let the build proceed with the "
              "committed map silently unrefreshed.")
        return 2
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
        try:
            old_r = json.loads(OUT.read_text())["routes"] if OUT.exists() else {}
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as e:
            # A corrupt map is not a stale map: nothing was compared, so this is exit 2.
            print(f"unreadable map at {OUT}: {e!r} — regenerate it: "
                  "python3 scripts/generate_page_dates.py")
            return 2
        if old_r != routes:
            drift = set(old_r) ^ set(routes)
            changed = {k for k in set(old_r) & set(routes) if old_r[k] != routes[k]}
            print(f"STALE — {len(drift)} route(s) added/removed, {len(changed)} changed. "
                  "Run: python3 scripts/generate_page_dates.py")
            return 1
        print(f"page-dates.json current — {len(routes)} routes")
        return 0

    # THE MAP MAY GROW OR HOLD; IT MAY NOT SHRINK ON ITS OWN.
    # This runs inside `prebuild` now, so it rewrites the committed map on every build, with
    # nobody reading the diff. A shallow checkout, a half-configured worktree or a glob that
    # stopped matching all express themselves the same way — fewer dated routes than last
    # time — and the overwrite would then quietly delete the honest dates of pages that still
    # exist and ship them undated. Fewer routes is therefore a refusal, not a write: the
    # build fails with the two numbers in it, and a deliberate removal is recorded by running
    # this once by hand and committing the smaller map.
    committed = 0
    try:
        committed = len(json.loads(OUT.read_text())["routes"])
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        pass
    if len(routes) < committed:
        print(f"REFUSING to write: {len(routes)} dated route(s) against {committed} in the "
              f"committed {OUT.name}. A map that shrank by itself means the run saw less "
              "history or fewer pages than the repo has — fix that, or commit the smaller "
              "map deliberately.")
        return 1

    if not args.dry_run:
        # Atomic: the map is committed, so a half-written file is a corrupted record in git
        # rather than something a re-run notices.
        OUT.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(OUT.parent), prefix=OUT.name + ".", suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as fh:
                fh.write(new)
            os.replace(tmp, str(OUT))
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
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
