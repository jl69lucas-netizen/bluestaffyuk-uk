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


@dataclasses.dataclass
class Section:
    component: str
    variant: str
    width: int
    inner: str


def find_sections(html):
    out = []
    for m in SEC.finditer(html):
        attrs = m.group(1) + m.group(3) + m.group(5)
        w = WIDTH.search(attrs)
        out.append(Section(m.group(2), m.group(4), int(w.group(1)) if w else 1280, m.group(6).strip()))
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


def artboard(sec, css, fonts_link, height, assets):
    inner = rewrite_assets(sec.inner, assets)
    inner = re.sub(r"<h3[^>]*>.*?</h3>\s*", "", inner, count=1, flags=re.S)   # the route's caption
    title = f"{sec.component} — variant {sec.variant}"
    props = json.dumps({"$preview": {"width": sec.width, "height": height}}, separators=(",", ":"))
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{H.escape(title)}</title>\n<script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n"
        f"{fonts_link}\n<style>\nbody{{margin:0;font-family:'Source Sans 3',system-ui,sans-serif;background:#F4F1EA}}\n"
        f"a{{color:#1F3A52}}a:hover{{color:#14202B}}\n{css}\n</style>\n</helmet>\n"
        f"<div style=\"width: {sec.width}px; height: {height}px; box-sizing: border-box; overflow: hidden; display: flex; flex-direction: column;\">\n"
        f"{inner}\n</div>\n</x-dc>\n"
        f"<script type=\"text/x-dc\" data-dc-script data-props='{props}'>\n"
        "class Component extends DCLogic {\n  renderVals() { return {}; }\n}\n</script>\n</body>\n</html>\n"
    )


def canvas_index(title, rows, boards, existing):
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
        idx["notes"][f"row-{row['id']}"] = {"x": 0, "y": y - 240, "text": row["title"], "kind": "title1", "maxW": 5 * w + 4 * 80}
        for i, v in enumerate("abcde"):
            f = f"{row['id']}-{v}.dc.html"
            idx["boards"][f] = {"x": i * (w + 80), "y": y, "w": w, "h": heights.get((row["id"], v), 200), "title": f"{row['title']} · {v}"}
            if row["id"] == "faq":
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
    heights = json.loads(pathlib.Path(a.heights).read_text()) if pathlib.Path(a.heights).exists() else {}
    css = page_css(html)
    out = pathlib.Path(a.out) / "project"
    out.mkdir(parents=True, exist_ok=True)
    boards = []
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
    idx_path = out / "canvas.json"
    existing = json.loads(idx_path.read_text()) if idx_path.exists() else None
    idx_path.write_text(json.dumps(canvas_index("BlueStaffyUK Design Canvas", rows, boards, existing), indent=1))
    print(f"wrote {len(boards)} artboards + canvas.json to {out}")
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
