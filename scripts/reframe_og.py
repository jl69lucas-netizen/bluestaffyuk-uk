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
walked until it is under 55 KB. A file that cannot meet its budget even at the quality
floor is refused (exit 2): both files are encoded to temps beside their targets and
moved into place only when both fit, so a refused run never touches an existing file.

A transparent master (RGBA, LA, or a palette with transparency) is flattened onto bone
before framing, never onto black. An animated master is refused.
"""
import argparse
import io
import os
import pathlib
import re
import sys
import warnings

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

W, H = 1408, 768
SIB_W, SIB_H = 760, 415
SIB_MAX_KB = 55
BONE_50 = (250, 248, 243)     # --color-bone-50  #FAF8F3
BONE_100 = (244, 241, 234)    # --color-bone-100 #F4F1EA
MAX_KB = 95
STYLES = ("contain", "blurfill", "topcover")
MOBCROP = re.compile(r"^[1-9]\d*:[1-9]\d*$")


def mobcrop_problem(mobcrop):
    """None when `mobcrop` is empty or a ratio like 4:5; otherwise the reason it is refused."""
    if mobcrop and not MOBCROP.match(mobcrop):
        return "mobcrop %r is not a ratio like 4:5 (two positive whole numbers)" % mobcrop
    return None


def flatten(im):
    """RGB, with any transparency composited onto BONE_50 rather than dropped to black."""
    if im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info):
        rgba = im.convert("RGBA")
        bed = Image.new("RGB", rgba.size, BONE_50)
        bed.paste(rgba, mask=rgba.getchannel("A"))
        return bed
    return im.convert("RGB")


def load(path):
    """The master as an upright RGB image. Raises ValueError for an animated file; a
    decompression-bomb warning is raised as an error, never shrugged off."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as im:
            if getattr(im, "n_frames", 1) > 1:
                raise ValueError("%s is animated (%d frames); give a still image"
                                 % (pathlib.Path(path).name, im.n_frames))
            return flatten(ImageOps.exif_transpose(im))


def subject_box(w=W, h=H, mobcrop="", fgmaxw=0):
    """(width, height) the sharp subject must fit inside."""
    if fgmaxw:
        return fgmaxw, h
    problem = mobcrop_problem(mobcrop)
    if problem:
        raise ValueError(problem)
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
    """Quality-walk 82 -> 60 (steps of 3, floor 60) until the file fits. Writes the file
    either way and returns (kb, q, ok): ok is False when even q60 is over `maxkb`, and the
    caller must then refuse the image."""
    q = 82
    while True:
        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=q, method=6)
        size = buf.tell() / 1024
        if size <= maxkb or q <= 60:
            pathlib.Path(path).write_bytes(buf.getvalue())
            return round(size, 1), q, size <= maxkb
        q = max(60, q - 3)


def sibling(img, w=SIB_W, h=SIB_H):
    return ImageOps.fit(img, (w, h), Image.LANCZOS)


def _mobcrop_arg(value):
    problem = mobcrop_problem(value)
    if problem:
        raise argparse.ArgumentTypeError(problem)
    return value


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--style", default="blurfill", choices=STYLES)
    ap.add_argument("--w", type=int, default=W)
    ap.add_argument("--h", type=int, default=H)
    ap.add_argument("--blur", type=int, default=14)
    ap.add_argument("--mobcrop", default="", type=_mobcrop_arg)
    ap.add_argument("--fgmaxw", type=int, default=0)
    ap.add_argument("--fgup", action="store_true")
    ap.add_argument("--maxkb", type=int, default=MAX_KB)
    ap.add_argument("--sib", default="")
    a = ap.parse_args(argv)
    if a.mobcrop and a.style != "blurfill":
        print("warning: --mobcrop only applies to --style blurfill; ignored for %s" % a.style,
              file=sys.stderr)
    try:
        master = load(a.src)
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as e:
        print("REFUSED: %s cannot be read as an image: %s" % (a.src, e), file=sys.stderr)
        return 2
    out = render(master, a.style, a.w, a.h, a.blur, a.mobcrop, a.fgmaxw, a.fgup)
    jobs = [(out, pathlib.Path(a.out), a.maxkb, "%dx%d" % (a.w, a.h), "  [%s]" % a.style)]
    if a.sib:
        jobs.append((sibling(out), pathlib.Path(a.sib), SIB_MAX_KB, "%dx%d" % (SIB_W, SIB_H), ""))
    # Encode beside each target; move into place only when every file met its budget, so a
    # refused run never deletes or half-replaces a file that was already there.
    temps, done, over = [], [], []
    try:
        for img, target, maxkb, dims, tag in jobs:
            tmp = target.with_name(".%s.tmp-%d" % (target.name, os.getpid()))
            temps.append(tmp)
            kb, q, ok = save_webp(img, tmp, maxkb)
            if not ok:
                over.append("%s is %sKB at the q60 floor, over the %s KB budget"
                            % (target, kb, maxkb))
            done.append((tmp, target, "  %s  %s  %sKB q%d%s" % (target, dims, kb, q, tag)))
        if over:
            print("REFUSED: %s; nothing written" % "; ".join(over), file=sys.stderr)
            return 2
        for tmp, target, line in done:
            os.replace(tmp, target)
            print(line)
        return 0
    finally:
        for tmp in temps:
            if tmp.exists():
                tmp.unlink()

if __name__ == "__main__":
    raise SystemExit(main())
