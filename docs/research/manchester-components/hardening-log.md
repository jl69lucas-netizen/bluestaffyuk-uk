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

## Task 24: key takeaways, tables, image and text (2026-10-07)

**How the passes ran.** `frontend-design:frontend-design` was invoked with the Skill tool on the
plan's Step 2 brief (batch: key-takeaways, tables, image-text; pool slot `c` of each). First,
every sheet the ideas index cites for the three components was opened with the Read tool (the
seven key-takeaways sources, the nine tables sources, the eleven image-text sources), and so were
the candidate served photos (the delivery van photo was dropped: it carries a phone number and
lettering, lessons 7). The outline rows were read: §5 (five lines, no heading), G2's litter table
(H4, caption, four columns), and the body rows the image-text variants stand in for: §13
delivery (A), §9 health tests and raising (B), §8 deposit and viewing (C). Those three were
chosen because their answers sit wholly inside the README's facts; §17–§19 need facts the list
does not hold. Outline §5 carries no heading, so no takeaways variant adds an H2: each names
itself in a `<p>`. The tables heading is the outline's H4, word for word, and every table
carries the outline caption.

Pool picks (Phase F ruling 4: furthest from London's pick, and suited to Manchester's rows):
- key-takeaways `c` ← `london/key-takeaways/b` "Tick card". "Numbered decisions" numbers five
  facts that are not a sequence.
- tables `c` ← `london/tables/c` "Boy or girl". "Payment schedule" is a payment table, and
  Manchester's outline has one table only: the litter.
- image-text `c` ← `london/image-text/b` "Offset block". It differs from London's pick on all
  four axes ("Flanked portrait" on three), and its spec sheet suits the deposit row.

Every pool copy differs from London's pick on all four axes.

Tables (working rule 13, ruling 5): all three render a real `<table class="stack-table">` with
the caption "This litter: each puppy, sex, coat and price", columns Puppy, Sex, Coat and Price,
and `data-label` on every `<td>`. Each one stacks into labelled `display:block` rows at 640px
and below, with no sideways scroll. Tables A carries each pup's own `card_photo` in its row
(Known Issue 100). The puppy photos keep the alt the site serves most for each `card_photo`
(`src/components/kit/PuppyCard.astro`, "<Name> the <coat> Staffordshire Bull Terrier puppy",
on 8 to 21 built pages each), word for word on first use. Tables C reuses two of them.

`impeccable:impeccable` was then invoked with the Skill tool (brand register; critique). Its
loader reported `hasProduct: false`, and `/impeccable teach` is interactive and the user's, so
the brand context came from the design-context files, as in Tasks 22–23. The two assessments ran
in isolation:
- **A.** A separate review agent read the nine fragments, the metas and 36 painted shots
  (375 / 768 / 1024 / 1280). Nielsen total about 29/40. No banned pattern was found: no side
  stripe, no hero-metric, no caps eyebrow, no numbered non-sequence, no CTA arrow, no em dash.
- **B.** The deterministic detector, `npx impeccable --json` on the three folders. Its only rows
  were 30 `cramped-padding` hits (19 distinct), all false positives of the kind Tasks 22–23
  recorded. jsdom does not resolve the stylesheet padding, and on the shots every child is inset.

This agent also painted its own review before and after each fix round (shots at four widths).

| Component | Variant | frontend-design direction | impeccable findings | Fixed | Widths |
|---|---|---|---|---|---|
| key-takeaways | a | **Hairline columns** (`component-idea444.png`, `component-idea3.png`). The five facts (price per sex in this litter, deposit, delivery band or collection, both parents' named tests with certificates on request, the guarantee), each a line icon, a serif title and one sentence, as columns split by vertical hairlines. Framed only by a steel rule above and a hairline below. No photo. | Five columns at 1024 gave an 18–20 character measure and four titles wrapped, with orphans at 1280 ("first", "tests"). The body type tiers were inverted (17px at tablet, 16px at desktop). "our Two-year health guarantee" read like a capitalisation slip. "DEFRA-" broke at its hyphen. | Three columns at 1024–1199 and five from 1200. Titles shortened ("Deposit first", "Door or collect", "Two DNA tests") with `text-wrap: balance`. Body is 16px at every tier. The guarantee item is titled with `guarantee_label` and carries `guarantee_cover`. "DEFRA-approved" never breaks. | 375 · 768 · 1024 · 1280 |
| key-takeaways | b | **Label and tiles** (`Page-Section-Module-design4.png`, `moderrn-carrd.png`). The strip's name in its own cell, then the five facts as sunk steel-100 tiles. The deposit tile carries `deposit_refund_clause` word for word. | Shared a's five icons, so the siblings read as twins at 375. The "icon + lead + sentence" tile was impeccable's identical-card-grid ban. The sub ("each one checked against our own price list…") read as defensive commentary. Tile 1 sat half empty beside the five-line tile 2. | Icons dropped. From 1024 the label is a column and the tiles a two-column bed, with the guarantee tile closing it across both columns. The sub now reads "Five facts about this litter, whether you collect in Carlisle or we deliver to Manchester." | 375 · 768 · 1024 · 1280 |
| key-takeaways | c | **Tick card**, the pool copy of `london/key-takeaways/b`. Refresh delta, axis **layout**: London's one column of four ticks under a heading becomes a two-column tick grid from 768px, with title and answer side by side above it. The photo is Manchester's own served family photo, served alt kept. | Tall: a 16:9 photo made the card about 1,090px. The fifth tick sat alone in a column. The lede was bottom-aligned away from the title. "from Lisa Bright" described the breeder from outside (working rule 1). "Two-/year" broke at the hyphen. | 2:1 crop from 640px (1,046px; the faces stay whole, so 5:2 was refused). The fifth tick spans both columns and carries `guarantee_cover`. Head is top-aligned. "Five plain answers from us…". | 375 · 768 · 1024 · 1280 |
| tables | a | **Photo shelf** (`puppy-card-idea2.png`, phone capture). The litter table in one raised card, each row led by the pup's own photo, an 80px rounded square on a bone mat, with name and Available. On phones each row becomes a two-up portrait card with labelled lines. | At 375 Cheryl's card (the last row) lost its padding and dividers: `tbody tr:last-child td` (0,2,3) beat the phone rule. Byrd's ears touched the top edge. The phone section was tall. A note that the thumbnail in the row header makes it repeat the alt. | The phone rule now covers `tr:last-child td` too. Byrd is cropped at 50% 30%. Phone photos are 3:2. Explicit ARIA table roles were added, so the `display:block` stack keeps table semantics. The alt-in-header is left as London's roster had it: the photo is the puppy column's own. | 375 · 768 · 1024 · 1280 |
| tables | b | **Steel ledger** (`compare-table-idea.png`, `component-idea55.png`). The table on a full-width steel band, compact. A token swatch beside each coat (steel solid, bone pale, split for both, striped for the blaze). A steel-300 rule where the boys end and the girls begin. Heading left, table right from 1024. | At 375 "Blue with white blaze" butted against "£1,700". Prices in brass-200 could read as links on a band where brass-200 marks links. "DEFRA-" split in the note. (The review suggested `display:grid` rows; that would fail `layout-table-stacks-on-mobile`, which requires `display:block` rows below 640px.) | Phone cells are 21 / 51 / 21% with a gutter on the coat. Prices are bone (`--color-text-on-inverse`), and labels stay brass-200. A `.nb` rule was added. ARIA roles. | 375 · 768 · 1024 · 1280 |
| tables | c | **Boy or girl**, the pool copy of `london/tables/c`. Refresh delta, axis **layout**: London's sideways table (attributes as rows, boys and girls as columns) becomes the outline's puppy-per-row table in two row groups that stand side by side from 641px, each headed by a photo and its one price ("£1,500 each, whatever the coat"). | The lede ("three boys on one side…") was false at 375, where the groups stack. The group photo inside `th scope=rowgroup` made every cell's header read the alt. Christa's ears were clipped. 1,392px tall at 375. The coat sat 8px off the price's edge at 1280. | The lede now reads "Our three boys and our three girls are grouped apart…". The photo moved into its own `<td data-label="Photo">`, so the row-group header is words alone. Christa is cropped at 53% 18%. The desktop coat padding was removed. ARIA roles. Height accepted: the 5:2 phone photos are the shortest crop that keeps Roman's face whole. | 375 · 768 · 1024 · 1280 |
| image-text | a | **Window card** (`card-idea55.png`, `card-idea2.png`), §13 delivery. One deep-steel card: the H2 and its answer left, the H2's photo (Manchester's own served pup photo) in a bone window right, then the H3 with its photo first and its answer, and one brass pill with the brass focus ring on steel. | The bone window was mostly empty mat around a 300px photo at 1024, and a full-width slab at 768. The H3 thumbnail (200px, 16:9) made faces tiny. The H3 answer "Neither suits every family" dodged its question. | The window now hugs the photo (12px mat, top-aligned, at most 384px wide at tablet). The H3 photo is 240px at 4:3. The answer leads with the trade-off: "Collection suits a family who wants to meet us in Carlisle…; delivery suits…, priced by distance." | 375 · 768 · 1024 · 1280 |
| image-text | b | **Zigzag pair** (`card-idea1.png`, `card-idea2.png`, split image+text sheet), §9. The H2 row puts Jones left; the H3 row puts Maggie with her pups right. Both are in the uniform 1408×768 in-body box with captions, divided by hairlines. | At 768 it ran 1,394px in one column (the zigzag started at 900). The H2 set in three lines at 27px. "…instead of printing a result on this page" invited doubt. | The zigzag starts at 640 (674px at 768). The H2 measure is 30ch from 1024. The answer ends "…and we share their certificates on request." | 375 · 768 · 1024 · 1280 |
| image-text | c | **Offset sheet**, the pool copy of `london/image-text/b`. Refresh delta, axis **layout**: London's one column of five label/value rows becomes a two-by-two sheet divided by a hairline cross from 640px. §8 deposit: what it does, what it comes off, the refund clause word for word, and what happens after the visit. Manchester's served family photo sits on the steel-100 bleed. | The dt "If you change your mind" was repeated word for word by the clause beneath it. "What it comes off" was awkward. The H2 set in three lines. "DEFRA-" split at 1024. | The dts now read "If plans change" and "Off the price of". The H2 measure is 30ch from 1024. "DEFRA-approved" never breaks. | 375 · 768 · 1024 · 1280 |

Copy checks common to all nine:
- Prices are said of this litter only.
- The deposit appears with `deposit_refund_clause` verbatim (takeaways B, image-text C) or with
  no refund wording at all (the outline's "whole clause or none").
- The delivery band is `delivery_note`'s, and the guarantee is `guarantee_label`, with
  `guarantee_cover` where a sentence carries it.
- Both parents' tests are named, with certificates on request: never a result, never "clear".
- No video call, rescue, licence, distance, time, rating or review. No phone number. No em
  dashes. Colours are tokens only, and no colour word appears in any CSS comment (the validator
  caught "white" in two table comments on the first run).
- First-person voice throughout.

Left for the board, not fixed here:
- Takeaways C and image-text C both use `victoria-family-blue-staffy-manchester.webp` with its
  served alt. If both are picked, the second use needs a new alt (working rule 11, 2026-09-29).
- Takeaways A's columns and the two pool copies' deltas show from 768 / 640 / 1200px. On a phone,
  A reads as ruled rows, and takeaways C and image-text C paint like their London originals.
  The metas' axes describe the tablet and desktop paint.
- Image-text B's media alternates; its `media: left` names the leading row.
- Jones's served photo reads as a young dog beside the caption "the sire of this litter". It is
  a served asset, so this is an image-choice risk for STOP 4, not a defect.
- On 2x screens the 723px and 780px masters upscale at 720 CSS px. The kit build takes the -760
  siblings through srcset.

Final runs:
- `python3 scripts/check_city_canvas.py --city manchester --only key-takeaways,tables,image-text`
  gave `examined 9 fragments, 3 meta files; 0 problems`.
- The full Manchester canvas smoke (`manchester-frames`, 27 frames) gave 112 passed at vp375,
  vp768, vp1024 and vp1280, with no advisories.

## Task 25: reviews, FAQ blocks, newsletter, contact form (2026-10-07)

**How the passes ran.** `frontend-design:frontend-design` was invoked with the Skill tool on the
plan's Step 2 brief (batch: reviews, faq-blocks, newsletter, contact-form; pool slot `c` of
each). First, every sheet the ideas index cites for the four components was opened with the
Read tool: the six reviews sources, the ten FAQ sources, the seven newsletter sources and the
eight contact-form sources. So were the candidate served photos. The outline rows were read
too:
- reviews §6, §11 and §20: no heading; one `data/reviews.json` row per slot (The Victoria
  Family, Mark J, Rachel L.), each quoted word for word with no score;
- FAQ §7, §12 and §21: six, seven and seven questions, in the outline's page wordings;
- newsletter §16: no heading, 35 words;
- contact form §22: its H2 and the image note "Lisa Bright with a puppy beside the form".

The FAQ answers are written only from each pick's bank rows (`found_in`) and the settings keys.
They are kept in one source (the scratchpad generator) so the three variants carry identical
copy:
- the mother-and-puppy answer is the STOP 2 q04 approved wording, word for word;
- the DNA answer names L-2-HGA and HC-HSF4 (and what each is) with the certificates on
  request: never a result, never "clear";
- "puts the terms in writing" (bank `buying-puppy-farm`) is left out, because the validator's
  `in writing` rule refuses an unconfirmed promise;
- the deposit answer carries `deposit_refund_clause` whole.

Each review, newsletter and FAQ variant shows all three slots or blocks stacked, in page order,
so the per-slot refresh delta (ruling 8) is visible on the canvas. On the page they sit far
apart. The canvas smoke reads media at section level, and a photo inside a repeated
`data-review-slot` / `data-faq-block` belongs to the item. So the review and FAQ variants
declare `media: none`, even where each slot or block carries its own photo.

Pool picks (Phase F ruling 4: furthest from London's pick, and suited to Manchester's rows):
- reviews `c` ← `london/reviews/c` "Kennel wall". It is one review on a plate, which suits
  mode single. "Two London notes" stacks two London reviews in one tray under a heading, which
  is built on London-only copy.
- faq-blocks `c` ← `london/faq-blocks/c` "Lead answer". Its blocks stack, as Manchester's three
  separated rows do. "Three trays" sets the three blocks side by side, which the outline places
  apart.
- newsletter `c` ← `london/newsletter/b` "Steel band". "Ruled row" was the other candidate, but
  its ruled, airy, left-set row overlaps newsletter B's ruled note.
- contact-form `c` ← `london/contact-form/a` "Letter to Carlisle". The letter carries the
  outline's "which puppy, or boy or girl, collect or delivery" as sentences, and its refresh
  adds the outline's Lisa photo. "Doorstep tray" is built around a London family photo and a
  call line.

Every pool copy differs from London's pick on all four axes. None uses the video call (q08).

**Harness fix, charged to the gate, not a new rule.** The validator read the approved H3
"Should I See the Mother With Her Puppy Before Money Changes Hands?" as naming a parent
"With", through the `mother <Name>` pattern on a Title Case heading. Test first:
`tests/py/test_check_city_canvas.py::test_a_title_case_question_is_not_a_parent_name` failed.
Then "With" joined `NOT_NAMES` in `scripts/check_city_canvas.py`, and the test file passes
(66 tests).

`impeccable:impeccable` was then invoked with the Skill tool (brand register; critique). Its
loader reported `hasProduct: false`, and `/impeccable teach` is interactive and the user's, so
the brand context came from the design-context files, as in Tasks 22–24. The two assessments
ran in isolation:
- **A.** A separate review agent read the twelve fragments, the metas and 48 painted shots
  (375 / 768 / 1024 / 1280). Nielsen total 29/40. No hard tell was found: no side stripe, no
  caps eyebrow, no middle dots, no CTA arrow, no hero metric, no numbered non-sequence, and no
  em dash in our copy. Rachel L.'s verbatim review keeps its own.
- **B.** The deterministic detector, `npx impeccable --json` on the four folders, returned 103
  rows:
  - 98 `cramped-padding` rows: jsdom false positives of the kind Tasks 22–24 recorded;
  - 4 `side-tab` rows, all for the 4px `border-top` section rules on FAQ C and contact C.
    These are full-measure rules over a block, not a side accent on a card (the ban is
    `border-left`/`border-right`);
  - 1 `clipped-overflow-container` row: `overflow:hidden` on reviews C, which holds the bled
    photo off the page's sideways scroll and has no popover inside it.

The smoke's advisories (face crops, upscales) and this agent's own measurement of every
section's height and H2 line count were folded into the fix rounds.

| Component | Variant | frontend-design direction | impeccable findings | Fixed | Widths |
|---|---|---|---|---|---|
| reviews | a | **Quote and nameplate** (`review-component-idea.png`, phone capture). Each review is on a bone-50 quote panel that closes on a steel nameplate with the name and the place as data gives it. The Victoria family's own served photo is their avatar; Mark J and Rachel L. have no served photo, so they get a brass monogram. | Three identical testimonial cards; the 24px step of the middle card read as a mistake. The 48px avatar shows half a face (the source's composition). | The step is gone. The per-slot delta is now an accent role: the middle nameplate is the deepest steel, and the short review is set in the display face at every width. | 375 · 768 · 1024 · 1280 |
| reviews | b | **Margin quote** (`about:team-idea1.png`, comparison capture). No box: each slot is ruled off, a display quote mark hangs in the margin, and the family's portrait sits in the far margin of the top slot. The mark swaps sides slot by slot. | At 375 the closing ” came before the review it closes. At 1024 and up the flipped mark sat about 380px from the text. The left edge of the text differs between slots. | Phones show the opening “ on every slot. From 640px the flipped slot is held to the measure plus 72px, so the closing ” hugs the text. The left-edge difference is the intended delta and was kept. | 375 · 768 · 1024 · 1280 |
| reviews | c | **Three plates**, the pool copy of `london/reviews/c`. Refresh delta, axis **layout**: London's one wall with one review becomes three plates, one per slot, with the photo alternating left, right, left. Each parent photo carries a credit pill, so a parent never reads as the reviewer's own dog. | The plate covered Maggie's face (top right of her photo) at 1024. The Victoria faces were cut at 375 and covered by the plate at 768. Upscaled 1.06x at 768. | Maggie moved beside Mark J (photo right, so her face is clear of the plate) and Jones beside Rachel L. The desktop credits sit at the photo's foot on its far side. Victoria is cropped at 45% 12%. At tablet the photo is inset at its natural 720px, and the plate overlap is reduced to 40px. | 375 · 768 · 1024 · 1280 |
| faq-blocks | a | **Question bars** (`faq-idea0.png`, `faq-idea44.png`). Each block is its own band holding one narrow column of filled question bars with chevrons. Accent role per block: soft steel bands with raised bars, and a raised middle band with soft steel bars. | Generic SaaS accordion (noted). The bone-50 middle band was about 1.04:1 on the page, so the delta did not show. The H2 ran to 3 lines at 1024. "L-2-HGA" broke at its hyphen. | The middle band is now the raised surface between hairlines. The desktop H2 is 26px with no measure cap (2 lines). Test names and "DEFRA-approved" never break. | 375 · 768 · 1024 · 1280 |
| faq-blocks | b | **Rows beside a photo** (`component-idea-faq1.png`, `faq-idea00.png`). Display-face rows between hairlines beside one photo per block: Christa (buying), Maggie with her pups (health and viewing), and Manchester's own served pup photo (everyday life). The photo swaps sides block by block and stays in view. | The 4:5 crop cut Maggie in half at 1024/1280. The Manchester pup photo was upscaled 1.36x at 768. Each block was about 1,000px tall on a phone. Hover dimmed the H3 to muted. | Square crops beside the rows from 640px (200px at tablet, 320px at desktop). Maggie is cropped at 75% 4%. Phones get a 3:1 strip. Hover now underlines. | 375 · 768 · 1024 · 1280 |
| faq-blocks | c | **Lead beside rows**, the pool copy of `london/faq-blocks/c`. Refresh delta, axis **layout**: London's open lead above a two-column fold grid becomes the open lead on its own bone sheet beside one column of rows (from 1024). The H2 stays full width. London's 01–19 numbers are dropped. Per block, the third block folds all seven questions into two newspaper columns. | The first draft, a side head, wrapped the H2 to 4–5 lines in its column at 1024 (`cityTypeFit` 1b, "heading column too narrow"). The lead H3 was over the tier caps (19/20px). Block 3's grid zigzagged. | The side head was replaced by lead-beside-rows (2-line H2s). Lead H3 sizes are now 17 / 18 / 20. Block 3 uses CSS `columns:2`, read down then across. | 375 · 768 · 1024 · 1280 |
| newsletter | a | **Sunk slip** (`Page-Newsletter-module-design2.png`, split capture). The whole sign-up sits in one soft steel slip pressed into the page and set left: the display line, one sentence on what a subscriber gets, then the field and button. | The first draft (ticks beside a slip) was a landing-page template; "That is all this list is for" read as a tick that is not a benefit; at 1024 and up it had the same composition as C. Field border steel-300 was 2.1–2.6:1 (WCAG 1.4.11). | Rebuilt as one stacked slip (layout `slip-stack`), with the ticks dropped. The note reads "…your email is used for nothing else." Borders and the slip edge are steel-500. | 375 · 768 · 1024 · 1280 |
| newsletter | b | **Postmarked note** (`card-idea55.png`, `newsletter-idea1.png`). A short signed note from Lisa between rules, with Vennie as a round postmark photo in a dashed ring. | Vennie's face was small in the full-frame circle. Field border contrast as above. No privacy line. | The postmark crops onto her face (`object-view-box`). Steel-500 border. Added "Your email is used for nothing else." | 375 · 768 · 1024 · 1280 |
| newsletter | c | **Split steel band**, the pool copy of `london/newsletter/b`. Refresh delta, axis **layout**: London's centred band becomes copy left and form right from 1024; it stays centred below. | The invalid state was a brass border (2.4:1 on the field). The label was left-set under centred copy on phones. "Tell me" was vague. | Invalid is a 3px brass ring on the steel band (large-text pair, about 5:1). The label is centred below 1024. The button reads "Email me the note". Privacy clause added. | 375 · 768 · 1024 · 1280 |
| contact-form | a | **Choice first** (`component-idea-shop1.png`, near-me capture). A raised card: the H2 beside Lisa's photo, then collect-or-delivery as two whole-box options before the kit's fields. The radio input covers its box, so the tap target is the box (the smoke's 44px field rule). | Field and option borders were steel-300 (WCAG 1.4.11). The H2 ran to 3 lines at desktop. The phone section was 1,540px with a 16:9 photo. | Steel-500 borders. The desktop photo column is 220px square, with no measure cap on the H2 (2 lines). Phones get a 5:2 strip (1,492px). | 375 · 768 · 1024 · 1280 |
| contact-form | b | **Photo at the edge** (`new-modern-card-idea.png`, phone capture). Lisa's photo bleeds from the left screen edge at full height, beside a compact form with a two-key collect-or-delivery switch. | The full-height crop upscaled the 1408×768 photo 1.16x. The unselected switch keys had no affordance. The H2 ran to 3 lines. "Send us the puppy you like" read oddly. The field grid matched A's. | A six-column desktop grid (name, email and phone; town and puppy; message) holds the section under 768px, with no upscale. Keys are raised with a steel-500 hairline, and a 3px ring when picked. The H2 is 2 lines. The lede reads "Tell us which puppy you like…". | 375 · 768 · 1024 · 1280 |
| contact-form | c | **Letter, addressed**, the pool copy of `london/contact-form/a`. Refresh delta, axis **layout**: London's lone letter now sits beside an addressee column with Lisa's photo (outline §22's image), and it gains the handover line "and I would rather …". | Tall on phones (about 1,650px). The DEFRA sentence was tacked under the send button. The labels sit under their fields. | Phone line padding was tightened (1,618px). DEFRA moved into the lede. The privacy clause sits by the send. Labels under fields are kept: it is the letter's design, and each field carries `<label for>`. | 375 · 768 · 1024 · 1280 |

Copy checks common to all twelve:
- Reviews are `data-review` quotes, word for word, attributed as data gives them: The Victoria
  Family, Manchester, UK; Mark J, London, UK; Rachel L., London. No stars, no score, no
  re-attribution.
- Prices are said of this litter only.
- The deposit carries `deposit_refund_clause` whole.
- The delivery band is `delivery_note`'s.
- The reply time is `enquiry-reply-time`'s ("within 24-48 business hours").
- "We confirm your puppy is still free before you pay anything" comes from
  `listing-availability`.
- No phone number, no video call, rescue, licence, distance, time or result. No em dash in our
  copy.
- Colours are tokens only. No colour word appears in any CSS comment.
- Lisa's photo carries a new alt ("Lisa Bright, the breeder who answers your enquiry, holding
  two young puppies at home in Carlisle"). It is not a validator-held served alt; London's
  built page serves it as "Lisa Bright, our blue Staffy breeder, smiling and holding up two
  young puppies, one fawn and one dark brindle", so Manchester's is the outline's "repeat
  carrying a new alt".

Left for the board or the kit build, not fixed here:
- **Error messages.** They are shown by CSS `:user-invalid`, with no `aria-describedby`.
  Pointing at a `display:none` error would make every field always announce its error. The
  kit's `ContactFormKit` wires its errors through `data-err` and its script; the built
  component does the same.
- **Privacy link.** No link to `/privacy-policy-uk/` was added: working rule 12 puts every link
  on the board first. The page board should list it beside the form and the newsletter.
- **Reduced motion.** It is held by the frame's global rule; the built page's CSS must carry
  the same rule.
- **Two delivery answers.** "Can My Blue Staffy Puppy Be Delivered…" (bank
  `about-delivery-home`) gives no price; "Do You Deliver Puppies Across the UK?" gives the band.
  Each answer is its own bank row, so neither borrows the other's fact.
- **The mother-and-puppy question.** It is answered "the £500 deposit comes first", which is
  the q04-approved wording the user chose knowingly (the batch named the trade-off).
- **Lisa's photo and the field names.** It appears in all three contact variants, and only one
  will be picked. The new `handover` field (collect or delivery) and the `any-boy` / `any-girl`
  puppy options are not in `ContactFormKit` yet; the kit build adds them.
- **Photos shared with Tasks 22–24.** If reviews A, B or C is picked alongside takeaways C or
  image-text C, `victoria-family-blue-staffy-manchester.webp` repeats on the page, and the
  repeat needs a new alt (working rule 11). Maggie and Jones in reviews C repeat image-text B's
  parents in the same way.
- **The outline's straight apostrophe.** The H3 "Can I Contact You for Advice for the Dog's
  Whole Life?" keeps it, as the outline writes it.

Final runs:
- `python3 scripts/check_city_canvas.py --city manchester --only
  reviews,faq-blocks,newsletter,contact-form` gave `examined 12 fragments, 4 meta files;
  0 problems`.
- The full Manchester canvas smoke (`manchester-frames`, 39 frames) gave 160 passed at vp375,
  vp768, vp1024 and vp1280, with no advisories.
- The whole city, all 13 components, gave `examined 39 fragments, 13 meta files; 0 problems`,
  and `npm run -s check:canvas` (London) still gives `examined 45 fragments, 15 meta files;
  0 problems`.

## Task 26 refinements (user notes)

The user picked hero C and trust-strip B on the canvas
(`docs/research/manchester-components/picks-2026-10-07.md`, submission
`s-2026-10-07T12-03-32-730Z`) and left one note on each. Plan Task 26 Step 5 redesign loop, for
these two variants only. `frontend-design:frontend-design` was invoked with the Skill tool on the
user's two notes plus the README contract, then `impeccable:impeccable` (brand register;
critique and harden). The loader again reported `hasProduct: false`, so the brand context came
from the design-context files, as in Task 22. The detector (`npx impeccable --json` on the two
fragments) returned six `cramped-padding` rows, all false positives: the bled photo column and the
panel wrappers, where jsdom does not resolve the stylesheet padding (the shots show every child
inset). The painted review used Playwright Chromium shots at 375 / 768 / 1024 / 1280.

**Why the fourth hero tick is not "Vet-signed health card".** That was the brief's recommended
pick, but trust-strip B's folder already holds "Vet-signed health card" as its first slip, so the
hero and the strip directly under it would repeat a line again, which is exactly what the user's
trust-strip note objects to. "Kennel Club registered parents" was ruled out because it matches the
evidence ledger's `kc-registered` vocabulary, and the ledger row's pattern is scoped to one
sentence ("Maggie and Jones are both Kennel Club registered"), so a tick would be
`claim-unledgered` on the built page. Deposit and price lines were ruled out for the hero by the
brief. The fourth tick is "DEFRA-approved transport", from `data/settings.json` `delivery_note`.
It fits a hero for a buyer whose puppy travels from Carlisle, it states no distance, it is a fact from
data, and it repeats nothing on the canvas's picked sections.

| Component | Variant | User's note | frontend-design direction | impeccable findings | Fixed | Widths |
|---|---|---|---|---|---|---|
| hero | c | "…should be four; add one more. Make it a one-liner on desktop and stack on mobile, with two on the left and two on the right, and make it look polished." | The tick row leaves the copy column and becomes a promise rail. From 1024px it runs as one line along the foot of the whole band: four equal cells, each tick in a ring, divided by short 24px steel hairlines, set to the page's 1200px content width under a full-width rule. Below 1024px the four sit as a 2x2 of soft steel tiles, filled column-first so the left holds Raised in our home and Support after collection, and the right holds Two-year health guarantee and DEFRA-approved transport. The ringed tick shares one centre line with one-line and two-line labels. | At 768 the 2x2 tiles ran the full 720px, leaving each label stranded in a wide empty tile, out of scale with the 48ch lede above. The four labels cannot fit one line at 768 (about 880px needed), so 2x2 is the correct tier there. At 375 every label wraps to two lines at the same height, so the grid is even, not ragged. | Tiles are capped at 300px per column from 640 to 1023. The photo column is 372px from 1024px, with the rail at 56px, so the band is 429px at 1024 and 1280 (inside 390–450). The photo still comes first on phones. Tap and type tiers are unchanged: tick labels are `--text-sm`, the tiles are 52–55px tall, and the CTAs are untouched. | 375 · 768 · 1024 · 1280 |
| trust-strip | b | "…change this text since we already have it on the selected hero above. ADD new related page-specific terms" | The "And from us" column (home, support, guarantee, now all hero ticks) becomes "From us to Manchester": the handover steps the folder doesn't cover. The deposit that holds a puppy, then home delivery or collection. Each item gets a new line icon (tag, van, pin). The intro no longer names collection and delivery, because the column now does: "The five papers and records that go home with every one of our puppies." | At 1280 "£500 deposit secures your / puppy" and at 375 "UK home delivery, £200–£350 by / distance" left orphan words. | `text-wrap: balance` on the column's items, so the lines now break as "£500 deposit / secures your puppy" and "UK home delivery, / £200–£350 by distance". | 375 · 768 · 1024 · 1280 |

The three new trust items and where each comes from:
- "£500 deposit secures your puppy": `deposit_gbp`, and `data/faq.json` "How much is the deposit?" ("secures your chosen puppy"). It is never called refundable, and it has no clause because it is not a deposit-terms sentence.
- "UK home delivery, £200–£350 by distance": `delivery_min_gbp`, `delivery_max_gbp`, and `delivery_note` ("priced by distance").
- "Or collect from us in Carlisle": collection in Carlisle (the locked facts; `data/faq.json` "you can collect in person instead").

None of the three repeats a hero tick or a folder slip. The hero's "DEFRA-approved transport" and
the strip's delivery line are kept apart on purpose: the strip's line carries the price band and
not the transport wording.

`meta.json` descriptions were updated for both. Hero C's axes are unchanged (layout
feature-thumbs, media left, density compact, framing bleed): the rail is a foot line inside the
same band, not a new layout. Trust-strip B's axes are unchanged too, and its `differs_from` now
says "three handover steps".

Final runs:
- `python3 scripts/check_city_canvas.py --city manchester --only hero,trust-strip` gave
  `examined 6 fragments, 2 meta files; 0 problems`.
- The full Manchester canvas smoke (`manchester-frames`, 39 frames) gave 160 passed at vp375,
  vp768, vp1024 and vp1280. The two refined frames re-run alone gave 8 passed, with no advisories.
- The canvas page was rebuilt with `--allow-partial --files-map
  docs/artifacts/canvas/manchester-files.json`: 39 variants, 14 images. It is not republished
  here; the controller publishes it.

## Built — Task 28

Hero C, counter B and trust B built into the kit from the frozen picks (355d5e43) as
`CityFeatureAndThree`, `CityRangeSheet` and `CityPuppyFolder` (`data/design/components.json` rows
M1-M3, each with `canvas_variant` and `root_selector`), previewed on the new
`/kit-preview/city-manchester/` (gap G11; London's `/kit-preview/city/` now renders London's rows
only). No London component is imported or copied; shared are tokens, `city.css`, and three new
`src/lib/cityKit.ts` helpers (`transportName`, `PUPPY_SIGNS`/`sign()`, `pickAvailable()`) plus
`servedPuppyAlt()` in `src/lib/imageFocus.ts`. Every figure, sign and name is read from data; the
hero's four photos keep PuppyCard's served alt on first use, and the counter's four repeats take
`puppyAlt(…, 'short')` (`shownAbove`), its two first uses (Byrd, Christa) the served alt.

`frontend-design:frontend-design` and then `impeccable:impeccable` were invoked with the Skill tool
on the built components, read from `CITY_SHOTS=…/BSUK-refs/manchester/_build-shots npm run
test:render:city` at 375 / 768 / 1024 / 1280 against the canvas fragments. The impeccable loader
again reported `hasProduct: false`; the brand context came from `rules/design.md` and the tokens,
as in Tasks 22 and 26. The render gate first failed on the hero heading mounted as an H2 on the
preview (desktop H2 at 3 lines in the 440-552px copy column, q06); the preview now mounts it as its
one H1, as the page will, at the canvas's 24px / 30px (inside the 26 / 30 / 34 caps).

| Component | frontend-design found | impeccable found (critique, harden) | Fixed | Widths |
|---|---|---|---|---|
| hero (feature and three) | Faithful to the pick: bled photo column, contact column of three, promise rail one line from 1024 and 2x2 below; band 428px at 1024 and 1280. No defect. | Harden: the canvas's `white-space: nowrap` on the rail would run a longer data label into its neighbour at 1024 (cells 244px); a long name could run its caption pill off a thumb; a litter down to one puppy would leave the feature in a 2fr column beside empty cells. | Rail labels `text-wrap: balance` instead of nowrap (one line at today's labels); pill `max-width` inside its photo; `.pic:has(> .feature:only-child)` gives a lone feature the whole column. | 375 · 768 · 1024 · 1280 |
| counter strip (range sheet) | At 375 "Each of our / three boys" wrapped to two lines and dropped £1,500 a line below £1,700 in the same row. | Critique: figures within the sheet at every width (probe `rangeSheetSpill`); contrast passes. No further defect. | Each figure cell is a column, label at the top and figure at the foot, so the two prices share a baseline. | 375 · 768 · 1024 · 1280 |
| trust strip (puppy folder) | At 1024 the fifth slip, "KC registration application form", ran to three lines in a half cell beside an empty one, so the folder ended ragged. | Critique: tab sits on the folder (probe), steps balanced (Task 26 fix carried), no step repeats a hero tick. No further defect. | From 640px an odd last slip spans both columns: one line at 768, 1024 and 1280. | 375 · 768 · 1024 · 1280 |

Gates after the fixes: `npm run -s build` exit 0; `python3 -m pytest -q tests/py/test_city_kit_manchester.py
tests/py/test_city_kit.py tests/py/test_design_components.py` 130 passed, 1 skipped (the skip
pre-dates this task); `npm run test:render:city` 57 passed, 55 skipped, 0 failed, with London's
three routes unchanged and no advisory on the Manchester route.

## Built — Task 29

Contents B, dial A and jump links B built into the kit from the frozen picks (355d5e43) as
`CityIconRows`, `CityNumeralRail` and `CityQuestionBar` (`data/design/components.json` rows M4-M6,
each with `canvas_variant` and `root_selector`), the `CityNavSet` a Manchester page passes to
`src/layouts/CityShell.astro` (`bar`, `dial`, `contents`). No London component is imported or copied;
shared are tokens, `city.css`, `cityIcons.ts` (four new line icons: papers, guarantee, family, coat;
`CityIcon` widened to match), `src/lib/sections.ts` (`SectionRef.row`, the contents row's fuller
name) and `src/lib/scrollSpy.ts`, reused for the current section (lessons entry 20: the whole band,
topmost wins), plus its new `keepRowInBox()`. The bar's top-chrome rules (the `--strip-h` jump
offset, the slide away on the way down and back on the way up from answer board q03, the holds) are
in a new `src/lib/jumpBar.ts`, so no city has to copy London's band to keep them. The preview's
nav demo is the outline's own H2s, word for word, with the canvas's short names, row names and
icons (`MANCHESTER_NAV` in `_registry.ts`), pointed at the preview's own Manchester anchors.

Gap G12: every city's bar and dial carry the shared `data-city-nav` hook (`"bar"` / `"dial"`).
London's `CityJumpStepper` and `CityDialPhotoMarker` gained the attribute and nothing else.
`tests/render/lib/cityTypeFit.ts` `skipRoot` and `src/styles/city.css`'s container rule now read
`[data-city-nav]` only, and the known-good fixture holds a bar and a dial of both cities.

Two rulings carried from London, by their own words: the contents list hides from 1024px, where the
dial is the contents ("Hide it from 1024px, as the other pages do", answer board q05, 2026-09-29), so
the canvas's 1024 card is not built; and the bar slides away on the way down (answer board q03). The
contents photo is the old site's `reputable-blue-staffy-breeder-manchester-pup.webp` at its served
path with its served alt, word for word; its row in `data/image-focus.json` records the puppy's face
only (the photo's subject and its alt's), so the 2:1 phone crop sits on the puppy, as the canvas's
did, rather than half a downturned head.

`frontend-design:frontend-design` and then `impeccable:impeccable` were invoked with the Skill tool
on the built components, read from `CITY_SHOTS=…/BSUK-refs/manchester/_build-shots npm run
test:render:city` at 375 / 768 / 1024 / 1280 and from per-component shots (`task29-*.png`, the
sheet open at 375 and 768, the dial marking a later section at 1024 and 1280). The impeccable loader
again reported `hasProduct: false`; the brand context came from `rules/design.md` and the tokens.
The render gate first failed on the contents photo at 768 (`img-srcset-within-2x`: the canvas's
220px column painted the 540px served file at 2.45x, and on the six-row preview the cover crop
really was about 2x oversized).

| Component | frontend-design found | impeccable found (critique, harden) | Fixed | Widths |
|---|---|---|---|---|
| contents (icon rows) | The 220px photo column decoded the served file at 2.45x its painted width at 768 (blocking gate). Two row columns from 640 leave about 136px of text per row at 640. | Critique: one list, rows in page order down the columns, icon before name; nothing repeated. Harden: an opened phone list (13 rows, one column) would stretch the photo to about 830px, a 1.5x upscale. | The photo column is `clamp(272px, 34%, 340px)` from 640px (1.99x at most); the rows take two columns from 768px and the phone cut holds to 767px; the photo stops at 560px tall, bone below. Two-line rows at 768 are kept: balanced, inside the 56px row. | 375 · 768 (hidden at 1024 · 1280) |
| desktop dial (numeral rail) | The rail sat on its column's edge, so the current row's soft steel met the gutter (flush to the viewport on the full-width preview). | Critique: brass square on one numeral, labels in ink, no stripe (the Task 23 fix carried). Harden: 13 rows overflow a laptop-height column, so the marked row is kept in view inside the rail (`keepRowInBox`); RTL-safe hairline (`border-inline-end`); hidden in print. | Left inset `--space-3`, as the canvas's own padding; logical properties throughout. | 1024 · 1280 (hidden at 375 · 768) |
| jump links (question bar) | The current sheet row's bold question ran into the row's right edge (8px). | Harden: a tap on the sheet's own padding shut it (the dialog is the click target for its padding as for the backdrop); opening focused Close, not the question being read; the sheet relied on the UA's `:modal` overflow. | The backdrop tap is read against the sheet's box; opening focuses the current question; explicit `overflow-y: auto`, `overscroll-behavior: contain`; even row padding. The probe now holds both behaviours (it failed on the old handler, passes on the new). | 375 · 768 (hidden at 1024 · 1280) |

Behaviour proven outside the gates: the bar mounted as chrome (by an init script on the preview)
published `--strip-h: 64px`, tucked on a settled scroll down, came back on the way up, held while its
sheet was open, showed at the top, and had no transition under reduced motion. Its probe runs
wherever a bar carries `data-strip`, which the noindex scaffold (Task 32) will. Both new current-
section probes were mutation-checked: with `markCurrent` removed they fail under both motion
preferences.

Gates after the fixes: `npm run -s build` exit 0; `python3 -m pytest -q tests/py/test_city_kit_manchester.py
tests/py/test_city_kit.py tests/py/test_design_components.py` 161 passed, 1 skipped (the skip pre-dates
Task 28); `npm run test:render:city` 57 passed, 55 skipped, 0 failed, London's three routes unchanged
and no advisory on the Manchester route.

One full `npm run test:render:city` after the last fix failed once, at vp375 on the Manchester route
only: every question-bar behaviour at once (sheet, focus, spy), with the test running 47s. The
server log shows the bar's script chunk was never served during that test (its first request comes
40s later, from the next test), so the page ran without it. Reproduced on purpose and not met
again: the route alone at `--repeat-each=12 --workers=4` (12 passed), the whole vp375 project at
`--repeat-each=4 --workers=4` (68 passed), then a full run (57 passed, 0 failed). Not gated: a
static-server stall on a cold first load is a harness fact, and is recorded here rather than excused
in the probe.
