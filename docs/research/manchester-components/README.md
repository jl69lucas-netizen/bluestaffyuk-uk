# Manchester Component Design Pass — Research Folder

Row 10 of the Manchester page run (`docs/superpowers/plans/2026-10-07-manchester-page-run.md`,
Phase F). London's pass (`docs/research/london-components/`, London Plan 1
`docs/superpowers/plans/2026-09-27-london-component-design-pass.md`) is the worked example; this
file records only what Manchester does differently, plus the contract every variant follows.

- `ideas-index.md`: where each idea came from. The 42 breeder sheets in
  `/Users/apple/Downloads/BSUK/bluestaffyuk-cms/Assets/Components-Ideas/` (outside git), London's
  captures and the MFS sheets, and every component's two London pool variants.
- `hardening-log.md`: the frontend-design and impeccable record for each variant (Tasks 22–25,
  then the built components).
- **The canvas:** not published yet. Task 26 publishes
  `docs/artifacts/bsuk-manchester-component-canvas.html` (built by
  `scripts/build_component_canvas.py --city manchester` from `design/city-canvas/manchester/`) and
  writes its URL here. Picks are stored in the canvas db exactly as London's are: collection
  `picks`, one document per component id; `notes/general`; `submissions/<s-time>`.

## Scope: thirteen components, two not used

Phase F ruling 2: the approved outline decides which components exist. Manchester's 22 outline
rows need 13 of the 15 city components.

| Component | Outline rows |
|---|---|
| `hero` | §1 |
| `counter-strip` | §2 |
| `trust-strip` | §3 |
| `contents-list`, `desktop-dial`, `jump-links` | §4 (22 sections, so all three mount) |
| `key-takeaways` | §5 |
| `reviews` | §6, §11, §20 |
| `faq-blocks` | §7, §12, §21 (6 + 7 + 7 = 20 questions) |
| `image-text` | the nine body sections |
| `tables` | the G2 litter table under the H4 "Who Are the Three Boys and Three Girls in This Litter?" |
| `newsletter` | §16 |
| `contact-form` | §22 |

Not used:
- **`puppy-cards`.** G2's table carries the six puppies, and no section is added to use a
  component.
- **`video` (Recommended; asked once in Task 26).**
  - Why: `data/settings.json` `youtube_embeds` holds three ids, and each already sits on its own
    page: `g9iV9RVr_Sk` on the breed guide, `g88qOo9C94c` on `/buy-staffy-puppies-for-sale-uk/`,
    `fXhu9jDS6CA` on `/blue-staffy-uk-breeders/`. Working rule 14 keeps a video where a page
    already had one, and Manchester's 5-word stub had none. The approved outline has no video row,
    and its schema note says "no VideoObject unless a youtube_embeds id is placed at STOP 3".
  - Trade-off: the page gets no video-search surface.
  - If the user picks (b), `g88qOo9C94c` goes under G2's H2 as a click-to-play facade: three
    `video` variants on the canvas (facade first), a `VideoObject`, and `bsuk-video-seo-agent` at
    row 12.

## Hero and counter: three new designs each

Phase F ruling 3, working rule 16. Neither offers a pool variant.
- The three heroes take their ideas from `hero-idea-3.png`, `hero-idea-5.png`, `hero-idea66.png`,
  `hero-idea77.png` and `comparison-hero-idea1.png` (London's used `hero-idea-1.png`,
  `hero-idea.png` and `hero-idea00.png`).
- Each counter variant cites at least one breeder sheet that shows figures. Five do:
  `hero-idea-3.png`, `hero-idea.png`, `hero-idea77.png`, `component-idea-modern.png`,
  `component-idea44.png` (what each shows is in `ideas-index.md`).
- `scripts/check_city_canvas.py` refuses a hero or counter variant whose `idea_sources` names no
  `Assets/Components-Ideas/` sheet.

## The pool rule (Phase F ruling 4)

`data/design/city-pool.json` holds London's 30 unpicked variants, two per component.
- For each of the other 11 components, variant `c` may be a refreshed pool variant. `a` and `b`
  are new.
- A pool variant is copied into `design/city-canvas/manchester/<component>/c.html`, rewritten
  with Manchester copy, and given one named refresh delta on a non-palette axis (layout, accent,
  motif, container or density).
- Its `meta.json` row records `"from_pool": "london/<component>/<v>"`, and its `idea_sources`
  stay those London's meta gives it (every one is cited under its component in `ideas-index.md`).
- It goes through the same validator, smoke test and both design skills as a new design.
- Pick the pool variant whose axes are furthest from London's pick and whose layout suits
  Manchester's outline. If neither suits the section (for example, a layout built around
  London's video call), `c` is new and its meta says why.
- (Recommended.) Why: pool variants have already passed frontend-design, impeccable, the canvas
  smoke test and the must-differ check, so they cost less than a fresh design. Trade-off: they were
  drawn for London's content, so the refresh delta has to be real, not a copy change.

The two pool variants per component, with their axes, open each section of `ideas-index.md`.

## London's picked axes (every new variant differs from these)

From `data/design/city-must-differ.json` `shape: "city"` rows. A Manchester variant differs on at
least two of layout, media, density and framing from London's pick for its component (ruling 1,
`city-pick-too-close`), from its siblings, and from every other row of its component in that
file.

| Component | London pick | Name | layout | media | density | framing |
|---|---|---|---|---|---|---|
| hero | `london/hero/b` | Litter filmstrip | filmstrip | bottom | compact | inset |
| counter-strip | `london/counter-strip/c` | Price scale | scale | none | regular | inset |
| trust-strip | `london/trust-strip/c` | Photo ledger | photo-ledger | left | airy | card |
| contents-list | `london/contents-list/c` | Photo index | photo-index | left | airy | inset |
| desktop-dial | `london/desktop-dial/c` | Photo marker | photo-track | top | airy | inset |
| jump-links | `london/jump-links/a` | Stepper band | stepper | none | compact | band |
| key-takeaways | `london/key-takeaways/a` | Answer ledger | ledger | left | regular | rule |
| tables | `london/tables/a` | Litter roster | roster | inline | compact | inset |
| image-text | `london/image-text/c` | Two chapters | chapters | inline | compact | inset |
| reviews | `london/reviews/a` | Owner's letter | letter | left | airy | card |
| faq-blocks | `london/faq-blocks/a` | Steel ledger | photo-rail | left | regular | band |
| newsletter | `london/newsletter/a` | Litter notice | split | left | regular | card |
| contact-form | `london/contact-form/b` | Litter line-up | lineup | grid | compact | band |

(London's `puppy-cards/b` and `video/c` picks are not listed: Manchester mounts neither.)

## The variant contract

London Plan 1 "The variant contract", unchanged except that the copy names Manchester and states
only Phase F ruling 10's facts.

Every variant is `design/city-canvas/manchester/<component>/<a|b|c>.html`: zero or more
`<style>` blocks, then exactly one `<section data-component="<component>" data-variant="<a|b|c>">`.
The builder wraps it in a frame holding the Google Fonts link, `src/styles/tokens.css` as a
`:root` block and a small base. One `meta.json` per component describes all three.

**What `python3 scripts/check_city_canvas.py --city manchester` refuses:**
- *Structure:* anything but one root section naming its own component and variant; `<script>`,
  `<link>`, `<iframe>`, `<object>`, `<embed>`, `<video>`, `<audio>`.
- *Colour:* hex, `rgb()`/`hsl()`/…, or `black`/`white`/`grey`/`gray`/`silver` in CSS, and any SVG
  paint attribute other than `currentColor`/`none`. Every colour is a `var(--…)` token.
- *Headings:* every h1–h6 ends in `?`, and the next start tag after it (skipping `<div>` wrappers
  and an image) is a `<p>` of at least 12 words.
- *Tables:* a `<td>` without a non-empty `data-label`.
- *Hero:* an `<img>`/`<picture>` that does not come before the first `<h1>`/`<h2>`.
- *Assets:* any `src`/`srcset`/`poster`/`url()` that is not `/images/<file>` (from
  `public/images/`) or `/puppies/<file>` (from `src/assets/puppies/`) and existing; an `<a href>`
  that is not `#…` or `/…`; a `<form action>` that is not absent or `#…`; an `<img>` without alt
  text or without numeric `width` and `height`; a served `/images/` file whose alt is not the alt
  it was served with, word for word (working rule 11).
- *Copy:* no mention of "Manchester"; a `£` figure that is not £1,500, £1,700, £500, £200 or
  £350 (read from `data/`); a parent named other than as `data/faq.json` names them (Maggie, our
  dam, and Jones, our sire); an unconfirmed claim the validator's `UNCONFIRMED_CLAIMS` lists;
  anything shaped like a phone number (write `PHONE_PLACEHOLDER`); a source-project marker or a
  reference-site host name.
- *Reviews:* a `<blockquote>` that is neither `data-placeholder="review"` nor
  `data-review="<n>"` quoting `data/reviews.json[n]` word for word.
- *Hooks and forms:* the hook counts London Plan 1's component table gives (3–6 `data-figure`,
  3–8 `data-trust-item`, exactly 3 `data-faq-block` with 15–20 `data-faq-q`, …); a form field with
  no `<label for>` or `aria-label`.
- *meta.json:* `component`, and for each of `a`, `b`, `c`: `name` (1–60 characters),
  `description` (one line, 1–160), `idea_sources` (each string cited verbatim under that
  component's section of **this** folder's `ideas-index.md`), `differs_from` (20+ characters),
  `axes` with exactly `layout`, `media`, `density` and `framing`, and `from_pool` on a pool copy.
  A hero or counter variant cites at least one `Assets/Components-Ideas/` sheet. Siblings differ
  on at least two axes, and each variant differs on at least two axes from every row of its
  component in `data/design/city-must-differ.json` (Manchester's own rows skipped), London's
  picks above included.

**What the smoke (`npm run test:render:canvas` with
`CANVAS_FRAMES_INDEX=docs/artifacts/canvas/manchester-frames/index.json`) refuses:** at 375, 768
and 1280, a frame that fails `layout-no-horizontal-overflow`, `layout-min-font-size`,
`layout-tap-target-size`, `layout-table-stacks-on-mobile`, `a11y-text-contrast-aa`,
`a11y-no-duplicate-ids` or `img-alt-present-and-unique`, or its component's probe (a hero band
outside 390–450px at 1024px and up, a hero photo painted under the heading at 900px or less, a
dial shown on a phone, a jump strip that does not stick).

**What no machine checks, and the reviews do:**
- *Tokens only.* Colour, fonts (`--font-display` for headings, `--font-body` for everything
  else), the type scale, spacing, radius, `--shadow-card`/`--shadow-lift` and the motion tokens.
  Brass (`--color-cta`) is a fill with `--color-cta-ink` text, never small text on a light
  surface. CTA buttons are pills (`--btn-radius`); form submits use `--btn-form-radius`.
- *Headings.* A buyer question in Title Case (`rules/headings.md`), followed by a
  conversational opening paragraph that answers it. Only the hero has an `<h1>`. No "Manchester"
  is added to an anchor or an FAQ heading (STOP 1 q12).
- *Manchester placeholder copy, ruling 10's facts only.* A variant may state:
  - the six puppies' names, sexes, colours, prices and statuses as `data/puppies.json` holds them
    (Roman, Byrd and Ince at £1,500; Vennie, Christa and Cheryl at £1,700; all Available today);
    colour and price are said of this litter only (q09);
  - the £500 deposit with its clause, `deposit_refund_clause` ("up to 70% refundable if you
    change your mind up to 1 day before collection or delivery"), never plainly "refundable";
  - UK home delivery for £200–£350 by DEFRA-approved transport, priced by distance, or collection
    in Carlisle;
  - the guarantee as `guarantee_label` and, where a guarantee sentence carries it,
    `guarantee_cover`, read from `data/settings.json`.
  - the parents' registration and the paperwork exactly as the evidence ledger words them:
    both parents are Kennel Club registered, and each puppy goes home with its KC registration
    application form (`parents-kc-registered-application-form`, confirmed 2026-10-04), never
    "a KC registered puppy";
  - the parents' DNA tests named (L-2-HGA, HC-HSF4) with the certificates shared on request
    (`tests-named-no-result`, `certificates-on-request`, confirmed 2026-10-05), never a result
    and never "clear".

  It never states a video call (q08), rescue wording (q10), a licence or statute claim, a phone
  number, a distance or travel time, a review score or an invented review. (Controller's ruling,
  2026-10-07: the two ledger-backed lines above replace London's looser "KC registered and
  DNA-tested parents".)
- *Images.* Reuse served images first, keeping each served alt word for word on its first use:
  - Manchester's own: `reputable-blue-staffy-breeder-manchester-pup.webp`,
    `victoria-family-blue-staffy-manchester.webp`, `victoria-family-blue-staffy-manchester-440.webp`
    (`public/images/`);
  - the parents: `maggie-blue-staffy-dam-with-pups.webp` (and its `-400`, `-760`),
    `jones-magnificent-blue-staffy-sire.webp` (and `-760`),
    `jones-strong-staffy-sire-temperament.webp` (and `-400`) (`public/images/`);
  - the puppies in `src/assets/puppies/`: `Roman1.jpg`, `Roman2.jpg`, `Byrd1.jpg`, `Ince1.jpg`,
    `Vennie.jpeg`, `Christa.jpeg`, `Cheryl1.jpeg`.
  No photo named for another city (G8). Every image box is reserved (`width`/`height` plus an
  `aspect-ratio`). Letterbox, `contain` and bleed backgrounds use bone (`--color-surface`,
  `--counter-bed`) or steel tokens, never grey or black (ruling 7).
- *Tables (ruling 5).* Caption "This litter: each puppy, sex, coat and price"; every `<td>`
  carries a `data-label`; the table stacks into labelled rows below 640px (`.stack-table`); at
  least one of the three variants carries each pup's own photo in its row (Known Issue 100).
- *Type fits every tier (ruling 6).* No big or chunky headings, no tall sections or paragraphs;
  the hero band is 390–450px at 1024px and up, photo first on phones.
- *Refresh delta (ruling 8).* The three review slots, the three FAQ blocks and the nine body
  sections each differ from their siblings on this page (photo side, accent role or density).
- *Accessible, light and fast.* Visible `:focus-visible` rings; tap targets of 44px; transitions
  of 0.2s or less and none under `prefers-reduced-motion`; CSS-first interaction; line-icon SVGs
  in `currentColor`, never emoji; no `user-select: none`.
- *Ideas, not markup.* A variant takes an idea from a capture or a sheet and is built fresh on
  BSUK's tokens. No reference-site text, image or class name.
