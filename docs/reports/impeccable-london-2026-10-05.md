# impeccable Harden pass: London, second run (2026-10-05)

Page: `/uk-locations/blue-staffy-puppies-london/` (`src/pages/uk-locations/blue-staffy-puppies-london.astro`),
`docs/reference/page-run.md` row 14. Re-run because `gate:page` reported the frontend-design key stale ("the
page changed after the frontend-design pass; re-run it") and this pass is the one before it. Since the
2026-10-03 passes the page gained the CARD-3 puppy band (`CityTicketStrip`), the CTA-1 brass pills on the
chapter closes, image swaps, the breeder photo, the chapter layout fixes, the close-proposal FAQ set, the
statement labels (`StatementLine`), the name swaps and the certificates sentences. This pass looked at all of
it, and at the rest of the page again.

The `impeccable:impeccable` skill was invoked with the Skill tool (args: audit and polish the built London
page at 375 / 768 / 1280; BSUK design system; content and the approved board unchanged; visual layer only).
This pass follows its `SKILL.md` (shared laws, absolute bans), `reference/brand.md` (brand register: a
breeder's long-form buying page), `reference/audit.md` and `reference/polish.md`.

**Setup gate.** `load-context.mjs` returns `hasProduct: false, hasDesign: false`. As in every earlier pass
(`docs/reports/impeccable-london-2026-10-03.md`), PRODUCT.md can only be written by `/impeccable teach` with
the user, so it was not synthesised; the brand context came from the repo's own design sources
(`rules/design.md`, `IMAGE-DESIGNS.md`, `src/styles/tokens.css`, `src/styles/city.css`, `data/settings.json`).
Fraunces is a locked token (`rules/design.md` rule 2): the skill's reflex-reject list is recorded, not acted
on. The palette never changes.

**Visual layer only.** No word, heading, link target, image choice or section order changed, and nothing the
breeder approved was repainted. The two fixes change where two lines may wrap and how wide three header links'
hit areas are; a change that would alter an approved look or any visible word is a proposal (below), not
applied.

## How it was assessed

1. `npm run -s build`, `dist/` served on 127.0.0.1, Chromium through Playwright (device scale 1).
2. Deterministic detector: `npx impeccable detect --json dist/uk-locations/blue-staffy-puppies-london/index.html`
   (13 rows).
3. Design review of real screenshots: viewport shots scrolled through the whole page at 375 (57 shots), 768
   (36) and 1280 (38), read as contact sheets.
4. A measuring probe in the same browser at each width: contrast of every painted text element against its
   effective background (675 / 681 / 672 elements), every interactive target's box (135 / 140 / 129), document
   width against the viewport, every element's right edge, a Tab walk recording each stop's ring (112 / 124 /
   113 stops), text under 14px, every image's decoded width against its painted width (60 per width), side
   borders over 1px, heading sizes, layout shift (PerformanceObserver through load and a full scroll), and the
   console.
5. A line-break probe at 375 / 768 / 1024 / 1280: every money or number range whose two ends land on different
   lines, and every " · " separator left at a line end.

Before / after pairs of the fixes: `docs/reports/screens/impeccable-london-2026-10-05/`. Previews of the
deferred changes (before and preview at each width): `docs/reports/london-harden-2026-10-05/`, collected on the
"London Harden Proposals" page (`docs/reports/london-harden-2026-10-05/index.html`).

## Detector rows

| Rows | Antipattern | Verdict | Reason |
|---|---|---|---|
| 0 | `side-tab` `border-top: 4px` | dismissed | `CityTakeawaysLedger`'s full-bleed steel rule on a radius-0 root (the known false positive). |
| 1–4 | `side-tab` `border-left: 3px + border-radius: 12px` | **verified, deferred (D1)** | `CityChapters` `.close`: the CTA-1 card's 3px brass left rule on the four chapter closes (deposit, litter, paperwork, temperament). An absolute ban, but CTA-1 is the breeder's pick (answer board 2026-10-04 q09 (a)), so the change is a preview. |
| 5–6 | `all-caps-body` (32 and 41 characters) | dismissed | The hero eyebrow and the ticket band's label: short labels, which `brand.md` reserves caps for. |
| 7–9 | `cramped-padding` on `div.list` | dismissed | `CityFaqLedger`'s ruled list; its `<summary>` rows carry the padding (known false positive). |
| 10 | `clipped-overflow-container` on `html` | dismissed | The site's `overflow-x: clip` on `html`. |
| 11 | `overused-font` Fraunces | recorded, not acted on | Locked display token (rule 2). |
| 12 | `side-tab` inset 3px stripe on `.city-scale` | dismissed | The counter bed's full-width top rule that `layout-hero-counter-separation` requires. |

## Audit health score

| # | Dimension | Score | Key finding |
|---|---|---|---|
| 1 | Accessibility | 3 | 0 contrast failures at any width; every focus stop draws a ring; three header nav links were under the 44px chrome target D3 set for every page (fixed, F2). |
| 2 | Performance | 3 | CLS 0.0000 through load and a full scroll at every width; no image decoded over 2x its box; 0 console errors. Five H2 photos paint upscaled from 400–550px masters (pre-existing advisory). |
| 3 | Responsive design | 3 | Document width = viewport at 375 / 768 / 1280, no element past the right edge; the new puppy band's delivery line split its price band and hung its separator (fixed, F1); 13px notes on a phone (D3). |
| 4 | Theming | 3 | Every colour a token; the fixes add no colour and no value off the scale. |
| 5 | Anti-patterns | 3 | One real absolute-ban hit, the CTA close card's side rule, on an approved design (D1). |
| **Total** | | **15/20** | **Good** |

**Anti-patterns verdict.** It does not read as AI-made: the steel ledger, the brass spent only on money and
steps, real photographs of the litter, a hero that leads with six named puppies. The one tell is the CTA close
card's brass side rule, added with CTA-1.

## Findings

5 findings: 2 fixed, 3 deferred. Severity: P1 blocks a reader, P2 a visible flaw, P3 polish.

| # | Sev | Finding | Location | Widths | Outcome |
|---|---|---|---|---|---|
| F1 | P2 | The new puppy band's delivery line broke inside its own facts: at 1280 all six cards split the price band "£200–" / "£350" across lines; at 375 and 768 all six left the "·" hanging at a line end ("by distance ·" / "or collect in Carlisle"); the roster's foot line did the same at 375. 19 breaks, measured by the line-break probe | `CityTicketStrip.astro` `.pc-del`, `CityRoster.astro` `.foot` | 375 768 1280 | **fixed**: cityKit `deliveryLineRuns` splits the canonical `deliveryLine` into runs (and throws if they ever stop spelling it), and the two components set the band and the "· or" in `.keep` spans (`white-space: nowrap`, in `city.css`), as `CityPuppySheet` already holds its band. Text content unchanged. The probe now finds 0 breaks at 375 / 768 / 1024 / 1280. Pairs: `pair-ticket-delivery-{375,768,1280}-{before,after}.png`, `pair-roster-foot-375-*.png` |
| F2 | P3 | The header's main nav links were 44px tall but 29–43px wide from 768 up ("Blog" 29px, "Home" 38px, "Health" 43px), under the 44×44 chrome target the breeder approved for every page (impeccable D3, 2026-10-03 q04), which fixed the brand link, crumbs and footer but not these | `SiteHeaderKit.astro` `.nav a` | 768 1280 | **fixed**: 8px of inline padding cancelled by an 8px negative margin (no word moves), and the current-page underline redrawn as a 2px background band sized to the old box, so it does not widen. Links now 45–120px wide. 24 header screenshots (home, blog, health, locations hub, London, contact at 768 / 900 / 1024 / 1280, the current-page underline included) are pixel-identical before and after |
| D1 | P3 | The CTA close card carries a 3px brass left rule with a 12px radius: the side-stripe absolute ban (detector rows 1–4) | `CityChapters.astro` `.close` | all | **deferred**: CTA-1 is the breeder's pick (answer board 2026-10-04 q09 (a)); changing its border is a visible change to an approved design (working rule 6). Preview: a 1px steel-300 hairline all round, the pill left as the card's one brass accent. `IMP-D1-close-rule-{375,1280}-{before,preview}.png` |
| D2 | P3 | The clause after each CTA pill opens with its comma: on a phone the pill fills the line, so the next line starts ", and tell us which puppy caught your eye."; from 768 the comma sits 6px after the pill, reading as a stray mark | `CityChapters.astro` `.close p` | 375 768 1280 | **deferred**: the fix changes what a reader sees of the board's sentence. Preview: the leading comma hidden (`aria-hidden`, so the sentence a screen reader hears is unchanged), the clause continuing "and tell us which puppy caught your eye." `IMP-D2-close-comma-{375,768,1280}-{before,preview}.png` |
| D3 | P2 | Reading text under 14px on a phone: the statement note under each of the seven statement labels ("Lisa Bright's own statement: the tests are named only, and no result is claimed"), and in each of the six puppy cards the eight "comes home with" lines and the delivery line, all at `--text-xs` 13px | `StatementLine.astro` `.stmt-note`, `CityTicketStrip.astro` `.pc-trust li`, `.pc-del` | 375 | **deferred**: a type-size change to two approved kit pieces (statement labels q02, CARD-3 q08 (c)); each card grows by about two lines. Preview: 14px below 640px only. `IMP-D3-phone-notes-{stmt,card}-375-{before,preview}.png` |

### Deferred: applied (2026-10-06)

The breeder approved all three deferred changes (answer board batch `2026-10-06-london-harden-calls`, rulings `docs/reference/answer-board/answers/2026-10-06-london-harden-calls-2026-10-06.md`); each is recorded as a London board revision (37–39) and the board re-approved (`d3b8ed40`):

| Change | Breeder's answer | Commit | What shipped |
|---|---|---|---|
| D1 | q01: (a) yes, thin outline | `4c7601b9` | `CityChapters` `.close`: a 1px `--color-steel-300` border all round in place of the 3px brass left rule; the pill is the card's one brass accent. Measured on the four closes at 375 / 768 / 1024 / 1280. |
| D2 | q02: (a) yes, hide the comma | `37624f45` | `CityChapters` wraps the comma straight after a close paragraph's first-child link in `.lead-comma`, visually hidden by the clip pattern (not `aria-hidden`, which would have dropped it from what a screen reader hears): the page text and the accessible text keep the board's sentence word for word, the screen shows "and tell us which puppy caught your eye." The route file is untouched; `check:verbatim`, `check:links`, `check:facts`, `check:outline` and `check:parity` exit 0 on the built page. |
| D3 | q03: (a) yes, 14px on phones | `6d8cf8be` | Below the 640px tier edge (`@container`): the seven statement notes and the six cards' 48 trust lines and 6 delivery lines at 14px (13px kept at 768 / 1024 / 1280). Each card 307/328px → 335/356px at 375, under the 2,030px per-card cap. |

Screens, before and after: `docs/reports/screens/harden-calls-2026-10-06/london/` (`45a824cd`).

### Measured and dismissed (not counted)

- The six puppy-card name links report no ring of their own: each link's `::before` stretches over its card
  and the card draws the ring (`.pc:focus-within`, computed `3px solid` brass, offset 3px), so the whole card
  is the target and the ring is around it.
- Jump stepper stops at 36×44 on a phone: WCAG 2.5.5's equivalent-control exception (the "All 10" key opens
  the sheet, 343×52–68 rows), as on 2026-10-03.
- Checklist checkboxes 20×20 sit in a `<label>` the width of their row; honeypot inputs are off screen;
  links inside sentences are WCAG 2.5.8's inline exception.
- The statement labels' 3px brass tick: a marker before a two-word caps label, radius 0, not a card or
  callout edge; the breeder's pick (q02).
- 13px caps labels, captions, footer column heads, the places chips and the reviewer lines: the label tier,
  not reading text.
- `img-not-upscaled` (advisory, pre-existing): five H2 photos paint at 1.16–1.76x their 400–550px masters at
  768 and 1280 (`find-health-certified-staffy-breeders-uk`, `puppy-vaccinations-uk`,
  `blue-staffy-testimonial-london-happy-owner`, `staffordshire-bull-terrier-vs-american-bully-comparison`,
  `blue-staffy-health-prioritising-wellbeing`). Unchanged by this pass; it needs larger masters added beside
  the served files at an image step (working rule 11).
- The legacy `SiteHeader` (pages on `BaseLayout`, not London) was not examined in this pass.

## Positive findings

- Document width equals the viewport at every width; tables stack below 640px (rule 13).
- 0 contrast failures over 2,028 text elements; 349 focus stops, every one ringed (the six card links on
  their card).
- CLS 0 through load and scroll; 60 images per width, none decoded over 2x its box; 0 console errors.
- The new pieces hold the system: the CARD-3 band's brass is a fill on the price chip only, the CTA pills are
  the brand's brass pill, and every new colour is a token.

## Verification

| Command | Exit | Examined |
|---|---|---|
| `npm run -s build` | 0 | 63 built pages |
| line-break probe (375 / 768 / 1024 / 1280) | — | 19 breaks before, 0 after |
| header pixel comparison | — | 24 captures, 0 differing |
| `npx playwright test -c tests/render/playwright.config.ts pages.spec.ts -g "blue-staffy-puppies-london"` | 0 | 3 passed (375, 768, 1280) |
| `npx playwright test -c tests/render/playwright.config.ts pages.spec.ts` (the header is on every page) | 0 | 63 passed (21 pages × 3 widths) |
| `python3 -m pytest tests/py -q` | 0 | 7683 passed, 18 skipped, 1 xfailed |

The pass is recorded in `data/page-runs/blue-staffy-puppies-london.json` (`impeccable`: 375 / 768 / 1280,
5 findings, 2 fixed, 3 deferred with the reasons above).
