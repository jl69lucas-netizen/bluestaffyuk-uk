# impeccable Harden pass: London, fourth run (2026-10-06b)

Page: `/uk-locations/blue-staffy-puppies-london/` (`src/pages/uk-locations/blue-staffy-puppies-london.astro`),
`docs/reference/page-run.md` row 14. Re-run because the page changed after the morning's passes
(`docs/reports/impeccable-london-2026-10-06.md`, `frontend-design-london-2026-10-06.md`): the breeder approved
the page (`docs/reference/answer-board/answers/final-approval-blue-staffy-puppies-london-2026-10-06.md`) and
`noindex, follow` came off (`f3031626`); the map's cookie note lost two words (`fbf80a9c`); and the scroll spy
the dial and the jump stepper share now keeps the reading band's whole state (`src/lib/scrollSpy.ts`,
`9010e4f4`, lessons entry 20). This pass looked at those first and at the rest of the page again.

The `impeccable:impeccable` skill was invoked with the Skill tool (args: audit and polish the built London page
at 375 / 768 / 1280; BSUK design system fixed; content and the approved board unchanged; visual layer only;
anything needing the breeder is a proposal). It follows the skill's `SKILL.md` (shared laws, absolute bans) and
`reference/audit.md`; the page is the **brand** register.

**Setup gate.** `load-context.mjs` returns `hasProduct: false, hasDesign: false`, as in every earlier pass.
PRODUCT.md is written only by `/impeccable teach` with the user, so it was not synthesised. The brand context
came from the repo's own design sources (`rules/design.md`, `IMAGE-DESIGNS.md`, `src/styles/tokens.css`,
`src/styles/city.css`, `data/settings.json`). Fraunces is a locked token (`rules/design.md` rule 2). The palette
never changes.

**Visual layer only.** No word, heading, link target, image or section order changed, and nothing the breeder
approved was repainted. The one fix makes the dial scroll its own box so the row it already marks is visible.
Nothing in this pass needed the breeder, so there are no proposals.

## How it was assessed

1. `npm run -s build`, `dist/` served on 127.0.0.1, Chromium through Playwright (device scale 1), every request
   to another host answered locally (0 such requests before the map is tapped, at every width).
2. Detector: `npx impeccable detect --json dist/uk-locations/blue-staffy-puppies-london/index.html` (9 rows).
3. A measuring probe at each width (375×812, 768×1024, 1280×800): the robots meta; document width against the
   viewport; contrast of every painted text element against its effective background (597 / 610 / 601
   elements); every interactive target's box (136 / 141 / 130); every element's right edge; a Tab walk recording
   each stop's ring (113 / 125 / 114 stops); reading text under 14px in `main`; CLS through load and a full
   scroll; console errors; the map note's words and size; and the scroll spy: for every touching pair of the
   10 sections the nav names, a boundary landed in the reading band and then the lower section filling it, with
   the marked row read each time (9 pairs per width).
4. Element shots of the map at 375 and 1280, the focused puppy card, and the dial in every section at 1280×800,
   1280×720, 1024×768 and 1440×900.

Screens: `docs/reports/screens/impeccable-london-2026-10-06b/`.

## What changed since the last pass, as built

| Change | Measured |
|---|---|
| `noindex` off | One robots meta, `index, follow`, at every width; the page is in `location-sitemap.xml` (`check:sitemaps`: 63 built pages, 37 sitemap urls, 0 problems). No visual effect. |
| Map note, two words shorter | "Nothing loads from Google until you tap. Showing the map loads Google Maps, which sets cookies." Both disclosures kept, 13px, two lines at 375 and 1280 (`map-note-375.png`, `map-note-1280.png`). |
| Scroll-spy fix | 9 of 9 touching pairs follow at 375, 768 and 1280 (0 stuck); the jump band at 375 and the dial at 1280 both mark `delivery` after a jump to it and a scroll back. |

## Detector rows

| Rows | Antipattern | Verdict | Reason |
|---|---|---|---|
| 0 | `side-tab` `border-top: 4px` | dismissed | `CityTakeawaysLedger`'s full-bleed steel rule on a radius-0 root (the known false positive). |
| 1–2 | `all-caps-body` | dismissed | The hero eyebrow and the ticket band's label: short labels. |
| 3–5 | `cramped-padding` on `div.list` | dismissed | `CityFaqLedger`'s ruled list; its `<summary>` rows carry the padding. |
| 6 | `clipped-overflow-container` on `html` | dismissed | The site's `overflow-x: clip` on `html`. |
| 7 | `overused-font` Fraunces | recorded, not acted on | Locked display token (rule 2). |
| 8 | `side-tab` inset 3px stripe on `.city-scale` | dismissed | The counter bed's full-width top rule (`layout-hero-counter-separation`). |

The same 9 rows as the morning's pass; the changes add none.

## Audit health score

| # | Dimension | Score | Key finding |
|---|---|---|---|
| 1 | Accessibility | 4 | 0 real contrast failures; every Tab stop draws a ring; the nav marks the right section after any jump. The dial marked its last rows out of sight on laptop-height screens (fixed, F1). |
| 2 | Performance | 3 | CLS 0.0000 at every width; 0 console errors; 0 requests to another host at load. The pre-existing upscaled-photo advisories are unchanged. |
| 3 | Responsive design | 4 | Document width = viewport at 375 / 768 / 1280; nothing past the right edge that paints. |
| 4 | Theming | 4 | No colour added; the fix is script only. |
| 5 | Anti-patterns | 3 | No new tell; Fraunces stays locked. |
| **Total** | | **18/20** | **Excellent** |

**Anti-patterns verdict.** It does not read as AI-made; the changes since the last pass add nothing visual
except two fewer words in a note.

## Findings

1 finding: 1 fixed, 0 deferred. Severity: P1 blocks a reader, P2 a visible flaw, P3 polish.

| # | Sev | Finding | Location | Widths | Outcome |
|---|---|---|---|---|---|
| F1 | P2 | The dial ("Where you are on the page") is sticky and scrolls inside its own box (`max-height: 100vh - header`, `overflow-y: auto`). On a laptop-height screen its last rows sit below that box's edge, so in the last sections the marked row could not be seen: at 1280×800 `everyday-health` (row 748–792) and `enquiry` (796–840) against a dial showing 89–784; at 1024×768 and 1280×720 `breed` too. The dial then told the reader nothing. Not found before because the spy probes read `aria-current`, never whether the row was on screen; at 1440×900 every row fits | `CityDialPhotoMarker.astro` (script) | 1024 1280 (laptop heights) | **fixed**: when the marked row is outside the dial's box, the dial's own box is scrolled (never the page, no `scrollIntoView`, no motion) to show it with 16px to spare; back on the first row it returns to the top so the photo shows again. Render test added to `tests/render/city-kit.spec.ts`, "the dial keeps its current row in view", at 1280×800 and 1024×720 on the specimen and on London: it failed before the fix on both routes (on London, 6 rows out of view: 2 at 1280×800, 4 at 1024×720) and passes after (20 rows examined on London). The touching-pairs spy test still passes at 375 and 1280. Pair: `pair-dial-current-row-1280x800-{before,after}.png` |

### Measured and dismissed (not counted)

- **1 contrast failure per width** ("Written by Lisa Bright, breeder, Carlisle", ratio 1.26): the probe's own
  bug. The byline's colour is `color(srgb 0.957 0.945 0.918 / 0.9)` (bone at 90%), which the probe's parser read
  as 0–255 values, so it took near-white for near-black. Computed again, the 90% bone blended over the
  steel-900 band (`#14202B`, `rgb(20, 32, 43)`) is 12.05:1.
- **6 Tab stops with no ring per width** (the six puppy-card name links): the ring is on the card, not the
  link. `CityTicketStrip.astro` draws `.pc:focus-within { outline: 3px solid var(--color-focus-on-inverse) }`
  because the name link's `::before` stretches over the whole card; measured `rgb(201, 162, 39) solid 3px` on the
  focused card and seen painted (`puppy-card-focus-375.png`).
- **Targets under 24px**: the eight call-checklist checkboxes are 20×20 inside labels 277–310px wide and 85–130px
  tall, which are the tap target; the 1×1 element is the form's honeypot (`tabindex="-1"`, `aria-hidden`).
- **18 elements past the right edge at 375**: the closed header drawer's links inside a closed `<details>`,
  never painted or focusable (as in every earlier pass).
- **13px text in `main`** (33 at 375, 105–106 from 768): label-tier text (eyebrows, statement labels, the
  ticket tags, the enquiry picker's "Boy · £1,500" captions under each thumbnail, the map's cookie note). None
  is a statement note or a card line, which the breeder's 14px phone ruling (2026-10-06 q03) names.
- The map note at 1280 breaks "Google / Maps," across its two lines: a natural break inside the note's measure.

## Positive findings

- The spy fix holds on the built page in a painting browser, not only in its test: 27 of 27 boundary jumps
  across three widths mark the section the reader is in.
- The page asks nothing of Google until the map is tapped, and has 0 layout shift at every width.
