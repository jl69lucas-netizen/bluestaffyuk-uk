---
name: framework-eebp
description: "Use when writing or auditing any BSUK transactional / for-sale / buy page section that must satisfy SEO + AEO + GEO + EEAT + conversions at once. EEBP = Entity → Evidence → Benefit → Purpose. This is a DISTINCT framework — do NOT substitute framework-ebp (Evidence→Baseline→Profile) or the bsuk-entity-agent EBP (Entity→Benefit→Purpose). Triggers: for-sale/buy page copy, product/offer blurbs, trust rows, 'make this section citation-friendly', EEBP."
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## ⚠️ DISAMBIGUATION — READ FIRST (this is why the framework keeps getting confused)

There are THREE different acronyms in this repo that all start with "E" and get collapsed into each other. They are NOT the same. This skill is **only** the first one.

| Framework | Expansion | Where it lives | Use for |
|---|---|---|---|
| **EEBP (this skill)** | **E**ntity → **E**vidence → **B**enefit → **P**urpose | `.claude/skills/framework-eebp/SKILL.md` | **For-sale / buy transactional pages** — the required framework on those pages |
| framework-ebp | **E**vidence → **B**aseline → **P**rofile | `.claude/skills/framework-ebp/SKILL.md` | Skeptical trust/credibility proof sections (claim → named evidence → how we exceed baseline) |
| bsuk-entity-agent EBP | **E**ntity → **B**enefit → **P**urpose | `.claude/skills/bsuk-entity-agent/SKILL.md` | Entity catalog / schema vocabulary (3-part, **no Evidence step**) |

**The one thing that makes EEBP unique: it has BOTH an Entity anchor AND a named Evidence step, then closes on buyer Purpose.** If you wrote a 3-part sentence, you used the wrong framework — EEBP is always four moves.

---

## What EEBP Is

EEBP structures a statement so it names a real thing, proves it with verifiable evidence, translates that into a buyer-meaningful benefit, and ends on the buyer's decision-making purpose. It is the on-page workhorse for BSUK transactional pages because a single well-formed EEBP row simultaneously feeds five systems.

```
E — Entity:    Name the concrete entity (puppy, credential, document, place, standard)
E — Evidence:  State the specific, verifiable proof attached to that entity
B — Benefit:   Translate the evidence into what the buyer actually gets
P — Purpose:   Close on the buyer's decision/outcome the statement enables
```

### The canonical example (breeder-supplied — do not alter the four moves)

| Entity | Evidence | Benefit | Purpose |
|---|---|---|---|
| Blue and White Staffy Puppy | Home-raised, KC registered, microchipped | Calm, loyal, adaptable family companion | Helps buyers confidently choose a fully papered Blue Staffy that matches their home and lifestyle. |
| LICENCE_CLAIM_PLACEHOLDER | Family home in Carlisle, Cumbria (a licence stays unstated until the breeder confirms it) | Demonstrates breeder transparency | Reduces buyer uncertainty and supports trust during the purchase decision. |
| Vet Health Check | Veterinary examination before collection | Greater confidence in the puppy's condition | Helps buyers make an informed decision before bringing a Blue Staffy home. |

## Why EEBP Beats a Plain Feature List (the 5-point payoff)

Every complete EEBP row is engineered to satisfy all five at once:

- **SEO:** the Entity step forces richer entity relationships (puppy ↔ credential ↔ document ↔ place).
- **AEO:** the Evidence + Benefit steps directly answer the user's implicit question, so answer engines can lift the sentence.
- **GEO:** the Evidence step produces citation-friendly *factual* statements (verifiable, not marketing fluff).
- **EEAT:** evidence-first phrasing emphasizes verifiable proof over unsupported claims.
- **Conversions:** the Benefit + Purpose steps connect a dry feature to a meaningful buyer outcome.

If a draft sentence doesn't advance at least one of these five, a move is probably missing.

## How to Write an EEBP Sentence (prose form)

Fold the four moves into first-person BlueStaffyUK voice, entity first, purpose last:

> **"Every Blue Staffy puppy we place (entity) is home-raised, KC registered and microchipped with a vet health check (evidence), so you bring home a calm, fully papered companion (benefit) — which is exactly how you choose a Staffy that fits your household with zero paperwork doubt (purpose)."**

Rules:
- **Entity leads the sentence** (also satisfies the Link-First anchor rule when the entity is a link).
- **Evidence must be ledger-verified** — only claims `data/quality/evidence-ledger.json` records with a proof on file, and facts in `data/*.json`. A row at proof `NOT FETCHED` (the parents' DNA results today) is not evidence. Never invent a test, cert, or count.
- **Benefit is buyer-facing**, not seller-facing ("you bring home…" not "we offer…").
- **Purpose names the decision** the buyer can now make (choose, verify, reserve, rule out, budget).
- Licensing framing stays accurate: **LICENCE_CLAIM_PLACEHOLDER, LEGAL_CLAIM_PLACEHOLDER compliant, mum always seen with the litter at our home.**

## When to Use vs Other Frameworks

- **Use EEBP** on for-sale / buy transactional pages: puppy-card blurbs, trust rows, "what's included," documentation panels, price-explainer rows, delivery-tier rows — anywhere a feature needs to become a buyer outcome AND a citable fact.
- **Use framework-ebp (Evidence→Baseline→Profile)** when the *whole point* of a section is surviving skeptical scrutiny (scam moat, "how do you know we're legit").
- **Use QAB / EFBP openers** for the conversational opening paragraph under each header; EEBP then structures the factual rows/claims inside.
- EEBP **stacks with** EFBP (the for-sale opening-paragraph pattern): EFBP opens the section conversationally, EEBP structures the proof rows beneath it.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Dropped the Evidence step (wrote Entity→Benefit→Purpose) | That's the entity-agent EBP, not EEBP. Add the named, verifiable proof. |
| Evidence is a marketing adjective ("amazing health") | Evidence must be verifiable and specific ("vet exam before collection"). |
| Benefit written from seller's side ("we guarantee…") | Rewrite as buyer outcome ("you get…"). |
| Purpose is a restated benefit | Purpose = the decision/action it enables, not the feeling. |
| Entity buried mid-sentence | Lead with the entity (Link-First + entity-SEO). |
| Unverifiable claim slipped into Evidence | Cut it or downgrade to Ledger-safe wording. |

## Quick self-check (before shipping a section)
- [ ] Does every proof row have all FOUR moves (Entity, Evidence, Benefit, Purpose)?
- [ ] Is each Evidence item Ledger-verified?
- [ ] Does each row read as a citable fact (GEO) AND a buyer outcome (conversion)?
- [ ] Entity leads? Purpose closes on a decision?
- [ ] LICENCE_CLAIM_PLACEHOLDER / LEGAL_CLAIM_PLACEHOLDER framing intact?
