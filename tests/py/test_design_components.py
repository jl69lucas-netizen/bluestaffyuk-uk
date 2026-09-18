"""data/design/components.json is the one list of kit components; everything else
(the kit folder, the canvas route, the picks board, picks.json) is checked against it."""
import json, pathlib, re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
COMPONENTS = ROOT / "data/design/components.json"
KIT = ROOT / "src/components/kit"
IDS = ["site-header", "hero", "buttons", "puppy-card", "trust-strip", "counter-strip",
       "info-card", "testimonial", "faq", "contact-form", "page-nav", "footer", "section-divider"]


def load():
    return json.loads(COMPONENTS.read_text())


def test_thirteen_components_in_spec_order():
    rows = load()
    assert [r["id"] for r in rows] == IDS


def test_each_row_has_file_title_width():
    for r in load():
        assert re.fullmatch(r"[A-Z][A-Za-z]+\.astro", r["file"]), r
        assert r["title"] and isinstance(r["title"], str)
        assert r["board_width"] in (640, 1280), r


def test_ids_and_files_are_unique():
    rows = load()
    ids, files = [r["id"] for r in rows], [r["file"] for r in rows]
    assert len(set(ids)) == len(ids), sorted(i for i in ids if ids.count(i) > 1)
    assert len(set(files)) == len(files), sorted(f for f in files if files.count(f) > 1)


@pytest.mark.xfail(strict=True, reason="kit lands in Tasks 4-16")
def test_kit_file_exists_for_each_row():
    missing = [r["file"] for r in load() if not (KIT / r["file"]).exists()]
    assert not missing, missing


VARIANT_TS = KIT / "_variant.ts"
MARK = KIT / "Mark.astro"


def test_variant_helper_exports_the_five_letters():
    t = VARIANT_TS.read_text()
    assert "export type Variant = 'a' | 'b' | 'c' | 'd' | 'e'" in t
    assert "export const VARIANTS" in t


def test_mark_has_five_variants_stroke_currentcolor_and_title():
    t = MARK.read_text()
    for v in "abcde":
        assert f"variant === '{v}'" in t, v
    assert 'stroke="currentColor"' in t
    assert "<title>" in t
    assert "fill=\"#" not in t and "stroke=\"#" not in t


ROUTE = ROOT / "src/pages/design-canvas/index.astro"
REGISTRY_TS = KIT / "_registry.ts"
DIST_ROUTE = ROOT / "dist/design-canvas/index.html"


def test_route_is_noindex():
    t = ROUTE.read_text()
    # The prop, not the bare word: the file's header comment also says "noindex", so
    # `'noindex' in t` would keep passing with the prop deleted from the BaseLayout call.
    assert 'noindex={true}' in t


@pytest.mark.xfail(strict=True, reason="kit lands in Tasks 5-15")
def test_registry_has_an_entry_for_every_component():
    # The route renders whatever REGISTRY holds and has no per-component branches, so the
    # registry - not the route's import list - is what has to name all thirteen ids.
    body = REGISTRY_TS.read_text().split("export const REGISTRY", 1)[1]
    missing = [r["id"] for r in load()
               if f"'{r['id']}'" not in body and not re.search(rf"\b{r['id']}\s*:", body)]
    assert not missing, missing


def test_built_canvas_is_noindex():
    # Deliberately its own passing test rather than a line inside the xfail'd count check:
    # the route being noindex is true TODAY, and it is what keeps it out of every sitemap.
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    assert 'name="robots" content="noindex' in DIST_ROUTE.read_text()


@pytest.mark.xfail(strict=True, reason="kit lands in Tasks 5-16")
def test_built_route_has_sixty_five_sections():
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    html = DIST_ROUTE.read_text()
    # 13 components x 5 variants. The mark's own section carries data-variant="all", like
    # the per-component heading sections, so only the artboard sections are counted here.
    secs = re.findall(r'<section[^>]*data-component="([a-z-]+)"[^>]*data-variant="([a-e])"', html)
    assert len(secs) == 65, len(secs)
    assert {c for c, _ in secs} == set(IDS)


SECTION_RE = re.compile(
    r'<section[^>]*data-component="([a-z-]+)"[^>]*data-variant="([a-e])"[^>]*>(.*?)</section>', re.S)


def test_built_sections_render_five_distinct_variants():
    """Whatever is on the canvas today must show five genuinely different things per
    component, with no hex reached for in an inline style. Passes for the components that
    exist; every later task widens it for free."""
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    by_component = {}
    for cid, variant, inner in SECTION_RE.findall(DIST_ROUTE.read_text()):
        by_component.setdefault(cid, {})[variant] = inner
    assert by_component, "the canvas built no variant sections at all"
    for cid, variants in sorted(by_component.items()):
        assert sorted(variants) == list("abcde"), (cid, sorted(variants))
        same = [(x, y) for i, x in enumerate("abcde") for y in "abcde"[i + 1:]
                if variants[x] == variants[y]]
        assert not same, (cid, same)
        hexes = [m for inner in variants.values()
                 for m in re.findall(r'style="[^"]*#[0-9A-Fa-f]{3}', inner)]
        assert not hexes, (cid, hexes)


def _sections(cid):
    """The built artboard sections for one component, keyed by variant letter."""
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    out = {v: inner for c, v, inner in SECTION_RE.findall(DIST_ROUTE.read_text()) if c == cid}
    if not out:
        pytest.skip(f"{cid} is not on the canvas yet")
    return out


def test_built_site_header_variants_carry_their_distinguishing_marks():
    """Convention 8. Five headers that differ only in CSS would pass the distinctness check
    above while the drawer, the dark bands and the strapline had all silently vanished."""
    s = _sections("site-header")
    assert "<details" in s["d"], "variant d is the drawer variant"
    assert "<details" not in s["a"]
    for v in ("b", "d"):
        assert 'data-surface="inverse"' in s[v], v
    for v in ("a", "c", "e"):
        assert 'data-surface="inverse"' not in s[v], v
    assert "Carlisle" in s["e"], "variant e shows the location strapline"
    assert "Glasgow" not in "".join(s.values())


def test_built_puppy_card_variants_carry_price_status_and_their_ornament():
    """Convention 8. The card's whole job is photo + name + price + status; a variant that
    renders the shell without the data is a pass on distinctness and a failure in fact."""
    s = _sections("puppy-card")
    for v, inner in sorted(s.items()):
        assert "£1," in inner, v          # £1,500 / £1,700 from data/puppies.json
        assert "Available" in inner, v
        assert "srcset=" in inner, v      # astro:assets, not a single fixed width
    assert "badge" in s["a"], "variant a carries the price badge"
    assert "ribbon" in s["b"], "variant b carries the status ribbon"
    assert "ribbon" not in s["a"] and "badge" not in s["b"]
