#!/usr/bin/env python3
"""Bake every image the migrated pages reference, plus the six pup masters.
Usage: python3 scripts/bake_images.py [--src /Users/apple/bluestaffyuk-site]"""
import argparse, json, pathlib, re, shutil
from PIL import Image, ImageOps, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_KB = 95
BOX = (1408, 768)
RASTER_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")
SIZED_VARIANT = re.compile(r"-\d{2,4}x\d{2,4}$")


def _walk(im, out, max_kb=MAX_KB):
    q = 82
    for q in range(82, 39, -3):
        im.save(out, "WEBP", quality=q, method=6)
        if out.stat().st_size <= max_kb * 1024:
            return q
    return q


MIN_WIDTH = 640


def _save_within_budget(im, out, max_kb=MAX_KB):
    """Quality walk first; if even q40 busts the budget, step the resolution down.

    Detailed photographs left at master resolution (the no-upscale branch) can sit at
    140-180KB even at q40, so quality alone cannot hold the budget for them.
    """
    _walk(im, out, max_kb)
    while out.stat().st_size > max_kb * 1024 and im.width > MIN_WIDTH:
        w = max(MIN_WIDTH, int(im.width * 0.85))
        im = im.resize((w, max(1, round(im.height * w / im.width))), Image.LANCZOS)
        _walk(im, out, max_kb)
    return im


def bake_body_image(src, dst_dir, stem, centering=(0.5, 0.5)):
    dst_dir = pathlib.Path(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    if im.width < BOX[0]:
        full_im = im                                   # never upscale
    else:
        full_im = ImageOps.fit(im, BOX, Image.LANCZOS, centering=centering)
    full = dst_dir / ("%s.webp" % stem)
    _save_within_budget(full_im, full)
    if full_im.width > 760:
        sib_im = full_im.resize((760, round(full_im.height * 760 / full_im.width)), Image.LANCZOS)
    else:
        sib_im = full_im
    sib = dst_dir / ("%s-760.webp" % stem)
    _save_within_budget(sib_im, sib)
    return full, sib


def bake_puppy_card(src, dst_dir, slug, centering=(0.5, 0.4)):
    dst_dir = pathlib.Path(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    card = dst_dir / ("%s-card-800.webp" % slug)
    _walk(ImageOps.fit(im, (800, 800), Image.LANCZOS, centering=centering), card)
    W, H = 800, 1000
    bg = ImageOps.fit(im, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
    fg = im.copy()
    fg.thumbnail((W, H), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    tall = dst_dir / ("%s-portrait-4x5.webp" % slug)
    _walk(bg, tall)
    return card, tall


def _generated_files():
    candidates = (list(ROOT.glob("src/pages/**/*.astro")) + [ROOT / "data/locations.json"]
                  + list(ROOT.glob("src/content/blog/*.md")))
    return [f for f in candidates if f.exists()]


def referenced_stems():
    stems = set()
    for f in _generated_files():
        for m in re.finditer(r"/images/([a-z0-9._-]+?)(?:-760)?\.(?:webp|png)",
                             f.read_text(encoding="utf-8")):
            stems.add(m.group(1))
    return sorted(stems)


def referenced_videos():
    """Video filenames the migrated pages/schema point at under /videos/."""
    names = set()
    for f in _generated_files():
        for m in re.finditer(r"/videos/([A-Za-z0-9._-]+\.(?:mp4|webm))", f.read_text(encoding="utf-8")):
            names.add(m.group(1))
    return sorted(names)


def find_master(uploads, stem):
    """The unsuffixed master, else the largest WordPress sized variant. (path, used_fallback)."""
    masters = [p for p in uploads.rglob("%s.*" % stem) if p.suffix.lower() in RASTER_SUFFIXES]
    if masters:
        return max(masters, key=lambda p: p.stat().st_size), False
    variants = [p for p in uploads.rglob("%s-*.*" % stem)
                if p.suffix.lower() in RASTER_SUFFIXES and SIZED_VARIANT.search(p.stem)]
    if variants:
        return max(variants, key=lambda p: p.stat().st_size), True
    return None, False


def main(src_site):
    from extract_images import LOGO_STEMS
    out = ROOT / "public/images"
    out.mkdir(parents=True, exist_ok=True)
    uploads = pathlib.Path(src_site) / "wp-content/uploads"
    missing, fallbacks = [], []
    for stem in referenced_stems():
        m, used_fallback = find_master(uploads, stem)
        if m is None:
            missing.append(stem)
            continue
        if used_fallback:
            fallbacks.append((stem, m.name))
        if stem in LOGO_STEMS:
            shutil.copy(m, out / ("%s.png" % stem))
            continue
        full, sib = bake_body_image(m, out, stem)
        print("%s: %dKB / %dKB" % (stem, full.stat().st_size // 1024, sib.stat().st_size // 1024))
    # Videos are only referenced from JSON-LD VideoObjects; copy them over untouched.
    videos_out = ROOT / "public/videos"
    for name in referenced_videos():
        srcs = list(uploads.rglob(name))
        if not srcs:
            missing.append(name)
            continue
        videos_out.mkdir(parents=True, exist_ok=True)
        shutil.copy(srcs[0], videos_out / name)
        print("%s: copied %dKB (video, verbatim)" % (name, srcs[0].stat().st_size // 1024))
    for p in json.loads((ROOT / "data/puppies.json").read_text(encoding="utf-8")):
        bake_puppy_card(ROOT / "assets/brand" / p["slug"] / p["card_photo"], out / "puppies", p["slug"])
        for g in p["gallery"]:
            bake_body_image(ROOT / "assets/brand" / p["slug"] / g, out / "puppies",
                            "%s-%s" % (p["slug"], pathlib.Path(g).stem.lower()))
    for stem, name in fallbacks:
        print("FALLBACK sized variant for %s -> %s" % (stem, name))
    for stem in missing:
        print("MISSING master for %s" % stem)
    return missing


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="/Users/apple/bluestaffyuk-site")
    raise SystemExit(1 if main(ap.parse_args().src) else 0)
