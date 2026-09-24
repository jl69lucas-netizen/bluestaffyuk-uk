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
| `CLAUDE.md` judgment rules 1–10 | voice, branch, commit, outline-first, confidence gate, no fabricated claims |
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
city-level statistic. A number nobody fetched is written `NOT FETCHED`.

---

## Step 1 — the competitor scan decides the section list

**There is no fixed section count.** A 22-section template produces 28 pages that differ
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
3. For each, record in the board's competitor block:

   | Field | What to record |
   |---|---|
   | url | the page |
   | sections | its H2 list, verbatim |
   | headings | the H3s under its two longest H2s |
   | words | body word count |
   | faqs | the questions it answers |
   | schema | the `@type`s in its JSON-LD |
   | gaps | what a buyer asks that the page never answers |

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

The scan output goes into `data/boards/<slug>.json` and the board is approved
(`python3 scripts/board_approve.py <slug>`) before a section is written — no page is built
without an approved board, and `python3 scripts/board_gate.py <slug>` refuses otherwise.

---

## Step 2 — the page spine

The fixed frame, in the order `docs/reference/location-page-template.md` ("The fixed frame")
sets. Frame parts sit in their own sections and are never counted as body sections. The
derived body sections from step 1 fill the three gaps, split roughly evenly.

| # | Section | Kit component and props | Checks it must satisfy |
|---|---|---|---|
| 1 | Hero — image first | `Hero as="h1"` | `layout-image-box-reserved` · `img-alt-present-and-unique` · `layout-no-horizontal-overflow` |
| 2 | Counter strip | `CounterStrip` | `layout-hero-counter-separation` |
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
| 11 | Review — bottom | `Testimonial mode="grid" reviews={…}` | `a11y-text-contrast-aa` · its own section |
| 12 | FAQ — bottom | `Faq` | `sem-heading-order` · FAQPage schema below |
| 13 | Enquiry form | `ContactFormKit` | `form-inquiry-contract` · `layout-tap-target-size` |
| — | Footer | `SiteFooterKit` | inherited from `BaseLayout`; never hand-written, not a frame part |

**The letters in `data/design/picks.json` are a record, never a prop.** Project 3's prune
(design-system spec §11 amendment 4) deleted every losing variant and every `variant` prop:
a kit component renders the breeder's picked design and takes no letter. Reading a letter out
of that file and handing it to a component is a build error.

The props a city page passes, as `src/components/kit/*.astro` declares them:

| Component | Props |
|---|---|
| `Hero` | `title`, `eyebrow`, `lede`, `image` (required — there is no default photo; `imageAlt` with it) and `as` (`h1` · `h2`; a location page's hero is the page's H1, so `as="h1"`). When `image` is a `/images/…` path string, also pass `imageWidth`, `imageHeight` and `imageSrcset` — `img_dims` and `img-srcset-within-2x` are blocking |
| `CounterStrip` | `stats` (required: `[{n, label, source?}]`), `tiles`, `label` |
| `TrustStrip` | `items` (`[{t, d, i}]`) |
| `PageNav` | `sections` (`[{id, label}]`, one per H2, each id real) |
| `Faq` | `items` (`[{id, q, a, source}]`, the `FaqRow` shape in `src/lib/faq.ts`). **Always pass the block's picks**: without `items` it renders the WHOLE bank. `q` is the question as written on the page (the `covered_by.text`), `a` is the bank row's answer or the settings-key fact, `source` what backs it |
| `PuppyCard` | `slug` (a row of `data/puppies.json`) |
| `Testimonial` | `mode` (`single` · `grid`, default `single`) and `reviews` — pass this page's rows from `data/reviews.json` so none is silently dropped |
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

**Reviews.** `data/reviews.json` holds three. Top / middle / bottom therefore means those
three, one per slot, or a single quote given room; a grid is used only where the page really
has that many real reviews. A review is never written, never re-attributed to another city,
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

**STOP — nested routes first.** Before the first city page goes into `data/facts/rebuilt.json`,
the facts, link-parity and verbatim gates and pageboard's live key must resolve nested routes
(`uk-locations/<slug>`) — a Project 5 prerequisite (see `docs/reference/session-log.md` Known
Issue 39). Until then do not add a city page to `data/facts/rebuilt.json`.

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
`fact_source` path may point at. Links sit inside answers, anchor first. An answer that
introduces a new fact is a fabricated claim with extra steps. FAQPage schema carries exactly
the visible questions, no visible date. `scripts/query_coverage_check.py` holds all of this.

---

## Step 6 — gates

Build first (`npm run build` — the gates measure `dist/`), then, in order:

```bash
npm run check:all
python3 scripts/board_gate.py <slug>
python3 scripts/final_page_audit.py
python3 scripts/dup_content_audit.py
python3 scripts/aeo_audit.py
python3 scripts/evidence_audit.py
npm run test:render:meta
npm run test:render:pages
```

`test:render:meta` is the gate that checks the checkers — run it before trusting any page
result. A gate's output is a hypothesis about the page: confirm a reported defect on the
built page before editing anything, and read a PASS's examined count before believing it
(`rules/gates.md`, `.claude/skills/bsuk-gate-integrity/SKILL.md`). The page audits report
only by default; `--fail-on-error` makes them exit non-zero and `--json` writes the result
under `docs/reports/`.

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
| 1 | Hero — Blue Staffy Puppies Manchester UK | row `h1`; `Hero` c |
| 2 | Counter strip — pups available · £500 refundable · £200–£350 delivery | `CounterStrip` d |
| 3 | Trust strip | `TrustStrip` d |
| 4 | On This Page | `PageNav` c, one entry per H2 below |
| 5 | Key Takeaways | `InfoCard` b, `kind="fact"` |
| 6 | Review — top | `data/reviews.json` |
| 7 | FAQ — top | the `top` picks in `data/queries/blue-staffy-puppies-manchester-uk.json`; `Faq` c |
| 8 | Our Litter and What Each Puppy Costs | `data/puppies.json`; `PuppyCard` c |
| 9 | Getting Your Puppy to Manchester | `settings.delivery_*`, or collection from `settings.location_label` |
| 10 | Reserving a Puppy With a £500 Refundable Deposit | `settings.deposit_gbp`, `settings.deposit_refundable` |
| 11 | Review — middle | `data/reviews.json` |
| 12 | FAQ — middle | the `middle` picks in `data/queries/blue-staffy-puppies-manchester-uk.json`; `Faq` c |
| 13 | Raised in Our Home, Not a Kennel | `rules/copy.md` evidence loop |
| 14 | Visiting Us in Carlisle Before You Decide | `data/faq.json` → row `contact-visit`; visits by appointment only |
| 15 | Cities Near Manchester We Deliver To | sibling rows of `data/locations.json` |
| 16 | Newsletter | `InfoCard` b, `kind="recommendation"`, `label="Newsletter"` |
| 17 | Extra section (question pool) | `extra_sections[0]` in `data/queries/blue-staffy-puppies-manchester-uk.json` |
| 18 | Extra section (question pool) | `extra_sections[1]` in `data/queries/blue-staffy-puppies-manchester-uk.json` |
| 19 | Extra section (question pool) | `extra_sections[2]` in `data/queries/blue-staffy-puppies-manchester-uk.json` |
| 20 | Review — bottom | `data/reviews.json` |
| 21 | FAQ — bottom | the `bottom` picks in `data/queries/blue-staffy-puppies-manchester-uk.json`; `Faq` c |
| 22 | Ask Us About a Puppy | `ContactFormKit` c |

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
   target), and record the competitor block and section target in the board.
3. Produce the outline — H1→H6 tree, the derived section list with its derivation, keyword
   distribution, review and newsletter positions, FAQ list, schema plan — and get it
   approved (`rules/headings.md` outline gate, `CLAUDE.md` rule 5).
4. Before rewriting a page that already exists, extract what the rebuild must keep:
   `python3 scripts/facts_preserved_check.py --extract <key>` (its facts into
   `data/facts/<key>.json`) and, where rule 15 applies (the page is in
   `data/verbatim/applies.json`), `python3 scripts/verbatim_set_check.py --extract <key>`
   (its verbatim set into `data/verbatim/<key>.json`). Both read the built migrated page.
   `<key>` is the page's bare slug (the bare slug for a top-level page, e.g.
   `blue-staffy-health-uk`). For a city page (`uk-locations/<slug>`) this step is held by the
   same STOP rule — `scripts/facts_preserved_check.py` and `scripts/verbatim_set_check.py`
   cannot yet read or write nested routes (see `docs/reference/session-log.md` Known Issue 39).
   Once Project 5 fixes that, run these extracts FIRST, before any
   rewrite, while `dist/` still holds the migrated page: the extraction cannot be redone
   afterwards. Never start a city rewrite without them.
5. Approve the board, then build. Add the page to `data/facts/rebuilt.json` only once the
   nested-route STOP rule above is cleared.
6. Below 97% confidence: write what is not blocked, log the question to the brief's
   `## Open Flags`, ask exactly one narrow question, keep going. Never dead-stop.

## Keyword variants — the four extra keyword types (system-gaps, 2026-09-24)

A new location, comparison or blog board carries four keyword types beyond the nine the
brief names: `variation`, `related`, `cooccurring` and `similar`, each a list in a section's
`keywords`. The page needs at least one term of each type SOMEWHERE — not in every section.
The `keyword-variants-missing` check in `scripts/family_rules.py` warns on a draft and fails
from `boarded` on. The twelve pages built before this rule are never asked.

Where the terms come from: after the query augmentation has cached its files and before the
outline is boarded, run `python3 scripts/keyword_variants.py <slug>`. It reads the cached
files under `data/queries/` only (no paid call) and proposes each list with the source of
every term: variations are spellings of the head term the cached text actually uses, related
terms are the search engine's related-searches box, co-occurring terms are phrases found in
two or more cached documents, and similar terms are how the ranking pages word the same
query. Put each term in the section where it reads naturally; drop a term that reads badly
anywhere rather than force it. Exit 6 means nothing is cached for the slug yet: run
bsuk-query-augmentation first. The board's block 4 shows every term as a chip grouped by
type, with the sections that use it.

## Build from the approved outline (system-gaps)

The user's ruling of 2026-09-24: build from the outline, never from crossovers, siblings or
duplicates. `rules/copy.md` `write-from-outline-never-from-sibling` is the method and
`outline-provenance-gate` is the gate that checks what the method leaves behind. Both bind
every city page this skill builds.

1. Write each body section from the approved board record, `data/boards/<slug>.json`, and
   from nothing else. The section's H2 is its `heading`; its H3s are its `tree` nodes, in
   record order, word for word (the build may title-case them). The copy answers the
   section's `intent` inside its `words` band.
2. Never open another city's page, board or built HTML for wording. The only text a sibling
   may share is the whitelist in `scripts/dup_content_audit.py`; a sentence that differs from
   a sibling's only by the city name is a copy, and the gate fails it.
3. A heading the tree does not carry, including an info card's H3, goes back to the board:
   add it to the tree and re-approve, then build. Never add one at build time.
4. The H4-H6 ladder is written at build time. Each ladder heading is new to this page and to
   the site.
5. After `npm run build`, run `python3 scripts/outline_provenance_check.py <slug>` on this
   city page and fix every FAIL in the copy, never by widening the whitelist. Only then add the
   city page to `data/facts/rebuilt.json`; from that point `npm run check:all` re-runs the gate on
   it with every other listed new-family page. The check ids it prints (`outline-extra`,
   `outline-missing`, `outline-order`, `outline-unknown-section`, `outline-duplicate-heading`,
   `outline-heading-crossover`, `outline-copy-crossover`, `outline-sentence-crossover`,
   `outline-unapproved`, `outline-not-found`) are listed in the script's docstring.

## Project 5 page rules (system-gaps)

These bind every location, comparison and blog-post page built from 2026-09-24 on. The
board refuses the record until each holds (`scripts/family_rules.py`); none of them applies
to the twelve pages built before.

1. **Keywords.** Run `python3 scripts/keyword_variants.py <slug>` (add `--also <cache dir>`
   when a registry folder holds the page's SERP) and write its proposals into the sections'
   `keywords.variation`, `related`, `cooccurring` and `similar`, keeping only terms the
   section really uses. An empty type fails `keyword-variants-missing` from `boarded` on.
2. **Entities.** Run `python3 scripts/ontology_seed.py --check`. Every entity a section names
   is in `data/bsuk-ontology.json` with a source; a health result stays PROPOSED until the
   evidence ledger holds it. The board shows them by class.
3. **External links.** At least six on six domains from four source types (gov, registry,
   vet-charity, welfare, research, local — `other` does not count toward the four), all rows
   of `docs/reference/external-link-library.md` (`external-links-six-diverse`). A location page
   adds its own council's dog or animal-licensing page as a `local` row, after
   `curl -sIL <url>` returns 200, dated in the Verified column.
4. **Anchors.** Every internal and external link carries `anchor_type` (exact, partial, lsi,
   natural, branded, naked-url): three or more internal types with at most two exact, three
   or more external types (`anchor-type-variation`), and never an in-copy internal anchor
   another board already uses for the same route (nav tiles excepted)
   (`anchor-reuse-sitewide`).
5. **Images.** Run `python3 scripts/image_candidates.py <slug> --write`. The hero and every
   body H2 and body H3 (FAQ blocks excepted) carry an image slot (`image-slot-missing`),
   filled in this order: the page's own migrated image, another served image, a file from
   the breeder's `Assets/Images/` folder (outside git; `BSUK_ASSETS_DIR` overrides) ingested
   with `python3 scripts/ingest_image.py folder`. When none fits,
   the slot is `source: generate` with an OG style, or `source: infographic` with an IG style,
   named in `IMAGE-DESIGNS.md`. The generated file is drafted with
   `python3 scripts/ingest_image.py draft`, approved on a second pass of the board by its
   sha12 pick, and only then published with `python3 scripts/ingest_image.py publish`
   (`image-generated-unapproved`). Every image slot has its `assets[]` row (slot, kind, w,
   h, required) planned at boarding; ingest and publish only fill its `file` and `status`.
   A slot without one fails `image-asset-row-missing`.
6. **Board and approval.** The board's block 7b lists every rule above for this page,
   evaluated as approval will see it; `scripts/board_approve.py` refuses the approval, and
   any re-approval, while one of them FAILs. The build-gate image checks are listed but never
   block approval: they can only pass after the image is approved and published.
7. **Routes.** A page whose route is not its bare slug (a city page under `/uk-locations/`,
   a post under the blog hub) has its row in `data/page-map.json` before it is built; without
   it `check:outline` looks for `dist/<slug>/` and reports `outline-not-found`.
8. **After the build,** `npm run -s check:outline` (also in `check:all`) must report the page
   examined with 0 problems.
