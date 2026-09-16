---
name: framework-aida
description: "Reference guide for the AIDA framework applied to BSUK homepage, puppy buying guide, and high-intent commercial pages. Use when building pages that must move a visitor from cold awareness to inquiry submission in a single session."
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## BSUK Project Context
> **Site:** https://SITE_URL_PLACEHOLDER — home-raised Blue Staffordshire Bull Terrier breeder in Glasgow, Scotland
> **Coat colours:** Blue (Roman, Byrd, Ince — £1,500) · Blue brindle / black brindle (Vennie, Christa, Cheryl — £1,700) — treat as distinct product lines
> **Licensing:** LICENCE_CLAIM_PLACEHOLDER and LEGAL_CLAIM_PLACEHOLDER compliance — NOT YET CONFIRMED by Lisa Bright. Never state either as fact, and never imply a puppy-farm or third-party sale.
> **Trust pillars:** LICENCE_CLAIM_PLACEHOLDER · LEGAL_CLAIM_PLACEHOLDER · KC registration · Microchip number · Vet health check · First vaccinations + worming record · Fully weaned + home-raised
> **Buyer fears (ranked):** Scam/unlicensed seller · Sick puppy · Puppy-farm origin · Missing paperwork · No post-sale support
> **Content root:** `site/content/` | **Sessions:** `sessions/`
> **Confidence Gate:** ≥97% before writing any site file

## What AIDA Is

AIDA is a conversion framework for pages where the visitor arrives with commercial intent and must be moved to action in one session. It works linearly — each stage qualifies the reader for the next.

```
A — Attention:  Stop the scroll. Make them read the next line.
I — Interest:   Show you understand their situation. Build relevance.
D — Desire:     Make them want what you have. Connect features to emotions.
A — Action:     Tell them exactly what to do next. Remove friction.
```

---

## When to Use AIDA at BSUK

| Page | AIDA Application |
|------|-----------------|
| Homepage (`/`) | Full AIDA arc across 18 sections |
| `/buy-blue-staffy-puppies-uk/` | AIDA with buyer-fear overlay |
| Region pages (`/uk-locations/<slug>/`) | AIDA with geo-specific desire |
| `/blue-staffy-pup-sale-uk/` | AIDA compressed — hero to CTA fast |
| `/buy-staffy-puppies-for-sale-uk/` | AIDA compressed — hero to CTA fast |

**Don't use AIDA for:** Informational pages, care guides, comparison pages — use Inverse Pyramid or QAB instead.

---

## BSUK AIDA Section Map

### A — Attention (Hero section)
**Goal:** Make the right visitor say "this is for me" in 3 seconds.

Rules:
- H1 names the reader's situation, not BSUK's product
- Subheading delivers the payoff promise
- Trust signals visible above fold
- CTA exists but isn't the focus yet

**Good BSUK Attention hook:**
```
H1: "Blue or blue brindle — which Staffy puppy is the right companion for your family?"
Subhead: "[X] years. [N]+ families. One Glasgow breeder who answers the phone after the sale — with KC registration and a vet health check on every puppy."
```

**Bad Attention hook:**
```
H1: "Welcome to BlueStaffyUK"
(No reader framing, no tension, no hook)
```

---

### I — Interest (Sections 2–4)
**Goal:** Show you understand the reader's specific situation better than they do.

Rules:
- Name the fears they haven't said out loud
- Validate their research process
- Show BSUK is different without saying "we're different"

**Interest techniques:**
- "You've probably heard..." (validates their existing knowledge)
- "Most breeders will tell you..." (sets up contrast)
- "Here's what 15 years taught us that nobody talks about..." (insider revelation)

**BSUK Interest content:**
- The problem with Gumtree / Facebook Marketplace (no licence number, bank-transfer deposits, no recourse)
- The problem with "cheap blue staffy" sites (no LICENCE_CLAIM_PLACEHOLDER, payment via no-recourse apps)
- What "home-raised and licensed" actually means (LICENCE_CLAIM_PLACEHOLDER + LEGAL_CLAIM_PLACEHOLDER + vet health check)

---

### D — Desire (Sections 5–12)
**Goal:** Make them want this specific puppy from this specific breeder.

Rules:
- Lead every feature with the emotional outcome, not the feature
- Use specificity to make desire concrete
- Social proof here (testimonials, family stories, milestones)

**Feature → Desire transformation:**
```
Feature:  "LICENCE_CLAIM_PLACEHOLDER and LEGAL_CLAIM_PLACEHOLDER compliance on every litter"
Desire:   "You'll meet your puppy with its mother in our home before you pay a penny —
           no puppy-farm risk, no questions at your door, no heartbreak after bonding with a
           puppy that was never really ours to sell."

Feature:  "Insured door-to-door puppy delivery across the UK, £200–£350 by distance"
Desire:   "Your Staffy travels in a climate-controlled van with a rest schedule and a
           vet health check in the folder. Not a motorway-services handover from a stranger."
```

**Desire amplifiers:**
- Milestone numbers ("2,000+ families have done this")
- Contrast ("most breeders give you 30 days — we give you 10 years")
- Story ("the Robertson family almost bought from a pet shop...")

---

### A — Action (Final CTA section)
**Goal:** Tell them exactly what to do. Remove every possible objection.

Rules:
- One clear CTA — not multiple competing options
- Remove friction: what happens after they submit?
- Address the last objection before the button
- Urgency must be honest (litter timing, waiting list)

**BSUK Action template:**
```html
<h2>Ready to Meet Your Blue Staffy Puppy?</h2>
<p>Fill out our quick inquiry form. Lisa Bright will respond personally within 24 hours
   — not an automated email, a real reply with available puppies that match your family.</p>
<p><strong>A £500 refundable deposit holds your puppy.</strong> Health guarantee + KC registration and vet health check included.</p>
[Inquiry Form — 3 fields: name, email, coat colour preference (blue / blue brindle)]
<p class="bsuk-form-note">We respond within 24 hours. No spam, no pressure, no bait-and-switch.</p>
```

---

## AIDA Quality Checks

Before finalizing an AIDA page:
- [ ] Attention: H1 names the reader's situation, not BSUK
- [ ] Interest: At least one fear named and validated
- [ ] Desire: Every feature paired with an emotional outcome
- [ ] Action: One CTA, reassurance below button, response time stated
- [ ] Flow: Each section earns the next — no section jumps to action before desire
- [ ] Trust: Social proof in Desire stage, not buried at bottom

---

## Rules

1. **AIDA is linear** — don't put the CTA before Desire is built
2. **Desire before Action** — if a reader doesn't want it yet, they won't act
3. **One CTA in Action stage** — multiple CTAs split attention
4. **Features serve Desire** — never list features without the emotional payoff
5. **Honest urgency only** — "our next litter is X weeks out" not "only 2 left!" if untrue
