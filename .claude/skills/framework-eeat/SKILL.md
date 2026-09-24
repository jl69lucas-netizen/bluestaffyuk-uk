---
name: framework-eeat
description: "Reference guide for Google's E-E-A-T framework applied to BSUK content. Use when auditing or building any page that must signal credibility to Google's quality raters and AI systems. Covers on-page signals, schema, licensing compliance framing, and author attribution."
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## BSUK Project Context
> **Site:** BlueStaffyUK — home-raised Blue Staffordshire Bull Terrier breeder in Carlisle, Cumbria
> **Coat colours:** blue and blue brindle (Roman, Byrd, Ince — £1,500) · black brindle and rarer blue lines (Vennie, Christa, Cheryl — £1,700) — treat as distinct product lines
> **Licensing:** LICENCE_CLAIM_PLACEHOLDER and LEGAL_CLAIM_PLACEHOLDER compliance — NOT YET CONFIRMED by Lisa Bright. Never state either as fact, and never imply a puppy-farm or third-party sale.
> **Trust pillars:** LICENCE_CLAIM_PLACEHOLDER · LEGAL_CLAIM_PLACEHOLDER · KC registration · Microchip number · Vet health check · First vaccinations + worming record · Fully weaned + home-raised
> **Buyer fears (ranked):** Scam/unlicensed seller · Sick puppy · Puppy-farm origin · Missing paperwork · No post-sale support
> **Pages:** `src/pages/` (built: `dist/`) | **Session docs:** `docs/superpowers/sessions/`
> **Confidence Gate:** ≥97% before writing any site file

---

## What E-E-A-T Is

E-E-A-T is Google's quality framework used by human quality raters and increasingly baked into ranking signals. For YMYL (Your Money or Your Life) topics — including puppy purchases — E-E-A-T signals are heavily weighted.

```
E — Experience:      First-hand experience with the topic
E — Expertise:       Subject matter knowledge and credentials
A — Authoritativeness: Recognition by peers and industry
T — Trustworthiness:  Accuracy, transparency, and safety
```

BlueStaffyUK is a YMYL site (buying a living animal is a significant decision). Every page must signal all four dimensions.

---

## BSUK E-E-A-T Assets

### Experience Signals (first-hand, lived)
- Lisa Bright: [X]+ years breeding Staffordshire Bull Terriers at home
- [N]+ families served — named in testimonials
- Specific litter stories, whelping observations, home-raising notes
- Carlisle, Cumbria (specific, verifiable)
- Blue vs blue brindle vs black brindle breeding distinctions from direct experience

### Expertise Signals (knowledge, credentials)
- LICENCE_CLAIM_PLACEHOLDER — include licence number where possible
- LEGAL_CLAIM_PLACEHOLDER compliance — mum always seen with the pups at our Carlisle home
- KC registration paperwork — names the registered kennel and litter
- Vet health check — names the vet practice and vet
- Home-raising and socialisation protocol — documented from birth
- Microchip number recorded per puppy — verifiable before collection

### Authoritativeness Signals (external recognition)
- Customer testimonials with full names and UK regions
- LICENCE_CLAIM_PLACEHOLDER (local-authority recognition of a licensed breeder)
- Local-authority and national regulatory compliance documentation (LEGAL_CLAIM_PLACEHOLDER)
- Links from credible canine sources (The Kennel Club, Staffordshire Bull Terrier Club, RSPCA)

### Trustworthiness Signals (accuracy, transparency)
- Prices shown openly on pages (no "DM for price")
- Licence and paperwork available to buyers (not just claimed)
- Vet health checks included with every puppy
- Microchip number and worming record included with every puppy
- KC registration and first vaccinations for each puppy
- Real contact info: phone, email, physical address
- Privacy policy and terms pages exist

---

## On-Page E-E-A-T Implementation

### Author Attribution
Every content-heavy page should name the source of expertise:

```html
<div class="bsuk-author-block">
  <p class="bsuk-body">
    <strong>Written by Lisa Bright,</strong> Blue Staffy breeder (LICENCE_CLAIM_PLACEHOLDER) 
    in Carlisle, Cumbria. Specialising in home-raised blue and blue brindle Staffordshire Bull 
    Terriers with full KC registration and health paperwork.
  </p>
</div>
```

### Experience Signals in Body Copy
Replace: "Staffordshire Bull Terriers are loyal dogs."
With: "In our years of breeding, we've placed Blue Staffy puppies with hundreds of families — and the home-raising and socialisation protocol we've developed from birth consistently produces dogs that are confident, bonded, and ready for their new homes."

### Schema for E-E-A-T

**Person schema** (for Lisa Bright):
// Requires @context and <script type="application/ld+json"> wrapper
```json
{
  "@type": "Person",
  "name": "Lisa Bright",
  "jobTitle": "Licensed Blue Staffordshire Bull Terrier Breeder",
  "worksFor": { "@type": "Organization", "name": "BlueStaffyUK" },
  "address": { "@type": "PostalAddress", "addressLocality": "Carlisle" }
}
```

**LocalBusiness schema** (in footer, on contact page):
// Requires @context and <script type="application/ld+json"> wrapper
```json
{
  "@type": "LocalBusiness",
  "name": "BlueStaffyUK",
  "founder": "Lisa Bright",
  "address": { "addressLocality": "Carlisle" },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "[RATING]",
    "reviewCount": "[COUNT]"
  }
}
```

---

## Licensing E-E-A-T — The BSUK Differentiator

Blue Staffy puppies sit in the most scam-heavy corner of the UK pet market. That makes the breeder's verifiable legal standing (LICENCE_CLAIM_PLACEHOLDER, and LEGAL_CLAIM_PLACEHOLDER compliance) the single strongest E-E-A-T signal available to BSUK, because:

1. **No competitor uses it.** The gap matrix shows only a handful of marketplace listings quote a LICENCE_CLAIM_PLACEHOLDER number. Every other Tier 1 breeder site is silent.
2. **It is externally verifiable.** LICENCE_CLAIM_PLACEHOLDER is issued by an outside authority — not self-reported.
3. **It addresses the buyer's deepest fear.** Puppy-farm origin and deposit scams are the defining fears of the UK puppy market, with no equivalent in ordinary retail.

### Licensing Trust Language (use on every page)
```html
<div class="bsuk-trust-bar">
  <span>LICENCE_CLAIM_PLACEHOLDER</span>
  <span>LEGAL_CLAIM_PLACEHOLDER Compliant — Mum Seen With Pups</span>
  <span>KC Registered</span>
  <span>Vet Health Checked</span>
</div>
```

### Licensing in Body Copy
Replace: "All our puppies are legal and documented."
With: "Every puppy comes with LICENCE_CLAIM_PLACEHOLDER number and LEGAL_CLAIM_PLACEHOLDER compliance — the breeder's verifiable legal standing, which you can check with the issuing authority directly. No BlueStaffyUK buyer has ever been sold a puppy sight-unseen, because every placement starts with viewing the litter with its mother at our home."

---

## E-E-A-T Audit Checklist

For any page audit, score each dimension 1–5 (total range: 4–20):

### Experience (1–5)
- [ ] First-person voice ("we've seen," "in our experience whelping")
- [ ] Specific timeframes and numbers ("in [year], we changed our weaning routine because...")
- [ ] Real observations ("blue brindle pups need more intensive handling in weeks 4–8")

### Expertise (1–5)
- [ ] Credentials named (LICENCE_CLAIM_PLACEHOLDER, LEGAL_CLAIM_PLACEHOLDER, KC registration, vet practice)
- [ ] Technical terms used correctly (litter, hereditary cataracts, L-2-HGA, hip score)
- [ ] Data cited with sources ("per The Kennel Club Assured Breeder requirements")

### Authoritativeness (1–5)
- [ ] Testimonials with full names and UK regions
- [ ] LICENCE_CLAIM_PLACEHOLDER number or KC registration reference
- [ ] External links to verifiable sources (the local licensing authority, vet practice, The Kennel Club)

### Trustworthiness (1–5)
- [ ] Contact info visible (not just a form)
- [ ] Prices stated openly
- [ ] Paperwork described specifically (not just "fully documented")
- [ ] Health check terms specific (vet name, date, conditions checked)
- [ ] Licensing language present on every page
- [ ] LEGAL_CLAIM_PLACEHOLDER / view-with-mum statement visible on listing pages
- [ ] No unverifiable superlatives ("best," "#1," "top-rated")

**Score 16–20:** Strong E-E-A-T — maintain
**Score 10–15:** Needs improvement — add experience/expertise signals
**Score < 10:** Urgent — Google quality raters would flag this page

---

## Common E-E-A-T Failures at BSUK

| Failure | Fix |
|---------|-----|
| "All our puppies are legal" (vague) | "LICENCE_CLAIM_PLACEHOLDER — number available on request" |
| "Health tested" (unverified) | "Vet health check — [VET_NAME], certificate included with the puppy" |
| No author name on content | Add Lisa Bright author block |
| Prices hidden ("contact us") | Show prices openly (£1,500 Roman, Byrd, Ince; £1,700 Vennie, Christa, Cheryl) |
| Generic testimonials | Name + UK region + specific outcome |
| "Our puppies are home-raised" | "Home-raised under LEGAL_CLAIM_PLACEHOLDER — mum viewable with the litter at our Carlisle home" |

---

## Rules

1. **Every claim needs a source** — KC registration, vet health check, microchip record, LICENCE_CLAIM_PLACEHOLDER, or BSUK internal data
2. **First-person experience in every major section** — not just the About page
3. **Schema required** — Person and LocalBusiness on every key page
4. **No unverifiable superlatives** — "best" requires external evidence
5. **Contact info must be real and visible** — not just a form
