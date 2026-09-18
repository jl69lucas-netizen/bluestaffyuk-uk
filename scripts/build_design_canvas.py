#!/usr/bin/env python3
"""build_design_canvas.py — dist/design-canvas/index.html → Design-type artboards.

Reads the built canvas route, writes one `.dc.html` per [data-component][data-variant]
section plus `canvas.json`, into docs/artifacts/canvas/project/. The controller then
publishes with the Artifact tool (url = the canvas, root = docs/artifacts/canvas,
file_path = project/canvas.json, files = every artboard). Images are uploaded once by the
controller; their /_blob/ urls are kept in data/design/canvas-assets.json and reused.

Astro inlines the built CSS, so there is no dist/_astro/*.css to read: the stylesheet for an
artboard is every <style> block of the built route, pasted in document order so the @layer
cascade survives.

Spec §11 amendment 3d: every PICKED variant also gets a 375 and a 768 artboard
(`<component>-<v>-m375.dc.html`, `-t768.dc.html`), laid out as two extra rows at the bottom
of the canvas, so the mobile and tablet renderings are judged rather than assumed. Only the
picks: 130 more boards for the losing variants is a canvas nobody can read.

Usage: python3 scripts/build_design_canvas.py [--dist dist] [--out docs/artifacts/canvas]
       [--heights data/design/canvas-heights.json]
Heights come from scripts/measure_canvas_heights.mjs (Playwright) — run it first.
"""
import argparse, dataclasses, html as H, json, pathlib, re, sys, datetime as dt
ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS_LINK = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
              'family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Source+Sans+3:wght@400;600&display=swap">')
SEC = re.compile(r'<section([^>]*)data-component="([a-z-]+)"([^>]*)data-variant="([a-e])"([^>]*)>(.*?)</section>', re.S)
WIDTH = re.compile(r'data-width="(\d+)"')
IMG_SRC = re.compile(r'(src|srcset)="([^"]+)"')
STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
SCRIPT = re.compile(r"<script\b[^>]*>.*?</script>", re.S)


@dataclasses.dataclass
class Section:
    component: str
    variant: str
    width: int
    inner: str


def find_sections(html):
    """Every artboard section, with its behaviour stripped out.

    A component's own `<script>` — SiteHeaderKit's search pill is the first — is hoisted into
    the section by the build and points at a `/_astro/*.js` bundle. An artboard is a static
    rendering for the eye, served from the canvas where that bundle does not exist and where
    `/search-index.json` does not either, so the tag would be a 404 and nothing more. It is
    dropped here, once, so neither the artboard nor the missing-asset scan ever sees it."""
    out = []
    for m in SEC.finditer(html):
        attrs = m.group(1) + m.group(3) + m.group(5)
        w = WIDTH.search(attrs)
        out.append(Section(m.group(2), m.group(4), int(w.group(1)) if w else 1280,
                           SCRIPT.sub("", m.group(6)).strip()))
    return out


def page_css(html):
    """Every inlined <style> block of the built page, in document order (@layer order matters)."""
    return "\n".join(m.group(1).strip() for m in STYLE.finditer(html))


def rewrite_assets(inner, assets):
    def sub(m):
        attr, val = m.group(1), m.group(2)
        if attr == "srcset":
            parts = []
            for cand in val.split(","):
                url, _, desc = cand.strip().partition(" ")
                parts.append((assets.get(url, url) + (" " + desc if desc else "")))
            return f'srcset="{", ".join(parts)}"'
        return f'{attr}="{assets.get(val, val)}"'
    return IMG_SRC.sub(sub, inner)


def artboard(sec, css, fonts_link, height, assets, width=None):
    """One artboard. `width` overrides the section's own board width, which is how the same
    built section becomes a 375 and a 768 board as well as its 640/1280 one."""
    width = sec.width if width is None else width
    inner = rewrite_assets(sec.inner, assets)
    inner = re.sub(r"<h3[^>]*>.*?</h3>\s*", "", inner, count=1, flags=re.S)   # the route's caption
    title = f"{sec.component} — variant {sec.variant}"
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


#: the two extra rows, as (suffix, board width, row title). Spec §11 amendment 3d.
RESPONSIVE_ROWS = (("m375", 375, "14 · Picked — mobile 375"),
                   ("t768", 768, "15 · Picked — tablet 768"))
GAP = 80


def canvas_index(title, rows, boards, existing, picked=()):
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    idx = existing or {"v": 3, "createdOnFiles": {"v": 1, "at": now}, "title": title, "launch": {"view": "canvas"},
                       "pages": [], "boards": {}, "order": [], "notes": {}, "designSystems": []}
    idx["title"] = title
    idx["boards"], idx["order"] = {}, []
    idx["notes"] = {k: v for k, v in idx.get("notes", {}).items() if v.get("kind") != "title1"}
    y = 0
    heights = {(c, v): h for c, v, h in boards}
    for row in rows:
        w = row["board_width"]
        row_h = max(heights.get((row["id"], v), 200) for v in "abcde")
        idx["notes"][f"row-{row['id']}"] = {"x": 0, "y": y - 240, "text": row["title"], "kind": "title1", "maxW": 5 * w + 4 * GAP}
        for i, v in enumerate("abcde"):
            f = f"{row['id']}-{v}.dc.html"
            idx["boards"][f] = {"x": i * (w + GAP), "y": y, "w": w, "h": heights.get((row["id"], v), 200), "title": f"{row['title']} · {v}"}
            if row["id"] == "faq":
                idx["boards"][f]["is_interactive"] = True
            idx["order"].append(f)
        y += row_h + 120 + 240

    # Rows 14 and 15: the picked variant of every component, at phone and tablet width. One
    # board per component, in components.json order, so a reader scanning left to right sees
    # the page they are about to build in the order it stacks.
    picked_h = {(c, v, s): h for c, v, s, h in picked}
    by_id = {r["id"]: r for r in rows}
    for suffix, w, row_title in RESPONSIVE_ROWS:
        in_row = [(c, v) for (c, v, s) in {(c, v, s) for c, v, s, _ in picked} if s == suffix]
        if not in_row:
            continue
        order = [r["id"] for r in rows]
        in_row.sort(key=lambda cv: order.index(cv[0]) if cv[0] in order else len(order))
        row_h = max(picked_h[(c, v, suffix)] for c, v in in_row)
        idx["notes"][f"row-picked-{suffix}"] = {
            "x": 0, "y": y - 240, "text": row_title, "kind": "title1",
            "maxW": len(in_row) * w + (len(in_row) - 1) * GAP}
        for i, (c, v) in enumerate(in_row):
            f = f"{c}-{v}-{suffix}.dc.html"
            idx["boards"][f] = {"x": i * (w + GAP), "y": y, "w": w,
                                "h": picked_h[(c, v, suffix)],
                                "title": f"{by_id.get(c, {}).get('title', c)} · {v} · {w}"}
            if c == "faq":
                idx["boards"][f]["is_interactive"] = True
            idx["order"].append(f)
        y += row_h + 120 + 240
    return idx


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default=str(ROOT / "dist/design-canvas/index.html"))
    ap.add_argument("--out", default=str(ROOT / "docs/artifacts/canvas"))
    ap.add_argument("--heights", default=str(ROOT / "data/design/canvas-heights.json"))
    a = ap.parse_args(argv)
    html = pathlib.Path(a.dist).read_text()
    rows = json.loads((ROOT / "data/design/components.json").read_text())
    assets = json.loads((ROOT / "data/design/canvas-assets.json").read_text())
    # The mark has no artboard at any width, so picks["mark"] is not read here.
    picks = json.loads((ROOT / "data/design/picks.json").read_text())["picks"]
    PICKED = {(cid, p["variant"]) for cid, p in picks.items()}
    heights = json.loads(pathlib.Path(a.heights).read_text()) if pathlib.Path(a.heights).exists() else {}
    css = page_css(html)
    out = pathlib.Path(a.out) / "project"
    out.mkdir(parents=True, exist_ok=True)
    boards = []
    picked_boards = []
    missing = set()
    sizes = []
    for sec in find_sections(html):
        if sec.variant not in "abcde" or sec.component == "mark":
            continue
        for m in IMG_SRC.finditer(sec.inner):
            for cand in m.group(2).split(","):
                url = cand.strip().split(" ")[0]
                if url.startswith("/_astro/") and url not in assets:
                    missing.add(url)
        h = heights.get(f"{sec.component}-{sec.variant}", 200)
        path = out / f"{sec.component}-{sec.variant}.dc.html"
        path.write_text(artboard(sec, css, FONTS_LINK, h, assets))
        sizes.append(path.stat().st_size)
        boards.append((sec.component, sec.variant, h))
        if (sec.component, sec.variant) in PICKED:
            for suffix, w, _ in RESPONSIVE_ROWS:
                rh = heights.get(f"{sec.component}-{sec.variant}-{suffix}", 200)
                rpath = out / f"{sec.component}-{sec.variant}-{suffix}.dc.html"
                rpath.write_text(artboard(sec, css, FONTS_LINK, rh, assets, width=w))
                sizes.append(rpath.stat().st_size)
                picked_boards.append((sec.component, sec.variant, suffix, rh))
    idx_path = out / "canvas.json"
    existing = json.loads(idx_path.read_text()) if idx_path.exists() else None
    idx_path.write_text(json.dumps(
        canvas_index("BlueStaffyUK Design Canvas", rows, boards, existing, picked_boards), indent=1))
    print(f"wrote {len(boards) + len(picked_boards)} artboards + canvas.json to {out} "
          f"({len(boards)} variant boards, {len(picked_boards)} picked mobile/tablet boards)")
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
