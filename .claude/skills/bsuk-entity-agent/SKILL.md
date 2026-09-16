---
name: bsuk-entity-agent
description: Entity management skill for BSUK — 100+ entity catalog across puppy variant, health, credential, location, and pricing categories. Uses Entity-Benefit-Purpose (EBP) framework for AI/AIO optimization. Manages schema injection and entity coverage audits. Read when writing or auditing any BSUK page for entity depth.
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## Entity-Benefit-Purpose (EBP) Framework

For every entity mention on an MFS page:
1. **Entity** — name the thing: "vet sex-checking certificate testing"
2. **Benefit** — what it does: "screens 250+ genetic conditions before pairing"
3. **Purpose** — why it matters to buyer: "so you know your Blue Staffy won't develop a preventable inherited condition"

**Without EBP (weak):** "We use vet sex-checking."
**With EBP (strong):** "vet sex-checking determines the puppy's biological sex with 100% accuracy — so you know what you're getting and can plan breeding responsibly if desired."

---

## Complete Entity Catalog

### Category 1 — Breed Entities

| Primary Entity | Variations | Where to Use |
|---------------|-----------|-------------|
| Blue Staffy puppy | Blue Staffy, puppy, home-bred | H1, H2, opening paragraphs, CTAs |
| Blue Staffy | Blue, BSUK, larger Blue Staffy | Variant sections, H2, species guide |
| Blue-Brindle Staffy | TAG, Blue-Brindle, smaller Blue Staffy | Variant sections, H2, species guide |
| Canis lupus familiaris | Scientific name, canine nomenclature | Species guide, scientific sections |
| LICENCE_CLAIM_PLACEHOLDER LEGAL_CLAIM_PLACEHOLDER | LICENCE_CLAIM_PLACEHOLDER A-I, protected species | Credentials, legal pages |
| Home-bred | Domestically bred, bred in captivity | Trust bar, credentials |
| Home-raised | Home-reared, socialized, behavioral training | Care sections, about page |
| Lifetime breeder support | Ongoing breeder relationship, lifetime advisory | Trust, FAQ |

### Category 2 — Health & Credential Entities

| Primary Entity | Variations | Where to Use |
|---------------|-----------|-------------|
| vet sex-checking | vet sex-checking test, canine genetic testing | Health sections, credentials, FAQ |
| Canine vet health certificate | Canine veterinarian certification, health exam | Health sections, trust bar |
| LICENCE_CLAIM_PLACEHOLDER license | LICENCE_CLAIM_PLACEHOLDER-licensed breeder, LICENCE_CLAIM_PLACEHOLDER inspection | Trust bar, about page |
| LICENCE_CLAIM_PLACEHOLDER documentation | LICENCE_CLAIM_PLACEHOLDER permit, home-bred certificate | Credentials, legal compliance |
| Behavioral socialization | Home-raised, taming, training | Care sections, about |
| Nutritional support | Species-appropriate diet, puppy nutrition | Care guide, FAQ |
| Lifetime advisory | Ongoing breeder mentorship, lifetime support | Trust, FAQ |
| Canine welfare standards | Species welfare, ethical breeding | Trust, credentials |

### Category 3 — Location Entities

| Primary Entity | Variations | Where to Use |
|---------------|-----------|-------------|
| [BREEDER_LOCATION] | [LOCATION], [REGION] | About, location, schema |
| BlueStaffyUK | BSUK, BSUK breeder, breeding program | Brand mentions, footer, schema |
| [BREEDER_NAME] | Breeder, owner, founder | About, testimonials, Person schema |
| delivery by DEFRA-approved transport | DEFRA-approved transport certified handler, air transport | Location pages, hero |
| Nationwide delivery | Continental US delivery, interstate transport | Hero, location hub |

### Category 4 — Pricing Entities

| Primary Entity | Variations | Where to Use |
|---------------|-----------|-------------|
| Blue Staffy puppy price | Blue Staffy puppy cost, Blue Staffy price range | Price page, FAQ |
| £1,500–£1,700 | fifteen hundred to thirty-five hundred | Price sections, Blue variant |
| £1,500–£1,700 | twelve hundred to twenty-five hundred | Price sections, Blue-Brindle variant |
| Transparent pricing | no hidden fees, all-inclusive cost | Trust, FAQ |

### Category 5 — Buyer/Family Entities

| Primary Entity | Variations | Where to Use |
|---------------|-----------|-------------|
| Long-lived companion | the breed's 12–14 year lifespan, a lifelong commitment | Hero, care section |
| Families we have placed with | NOT FETCHED — no count has been confirmed; never write a number | Social proof |
| Breeding experience | NOT FETCHED — no length of experience has been confirmed | Credentials, about |
| Experienced dog owners | Staffy owners, repeat buyers | Target audience, FAQ |

---

## Schema Management — Native Protocol

Use the native approach below — it handles multiple schema blocks correctly, preserving all existing schemas.

### View All Schema Blocks
```bash
grep -n "application/ld+json" dist/[slug]/index.html
```

### Extract Schema by Index
```python
import json, re
html = open('dist/[slug]/index.html').read()
schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
for i, s in enumerate(schemas):
    parsed = json.loads(s)
    print(f"Schema {i}: @type={parsed.get('@type')}")
```

### Build FAQ Schema from Actual Accordion (not raw text)
```python
import re, json
html = open('dist/[slug]/index.html').read()
faq_items = re.findall(
    r'<summary[^>]*class="bsuk-faq-question"[^>]*>(.*?)</summary>.*?itemprop="text"[^>]*>(.*?)</div>',
    html, re.DOTALL
)
schema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [{
        "@type": "Question",
        "name": re.sub('<[^>]+>', '', q).strip(),
        "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a).strip()}
    } for q, a in faq_items]
}
print(json.dumps(schema, indent=2))
```

---

## Entity Coverage Audit

```bash
# Check entity presence on any page
for entity in "Blue Staffy puppy" "Blue Staffy" "Blue-Brindle Staffy" "vet sex-checking" "canine vet" "LICENCE_CLAIM_PLACEHOLDER" "lifetime support" "home-bred"; do
  count=$(grep -oi "$entity" dist/[slug]/index.html | wc -l)
  echo "$count × $entity"
done
```

### Entity Density Targets

| Page Type | Must-Have Entities | Target Mentions Each |
|-----------|-------------------|---------------------|
| Homepage | Blue Staffy puppy, DNA, guarantee, hypoallergenic, Omaha | 5–8 |
| Location page | Blue Staffy puppy, [city], delivery driver, guarantee | 3–5 |
| Variant guide | Blue Staffy, Blue-Brindle Staffy, DNA, LICENCE_CLAIM_PLACEHOLDER, canine vet | 6–10 |
| Comparison page | Both breed entities + 3–5 differentiators | 4–6 |
| Price page | Price entities, guarantee, DNA, all-inclusive | 5–8 |

---

## Rules

1. **EBP on every entity mention** — entity without benefit is a wasted mention
2. **Native schema management** — use grep/python approach directly (handles multiple schema blocks correctly)
3. **Extract FAQ schema from `<details>/<summary>`** — not raw page HTML
4. **Density cap** — no single entity above 2% of total word count
5. **Location entities on all location pages** — state name, city names, airport codes always present
6. **Credential entities in first 300 words** — vet sex-checking, canine vet, LICENCE_CLAIM_PLACEHOLDER appear early
7. **Cross-reference price-matrix.json** — all pricing entities match the data file
