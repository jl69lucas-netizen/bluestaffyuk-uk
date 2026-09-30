---
name: framework-qab
description: "Reference guide for the QAB framework applied to BSUK FAQ sections, price pages, and comparison content. Use whenever writing FAQ items, cost breakdowns, or any content that must answer a buyer's question AND connect the answer to a personal benefit."
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## BSUK Project Context
> **Site:** BlueStaffyUK — home-raised Blue Staffordshire Bull Terrier breeder in Carlisle, Cumbria (Lisa Bright)
> **The litter:** `data/puppies.json` — males Roman, Byrd, Ince at £1,500 · females Vennie, Christa, Cheryl at £1,700. The price follows the sex, not the coat; each pup's coat is its own row's `colour` (blue, blue and white, white, blue with white blaze), and none of the six is brindle
> **Licensing:** LICENCE_CLAIM_PLACEHOLDER and LEGAL_CLAIM_PLACEHOLDER compliance — NOT YET CONFIRMED by Lisa Bright. Never state either as fact, and never imply a puppy-farm or third-party sale.
> **Trust pillars:** LICENCE_CLAIM_PLACEHOLDER · LEGAL_CLAIM_PLACEHOLDER · KC registration · Microchip number · Vet health check · First vaccinations + worming record · Fully weaned + home-raised
> **Buyer fears (ranked):** Scam/fraud · Sick puppy · Missing paperwork · Puppy-farm origin · Post-sale abandonment
> **Pages:** `src/pages/` (built: `dist/`) | **Session docs:** `docs/superpowers/sessions/`
> **Confidence Gate:** ≥97% before writing any site file

## What QAB Is

QAB is BSUK's primary framework for FAQ sections, pricing content, and any "question-and-answer" format. It extends a basic Q&A with a third step — the Benefit — which converts informational readers into buyers.

```
Q — Question:  The exact question the buyer is asking (in their language)
A — Answer:    The direct, specific, factual answer (Inverse Pyramid — answer first)
B — Benefit:   Why this answer matters to the reader's specific situation
```

Without the Benefit, you have a FAQ. With the Benefit, you have a conversion tool.

---

## QAB vs Basic Q&A

```
BASIC Q&A:
Q: How much does a blue Staffy puppy cost?
A: Blue Staffordshire Bull Terrier puppies typically range from £1,500 to £1,700.

QAB:
Q: How much does a blue Staffy puppy cost from a reputable breeder?
A: Blue Staffy puppies from BlueStaffyUK are priced at £1,500–£1,700. This includes 
   KC registration, microchip number, vet health check, first vaccinations, worming record, 
   and a vet-signed health card. A £500 deposit books your viewing and reserves your puppy.
B: Transparent pricing means no surprise paperwork fees after you've already bonded with 
   your puppy — and no "registration add-on" charges at handover.
```

---

## Question Writing Rules

**Write questions in the buyer's exact language:**
- Use "how much" not "what is the price"
- Use "near me" where that's how buyers search
- Use "reputable breeder" because that's the qualifier buyers use
- Use "is a blue Staffy right for me" not "Staffordshire Bull Terrier suitability assessment"

**Question sources (where real buyer language lives):**
- Google People Also Ask for the primary keyword
- Google autocomplete suggestions
- GSC Queries.csv — real queries driving impressions
- Reddit, Quora, Facebook groups (what buyers actually ask)

**Question length:**
- 8–15 words optimal
- Conversational, not formal
- One topic per question (not "how much does a blue Staffy puppy cost and what's included")

---

## Answer Writing Rules

**Lead with the answer, not with context:**
```
Bad:  "When considering the cost of a blue Staffy puppy, there are several factors to consider..."
Good: "Blue Staffy puppies from BlueStaffyUK cost £1,500 (Roman, Byrd, Ince) / £1,700 (Vennie, Christa, Cheryl) depending on the puppy."
```

**Be specific — use real numbers:**
```
Bad:  "Crate costs can vary but are generally affordable."
Good: "Expect to budget for an appropriate crate — a minimum 30" model suits an adult Staffy."
```

**Source the answer:**
- Prices: from `data/puppies.json` and `data/price-matrix.json` — never typed
- Costs: from BSUK pricing data (Phase 2: `data/price-matrix.json`)
- Health: per vet health check / worming and vaccination record
- Breed facts: per Kennel Club breed standard and UK breeding regulations

---

## Benefit Writing Rules

The Benefit is not a repeat of the answer. It's the emotional or practical payoff:

```
Bad Benefit:  "This is why BlueStaffyUK is a great choice." (marketing speak)
Good Benefit: "Knowing your puppy's complete paperwork before handover means your first 
               vet visit is a celebration, not a discovery of missing records."
```

**Benefit types:**
- **Fear-removal:** "...so you never have to worry about hidden fees"
- **Outcome clarity:** "...which means your puppy arrives calm and healthy"
- **Decision confidence:** "...so you can compare breeders with the same standard"
- **Financial:** "...saving you the first-year vet costs a puppy-farm puppy brings — an amount that is NOT FETCHED, so never print one"

---

## QAB Template (HTML ready)

```html
<details class="bsuk-faq-item">
  <summary class="bsuk-faq-question">
    [Question text in buyer's language?]
  </summary>
  <div class="bsuk-faq-answer">
    <p>[Direct answer — specific, sourced, no hedging]</p>
    <p class="bsuk-faq-benefit">[Benefit — why this matters to the reader]</p>
  </div>
</details>
```

---

## QAB for Price Pages

On cost pages, QAB structure is required for every line item:

```
Q: What's included in the blue Staffy puppy price?
A: Every BlueStaffyUK puppy includes: KC registration, microchip number, 
   vet health check, first vaccinations, worming record, 
   and a puppy pack to help them settle in. Price: £1,500 / £1,700 by puppy.
B: Unlike dealers that add paperwork fees after purchase, BlueStaffyUK pricing 
   is all-inclusive — what you see is what you pay.
```

---

## BSUK FAQ Question Bank (pre-built QAB sets)

### Price & Cost
- How much does a blue Staffy puppy cost?
- Why do your male and female puppies cost different amounts?
- What's the deposit to hold a puppy?
- What's included in the purchase price?
- What's the total first-year cost of owning a Staffy?
- Do blue and white puppies cost more than solid blue ones?

### Licensing & Legality
- Are your puppies sold under a LICENCE_CLAIM_PLACEHOLDER?
- Is it legal to buy a Staffy puppy this way in the UK?
- What paperwork do I receive with my puppy?
- What is LEGAL_CLAIM_PLACEHOLDER and why does it matter?
- Can I see the puppy with its mother before buying?

### Health & Documentation
- What health conditions do Staffordshire Bull Terriers have?
- What does an L-2-HGA DNA result confirm?
- What are hereditary cataracts (HC) and do you test for them?
- What does the vet health check cover?
- What is a microchip number and KC registration?

### Buying Process
- How do I reserve a blue Staffy puppy?
- Is puppy delivery safe?
- How does UK-wide puppy delivery work?
- Can I visit in person to meet the puppy before purchasing?
- What if the puppy gets sick after I bring them home?

### Breed & Coat Colours
- What's the difference between a blue and a blue brindle Staffy?
- Are Staffies good with children?
- How long do Staffordshire Bull Terriers live?
- Are Staffies good for first-time owners?
- How much exercise does a Staffy need?

---

## Minimum QAB Requirements Per Page

| Page Type | Min FAQ Items | Framework |
|-----------|-------------|-----------|
| Homepage | 6 | QAB |
| Location pages | 6 | QAB |
| Blue Staffy for sale page | 8 | QAB |
| Staffy puppies for sale page | 8 | QAB |
| Price/cost page | 8 | QAB |
| Comparison pages | 6 | QAB |
| Care guide | 10 | QAB |
| Licensing/documentation guide | 8 | QAB |

---

## Rules

1. **Benefit is required** — a Q&A without a Benefit is incomplete QAB
2. **Questions in buyer's language** — not marketing language
3. **Answer leads with the fact** — Inverse Pyramid inside the A
4. **Numbers from data files** — read `data/settings.json`, `data/puppies.json` and `data/price-matrix.json`
5. **FAQPage JSON-LD required** — every QAB FAQ section needs schema
6. **No generic benefits** — "this is why BlueStaffyUK is great" is not a benefit
