# London Component Variants — Design and Hardening Log

One row per variant: the frontend-design direction it came from, what the impeccable pass found,
what changed, and the widths it was checked at. Shots: `/Users/apple/Downloads/BSUK-refs/london/_variants/`.

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
