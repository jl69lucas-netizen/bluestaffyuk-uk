#!/usr/bin/env python3
"""The must-differ inventory for a city component pass (London first).

For each of the fifteen city components (scripts/city_components.py): every arrangement the
site already offers for it — the S1–S3 styles and, for the hero and the counter strip, the
eighteen per-page styles in src/lib/boardStyles.ts — with the built pages that wear each one
(the pick IN FORCE, `pageboard.pick_in_force`, over every record in data/facts/rebuilt.json)
and its structural axes on the canvas's four canonical axes. A new canvas variant must differ
from every row of its component on at least two axes (scripts/check_city_canvas.py).

Writes two files from one computation, so they cannot disagree:
  data/design/city-must-differ.json                 — what the validator and the gate read
  docs/research/london-components/must-differ.md    — what a designer reads

    python3 scripts/city_must_differ.py           # write both
    python3 scripts/city_must_differ.py --check   # exit 1 if either is stale
"""
import argparse
import ast
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pageboard as PB  # noqa: E402
from city_components import COMPONENTS, KIT_ONLY  # noqa: E402

ROOT = PB.ROOT
TS = ROOT / "src" / "lib" / "boardStyles.ts"
OUT_JSON = ROOT / "data" / "design" / "city-must-differ.json"
OUT_MD = ROOT / "docs" / "research" / "london-components" / "must-differ.md"

_HEAD = re.compile(r"^  '?([a-z-]+)'?:\s*\[\s*$", re.M)
_DEF = re.compile(r"def\('([^']+)',\s*'([^']*)',\s*(\{.*?\})\)", re.S)

#: The neutral value of every Layout axis a renderer defaults, as the components default them
#: (Hero `split`, CounterStrip `inline`, Testimonial `single`; boxClass() NEUTRAL for the rest).
DEFAULTS = {"hero": "split", "tiles": "inline", "mode": "single", "list": "stack",
            "columns": 1, "aside": "none", "chrome": "ruled", "play": "iframe",
            "media": "none", "frame": "plain"}


def _get(layout, key):
    return layout.get(key, DEFAULTS.get(key))


def layout_slug(shape, layout):
    """The canonical `layout` axis of one boardStyles def: the arrangement, named the way a
    canvas variant names its own."""
    if shape == "hero":
        return _get(layout, "hero")
    if shape == "stats":
        return _get(layout, "tiles")
    if shape in ("takeaways", "puppies"):
        return _get(layout, "list")
    if shape == "reviews":
        return _get(layout, "mode")
    if shape == "table":
        return _get(layout, "chrome")
    if shape == "video":
        return _get(layout, "play")
    if shape == "dial":
        return f"ring-{layout.get('ring')}+{layout.get('marks')}+{layout.get('list')}"
    if shape == "strip":
        return layout.get("chip")
    if shape == "sheet":
        return layout.get("launcher")
    aside = _get(layout, "aside")
    return f"cols-{_get(layout, 'columns')}" + ("" if aside == "none" else f"+{aside}")


def canonical_axes(shape, layout):
    return {"layout": layout_slug(shape, layout), "media": _get(layout, "media"),
            "density": None, "framing": _get(layout, "frame")}


def _parse_block(src, const_name):
    """{group: [(id, name, layout dict)]} for one `export const <name> … = { … };` map."""
    body = src.split("export const " + const_name, 1)[1].split("\n};", 1)[0]
    parts = _HEAD.split(body)[1:]
    out = {}
    for i in range(0, len(parts), 2):
        rows = []
        for m in _DEF.finditer(parts[i + 1]):
            obj = re.sub(r"(\w+):", r"'\1':", " ".join(m.group(3).split()))
            rows.append((m.group(1), m.group(2), ast.literal_eval(obj)))
        out[parts[i]] = rows
    return out


def style_defs(ts_path=TS):
    """{shape: [(id, name, layout)]} — the shape-wide trios plus, under `hero` and `stats`,
    the per-page sets of every layout family, in the file's own order."""
    src = pathlib.Path(ts_path).read_text(encoding="utf-8")
    trios = _parse_block(src, "STYLES:")
    defs = {shape: list(rows) for shape, rows in trios.items()}
    for const, shape in (("HERO_STYLES_BY_PAGE_TYPE", "hero"),
                         ("COUNTER_STYLES_BY_PAGE_TYPE", "stats")):
        for rows in _parse_block(src, const).values():
            defs[shape].extend(rows)
    return defs


def worn_by(boards, slugs):
    """{(shape, style id): [slug]} — the pick in force of every section of every built page."""
    out = {}
    for slug in sorted(slugs):
        b = boards.get(slug)
        if not b:
            continue
        for sec in b.get("sections", []):
            pick = PB.pick_in_force(b, sec.get("id"))
            if pick:
                out.setdefault((sec.get("shape"), pick), []).append(slug)
    return out


def inventory(ts_path=TS, boards=None, slugs=None):
    """{component id: [row]} in city-page order. A row is {shape, id, name, axes, used_by}."""
    defs = style_defs(ts_path)
    boards = PB.load_all_boards() if boards is None else boards
    slugs = PB.rebuilt_slugs() if slugs is None else slugs
    worn = worn_by(boards, slugs)
    out = {}
    for cid, _name, shapes in COMPONENTS:
        rows = [dict(r, shape="kit") for r in KIT_ONLY.get(cid, [])]
        for shape in shapes:
            for sid, name, layout in defs.get(shape, []):
                rows.append({"shape": shape, "id": sid, "name": name,
                             "axes": canonical_axes(shape, layout),
                             "used_by": sorted(set(worn.get((shape, sid), [])))})
        out[cid] = rows
    return out


def render_json(inv):
    doc = {"_comment": "Generated by scripts/city_must_differ.py — do not hand-edit. Every "
                       "arrangement the site already offers per city component, with the "
                       "built pages wearing it; a canvas variant differs from each row on at "
                       "least two of layout/media/density/framing (a null never counts).",
           "components": inv}
    return json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def render_md(inv):
    names = {c[0]: c[1] for c in COMPONENTS}
    lines = ["# Must Differ — the London Component Design Pass", "",
             "Generated by `scripts/city_must_differ.py` from `src/lib/boardStyles.ts` and the "
             "approved picks in `data/boards/` (the pick in force on each built page). Do not "
             "hand-edit; re-run the script. The machine-readable copy is "
             "`data/design/city-must-differ.json`.", "",
             "Every London variant differs from **every row of its component** on at least two "
             "of the four axes (layout, media, density, framing), and from its two siblings. A "
             "colour change never counts. A dash is an axis the style does not state, which "
             "never counts as a difference.", ""]
    for cid, rows in inv.items():
        lines += [f"## {cid} — {names[cid]}", ""]
        if not rows:
            lines += ["No existing arrangement: the kit has no such component. A variant "
                      "differs from its two siblings only.", ""]
            continue
        lines += ["| Style | Shape | What it renders | layout | media | framing | Worn by |",
                  "|---|---|---|---|---|---|---|"]
        for r in rows:
            a = r["axes"]
            worn = ", ".join(r["used_by"]) or "—"
            lines.append(f"| `{r['id']}` | {r['shape']} | {r['name']} | {a['layout'] or '—'} | "
                         f"{a['media'] or '—'} | {a['framing'] or '—'} | {worn} |")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if either output is stale")
    a = ap.parse_args(argv)
    inv = inventory()
    want = {OUT_JSON: render_json(inv), OUT_MD: render_md(inv)}
    rows = sum(len(v) for v in inv.values())
    if a.check:
        stale = [p for p, text in want.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != text]
        for p in stale:
            print(f"STALE {p.relative_to(ROOT)} — run python3 scripts/city_must_differ.py")
        print(f"city-must-differ: {len(inv)} components, {rows} rows examined; "
              f"{len(stale)} stale")
        return 1 if stale else 0
    for p, text in want.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        print(f"wrote {p.relative_to(ROOT)}")
    print(f"city-must-differ: {len(inv)} components, {rows} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
