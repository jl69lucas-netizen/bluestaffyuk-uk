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


def city_of(row):
    """The city a city row was built for: its `canvas_variant`'s city. London's rows predate the
    field (the Manchester page run back-fills them in Phase F Task 32, gap G10), so a row with
    none is London's."""
    return row.get("canvas_variant", "london/").split("/", 1)[0]


def city_rows():
    """London's city rows: this file holds London's components and /kit-preview/city/.
    Manchester's own are held by tests/py/test_city_kit_manchester.py on /kit-preview/city-manchester/."""
    return [r for r in json.loads(COMPONENTS.read_text(encoding="utf-8"))
            if r["project"] == 5 and city_of(r) == "london"]


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


def test_every_puppy_photo_a_city_component_may_paint_records_its_face():
    """Task 7b review, item 9: a puppy photo without a face box is one img-face-visible cannot
    examine. Every card and gallery photo in data/puppies.json is one a city component may paint
    (the litter wall's gallery choice, plan2-notes Task 7), so each carries its face and scene."""
    rows = focus_rows()
    for pup in json.loads((ROOT / "data/puppies.json").read_text()):
        for name in {pup["card_photo"], *pup.get("gallery", [])}:
            assert name in rows, f"data/image-focus.json has no face box for {name}"
            assert rows[name]["src"] == "puppies" and rows[name]["scene"], name
    scenes = [r["scene"] for r in rows.values() if r["src"] == "puppies"]
    assert len(scenes) == len(set(scenes)), "two puppy photos share a scene, so puppyAlt() would repeat"


def test_a_served_photo_keeps_its_served_alt_and_its_baked_siblings():
    served = served_alts()
    for name, row in focus_rows().items():
        if row["src"] != "images":
            assert "alt" not in row, f"{name}: a puppy photo's alt is the component's, not a served one"
            continue
        if "published" in row:
            # A file this rebuild published (an Asset Gate's), not one the old site served: no served
            # alt to keep, so it carries none, and the record that approved it must exist.
            assert "alt" not in row and name not in served, f"{name}: a published file carries no served alt"
            assert (ROOT / row["published"]).is_file(), (name, row["published"])
        else:
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
    s = section("city-hero-filmstrip")
    assert 'class="city-kit kit-hero city-hero-filmstrip' in s and 'data-hero-layout="filmstrip"' in s
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


def test_the_city_kit_reads_the_refund_clause_from_the_data_and_never_types_it():
    """The Task 7b review (item 6) kept a refund helper out of src/lib/cityKit.ts while the wording
    was being settled on another branch: a helper with no wording behind it was dead code. The
    wording landed as data/settings.json `deposit_refund_clause` (2026-09-30), and Manchester's
    deposit section prints it (Phase F ruling 10; outline row 8; Task 30). So the kit may carry ONE
    helper, `refundClause`, that reads that key and types none of its words, and a city component
    must use it (no dead helper)."""
    src = (ROOT / "src/lib/cityKit.ts").read_text(encoding="utf-8")
    clause = json.loads((ROOT / "data/settings.json").read_text())["deposit_refund_clause"]
    assert "depositRefundClause" not in src
    assert "deposit_refund_clause: string }).deposit_refund_clause" in src, "the clause is read from data/settings.json"
    code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith(("//", "*", "/*")))
    for words in (clause, clause[:20], "70%", "1 day before"):
        assert words not in code, f"cityKit types the clause's words: {words!r}"
    users = [f.name for f in (ROOT / "src").rglob("*.ts*") if "refundClause(" in f.read_text(encoding="utf-8") and f.name != "cityKit.ts"]
    users += [f.name for f in (ROOT / "src").rglob("*.astro") if "refundClause(" in f.read_text(encoding="utf-8")]
    assert "refundClause(" in src.split("export function refundClause", 1)[1] or users, "a helper nobody calls is dead code"


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
    # The guarantee is the breeder's answer (answer board q07, 2026-09-29): two years. It is
    # printed from data/settings.json, once, as one of the ledger's claims.
    g = guarantee()
    assert _text(s).count(g["guarantee_label"]) == 1, "the trust ledger prints the guarantee from the data, once"
    assert "-day guarantee" not in s


def guarantee():
    """data/settings.json's guarantee (answer board q07, 2026-09-29): 730 days, worded as the
    site words a guarantee elsewhere (a "health guarantee", data/faq.json home-health-guarantee;
    the site never names what it covers, so no "genetic")."""
    s = json.loads((ROOT / "data/settings.json").read_text())
    assert s["guarantee_days"] == 730
    assert s["guarantee_label"] == "Two-year health guarantee"
    assert s["guarantee_note"]
    return s


CITY_CSS = ROOT / "src/styles/city.css"


def test_every_city_root_carries_the_city_type_base():
    """src/styles/city.css `.city-kit`: the headings and measures the canvas frames painted,
    imported by every city component and by the city layout, and by nothing site-wide (I2)."""
    for r in city_rows():
        src = (KIT / r["file"]).read_text(encoding="utf-8")
        assert "class:list={['city-kit', " in src, r["file"]
        assert "import '../../styles/city.css';" in src.split("---", 2)[1], r["file"]
    assert "import '../styles/city.css';" in (ROOT / "src/layouts/CityShell.astro").read_text(encoding="utf-8")
    css = CITY_CSS.read_text(encoding="utf-8")
    assert ".city-kit :where(h1, h2, h3) { font-weight: 700; color: var(--color-brand); }" in css
    for shared in (KIT_CSS, ROOT / "src/styles/global.css", ROOT / "src/styles/tokens.css"):
        text = re.sub(r"/\*.*?\*/", "", shared.read_text(encoding="utf-8"), flags=re.S)
        # global.css names `.city-kit` once, inside the reading-link rule's `:not()` exclusion,
        # which leaves the city kit out (2026-10-04); no city RULE may live there.
        assert ".city-kit" not in _city_rules_outside_exclusions(text, _board_styles_city_exclusions()), shared.name
        assert "--city-" not in text, shared.name


def _ts_const(name):
    src = (ROOT / "src/lib/cityKit.ts").read_text(encoding="utf-8")
    return int(re.search(rf"export const {name} = (\d+);", src).group(1))


def _px_token(css, token):
    tokens = (ROOT / "src/styles/tokens.css").read_text(encoding="utf-8")
    m = re.search(rf"{re.escape(token)}:\s*(\d+)px", css) or re.search(rf"{re.escape(token)}:\s*(\d+)px", tokens)
    return int(m.group(1))


def test_the_city_geometry_constants_equal_their_css():
    """M3: cityKit's DIAL_W, SHELL_GUTTER, DIAL_GAP and CONTAINER are the CSS values the layout
    paints with; the column in every `sizes` is derived from them."""
    city = CITY_CSS.read_text(encoding="utf-8")
    glob_css = (ROOT / "src/styles/global.css").read_text(encoding="utf-8")
    shell = (ROOT / "src/layouts/PageShell.astro").read_text(encoding="utf-8")
    own = shell.split(".page-shell.has-own-dial {", 1)[1].split("}", 1)[0]
    gutter = re.search(r"padding-inline: var\((--space-\d+)\)", own).group(1)
    gap = re.search(r"gap: var\((--space-\d+)\)", own).group(1)
    assert _px_token(city, "--city-dial-w") == _ts_const("DIAL_W")
    assert _px_token(glob_css, "--container") == _ts_const("CONTAINER")
    assert _px_token("", gutter) == _ts_const("SHELL_GUTTER")
    assert _px_token("", gap) == _ts_const("DIAL_GAP")
    assert re.search(r"@media \(min-width: (\d+)px\)[^{]*\{\s*\.page-shell\.has-own-dial", shell).group(1) == str(_ts_const("DIAL_FROM"))


def test_one_pair_of_tier_edges_for_type_and_layout():
    """I4: type and layout switch at the same two edges of the section's own box, cityKit TIER,
    mirrored in city.css; container-type is declared once, in city.css (M4); every query uses
    range syntax (M2); the tier custom properties sit on `.city-kit > *` (M5)."""
    src = (ROOT / "src/lib/cityKit.ts").read_text(encoding="utf-8")
    tier = dict(re.findall(r"(tablet|desktop): (\d+)", re.search(r"export const TIER = \{([^}]*)\}", src).group(1)))
    edges = {int(tier["tablet"]), int(tier["desktop"])}
    city = CITY_CSS.read_text(encoding="utf-8")
    assert set(int(x) for x in re.findall(r"@container \(width >= (\d+)px\)", city)) == edges
    assert "phone    width < 640px" in city and "tablet   640px <= width < 800px" in city
    assert ".city-kit > * {" in city and ".city-kit * {" not in city
    assert city.count("container-type: inline-size") == 1
    # Named sub-steps inside a tier (each documented where it is written).
    SUB_STEPS = {("CityChapters.astro", 1000)}
    for r in city_rows():
        text = (KIT / r["file"]).read_text(encoding="utf-8")
        css = text.split("<style>", 1)[1]
        assert "container-type" not in css, r["file"]
        assert not re.search(r"@(container|media)[^{]*\((min|max)-width", css), f"{r['file']}: not range syntax"
        for n in re.findall(r"@container \(([^)]*)\)", css):
            for px in (int(x) for x in re.findall(r"(\d+)px", n)):
                assert px in edges or (r["file"], px) in SUB_STEPS, (r["file"], n)


def _demo_sections():
    """The ids the three nav demos name (CITY_DEMO_SECTIONS in _registry.ts)."""
    src = (KIT / "_registry.ts").read_text(encoding="utf-8")
    block = src.split("export const CITY_DEMO_SECTIONS", 1)[1].split("];", 1)[0]
    return re.findall(r"id: '([^']+)'", block)


@pytest.mark.parametrize("name", ["CityContentsPhotoIndex.astro", "CityDialPhotoMarker.astro", "CityJumpStepper.astro"])
def test_the_city_nav_set_marks_by_script_never_by_target_or_scroll_timeline(name):
    """plan2-notes: the canvas marked the current section with `:target` and scroll-driven
    animations (a reduced-motion reader saw section one stuck, learning loop L8); the kit marks
    it with src/lib/scrollSpy.ts. And no `!important` animation longhand is ever ported."""
    src = (KIT / name).read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/", "", re.sub(r"^\s*//.*$", "", src, flags=re.M), flags=re.S)
    # The one sanctioned `!important`: CityContentsPhotoIndex' <noscript> rule, which must beat the
    # phone rule it undoes for a reader with no scripting.
    code = code.replace("NOSCRIPT_CSS = '.city-contents-photo-index [data-rest]{display:block!important}"
                        ".city-contents-photo-index .more{display:none!important}'", "")
    for banned in (":target", "animation-timeline", "view-timeline", "timeline-scope", "!important"):
        assert banned not in code, (name, banned)


def test_built_city_contents_is_one_list_with_a_phone_disclosure():
    s = section("city-contents-photo-index")
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
    s = section("city-dial-photo-marker")
    assert "data-city-dial-photo-marker" in s
    assert 'aria-labelledby="city-dial-title"' in s and 'id="city-dial-title"' in s
    assert re.findall(r'data-spy="([^"]+)"', s) == _demo_sections()
    assert s.count('aria-current="location"') == 1
    assert 'aria-current=""' not in s


def test_built_city_jump_band_is_a_rail_and_a_native_dialog_sheet():
    s = section("city-jump-stepper")
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
    src = (KIT / "CityJumpStepper.astro").read_text(encoding="utf-8")
    assert "showModal()" in src and "addEventListener('close'" in src


CITY_NAV_ROOTS = ("city-contents-photo-index", "city-dial-photo-marker", "city-jump-stepper")


def test_the_nav_set_is_pluggable_and_pageshell_carries_no_city_pick():
    """Task 7b review, items 4 and 5. PageShell names no city component: a page's own nav set
    comes in through three named slots (`nav-bar`, `nav-contents`, `nav-dial`), and the city
    layout (src/layouts/CityShell.astro) fills them from the components a city page passes it,
    so the next city mounts different picks without an edit to PageShell or CityShell."""
    shell = (ROOT / "src/layouts/PageShell.astro").read_text(encoding="utf-8")
    code = shell.split("---", 2)[1]
    assert not re.search(r"import\s+City\w+", code), "PageShell imports a city component"
    assert "cityNav" not in shell
    for name in ("nav-bar", "nav-contents", "nav-dial"):
        assert f'<slot name="{name}"' in shell, name
    city = (ROOT / "src/layouts/CityShell.astro").read_text(encoding="utf-8")
    ccode = city.split("---", 2)[1]
    assert "import PageShell" in ccode
    assert not re.search(r"import\s+City\w+", ccode), "CityShell names a city's picks"
    for name in ("nav-bar", "nav-contents", "nav-dial"):
        assert f'slot="{name}"' in city, name
    # No site page mounts the city layout or names a city nav pick (London arrives in Task 8).
    for page in (ROOT / "src/pages").rglob("*.astro"):
        if "kit-preview" in page.parts or page.name == "blue-staffy-puppies-london.astro":
            continue
        text = page.read_text(encoding="utf-8")
        assert "CityShell" not in text and "slot=\"nav-dial\"" not in text, page


def _norm_selector(text):
    """Selector text as the minifier and the source can both be compared: no quotes, no spaces."""
    return re.sub(r"[\s\"']", "", text)


def _not_groups(css):
    """Every `:not(...)` group in `css`, balanced over nested parentheses, in source order."""
    out, i = [], 0
    while (i := css.find(":not(", i)) != -1:
        depth, j = 0, i + 4
        while j < len(css):
            depth += {"(": 1, ")": -1}.get(css[j], 0)
            if depth == 0:
                break
            j += 1
        out.append(css[i:j + 1])
        i += 5
    return out


def _board_styles_city_exclusions():
    """The exact `:not()` groups the site-wide sheets write to leave the city kit alone: in
    src/styles/board-styles.css, the body-heading scale and the gutter rule (Known Issue 97); in
    src/styles/global.css, the reading-link underline's general selector (answer board 2026-10-03
    q01, whose city half lives in src/styles/city.css). Each names `.city-kit` and is an
    exclusion, not a city rule."""
    out = set()
    for sheet in ("board-styles.css", "global.css"):
        src = re.sub(r"/\*.*?\*/", "", (ROOT / "src/styles" / sheet).read_text(encoding="utf-8"), flags=re.S)
        out |= {_norm_selector(g) for g in _not_groups(src) if ".city-kit" in g and ":not(:not(" not in g}
    return out


def _city_rules_outside_exclusions(css, exclusions):
    """`css` normalised, with ONLY the listed exclusion groups blanked, and only where a group is
    not itself negated again (`:not(:not(.city-kit *))` selects city headings, so it is kept)."""
    css = _norm_selector(css)
    for g in sorted(exclusions, key=len, reverse=True):
        parts = css.split(g)
        kept = parts[0]
        for part in parts[1:]:
            kept += (g if kept.endswith(":not(") else ":not()") + part
        css = kept
    return css


def test_the_city_exclusion_filter_blanks_only_the_exact_groups():
    """Mutation proof for the guard below (the Known Issue 97 review, item 9)."""
    groups = _board_styles_city_exclusions()
    assert groups, "board-styles.css names no .city-kit exclusion, so this filter guards nothing"
    # As the minifier emits the body-heading scale's H2 rule (quotes dropped where it can).
    real = 'main :where(h2:not(.bl-box h2,[class^=kit-] *,[class*=" kit-"] *,.city-kit *)){font-size:22px}'
    assert ".city-kit" not in _city_rules_outside_exclusions(real, groups)
    for mutant in (
        "main h2:not(:not(.city-kit *)){color:red}",
        ".city-kit h2{color:red}",
        'main :where(h2:not(:not(.bl-box h2,[class^=kit-] *,[class*=" kit-"] *,.city-kit *))){color:red}',
        "main :where(h2:not(.city-kit *)){color:red}",
    ):
        assert ".city-kit" in _city_rules_outside_exclusions(mutant, groups), mutant


def test_the_built_pages_ship_none_of_the_city_nav_css():
    """Task 7b review, item 5: with the picks out of PageShell, Astro bundles their CSS only
    where a page imports them. The twelve built pages carry no rule of the city nav set, and no
    rule or token of the city type scale either (the Task 7b quality review, I2)."""
    from _slugs import resolve_page
    rebuilt = json.loads((ROOT / "data/facts/rebuilt.json").read_text())
    exclusions = _board_styles_city_exclusions()
    # A rebuilt CITY page (London, the thirteenth) mounts the city kit, so it ships city CSS by
    # design. Its key is the bare slug and its route is uk-locations/<slug> (scripts/_slugs.py):
    # read as dist/<key>/ it was never found, and the skip below hid every page after it.
    pages = [(k, r) for k in rebuilt for r in [resolve_page(k, ROOT)[1]] if not r.startswith("uk-locations/")]
    assert len(pages) >= 12, pages
    for slug, route in pages:
        path = ROOT / "dist" / (f"{route}/index.html" if route else "index.html")
        if not path.exists():
            pytest.skip("run npm run build first")
        css = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", path.read_text(encoding="utf-8"), re.S))
        assert len(css) > 10_000, f"{slug}: collected no page CSS, so nothing was checked"
        for root in CITY_NAV_ROOTS:
            assert f".{root}" not in css, (slug, root)
        # Nor the city type base and scale, nor the dial token (src/styles/city.css: I2). A
        # `.city-kit` inside one of board-styles.css's own exclusion groups is not a city rule
        # (Known Issue 97); only those exact groups are blanked before the search.
        assert ".city-kit" not in _city_rules_outside_exclusions(css, exclusions), slug
        assert "--city-" not in css, slug


# --------------------------------------------------------------------------- Task 4

def _available():
    return [p for p in json.loads((ROOT / "data/puppies.json").read_text()) if p["status"] == "Available"]


def test_built_city_takeaways_is_a_ruled_ledger_with_a_served_photo():
    s = section("city-takeaways-ledger")
    assert 3 <= s.count("data-takeaway") <= 6
    assert s.count("<dt") == s.count("data-takeaway") == s.count("<dd")
    src = re.search(r'<img [^>]*src="/images/([^"]+)"[^>]*>', s)
    alt = re.search(r'alt="([^"]*)"', src.group(0)).group(1)
    assert alt in served_alts()[src.group(1)]
    # The photo is first in source: a phone meets it before the facts.
    assert s.find("<img") < s.find("<h2")
    # One row is the guarantee, printed from data/settings.json (answer board q07).
    assert _text(s).count(guarantee()["guarantee_label"]) == 1


def test_built_city_puppy_sheet_prints_every_available_puppy_from_the_data():
    s = section("city-puppy-sheet")
    pups = _available()
    arts = re.findall(r'<article[^>]*class="city-pup[^"]*"[^>]*>(.*?)</article>', s, re.S)
    assert len(arts) == len(pups)
    for p, a in zip(pups, arts):
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a))
        assert p["name"] in text and "£{:,}".format(p["price_gbp"]) in text, p["name"]
        assert ("Boy" if p["sex"] == "male" else "Girl") in text and p["colour"] in text
        hrefs = re.findall(r'href="([^"]+)"', a)
        assert hrefs == [f"/available-puppies/{p['slug']}/"], "one link per print, to the puppy's page"
        assert f"Ask About {p['name']}" in text
        assert "focus fx-" in a
    assert "books your viewing and reserves your puppy" in s


def test_built_city_roster_is_a_semantic_table_that_stacks():
    s = section("city-roster")
    table = re.search(r"<table[^>]*>(.*?)</table>", s, re.S)
    assert 'class="stack-table' in re.search(r"<table[^>]*>", s).group(0)
    body = table.group(1)
    assert "<caption" in body
    assert body.count('scope="col"') == 5
    assert body.count('scope="row"') == len(_available())
    tds = re.findall(r"<td[^>]*>", body)
    assert tds and all('data-label="' in td for td in tds)
    text = re.sub(r"<[^>]+>", " ", body)
    for p in _available():
        assert p["name"] in text and "£{:,}".format(p["price_gbp"]) in text


# --------------------------------------------------------------------------- Task 5

def test_built_city_video_panel_is_a_facade_on_a_site_video_id():
    s = section("city-video-panel")
    ids = json.loads((ROOT / "data/settings.json").read_text())["youtube_embeds"]
    found = set(re.findall(r"youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]{6,})", s))
    assert found and found <= set(ids), found
    btn = re.search(r"<button[^>]*data-video-play[^>]*>", s).group(0)
    assert 'aria-label="Play the film: ' in btn, "the visible chip text starts the accessible name"
    assert "<noscript>" in s, "the no-JS player stays"
    assert "iframe" in s.split("<noscript>", 1)[1]
    # The poster is decorative (the button names the video); the side photo is described.
    poster = re.search(r"<button[^>]*data-video-play[^>]*>\s*<img [^>]*>", s).group(0)
    assert re.search(r'\balt(="")?[\s>]', poster)
    assert "focus fx-" in poster


def test_the_video_embed_poster_and_label_are_opt_in():
    """The two new VideoEmbed props change nothing for a caller that passes neither: the kit
    preview's facade still shows YouTube's thumbnail and the unlabelled round badge."""
    site = ROOT / "dist/kit-preview/index.html"
    if not site.exists():
        pytest.skip("run npm run build first")
    html = site.read_text(encoding="utf-8")
    start = html.find('data-component="video-embed"')
    kit = html[start:html.find("</section>", start)]
    assert "i.ytimg.com" in kit or "img.youtube.com" in kit
    assert 'aria-label="Play the video: ' in kit and "data-play-label" not in kit


def test_the_city_letter_sizes_its_photo_from_the_photos_own_record():
    """Task 7b review, item 8: the letter's photograph takes its box and its `sizes` from the
    photo's own width and height (data/image-focus.json through servedPhoto()), never from
    numbers fitted to Mark's photo, so another city's letter can pin any served photo."""
    src = (KIT / "CityLetter.astro").read_text(encoding="utf-8")
    assert "319" not in src and "213" not in src
    assert "${p.w}px" in src
    s = section("city-letter")
    img = re.search(r'<img [^>]*src="/images/([^"]+)"[^>]*>', s)
    row = focus_rows()[img.group(1)]
    assert f'width="{row["w"]}"' in img.group(0) and f'height="{row["h"]}"' in img.group(0)
    assert f'{row["w"]}px' in re.search(r'sizes="([^"]*)"', img.group(0)).group(1)


def test_built_city_chapters_put_each_photo_straight_after_its_heading():
    s = section("city-chapters")
    blocks = re.findall(r"<h3[^>]*>.*?</h3>\s*(<img [^>]*>)", s, re.S)
    assert 1 <= len(blocks) <= 2 and len(blocks) == s.count("<h3")
    for img in blocks:
        assert re.search(r'class="[^"]*\bbl-img\b', img), img
    served = served_alts()
    for src, alt in re.findall(r'<img [^>]*src="/images/([^"]+)"[^>]*alt="([^"]*)"', s):
        assert alt in served[src], src


def test_built_city_letter_quotes_its_review_word_for_word():
    s = section("city-letter")
    reviews = json.loads((ROOT / "data/reviews.json").read_text())
    n = int(re.search(r'data-review="(\d+)"', s).group(1))
    import html as _h
    block = re.search(r"<blockquote[^>]*>(.*?)</blockquote>", s, re.S).group(1)
    paras = [_h.unescape(x) for x in re.findall(r"<p[^>]*>(.*?)</p>", block, re.S)]
    # Word for word and in order: the paragraphs rejoined at single spaces ARE the data's quote
    # (the Task 7b review: split at sentence breaks so no paragraph breaks the line caps).
    assert " ".join(paras) == reviews[n]["quote"]
    assert len(paras) > 1, "the review is split at its sentence breaks"
    for para in paras:
        assert _ends_a_sentence(para), f"a paragraph ends mid-sentence: {para!r}"
    assert reviews[n]["name"] in s
    assert "AggregateRating" not in s and "★" not in s


_ABBREV = ("Mr.", "Mrs.", "Ms.", "Dr.", "St.", "Mt.", "No.", "vs.", "etc.", "e.g.", "i.e.")


def _ends_a_sentence(text):
    """A sentence end: . ! or ? with an optional closing quote, and never an abbreviation."""
    return bool(re.search(r"[.!?][\"”’']?$", text)) and not text.endswith(_ABBREV)


def run_split_review(tmp_path, cases):
    """[(quote, max_chars)] -> [paragraphs] from the compiled src/lib/cityKit.ts splitReview()."""
    import json as _json, shutil, subprocess
    esbuild, node = ROOT / "node_modules/.bin/esbuild", shutil.which("node")
    if not esbuild.exists() or not node:
        pytest.skip("needs node and node_modules/.bin/esbuild (npm install)")
    out = tmp_path / "cityKit.mjs"
    subprocess.run([str(esbuild), str(ROOT / "src/lib/cityKit.ts"), "--bundle", "--format=esm",
                    "--platform=node", "--define:import.meta.env={}", f"--outfile={out}", "--log-level=error"], check=True)
    driver = (f"const m = await import({_json.dumps(out.as_uri())});"
              f"console.log(JSON.stringify({_json.dumps(cases)}.map(([q, n]) => m.splitReview(q, n))));")
    res = subprocess.run([node, "--input-type=module", "-e", driver], check=True, capture_output=True, text=True)
    return _json.loads(res.stdout)


def test_split_review_breaks_only_at_real_sentence_ends(tmp_path):
    """M1: CityLetter's splitter is cityKit.splitReview(quote, maxChars). It joins sentences while a
    paragraph stays within maxChars, keeps every word in order, never splits after an
    abbreviation or inside a decimal, splits after a closing quote and after an ellipsis that ends
    a sentence, and never cuts a single sentence longer than maxChars."""
    long_one = "We " + "really " * 40 + "loved him."
    cases = [
        ("We met Mr. Bright and Dr. Jones at St. Mary's. They were kind.", 60),
        ("It cost £1.5k all in, vs. £2k elsewhere. Worth it.", 30),
        ('He said "we love him." Then we left.', 25),
        ("We waited... It was worth it. And then... we smiled.", 20),
        (long_one, 200),
        ("One. Two. Three.", 200),
    ]
    got = run_split_review(tmp_path, cases)
    assert got[0] == ["We met Mr. Bright and Dr. Jones at St. Mary's.", "They were kind."]
    assert got[1] == ["It cost £1.5k all in, vs. £2k elsewhere.", "Worth it."]
    assert got[2] == ['He said "we love him."', "Then we left."]
    assert got[3] == ["We waited...", "It was worth it.", "And then... we smiled."]
    assert got[4] == [long_one], "a sentence over the limit is kept whole, never cut"
    assert got[5] == ["One. Two. Three."]
    for (quote, _), paras in zip(cases, got):
        assert " ".join(paras) == quote
        assert all(_ends_a_sentence(p) for p in paras), paras


# --------------------------------------------------------------------------- Task 6

def _text(fragment):
    import html as _h
    return re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def test_built_city_faq_ledger_blocks_number_on_and_carry_one_rail():
    s = section("city-faq-ledger")
    blocks = re.findall(r'data-faq-block="([a-z-]+)"', s)
    assert len(blocks) == 3 and len(set(blocks)) == 3
    nums = [int(n) for n in re.findall(r'<span class="n"[^>]*>(\d+)</span>', s)]
    assert nums == list(range(1, len(nums) + 1)), nums
    # The user's ruling for a city page's FAQ: three blocks, 15 to 20 questions.
    assert 15 <= len(nums) <= 20, len(nums)
    assert s.count('class="rail"') == 1, "the rail goes with the top block only"
    qs = re.findall(r"<summary[^>]*>.*?<h3[^>]*data-faq-q[^>]*>(.*?)</h3>.*?</summary>", s, re.S)
    assert len(qs) == len(nums)
    # Title Case at render, as Faq.astro does (rules/headings.md).
    assert all(q[0].isupper() for q in qs)
    # The guarantee is printed once, in the rail's brief, from data/settings.json (q07).
    g = guarantee()
    assert _text(s).count(g["guarantee_label"]) == 1
    assert "-day guarantee" not in s and "genetic" not in s.lower()
    # No licence detail, no refund clause, and the rail's served photo keeps its served alt.
    assert "licen" not in s.lower() and "refund" not in s.lower()
    src = re.search(r'<img [^>]*src="/images/([^"]+)"[^>]*>', s)
    assert re.search(r'alt="([^"]*)"', src.group(0)).group(1) in served_alts()[src.group(1)]


def test_the_faq_rail_prints_its_facts_from_the_one_source():
    """Task 7b review, item 7: the rail's brief types no fact beside src/lib/cityKit.ts. The
    deposit phrase and the transport line are cityKit exports (the transport from
    data/settings.json `delivery_note`), and the guarantee row is `guaranteeRow()`, which prints
    only what data/settings.json holds (`guarantee_label`, `guarantee_note`), never wording of its own."""
    src = (KIT / "CityFaqLedger.astro").read_text(encoding="utf-8")
    code = src.split("---", 2)[1]
    for literal in ("DEFRA", "Books your viewing", "genetic", "-day guarantee"):
        assert literal not in code, literal
    for name in ("depositBrief", "transportLine", "guaranteeRow"):
        assert name in code, name
    kit = (ROOT / "src/lib/cityKit.ts").read_text(encoding="utf-8")
    assert "delivery_note" in kit and "guarantee_note" in kit
    settings = json.loads((ROOT / "data/settings.json").read_text())
    rail = _text(section("city-faq-ledger").split('class="rail"', 1)[1].split("</dl>", 1)[0])
    assert "By DEFRA-approved transport, priced by distance." in rail
    assert settings["delivery_note"].endswith("by DEFRA-approved transport, priced by distance")
    assert "Books your viewing and reserves your puppy, and it comes off the price." in rail
    g = guarantee()
    assert g["guarantee_label"] in rail and g["guarantee_note"] in rail


def test_no_heading_on_the_city_preview_repeats_an_faq_question():
    """plan2-notes (from the Task 9 review): no real section heading may repeat an FAQ question."""
    html = built()
    faq = {_text(q).lower() for q in re.findall(r"<h3[^>]*data-faq-q[^>]*>(.*?)</h3>", html, re.S)}
    assert faq
    heads = [_text(h) for h in re.findall(r"<h[1-6](?![^>]*data-faq-q)[^>]*>(.*?)</h[1-6]>", html, re.S)]
    assert not [h for h in heads if h.lower() in faq]


def test_built_city_newsletter_is_one_email_field_on_the_one_endpoint():
    s = section("city-newsletter-notice")
    form = re.search(r"<form[^>]*data-newsletter[^>]*>(.*?)</form>", s, re.S)
    head = re.search(r"<form[^>]*data-newsletter[^>]*>", s).group(0)
    assert 'method="POST"' in head
    ctl = re.findall(r"<(input|select|textarea)\b([^>]*)>", form.group(1))
    real = [a for t, a in ctl if 'type="hidden"' not in a and 'name="_gotcha"' not in a]
    assert len(real) == 1 and 'type="email"' in real[0] and 'name="email"' in real[0]
    for hidden in ("_next", "_subject"):
        assert f'name="{hidden}"' in form.group(1)
    assert 'name="_gotcha"' in form.group(1)
    # The same endpoint as the site's enquiry form, built by the same build.
    contact = ROOT / "dist/uk-blue-staffy-breeders-contact/index.html"
    if contact.exists():
        real_action = re.findall(r'<form[^>]*\saction="([^"]*)"', contact.read_text())
        assert re.search(r'\saction="([^"]*)"', head).group(1) in real_action


def test_built_city_contact_lineup_keeps_the_whole_form_contract():
    s = section("city-contact-lineup")
    form = re.search(r'<form[^>]*data-layout="grid"[^>]*>(.*?)</form>', s, re.S)
    head = re.search(r'<form[^>]*data-layout="grid"[^>]*>', s).group(0)
    assert form and 'method="POST"' in head and "data-contact-form" in head
    body = form.group(1)
    for name in ("name", "email", "phone", "location", "puppy", "message", "_gotcha", "_next", "_subject"):
        assert f'name="{name}"' in body, name
    assert 'value="waiting-list"' in body
    for p in _available():
        assert f'value="{p["slug"]}"' in body, p["slug"]
    for key in ("name", "email", "puppy", "message"):
        assert f'data-err="city-contact-{key}-err"' in body and f'id="city-contact-{key}-err"' in body, key
    # Every control has its own label.
    for cid in re.findall(r'<(?:input|select|textarea)[^>]*id="([^"]+)"', body):
        assert f'for="{cid}"' in body, cid
    # The line-up: every available puppy, pictures only.
    lineup = s.split('class="pups"', 1)[1].split("</ul>", 1)[0]
    assert lineup.count("<li") == len(_available())
    assert "<a " not in lineup and "<button" not in lineup


def test_the_grid_layout_of_the_kit_form_is_opt_in():
    """ContactFormKit's `layout="grid"` is the city line-up's alone: judged FORM BY FORM, every
    grid form sits inside a city contact line-up (`section.city-contact`, the London scaffold from
    Plan 2 Task 8), and every other form on every built page is still the stepped form, with
    three fieldsets and no error wiring. Manchester's `layout="compact"` (Phase F Task 31) is its
    photo-at-the-edge section's alone, held the same way."""
    pages = [p for p in (ROOT / "dist").rglob("index.html")
             if "kit-preview" not in p.parts and 'data-form="contact"' in p.read_text(encoding="utf-8")]
    if not pages:
        pytest.skip("run npm run build first")
    grids = 0
    for page in pages:
        html = page.read_text(encoding="utf-8")
        lineups = [(m.start(), html.index("</section>", m.start()))
                   for m in re.finditer(r'<section[^>]*class="city-kit city-contact', html)]
        edges = [(m.start(), html.index("</section>", m.start()))
                 for m in re.finditer(r'<section[^>]*class="city-kit city-photo-at-the-edge', html)]
        for m in re.finditer(r'<form[^>]*data-form="contact"[^>]*>.*?</form>', html, re.S):
            f = m.group(0)
            inside = any(a < m.start() < b for a, b in lineups)
            if 'data-layout="compact"' in f.split(">", 1)[0]:
                assert any(a < m.start() < b for a, b in edges), f"{page}: a compact form outside a photo-at-the-edge section"
                continue
            assert not any(a < m.start() < b for a, b in edges), f"{page}: a photo-at-the-edge section without the compact form"
            if 'data-layout="grid"' in f.split(">", 1)[0]:
                grids += 1
                assert inside, f"{page}: a grid form outside a city contact line-up"
            else:
                assert not inside, f"{page}: a city contact line-up without the grid form"
                assert "data-err=" not in f, page
                assert f.count("<fieldset") == 3, page
    assert grids >= 1, "the London scaffold's line-up carries the grid form"


def test_every_london_pick_names_its_kit_component_and_every_city_row_is_one():
    """Every city row is a canvas pick's component, except the pieces inside a section, which a
    board's `subcomponents` (block 6b) names instead: each of those rows names the record entry
    it builds, and that entry exists on the London board."""
    from city_components import COMPONENT_IDS, KIT_OF_VARIANT
    picks = json.loads((ROOT / "data/design/city-picks/blue-staffy-puppies-london.json").read_text())["picks"]
    assert list(picks) == list(COMPONENT_IDS)
    sections = [r for r in city_rows() if "subcomponent" not in r]
    assert [KIT_OF_VARIANT[picks[c]] for c in COMPONENT_IDS] == [r["id"] for r in sections]
    board = json.loads((ROOT / "data/boards/blue-staffy-puppies-london.json").read_text())
    pieces = {s["id"] for s in board.get("subcomponents", [])}
    subs = [r for r in city_rows() if "subcomponent" in r]
    assert subs, "the London board revision's four pieces are registered"
    assert {r["subcomponent"] for r in subs} <= pieces, sorted({r["subcomponent"] for r in subs} - pieces)
    assert city_rows()[-len(subs):] == subs, "the pieces follow the fifteen picks"


def _words(s):
    """The words of a CamelCase file stem or a kebab-case id: CityHeroFilmstrip, city-hero-filmstrip."""
    return {w.lower() for w in re.findall(r"[A-Z][a-z]*|[a-z]+", s)}


def _name_words(name):
    """A variant's name as words: "Litter line-up" -> {litter, lineup}."""
    return set(re.sub(r"[-']", "", name.lower()).split())


def test_each_city_component_is_named_for_the_variant_it_builds():
    """Working rule 16 forbids reusing a pick across cities, so a city component is ONE variant,
    named for it (Task 7b review, item 4): CityHeroFilmstrip is london/hero/b "Litter filmstrip",
    never a generic CityHero the next city would be tempted to mount again. The kit id, the file
    and the title each carry a word of the variant's own name; ids and files are unique."""
    from city_components import KIT_OF_VARIANT
    rows = {r["id"]: r for r in city_rows()}
    assert len({r["file"] for r in rows.values()}) == len(rows)
    # London's picks; Manchester's are named by tests/py/test_city_kit_manchester.py as each is built.
    for key, kit_id in ((k, v) for k, v in KIT_OF_VARIANT.items() if k.startswith("london/")):
        city, comp, v = key.split("/")
        name = json.loads((ROOT / "design/city-canvas" / city / comp / "meta.json").read_text())["variants"][v]["name"]
        own = _name_words(name) - {"litter", "photo"} or _name_words(name)
        row = rows[kit_id]
        assert own & _words(row["file"].rsplit(".", 1)[0]), (key, name, row["file"])
        assert own & _words(kit_id), (key, name, kit_id)
        assert name.lower() in row["title"].lower(), (key, name, row["title"])


CITY_PAGE = ROOT / "dist/kit-preview/city-page/index.html"


def test_the_city_page_specimen_lays_the_kit_out_as_a_city_page_does():
    """Task 7b review, item 1: /kit-preview/city-page/ is the city kit inside CityShell — the
    nav set in PageShell's three slots, the hero strips full width above the dial's grid, and
    every in-body component in the column (`has-own-dial`), each with its images' `sizes`
    written for the column (src/lib/cityKit.ts citySizes, `fit` 'column')."""
    if not CITY_PAGE.exists():
        pytest.skip("run npm run build first")
    html = CITY_PAGE.read_text(encoding="utf-8")
    assert 'name="robots" content="noindex' in html
    for root in CITY_NAV_ROOTS:
        assert html.count(f"{root}") >= 1, root
    for hook in ("data-city-jump-stepper", "data-city-dial-photo-marker"):
        assert len(re.findall(rf"<[a-z]+ [^>]*\b{hook}\b", html)) == 1, hook
    grid = html.index('class="page-shell has-own-dial')
    for cid in ("city-hero-filmstrip", "city-price-scale", "city-trust-ledger"):
        assert html.index(f'data-component="{cid}"') < grid, f"{cid} belongs above the dial's grid"
    body = ("city-takeaways-ledger", "city-puppy-sheet", "city-roster", "city-video-panel", "city-chapters",
            "city-letter", "city-faq-ledger", "city-newsletter-notice", "city-contact-lineup")
    for cid in body:
        assert html.index(f'data-component="{cid}"') > grid, f"{cid} belongs in the column"
        assert f'id="pg-{cid}"' in html, cid
    # The column's width, derived from cityKit's geometry, is written into the images' sizes on the
    # city page and on no full-width specimen.
    beside = 2 * _ts_const("SHELL_GUTTER") + _ts_const("DIAL_W") + _ts_const("DIAL_GAP")
    column = f"min(100vw, {_ts_const('CONTAINER')}px) - {beside}px"
    assert column in html
    assert column not in PREVIEW.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- Task 7b minors

def _contrast(a, b):
    def lum(h):
        c = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_the_grid_forms_invalid_border_is_a_warn_tint_that_reads_on_the_band():
    """M7: the grid form sits on the steel-900 band; its invalid border is a warn tint, never the
    focus brass, at 3:1 or more against the band (WCAG 1.4.11). --color-warn itself is 2.66:1
    there, so the band uses --city-warn-on-inverse (src/styles/city.css)."""
    src = (KIT / "ContactFormKit.astro").read_text(encoding="utf-8")
    rule = re.search(r"\[data-layout='grid'\] :user-invalid \{([^}]*)\}", src).group(1)
    assert "var(--form-invalid, var(--color-warn))" in rule and "--color-cta" not in rule
    lineup = (KIT / "CityContactLineup.astro").read_text(encoding="utf-8")
    assert "--form-invalid: var(--city-warn-on-inverse)" in lineup
    tokens = (ROOT / "src/styles/tokens.css").read_text(encoding="utf-8")
    band = re.search(r"--color-steel-900:\s*(#[0-9A-Fa-f]{6})", tokens).group(1)
    tint = re.search(r"--city-warn-on-inverse:\s*(#[0-9A-Fa-f]{6})", CITY_CSS.read_text(encoding="utf-8")).group(1)
    assert _contrast(tint, band) >= 3, _contrast(tint, band)


def test_the_jump_stepper_refuses_more_stops_than_fit_a_phone(tmp_path):
    """M8, as behaviour: the stepper's guard is cityKit.stepperStops(sections), which the component
    calls at build time; ten sections pass, eleven stop the build with the reason."""
    import json as _json, shutil, subprocess
    esbuild, node = ROOT / "node_modules/.bin/esbuild", shutil.which("node")
    if not esbuild.exists() or not node:
        pytest.skip("needs node and node_modules/.bin/esbuild (npm install)")
    out = tmp_path / "cityKit.mjs"
    subprocess.run([str(esbuild), str(ROOT / "src/lib/cityKit.ts"), "--bundle", "--format=esm", "--platform=node",
                    "--define:import.meta.env={}", f"--outfile={out}", "--log-level=error"], check=True)
    mk = lambda n: [{"id": f"s{i}", "label": f"S{i}", "question": "Q?", "icon": "list"} for i in range(n)]  # noqa: E731
    driver = (f"const m = await import({_json.dumps(out.as_uri())});"
              "const r = [];"
              f"for (const s of {_json.dumps([mk(10), mk(11)])}) {{ try {{ m.stepperStops(s); r.push('ok'); }} catch (e) {{ r.push(String(e.message)); }} }}"
              "console.log(JSON.stringify(r));")
    res = subprocess.run([node, "--input-type=module", "-e", driver], check=True, capture_output=True, text=True)
    ten, eleven = _json.loads(res.stdout)
    assert ten == "ok"
    assert "11 sections" in eleven and "10 stops" in eleven
    src = (KIT / "CityJumpStepper.astro").read_text(encoding="utf-8").split("---", 2)[1]
    assert "stepperStops(sections)" in src


def test_a_print_rings_only_for_keyboard_focus_on_its_ask_link():
    """M6: the ring is the stretched link's own ::after, drawn on .ask:focus-visible, so it needs
    no :has() (the render probe tabs to an Ask link and reads the ring)."""
    src = (KIT / "CityPuppySheet.astro").read_text(encoding="utf-8").split("<style>", 1)[1]
    assert re.search(r"\.ask:focus-visible::after \{[^}]*outline: 3px solid var\(--kit-ring\)", src)
    assert ":has(" not in src and ":focus-within" not in src


def test_the_video_panels_side_notes_are_no_landmark():
    assert "<aside" not in section("city-video-panel")


def test_the_specimens_count_the_litter_from_the_data():
    src = (KIT / "_registry.ts").read_text(encoding="utf-8")
    for literal in ("Six puppies", "Three boys", "three boys", "three girls"):
        assert literal not in src, literal
    # No hand-typed litter size in any specimen string ('The six', 'the six', 'Six Puppies'):
    # the word is LITTER, from availablePuppies().length (Task 7b spec review, gap 3).
    code = "\n".join(l for l in src.splitlines()
                     if not l.lstrip().startswith(("//", "*", "/*")) and "const WORDS" not in l)
    typed = re.findall(r"""['`][^'`\n]*\b[Ss]ix\b[^'`\n]*['`]""", code)
    assert not typed, typed


IN_BODY = ("CityTakeawaysLedger", "CityPuppySheet", "CityRoster", "CityVideoPanel", "CityChapters",
           "CityLetter", "CityFaqLedger", "CityNewsletterNotice", "CityContactLineup")


def test_no_in_body_city_component_reads_the_viewport_width():
    """Task 7b spec review, gap 2: an in-body component lays out for its own box, full width or in
    the column beside the dial, so no width rule of one reads the viewport — not the roster's
    stack (rule 13 now stacks below a 640px box) and not the padding steps. Motion and print
    queries are not width rules."""
    for name in IN_BODY:
        css = (KIT / f"{name}.astro").read_text(encoding="utf-8").split("<style>", 1)[1]
        width = re.findall(r"@media[^{]*\b(?:min|max)-width[^{]*\{", css)
        assert not width, (name, width)


def test_the_guarantee_prints_from_the_data_on_the_london_page():
    """Answer board q07 (2026-09-29): the guarantee is two years. On the London page the trust
    strip, the takeaways and the FAQ rail print it from data/settings.json, and no built page
    of the twelve prints it (their copy is theirs until each is rebuilt).
    London joined data/facts/rebuilt.json (075355ba), so "the twelve" is read as the rebuilt
    pages family_rules does not count as project 5 pages; a project 5 page prints the
    guarantee from the data by design, and London is held to that above."""
    import family_rules as FR
    g = guarantee()
    page = ROOT / "dist/uk-locations/blue-staffy-puppies-london/index.html"
    if not page.exists():
        pytest.skip("run npm run build first")
    html = page.read_text(encoding="utf-8")
    for root in ("city-trust", "city-takeaways-ledger", "city-faq"):
        m = re.search(r'<section[^>]*class="city-kit %s[" ].*?</section>' % root, html, re.S)
        assert m, root
        assert g["guarantee_label"] in _text(m.group(0)), f"{root} does not print the guarantee"
    twelve = [b for b in json.loads((ROOT / "data/facts/rebuilt.json").read_text())
              if not FR.is_new_page(b)]
    assert len(twelve) == len(FR.BUILT_BEFORE_SYSTEM_GAPS), twelve
    for built in twelve:
        f = ROOT / "dist/index.html" if built == "index" else ROOT / "dist" / built / "index.html"
        assert f.exists(), built
        assert g["guarantee_label"] not in f.read_text(encoding="utf-8"), built


def test_the_litters_age_is_one_data_field_and_no_birth_date_is_stated():
    """The breeder's answer (answer board q08, 2026-09-29): no date of birth, "just 10 weeks".
    The age lives in ONE place, data/settings.json `age_weeks`, and a page that states it says
    "10 weeks old" from that field. No city component, city specimen or the London scaffold types
    an age or a birth date (none states an age today)."""
    s = json.loads((ROOT / "data/settings.json").read_text())
    assert s["age_weeks"] == 10
    # "birth defects" is what the guarantee covers (answer board q02), not a date of birth.
    assert "birth" not in json.dumps(s).lower().replace("no date of birth", "").replace("birth defects", "")
    sources = [*KIT.glob("City*.astro"), ROOT / "src/lib/cityKit.ts", KIT / "_registry.ts",
               ROOT / "src/pages/uk-locations/blue-staffy-puppies-london.astro",
               *(ROOT / "src/pages/kit-preview").glob("city*.astro")]
    typed = re.compile(r"(?i)\b\d+\s*weeks?\s+old\b|\bborn on\b|date of birth|\bdob\b")
    assert [str(p.relative_to(ROOT)) for p in sources if typed.search(p.read_text(encoding="utf-8"))] == []


def test_the_guarantee_label_must_open_with_its_length_as_whole_words(tmp_path):
    """Task 10b review, item 2: cityKit refuses a guarantee label that does not open with the
    length `guarantee_days` holds, as whole words (a word boundary after "Two-year"). Each case
    runs through `checkGuaranteeLabel(days, label)`, the check `guaranteeRow()` calls."""
    import json as _json, shutil, subprocess
    esbuild, node = ROOT / "node_modules/.bin/esbuild", shutil.which("node")
    if not esbuild.exists() or not node:
        pytest.skip("needs node and node_modules/.bin/esbuild (npm install)")
    out = tmp_path / "cityKit.mjs"
    subprocess.run([str(esbuild), str(ROOT / "src/lib/cityKit.ts"), "--bundle", "--format=esm", "--platform=node",
                    "--define:import.meta.env={}", f"--outfile={out}", "--log-level=error"], check=True)
    cases = [[730, "Two-year health guarantee"], [365, "Two-year health guarantee"],
             [730, "two-year health guarantee"], [730, "Health guarantee, two years"],
             [730, "Two-years of cover"], [730, "Two-year-old promise"], [365, "One-year health guarantee"],
             [30, "30-day health guarantee"], [30, "30-days health guarantee"]]
    driver = (f"const m = await import({_json.dumps(out.as_uri())});"
              "const r = [];"
              f"for (const [d, l] of {_json.dumps(cases)}) {{ try {{ m.checkGuaranteeLabel(d, l); r.push('ok'); }} catch (e) {{ r.push('refused'); }} }}"
              "console.log(JSON.stringify(r));")
    res = subprocess.run([node, "--input-type=module", "-e", driver], check=True, capture_output=True, text=True)
    assert _json.loads(res.stdout) == ["ok", "refused", "refused", "refused", "refused", "refused", "ok", "ok", "refused"]
    kit = (ROOT / "src/lib/cityKit.ts").read_text(encoding="utf-8")
    # guaranteeRow() is src/lib/guarantee.ts guaranteeRowParts(G), which runs the label check.
    assert "guaranteeRowParts(G)" in kit
    assert "checkGuaranteeLabel(s.guarantee_days, s.guarantee_label)" in (ROOT / "src/lib/guarantee.ts").read_text(encoding="utf-8")


def test_the_built_pages_refuse_a_mismatched_or_cover_naming_guarantee_label(tmp_path):
    """Re-review, item 7: src/lib/site.ts guaranteeLabel(), which the rebuilt pages read, runs the
    same check as cityKit (src/lib/guarantee.ts `guaranteeWords`), so a label whose length does not
    match `guarantee_days` stops the build of a built page too; and a label that names a cover
    (anything after "guarantee", or covers/covering/for/hips/hereditary …) is refused, because the
    breeder has not said what it covers (rule 9)."""
    import json as _json, shutil, subprocess
    esbuild, node = ROOT / "node_modules/.bin/esbuild", shutil.which("node")
    if not esbuild.exists() or not node:
        pytest.skip("needs node and node_modules/.bin/esbuild (npm install)")
    out = tmp_path / "guarantee.mjs"
    subprocess.run([str(esbuild), str(ROOT / "src/lib/guarantee.ts"), "--bundle", "--format=esm", "--platform=node",
                    f"--outfile={out}", "--log-level=error"], check=True)
    cases = [[730, "Two-year health guarantee"], [365, "Two-year health guarantee"],
             [730, "Two-year health guarantee covering hips"], [730, "Two-year health guarantee for hips"],
             [730, "Two-year hereditary health guarantee"], [730, "Two-year health guarantee against hereditary conditions"],
             [730, "Two-year health guarantee (covers eyes)"], [730, "Two-year guarantee"]]
    driver = (f"const m = await import({_json.dumps(out.as_uri())});"
              "const r = [];"
              f"for (const [d, l] of {_json.dumps(cases)}) {{ try {{ r.push(m.guaranteeWords({{guarantee_days: d, guarantee_label: l}}, 'lower')); }} catch (e) {{ r.push('refused'); }} }}"
              "console.log(JSON.stringify(r));")
    res = subprocess.run([node, "--input-type=module", "-e", driver], check=True, capture_output=True, text=True)
    assert _json.loads(res.stdout) == ["two-year health guarantee", "refused", "refused", "refused", "refused",
                                        "refused", "refused", "two-year guarantee"]
    site = (ROOT / "src/lib/site.ts").read_text(encoding="utf-8")
    assert "guaranteeWords(settings" in site
