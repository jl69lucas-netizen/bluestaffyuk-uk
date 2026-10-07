"""Manchester's own city components (the Manchester page run, Phase F Tasks 28-31): the frozen
picks (data/design/city-picks/blue-staffy-puppies-manchester-uk.json, 355d5e43) built into the
kit as components of their own, never London's (rules/design.md `own-components-per-page`;
working rule 16), and previewed on /kit-preview/city-manchester/ (gap G11).

Per component, the plan's Step 1 contract: a `"project": 5` row of data/design/components.json
carrying `canvas_variant` and `root_selector`; a `_registry.ts` entry; a root that carries
`city-kit`; every fact read from src/lib/cityKit.ts or a data file, never a typed price; the
hero's photo before its H1 in source; and the component rendered on the Manchester preview.
Plus the served-alt rule (working rule 11, the user's ruling of 2026-09-29): a puppy photo's
FIRST use on the page keeps the alt the site already serves for it (PuppyCard's, on every page
that lists the litter), and each repeat carries a new one, never a copy.

`BUILT` grows by one batch per task: Task 28 is the hero, the counter strip and the trust strip;
Task 29 the nav set (the contents list, the desktop dial and the jump links, mounted by
src/layouts/CityShell.astro as a `CityNavSet`) and the shared `data-city-nav` hook every city's
nav furniture carries (gap G12); Task 30 the first in-body components (the key takeaways, the
litter table with each puppy's own photo, and the image-and-text section), which bring the
Manchester preview under city-layout-follows-box; Task 31 the last four (the reviews, the FAQ
blocks, the newsletter and the enquiry form), each mounted at its place on the page, so the three
review slots and the three FAQ blocks are three mounts of one component.
"""
import html as _h
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from city_components import KIT_OF_VARIANT  # noqa: E402
from check_city_canvas import served_alts  # noqa: E402
from test_manchester_board import REWORDED  # noqa: E402

#: The nine FAQ wordings the breeder adopted at STOP 3, outline wording -> adopted wording.
ADOPTED = {old: new for old, (new, _) in REWORDED.items()}

SLUG = "blue-staffy-puppies-manchester-uk"
PICKS = json.loads((ROOT / f"data/design/city-picks/{SLUG}.json").read_text())["picks"]
COMPONENTS = ROOT / "data/design/components.json"
KIT = ROOT / "src/components/kit"
REGISTRY = KIT / "_registry.ts"
PREVIEW_SRC = ROOT / "src/pages/kit-preview/city-manchester.astro"
PREVIEW = ROOT / "dist/kit-preview/city-manchester/index.html"
LONDON_PREVIEW = ROOT / "dist/kit-preview/city/index.html"
SPEC = ROOT / "tests/render/city-kit.spec.ts"
SETTINGS = json.loads((ROOT / "data/settings.json").read_text())
PRICES = json.loads((ROOT / "data/price-matrix.json").read_text())
PUPPIES = [p for p in json.loads((ROOT / "data/puppies.json").read_text()) if p["status"] == "Available"]
CITY = next(r["city"] for r in json.loads((ROOT / "data/locations.json").read_text()) if r["slug"] == SLUG)

#: The components built so far, by task (Task 28: the hero, the counter strip, the trust strip;
#: Task 29: the nav set; Task 30: the key takeaways, the table, the image and text; Task 31: the
#: reviews, the FAQ blocks, the newsletter and the enquiry form).
NAV = ["contents-list", "desktop-dial", "jump-links"]
TAIL = ["reviews", "faq-blocks", "newsletter", "contact-form"]
IN_BODY = ["key-takeaways", "tables", "image-text", *TAIL]
BUILT = ["hero", "counter-strip", "trust-strip", *NAV, *IN_BODY]
#: The components that state facts (prices, the deposit, the band, names): each reads them through
#: src/lib/cityKit.ts. The nav set states none: its words are the page's own section list.
FACTS = [c for c in BUILT if c not in NAV]
#: The kit id and the file of each, from the frozen picks and KIT_OF_VARIANT.
KIT_ID = {c: KIT_OF_VARIANT[PICKS[c]] for c in BUILT}
FILE = {c: "".join(w.capitalize() for w in KIT_ID[c].split("-")) + ".astro" for c in BUILT}


def gbp(n):
    return "£{:,}".format(n)


def rows():
    return {r["id"]: r for r in json.loads(COMPONENTS.read_text(encoding="utf-8"))}


def london_files():
    """London's city component files: the project 5 rows that are no Manchester pick."""
    mine = set(KIT_ID.values()) | {v for k, v in KIT_OF_VARIANT.items() if k.startswith("manchester/")}
    return {r["file"] for r in rows().values() if r["project"] == 5 and r["id"] not in mine}


def built():
    if not PREVIEW.exists():
        pytest.fail("dist/kit-preview/city-manchester/index.html is not built: create the route and run npm run build")
    return PREVIEW.read_text(encoding="utf-8")


def section(kit_id):
    """The built preview section of one component; a missing one is a failure, never a skip."""
    page = built()
    start = page.find(f'data-component="{kit_id}"')
    assert start >= 0, f"/kit-preview/city-manchester/ has no section for {kit_id}"
    nxt = page.find('data-component="city-', start + 10)
    end = nxt if nxt >= 0 else page.find("</main>", start)
    return page[start:end]


def text(fragment):
    return re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def code_of(src):
    """An .astro file with its comments stripped, so a prose comment cannot satisfy or trip a test."""
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"^\s*//.*$", "", src, flags=re.M)


def decorative(img):
    """An `<img>` with an empty alt (Astro writes `alt=""` as a bare `alt`) that is hidden from
    assistive technology."""
    return bool(re.search(r'\salt(?:=""|(?=[\s>/]))', img)) and 'aria-hidden="true"' in img


def served_puppy_alt(p):
    """The alt the site serves for a puppy's card photo (src/components/kit/PuppyCard.astro)."""
    return f"{p['name']} the {p['colour'].lower()} Staffordshire Bull Terrier puppy"


# --------------------------------------------------------------------------- per component

@pytest.mark.parametrize("comp", BUILT)
def test_each_pick_has_a_project_5_row_with_its_variant_and_root(comp):
    row = rows().get(KIT_ID[comp])
    assert row, f"data/design/components.json has no row for {KIT_ID[comp]}"
    assert row["project"] == 5
    assert row["canvas_variant"] == PICKS[comp]
    assert row["root_selector"] == f".{KIT_ID[comp]}"
    assert row["file"] == FILE[comp] and (KIT / FILE[comp]).is_file(), row
    name = json.loads((ROOT / "design/city-canvas/manchester" / comp / "meta.json").read_text())["variants"][PICKS[comp][-1]]["name"]
    assert name.lower() in row["title"].lower(), (row["title"], name)
    assert CITY.lower() in row["title"].lower(), row["title"]


@pytest.mark.parametrize("comp", BUILT)
def test_each_pick_is_registered_with_a_demo(comp):
    src = REGISTRY.read_text(encoding="utf-8")
    stem = FILE[comp].rsplit(".", 1)[0]
    assert f"import {stem} from './{FILE[comp]}';" in src, stem
    assert f"'{KIT_ID[comp]}'" in src.split("export type ComponentId", 1)[1].split(";", 1)[0], "ComponentId names it"
    assert re.search(rf"'{KIT_ID[comp]}': \{{\s*C: {stem},", src), "REGISTRY has its entry"


@pytest.mark.parametrize("comp", BUILT)
def test_each_root_carries_the_city_type_base_and_imports_no_london_component(comp):
    src = (KIT / FILE[comp]).read_text(encoding="utf-8")
    front = src.split("---", 2)[1]
    assert f"class:list={{['city-kit', " in src, FILE[comp]
    assert "import '../../styles/city.css';" in front
    for f in london_files():
        assert f not in code_of(src), f"{FILE[comp]} imports or names London's {f}"
    # The own-components rule: never a London root class either.
    for cls in ("city-hero-filmstrip", "city-scale", "city-trust", "city-price-scale", "city-trust-ledger",
                "city-contents-photo-index", "city-dial-photo-marker", "city-jump-stepper"):
        assert re.search(rf"['\" ]{cls}['\" ]", code_of(src)) is None, (FILE[comp], cls)


@pytest.mark.parametrize("comp", FACTS)
def test_each_reads_its_facts_from_the_data_never_a_typed_figure(comp):
    """Working rule 9: no price, deposit, band or count is typed into a component."""
    code = code_of((KIT / FILE[comp]).read_text(encoding="utf-8"))
    markup = code.split("<style>", 1)[0]
    assert "£" not in markup, FILE[comp]
    for n in {PRICES["male_gbp"], PRICES["female_gbp"], SETTINGS["deposit_gbp"],
              SETTINGS["delivery_min_gbp"], SETTINGS["delivery_max_gbp"]}:
        assert not re.search(rf"(?<![\w.-]){n:,}(?![\w%])|(?<![\w.-]){n}(?![\w%px])", markup), (FILE[comp], n)
    assert "lib/cityKit" in code, f"{FILE[comp]} reads its facts through src/lib/cityKit.ts"
    for name in ("Carlisle", "Manchester", "Roman", "Cheryl", "Ince", "Vennie", "Byrd", "Christa"):
        assert name not in markup, (FILE[comp], name)


@pytest.mark.parametrize("comp", NAV)
def test_the_nav_set_types_no_fact_and_no_city(comp):
    """The nav components carry the page's section list and nothing else: no price, no figure,
    no puppy name, no city typed into them (the city comes in as a prop, from data/locations.json)."""
    markup = code_of((KIT / FILE[comp]).read_text(encoding="utf-8")).split("<style>", 1)[0]
    assert "£" not in markup, FILE[comp]
    for n in (PRICES["male_gbp"], PRICES["female_gbp"], SETTINGS["deposit_gbp"],
              SETTINGS["delivery_min_gbp"], SETTINGS["delivery_max_gbp"]):
        assert str(n) not in markup and f"{n:,}" not in markup, (FILE[comp], n)
    for name in ("Carlisle", "Manchester", "London", "Roman", "Cheryl", "Ince", "Vennie", "Byrd", "Christa"):
        assert name not in markup, (FILE[comp], name)


@pytest.mark.parametrize("comp", BUILT)
def test_each_is_rendered_on_the_manchester_preview_with_no_inline_style_or_hex(comp):
    s = section(KIT_ID[comp])
    assert f'class="city-kit {KIT_ID[comp]}' in s or f'class="city-kit kit-hero {KIT_ID[comp]}' in s, KIT_ID[comp]
    assert "style=" not in s, re.findall(r'style="[^"]*"', s)[:3]
    assert not re.findall(r"#[0-9A-Fa-f]{6}\b", s)
    # The deposit is never called plainly "refundable" (Phase F ruling 10): the one place the word
    # may stand is inside data/settings.json `deposit_refund_clause`, word for word.
    t = text(s).lower().replace(SETTINGS["deposit_refund_clause"].lower(), "")
    for banned in ("video call", "rescue", "licence", "licensed", "refundable"):
        assert banned not in t, (KIT_ID[comp], banned)


# --------------------------------------------------------------------------- the preview route

def test_the_manchester_preview_is_noindex_and_carries_only_manchesters_rows():
    assert PREVIEW_SRC.is_file()
    page = built()
    assert 'name="robots" content="noindex' in page
    found = re.findall(r'<section[^>]*data-component="(city-[a-z-]+)"', page)
    mine = [r["id"] for r in rows().values() if str(r.get("canvas_variant", "")).startswith("manchester/")]
    assert found == mine, found
    assert set(KIT_ID.values()) <= set(found)


def test_londons_preview_carries_none_of_manchesters_components():
    if not LONDON_PREVIEW.exists():
        pytest.fail("run npm run build first")
    london = LONDON_PREVIEW.read_text(encoding="utf-8")
    for kit_id in KIT_ID.values():
        assert f'data-component="{kit_id}"' not in london, kit_id


def test_the_render_spec_paints_the_manchester_preview_and_probes_each_component():
    spec = SPEC.read_text(encoding="utf-8")
    routes = re.search(r"const ROUTES = \[([^\]]*)\]", spec).group(1)
    assert "'/kit-preview/city-manchester/'" in routes or "MANCHESTER_KIT" in routes, routes
    assert "const MANCHESTER_KIT = '/kit-preview/city-manchester/'" in spec
    probes = spec.split("const PROBES", 1)[1]
    for kit_id in KIT_ID.values():
        assert f"'{kit_id}': {{" in probes, kit_id


def test_every_alt_on_the_manchester_preview_is_unique_and_a_first_use_keeps_the_served_alt():
    page = built()
    # A decorative image (alt="" and aria-hidden: the question bar's small puppy) is not a use of
    # the photograph a reader is told about, so it neither spends the served alt nor repeats it.
    imgs = [i for i in re.findall(r"<img\b[^>]*>", page) if not decorative(i)]
    alts = [_h.unescape(re.search(r'alt="([^"]*)"', i).group(1)) for i in imgs]
    named = [a for a in alts if a]
    assert len(named) == len(set(named)), sorted(a for a in named if named.count(a) > 1)
    seen = set()
    for tag, alt in zip(imgs, alts):
        pup = next((p for p in PUPPIES if f"/{p['card_photo'].rsplit('.', 1)[0]}." in tag), None)
        if not pup:
            continue
        if pup["name"] not in seen:
            assert alt == served_puppy_alt(pup), (pup["name"], alt)
        else:
            assert alt != served_puppy_alt(pup) and pup["name"] in alt, (pup["name"], alt)
        seen.add(pup["name"])
    assert seen == {p["name"] for p in PUPPIES}, "the hero and the counter between them show the whole litter"


# --------------------------------------------------------------------------- hero C, "Feature and three"

def test_hero_is_a_kit_hero_with_the_photo_before_the_heading():
    s = section(KIT_ID["hero"])
    assert 'kit-hero' in s and 'data-hero-layout="feature-and-three"' in s
    assert 0 <= s.find('class="pic') < s.find('class="title'), "rule 10: the photo precedes the heading in source"
    imgs = re.findall(r"<img\b[^>]*>", s)
    assert len(imgs) == 4, len(imgs)
    assert 'fetchpriority="high"' in imgs[0] and s.count('fetchpriority="high"') == 1
    assert all('loading="eager"' in i for i in imgs)
    # The feature's caption names the puppy and its share of the litter, counted from the data.
    feature = next(p for p in PUPPIES if f"/{p['card_photo'].rsplit('.', 1)[0]}." in imgs[0])
    same_sex = sum(1 for p in PUPPIES if p["sex"] == feature["sex"])
    words = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight"]
    word = "boys" if feature["sex"] == "male" else "girls"
    assert f"{feature['name']}, one of our {words[same_sex]} {word}" in text(s)
    assert 'class="cta"' in s and 'class="more"' in s


def test_hero_ticks_are_four_facts_from_the_data():
    s = section(KIT_ID["hero"])
    ticks = [text(t) for t in re.findall(r"<li[^>]*data-tick[^>]*>(.*?)</li>", s, re.S)]
    by = re.search(r"\bby (.+)$", SETTINGS["delivery_note"]).group(1).split(",")[0]
    assert ticks == ["Raised in our home", "Support after collection", SETTINGS["guarantee_label"], by], ticks
    for t in ticks[:2]:
        assert t in SETTINGS["puppy_trust_signs"], t


# --------------------------------------------------------------------------- counter B, "Range sheet"

def test_counter_reads_every_figure_from_the_data():
    s = section(KIT_ID["counter-strip"])
    t = text(s)
    band = f"{gbp(SETTINGS['delivery_min_gbp'])}–{gbp(SETTINGS['delivery_max_gbp'])}"
    for figure in (str(len(PUPPIES)), gbp(PRICES["male_gbp"]), gbp(PRICES["female_gbp"]), band,
                   gbp(SETTINGS["delivery_min_gbp"]), gbp(SETTINGS["delivery_max_gbp"])):
        assert figure in t, figure
    assert f"UK home delivery to {CITY}" in t
    assert SETTINGS["address"]["city"] in t
    assert s.count("data-figure") == 4
    faces = re.findall(r'<span class="faces"[^>]*>(.*?)</span>', s, re.S)
    assert faces and len(re.findall(r"<img\b", faces[0])) == len(PUPPIES)


# --------------------------------------------------------------------------- trust B, "Puppy folder"

def test_trust_folder_holds_the_papers_and_the_three_handover_steps_from_the_data():
    s = section(KIT_ID["trust-strip"])
    t = text(s)
    papers = [text(x) for x in re.findall(r'<ul class="docs"[^>]*>(.*?)</ul>', s, re.S)[0].split("</li>")[:-1]]
    assert papers == SETTINGS["puppy_trust_signs"][:5], papers
    assert f"The {['no','one','two','three','four','five','six'][len(papers)]} papers and records" in t
    steps = [text(x) for x in re.findall(r'<ul class="us"[^>]*>(.*?)</ul>', s, re.S)[0].split("</li>")[:-1]]
    band = f"{gbp(SETTINGS['delivery_min_gbp'])}–{gbp(SETTINGS['delivery_max_gbp'])}"
    assert steps == [f"{gbp(SETTINGS['deposit_gbp'])} deposit secures your puppy",
                     f"UK home delivery, {band} by distance",
                     f"Or collect from us in {SETTINGS['address']['city']}"], steps
    assert f"From us to {CITY}" in t
    assert s.count("data-trust-item") == len(papers) + 3
    assert s.count("<svg") == s.count("data-trust-item")
    # Nothing the hero's ticks already say (the user's canvas note on trust B).
    hero = text(section(KIT_ID["hero"]))
    for tick in ("Raised in our home", "Support after collection", SETTINGS["guarantee_label"]):
        assert tick in hero and tick not in t, tick


def test_the_served_puppy_alt_is_puppycards_template():
    """`servedPuppyAlt` (src/lib/imageFocus.ts) is the alt PuppyCard serves on every page that lists
    the litter; if either template moves, a city component's "first use" would stop being one."""
    card = (KIT / "PuppyCard.astro").read_text(encoding="utf-8")
    lib = (ROOT / "src/lib/imageFocus.ts").read_text(encoding="utf-8")
    template = "`${p.name} the ${p.colour.toLowerCase()} Staffordshire Bull Terrier puppy`"
    assert template in card and template in lib


# --------------------------------------------------------------------------- the nav set (Task 29)

OUTLINE = json.loads((ROOT / f"data/outlines/{SLUG}.json").read_text())
#: The page's sections the nav set lists: every outline section that carries an H2, in order.
OUTLINE_H2 = [h["text"] for sec in OUTLINE["sections"] for h in sec["headings"] if h["level"] == 2]
MANCHESTER_PUP = "reputable-blue-staffy-breeder-manchester-pup.webp"


def demo_ids():
    """The anchors the preview's nav demos name: the preview's own Manchester sections, in order,
    one per outline H2 at most, so every link resolves on /kit-preview/city-manchester/."""
    mine = [r["id"] for r in rows().values() if str(r.get("canvas_variant", "")).startswith("manchester/")]
    return [f"kit-{i}" for i in mine][:len(OUTLINE_H2)]


def test_the_outline_gives_the_nav_set_thirteen_sections():
    assert len(OUTLINE_H2) == 13, OUTLINE_H2


@pytest.mark.parametrize("comp", NAV)
def test_the_nav_set_marks_by_script_never_by_target_or_scroll_timeline(comp):
    """London Plan 2 execution note 13 and plan2-notes: the canvas marked the current section with
    `:target` and scroll-driven animations (stuck on section one for a reduced-motion reader,
    learning loop L8). The kit marks it through src/lib/scrollSpy.ts, never a second spy."""
    src = (KIT / FILE[comp]).read_text(encoding="utf-8")
    code = code_of(src)
    code = re.sub(r"NOSCRIPT_CSS = '[^']*'", "", code)
    for banned in (":target", "animation-timeline", "view-timeline", "timeline-scope", "!important", "data-canvas-only"):
        assert banned not in code, (FILE[comp], banned)
    if comp != "contents-list":
        assert "from '../../lib/scrollSpy'" in code, f"{FILE[comp]} reuses src/lib/scrollSpy.ts"
        assert "IntersectionObserver" not in code, f"{FILE[comp]} runs a spy of its own"


def test_contents_is_one_list_of_icon_rows_with_a_phone_disclosure():
    s = section(KIT_ID["contents-list"])
    ids = demo_ids()
    hrefs = re.findall(r'<a href="#([^"]+)"', s)
    assert hrefs == ids, "one row per section, each once: no second copy for phones (plan2-notes)"
    assert s.count("<ul") == 1
    rows_ = re.findall(r"<li\b[^>]*>(.*?)</li>", s, re.S)
    assert all("<svg" in r for r in rows_), "every row carries its line icon"
    rest = len(re.findall(r"<li data-rest", s))
    assert rest == max(0, len(ids) - 6)
    if rest:
        m = re.search(r'<button[^>]*data-more[^>]*>', s)
        assert m and 'aria-expanded="false"' in m.group(0) and 'aria-controls="city-icon-rows-list"' in m.group(0)
        assert 'id="city-icon-rows-list"' in s
    assert "<noscript>" in s, "a reader without scripting gets every row"
    nav = re.search(r"<nav[^>]*>", s).group(0)
    assert 'aria-labelledby="city-icon-rows-title"' in nav and 'id="city-icon-rows-title"' in s
    assert f"Go straight to any part of this {CITY} page" in text(s)


def test_contents_photo_is_manchesters_served_photo_with_its_served_alt():
    """The task's instruction and working rule 11: the photo is the Manchester pup the old site
    served, at its original path, with the alt it was served with, word for word."""
    s = section(KIT_ID["contents-list"])
    img = re.search(r"<img\b[^>]*>", s).group(0)
    assert f'src="/images/{MANCHESTER_PUP}"' in img
    alt = _h.unescape(re.search(r'alt="([^"]*)"', img).group(1))
    assert alt in served_alts()[MANCHESTER_PUP], alt
    assert s.find("<img") < s.find("<nav"), "the photo comes first (above the list on a phone)"


def test_dial_is_a_numeral_rail_with_one_current_row():
    s = section(KIT_ID["desktop-dial"])
    ids = demo_ids()
    root = re.search(r"<aside\b[^>]*>", s).group(0)
    assert 'data-city-nav="dial"' in root
    assert re.findall(r'data-spy="([^"]+)"', s) == ids
    nums = re.findall(r'<span class="n"[^>]*>(\d+)</span>', s)
    assert nums == [f"{i + 1:02d}" for i in range(len(ids))], nums
    assert s.count('aria-current="location"') == 1 and 'aria-current=""' not in s
    assert 'aria-labelledby="city-numeral-rail-title"' in s and 'id="city-numeral-rail-title"' in s
    t = text(s)
    assert f"This {CITY} page" in t
    assert f"{len(ids)} sections, in page order" in t
    assert "<img" not in s, "the rail carries no photo (the pick's media axis: none)"


def test_question_bar_is_a_readout_ticks_and_a_native_dialog_of_the_questions():
    s = section(KIT_ID["jump-links"])
    ids = demo_ids()
    root = re.search(r"<div\b[^>]*city-question-bar[^>]*>", s).group(0)
    assert 'data-city-nav="bar"' in root
    assert "data-strip" not in root, "the preview's bar is a picture of the component, not this page's chrome"
    assert "<dialog" in s and 'aria-labelledby="city-question-bar-title"' in s
    key = re.search(r"<button[^>]*data-jump-open[^>]*>", s).group(0)
    assert 'aria-haspopup="dialog"' in key and 'aria-expanded="false"' in key
    assert "aria-label" not in key, "the key's name is its visible text (WCAG 2.5.3)"
    sheet = re.search(r"<dialog\b.*?</dialog>", s, re.S).group(0)
    assert re.findall(r'data-spy="([^"]+)"', sheet) == ids
    qs = [text(a) for a in re.findall(r"<a\b[^>]*data-spy[^>]*>(.*?)</a>", sheet, re.S)]
    assert qs == OUTLINE_H2[:len(ids)], "the sheet lists the page's questions word for word"
    assert re.findall(r'data-spy="([^"]+)"', s) == ids, "the sheet's rows are the bar's only links"
    assert sheet.count('aria-current="location"') == 1
    ticks = re.search(r'<div class="ticks"[^>]*>(.*?)</div>', s, re.S)
    assert 'aria-hidden="true"' in ticks.group(0)
    assert ticks.group(1).count("<i") == len(ids) and ticks.group(1).count("data-on") == 1
    assert f"1 of {len(ids)}:" in text(s)
    assert f"{CITY} page, {len(ids)} sections" in text(s)
    img = re.search(r"<img\b[^>]*>", s).group(0)
    assert decorative(img), "the small puppy is decorative"
    assert "1080w" not in img, "a small derivative, never the 1080px source"
    src = (KIT / FILE["jump-links"]).read_text(encoding="utf-8")
    assert "showModal()" in src and "addEventListener('close'" in src


def test_the_nav_demo_reads_its_questions_from_the_outline():
    """The specimen's sections are the outline's own H2s and labels for the preview's anchors: one
    list for the three components (src/layouts/CityShell.astro hands each the same list)."""
    # One list for the preview and the page (Phase F Task 32): src/lib/manchesterNav.ts, which the
    # registry re-exports, so a page never imports the registry (and every kit component's CSS).
    src = (ROOT / "src/lib/manchesterNav.ts").read_text(encoding="utf-8")
    block = src.split("export const MANCHESTER_NAV", 1)[1].split("];", 1)[0]
    assert len(re.findall(r"label: '", block)) == len(OUTLINE_H2) == 13
    assert re.search(r"const MANCHESTER_H2\b[^\n]*outline\b[^\n]*\)\.sections", src), "the questions are read from the outline"
    assert "export { MANCHESTER_NAV }" in REGISTRY.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- G12: the shared nav hook

NAV_FURNITURE = {  # every city's bar and dial: London's two and Manchester's two
    "CityJumpStepper.astro": "bar", "CityDialPhotoMarker.astro": "dial",
    "CityQuestionBar.astro": "bar", "CityNumeralRail.astro": "dial",
}


@pytest.mark.parametrize("name", sorted(NAV_FURNITURE))
def test_every_citys_nav_furniture_carries_the_shared_hook(name):
    src = (KIT / name).read_text(encoding="utf-8")
    root = re.search(r"\n<(div|aside|nav)\b[^>]*class:list=\{\['city-kit'[^>]*>", src).group(0)
    assert f'data-city-nav="{NAV_FURNITURE[name]}"' in root, name


def test_the_type_fit_skip_and_the_container_rule_read_the_shared_hook_only():
    """Gap G12: `cityTypeFit.ts` skipped London's nav by its own two hooks, so the next city's bar
    and dial would have been judged as reading text. Both exclusions now name `[data-city-nav]`
    and no city's own hook."""
    fit = (ROOT / "tests/render/lib/cityTypeFit.ts").read_text(encoding="utf-8")
    skip = re.search(r"const skipRoot = .*", fit).group(0)
    assert "root.matches('[data-city-nav]')" in skip, skip
    assert "jump-stepper" not in skip and "photo-marker" not in skip
    css = (ROOT / "src/styles/city.css").read_text(encoding="utf-8")
    assert ".city-kit:not([data-city-nav]) { container-type: inline-size; }" in css
    good = (ROOT / "tests/render/fixtures/city/type-fit-good.html").read_text(encoding="utf-8")
    furniture = re.findall(r"<(?:div|aside)[^>]*\bdata-city-nav=\"(bar|dial)\"[^>]*>", good)
    assert len(furniture) >= 3, "the fixture holds a bar and a dial of more than one city"


def test_londons_built_nav_gains_the_hook_and_nothing_else_moves():
    page = (ROOT / "dist/kit-preview/city-page/index.html")
    if not page.exists():
        pytest.fail("run npm run build first")
    html = page.read_text(encoding="utf-8")
    for hook, part in (("data-city-jump-stepper", "bar"), ("data-city-dial-photo-marker", "dial")):
        tag = re.search(rf"<[a-z]+ [^>]*\b{hook}\b[^>]*>", html).group(0)
        assert f'data-city-nav="{part}"' in tag, tag


def test_the_built_pages_ship_none_of_manchesters_nav_css():
    """As London's (tests/py/test_city_kit.py): Astro bundles a city component's CSS only where a
    page imports it, so the twelve built pages carry none of Manchester's nav set."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from _slugs import resolve_page
    rebuilt = json.loads((ROOT / "data/facts/rebuilt.json").read_text())
    pages = [r for k in rebuilt for r in [resolve_page(k, ROOT)[1]] if not r.startswith("uk-locations/")]
    assert len(pages) >= 12
    for route in pages:
        path = ROOT / "dist" / (f"{route}/index.html" if route else "index.html")
        if not path.exists():
            pytest.fail("run npm run build first")
        css = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", path.read_text(encoding="utf-8"), re.S))
        for kit_id in (KIT_ID[c] for c in NAV):
            assert f".{kit_id}" not in css, (route, kit_id)


# --------------------------------------------------------------------------- Task 30: the in-body components

FAMILY = "victoria-family-blue-staffy-manchester.webp"
BAND = f"{gbp(SETTINGS['delivery_min_gbp'])}–{gbp(SETTINGS['delivery_max_gbp'])}"
TABLE = next(sec["table"] for sec in OUTLINE["sections"] if sec.get("table"))
TABLE_H4 = TABLE["under"].split(" ", 1)[1]
DEPOSIT_H2 = next(h["text"] for sec in OUTLINE["sections"] for h in sec["headings"]
                  if h["level"] == 2 and "Deposit" in h["text"])
TOWN = SETTINGS["address"]["city"]


def alt_of(img):
    return _h.unescape(re.search(r'alt="([^"]*)"', img).group(1))


def sentence_case(s):
    return s[:1].upper() + s[1:]


def test_the_in_body_components_are_judged_by_layout_follows_box_on_the_manchester_preview():
    """Task 28 kept the Manchester preview out of city-layout-follows-box (`NO_IN_BODY_YET`) until
    an in-body component existed; Task 30 builds three, so the skip goes and each one's layout
    facts are in the check's SPEC, keyed to its kit id."""
    spec = SPEC.read_text(encoding="utf-8")
    assert "NO_IN_BODY_YET" not in spec, "the Manchester preview is judged by city-layout-follows-box now"
    lib = (ROOT / "tests/render/lib/cityLayoutFollowsBox.ts").read_text(encoding="utf-8")
    spec_component = lib.split("export const SPEC_COMPONENT", 1)[1].split("};", 1)[0]
    for comp in IN_BODY:
        kit_id = KIT_ID[comp]
        assert re.search(rf"'\.{kit_id}[^']*': \{{\s*tablet", lib), f"{kit_id} has layout facts in SPEC"
        assert f": '{kit_id}'" in spec_component, f"SPEC_COMPONENT names {kit_id}"


# --------------------------------------------------------------------------- key takeaways C, "Tick card"

def tick_lines():
    """The five facts outline row 5 names, each built from the data as the component must."""
    tests = [e["name"].removesuffix(" DNA test") for e in json.loads((ROOT / "data/bsuk-ontology.json").read_text())["entities"]
             if e["id"] in ("ont:l-2-hga-dna-test", "ont:hc-hsf4-dna-test")]
    by = re.search(r"\bby (.+)$", SETTINGS["delivery_note"]).group(1)
    transport, priced = [x.strip() for x in by.split(",", 1)]
    cover = SETTINGS["guarantee_cover"].replace(" for two years", "")
    return [
        f"Each boy in this litter is {gbp(PRICES['male_gbp'])} and each girl {gbp(PRICES['female_gbp'])}, whatever the coat.",
        f"A {gbp(SETTINGS['deposit_gbp'])} deposit books your viewing and reserves your puppy, and it comes off the price.",
        f"We deliver by {transport} for {BAND}, {priced}, or you collect in {TOWN}.",
        f"Both parents are DNA tested for {sorted(tests)[1]} and {sorted(tests)[0]}, with the certificates shared on request.",
        f"{SETTINGS['guarantee_label']}: it {cover}.",
    ]


def test_tick_card_states_the_five_facts_of_outline_row_5_from_the_data():
    s = section(KIT_ID["key-takeaways"])
    # A tick's words run through inline `keep` spans: strip the tags without adding a space.
    inline = lambda f: re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", "", f))).strip()
    ticks = [inline(t) for t in re.findall(r"<li[^>]*data-takeaway[^>]*>(.*?)</li>", s, re.S)]
    assert ticks == tick_lines(), ticks
    assert re.search(r"<h[1-6]\b", s) is None, "outline row 5 carries no heading: the card's title is a line of type"
    t = text(s)
    assert f"for your {CITY} home" in t
    assert "Five plain answers from us" in t
    assert 'class="cta"' in s and "Ask about a puppy" in t
    # Every tick carries its brass disc, hidden from assistive technology.
    assert s.count('class="tick"') == 5 and all('aria-hidden="true"' in m for m in re.findall(r'<span class="tick"[^>]*>', s))


def test_tick_card_photo_is_the_served_family_photo_on_its_first_use():
    s = section(KIT_ID["key-takeaways"])
    img = re.search(r"<img\b[^>]*>", s).group(0)
    assert f'src="/images/{FAMILY}"' in img
    assert alt_of(img) in served_alts()[FAMILY], alt_of(img)
    assert s.find("<img") < s.find("data-takeaway"), "the photo heads the card"


# --------------------------------------------------------------------------- tables A, "Photo shelf"

def test_photo_shelf_is_the_outlines_litter_table_with_every_cell_labelled():
    s = section(KIT_ID["tables"])
    assert re.search(r"<h4\b[^>]*>\s*" + re.escape(TABLE_H4) + r"\s*</h4>", s), "the outline's H4, word for word"
    table = re.search(r"<table\b[^>]*>", s).group(0)
    assert "stack-table" in table and 'role="table"' in table
    assert text(re.search(r"<caption\b.*?</caption>", s, re.S).group(0)) == TABLE["caption"]
    heads = [text(h) for h in re.findall(r"<th\b[^>]*scope=\"col\"[^>]*>(.*?)</th>", s, re.S)]
    assert heads == [c["label"] for c in TABLE["columns"]], heads
    tds = re.findall(r"<td\b[^>]*>", s)
    assert tds and all("data-label=" in td for td in tds), "rule 13: every <td> carries its data-label"
    labels = [re.search(r'data-label="([^"]+)"', td).group(1) for td in tds]
    assert set(labels) == {c["label"] for c in TABLE["columns"][1:]}


def test_photo_shelf_rows_are_the_available_litter_from_the_data():
    s = section(KIT_ID["tables"])
    body = re.search(r"<tbody\b.*?</tbody>", s, re.S).group(0)
    rows_ = re.findall(r"<tr\b.*?</tr>", body, re.S)
    assert len(rows_) == len(PUPPIES) == 6, "outline: 6, one per puppy, status Available only"
    for row, p in zip(rows_, PUPPIES):
        price = gbp(PRICES["male_gbp"] if p["sex"] == "male" else PRICES["female_gbp"])
        cells = {re.search(r'data-label="([^"]+)"', td).group(1): text(td)
                 for td in re.findall(r"<td\b.*?</td>", row, re.S)}
        assert cells == {"Sex": "Boy" if p["sex"] == "male" else "Girl", "Coat": p["colour"], "Price": price}, cells
        head = text(re.search(r"<th\b.*?</th>", row, re.S).group(0))
        assert head == f"{p['name']} {p['status']}", head
        img = re.search(r"<img\b[^>]*>", row).group(0)
        assert f"/{p['card_photo'].rsplit('.', 1)[0]}." in img, (p["name"], "each row carries the pup's own card photo (KI 100)")
    lede = text(re.search(r'<p class="lede"[^>]*>.*?</p>', s, re.S).group(0))
    assert gbp(PRICES["male_gbp"]) in lede and gbp(PRICES["female_gbp"]) in lede and CITY in lede


def test_photo_shelf_types_no_name_and_reads_price_by_sex():
    src = code_of((KIT / FILE["tables"]).read_text(encoding="utf-8"))
    assert "availablePuppies" in src and ("BOY_PRICE" in src or "priceFor" in src)
    assert "font-variant" not in src


# --------------------------------------------------------------------------- image and text C, "Offset sheet"

def test_offset_sheet_is_the_deposit_section_with_its_four_cells_from_the_data():
    s = section(KIT_ID["image-text"])
    assert re.search(r"<h2\b[^>]*>\s*" + re.escape(DEPOSIT_H2) + r"\s*</h2>", s), "outline row 8's H2, word for word"
    assert s.find("<figure") < s.find("<h2"), "the section's photo comes before its heading (rule 17, H3-image-first)"
    cells = dict(zip([text(d) for d in re.findall(r"<dt\b[^>]*>(.*?)</dt>", s, re.S)],
                     [text(d) for d in re.findall(r"<dd\b[^>]*>(.*?)</dd>", s, re.S)]))
    assert list(cells) == ["What it does", "Off the price of", "If plans change", "After the visit"], cells
    assert cells["What it does"] == f"{gbp(SETTINGS['deposit_gbp'])} books your viewing and reserves your puppy"
    assert cells["Off the price of"] == f"{gbp(PRICES['male_gbp'])} for a boy or {gbp(PRICES['female_gbp'])} for a girl, in this litter"
    assert cells["If plans change"] == sentence_case(SETTINGS["deposit_refund_clause"]), "the clause word for word, never plainly 'refundable'"
    assert BAND in cells["After the visit"] and TOWN in cells["After the visit"] and "priced by distance" in cells["After the visit"]
    t = text(s)
    assert CITY in t and TOWN in t
    assert 'class="cta"' in s


def test_the_family_photo_repeated_by_the_offset_sheet_takes_a_new_alt():
    """Working rule 11 (2026-09-29, "same photo use new alt"): takeaways C and image-text C both
    show the family photo; the first use keeps its served alt, the second carries its own."""
    first = re.search(r"<img\b[^>]*>", section(KIT_ID["key-takeaways"])).group(0)
    second = re.search(r"<img\b[^>]*>", section(KIT_ID["image-text"])).group(0)
    assert f'src="/images/{FAMILY}"' in second
    assert alt_of(first) in served_alts()[FAMILY]
    assert alt_of(second) and alt_of(second) not in served_alts()[FAMILY] and alt_of(second) != alt_of(first)


@pytest.mark.parametrize("comp", IN_BODY)
def test_each_in_body_component_follows_its_own_box(comp):
    """An in-body city component is a container: its tiers read its own box (@container), never
    the viewport, so it lays out the same in the column beside the dial as on the preview."""
    css = code_of((KIT / FILE[comp]).read_text(encoding="utf-8")).split("<style>", 1)[1]
    assert "@container" in css, FILE[comp]
    assert "@media (width" not in css and "@media (min-width" not in css and "@media (max-width" not in css, FILE[comp]
    assert "font-variant" not in css and "variant" not in css.lower(), FILE[comp]


# --------------------------------------------------------------------------- Task 31: the last four

REVIEWS = json.loads((ROOT / "data/reviews.json").read_text())
BANK = {r["id"]: r for r in json.loads((ROOT / "data/faq.json").read_text())}
FAQ_SECTIONS = [sec for sec in OUTLINE["sections"] if sec.get("faq")]
ENQUIRY_H2 = OUTLINE["sections"][-1]["headings"][0]["text"]
MAGGIE = "maggie-blue-staffy-dam-with-pups.webp"
JONES = "jones-magnificent-blue-staffy-sire.webp"
LISA = "lisa-bright-blue-staffy-breeder-carlisle.webp"
DNA = sorted(e["name"].removesuffix(" DNA test") for e in json.loads((ROOT / "data/bsuk-ontology.json").read_text())["entities"]
             if e["id"] in ("ont:l-2-hga-dna-test", "ont:hc-hsf4-dna-test"))
CLAUSE = SETTINGS["deposit_refund_clause"]
DEPOSIT = gbp(SETTINGS["deposit_gbp"])
#: The answer board's q04 wording (2026-10-07, docs/reference/answer-board/answers/
#: 2026-10-07-outline-blue-staffy-puppies-manchester-uk-2026-10-07.md), every figure read here
#: from data/settings.json, as the build must read it.
MOTHER_ANSWER = (f"See them together before you commit to a puppy. With us the {DEPOSIT} deposit comes first: "
                 f"it books your viewing and reserves your puppy, it comes off the price, and it is {CLAUSE}. "
                 "At the viewing you see both parents, their registration papers and the veterinary records "
                 "before you commit to a puppy, and again on the day you collect.")
#: The answers that are a bank row word for word (data/faq.json, no token in them).
VERBATIM = {
    "How Do I Know Which Puppies Are Still Available?": "listing-availability",
    "What Vaccinations, Worming and Flea Treatments Has the Puppy Had?": "health-vaccinations",
    "Is Blue Staffy Aggressive?": "listing-aggressive",
    "Do Blue Staffies Suit First-Time Dog Owners?": "listing-first-time-owners",
    "Can a Staffy Be Left Alone for Hours?": "listing-left-alone",
    "Do Blue Staffies Make Good Family Pets for Homes With Children?": "home-family-children",
    "Is a Staffordshire Bull Terrier Able to Live in a Flat?": "guide-flat-living",
}


def inline(fragment):
    """Text with tags stripped and NO space added: a keep span inside a word stays inside it."""
    return re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def mounts(kit_id):
    """Every root of one component on the preview (a component mounted at several places)."""
    return re.findall(rf'<(?:section|aside|div)\b[^>]*class="city-kit {kit_id}\b.*?</section>', section(kit_id), re.S)


def served_alt_of(file):
    return served_alts()[file]


TEST_ID = "test-form-id"


def with_id(fn):
    """Run `fn` with a stand-in PUBLIC_FORMSPREE_ID: the audit refuses to run without one (it would
    match nothing), and the real id lives only in .env."""
    import os
    old = os.environ.get("PUBLIC_FORMSPREE_ID")
    os.environ["PUBLIC_FORMSPREE_ID"] = TEST_ID
    try:
        return fn()
    finally:
        if old is None:
            os.environ.pop("PUBLIC_FORMSPREE_ID", None)
        else:
            os.environ["PUBLIC_FORMSPREE_ID"] = old


# ---- reviews C, "Three plates": one review per mount, three mounts, data/reviews.json word for word

def test_three_plates_quote_each_review_word_for_word_one_per_slot_with_no_score():
    s = section(KIT_ID["reviews"])
    plates = mounts(KIT_ID["reviews"])
    assert len(plates) == 3 and s.count("data-review-slot") == 3, "outline rows 6, 11 and 20: one review each"
    want = {r["name"]: r for r in REVIEWS}
    names = []
    for plate in plates:
        quote = " ".join(inline(p) for p in re.findall(r"<p\b[^>]*>(.*?)</p>", re.search(r"<blockquote\b.*?</blockquote>", plate, re.S).group(0), re.S))
        cite = inline(re.search(r"<cite\b[^>]*>(.*?)</cite>", plate, re.S).group(1))
        r = want[cite]
        assert quote == r["quote"], (cite, quote[:60])
        assert f"{r['name']}, {r['place']}" in inline(plate), "attributed as the data gives it"
        names.append(cite)
    assert names == ["The Victoria Family", "Mark J", "Rachel L."]
    for banned in ("★", "☆", "/5", "out of 5", "rating", "stars"):
        assert banned not in text(s).lower() and banned not in s, banned
    assert "aggregateRating" not in built() and "reviewRating" not in built()
    src = code_of((KIT / FILE["reviews"]).read_text(encoding="utf-8"))
    assert "reviews.json" in src, "the review is read from data/reviews.json by name, never typed"


def test_three_plates_alternate_the_photo_side_and_credit_every_parent_photo():
    plates = mounts(KIT_ID["reviews"])
    sides = [re.search(r'data-side="(start|end)"', p).group(1) for p in plates]
    assert sides == ["start", "end", "start"], sides
    files = [re.search(r'src="/images/([^"?]+)', p).group(1).split(" ")[0] for p in plates]
    assert files == [FAMILY, MAGGIE, JONES], files
    for p in plates[1:]:
        assert re.search(r'class="cr"[^>]*>\s*Photo:', p), "a parent's photo never reads as the reviewer's own dog"
    # Working rule 11: the family photo is on the preview twice already (takeaways, offset sheet),
    # so the plate takes a third alt; Maggie and Jones are first uses and keep the served alt.
    alts = [alt_of(re.search(r"<img\b[^>]*>", p).group(0)) for p in plates]
    assert alts[0] not in served_alt_of(FAMILY)
    assert alts[1] in served_alt_of(MAGGIE) and alts[2] in served_alt_of(JONES)


# ---- FAQ B, "Rows beside a photo": three mounts, the board's questions (the outline's, nine reworded at STOP 3), answers from the bank and the data

def faq_blocks():
    return mounts(KIT_ID["faq-blocks"])


def faq_rows(block):
    """(question, answer) per row: a long answer is set in paragraphs at its own sentence breaks, so
    the answer is its paragraphs rejoined with single spaces (the FAQPage text, words untouched)."""
    out = []
    for q, a in re.findall(r"<details\b[^>]*>\s*<summary\b[^>]*>.*?<h3\b[^>]*>(.*?)</h3>.*?</summary>\s*<div class=\"a\"[^>]*>(.*?)</div>\s*</details>", block, re.S):
        out.append((inline(q), " ".join(inline(t) for t in re.findall(r"<p\b[^>]*>(.*?)</p>", a, re.S))))
    return out


def test_faq_blocks_are_the_outlines_three_blocks_word_for_word():
    blocks = faq_blocks()
    assert len(blocks) == 3 == len(FAQ_SECTIONS)
    total = 0
    for block, sec in zip(blocks, FAQ_SECTIONS):
        h2 = sec["headings"][0]
        assert re.search(r"<h2\b[^>]*>\s*" + re.escape(h2["text"]) + r"\s*</h2>", block), h2["text"]
        qs = [q for q, _ in faq_rows(block)]
        assert qs == [ADOPTED.get(c["text"], c["text"]) for c in h2["children"]], qs
        total += len(qs)
        assert block.count("<details") == len(qs) and block.count("<summary") == len(qs)
    assert total == 20, "6 + 7 + 7 questions (Phase F ruling 2)"


def test_faq_answers_come_from_the_bank_and_the_data_never_typed():
    rows = dict(r for b in faq_blocks() for r in faq_rows(b))
    for q, bank in VERBATIM.items():
        assert rows[ADOPTED.get(q, q)] == BANK[bank]["a"], (q, bank)
    boys = [p["name"] for p in PUPPIES if p["sex"] == "male"]
    girls = [p["name"] for p in PUPPIES if p["sex"] == "female"]
    cost = rows[ADOPTED["How Much Does Each Blue Staffy Puppy Cost?"]]
    assert gbp(PRICES["male_gbp"]) in cost and gbp(PRICES["female_gbp"]) in cost
    assert all(n in cost for n in boys + girls), cost
    deposit = rows[ADOPTED["How Much Is Your Deposit?"]]
    assert deposit.startswith(DEPOSIT) and CLAUSE in deposit, deposit
    assert rows[ADOPTED["Should I See the Mother With Her Puppy Before Money Changes Hands?"]] == MOTHER_ANSWER
    across = rows[ADOPTED["Do You Deliver Puppies Across the UK?"]]
    assert across.startswith("Wherever you are in the UK"), across
    assert BAND.replace("–", " to ") in across or (gbp(SETTINGS["delivery_min_gbp"]) in across and gbp(SETTINGS["delivery_max_gbp"]) in across)
    assert SETTINGS["delivery_note"] in across and TOWN in across
    dna = rows[ADOPTED["Are Both Parents DNA Tested Clear for L-2-HGA and for HC-HSF4?"]]
    assert all(t in dna for t in DNA) and "certificates on request" in dna, dna
    for word in ("clear", "result", "negative", "passed", "free of"):
        assert word not in dna.lower(), (word, dna)
    where = rows["Where Do I Find Blue Staffy Puppies to Buy Near Manchester?"]
    assert where == "Here. " + BANK["home-find-breeders"]["a"].split(". ", 1)[1], where
    for q, a in rows.items():
        assert "—" not in a, (q, "no em dash in our copy")
        assert "refundable" not in a.replace(CLAUSE, ""), (q, "never plainly refundable")
    lib = (ROOT / "src/lib/manchesterFaq.ts").read_text(encoding="utf-8")
    assert "loadFaq" in lib and "boards/blue-staffy-puppies-manchester-uk.json" in lib, "bank rows and the board's questions"
    assert "£" not in code_of(lib) and not re.search(r"(?<![\w.-])(500|1,500|1,700|200|350)(?![\w%])", code_of(lib))


def test_faq_photos_swap_sides_and_every_repeat_takes_a_new_alt():
    blocks = faq_blocks()
    assert [re.search(r'data-side="(start|end)"', b).group(1) for b in blocks] == ["end", "start", "end"]
    imgs = [re.search(r"<img\b[^>]*>", b).group(0) for b in blocks]
    christa = next(p for p in PUPPIES if p["name"] == "Christa")
    assert f"/{christa['card_photo'].rsplit('.', 1)[0]}." in imgs[0]
    assert f'src="/images/{MAGGIE}"' in imgs[1] and f'src="/images/{MANCHESTER_PUP}"' in imgs[2]
    assert alt_of(imgs[1]) not in served_alt_of(MAGGIE) and alt_of(imgs[2]) not in served_alt_of(MANCHESTER_PUP)
    for b in blocks:
        assert b.find("<img") < b.find('class="rows'), "the photo comes before the rows (a strip on top on a phone)"


# ---- newsletter B, "Postmarked note": no heading, no count, the one endpoint, classed `newsletter`

def test_postmarked_note_says_what_a_subscriber_gets_with_no_heading_and_no_count():
    s = section(KIT_ID["newsletter"])
    assert re.search(r"<h[1-6]\b", s) is None, "outline row 16 carries no heading"
    t = text(s)
    assert "next litter" in t and f"Greater {CITY}" in t
    assert not re.search(r"\b\d[\d,]*\s*(subscribers|readers|families|people|owners)", t, re.I), "no subscriber count"
    assert f"{SETTINGS['breeder_name']}" in t and TOWN in t, "signed by the breeder, from the town"
    assert "Your email is used for nothing else." in t
    img = re.search(r"<img\b[^>]*>", s).group(0)
    vennie = next(p for p in PUPPIES if p["name"] == "Vennie")
    assert f"/{vennie['card_photo'].rsplit('.', 1)[0]}." in img and "Vennie" in alt_of(img)


def test_postmarked_note_posts_one_email_to_the_one_endpoint():
    s = section(KIT_ID["newsletter"])
    forms = re.findall(r"<form\b[^>]*>.*?</form>", s, re.S)
    assert len(forms) == 1
    head = re.search(r"<form\b[^>]*>", forms[0]).group(0)
    assert 'method="POST"' in head and "data-newsletter" in head
    contact = ROOT / "dist/uk-blue-staffy-breeders-contact/index.html"
    real = re.findall(r'<form[^>]*\saction="([^"]*)"', contact.read_text(encoding="utf-8"))
    assert re.search(r'\saction="([^"]*)"', head).group(1) in real, "the endpoint every form posts to"
    for name in ("_next", "_subject", "_gotcha", "email"):
        assert f'name="{name}"' in forms[0], name
    email = re.search(r'<input\b[^>]*type="email"[^>]*>', forms[0]).group(0)
    eid = re.search(r'id="([^"]+)"', email).group(1)
    assert f'for="{eid}"' in forms[0] and "required" in email and 'data-err="' in email
    import form_contract_audit as F
    rows = with_id(lambda: F.audit_html(forms[0], "kit-preview/city-manchester"))
    assert [r["kind"] for r in rows] == ["newsletter"], rows


# ---- contact B, "Photo at the edge": the kit form's contract, a collect-or-delivery switch, the
# ---- any-boy / any-girl / next-litter options, the reply time as data/faq.json words it

def test_photo_at_the_edge_heads_the_form_with_lisas_photo_and_the_outlines_h2():
    s = section(KIT_ID["contact-form"])
    assert re.search(r"<h2\b[^>]*>\s*" + re.escape(ENQUIRY_H2) + r"\s*</h2>", s), "outline row 22's H2"
    img = re.search(r"<img\b[^>]*>", s).group(0)
    assert f'src="/images/{LISA}"' in img
    assert s.find("<img") < s.find("<h2"), "the photo comes first (a strip on top on a phone)"
    london = (ROOT / "dist/uk-locations/blue-staffy-puppies-london/index.html").read_text(encoding="utf-8")
    there = {alt_of(i) for i in re.findall(r"<img\b[^>]*>", london) if LISA.rsplit(".", 1)[0] in i}
    assert there and alt_of(img) not in there and "Lisa Bright" in alt_of(img), "a repeat carrying a new alt"


def test_photo_at_the_edge_keeps_the_kit_forms_whole_contract_plus_the_switch():
    s = section(KIT_ID["contact-form"])
    form = re.search(r"<form\b[^>]*>.*?</form>", s, re.S).group(0)
    head = re.search(r"<form\b[^>]*>", form).group(0)
    assert 'method="POST"' in head and 'data-layout="compact"' in head and "data-contact-form" in head
    for name in ("name", "email", "phone", "location", "puppy", "message", "_gotcha", "_next", "_subject", "handover"):
        assert f'name="{name}"' in form, name
    radios = re.findall(r'<input\b[^>]*name="handover"[^>]*>', form)
    assert sorted(re.search(r'value="([^"]+)"', r).group(1) for r in radios) == ["collect", "delivery"]
    assert all('type="radio"' in r for r in radios)
    t = text(form)
    assert f"Collect in {TOWN}" in t and "Home delivery" in t
    assert BAND in t and "priced by distance" in t
    values = re.findall(r'<option\b[^>]*value="([^"]*)"', form)
    assert values == ["", *[p["slug"] for p in PUPPIES], "any-boy", "any-girl", "waiting-list"], values
    labels = [inline(o) for o in re.findall(r"<option\b[^>]*>(.*?)</option>", form, re.S)]
    for p in PUPPIES:
        price = gbp(PRICES["male_gbp"] if p["sex"] == "male" else PRICES["female_gbp"])
        assert f"{p['name']}, {'boy' if p['sex'] == 'male' else 'girl'}, {price}" in labels, p["name"]
    words = ["no", "one", "two", "three", "four", "five", "six"]
    n_boys = sum(p["sex"] == "male" for p in PUPPIES); n_girls = len(PUPPIES) - n_boys
    assert f"Any of our {words[n_boys]} boys" in labels and f"Any of our {words[n_girls]} girls" in labels
    reply = BANK["enquiry-reply-time"]["a"].split(". ", 1)[0] + "."
    assert reply in t, "the reply time only as data/faq.json enquiry-reply-time words it"
    for cid in re.findall(r'<(?:input|select|textarea)\b[^>]*\bid="([^"]+)"', form):
        assert f'for="{cid}"' in form, cid
    for key in ("name", "email", "puppy", "message"):
        assert re.search(rf'name="{key}"[^>]*data-err="[^"]+"|data-err="[^"]+"[^>]*name="{key}"', form), key
    assert "PHONE_PLACEHOLDER" not in s and not re.search(r"\b0\d{3,4}\s?\d{3}\s?\d{3,4}\b", t), "no phone number"
    import form_contract_audit as F
    # Judged as the FULL contract a content page owes (a specimen route skips it), at the id's endpoint.
    live = form.replace(re.search(r'\saction="[^"]*"', head).group(0), f' action="https://formspree.io/f/{TEST_ID}"', 1)
    rows = with_id(lambda: F.audit_html(live, "blue-staffy-vs-staffordshire-bull-terrier"))
    assert [r["kind"] for r in rows] == ["inquiry"] and rows[0]["problems"] == [], rows
    assert rows[0]["in_scope"], "the full field contract was applied"


def test_every_served_photo_on_the_preview_keeps_its_served_alt_first_and_a_new_one_after():
    """Working rule 11 for the served /images/ files (the puppy photos are held above): the first
    use keeps an alt the old site served, every later use carries its own, and no two are alike."""
    page = built()
    seen = {}
    for img in re.findall(r"<img\b[^>]*>", page):
        m = re.search(r'src="/images/([^"/]+?\.webp)"', img)
        if not m or decorative(img) or m.group(1) not in served_alts():
            continue
        f, alt = m.group(1), alt_of(img)
        if f not in seen:
            assert alt in served_alts()[f], (f, alt)
        else:
            assert alt not in served_alts()[f] and alt not in seen[f], (f, alt)
        seen.setdefault(f, []).append(alt)
    assert {FAMILY, MAGGIE, JONES, MANCHESTER_PUP} <= set(seen)
