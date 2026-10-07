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

`BUILT` grows by one batch per task: Task 28 is the hero, the counter strip and the trust strip.
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

#: The components built so far, by task (Task 28: the hero, the counter strip, the trust strip).
BUILT = ["hero", "counter-strip", "trust-strip"]
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
    for cls in ("city-hero-filmstrip", "city-scale", "city-trust", "city-price-scale", "city-trust-ledger"):
        assert re.search(rf"['\" ]{cls}['\" ]", code_of(src)) is None, (FILE[comp], cls)


@pytest.mark.parametrize("comp", BUILT)
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


@pytest.mark.parametrize("comp", BUILT)
def test_each_is_rendered_on_the_manchester_preview_with_no_inline_style_or_hex(comp):
    s = section(KIT_ID[comp])
    assert f'class="city-kit {KIT_ID[comp]}' in s or f'class="city-kit kit-hero {KIT_ID[comp]}' in s, KIT_ID[comp]
    assert "style=" not in s, re.findall(r'style="[^"]*"', s)[:3]
    assert not re.findall(r"#[0-9A-Fa-f]{6}\b", s)
    t = text(s).lower()
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
    imgs = re.findall(r"<img\b[^>]*>", page)
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
