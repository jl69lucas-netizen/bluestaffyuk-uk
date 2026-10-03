---
name: bsuk-infographic
description: Builds BlueStaffyUK infographics in the five named styles of IMAGE-DESIGNS.md §8 — IG-1 Stat Panel, IG-2 Process Steps, IG-3 Comparison Split, IG-4 Checklist Grid, IG-5 Route Map — as token-only HTML/CSS (the default) or as a baked raster framed with Style A. Picks the style from the heading's intent, uses only locked facts, and puts the style pick on the page board for approval. Use when a board slot's source is "infographic".
allowed-tools: [Read, Write, Bash]
---

# BSUK Infographic

**Announce at start:** "Using bsuk-infographic for [page slug] — [slot heading], style [IG-n]."

> **Image art-direction:** Read `IMAGE-DESIGNS.md` (repo root) first. §8 defines the styles,
> §9 the approval, §10 the slot fields. It wins over anything here.

## When to use

A board slot whose `source` is `infographic`: the section is figures, steps, a comparison, a
checklist or a journey, and a picture of it says more than a photo would.

## Pick the style from the heading's intent

| Heading intent | Style | Typical heading |
|---|---|---|
| cost, price, how much, how many | IG-1 Stat Panel | "What a Blue Staffy Costs to Bring Home" |
| how to, steps, what happens, timeline | IG-2 Process Steps | "How Collection Day Works" |
| versus, difference, which is better | IG-3 Comparison Split | "Blue Staffy vs Brindle Staffy" |
| checklist, what to check, what to bring, signs of | IG-4 Checklist Grid | "What to Check Before You Pay a Deposit" |
| delivery, collection, travel, where | IG-5 Route Map | "Delivery From Carlisle to Leeds" |

A comparison page carries IG-3 in at least one H2; a location page's delivery section is
IG-5 (IMAGE-DESIGNS.md §5).

## Facts on an infographic

Every figure comes from `data/*.json` or a cited source (CLAUDE.md rule 9): prices from
`data/price-matrix.json`, the deposit and delivery band from `data/settings.json`. IG-5 shows
the locked band (£200–£350 by distance, by DEFRA-approved transport) and collection in
Carlisle, never a mileage or drive time nobody measured. No figure, no infographic.

## Size

Width by page type, from design rule 9 in `rules/design.md`: a 760px wrapper for blog, guide
and care pages; 1100px for home, location and hero sections. 400px tall on desktop (380 to
450), `height:auto` on mobile, where every layout stacks. Stack at 640px for the 760 wrapper
and 767px for the 1100 wrapper.

## Mode

- **HTML/CSS (default).** Token-only markup: every colour is a `var(--color-…)` from
  `src/styles/tokens.css`, never a hex (design rule 1); no `font-family` (the global type
  applies); line-icon SVGs, never emoji (design rule 7); no heading tags inside the graphic,
  so the page's outline gate is untouched. Text colours use only the pairs in
  `data/design/contrast.json`: brass text sits on steel and only at large size.
- **Raster.** When the breeder wants a picture file, render the same design (Type 4 below):
  it is a generated image, so it goes through the draft, second board pass and publish of
  IMAGE-DESIGNS.md §9, framed with Style A so no baked text is cropped.

## Board styles, frame heights and baking (`scripts/infographic_plan.py`)

On a project 5 board, block 7c offers each infographic slot in three playful styles: the
breeder's ruling q08 (2026-10-02) asked for "nice, playful, cartoonish". All three use the
site tokens only (steel, bone, brass), and every figure is exact text, never drawn:

- **sticker:** white die-cut cards with thick ink outlines and hard offset shadows, brass
  number badges, and the doodle-dog mascot (a friendly Staffy with rose ears and no collar).
- **chalk:** a sketchbook on bone graph paper, with wobbly hand-drawn outlines (the SVG filter
  touches lines only, never text), wavy brass underlines and highlighter swipes.
- **comic:** heavy-bordered panels, the dog saying the title in a speech bubble, brass
  caption boxes, speech-bubble labels and halftone corners.

The pick is `ig:<slot>` = `sticker` | `chalk` | `comic` (`pageboard.V2_PICKS`).

**Commands. They need node plus Playwright's Chromium** (`npx playwright install chromium`):

```bash
python3 scripts/infographic_plan.py <slug> --write     # write the previews, then measure heights
python3 scripts/infographic_plan.py <slug> --heights   # re-measure only
python3 scripts/build_page_board.py <slug>              # board frames sized from heights.json
```

- **What the measuring writes.** `scripts/ig_shots.mjs` renders every preview at 1280, 768
  and 375 with the fonts served. It writes
  `docs/artifacts/boards/ig/<slug>/heights.json`, which holds each frame's height plus each
  preview's sha256.
- **Freshness.** A preview edited without re-measuring fails
  `test_heights_json_is_not_stale`.
- **Without Chromium.** `--write` deletes that file (the board falls back to scrolling
  frames) and exits 2.

**The `.fig` gate.** Every exact figure (a price, the band, a city) carries `class="fig"`. The
measurement fails (`FigureDefect`, exit 3, nothing written) when any figure's text overflows
its box or card, or touches an icon box, at any width. Icons get a reserved corner, figures
get their own line, and a figure in a narrow card drops a type step.

**Bake after the pick, one style per slot.**
`infographic_plan.bake_infographic(slug, slot, style)` crops the PICKED style to its figure
twice: once at the width that fills the 1408×768 box, once as the 760-wide phone layout. It
writes the two lossless masters (`<slug>-<slot>-<style>.png` and `-760.png`) and refuses a box
covered under 85% or phone text under 14px. Draft them together with
`ingest_image.py draft <box> --infographic IG-n --sibling <phone>`; it runs at Task 9 or STOP 4.
Never bake the unpicked styles.

## IG-1 Stat Panel

```html
<!-- BSUK Infographic: IG-1 Stat Panel | <slug> | height: 400px -->
<div role="img" aria-label="[TITLE]" style="background:var(--color-surface-inverse);color:var(--color-text-on-inverse);border-radius:var(--radius-md);box-shadow:var(--shadow-card);min-height:380px;max-height:450px;display:flex;flex-direction:column;padding:var(--space-5)">
  <p style="margin:0 0 var(--space-4);font-size:var(--text-lg)">[TITLE]</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:var(--space-4);flex:1;align-content:center">
    <div><p style="margin:0;font-size:var(--text-4xl);color:var(--color-cta)">[FIGURE]</p><p style="margin:0;font-size:var(--text-sm)">[ONE LINE OF CONTEXT]</p></div>
    <!-- two to four figures -->
  </div>
</div>
```

## IG-2 Process Steps

```html
<!-- BSUK Infographic: IG-2 Process Steps | <slug> | height: 400px -->
<div role="img" aria-label="[TITLE]" style="background:var(--color-surface);border:var(--card-border);border-radius:var(--radius-md);box-shadow:var(--shadow-card);min-height:380px;max-height:450px;display:flex;flex-direction:column">
  <p style="margin:0;background:var(--color-surface-inverse);color:var(--color-text-on-inverse);padding:var(--space-3) var(--space-4);text-align:center">[TITLE]</p>
  <ol style="list-style:none;margin:0;padding:var(--space-4);display:flex;flex-wrap:wrap;gap:var(--space-3);flex:1">
    <li style="flex:1 1 120px;text-align:center;border-top:2px solid var(--color-brand-mid);padding-top:var(--space-3)">
      <span style="display:inline-flex;width:36px;height:36px;border-radius:50%;background:var(--color-brand);color:var(--color-text-on-inverse);align-items:center;justify-content:center">[N]</span>
      <p style="margin:var(--space-2) 0 0;color:var(--color-text)">[STEP]</p>
      <p style="margin:0;font-size:var(--text-sm);color:var(--color-text-muted)">[ONE LINE]</p>
    </li>
    <!-- three to five steps -->
  </ol>
</div>
```

## IG-3 Comparison Split

```html
<!-- BSUK Infographic: IG-3 Comparison Split | <slug> | height: 420px -->
<div role="img" aria-label="[TITLE]" style="border-radius:var(--radius-md);overflow:hidden;box-shadow:var(--shadow-card);min-height:380px;max-height:450px;display:flex;flex-direction:column">
  <div style="display:grid;grid-template-columns:1fr 1fr;flex:1">
    <div style="background:var(--color-brand-soft);padding:var(--space-4)">
      <p style="margin:0 0 var(--space-3);color:var(--color-brand)">[SUBJECT A]</p>
      <p style="margin:0;color:var(--color-brand)">[ATTRIBUTE]: [VALUE]</p>
    </div>
    <div style="background:var(--counter-bed);padding:var(--space-4)">
      <p style="margin:0 0 var(--space-3);color:var(--color-text)">[SUBJECT B]</p>
      <p style="margin:0;color:var(--color-text)">[ATTRIBUTE]: [VALUE]</p>
    </div>
  </div>
  <p style="margin:0;background:var(--color-surface-inverse);color:var(--color-text-on-inverse);padding:var(--space-3) var(--space-4);text-align:center">[VERDICT]</p>
</div>
```

## IG-4 Checklist Grid

```html
<!-- BSUK Infographic: IG-4 Checklist Grid | <slug> | height: 420px -->
<div role="img" aria-label="[TITLE]" style="background:var(--color-surface-inverse);color:var(--color-text-on-inverse);border-radius:var(--radius-md);box-shadow:var(--shadow-card);min-height:380px;max-height:450px;padding:var(--space-4);display:flex;flex-direction:column">
  <p style="margin:0 0 var(--space-3);text-align:center">[TITLE]</p>
  <ul style="list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:var(--space-2);flex:1">
    <li style="display:flex;gap:var(--space-2);align-items:flex-start"><span aria-hidden="true" style="color:var(--color-cta);font-size:var(--text-xl)">✔</span><span>[CHECK]</span></li>
    <!-- six to twelve cells -->
  </ul>
</div>
```

## IG-5 Route Map

A schematic, never map tiles: a straight or gently curved line from Carlisle to the
destination city, with the two names and the locked band.

```html
<!-- BSUK Infographic: IG-5 Route Map | <slug> | height: 400px -->
<div role="img" aria-label="Delivery from Carlisle to [CITY]" style="background:var(--color-surface);border:var(--card-border);border-radius:var(--radius-md);box-shadow:var(--shadow-card);min-height:380px;max-height:450px;padding:var(--space-5);display:flex;flex-direction:column;justify-content:center">
  <svg viewBox="0 0 600 160" width="100%" aria-hidden="true">
    <path d="M60 110 C 220 20, 380 20, 540 110" fill="none" stroke="var(--color-brand)" stroke-width="4" stroke-dasharray="10 8"/>
    <circle cx="60" cy="110" r="12" fill="var(--color-cta)"/>
    <circle cx="540" cy="110" r="12" fill="var(--color-brand-mid)"/>
  </svg>
  <div style="display:flex;justify-content:space-between;color:var(--color-text)"><span>Carlisle</span><span>[CITY]</span></div>
  <p style="margin:var(--space-3) 0 0;text-align:center;color:var(--color-text)">UK home delivery £200–£350 by distance, by DEFRA-approved transport, or collection in Carlisle</p>
</div>
```

## Type 4: AI-Rendered Infographic

The older "Type 1, 2, 3" names map onto the styles: Type 1 Comparison is IG-3, Type 2
Feature Grid is IG-4, Type 3 Process Flow is IG-2. Type 4 is a raster rendering of any IG
style: build the design as HTML first, then render it by the `bsuk-image-generation` route
(or a screenshot of the approved HTML), check every figure against its source, and bake the
draft:

```bash
python3 scripts/ingest_image.py draft "<master.png>" --board <slug> --slot <slot> --infographic IG-3
```

The board's second pass approves it as `ig:IG-3:<sha12>`; then
`python3 scripts/ingest_image.py publish --board <slug> --slot <slot> --stem <seo-stem>` copies
those bytes unchanged into `public/images/`. A bare `ig:IG-<n>` pick approves the style only.

## Type 5: Higgsfield Reference

Only when the Higgsfield connector lists an image-generation tool in the session (find it
through ToolSearch; ask before any paid call). Same prompt rules as Type 4; same draft,
approval and publish.

## Integration Checklist

- [ ] Style picked from the heading's intent, and the pick is on the board (IMAGE-DESIGNS.md §9).
- [ ] Every figure traced to `data/*.json` or a cited source; no invented number.
- [ ] Token colours only; no hex, no `font-family`, no emoji, no heading tags inside.
- [ ] Brass text only on steel, only large.
- [ ] Width 760 or 1100 by page type; 380 to 450px tall on desktop; stacks on mobile.
- [ ] `role="img"` and an `aria-label` that states the graphic's point.
- [ ] A raster version drafted with `--infographic IG-n`, approved by its sha12, then published.
- [ ] The slot's `infographic_style` matches the style built.

> **Image designs:** `IMAGE-DESIGNS.md` (repo root) names the OG framing styles (§7: A, B, C, D, E, H), the infographic styles (§8: IG-1 to IG-5), the approval rule (§9: nothing generated is built until the board approves its exact bytes) and the image-slot fields and picks (§10: `source`, `file`, `source_file`, `og_style`, `infographic_style`, `prompt`, `img:<slot>`). Read it before choosing, generating, framing or placing an image; on conflict it wins.
