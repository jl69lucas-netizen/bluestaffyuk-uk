# Query augmentation, thread sourcing and the location-page rules — design

Status: approved in brainstorm 2026-09-23. Branch `query-augmentation`, cut from `foundation`
at `db37ca1` (project 4 merged). A bridge build between project 4 and project 5: it closes
Known Issue 17 before project 5 builds 28 city pages.

## 1. Decisions

| # | Decision | Picked |
|---|---|---|
| 1 | Scope | Query augmentation plus the thread-sourcing half of CAG's `reddit-strategy`, re-based for BSUK. `cag-visual-intelligence` stays an open item |
| 2 | Question sources | DataForSEO (via the claude.ai connector) first; free sources as fallback; offline bank always |
| 3 | `reddit-strategy` scope | Thread sourcing only. "Reddit-modifier" pages are recorded as a later option, not built |
| 4 | Pages served | Every page builder — location, comparison, blog, puppy; location pages pilot it |
| 5 | Enforcement | A per-page question file plus a check that fails `npm run check:all` |
| 6 | Who calls DataForSEO | The skill calls the connector; scripts merge, score, cap spend and gate. No new credentials |
| 7 | FAQ format | The user's Illinois template: three blocks (top 5–7, middle 5–7, bottom 7–10), 15–20 questions, each an H3 |
| 8 | Location section count | Competitors' count + 3 research-suggested sections (rule in §6). Never a fixed 22 |
| 9 | Skill authoring | `superpowers:writing-skills` (RED/GREEN/REFACTOR with subagents); scripts by `superpowers:test-driven-development` |

## 2. Components

New:

- `.claude/skills/bsuk-query-augmentation/SKILL.md` — input: slug, page type, primary keyword.
  Drives the paid and free sources, runs the scripts, hands the page builder its question file.
- `.claude/skills/bsuk-reddit-threads/SKILL.md` — the thread-sourcing protocol from CAG's
  `reddit-strategy` (derive queries from the page; search via the `research-recency` ladder;
  score; open and verify; log), re-based to Staffy and UK subreddits/forums. Callable alone.
- `scripts/query_augment.py` — `--preflight <slug>` (cache and budget check) and
  `<slug>` (merge, dedupe, score, assign, write the question file).
- `scripts/query_coverage_check.py` — the gate, added to `check:all`.
- `data/queries/<slug>.json`, `data/queries/raw/<slug>/`, `data/queries/spend.json`.
- `schemas/queries.schema.json` — the question-file contract.
- `docs/reference/location-page-template.md` — the Illinois template converted to BSUK (§7).
- `tests/py/test_query_augment.py`, `tests/py/test_query_coverage_check.py`, fixtures of
  recorded DataForSEO responses under `tests/py/fixtures/queries/`.

Changed:

- `bsuk-location-page-builder` Step 1 (section rule, §6) and Step 5 (FAQ, §5); the
  query-augmentation paragraph becomes a call to the new skill.
- `bsuk-comparison-page-builder`, `bsuk-blog-post`, `bsuk-puppy-page-builder`: call the skill
  before writing.
- `data/settings.json`: `query_budget_usd` (start 0.50; set from the live test).
- `data/port-manifest.json`: re-file `reddit-strategy` (thread half ported as
  `bsuk-reddit-threads`); add rows for the ten CAG files the manifest never recorded
  (`cag-bird-listing-page`, `cag-bird-page-build`, `cag-bird-page-excellence`,
  `cag-bird-personality`, `cag-clutch-manager`, `cag-timneh-specialist`,
  `cag-species-guide-builder`, `cag-variant-specialist`, `cag-competitor-pricing-alert-agent`,
  `cag-competitor-registry`) with a stated reason each.
- `docs/reference/session-log.md`: close Known Issue 17; open items for reddit-modifier pages
  and `cag-visual-intelligence`.
- Regenerated `docs/reference/system-registry.md` (57 skills).

## 3. Data flow

1. **Preflight.** `query_augment.py --preflight <slug>` exits 0 (proceed), 3 (cached — no call)
   or 4 (budget would be exceeded — stop and report). Run before every paid call.
2. **Paid, via the DataForSEO connector:** Google organic SERP for the primary keyword (PAA,
   related searches, top-10 URLs); Bing organic SERP (top-10 URLs); AI-engine answers for the
   keyword (the questions and entities the answer assembles). Each raw response saved to
   `data/queries/raw/<slug>/<source>.json`; its reported `cost` appended to `spend.json`.
3. **Free:** `bsuk-reddit-threads` through the `research-recency` ladder (Firecrawl → WebFetch →
   headless browser → `/last30days`). Output `raw/<slug>/threads.json`. Unreachable =
   `NOT FETCHED`, never invented. Fallback for step 2 when the connector is absent or out of
   credit: browser PAA (`bsuk-paa-agent` protocol) and Firecrawl search.
4. **Offline:** the question bank in `bsuk-paa-agent`, `data/faq.json`, and the fact files.
5. **Merge.** `query_augment.py <slug>` writes `data/queries/<slug>.json`.
6. **Write.** The page builder writes from the file and fills each `covered_by`.
7. **Gate.** `query_coverage_check.py` over the built `dist/`.

## 4. The question file

```json
{
  "slug": "blue-staffy-puppies-manchester-uk",
  "page_type": "location",
  "primary_keyword": "blue staffy puppies manchester",
  "fetched": "2026-09-23",
  "spend_usd": 0.04,
  "sources": { "serp_google": "ok", "serp_bing": "ok", "ai_engines": "ok", "threads": "ok", "bank": "ok" },
  "competitors": [
    { "url": "…", "google_pos": 1, "bing_pos": 3, "h2_raw": 16, "h2_clean": 12, "outlier": false }
  ],
  "section_target": { "matched": 12, "set_by": "…", "extra": 3, "total": 15 },
  "extra_sections": [ { "topic": "…", "question_ids": ["q-…"] } ],
  "questions": [
    {
      "id": "q-delivery",
      "question": "Do you deliver Staffy puppies to Manchester?",
      "found_in": ["serp_google_paa", "ai_chatgpt", "thread:r/StaffordshireBullTerrier/abc123"],
      "score": 9,
      "must_answer": true,
      "faq": "top",
      "fact_source": "data/settings.json#delivery_min_gbp",
      "blocked": null,
      "covered_by": { "where": "faq", "text": "Do you deliver Staffy puppies to Manchester?" }
    }
  ]
}
```

Scoring (deterministic, in `query_augment.py`):

- **Evidence:** +1 per distinct source type the question appears in (Google PAA, related
  searches, Bing, AI engine, verified thread, bank).
- **Page-type fit:** a fixed weight table per page type (location: delivery/distance/collection
  highest; comparison: "X vs Y"; puppy: price/deposit/availability; blog: the post's topic).
- **Dedupe first:** questions that normalise to the same text merge, keeping every source.
- **Fact rule:** a question can be `must_answer` only when `fact_source` points at a real key in
  a data file. Otherwise `must_answer: false, blocked: "unverified fact"`. The gate can never
  force an invented claim.
- **City-dependent answers** use only facts that exist. `data/locations.json` today holds stubs
  (no distance, no delivery band); a delivery answer states the locked £200–£350 range "priced by
  distance" and the city name. Per-city bands are out of scope until Lisa Bright supplies them.

## 5. FAQ rules (from the Illinois template)

- Three blocks: **top** 5–7 (buying and logistics: price, deposit, delivery to this city,
  reserving), **middle** 5–7 (process and trust: paperwork, health testing, visiting,
  collection age), **bottom** 7–10 (breed and lifestyle: flats, other pets, training,
  lifespan 12–14, coat). 15–20 in total.
- Each question is an H3; a concise direct answer follows; internal/external links sit inside
  answers, link-first (`link-first-anchors`).
- Block assignment by topic table per page type; order within a block by score.
- FAQPage schema carries exactly the visible questions, no more.
- If the pool cannot supply 15 fact-backed questions, the run **stops** and lists the blocked
  questions — no padding.

## 6. Location section rule

1. **Pool:** the top-5 breeder/location pages for the city query on Google plus the top-5 on
   Bing, merged; marketplaces and directories excluded.
2. **Clean:** strip non-content H2s (sidebar, footer, related posts, repeated CTAs).
3. **Match:** the highest cleaned H2 count in the pool. If it exceeds 1.5× the next highest, it
   is recorded as an outlier and the next highest is matched.
4. **+3:** three extra sections from the query pool's strongest topics no pooled page covers.
5. **Count only body H2s** on both sides. Hero, counter, trust strip, TOC, key takeaways,
   reviews, newsletter, form and the three FAQ blocks are the fixed frame and never counted.
6. **Record** every competitor's URL, Google and Bing position, raw and cleaned counts, and which
   page set the number, in the question file and on the board.
7. Fewer than three usable pages is a finding: match what exists.

## 7. The converted template

`docs/reference/location-page-template.md` keeps the Illinois template's structure of intent
(key takeaways, reviews top/middle/bottom, newsletter, conversational question headers with
opening paragraphs, link-first anchors, varied anchor text, delivery/cities/local
activities/regulations/climate topics, voice-search phrasing) and converts it:

- MFS → BlueStaffyUK, Lisa Bright, Carlisle · Cumbria. Maltipoo/Maltese types → the locked pups
  and prices (£1,500 / £1,700), deposit £500 refundable, delivery £200–£350 by distance.
- State → city. Airports → roads, motorway junctions, stations for collection. Dog parks →
  local walks. State regulations → UK law (Dangerous Dogs Act — Staffies are not banned;
  microchipping). AKC → The Kennel Club. USD → £.
- **Dropped as MFS-only or unbacked:** 20+ years, 10-year health guarantee, ENS, Puppy Culture,
  Embark, USDA licence (→ `LICENCE_CLAIM_PLACEHOLDER`), "5,000+ subscribers", invented
  testimonials (three real reviews + `REVIEW_PLACEHOLDER` slots), BBB rating.
- **Resized:** "50+ internal links" → every relevant internal target at least once plus varied
  repeats; "150+ entities" → as many real local entities as the city supports, none invented.
- Section count: §6, not 22. FAQ: §5.

The file passes the fact lint and path guard like any `docs/reference` document.

## 8. Spend cap

- `spend.json` logs `{ts, slug, endpoint, cost_usd}` per paid call. `query_budget_usd` in
  settings caps one run; preflight refuses when log + typical call cost would exceed it.
- Cached raw responses are never re-bought; `--refresh` is explicit.
- The live pilot (§11 step 4) measures real cost per city; the cap is set from it. The account
  holds $1.

## 9. Failure handling

| Failure | Behaviour |
|---|---|
| Connector absent or out of credit | Free fallback; `sources.*: "fallback"`; run continues |
| Source still blocked after the ladder | `NOT FETCHED`; no questions invented |
| Bing not returned by DataForSEO | Bing half via Firecrawl/WebFetch/browser; else `NOT FETCHED` |
| Fewer than 3 usable competitors | Finding recorded; match what exists |
| Fewer than 15 fact-backed FAQ questions | Stop; list blocked questions for the user |
| Budget reached | Preflight exit 4; stop and report spend |

## 10. The gate

`scripts/query_coverage_check.py`, in `npm run check:all`, for every built page with a question
file. Fails when:

1. FAQ total is outside 15–20, a block is outside its range, or a question is not an H3.
2. A `must_answer` question's `covered_by.text` is absent from the built page, or the answer
   after it is empty.
3. FAQPage schema questions differ from the visible FAQ questions.
4. An `extra_sections` topic has no matching body H2.
5. Body H2 count is below `section_target.total` (location pages).

Prints `examined N pages; 0 problems`. Pages without a question file are skipped and counted, so
existing project 4 pages stay green until they are re-run.

## 11. Build order

1. Convert the Illinois template → `docs/reference/location-page-template.md`.
2. Question-file schema + `query_augment.py` + tests (TDD, recorded fixtures).
3. `query_coverage_check.py` + tests; wire into `check:all`.
4. Live pilot on Manchester: measure cost, confirm Bing via DataForSEO, set the cap.
5. `bsuk-reddit-threads` via writing-skills (RED baseline → GREEN → REFACTOR).
6. `bsuk-query-augmentation` via writing-skills.
7. Rewrite location builder Steps 1 and 5; point comparison, blog and puppy builders at the
   skill.
8. Housekeeping: manifest rows, session log, registries.
9. Close-out: whole-branch review, gate report Artifact, merge to `foundation`, session closer
   names project 5.

## 12. Testing

- Pytest for merge, dedupe, scoring, block assignment, fact rule, preflight exits, outlier guard
  and all five gate rules — passing and failing fixture each. No live calls in tests.
- Writing-skills baseline: a subagent given the Manchester task without the skills; record its
  failures (invented questions, FAQ count, fixed sections, skipped Bing, overspend); write the
  skills against them; re-run until it complies.
- Existing guards stay green: fact lint, skills frontmatter, table lint, path guard, registries,
  marker gate.

## 13. Out of scope

Reddit-modifier pages; `cag-visual-intelligence`; building any of the 28 city pages (project 5);
re-running the twelve project 4 pages; per-city delivery bands; scheduled/automatic refreshes.
