# London side-by-side · confirm the match and seven decisions

The fifteen London components are built on the real London page. The side-by-side shows each one
beside the canvas frame you picked, at 375, 768 and 1280px:
https://claude.ai/artifact/EPtLABruWw8yjBwFj5skf6. Each card says what differs on purpose.
Question 1 is the confirmation Plan 2 waits on; the rest are decisions the build could not make
for you. Claude's recommendation is marked.

## The match

1. **Do the fifteen built components match the canvas picks?** Every difference that is on purpose is
   written on its card:
   - a different served photo where the canvas repeated Maggie's;
   - bold headings;
   - the capped type sizes you asked for on 2026-09-28;
   - the column beside the dial;
   - no guarantee line;
   - the review in three paragraphs.

   If any component differs in a way you do not want, name it and what to change. It is fixed in
   that component and the side-by-side is republished at the same link.
   **Where it goes:** Plan 2 closes (Task 11) on your yes; then the London page run starts with its
   research board.
   - (a) All fifteen match; close Plan 2
   - (b) Some differ; I name them in the text box

## Photos and layout

2. **Keep the photo swaps?** A served photo may appear once per page (its alt text stays word for
   word, and a repeated alt fails the image gate), so where the canvas used Maggie's photo five
   times the page uses:
   - Jones's portrait (trust strip);
   - Jones seated (takeaways);
   - Byrd (chapter one);
   - the London owner photo (FAQ rail).

   Maggie stays on the puppy sheet. Recommended: (a) — every photo is one the site already serves
   and ranks, so nothing new is added. Trade-off: the canvas's Maggie-first look is softer on
   those four components.
   **Where it goes:** the London page board's image slots; any file named there is accepted.
   - (a) Keep the four swaps
   - (b) Use other served photos; I name them in the text box
3. **On a phone, the site header plus the jump band cover about 27% of the screen (221 of 812px at
   375).** The header is shared with the 12 built pages; the band is your pick. Recommended: (b) —
   it frees the screen on the city pages only and leaves the 12 built pages untouched. Trade-off:
   the band's step numbers are hidden while the reader scrolls down.
   **Where it goes:** `CityJumpStepper.astro` (city pages only).
   - (a) Keep both as they are
   - (b) The jump band slides away while scrolling down and comes back on scrolling up
   - (c) The band shrinks to one slim row after the first scroll
4. **Keep the price scale's tablet layout?** From 640 to 839px the puppy count sits above the price
   line so the four prices keep their width. Placed on the line, as the canvas has it, "£1,700"
   ran up to 21px outside its panel. Recommended: (a) — it is the only layout measured to fit at
   every width from 640 to 1100px. Trade-off: at those widths it differs from the canvas.
   **Where it goes:** `CityPriceScale.astro`.
   - (a) Keep the count above the line from 640 to 839px
   - (b) Try a smaller price size in that range instead
5. **Show the contents list at desktop too?** Beside the dial, the contents list repeats the same
   sections. The site's other pages hide their contents list from 1024px; your London pick shows
   it at every width. Recommended: (a) — it is your pick as designed. Trade-off: the section names
   appear twice on a desktop screen.
   **Where it goes:** `CityContentsPhotoIndex.astro`.
   - (a) Show it at every width (as picked)
   - (b) Hide it from 1024px, as the other pages do
6. **The takeaways heading wraps to three lines on desktop.** Its heading sits in a narrow column
   beside the answers, as on the canvas. The other headings now wrap to two lines at most on
   desktop. Recommended: (b) — it matches the "no tall headers" ruling. Trade-off: the answers
   column gets narrower.
   **Where it goes:** `CityTakeawaysLedger.astro`.
   - (a) Keep it as on the canvas
   - (b) Give the heading column more width so it wraps to two lines

## Facts for the page

7. **How long is the health guarantee?** The canvas said "two-year health guarantee", but no page may
   state a length until you give one (`guarantee_days` is empty), so every guarantee line is hidden
   today. If you give it, the trust strip, takeaways and FAQ print it from the data.
   **Where it goes:** `data/settings.json` `guarantee_days`.
   - (a) Two years
   - (b) Another length; I give it in the text box
   - (c) Leave it off the site for now
8. **What is the litter's date of birth?** You said the puppies are now 10 weeks old, but the data
   has no birth date. With one, every page can work their age out and never go stale.
   **Where it goes:** `data/puppies.json` (a birth date on the litter).
