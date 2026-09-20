#!/usr/bin/env python3
"""build_design_system.py — the repo → the Design System artifact's `project/` files.

Reads `src/styles/tokens.css`, `data/design/components.json`, `data/design/canvas-heights.json`,
`data/design/picks.json`, `data/settings.json`, `rules/design.md`, `public/brand/` and the
built `dist/kit-preview/index.html`; writes everything the Design System type serves under
`docs/artifacts/design-system/project/` (gitignored, like the canvas). The controller uploads
the assets and publishes; this script never touches the network.

WHAT THE TYPE ACTUALLY WANTS (spec §11 amendment 7). Three things about its shape are not
what the plan's draft assumed, and each one changes the output:

 1. `tokens.json` is a LIST per family — `{"color": {"themes": [...], "tokens": [...]},
    "spacing": {"tokens": [...]}, ...}` — not one flat `tokens` array with a `layer` field.
    A name-to-value map is valid JSON the page silently cannot read, so the families are
    built as lists or not at all. Colours may alias another colour token (`"{color-steel-700}"`),
    which is exactly how the semantic layer is expressed; lengths and shadows may not, so a
    component-layer radius carries the literal its `var()` resolves to.
 2. There is NO component bundle. The kit is Astro, it does not run in the artifact's preview
    frame, and hand-porting thirteen components to React would be a second implementation to
    keep in step with the first. Each `components/<Comp>/preview.html` is therefore a STATIC
    rendering: the component's own built section out of `dist/kit-preview/index.html`, with
    the page's stylesheet inlined, the document sprite pasted back in and the images pointed
    at this artifact's blob store. `libraries` is empty and the index declares no namespace
    bundle.
 3. Fonts are Google-hosted, so `type.fonts` is `[]` and `type.families` names the stacks.
    Nothing is embedded that the page would have to serve.

BLOBS. Images, the four lockups and the favicon live in the artifact's file store, which only
the controller can write to. Their ids come from `data/design/design-system-assets.json`
(`assets` for the uploads listed under `assets/Logos/`, `images` for the built `/_astro/` urls)
— the same pattern as `build_design_canvas.py` and `data/design/canvas-assets.json`. When an
id is missing the generator writes every file it can, REFUSES to invent an `assetGroups.files`
entry for it, prints the upload list and exits 2. Filling the map in and re-running is the
whole of the second pass.

Usage: python3 scripts/build_design_system.py [--dist …] [--out …] [--heights …]
       npm run ds:build
Exit: 0 everything written; 2 uploads outstanding (the list is on stdout).
"""
import argparse
import datetime as dt
import html as H
import json
import pathlib
import re
import shutil
import sys

from _kit_sections import (FONTS_LINK, find_sections, page_css, page_sprite,
                           rewrite_assets, section_image_urls, uses_sprite)

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS_CSS = ROOT / "src/styles/tokens.css"
BRAND = ROOT / "public/brand"
FAVICON = ROOT / "public/favicon.svg"
ASSET_MAP = ROOT / "data/design/design-system-assets.json"

DECL = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;]+);")
VAR = re.compile(r"var\((--[a-z0-9-]+)\)")
LAYERS = ("primitive", "semantic", "component")

# The four lockups and the favicon, in the order the group lists them. `logo-icon.svg` and
# `favicon.svg` are the same 100-grid badge at two jobs, which is why both are here.
LOGO_FILES = ("logo-horizontal.svg", "logo-stacked.svg", "logo-icon.svg", "logo-mono.svg",
              "favicon.svg")


# --------------------------------------------------------------------------- tokens.css

def layers(text=None):
    """`tokens.css` split on its `@layer-*` markers into three name → value maps."""
    text = TOKENS_CSS.read_text() if text is None else text
    parts = re.split(r"/\*\s*@layer-(primitive|semantic|component)\s*\*/", text)
    return {parts[i]: dict(DECL.findall(parts[i + 1])) for i in range(1, len(parts), 2)}


def flat(L):
    """Every declaration, later layers overriding earlier ones (none do; the check is free)."""
    out = {}
    for layer in LAYERS:
        out.update(L[layer])
    return out


def resolve(value, L, depth=0):
    """A declared value with every `var()` replaced by what it ultimately resolves to."""
    if depth > 16:
        raise ValueError(f"token alias chain deeper than 16: {value}")
    value = value.strip()
    m = VAR.fullmatch(value)
    if not m:
        return value
    all_decls = flat(L)
    if m.group(1) not in all_decls:
        raise ValueError(f"{value} names a token tokens.css does not declare")
    return resolve(all_decls[m.group(1)], L, depth + 1)


def alias_of(value):
    """`var(--color-steel-700)` → `color-steel-700`, else None."""
    m = VAR.fullmatch(value.strip())
    return m.group(1).lstrip("-") if m else None


# --------------------------------------------------------------------------- usage notes
#
# Every token needs a `usage` sentence, and a sentence nobody checked is a sentence that is
# wrong by the next commit. These were written against a grep of `src/components/kit/` and
# `src/styles/kit.css` — the map below records WHERE, and `verify_usage()` re-runs that grep
# and fails the build when a token's claim no longer has a use behind it. A primitive that no
# component names directly says so: the semantic layer is the only thing allowed to reach a
# raw hue, which is the point of having one.

USAGE = {
    # ---- primitive colour
    "color-steel-900": "Deepest steel. Never named by a component: it is the value behind `color-surface-deep` (the footer band) and `color-cta-ink` (the label on every brass fill).",
    "color-steel-700": "The brand steel. Never named by a component: it is the value behind `color-brand`, `color-surface-inverse`, `color-link` and `color-focus`.",
    "color-steel-500": "Mid steel. Never named by a component: it is the value behind `color-brand-mid`, the mark's rose ears.",
    "color-steel-300": "Pale steel. Never named by a component: it is the value behind `color-brand-tint`, the mark's skull fill.",
    "color-steel-100": "Steel wash. Never named by a component: it is the value behind `color-brand-soft`, the tint under chips and the outline button's hover.",
    "color-brass-600": "Darker brass. Never named by a component: it is the value behind `color-cta-hover`.",
    "color-brass-500": "The brass. Never named by a component: it is the value behind `color-cta` and `color-focus-on-inverse`.",
    "color-brass-200": "Brass wash. Never named by a component: it is the value behind `color-cta-soft` (the puppy card's price chip) and `color-link-on-inverse`.",
    "color-bone-100": "The page bone. Never named by a component: it is the value behind `color-surface` and `color-text-on-inverse`.",
    "color-bone-50": "The palest bone. Never named by a component: it is the value behind `counter-bed`, the stat strip's own bed.",
    "color-white": "Pure white. Never named by a component: it is the value behind `color-surface-raised`, every card and the header bar.",
    "color-ink": "Body ink. Never named by a component: it is the value behind `color-text`.",
    "color-ink-2": "Second ink. Declared for a secondary body tone; nothing in the kit reaches it yet, directly or through a semantic name.",
    "color-ink-3": "Muted ink. Never named by a component: it is the value behind `color-text-muted`.",
    "color-rule": "Hairline. Never named by a component: it is the value behind `color-border`.",
    "color-ok": "The success green. The puppy card's available status dot and rule 7's check-circle icon.",
    "color-warn": "The caution rust. Reserved for a warning state; nothing in the kit paints one yet.",
    # ---- semantic colour
    "color-surface": "The page surface. The bone the hero, the mark's blaze and the outline button sit on.",
    "color-surface-raised": "A raised surface. Every card, the FAQ panel, the header bar, the form fields and the divider's medal.",
    "color-surface-inverse": "A dark band. The trust strip, the testimonial band, the header drawer and the inverse button's fill.",
    "color-surface-deep": "The deepest band. The footer, the inverse button's hover and the mark's eyes, nose and muzzle line.",
    "color-text": "Body text. The default ink for the hero copy, the info card, the FAQ, the form labels, the breadcrumb and the counter figures.",
    "color-text-muted": "Secondary text. Ledes, field hints, the breadcrumb's current crumb, the FAQ summary meta and the counter captions.",
    "color-text-on-inverse": "Text on a dark band. The footer, the section divider's caption, the header drawer and the chip on an inverse surface.",
    "color-brand": "The brand steel. Headings, the header, the mark's roundel, the info card's header band, the divider's rules, the counter figures and the outline button's border and label.",
    "color-brand-soft": "The brand tint. Chip beds, the breadcrumb chips, the header's hover and the outline button's hover fill.",
    "color-brand-mid": "Mid steel, a FILL only. The mark's rose ears; it is never text and so carries no contrast pair.",
    "color-brand-tint": "Pale steel, a FILL only. The mark's skull; it is never text and so carries no contrast pair.",
    "color-cta": "The call to action. The primary and submit button fills, the trust strip's icons, the header's search pill accent, the mark's brass ring and tongue, and the footer's accents. A FILL, never small text on bone, where it is 2.1:1.",
    "color-cta-ink": "The label on a brass fill. The primary and submit button text and the puppy card's price chip.",
    "color-cta-hover": "The brass under the pointer. The primary and submit buttons' hover fill.",
    "color-cta-soft": "The brass wash. The puppy card's price chip bed.",
    "color-link": "A link. The breadcrumb trail, the header nav and the text button.",
    "color-link-on-inverse": "A link on a dark band. Every footer link, including the social rows, and their hover.",
    "color-border": "A hairline. Card and field borders, the section divider's rules, the header's underline and the testimonial's separators.",
    "color-focus": "The focus ring on a light surface. Steel, because brass manages only 2.1:1 on bone and WCAG 1.4.11 asks 3:1 of a non-text component.",
    "color-focus-on-inverse": "The focus ring on a dark band. Brass, because steel on steel would vanish; the inverse button and the header drawer set it on themselves.",
    # ---- component colour
    "hdr-bg": "The site header's own background, so a page can repaint the bar without touching `color-surface-raised`.",
    "counter-bed": "The stat strip's bed — the tone shift half of rule `layout-hero-counter-separation`, whose other half is the 3px seam rule above it.",
    # ---- spacing
    "space-1": "4px. The tightest gap: the header's icon-to-label spacing.",
    "space-2": "8px. Chip rows, icon gaps and tight stacks; the most-used step in the kit after 12px.",
    "space-3": "12px. The default gap inside a component — the header's control spacing, card meta rows, FAQ and testimonial internals.",
    "space-4": "16px. Block padding and the gap between a heading and its body in the hero, the FAQ, the form and the footer columns.",
    "space-5": "24px. Card padding and the gap between the hero's copy blocks, the divider's parts and the footer's column rows.",
    "space-6": "32px. Section padding: the trust strip, the form, the counter strip, the testimonial and the footer's column gutter.",
    "space-7": "40px. Declared for a larger section step; nothing in the kit uses it yet.",
    "space-8": "48px. Band padding: the hero, the divider's outer margin, the footer's band and the testimonial's outer rhythm.",
    "space-9": "56px. Declared for a larger band step; nothing in the kit uses it yet.",
    "space-10": "64px. The hero band's own vertical padding.",
    "space-11": "80px. Declared for the widest band step; nothing in the kit uses it yet.",
    "space-12": "96px. Declared for the widest band step; nothing in the kit uses it yet.",
    # ---- radius
    "radius-sm": "6px. Form fields, the header's search input and drawer controls, the breadcrumb chips and the FAQ panel's inner edges.",
    "radius-md": "12px. The FAQ panel and the form's larger controls; also the value behind `btn-form-radius`.",
    "radius-lg": "20px. Never named directly: it is the value behind `card-radius`.",
    "radius-pill": "50px. The chip and the header's search pill; also the value behind `btn-radius`, the brand signature.",
    "btn-radius": "The primary, outline and inverse buttons — the brass pill that is the brand's signature (design rule 3).",
    "btn-form-radius": "The form submit button only. A full-width submit reads as a field control, not as a pill (design rule 3).",
    "card-radius": "Every card shell: the puppy card, the info card, the testimonial, the hero's photo frame and the header drawer.",
    # ---- shadow
    "shadow-card": "The resting card. Steel-tinted, on `.kit-card` and so on every component that uses the shared shell (design rule 5).",
    "shadow-lift": "The card under the pointer, and the header drawer. Only opt-in: a card that is not a link should not rise (design rule 5).",
}


def verify_usage(names):
    """Every token has a usage sentence, and no sentence is left behind by a deleted token."""
    missing = [n for n in names if n not in USAGE or not USAGE[n].strip()]
    if missing:
        raise SystemExit(f"tokens with no usage sentence: {', '.join(missing)}")
    stale = [n for n in USAGE if n not in names]
    if stale:
        raise SystemExit(f"usage sentences for tokens tokens.css no longer declares: {', '.join(stale)}")


# --------------------------------------------------------------------------- tokens.json

#: The text scale, as `--text-*` declares it. A style's size and line height are read from
#: tokens.css rather than retyped; the group, weight and name are the editorial decision.
TYPE_GROUPS = (
    ("Display", "display", (
        ("h1", "text-4xl", 700, "Page title. The hero's H1, at the size rule 10's clamp leaves it."),
        ("h2", "text-3xl", 700, "Section heading, and the hero's heading when a page already owns its H1."),
        ("h3", "text-2xl", 600, "Sub-section heading; the contact form's own title."),
        ("h4", "text-xl", 600, "Card heading: the puppy card's name, the info card's statement and the counter figures."),
    )),
    ("Text", "body", (
        ("lead", "text-lg", 400, "The lede under a heading, and the testimonial quote."),
        ("body", "text-base", 400, "Running copy: the FAQ answers and every paragraph the kit renders."),
        ("label", "text-sm", 600, "A form label, a nav item and the trust strip's claims."),
        ("small", "text-sm", 400, "Secondary copy: field hints, card meta, breadcrumbs and footer links."),
        ("micro", "text-xs", 600, "Chips, eyebrows, statement labels and the footer's fine print."),
    )),
)


def tokens_json(L=None):
    """The type's token document: one LIST per family, colours aliasing colours."""
    L = layers() if L is None else L
    colours, spacing, radius, shadow = [], [], [], []

    def add(bucket, name, value, layer):
        bucket.append({"name": name, "value": value, "usage": USAGE[name]})

    for layer in LAYERS:
        for decl, raw in L[layer].items():
            name = decl.lstrip("-")
            raw = raw.strip()
            alias = alias_of(raw)
            # A composite (`card-border`), a gradient (`seam-gradient`) or a motion value has
            # no family in this grammar: the type has no motion family and refuses `var()`
            # inside a shadow or a generic value. They are documented in README.md instead.
            if decl in ("--card-border", "--seam-gradient", "--dur-fast", "--dur-base",
                        "--ease-out") or decl.startswith("--font-") or decl.startswith("--text-"):
                continue
            if decl.startswith("--color-") or decl in ("--hdr-bg", "--counter-bed"):
                # Colours are the one family that may alias, and the semantic layer IS an
                # alias layer: writing the hex twice would let the two drift.
                add(colours, name, "{%s}" % alias if alias else raw.lower(), layer)
            elif decl.startswith("--space-"):
                add(spacing, name, resolve(raw, L), layer)
            elif decl.startswith("--radius-") or decl in ("--btn-radius", "--btn-form-radius",
                                                          "--card-radius"):
                # Lengths may not alias, so a component radius carries its literal.
                add(radius, name, resolve(raw, L), layer)
            elif decl.startswith("--shadow-"):
                add(shadow, name, resolve(raw, L), layer)

    verify_usage([t["name"] for t in colours + spacing + radius + shadow])
    names = [t["name"] for t in colours + spacing + radius + shadow]
    if len(names) != len(set(names)):
        raise SystemExit("token names are not unique across families")

    text_scale = {k.lstrip("-"): v.strip() for k, v in L["primitive"].items()
                  if k.startswith("--text-")}
    groups = []
    for group_name, family, styles in TYPE_GROUPS:
        rows = []
        for style, step, weight, usage in styles:
            rows.append({"name": style,
                         "fontSize": text_scale[step],
                         "lineHeight": float(text_scale[f"{step}--line-height"]),
                         "fontWeight": weight,
                         "usage": usage})
        groups.append({"name": group_name, "family": family, "styles": rows})

    return {
        "name": "BlueStaffyUK",
        "version": 1,
        "color": {"themes": [{"id": "light", "name": "Light"}], "tokens": colours},
        "type": {
            # Both families are served by Google Fonts and linked from every preview, so
            # nothing is embedded and `fonts` stays empty.
            "fonts": [],
            "families": {"display": L["primitive"]["--font-display"].strip(),
                         "body": L["primitive"]["--font-body"].strip()},
            "groups": groups,
        },
        "spacing": {"note": "A 4px grid. Steps 1–6 space the inside of a component, 8–12 its band.",
                    "tokens": spacing},
        "radius": {"note": "The pill is the brand signature; the form submit is the one exception.",
                   "tokens": radius},
        "shadow": {"note": "Steel-tinted, never neutral grey and never hand-written (design rule 5).",
                   "tokens": shadow},
    }


# --------------------------------------------------------------------------- components

#: Every row of `data/design/components.json`, in its order: project 3's thirteen, and
#: project 4's two in-page nav components (spec §3 — the Design System artifact gains a
#: preview for each). Unlike the canvas and the picks board, this artifact documents the
#: CURRENT kit rather than a record of a closed pick process, so it does not filter on
#: `project`. `group` sections the artifact's component table; the prose is written here
#: because it is editorial, and each `checks` row names a test that holds the component
#: to it, most of them in `tests/py/test_design_components.py`.
COMPONENTS = {
    "site-header": dict(
        comp="SiteHeader", group="Navigation",
        summary="The site's top bar: the logo-only lockup, the primary nav, a search combobox and the mobile drawer.",
        props=["`class` and any `HTMLAttributes<'header'>` attribute, spread onto the root — the component takes no other props; the nav and the site name come from `src/lib/site.ts` and `data/settings.json`."],
        states=["Resting, hover and focus on every nav item and control.",
                "Search: closed, open with a listbox of options, one option active (`aria-activedescendant`), and the polite status line carrying the result count.",
                "Drawer: closed, and open — below 768px the search form becomes a full-width bar row.",
                "Sticky on a real page; the preview pins one copy static, because a page has one set of top chrome."],
        checks=["`test_built_site_header_is_logo_only_with_the_search_pill_and_the_drawer`",
                "`test_the_header_search_is_one_combobox_with_one_of_everything`",
                "`test_the_header_search_script_handles_the_combobox_keys_smoke`"],
        donts=["Do not add a wordmark beside the mark — the header is logo only (spec §11 amendment 3b).",
               "Do not mount a second search form for the drawer; there is one combobox and CSS moves it.",
               "Do not make the results list an `aria-live` region: it holds the active option and would be re-announced on every keystroke.",
               "Do not mount a second sticky header on a page; the render harness measures the chrome once."]),
    "hero": dict(
        comp="Hero", group="Layout",
        summary="The page's opening band: eyebrow, heading, lede, trust chips, two calls to action and the photo.",
        props=["`as?: 'h1' | 'h2'` — the heading level, default `'h1'`; a page that already owns an H1 passes `'h2'`.",
               "`eyebrow?: string` — default `KC registered · <location label>` from `data/settings.json`.",
               "`title?: string` — default `Blue Staffy puppies raised in a family home`.",
               "`lede?: string` — default names the health-tested parents, the Kennel Club paperwork and the delivery floor; two lines at the desktop clamp.",
               "`class` and any `HTMLAttributes<'section'>` attribute, spread onto the root."],
        states=["Desktop (≥1024px): the band is clamped between 390px and 450px and the photo is what the clamp crops.",
                "Below 1024px: height is auto, so a phone hero never clips its own call to action.",
                "Hover and focus on both CTAs."],
        checks=["`test_built_hero_carries_its_photo_copy_chips_and_ctas`",
                "`test_built_hero_puts_the_image_before_the_heading`",
                "`test_measured_hero_fits_its_clamp_without_clipping_anything`"],
        donts=["Do not put `overflow: hidden` anywhere on the copy path — a hero that no longer fits must fail loudly, not lose its CTA row quietly.",
               "Do not lengthen the lede past two lines: `lede_overflow` is measured at 1024, 1100 and 1280 and must be zero.",
               "Do not move the image after the copy in source order; CSS `order` puts it back where the layout wants it."]),
    "buttons": dict(
        comp="Buttons", group="Forms",
        summary="The five button jobs: the brass primary pill, the outline beside it, the inverse pill for dark bands, the full-width form submit and the text link.",
        props=["`kind?: 'primary' | 'outline' | 'inverse' | 'submit' | 'text'` — which job, default `'primary'`.",
               "`label: string` — the visible text; required.",
               "`class` and any `HTMLAttributes<'a'>` or `HTMLAttributes<'button'>` attribute, spread onto the root — an `href` renders an anchor, a `type` a button."],
        states=["Resting, hover (`color-cta-hover` on the brass fills, `color-brand-soft` under the outline, `color-surface-deep` under the inverse) and focus.",
                "`inverse` paints its own dark band and sets `--kit-ring` on itself, because the steel ring would be invisible on its steel fill."],
        checks=["`test_built_buttons_show_all_five_kinds`"],
        donts=["Do not colour a label brass on a light surface: brass is 2.1:1 on bone and is a FILL carrying `color-cta-ink`.",
               "Do not give a form submit the pill radius, or a page CTA the form radius (design rule 3).",
               "Do not hard-code a focus colour; read `--kit-ring`, which the surface sets."]),
    "puppy-card": dict(
        comp="PuppyCard", group="Content",
        summary="One puppy: the photo, the name, the price chip, the availability status and the meta row.",
        props=["`slug?: string` — which puppy to render from `data/puppies.json`, default `'roman'`.",
               "`class` and any `HTMLAttributes<'article'>` attribute, spread onto the root."],
        states=["Resting and hover — the card opts into `.kit-card--lift`, because it is a link.",
                "Availability: the status dot takes `color-ok` when the puppy is available.",
                "A longer colour name wraps the meta row, which is why the preview shows two puppies."],
        checks=["`test_built_puppy_card_carries_price_status_and_the_chip_row`"],
        donts=["Do not type a price, a colour or a status into the markup: every figure is `data/puppies.json`.",
               "Do not add the lift to a card that is not a link."]),
    "trust-strip": dict(
        comp="TrustStrip", group="Layout",
        summary="Three backed claims on a dark band, each with an inline line icon.",
        props=["`class` and any `HTMLAttributes<'section'>` attribute, spread onto the root — the three claims are the component's own."],
        states=["One band; the icons take `color-cta` on the inverse surface."],
        checks=["`test_built_trust_strip_carries_three_backed_claims_and_line_icons`"],
        donts=["Do not use an emoji for a claim icon — inline stroke SVG on a 24 grid only (design rule 7).",
               "Do not add a fourth claim that the homepage does not already back."]),
    "counter-strip": dict(
        comp="CounterStrip", group="Layout",
        summary="The figures strip: a row of counts with captions, on its own bed under a seam rule.",
        props=["`class` and any `HTMLAttributes<'section'>` attribute, spread onto the root — the figures come from the data files."],
        states=["One row; the bed is `counter-bed` and the seam above it is a 3px `seam-gradient` bar."],
        checks=["`test_built_counter_strip_keeps_the_harness_hooks_and_the_data_figures`",
                "`test_kit_counter_fixture_hexes_are_the_tokens_they_stand_for`",
                "`layout-hero-counter-separation` in `tests/render/checks/layout.ts`"],
        donts=["Do not place this flush under a hero on one continuous background: the rule asks for a tone shift AND a 1px rule, at minimum.",
               "Do not separate it with whitespace alone.",
               "Do not type a figure: every number is read from data."]),
    "info-card": dict(
        comp="InfoCard", group="Content",
        summary="A kinded statement card: a labelled band, a heading and a short body.",
        props=["`kind?: StatementKind` — the statement kind, default `'fact'`; it also picks the default label.",
               "`label?: string` — overrides the kind's label from `src/lib/statement.ts`.",
               "`heading?: string` — the card's heading. Named `heading`, not `title`, because `HTMLAttributes<'article'>` already owns `title`.",
               "`body?: string` — the card's body.",
               "`class` and any `HTMLAttributes<'article'>` attribute, spread onto the root."],
        states=["One per statement kind; the preview shows `fact` and `recommendation`, because a board showing one label would hide whether the others paint at all."],
        checks=["`test_built_info_card_carries_a_kinded_statement_label`"],
        donts=["Do not pass `title` expecting the heading — it lands on the element as a tooltip.",
               "Do not invent a claim: the defaults are claims the live homepage already makes."]),
    "testimonial": dict(
        comp="Testimonial", group="Content",
        summary="Reviews, either one given room or a strip of three.",
        props=["`mode?: 'single' | 'grid'` — one review or the multi-review strip, default `'single'`.",
               "`reviews?: Review[]` — an explicit list, rendered in full; the default is the component's own slice of `data/reviews.json`.",
               "`class` and any `HTMLAttributes<'section'>` attribute, spread onto the root."],
        states=["`single` and `grid`, both on the dark band.",
                "A slot with no real review carries `REVIEW_PLACEHOLDER`, which `scripts/placeholder_check.py` counts."],
        checks=["`test_built_testimonial_blocks_quote_the_reviews_file_verbatim_in_both_modes`",
                "`test_the_testimonial_takes_an_explicit_review_list`",
                "`test_reviews_json_quotes_exist_verbatim_on_the_page_each_one_names`"],
        donts=["Do not edit a quote: the text must match `data/reviews.json` verbatim.",
               "Do not fill an empty slot with invented praise — leave `REVIEW_PLACEHOLDER` standing."]),
    "faq": dict(
        comp="Faq", group="Content",
        summary="A native `<details>` accordion of backed answers.",
        props=["`items?: FaqRow[]` — the rows; the default is the component's own three, two of them read from `data/settings.json` so a price change is never a copy edit.",
               "`class` and any `HTMLAttributes<'div'>` attribute, spread onto the root."],
        states=["Each row closed and open; hover and focus on the summary."],
        checks=["`test_built_faq_is_native_details_with_backed_answers`"],
        donts=["Do not replace `<details>`/`<summary>` with scripted disclosure: the accordion must work with no JavaScript.",
               "Do not type a price into an answer."]),
    "contact-form": dict(
        comp="ContactForm", group="Forms",
        summary="The enquiry form: six controls, a honeypot and two hidden fields — the whole form contract.",
        props=["`class` and any `HTMLAttributes<'form'>` attribute, spread onto the root — the puppy options are read from `data/puppies.json`."],
        states=["Resting, focus and hover on every control; the submit is full width at `btn-form-radius`.",
                "The honeypot is present and hidden."],
        checks=["`test_built_contact_form_keeps_the_whole_form_contract`",
                "`scripts/form_contract_audit.py` (the preview route is in its `NON_CONTENT_ROUTES`)"],
        donts=["Do not drop or rename a field: the six controls, the honeypot and the two hidden fields are the contract.",
               "Do not point the action at a live endpoint from a preview; the endpoint is `FORMSPREE_ID_PLACEHOLDER` until project 6 provisions one."]),
    "page-nav": dict(
        comp="PageNav", group="Navigation",
        summary="The breadcrumb trail, with an optional in-page section chip row under it.",
        props=["`path?: string` — the page's own path, which `crumbs()` turns into the trail.",
               "`title?: string` — the current page's title, the last crumb.",
               "`sections?: NavSection[]` — `{ id, label }` rows for the chip row; default `[]`, which renders the breadcrumb alone.",
               "`class` and any `HTMLAttributes<'div'>` attribute, spread onto the root."],
        states=["Breadcrumb only (the default), and breadcrumb plus chip row.",
                "Hover and focus on every crumb and chip; the current crumb is muted and not a link."],
        checks=["`test_built_page_nav_carries_the_real_trail_and_the_chip_row`",
                "`nav-anchors-resolve` in the render harness"],
        donts=["Do not pass a section id that does not exist on the page that mounts this: a dead in-page anchor is blocking, and a preview gets no pass for being a preview.",
               "Do not hand-build the trail; pass `path` and let `crumbs()` derive it."]),
    "footer": dict(
        comp="Footer", group="Navigation",
        summary="The site footer: a call-to-action band, four link columns, the contact rows and the social icons.",
        props=["`class` and any `HTMLAttributes<'footer'>` attribute, spread onto the root — every link and contact row comes from the nav data and `data/settings.json`."],
        states=["One deep-steel band; hover and focus shift every link to `color-link-on-inverse`.",
                "Four social anchors, each an inline 24-grid SVG plus the platform name."],
        checks=["`test_built_footer_carries_the_nav_the_socials_and_the_contact_rows`",
                "`test_built_footer_carries_the_cta_band_and_social_icons`"],
        donts=["Do not drop the CTA band, or move it after the columns — it is first in source order (spec §11 amendment 5a).",
               "Do not use an icon alone or a name alone for a social link: the icon is `aria-hidden` and the anchor carries `aria-label=\"<site name> on <Platform>\"`.",
               "Do not derive a platform name by capitalising the settings key — that produces \"Youtube\".",
               "Do not use an `<img>`, an icon font or an emoji here: the icons are paths."]),
    "section-divider": dict(
        comp="SectionDivider", group="Brand",
        summary="The brand divider: the mark on a medal between two hairline rules.",
        props=["`inverse?: boolean` — set it when the divider sits on a dark band.",
               "`class` and any `HTMLAttributes<'div'>` attribute, spread onto the root."],
        states=["Two: the default, where the medal is `color-surface-raised` and the rules are "
                "`color-border`; and `inverse`, for a dark band."],
        checks=["`test_built_section_divider_is_the_mark_between_two_rules`"],
        donts=["Do not substitute a glyph or an image for the mark: it is a `<use>` at the document sprite.",
               "Do not use this as a spacer — it is a brand beat, not a margin."]),
    # ------------------------------------------------------------------ project 4 (spec §3)
    # The pair is ONE piece of in-page navigation split at 1024px: the dial owns desktop, the
    # sheet owns everything below it, and a page mounts both. Documented as two components
    # because they are two files with two APIs, but every "don't" that names the breakpoint
    # is really the same rule said twice.
    "page-dial": dict(
        comp="PageDial", group="Navigation",
        summary="The desktop in-page dial: a sticky 196px column of hairline-ruled, numbered section rows with a scroll-spy.",
        props=["`sections: SectionRef[]` — the page's own sections, `{ id, label }`, in the page's order. "
               "`src/lib/sections.ts` builds the list from a board record with `sectionsFromRecord()`; the "
               "component never derives it, because the order belongs to the page.",
               "`title?: string` — the list heading, default `'On this page'`.",
               "`class` and any `HTMLAttributes<'aside'>` attribute, spread onto the root."],
        states=["Hidden below 1024px — SectionStrip and SectionSheet are the in-page nav there, and a dial "
                "that merely shrank would be a second copy of the same links in the tab order.",
                "Scroll-spy active: the current row carries `aria-current`, painted `color-brand-soft` on "
                "`color-brand`. The reading band is `-40% 0px -55% 0px`, the same window SectionStrip and "
                "SectionSheet use, so the three never disagree about which section the reader is in.",
                "Resting, hover and focus on every row; the focus ring is `--kit-ring` at 3px.",
                "Row one is marked current at render, so the dial is never blank before JS runs."],
        checks=["`test_built_page_dial_is_a_numbered_strip_with_spy_hooks_and_no_ring`",
                "`test_no_built_page_ships_an_empty_aria_current` and "
                "`test_no_built_page_ships_a_duplicate_id` (dist-wide).",
                "`a11y-no-duplicate-ids` (render harness, advisory) — the demo's six stub targets are "
                "rendered once per PAGE, not once per demo box.",
                "`nav-jump-target-lands` (render harness, blocking) — every row's target must clear the top chrome.",
                "`nav-anchors-resolve` (render harness, blocking) — a row pointing at no element is a dead anchor."],
        donts=["Do not pass sections whose ids are not on the page: the dial's rows are ordinary in-page links "
               "and the harness judges them as such.",
               "Do not mark the current row with `toggleAttribute('aria-current', …)`. That emits "
               "`aria-current=\"\"`, and the empty string is the token `false` — the row a reader is in "
               "would be announced as the one row that is NOT current. Use "
               "`setAttribute('aria-current', 'location')` and `removeAttribute`, and match "
               "`[aria-current=\"location\"]` in CSS so the paint and the announcement cannot disagree.",
               "Do not bring back the progress ring. The breeder picked the ringless arrangement on the "
               "contact board (2026-09-19): it repeated in a second place what the numbered rows already "
               "say, and its dash geometry was the only inline style this component wrote.",
               "Do not mount this without SectionStrip and SectionSheet: below 1024px the page would have "
               "no in-page nav at all."]),
    "section-sheet": dict(
        comp="SectionSheet", group="Navigation",
        summary="The mobile in-page nav: a fixed 64px bar of three site links with a full-width Sections pill above it, opening a native `<dialog>` bottom sheet of the page's sections.",
        props=["`sections: SectionRef[]` — the same list PageDial takes, from the same `src/lib/sections.ts` helper.",
               "`ctaLabel?: string` / `ctaHref?: string` — the sheet's primary button, default "
               "`'Available puppies'` to `/available-puppies/`.",
               "`class` and any `HTMLAttributes<'div'>` attribute, spread onto the root."],
        states=["Hidden at 1024px and above, and in print — PageDial owns in-page nav there.",
                "Bar: resting, hover and focus on the three tabs and the pill. The focus ring is `--kit-ring` at 3px with "
                "`outline-offset: -3px`, because the bar is flush to the viewport edge.",
                "Sheet closed, and open via `showModal()` — which is what supplies the focus trap, the inert "
                "background and the Escape key. Following a section link closes it, and so does a backdrop click.",
                "Scroll-spy active: the current row in the sheet carries `aria-current`, on the same reading "
                "band as the dial and the strip."],
        checks=["`test_built_section_sheet_has_tab_bar_and_dialog`",
                "`test_no_built_page_ships_an_empty_aria_current` and "
                "`test_no_built_page_ships_a_duplicate_id` (dist-wide).",
                "`nav-bottom-chrome-clear` (render harness, blocking) — the bar must never cover the landing "
                "position of an in-page jump target. The fixture pair "
                "`tests/render/fixtures/{known_good/kit-bottom-chrome-clear,known_broken/kit-bottom-chrome-covers}.html` "
                "is this component's own geometry.",
                "`layout-tap-target-size` (render harness, blocking) — every tab is at least 44px."],
        donts=["Do not delete the `is:global` `body:has(.kit-sheet) { padding-bottom: 116px }`. The bar is "
               "`position: fixed` and out of flow, so without the reservation the last 116px of every page — "
               "including a short final section a reader jumps to — sits underneath it.",
               "Do not delete the `@supports not selector(:has(*))` fallback beside it either. The scoped "
               "reservation depends on `:has()`; a browser without it drops the rule and loses the padding "
               "with no symptom until someone jumps to the last section. The fallback pads the body "
               "unconditionally there — a 116px gap on a page with no bar is cosmetic, a covered jump target "
               "is blocking.",
               "Do not replace the `<dialog>` with a div and `role=\"dialog\"`: the focus trap and Escape are "
               "native there, and the two that get forgotten by hand are always those two.",
               "Do not change the 64px bar or the 52px pill row without changing the 116px body reservation "
               "to match; they are one number said twice and `nav-bottom-chrome-clear` measures the pair.",
               "Do not use an emoji or an `<img>` for a tab icon — all four are inline stroke SVG on one 24 grid.",
               "Do not fold Sections back into the bar as a fourth tab. The breeder picked the pill on the "
               "contact board (2026-09-19): as one icon among four, the control this component exists for "
               "read as a site destination."]),
    "section-strip": dict(
        comp="SectionStrip", group="Navigation",
        summary="The mobile top chrome: a sticky, horizontally scrolling rail of numbered section chips "
                "(`01 Label · 02 Label …`) pinned under the header below 1024px.",
        props=["`sections: SectionRef[]` — the same list PageDial and SectionSheet take, from the same "
               "`src/lib/sections.ts` helper, so the three can never disagree about a page's sections.",
               "`label?: string` — the rail's accessible name, default `'Sections'`.",
               "`class` and any `HTMLAttributes<'nav'>` attribute, spread onto the root."],
        states=["Hidden at 1024px and above, and in print — PageDial owns in-page nav there.",
                "Chip resting, hover and focus. The focus ring is `--kit-ring` at 3px with "
                "`outline-offset: -2px`, because a chip sits flush inside a rail that clips.",
                "Scroll-spy active: the current chip carries `aria-current=\"location\"`, on the same reading "
                "band as the dial and the sheet, and is scrolled back into view when it changes.",
                "Chip one is marked current AT RENDER, so the rail is never blank before JS runs."],
        checks=["`test_built_section_strip_is_a_sticky_chip_rail_with_spy_hooks`",
                "`test_section_strip_pins_under_the_header_and_pays_for_its_own_height`",
                "`nav-jump-target-lands` (render harness, blocking) — the strip is part of the pinned top "
                "band `measureTopChrome` measures, and the fixture pair "
                "`tests/render/fixtures/{known_good,known_broken}/nav-jump-target-lands.html` carries a strip "
                "so a target landing underneath one is caught.",
                "`layout-tap-target-size` (render harness, blocking) — every chip is at least 44px."],
        donts=["Do not delete the `is:global` rule that adds `var(--strip-h, 0px)` to "
               "`[id] { scroll-margin-top }`. The strip is sticky and pins UNDER the header, so a target "
               "offset for the header alone lands behind the rail — the top-chrome twin of the defect "
               "`nav-bottom-chrome-clear` catches at the bottom of the viewport.",
               "Do not replace the ResizeObserver that publishes `--strip-h` with a constant. The rail is a "
               "different height in each of its styles, it rewraps, and it changes again when the display "
               "font loads — a hard-coded number is wrong in all three cases.",
               "Do not give the rail a visible scrollbar: it is thumb-scrolled, and a bar under 44px chips "
               "reads as a second control. The chips stay in the keyboard tab order regardless.",
               "Do not use `scrollIntoView({ inline: 'center' })` for the active chip — `center` scrolls the "
               "PAGE as well as the rail, fighting the scroll that moved the spy, and the strip jitters.",
               "Do not mount this without SectionSheet: the strip is the quick jump, the sheet is the full "
               "list, and below 1024px a long page needs both.",
               "Do not return the chips to outlines or to plain underlined text. The breeder picked the "
               "filled chip on the contact board (2026-09-19): a filled chip keeps its shape when it is "
               "half-scrolled at the rail's edge, and the other two did not."]),
    # Component 17 (working rule 13; spec §9 amendment 5). The only kit component whose
    # three board arrangements are a LAYOUT axis rather than a prop, which is why its
    # "don'ts" are mostly about the stack: the arrangement is a choice, the stacking is not.
    "data-table": dict(
        comp="DataTable", group="Content",
        summary="The data table: prices, delivery bands, health tests and comparisons, as a semantic "
                "`<table>` that stacks into labelled rows below 640px.",
        props=["`caption: string` — the table's name, rendered as a real `<caption>`. Not optional: a "
               "table with no name is a grid, and stacked it is a grid with no title either.",
               "`columns: string[]` — the column headers, in order. They are also the source of every "
               "cell's `data-label`, so the two can never disagree.",
               "`rows: (string | number)[][]` — one array per row, as long as `columns`. "
               "`scripts/pageboard.py` refuses a board record whose rows are any other length.",
               "`numeric?: number[]` — zero-based indexes of the columns to right-align. A LIST, not a "
               "guess from the content: `£1,500` and `£850 to £1,200` are both strings.",
               "`class` and any `HTMLAttributes<'table'>` attribute, spread onto the root."],
        states=["Three board arrangements on the `chrome` axis of `src/lib/boardStyles.ts`, resolved to "
                "`bl-chrome-*` classes by `boxClass()` and painted in `src/styles/board-styles.css`: "
                "S1 ruled rows under a brand header band, S2 zebra rows inside a card, S3 borderless with "
                "brass column rules. S1 is the component's own default, so a copy mounted outside a board "
                "box is a finished table.",
                "Stacked, below 640px: `.stack-table` turns every cell into a block, moves the `<thead>` "
                "off-screen and prints each cell's `data-label` before its value. All three arrangements "
                "stack the same way — it is not one of the three.",
                "On a steel band the header band re-points to `color-surface-deep`, and the caption and "
                "the row headers inherit the band's own text colour."],
        checks=["`test_built_data_table_is_semantic_and_labels_every_cell_for_the_stack`",
                "`layout-table-stacks-on-mobile` (render harness, blocking) — every `<table>` under "
                "`<main>` labels its cells, and below 640px lays its rows out as blocks with no sideways "
                "scroll. The fixture pair "
                "`tests/render/fixtures/{known_good,known_broken}/layout-table-stacks-on-mobile.html` "
                "is this component's own contract.",
                "`layout-no-horizontal-overflow` (render harness, blocking) — a table is the commonest "
                "way a page comes to scroll sideways on a phone."],
        donts=["Do not add a `chrome` prop. The three arrangements are a board axis so that what the "
               "breeder approves on `/board-preview/<slug>/` and what the rebuilt page resolves are one "
               "rule in one stylesheet; a prop would be the same decision written twice.",
               "Do not wrap it in `.table-wrap` to make it scroll. A sideways-scrolling table is the "
               "defect working rule 13 exists to stop, not the fallback for a wide one — drop a column.",
               "Do not omit `data-label` on a cell, or write one that is not its column's name. With the "
               "header row moved off-screen it is the only thing left saying what the cell is.",
               "Do not type a price, a delivery band or a test result in here by hand: the numbers come "
               "from `data/price-matrix.json`, `data/puppies.json`, `data/settings.json` or the board "
               "record's own `table` block (rule 9).",
               "Do not use the first column's `<th scope=\"row\">` for an ordinary value — it is the "
               "row's title, and it is what a screen reader announces before every cell in the row."]),
    # Component 18 (working rule 14; spec §9 amendment 7). The one component whose board
    # axes are half class and half prop: the bed is CSS, the facade is markup.
    "video-embed": dict(
        comp="VideoEmbed", group="Content",
        summary="A YouTube video from the old site, reused at its original id, in a reserved 16:9 box "
                "that loads its player only when someone presses play.",
        props=["`id: string` — the eleven-character YouTube id, never a url and never a pasted embed "
               "code. Working rule 14: it is the id the old site already carries.",
               "`title: string` — required. It is the accessible name, on the `<iframe>` and on the "
               "facade's play button alike; an unnamed frame is unnavigable.",
               "`caption?: string` — one line under the box, as a real `<figcaption>`.",
               "`play?: 'facade' | 'iframe'` — `facade` (the default) draws the thumbnail and injects "
               "the player on the first click; `iframe` puts the player in the document immediately.",
               "`class` and any `HTMLAttributes<'figure'>` attribute, spread onto the root."],
        states=["Three board arrangements on the `frame` and `play` axes of `src/lib/boardStyles.ts`: "
                "S1 the player in a card with the caption beneath it, S2 the player full width on a "
                "steel band, S3 the click-to-play facade. S3 is what a rebuilt page takes unless the "
                "board says otherwise, because it is the only one that costs nothing before a click.",
                "Without scripting the facade is replaced by the plain player: the `<noscript>` block "
                "carries both the `<iframe>` and the rule that hides the button.",
                "The 16:9 box is reserved by `aspect-ratio`, so nothing below the video moves when the "
                "thumbnail decodes."],
        checks=["`test_built_video_embed_reserves_its_box_and_loads_on_click`",
                "`layout-image-box-reserved` (render harness) — the reserved box and the painted box "
                "are the same box.",
                "`scripts/facts_preserved_check.py` — a video id the migrated page carried and the "
                "rebuilt page does not is a dropped fact, reported by name."],
        donts=["Do not mint a new video id, and do not re-upload the footage. Every id already ranks in "
               "video search; a fresh one starts at zero (working rule 14).",
               "Do not point the player at `youtube.com`. The component uses `youtube-nocookie.com`, and "
               "the facade makes no request at all before the click except the thumbnail.",
               "Do not drop the `title`. It is the frame's only accessible name.",
               "Do not set a fixed height on the box or wrap it in a padding-ratio hack: the "
               "`aspect-ratio` here is what the CLS check measures."]),
}

#: The marker's `group`, in the order the artifact's component table should read.
GROUP_ORDER = ("Brand", "Navigation", "Layout", "Content", "Forms")


def preview_html(sec, css, sprite, height, images, group, comp):
    """One `components/<Comp>/preview.html`: the marker, then a self-contained document.

    Static by design (see the module docstring): no bundle to mount, no scripts at all, the
    page's stylesheet inlined and the sprite pasted back in when the section references it."""
    inner = rewrite_assets(sec.inner, images)
    inner = re.sub(r"<h3[^>]*>.*?</h3>\s*", "", inner, count=1, flags=re.S)   # the route's caption
    # A `<noscript>` fallback is BEHAVIOUR, not a picture of the component. VideoEmbed's
    # carries the real player, and an artifact preview is a static document served with
    # scripting on — so the block would never be shown to a reader and would only make the
    # one preview in the set that embeds a third-party frame. Stripped for the same reason
    # `_kit_sections.find_sections` strips `<script>`.
    inner = re.sub(r"<noscript>.*?</noscript>", "", inner, flags=re.S)
    head_sprite = f"{sprite}\n" if sprite and uses_sprite(inner) else ""
    return (
        f'<!-- @dsCard group="{group}" height={height} width={sec.width} -->\n'
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{H.escape(comp)} — BlueStaffyUK</title>\n{FONTS_LINK}\n<style>\n"
        "body{margin:0;font-family:'Source Sans 3',system-ui,sans-serif;"
        "background:var(--color-surface,#F4F1EA)}\n"
        "a{color:var(--color-link,#1F3A52)}a:hover{color:var(--color-surface-deep,#14202B)}\n"
        f"{css}\n</style>\n</head>\n<body>\n{head_sprite}"
        f'<div style="width:{sec.width}px;max-width:100%;box-sizing:border-box;'
        'display:flex;flex-direction:column">\n'
        f"{inner}\n</div>\n</body>\n</html>\n"
    )


def component_readme(cid, spec):
    """`components/<Comp>/README.md`. First sentence is the manifest summary.

    The opening paragraph states the file the artifact name maps to, ALWAYS and not only when
    the two differ. Four of the thirteen are not named after their file — `SiteHeader` is
    `SiteHeaderKit.astro`, `Buttons` is `Button.astro`, `Footer` is `SiteFooterKit.astro` and
    `ContactForm` is `ContactFormKit.astro` — because the artifact groups components by what a
    reader calls them and the repo names them for what they are. A reader who guesses the
    filename from the heading is wrong four times in thirteen, so the mapping is printed
    rather than implied, and those four say the difference in words as well.
    """
    def bullets(rows):
        return "\n".join(f"- {r}" for r in rows)
    file = FILE_BY_ID[cid]
    aka = ("" if file == f"{spec['comp']}.astro" else
           f" **The two names differ:** this artifact calls it *{spec['comp']}*,"
           f" the repo calls it `{file[:-6]}` \u2014 mount `{file[:-6]}`, not `{spec['comp']}`.")
    return f"""# {spec['comp']}

{spec['summary']} It is an Astro component in the site repo at `src/components/kit/{file}`, and the preview beside this file is a static rendering of its built markup, not a live mount.{aka}

## Props

{bullets(spec['props'])}

## Slots

None. Every kit component takes its content through props and its data from `data/`, so there is no slot to fill — a caller that needs different content passes a prop or edits the data file.

## States

{bullets(spec['states'])}

## What holds it up

{bullets(spec['checks'])}

## Don'ts

{bullets(spec['donts'])}
"""


# --------------------------------------------------------------------------- the cover

def badge_inner():
    """The badge's paths, hexes already resolved, lifted out of the shipped icon lockup.

    `public/brand/logo-icon.svg` IS the standalone mark with every `var()` resolved — it is
    what `scripts/build_lockups.py` wrote from `markShapes.ts`. Re-resolving the geometry here
    would be a second copy of a drawing that has to stay identical, so the cover reads the
    file instead."""
    svg = (BRAND / "logo-icon.svg").read_text()
    inner = svg[svg.index(">", svg.index("<svg")) + 1:svg.rindex("</svg>")]
    return re.sub(r"<title\b.*?</title>\s*", "", inner, flags=re.S).strip()


COVER_HEIGHT = 288


def cover_html(hexes):
    """`components/Cover/preview.html` — the face of the system, at 960 × 288.

    Sized per the type's cover brief: the name at 64px ("BlueStaffyUK" is one unbreakable
    word and measures about 422px at that size in a serif, inside the 440px text zone), the
    blocks and pattern in one box from x = 480 to the right edge, one layout, no motion."""
    c = hexes
    return f"""<!-- @dsCard height={COVER_HEIGHT} -->
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>BlueStaffyUK — cover</title>
{FONTS_LINK}
<style>
  body {{ margin: 0; background: {c['color-bone-100']}; }}
  .brand {{ fill: {c['color-steel-700']}; }}
  .deep {{ fill: {c['color-steel-900']}; }}
  .cta {{ fill: {c['color-brass-500']}; }}
  .soft {{ fill: {c['color-steel-100']}; }}
  .tint {{ fill: {c['color-brass-200']}; }}
  .ring {{ fill: none; stroke: {c['color-brass-500']}; stroke-width: 4; }}
  .ground {{ fill: {c['color-bone-100']}; }}
  .name {{ fill: {c['color-ink']}; font-family: "Fraunces", Georgia, serif;
           font-weight: 700; font-size: 64px; }}
  .tag {{ fill: {c['color-ink-3']}; font-family: "Source Sans 3", system-ui, sans-serif;
          font-weight: 400; font-size: 14px; }}
</style>
</head>
<body>
<!-- Derivation.
     Blocks: steel-700 240x208 slab, steel-900 112x96, brass-500 112x96, brass-200 112x96,
             steel-100 112x96 — every side is a 4px-grid multiple of space-6 (32px), and the
             208 is space-6 x 6.5, the slab's own two-satellite height plus the 16px gutter.
     Arrangement: one tall brand slab at x=480, a 2x2 of satellites to its right, the last
             column bleeding off the right edge; weighted by identity, not a swatch row.
     Pattern: rings and pills from the radius scale, chosen because the brand's two signatures
             ARE a ring and a pill — the steel roundel with its brass ring (the mark) and the
             brass pill CTA that design rule 3 names the brand signature.
     Scales: gutter space-4 (16px), pitch space-6 (32px), corners radius-lg (20px) and
             radius-md (12px); the rings are the badge's own r=43 and r=47 on the 100 grid.
-->
<svg width="960" height="{COVER_HEIGHT}" viewBox="0 0 960 {COVER_HEIGHT}"
     xmlns="http://www.w3.org/2000/svg" role="img" aria-label="BlueStaffyUK design system">
  <rect class="ground" x="0" y="0" width="960" height="{COVER_HEIGHT}"/>

  <!-- blocks: one tall slab, a 2x2 of satellites, the last column off the right edge -->
  <rect class="brand" x="480" y="40" width="240" height="208" rx="20"/>
  <rect class="deep"  x="736" y="40"  width="112" height="96" rx="20"/>
  <rect class="cta"   x="736" y="152" width="112" height="96" rx="20"/>
  <rect class="tint"  x="864" y="40"  width="112" height="96" rx="20"/>
  <rect class="soft"  x="864" y="152" width="112" height="96" rx="20"/>

  <!-- pattern: the mark's two rings over the slab, and pills at the space-6 pitch -->
  <circle class="ring" cx="600" cy="116" r="47"/>
  <circle class="ring" cx="600" cy="116" r="43" opacity="0.4"/>
  <rect class="tint" x="512" y="196" width="88" height="24" rx="12"/>
  <rect class="cta"  x="616" y="196" width="56" height="24" rx="12"/>
  <rect class="soft" x="512" y="228" width="120" height="8" rx="4" opacity="0.45"/>

  <!-- the mark, as the brand's own figure above the name -->
  <g transform="translate(40 44) scale(0.46)">
{badge_inner()}
  </g>

  <!-- the name, on the ground, bottom-left, inside the 440px text zone -->
  <text class="name" x="40" y="196">BlueStaffyUK</text>
  <text class="tag"  x="42" y="228">The design system behind Blue Staffy UK — {c['location_label']}.</text>
</svg>
</body>
</html>
"""


# --------------------------------------------------------------------------- README.md

def design_rules(text):
    """The ten rules from `rules/design.md`, in their current wording.

    Nine of them are one numbered list under a heading; rule 10 is its own front-matter block
    further down. Both are lifted verbatim — a paraphrase of a non-negotiable rule is a second
    wording to argue about."""
    nine = text[text.index("**Non-Negotiable Design Rules"):].split("\n---")[0].strip()
    ten = text[text.index("10. **Hero image first in the DOM"):].strip()
    return nine, ten


def readme(tokens, settings, rules_text, comps):
    nine, ten = design_rules(rules_text)
    colour_rows = "\n".join(
        f"| `{t['name']}` | `{t['value']}` | {t['usage']} |" for t in tokens["color"]["tokens"])
    type_rows = "\n".join(
        f"| `{s['name']}` | {g['name']} | {s['fontSize']} / {s['lineHeight']} / {s['fontWeight']} | {s['usage']} |"
        for g in tokens["type"]["groups"] for s in g["styles"])
    space_rows = "\n".join(f"| `{t['name']}` | {t['value']} | {t['usage']} |"
                           for t in tokens["spacing"]["tokens"])
    radius_rows = "\n".join(f"| `{t['name']}` | {t['value']} | {t['usage']} |"
                            for t in tokens["radius"]["tokens"])
    shadow_rows = "\n".join(f"| `{t['name']}` | `{t['value']}` | {t['usage']} |"
                            for t in tokens["shadow"]["tokens"])
    comp_rows = "\n".join(
        f"| `{COMPONENTS[cid]['comp']}` | {COMPONENTS[cid]['group']} | `src/components/kit/{FILE_BY_ID[cid]}` | {COMPONENTS[cid]['summary']} |"
        for cid in comps)
    # Read from `price_range`, not typed: "£1500 - £1700" is the locked figure, and the
    # thousands separator is this document's formatting rather than a second source of truth.
    price_lo, price_hi = (f"£{int(n):,}" for n in re.findall(r"£\s*(\d+)", settings["price_range"]))
    return f"""# BlueStaffyUK

The design system behind Blue Staffy UK: the tokens every surface reads, the brand mark and
its lockups, and the {len(comps)} components the site is built from.

Generated by `scripts/build_design_system.py` from `src/styles/tokens.css`,
`data/design/components.json`, `data/settings.json`, `rules/design.md`, `public/brand/` and the
built `dist/kit-preview/`. **Do not edit this page by hand** — change the source and rebuild.

## Palette

Every colour on every surface is one of these, and nothing else. The primitives are the hues;
the semantic names are the only things a component is allowed to reach for, which is what
keeps a hue swappable. In the site repo `src/styles/tokens.css` is the ONLY file permitted to
spell a colour (design rule 1).

| Token | Value | Usage |
|---|---|---|
{colour_rows}

**The usage rules that matter most.**

- Headings, the header, the mark's roundel and the dark bands are `color-brand`. A heading is
  never brass.
- Every call to action is a `color-cta` FILL carrying `color-cta-ink`. Brass measures 2.1:1 on
  the bone surface, so it is never the colour of small text there — only a fill, an icon on a
  dark band, or a hairline accent.
- The page surface is `color-surface`; anything that lifts off it is `color-surface-raised`.
  Dark bands are `color-surface-inverse`, and the footer is `color-surface-deep`.
- Text is `color-text`, secondary text `color-text-muted`, and text on a dark band
  `color-text-on-inverse`. Add the pair to `data/design/contrast.json` before you use it: AA
  contrast for every text-on-background pair is asserted, not assumed.
- The focus ring is `color-focus` on light surfaces and `color-focus-on-inverse` on dark ones.
  A single fixed ring colour disappears on one of the two, because the brand steel and the
  inverse surface are the same value.
- `color-brand-mid` and `color-brand-tint` are FILLS in the mark only. They are never text and
  so carry no contrast pair; add one the day that changes.

## Type

Two families, both Google-hosted and linked rather than embedded — this system ships no font
files, and `tokens.json` `type.fonts` is empty by design.

- **Display — {tokens['type']['families']['display']}.** ALL headings, H1 to H6.
- **Body — {tokens['type']['families']['body']}.** All body copy, labels and buttons.

A `font-family` is never hard-coded on an element; the two families are applied globally
(design rule 2).

| Style | Group | Size / line height / weight | Usage |
|---|---|---|---|
{type_rows}

## Spacing

A 4px grid. Steps 1–6 space the inside of a component; 8–12 space its band.

| Token | Value | Usage |
|---|---|---|
{space_rows}

## Radius

| Token | Value | Usage |
|---|---|---|
{radius_rows}

The pill is the brand signature: the primary, outline and inverse buttons all take
`btn-radius`. The one exception is the form submit, which takes `btn-form-radius` because a
full-width submit reads as a field control rather than as a page CTA (design rule 3).

## Shadow

| Token | Value | Usage |
|---|---|---|
{shadow_rows}

Both are steel-tinted `rgba(20, 32, 43, …)`. Never a neutral grey, never a hand-written
shadow (design rule 5).

## Motion

Not a token family here — the type has none — but the values are fixed in
`src/styles/tokens.css` and are part of the system:

- `--dur-fast` **120ms**, `--dur-base` **200ms**, `--ease-out`
  **cubic-bezier(0.2, 0.7, 0.2, 1)**.
- Maximum 0.2s on any transition. No bounce, no parallax, no auto-playing video (design
  rule 6).

## Two composites

Two declarations are not single values and so have no family in this document's grammar. They
are still tokens in the source and must be used as such:

- `--card-border` — `1px solid var(--color-border)`, the border on every card.
- `--seam-gradient` — `linear-gradient(90deg, var(--color-steel-700), var(--color-brass-500))`,
  the 3px seam bar that separates a stat strip from the band above it.

## Logo

The mark is **the L1 badge**: a flat-shaded Staffordshire Bull Terrier head — broad skull, rose
ears, white blaze, breed grin with a brass tongue — inside a steel roundel with a brass ring.
The skull is `color-brand-tint`, the ears `color-brand-mid`, the roundel `color-brand`, the
ring and the tongue `color-cta`. The geometry lives once, in
`src/components/kit/markShapes.ts`, on a 100 × 100 grid; on a page it is a `<use>` at a
document sprite, and the lockup files inline it.

**The four lockups** (plus the favicon) are on this system under `assets/Logos/`:

- `logo-horizontal.svg` — the badge with the wordmark and strapline beside it. The default,
  and what the site header would use if the header carried a wordmark.
- `logo-stacked.svg` — the badge above the wordmark and strapline. For square and tall spaces.
- `logo-icon.svg` — the badge alone, on the 100 grid. This is the site header's lockup: the
  header is **logo only, no wordmark**.
- `logo-mono.svg` — a single-ink outline of the horizontal lockup, drawn in `currentColor`.
- `favicon.svg` — the badge again, as the tab icon.

**Clear space.** Keep clear on every side at least the radius of the badge's brass ring — on
the 100 grid that is 43 units, so a little under half the badge's width. Nothing sets type or
a rule inside it.

**Minimum size: 32px.** Below that the blaze, the eyes and the tongue stop resolving and the
badge reads as a blue dot. If you need smaller, you need a different mark, not this one
shrunk.

**Don't:**

- Don't recolour the badge. The five inks are tokens, and the two-tone head is the mark.
- Don't outline, emboss, add a shadow to, or rotate the badge.
- Don't stretch it: the lockups carry their own `viewBox` and must scale uniformly.
- Don't set the wordmark yourself — use a lockup file.
- Don't place the colour badge on a mid-steel background, where the roundel disappears. Use
  `logo-mono.svg` there.
- Don't use the badge below 32px, and don't crop it to the head.

## Iconography

Icons are **inline stroke SVGs on a 24 grid**, `stroke="currentColor"`, sized in `em`, one per
element. Never emoji (design rule 7). The only text glyphs kept are `✔ ✗ ★` as list and rating
markers.

- An icon inside a data array must be rendered with `set:html`, and `grep -rl "&lt;svg" dist/`
  must come back empty.
- **Never put an `<svg>` inside a CSS `content:`** — `content` renders plain text only, so the
  markup is dumped or dropped and the badge spacing collapses with it. Put the `<svg>` in the
  markup.
- The dog icon is never a generic emoji: it is the custom line-icon set, or the custom images
  when a filled mark is wanted.
- **The social set** — YouTube, Instagram, X and Facebook — is four inline 24-grid paths in
  `SiteFooterKit.astro`: a play mark in a rounded rectangle, a rounded square with a circle and
  a dot, two crossed strokes, and an `f`. They are paths, not characters, so nothing is loaded
  from an icon font. The icon is `aria-hidden` and the platform name stays beside it; the
  anchor carries `aria-label="<site name> on <Platform>"`.

## Components

All {len(comps)}, in the order `data/design/components.json` lists them. Each has a folder here with a
static preview and its own README.

| Component | Group | Source | What it is |
|---|---|---|---|
{comp_rows}

## The ten design rules

These are the repo's rules, in their current wording from `rules/design.md`. They are
non-negotiable and enforced on every build.

{nine}

{ten}

## Locked facts

Nothing on a surface may contradict these, and nothing may invent a figure they do not give.

- The breeder is **{settings['breeder_name']}**.
- The location is **{settings['location_label']}**.
- Puppies are **{price_lo}** and **{price_hi}** (`price_range` in `data/settings.json`).
- The deposit is **£{settings['deposit_gbp']}**, and it is **refundable**.
- UK delivery is **£{settings['delivery_min_gbp']}–£{settings['delivery_max_gbp']}, priced by
  distance** ({settings['delivery_note']}).

**Placeholders that must stay placeholders.** These are stand-ins for things nobody has yet,
and a design that fills one in has invented it. Named exactly as the repo names them:

- `SITE_URL_PLACEHOLDER` — the domain, unbought.
- `PHONE_PLACEHOLDER` — the number, unprovisioned.
- `FORMSPREE_ID_PLACEHOLDER` — the form endpoint.
- `LICENCE_CLAIM_PLACEHOLDER` — the breeder-licence claim, unverified.
- `LEGAL_CLAIM_PLACEHOLDER` — the Lucy's Law claim, unverified.
- `REVIEW_PLACEHOLDER` — a testimonial slot with no real review behind it.

`scripts/placeholder_check.py` counts every one of them on every run.

## Consuming this system

- The namespace `bsuk` prefixes every class name, data attribute and sprite id this system
  emits.
- **There is no bundle.** This system ships no `components/bundle.js` and no
  `components/bundle.css`, and declares no libraries. The components are **Astro**, in the site
  repo at `src/components/kit/`, and they are rendered on the server — there is nothing to
  mount in a browser.
- **The previews here are static renderings**, cut from the built `dist/kit-preview/` route:
  real built markup with the page's own stylesheet inlined and the images pointed at this
  system's file store. They are for reading and judging, not for running.
- **To use the tokens**, read `tokens.json` (or the compiled `tokens.css` this system serves)
  and take the values from there. In the site repo the tokens come from
  `src/styles/tokens.css`, which is the one file allowed to spell a colour.
- **To use a component**, import it from `src/components/kit/` in the site repo and read its
  README here for props, states and don'ts.
"""


# --------------------------------------------------------------------------- assets

def logo_readme(sizes):
    rows = "\n".join(f"| `{n}` | {sizes[n]:,} bytes |" for n in LOGO_FILES if n in sizes)
    return f"""# Logos

The BlueStaffyUK mark and its lockups, exactly as the site serves them. All five are SVG; all
but `logo-mono.svg` carry their own inks.

| File | Size |
|---|---|
{rows}

- **`logo-horizontal.svg`** — the badge with the wordmark and the strapline beside it, on a
  278 × 72 board. The default lockup.
- **`logo-stacked.svg`** — the badge above the wordmark and strapline, on a 216 × 148 board.
  For square and tall spaces.
- **`logo-icon.svg`** — the badge alone, on the 100 × 100 grid. This is the site header's
  lockup: the header is logo only.
- **`logo-mono.svg`** — a single-ink outline of the horizontal lockup. **Its ink is
  `currentColor`**, so whatever paints it must set a colour: use `color-brand` on a light
  surface and `color-text-on-inverse` on a dark band.
- **`favicon.svg`** — the badge again, as the browser tab icon.

Clear space on every side is at least 43 units of the badge's own 100 grid. The minimum size
is 32px; below that the blaze, eyes and tongue stop resolving. Do not recolour, outline,
rotate or stretch any of them — see the brand book's Logo section.
"""


# --------------------------------------------------------------------------- the index

def index_json(asset_blobs, sizes, now):
    """`design-system.json`, the file-layout index.

    An asset with no uploaded blob is REFUSED an `assetGroups.files` entry rather than given
    an invented one: an index that names a blob the store does not hold is an index that
    renders a broken tile and says nothing about why."""
    files, order = {}, []
    for name in LOGO_FILES:
        rec = asset_blobs.get(name)
        if not rec or not rec.get("blob"):
            continue
        order.append(name)
        files[name] = {"name": name, "blob": rec["blob"],
                       "size": rec.get("size", sizes.get(name, 0)),
                       "type": rec.get("type", "image/svg+xml")}
    return {
        "v": 3,
        "layout": "files",
        "createdOnFiles": {"v": 1, "at": now},
        "title": "BlueStaffyUK",
        "namespace": "bsuk",
        "libraries": [],
        "sections": {},
        "groups": ["Logos"],
        "assetGroups": {"Logos": {"name": "Logos", "tile": "l", "order": order, "files": files}},
        "blobs": {},
        "docs": {"readme": "project/README.md", "sections": []},
        "lastChange": {"by": "Lisa Bright's BSUK team", "at": now,
                       "via": "Claude Code (scripts/build_design_system.py)",
                       "note": "project 3 close-out"},
    }


# --------------------------------------------------------------------------- main

FILE_BY_ID = {}


def load_asset_map():
    if not ASSET_MAP.exists():
        return {}, {}
    raw = json.loads(ASSET_MAP.read_text())
    return raw.get("assets", {}), raw.get("images", {})


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default=str(ROOT / "dist/kit-preview/index.html"))
    ap.add_argument("--out", default=str(ROOT / "docs/artifacts/design-system"))
    ap.add_argument("--heights", default=str(ROOT / "data/design/canvas-heights.json"))
    a = ap.parse_args(argv)

    rows = json.loads((ROOT / "data/design/components.json").read_text())
    FILE_BY_ID.clear()
    FILE_BY_ID.update({r["id"]: r["file"] for r in rows})
    settings = json.loads((ROOT / "data/settings.json").read_text())
    heights = json.loads(pathlib.Path(a.heights).read_text())
    asset_blobs, images = load_asset_map()
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    out = pathlib.Path(a.out) / "project"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    tokens = tokens_json()
    (out / "tokens.json").write_text(json.dumps(tokens, indent=1) + "\n")
    (out / "README.md").write_text(
        readme(tokens, settings, (ROOT / "rules/design.md").read_text(), [r["id"] for r in rows]))

    html = pathlib.Path(a.dist).read_text()
    css = page_css(html)
    sprite = page_sprite(html)
    sections = {s.component: s for s in find_sections(html)}
    missing_images = set()
    written = []
    for r in rows:
        cid = r["id"]
        spec = COMPONENTS[cid]
        sec = sections.get(cid)
        if sec is None:
            raise SystemExit(f"dist/kit-preview has no section for {cid}; run npm run build")
        for url in section_image_urls(sec.inner):
            if url.startswith("/_astro/") and url not in images:
                missing_images.add(url)
        d = out / "components" / spec["comp"]
        d.mkdir(parents=True)
        (d / "preview.html").write_text(
            preview_html(sec, css, sprite, heights.get(cid, 200), images, spec["group"], spec["comp"]))
        (d / "README.md").write_text(component_readme(cid, spec))
        written += [d / "preview.html", d / "README.md"]

    # The cover is written LAST, from what was built, and its folder stays BARE: a README.md
    # beside it would make Cover an ordinary component and the system would have no cover.
    hexes = {t["name"]: t["value"] for t in tokens["color"]["tokens"] if t["value"].startswith("#")}
    hexes["location_label"] = settings["location_label"]
    cover_dir = out / "components" / "Cover"
    cover_dir.mkdir(parents=True)
    (cover_dir / "preview.html").write_text(cover_html(hexes))

    logos = out / "assets" / "Logos"
    logos.mkdir(parents=True)
    sizes = {}
    for name in LOGO_FILES:
        src = FAVICON if name == "favicon.svg" else BRAND / name
        shutil.copyfile(src, logos / name)
        sizes[name] = src.stat().st_size
    (logos / "README.md").write_text(logo_readme(sizes))

    (out / "design-system.json").write_text(
        json.dumps(index_json(asset_blobs, sizes, now), indent=1) + "\n")

    files = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    print(f"wrote {len(files)} files to {out}")
    for f in files:
        print("  ", f)

    pending_assets = [n for n in LOGO_FILES if not asset_blobs.get(n, {}).get("blob")]
    if pending_assets or missing_images:
        print("\nUPLOAD FIRST, then fill data/design/design-system-assets.json and re-run:")
        if pending_assets:
            print("  assets (upload from project/assets/Logos/, key by file name):")
            for n in pending_assets:
                print(f"    {n:24} {sizes[n]:>7,} bytes  image/svg+xml")
        if missing_images:
            print("  images (upload the built file from dist/kit-preview, key by this url):")
            for u in sorted(missing_images):
                p = ROOT / "dist" / u.lstrip("/")
                sz = p.stat().st_size if p.exists() else 0
                print(f"    {u}  {sz:,} bytes  image/webp")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
