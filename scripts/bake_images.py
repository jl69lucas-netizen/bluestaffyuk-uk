#!/usr/bin/env python3
"""Bake every image the migrated pages reference, plus the six pup masters.

Every baked file is measured into data/image-manifest.json, and the run then ENDS BY
RE-EXTRACTING (apply_manifest) so the pages' width/height/srcset come from those
measurements rather than from guessed numbers. `npm run bake` therefore rewrites
src/pages, src/content/blog and data/locations.json as well as public/images, and is
idempotent: same source clone plus same manifest yields byte-identical output.

Usage: python3 scripts/bake_images.py [--src /Users/apple/bluestaffyuk-site]"""
import argparse, json, pathlib, re, shutil
from PIL import Image, ImageOps, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_KB = 95
BOX = (1408, 768)
RASTER_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")
SIZED_VARIANT = re.compile(r"-\d{2,4}x\d{2,4}$")


def _walk(im, out, max_kb=MAX_KB):
    """Save as WebP, stepping quality down until the file fits. Returns the quality used."""
    for q in range(82, 39, -3):
        im.save(out, "WEBP", quality=q, method=6)
        if out.stat().st_size <= max_kb * 1024:
            return q
    return 40


MIN_WIDTH = 640
SIB_WIDTH = 760


def _over(out, max_kb):
    return out.stat().st_size > max_kb * 1024


def _save_within_budget(im, out, max_kb=MAX_KB, allow_downscale=True):
    """Quality walk first; if even q40 busts the budget, step the resolution down.

    Detailed photographs left at master resolution (the no-upscale branch) can sit at
    140-180KB even at q40, so quality alone cannot hold the budget for them. Fixed-geometry
    outputs (pup cards, 4:5 portraits) pass allow_downscale=False and only get a warning:
    their dimensions are a layout contract, so shrinking them is not ours to do.
    Returns the image as actually written, so callers can record its real size.
    """
    _walk(im, out, max_kb)
    if allow_downscale:
        while _over(out, max_kb) and im.width > MIN_WIDTH:
            w = max(MIN_WIDTH, int(im.width * 0.85))
            im = im.resize((w, max(1, round(im.height * w / im.width))), Image.LANCZOS)
            _walk(im, out, max_kb)
    if _over(out, max_kb):
        print("WARNING over budget at q40 (%dx%d, %dKB): %s" % (
            im.width, im.height, out.stat().st_size // 1024, out.name))
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
    # The budget fit may have shrunk the full image, so the sibling must be derived from
    # what was actually written -- otherwise the "smaller" candidate can end up wider.
    full_im = _save_within_budget(full_im, full)
    sib = dst_dir / ("%s-760.webp" % stem)
    if full_im.width > SIB_WIDTH:
        sib_im = full_im.resize(
            (SIB_WIDTH, max(1, round(full_im.height * SIB_WIDTH / full_im.width))), Image.LANCZOS)
        sib_im = _save_within_budget(sib_im, sib)
        sib_w = sib_im.width
    else:
        # A sibling would be byte-identical to the full image: don't write one, and clear
        # any stale copy left by an earlier bake.
        if sib.exists():
            sib.unlink()
        sib, sib_w = None, None
    return full, sib, {"w": full_im.width, "h": full_im.height, "sib_w": sib_w}


def bake_puppy_card(src, dst_dir, slug, centering=(0.5, 0.4), portrait=True):
    """The square card, and (only when asked) the blurred-background 4:5 portrait.

    Project 3 Task 7: the pages render the masters through astro:assets, so the portrait
    and the gallery derivatives have no consumer left. `portrait=False` is what main()
    passes; the default keeps the pair for any caller that still wants both.
    """
    dst_dir = pathlib.Path(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    card = dst_dir / ("%s-card-800.webp" % slug)
    _save_within_budget(ImageOps.fit(im, (800, 800), Image.LANCZOS, centering=centering),
                        card, allow_downscale=False)
    if not portrait:
        return card, None
    W, H = 800, 1000
    bg = ImageOps.fit(im, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
    fg = im.copy()
    fg.thumbnail((W, H), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    tall = dst_dir / ("%s-portrait-4x5.webp" % slug)
    _save_within_budget(bg, tall, allow_downscale=False)
    return card, tall


def _generated_files():
    candidates = (list(ROOT.glob("src/pages/**/*.astro")) + [ROOT / "data/locations.json"]
                  + list(ROOT.glob("src/content/blog/*.md")))
    return [f for f in candidates if f.exists()]


def referenced_stems(files=None):
    stems = set()
    for f in _generated_files() if files is None else files:
        for m in re.finditer(r"/images/([A-Za-z0-9._-]+?)(?:-760)?\.(?:webp|png)",
                             pathlib.Path(f).read_text(encoding="utf-8")):
            stems.add(m.group(1))
    return sorted(stems)


def referenced_videos(files=None):
    """Video filenames the migrated pages/schema point at under /videos/."""
    names = set()
    for f in _generated_files() if files is None else files:
        for m in re.finditer(r"/videos/([A-Za-z0-9._-]+\.(?:mp4|webm))",
                             pathlib.Path(f).read_text(encoding="utf-8")):
            names.add(m.group(1))
    return sorted(names)


def load_centering():
    """Optional per-stem crop centering, so art direction can override the default centre."""
    try:
        raw = json.loads((ROOT / "data/image-centering.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict((k, tuple(v)) for k, v in raw.items()
                if not k.startswith("_") and isinstance(v, list) and len(v) == 2)


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


def apply_manifest(src_site, manifest):
    """Re-run the extraction so the rewrite emits the freshly measured widths.

    The bodies live JSON-encoded inside .astro frontmatter and locations.json, so patching
    them in place would mean re-parsing generated output. Re-extracting from the source
    clone is both simpler and exactly idempotent: same input, same manifest, same bytes.
    """
    import extract_images
    from extract_writers import run
    extract_images.set_manifest(manifest)
    run(pathlib.Path(src_site), ROOT)


def load_manifest():
    """The last measured manifest from disk, or {} when there is none yet."""
    try:
        return json.loads((ROOT / "data/image-manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def main(src_site):
    from extract_images import LOGO_STEMS
    # Cold start: on a fresh clone there are no generated pages yet, so nothing references
    # any image and the bake would copy nothing. Extract once from the stored manifest first
    # so the referenced-stem scan below has pages to read and one bake converges.
    #
    # SIDE EFFECT, deliberate: apply_manifest() re-runs the whole extraction, so this
    # rewrites every generated file (src/pages/**, data/locations.json, src/content/blog/*)
    # from the source clone before a single image is baked. That is safe because generated
    # output is a pure function of the clone plus the manifest, but it means `npm run bake`
    # on a fresh checkout also regenerates the pages — and it only fires when nothing is
    # generated yet, so a normal repeat bake never triggers it.
    if not referenced_stems():
        apply_manifest(src_site, load_manifest())
    out = ROOT / "public/images"
    out.mkdir(parents=True, exist_ok=True)
    uploads = pathlib.Path(src_site) / "wp-content/uploads"
    centering = load_centering()
    manifest, missing, fallbacks = {}, [], []
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
        full, sib, dims = bake_body_image(m, out, stem, centering.get(stem, (0.5, 0.5)))
        manifest[stem] = dims
        print("%s: %dx%d %dKB%s" % (
            stem, dims["w"], dims["h"], full.stat().st_size // 1024,
            " / %dw %dKB" % (dims["sib_w"], sib.stat().st_size // 1024) if sib else " (no sibling)"))
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
    # Project 3 Task 7 moved the puppy masters from assets/brand/<slug>/ into
    # src/assets/puppies/, and the pages now render THEM through astro:assets. One
    # derivative survives: og:image and the Product schema are absolute URLs in markup,
    # which a content-hashed build asset cannot be, so they keep pointing at
    # public/images/puppies/<slug>-card-800.webp. The portrait and the gallery webps had
    # no consumer left, so they are no longer baked.
    masters = ROOT / "src/assets/puppies"
    for p in json.loads((ROOT / "data/puppies.json").read_text(encoding="utf-8")):
        slug = p["slug"]
        bake_puppy_card(masters / p["card_photo"], out / "puppies", slug, portrait=False)
        manifest["puppies/%s-card-800" % slug] = {"w": 800, "h": 800, "sib_w": None}
    (ROOT / "data/image-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote data/image-manifest.json (%d entries)" % len(manifest))
    for stem, name in fallbacks:
        print("FALLBACK sized variant for %s -> %s" % (stem, name))
    for stem in missing:
        print("MISSING master for %s" % stem)
    if not missing:
        apply_manifest(src_site, manifest)
    return missing


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="/Users/apple/bluestaffyuk-site")
    raise SystemExit(1 if main(ap.parse_args().src) else 0)
