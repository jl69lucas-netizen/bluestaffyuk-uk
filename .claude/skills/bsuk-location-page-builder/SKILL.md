---
name: bsuk-location-page-builder
description: Use when building or rebuilding any UK city location page at /uk-locations/<slug>/ on BlueStaffyUK — derives the section list from a live competitor scan rather than a fixed template, names the kit component and the render check for every section, and fixes the keyword, link, review, FAQ and schema rules for the 28 cities in data/locations.json. Triggers - "location page", "city page", "rebuild <city>", "/uk-locations/<slug>/".
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

1. Search, for the target city, the three query shapes a buyer actually types:
   `staffy puppies for sale <city>`, `blue staffy puppies <city>`,
   `staffordshire bull terrier breeder near <city>`.
2. Take the **3–5 ranking pages that are breeder or location pages**, not marketplaces and
   not directory listings. Fewer than three usable results is a finding, not a blocker:
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

4. **Derive the section list**: the union of topics two or more of them cover, plus every
   gap, minus anything BSUK cannot state from the fact table above. A typical result is
   9–14 body sections. Drop a topic rather than pad it with a claim.
5. Anything the scan could not supply is written `NOT FETCHED` in the board. Never a guess.

The scan output goes into `data/boards/<slug>.json` and the board is approved
(`python3 scripts/board_approve.py <slug>`) before a section is written — no page is built
without an approved board, and `python3 scripts/board_gate.py <slug>` refuses otherwise.

---

## Step 2 — the page spine

Mandatory, in this order. Everything between **Key takeaways** and **FAQ** is the derived
body from step 1.

| # | Section | Kit component (picked variant) | Checks it must satisfy |
|---|---|---|---|
| 1 | Hero — image first | `Hero` variant `c` | `layout-image-box-reserved` · `img-alt-present-and-unique` · `layout-no-horizontal-overflow` |
| 2 | Counter strip | `CounterStrip` variant `d` | `layout-hero-counter-separation` |
| 3 | Trust strip | `TrustStrip` variant `d` | `a11y-text-contrast-aa` |
| 4 | Table of contents | `PageNav` variant `c` | `nav-anchors-resolve` · `nav-jump-target-lands` |
| 5 | Key takeaways | `InfoCard` variant `b`, `kind="fact"` | `sem-statement-label-visible` |
| 6 | Review — top | `Testimonial` variant `b` | `a11y-text-contrast-aa` |
| 7…n | Derived body sections | `InfoCard` · `PuppyCard` variant `c` · `SectionDivider` variant `a` | `layout-h3-image-first` · `sem-section-opening-paragraph` · `sem-heading-order` · `sem-all-six-levels` |
| — | Review — middle | `Testimonial` variant `b` | inside the body run, never two testimonials in a row |
| — | Newsletter block | `InfoCard` variant `b`, `kind="note"` | `layout-tap-target-size` |
| n+1 | Review — bottom | `Testimonial` variant `b` | `a11y-text-contrast-aa` |
| n+2 | Contact form | `ContactFormKit` variant `c` | `form-inquiry-contract` · `layout-tap-target-size` |
| n+3 | FAQ | `Faq` variant `c` | `sem-heading-order` · FAQPage schema below |
| n+4 | Footer | `SiteFooterKit` variant `a` | inherited from `BaseLayout`; never hand-written |

Variants come from `data/design/picks.json` — the breeder's picks, not a choice made here.

**Hero.** The image comes before the copy, and its box is reserved so nothing reflows under
it: 390–450px tall on desktop (the 400px band of `rules/design.md` rule 9), `auto` on
mobile. Hero and counter strip never share one continuous background — a tone shift **and** a
1px rule at minimum (`layout-hero-counter-separation`).

**Reviews.** `data/reviews.json` holds three. Top / middle / bottom therefore means those
three, one per slot, or a single quote given room; a grid is used only where the page really
has that many real reviews. A review is never written, never re-attributed to another city,
and a slot with nothing real in it carries the placeholder the component already emits
(`scripts/placeholder_check.py` counts it) rather than invented praise.

**Newsletter.** One block mid-page; a second above the footer only on a page past ~2,000
words. It says what a subscriber gets and nothing about how many subscribers there are.

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

**Query augmentation (before writing).** Expand the primary keyword into the questions and
entities an AI answer engine assembles when someone asks about buying a Staffy near that
city: what it costs, whether delivery reaches there, what paperwork comes with the puppy,
how old the puppy is at collection, what the breed is like in a flat, what health testing
the parents had. Write each as a question, answer it on the page in its own sentence, and
mirror the strongest six into the FAQ. There is **no dedicated query-augmentation skill in
this repo yet** — this paragraph is the whole procedure until one exists.

**Links.** Anchors start the sentence, never trail it (`link-first-anchors`). Vary anchor
text across the page — exact, partial and descriptive — and never `click here`. Internal
targets: the buy page, the available puppies, the breed guide, delivery, the comparison
page, contact, and 3–5 nearby city pages. External links go to breed and health authorities
only; never to a competitor, a marketplace, or a page naming a local business BSUK has not
verified.

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

`data/faq.json` supplies the base questions. Add city-specific Q&A only where the page's own
copy already backs the answer — an FAQ answer that introduces a new fact is a fabricated
claim with extra steps. Six to ten questions total, `Faq` variant `c`, mirrored into FAQPage
schema, no visible date.

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

**Competitor scan: `NOT FETCHED`.** Nothing below is an approved outline; it is the shape a
derived list takes once step 1 has actually run.

| # | Section | Where it comes from |
|---|---|---|
| 1 | Hero — Blue Staffy Puppies Manchester UK | row `h1`; `Hero` c |
| 2 | Counter strip — pups available · £500 refundable · £200–£350 delivery | `CounterStrip` d |
| 3 | Trust strip | `TrustStrip` d |
| 4 | On This Page | `PageNav` c, one entry per H2 below |
| 5 | Key Takeaways | `InfoCard` b, `kind="fact"` |
| 6 | Review — top | `data/reviews.json` |
| 7 | Our Litter and What Each Puppy Costs | `data/puppies.json`; `PuppyCard` c |
| 8 | Getting Your Puppy to Manchester | `settings.delivery_*`, or collection from `settings.location_label` |
| 9 | Health Testing and the Paperwork You Get | `TrustStrip` facts; any licence line is `LICENCE_CLAIM_PLACEHOLDER` |
| 10 | Review — middle | `data/reviews.json` |
| 11 | Raised in Our Home, Not a Kennel | `rules/copy.md` evidence loop |
| 12 | What a Blue Staffy Is Like to Live With | breed facts; lifespan 12–14 years |
| 13 | Newsletter | `InfoCard` b, `kind="note"` |
| 14 | Cities Near Manchester We Deliver To | sibling rows of `data/locations.json` |
| 15 | Competitor-gap section | `NOT FETCHED` — step 1 supplies the topic |
| 16 | Competitor-gap section | `NOT FETCHED` — step 1 supplies the topic |
| 17 | Review — bottom | `data/reviews.json` |
| 18 | Ask Us About a Puppy | `ContactFormKit` c |
| 19 | Manchester Buyer Questions | `data/faq.json` plus page-backed Q&A; `Faq` c |

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
2. Run the competitor scan and record it in the board.
3. Produce the outline — H1→H6 tree, the derived section list with its derivation, keyword
   distribution, review and newsletter positions, FAQ list, schema plan — and get it
   approved (`rules/headings.md` outline gate, `CLAUDE.md` rule 5).
4. Approve the board, then build.
5. Below 97% confidence: write what is not blocked, log the question to the brief's
   `## Open Flags`, ask exactly one narrow question, keep going. Never dead-stop.
