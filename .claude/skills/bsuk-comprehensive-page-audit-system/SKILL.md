---
name: bsuk-comprehensive-page-audit-system
description: "Use when auditing any BlueStaffyUK page deeply — SEO, semantic, AEO, entity, UX, CRO, visual-asset, and backlink — to get one brutal scored verdict with prioritized fixes. Runs as a chain over existing BSUK specialists. Triggers: \"audit this page\", \"deep audit\", \"why isn't this page ranking\", \"page audit\"."
---

# BlueStaffyUK Comprehensive Page Audit System

## Overview
A brutal, no-fluff 17-section deep audit of **ONE** page, run as a **skill chain**. It does not re-do work the BSUK system already owns — each of the 17 sections **routes to the specialist that owns it** (keyword-verifier for technical SEO, the entity agent for entities, internal-link-agent for links, conversion-tracker for CRO, and so on). This skill itself owns only the **5 lenses BSUK lacked** — the AEO score, the entity-coverage score, the visual-asset decision table, the backlink-magnet score, and the unified verdict — plus it **assembles one dated report** out of all the routed outputs.

The contract is honesty: every recommendation must be justified by **business or ranking value**, never by taste. If a section is fine, say it's fine and move on. If it's broken, say exactly how and what it costs. The output is a single scored verdict a busy breeder can act on top-down.

## When to Use / Not
**USE** — strategic audit of a page that is **live or already built**, any type, any time. "Audit this page", "why isn't this page ranking", "deep audit", "is this page good enough".

**NOT** —
- **Pre-build planning** of a page that does not exist yet → use `bsuk-content-audit-agent` (intent → competitor → action plan → internal links, before you write).
- **Final mechanical QA gate** immediately before deploy → use `manual-auditor-check` (the 29-check `dist/` pass; **interior pages only**).

This skill is **broader** than `manual-auditor-check` and deliberately **covers the page types that one excludes** — comparison, location, for-sale/commercial, and blog pages all get a full audit here.

## BSUK-Safety (guardrail — CLAUDE.md already enforces most of this)
Subagents **inherit the project `CLAUDE.md`**, so an un-guided auditor is already BSUK-safe. This block is a **checklist to confirm, not a re-teach**:
- **Palette comes from `rules/design.md`** — refer to the tokens, never hardcode a colour in a recommendation.
- **No visible date** applies to the **site page** the audit recommends changes to — freshness lives in schema `dateModified` only. It does **not** apply to the audit report file itself (a normal dated doc in `docs/superpowers/sessions/`).
- **No fabrication** — every §3–4 competitor metric must be a **REAL fetch** (Firecrawl `mcp__firecrawl-mcp__firecrawl_scrape` / `firecrawl_search`; Playwright fallback). Never invent DA, backlinks, or traffic. All claims bounded by `data/quality/evidence-ledger.json`; a licence or statute claim is written LICENCE_CLAIM_PLACEHOLDER / LEGAL_CLAIM_PLACEHOLDER in prose until it is confirmed.
- **Proposed copy** uses **first-person BlueStaffyUK voice** (we / us / our) and respects the `.claude/skills/anti-ai-writing/SKILL.md` blacklist.
- **Confidence Gate ≥97%** before editing any site file — this skill **RECOMMENDS**; it does **not** auto-edit pages unless explicitly told to.

## Page-Type Map (read first → sets section weighting)
Before auditing, map the page via `data/page-map.json` to one of:

**Homepage · Location (one of the 28 UK cities) · Comparison ([X] vs [Y]) · Variant/Attribute · For-sale/Commercial · Care/Health Guide · Breed Guide · Blog · Interior · Hub.**

Then tag the **funnel stage**: **TOFU** (top — discovery/educational) · **MOFU** (middle — comparison/consideration) · **BOFU** (bottom — purchase intent).

The page type + funnel stage **re-weights** which sections matter most:

| Page type | Heaviest axes |
|---|---|
| For-sale / Commercial / Variant-Attribute (BOFU) | **CRO + trust** (Product/Offer schema, delivery line, social proof) |
| Care/Health Guide · Breed Guide · Blog (TOFU) | **AEO + entity + semantic** (citation-readiness, coverage, topical depth) |
| Location (one of the 28 UK cities) | **local intent + internal links** (city entity coverage, delivery, hub linking) |
| Comparison ([X] vs [Y], MOFU) | **comparison tables + entity coverage** (structured data, decision support) |

State the weighting explicitly in the report header so the scorecard is read in context.

## The Chain — Section → Specialist Routing
Run each section in order. "Run / dispatch" names the specialist that owns the work; "This skill adds" is what this audit layers on top.

| # | Section | Run / dispatch | This skill adds |
|---|---|---|---|
| 1 | Page identification | self + `data/page-map.json` | page-type + funnel tag |
| 2 | Primary search intent | self (GSC data is NOT FETCHED until project 6) | "what the user REALLY wants" |
| 3 | Top-3 SERP competitors | `bsuk-framework-agent` / `bsuk-competitor-intel` (**REAL fetch**) | — |
| 4 | Why BSUK wins / loses | self, from §3 | **Competitive-Advantage score /10** |
| 5 | Technical SEO | `bsuk-keyword-verifier` + `rules/` (the nine packs) | per-element /10 |
| 6 | Semantic SEO | `bsuk-content-audit-agent` + `.claude/skills/framework-aio-geo/SKILL.md` | missing-topics list |
| 7 | Entity audit | `bsuk-entity-incorporation-agent` working the `entity-4-move-loop` in `rules/copy.md` (+ `.claude/skills/bsuk-entity-agent/SKILL.md` vocab, the evidence ledger) | **Entity-coverage /10** |
| 8 | NLP / LSI | `.claude/skills/keyword-cluster/SKILL.md` + `bsuk-keyword-verifier` | must-add terms (no stuffing) |
| 9 | AEO | `.claude/skills/framework-aio-geo/SKILL.md` | **AEO /10 rubric** |
| 10 | Content architecture | `.claude/skills/framework-heading-hierarchy/SKILL.md` + `.claude/skills/section-auditor/SKILL.md` | improved H-tree |
| 11 | Visual asset audit | `rules/images.md` | **Visual-need table** |
| 12 | Image prompts | `.claude/skills/image-prompt-generator/SKILL.md` (`rules/images.md` + negatives + palette) | prompts for §11 **YES** only |
| 13 | Special content blocks | `bsuk-interactive-component` / `bsuk-infographic-builder` | relevant-only list |
| 14 | Internal links | `.claude/skills/internal-link-agent/SKILL.md` | source → dest → anchor |
| 15 | Backlink opportunity | self (the source repo's backlink agent was not ported — source repo only) | **Backlink-magnet /10** |
| 16 | CRO | self (the source repo's conversion tracker was not ported — source repo only) | **CRO /10** |
| 17 | Final scoring + verdict | self | **Scorecard + verdict tier** |

## The 5 Owned Scorers
These are the lenses the un-guided baseline missed. Use the exact rubrics — no narrative "92/100".

### §9 — AEO /10 (Answer-Engine Optimization)
Award **+1 for each item present (YES), 0 if absent (NO)**. Report every item YES/NO, then the total /10:
1. Quick-answer box (direct answer in the first screenful)
2. Snippet-ready one-sentence definition
3. Comparison table
4. FAQ block — **visible AND `FAQPage` schema** (both required)
5. Decision tree / checklist
6. Bullet summary
7. Structured data with the **correct `@type`** for the page
8. A statistic or research-backed claim (cited)
9. Entity-dense first paragraph
10. Direct-question H2s ("What…", "How…", "Is…", "Can…")

### §7 — Entity-coverage /10
Extract every entity on the page across these classes: **species, diseases, brands, foods, breeders, organisations, locations, products, scientific concepts.** Score `/10 = entities covered ÷ entities expected-for-this-page-type` (rounded). List the **Important Missing Entities** and, per entity, **why it matters for AI** (what query/citation it unlocks). **Never assert a Ledger-unverified credential** (no L-2-HGA/HC-HSF4/board-cert claim beyond what `data/quality/evidence-ledger.json` records as proven — the parents' DNA results are `NOT FETCHED` today).

### §11 — Visual-need (per section — honest, NOT everywhere)
For each section answer **YES (Mandatory) / YES (Recommended) / MAYBE / NO**. Answer YES **only** if a visual improves **comprehension, retention, shareability, backlinks, or conversion** — never decorative. Output a table:

| Section | Need Visual? | Type | Why |
|---|---|---|---|

Types are drawn from `IMAGE-DESIGNS.md §5` scene types **plus** infographic / table / calculator. A page with three honest "NO"s and one "YES (Mandatory)" is a correct, good outcome.

### §15 — Backlink-magnet /10
Score the page 0–10 on its ability to **earn links**. If the score is **≥6**, name the magnet — original breeder data, an infographic, a calculator, an interactive tool, or research — **and state why another site would link to it** (what gap it fills for them).

### §17 — Verdict tier
Assign exactly one tier with the precise reason:
- **Elite** — top of SERP, nothing material to fix.
- **Strong** — competitive; only minor gains left.
- **Good-but-incomplete** — solid base, one or two high-value gaps.
- **Average** — present but undifferentiated; loses to competitors on specifics.
- **Weak** — multiple structural failures; underperforms its intent.
- **Major-rebuild** — wrong structure/intent; rebuild rather than patch.

## Output Contract (save to `docs/superpowers/sessions/<date>-audit-<slug>.md`)
Reproduce all 17 sections in order (Page ID → Final Verdict), then close with:

**FINAL SCORECARD**

| Axis | Score |
|---|---|
| SEO | /10 |
| Semantic | /10 |
| AEO | /10 |
| Entity | /10 |
| UX | /10 |
| Visual | /10 |
| CRO | /10 |
| Backlink | /10 |
| Competitive-Advantage | /10 |
| **Verdict** | *(tier)* |

**Prioritized Fix List** — ordered **highest business impact first**, each line stating the **WHY** (the ranking/conversion/citation value it unlocks), not just the what. (The report file is a dated doc in `docs/superpowers/sessions/`; the no-visible-date rule applies to the *site page*, not this report.)

## Batch / Site-Wide Mode
Given a page list (or all of `src/pages/`), run the audit per page but emit **only the FINAL SCORECARD row per page** into one table, **sorted ascending by Competitive-Advantage score** — that table is the **audit backlog** (worst pages first). Feed it to `bsuk-strategy-synthesizer` for sequencing. To control cost, produce **full 17-section reports only for the worst N pages**; the rest stay as scorecard rows until promoted.

## Output Rules
- **Brutal honesty** — no grade inflation; a 6/10 is a 6/10.
- **No generic advice** — every rec is specific to this page.
- **No fluff** — cut filler; if a section passes, say so in one line.
- **Explain WHY** — every recommendation carries its business/ranking/citation value.
- **Never force visuals** — "NO" is a valid, common answer in §11.
- **Prioritize business impact** — order fixes by what moves rankings or conversions.
- **Optimize for 2026 search** — AI Overviews, ChatGPT/Perplexity citations, passage ranking, and zero-click results are first-class targets, not afterthoughts.
