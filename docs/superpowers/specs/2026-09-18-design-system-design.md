# Design System and Component Variations — Design Spec

BlueStaffyUK rebuild, project 3 of 6. Date 2026-09-18. Branch `design-system`, cut from
`foundation` at `e049f55`. No remote; nothing is pushed.

Approved in the brainstorm on 2026-09-18 (visual companion for palette, type and mark; terminal
for scope, canvas mechanism and the prompt-pack replacement). Picks made there are locked facts
of this spec and are not re-opened during planning or execution.

## 1. Goal and scope

Project 3 produces the visual system that projects 4, 5 and 6 consume, without rewriting any
page content:

- design tokens (colour, type, space, radius, shadow, motion) as the single source of truth;
- one logo mark in four lockups;
- thirteen components, each built in five real variants, shown live on a published design canvas;
- the user's picks recorded as data and the non-picked variants deleted;
- a published Design System artifact carrying the tokens and the thirteen picked components, for
  every later design canvas to attach.

**Out of scope.** Page copy of any kind; the Glasgow → Carlisle change in content, settings and
schema (Known Issue 16, project 4); location pages, comparison cluster and blog posts (project
5); domain, phone, GSC, GA4, IndexNow (project 6). The Claude Design prompt pack named in the
original six-project plan is **replaced** by the Design System artifact (§7); no
`docs/design/prompt-pack.md` is written.

## 2. Locked design picks

| Decision | Pick | Alternatives shown |
|---|---|---|
| Palette | **A. Steel blue + brass**: steel `#1F3A52`, slate `#5B7C99`, brass `#C9A227`, bone `#F4F1EA`, ink `#1B2430` | coat slate; clay CTA on blue; dark premium |
| Type | **A. Fraunces** (display, H1–H6) + **Source Sans 3** (body, labels, buttons) | Newsreader + IBM Plex Sans (the ported rule); Bricolage Grotesque + Inter |
| Mark | **A. Line-drawn, front-facing Staffy head**, stroke-based, `currentColor` | brass monogram roundel; kennel-club shield; pure wordmark |
| Logo scope | **One mark, four lockups** (horizontal, stacked, icon, mono) | four competing concepts |
| Components | **The thirteen in §5** (twelve picked in the brainstorm plus the section divider added at spec approval) | twelve + comparison table + blog layout; a core of six |
| Canvas | **Published Design-type canvas + picks board with a shared database** | local browser screens only; both |
| Prompt pack | **Replaced by a Design System artifact** | one prompt per page type; per component; both |

Strapline under the wordmark: `Carlisle · Cumbria` (the breeder has relocated; Known Issue 16).
The wordmark is `BlueStaffyUK`.

## 3. Tokens

**File.** `src/styles/tokens.css`, a Tailwind 4 `@theme` block, imported first by
`src/styles/global.css`. The two tokens already in `global.css`'s `@theme` (`--color-ink`,
`--color-rule`) move into `tokens.css`; `global.css` keeps layout variables (`--hdr`,
`--container`, `--text-max`) and the base layer.

**Three layers, one file, in this order.**

1. *Primitive* — named by hue and step, never by use:
   `--color-steel-900 #14202B`, `--color-steel-700 #1F3A52`, `--color-steel-500 #5B7C99`,
   `--color-steel-300 #8FA3B8`, `--color-steel-100 #E4EAF1`; `--color-brass-600 #A8861C`,
   `--color-brass-500 #C9A227`, `--color-brass-200 #EFE3B4`; `--color-bone-100 #F4F1EA`,
   `--color-bone-50 #FAF8F3`, `--color-white #FFFFFF`; `--color-ink #1B2430`,
   `--color-ink-2 #46566B`, `--color-ink-3 #5E6B7A`; `--color-rule #DAD6CC`;
   `--color-ok #2F6B4F`, `--color-warn #9A4A2A`.
   `--font-display: "Fraunces", Georgia, serif`; `--font-body: "Source Sans 3", system-ui,
   sans-serif`. Type scale `--text-xs 13px` … `--text-4xl 44px` with matching line heights.
   Space scale `--space-1 4px` … `--space-12 96px`. Radius `--radius-sm 6px`, `--radius-md
   12px`, `--radius-lg 20px`, `--radius-pill 50px`. Shadow `--shadow-card 0 2px 8px
   rgba(20,32,43,.08), 0 8px 24px rgba(20,32,43,.06)`. Motion `--dur-fast 120ms`, `--dur-base
   200ms`, `--ease-out cubic-bezier(.2,.7,.2,1)`.
2. *Semantic* — named by role: `--color-surface` (bone-100), `--color-surface-raised`
   (white), `--color-surface-inverse` (steel-700), `--color-text` (ink), `--color-text-muted`
   (ink-3), `--color-text-on-inverse` (bone-100), `--color-brand` (steel-700),
   `--color-brand-soft` (steel-100), `--color-cta` (brass-500), `--color-cta-ink`
   (steel-900), `--color-cta-hover` (brass-600), `--color-link` (steel-700),
   `--color-link-on-inverse` (brass-200), `--color-border` (rule), `--color-focus`
   (brass-500).
3. *Component* — only where a component needs a named lever: `--btn-radius` (pill),
   `--btn-form-radius` (md), `--card-radius` (lg), `--card-border`, `--hdr-bg`,
   `--counter-bed` (bone-50), `--seam-gradient` (steel-700 → brass-500).

**Contrast is proven, not asserted.** `data/design/contrast.json` lists every text/background
pair the tokens allow (`[{"fg":"--color-cta-ink","bg":"--color-cta","size":"normal"}, …]`).
`tests/py/test_design_tokens.py` parses `tokens.css`, resolves each pair through the semantic
layer to a hex, computes the WCAG 2.x contrast ratio and fails under 4.5:1 for `normal` and
3:1 for `large`. It also asserts every semantic token resolves to a primitive that exists, no
hex literal appears outside the primitive layer, and `global.css` declares no `--color-*`.

**Rule update.** `rules/design.md` rule 1 (colours) and rule 2 (type) are rewritten to the
new palette and pairing; the Forest Green / Clay / Cream values and the Newsreader / IBM Plex
Sans pairing are removed, together with the `font-lora` / `font-sora` utility names. Rule 5's
warm shadow becomes the steel-brown tint. The `design-system-nine` row in
`data/quality/rule-index.json` moves from `untested` to `test`, backed by
`test_design_tokens.py`. `tests/py/test_rules_index.py` and the marker gate continue to
pass; the fact lint's banned-token list gains `#2D6A4F`, `#e8604c`, `Newsreader`, `IBM Plex`.

## 4. Logo

**Mark.** A front-facing Staffordshire Bull Terrier head with rose ears, drawn as stroke paths
(`stroke="currentColor"`, `stroke-width` 3 on a 64-unit grid, round joins and caps, no fills
except the eyes). Five variants go on the canvas (§6): (a) plain head, (b) head with collar
and brass tag, (c) head inside a thin roundel, (d) heavier 4-unit stroke, (e) head with a
subtle open-mouth expression. One is picked; the rest are deleted.

**Lockups**, all SVG in `public/brand/`, built by hand from the picked head and committed:

| File | Use | Contents |
|---|---|---|
| `logo-horizontal.svg` | site header, email signature | mark left, wordmark `BlueStaffyUK` in Fraunces 700 right, strapline `Carlisle · Cumbria` in Source Sans 3 600 caps under the wordmark |
| `logo-stacked.svg` | footer, social avatars, print | mark above centred wordmark and strapline |
| `logo-icon.svg` | favicon, app tile, watermark | mark only, on a steel-700 rounded square |
| `logo-mono.svg` | embroidery, single-colour print | horizontal lockup in one colour, `currentColor` |

Fonts inside the SVGs are converted to outlines (`<path>`), so the lockups render without the
web fonts. `logo-icon.svg` is rendered by `scripts/build_favicons.py` (Pillow + cairosvg) into
`public/favicon.svg`, `public/favicon-32.png`, `public/apple-touch-icon.png` (180) and
`public/icon-512.png`; the render is committed and the script is idempotent.

`data/settings.json` `logo` and `logo_header` point at `/brand/logo-stacked.svg` and
`/brand/logo-horizontal.svg`; `SiteHeader.astro` and `SiteFooter.astro` render the SVGs
inline (so `currentColor` works on the inverse header) with `<title>` and `aria-label`. The two
legacy raster logos are removed from `public/images/` and from `data/image-manifest.json`.

**Test.** `tests/py/test_brand_assets.py`: the four SVGs and four favicon files exist; each SVG
parses, carries a `<title>`, contains no `<text>` element and no `<image>`; `src/` references
no `.png`/`.webp` logo; `settings.json`'s two logo paths resolve to files.

## 5. The component kit

Thirteen components, each an Astro component in `src/components/kit/`, styled only with
tokens (a `test_design_tokens.py` case greps `src/components/kit/` for hex literals and fails
on any). During project 3 each takes a `variant` prop typed `'a'|'b'|'c'|'d'|'e'`; after the
picks are pulled (§6) the prop and the non-picked branches are removed, leaving thirteen
single-purpose components.

| # | Component | File | The five variants explore | Serves |
|---|---|---|---|---|
| 1 | Site header + nav | `SiteHeaderKit.astro` | inverse vs bone bar; centred vs left nav; CTA in bar or not; mobile drawer vs sheet | all pages; replaces `SiteHeader.astro` |
| 2 | Hero | `Hero.astro` | photo-right, photo-full-bleed, split with trust chips, text-only on inverse, short location hero | home, location, guide |
| 3 | Buttons | `Button.astro` | pill/brass, pill/outline, pill/inverse, form-radius submit, text link with arrow | everywhere |
| 4 | Puppy card | `PuppyCard.astro` | image ratio 4:5 vs 1:1; price badge position; status ribbon; sex/colour chips; hover lift | for-sale, home, location |
| 5 | Trust strip | `TrustStrip.astro` | icon row, three tiles, single line with dividers, inverse band, stacked list | home, for-sale, location |
| 6 | Stat / counter strip | `CounterStrip.astro` | tone-shift + rule, seam gradient bar, boxed tiles, inline with hero-edge, minimal | home, location; satisfies `layout-hero-counter-separation` |
| 7 | Content / info card | `InfoCard.astro` | steel header band, brass eyebrow, icon-led, image-top (H3 owns `.sec-img`), plain | guides, about |
| 8 | Testimonial | `Testimonial.astro` | quote card, inverse band with avatar, three-up grid, single large pull-quote, carousel-free stacked | home, for-sale |
| 9 | FAQ accordion | `Faq.astro` | native `<details>` styled five ways (plus-icon, chevron, numbered, bordered, divided) | guides, for-sale, location |
| 10 | Contact form | `ContactFormKit.astro` | single column, two column, stepped labels, inverse card, inline sidebar form | contact; replaces `ContactForm.astro` markup, keeps the Formspree action and the `FORM_ENDPOINT` contract |
| 11 | Breadcrumb + in-page nav | `PageNav.astro` | breadcrumb only, breadcrumb + sticky ToC, chip row, sidebar ToC, jump-bar | guides, location |
| 12 | Footer | `SiteFooterKit.astro` | four-column, three-column with stacked logo, slim single row, inverse with CTA band, sitemap-style | all pages; replaces `SiteFooter.astro` |
| 13 | Section divider | `SectionDivider.astro` | mark centred on a rule, two brass rules with the stacked lockup between them, mark-only with fading rule, seam gradient bar with the icon in a bone medallion, slim rule with the icon at the left margin | between sections on every page; the mark is the picked head (§4), so the divider variants render with head variant (a) until the pick and are regenerated after it |

Each variant is a distinct layout, not a colour swap; a variant that differs from a sibling
only in tokens is rejected in review. Copy inside the kit is placeholder-free real copy from
`data/puppies.json`, `data/settings.json` (excluding `address`, which is Glasgow until project 4
— the kit shows `Carlisle · Cumbria` from a new `data/settings.json` key `location_label`
added in this project) and the existing pages; no invented claims, prices or reviews. Where a
component needs a review and none exists in the repo, the slot reads `REVIEW_PLACEHOLDER`,
a sixth token added to `scripts/placeholder_check.py` so the gate counts it and refuses to
ship it.

**Images.** `PuppyCard.astro` and `Hero.astro` use `astro:assets` `<Image>` with widths
`[400, 800, 1200]` and `sizes`, sourced from `src/assets/puppies/` (moved from
`public/images/` for the six puppies and the hero images). This closes Known Issue 4: the
puppy `srcset` 2x blocking rows must reach 0 in the render harness.

**The kit renders on one route.** `src/pages/design-canvas/index.astro` renders every
component in every variant under `<section data-component="hero" data-variant="c">` with
`noindex`, is excluded from the sitemaps by the existing noindex rule in
`scripts/sitemap_check.py`, and is removed at the end of the project together with the
variant prop. It is the only place the kit is mounted during project 3; existing pages are not
touched (project 4 adopts the picked components).

## 6. Canvas and picks

**Canvas.** The Design-type artifact created during the brainstorm,
`https://claude.ai/artifact/TAc7sSMqtcANRq9ujEQ5uR`, title *BlueStaffyUK Design Canvas*. It
is filled, never re-created. `scripts/build_design_canvas.py`:

1. reads `dist/design-canvas/index.html` after `npm run build`;
2. for each `[data-component][data-variant]` section, writes one artboard
   `docs/artifacts/canvas/project/<component>-<variant>.dc.html`: a self-contained page with
   the section's HTML inside `<x-dc>`, the built CSS for that section inlined into
   `<helmet><style>` (the compiled Tailwind output filtered to selectors the section uses),
   the Google Fonts `<link>` for Fraunces and Source Sans 3, the `support.js` head line, and a
   `data-props` block with `$preview` equal to the board size (1280 wide for header, hero,
   strips, footer; 640 for cards, buttons, form, FAQ, nav; height measured by Playwright at
   build time and rounded up to 8);
3. images referenced by the section are uploaded as canvas assets once and the returned
   `/_blob/` URLs substituted (`data/design/canvas-assets.json` maps source path → blob URL so
   re-runs reuse uploads);
4. writes `project/canvas.json`: thirteen rows, five boards per row 80 px apart, rows 120 px
   apart, one `title1` note per row (`1 · Site header`, …), `order` back to front, `launch`
   `{"view":"canvas"}`, `createdOnFiles` carried over from the existing index if present;
5. prints the file list. The controller publishes with the Artifact tool (`url`, `root`,
   `file_path` = `canvas.json`, `files` = the sixty-five artboards); the script never calls the
   network itself except for step 3, which the controller also performs.

The `<x-dc>` markup keeps the kit's real `<button>`, `<a href>`, `<input>` + `<label>`
elements; a `<details>` FAQ is marked `is_interactive: true`. No emoji, no `<iframe>`, no
scripts other than the required `data-dc-script` class.

**Picks board.** `docs/artifacts/design-picks.html`, a plain published Artifact with the
shared-database capability, built by `scripts/build_picks_board.py` from the same section
list: thirteen rows, each with the component name, a link to its canvas row, five pick buttons
`a`–`e`, a note field and a "Save" that writes `{component, variant, note, at, by}` to the
database key `picks/<component>`. The board shows the saved state on load. It is the same
mechanism as `data/boards/index.json`'s Artifact from project 2, with the `db` rules copied.

**Pull.** `scripts/pull_design_picks.py` takes the thirteen `picks/*` rows (the controller reads
them with the ArtifactData tool and passes the JSON on stdin, the same way the project 2 board
approval was pulled) and writes `data/design/picks.json`:

```json
{"pulled_at": "2026-09-19T10:00:00Z", "picks": {"site-header": {"variant": "c", "note": "…"}, …}}
```

`tests/py/test_design_picks.py`: the file has exactly the thirteen component ids of §5, every
variant is one of `a`–`e`, and after the prune step (§8, task order) every picked variant
file's component still exists and no `variant=` prop remains in `src/components/kit/`. Until
`picks.json` exists the test is skipped with a reason naming this spec, so the suite stays
green between the canvas publish and the picks.

## 7. Design System artifact

Created from the *Design System* artifact type
(`https://claude.ai/artifact/5M7UeXXcx16TP3vzVFNDzd`) once, titled *BlueStaffyUK Design
System*, and recorded in `data/design/artifacts.json` with the canvas and picks-board URLs.
`scripts/build_design_system.py` generates its content from `tokens.css`, `picks.json` and
`public/brand/`:

- `project/tokens.json` — the primitive and semantic layers, in the type's token shape (read
  from the type's own instructions at build time; the plan's first task is to create the
  artifact and read them, and to adjust this section's file list if the type differs);
- `project/README.md` — palette, type, spacing, radius, shadow, the nine design rules in
  their rewritten form, the locked facts (breeder, Carlisle, prices, placeholders that must
  stay placeholders), and a "Consuming this system" section naming the namespace `bsuk`;
- one reference board per picked component, as `.dc.html` files re-used from the canvas
  build (only the picked variant of each), plus the four logo lockups as assets.

Because everything is generated from repo data, the artifact cannot drift from the tokens; a
re-run after a token change republishes it. This artifact **replaces the Claude Design prompt
pack**: project 4 creates one Design canvas per page type with `bsuk` attached, so page
mockups are drawn from the picked components rather than described in prose.

## 8. Order of work, in outline

Easier first, each step committed:

1. Tokens + contrast test + rule rewrite (§3).
2. Kit components with five variants each, in the order of §5's table, each with its own
   render-harness fixture pair (`known_good` / `known_broken`) so `sem-heading-order`,
   `layout-tap-target-size` and `a11y-text-contrast-aa` measure it.
3. The `/design-canvas/` route, the five head variants as an inline-SVG artboard, the canvas
   builder, publish, the picks board, publish.
4. **User picks** (pause point — the only one in the project).
5. Pull picks, prune variants, produce the four lockups and favicons from the picked head,
   rewire header and footer to the new logo files.
6. Promote the three deferred harness checks (`layout-hero-counter-separation`,
   `layout-h3-image-first`, `sem-statement-label-visible`) by giving the kit the conventions
   they measure; remove their `deferred_checks` entries.
7. Design System artifact, gate report, Artifacts, session-closer.

## 9. Definition of done

1. `npm run check:all` green twice; marker gate `0 problems`; the placeholder total does not
   rise except for `REVIEW_PLACEHOLDER` slots, which are listed in the gate report (§5).
2. `npm run test:py` green twice, including `test_design_tokens.py`, `test_brand_assets.py`
   and `test_design_picks.py` (not skipped).
3. `npm run test:render:meta` green; the three deferred checks are promoted and Guard 2 prints
   no `DEFERRED` line; `npm run test:render:pages` at a new recorded baseline
   `docs/reports/render-baseline-project3.md` with **no new blocking row** and the `IMG`
   family's `img-srcset-within-2x` at 0.
4. `data/design/picks.json` holds thirteen picks; `src/components/kit/` has thirteen components and
   no `variant` prop; the `/design-canvas/` route is gone.
5. `public/brand/` holds the four lockups and the four favicon renders; header and footer
   render the SVG logo.
6. The three Artifacts are published and their URLs recorded in `data/design/artifacts.json`:
   the canvas (sixty-five artboards), the picks board, the Design System.
7. Lighthouse warm median of 3 on the five Foundation page types: no category score below
   the Foundation baseline (99/100/100/100 home; 99/100/100/92 for-sale; 98/100/100/100
   puppy; 100/100/100/92 location; 100/100/100/100 blog). Recorded, not a gate.
8. `docs/reports/design-system-gate-report.md` written and published as an Artifact; this
   spec and the plan published as Artifacts via `scripts/build_spec_artifact.py`.
9. Every commit carries `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
10. Session-closer summary names project 4 as next and lists any new open flags appended to
    `docs/reference/session-log.md` Known Issues.

## 10. Risks and their answers

- *The Design type's artboard format rejects the compiled CSS.* Artboards inline the filtered
  CSS in `<helmet><style>`; the format allows a stylesheet there. If a selector form is
  refused, the builder falls back to inlining computed styles per element (Playwright
  `getComputedStyle`), which the type edits natively. Decided at task time; the fallback is
  in the plan, not improvised.
- *Sixty-five uploads of the same images.* The asset map in `data/design/canvas-assets.json`
  de-duplicates; the six puppy images and three hero images are the whole set.
- *Picks arrive over several sessions.* The board persists in its database; the pull script is
  idempotent and the test skips until all thirteen are present.
- *The kit's contact form must not break the form contract.* `ContactFormKit.astro` keeps the
  field names, the `action` from `PUBLIC_FORMSPREE_ID` and the honeypot;
  `scripts/form_contract_audit.py` runs in `check:all` and must stay at 0 problems.

## 11. Amendments

Recorded here as they happen during planning and execution, in the same way as the project 2
spec's §11.

1. **2026-09-18, at spec approval.** Component 13, *Section divider*, added to §5 at the user's request: dividers built around the logo mark (a centred mark on a rule, in the style of the source site's parrot divider), five variants like every other component. Counts throughout the spec move from twelve to thirteen components and from sixty to sixty-five artboards.

2. **2026-09-18, during Task 13.** *The kit's contact form is audited as a form, not as five pages.* `scripts/form_contract_audit.py` routes a page to a field contract by `data/page-map.json` `kind`, falling back to a slug heuristic; `design-canvas` is in neither, so the five `ContactFormKit` layouts on the hidden canvas route were falling to the `full` contract and being judged as five separate enquiry pages. They are five specimens of one form, on a `noindex` route no visitor reaches and that Task 19 deletes. The route is therefore named in a new `NON_CONTENT_ROUTES` tuple and excluded from the per-page FIELD contract only — the endpoint, `POST` and netlify-residue checks still apply to every specimen, so a form posting anywhere but the one Formspree endpoint is still a failure — with one documented exception added in the Task 15 review: on those routes the local `#contact` stub is also allowed, and the canvas registry passes it deliberately, because five live endpoints on one page is five ways for a stray click to send a real enquiry. The exclusion also expires by test: every name in `NON_CONTENT_ROUTES` must exist as `src/pages/<name>/`, so Task 19 cannot delete the canvas route without deleting the exemption. The field contract itself is not weakened: `ContactFormKit` carries all six named controls with the built page's required set, the `_gotcha` honeypot and the hidden `_next`/`_subject` in every variant, and `tests/py/test_design_components.py::test_built_contact_form_variants_all_keep_the_whole_form_contract` asserts that in dist for all five. It differs from `ContactForm.astro` in one place: its `puppy` select is built from `data/puppies.json` availability plus a waiting-list choice, and it carries no collection option naming the breeder's former city (Known Issue 16). When project 4 mounts this component on the contact page, that page is a content page and the full audit applies to it as it does today.
