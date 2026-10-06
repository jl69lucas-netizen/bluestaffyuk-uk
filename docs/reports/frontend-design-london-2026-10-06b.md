# frontend-design Harden pass: London, fourth run (2026-10-06b)

Page: `/uk-locations/blue-staffy-puppies-london/` (`src/pages/uk-locations/blue-staffy-puppies-london.astro`),
`docs/reference/page-run.md` row 15, run after the afternoon's impeccable pass
(`docs/reports/impeccable-london-2026-10-06b.md`, recorded at `ad2c9c40`) on a build that carries its fix
(`f0d155b1`: the dial scrolls its own box to show the row it marks). The `frontend-design:frontend-design` skill
was invoked with the Skill tool (args: Harden pass on the built London page at 375 / 768 / 1280; BSUK design
system fixed; content and the approved board unchanged; visual layer only; design changes needing the breeder
are proposals, not applied). The pass applies that skill's `SKILL.md` (purpose, tone, differentiation;
typography, colour commitment, motion, spatial composition, visual detail) inside BSUK's locked system:
Fraunces and Source Sans 3, the steel / bone / brass tokens, `rules/design.md` (rule 6: motion at most 0.2s) and
the city type tiers in `src/styles/city.css`. The skill's "choose unique fonts" and "vary themes" directions do
not apply: the system is fixed.

**Visual layer only.** Nothing was changed by this pass. Nothing in it needed the breeder, so there are no
proposals.

## What changed since the last pass

`noindex` off (no visual effect), the map's cookie note two words shorter (`fbf80a9c`), the scroll spy keeping
the reading band's whole state (`9010e4f4`), and the dial now scrolling its own box to show its marked row
(`f0d155b1`). This pass read those as composition first.

## How it was assessed

`npm run -s build`, `dist/` served on 127.0.0.1, Chromium through Playwright (device scale 1), requests to any
other host answered locally. The impeccable pass's element shots (the map at 375 and 1280, the dial in every
section at four laptop and desktop heights, the focused puppy card) were re-read for composition. Then probes ran
at 375×812, 768×1024 and 1280×800, after a full scroll so every lazy image had loaded:

- the last line of every heading, paragraph, list row, caption, label, summary and FAQ question in `main` with
  at least four words (244 / 246 / 248 text elements examined), for a line holding one word alone;
- every element's transition and animation duration against rule 6;
- at 1280×800, the dial in each of its 10 sections: the marked row, how far the dial's box has scrolled, and the
  room left under the marked row; then back at the top of the page.

## The aesthetic read

**Point of view, unchanged: a breeder's ledger in steel and brass.** Nothing since the last pass adds a voice.
The map note reads as the fine print it is, under the caption, and still carries both disclosures.

**The dial, as composition.** It was the one place the page broke its own promise: a panel titled "Where you
are on the page" that, in the last two sections at 1280×800, marked a row below its own edge. It now marks a row
the reader can see in all 10 sections, and it moves only when it must: the box stays at the top for the first
eight sections (scroll 0), then scrolls 24px for everyday health and 72px for the enquiry, leaving the same 16px
under the marked row each time, and it returns to 0 when the reader goes back to the top. It moves in one frame,
with no animation, so rule 6 and a reader who asks for reduced motion are both untouched.

## Findings

0 findings: 0 fixed, 0 deferred.

### Measured and dismissed (not counted)

- One-word last lines: 0 at 375, 768 and 1280 among the 244 / 246 / 248 text elements examined.
- Motion: 0 transitions or animations longer than 0.2s at any width.
- **The dial's photo scrolls with its box.** In the last two sections at a laptop height, the 24px or 72px the box
  scrolls is taken from the top of its photo (Cheryl, 181px tall at 1280), so for those two sections the photo
  shows its lower 157px or 109px. That is the box's ordinary scroll, the same a reader got by scrolling the dial
  before the fix, and the marked row being visible is what the panel is for. Shrinking the photo on short screens
  instead would change the approved look, so it is not proposed as a fix here; it is listed so the breeder can
  ask for it at the post-launch refinement if she prefers it.
- The map note at 1280 breaks "Google / Maps," across its two lines: a natural break inside the note's measure.

## Positive findings

- The dial and the jump band now agree with the page in every section, at every width measured.
- The page has no motion over 0.2s and no one-word last line anywhere in `main`.
