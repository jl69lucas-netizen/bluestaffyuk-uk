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


def test_kit_file_exists_for_each_row():
    missing = [r["file"] for r in load() if not (KIT / r["file"]).exists()]
    assert not missing, missing


VARIANT_TS = KIT / "_variant.ts"
MARK = KIT / "Mark.astro"


def test_variant_helper_exports_the_five_letters():
    t = VARIANT_TS.read_text()
    assert "export type Variant = 'a' | 'b' | 'c' | 'd' | 'e'" in t
    assert "export const VARIANTS" in t


def test_mark_is_one_badge_on_a_100_grid_with_a_title_and_no_hex():
    """Spec §11 amendment 3a: the five stroke variants are replaced by ONE filled badge.

    Two `<circle>` and no more — the roundel and the brass ring. The eye catchlights are
    `<ellipse>` with rx == ry on purpose, so this count stays a statement about the badge
    frame rather than a tally of every round thing in the head.
    """
    t = MARK.read_text()
    assert t.count("<svg") == 1
    assert 'viewBox="0 0 100 100"' in t
    assert "<title>" in t
    assert t.count("<circle") == 2, "the badge and its ring, nothing else"
    assert 'fill="#' not in t and 'stroke="#' not in t
    # the prop is accepted and ignored: no variant branch is left in the markup
    assert "variant ===" not in t


def test_mark_inverse_swaps_the_badge_and_the_outline_for_dark_bands():
    t = MARK.read_text()
    assert "inverse = false" in t
    assert "inverse ? 'var(--color-surface)' : 'var(--color-brand)'" in t
    assert "inverse ? 'var(--color-brand)' : 'var(--color-surface)'" in t
    for token in ("--color-cta", "--color-brand-mid", "--color-brand-tint", "--color-surface-deep"):
        assert f"var({token})" in t, token


ROUTE = ROOT / "src/pages/design-canvas/index.astro"
REGISTRY_TS = KIT / "_registry.ts"
DIST_ROUTE = ROOT / "dist/design-canvas/index.html"


def test_route_is_noindex():
    t = ROUTE.read_text()
    # The prop, not the bare word: the file's header comment also says "noindex", so
    # `'noindex' in t` would keep passing with the prop deleted from the BaseLayout call.
    assert 'noindex={true}' in t


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


# The artboard's own caption — `<h3 style="…">Title — variant a</h3>`, written by the route,
# not by the component. It carries the variant letter, so leaving it in makes every pair of
# sections differ no matter what the components rendered.
CAPTION_RE = re.compile(r'^\s*<h3[^>]*>.*?</h3>', re.S)
VARIANT_ATTR_RE = re.compile(r'data-variant="[a-e]"')


#: components whose variant class stem is NOT derivable from their id. Four of the thirteen
#: name their root class after the thing rather than the row — `testimonial` paints
#: `kit-quote-a`, `site-header` paints `kit-hdr-a` — and for those the derived pattern below
#: matched nothing at all, so the variant letter survived normalisation and every pair of
#: sections differed by that letter alone. The distinctness check passed vacuously for them.
#: `buttons` has no stem on purpose: its five variants are five different utility class
#: lists, with no `kit-buttons-[a-e]` to normalise away.
CLASS_STEM = {
    "site-header": "hdr",
    "puppy-card": "pup",
    "testimonial": "quote",
    "section-divider": "divider",
}


def _variant_class_re(cid):
    r"""The one class that spells this component's variant letter.

    Built from `data-component`, not from a blanket `kit-\w+-[a-e]`: a blanket pattern also
    rewrites any other kit class that happens to end in a hyphen and a letter a-e, and a
    normalisation that reaches classes it was not aimed at can only ever erase differences
    the check exists to find. `kit-counter-a` comes from the `counter-strip` row, so the
    stem is the id with a trailing `-strip`/`-card` dropped, and the full id is allowed too —
    except for the four in CLASS_STEM, which say outright what they paint.
    """
    stems = {re.sub(r"-(strip|card)$", "", cid), cid}
    if cid in CLASS_STEM:
        stems.add(CLASS_STEM[cid])
    alts = "|".join(sorted((re.escape(s) for s in stems), key=len, reverse=True))
    return re.compile(rf"\bkit-(?:{alts})-([a-e])\b")


def _rendering(cid, inner):
    """One variant section reduced to what it actually RENDERS.

    Two variants can be byte-different and visually identical: the route stamps the letter
    into the artboard caption and the component stamps it into its own class and into
    data-variant. Those three alone were enough to make a pairwise byte comparison pass on
    five copies of one card, which is what this strips or normalises away.

    LIMITATION, stated once: what survives is markup, so this proves "differs in markup",
    which is a PROXY for "differs on screen" and not the thing itself. It is sound in one
    direction only — identical markup after normalisation means the canvas really is
    showing the same thing twice, so a failure here is always real. The converse does not
    hold: two variants that differ only in a scoped stylesheet (`.kit-x-e { box-shadow:
    none }`) now read as distinct markup once one of them also gains an element, and two
    that differ by a single aria-hidden glyph pass while looking nearly identical to the
    eye choosing between them. The canvas itself, and the human picking from it, remain the
    real judge of whether five options are five options."""
    out = CAPTION_RE.sub("", inner)
    out = _variant_class_re(cid).sub(lambda m: m.group(0)[: -1] + "V", out)
    out = VARIANT_ATTR_RE.sub('data-variant="V"', out)
    return out.strip()


#: components exempt from the five-way distinctness check, each with the reason in full.
#: A named list, never a silent skip: an exemption nobody can read is an exemption nobody
#: can revoke, and `test_distinctness_exemptions_are_still_warranted` below fails the day
#: an exempt component starts passing again.
DISTINCTNESS_EXEMPT = {
    "testimonial": "amendment 3e: modes replace variants; a≡c (single), d≡e (single/stacked) "
                   "collapse at Task 19",
}


def test_built_sections_render_five_distinct_variants():
    """Whatever is on the canvas today must show five genuinely different THINGS per
    component, with no hex reached for in an inline style. Compared on _rendering(), not on
    the raw section: the raw bytes always differ, because the route writes the variant
    letter into the artboard caption and the component writes it into its own class, so a
    byte comparison would have passed on five copies of one card. Passes for the components
    that exist; every later task widens it for free."""
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    by_component = {}
    for cid, variant, inner in SECTION_RE.findall(DIST_ROUTE.read_text()):
        by_component.setdefault(cid, {})[variant] = inner
    assert by_component, "the canvas built no variant sections at all"
    for cid, variants in sorted(by_component.items()):
        assert sorted(variants) == list("abcde"), (cid, sorted(variants))
        painted = {v: _rendering(cid, inner) for v, inner in variants.items()}
        same = [(x, y) for i, x in enumerate("abcde") for y in "abcde"[i + 1:]
                if painted[x] == painted[y]]
        if cid in DISTINCTNESS_EXEMPT:
            continue
        assert not same, (
            f"{cid}: {same} render the same markup once the variant letter is normalised "
            f"away — they are one option on the canvas, not two")
        hexes = [m for inner in variants.values()
                 for m in re.findall(r'style="[^"]*#[0-9A-Fa-f]{3}', inner)]
        assert not hexes, (cid, hexes)


def _sections(cid):
    """The built artboard sections for one component, keyed by variant letter.

    A registered component with zero sections is a failure, not a skip: that is exactly
    what a route regression looks like, and skipping it would hide one."""
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    out = {v: inner for c, v, inner in SECTION_RE.findall(DIST_ROUTE.read_text()) if c == cid}
    assert sorted(out) == list("abcde"), (cid, sorted(out))
    return out


def test_built_site_header_variants_carry_their_distinguishing_marks():
    """Convention 8. Five headers that differ only in CSS would pass the distinctness check
    above while the drawer, the dark bands and the strapline had all silently vanished."""
    s = _sections("site-header")
    # The drawer is every variant's MOBILE nav, so it is in all five; what makes d the
    # drawer variant is that it ships no inline nav to hide.
    for v, inner in sorted(s.items()):
        assert "<details" in inner, v
    assert 'class="nav' not in s["d"] and "Open menu" in s["d"]
    for v in ("a", "b", "c", "e"):
        assert 'class="nav' in s[v], v
    for v in ("b", "d"):
        assert 'data-surface="inverse"' in s[v], v
    for v in ("a", "c", "e"):
        assert 'data-surface="inverse"' not in s[v], v
    assert "Carlisle" in s["e"], "variant e shows the location strapline"


def test_built_site_header_variants_are_logo_only_and_all_carry_the_search_pill():
    """Spec §11 amendment 3b. The pick is variant a, but the wordmark came off and the
    search pill went on in ALL FIVE, so the canvas keeps comparing like with like.

    Two forms per header — the bar's pill and the same form full-width in the drawer — and
    both are a real GET to /search/, so Enter works with the script removed."""
    s = _sections("site-header")
    for v, inner in sorted(s.items()):
        assert inner.count('role="search"') == 2, (v, "bar pill + drawer form")
        assert inner.count('action="/search/"') == 2, v
        assert 'name="q"' in inner and 'type="search"' in inner, v
        assert 'id="site-search-results"' in inner and 'aria-live="polite"' in inner, v
        assert 'class="word"' not in inner, (v, "the wordmark text is gone")
        # the brand link keeps its accessible name without the wordmark
        assert 'class="brand" aria-label=' in inner, v
    # e is the only variant that still prints the strapline, now as a caption under the logo
    for v in ("a", "b", "c", "d"):
        assert "Carlisle" not in s[v], v


def test_built_puppy_card_variants_carry_price_status_and_their_ornament():
    """Convention 8. The card's whole job is photo + name + price + status; a variant that
    renders the shell without the data is a pass on distinctness and a failure in fact.
    The prices are read from the data, so a price change is a data edit, not a test edit."""
    pups = {p["slug"]: p for p in json.loads((ROOT / "data/puppies.json").read_text())}
    demo = ("roman", "christa")
    s = _sections("puppy-card")
    for v, inner in sorted(s.items()):
        for slug in demo:
            p = pups[slug]
            assert f"£{p['price_gbp']:,}" in inner, (v, slug)
            assert p["status"] in inner, (v, slug)
            assert p["name"] in inner, (v, slug)
        assert "srcset=" in inner, v      # astro:assets, not a single fixed width
    assert "badge" in s["a"], "variant a carries the price badge"
    assert "ribbon" in s["b"], "variant b carries the status ribbon"
    assert "ribbon" not in s["a"] and "badge" not in s["b"]


def test_built_hero_variants_carry_their_photo_copy_and_band():
    """Convention 8. The hero's job is one heading, one lede and — where it shows a photo —
    a responsive one. Five heroes that differ only in a class name would pass the
    distinctness check above with the image or the CTAs silently gone."""
    s = _sections("hero")
    for v, inner in sorted(s.items()):
        # The canvas fixture passes as="h2" so the page keeps one h1; the component's
        # default is h1 and that is what project 4 will render.
        assert 'class="title' in inner and "<h2" in inner, v
        assert "KC registered" in inner, v
        assert "Carlisle" in inner, v
    # a and c show the .pic photo; b paints the full-bleed band photo; d and e are text-only.
    for v in ("a", "b", "c"):
        assert "srcset=" in s[v], v
    for v in ("d", "e"):
        assert "srcset=" not in s[v], v
    assert 'class="bg' in s["b"] and 'class="pic' not in s["b"]
    for v in ("a", "c"):
        assert 'class="pic' in s[v], v
    for v in ("b", "d"):
        assert 'data-surface="inverse"' in s[v], v
    for v in ("a", "c", "e"):
        assert 'data-surface="inverse"' not in s[v], v
    assert "chips" in s["c"] and "chips" not in s["a"]
    # e is the short location hero: eyebrow, heading, one line, no CTA row.
    assert "ctas" not in s["e"]
    for v in ("a", "b", "c", "d"):
        assert "ctas" in s[v], v


def test_built_hero_puts_the_image_before_the_heading():
    """rules/design.md rule 10, first half (spec §11 amendment 3c). SOURCE ORDER, not the
    painted layout: `order` moves the photo back to the right of the copy on screen, so the
    only way to see this is where the <img> sits in the markup."""
    s = _sections("hero")
    for v in ("a", "b", "c"):
        inner = s[v]
        img = inner.find("<img")
        head = inner.find("<h2")
        assert img != -1 and head != -1, v
        assert img < head, (v, "the hero image must precede the heading in the DOM")
    # d and e have no hero image at all, which rule 10 does not make a violation
    for v in ("d", "e"):
        assert "<img" not in s[v], v


HEIGHTS = ROOT / "data/design/canvas-heights.json"


def test_measured_hero_fits_its_clamp_without_clipping_anything():
    """rules/design.md rule 10, second half — and the half a board height cannot prove.

    The old version of this test read the rounded artboard height and called <= 472 a pass.
    That number is produced by `max-height` whether the copy FITS in the clamp or is being
    CUT OFF by it, so a hero with its CTA row sliced in half measured exactly as well as one
    that fitted. scripts/measure_canvas_heights.mjs therefore records, per hero and at each
    of the three desktop widths where the clamp is live, the scroll overflow of `.inner` and
    of the section, and where the CTA row's bottom edge sits relative to the section's own.
    Overflow of zero and a CTA row at or above the section's bottom is the real assertion;
    the 390-450 band is checked on the unrounded section height beside it."""
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
            if m["ctas_below"] is not None:
                assert m["ctas_below"] <= 0, (key, w, m, "the CTA row hangs below the hero")
            assert 390 <= m["height"] <= 450, (key, w, m["height"])


def test_built_trust_strip_variants_carry_three_backed_claims_and_line_icons():
    """Convention 8. Rule 7: the icons are inline stroke SVG, never an emoji. Rule 9: each
    claim is one the live homepage already makes (KC registration, L-2-HGA / HC-HSF4 clear
    parents, home rearing) — a strip that invented a fourth would be a statutory statement
    with nothing behind it."""
    s = _sections("trust-strip")
    for v, inner in sorted(s.items()):
        for claim in ("KC registered", "DNA-tested parents", "Raised in the home"):
            assert claim in inner, (v, claim)
        assert inner.count("<svg") == 3, v
        assert 'stroke="currentColor"' in inner, v
        # Rule 7, measured rather than asserted by keyword: an icon is an inline stroke SVG,
        # so there is no <img> in the strip and no character in the emoji planes.
        assert "<img" not in inner, v
        emoji = [c for c in inner if ord(c) >= 0x1F000]
        assert not emoji, (v, emoji)
    # c is the single line: the headline claims only, no description sentences.
    assert "L-2-HGA" not in s["c"]
    for v in ("a", "b", "d", "e"):
        assert "L-2-HGA" in s[v], v
    assert 'data-surface="inverse"' in s["d"]
    for v in ("a", "b", "c", "e"):
        assert 'data-surface="inverse"' not in s[v], v


def test_built_counter_strip_variants_keep_the_harness_hooks_and_the_data_figures():
    """Convention 8. `.counter-wrap` and `[data-counters]` are what
    tests/render/checks/layout.ts selects on: rename either and the
    layout-hero-counter-separation check examines zero elements and passes vacuously.
    The figures are read from the data here too, so a sold puppy is a data edit."""
    settings = json.loads((ROOT / "data/settings.json").read_text())
    pups = json.loads((ROOT / "data/puppies.json").read_text())
    available = sum(1 for p in pups if p["status"] == "Available")
    s = _sections("counter-strip")
    for v, inner in sorted(s.items()):
        assert "counter-wrap" in inner and "data-counters" in inner, v
        assert f">{available}<" in inner, (v, available)
        assert f"£{settings['deposit_gbp']}" in inner, v
        assert f"£{settings['delivery_min_gbp']}" in inner, v
        assert f"£{settings['delivery_max_gbp']}" in inner, v


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


def test_built_info_card_variants_carry_a_kinded_statement_label_and_d_owns_its_image():
    """Convention 8, and the two deferred checks' half of it.

    `sem-statement-label-visible` requires every `.stmt-label` to be painted AND to carry a
    data-kind of fact/observed/recommendation; a label that lost its kind, or a variant
    that quietly stopped rendering one, would still pass the distinctness check above.
    `layout-h3-image-first` reads the SIBLINGS of an h3, so variant d's image and prose
    have to be direct children of the article in that order — wrapping them back into a
    <div> makes the check examine zero and pass vacuously, which is the regression this
    pins. The kinds come from the registry's two demo fixtures."""
    s = _sections("info-card")
    for v, inner in sorted(s.items()):
        # Counted on the class token, not on a whole attribute: Astro appends its scoped
        # `astro-*` class to every element its <style> matches.
        assert len(re.findall(r'\bstmt-label\b', inner)) == 2, (v, "one label per demo fixture")
        assert 'data-kind="fact"' in inner, v
        assert 'data-kind="recommendation"' in inner, v
        assert re.search(r'data-kind="(?!fact|observed|recommendation)', inner) is None, v
    # d is the only variant that owns a sectional image, and the H3 comes first.
    d = s["d"]
    assert "sec-img" in d
    order = [m.group(1) for m in re.finditer(r'<(h3|img|p)\b[^>]*\b(?:sec-h3|sec-img|prose)\b', d)]
    assert order[:3] == ["h3", "img", "p"], order[:6]
    # The srcset is the card's painted width, not a hero's: 420 and 840, nothing wider.
    assert 'sizes="(max-width: 640px) 100vw, 420px"' in d
    assert "1200w" not in d and "1600w" not in d, "the 420px card must not decode a hero width"
    for v in ("a", "b", "c", "e"):
        assert "sec-img" not in s[v], v


QUOTE_BLOCK_RE = re.compile(
    r'<section class="kit-quote[^"]*kit-quote-([a-e])"([^>]*)>(.*?)</section>', re.S)


def _quote_blocks():
    """Every Testimonial the canvas built, keyed by (variant, mode).

    Read off the component's OWN sections rather than through `_sections`: the artboard
    wrapper is a <section> too, and the outer match stops at the first nested `</section>`,
    so the second block on each artboard is invisible from there."""
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    out = {}
    for variant, attrs, inner in QUOTE_BLOCK_RE.findall(DIST_ROUTE.read_text()):
        m = re.search(r'data-mode="(\w+)"', attrs)
        out[(variant, m.group(1) if m else "?")] = attrs + inner
    return out


def test_built_testimonial_blocks_quote_the_reviews_file_verbatim_in_both_modes():
    """Convention 8, and rule 9's half of it. A testimonial component is the easiest place
    in the kit to invent a claim, so the built artboards are compared against
    data/reviews.json rather than against a shape: every block must print the reviews it
    shows word for word. If a review is a REVIEW_PLACEHOLDER row it still has to appear,
    because a slot silently dropped is the same defect as a slot silently invented.

    Spec §11 amendment 3e: how many it shows is `mode`, not the variant letter — `single` is
    one review given room, `grid` is the strip — so both modes are built on every artboard
    and both are asserted here."""
    reviews = json.loads((ROOT / "data/reviews.json").read_text())
    assert len(reviews) == 3, len(reviews)
    blocks = _quote_blocks()
    assert sorted(blocks) == [(v, m) for v in "abcde" for m in ("grid", "single")], sorted(blocks)

    def printed(text, inner):
        # The built HTML escapes & < >; nothing else in these quotes needs escaping.
        return text.replace("&", "&#38;").replace("<", "&#60;").replace(">", "&#62;") in inner

    for (v, mode), inner in sorted(blocks.items()):
        shown = reviews if mode == "grid" else reviews[:1]
        for r in shown:
            assert printed(r["quote"], inner), (v, mode, r["name"], "quote not printed verbatim")
            assert printed(r["name"], inner), (v, mode, r["name"])
        if mode == "single":
            assert not printed(reviews[2]["quote"], inner), (v, "single mode shows one review")
        # the container follows the mode, never the variant
        assert f'class="container {"grid" if mode == "grid" else "stack"}' in inner, (v, mode)
    # b is still the only variant that paints its own dark band — mode does not change that.
    for mode in ("single", "grid"):
        assert 'data-surface="inverse"' in blocks[("b", mode)], mode
        for v in ("a", "c", "d", "e"):
            assert 'data-surface="inverse"' not in blocks[(v, mode)], (v, mode)


def test_reviews_json_quotes_exist_verbatim_on_the_page_each_one_names():
    """Rule 9, enforced at the source. Each row carries the path it was copied from; this
    reads that file and fails if the quote or the attribution is not in it character for
    character. A REVIEW_PLACEHOLDER row has no source and is exempt — that is the whole
    point of the placeholder."""
    reviews = json.loads((ROOT / "data/reviews.json").read_text())
    for r in reviews:
        if r["quote"] == "REVIEW_PLACEHOLDER":
            assert r["source"] == "", r
            continue
        page = (ROOT / r["source"]).read_text()
        m = re.search(r'const body = "(.*?)";\n', page, re.S)
        assert m, r["source"]
        body = m.group(1).encode().decode("unicode_escape").encode("latin-1").decode("utf-8")
        assert r["quote"] in body, (r["source"], r["quote"][:60])
        assert r["name"] in body, (r["source"], r["name"])
        assert r["place"] in body, (r["source"], r["place"])


def test_built_faq_variants_are_native_details_with_backed_answers():
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
    }
    resolved = [
        {"q": r["q"], "a": re.sub(r"\{([a-z_]+)\}", lambda m: tokens[m.group(1)], r["a"])}
        for r in rows
    ]
    s = _sections("faq")
    for v, inner in sorted(s.items()):
        assert inner.count("<details") == len(rows), v
        assert inner.count("<summary") == len(rows), v
        # The question is a heading inside the summary, so the answers are a navigable list.
        assert len(re.findall(r'<h3[^>]*\bq\b[^>]*>', inner)) == len(rows), v
        for r in resolved:
            assert r["q"] in inner, (v, r["q"])
            assert r["a"] in inner, (v, r["a"])
    # a and b are the only variants with a marker glyph, and they are different glyphs.
    for v in ("a", "b"):
        assert 'stroke="currentColor"' in s[v], v
        assert s[v].count("<svg") == len(rows), v
    for v in ("c", "d", "e"):
        assert "<svg" not in s[v], v
    # c is the numbered treatment.
    assert ">01<" in s["c"] and f">{len(rows):02d}<" in s["c"]


def _has_class(html, token):
    """True when `token` appears as a class TOKEN in a class attribute.

    Astro appends its own `astro-cid-*` class to every styled element, and the scoped
    stylesheet inside the same section spells every class name this file looks for, so a
    bare `"cols" in inner` passes on a component that renders no such element at all."""
    return any(token in value.split()
               for value in re.findall(r'class="([^"]*)"', html))


def test_the_contact_page_itself_still_posts_to_the_live_endpoint():
    """The canvas specimens post nowhere on purpose (below), which is only safe while the
    REAL contact page still posts to the one Formspree endpoint. Skipped, not silently
    passed, when the id is unset: the built page then legitimately carries the stub."""
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


def test_built_contact_form_variants_all_keep_the_whole_form_contract():
    """Convention 8, and spec §11 amendment 2's half of it.

    The canvas route is excluded from form_contract_audit.py's per-page FIELD contract
    (NON_CONTENT_ROUTES) because five specimens of one form are not five enquiry forms.
    That exclusion is only safe while something else proves the specimens still carry the
    contract — this is that something. Every variant must show the six named controls with
    the built page's required set, the honeypot, both hidden fields, POST, and the endpoint
    built from the environment rather than spelled in the component. The puppy options are
    read from data/puppies.json, so a reserved pup is a data edit and not a test edit."""
    pups = json.loads((ROOT / "data/puppies.json").read_text())
    available = [p for p in pups if p["status"] == "Available"]
    assert available, "the fixture needs at least one available puppy"
    s = _sections("contact-form")
    for v, inner in sorted(s.items()):
        assert 'method="POST"' in inner, v
        assert 'name="_gotcha"' in inner, v
        for hidden in ('name="_next"', 'name="_subject"'):
            assert hidden in inner, (v, hidden)
        for key in ("name", "email", "phone", "location", "puppy", "message"):
            assert f'name="{key}"' in inner, (v, key)
        # The four the built contact page marks required; phone and location are optional
        # there, and a kit form that demanded them would not be the same form.
        for key in ("name", "email", "puppy", "message"):
            assert re.search(rf'name="{key}"[^>]*\brequired\b|\brequired\b[^>]*name="{key}"',
                             inner), (v, key)
        assert '<select' in inner and 'name="puppy"' in inner, v
        for p in available:
            assert f'value="{p["slug"]}"' in inner, (v, p["slug"])
        assert 'value="waiting-list"' in inner, v
        assert "<textarea" in inner, v
        # The canvas specimens post NOWHERE: the registry passes the component's
        # documented `action` override so five copies of one form on one page cannot send
        # five real enquiries. form_contract_audit.py allows that one stub here only.
        assert re.findall(r'<form[^>]*\saction="([^"]*)"', inner) == ["#contact"], v
    # d is the only variant that paints its own dark card, and the only one with the eyebrow.
    assert 'data-surface="inverse"' in s["d"] and _has_class(s["d"], "eyebrow")
    for v in ("a", "b", "c", "e"):
        assert 'data-surface="inverse"' not in s[v], v
    # c is the stepped one: three fieldsets with legends, and the only variant with any.
    assert s["c"].count("<fieldset") == 3 and s["c"].count("<legend") == 3
    for v in ("a", "b", "d", "e"):
        assert "<fieldset" not in s[v], v
    # b is the two-column one: the short fields sit in their own row wrapper. Anchored on
    # the class token in a class attribute, not on the bare word, which also appears in
    # any stylesheet or comment that mentions it.
    assert _has_class(s["b"], "cols"), "b wraps its short fields in a row"
    for v in ("a", "d", "e"):
        assert not _has_class(s[v], "cols"), v
    # e is the compact panel, and the only one offering the address as a direct line.
    assert _has_class(s["e"], "direct") and "mailto:" in s["e"]
    for v in ("a", "b", "c", "d"):
        assert "mailto:" not in s[v], v


def test_built_page_nav_variants_carry_the_real_trail_and_their_own_toc_shape():
    """Convention 8. Two things are pinned. First the trail: it is produced by crumbs()
    in src/lib/site.ts, so the intermediate label has to be NAV's label for that href and
    the last crumb has to be the page itself, marked aria-current — a breadcrumb whose
    last item is a link is the defect this catches. Second the shape: five treatments that
    differed only in CSS would pass the distinctness check above with the list gone."""
    s = _sections("page-nav")
    labels = ["Temperament", "Health", "Exercise", "Cost"]
    for v, inner in sorted(s.items()):
        assert 'aria-label="Breadcrumb"' in inner, v
        assert 'href="/"' in inner and ">Home<" in inner, v
        # The leaf is the page, not a link: crumbs() puts the title last.
        assert 'aria-current="page"' in inner, v
        assert "Staffordshire Bull Terrier guide" in inner, v
    # a is the breadcrumb alone; the other four carry the jump list from the demo fixture.
    assert 'aria-label="On this page"' not in s["a"]
    for label in labels:
        assert label not in s["a"], label
    for v in ("b", "c", "d", "e"):
        assert 'aria-label="On this page"' in s[v], v
        for label in labels:
            assert f'#{label.lower()}"' in s[v], (v, label)
            assert label in s[v], (v, label)
    # b and d announce the list with a VISIBLE heading; the aria-label is on all four, so
    # the heading is matched as element text and not as the bare phrase.
    for v in ("b", "d"):
        assert ">On this page</h2>" in s[v], v
    for v in ("c", "e"):
        assert "</h2>" not in s[v], v
    assert s["d"].count("<ol") == 2, "the trail's <ol> plus the numbered rail"
    for v in ("a", "b", "c", "e"):
        assert s[v].count("<ol") == 1, v
    # e is the only one with a jump glyph, and it is an inline stroke SVG (rule 7).
    assert s["e"].count("<svg") == len(labels)
    assert 'stroke="currentColor"' in s["e"]
    for v in ("a", "b", "c", "d"):
        assert "<svg" not in s[v], v


def test_built_footer_variants_carry_the_nav_the_socials_and_their_own_arrangement():
    """Convention 8, and rule 9's half of it. The footer is where invented copy and dead
    links collect, so the built artboards are compared against src/lib/site.ts's NAV and
    data/settings.json rather than against a shape: every variant must link every NAV item
    it claims to list and every social profile in the settings file, and the contact rows
    must be the settings email and hours rather than a second copy of them."""
    settings = json.loads((ROOT / "data/settings.json").read_text())
    # Parsed from the NAV block alone: a bare href/label pattern over the whole file would
    # also swallow any other array of links src/lib/site.ts grows later.
    site = (ROOT / "src/lib/site.ts").read_text()
    block = re.search(r"export const NAV = \[(.*?)\n\];", site, re.S)
    assert block, "src/lib/site.ts no longer declares NAV as a literal array"
    nav = re.findall(r"\{ href: '([^']+)', label: '([^']+)' \}", block.group(1))
    assert len(nav) == 7, nav
    s = _sections("footer")
    for v, inner in sorted(s.items()):
        # c is the slim row and carries the primary four; the rest carry the whole list.
        expected = nav[:4] if v == "c" else nav
        for href, label in expected:
            assert f'href="{href}"' in inner, (v, href)
            assert label in inner, (v, label)
        assert settings["location_label"] in inner, v
        assert settings["site_name"] in inner, v
        assert 'href="/privacy-policy-uk/"' in inner, v
        assert 'data-surface="inverse"' in inner, v
        # No colour is spelled in the footer's own markup.
        assert not re.findall(r'style="[^"]*#[0-9A-Fa-f]{3}', inner), v
    # c is one line and carries no follow column; the other four link every profile in
    # the settings file, so a new social account is a data edit.
    for v in ("a", "b", "d", "e"):
        for url in settings["socials"].values():
            assert f'href="{url}"' in s[v], (v, url)
    for url in settings["socials"].values():
        assert url not in s["c"], url
    # a and e are the ones with a contact column; both print the settings email and hours.
    for v in ("a", "e"):
        assert f'mailto:{settings["email"]}' in s[v], v
        assert settings["hours"] in s[v], v
    for v in ("b", "c", "d"):
        assert "mailto:" not in s[v], v
    # d is the only variant with the call-to-action band above the columns.
    assert _has_class(s["d"], "cta-band") and "Ready to meet the litter?" in s["d"]
    for v in ("a", "b", "c", "e"):
        assert not _has_class(s[v], "cta-band"), v
    # c is the slim row: no column headings and no tagline.
    assert "<h2" not in s["c"] and settings["tagline"] not in s["c"]
    for v in ("a", "b", "d", "e"):
        assert "<h2" in s[v] and settings["tagline"] in s[v], v
    # b is the centred lockup and the only one with the larger mark.
    assert 'width="56"' in s["b"]
    for v in ("a", "c", "d", "e"):
        assert 'width="40"' in s[v], v
    # e is the sitemap arrangement: four columns, so it alone carries the small-print one.
    assert "Small print" in s["e"]
    for v in ("a", "b", "c", "d"):
        assert "Small print" not in s[v], v


def test_distinctness_exemptions_are_still_warranted():
    """An exemption that has stopped being needed is a hole left open.

    Every id in DISTINCTNESS_EXEMPT must still collapse — and must still be a real
    component — so the list shrinks itself rather than outliving its reason."""
    if not DIST_ROUTE.exists():
        pytest.skip("run npm run build first")
    by_component = {}
    for cid, variant, inner in SECTION_RE.findall(DIST_ROUTE.read_text()):
        by_component.setdefault(cid, {})[variant] = inner
    for cid, reason in sorted(DISTINCTNESS_EXEMPT.items()):
        assert cid in IDS, cid
        assert reason.strip(), cid
        painted = {v: _rendering(cid, inner) for v, inner in by_component[cid].items()}
        same = [(x, y) for i, x in enumerate("abcde") for y in "abcde"[i + 1:]
                if painted[x] == painted[y]]
        assert same, f"{cid} no longer collapses — drop it from DISTINCTNESS_EXEMPT"
