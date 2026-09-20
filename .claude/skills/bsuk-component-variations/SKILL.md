---
name: bsuk-component-variations
description: "Use when the breeder wants three variations of a BlueStaffyUK component, a new hero, a new counter strip, a different table or FAQ treatment, or asks to \"see the options\", \"show me three\", \"this component is wrong on mobile\", \"build a variations canvas\" — on this repo that is the BOARD system, not a design canvas: three structurally different styles per section, rendered from the real kit on /board-preview/<slug>/ and shown on the page board at 1280 / 768 / 375 for the breeder to pick from before anything is written to src/pages/."
---

# SKILL: BSUK Component Variations — three rendered styles per section

## 1. What this is, and what it is NOT

The source repo produced variations as hand-authored artboards on a `/design` canvas.
**This repo does not.** Here a variation is a `StyleDef` in `src/lib/boardStyles.ts` that the
REAL kit renders: `src/pages/board-preview/[slug].astro` emits every section of a board
record three times as `<section data-section data-style>`,
`scripts/build_board_previews.py` cuts those blocks out of the built page, and
`scripts/build_page_board.py` mounts each one in a sandboxed `srcdoc` iframe at 1280, 768
and 375 on `docs/artifacts/boards/<slug>.html`.

Three consequences, and they are the whole reason for the change:

- **What the breeder approves is what ships.** A rebuilt page calls the same `boxClass()`
  with the picked id. There is no second implementation to drift.
- **A variation cannot lie.** It renders the kit's own markup, the record's own copy and the
  record's own images, so an artboard can never assert a claim the page will not carry.
- **A variation is only real if a renderer reads it.** `RENDERED_AXES` names, per shape, the
  axes that shape's renderer actually reads. An axis outside that list would describe a
  difference nobody can see, and three styles that all render the same are a pick with no
  question in it.

Nothing is written to `src/pages/` until the record is approved (judgment rule 6, preview
before apply).

## 2. Invariants every variation keeps

Read `.claude/skills/bsuk-component-refresh/SKILL.md` §0 — the same eleven invariants bind
here, because a variation is a refresh the breeder has not picked yet. In short, and in the
order they get broken:

1. **Palette and type are tokens.** Steel / brass / bone and Fraunces / Source Sans 3, from
   `src/styles/tokens.css`. No hex under `src/` outside that file. No new colour is ever a
   variation.
2. **The pill CTA** (`--btn-radius`) and the card radius (`--card-radius`) are fixed.
3. **The hero clamp**, `rules/design.md` rule 10: photo first in the DOM, band held between
   390px and 450px at 1024px and up, nothing clipped, the copy sized to fit and only the
   photo cropped. Measured by `scripts/measure_canvas_heights.mjs`.
4. **Hero / counter separation**: a tone shift AND a rule between them.
5. **The dial, the sheet and the strip are decided** (2026-09-19). Their entries stay in the
   style map so approved records can re-approve, but all three ids render the one shipped
   arrangement. Do not author a fourth.
6. **Tables stack into labelled rows below 640px in all three chrome arrangements** —
   working rule 13.
7. **Images by their original public path, videos at their original id** — working rules 11
   and 14. A variation never re-encodes a served file and never mints an id.
8. **Copy is the record's own.** The preview route prints the section `heading` as the H2,
   the first sentence of `intent` as the lede, and one sentence per tree node as a stub. It
   invents nothing (working rule 9), and neither may a variation.
9. **The verbatim set** (working rule 15) survives every arrangement.
10. **No emoji anywhere.** Inline SVG, from `src/components/kit/markShapes.ts`.

## 3. Inputs, read before drawing anything

- **`src/lib/boardStyles.ts`** — what already exists. A new variation should read as a
  deliberate departure from the three that ship, not as an accident of not having looked.
- **`src/components/kit/_registry.ts`** — the eighteen kit components and what each takes.
- **The breeder's idea sheets** — the hero and component reference images the breeder
  supplied. They are the source of the per-page hero and counter sets under working rule 16;
  describe the one you drew from in the commit message so the choice is traceable.
- **`rules/design.md`** — the nine non-negotiable visual rules this stacks on top of, plus
  the hero/counter separation rule and the H3-image-first rule.
- **The board record** — `data/boards/<slug>.json`. On a boarded page the copy source is the
  RECORD, never a sibling page and never `dist/`.

## 4. Method

1. **Name the axis, never the size.** One axis word per variation. "Smaller" is not an axis;
   `media: 'top'` against `media: 'right'` is. The three defs of a shape must differ on at
   least one axis in that shape's `RENDERED_AXES` row — `tests/py/test_board_previews.py`
   holds them to it, and holds the BUILT blocks of `/board-preview/_demo/` to differing too.
2. **Differ STRUCTURALLY.** A different column count, a different media position, a band
   instead of a card, a grid instead of a stack. Never a token, never a spacing step.
3. **Set only the axes the renderer reads.** `boxClass()` fills the rest with the neutral
   value; an axis a renderer ignores is decoration in a data structure.
4. **Per-page sets, for the hero and the counter** (working rule 16).
   `HERO_STYLES_BY_PAGE_TYPE` and `COUNTER_STYLES_BY_PAGE_TYPE` give each page type three
   styles that are structurally different from each other AND from every other page type's
   set. A prop a new layout needs is added to `src/components/kit/Hero.astro` or
   `src/components/kit/CounterStrip.astro` as OPTIONAL with no default that asserts content
   — the 2026-09-20 review removed the hero's hard-coded chips and CTAs for exactly that
   reason, and a default that states a credential is a component asserting a page's
   credentials for it.
5. **Counter figures come from the record**, as `sections[].stats` rows of
   `{n, label, source}`, each `source` a path into `data/*.json` that a test resolves. Never
   a typed number. Where nothing on disk backs a figure, ship fewer tiles.
6. **Name the style for what it RENDERS.** The `name` string is printed over the preview and
   may not mention an axis outside `RENDERED_AXES`.
7. **Build and show.**

```bash
npm run build
```
```bash
python3 scripts/build_board_previews.py <slug>
```
```bash
python3 scripts/build_page_board.py <slug>
```

The board is the deliverable: `docs/artifacts/boards/<slug>.html`, published as an Artifact
with copy buttons. Judgment rule 10 — a visual decision is shown in a browser, never
described in words alone.

8. **Measure, do not assert.** `npm run test:render:pages` measures at 375 / 768 / 1280 in a
   real browser; `scripts/measure_canvas_heights.mjs` measures the hero band, the lede's own
   overflow and the CTA row's bottom edge. A probe that reports a PASS having measured zero
   blocks is the exact failure `.claude/skills/bsuk-gate-integrity/SKILL.md` exists to catch
   — read the examined count before believing the verdict.
9. **Critique, harden, refine** — the three lenses, in this order:
   - **Critique** — brand register, hierarchy, cognitive load, affordance, copy fit, and
     honesty: does the arrangement imply something the page does not actually carry.
   - **Harden** — horizontal overflow, box fit, hit targets, text size, contrast sweep at
     each width, well-formedness.
   - **Refine** — type scale, spacing rhythm, one primary CTA per section, alignment.
10. **The breeder picks one per section.** `python3 scripts/board_approve.py <slug>` records
    it; `python3 scripts/board_gate.py <slug>` refuses to let a page be built from a record
    with an unpicked style.

## 5. Adding a variation to the style map — the checklist

| Step | File | What must be true afterwards |
|---|---|---|
| Add or edit the three defs | `src/lib/boardStyles.ts` | they differ on a rendered axis |
| Add the axis, if it is new | `src/lib/boardStyles.ts` | it is in that shape's `RENDERED_AXES` row |
| Give the axis a neutral value | `src/lib/boardStyles.ts` | unless it is a PROP, not a class |
| Paint the class | `src/styles/board-styles.css` | the preview and the page resolve the same rule |
| Render it | `src/pages/board-preview/[slug].astro` | every style id emits a block |
| Hold it | `tests/py/test_board_previews.py` | distinctness, and the built blocks differ |

A `play`-style axis that is a PROP rather than a class is the exception worth knowing: two
arrangements that are different MARKUP — a button and a thumbnail against an iframe — are
something no stylesheet can turn into the other, so they are handed to the component and are
deliberately absent from the neutral map.

## 6. Parallel authoring

Authors write **disjoint files**: one author per shape or per page type, each touching its
own block of `src/lib/boardStyles.ts` and its own record. **No author commits.** The
controller merges, rebuilds the previews and the boards, runs the gates and commits. Run
every `git` command from the repo root, and stage with an explicit path list — a bare
`git add -A` on this repo stages the generated pages and the gitignored preview payloads'
siblings along with the work.

## 7. What NOT to do

- A palette change as a variation. The axis is layout, accent role, motif, container or
  density.
- A style whose three options render identically. That is a fieldset with no question in it.
- An axis no renderer reads.
- A hero variation that meets the 450px ceiling by hiding its overflow. The clamp crops the
  PHOTO; it is not a guillotine across the copy, and a hero that lost its CTA row would
  still measure as a pass.
- A counter tile with a number nobody can source.
- A default prop that asserts a credential, a price or a claim. Optional, and empty.
- Copy lifted from a sibling page. Judgment rule 8: reuse components freely, write prose
  from the page's own outline.
- A fourth arrangement of the dial, the sheet or the strip.
- Measuring in a hidden browser pane. It reports a zero viewport, which fakes a horizontal
  overflow defect on every block.

## 8. Record

- `src/lib/boardStyles.ts` — the style map, and the comment at its head is the contract.
- `src/styles/board-styles.css` — what the classes resolve to.
- `data/boards/index.json` — the homepage board, the worked example.
- `data/boards/_demo.json` — the fixture the preview route, the cutter and their tests
  render; it is not a page.
- `docs/superpowers/specs/2026-09-16-system-transfer-design.md` — where the board system
  came from and why it replaced the canvas.
