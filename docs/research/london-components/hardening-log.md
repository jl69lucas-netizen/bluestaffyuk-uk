# London Component Variants — Design and Hardening Log

One row per variant: the frontend-design direction it came from, what the impeccable pass found,
what changed, and the widths it was checked at. Shots: `/Users/apple/Downloads/BSUK/BSUK-refs/london/_variants/`.

**How the passes ran (Task 5: hero, counter strip, trust strip).** `frontend-design:frontend-design`
was invoked with the Skill tool on the brief in the plan's Task 5 Step 5 and the references its
ideas-index sections cite (every capture and sheet opened with the Read tool). It set three
directions per component before any file was written; the fonts and colours are the fixed BSUK
tokens, so distinctiveness comes from structure, not a new palette. `impeccable:impeccable` was
then invoked with the Skill tool (brand register). Its setup gate asks for a `PRODUCT.md`, which
this repo does not have and which only `/impeccable teach` (an interactive session with the user)
may write; the brand context it stands for was taken from the files `rules/gates.md`
`design-context-read-first` names (foundation spec, `data/settings.json`, `rules/design.md`,
`src/styles/global.css`, `src/styles/tokens.css`). Both of its assessments ran: the deterministic
detector (`npx impeccable --json` on the nine fragments) and a design review of the 27 shots at
375 / 768 / 1280. Its reflex-reject list names Fraunces; the display face is a locked brand token
(`rules/design.md` rule 2), so that finding is recorded and not acted on. The detector's
`cramped-padding` rows were false positives (it does not resolve padding that sits on the inner
wrappers), and its `side-tab` row on hero A is the full-width masthead rule, not a card stripe.

| Component | Variant | frontend-design direction | impeccable findings | Fixed | Widths |
|---|---|---|---|---|---|
| hero | a | **Broadsheet.** Editorial front page: a 4px steel rule over the band, a hairline under it, a column rule between copy and photo; the photo mounted as a slightly tilted postcard with a caption plate. Photo first in source, moved right by `order` at 1024+. | At 768 the 4:3 photo ran 540px tall and pushed the heading below the fold; heading held to 18ch wrapped to three lines at tablet widths. Detector `side-tab` on the top rule is a false positive (full-width masthead rule). Tilt already removed under reduced motion. | Tablet (640–1023) photo cropped 16:9 at 25% focus; heading widened to 22ch there. | 375 · 768 · 1280 |
| hero | b | **Litter filmstrip.** A deep-steel panel inset in the bone page; all six puppies as a contact strip along its foot (3×2 on phones, first in source), copy in two editorial columns above. | Name tags overhung the thumbnails at 1280 (grid rows stretched the list items taller than the photos). Detector flagged the uppercase eyebrow as "all-caps body"; it is a 31-character label, which the brand register allows. | Strip aligned to start; tags inset 8px inside the photo corner. | 375 · 768 · 1280 |
| hero | c | **Rail ticket.** Photo edge to edge as the window behind the band; the copy printed on a notched bone ticket with a Carlisle → London route line and a perforation; on phones the ticket slides up over the photo's foot. | The crop cut the puppy's eyes off at 768 and 1280 (centre focus on a square photo); "Door to door" wrapped to two lines on the route line at 375. | Focus moved to 18–22% from the top; the "Door to door" tag shows from 480px up only. | 375 · 768 · 1280 |
| counter-strip | a | **Docket.** The figures as an itemised bill: label, dotted leader, figure right-set in the display face with tabular numerals; three ruled columns under a steel top rule, a short caps title in the margin. | Five items in three columns left a hole in the grid; "Delivery to London, by distance" wrapped under its figure; the leader was an extra `<span>` inside `<dl>`, invalid markup. | Leader moved to `dt::after`; a sixth true figure (3 + 3 boys and girls) fills the grid; labels shortened so no line wraps at 1280. | 375 · 768 · 1280 |
| counter-strip | b | **Figure sentence** (was "Lead figure"). A litter photo beside one sentence a buyer can repeat, each figure raised in the display face on a steel-100 highlight. | The first build (a huge "6", small label, supporting stats, seam gradient) matched impeccable's banned hero-metric template exactly. | Rebuilt as the figure sentence; gradient seam replaced by a 3px steel rule; highlight held to 1.15em so line spacing stays even; meta name, layout slug and description updated. | 375 · 768 · 1280 |
| counter-strip | c | **Price scale.** The figures as stops on one broken number line, read in the order the money goes out (delivery range bar, deposit, a break, then the two prices); vertical on phones; inset on a steel-100 panel. | At 768 and 1280 the ticks and the range bar were drawn over the figures (the axis sat in the list's padding but the ticks were placed on each item). | Axis fixed at the top of the list, every stop padded 40px below it, ticks centred on the axis, the break glyph masked onto the line. | 375 · 768 · 1280 |
| trust-strip | a | **Route line.** The claims as stops on a transit-map line from the parents in Carlisle to a London door, line icons in the stop roundels, brass on the last stop; horizontal at 1024+, vertical below; ruled top and bottom, under its own question heading. | The "Carlisle" and "London" labels pushed their items' titles down, so the five titles sat on three baselines; the line ran past the last roundel; "HC-HSF4" broke at its hyphen. | Place labels lifted above the line; items align to start; at 1024+ the line ends on the last roundel's centre; test names wrapped in `nowrap`. (Correction from review: below 1024 the vertical line still ran past the last stop; fixed in the review round below.) | 375 · 768 · 1280 |
| trust-strip | b | **Seal band.** Six promises struck as brass-ringed seals with a dashed outer ring and a two-line label, across a full-width steel band; 2 / 3 / 6 across. | Titles sat on different heights because the list items stretched; checked brass-on-steel is used only for the icon rings (non-text), labels are bone on steel (AA). | Items align to start. | 375 · 768 · 1280 |
| trust-strip | c | **Photo ledger.** A raised sheet inset in the bone page: a litter photo left, a question heading and its answer, then a two-column ledger of icon, bold claim and one plain line. | A CSS comment said "white", which the validator refuses; two detail lines read as invented facts ("handled daily from birth", "in writing"); "HC-HSF4" broke at its hyphen. | Comment reworded; both lines replaced by allowed facts (ENS, speak to the vet); test names wrapped in `nowrap`. | 375 · 768 · 1280 |

Copy checks common to all nine: every heading is a Title Case buyer question with a 12+ word
answering paragraph; the deposit is always "£500 … books your viewing and reserves your puppy",
never plainly "refundable"; no licence, council or score claim; the guarantee appears only as
"a two-year genetic health guarantee" (the user's 2026-09-27 ruling); the parents are "the
parents, Angie and Lays" (superseded 2026-09-27 by the user: the parents are Maggie, the dam, and Jones, the sire; see the round-2 section); no em dashes in visible copy.

## Review round (Task 5 review, 2026-09-27)

The spec review found axes that flattered three designs, and a set of honesty and layout
faults. `frontend-design:frontend-design` was invoked again (Skill tool) for the three
redesigns (hero a, hero c, counter-strip a), and `impeccable:impeccable` again (Skill tool,
brand register, detector plus a shot review at 375 / 768 / 1024 / 1280) on every changed
variant. The smoke now also paints every frame at 1024 (`tests/render/canvas.config.ts`
project `vp1024`), where rule 10's 390–450px hero band starts. Measured bands: hero a 395px
at 1024/1100/1280; hero b 436 / 422 / 422; hero c 430.

| Component | Variant | frontend-design direction | impeccable findings | Fixed | Widths |
|---|---|---|---|---|---|
| hero | a | **Masthead** (replaces Broadsheet, which rendered copy-left/photo-right, the built `split/right` rows). Two tiers: the headline (up to 22ch) with a delivery ear, a rule, then three ruled columns: photo under the headline, the deck, the actions. No tilted postcard. Honest axes masthead / bottom / regular / rule. | A panoramic crop of Roman showed only his eyes at 1280; the CTA wrapped, then ran 3px past the content edge at 1024; detector repeats (masthead rule, short caps dateline) are false positives. | Photo column narrowed to 5/12 so the crop keeps the face; action column held to 256px minimum, CTA `nowrap` with tighter padding. | 375 · 768 · 1024 · 1280 |
| hero | b | Unchanged direction. | 464px tall at 1024 (rule 10 is 390–450); "One litter" is unconfirmed; the pill name tags looked tappable. | 1024–1199: heading at `--text-2xl`, strip photos 120px tall (436px at 1024); eyebrow "Six puppies · Carlisle to London"; tags are square corner plates on steel-900 with no pointer events. | 375 · 768 · 1024 · 1280 |
| hero | c | The photo now fills the whole band (`inset:0`) behind the ticket card. Honest axes ticket / background / regular / card. | "Door to door" was hidden under 480px; with the photo full width the ticket hid the puppy's face at 1024. | Route line reads "Carlisle → Your London door" at every width; the photo became Vennie with the ticket on the right. (Correction from round 2: at 1024 the ticket still covered half of Vennie's face, the 1080px square was upscaled and soft at 1280, and Vennie reads white on a Blue Staffy hero; fixed in round 2 below.) |
| counter-strip | a | **Price slip** (replaces Docket, which rendered as the built ruled columns beside a title). One torn-edge receipt slip inset in the bed, a single column read count, boy, girl, deposit, delivery, a running dotted rule between label and figure, and no total. Honest axes receipt / none / compact / inset. | The running rule first collided with "£200–£350"; figure hooks on `display:contents` rows had no box. | The rule is now each figure's own left border, so it runs unbroken and never overlaps; `data-figure` moved onto the figures. "3 + 3" dropped. Foot: "Each line is its own figure, not a running total." | 375 · 768 · 1024 · 1280 |
| counter-strip | b | Unchanged direction; framing relabelled `rule` (same bed and 3px rule as its siblings). | The newborn litter photo (about eight pups, some black) contradicted "6 puppies ready now" and was soft; "3 boys … three girls" was inconsistent. | A 2×3 grid of the six real puppies; "3 boys … 3 girls", each a figure. | 375 · 768 · 1024 · 1280 |
| counter-strip | c | Unchanged direction; relabelled so it never reads as a bill. | Boys and girls read as two consecutive charges and the deposit as an add-on. | Lead "Every figure you will meet, smallest to largest"; the price is one forked stop, "£1,500 a boy or £1,700 a girl, the price of one puppy"; the deposit says only what it does. | 375 · 768 · 1024 · 1280 |
| trust-strip | a | Unchanged direction. | Below 1024 the vertical line ran past the last (brass) stop; collection in Carlisle sat on the London stop; the eye stop did not say elbows. | The phone line is drawn per stop, from each roundel to the next, so it ends on the last one; collection moved to the intro; stop reads "Eyes and elbows screened". | 375 · 768 · 1024 · 1280 |
| trust-strip | b | Unchanged direction. | The bold pale-brass kicker read like a link. | Kicker emphasis is the display face in bone, not a link colour. | 375 · 768 · 1024 · 1280 |
| trust-strip | c | Unchanged direction; framing relabelled `card` (raised surface, card border, card shadow). | The same newborn litter photo, soft at 400×500. | Photo is the puppy-and-owner image at its own 400×437 ratio in a 360px column. | 375 · 768 · 1024 · 1280 |

## Review round 2 (Task 5, 2026-09-27)

`impeccable:impeccable` was invoked again (Skill tool, brand register): the detector on the
nine fragments (only the known false-positive classes: wrapper padding, short caps labels, the
masthead rule) and a shot review at 375 / 1024 / 1280 of every changed variant. Measured at
1024 / 1280: hero a 420 / 420px, hero b 436 / 422px, hero c 430 / 430px; counter a 275 / 255px.

**Parents (the user's ruling, 2026-09-27):** the parents are Maggie, the dam, and Jones, the
sire, as `data/faq.json` says. Every "Angie and Lays" is gone from the fragments (trust a, b
and c); trust c now shows the site's own photo of Maggie with her puppies
(`/images/maggie-blue-staffy-dam-with-pups.webp`), captioned as such.

| Component | Variant | frontend-design direction | impeccable findings | Fixed | Widths |
|---|---|---|---|---|---|
| hero | a | Masthead, unchanged. | The delivery note (not the deck) sits beside the headline, so the meta description was wrong; dead space beside the headline at 1280; Roman's ears cut off by the crop. | Meta description corrected; the headline runs full width on its first line and the delivery ear is a ruled column with the £200–£350 figure set in the display face; crop anchored near the top (ears mostly in, at the source's own edge). | 375 · 1024 · 1280 |
| hero | c | Rail ticket, unchanged direction. | See the correction above. | Photo is Cheryl, a solid blue girl with a white blaze (1080×1350, the tallest source). From 1024 to 1279 the photo is held at 1280px and anchored right so her face slides clear of the ticket; ticket narrowed to 440px (460 at 1280). Face clear at 1024 and 1280. | 375 · 1024 · 1280 |
| counter-strip | a | Price slip, made honestly inset. | The slip was drawn as a card (raised surface and card shadow) while declared inset; at 1024+ it was a 600×540 block, not a strip. | The receipt is pressed flat into a steel-100 panel with no shadow and no raised surface; from 1024 the five lines flow into two columns inside the one slip (count, boy, girl / deposit, delivery), figures in a fixed-width column; the "not a running total" note moved into the header. 255px tall at 1280. | 375 · 1024 · 1280 |
| counter-strip | c | Price scale, unchanged. | The lead was long. | Lead reads "6 puppies. What each part costs". | 375 · 1024 · 1280 |
| trust-strip | a | Route line, unchanged. | Parent names. | "The parents, Maggie and Jones". | 375 · 1024 · 1280 |
| trust-strip | b | Seal band, unchanged. | The kicker mixed two typefaces. | Kicker is one typeface (body), emphasis by weight only. | 375 · 1024 · 1280 |
| trust-strip | c | Photo ledger, unchanged direction. | The owner photo was soft and floated mid-card; parent names. | Photo is Maggie with her puppies at its own 780×585 ratio in a 390px column (sharp at 2x), top-aligned with the heading and captioned. Open: at 1024 the ledger is taller than the photo, leaving space under the caption; stretching the photo to fill it would upscale and soften it, so the space stays. | 375 · 1024 · 1280 |

## Task 6: contents list, desktop dial, jump links (2026-09-27)

**How the passes ran.** `frontend-design:frontend-design` was invoked with the Skill tool on the
brief in the plan's Task 6 Step 3, after every capture and idea sheet the three ideas-index
sections cite was opened with the Read tool, and the shipped `PageNav`, `PageDial`,
`SectionStrip` and `SectionSheet` were read. It set three directions per component. Every
must-differ row for these three components is `media: none`, `framing: plain`, so each
variant was built to differ on its layout **and** on framing (and, where the layout could be
read as a list, on media too), so that no honest re-reading of a layout brings it within one
axis of a row. `impeccable:impeccable` was then invoked with the Skill tool (brand register;
no `PRODUCT.md`, so the brand context came from the design-context files, as in Task 5): the
detector (`npx impeccable --json` on the nine fragments) and a design review of the shots at
375 / 768 / 1024 / 1280, plus viewport shots taken scrolled, with the sheet open and after a
jump from the sheet (`<component>-<v>-<width>-{top,scrolled,sheet,jumped}.png`). Detector
results: `cramped-padding` rows on every fragment are the known false-positive class (padding
on inner wrappers, hairline rows); `side-tab` on contents A is its full-width masthead rule.

**Interaction, all CSS.** The dials and the strips mark the current section with `:target`
(first section by default), and with a scroll-driven animation (`view-timeline` per section,
`timeline-scope` on the root, `animation-range: cover 50vh cover calc(100% - 50vh)`) where the
browser supports it and motion is not reduced. Each sheet is the `:target` of its opener; a
jump, the Close link or a tap on the scrim retargets to a fixed, zero-size anchor, so the sheet
closes without the page moving. Measured after a jump from the sheet at 375 and 768: the sheet
is closed and the target lands 12–28px below the strip on all three.

| Component | Variant | frontend-design direction | impeccable findings | Fixed | Widths |
|---|---|---|---|---|---|
| contents-list | a | **Ruled index.** A numbered index under a question heading and a steel masthead rule: display numeral, bold name and a one-line summary, hairline rows, two columns from 768px (from the numbered 'on this page' column and the hairline index sheet). | On phones the ten two-line rows ran about 950px under the hero; detector `side-tab` is the masthead rule. | Phone rows tightened (40px numeral column, 56px minimum rows). | 375 · 768 · 1024 · 1280 |
| contents-list | b | **Three stages.** The sections sorted by what the buyer is doing (Choose / Pay and book / Bring home) as three ruled link columns on a full-width steel band, bone text, brass stage numerals. | Clean at every width; stage labels are pale brass on steel (AA). | None needed. | 375 · 768 · 1024 · 1280 |
| contents-list | c | **Photo index.** A sunk steel-100 panel (no shadow) with a puppy photo at its left and the sections as generous arrow rows in two columns. | The first photo was the soft newborn litter shot with black pups (the photo Task 5's review rejected); at 768 the 4:3 photo on top ran 540px; at 1024 the two link columns wrapped every label. | Photo is Christa (1080px, sharp); 21:9 crop from 640 to 1023, 16:10 on phones; at 1024 the photo column is 4/12 so labels hold one line. | 375 · 768 · 1024 · 1280 |
| desktop-dial | a | **Page map.** A full-height steel band down the left edge draws the page as blocks, each as tall as its section, with faint text lines; the current block fills brass and a window frame slides down the map with the scroll. | Empty blocks read as broken buttons; the window was a fixed 64px, not the share of the page a screen shows. | Blocks carry faint text lines so the map reads as a page thumbnail; window is 18% of the map. | 375 (hidden) · 768 (hidden) · 1024 · 1280 |
| desktop-dial | b | **Clock face.** A raised card with the eight sections as line-icon stops round a ring, Roman's photo in the middle, and a readout naming the current stop; pointing at or tabbing to a stop names that one. | Icons alone do not name a section, so the readout and the hover/focus naming carry it, plus hidden link text for screen readers. | Readout default is section one; hover/focus overrides the scroll marker without a second name showing. | 375 (hidden) · 768 (hidden) · 1024 · 1280 |
| desktop-dial | c | **Photo marker.** A sunk steel-100 panel in the left margin: Cheryl's photo at its head, then the sections as plain labels along a thin track. | The current label was marked with a 4px left border, impeccable's side-stripe ban. | Rebuilt as stops on the track: every row has a small steel stop, the current one swells to a 14px steel stop with a raised row and bold type. | 375 (hidden) · 768 (hidden) · 1024 · 1280 |
| jump-links | a | **Stepper band.** A sticky steel band: eight numbered stops on one line (names under them from 600px), the current stop brass; a second row names the current section and is itself the key that raises the bottom sheet of section questions. | The first build scrolled the stops sideways, so after scrolling to Health the current stop was off screen with nothing marked. | All eight stops fit the width at 375 (44px each), no sideways scroll; the named row makes the place explicit. | 375 · 768 · 1024 (hidden) · 1280 (hidden) |
| jump-links | b | **Drop panel.** A sticky raised card: Maggie's photo, a wide "Jump to a section" control and a brass Enquire pill; the control drops a grid of icon tiles straight down from the card. | The strip showed no current section. | The control's small line now reads "Now 5 of 8 · Health", following the scroll. | 375 · 768 · 1024 (hidden) · 1280 (hidden) |
| jump-links | c | **Photo pager** (was "Photo tiles"). A sticky sunk steel-100 tray showing only the section you are in: its photo, "n of 8" and its name, with a step back and a step on; the All key slides in a side sheet. | The first build (a sideways row of eight photo tiles) hid the current tile off screen, as jump A did; the current name was cut with an ellipsis at 375. | Rebuilt as the pager (the steps work by `:target` alone); names wrap to two lines inside a 56px row; meta name, layout slug and description updated. | 375 · 768 · 1024 (hidden) · 1280 (hidden) |

Copy checks common to all nine: every heading is a Title Case buyer question with a 12+ word
answering paragraph; the deposit "books your viewing and reserves your puppy"; the parents are
Maggie, the dam, and Jones, the sire; DNA tests L-2-HGA and HC-HSF4 (held on one line), eyes
and elbows screened, the buyer may speak to our vet; Puppy Culture and ENS; delivery £200 to
£350 by DEFRA-approved transport, priced by distance, or collection in Carlisle; no licence,
travel time, distance, score or invented claim; no em dashes in visible copy. Stub sections are
labelled as stand-ins.

## Review round (Task 6 review, 2026-09-27)

The quality review found three important faults and a set of minor ones. `impeccable:impeccable`
was invoked again with the Skill tool (brand register) on all nine changed variants: the detector
(only the known false-positive classes: `cramped-padding` on wrapper padding and hairline rows,
`side-tab` on contents a's full-width masthead rule) and a review of re-shot frames at 375 / 768 /
1024 / 1280 plus the scrolled, sheet-open and after-jump viewport shots.

**Current-section marking (every dial and strip).** The scroll-driven marker was inside
`@media (prefers-reduced-motion:no-preference)`, so reduced-motion readers fell back to `:target`
and to a "first section is current" default: a mark stuck on section 1, or on the last jump. The
marker is state, not motion, so it now runs whatever the motion preference (its `animation-*`
longhands are `!important`, which also outranks the frame's reduced-motion reset). `:target` is
kept only where the browser has no scroll timelines, and every "first section is current" default
is deleted: nothing is marked rather than the wrong thing. Where a readout would then be empty it
shows a neutral base line ("Scroll, or point at a stop"; "8 sections on this London page";
"London page · 8 sections"), covered by the current name when there is one. Measured in Chromium
with `reducedMotion: 'reduce'` and `'no-preference'`: at the top and after a 1,900px scroll, all
six mark section 1 and then section 6, the same under both.

| Component | Variant | Review finding | Fixed | Widths |
|---|---|---|---|---|
| contents-list | a | About 690–850px tall on phones before the puppies; the lede claimed an order "most London buyers ask" (unverified). | Below 768px: five rows, then a `<details>` "5 more sections" holding rows 6–10 (all ten in two columns from 768px). Lede no longer claims buyer behaviour. Stubs tagged `data-canvas-only`. | 375 · 768 · 1024 · 1280 |
| contents-list | b | "The page runs in three stages". | "The sections fall into three stages". Stubs tagged `data-canvas-only`. | 375 · 768 · 1024 · 1280 |
| contents-list | c | About 850px on phones; the lede claimed what "some London buyers" want; meta said "litter photo". | Below 640px: five rows and a "5 more sections" disclosure, photo cropped 2:1; lede rewritten; meta says "puppy photo". | 375 · 768 · 1024 · 1280 |
| desktop-dial | a | The sliding window and the brass current block disagreed near the foot (two timelines, approximate block heights). | Window removed; the brass block is the only marker. | 1024 · 1280 |
| desktop-dial | b | Readout defaulted to section one. | Base line "Scroll, or point at a stop" under the current name; hover and focus still name any stop. | 1024 · 1280 |
| desktop-dial | c | Default first-row mark. | Removed; scroll timeline marks the row, `:target` only without scroll timelines. | 1024 · 1280 |
| jump-links | a | Below 600px the dots showed only numbers, so a buyer could not tell 5 was Health; the opener's `aria-label` ("See all 8 sections") did not contain its visible text. | Each stop is a line icon (paw, pound, ticket, van, shield, house, question, envelope), its name in `.lab` for screen readers and shown under it from 600px. The opener has no `aria-label`: its name is the current section plus "All 8" and a hidden " sections". The sheet row for the current section is tinted and bold. Axes unchanged (a stepper on a band). | 375 · 768 |
| jump-links | b | The 44px Maggie thumbnail had alt text though it is decorative. | The validator refuses `alt=""`, so the thumbnail is a CSS background on an `aria-hidden` span (media still `left`). The "Now 6 of 8 · Raising" line is part of the control's name. Sheet tile for the current section is outlined. | 375 · 768 |
| jump-links | c | Default first page in the tray. | A base "8 sections · On this London page" sits under the pages; the current page covers it. Sheet row for the current section is tinted. | 375 · 768 |

Copy: the FAQ stub no longer says what "most London buyers" ask; the Enquire stub reads "she can
price the delivery; you book a viewing with the £500 deposit". The "which one navigates at this
width" notes and every stub section carry `data-canvas-only` so Plan 2 never ports them.

## Task 7: key takeaways, puppy cards, tables (2026-09-27)

**How the passes ran.** `frontend-design:frontend-design` was invoked with the Skill tool on the
brief in the plan's Task 7 Step 3, after the captures and idea sheets the three ideas-index
sections cite were opened with the Read tool, and `PuppyCard.astro`, `InfoCard.astro`,
`DataTable.astro`, `global.css` `.stack-table` and the `layout-table-stacks-on-mobile` check
were read. Every must-differ row for these three components is `media: none`, and every
`framing` is `plain`, `band` or `card`, so each variant was built to differ on **media and
framing** at once (never on layout alone), so an honest re-reading of its layout cannot bring it
within one axis of a row. Puppy cards B is honestly a three-up grid, so it uses the row's slug
`grid-3` verbatim and differs on media (photo top) and framing (inset). `impeccable:impeccable`
was then invoked with the Skill tool (brand register; no `PRODUCT.md`, so the brand context came
from the design-context files, as in Tasks 5 and 6): the detector (`npx impeccable --json` on
the nine fragments) and a design review of the shots at 375 / 768 / 1024 / 1280. Detector
results: `cramped-padding` rows are the known false-positive class (padding on inner wrappers,
hairline rows); `side-tab` on key takeaways A, puppy cards A and tables C is the full-width 4px
masthead rule over the section; the six `side-tab` rows on puppy cards C were real (a 3px steel
top stripe on each name plate) and were removed. Mid-task the user moved the worktree to
`/Users/apple/Downloads/BSUK/BSUK-london` and the captures to `/Users/apple/Downloads/BSUK/BSUK-refs/`;
the shots were re-taken there.

| Component | Variant | frontend-design direction | impeccable findings | Fixed | Widths |
|---|---|---|---|---|---|
| key-takeaways | a | **Answer ledger.** An answer sheet under a steel masthead rule: Maggie and her puppies at the left, then five ruled rows of a short caps label and one sentence (the six, the deposit, the route, the parents, the promise). | At 1024+ the 4:3 photo left ~250px of dead space under it beside the taller list; stretching the photo to fill it upscaled the 780×585 source and cut Maggie's face; the lede said "one line each" over two-line rows. | From 1024 the heading and lede run across the top as one ruled-off row and the photo (1:1, focus on Maggie) sits beside the list only; lede reads "one sentence each". | 375 · 768 · 1024 · 1280 |
| key-takeaways | b | **Tick card.** One raised card on the bone page: a wide crop of Ince across its top, the question, four large-type lines each with a brass-filled tick disc, an Ask pill and a line about speaking to our vet. | Clean at every width; brass is a fill with steel-900 ink (AA), never text. | None needed. | 375 · 768 · 1024 · 1280 |
| key-takeaways | c | **Numbered decisions.** A sunk steel-100 panel: three decisions, each a large display numeral, a bold lead and one sentence, beside a tall photo of Cheryl filling the panel's right side (first on phones). | The lede called the puppy "she", which is wrong for the three boys. | "how your puppy reaches your door". | 375 · 768 · 1024 · 1280 |
| puppy-cards | a | **Kennel ledger.** The six as ruled ledger rows, not cards: square photo left, name in the display face, sex and colour, a green Available mark, the price set large at the right and a brass Ask pill; boys and girls as two ruled columns from 1024px. | The column heads repeated each row's price ("£1,500 each" over three £1,500 rows). | Heads read "3 available". | 375 · 768 · 1024 · 1280 |
| puppy-cards | b | **Contact sheet.** Six prints on a sunk steel-100 tray: a 4:5 photo (1:1 from 1024), a bone-50 mount with the name, a brass price tag, sex and colour, Available and an Ask link stretched over the whole print, so the print is the tap target. | On a phone the price tag sat beside some names and under others, and "Ask About Christa" wrapped to two lines with the arrow orphaned. | Below 768 the tag always sits under the name, the Ask line is one line at `--text-xs` with no arrow. | 375 · 768 · 1024 · 1280 |
| puppy-cards | c | **Litter wall.** An edge-to-edge photo mosaic with 2px bone seams; from 1024 Cheryl's tall photo takes a double square and the other five fill the squares round it, each named on a small raised plate in its lower corner; below 1024 an even two- or three-across wall with the plate under each photo. | The first mosaic used 2:1 wide panes: Vennie's face was cut by the full-width plate and Christa's was cropped to her nose; each plate carried a 3px steel top stripe (detector `side-tab`). | Mosaic rebuilt as a 3×3 grid (one 2×2, five near-square singles), plates shrunk to corner cards with no stripe; faces clear at 1024 and 1280. | 375 · 768 · 1024 · 1280 |
| tables | a | **Litter roster.** One real table of the six sunk in a steel-100 tray: a round photo and the name lead each row, then sex, colour, price in tabular figures and Available; no header band, zebra or brass rules. Rows become mini sheets on the tray below 640px. | The stacked view ran about 2,050px at 375 (every value on its own line); a first two-column fix used `display:grid` on the row, which the stacking check (rightly) reads as "not stacked". | Rows stay `display:block`; the four labelled values sit two to a line as inline blocks, label over value; about 1,580px at 375. | 375 · 768 · 1024 · 1280 |
| tables | b | **Payment schedule.** A full-width steel band: one table read as three steps (reserve, the puppy, getting home) on a brass numbered rail, bone text, pale-brass column heads, with a photo of a young owner hugging a blue puppy beside it (first on phones). | The heading asked "and When", which the table does not answer (it gives order, not dates); the caption repeated the heading; the lede called the puppy "her". | Heading "What Will You Pay for a Puppy in London, Step by Step?"; caption "Three payments, in order"; lede reworded. | 375 · 768 · 1024 · 1280 |
| tables | c | **Boy or girl.** A two-column comparison headed by photos of Roman and Vennie with "Boys" / "Girls" under them; rows of price, names, colours, deposit and delivery between hairlines under a steel masthead rule; on a phone the photos stay side by side and each row stacks into two labelled answers. | The empty corner cell showed a stray "Compare" label; the lede claimed "everything else is the same". | Corner label is screen-reader only ("What differs"); lede says only that the deposit and delivery are the same for both. | 375 · 768 · 1024 · 1280 |

Copy checks common to all nine: every heading is a Title Case buyer question with a 12+ word
answering paragraph; the six puppies, sexes, colours and prices are `data/puppies.json`'s; the
deposit "books your viewing and reserves your puppy" and "comes off the price"
(`data/faq.json` `home-price-range`), never plainly "refundable"; the parents are Maggie and
Jones, DNA-tested clear of L-2-HGA and HC-HSF4 (held on one line), eyes and elbows screened;
Puppy Culture and ENS; a two-year genetic health guarantee; the buyer may speak to our vet;
delivery £200 to £350 by DEFRA-approved transport, priced by distance, or collection in
Carlisle; no licence, travel time, distance, score, age or invented claim; no em dashes in
visible copy. Every `<td>` carries `data-label`, every table has a `<caption>` and `<th scope>`.

## Review round (Task 7 review, 2026-09-27)

`impeccable:impeccable` was invoked again with the Skill tool (brand register) on the seven
changed variants (puppy cards a, b and c, tables a, b and c, key takeaways b): the detector
(only the known false-positive classes: `cramped-padding` on wrapper padding and hairline rows,
`side-tab` on the full-width 4px masthead rules of puppy cards a and tables c) and a review of
re-shot frames at 375 / 768 / 1024 / 1280.

**One media convention for puppy cards.** `media` is read at section level: a photo on each
card is not section media (the built S1–S3 rows are `media: none` though their cards carry
photos). Ledger A and Litter wall C therefore declare `media: none` and differ from every row
on layout and framing; Family sheet B carries a real section photo.

| Component | Variant | Review finding | Fixed | Widths |
|---|---|---|---|---|
| puppy-cards | a | No delivery line on the cards; two ruled columns at 1024+ could honestly read as S2's two-up grid. | One ruled column of line entries (photo, name, sex, colour, Available, the canonical delivery line, price in a fixed column, Ask pill); boys then girls. Axes `ledger / none / compact / rule`. | 375 · 768 · 1024 · 1280 |
| puppy-cards | b | **Critical:** "Contact sheet" was S1's shipped three-up photo-topped grid on a tray, differing on framing only. | Redesigned as **Family sheet**: the sunk tray opens with a section-level photo of Maggie, the dam, with her puppies beside the question and answer, then the six prints (each now with the delivery line). Axes `grid-3 / left / regular / inset` (row slug kept verbatim; differs from S1 on media and framing). Lede "before you ask" (no phone is published). | 375 · 768 · 1024 · 1280 |
| puppy-cards | c | No delivery line; density declared airy for an edge-to-edge wall with 2px seams; Roman's ear tips cut at 1280; below 1024 an even three-across grid. | Delivery line on every plate (band held on one line; fits at 375 in three short lines); density `compact`, media `none`; Roman shows his gallery photo `Roman1.jpg` with his face clear of the plate; from 640 to 1023 Cheryl and Christa run full width around a two-across middle. | 375 · 768 · 1024 · 1280 |
| tables | a | Stacked rows ran about 1,580px; the footnote did not say delivery is extra. | Each stacked row is two lines (photo, name and price; then sex · colour · Available), about 510px for the six; footnote: delivery is extra (£200 to £350 by distance) or collect in Carlisle, and the £500 comes off the price. | 375 · 768 · 1024 · 1280 |
| tables | b | "What you pay" beside "Three payments, in order" invited adding the £500 twice; the caption was sentimental. | Caption "Three figures, in order"; columns Step / Figure / What it means; step 2 "The puppy's price": "the £500 deposit comes off it, so it is never paid twice"; photo caption "A blue Staffy puppy in a family garden". | 375 · 768 · 1024 · 1280 |
| tables | c | Roman's ear tips cut in the column photo. | Crop anchored near the top (22% 5%). | 375 · 768 · 1024 · 1280 |
| key-takeaways | b | "The price on the card is the price" left out getting the puppy home. | "The price on the card is the puppy's price, plus delivery or collection". | 375 · 768 · 1024 · 1280 |

The deposit is phrased one way everywhere: "£500 books your viewing and reserves your puppy,
and it comes off the price" (`data/faq.json` `home-price-range`).

## Task 8: video, image and text, reviews (2026-09-27)

**How the passes ran.** `frontend-design:frontend-design` was invoked with the Skill tool on the
brief in the plan's Task 8 Step 3, after every capture and idea sheet the three ideas-index
sections cite was opened with the Read tool (4 for video, 24 for image and text, 8 for reviews),
and `VideoEmbed.astro`, `data/settings.json` `youtube_embeds`, `data/reviews.json` and the
served images' own alt text (`data/verbatim/*.json`, `data/locations.json`) were read. **One media
convention for all three:** `media` is read at section level. For video the poster inside the
facade is the video, not section media (the built S3 facade row is `media: none`), so each video
variant carries a real section photo besides its poster; with every must-differ row at
`media: none` and framing `card` / `band` / `plain`, every variant differs from every row on
media AND framing (and a reviewer who reads every video layout as `facade` still finds two axes
from S3). `impeccable:impeccable` was then invoked with the Skill tool (brand register; no
`PRODUCT.md`, whose loader reported `hasProduct: false`, so the brand context came from the
design-context files as in Tasks 5 to 7): the detector (`npx impeccable --json` on the nine
fragments) and a design review of the shots at 375 / 768 / 1024 / 1280. Detector results:
`cramped-padding` rows are the known false-positive class (padding on inner wrappers, hairline
rows); `side-tab` on video B and image and text A is the full-width 4px masthead rule over the
section; the `side-tab` on reviews C was real (a 4px steel stripe on the plate) and was replaced
by a 1px inset border. Every video is the facade for `g9iV9RVr_Sk` (the one id in
`data/settings.json` the guide page carries); its accessible name is the guide board's existing
title, never a new one, and nothing loads from YouTube.

| Component | Variant | frontend-design direction | impeccable findings | Fixed | Widths |
|---|---|---|---|---|---|
| video | a | **Screening room.** A deep-steel band like a darkened cinema: the question centred, one wide 16:9 facade (Maggie and two puppies as the poster), and a programme line under it with the caption and a round print of Jones, the sire. Axes `screening / bottom / airy / band`. | The centred play disc sat on the grey sofa between the dogs and read as part of the photo; the frame ran wider than the 780px poster, so the image was upscaled at 1280. | Disc moved to the poster's clear lower-left corner; screen held to 780px so the poster is never upscaled; `font:inherit` on the button. | 375 · 768 · 1024 · 1280 |
| video | b | **Portrait reel.** Rules only (4px steel masthead, hairline foot): the copy column with a short accent rule, the answer and an inline print of a puppy with its new owner, beside a tall 4:5 facade of Cheryl with a brass disc at its foot. Axes `reel / inline / regular / rule`. | The validator refused a `<span>` accent rule between the heading and its paragraph; the inline print's caption hung at the print's foot, leaving a gap. | Accent rule drawn as the heading's `::after`; the print caption centred on the photo. | 375 · 768 · 1024 · 1280 |
| video | c | **Side panel.** A sunk steel-100 tray: a wide 16:9 facade of Christa with a brass "Play the film" pill, beside a panel with Ince's photo and three ruled facts (parents, price, getting home). Axes `side-panel / right / compact / inset`. | At 768 the panel was a narrow column under a short screen, with a tall empty area below the screen; Christa's ear tips were cut at 16:9. | Below 1024 the panel drops under the screen, Ince's photo beside the facts from 640px; the poster crop anchored near the top (50% 4%). | 375 · 768 · 1024 · 1280 |
| image-text | a | **Flanked portrait.** Under a steel masthead rule, a centred question and answer; a tall photo of a young owner hugging a blue puppy stands in the middle with three numbered, ruled points on each side (parents, DNA, eyes and elbows; Puppy Culture and ENS, the vet, the guarantee). Axes `flank / inline / regular / rule`. | On a phone the 540×664 photo ran about 420px tall before the first point, and the two lists met with a double rule. | Below 1024 the photo is cropped 4:3 round the faces and the points run two columns from 640px; the double rule removed. | 375 · 768 · 1024 · 1280 |
| image-text | b | **Offset block.** A steel-100 block bleeds off the left page edge with the London owner photo offset on it at no more than its own 400px; to the right the question, a label and value spec sheet (deposit, price, getting home, parents, guarantee) and a brass Ask pill. Axes `offset / left / regular / bleed`. | The lede promised "agreed in writing", which no file states; the alt had been rewritten. | Lede reworded to what the page shows; the image keeps its served alt text word for word (working rule 11). | 375 · 768 · 1024 · 1280 |
| image-text | c | **Two chapters.** A sunk steel-100 tray, Carlisle then London: each chapter a brass numeral, an H3 question, its own photo straight after the heading, then the answering prose (`layout-h3-image-first`). Axes `chapters / inline / compact / inset`. | At 4:3 the phone photos ran tall; the London photo's crop sat low. | Photos 3:2 with a focus near the faces. | 375 · 768 · 1024 · 1280 |
| reviews | a | **Owner's letter.** Mark J's London review word for word on a raised card (surface, card border, card shadow), his own photo from the site at the left (the pairing the homepage already makes), a large quote mark and a signed foot. Axes `letter / left / airy / card`. | The brass quote mark failed AA (2.42:1) as text on white; the photo was painted at 260px beside the quote at 768 with dead space under it; a caption implied more than the file says. | Quote mark in steel-500; two columns from 1024 only (photo at its own 319px width above the quote below that); the caption removed. | 375 · 768 · 1024 · 1280 |
| reviews | b | **Two London notes.** A sunk steel-100 tray that opens on a wide, credited photo of Vennie, then the two reviews that give London as home, one per slot, stacked in one column; the second stepped in from the left. Axes `stack / top / compact / inset`. | Both quotes were the same heavy display face, so the long review ran about 900px on a phone; the 21:9 photo was a sliver at 375. | The short review is set large in the display face, the long one in the body face; the photo is 16:9 below 768. | 375 · 768 · 1024 · 1280 |
| reviews | c | **Kennel wall.** A photo of Jones, credited as the sire so it never reads as the reviewer's dog, bleeds to the right page edge; a bone plate overlaps its left edge with the question and Rachel L.'s review set large. On a phone the photo leads and the plate rises over its foot. Axes `overlap / right / regular / bleed`. | Detector `side-tab`: a 4px steel stripe on the plate. | Stripe replaced by a 1px inset border; the quote set at weight 600. | 375 · 768 · 1024 · 1280 |

Copy checks common to all nine: every heading is a Title Case buyer question with a 12+ word
answering paragraph that names London; reviews are only `data/reviews.json` rows 1 (Mark J) and 2
(Rachel L.), word for word with `data-review`, one per slot, with no star, score or
AggregateRating; the deposit reads "£500 books your viewing and reserves your puppy, and it
comes off the price"; the parents are Maggie and Jones, DNA-tested clear of L-2-HGA and HC-HSF4,
eyes and elbows screened; Puppy Culture and ENS; the buyer may speak to our vet; a two-year
genetic health guarantee; delivery £200 to £350 by DEFRA-approved transport, priced by
distance, or collection in Carlisle; no licence, travel time, distance, age or invented claim;
no em dashes in our own visible copy (the two em dashes on the canvas are inside Rachel L.'s
verbatim review, and the video's accessible name is the guide board's existing title).

## Review round (Task 8 review, 2026-09-27)

`impeccable:impeccable` was invoked again with the Skill tool (brand register, no `PRODUCT.md`)
on the changed variants: the detector on video a and b, image and text a and c, reviews b and c
(only the known false-positive classes: `cramped-padding` on wrapper padding and hairline rows,
`side-tab` on the full-width 4px masthead rules of video b and image and text a), and a review
of re-shot frames at 375 / 768 / 1024 / 1280.

**Served alt text (working rule 11).** Every served image now carries its served alt word for
word, copied from `dist/`: `ethical-staffy-puppy-london-delivery.webp` (image and text a and c,
video b), `maggie-blue-staffy-dam-with-pups.webp` (video a, image and text c),
`jones-strong-staffy-sire-temperament.webp` (video a) and `jones-magnificent-blue-staffy-sire.webp`
(reviews c). The unconfirmed ages and the "Mark and Emma P." credit they contain are listed in
`plan2-notes.md` under "Alt text — awaiting the user's ruling"; the visible captions state none
of them.

| Component | Variant | Review finding | Fixed | Widths |
|---|---|---|---|---|
| video | a | **Critical:** the 88px round Jones thumbnail was a token, so "Screening room" was honestly S3's facade on a band (one axis). | Redesigned as **Double bill**: the facade takes two thirds of the row and a full-height print of Jones, the sire, takes the other third at the same height, named on a plate at its foot clear of his face; two notes run under the pair (caption; parents and DNA). Below 768px the screen runs full width and the print (a third of the row) sits beside the notes. Axes `double-bill / right / airy / band`: from S3 media and framing, from S2 layout and media. First re-shoot: at 768 a tall caption plate covered Jones's face; the plate now carries only his name. | 375 · 768 · 1024 · 1280 |
| video | b | Rewritten alt on the owner photo. | Served alt restored. | 375 · 768 · 1024 · 1280 |
| image-text | a, c | Rewritten alts on the owner and Maggie photos. | Served alts restored. | 375 · 768 · 1024 · 1280 |
| reviews | b | Vennie's muzzle cut at the foot of the banner. | Crop 50% 40%. | 375 · 768 · 1024 · 1280 |
| reviews | c | "Buy From Us Again" asked what the review does not literally answer; rewritten alt on Jones. | Heading "Would a London Owner Recommend Us?" (answering paragraph kept); served alt restored. | 375 · 768 · 1024 · 1280 |

## Task 9: FAQ blocks, newsletter, contact form (2026-09-27)

`frontend-design:frontend-design` was invoked with the Skill tool on the plan's Task 9 Step 3
brief and the three components' ideas-index entries (every capture and sheet cited in the three
`meta.json` files opened with the Read tool). It set three directions per component before any
file was written; the fonts and colours are the fixed BSUK tokens. `impeccable:impeccable` was
then invoked with the Skill tool (brand register). No `PRODUCT.md` exists and only
`/impeccable teach` (interactive, with the user) may write one, so the brand context was taken
from `rules/design.md`, `src/styles/tokens.css`, `data/settings.json`, `src/styles/global.css`
and the foundation spec, as in Tasks 5 to 8. Both assessments ran: the detector
(`npx impeccable --json` on the nine fragments: only the known false-positive classes,
`cramped-padding` on wrapper padding and hairline `<details>` rows whose padding sits on the
`<summary>`, and `side-tab` on the full-width 4px rules of FAQ c, newsletter c and contact a)
and a review of the shots at 375 / 768 / 1024 / 1280. The smoke passed first time; every fix
below came from the shot review, and the smoke and `check:canvas` were re-run after it.

**Copy (all nine).** The FAQ carries 19 questions in three blocks (6 buying from London, 6
checking us from afar, 7 a Staffy in a London home), the location template's top / middle /
bottom split; every question and block heading is a Title Case buyer question ("If" capitalised,
as `rules/headings.md` lists it among no lowercase words), every answer 20+ words, and no
question repeats a block heading. Facts only: the six puppies, sexes and colours from
`data/puppies.json`; £1,500 / £1,700; the £500 deposit "books your viewing and reserves your
puppy, and it comes off the price" (never plainly refundable; the 70% no-show refund was left
out rather than risk misstating it); delivery £200–£350 by DEFRA-approved transport, priced by
distance, or collection in Carlisle; Maggie the dam and Jones the sire, KC registered, DNA
tested clear of L-2-HGA and HC-HSF4, eyes and elbows screened (no grade); buyers may contact
our vet; a two-year genetic health guarantee; take-back if the fault is ours or the owner can
no longer keep the puppy; Puppy Culture and ENS; the 24 to 48 business-hour reply
(`data/faq.json`); breed answers from `data/faq.json` (flats, exercise, children, time alone,
training, first dogs, the 12 to 14 year lifespan from the Staffordshire Bull Terrier Club). No
age, licence, statute, distance, travel time, score or "most buyers". The newsletters promise
nothing but a note when a litter is due. The forms carry the `bsuk-contact-form` field
contract (name, email, phone, location, puppy, message; labels "Your name", "Email", "Phone",
"Town or postcode", "Which puppy?", "Message"; name, email, puppy and message required; the six
puppies plus the next litter as options), no `action`, `PHONE_PLACEHOLDER` where a number would
be, submits on `--btn-form-radius`, and error states drawn with `:user-invalid` (a warn border
and a one-line message per required field, no script); the success state is the reply line
beside each submit.

| Component | Variant | frontend-design direction | impeccable findings | Fixed | Widths |
|---|---|---|---|---|---|
| faq-blocks | a | **Steel ledger.** One deep-steel band: the site's photo of Maggie with two pups on a sticky rail at the left from 1024, the three blocks as one numbered ledger (01 to 19) beside it, brass-200 numbers, a brass plus that turns to a minus. On a phone the photo is a short 16:9 strip on top. Axes `photo-rail / left / regular / band`. | At 1280 the 4:5 crop cut Maggie in half and lost a pup; below the photo the rail was an empty column. | Whole-scene 4:3 crop at 1024+ (all three dogs, faces clear); three figures in brief under the caption (deposit, delivery, guarantee) as a ruled `<dl>`, not links, so the rail reads as content and never as a jump list. | 375 · 768 · 1024 · 1280 |
| faq-blocks | b | **Three trays.** The three blocks side by side from 1024 as sunk steel-100 trays (hairline edge, no shadow), each with a "1 of 3" tag, its question and answer and tight chevron rows; one 720px column below 1024. Axes `tri-column / none / compact / inset`. | Clean at every width; the rows are 48px, the chevron is drawn in CSS, and the hover underline sits on the question only. | No change. | 375 · 768 · 1024 · 1280 |
| faq-blocks | c | **Lead answer.** Each block under a 4px steel rule: question left, answer right from 1024; the block's first question open as a large lead; the rest folded into a two-column grid of hairline rows with plus marks. Axes `lead-grid / none / airy / rule`. | The lead answer was set in the display face, which the frame loads only at 600/700, so it painted bold, and rule 2 keeps body copy in `--font-body`. | Lead answer in the body face at `--text-lg`, weight 400. | 375 · 768 · 1024 · 1280 |
| newsletter | a | **Litter notice.** A raised card (card border, radius, shadow): Christa's photo on the left from 768, a strip on top on a phone; a ruled eyebrow, the question, its answer, a stacked email field over a full-width brass submit. Axes `split / left / regular / card`. | Clean; Christa's face clear at every crop. | No change. | 375 · 768 · 1024 · 1280 |
| newsletter | b | **Steel band.** A compact centred steel-700 band: a brass line-icon envelope, the question in bone, one joined row of field and brass submit (stacked on a phone). Axes `centred / none / compact / band`. | The lede left a one-word orphan ("for.") at 1280. | Lede to 58ch with `text-wrap: pretty`. | 375 · 768 · 1024 · 1280 |
| newsletter | c | **Ruled row.** Open bone page between a 4px steel rule and a hairline: question left, field and submit on one line right from 1024, two ticked lines under it. Axes `inline-row / none / airy / rule`. | The submit was a steel fill; rule 1 gives every button the brass CTA role. A lede line ("Plenty of London families find us between litters") was an unsupported claim. | Brass submit with `--color-cta-ink`; lede rewritten to what the list is for. | 375 · 768 · 1024 · 1280 |
| contact-form | a | **Letter to Carlisle.** The enquiry as a ruled letter: "Dear Lisa," then one sentence per line, each ending in a real field with its label printed under it (name, part of London, which puppy, email, phone), then the message and "Send my letter". Axes `letter / none / airy / rule`. | Two blanks per sentence wrapped at 1280 and left ", London." and "." stranded on their own lines at 375; the letter lines were in the display face (bold, and against rule 2). | One blank per line with no trailing punctuation ("My part of London is ___", "If it is easier, call me on ___"); letter lines in the body face at `--text-lg`. | 375 · 768 · 1024 · 1280 |
| contact-form | b | **Litter line-up.** A deep-steel band: the question, the six puppies as a line-up of square photos with name, sex and price plates (3 × 2 on a phone, 6 across from 768; `pointer-events: none`, no hover, so nothing looks pressable), then a compact form straight on the band, three fields to a row at 1024. Axes `lineup / grid / compact / band`. | Default `<p>` margins opened 40px gaps between the fields, so "compact" was not true. | Field wrappers `margin: 0`. | 375 · 768 · 1024 · 1280 |
| contact-form | c | **Doorstep tray.** A sunk steel-100 tray: the site's photo of a puppy with its new family in London (served alt kept) on the left from 1024 with a caption and "Rather talk it through? Call PHONE_PLACEHOLDER" at its foot; the question, its answer and a two-up form on the right. Axes `photo-split / left / regular / inset`. | At 1024 and 1280 the photo stopped halfway down a column the form made twice as tall. | The photo grows to the form's height (flex, cover, focus 45% 50%; about 650px tall at 1280, close to its 664px source height, a little taller at 1024); the call line sits at the column foot. | 375 · 768 · 1024 · 1280 |

## Plan 2 — built components

**Task 2: hero B, counter strip C, trust strip C (2026-09-28).** Built on `/kit-preview/city/` and shot
at 375 / 768 / 1024 / 1280 (`CITY_SHOTS=/Users/apple/Downloads/BSUK/BSUK-refs/london/_plan2-shots npm
run test:render:city`, plus one element shot per component, `built-<component>-<width>.png`, and a
canvas-beside-built pair, `pair-<component>-<width>.png`, in the same folder, against
`BSUK-refs/london/_variants/`). `impeccable:impeccable` ran first and `frontend-design:frontend-design`
second (the controller's order for this task). As in Plan 1, impeccable's `PRODUCT.md` gate is
unmet: no such file exists and only `/impeccable teach` with the user may write one, so the brand
context came from the `design-context-read-first` files. Its detector (`npx impeccable --json`)
found nothing in the three `.astro` sources. On the built preview it raised four warnings, none of
them on a component: Fraunces is the locked display token (rule 2); the `side-tab` row is the
counter bed's full-width 3px steel top rule, which rules/design.md's hero/counter separation asks
for; `flat-type-hierarchy` read the preview page's own 16px heading; `clipped-overflow-container`
is the site's `overflow-x: clip` on `html`.

| Component | impeccable found | frontend-design found | Changed | Widths |
|---|---|---|---|---|
| hero (CityHero, B) | The "more" link painted without its underline: the site's preflight sets links to `text-decoration: inherit`, and the canvas frame, which has no preflight, underlined it. On the steel band it was told apart by colour alone (WCAG 1.4.1). | Strip, name plates, brass CTA and the 1024–1199 step match the frame; every face stays whole at 120px and 148px thumbs; the band is 422px at 1024 and 1280 (rule 10: 390–450). | `.more` restates `text-decoration: underline`. | 375 768 1024 1280 |
| counter strip (CityPriceScale, C) | No finding on the component. | The number line, the pill range stop, the break mark and the boy/girl fork match at every width; the phone's vertical line is identical. | Nothing. | 375 768 1024 1280 |
| trust strip (CityTrustLedger, C) | No finding on the component. | Card, stretched photo column and two-column ledger match. Jones stands in for Maggie (one served photo per page, Code facts 4) and the guarantee claim is dropped (`guarantee_days` null). The canvas held `L-2-HGA` / `HC-HSF4` in nowrap spans; the plain-string prop has no such guard. They do not break at the four widths, so this is left to the city page's copy step. | Nothing. | 375 768 1024 1280 |

**Task 3: contents list C, desktop dial C, jump links A and the sheet (2026-09-28).** Built on
`/kit-preview/city/` and shot at 375 / 768 / 1024 / 1280, with the states the canvas recorded:
the contents disclosure open (375), the dial after a scroll (1024, 1280), the band after a scroll,
with the sheet open, and after a jump from the sheet (375, 768). Element and state shots are
`built-<component>-<width>[-state].png`, and canvas-beside-built pairs are
`pair-<component>-<width>[-state].png`, all in `BSUK-refs/london/_plan2-shots/`, against
`_variants/contents-list-c-*`, `desktop-dial-c-*` and `jump-links-a-*`. Two things were set up only
for the shots. The preview's own site header was hidden so it could not cover an element shot. In
the scrolled shots the dial and the band were pinned (`position: fixed`), because on the preview
they sit in their own sections; on a city page they are PageShell's sticky column and header band
(Task 8). `impeccable:impeccable` ran first and `frontend-design:frontend-design` second. The
`PRODUCT.md` gate is still unmet, for the reason given under Task 2. The detector
(`npx impeccable --json`) found nothing in the three `.astro` sources. On the built preview it
raised the same three page-level warnings as in Task 2 (Fraunces, the counter bed's rule, `html`
overflow clip) and none on a nav component.

Behaviour, as measured in the painting browser:
- Opening the sheet moves focus to Close. After 12 Tabs focus is still inside the dialog, so focus
  is trapped.
- Escape closes the sheet, and the key goes back to `aria-expanded="false"`.
- Opening and closing the sheet adds 0 history entries. A sheet link adds one, as any in-page
  anchor does.
- After a scroll the rail, the sheet, the key's line ("03 Checks") and the dial all mark the
  third section.
- The render probe `city-nav-current-section` passes under `reducedMotion: reduce` and under
  `no-preference`. To show it is not vacuous, the spy was frozen on row one, which is what the
  canvas's reduced-motion reader saw (L8). The probe then failed at all four widths under both
  settings ("section kit-city-contents in the reading band, current is [kit-city-hero]"), and it
  passed again once the spy was restored.

| Component | impeccable found | frontend-design found | Changed | Widths |
|---|---|---|---|---|
| contents list (CityContents, C) | The disclosure read "1 more sections" with the preview's six sections. The plan's CSS had no 1200px step: the frame's body padding grows to `space-9 space-8` there, and the built panel stayed at `space-8 space-7`, which is 8px short at each side. | Photo column, sunk steel-100 panel (no shadow), balanced heading, two-column arrow rows from 640px and the 2:1 / 21:9 phone crops match the frame. It is one list, and the phone disclosure opens it in place ("Fewer sections" when open). | The label is singular for one row. Added the `min-width: 1200px` padding step. | 375 768 1024 1280 |
| desktop dial (CityDial, C) | No finding on the component. Its corners clip the photograph (checked by pixel). | Track, swollen brand stop, raised current row and uppercase title match the frame. The crop is the focus map's (`fx-40 fy-45`, the face's centre) rather than the frame's hand-set `50% 28%`: it sits about 100px lower in the portrait and trims the raised paws, but the face is whole. Hidden below 1024px. | Nothing. | 1024 1280 (375 and 768: not painted, by design) |
| jump band and sheet (CityJumpBand, A) | The sheet had 20px gutters on a phone: the UA stylesheet's dialog `max-width: calc(100% - 2em - 6px)` beat `width: min(100%, 560px)`, and the frame's sheet runs edge to edge. | Stepper rail (brass current stop, names from 600px), the key with its brass numeral and "ALL n", the bottom sheet with its grab bar, Close pill and numbered question rows all match the frame at 375 and 768. On the preview a jump cannot bring its target to the top, because the preview's last sections sit at the foot of the page. The landing is measured on the real page by `nav-jump-target-lands` (Task 8). | The sheet sets `max-width: 100%`. | 375 768 (1024 and 1280: not painted, by design) |

**Task 4: key takeaways A, puppy cards B, tables A (2026-09-28).** Built on `/kit-preview/city/` and
shot at 375 / 768 / 1024 / 1280 (`CITY_SHOTS=… npm run test:render:city`, plus one element shot per
component, `built-<component>-<width>.png`, and a canvas-beside-built pair,
`pair-<component>-<width>.png`, in `BSUK-refs/london/_plan2-shots/`, against
`_variants/key-takeaways-a-*`, `puppy-cards-b-*` and `tables-a-*`; the keyboard focus state of a
print is `built-puppy-cards-b-375-focus.png`). `impeccable:impeccable` ran first and
`frontend-design:frontend-design` second. The `PRODUCT.md` gate is still unmet, for the reason given
under Task 2. The detector (`npx impeccable --json`) raised one warning on the three sources,
`border-accent-on-rounded` at `CityTakeaways.astro` `border-top: 4px solid`: a false positive, since
that rule is the pick's full-bleed 4px steel rule on the section root, which has no radius.

| Component | impeccable found | frontend-design found | Changed | Widths |
|---|---|---|---|---|
| key takeaways (CityTakeaways, A) | No finding on the component beyond the detector's false positive. | Rules-only ledger, photo first on phones, 21:9 crop from 640, head across the top with the square photo beside the list from 1024: all match the frame. Jones (`jones-strong-staffy-sire-temperament.webp`) stands in for Maggie (one served photo per page, Code facts 4); the canvas's fifth row stated a two-year guarantee, and the specimen's fifth row does not (`guarantee_days` null). At 768 the full-width 21:9 crop paints the 663px master at 736px: `img-not-upscaled` advisory, 1.11x. No larger master exists; left for the city page, whose column is narrower. | Nothing. | 375 768 1024 1280 |
| puppy cards (CityPuppySheet, B) | On a phone the delivery line broke inside the band ("£200–" / "£350"); the frame held the band on one line (plan2-notes, Task 7). | Sunk tray, family photo beside the question, prints two-up then three-up, brass price tag, status, delivery line and the stretched Ask link match at every width. Every photo hands the tap to its Ask link (render probe); keyboard focus draws the 3px ring round the whole print. | The band renders in a `nowrap` span, split out of `deliveryLine` itself so the canonical words keep one source. | 375 768 1024 1280 |
| table (CityRoster, A) | At 375 the last row's price painted at 15px, not 20px: `tbody tr:last-child td` outranked `tbody td.num`. | The price column sat LEFT at 768 and up, while the frame right-aligns it: Astro's scoped `.num` (one class + one attribute) lost to `tbody td` / `thead th` (two elements + two attributes). Otherwise the semantic table, round photos, display-face names, 2px brand rule under the head and the phone's two-line slips match. The foot is the canonical delivery line and the deposit line from `src/lib/cityKit.ts`, not the frame's hand-typed "£200 to £350" sentence. | `thead th.num, tbody td.num` right-align the price; the phone rule adds `tbody tr:last-child td.num`. | 375 768 1024 1280 |

**Task 5: video C, image and text C, reviews A (2026-09-28).** Built on `/kit-preview/city/` and shot
at 375 / 768 / 1024 / 1280 (`CITY_SHOTS=… npm run test:render:city`, plus one element shot per
component, `built-<component>-<width>.png`, and a canvas-beside-built pair,
`pair-<component>-<width>.png`, in `BSUK-refs/london/_plan2-shots/`, against `_variants/video-c-*`,
`image-text-c-*` and `reviews-a-*`). `impeccable:impeccable` ran first and
`frontend-design:frontend-design` second. The `PRODUCT.md` gate is still unmet, for the reason given
under Task 2. The detector (`npx impeccable --json`) found nothing in the three sources or in
`VideoEmbed.astro`. The video is the site's own `g9iV9RVr_Sk` (`youtube_embeds[0]`) as a
click-to-play facade; pressing play loads the youtube-nocookie player (render probe), and the
`<noscript>` player stays. The review is `data/reviews.json` by name (Mark J), word for word, with
no stars and no AggregateRating. The two served photos (the London delivery photo, Mark's photo)
are used once on the preview, with their served alts.

| Component | impeccable found | frontend-design found | Changed | Widths |
|---|---|---|---|---|
| video (CityVideoPanel, C) | At 375 the Parents fact broke inside a test name ("L-2-" / "HGA"); the frame held the two names in nowrap spans. | Tray, 16:9 screen, brass "Play the film" chip (48px, ink disc), side photo over three ruled facts, the 640–1023 photo-beside-facts step and the 1024 two-column row all match. The poster crop is the focus map's (Christa's face centred) rather than the frame's `50% 4%`: the ear tips sit a little closer to the top edge, the face is whole. The caption is VideoEmbed's `--text-sm`, not the frame's `--text-xs` (left: shared component, and the larger size reads better). The chip's name starts with its visible label (WCAG 2.5.3; probe). The "Getting home" fact is the canonical delivery line, not the frame's typed sentence. | A hyphenated code in a fact (`L-2-HGA`, `HC-HSF4`) renders in a `nowrap` span, split in the component so the fact stays one plain string. The specimen caption restores the frame's poster credit ("Poster photo: Christa, one of the six available now."). The labelled-badge CSS lives in CityVideoPanel, not VideoEmbed, so the built pages' video stylesheet is byte-identical. | 375 768 1024 1280 |
| image and text (CityChapters, C) | The brass numeral sat `--space-3` above its H3 (the chapter's grid gap); the frame kept them `--space-1` apart as one heading unit (its `.hd` wrapper, which the build drops so the photo stays the H3's next sibling). | Tray, hairline chapters, numeral discs, phone order numeral / H3 / photo / prose, the 768 photo-beside-prose step and the 1024 three-column row match. `layout-h3-image-first` examined 2 at every width. Chapter one is Byrd's own photo (the page's alt), not Maggie's served photo, which the puppy sheet already uses (one served photo per page, Code facts 4). | `.num + h3` pulls the heading up by `--space-3 − --space-1`. | 375 768 1024 1280 |
| review (CityLetter, A) | No finding on the component. | Raised card, Mark's photo at its own 319px width on top below 1024 and pinned left from 1024, the steel quote mark, the verbatim quote and the signed foot match. The frame's card and section end about 16px lower: the frame has no preflight, so its `p.sig` kept the UA's 1em bottom margin; the built card's padding is even on all sides. | Nothing. | 375 768 1024 1280 |

The twelve built pages: `VideoEmbed`'s `poster` / `posterSizes` / `playLabel` and `BodyImage`'s `class`
are opt-in and no built page passes one. After the build, every built page's HTML matches the
Task 4 build except one reordered, byte-identical VideoEmbed style block on the three pages that
carry a video (the home, about and for-sale pages; no rule in the blocks it moves past can reach
a video element). `npm run test:render:pages` against a build of `f010977`: every built page's
scorecard is identical (the same three `uk-locations/blue-staffy-puppies-uk` rows, Known Issue 81).

**Task 6: FAQ blocks A, newsletter A, contact form B (2026-09-28).** Built on `/kit-preview/city/` and
shot at 375 / 768 / 1024 / 1280 (`CITY_SHOTS=… npm run test:render:city`, plus one element shot per
component, `built-<component>-<width>.png`, the states `built-faq-blocks-a-<width>-open.png` (the
first question of each block open) and `built-{newsletter-a,contact-form-b}-<width>-error.png` (an
empty submit, with the contact form's phone field focused), and canvas-beside-built pairs,
`pair-<component>-<width>[-open|-error].png`, all in `BSUK-refs/london/_plan2-shots/`, against
`_variants/faq-blocks-a-*`, `newsletter-a-*` and `contact-form-b-*`). The element shots were taken
at a 3200px-tall viewport with the preview's own site header removed: at 900px the preview's
sticky header (259px tall at 375) cut the foot off an element shot. `impeccable:impeccable` ran
first and `frontend-design:frontend-design` second. The `PRODUCT.md` gate is still unmet, for the
reason given under Task 2. The detector (`npx impeccable --json`) found nothing in the three sources
or in `ContactFormKit.astro`.

The specimen FAQ is 18 questions in three blocks of six (the user's ruling: three blocks, 15 to 20),
numbered 01 to 18 through `start`, the rail on the top block only. Every answer is a fact the data
files or the breeder's confirmed answers back: the prices and the six by name (read from the data),
the deposit ruling (`depositLine`, no refund clause), the delivery band and collection in Carlisle,
Maggie and Jones, the two DNA tests, eye and elbow screening with no score, the vet, the take-back
terms, what a puppy has had, Puppy Culture and ENS, and the breed facts `data/faq.json` already
carries. The canvas's KC-registration, two-year guarantee and 24-to-48-hour lines are not carried;
there is no guarantee row while `guarantee_days` is null and no licence detail. No heading on the
preview repeats an FAQ question (new test). Measured in the painting browser: an empty submit marks
the newsletter's email and the contact form's four required controls `aria-invalid="true"`, each
described by its painted error line; the rings on both steel bands read `--color-focus-on-inverse`
(brass-500) through `.on-inverse`; no width scrolls sideways.

| Component | impeccable found | frontend-design found | Changed | Widths |
|---|---|---|---|---|
| FAQ blocks (CityFaqLedger, A) | A block without the rail ran its rows across the full band (1,150px at 1280), so a question and its plus sat a long glance apart; the canvas ledger was a 780px column beside the rail. | Deep band, sticky photo rail over the brief, brass-200 numbers, plus-to-minus, the open answer indented under its question, the 21:9 strip at 768 and the 16:9 strip on a phone match the frame. The rail photo is the London owner photo (Maggie's is the puppy sheet's; one served photo per page), served alt kept. At 768 the 400px master paints at 704px in the 21:9 strip (`img-not-upscaled` advisory, 1.76x): a photo choice for the page's board, not a component fix. The blocks sit as three sections, so the space between them is two section paddings, as on a city page, where they are apart. | A block without the rail keeps a 780px measure. | 375 768 1024 1280 |
| newsletter (CityNewsletter, A) | No finding on the component. | Raised card on bone, Christa on the left from 768 and on top on a phone, ruled eyebrow, brass full-width submit on the form radius, warn-colour error line under the field: all match. The plan's alt ("looking up … from a fleece rug") did not match the photo, and the `scene` alt was already on the page, so the specimen's alt is its own, checked against the photo. | Specimen alt only. | 375 768 1024 1280 |
| contact form (CityContactLineup + ContactFormKit `layout="grid"`, B) | The privacy link in the note painted without its underline (the site preflight), told apart by colour alone on the band (WCAG 1.4.1). The plan's `.req { opacity: 0.85 }` would trip `page_hardening_scan` `opacity-dims-text-contrast` (the bsuk-contact-form skill, trap 2). | Line-up three by two then six across, display-face names, the form three to a row from 1024, brass submit beside its note: match. In the error state a field that shares a row with a painted error line (phone, town) dropped and stretched, because `.field` stretched its rows; the frame sets `align-content: start`. The Button `submit` kind is `w-full` (Tailwind utilities layer), which a rule inside `@layer components` cannot override, so the width rule sits outside the layer. The note is the kit's ("We reply by email…"), not the frame's 24-to-48-hour line. | `.field { align-content: start }` and an underlined `.note a` in the grid layout; `.req` takes steel-100 instead of opacity; the submit's `width: auto` rule is unlayered. | 375 768 1024 1280 |

The twelve built pages: `ContactFormKit` keeps its stepped form for every page that does not pass
`layout="grid"` (new test `test_the_grid_layout_of_the_kit_form_is_opt_in`). Wrapping the stepped
form in the `{grid ? … : …}` expression makes Astro drop whitespace-only text between its tags, and
it dropped the one visible space, "Your name (required)", which is now an explicit `{' '}`. Against a
build of `79196ea`, the contact form on the four pages that carry it
(`uk-blue-staffy-breeders-contact`, `blue-staffy-pup-sale-uk`, `buy-blue-staffy-puppies-uk`,
`buy-staffy-puppies-for-sale-uk`) has identical `innerText`, box and pixels at 375, 768 and 1280
(one 1px scroll offset at 1280 on the buy page is the harness's own: it recurs comparing that build
with itself). Every other built page's HTML is unchanged apart from the shared stylesheet, which
gains the grid rules (matching nothing on a stepped form) and a `--color-warn` declaration Tailwind
now emits because the newsletter reads it. `npm run test:render:pages` on this build and on a build
of `79196ea`: 57 passed, 3 failed both times (`uk-locations/blue-staffy-puppies-uk`'s
`nav-jump-target-lands`, Known Issue 81), and every scorecard's defects are identical. The one
moved number is advisory: `css-no-dead-component-rule` counts 6 more unmatched rules per width on
the four pages with a contact form (the grid rules), and 67 more on `/kit-preview/` (the three new
components' CSS, bundled through the registry).

**Task 7b: review fixes, the column layouts and the city type scale (2026-09-28).** Judged on
`/kit-preview/city-page/`, the city kit inside `CityShell` with the body in the column beside the
dial (656px at 1024, 832px at 1280), at 375 / 768 / 1280 in a painting browser (full-page shots,
plus in-column element shots at 1024 / 1280 composed beside their canvas frames as
`BSUK-refs/london/_plan2-shots/onpage-<component>-<w>.png`, 18 pairs). `impeccable:impeccable` ran
first and `frontend-design:frontend-design` second, with type fit as the headline lens (the user's
ruling: no big headers, even paragraphs, no chunky titles or tall sections). The `PRODUCT.md` gate
is still unmet (the loader reports no PRODUCT.md or DESIGN.md; only `/impeccable teach` with the
user may write one), so the brand context came from the `design-context-read-first` files.

Before this task every in-body component showed its phone or tablet layout on a real city page
(the canvas's 976/1024 thresholds are wider than the column can ever be), and headings were the
site's fixed 30/36px steps in a 656–832px box: the two-chapters questions ran five lines deep.
Heading sizes, before → after (min–max on the page):

| Width | h1 (hero) | h2 | h3 / card titles | paragraphs max |
|---|---|---|---|---|
| 375 | 36 → 25.4 | 30–36 → 21.9–22 | 20–24 → 17 | 20 → 17 |
| 768 | 36 → 30 | 30–36 → 24.8–25 | 20–24 → 18 | 20 → 18 |
| 1024 (column 656) | 30 → 33.7 (full-width hero) | 30–36 → 23–28 | 20–24 → 18 | 20 → 18 |
| 1280 (column 832) | 36 → 34 | 30–36 → 27.8–28 | 20–24 → 19.8–20 | 20 → 18 |

| Component | impeccable found | frontend-design found | Changed | Widths |
|---|---|---|---|---|
| all fifteen | Headings sized for a full page in a 656px column; the chapters' questions five lines deep, the FAQ questions 20px on a phone. | One scale in one place, tiered by the section's own box, reads as one system from the hero to the form; the section rhythm (32/40/48px) no longer leaves loose bands. | The city type scale in `kit.css`; no component sets its own heading, lead or body size; tall 56–64px paddings replaced by `--city-pad-y`. | 375 768 1024 1280 |
| contact form (CityContactLineup + ContactFormKit grid) | The message field stopped at 549px of a 768px form at 1280: the new 65ch paragraph measure caught its `p.field` row. | The form reads as three to a row with the message across all three, as on the canvas. | The measure and body size apply to reading paragraphs only (`p:not(form *)`); the layout probe gains a `fill` fact so a full-width row that shrinks fails. | 1024 1280 |
| two chapters (CityChapters) | In the column the 5/7/9 split left the heading 150px wide. | Heading, photo and prose sit as three even columns in the column. | 6/7/8 in a 776–975px box; 5/7/9 (the canvas's proportions) full width. | 1280 |
| puppy sheet (CityPuppySheet) | Full width at 1280 the six 360px prints make the section 1,603px, over 1.6 viewports. | The prints are the product; at 360px they are the size a buyer judges a puppy by, and no city page lays the sheet full width. | Named exemption in `cityTypeFit.ts`, for a box of 1000px or more only; the column copy (1,309 → under 1,280px after the rhythm pass) is held to the rule. | 1280 |

Everything else was judged and left: the hero's filmstrip and plates, the price scale's line, the
trust ledger's two columns, the letter's quote (exempt from the paragraph length by name: a review
is data word for word), and the FAQ ledger's numbers and plus signs.

**Task 7b spec review (2026-09-28).** Four gaps closed after the review:
- The letter's review is no longer exempt from the type-fit line caps. CityLetter splits it at
  its sentence breaks at render (words and order exactly the data's; `data/reviews.json`
  untouched), so its paragraphs run 5/4/3 lines at 375, 3/3/2 at 768 and 1024, and 4/3/2 in the
  1280 column. Before, it was one paragraph of 12 lines at 375 and 9 in the column.
- The roster's stack and the roster's and puppy sheet's gutters read their own box
  (`@container` at 640 / 800), never the viewport. In the 656px column at 1024 they now take
  the tablet gutters instead of the desktop ones.
- The specimens' litter size ("six") is read from `availablePuppies()` in every string.
- `city-nav-current-section` waits for the spy to settle instead of reading after a fixed
  300ms; five consecutive city runs passed.

**Plan 2 Task 8: the London scaffold (2026-09-28).** Judged on the built scaffold,
`/uk-locations/blue-staffy-puppies-london/` (the fifteen picks on `CityShell`, placeholder copy,
noindex), full-page shots at 375 / 768 / 1024 / 1280 from
`CITY_SHOTS=/Users/apple/Downloads/BSUK/BSUK-refs/london/_plan2-shots npm run test:render:city`,
read in slices. `impeccable:impeccable` ran first and `frontend-design:frontend-design` second,
type fit the headline lens. The `PRODUCT.md` gate is still unmet (the loader reports
`hasProduct: false`), so the brand context came from the design-context files as before.

| Where | impeccable found | frontend-design found | Changed | Widths |
|---|---|---|---|---|
| the shots themselves | Every lazy photograph below the first screen was an empty box in the full-page shot (trust, takeaways, sheet, roster, FAQ rail, chapters, letter, line-up), so a design pass could not judge them. | The same: the shots showed the frames, not the page. | The city spec, under `CITY_SHOTS` only, walks the page and waits (capped at 3s per image) for each photo to decode before the shot. No check's input changes. | 375 768 1024 1280 |
| price scale (CityPriceScale) | At 768 the delivery range broke at its en dash, "£200–" over "£350": one figure read as two. | A figure is one unit; the tablet line should read left to right as four stops. | `.range .n` never wraps; from 640 to 1023px the range stop takes its figure's width (`min-content`) and the deposit and the fork share the rest (107 / 150px at 768, was 89px for the deposit when the range first took its label's width). 1280 is unchanged. | 768 (640–1023) |

Measured after the fix (a painting browser): no horizontal overflow at 375, 768 or 1280; the
range figure 173×33px at 768 and 250×33px at 1280, one line.

Judged and left, with the reason:
- **The sticky chrome on a phone** is the site header (121px at 375, two rows) plus the jump band
  (100px, the stepper rail and the key): 221px, 27% of an 812px screen; at 768 it is 113 + 122px
  (23%). The header is PageShell's (the twelve built pages' contract) and the band is the user's
  pick (jump-links A, rail and key both), so neither is changed here. Flagged for the user's
  side-by-side (Task 10): a phone band of the key alone would be about 52px.
- **Money ranges inside running text** ("UK home delivery £200–" / "£350 …" in the video's
  facts at 1280, the roster's foot) break at the en dash like any word. The strings are
  `cityKit.deliveryLine`, which the built pages' cards and the tests read word for word; a
  joiner character would change the text itself, so the break is left to the page run's copy.
- **Test names at a line end** ("L-" / "2-HGA" in the takeaways at 1280) are placeholder copy;
  London's outline rewrites it.
- The rhythm of the fifteen together (bone, steel tray and deep-steel band alternating; three
  FAQ bands at the top, middle and foot of the body, the contact band last) reads as one page;
  headings stay two to three lines at every width and no paragraph runs past the type-fit caps
  (`city-type-fit` examined 121 / 106 / 106 / 121 nodes at 375 / 768 / 1024 / 1280 with no
  defect, and 121 / 106 at the 660 / 1160 edges).

**Plan 2 Task 8 quality review (2026-09-29).** The design-pass fix to the price scale had moved
the problem instead of removing it. With the range kept on one line and the count beside the
number line, the fork's figures painted past the panel from 640px to about 665px ("£1,500 a boy"
53px past the content edge at 640), and ran past the line's end up to about 700px. 640 and 667
were not among the widths the spec painted. The harness was fixed first: the edge runs now
include 640 and 667, and `priceScaleSpill` measures each figure's painted glyphs against the
panel's content edge and the number line's end. It failed at 640 on all three city routes.

- **Price scale:** below 840px the count sits above the line, as it does on a phone, so the four
  stops get the panel's full width. The count keeps its own width, which the first attempt did
  not: it measured 78ch at 768, and `city-type-fit` caught it. A 640–1100px sweep in 10px steps
  (three routes) found the worst figure 16px inside its limit, at 1030px. Before and after pairs
  are `BSUK-refs/london/_plan2-shots/scale-pair-{640,667,768,1024,1280}.png`. "Before" is the
  86632ce build's `/kit-preview/city-page/`, because London had no scaffold then.
- **Roster at a 640px box:** the new 640 run also caught this. The site's `.stack-table` stacks at
  `max-width: 640px`, and that query includes 640, while the roster's own tier is a table from a
  640px box. At exactly 640 the rows were blocks without the slip layout. The roster now restores
  table display from a 640px box.

## Plan 2 Task 10b (2026-09-29): the answer-board rulings

`impeccable:impeccable`, then `frontend-design:frontend-design`, on
`/uk-locations/blue-staffy-puppies-london/` (dist/) at 375, 768 and 1280, focused on what the
rulings changed. Shots: `BSUK-refs/london/_plan2-shots/10b/` (outside git). impeccable's
PRODUCT.md gate had nothing to load (no PRODUCT.md in the repo); the brand context read was
CLAUDE.md's Brand context and `rules/design.md`, as in the earlier passes.

- **Jump band (q03).** At 375 and 768 a scroll down leaves only the site header; a scroll back
  up brings the steel band back flush under it, with the current stop swollen. The slide is
  `transform` only and goes behind the header (z 50 over 30), so no strip of the band shows
  mid-slide. No change.
- **Contents list (q05).** Shown at 375 and 768, gone at 1024 and 1280, where the dial is the
  page's contents. The hero and the price scale now lead straight into the body at desktop,
  with no duplicate list. No change.
- **Takeaways (q06, q07).** At 1280 the question sits on two lines in the 7fr head column and the
  lede on four in the 5fr; the head no longer lines up with the photo/list split below, which
  reads as a deliberate masthead rather than a misalignment. **Fixed:** the lede and the nav
  label still said "five" answers after the guarantee made six rows. The scaffold now builds the
  rows once and says the count from them ("Six plain answers", "The page in six answers"); the
  specimen's lede counts the same way.
- **Trust strip (q07).** Six claims now fill the two-column ledger as three even rows at 768 and
  1280 (five left a hole bottom right); the shield icon matches the line set. No change.
- **FAQ rail (q07).** The guarantee is the third brief under the photo. At 1280 its title takes
  two lines in the 4fr rail where the other two take one; it is the rail's own measure and the
  words are the data's, so it stays.

## Plan 2 — close

`impeccable:impeccable` (its `audit` command), then `frontend-design:frontend-design`, on the final
build: the fifteen built components on `/kit-preview/city/` and the London scaffold
`/uk-locations/blue-staffy-puppies-london/`, at 375, 768 and 1280 (and 1024) in a painting browser,
from the shots of `CITY_SHOTS=/Users/apple/Downloads/BSUK/BSUK-refs/london/_plan2-shots/close/city
npm run test:render:city` (outside git). impeccable's PRODUCT.md gate is unmet as before (its
loader reports no PRODUCT.md and no DESIGN.md; only `/impeccable teach` with the user may write
one), so the pass is read-only: its mutation gate stays closed and the brand context came from
the `design-context-read-first` files. No finding changed a component, so Step 1 was not re-run.

| # | Pass | Finding | Where, widths | Changed |
|---|---|---|---|---|
| 1 | impeccable (detector) | `border-accent-on-rounded` at `CityTakeawaysLedger.astro:59` `border-top: 4px solid` | source | Nothing: the section has no radius; the same false positive as Task 7. |
| 2 | impeccable (audit, responsive) | `img-not-upscaled` advisories: the owner photo `blue-staffy-testimonial-london-happy-owner.webp` (400×437) painted 704×302 in the FAQ rail at 768 (1.76×) and 592×254 at 1024 (1.48×); Christa (400×400) at 1.17× in the video side panel at 1280; Jones (663×660) at 1.11× in the takeaways crop at 768 | both routes | Nothing here: a larger master goes beside the served file (working rule 11) in London's page run, at its image step (page-run row 11). |
| 3 | impeccable (audit, a11y) | `img-face-visible` advisory: the owner photo's two faces are 89–90% painted in the FAQ rail's wide crop at 768 and 1024 | both routes | Nothing: advisory, and the crop box is the London board's to choose. |
| 4 | impeccable (audit, a11y) | contrast 0 AA failures (324–336 text nodes per width), tap targets clean, no horizontal overflow, headings in order, alts present; `city-type-fit` green on every width (104–123 examined) | both routes | Nothing. |
| 5 | impeccable (audit, theming) | the site `Breadcrumb` puts its `›` flush against the next crumb ("UK Locations ›London"): the `gap` sits between the `li`s, not inside them | every page, all widths (site chrome, not a city component) | Nothing: a visual change to every built page is previewed first (working rule 6); listed for the next chrome touch. |
| 6 | impeccable (anti-patterns) | no gradient text, glass, side stripes, hero-metric template or nested cards; the trust strip's icon rows are a two-column ledger, not a card grid. The scaffold's closing line "The old page's words, kept until this page is written" is placeholder copy, expected until London's page run | London scaffold | Nothing. |
| 7 | frontend-design | the fifteen components hold one direction (steel band, brass CTA, bone ground, Fraunces over Source Sans) and match the canvas frames the user confirmed ("All fifteen match", 2026-09-29, side-by-side https://claude.ai/artifact/EPtLABruWw8yjBwFj5skf6) | `/kit-preview/city/` | Nothing. |
| 8 | frontend-design | at 768 the review card sets the owner's photo at a third of the card's width above the letter, leaving the right two thirds of that band empty | both routes, 768 | Nothing: composition is the London board's call per section (the outline decides the sections, `outline-before-components`); noted for it. |

## Known Issue 97 applied (2026-09-29)

The user's pick "a and all recommendations" (preview https://claude.ai/artifact/7WfxLwvXTxxBGN9HtZuMwZ):
option (a)'s body-heading scale, the side gutter on unboxed prose, and the boxed H2 on the same
scale, all in `src/styles/board-styles.css`. `impeccable:impeccable`, then
`frontend-design:frontend-design`, were invoked with the Skill tool on the four preview pages
(`/blue-staffy-health-uk/`, `/uk-blue-staffy-puppy-buying-guide/`,
`/uk-staffordshire-bull-terrier-guide/`, `/privacy-policy-uk/`) at 375, 768 and 1280, from shots
painted in Chromium through Playwright (device scale 1) of the same regions as the preview, the
first boxed H2 and the gutter: `/Users/apple/Downloads/BSUK/BSUK-refs/london/_plan2-shots/ki97-after/`
(outside git). impeccable's PRODUCT.md gate is unmet as before (its loader reports no PRODUCT.md
and no DESIGN.md), so the pass is read-only, with the brand context from the
`design-context-read-first` files; brand register.

| # | Pass | Finding | Where, widths | Changed |
|---|---|---|---|---|
| 1 | impeccable (typography) | the hierarchy now reads: body H2 22 / 25 / 28px at 700 and H3 18 / 18 / 20px at 600 over 17px prose, a 1.29 / 1.47 / 1.65 step from body to H2; the privacy page's run of H2, H3, H3 no longer reads as one grey column | all four, all widths | Nothing further. |
| 2 | impeccable (responsive) | every text block sits 24px in from both edges at 375 and 768 (was 0px on all four); at 1280 nothing moved | all four | Nothing further. |
| 3 | impeccable (typography) | the boxed H2 is on the same size and line-height as the unboxed H2 but keeps the regular (400) weight, so a box's own heading reads lighter than a migrated section's H2 on the same page | all four, all widths | Nothing: the preview and the brief set size and line-height only; a weight change repaints all 104 boxed H2s and goes to the same preview as heading colour (Known Issue 97, next). |
| 4 | impeccable (layout) | at 1280, unboxed text starts at x = 292 and boxed text at x = 316: the box's own 24px padding against the dial column's edge | all four, 1280 | Nothing: as built before this change, and aligning them moves every unboxed section at desktop, which the gutter fix deliberately does not. Listed in Known Issue 97. |
| 5 | impeccable (typography) | `text-wrap: balance` puts the migrated " : " at the start of a line ("Blue Staffy Health UK / : Our Commitment to …", 375) | health page, boxed H2 | Nothing: the space before the colon is the migrated heading's own text (verbatim set), a content change. |
| 6 | impeccable (anti-patterns) | no side stripes, gradient text, glass or new cards; the change adds no colour and no component | all four | Nothing. |
| 7 | frontend-design | one editorial rhythm now runs through the pages: Fraunces headings at the city kit's own tiers, Source Sans prose at 17px, tokens unchanged; the long migrated H2/H3s wrap to 4 or 5 lines at 375 on the buying guide, as the preview measured | buying guide, 375 | Nothing: rewording them is content (working rule 15). |
| 8 | frontend-design | the boxed H2 no longer dominates a phone screen: the health page's first is three lines and 78px at 375 (was four lines, 198px), the breed guide's first three lines (was five, 248px) | health, breed guide, 375 | Nothing further. |
