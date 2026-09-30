#!/usr/bin/env python3
"""build_favicons.py — public/brand/logo-icon.svg → favicon.svg, favicon-32.png,
apple-touch-icon.png (180) and icon-512.png. Idempotent; re-run after build_lockups.py.

icon-512.png is not only a favicon: it is also the raster the JSON-LD `image` and the
default `og:image` point at, because neither Google's structured-data pipeline nor a social
card renderer will take an SVG.

RASTERISER. cairosvg is what the plan named and what this prefers, but it is a binding to
the system libcairo, which is not present on a stock macOS without Homebrew. resvg-py ships
a self-contained wheel with the renderer compiled in, so it is tried second and is what the
committed renders were actually produced with. Both rasterise this file identically — the
icon is flat fills, arcs and cubics with no text, no filters and no gradients.
"""
from __future__ import annotations

import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "public/brand/logo-icon.svg"
SIZES = (("favicon-32.png", 32), ("apple-touch-icon.png", 180), ("icon-512.png", 512))


def rasteriser():
    try:
        import cairosvg  # noqa: PLC0415
        return lambda svg, px: cairosvg.svg2png(bytestring=svg, output_width=px,
                                                output_height=px)
    except (ImportError, OSError):
        pass
    try:
        import resvg_py  # noqa: PLC0415
        return lambda svg, px: bytes(resvg_py.svg_to_bytes(svg_string=svg.decode("utf-8"),
                                                           width=px, height=px))
    except ImportError:
        print("no rasteriser: pip3 install cairosvg (needs libcairo) or resvg-py",
              file=sys.stderr)
        raise SystemExit(2)


def main() -> int:
    if not SRC.exists():
        print(f"missing {SRC.relative_to(ROOT)} — run scripts/build_lockups.py first",
              file=sys.stderr)
        return 2
    svg = SRC.read_bytes()
    render = rasteriser()
    shutil.copyfile(SRC, ROOT / "public/favicon.svg")
    print("wrote public/favicon.svg")
    for name, px in SIZES:
        out = ROOT / "public" / name
        out.write_bytes(render(svg, px))
        print(f"wrote public/{name} ({out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
