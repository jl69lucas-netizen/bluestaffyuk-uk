#!/usr/bin/env python3
"""Read the named image styles and the image-slot fields out of IMAGE-DESIGNS.md.

IMAGE-DESIGNS.md is the one place the OG framing styles (§7), the infographic styles (§8)
and the slot field values (§10) are written for a reader. A second, hand-typed copy of those
ids would drift from the document the breeder reads, so this module parses them from it:

    load()     -> {"og_styles", "og_names", "og_uses", "infographic_styles",
                   "infographic_names", "infographic_uses", "fields"}
    labels()   -> the board's label map, the shape of data/design/image-styles.json

The build gate's own constants (`OG_STYLES`, `IG_STYLES` in scripts/image_rules.py) are
pinned to these ids by tests/py/test_image_designs.py.

Usage:
  python3 scripts/image_designs.py            # print what it read
  python3 scripts/image_designs.py --write    # rewrite data/design/image-styles.json
  python3 scripts/image_designs.py --check    # exit 1 when that file is stale
"""
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


def _section_lines(text, number):
    """Lines of `## <number>.` up to the next `## ` heading (### subsections included)."""
    out, inside = [], False
    for line in text.splitlines():
        m = SECTION.match(line)
        if m:
            inside = m.group(1) == str(number)
            continue
        if inside and line.startswith("## "):
            break
        if inside:
            out.append(line)
    return out


def _id_rows(lines):
    """[(id, [cells...])] for every table row whose first cell is a backticked id."""
    rows = []
    for line in lines:
        m = ID_CELL.match(line)
        if m:
            rows.append((m.group(1), [c.strip() for c in line.strip().strip("|").split("|")]))
    return rows


def load(path=DOC):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    og = _id_rows(_section_lines(text, 7))           # Id | Name | Engine | When to use | Whole dog?
    ig = _id_rows(_section_lines(text, 8))           # Id | Name | Layout | Palette | Heading intents | Page types
    fields = {i: TICKED.findall(c[1]) for i, c in _id_rows(_section_lines(text, 10))}
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
    if "--write" in argv:
        LABELS.write_text(render_labels(), encoding="utf-8")
        print("wrote %s" % LABELS.relative_to(ROOT))
        return 0
    if "--check" in argv:
        stale = not LABELS.exists() or LABELS.read_text(encoding="utf-8") != render_labels()
        print("%s: %s" % (LABELS.relative_to(ROOT), "STALE — run --write" if stale else "in sync"))
        return 1 if stale else 0
    json.dump(load(), sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
