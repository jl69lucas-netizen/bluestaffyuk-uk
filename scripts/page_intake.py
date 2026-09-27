#!/usr/bin/env python3
"""page_intake.py <slug> [--json] — a page's starting state, found by looking.

The page-build brief opens every page with a target block, and its rule is that the mode is
determined by looking, never assumed, and a baseline reads NOT FETCHED only with its barrier.
Project 5 starts its 28 city pages from different states: stubs with no verbatim set (Known
Issue 79), indexable bodies that print retired terms (Known Issue 65), rows with an empty h1
(Known Issue 59). This reads each page's state from the files, so no builder works it out
again from nothing, and scripts/build_page_board.py renders the same lines as block 0 of the
page's board.

Fields: mode (stub · migrated · rebuilt · new), robots (from the built page, else the data
row), the built file with its size and freshness, the sitemap entry, the verbatim set, the H1,
the question file, the LLM-intel file, the board's status, the Search Console baseline with
its barrier, inbound links from other pages' <main>, and retired-term hits: the findings
scripts/retired_facts_check.py (npm run check:retired) makes on the built page — else on the
city row's body_html — judged by the same functions against the same locked set, so the
intake and the gate never disagree about what is retired.

Usage:
  python3 scripts/page_intake.py <slug>          # print the intake
  python3 scripts/page_intake.py <slug> --json   # print it as JSON

Exit 0 with the intake printed; 2 when the slug is malformed or no data file knows it (not in
data/locations.json, not in data/page-map.json, and no data/boards/<slug>.json).
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pageboard as PB  # noqa: E402
import retired_facts_check as RFC  # noqa: E402
import verbatim_set_check as VSC  # noqa: E402
from _slugs import resolve_page  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]

MODES = ("stub", "migrated", "rebuilt", "new")
#: How each kind of retired_facts_check finding is labelled on the board.
RETIRED_LABEL = {"amount": "{} (not a locked amount)", "term": "{}",
                 "city": "{} (former city)", "home": "{} (former home)"}
ROBOTS = re.compile(r"""<meta\s+name=["']robots["']\s+content=["']([^"']*)["']""", re.I)
MAIN = re.compile(r"<main\b[\s\S]*?</main>", re.I)
HREF = re.compile(r"""href=["']([^"'#?]+)""")
#: Built pages that are specimens of the kit, not pages a reader reaches.
SPECIMENS = ("board-preview", "kit-preview")


class UnknownSlug(Exception):
    pass


def _read_json(path, default):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def locked_amounts(root):
    """check:retired's locked set for this tree: ({single £ values}, {(low, high) ranges}),
    read from data/settings.json and data/price-matrix.json, never typed here."""
    return RFC.locked_amounts(pathlib.Path(root))


def retired_hits(markup, locked, key):
    """{label: count} for every retired_facts_check finding in one page's markup: an £ figure
    or range outside the locked set, a retired term, the former city (except on the one page
    that sells puppies there) and a former-home claim."""
    hits = {}
    for kind, value in RFC.html_findings(markup, locked, city_page=key == RFC.FORMER_CITY_PAGE):
        label = RETIRED_LABEL[kind].format(value)
        hits[label] = hits.get(label, 0) + 1
    return hits


def inbound_links(route, dist):
    """How many OTHER built pages link to /<route>/ from inside their <main>. Site chrome (the
    header and the footer's city list) links every city from every page and says nothing about
    where equity points, so it is not counted."""
    target = "/" + route.strip("/") + "/"
    own = dist / route / "index.html"
    pages = 0
    for page in sorted(dist.rglob("index.html")):
        rel = page.relative_to(dist).as_posix()
        if page == own or rel.startswith(SPECIMENS):
            continue
        m = MAIN.search(page.read_text(encoding="utf-8", errors="ignore"))
        if m and any(re.sub(r"^https?://[^/]+", "", h).rstrip("/") + "/" == target
                     for h in HREF.findall(m.group(0))):
            pages += 1
    return pages


def intake(slug, root=None, dist=None):
    """The page's starting state as a dict. Raises UnknownSlug when no data file knows it."""
    root = pathlib.Path(root) if root is not None else ROOT
    dist = pathlib.Path(dist) if dist is not None else root / "dist"
    try:
        key, route = resolve_page(slug, root)
        board_file = root / "data/boards" / (PB.slug_file(key) + ".json")
    except (ValueError, PB.BoardError) as e:
        raise UnknownSlug(str(e))
    city = next((r for r in _read_json(root / "data/locations.json", [])
                 if isinstance(r, dict) and r.get("slug") == key), None)
    pm_rows = _read_json(root / "data/page-map.json", {}).get("pages", [])
    pm = next((r for r in pm_rows if isinstance(r, dict)
               and r.get("url", "").strip("/") == route), None)
    board = _read_json(board_file, None) if board_file.is_file() else None
    if city is None and pm is None and board is None:
        raise UnknownSlug(f"{slug}: not in data/locations.json, not in data/page-map.json, "
                          f"and no {board_file.relative_to(root)}")

    rebuilt = key in PB.rebuilt_slugs(root / "data/facts/rebuilt.json")
    if rebuilt:
        mode = "rebuilt"
    elif city is not None:
        mode = "stub" if "stub" in (city.get("defects") or []) else "migrated"
    elif pm is not None:
        mode = "migrated"
    else:
        mode = "new"

    built = dist / route / "index.html" if route else dist / "index.html"
    html = built.read_text(encoding="utf-8", errors="ignore") if built.is_file() else ""
    m = ROBOTS.search(html)
    if m:
        robots = m.group(1)
    elif city is not None:
        robots = city.get("robots") or "NOT FETCHED — the data row carries no robots value"
    else:
        robots = "NOT FETCHED — not built yet"

    if not dist.is_dir():
        sitemap = None
    else:
        loc = "/" + route + "/" if route else "/"
        sitemap = any(f"{loc}</loc>" in p.read_text(encoding="utf-8", errors="ignore")
                      for p in dist.glob("*.xml"))

    h1 = (city or pm or {}).get("h1")
    if board is not None and not h1:
        bh = board.get("h1") or {}
        pick = bh.get("pick") if bh.get("pick") is not None else bh.get("recommended")
        variants = bh.get("variants") or []
        if isinstance(pick, int) and 0 <= pick < len(variants):
            h1 = variants[pick]

    applies = _read_json(root / "data/verbatim/applies.json", {}).get("slugs", [])
    vfile = root / "data/verbatim" / f"{key}.json"
    if mode == "stub":
        verbatim = "stub — no verbatim set (Known Issue 79)"
    elif vfile.is_file():
        verbatim = len(VSC.elements(_read_json(vfile, {})))
    elif mode == "migrated":
        verbatim = (f"not extracted — run python3 scripts/verbatim_set_check.py --extract {key} "
                    "before any rewrite")
    else:
        verbatim = "none — a new page has no migrated wording"

    llm = sorted((root / "docs/research/llm-intel").glob(f"{key}-*.json"))
    llm_status = None
    if llm:
        llm_status = (_read_json(llm[-1], {}).get("fetched") or {}).get("status")

    if pm is not None and pm.get("baseline_gsc"):
        baseline = pm["baseline_gsc"]
    elif (root / "data/analytics").is_dir():
        baseline = "data/analytics/ exists — read it before writing NOT FETCHED"
    else:
        baseline = "NOT FETCHED — no Search Console export under data/analytics/"

    # The built page is what check:retired judges; before a build, the city row's body_html.
    markup = html or ((city or {}).get("body_html") or "")

    return {
        "slug": key,
        "route": route,
        "page_type": (board or {}).get("meta", {}).get("page_type") or (
            "location" if city is not None else None),
        "mode": mode,
        "robots": robots,
        "built": ({"path": built.relative_to(root).as_posix() if root in built.parents
                   else str(built), "bytes": built.stat().st_size,
                   "fresh": PB.dist_page_is_fresh(built, root, key)}
                  if built.is_file() else None),
        "sitemap": sitemap,
        "h1": h1 if h1 else "EMPTY",
        "verbatim": verbatim,
        "verbatim_applies": key in applies,
        "question_file": (root / "data/queries" / f"{key}.json").is_file(),
        "llm_intel": ({"file": llm[-1].relative_to(root).as_posix(), "status": llm_status}
                      if llm else None),
        "board": (board or {}).get("meta", {}).get("status") if board else None,
        "baseline": baseline,
        "inbound_links": inbound_links(route, dist) if dist.is_dir() and route else 0,
        "retired": retired_hits(markup, locked_amounts(root), key) if markup else {},
    }


def rows(it):
    """[(field, value)] in the order the board shows them."""
    built = it["built"]
    llm = it["llm_intel"]
    return [
        ("Mode", it["mode"]),
        ("Page type", it["page_type"] or "not recorded"),
        ("Route", "/" + it["route"] + "/" if it["route"] else "/"),
        ("Robots", it["robots"]),
        ("Built page", "not built" if built is None else
         "%s — %d bytes, %s" % (built["path"], built["bytes"],
                                "fresh" if built["fresh"] else "STALE: run npm run build")),
        ("Sitemap entry", "no dist/ to read" if it["sitemap"] is None else
         ("listed" if it["sitemap"] else "not listed")),
        ("H1", it["h1"]),
        ("Verbatim set", "%s element(s)" % it["verbatim"] if isinstance(it["verbatim"], int)
         else it["verbatim"]),
        ("Question file", "data/queries/%s.json" % it["slug"] if it["question_file"]
         else "none — run bsuk-query-augmentation"),
        ("LLM intel", "none — run bsuk-llm-keyword-intel" if llm is None else
         "%s (%s)" % (llm["file"], llm["status"])),
        ("Board", it["board"] or "none"),
        ("Search Console baseline", it["baseline"]),
        ("Inbound links (other pages' main)", str(it["inbound_links"])),
        ("Retired-term hits", ", ".join("%s × %d" % (k, n) for k, n in sorted(it["retired"].items()))
         or "none"),
    ]


def render_md(it):
    """The intake as a two-column markdown table, the form block 0 of the board shows."""
    esc = lambda v: str(v).replace("|", "\\|")
    lines = ["| Field | Value |", "|---|---|"]
    lines += ["| %s | %s |" % (esc(k), esc(v)) for k, v in rows(it)]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="page_intake.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--json", action="store_true", help="print the intake as JSON")
    ns = ap.parse_args(argv)
    try:
        it = intake(ns.slug)
    except UnknownSlug as e:
        print(f"page-intake ERROR {e}")
        return 2
    if ns.json:
        print(json.dumps(it, indent=2, ensure_ascii=False))
    else:
        print("intake for " + ("/" + it["route"] + "/" if it["route"] else "/"))
        for k, v in rows(it):
            print(f"  {k:<34} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
