# Plan 2 Notes (London Components)

A running list of what Plan 2 must honour when it builds the picked variants into the kit.
Added to by each Plan 1 task review; read before writing Plan 2.

## Navigation (Task 6: contents list, desktop dial, jump links)

- **The picked sheet is built on the kit's `SectionSheet.astro` pattern**, not on the canvas's
  `:target` mechanism: a `<dialog>` opened with `showModal()`, so it gets Escape to close, a
  focus trap, an inert background, `aria-expanded` on the opener, and no history entry per open
  and close. The canvas fragment is the visual spec only.
- **Current-section marking uses the kit's scroll-spy scripts** (the IntersectionObserver in
  `PageDial.astro` and `SectionStrip.astro`, with `aria-current="location"`), not `:target` and
  not scroll-driven animations. The canvas uses CSS only because a mockup frame carries no script.
- **Dial A (page map) block heights come from the real section lengths** measured on the built
  page (or from the section word counts at build time), never from the stand-in weights.
- **Fragments are the visual spec.** Build each picked component from a `sections` array (id,
  short label, long label, icon), never by pasting the fragment's repeated markup; move every
  inline `style=` value (stub heights, the dial's `--i` stop angles, nowrap spans) into classes
  or computed props.
- **Anything marked `data-canvas-only` is never ported**: the stand-in sections (`.stub`,
  `.stubs`), the "which one navigates at this width" notes, and the fixed zero-size close anchor.

## From the Task 6 re-review

- The `!important` animation longhands in the nav fragments exist only to defeat the canvas frame's
  reduced-motion reset (`scripts/build_component_canvas.py`). Never port them: the kit marks the
  current section with its scroll-spy script.
- Contents a and c duplicate rows 6–10 (a desktop copy and a phone `<details>` copy). Build one
  list and hide rows 6–10 on phones behind the disclosure instead.

## Task 7: key takeaways, puppy cards, tables

- **Puppy cards are built from `data/puppies.json`**, never from the fragment's six repeated
  blocks: name, sex (`male`/`female` shown as Boy/Girl), colour, `price_gbp`, `status` and
  `card_photo`. The per-card `style="object-position:…"` crops move into a small map keyed by
  slug (or a `focus` field added to the data), not inline styles. Photos go through
  `astro:assets` as `PuppyCard.astro` already does (srcset, lazy), with the reserved box kept.
- **The Ask target.** The canvas links every Ask to `#contact`. In the kit the picked card
  links wherever the site's puppy CTA goes (the kit card links `/available-puppies/<slug>/`);
  keep the label "Ask About <name>" and keep one tap target per card (Contact sheet B and
  Litter wall C stretch the link over the card; a second link to the same place inside the
  card is `tabindex="-1"`, as the kit card does).
- **The delivery line.** `rules/puppies.md` `delivery-band-on-every-card` (test-enforced by
  `tests/py/test_puppy_card_delivery.py`) wants the canonical line
  `UK home delivery £200–£350 by distance · or collect in Carlisle` on every card. After the
  Task 7 review all three variants carry it on every card as `<p class="deliv">` (the band
  held on one line). The kit reads the band and the town from `data/settings.json`, as
  `PuppyCard.astro` does; point the test at the picked card's markup.
- **Photos per variant.** Litter wall C shows Roman's gallery photo (`Roman1.jpg`, face
  higher in the frame, so the corner plate never covers it); the others show his
  `card_photo` (`Roman2.jpg`). If C is picked, add a per-variant photo choice (or a focus
  field) rather than changing `card_photo`.
- **Family sheet B's section photo** is the site's served `maggie-blue-staffy-dam-with-pups.webp`
  (working rule 11: reuse, keep filename and alt).
- **Tables are built on `DataTable.astro` semantics** (caption, `th scope="col"`, row `th`,
  `data-label` from the column list). The canvas tables carry their own stacking CSS because
  the frame has no `global.css`; the kit keeps `.stack-table` and the picked style becomes a
  board-style class. A stacked row must stay `display:block` (the stacking check reads it);
  lay values two-up inside it with inline blocks, never by making the row a grid.
- **Figures come from data.** "£1,500 a boy / £1,700 a girl", the £500 deposit and the
  £200–£350 band are rendered from `data/puppies.json`, `data/price-matrix.json` and
  `data/settings.json`, never typed.

## Task 8: video, image and text, reviews

- **Video is built on `VideoEmbed.astro`** (`play="facade"`, id `g9iV9RVr_Sk`, title and caption
  from the board record), not from the fragment's `<button>`: the kit injects the
  youtube-nocookie player on click and carries the `<noscript>` iframe. The canvas poster is a
  served photo only because a mockup may not load YouTube's thumbnail; if the picked variant
  keeps a served poster, add a `poster` prop to `VideoEmbed` (reserved box kept), never a
  second video id. Only the ids in `data/settings.json` `youtube_embeds` may appear.
- **Reviews are built on `Testimonial.astro` from `data/reviews.json`** by name (as
  `buy-blue-staffy-puppies-uk` selects Rachel L.), never by pasting the quote; one review per
  slot; no AggregateRating or stars. Reviews A pairs Mark J with `mark-blue-staffy-london.webp`
  (the homepage's own pairing, original alt); B and C use puppy and sire photos and credit them
  in a visible caption so they never read as the reviewer's dog. Keep those captions.
- **Alt text.** Image and text B keeps `blue-staffy-testimonial-london-happy-owner.webp`'s served
  alt word for word ("... sharing a testimonial"), per working rule 11, although the section is
  not a review; if B is picked, ask the breeder whether that alt may change or use a different
  photo. Video A and reviews C describe `jones-strong-staffy-sire-temperament.webp` and
  `jones-magnificent-blue-staffy-sire.webp` without the served alts' "3-year-old" (an age the
  facts file does not hold); Plan 2 decides with the breeder which wins.
- **Image and text C's H3 photos use the kit's `.bl-img` class** so `layout-h3-image-first`
  counts them; build them with `BodyImage.astro`.
- **Inline `style="object-position:…"`** on image and text C moves into a class or a focus prop.
