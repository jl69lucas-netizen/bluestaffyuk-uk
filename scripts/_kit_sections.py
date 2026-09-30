#!/usr/bin/env python3
"""_kit_sections.py — read `dist/kit-preview/index.html` once, for both artifact builders.

`scripts/build_design_canvas.py` cut the built preview route into Design-type artboards and
owned the section extraction, the CSS inlining and the asset rewriting. Task 22 needs the
same three things for the Design System's `components/<Comp>/preview.html` files, and a
second copy of a regex that has to agree with the Astro build byte for byte is a copy that
drifts the first time the build output changes. So they live here and both builders import
them; `build_design_canvas` re-exports the names its own test binds to.

What a "section" is: the preview route renders one `<section data-component="<id>"
data-width="<px>">` per row of `data/design/components.json`, plus one for the mark. The
section's inner HTML is the component as the build emits it — the same markup the render
harness asserts against — with its behaviour stripped out (see `find_sections`).

What a sprite is: `Mark.astro` is a `<use href="#bsuk-mark">` at a `<symbol>` pair that
`BaseLayout` emits ONCE per document, OUTSIDE every section. A preview document that carries
a section containing a `<use>` and not the sprite renders an empty box where the mark should
be, so `page_sprite()` lifts it and the callers paste it back in.
"""
import dataclasses
import re

#: The two Google-hosted families, at the weights the kit actually uses (Fraunces 600/700,
#: Source Sans 3 400/600). Both artifacts are read over the network, so the faces are linked
#: rather than embedded; `tokens.json` therefore carries `fonts: []` and names families only.
FONTS_LINK = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
              'family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Source+Sans+3:wght@400;600&display=swap">')

SEC = re.compile(r'<section([^>]*)data-component="([a-z-]+)"([^>]*)>(.*?)</section>', re.S)
WIDTH = re.compile(r'data-width="(\d+)"')
IMG_SRC = re.compile(r'(src|srcset)="([^"]+)"')
STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
SCRIPT = re.compile(r"<script\b[^>]*>.*?</script>", re.S)
#: The document sprite: the one `<svg>` that is hidden, aria-hidden and full of `<symbol>`s.
SPRITE = re.compile(r'(<svg\b[^>]*aria-hidden="true"[^>]*>\s*<symbol\b.*?</svg>)', re.S)
USE_HREF = re.compile(r'<use\b[^>]*href="#([A-Za-z0-9_-]+)"')


@dataclasses.dataclass
class Section:
    component: str
    width: int
    inner: str


def find_sections(html):
    """Every artboard section, with its behaviour stripped out.

    A component's own `<script>` — SiteHeaderKit's search pill is the first — is hoisted into
    the section by the build and points at a `/_astro/*.js` bundle. An artboard is a static
    rendering for the eye, served from an artifact where that bundle does not exist and where
    `/search-index.json` does not either, so the tag would be a 404 and nothing more. It is
    dropped here, once, so neither the artboard nor the missing-asset scan ever sees it."""
    out = []
    for m in SEC.finditer(html):
        attrs = m.group(1) + m.group(3)
        w = WIDTH.search(attrs)
        out.append(Section(m.group(2), int(w.group(1)) if w else 1280,
                           SCRIPT.sub("", m.group(4)).strip()))
    return out


#: The site's own `@font-face` rules (src/styles/fonts.css, Known Issue 24).
FONT_FACE = re.compile(r"@font-face\s*\{[^}]*\}")


def page_css(html):
    """Every inlined <style> block of the built page, in document order (@layer order matters).

    Astro inlines the built CSS, so there is no `dist/_astro/*.css` to link: the stylesheet
    for a rendering is the page's own style blocks pasted in the order they appear, which is
    the order the `@layer` cascade was written for.

    LESS THE SITE'S `@font-face` RULES. Every caller builds an Artifact (a board, the design
    canvas, the Design System) whose page links the same two families from Google Fonts
    (`FONTS_LINK`), and the site's `/fonts/…` URLs do not resolve there — a board's preview
    frames are sandboxed and have no origin at all — so a face that fails to load would stand in
    front of the linked one."""
    return "\n".join(FONT_FACE.sub("", m.group(1)).strip() for m in STYLE.finditer(html))


def page_sprite(html):
    """The document's `<symbol>` sprite, or "" when the page has none."""
    m = SPRITE.search(html)
    return m.group(1) if m else ""


def uses_sprite(inner):
    """True when this section references a `<symbol>` by id — i.e. it needs the sprite."""
    return bool(USE_HREF.search(inner))


def rewrite_assets(inner, assets):
    """Point every `src`/`srcset` at the artifact's own blob store.

    `assets` maps a built `/_astro/…` url to the `/_blob/<id>` the controller's upload
    produced. A url with no entry is left alone — the caller reports it as an upload to make
    rather than silently shipping a 404."""
    def sub(m):
        attr, val = m.group(1), m.group(2)
        if attr == "srcset":
            parts = []
            for cand in val.split(","):
                url, _, desc = cand.strip().partition(" ")
                parts.append((assets.get(url, url) + (" " + desc if desc else "")))
            return f'srcset="{", ".join(parts)}"'
        return f'{attr}="{assets.get(val, val)}"'
    return IMG_SRC.sub(sub, inner)


def section_image_urls(inner):
    """Every distinct image url a section references, srcset candidates unpacked."""
    urls = set()
    for m in IMG_SRC.finditer(inner):
        for cand in m.group(2).split(","):
            url = cand.strip().split(" ")[0]
            if url:
                urls.add(url)
    return urls
