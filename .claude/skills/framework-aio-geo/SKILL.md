---
name: framework-aio-geo
description: "Reference guide for AIO (AI Overview) and GEO (Generative Engine Optimization) applied to BSUK content. Use when building or auditing any page that should be cited by ChatGPT, Perplexity, Google AIO, or other AI answer engines."
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## BSUK Project Context
> **Site:** BlueStaffyUK — licensed Blue Staffordshire Bull Terrier breeder, Glasgow
> **Coat colours:** Blue (Roman, Byrd, Ince — £1,500) · Blue brindle / black brindle (Vennie, Christa, Cheryl — £1,700) — treat as distinct product lines
> **Licensing:** LICENCE_CLAIM_PLACEHOLDER and LEGAL_CLAIM_PLACEHOLDER compliance — NOT YET CONFIRMED by Lisa Bright. Never state either as fact, and never imply a puppy-farm or third-party sale.
> **Trust pillars:** LICENCE_CLAIM_PLACEHOLDER · LEGAL_CLAIM_PLACEHOLDER · KC registration · Microchip number · Vet health check · First vaccinations + worming record · Fully weaned + home-raised
> **Buyer fears (ranked):** Scam/unlicensed seller · Sick puppy · Puppy-farm origin · Missing paperwork · No post-sale support
> **Content root:** `site/content/` | **Sessions:** `sessions/`
> **Confidence Gate:** ≥97% before writing any site file

---

## What AIO/GEO Is

**AIO (AI Overview):** Google's generative answers that appear above search results, citing sources. Being cited in AIO drives significant no-click impressions and brand authority.

**GEO (Generative Engine Optimization):** Optimizing content to be cited by ChatGPT, Perplexity, Claude, Gemini, and other AI answer engines when users ask questions about Staffordshire Bull Terriers, breeders, or puppy buying.

The core insight: AI engines prefer content that is **structured, declarative, source-attributed, and entity-rich** — the opposite of vague blog-style prose.

---

## AIO/GEO Citation Triggers

Content gets cited by AI engines when it:

1. **Answers a specific question directly in the first sentence**
2. **Contains named entities** (puppy names, health conditions, certifications, locations)
3. **Uses declarative statements** ("Staffordshire Bull Terriers weigh X" not "Staffordshire Bull Terriers can weigh")
4. **Attributes claims to named sources** ("confirmed by KC registration + vet health check," "per LICENCE_CLAIM_PLACEHOLDER standards")
5. **Uses structured patterns** (tables, lists, labeled sections) over undifferentiated prose
6. **Has FAQPage schema** — directly feeds AI answer extraction

---

## Entity-First Writing Pattern

AI engines parse content as entity → attribute → value. Structure content to match:

```
Entity:    Staffordshire Bull Terrier
Attribute: Coat colours
Value:     Blue: 11–17 kg, solid grey-blue coat, £1,500 | Blue brindle / black brindle: 11–17 kg, striped coat, £1,700
Source:    docs/reference/domain-knowledge.md + BSUK breeding data

Entity:    Staffordshire Bull Terrier
Attribute: Lifespan
Value:     12–14 years with routine veterinary care
Source:    Kennel Club breed health data (Staffordshire Bull Terrier longevity surveys)

Entity:    Staffordshire Bull Terrier
Attribute: Legal sale status in the UK
Value:     LEGAL_CLAIM_PLACEHOLDER — the breeder's verifiable legal standing (LICENCE_CLAIM_PLACEHOLDER) is what a buyer checks before paying
Source:    LICENCE_CLAIM_PLACEHOLDER / LEGAL_CLAIM_PLACEHOLDER
```

**Prose translation:**
```
Bad (vague): "Blue Staffy puppies come in different colours and live a long time."

Good (citable): "Blue Staffordshire Bull Terriers are bred in two colour lines: the solid blue
Staffy (11–17 kg, grey-blue coat, £1,500) and the blue or black brindle Staffy (11–17 kg,
striped coat, £1,700). With routine veterinary care, Staffordshire Bull Terriers live 12–14
years — a typical lifespan for a medium-sized terrier breed."
```

---

## Inverse Pyramid for AIO

Every section must lead with the answer — AI engines pull from the first sentence, not the conclusion:

```
Paragraph 1: [Direct answer — the fact stated plainly]
Paragraph 2: [Evidence — named source, specific data]
Paragraph 3: [BSUK context — how this applies to BSUK breeding]
```

**Example — licensing and paperwork section:**
```
Para 1: Blue Staffordshire Bull Terrier puppies come directly from the breeder who
        raised them, with LEGAL_CLAIM_PLACEHOLDER, LICENCE_CLAIM_PLACEHOLDER number and
        full paperwork.

Para 2: KC registration + a vet health check confirms each puppy's health status and
        identity. A microchip number is required by law before a puppy leaves the breeder.

Para 3: BlueStaffyUK includes a LICENCE_CLAIM_PLACEHOLDER number, KC registration,
        microchip number, vet health check, and first vaccinations with worming record on
        every puppy — buyers can verify full documentation before bringing their puppy home.
```

---

## Structured Data for AIO

### FAQPage Schema (required on every FAQ section)
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How much does a blue Staffordshire Bull Terrier puppy cost?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Blue Staffordshire Bull Terrier puppies from licensed UK breeders range from £1,500 to £1,700. Price depends on coat colour, sex, and pedigree. Every puppy from BlueStaffyUK includes a LICENCE_CLAIM_PLACEHOLDER number, KC registration, microchip number, vet health check, and first vaccinations with a worming record."
      }
    }
  ]
}
```

### HowTo Schema (for process content)
Use for: "How to find a reputable blue Staffy breeder," "How to prepare for a new Staffy puppy"

### Breed-specific Entity Schema
```json
{
  "@context": "https://schema.org",
  "@type": "Animal",
  "name": "Staffordshire Bull Terrier",
  "description": "A compact, affectionate terrier breed originating in the English Midlands, bred in the UK under LICENCE_CLAIM_PLACEHOLDER and LEGAL_CLAIM_PLACEHOLDER.",
  "alternateName": ["Blue Staffy", "Blue Staffordshire Bull Terrier", "Staffy", "Staffie"]
}
```

---

## AIO Content Audit

For any page, check:

```bash
# Does every H2 section start with a direct answer sentence?
# Are all entities named (not pronoun-heavy)?
# Do tables exist for size/price/health data?
# Is FAQPage JSON-LD present?
grep -n "FAQPage\|@type.*Question" site/content/[slug]/*.md | head -10
```

### Sentence-Level Checks
- [ ] First sentence of each section states the fact (not "In this section we will discuss...")
- [ ] No hedging language ("might," "could," "possibly") on factual claims
- [ ] "Staffordshire Bull Terrier" always capitalized (entity consistency — not "staffy" or "the dog")
- [ ] Numbers written as numerals (14 kg, 14 years, £1,500 — AI parses numerals better)

---

## GEO Targeting — Specific AI Engines

### Google AIO
- Targets: FAQ schema, structured lists, direct answers
- Avoid: thin content, vague claims, excessive internal repetition

### ChatGPT / Perplexity
- Targets: cited sources (KC registration + vet health check, LICENCE_CLAIM_PLACEHOLDER), specific data points, comparisons
- Note: These engines index from the web — pages must be crawlable

### Claude (Anthropic)
- Targets: well-structured entity-tree content, clear attribution
- Note: Training cutoff varies — evergreen facts more likely to be cited

### GEO Local Targeting
- "blue staffy puppies for sale [city]" — location-specific landing pages under `/uk-locations/<slug>/`
- "buy blue staffy puppy near me" — proximity intent, include Glasgow, Scotland signals
- "blue staffy breeder [region]" — region-level pages with local trust signals

---

## AIO/GEO Content Checklist

- [ ] Every H2 section leads with a direct declarative statement
- [ ] All size/weight/price data in a table or labeled list
- [ ] All health claims attributed to KC registration + vet health check, the vet health certificate, or the LICENCE_CLAIM_PLACEHOLDER
- [ ] FAQPage JSON-LD on every FAQ section
- [ ] No hedging on factual claims
- [ ] Entity names consistent (always "Staffordshire Bull Terrier" not "staffy" or "the dog")
- [ ] Lifespan stated as a range with source ("12–14 years per Kennel Club breed health data")

---

## Featured Snippet Capture Strategies

Use these 4 pattern types to win Google Featured Snippets and position zero. Place snippet-target content within the first 800 words of every page.

### Strategy 1 — "Definition + List" Combo
Many snippets show a definition paragraph AND a list. Structure:
```html
<h2>Who Are the Best Blue Staffy Breeders in [Region]?</h2>
<p>The best blue Staffy breeders in [Region] provide a LICENCE_CLAIM_PLACEHOLDER number,
health screening, and lifetime breeder support. Top breeders demonstrate:</p>
<ol>
  <li>LICENCE_CLAIM_PLACEHOLDER number displayed on every advert</li>
  <li>KC registration paperwork handed over at collection</li>
  <li>Vet health check before transfer</li>
  <li>Hereditary cataracts (HC) and L-2-HGA DNA status on both parents</li>
  <li>LEGAL_CLAIM_PLACEHOLDER compliance — puppy seen with its mother at the breeder's home</li>
  <li>Home-raised puppies with microchip, first vaccinations, and worming records</li>
</ol>
```

### Strategy 2 — "Question in Heading, Answer in First Paragraph"
Works for: Why, What, How, Are, Is, Can, Should questions.
- First paragraph directly answers the H2 question in 40 to 60 words
- Active voice, specific numbers, no hedging
```html
<h2>Why Choose a Blue Staffordshire Bull Terrier Over Other Terrier Breeds?</h2>
<p>Blue Staffordshire Bull Terriers are chosen for their affectionate temperament, manageable
size (11–17 kg), and famously strong bond with children. Unlike larger bull breeds or working
terriers, Staffies settle happily in flats and family homes, need around an hour of daily
exercise, and remain one of the few breeds the Kennel Club describes as thoroughly reliable
with children.</p>
```

### Strategy 3 — Comparison Table Domination
Works for: "[X] vs [Y]", "difference between X and Y", "compare X and Y"
Table requirements: 3–6 columns, 3–8 rows, include numbers/data (not just text), bold Winner column.
```html
<h2>Blue Staffy vs Blue Brindle Staffy: Which Is Right for You?</h2>
<table>
  <tr><th>Feature</th><th>Blue</th><th>Blue / Black Brindle</th><th>Best For</th></tr>
  <tr><td>Adult Size</td><td>11–17 kg, ~36–41 cm</td><td>11–17 kg, ~36–41 cm</td><td>Identical build — choose on coat</td></tr>
  <tr><td>Coat</td><td>Solid grey-blue, shows dirt less</td><td>Striped, hides scuffs and mud</td><td>Show look → blue; low-fuss → brindle</td></tr>
  <tr><td>Price</td><td>£1,500 (Roman, Byrd, Ince)</td><td>£1,700 (Vennie, Christa, Cheryl)</td><td>Both include full paperwork</td></tr>
  <tr><td>Skin Sensitivity</td><td>Dilute coat needs more skin care</td><td>Standard coat, fewer skin issues</td><td>First-time owner → brindle</td></tr>
</table>
```

### Strategy 4 — Step-by-Step Process Capture
Works for: "How to find a reputable blue Staffy breeder", "Steps to prepare for a Staffy puppy"
Format: numbered steps, bold step title + 1–2 sentence explanation.
```html
<h2>How to Choose a Reputable Blue Staffy Breeder: 7 Steps</h2>
<ol>
  <li><strong>Verify the LICENCE_CLAIM_PLACEHOLDER</strong> — Every licensed UK breeder has a LICENCE_CLAIM_PLACEHOLDER number. Ask for it before paying any deposit.</li>
  <li><strong>Confirm LEGAL_CLAIM_PLACEHOLDER compliance</strong> — Ask to see the puppy with its mother at the breeder's home. Refuse any meet-up handover.</li>
  <li><strong>Request hereditary cataracts (HC) and L-2-HGA DNA results</strong> — These conditions are inherited and silent in young puppies. Reputable breeders test both parents.</li>
  <li><strong>Ask for the vet health check</strong> — Confirms the puppy was examined by a licensed veterinary surgeon before transfer.</li>
  <li><strong>Verify KC registration</strong> — Kennel Club papers confirm pedigree and litter registration; check the names match the parents you met.</li>
  <li><strong>Check the microchip number and worming record</strong> — Microchipping is a legal requirement before sale; the number must be registered to the breeder first.</li>
  <li><strong>Contact previous buyers</strong> — Ask the breeder for references; legitimate breeders welcome this.</li>
</ol>
```

### Featured Snippet Checklist (run on every new or rebuilt page)
- [ ] Use exact question as H2 or H3 heading
- [ ] Include target keyword in heading
- [ ] Match the user's search intent perfectly (informational vs. transactional)
- [ ] Answer in first 1–2 sentences (40–50 words)
- [ ] Provide specific numbers, not vague terms ("11–17 kg" not "medium dog")
- [ ] Use active voice and clear language
- [ ] Add supporting details after the main answer
- [ ] For list snippets: use `<ol>` or `<ul>` with 5–10 items
- [ ] For table snippets: proper `<table>` with header row + data cells with numbers
- [ ] Place snippet target content within first 800 words
- [ ] Use FAQPage schema for question-format snippets
- [ ] Page loads < 3 seconds (no render-blocking scripts before snippet content)
- [ ] Mobile-friendly formatting (no horizontal scroll on tables)

---

## Rules

1. **Answer first, always** — first sentence of every section is the answer
2. **Source every claim** — "confirmed by," "per," "according to" + named source
3. **Tables over prose for data** — size, price, health conditions, comparisons
4. **FAQPage schema is non-negotiable** on every FAQ section
5. **No hedging on facts** — "Staffordshire Bull Terriers weigh 11–17 kg" not "Staffordshire Bull Terriers typically weigh around 11–17 kg"
6. **Entity consistency** — same name every time, every page
7. **Featured snippet checklist** — run on every new or rebuilt page before marking complete
