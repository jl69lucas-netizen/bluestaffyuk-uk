# London previews, 2026-10-04: the diffs to apply after approval

Preview only. Nothing here is applied to `src/`, `data/` or `public/` until the breeder picks.
Each section is one option, labelled as on `index.html`. The CSS is the CSS the preview
injected into a copy of `dist/` (served from `/private/tmp/claude-501/london-preview-dist`).
Here it is written as the component edit it becomes. Every colour is a token. No hex is added
under `src/`.

Contrast pairs that are new to `data/design/contrast.json` (add these before applying any
option that uses them; ratios measured here): `--color-ink-2` on `--color-bone-50` 7.06:1,
`--color-brand` on `--color-bone-50` 11.08:1, `--color-text` on `--color-bone-50` 14.75:1,
`--color-ok` (icon, nontext) on `--color-white` 6.29:1 / on `--color-bone-50` 5.93:1 /
on `--color-brand-soft` 5.20:1.

---

## CTA-1: the four existing enquiry lines become brass pills (Recommended)

No new words and no new links. The four `#enquiry` sentences already on the approved board
(sections 7, 9, 13 and 16: "Send us your enquiry and ask for the video call", "Ask about a
puppy from this litter", "Ask us for the full terms before you reserve", "Tell us about your
London home and household") already close the deposit, litter, paperwork and temperament
chapters. Only their styling changes.

`src/components/kit/CityChapters.astro`, inside `@layer components`:

```diff
-    .close { padding-top: var(--space-4); border-top: 1px solid var(--color-steel-300); }
-    .close :global(p) { margin: 0; font-weight: 600; }
+    /* THE CHAPTER'S CLOSING LINE IS ITS CALL TO ACTION (London previews 2026-10-04, CTA-1): the
+       sentence's link, always its first child (links-plan M2, sentence_start), is the brass pill
+       (rules/design.md rule 3); the rest of the sentence follows it, in ink-2 on a bone-50 card
+       ruled in brass. Words and hrefs are the board's, unchanged. */
+    .close { margin-top: var(--space-3); padding: var(--space-4); border-radius: var(--radius-md);
+      background: var(--color-bone-50); border-left: 3px solid var(--color-cta); }
+    .close :global(p) { margin: 0; font-weight: 600; color: var(--color-ink-2); line-height: 1.5; }
+    .close :global(p > a:first-child) {
+      display: inline-flex; align-items: center; min-height: 44px; padding: var(--space-2) 22px;
+      margin: 0 6px 6px 0; border-radius: var(--btn-radius); background: var(--color-cta);
+      color: var(--color-cta-ink); font-weight: 700; line-height: 1.25; text-wrap: balance;
+      text-align: center; text-decoration: none; box-shadow: var(--shadow-card);
+      transition: background-color var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out);
+    }
+    .close :global(p > a:first-child:hover) { background: var(--color-cta-hover); transform: translateY(-1px); }
+    .close :global(p > a:first-child:focus-visible) { outline: 3px solid var(--kit-ring); outline-offset: 2px; }
+    @media (prefers-reduced-motion: reduce) {
+      .close :global(p > a:first-child) { transition: none; }
+      .close :global(p > a:first-child:hover) { transform: none; }
+    }
```

Note: `city.css` underlines paragraph links (`.city-kit :where(p:not(form *)) a`). The scoped
`text-decoration: none` above wins because it is a scoped class rule inside the same layer.
Re-check this after the build, and add `.close` to the underline rule's exclusions if it does not win.

## CTA-2: one new next-step band after Rachel L.'s letter (#review-middle)

This adds a section, so it is a content change. It needs a board row, its two links on the
board (both targets are already there), and the lead-in line written by the breeder. It also
needs a new kit component, so `data/design/components.json`, `src/components/kit/_registry.ts`
and the rule-16 component gate all change.

New file `src/components/kit/CityNextStep.astro`:

```astro
---
// src/components/kit/CityNextStep.astro: the mid-page next step (London previews 2026-10-04,
// CTA-2). One steel-900 panel with a seam-gradient top rule, a lead-in line written on the board,
// and two pills: brass (#enquiry) and an outline on inverse (/available-puppies/). Both links are
// on the approved board, so this component adds no href of its own.
import '../../styles/city.css';
import type { HTMLAttributes } from 'astro/types';
type Props = HTMLAttributes<'section'> & { lead: string; primary: { label: string; href: string }; secondary: { label: string; href: string } };
const { lead, primary, secondary, class: cls, ...rest } = Astro.props;
---
<section {...rest} class:list={['city-kit', 'city-next-step', cls]}>
  <div class="in on-inverse">
    <p class="lead">{lead}</p>
    <div class="row"><a class="pill" href={primary.href}>{primary.label}</a><a class="ghost" href={secondary.href}>{secondary.label}</a></div>
  </div>
</section>
<style>
  @layer components {
    .city-next-step { background: var(--color-surface); padding: var(--space-5) 0; }
    .in { max-width: min(1100px, calc(100% - 2 * var(--space-4))); margin: 0 auto; padding: var(--space-5) var(--space-4);
      border-radius: var(--radius-lg); text-align: center; color: var(--color-text-on-inverse); border-top: 3px solid transparent;
      background: linear-gradient(var(--color-surface-deep), var(--color-surface-deep)) padding-box, var(--seam-gradient) border-box; }
    .lead { margin: 0 auto var(--space-4); max-inline-size: 40ch; font-family: var(--font-display); font-size: var(--text-lg); line-height: 1.3; color: var(--color-text-on-inverse); }
    .row { display: flex; flex-wrap: wrap; justify-content: center; gap: var(--space-3); }
    a { display: inline-flex; align-items: center; justify-content: center; min-height: 48px; padding: 10px 22px; border-radius: var(--btn-radius);
      font-weight: 700; line-height: 1.25; text-wrap: balance; text-decoration: none;
      transition: background-color var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out); }
    .pill { background: var(--color-cta); color: var(--color-cta-ink); }
    .pill:hover { background: var(--color-cta-hover); transform: translateY(-1px); }
    .ghost { color: var(--color-text-on-inverse); box-shadow: inset 0 0 0 2px var(--color-link-on-inverse); }
    .ghost:hover { background: var(--color-surface-inverse); transform: translateY(-1px); }
    a:focus-visible { outline: 3px solid var(--color-focus-on-inverse); outline-offset: 2px; }
    @media (prefers-reduced-motion: reduce) { a { transition: none; } a:hover { transform: none; } }
    @container (width < 520px) { .row a { flex: 1 1 100%; } }
    @container (width >= 640px) { .in { max-width: min(1100px, calc(100% - 2 * var(--space-6))); padding: var(--space-6) var(--space-5); } }
  }
</style>
```

(The `.ghost` ring is an inset box-shadow used as a 2px border, not a shadow. If
`tests/py/test_design_tokens.py` reads it as a hand-written shadow, write it as
`border: 2px solid var(--color-link-on-inverse)` with the padding 2px smaller.)

`src/pages/uk-locations/blue-staffy-puppies-london.astro`, straight after the `#review-middle` `CityLetter`:

```diff
+  <SectionDivider />
+  <CityNextStep id="next-step" data-section-label="[board label]"
+    lead="[Lisa's one-line lead-in, worded and approved on the board]"
+    primary={{ label: 'Send us your enquiry and ask for the video call', href: '#enquiry' }}
+    secondary={{ label: 'Blue Staffy puppies available now', href: '/available-puppies/' }} />
```

The two labels reuse anchors that are already on the board (section 7 and the hero). If the
dup/anchor gates refuse a repeated anchor, the board gives this band its own anchors.

---

## The puppy cards: shared to CARD-1, CARD-2 and CARD-3

**Mount.** The strip leaves `CityTakeawaysLedger`'s default slot and becomes its own band
straight after `#key-takeaways`. Measured: mounted in place, every style pushes the takeaways
section over its height gate (375: 3,808–4,382px against a 2,030px cap; 1280: 1,920–2,407px
against 1,280px).

```diff
   <CityTakeawaysLedger id="key-takeaways" ... rows={takeaways}>
-    <CityTicketStrip />
   </CityTakeawaysLedger>
+  <CityTicketStrip />
```

**Data (after the breeder approves, not before).**
- `data/puppies.json`: one `personality` string per puppy. The DRAFT lines in the preview were
  supplied by the coordinator and written from the photos. They are not the breeder's words
  until she approves them on the board. The component throws if an available puppy has none.
- `data/settings.json`: `puppy_trust_signs`, the breeder's confirmed list, with a `_source`
  (brief 2026-10-04). The values: "Vet-signed health card", "First vaccinations",
  "Microchipped", "Wormed and flea treated", "KC registration application form included",
  "Parents KC registered", "Raised in our home", "Support after collection". The guarantee is
  appended from `guarantee_label` at render time and is never typed into the list.
- The delivery line is `deliveryLine` from `src/lib/cityKit.ts`, which already exists
  (`rules/puppies.md` `delivery-band-on-every-card`). The price is `money(p.price_gbp)`.
- `scripts/dup_content_audit.py`: the trust list and delivery line repeat six times by design.
  Whitelist them as stems, the way the delivery line already is for `PuppyCard`.

**Markup** (`src/components/kit/CityTicketStrip.astro`; one `<article>` per puppy, and the
name link stretched over the card so the whole card is the tap target; no heading, so the
outline is unchanged):

```astro
---
import '../../styles/city.css';
import settings from '../../../data/settings.json';
import { availablePuppies, money, sexWord, deliveryLine } from '../../lib/cityKit';
import { numberWord } from '../../lib/recordText';
const pups = availablePuppies();
const trust = [...settings.puppy_trust_signs, settings.guarantee_label];
for (const p of pups) if (!p.personality) throw new Error(`CityTicketStrip: ${p.slug} has no personality line`);
const { label = `Our ${numberWord(pups.length)} puppies · each opens its own page`, class: cls, ...rest } = Astro.props;
const CHECK = 'M5 12.5l4.5 4.5L19 7.5';
---
<section {...rest} class:list={['city-kit', 'city-ticket-strip', cls]} data-ticket-strip>
  <div class="in">
    <p class="label">{label}</p>
    <ul class="grid">
      {pups.map((p) => (
        <li><article class="pc" data-ticket={p.slug}>
          {/* CARD-2 only: <Image src={puppyImage(p.card_photo)} alt={puppyAlt(p, 'scene')} widths={[240, 400]} class={`pc-img ${focusClass(p.card_photo)}`} loading="lazy" /> */}
          <div class="pc-top">
            <p class="pc-name"><a href={`/available-puppies/${p.slug}/`}>{p.name}</a></p>
            <p class="pc-meta">{sexWord(p)} · {p.colour}</p>
            {/* CARD-3: the price sits here as the brass chip */}
          </div>
          <p class="pc-say">{p.personality}</p>
          <ul class="pc-trust" aria-label={`Comes home with ${p.name}`}>
            {trust.map((t) => <li><svg class="ic" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d={CHECK} /></svg><span>{t}</span></li>)}
          </ul>
          <div class="pc-stub">
            {/* CARD-1 and CARD-2: <p class="pc-price">{money(p.price_gbp)}</p> */}
            <p class="pc-del">{deliveryLine}</p>
            <span class="pc-go" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6" /></svg></span>
          </div>
        </article></li>
      ))}
    </ul>
  </div>
</section>
```

**Shared CSS** (all three styles; inside `@layer components`, scoped). Hover is a 3px lift
plus the opacity of a `--shadow-lift` layer, so only transform and opacity move. Reduced motion
turns both off.

```css
.city-ticket-strip { background: var(--color-surface); }
.in { max-width: min(1100px, calc(100% - 2 * var(--space-4))); margin: var(--city-pad-y) auto; }
.label { margin: 0 0 var(--space-3); font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--color-ink-3); max-inline-size: 60ch; }
.grid { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; grid-template-columns: minmax(0, 1fr); }
.grid > li { margin: 0; min-width: 0; max-width: none; }
.pc { position: relative; height: 100%; display: flex; flex-direction: column; isolation: isolate; transition: transform var(--dur-base) var(--ease-out); }
.pc::after { content: ""; position: absolute; inset: 0; border-radius: inherit; box-shadow: var(--shadow-lift); opacity: 0; z-index: -1; pointer-events: none; transition: opacity var(--dur-base) var(--ease-out); }
.pc:hover { transform: translateY(-3px); }
.pc:hover::after { opacity: 1; }
.pc:focus-within { outline: 3px solid var(--kit-ring); outline-offset: 3px; }
.pc-name a { color: inherit; text-decoration: none; outline: none; }
.pc-name a::before { content: ""; position: absolute; inset: 0; z-index: 1; border-radius: inherit; }
p { margin: 0; max-inline-size: none; }
.pc-name { font-family: var(--font-display); font-weight: 650; font-size: var(--text-lg); line-height: 1.25; color: var(--color-brand); }
.pc-meta { font-size: 14px; line-height: 1.35; color: var(--color-ink-2); margin-top: 2px; }
.pc-say { font-size: var(--text-sm); line-height: 1.45; font-style: italic; color: var(--color-text); }
.pc-trust { list-style: none; margin: 0; padding: 0; }
.pc-trust li { margin: 0; max-width: none; font-size: var(--text-xs); line-height: 1.35; color: var(--color-ink-2); display: flex; gap: 6px; align-items: flex-start; }
.pc-trust .ic { flex: none; margin-top: 2px; color: var(--color-ok); }
.pc-price { font-family: var(--font-display); font-weight: 650; font-size: 22px; line-height: 1.1; font-feature-settings: "tnum", "lnum"; color: var(--color-text); }
.pc-del { font-size: var(--text-xs); line-height: 1.4; color: var(--color-ink-2); }
.pc-go { color: var(--color-brand); display: inline-flex; transition: transform var(--dur-base) var(--ease-out); }
.pc:hover .pc-go { transform: translateX(3px); }
@media (prefers-reduced-motion: reduce) { .pc, .pc::after, .pc-go { transition: none; } .pc:hover, .pc:hover .pc-go { transform: none; } }
@container (width >= 640px) { .in { max-width: min(1100px, calc(100% - 2 * var(--space-6))); } }
```

## CARD-1: the ticket, extended (motif kept)

```css
.pc { background: var(--color-white); border: var(--card-border); border-radius: var(--radius-md); }
.pc-top { padding: 14px 16px 0; }
.pc-say { padding: 8px 16px 0; }
.pc-trust { padding: 10px 16px 12px; display: flex; flex-wrap: wrap; gap: 2px 12px; flex: 1; align-content: start; }
.pc-stub { position: relative; border-top: 1.5px dashed var(--color-border); padding: 10px 16px 12px; display: grid; grid-template-columns: 1fr auto;
  grid-template-areas: "price go" "del go"; align-items: center; column-gap: 8px; background: var(--color-bone-50); border-radius: 0 0 var(--radius-md) var(--radius-md); }
.pc-stub::before, .pc-stub::after { content: ""; position: absolute; top: -8px; width: 14px; height: 14px; border-radius: 50%; background: var(--color-surface); border: var(--card-border); }
.pc-stub::before { left: -8px; clip-path: inset(0 0 0 50%); }
.pc-stub::after { right: -8px; clip-path: inset(0 50% 0 0); }
.pc-price { grid-area: price; } .pc-del { grid-area: del; } .pc-go { grid-area: go; }
@container (width >= 560px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .pc-trust { display: grid; grid-template-columns: 1fr; gap: 4px; } }
@container (width >= 780px) { .grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; } }
```

## CARD-2: the portrait card (photo-led layout)

It adds the photo, with `puppyAlt(p, 'scene')` for alt text. That alt is new on this page,
so the "same photo, new alt" rule holds. Import `Image`, `puppyImage`, `focusClass` and
`puppyAlt`. `sizes`: `(min-width: 1280px) 243px, (min-width: 1024px) 288px, (min-width: 560px) calc(50vw - 40px), 88px`.
The painted widths this was measured against: 88px at 375, 280 at 640, 342 at 768, 286 at
1024 and 243 at 1280. Run `img-sizes-matches-box` again after the build.

```css
.pc { background: var(--color-white); border: var(--card-border); border-radius: var(--card-radius); box-shadow: var(--shadow-card);
  display: grid; grid-template-columns: 88px minmax(0, 1fr); grid-template-areas: "img top" "say say" "trust trust" "stub stub"; column-gap: 12px; padding: 12px; }
.pc-img { grid-area: img; width: 88px; height: 88px; object-fit: cover; border-radius: var(--radius-md); background: var(--color-bone-50); display: block; }
.pc-top { grid-area: top; align-self: center; }
.pc-say { grid-area: say; padding-top: 10px; }
.pc-trust { grid-area: trust; display: flex; flex-wrap: wrap; gap: 6px; padding-top: 10px; }
.pc-trust li { background: var(--color-brand-soft); border-radius: var(--radius-pill); padding: 3px 10px 3px 7px; align-items: center; color: var(--color-text); }
.pc-trust .ic { margin-top: 0; }
.pc-stub { grid-area: stub; margin-top: 12px; padding-top: 10px; border-top: var(--card-border); display: grid; grid-template-columns: auto 1fr auto; grid-template-areas: "price del go"; align-items: center; column-gap: 12px; }
.pc-price { grid-area: price; } .pc-del { grid-area: del; } .pc-go { grid-area: go; }
@container (width >= 560px) {
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
  .pc { grid-template-columns: minmax(0, 1fr); grid-template-areas: "img" "top" "say" "trust" "stub"; padding: 0 0 14px; overflow: clip; }
  .pc-img { width: 100%; height: auto; aspect-ratio: 16 / 10; border-radius: 0; }
  .pc-top { padding: 12px 16px 0; }
  .pc-say, .pc-trust { padding-inline: 16px; }
  .pc-stub { margin: 12px 16px 0; grid-template-columns: 1fr auto; grid-template-areas: "price go" "del go"; }
}
@container (width >= 780px) { .grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
```

## CARD-3: the steel pass (accent role changes) (Recommended)

```css
.in { background: var(--color-surface-inverse); border-radius: var(--radius-lg); padding: 16px 12px; margin-block: var(--space-5); }
.grid { gap: 10px; }
.label { color: var(--color-link-on-inverse); }
.pc { background: var(--color-bone-50); border-radius: var(--radius-md); padding: 12px 14px; gap: 8px; }
.pc:focus-within { outline-color: var(--color-focus-on-inverse); }
.pc-say { font-size: var(--text-sm); line-height: 1.4; }
.pc-top { display: grid; grid-template-columns: minmax(0, 1fr) auto; grid-template-areas: "name price" "meta price"; column-gap: 10px; align-items: center; }
.pc-name { grid-area: name; } .pc-meta { grid-area: meta; }
.pc-price-chip { grid-area: price; background: var(--color-cta); color: var(--color-cta-ink); border-radius: var(--radius-pill); padding: 6px 12px; font-size: 18px; }
.pc-trust { display: flex; flex-wrap: wrap; gap: 1px 10px; padding-top: 8px; border-top: var(--card-border); }
.pc-trust li { line-height: 1.3; }
.pc-stub { display: grid; grid-template-columns: 1fr auto; align-items: center; column-gap: 8px; margin-top: auto; padding: 8px 12px; border-radius: var(--radius-sm); background: var(--color-brand-soft); }
.pc-del { color: var(--color-text); font-weight: 600; }
@container (width >= 560px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; } .in { padding: var(--space-5); margin-block: var(--city-pad-y); } .pc { padding: 14px 16px; gap: 10px; } }
@container (width >= 780px) { .grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
```

In CARD-3 the price moves into `.pc-top` as `<p class="pc-price pc-price-chip">`, and the stub
carries only the delivery line and the arrow.

---

## FIX-a: the two chapter questions that wrap to four lines at 640 and 1024 (Recommended)

`src/components/kit/CityChapters.astro`, in the `@container (width >= 640px)` block (the
`>= 800px` block still sets its own `1fr / 340px`):

```diff
       .ch {
-        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
+        /* 7 : 5, not 1 : 1 (London previews 2026-10-04, FIX-a): in the 656px column beside the dial
+           and at 640-667px a long question took 4 lines in half the tray; seven-twelfths holds it to 3. */
+        grid-template-columns: minmax(0, 7fr) minmax(0, 5fr);
```

and the photo's `sizes`, in the same file, the tablet term:

```diff
-  tablet: (B) => `calc((min(${B}, 1164px) - 152px) / 2)`,
+  tablet: (B) => `calc((min(${B}, 1164px) - 152px) * 5 / 12)`,
```

(Measured photo width with the fix: 203px at 640, 210px in the 656px column, 257px at 768.
The formula gives 203, 210 and 257.)

## FIX-b: the H1 wraps to four lines at 375 (and at 1024) (Recommended)

`src/components/kit/CityHeroFilmstrip.astro`, inside `@layer components`:

```diff
+    /* THE H1 FITS THREE LINES ON A PHONE (London previews 2026-10-04, FIX-b): the panel sits 8px
+       in from the screen with 8px of padding and the copy loses its own 8px inset, so the H1 gets
+       343px of the 375px screen, not 311px; at 24px (2px over the phone H2's 22px) it takes three lines. */
+    @media (width < 640px) {
+      .inner { max-width: calc(100% - 2 * var(--space-2)); padding: var(--space-2); }
+      .copy { padding-inline: 0; }
+      .title { font-size: 24px; }
+    }
     @media (1024px <= width < 1200px) {
       .pic :global(img) { height: 120px; }
+      /* 1024-1199: the H1 column is 432px at 1024; the desktop tier's own floor (31px) and a 32px
+         gutter hold it to 3 lines without stretching the lede past 6. */
+      .copy { column-gap: var(--space-6); }
+      .title { font-size: 31px; }
     }
```

and the strip's phone `sizes` term (the thumbs grow by about 5px):

```diff
-  + '(min-width: 640px) calc(16.667vw - 14.667px), calc(33.333vw - 21.333px)';
+  + '(min-width: 640px) calc(16.667vw - 14.667px), calc(33.333vw - 16px)';
```

## FIX-c: the hero band is 18px over its 450px ceiling at 1280 (Recommended)

`src/components/kit/CityHeroFilmstrip.astro`, in the `@media (width >= 1024px)` block:

```diff
-      .pic :global(img) { aspect-ratio: auto; height: 148px; }
+      /* 128px, not 148 (London previews 2026-10-04, FIX-c): the band measured 468px at 1280 and 1440;
+         rule 10 says the photo is what the clamp crops, so the strip gives up the 20px, not the copy. */
+      .pic :global(img) { aspect-ratio: auto; height: 128px; }
```

(1024–1199 keeps its own 120px rule. Re-run `scripts/measure_canvas_heights.mjs` and
`tests/py/test_design_components.py::test_measured_hero_fits_its_clamp_without_clipping_anything`.)

## FIX-d: chapter sections over the height cap

No CSS-only diff makes these rows pass. The measurements are on `index.html`. The options are
a gate ruling (d-1), a split of the outline (d-2), or a change to the approved phone
infographics (d-3). Each needs the breeder's decision first, so there is nothing to apply yet.
