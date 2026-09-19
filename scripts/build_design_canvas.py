#!/usr/bin/env python3
"""build_design_canvas.py — dist/kit-preview/index.html → Design-type artboards.

Reads the built preview route, writes one `.dc.html` per [data-component] section plus
`canvas.json`, into docs/artifacts/canvas/project/. The controller then publishes with the
Artifact tool (url = the canvas, root = docs/artifacts/canvas, file_path =
project/canvas.json, files = every artboard). Images are uploaded once by the controller;
their /_blob/ urls are kept in data/design/canvas-assets.json and reused.

Astro inlines the built CSS, so there is no dist/_astro/*.css to read: the stylesheet for an
artboard is every <style> block of the built route, pasted in document order so the @layer
cascade survives. Reading the route -- the sections, that stylesheet and the asset rewriting --
moved to scripts/_kit_sections.py in Task 22, so the Design System builder cuts the same
sections from the same markup rather than keeping a second copy of these regexes.

THIRTY-NINE BOARDS, NOT SIXTY-FIVE. Task 19 pruned the kit to the picks and deleted the
canvas route, so there is no variant letter left to put on a board: each of the thirteen
components is cut once at its own board width (1280 or 640, from components.json) and again
at 375 and at 768 (spec §11 amendment 3d, so the phone and tablet renderings are judged
rather than assumed). The three rows are `<component>.dc.html`, `<component>-m375.dc.html`
and `<component>-t768.dc.html`.

Usage: python3 scripts/build_design_canvas.py [--dist dist/kit-preview/index.html]
       [--out docs/artifacts/canvas] [--heights data/design/canvas-heights.json]
Heights come from scripts/measure_canvas_heights.mjs (Playwright) — run it first.
"""
import argparse, html as H, json, pathlib, re, sys, datetime as dt

from _kit_sections import (FONTS_LINK, IMG_SRC, SEC, SCRIPT, STYLE, WIDTH, Section,
                           find_sections, page_css, rewrite_assets)

ROOT = pathlib.Path(__file__).resolve().parent.parent

def artboard(sec, css, fonts_link, height, assets, width=None):
    """One artboard. `width` overrides the section's own board width, which is how the same
    built section becomes a 375 and a 768 board as well as its 640/1280 one."""
    width = sec.width if width is None else width
    inner = rewrite_assets(sec.inner, assets)
    inner = re.sub(r"<h3[^>]*>.*?</h3>\s*", "", inner, count=1, flags=re.S)   # the route's caption
    title = f"{sec.component} — {width}"
    props = json.dumps({"$preview": {"width": width, "height": height}}, separators=(",", ":"))
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{H.escape(title)}</title>\n<script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n"
        f"{fonts_link}\n<style>\nbody{{margin:0;font-family:'Source Sans 3',system-ui,sans-serif;background:#F4F1EA}}\n"
        f"a{{color:#1F3A52}}a:hover{{color:#14202B}}\n{css}\n</style>\n</helmet>\n"
        f"<div style=\"width: {width}px; height: {height}px; box-sizing: border-box; overflow: hidden; display: flex; flex-direction: column;\">\n"
        f"{inner}\n</div>\n</x-dc>\n"
        f"<script type=\"text/x-dc\" data-dc-script data-props='{props}'>\n"
        "class Component extends DCLogic {\n  renderVals() { return {}; }\n}\n</script>\n</body>\n</html>\n"
    )


#: The three rows, as (suffix, board width or None for the component's own, row title).
#: Row 1 cuts each component at its components.json width; rows 2 and 3 are spec §11
#: amendment 3d's phone and tablet passes over the same built section.
BOARD_ROWS = (("", None, "1 · The kit"),
              ("m375", 375, "2 · The kit — mobile 375"),
              ("t768", 768, "3 · The kit — tablet 768"))
GAP = 80


def board_name(cid, suffix):
    """`hero.dc.html` on row 1, `hero-m375.dc.html` on the responsive rows."""
    return f"{cid}-{suffix}.dc.html" if suffix else f"{cid}.dc.html"


def height_key(cid, suffix):
    """The key scripts/measure_canvas_heights.mjs writes for that board."""
    return f"{cid}-{suffix}" if suffix else cid


def canvas_index(title, rows, heights, existing=None):
    """The canvas index: three rows of one board per component, in components.json order.

    `heights` is the measured map (component -> px, component-m375 -> px, ...). A component
    with no measurement falls back to 200 rather than failing the build: a board of the
    wrong height is visible and fixable, a build that refuses to write is not."""
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    idx = existing or {"v": 3, "createdOnFiles": {"v": 1, "at": now}, "title": title, "launch": {"view": "canvas"},
                       "pages": [], "boards": {}, "order": [], "notes": {}, "designSystems": []}
    idx["title"] = title
    idx["boards"], idx["order"] = {}, []
    idx["notes"] = {k: v for k, v in idx.get("notes", {}).items() if v.get("kind") != "title1"}
    y = 0
    for suffix, row_w, row_title in BOARD_ROWS:
        x = 0
        row_h = 200
        for row in rows:
            w = row_w or row["board_width"]
            h = heights.get(height_key(row["id"], suffix), 200)
            f = board_name(row["id"], suffix)
            idx["boards"][f] = {"x": x, "y": y, "w": w, "h": h,
                                "title": f"{row['title']} · {w}"}
            # The FAQ is the one component whose whole point is a control that opens.
            if row["id"] == "faq":
                idx["boards"][f]["is_interactive"] = True
            idx["order"].append(f)
            x += w + GAP
            row_h = max(row_h, h)
        idx["notes"][f"row-{suffix or 'kit'}"] = {
            "x": 0, "y": y - 240, "text": row_title, "kind": "title1", "maxW": max(x - GAP, 0)}
        y += row_h + 120 + 240
    return idx


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default=str(ROOT / "dist/kit-preview/index.html"))
    ap.add_argument("--out", default=str(ROOT / "docs/artifacts/canvas"))
    ap.add_argument("--heights", default=str(ROOT / "data/design/canvas-heights.json"))
    a = ap.parse_args(argv)
    html = pathlib.Path(a.dist).read_text()
    rows = json.loads((ROOT / "data/design/components.json").read_text())
    assets = json.loads((ROOT / "data/design/canvas-assets.json").read_text())
    heights = json.loads(pathlib.Path(a.heights).read_text()) if pathlib.Path(a.heights).exists() else {}
    css = page_css(html)
    out = pathlib.Path(a.out) / "project"
    out.mkdir(parents=True, exist_ok=True)
    written = 0
    missing = set()
    sizes = []
    for sec in find_sections(html):
        # The mark has no artboard at any width: it is shown on the preview page on both
        # surfaces it has to work on, and it is not a components.json row.
        if sec.component == "mark":
            continue
        for m in IMG_SRC.finditer(sec.inner):
            for cand in m.group(2).split(","):
                url = cand.strip().split(" ")[0]
                if url.startswith("/_astro/") and url not in assets:
                    missing.add(url)
        for suffix, row_w, _ in BOARD_ROWS:
            h = heights.get(height_key(sec.component, suffix), 200)
            path = out / board_name(sec.component, suffix)
            path.write_text(artboard(sec, css, FONTS_LINK, h, assets, width=row_w))
            sizes.append(path.stat().st_size)
            written += 1
    idx_path = out / "canvas.json"
    existing = json.loads(idx_path.read_text()) if idx_path.exists() else None
    idx_path.write_text(json.dumps(
        canvas_index("BlueStaffyUK Design Canvas", rows, heights, existing), indent=1))
    print(f"wrote {written} artboards + canvas.json to {out} "
          f"({len(rows)} components x {len(BOARD_ROWS)} widths)")
    if sizes:
        print(f"artboard size: min {min(sizes) // 1024} KB, max {max(sizes) // 1024} KB")
    if missing:
        print("UPLOAD FIRST (then add to data/design/canvas-assets.json):")
        for u in sorted(missing):
            print("  ", u)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
