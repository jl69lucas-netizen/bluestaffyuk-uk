---
name: bsuk-seo-master-checklist
description: Use BEFORE starting any interior page build on BlueStaffyUK (homepage, breed/care guides, blog, variant, trust, scam, purchase, FAQ, about) — the 4-phase master SEO execution checklist v2.0 (Pre-Build Research → Planning/Outline Gate → 5-Tier Section Form → Optimization + QA), the 12-category keyword fan-out, 95–105-distinct-entity research (Rule 57, 2026-09-09), 3 anchor-text strategies and the Internal Linking Library (Appendix A). NOT for location or comparison pages (they have their own builders). Triggers - "run the SEO checklist", "master checklist", "Rule 51 outline gate", "keyword fan-out", "Appendix A links".
---

# SKILL: BSUK Master SEO Execution Checklist (v2.0)

## Rule packs

This checklist is long, and where it and a rule pack say the same thing the **pack wins** —
the pack is the copy a checker can be pointed at, and the one that gets updated. Read these
before using anything below, and cite the rule id rather than restating the rule:

| Pack | Rules this checklist leans on |
|---|---|
| `rules/headings.md` | `heading-hierarchy-outline-gate` · `title-case-headings` · `header-style-declared` |
| `rules/copy.md` | `write-from-outline-never-from-sibling` · `first-person-brand-voice` · `entity-4-move-loop` · `meaningful-words-no-stop-words` |
| `rules/images.md` | `image-keyword-distribution` · `uniform-inbody-image-sizing` · `read-card-thumb-is-target-hero` |
| `rules/links.md` | `link-first-anchors` |
| `rules/schema.md` | `no-visible-date` |
| `rules/puppies.md` | `puppies-extended-meta` · `delivery-band-on-every-card` · `product-schema-per-pup` · `instock-only-on-an-available-pup` |
| `rules/gates.md` | `confidence-gate-97` · `recommend-plus-why` · `verify-the-gate-first` · `no-test-no-rule` |
| `rules/deploy.md` | `commit-after-build-never-push` · `release-guarded-publication` · `no-credential-in-a-committed-file` |

Where a section below still restates a pack rule in full, the pack is the source of truth
and the restatement is the copy to delete on the next pass.

---

## SCOPE

**Applies to:** Homepage · Breed guides · Care guides · Blog posts · Variant pages · Trust pages · Scam pages · Purchase guides · FAQ pages · About page · Any new hub or spoke page

**Excluded:** Location pages (use `@bsuk-location-builder` template) · Comparison pages (use `@bsuk-comparison-builder` template)

**Required reading before invoking this skill:**
- `rules/` — the nine rule packs, routed from `CLAUDE.md` (what to do and NOT do)
- `rules/puppies.md` — the litter, prices, delivery band, schema and portrait rules
- a search-console traffic baseline — NOT FETCHED until project 6

---

## INTERIOR-PAGE PROFILE (health · delivery · faq · care/resource · about · why-choose · scam · policy · etc.)

These informational/secondary pages use the **homepage design + method**. The human, copy-paste,
verify-each-step build guide is **`MANUAL INTERIOR-PAGE CHECKLIST.md`** (repo root, Hero → CTA).

**Same as the homepage:** first-person BlueStaffyUK voice · two-keyword conversational headers (Step 5) ·
full H1–H6 band · the 4-Move entity loop + the evidence ledger (`data/quality/evidence-ledger.json`) · Link-First anchors (links at sentence START) ·
"Honesty Policy" humor · GEO/AEO declarative ≤320-char answer blocks · seam-logo dividers
(`.bsuk-seam` + `/bsuk-footer-logo.png`) · AA contrast + Lighthouse perf gates · 5-element image SEO.

**Deltas vs the homepage:**
- **KEEP:** hero · counter snippet · key-takeaway/BLUF · TOC (if >1,500 words) · ≥1 trust element · FAQ · final CTA/contact.
- **DROP** (money/comparison-page-owned): product/puppy grid · breeding-pairs · full compare-table — link out instead.
- **ADD `BreadcrumbList` schema** (interior pages get it; the homepage omits it).

**Excludes (own structure, do NOT use this profile):** comparison · location · all "…for-sale" · blog posts.

---

## HOMEPAGE-SPECIFIC RULES

**Primary keyword: `blue staffy breeder`**
**Homepage is CONVERSION-FIRST. Every section drives toward form submission.**

| Role | Keyword | Placement |
|---|---|---|
| Primary (H1) | `blue staffy breeder` | H1, title tag (Rule 21), the opening sentence (Rule 40), H2s |
| Transactional | `blue staffies for sale` | H2 hero subtitle, counter snippets, CTAs |
| Variant | `blue staffy for sale` | H2 in available puppies section |
| Compliance | `home bred blue staffy` | H2 in LICENCE_CLAIM_PLACEHOLDER trust section |
| Discovery | `buy blue staffy` | H2 in purchase guide section |
| Authority | `LICENCE_CLAIM_PLACEHOLDER documented blue staffy breeder` | H3/H4 in trust section |

**H1 recommendation (approved):**
```
Blue Staffy Breeder | BlueStaffyUK — Home-Raised Blue Staffy Puppies | Carlisle
```

**Homepage CTA rule:** ALL CTAs use form links — NO phone number in body. Phone PHONE_PLACEHOLDER appears ONLY in the footer.

---

## PHASE 1: PRE-BUILD RESEARCH

### Step 1: Competitor Analysis (MANDATORY — 8–12 Competitors)

Before writing ANY content, perform comprehensive competitor research.

**Search queries to analyze:**
1. `[Primary keyword] for sale` — e.g., "Blue Staffy puppies for sale"
2. `[Primary keyword] near me`
3. `buy [primary keyword]`
4. `Blue Staffy breeders`
5. `[Primary keyword] [city]` — the top 5 of the 28 UK cities in `data/locations.json`
6. Search Console queries (Rule 15) and GA4 figures are NOT FETCHED until project 6 — never quote an impression figure

**Competitors to analyze (at least 8 — Rule 55):**
- Top 3 Google organic results for primary keyword
- Top 3 Bing organic results for primary keyword
- 2 specialist UK breeder sites (Rule 55)
- the RSPCA (https://www.rspca.org.uk/) — a competitor-scan benchmark, not a link; a page links only the RSPCA's library rows (B. External Links)
- 1–2 informational authority sites — rows of `docs/reference/external-link-library.md` only (the PDSA, Blue Cross, The Royal Kennel Club)

**For each competitor, document:**
1. **Word Count** — total page length
2. **Sections Included** — all major topics covered (H2 list)
3. **Keyword Usage** — primary, LSI, long-tail variations used
4. **Entity Density** — canine medical terms, locations, brands, people, statistics
5. **Linking Strategy** — internal links (count + anchor patterns), external authority links, anchor text
6. **Unique Selling Points** — health guarantees (theirs; BSUK names one only when `guarantee_days` in `data/settings.json` is set), pricing, delivery safety, certifications
7. **Weaknesses/Gaps** — missing content, weak sections, thin coverage
8. **Strengths** — what they do well that BSUK must match or exceed
9. **User Experience** — navigation, CTA placement, testimonials, FAQ placement
10. **Angles Used** — transactional, urgency, comparison, trust, value, lifestyle
11. **Their ICP** — who are they targeting (first-time owners, experienced puppy keepers, etc.)
12. **Outranking strategy** — specific 3–5 actions to outrank this competitor

**Deliverable format:**

```markdown
# COMPETITOR GAP REPORT — [Page Name]

## Competitor #1: [Name]
- URL: [URL]
- Word Count: [X words]
- H2 Topics: [list all H2s]
- Missing Entities: [canine medical terms, locations, credentials they lack]
- Keyword Gaps: [keywords BSUK can capture that they miss]
- Weaknesses: [thin sections, missing trust signals, poor LICENCE_CLAIM_PLACEHOLDER coverage]
- Our Advantage: [3–5 specific actions to outrank them]

[Repeat for all 8–12 competitors]

## FINAL OUTRANKING STRATEGY
[Comprehensive strategy based on all gaps found — what BSUK page will include that NO competitor has]

## Content Gaps to Fill
- [Gap 1]
- [Gap 2]

## Keywords Competitors Missed
- [Keyword 1]
- [Keyword 2]
```

---

### Step 2: Keyword Research + Entity Research

#### A. Primary Keyword Selection

The primary keyword is set by the page type:
- **Homepage:** `blue staffy breeder`
- **Blue variant page:** `blue staffy for sale`
- **A pup's own page** (`/available-puppies/<slug>/`): `blue staffy puppy for sale`, with the pup's name and its `colour` from `data/puppies.json`
- **Breed guide:** `blue staffy guide` / `blue staffy care`
- **Purchase guide:** `buy blue staffy near me`
- **Scam page:** `blue staffy scam`
- **Price page:** `blue staffy price`

#### B. Keyword Variations by Intent Type (sized to the competitor — Rule 56)

Count the variants the top-ranking competitor page actually uses (a real fetch) and target that
count +5 to +10 (Rule 56), across these categories:

**1. Transactional (Bottom-Funnel):**
- `buy [variant] blue staffy`
- `[variant] blue staffies for sale`
- `[variant] blue staffy pups available now`
- `blue staffy price`
- `home-reared blue staffy for sale`

**2. Long-Tail Conversational (6+ words):**
- `where can I buy a home-reared blue staffy with health guarantee` — only once `guarantee_days` in `data/settings.json` is set
- `best blue staffy breeders near me with LICENCE_CLAIM_PLACEHOLDER documentation`
- `how much does a home-reared blue staffy puppy cost`

**3. Voice Search Optimized:**
- `Are Blue Staffy puppies good for apartments?`
- `How big do Blue Staffy puppies get?`
- `Can I get an Blue Staffy puppy as a first puppy?`

**4. Problem-Solution:**
- `home-reared blue staffy pups`
- `highly socialized companion puppies`
- `LICENCE_CLAIM_PLACEHOLDER documented home-bred blue staffy`
- `apartment-friendly temperament puppy`

**5. Comparison:**
- `blue vs brindle staffy puppies`
- `Blue Staffy vs English Bull Terrier`
- `home-reared vs parent-raised blue staffy`

**6. Geographic/Local:**
- `blue staffy for sale [city]`
- `blue staffy breeders near [city]`
- `blue staffy nationwide delivery`
- Include all 28 UK cities from `data/locations.json`

**7. LSI (Latent Semantic Indexing):**
- Blue Staffy temperament, training, health
- blue coat, blue and white coat, temperament
- companion puppy, home-reared puppy

**8. NLP (Natural Language Processing):**
- blue staffy care requirements
- best food for blue staffies
- blue staffy socialization tips

**9. Branded:**
- `BlueStaffyUK blue staffies`
- `BlueStaffyUK`
- `Lisa Bright blue staffy breeders`
- `Carlisle blue staffy breeder`

**10. Review/Testimonial:**
- `blue staffy reviews`
- `best blue staffy breeder testimonials`
- `BlueStaffyUK reviews`
- `SITE_URL_PLACEHOLDER reviews`

**11. Scam-Avoidance (Negative Keyword Counter-Positioning):**
- `blue staffy scam warning`
- `how to avoid blue staffy scams`
- `LICENCE_CLAIM_PLACEHOLDER certified blue staffy breeder vs scammer`
- `real blue staffy breeders with documentation`

#### C. Entity Optimization (95–105 Distinct Entities, Each Once — Rule 57 as of 2026-09-09)

Every full-length page carries 95–105 **distinct** named entities, each said ONCE where load-bearing (breeder correction 2026-09-09; the old "150+ mentions" floor is retired — a repeated term is a `term-budget-per-page` defect, not a score). The 6 categories:

**1. People Entities (confirmed people only — Rule 57):**
- Lisa Bright (breeder, BlueStaffyUK, Carlisle, Cumbria)
- (no second person has been confirmed — NOT FETCHED)

**2. Location Entities (the 28 cities plus Carlisle — Rule 57):**
- **Primary:** Carlisle · Cumbria (town and region only — no street, no postcode, Known Issue 16)
- **Target cities:** From `data/locations.json` — include all 28 UK cities
- **Delivery routes:** the road legs from Carlisle to the 28 cities — delivery here is by road, by DEFRA-approved transport
- **Regions:** Cumbria, the Borders, the North West, the North East, Yorkshire, Scotland, the Midlands, Wales, the South West, Greater London
- **DEFRA-approved transport coverage:** Cross-reference with `data/locations.json`

**3. Medical/Health Entities (ledger-bounded, no quota):**
- L-2-HGA and HC-HSF4 — the hereditary conditions the breed is DNA-tested for, stated only where the evidence ledger records the certificate
- any other health entity needs an evidence-ledger entry before it is named, and is cited once (Rule 64)

**4. Brand/Product Entities (food and product brands a source names — Rule 57; none invented):**
- a named socialisation or early-handling programme (Puppy Culture, ENH) — only if the breeder confirms it (Lisa's question sheet, the socialisation question); NOT FETCHED today, never stated as a BSUK practice
- The Kennel Club (the UK breed registry)

**5. Statistical Entities (locked facts only — Rule 57):**
- puppies placed — the count and the founding year are NOT FETCHED
- 12–14 years average lifespan
- £1,500–£1,700 Blue Staffy price range
- £1,500 a male · £1,700 a female (`data/price-matrix.json`) — the price follows the sex, not the coat
- £500 refundable deposit · £200–£350 delivery, priced by distance

**6. Credential/Certification Entities (placeholders until confirmed — Rule 57):**
- LICENCE_CLAIM_PLACEHOLDER licence (the statute behind it is LEGAL_CLAIM_PLACEHOLDER)
- a Kennel Club registration — LICENCE_CLAIM_PLACEHOLDER until confirmed
- delivery by DEFRA-approved transport (any transport statute is LEGAL_CLAIM_PLACEHOLDER)

**Entity density target:** 8–12 entities per 100 words (Rule 57; naturally integrated — never listed robotically or force-inserted)

**Good entity integration example:**
> "Every BlueStaffyUK Blue Staffy pup goes home from Carlisle, Cumbria with a vet health check, a microchip and — only where the evidence ledger records the certificate — the parents' results for the hereditary conditions the breed is DNA-tested for (L-2-HGA, HC-HSF4)."

**Bad entity integration (avoid):**
> "Our Blue Staffies get DNA tests and vet checks and microchips and paperwork and..."

---

### Step 3: Keyword Fan-Out Expansion (MANDATORY)

Generate expanded keyword sets in the categories below, sized to the competitor (Rule 56: its variant
count +5 to +10, split across the categories):

**Category 1: Transactional Keywords**
Examples:
- `buy blue staffies [city]`
- `blue staffies for sale [city]`
- `purchase home-reared blue staffy pup`
- `LICENCE_CLAIM_PLACEHOLDER documented blue staffy available`
Generate more targeting the page's primary keyword + city modifiers (the 28 UK cities in `data/locations.json`)

**Category 2: Conversational/Voice Search**
Examples:
- `Where is the best place to buy an blue staffy?`
- `How much does a Blue Staffy puppy cost?`
- `Who are reputable blue staffy breeders in [city]?`
- `What should I look for in an blue staffy breeder?`
Generate more in full question format

**Category 3: Problem-Solution Keywords**
Examples:
- `home-bred blue staffy with LICENCE_CLAIM_PLACEHOLDER documentation`
- `apartment-friendly temperament puppy`
- `blue staffy for first-time puppy owner`
Generate more

**Category 4: Comparison Keywords**
Examples:
- `blue vs brindle staffy breeders`
- `Blue Staffy vs American Bully for beginners`
- `home-reared vs parent-raised blue staffy temperament`
Generate more

**Category 5: Delivery/Delivery Keywords**
Examples:
- `blue staffy delivery service to [city]`
- `blue staffy delivery by DEFRA-approved transport [city]`
- `safe blue staffy delivery nationwide`
Generate more

**Category 6: City-Based Keywords**
Examples:
- `blue staffies for sale [city] [city]`
- `blue staffy breeders [city]`
- `buy blue staffy near [city]`
Cover ALL target cities from `data/locations.json`

**Category 7: NLP/LSI Variants**
Examples:
- `ethical blue staffy breeders`
- `DNA health tested blue staffy`
- `vet-checked blue staffy puppy`
- `home-bred LICENCE_CLAIM_PLACEHOLDER compliant puppy breeder`
Generate more

**Category 8: Scam-Avoidance Keywords**
Examples:
- `legitimate blue staffy breeder vs scam`
- `verified LICENCE_CLAIM_PLACEHOLDER documentation blue staffy`
- `blue staffy scam warning signs`
- `how to find reputable blue staffy breeders`
Generate more

**Category 9: Care/Lifestyle Keywords**
Examples:
- `blue staffy care requirements`
- `blue staffy lifespan commitment`
- `blue staffy care for beginners`
- `blue staffy temperament training`
Generate more

**Category 10: Trust/Review Keywords**
Examples:
- `BlueStaffyUK blue staffy reviews`
- `best blue staffy breeder testimonials`
- `SITE_URL_PLACEHOLDER ratings`
- `lisa bright blue staffy reviews`
Generate more

**Category 11: Variant-Specific Keywords**
Examples:
- `blue and white vs solid blue staffy personality`
- `male vs female blue staffy differences`
Generate more

**Category 12: Important Keywords (Suggested)**
Generate additional keyword suggestions based on the specific page topic, competitor analysis gaps, and — from project 6 — search-console data. Until then no query or impression figure may be written

---

### Step 4: Location/Logistics Entity Research

For pages with a delivery/delivery section, use web search to gather these entities:

**Geographic Entities Required:**
- The cities in `data/locations.json` for the target region
- Most puppy-friendly neighborhoods/communities in key cities
- Canine vet clinics in key cities — research context only; a page never names a local business
- UK dog-ownership rules relevant to the cities in `data/locations.json` (LEGAL_CLAIM_PLACEHOLDER until confirmed)

**Authority Entities Required:**
- UK veterinary and breed bodies — link only their rows of `docs/reference/external-link-library.md`
- LICENCE_CLAIM_PLACEHOLDER LICENCE_CLAIM_PLACEHOLDER regional offices
- Local puppy/canine societies and clubs

**Logistics Entities Required:**
- DEFRA-approved pet transport companies serving the 28 UK cities in `data/locations.json`
- Road routes from Carlisle to the target cities (a travel time is NOT FETCHED unless sourced)

---

## PHASE 2: PLANNING GATE

### Step 5: Page Structure Planning

**Section count:** no default. The count is `section_target.total` in the page's question file (`data/queries/<slug>.json`, from `/bsuk-query-augmentation`): the competitors' highest cleaned H2 count + 3, never fewer than 9 (`docs/reference/location-page-template.md`, "Section count").

**Word count:** `NOT FETCHED` until the competitor scan gives a median — never pick a number first and write to fill it (Rule 27).

**Header count targets (Rule 28):**
- H1: exactly 1 per page (hero only)
- H2: 25–35 · H3: 40–50 · H4: 10–20
- H5: minimum 5 — deep LSI / technical authority terms
- H6: minimum 5 — voice-search phrasing, breeder notes, citations
- All six levels on every full-length page, no skipped level. On the homepage and the location
  pages the 5-per-level minimums are advisory (WARN); "all six levels" and "no skipped levels"
  stay hard (`rules/headings.md`, `heading-hierarchy-outline-gate`).

**Two-Keyword Header Method (apply to every header that can carry a second term):**
Each header should pull double SEO duty: **[secondary/conversational keyword] + [related LSI · NLP · entity · concurrent keyword · or long-form modifier]**. Don't stop at the obvious keyword — append a second, *useful* term that broadens the header's reach without keyword-stuffing.
- ✅ "Why Choose BlueStaffyUK For Your **Home-Reared** Blue Staffies?" (secondary KW + LSI "home-reared")
- ✅ "How Much Does a **Blue** Blue Staffy Cost — and What's the **First-Year Total**?" (variant entity + long-form concurrent KW)
- ✅ "How Does BlueStaffyUK **Deliver** a Blue Staffy **to Your City**?" (transactional KW + geographic NLP)
- ❌ "Why Choose Us?" (no keyword) · ❌ "Delivery" (single bare term)
Keep it natural and conversational (What/How/Is/Can/Who). One secondary keyword + one related term per header — never three+ stacked. Applies across H2–H4 especially.

**Candidate topics, not a section list.** Choose only the topics the competitor scan and BSUK's own
data support; how many body sections the page has is `section_target.total` (above), never this
table's length. Word ranges are planning guides, not quotas.

| # | Section | Word Count | Anchor ID |
|---|---|---|---|
| 1 | Hero — H1 + subheadline + key takeaways + counter snippets | 150–200 | `#top` |
| 2 | Available Puppies & Current Litter | 400–600 | `#available-puppies` |
| 3 | Health Testing — the parents' tests as the evidence ledger records them, `NOT FETCHED` otherwise; the guarantee as `guarantee_days` in `data/settings.json` (the breeder's answer of 2026-09-29: 730 days, a two-year guarantee) and `guarantee_label` word it | 800–1,200 | `#health-testing` |
| 4 | What is a [Variant] Blue Staffy? | 200–250 | `#what-is-blue-staffy` |
| 5 | Blue Staffy Breed History & Research | 300–400 | `#breed-history` |
| 6 | Blue Staffy Temperament & Personality | 400–500 | `#temperament` |
| 7 | Blue Staffy Coat Care & Grooming | 500–600 | `#grooming` |
| 8 | Blue Staffy Nutrition & Diet | 500–600 | `#nutrition` |
| 9 | Blue Staffy Training & Training Development | 400–500 | `#training` |
| 10 | Blue Staffy Care & Environmental Needs | 400–500 | `#care-environment` |
| 11 | Blue Staffy Socialisation — a named programme (Puppy Culture, ENH) only if the breeder confirms it (Lisa's question sheet, the socialisation question); NOT FETCHED today, never stated as a BSUK practice | 300–400 | `#socialization` |
| 12 | Why Choose BlueStaffyUK for Your Blue Staffy | 300–400 | `#why-choose-BSUK` |
| 13 | About BlueStaffyUK & Meet Lisa Bright | 200–250 | `#about-BSUK` |
| 14 | How BlueStaffyUK Raises Its Litters — in the family home, not kennels (`about-home-raised` in `data/faq.json`) | 250–300 | `#how-we-raise` |
| 15 | Meet the Parents | 300–400 | `#meet-parents` |
| 16 | Reviews — top, middle and bottom: one row of `data/reviews.json` each, a `Testimonial mode="single"` block in its own section, never inside a body section | N/A | its own section |
| 17 | BlueStaffyUK Breeding Commitment & Ethics | 200–250 | `#breeding-commitment` |
| 18 | Male or Female? Choosing From Our Litter | 500–600 | `#choosing-your-puppy` |
| 19 | DEFRA-approved transport Delivery & Coverage Areas | 700–900 | `#delivery` |
| 20 | Frequently Asked Questions — the question file's picks (`faq` in `data/queries/<slug>.json`) | 800–1,000 | `#faqs` |
| 21 | How to Buy Your Blue Staffy from BlueStaffyUK | 300–400 | `#how-to-buy` |
| 22 | Contact Information & Next Steps | 150–200 | `#contact` |
| 23 | Map & DEFRA-approved transport Delivery Coverage Area | 100–150 | `#map` |
| 24 | Table of Contents (Required >1,500 words) | N/A | `#toc` |

---

### Step 6: Page Outline Gate + User Approval (FULL STOP — Rule 51)

**STOP. Do not write any section content until the user explicitly approves this outline.**

The Page Outline document must contain ALL of the following:

**A. Page Identity**
- Target URL slug
- Primary keyword (exact match)
- Page type (Transactional / Informational / Comparison / Scam Recovery / Breed Guide / Care Guide)
- Recommended framework (AIDA, PAS, QAB, EBD, BAB, H-S-S, Inverse Pyramid, Entity-Tree)
- Target word count: the competitor scan's median (Rule 27) — NOT FETCHED until the scan exists

**B. Competitor Snapshot (top 5 competitors)**
For each: URL, word count, all H2 topics listed, primary keywords, special elements, unique angles, weaknesses BSUK can exploit.

**C. Complete H1–H6 Heading Tree**
Every heading on the page with:
- Heading level (H1/H2/H3/H4/H5/H6)
- Heading text (draft — question format where natural)
- Keyword type (Primary / Secondary / LSI / NLP / Longtail / Comparison / Voice Search)
- Why this heading (1 sentence)
- Section angle (AIDA, PAS, QAB, EBD, BAB, H-S-S, Trust, Urgency, Comparison, Value, Lifestyle)

**D. Keyword Distribution Table (section by section)**

| Section | Heading | Primary KW | LSI KWs | Longtail KWs | NLP/Conv | Comparison | Word Count |
|---|---|---|---|---|---|---|---|

Total row at bottom stays at or under 105 total keyword mentions (Rule 18 — a ceiling, no floor).

**E. Special Elements Plan**
- Newsletter: one block only, frame part 10 — `InfoCard kind="recommendation" label="Newsletter"` with `id="newsletter"`; no offer, no subscriber count
- Comparison table
- Price card
- Counter snippets (4, immediately after the hero — Rule 31)
- Trust badge bar
- Contact/inquiry form (3 required per page — Rule 32)
- Video embed placeholder
- FAQ accordion
- Table of Contents (required >1,500 words — Rule 29)

**F. Fan-Out Keyword List**
All keyword variations planned: exact match, phrase match, LSI clusters, NLP signals, PAA questions, voice queries, location modifiers, comparison phrases.

**GATE:** User must respond with "Approved", "Continue", or specific changes before any section is written.

---

## PHASE 3: BUILD

### Step 7: Section-by-Section Writing

**Workflow (Rule 13):**
1. Produce competitor analysis only → STOP, wait for user
2. User approves → produce Sections 1–5 only → STOP
3. User says "Continue" → produce Sections 6–10 → STOP
4. Repeat in batches of 5 until all sections complete
5. NEVER skip sections. NEVER merge sections. NEVER continue without "Continue" command.

#### 5-Tier Section Creation Form (complete BEFORE writing each section)

```
SECTION [#]: [TITLE]
================================================

TIER 1: CRITICAL ELEMENTS
—————————————————————————
1. Section Number & Title: Section [#]: [Exact Title]

2. Target Word Count:
   Min: [number - 10%]
   Max: [number + 10%]

3. Primary Keywords (3–5 from fan-out — Rule 59):
   ✓ [Primary Keyword] (0.8–1.2% of the section — Rule 19)
   ✓ [Secondary Keyword] (use naturally)
   ✓ [Long-tail Keyword] (use naturally)
   ✓ [LSI Keyword] (use naturally)
   ✓ [Location/Entity Keyword] (once — Rule 57)

TIER 2: CONTENT FOUNDATION
—————————————————————————
4. Content Angle (choose primary):
   ☐ T — Transactional/Urgency
   ☐ C — Comparison/Differentiation
   ☐ E — Health/E-E-A-T
   ☐ Blended — [specify angles]

   Supporting angles:
   ☐ [Second angle]
   ☐ [Third angle]

5. Conversational Opening (75–100 words, framework-matched):
   [Write the opening — Entity-Benefit-Purpose format]
   (Entity: what. Feature: measurable fact. Benefit: what buyer gains. Purpose: why it matters long-term.)

6. Header Structure (complete before writing):
   H2: [Main section header with primary keyword]
   H3: [Subsection 1 — question format preferred]
   H3: [Subsection 2]
   H4: [Detail point 1 with LSI keyword]
   H4: [Detail point 2 with LSI keyword]
   H5: [Technical authority term — e.g., "L-2-HGA Screening Protocol"]
   H6: [Voice search query — e.g., "Is This Puppy Good With Kids?"]

TIER 3: LINKING STRATEGY
—————————————————————————
7. Internal Links (no per-section count):
   Position: START of the sentence (Link-First, `rules/links.md`).
   Use varied anchor text — no repetition.
   1. [Anchor Text] → [/<slug>/]  |  Context: [where it appears]
   2. [Anchor Text] → [/<slug>/]  |  Context: [where it appears]
   [Continue for as many as the section needs — each to a route that exists under `src/pages/` or comes from `data/locations.json`, `data/puppies.json` or the blog posts (Rule 62; Appendix A lists them)]

8. External Authority Links (1–2 per section):
   Position: START of the sentence (Link-First, `rules/links.md`).
   Use descriptive anchor text (not "click here").
   1. [Anchor Text] → [a row of docs/reference/external-link-library.md]  |  Source: [PDSA / RSPCA / Royal Kennel Club / GOV.UK …]
   2. [Anchor Text] → [a row of docs/reference/external-link-library.md]  |  Source: [authority]

TIER 4: ENTITY & TRUST
—————————————————————————
9. Geographic Entities (3–5 per section):
   ☐ Cities: [specific cities mentioned]
   ☐ Cities/Regions: [cities from `data/locations.json` referenced]
   ☐ Delivery routes / travel time from Carlisle: [if relevant]

10. Authority Entities (1–2 per section):
    ☐ [a UK veterinary or breed body with a row in the link library]
    ☐ [a credential — LICENCE_CLAIM_PLACEHOLDER until confirmed]

11. Trust Signals (2–3 per section):
    ☐ "[count NOT FETCHED] puppies placed..."
    ☐ "12–14 year lifespan commitment..."
    ☐ "LICENCE_CLAIM_PLACEHOLDER LEGAL_CLAIM_PLACEHOLDER home-bred..."
    ☐ "Raised in our home, not in kennels..." (`about-home-raised`)
    ☐ A locked fact: £500 refundable deposit, £200–£350 delivery by distance, £1,500 / £1,700 (Rule 57)

TIER 5: QUALITY CONTROL
—————————————————————————
12. Special Elements for this Section:
    ☐ FAQ module
    ☐ Pricing table
    ☐ Comparison table
    ☐ Map embed
    ☐ Image gallery/placeholder

13. Image Requirements:
    ☐ [Section image description] — [dimensions per `data/image-manifest.json` (Rule IMAGE-01)]
    ☐ Alt text ≤190 characters (`scripts/final_page_audit.py`, `img_alt_le190`)
    ☐ Title, caption and description block (Step 12's five elements)
    ☐ File name: [keyword-rich-seo-filename.webp]

14. Call-To-Action (form-based — NO phone number):
    CTA Type: ☐ Inquire Now ☐ Submit Inquiry ☐ Reserve a Puppy ☐ See Available Puppies
    CTA Text: "[Action statement with benefit, link to /uk-blue-staffy-breeders-contact/]"

15. Final Section Checklist:
    ☐ Word count within target range
    ☐ Primary keyword at 0.8–1.2% of the section, naturally (Rule 19)
    ☐ Internal links only to routes that exist (Appendix A) — Link-First: anchor at sentence start
    ☐ 1–2 external authority links included
    ☐ 3–5 geographic entities mentioned
    ☐ Headers use question format where natural
    ☐ Conversational, warm, expert breeder tone
    ☐ Short paragraphs; the section opening is 50–80 words with the answer first (Rule 40)
    ☐ No keyword stuffing
    ☐ No stop words used unnecessarily
    ☐ Negative keywords addressed (scam / puppy farm / cheap)
    ☐ Trust signals included
    ☐ Local entities naturally integrated
    ☐ Clear CTA at section end (form link only)
    ☐ Home-reared in Carlisle stated in the counters after the hero (Rule 31)
```

---

### Step 8: Linking Strategy

#### A. Internal Links (only routes that exist — no count)

No rule sets a number of internal links. `rules/links.md` sets where the anchor sits (Link-First)
and Rule 62 sets the targets: routes that exist under `src/pages/` or come from `data/locations.json`,
`data/puppies.json` or the blog posts (Appendix A lists them), `/<slug>/` with the trailing slash.
The source template's "50 or more" assumed a larger site (`docs/reference/location-page-template.md`).

**Link categories:**

**1. Navigation Links:**
- Table of Contents at top (jump links to all sections)
- Quick navigation menu at bottom
- Back to top: `[⬆ Back to Top](#top)` at end of each major section

**2. Cross-Section Jump Links (examples):**
- From Key Takeaways → Available Puppies, Health Testing, Pricing
- From Available Puppies → Purchase Process, Delivery, Testimonials
- From Health Testing → Socialisation, Meet Parent Puppies (a guarantee is named only when `guarantee_days` in `data/settings.json` is set)
- From Choosing From Our Litter → each pup's own page under `/available-puppies/`
- From FAQ → Relevant sections (Care, Diet, Delivery)
- From How to Buy → Available Puppies, Contact, Delivery

**3. Related Pages (Internal Site Links):**
Use Appendix A URL Library at end of this skill for all valid URLs.

**4. Contextual Links (Within Paragraphs):**
Example: `"Our [Staffordshire Bull Terrier guide](/uk-staffordshire-bull-terrier-guide/) covers diet in depth."`
Example: `"[The breeder story](/blue-staffy-uk-breeders/) explains how every litter is raised in our home."`

#### B. External Links (rows of the library only)

Every outside link goes to a URL recorded in `docs/reference/external-link-library.md`; a board
naming any other URL is refused (`scripts/pageboard.py`). There is no per-page quota: link where
an independent UK source says it better than we can, anchor first. To cite something new, check
it returns 200 and add the row before the board names it. Today's rows, by topic:

**Health & Veterinary:**
1. [PDSA — Staffordshire Bull Terrier breed advice](https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/puppies-dogs/medium-dogs/staffordshire-bull-terrier)
2. [PDSA — dog vaccinations](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/other-veterinary-advice/dog-vaccines)
3. [PDSA — how much exercise a dog needs](https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/puppies-dogs/how-much-exercise-does-your-dog-need)
4. [BVA — eye scheme](https://www.bva.co.uk/canine-health-schemes/eye-scheme/)
5. [The Royal Kennel Club — the L-2-HGA DNA test](https://www.royalkennelclub.com/health-and-dog-care/health-dog-care/health/getting-started-with-health-testing-and-screening/dna-testing/dna-test-l-2hga/)
6. [The Royal Kennel Club — the HC-HSF4 DNA test](https://www.royalkennelclub.com/health-and-dog-care/health-dog-care/health/getting-started-with-health-testing-and-screening/dna-testing/dna-test-hc-hsf4/)
7. [The Royal Kennel Club — understanding canine genetics](https://www.royalkennelclub.com/health-and-dog-care/health-dog-care/health/getting-started-with-health-testing-and-screening/understanding-canine-genetics/)
8. [RSPCA — caring for a new puppy](https://www.rspca.org.uk/adviceandwelfare/pets/dogs/health/puppycare)

**Breed Information & Standards:**
1. [The Royal Kennel Club — the Staffordshire Bull Terrier breed standard](https://www.royalkennelclub.com/breed-standards/terrier/staffordshire-bull-terrier/)
2. [The Royal Kennel Club — the Staffordshire Bull Terrier breed page](https://www.royalkennelclub.com/search/breeds-a-to-z/breeds/terrier/staffordshire-bull-terrier/)
3. [The Kennel Club](https://www.thekennelclub.org.uk/)

**Training & Behaviour:**
1. [Blue Cross — socialising your puppy](https://www.bluecross.org.uk/advice/dog/socialising-your-puppy)
2. [RSPCA — puppy advice](https://www.rspca.org.uk/adviceandwelfare/pets/dogs/puppy)

**Buying Safely & the Law** (a statute line stays `LEGAL_CLAIM_PLACEHOLDER` until confirmed):
1. [RSPCA — spotting a puppy dealer](https://www.rspca.org.uk/adviceandwelfare/pets/dogs/puppy/sales)
2. [The Royal Kennel Club — questions to ask the breeder](https://www.royalkennelclub.com/your-dog/getting-a-dog/buying-a-dog/questions-for-the-breeder/)
3. [The Kennel Club — breeding regulations](https://www.thekennelclub.org.uk/dog-breeding/dog-breeding-regulations/)
4. [GOV.UK — microchipping your dog](https://www.gov.uk/get-your-dog-cat-microchipped)
5. [GOV.UK — welfare in transport guidance (PB10308)](https://assets.publishing.service.gov.uk/media/5a819d3bed915d74e623335d/pb10308-dogs-cats-welfare-060215.pdf)
6. [GOV.UK — banned dogs](https://www.gov.uk/control-dog-public/banned-dogs) — the breed guide's row, and the one statute line a city page may state: the Staffordshire Bull Terrier is not a banned breed (the user's ruling on Known Issue 46, 2026-09-23)

#### C. 3 Anchor Text Strategies (Rule 58)

**Strategy 1: Exact Match Anchors (use sparingly — 1–2 per page)**
- Anchor text = the exact keyword you want the target page to rank for
- Power: Highest SEO signal · Risk: Moderate if overused
- Best for: Links from detail pages to category/hub pages

Example: "[Blue Staffy puppies for sale](/available-puppies/) are listed one pup to a page."

**Strategy 2: Conversational/Descriptive Anchors (preferred — most links)**
- Anchor text = longer phrase describing destination naturally within a sentence
- Power: Medium-High · Risk: Low
- Best for: Long-tail keyword links, cross-section navigation

Example: "[Whether a Staffy suits a flat](#temperament) comes down to its daily exercise and company."
Example: "[The buying guide's visit checklist](/uk-blue-staffy-puppy-buying-guide/) lists the paperwork to ask for."

**Strategy 3: Branded Anchors (use for trust building)**
- Anchor text = brand/company name
- Best for: About page references, testimonials, schema reinforcement

Example: "[BlueStaffyUK](/blue-staffy-uk-breeders/) raises every litter in the family home in Carlisle."

---

### Step 9: Special Elements Placement

**Counter Snippets (Rule 31):**
Four counters immediately after the hero, under four words each, each starting with a number or
percentage, each stating something BlueStaffyUK can back:
- `£500 Refundable Deposit`
- `12–14 Year Lifespan`
- `28 UK Cities Covered`
- `Home-Reared in Carlisle`

A counter that asserts a licence, an award or a review count is a defect, not a variation (Rule 31).

**Contact/Inquiry Forms (3 required — Rule 32):**
1. After hero / counter snippets (top)
2. After trust section / mid-page
3. After FAQ section (bottom)

**CTAs — Form Only (Rule 61):**
- ✅ `👉 [Submit an inquiry to reserve your Blue Staffy](/uk-blue-staffy-breeders-contact/)`
- ✅ `📋 [Fill out our quick inquiry form](/uk-blue-staffy-breeders-contact/)`
- ✅ `<a href="/uk-blue-staffy-breeders-contact/" class="bsuk-btn-primary">Inquire About a Puppy</a>`
- ❌ `📞 Call PHONE_PLACEHOLDER to reserve today!` — NEVER in body copy

**Newsletter (one block, frame part 10):** `InfoCard kind="recommendation" label="Newsletter"` with `id="newsletter"`. It says what a subscriber gets
(`bsuk-location-page-builder`, Newsletter); no invented offer (a free guide, a calculator) and no
subscriber count. There is never a second block.

**Image Placeholders:**
Leave clearly labeled placeholders for all images/videos:
- `[INSERT PHOTO: puppy-name-profile.webp] Alt: "[≤190-char keyword-rich alt text]" Title: "[transactional-keyword phrase]"`
- `[INSERT INFOGRAPHIC: feature-type-760px.html]`
- `[INSERT VIDEO: filename.mp4]`
- `[INSERT MAP: google-maps-carlisle-embed]`

---

### Step 10: Writing Guidelines

#### A. Voice & Tone

**✅ DO:**
- Natural, conversational language — write like a trusted dog breeder
- Answer real questions people actually search
- Include emotional connection and empathy (a 12–14 year commitment is life-changing)
- Build trust through transparency (pricing, documentation, process)
- Sound human, warm, and knowledgeable
- Guide readers: Curiosity → Trust → Inquiry → Form Submission
- Use contractions: "we're" not "we are", "you'll" not "you will"
- Second person (you/your): Address reader directly
- Satisfy search intent immediately in the first paragraph
- Question-based H2/H3 headers (conversational FAQ format: What, How, Is, Can, Do)

**❌ DON'T:**
- Keyword stuff: "Blue staffy for sale... our Blue staffies for sale..."
- Use robotic language: "This product..." / "This offering..."
- Repeat exact phrases unnaturally
- Sound like a template or generic AI output
- Use aggressive marketing or unverifiable claims
- Use excessive exclamation points
- Use ALL CAPS except for emphasis
- Use generic platitudes ("We care about puppies" — be specific!)
- Overpromise ("Perfect companion for everyone without effort!")

**Good vs Bad Examples:**

❌ Bad: "Blue Staffy pups are available for sale. They are smart puppies. Contact us."
✅ Good: "Looking for a family dog who wants to be wherever you are? Our Blue Staffy puppies are home-raised by Lisa Bright in Carlisle, Cumbria, and go home at £1,500 or £1,700."

❌ Bad: "Our puppies have health guarantees." (a bare claim — BSUK names its guarantee only with the length and words of `guarantee_days` and `guarantee_label` in `data/settings.json`)
✅ Good: "What if your puppy develops an underlying congenital health issue later in life? Start with the parents: we show you the health tests the evidence ledger records for them, and we claim nothing it does not."

#### B. Humor Rules (Apply to ALL Pages — Rule 36)

Apply thoughtfully, not forced. Four humor modes:

1. **"The Honesty Policy"** — relatable breeder honesty:
   *"Our Blue Staffies are bred for companionship, and for the uncanny ability to hear the fridge door open from two rooms away."*

2. **"The Interviewer" Tone** — the puppy is vetting the owner:
   *"Are you prepared to lose the best spot on the sofa for the next twelve to fourteen years? Apply to be [Puppy Name]'s forever person."*

3. **Punny Wordplay** — lean into the breed's character:
   *"Blue coat, big grin, no interest whatsoever in personal space."*

4. **Comparison Humor** — unexpected comparisons:
   *"Technically this is a puppy. Functionally, it is a family member on a twelve-to-fourteen-year contract."*

#### C. Opening Paragraph Formula (Rule 37)

Every section opening (1–2 sentences) must contain all four:
- **Entity** — who/what (puppy name, variant, BlueStaffyUK, Carlisle)
- **Feature** — a measurable, locked fact (price, deposit, delivery band, age)
- **Benefit** — what it means for the buyer
- **Purpose** — the deeper reason it matters (a 12–14 year bond, a family commitment)

Example (Rule 37's own): *"Roman is a blue Staffordshire Bull Terrier pup reared at home in Carlisle (entity) at £1,500 with a £500 refundable deposit (feature), handled daily so he settles into a new household within days rather than weeks (benefit) — the start of a 12–14 year relationship (purpose)."*

#### D. Conversational Header Format (Rules 38, 52)

**ALL headers in conversation FAQ-style where natural — format: What / How / I / Is / Can / Do / Are**

H1 examples:
1. "Where Can I Buy a Home-Reared Blue Staffy Puppy with LICENCE_CLAIM_PLACEHOLDER Documentation?"
2. "Looking for an Intelligent Companion? Meet Our Home-Bred Blue Staffy Puppies"
3. "Blue Staffy Puppies for Sale: DEFRA-approved transport Safe Delivery to 28 UK Cities from Carlisle"
4. "Why Are BlueStaffyUK Blue Staffies Chosen by [count NOT FETCHED] Happy Families?"
5. "Ready for a Twelve-to-Fourteen-Year Companion? Meet Our Home-Reared Blue Staffy Puppies"
6. "Blue Staffy Breeder | BlueStaffyUK — Home-Raised Blue Staffy Puppies | Carlisle"

H2 examples:
- "What Makes the Blue Staffy the Ultimate Companion Puppy?"
- "How Much Does a Home-Bred Blue Staffy Really Cost? (Full Price Breakdown)"
- "Are Blue Staffies Good in Flats? Here's What Our Placements Taught Us"
- "Male or Female Blue Staffy: Which Puppy Is Right for Your Family?"

H3 examples:
- "Do Blue Staffies Bark a Lot? (And How to Teach Quiet Behaviour)"
- "Can I Leave My Blue Staffy Alone During the Workday? (The Honest Answer)"
- "What's Included with Every BlueStaffyUK Blue Staffy? (Full Documentation Breakdown)"

H5 examples (technical authority — must be present):
- "What an L-2-HGA Result Means for a Puppy Buyer"
- "LICENCE_CLAIM_PLACEHOLDER Licence Explained"

H6 examples (voice search — must be present):
- "Is This Puppy Good With Kids?"
- "What Happens After I Pay a Deposit?"
- "Can I Visit the Pups at Home Before Buying?"
- "How Do I Know This Puppy Is Home-Bred?"

#### E. Paragraph Structure

**Opening paragraph format (first 150 words of page):**
1. Answer the primary question immediately
2. Include location-specific details (Carlisle + the target city from `data/locations.json`)
3. Integrate entities naturally (Rule 57: 8–12 per 100 words)
4. Add clear call-to-action (form link)
5. Use long-tail keyword variations

**Body paragraph guidelines:**
- Short, scannable paragraphs
- One main idea per paragraph
- Use transition words (However, Additionally, For example)
- Bold key facts, prices, important stats sparingly
- Include specific examples and figures — locked facts only (Rule 57)

---

## PHASE 4: OPTIMIZATION + QA

### Step 11: SEO Optimization

#### A. Meta Information (Rules 21, 23)

**Meta title — Rule 21, the only format:**
```
[Primary Keyword] + [Number where authentic] + [Power Word] + [Long-tail conversational query] + BlueStaffyUK
```
- Begin with the primary keyword
- Add a number ONLY where it is locked: £1,500 / £1,700, £500 deposit, £200–£350 delivery, 28 cities, 12–14 years. Anything else is NOT FETCHED.
- Power word from Rule 21: Trusted, Healthy, Home-Reared, Hand-Socialised
- End with `BlueStaffyUK` (or `BlueStaffyUK – Carlisle`)
- One clause, no pipe separators, **≤ 70 characters**

Example: `Blue Staffy Puppies for Sale, Home-Reared in Carlisle – BlueStaffyUK` (68 characters)

**Tone labels (Rule 22 — retired):** 🔴 urgency / 🆚 comparison / 💰 transactional / 🛡️ trust survive as
planning labels only — never rendered into a title or description.

**Meta Description (Rule 23):**
- ≤ 160 characters, conversational, benefit-driven, one sentence flow
- Must carry: primary keyword + a long-tail or LSI variation + a trust signal + a CTA
- Emphasise what is locked: home-reared in Carlisle, UK delivery £200–£350 by distance via
  DEFRA-approved transport or collection in Carlisle, £500 refundable deposit
- Never emphasise a licence, a statute or a review count; a guarantee length only as `guarantee_days` and `guarantee_label` in `data/settings.json` word it

Example:
> Home-reared Blue Staffy puppies from Carlisle, £1,500–£1,700 with a £500 refundable deposit and UK delivery by DEFRA-approved transport. Ask about a pup today.

#### B. Schema Markup (Rule 5)

Implement these schema types on every full page:
1. **Organization Schema** — BlueStaffyUK business information (managed by `src/components/Schema.astro`)
2. **LocalBusiness Schema** — Carlisle location, hours, contact
3. **Product Schema** — Individual puppy listings with price, availability
4. **FAQPage Schema** — one per page, naming exactly the visible FAQ questions (`scripts/query_coverage_check.py`)
5. **BreadcrumbList Schema** — `Home > [Section] > [Page]`
6. **Person Schema** — Lisa Bright profiles (on About page)

No AggregateRating markup: no review corpus has been established (Rule 33).
Never remove or modify an existing schema JSON-LD block — preserve it verbatim, only add (Rule 5).

#### C. Voice Search & AI Chatbot Optimization (AIO/GEO)

**Strategies:**
1. Use natural questions as H2/H3 headers (How, What, Why, When, Where, Are, Can, Is, Do)
2. Answer the question in the section's first sentence (Rule 40)
3. Featured snippet-ready content (Rule 41):
   - Bullet lists with clear structure
   - Comparison tables (3–6 columns, 3–8 rows, first column = categories)
   - Step-by-step numbered lists
   - Rapid-fire definition paragraphs
4. Conversational phrasing (contractions, second-person)
5. Long-tail queries within H2/H3 headers
6. Entity-dense answers (proper nouns, locked figures, specific conditions)

**Voice Search Optimization Example:**
Query: "How big do Blue Staffy puppies get?"
Optimized answer (a paragraph snippet of roughly fifty words, answer first — Rule 41): lead with the adult height and weight from the Kennel Club breed standard once it has been fetched (NOT FETCHED) — never a figure from memory — then one line on how BlueStaffyUK raises its pups at home in Carlisle.

#### D. Keyword Density Guidelines (Rule 18, 19)

**Target keyword density:**
- Primary keyword: 1–2% on the page (Rule 18), 0.8–1.2% per section (Rule 19) — never forced
- Secondary keywords: the Rule 18 frequency table's counts
- LSI keywords: distributed fluidly throughout
- Long-tail variations: embedded in headers and body

**Keyword placement priority:**
1. H1 title (primary keyword front-loaded)
2. The opening sentence (primary keyword early — Rule 40)
3. H2 headers (transactional + conversational variations)
4. Body paragraphs (organic contextual flow)
5. Image alt text (where strictly relevant)
6. Meta title and meta description
7. URL slug (`/[primary-keyword-slug]/`)

---

### Step 12: Image Optimization (Rules IMAGE-01 to IMAGE-04, `rules/images.md`)

**Before generating any image:**
1. Read `rules/images.md` for the current page type and section
2. Use the specified `dims`, `source`, and `infographic_type` exactly
3. Priority: breeder instruction > `data/image-manifest.json` > agent defaults (Rule IMAGE-01)

**Every image is a ranking asset — the 5-Element Image-SEO rule is a MUST (none optional):**
1. **FILENAME** — keyword-rich, lowercase-with-hyphens, `.webp`, no spaces (e.g. `home-reared-male-blue-blue-staffy-for-sale-carlisle.webp`).
2. **ALT TEXT** — descriptive, **≤190 characters** (AA / screen-reader cap + the `final_page_audit` alt-length check; an alt >190 is a FAIL). Lead with keyword + entity + context + location.
3. **TITLE** — the `title=""` attribute: a short transactional-keyword phrase.
4. **CAPTION** — a visible `<figcaption>` with a soft CTA where natural.
5. **DESCRIPTION** — a long-form SEO description block (image-metadata pipeline, not the rendered DOM).

**Transactional-keyword variation rule (MUST):** each image's filename / alt / title must use a *different* transactional keyword variation than the visible page copy — e.g. "buy home-reared male Blue Staffy," "vet-checked Blue Staffy puppy for sale near me," "home-bred Blue Staffy for sale Manchester" — so one page ranks for many queries. Never repeat the H1 keyword verbatim across images.

- **File size:** <100 KB WebP for page-content images (`rules/images.md`, `uniform-inbody-image-sizing`)
- **Dimensions:** `data/image-manifest.json` per page type (Rule IMAGE-01)

> **ALT-length correction (2026-06-20):** alt was once specced far longer; corrected to **≤190** for WCAG AA + auditor compliance. The long-form content now lives in the **TITLE + CAPTION + DESCRIPTION**, not in ALT.

**Portrait images:** 1200×2133px native (9:16) — CSS display width: 350px (Rule IMAGE-03)
**Infographic widths (Rule 54):**
- Breed guide, blog, care guide: **760px** wrapper, 400px desktop height
- Homepage, location pages, hero: **1100px** wrapper, 400px desktop height
- Mobile: 100% width, auto height

**OG Image:** Every page needs a 1200×630px OG image (separate generation — Rule IMAGE-04)

**Alt text example (location-specific, ≤190 characters):**
```
Home-reared blue Staffy puppy for sale from BlueStaffyUK in Carlisle, ready for delivery by DEFRA-approved transport to Manchester
```

---

### Step 13: Readability Check

**Target metrics:**
- Flesch Reading Ease: 60–70, floor about 55 for entity-dense pages — never gut entity density to
  chase it (`bsuk-final-page-pass`)
- Short sentences, short paragraphs, active voice and plain transitions — guides, not gates; no rule
  or checker sets a number for them

**Transition words to use:**
However, Additionally, For example, Specifically, In contrast, As a result, Furthermore, Because of this, Unlike, In addition to, That said, Here's why...

---

### Step 14: Content Delivery Format (Rule 60)

Every full-length page build delivers 4 documents as separate outputs:

**PART 1: Competitor Analysis Report**
- 8–12 competitor breakdowns with gap matrix
- Core keyword gaps identified
- Final outranking strategy

**PART 2: Complete Page Content (Main Document)**
Format requirements:
- Markdown (.md)
- H1–H6 heading structure throughout
- Every section anchor tag: `<a name="section-name"></a>` or `id="section-name"`
- All internal links: `[Link Text](#anchor)` or `[Link Text](/<page-url>/)`
- All external links: `[Link Text](https://example.com/)` with `target="_blank"`
- Image placeholders: `[INSERT PHOTO: filename.webp]` with alt text
- Newsletter: the one frame-part-10 block (`id="newsletter"`), never one per section
- Map placeholders: `[INSERT MAP: description]`
- Video placeholders: `[INSERT VIDEO: filename.mp4]`

**Document structure:**
```markdown
<a name="top"></a>
# [H1 Title — Primary Keyword Front-Loaded]

[Opening paragraph: entities + Carlisle + benefits + form CTA]

👉 [Inquire about available Blue Staffy pups](/uk-blue-staffy-breeders-contact/)

---

## Quick Navigation — Jump to Any Section
[Table of Contents with all section jump links]

---

<a name="key-takeaways"></a>
## Key Takeaways

[Content]

---

[Continue for every body section — `section_target.total` of them (Step 5) — through to contact/navigation]

---

## Quick Navigation — Jump to Any Section (Bottom)
[Navigation grid organized by topic]

[External resource links list]

[⬆ Back to Top](#top)

---
*This page contains [WORD COUNT] total words and incorporates all [#] mandatory sections.*
```

**PART 3: SEO Metadata Sheet**
- 3 meta title options (Rule 21: one clause, ≤ 70 characters)
- 3 meta description options (Rule 23: ≤ 160 characters)
- Primary target keyword
- Secondary keywords list, LSI keyword groupings and conversational long-tail strings — sized to the
  fan-out (Rule 56)
- Schema markup implementation instructions

**PART 4: Linking Strategy Map**
- Complete internal link map (source anchor → target page/section)
- External authority link catalog by category
- Full jump link blueprint (all section anchors)

---

### Step 15: QA Checklist (15-Point Verification)

Before final submission, verify all items:

**Content Completeness:**
- ☐ All required sections present with target word counts achieved
- ☐ Word total from the competitor scan's median (Step 5) — `NOT FETCHED` until that scan exists, never a number picked first
- ☐ Alternative phrasings: five for every H2 and H3 (Rule 38)
- ☐ Puppy details only from `data/puppies.json` (`rules/puppies.md`), and only on a page that shows the litter — an interior page links to it instead
- ☐ Reviews top, middle and bottom: the three rows of `data/reviews.json`, one per slot, each a `Testimonial mode="single"` block in its own section
- ☐ Newsletter: one block only, frame part 10 — `InfoCard kind="recommendation" label="Newsletter"` with `id="newsletter"`; no offer, never a subscriber count
- ☐ FAQ: "every picked question appears on the page, each an H3, in score order" (`bsuk-query-augmentation`) — the picks are `faq` in `data/queries/<slug>.json`, and questions come only from fetched sources and `data/faq.json`. A city page splits them into three blocks, 17–20 questions (the gate checks 15–20; `docs/reference/location-page-template.md`); other pages may render them in one `Faq` block, and the final pass requires a FAQPage (`bsuk-final-page-pass`, `faqpage_present`)
- ☐ 95–105 distinct named entities, each once where load-bearing (Rule 57, 2026-09-09) — people, locations, medical, brands, stats, credentials

**Linking Quality:**
- ☐ Internal links only to a route that exists under `src/pages/` or comes from `data/locations.json`, `data/puppies.json` or the blog posts (Rule 62; Appendix A lists them), with the trailing slash — Link-First: anchors at sentence start; varied anchor text, no repeats per target
- ☐ Every external link is a row of `docs/reference/external-link-library.md` — no per-page quota; a board naming any other URL is refused
- ☐ All anchor targets verified to exist on the site
- ☐ Table of Contents at top with all section jump links
- ☐ Quick navigation at bottom
- ☐ "Back to Top" links at end of each major section

**Search Engine Alignment:**
- ☐ Primary keyword in the H1, the title tag (Rule 21) and the opening sentence (Rule 40)
- ☐ Keyword density 1–2% on the page (Rule 18), 0.8–1.2% per section (Rule 19) — natural, not stuffed
- ☐ 3 meta title options + 3 meta descriptions delivered
- ☐ All 6 heading levels (H1–H6) present and sequentially correct
- ☐ Home-reared in Carlisle stated in the counters after the hero (Rule 31)
- ☐ Coat colours named as the litter has them (each pup's `colour` in `data/puppies.json`; none is brindle)
- ☐ The 12–14 year commitment referenced at least once (Rule 34)
- ☐ Voice search questions embedded in H2/H3 headers

**User Conversion Metrics:**
- ☐ Conversational, authentic breeder tone maintained throughout
- ☐ The inquiry form at least three times — after the hero, mid-page after the trust section, after the FAQ (Rule 32); no phone number in body copy (Rule 61)
- ☐ Mobile-optimized layout (short paragraphs, bullet breakdowns)
- ☐ No technical jargon barriers or generic AI-sounding copy
- ☐ Buyer fears addressed — scam, cheap puppies, puppy-farm suspicion — stating only what the repo can back (Rule 20)
- ☐ Empathy displayed toward common ownership challenges (a 12–14 year commitment, lifespan, care)

**Technical Format:**
- ☐ All image placeholders with keyword-rich filenames, ≤190-char alt text + title + caption (5-element rule)
- ☐ Video content placeholders present where needed
- ☐ Map embedding placeholders present for delivery/location sections
- ☐ The one newsletter block at frame part 10 (`id="newsletter"`)
- ☐ Schema markup recommendations provided (FAQPage, Organization, Product, BreadcrumbList)
- ☐ Canonical URL formatted correctly (absolute: `https://SITE_URL_PLACEHOLDER/<slug>/`)

---

## FINAL REMINDERS (Step 10)

This is NOT a template-filling exercise. Every page must:

1. **Actually perform competitor research** across premium canine domains using Firecrawl MCP or Playwright MCP
2. **Analyze existing content gaps** to deliver fundamentally superior, more thorough page layouts
3. **Write with genuine human voice** (conversational warmth, professional breeding expertise)
4. **Integrate proper nouns and medical entities seamlessly** (avoid forced keyword groupings)
5. **Link with strategic accuracy** (internal links only to a route that exists under `src/pages/` or comes from `data/locations.json`, `data/puppies.json` or the blog posts (Rule 62; Appendix A lists them), external links only to rows of `docs/reference/external-link-library.md`)
6. **Optimize for natural language processing** (voice query compatibility, clear definition blocks)
7. **Maintain conversion-driven layouts** (form CTAs, a real, checkable litter count (Rule 39), trust signals a data file backs)
8. **Uphold flawless E-E-A-T** (demonstrate actual canine science, real-world handling experience, authority)

**Success benchmarks:**
- Outranks existing kennel sites for primary keyword
- Earns citations from AI search engines (Google AIO, Perplexity, Claude)
- Converts curious browsers into qualified Blue Staffy inquiries via form submissions
- Provides genuine education protecting puppy health and supporting long-term owner success
- Underscores BlueStaffyUK ethical commitment to home-bred, LICENCE_CLAIM_PLACEHOLDER-compliant dog breeding

---

## APPENDIX A: Internal Linking Library

The routes a page may link to, each listed once. Rule 62: never invent an internal URL — link
only to a route that exists under `src/pages/` (the city, puppy and post routes come from
`data/locations.json`, `data/puppies.json` and the blog posts). `data/page-map.json` is the
canonical page list and wins over this appendix; every route here is a built page. All routes use
the trailing slash; an absolute URL (a canonical tag) is `https://SITE_URL_PLACEHOLDER` + the route.

**Core pages:**
- `/` — the homepage
- `/uk-blue-staffy-breeders-contact/` — contact and the enquiry form (every body CTA, Rule 61)
- `/blue-staffy-uk-breeders/` — the breeder story (about)
- `/privacy-policy-uk/` — the privacy policy

**Puppies, prices and health:**
- `/available-puppies/` — the litter; each pup has its own page, `/available-puppies/<name>/`
- `/buy-blue-staffy-puppies-uk/`
- `/blue-staffy-pup-sale-uk/`
- `/buy-staffy-puppies-for-sale-uk/`
- `/blue-staffy-health-uk/`

**Guides:**
- `/uk-blue-staffy-puppy-buying-guide/`
- `/uk-staffordshire-bull-terrier-guide/`

**Blog:**
- `/blue-staffy-blog-guides/` — the blog hub
- `/how-to-choose-the-right-blue-staffy-puppy-for-your-family/` — a post; posts sit at the site root (`src/pages/[...post].astro`)
- `/blog/` is the legacy archive address — `noindex`, its canonical is the hub. Never link to it.

**Location pages** (every slug is a row of `data/locations.json`):
- `/uk-locations/` — the locations index
- `/uk-locations/staffy-puppies-for-sale-essex/`
- `/uk-locations/blue-staffy-puppies-middlesbrough/`
- `/uk-locations/blue-staffy-puppies-london/`
- `/uk-locations/staffy-breeding-dogs-glasgow/`
- `/uk-locations/staffy-puppies-cardiff-wales/`
- `/uk-locations/blue-staffy-puppies-dundee/`
- `/uk-locations/blue-staffy-puppies-uk/`
- `/uk-locations/blue-staffy-puppies-for-sale-leeds/`
- `/uk-locations/blue-staffy-puppies-edinburgh/`
- `/uk-locations/staffy-puppies-for-sale-nottingham/`
- `/uk-locations/staffy-puppies-for-sale-liverpool/`
- `/uk-locations/blue-staffy-puppies-sunderland/`
- `/uk-locations/staffy-puppies-for-sale-cornwall/`
- `/uk-locations/blue-staffies-newcastle-under-lyme/`
- `/uk-locations/blue-staffy-puppies-for-sale-in-leicester/`
- `/uk-locations/blue-staffy-puppies-bristol-uk/`
- `/uk-locations/blue-staffy-puppies-south-yorkshire/`
- `/uk-locations/staffy-puppies-for-sale-glasgow/`
- `/uk-locations/blue-staffy-puppies-aberdeen/`
- `/uk-locations/blue-staffy-puppies-inverness/`
- `/uk-locations/staffy-puppies-wolverhampton/`
- `/uk-locations/buy-blue-staffy-puppy-coventry-area/`
- `/uk-locations/blue-staffy-puppies-hull/`
- `/uk-locations/blue-staffy-puppies-york/`
- `/uk-locations/uk-staffordshire-bull-terrier-breeder/`
- `/uk-locations/blue-staffy-puppies-oxford/`
- `/uk-locations/blue-staffy-puppies-manchester-uk/`
- `/uk-locations/blue-staffy-puppies-birmingham/`
---

## APPENDIX B: Example Execution

### Example Section: Blue Staffy Temperament & Personality

```markdown
<a name="temperament"></a>
## What is the Real Blue Staffy Temperament? Understanding the Intellectual Companion Puppy

[The Royal Kennel Club's Staffordshire Bull Terrier breed page](https://www.royalkennelclub.com/search/breeds-a-to-z/breeds/terrier/staffordshire-bull-terrier/) is the best first stop if you're
wondering whether a Blue Staffy matches your daily home life. [BlueStaffyUK](#about-BSUK) raises every litter
in our family home in Carlisle, and the breed's reputation holds up there: Staffies are affectionate,
observant companions who bond closely with their chosen families.

### What Makes the Blue Staffy Personality So Unique?

**Core Temperament Trait Profiles:**
- **Deeply Empathetic:** Staffies are incredibly sensitive to human emotions and frequently match the calm 
  or energetic mood of their owners.
- **Incredibly Observant:** They notice subtle environmental changes — learning your daily routine and 
  watching your movements with deep focus.
- **Playful Thinkers:** Beyond simple play, they require interactive, complex mental challenges like 
  puzzle boxes and enrichment games.
- **Adaptable Companions:** Excel in dedicated canine spaces, quiet home offices, or spacious urban 
  apartments when given steady daily interaction.

### Blue Staffy Cognitive Capacity: How Trainable Are They?

How quickly a BlueStaffyUK pup learns is a trainability claim BSUK has not verified — NOT FETCHED
until Lisa confirms it from her own litters.

##### L-2-HGA and Behavioral Stability
L-2-HGA is one of the hereditary conditions the breed is DNA-tested for (L-2-HGA, HC-HSF4); a parent's
result is stated only where the evidence ledger records the certificate.

###### Can I Leave My Blue Staffy Alone During Work Hours?
How long an adult Blue Staffy can be left is NOT FETCHED until Lisa gives her own answer — never a
number of hours from memory. [See how to buy](#how-to-buy).

---

👉 [Submit an inquiry about our available pups](/uk-blue-staffy-breeders-contact/).

**Continue Reading:**
- [Complete Blue Staffy Environmental & Crate Setup Guide](#care-environment)
- [Advanced Training and Clicker Training Techniques](#training)
- [How a Blue Staffy Puppy Is Socialised](#socialization)
- [Male or Female? Choosing From Our Litter](#choosing-your-puppy)

**Authoritative External Resources:**
- [RSPCA — caring for a new puppy](https://www.rspca.org.uk/adviceandwelfare/pets/dogs/health/puppycare)
```

---

## APPENDIX C: Term Conversion Table — retired

The source repo's term-conversion table mapped another breeder's names, places, programmes
and US regulators onto BlueStaffyUK. Nothing is converted from that material any more: every
BSUK fact comes from `data/*.json`, and an outside source is a row of
`docs/reference/external-link-library.md`.
