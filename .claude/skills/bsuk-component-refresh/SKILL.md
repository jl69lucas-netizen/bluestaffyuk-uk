---
name: bsuk-component-refresh
description: "Use when building or rebuilding any BlueStaffyUK page in a cluster (the buy/for-sale set, the guide set, the location pages, the blog cluster, the interior pages) to give each page a controlled \"refresh delta\" — a small, deliberate layout / accent-role / motif variation per section — so sibling pages do not read as one template with the words swapped, WITHOUT touching the locked palette tokens, the pill CTA, the hero clamp, the decided chrome or the verbatim set. Triggers: \"refresh the components\", \"make this page look different from the built ones\", \"component refresh\", \"the pages all look the same\", \"differentiate the hero/counter/table\", working rule 16."
---

# SKILL: BSUK Component Refresh (the "Refresh Agent")

**The problem this solves.** Eleven rich pages are built from one kit
(`src/components/kit/`) and one style map (`src/lib/boardStyles.ts`). Left alone they drift
toward being *the same page with the words swapped* — identical hero, identical counter
strip, identical takeaway cards, identical table chrome. Working rule 16 makes the hero and
the counter strip per-page by construction; this skill covers **every other section**, where
the delta is small and deliberate rather than a new design.

**The rule.** A refresh is **layout OR accent-role OR motif/density**, section by section —
**never a palette change**. Change how the same tokens are arranged, never the tokens.

**Where a refresh is recorded.** On the board record, per section, as
`refresh: {axis, note}` (`schemas/board.schema.json`). The board shows it, the breeder
approves it with the style pick, and the rebuilt page reads it back. A refresh that is not
on the record is not a refresh, it is drift.

---

## 0. Invariants that NEVER refresh (breaking one is a FAIL, not a variation)

A refresh works *around* these, never through them.

1. **Palette tokens.** Steel / brass / bone, defined once in `src/styles/tokens.css` as a
   three-layer `@theme` block. A hex anywhere else under `src/` fails
   `tests/py/test_design_tokens.py`. There is one accent, `--color-cta`; brass on bone is
   below the AA floor, so brass never carries small text on a light bed.
2. **Type.** Fraunces for display, Source Sans 3 for body, both as `--font-display` /
   `--font-body`. No hard-coded `font-family`, ever.
3. **The pill CTA.** Primary buttons take `--btn-radius` (the pill); cards take
   `--card-radius`. A refresh may change which button leads a section, never its shape.
4. **The hero clamp — rules/design.md rule 10.** The hero photo PRECEDES the copy in source
   order, and at 1024px and up the band is held between 390px and 450px with nothing
   clipped: the copy is sized to fit and only the photo is cropped. Every per-page hero
   style in `HERO_STYLES_BY_PAGE_TYPE` is measured against that clamp by
   `scripts/measure_canvas_heights.mjs`, and a layout that meets it by hiding overflow has
   failed it.
5. **Hero / counter separation.** A tone shift AND a rule between the hero and the counter
   strip below it — `rules/design.md` asks for both, and a strip carrying only one of them
   reads as hero furniture, at which point the figures stop registering as claims.
6. **The three chrome components are decided.** `PageDial`, `SectionSheet` and
   `SectionStrip` were picked on the contact board (2026-09-19) and pruned to one
   arrangement each. They are in-page navigation, not a stretch of page: they are identical
   on every page by design and are never a refresh target.
7. **Tables stack below 640px** — working rule 13, in every chrome arrangement. Stacking is
   not on the refresh menu; what differs above that breakpoint is.
8. **Images and videos keep their URLs and ids** — working rules 11 and 14. A refresh moves
   a photo's side or its bed; it never renames, re-encodes or replaces the file, and it
   never mints a YouTube id.
9. **The verbatim set** — working rule 15. The migrated page's H1, its keyword H2/H3s, the
   first paragraph under each, the FAQ questions and every image alt are carried word for
   word. A refresh is a visual layer: it may move a heading, never reword one.
10. **The facts and links gates.** Every figure comes from `data/*.json` or the record
    (working rule 9), and every link is on the approved board (working rule 12). A refresh
    that adds a card adds no claim and no href.
11. **Heading hierarchy.** The H1 outranks every H2 at every width; no skipped levels.
    `rules/headings.md` and the render harness own this, and a layout change is the usual
    way it breaks.

## 1. The refresh budget — do NOT refresh everything

**Refresh three to five sections meaningfully per page; leave the rest consistent.** The
total drift should read as *a different editorial rhythm*, not a different website.
Over-refreshing destroys the cohesion the kit exists to give and doubles the QA; under-
refreshing (nought to two) is the complaint this skill was written for. The hero and the
counter strip are refreshed by construction under working rule 16 and do **not** spend
budget — pick the page's two or three highest-scroll sections to carry the rest.

## 2. Refresh dimensions — pick exactly ONE per refreshed section

| Dimension | What changes | Worked example on this kit |
|---|---|---|
| **Layout** | column count, media side, band vs card vs plain bed, aside vs inline | a `standard` section from photo-right to photo-top over two columns |
| **Accent role** | which locked token leads — steel band vs bone surface, brass as a rule vs brass as a fill | a `takeaways` block on the steel band on one page, on bone with a brass hairline on the next |
| **Motif** | the visual metaphor of a callout or a figure | delivery as a band of distance chips on one page, as a two-row ledger on another |
| **Container** | card shell vs full-bleed band vs plain surface, border vs lift | `faq` in a card with a jump list, or full width under the heading |
| **Density** | compact vs airy, inline chips vs stacked rows | `trust` as one flush line, or as a three-up grid with room around it |

`axis` on the record's `refresh` block is one of these five words: `layout`, `accent`,
`motif`, `container`, `density`. `note` is one sentence saying what the delta is and which
sibling page it is a delta *from*.

## 3. The section ledger — a rotation, so no two siblings ship the same treatment

Each recurring shape keeps two to four interchangeable treatments. The three ids in
`src/lib/boardStyles.ts` are the menu; this ledger says which one a page should reach for
and why, and the board record's `refresh.note` says which sibling it is departing from.

### Hero (`hero`) — per page type, working rule 16
Not a rotation: `HERO_STYLES_BY_PAGE_TYPE` in `src/lib/boardStyles.ts` gives each page type
its own three structurally different arrangements, and no two page types share a set. The
refresh work here is choosing which of the three, and the clamp in §0.4 is the gate.

### Counter strip (`stats`) — per page type, working rule 16
`COUNTER_STYLES_BY_PAGE_TYPE`, same construction. The FIGURES are the page's own, each with
a `source` path into `data/*.json` that a test resolves. Fewer tiles is always correct;
an invented tile never is.

### Takeaways (`takeaways`)
- **A. Stacked statement cards** — calm, reads as a summary.
- **B. Three-up grid on the steel band** — the loudest option; one page per cluster.
- **C. Rail of cards beside the heading** — for a section whose heading carries the keyword.

### Prose (`standard`)
- **A. Photo right of the prose** — the default; do not spend it twice in a cluster.
- **B. Photo full width above two columns** — for a section with a landscape master.
- **C. Band with an InfoCard aside** — for a section that carries a caveat.

### Puppies (`puppies`)
- **A. Three-up card grid**, **B. two-up beside the heading**, **C. rail on a band.** The
  rail is the only one that survives a litter of two without looking empty.

### Reviews (`reviews`)
- **A. One review given room** (a page with one strong review), **B. a grid on a band**,
  **C. a grid beside the heading.**

### FAQ (`faq`)
- **A. Full-width accordion**, **B. heading and intro beside it**, **C. in a card with a
  jump list.** C is for a page with more than about eight questions.

### Table (`table`) — chrome only
- **A. Ruled rows under a brand header band**, **B. zebra rows in a card**, **C. borderless
  rows with brass column rules.** All three stack below 640px (§0.7).

### Video (`video`)
- **A. Player in a card**, **B. player on a steel band**, **C. thumbnail facade.** C ships
  unless the board says otherwise: it is the only one that does not load a player before
  anybody asks for one.

### Trust (`trust`) and divider (`divider`)
The quietest two. Use them to *absorb* drift: when a page has spent its budget, these stay
on the cluster default so the page still reads as part of the system.

## 4. Process — run this BEFORE writing page code

1. **Audit the siblings.** For the cluster the page joins, list what each built sibling used
   per recurring section. The board records are the record: `data/boards/<slug>.json`.
2. **Set the budget.** Three to five signature sections. Hero and counter are already
   per-page and are not counted.
3. **Pick from the ledger** — a treatment neither of the two nearest siblings owns.
4. **Show the refresh matrix**: section · sibling treatment · this page's treatment · axis ·
   why, and the trade-off of the recommended one (judgment rule 4). Show it RENDERED on
   `/board-preview/<slug>/`, never described in words (judgment rule 10). Get approval
   before code (judgment rule 6, preview before apply).
5. **Write it to the record** as `refresh: {axis, note}` on each refreshed section, rebuild
   the previews and the board, and re-approve.
6. **Apply.** The rebuilt page calls the same `boxClass()` the preview called, so what was
   approved is what ships. Re-measure the hero clamp, because the layout changed.

## 5. Pass gates (the standing chain, plus two of this skill's own)

```bash
npm run check:all
```
```bash
npm run test:py
```
```bash
npm run test:render:pages
```

Plus, for the page that was refreshed:

```bash
python3 scripts/board_gate.py <slug>
```
```bash
python3 scripts/verbatim_set_check.py <slug> --check
```
```bash
python3 scripts/dup_content_audit.py --headers
```
```bash
python3 scripts/final_page_audit.py
```

A refresh must not reintroduce duplicate copy (a layout change is a common way a heading
gets re-typed), and `scripts/measure_canvas_heights.mjs` must still report the hero inside
its clamp with nothing clipped. Read `rules/gates.md` first: a gate's output is a hypothesis
about the page, and a PASS whose examined count is zero is not a pass.

## 6. What NOT to do

- A palette change dressed as a variation. The axis is layout / accent-role / motif /
  container / density, never colour.
- A refresh that adds or removes content. Judgment rule 6: a redesign is the visual layer
  only, and a new card with a new claim is a content change that never went past the board.
- A figure typed by hand. Every counter tile carries a `source`; where nothing on disk backs
  a figure the page ships fewer tiles.
- Refreshing the dial, the sheet or the strip. Decided 2026-09-19 (§0.6).
- Refreshing ten sections because five felt timid. That is a redesign, and it belongs in its
  own board.
- A heading reworded to fit a narrower column. Working rule 15 carries the wording; the
  layout bends around it.

## 7. Reuse beyond one cluster

The ledger above is written for the eleven rich pages, but the **method** — invariants,
budget, dimension, matrix, record, log — is what transfers. The location pages
(`data/locations.json`) and the blog collection rotate the same way: add a per-cluster
ledger section here when a new cluster starts being differentiated, and keep the rotation in
the records rather than in someone's memory.
