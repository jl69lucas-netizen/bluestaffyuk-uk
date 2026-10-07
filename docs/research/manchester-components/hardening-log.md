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

## Task 23: contents list, desktop dial, jump links (2026-10-07)

**How the passes ran.** `frontend-design:frontend-design` was invoked with the Skill tool on the
plan's Step 2 brief (batch: contents-list, desktop-dial, jump-links; pool slot `c` of each).
First, every sheet the ideas index cites for the three components was opened with the Read tool:
`component-idea44.png`, `card-with-image.png`, `component-idea2.png`, `component-idea3.png`,
`component-idea-modern.png`, `modern-faq-idea.png`, `puppy-card-with-filter-idea-1.png`, and
London's eight captures under `BSUK-refs/london/{contents-list,desktop-dial,jump-links}/`. The
outline's 13 H2s were read too. Outline §4 carries no heading, so no nav variant adds an H2: each
names itself in a `<p>` title. Every stand-in section the dial and jump frames scroll through
carries the outline's own H2, word for word, sized by the outline's word count for it.

Pool picks (Phase F ruling 4: furthest from London's pick, and suited to 13 sections):
- contents-list `c` ← `london/contents-list/b` "Three stages". `a` "Ruled index" was the other
  candidate, but contents A already makes a ruled, numbered question index.
- desktop-dial `c` ← `london/desktop-dial/a` "Page map". "Clock face" would put 13 stops round a
  232px ring, which is too crowded.
- jump-links `c` ← `london/jump-links/b` "Drop panel". "Photo pager" needs one photo per section,
  and 13 photos with unique alts are more than the strip should carry.
- All three differ from London's pick on all four axes.

The three stages are page-order runs of four (sections 1–4, 5–8, 9–12, then the enquiry). The
same stages are reused by contents C and jump links A and C, so the page has one way of dividing
itself.

`impeccable:impeccable` was then invoked with the Skill tool (brand register; critique). Its
loader reported `hasProduct: false`, and `/impeccable teach` is interactive and the user's, so
the brand context came from the design-context files, as in Task 22. The two assessments ran in
isolation:
- **A.** A separate review agent read the nine fragments, the metas and 36 painted shots
  (375 / 768 / 1024 / 1280). Nielsen total 28/40.
- **B.** The deterministic detector, `npx impeccable --json` on the three folders. Its only rows
  were 195 `cramped-padding` hits (35 distinct), all false positives of the kind Task 22
  recorded. jsdom reads ruled list items as "children flush against border-top/bottom", but on
  the shots every link carries its own 8–16px padding and the rule is a separator, not a box.

This agent also painted the states the full-page shots cannot show: each jump sheet opened at
375 and 768, each strip after a 1400px scroll, each dial after a 2600px scroll at 1280, and the
contents disclosures opened.

| Component | Variant | frontend-design direction | impeccable findings | Fixed | Widths |
|---|---|---|---|---|---|
| contents-list | a | **Question index** (`component-idea44.png`, comparison capture). The 13 outline H2s, word for word, are the contents list. Display face, numbered in page order (a real sequence), ruled rows under one steel rule; two columns of seven from 800px. | At 375 six display-face questions ran to about 700px before any content. "Tap a question" was shown on desktop too. Every link is in the source twice (the `li.rest` rows plus the disclosure copy), as in London's ruled index. | Phones show four questions at 15px, then a "9 more questions" disclosure. The hint now reads "Choose a question to jump to its answer." The duplicate links are kept for the CSS-only canvas; the kit build renders the list once. | 375 · 768 · 1024 · 1280 |
| contents-list | b | **Icon rows** (`component-idea2.png`, `card-with-image.png`). One raised card: line-icon rows divided by rules, and Manchester's own served puppy photo (served alt kept word for word) filling the right column. | The smoke's `img-not-upscaled` advisory at 768: the 3:1 banner stretched the 540px photo to 734px (1.36x). The banner cropped to a torso at 375. The two-column grid read in Z order. | From 640px the photo is a 220px right column (0.94x at 768), so `media: right` holds from tablet up. The phone crop sits on the puppy (`50% 78%`). The list flows down its columns (`grid-auto-flow: column`, 7 rows). | 375 · 768 · 1024 · 1280 |
| contents-list | c | **Stage rows**, the pool copy of `london/contents-list/b` "Three stages". Refresh delta, axis **layout**: London's three equal stage columns become three stage rows (numeral and name left, four ruled links beside), and the enquiry closes the band as a brass pill. | The stage names promised more than the sections kept: "Bring your puppy home" opened on viewing questions. The arrow appended to every link floated about 400px from its label at 1280. The band ran to about 1,050px at 375, with no disclosure. "Ready to talk about one of the six?" had no referent. | Stages renamed "Choosing your puppy", "Checks, papers and the journey home", "Living with a Staffy", and the lede to match. Arrows removed (underline on hover). Phones show stage 1, then "Two more stages, 8 sections" (about 610px). The close now reads "Ready to ask about one of our six puppies?" | 375 · 768 · 1024 · 1280 |
| desktop-dial | a | **Numeral rail** (`component-idea3.png`, comparison capture). No box: the 13 sections as thin display numerals on the bone page, one steel hairline from the text. | The current row was marked with a 3px brass inset stripe, which is impeccable's side-stripe ban. The 24px brand-steel numerals outweighed the labels. | The current numeral now sits in a brass square (`--color-cta` under `--color-cta-ink`) on a soft steel row. Numerals dropped to `--text-lg` in `--color-ink-3`, and labels are `--color-ink`. | 1024 · 1280 (hidden below, probe-checked at 375 / 768) |
| desktop-dial | b | **Fact ledger** (for-sale and near-me captures). A raised deep-steel card: a readout naming the part you are reading, then tight rows, each with its section's own figure as a pill where it has one. | "6 Q" and "7 Q" were cryptic. "4 coats" counted the four colour strings in `data/puppies.json` but contradicted the coat stand-in, which names three coats. The reviewer queried "KC form". | Pills now read "6 questions" and "7 questions", and their rows "Asked first" and "Everyday life". The coat pill was dropped. "KC form" was kept: the README's ledger line says each puppy goes home with its KC registration application form. | 1024 · 1280 |
| desktop-dial | c | **Page map**, the pool copy of `london/desktop-dial/a`. Refresh delta, axis **motif**: London struck every block with one ruled texture. Manchester's three question blocks are dotted and carry a question mark, so the map shows where the 20 answers sit. Block heights come from the outline's word counts. | The dot layer tiled up under the labels, because a repeating background ignores its offset. The legend "Dotted blocks hold the questions" was ambiguous on a page where every section is a question. The 44px floor flattens the shorter blocks' proportions. | The dots moved to an `::after` layer inset below the label. The legend now reads "Dotted blocks are the three question blocks". The 44px floor stays: it is the tap target. | 1024 · 1280 |
| jump-links | a | **Part switch** (`component-idea-modern.png`, `modern-faq-idea.png`). A sticky sunk track as a four-way switch over the page's three stages and Ask; the stage you are reading rises as a raised key. All raises a bottom sheet of ruled rows under the stage names. | "Bring home" wrapped to two lines in a 44px key at 375. The stage names mislabelled their sections, as in contents C. | The keys read "Choose", "Checks", "Living" and "Ask", sized to their labels (`flex: 1 1 auto`, no wrap). The opener reads "All", with the aria-label "All 13 sections". The sheet groups use the renamed stages. | 375 · 768 (hidden at 1024 / 1280) |
| jump-links | b | **Question bar** (for-sale capture, `puppy-card-with-filter-idea-1.png`). A slim bar ruled off by 13 progress ticks, showing "n of 13" and the section name. The Questions key raises the page's 13 H2s word for word. | The sheet's current row used the 3px brass side stripe. The idle ticks were steel-100 on the raised surface (about 1.2:1), close to invisible. The chevron pointed down for a sheet that rises. The 40px Christa avatar was announced on every page. | The current row now carries a soft steel ground and bold weight. Idle ticks are steel-300. The chevron points up. The avatar is decorative (`alt=""`, `aria-hidden`). The built component takes a small derivative, not the 1080px source. | 375 · 768 |
| jump-links | c | **Grouped drop panel**, the pool copy of `london/jump-links/b` "Drop panel". Refresh delta, axis **layout**: London's two-column grid of eight icon tiles becomes ruled icon rows under the three stage names (one column on phones, three stage columns from 600px), plus the enquiry row. The thumb is the Victoria family's Manchester puppy (CSS background, not announced). | Stage names, as in A. The reviewer also asked for the popover API on all three sheets, for focus, Esc and no history entries. | Stages renamed. Popover was **not** adopted: without script, a jump link inside a popover does not close it, so the sheet would stay over the section it just jumped to. `:target` closes on every jump, which is London's canvas pattern. Focus return and Esc belong to the kit build's script. | 375 · 768 |

Copy checks common to all nine:
- Prices, the deposit and its clause (`deposit_refund_clause`, verbatim), the delivery band, the
  parents' registration, the two DNA tests (named, certificates on request, never "clear") and
  `guarantee_label` appear only in the stand-in openings, and only as `data/` holds them.
- No video call, rescue, licence, distance, time, rating or review. No phone number. No em
  dashes.
- "Manchester" is never added to an anchor beyond what its H2 says. The labels "Travel to
  Greater Manchester" and the H2s in jump links B repeat the outline's own wording (outline §4
  entity note).
- Colours are tokens only. No colour word appears in any CSS comment.

Left for the board, not fixed here (the review's cross-component note): contents B and jump
links C share one icon set; contents C and jump links A and C share the stage names; and dial B
and jump links B and C share the "n of 13" readout. Siblings within each component are distinct.
If the user's picks pair two of these, the page board's refresh note should name which one
gives way. One pairing that shares neither icons nor stage names is contents A, dial B and jump
links B.

Final runs:
- `python3 scripts/check_city_canvas.py --city manchester --only
  contents-list,desktop-dial,jump-links` gave `examined 9 fragments, 3 meta files; 0 problems`.
- The full Manchester canvas smoke (`manchester-frames`, 18 frames) gave 76 passed at vp375,
  vp768, vp1024 and vp1280, with no advisories. The one advisory before the fix was contents B's
  upscale at 768.
