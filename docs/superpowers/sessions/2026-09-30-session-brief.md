# Session Brief — 2026-09-30

> **Status:** READY. The interview is complete.
> **Last updated:** 2026-09-30 (pre-filled from disk)

## Q&A Log (Verbatim)
_(The user's exact answer to each question is appended here as the interview proceeds. Entries marked "from disk" were read from the repo, not asked, and are pending the user's confirmation.)_

**Q1 — Outcome (from disk):** The London city page `/uk-locations/blue-staffy-puppies-london/` is built from its own outline and passes every gate. Claude verifies it; then the user approves or fails it. (Definition of done: `bsuk-project5-board-decisions`, answer board 2026-09-26/27.)

**Q2 — Traffic reality (from disk):**
- Search Console and Bing data are NOT FETCHED: the GSC property is unverified because the domain expired, and there are no exports on disk (`data/page-map.json` `baseline_gsc`).
- London today is a stub: 4 words, an empty H1, noindex. The scaffold uses the placeholder kit.

**Q3 — Worst performer (from disk):** London itself. It is the first of 28 city pages, and all 28 are stubs or migrated WordPress bodies (gap matrix 2026-09-25).

**Q5 — Constraints (from disk, rulings on record):** see the CONSTRAINT lines below.

**Q6 — Specific target (from disk):** `/uk-locations/blue-staffy-puppies-london/`, slug `blue-staffy-puppies-london`, kind `location`, hub `/uk-locations/`.

**Q7 — Done looks like (from disk):** research → research board (STOP 1) → outline (STOP 2, approved separately) → page board (STOP 3) → build → all gates (render, Lighthouse, SEO) → Claude verifies → the user approves or fails the page.

**Q10 — Framework (from disk):** decided at the research board (STOP 1). The user picks the angles, strategy and frameworks there, and not before (`research-board-before-outline`).

**Q11 — AIO/GEO approach (from disk):** decided at the research board (STOP 1), with the LLM-intel file `docs/research/llm-intel/blue-staffy-puppies-london-2026-09-25.json` as input.

**Q12 — Visual plan (from disk):** decided on the page board (STOP 3). Every H2/H3 and the hero get an image (rule 17), taken first from the page's own images, then the site's served images, then `Assets/Images/`. The London component kit is the menu.

- **CONSTRAINT:** Never push; commit after every task. Every commit trailer is `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Never merge into `foundation` until the user says so.
- **CONSTRAINT:** No component is chosen and no page board is built before the outline is approved separately (STOP 2, `outline-approved-before-page-board`).
- **CONSTRAINT:** Headers are buyer questions in FAQ style, each answered first by a conversational paragraph. No FAQ-block question repeats a header.
- **CONSTRAINT:** 2,000–3,000 words when the competitor median is NOT FETCHED.
- **CONSTRAINT:** The parents are Maggie (dam) and Jones (sire), with the site's existing parent images. Prices, deposit, delivery, guarantee and age all come from data. The deposit is never called plainly "refundable".
- **CONSTRAINT:** Health: name the tests (L-2-HGA, HC-HSF4, eye and elbow screening) and never state a result. No DNA certificates are held (Lisa, 2026-09-29).
- **CONSTRAINT:** Nothing about the licence goes on the site.
- **CONSTRAINT:** Type fits every tier: no big or chunky headings, and no tall sections or paragraphs (user, 2026-09-28).
- **CONSTRAINT:** Write from the outline only, never from a sibling (rule 8, rule 17). Include six external links on six domains from four source types.

**Q8 — Reader profile:** asked with examples (the 300-mile distance, paying the deposit before seeing the puppy, doubts about delivery, price against London sellers). The user answered: "having to pay the deposit before seeing the puppy, this one". The user also said "the board looks fine", and the pre-filled answers were accepted.

- **CONSTRAINT:** The deposit-first fear is the London buyer's main worry and main reason to leave. The page must answer it head-on: the deposit books the viewing and reserves the puppy, a video call is offered before the deposit, the deposit is up to 70% refundable if a visitor fails to show up, and it comes off the price. All of this comes from the rulings on record and data.

**Q9 — Benchmark:** "no, we use the competitors research data to build the page, until we published the sites, i can see it myself then we determine"

**Q14 — Urgency:** "no dateline, once we ggo thhrough all the steps, and gates/stop, we use impecable latrr to refine, polish each page"

**Task 4 (paid calls):** user chose SERP + volumes + backlinks, 2026-09-30 (chat). That approves three DataForSEO calls for London, about $0.15–0.30 in total: the Google SERP with People Also Ask, one batched keyword search-volume call (UK, English), and a backlinks summary for the top-5 competitor domains. Caps unchanged: $0.50 per page per day, $1.00 total.

## Decisions Log
- Framework, angles and strategy: to be picked by the user at STOP 1.
- There is no deadline. Every step, gate and stop is done in full, then an impeccable refinement pass polishes each page (Q14).
- No benchmark page: the London page is built from the competitor research data. The user judges it once the site is published (Q9).
- The primary reader fear to resolve is paying the deposit before seeing the puppy (user, Q8).
- The London component kit (15 picks, confirmed 2026-09-29) is the menu; the outline decides the sections.

## Open Flags
- **Research on hand:** a gap matrix exists (2026-09-23 and 2026-09-25), and so does the LLM-intel file for London (2026-09-25). `data/queries/` has no London query file, so competitor research and fan-out (page-run rows 4–7) are still to run.
- **Board:** London has no approved page board. That is expected; it comes at STOP 3.
- **Audit:** London has not been through `@bsuk-content-audit-agent`. It is a stub with 4 words, so an audit adds little; the research board covers the intent and gaps.
- **Hub:** `/uk-locations/` is built. Known Issue 86: the UK hub's body does not link the indexable city pages.
- **Deposit refund clause (Ruling 2 of the London plan):** the user's condition is "if you change your mind up to 1 day before collection or delivery" (deposit-wording batch Q3 (b), 2026-09-27), which supersedes this brief's "if a visitor fails to show up". It lives on the unmerged `deposit-wording` branch; `data/settings.json` has no refund-wording key. London prints `depositLine` with no refund wording until that branch is merged (the user's call).
  - **Superseded 2026-09-30 (user, in chat):** "ignore that or just write when build the page, go to the next task". The `deposit-wording` branch is no longer awaited. At the build (Task 23 onward), the refund clause — the deposit is up to 70% refundable if you change your mind up to 1 day before collection or delivery — is added as a data key in `data/settings.json` and the London page reads it from there, never typed. The STOP 1 answer to q07 ((a), wait for the push) is replaced by this ruling. The outline carries the clause in the deposit section.
  - **Landed 2026-09-30 (Task 21 review):** the clause is now `data/settings.json` `deposit_refund_clause` (with `deposit_refund_clause_source`); the London board's rows 8 and 14 point at that key. The approved research board's S2 trade-off ("its lead answer waits on the refund wording … can say what the deposit does" but not when the money comes back) is superseded by this key; the research-board record is left as approved, not edited.
- **Served alt with an unproven result (Task 21 review, 2026-09-30):** `/images/breeder-sitting-blue-staffy-puppy-home.webp` is served on `/blue-staffy-uk-breeders/` with the alt "… Responsible breeders of blue Staffies L-2-HGA clear." That states a DNA result no file backs (working rule 9; plan Ruling 4; evidence ledger `parents-dna-clear` NOT FETCHED — none held). The London board drops the clause in `verbatim.changed`; the breeders page still serves the alt, and correcting it there is a separate decision for the user.
- **FAQ total 21 against the 15–20 cap (Task 27, 2026-10-03):** the approved board carries 21 FAQ questions (top 6, middle 7, bottom 8, since the breeder's q04 of 2026-10-02 added "How Rare Are Blue Staffies?"), and the London page renders all 21. `scripts/query_coverage_check.py` caps a location page at `FAQ_TOTAL_MAX` 20 (plan Ruling 9), so once London is in `data/facts/rebuilt.json` (Task 28) `check:queries` reports `FAQ total: 21, want 15–20` and nothing else. One narrow question for the user: drop one of the two promoted top-block questions ("Where Can I Find Blue Staffy Breeders in the UK?" is the weaker), or allow 21 on this page. Not widened, not dropped: the page follows the approved board until the user answers.

---
<!-- The synthesized fields below are filled in at finalization, from the Q&A Log above. -->
- **External link live checks (Task 19, 2026-09-30):** `curl -sIL` to all six external hosts returned `000`: the session egress proxy refuses CONNECT with 403 (policy). Each is recorded `NOT FETCHED — egress proxy CONNECT 403` in `docs/research/london-page-run/links-plan.md`, with a Firecrawl `maxAge: 0` scrape returning 200 recorded beside it as a second source. This departs from the plan's "keep only 200s" (Task 19 Step 2). Re-run the curl checks from an unrestricted network before launch (project 6).

## Business Focus
Build London, the first of the 28 city pages, from real competitor research, and approve it stop by stop. The page has to win over a London buyer who fears paying a deposit before seeing the puppy. It must do that with facts that are true and read from data.

## SESSION CONTEXT
- **Page type:** location (city)
- **Target keyword:** blue staffy puppies london. The research board confirms the primary keyword and its distribution.
- **Framework:** picked at STOP 1 (research board).
- **Framework reason:** recorded at STOP 1.
- **AIO / GEO approach:** picked at STOP 1.
- **AIO notes:** `docs/research/llm-intel/blue-staffy-puppies-london-2026-09-25.json` is the one-engine input; its `bsuk_cited` is reported on the research board.
- **Component style:** city kit (15 components confirmed 2026-09-29). The outline decides the sections, and the page board maps each section to a component.
- **Visual plan:** picked on the page board (STOP 3). Every H2/H3 and the hero get an image (rule 17).
- **Audit status:** not run. The page is a 4-word stub; the research board covers intent and gaps.
- **LLM visibility:** see the llm-intel file above (reported at STOP 1).
- **Structure.json entry:** location cluster under `/uk-locations/`.
- **Hub page:** `/uk-locations/` (built; Known Issue 86: its body does not link the city pages).
- **Internal links needed:** chosen on the page board (rule 12: every link is on the board).

## Today's Target
- **Page:** `/uk-locations/blue-staffy-puppies-london/`
- **Goal:** the full page run (research → STOP 1 → STOP 2 → STOP 3 → build → gates), then Claude verifies and the user approves.
- **Reader:** a London buyer. Their main fear, and main reason to leave, is paying the deposit before seeing the puppy.
- **Benchmark:** none. The page is built from the competitor research data.

## Constraints
See every CONSTRAINT line in the Q&A Log above.

## Repeat / Avoid
- **Repeat:** subagent build, then spec review, then quality review. Every page change is proven by a check that fails first.
- **Avoid:**
  - choosing components before the outline is approved;
  - stating health results;
  - calling the deposit plainly "refundable".

## Urgency
No deadline. Every step, gate and stop comes first, then an impeccable refinement pass.

## Recommended Next Steps
- **Page-run row 1:** the `superpowers:writing-plans` skill writes London's page plan, then the `bsuk-location-page-builder` skill loads. Then run `python3 scripts/page_run_record.py blue-staffy-puppies-london session-open --builder bsuk-location-page-builder`.
- **Rows 2–7:** intake, URL decision, research inventory, competitor research and query fan-out (`bsuk-query-augmentation`), keyword deliverables and entities.
- **Row 8:** the research board, which is STOP 1. The user picks the angles, strategy, frameworks and keywords.

## What's Next

_Filled by session-closer, 2026-10-06. London closed: approved, indexable, gate PASS at 88a80f39; `london-components` fast-forwarded into `foundation` (local only, no push until project 6)._

1. **The next project 5 city page.** Walk `docs/reference/page-run.md` from row 1. Row 1 now reads `docs/reference/lessons.md` first. Before its research board, run Known Issue 99: tune the location word-count ceilings in `data/quality/evidence-budgets.json` against London's real counts. Also run the duplicate-content gate straight after the first build (lessons, entry 18), not first at the close.
2. **Known Issue 101:** port the scroll-spy fix (`src/lib/scrollSpy.ts`, 9010e4f4) to `src/components/kit/PageDial.astro` on the twelve pre-project-5 pages, with its test.
3. **Lessons marked "not gated"** (`docs/reference/lessons.md`): turn the cheapest into tests. Candidates: text inside generated images read as copy before the board (entry 7); alts checked against their image at the Asset Gate (entry 8); a fact-correction sweep (entry 19).

## Unfinished
- Known Issue 100: puppy-card photos on London. Deferred by the breeder to the post-launch refinement (project 6).
- The certificates sentence is on 11 pages. The certificates themselves (lab, grades) are not in the repo, so no page may state a result until they are supplied.
- The Glasgow migrated page still carries a coordinate map (Known Issue 55). The breeder said to leave it for its rebuild.
- `GEMINI_API_KEY` is still in `.env`. The breeder deletes it when image work is done.

## Discovered This Session
- `scripts/pipeline_status.py` misread rows 13 and 16–21 (scorecards named by route, the `verification_before_completion` key, hard-coded rows). Fixed with tests; a gate run stays current across docs-only commits.
- `test:render:city` flakes had three causes: an animation mid-measure, scroll timing, and a real scroll-spy defect. All are fixed; the stress run was 500/0.
- "Sharine Amelia" (the old owner name) shipped on the UK hub until 2026-10-04. `check:retired` now gates it site-wide (Known Issue 12, reopened and closed).
- Breeder facts confirmed 2026-10-04/05: KC registration application form; vet-signed health card, first vaccinations, microchip, worming and flea treatment; home-raised; support after collection; certificates on request; puppy personality lines in `data/puppies.json`.
- Mods: the route map has a live card and real per-row proof; the gauges band has a work clock under the prompt.
