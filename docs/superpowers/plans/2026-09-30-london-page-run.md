# London Page Run Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Walk `/uk-locations/blue-staffy-puppies-london/` (slug `blue-staffy-puppies-london`) through page-run rows 1–21 so the London scaffold becomes a real city page. It is written from its own approved outline, passes every gate twice, and waits for the user to approve or fail it.

**Architecture:** One page, one run, top to bottom, in `docs/reference/page-run.md` order. The research (rows 4–7) writes to disk under `data/queries/` and `docs/research/`. Four hard stops follow, each a controller task that publishes an Artifact, posts one answer-board batch named for the slug, waits for the user's Send and records the approval from the saved answers file:
- the research board (STOP 1);
- the outline (STOP 2);
- the page board (STOP 3);
- the Asset Gate (STOP 4).

The existing scaffold (`src/pages/uk-locations/blue-staffy-puppies-london.astro`, on `CityShell`) is rewritten from the approved board. The 15 London kit components are the menu, and the approved outline decides which ones are used. The page stays `noindex, follow` until the user approves the finished page.

**Tech Stack:**
- Astro 4 pages on `CityShell`, and the `src/components/kit/City*.astro` kit.
- Python 3 gate scripts under `scripts/` and pytest under `tests/py/`.
- Playwright render harness under `tests/render/`.
- The DataForSEO MCP (paid, behind `scripts/query_augment.py`'s spend guard) and the Firecrawl MCP (paid in credits, last resort).
- The Playwright MCP (free browser reads).
- The claude.ai Artifact, ArtifactData and ArtifactComments tools, for the boards and the answer board.

---

## How this plan is executed

- **Subagent-driven.** Use Opus implementers, one fresh subagent per task. After each task, run a spec-compliance review, then a code-quality review (`superpowers:subagent-driven-development`). A reviewer's finding is fixed and re-reviewed before the next task starts.
- **Controller-only tasks.** These are marked **CONTROLLER**. The implementer never runs them:
  - every STOP task;
  - every paid-call approval;
  - every ArtifactComments watch;
  - every ArtifactData read or write on the answer board or a page board;
  - every Artifact publish;
  - every Skill invocation that a stop depends on.

  Only a main-loop session can hold an answer-board watch.
- **Commits.** Commit after every task on branch `london-components`, in worktree `/Users/apple/Downloads/BSUK/BSUK-london`. Never push. Never merge into `foundation` without the user's word. Every commit message ends with:

  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```
- **Never use `git stash`**, and never start background jobs. Other agents may be committing in the same worktree, so stage by explicit path. Never use `git add -A` or `git add .`.
- **Confidence gate (working rule 7).** When a task falls below 97% confidence, do not dead-stop:
  1. write the finished part to disk;
  2. append the open question to `docs/superpowers/sessions/2026-09-30-session-brief.md` under `## Open Flags`;
  3. the controller asks the user exactly one narrow question;
  4. keep building whatever is not blocked.
- **A gate's output is a hypothesis** (`rules/gates.md` `verify-the-gate-first`). Before editing anything in response to a FAIL, confirm the defect on the built page. Before believing a PASS, read the gate's examined count.
- **Invoking a skill.** A skill named `plugin:name` is invoked with the Skill tool by exactly that name. If a BSUK skill is missing from this session's Skill listing because it was ported into this worktree after the session started (`bsuk-visual-intelligence`, `bsuk-reddit-threads`), read and follow `.claude/skills/<name>/SKILL.md` instead, and say so in the task report.
- **Dates.** Every command that names a date sets it first with `D=$(date +%F)`. Batch ids, answers files and dated research files use that value.

## Rulings that bind every task (from the session brief and memory)

1. **The primary reader fear** is paying the deposit before seeing the puppy (the brief, Q8). The page answers it head-on:
   - the deposit books the viewing and reserves the puppy;
   - a live video call with the puppy and its mother is offered on request before any deposit (Lisa, answer board q03, 2026-09-29);
   - the deposit is paid by bank transfer (q04);
   - the deposit comes off the price (`src/lib/cityKit.ts` `depositLine`).
2. **The refund clause is not in the data yet.**
   - The deposit is never called plainly "refundable".
   - The 70% condition the user picked is "if you change your mind up to 1 day before collection or delivery" (deposit-wording batch, Q3 (b), 2026-09-27). It supersedes the brief's "if a visitor fails to show up".
   - That wording lives on the unmerged `deposit-wording` branch. `data/settings.json` has no refund-wording key, and `cityKit.ts` deliberately prints no refund clause.
   - So the page prints `depositLine` (no refund wording) until that branch lands. Task 3 logs the flag.
3. **Parents: Maggie (dam) and Jones (sire)**, with the site's existing parent images.
4. **Health.** Name the tests (L-2-HGA, HC-HSF4, eye screening, elbow screening) and never state a result. "Clear", "certified" and "will not be affected" never appear (Lisa q01, 2026-09-29; Known Issue 98). `/blue-staffy-health-uk/` is the internal source for health claims.
5. **Nothing about a licence** goes on the page: no number, no council, no claim, and no licensing link (user, 2026-09-27).
6. **Facts come from data only, via `src/lib/cityKit.ts` and the data files.** This covers prices, deposit, delivery band, town, guarantee (`guaranteeRow()`, which reads `data/settings.json` `guarantee_days` 730 and `guarantee_label`) and the puppies' age ("10 weeks old", no date of birth). The CLAUDE.md line "`guarantee_days: null`" is stale: settings now carries the breeder's two-year answer (q07, 2026-09-29). Never type a price or a figure.
7. **Every H2 and H3 is a buyer question in FAQ style**, answered first by a conversational opening paragraph. No FAQ-block question repeats a header.
8. **Words: 2,000–3,000** when the competitor median is `NOT FETCHED`.
9. **FAQ:** three blocks, top 5–7, middle 5–7 and bottom 7–10, for 15–20 H3s in total. Every pick comes from `data/queries/blue-staffy-puppies-london.json`.
10. **Type fits every tier:** no big or chunky headings, and no tall sections or paragraphs.
11. **Write from the outline only**, never from a sibling (rules 8 and 17). Carry six external links on six domains from four source types.

## Stops (controller-owned, hard)

| Stop | Page-run row | Task | Batch id | Recorded by |
|---|---|---|---|---|
| STOP 1: research board | 8 | Task 17 | `${D}-research-board-blue-staffy-puppies-london` | `python3 scripts/research_board.py blue-staffy-puppies-london --approve --answers <file>` |
| STOP 2: outline (section matrix) | 9 | Task 20 | `${D}-outline-blue-staffy-puppies-london` | `python3 scripts/outline_matrix.py blue-staffy-puppies-london --approve --answers <file>` |
| STOP 3: page board | 10 | Task 23 | `${D}-page-board-blue-staffy-puppies-london` | the board's db, then `python3 scripts/board_approve.py blue-staffy-puppies-london` |
| STOP 4: Asset Gate | 11 | Task 25 | `${D}-asset-gate-blue-staffy-puppies-london` | the board's db (second pass), then `python3 scripts/board_approve.py blue-staffy-puppies-london` |

At every stop, the task:
1. publishes the Artifact;
2. posts the batch;
3. says in chat only "N new questions on the board: https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf";
4. then **ends the turn and waits**.

Nothing after a stop starts until its approval is recorded and committed. The two Harden passes (Tasks 30–31) pause only for a PREVIEW, never as a fifth stop. The final approve-or-fail (Task 37) is one either/or pick in chat, which is allowed.

## Paid fetches: spend guard and estimates

Guard state read on 2026-09-30 with `python3 scripts/query_augment.py --budget serp_google`:
- total counted $0.30215 of the $1.00 cap;
- typical call $0.01;
- page cap $0.50 per slug per day;
- the spend log holds 41 entries.

| Call | Source | Guard | Estimate | Time |
|---|---|---|---|---|
| Google SERP + PAA (depth 10, PAA click depth 1) for "blue staffy puppies london" | DataForSEO `serp_organic_live_advanced` | `--preflight … --source serp_google`, then `--record` | $0.01 (the guard's typical call; earlier runs logged $0.05 as a conservative estimate, so allow up to $0.05) | ~1 min |
| ChatGPT answer for London | DataForSEO `ai_optimization_chat_gpt_scraper` | already bought 2026-09-25 (spend log entry, `data/queries/raw/blue-staffy-puppies-london/ai_engines.response.json`); preflight must exit 3 | $0.00 | 0 |
| Bing top 10 | free, Playwright MCP | none needed | $0.00 | ~5 min |
| Competitor pages (up to 10) | `curl` first (free), then a Playwright capture (free) | Firecrawl scrape last, 1 credit per page | 0 credits expected; worst case ~10 Firecrawl credits | ~15 min |
| People Also Ask fallback | `bsuk-paa-agent` (Playwright, free), then Firecrawl search | Firecrawl search ~2 credits per call | 0 expected (PAA comes with the paid SERP) | ~10 min |
| Keyword volumes | none | the guard has no keyword-volume source (`PAID_SOURCES = ("serp_google", "ai_engines")`) | not bought: written `NOT FETCHED — <barrier>` | 0 |
| Authority and referring domains | none | the guard has no backlinks source | not bought: written `NOT FETCHED — <barrier>` | 0 |

**Worst case for the whole run:** $0.05 in DataForSEO and about 12 Firecrawl credits. The page cap leaves $0.45 of headroom.

**Rough total time:**
- research, rows 2–8: 3–4 agent-hours;
- outline, row 9: about 1 hour;
- board and images, rows 10–11: 2–3 hours;
- build, row 12: 3–4 hours;
- Harden and gates, rows 13–21: 3–4 hours.

The user's waits at the four stops come on top of these figures.

## What London cannot do yet (each is a `NOT FETCHED — <barrier>` or an Open Flag, never a guess)

1. **Keyword volumes** (research board section 13). The spend guard in `scripts/query_augment.py` accepts only `serp_google` and `ai_engines`, and the skill forbids working around it. The barrier line is: `NOT FETCHED — scripts/query_augment.py's spend guard has no keyword-volume source (PAID_SOURCES is serp_google, ai_engines), so no call was made`.
2. **Authority and referring domains** (section 18). The same barrier applies, for backlinks.
3. **Generated images** (source `generate`). `GEMINI_API_KEY` is absent from `.env`. Every image slot is filled from the page's own images, the site's served images, the breeder's folder `/Users/apple/Downloads/BSUK/bluestaffyuk-cms/Assets/Images`, or an `infographic` slot. No slot is `generate` while the key is missing.
4. **The deposit's 70% refund condition** (Ruling 2). The data key does not exist until the `deposit-wording` branch merges. That merge needs the user. Until then the page prints no refund wording.
5. **Search Console and Bing baselines.** These are `NOT FETCHED — GSC property unverified (domain expired); no exports on disk` (from `page_intake.py`).
6. **LLM mentions.** `NOT FETCHED` until BSUK's domain is live (project 6).
7. **Deploy-side checks.** The live 200, IndexNow, and `perf_audit.py --live` or `--psi` wait for project 6. `--live` refuses on the `SITE_URL` placeholder.
8. **A `local` external link.** The builder skill asks for the city's own council licensing page. London has 33 borough councils plus the City of London, and the licence ruling keeps licensing off the page. The page therefore meets four source types without a `local` row. The research board carries this as a question (Task 17, q06).

## File map

**Created**
- `data/page-runs/blue-staffy-puppies-london.json`: the run record (session open, Harden passes, verification).
- `data/facts/blue-staffy-puppies-london.json`: the facts extracted from the migrated 4-word body.
- `data/queries/raw/blue-staffy-puppies-london/serp_google.response.json`, `serp_google.json`, `serp_bing.json`, `competitors.json` and `threads.json`: the row 5 inputs.
- `data/queries/cache/blue-staffy-puppies-london/<n>.html`: the saved competitor pages. This folder is git-ignored and is the evidence the research board cites.
- `data/queries/blue-staffy-puppies-london.json`: the question file.
- `docs/research/london-page-run/`, which holds:
  - `inventory.md`: the row 4 inventory;
  - `keyword-variants.json`;
  - `keyword-universe.json`;
  - `entities.md`;
  - `serp-findings.md`: the `bsuk-framework-agent` read of each saved page;
  - `angles.md`;
  - `strategies.md`;
  - `frameworks.md`;
  - `links-plan.md`.
- `docs/research/llm-intel/blue-staffy-puppies-london-${D}.json`: refreshed from the saved response, with no new call.
- `data/research-boards/blue-staffy-puppies-london.json`, plus `docs/artifacts/research/blue-staffy-puppies-london.html` and `.md`.
- `data/outlines/blue-staffy-puppies-london.json`, plus `docs/artifacts/outlines/blue-staffy-puppies-london.html` and `.md`.
- `data/boards/blue-staffy-puppies-london.json`, plus `docs/artifacts/boards/blue-staffy-puppies-london.html`.
- `docs/reference/answer-board/batches/${D}-{research-board,outline,page-board,asset-gate}-blue-staffy-puppies-london.md` and `.json`.
- `docs/reference/answer-board/answers/<batchId>-<date>.json` and `.md`, one pair per stop.
- `tests/py/test_london_page.py`: the rebuilt page's own invariants.
- `docs/superpowers/sessions/${D}-visual-intel-blue-staffy-puppies-london.md`: the row 16 report.
- `data/quality/scorecards/blue-staffy-puppies-london-${D}.json`: written by the render run.

**Modified**
- `src/pages/uk-locations/blue-staffy-puppies-london.astro`: the scaffold becomes the page.
- `tests/py/test_city_scaffold.py`: London stops being a scaffold.
- `data/facts/rebuilt.json`: adds `blue-staffy-puppies-london`.
- `tests/render/targets.json`: adds `{"slug": "uk-locations/blue-staffy-puppies-london", "page_type": "location", "corpus": true}`.
- `data/bsuk-ontology.json`: only for a new entity, which is `PROPOSED` with its source.
- `docs/reference/external-link-library.md`: only if Protocol A adds a row, dated and typed.
- `docs/superpowers/sessions/2026-09-30-session-brief.md` (`## Open Flags`, `## What's Next`).
- `docs/reference/session-log.md` (Known Issues), at the close.

**Never hand-edited:** `data/locations.json`, `data/page-map.json`, `public/_redirects`, `public/images/**` (except through `scripts/ingest_image.py`), and `data/queries/spend.json` or `dashboard.json`.

---

## Phase A: Session open (row 1)

### Task 1: Load the builder skill and record the session open

**Files:**
- Create: `data/page-runs/blue-staffy-puppies-london.json`
- Test: `python3 scripts/page_run_record.py blue-staffy-puppies-london --check`

- [ ] **Step 1 (CONTROLLER): Arm the answer-board watch**

  Run ArtifactComments `watch` on `https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf`. Then run a bare ArtifactComments `watch` and confirm that the board's row says auto-replies are armed. If it does not, ask the user to paste the board link in chat and watch again.

- [ ] **Step 2: Invoke the builder skill**

  Invoke the Skill tool with `bsuk-location-page-builder`. `grill-me` ran on 2026-09-30 (commit 1373d0c, the session brief). `superpowers:writing-plans` is this plan.

- [ ] **Step 3: Record the session open**

  Run:

  ```bash
  python3 scripts/page_run_record.py blue-staffy-puppies-london session-open --builder bsuk-location-page-builder
  ```

  Expected: exit 0, and `data/page-runs/blue-staffy-puppies-london.json` exists with a `session_open` key listing `grill-me`, `superpowers:writing-plans` and `bsuk-location-page-builder`, in that order.

- [ ] **Step 4: Check the record**

  Run:

  ```bash
  python3 scripts/page_run_record.py blue-staffy-puppies-london --check
  ```

  Expected: exit 1. The problems listed are the missing `impeccable`, `frontend_design` and `verification_before_completion` keys, and **not** `session_open`. If `session_open` is listed, stop and report.

- [ ] **Step 5: Commit**

  ```bash
  git add data/page-runs/blue-staffy-puppies-london.json
  git commit -m "chore(london): page-run session open recorded (row 1)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

## Phase B: Intake, URL and inventory (rows 2–4)

### Task 2: Intake, URL decision and facts extract

**Files:**
- Create: `docs/research/london-page-run/intake.txt`, `data/facts/blue-staffy-puppies-london.json`
- Test: `npm run -s check:redirects`

- [ ] **Step 1: Save the intake (row 2)**

  Run:

  ```bash
  mkdir -p docs/research/london-page-run
  python3 scripts/page_intake.py blue-staffy-puppies-london | tee docs/research/london-page-run/intake.txt
  ```

  Expected lines:
  - `Mode stub`
  - `Robots noindex, follow`
  - `H1 (migrated row) EMPTY`
  - `Question file none`
  - `LLM intel docs/research/llm-intel/blue-staffy-puppies-london-2026-09-25.json (ok)`
  - `Board none`

- [ ] **Step 2: Confirm the URL decision (row 3)**

  Run:

  ```bash
  grep -n "blue-staffy-puppies-london" docs/research/2026-09-26-url-family-decision.md
  npm run -s check:redirects
  ```

  Expected:
  - The row reads "keep the slug; rebuild the stub".
  - `check:redirects` exits 0.
  - `data/redirects.json` gets no row: the slug does not move.

- [ ] **Step 3: Extract the facts before the rewrite**

  Run:

  ```bash
  python3 scripts/facts_preserved_check.py --extract blue-staffy-puppies-london
  ```

  The extract reads only `article.prose-migrated`, whose body is "Blue Staffy Puppies London". Expected output: `extracted facts for blue-staffy-puppies-london: 0 prices, 0 names, 0 tests, 0 creds, 0 images, 0 embeds`.

  If any count is non-zero, the extract read placeholder copy. That is a harness defect. Do not commit the file. Report it to the controller, who logs it under Open Flags.

- [ ] **Step 4: Confirm that no verbatim set applies**

  Rule 15 does not apply: the page is a stub, Known Issue 79. Run:

  ```bash
  python3 -c "import json;print('blue-staffy-puppies-london' in json.load(open('data/verbatim/applies.json'))['slugs'])"
  ```

  Expected: `False`. Do not run `verbatim_set_check.py --extract`.

- [ ] **Step 5: Commit**

  ```bash
  git add docs/research/london-page-run/intake.txt data/facts/blue-staffy-puppies-london.json
  git commit -m "chore(london): intake, URL kept, migrated facts extracted (rows 2-3)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 3: Research inventory before any fetch (row 4)

**Files:**
- Create: `docs/research/london-page-run/inventory.md`
- Modify: `docs/superpowers/sessions/2026-09-30-session-brief.md` (`## Open Flags`)
- Test: `npm run -s check:barriers`

- [ ] **Step 1: Run the preflights that decide what is banked**

  Run:

  ```bash
  python3 scripts/query_augment.py --preflight blue-staffy-puppies-london --source ai_engines; echo "exit $?"
  python3 scripts/query_augment.py --preflight blue-staffy-puppies-london --source serp_google; echo "exit $?"
  ```

  Expected: `ai_engines` exits 3 (bought 2026-09-25), and `serp_google` exits 0 (not bought). If `serp_google` exits 4, stop: the budget is exceeded, and the guard's stderr line goes to the controller.

- [ ] **Step 2: Write the inventory**

  Write `docs/research/london-page-run/inventory.md` with this exact content, adjusting only the exit codes you saw:

  ```markdown
  # London research inventory (page-run row 4)

  | Item | On disk | Status | What fetches it if missing |
  |---|---|---|---|
  | ChatGPT answer (1 engine) | data/queries/raw/blue-staffy-puppies-london/ai_engines.response.json | banked 2026-09-25; preflight exit 3 | — |
  | LLM-intel file | docs/research/llm-intel/blue-staffy-puppies-london-2026-09-25.json | banked; page_source provisional (no question file then) | bsuk-llm-keyword-intel (Task 11), no new call |
  | Google SERP + PAA, "blue staffy puppies london" | none | missing; preflight exit 0 | Task 6 (paid, $0.01) |
  | Google SERP, "staffy puppies for sale london" (registry) | data/queries/raw/registry-staffy-puppies-for-sale-london/serp_google.response.json | banked 2026-09-23; a different keyword | gap scan only; never the section count |
  | Bing top 10 | none | missing | Task 7 (free, browser) |
  | Competitor pages | none under data/queries/cache/blue-staffy-puppies-london/ | missing | Task 8 (curl first) |
  | Reddit threads | none | missing | Task 9 (bsuk-reddit-threads) |
  | Competitor reports (registry) | docs/research/competitors/*.md | banked 2026-09-23/25 | bsuk-competitor-intel only for a registry competitor with no report |
  | Gap matrix / keyword gap | docs/research/gap-matrix-2026-09-25.md, keyword-gap-2026-09-25.md | banked; London 12/20 | — |
  | Cluster strategy row | docs/superpowers/sessions/2026-09-25-location-pages-strategy.md (London, line 107) | banked | — |
  | Keyword volumes | none | NOT FETCHED — scripts/query_augment.py's spend guard has no keyword-volume source (PAID_SOURCES is serp_google, ai_engines), so no call was made | a guarded source added to the spend guard |
  | Authority / referring domains | none | NOT FETCHED — scripts/query_augment.py's spend guard has no backlinks source, so no DataForSEO backlinks call was made | a guarded source added to the spend guard |
  | Search Console baseline | none | NOT FETCHED — GSC property unverified (domain expired); no exports on disk | project 6 |
  | LLM mentions | none | NOT FETCHED — llm_mentions only once BSUK's domain is live (project 6) | project 6 |
  ```

- [ ] **Step 3: Log the deposit flag**

  Append this line under `## Open Flags` in `docs/superpowers/sessions/2026-09-30-session-brief.md`:

  ```markdown
  - **Deposit refund clause (Ruling 2 of the London plan):** the user's condition is "if you change your mind up to 1 day before collection or delivery" (deposit-wording batch Q3 (b), 2026-09-27), which supersedes this brief's "if a visitor fails to show up". It lives on the unmerged `deposit-wording` branch; `data/settings.json` has no refund-wording key. London prints `depositLine` with no refund wording until that branch is merged (the user's call).
  ```

- [ ] **Step 4: Run the barrier lint**

  Run:

  ```bash
  npm run -s check:barriers
  ```

  Expected: exit 0. Every `NOT FETCHED` in the new file names a barrier of two or more words.

- [ ] **Step 5: Commit**

  ```bash
  git add docs/research/london-page-run/inventory.md docs/superpowers/sessions/2026-09-30-session-brief.md
  git commit -m "docs(london): research inventory before any fetch; deposit refund flag (row 4)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

## Phase C: Research and fan-out (rows 5–7)

### Task 4 (CONTROLLER): Approve the one paid call

**Files:** none.

- [ ] **Step 1: Read the guard**

  Run:

  ```bash
  python3 scripts/query_augment.py --budget serp_google
  ```

  Note the first line (the typical call) and the last line (the number of spend-log entries).

- [ ] **Step 2: Ask one question in chat and wait**

  Ask exactly this:

  > "Approve one paid DataForSEO Google SERP call for London ('blue staffy puppies london', UK, depth 10, People Also Ask depth 1): guard estimate $0.01, at most $0.05? If yes, reply with today's DataForSEO dashboard balance and whether you topped up since 2026-09-25."

  Then end the turn.

- [ ] **Step 3: Record the reading and relay the approval**

  On a yes with a balance B, run the reading procedure from `.claude/skills/bsuk-query-augmentation/SKILL.md` (Working rules, Money):

  ```bash
  python3 scripts/query_augment.py --reconcile --balance B --opening O --covers N
  ```

  Here O is the last `opening_balance_usd` in `data/queries/dashboard.json`, plus any top-up, and N is the entry count from Step 1. Read O back to the user. Then hand Task 5 its go-ahead.

  On a no, Task 5 writes nothing and Task 6 takes the free PAA fallback. `serp_google` is then written `NOT FETCHED — the user declined the paid Google SERP on <D>`.

- [ ] **Step 4: Commit**

  Only the controller records the dashboard file:

  ```bash
  git add data/queries/dashboard.json
  git commit -m "chore(queries): dashboard reading before London's Google SERP

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 5: Google SERP and People Also Ask (row 5, step 1; paid)

**Files:**
- Create: `data/queries/raw/blue-staffy-puppies-london/serp_google.response.json`, `data/queries/raw/blue-staffy-puppies-london/serp_google.json`
- Test: `python3 -m pytest tests/py/test_no_third_party_contacts.py -q`

- [ ] **Step 1: Preflight**

  Run:

  ```bash
  python3 scripts/query_augment.py --preflight blue-staffy-puppies-london --source serp_google
  ```

  Expected: exit 0. Any other exit means no call. Report it and stop.

- [ ] **Step 2: Make the call**

  Call the DataForSEO MCP `serp_organic_live_advanced` tool (load it with ToolSearch) with:
  - `keyword`: `blue staffy puppies london`
  - `search_engine`: `google`
  - `location_name`: `United Kingdom`
  - `language_code`: `en`
  - `depth`: 10
  - `people_also_ask_click_depth`: 1

- [ ] **Step 3: Record the cost at once, before saving anything**

  Run:

  ```bash
  python3 scripts/query_augment.py --record blue-staffy-puppies-london --source serp_google \
    --endpoint "serp_organic_live_advanced google UK en depth10 paa1 (response carries no cost; typical-call estimate)" --cost 0.01
  ```

  If the response shows a cost, record that figure instead. If `--record` exits 2, still save the response, then stop and tell the controller the cost.

- [ ] **Step 4: Save the response**

  Save the response as `data/queries/raw/blue-staffy-puppies-london/serp_google.response.json`. First remove third-party phone numbers, street addresses, emails and profile or WhatsApp URLs. Name what was dropped in `_saved_note`.

- [ ] **Step 5: Write the normalised file**

  Write `data/queries/raw/blue-staffy-puppies-london/serp_google.json` in this shape:

  ```json
  {"source": "serp_google", "status": "ok", "fetched": "<D>",
   "results": [{"google_pos": 1, "url": "<organic url 1>"}],
   "questions": [{"text": "<PAA question as shown>", "detail": "serp_google_paa", "fact_source": null},
                 {"text": "<related search as shown>", "detail": "serp_google_related", "fact_source": null}]}
  ```

  Carry the first 10 organic results. Set `fact_source` only to a data key (`data/settings.json#deposit_gbp`) or to a `bank:<id>` whose answer answers the question as asked. Otherwise leave it `null`.

  If the response holds an `ai_overview` item, also copy its text and cited domains into `docs/research/london-page-run/serp-findings.md` under `## AI Overview (from the paid SERP)`. Task 13 uses it.

- [ ] **Step 6: Run the contacts test**

  Run:

  ```bash
  python3 -m pytest tests/py/test_no_third_party_contacts.py -q
  ```

  Expected: PASS.

- [ ] **Step 7: Commit**

  ```bash
  git add data/queries/raw/blue-staffy-puppies-london/serp_google.response.json data/queries/raw/blue-staffy-puppies-london/serp_google.json data/queries/spend.json docs/research/london-page-run/serp-findings.md
  git commit -m "research(london): Google SERP + PAA for blue staffy puppies london (row 5)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 6: People Also Ask fallback (only if Task 4 was declined or Google gave a challenge page)

**Files:**
- Create: `data/queries/raw/blue-staffy-puppies-london/serp_google.json` (`"status": "fallback"`)

- [ ] **Step 1: Skip if the paid SERP is saved**

  If Task 5 saved a response, mark this task skipped in the report and go to Task 7.

- [ ] **Step 2: Read Google through the PAA agent**

  Dispatch the `bsuk-paa-agent` agent with this brief:

  > "Read Google UK for 'blue staffy puppies london' in the browser (Playwright). Record the top 10 organic URLs and every People Also Ask question as shown. If Google shows a robot check or consent wall you cannot pass by declining non-essential cookies, stop: write nothing and report NOT FETCHED."

  Save the browser artefacts only in the session scratchpad.

- [ ] **Step 3: Write the fallback file or the barrier**

  Write the normalised file with `"status": "fallback"` and `results[].google_pos`.

  On a robot check, write no file. Record `NOT FETCHED — Google returned a robot check to the Playwright browser on <D>` in `docs/research/london-page-run/serp-findings.md`.

- [ ] **Step 4: Commit**

  ```bash
  git add data/queries/raw/blue-staffy-puppies-london/serp_google.json docs/research/london-page-run/serp-findings.md
  git commit -m "research(london): PAA fallback read in the browser (row 5)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 7: Bing top 10, read free (row 5, step 1)

**Files:**
- Create: `data/queries/raw/blue-staffy-puppies-london/serp_bing.json`

- [ ] **Step 1: Read Bing**

  Open `https://www.bing.com/search?q=blue+staffy+puppies+london&cc=GB&setlang=en-GB` with the Playwright MCP. Decline non-essential cookies. Do not preflight: this is a free read.

- [ ] **Step 2: Write the normalised file**

  Write:

  ```json
  {"source": "serp_bing", "status": "ok", "fetched": "<D>",
   "note": "Read free in the browser (Playwright MCP), cc=GB, setlang=en-GB.",
   "results": [{"bing_pos": 1, "url": "<url 1>"}],
   "questions": [{"text": "<Bing related question as shown>", "detail": "serp_bing", "fact_source": null}]}
  ```

  Carry positions 1–10 exactly as shown.

  On a challenge page, write no file. Record `NOT FETCHED — Bing returned a challenge page to the Playwright browser on <D>` in `serp-findings.md`.

- [ ] **Step 3: Commit**

  ```bash
  git add data/queries/raw/blue-staffy-puppies-london/serp_bing.json
  git commit -m "research(london): Bing top 10 read free (row 5)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 8: Competitor pool: save, extract H2s, metrics (row 5, steps 2–3)

**Files:**
- Create: `data/queries/cache/blue-staffy-puppies-london/<n>.html` (git-ignored), `data/queries/raw/blue-staffy-puppies-london/competitors.json`

- [ ] **Step 1: Build the pool**

  The pool is the first five Google results merged with the first five Bing results, de-duplicated by URL. Marketplaces and directories stay in. Only off-topic results are dropped, and each drop is named in the task report.

- [ ] **Step 2: Save each page**

  Save each page `n` (1-based, in pool order) with curl first:

  ```bash
  mkdir -p data/queries/cache/blue-staffy-puppies-london
  curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" --max-time 30 "<url n>" -o data/queries/cache/blue-staffy-puppies-london/<n>.html; echo "exit $?"
  ```

  If curl fails or saves a challenge page, save a Playwright capture of the rendered HTML to the same path. Firecrawl `scrape` (rawHtml) comes last. Count its `creditsUsed` for the spend report.

- [ ] **Step 3: Extract each page's H2s**

  Run, for each `n`:

  ```bash
  python3 scripts/query_augment.py --extract-h2 data/queries/cache/blue-staffy-puppies-london/<n>.html
  ```

  Expected: exit 0 per page. Exit 6 means capture the page again.

- [ ] **Step 4: Write `competitors.json`**

  Write `data/queries/raw/blue-staffy-puppies-london/competitors.json`:

  ```json
  {"status": "ok", "fetched": "<D>",
   "pages": [{"url": "<url>", "google_pos": 1, "bing_pos": null, "h2": ["<from --extract-h2>"], "h2_all": ["<from --extract-h2>"], "blocked": false}]}
  ```

  A position is `null` when the page is not in that engine's five. A challenge page stays in the pool with `"blocked": true`. Never count or clean H2s by hand.

- [ ] **Step 5: Fill the metrics**

  Run:

  ```bash
  python3 scripts/query_augment.py --competitor-metrics blue-staffy-puppies-london
  ```

  Expected: exit 0, with `metrics` written into every page that has a matching cache file. Exit 6 means re-save that page. Never edit the record to match.

- [ ] **Step 6: Commit (the cache is git-ignored)**

  ```bash
  git add data/queries/raw/blue-staffy-puppies-london/competitors.json
  git commit -m "research(london): competitor pool saved, H2s extracted, metrics (row 5)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 9: Threads and owner language (row 5, step 4)

**Files:**
- Create: `data/queries/raw/blue-staffy-puppies-london/threads.json`
- Modify: `data/queries/thread-ledger.json`
- Test: `npm run -s check:threads`

- [ ] **Step 1: Find the threads and check each against the ledger**

  Invoke `bsuk-reddit-threads` for the slug, or read `.claude/skills/bsuk-reddit-threads/SKILL.md` if the Skill tool does not list it. The search targets London buyers and the deposit-before-viewing fear, for example "staffy puppy deposit before viewing", "blue staffy london breeder" and "deposit scam puppy uk".

  For every candidate thread URL, run this before reading it:

  ```bash
  python3 scripts/thread_ledger.py --known <url> [<url> ...]
  ```

  A line reading `reuse` means the thread was read in the last REUSE_DAYS days. Seed it from the ledger instead of opening it again:

  ```bash
  python3 scripts/thread_ledger.py --seed <url> [<url> ...]
  ```

  The seeded rows go into `threads.json` with their `seeded_from`. A line reading `fetch` means read the thread.

- [ ] **Step 2: Handle blocked sources**

  If a source blocks the fetchers (403, 429 or a bot wall), use the `research-recency` skill's fallback. What stays blocked is written `NOT FETCHED — <what was tried and what stopped it>`.

  Once `threads.json` is written, rebuild the ledger:

  ```bash
  python3 scripts/thread_ledger.py --write
  ```

- [ ] **Step 3: Keep the owner-language quotes**

  Keep up to 8 owner-language quotes, each with its thread URL, for the research board's `owner_language`.

- [ ] **Step 4: Run the threads gate**

  Run:

  ```bash
  npm run -s check:threads
  ```

  Expected: exit 0.

- [ ] **Step 5: Commit**

  ```bash
  git add data/queries/raw/blue-staffy-puppies-london/threads.json data/queries/thread-ledger.json
  git commit -m "research(london): buyer threads and owner language (row 5)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 10: The question file (row 5; the builder's section target and FAQ picks)

**Files:**
- Create: `data/queries/blue-staffy-puppies-london.json`
- Test: `npm run -s check:queries && npm run -s check:competitors && npm run -s check:gaps`

- [ ] **Step 1: Build the question file**

  The primary keyword is `blue staffy puppies london`, the row's title. The row's `h1` is empty, and `data/locations.json` is generated, so it is never edited. Run:

  ```bash
  python3 scripts/query_augment.py blue-staffy-puppies-london --page-type location \
    --keyword "blue staffy puppies london" --route /uk-locations/blue-staffy-puppies-london/
  ```

  Expected: exit 0, and a printed `kept N covered_by and M headings, dropped K`.

  On exit 5, too few fact-backed questions exist for a block. Show the blocked list to the controller and stop. Never pad a block.

  On exit 6, fix the named raw file from its source response.

- [ ] **Step 2: Read the target and the picks**

  Run:

  ```bash
  python3 -c "
  import json;q=json.load(open('data/queries/blue-staffy-puppies-london.json'))
  print('section_target', q['section_target']); print('word_target', q.get('word_target'))
  print('faq', {b: sum(1 for x in q['questions'] if x.get('faq')==b) for b in ('top','middle','bottom')})
  print('extra', [e.get('topic') for e in q['extra_sections']])"
  ```

  Expected:
  - `section_target.total` is at least 9;
  - the FAQ picks total 15–20 (top 5–7, middle 5–7, bottom 7–10);
  - there are three extra sections.

  If `word_target` has no median, the band is the user's 2,000–3,000 (Ruling 8), recorded on the research board.

- [ ] **Step 3: Run the gates**

  Run:

  ```bash
  npm run -s check:queries; npm run -s check:competitors; npm run -s check:gaps
  ```

  Expected: each exits 0. `check:queries` prints London as awaiting rebuild, which is correct until Task 28.

- [ ] **Step 4: Commit**

  ```bash
  git add data/queries/blue-staffy-puppies-london.json
  git commit -m "research(london): question file: section target, FAQ picks, extra sections (row 5)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 11: LLM intel against the question file (row 5, step 5; no new call)

**Files:**
- Create: `docs/research/llm-intel/blue-staffy-puppies-london-${D}.json`

- [ ] **Step 1: Confirm no new call is needed**

  Run:

  ```bash
  python3 scripts/query_augment.py --preflight blue-staffy-puppies-london --source ai_engines
  ```

  Expected: exit 3 (cached). No call is made.

- [ ] **Step 2: Refresh the intel file**

  Dispatch `bsuk-llm-keyword-intel` with this brief:

  > "Run for blue-staffy-puppies-london from the saved response data/queries/raw/blue-staffy-puppies-london/ai_engines.response.json (bought 2026-09-25; preflight exits 3: make no call). Check the answer against the question file data/queries/blue-staffy-puppies-london.json this time, not the page map, and write docs/research/llm-intel/blue-staffy-puppies-london-<D>.json. Report bsuk_cited, citations, citation_gap and the engine entities the page lacks."

  Expected: `bsuk_cited: false`. `citation_gap` carries the registry ids the answer cited, and `page_source.kind` is no longer `page-map`.

- [ ] **Step 3: Commit**

  ```bash
  git add docs/research/llm-intel/blue-staffy-puppies-london-${D}.json
  git commit -m "research(london): LLM intel re-read against the question file (row 5)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 12: Keyword deliverables (row 6)

**Files:**
- Create: `docs/research/london-page-run/keyword-variants.json`, `docs/research/london-page-run/keyword-universe.json`
- Test: `python3 -m pytest tests/py/test_keyword_variants.py -q`

- [ ] **Step 1: Propose the four extra keyword types**

  Run:

  ```bash
  python3 scripts/keyword_variants.py blue-staffy-puppies-london > docs/research/london-page-run/keyword-variants.json
  ```

  Expected: exit 0, with `examined.documents` greater than 2 now that the SERP and the pages are cached. On 2026-09-30, before Tasks 5–8, it read 2 documents. Exit 6 means nothing is cached; go back to Task 8.

- [ ] **Step 2: Write the keyword universe**

  Write `docs/research/london-page-run/keyword-universe.json`: one entry per keyword, `{"keyword", "intent", "type", "volume", "source"}`.

  - `intent` is one of `transactional`, `commercial`, `informational`, `navigational` or `local`.
  - `type` is one of `primary`, `secondary`, `question`, `variation`, `related`, `cooccurring` or `similar`.
  - `volume` is the barrier line from Task 3.
  - `source` names where the keyword came from.

  The sources are:
  1. the primary keyword, `blue staffy puppies london`;
  2. the Google PAA and related searches (`serp_google.json`);
  3. Bing's related questions;
  4. the cluster strategy's London phrases (`docs/superpowers/sessions/2026-09-25-location-pages-strategy.md` lines 23–24 and 107): "staffordshire bull terrier puppies and dogs for sale in london", "staffie puppies in london" and "staffies in london";
  5. the gap matrix rows (`docs/research/gap-matrix-2026-09-25.md` lines 97 and 108);
  6. the four buckets from Step 1;
  7. the deposit-fear phrases found in Task 9's threads, quoted as found.

  Never add a keyword no source holds.

- [ ] **Step 3: Run the test**

  Run:

  ```bash
  python3 -m pytest tests/py/test_keyword_variants.py -q
  ```

  Expected: PASS.

- [ ] **Step 4: Commit**

  ```bash
  git add docs/research/london-page-run/keyword-variants.json docs/research/london-page-run/keyword-universe.json
  git commit -m "research(london): keyword variants and keyword universe (row 6)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 13: Entities and co-occurrence (row 7)

**Files:**
- Create: `docs/research/london-page-run/entities.md`
- Modify: `data/bsuk-ontology.json` (only a new entity, as `PROPOSED`, with its source)
- Test: `python3 scripts/ontology_seed.py --check`

- [ ] **Step 1: Check the ontology**

  Run:

  ```bash
  python3 scripts/ontology_seed.py --check
  ```

  This is advisory. Note its output.

- [ ] **Step 2: Recommend the entities**

  Dispatch `bsuk-entity-incorporation-agent`, Move 2 only (the recommended entities, each with its why), with this brief:

  > "For blue-staffy-puppies-london, recommend entities per planned section group: (1) the deposit, viewing and video call; (2) the litter, prices and parents Maggie and Jones; (3) delivery to London and collection in Carlisle; (4) health tests (L-2-HGA, HC-HSF4, eye screening, elbow screening; tests named only, never a result); (5) raising (Puppy Culture, ENS, home-raised); (6) life with a Staffy in London (flats, exercise, children, time alone); (7) buyer safety. Ground each in the LLM-intel entities (docs/research/llm-intel/blue-staffy-puppies-london-<D>.json), the PAA and threads (data/queries/raw/blue-staffy-puppies-london/), or a competitor gap (docs/research/gap-matrix-2026-09-25.md). Use only ids in data/bsuk-ontology.json; a new one is added PROPOSED with its source. Nothing about a licence."

- [ ] **Step 3: Write the entities file**

  Write the agent's result to `docs/research/london-page-run/entities.md`, grouped by ontology class.

- [ ] **Step 4: Commit**

  ```bash
  git add docs/research/london-page-run/entities.md data/bsuk-ontology.json
  git commit -m "research(london): entities per section group, ontology-backed (row 7)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

## Phase D: The research board (row 8, STOP 1)

### Task 14: Competitor findings: why each ranks, weakness, reverse-engineering

**Files:**
- Modify: `docs/research/london-page-run/serp-findings.md`

- [ ] **Step 1: Read every saved page**

  Dispatch `bsuk-framework-agent` with this brief:

  > "Read each saved page under data/queries/cache/blue-staffy-puppies-london/<n>.html (the pool in data/queries/raw/blue-staffy-puppies-london/competitors.json). Fetch nothing new. The registry report docs/research/competitors/<id>.md may be read as supporting evidence where the page's domain is a registry competitor. For every top-5 result on Google or Bing, write:
  > - `url`
  > - `type` (marketplace, breeder, directory, rescue, information)
  > - `why_ranks`
  > - `weakness` (our wedge)
  > - `evidence` (the cache path `data/queries/cache/blue-staffy-puppies-london/<n>.html`, or a docs/research/competitors/<id>.md path)
  > - `fetched` (the capture date)
  > - heading counts H1–H6
  > - tables
  > - faq (true/false)
  > - byline
  > - JSON-LD schema types
  > - its heading style class.
  >
  > Then write: the universal gaps every fetched page misses; the heading shape that wins; the SERP schema list; and a one-paragraph structural read of the SERP. A page you cannot read is `NOT FETCHED — <what was tried and what stopped it>`. Words and H2 counts are never retyped: they are read from data/queries/blue-staffy-puppies-london.json."

  Append the result to `docs/research/london-page-run/serp-findings.md` under `## Competitors`, `## Universal gaps`, `## Heading types`, `## SERP schema` and `## Structural read`.

- [ ] **Step 2: Capture the AI Overview if the paid SERP did not**

  If Task 5 found no `ai_overview` item, dispatch `bsuk-paa-agent`:

  > "Load Google UK for 'blue staffy puppies london' in Playwright and capture the AI Overview's text and cited domains, or record that none was shown. On a robot check write NOT FETCHED — Google returned a robot check on <D>."

  Append the result under `## AI Overview`.

- [ ] **Step 3: Commit**

  ```bash
  git add docs/research/london-page-run/serp-findings.md
  git commit -m "research(london): why each competitor ranks, weaknesses, reverse-engineering (row 8)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 15: The options: angles, strategies, frameworks

**Files:**
- Create: `docs/research/london-page-run/angles.md`, `docs/research/london-page-run/strategies.md`, `docs/research/london-page-run/frameworks.md`
- Test: `python3 scripts/strategy_cite_check.py docs/research/london-page-run/strategies.md`

- [ ] **Step 1: Three angles**

  Dispatch `bsuk-angle-agent` with this brief:

  > "Three angle options with hooks for the London city page, from the research in docs/research/london-page-run/ and data/queries/blue-staffy-puppies-london.json. The primary reader fear is paying the deposit before seeing the puppy (session brief Q8); the facts that answer it are the deposit books the viewing and reserves the puppy, it comes off the price, a live video call with the puppy and its mother is offered on request before any deposit, the deposit is paid by bank transfer. No refund percentage (not in data yet). No licence. Mark exactly one (Recommended), with its why from the research (a competitor weakness, a thread quote or the AI Overview) and its named trade-off."

  Write the result to `angles.md`.

- [ ] **Step 2: Two or three strategy directions**

  S1 is the cluster strategy's London row, verbatim, citing `docs/superpowers/sessions/2026-09-25-location-pages-strategy.md` line 107. Dispatch `bsuk-strategy-synthesizer` for S2 and S3:

  > "Two alternative strategy directions for /uk-locations/blue-staffy-puppies-london/ only, each citing the research files it rests on (docs/research/london-page-run/serp-findings.md, the gap matrix, the question file). Mark one of S1–S3 (Recommended) with its why and trade-off."

  Write all three to `strategies.md`.

- [ ] **Step 3: Frameworks per section group**

  Dispatch `bsuk-content-architect` to route the framework options per planned section group:
  - hero and opening;
  - the deposit and viewing;
  - the litter and prices;
  - delivery and collection;
  - health and raising;
  - London life;
  - the FAQ blocks.

  Each group gets two or three options from the `framework-*` skills, using the board schema's names: EEBP, FAB, QAB, PAS, BAB, PDB, AIDA, EBD and HSS. One option per group is marked (Recommended), with its why and trade-off.

  Also record the header-style line (`rules/headings.md` `header-style-declared`). Recommended: Style 1 Pure Conversational, FAQ register. The grounds are the user's ruling that every H2 and H3 is a buyer question (answer board, 2026-09-27) and the question file's PAA share. Name the trade-off: less room for exact-match heading keywords.

  Write the result to `frameworks.md`.

- [ ] **Step 4: Check the strategy citations**

  Run:

  ```bash
  python3 scripts/strategy_cite_check.py docs/research/london-page-run/strategies.md
  ```

  Expected: exit 0.

- [ ] **Step 5: Commit**

  ```bash
  git add docs/research/london-page-run/angles.md docs/research/london-page-run/strategies.md docs/research/london-page-run/frameworks.md
  git commit -m "research(london): three angles, three strategies, frameworks per section group (row 8)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 16: Assemble and validate the research-board record

**Files:**
- Create: `data/research-boards/blue-staffy-puppies-london.json`, `docs/artifacts/research/blue-staffy-puppies-london.html`, `docs/artifacts/research/blue-staffy-puppies-london.md`
- Test: `python3 -m pytest tests/py/test_research_board_builder.py tests/py/test_research_board_rule.py -q`

- [ ] **Step 1: Write the record**

  Write the record with every field the builder requires. `tests/py/fixtures/research_board/record.json` is the worked shape. The top-level keys, all required, are:
  - `slug`, `page_type`, `route`, `date`, `queries_file`, `method`, `approval`;
  - `serp`, `intent`, `reverse_engineering`, `universal_gaps`, `owner_language`, `fanout`;
  - `why_competitors_rank`, `how_we_win`, `content_gap`;
  - `entities`, `angles`, `strategies`, `frameworks`, `keywords`;
  - `ai_overview`, `heading_types`, `serp_schema`, `authority`.

  The values are:

  ```json
  {
   "slug": "blue-staffy-puppies-london",
   "page_type": "location",
   "route": "/uk-locations/blue-staffy-puppies-london/",
   "date": "<D>",
   "queries_file": "data/queries/blue-staffy-puppies-london.json",
   "method": "Research for London's page run: Google SERP + PAA (DataForSEO, <D>), Bing read free in the browser, competitor pages saved under data/queries/cache/blue-staffy-puppies-london/, threads via bsuk-reddit-threads, ChatGPT answer (2026-09-25, reused), keyword variants from the cache. Keyword volumes and authority NOT FETCHED (spend guard has no source).",
   "approval": null
  }
  ```

  The remaining fields are filled from the research files:

  | Field | Source |
  |---|---|
  | `serp.results` and `serp.structural_read` | `serp-findings.md`, each result with `why_ranks`, `weakness`, `evidence` and `fetched` |
  | `intent` | four layers. `dominant`: transactional. `secondary`: from the SERP types. `emotional`: the deposit-before-viewing fear, citing the thread quote. `local`: delivery to London or collection in Carlisle |
  | `reverse_engineering[]` and `universal_gaps[]` | `serp-findings.md` (no `words` typed; the builder reads them from the query file) |
  | `owner_language` | Task 9's quotes with URLs, or its barrier line |
  | `fanout` | `paa` from `serp_google.json`, `threads` from `threads.json`, and `llm_intel`, the path of Task 11's file |
  | `why_competitors_rank`, `how_we_win[]` and `content_gap[]` | from sections 1–5. `how_we_win` includes "answer the deposit-before-viewing fear head-on, from data" |
  | `entities[]` | `entities.md`, as `{"id", "class"}` |
  | `angles[]`, `strategies[]` and `frameworks[]` | Task 15, exactly one `recommended: true` per choice, each with `why` and `trade_off` |
  | `keywords.universe` | `keyword-universe.json` |
  | `keywords.distribution` | one row per planned section group, `{"section", "primary": [...], "secondary": [...]}`. Every keyword is placed, or parked in a `parked` list with a reason |
  | `ai_overview` | `{"present", "says", "cites", "implication", "fetched", "evidence"}`, or the barrier line |
  | `heading_types` | `{"rows": [...], "winning_shape": "..."}` |
  | `serp_schema[]` | from `serp-findings.md` |
  | `authority` | `"NOT FETCHED — scripts/query_augment.py's spend guard has no backlinks source, so no DataForSEO backlinks call was made"` |

- [ ] **Step 2: Build the board**

  Run:

  ```bash
  python3 scripts/research_board.py blue-staffy-puppies-london
  ```

  Expected: exit 0, and it writes `docs/artifacts/research/blue-staffy-puppies-london.html` and `.md`.

  Exit 1 prints every problem: a top-5 competitor with no `why_ranks` or `weakness`, a finding with no evidence, a bare `NOT FETCHED`, or a missing section. Fix each in the record from the research files, never by inventing. Re-run until exit 0.

- [ ] **Step 3: Run the tests and the barrier lint**

  Run:

  ```bash
  python3 -m pytest tests/py/test_research_board_builder.py tests/py/test_research_board_rule.py -q
  npm run -s check:barriers
  ```

  Expected: PASS and exit 0.

- [ ] **Step 4: Commit**

  ```bash
  git add data/research-boards/blue-staffy-puppies-london.json docs/artifacts/research/blue-staffy-puppies-london.html docs/artifacts/research/blue-staffy-puppies-london.md
  git commit -m "research(london): research-board record and board page (row 8)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 17 (CONTROLLER): STOP 1, the research board

**Files:**
- Create: `docs/reference/answer-board/batches/${D}-research-board-blue-staffy-puppies-london.md` and `.json`, `docs/reference/answer-board/answers/${D}-research-board-blue-staffy-puppies-london-<received date>.json` and `.md`
- Modify: `data/research-boards/blue-staffy-puppies-london.json` (`approval`)

- [ ] **Step 1: Publish the board**

  Publish `docs/artifacts/research/blue-staffy-puppies-london.html` with the Artifact tool, icon `chart`. Keep the URL for the batch.

- [ ] **Step 2: Write the batch sheet**

  Write `docs/reference/answer-board/batches/${D}-research-board-blue-staffy-puppies-london.md`. In each question, put the option marked (Recommended) first, with its why and trade-off copied from the record, and link the research-board URL:

  ```markdown
  # London research board · pick the angle, strategy, frameworks and keywords

  The research board for /uk-locations/blue-staffy-puppies-london/: <research-board URL>. Nothing is outlined until you pick.

  ## Direction

  1. **Which angle should the London page take?** <A1 hook — Recommended: why · trade-off>
     **Where it goes:** the outline's H1, opening and section order.
     - (a) A1 <hook>
     - (b) A2 <hook>
     - (c) A3 <hook>
  2. **Which strategy direction?** <S1 from the cluster strategy; S2; S3 — the recommended one marked, with why and trade-off>
     - (a) S1
     - (b) S2
     - (c) S3
  3. **Which framework for each section group?** One line per group from the record's `frameworks`; the recommended pick is (a).
     - (a) Take every recommended framework
     - (b) Change some (say which in the text box)

  ## Keywords and size

  4. **Is this keyword universe and its distribution right?** <counts by intent; the primary keyword; volumes NOT FETCHED and why>
     - (a) Yes, as shown
     - (b) Change it (say what in the text box)
  5. **Word band?** <the query file's median, or: the median is NOT FETCHED, so 2,000–3,000 per your 2026-09-27 ruling>
     - (a) <the band shown>
     - (b) Another band (type it)
  6. **External links without a council licensing page?** London has 33 borough councils and the licence stays off the site, so the six external links would come from gov, registry, vet-charity, welfare and research sources, with no `local` row. Recommended: (a). Trade-off: no local-authority signal on the page.
     - (a) Yes, no local council link
     - (b) Add a London council page that says nothing about licensing (name it in the text box)
  ```

- [ ] **Step 3: Post the batch**

  Run:

  ```bash
  D=$(date +%F)
  python3 scripts/answer_board_batch.py docs/reference/answer-board/batches/${D}-research-board-blue-staffy-puppies-london.md --project project-5 --batch-id ${D}-research-board-blue-staffy-puppies-london
  ```

  Then run ArtifactData `set` on the board URL: collection `batches`, doc_id `${D}-research-board-blue-staffy-puppies-london`, `file_path` the printed JSON.

- [ ] **Step 4: Commit the sheet and the JSON**

  ```bash
  git add docs/reference/answer-board/batches/${D}-research-board-blue-staffy-puppies-london.md docs/reference/answer-board/batches/${D}-research-board-blue-staffy-puppies-london.json
  git commit -m "docs: answer-board batch — London research board (STOP 1)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

- [ ] **Step 5: STOP**

  Say in chat only: "6 new questions on the board: https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf". End the turn, and wait for the user's Send.

- [ ] **Step 6: Save the answers**

  On the Send, follow `docs/reference/answer-board/README.md` "Receive answers":
  - ArtifactData `get` `batches/<batchId>/submissions` `s-…`;
  - save the result as `docs/reference/answer-board/answers/${D}-research-board-blue-staffy-puppies-london-<received date>.json` and `.md`;
  - commit;
  - ArtifactData `update` the batch to `received`;
  - reply in the Send's thread.

- [ ] **Step 7: Record the approval**

  Run:

  ```bash
  python3 scripts/research_board.py blue-staffy-puppies-london --approve --answers docs/reference/answer-board/answers/<that file>.json
  ```

  Expected: exit 0, and `approval` is stamped with `record_hash`.

  If the user picked "change" on any question, apply the change to the record first, re-run `python3 scripts/research_board.py blue-staffy-puppies-london` (it must exit 0), republish the board, and only then approve.

- [ ] **Step 8: Commit**

  ```bash
  git add data/research-boards/blue-staffy-puppies-london.json docs/reference/answer-board/answers/
  git commit -m "research(london): STOP 1 approved — research-board picks recorded

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

## Phase E: The outline (row 9, STOP 2)

### Task 18: Write the outline record from the picks

**Files:**
- Create: `data/outlines/blue-staffy-puppies-london.json`
- Test: `python3 scripts/outline_matrix.py blue-staffy-puppies-london --check`

- [ ] **Step 1: Confirm the research board is approved as it stands**

  Run:

  ```bash
  python3 scripts/outline_matrix.py blue-staffy-puppies-london --check; echo "exit $?"
  ```

  Expected: exit 2 ("no record"). An exit 2 that names the research board means STOP 1 is not recorded. Go back to Task 17.

- [ ] **Step 2: Write the record**

  The shape is `tests/py/fixtures/outline_matrix/good.json`. Build it as follows.

  **Top-level fields:**
  - `slug`: `blue-staffy-puppies-london`
  - `page_type`: `location`
  - `route`: `/uk-locations/blue-staffy-puppies-london/`
  - `date`: `<D>`
  - `research_board`: `data/research-boards/blue-staffy-puppies-london.json`
  - `h1`: the picked angle's H1, a buyer question in Title Case that carries "Blue Staffy" and "London" (`h1-pick-is-final`: once it is picked on the board it is never re-asked)
  - `word_target`: `{"min": 2000, "max": 3000, "source": "median NOT FETCHED in data/queries/blue-staffy-puppies-london.json; the user's 2,000–3,000 band (answer board 2026-09-27), confirmed at STOP 1 q05"}`, or the band the user picked at STOP 1
  - `header_style`: `"Style 1 Pure Conversational · FAQ register — every H2/H3 a buyer question (user, 2026-09-27)"`
  - `schema`: `"LocalBusiness (areaServed London; no telephone while PHONE_PLACEHOLDER) + FAQPage (exactly the visible questions) + BreadcrumbList + VideoObject if the video section is kept + Product only where a puppy card shows (one offer each)"`
  - `components`: `"Chosen at STOP 3 (the page board), after this outline is approved; the 15 London picks are the menu."`
  - `approval`: `null`

  **Frame rows (`cat` A, `framework` `—` where the row has no heading below H1):**
  - Hero, the H1;
  - Counter strip;
  - Trust strip;
  - Contents;
  - Key takeaways;
  - the Review rows at top, middle and bottom (one `data/reviews.json` row each);
  - Newsletter;
  - Enquiry form.

  **Body rows:**
  - There are exactly `section_target.total` of them, from the question file. They are split evenly across the three gaps of the builder's spine: after FAQ top, after FAQ middle, and after the newsletter.
  - Every H2 and H3 is a buyer question. Every H3 has an H4, and the ladder reaches H5 and H6 in at least one section, so the census holds one H1 and all six levels with no skipped level. H5 and H6 at five or more each is advisory on a location page.
  - The first body section after FAQ top is the deposit-before-viewing section. It is `cat: "C"`, with `why_source` set to the `how_we_win` index that names the deposit fear. It carries the video-call-on-request, bank-transfer and comes-off-the-price facts, and no refund percentage.
  - Each of the three `extra_sections` is one H2 row, `cat: "C"`, with `why_source` set to its `content_gap[i]` or `universal_gaps[i]` index.
  - A row matched to a fetched competitor section is `cat: "B"`, with `why_source` set to `serp.results[i]`.
  - Each row carries `framework` (its STOP 1 pick), `words` (the rows sum inside the word target), `keywords` (`primary` and `secondary`, placed exactly as `keywords.distribution` placed them, matched by section name) and `image` (a slot description; FAQ rows excepted).

  **FAQ rows:** three rows with `faq: true`, top, middle and bottom. Each is an H2 whose H3 children are exactly the question file's picks for that block, in score order, with city wording only where the meaning is unchanged. There are 15–20 H3s in total. No H3 repeats a body heading.

- [ ] **Step 3: Validate**

  Run:

  ```bash
  python3 scripts/outline_matrix.py blue-staffy-puppies-london --check
  ```

  Expected: exit 0. Exit 1 prints each broken rule:
  - a row with no Cat, framework, words or Why;
  - a B or C `why_source` that does not resolve;
  - a keyword outside the universe;
  - a heading with no image;
  - a skipped level;
  - a census without exactly one H1;
  - a sum outside the word target.

  Fix each from the research board and re-run until exit 0.

- [ ] **Step 4: Commit**

  ```bash
  git add data/outlines/blue-staffy-puppies-london.json
  git commit -m "outline(london): section matrix written from the STOP 1 picks (row 9)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 19: Entities, internal links and external links per section (row 9, steps 4–5)

**Files:**
- Modify: `data/outlines/blue-staffy-puppies-london.json` (each section's `entities`)
- Create: `docs/research/london-page-run/links-plan.md`
- Modify (only when a new row is needed): `docs/reference/external-link-library.md`
- Test: `python3 -m pytest tests/py/test_link_library.py tests/py/test_link_diversity.py -q`

- [ ] **Step 1: Run the entity loop**

  Dispatch `bsuk-entity-incorporation-agent`, Moves 1, 2 and 4, per outline section:
  - the structural critique;
  - each section's `entities` (ontology ids, each with its why);
  - its internal links and schema notes.

  Write the `entities` arrays into the outline rows. Put the internal links into `links-plan.md` as a table:

  | Section | Target | Anchor text | anchor_type | Purpose | Resolves today |
  |---|---|---|---|---|---|

  Internal targets are only these real routes:
  - `/available-puppies/` and its puppy pages;
  - `/buy-blue-staffy-puppies-uk/`, `/buy-staffy-puppies-for-sale-uk/` and `/blue-staffy-pup-sale-uk/`;
  - `/uk-blue-staffy-puppy-buying-guide/`;
  - `/uk-staffordshire-bull-terrier-guide/`;
  - `/blue-staffy-health-uk/`, the source for health claims;
  - `/blue-staffy-uk-breeders/`;
  - `/uk-blue-staffy-breeders-contact/`;
  - `/`;
  - `/blue-staffy-blog-guides/`;
  - `/uk-locations/`;
  - 3–5 nearby city pages from `data/locations.json`, picked by real proximity to London.

  The anchors cover three or more types with at most two exact. No anchor repeats on the page, and no anchor reuses one that another board in `data/boards/` uses for the same route.

- [ ] **Step 2: Plan the external links**

  Dispatch `bsuk-external-link-agent`, Protocol A, with this brief:

  > "Six external links on six domains from four source types for London's outline, from docs/reference/external-link-library.md only: no licensing page, no council page (STOP 1 q06 unless the user picked (b)), no competitor, no marketplace. Candidate set:
  > - gov.uk banned-dogs (gov)
  > - royalkennelclub.com (registry)
  > - pdsa.org.uk (vet-charity)
  > - bva.co.uk (vet-charity)
  > - rspca.org.uk or dogstrust.org.uk (welfare)
  > - pmc.ncbi.nlm.nih.gov (research)
  >
  > Live-check each with `curl -sIL -o /dev/null -w '%{http_code}' <url>` and keep only 200s. Each link Link-First, typed (≥3 external anchor types), mapped to the section claim it stands behind."

  Append the external table to `links-plan.md`. A new library row is dated `YYYY-MM-DD · 200` and typed.

- [ ] **Step 3: Test and re-validate**

  Run:

  ```bash
  python3 -m pytest tests/py/test_link_library.py tests/py/test_link_diversity.py -q
  python3 scripts/outline_matrix.py blue-staffy-puppies-london --check
  ```

  Expected: PASS and exit 0.

- [ ] **Step 4: Commit**

  ```bash
  git add data/outlines/blue-staffy-puppies-london.json docs/research/london-page-run/links-plan.md docs/reference/external-link-library.md
  git commit -m "outline(london): entities per section; internal and six external links planned (row 9)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 20 (CONTROLLER): STOP 2, the outline

**Files:**
- Create: `docs/artifacts/outlines/blue-staffy-puppies-london.html` and `.md`, `docs/reference/answer-board/batches/${D}-outline-blue-staffy-puppies-london.md` and `.json`, the answers file pair
- Modify: `data/outlines/blue-staffy-puppies-london.json` (`approval`)

- [ ] **Step 1: Build the matrix**

  Run:

  ```bash
  python3 scripts/outline_matrix.py blue-staffy-puppies-london
  ```

  Expected: exit 0, and it writes the `.html` and `.md`.

- [ ] **Step 2: Publish and post**

  Publish the `.html` as an Artifact, icon `list`. Write the sheet `docs/reference/answer-board/batches/${D}-outline-blue-staffy-puppies-london.md`:

  ```markdown
  # London outline · approve the section matrix

  The section matrix for /uk-locations/blue-staffy-puppies-london/: <outline URL>. Every H2 and H3 with its keywords, words, Cat, Why and image. No component is chosen until you approve.

  ## Approval

  1. **Approve the London outline as shown?** Recommended: (a). Why: every row cites the research board you approved; the deposit-before-viewing section comes first after the top FAQ. Trade-off: <words total> words sits <inside the band / at its edge>.
     - (a) Approve as shown
     - (b) Approve with changes (say which rows in the text box)
     - (c) Not yet (say why)
  2. **Is the H1 right?** "<H1>" (the picked angle's H1).
     - (a) Yes
     - (b) Use this H1 instead (type it)
  ```

  Then run:

  ```bash
  D=$(date +%F)
  python3 scripts/answer_board_batch.py docs/reference/answer-board/batches/${D}-outline-blue-staffy-puppies-london.md --project project-5 --batch-id ${D}-outline-blue-staffy-puppies-london
  ```

  ArtifactData `set` the batch, and commit the sheet and the JSON with the message `docs: answer-board batch — London outline (STOP 2)`.

- [ ] **Step 3: STOP**

  Say in chat only: "2 new questions on the board: https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf". End the turn and wait.

- [ ] **Step 4: Save the answers**

  On the Send, save the answers as `docs/reference/answer-board/answers/${D}-outline-blue-staffy-puppies-london-<received date>.json` and `.md`, then mark the batch received and reply in the thread.

- [ ] **Step 5: Apply any changes**

  If the user picked (b) on either question, edit the record, re-run `python3 scripts/outline_matrix.py blue-staffy-puppies-london` (it must exit 0), and republish the matrix.

- [ ] **Step 6: Record the approval**

  Run:

  ```bash
  python3 scripts/outline_matrix.py blue-staffy-puppies-london --approve --answers docs/reference/answer-board/answers/<that file>.json
  ```

  Expected: exit 0. The command refuses the research board's answers file.

- [ ] **Step 7: Commit**

  ```bash
  git add data/outlines/blue-staffy-puppies-london.json docs/artifacts/outlines/ docs/reference/answer-board/answers/
  git commit -m "outline(london): STOP 2 approved — section matrix recorded

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

## Phase F: The page board (row 10, STOP 3)

### Task 21: Write the page-board record from the approved outline

**Files:**
- Create: `data/boards/blue-staffy-puppies-london.json`
- Test: `python3 -m pytest tests/py/test_rule16_gate.py tests/py/test_anchor_types.py tests/py/test_link_diversity.py tests/py/test_image_rules.py tests/py/test_outline_approval.py -q`

- [ ] **Step 1: Confirm the outline gate is open**

  Run:

  ```bash
  python3 -c "import sys;sys.path.insert(0,'scripts');import outline_matrix as OM;print(OM.approval_refusal('blue-staffy-puppies-london'))"
  ```

  Expected: `None`. Anything else means STOP 2 is not recorded as it stands. Go back to Task 20.

- [ ] **Step 2: Write the board record**

  The shape is `schemas/board.schema.json`, and `data/boards/index.json` is the worked example. Write:

  - **`meta`:**
    - the title (front-loaded with "Blue Staffy Puppies London", 70 characters or fewer);
    - the description (140–160 characters);
    - `slug`;
    - `canonical` `/uk-locations/blue-staffy-puppies-london/`;
    - `h1`, the approved H1.

  - **`sections`:** copied from the approved outline, with the same ids, headings (the `tree`), keywords, `words`, `why` and `why_source`, unchanged. A body section that answers a competitor is `group: "COMPETITOR-BASED"`, with that competitor's URL in `why_source`. The four keyword types (`variation`, `related`, `cooccurring`, `similar`) go into the sections where they read naturally, from `keyword-variants.json`, so that each type holds at least one term on the page.

  - **The component mapping (block 5b).** Map each section to a London kit component by its `shape`. Use only the sections the outline has; never add a section to use a component:

    | Outline section | shape | Component (`data/design/city-picks/blue-staffy-puppies-london.json`) |
    |---|---|---|
    | Hero | `hero` | `CityHeroFilmstrip` (`london/hero/b`) |
    | Counter strip | `stats` | `CityPriceScale` (`london/counter-strip/c`); `stats` is `[{n, label, source}]` from `data/settings.json` and `data/price-matrix.json` only |
    | Trust strip | `trust` | `CityTrustLedger` (`london/trust-strip/c`) |
    | Contents, dial, jump links | `dial`, `strip` | `CityContentsPhotoIndex`, `CityDialPhotoMarker` and `CityJumpStepper` (nav slots of `CityShell`) |
    | Key takeaways | `takeaways` | `CityTakeawaysLedger` |
    | A litter or puppy section | `puppies` | `CityPuppySheet` |
    | A price comparison | `table` | `CityRoster`: a `table` shape with three styles at 1280 / 768 / 375 that stacks below 640px (rule 13) |
    | Video | `video` | `CityVideoPanel`: three styles (player in a card, on a steel band, click-to-play facade); the facade ships unless the user picks otherwise; id `settings.youtube_embeds[0]` (rule 14) |
    | Image-and-text body sections | `sheet` | `CityChapters` |
    | Reviews | `reviews` | `CityLetter`, style S1 ("One review given room"), one `data/reviews.json` row per slot |
    | FAQ top, middle, bottom | `faq` | `CityFaqLedger` (`block` buy, trust or life, per the outline's three rows) |
    | Newsletter | `strip` | `CityNewsletterNotice` |
    | Enquiry | `form` | `CityContactLineup` |

  - **`links`** (block 3, rule 12). Every row of `links-plan.md`, per section and once more as the page table, each with target, anchor, `anchor_type`, purpose and whether it resolves.

  - **`assets[]`.** One row per image slot: `{slot, kind, w, h, required}` for the hero and every body H2 and H3. FAQ blocks are excepted.

  - **`entities`.** Per section, from the outline.

  - **`dropped`.** `{}`: the facts extract was empty.

- [ ] **Step 3: Fill the image candidates (block 7, first pass)**

  Run:

  ```bash
  python3 scripts/image_candidates.py blue-staffy-puppies-london --write
  ```

  Expected: exit 0. Every slot offers the page's own images first, then the site's served images, then `/Users/apple/Downloads/BSUK/bluestaffyuk-cms/Assets/Images`. Set each slot's `source` to `existing`, `assets-folder` or `infographic` (with an IG-1 to IG-5 style from `IMAGE-DESIGNS.md`), never `generate`: `GEMINI_API_KEY` is absent.

  Maggie and Jones use their served parent images: `maggie-blue-staffy-dam-with-pups.webp`, `jones-magnificent-blue-staffy-sire.webp` and `jones-strong-staffy-sire-temperament.webp`. A served image keeps its served alt on its first use, and a repeat gets a new alt. The primary keyword goes in the hero alt only.

- [ ] **Step 4: Build the site, the previews and the board**

  Run:

  ```bash
  npm run -s build
  python3 scripts/build_board_previews.py blue-staffy-puppies-london
  python3 scripts/build_page_board.py blue-staffy-puppies-london
  ```

  Expected: exit 0 on all three, and the last writes `docs/artifacts/boards/blue-staffy-puppies-london.html`. Exit 2 with `outline-unapproved` means the outline was edited after STOP 2. Revert that edit.

- [ ] **Step 5: Measure ours against the top five**

  Run:

  ```bash
  python3 scripts/keyword_metrics.py blue-staffy-puppies-london; echo "exit $?"
  ```

  Expected: exit 0, with no FAIL on title-front-load, first-100-words or the primary keyword. A FAIL is fixed in the board's `meta` or H1 wording, and the change is shown at STOP 3.

- [ ] **Step 6: Run the tests**

  Run:

  ```bash
  python3 -m pytest tests/py/test_rule16_gate.py tests/py/test_anchor_types.py tests/py/test_link_diversity.py tests/py/test_image_rules.py tests/py/test_outline_approval.py -q
  ```

  Expected: PASS.

- [ ] **Step 7: Commit**

  ```bash
  git add data/boards/blue-staffy-puppies-london.json docs/artifacts/boards/blue-staffy-puppies-london.html
  git commit -m "board(london): page board from the approved outline — components, links, images (row 10)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 22: Read the board as approval will see it

**Files:** none (read-only).

- [ ] **Step 1: Run the gate**

  Run:

  ```bash
  python3 scripts/board_gate.py blue-staffy-puppies-london; echo "exit $?"
  ```

  Expected: FAIL only on `unapproved`, plus the build-gate image checks that can pass only after publish. Every block-7b project 5 rule reads PASS:
  - `external-links-six-diverse`;
  - `anchor-type-variation`;
  - `keyword-variants-missing`;
  - `image-slot-missing`;
  - `image-asset-row-missing`;
  - `entity-blocked`.

  Any other FAIL is fixed in the record, followed by a rebuild of the board (Task 21 Steps 4–7).

- [ ] **Step 2: Report**

  Report the gate's output to the controller.

### Task 23 (CONTROLLER): STOP 3, the page board

**Files:**
- Create: `docs/reference/answer-board/batches/${D}-page-board-blue-staffy-puppies-london.md` and `.json`, `data/boards/inbox/blue-staffy-puppies-london.json`, the answers file pair
- Modify: `data/boards/blue-staffy-puppies-london.json` (approval), `data/component-ledger.json`

- [ ] **Step 1: Publish the board**

  Publish `docs/artifacts/boards/blue-staffy-puppies-london.html` as an Artifact, icon `layout`, with `capabilities={"db": {}}` (the board writes its approval to its own db).

- [ ] **Step 2: Post the batch**

  Write the sheet `docs/reference/answer-board/batches/${D}-page-board-blue-staffy-puppies-london.md`:

  ```markdown
  # London page board · approve the components, links and images

  The page board: <board URL>. It maps each approved outline section to a London kit component, lists every link (internal and external, with anchor types) and every image slot. Make your picks on the board itself and press its approve button; this question records that you have.

  ## Approval

  1. **Have you approved the London page board?** Recommended: (a). Why: block 7b shows every project 5 rule passing. Trade-off: the image slots with no photo of London itself use served photos of our puppies.
     - (a) Approved on the board
     - (b) Changes needed (say which in the text box)
  ```

  Then run:

  ```bash
  D=$(date +%F)
  python3 scripts/answer_board_batch.py docs/reference/answer-board/batches/${D}-page-board-blue-staffy-puppies-london.md --project project-5 --batch-id ${D}-page-board-blue-staffy-puppies-london
  ```

  ArtifactData `set` the batch, and commit the sheet and the JSON.

- [ ] **Step 3: STOP**

  Say in chat only: "1 new question on the board: https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf". End the turn and wait.

- [ ] **Step 4: Save the answers and read the board's db**

  On the Send:
  1. Save the answers file pair and mark the batch received.
  2. ArtifactData `get` on the page board's URL, collection `boards`, doc_id `blue-staffy-puppies-london`.
  3. Save the result as `data/boards/inbox/blue-staffy-puppies-london.json`.

- [ ] **Step 5: Record the approval**

  Run:

  ```bash
  npm run -s build
  python3 scripts/board_approve.py blue-staffy-puppies-london
  ```

  Expected: exit 0. The status is `approved`, the picks are copied in, and `data/component-ledger.json` is appended.

  A refusal names its cause: a stale hash, a heading collision, or a block-7b FAIL. Fix the record, rebuild the board, republish, and ask again. That is a new batch, never a re-`set` of a received one.

- [ ] **Step 6: Commit**

  ```bash
  git add data/boards/blue-staffy-puppies-london.json data/boards/inbox/blue-staffy-puppies-london.json data/component-ledger.json docs/reference/answer-board/
  git commit -m "board(london): STOP 3 approved — page board recorded

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

## Phase G: Images and the Asset Gate (row 11, STOP 4)

### Task 24: Ingest the picked images

**Files:**
- Create: `public/images/<stem>.webp` and `<stem>-760.webp`, only through the script, for each `assets-folder` pick
- Modify: `data/boards/blue-staffy-puppies-london.json` (`assets[].file` and `status`), `data/image-manifest.json` (written by the script)
- Test: `python3 -m pytest tests/py/test_uniform_image_box.py tests/py/test_served_alt_preserved.py -q`

- [ ] **Step 1: Ingest each `assets-folder` pick**

  Run, for each pick:

  ```bash
  python3 scripts/ingest_image.py folder "/Users/apple/Downloads/BSUK/bluestaffyuk-cms/Assets/Images/<file>" --board blue-staffy-puppies-london --slot <slot> --stem <meaningful-stem> --og-style A
  ```

  Portraits use style A (contain, bone gradient), never blurfill. Expected: exit 0.

- [ ] **Step 2: Draft each infographic slot**

  Run, for each `infographic` slot:

  ```bash
  python3 scripts/ingest_image.py draft <master> --board blue-staffy-puppies-london --slot <slot> --infographic IG-<n>
  ```

  `<master>` is the infographic rendered by `bsuk-infographic-builder` from the slot's brief, using facts from data only. The draft lands under `data/boards/generated/`, awaiting its sha12 pick.

- [ ] **Step 3: Leave `existing` slots alone**

  `existing` slots need no ingest. The served file is reused at its own path (working rule 11), and nothing is renamed or re-encoded.

- [ ] **Step 4: Run the tests**

  Run:

  ```bash
  python3 -m pytest tests/py/test_uniform_image_box.py tests/py/test_served_alt_preserved.py -q
  ```

  Expected: PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add public/images/ data/image-manifest.json data/boards/blue-staffy-puppies-london.json data/boards/generated/
  git commit -m "images(london): picked folder images ingested; infographic drafts for the Asset Gate (row 11)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 25 (CONTROLLER): STOP 4, the Asset Gate

**Files:**
- Create: `docs/reference/answer-board/batches/${D}-asset-gate-blue-staffy-puppies-london.md` and `.json`, the answers file pair
- Modify: `data/boards/blue-staffy-puppies-london.json` (`approval.picks["img:<slot>"]`)

- [ ] **Step 1: Rebuild and republish the board (second pass)**

  Run:

  ```bash
  npm run -s build
  python3 scripts/build_page_board.py blue-staffy-puppies-london
  ```

  Republish the board to the same URL (same `file_path`). Block 7 now shows every draft with its sha12 and every ingested image.

- [ ] **Step 2: Post the batch**

  Write `docs/reference/answer-board/batches/${D}-asset-gate-blue-staffy-puppies-london.md`:

  ```markdown
  # London Asset Gate · approve each image by its pick

  The London board's image block, second pass: <board URL>. Each draft shows its sha12. Pick on the board; this question records that you have.

  ## Images

  1. **Have you approved every London image slot on the board?** Recommended: (a). Why: every body heading and the hero has a slot, filled from our own photos first. Trade-off: <n> infographic slots are drafts you are seeing for the first time.
     - (a) Approved on the board
     - (b) Changes needed (name the slots in the text box)
  ```

  Then run `answer_board_batch.py` with `--batch-id ${D}-asset-gate-blue-staffy-puppies-london`, ArtifactData `set`, and commit.

  If the board has no `infographic` or `assets-folder` slot, every slot is a served image already picked at STOP 3. The stop still runs: the question asks the user to confirm the image block as shown.

- [ ] **Step 3: STOP**

  Say in chat only: "1 new question on the board: https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf". End the turn and wait.

- [ ] **Step 4: Record the image picks**

  On the Send:
  1. Save the answers.
  2. ArtifactData `get` the board's db into `data/boards/inbox/blue-staffy-puppies-london.json`.
  3. Run:

     ```bash
     npm run -s build
     python3 scripts/board_approve.py blue-staffy-puppies-london
     ```

     Expected: exit 0, with the `img:<slot>` picks recorded.

- [ ] **Step 5: Publish each approved draft**

  Run, for each approved draft:

  ```bash
  python3 scripts/ingest_image.py publish --board blue-staffy-puppies-london --slot <slot> --stem <meaningful-stem>
  ```

- [ ] **Step 6: Check the board**

  Run:

  ```bash
  python3 scripts/board_gate.py blue-staffy-puppies-london
  ```

  Expected: PASS on every image rule except those that need the built page.

- [ ] **Step 7: Commit**

  ```bash
  git add data/boards/ public/images/ data/image-manifest.json docs/reference/answer-board/
  git commit -m "images(london): STOP 4 approved — Asset Gate picks recorded and published

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

## Phase H: Build from the outline (row 12)

### Task 26: The rebuilt page's own tests, written first

**Files:**
- Create: `tests/py/test_london_page.py`
- Modify: `tests/py/test_city_scaffold.py`

- [ ] **Step 1: Write the failing test file**

  Write `tests/py/test_london_page.py`:

  ```python
  """The London city page, rebuilt from its approved outline (page-run row 12).

  What must hold once the scaffold is replaced:
    - no scaffold marker and no migrated body: London is a rebuilt page;
    - the H1 is the approved outline's H1, and every body H2/H3 is a question;
    - facts come from data: no hand-typed £ in the page source, parents Maggie and Jones,
      the tests named and no result stated, nothing about a licence;
    - the deposit is never called plainly "refundable" (the user's ruling, 2026-09-27);
    - three FAQ blocks, 15-20 questions, and the page stays noindex until the user approves it.
  """
  import html as H
  import json
  import pathlib
  import re

  import pytest

  ROOT = pathlib.Path(__file__).resolve().parents[2]
  SLUG = "blue-staffy-puppies-london"
  SRC = ROOT / "src/pages/uk-locations" / f"{SLUG}.astro"
  BUILT = ROOT / "dist/uk-locations" / SLUG / "index.html"
  OUTLINE = ROOT / "data/outlines" / f"{SLUG}.json"


  def built():
      if not BUILT.exists():
          pytest.skip("run npm run build first")
      return BUILT.read_text(encoding="utf-8")


  def text(fragment):
      return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


  def main_text(html):
      return text(html.split("<main", 1)[1].split("</main>", 1)[0])


  def test_london_is_no_longer_a_scaffold():
      html = built()
      assert "data-city-scaffold" not in html
      assert "prose-migrated" not in html


  def test_the_h1_is_the_approved_outline_h1():
      outline = json.loads(OUTLINE.read_text())
      assert outline["approval"], "STOP 2 is recorded"
      h1s = [text(h) for h in re.findall(r"<h1[^>]*>(.*?)</h1>", built(), re.S)]
      assert h1s == [outline["h1"]]


  def test_every_body_h2_and_h3_is_a_question():
      html = built().split("<main", 1)[1].split("</main>", 1)[0]
      heads = [text(h) for h in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", html, re.S)]
      assert heads
      assert [h for h in heads if not h.endswith("?")] == []


  def test_no_price_is_typed_in_the_page_source():
      assert "£" not in SRC.read_text(encoding="utf-8")


  def test_the_parents_are_maggie_and_jones():
      body = main_text(built())
      assert "Maggie" in body and "Jones" in body


  def test_the_tests_are_named_and_no_result_is_stated():
      body = main_text(built())
      for name in ("L-2-HGA", "HC-HSF4"):
          assert name in body, name
      for m in re.finditer(r"L-2-HGA|HC-HSF4|eye screening|elbow screening", body, re.I):
          window = body[max(0, m.start() - 80): m.end() + 80].lower()
          assert not re.search(r"\bclear\b|\bcertified\b|will not be affected", window), window


  def test_nothing_about_a_licence():
      body = main_text(built()).lower()
      assert "licence" not in body and "license" not in body


  def test_the_deposit_is_never_plainly_refundable():
      body = main_text(built())
      for m in re.finditer(r"refundable", body, re.I):
          window = body[max(0, m.start() - 60): m.end() + 60]
          assert "70%" in window, window


  def test_no_research_placeholder_ships():
      assert "NOT FETCHED" not in main_text(built())


  def test_three_faq_blocks_and_fifteen_to_twenty_questions():
      html = built()
      assert html.count('data-faq-block="') == 3
      qs = re.findall(r"<h3[^>]*data-faq-q[^>]*>", html)
      assert 15 <= len(qs) <= 20, len(qs)


  def test_noindex_until_the_user_approves_the_page():
      assert re.search(r'<meta name="robots" content="noindex[^"]*"', built())
  ```

- [ ] **Step 2: Retire the scaffold-only assertions for London**

  In `tests/py/test_city_scaffold.py`, replace these tests:
  - `test_london_is_built_from_the_scaffold_and_every_other_city_from_the_template`;
  - `test_every_scaffold_is_noindex_and_in_no_sitemap`;
  - `test_every_pick_is_on_the_page_and_the_nav_set_is_the_citys`;
  - `test_the_migrated_body_stays_word_for_word_for_parity`;
  - the "the scaffold's FAQ questions are found" message.

  The replacement code:

  ```python
  def test_london_has_its_own_file_and_every_other_city_the_template():
      html = built()
      assert "prose-migrated" not in html, "London is rebuilt; its migrated body is gone"
      others = [l["slug"] for l in LOCATIONS if l["slug"] != SLUG]
      assert len(others) == len(LOCATIONS) - 1
      for slug in others:
          page = ROOT / "dist/uk-locations" / slug / "index.html"
          assert page.is_file(), slug
          body = page.read_text(encoding="utf-8")
          assert "prose-migrated" in body and "data-city-scaffold" not in body, slug


  def test_every_scaffold_is_noindex_and_in_no_sitemap():
      """The invariant, for any city (the quality review, M6). Once London is rebuilt there may
      be no scaffold at all, and that is a pass, not a skip."""
      built()
      shards = [s.read_text(encoding="utf-8") for s in (ROOT / "dist").glob("*sitemap*.xml")]
      assert shards
      for route, html in _scaffolds().items():
          assert re.search(r'<meta name="robots" content="noindex[^"]*"', html), route
          assert not [s for s in shards if f"{route}<" in s or f"{route}\"" in s], route


  def test_every_component_on_the_page_is_a_london_pick_and_the_nav_set_is_the_citys():
      """The kit is a menu (rules/gates.md outline-before-components): the approved outline
      decides which picks are used, so the page may use fewer than fifteen, never another's."""
      html = built()
      assert set(PICK_ROOTS) == set(PICKS["picks"].values())
      used = [key for key, root in PICK_ROOTS.items() if root in html]
      assert "london/hero/b" in used and "london/faq-blocks/a" in used
      assert html.count('data-faq-block="') == 3, "the three FAQ blocks"
      for kit in ('class="kit-dial', 'class="kit-strip', 'class="kit-sheet'):
          assert kit not in html, kit
      band = re.search(r"<div[^>]*data-city-jump-stepper[^>]*>", html).group(0)
      assert "data-strip" in band, "on a real page the band is the top chrome"
  ```

  Delete `test_the_migrated_body_stays_word_for_word_for_parity`: London is now held by `check:facts` against `data/facts/blue-staffy-puppies-london.json`. In `test_no_section_heading_repeats_an_faq_question`, change the message to `"the page's FAQ questions are found"`.

- [ ] **Step 3: Run the tests and see them fail**

  Run:

  ```bash
  npm run -s build
  python3 -m pytest tests/py/test_london_page.py tests/py/test_city_scaffold.py -q
  ```

  Expected: FAIL. `test_london_is_no_longer_a_scaffold`, `test_the_h1_is_the_approved_outline_h1`, `test_london_has_its_own_file_and_every_other_city_the_template` and the question-heading test fail on the scaffold.

- [ ] **Step 4: Commit the failing tests**

  ```bash
  git add tests/py/test_london_page.py tests/py/test_city_scaffold.py
  git commit -m "test(london): the rebuilt page's invariants, failing on the scaffold (row 12)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 27: Write the page from the approved board

**Files:**
- Modify: `src/pages/uk-locations/blue-staffy-puppies-london.astro`

- [ ] **Step 1: Read the sources first**

  Read the approved board `data/boards/blue-staffy-puppies-london.json`, then `data/settings.json`, `data/puppies.json`, `data/price-matrix.json`, `data/reviews.json`, `data/faq.json` and `src/lib/cityKit.ts`. Do not open any sibling page, board or built HTML for wording.

- [ ] **Step 2: Write the page top to bottom**

  Write the page in the board's section order, with each section's H2 its `heading` and its H3s its `tree` nodes, word for word (Title Case). Keep the scaffold's imports and data plumbing (`availablePuppies`, `numberWord`, `cityKit`). Replace every placeholder string. Remove the `migrated` section, its `<style>` rules, and `data-city-scaffold`. Keep `robots="noindex, follow"` (the close flips it, Task 37).

  Write the copy per section, drafting each section's prose through `bsuk-seo-content-writer` from the entity agent's approved draft:
  - The opening paragraph under each H2 and H3 answers its question conversationally, in Lisa Bright's first-person plural voice (`we`, `our`, `here at BlueStaffyUK`), inside the section's `words` band. Filter it through the `anti-ai-writing` skill.
  - Every fact is an interpolation, never typed:
    - `BOY_PRICE`, `GIRL_PRICE`, `DEPOSIT`, `DELIVERY_BAND` and `TOWN`;
    - `depositLine` and `depositBrief`;
    - `deliveryLine` and `transportLine`;
    - `guaranteeRow()`;
    - `settings.breeder_name`;
    - the puppies' names, colours and sexes from `availablePuppies()`.
  - The deposit section says: the deposit books the viewing and reserves the puppy, it comes off the price, a live video call with the puppy and its mother is offered on request before any deposit, and payment is by bank transfer. It carries no refund percentage (Ruling 2).
  - Health names L-2-HGA, HC-HSF4, eye screening and elbow screening, states no result, and links `/blue-staffy-health-uk/`.
  - Nothing mentions a licence.
  - The only law line is the builder skill's banned-breed line, linked to `https://www.gov.uk/control-dog-public/banned-dogs`, and only if the outline carries it.
  - Distance is only the delivery band or collection from `TOWN`: never a mileage, a journey time or a date.
  - Every link on the board, and no other, sits Link-First at the start of its sentence with the board's anchor.

  Build the named parts with their agents:
  - If the STOP 1 picks include a scam and trust section, `bsuk-scam-trust-agent` builds that section to the outline. It flags only a transfer made before any video call or visit to a seller who cannot be checked (Lisa q04).
  - If the board keeps the video section, `bsuk-video-seo-agent` writes its title, caption and `VideoObject` for id `settings.youtube_embeds[0]`, as a click-to-play facade unless the user picked otherwise.

  Wire each component as follows:
  - Each `BodyImage` sits directly after its H3 and before that block's prose, with `box="uniform"` (`box="tall"` for a portrait).
  - `CityFaqLedger` gets `items` equal to exactly the question file's picks for its block, with `q` as written on the page (update `covered_by.text` in `data/queries/blue-staffy-puppies-london.json` to match) and `a` taken only from the question's `bank:<id>` row or data key.
  - `schema` is `faqPageNode([...all visible rows])`, plus a `LocalBusiness` node with `areaServed` London and no `telephone` key.

- [ ] **Step 3: Refill the question file's covered_by**

  Run:

  ```bash
  python3 scripts/query_augment.py blue-staffy-puppies-london --page-type location --keyword "blue staffy puppies london" --route /uk-locations/blue-staffy-puppies-london/
  ```

  Expected: exit 0 with `dropped 0`.

- [ ] **Step 4: Run the tests**

  Run:

  ```bash
  npm run -s build
  python3 -m pytest tests/py/test_london_page.py tests/py/test_city_scaffold.py -q
  ```

  Expected: PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/pages/uk-locations/blue-staffy-puppies-london.astro data/queries/blue-staffy-puppies-london.json
  git commit -m "feat(london): the page written from its approved outline and board (row 12)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 28: Provenance, registration and the site gates

**Files:**
- Modify: `data/facts/rebuilt.json`, `tests/render/targets.json`

- [ ] **Step 1: Check provenance before registering**

  Run:

  ```bash
  npm run -s build
  python3 scripts/outline_provenance_check.py blue-staffy-puppies-london; echo "exit $?"
  ```

  Expected: exit 0, with no `outline-extra`, `outline-missing`, `outline-order`, `outline-heading-crossover`, `outline-copy-crossover` or `outline-sentence-crossover`. Fix any FAIL in the copy, never by widening the whitelist.

- [ ] **Step 2: Register the page**

  Append `"blue-staffy-puppies-london"` to the list in `data/facts/rebuilt.json`. Append this object to `pages` in `tests/render/targets.json`:

  ```json
  {"slug": "uk-locations/blue-staffy-puppies-london", "page_type": "location", "corpus": true}
  ```

- [ ] **Step 3: Run the site gates**

  Run:

  ```bash
  npm run -s build
  npm run -s check:all; echo "exit $?"
  python3 scripts/board_gate.py blue-staffy-puppies-london
  python3 scripts/keyword_metrics.py blue-staffy-puppies-london
  npm run -s test:py
  ```

  Expected: exit 0 on each. `check:queries` and `check:outline` now examine London (read their examined counts). `check:facts` examines London against the empty fact set.

  A FAIL is confirmed on `dist/uk-locations/blue-staffy-puppies-london/index.html` before anything is edited.

- [ ] **Step 4: Commit**

  ```bash
  git add data/facts/rebuilt.json tests/render/targets.json
  git commit -m "chore(london): registered as rebuilt; check:all green (row 12)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

## Phase I: Harden (rows 13–16)

### Task 29: Render gates (row 13)

**Files:**
- Create: `data/quality/scorecards/blue-staffy-puppies-london-${D}.json` (written by the run)

- [ ] **Step 1: Check the checkers first**

  Run:

  ```bash
  npm run test:render:meta
  ```

  Expected: PASS. A failure here means the harness is broken. Stop and report; trust no page result.

- [ ] **Step 2: Run the page renders**

  Run:

  ```bash
  npm run test:render:pages
  npm run test:render:city
  ```

  Expected: no blocking IMG, LAYOUT or NAV row, and no check that examined zero nodes. The four promoted checks pass on London:
  - `hero-counter-separation`;
  - `h3-image-first`;
  - `sem-section-opening-paragraph`;
  - `sem-title-case-headings`.

  `city-type-fit` passes. Fix in the page or its data, confirming each defect on the built page first.

- [ ] **Step 3: Commit**

  ```bash
  git add data/quality/scorecards/ src/pages/uk-locations/blue-staffy-puppies-london.astro
  git commit -m "test(london): render gates at 375/768/1280, scorecard (row 13)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 30 (CONTROLLER invokes the skill): Harden, the impeccable pass (row 14)

**Files:**
- Modify: `src/pages/uk-locations/blue-staffy-puppies-london.astro` and the kit components it uses, only for fixes that change no content and no palette
- Modify: `data/page-runs/blue-staffy-puppies-london.json`

- [ ] **Step 1: Run the pass**

  Invoke the Skill tool with `impeccable:impeccable` on the built page, `http://localhost:4321/uk-locations/blue-staffy-puppies-london/`. The worktree has no `.claude/launch.json` yet, so create one first with a single configuration, `{"name": "bsuk-preview", "runtimeExecutable": "npx", "runtimeArgs": ["astro", "preview", "--port", "4321"], "port": 4321}`. Start it with the Browser pane's `preview_start` (name `bsuk-preview`), never a background shell job. Judge the page at 375, 768 and 1280 in a painting browser: the Playwright MCP or the Browser pane, with screenshots taken section by section.

  Apply the user's type rule: every heading, paragraph and label sized per tier, no chunky headings, and no tall sections or uneven paragraphs.

- [ ] **Step 2: Fix or defer each finding**

  Commit each fix that is not a visual redesign.

  A proposed visual change is written as a preview under `docs/superpowers/sessions/${D}-london-impeccable-preview/` and not applied. Log it under Open Flags and record it `--deferred "<reason>"`.

- [ ] **Step 3: Record the pass**

  Run:

  ```bash
  python3 scripts/page_run_record.py blue-staffy-puppies-london impeccable --findings <n> --fixed <n> [--deferred "<reason>" ...]
  ```

  Expected: exit 0.

- [ ] **Step 4: Commit**

  ```bash
  git add data/page-runs/blue-staffy-puppies-london.json
  git commit -m "chore(london): impeccable pass recorded (row 14)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

### Task 31 (CONTROLLER invokes the skill): Harden, the frontend-design pass (row 15)

**Files:**
- Modify: as Task 30, and `data/page-runs/blue-staffy-puppies-london.json`

- [ ] **Step 1: Run the pass**

  Invoke the Skill tool with `frontend-design:frontend-design` the same way, at 375, 768 and 1280, in a painting browser. Fixes are committed. A visual change is a deferred preview. The palette never changes.

- [ ] **Step 2: Record the pass**

  Run:

  ```bash
  python3 scripts/page_run_record.py blue-staffy-puppies-london frontend-design --findings <n> --fixed <n>
  ```

  Expected: exit 0.

- [ ] **Step 3: Commit**

  Use the message `chore(london): frontend-design pass recorded (row 15)` with the trailer. From here on, any page edit stales this pass and it must be re-run.

### Task 32: The static scan and visual intelligence (row 16)

**Files:**
- Create: `docs/superpowers/sessions/${D}-visual-intel-blue-staffy-puppies-london.md`

- [ ] **Step 1: Run the static scan**

  Run:

  ```bash
  python3 scripts/page_hardening_scan.py uk-locations/blue-staffy-puppies-london --fail-on-error; echo "exit $?"
  ```

  Expected: exit 0, with 0 ERROR. Triage every WARN in the task report as real, dead code or a false positive.

- [ ] **Step 2: Run the visual-intelligence report**

  Invoke `bsuk-visual-intelligence` (Skill tool, or `.claude/skills/bsuk-visual-intelligence/SKILL.md`) on the built page against every sibling in the location cluster that `tests/render/targets.json` lists:
  - `uk-locations/blue-staffy-puppies-birmingham`;
  - `uk-locations/blue-staffy-puppies-uk`.

  Write the report to `docs/superpowers/sessions/${D}-visual-intel-blue-staffy-puppies-london.md`. It carries the verdict, every score's source, every finding's owner, the verbalization table and the predicate inventory (the row 20 input). A proposed visual change is a preview, as in rows 14 and 15.

- [ ] **Step 3: Commit**

  ```bash
  git add docs/superpowers/sessions/${D}-visual-intel-blue-staffy-puppies-london.md
  git commit -m "docs(london): static scan clean; visual-intelligence report (row 16)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

## Phase J: Gates, verification and close (rows 17–21)

### Task 33: Every gate twice (row 17)

**Files:** none tracked. `docs/reports/gate-page/blue-staffy-puppies-london.json` is git-ignored.

- [ ] **Step 1: Confirm the tree is committed**

  Run:

  ```bash
  git status --short
  ```

  Expected: no modified tracked file except `public/search-index.json` or a current `data/page-dates.json`.

- [ ] **Step 2: Run the gates**

  Run:

  ```bash
  npm run -s build
  npm run gate:page -- blue-staffy-puppies-london --skip-record; echo "exit $?"
  python3 scripts/quality_report.py
  python3 scripts/perf_audit.py uk-locations/blue-staffy-puppies-london
  ```

  Expected:
  - `gate:page` exits 0, with both runs identical: dup (body and `--headers`), `final_page_audit` `--type location`, hardening, AEO, evidence (`--fail-on-error`: an unledgered health claim is an ERROR) and `board_gate`, each twice. The `listed` step passes.
  - `quality_report.py` §5 is read.
  - `perf_audit.py` reports the warm median of runs 2–5 on `dist/`. Do not use `--live`: it refuses on the placeholder.

  Any FAIL is confirmed on the page, fixed, committed, and then Tasks 30–31 are re-run, because the page changed after frontend-design.

### Task 34: Verification before completion (row 18)

**Files:**
- Modify: `data/page-runs/blue-staffy-puppies-london.json`

- [ ] **Step 1: Invoke the skill**

  Invoke the Skill tool with `superpowers:verification-before-completion`.

- [ ] **Step 2: Record the verification**

  With the tree committed, run:

  ```bash
  python3 scripts/page_run_record.py blue-staffy-puppies-london verification \
    --run "npm run -s build" --run "npm run -s check:all" \
    --run "npm run gate:page -- blue-staffy-puppies-london --skip-record" \
    --claim "London passes every page gate twice, built from its approved outline and board"
  ```

  Expected: exit 0, with each command's exit code 0 and an examined count above 0.

- [ ] **Step 3: Commit and run the full gate**

  ```bash
  git add data/page-runs/blue-staffy-puppies-london.json
  git commit -m "chore(london): verification-before-completion recorded (row 18)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  npm run gate:page -- blue-staffy-puppies-london; echo "exit $?"
  ```

  Expected: exit 0. The full gate re-runs `check:all` itself and checks the run record.

### Task 35: The measurement ledger and LLM visibility (rows 19–20)

**Files:**
- Create: `docs/reports/p5-london-gate-table.md` (git-ignored under `docs/reports/`; its table is pasted into the gate report in Task 36)

- [ ] **Step 1: Run the ledger**

  Run:

  ```bash
  python3 scripts/measurement_ledger.py p5 --slugs blue-staffy-puppies-london --md docs/reports/p5-london-gate-table.md
  python3 scripts/measurement_ledger.py p5 --require-pages; echo "exit $?"
  ```

  Expected:
  - M1–M3, M6, M8–M10, M12, M13 and M18 are printed as numbers.
  - `--require-pages` exits 0, with no FAIL or STALE on M1, M2, M6, M8 or M10.
  - A STALE M6 means the scorecard is older than the page: re-run Task 29.
  - A STALE M8 means re-gate at HEAD (Task 33).

- [ ] **Step 2: Check LLM visibility**

  Run:

  ```bash
  python3 scripts/aeo_audit.py uk-locations/blue-staffy-puppies-london --fail-on-error; echo "exit $?"
  ```

  Expected: exit 0.

  Read it with the Task 32 report and Task 11's intel file. The fetched denominator is 1 of 1 (ChatGPT, 2026-09-25). `bsuk_cited` is `false` (the page is not live). List the engine terms the page still lacks for the gate report.

### Task 36: The close (row 21)

**Files:**
- Modify: `docs/superpowers/sessions/2026-09-30-session-brief.md` (`## What's Next`), `docs/reference/session-log.md` (Known Issues)
- Create: the gate report `docs/reports/p5-london-gate-report.md` (published) and `docs/artifacts/reports/p5-london-gate-report.html` (the versioned Artifact source)

- [ ] **Step 1: Run the close in its fixed order, with no rebuild after gating**

  Run:

  ```bash
  npm run -s build
  npm run test:render:pages
  python3 -c "import json;[print(s) for s in json.load(open('data/facts/rebuilt.json'))]" | while read s; do npm run -s gate:page -- "$s" || echo "GATE FAIL $s"; done
  python3 scripts/rendered_changes.py --base $(git merge-base HEAD foundation) --json
  python3 scripts/measurement_ledger.py p5 --require-pages
  ```

  Expected: no `GATE FAIL` line. `rendered_changes` lists `blue-staffy-puppies-london` among the changed slugs. The ledger exits 0.

- [ ] **Step 2: Verify again before any PASS claim**

  Invoke `superpowers:verification-before-completion` again before the gate report says PASS.

- [ ] **Step 3: Close the session**

  Invoke `session-closer`. Update the brief's `## What's Next` and the Known Issues, recording what could not be done and why (this plan's "What London cannot do yet").

- [ ] **Step 4: Publish the gate report**

  Write the gate report with a copy button per section and a `.md` download. It carries:
  - the ledger table;
  - each gate's two runs;
  - every `NOT FETCHED` with its barrier;
  - the deferred Harden previews;
  - the open flags.

  Publish it as an Artifact, icon `check`.

- [ ] **Step 5: Commit**

  ```bash
  git add docs/superpowers/sessions/2026-09-30-session-brief.md docs/reference/session-log.md docs/artifacts/reports/ public/search-index.json data/page-dates.json
  git commit -m "docs(london): page-run close — gate report, ledger, Known Issues (row 21)

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

  Never push.

### Task 37 (CONTROLLER): The user approves or fails the page; noindex comes off only on approval

**Files:**
- Modify: `src/pages/uk-locations/blue-staffy-puppies-london.astro` (robots), `tests/py/test_london_page.py`, `tests/py/test_city_scaffold.py`

- [ ] **Step 1: Ask one either/or question in chat**

  > "London is built and passes every gate twice (gate report: <URL>). Approve it to come out of noindex, or fail it with what to change?"

  End the turn and wait.

- [ ] **Step 2: On a fail**

  Log each point under Open Flags. The fixes re-enter at the row they belong to: copy at Task 27, which re-runs Tasks 28–36, and a visual change goes through a preview first.

- [ ] **Step 3: On approval, update the tests first and see them fail**

  In `tests/py/test_london_page.py`, replace `test_noindex_until_the_user_approves_the_page` with:

  ```python
  def test_london_is_indexable_and_in_the_sitemap():
      html = built()
      assert not re.search(r'<meta name="robots" content="noindex', html)
      shards = [s.read_text(encoding="utf-8") for s in (ROOT / "dist").glob("*sitemap*.xml")]
      assert any("/uk-locations/blue-staffy-puppies-london/" in s for s in shards)
  ```

  In `tests/py/test_city_scaffold.py`, delete `test_the_scaffold_is_noindex_and_in_no_sitemap`: London is no longer a scaffold, and `test_every_scaffold_is_noindex_and_in_no_sitemap` still guards any future one.

  Then run:

  ```bash
  npm run -s build
  python3 -m pytest tests/py/test_london_page.py -q
  ```

  Expected: FAIL on `test_london_is_indexable_and_in_the_sitemap`.

- [ ] **Step 4: Flip the robots value**

  In the page, change `robots="noindex, follow"` to `robots="index, follow, max-snippet:-1, max-video-preview:-1, max-image-preview:large"`. Update the file-top comment's "KEPT OUT OF THE INDEX" paragraph to say the user approved the page on `<D>`.

  Run:

  ```bash
  npm run -s build
  python3 -m pytest tests/py/test_london_page.py tests/py/test_city_scaffold.py -q
  npm run -s check:sitemaps
  ```

  Expected: PASS, and exit 0.

- [ ] **Step 5: Commit, then re-run the close**

  ```bash
  git add src/pages/uk-locations/blue-staffy-puppies-london.astro tests/py/test_london_page.py tests/py/test_city_scaffold.py
  git commit -m "feat(london): out of noindex on the user's approval

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

  The page changed after frontend-design, so re-run Tasks 30–31 (the passes re-record), then Tasks 33–36 in order. Never push. Do not merge into `foundation` until the user says so.
