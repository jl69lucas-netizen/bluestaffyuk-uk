"""The city components (the London component design pass, Plan 2): the `"project": 5` rows of
data/design/components.json, built from the user's frozen picks
(data/design/city-picks/blue-staffy-puppies-london.json) and previewed on /kit-preview/city/.

Kit convention 8 for the city set: one dist assertion per component on the built preview, plus
the shared contracts every one of them leans on — the face data that places every crop
(data/image-focus.json), served alts kept word for word (working rule 11), no inline style,
no hex, and the render spec's four widths.
"""
import json
import math
import pathlib
import re
import sys

import pytest
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from check_city_canvas import served_alts  # noqa: E402

COMPONENTS = ROOT / "data/design/components.json"
FOCUS = ROOT / "data/image-focus.json"
KIT_CSS = ROOT / "src/styles/kit.css"
KIT = ROOT / "src/components/kit"
PREVIEW = ROOT / "dist/kit-preview/city/index.html"
CONFIG = ROOT / "tests/render/city-kit.config.ts"


def city_rows():
    return [r for r in json.loads(COMPONENTS.read_text(encoding="utf-8")) if r["project"] == 5]


def focus_rows():
    return json.loads(FOCUS.read_text(encoding="utf-8"))["images"]


def built():
    if not PREVIEW.exists():
        pytest.skip("run npm run build first")
    return PREVIEW.read_text(encoding="utf-8")


def section(cid):
    """The built preview section for one city component. A registered component with no
    section is a failure, not a skip: that is what a route regression looks like."""
    html = built()
    start = html.find(f'data-component="{cid}"')
    assert start >= 0, f"/kit-preview/city/ has no section for {cid}"
    nxt = html.find('data-component="city-', start + 10)
    end = nxt if nxt >= 0 else html.find("</main>", start)
    return html[start:end]


def focus_point(file):
    """The Python twin of src/lib/imageFocus.ts focusPoint(): the centre of the faces' union,
    as whole percentages on the 5% grid."""
    row = focus_rows()[file]
    x0 = min(f[0] for f in row["faces"])
    y0 = min(f[1] for f in row["faces"])
    x1 = max(f[0] + f[2] for f in row["faces"])
    y1 = max(f[1] + f[3] for f in row["faces"])
    step = lambda n: min(100, max(0, int(math.floor(n / 5.0 + 0.5)) * 5))  # noqa: E731  (JS Math.round)
    return step(100 * (x0 + x1) / 2 / row["w"]), step(100 * (y0 + y1) / 2 / row["h"])


# --------------------------------------------------------------------------- the shared data

def test_every_city_row_is_a_kit_file_with_a_city_id():
    rows = city_rows()
    assert rows, "no project 5 rows in data/design/components.json"
    for r in rows:
        assert r["id"].startswith("city-"), r
        assert (ROOT / "src/components/kit" / r["file"]).is_file(), r


def test_the_face_data_names_real_masters_at_their_real_size():
    for name, row in focus_rows().items():
        path = ROOT / ("src/assets/puppies" if row["src"] == "puppies" else "public/images") / name
        assert path.is_file(), name
        assert Image.open(path).size == (row["w"], row["h"]), name
        assert row["faces"], f"{name}: a photo the city kit paints records at least one face"
        for x, y, w, h in row["faces"]:
            assert 0 <= x and 0 <= y and w > 0 and h > 0, name
            assert x + w <= row["w"] and y + h <= row["h"], f"{name}: a face runs off the master"


def test_a_served_photo_keeps_its_served_alt_and_its_baked_siblings():
    served = served_alts()
    for name, row in focus_rows().items():
        if row["src"] != "images":
            assert "alt" not in row, f"{name}: a puppy photo's alt is the component's, not a served one"
            continue
        assert row["alt"] in served.get(name, ()), f"{name}: alt is not the one the old site served"
        stem, ext = name.rsplit(".", 1)
        for w in row.get("widths", []):
            assert (ROOT / "public/images" / f"{stem}-{w}.{ext}").is_file(), (name, w)


def test_kit_css_has_a_focus_class_for_every_step():
    css = KIT_CSS.read_text(encoding="utf-8")
    assert ".focus { object-position: var(--fx, 50%) var(--fy, 50%); }" in css
    for n in range(0, 101, 5):
        assert f".fx-{n} {{ --fx: {n}%; }}" in css and f".fy-{n} {{ --fy: {n}%; }}" in css, n


def test_the_city_render_spec_paints_the_four_boundary_widths():
    got = {int(w) for w in re.findall(r"viewport:\s*\{\s*width:\s*(\d+)", CONFIG.read_text(encoding="utf-8"))}
    assert {375, 768, 1024, 1280} <= got, sorted(got)


# --------------------------------------------------------------------------- the built preview

def test_the_city_preview_is_noindex_and_carries_every_city_row_in_order():
    html = built()
    assert 'content="noindex, nofollow"' in html
    found = re.findall(r'<section[^>]*data-component="(city-[a-z-]+)"', html)
    assert found == [r["id"] for r in city_rows()], found


def test_no_city_section_writes_an_inline_style_or_a_hex():
    """plan2-notes: every inline `style=` of the canvas moved into classes or computed props;
    rule 1: no hex outside tokens.css."""
    for r in city_rows():
        s = section(r["id"])
        assert "style=" not in s, (r["id"], re.findall(r'style="[^"]*"', s)[:3])
        assert not re.findall(r"#[0-9A-Fa-f]{6}\b", s), r["id"]


def test_the_site_preview_carries_no_city_component():
    """The city nav set is a page singleton; /kit-preview/ keeps the site kit's."""
    site = ROOT / "dist/kit-preview/index.html"
    if not site.exists():
        pytest.skip("run npm run build first")
    assert 'data-component="city-' not in site.read_text(encoding="utf-8")


def test_built_city_hero_is_a_filmstrip_kit_hero_with_the_litter_first():
    s = section("city-hero")
    assert 'class="city-kit kit-hero city-hero' in s and 'data-hero-layout="filmstrip"' in s
    pups = [p for p in json.loads((ROOT / "data/puppies.json").read_text()) if p["status"] == "Available"]
    imgs = re.findall(r"<img [^>]*>", s)
    assert len(imgs) == len(pups), len(imgs)
    # rule 10: the strip (.pic) precedes the heading (.title) in source.
    assert s.find('class="pic') < s.find('class="title')
    for p, tag in zip(pups, imgs):
        x, y = focus_point(p["card_photo"])
        assert f"focus fx-{x} fy-{y}" in tag, (p["name"], tag)
        assert 'loading="eager"' in tag, p["name"]
    assert 'fetchpriority="high"' in imgs[0]
    assert s.count('fetchpriority="high"') == 1
    assert 'class="cta"' in s


def test_built_city_price_scale_reads_every_figure_from_the_data_files():
    s = section("city-price-scale")
    settings = json.loads((ROOT / "data/settings.json").read_text())
    prices = json.loads((ROOT / "data/price-matrix.json").read_text())
    count = sum(1 for p in json.loads((ROOT / "data/puppies.json").read_text()) if p["status"] == "Available")
    gbp = lambda n: "£{:,}".format(n)  # noqa: E731
    text = re.sub(r"<[^>]+>", " ", s)
    for figure in (str(count), f"{gbp(settings['delivery_min_gbp'])}–{gbp(settings['delivery_max_gbp'])}",
                   gbp(settings["deposit_gbp"]), gbp(prices["male_gbp"]), gbp(prices["female_gbp"])):
        assert figure in text, figure
    assert "data-counters" in s
    assert 3 <= s.count("data-figure") <= 6
    # The user's deposit ruling: never plainly "refundable".
    assert "refundable" not in text.lower()


def test_built_city_trust_ledger_keeps_its_served_photo_whole():
    s = section("city-trust-ledger")
    served = served_alts()
    photo = re.search(r'<img [^>]*src="/images/([^"]+)"[^>]*>', s)
    assert photo, "the ledger's photograph is a served /images/ file"
    alt = re.search(r'alt="([^"]*)"', photo.group(0)).group(1)
    assert alt.replace("&#39;", "'") in served[photo.group(1)]
    assert "srcset=" in photo.group(0) and 'loading="lazy"' in photo.group(0)
    assert 3 <= s.count("data-trust-item") <= 8
    assert s.count("<svg") == s.count("data-trust-item")
    assert "guarantee" not in s.lower(), "no guarantee length while guarantee_days is null"


def test_every_city_root_carries_the_city_type_base():
    """kit.css `.city-kit`: the headings and measures the canvas frames painted."""
    for r in city_rows():
        src = (KIT / r["file"]).read_text(encoding="utf-8")
        assert "class:list={['city-kit', " in src, r["file"]
    css = KIT_CSS.read_text(encoding="utf-8")
    assert ".city-kit :where(h1, h2, h3) { font-weight: 700; color: var(--color-brand); }" in css


def _demo_sections():
    """The ids the three nav demos name (CITY_DEMO_SECTIONS in _registry.ts)."""
    src = (KIT / "_registry.ts").read_text(encoding="utf-8")
    block = src.split("export const CITY_DEMO_SECTIONS", 1)[1].split("];", 1)[0]
    return re.findall(r"id: '([^']+)'", block)


@pytest.mark.parametrize("name", ["CityContents.astro", "CityDial.astro", "CityJumpBand.astro"])
def test_the_city_nav_set_marks_by_script_never_by_target_or_scroll_timeline(name):
    """plan2-notes: the canvas marked the current section with `:target` and scroll-driven
    animations (a reduced-motion reader saw section one stuck, learning loop L8); the kit marks
    it with src/lib/scrollSpy.ts. And no `!important` animation longhand is ever ported."""
    src = (KIT / name).read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/", "", re.sub(r"^\s*//.*$", "", src, flags=re.M), flags=re.S)
    # The one sanctioned `!important`: CityContents' <noscript> rule, which must beat the
    # phone rule it undoes for a reader with no scripting.
    code = code.replace("NOSCRIPT_CSS = '.city-contents [data-rest]{display:block!important}"
                        ".city-contents .more{display:none!important}'", "")
    for banned in (":target", "animation-timeline", "view-timeline", "timeline-scope", "!important"):
        assert banned not in code, (name, banned)


def test_built_city_contents_is_one_list_with_a_phone_disclosure():
    s = section("city-contents")
    ids = _demo_sections()
    hrefs = re.findall(r'<a href="#([^"]+)"', s)
    assert hrefs == ids, "one row per section, each once — no second copy for phones"
    assert s.count("<ul") == 1
    rest = len(re.findall(r"<li data-rest", s))
    assert rest == max(0, len(ids) - 5)
    if rest:
        m = re.search(r'<button[^>]*class="more"[^>]*>', s)
        assert m and 'aria-expanded="false"' in m.group(0)
        assert 'aria-controls="city-contents-list"' in m.group(0) and 'id="city-contents-list"' in s
    assert "<noscript>" in s, "a reader without scripting gets every row"


def test_built_city_dial_is_a_labelled_track_with_one_current_row():
    s = section("city-dial")
    assert "data-city-dial" in s
    assert 'aria-labelledby="city-dial-title"' in s and 'id="city-dial-title"' in s
    assert re.findall(r'data-spy="([^"]+)"', s) == _demo_sections()
    assert s.count('aria-current="location"') == 1
    assert 'aria-current=""' not in s


def test_built_city_jump_band_is_a_rail_and_a_native_dialog_sheet():
    s = section("city-jump-band")
    ids = _demo_sections()
    assert "<dialog" in s and 'aria-labelledby="city-jump-sheet-title"' in s
    key = re.search(r"<button[^>]*data-jump-open[^>]*>", s).group(0)
    assert 'aria-haspopup="dialog"' in key and 'aria-expanded="false"' in key
    assert "aria-label" not in key, "the key's name is its visible text (WCAG 2.5.3)"
    spies = re.findall(r'data-spy="([^"]+)"', s)
    assert spies == ids + ids, "one rail stop and one sheet row per section"
    assert s.count("<svg") >= len(ids)
    # The preview's band is a picture of the component, not this page's chrome.
    assert "data-strip" not in s
    src = (KIT / "CityJumpBand.astro").read_text(encoding="utf-8")
    assert "showModal()" in src and "addEventListener('close'" in src


def test_pageshell_swaps_the_nav_set_only_for_a_city_page():
    src = (ROOT / "src/layouts/PageShell.astro").read_text(encoding="utf-8")
    assert "cityNav" in src and "CityJumpBand" in src and "CityDial" in src and "CityContents" in src
    # The site pages never pass cityNav, so they still mount the kit's set.
    for page in (ROOT / "src/pages").rglob("*.astro"):
        if page.name != "blue-staffy-puppies-london.astro":
            assert "cityNav" not in page.read_text(encoding="utf-8"), page
