# Competitor intelligence gate report

BlueStaffyUK rebuild, the second bridge build between project 4 and project 5. Written by hand
from the close-out runs, the pilot outputs under `docs/research/`, `data/competitors.json`, the
spend log and the branch history. Date 2026-09-23. Branch `competitor-intel`, cut from
`foundation` at `db37ca1` and rebased onto `c9c981c` (after `query-augmentation` merged); no
remote, nothing pushed. **Merge:** done by the controller after this report is reviewed — the
merge hash is recorded in `docs/reference/session-log.md` once it exists.

Spec: `docs/superpowers/specs/2026-09-23-competitor-intel-design.md`. Sections §1–§15 are the
definition of done **as amended by §16 (amendments 1–19)**; where a section's literal text and an
amendment disagree, the amendment wins, and every deviation below names the amendment that
records it. Plan: `docs/superpowers/plans/2026-09-23-competitor-intel.md` (its "Executed" note
lists the deviations per task).

This build ships research tooling and one pilot's research, not pages. No page was built or
rebuilt. Every figure below comes from a file in the repo or a command re-run at close-out.

---

## Summary

**What shipped.** The competitor research chain the source repo had, re-based to UK Staffies:
a national registry, per-competitor intel with a BSUK profile, a gap matrix built by script, a
keyword-gap list, LLM citation intel and a two-strategy synthesis whose figures are checked by
script. Every paid call goes through the query-augmentation spend guard.

| Part | File |
|---|---|
| Registry agent | `.claude/agents/bsuk-competitor-registry.md` |
| Intel agent (+ BSUK profile, `--bsuk`) | `.claude/agents/bsuk-competitor-intel.md` |
| Keyword-gap agent | `.claude/agents/bsuk-competitive-keyword-gap-agent.md` |
| LLM-intel agent | `.claude/agents/bsuk-llm-keyword-intel.md` |
| Strategy synthesizer | `.claude/agents/bsuk-strategy-synthesizer.md` |
| Registry rules, derived priority, suspect-seller link guard | `scripts/competitor_registry_check.py` (`npm run check:competitors`, in `check:all`) |
| Gap matrix build and `--check` | `scripts/gap_matrix.py` (`npm run check:gaps`, in `check:all`) |
| Strategy citation check | `scripts/strategy_cite_check.py` |
| Contracts | `schemas/competitors.schema.json`, `schemas/competitor-report.schema.json`, `schemas/llm-intel.schema.json` |
| Tests (collected) | `tests/py/test_competitors_registry.py` (63), `test_gap_matrix.py` (47), `test_strategy_cite_check.py` (56), `test_competitor_spend.py` (7), `test_keyword_gap_script.py` (19), `test_llm_intel.py` (63), `test_agent_snippets.py` (4), `test_strategy_example.py` (5) — 264 in all |
| Fixtures | `tests/py/fixtures/competitors/` (10 files) |
| Pilot outputs | `data/competitors.json`; `docs/research/competitor-registry-proposal-2026-09-23.md` + `.json`; `docs/research/competitors/{trojanstaffuk,pets4homes,rspca,bsuk}.json` + `.md`; `docs/research/gap-matrix-2026-09-23.md`; `docs/research/keyword-gap-2026-09-23.md`; `docs/research/llm-intel/{blue-staffy-puppies-manchester-uk,blue-staffy-puppies-for-sale-leeds}-2026-09-23.json`; `docs/superpowers/sessions/2026-09-23-location-pages-strategy.md` |
| Housekeeping | `data/port-manifest.json` (four rows `deferred` → `rebase`, the registry row added; pricing alert stays `deferred`), `docs/reference/WORKFLOW.md`, `docs/reference/session-log.md`, both registries |
| Budget | `data/settings.json` `query_typical_call_usd` 0.10 → **0.05** (user ruling A, `efdac63`) |

**Commit range.** `a116055..638a6d4` — **49** commits from the spec to the pilot's strategy,
then the close-out fix `7ece4ff` and this report's docs commit. Every one carries
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (49 of 49 counted in `c9c981c..638a6d4`).

**Counts at close-out** (after `7ece4ff`):

| Step | Summary line |
|---|---|
| `python3 -m pytest tests/py -q` | `2375 passed, 27 skipped, 1 xfailed` |
| `npm run -s check:all` | exit **0** |
| `check:competitors` (new) | `competitors: 21 entries; 1 banned domain; 83 files scanned; 0 problems` |
| `check:gaps` (new) | `gaps: gap-matrix-2026-09-23.md matches 4 reports (3 competitors, BSUK profile present)` |
| `check:queries` | `examined 0 pages (0 not built, 2 awaiting rebuild); 0 problems` |
| `check:schema` | `examined 58 pages; 0 blocking, 0 advisory` |
| `check:sitemaps` | `examined 58 built pages, 5 shards, 36 sitemap urls; 0 problems` |
| `check:placeholders` | `placeholders: 1732` (advisory until project 6; +1 is `LICENCE_CLAIM_PLACEHOLDER` named in Known Issue 54) |
| `check:markers` | `examined 265 files; 0 problems` |
| `agents` | `examined 41 agents; 0 problems` |

Pytest moved 2071 → 2375 passed against the query-augmentation close.

**Spend.** This build logged $0.60 (ten registry searches at $0.05, one Leeds ChatGPT answer at
$0.10), taking `data/queries/spend.json` to **$0.80** of the $1.00 cap — all estimates. Firecrawl:
**20 credits** (776 left).

**Verdict.** 3 PASS · 12 PASS-WITH-DEVIATION · 0 FAIL against spec §1–§15 as amended by §16.

## Close-out fixes (`7ece4ff`)

Small defects that would have tripped project 5, each test-first:

| Fix | Test |
|---|---|
| Keyword gap: "licenced" joins the always-high trust words (the same five spellings as llm-intel's licence entity) | `test_every_licence_spelling_is_always_high_like_llm_intels_safety_list` in `tests/py/test_keyword_gap_script.py` |
| LLM intel: `brand_entities` items with `category: local_business` are local businesses (the connector's current shape); a name with no link is kept by `name`, domain null, mapped to the registry only by exact name; schema `named_site` | `test_brand_entities_in_the_local_business_category_are_local_businesses` in `tests/py/test_llm_intel.py` |
| Leeds llm-intel re-derived from its saved response — preflight exit 3, no call; only `local_businesses` changed (three named businesses); the strategy's cite-check still reports 12 sources, 36 figures, 0 problems | `python3 tests/py/test_llm_intel.py docs/research/llm-intel/*.json` → `2 file(s); 0 problem(s)` |
| grill-me, session-closer and `bsuk-content-architect` agree on `docs/superpowers/sessions/<date>-session-brief[-<n>].md`; the synthesizer's same-day `-strategy-2.md` spelled out | agent/skill lint in the suite |
| WORKFLOW: Sprint 0 runs in dependency order; `bsuk-seasonal-content-agent` marked not ported; the component gate points at `src/components/kit/`, `data/design/components.json` and the board's three styles (the named `components.md` never existed) | path guard in the suite |

The docs commit also corrected WORKFLOW's stale monitoring rows (pricing alert deferred, one LLM
engine, 21 registry entries) and the Sprint 0.5 note that required top-pages.

## The pilot

User-approved, controller-run (plan Task 11).

**Registry** — `2bcdbf6` (discovery), `9f3277f` (approved). Ten seeds, one `serp_google` call each
under a `registry-<keyword>` pseudo-slug: blue staffy puppies for sale · staffordshire bull
terrier puppies for sale uk · blue staffy breeder · staffy puppies for sale in London,
Birmingham, Manchester, Leeds and Liverpool · kc registered staffy puppies · staffy puppy price
uk. Proposal: `docs/research/competitor-registry-proposal-2026-09-23.md` (Artifact
https://claude.ai/artifact/6rUP9jPKqVbuvzFvQHoRFG). The user approved **21 sites** with three
edits (wildbluestaffords dropped, the tier-5 entry kept, RSPCA moved to tier 3): tier 1 breeder
5 · tier 2 marketplace/directory 12 · tier 3 breed information 2 · tier 4 rescue 1 · tier 5
suspect seller 1 (`link_allowed: false`, guarded). Priority high 9 · medium 5 · low 7, derived by
the check.

**Intel** — `1c5f1a2`. trojanstaffuk (tier 1), pets4homes (tier 2), rspca (tier 3) and the BSUK
profile (`--bsuk`, indexable sitemap URLs only), 20 Firecrawl credits. Reports in
`docs/research/competitors/`. Findings: BSUK claims "council-licensed" but shows no licence number
(the claim stays `LICENCE_CLAIM_PLACEHOLDER`).

**Gap matrix** — `docs/research/gap-matrix-2026-09-23.md`, 3 competitor reports + BSUK profile,
18 registry entries with no report yet. Page types BSUK lacks: **care-guide 2/3 (high)**; faq,
price, reviews 1/3 (medium). City gaps: none against the three competitors. Priority queue: the
care-guide row, then nine 1/3 keyword rows (blue colour-variant phrases).

**Keyword gaps** — `docs/research/keyword-gap-2026-09-23.md` (`0da8570`), from the BSUK profile:
**4 high** (the full-breed-name listing phrase, the Manchester breed-plus-city listing, a
"staffy puppies quality blue" homepage, the licensed-breeders page), 1 medium (a price
calculator), 3 low; 1 topic already covered; 8 pages skipped with reasons.

**LLM intel** — `0da8570`, one ChatGPT answer per page, UK location:

| Page | Answer | Cost | BSUK cited | Citations | Local businesses | Citation gap | High entities | Format |
|---|---|---|---|---|---|---|---|---|
| `blue-staffy-puppies-manchester-uk` | cached from query augmentation, condensed save | $0 | no | thekennelclub.org.uk | 5 (incl. trojanstaffuk, ukstaffypups) | trojanstaffuk, ukstaffypups | microchip, vaccinations, contract | NOT FETCHED (summary save) |
| `blue-staffy-puppies-for-sale-leeds` | bought, verbatim | $0.10 logged | no | royalkennelclub.com, rspca.org.uk, dbrg.uk | 3 named, no links (close-out fix) | royalkennelclub, rspca | L-2-HGA, HC-HSF4, meet the mother | numbered list, statement opening |

Both on-page checks are provisional (question-file page text; the pages are noindex stubs).

**Strategy** — `docs/superpowers/sessions/2026-09-23-location-pages-strategy.md` (`638a6d4`,
Artifact https://claude.ai/artifact/PpjywspMRJXayQtkfiTki1). Topic: the 28 location pages. **Pick
A — contested stubs first**, not provisional; the named downside is that the care guide waits.
First three builds: the Manchester stub, the licensed-breeder stub, the Leeds stub — each a
project 5 rebuild at its existing URL. `strategy_cite_check.py`: 12 sources, 36 figures checked, 0
problems (re-run at close-out after the Leeds re-derivation: unchanged).

## Spend

| Ledger | Figure |
|---|---|
| `data/queries/spend.json` before this build | $0.20 (three query-augmentation calls on Manchester) |
| This build | $0.60 — 10 × `serp_google` at $0.05 + 1 × `ai_engines` (Leeds) at $0.10 |
| Log total | **$0.80 of the $1.00** `query_total_budget_usd` cap |
| Dashboard | **$0.99185** before the pilot (user, 2026-09-23) — the three earlier calls really cost about $0.008 against $0.20 logged |
| Firecrawl | 20 credits (776 left) |

Every logged figure is an estimate: the connector returns no cost field. By user ruling A,
`query_typical_call_usd` is 0.05 (`efdac63`); the guard budgets `ai_engines` at its largest logged
cost, 0.10. The log's $0.20 of headroom now covers two more LLM-intel pages — Known Issues 45
and 58.

## User and controller rulings during the build

| Ruling | Effect | Where |
|---|---|---|
| Typical DataForSEO call $0.05 (ruling A) | Ten seeds fit the cap | §16.16; `efdac63` |
| Registry: drop wildbluestaffords, keep the tier-5 entry, RSPCA to tier 3 | 21 sites | §16.19; `9f3277f` |
| A noindex BSUK page is not coverage | Stub rows labelled, routed as "rebuild the stub" | §16.8–9; `612f2a6`, `273214c` |
| Keyword-gap rubric (dedicated point, whole-H1 always-high, "tested", "blue", city rules) | Low band restored; rows order-independent | §16.10 |
| `ai_*` filter: drop a question only when all its sources are AI | Page text keeps mixed-source questions | §16.11; `330e3a0` |
| No tools list for connector agents | Tool names are session-specific | §16.15 |
| Missing registry → tier unknown; tie-break by keyword-gap band then matrix share | Synthesizer | §16.14; `0e43583` |
| Intel `--bsuk` may cut brand-name runs | Accepted | Known Issue 51 |

## Open items

Known Issue 42 (the competitor intelligence build) is **closed by this build**. New, in
`docs/reference/session-log.md`:

47. **The link guard misses JSON-escaped URLs** (`https:\/\/`) — none exist today.
48. **`gap_matrix.py` minors** — directory `--write` traceback, case-fold hint, backslash before a pipe.
49. **`strategy_cite_check.py` minors** — a year with no cue word, a `##` after Sources, the Risks message, Strategy A/B sections unchecked.
50. **Registry agent minors** — `-2` proposal suffix, date-only change check, tier-5 notes; `dbrg.uk` candidate; the rank tracker's `last_monitored` field does not exist.
51. **Intel agent minors** — tie-breaks, loose measures, substring page types, pagination, BSUK city count, image-name emails, desktop mobile check, RSPCA map sample, brand-name cuts.
52. **Keyword-gap minors** — foreign-domain URLs, duplicate URLs, places outside `locations.json`, "Greater Manchester", typed "-vs-" order, two-city stub label.
53. **LLM-intel minors** — Manchester condensed save (needs `; refresh`), provisional on-page checks, `EXTRA` not recorded, opening-move edge cases, fixture Instagram link, own-domain logic, dist freshness, noindex regex order, no homepage slug, schemas absent from the system registry.
54. **Research notes for project 5** — matrix `cities` counts a named stub city as covered; the national phrase belongs on the listing page; the licence claim; the fixture's London row.
55. **The former business street address is in `data/locations.json`** (line 385, the old-city breeding-dogs page) — not to be carried into the rebuild.
56. **Session paths and WORKFLOW leftovers** — 46 files still name a bare `sessions/`; stale content-root lines; unported monitoring agents unmarked; stale manifest notes.
57. **Next step — intel on the other 18 registry entries**, then a matrix rebuild.
58. **Next step — LLM intel for the other 26 location pages**, after the cap or typical cost is re-set.

Still open from earlier builds and touched here: **Known Issue 45** (costs unknown — partly
addressed: ruling A and the dashboard figure are recorded; the log is still estimates) and the
pricing alert, rank tracker, branded search and GSC analytics, all project 6.

## Definition of done — spec §1–§15, as amended by §16

| § | Section (amended) | Verdict | Evidence |
|---|---|---|---|
| 1 | Why these agents were not ported | **PASS** | Each source fault is fixed: registry size and tiers set (§4); intel and keyword gap share one page-type table and the keyword gap reuses intel's page lists, no second fetch (`612f2a6`); every count is built by script (`gap_matrix.py`, the keyword-gap and llm-intel heredocs, tested); the "never fabricate" sentence is `strategy_cite_check.py`; LLM intel uses the DataForSEO connector, no vendor keys |
| 2 | Decisions | **PASS-WITH-DEVIATION** | All seven built: five agents, connector through the spend guard, registry ≤ 30 in five tiers (21 approved), scripts count, `bsuk-` names, the 28 cities, marketplaces counted (12 tier-2 entries). **Deviation:** `llm_response`/`llm_mentions` not used — one ChatGPT scraper answer per page, `llm_mentions` NOT FETCHED until the domain is live (§16.11–12) |
| 3 | Data flow | **PASS-WITH-DEVIATION** | Each arrow exercised by the pilot, in order, each step reading files only; stale inputs flagged (30-day rule in every agent). **Deviations:** the matrix reads the BSUK profile, not the page map (§16.5); the strategy path takes a `-2` suffix (§16.14, §16.18) |
| 4 | The registry | **PASS-WITH-DEVIATION** | `data/competitors.json` valid against `schemas/competitors.schema.json`, 21 entries, `check:competitors` 0 problems; 63 tests (≤ 30, root domains, duplicates, own domain, tier-5 `link_allowed`, cities, `seed_hits`); discovery via DataForSEO Google, proposal to the user, file written after "approved" (`9f3277f`). **Deviations:** registrable-domain rule (§16.1); priority derived (§16.2); proposal and two stop tokens (§16.4); ten seeds, final list as run (§16.19) |
| 5 | Competitor intel | **PASS-WITH-DEVIATION** | Ten categories in `schemas/competitor-report.schema.json`; `NOT FETCHED` recorded, never guessed; three reports + the BSUK profile, `last_analyzed` set; wording summarised. **Deviations:** homepage gate, script-fixed keyword/page-type rules, map-and-scrape only, `--bsuk` indexable pages (§16.5, §16.7); no Lighthouse run in the pilot (`lighthouse_performance` NOT FETCHED in all four reports) |
| 6 | Gap matrix | **PASS-WITH-DEVIATION** | `scripts/gap_matrix.py`, 47 tests; `N/M` over fetched competitors, separate not-fetched column, 40/20 % bands, top-ten queue; `--check` in `check:all` (`matches 4 reports`). **Deviations:** BSUK side from `bsuk.json`, §6's sentence corrected (§16.5); hardening (§16.6) |
| 7 | Keyword gap | **PASS-WITH-DEVIATION** | `docs/research/keyword-gap-2026-09-23.md`: every gap names its competitor URL, scored and banded; no fetch (lists within 30 days); licence and health-testing words always high. Script tested (19 tests). **Deviations:** compares against the BSUK profile, noindex not coverage, stub rows as rebuilds, rubric rulings, "licenced" (§16.8–10) |
| 8 | LLM keyword intel | **PASS-WITH-DEVIATION** | `docs/research/llm-intel/` for Manchester and Leeds, raw responses under `data/queries/raw/<slug>/`; citations mapped to the registry, citation gap, entities, answer format; schema + 63 tests. **Deviations:** high = a missing safety entity (§16.12); query fallbacks, `ai_*` filter, provisional page text, `llm_mentions` deferred, `brand_entities` local businesses (§16.11) |
| 9 | Strategy synthesizer | **PASS-WITH-DEVIATION** | `docs/superpowers/sessions/2026-09-23-location-pages-strategy.md`: two strategies, one pick with a WHY of four data points and a named downside, first three steps, artefact table; cite-check 36 figures, 0 problems, run before hand-off. **Deviations:** cite-check rules (§16.13); synthesizer rulings (§16.14) |
| 10 | Spend | **PASS-WITH-DEVIATION** | Every paid call preflighted and recorded: 11 rows this build, no Bing, the Manchester answer reused (exit 3), the Leeds re-derivation made no call (exit 3). **Deviations:** typical 0.05 by ruling A; the $0.90 balance superseded by $0.99185; log $0.80, estimates (§16.16) — Known Issue 45 stays open |
| 11 | Failure handling | **PASS** | Exit 4 and exit 3 tested (`test_competitor_spend.py`) and exit 3 exercised; `NOT FETCHED` counted apart in the matrix; staleness flagged; `check:all` fails on a registry, matrix or schema breach; the tier-5 entry analysable, never linked (link guard) |
| 12 | Guards | **PASS-WITH-DEVIATION** | Registry test, `check:gaps`, `check:competitors`, cite-check tests; the link guard refuses tier-5 hosts; the five agents pass frontmatter, marker gate (265 files), fact lint and path guard; manifest rows moved to `rebase`, pricing alert `deferred`; WORKFLOW rewritten (`c98778b`, `6b9714e`, `7ece4ff`). **Deviations:** link guard scans source roots, not `dist/`, and misses JSON-escaped URLs (§16.3, Known Issue 47); WORKFLOW order and gates (§16.17) |
| 13 | Build order | **PASS-WITH-DEVIATION** | Steps 1–12 in order (commits in the plan's Executed note); step 13's gate report is this file; no full run was asked for. **Deviation:** the pilot also bought LLM intel for Leeds and ran intel `--bsuk` (§16.19). **Outstanding, by instruction:** Artifacts and the merge, by the controller |
| 14 | Testing | **PASS-WITH-DEVIATION** | 264 new tests, no paid calls, fixtures for every listed case (duplicate domains, subdomains, unknown city, tier-5, NOT FETCHED in M, matrix drift, an unsourced figure, a missing source, an unknown spend source); agents through the instruction-tree tests; the pilot as the end-to-end test, reviewed by the user at each stop. **Deviation:** added script-level tests of the agents' embedded heredocs (`test_keyword_gap_script.py`, `test_llm_intel.py`, `test_agent_snippets.py`) |
| 15 | Out of scope | **PASS** | No pricing alert, rank tracker, branded search or GSC analytics built; no strategists or visual intelligence; intel on 3 of 21 only — the rest is Known Issue 57 |

**Verdict count: 3 PASS · 12 PASS-WITH-DEVIATION · 0 FAIL.**

Every deviation is an amendment in §16 — a plan refinement, a review finding or a ruling — and
none weakens a gate: most make a check stricter (registrable domains, derived priority,
validated reports, whole-token figures) or record what the live pilot showed (the page map
cannot say what BSUK covers; noindex stubs are gaps, not coverage; the real per-call cost).
