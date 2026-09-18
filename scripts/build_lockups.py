#!/usr/bin/env python3
"""build_lockups.py — the four brand lockups in public/brand/, generated, never hand-drawn.

WHY A GENERATOR. The mark's geometry has exactly one home, src/components/kit/markShapes.ts
(see its header comment). A lockup file that re-typed those twelve paths would be a
thirteenth copy free to drift away from the one the site actually renders, which is the
failure markShapes.ts exists to prevent. So this script READS that file, pulls the
`markBody` template literal out of it, and substitutes each `var(--color-…)` for the hex
that src/styles/tokens.css resolves it to. Rule 1 ("only tokens.css spells a colour")
governs src/; public/brand/*.svg are standalone SVG *documents* with no stylesheet to
resolve a custom property against, so they must carry literal hexes — and they get them
from tokens.css by resolution here, not by someone retyping #1F3A52 into four files.

THE WORDMARK is outlined, not set in a font: an SVG that names "Fraunces" renders in
Georgia on any machine without it, and a logo that changes shape by machine is not a logo.
fontTools walks the glyphs and emits `<path>` data. Fraunces is variable, so it is
instantiated at wght 700 / opsz 72 first — its default instance is Regular.

FONTS are not vendored (they are OFL, but ~1MB of build-time-only input). Point --fonts at
a directory holding the two Google Fonts files, or set BSUK_FONT_DIR:
    Fraunces[SOFT,WONK,opsz,wght].ttf   (ofl/fraunces)   -> any name matching Fraunces*.ttf
    SourceSans3[wght].ttf               (ofl/sourcesans3) -> any name matching SourceSans3*.ttf

Regenerate with `npm run brand:lockups`, then `npm run brand:favicons`.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS = ROOT / "src/styles/tokens.css"
SHAPES = ROOT / "src/components/kit/markShapes.ts"
OUT = ROOT / "public/brand"

WORDMARK = "BlueStaffyUK"
STRAPLINE = "CARLISLE · CUMBRIA"

# The badge as the site renders it: markBody('var(--color-brand)', 'var(--color-surface)'),
# i.e. the steel roundel with bone outlines. MarkSprite.astro passes exactly this pair.
BADGE_FILL = "var(--color-brand)"
BADGE_OUTLINE = "var(--color-surface)"

# Mono: one ink, three tones, nothing white and no second hue.
#
# The constraint that shapes this map is that paint only ever darkens. A shape drawn at any
# fill-opacity over a filled shape composites to something darker than both, so a mono mark
# cannot have a light blaze inside a darker skull the way the colour mark does. So the two
# fills that exist only to be LIGHTER than what they sit on — the roundel under the head and
# the blaze inside it — drop out entirely, and the tones that remain sit side by side:
# ring, outlines and features at 1, ears at .55, skull at .25.
MONO_OUTLINE = "__outline__"  # the `outline` argument, distinct from the blaze's own token
MONO_TONES = {
    "var(--color-brand)": ("none", None),                 # roundel: no wash under the head
    "var(--color-cta)": ("currentColor", "1"),            # ring, tongue
    "var(--color-brand-tint)": ("currentColor", "0.25"),  # skull
    "var(--color-brand-mid)": ("currentColor", "0.55"),   # ears
    MONO_OUTLINE: ("currentColor", "1"),                  # skull and ear outlines
    "var(--color-surface)": ("none", None),               # blaze: nothing lighter to be
    "var(--color-surface-deep)": ("currentColor", "1"),   # eyes, nose, grin
    "var(--color-surface-raised)": ("none", None),        # catchlights: same reason
}


def token_hexes() -> dict[str, str]:
    """Resolve every `--color-*` in tokens.css to a literal hex, following one alias hop."""
    text = TOKENS.read_text(encoding="utf-8")
    raw = dict(re.findall(r"(--color-[\w-]+)\s*:\s*([^;]+);", text))
    resolved: dict[str, str] = {}

    def resolve(name: str, seen: frozenset[str] = frozenset()) -> str:
        if name in resolved:
            return resolved[name]
        if name in seen:
            raise SystemExit(f"token cycle at {name}")
        value = raw[name].strip()
        alias = re.fullmatch(r"var\((--color-[\w-]+)\)", value)
        out = resolve(alias.group(1), seen | {name}) if alias else value
        if not re.fullmatch(r"#[0-9A-Fa-f]{3,8}", out):
            raise SystemExit(f"{name} is not a colour literal: {out}")
        resolved[name] = out
        return out

    for name in raw:
        resolve(name)
    return resolved


def mark_body(fill: str, outline: str) -> str:
    """The `markBody` template literal from markShapes.ts, with its two arguments applied."""
    text = SHAPES.read_text(encoding="utf-8")
    m = re.search(r"export const markBody = \(badge: string, outline: string\) => `(.*?)`;",
                  text, re.S)
    if not m:
        raise SystemExit("markBody template not found in markShapes.ts — did its shape change?")
    return m.group(1).replace("${badge}", fill).replace("${outline}", outline)


def colourise(body: str, hexes: dict[str, str]) -> str:
    """Every `var(--color-x)` becomes its hex. A leftover var() is a token this file missed."""
    out = re.sub(r"var\((--color-[\w-]+)\)", lambda m: hexes[m.group(1)], body)
    assert "var(" not in out, out
    return out


def monoise(body: str) -> str:
    """Every colour becomes currentColor at one of three tones (or drops out)."""
    def swap(attr: str, value: str) -> str:
        paint, opacity = MONO_TONES[value]
        if opacity is None:
            return f'{attr}="{paint}"'
        return f'{attr}="{paint}" {attr}-opacity="{opacity}"'

    out = re.sub(rf'(fill|stroke)="(var\(--color-[\w-]+\)|{MONO_OUTLINE})"',
                 lambda m: swap(m.group(1), m.group(2)), body)
    assert "var(" not in out, out
    return out


# --- the wordmark ------------------------------------------------------------------------

def load_font(font_dir: pathlib.Path, pattern: str, axes: dict[str, float] | None):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    matches = sorted(font_dir.glob(pattern))
    if not matches:
        raise SystemExit(f"no font matching {pattern} in {font_dir} — see this file's header")
    font = TTFont(matches[0])
    if axes and "fvar" in font:
        font = instancer.instantiateVariableFont(font, axes, inplace=False, updateFontNames=False)
    return font


def outline(font, text: str, size: float, tracking: float = 0.0) -> tuple[str, float]:
    """Glyph outlines as one `<path>` per character, plus the advance the run consumed.

    The y flip is in the per-glyph transform: font units run up from the baseline, SVG user
    units run down, so the glyph is scaled by (s, -s) and translated to its pen position.
    """
    from fontTools.pens.svgPathPen import SVGPathPen

    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    scale = size / upm
    parts: list[str] = []
    pen_x = 0.0
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            raise SystemExit(f"{ch!r} is not in the font")
        # Integer font units: at upm 1000 drawn at 30px that is a 0.03px rounding, invisible
        # at any size the lockup is ever painted, and it cuts the path data by about 60% —
        # the horizontal lockup is inlined into the header of every page on the site.
        pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.0f}")
        glyphs[name].draw(pen)
        d = pen.getCommands()
        if d:
            parts.append(f'<path transform="translate({pen_x:.2f},0) '
                         f'scale({scale:.5f},{-scale:.5f})" d="{d}" />')
        pen_x += glyphs[name].width * scale + tracking
    return "\n      ".join(parts), (pen_x - tracking if text else 0.0)


# --- composition -------------------------------------------------------------------------

WORD_SIZE = 30.0
STRAP_SIZE = 10.0
STRAP_TRACK = 1.7

HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" '
        'height="{h:g}" role="img" aria-labelledby="{tid}">\n'
        '  <title id="{tid}">{title}</title>\n')
TITLE = "BlueStaffyUK — Carlisle, Cumbria"


def badge(body: str, x: float, y: float, size: float) -> str:
    s = size / 100.0
    return (f'  <g transform="translate({x:g},{y:g}) scale({s:.5f})">{body}\n  </g>\n')


def write(name: str, svg: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(svg, encoding="utf-8")
    print(f"wrote public/brand/{name} ({len(svg.encode()):,} bytes)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fonts", default=os.environ.get("BSUK_FONT_DIR", ""),
                    help="directory holding Fraunces*.ttf and SourceSans3*.ttf")
    args = ap.parse_args()
    if not args.fonts:
        print("--fonts (or BSUK_FONT_DIR) is required; see this file's header", file=sys.stderr)
        return 2
    font_dir = pathlib.Path(args.fonts)

    hexes = token_hexes()
    ink = hexes["--color-brand"]
    quiet = hexes["--color-brand-mid"]
    body_colour = colourise(mark_body(BADGE_FILL, BADGE_OUTLINE), hexes)
    body_mono = monoise(mark_body(BADGE_FILL, MONO_OUTLINE))

    fraunces = load_font(font_dir, "Fraunces*.ttf", {"wght": 700, "opsz": 72})
    source = load_font(font_dir, "SourceSans3*.ttf", {"wght": 600})
    word, word_w = outline(fraunces, WORDMARK, WORD_SIZE)
    strap, strap_w = outline(source, STRAPLINE, STRAP_SIZE, STRAP_TRACK)

    # --- horizontal: badge left, wordmark and strapline in a left-aligned stack ---------
    h_h = 72.0
    b_size = 64.0
    text_x = 80.0
    word_base = 40.0
    strap_base = 58.0
    h_w = round(text_x + max(word_w, strap_w) + 6.0)

    def horizontal(mark: str, word_fill: str, strap_fill: str, tid: str,
                   word_extra: str = "", strap_extra: str = "") -> str:
        return (HEAD.format(w=h_w, h=h_h, title=TITLE, tid=tid)
                + badge(mark, 4, 4, b_size)
                + f'  <g fill="{word_fill}"{word_extra} '
                  f'transform="translate({text_x:g},{word_base:g})">\n      {word}\n  </g>\n'
                + f'  <g fill="{strap_fill}"{strap_extra} '
                  f'transform="translate({text_x:g},{strap_base:g})">\n      {strap}\n  </g>\n'
                + "</svg>\n")

    write("logo-horizontal.svg", horizontal(body_colour, ink, quiet, "bsuk-logo-h"))
    write("logo-mono.svg", horizontal(body_mono, "currentColor", "currentColor",
                                      "bsuk-logo-mono", strap_extra=' fill-opacity="0.55"'))

    # --- stacked: badge over a centred wordmark and strapline ---------------------------
    s_badge = 88.0
    s_w = round(max(s_badge, word_w, strap_w) + 24.0)
    s_h = 148.0
    write("logo-stacked.svg",
          HEAD.format(w=s_w, h=s_h, title=TITLE, tid="bsuk-logo-stacked")
          + badge(body_colour, (s_w - s_badge) / 2, 4, s_badge)
          + f'  <g fill="{ink}" transform="translate({(s_w - word_w) / 2:.2f},122)">\n'
            f'      {word}\n  </g>\n'
          + f'  <g fill="{quiet}" transform="translate({(s_w - strap_w) / 2:.2f},141)">\n'
            f'      {strap}\n  </g>\n'
          + "</svg>\n")

    # --- icon: the badge alone, at its own 100x100 grid ---------------------------------
    write("logo-icon.svg",
          HEAD.format(w=100, h=100, title="BlueStaffyUK", tid="bsuk-logo-icon")
          + body_colour + "\n</svg>\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
