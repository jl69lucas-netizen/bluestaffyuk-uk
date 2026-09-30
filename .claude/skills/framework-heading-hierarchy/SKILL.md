---
name: framework-heading-hierarchy
description: H1–H6 strategic keyword placement guide for BSUK pages. Maps each heading level to a specific keyword type and user intent. Use before writing or auditing any page's heading structure. Prevents empty headings, keyword-stuffed headers, and wrong intent-level targeting.
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Every heading level targets a specific keyword type. Never use a heading just for formatting — every heading must capture a distinct search intent layer and could stand alone as a Google search query.

---

## BSUK Project Context
> **Site:** BlueStaffyUK — home-raised Blue Staffordshire Bull Terrier breeder in Carlisle, Cumbria
> **The litter:** `data/puppies.json` — males Roman, Byrd, Ince at £1,500 · females Vennie, Christa, Cheryl at £1,700. The price follows the sex, not the coat; each pup's coat is its own row's `colour` (blue, blue and white, white, blue with white blaze), and none of the six is brindle
> **Licensing:** LICENCE_CLAIM_PLACEHOLDER and LEGAL_CLAIM_PLACEHOLDER compliance — NOT YET CONFIRMED by Lisa Bright. Never state either as fact, and never imply a puppy-farm or third-party sale.
> **Trust pillars:** LICENCE_CLAIM_PLACEHOLDER · LEGAL_CLAIM_PLACEHOLDER · KC registration · Microchip number · Vet health check · First vaccinations + worming record · Fully weaned + home-raised
> **Buyer fears (ranked):** Scam/unlicensed seller · Sick puppy · Puppy-farm origin · Missing paperwork · No post-sale support
> **Pages:** `src/pages/` (built: `dist/`) | **Session docs:** `docs/superpowers/sessions/`
> **Confidence Gate:** ≥97% before writing any site file

---

## Purpose

You are the **Heading Hierarchy Framework** for BlueStaffyUK. Use this before writing or auditing any page's heading structure. It maps H1–H6 to specific keyword types, provides example patterns, and includes a full audit checklist.

---

## The 6-Level Keyword Mapping

### H1 — Primary Keyword (One Per Page, Strict)
**Maps to:** Highest-volume transactional or informational keyword for the page
**Format:** Primary keyword + coat-colour/variant modifier + optional brand or location
**Rules:**
- ONE H1 per page — never two H1s on the same page
- Never repeat the H1 text verbatim anywhere else on the page
- Include the main commercial keyword in the first 3 words where possible

**Examples:**
- `Blue Staffy Puppies for Sale UK | Home-Raised in Carlisle | BlueStaffyUK`
- `Blue and White Staffy Puppy for Sale in [UK Region] | Home-Raised, KC Registered`
- `Blue vs Blue Brindle Staffy: The Complete Buyer's Comparison`

---

### H2 — Secondary Keyword + Conversational Hook
**Maps to:** Long-tail variation (location, coat-colour modifier, or "Staffordshire Bull Terrier" context) + conversational wrapper
**Format:** Secondary keyword + question or benefit statement
**Rules:**
- Use 2+ H2s per section; Q&A format where it fits naturally
- H2s must form a logical narrative when scanned without body text

**3 H2 Patterns:**
- *Location Focus:* "Searching for a Home-Raised Blue Staffy Puppy in [UK Region]? Meet [Name]."
- *Coat-Colour Focus:* "Meet [Name]: The [Coat, from `colour` in data/puppies.json] Staffy Perfect for Families."
- *Benefit Focus:* "Why Every Puppy Includes KC Registration, a Microchip and a Vet Health Check."

**5 Alternative Variations Rule:**
For every core H2, generate 5 variations for A/B testing:
1. Direct statement version
2. Question version
3. Location-specific version
4. Benefit-focused version
5. Documentation/trust version

---

### H3 — Category Keywords (Specific Attributes)
**Maps to:** Attribute-level keywords: Size, Coat colour, Temperament, Paperwork, Health, Trainability, Weaning
**Format:** Category keyword + specific angle or question
**Rules:**
- H3s must be subordinate to their parent H2 (don't skip levels)
- Each H3 covers a distinct attribute angle — no two H3s under the same H2 repeat the same topic

**Examples:**
- *Size:* "How Big Will [Name] Get? Adult Weight and Size for Blue Staffies."
- *Health:* "Peace of Mind: Is [Name] L-2-HGA Clear by Parentage? What That Means for Your New Puppy."
- *Documentation:* "What Paperwork Comes with [Name]?"
- *Temperament:* "Boisterous or Calm? How to Match a Staffy's Temperament to Your Lifestyle."

---

### H4 — LSI Keywords (Contextual Depth)
**Maps to:** Latent Semantic Indexing (LSI) terms — words frequently found alongside Blue Staffy topics
**Format:** LSI keyword or phrase + specific sub-topic
**Purpose:** Shows Google the page covers the topic in depth, not just the sale

**Examples:**
- Feeding Schedule, Weaning Timeline, Socialisation Protocol, Hereditary Cataract Screening, Hip Scoring
- "[Name]'s Progress: Feeding Schedule and Where We Are in the Weaning Process."
- "Puppy Care 101: Nutritional Needs for a Young Staffordshire Bull Terrier."
- "What's Included: KC Registration, Microchip Number, Vet Health Check and Worming Record."

---

### H5 — Deep LSI / Technical Authority Terms (MANDATORY — Minimum 5 Per Page)
**Maps to:** Technical and expert terms that establish topical authority on Staffordshire Bull Terrier breeding
**Format:** Specific technical term + context or explanation
**Purpose:** Signals expertise to Google and AIO; targets niche searchers who know the terminology
**Status: MANDATORY — not optional. Every full-length page (22+ sections) must have ≥5 H5 headings.**

**Examples:**
- "Meeting the Parents: Blue Staffy Genetic and Behavioural Lineage."
- "Hereditary Cataracts (HC) Explained: Why It Matters for Your Puppy's Health."
- "Travel Ready: How [Name] Gets to Your UK Region with Full Paperwork."
- "LICENCE_CLAIM_PLACEHOLDER Explained: What Annual Inspection Means for Buyers."
- "L-2-HGA DNA Status: How We Confirm Your Puppy Is Clear Before Collection."
- "Microchip Number and KC Registration: Your Puppy's Identity on Paper."

---

### H6 — NLP / Voice Search / Ultra-Specific Breeder Notes & Citations (MANDATORY — Minimum 5 Per Page)
**Maps to:** Phrases users speak into Siri, Alexa, or type into AI chatbots; plus ultra-specific details, breeder notes, and source citations
**Format:** Natural language question or statement matching real voice queries; or a precise breeder note / cited fact
**Purpose:** Captures voice search and AI Overview citations; answers "what users actually say" and anchors hyper-specific authority detail
**Status: MANDATORY — not optional. Every full-length page must have ≥5 H6 headings (no fewer than 5 — 1 H6 = automatic FAIL, breeder rule 2026-06-20).**

**Examples:**
- "Is [Name] Good with Kids and Other Pets?"
- "What Is the Total Price and Is a Deposit Required?"
- "Ready to Go Home Now: How to Reserve [Name] Today."
- "Can I See [Name] Before I Commit? How Our Home Visits Work."
- "What Happens After I Pay the £500 Deposit?"
- "How Long Until My Puppy Is Ready to Come Home?"

---

## Header Style Selection (added 2026-07-29)

The 6-level map above decides **what keyword** each heading carries. This section
decides **how it is phrased** — and the choice must be justified out loud at the
outline gate, grounded in that page's own query data, never in taste.

### The three styles

**Style 1 — Pure Conversational.** Natural language, reader curiosity, no forced
keyword.
*"What Is It Really Like to Live with a Blue Staffy?"*
Highest engagement, weakest keyword signal.

**Style 2 — Conversational Hybrid (keyword + entity).** Question or benefit phrasing
wrapped around a target keyword and a named entity.
*"How to Choose the Best Blue Staffy Crate Setup"* ·
*"Safe Foods vs. Toxic Foods for Staffordshire Bull Terriers"*
Balanced. Best for informational depth across many sections.

**Style 3 — Recommended Hybrid (direct-answer / snippet-targeted).** Question plus a
parenthetical or colon that states the answer scope, so the section is extractable on
its own.
*"What Do Blue Staffies Eat? (Nutrition & Safe Foods)"*
Strongest for Featured Snippets and AI Overviews. Reads repetitive if every H2 uses
it — alternate with Style 2 inside a page.

### Register variants (choose the register, not a fourth style)

| Register | Example | Best for | Cost |
|---|---|---|---|
| **FAQ question-based** | "How Long Do Blue Staffies Live?" | direct answers, AIO + Featured Snippets | monotonous if overused |
| **Quora-style** | "Why Is My Staffy Chewing Its Paws Raw All of a Sudden?" | long-tail behaviour / problem posts | too long to scan |
| **Reddit-style** | "Is a Blue Staffy Actually Worth the Hassle for a First-Time Owner?" | community, subjective, review roundups, Reddit-modifier pages | weak explicit keyword |

### Page-type → default style

| Page type | Default | Why |
|---|---|---|
| For-sale / buy (transactional) | **Style 3**, ~30% Style 2 | Buyer queries are decision questions; the parenthetical carries the commercial modifier without stuffing the H2 |
| Comparison | **Style 3**, both entities named | The query *is* the comparison — both entities must appear for passage-level ranking |
| Care / health / informational | **Style 2** | Long-tail depth queries; entity density beats snippet framing across 20+ sections |
| Puppy listing `/available-puppies/` | **FAQ register on Style 2** | Buyers ask about one named puppy — name + attribute + question |
| Reddit-modifier | **Reddit register**, deliberately | The page's whole promise is "what owners actually say" |
| Blog | **Style 2**, Quora-register H1 | Curiosity opener, keyword body |
| Location | **Style 2** with the geo modifier | The UK region/city IS the differentiator |
| Legal / privacy | Plain declarative | No search intent to serve; clarity only |

### The justification requirement (binding)

Every H1–H6 outline presented at the Sprint 1 gate MUST carry a one-line style
declaration and a reason grounded in real data — the page's GSC/query set, the SERP
snapshot, PAA demand, or a named competitor gap. **Never taste.**

```
Header style: Style 3 (Recommended Hybrid), FAQ register on H4–H6.
Why: price intent beats rehoming intent 5:1 in this page's own query set, and 6 of the
top 10 SERP results are question-led — so a direct-answer H2 competes for the snippet
those informational results currently hold.
Trade-off: Style 3 on every H2 reads repetitive; H3s alternate to Style 2.
```

An outline submitted without the style line and its reason is **incomplete** and does
not pass the gate. Deviating from the page-type default is allowed; deviating
**silently** is not.

Style choice never overrides the heading standards: **Title Case applies to every
H1–H6 regardless of style**, and FAQ `<summary>` text — which is not a heading — stays
conversational sentence case.

---

## The No-Skip Law

Heading levels MUST be sequential. You cannot use H2 and then jump to H4 — H3 must come first.
The only legal movements are: one level down (H2 → H3), or back up to any higher level to start a new section (H4 → H2 is fine when starting a new major topic).

**ILLEGAL patterns — these break the heading audit and hurt SEO:**
- H2 → H4 (skipped H3) ❌
- H3 → H5 (skipped H4) ❌
- H1 → H3 (skipped H2) ❌
- H2 → H5 → H6 (skipped H3 and H4) ❌

**LEGAL patterns:**
- H2 → H3 → H4 → H5 → H6 → H2 (new major section) ✓
- H2 → H3 → H2 (stepping back up to start a new major topic) ✓
- H3 → H4 → H5 → H3 (back up within a section) ✓
- H4 → H5 → H6 → H2 (jumping back up to open a new section) ✓

**Mnemonic:** Think of headings like filesystem folders. You cannot create `/H2/H4/` without `/H2/H3/H4/` — the intermediate folder must exist first.

---

## Complete Example: Individual Puppy Listing Page

```
H1: Roman — Blue Staffy Puppy for Sale | Male, KC Registered, £1,500 | BlueStaffyUK
H2: Searching for a Home-Raised Blue Staffy Puppy in [UK Region]? Meet Your Match.
  H3: How Big Will Roman Get? Adult Size and Weight for Blue Staffies.
    H4: Current Weight: Where Roman Is in His Development Timeline.
    H4: What Roman Eats: His Weaning Diet and Feeding Schedule.
  H3: Is Roman Microchipped and Vet Checked? What That Means for Your New Puppy.
    H4: Complete Documentation: KC Registration, Vet Health Check, First Vaccinations and Worming Record.
    H5: Hereditary Cataracts (HC) Explained: Why It Matters for Your Puppy's Health.
H2: Why Choose a Blue Staffy from BlueStaffyUK?
  H3: Blue vs Blue Brindle: Which Coat Colour Is Right for Your Household?
  H3: How Roman Was Raised: Our Home-Raising and Socialisation Protocol.
    H4: Enrichment and Training Progress: What Roman Can Do at [X] Weeks.
    H5: LICENCE_CLAIM_PLACEHOLDER: What Annual Inspection Means for Buyers.
    H6: Is Roman Lead Trained Yet? Here's What to Expect at This Age.
H2: How to Reserve Roman and Bring Him Home
  H3: The BSUK Reservation Process: 5 Simple Steps.
    H4: The £500 Deposit That Books Your Viewing, Payment, and What's Included in Roman's Delivery Package.
    H6: Ready to Go Now: How to Reserve Roman Today.
```

---

## Heading Audit Checklist

Run this on every page before publishing or after any heading changes:

- [ ] Exactly 1 H1 on the page (grep: `<h1`)
- [ ] H1 contains primary keyword in first 3 words
- [ ] H1 is unique across the site (no other page has the same H1 text)
- [ ] H2s use conversational or question format where applicable
- [ ] H3s cover distinct attribute angles (health, size, documentation, temperament — not repeating)
- [ ] H4 headings present (target 10–20 on full-length pages)
- [ ] **H5 count ≥ 5** on EVERY page (MANDATORY) — grep: `<h5`
- [ ] **H6 count ≥ 5** on EVERY page (MANDATORY) — grep: `<h6`
- [ ] **OUTLINE SHOWN + APPROVED FIRST** — the full H1→H6 outline was presented to the breeder and approved BEFORE any page code was written/edited
- [ ] **No level skipping** — run skip-detection command below
- [ ] No two adjacent headings at the same level with the same keyword
- [ ] No heading text duplicated verbatim in body paragraphs below it
- [ ] Every H2/H3 could stand alone as a realistic Google search query
- [ ] H6 headings use natural language / voice search phrasing (not marketing language)

**Audit commands:**
```bash
# List all headings in order
grep -n "<h[1-6]" dist/[slug]/index.html | head -80

# Count each level
grep -c "<h5" dist/[slug]/index.html   # must be ≥5
grep -c "<h6" dist/[slug]/index.html   # must be ≥5

# Detect skipped levels (prints any H-jump greater than 1)
grep -oP '(?<=<)[hH][1-6]' dist/[slug]/index.html | grep -oP '[1-6]' | awk 'NR>1 && $1 > prev+1 {print "SKIP DETECTED: H"prev" → H"$1} {prev=$1}'
```

---

## Anti-Patterns (Never Do)

- `<h2>Staffordshire Bull Terriers</h2>` — too generic, not a search query
- `<h2>Best Blue Staffy Puppies For Sale Near Me In 2025</h2>` — keyword stuffing
- Two `<h1>` tags on the same page
- Using `<h4>` directly under `<h2>` without an `<h3>` in between
- Heading text like "Section 3" or "Introduction" that adds no SEO value
- Repeating the H1 keyword verbatim in every H2
- Using heading levels purely for font size styling — every heading must carry a keyword

---

## Rules

1. **One H1 per page** — non-negotiable
2. **5 variations per core H2** — required for all commercial and location pages
3. **No level skipping** — sequential order only (H1 → H2 → H3 → H4 → H5 → H6); jumping levels is BANNED
4. **All six levels required** on every full-length page (22+ sections) — H5 and H6 are not optional
5. **H5 minimum: 5 per page** — supporting facts / warnings / examples (deep LSI / technical authority)
6. **H6 minimum: 5 per page** — ultra-specific details / breeder notes / citations / voice-search queries
7. **Question format preferred for H2/H3** — conversational, voice-search optimized
8. **Audit command first** — always grep heading levels and run skip-detection before manual review
9. **OUTLINE-FIRST APPROVAL GATE** — the full H1→H6 heading tree must be presented to the breeder and **approved before any page code is written or edited** (breeder rule 2026-06-20). Semantic map: H1=topic · H2=search intents · H3=subtopics/clusters · H4=micro-intent/PAA · H5=supporting facts/warnings/examples · H6=ultra-specific details/breeder notes/citations.
10. **HEADER STYLE MUST BE DECLARED AND JUSTIFIED** at the outline gate — one of Style 1 (Pure Conversational) / Style 2 (Conversational Hybrid) / Style 3 (Recommended Hybrid), plus its register (FAQ / Quora / Reddit), with a data-grounded reason and a named trade-off. See §Header Style Selection. **No style line = incomplete outline.**
11. **STYLE FOLLOWS PAGE TYPE BY DEFAULT** — Style 3 for transactional and comparison, Style 2 for informational / care / location / blog, FAQ register for puppy listings, Reddit register for Reddit-modifier pages. Deviating is allowed; deviating silently is not.
12. **TITLE CASE OVERRIDES STYLE** — every H1–H6 is AP-style Title Case whatever the style. FAQ `<summary>` text is not a heading and stays sentence case.
