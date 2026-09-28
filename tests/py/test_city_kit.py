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


def test_the_city_kit_carries_no_refund_clause_helper():
    """The deposit's refund wording is being settled on another branch (deposit-wording); until
    it lands no city component prints a refund clause, so src/lib/cityKit.ts carries no dead
    helper for it (Task 7b review, item 6). The wording will be the data's when it comes."""
    src = (ROOT / "src/lib/cityKit.ts").read_text(encoding="utf-8")
    assert "depositRefundClause" not in src
    assert "deposit_refund" not in src


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


def test_the_built_pages_ship_none_of_the_city_nav_css():
    """Task 7b review, item 5: with the picks out of PageShell, Astro bundles their CSS only
    where a page imports them. The twelve built pages carry no rule of the city nav set."""
    rebuilt = json.loads((ROOT / "data/facts/rebuilt.json").read_text())
    for slug in rebuilt:
        path = ROOT / "dist" / ("index.html" if slug == "index" else f"{slug}/index.html")
        if not path.exists():
            pytest.skip("run npm run build first")
        css = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", path.read_text(encoding="utf-8"), re.S))
        for root in CITY_NAV_ROOTS + ("has-city-dial",):
            assert f".{root}" not in css, (slug, root)


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
        assert re.search(r"[.!?]$", para), f"a paragraph ends mid-sentence: {para!r}"
    assert reviews[n]["name"] in s
    assert "AggregateRating" not in s and "★" not in s


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
    # No guarantee figure while data/settings.json guarantee_days is null.
    assert json.loads((ROOT / "data/settings.json").read_text())["guarantee_days"] is None
    assert "guarantee" not in s.lower()
    # No licence detail, no refund clause, and the rail's served photo keeps its served alt.
    assert "licen" not in s.lower() and "refund" not in s.lower()
    src = re.search(r'<img [^>]*src="/images/([^"]+)"[^>]*>', s)
    assert re.search(r'alt="([^"]*)"', src.group(0)).group(1) in served_alts()[src.group(1)]


def test_the_faq_rail_prints_its_facts_from_the_one_source():
    """Task 7b review, item 7: the rail's brief types no fact beside src/lib/cityKit.ts. The
    deposit phrase and the transport line are cityKit exports (the transport from
    data/settings.json `delivery_note`), and the guarantee row is `guaranteeRow()`, which is null
    while `guarantee_days` is null and never carries wording the data does not."""
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
    """ContactFormKit's `layout="grid"` is the city line-up's alone: every built page's form is
    still the stepped form, with its own heading, three fieldsets and no error wiring."""
    pages = [p for p in (ROOT / "dist").rglob("index.html")
             if "kit-preview" not in p.parts and 'data-form="contact"' in p.read_text(encoding="utf-8")]
    if not pages:
        pytest.skip("run npm run build first")
    for page in pages:
        html = page.read_text(encoding="utf-8")
        for f in re.findall(r'<form[^>]*data-form="contact"[^>]*>.*?</form>', html, re.S):
            assert 'data-layout="grid"' not in f and "data-err=" not in f, page
            assert f.count("<fieldset") == 3, page


def test_every_london_pick_names_its_kit_component_and_every_city_row_is_one():
    from city_components import COMPONENT_IDS, KIT_OF_VARIANT
    picks = json.loads((ROOT / "data/design/city-picks/blue-staffy-puppies-london.json").read_text())["picks"]
    assert list(picks) == list(COMPONENT_IDS)
    assert [KIT_OF_VARIANT[picks[c]] for c in COMPONENT_IDS] == [r["id"] for r in city_rows()]


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
    for key, kit_id in KIT_OF_VARIANT.items():
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
    # The column's width is written into sizes (min(100vw, 1200px) less the shell, dial and gap).
    assert "min(100vw, 1200px) - 368px" in html
    assert "min(100vw, 1200px) - 368px" not in PREVIEW.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- Task 7b minors

def test_the_grid_forms_invalid_border_is_the_warn_colour_not_the_focus_brass():
    src = (KIT / "ContactFormKit.astro").read_text(encoding="utf-8")
    rule = re.search(r"\[data-layout='grid'\] :user-invalid \{([^}]*)\}", src).group(1)
    assert "--color-warn" in rule and "--color-cta" not in rule


def test_an_empty_email_and_a_malformed_one_get_different_error_lines():
    """An empty required field is not 'incomplete': each email error line carries an empty and a
    malformed message, and CSS shows one by :placeholder-shown (no script)."""
    for cid, form in (("city-newsletter-notice", "data-newsletter"), ("city-contact-lineup", "data-contact-form")):
        s = section(cid)
        email = re.search(r'<input [^>]*type="email"[^>]*>', s).group(0)
        assert 'placeholder=" "' in email, cid
        assert s.count('class="e-empty"') == 1 and s.count('class="e-bad"') == 1, cid
    for f in ("CityNewsletterNotice.astro", "ContactFormKit.astro"):
        assert ":placeholder-shown" in (KIT / f).read_text(encoding="utf-8"), f


def test_the_jump_stepper_refuses_more_stops_than_fit_a_phone():
    src = (KIT / "CityJumpStepper.astro").read_text(encoding="utf-8")
    assert re.search(r"const MAX_STOPS = \d+;", src)
    assert "sections.length > MAX_STOPS" in src and "throw new Error" in src.split("sections.length > MAX_STOPS", 1)[1][:300]


def test_a_print_rings_only_for_keyboard_focus_on_its_ask_link():
    src = (KIT / "CityPuppySheet.astro").read_text(encoding="utf-8")
    assert ".city-pup:has(.ask:focus-visible)" in src and ":focus-within" not in src


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
