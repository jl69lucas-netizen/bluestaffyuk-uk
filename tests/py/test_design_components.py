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
DIST_ROUTE = ROOT / "dist/design-canvas/index.html"


@pytest.mark.xfail(strict=True, reason="kit lands in Tasks 5-15")
def test_route_is_noindex_and_mounts_every_component_variant():
    t = ROUTE.read_text()
    # The prop, not the bare word: the file's header comment also says "noindex", so
    # `'noindex' in t` would keep passing with the prop deleted from the BaseLayout call.
    assert 'noindex={true}' in t
    for r in load():
        stem = r["file"].removesuffix(".astro")
        assert f"import {stem} from" in t, stem


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
    assert 'name="robots" content="noindex' in html
