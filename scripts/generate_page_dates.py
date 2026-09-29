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

datePublished = the first commit that touched the page file — and never later than the
                earliest datePublished any COMMITTED data/page-dates.json gave the route: a
                URL that changes source (a city leaving the template for its own file, Plan 2
                Task 8) was still published when it was first published. The floor is
                ONE-WAY: a date an old map got wrong is corrected by a `floor_override`
                (route -> datePublished + reason) in data/page-dates-ignore.json.
dateModified  = the most recent commit that touched it, less the commits
                data/page-dates-ignore.json lists for that path: a commit that changed a
                route's sources without changing its content (the template's own-file skip)
                is not a modification, and counting it stamps a false freshness date on
                every page the template builds (working rule 9).

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
# Commits that changed a page's SOURCES without changing what the page says, each ignored for
# the source paths it names (a commit that also created a real page stays real for that page).
IGNORE = "data/page-dates-ignore.json"
MAP = "data/page-dates.json"


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
    slugs = [r["slug"] for r in data if isinstance(r, dict) and r.get("slug")]
    dup = sorted({x for x in slugs if slugs.count(x) > 1})
    if dup:
        raise DataFileError(f"{path} has more than one row with the slug {', '.join(dup)}; one page "
                            "cannot be built or dated from two rows, so give each row its own slug.")
    return slugs


def expand(template, static_routes=frozenset()):
    """(route, [source paths]) for every page `template` builds. A data row whose route a
    STATIC page already builds is not the template's: src/pages/uk-locations/[slug].astro skips
    a city that has its own file (the London component design pass, Plan 2), so that city is
    dated by its own file alone."""
    kind = DYNAMIC[template]
    if kind == "blog":
        out = []
        for md in sorted(_rel(f"{BLOG_DIR}/*.md")):
            slug = post_slug(md)
            out.append((f"/{slug}/" if slug else None, [template, md]))
        return out
    data_file, base = kind
    # A data-driven page's data source is ITS OWN ROW, `data/x.json#slug` (Task 8b review, B2):
    # a real edit to one city's row re-dates that city alone. The template stays a shared source.
    return [(f"{base}{slug}/", [template, f"{data_file}{ROW}{slug}"]) for slug in rows_with_slugs(data_file)
            if f"{base}{slug}/" not in static_routes]


#: Separates a data file from a row's slug in a row source, `data/locations.json#<slug>`.
ROW = "#"


def route_for(path):
    """src/pages/foo/index.astro -> /foo/ ; src/pages/index.astro -> /"""
    parts = path.split("/")
    if parts[-1] in ("index.astro", "index.html"):
        seg = parts[2:-1]
    else:
        seg = parts[2:-1] + [parts[-1].rsplit(".", 1)[0]]
    return "/" + "/".join(seg) + "/" if seg else "/"


def span(paths, ignore=()):
    """(earliest first-commit, latest last-commit) across every source of one page."""
    firsts, lasts = [], []
    for p in paths:
        first, last = git_dates(p, ignore)
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


def _git(*args):
    try:
        return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True,
                              check=True).stdout
    except FileNotFoundError as exc:
        raise NoGit(exc) from exc


class IgnoreFileError(ValueError):
    """data/page-dates-ignore.json cannot be used. The date step stops (exit 2) with this one
    sentence rather than dating by every commit, which is the defect the file exists to fix."""


_SHA = re.compile(r"^[0-9a-fA-F]{7,40}$")
_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _load_ignore():
    """The parsed ignore file, shape-checked, or None when there is none."""
    f = ROOT / IGNORE
    if not f.exists():
        return None
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise IgnoreFileError(f"{IGNORE} is not readable JSON ({e}); fix it before any page is dated.")
    if not isinstance(data, dict) or not isinstance(data.get("commits"), list):
        raise IgnoreFileError(f"{IGNORE} must be an object with a `commits` list.")
    for r in data["commits"]:
        ok = (isinstance(r, dict) and isinstance(r.get("sha"), str) and _SHA.match(r["sha"])
              and isinstance(r.get("paths"), list) and r["paths"]
              and all(isinstance(x, str) and x for x in r["paths"])
              and isinstance(r.get("reason"), str) and r["reason"].strip())
        if not ok:
            raise IgnoreFileError(f"{IGNORE}: every entry needs a `sha` of 7 to 40 hex characters, a "
                                  f"non-empty `paths` list of strings and a `reason`; this one does not: {r!r}")
    fan = data.get("fanout_accepted", [])
    if not isinstance(fan, list) or not all(
            isinstance(r, dict) and isinstance(r.get("sha"), str) and _SHA.match(r["sha"])
            and isinstance(r.get("reason"), str) and r["reason"].strip() for r in fan):
        raise IgnoreFileError(f"{IGNORE}: `fanout_accepted` is a list of entries, each with a `sha` "
                              "of 7 to 40 hex characters and a `reason`.")
    over = data.get("floor_override", {})
    if not isinstance(over, dict) or not all(
            isinstance(v, dict) and isinstance(v.get("datePublished"), str) and _DAY.match(v["datePublished"])
            and isinstance(v.get("reason"), str) and v["reason"].strip() for v in over.values()):
        raise IgnoreFileError(f"{IGNORE}: `floor_override` maps a route to a `datePublished` "
                              "(YYYY-MM-DD) and a `reason`.")
    return data


def ignored_commits():
    """[(full sha, {paths})] from data/page-dates-ignore.json; [] when the file is absent.
    Every SHA is resolved ONCE to the one commit it names in this history (`git rev-parse
    --verify`) and compared in full: a SHA that is missing or ambiguous here is refused, never
    matched by prefix against whatever happens to share it."""
    data = _load_ignore()
    if not data:
        return []
    return [(_resolve(r["sha"], "commits"), set(r["paths"])) for r in data["commits"]]


def _resolve(sha, key):
    try:
        full = _git("rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}").strip()
    except subprocess.CalledProcessError:
        full = ""
    if not full:
        raise IgnoreFileError(f"{IGNORE} `{key}`: {sha} is not exactly one commit of this "
                              "repository's history (missing or ambiguous); list its full SHA.")
    return full.lower()


def accepted_fanout():
    """{full sha} from `fanout_accepted`: commits whose re-dating of many routes is real, because
    the content of every page they re-date really changed (checked by diffing the build)."""
    data = _load_ignore()
    return {_resolve(r["sha"], "fanout_accepted") for r in (data or {}).get("fanout_accepted", [])}


def floor_overrides():
    """{route: datePublished} from the ignore file's optional `floor_override`."""
    data = _load_ignore()
    return {k: v["datePublished"] for k, v in (data or {}).get("floor_override", {}).items()}


def published_floor():
    """{route: earliest datePublished in any committed version of data/page-dates.json}.

    THE FLOOR IS ONE-WAY: once any commit of the map carried a date for a route, no later run
    can move that route's datePublished later, only keep or lower it. A date that was WRONG in
    an old map is therefore corrected by a `floor_override` (route -> datePublished + reason)
    in data/page-dates-ignore.json, never by editing history. Every version is read through ONE
    `git cat-file --batch` process, so the whole history costs two git calls."""
    floor = {}
    try:
        shas = _git("log", "--format=%H", "--", MAP).split()
    except subprocess.CalledProcessError:
        return floor
    if not shas:
        return floor
    try:
        raw = subprocess.run(["git", "cat-file", "--batch"], cwd=str(ROOT), capture_output=True,
                             check=True, input="".join(f"{s}:{MAP}\n" for s in shas).encode()).stdout
    except FileNotFoundError as exc:
        raise NoGit(exc) from exc
    except subprocess.CalledProcessError:
        return floor
    i = 0
    while i < len(raw):
        nl = raw.index(b"\n", i)
        head = raw[i:nl].split()
        i = nl + 1
        if len(head) < 3 or head[1] != b"blob":
            continue                       # "<rev> missing": that commit deleted the map
        size = int(head[2])
        body, i = raw[i:i + size], i + size + 1
        try:
            routes = json.loads(body.decode("utf-8"))["routes"]
        except (ValueError, KeyError, TypeError):
            continue
        for route, row in routes.items():
            d = isinstance(row, dict) and row.get("datePublished")
            if d and (route not in floor or d < floor[route]):
                floor[route] = d
    return floor


_DATES_CACHE = {}


def git_dates(path, ignore=()):
    """(first, last) commit dates for a path as YYYY-MM-DD, or (None, None), skipping every
    commit `ignore` lists for this path. Cached per (root, path, ignore) for the run: the
    location and puppy templates share their two sources across every page they build."""
    log = _counted_log(path, ignore)
    return (log[-1][1], log[0][1]) if log else (None, None)


#: The row keys each data-driven template RENDERS (Task 8b re-review, N1). Only these date a
#: page: `defects`, `word_count` and `canonical` sit in data/locations.json for the tooling and
#: never reach a city page, so a commit that changes them on every row changes no page.
#: tests/py/test_page_dates.py pins each list to the keys its template reads.
RENDERED = {
    "data/locations.json": ("body_html", "city", "description", "h1", "og_type", "robots",
                            "schema", "slug", "title"),
    "data/puppies.json": ("card_photo", "colour", "gallery", "name", "price_gbp", "sex", "slug",
                          "status"),
}


class DataFileError(ValueError):
    """A data file cannot date its pages (a duplicate slug). Exit 2, one sentence."""


def _rows_of(data_file, body):
    """{slug: canonical JSON of its rendered keys} for one version of `data_file`, or None when
    the version does not parse (it is skipped: the rows before it stand, M1)."""
    try:
        data = json.loads(body.decode("utf-8"))
    except (ValueError, AttributeError):
        return None
    if not isinstance(data, list):
        return None
    keys = RENDERED.get(data_file)
    out = {}
    for r in data:
        if isinstance(r, dict) and r.get("slug"):
            out[r["slug"]] = json.dumps({k: v for k, v in r.items() if keys is None or k in keys},
                                        sort_keys=True)
    return out


def _row_logs(data_file):
    """{slug: [(sha, YYYY-MM-DD)] newest first}: for every row of `data_file`, the commits in
    which THAT ROW's rendered keys changed, its first appearance included.

    Each commit is compared with its REAL PARENTS, not with the commit before it in log order
    (N2): a merge counts a row as changed only when it differs from every parent, so merging a
    branch that edited x1 into a main that edited x8 re-dates neither. Every version, the
    commits' and their parents', is read through ONE `git cat-file --batch`; a version that does
    not parse stands in for nothing (the rows of its own first parent carry through, M1). A row
    is compared by the canonical JSON of the keys its template renders (RENDERED), so a reorder,
    a reformat or an unrendered key changes no row."""
    key = (str(ROOT), "rows", data_file)
    if key in _DATES_CACHE:
        return _DATES_CACHE[key]
    try:
        log = [l.split() for l in _git("log", "--topo-order", "--reverse", "--format=%H %cs %P",
                                       "--", data_file).splitlines() if l]
    except subprocess.CalledProcessError:
        log = []
    revs = []
    for sha, _date, *parents in log:
        revs.append(f"{sha}:{data_file}")
        revs += [f"{p}:{data_file}" for p in parents]
    blobs = iter(_cat_file(revs))
    by_oid = {}                        # blob id -> the rows it stands for (parsed or carried)
    rows_log = {}

    def rows_for(oid, body):
        if oid is None:
            return {}                  # the file did not exist in that commit
        if oid not in by_oid:
            by_oid[oid] = _rows_of(data_file, body)
        return by_oid[oid]

    for sha, date, *parents in log:            # oldest first; every parent before its child
        oid, body = next(blobs)
        parent_rows = []
        for _ in parents:
            p_oid, p_body = next(blobs)
            parent_rows.append(rows_for(p_oid, p_body))
        parent_rows = [r for r in parent_rows if r is not None] or ([{}] if not parents else [])
        mine = rows_for(oid, body)
        if mine is None:                       # does not parse: carries its first parent's rows
            by_oid[oid] = parent_rows[0] if parent_rows else {}
            continue
        for slug, canon in mine.items():
            if all(pr.get(slug) != canon for pr in parent_rows):
                rows_log.setdefault(slug, []).insert(0, (sha, date))
    _DATES_CACHE[key] = rows_log
    return rows_log


def _cat_file(revs):
    """[(blob id, bytes)] for each `rev:path` in `revs`, in order ((None, None) where missing),
    through one `git cat-file --batch` process."""
    if not revs:
        return []
    try:
        raw = subprocess.run(["git", "cat-file", "--batch"], cwd=str(ROOT), capture_output=True,
                             check=True, input="".join(f"{r}\n" for r in revs).encode()).stdout
    except FileNotFoundError as exc:
        raise NoGit(exc) from exc
    except subprocess.CalledProcessError:
        return [(None, None)] * len(revs)
    out, i = [], 0
    while i < len(raw) and len(out) < len(revs):
        nl = raw.index(b"\n", i)
        head = raw[i:nl].split()
        i = nl + 1
        if len(head) < 3 or head[1] != b"blob":
            out.append((None, None))
            continue
        size = int(head[2])
        out.append((head[0].decode(), raw[i:i + size]))
        i += size + 1
    return out + [(None, None)] * (len(revs) - len(out))


def _counted_log(path, ignore=()):
    """[(sha, YYYY-MM-DD)] newest first, for the commits that date `path` (ignored ones out).
    A row source (`data/x.json#slug`) is dated by the commits that changed that row; an ignore
    entry for the data file applies to its rows."""
    key = (str(ROOT), path, tuple((s, tuple(sorted(p))) for s, p in ignore))
    if key in _DATES_CACHE:
        return _DATES_CACHE[key]
    if ROW in path:
        data_file, slug = path.split(ROW, 1)
        log = [(sha, d) for sha, d in _row_logs(data_file).get(slug, [])
               if not any(sha == full and data_file in paths for full, paths in ignore)]
        _DATES_CACHE[key] = log
        return log
    try:
        out = _git("log", "--follow", "--format=%H %cs", "--", path).split("\n")
    except subprocess.CalledProcessError:
        out = []
    log = []
    for line in filter(None, out):
        sha, date = line.split()
        if any(sha == full and path in paths for full, paths in ignore):
            continue
        log.append((sha, date))
    _DATES_CACHE[key] = log
    return log


#: route -> (sha, source path) of the commit that set its dateModified, filled by build().
LAST_COMMIT = {}
#: `fanout_accepted`, resolved by build() so a bad SHA stops every run, map or no map.
ACCEPTED = set()


def fanout_problems(routes):
    """Sentences for every commit that moves dateModified on FANOUT or more routes, against the
    map at HEAD, and is listed neither in `commits` (no content change: the dates stay) nor in
    `fanout_accepted` (real content change on every page). A no-content commit to a shared
    source re-dated every page it builds three times on the London branch (6520267, c2705da,
    142b3d6) before this guard; each would have been refused here."""
    try:
        head = json.loads(_git("show", f"HEAD:{MAP}"))["routes"]
    except (subprocess.CalledProcessError, ValueError, KeyError, TypeError):
        return []
    accepted = ACCEPTED
    groups = {}
    for route, row in routes.items():
        old = head.get(route)
        if not isinstance(old, dict) or old.get("dateModified") == row["dateModified"]:
            continue
        if route in LAST_COMMIT:
            sha, src = LAST_COMMIT[route]
            # A row source is named by its data file: one commit that changes rendered keys on
            # 3+ rows re-dates 3+ pages at once and meets the same bar (Task 8b re-review, N1).
            groups.setdefault(sha, {}).setdefault(src.split(ROW, 1)[0], []).append(route)
    out = []
    # Grouped by COMMIT alone (B1): one commit that edits three pages' own files re-dates three
    # routes as surely as one commit to a shared template does.
    for sha, by_src in sorted(groups.items()):
        moved = sorted(r for rs in by_src.values() for r in rs)
        if len(moved) < FANOUT or sha in accepted:
            continue
        srcs = ", ".join(sorted(by_src))
        shown = ", ".join(moved[:6]) + (f" and {len(moved) - 6} more" if len(moved) > 6 else "")
        out.append(f"commit {sha[:10]} moves dateModified on {len(moved)} routes ({shown}) through "
                   f"{srcs}; diff those built pages against the build before it, then list the "
                   f"commit in {IGNORE} under `commits` for those paths if no page's content "
                   "changed, or under `fanout_accepted` with a reason if every page's content "
                   "really changed. A data file counts only the rows whose rendered keys changed.")
    return out


FANOUT = 3


def build():
    """(routes, skipped, undatable). Static pages by their own path; dynamic templates by
    what they build. No emitted route may contain `[` — that would be an unexpanded
    template, the defect this function exists to prevent."""
    static = [p for p in sorted(_rel("src/pages/**/*.astro")) + sorted(_rel("src/pages/**/*.html"))
              if p not in DYNAMIC]
    pages = [(route_for(p), [p]) for p in static if "[" not in p]
    static_routes = frozenset(r for r, _ in pages)
    own_row_routes = set()
    # An OWN-FILE page for a data row (London's scaffold, /uk-locations/<slug>.astro) still
    # renders that row (its title, description, migrated body), so the row is its second source,
    # compared on the same rendered keys (Task 8c).
    for kind in DYNAMIC.values():
        if kind == "blog":
            continue
        data_file, base = kind
        own = {f"{base}{slug}/": f"{data_file}{ROW}{slug}" for slug in rows_with_slugs(data_file)}
        pages = [(r, srcs + [own[r]] if r in own else srcs) for r, srcs in pages]
        own_row_routes.update(r for r in own if r in static_routes)
    for template in sorted(DYNAMIC):
        if (ROOT / template).exists():
            pages += expand(template, static_routes)

    _DATES_CACHE.clear()        # history may have moved since the last call in this process
    LAST_COMMIT.clear()
    ACCEPTED.clear()
    ACCEPTED.update(accepted_fanout())
    ignore, floor, override = ignored_commits(), published_floor(), floor_overrides()
    routes, skipped = {}, []
    for route, sources in pages:
        if route is None:
            skipped.append(f"{sources[-1]} (no frontmatter slug — no route to date)")
            continue
        if "[" in route or "]" in route:
            raise AssertionError(f"unexpanded template route {route!r} from {sources}")
        first, last = span(sources, ignore)
        rows = [p for p in sources if ROW in p]
        if rows and last:
            # A data route was published when its ROW first appeared, not when the template
            # did (Task 8b re-review, M3); the floor from committed maps still applies below.
            row_log = _counted_log(rows[0], ignore)
            if row_log:
                first = row_log[-1][1]
        newest = [(log[0][1], log[0][0], p) for p in sources if (log := _counted_log(p, ignore))]
        if newest:
            top = max(d for d, _, _ in newest)
            # On a tie a SHARED source takes the blame, so a commit that touched the template
            # and the rows is still judged as the template's fan-out.
            _, sha, src = sorted((t for t in newest if t[0] == top), key=lambda t: ROW in t[2])[0]
            LAST_COMMIT[route] = (sha, src)
        if not last:
            skipped.append(sources[-1])     # never committed yet — no honest date exists
            continue
        # The URL was published when it was first published, whatever builds it now.
        if route in floor and floor[route] < first:
            first = floor[route]
        if route in override:            # a wrong committed date, corrected with its reason
            first = override[route]
        # Does the page already emit its own dateModified? A page that builds its schema
        # inline in the BODY rather than passing it via the schemaJson prop cannot be
        # detected from props, and would end up with TWO contradicting dates. Detect it at
        # the source and let the layout honour the flag.
        # An own-file page's schema is its own file's; the row it reads for its words does not
        # make it self-dated (the data file mentions dateModified in other rows' schema).
        flag_sources = sources[:-1] if route in own_row_routes else sources
        self_dated = any("dateModified" in (ROOT / p.split(ROW, 1)[0]).read_text(encoding="utf-8", errors="ignore")
                         for p in flag_sources)
        routes[route] = {
            "datePublished": first,
            "dateModified": last,
            "selfDated": self_dated,
        }
    return routes, skipped, None


def derive_routes(root=None):
    """build()'s routes for another checkout (a test's tmp repo), in-process: every helper
    reads the module's ROOT, so it is pointed at `root` for the call and restored after.
    Raises NoGit as build() does."""
    global ROOT
    saved = ROOT
    ROOT = pathlib.Path(root) if root is not None else ROOT
    try:
        return build()[0]
    finally:
        ROOT = saved


def is_current(root=None):
    """True when <root>/data/page-dates.json holds exactly the routes a fresh derivation from
    committed history gives — the --check test, in-process. An unreadable map, or no git, is
    not current. scripts/page_run_record.py dirty_tracked sets the map aside only then."""
    base = pathlib.Path(root) if root is not None else ROOT
    try:
        old = json.loads((base / "data" / "page-dates.json").read_text(encoding="utf-8"))["routes"]
        return old == derive_routes(base)
    except (NoGit, OSError, ValueError, KeyError, TypeError):
        return False


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate data/page-dates.json from git history.")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="exit non-zero if the committed map is stale")
    mode.add_argument("--dry-run", action="store_true", help="print the summary, write nothing")
    args = ap.parse_args(argv)

    try:
        routes, skipped, _ = build()
        fanout = fanout_problems(routes)
    except (IgnoreFileError, DataFileError) as e:
        print(f"cannot run: {e}")
        return 2
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

    if fanout:
        # One refusal for write, --dry-run and --check alike: nothing is written.
        for line in fanout:
            print(f"REFUSING to re-date: {line}")
        return 1

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
