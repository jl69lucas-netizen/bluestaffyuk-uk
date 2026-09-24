#!/usr/bin/env python3
"""page_sections — one definition of a board page's parts, shared by every script that asks
"which page is this record, and which of its sections are body?" (system-gaps build, Task 12a).

WHERE A BOARD'S PAGE IS BUILT. A board key is the bare slug; a city page is built at
dist/uk-locations/<slug>/. resolve_page() turns either spelling into (key, route) from
data/page-map.json. `_slugs.resolve_page` replaces it when that shared resolver exists
(p5-readiness Task 43, F2a); until then the same rule runs here. Read by
scripts/outline_provenance_check.py and scripts/image_candidates.py.

This module imports nothing from the board scripts, so any of them can import it.
"""
import json
from pathlib import Path

try:  # p5-readiness Task 43 (F2a) adds the shared resolver; the local one below mirrors it.
    from _slugs import resolve_page as _shared_resolve_page  # noqa: E402
except ImportError:  # pragma: no cover — depends on merge order
    _shared_resolve_page = None


# ── routes ────────────────────────────────────────────────────────────────────────────────
def page_map_routes(root):
    """{last segment: route} for every row of data/page-map.json, first row wins."""
    path = Path(root) / "data" / "page-map.json"
    if not path.is_file():
        return {}
    routes = {}
    for row in json.loads(path.read_text(encoding="utf-8"))["pages"]:
        route = row["url"].strip("/")
        if route:
            routes.setdefault(route.rsplit("/", 1)[-1], route)
    return routes


def resolve_page(slug, root):
    """(key, route): the shared resolver when it exists, else the same rule locally — a bare
    slug or full route of a data/page-map.json row is (its last segment, its route); anything
    else is (slug, slug); the root is ("index", "")."""
    if _shared_resolve_page is not None:
        return _shared_resolve_page(slug, root)
    s = str(slug).strip("/")
    if s in ("", "index"):
        return "index", ""
    last = s.rsplit("/", 1)[-1]
    route = page_map_routes(root).get(last)
    if route is not None and s in (last, route):
        return last, route
    return s, s
