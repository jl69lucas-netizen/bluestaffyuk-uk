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
- **Image and text C's H3 photos use the kit's `.bl-img` class** so `layout-h3-image-first`
  counts them; build them with `BodyImage.astro`.
- **Inline `style="object-position:…"`** on image and text C moves into a class or a focus prop.

## Alt text — awaiting the user's ruling

Working rule 11 keeps a served image's filename, path AND alt text. After the Task 8 review
every served image on the canvas carries its served alt word for word (copied from `dist/`),
including wording the facts files do not confirm. The controller is asking the user whether
the unconfirmed ages and customer names may be dropped; until then, nothing is rewritten.

| Image | Canvas variants | Served alt (verbatim) | Unconfirmed wording |
|---|---|---|---|
| `ethical-staffy-puppy-london-delivery.webp` | image-text a, image-text c, video b | "An ethical blue Staffy puppy, delivered professionally by BlueStaffyUK, happily with its new owners Mark and Emma P. in London." | the owners' names "Mark and Emma P." (no review or file names them), "delivered professionally" |
| `maggie-blue-staffy-dam-with-pups.webp` | video a, image-text c | "A heartwarming photo of Maggie, a beautiful 2-year-old blue Staffy Dam, lovingly tending to her pups." | Maggie's age, "2-year-old" |
| `jones-strong-staffy-sire-temperament.webp` | video a | "Jones, a magnificent 3-year-old blue Staffordshire Bull Terrier Sire, displaying his calm strength and good temperament." | Jones's age, "3-year-old" |
| `jones-magnificent-blue-staffy-sire.webp` | reviews c | "A striking portrait of Jones, our magnificent 3-year-old blue Staffordshire Bull Terrier Sire." | Jones's age, "3-year-old" |

Also served verbatim and noted for the same ruling: `blue-staffy-testimonial-london-happy-owner.webp`
(image-text b) keeps "Happy Blue Staffy puppy owner from London sharing a testimonial" although
that section is not a review; `mark-blue-staffy-london.webp` (reviews a) keeps "Mark with their
healthy blue Staffy puppy from BlueStaffyUK.uk in London.". The validator accepted every served
alt (0 problems).

## Served alt text across every component (controller, after the Task 8 review)

Working rule 11 keeps a served image's alt text word for word. Tasks 5–7 had also rewritten the
alts of `maggie-blue-staffy-dam-with-pups.webp` (trust-strip c, jump-links c, puppy-cards b,
key-takeaways a) and `ethical-staffy-puppy-london-delivery.webp` (jump-links c, tables b). All
are now restored from `dist/`, so every `/images/` file in the canvas carries its served alt.
Puppy photos (`/puppies/…`) already carry different alts on different built pages, so a variant's
own puppy alt does not breach the rule.

## Task 9: FAQ blocks, newsletter, contact form

- **FAQ blocks are built from a question file, never from the fragment.** On the London page the
  three blocks sit at the template's three places (top, middle, bottom), not together as on the
  canvas; each block renders its rows through `Faq.astro` semantics (question `<h3>` inside the
  `<summary>`, `titleCase()` at render) and the FAQPage schema carries exactly the visible
  questions. Numbering (FAQ a) runs across the three blocks, so the kit takes a `start` index.
- **FAQ a's rail facts** (deposit, delivery, guarantee) are read from `data/settings.json` and
  `data/puppies.json`, never typed; if the three blocks are split across the page, the rail
  goes with the top block only.
- **Forms are built on `ContactFormKit.astro`**, which carries what the mockups leave out: the
  `_gotcha` honeypot, the hidden `_next` and `_subject`, `method="POST"` and the one endpoint
  (`#contact` until `PUBLIC_FORMSPREE_ID` is set). The puppy options come from
  `data/puppies.json`; `scripts/form_contract_audit.py` must pass on the built page. Contact a
  (letter) keeps every control a labelled field with its own `for`; its phrases are UI copy,
  so the dup gate's `form` exclusion still applies.
- **The newsletter posts to the same endpoint** and must stay a one-email-field form so the
  audit classes it `newsletter`. The kit has no newsletter component yet; add one.
- **Contact b's six photos** are built from `data/puppies.json` (`card_photo`), and the inline
  `style="object-position:…"` crops move into the puppy focus map noted under Task 7.
- **`:user-invalid` error states** are the CSS floor; the kit keeps native validation and may
  add `aria-describedby` from each field to its error line.
- **Served alts.** FAQ a keeps Maggie's served alt and contact c the London owner photo's
  served alt, both listed above under "Alt text — awaiting the user's ruling".

## From the Task 9 review

- No real section heading may repeat an FAQ question. On the canvas, "What Does the £500
  Deposit Do?" and "Which Health Tests Do the Parents Have?" are both the headings of the
  `data-canvas-only` stubs and FAQ questions.
- The forms' error messages (`.err`) are not tied to their fields. Build on `ContactFormKit` with
  `aria-describedby` and `aria-invalid`.
- Contact b's six-puppy strip invites a tap but selects nothing. Either make each photo
  preselect its puppy option, or style the strip as plainly non-interactive.
- Contact a's fill-in-the-sentence layout collapses to label-above-field rows below about 480px.
  Keep the sentence and field on one line as far down as it fits.
