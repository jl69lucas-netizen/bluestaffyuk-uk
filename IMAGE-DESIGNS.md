# Image Designs

> **Read this before you choose, generate, frame or place any image on BlueStaffyUK.**
> `rules/design.md` and `src/styles/tokens.css` govern *the page*. **This file governs *the
> picture*:** how a photograph or infographic must look, how it is cropped and lit, which
> named style frames it, and how it is approved before a build may use it.
>
> **This file wins.** If an image agent or skill carries an older value (a stale colour, a
> wrong town, a crop recipe that cuts the dog's head off), the value here is canonical: fix
> the consumer to match this file, never the reverse.
>
> "OG photo" in this file means an **original photograph** (a real photo of our dogs, or one
> from the breeder's folder), not the Open Graph share card. The share card is its own slot in §1.
>
> **Scope.** This file governs the images on location, comparison and blog-post pages built
> from 2026-09-24 on. `scripts/family_rules.py` names the pages it never touches: the pages
> built before keep their images and boards unchanged.

---

## 0. Brand Facts

- **Breeder:** Lisa Bright, BlueStaffyUK, **Carlisle, Cumbria** (town and region only; there
  is no street and no postcode, Known Issue 16). Source of truth: `data/settings.json`.
  Copy speaks as *we / us / our*; an image carries mood, never words.
- **In-image palette** (echo the site, never fight it; the hexes are the locked tokens in
  `src/styles/tokens.css`):
  - **Steel `#1F3A52`**: framing, deep background tone, infographic title bars.
  - **Slate `#5B7C99`**: cool mid-tone for secondary surfaces. A blue coat sits close to
    slate, so a slate background must be lit or blurred apart from the dog, never behind it
    at the same value.
  - **Brass `#C9A227`**: a small warm accent only (a collar tag, a lead clip, a lamp, a
    figure on an infographic). Never the dominant cast. Brass on bone fails contrast, so
    brass text sits on steel only.
  - **Bone `#F4F1EA`**: surfaces, walls, blankets, infographic beds.
  - **Grade:** neutral to gently warm daylight. Never a cold blue cast, never a grey
    clinical look, never a studio flash.
- **Breed accuracy (non-negotiable: get the dog right).** Every dog is a **blue Staffordshire
  Bull Terrier**, drawn to the registry's breed standard: the royalkennelclub.com
  Staffordshire Bull Terrier breed-standard row in `docs/reference/external-link-library.md`.
  Every breed description below is worded as the repo's breed facts state it, in
  `data/facts/uk-staffordshire-bull-terrier-guide.json`; describe nothing it does not.
  - **Medium-sized** and **muscular**.
  - Head **Broad and deep**, with **pronounced cheek muscles**.
  - Coat **Short, smooth, and close-lying**; for our dogs, the **grey/blue** coat, or blue
    with white where the puppy really is marked that way.
  - Ears **Rose or half-pricked**, natural and **never cropped**.
  - Relaxed, friendly expression. A puppy is a puppy: soft, curious, close to the family.
  - **NEVER** a generic dog, another breed, a cartoon stand-in or a dog emoji (design rule 7).

---

## 1. Crop & Aspect Ratios (per slot)

| Slot | Ratio | Pixels | Notes |
|---|---|---|---|
| Hero | 16:9 | 1600×900 master | LCP image: `fetchpriority="high"`, WebP, never lazy. The page's own hero style decides the frame (CLAUDE.md rule 16) |
| In-body section (H2 or H3) | 1408:768 | 1408×768 plus a 760×415 sibling | The uniform box of §1a. OG photo and infographic alike |
| Share card (Open Graph) | 1.91:1 | 1200×630 | One per page; same subject as the hero, recomposed, never the hero squashed |
| Further-reading thumb | 1408:768 family | 320×175 and 760×416 | Always the TARGET page's own hero (`rules/images.md`) |
| Social vertical | 9:16 | 1080×1920 | Reels and Shorts only; never placed on a page |
| HTML infographic | per page width | 760px (guide, blog, care) or 1100px (home, location) wide, 400px tall desktop, auto on mobile | Design rule 9 in `rules/design.md` |

### 1a. Uniform In-Body Image Sizing

The rule is `uniform-inbody-image-sizing` in `rules/images.md`, and this file does not restate
it differently: every in-body section image, OG photo and infographic alike, renders in the
same `.sec-img.inf-img` box (`max-width:760px; aspect-ratio:1408/768; object-fit:cover`),
identical at every width, shipped as a WebP under 95 KB plus a `-760.webp` sibling with
`srcset`/`sizes`.

What this file adds is **how a master becomes that 1408×768 file without losing the dog.**
A landscape master already close to 16:9 may be cover-fitted with a per-image focal point
(`data/image-centering.json`). A portrait or near-square master must NOT be: it is baked
with a named framing style from §7 by `scripts/reframe_og.py`, which returns a 1408×768 file
that keeps the whole dog, so the box's `object-fit:cover` then has nothing left to cut.

---

## 2. Reusable Style Wrapper

Prepend this string to every photoreal prompt, then add the scene from §5:

> Editorial pet photography, soft natural daylight with a gentle warm cast, shallow depth of
> field, a true-to-breed blue Staffordshire Bull Terrier: medium-sized and muscular, broad
> and deep head with pronounced cheek muscles, short, smooth, close-lying grey/blue coat,
> natural rose or half-pricked ears, calm friendly expression, relaxed family home in the north of England,
> steel-blue and bone palette with one small brass accent, photorealistic, crisp detail on
> the eyes and coat.

---

## 3. Negative List

Append this string to every prompt. It is non-negotiable:

> no text, no watermarks, no logos, no captions, no UI chrome, no cropped ears, no fighting or
> aggression imagery, no bared teeth or snarling, no dog pulling toward another dog, no
> spiked collar, no chain collar, no XL Bully build, no pit-bull-type build, no oversized
> head or exaggerated bulk, no tall leggy frame, nothing that could imply a banned type, no
> other breed, no generic dog, no merle or bright-blue coat, no cartoon, 3D or illustration
> style for a photo slot, no cold blue cast, no clinical or studio lighting, no kennel rows
> or cages, no distorted anatomy, no extra legs or merged paws, no sharp identifiable human
> faces unless it is a real buyer photo, no cluttered background.

---

## 4. Lighting & Focal Length (per scene)

| Scene | Lighting | Focal length / aperture |
|---|---|---|
| Hero portrait | soft window light or late-afternoon daylight | 85mm f/1.8 |
| Family lifestyle | ambient room light, candid | 35–50mm f/2.8 |
| Size reference (puppy in two hands) | even, bright, full coat detail | 50mm f/4 |
| Health and coat detail | diffused, no flash | 100mm macro f/5.6 |
| Garden and exercise | open shade or soft overcast | 70–200mm f/2.8 |
| Travel and collection | clean interior daylight | 35mm f/4 |
| Infographic | flat design | N/A |

---

## 5. Scene Types by Page Type (routing table)

| Page type | Hero scene | Body H2 slots | Body H3 slots | Avoid |
|---|---|---|---|---|
| Location | one blue puppy, direct gaze, soft local context of the city (a park path or terrace street well out of focus) | IG-5 route map for delivery or collection sections; family-life OG photos elsewhere | IG-2 steps for reserve and collection; size-reference or garden photos | landmark postcards, flags, maps baked into a photo, any claim of a local address |
| Comparison | both subjects side by side, same light, same scale | IG-3 comparison split in at least one H2; OG photos framed with Style H for a pair | IG-1 stat panel for figures; IG-4 checklist for what to check | showing only one subject, a winner-and-loser mood |
| Blog | topic-illustrative lifestyle or portrait | OG photo that shows the section's subject; an infographic when the section is data or steps | IG-2 or IG-4 for how-to and checklist H3s; detail photos otherwise | price overlays, sales mood on a care topic |

The migrated page's own images come first, always (CLAUDE.md rule 11). A slot is only
generated when no existing image fits: not the migrated page's images, not `public/images/`,
and not the breeder's folder `/Users/apple/Downloads/BSUK/bluestaffyuk-cms/Assets/Images/`.

---

## 6. Output Handoff

Every image, found or generated, reaches the site the same way:

1. **A folder photo** (`source: assets-folder`): the **`bsuk-photo-ingest`** skill runs
   `python3 scripts/ingest_image.py folder …`, which bakes it into `public/images/` under an
   SEO filename, records the manifest row and, when the name differs from the default,
   writes it into the slot's `assets[]` row `file`.
2. **A generated photo or infographic** (`source: generate` or `infographic`): the
   **`bsuk-image-generation`** or **`bsuk-infographic`** skill produces a master,
   `python3 scripts/ingest_image.py draft …` bakes it into the board's draft folder, and only
   after the board approves those exact bytes does `python3 scripts/ingest_image.py publish …`
   copy them, unchanged, into `public/images/` (§9).
3. **`image-metadata`** skill: filename, alt (190 characters at most), title, caption.
4. **Keyword distribution** (`image-keyword-distribution` in `rules/images.md`): the primary
   keyword goes in the primary image's alt only; every other image rotates a different
   keyword type, and no two images on a page share an alt.

A file already served is never renamed, moved, re-encoded or deleted (CLAUDE.md rule 11).

---

## 7. Named OG Framing Styles

**The head-cutoff rule:** never cover-crop a portrait or near-square master into the wide box
with a focal point. On a tall master that slices off the head. Pick a named style and bake it
with `scripts/reframe_og.py <master> <out.webp> --style <style> --sib <out-760.webp>`, which
writes a 1408×768 file that keeps the whole dog plus a `-760` sibling under 55 KB. Every
baked style centres the dog full-height, so a later mobile cover crop only trims padding.

| Id | Name | Engine | When to use | Whole dog? |
|---|---|---|---|---|
| `A` | Contain on Bone | `--style contain` | the default for any in-body photo on a new page, portraits included: wide shots, scenes, single dogs | yes |
| `B` | Blur-Fill | `--style blurfill` | social OG images only; the twelve built pages' existing in-body images | yes |
| `C` | Editorial Split | CSS component, master baked native | a "meet the puppy" moment: photo beside a steel caption panel | yes |
| `D` | Portrait Frame | CSS component, master baked native | a matted 3:4 portrait inside the 16:9 box | yes |
| `E` | Top-Anchored Cover | `--style topcover` | a photo that should fill the box; the head is never cut, paws may crop | head-safe |
| `H` | Duo Strip | CSS component, two masters baked native | two puppies or a pair, two portraits side by side | yes |

**Style `B`:** Retired for in-body images on new pages (user ruling 2026-09-26: bleeds use design colours — bone — never a blurred/grey/black bed). Social OG only. `scripts/ingest_image.py` refuses `--og-style B` for any page not in `BUILT_BEFORE_SYSTEM_GAPS` (`scripts/family_rules.py`), and board block 7 does not offer it there.

**Mobile counterparts** (full-bleed, taller): **mA** 4:5 top-cover · **mB** 4:5 contain ·
**mC** 4:5 blur-fill (matches B; retired for new pages, user ruling 2026-09-26 — use mB, 4:5 contain on bone, instead) · **mG** stacked two-up (matches H) · **mH** 3:4 top-cover.

**Standing default:** a single-dog or pair portrait on a new page is baked with
`--style contain` (Style `A`), which keeps the whole dog centred full-height over the bone
gradient, so a desktop 16:9 box or a mobile 4:5 crop only trims bone, never the dog, and the
bleed is always a design-system colour. The twelve built pages keep their existing
`--style blurfill --mobcrop 4:5` images. A wide scene or an infographic
keeps the standard 16:9 box and is never forced into 4:5.

---

## 8. Named Infographic Styles

An infographic is either an HTML/CSS component built on the tokens (the default: editable, no
cost) or a baked raster of the same design. Every figure on it is a locked fact from
`data/*.json` or a cited source (CLAUDE.md rule 9); an infographic never carries a number the
page cannot back. Text contrast uses only the pairs in `data/design/contrast.json`.

| Id | Name | Layout | Palette | Heading intents | Page types |
|---|---|---|---|---|---|
| `IG-1` | Stat Panel | two to four large figures, one line of context each | steel bed, brass figures (large text only), bone labels | cost, price, how much, how many | location, comparison, blog |
| `IG-2` | Process Steps | three to five numbered steps joined by a line | bone bed, steel numbered circles, slate connector | how to, steps, what happens, timeline | location, blog |
| `IG-3` | Comparison Split | two columns with a shared row per attribute and a verdict bar | steel-100 and bone-50 columns, steel headers, steel verdict bar with bone text | versus, difference, which is better | comparison, blog |
| `IG-4` | Checklist Grid | six to twelve cells, a line icon and a short line each | steel bed, bone text, brass tick glyph | checklist, what to check, what to bring, signs of | blog, comparison, location |
| `IG-5` | Route Map | a schematic line from Carlisle to the destination city, never map tiles | bone bed, steel route, brass Carlisle dot, slate destination dot | delivery, collection, travel, where | location |

**When to use which.** Choose by the heading's intent, not by the page's mood: a figures
heading gets IG-1, a sequence gets IG-2, two named subjects get IG-3, a list of checks gets
IG-4, a journey gets IG-5. IG-5 states only the locked delivery band (£200–£350 by distance,
by DEFRA-approved transport) and the collection alternative in Carlisle; it never prints a
mileage or a drive time nobody measured. Icons are line SVGs, never emoji (design rule 7).
A baked infographic is framed with Style `A` so no baked text is ever cropped.

**Board treatments (breeder q08, 2026-10-02: "nice, playful, cartoonish").** Each IG slot on
a project 5 board is shown in three styles: **sticker**, **chalk** and **comic** (pick
`ig:<slot>`).
- **sticker:** die-cut cards with ink outlines and the doodle-dog mascot.
- **chalk:** a sketchbook on bone graph paper with wobbly drawn lines, never wobbly text.
- **comic:** panels, speech-bubble labels and halftone corners.

All three are on the tokens only, and every figure is exact text.

**Measuring the frames.** `python3 scripts/infographic_plan.py <slug> --write` (or
`--heights`) needs node plus Playwright's Chromium. It measures every preview at 1280, 768 and
375 into `docs/artifacts/boards/ig/<slug>/heights.json`, together with each preview's sha256,
so a stale file fails a test. Without Chromium it deletes that file and exits 2.

**The `.fig` gate.** The measurement also refuses any exact figure (`.fig`) whose text
overflows its box or card or touches an icon.

**Baking.** Only after the pick, one style per slot (Task 9 or STOP 4):
`infographic_plan.bake_infographic()` writes two lossless masters, both cropped to the figure on
a transparent ground: the box master, rendered at the width whose figure is shaped most like
1408:768 (no exact figure may wrap there), and the reflowed phone layout, exactly 760 wide. It
refuses a box covered under 85% of its binding side, and phone text under 14px. Then
`python3 scripts/ingest_image.py draft <box master> --board <slug> --slot <slot> --infographic IG-<n> --sibling <phone master>`
frames the box master with Style A through its alpha (the margin is the frame's own bone, so no
band), stores the phone master beside the draft as `<slot>-760.webp`, and `publish` serves that
file as the `-760` sibling instead of shrinking the box.

---

## 9. Approval Before the Build

**Every choice is shown on the page board and approved before a build uses it:** each slot's
image, each OG style pick, each infographic style pick, and each generated image. The board
renders a candidate in the slot's own box, never a description in words (CLAUDE.md rule 10).
The breeder answers each slot with one radio pick, stored as `approval.picks["img:<slot>"]`
(outside the record hash, so a pick never un-approves the outline).

**Two passes for a generated image.**

1. **Pass one: the plan.** `scripts/image_candidates.py <slug>` offers each slot the page's
   own images first, then served ones, then the breeder's folder; the board shows them with
   the style ids. The breeder picks `file:/images/…`, `assets:<filename>`, `og:<style>` or
   `ig:IG-<n>`. A bare `og:`/`ig:` pick approves the STYLE, not an image: nothing exists yet.
2. **Generate.** The image is generated per §2–§5 and baked with
   `python3 scripts/ingest_image.py draft <master> --board <slug> --slot <slot> --og-style <X>`
   (or `--infographic IG-<n>`), which writes the final bytes to
   `data/boards/generated/<slug file>/<slot>.webp` (never under `public/`, which ships whole)
   and prints their sha12: the first 12 hex digits of the sha256 of the file.
3. **Pass two: the image.** The board is rebuilt and shows the draft. Approving it stores
   `og:<style>:<sha12>` (or `ig:IG-<n>:<sha12>`), naming the exact bytes the breeder saw.
   Regenerate the file and the pick no longer matches.
4. **Publish.** `python3 scripts/ingest_image.py publish --board <slug> --slot <slot> --stem <seo-stem>`
   refuses unless the pick carries the draft's sha12, then copies the bytes UNCHANGED into
   `public/images/<seo-stem>.webp`, bakes the `-760` sibling beside it, records the manifest
   row, and sets the slot's `assets[]` row `file` and `status: "baked"` (both outside the hash).

Every image slot has its `assets[]` row (slot, kind, w, h, required) planned at boarding;
ingest and publish only fill its `file` and `status`. A slot with no row fails
`image-asset-row-missing` from `boarded` on, so the board refuses it before approval, not the
publish step after it.

**The build refuses an unapproved generated image.** `scripts/image_rules.py` (registered in
`scripts/family_rules.py`) fails the build with `image-generated-unapproved` when a slot's
pick has no sha12 or the served bytes differ from it, `image-generated-not-ingested` when the
approved image is not yet published, and `image-asset-not-ingested` when a picked folder file
was never ingested. A folder file lands at `/images/<asset stem>.webp` by default
(`image_candidates.ingest_target`); any other name must be written into the slot's `assets[]`
row `file`, which `scripts/ingest_image.py folder --board <slug> --slot <slot>` does.

---

## 10. Image-Slot Fields

Each image slot on a board (the hero, every body H2 and every body H3; FAQ-block H3s are
excluded) is an item of `sections[].images[]`, or of a tree node's `images[]` for an H3. The
fields are optional in the schema, so the pages built before this file keep their approvals.
`scripts/image_designs.py` reads the ids from this section.

| Field | Values | Meaning |
|---|---|---|
| `source` | `existing` · `assets-folder` · `generate` · `infographic` | a served image; a file in the breeder's folder; a new generated photo; an infographic |
| `og_style` | `A` · `B` · `C` · `D` · `E` · `H` | the §7 framing style; required when `source` is `generate` |
| `infographic_style` | `IG-1` · `IG-2` · `IG-3` · `IG-4` · `IG-5` | the §8 style; required when `source` is `infographic` |
| `file` | a served path, `/images/…` | required when `source` is `existing` |
| `source_file` | a filename in the breeder's folder | required when `source` is `assets-folder` |
| `prompt` | one sentence | the slot's subject, from its own outline; required when `source` is `generate` |

The pick for a slot, `approval.picks["img:<slot>"]`:

| Pick | Means |
|---|---|
| `file:/images/<path>` | use this served file |
| `assets:<filename>` | use this folder file, ingested first |
| `og:<style>` | generate an OG photo in this style; not yet an approved image |
| `og:<style>:<sha12>` | this generated photo is approved |
| `ig:IG-<n>` | build an infographic in this style; not yet an approved image |
| `ig:IG-<n>:<sha12>` | this generated infographic is approved |

`data/design/image-styles.json` carries the style names and uses for the board's labels; it
is written from §7 and §8 by `python3 scripts/image_designs.py --write`.

*Consumed by:* `.claude/agents/bsuk-image-pipeline.md`, `.claude/agents/bsuk-infographic-builder.md`,
`.claude/skills/image-prompt-generator/SKILL.md`, `.claude/skills/image-metadata/SKILL.md`,
`.claude/skills/bsuk-image-generation/SKILL.md`, `.claude/skills/bsuk-infographic/SKILL.md`,
`.claude/skills/bsuk-photo-ingest/SKILL.md`. On conflict, this file wins.
