# Query augmentation, thread sourcing and the location-page rules — design

Status: approved in brainstorm 2026-09-23. Branch `query-augmentation`, cut from `foundation`
at `db37ca1` (project 4 merged). A bridge build between project 4 and project 5: it closes
Known Issue 17 before project 5 builds 28 city pages.

Executed 2026-09-23 on the same branch. What changed during execution is recorded in §14; the
sentences it supersedes are marked in place and left as written.

## 1. Decisions

| # | Decision | Picked |
|---|---|---|
| 1 | Scope | Query augmentation plus the thread-sourcing half of CAG's `reddit-strategy`, re-based for BSUK. `cag-visual-intelligence` stays an open item |
| 2 | Question sources | DataForSEO (via the claude.ai connector) first; free sources as fallback; offline bank always |
| 3 | `reddit-strategy` scope | Thread sourcing only. "Reddit-modifier" pages are recorded as a later option, not built |
| 4 | Pages served | Every page builder — location, comparison, blog, puppy; location pages pilot it |
| 5 | Enforcement | A per-page question file plus a check that fails `npm run check:all` |
| 6 | Who calls DataForSEO | The skill calls the connector; scripts merge, score, cap spend and gate. No new credentials |
| 7 | FAQ format | The user's Illinois template: three blocks (top 5–7, middle 5–7, bottom 7–10), 15–20 questions, each an H3 (amended — see §14.13) |
| 8 | Location section count | Competitors' count + 3 research-suggested sections (rule in §6). Never a fixed 22 (amended — see §14.4) |
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
- `data/queries/<slug>.json`, `data/queries/raw/<slug>/`, `data/queries/spend.json`. (amended — see §14.3, §14.8)
- `schemas/queries.schema.json` — the question-file contract.
- `docs/reference/location-page-template.md` — the Illinois template converted to BSUK (§7).
- `tests/py/test_query_augment.py`, `tests/py/test_query_coverage_check.py`, fixtures of
  recorded DataForSEO responses under `tests/py/fixtures/queries/`. (amended — see §14.20)

Changed:

- `bsuk-location-page-builder` Step 1 (section rule, §6) and Step 5 (FAQ, §5); the
  query-augmentation paragraph becomes a call to the new skill.
- `bsuk-comparison-page-builder`, `bsuk-blog-post`, `bsuk-puppy-page-builder`: call the skill
  before writing.
- `data/settings.json`: `query_budget_usd` (start 0.50; set from the live test). (amended — see §14.9)
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
   or 4 (budget would be exceeded — stop and report). Run before every paid call. (amended — see §14.14, §14.7)
2. **Paid, via the DataForSEO connector:** Google organic SERP for the primary keyword (PAA,
   related searches, top-10 URLs); Bing organic SERP (top-10 URLs) (amended — see §14.5); AI-engine answers for the
   keyword (the questions and entities the answer assembles) (amended — see §14.7). Each raw response saved to
   `data/queries/raw/<slug>/<source>.json`; its reported `cost` appended to `spend.json`. (amended — see §14.6, §14.7, §14.8)
3. **Free:** `bsuk-reddit-threads` through the `research-recency` ladder (Firecrawl → WebFetch →
   headless browser → `/last30days`). Output `raw/<slug>/threads.json`. Unreachable =
   `NOT FETCHED`, never invented. Fallback for step 2 when the connector is absent or out of
   credit: browser PAA (`bsuk-paa-agent` protocol) and Firecrawl search. (amended — see §14.10)
4. **Offline:** the question bank in `bsuk-paa-agent`, `data/faq.json`, and the fact files.
5. **Merge.** `query_augment.py <slug>` writes `data/queries/<slug>.json`.
6. **Write.** The page builder writes from the file and fills each `covered_by`.
7. **Gate.** `query_coverage_check.py` over the built `dist/`. (amended — see §14.15)

## 4. The question file

The example below predates the schema as built (amended — see §14.18).

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
  searches, Bing, AI engine, verified thread, bank). (amended — see §14.12)
- **Page-type fit:** a fixed weight table per page type (location: delivery/distance/collection
  highest; comparison: "X vs Y"; puppy: price/deposit/availability; blog: the post's topic).
- **Dedupe first:** questions that normalise to the same text merge, keeping every source. (amended — see §14.12)
- **Fact rule:** a question can be `must_answer` only when `fact_source` points at a real key in
  a data file. Otherwise `must_answer: false, blocked: "unverified fact"`. The gate can never
  force an invented claim. (amended — see §14.11)
- **City-dependent answers** use only facts that exist. `data/locations.json` today holds stubs
  (no distance, no delivery band); a delivery answer states the locked £200–£350 range "priced by
  distance" and the city name. Per-city bands are out of scope until Lisa Bright supplies them.

## 5. FAQ rules (from the Illinois template)

- Three blocks: **top** 5–7 (buying and logistics: price, deposit, delivery to this city,
  reserving), **middle** 5–7 (process and trust: paperwork, health testing, visiting,
  collection age), **bottom** 7–10 (breed and lifestyle: flats, other pets, training,
  lifespan 12–14, coat). 15–20 in total. (amended — see §14.13)
- Each question is an H3; a concise direct answer follows; internal/external links sit inside
  answers, link-first (`link-first-anchors`).
- Block assignment by topic table per page type; order within a block by score. (amended — see §14.12)
- FAQPage schema carries exactly the visible questions, no more.
- If the pool cannot supply 15 fact-backed questions, the run **stops** and lists the blocked
  questions — no padding. (amended — see §14.13)

## 6. Location section rule

1. **Pool:** the top-5 breeder/location pages for the city query on Google plus the top-5 on
   Bing, merged; marketplaces and directories excluded. (amended — see §14.1, §14.2)
2. **Clean:** strip non-content H2s (sidebar, footer, related posts, repeated CTAs). (amended — see §14.3)
3. **Match:** the highest cleaned H2 count in the pool. If it exceeds 1.5× the next highest, it
   is recorded as an outlier and the next highest is matched.
4. **+3:** three extra sections from the query pool's strongest topics no pooled page covers. (amended — see §14.4)
5. **Count only body H2s** on both sides. Hero, counter, trust strip, TOC, key takeaways,
   reviews, newsletter, form and the three FAQ blocks are the fixed frame and never counted. (amended — see §14.16)
6. **Record** every competitor's URL, Google and Bing position, raw and cleaned counts, and which
   page set the number, in the question file and on the board. (amended — see §14.3, §14.18)
7. Fewer than three usable pages is a finding: match what exists. (amended — see §14.4, §14.21)

## 7. The converted template

`docs/reference/location-page-template.md` keeps the Illinois template's structure of intent
(key takeaways, reviews top/middle/bottom, newsletter, conversational question headers with
opening paragraphs, link-first anchors, varied anchor text, delivery/cities/local
activities/regulations/climate topics, voice-search phrasing) and converts it:

- MFS → BlueStaffyUK, Lisa Bright, Carlisle · Cumbria. Maltipoo/Maltese types → the locked pups
  and prices (£1,500 / £1,700), deposit £500 refundable, delivery £200–£350 by distance.
- State → city. Airports → roads, motorway junctions, stations for collection. Dog parks →
  local walks. State regulations → UK law (Dangerous Dogs Act — Staffies are not banned;
  microchipping) (amended — see §14.17). AKC → The Kennel Club. USD → £.
- **Dropped as MFS-only or unbacked:** 20+ years, 10-year health guarantee, ENS, Puppy Culture,
  Embark, USDA licence (→ `LICENCE_CLAIM_PLACEHOLDER`), "5,000+ subscribers", invented
  testimonials (three real reviews + `REVIEW_PLACEHOLDER` slots), BBB rating.
- **Resized:** "50+ internal links" → every relevant internal target at least once plus varied
  repeats; "150+ entities" → as many real local entities as the city supports, none invented.
- Section count: §6, not 22. FAQ: §5.

The file passes the fact lint and path guard like any `docs/reference` document.

## 8. Spend cap

- `spend.json` logs `{ts, slug, endpoint, cost_usd}` per paid call. `query_budget_usd` in
  settings caps one run; preflight refuses when log + typical call cost would exceed it. (amended — see §14.6, §14.9)
- Cached raw responses are never re-bought; `--refresh` is explicit. (amended — see §14.10)
- The live pilot (§11 step 4) measures real cost per city; the cap is set from it. The account
  holds $1. (amended — see §14.6)

## 9. Failure handling

| Failure | Behaviour |
|---|---|
| Connector absent or out of credit | Free fallback; `sources.*: "fallback"`; run continues (amended — see §14.10) |
| Source still blocked after the ladder | `NOT FETCHED`; no questions invented |
| Bing not returned by DataForSEO | Bing half via Firecrawl/WebFetch/browser; else `NOT FETCHED` (amended — see §14.5) |
| Fewer than 3 usable competitors | Finding recorded; match what exists |
| Fewer than 15 fact-backed FAQ questions | Stop; list blocked questions for the user (amended — see §14.13) |
| Budget reached | Preflight exit 4; stop and report spend |

## 10. The gate

`scripts/query_coverage_check.py`, in `npm run check:all`, for every built page with a question
file (amended — see §14.15). Fails when:

1. FAQ total is outside 15–20, a block is outside its range, or a question is not an H3. (amended — see §14.15)
2. A `must_answer` question's `covered_by.text` is absent from the built page, or the answer
   after it is empty.
3. FAQPage schema questions differ from the visible FAQ questions.
4. An `extra_sections` topic has no matching body H2. (amended — see §14.15)
5. Body H2 count is below `section_target.total` (location pages). (amended — see §14.4, §14.16)

Prints `examined N pages; 0 problems`. Pages without a question file are skipped and counted, so
existing project 4 pages stay green until they are re-run. (amended — see §14.15)

## 11. Build order

1. Convert the Illinois template → `docs/reference/location-page-template.md`.
2. Question-file schema + `query_augment.py` + tests (TDD, recorded fixtures). (amended — see §14.20)
3. `query_coverage_check.py` + tests; wire into `check:all`.
4. Live pilot on Manchester: measure cost, confirm Bing via DataForSEO, set the cap. (amended — see §14.5, §14.6)
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

Reddit-modifier pages; `cag-visual-intelligence`; building any of the 28 city pages (project 5) (amended — see §14.19);
re-running the twelve project 4 pages; per-city delivery bands; scheduled/automatic refreshes.

## 14. Amendments during execution (2026-09-23)

Each item names where it came from: a **user ruling**, a **review finding** (a spec, quality or
whole-task review, or what the Manchester pilot showed), or a **plan refinement** (written into
the plan's execution notes before Task 1). The superseded sentences above are marked, not deleted.

1. **Marketplaces and directories count in the competitor pool.** User ruling, after the pilot
   found every Google and Bing top-5 result for the keyword was a marketplace or directory; only
   off-topic results are dropped. Supersedes §6.1's "marketplaces and directories excluded"
   (5666007, f810e28, 99b7d5c).
2. **One competitor query per engine.** The pool is the top 5 on Google plus the top 5 on Bing for
   the page's primary keyword, merged — one query per engine, not a set of city-query variants.
   Review finding on the converted template (17ecb3f).
3. **Real headings from saved pages (Task 7a).** Each competitor page's raw HTML is saved to
   `data/queries/cache/<slug>/<n>.html` (gitignored: third-party pages carry advertisers'
   contact details), and `query_augment.py --extract-h2` reads it, dropping H2s inside links,
   card articles, card-grid list items, nav, stray headers, footer, aside and form, stripping
   marketplace furniture headings, and reporting `h2`, `h2_all` and `blocked` (challenge pages
   are recorded, never counted); headings are never written by hand. Review finding from the
   pilot (99b7d5c, 4dcbc35, 651387d, 1c75b18).
4. **Section floor 9.** `section_target.total = max(matched + 3, 9)`, so a location page never has
   fewer than 9 body sections, including when fewer than three usable competitors exist. User
   ruling (99b7d5c).
5. **Bing is read free in the browser.** DataForSEO's Bing SERP returned results for "blue" alone
   in the pilot (logged, unusable), so the skill reads `bing.com` with `cc=GB` and never buys or
   preflights `serp_bing`; the script treats it as a free source (never budget-checked) and
   refuses `--record --source serp_bing` (exit 2). Review finding from the pilot (5666007,
   4ee6a25, 3aa5e4f); whole-branch review (c22a3e2).
6. **The connector returns no cost field.** Every paid call is logged at a conservative estimate
   and says so in the endpoint text — the pilot logged $0.20 across three calls — and
   `query_typical_call_usd` is the largest estimate (0.10). Review finding from the pilot
   (5666007).
7. **Record the cost at once; one AI engine per page.** The order is preflight → call → record →
   save → normalise, one preflight per paid call; a saved `.response.json` counts as bought, a
   refused record still saves the response, the balance is confirmed first, and one AI engine
   (ChatGPT) is asked once per page. Review finding on Task 4 (3b705b0, a25f139, cfcb1f0).
8. **Raw and normalised files.** The connector response is saved as
   `raw/<slug>/<source>.response.json` for audit, dropping third-party contact details (phone
   numbers, street addresses, emails, profile/WhatsApp URLs) and noting what was dropped in
   `_saved_note`; `tests/py/test_no_third_party_contacts.py` fails on any that reach a committed
   raw file. The script reads only the normalised `raw/<slug>/<source>.json`. Plan refinement
   (15b0b40); whole-branch review (c22a3e2).
9. **Two budgets.** `query_budget_usd` caps one page's paid calls per UTC day and
   `query_total_budget_usd` (1.00) caps all spend, alongside `query_typical_call_usd`, all in
   `data/settings.json`. Plan refinement (15b0b40, cc2087f).
10. **Fallback files don't block a bought call.** Only a saved `.response.json` or a `<source>.json`
    with `"status": "ok"` counts as cached; a `fallback` or `NOT FETCHED` file does not, and
    `--refresh` is only for re-buying a real response. Review finding (a6594b2, 10cd568).
11. **`fact_source` form.** A fact is `data/<file>.json#key` or `bank:<id>` (resolved to that
    `data/faq.json` row's source), never a bare path; a non-bank candidate citing a bare path is
    ignored. Review finding on Task 3 (aa10f1e).
12. **Buyer wording wins; near-duplicates collapse; a per-topic cap (Task 7b).** A search or AI
    question citing `bank:<id>` joins that bank row and keeps the buyer's wording; the score is 2
    per distinct non-bank source type + 1 for the bank + page-type fit; same-topic entries with
    Jaccard ≥ 0.5 and at least two shared content words collapse transitively, each group led by
    a fact-backed question (an unbacked lead never borrows a fact); and each FAQ block takes at
    most two questions per topic unless it cannot otherwise fill. Review finding from the pilot's
    first question file, plus the controller's lead ruling (20721a4, c147f69, de9243b).
13. **Effective FAQ floor 17.** The block minimums (5 + 5 + 7) exceed the stated 15, so the script
    fills every block minimum and a page carries 17–20 questions; the gate still checks 15–20 in
    total and each block's range, and a run short of the block minimums stops (exit 5). Plan
    refinement (15b0b40, e868c35).
14. **Exit codes 0–6.** 0 ok; 1 internal error; 2 usage (bad slug, route, `--today` or `--cost`,
    or `--record` refused); 3 cached and 4 budget (preflight only; 4 also for unreadable settings
    or spend log); 5 short (build); 6 bad input (a malformed raw file, or unreadable saved HTML for
    `--extract-h2`). Review findings (f949cfa, 4502bfe, 3e19e5b, e868c35, 3aa5e4f).
15. **The gate waits for the rebuild; three-block rules on location pages only.** A question file
    is gated only once its page is built and listed in `data/facts/rebuilt.json` under the bare
    slug (the route's last segment; the nested `uk-locations/<slug>` key is accepted too), and the
    gate counts not-built and awaiting-rebuild files; the three-block count and ranges apply to
    location pages only, answers end at their own `<details>`, and an extra section's recorded
    heading must be an H2 inside `<main>`. Review findings (7cf6010, b4cc33f, 14f237d, 51b7302).
16. **Frame order and frame ids.** The frame runs hero, counter, trust strip, table of contents,
    key takeaways, review top, FAQ top, then body; review middle, FAQ middle, body; newsletter,
    body; review bottom, FAQ bottom, enquiry form. A body section is a `<section
    data-section-label>` in `<main>` with an H2 that is not `#top`, `#key-takeaways` or
    `#newsletter` and holds no frame part. Review findings (0c96a23, 0051497, caa5166, 17ecb3f,
    51b7302).
17. **The law row is `LEGAL_CLAIM_PLACEHOLDER`.** §7 said "Staffies are not banned"; the template
    names the Dangerous Dogs Act and microchipping as topics but makes every statute line
    `LEGAL_CLAIM_PLACEHOLDER` (`CLAUDE.md` rule 9, `rules/copy.md`). The breed guide asserts it
    via the gov.uk row, so Known Issue 46 stays open for a user ruling. Review finding (6f1b36f,
    c73f540).
18. **§4 example additions.** The schema adds a required top-level `route`; competitors may carry
    `blocked` and take `h2_raw` from the saved page's `h2_all` (the raw `competitors.json` record
    carries `h2`, `h2_all`, `blocked`); `section_target` gains `floor`; each `extra_sections` item
    has `topic`, `uncovered`, `question_ids` and `heading`; each question gains `topic` and
    `block`, `covered_by.where` is `faq` or `heading`, and thread evidence is
    `thread:<permalink>`, not `thread:r/.../id`. Review finding (f949cfa, 99b7d5c, c72033b).
19. **Project 5 prerequisite and checklist.** Known Issue 39: `facts_preserved_check`,
    `link_parity_check`, `verbatim_set_check` and `pageboard.own_live_key` must resolve nested
    `uk-locations/<slug>` routes before any city page enters `data/facts/rebuilt.json`. Known
    Issue 40 lists the builder quality items deferred to project 5. User ruling deferring them
    (870799a, c73f540).
20. **No recorded fixtures.** The recorded DataForSEO fixtures under `tests/py/fixtures/queries/`
    (§2, §11) were not created: the tests build inline synthetic data under `tmp_path`, and make
    no live calls. Whole-branch review (c22a3e2).
21. **A usable competitor page.** A page is usable when it has at least 3 cleaned H2s and is not
    blocked (`MIN_USABLE_H2` in `scripts/query_augment.py`); only usable pages set the number or
    count as an outlier's comparison, and every page is still recorded. Whole-branch review
    (c22a3e2).
