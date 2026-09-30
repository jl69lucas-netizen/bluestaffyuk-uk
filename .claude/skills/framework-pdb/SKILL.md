---
name: framework-pdb
description: "Reference guide for the PDB framework applied to BSUK buyer-fear content, licensing safety pages, and high-stakes decision pages. Use when the reader arrives with a specific pain — a scam, a paperwork fear, a puppy-farm suspicion — and needs content that names their pain before offering the solution."
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
> **Buyer fears (ranked):** Scam/fraud · Sick puppy · Missing paperwork · Puppy-farm origin · Post-sale abandonment · Cost uncertainty
> **Pages:** `src/pages/` (built: `dist/`) | **Session docs:** `docs/superpowers/sessions/`
> **Confidence Gate:** ≥97% before writing any site file

## What PDB Is

PDB is a variant of PAS (Problem-Agitate-Solution) calibrated for BSUK's specific buyer fears. It works by naming the reader's pain with unusual specificity — making them feel understood — before presenting the solution. Unlike generic PAS, PDB starts with a brief (a dossier of the reader's fears) rather than a general problem statement.

```
P — Pain:    Name the specific fear. Not "it's hard to find a good breeder" 
             but "you've seen the Facebook posts about puppies that arrived sick."
D — Depth:   Go deeper into why this fear is rational and specific.
B — Brief:   Summarize what this reader needs — then show BlueStaffyUK provides it.
```

---

## BSUK Buyer Fear Stack

These are the ranked fears Blue Staffy buyers arrive with (in order of frequency):

1. **Scam fear** — "Is this breeder real or will I lose my £500 deposit to a scammer?"
2. **Licensing/legal fear** — "Is this seller actually licensed, or am I buying outside LEGAL_CLAIM_PLACEHOLDER?"
3. **Puppy-farm suspicion** — "Was this litter home-raised, or farmed and handed over in a car park?"
4. **Sick puppy fear** — "What if the puppy carries hereditary cataracts or L-2-HGA I won't discover for months?"
5. **Support abandonment fear** — "Will the breeder answer the phone after the money is sent?"
6. **Cost uncertainty fear** — "What's the true total cost — not just the purchase price?"

---

## PDB Application by Page

| Page | Primary Pain | PDB Hook |
|------|-------------|---------|
| `/blue-staffy-uk-breeders/` | Scam fear | "You've seen the Facebook posts about puppy scams. Here's how to know you're not in one." |
| `/uk-blue-staffy-puppy-buying-guide/` | Scam + licensing fear | "The paperwork looked real. It wasn't. Here's how to verify before you send anything." |
| `/buy-blue-staffy-puppies-uk/` | Cost uncertainty | "The purchase price is the smallest number in this equation." |
| Location pages | Distance/trust | "You're trusting a breeder you've never met with £1,500+. Here's how to verify them." |
| `/blue-staffy-pup-sale-uk/` | Puppy-farm suspicion | "Every 'cheap blue staffy' ad you've seen — here's what they're not showing you." |

---

## PDB Structure

### Pain (1–3 sentences)
```
You found three Blue Staffy breeders online. One has a slick website with adorable photos. 
One says "KC registered" in the description but the price is well under £1,500. The other has been operating 
since [YEAR] with a LICENCE_CLAIM_PLACEHOLDER number you can look up. You can't 
tell which one is real.
```

### Depth (2–4 sentences)
```
That uncertainty is rational. Puppy sale scams cost UK buyers millions annually — 
and forged KC paperwork is a real phenomenon in the Staffordshire Bull Terrier market. An
unlicensed seller's promise, their "health guarantee" included, is worth nothing once the
listing has already disappeared. Your fear isn't paranoia — it's pattern recognition.
```

### Brief (1 paragraph)
```
What you need: a breeder with a verifiable LICENCE_CLAIM_PLACEHOLDER number, KC 
registration you can independently check with the Kennel Club, a traceable payment method, 
and a vet health check naming the practice by name. Here's what each of those looks like at 
BlueStaffyUK — and here's how to verify each one independently.
[CTA or link to documentation section]
```

---

## PDB vs BAB — When to Use Which

| Scenario | Use PDB | Use BAB |
|----------|---------|---------|
| Reader has a named fear before landing on page | ✅ | |
| Reader had a bad experience (scam, sick puppy) | ✅ | |
| Reader is comparing options and needs contrast | | ✅ |
| Reader needs to see transformation | | ✅ |
| Page is scam-prevention focused | ✅ | |
| Page is rehoming/rescue reframe | | ✅ |

PDB validates the fear first. BAB shows the contrast after. On the same page, PDB often comes before BAB — validate the fear, then show the transformation.

---

## PDB Writing Rules

### Pain Specificity
```
Weak Pain:  "Finding a reputable breeder can be challenging."
Strong Pain: "The seller had 47 five-star reviews, a licence certificate on their website, 
              and a no-questions-asked refund policy. Three days after the deposit, 
              the website disappeared."
```

### Depth Validation
- Never tell the reader their fear is irrational
- Cite real data where available ("puppy scam losses topped £X last year — Action Fraud data")
- Use "your fear isn't [X], it's [Y]" framing — reframes the emotion as intelligence

### Brief Precision
- The Brief is a compact requirements list — what this reader needs
- Then BlueStaffyUK checks every box on that list
- Brief is not a feature dump — it's a needs summary

---

## Fear-to-Solution Map (ready reference)

| Fear | Depth Fact | BSUK Solution |
|------|-----------|-------------|
| Scam | Puppy fraud is common on Gumtree/FB Marketplace | LICENCE_CLAIM_PLACEHOLDER, traceable payment, [YEAR]+ history |
| Licensing/legal | Unlicensed sellers cannot show LEGAL_CLAIM_PLACEHOLDER; paperwork is forged | Licence number checkable with the issuing authority before deposit |
| Puppy farm | "Home-raised" is claimed freely, rarely proven | Mother seen with the litter at the home; KC registration + microchip number per puppy |
| Sick puppy | HC and L-2-HGA can stay hidden for months | Vet health check, first vaccinations, worming record, parental DNA status |
| Abandonment | Most puppy sellers have no post-sale support | Lisa Bright's email on every page (`data/settings.json` → `email`); the phone stays `PHONE_PLACEHOLDER` until project 6 |
| Hidden costs | Vet costs, insurance, delivery £200–£350 add up | All-in cost guide published openly |

---

## Rules

1. **Pain must be specific** — generic fears don't create the "how do they know that?" response
2. **Depth validates, never dismisses** — the fear is rational, not paranoid
3. **Brief is a needs summary** — not a feature list
4. **BlueStaffyUK must check every Brief item** — don't promise what you can't deliver
5. **Cite real data in Depth** — Action Fraud, vets / The Kennel Club, or BSUK internal data
6. **CTA after Brief** — PDB without an action path is just empathy
