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
| trust-strip | a | **Route line.** The claims as stops on a transit-map line from the parents in Carlisle to a London door, line icons in the stop roundels, brass on the last stop; horizontal at 1024+, vertical below; ruled top and bottom, under its own question heading. | The "Carlisle" and "London" labels pushed their items' titles down, so the five titles sat on three baselines; the line ran past the last roundel; "HC-HSF4" broke at its hyphen. | Place labels lifted above the line; items align to start; the line ends on the last roundel's centre; test names wrapped in `nowrap`. | 375 · 768 · 1280 |
| trust-strip | b | **Seal band.** Six promises struck as brass-ringed seals with a dashed outer ring and a two-line label, across a full-width steel band; 2 / 3 / 6 across. | Titles sat on different heights because the list items stretched; checked brass-on-steel is used only for the icon rings (non-text), labels are bone on steel (AA). | Items align to start. | 375 · 768 · 1280 |
| trust-strip | c | **Photo ledger.** A raised sheet inset in the bone page: a litter photo left, a question heading and its answer, then a two-column ledger of icon, bold claim and one plain line. | A CSS comment said "white", which the validator refuses; two detail lines read as invented facts ("handled daily from birth", "in writing"); "HC-HSF4" broke at its hyphen. | Comment reworded; both lines replaced by allowed facts (ENS, speak to the vet); test names wrapped in `nowrap`. | 375 · 768 · 1280 |

Copy checks common to all nine: every heading is a Title Case buyer question with a 12+ word
answering paragraph; the deposit is always "£500 … books your viewing and reserves your puppy",
never plainly "refundable"; no licence, council or score claim; the guarantee appears only as
"a two-year genetic health guarantee" (the user's 2026-09-27 ruling); the parents are "the
parents, Angie and Lays"; no em dashes in visible copy.
