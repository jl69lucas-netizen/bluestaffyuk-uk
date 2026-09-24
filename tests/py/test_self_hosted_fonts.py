"""The picked families are self-hosted, and the built site loads them (Known Issue 24, user
ruling R3, 2026-09-23).

Until the project 5 readiness pass nothing under `src/` or `public/` requested a web font, so
the site rendered Fraunces and Source Sans 3 in their fallbacks (Georgia and `system-ui`)
while every board the breeder approved showed the real faces through Google Fonts.
`data/design/fonts.json` is the record of what is served: each file's path, the package and
version it was copied from, and its size and sha256, so a file that changes on disk fails
here rather than shipping. `src/styles/fonts.css` declares one `@font-face` per file, and
`BaseLayout` preloads the two latin files every page paints with.
"""
import hashlib
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "design" / "fonts.json"
FONTS_CSS = ROOT / "src" / "styles" / "fonts.css"
GLOBAL_CSS = ROOT / "src" / "styles" / "global.css"
TOKENS = ROOT / "src" / "styles" / "tokens.css"
BASE = ROOT / "src" / "layouts" / "BaseLayout.astro"
DIST = ROOT / "dist"
FACE = re.compile(r"@font-face\s*\{([^}]*)\}")


def manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def woff2_rows():
    return [f for f in manifest()["files"] if f["path"].endswith(".woff2")]


def url_of(row):
    """The URL a `public/` file is served at."""
    return "/" + row["path"].removeprefix("public/")


def faces():
    out = []
    for body in FACE.findall(FONTS_CSS.read_text(encoding="utf-8")):
        decl = dict((k.strip(), v.strip()) for k, v in
                    (d.split(":", 1) for d in body.split(";") if ":" in d))
        out.append(decl)
    return out


def test_every_served_font_file_is_the_one_the_manifest_records():
    rows = manifest()["files"]
    assert len(woff2_rows()) == 4 and len(rows) == 6, [r["path"] for r in rows]
    for r in rows:
        f = ROOT / r["path"]
        assert f.is_file(), r["path"]
        data = f.read_bytes()
        assert len(data) == r["bytes"], (r["path"], len(data))
        assert hashlib.sha256(data).hexdigest() == r["sha256"], r["path"]
    for r in woff2_rows():
        assert (ROOT / r["path"]).read_bytes()[:4] == b"wOF2", r["path"]


def test_the_two_families_are_the_tokens_first_choices():
    tokens = TOKENS.read_text(encoding="utf-8")
    first = {k: re.search(r"--font-%s:\s*\"([^\"]+)\"" % k, tokens).group(1)
             for k in ("display", "body")}
    assert first == {"display": "Fraunces", "body": "Source Sans 3"}
    assert {f["font-family"].strip("\"'") for f in faces()} == set(first.values())
    assert {r["family"] for r in woff2_rows()} == set(first.values())


def test_fonts_css_declares_each_file_once_and_swaps():
    declared = []
    for f in faces():
        assert f.get("font-display") == "swap", f
        assert f.get("unicode-range"), f
        assert f.get("font-style") == "normal", f
        urls = re.findall(r"url\(\s*[\"']?([^\"')]+)", f["src"])
        assert len(urls) == 1 and "format(\"woff2" in f["src"], f
        declared += urls
    assert sorted(declared) == sorted(url_of(r) for r in woff2_rows())


def test_every_layout_imports_the_faces():
    assert re.search(r'^@import "\./fonts\.css";', GLOBAL_CSS.read_text(encoding="utf-8"), re.M)
    assert "import '../styles/global.css';" in BASE.read_text(encoding="utf-8")


def test_base_layout_preloads_exactly_the_two_latin_files():
    base = BASE.read_text(encoding="utf-8")
    preloads = re.findall(r'<link rel="preload" href="([^"]+)" as="font" type="font/woff2" crossorigin />', base)
    want = sorted(url_of(r) for r in woff2_rows() if r["preload"])
    assert len(want) == 2 and all("-latin-" in u and "-latin-ext-" not in u for u in want)
    assert sorted(preloads) == want
    assert base.count('rel="preload"') == 2, "no other font may be preloaded"


def _built_pages():
    if not (DIST / "index.html").is_file():
        pytest.skip("run npm run build first")
    return sorted(DIST.rglob("*.html"))


def test_the_built_site_serves_its_own_fonts_and_asks_google_for_none():
    pages = _built_pages()
    rows = woff2_rows()
    for r in rows:
        built = DIST / r["path"].removeprefix("public/")
        assert built.is_file() and built.read_bytes() == (ROOT / r["path"]).read_bytes(), r["path"]
    # Astro inlines the stylesheet into each page today; a bundled `_astro/*.css` counts too,
    # so the test survives the build switching between the two.
    bundled = "".join(p.read_text(encoding="utf-8") for p in (DIST / "_astro").glob("*.css"))
    preloads = [url_of(r) for r in rows if r["preload"]]
    with_layout = 0
    for p in pages:
        html = p.read_text(encoding="utf-8", errors="replace")
        assert "fonts.googleapis.com" not in html and "fonts.gstatic.com" not in html, p
        if 'rel="icon" href="/favicon.svg"' in html:          # every BaseLayout page
            with_layout += 1
            for u in preloads:
                assert f'<link rel="preload" href="{u}" as="font" type="font/woff2" crossorigin>' in html, (p, u)
            for r in rows:
                assert f"url({url_of(r)})" in html + bundled, (p, r["path"], "no @font-face")
    assert with_layout >= 50, with_layout


def test_the_artifact_builders_leave_the_self_hosted_faces_out():
    """Boards, the design canvas and the Design System are Artifacts built from the page's own
    stylesheet (`page_css()`), and each links the same two families from Google Fonts. A
    `/fonts/…` URL does not resolve on an Artifact — a board's preview frames are sandboxed and
    have no origin at all — so the site's `@font-face` rules are left out of what they are
    handed: kept, a face that fails to load could stand in front of the linked one."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import _kit_sections as K
    html = ("<style>@font-face{font-family:Fraunces;src:url(/fonts/a.woff2)format(\"woff2\")}"
            ".a{color:red}</style><style>@layer x{.b{margin:0}}</style>")
    css = K.page_css(html)
    assert "@font-face" not in css and "/fonts/" not in css
    assert ".a{color:red}" in css and "@layer x{.b{margin:0}}" in css
    for board in sorted((ROOT / "docs" / "artifacts" / "boards").glob("*.html")):
        assert "url(/fonts/" not in board.read_text(encoding="utf-8"), board.name
