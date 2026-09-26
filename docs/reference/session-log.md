# BlueStaffyUK Session Log and Known Issues

History and open defects. Nothing here is a rule; it is state. The source repo's log was
replaced wholesale rather than re-based — it was eighteen months of another site's build
history, and translating it would have invented a past this repo does not have.

## Project 1 — Foundation (2026-09-15/16) — COMPLETE

The Astro 6.3.8 static site, the rule packs, the Python suite and the render harness.
Full report and evidence: `docs/reports/foundation-gate-report.md`.

## Project 2 — System transfer (2026-09-16/17) — COMPLETE

Moves the site operating system — rules, agents, skills, gate scripts and reference docs —
from the source repo into this one, re-based onto a Carlisle Staffordshire Bull
Terrier breeder, with `scripts/marker_check.py` as the zero-tolerance
proof. `data/port-manifest.json` is the record of every file that crossed.
Plan: `docs/superpowers/plans/2026-09-16-system-transfer.md`.

Closed 2026-09-17 on branch `system-transfer`, 57 commits, `6c1f2c3..939033b` plus the
close-out commit, no remote and nothing pushed. Every gate was run twice with identical
results; the transcript is `docs/reports/system-transfer-run.log`. Full report and evidence:
`docs/reports/system-transfer-gate-report.md`.

Headline numbers: the marker gate went 418 → 0 (`examined 233 files; 0 problems`); the
manifest carries 180 rows (10 copy, 129 rebase, 41 deferred) and `scripts/port_from_cag.py` reports
`missing 0, blocked 0` with no rebase row re-applied on the second run; 36 agents and 53
skills in the single `.claude` tree with both registries generated and in sync; 1240 pytest
tests pass; the render meta gate is at 315 passed and the pages gate at the recorded Project
2 baseline with no new blocking row.

Credentials moved out of the MCP server and into a gitignored `.env` holding eleven keys by
name (values never printed, never committed). The `bluestaffyuk` MCP block was removed from
the Claude desktop config, which was backed up first as
`claude_desktop_config.json.bak-20260917-022840`; `~/bsuk-mcp-server` was deleted. Only
`gscServer` remains.

## Project 3 — Design system (2026-09-18/19) — COMPLETE

Gives the site a visual system of its own: a three-layer token file, the L1 badge mark and
its four lockups, and a thirteen-component kit picked by the user from five variants each on
a published design canvas. Nothing of the kit is mounted on a real page yet except the shell
— project 4 does that — so the site's content gates are unchanged by design.
Plan: `docs/superpowers/plans/2026-09-18-design-system.md`.
Spec: `docs/superpowers/specs/2026-09-18-design-system-design.md`, approved and amended seven
times during execution; §11 is where every in-flight decision is recorded.

Closed 2026-09-19 on branch `design-system`, 61 commits from `e049f55` including the
close-out, the working-rule-11 commit and the close-out review's fixes, no remote and nothing
pushed. Every gate was run twice with identical results; the transcript is
`docs/reports/design-system-run.log`, and the two halves are proven identical as multisets of
time-normalised lines. Full report and evidence:
`docs/reports/design-system-gate-report.md`.

Headline numbers: 51 pages built; 66 design tokens with 20 contrast pairs asserted at AA;
thirteen kit components and thirteen owner picks; the canvas went 65 → 91 → 39 boards as the
mobile and tablet rows arrived and the losing variants were pruned; the `/design-canvas/`
route was replaced by `/kit-preview/`, which is a measured target page rather than a hidden
one; 1353 pytest tests pass; the render meta gate is at 324 passed with the three formerly
deferred checks promoted and no `DEFERRED` line; the pages gate is at the recorded project 3
baseline, `8 passed, 46 failed`, with blocking rows 67 → 58 and no new blocking row anywhere.
The fall is the image pass: `img-srcset-within-2x` went from 15 rows to 6, and the puppy
page's Lighthouse Performance rose 98 → 100 with LCP 2277 ms → 1516 ms. No Lighthouse category
score fell on any of the five page types. The placeholder total fell 1698 → 1605.

A correction to an in-flight report: during Task 16 the controller reported the pages gate as
"0 failed". That was a stale-scorecard artefact. The true figure is 46 failing pages,
unchanged from project 2.

Three Artifacts were published and their URLs recorded in `data/design/artifacts.json`: the
design canvas, the picks board, and the Design System — the last replacing the spec's original
draft of a prompt pack, because the artifact type's own format is a token-and-component
document rather than a set of prompts.

## Project 4 — Page rebuilds (2026-09-19/22) — COMPLETE

Rebuilds every rich page on the project 3 kit, each written fresh from an approved outline
through its own page board, and fixes the facts the migration carried wrong.
Plan: `docs/superpowers/plans/2026-09-19-page-rebuilds.md`.
Spec: `docs/superpowers/specs/2026-09-19-page-rebuilds-design.md`, amended eleven times during
execution; §9 is where every in-flight decision is recorded.

Closed 2026-09-22 on branch `page-rebuilds`, cut from `foundation` at `63a7b12`, 120 commits
including step 0 (`f94baee`, the video copy that described silent puppy clips as a voice, a
tour and a guide) and the close-out, merged into `foundation` with `--no-ff`; no remote and
nothing pushed. Every gate was run twice; the transcript is
`docs/reports/page-rebuilds-run.log`. One line drifted between the runs — pytest's two
real-scorecard baseline tests skip until `docs/reports/render-baseline-project4.md` has a generated block,
and run 1's pytest ran before run 1 filled it — and the cause is removed by committing the
filled block. Full report and evidence: `docs/reports/page-rebuilds-gate-report.md`.

Headline numbers: twelve pages rebuilt from twelve approved boards (URLs in
`data/design/artifacts.json` `boards`); five new kit components (dial, sheet, strip, data table,
video embed — eighteen in all), the first three on every rebuilt page and the three hubs; rule
15's verbatim set carried on nine pages, 507 elements, 181 changed with reasons, 0 missing;
the review-slot stand-in at 0 — every review slot filled from the three real reviews; render blocking
rows **58 → 6**, none on a rebuilt page (the six are Known Issue 31's two routes);
`schema-date-modified-present` 18 → 0; `img-srcset-within-2x` 6 → 0; `scripts/final_page_audit.py`
12 FAIL → 0 FAIL; AEO 38 baseline-only FAIL pages → 0; pytest 1355 → 1703 passed; render meta
324 → 370 passed. Lighthouse (warm median of 3, mobile and desktop, fourteen pages): 100 in all five categories everywhere except the thank-you page's SEO 69 (`noindex` by design), the breed guide's Best Practices 96 (Known Issue 38), the location route's SEO 92 (migrated link text) and three mobile Performance 99s — the blog hub's, the one fall against project 3, is TBT variance. Working rules 12–16 were given during the build; rules 10–11 (project 3's
close) were applied to real pages for the first time.

Definition of done: 4 PASS, 1 PASS-WITH-DEVIATION, 1 DEVIATION (the trailer, Known Issue 37),
1 FAIL (partial) — the former city is gone from every rebuilt page, settings, schema and the
form, but not from the puppy and location pages this build gave the shell only (Known Issue 16,
build 5). **Next: project 5 — the 28 location pages, the comparison cluster and the two new
blog posts.**

## Query augmentation bridge build (2026-09-23) — COMPLETE

A bridge build between project 4 and project 5 that closes Known Issue 17: a question step
every page builder runs first. `.claude/skills/bsuk-query-augmentation/SKILL.md` drives the
sources (DataForSEO through the connector, a free Bing read, `data/faq.json`, and Reddit
threads via `.claude/skills/bsuk-reddit-threads/SKILL.md`); `scripts/query_augment.py`
merges, scores, caps spend and writes the page's question file under `data/queries/`;
`scripts/query_coverage_check.py` gates the built page in `npm run check:all`. The Illinois
city template is converted to `docs/reference/location-page-template.md`, and the location,
comparison, blog and puppy builders call the skill first.
Plan: `docs/superpowers/plans/2026-09-23-query-augmentation.md`.
Spec: `docs/superpowers/specs/2026-09-23-query-augmentation-design.md`, amended 21 times
during execution; §14 is where every in-flight decision is recorded.

Closed 2026-09-23 on branch `query-augmentation`, cut from `foundation` at `db37ca1`, 61
commits `1f655fd..24d9dc4` plus the close-out, every one with the Fable 5.1 trailer; no remote
and nothing pushed. The whole-branch review was approved. `npm run build && npm run test:py &&
npm run check:all` ran twice with identical counts, both exit 0. Full report and evidence:
`docs/reports/query-augmentation-gate-report.md`.

Headline numbers: pytest 1703 → 2071 passed; the new gate prints `examined 0 pages (0 not
built, 2 awaiting rebuild); 0 problems` — the Manchester and Leeds question files wait for
their project 5 rebuild; marker gate `examined 260 files; 0 problems`; 57 skills in the
regenerated registry. The Manchester pilot made three paid calls (Google and ChatGPT usable,
Bing off-topic and replaced by a free browser read), logged at a conservative $0.20 of the $1
because the connector returns no cost; every ranking page was a marketplace or directory with
no real sections, so the target is 9 via the floor. Leeds ran on free sources only, $0. Both
files carry 20 FAQ picks, all fact-backed.

User rulings: marketplaces and directories count; the section floor is 9; one AI engine per
page; Task 10 fixes only what this build broke; competitor intelligence is its own build.
Definition of done: 1 PASS, 12 PASS-WITH-DEVIATION (each an amendment in §14), 0 FAIL. Open
items are Known Issues 39–46. **Next: project 5 — location, comparison and blog pages.** It
starts with brainstorming; the nested-route prerequisite (Known Issue 39) comes first, and each
page begins with `/bsuk-query-augmentation`.

## Competitor intelligence bridge build (2026-09-23) — COMPLETE

A bridge build that closes Known Issue 42: a national competitor registry, per-competitor intel
reports with a BSUK profile, a script-built gap matrix, a keyword-gap list, LLM citation intel
and a two-strategy synthesis, every count built by a script and every paid call behind the spend guard.
Five agents under `.claude/agents/` (bsuk-competitor-registry, bsuk-competitor-intel,
bsuk-competitive-keyword-gap-agent, bsuk-llm-keyword-intel, bsuk-strategy-synthesizer) and three scripts (`scripts/competitor_registry_check.py`,
`scripts/gap_matrix.py`, `scripts/strategy_cite_check.py`; `check:competitors` and `check:gaps`
in `check:all`). Plan `docs/superpowers/plans/2026-09-23-competitor-intel.md`; spec
`docs/superpowers/specs/2026-09-23-competitor-intel-design.md`, amended 19 times during
execution (§16).

Closed 2026-09-23 on branch `competitor-intel` (cut from `foundation` at `db37ca1`, rebased onto
`c9c981c`): 49 commits `a116055..638a6d4`, then the close-out fix `7ece4ff` and its docs commit,
every one with the Fable 5.1 trailer; no remote, nothing pushed. Merged `--no-ff` into `foundation`
at `dcf1f9a` (gate report `docs/reports/competitor-intel-gate-report.md`). `python3 -m pytest tests/py -q` → 2375 passed, 27
skipped, 1 xfailed; `npm run -s check:all` exit 0 (`competitors: 21 entries; 1 banned domain; 83
files scanned; 0 problems`, `gaps: gap-matrix-2026-09-23.md matches 4 reports (3 competitors, BSUK
profile present)`, `examined 41 agents; 0 problems`).

Pilot (user-approved): ten registry seeds → 21 sites approved (tiers 1: 5 · 2: 12 · 3: 2 · 4: 1 ·
5: 1); intel on trojanstaffuk, pets4homes and rspca plus the BSUK profile (20 Firecrawl credits);
gap matrix — BSUK lacks care-guide (2/3, high), faq, price and reviews (1/3, medium); keyword gaps
— 4 high; LLM intel for Manchester (cached, condensed save) and Leeds (paid) — BSUK cited by
neither; strategy for the 28 location pages — pick A, contested stubs first (cite-check 12
sources, 36 figures, 0 problems). Spend log $0.80 of the $1.00 cap, all estimates; the dashboard
read $0.99185 before the pilot. User ruling A set `query_typical_call_usd` to 0.05. Open items:
Known Issues 47–58. **Next: project 5** — starting with the strategy's first three stub
rebuilds (Manchester, the licensed-breeder page, Leeds), after Known Issue 39.

## System gaps bridge build (2026-09-24) — COMPLETE

Branch `system-gaps` (worktree `/Users/apple/Downloads/BSUK-gaps`), cut from `foundation` at `9927710`, merged `--no-ff` into `foundation` at `06dee26`. It ran beside `p5-readiness`, which another session was executing, and merged first. Plan: `docs/superpowers/plans/2026-09-24-system-gaps.md` (Artifact https://claude.ai/artifact/FS2ekGxx7jAM5T8poem95R). Gate report: `docs/reports/system-gaps-gate-report.md` (Artifact https://claude.ai/artifact/VFCVy6avEXQ7gGKVcD2mae).

What it closed (the user's five gaps, new location/comparison/blog pages only; the twelve built pages are frozen out by name in `scripts/family_rules.py`):
- **Board entity and keyword view.** One card per entity, grouped by class, with a sticky filter and search and a phone-stacking matrix; the graph is removed. Keyword chips are grouped by type (`scripts/board_entities.py`).
- **Keyword variation, related, co-occurring and similar types**, plus `scripts/keyword_variants.py`, which proposes them free from cached data. The ontology is seeded from sourced data: 7 → 56 entities in 8 classes (`scripts/ontology_seed.py`).
- **Outline provenance.** `scripts/outline_provenance_check.py` (`check:outline` in `check:all`) and `outline-heading-repeat`.
- **External links:** ≥6 on 6 domains from 4 source types. **Anchor types:** varied, and never reused across boards (`scripts/link_diversity.py`, `scripts/link_library.py`).
- **Images.** `IMAGE-DESIGNS.md` (OG styles A–H, IG-1..5, two-pass sha12 approval). `scripts/image_candidates.py` ranks the page's own images, then served images, then `Assets/Images`. `scripts/image_rules.py` requires a slot per body H2/H3 and the hero, and runs the build gate. `scripts/reframe_og.py` and `scripts/ingest_image.py`. Three image skills ported. Board block 7 "Images & styles".
- **Rules answered before approval.** Board block 7b lists every rule as approval will see it, and `scripts/board_approve.py` refuses approval and re-approval while one FAILs (build-gate image checks excepted).
- **Wiring.** CLAUDE.md working rule 17, WORKFLOW rule 13, the builder skills' "Project 5 page rules (system-gaps)" block. `GEMINI_API_KEY` is documented by name, and `google-genai==1.47.0` is pinned.

Known Issues 59–69 are left for the numbers the `p5-readiness` plan already uses; this build's start at 70.

### Merge guide for `p5-readiness` (whichever merges second)
A trial merge showed 7 textual conflicts across 14 shared files:
- `package.json` and `tests/py/test_package_scripts.py`: keep both `check:outline` and `check:workflow`.
- `docs/reference/system-registry.md`: regenerate it.
- `.claude/skills/bsuk-comparison-page-builder/SKILL.md`: keep p5-readiness's rewritten list, then this build's appended blocks.
- `docs/reference/WORKFLOW.md`: p5-readiness moved rules 10–12, so rule 13 follows them.
- `.claude/agents/bsuk-image-pipeline.md`: keep p5-readiness's rules banner.
- `.claude/agents/bsuk-infographic-builder.md`: drop the "not ported" notes on `bsuk-infographic`, because that skill is ported now.

After resolving, fix three tests on the merged tree:
- Remove `"IMAGE-DESIGNS.md": "rules/images.md"` from the REPLACED map in `tests/py/test_agent_references.py` (arrives in the p5-readiness merge), since the file exists now.
- Add a `check:outline` row to the gate table in `scripts/build_system_registry.py`.
- Keep the rules banner line in `.claude/agents/bsuk-image-pipeline.md`.

When p5-readiness Task 43 (F2a) adds `_slugs.resolve_page`, `scripts/page_sections.py` uses it automatically.

## Project 5 readiness build (2026-09-23/2026-09-25) — COMPLETE

A readiness pass between the competitor intelligence build and project 5, run because the user asked
that everything built so far be checked as registered and working before a page is built ("check if
everything was done well right up to the start of project 5, if all the agents, skills, rules,
workflow, board, sprints etc are registered and are all working well"). Five phases on one branch:
the instruction harness (CLAUDE.md, WORKFLOW's seven sprints, the quick-start, the system registry,
the port manifest, 57 skills and 41 agents, with guards so none of it drifts again: `check:workflow`
in `check:all`, one dead-root path guard across agents, skills and commands, a residue lint for
skills and commands, a marker gate that reads a line break); small site fixes (search titles, the
relocated city on the puppy pages, the counter dot's contrast, the puppy hub's headings, the contact
board preview); the research tools (Known Issues 47–53), the nested city routes (39) and the spend
guard's dashboard reconciliation (45); the user's rulings R3–R14 (self-hosted fonts, rule-index rows,
the breeder's question sheet, the banned-breed line, the video facade, the homepage mosaic, three
guide heroes, rule 16's gate with the utility pages exempt); and the research the user made
mandatory before any page is built — competitor intel on all 21 registry entries, the BSUK profile
and gap matrix, the keyword gap, AI-answer intel for the other 26 location pages and a re-synthesised
strategy. Plan `docs/superpowers/plans/2026-09-24-p5-readiness.md` (committed as the branch's first
commit, with an Executed note added at close-out); gate report
`docs/reports/p5-readiness-gate-report.md`; the breeder's question sheet
`docs/reference/questions-for-lisa.md`.

Closed on branch `p5-readiness`, cut from `foundation` at `9927710`: 171 commits
`845e4c0..707f319`, then the close-out's docs commits (`e7c7aaf`, `1305cec`); then `foundation` (the
system gaps build's 59 commits) was merged into the branch at `c7c41be`, followed by `dd34099`,
`7f9235b` and the docs commit that records it — 177 commits of the branch's own and the 59 brought
in, every one with the Fable 5.1 trailer (176 of 176 own and 59 of 59 counted before that docs
commit); no remote, nothing pushed. After that merge the suite read `5168 passed, 1 skipped,
1 xfailed` and `npm run -s check:all` exited 0, on both runs. Merged `--no-ff` into
`foundation` at `b76595e`. Run twice with identical counts:
`python3 -m pytest tests/py -q` → `4539 passed, 1 skipped, 1 xfailed, 152 warnings`;
`npm run -s check:all` exit 0; `npm run -s registry`, `npm run -s agents` and
`npm run -s baseline` `0 problems`.

Headline numbers: pytest 2388 → 4539 passed and 14 → 1 skipped (3811 after the instruction
harness, 3819 after the site fixes, 4105 after the spend guard's first task, 4366 after the review
minors, 4415 at the end of the rulings, 4539 after the intel classifier's rework in Phase 4; the 13
skips that went are duplicate-whitelist cases now left out when the tests are collected);
`check:workflow` `workflow-ref-check: examined 224 references in 2 files; 0 problems` (it read
215 references and 45 problems before Task C1); marker gate 265 → 266 files; placeholders 1732 at
the build's first `check:all` → 1434 (advisory; the count moves with the build; the last 2 are this
close-out's new Known Issues quoting two placeholder tokens); every rebuilt hero measured with Fraunces and Source
Sans 3 loaded. Research: 21 competitor reports and the BSUK profile; the gap matrix on all 21 has no
high row, and its queue starts with Person and SearchAction schema (5/20 each) and the care-guide,
faq, price and reviews page types (4/19 each), all six medium; the keyword gap finds 16 gaps, 10
high and 6 medium, from 20 reports (petsforlove could not be read); AI-answer intel now covers all
28 location pages (29 files — Manchester's re-buy sits beside its first answer), and none cites
BSUK; the re-synthesised strategy keeps Strategy A, contested city pages first, and its first three
steps rebuild the London, Manchester and Liverpool stubs (cite check: 48 sources, 78 figures, 0
problems). Spend: 27 DataForSEO calls in this build (the 26 other location pages and the Manchester
re-buy), logged at the $0.01 estimate each ($0.27; about $0.004 a call real); `python3
scripts/query_augment.py --budget ai_engines` counts $0.30215 of the $1.00 cap, with 69 more calls
fitting; the dashboard read $0.96785 before Phase 4, re-recorded for 2026-09-25 (`c13a807`);
Firecrawl 110 credits, 776 → 666.

User rulings (2026-09-23/24): lower the per-call estimate, not the cap (R1); competitor analysis
before any page (R2); self-host the fonts (R3); re-buy Manchester's AI answer (R4); rule-index rows
for rules 10–16 (R5); publish the breeder's question sheet (R6); city pages may state the
banned-breed line (R7); the S3 facade (R8); the counter dot steel (R9); keep `Button.kind`'s five
(R10); complete the homepage mosaic (R11); exempt the utility pages from rule 16 (R12); new guide
heroes (R13 — answered health H-GD1, breed guide H-GD3 with the S3 video, buying guide H-GD2 with
its counter C-GD2); `uploadDate` to project 6 (R14). At the one visual pause (2026-09-24) the user
kept homepage photos 1–4, the beside/below layout and photo 1's alt text, and agreed that the about
page's aside label goes. The Fraunces file question was not asked: mobile Performance stayed at 95
or more with the optical-size file.

Deviations from the plan, each recorded in the gate report as PASS-WITH-DEVIATION: the buying
guide's H-GD2 hero carries its chips (a controller amendment to Task R13; measured 411 at 1280);
two board saves at the pause were wrong — the browser restored an earlier form choice, so the health
board first saved H-GD3 and the buying board C-GD3 — and both were re-approved (Known Issue 66);
Task R12 gained two follow-ups, a rule-16 check at approval time (`876d65d`) and a refusal for a
re-boarded page that re-picks the arrangement it left (`94ad7f3`); Task X3 gained one (`c2d888e`);
a review-minors task (13 commits, `37e8ff3..7b153e5`) and a pre-G1 fix task (`a1aedcf`, `335f621`,
`f1eb5d2`) ran between the rulings and the research; in G1 the key-page classifier was reworked
mid-run (`4e2fe7f` to `9d7e7b9`), the per-entry credit ceiling went from 7 to 8 (a search map when the
first map misses the breed) and G1's ceiling from 141 to 161, and 110 credits were spent; a
consistency pass re-typed six reports for free (`8670a98`) and topped up six (`ca0c730`); the
dashboard reading was re-recorded for 2026-09-25 before G4 (`c13a807`); the intel agent's mobile
check uses the page's `clientWidth` against `screen.width`, with proof that a phone was emulated,
in place of the plan's `scrollWidth` against `innerWidth` (a controller amendment at Task E4); and
some of the plan's expected counts were stale (Task R13 Step 13's "342 passed" is 329, 334 with the
added tests; Task R11 Step 10's "20 WARN" is 18 on a fresh build). The plan stayed at its committed
path rather than the new dated copy the close-out task names.

Open items: Known Issues 59–69 and 75–80 (new; 70–74 are the system gaps build's), and still open 3, 5, 6, 7, 10, 13–16, 18, 23, 26, 27
(project 6), 30 (the breed guide's zero headroom), 31 (second half), 33 (the utility mosaics), 34,
36, 41, 43, 44, 53 (two items), 54, 55. Known Issue 15 — rotate the Google Cloud OAuth client and
scrub the source repo — is still the user's to do. **Flag for the user now:** Known Issue 65, the
older indexable location pages still print retired terms. **Next: project 5** — the location
pages, the comparison cluster and the two blog posts, in the order the re-synthesised strategy
gives (London, Manchester and Liverpool stub rebuilds first), starting with Known Issues 60 and 61.

## Answer board tool build (2026-09-26) — COMPLETE

Branch `answer-board` (worktree `/Users/apple/Downloads/BSUK-answers`), cut from `foundation` at `e9b3c1b`. Spec: `docs/superpowers/specs/2026-09-26-answer-board-design.md` (Artifact https://claude.ai/artifact/53L9VZvUS3Q4UfnqyDAYWV). Plan: `docs/superpowers/plans/2026-09-26-answer-board.md`.

What it added:
- **One standing board, "Questions for You"** (`scripts/build_answer_board.py` → `docs/artifacts/bsuk-answer-board.html`). Every batch of questions for the user is posted there; the user answers in place (text, or a choice plus a note; Not yet / Skip on every question) and presses **Send to Claude Code** per batch. Layout A: sticky progress rail, wide question column, a top bar on phones.
- **Batches live in the board's `db`**, written by Claude with the ArtifactData tool from `scripts/answer_board_batch.py`'s JSON (sheet parser `scripts/answer_sheet.py`), so posting never republishes the page. Answers save one document per question with a browser draft as backup; Send writes a snapshot and sends a short note (a comment is capped at 4 KiB) naming it.
- **The rule:** CLAUDE.md "Questions for the user — the answer board"; the procedure is `docs/reference/answer-board/README.md`. Lisa's 21 questions are the first batch (`docs/reference/answer-board/batches/2026-09-24-questions-for-lisa-bright.json`).

## Known Issues

Seeded from the Foundation gate report's "Open items" 1–8 and extended by projects 2 and 3.
Items 1 and 2 are closed by project 2 and item 4 by project 3; 3 and 5–8 are carried forward
with their owning project; 9–14 are new from the system transfer, 15–16 were added after it,
17–26 are new from the design system, and 27–38 are new from the page rebuilds. Project 4
closed 8, 9, 11, 12, 20, 22, 25, 28 and 29. The query augmentation bridge build closed 17 and
added 39–46. The competitor intelligence bridge build closed 42 and added 47–58. The
project 5 readiness pass closed 19, 21, 24, 32, 35, 37, 38, 39, 45–52, 56, 57 and 58, the
first half of 31, the buying-guide half of 30, the homepage and sharing halves of 33, all but two
items of 53 and the instruction items of 40; corrected 23; moved 27 to project 6 and 16 on to its
location-page remainder; and added 59–69 and 75–80. The system gaps bridge build added 70–74.
Renumbered at the merge of `foundation` into `p5-readiness` (2026-09-25): the readiness pass first
numbered its items 59–75, and its 70–75 became 75–80 so the system gaps build keeps 70–74 (70 → 75,
71 → 76, 72 → 77, 73 → 78, 74 → 79, 75 → 80). Commit messages from before that merge cite the old
numbers.

1. **`FORM_ENDPOINT` contract — CLOSED by project 2.** The contact-page form contract was
   re-based onto this repo's own fields and endpoint env key. See
   `scripts/form_contract_audit.py` and `tests/render/checks/form.ts`.
2. **The DUP whitelist — CLOSED by project 2.** The duplicate-content whitelist was
   re-based onto this site's own built pages, together with the fixture that depends on
   its stems. See `scripts/dup_content_audit.py`.
3. **The orphan check is blinded by the catch-all route.** `builtRoutesWithoutSource()` in
   `tests/render/lib/freshness.ts` compares built routes to source routes, and the
   root-level `src/pages/[...post].astro` matches any path — so while it exists the
   function cannot prove any route orphaned, static pages included. The mtime comparison is
   the only remaining freshness signal. A real answer needs a check that reads the content
   collection rather than the filesystem. **Carried forward.**
4. **Puppy `srcset` 2x rows — CLOSED by project 3.** The puppy photos moved to `astro:assets`
   with a bounded `srcset`. `img-srcset-within-2x` fell from 15 blocking rows over 6 pages to
   **6 rows over 3 pages**, and the puppy page's Lighthouse LCP fell 2277 ms → 1516 ms with
   Performance 98 → 100 — the two numbers moved together, as Foundation predicted. The six
   remaining rows are two plain `<img>` tags in migrated WordPress body copy on three pages,
   named in `docs/reports/design-system-gate-report.md`; they are not kit output and belong
   to **project 4**'s content pass.
5. **`nav-jump-target-lands` baseline.** 18 rows over 6 pages remain after the shell fix.
   **2026-09-22 (project 4 close): 3 rows on 1 page** — the rebuilt pages carry none; what is
   left is `/uk-locations/blue-staffy-puppies-uk/`'s `#Staffy-adoption` (Known Issue 31). Build 5.
   `--hdr` is measured from the header (`--hdr-measured`), with the media query kept as the
   no-JS fallback, so the remaining rows are migrated in-page anchors rather than chrome
   miscalculation. **Carried forward.**
6. **17 stub locations are noindexed.** They carry 0–7 words of legacy body.
   **Project 5** writes them; `scripts/sitemap_check.py` keeps them out of the shards until
   then.
7. **Placeholders.** Five stand-in tokens are still in the tree. This entry describes them
   rather than naming them: `docs/reference` is itself a placeholder scan root, so spelling
   a token here would register as a permanent hit and the gate would never reach zero on
   launch day. The exact token names and counts are in
   `docs/reports/system-transfer-gate-report.md`, which is not a scan root.
   The site-URL stand-in and the phone stand-in resolve at **project 6** launch; the
   form-endpoint stand-in is already clear, because the build reads the endpoint from `.env`.
   The two legal-claim stand-ins — the breeder-licence claim and the Lucy's-Law claim — were
   added by project 2's skill re-base and await **Lisa Bright's** confirmation of the
   wording. `BSUK_RELEASE=1 npm run check:placeholders` refuses to ship any of them
   (exit 1, confirmed). While the phone stand-in is in `data/settings.json`,
   `scripts/final_page_audit.py` exempts `phone_in_footer` on every page with this entry as
   its printed reason (2026-09-22); the exemption reads the setting, so it lapses on its own
   the run after a real number lands.
8. **CLOSED 2026-09-22 (project 4) — `schema-date-modified-present` 18 → 0.** Was: 18 rows over 6 pages; needs
   `scripts/generate_page_dates.py` wired into the content pass, which arrives with
   **project 4** — the same project that gives pages a real edit history for sitemap
   `lastmod`.

9. **Three carried header duplicates. CLOSED 2026-09-20 (project 4 Task 18).**
   `board_gate.py index` reported three `header-collision` FAILs in migrated copy: the
   homepage's *Meet the Proud Parents of Our Blue Staffy Puppies* and *Our Commitment to the
   Health of Our Blue Staffy Puppies* against `/uk-locations/staffy-breeding-dogs-glasgow/`,
   and *How to Buy Your Blue Staffy Puppy* against `/uk-blue-staffy-puppy-buying-guide/`.
   All three are gone from the rebuilt homepage, each reworded under working rule 15 with its
   reason recorded in `data/boards/index.json` `verbatim.changed`: the first two keep every
   word up to the colliding five-word tail (*…of This Litter*, *…of Every Puppy We Raise*),
   and the third keeps the four words that carry the promise (*How to Buy Your Puppy, Step by
   Step*), because every nearer wording collided too. `board_gate.py index` is at **0 FAIL**
   against 50 live pages, header-collision 0.
10. **Deferred-check id drift.** `bottom-bar-under-tabbar` and `analytics-double-load` are
    Python page-hardening checks in the source repo, not render-harness checks, so they could
    not be deferred in `tests/render/targets.json`. Defer them if a later project ports them
    into the harness.
11. **CLOSED 2026-09-22 (project 4).** The old band is 0 times on every rebuilt page, listed in
    each record's `dropped.prices`. Was: **Old price range in migrated copy.** A pre-migration price band, below the locked
    £1,500 / £1,700, persists in several migrated page bodies (see the project-2 gate
    report, open item 11, for the exact pages). The fact lint covers `.claude/agents` and
    `.claude/skills` only; page bodies are content. **Project 4.**
12. **CLOSED 2026-09-22 (project 4).** The old byline is on no built page; it is in the
    homepage's and breeders page's `dropped.names`. Was: **`Sharine Amelia` byline.** The migrated author byline persists on the homepage and the
    breeders page. **Project 4.**
13. **`INDEXNOW_KEY` empty, `SITE_URL` still the placeholder.** IndexNow and pagefind are
    ported and guarded (`scripts/indexnow_submit.py` exits 2 without `BSUK_RELEASE=1` and again on
    the placeholder; `build:release` sits behind `scripts/release_guard.sh`). There is no
    deploy script — the source repo pushed to a host and this repo has none. **Project 6.**
14. **GSC and GA4 pulls are unwired.** The eight keys are in `.env` and named in
    `docs/reference/credentials.md`, but no script reads them yet. **Project 6.**

15. **Two live credential values were committed in this branch — ROTATION PENDING.**
    `.claude/skills/bsuk-indexing/SKILL.md` carried the live values of `GSC_CLIENT_SECRET`
    and `GA4_CLIENT_ID` inside an OAuth token-exchange example, from the skills re-base
    (`7a89519`) through the first close-out commit (`eed05a5`). The literals were replaced
    with `$GSC_CLIENT_SECRET` / `$GA4_CLIENT_ID` at the close-out, but they remain in this
    branch's git history. The branch has **no remote** and was never pushed; however the
    identical values are in the source repo's own indexing skill, which is tracked and
    pushed to its GitHub origin, so the OAuth client is exposed regardless of BSUK's local
    history.
    **Action required by the user: rotate the GSC OAuth client and the GA4 client in the
    Google Cloud Console — new client secret, refresh tokens re-minted — before project 6
    wires up the GSC and GA4 pulls.** No agent can do this. Two guards now prove the absence
    on every run: `tests/py/test_no_env_value_committed.py` (every `.env` value against all
    tracked files, the run log and the Artifacts) and `tests/py/test_secret_shapes.py`
    (credential shapes across the marker gate's roots plus reports, artifacts, scorecards and
    fixtures). Full account: `docs/reports/system-transfer-gate-report.md` § Credentials and
    MCP → Incident. **Open until rotated.** 2026-09-18: the source repo's working copy and
    its legacy skill file were scrubbed to env refs and committed locally (not pushed);
    rotation still pending.

16. **The breeder has relocated: Carlisle, Cumbria, England.** Confirmed by
    the user 2026-09-18 during the build 3 brainstorm, as a full relocation of the business
    and the website. Address is town-level only (Carlisle, Cumbria) until the breeder says
    otherwise. Everything that named the old city was wrong: the homepage and page
    copy, `data/settings.json`, the schema `address` / `areaServed`, the fact lint's locked
    geography in `tests/py/test_agent_facts.py`, agents and skills, and
    `/uk-locations/staffy-breeding-dogs-glasgow/`, which becomes an outreach page rather
    than the home base and keeps its URL. **Build 3** carried the new city in the logo
    lockups and tokens only; **build 5** re-plans the 28 locations around
    Carlisle (Cumbria, the Borders, the North West and North East are now the near ring).
    One strand of this debt was machine-readable and easy to miss: the form contract's
    `PUPPY_OPTION` constant in `scripts/form_contract_audit.py`, and the matching
    `<option>` value and visible label in `src/components/ContactForm.astro`, named the old
    city in a collection choice — so the gate *required* the wrong geography of
    every page it audited in full, and the shipped contact page offered a collection point
    the breeder had left.

    **Status 2026-09-19 (project 4 Task 6): settings, schema, the instruction tree and the
    form contract are done.** `data/settings.json` `address` is
    `{city: Carlisle, region: Cumbria, country: GB}` — no street, no postcode, no
    coordinates, because the breeder has not supplied them; `src/components/Schema.astro`
    emits only the fields that are there and no `geo` node, and `scripts/schema_check.py`
    accepts an address without a street or a postcode while blocking one that states a
    field it has nothing to put in. `PUPPY_OPTION` is now `waiting-list`, the option
    `src/components/kit/ContactFormKit.astro` builds, and
    `src/components/ContactForm.astro` emits the same set from the same data, which also
    closes Known Issue 22. Every instruction file under `.claude/`, `CLAUDE.md`, `rules/`
    and `docs/reference/` names Carlisle, and the fact lint bans the old city outright,
    allowing it only on a line carrying the outreach page's slug or this issue's number.
    **Page bodies and their ported schema follow per page in Tasks 7–18** — the eleven rich
    pages and the blog are rewritten one at a time and are not edited ahead of their task,
    so the old city is still in the generated page bodies until each is rebuilt.
    **4 of 12 rebuilt (Task 7, `/privacy-policy-uk/`, 2026-09-19; Task 8,
    `/thank-you-blue-staffy-puppies-journey/`, Task 9,
    `/uk-blue-staffy-breeders-contact/`, and Task 18, `/`, all 2026-09-20).** None of the
    four carries the old city anywhere: every body is written fresh, and the legacy schema
    graph that
    hard-coded a street address, a postcode and coordinates for the former city is gone with
    them — `BaseLayout` now emits the `WebPage` node from `data/page-dates.json` instead, and
    the contact page emits its own `ContactPage` and `FAQPage` nodes and nothing else. Both
    new pages drop the migrated body's link to that city's breeding-dogs page, and the
    contact page drops the "Our Location" paragraph built on the old address, each recorded
    with its reason in the board record's `dropped`; the by-appointment-only fact itself is
    kept. The homepage is the loudest of the four: the migrated body named the old city three
    times — as the home city in the delivery list, as where the puppies were socialised, and
    in the FAQ lede — plus a landmark in it, and the Google Maps iframe at the foot encoded
    the old street, postcode and coordinates in its URL. All of it is gone, each strand
    logged with its reason in `dropped.names`, `dropped.text` and `dropped.embeds`, and the
    FAQ lede is carried under rule 15 with the city clause removed rather than re-pointed
    (`verbatim.changed`). The one surviving reference anywhere on the rebuilt page is the
    href of `/uk-locations/staffy-breeding-dogs-glasgow/`, whose URL rule 11 keeps and whose
    anchor on this page names our breeding dogs rather than a town.
    **8 page bodies to go.**
    **2026-09-22 (project 4 close): all twelve rebuilt pages carry the former city 0 times.**
    What is left is outside project 4's rewrite scope and is **build 5**'s: the meta
    descriptions and hub copy of `/available-puppies/` and its six puppy pages
    (`src/pages/available-puppies/index.astro`, `[slug].astro`, `src/components/PuppyList.astro`),
    `/uk-locations/` (`src/pages/uk-locations/index.astro`), `/search/` (two
    `data/page-map.json` titles), and the 28 location bodies. Spec §7.3's literal grep is
    therefore not yet 0; the gate report records it as the one partial FAIL.
    **Update (project 5 readiness pass): the templates outside the 28 location bodies are
    done.** `/available-puppies/`, its six puppy pages (meta description and delivery row), the
    unused H2 branch of `src/components/PuppyList.astro` and `/uk-locations/` (meta description
    and intro) print `SITE.address.city` from `data/settings.json`, and
    `tests/py/test_former_city_templates.py` keeps the former city out of `src/` except in a
    route that names it. `/search/` now shows each page's own built title
    (`scripts/build_search_index.py` no longer copies the migrated titles in
    `data/page-map.json`), so the one index row still naming the former city is the outreach
    page, whose built title does. What remains is **build 5**'s: the 28 location bodies and
    their `data/locations.json` rows (including the former street address, Known Issue 55).

17. **There is no query-augmentation skill.** `.claude/skills/bsuk-location-page-builder/SKILL.md`
    was rebuilt in project 3 around a per-city competitor scan, and it names the
    query-augmentation step — expand the primary keyword into the real questions before
    writing, mirror the strongest six into the FAQ — while recording that no skill performs it.
    Today it is done by hand or not at all. **Project 5** needs one before it builds 28 city
    pages from that skill. **Closed 2026-09-23** by `.claude/skills/bsuk-query-augmentation/SKILL.md`,
    `scripts/query_augment.py` and the gate `scripts/query_coverage_check.py` (in `npm run check:all`).
18. **The hero lede is clamped to two lines, and the copy must fit it.** Design rule 10 clamps
    the lede and `scripts/measure_canvas_heights.mjs` records `lede_overflow`, which the test
    requires to be zero — so copy needing a third line fails the build rather than being
    silently truncated by the clamp. Measured at zero today at 1024, 1100 and 1280. It is a
    standing constraint on every hero **project 4** writes.
19. **CLOSED (project 5 readiness pass) — `Button.kind` keeps all five treatments, by the user's
    ruling R10 (2026-09-23).** `test_built_buttons_show_all_five_kinds` in
    `tests/py/test_design_components.py` holds the five. Was: **`Button.kind` keeps all five
    treatments — AWAITING THE USER'S CONFIRMATION.** The prune
    deleted every other variant prop, but `Button` kept five treatments renamed as `kind`
    (primary, outline, inverse, submit, text) on the reasoning that a page needs more than one
    button and these are five jobs rather than five styles. That is a judgment made during
    execution and the user has not confirmed it. Deleting an unwanted treatment is a one-line
    registry change plus its fixtures and is cheapest **before project 4** mounts buttons on
    real pages.
20. **CLOSED 2026-09-22 (project 4).** `prebuild` runs `scripts/generate_page_dates.py`, `BaseLayout`
    emits `dateModified` from it, and `generate_page_dates.py --check` is green. Was: **`data/page-dates.json` is generated but unwired.** `npm run dates` writes it from git
    history, and `/kit-preview/` is its only consumer — it reads the file for its `WebPage`
    `dateModified` rather than calling `new Date()`. The 18 `schema-date-modified-present` rows
    in Known Issue 8 are exactly the real pages that do not read it yet. **Project 4** wires it
    into the content pass and into sitemap `lastmod`.
21. **CLOSED (project 5 readiness pass) — the separator dot takes the strip's steel ink.**
    `.dot` in `src/components/kit/CounterStrip.astro` is `--color-brand` on the strip's
    `--color-brand-soft` bed, a pair `data/design/contrast.json` already guards, and
    `test_counter_inks_are_guarded_pairs_on_the_counter_bed` in `tests/py/test_design_tokens.py`
    requires every ink the strip paints on its bed to be such a pair (the label's
    `--color-text` pair was added with it). `a11y-text-contrast-aa`: 6 rows → 0 on
    `/kit-preview/`, thank-you and contact. Was: **(2026-09-22: now also on
    `/thank-you-blue-staffy-puppies-journey/` and `/uk-blue-staffy-breeders-contact/`, through
    C-UT1's inline dot — 6 advisory rows on 3 pages; still open, build 5.)** **The separator dot
    misses AA by one hundredth.** Two advisory `a11y-text-contrast-aa` rows
    on `/kit-preview/` at 768 and 1280: the middle-dot separator measures 4.49:1 where AA wants
    4.50:1. Decorative, but a real row. The fix then proposed was one token step darker; not
    taken — the user's ruling (D10: steel, 2026-09-23) gave the dot the strip's own
    `--color-brand` instead.
22. **The kit contact form reports one missing screening option.** `form-inquiry-contract`
    reports one advisory row at all three viewports on `/kit-preview/`: the puppy select is
    missing the collection option that `scripts/form_contract_audit.py`'s `PUPPY_OPTION`
    constant requires. The kit form is right and the constant is wrong — the option names a
    collection point the breeder has left (Known Issue 16). **Closed 2026-09-19** by project 4
    Task 6: the constant is `waiting-list`, the option the kit form builds, and the legacy
    form now emits the same set from the same data.
23. **Page weight of the inline lockups — now only on the legacy shell (updated in the
    project 5 readiness pass).** The kit chrome that `src/layouts/PageShell.astro` mounts draws
    the mark from the sprite and inlines no lockup, so the twelve rebuilt pages, the hubs, the
    puppy pages and the post carry 5–8 KB of inline SVG (the built homepage: 7,618 bytes of
    182,646). The legacy shell (`src/components/SiteHeader.astro` and
    `src/components/SiteFooter.astro`, mounted by `src/layouts/BaseLayout.astro`) still
    inlines both lockups, 15,084 + 15,391 bytes, on 36 routes: the 28 location pages,
    `/search/`, `/kit-preview/` and six board-preview routes. It closes for the location pages
    when **build 5** moves them onto `PageShell`. Was: the header and footer inlined about 15 KB
    of SVG each on every page (homepage 163 KB, 52 KB of it inline SVG); recorded, not yet a
    defect.
24. **CLOSED (project 5 readiness pass, Task R3) — Fraunces and Source Sans 3 are self-hosted.**
    The four `.woff2` files are in `public/fonts/`, copied unchanged from
    `@fontsource-variable/fraunces@5.3.0` and `@fontsource-variable/source-sans-3@5.3.0` (the user
    approved the download), each recorded with its size and sha256 in `data/design/fonts.json`;
    `src/styles/fonts.css` declares them (`font-display: swap`; latin preloaded by `BaseLayout`,
    latin-ext on demand) and `tests/py/test_self_hosted_fonts.py` holds the files, the faces, the
    preloads and the built pages to each other — and no built page asks Google Fonts for anything.
    The Artifact builders keep linking Google Fonts and `page_css()` leaves the site's faces out of
    them. Every rebuilt hero was re-measured with the faces loaded (Known Issues 18, 28, 30): the
    about page's aside label went so its band holds at 1280 (re-approved as wording at the pause),
    and the kit canvas heights were re-measured. Lighthouse medians are in the gate report (mobile
    Performance 95 on `/`, 95 on the about page and the breed guide, 97 on the contact page;
    desktop 100 on all four). The Design System artifact's font list stays empty by design: its
    previews link the same two families. Was: **The picked fonts are not loaded at all —
    corrected in the project 5 readiness pass.**
    This entry said Fraunces and Source Sans 3 load from Google Fonts. They do not: nothing
    under `src/` or `public/` requests a web font, and no page in `dist/` carries a font link or
    an `@font-face` rule. `src/styles/tokens.css` names the two families first in
    `--font-display` and `--font-body`, so the site renders in their fallbacks — Georgia for
    headings, `system-ui` for body text — unless a visitor has them installed. Only the Artifact
    and board builders link Google Fonts (`scripts/build_page_board.py`,
    `scripts/_kit_sections.py`, `scripts/build_picks_board.py` and the spec, plan and report
    builders), so every board and canvas the breeder approved showed the picked type and the
    site does not. Every hero measure so far (Known Issues 18, 28 and 30) was taken in the
    fallbacks, and loading the real fonts will reflow them. **Needs the user's decision before
    project 5 builds pages**: self-host the two families, link Google Fonts, or keep the
    fallbacks and record that in the design system. The Design System artifact's empty font
    list (spec §11 amendment 7c) stands until then.
25. **CLOSED 2026-09-22 (project 4 close-out audit) — `scripts/render_baseline.py`'s default
    report is project 4's.** `REPORT`, `tests/py/test_render_baseline.py`'s `REAL_REPORT`,
    `npm run baseline` and `scripts/health-sweep.sh` all name
    `docs/reports/render-baseline-project4.md`, which exists as a skeleton with the two
    generated-block markers and no numbers — Task 19 fills it. Until then the two
    real-scorecard tests skip (an empty block is "not run yet", not drift) and the sweep
    warns. `--out` now creates a missing report, `--check` on a missing one exits 1 instead of
    crashing, and the plan's Task 19 command no longer combines `--out` with `--write` (they
    are one option; argparse read the pair as a second `--out` with no value). Projects 2's
    and 3's files stay as published.

26. **Existing images and videos must be reused with their URLs intact.** Every file under
    `public/images/` and the YouTube embeds in `data/settings.json` already rank; projects 4–6
    reuse them first and never rename, delete or re-encode a served file (CLAUDE.md working
    rule 11, breeder 2026-09-19). Project 3 briefly deleted the two legacy logo rasters
    (`blue-staffy-uk-official-logo0.png`, `blue-staffy-uk-header-logo-88.webp`) when the SVG
    lockups replaced them; both are restored at their original paths and stay served even
    though no template references them. **Standing constraint for projects 4–6.**

27. **MOVED TO PROJECT 6 (user ruling R14, 2026-09-23) — no `uploadDate` for any VideoObject.**
    It stays off until the breeder reads the real dates from the channel, and project 6, which owns
    the launch and the rich results, asks for them. Was: **No `uploadDate` for any VideoObject — no
    file in this repo holds one.** Project 4 Task 12
    mints a `VideoObject` on each of the four rebuilt pages that carry a YouTube embed (the
    homepage's three ids, `/blue-staffy-uk-breeders/`, `/buy-staffy-puppies-for-sale-uk/` and
    `/uk-staffordshire-bull-terrier-guide/`), built from the record's own `video` block through
    `src/lib/video.ts` so the schema and `video-sitemap.xml` describe one id in one spelling.
    Google wants an `uploadDate` for a video rich result and **none is written**, because the
    only two dates available would both be inventions: the migrated theme's own
    `VideoObject.uploadDate` is the old site's markup rather than a fact this repo keeps (the
    same reasoning that removed "since May 2025" from the about page's video caption at
    1c500e5), and `data/page-dates.json` records when the PAGE changed, which says nothing
    about when the footage was published. `scripts/schema_check.py` accepts the node without
    one — it blocks five specific defects and a missing optional field is not among them — so
    this is a rich-result gap rather than a gate failure. **Closes when the breeder supplies
    the real upload dates from the YouTube channel**, which is a two-minute read of the
    channel's video list and cannot be derived from anything on disk.

28. **RESOLVED 2026-09-21 — the hero ceiling was a 1280 measure applied from 1024.** At 1024
    the legacy `split` hero's two-line `.lede` clamp hid **198px of `/` and
    `/privacy-policy-uk/`, 165px of `/uk-blue-staffy-breeders-contact/` and 99px of
    `/thank-you-blue-staffy-puppies-journey/`** — three to six lines of each page's own
    opening sentence — and the hero's `.container.inner` ran past its box by **41px on `/`,
    45px on `/buy-blue-staffy-puppies-uk/` and 12px on `/buy-staffy-puppies-for-sale-uk/`**,
    far enough on the first two to end 17px and 21px inside the section below. One cause: the
    copy column is narrower at 1024 than at 1280, so the same words take more lines, and the
    band was not allowed to grow. Not a copy defect — the same copy fits at 1280 — and the H1
    that grows is in the page's VERBATIM SET, so it cannot be shortened to fit a band.
    **The breeder's ruling (2026-09-21): the band gives way below 1280.** `max-height: 450px`
    and the lede's line-clamp are now scoped to `min-width: 1280px`; the 390 floor, the type
    step-down and the photo column's absolute cap stay on from 1024, so a hero still reads as
    a hero and its photograph still cannot set its height. Recorded as spec §9 amendment 10.4
    sub-note. Measured after, on `/`, the listing, why-us, privacy, thank-you and contact at
    1024 / 1100 / 1280: **0 hidden copy, 0 clipping and 0 overlap with the next section at
    every width**, and 390–450 held at 1280 on all six. The harness now asks the same
    question: `scripts/measure_canvas_heights.mjs` records `content_below` and `next_overlap` (its
    three older figures were all taken INSIDE the hero, which is why this was found by hand),
    and the band assertion applies only at 1280 while the overlap assertion applies at all
    three widths.
    **What is left, deliberately, is at 1280 only.** The two-line clamp is how the 390-450
    band is kept there, so on the four pre-rule-16 pages it still hides the tail of a long
    lede at that width — measured **165px on `/`, 132px on `/privacy-policy-uk/` and
    `/uk-blue-staffy-breeders-contact/`, 66px on `/thank-you-blue-staffy-puppies-journey/`**.
    That is unchanged from before the ruling rather than introduced by it, and it is a COPY
    length to settle when each of those four is rebuilt against its own rule-16 board, not a
    second release of the ceiling: the lede is written fresh under working rule 15 and can be
    cut to two lines, which the verbatim H1 beside it cannot.
    **Residual CLOSED 2026-09-22**, with the four rule-16 rebuilds (H-HM2/C-HM2 on `/`, H-UT1
    on privacy, H-UT1/C-UT1 on thank-you and contact). Each page's own lede was rewritten to
    two lines at every desktop width, and the sentences it gave up moved into the hero
    section's own paragraph beneath the band rather than being dropped (working rule 6).
    Measured on `dist/`, `.kit-hero` height / lede overflow at 1024 · 1100 · 1280:
    `/` 451/0 · 450/0 · 450/0; `/privacy-policy-uk/` 422/0 · 450/0 · 450/0;
    `/thank-you-blue-staffy-puppies-journey/` 422/0 · 450/0 · 450/0;
    `/uk-blue-staffy-breeders-contact/` 422/0 · 450/0 · 450/0 — two lede lines at all three
    widths on all four, no clipping, and no overlap with the section below.

29. **RESOLVED 2026-09-21 — `/blog/` is kept as the legacy archive and exempted by name.**
    The built page is `noindex, nofollow` with its canonical on `/blue-staffy-blog-guides/`,
    the real guides hub rebuilt at `5ed62ed`, and it was failing the rich-page floor
    (`all_six_levels`, `min_h5_5`, `min_h6_5`, `faqpage_present`). **The breeder's ruling: keep
    the route** — `public/_redirects` sends `/category/*` to it with a 301, and retiring it
    would turn every category URL the previous site served into a 404 — **and exempt it by
    name.** A de-indexed redirect target could satisfy those four only by inventing eleven
    sub-points and three questions it does not have, which is a page written for a gate and
    schema for content that is not there. `ARCHIVE_EXEMPT` in `scripts/final_page_audit.py`
    carries the slug and the reason, and the audit prints both; the exemption is by SLUG
    rather than by profile, because the guides hub is on the same profile and the four checks
    are exactly right there. `--blog` now reports 3 PASS, 0 problems. **Project 5 may retire
    the route** once its two new posts land and the archive carries nothing the hub does not.

30. **PARTLY CLOSED (project 5 readiness pass, Task R13) — the buying guide is off H-GD3; the
    breed guide still sits at the ceiling.** Measured at 1280 with the self-hosted faces: the buying
    guide on H-GD2, with its chip row, is 411px with nothing clipped (it was 450 with 3px of copy
    past its box); the breed guide keeps H-GD3 at 450px with nothing clipped and no headroom. What
    is left is the breed guide's zero headroom — one more line of its H1, eyebrow or aside puts it
    over — and the closing condition below.
    Was: **The H-GD3 hero's photo column pins two pages at exactly 450px.** `.pic` in the
    interior-guide panel arrangement carries `aspect-ratio: 3 / 4`, and at 1280 that makes the
    photo 299px tall, which with the panel's 32px padding puts
    `/uk-blue-staffy-puppy-buying-guide/` and `/uk-staffordshire-bull-terrier-guide/` at
    **exactly 450px** — the very top of rule 10's 390-450 band, with the buying guide's inner
    content already 3px past its own box. `/blue-staffy-health-uk/`, the third H-GD3 page, sits
    at 444 because its copy column is shorter. Nothing is clipped today and the band is met,
    but two of the three pages have zero headroom: one extra line of H1, eyebrow or aside on
    either of them puts the arrangement over the ceiling, which is how the defects amendment
    10.4 lists were found. Known Issue 28's ruling relieves this BELOW 1280 — the band may now
    grow there, so an extra line at 1024 is absorbed rather than clipped — and leaves it
    exactly as it was AT 1280, where the ceiling still holds and these two have nothing spare.
    **Closes when the aspect is budgeted rather than fixed** — the photo box sized from the
    space the copy leaves, not the other way round.

31. **Two blocking rows on the two data-driven routes (corrected 2026-09-22). First half
    CLOSED (project 5 readiness pass):** `/available-puppies/` opens each card at H2 —
    `src/components/PuppyList.astro` with `heading="none"` — so `sem-heading-order` is 3 rows
    → 0 there, guarded by `tests/py/test_puppy_hub_headings.py`. The location route's anchor
    row (the second bullet below) stays **build 5**'s.
    `test:render:pages` fails six rows on two pages project 4 did not rebuild, and the two are
    DIFFERENT failures — this entry first said both were SEM, and the close-out audit's run
    shows otherwise:
    - `/available-puppies/` — `[SEM] 1 skipped heading level(s): H1→H3 at "Roman"` at all three
      viewports: the card grid opens each puppy at H3 under the page's H1 with no H2 between
      them (from `data/puppies.json`).
    - `/uk-locations/blue-staffy-puppies-uk/` — `[NAV] 1 of 2 in-page links land outside` the
      landing band, at all three viewports, first `#Staffy-adoption` (at 2903px / 3436px /
      3439px): the migrated body's own anchor target sits outside the band the sticky header
      leaves. It is not a heading skip.
    Both are inherited rather than introduced (identical at `7b5be27`), and they are the only
    rows standing between `test:render:pages` and a clean exit — every one of the twelve
    boarded pages passes. **Project 5's puppy and location cluster owns both routes** and
    closes them: the missing H2 (or cards opened at H2) on the first, the anchor target on the
    second.

32. **CLOSED (project 5 readiness pass).** `.bp-chrome` in
    `src/pages/board-preview/[slug].astro` is a `minmax(0, 1fr)` grid track, so the strip
    specimen keeps its own scroller: the route's document is 375px wide at 375 (was 981px) and
    each strip 279px (was 933px). Was: **606px of horizontal overflow at 375 on the contact
    board-preview route.** `NAV.kit-strip`
    inside `.bp-targets` on `/board-preview/uk-blue-staffy-breeders-contact/` is 933px wide in
    a 375px viewport, and the page scrolls sideways. It is the mobile section STRIP specimen
    rendered over its six stub targets — scaffolding the preview route builds so the breeder
    can see the arrangement, not a section of any page. Verified identical at `7b5be27`. The
    contact page itself has zero horizontal overflow at 375, and so does every counter and
    hero rendering on that route. PREVIEW-ONLY, and it closes when the specimen's target row
    is given a scroller of its own rather than being allowed to set the page's width.

33. **PARTLY CLOSED (project 5 readiness pass, Tasks R11 and R12) — what is left is H-UT1's one
    photograph.** The homepage's H-HM2 renders the four-photo mosaic and its figure tiles: the
    record names four of the homepage's own photographs at their original paths and two figures read
    from `data/settings.json` (`tests/py/test_homepage_hero.py`), approved on its board at the
    readiness pause (user ruling R11: photos 1–4 kept, the beside/below layout and photo 1's alt
    text as they were). The three utility pages are exempt from rule 16 by name (user ruling R12):
    `RULE16_EXEMPT` in `scripts/pageboard.py`, `tests/py/test_rule16_gate.py`, and CLAUDE.md rule
    16 says so; their refresh notes now name H-UT1 and C-UT1. Still open: H-UT1 on the three
    utility pages renders its single-photo fallback, because each record names one photograph —
    the rulings covered the homepage and the sharing, not these mosaics. Was: **Two approved picks
    render as their DEGRADED arrangements, faithfully.** H-HM2 on `/` is
    "four-photo mosaic above the copy, figure tiles beneath it", but the homepage record's
    `top` names ONE photograph and no ledge figures, so the hero renders — on the board the
    breeder approved and on the page — as the single photo beside centred copy with no ledge:
    `Hero` degrades a mosaic of fewer than two tiles rather than inventing one, and a ledge
    whose data the record did not supply renders nothing. The same is true of H-UT1 on all
    three utility pages (one photograph each). And those three pages all picked H-UT1, and
    thank-you and contact both picked C-UT1, so rule 16's "no two pages share the same hero
    layout or counter strip" is not met between them; their `refresh` notes still describe
    the H-UT2/H-UT3 arrangements they did not pick. Separately, C-UT1 (`tiles: inline`,
    `label: above`) printed its inter-figure `·` on a line of its own under the first figure,
    because the dot was inside a column-flex tile — FIXED 2026-09-22 in `CounterStrip`: the dot
    is positioned out of flow in the gap after its tile (verified at 375 / 768 / 1280 on
    thank-you, contact and the contact board preview; hidden below 720px as before).
    **Closes with a breeder decision**: more photographs and ledge rows on the four records
    (and new refresh notes), or new picks. The page renders what was approved until then.

34. **Per-slug evidence budgets for the twelve rebuilt pages (2026-09-22).**
    `scripts/evidence_audit.py --all` raised term-budget ERRORs on every rebuilt page, and not
    because the writing is stuffed: working rule 15 requires each page's migrated H1, keyword
    H2/H3s, their opening paragraphs and its FAQ questions word for word, the page shell repeats
    the approved headings in the section dial, strip, sheet and table of contents, and the
    approved tables and counters state the head terms in their own rows. The page-type ceilings
    in `data/quality/evidence-budgets.json` are uncalibrated proposals re-based from the source
    repo (`calibrated: null`) and were never sized for any of that. So each rebuilt slug now has
    a `budgets_by_slug` entry, MEASURED on `dist/`: budget = carried count (the verbatim set on
    the page plus the shell's repetition of it) + the page type's own-prose ceiling, floored at
    the count as built — a ratchet, so any later edit that raises a term re-fails. Each entry's
    `_why` prints the decomposition per term, and names the terms where the page's own text
    (which includes the kit's table, counter, FAQ and review rows) is already over the proposed
    ceiling. **Project 5's location and puppy pages carry no override** and are judged on the
    page-type defaults; the audit still ERRORs on three location routes, the blog post and the
    board-preview routes, none of them rebuilt pages. A calibration pass that measures the
    ceilings against cited pages should retire most of these entries.

35. **CLOSED (project 5 readiness pass, Tasks R13 and R12) — three guides, three heroes, and a
    gate.** Re-boarded and approved at the readiness pause (user ruling R13): the health guide on
    H-GD1, the breed guide on H-GD3, the buying guide on H-GD2 (with its chips, and its counter
    re-approved as C-GD2). H-GD1 had never been rendered; `Hero` now puts a split hero's aside on a
    second row (three tracks left the copy 276px), and it fits the health guide only, which leaves
    its credential line out of that arrangement. `tests/py/test_guide_heroes.py` holds the three
    apart, and the board-gate row this entry asked for exists as `tests/py/test_rule16_gate.py`:
    any hero or counter two pages share fails, the three utility pages excepted by name;
    `scripts/board_gate.py` runs the same check per board and `scripts/board_approve.py` refuses an
    approval that would create a share. Was: **The three guides share one hero arrangement
    (2026-09-22).** `/blue-staffy-health-uk/`,
    `/uk-staffordshire-bull-terrier-guide/` and `/uk-blue-staffy-puppy-buying-guide/` all picked
    H-GD3, so working rule 16's "no two pages share the same hero layout" is not met between
    them — the same gap Known Issue 33 records for the three utility pages' H-UT1. Their
    counters differ (C-GD1, C-GD3, C-GD2). `ledger-tuple-owned` does not catch it because its
    signature is hero + faq + table + takeaway, and the three differ on the other axes.
    **Closes with the breeder's new picks** for two of the three (H-GD1 and H-GD2 are unused),
    and should be followed by a board-gate row that fails a shared per-page hero or counter
    outright.

36. **Seventeen duplicate passages touch rebuilt pages (2026-09-22).** `scripts/dup_content_audit.py`
    reports 131 passages; 114 lie between pages project 4 did not rebuild, and 17 touch one it
    did: the FAQ answer "a comprehensive puppy package…" rendered from one `data/faq.json` row
    on four pages, and "are the puppies raised in a family home…" on two; the review
    attribution tail "…is the heart of our family — the Victoria Family, Manchester" crossing
    the quote whitelist on three pairs; three working-rule-15 openings the homepage carries from
    the pages it summarises; the post against the buying guide (35 words); and pup-sale's
    "healthy, vaccinated and ready" line against two location bodies. **Build 5**: whitelist
    shared FAQ rows and review attributions as sitewide lines (as the quotes already are), and
    rewrite the rest when the location and post bodies are rewritten.

37. **CLOSED (project 5 readiness pass) — the trailer is Fable 5.1.** The user's standing
    rule for this repo is `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`, and all
    115 commits since the project 4 merge (`db37ca1..9927710`, both bridge builds) carry it.
    The nine Opus 5.5 commits described below and the project 4 merge commit stay as history;
    nothing rewrites them. Was: **The commit trailer (2026-09-22).** Spec §7.7 names
    `Co-Authored-By: Claude Fable 5.1`.
    Every commit on `page-rebuilds` carries a `Co-Authored-By` trailer; 111 carry Fable 5.1 and
    the last nine (`2ce9e93` onward, including step 0 and the two close-out commits), plus the merge commit
    on `foundation`, carry `Claude Opus 5.5`, by the controller's instruction for those
    sessions. **Closes with the user's ruling** on which trailer project 5 uses.

38. **CLOSED (project 5 readiness pass, Task R8) — the breed guide ships the S3 facade.** The user
    ruled S3 (R8); the pick moved on the breed guide's re-board (a re-approval cannot move a pick),
    `VideoEmbed` takes `play` from it, and `tests/py/test_breed_guide_video.py` holds the pick and the
    built page (no player until pressed) together. Lighthouse Best Practices 100 on desktop and 100
    on mobile (medians of three; mobile Performance 95) (was 96 / 96). Was: **The breed guide's
    video player loads with the page (2026-09-22).** The breeder picked S2
    (the player full width on a steel band) for `/uk-staffordshire-bull-terrier-guide/`, so
    `youtube-nocookie.com/embed/g9iV9RVr_Sk` loads on page load and Chrome raises a cookie
    issue: Lighthouse Best Practices 96 on mobile and desktop, every other rebuilt page 100.
    The S3 facade — rule 14's default — fetches the player only on a press. **Closes with the
    breeder's choice**: keep S2 and accept the score, or pick S3.

39. **Project 5 prerequisite — nested routes (2026-09-23).** The STOP rules in
    `.claude/skills/bsuk-location-page-builder/SKILL.md` and
    `.claude/skills/bsuk-query-augmentation/SKILL.md` point here. Four tools build paths from a
    flat slug and cannot read or write a city page at `uk-locations/<slug>`:
    - `scripts/facts_preserved_check.py`: `dist_html` (lines 360–362); the `--extract` path
      creates only `data/facts/` and no subfolder (mkdir on 395, write on 396).
    - `scripts/link_parity_check.py` lines 231–232 (the dist path and the board path).
    - `scripts/verbatim_set_check.py`: `dist_html` and `load_record`, and `do_extract`
      (lines 486–491), which creates only `data/verbatim/` and no subfolder.
    - `scripts/pageboard.py` `own_live_key` (lines 920–927, the return on 927).

    Each must resolve `uk-locations/<slug>` to `dist/uk-locations/<slug>/index.html` (and the
    matching board, record and live key) through `data/page-map.json`, as
    `scripts/migration_parity.py` effectively does. **No city page goes into
    `data/facts/rebuilt.json` until this is fixed and tested.** In the same change,
    `scripts/query_coverage_check.py` should report a problem when a route's last segment is in
    `data/facts/rebuilt.json` but its page is missing, print the awaiting-rebuild slugs, and
    turn a malformed `data/facts/rebuilt.json` into a problem line rather than a crash.
    **CLOSED 2026-09-24 (project 5 readiness, Task F2).** One resolver,
    `scripts/_slugs.py` (`resolve_page`, `built_page`), turns a slug into its key and route
    through `data/page-map.json`. A city page keeps its bare slug as its key — the name of its
    `data/facts/`, `data/verbatim/` and `data/boards/` files and its `data/facts/rebuilt.json`
    entry, as `scripts/migration_parity.py` already keyed it — and is found at
    `dist/uk-locations/<slug>/index.html`. `scripts/facts_preserved_check.py`,
    `scripts/link_parity_check.py`, `scripts/verbatim_set_check.py` (its built page, record, set
    file and page title, and for a city page the migrated body, read from the city's row of
    `data/locations.json` at the frozen migration commit) and `scripts/pageboard.py`
    (`own_live_key` and its four built-page readers) all use it. `--extract` takes the bare slug
    or `uk-locations/<slug>` and creates any folder a nested key needs.
    `scripts/query_coverage_check.py` now fails a page listed in `data/facts/rebuilt.json` that is
    not built, prints the slugs awaiting rebuild, and reports a malformed
    `data/facts/rebuilt.json` as a problem line. The STOP rules in the location-page-builder and
    query-augmentation skills are removed. Tests: `tests/py/test_nested_routes.py` and the
    additions to `tests/py/test_query_coverage_check.py`. Left as it is: pageboard's freshness
    check still looks for a page's own sources under `src/pages/<slug>`; where a rebuilt city
    page's source lives is a project 5 decision.

40. **CLOSED for its instruction items (project 5 readiness pass, Tasks B1–B5 and B7); the rest is
    Known Issue 59.** Fixed: the parents' clear results are the unproven `parents-dna-clear` claim at
    `NOT FETCHED`, so `data/faq.json` no longer asserts what `rules/copy.md` records as not fetched
    without the ledger saying so (B1; the FAQ rows' own wording waits for the breeder — Known Issue
    68); the location builder cites rules 15 and 16, names `Hero`'s arrangement props, gives no
    component a variant letter and no city a shared counter, keeps reviews in their own sections,
    reads competitors from the question file and labels body sections (B2); the comparison builder
    derives its section count and lost push-to-main, the breeding pair, "12+ years" and NewsletterV2
    (B3); the blog builder uses the link library and the registry (B4); the SEO checklist's external
    links are UK library rows (B5); the map skill's US wording is gone (B7); the puppy ContactForm
    name is gone too (`43dc994`: `ContactFormKit` everywhere). Moved to Known Issue 59: the
    empty-`h1` rows, the later gate work and the minors. Was: **Project 5 builder checklist
    (2026-09-23).** Quality-review items on the builders deferred by the user's ruling during the
    query-augmentation build; clear each before or while the first city page is built.
    - Rule 15 (faithful rewrite) against the migrated city FAQs: 11 indexed city pages carry
      bodies, and the precedence table cites rules 1–10 only.
    - 11 location rows have an empty `h1`, so the primary-keyword source is undefined for them.
    - The worked example still carries variant letters and a shared counter, against rule 16
      (per-page hero and counter).
    - `src/components/kit/Hero.astro` takes layout props (`layout`, `align`, `media`, `ledge`)
      while the builder says "no variant prop" — reconcile the wording.
    - The bottom review mode is ambiguous; reviews sit in their own sections, never inside a
      body section.
    - Health-test fact conflict: `data/faq.json` asserts "certified clear" while
      `rules/copy.md` records the certificate as NOT FETCHED.
    - Step 1's hand-recorded competitor table and the board "competitor block" (which does not
      exist) — use the question file's competitors and `why_source` URL instead.
    - `scripts/query_coverage_check.py` needs body blocks as `<section data-section-label>`;
      the builder must say so.
    - `.claude/skills/bsuk-blog-post/SKILL.md` leftovers: governs-in-conflict wording,
      Firecrawl-first, no link library, "airport" delivery, "since 2014", push to main.
    - `.claude/skills/bsuk-comparison-page-builder/SKILL.md` leftovers: a US Google market
      setting, 22–25 fixed sections, push to main, eggs/breeding pair, "12+ years", a
      NewsletterV2 variant.
    - `.claude/skills/bsuk-seo-master-checklist/SKILL.md`'s external-link library is
      US-centric (AVMA, AAHA, ASPCA, FTC, VEG, Pet Poison Helpline, Chewy; the petmd homepage
      mislabelled) — replace with UK sources (PDSA, Blue Cross, BVA, gov.uk) via
      `docs/reference/external-link-library.md`.
    - `.claude/skills/bsuk-google-map/SKILL.md`'s location template uses `CITY%2C%20STATE` and
      "For state/city location pages" (US wording).
    - Later gate work: count built `dist/uk-locations/*` pages with no question file and print
      it; an optional per-page-type "must have a file" switch once project 5 covers all 28;
      check the visible FAQ questions come from the question file; an extra-section H2 must
      sit in a body section, not the frame; a heading-covered answer should stop at its
      section end.
    - Minors: lifespan source; `rules/copy.md` as a source; sem-all-six-levels is page-level;
      proximity/roads claims without a source; the former-city row (Known Issue 16) and the
      national rows compete; the blog builder's raw caps note; the puppy ContactForm name;
      top-10 vs top-5.

41. **Questions for Lisa Bright (2026-09-23). Sent (project 5 readiness pass, Task R6):** the
    questions below, with the Kennel Club, licence (Known Issue 54) and Lucy's Law (Known Issue 7)
    questions, are `docs/reference/questions-for-lisa.md` (21 questions), published for the user to
    forward (https://claude.ai/artifact/CvLPpj438KFNfJcFd9gFTH). Open until she answers. Since 2026-09-26 they are the first batch on the answer board (`docs/reference/answer-board/README.md`): the user types each answer there and presses Send to Claude Code. Grouped and reworded from the files' blocked
    buyer questions: the Manchester and Leeds question files hold buyer questions (from Google,
    Bing, ChatGPT and Reddit) that the merge blocked as "unverified fact" because BSUK has no
    recorded fact to answer them. Each answer becomes a `data/faq.json` row or a
    `data/settings.json` key; then both question files rebuild
    (`python3 scripts/query_augment.py <slug> ...`, all sources cached, no calls).
    - Are there blue Staffy puppies available now for buyers in Manchester?
    - How much does a BSUK puppy cost?
    - Should I pay a deposit before I have seen the puppy — what is BSUK's deposit policy?
    - Is there a waiting list?
    - Can I see the puppy with its mother where the litter was raised?
    - Do you give a written contract and a return-to-breeder policy?
    - Does the contract give me time to have my own vet check the puppy?
    - Have both parents been tested for L-2-HGA and hereditary cataracts?
    - Have the parents had eye examinations and elbow screening, as well as DNA tests?
    - What are the parents' Kennel Club registered names, and what if the papers are delayed?
    - What is the parents' coefficient of inbreeding?
    - How can I confirm the puppy has been examined by a vet (can I contact your vet)?
    - Has the puppy had its first vaccination before I collect it?
    - What socialisation has the puppy had?
    - Can a blue puppy come from parents that are not both blue — what colours are your
      parents?
    - (Added in the project 5 readiness pass, from project 4.) Is BSUK a member of the Kennel
      Club Assured Breeder Scheme? The migrated why-us body claimed it five times and project 4
      dropped every claim as unbacked (`data/boards/buy-staffy-puppies-for-sale-uk.json`
      `dropped`); a yes, with the membership record, lets the claim back onto the pages.
    - (Added in the project 5 readiness pass.) Do you give a written health guarantee? If so,
      for how long and what does it cover? The answer sets `data/settings.json`
      `guarantee_days` (null today). `data/faq.json` `home-health-guarantee` still promises a
      *written* guarantee: that is project 4's wording of the old site's "puppy health
      guarantee" claim (`data/facts/index.json`), so "written" is itself unconfirmed.
    - (Added in the project 5 readiness pass.) Do you follow Puppy Culture or early
      neurological stimulation (ENS) with your litters? One migrated location body in
      `data/locations.json` says so. It is unconfirmed; that location page still renders it,
      and no rewritten page carries it until she confirms it (build 5 rewrites the body).

42. **Competitor intelligence build (2026-09-23).** The source repo's competitor-registry,
    competitor-intel, strategy-synthesizer and keyword-gap agents were not ported. User ruling
    (2026-09-23): a separate build after this one, started separately (2026-09-23).
    **CLOSED 2026-09-23 by the competitor intelligence build** (agents, checks and the
    user-approved pilot all done; gate report `docs/reports/competitor-intel-gate-report.md`;
    branch `competitor-intel`): five
    agents — `.claude/agents/bsuk-competitor-registry.md`, `.claude/agents/bsuk-competitor-intel.md`,
    `.claude/agents/bsuk-competitive-keyword-gap-agent.md`, `.claude/agents/bsuk-llm-keyword-intel.md`
    and `.claude/agents/bsuk-strategy-synthesizer.md` — and three scripts —
    `scripts/competitor_registry_check.py`, `scripts/gap_matrix.py` and
    `scripts/strategy_cite_check.py` (`npm run check:competitors` and `npm run check:gaps` are in
    `check:all`). The competitor pricing-alert agent stays deferred to project 6.

43. **Reddit-modifier pages are a recorded option, not built.** Short pages aimed at
    `"<keyword> reddit"` searches (the source repo's playbook). Decide with search-volume data
    in project 5 or later; the thread half is `.claude/skills/bsuk-reddit-threads/SKILL.md`.

44. **No page-communication audit.** The source repo's visual-intelligence skill (does the page
    communicate, what job is it doing, why do two pages feel the same) was deferred to project
    3 in project 2's manifest; project 3 shipped without porting it. The 28 city pages in
    project 5 are where it would pay.

45. **DataForSEO costs are unknown (2026-09-23).** The connector returns no cost field, so
    `data/queries/spend.json` holds conservative estimates ($0.20 for Manchester). The user is
    to check the DataForSEO dashboard for the real spend; then set `query_typical_call_usd` in
    `data/settings.json` from the real per-call figure.
    **Update (competitor intelligence build, 2026-09-23):** the dashboard read $0.99185 after
    the three calls above (about $0.008 real against $0.20 logged). By user ruling A,
    `query_typical_call_usd` is now 0.05 (`efdac63`); `ai_engines` still budgets at its logged
    0.10. The log stands at $0.80 of the $1.00 cap, all estimates, so the cap binds long before
    the real balance does. Stays open until the log records real costs or the cap is re-set from
    the dashboard.
    **CLOSED 2026-09-23 (project 5 readiness, Task F1).** The spend guard now reads the dashboard.
    `python3 scripts/query_augment.py --reconcile --balance <n> [--opening <n>] [--covers <n>]`
    appends a reading to `data/queries/dashboard.json` (append-only: date, balance, opening
    balance, and how many spend-log entries it covers — the whole log unless `--covers` says
    fewer). The guard counts the covered calls at their real cost (opening minus balance) and only
    later calls at their logged cost; the typical cost is the larger of `query_typical_call_usd`
    and the costs logged for that source after the reading. The first reading — $0.96785 left of a $1.00 opening,
    covering all 14 logged calls — puts real spend at $0.03215 against $0.80 of estimates: about
    $0.002 per Google SERP call and $0.004 per ChatGPT-scraper call.
    By the user's second option (Known Issue 58), `query_typical_call_usd` is now 0.01 (2.5 times
    the ChatGPT price, 5 times the SERP price); the $1.00 cap is unchanged.
    `python3 scripts/query_augment.py --budget <source>` prints what the guard counts, then
    "spend log holds N entries". Only the controller runs `--reconcile`, and only when the user
    reads the dashboard again; the agents never do. The controller's reading procedure: run
    `python3 scripts/query_augment.py --budget <source>` and note "spend log holds N entries";
    ask the user for the dashboard balance B and whether they topped up since the last reading;
    run `python3 scripts/query_augment.py --reconcile --balance B --opening O --covers N`, where O
    is the opening with every top-up included; read O back to the user. Calls made after the
    latest reading count at their logged cost ($0.01 each), and `--reconcile` refuses the latest
    reading's balance repeated after new calls ("read the dashboard again"), which would count
    those calls at nothing. It also refuses (exit 2, nothing written) a bad amount, a `--covers`
    out of range (below the last reading's or above the log's length), a reading dated before the
    last one, spend that would fall and a damaged file; `--balance`, `--opening` and `--covers`
    given without `--reconcile` are refused too. `data/queries/spend.json` is untouched and still
    holds the estimates as they were logged.

46. **CLOSED (project 5 readiness pass, Task R7) — city pages may state it, with the gov.uk row
    (user ruling R7).** The location template, the location builder skill and agent and the SEO
    checklist allow the one line — the Staffordshire Bull Terrier is not a banned breed in the UK,
    linked to https://www.gov.uk/control-dog-public/banned-dogs — and keep every other statute line
    `LEGAL_CLAIM_PLACEHOLDER`; `test_the_banned_breed_line_is_the_one_statute_line_a_city_page_may_state`
    in `tests/py/test_builder_skills.py` holds both halves. Was: **Needs a user ruling — the
    banned-breed line (2026-09-23).** The breed guide
    (`src/pages/uk-staffordshire-bull-terrier-guide/index.astro`) states the Staffordshire Bull
    Terrier is not a banned breed, backed by the gov.uk banned-dogs row in
    `docs/reference/external-link-library.md`. The city-page template
    (`docs/reference/location-page-template.md`) and the builders make every statute line
    `LEGAL_CLAIM_PLACEHOLDER`. **Closes with the user's ruling**: city pages may state it with
    that same gov.uk row, or the breed guide moves to the placeholder.

47. **CLOSED (project 5 readiness pass, Task D1) — the link guard reads `https:\/\/host` in a JSON string too.** Was: **The link guard misses JSON-escaped URLs (2026-09-23).** `scripts/competitor_registry_check.py`
    finds a tier-5 host in `src/`, `data/boards/` and the external-link library in every plain URL
    form, but not written as `https:\/\/host` inside a JSON string. None exists today. Fix when a
    JSON file under those roots first carries escaped links.

48. **CLOSED (project 5 readiness pass, Task D2) — an unwritable `--write` path is a message, a schema type that differs only in case gets a hint, and a backslash before a pipe is escaped.** Was: **`scripts/gap_matrix.py` minors (2026-09-23).** `--write` to a path that is a directory ends
    in an OSError traceback, not a message; a schema-type value differing only in case fails
    without a "did you mean" hint; a backslash directly before a pipe in a cell is not
    double-escaped by `_cell`. None affects today's matrix.

49. **CLOSED (project 5 readiness pass, Task D3) — a heading after `## Sources` is flagged, the Risks message names the rule, the Strategy A/B sections are checked, and a calendar year with no cue word gets a hint.** Was: **`scripts/strategy_cite_check.py` minors (2026-09-23).** a calendar year written with no cue
    word ("the <year> plan") fails as an unsourced figure — the synthesizer is told to put a cue
    before a year ("in <year>"); a `##` heading
    after `## Sources` is not flagged; the message for a figure under `## Risks` could name the
    rule more plainly; figures inside the Strategy A / Strategy B sections are not checked (only
    the pick is).

50. **CLOSED (project 5 readiness pass, Task D4) — the same-day `-2` proposal path, the hash-based change check, tier-5 notes, the `dbrg.uk` candidate (`docs/research/competitor-registry-candidates.md`) and the rank tracker's field.** Was: **Registry agent minors (2026-09-23).** The proposal-path pattern does not allow a same-day
    `-2` suffix; the same-day "registry changed" check compares dates only; a tier-5 edit keeps the
    old notes. `dbrg.uk` (cited in the Leeds answer, no registry id) is a candidate add for the next
    registry refresh. `.claude/agents/bsuk-rank-tracker.md` says it updates `last_monitored` in
    `data/competitors.json` — the schema has no such field (it has `last_analyzed`); fix when the
    rank tracker is rebuilt in project 6.

51. **CLOSED (project 5 readiness pass, Tasks E1–E4, and G1 for the two run-time items) — one whole-word page-type table, pagination left out, the key-page rule, the homepage measures by script, the image-name email fix, the BSUK location rows typed; trojanstaffuk's mobile check re-run as an emulated phone (the check now compares `clientWidth` with `screen.width` and needs proof of emulation — a controller amendment at Task E4) and RSPCA re-mapped in G1 (its Staffy advice page is still unanalysed: no fetch returned its URL — Known Issue 57). `--bsuk` cutting brand-name runs stays accepted.** Was: **Intel agent minors (2026-09-23).** Key-page tie-break when two pages tie; loosely defined
    measures (`reviews_shown`, `homepage_images`, `alt_text`, `steps_to_enquire`); id wording;
    substring page-type rows (`/careers/` reads as care-guide, `/preview/` as reviews); blog
    pagination URLs counted as posts; the BSUK city count includes the UK hub and the outreach
    page from `location-sitemap.xml`; an image name like `x@y.PNG` reads as an email; the
    trojanstaffuk mobile check used a desktop browser; the RSPCA Staffy advice page was not in the
    map sample; `--bsuk` cuts brand-name runs such as "blue staffy uk breeders" (accepted).

52. **CLOSED (project 5 readiness pass, Tasks E2, E5 and E6) — foreign-domain and duplicate URLs are flagged, "Greater Manchester" is Manchester, a two-city page gets each stub, off-list places stay out, and both agents read one page-type table with `comparison` first.** Was: **Keyword-gap minors (2026-09-23).** A report whose page URLs sit on a different domain from
    its `root_domain`, and the same URL in two reports, are not flagged; places not in
    `data/locations.json` (Scotland, Newcastle upon Tyne) drop out of topics; "Greater Manchester"
    is not read as a city topic (region words), so the pets4homes Manchester row is not labelled
    with the Manchester stub; a typed "-vs-" comparison is matched before intel's page-type table
    (`/blog/staffy-vs-pitbull` differs between the two agents); a two-city page gets no stub label.

53. **LLM-intel minors (2026-09-23) — CLOSED except two (project 5 readiness pass, Tasks C3 and E7–E11).** Fixed: one own-domain rule (E7); the homepage read, noindex in any attribute order, a stale build refused (E8); one location-question rule (E9); names with digits, inline labels, table-first answers, short separators (E10); `extra` recorded and the fixture's Instagram link gone (E11); `schemas/` in the system registry (C3); the Manchester format, measured once the answer was re-bought (G4, `bc8eec1`). Still open: every on-page check is provisional until project 5 builds the pages, and Manchester's normalised `data/queries/raw/blue-staffy-puppies-manchester-uk/ai_engines.json` still holds the old save until its project-5 build re-normalises it. The entry as it stood: The Manchester answer was re-bought verbatim at the user's
    `; refresh` (project 5 readiness, bc8eec1), so its format is now measured; the normalised
    `data/queries/raw/blue-staffy-puppies-manchester-uk/ai_engines.json` still holds the old save
    and needs re-normalising by `bsuk-query-augmentation` at Manchester's project-5 build; every
    on-page check is provisional until project 5 builds the pages; the output does not record the
    `EXTRA` string, so a re-run cannot reproduce an entity's variants exactly (the close-out
    re-derivation of Leeds patched only `local_businesses` for that reason); digits in a brand name
    read as a "statistic" opening; an inline bold label is not skipped; table-first answers and
    short separators; the synthetic fixture still holds an Instagram link; the own-domain logic
    differs between the script and `tests/py/test_llm_intel.py`; dist build freshness is not
    checked; the noindex regex assumes an attribute order; the homepage has no slug for llm-intel;
    `docs/reference/system-registry.md` does not list `schemas/`.

54. **Research notes for project 5 (2026-09-23).** The gap matrix's `cities` row counts a city
    merely named on a BSUK page ("Cities We Serve") as covered although its page is a noindex stub;
    the national phrase "staffordshire bull terrier puppies for sale" belongs on the listing page,
    not a city page; BSUK says "council-licensed" but shows no licence number — the claim stays
    `LICENCE_CLAIM_PLACEHOLDER` until the breeder confirms it; the Task 9 fixture BSUK profile marks
    London covered where the page map has a noindex stub.

55. **The former business street address is in `data/locations.json` (2026-09-23).** The migrated
    body HTML of `/uk-locations/staffy-breeding-dogs-glasgow/` (line 385) carries a map embed and
    title with the old street address and postcode — BSUK's own former address in the old city,
    not a third party's. The Known Issue 16 relocation applies: it must not be carried into that
    page's rebuild.

56. **CLOSED (project 5 readiness pass, Tasks A1, B6, C1 and C4) — every agent, skill and command names `docs/superpowers/sessions/`, one dead-root guard reads all three trees (`tests/py/test_rules_index.py`), WORKFLOW marks what was never ported and `check:workflow` holds its references, and the port-manifest notes match the repo.** Was: **Session paths and WORKFLOW leftovers (2026-09-23).** grill-me, session-closer and
    `bsuk-content-architect` now use `docs/superpowers/sessions/`, but 46 other agent and skill
    files still name a bare `sessions/` directory, which does not exist; grill-me and
    session-closer still say "Content root: `site/content/`". WORKFLOW still lists monitoring
    agents that were never ported (branded search, litter manager, review collection and others)
    without a marker, and its intel/keyword-gap handoff lines are looser than the agents' own.
    `data/port-manifest.json` notes on the framework, content-audit and rank-tracker rows still
    say `data/competitors.json` or competitor-intel is not ported / deferred, though both now exist.

57. **Intel on all 21 registry entries — CLOSED (project 5 readiness).** Every registry entry has a
    report in `docs/research/competitors/` dated 2026-09-25, run one id at a time in five batches
    (0–4): the three pilots (trojanstaffuk, pets4homes, rspca) were re-run first, because the rules
    changed after them (Known Issue 51), then the other 18. The key-page classifier was reworked
    during the run (4e2fe7f to 9d7e7b9): the breed's own pages first, one search map when the first
    map misses the breed, and rules for marketplaces, general classifieds and adverts. A consistency
    pass followed: six reports re-typed for free (8670a98) and six topped up (ca0c730). Firecrawl
    used 110 credits (776 to 666). The tier-5 entry (staffordshirebullterrierkennel) was fetched on
    its homepage only and is never linked. petsforlove.co.uk did not answer (ports 80 and 443
    closed), so its report is homepage-gated and every field is NOT FETCHED; the registry fix for
    `bsuk-competitor-registry` is to re-check the site or retire it. RSPCA's Staffy advice page is
    still unanalysed, because no fetch returned its URL. The BSUK profile was rebuilt with `--bsuk`
    (bb9dfc2) and the gap matrix rebuilt on all 21: in every row, measured plus not fetched is 21
    (136 keyword, 11 page-type, 25 city and 23 schema rows), and its `No report yet:` line is gone.
    The keyword gap (2049d6d, 20 reports; petsforlove has nothing to read) finds 16 gaps, 10 of them
    high. The strategy was re-synthesised (528e597, strategy Artifact version 2): the same bet,
    contested city pages first, in a new order led by London, Manchester, Liverpool, Essex and
    Dundee.

58. **LLM intel for the other 26 location pages — CLOSED (project 5 readiness).** Every location
    page has a `docs/research/llm-intel/` file: 26 new pages plus a Manchester refresh, 27
    ChatGPT-scraper calls through the spend guard in five batches (237b9e6, 0c0e5ee, 7255193,
    c3c83bf, bc8eec1). The user's dashboard reading was first re-recorded for 2026-09-25 (c13a807:
    still $0.96785, covering the 14 calls logged before). The guard now counts $0.30215 of the $1.00
    cap; the log holds each new call at the $0.01 estimate (real cost is about $0.004 a call) until
    the next reading (Known Issue 45). The question is `location_question()` in
    `scripts/query_augment.py`: the two national pages share one ("in the UK"), and the pages
    `staffy-breeding-dogs-glasgow` and `staffy-puppies-for-sale-glasgow` another ("near Glasgow"),
    each keeping its own file. Of the 26, the 15 stub pages are checked against the page map
    (provisional) and the 11 indexable pages against `dist/`; compare bands within one kind only.
    `bsuk_cited` is false in every file. The 27 domains the answers name with no registry id are
    listed in `docs/research/competitor-registry-candidates.md` (2d75ff4); they enter the registry
    only through a seed search and an approved proposal.

59. **Project 5 builder checklist (carried from Known Issue 40, project 5 readiness pass).** Clear
    each before or while the first city page is built:
    - 9 location rows have an empty `h1` (`data/locations.json`), so their primary-keyword source is
      undefined.
    - Later gate work: count built `dist/uk-locations/*` pages with no question file and print it; an
      optional per-page-type "must have a file" switch once project 5 covers all 28; check the visible
      FAQ questions come from the question file; an extra-section H2 must sit in a body section, not
      the frame; a heading-covered answer should stop at its section end.
    - Minors: lifespan source; `rules/copy.md` as a source; sem-all-six-levels is page-level;
      proximity and roads claims without a source; the former-city row (Known Issue 16) and the
      national rows compete; the blog builder's raw caps note; top-10 vs top-5.
    - Found by the readiness audit and not fixed there: WORKFLOW line 28 reads "latest session brief
      and UK city their default", a garbled replacement; `scripts/page_hardening_scan.py` (lines
      453–463) checks `heroPreload` props `BaseLayout.astro` does not have; IndexNow `--changed`
      diffs against `origin/main`, which cannot exist before project 6. (Two lines the audit found
      were fixed during the pass: `.claude/agents/bsuk-hub-builder.md` now says
      `/blue-staffy-uk-breeders/` is the About page and no comparison hub exists, and every commit
      example in an agent or skill carries the trailer — Task X3, guarded by
      `tests/py/test_commit_trailer_examples.py`.)

60. **The 28 city pages have no hero pool of their own (project 5 prerequisite). STOP before the
    first city board: the user decides.** Working rule 16 says no two pages share a hero or a
    counter, and `src/lib/boardStyles.ts` maps a `location` page to the `interior-guide` family —
    three heroes (H-GD1–3), all three now taken by the guides (Known Issue 35). Twenty-eight city
    pages cannot each have their own arrangement from three. `tests/py/test_rule16_gate.py` would
    catch the first shared pick on a record that names its `meta.layout_type`, and misses one that
    does not (the gate skips records with no layout family, a blind spot for exactly these
    records). **Needs the user's decision before the first city board**: a `location` family whose
    heroes vary per city by rule, an exemption for the location cluster by name as R12 gave the
    utility pages, or a design pass that gives the cluster its own pool. The same STOP line belongs
    in `.claude/skills/bsuk-location-page-builder/SKILL.md` (as Known Issue 39's STOP was); the
    readiness pass left that skill untouched at close-out, so project 5 adds the line before its
    first city board or the user's decision makes it moot.

61. **Where a rebuilt city page's source lives (project 5 decision).** Every city page is built today
    by `src/pages/uk-locations/[slug].astro` from its `data/locations.json` row (the migrated body).
    A rebuilt page needs its own board-driven source: a per-city `.astro` file, a record-driven
    branch of the dynamic route, or content files. Known Issue 39 left `scripts/pageboard.py`'s
    freshness and own-source lookups keyed to `src/pages/<slug>` for this reason.

62. **Comparison pages have no URLs and no hub yet (project 5).** `.claude/skills/bsuk-comparison-page-builder/SKILL.md`
    §1 says no comparison page exists and the project-5 plan fixes each slug on its board;
    `data/page-map.json` has none, and no hub page exists — `/blue-staffy-uk-breeders/` is the About
    page. The strategy's first comparison is the blue or black Staffy page; its slug, and whether a
    hub comes first, are the plan's.

63. **Pageboard freshness does not see a city page's sources (project 5).** `freshness_inputs()` in
    `scripts/pageboard.py` measures a page against `src/pages/<slug>/`, its record, the shared shell
    and top-level `data/*.json`. A city page's markup comes from `src/pages/uk-locations/[slug].astro`,
    which is not `src/pages/<slug>`, so an edit there does not make its built page read as stale
    (`data/locations.json` is covered by the top-level data files). Settle it with Known Issue 61.

64. **No gate measures rule 10 on a built page (found in the readiness pass).** `scripts/measure_canvas_heights.mjs`
    measures the heroes on `/kit-preview/` only; the rebuilt pages' heroes were measured by a scratch
    probe (readiness Tasks R3, R11, R13). It found two pages whose hero section box is shorter than its
    content at 1280, before and after the fonts: `/buy-staffy-puppies-for-sale-uk/` by 12px and
    `/buy-blue-staffy-puppies-uk/` by 5px — nothing runs into the next section, but the band is not
    held the way rule 10 says. Every other rebuilt hero held (at 1024 / 1100 / 1280: `/` 476 / 476 /
    450, the health guide 528 / 470 / 450, the breed guide 440 / 408 / 450, the buying guide 445 /
    445 / 411 with its chips, the about page 407 / 390 / 445). Twenty-eight city heroes are about to
    be built: the probe belongs in the render harness (or `scripts/measure_canvas_heights.mjs` given
    the rebuilt pages) before the first one.

65. **The older indexable location pages print retired terms — LIVE today; flag to the user
    (found in the readiness research).** Checked in `dist/` at close-out; every page below is
    `index, follow`. These are the migrated bodies in `data/locations.json`; every figure they
    print is RETIRED and none is a locked fact (the amounts are quoted, marked retired, in the gate
    report `docs/reports/p5-readiness-gate-report.md`; `docs/research/competitors/bsuk.md` found them):
    - a flat delivery fee (retired) on nine city pages: Aberdeen, Dundee, Edinburgh, Hull,
      Inverness, Middlesbrough, Oxford, Sunderland and York;
    - a puppy price band (retired) on Aberdeen, Edinburgh, the UK hub
      (`/uk-locations/blue-staffy-puppies-uk/`) and `staffy-breeding-dogs-glasgow`, and on Aberdeen
      and Edinburgh a price for each of the puppies they list (retired; those puppies are gone);
    - Hull calls the deposit "non-refundable" (retired wording);
    - the UK hub prints a deposit amount (retired), collection from the former city (Known Issue 16)
      and "council-licensed" (unconfirmed — Known Issue 54).
    The rebuilt pages carry none of these. Project 5 rewrites each body; until then they are live,
    indexable defects under the facts rules. **The user decides** whether to correct them now as a
    fix (not a page build) or leave them to the rebuilds; the strategy ranks Oxford and Sunderland
    mid-order, so waiting keeps them live for longer.

66. **Board records and board forms (project 5 readiness pass).**
    - **Refresh notes that describe another arrangement.** Many hero and counter `refresh` notes
      describe an arrangement other than the pick's current definition in `src/lib/boardStyles.ts`
      (`data/boards/index.json` lines 327 and 425, the health board's line 413, C-GD2, C-GD3,
      C-FS2, H-FS1–3, H-BL3, C-BL2). The notes were written in `ebfba87` and the styles redefined
      in `0062144` (2026-09-20, 21:15 UTC). Every approval on record is later than that commit (the
      earliest, 22:03 UTC the same evening; the rest 2026-09-22 and 2026-09-24), so no approval
      predates the redefinition by timestamp; whether each board shown then was built from the
      redefined styles is not proven by the timestamps alone. Rewrite the notes from the current
      definitions (re-approved as wording).
    - **Board forms need `autocomplete="off"`.** At the readiness pause the browser restored an
      earlier form choice and two saves were wrong: the health board first saved H-GD3 and the
      buying board C-GD3. The user re-approved both (H-GD1, C-GD2). Nothing in the form stops it
      happening again.
    - **`scripts/build_page_board.py` line 1003** compares the database's pre-approval hash with the
      page's `RECORD_HASH`; a board rebuilt after its approval, if republished, shows "an earlier
      version was approved". Embed the approval-time hash too and accept either.
    - `docs/reports/page-rebuilds-gate-report.md` line 124 says rule 16 is not fully met and has
      no gate: historical, as project 4 left it. Rule 16's gate now exists
      (`tests/py/test_rule16_gate.py`, `scripts/board_gate.py`, `scripts/board_approve.py`);
      the report stays as written.

67. **Health-test spelling needs the user's ruling (project 5 readiness pass).** The evidence
    ledger, `data/faq.json` and the boards write L-2-HGA and HC-HSF4; `rules/copy.md` writes L2-HGA
    and HC, and the location builder skill's test names were left as they are rather than split the
    vocabulary. **The user picks one spelling**; then the ledger, the FAQ rows, the boards, the rule
    pack and the skills move to it together.

68. **`data/faq.json` states two claims nothing proves (waits for the breeder's answers).** About
    ten rows say the parents are "certified clear" of L-2-HGA and HC-HSF4, and
    `home-health-guarantee` promises a "written health guarantee". The evidence ledger holds the
    DNA claim (`parents-dna-clear`) at `NOT FETCHED`, and `data/settings.json` `guarantee_days` is
    null. The instructions route around both (Known Issue 40), but the FAQ bank itself still
    states them, and the rows render on built pages. It closes with the breeder's answers to the
    question sheet (Known Issue 41: the DNA and guarantee questions): record the proof and
    `guarantee_days`, or reword the rows.

69. **Competitor-intel classifier and measure minors (found in the readiness research, G1).** None
    changes today's picks enough to re-run; each is for the next intel run.
    - The blog word list is written twice in `.claude/agents/bsuk-competitor-intel.md` (lines
      ~261–262 against the page-type table) and its dated pattern is picked by position: build it
      from one list.
    - A hyphenated blog folder (`/staffy-blog/<slug>/`) now counts 0 posts without `--post-folder`;
      the script could print a hint when such a folder exists.
    - Posts are undercounted where a site's article folders are missing from the map sample
      (staffie-owners' info guides, puppies' advice pages).
    - ukpets' post count includes sitemap `.xml` files and account and thank-you pages; the post
      rule should leave them out.
    - RSPCA's search map counted 11 PDF URLs as adverts (numeric ids in the file names): the advert
      test should skip `.pdf`. Its Cornwall city came from one rescue-dog page on a subdomain.
    - champdogs' `/litter/9716` (sold 2007) was a listing pick until the consistency pass: a 4-digit
      trailing id under a litter or advert folder should read as an advert.
    - The listing row matches "puppies" inside care-folder names (PDSA's `/puppies-dogs/`, which
      typed its breed page a listing and its listing count 181). Decide whether folder words count.
    - A `/tortoise-for-sale/` page can beat a dog page on a site that names no listed species;
      "american-bull-staffy" counts as the breed because it contains "staffy". Some final picks are
      narrow (preloved's search page, puppies' `/leek` page, gumtree's `/uk/nelson`), noted in
      their reports.
    - `council_licence_shown`: the consistency pass applied one rule — true only when a licence
      number or a named council is shown (bullscaff, freeads, pets4homes and puppies flipped to
      false) — but `.claude/agents/bsuk-competitor-intel.md` does not yet say so. Write the rule
      into the agent's trust row.
    - M2: `.claude/agents/bsuk-competitive-keyword-gap-agent.md` types pages by the page-type table
      alone, with none of intel's hub or breeds-folder overrides. Copy the overrides or document the
      difference.

70. **Generated images wait for the user's key (system gaps, 2026-09-24).** `google-genai==1.47.0` is installed and pinned, and the whole generate → approve → publish flow is tested on synthetic images. The one real smoke image (plan Task 11b Step 3) waits until the user sets `GEMINI_API_KEY` in `.env`. Until then, slots use an existing image or an infographic. The system Python is 3.9.6: google-auth warns that 3.9 is past end of life, and urllib3 warns that it was built with LibreSSL. Consider a newer Python before project 6.
71. **Organisation and regulation entities have no owner page (system gaps).** The 12 organisations and 6 regulations in `data/bsuk-ontology.json` have `owner_page` unset. The first project 5 page that makes one of them its subject should claim it at boarding.
72. **One research row in the link library (system gaps).** Only the PubMed Central copy of Pegram et al. 2020 could be verified with `curl`. The RVC VetCompass page blocks bots (403), so it needs a headless-browser check before it can be a row. The four-source-type rule does not need a research row.
73. **Committed board HTML lags the renderer (system gaps).** `docs/artifacts/boards/*.html` for the 12 built pages still shows the old block 5 graph and the old "7. Asset slots" title. The boards render correctly from `scripts/build_page_board.py`; republish them the next time any of them is touched.
74. **Small helper duplicates (system gaps).**
    - `slug_file` exists in `pageboard`, `image_candidates` and `ingest_image`; only the first validates.
    - `route_of` exists in `image_candidates` and `build_page_board`.
    - `image_candidates.py --write` writes `data/boards/candidates/` (arrives in the first `--write` run), which nothing reads, because the board recomputes candidates itself.

    Fold these together when one of them next changes.

75. **Keyword-gap, LLM-intel, strategy and spend-guard minors (found in the readiness pass).**
    - Keyword gap: `CITYISH` misses a heading with "near me", a county name (Merseyside), "0 ads"
      or "dogs", and the source's run-together "salein" breaks the Manchester match, so the London,
      Liverpool, Manchester and Dundee rows scored as word topics (the keyword-gap file says so).
      Consider normalising those words before the city test.
    - LLM intel: `ueniweb.com` (a hosted site builder) is missing from the platform list, so a
      ueniweb seller reads as a registry candidate rather than a platform note; `local_businesses`
      can hold breed clubs, rescues and adoption listings, and downstream must never count them as
      competitors (the strategy counts registry entries only); an entry whose only link is
      Instagram or wa.me is dropped whole, name and all — consider keeping the name with a null
      domain; county and region rows (South Yorkshire, Cornwall, Essex) ask "near <place>", where
      "in <place>" would read better (needs a county flag in `data/locations.json` and a ruling).
    - Strategy: `scripts/strategy_cite_check.py` checks that each figure appears somewhere in the
      sources, so it cannot catch a quote of a keyword-gap row that has since gone (the pilot
      strategy quoted one; the re-synthesis left it out). Matching quoted row labels against the
      source rows would catch it.
    - Spend guard: `test_the_committed_state_admits_the_26_remaining_city_calls` in
      `tests/py/test_spend_reconcile.py` reads the real spend log and dashboard; it passes today (69
      more calls fit) and will fail once fewer than 26 calls of headroom are left. Re-scope it to
      assert the committed state still obeys the guard's rules, not a fixed 26.

76. **Registry fix: petsforlove is down (found in G1, 2026-09-25).** petsforlove.co.uk did not
    answer (DNS resolves; ports 80 and 443 closed), so its report is homepage-gated with every
    field NOT FETCHED, it is left out of the keyword gap, and it counts as "not fetched" in every
    matrix row. `bsuk-competitor-registry` should re-check the site at its next refresh and retire
    the entry if it is still down. The 27 answer-named domains in
    `docs/research/competitor-registry-candidates.md` wait for the same refresh.

77. **Instruction lines and code comments the readiness pass left stale.** Each is a one-line or
    one-paragraph fix; none is load-bearing today.
    - `docs/reference/seo-rules.md` Rule 31 fixes four site-wide counters (one reads "Home-Reared in
      Carlisle") against working rule 16's per-page counters; Rule 32 still says "3× per page" and
      names the retired `src/components/ContactForm.astro`; the SEO checklist's Special Elements
      list still says "Contact/inquiry form (3 required per page — Rule 32)".
    - The fan-out category counts disagree: the SEO checklist's Step B lists 11 categories, its
      Step 3 twelve (one headed "Delivery/Delivery Keywords", a doubled word) and seo-rules Rule 56
      says ten.
    - The comparison skill's row 25 ("Final CTA + page-specific inquiry form + newsletter") against
      its §11.6 ("no second CTA band after it") and §13.6's newsletter placement.
    - Skill residue the agent residue list would catch: `framework-aida` recommends a milestone
      figure ("2,000+ families have done this") and an invented family story ("the Robertson
      family") as desire amplifiers; `bsuk-entity-agent`'s entity row "LICENCE_CLAIM_PLACEHOLDER
      permit, home-bred certificate"; `bsuk-page-hardening` cites `.egg-rail`, a source-repo class.
      The two residue lists (skills and agents) are still separate.
    - Code comments: `src/pages/index.astro` says the contact page and listing carry "the site's
      two" forms (four pages mount one each); `src/components/kit/Hero.astro` and
      `src/components/kit/TrustStrip.astro` call brass "3.1:1 on bone" (it is 2.1:1;
      `src/styles/tokens.css` is right).
    - `data/design/fonts.json`'s `_why` should say that the licence files under `/fonts/*` are
      cached as immutable with unversioned names, so a font update renames them too.
    - `scripts/build_plan_artifact.py` splits a plan into sections at every `##` or `###` line,
      inside code fences too, so a plan that quotes a report template splits mid-fence (240
      sections for this build's plan, against 84 with a fence-aware split). The plan Artifact was
      built with a fence-aware copy of the script kept outside the repo; the fix belongs in the
      script, with a test.

78. **Blog posts: template limits and two rulings (project 5, before the two new posts).**
    - `src/content.config.ts` globs only `**/*.md`, and `featured_image` is a bare string with no
      width, height or srcset; `[...post].astro` passes `Hero` only an image and its alt. A post
      cannot pass hero dimensions (the `img_dims` check blocks a string hero), use a `src/assets/`
      hero or mount kit components. Project 5 extends the collection (MDX and image fields) first.
    - **Ruling needed:** `rules/headings.md` asks for all six heading levels, five or more H5s and
      five or more H6s on every page, but `scripts/final_page_audit.py` `POST_EXEMPT_CHECKS`
      exempts collection posts (and `faqpage_present`). Exempt posts in the rule pack, or enforce
      it in the audit.
    - **Ruling needed:** the blog skill names a Person author; `[...post].astro` emits an
      Organization with `d.author`, and the only post's author is "Blue Staffy UK Team". Decide and
      align.

79. **Seven stub cities give the verbatim gate nothing to examine (project 5).** bristol-uk,
    for-sale-leeds, south-yorkshire, coventry-area, cornwall, essex and
    uk-staffordshire-bull-terrier-breeder have an empty migrated body at the frozen migration
    commit, so `verbatim --extract` finds 0 elements and `--check` passes having examined nothing.
    A stub city must stay out of the verbatim applies list (there is no verbatim set to keep), or
    the gate must print "stub — no verbatim set" rather than "0 problems". Also: `facts --extract`
    on an unbuilt city ends in a raw FileNotFoundError.

80. **DONE 2026-09-25 (close-out, the controller's) — the Artifact pages carry the builder's
    current script line.** The review-minors task changed `scripts/build_report_artifact.py`'s copy
    script (it now un-escapes `<\/script` before rendering or copying, `fce3070`), and that commit
    regenerated the Foundation gate report's HTML (`docs/artifacts/bsuk-foundation-gate-report.html`,
    one line); rebuilt again at close-out, it is unchanged. The breeder's question sheet
    (`docs/artifacts/bsuk-questions-for-lisa.html`) had not been regenerated; the close-out rebuilt
    it with Task R6's command (one line changed) in the commit that recorded the close-out's
    Artifact URLs, and the controller republished it at
    https://claude.ai/artifact/CvLPpj438KFNfJcFd9gFTH right after that commit, together with the
    gate report (https://claude.ai/artifact/YHsi2sEDq1uUpgYsQTjUdU). No Artifact URL for the
    Foundation report is recorded in the repo, so it had nothing to republish; a published copy,
    if one exists, is republished from the committed HTML.
