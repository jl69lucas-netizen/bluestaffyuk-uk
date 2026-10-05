# London map preview: the diffs to apply after approval

Preview only. Nothing here is applied: `src/`, `data/` and the boards are unchanged. Apply in this
order once the breeder has picked a placement and a style on the answer board. Everything below is
written for the **recommended pick, P1 + S1**; the S2 and S3 deltas are at the end of section 1.

---

## 1. New kit component: `src/components/kit/CityMapFacade.astro`

```astro
---
// src/components/kit/CityMapFacade.astro: city component 20, the map (London pick: map S1,
// "Steel panel"; answer board <date> q<NN>). A click-to-load Google Maps embed of the CITY CENTRE
// (.claude/skills/bsuk-google-map/SKILL.md, "Template: a UK city page"). The target is the row's
// `city` from data/locations.json, passed in by the page and never typed. It is never a street, a
// postcode or coordinates. The map shows where the BUYER is. The caption says where we are
// (Carlisle) and how the puppy gets there: the delivery band by distance, by DEFRA-approved
// transport, or collection. No drive time, no mileage, no route line.
//
// NOTHING IS REQUESTED FROM GOOGLE UNTIL THE READER TAPS. The panel is drawn from tokens (an
// abstract contour motif and a brass pin, inline SVG), never a Static Maps image, so the page makes
// no third-party request and sets no third-party cookie at load (the Known Issue 38 trade-off, met
// here the way working rule 14 meets it for video). On a tap the iframe takes the panel's reserved
// box, so nothing below it moves. The button is a real <button> (44px, keyboard, focus ring), and
// focus moves into the map once it is in place.
import type { HTMLAttributes } from 'astro/types';
import { TOWN } from '../../lib/cityKit';

type Props = HTMLAttributes<'figure'> & {
  /** data/locations.json `city` for this page's row. */
  city: string;
  /** The delivery caption, built by the page from data/settings.json. */
  caption: string;
  /** Google's zoom: 10 shows a whole city. */
  zoom?: number;
};
const { city, caption, zoom = 10, class: cls, ...rest } = Astro.props;
// The two hub rows are city "UK" and never carry a city map (the skill's rule).
if (!city || city === 'UK') throw new Error('CityMapFacade: a hub row ("UK") never carries a city map');
const src = `https://maps.google.com/maps?q=${encodeURIComponent(`${city}, UK`)}&z=${zoom}&hl=en&t=m&output=embed&iwloc=near`;
const title = `${city} — delivery from BlueStaffyUK in ${TOWN}`;
const noteId = `map-note-${city.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
---
<figure {...rest} class:list={['city-map', cls]} data-city-map data-src={src} data-title={title}>
  <div class="stage">
    <svg class="art" viewBox="0 0 400 240" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">
      <g fill="none" stroke="currentColor">
        <path d="M-20 168C50 132 104 190 168 160S262 98 324 132 396 156 430 124" stroke-width="14" opacity=".45" stroke-linecap="round" />
        <g stroke-width="1.2" opacity=".75">
          <ellipse cx="200" cy="112" rx="60" ry="44" /><ellipse cx="200" cy="112" rx="112" ry="80" />
          <ellipse cx="200" cy="112" rx="170" ry="118" /><ellipse cx="200" cy="112" rx="232" ry="160" />
        </g>
      </g>
    </svg>
    <svg class="pin" viewBox="0 0 32 42" aria-hidden="true" focusable="false">
      <path class="body" d="M16 1.5C8 1.5 1.5 7.9 1.5 15.8 1.5 26.6 16 40.5 16 40.5s14.5-13.9 14.5-24.7C30.5 7.9 24 1.5 16 1.5z" />
      <circle class="dot" cx="16" cy="15.6" r="5.4" />
    </svg>
    <span class="place">{city}</span>
    <button type="button" class="load" data-city-map-load aria-describedby={noteId}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M1 6v16l7-4 8 4 7-4V2l-7 4-8-4-7 4z" /><path d="M8 2v16M16 6v16" /></svg>
      Show the map
    </button>
  </div>
  <figcaption>
    <p class="cap">{caption}</p>
    <p class="note" id={noteId}>Nothing loads from Google until you tap. Showing the map loads Google Maps, which sets its own cookies.</p>
  </figcaption>
  <noscript><p class="note"><a href={src} target="_blank" rel="noopener noreferrer">Open the map of {city} on Google Maps</a></p></noscript>
</figure>

<script>
  // ONE DELEGATED LISTENER for the document (VideoEmbed's pattern): the map's iframe is made
  // only here, on a tap, so Google is never asked for anything at load.
  document.addEventListener('click', (event) => {
    const button = (event.target as Element | null)?.closest?.('[data-city-map-load]');
    if (!button) return;
    const fig = button.closest('[data-city-map]') as HTMLElement | null;
    const stage = fig?.querySelector('.stage');
    if (!fig || !stage) return;
    const frame = document.createElement('iframe');
    frame.src = fig.dataset.src ?? '';
    frame.title = fig.dataset.title ?? 'Map';
    frame.loading = 'lazy';
    frame.referrerPolicy = 'no-referrer-when-downgrade';
    frame.allowFullscreen = true;
    stage.classList.add('live');
    stage.replaceChildren(frame);
    fig.toggleAttribute('data-loaded', true);
    // The button that had focus has gone; without this the reader is returned to the top.
    frame.focus();
  });
</script>

<style>
  @layer components {
    /* Inside CityChapters' text column, whose `.txt p` rule is (0,2,1): every rule here carries
       the figure's class, so the scoped selectors (0,4,0) win without !important. */
    .city-map { margin: var(--space-4) 0; min-width: 0; container-type: inline-size; }
    /* THE RESERVED BOX: 4:3 in a narrow column, 16:9 from 560px, never taller than 300px (the
       1280 answer cap: at 360px the delivery answer had 21px left under 1.6 viewports; at 300px
       it has 81px, measured 2026-10-06). The iframe takes this same box on a tap. */
    .city-map .stage {
      position: relative; isolation: isolate; display: grid; place-items: center; align-content: center;
      gap: var(--space-3); width: 100%; aspect-ratio: 4 / 3; max-height: 300px; overflow: hidden;
      border-radius: var(--radius-md); background: var(--color-surface-inverse); color: var(--color-text-on-inverse);
      box-shadow: var(--shadow-card);
    }
    @container (width >= 560px) { .city-map .stage { aspect-ratio: 16 / 9; } }
    .city-map .art { position: absolute; inset: 0; width: 100%; height: 100%; z-index: -1; color: var(--color-brand-mid); }
    .city-map .pin { display: block; width: 40px; height: 52px; }
    .city-map .pin .body { fill: var(--color-cta); }
    .city-map .pin .dot { fill: var(--color-surface-inverse); }
    .city-map .place {
      display: block; font-family: var(--font-display); font-weight: 600; font-size: var(--text-xl);
      line-height: 1.1; letter-spacing: 0.01em; color: var(--color-text-on-inverse);
    }
    /* rules/design.md rule 3: the CTA pill. */
    .city-map .load {
      display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2);
      min-height: 44px; padding: var(--space-2) 22px; border: 0; border-radius: var(--btn-radius);
      background: var(--color-cta); color: var(--color-cta-ink); font: inherit; font-weight: 700; line-height: 1.25;
      box-shadow: var(--shadow-card); cursor: pointer; transition: background-color var(--dur-fast) var(--ease-out);
    }
    .city-map .load svg { width: 18px; height: 18px; flex: none; }
    .city-map .load:hover { background: var(--color-cta-hover); }
    /* On the steel panel the ring is brass (tokens.css: steel on steel would disappear). */
    .city-map .load:focus-visible { outline: 3px solid var(--color-focus-on-inverse); outline-offset: 3px; }
    .city-map .stage.live { background: var(--color-bone-50); }
    /* The iframe is made by the script, so it has no scope attribute: :global. */
    .city-map .stage :global(iframe) { position: absolute; inset: 0; display: block; width: 100%; height: 100%; border: 0; }
    .city-map .cap { margin: var(--space-3) 0 0; font-size: var(--text-sm); line-height: 1.5; color: var(--color-ink-2); }
    .city-map .note { margin: var(--space-1) 0 0; font-size: var(--text-xs); line-height: 1.4; color: var(--color-ink-2); }
    @media (prefers-reduced-motion: reduce) { .city-map .load { transition: none; } }
  }
</style>
```

Colour pairs used, all already in `data/design/contrast.json`: `--color-text-on-inverse` on
`--color-surface-inverse` (the place name), `--color-cta-ink` on `--color-cta` (the button),
`--color-ink-2` on `--color-brand-soft` (the caption and note, on the chapters' tray). The pin, the
contour motif and the focus ring are non-text. **No `contrast.json` change is needed for S1.**

### If the breeder picks S2 (bone card, steel line-map motif) instead

Swap the `.art` SVG for the street-grid motif in `harness/facade.mjs` (`ART_S2`), and change:

```css
.city-map .stage { background: var(--color-bone-50); color: var(--color-brand); border: var(--card-border);
  border-radius: var(--card-radius); box-shadow: var(--shadow-card); }
.city-map .art { color: var(--color-brand-tint); }
.city-map .pin .body { fill: var(--color-cta); stroke: var(--color-brand); stroke-width: 1.5; }
.city-map .pin .dot { fill: var(--color-bone-50); }
.city-map .place { color: var(--color-brand); }
.city-map .load:focus-visible { outline-color: var(--color-focus); }
```
Pairs: `--color-brand` on `--color-bone-50` (present). No contrast change.

### If the breeder picks S3 (compact strip) instead

Markup: replace `.stage` with a strip, and let the script create the stage on a tap:

```astro
<div class="strip">
  <span class="disc"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" /><circle cx="12" cy="10" r="3" /></svg></span>
  <span class="label"><span class="city">{city}</span> <span class="sub">on Google Maps</span></span>
  <button type="button" class="load" data-city-map-load aria-describedby={noteId}>…Show the map</button>
</div>
```
Script: `let stage = fig.querySelector('.stage'); if (!stage) { stage = document.createElement('div'); stage.className = 'stage'; fig.querySelector('.strip')!.after(stage); } button.remove();`.
Because that stage is made by the script, every stage rule must be written `.city-map :global(.stage)`.
CSS: `.strip { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-3); background: var(--color-surface-raised); border: var(--card-border); border-radius: var(--radius-md); box-shadow: var(--shadow-card); }`,
`.disc { flex: none; display: grid; place-items: center; width: 40px; height: 40px; border-radius: 50%; background: var(--color-cta-soft); color: var(--color-brand); }`,
`.label { flex: 1 1 0; min-width: 0; display: grid; line-height: 1.2; }`, `.city { font-family: var(--font-display); font-weight: 600; font-size: var(--text-lg); color: var(--color-brand); }`,
`.sub { font-size: var(--text-xs); color: var(--color-ink-2); }`, the live stage `margin-top: var(--space-3); max-height: 260px` (at 300px the loaded 1280 answer is 1,281px, 1px over its cap),
and below a 400px box `gap: var(--space-2)`, a 32px disc, `padding-inline: 16px` on the button and its icon hidden. Without that, "London on Google Maps" broke onto four lines at 375.
Pairs: `--color-brand` and `--color-ink-2` on `--color-white` (both present).

---

## 2. `src/pages/uk-locations/blue-staffy-puppies-london.astro`

```diff
 import CityPlacesByPublisher from '../../components/kit/CityPlacesByPublisher.astro';
+import CityMapFacade from '../../components/kit/CityMapFacade.astro';
 import { placeGroups, type PlaceRow } from '../../lib/cityPlaces';
```

P1: delivery answer 3, first in the `ch-3` slot, so it sits after the answer's opening paragraph
("…from Enfield in the north to Sutton in the south.") and before the past-deliveries paragraph:

```diff
     <Fragment slot="ch-3">
+      {/* The London map (answer board <date> q<NN>; subcomponent london-map): the city centre from
+          the row's `city`, a tap-to-load facade, the delivery caption from data/settings.json. */}
+      <CityMapFacade city={loc.city}
+        caption={`We deliver from ${TOWN} for ${DELIVERY_BAND}, priced by distance, by DEFRA-approved transport, or you collect your puppy from us in ${TOWN}.`} />
       <p>Puppies from {BREEDER} have gone to {PAST_DELIVERIES} before. London buyers take home delivery, and handovers are by request, so ask us when you enquire.</p>
```

`loc` is the page's London row (line 78); `TOWN` and `DELIVERY_BAND` are already imported from
`src/lib/cityKit.ts` (`settings.address.city`, `settings.delivery_min_gbp`–`delivery_max_gbp`).

(P2, if picked instead: in the `london-life` `ch-1-full` slot, between the parks paragraph and
`<CityPlacesByPublisher …/>`. The component and caption stay the same.)

---

## 3. `data/design/components.json`: one row after C19

```json
  {"id": "city-map-facade", "file": "CityMapFacade.astro", "title": "C20 · City map (tap to load)", "board_width": 1280, "project": 5, "subcomponent": "london-map"}
```

Only London mounts it, so the own-components rule (`component-shared`) is untouched.

---

## 4. `docs/reference/external-link-library.md`: one row

The library's own columns (`| URL | Host | What it is | First page using it | Verified | Source type |`):

```
| https://maps.google.com/maps?q=London%2C%20UK&z=10&hl=en&t=m&output=embed&iwloc=near | maps.google.com | Google Maps, the London city centre at zoom 10, as a tap-to-load embed (an iframe, not a citation): it shows where the buyer is, never where we are | `/uk-locations/blue-staffy-puppies-london/` | 2026-10-06 · 301 → 200 (www.google.com/maps/embed) | other |
```

`other` counts toward the six links and six domains but not toward the four source types.

The library is the allowlist `pageboard.validate_board` holds every external href to, so the board
row in section 5 needs this row first.

---

## 5. `data/boards/blue-staffy-puppies-london.json`: three entries, then re-approve

**5a. `sections[id=delivery].links.external[]`** (working rule 12: target, anchor/title, purpose, resolves today):

```json
{
  "href": "https://maps.google.com/maps?q=London%2C%20UK&z=10&hl=en&t=m&output=embed&iwloc=near",
  "anchor": "London — delivery from BlueStaffyUK in Carlisle",
  "anchor_type": "branded",
  "library_row": "https://maps.google.com/maps?q=London%2C%20UK&z=10&hl=en&t=m&output=embed&iwloc=near",
  "why": "EMBED, not a body link. The London map (subcomponent london-map): an iframe whose title is the anchor, loaded only when the reader taps 'Show the map' (no request to Google before the tap). The without-JavaScript fallback is a <noscript> link to the same URL, worded 'Open the map of London on Google Maps'. Purpose: shows where the buyer is (London city centre, zoom 10, from data/locations.json city). It never implies BlueStaffyUK is in London; the caption names Carlisle. No route, mileage or drive time. Resolves today: yes. Checked 2026-10-06: 301 to www.google.com/maps/embed, then 200, and the map painted in the preview at 375 and 1280 (docs/reports/london-map-preview-2026-10-06/)."
}
```

**5b. `subcomponents[]`:**

```json
{
  "id": "london-map",
  "section": "delivery",
  "node": "tree[2]",
  "heading": "Which Way Does My Staffordshire Puppy Travel to London?",
  "name": "London map (tap to load)",
  "placement": "in answer 3, after its opening paragraph (…from Enfield in the north to Sutton in the south.) and before the past-deliveries paragraph, at the text column's width",
  "style": {
    "pick": "A",
    "name": "S1 · Steel panel, brass pin",
    "preview": "docs/reports/london-map-preview-2026-10-06/index.html"
  },
  "source": "answer board 2026-10-0X-london-map q01",
  "data": [
    "data/locations.json row blue-staffy-puppies-london `city` (the map query 'London, UK', zoom 10)",
    "data/settings.json address.city, delivery_min_gbp, delivery_max_gbp (the caption, via src/lib/cityKit.ts TOWN and DELIVERY_BAND)"
  ],
  "condition": "the facade always renders; the iframe exists only after a tap. No Static Maps image, no street, postcode or coordinates, no route line, no drive time or mileage.",
  "links": ["https://maps.google.com/maps?q=London%2C%20UK&z=10&hl=en&t=m&output=embed&iwloc=near"]
}
```

(For P2: `"section": "london-life"`, `"node": "tree[0].children[0]"`,
`"heading": "Where Can a Flat-Dwelling Staffy Stretch Its Legs in London's Parks?"`, and the 5a
row goes in `sections[id=london-life].links.external[]`.)

**5c. `board_revisions[]`** (the 41st row):

```json
{
  "date": "2026-10-0X",
  "source": "answer board 2026-10-0X-london-map q01",
  "decision": "The London map: placement P1 (delivery answer 3) and facade S1 (steel panel, brass pin), click-to-load. Proposal docs/reports/london-map-preview-2026-10-06/.",
  "record_change": "subcomponents[london-map]; delivery.links.external + one library row (Google Maps embed, type other); component C20 city-map-facade",
  "sections": ["delivery"]
}
```

**Validated 2026-10-06** in memory against `pageboard.validate_board` (the real board, a scratch copy
of the library with the section 4 row): **OK**. The schema (`board.schema.json`) is strict about
three things. A link row takes no extra keys, so `kind: "embed"` was refused and the embed is said
in `why`. `style.pick` is one capital letter (S1 = `A`, S2 = `B`, S3 = `C`). `source` must read
`answer board YYYY-MM-DD-<batch> qNN`. Replace `2026-10-0X-london-map q01` with the real batch and
question.

Then `python3 scripts/board_approve.py blue-staffy-puppies-london` and
`python3 scripts/board_gate.py blue-staffy-puppies-london`.

---

## 6. After applying: gates and follow-ups

- `npm run -s build`, then `npm run check:all`, `npm run test:render:meta`, then
  `npm run gate:page -- blue-staffy-puppies-london` (twice by design). City type-fit should read
  **0 new defects** with the answer at 1,697 / 2,030 px at 375 and 1,199 / 1,280 px at 1280,
  the figures this preview measured.
- A suggested render probe for `tests/render/city-kit.spec.ts` (London route): (1) no request to a
  Google host after load; (2) `.city-map .load` is at least 44px tall and reachable by Tab; (3) a
  click puts an `iframe` in `.stage` whose `title`, `loading=lazy` and
  `referrerpolicy=no-referrer-when-downgrade` match, and the answer's height does not change.
- `.claude/skills/bsuk-google-map/SKILL.md` says "No rebuilt page carries one today"; update that
  line to name London and `CityMapFacade.astro` once this ships.
- `rules/links.md` / `scripts/link_diversity.py`: the embed counts as an external link of type
  `other` (one more link, one more domain, `google.com`). That only adds to the six-link minimum.
  If the breeder would rather an embed not count at all, that needs a new field in
  `board.schema.json` and an exclusion in `link_diversity.external_links()`, which is a tooling
  change outside this preview. Measured on the dry run, the page's external summary goes from
  14 to 15 links and from 11 to 12 domains (`google.com` added), with the source types unchanged.
