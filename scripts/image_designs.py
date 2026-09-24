#!/usr/bin/env python3
"""Read the named image styles and the image-slot fields out of IMAGE-DESIGNS.md.

IMAGE-DESIGNS.md is the one place the OG framing styles (§7), the infographic styles (§8)
and the slot field values (§10) are written for a reader. A second, hand-typed copy of those
ids would drift from the document the breeder reads, so this module parses them from it:

    load()     -> {"og_styles", "og_names", "og_uses", "infographic_styles",
                   "infographic_names", "infographic_uses", "fields"}
    labels()   -> the board's label map, the shape of data/design/image-styles.json

The document's row order IS the board's display order: the style lists, the label map and
the field values keep the order the rows are written in, and the tests assert that order.

A broken document is an error, never a quietly shorter list: `load()` raises ValueError,
naming the document and the problem, for a missing required heading, an empty §7/§8/§10
table, a duplicate id, or a style row with too few cells.

The build gate's own constants (`OG_STYLES`, `IG_STYLES` in scripts/image_rules.py) are
pinned to these ids by tests/py/test_image_designs.py.

Usage:
  python3 scripts/image_designs.py            # print what it read
  python3 scripts/image_designs.py --write    # rewrite data/design/image-styles.json
  python3 scripts/image_designs.py --check    # exit 1 when that file is stale
Exit 2 on a bad flag or a broken IMAGE-DESIGNS.md.
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "IMAGE-DESIGNS.md"
LABELS = ROOT / "data/design/image-styles.json"

REQUIRED_SECTIONS = (
    "## 0. Brand Facts",
    "## 1. Crop & Aspect Ratios (per slot)",
    "### 1a. Uniform In-Body Image Sizing",
    "## 2. Reusable Style Wrapper",
    "## 3. Negative List",
    "## 4. Lighting & Focal Length (per scene)",
    "## 5. Scene Types by Page Type (routing table)",
    "## 6. Output Handoff",
    "## 7. Named OG Framing Styles",
    "## 8. Named Infographic Styles",
    "## 9. Approval Before the Build",
    "## 10. Image-Slot Fields",
)

SECTION = re.compile(r"^##\s+(\d+)\.")
ID_CELL = re.compile(r"^\|\s*`([^`]+)`\s*\|")
TICKED = re.compile(r"`([^`]+)`")

# Minimum cells per style row: §7 Id | Name | Engine | When to use | Whole dog?
# and §8 Id | Name | Layout | Palette | Heading intents | Page types.
MIN_CELLS = {7: 5, 8: 6}


def _section_lines(text, number):
    """Lines of the FIRST `## <number>.` section, up to the next `## ` heading (### subsections
    included). A later heading with the same number (an appendix) never reopens it."""
    out, inside = [], False
    for line in text.splitlines():
        if inside and line.startswith("## "):
            break
        m = SECTION.match(line)
        if m and m.group(1) == str(number):
            inside = True
            continue
        if inside:
            out.append(line)
    return out


def _first_table(lines):
    """The lines of the first markdown table in `lines` (header and separator included)."""
    out = []
    for line in lines:
        if line.startswith("|"):
            out.append(line)
        elif out:
            break
    return out


def _id_rows(lines, where, doc, min_cells=0):
    """[(id, [cells...])] for every table row whose first cell is a backticked id.

    Raises ValueError for no such rows, a duplicate id, or a row shorter than `min_cells`."""
    rows = []
    for line in lines:
        m = ID_CELL.match(line)
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < min_cells:
                raise ValueError("%s: %s row `%s` has %d cells, needs %d cells"
                                 % (doc, where, m.group(1), len(cells), min_cells))
            rows.append((m.group(1), cells))
    if not rows:
        raise ValueError("%s: %s has no style rows" % (doc, where))
    seen = set()
    for i, _ in rows:
        if i in seen:
            raise ValueError("%s: %s has a duplicate id `%s`" % (doc, where, i))
        seen.add(i)
    return rows


def load(path=None):
    path = pathlib.Path(path or DOC)
    text = path.read_text(encoding="utf-8")
    doc = path.name
    lines = set(text.splitlines())
    missing = [h for h in REQUIRED_SECTIONS if h not in lines]
    if missing:
        raise ValueError("%s: missing required section(s): %s" % (doc, "; ".join(missing)))
    og = _id_rows(_section_lines(text, 7), "§7", doc, MIN_CELLS[7])
    ig = _id_rows(_section_lines(text, 8), "§8", doc, MIN_CELLS[8])
    # §10 carries two tables: the slot fields, then the pick grammar. Only the first is fields.
    field_rows = _id_rows(_first_table(_section_lines(text, 10)), "§10", doc, 2)
    fields = {i: TICKED.findall(c[1]) for i, c in field_rows}
    return {
        "og_styles": [i for i, _ in og],
        "og_names": {i: c[1] for i, c in og},
        "og_uses": {i: c[3] for i, c in og},
        "infographic_styles": [i for i, _ in ig],
        "infographic_names": {i: c[1] for i, c in ig},
        "infographic_uses": {i: "%s (%s)" % (c[4], c[5]) for i, c in ig},
        "fields": fields,
    }


def labels(spec=None):
    """{"og": {id: {"name", "use"}}, "infographic": {id: {"name", "use"}}} for the board."""
    spec = spec or load()
    return {
        "og": {i: {"name": spec["og_names"][i], "use": spec["og_uses"][i]}
               for i in spec["og_styles"]},
        "infographic": {i: {"name": spec["infographic_names"][i],
                            "use": spec["infographic_uses"][i]}
                        for i in spec["infographic_styles"]},
    }


def render_labels(spec=None):
    return json.dumps(labels(spec), indent=2, ensure_ascii=False) + "\n"


def main(argv):
    ap = argparse.ArgumentParser(description="Read the image style ids out of IMAGE-DESIGNS.md.")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true",
                      help="rewrite data/design/image-styles.json")
    mode.add_argument("--check", action="store_true",
                      help="exit 1 when data/design/image-styles.json is stale")
    args = ap.parse_args(argv)
    try:
        spec = load()
    except ValueError as e:
        print("image_designs: %s" % e, file=sys.stderr)
        return 2
    if args.write:
        LABELS.write_text(render_labels(spec), encoding="utf-8")
        print("wrote %s" % LABELS.relative_to(ROOT))
        return 0
    if args.check:
        stale = not LABELS.exists() or LABELS.read_text(encoding="utf-8") != render_labels(spec)
        print("%s: %s" % (LABELS.relative_to(ROOT), "STALE — run --write" if stale else "in sync"))
        return 1 if stale else 0
    json.dump(spec, sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
