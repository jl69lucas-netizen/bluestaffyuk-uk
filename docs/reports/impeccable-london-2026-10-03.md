# impeccable Harden pass: London (2026-10-03)

Page: `/uk-locations/blue-staffy-puppies-london/` (`src/pages/uk-locations/blue-staffy-puppies-london.astro`),
`docs/reference/page-run.md` row 14. The controller invoked `impeccable:impeccable` with the Skill tool; this
pass follows its `SKILL.md` (shared laws, absolute bans), `reference/brand.md` (brand register),
`reference/audit.md` and `reference/polish.md`.

**Setup gate.** As in every earlier pass (`docs/research/london-components/hardening-log.md`), the loader's
`PRODUCT.md` gate is unmet: no such file exists and only `/impeccable teach` with the user may write one. The
brand context came from the `design-context-read-first` files (foundation spec, `data/settings.json`,
`rules/design.md`, `src/styles/global.css`, `src/styles/tokens.css`). Fraunces is a locked token
(`rules/design.md` rule 2) and the palette never changes.

**Visual layer only.** No text, heading, link, image choice or section order changed; the approved board is
untouched. One finding came from the controller mid-pass (the render gate's `img-srcset-within-2x`), and is
fixed here (F9).

**How it was assessed.**
1. Deterministic detector: `npx impeccable --json dist/uk-locations/blue-staffy-puppies-london/index.html`
   after `npm run -s build` (24 rows).
2. Design review of real screenshots from a painting browser (Chromium through Playwright, device scale 1):
   full page plus viewport shots scrolled through the page at 375 (52 shots), 768 (37) and 1280 (44), read
   as contact sheets.
3. A measuring pass in the same browser at 375 / 768 / 1280: contrast of every painted text node against
   its effective background (555 / 575 / 567 text elements), every interactive target's box (125 / 138 /
   127), document width against the viewport, a Tab walk recording each focus ring (117 / 129 / 118 stops),
   heading sizes and line counts, text under 14px, and every image's decoded width against its painted width
   (also at 1024).

Screens: `docs/reports/screens/impeccable-london/` (before / after pairs of the changed pieces at each width,
`pair-<piece>-<width>.png`, and the top viewport before and after). Previews of the deferred changes:
`docs/reports/impeccable-london/`.

## Detector rows

| Rows | Antipattern | Verdict | Reason |
|---|---|---|---|
| 0 | `side-tab` `border-top: 4px` | dismissed | `CityTakeawaysLedger`'s full-bleed 4px steel rule on the section root, which has no radius (the same false positive as Plan 2 Task 4). |
| 1–10 | `side-tab` `border-left: 3px + border-radius: 12px` | **verified, fixed (F1)** | `CityPlacesByPublisher` `.place`: a 3px brass side stripe on each London place card, an absolute ban. |
| 11–14 | `low-contrast` 4.49:1, `#5e6b7a` on `#e4eaf1` | **verified, fixed (F2)** | The "Rules set by" label, `--color-ink-3` on the steel-100 tray (measured 4.49:1 at all three widths). |
| 15–16 | `all-caps-body` (32 and 41 characters) | dismissed | The hero eyebrow "Six puppies · Carlisle to London" and the ticket strip's "Our six puppies · each opens its own page": short labels, which `brand.md` reserves caps for, not body passages. |
| 17–19 | `cramped-padding` on `div.list` | dismissed | `CityFaqLedger`'s `.list` carries the top rule; its rows are `<details>` whose `<summary>` has `--space-3` padding. The known inner-wrapper false positive. |
| 20 | `clipped-overflow-container` on `html` | dismissed | The site's `overflow-x: clip` on `html` (every page). |
| 21 | `overused-font` Fraunces | recorded, not acted on | Locked display token (rule 2). |
| 22 | `flat-type-hierarchy` (h2 13px, h4–h6 16px) | partly verified | The 13px "h2"s are the site footer's column labels (chrome, label role). The H4–H6 part is real: in `CityChapters` they had no rule of their own and sat on the body's size and 1.65 leading. The leading is fixed (F6); weight and colour are a design change, deferred (D2). |
| 23 | `side-tab` inset box-shadow 3px stripe on `.city-scale` | dismissed | The counter bed's full-width 3px steel top rule, which `layout-hero-counter-separation` requires. |

## Audit health score

| # | Dimension | Before | After | Key finding |
|---|---|---|---|---|
| 1 | Accessibility | 2 | 3 | One AA contrast failure, 14 standalone links with 21–24px targets, and the dial/stepper announcing the wrong `aria-current` after a scroll back up; all fixed. Site chrome targets under 44px remain (D3). |
| 2 | Performance | 2 | 3 | 21 images decoded at 2.0–2.9x their box across 375–1280; 0 now. Smaller masters still paint upscaled (advisory `img-not-upscaled`, pre-existing, needs larger masters at the image step). |
| 3 | Responsive design | 3 | 3 | No horizontal scroll at any width (document width = viewport), tables stack, every focus stop draws a ring. The chapter rows leave tall empty bays from 1024 (D1); phone infographics shrink their labels to illegible (D4). |
| 4 | Theming | 3 | 3 | Tokens throughout; one component set five type sizes in px off the scale (fixed). Light only, by the brand's design (no dark tokens in `tokens.css`). |
| 5 | Anti-patterns | 3 | 3 | One absolute ban (the places side stripe), fixed. No gradient text, glass, nested cards or hero-metric template; Fraunces is the reflex-list face, kept as a locked token. |
| **Total** | | **13/20** (Acceptable) | **15/20** (Good) | |

**Anti-patterns verdict.** Pass, with one tell removed. The page reads as one designed system (steel band,
brass CTA, bone ground, numbered chapters, ruled ledgers) rather than a template; the side-striped place
cards were the one AI-UI reflex on it. The display face is the reflex-list Fraunces, which the brand has
locked.

## Findings

13 findings: 9 fixed, 4 deferred. Severity per `audit.md`.

| # | Sev | Finding | Location | Widths | Outcome |
|---|---|---|---|---|---|
| F1 | P1 | 3px brass `border-left` on 12px-radius place cards (absolute ban: side stripe) | `src/components/kit/CityPlacesByPublisher.astro` `.place` | all | **fixed 693c67f2**: a whole 1px `--color-border` hairline |
| F2 | P1 | "Rules set by" label at 4.49:1 (`--color-ink-3` on steel-100), WCAG 1.4.3 | `CityPlacesByPublisher.astro` `.owner-k` | all | **fixed 693c67f2**: `--color-ink-2`, 6.18:1; the pair is registered in `data/design/contrast.json` (rule 1) |
| F3 | P2 | 11px chips and label, 12.5px place line, 14.5px facts: off the type scale and under the kit's 13px floor (type fits every tier) | `CityPlacesByPublisher.astro` | all | **fixed 693c67f2**: `--text-xs` / `--text-sm` |
| F4 | P2 | Seven standalone source links in the London places, 21px tall | `CityPlacesByPublisher.astro` `.owner a` | all | **fixed 693c67f2**: each link a 44px row |
| F5 | P2 | Six in-page "more" links under the FAQ answers, 22–24px tall | `src/components/kit/CityFaqLedger.astro` `p.more a` | all | **fixed 693c67f2**: 44px hit area, padding given back by a negative margin (no layout change) |
| F6 | P2 | H4–H6 in chapters on the body's 1.65 leading: a three-line question read as loose as prose | `src/components/kit/CityChapters.astro` | all | **fixed 1280f625**: leading 1.3, balanced lines |
| F7 | P3 | Hero CTA label wraps unbalanced on a phone ("…available / now") with no vertical padding in the pill | `src/components/kit/CityHeroFilmstrip.astro` `.cta` | 375 | **fixed 693c67f2**: balanced, centred, `--space-2` block padding |
| F8 | P2 | After scrolling to a later section and back above the first stop, the dial and stepper kept that stop current ("Staffy, pit bull or AmStaff" while reading the takeaways); a fresh load marks the first | `src/lib/scrollSpy.ts` | all | **fixed 693c67f2**: above the first section the first row is current; probed fresh, after a jump to Breed and back, and at the top |
| F9 | P1 | 21 images decoded at 2.0–2.9x their painted width (render gate `img-srcset-within-2x`: 9 at 375, 9 at 768; the sweep found more at 1024 and 1280): every infographic's tall phone file and wide file, eleven chapter photos, the Ince card, the FAQ rail photo, Victoria's letter photo, three H4 photos on the uniform 100vw `sizes` | page, `BodyImage.astro`, `CityChapters.astro`, `CityLetter.astro`, `src/lib/cityKit.ts`, `data/image-focus.json`, `public/images/` | 375 768 1024 1280 | **fixed 1280f625**: 35 width siblings added BESIDE the served masters (working rule 11: no master renamed, re-encoded or replaced), `phone.srcset` on the art-directed source, and `sizes` measured to the boxes. 0 oversized at all four widths; the filtered render gate passes 3/3 |
| D1 | P2 | From a 1024px viewport the chapter rows put heading, photo and prose in three columns; the prose column (with its H4 ladder) runs two to three times the height of the other two, leaving tall empty bays under the heading and photo | `CityChapters.astro`, every chapter with an H4 ladder | 1024 1280 | **deferred**: a layout change (working rule 6). Preview: heading and photo ride along with the prose (`position: sticky`), `docs/reports/impeccable-london/D1-chapter-bay-1280-before.png` / `-preview.png` |
| D2 | P3 | H4–H6 in chapters are Fraunces 400 in body ink, where the site's H4 convention (`board-styles.css`) is 700 in `--color-brand`; on a phone the H4 reads lighter than the prose around it | `CityChapters.astro` | all | **deferred**: a weight and colour-role change. Preview at 600 / `--color-brand`: `D2-h4-weight-{375,1280}-before.png` / `-preview.png` |
| D3 | P3 | Site chrome targets under 44px: header brand 40×40, breadcrumb links 31px tall (the deliberate `.tap-24` class), footer "Home" / "Blog" / "X" 29–43px wide; all pass WCAG 2.5.8 AA (24px) | `SiteHeaderKit.astro`, `Breadcrumb.astro`, `SiteFooterKit.astro` | all | **deferred**: shared chrome on every built page; a change there repaints all of them and is previewed first (the precedent in hardening-log Plan 2 close, row 5). Preview (targets outlined): `D3-chrome-targets-375.png`, `D3-chrome-footer-targets-375.png` |
| D4 | P2 | On a phone the six infographics paint their tall `-760` layout at 319px, about 0.42x, and the labels inside them shrink to roughly 5–7px; the prose beside each carries the same facts | the six approved infographic files | 375 | **deferred**: an asset change (a phone layout drawn at a larger type size), which goes back through the board's image slots and the Asset Gate. Preview: `D4-infographic-phone-375.png` |

### Deferred: applied (2026-10-04)

D1 (as the breeder directed), D2 and D3 were applied after the breeder's answers (answer board batch `2026-10-03-london-harden-decisions`; D4 went to the infographic pipeline separately), together with the six changes the frontend-design pass deferred (batch `2026-10-03-london-design-pass-decisions`, all (a)):

| Change | Breeder's answer | Commit(s) | What shipped |
|---|---|---|---|
| D1 (impeccable) | harden q02: no to sticky; "the text or paragraphs go under the image/header ... no long/tall, empty space" | `0f5a10ad` | From a 640px box each chapter opens on one row, numeral and H3 beside the photo (centred on it), and the prose with its H4–H6 ladder runs the full chapter width UNDER that row at 65ch. Measured bay beside the prose: 761px / 983px at 768 / 1280 before, none after (the largest gap left is 47–53px between a centred heading and its photo's foot). Phones unchanged. |
| D2 (impeccable) | harden q03: yes | `0f5a10ad` | The chapter ladder (the slots' own H4–H6) at 600 in `--color-brand`; F6's 1.3 leading kept. |
| D3 (impeccable) | harden q04: yes, every page | `7bacef15`, fix `d1794e82` | Header brand link 44×44; every crumb link 44px tall and ≥44px wide (8px padding cancelled by an 8px negative margin, so the › keeps 8px each side: a plain `min-width` failed `nav-breadcrumb-separator-spaced` on six pages, caught by the full render gate and fixed); `SiteFooterKit` and the legacy `SiteFooter` links ≥44×44. Measured at 375 on London, health, the locations hub and /search/: 0 chrome links under 44. |
| Site-wide link underline | design-pass q01: yes, every page | `cf3dabf8` | London's F1 rule moved from `city.css` to `global.css`: links in body p / li / dd / td / figcaption / blockquote in `<main>` (not nav, kit components or the city kit) are underlined; London unchanged, home 28 links, health 15, contact 9, the locations hub 28 newly underlined. |
| D9 (frontend-design) | design-pass q02: yes | `7bacef15` (legal row), `cf3dabf8` (form link) | Footer legal row `align-items: center`; the contact form's privacy link takes the shared underline and hover. |
| D5 (frontend-design) | design-pass q03: yes | `458007c9` | `SectionDivider hairline`: a 1px steel-300 rule on the six seams between two chapter bands; the seal stays at the twelve turns. |
| D6 (frontend-design) | design-pass q04: yes | `1f056581` | The six filmstrip photos fade in and rise 8px once, 200ms each, 60ms stagger, transform and opacity only, inside `prefers-reduced-motion: no-preference`. |
| D7 (frontend-design) | design-pass q05: yes, add the smaller copy | `458007c9`, fix `d8ef6e2b` | `-240` / `-400` siblings ADDED beside `kc-registered-staffy-puppies.webp` (master untouched); the tray's inset is 16px / 32px; the chapter `sizes` follow (311 / 640 / 704px at 375 / 768 / 1280). The portrait then takes the text's `sizes` instead of the tall box's 230vw (`img-srcset-within-2x` caught 2.77x at 375 and 768 in the full gate; fixed). |
| D8 (frontend-design) | design-pass q06: yes | `458007c9` | The contact graphic (deposit chapter 1) and the breed comparison (breed H2) shown whole, `object-fit: contain` on bone-50, on London only. |

Screens, before and after at 375 / 768 / 1280 (D6 as 0 / 150 / 300 / 500ms frames): `docs/reports/screens/harden-d1-d3/` (`302af9eb`).

Verification, after `d8ef6e2b`, on a fresh build (63 built pages): `npm run -s test:render:pages` exit 0, 63 passed (21 pages × 375 / 768 / 1280; scorecards written, 218 advisory rows across 21 pages); `python3 -m pytest tests/py/test_london_page.py -q` 21 passed; `python3 scripts/board_gate.py blue-staffy-puppies-london` 0 FAIL, 31 WARN (22 sections, 93 headings, 35 assets examined); `npm run -s check:all` exit 0 (board gate --all 13 rebuilt pages, 0 failed). The city-kit spec (`tests/render/city-kit.config.ts`, not in the chain) fails the same 9 of 34 tests before and after on its pre-existing rows (section heights, `.tk-go` contrast, specimen sections missing); its chapter layout facts now follow the new layout and pass (the 45 chapter-layout rows it reported before are gone).

### Measured and dismissed (not counted)

- `span.tk-go` arrows in the ticket strip at 4.39:1: `aria-hidden="true"` and decorative, so the 3:1
  non-text threshold applies, which they pass.
- Checklist checkboxes 20×20: each sits inside a `<label>` that spans its whole row (well over 44px), and the
  label is the target. Form labels at 25px tall: the input below each is the target (46px).
- The jump stepper's ten stops at 36×44 on a phone: WCAG 2.5.5's equivalent-control exception applies. The
  "All 10 sections" key (359×44) opens the sheet, where every section is a 343×52–68 row.
- Honeypot inputs, the skip link and the stacked table head off screen: intentional.
- The em dash in the review-middle quote: Rachel L.'s words from `data/reviews.json`, page copy kept word for
  word.
- `img-not-upscaled` (advisory): masters smaller than their uniform box (for example the 400px London owner
  photo in a 744px box). This was there before the pass, is unchanged by it, and needs larger masters added
  beside the served files at the page's image step (Plan 2 close, row 2).

## Positive findings

- No horizontal scroll at any width; every table stacks into labelled rows below 640px (rule 13).
- 117–129 focus stops per width, every one drawing a ring; the sheet traps focus and Escape closes it.
- Images: 61, every one with `width` / `height` (each reserves its box before it loads), 55 lazy, one
  `fetchpriority="high"`.
- Every colour is a token; motion respects `prefers-reduced-motion`.
- The hero puts its photographs first on a phone, the hero and counter strip are separated by a tone shift
  and a rule, and every H3 opens with its image.

## Verification

Run after the fix commits (`693c67f2`, `1280f625`) and the screens commit (`390a65a3`), in sequence (each
finished before the next started):

| Command | Exit | Examined |
|---|---|---|
| `npm run -s build` | 0 | 63 built pages |
| `python3 -m pytest tests/py/test_london_page.py -q` | 0 | 21 passed |
| `python3 scripts/board_gate.py blue-staffy-puppies-london` | 0 | 22 sections, 93 headings, 51 live pages, 79 entity refs, 35 assets; 0 FAIL, 31 WARN (the board's own keyword and entity advisories, unchanged by this pass) |
| `npm run -s check:all` | 0 | every gate in the chain 0 problems (e.g. board gate --all 13 rebuilt pages, 0 failed; sitemaps 63 built pages; redirects 2759 internal refs; city canvas 45 fragments) |
| `npx playwright test -c tests/render/playwright.config.ts pages.spec.ts -g "blue-staffy-puppies-london"` | 0 (3 passed) | `img-srcset-within-2x`: no row at 375, 768 or 1280 |
| `python3 -m pytest tests/py -q` | 0 with one deselect | 7538 passed. The deselected `test_render_baseline.py::test_the_committed_report_matches_the_real_scorecards` fails on `docs/reports/render-baseline-project4.md` being stale; its inputs (`tests/render/`, `data/boards/`, `data/quality/`, the script) are byte-identical between `8c3f6f31` (before this pass) and HEAD, so the staleness predates the pass. |

The pass is recorded in `data/page-runs/blue-staffy-puppies-london.json` (`impeccable`: 375 / 768 / 1280,
13 findings, 9 fixed, 4 deferred with the reasons above).
