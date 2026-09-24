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
> **Site:** BlueStaffyUK — home-raised Blue Staffordshire Bull Terrier breeder in Carlisle, Cumbria (Lisa Bright)
> **The litter:** `data/puppies.json` — males Roman, Byrd, Ince at £1,500 · females Vennie, Christa, Cheryl at £1,700. The price follows the sex, not the coat; each pup's coat is its own row's `colour` (blue, blue and white, white, blue with white blaze), and none of the six is brindle
> **Licensing:** LICENCE_CLAIM_PLACEHOLDER and LEGAL_CLAIM_PLACEHOLDER compliance — NOT YET CONFIRMED by Lisa Bright. Never state either as fact, and never imply a puppy-farm or third-party sale.
> **Trust pillars:** LICENCE_CLAIM_PLACEHOLDER · LEGAL_CLAIM_PLACEHOLDER · KC registration · Microchip number · Vet health check · First vaccinations + worming record · Fully weaned + home-raised
> **Buyer fears (ranked):** Scam/unlicensed seller · Sick puppy · Puppy-farm origin · Missing paperwork · No post-sale support
> **Pages:** `src/pages/` (built: `dist/`) | **Session docs:** `docs/superpowers/sessions/`
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
- Sellers who claim a licence and quote an invented licence number
- Facebook Marketplace listings with stock photos and bank-transfer deposit requests
- Sites that say "home-raised" with no paperwork to show
- "Cheap blue staffy" sites with no LICENCE_CLAIM_PLACEHOLDER, no vet check, no recourse

EBP converts vague claims into verifiable proof. "All our puppies are documented" becomes "LICENCE_CLAIM_PLACEHOLDER #[NUMBER] — verifiable with the local licensing authority."

---

## EBP Evidence Sources for BSUK

| Claim | Evidence Source | How to Cite |
|-------|---------------|-------------|
| Legally sold | LEGAL_CLAIM_PLACEHOLDER compliance | "LEGAL_CLAIM_PLACEHOLDER compliant — puppy seen with its mother at our Carlisle home" |
| Licensed breeder | LICENCE_CLAIM_PLACEHOLDER | "LICENCE_CLAIM_PLACEHOLDER #[NUMBER] — verifiable at the issuing council's register" |
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
[Claim]: Staffordshire Bull Terriers from BlueStaffyUK are bred under a LICENCE_CLAIM_PLACEHOLDER.
[Evidence]: Licence issued by the local licensing authority under UK animal-activity licensing rules. Licence number
            available before any deposit is sent. Verifiable independently with the council.
[Profile]: Every puppy leaves with KC registration, microchip number, vet health check, first vaccinations,
           and a worming record. No buyer has ever had a paperwork problem at their first vet visit.
```

### Full EBP Section (for health/trust pages)
```html
<div class="bsuk-ebp-block">
  <h3>Documentation — The Paperwork Behind Every BlueStaffyUK Puppy</h3>

  <div class="bsuk-ebp-item">
    <strong>LICENCE_CLAIM_PLACEHOLDER</strong>
    <p>Every blue Staffordshire Bull Terrier puppy from BlueStaffyUK is bred under
       LICENCE_CLAIM_PLACEHOLDER — the breeder's verifiable legal standing, issued by an
       outside authority rather than self-reported.
       Licence number available before any deposit is sent.</p>
    <p class="bsuk-evidence-note">Evidence: LICENCE_CLAIM_PLACEHOLDER number supplied with every puppy.
       Verifiable independently at the issuing council's register.</p>
  </div>

  <div class="bsuk-ebp-item">
    <strong>Vet Health Check</strong>
    <p>The dam and every puppy receive a health check from a licensed veterinary surgeon,
       along with first vaccinations and a worming record. This is the same standard required
       for a responsible transfer under LEGAL_CLAIM_PLACEHOLDER.</p>
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
Evidence: First-year vet costs are NOT FETCHED — quote a figure only when the breeder or a vet supplies one
          (routine care only). First-year vet costs for undocumented puppies
          are NOT FETCHED (illness + re-vaccination + paperwork issues).
          Source: BSUK owner survey data.
Profile:  The £1,500 (male) / £1,700 (female) price is the locked fact; vet costs are NOT FETCHED. A breeder who can show paperwork (LICENCE_CLAIM_PLACEHOLDER) is
          KC-registered puppy with full paperwork from day one. £500 deposit, refundable.
```

---

## EBP vs Assertion — Side-by-Side

| Assertion (weak) | EBP (strong) |
|-----------------|-------------|
| "All our puppies are legal" | "LICENCE_CLAIM_PLACEHOLDER #[NUMBER] — verifiable at the issuing council's register" |
| "Our puppies are health tested" | "Vet health check — [VET_NAME], certificate included" |
| "KC registered" | "Kennel Club registration — [KC_NUMBER], papers at collection" |
| "Home-raised from birth" | "Socialisation log from day 1 — available on request" |
| "We've been breeding for X years" | "LICENCE_CLAIM_PLACEHOLDER #[NUMBER], breeding since [YEAR]" |
| "Health guaranteed" | "Health guarantee — full terms at [link]" |

---

## EBP Audit

```bash
# Find pages with unverified claims
grep -n "we guarantee\|health tested\|best\|top\|premier\|reputable\|home-raised" dist/[slug]/index.html | head -20
# For each match: is there a named evidence source within 2 sentences?
```

---

## Rules

1. **Every claim gets evidence** — no claim stands without a named source
2. **Name the source specifically** — "LICENCE_CLAIM_PLACEHOLDER" not "documentation"
3. **Baseline matters** — show what the evidence standard means (LICENCE_CLAIM_PLACEHOLDER, LEGAL_CLAIM_PLACEHOLDER, KC registration)
4. **Profile shows BSUK exceeding baseline** — don't just meet the standard, show how BSUK leads
5. **Evidence must be verifiable** — LICENCE_CLAIM_PLACEHOLDER number, KC registration number, microchip number, vet certificate
6. **No unverifiable superlatives** — "best," "top," "premier" require external evidence to cite
