#!/usr/bin/env python3
"""page_sections — one definition of a board page's parts, shared by every script that asks
"which page is this record, and which of its sections are body?" (system-gaps build, Task 12a).

WHERE A BOARD'S PAGE IS BUILT. A board key is the bare slug; a city page is built at
dist/uk-locations/<slug>/. resolve_page() turns either spelling into (key, route) from
data/page-map.json. `_slugs.resolve_page` replaces it when that shared resolver exists
(p5-readiness Task 43, F2a); until then the same rule runs here. Read by
scripts/outline_provenance_check.py and scripts/image_candidates.py.

WHICH SECTIONS ARE BODY. The fixed frame of docs/reference/location-page-template.md, spelled
as the record spells it, is never body:

  FRAME_SHAPES  hero, takeaways, stats (counter), trust, reviews, faq, form, puppies (the
                puppy grid), divider, and the chrome shapes nav, dial, sheet and strip
  FRAME_IDS     top, key-takeaways, newsletter (the ids scripts/query_coverage_check.py
                treats as frame; a test pins the two)
  an FAQ block  a section of shape `faq`, OR any section carrying `questions` (the older
                spelling: a standard section with id `faq`). Its tree holds data/faq.json row
                ids, and every H3 in it is a question, never an outline heading.

body_sections(board) is every other section, in record order. Read by
scripts/outline_provenance_check.py (the outline a built page is compared with),
scripts/family_rules.py outline_heading_repeat (an FAQ block's tree is not headings) and
scripts/image_rules.py.

ONE PURPOSE DIFFERENCE. The image rule also exempts OWN_MEDIA_SHAPES (video, puppies): those
sections are body copy-wise, but their media IS the video or the puppy cards, so they are
never asked for an image slot. `puppies` is already frame; `video` is the one section the
outline gate compares and the image rule does not ask for a picture.

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


# ── sections ──────────────────────────────────────────────────────────────────────────────
FRAME_SHAPES = frozenset({"hero", "takeaways", "stats", "trust", "reviews", "faq", "form",
                          "puppies", "divider", "dial", "sheet", "strip", "nav"})
FRAME_IDS = frozenset({"top", "key-takeaways", "newsletter"})
OWN_MEDIA_SHAPES = frozenset({"video", "puppies"})


def is_faq_block(section):
    """Shape `faq`, or any section carrying `questions`."""
    return section.get("shape") == "faq" or bool(section.get("questions"))


def is_frame(section):
    return (section.get("shape") in FRAME_SHAPES or section.get("id") in FRAME_IDS
            or is_faq_block(section))


def body_sections(board):
    """Every section of the record that is not frame, in record order."""
    return [s for s in board.get("sections", []) if not is_frame(s)]
