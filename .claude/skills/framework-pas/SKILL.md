---
name: framework-pas
description: "Reference guide for the PAS (Problem → Agitate → Solution) framework applied to BSUK pages. Use when the reader arrives already in pain — behavioural issues (chewing, separation barking, lead pulling), scam fear, sick-puppy fear, food refusal, adolescent stubbornness — and needs the fastest path from pain to our documented answer. The fastest-converting framework for problem-aware audiences."
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> **Link-First (ALWAYS):** anchors at the START of the sentence — never mid-sentence, never at the end.
> Use Claude Code and Playwright CLI to solve problems first.
> **Confidence Gate:** ≥97% before writing any site file.

---

## BSUK Project Context
> **Site:** BlueStaffyUK — home-raised Blue Staffordshire Bull Terrier breeder in Carlisle, Cumbria (Lisa Bright)
> **The litter:** `data/puppies.json` — males Roman, Byrd, Ince at £1,500 · females Vennie, Christa, Cheryl at £1,700. The price follows the sex, not the coat; each pup's coat is its own row's `colour` (blue, blue and white, white, blue with white blaze), and none of the six is brindle
> **Licensing:** LICENCE_CLAIM_PLACEHOLDER and LEGAL_CLAIM_PLACEHOLDER compliance — NOT YET CONFIRMED by Lisa Bright. Never state either as fact, and never imply a puppy-farm or third-party sale.
> **Buyer fears (ranked):** Scam/unlicensed seller · Sick puppy · Puppy-farm origin · Missing paperwork · No post-sale support
> **Health claims:** bounded by the evidence ledger (`data/quality/evidence-ledger.json`) — never invent symptoms, cures, or statistics.

---

## What PAS Is

PAS is the fastest path to conversion when the audience feels a specific pain. Name the problem in their words, make the cost of inaction concrete, then present the solution.

```
P — Problem:  Name their exact pain, in the reader's own words (GSC/PAA/Reddit phrasing).
A — Agitate:  Make the cost of inaction concrete and true. Never invent horror; use verified consequences.
S — Solution: Our documented answer — specific, first-person, with the next step.
```

## When to Use on BSUK

| Use PAS | Don't use PAS |
|---|---|
| Behaviour guides (chewing, separation barking, lead pulling) | Cold top-of-funnel readers → `framework-aida` |
| Scam-fear content ("is this breeder legit?") | Contrast/transformation stories → `framework-bab` |
| Health-problem sections (skin allergy signs, food refusal) | Spec/feature sections (crate, pricing rows) → `framework-fab` |
| Diagnostic openings on pillar guides (problem in H1, agitation in sub-headline, solution as header — the extractable AIO pattern) | FAQ answers → `framework-qab` |

## BSUK Worked Example (skin allergy section)

- **P:** "Is your Staffy chewing its paws raw — and the vet found no mites or fleas?"
- **A:** "Untreated atopic itching becomes a scratch-infect-scratch cycle within months; skin that's been broken open long enough thickens and darkens permanently. Staffordshire Bull Terriers are among the most allergy-prone breeds we work with." *(stays inside the evidence ledger — breed allergy-proneness is documented; no invented percentages)*
- **S:** "Our diet and bathing routine is the same one we use in our own kennel — a single-protein food from week eight, oatmeal rinse every third day. [Full routine + the starter pack we send with every puppy →]"

**Agitate honestly:** every agitation line must be a true, sourced consequence. Fear without fabrication — the humor-honesty policy applies in reverse: never on legal/health, never invented.

## PAS + the House Rules
- **Setup-Stat-Reframe cadence** inside the Agitate beat (name problem → attributed stat → reframe) is the AIO-citation-friendly variant — cite the stat or drop it.
- Headers stay conversational Quora-style (the P beat often IS the H2/H3 question).
- First-person BlueStaffyUK voice in the S beat; encyclopedic neutrality allowed in P/A facts.
- One CTA per page still applies — PAS sections funnel to the page's single CTA, not one CTA per section.

## Common Mistakes
- **Inventing agitation** — fabricated statistics or horror stories violate the evidence ledger and the honesty policy.
- **Agitating on legal/health past the ledger** — hereditary cataracts / L-2-HGA / vet claims only as confirmed.
- **Solution before problem** — leading with "we offer…" kills the framework; the reader's pain leads.
- **Using PAS on unaware readers** — they don't feel the problem yet; that's AIDA's job.
