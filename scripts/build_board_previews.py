#!/usr/bin/env python3
"""build_board_previews.py <slug> — the built board-preview route -> the board's style blocks.

`src/pages/board-preview/<slug>.astro` renders every section of a board record three times,
once per style, as `<section data-section="<id>" data-style="S1|S2|S3">`. This script cuts
those blocks out of the BUILT page and writes them, with the page's own inlined CSS, to
`data/boards/previews/<slug>.json`:

    {"css": "<every <style> block of the built page, in document order>",
     "blocks": {"<section id>|<style id>": "<inner html>"}}

`scripts/build_page_board.py` reads that file and mounts each block in a sandboxed srcdoc
iframe at 1280 / 768 / 375, three per style, so the breeder judges the arrangement at the
three widths rather than at one.

The file is GITIGNORED: it is derived from `dist/`, which is itself gitignored, and a
committed copy would be a snapshot that disagrees with the kit the moment a component
changes. Run it after `npm run build`, before `build_page_board.py`.

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


#: A preview frame is `srcdoc` in a sandboxed iframe: it has NO origin, so `/images/x.webp`
#: and `/_astro/x.webp` resolve to nothing and every photo in a board would be a broken box.
#: The images are therefore carried WITH the blocks, as data URIs, and the board rewrites
#: each `src` from that map as it fills a frame. Two ceilings keep a board a file a browser
#: will open: the largest single image embedded, and the total across the page.
IMG_MAX = 256 * 1024
IMG_TOTAL_MAX = 8 * 1024 * 1024
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


def embed_images(blocks, dist):
    """{url: data URI} for every image the blocks reference, within the two ceilings.

    A url left out of the map is reported by the caller and renders as a broken box in the
    board — visible, which is the point: a silently dropped photo would be read as a style
    that has no image in it."""
    import base64
    urls = sorted({u for inner in blocks.values() for u in _candidates(inner)})
    out, total, skipped = {}, 0, []
    for u in urls:
        f = dist / u.lstrip("/")
        if not f.exists():
            skipped.append(u)
            continue
        raw = f.read_bytes()
        if len(raw) > IMG_MAX or total + len(raw) > IMG_TOTAL_MAX:
            skipped.append(u)
            continue
        total += len(raw)
        mime = MEDIA.get(f.suffix.lower(), "application/octet-stream")
        out[u] = f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")
    return out, skipped


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
    images, skipped = embed_images(thinned, PB.DIST)
    payload = {"css": page_css(html), "blocks": thinned,
               "names": {f"{a}|{b}": v for (a, b), v in sorted(names.items())},
               "images": images}
    out.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {_rel(out)} — {len(payload['blocks'])} blocks, "
          f"{len(payload['css'])} bytes of css, {len(images)} image(s) embedded, "
          f"{len(wanted)} block(s) required by the record")
    for u in skipped:
        print(f"  image not embedded (missing or over {IMG_MAX // 1024}KiB): {u}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
