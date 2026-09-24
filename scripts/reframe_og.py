#!/usr/bin/env python3
"""Bake a named OG framing style (IMAGE-DESIGNS.md §7) into a 1408x768 in-body image.

A portrait or near-square master cover-cropped into the 16:9 box loses the dog's head.
These styles keep the whole dog instead, centred full-height, so the box's later
`object-fit:cover` (or a mobile 4:5 crop) only ever trims padding:

  contain   Style A — the sharp master contained over a bone gradient (#FAF8F3 -> #F4F1EA).
  blurfill  Style B — the sharp master contained over a blurred cover copy of itself.
            The default for a single-dog portrait.
  topcover  Style E — cover fill anchored to the TOP: the head is never cut, paws may crop.

Styles C, D and H are CSS components; their masters are baked at native ratio by
scripts/ingest_image.py, not here.

Usage:
  python3 scripts/reframe_og.py <master> <out.webp> [--style blurfill] [--mobcrop 4:5]
        [--sib <out-760.webp>] [--w 1408] [--h 768] [--blur 14] [--fgup] [--maxkb 95]

`--mobcrop 4:5` keeps the sharp dog inside the central 4:5 strip of the box, so it
survives both the desktop 16:9 box and a mobile 4:5 crop. The main file is quality-walked
from 82 down until it is under --maxkb (rules/images.md); the -760 sibling (760x415) is
walked until it is under 55 KB.
"""
import argparse
import io
import pathlib

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

W, H = 1408, 768
SIB_W, SIB_H = 760, 415
SIB_MAX_KB = 55
BONE_50 = (250, 248, 243)     # --color-bone-50  #FAF8F3
BONE_100 = (244, 241, 234)    # --color-bone-100 #F4F1EA
STYLES = ("contain", "blurfill", "topcover")


def load(path):
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def subject_box(w=W, h=H, mobcrop="", fgmaxw=0):
    """(width, height) the sharp subject must fit inside."""
    if fgmaxw:
        return fgmaxw, h
    if mobcrop:
        rw, rh = (int(x) for x in mobcrop.split(":"))
        return int(h * rw / rh), h
    return w, h


def fit_subject(im, fgw, fgh, allow_upscale=False):
    """Contain the master inside (fgw, fgh). Only upscales when asked: a small master
    then fills the box rather than floating as a stamp (rules/images.md: uniform size
    beats pixel-peeping)."""
    if not allow_upscale:
        fg = im.copy()
        fg.thumbnail((fgw, fgh), Image.LANCZOS)
        return fg
    s = min(fgw / im.width, fgh / im.height)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


def _paste_centred(canvas, fg):
    canvas.paste(fg, ((canvas.width - fg.width) // 2, (canvas.height - fg.height) // 2))
    return canvas


def gradient(w=W, h=H):
    g = Image.new("RGB", (w, h))
    px = g.load()
    for y in range(h):
        t = y / max(1, h - 1)
        row = tuple(int(BONE_50[i] + (BONE_100[i] - BONE_50[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = row
    return g


def contain(im, w=W, h=H, pad=0.90):
    fg = im.copy()
    fg.thumbnail((int(w * pad), int(h * pad)), Image.LANCZOS)
    return _paste_centred(gradient(w, h), fg)


def blurfill(im, w=W, h=H, blur=14, fgw=None, fgh=None, fgup=False):
    bed = ImageOps.fit(im, (w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(blur))
    bed = ImageEnhance.Brightness(bed).enhance(0.92)
    fg = fit_subject(im, fgw or w, fgh or h, fgup)
    return _paste_centred(bed, fg)


def topcover(im, w=W, h=H):
    return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, 0.0))


def render(im, style, w=W, h=H, blur=14, mobcrop="", fgmaxw=0, fgup=False):
    if style == "contain":
        return contain(im, w, h)
    if style == "blurfill":
        fgw, fgh = subject_box(w, h, mobcrop, fgmaxw)
        return blurfill(im, w, h, blur, fgw, fgh, fgup)
    if style == "topcover":
        return topcover(im, w, h)
    raise ValueError("unknown style %r (one of %s)" % (style, ", ".join(STYLES)))


def save_webp(img, path, maxkb):
    """Quality-walk 82 -> 60 (steps of 3, floor 60) until the file fits; returns (kb, q)."""
    q = 82
    while True:
        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=q, method=6)
        if buf.tell() / 1024 <= maxkb or q <= 60:
            pathlib.Path(path).write_bytes(buf.getvalue())
            return round(buf.tell() / 1024, 1), q
        q = max(60, q - 3)


def sibling(img, w=SIB_W, h=SIB_H):
    return ImageOps.fit(img, (w, h), Image.LANCZOS)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--style", default="blurfill", choices=STYLES)
    ap.add_argument("--w", type=int, default=W)
    ap.add_argument("--h", type=int, default=H)
    ap.add_argument("--blur", type=int, default=14)
    ap.add_argument("--mobcrop", default="")
    ap.add_argument("--fgmaxw", type=int, default=0)
    ap.add_argument("--fgup", action="store_true")
    ap.add_argument("--maxkb", type=int, default=95)
    ap.add_argument("--sib", default="")
    a = ap.parse_args(argv)
    out = render(load(a.src), a.style, a.w, a.h, a.blur, a.mobcrop, a.fgmaxw, a.fgup)
    kb, q = save_webp(out, a.out, a.maxkb)
    print("  %s  %dx%d  %sKB q%d  [%s]" % (a.out, a.w, a.h, kb, q, a.style))
    if a.sib:
        kb2, q2 = save_webp(sibling(out), a.sib, SIB_MAX_KB)
        print("  %s  %dx%d  %sKB q%d" % (a.sib, SIB_W, SIB_H, kb2, q2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
