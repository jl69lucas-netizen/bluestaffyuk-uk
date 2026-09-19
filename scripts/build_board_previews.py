#!/usr/bin/env python3
"""build_board_previews.py <slug> — the built board-preview route -> the board's style blocks.

`src/pages/board-preview/<slug>.astro` renders every section of a board record three times,
once per style, as `<section data-section="<id>" data-style="S1|S2|S3">`. This script cuts
those blocks out of the BUILT page and writes them, with the page's own inlined CSS, to
`data/boards/previews/<slug>.json`:

    {"css":    "<every <style> block of the built page, in document order>",
     "blocks": {"<section id>|<style id>": "<inner html>"},
     "names":  {"<section id>|<style id>": "<the style's own name>"},
     "images": {"<original url>": "data:image/webp;base64,…"}}

`scripts/build_page_board.py` reads that file and mounts each block in a sandboxed srcdoc
iframe at 1280 / 768 / 375, three per style, so the breeder judges the arrangement at the
three widths rather than at one.

WHERE THE BYTES LIVE. This JSON is GITIGNORED (`data/boards/previews/`): it is derived from
`dist/`, which is itself gitignored, and a committed copy would be a snapshot that
disagrees with the kit the moment a component changes. The BOARD, on the other hand, is a
committed artifact and it CARRIES the images — a srcdoc frame is sandboxed and has no
origin, so `/images/x.webp` inside one resolves to nothing and every photo would be a
broken box. So each photo is re-encoded here (downscaled to the widest frame, webp q80) and
embedded once per board as a data URI. That re-encode is what keeps
`docs/artifacts/boards/<slug>.html` a file a browser opens rather than a megabyte per
photo; the totals are printed on every run so the growth is visible, not discovered.

Run it after `npm run build`, before `build_page_board.py`.

  python3 scripts/build_board_previews.py _demo
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pageboard as PB
from _kit_sections import page_css

OUT = PB.ROOT / "data" / "boards" / "previews"

#: The three ids a styled section offers, in order. Mirrors STYLE_IDS in src/lib/boardStyles.ts.
STYLE_IDS = ("S1", "S2", "S3")

_OPEN = re.compile(r"<section\b([^>]*)>", re.I)
_TAG = re.compile(r"</?section\b[^>]*>", re.I)
_ATTR = re.compile(r'data-(section|style|style-name)="([^"]*)"')


def _rel(path):
    """The path as the repo spells it, or absolute when it is outside the repo (a test's
    tmp_path). A message is never worth a traceback of its own."""
    try:
        return str(pathlib.Path(path).relative_to(PB.ROOT))
    except ValueError:
        return str(path)


class StyleError(Exception):
    """A record whose style options are not the three the preview route renders."""


def validate_styles(record):
    """Refuse a record whose `styles` is neither empty nor exactly S1/S2/S3.

    A section offering two styles would render two blocks and the board would show a
    three-radio fieldset with a blank in it; a section offering four would give the page
    build a pick `src/lib/boardStyles.ts` has no entry for. Both are the same fault —
    the record and the style map have drifted — so both are refused here, by name, before
    anything is cut."""
    for sec in record.get("sections", []):
        styles = sec.get("styles")
        if not styles:
            continue
        if list(styles) != list(STYLE_IDS):
            raise StyleError(
                f"section {sec.get('id')}: styles {styles!r} — a styled section offers "
                f"exactly {list(STYLE_IDS)}")
    return True


def cut(html):
    """{(section id, style id): inner html} for every `[data-section][data-style]` block.

    DEPTH-AWARE, not a non-greedy regex: the kit's Hero, TrustStrip, CounterStrip and
    Testimonial each render a `<section>` of their own, so the first `</section>` after a
    block's opening tag is usually the CHILD's. Scanning section tags and tracking the
    depth is the only way the outer block's true end is found."""
    return _scan(html)[0]


def style_names(html):
    """{(section id, style id): the style's own name} from each block's `data-style-name`.

    The NAME lives on the rendered section rather than in a second copy of the style map
    here: src/lib/boardStyles.ts is the one place a style is named, and a Python table of
    the same labels would drift the first time one is reworded."""
    return _scan(html)[1]


def _scan(html):
    blocks, names, stack = {}, {}, []
    for m in _TAG.finditer(html):
        tag = m.group(0)
        if tag.startswith("</"):
            if stack:
                start, key = stack.pop()
                if key is not None:
                    blocks[key] = html[start:m.start()].strip()
            continue
        attrs = dict(_ATTR.findall(_OPEN.match(tag).group(1)))
        key = None
        if "section" in attrs and "style" in attrs:
            key = (attrs["section"], attrs["style"])
            if attrs.get("style-name"):
                names[key] = attrs["style-name"]
        stack.append((m.end(), key))
    return blocks, names


#: The widest frame a board shows (build_page_board.PREVIEW_W[0]). No photo in a preview is
#: ever painted wider than this, so no photo is carried wider than this either: a 2400px
#: master embedded at full size is a megabyte of base64 that the browser then scales down.
FRAME_MAX_W = 1280
#: webp quality for the re-encode. 80 is the band where a 1280px photo stops being
#: distinguishable from the master at arm's length and is a third of the bytes.
WEBP_QUALITY = 80
#: Ceilings, AFTER the re-encode. The per-image one is what a board may spend on one photo;
#: the total is what it may spend on all of them. A url over either is left out of the map
#: and named on stdout — a visible broken box, because a silently dropped photo would be
#: read as a style that has no image in it.
IMG_MAX = 192 * 1024
IMG_TOTAL_MAX = 6 * 1024 * 1024
_IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
_SRCSET = re.compile(r'\s(?:srcset|sizes)="[^"]*"', re.I)
_SRC = re.compile(r'src="([^"]+)"')
MEDIA = {".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
         ".png": "image/png", ".gif": "image/gif", ".svg": "image/svg+xml", ".avif": "image/avif"}


def _candidates(tag):
    """Every url an `<img>` offers: its `src` plus each `srcset` candidate."""
    urls = []
    m = _SRC.search(tag)
    if m:
        urls.append(m.group(1))
    ss = re.search(r'srcset="([^"]+)"', tag, re.I)
    if ss:
        urls += [c.strip().split(" ")[0] for c in ss.group(1).split(",") if c.strip()]
    return [u for u in dict.fromkeys(urls) if u.startswith("/")]


def thin_images(inner, dist):
    """Point each `<img>` at the SMALLEST rendering it offers and drop `srcset`/`sizes`.

    The frames are 375–1280 wide and a board carries nine of them per styled section; a
    responsive set would hand each one the largest file and then scale it down. The pick is
    about arrangement, so the smallest rendering is the honest one to ship."""
    def sub(tag):
        cands = _candidates(tag)
        if not cands:
            return tag
        sized = [(( dist / u.lstrip("/")).stat().st_size, u) for u in cands
                 if (dist / u.lstrip("/")).exists()]
        best = min(sized)[1] if sized else cands[0]
        return _SRC.sub(f'src="{best}"', _SRCSET.sub("", tag), count=1)
    return _IMG_TAG.sub(lambda m: sub(m.group(0)), inner)


def encode_for_frame(path):
    """One image file -> (webp bytes, mime), downscaled so it is never wider than a frame.

    An SVG is passed through: it is already resolution-independent and Pillow would
    rasterise it. Anything Pillow cannot open is passed through as its own bytes rather
    than dropped — a board showing the original is better than a board showing a gap."""
    if path.suffix.lower() == ".svg":
        return path.read_bytes(), "image/svg+xml"
    try:
        from PIL import Image
    except ImportError:                                    # pragma: no cover - Pillow is pinned
        return path.read_bytes(), MEDIA.get(path.suffix.lower(), "application/octet-stream")
    import io
    try:
        with Image.open(path) as im:
            im = im.convert("RGB") if im.mode in ("P", "CMYK") else im.convert("RGBA") if im.mode == "LA" else im
            if im.width > FRAME_MAX_W:
                im = im.resize((FRAME_MAX_W, round(im.height * FRAME_MAX_W / im.width)), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="WEBP", quality=WEBP_QUALITY, method=4)
            return buf.getvalue(), "image/webp"
    except OSError:
        return path.read_bytes(), MEDIA.get(path.suffix.lower(), "application/octet-stream")


def embed_images(blocks, dist):
    """({url: data URI}, [urls left out], total bytes) for every image the blocks reference.

    Each image is re-encoded for the widest frame first (`encode_for_frame`), and the
    ceilings are applied to the RESULT: what matters is what the board ends up carrying,
    not what dist/ happens to hold."""
    import base64
    urls = sorted({u for inner in blocks.values() for u in _candidates(inner)})
    out, total, skipped = {}, 0, []
    for u in urls:
        f = dist / u.lstrip("/")
        if not f.exists():
            skipped.append((u, "not in dist/"))
            continue
        raw, mime = encode_for_frame(f)
        if len(raw) > IMG_MAX:
            skipped.append((u, f"{len(raw) // 1024}KiB after re-encode, over the {IMG_MAX // 1024}KiB per-image cap"))
            continue
        if total + len(raw) > IMG_TOTAL_MAX:
            skipped.append((u, f"would take the board past the {IMG_TOTAL_MAX // (1024 * 1024)}MiB total"))
            continue
        total += len(raw)
        out[u] = f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")
    return out, skipped, total


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: build_board_previews.py <slug>")
        return 2
    slug = argv[0]
    try:
        record = PB.load_board(slug)
        validate_styles(record)
    except (PB.BoardError, StyleError) as e:
        print(f"board-previews ERROR {e}")
        return 2

    page = PB.DIST / "board-preview" / PB.slug_file(slug) / "index.html"
    if not page.exists():
        print(f"board-previews ERROR no built preview at {_rel(page)} — run npm run build")
        return 2
    html = page.read_text(encoding="utf-8")
    blocks = cut(html)

    # A gate that examined nothing is not a pass: say which styled section came back empty
    # rather than writing a file the board would render as three blank iframes.
    wanted = [(s["id"], sid) for s in record["sections"] if s.get("styles") for sid in s["styles"]]
    missing = [f"{a}|{b}" for a, b in wanted if not blocks.get((a, b))]
    if missing:
        print(f"board-previews ERROR {len(missing)} block(s) missing from the built page: {', '.join(missing)}")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / (PB.slug_file(slug) + ".json")
    names = style_names(html)
    thinned = {f"{a}|{b}": thin_images(v, PB.DIST) for (a, b), v in sorted(blocks.items())}
    images, skipped, img_bytes = embed_images(thinned, PB.DIST)
    payload = {"css": page_css(html), "blocks": thinned,
               "names": {f"{a}|{b}": v for (a, b), v in sorted(names.items())},
               "images": images}
    out.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
    block_bytes = sum(len(v) for v in thinned.values())
    print(f"wrote {_rel(out)} — {len(payload['blocks'])} blocks, "
          f"{len(wanted)} required by the record")
    # The totals are printed every run, because the board carries them into a committed
    # file and a board that quietly grew to five megabytes is found by the person opening it.
    print(f"  css {len(payload['css']) // 1024}KiB · blocks {block_bytes // 1024}KiB · "
          f"{len(images)} image(s) {img_bytes // 1024}KiB "
          f"(re-encoded to webp q{WEBP_QUALITY}, max {FRAME_MAX_W}px wide; "
          f"caps {IMG_MAX // 1024}KiB each, {IMG_TOTAL_MAX // (1024 * 1024)}MiB total)")
    for u, why in skipped:
        print(f"  image not embedded — {why}: {u}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
