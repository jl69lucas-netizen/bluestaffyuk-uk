---
name: bsuk-evidence-pass
description: Use when a BSUK page is about to be called done, or when a page repeats LICENCE_CLAIM_PLACEHOLDER / LICENCE_CLAIM_PLACEHOLDER / DNA / BlueStaffyUK / home-bred / Carlisle / scam / legit more than a handful of times, when a credential is asserted but never shown, when breed or health facts sit next to breeder opinion with no label, when a review quote might be credited to the wrong buyer, when a title runs past one clause, or when a keyword-count or entity-count rule is pushing copy to say the same thing again. Also use when an AI answer engine quotes a competitor for a fact we state more often than they do.
---

# SKILL: BSUK Evidence Pass — Say It Once, Then Prove It

**Run this AFTER `.claude/skills/anti-ai-writing/SKILL.md` and BEFORE `.claude/skills/bsuk-final-page-pass/SKILL.md`.** Hardening asks *does the page render*, the AEO pass asks *can an engine lift a sentence*; this asks *does the page prove what it asserts, or only repeat it*.

```bash
npm run -s build
python3 scripts/evidence_audit.py <slug> [<slug> ...]      # slugs LITERALLY; `index` is the homepage
```
`ERROR` = fix before deploy. `WARN` = read the section, then decide. `0 pages matched` is not a pass.

> **Read `.claude/skills/bsuk-gate-integrity/SKILL.md` first.** Term counts are exact. The statement-label and superlative checks are proxies: confirm a flagged section by reading it.

## Why this gate exists (measured 2026-09-09, `dist/`)
In the source repo the homepage `<main>` said one licence term 44×, the brand 66×, DNA 40× and one statute term 28× across 8,830 words, and credited one review quote to two different buyers. Not one credential on the site linked to a proof object. Four house rules (a keyword floor (85 mentions), "150+ entity mentions", ≥5 H5 + ≥5 H6, a title that was "never short") were the cause. The breeder's ruling: **sections stay; repetition goes; proof replaces assertion.**

## The four rules this skill owns
| Rule | What it means on the page |
|---|---|
| **Term budget** (`data/quality/evidence-budgets.json`) | Each trust concept is said where it is load-bearing and nowhere else. Over budget → cut the mention or turn it into a link to the section that owns it. |
| **Claim → proof** (`data/quality/evidence-ledger.json`) | A credential made twice must link its proof object (a redacted licence record, an example vet or health-test certificate). Proof `NOT FETCHED` → say it **once**, in the trust section, and link there from everywhere else. Never write NOT FETCHED in prose. |
| **Statement labels** (`StatementLabel.astro`) | Breed, legal and health facts open with **Fact** (+ source link). What we have seen opens with **Observed here** (+ n, since). Advice opens with **Our recommendation**. Marketing copy carries no label and makes no factual claim. |
| **Evidence integrity** | One quote, one name, everywhere — reviews are NOT FETCHED until the breeder supplies them, and an unfetched review is never written. No invented identifiers. No superlative without a source in the same sentence. Title ≤70 chars, one clause. |

## Procedure, per section (sections are never removed)
1. Count: `python3 scripts/evidence_audit.py <slug>` — note every ERROR term and the section it lives in (grep the built `<main>` by section id).
2. Choose the one load-bearing mention per term per page. The trust section owns credentials; the health section owns screening; the pricing section owns the price.
3. Every other mention becomes either (a) a pronoun / plain noun ("our paperwork", "the certificate"), or (b) a link to the owning section.
4. Wrap each breed / legal / health sentence with the right `StatementLabel`. If you cannot name the source for a Fact, it is not a Fact: relabel as Observed here or delete.
5. Re-run the audit. Re-run `python3 scripts/dup_content_audit.py <slug>` — de-repetition must not converge sibling pages.
6. Word count is NOT a target. If it fell, good. If it did not, the page was not repeating; leave it.

## Rationalisations this skill closes (from the 2026-09-09 baseline)

Every row quotes or paraphrases an entry in the source repo's 2026-09-09 evidence baseline (not ported — source repo only). The number in brackets is that entry. If you catch yourself writing one of these sentences in a change log, the change is wrong.

| Excuse | Reality |
|---|---|
| "The keyword-verifier says under 85 mentions is under-optimised" — the floor the RED subagent optimised toward on every line [#1, #2, #9] | The floor was deleted 2026-09-09. Only the ceiling exists (`data/quality/evidence-budgets.json`). Repeating a term is now a defect, not a score. |
| "Rule 57 wants 150+ entity mentions" — "Rule 57 category 6 'Credential/Certification Entities'" [#4], "adds two brand/product entities (Rule 57)" [#6] | Rule 57 now reads 95–105 **distinct** entities, each said once where load-bearing. Mentions are not entities. Naming LICENCE_CLAIM_PLACEHOLDER in an H5 list after it appeared in the intro adds zero distinct entities and one over-budget mention. |
| "The AEO pass wants named entities instead of pronouns" — "pronoun 'we' replaced with 'BlueStaffyUK' / 'Lisa Bright'. `.claude/skills/bsuk-aeo-pass/SKILL.md` Part 3" [#3], "'Every blue Staffy we place' → 'every blue Staffy BlueStaffyUK places.' Part 3 entity-rich" [#14] | The AEO named entity is wanted **once per section, at the answer sentence**. Everywhere else `we / our / ours` is the house voice (CLAUDE.md rule 1). The 66th "BlueStaffyUK" is not an entity signal, it is noise, and it took the brand count from 4→9 and 2→10 in two sections. |
| "≥5 H5 and ≥5 H6 need content to sit under them" — "7 H5 / 7 H6 across the two sections, which alone clears the ≥5/≥5 page floor in `rules/headings.md`" [#7] | The H5/H6 minimums are **advisory** on the homepage and location pages. They are never a reason to add a heading. Six headings added to feed a counter is six defects. |
| "This H6 is the section's ≥5-H6 contribution" — "Rule 57 wants H6-level 'ultra-specific details / breeder notes' … and this is the section's ≥5-H6 contribution" [#5] | A heading exists because the outline has a sub-topic under it, never because a page-level counter is short. If the only justification you can write is the counter, delete the heading and fold any real content into the paragraph above it. |
| "Alt text is ≥250 characters (IMAGE-01)" — "Hero image alt expanded from ~130 to ~390 characters, naming BlueStaffyUK, Lisa Bright, Carlisle, LICENCE_CLAIM_PLACEHOLDER, LICENCE_CLAIM_PLACEHOLDER LEGAL_CLAIM_PLACEHOLDER, […]" [#2], "`imageAlt` expanded to ~300 characters with breeder names, weaning window, […], LICENCE_CLAIM_PLACEHOLDER LEGAL_CLAIM_PLACEHOLDER and price range. IMAGE-01 ≥250 chars" [#9] | IMAGE-01's ≥250-char floor is retired. Alt text **describes the image in ≤125 characters**. It carries no credential, price or licence: a screen reader hears the picture, not a trust bar. Every trust term in an alt counts against the page budget. |
| "I raised counts by adding *distinct* named entities rather than repeating the head term" [#13] | Distinct entities are fine **once each**. Wrapping each new entity in a re-statement of LICENCE_CLAIM_PLACEHOLDER / LICENCE_CLAIM_PLACEHOLDER / DNA / BlueStaffyUK (as #4, #8, #11, #12 did) is repetition wearing an entity's coat. Check the term counts before and after: if LICENCE_CLAIM_PLACEHOLDER, LEGAL_CLAIM_PLACEHOLDER, DNA or BlueStaffyUK rose, the "distinct entity" was a vehicle. |
| "'blue Staffy' at 40 in 950 words (~4.2%) exceeds the 2%-per-entity section cap — but the original section was already ~4.3%, and the term is the section's subject" [#13] | Being the subject is why the term appears in the H2 and the answer sentence; it is not a licence to exceed the cap in the body. Over cap → pronoun or plain noun ("the puppy", "this variant"). "The original was already over" is a reason to cut, not to match. |
| "Breeder entity properties added to the first 100 words — owner name, Carlisle, a founding date, LICENCE_CLAIM_PLACEHOLDER licence" [#1] | The first 100 words answer the section's question. Owner name, city, founding date and licence are said **once** on the page, in the section that owns them (trust), and linked from elsewhere. Four credentials in one opening sentence is a trust bar, not an answer. |
| "Each bullet names a credential entity: LICENCE_CLAIM_PLACEHOLDER + a public licence search, LEGAL_CLAIM_PLACEHOLDER, the vet check and the microchip record, […] L-2-HGA and HC-HSF4 parent testing" [#4] | A credential made twice on a page **without its proof link is an ERROR** (`data/quality/evidence-ledger.json`). The second mention becomes a plain noun ("the licence", "the certificate") or a link to `#proof`. Proof `NOT FETCHED` → the one mention lives in the trust section and that is all. |
| "Location Entities (the weakest category on this page — the rule asks for 80+ page-wide)" [#10] | There is no page-wide location quota. A range-map paragraph is welcome if the outline calls for it; a list of seven countries written to lift a category count is filler. |
| "Stat-bearing H6 'The Kennel Club Endangered Since 2016, LICENCE_CLAIM_PLACEHOLDER LEGAL_CLAIM_PLACEHOLDER Since 2017' carrying the LICENCE_CLAIM_PLACEHOLDER framing CLAUDE.md rule 2 requires" [#11] | Rule 2 requires the framing to be **correct** wherever it appears, not to appear again. LEGAL_CLAIM_PLACEHOLDER has a page budget of 1–2. One correct **Fact**-labelled sentence with its LICENCE_CLAIM_PLACEHOLDER source link is compliance; a second heading is a budget overrun. |
| "New FAQ 3 (H5) 'What health testing does a BlueStaffyUK puppy come with?' + H6 … Rule 57 category 3 Medical entities; `rules/headings.md` ≥5 H5/H6" [#12] | An FAQ is added when GSC / PAA shows the question is asked, never to raise a medical-entity count or a heading count. If the health section already answers it, link there. |
| "Lisa Bright home-raise every BlueStaffyUK puppy… have its sex confirmed by the vet, and supply LICENCE_CLAIM_PLACEHOLDER LEGAL_CLAIM_PLACEHOLDER home-bred documentation with a written health guarantee (its length unstated)" — one SplitFeature body [#8] | One sentence carrying five trust terms is a term-budget overrun in miniature. The SplitFeature body says what the puppy gets and links the trust section for the paperwork. The breeder has not named a house method, so none may be written. The guarantee is named only with its length from `guarantee_days` (730 days: a two-year guarantee) and the words of `guarantee_label`. |
| "Repeating LEGAL_CLAIM_PLACEHOLDER is compliance-safe" [paraphrase of #11] | Saying it once correctly is compliance. Saying it 28 times is a pattern Google's spam guidance names. |
| "The breeder wants trust signals everywhere" [paraphrase of #4] | The breeder approved Strategy A: say it once, prove it, move on. Proof is the trust signal. |
| "I'll add the proof link later" [what #4 and #8 left undone] | A claim made twice without its proof is an ERROR today. Say it once, or link the trust section now. |
| "This is marketing copy, labels don't apply" [what #8 assumed] | Then it must make no factual claim. A lifespan, a screening test, a legal status is a fact; label it or cut it. |

## Red flags — stop and re-read the procedure
- You are about to add a heading, an FAQ or a paragraph to reach a count.
- You typed a credential you did not read in `data/quality/evidence-ledger.json`. `docs/reference/credentials.md` names every key and no value.
- You wrote a licence number, a study, or a buyer name from memory.
- The audit passed on `0 pages matched`.
- Two review quotes on the page read the same.
- Your change log cites a counter (mentions, entities, H5/H6, alt length) as the WHY. A counter is never a why.
- The word count went up and you cannot name the question the new words answer.

## What this skill does not do
It does not write prose (write from the outline: `rules/copy.md` → `write-from-outline-never-from-sibling`). It does not judge AI-tells (`.claude/skills/anti-ai-writing/SKILL.md`), citability (`.claude/skills/bsuk-aeo-pass/SKILL.md`) or sibling overlap (`.claude/skills/bsuk-duplicate-content-gate/SKILL.md`). It does not calibrate the budgets: Sprint 0 does, against the pages the engines actually cited.
