---
name: framework-library
description: "Catalog of the long-tail copywriting frameworks for BSUK beyond the dedicated skills — 4Ps, AICPBSAWN, QUEST, ACCA, HIPASI, A-FOREST, String of Pearls, VAD, Setup-Stat-Reframe, The 4 Ss, the 5 Basic Objections, and the objection-handling block. Use when selecting a framework for a page/section and none of the dedicated framework-* skills fits, when writing long-form landing pages for cold traffic, consultative/qualifying content, testimonial structure, or objection-handling blocks. Includes the master routing table by page type + reader awareness level, and the EBP disambiguation note."
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> **Link-First (ALWAYS):** anchors at the START of the sentence — never mid-sentence, never at the end.
> **Confidence Gate:** ≥97% before writing any site file.
> Every framework below is bounded by the evidence ledger (`data/quality/evidence-ledger.json`), first-person BlueStaffyUK voice, licensing safety, and the anti-ai-writing filter.

---

## How to Pick — Master Routing Table

**By reader awareness level:**

| Reader state | Framework | Skill |
|---|---|---|
| Unaware (doesn't know they want a Blue Staffy) | AIDA | `framework-aida` |
| Problem-aware (separation whining, scam fear, sick puppy) | PAS | `framework-pas` |
| Solution-aware (comparing options/methods) | BAB or FAB | `framework-bab` / `framework-fab` |
| Product-aware, skeptical (high-ticket doubt) | 4Ps or AICPBSAWN | this file |
| Needs vetting (is a Staffy right for THEM?) | QUEST or ACCA | this file |
| Asking a direct question | QAB | `framework-qab` |
| Needs credibility proof | EEAT / EBP | `framework-eeat` / `framework-ebp` |

**By BSUK page/section type:**

| Page/section | Primary framework |
|---|---|
| Homepage hero, seasonal campaigns | AIDA |
| Behaviour/health problem guides | PAS (+ Setup-Stat-Reframe for stats) |
| Scam cluster, buyer-fear pages | PAS or BAB (+ 5 Basic Objections sweep) |
| Puppy listings, pricing rows, delivery tiers | FAB |
| Comparison pages/rows | FAB advantage-comparison + VAD |
| High-intent long-form (for-sale, purchase guide) | AICPBSAWN skeleton or 4Ps |
| "Is a Blue Staffy right for you?" content | QUEST / ACCA |
| Testimonials/case studies | The 4 Ss |
| Blog posts | HIPASI skeleton; A-FOREST or String of Pearls for body texture |
| Pillar guides | Topic-cluster architecture + PAS-structured opening (see `bsuk-seo-master-checklist`) |
| FAQ | QAB (`framework-qab`) |

---

## The Frameworks

### 4Ps — Promise, Picture, Proof, Push
High-investment, skepticism-heavy offers (buying a £1,500–£1,700 puppy).
1. **Promise** — the core claim ("a healthy, home-raised, fully documented Blue Staffy").
2. **Picture** — paint the owned future concretely (first tail-wag in your kitchen).
3. **Proof** — the trust stack: real reviews (reviewCount 52), LICENCE_CLAIM_PLACEHOLDER, LEGAL_CLAIM_PLACEHOLDER compliance, KC registration, vet health checks. Proof validates the Promise BEFORE the ask.
4. **Push** — the single CTA. Real scarcity only (`data/puppies.json`).

### AICPBSAWN — the long-form cold-traffic skeleton
Attention · Interest · Credibility · Proof · Benefits · Scarcity · Action · Warning · Now. Use as the SECTION ORDER for a full high-intent landing page. BSUK mapping: Credibility = breeder story/credentials · Scarcity = real litter counts only · **Warning = the risks of unlicensed/puppy-farm sellers (natural home for Negative Keyword Counter-Positioning)** · Now = why this season/litter. Never fabricate scarcity or urgency (seo-rules Rule 48).

### QUEST — Qualify, Understand, Educate, Stimulate, Transition
Consultative selling; ideal because Staffy buyers SHOULD be vetted. Open by qualifying ("Are you ready for a 12–14-year, high-energy companion?"), empathize with the research burden, educate (link out to guides — Link-First), stimulate with what ownership is actually like, transition to the enquiry form. This is the framework for `/buy-blue-staffy-puppies-uk/`-class pages and the rehoming page's honest-breeder frame.

### ACCA — Awareness, Comprehension, Conviction, Action
For readers who don't yet understand the problem (e.g. LEGAL_CLAIM_PLACEHOLDER and LICENCE_CLAIM_PLACEHOLDER education, why "cheap Blue Staffy" ads are dangerous). Heavier on Comprehension than PAS — explain mechanics before asking for conviction.

### HIPASI — Headline, Image, Problem, Agitation, Solution, Invitation
The blog-post skeleton: hook headline → hero image (Rule 50b alts) → PAS body → soft Invitation (newsletter/guide link, not a hard sell). Stacks with `bsuk-blog-post`'s 14-step architecture — HIPASI orders the narrative INSIDE that structure.

### A-FOREST — Alliteration, Facts, Opinions, Repetition, Examples, Statistics, Three
Texture checklist for long-form body copy: verified facts, owned first-person opinions (breeder POV is our moat), key-message repetition, real examples (Roman, real enquiry calls), attributed statistics, rule-of-three cadence. Apply SPARINGLY — anti-ai-writing bans tricolon adjective stacks; "Three" means three supporting points, not three adjectives.

### String of Pearls
Sequential drops of true, specific details that accumulate into authority — e.g. a home-raising timeline told through five real moments. Each pearl must be a verifiable specific (ledger-bounded). Great for About/story sections and non-commodity rewrites.

### VAD — Verb, Application, Differentiator
One-line positioning for cards, meta descriptions, comparison intros: what we DO (verb), for whom/what (application), why us (differentiator). "We home-raise (V) blue, blue and white, and white Staffordshire Bull Terriers for documented family placement (A) with KC registration and parents DNA-tested for L-2-HGA and HC-HSF4 (D)." — the test results are `NOT FETCHED` until the certificates are on file, so the line names the tests, never a result.

### Setup-Stat-Reframe
Three-beat evidence cadence AI engines preferentially cite: name the problem → attributed statistic → reframe what it means for the reader. Every stat carries a named source (link at sentence START) or gets dropped — no orphan numbers. Use inside PAS-Agitate, health sections, and comparison myth-busting.

### The 4 Ss (testimonial structure)
Specific · Sizzling (switched from another seller? why us?) · Substantiated (real name/UK region per the review system) · Succinct. Only REAL reviews — the rows of `data/reviews.json`; the source repo's review-collection agent was not ported, so a new review arrives only from the breeder.

### The 5 Basic Objections + Objection Block
Every money page answers: no time · no money · won't work for me · don't believe you · don't need it. Sweep each money page against all five; the natural BSUK carriers are the FAQ, the price-transparency section, and the documentation stack. The **"But you might be wondering…"** objection block is a proven CTR lifter — place one before the final CTA, answering the page's #1 unresolved doubt (from PAA/GSC data, not guessed).

---

## EBP Disambiguation (three meanings — say which you mean)
1. **`framework-ebp` skill = Evidence → Benefit → Proof** — credibility-first section writing. Default meaning on BSUK.
2. **Entity catalog EBP = Entity → Benefit → Purpose** (`.claude/skills/bsuk-entity-agent/SKILL.md`) — entity-SEO writing pattern.
3. **Evidence-Based Practice reporting** (problem statement → SMART purpose → evidence-reviewed recommendations) — use for E-E-A-T-heavy health/technical pages and any content a vet might read; on BSUK this collapses into: state the problem, cite the evidence (The Kennel Club / BVA / RSPCA, Link-First), give the recommendation, show our practice.

## Common Mistakes
- **Framework stacking** — one primary framework per section; a page may vary frameworks BY section (that's the distribution matrix), but a single section running PAS+AIDA+4Ps reads as slop.
- **Skeleton showing** — the reader should never see the beats ("Now here's the proof:"). Frameworks are load-bearing walls, not signage.
- **Fabricated Proof/Scarcity/Warning beats** — every framework's persuasion slots stay inside the evidence ledger and Rule 48.
- **Ignoring awareness level** — QUEST on a problem-aware reader wastes their patience; PAS on an unaware reader has no pain to press.
