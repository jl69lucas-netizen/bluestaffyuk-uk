# Manchester Component Variants — Design and Hardening Log

One section per task (Tasks 22–25, then `## Built — Task <n>`): the frontend-design direction
each variant came from, what the impeccable pass found, what changed, and the widths it was
checked at (375 / 768 / 1280). Plan: `docs/superpowers/plans/2026-10-07-manchester-page-run.md`,
Phase F. Contract: `docs/research/manchester-components/README.md`.

## Task 22: hero, counter strip, trust strip (2026-10-07)

**How the passes ran.** `frontend-design:frontend-design` was invoked with the Skill tool on the
plan's Step 2 brief (batch: hero, counter-strip, trust-strip; pool slot `c` of trust-strip only).
First, every cited sheet was opened with the Read tool: the five hero sheets, the five counter
sheets, `hero-idea-1.png` and the MFS trust sheet. The outline rows §1–§3 were read too. The
fonts and colours are the fixed BSUK tokens, so each variant is distinct in structure, not in
palette. The skill's generic-design tells were avoided on purpose: no italic accent word in the H1
(several sheets use one), no all-caps eyebrows, no middle-dot meta strings, no arrows in CTAs.
Outline §2 and §3 carry no headings, so neither strip adds an H2.

`impeccable:impeccable` was then invoked with the Skill tool (brand register; `critique`). Its
loader reported `hasProduct: false`. There is no `PRODUCT.md`, and only `/impeccable teach`, run
interactively with the user, may write one. So, as in London's log, the brand context came from
the design-context files (`rules/design.md`, `src/styles/tokens.css`, `src/styles/city.css`,
`data/design/contrast.json`, the README contract). Both assessments ran, one after the other in
this agent:
- the deterministic detector, `npx impeccable --json` on the nine fragments. Its only rows were
  26 `cramped-padding` hits, every one a false positive: jsdom does not resolve the stylesheet
  padding on the inner wrappers, and the shots show every child inset.
- a painted review of 36 shots (9 frames at 375 / 768 / 1024 / 1280, Playwright, Chromium).

The smoke's two `img-face-visible` advisories (Roman1 at every width, Vennie at 375) were folded
into that review.

| Component | Variant | frontend-design direction | impeccable findings | Fixed | Widths |
|---|---|---|---|---|---|
| hero | a | **Print board** (`hero-idea66.png`). Four tilted prints of the litter, four coats (Ince blue, Roman blue and white, Christa blue, Byrd white), captioned in two offset columns on the bone page. The prints come first in source: 2x2 on phones, four across at tablet, right of the copy from 1024. | Roman's caption wrapped to two lines, so the prints were uneven. Roman1's face sat in a 3:2 cover crop (advisory). At 1280 the board was small and far from the copy. | Each caption is now name over coat (serif italic name, small sans coat), so every print is the same height. Roman1 is cropped at 50% 28%. The columns are 1fr/1fr and the board widens to 440px at a 16:10 crop. Band 440px at 1024/1280. | 375 · 768 · 1024 · 1280 |
| hero | b | **Coat pair** (`comparison-hero-idea1.png`). The H1 answered in a picture: Christa (blue) and Vennie (blue and white), two girls at staggered heights with an "or" badge, and a line saying both are £1,700. The coat changes; the price does not. Framed only by hairline rules. | At 375, "Vennie, blue and white" wrapped inside its pill and the pills sat on the faces. At 768 the pair was centred while the copy below sat left. "Two coats … £1,700." left an orphaned price at 375. The lede said "Here in Carlisle the price follows…", which reads as a kennel-wide rule, not this litter (q09). | Below 640 the captions sit under the photos as plain text. At 640–1023 the pair is left-aligned. The price line takes `text-wrap: balance`. The lede now reads "In our Carlisle litter the price follows boy or girl". Band 392 / 402px. | 375 · 768 · 1024 · 1280 |
| hero | c | **Feature and three** (`hero-idea77.png`, `hero-idea-5.png`). Roman large, bled to the screen's left edge with a caption pill, and Cheryl, Ince and Vennie stacked beside him. The copy sits right, with a hairline tick row: Raised in our home, Two-year health guarantee, Support after collection. | At 768 the photo block ran about 570px before the heading, which made the section 972px tall. Vennie's caption covered 11% of her face at 375 (advisory). | The photo block is capped at 360px from 640 to 1023, so the section is now 754px at 768. Thumbnail captions moved to the bottom-right corner, off the faces. Band 420px. | 375 · 768 · 1024 · 1280 |
| counter-strip | a | **Tally box** (`hero-idea-3.png`, `hero-idea77.png`). Four figures in one box drawn with hairline rules on the counter bed: 6 puppies available now, £1,500 for each boy, £1,700 for each girl, £200–£350 delivery. Serif figure over a sentence-case label. 2x2 on phones, four across from 800. | The gradient seam over a big-figure, small-label row matched impeccable's banned hero-metric template. The delivery label ran to three lines at 375. | Seam replaced by a 2px steel rule plus the tone shift, which still meets the hero/counter separation rule. The label is now "delivery to Manchester, priced by distance", and the note carries "UK home delivery by DEFRA-approved transport, or collect … in Carlisle". | 375 · 768 · 1024 · 1280 |
| counter-strip | b | **Range sheet** (`component-idea-modern.png`, `hero-idea.png`). A white sheet of labelled cells, with the six puppies' faces set in a row beside the "6". The delivery band is drawn as a £200-to-£350 range bar in the seam colours, because a band priced by distance is a range. | The smoke failed it at 1280: media was declared `inline`, but the face row sat inside a `data-figure` item, so it counted as the item's image, not the section's. | `data-figure` moved from the cell to the figure's own span, so the face row is section-level. 4 figures; the axes now match the paint. | 375 · 768 · 1024 · 1280 |
| counter-strip | c | **Stat block and rows** (`component-idea44.png`). The litter count leads, set large on a steel block that bleeds to the left screen edge with its label at body size. The prices and delivery band follow as ruled price-list rows. Airy. | Checked against the hero-metric ban: the lead label is 17px body copy, not a small label; the rows are a list, not stat tiles; there is no gradient. Contrast: bone on steel-700 is AA. | None needed. | 375 · 768 · 1024 · 1280 |
| trust-strip | a | **Tick run** (`hero-idea-5.png`, `hero-idea00.png`). The eight items, the seven `puppy_trust_signs` verbatim plus `guarantee_label`, as one wrapping run of ticked words under a serif lead, ruled above and below. | At 375 the run broke raggedly, one item on a line in some places and two in others. | Below 640 the run is one column. It wraps as a run from 640. | 375 · 768 · 1024 · 1280 |
| trust-strip | b | **Puppy folder** (MFS trust sheet, `hero-idea00.png`). The five papers and records drawn as paper slips in a tabbed brass-tint folder, with "And from us" (home, support, guarantee) beside it, inset in one soft steel panel. | Contrast pairs checked: text on raised slips, brand on cta-soft (the tab), text and brand on brand-soft. All are in `contrast.json`. Height at 375 is 728px: eight items in two groups, accepted for an airy variant. | None needed. | 375 · 768 · 1024 · 1280 |
| trust-strip | c | **Seal sheet**, the pool copy of `london/trust-strip/b` "Seal band". Refresh delta, axis **layout**: London's centred kicker over one six-across row becomes a kicker column beside a 4x2 sheet of eight seals. Manchester copy uses the eight trust items only; London's vet, take-back and Puppy Culture lines are dropped because they are not in ruling 10's facts. | At 375 the 2x4 stack of centred seals ran 679px tall. | Below 640 each seal sits left of its label, as compact rows in two columns (409px at 375). From 640 it is the 4x2 sheet. | 375 · 768 · 1024 · 1280 |

Copy checks common to all nine:
- The H1 is the outline's, verbatim, followed by a 12+ word answer ("Not on its own").
- Prices are said of this litter only.
- No deposit wording appears, so no refund clause is needed.
- The guarantee appears only as `guarantee_label` ("Two-year health guarantee").
- No video call, rescue, licence, distance or time, rating or review. No phone number. No em
  dashes in visible copy.
- Every puppy alt names the puppy and Carlisle. No served `/images/` file is used, so no
  served alt is at stake.
- Every photo box is reserved (width/height plus `aspect-ratio`). Bleeds and letterboxes are bone
  or steel-100.

Final runs: `python3 scripts/check_city_canvas.py --city manchester --only
hero,counter-strip,trust-strip` gave `examined 9 fragments, 3 meta files; 0 problems`, and the
canvas smoke (`manchester-frames`) gave 40 passed at vp375, vp768, vp1024 and vp1280, with no
advisories.
