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

For every entity mention on a BSUK page:
1. **Entity** — name the thing: "a full veterinary health check"
2. **Benefit** — what it does: "every puppy is examined by a vet, given its first vaccination, microchipped, wormed and treated for fleas before it goes home" (`data/faq.json` `health-vaccinations`)
3. **Purpose** — why it matters to buyer: "so your own vet starts from a vet-signed health card, not a promise"

**Without EBP (weak):** "We do health checks."
**With EBP (strong):** "Every puppy has a full veterinary health check before it goes home, and it all goes on a vet-signed health card that travels with the puppy — so your own vet starts from a written record."

---

## Complete Entity Catalog

### Category 1 — Breed Entities

| Primary Entity | Variations | Where to Use |
|---------------|-----------|-------------|
| Blue Staffy puppy | Blue Staffy, puppy, home-bred | H1, H2, opening paragraphs, CTAs |
| Blue Staffy | Blue, BSUK | Variant sections, H2, breed guide |
| Coat colour | blue, blue and white, white, blue with white blaze — each pup's `colour` in `data/puppies.json` (none is brindle) | Puppy cards, puppy pages, alt text |
| Canis lupus familiaris | Scientific name, canine nomenclature | Breed guide, scientific sections |
| Home-bred | Domestically bred | Trust bar, credentials |
| Home-raised | Home-reared, socialized, behavioral training | Care sections, about page |
| Lifetime breeder support | Ongoing breeder relationship, lifetime advisory | Trust, FAQ |

### Category 2 — Health & Credential Entities

| Primary Entity | Variations | Where to Use |
|---------------|-----------|-------------|
| Veterinary health check | full vet health check, vet-signed health card, first vaccinations, microchip, worming and flea treatment (`data/faq.json` `puppy-package`) | Health sections, credentials, FAQ |
| L-2-HGA and HC-HSF4 DNA tests | the parents' DNA tests (results `NOT FETCHED` — `data/quality/evidence-ledger.json` `parents-dna-clear`) | Health sections, FAQ |
| Canine vet health certificate | Canine veterinarian certification, health exam | Health sections, trust bar |
| LICENCE_CLAIM_PLACEHOLDER license | LICENCE_CLAIM_PLACEHOLDER-licensed breeder, LICENCE_CLAIM_PLACEHOLDER inspection | Trust bar, about page |
| LICENCE_CLAIM_PLACEHOLDER documentation | LICENCE_CLAIM_PLACEHOLDER permit, home-bred certificate | Credentials, legal compliance |
| Behavioral socialization | Home-raised, taming, training | Care sections, about |
| Nutritional support | Breed-appropriate diet, puppy nutrition | Care guide, FAQ |
| Lifetime advisory | Ongoing breeder mentorship, lifetime support | Trust, FAQ |
| Canine welfare standards | Dog welfare, ethical breeding | Trust, credentials |

### Category 3 — Location Entities

| Primary Entity | Variations | Where to Use |
|---------------|-----------|-------------|
| [BREEDER_LOCATION] | [LOCATION], [REGION] | About, location, schema |
| BlueStaffyUK | BSUK, BSUK breeder, breeding program | Brand mentions, footer, schema |
| [BREEDER_NAME] | Breeder, owner, founder | About, testimonials, Person schema |
| delivery by DEFRA-approved transport | DEFRA-approved transport, road delivery priced by distance (£200–£350) | Location pages, hero |
| Nationwide delivery | UK home delivery to the 28 cities in `data/locations.json`, collection from Carlisle | Hero, location hub |

### Category 4 — Pricing Entities

| Primary Entity | Variations | Where to Use |
|---------------|-----------|-------------|
| Blue Staffy puppy price | Blue Staffy puppy cost, Blue Staffy price range | Price page, FAQ |
| £1,500 | a male puppy (Roman, Byrd, Ince) — `data/price-matrix.json` `male_gbp` | Price sections, puppy cards |
| £1,700 | a female puppy (Vennie, Christa, Cheryl) — `data/price-matrix.json` `female_gbp` | Price sections, puppy cards |
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
for entity in "Blue Staffy puppy" "Blue Staffy" "Staffordshire Bull Terrier" "health check" "canine vet" "LICENCE_CLAIM_PLACEHOLDER" "lifetime support" "home-bred"; do
  count=$(grep -oi "$entity" dist/[slug]/index.html | wc -l)
  echo "$count × $entity"
done
```

### Entity Density Targets

| Page Type | Must-Have Entities | Target Mentions Each |
|-----------|-------------------|---------------------|
| Homepage | Blue Staffy puppy, DNA, vet health check, Carlisle | 5–8 |
| Location page | Blue Staffy puppy, [city], DEFRA-approved transport, vet health check | 3–5 |
| Breed guide | Blue Staffy, Staffordshire Bull Terrier, DNA, LICENCE_CLAIM_PLACEHOLDER, canine vet | 6–10 |
| Comparison page | Both breed entities + 3–5 differentiators | 4–6 |
| Price page | Price entities, vet health check, DNA, all-inclusive | 5–8 |

---

## Rules

1. **EBP on every entity mention** — entity without benefit is a wasted mention
2. **Native schema management** — use grep/python approach directly (handles multiple schema blocks correctly)
3. **Extract FAQ schema from `<details>/<summary>`** — not raw page HTML
4. **Density cap** — no single entity above 2% of total word count
5. **Location entities on all location pages** — the city, its region and its nearby cities from `data/locations.json` always present; never a mileage or a drive time
6. **Credential entities in first 300 words** — veterinary health check, the parents' L-2-HGA and HC-HSF4 DNA tests, LICENCE_CLAIM_PLACEHOLDER appear early
7. **Cross-reference price-matrix.json** — all pricing entities match the data file

See also: `bsuk-competitor-parity` — match competitors type by type, close 2+-domain gaps, beat them on evidence from data.
