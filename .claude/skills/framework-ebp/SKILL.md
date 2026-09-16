---
name: framework-ebp
description: "Reference guide for the EBP framework applied to BSUK breeder credibility sections, licensing and paperwork explanations, and any content that must prove a claim with named evidence. Use when building trust sections that must survive skeptical scrutiny."
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## BSUK Project Context
> **Site:** BlueStaffyUK — licensed Blue Staffordshire Bull Terrier breeder, Glasgow
> **Coat colours:** Blue (Roman, Byrd, Ince — £1,500) · Blue brindle / black brindle (Vennie, Christa, Cheryl — £1,700) — treat as distinct product lines
> **Licensing:** Staffordshire Bull Terriers are bred here under a Glasgow City Council breeder licence with full Lucy's Law compliance — every puppy is seen with its mother at our home. Never imply puppy-farm or third-party sale.
> **Trust pillars:** Glasgow City Council breeder licence · Lucy's Law compliant · KC registration · Microchipped · Vet health check · First vaccinations + worming · Fully weaned + home-raised
> **Buyer fears (ranked):** Scam/unlicensed seller · Sick puppy · Puppy-farm origin · Missing paperwork · No post-sale support
> **Content root:** `site/content/` | **Sessions:** `sessions/`
> **Confidence Gate:** ≥97% before writing any site file

## What EBP Is

EBP is the framework for building credibility through evidence — not assertion. Every claim must be followed immediately by the named evidence that supports it. No claim stands alone.

```
E — Evidence:  Name the specific proof source
B — Baseline:  State what the evidence proves
P — Profile:   Show how BSUK meets or exceeds the baseline
```

The pattern: Claim → Evidence → What it means for the buyer.

---

## Why BSUK Needs EBP

BSUK operates in a trust-scarce market. Blue Staffy buyers have been burned by:
- Sellers who say "licensed breeder" with an invented licence number
- Facebook Marketplace listings with stock photos and bank-transfer deposit requests
- Sites that say "home-raised" with no paperwork to show
- "Cheap blue staffy" sites with no council licence, no vet check, no recourse

EBP converts vague claims into verifiable proof. "All our puppies are documented" becomes "Glasgow City Council breeder licence #[NUMBER] — verifiable with Glasgow City Council."

---

## EBP Evidence Sources for BSUK

| Claim | Evidence Source | How to Cite |
|-------|---------------|-------------|
| Legally sold | Lucy's Law compliance | "Lucy's Law compliant — puppy seen with its mother at our Glasgow home" |
| Licensed breeder | Glasgow City Council breeder licence | "Glasgow City Council breeder licence #[NUMBER] — verifiable at glasgow.gov.uk" |
| Pedigree verified | KC registration | "Kennel Club registration — [KC_NUMBER], papers handed over at collection" |
| Health tested | Vet health check | "Vet health check — [VET_NAME], issued on [date]" |
| Home-raised | Socialisation log | "Socialisation log from birth — documented week by week" |
| Identity verified | Microchip number | "Microchip #[NUMBER] — registered to the breeder, transferable to you" |
| Lifespan claim | Kennel Club breed health data | "12–14 years per Staffordshire Bull Terrier longevity surveys" |
| Hereditary health | HC and L-2-HGA DNA status | "Both parents DNA clear for HC and L-2-HGA — certificates on request" |

---

## EBP Section Structure

### Basic EBP Block (for inline credibility)
```
[Claim]: Staffordshire Bull Terriers from BlueStaffyUK are bred under a Glasgow City Council breeder licence.
[Evidence]: Licence issued by Glasgow City Council under UK animal-activity licensing rules. Licence number
            available before any deposit is sent. Verifiable independently with the council.
[Profile]: Every puppy leaves with KC registration, microchip number, vet health check, first vaccinations,
           and a worming record. No buyer has ever had a paperwork problem at their first vet visit.
```

### Full EBP Section (for health/trust pages)
```html
<div class="bsuk-ebp-block">
  <h3>Documentation — What "Licensed Breeder" Actually Means at BlueStaffyUK</h3>

  <div class="bsuk-ebp-item">
    <strong>Glasgow City Council Breeder Licence</strong>
    <p>Every blue Staffordshire Bull Terrier puppy from BlueStaffyUK is bred under a Glasgow
       City Council breeder licence. This licence is issued by the local authority and is
       required by law for anyone breeding and selling puppies in Scotland.
       Licence number available before any deposit is sent.</p>
    <p class="bsuk-evidence-note">Evidence: Glasgow City Council breeder licence number supplied with every puppy.
       Verifiable independently at glasgow.gov.uk.</p>
  </div>

  <div class="bsuk-ebp-item">
    <strong>Vet Health Check</strong>
    <p>The dam and every puppy receive a health check from a licensed veterinary surgeon,
       along with first vaccinations and a worming record. This is the same standard required
       for a responsible transfer under Lucy's Law.</p>
    <p class="bsuk-evidence-note">Evidence: Vet health check — [VET_NAME],
       certificate included with puppy.</p>
  </div>
</div>
```

---

## EBP for Pricing Claims

Pricing transparency is also evidence-based:

```
Claim:    "BlueStaffyUK puppies cost less than a pet-shop or unlicensed puppy over a lifetime."
Evidence: First-year vet costs for health-checked, vaccinated puppies average £300–£500
          (routine care only). First-year vet costs for undocumented puppies
          average £1,200–£2,800 (illness + re-vaccination + paperwork issues).
          Source: BSUK owner survey data.
Profile:  The £1,500 (blue) / £1,700 (blue or black brindle) price + £300–£500 vet = a licensed,
          KC-registered puppy with full paperwork from day one. £500 deposit, refundable.
```

---

## EBP vs Assertion — Side-by-Side

| Assertion (weak) | EBP (strong) |
|-----------------|-------------|
| "All our puppies are legal" | "Glasgow City Council breeder licence #[NUMBER] — verifiable at glasgow.gov.uk" |
| "Our puppies are health tested" | "Vet health check — [VET_NAME], certificate included" |
| "KC registered" | "Kennel Club registration — [KC_NUMBER], papers at collection" |
| "Home-raised from birth" | "Socialisation log from day 1 — available on request" |
| "We've been breeding for X years" | "Glasgow City Council breeder licence #[NUMBER], breeding since [YEAR]" |
| "Health guaranteed" | "Health guarantee — full terms at [link]" |

---

## EBP Audit

```bash
# Find pages with unverified claims
grep -n "we guarantee\|health tested\|best\|top\|premier\|reputable\|home-raised" site/content/[slug]/*.md | head -20
# For each match: is there a named evidence source within 2 sentences?
```

---

## Rules

1. **Every claim gets evidence** — no claim stands without a named source
2. **Name the source specifically** — "Glasgow City Council breeder licence" not "documentation"
3. **Baseline matters** — show what the evidence standard means (council licence, Lucy's Law, KC registration)
4. **Profile shows BSUK exceeding baseline** — don't just meet the standard, show how BSUK leads
5. **Evidence must be verifiable** — council licence number, KC registration number, microchip number, vet certificate
6. **No unverifiable superlatives** — "best," "top," "premier" require external evidence to cite
