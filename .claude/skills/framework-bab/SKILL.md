---
name: framework-bab
description: "Reference guide for the BAB framework applied to BSUK buyer-fear content, scam-prevention sections, and licensing safety content. Use when the reader needs to see a clear contrast between their current risky situation and the documented outcome — and BSUK as the bridge."
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

---

## What BAB Is

BAB is a contrast framework. It shows the reader where they are now (Before), where they want to be (After), and presents BlueStaffyUK as the Bridge between those two states. It works best when the reader is in pain — a bad experience with sellers, a failed purchase, a fear of being scammed.

```
B — Before:  Name their current reality. The pain, the fear, the frustration.
A — After:   Show the transformed future. Specific, emotional, concrete.
B — Bridge:  BSUK as the path from Before to After.
```

---

## When to Use BAB at BSUK

| Page / Section | BAB Application |
|----------------|----------------|
| Scam-prevention sections | Before: bank-transfer seller risk → After: licensed, documented purchase |
| Licensing safety sections | Before: unlicensed puppy-farm risk → After: full LEGAL_CLAIM_PLACEHOLDER-compliant paperwork |
| Health section | Before: sick puppy fear → After: vet health check, first vaccinations, a vet-signed health card (a guarantee only once `guarantee_days` is set) |
| First-time owner sections | Before: overwhelmed by complexity → After: guided and supported |
| `/uk-blue-staffy-puppy-buying-guide/` | Before: online scam → After: verified breeder checklist |

**Don't use BAB for:** Informational care content, coat-colour comparison tables, FAQ sections.

---

## BAB in Practice — BSUK Examples

### Scam-Prevention Section
```
BEFORE:
You found a blue Staffy puppy for well under £1,500 on Facebook Marketplace. The photos looked real.
The seller had a phone number. You sent a bank transfer as a deposit.
Then silence. The number disconnected. The profile disappeared.
That's not a rare story — it happens every week in UK Staffy Facebook groups.

AFTER:
Your BlueStaffyUK puppy comes with a LICENCE_CLAIM_PLACEHOLDER number — the
council record issued under UK licensing law. KC registration papers from the Kennel Club.
A vet health check naming the vet and practice. A microchip number registered to us first.
You can verify every document independently before sending a single pound.

BRIDGE:
Buying a Staffy from a breeder who shows you the paperwork isn't more expensive than buying from
an online stranger — it's a different category of transaction entirely. One where the
paperwork is real, the sale is legal, and there's a human being who answers the phone
after the sale. Every puppy Lisa Bright places is raised in her own home in Carlisle.
[CTA: Start your inquiry →]
```

### Licensing Safety Section
```
BEFORE:
You bought a beautiful blue Staffy from a site that said "fully licensed."
Three months later, your vet asked who registered the microchip. The licence number
was invented. Trading Standards had already been out to the address. You had no idea.

AFTER:
Every puppy from BlueStaffyUK leaves with a LICENCE_CLAIM_PLACEHOLDER number
and full LEGAL_CLAIM_PLACEHOLDER compliance. You receive the licence number before you pay a deposit.
You can check it with the council directly. It's not a certificate we printed — it's a
council record with a traceable number.

BRIDGE:
LICENCE_CLAIM_PLACEHOLDER either exists as an authority record or it doesn't. There's no grey area.
Here's what a genuine LICENCE_CLAIM_PLACEHOLDER looks like — and how to verify
yours before sending any deposit. [Link: LICENCE_CLAIM_PLACEHOLDER verification guide]
[CTA: Verify your breeder's licence →]
```

---

## BAB Writing Rules

### Before — Make the Pain Real
- **Specific, not generic:** "You sent a bank transfer online and never heard back" > "some people get scammed"
- **Empathetic, not condescending:** "that's not a horror story — that's a Tuesday for Staffy buyers in Facebook groups" validates without judging
- **Name the emotion:** fear, frustration, heartbreak — not just the situation

### After — Make the Future Concrete
- **Sensory specificity:** "your £500 deposit books the viewing, and you meet the puppy with its mother in our kitchen"
- **Numbers where possible:** "the vet bills you were told to expect, and no others" > "fewer vet visits"
- **Their future, not BlueStaffyUK's product:** show their life, not BSUK's features

### Bridge — Earn the Transition
- **Don't jump straight to CTA:** earn the bridge by validating the Before fully
- **Show the mechanism:** what specifically makes BlueStaffyUK the bridge (LICENCE_CLAIM_PLACEHOLDER, vet health check + KC registration, insured door-to-door puppy delivery)
- **One bridge per BAB:** don't list every BSUK feature — pick the one that most directly solves the Before

---

## BAB Length Guidelines

| Application | Before | After | Bridge |
|-------------|--------|-------|--------|
| Section hook (2–4 paragraphs) | 1 para | 1 para | 1–2 para |
| Full section (hero to CTA) | 2–3 para | 2–3 para | 3–4 para |
| Email sequence | 1 para | 1 para | 1 para |
| Social caption | 2–3 sentences | 2–3 sentences | 1–2 sentences |

---

## Common BAB Mistakes

| Mistake | Fix |
|---------|-----|
| Before is too mild ("it can be hard to find a good breeder") | Make the pain specific and real |
| After is vague ("peace of mind") | Make After concrete ("the vet bills you were told to expect, and no others") |
| Bridge is a feature list | Bridge is a single mechanism — the one thing that closes the gap |
| BAB without CTA | Every BAB ends with an action path |
| Before sounds like you're insulting scam sellers/competitors | Empathize with the reader's experience, don't attack the industry |

---

## Rules

1. **Before must name real pain** — vague discomfort doesn't motivate action
2. **After must be the reader's life, not BlueStaffyUK's product** — show their future
3. **Bridge is one mechanism** — the specific BSUK capability that makes the After real
4. **CTA required after every BAB** — contrast without action is just storytelling
5. **Don't attack competitors by name** — frame the industry pattern, not a specific seller
6. **BAB is for fear and contrast** — use AIDA for commercial intent, QAB for FAQ
