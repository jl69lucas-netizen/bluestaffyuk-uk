---
name: bsuk-location-page-builder
description: Use when building or rebuilding any UK city location page at /uk-locations/<slug>/ on BlueStaffyUK — derives the section list from a live competitor scan rather than a fixed template (competitors' section count + 3, via bsuk-query-augmentation), names the kit component and the render check for every section, and fixes the keyword, link, review, FAQ and schema rules for the 28 cities in data/locations.json. Triggers - "location page", "city page", "rebuild <city>", "/uk-locations/<slug>/".
allowed-tools: [Read, Write, Bash]
---

# Location page builder

One page per UK city under `/uk-locations/<slug>/`. The 28 slugs are `data/locations.json`
and nowhere else. This file says how the page is shaped; the packs say how it is written.

## What wins when this file and something else disagree

| Source | It owns |
|---|---|
| `CLAUDE.md` rules 1–16 | voice, branch, commit, outline-first, confidence gate, no fabricated claims (1–10) · reuse every image and video (11, 14) · every link on the board (12) · tables stacked on mobile (13) · **faithful rewrite (15)**: a city page with a migrated body keeps its verbatim set ("Before you write anything", item 4) · **per-page hero and counter, and a refresh delta on every section (16)** |
| `rules/headings.md` | `heading-hierarchy-outline-gate` · `title-case-headings` · `header-style-declared` |
| `rules/copy.md` | `write-from-outline-never-from-sibling` · `first-person-brand-voice` · `entity-4-move-loop` |
| `rules/links.md` | `link-first-anchors` |
| `rules/images.md` | `uniform-inbody-image-sizing` · `read-card-thumb-is-target-hero` |
| `rules/design.md` | the nine visual rules · `layout-hero-counter-separation` · `layout-h3-image-first` |
| `rules/schema.md` | structured data and `no-visible-date` |
| `rules/gates.md` | `confidence-gate-97` · `verify-the-gate-first` |
| `rules/puppies.md` | anything that states a price, a status or a delivery band |
| `docs/reference/location-page-template.md` | structure, FAQ format and tone (this file's fact table wins for facts) |

The packs win. Cite a rule id rather than restating the rule.

## The facts a city page may state

Everything here comes from a file, never from memory:

| Fact | Source |
|---|---|
| Prices £1,500 (Roman, Byrd, Ince) · £1,700 (Vennie, Christa, Cheryl) | `data/puppies.json`, `data/price-matrix.json` |
| £500 refundable deposit | `data/settings.json` → `deposit_gbp`, `deposit_refundable` |
| £200–£350 UK home delivery, priced by distance, by DEFRA-approved transport | `data/settings.json` → `delivery_min_gbp`, `delivery_max_gbp`, `delivery_note` |
| Where we are | `data/settings.json` → `location_label` (Carlisle · Cumbria) |
| Breed lifespan 12–14 years | the Staffordshire Bull Terrier breed figure |
| City, h1, title, description, canonical | `data/locations.json` |
| Reviews | `data/reviews.json` — three real reviews, no others exist |
| home-raised: every puppy is raised in our home, not a kennel | `data/faq.json` → row `about-home-raised` |
| FAQ base set | `data/faq.json` |

Not established, and therefore never written as a fact: a licence, a registration or a
council permission (`LICENCE_CLAIM_PLACEHOLDER`), a statute or by-law
(`LEGAL_CLAIM_PLACEHOLDER`), the guarantee length (`NOT FETCHED` — `guarantee_days: null`),
a named vet or local business, a mileage, a journey time, a delivery date, a local price, a
city-level statistic, a health-test result. The parents' L-2-HGA and HC-HSF4 "clear" results
are `NOT FETCHED` until the certificate is on file (`rules/copy.md`, `entity-4-move-loop`):
`data/quality/evidence-ledger.json` records them as the `parents-dna-clear` claim at proof
`NOT FETCHED`, and `scripts/query_augment.py` blocks, as "unverified fact", any question only
a row making that claim could answer — the breeder's answer is Known Issue 41. A number
nobody fetched is written `NOT FETCHED`.

---

## Step 1 — the competitor scan decides the section list

**There is no fixed section count.** A fixed template produces 28 pages that differ
only in a city name, which is the exact failure `dup-no-sibling-crossover` exists to catch.
The mandatory spine is fixed; the body sections are derived per city.

### Procedure

1. Search the page's primary keyword (the city row's H1 keyword) on Google and on Bing, as
   `/bsuk-query-augmentation` sets out. The three query shapes a buyer also types
   (`staffy puppies for sale <city>`, `blue staffy puppies <city>`,
   `staffordshire bull terrier breeder near <city>`) are an optional free gap scan: they
   supply topics, never the count.
2. Take the top-5 on each engine, merged — **marketplaces and directories included**; only
   off-topic results are dropped. Fewer than three usable pages is a finding, not a blocker:
   record it and derive from what exists.
3. Record nothing by hand. The competitor record is the question file's `competitors` array
   (`url`, `google_pos`, `bing_pos`, `h2_raw`, `h2_clean`, `outlier`, `blocked`), written by
   `/bsuk-query-augmentation`; the board schema (`schemas/board.schema.json`) has no
   competitor block. On the board, a body section that answers a competitor is
   `group: "COMPETITOR-BASED"` and names that competitor's URL in its `why_source` —
   `scripts/pageboard.py` refuses one without a URL. What a buyer asks that no pooled page
   answers is the question file's `extra_sections` with `uncovered: true`.

4. **Set the section count** with `/bsuk-query-augmentation` (it runs this scan with Bing
   included and writes `data/queries/<slug>.json`). The pool is the top-5 Google results
   plus the top-5 Bing results for the primary keyword, merged, **marketplaces and
   directories included** — only off-topic results are dropped. Competitor headings come
   from `python3 scripts/query_augment.py --extract-h2` run on each saved page; advert cards
   and navigation never count, and nobody counts H2s by hand. The page matches the highest
   real count (an outlier over 1.5× the next is recorded and skipped), then adds the three
   `extra_sections` the question pool suggests: the target is that count + 3, and **never
   fewer than 9 body sections**. `section_target.total` is the minimum;
   `scripts/query_coverage_check.py` fails a page below it. Body topics come from what the
   pooled pages cover plus the gaps, minus anything BSUK cannot state from the fact table
   above. Drop a topic rather than pad it with a claim.
   `docs/reference/location-page-template.md` is the full rule and the page's structure.
5. Anything the scan could not supply is written `NOT FETCHED` in the board. Never a guess.

The scan lives in `data/queries/<slug>.json`; the board (`data/boards/<slug>.json`) cites it
section by section and is approved
(`python3 scripts/board_approve.py <slug>`) before a section is written — no page is built
without an approved board, and `python3 scripts/board_gate.py <slug>` refuses otherwise.
The board key is the bare slug: the record is `data/boards/<slug>.json` and
`python3 scripts/board_gate.py <slug>` takes the bare slug (`own_live_key` in
`scripts/pageboard.py` resolves the live route `uk-locations/<slug>` through
`data/page-map.json`). Never key the board `uk-locations/<slug>`: `scripts/board_gate.py`
would look for `data/boards/uk-locations--<slug>.json`.

---

## Step 2 — the page spine

The fixed frame, in the order `docs/reference/location-page-template.md` ("The fixed frame")
sets. Frame parts sit in their own sections and are never counted as body sections. The
derived body sections from step 1 fill the three gaps, split roughly evenly.

**Every section is a `<section data-section-label="…">` directly inside `<main>`** — one per
frame part and one per body section, never nested in another labelled section.
`scripts/query_coverage_check.py` counts body sections by exactly that shape: a labelled
section that holds an H2, is not `#top`, `#key-takeaways` or `#newsletter`, and holds no frame
component (kit hero, counter, trust strip, page nav, review, FAQ block, form). A body H2 in an
unlabelled `<div>`, or inside a frame section, is not counted, and the page falls short of
its `section_target.total`.

| # | Section | Kit component and props | Checks it must satisfy |
|---|---|---|---|
| 1 | Hero — image first | `Hero as="h1"` with the board's picked `layout` · `align` · `media` · `ledge` | `layout-image-box-reserved` · `img-alt-present-and-unique` · `layout-no-horizontal-overflow` |
| 2 | Counter strip | `CounterStrip` — this page's own `stats`, the board's picked `tiles` · `label` | `layout-hero-counter-separation` |
| 3 | Trust strip | `TrustStrip` | `a11y-text-contrast-aa` |
| 4 | Table of contents | `PageNav` | `nav-anchors-resolve` · `nav-jump-target-lands` |
| 5 | Key takeaways, `id="key-takeaways"` | `InfoCard kind="fact"` | `sem-statement-label-visible` |
| 6 | Review — top | `Testimonial mode="single" reviews={…}` | `a11y-text-contrast-aa` · its own section |
| 7 | FAQ — top | `Faq` | `sem-heading-order` · FAQPage schema below |
| — | Body sections (derived, step 1) | `InfoCard` · `PuppyCard` · `SectionDivider` (add `inverse` on a dark band) | `layout-h3-image-first` · `sem-section-opening-paragraph` · `sem-heading-order` · `sem-all-six-levels` |
| 8 | Review — middle | `Testimonial mode="single" reviews={…}` | its own section, never inside a body section |
| 9 | FAQ — middle | `Faq` | `sem-heading-order` · FAQPage schema below |
| — | Body sections (derived, step 1) | `InfoCard` · `PuppyCard` · `SectionDivider` (add `inverse` on a dark band) | `layout-h3-image-first` · `sem-section-opening-paragraph` · `sem-heading-order` · `sem-all-six-levels` |
| 10 | Newsletter, `id="newsletter"` | `InfoCard kind="recommendation" label="Newsletter"` | `layout-tap-target-size` · the only newsletter on the page |
| — | Body sections (derived, step 1) | `InfoCard` · `PuppyCard` · `SectionDivider` (add `inverse` on a dark band) | `layout-h3-image-first` · `sem-section-opening-paragraph` · `sem-heading-order` · `sem-all-six-levels` |
| 11 | Review — bottom | `Testimonial mode="single" reviews={…}` | `a11y-text-contrast-aa` · its own section, never inside a body section |
| 12 | FAQ — bottom | `Faq` | `sem-heading-order` · FAQPage schema below |
| 13 | Enquiry form | `ContactFormKit` | `form-inquiry-contract` · `layout-tap-target-size` |
| — | Footer | `SiteFooterKit` | inherited from `BaseLayout`; never hand-written, not a frame part |

**No `variant` prop and no letter — but the arrangement props are the page's own.** The
letters in `data/design/picks.json` are a record of project 3's component picks, never a prop:
project 3's prune (design-system spec §11 amendment 4) deleted every losing variant and every
`variant` prop, and handing a letter to a component is a build error. What a component DOES
take is its per-page arrangement, read from the page's approved board with
`const pick = pickedStyle(record, '<section id>')` (`src/lib/pickedStyle.ts`), exactly as the
rebuilt pages do (`src/pages/blue-staffy-health-uk/index.astro`): the hero's
`layout={pick.layout.hero}` (the style's `hero` axis — there is no `pick.layout.layout`),
`align={pick.layout.align}`, `media={pick.layout.media}` and `ledge={pick.layout.ledge}`; the
counter's `tiles={pick.layout.tiles}` and `label={pick.layout.label}`. Rule 16 gives every
page its own three hero and three counter styles on its board; never copy a sibling city's
pick. Reviews keep a board pick but never a grid: a review section is a kit shape, so the
board schema makes it offer `S1`/`S2`/`S3` like every kit section, and `S2` and `S3` are
grids. A city board picks `S1` ("One review given room") for every review section, and every
city review slot is `Testimonial mode="single"` (see Reviews), never `mode={pick.layout.mode}`.

The props a city page passes, as `src/components/kit/*.astro` declares them:

| Component | Props |
|---|---|
| `Hero` | `title`, `eyebrow`, `lede`, `image` (required — there is no default photo; `imageAlt` with it) and `as` (`h1` · `h2`; a location page's hero is the page's H1, so `as="h1"`), and the arrangement from the board pick: `layout` (`split` · `stacked` · `mosaic` · `panel` · `bleed`), `align` (`left` · `center`), `media` (`none` · `left` · `right` · `top`), `ledge` (`none` · `chips` · `stats` · `aside` · `ticks`). When `image` is a `/images/…` path string, also pass `imageWidth`, `imageHeight` and `imageSrcset` — `img_dims` and `img-srcset-within-2x` are blocking |
| `CounterStrip` | `stats` (required: `[{n, label, source?}]` — this page's own facts, rule 16), `tiles` and `label` (from the board pick) |
| `TrustStrip` | `items` (`[{t, d, i}]`) |
| `PageNav` | `sections` (`[{id, label}]`, one per H2, each id real) |
| `Faq` | `items` (`[{id, q, a, source}]`, the `FaqRow` shape in `src/lib/faq.ts`). **Always pass the block's picks**: without `items` it renders the WHOLE bank. `q` is the question as written on the page (the `covered_by.text`), `a` is the bank row's answer or the settings-key fact, `source` what backs it |
| `PuppyCard` | `slug` (a row of `data/puppies.json`) |
| `Testimonial` | `mode` (`single` · `grid`, default `single`) and `reviews` — the rows for THIS slot, from `data/reviews.json`. A city page passes `mode="single"` and one row per slot (see Reviews) |
| `InfoCard` | `kind` (`fact` · `observed` · `recommendation`, the whole vocabulary in `src/lib/statement.ts`), `label` to override the default word, `heading` and `body`. Omitted, `heading` and `body` fall back to a health-test card — the newsletter card must pass both |
| `SectionDivider` | `inverse` — set it when the divider sits on a dark band |
| `Button` | `kind` (`primary` · `outline` · `inverse` · `submit` · `text`, default `primary`) and `label` |
| `ContactFormKit` | `idPrefix` only when a page carries two forms |

`InfoCard kind="note"` **does not exist**: `sem-statement-label-visible` accepts exactly the
three kinds above and treats anything else as a defect. A newsletter block is a
`recommendation` with an explicit `label` ("Newsletter"), which keeps the label visible and
the check silent.

**Hero.** The image comes before the copy, and its box is reserved so nothing reflows under
it: 390–450px tall on desktop (the 400px band of `rules/design.md` rule 9), `auto` on
mobile. Hero and counter strip never share one continuous background — a tone shift **and** a
1px rule at minimum (`layout-hero-counter-separation`).

**Reviews.** `data/reviews.json` holds three, so top / middle / bottom is those three, one per
slot, each `Testimonial mode="single" reviews={[row]}` — the bottom slot included. A `grid`
at the bottom would repeat the two rows already shown above it, so a city page never uses
one. A review is never written, never re-attributed to another city,
and a slot with nothing real in it carries the placeholder the component already emits
(`scripts/placeholder_check.py` counts it) rather than invented praise. Each review sits in
its own section, never inside a body section.

**Newsletter.** One block per location page, frame part 10 (`id="newsletter"`); there is
never a second, and no other element takes that id. It says what a subscriber gets and
nothing about how many subscribers there are.

**Contact form.** `ContactFormKit` only — never a hand-rolled form. The contract is asserted
by `form-inquiry-contract`, and `PUBLIC_FORMSPREE_ID` is unset until project 6.

**Tap targets.** Every control, jump link and accordion summary is at least 44px
(`layout-tap-target-size`). Every `PageNav` entry resolves to a real id and lands on the
heading rather than past it (`nav-jump-target-lands`).

---

## Step 3 — keywords and entities

**Primary keyword** is the city row's `h1`, already in the UK city pattern
`Blue Staffy Puppies <City> UK` / `Staffy Puppies for Sale <City>`. Never rewrite it here;
`data/locations.json` is generated.

**Variation, so 28 siblings do not read as one page.** Each page takes its long-tail set
from its own outline and its own competitor gaps:

- transactional — `buy staffy puppy <city>`, `blue staffy puppies available <city>`
- conversational — `where to find a staffy breeder near <city>`
- logistics — `staffy puppy delivered to <city>`, `collection or delivery <city>`
- comparison — `blue staffy vs blue brindle`, `kc registered vs unregistered`
- LSI / entity — Staffordshire Bull Terrier, blue coat dilution, L-2-HGA, HC-HSF4, early
  socialisation, home-reared, refundable deposit

**Rule: write from the outline, never from a sibling** (`CLAUDE.md` rule 8). Reuse
components, CSS and structure freely; never open another city's page to reword a paragraph.
A page copied and then reworded passes `dup-no-sibling-crossover` and still breaks the rule.

**Query augmentation (before writing).** Run `/bsuk-query-augmentation <slug> location
"<primary keyword>" /uk-locations/<slug>/` before the outline. Its question file decides the
FAQ picks, the three extra sections and the section target; answer every `must_answer`
question on the page and record where in `covered_by`. When the page is rebuilt, add its
bare slug (the route's last segment, e.g. `blue-staffy-puppies-manchester-uk`) to
`data/facts/rebuilt.json` — the key the other gates use — and only then does
`npm run check:queries` hold the page; until then it is skipped as awaiting rebuild.

**One key per city page.** The facts, link-parity and verbatim gates and pageboard key a city
page by its bare slug and find it at `dist/uk-locations/<slug>/index.html` through
`data/page-map.json` (`scripts/_slugs.py`). The query gate finds the same page through the
route in its question file, `data/queries/<slug>.json` (that route must end in `/<slug>/`), and
accepts the bare slug in `data/facts/rebuilt.json`. So one `data/facts/rebuilt.json` entry
covers every gate. Add a city's slug there only once its rebuilt page is built —
`[slug].astro` builds all 28 routes, so a slug listed early is judged against the old migrated
page.

**Links.** Anchors start the sentence, never trail it (`link-first-anchors`). Vary anchor
text across the page — exact, partial and descriptive — and never `click here`. Internal
targets are the real routes in the "Links" list of `docs/reference/location-page-template.md`:
`/available-puppies/` and its puppy pages, the buy pages (`/buy-blue-staffy-puppies-uk/`,
`/buy-staffy-puppies-for-sale-uk/`, `/blue-staffy-pup-sale-uk/`), the buying guide, the breed
guide, health, the breeder story, contact, the homepage, the blog hub and its posts, and 3–5
nearby city pages. There is no delivery page and no pricing page: those facts are stated on
the page itself. External links go only to URLs in `docs/reference/external-link-library.md`
(breed and health authorities, gov.uk for law topics); never to a competitor, a marketplace,
or a local business.

**UK geography.** The nearby-city cluster is the other rows of `data/locations.json`, picked
by real proximity to the target city. Distance and delivery are expressed only as
`settings.delivery_min_gbp`–`settings.delivery_max_gbp` by distance,
by DEFRA-approved transport, or as collection from `settings.location_label`.
Never a mileage, never a drive time, never a delivery date.

---

## Step 4 — schema

Per `rules/schema.md`, enforced by `python3 scripts/schema_check.py`:

- **LocalBusiness** — name, `address` and geo from `data/settings.json`, `priceRange`,
  `openingHours`, `sameAs` from `socials`, and `areaServed` naming the target city.
  **No `telephone` key while `settings.phone` is `PHONE_PLACEHOLDER`**: an unresolved
  placeholder in schema is worse than an absent property.
- **Product** — only where the page shows a puppy. One offer per product node
  (`schema-single-product-offer`); `availability` is `InStock` only for a pup
  `data/puppies.json` marks Available, and a sold pup is `SoldOut`
  (`schema-sold-not-instock`).
- **FAQPage** — one node, carrying every visible Q&A and nothing that is not visible.
- `dateModified` is present in schema and never rendered as visible text
  (`schema-date-modified-present`, `schema-no-visible-date`).
- Every `@id` a node references is defined by a real node on the page.

---

## Step 5 — FAQ

Three `Faq` blocks — **top** (5–7: price, deposit, delivery to this city, reserving),
**middle** (5–7: paperwork, health testing, visiting, age at collection) and **bottom**
(7–10: flats, children and other pets, training, lifespan, coat) — carrying exactly the
questions `data/queries/<slug>.json` picked for each block, 17–20 in practice. Picks come
only from the question file: to change one, change the data (a bank row in `data/faq.json`,
a settings key, a real sourced question) and rebuild the file — never swap, add or drop a
pick by hand. A question may name the city ("Do You Deliver Staffy Puppies to Manchester?")
only if its meaning and its fact are unchanged; record the wording used on the page in
`covered_by.text`. Each question renders as an H3 with a short, direct answer drawn only from its fact: the
`a` of the `bank:<id>` row named in the question's `found_in`, or the data key its
`fact_source` names (`data/settings.json#deposit_gbp`) — never from the whole page file a
`fact_source` path may point at, and never from a bank row whose answer makes a `NOT FETCHED`
ledger claim (`parents-dna-clear`), even when `found_in` names it. Links sit inside answers, anchor first. An answer that
introduces a new fact is a fabricated claim with extra steps. FAQPage schema carries exactly
the visible questions, no visible date. `scripts/query_coverage_check.py` holds all of this.

---

## Step 6 — gates

Build first (`npm run build` — the gates measure `dist/`), then, in order:

```bash
npm run check:all
python3 scripts/board_gate.py <slug>
python3 scripts/final_page_audit.py uk-locations/<slug> --type location
python3 scripts/dup_content_audit.py
python3 scripts/aeo_audit.py uk-locations/<slug>
python3 scripts/evidence_audit.py uk-locations/<slug> --type location
npm run test:render:meta
npm run test:render:pages
```

`test:render:meta` is the gate that checks the checkers — run it before trusting any page
result. A gate's output is a hypothesis about the page: confirm a reported defect on the
built page before editing anything, and read a PASS's examined count before believing it
(`rules/gates.md`, `.claude/skills/bsuk-gate-integrity/SKILL.md`). The page audits take
the page's route as the slug (`uk-locations/<slug>`): with no slug,
`scripts/final_page_audit.py` audits the flat pages and never a city page,
`scripts/evidence_audit.py` matches 0 pages and exits 1, and `scripts/aeo_audit.py` refuses.
`scripts/dup_content_audit.py` is site-wide by design. Every one exits 1 on a FAIL or ERROR;
`--fail-on-error` also fails the AEO and evidence audits on a WARN, and `--json` writes the
result under `docs/reports/`.

---

## Worked example — `uk-locations/blue-staffy-puppies-manchester-uk`

That row is a five-word stub today, carrying `"robots": "noindex, follow"` and
`"defects": ["stub"]`. Its H1 is `Blue Staffy Puppies Manchester UK` and its canonical is
`/uk-locations/blue-staffy-puppies-manchester-uk/` — both taken from the row, never
rewritten here.

**Question file: `data/queries/blue-staffy-puppies-manchester-uk.json`.** Every pooled page
was a marketplace or directory, and the build's cleaning left none of them a body H2 (one was
a challenge page, recorded as blocked), so `section_target.total` is the floor, 9; the three
`extra_sections` are temperament, paperwork and health. Nothing below is an approved outline;
it is the shape the list takes from that file, in the frame order of step 2: nine body
sections, three in each gap.

| # | Section | Where it comes from |
|---|---|---|
| 1 | Hero — Blue Staffy Puppies Manchester UK | row `h1`; `Hero`, arranged by this page's own board pick (rule 16) |
| 2 | Counter strip — this page's own figures, chosen on its board from its facts, never a set a sibling city shares | `CounterStrip`, `tiles` and `label` from this page's board pick (rule 16) |
| 3 | Trust strip | `TrustStrip` |
| 4 | On This Page | `PageNav`, one entry per H2 below |
| 5 | Key Takeaways | `InfoCard kind="fact"` |
| 6 | Review — top | one row of `data/reviews.json`; `Testimonial mode="single"` |
| 7 | FAQ — top | the `top` picks in `data/queries/blue-staffy-puppies-manchester-uk.json`; `Faq` |
| 8 | Our Litter and What Each Puppy Costs | `data/puppies.json`; `PuppyCard` |
| 9 | Getting Your Puppy to Manchester | `settings.delivery_*`, or collection from `settings.location_label` |
| 10 | Reserving a Puppy With a £500 Refundable Deposit | `settings.deposit_gbp`, `settings.deposit_refundable` |
| 11 | Review — middle | a second row of `data/reviews.json`; `Testimonial mode="single"` |
| 12 | FAQ — middle | the `middle` picks in `data/queries/blue-staffy-puppies-manchester-uk.json`; `Faq` |
| 13 | Raised in Our Home, Not a Kennel | `rules/copy.md` evidence loop |
| 14 | Visiting Us in Carlisle Before You Decide | `data/faq.json` → row `contact-visit`; visits by appointment only |
| 15 | Cities Near Manchester We Deliver To | sibling rows of `data/locations.json` |
| 16 | Newsletter | `InfoCard kind="recommendation" label="Newsletter"` |
| 17 | Extra section (question pool) | `extra_sections[0]` in `data/queries/blue-staffy-puppies-manchester-uk.json` |
| 18 | Extra section (question pool) | `extra_sections[1]` in `data/queries/blue-staffy-puppies-manchester-uk.json` |
| 19 | Extra section (question pool) | `extra_sections[2]` in `data/queries/blue-staffy-puppies-manchester-uk.json` |
| 20 | Review — bottom | the third row of `data/reviews.json`; `Testimonial mode="single"` |
| 21 | FAQ — bottom | the `bottom` picks in `data/queries/blue-staffy-puppies-manchester-uk.json`; `Faq` |
| 22 | Ask Us About a Puppy | `ContactFormKit` |

Word-count target: `NOT FETCHED` until the scan gives a competitor median. Never pick a
number first and write to fill it.

**What this page may not say**, whatever the scan finds on a competitor: a Manchester vet or
kennel by name, a council licence, a by-law, a mileage or drive time, a delivery date, a
Manchester-specific price, or a review from a Manchester buyer that is not already in
`data/reviews.json`.

---

## Before you write anything

1. Read the row in `data/locations.json`, then `data/settings.json`, `data/puppies.json`,
   `data/reviews.json`, `data/faq.json`, `data/design/picks.json`.
2. Run `/bsuk-query-augmentation` for the slug (competitor scan, questions, FAQ picks, section
   target). The board cites that question file; it has no competitor block of its own
   (step 1, item 3).
3. Produce the outline — H1→H6 tree, the derived section list with its derivation, keyword
   distribution, review and newsletter positions, FAQ list, schema plan — and get it
   approved (`rules/headings.md` outline gate, `CLAUDE.md` rule 5).
4. Before rewriting a page that already exists, extract what the rebuild must keep:
   `python3 scripts/facts_preserved_check.py --extract <key>` (its facts into
   `data/facts/<key>.json`) and, where rule 15 applies (the page is in
   `data/verbatim/applies.json`), `python3 scripts/verbatim_set_check.py --extract <key>`
   (its verbatim set into `data/verbatim/<key>.json`). The facts extract reads the built
   migrated page (`dist/uk-locations/<slug>/index.html`); the verbatim extract reads the city's
   row of `data/locations.json` at the frozen migration commit. `<key>` is the page's bare slug,
   a city page included (`blue-staffy-health-uk`, `blue-staffy-puppies-manchester-uk`). Run
   these extracts FIRST, before any rewrite, while `dist/` still holds the migrated page: the
   facts extraction cannot be redone afterwards. Never start a city rewrite without them.
5. Approve the board, then build. Once the rebuilt page is built, add its bare slug to
   `data/facts/rebuilt.json`.
6. Below 97% confidence: write what is not blocked, log the question to the brief's
   `## Open Flags`, ask exactly one narrow question, keep going. Never dead-stop.
