"""data/design/components.json is the one list of kit components; everything else
(the kit folder, the canvas route, the picks board, picks.json) is checked against it."""
import json, pathlib, re, subprocess

import pytest

import verbatim_set_check as V

ROOT = pathlib.Path(__file__).resolve().parents[2]
COMPONENTS = ROOT / "data/design/components.json"
KIT = ROOT / "src/components/kit"
IDS = ["site-header", "hero", "buttons", "puppy-card", "trust-strip", "counter-strip",
       "info-card", "testimonial", "faq", "contact-form", "page-nav", "footer", "section-divider",
       # Project 4 adds the three in-page navigation components. They are LAST on purpose:
       # the numbering in `title` is the spec's reading order and the board sheets are cut
       # in it. The set is the dial (>=1024px) and, below it, the strip and the sheet.
       "page-dial", "section-sheet", "section-strip",
       # And component 17, the data table (working rule 13; spec §9 amendment 5), and
       # component 18, the video embed (working rule 14; spec §9 amendment 7).
       "data-table", "video-embed"]

#: The city components (project 5; the London component design pass, Plan 2): one row per
#: city component built from a city's picks, previewed on /kit-preview/city/, in city-page
#: order (scripts/city_components.py). tests/py/test_city_kit.py holds them.
CITY_IDS = ["city-hero-filmstrip", "city-price-scale", "city-trust-ledger", "city-contents-photo-index", "city-dial-photo-marker",
            "city-jump-stepper", "city-takeaways-ledger", "city-puppy-sheet", "city-roster", "city-video-panel",
            "city-chapters", "city-letter", "city-faq-ledger", "city-newsletter-notice", "city-contact-lineup"]


def load():
    return json.loads(COMPONENTS.read_text())


def test_every_component_in_spec_order():
    rows = load()
    assert [r["id"] for r in rows] == IDS + CITY_IDS


def test_each_row_has_file_title_width():
    for r in load():
        assert re.fullmatch(r"[A-Z][A-Za-z]+\.astro", r["file"]), r
        assert r["title"] and isinstance(r["title"], str)
        assert r["board_width"] in (640, 1280), r
        # Which project added the row. The canvas, the picks board and the variant prune
        # filter to 3 — they record project 3's closed five-option pick process; the kit
        # preview, _registry.ts and the Design System artifact carry every row.
        assert r["project"] in (3, 4, 5), r


def test_ids_and_files_are_unique():
    rows = load()
    ids, files = [r["id"] for r in rows], [r["file"] for r in rows]
    assert len(set(ids)) == len(ids), sorted(i for i in ids if ids.count(i) > 1)
    assert len(set(files)) == len(files), sorted(f for f in files if files.count(f) > 1)


def test_kit_file_exists_for_each_row():
    missing = [r["file"] for r in load() if not (KIT / r["file"]).exists()]
    assert not missing, missing




MARK = KIT / "Mark.astro"
MARK_SHAPES = KIT / "markShapes.ts"
MARK_SPRITE = KIT / "MarkSprite.astro"


def test_mark_geometry_is_one_badge_on_a_100_grid_with_no_hex():
    """Spec §11 amendment 3a: the five stroke options were replaced by ONE filled badge,
    and Task 19 removed the prop that used to name them.

    The paths live in markShapes.ts, once, because the sprite and the standalone copy both
    draw them and two copies of a twelve-path head is two drawings that drift. Two
    `<circle>` and no more — the roundel and the brass ring. The eye catchlights are
    `<ellipse>` with rx == ry on purpose, so this count stays a statement about the badge
    frame rather than a tally of every round thing in the head."""
    t = MARK_SHAPES.read_text()
    assert "MARK_VIEWBOX = '0 0 100 100'" in t
    assert t.count("<circle") == 2, "the badge and its ring, nothing else"
    assert 'fill="#' not in t and 'stroke="#' not in t
    for token in ("--color-cta", "--color-brand-mid", "--color-brand-tint", "--color-surface-deep"):
        assert f"var({token})" in t, token


def test_mark_is_a_use_at_the_document_sprite_with_a_standalone_escape_hatch():
    """A page carries the mark in the header, in every divider and in the footer, so it is
    drawn once into the document's two <symbol>s and referenced after that. `standalone`
    inlines the paths for a document with no sprite to point at — which is what the Task 20
    lockup files are."""
    t = MARK.read_text()
    assert "<use href={spriteHref(inverse)} />" in t
    assert "standalone = false" in t and "markBody(" in t
    # The name is on the referencing <svg>, where each caller decides content vs ornament.
    assert "<title>{title}</title>" in t
    assert t.count("<svg") == 1
    # No geometry here any more: the paths are markShapes.ts's.
    assert "<circle" not in t and "<path" not in t


def test_the_sprite_carries_both_marks_and_is_out_of_the_accessibility_tree():
    t = MARK_SPRITE.read_text()
    assert "MARK_SPRITE_ID}" in t and "MARK_SPRITE_ID_INVERSE}" in t
    assert t.count("<symbol id=") == 2
    assert 'aria-hidden="true"' in t
    # The inverse symbol swaps the roundel fill and the outline stroke, and nothing else.
    assert "markBody('var(--color-brand)', 'var(--color-surface)')" in t
    assert "markBody('var(--color-surface)', 'var(--color-brand)')" in t


def test_the_layout_emits_the_sprite_once():
    """Once per document, in BaseLayout — not once per <Mark />, which is the whole point."""
    t = (ROOT / "src/layouts/BaseLayout.astro").read_text()
    assert "import MarkSprite from '../components/kit/MarkSprite.astro';" in t
    assert t.count("<MarkSprite />") == 1


def test_built_pages_carry_one_sprite_and_the_kit_references_it():
    """Every page gets the sprite, because BaseLayout emits it; the pages that mount the
    kit point at it. Project 4 replaces SiteHeader/SiteFooter with the kit's, at which
    point every page does both."""
    for page_path in ("dist/index.html", "dist/kit-preview/index.html"):
        built = ROOT / page_path
        if not built.exists():
            pytest.skip("run npm run build first")
        html = built.read_text()
        assert html.count('id="bsuk-mark"') == 1, page_path
        assert html.count('id="bsuk-mark-inverse"') == 1, page_path
    kit = (ROOT / "dist/kit-preview/index.html").read_text()
    assert 'href="#bsuk-mark"' in kit
    assert 'href="#bsuk-mark-inverse"' in kit
    # …and no <Mark /> carries its own copy of the paths: every one of them is a <use>.
    # Four copies of the skull outline reach the page, and only four — one in each of the
    # sprite's two symbols, plus the header and footer lockups, which are standalone SVG
    # *documents* (public/brand/*.svg, generated from this same geometry in Task 20) and so
    # have no sprite to point at when the legacy shell inlines them. A fifth copy would be
    # a <Mark /> that inlined itself, which is the duplication the sprite exists to prevent.
    assert kit.count('d="M-30 -14 C-30 -34') == 4, (
        "two symbols plus the two shell lockups, and nothing else")


CANVAS_ROUTE = ROOT / "src/pages/design-canvas"
ROUTE = ROOT / "src/pages/kit-preview/index.astro"
REGISTRY_TS = KIT / "_registry.ts"
DIST_ROUTE = ROOT / "dist/kit-preview/index.html"


def test_no_canvas_route_after_prune():
    """Task 19. The canvas existed to compare five options per component; the picks are
    made and the losers are gone, so the route that mounted them is gone too. Its two jobs
    that outlived it — a source for the artboard builder, and a place for the per-component
    dist assertions below to point at — moved to src/pages/kit-preview/."""
    assert not CANVAS_ROUTE.exists(), "src/pages/design-canvas/ must not come back"
    assert not (KIT / "_variant.ts").exists()
    assert ROUTE.exists(), "the kit preview route replaces it"


def test_preview_route_is_noindex():
    # The prop, not the bare word: the file's header comment also says "noindex", so
    # `'noindex' in t` would keep passing with the prop deleted from the BaseLayout call.
    assert 'noindex={true}' in ROUTE.read_text()


def test_registry_has_an_entry_for_every_component():
    # The preview renders whatever REGISTRY holds and has no per-component branches, so the
    # registry - not the route's import list - is what has to name all thirteen ids.
    body = REGISTRY_TS.read_text().split("export const REGISTRY", 1)[1]
    missing = [r["id"] for r in load()
               if f"'{r['id']}'" not in body and not re.search(rf"\b{r['id']}\s*:", body)]
    assert not missing, missing


def test_built_preview_is_noindex():
    # Deliberately its own test: the route being noindex is what keeps it out of every
    # sitemap and out of the search index, with no second exclusion list to maintain.
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    assert 'name="robots" content="noindex' in DIST_ROUTE.read_text()


#: The preview's own sections. `(.*?)</section>` stops at the FIRST closing tag, so for a
#: component that is itself a <section> the match ends at the component's own close — which
#: still contains everything it rendered. A component that renders TWO sections (the
#: testimonial's two modes) needs the dedicated reader further down.
SECTION_RE = re.compile(r'<section[^>]*data-component="([a-z-]+)"[^>]*>(.*?)</section>', re.S)


def test_built_preview_has_one_section_per_component():
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    found = [cid for cid, _ in SECTION_RE.findall(DIST_ROUTE.read_text())]
    # The mark has no components.json row and no artboard; it is shown here on both
    # surfaces it has to work on, and the builder skips it.
    assert found == ["mark"] + IDS, found


def test_built_sections_spell_no_hex_in_a_style_attribute():
    """Rule 1, on the one page that mounts the whole kit. Inline styles are where a colour
    gets spelled by hand, because a style attribute is the one place a scoped stylesheet
    review does not look."""
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    for cid, inner in SECTION_RE.findall(DIST_ROUTE.read_text()):
        hexes = re.findall(r'style="[^"]*#[0-9A-Fa-f]{3}', inner)
        assert not hexes, (cid, hexes)


def _sections(cid):
    """The built preview section for one component.

    A registered component with no section is a failure, not a skip: that is exactly what
    a route regression looks like, and skipping it would hide one."""
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    out = [inner for c, inner in SECTION_RE.findall(DIST_ROUTE.read_text()) if c == cid]
    assert len(out) == 1, (cid, len(out))
    return out[0]


def _has_class(html, token):
    """True when `token` appears as a class TOKEN in a class attribute.

    Astro appends its own `astro-cid-*` class to every styled element, and the scoped
    stylesheet inside the same section spells every class name this file looks for, so a
    bare `"cols" in inner` passes on a component that renders no such element at all."""
    return any(token in value.split()
               for value in re.findall(r'class="([^"]*)"', html))


def test_built_site_header_is_logo_only_with_the_search_pill_and_the_drawer():
    """Convention 8, and spec §11 amendment 3b's half of it. A header that quietly lost the
    drawer, the search form or the mark would still build and would still be a header."""
    settings = json.loads((ROOT / "data/settings.json").read_text())
    inner = _sections("site-header")
    assert "<details" in inner, "the mobile drawer"
    assert "Open menu" in inner and "Close menu" in inner
    assert 'aria-label="Main"' in inner
    assert 'role="search"' in inner and 'action="/search/"' in inner
    assert 'name="q"' in inner
    assert 'id="site-search-results"' in inner
    # Logo only: the brand link is the mark, named by its aria-label, with no wordmark text.
    assert f'aria-label="{settings["site_name"]} home"' in inner
    assert "<svg" in inner
    assert "kit-mark" in inner
    # The call to action survives the prune; the strapline (a losing option's) does not.
    assert 'href="/available-puppies/"' in inner
    assert settings["location_label"] not in inner


def test_the_header_search_is_one_combobox_with_one_of_everything():
    """Spec §11 amendment 3b, and the a11y half of it.

    ONE form. The drawer used to carry a second copy, which meant two inputs, two result
    lists and a duplicated `#site-search-results-drawer` — one search on one page announced
    as two. Below 768px CSS gives the single form a full-width row when the drawer is open.

    And it is a COMBOBOX, marked up as one: without `role="combobox"`, `aria-expanded`,
    `aria-controls` and `aria-activedescendant`, the result list was a panel a mouse could
    reach and a keyboard could not — and the arrow keys had nothing to move."""
    inner = _sections("site-header")
    assert inner.count("<form") == 1, "one search form on the page, not one per surface"
    assert inner.count('name="q"') == 1
    assert "site-search-results-drawer" not in inner
    for expect in ('role="combobox"', 'aria-expanded="false"',
                   'aria-controls="site-search-results"', 'aria-autocomplete="list"',
                   'aria-describedby="site-search-hint"'):
        assert expect in inner, expect
    # One hint, on the one input, and it names the keys.
    assert inner.count('id="site-search-hint"') == 1
    for key in ("arrow", "Enter", "Escape"):
        assert key in inner, key
    # The list is NOT a live region: a live region holding the active option is
    # re-announced on every arrow press. The count goes to a separate polite status line.
    results = inner[inner.index('id="site-search-results"'):]
    results = results[: results.index("</ul>")]
    assert "aria-live" not in results, "the result list must not be a live region"
    assert 'id="site-search-status"' in inner and 'role="status"' in inner
    assert 'aria-live="polite"' in inner


def test_the_header_search_script_handles_the_combobox_keys_smoke():
    """A SMOKE CHECK, and named one: it greps the component source for the key names.

    Grepping a source file cannot tell a handler that moves the highlight from one that
    names the key and does nothing, so this proves only that the wiring has not been
    deleted wholesale. The real coverage is `tests/render/kit-search.spec.ts`, which drives
    the built page in a browser: types, arrows, presses Enter and clicks a result with the
    mouse. Kept beside it because it runs in the Python gate with no browser and fails in
    milliseconds when someone removes a branch."""
    t = (KIT / "SiteHeaderKit.astro").read_text()
    for key in ("'ArrowDown'", "'ArrowUp'", "'Home'", "'End'", "'Enter'", "'Escape'"):
        assert key in t, key
    assert "aria-activedescendant" in t
    assert "focusout" in t, "the list is dismissed when focus leaves the form"
    assert "optionIdPrefix" in t, "the list is rendered with listbox roles"


def test_built_hero_carries_its_photo_copy_chips_and_ctas():
    """Convention 8. The hero's job is one heading, one lede, the trust chips and — as the
    picked layout shows one — a responsive photo."""
    inner = _sections("hero")
    # The preview fixture passes as="h2" so the page keeps one h1; the component's default
    # is h1 and that is what project 4 will render.
    assert 'class="title' in inner and "<h2" in inner
    assert "KC registered" in inner
    assert "Carlisle" in inner
    assert "srcset=" in inner, "astro:assets, not a single fixed width"
    assert _has_class(inner, "pic")
    assert _has_class(inner, "chips")
    assert _has_class(inner, "ctas")
    # The picked layout sits on the bone surface; it paints no band of its own.
    assert 'data-surface="inverse"' not in inner


def test_built_hero_puts_the_image_before_the_heading():
    """rules/design.md rule 10, first half (spec §11 amendment 3c). SOURCE ORDER, not the
    painted layout: `order` moves the photo back to the right of the copy on screen, so the
    only way to see this is where the <img> sits in the markup."""
    inner = _sections("hero")
    img = inner.find("<img")
    head = inner.find("<h2")
    assert img != -1 and head != -1
    assert img < head, "the hero image must precede the heading in the DOM"


HEIGHTS = ROOT / "data/design/canvas-heights.json"


def test_measured_hero_fits_its_clamp_without_clipping_anything():
    """rules/design.md rule 10, second half — and the half a board height cannot prove.

    The old version of this test read the rounded artboard height and called <= 472 a pass.
    That number is produced by `max-height` whether the copy FITS in the clamp or is being
    CUT OFF by it, so a hero with its CTA row sliced in half measured exactly as well as one
    that fitted. scripts/measure_canvas_heights.mjs therefore records, at each of the three
    desktop widths where the clamp is live, the scroll overflow of `.inner` and of the
    section, the scroll overflow of the LEDE, and where the CTA row's bottom edge sits
    relative to the section's own. Overflow of zero and a CTA row at or above the section's
    bottom is the real assertion; the 390-450 band is checked on the unrounded section
    height beside it."""
    if not HEIGHTS.exists():
        pytest.skip("run npm run canvas:heights first")
    data = json.loads(HEIGHTS.read_text())
    heroes = data.get("hero_overflow")
    assert heroes, "canvas-heights.json has no hero_overflow block — re-run npm run canvas:heights"
    for key, widths in sorted(heroes.items()):
        for w in ("1024", "1100", "1280"):
            m = widths.get(w)
            assert m is not None, (key, w, "not measured")
            assert m["overflow"] == 0, (key, w, m, ".inner is clipping its own copy")
            assert m["section_overflow"] == 0, (key, w, m, "the hero section is clipping content")
            # The lede is the ONE element rule 10 clamps, and a clamp hides its own
            # overflow: a third line is never pushed past the ceiling where the two figures
            # above would catch it, it is simply not painted. Held to two lines AND
            # measured, so the clamp can never become the thing that makes the copy fit.
            assert m["lede_overflow"] == 0, (
                key, w, m,
                "the lede runs past the two lines the clamp paints — shorten the copy",
            )
            if m["ctas_below"] is not None:
                assert m["ctas_below"] <= 0, (key, w, m, "the CTA row hangs below the hero")
            # NOT RUNNING INTO THE NEXT SECTION holds at EVERY width, and it is the one thing
            # the three figures above cannot see: all three are taken INSIDE the hero, so
            # content spilling out of a box whose ceiling has been released registers as zero
            # on every one of them. That is exactly what Known Issue 28 was — the homepage's
            # hero content ended 17px inside the section below it at 1024, and nothing here
            # noticed.
            if m.get("next_overlap") is not None:
                assert m["next_overlap"] <= 0, (
                    key, w, m, "the hero's content runs into the section below it")
            # The 390 FLOOR is live from 1024 (`.inner` keeps its `min-height`), so a hero
            # that collapses is still caught at every width.
            assert m["height"] >= 390, (key, w, m["height"])
            # THE CEILING IS A 1280 MEASURE (spec §9 amendment 10.4 sub-note, breeder
            # 2026-09-21). Between 1024 and 1279 the copy column is narrower and the same
            # words take more lines; a verbatim H1 cannot be shortened to fit a band written
            # for 1280 (working rule 15), so the band gives way and the clamp is scoped to
            # 1280 and up. Asserting 450 below it is asserting the defect: it is what hid
            # three to six lines of four pages' ledes and ran two heroes into the section
            # beneath them.
            if w == "1280":
                assert m["height"] <= 450, (key, w, m["height"])


def test_built_buttons_show_all_five_kinds():
    """Task 19 kept the five button treatments and renamed them `kind`, because a page
    needs more than one: they are five jobs, not five styles of one. The preview mounts all
    five, and a kind that silently stopped painting differently would be a kind a page could
    not reach."""
    inner = _sections("buttons")
    kinds = re.findall(r'data-kind="([a-z]+)"', inner)
    assert sorted(kinds) == ["inverse", "outline", "primary", "submit", "text"], kinds
    # The text kind is the only one carrying the arrow glyph, and it is an inline stroke
    # SVG rather than a character (rule 7).
    assert inner.count("<svg") == 1 and 'stroke="currentColor"' in inner
    # The submit kind is the only <button>; the rest are links.
    assert inner.count("<button") == 1 and 'type="submit"' in inner


def test_built_puppy_card_carries_price_status_and_the_chip_row():
    """Convention 8, and rule 9's half of it: every figure on the card is read from
    data/puppies.json, so a reserved pup or a price change is a data edit."""
    pups = {p["slug"]: p for p in json.loads((ROOT / "data/puppies.json").read_text())}
    inner = _sections("puppy-card")
    for slug in ("roman", "christa"):
        p = pups[slug]
        assert f"£{p['price_gbp']:,}" in inner, slug
        assert p["status"] in inner, slug
        assert p["name"] in inner, slug
    assert "srcset=" in inner, "astro:assets, not a single fixed width"
    # The picked card puts the price in the chip row and paints nothing over the photograph.
    assert _has_class(inner, "strong"), "the price chip"
    assert not _has_class(inner, "badge") and not _has_class(inner, "ribbon")


def test_built_trust_strip_carries_three_backed_claims_and_line_icons():
    """Convention 8. Rule 7: the icons are inline stroke SVG, never an emoji. Rule 9: each
    claim is one the live homepage already makes (KC registration, L-2-HGA / HC-HSF4 clear
    parents, home rearing) — a strip that invented a fourth would be a statutory statement
    with nothing behind it."""
    inner = _sections("trust-strip")
    for claim in ("KC registered", "DNA-tested parents", "Raised in the home"):
        assert claim in inner, claim
    assert "L-2-HGA" in inner, "the picked strip carries the description sentences"
    assert inner.count("<svg") == 3
    assert 'stroke="currentColor"' in inner
    # Rule 7, measured rather than asserted by keyword: an icon is an inline stroke SVG,
    # so there is no <img> in the strip and no character in the emoji planes.
    assert "<img" not in inner
    assert not [c for c in inner if ord(c) >= 0x1F000]
    assert 'data-surface="inverse"' in inner, "the picked strip is the steel band"


def test_built_counter_strip_keeps_the_harness_hooks_and_the_data_figures():
    """Convention 8. `.counter-wrap` and `[data-counters]` are what
    tests/render/checks/layout.ts selects on: rename either and the
    layout-hero-counter-separation check examines zero elements and passes vacuously.
    The figures are read from the data here too, so a sold puppy is a data edit."""
    settings = json.loads((ROOT / "data/settings.json").read_text())
    pups = json.loads((ROOT / "data/puppies.json").read_text())
    available = sum(1 for p in pups if p["status"] == "Available")
    inner = _sections("counter-strip")
    assert "counter-wrap" in inner and "data-counters" in inner
    assert f">{available}<" in inner, available
    assert f"£{settings['deposit_gbp']}" in inner
    assert f"£{settings['delivery_min_gbp']}" in inner
    assert f"£{settings['delivery_max_gbp']}" in inner
    # The picked treatment is the inline line, so it carries the dots between the pairs.
    assert _has_class(inner, "dot")


def test_kit_counter_fixture_hexes_are_the_tokens_they_stand_for():
    """The fixture pair spells hex because a fixture is test data served as a static file —
    it cannot read tokens.css. That freedom is also the failure mode: retune --counter-bed
    and the fixture goes on proving that some OTHER bed clears the check while the shipped
    component no longer does. This binds the two, so a token change that orphans the fixture
    fails here instead of passing silently."""
    from test_design_tokens import layers, resolve

    L = layers()
    fixture = (ROOT / "tests/render/fixtures/known_good/kit-counter-separated.html").read_text()
    lowered = fixture.lower()
    for token in ("--counter-bed", "--color-border", "--color-surface-inverse"):
        value = resolve(token, L)
        assert re.fullmatch(r"#[0-9a-fA-F]{6}", value), (token, value)
        assert value.lower() in lowered, (
            f"{token} resolves to {value}, which the kit counter fixture does not spell; "
            f"the fixture is no longer the shipped component's geometry")


def test_built_info_card_carries_a_kinded_statement_label():
    """Convention 8, and the deferred check's half of it.

    `sem-statement-label-visible` requires every `.stmt-label` to be painted AND to carry a
    data-kind of fact/observed/recommendation; a label that lost its kind, or a card that
    quietly stopped rendering one, would break the check with nothing else to say so. The
    kinds come from the registry's two demo fixtures."""
    inner = _sections("info-card")
    # Counted on the class token, not on a whole attribute: Astro appends its scoped
    # `astro-*` class to every element its <style> matches.
    assert len(re.findall(r'\bstmt-label\b', inner)) == 2, "one label per demo fixture"
    assert 'data-kind="fact"' in inner
    assert 'data-kind="recommendation"' in inner
    assert re.search(r'data-kind="(?!fact|observed|recommendation)', inner) is None
    # The image-top layout was one of the losing options: the card no longer owns a
    # sectional image, and layout-h3-image-first's coverage is its fixture pair.
    assert "sec-img" not in inner


# Attribute ORDER is Astro's business, not this test's: the day the preview page grew a
# <style> block, Astro began propagating its scope attribute onto the mounted components'
# roots, `class` stopped being the first attribute on the section, and a pattern anchored to
# `<section class="kit-quote` found nothing — reporting "the preview builds no testimonial"
# for a page that builds two. Match the tag, then the class token inside it.
QUOTE_BLOCK_RE = re.compile(
    r'<section\b([^>]*\bclass="[^"]*\bkit-quote\b[^"]*"[^>]*)>(.*?)</section>', re.S
)


def _quote_blocks():
    """Every Testimonial the preview built, keyed by mode.

    Read off the component's OWN sections rather than through `_sections`: the preview's
    wrapper is a <section> too, and the outer match stops at the first nested `</section>`,
    so the second block would be invisible from there."""
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    out = {}
    for attrs, inner in QUOTE_BLOCK_RE.findall(DIST_ROUTE.read_text()):
        m = re.search(r'data-mode="(\w+)"', attrs)
        out[m.group(1) if m else "?"] = attrs + inner
    return out


def test_built_testimonial_blocks_quote_the_reviews_file_verbatim_in_both_modes():
    """Convention 8, and rule 9's half of it. A testimonial component is the easiest place
    in the kit to invent a claim, so the built blocks are compared against data/reviews.json
    rather than against a shape: every block must print the reviews it shows word for word.
    If a review is a REVIEW_PLACEHOLDER row it still has to appear, because a slot silently
    dropped is the same defect as a slot silently invented.

    Spec §11 amendment 3e: how many it shows is `mode`, which is what survived the prune —
    `single` is one review given room, `grid` is the strip — so both are built here and
    both are asserted."""
    reviews = json.loads((ROOT / "data/reviews.json").read_text())
    assert len(reviews) == 3, len(reviews)
    blocks = _quote_blocks()
    assert sorted(blocks) == ["grid", "single"], sorted(blocks)

    def printed(text, inner):
        # The built HTML escapes & < >; nothing else in these quotes needs escaping.
        return text.replace("&", "&#38;").replace("<", "&#60;").replace(">", "&#62;") in inner

    for mode, inner in sorted(blocks.items()):
        shown = reviews if mode == "grid" else reviews[:1]
        for r in shown:
            assert printed(r["quote"], inner), (mode, r["name"], "quote not printed verbatim")
            assert printed(r["name"], inner), (mode, r["name"])
        if mode == "single":
            assert not printed(reviews[2]["quote"], inner), "single mode shows one review"
        # the container follows the mode
        assert f'class="container {mode if mode == "grid" else "stack"}' in inner, mode
        # the picked treatment is the steel band, in either mode
        assert 'data-surface="inverse"' in inner, mode


def test_the_testimonial_takes_an_explicit_review_list():
    """Spec §11 amendment 3e, and rules/copy.md's review placement. A page with more
    reviews than one block shows has to be able to place THE REMAINDER, so `reviews` is an
    explicit list the caller passes and the component renders in full; passing nothing
    keeps the component's own slice of data/reviews.json."""
    t = (KIT / "Testimonial.astro").read_text()
    assert "reviews?: Review[]" in t
    assert "reviews ?? (mode === 'grid'" in t


def test_reviews_json_quotes_exist_verbatim_on_the_page_each_one_names():
    """Rule 9, enforced at the source. Each row carries the path it was copied from; this
    reads that file and fails if the quote or the attribution is not in it character for
    character. A REVIEW_PLACEHOLDER row has no source and is exempt — that is the whole
    point of the placeholder.

    THE SOURCE IS THE MIGRATED PAGE, so a REBUILT page is read at the migration commit and
    not out of the working tree. `source` records where a quote was copied FROM — a
    WordPress body the extractor wrote into `const body` — and project 4 replaces those
    files one at a time: from Task 18 the homepage is a hand-written Astro page with no
    `const body` in it at all, and reading the working tree would fail a row whose evidence
    is intact. `verbatim_set_check.MIGRATED` is the same frozen commit rule 15's own gate
    reads, for the same reason: it is history and cannot move."""
    reviews = json.loads((ROOT / "data/reviews.json").read_text())
    for r in reviews:
        if r["quote"] == "REVIEW_PLACEHOLDER":
            assert r["source"] == "", r
            continue
        page = (ROOT / r["source"]).read_text()
        m = re.search(r'const body = "(.*?)";\n', page, re.S)
        if not m:
            migrated = subprocess.run(
                ["git", "show", f"{V.MIGRATED}:{r['source']}"],
                cwd=ROOT, capture_output=True, text=True)
            assert migrated.returncode == 0, (r["source"], migrated.stderr)
            m = re.search(r'const body = "(.*?)";\n', migrated.stdout, re.S)
        assert m, r["source"]
        body = m.group(1).encode().decode("unicode_escape").encode("latin-1").decode("utf-8")
        assert r["quote"] in body, (r["source"], r["quote"][:60])
        assert r["name"] in body, (r["source"], r["name"])
        assert r["place"] in body, (r["source"], r["place"])


def test_built_faq_is_native_details_with_backed_answers():
    """Convention 8. Two things are pinned here. First the element: a kit that quietly
    swapped <details> for a scripted div would lose keyboard operation, find-in-page and
    the no-JavaScript open, and every other test would stay green. Second the copy: the
    questions and answers are read out of data/faq.json with the same interpolation
    src/lib/faq.ts performs, so an answer edited in the component instead of in the data —
    or a price edited in settings and left stale in the FAQ — fails here."""
    settings = json.loads((ROOT / "data/settings.json").read_text())
    rows = json.loads((ROOT / "data/faq.json").read_text())
    tokens = {
        "deposit_gbp": str(settings["deposit_gbp"]),
        "delivery_min_gbp": str(settings["delivery_min_gbp"]),
        "delivery_max_gbp": str(settings["delivery_max_gbp"]),
        "delivery_note": settings["delivery_note"],
        "deposit_terms": "refundable" if settings["deposit_refundable"] else "non-refundable",
        "guarantee_label_lc": settings["guarantee_label"][:1].lower() + settings["guarantee_label"][1:],
        "guarantee_phrase": settings["guarantee_label"].split(" ", 1)[1] + ", which " + settings["guarantee_cover"] + ",",
    }
    resolved = [
        {"q": r["q"], "a": re.sub(r"\{([a-z_]+)\}", lambda m: tokens[m.group(1)], r["a"])}
        for r in rows
    ]
    inner = _sections("faq")
    assert inner.count("<details") == len(rows)
    assert inner.count("<summary") == len(rows)
    # The question is a heading inside the summary, so the answers are a navigable list.
    assert len(re.findall(r'<h3[^>]*\bq\b[^>]*>', inner)) == len(rows)
    # CASE-INSENSITIVE, deliberately. The question is rendered in Title Case
    # (rules/headings.md, amended 2026-09-20: an `<h3>` inside a `<summary>` is still a
    # heading) while data/faq.json keeps the sentence-case wording, which is what the FAQPage
    # schema `name` and the dup gate read. Asserting the exact cased string here would need a
    # Python port of src/lib/headings.ts, and a second caser is a caser that drifts — the CASE
    # is already measured by tests/render/checks/sem.ts::sem-title-case-headings, which sees
    # these h3s. What this test owns is that the ROW reached the page at all.
    for r in resolved:
        assert r["q"].lower() in inner.lower(), r["q"]
        assert r["a"] in inner, r["a"]
    # The picked treatment is the numbered one, and it carries no marker glyph.
    assert ">01<" in inner and f">{len(rows):02d}<" in inner
    assert "<svg" not in inner


def test_the_contact_page_itself_still_posts_to_the_live_endpoint():
    """The preview's specimen is excluded from the per-page FIELD contract, which is only
    safe while the REAL contact page still posts to the one Formspree endpoint. Skipped,
    not silently passed, when the id is unset: the built page then legitimately carries the
    local stub."""
    import os
    if not os.environ.get("PUBLIC_FORMSPREE_ID"):
        pytest.skip("PUBLIC_FORMSPREE_ID unset; the built contact page carries the stub")
    built = ROOT / "dist/uk-blue-staffy-breeders-contact/index.html"
    if not built.exists():
        pytest.skip("run npm run build first")
    actions = re.findall(r'<form[^>]*\saction="([^"]*)"', built.read_text())
    inquiry = [a for a in actions if not a.startswith("/search")]
    assert inquiry, actions
    for a in inquiry:
        assert a.startswith("https://formspree.io/f/"), a


def test_built_contact_form_keeps_the_whole_form_contract():
    """Convention 8, and spec §11 amendment 2's half of it.

    The preview route is excluded from form_contract_audit.py's per-page FIELD contract
    (NON_CONTENT_ROUTES) because a specimen of the form is not a reachable enquiry form.
    That exclusion is only safe while something else proves the specimen still carries the
    contract — this is that something. It must show the six named controls with the built
    page's required set, the honeypot, both hidden fields, POST, and an endpoint built from
    the environment rather than spelled in the component. The puppy options are read from
    data/puppies.json, so a reserved pup is a data edit and not a test edit."""
    pups = json.loads((ROOT / "data/puppies.json").read_text())
    available = [p for p in pups if p["status"] == "Available"]
    assert available, "the fixture needs at least one available puppy"
    inner = _sections("contact-form")
    assert 'method="POST"' in inner
    assert 'name="_gotcha"' in inner
    for hidden in ('name="_next"', 'name="_subject"'):
        assert hidden in inner, hidden
    for key in ("name", "email", "phone", "location", "puppy", "message"):
        assert f'name="{key}"' in inner, key
    # The four the built contact page marks required; phone and location are optional
    # there, and a kit form that demanded them would not be the same form.
    for key in ("name", "email", "puppy", "message"):
        assert re.search(rf'name="{key}"[^>]*\brequired\b|\brequired\b[^>]*name="{key}"',
                         inner), key
    assert '<select' in inner and 'name="puppy"' in inner
    for p in available:
        assert f'value="{p["slug"]}"' in inner, p["slug"]
    assert 'value="waiting-list"' in inner
    assert "<textarea" in inner
    # The endpoint is built from the environment, so the specimen posts wherever the real
    # contact page posts and nowhere else. Compared against THAT page's built action rather
    # than against the current environment: both were written by the same build, and reading
    # os.environ here fails whenever the suite runs without the id that built dist/.
    # There is no `action` override prop any more — it existed for the canvas's five
    # specimens and went with the canvas.
    actions = re.findall(r'<form[^>]*\saction="([^"]*)"', inner)
    assert len(actions) == 1, actions
    contact = ROOT / "dist/uk-blue-staffy-breeders-contact/index.html"
    if contact.exists():
        real = [a for a in re.findall(r'<form[^>]*\saction="([^"]*)"', contact.read_text())
                if not a.startswith("/search")]
        assert actions == real[:1], (actions, real)
    assert actions[0].startswith("https://formspree.io/f/") or actions[0] == "#contact", actions
    # The picked layout is the stepped one: three fieldsets, each with a legend.
    assert inner.count("<fieldset") == 3 and inner.count("<legend") == 3


def test_built_page_nav_carries_the_real_trail_and_the_chip_row():
    """Convention 8. Two things are pinned. First the trail: it is produced by crumbs()
    in src/lib/site.ts, so the intermediate label has to be NAV's label for that href and
    the last crumb has to be the page itself, marked aria-current — a breadcrumb whose last
    item is a link is the defect this catches. Second the jump list, which the picked
    treatment paints as a row of chips with no heading over it."""
    inner = _sections("page-nav")
    # The demo's four sections name kit-preview's OWN section anchors, because
    # `nav-anchors-resolve` is blocking and a preview does not get a pass for linking to
    # #temperament on a page that has no such element (Task 21).
    jumps = [("kit-hero", "Hero"), ("kit-puppy-card", "Puppy Card"),
             ("kit-faq", "FAQ"), ("kit-footer", "Footer")]
    assert 'aria-label="Breadcrumb"' in inner
    assert 'href="/"' in inner and ">Home<" in inner
    # The leaf is the page, not a link: crumbs() puts the title last.
    assert 'aria-current="page"' in inner
    assert "Staffordshire Bull Terrier guide" in inner
    assert 'aria-label="On this page"' in inner
    for anchor, label in jumps:
        assert f'#{anchor}"' in inner, anchor
        assert label in inner, label
    # No visible heading over the chips, and no glyph in them: those belonged to the
    # treatments the prune did not keep.
    assert "</h2>" not in inner
    assert "<svg" not in inner
    # One <ol> only — the trail's. The chips are a <ul>.
    assert inner.count("<ol") == 1
    # Nothing pins itself above the jump target any more, so the global [id]
    # scroll-margin-top offset stays correct and project 4 has no extra chrome to clear.
    assert "data-pinned-chrome" not in inner


def test_built_footer_carries_the_nav_the_socials_and_the_contact_rows():
    """Convention 8, and rule 9's half of it. The footer is where invented copy and dead
    links collect, so the built markup is compared against src/lib/site.ts's NAV and
    data/settings.json rather than against a shape: it must link every NAV item and every
    social profile in the settings file, and the contact rows must be the settings email
    and hours rather than a second copy of them."""
    settings = json.loads((ROOT / "data/settings.json").read_text())
    # Parsed from the NAV block alone: a bare href/label pattern over the whole file would
    # also swallow any other array of links src/lib/site.ts grows later.
    site = (ROOT / "src/lib/site.ts").read_text()
    block = re.search(r"export const NAV = \[(.*?)\n\];", site, re.S)
    assert block, "src/lib/site.ts no longer declares NAV as a literal array"
    nav = re.findall(r"\{ href: '([^']+)', label: '([^']+)' \}", block.group(1))
    assert len(nav) == 7, nav
    inner = _sections("footer")
    for href, label in nav:
        assert f'href="{href}"' in inner, href
        assert label in inner, label
    for url in settings["socials"].values():
        assert f'href="{url}"' in inner, url
    assert f'mailto:{settings["email"]}' in inner
    assert settings["hours"] in inner
    assert settings["location_label"] in inner
    assert settings["site_name"] in inner
    assert settings["tagline"] in inner
    assert 'href="/privacy-policy-uk/"' in inner
    assert 'data-surface="inverse"' in inner
    # No colour is spelled in the footer's own markup.
    assert not re.findall(r'style="[^"]*#[0-9A-Fa-f]{3}', inner)
    # Four columns: brand, Explore, Contact, Follow.
    assert inner.count("<h2") == 3, "one heading per link column"
    assert 'width="40"' in inner, "the footer mark"


def test_built_footer_carries_the_cta_band_and_social_icons():
    """Spec §11 amendment 5. Two things the user kept that the picked arrangement did not
    come with: the call-to-action band that belonged to a losing option, and social ICONS.

    The icons are the part worth pinning. Rule 7 forbids emoji, not brand glyphs, so these
    are inline paths — but an icon-only link announces as its url, so each anchor carries an
    aria-label naming the destination and the icon itself is aria-hidden. A row that lost
    the labels, or grew an <img>, would look identical and read as four unnamed links."""
    settings = json.loads((ROOT / "data/settings.json").read_text())
    inner = _sections("footer")
    # (1) the band, above the columns and before them in source order.
    assert _has_class(inner, "cta-band")
    assert "Ready to meet the litter?" in inner
    assert 'href="/buy-blue-staffy-puppies-uk/"' in inner
    assert inner.index("cta-band") < inner.index("Explore"), "the band sits above the columns"
    # (2) one icon link per profile in the settings file, each named by its destination.
    socials = settings["socials"]
    assert len(socials) == 4, socials
    for url in socials.values():
        assert f'href="{url}"' in inner, url
        assert 'target="_blank"' in inner and 'rel="noopener noreferrer"' in inner
    labels = re.findall(rf'aria-label="{re.escape(settings["site_name"])} on ([^"]+)"', inner)
    assert sorted(labels) == ["Facebook", "Instagram", "X", "YouTube"], labels
    # Four icons plus the footer mark, all inline SVG — never an <img> and never a glyph.
    assert inner.count("<svg") == 5, inner.count("<svg")
    assert "<img" not in inner
    assert not [c for c in inner if ord(c) >= 0x1F000]
    # The icon is decoration beside a name the anchor already announces.
    assert inner.count('aria-hidden="true"') >= 4
    # currentColor only: no brand hex reaches src/ (rule 1).
    assert not re.findall(r"#[0-9A-Fa-f]{6}", inner)


def test_built_section_divider_is_the_mark_between_two_rules():
    """Convention 8. The divider is real structure — role="separator" — with the ornament
    inside hidden from the accessibility tree, because the sections either side already
    carry their own headings."""
    inner = _sections("section-divider")
    assert 'role="separator"' in inner
    assert _has_class(inner, "medal")
    assert len(re.findall(r'class="[^"]*\brule\b', inner)) == 2, "a rule out to each margin"
    # The mark is decorative here: title="" drops the <title> and hides the whole SVG.
    assert 'aria-hidden="true"' in inner
    assert "<title>" not in inner



def test_built_page_dial_is_a_numbered_strip_with_spy_hooks_and_no_ring():
    """Convention 8. The dial is two things at once — a numbered list and a scroll-spy —
    and losing either still builds and still looks like a sidebar. The six `<li>` are the
    demo fixture's six sections.

    THE RING IS ASSERTED ABSENT, not merely unmentioned. The breeder picked S2 on the
    contact board (2026-09-19) and PageDial was pruned to it; a ring creeping back would be
    a second progress indicator saying what the numbered rows already say, and the inline
    dash geometry it needed was the component's only inline style."""
    dial = _sections("page-dial")
    assert _has_class(dial, "kit-dial")
    # Labelled BY the visible heading, never by a duplicate literal: a `<nav aria-label>`
    # and a visible "On this page" would give a screen-reader user different words from the
    # ones on the screen.
    assert "<nav" in dial and 'aria-labelledby="kit-dial-title"' in dial
    assert 'id="kit-dial-title"' in dial
    assert dial.count("<li") >= 6, dial.count("<li")
    assert dial.count('data-spy="') >= 6, dial
    # Every row is numbered — that is what the picked arrangement is.
    assert dial.count('class="num"') >= 6, dial.count('class="num"')
    # …and the ring is gone, markup, hooks and all.
    assert "<circle" not in dial, dial
    assert "data-ring" not in dial, dial
    # Rule 1, restated at the component. The dial no longer writes ANY inline style — the
    # ring's dash geometry was the only one — so the hex probe has nothing to find.
    assert not re.findall(r'style="[^"]*#[0-9A-Fa-f]{3,6}', dial), dial


PROJECT_4_IDS = ["page-dial", "section-sheet", "section-strip", "data-table", "video-embed"]


def test_components_json_has_eighteen_rows_after_project_4_additions():
    """Project 4's five additions are appended, not interleaved. Spelled as its own test
    because IDS above is the list every other test walks: if the five rows were ever moved
    ahead of the project 3 thirteen, the board sheets and the artboard numbering would
    silently renumber while `test_every_component_in_spec_order` stayed green."""
    ids = [r["id"] for r in load() if r["project"] != 5]
    assert len(ids) == 18, ids
    assert ids[-5:] == PROJECT_4_IDS, ids[-5:]
    by_project = {r["id"]: r["project"] for r in load()}
    # The city rows come after all eighteen and are the only project 5 rows.
    assert [i for i, p in by_project.items() if p == 5] == CITY_IDS
    assert [r["id"] for r in load()][18:] == CITY_IDS
    assert [i for i, p in by_project.items() if p == 4] == PROJECT_4_IDS
    assert len([i for i, p in by_project.items() if p == 3]) == 13


def test_built_section_sheet_has_tab_bar_and_dialog():
    """Convention 8. The sheet is the dial's other half: a fixed tab bar carrying three
    site destinations and a Sections button, and a native <dialog> holding the same six
    sections. `<dialog>` is load-bearing — showModal() is what gives the sheet its focus
    trap and its Escape key, and swapping it for a <div> would lose both silently."""
    s = _sections("section-sheet")
    assert _has_class(s, "kit-tabbar")
    assert s.count("<a ") >= 3, s.count("<a ")
    assert "<button" in s
    assert "<dialog" in s and 'aria-label="Sections"' in s
    # The opener ships its resting state; the script drives it from the dialog's own
    # `close` event, so Escape and a backdrop click cannot leave it stuck on "true".
    assert 'aria-haspopup="dialog"' in s and 'aria-expanded="false"' in s
    # Four line icons, drawn not lettered: three tabs plus Sections. Never an <img>, never
    # an emoji glyph — the same bar the footer's icon row is held to.
    assert s.count("<svg") >= 4, s.count("<svg")
    assert "<img" not in s
    assert not [c for c in s if ord(c) >= 0x1F000]
    assert s.count('data-spy="') >= 6, s
    assert not re.findall(r'style="[^"]*#[0-9A-Fa-f]{3,6}', s), s


#: Every built page, not just the preview. These two are dist-WIDE on purpose: both defects
#: are produced by a component and shipped by whatever page mounts it, so checking only the
#: page the component was written against would miss the next page that mounts it.
DIST = ROOT / "dist"


def _built_pages():
    if not DIST.exists():
        pytest.skip("run npm run build first")
    return sorted(DIST.rglob("index.html"))


def test_no_built_page_ships_an_empty_aria_current():
    """`aria-current=""` is the token `false`.

    `el.toggleAttribute('aria-current', true)` sets the attribute to the empty string, and
    the empty string is not "unspecified" for this attribute — it is an explicit `false`.
    A scroll-spy written that way marks the row the reader is IN as the one row that is
    NOT current, which is worse than marking none of them. The two in-page nav components
    use `setAttribute('aria-current', 'location')`; this is the guard that keeps the next
    one from reaching for `toggleAttribute` because it reads shorter."""
    bad = [(p.relative_to(ROOT), m) for p in _built_pages()
           for m in re.findall(r'aria-current=""', p.read_text())]
    assert not bad, bad[:5]


def test_no_built_page_ships_a_duplicate_id():
    """`getElementById` returns the FIRST match, so a second element with the same id is
    unreachable by script and by fragment, and every `href="#x"` has two destinations with
    only one of them ever chosen.

    kit-preview shipped exactly this when the scroll-spy's six stub targets were rendered
    inside every `with-targets` demo box instead of once per page: `nav-anchors-resolve`
    stayed green because the anchors all resolved — to the first copy. The harness's
    `a11y-no-duplicate-ids` catches it on a painted page; this catches it in dist without
    a browser, on every route at once."""
    offenders = {}
    for p in _built_pages():
        ids = re.findall(r'\sid="([^"]+)"', p.read_text())
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            offenders[str(p.relative_to(ROOT))] = dupes
    assert not offenders, offenders


def test_built_section_strip_is_a_sticky_chip_rail_with_spy_hooks():
    """Convention 8. Component 16 is the top-chrome third of the in-page nav set: a sticky
    rail of six numbered chips that scrolls sideways under the thumb. Three things are
    load-bearing and all three are asserted: it is STICKY (fixed would take it out of flow
    and it would need the body padding the bottom bar needs), every chip carries a
    `data-spy` so the scroll-spy has a row per section, and the chips clear the 44px tap
    target the blocking `layout-tap-target-size` check measures."""
    s = _sections("section-strip")
    assert _has_class(s, "kit-strip")
    assert "<nav" in s and 'aria-label="Sections"' in s
    assert s.count("<li") >= 6, s.count("<li")
    assert s.count('data-spy="') >= 6, s
    # The numbers are rendered, zero-padded, and are part of the chip's text — not a CSS
    # counter, which a screen reader would not read out.
    assert ">01<" in s and ">06<" in s, s
    # Icons would be wrong here and emoji are banned outright; the rail is text and numbers.
    assert "<img" not in s
    assert not [c for c in s if ord(c) >= 0x1F000]
    assert not re.findall(r'style="[^"]*#[0-9A-Fa-f]{3,6}', s), s


def test_section_strip_pins_under_the_header_and_pays_for_its_own_height():
    """The strip's two CSS contracts, read off the built stylesheet rather than the source.

    1. It pins to the same measured header height every jump target is offset by. A literal
       px `top` would drift the moment the header rewrapped.
    2. It adds `--strip-h` to the global `[id] { scroll-margin-top }`. Without that a jump
       target lands UNDER the strip — the top-chrome twin of the defect
       `nav-bottom-chrome-clear` catches at the bottom of the viewport."""
    # Read off the BUILT page, not a .css file: Astro inlines a component's scoped and
    # global styles into the document that mounts it, so dist/ carries no stylesheet to read.
    html = (ROOT / "dist" / "kit-preview" / "index.html").read_text(encoding="utf-8")
    assert "--strip-h" in html, "the strip never publishes its height"
    norm = re.sub(r"\s+", "", html)
    assert "top:var(--hdr-measured,var(--hdr))" in norm, "the strip is not pinned to the measured header"
    assert "scroll-margin-top:calc(var(--hdr-measured,var(--hdr))+var(--strip-h,0px)+16px)" in norm, \
        "the jump offset does not include the strip's height"


def test_the_preview_specimen_strip_is_not_the_previews_top_chrome():
    """A specimen is a picture of the component, and it must not move the page's anchors.

    The `/kit-preview/` strip sits in a short `position: relative` demo box, so it cannot
    pin and `measureTopChrome` does not count it — but it was still publishing its own
    measured height as `--strip-h`, so every id on that page declared
    `scroll-margin-top: 152px` against 75px of real chrome. `nav-jump-target-lands` reported
    10 of 11 targets outside the band at 375 and 768: two blocking rows on a page whose only
    strip is a photograph of one.

    `data-strip` is now the one selector that says "this strip IS this document's top
    chrome", and both halves of the offset key off it — the script that publishes
    `--strip-h`, and the no-JS floor."""
    preview = (ROOT / "dist" / "kit-preview" / "index.html").read_text(encoding="utf-8")
    strips = re.findall(r'<nav[^>]*class="kit-strip"[^>]*>', preview)
    assert len(strips) == 1, strips
    assert "data-strip" not in strips[0], strips[0]

    norm = re.sub(r"\s+", "", preview)
    assert ":root:has(.kit-strip[data-strip]){--strip-h:48px}" in norm, \
        "the no-JS floor still fires on a specimen strip"
    # Astro scopes the rule with its own `data-astro-cid-*` attribute, so match around it.
    assert re.search(r"\.kit-strip\[data-astro-cid-[a-z0-9]+\]:not\(\[data-strip\]\)\{position:static\}", norm), \
        "the specimen still claims to be sticky chrome"


def test_a_shell_mounted_strip_is_still_the_pages_top_chrome():
    """The other half of the same contract: a strip the shell mounts keeps `data-strip`, so
    it keeps the script, the floor and the offset. Read off a rebuilt page, not the preview."""
    page = (ROOT / "dist" / "privacy-policy-uk" / "index.html").read_text(encoding="utf-8")
    strips = re.findall(r'<nav[^>]*class="kit-strip"[^>]*>', page)
    assert len(strips) == 1 and "data-strip" in strips[0], strips


def test_built_data_table_is_semantic_and_labels_every_cell_for_the_stack():
    """Convention 8. Component 17 is the data table (working rule 13; spec §9 amendment 5),
    and everything asserted here is what makes it stack CLEANLY rather than merely narrowly:

    · it carries `.stack-table`, whose below-640px rules in global.css turn every cell into
      a block and move the `<thead>` off-screen;
    · every `<td>` carries a `data-label` naming its column, because with the header row
      gone that attribute is the only thing left saying what a cell is;
    · the row's first cell is a `<th scope="row">` — the row's own title, which is why it
      takes no label of its own — and each column header is a `<th scope="col">`;
    · the numbers are DATA. The demo reads `data/puppies.json` and
      `data/price-matrix.json`, so no price in this repo can be typed by hand (rule 9).

    The three board arrangements are deliberately NOT asserted here: `chrome` is a layout
    axis in src/lib/boardStyles.ts, so they exist on /board-preview/<slug>/ and are held by
    test_board_previews.py. What the preview carries is the component's own default."""
    s = _sections("data-table")
    assert _has_class(s, "kit-table") and _has_class(s, "stack-table"), s[:300]
    assert "<caption" in s
    assert s.count('scope="col"') == 4, s.count('scope="col"')
    assert s.count('scope="row"') == 4, s.count('scope="row"')
    tds = re.findall(r"<td[^>]*>", s)
    assert len(tds) == 12, len(tds)
    unlabelled = [t for t in tds if not re.search(r'data-label="[^"]+"', t)]
    assert not unlabelled, unlabelled
    # The prices come from data/, never from this file or that one.
    pups = json.loads((ROOT / "data/puppies.json").read_text())[:4]
    prices = json.loads((ROOT / "data/price-matrix.json").read_text())
    for p in pups:
        assert f">{p['name']}<" in s, p["name"]
        assert f"£{p['price_gbp']:,}" in s, p
    assert f"£{prices['deposit_gbp']:,}" in s
    # Tokens only, and no emoji: a table is text.
    assert not re.findall(r'style="[^"]*#[0-9A-Fa-f]{3,6}', s), s
    assert not [c for c in s if ord(c) >= 0x1F000]


def test_built_video_embed_reserves_its_box_and_loads_on_click():
    """Convention 8. Component 18 is the video embed (working rule 14; spec §9 amendment 7).

    What is asserted here is the half of the component that is NOT a board choice:

    · the id is the old site's own. `data/settings.json`'s `youtube_embeds` is the list of
      videos the migrated pages carry, and the demo reads its first entry — rule 9 forbids a
      specimen from inventing an eleven-character id, and an invented one is a 404;
    · the box is RESERVED. `aspect-ratio: 16 / 9` is declared on the frame, so the space is
      the same size before and after the thumbnail decodes (`layout-image-box-reserved`);
    · the default is the FACADE: the preview carries a play button and a thumbnail, and no
      `<iframe>` outside the `<noscript>` fallback, so a page mounting three videos fetches
      no player at all until someone presses one;
    · the `<noscript>` block carries both the real player and the rule that hides the button,
      which is what makes it a fallback rather than a second video;
    · the player is `youtube-nocookie.com`, and the frame is named.

    The three board arrangements are deliberately not asserted here: `frame` and `play` are
    axes in src/lib/boardStyles.ts, so they live on /board-preview/<slug>/ and are held by
    test_board_previews.py — the same split the data table's test makes."""
    s = _sections("video-embed")
    wanted = json.loads((ROOT / "data/settings.json").read_text())["youtube_embeds"][0]
    assert wanted in s, wanted
    assert f"https://i.ytimg.com/vi/{wanted}/hqdefault.jpg" in s, s[:400]
    assert "data-video-play" in s and "data-video-frame" in s, s[:400]
    # The facade is a real <button>, not a div with a click handler.
    assert re.search(r'<button[^>]+type="button"[^>]*data-video-play', s), s[:600]
    assert re.search(r'aria-label="Play the video: [^"]+"', s), s[:600]
    # No eager player: every iframe on this section is inside the no-JS fallback.
    outside = re.sub(r"<noscript>.*?</noscript>", "", s, flags=re.S)
    assert "<iframe" not in outside, outside[:600]
    noscript = re.search(r"<noscript>(.*?)</noscript>", s, re.S)
    assert noscript, s[:600]
    assert "<iframe" in noscript.group(1) and "data-video-play" in noscript.group(1), noscript.group(1)[:400]
    # The player is the no-cookie host, in both places it is spelled.
    assert "youtube.com/embed" not in s, s[:600]
    assert f"youtube-nocookie.com/embed/{wanted}" in s
    # Tokens only, and no emoji: the play mark is a path.
    assert not re.findall(r'style="[^"]*#[0-9A-Fa-f]{3,6}', s), s
    assert not [c for c in s if ord(c) >= 0x1F000]


def test_the_video_box_is_reserved_in_the_components_own_stylesheet():
    """The 16:9 is declared in the component, not left to the page: a caller who forgot it
    would ship the largest layout shift a page can have, and the check that measures it is
    an advisory one, so nothing would refuse the build."""
    css = (KIT / "VideoEmbed.astro").read_text()
    assert re.search(r"aspect-ratio:\s*16\s*/\s*9", css), css[:200]
    # Convention 2, read off the RULE rather than off the file: the comment above it names
    # --color-focus in order to say what the ring is not.
    ring = re.search(r"focus-visible \{[^}]*\}", css)
    assert ring and "--kit-ring" in ring.group(0) and "--color-focus" not in ring.group(0), ring
    # Rule 1: no hex anywhere in src/. The thumbnail url is not a colour.
    assert not re.findall(r"#[0-9A-Fa-f]{3,6}\b", css), css


#: The three pages project 4 has rebuilt onto `PageShell`. They are the only pages that pass
#: a section list, so they are the only ones that mount the in-page nav set.
REBUILT_PAGES = ["privacy-policy-uk", "thank-you-blue-staffy-puppies-journey",
                 "uk-blue-staffy-breeders-contact"]


@pytest.mark.parametrize("slug", REBUILT_PAGES)
def test_every_rebuilt_page_mounts_the_toc_below_its_hero(slug):
    """Component 11 is the fourth member of the in-page nav set, and `PageShell` mounts it.

    Before this, the dial, the strip and the sheet were all mounted by the shell and the TOC
    was mounted by nobody — it existed in the kit and on `/kit-preview/`, and every rebuilt
    page shipped without it. The shell now renders it between the `hero` slot and the body,
    which is what makes the board's "Navigation on this page" block a true statement.

    Two things are asserted beyond its presence:

    · it comes AFTER the page's opening section. A list of where to go that a reader meets
      before the page has said what it is is a table of contents for an unknown document;
    · there is exactly ONE breadcrumb landmark. BaseLayout already renders the trail above
      `<main>`, so the shell passes `crumbs={false}` — two `nav[aria-label="Breadcrumb"]`
      with the same links is a duplicate landmark and a duplicated trail for a crawler."""
    page = ROOT / "dist" / slug / "index.html"
    if not page.exists():
        pytest.skip("run npm run build first")
    html = page.read_text(encoding="utf-8")
    assert html.count('aria-label="Breadcrumb"') == 1, html.count('aria-label="Breadcrumb"')
    toc = html.find('aria-label="On this page"')
    assert toc > 0, "PageShell did not mount PageNav"
    # The hero is the first `<section id=…>` of the body; the TOC follows it.
    first_section = re.search(r'<section[^>]*\sid="([a-z][a-z0-9-]*)"', html)
    assert first_section and first_section.start() < toc, (first_section, toc)
    # Every jump link resolves to an id the page actually carries (nav-anchors-resolve).
    block = html[html.find('class="kit-nav', 0):toc + 4000]
    for href in set(re.findall(r'<a href="#([a-z][a-z0-9-]*)"', block)):
        assert f'id="{href}"' in html, href



TRUST_DEFAULT = ("KC registered", "DNA-tested parents", "Raised in the home")


def _trust_items(built):
    """(count, [titles]) for the one `kit-trust` strip on a built page."""
    html = built.read_text(encoding="utf-8")
    m = re.search(r"<section[^>]*kit-trust[^>]*>.*?</section>", html, re.S)
    assert m, f"{built} renders no trust strip"
    seg = m.group(0)
    return len(re.findall(r"<li", seg)), re.findall(r"<strong[^>]*>(.*?)</strong>", seg)


def test_trust_strip_default_is_unchanged_for_every_page_that_passes_no_items():
    """`items` was added at the 2026-09-21 review so /buy-staffy-puppies-for-sale-uk/ could
    print the FOUR documents its record's `promises` section names. The prop is optional and
    the default is the same three claims the component always carried, so the three callers
    that pass nothing must be byte-for-byte what they were — that is the whole safety argument
    for adding the prop rather than editing the list."""
    # The root slug's built file is `dist/index.html` and NOT `dist/index/index.html`, which
    # exists on no build — spec §9 amendment 9.3, the four places that spelled it wrong.
    for built in (ROOT / "dist/index.html",
                  ROOT / "dist/uk-blue-staffy-breeders-contact/index.html",
                  ROOT / "dist/kit-preview/index.html"):
        assert built.exists(), f"{built} not built — run npm run build"
        count, titles = _trust_items(built)
        assert count == 3, (built.parent.name, count)
        assert tuple(titles) == TRUST_DEFAULT, (built.parent.name, titles)


def test_the_why_us_page_passes_the_four_documents_its_record_names():
    """Rule 9 follows a page's own `items` exactly as it governs the default: each of the four
    is a document backed on disk, and the paragraph beside the strip names the same four. The
    record's `promises` intent says "the four things we can actually hand a reader", and a
    strip printing three made that section contradict itself."""
    built = ROOT / "dist/buy-staffy-puppies-for-sale-uk/index.html"
    if not built.exists():
        pytest.skip("why-us page not built")
    count, titles = _trust_items(built)
    assert count == 4, titles
    assert tuple(titles) == (
        "Kennel Club registered", "Two DNA tests", "Vet checked and chipped",
        "A written contract",
    ), titles
    # Not the kit default's wording: a shared sentence between this strip and the homepage's
    # is the rule 8 crossover the dup gate catches.
    assert "DNA-tested parents" not in titles
