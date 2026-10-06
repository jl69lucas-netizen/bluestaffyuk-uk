# frontend-design Harden pass: London, third run (2026-10-06)

Page: `/uk-locations/blue-staffy-puppies-london/` (`src/pages/uk-locations/blue-staffy-puppies-london.astro`),
`docs/reference/page-run.md` row 15, run after today's impeccable pass
(`docs/reports/impeccable-london-2026-10-06.md`, recorded at `b34a9c04`) on a fresh build that carries its fix.
The `frontend-design:frontend-design` skill was invoked with the Skill tool (args: Harden pass on the built
London page at 375 / 768 / 1280; BSUK design system fixed; content and the approved board unchanged; visual
layer only; design changes previewed, not applied). The pass applies that skill's `SKILL.md` (purpose, tone,
differentiation; typography, colour commitment, motion, spatial composition, visual detail) inside BSUK's
locked system: Fraunces and Source Sans 3, the steel / bone / brass tokens, `rules/design.md` (rule 6: motion
at most 0.2s) and the city type tiers in `src/styles/city.css`. The skill's "choose unique fonts" and "vary
themes" directions do not apply: the system is fixed.

**Visual layer only.** No word, heading, link target, image or section order changed. The one fix changes only
where a three-word label wraps. Nothing in this pass needed the breeder, so there are no proposals.

## How it was assessed

`npm run -s build`, `dist/` served on 127.0.0.1, Chromium through Playwright (device scale 1), requests to any
other host answered locally. Today's impeccable contact sheets (full-page captures at 375 / 768 / 1280) and its
element shots of the map in every state were re-read for composition. Then probes ran in the same browser at
each width: the last line of every heading, paragraph, list row, ledger value, caption and FAQ question in
`main` (a one-word last line under a longer text, read per text element so a numbered summary's number is not
taken for a line); every element's transition and animation duration against rule 6; the map's composition (the
pin, name and button against the panel's centre, the space above and below them, its radius and shadow against
the answer's own picture, and its margins against the paragraph rhythm of the answer); and the map button's
hover (colour, cursor, and the hover pair's contrast).

Before / after pairs: `docs/reports/screens/frontend-design-london-2026-10-06/`.

## The aesthetic read

**Point of view, unchanged: a breeder's ledger in steel and brass.** The map joins it rather than adding a new
voice. It is not a grey map tile dropped into the column: it is a steel panel in the ledger's own colour, an
abstract contour and a river line in a lighter steel, one brass pin, the city's name in Fraunces, and one brass
pill. It reads as "this is where you are" before the
reader asks for Google, and the caption under it says where we are. Composition measured: the pin, name and
button sit exactly on the panel's centre (0px off at every width), with 43px above and below on a phone and 77px
from 768; the panel's 12px radius matches the answer's picture; the margins around it (16px) open slightly
wider than the answer's paragraph rhythm (12px), which sets it apart as a figure without breaking the column.

**The five Harden calls, as composition.** The one-row phone header (logo, the "Available puppies" pill centred,
the menu icon) gives back 48px of every phone screen and makes the pill the header's one action. The puppy
cards stand two across at 1280, 353px each (measured), where three across gave 231px. The close cards' steel
outline leaves the pill as the card's one brass; the hidden comma lets the clause read as its own line.

**Weakest now:** nothing structural. The one craft flaw left was a single word alone on the counter's label at a
desktop width (F1).

## Findings

1 finding: 1 fixed, 0 deferred. Severity as row 14 uses it (P1 blocks a reader, P2 a visible flaw, P3 polish).

| # | Sev | Finding | Location | Widths | Outcome |
|---|---|---|---|---|---|
| F1 | P3 | From an 840px viewport the price scale's count stands in a 14ch column beside the line, and its label broke "puppies available" / "now": the page's first figure, under the hero, ended on one word at 1024 and 1280 | `CityPriceScale.astro` `.count .l` | 1024 1280 | **fixed**: `text-wrap: balance`, so it reads "puppies" / "available now". Same two lines, same height (111px), no word changed; 768 and 375 (one line beside the figure) unchanged. Render test added to `tests/render/city-kit.spec.ts`: it failed before (1 word on the last line at 1024 and 1280) and passes after (2). Pairs `pair-fd-count-label-{1024,1280}-{before,after}.png` |

### Measured and dismissed (not counted)

- One-word last lines elsewhere in `main`: 0 at 768 and 1280. At 375 one is left, the places list's "Rules set by
  London Borough of" / "Sutton": a publisher's name, as the 2026-10-05 pass recorded.
- The map panel carries the kit's card shadow while the answer's picture above it carries none. It is the
  preview the breeder picked (S1), and the lift marks the panel as something to tap, not a picture.
- The map runs the text column's width while the paragraphs stop at their 65ch measure: the board's placement,
  as the preview showed it.
- Motion: no transition or animation in `main` over 0.2s at any width; the map button's background change is
  `--dur-fast` and is switched off under `prefers-reduced-motion`.
- The map button's hover (steel-900 on brass-600, the site's CTA hover pair) is 4.79:1; the cursor is a pointer.
- `img-not-upscaled` and `img-face-visible` advisories: pre-existing, unchanged by this pass.

## Positive findings

- The facade does the job a map image would do (it names the place) with no request to Google, and the tap swaps
  it for the real map in the same box, so the page never jumps.
- The new pieces since 2026-10-05 stayed inside the system: no new colour, no new type size, no motion over
  0.2s, no new radius.
