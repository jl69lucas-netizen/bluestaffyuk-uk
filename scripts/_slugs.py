"""Shared slug-resolution helpers for the audit scripts.

Convention (matches final_page_audit.py / evidence_audit.py): `index` (and
"" / "/") means EXACTLY dist/index.html; any other slug means EXACTLY
dist/<slug>/index.html (slug may be nested, e.g. available/roys — nested
slugs keep their full path). Deliberately NOT substring matching — see
tests/test_audit_slug_resolution.py for the history of each script's bug.
"""


def dist_path(slug, dist="dist"):
    """Resolve a flat or nested slug to its rendered index.html, per the convention
    above. `dist` may be a str or a pathlib.Path; the return type follows it."""
    import pathlib
    root = pathlib.Path(dist)
    p = root / "index.html" if slug in ("index", "", "/") else root / slug.strip("/") / "index.html"
    return p if isinstance(dist, pathlib.PurePath) else str(p)


def select_pages(paths, slugs, dist="dist"):
    """Resolve slugs to built page paths. `paths` is the list of candidate
    built page paths (as strings); `dist` is the dist-root prefix used to
    build the target paths."""
    if not slugs:
        return paths
    targets = set()
    for s in slugs:
        if s in ("index", "", "/"):
            targets.add(f"{dist}/index.html")
        else:
            targets.add(f"{dist}/{s.strip('/')}/index.html")
    return [p for p in paths if p in targets]


def page_key(path, dist):
    """Slug key for a built page: dist/index.html -> "index";
    dist/<slug>/index.html -> "<slug>" (nested slugs, e.g.
    dist/available/roys/index.html -> "available/roys", keep their full path).
    `path` and `dist` are pathlib.Path objects."""
    rel = path.relative_to(dist).as_posix()
    if rel == "index.html":
        return "index"
    return rel[: -len("/index.html")]


# ── routes through data/page-map.json (Known Issue 39) ───────────────────────────────────────
#
# A page has a KEY and a ROUTE. The key names its per-page files (data/facts/<key>.json,
# data/boards/<key>.json, data/verbatim/<key>.json) and its data/facts/rebuilt.json entry;
# the route is where it is built (dist/<route>/index.html). For a top-level page the two are
# the same. For a city page the key is the bare slug and the route is uk-locations/<slug> —
# the same bare key scripts/migration_parity.py (slug_of) and query_coverage_check.py
# (route_slug) already use, so one rebuilt.json entry means one page to every gate.

import re as _re

# pageboard.SLUG's shape; a segment of dashes alone names nothing and is refused
_SLUG = _re.compile(r"_?(?=[a-z0-9-]*[a-z0-9])[a-z0-9-]+(/(?=[a-z0-9-]*[a-z0-9])[a-z0-9-]+)*")


def _page_map_routes(root):
    """{last segment: route} for every data/page-map.json row but the root, plus
    `uk-locations/<slug>` for every data/locations.json row (a city added there before the
    extractor's map knows it is still a city page). {} with neither file. Two routes ending
    in the same segment would make a bare key ambiguous: refused."""
    import json
    import pathlib
    path = pathlib.Path(root) / "data" / "page-map.json"
    cities = pathlib.Path(root) / "data" / "locations.json"
    urls = []
    if path.is_file():
        urls += [row["url"] for row in json.loads(path.read_text(encoding="utf-8"))["pages"]]
    if cities.is_file():
        urls += ["/uk-locations/%s/" % row["slug"]
                 for row in json.loads(cities.read_text(encoding="utf-8"))]
    routes = {}
    for url in urls:
        route = url.strip("/")
        if not route:
            continue
        last = route.rsplit("/", 1)[-1]
        if routes.get(last, route) != route:
            raise ValueError(f"data/page-map.json + data/locations.json: two routes end in {last!r}: "
                             f"{routes[last]} and {route}")
        routes[last] = route
    return routes


def resolve_page(slug, root):
    """(key, route) for a slug, a route or a route with its slashes.

    `index`, "" and "/" are the site root: ("index", ""). A bare slug, or the full route, of a
    data/page-map.json row (or a data/locations.json city, under uk-locations/) resolves to (its last segment, its route) — so
    `blue-staffy-puppies-for-sale-leeds` and `uk-locations/blue-staffy-puppies-for-sale-leeds`
    are both (`blue-staffy-puppies-for-sale-leeds`, `uk-locations/blue-staffy-puppies-for-sale-leeds`).
    Anything else is a page built after the migration (`available/roys`): its key and route
    are the slug as given. A slug that is not [a-z0-9-] segments joined by '/' (an optional
    leading '_' for pageboard's demo record) raises ValueError: a key names a file, and
    `../x` would name one outside the tree."""
    s = str(slug).strip("/")
    if s in ("", "index"):
        return "index", ""
    if not _SLUG.fullmatch(s):
        raise ValueError(f"not a slug: {slug!r} — expected [a-z0-9-] segments joined by '/'")
    last = s.rsplit("/", 1)[-1]
    route = _page_map_routes(root).get(last)
    if route is not None and s in (last, route):
        return last, route
    return s, s


def built_page(slug, root, dist=None):
    """The built index.html for a slug: <dist>/<route>/index.html, <dist>/index.html for the
    root. `dist` defaults to <root>/dist; the result is a pathlib.Path."""
    import pathlib
    _, route = resolve_page(slug, root)
    base = pathlib.Path(root) / "dist" if dist is None else pathlib.Path(dist)
    return base / route / "index.html" if route else base / "index.html"
