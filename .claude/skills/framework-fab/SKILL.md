---
name: framework-fab
description: "Reference guide for the FAB (Features → Advantages → Benefits) framework applied to BSUK pages. Use when writing spec-bearing content — puppy listing details, pricing what's-included rows, crate/diet/setup recommendations, documentation stacks, delivery tiers — so a raw fact never ships without its advantage and its owner-benefit. Also the comparison-row framework (advantage comparison vs competitors/other breeds)."
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> **Link-First (ALWAYS):** anchors at the START of the sentence — never mid-sentence, never at the end.
> Use Claude Code and Playwright CLI to solve problems first.
> **Confidence Gate:** ≥97% before writing any site file.

---

## BSUK Project Context
> **Site:** BlueStaffyUK — licensed Blue Staffordshire Bull Terrier breeder, Glasgow
> **Coat colours:** blue and blue brindle (Roman, Byrd, Ince — £1,500) · black brindle and rarer blue lines (Vennie, Christa, Cheryl — £1,700)
> **Licensing:** Glasgow City Council breeder licence; Lucy's Law compliant — every puppy seen with its mother at our home.
> **Facts source:** `data/price-matrix.json` · `data/puppies.json` · `data/locations.json` · Verified-Claim Ledger — never invent a spec.

---

## What FAB Is

FAB forbids naked facts. Every feature gets translated twice — into what it does better (advantage) and what that means for the buyer's life (benefit).

```
F — Feature:   The verifiable fact/spec. ("Every puppy leaves with an L-2-HGA DNA status certificate for both parents.")
A — Advantage: What that does better than the alternative. ("You cannot see L-2-HGA in a puppy — affected dogs look normal until symptoms appear in adolescence; DNA status on both parents is the only reliable way to rule it out.")
B — Benefit:   What it means for THIS buyer. ("You know on day one that your Staffy is clear by parentage — and a late neurological diagnosis never blindsides you.")
```

**Related EBP note:** BSUK's `framework-ebp` (Evidence → Benefit → Proof) is the credibility-first cousin; the entity catalog's EBP (Entity-Benefit-Purpose) is the entity-SEO variant. FAB is the *spec-translation* tool — see `.claude/skills/framework-library/SKILL.md §EBP disambiguation`.

## When to Use on BSUK

| Use FAB | Don't use FAB |
|---|---|
| Puppy listing spec blocks (weaning, microchip, documentation) | Pain-led sections → `framework-pas` |
| Pricing "what's included" rows | Story/trust sections → `framework-eeat` / H-S-S |
| Crate/diet/setup product recommendations | FAQ answers → `framework-qab` |
| Comparison-table rows + advantage columns (X vs Y pages) | Cold-traffic heroes → `framework-aida` |
| Delivery tiers (£200 local / £350 long-distance — advantage + benefit per tier) | |

## BSUK Worked Example (delivery tier row)

- **F:** "Door-to-door delivery, £350 — a dedicated driver, air-conditioned van, straight from our Glasgow home to yours."
- **A:** "Unlike a motorway service-station handover, your puppy never changes hands in a car park and you never drive six hours each way."
- **B:** "Your Staffy steps out of the crate into its new living room — one calm transition instead of three stressful ones."

## The Advantage-Comparison Variant (comparison pages)

On [X] vs [Y] pages, the A beat carries the row: state what our option does better *than the named alternative*, grounded in fetched competitor/breed data — `NOT FETCHED` data is never invented. Pair with the honesty moat: when the alternative genuinely wins a row, say so (that's the trust play that outranks fluff).

## Common Mistakes
- **Shipping the F without the B** — a spec list with no translation is commodity content; the Generic-Slayer filter will flag it.
- **Fake advantages** — "chew-proof stainless" only if the recommended product actually is; specs trace to real data files or reviewed products.
- **Benefit inflation** — the B beat stays inside verified claims; no lifespan/health promises beyond the ledger.
- **FAB-ing every paragraph** — it's for spec-bearing content; narrative sections use their own frameworks.
