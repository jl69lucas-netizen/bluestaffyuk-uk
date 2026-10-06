# impeccable Harden pass: London, third run (2026-10-06)

Page: `/uk-locations/blue-staffy-puppies-london/` (`src/pages/uk-locations/blue-staffy-puppies-london.astro`),
`docs/reference/page-run.md` row 14. Re-run because the page changed after the 2026-10-05 passes: the London
map (`src/components/kit/CityMapFacade.astro`, C20, delivery answer 3; answer board 2026-10-06-london-map q01 (a)
P1, q02 (a) S1; commit `0b6cd04e`) and the five Harden calls the breeder approved on 2026-10-06 (answer board
2026-10-06-london-harden-calls q01-q05: the close card's steel outline, the hidden lead comma, 14px phone notes,
the one-row phone header, the puppy cards two across). This pass looked at those first and at the rest of the
page again.

The `impeccable:impeccable` skill was invoked with the Skill tool (args: audit and polish the built London page
at 375 / 768 / 1280; BSUK design system fixed; content and the approved board unchanged; visual layer only). It
follows the skill's `SKILL.md` (shared laws, absolute bans), `reference/brand.md`, `reference/audit.md` and
`reference/polish.md`.

**Setup gate.** `load-context.mjs` returns `hasProduct: false, hasDesign: false`, as in every earlier pass.
PRODUCT.md is written only by `/impeccable teach` with the user, so it was not synthesised. The brand context
came from the repo's own design sources (`rules/design.md`, `IMAGE-DESIGNS.md`, `src/styles/tokens.css`,
`src/styles/city.css`, `data/settings.json`). Fraunces is a locked token (`rules/design.md` rule 2), so the
reflex-reject list is recorded, not acted on. The palette never changes.

**Visual layer only.** No word, heading, link target, image or section order changed, and nothing the breeder
approved was repainted. The one fix adds a focus ring that only a keyboard user sees, after a keyboard tap on
the map. Nothing in this pass needed the breeder, so there are no proposals.

## How it was assessed

1. `npm run -s build`, `dist/` served on 127.0.0.1, Chromium through Playwright (device scale 1). Every request
   to a host other than the site's own was answered locally, so the pass never depended on Google.
2. Detector: `npx impeccable detect --json dist/uk-locations/blue-staffy-puppies-london/index.html` (9 rows).
3. Design review of real screenshots: full-page captures at 375, 768 and 1280 read as contact sheets, and
   element shots of the map in each state (facade, button focus, hover, loaded, keyboard-loaded).
4. A measuring probe at each width: contrast of every painted text element against its effective background
   (668 / 672 / 677 elements), every interactive target's box (136 / 141 / 130), document width against the
   viewport, every element's right edge, a full Tab walk recording each stop's ring (113 / 125 / 114 stops),
   reading text under 14px, side borders over 1px, every money range or " · " split across lines, heading
   sizes, layout shift (PerformanceObserver through load and a full scroll), console errors, requests to any
   other host before the map is tapped, and the delivery answer's height before and after the tap.
5. The phone header's drawer opened at 375, to check the menu panel the edge probe reported.

Before / after pairs of the fix and the map in its states: `docs/reports/screens/impeccable-london-2026-10-06/`.

## Detector rows

| Rows | Antipattern | Verdict | Reason |
|---|---|---|---|
| 0 | `side-tab` `border-top: 4px` | dismissed | `CityTakeawaysLedger`'s full-bleed steel rule on a radius-0 root (the known false positive). |
| 1–2 | `all-caps-body` (32 and 41 characters) | dismissed | The hero eyebrow and the ticket band's label: short labels, which `brand.md` reserves caps for. |
| 3–5 | `cramped-padding` on `div.list` | dismissed | `CityFaqLedger`'s ruled list; its `<summary>` rows carry the padding (known false positive). |
| 6 | `clipped-overflow-container` on `html` | dismissed | The site's `overflow-x: clip` on `html`. |
| 7 | `overused-font` Fraunces | recorded, not acted on | Locked display token (rule 2). |
| 8 | `side-tab` inset 3px stripe on `.city-scale` | dismissed | The counter bed's full-width top rule that `layout-hero-counter-separation` requires. |

The four close-card `side-tab` rows of 2026-10-05 (D1) are gone: the steel outline the breeder approved (q01)
replaced the brass left rule. The map adds no detector row.

## Audit health score

| # | Dimension | Score | Key finding |
|---|---|---|---|
| 1 | Accessibility | 4 | 0 contrast failures at any width; every one of 113 / 125 / 114 Tab stops draws a ring; the map's button is a real 44px `<button>`. One gap: after a keyboard tap, focus sat in the map with no ring (fixed, F1). |
| 2 | Performance | 3 | CLS 0.0000 through load and a full scroll at every width; 0 console errors; 0 requests to another host before the map is tapped, so the map costs no third-party script or cookie at load. Five H2 photos still paint upscaled from 400–550px masters (pre-existing advisory). |
| 3 | Responsive design | 4 | Document width = viewport at 375 / 768 / 1280; the map's box is 311×233, 640×300 and 704×300, and the tap changes the answer's height by 0px. The delivery answer is 1,697px at 375 (cap 2,030) and 1,199px at 1280 (cap 1,280), the preview's figures. |
| 4 | Theming | 4 | Every colour in the map is a token already paired in `data/design/contrast.json`; the fix uses `--color-focus`. |
| 5 | Anti-patterns | 3 | No new tell. The map facade is drawn from tokens (contour motif, brass pin), not a stock map tile. Fraunces stays locked. |
| **Total** | | **18/20** | **Excellent** |

**Anti-patterns verdict.** It does not read as AI-made. The map is the page's own: the steel panel and brass
pin of the ledger, the city's name in the display face, one CTA pill. The Harden calls removed the one tell the
last pass found (the close card's side stripe).

## Findings

1 finding: 1 fixed, 0 deferred. Severity: P1 blocks a reader, P2 a visible flaw, P3 polish.

| # | Sev | Finding | Location | Widths | Outcome |
|---|---|---|---|---|---|
| F1 | P2 | After a keyboard tap on "Show the map", focus moves into the map's iframe (the component does this on purpose, so the reader is not sent back to the top), but Chrome draws no ring on an iframe focused from script: `:focus-visible` false, outline `none`. A keyboard reader could not see where focus was (WCAG 2.4.7). Measured at 375 and 1280 | `CityMapFacade.astro` (script and `.stage.live`) | 375 768 1280 | **fixed**: a keyboard activation (a click with `detail` 0) marks the figure `data-kbd`, and the live box draws a 3px `--color-focus` ring, offset 3px, while the map holds focus. A mouse tap draws none, so the approved look after a tap is unchanged. Render test added to `tests/render/city-kit.spec.ts`: it failed before the fix (`outline none`) and passes at 375 and 1280. Pairs: `pair-map-keyboard-focus-{375,1280}-{before,after}.png` |

### Measured and dismissed (not counted)

- The map's cookie note ("Nothing loads from Google until you tap…") is 13px: a caption's fine print under the
  15px caption, the label tier this pass has always dismissed (captions, reviewer lines, places chips). The
  breeder's 14px phone ruling (2026-10-06 q03) names the statement notes and the card lines, and the note is as
  the S1 preview showed it.
- From 768 the map runs the text column's full width (640 / 704px) while the paragraphs around it stop at their
  65ch measure (549px). The board places it "at the text column's width", and the preview the breeder picked
  from showed it so.
- "DEFRA-approved" breaks at its hyphen in the caption at 1280. A natural break; the money band never splits
  (0 range splits at every width).
- The edge probe reported links past the right edge at 375: they are the closed header drawer's panel inside a
  closed `<details>`, never painted or focusable. Opened, the drawer sits inside the viewport (280px wide, 0 links
  past the edge).
- Jump stepper stops at 36×44 on a phone: WCAG 2.5.5's equivalent-control exception (the "All 10" key opens the
  sheet), as in every earlier pass.
- The seven statement labels' 3px brass tick: a marker before a two-word caps label, radius 0, the breeder's pick.
- No `:active` state on the map's button: no kit control has one, so adding one here would be drift.
- `img-not-upscaled` and `img-face-visible` advisories: pre-existing, unchanged by this pass.

### The five Harden calls, checked as built

| Call | Measured |
|---|---|
| q01 close card outline | 0 side-tab detector rows on the closes; all four closes 1px all round in steel-300 at 375 and 1280. |
| q02 hidden lead comma | The closes read "and tell us which puppy caught your eye." on screen at 375. |
| q03 14px phone notes | 0 card trust lines or delivery lines under 14px at 375; 13px kept at 768 / 1280. |
| q04 one-row phone header | 73px at 375 (one row: logo, "Available puppies" centred, menu icon). |
| q05 two across | Puppy cards 353px wide, two across at 1280. |

## Positive findings

- The map asks nothing of Google until a tap, and the render spec now holds that, the 44px button, the iframe's
  title, `loading=lazy` and `referrerpolicy`, and the box not moving.
- The iframe takes the facade's reserved box exactly: 0px change in the answer's height at every width.
- Focus moves into the map after the tap, and the next Tab reaches "Buyers in Essex", the next link in the answer.
