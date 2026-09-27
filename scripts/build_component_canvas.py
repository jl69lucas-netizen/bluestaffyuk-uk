#!/usr/bin/env python3
"""Build a city component canvas — one self-contained page the user picks from.

Spec docs/superpowers/specs/2026-09-27-london-component-design-pass-design.md §2. Fifteen
sections in city-page order (scripts/city_components.py); each holds variants A, B and C,
each rendered in its own true-width frame (an iframe whose srcdoc is the fragment wrapped in
the real design tokens) at 375, 768 or 1280, phone first. Frames load lazily, one section at
a time. Each component takes one pick (A, B, C or "none — redesign") and a note, saved in the
canvas's own db; "Send picks to Claude" posts a comment the way the answer board does
(scripts/answer_board_client.js). Without a db the page is a read-only view.

    python3 scripts/build_component_canvas.py [--city london] [--out PATH] [--files-map PATH]
        [--inline-images] [--allow-partial] [--final] [--emit-frames DIR]

--files-map writes the {published path: source path} map of every image a fragment uses, for
the Artifact publish's `files` (a srcdoc frame resolves relative URLs against the page).
--inline-images embeds every image as a data: URI instead — the fallback if the published
page's frames cannot reach its files; refused when the page would pass 15 MB.
--emit-frames writes each variant as a standalone document under DIR, with image URLs that
resolve when DIR is served from the repo root, plus DIR/index.json — the input of
tests/render/canvas.spec.ts. Publish the page with capabilities
{db: {rules: [{path: "", read: "admin", write: "admin"}]}, comments: {}}.
"""
import argparse
import base64
import html
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from city_components import CANVAS_ROOT, COMPONENTS, ROOT, VARIANT_IDS  # noqa: E402

CLIENT_JS = ROOT / "scripts" / "component_canvas_client.js"
TOKENS = ROOT / "src" / "styles" / "tokens.css"
TITLE = "London Component Canvas"
WIDTHS = (375, 768, 1280)
#: Components whose point is how they behave while the page scrolls (a sticky strip, a fixed
#: dial). Their frame is held to a device's height, so it scrolls inside itself, instead of
#: being grown to its content like every other frame.
DEVICE_FRAMES = ("desktop-dial", "jump-links")
FONTS_HREF = ("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;"
              "9..144,700&family=Source+Sans+3:wght@400;600;700&display=swap")
IMAGE_SOURCES = {"images": ROOT / "public" / "images", "puppies": ROOT / "src" / "assets" / "puppies"}
CANVAS_ASSETS = {"images": "images/", "puppies": "puppies/"}
SERVED_ASSETS = {"images": "/public/images/", "puppies": "/src/assets/puppies/"}
_ASSET = re.compile(r"(?<=[\"'(\s,])/(images|puppies)/")
_ASSET_FILE = re.compile(r"(?<=[\"'(\s,])/(images|puppies)/([A-Za-z0-9._-]+)")
MIME = {".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".svg": "image/svg+xml", ".avif": "image/avif"}
MAX_PAGE_BYTES = 15 * 1024 * 1024

FRAME_BASE = (
    "*,*::before,*::after{box-sizing:border-box}"
    "html{-webkit-text-size-adjust:100%}"
    "body{margin:0;background:var(--color-surface);color:var(--color-text);"
    "font-family:var(--font-body);font-size:var(--text-base);"
    "line-height:var(--text-base--line-height)}"
    "h1,h2,h3,h4,h5,h6{font-family:var(--font-display);color:var(--color-brand)}"
    "img{max-width:100%;height:auto}"
    "a{color:var(--color-link)}"
    ":focus-visible{outline:3px solid var(--color-focus);outline-offset:2px}"
    "@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}"
)

CSS = """
:root{--ground:#F4F1EA;--paper:#FFFFFF;--ink:#1B2430;--ink-2:#46566B;--ink-3:#5E6B7A;--line:#DAD6CC;--brand:#1F3A52;--brand-soft:#E4EAF1;--accent:#A8861C;--ok:#2F6B4F;--warn:#9A4A2A;--on-brand:#FFFFFF;--field:#FAF8F3;--stage:#E4EAF1;--shade:#14202B2E}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ground:#121920;--paper:#1A232D;--ink:#E9ECF0;--ink-2:#B4BFCC;--ink-3:#8F9CAB;--line:#2C3743;--brand:#9DBAD6;--brand-soft:#22303F;--accent:#D9B84A;--ok:#7FC49F;--warn:#E39B7A;--on-brand:#121920;--field:#151D26;--stage:#0E141A;--shade:#00000066}}
:root[data-theme="dark"]{--ground:#121920;--paper:#1A232D;--ink:#E9ECF0;--ink-2:#B4BFCC;--ink-3:#8F9CAB;--line:#2C3743;--brand:#9DBAD6;--brand-soft:#22303F;--accent:#D9B84A;--ok:#7FC49F;--warn:#E39B7A;--on-brand:#121920;--field:#151D26;--stage:#0E141A;--shade:#00000066}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--ground);color:var(--ink);font:16px/1.6 "Source Sans 3",system-ui,-apple-system,sans-serif;overflow-x:hidden}
a{color:var(--brand)}
.wrap{max-width:1360px;margin:0 auto;padding:24px clamp(16px,3vw,40px) 96px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--brand);font-weight:700;margin:0 0 6px}
h1.title{font:700 clamp(28px,4vw,42px)/1.08 Fraunces,Georgia,serif;margin:0 0 8px}
.lede{max-width:72ch;color:var(--ink-2);margin:0 0 12px}
.bar{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:16px 0}
.count{font:700 20px/1 Fraunces,Georgia,serif}.count span{font:600 13px "Source Sans 3",sans-serif;color:var(--ink-3)}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:999px;overflow:hidden}
.seg button{font:inherit;font-size:13px;font-weight:600;border:0;background:transparent;color:var(--ink-2);padding:8px 12px;min-height:40px;cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--brand);color:var(--on-brand)}
.status{font-size:14px;color:var(--ink-2);margin:0}
nav.toc ol{display:flex;flex-wrap:wrap;gap:6px;list-style:none;padding:0;margin:0 0 16px}
nav.toc a{display:inline-flex;gap:6px;align-items:center;font-size:13px;text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:6px 10px;min-height:36px;background:var(--paper);color:var(--ink-2)}
nav.toc a[data-picked="true"]{border-color:var(--ok);color:var(--ink)}
.dot{width:9px;height:9px;border-radius:50%;border:1.5px solid var(--ink-3)}
[data-picked="true"] .dot{background:var(--ok);border-color:var(--ok)}
section.comp{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:20px clamp(16px,2vw,28px);margin:0 0 20px;scroll-margin-top:84px}
.comp-head{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px;align-items:baseline}
.comp h2{font:700 24px/1.2 Fraunces,Georgia,serif;margin:0}
.variants{display:grid;grid-template-columns:minmax(0,1fr);gap:18px;margin:14px 0}
@media (min-width:1200px){.comp[data-width="375"] .variants{grid-template-columns:repeat(3,minmax(0,1fr))}}
figure.variant{margin:0;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--field);min-width:0}
figure.variant figcaption{padding:10px 12px;border-bottom:1px solid var(--line)}
.vname{font-weight:700}.vname b{color:var(--brand);margin-right:6px}
.vdesc,.vnew,.vsrc{font-size:14px;color:var(--ink-2);margin:4px 0 0}
.vnew{color:var(--ink)}.vsrc{font-size:12px;color:var(--ink-3);overflow-wrap:anywhere}
.stage{background:var(--stage);padding:12px;overflow:hidden}
.stage-inner{position:relative;margin:0 auto}
.stage iframe{display:block;border:0;background:var(--paper);transform-origin:0 0;box-shadow:0 1px 3px var(--shade)}
.stage .loading{font-size:13px;color:var(--ink-3);padding:24px;text-align:center}
fieldset.pick{border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:6px 0 0}
fieldset.pick legend{font-weight:700;padding:0 6px}
.opts{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 10px}
.opts label{display:inline-flex;gap:8px;align-items:center;border:1.5px solid var(--line);border-radius:8px;padding:8px 12px;min-height:44px;cursor:pointer;background:var(--field)}
.opts input{accent-color:var(--brand);width:18px;height:18px}
.opts label:has(input:checked){border-color:var(--ok);background:var(--brand-soft);font-weight:600}
label.lab{display:block;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--brand);margin:4px 0}
textarea{width:100%;min-height:64px;resize:vertical;font:15px/1.5 "Source Sans 3",system-ui,sans-serif;color:var(--ink);background:var(--field);border:1.5px solid var(--line);border-radius:8px;padding:10px 12px}
textarea:focus{border-color:var(--brand)}
button:focus-visible,a:focus-visible,textarea:focus-visible,input:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.btn{font:inherit;font-weight:700;border:1px solid var(--brand);background:var(--brand);color:var(--on-brand);border-radius:8px;padding:12px 20px;min-height:44px;cursor:pointer}
.btn.ghost{background:transparent;color:var(--brand)}
.btn[aria-disabled="true"],.btn:disabled{opacity:.5;cursor:not-allowed}
section.send{border:2px solid var(--brand)}
.final{background:var(--brand-soft);border:1px solid var(--brand);border-radius:10px;padding:12px 14px;margin:12px 0;font-weight:600}
@media (max-width:640px){.bar{position:static}.comp h2{font-size:21px}.stage{padding:8px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""


def load_canvas(canvas_dir):
    """({component: {variant: fragment}}, {component: meta}) for the components present."""
    frags, metas = {}, {}
    for cid, _name, _shapes in COMPONENTS:
        d = pathlib.Path(canvas_dir) / cid
        if not d.is_dir():
            continue
        frags[cid] = {v: (d / f"{v}.html").read_text(encoding="utf-8")
                      for v in VARIANT_IDS if (d / f"{v}.html").is_file()}
        m = d / "meta.json"
        metas[cid] = json.loads(m.read_text(encoding="utf-8")) if m.is_file() else {"variants": {}}
    return frags, metas


def frame_tokens(tokens_path=TOKENS):
    """tokens.css as a plain `:root` block: Tailwind's `@theme` means nothing in a frame."""
    return pathlib.Path(tokens_path).read_text(encoding="utf-8").replace("@theme {", ":root {", 1)


def rewrite_assets(fragment, prefixes):
    return _ASSET.sub(lambda m: prefixes[m.group(1)], fragment)


def inline_images(fragment):
    """Every /images/ and /puppies/ URL as a data: URI of the repo file it names."""
    def data_uri(m):
        src = IMAGE_SOURCES[m.group(1)] / m.group(2)
        mime = MIME.get(src.suffix.lower(), "application/octet-stream")
        return f"data:{mime};base64," + base64.b64encode(src.read_bytes()).decode("ascii")
    return _ASSET_FILE.sub(data_uri, fragment)


def frame_document(fragment, prefixes, tokens):
    """One variant as a standalone document: fonts, tokens, the frame base, the fragment.
    `prefixes` None means the images are already inlined."""
    return ("<!doctype html><html lang=\"en-GB\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<link rel=\"stylesheet\" href=\"{FONTS_HREF}\">"
            f"<style>{tokens}</style><style>{FRAME_BASE}</style></head>"
            f"<body><main class=\"canvas-frame\">"
            f"{fragment if prefixes is None else rewrite_assets(fragment, prefixes)}</main>"
            "</body></html>")


def files_map(frags):
    """{published path: repo path} for every image any fragment references."""
    out = {}
    for variants in frags.values():
        for text in variants.values():
            for m in re.finditer(r"/(images|puppies)/([A-Za-z0-9._-]+)", text):
                folder, name = m.group(1), m.group(2)
                src = IMAGE_SOURCES[folder] / name
                if src.is_file():
                    out[f"{folder}/{name}"] = str(src.relative_to(ROOT))
    return dict(sorted(out.items()))


def _blob(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True)
            .replace("</", "<\\/").replace("<!--", "<\\u0021--"))


def _width_switch(scope):
    return (f'<div class="seg" role="group" aria-label="Preview width{scope}">'
            + "".join(f'<button type="button" data-width="{w}" aria-pressed="{str(w == 375).lower()}">'
                      f'{label} {w}</button>'
                      for w, label in zip(WIDTHS, ("Phone", "Tablet", "Desktop")))
            + "</div>")


def _section(n, cid, name, variants, meta, final):
    rows = (meta.get("variants") or {})
    figs = []
    for v in VARIANT_IDS:
        if v not in variants:
            continue
        r = rows.get(v) or {}
        srcs = ", ".join(pathlib.PurePath(s).name if s.startswith("/") else s
                         for s in (r.get("idea_sources") or []))
        figs.append(
            f'<figure class="variant" data-variant="{v}">'
            f'<figcaption><p class="vname"><b>{v.upper()}</b>{html.escape(r.get("name", ""))}</p>'
            f'<p class="vdesc">{html.escape(r.get("description", ""))}</p>'
            f'<p class="vnew"><strong>New because:</strong> {html.escape(r.get("differs_from", ""))}</p>'
            f'<p class="vsrc">Idea from: {html.escape(srcs)}</p></figcaption>'
            f'<div class="stage"><div class="stage-inner">'
            f'<p class="loading">Loading the preview…</p>'
            f'<iframe title="{html.escape(name)} — variant {v.upper()}" data-key="{cid}/{v}" '
            f'width="375" height="480" tabindex="-1"></iframe></div></div></figure>')
    dis = " disabled" if final else ""
    opts = "".join(
        f'<label><input type="radio" name="pick-{cid}" value="{val}"{dis}> {label}</label>'
        for val, label in (("a", "A"), ("b", "B"), ("c", "C"), ("redesign", "None — redesign")))
    device = ' data-frame="device"' if cid in DEVICE_FRAMES else ""
    return (f'<section class="comp" id="c-{cid}" data-component="{cid}" data-width="375"{device} '
            f'aria-labelledby="h-{cid}">'
            f'<div class="comp-head"><h2 id="h-{cid}">{n}. {html.escape(name)}</h2>'
            f'{_width_switch(" for " + html.escape(name))}</div>'
            f'<div class="variants">{"".join(figs)}</div>'
            f'<fieldset class="pick" data-pick="{cid}"><legend>Your pick for {html.escape(name)}</legend>'
            f'<div class="opts">{opts}</div>'
            f'<label class="lab" for="note-{cid}">Note (what to keep, what to change)</label>'
            f'<textarea id="note-{cid}" data-note="{cid}" rows="2" autocomplete="off"{dis}></textarea>'
            f'</fieldset></section>')


def render_page(frags, metas, tokens, final=False, inline=False):
    frames = {f"{cid}/{v}": (frame_document(inline_images(text), None, tokens) if inline
                             else frame_document(text, CANVAS_ASSETS, tokens))
              for cid, variants in frags.items() for v, text in variants.items()}
    names = [(cid, name) for cid, name, _s in COMPONENTS if cid in frags]
    toc = "".join(f'<li><a href="#c-{cid}" data-toc="{cid}"><span class="dot" aria-hidden="true"></span>'
                  f'{i}. {html.escape(name)}</a></li>' for i, (cid, name) in enumerate(names, 1))
    sections = "".join(_section(i, cid, name, frags[cid], metas.get(cid, {}), final)
                       for i, (cid, name) in enumerate(names, 1))
    client = CLIENT_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
    banner = ('<p class="final" role="note">Final — these picks are frozen and saved in the repo. '
              'The page is kept as the record of what was offered.</p>') if final else ""
    dis = " disabled" if final else ""
    return f"""<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITLE)}</title>
<link rel="stylesheet" href="{FONTS_HREF}">
<style>{CSS}</style></head><body data-final="{str(final).lower()}">
<div class="wrap">
<header><p class="eyebrow">BlueStaffyUK · project 5 · the London page</p>
<h1 class="title">{html.escape(TITLE)}</h1>
<p class="lede">Fifteen components of the London page, three new designs each, on the real
BlueStaffyUK tokens. Pick A, B or C for each one, or "None — redesign" with a note, then send
your picks. Previews start at phone width; switch any section, or all of them, to tablet or
desktop. The dial and the jump links scroll inside their own frames, so you can see them stick.
Copy in the previews is placeholder London copy; reviews are marked placeholders.</p>
{banner}</header>
<div class="bar" role="region" aria-label="Progress and preview width">
<p class="count"><b id="picked">0</b> / <b id="total">{len(names)}</b><span> picked</span></p>
{_width_switch(" for every section").replace('class="seg"', 'class="seg" id="all-widths"')}
<p id="status" class="status" role="status">Connecting to the canvas…</p>
</div>
<nav class="toc" aria-label="Components"><ol>{toc}</ol></nav>
{sections}
<section class="comp send" id="send" aria-labelledby="h-send">
<h2 id="h-send">Anything else, then send</h2>
<label class="lab" for="general-notes">General notes</label>
<textarea id="general-notes" rows="4" autocomplete="off"{dis}></textarea>
<p><button type="button" class="btn" id="send-picks"{dis}>Send picks to Claude</button>
<button type="button" class="btn ghost" id="copy-picks">Copy picks</button></p>
<p id="send-status" class="status" role="status"></p>
</section>
</div>
<script type="application/json" id="frames">{_blob(frames)}</script>
<script>{client}</script>
</body></html>
"""


def emit_frames(frags, out_dir, tokens, metas=None):
    """Write each variant as a standalone document under out_dir, plus index.json. The files
    the previous index listed are removed first, so a dropped variant cannot linger and be
    measured. With `metas`, each row carries the variant's declared meta.json axes, which the
    canvas smoke holds against the paint (tests/render/canvas.spec.ts, learning loop 2026-09-27)."""
    out_dir = pathlib.Path(out_dir)
    old = out_dir / "index.json"
    if old.is_file():
        for row in json.loads(old.read_text(encoding="utf-8")):
            stale = ROOT / row["path"]
            if stale.is_file() and out_dir.resolve() in stale.resolve().parents:
                stale.unlink()
    index = []
    for cid, variants in frags.items():
        for v, text in variants.items():
            p = out_dir / cid / f"{v}.html"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(frame_document(text, SERVED_ASSETS, tokens), encoding="utf-8")
            row = {"component": cid, "variant": v, "path": str(p.resolve().relative_to(ROOT))}
            axes = (((metas or {}).get(cid) or {}).get("variants", {}).get(v) or {}).get("axes")
            if axes is not None:
                row["axes"] = axes
            index.append(row)
    (out_dir / "index.json").write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")
    return index


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build a city component canvas.")
    ap.add_argument("--city", default="london")
    ap.add_argument("--out")
    ap.add_argument("--files-map")
    ap.add_argument("--inline-images", action="store_true")
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--emit-frames")
    ap.add_argument("--root", help="read the canvas from this folder instead of "
                    "design/city-canvas/<city> (a past revision's fragments, replayed)")
    a = ap.parse_args(argv)
    frags, metas = load_canvas(pathlib.Path(a.root) if a.root else CANVAS_ROOT / a.city)
    tokens = frame_tokens()
    if a.emit_frames:
        index = emit_frames(frags, a.emit_frames, tokens, metas)
        print(f"{a.emit_frames}: {len(index)} frames from {len(frags)} components")
        if not index:
            print("emitted 0 frames — nothing to render, not a pass")
            return 1
        return 0
    complete = len(frags) == len(COMPONENTS) and all(len(v) == 3 for v in frags.values())
    if not complete and not a.allow_partial:
        print(f"the {a.city} canvas holds {sum(len(v) for v in frags.values())} of "
              f"{len(COMPONENTS) * 3} variants; pass --allow-partial to build it anyway",
              file=sys.stderr)
        return 1
    out = pathlib.Path(a.out or ROOT / "docs" / "artifacts" / f"bsuk-{a.city}-component-canvas.html")
    page = render_page(frags, metas, tokens, final=a.final, inline=a.inline_images)
    if len(page.encode("utf-8")) > MAX_PAGE_BYTES:
        print(f"the page would be {len(page.encode('utf-8'))} bytes, over the 15 MB budget; "
              "publish with --files-map instead of --inline-images", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"{out} — {len(page.encode('utf-8'))} bytes, "
          f"{sum(len(v) for v in frags.values())} variants")
    if a.files_map:
        fm = files_map(frags)
        pathlib.Path(a.files_map).write_text(json.dumps(fm, indent=1) + "\n", encoding="utf-8")
        print(f"{a.files_map} — {len(fm)} images")
    return 0


if __name__ == "__main__":
    sys.exit(main())
