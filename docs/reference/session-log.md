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

Branch `answer-board` (worktree `/Users/apple/Downloads/BSUK-answers`), cut from `foundation` at `e9b3c1b`. Spec: `docs/superpowers/specs/2026-09-26-answer-board-design.md` (Artifact https://claude.ai/artifact/53L9VZvUS3Q4UfnqyDAYWV). Plan: `docs/superpowers/plans/2026-09-26-answer-board.md` (Artifact https://claude.ai/artifact/1RYiRJ7TKniXQBJCyyijhA). **The board: https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf** (published 2026-09-26 with `db` rules read/write `admin`, `comments`, `downloads`; Lisa's batch posted at version 1; a non-editor reads nothing).

What it added:
- **One standing board, "Questions for You"** (`scripts/build_answer_board.py` → `docs/artifacts/bsuk-answer-board.html`). Every batch of questions for the user is posted there; the user answers in place (text, or a choice plus a note; Not yet / Skip on every question) and presses **Send to Claude Code** per batch. Layout A: sticky progress rail, wide question column, a top bar on phones.
- **Batches live in the board's `db`**, written by Claude with the ArtifactData tool from `scripts/answer_board_batch.py`'s JSON (sheet parser `scripts/answer_sheet.py`), so posting never republishes the page. Answers save one document per question with a browser draft as backup; Send writes a snapshot and sends a short note (a comment is capped at 4 KiB) naming it.
- **The rule:** CLAUDE.md "Questions for the user — the answer board"; the procedure is `docs/reference/answer-board/README.md`. Lisa's 21 questions are the first batch (`docs/reference/answer-board/batches/2026-09-24-questions-for-lisa-bright.json`).
- **Any additional questions** (2026-09-26, branch `answer-board-extra`, merged `5f4a8c7`; board republished as version 2): one free-text section after the open batches where the user types extra questions or sub-tasks and sends them; saved as `drafts/additional`, sent as a snapshot `additional/s-…`; receiving is in `docs/reference/answer-board/README.md` ("Additional questions").

## Brief parity build (2026-09-26/27) — CLOSED ON THE BRANCH, merge waits for the user

This build closes the gaps that the parity audit of CAG's *Universal Page Build Brief* found before project 5 (26 sections, 423 items, 27 gaps, 2 decisions). It runs on the parity branch in worktree `/Users/apple/Downloads/BSUK-cag`, cut from `foundation` at `0454a96`. The branch's full name, the audit's and the plan's paths are given in the gate report, because the marker gate keeps the brief's file prefix out of `docs/reference/`.

- **Commits:** 83, `b99d7d6..5893869`, then the close-out's docs commit. Every one carries the Fable 5.1 trailer, and nothing is pushed.
- **Plan:** 28 tasks, replayed green by the controller before execution.
- **Gate report:** `docs/reports/brief-parity-gate-report.md` (Artifact: https://claude.ai/artifact/MiQXGY16rYKz1betiZR6q1).
- **Answer board:** https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf.

**Gates** (run by the controller at `5893869`):
- The build exits 0, and `npm run -s check:all` exits 0 on both runs.
- `python3 -m pytest tests/py -q -p no:cacheprovider` gives `6222 passed, 12 skipped, 1 xfailed` on both runs.
- `npm run test:render:meta` gives 415 passed and 38 skipped.
- `npm run test:render:pages` gives 57 passed and 3 failed. All three failures are the pre-existing NAV row on the UK hub (Known Issue 81).
- The zero-examined guard: 31 checks, none at zero.
- `scripts/rendered_changes.py` against `foundation`'s `dist/` reports 12 changed of 51, exactly the 12 rebuilt pages.
- `scripts/measurement_ledger.py brief-parity` exits 0, with none failed and none stale. M6, M8, M10 and M12 are empty because no project 5 page exists yet.

**Definition of done:** 29 rows, 24 PASS, 5 PASS-WITH-DEVIATION and 0 FAIL. The deviations are:
- the retired-facts allowlist is 61, not 48;
- `layout-h3-image-first` has never passed on a real page;
- Manchester's word target is NOT FETCHED and Leeds has no cache;
- the harden record is self-reported;
- the URL-family decision is not yet taken.

What it added, by wave:
- **Wave 1:**
  - the invented method label is gone and linted;
  - evidence budgets are per city, and the brand has a budget;
  - puppy cards carry the delivery line;
  - Rule 18 is a ceiling with no floor;
  - the perf gate uses a warm median of 5;
  - seven drifted instructions are pinned;
  - `global_cta` is wired (board answer (a));
  - new pages use the uniform in-body image box, with no blurfill bleed (board answer (a), plus the user's design-colour note).
- **Wave 2:**
  - `check:retired`;
  - every rebuilt page is a render target;
  - the page run ends in the zero-examined guard;
  - `check:boards`;
  - approval refuses a header collision;
  - `layout-h3-image-first` is retargeted to `.bl-img`, and a `promotions` record means four checks block new pages;
  - the hardening scope covers the city template, its data and the kit;
  - `scripts/rendered_changes.py` runs at every close, and IndexNow `--changed` reads it.
- **Wave 3:**
  - competitor page metrics and Rule 27's word target;
  - `scripts/keyword_metrics.py` (board block 4b);
  - geo-token and two-keyword-header checks;
  - the claim ledger inverted (`claim-unledgered`);
  - `check:barriers`;
  - `check:threads`.
- **Wave 4:**
  - `docs/reference/page-run.md`, guarded by `check:workflow`, with `impeccable`, `frontend-design` and `superpowers:verification-before-completion` mandatory on every page;
  - board block 0, the page intake (closes Known Issue 63);
  - `npm run gate:page -- <slug>`, which runs every page gate twice and diffs them, plus the run-twice rule;
  - `scripts/measurement_ledger.py`;
  - the URL-family decision `docs/research/2026-09-26-url-family-decision.md`.
- **Beyond the plan:**
  - Task 28a's whole-branch review fixes (`dd29aec`, `ee0bf14`, `0c7bf89`):
    - the global CTA's city lookup;
    - `gate:page`'s board and listed steps;
    - an entity-blocked board refuses approval;
    - the dirty-tree rule for build outputs and page dates;
    - the close order;
    - the grill-me route;
    - the builder gate lists;
    - a sweep from `npx astro build` to `npm run -s build`.
  - Task 26's review rounds (`fdc2222`, `677946f`, `769465d`).
  - Task 27's review (`c9ce585`).

The audit's live defects are all closed:
- **D1**, the invented method label: Task 1 (`4c921ce`, `90db8fd`, `1b148de`).
- **D2**, the city-term budget hard-coded to one city: Task 2 (`c6b0756`, `82ab14b`).
- **D3**, `global_cta` ignored: Task 7 (`fb32212`, `13623cf`), with the city lookup fixed in `dd29aec`.
- **D4**, puppy cards without a delivery line: Task 3 (`65ba9da`).
- **D5**, retired facts unswept: Task 9 (`d196042`, `7c270a5`, `eed8178`). It is closed as a failing gate. The 61 allowlisted offenders stay live until each page is rebuilt (Known Issues 65 and 82).
- **D6**, IndexNow blind to city pages: Task 16 (`dd3bd1e`, `57995dd`).

Answer board:
- Batch `2026-09-26-brief-parity-two-decisions-before-project-5` is answered (`ac01ec0`: q01 (a), where bleed uses the design colours and never grey or black; q02 (a)).
- Batch `2026-09-27-brief-parity-close-three-decisions-before-the-london-page` is posted (`5893869`) and **open**. It asks about the URL family, the comparison slug and the fallback word band.

**Open items:**
- Known Issues 81–92 are new.
- Known Issue 73 is extended, and Known Issue 63 is closed.
- The other open items are as the readiness pass left them.
- **Next:** read the open board batch, merge `--no-ff` into `foundation` after the user confirms, then start project 5, London first.

## London component design pass, Plan 1 (2026-09-27) — CLOSED ON THE BRANCH, picks with the user

Branch `london-components` (worktree `/Users/apple/Downloads/BSUK/BSUK-london`), cut from `foundation`
at `5b41cd5`. Spec: `docs/superpowers/specs/2026-09-27-london-component-design-pass-design.md`.
Plan: `docs/superpowers/plans/2026-09-27-london-component-design-pass.md`.
**The canvas: https://claude.ai/artifact/EHMKbn9kV3qcfJfPrJhhXN** (`db` + `comments`; picks in `picks/<component>`).

- **Variants:** 45 (15 components × 3) in `design/city-canvas/london/`, each designed with
  frontend-design and hardened with impeccable (`docs/research/london-components/hardening-log.md`),
  held by `npm run check:canvas` and `npm run test:render:canvas`.
- **Inputs:** the Playwright MCP captures (outside the repo) indexed in
  `docs/research/london-components/ideas-index.md`; the must-differ inventory
  `data/design/city-must-differ.json` (generated by `scripts/city_must_differ.py`).
- **Picks (`7e11cf8`):** all fifteen components picked, none marked for redesign, no notes —
  hero B, counter strip C, trust strip C, contents list C, desktop dial C, jump links A, key
  takeaways A, puppy cards B, tables A, video C, image and text C, reviews A, FAQ blocks A,
  newsletter A, contact form B (`docs/research/london-components/picks-2026-09-27.md`).
- **The user's rulings:** served alts stay exactly as served (only puppy facts change where
  needed); the puppies are 10 weeks old; the parents are Maggie and Jones on every page (`7ce341a`,
  superseding `5793200`); the £500 deposit comes off the puppy's price (`1367385`); a research board
  the user picks from comes before every page's outline, on every page (`4256934`, Task 12b).
- **Hero fix:** the photo paints first below 900px on every layout; `layout-hero-image-first-mobile`
  blocks on every page; eight frozen pages' phone heroes changed
  (`docs/research/london-components/hero-mobile-fix.md`).
- **City family:** Known Issue 60 closed — `location` maps to `city`; the rule-16 gate judges city
  picks across all fifteen components (`city_rule16_findings`).
- **Gates at close** (controller, at `4256934`): the build exits 0; `npm run -s check:all` exits 0
  twice (`board-gate: examined 12 rebuilt pages, 0 failed`); pytest `6322 passed, 12 skipped,
  1 xfailed` twice; `npm run test:render:meta` 424 passed, 38 skipped; `npm run -s check:canvas`
  45 fragments, 15 meta, 0 problems; `npm run test:render:canvas` 184 passed.
- **Learning loop (Task 13b):** `docs/reports/learning-loop-2026-09-27.md` classifies every escape
  of the brief-parity build and this pass. Its shortlist items 1 and 3–8 land on this branch as
  `harness: … (learning loop)` commits, and its two rework-ledger windows are appended to
  `data/quality/rework-ledger.json`. Item 2 (the face-in-crop check) goes to Plan 2.
- **Next:** Plan 2, written from the user's picks.

## CAG ports before the London page run (2026-09-29, Task 10c) — ON THE BRANCH

The user's ruling: six pieces the port manifest had deferred cross over before the London page
run. Each is re-based (method kept; routes, data files, scripts, rule packs and facts BSUK's own;
no price, deposit, delivery figure or guarantee length typed) and recorded `rebase` in
`data/port-manifest.json`. Commit `0a3c859`; tests `tests/py/test_cag_ports_10c.py`.

- `.claude/skills/bsuk-visual-intelligence/SKILL.md` — the page-communication audit (Known Issue 44); page-run rows 16 and 20.
- `.claude/agents/bsuk-external-link-agent.md` — the external link library, six links on six domains from four source types, Link-First, live-checked; page-run row 9.
- `.claude/agents/bsuk-entity-incorporation-agent.md` — the 4-Move Loop on the ontology and the evidence ledger; page-run rows 7 and 9 (and `rules/copy.md` `entity-4-move-loop` names it again as the active engine).
- `.claude/agents/bsuk-coat-variant-builder.md` — coat-colour comparison pages with the shared coat table and cross-link block, to the `bsuk-comparison-page-builder` blueprint; page-run row 12.
- `.claude/agents/bsuk-scam-trust-agent.md` — UK puppy-scam fears answered with checkable proof only, no licence detail; page-run row 12.
- `.claude/agents/bsuk-video-seo-agent.md` — the site side of video SEO for the `youtube_embeds` ids; the channel is never touched; page-run row 12.

## London component design pass, Plan 2 (2026-09-28/29) — the picks built; side-by-side confirmed 2026-09-29

Branch `london-components` (worktree `/Users/apple/Downloads/BSUK/BSUK-london`). Spec: `docs/superpowers/specs/2026-09-27-london-component-design-pass-design.md`. Plan: `docs/superpowers/plans/2026-09-28-london-component-build.md`. Side-by-side: https://claude.ai/artifact/EPtLABruWw8yjBwFj5skf6. The user answered "All fifteen match" on 2026-09-29 (`docs/reference/answer-board/answers/2026-09-29-london-side-by-side-confirm-the-match-and-seven-decisions-2026-09-29.md`). Merging into `foundation` waits for the user's word.

- **Frozen:** `data/design/city-picks/blue-staffy-puppies-london.json` (15 picks, from the 2026-09-27 Send) and `data/design/city-pool.json` (the 30 unpicked); the canvas rebuilt `--final` and republished; the city gate green on the real files.
- **Built:** fifteen kit components, each named for its variant (`CityHeroFilmstrip`, `CityPriceScale`, `CityTrustLedger`, `CityContentsPhotoIndex`, `CityDialPhotoMarker`, `CityJumpStepper`, `CityTakeawaysLedger`, `CityPuppySheet`, `CityRoster`, `CityVideoPanel`, `CityChapters`, `CityLetter`, `CityFaqLedger`, `CityNewsletterNotice`, `CityContactLineup`), with `"project": 5` rows, on `/kit-preview/city/`. They read the data files through `src/lib/cityKit.ts`, and every crop comes from `data/image-focus.json`. The in-body components are containers. `npm run test:render:city` paints them at 375/768/1024/1280.
- **The city shell:** the nav set plugs in through `src/layouts/CityShell.astro` and its named slots, not through a PageShell prop.
- **The city type scale:** `src/styles/city.css` sets the type scale per tier from each section's own box. The `city-type-fit` gate in `tests/render/city-kit.spec.ts` holds heading caps and lines, the 75ch measure, paragraph length and section height, with its own known_broken and known_good fixtures.
- **Dates:** the date generator was hardened (Known Issue 94, closed in `7488a3c`). It now dates data rows by their own history, has a fan-out guard, and keeps a published floor.
- **Face check:** `img-face-visible` (advisory), learning-loop item 2; `no-head-cropped-portraits` is tested (Known Issue 92).
- **Scaffold:** `src/pages/uk-locations/blue-staffy-puppies-london.astro`, noindex and out of every sitemap. `[slug].astro` and the date map skip a city with its own file. It carries placeholder copy only; London's page run starts at its research board.
- **Chain:** `check:canvas` is in `check:all`.
- **Task 10b, the seven rulings (answer board, 2026-09-29):** keep the four photo swaps, and a repeated photo gets a new alt (q02); the jump band slides away while scrolling down and returns on scrolling up (q03); keep the price scale's tablet layout (q04); hide the contents list from 1024px (q05); widen the takeaways heading column (q06); the guarantee is two years (q07); pages say "10 weeks old", with no date of birth (q08). The guarantee corrections on the built pages are Known Issue 95.
- **Task 10c, six CAG ports:** see the entry above; Known Issue 44 is closed in `0a3c859`.
- **The outline-first rule (the user's ruling, 2026-09-29):** the user sees the research, the research board and the full outline (every H2 and H3 with its keywords, word count and purpose) before any component is selected or built. A city's component pass comes after the outline, and only for the sections it needs. For London, the built kit is a menu: the outline decides the sections, and the board maps each section to a component. It is written in `docs/reference/page-run.md` rows 8–10 (a hold before row 10, so the stops stay three), `rules/gates.md` `outline-before-components`, `data/quality/rule-index.json` (84 rules) and CLAUDE.md's project-5 paragraph, and pinned by `tests/py/test_outline_first_rule.py`.
- **Design passes at close:** `impeccable:impeccable`, then `frontend-design:frontend-design`, on `/kit-preview/city/` and the scaffold at 375/768/1280. They changed nothing (`docs/research/london-components/hardening-log.md` `## Plan 2 — close`).
- **Found at close, not fixed:** headings at body size on the built pages (Known Issue 97, awaiting the user's preview); the health page's findings (Known Issue 98); the `sizes` parse (Known Issue 96).
- **Lisa questions (posted, not yet answered):** batch `2026-09-29-lisa-bright-five-facts-before-the-london-page` (`8a7d787`) asks her five things: 1, whether she holds the DNA certificates for Maggie and Jones (Known Issue 98); 2, what the two-year guarantee covers (Known Issue 95); 3, whether she offers a live video call before payment; 4, how the £500 deposit is paid; 5, whether the take-back promise is in the sale contract. Questions 3–5 feed the scam-advice, safe-payment and trust copy of the buy and city pages.
- **Gates at close:** the build exits 0; `npm run -s check:all` exits 0 twice with identical examined lines (`board-gate --all: examined 12 rebuilt pages against 51 live pages; 0 failed`, `check-city-canvas london: examined 45 fragments, 15 meta files; 0 problems`); pytest in two halves, twice: 6759 passed, 12 skipped, 3 xfailed both times; `npm run test:render:meta` 442 passed, 38 skipped; `npm run test:render:canvas` 184 passed; `npm run test:render:city` 34 passed, 18 skipped (`city-type-fit` examined 104–123 per width on each route; `city-layout-follows-box` examines 0 at 375 by design, where the check holds no phone facts, and 10–15 above); `npm run test:render:pages` 57 passed, 3 failed: the three inherited Known Issue 81 rows, `uk-locations/blue-staffy-puppies-uk` `nav-jump-target-lands` at 375/768/1280 (`#Staffy-adoption` lands outside the band), not fixed here; `img-face-visible` examined 210 photographs with one advisory (the homepage's Maggie tile at 1280); `python3 scripts/generate_page_dates.py --check` current (55 routes); `python3 scripts/build_system_registry.py --check` 0 problems; the render baseline regenerated and the 2026-09-29 scorecards committed.
- **Next:** London's page run (`docs/reference/page-run.md`): the research board first, then the outline shown to the user, then the board mapping the outline's sections to the kit. The picks go on the board with real copy. Merge into `foundation` when the user says.

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
location-page remainder; and added 59–69 and 75–80. The system gaps bridge build added 70–74. The brief-parity build closed 63, extended 73
and added 81–92.
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
    row (the second bullet below) stays **build 5**'s. Re-measured at the brief-parity close (2026-09-27): now
    Known Issue 81.
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

44. **No page-communication audit. CLOSED in `0a3c859` (Task 10c, 2026-09-29).** The source repo's visual-intelligence skill (does the page
    communicate, what job is it doing, why do two pages feel the same) was deferred to project
    3 in project 2's manifest; project 3 shipped without porting it. The 28 city pages in
    project 5 are where it would pay.
    **Closed:** ported as `.claude/skills/bsuk-visual-intelligence/SKILL.md`, written against a
    baseline test, and run at `docs/reference/page-run.md` row 16 (after the static scan, before
    or with the AEO pass of row 20). See "CAG ports before the London page run" above.

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
    **Decided and built (2026-09-27):** the user chose a component design pass per city (answer
    board q01 (c)). `src/lib/boardStyles.ts` maps `location` to a seventh family, `city`, that
    cuts no hero or counter trio; each city's fifteen component picks are saved in
    `data/design/city-picks/<slug>.json`, and `scripts/pageboard.py` `city_rule16_findings`
    (called from `rule16_findings`, so the board gate and approval both apply it) refuses a pick
    another city wears, one within one structural axis of another city's pick, or one within
    one axis of an arrangement a built page wears. Unpicked variants go to
    `data/design/city-pool.json`. Tested by `tests/py/test_city_uniqueness_gate.py`. London's
    picks are the first entries (Plan 2 of the London component design pass).

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

63. **CLOSED (the brief-parity build, Task 24) — `freshness_inputs()` in `scripts/pageboard.py`
    now counts every `[...]` route file in a nested page's parent directory, so an edit to
    `src/pages/uk-locations/[slug].astro` makes a city page's built file read as stale; the page
    intake (`scripts/page_intake.py`, block 0 of the board) reports that freshness, and
    `tests/py/test_page_intake.py` holds both.** Was: **Pageboard freshness does not see a city
    page's sources (project 5).** `freshness_inputs()` in
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
    **2026-09-27 (brief-parity build, Task 9):** `npm run check:retired` (in `check:all`) now fails
    on any new offender in `data/`, `src/` or `dist/`. The live ones are allowlisted (61 entries)
    and burn down page by page (Known Issue 82).

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
73. **Committed board HTML lags the renderer (system gaps).** `docs/artifacts/boards/*.html` for the 12 built pages still shows the old block 5 graph and the old "7. Asset slots" title. The boards render correctly from `scripts/build_page_board.py`; republish them the next time any of them is touched. **2026-09-27 (brief-parity close):** still stale. The Task 19 review measured about 1.5k lines of drift against the current renderer. The boards were not regenerated at this close, and no approval changed. Regenerate and republish a board when its page is next touched, and check that its `approval` is unchanged.
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

81. **The UK hub's in-page anchor misses the landing band (the brief-parity close; carries Known Issue 31's second half).**
    - **Where:** `npm run test:render:pages` fails `nav-jump-target-lands` on `uk-locations/blue-staffy-puppies-uk` at all three widths: `[NAV] 1 of 2 in-page links land outside` the band, first `#Staffy-adoption` at 2847px (375), 3495px (768) and 3493px (1280).
    - **Why it matters:** these are the only rows keeping the page run from a clean exit (ledger M3 blocking 3). The migrated body's anchor target sits outside the band that the sticky header leaves.
    - **Next:** project 5's hub refresh rebuilds the body and its anchor target, and the render run must then exit 0. Do not fix it inside another task (plan execution note 8).
82. **Burn down the retired-facts allowlist, city page by city page (the brief-parity build, Task 9; Known Issue 65).**
    - **Where:** `data/quality/retired-facts-allowlist.json` holds **61** entries on 11 pages. The pages are the UK hub, `staffy-breeding-dogs-glasgow`, Aberdeen, Dundee, Edinburgh, Hull, Inverness, Middlesbrough, Oxford, Sunderland and York; the entries cover both `data/locations.json` and `dist/`.
    - **Why it grew:** the plan froze 48. The Task 9 review rounds widened detection to 'to' ranges, unprefixed ranges and former-home claims, so the list went 48 → 57 (`7c270a5`) → 61 (`eed8178`).
    - **What the gate does:** `check:retired` fails on any new offender and on any stale entry, and `tests/py/test_retired_facts_check.py` pins the ceiling.
    - **Next:** each rebuilt city page deletes its own entries in its build commit, because a rebuilt page left on the list fails the gate. The terms stay live on those indexable pages until then (Known Issue 65's decision).
83. **The four new-page promotions stay scoped to new pages (the brief-parity build, Task 14).**
    - **Where:** `tests/render/targets.json` `promotions` gives `layout-h3-image-first`, `layout-hero-counter-separation`, `sem-section-opening-paragraph` and `sem-title-case-headings` the scope `new-pages`. They block a project 5 page from board approval on, and they stay advisory on the frozen and migrated pages.
    - **Why:** `layout-h3-image-first` has never passed on a real page, and its reports on the frozen pages are true reports (Known Issue 90).
    - **Next:** widen any of them to `all` only after one full project 5 cluster runs clean with `false_reports` 0. The first page builder confirms a `BodyImage` after every H3.
    - **Keep in sync:** `approvedBoards` (TypeScript) and `approved_boards` (Python) both treat any truthy `approval` or `approval_previous` as approved. If the board's definition of "approved" changes, update both, because the parity test compares only the two with each other.
84. **Leeds has no competitor HTML cache; Manchester has no word target (the brief-parity build, Task 17).**
    - **Leeds:** `data/queries/raw/blue-staffy-puppies-for-sale-leeds/competitors.json` lists 8 pages with no `metrics`. The gitignored cache `data/queries/cache/` holds Manchester only, so `--competitor-metrics` had nothing to backfill.
    - **Manchester:** its 8 pages are measured, but all 8 are marketplace listings or blocked, so Rule 27's `word_target` is NOT FETCHED. Many city searches will look the same.
    - **Next:** Leeds's page run re-fetches its pool with `--extract-h2`, which saves the cache and the metrics. A city whose target stays NOT FETCHED takes the fallback band that the user picks (Known Issue 85).
85. **Three decisions on the answer board before the London board (the brief-parity close).**
    - **Where:** batch `2026-09-27-brief-parity-close-three-decisions-before-the-london-page` (`5893869`, https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf) is open. It asks:
      - q1: the URL family for the 28 city-cluster pages (`docs/research/2026-09-26-url-family-decision.md`; recommended (a): keep every slug, add no redirect, keep both intent pairs);
      - q2: the first comparison page's slug (recommended (a) `/blue-and-black-staffy-uk/`);
      - q3: the fallback word band when the competitor median is NOT FETCHED (recommended (a) 1,500–2,000 words).
    - **Next:** read the answers before the London board and apply them where each question says: city boards' `meta.slug` and `data/redirects.json`, the comparison board, and each city board's word target.
86. **The UK hub's body does not link the 9 indexable city pages (the brief-parity build, Task 27 review).**
    - **Where:** on the 2026-09-26 build, `uk-locations/blue-staffy-puppies-uk` links 18 of the other 27 location pages from its body. It misses Aberdeen, Dundee, Edinburgh, Hull, Inverness, Middlesbrough, Oxford, Sunderland and York, which only the header and footer city list reach (`docs/research/2026-09-26-url-family-decision.md`).
    - **Next:** the hub refresh links all 10 other indexable pages from its body, whatever the URL-family answer.
87. **The city template bypasses `PageShell`, so `global_cta` cannot reach a city page (the brief-parity build, Task 7 review).**
    - **Where:** `src/pages/uk-locations/[slug].astro` uses `BaseLayout` and the legacy `SiteFooter`, which never had the CTA band. `search`, `board-preview` and `kit-preview` also bypass `PageShell`.
    - **Next:** project 5's city template (Known Issue 61) moves to `PageShell`, so the board's `global_cta` applies. Check the footer spacing without the band in the page's impeccable pass.
88. **Hardening debt: 369 pre-existing `header-not-title-case` ERRORs (the brief-parity build, Task 15).**
    - **Where:** `python3 scripts/page_hardening_scan.py` (2026-09-27, report-only) gives `369 ERROR · 35 WARN`. The 369 split into board-preview 306, uk-locations 41 (the legacy city FAQ H3s), kit-preview 19 and available-puppies 3.
    - **Why it matters:** `npm run gate:page -- <slug>` runs the scan with `--fail-on-error`, so it fails on any legacy city page until project 5 rebuilds it. That is expected, not a gate fault.
    - **Advisory kit WARNs, unverified:**
      - opacity .85 on `SiteFooterKit` `.tag`, `.plain` and `.legal` and on the testimonial (contrast unmeasured);
      - `Hero.astro` `.ticks` `align-items`;
      - a `Button.astro` `kit-btn` false positive (a JS const the scan does not read).
    - **Next:** each city rebuild clears its own rows. The board-preview demo rows need a decision: exempt the route, or title-case the demo.
89. **Evidence debt on migrated and frozen pages; the ledger's `dna-clear` row also matches PHPV (the brief-parity build, Task 20).**
    - **Where:** `python3 scripts/evidence_audit.py --all` (2026-09-27) exits 1 with `examined 61 pages; 42 problems (192 WARN)`. The 42 ERRORs are term budgets on migrated pages. 133 of the WARNs are `claim-unledgered` (kc-registered 54, health-tested 28, vet-checked 27, dna-test 22, dna-clear 2); the Task 20 run counted 222 before its review narrowed the patterns. `check:all` does not run this audit, and `gate:page` fails only a new page on it.
    - **PHPV:** the `dna-clear` pattern in `data/quality/evidence-ledger.json` also matches "clear of PHPV", so a PHPV claim binds to `parents-dna-clear`. That row's proof covers L-2-HGA and HC-HSF4 only (PHPV pending, Known Issue 68).
    - **Next:** narrow the pattern, or add a PHPV row when the breeder answers. Each rebuild clears its page's budget and claim rows.
90. **Frozen-page debt: H3 image-first and the opening copy (the brief-parity build, Tasks 14 and 18).**
    - **H3 image-first:** the 2026-09-27 scorecards carry advisory `layout-h3-image-first` reports, where prose comes before the photo. Per viewport: the buying guide 7, the breed guide 2, the for-sale page 1 and the homepage 1.
    - **Opening copy:** `scripts/keyword_metrics.py` finds the primary keyword missing from the first 100 words on 11 of the 12 frozen pages (only `blue-staffy-pup-sale-uk` has it), and the title does not front-load it on 6.
    - **Title gate slack:** a title such as "Blue Staffy Puppies | BlueStaffyUK Manchester" passes, which is brand before city (Rule 21) and would need its own check.
    - **Next:** these pages keep their contracts (`BUILT_BEFORE_SYSTEM_GAPS`). Fix them only when a page is next re-boarded.
91. **The harden passes are self-recorded (the brief-parity build, Task 25).** `data/page-runs/<slug>.json` records the `impeccable`, `frontend-design` and verification passes, and the operator writes it. It is an honour system.
    - **What the gate does:** `gate:page` forces a re-record after any later page change and re-runs `check:all` itself rather than trusting the record's exit codes.
    - **Next:** the controller spot-checks that each record's widths and findings match a real run (screenshots at 375/768/1280) before a page is called done.
92. **M18: 17 of 81 rules in the rule index are untested (the brief-parity ledger).**
    - **The rules:** `design-context-read-first`, `entity-4-move-loop`, `header-style-declared`, `image-keyword-distribution`, `link-first-anchors`, `meaningful-words-no-stop-words`, `no-credential-in-a-committed-file`, `no-head-cropped-portraits`, `puppies-extended-meta`, `read-card-thumb-is-target-hero`, `release-guarded-publication`, `reuse-every-image-and-video`, `same-content-on-redesign`, `src-pages-is-deployed`, `verify-the-gate-first`, `visual-companion-always` and `visual-first-workflow`.
    - **Next:** the ledger reports the count at every close. Give a rule a test when a project 5 page first exercises it; `link-first-anchors` can ride along with the first city page (the audit's "Adopt later").
    - **2026-09-27 (London branch):** `reuse-every-image-and-video` is now `enforced: test` for its alt half (`tests/py/test_served_alt_preserved.py`, learning loop shortlist #1), so 16 are untested.
    - **2026-09-28 (London Plan 2):** `no-head-cropped-portraits` is now `enforced: test` (`tests/render/checks/img.ts::img-face-visible`, advisory; face boxes in `data/image-focus.json`), so 15 are untested.
    - **2026-09-29 (Plan 2 close):** the index grows to 84 rules with `outline-before-components` (`enforced: test`, `tests/py/test_outline_first_rule.py`); still 15 untested.
93. **What the learning-loop checks found on arrival (London branch, 2026-09-27; reported, nothing edited).**
    - **Served alts re-described (`tests/py/test_served_alt_preserved.py`, blocking, counted in `KNOWN`):** four hero-mosaic tiles give a served file a new alt while the same file's body instance keeps the served one — `blue-staffy-pups-near-you.webp` and `blue-staffy-puppy-delivery-uk.webp` on `buy-blue-staffy-puppies-uk`, `breeder-sitting-blue-staffy-puppy-home.webp` and `playful-blue-staffy-lawn-uk.webp` on `blue-staffy-uk-breeders`. Real under working rule 11's letter; the user's ruling decides whether the tiles take the served alt or `alt=""`.
    - **Upscaled images (`img-not-upscaled`, advisory):** 145 instances on all 12 rebuilt pages (20 of 36 page × viewport runs; content-box measure, 2026-09-28) — e.g. `blue-staffy-health-uk`'s 500px in-body files painted 874px wide at 1280 — and 4 on the London canvas (hero c at 1024/1280, tables b and contact-form c at 768). Hero c, tables b and contact c were not picked.
    - **Gates that pass on zero input by design (conditional strict xfails in `tests/py/test_gates_refuse_nothing.py`):** `check:outline` and `check:queries`, which judge only project 5 pages and examine 0 today. The xfail holds only while no approved new-family board exists in `data/boards/` (`family_rules.is_new_page`); the first approved city board lifts it, and both gates must then refuse zero input.
    - **Ruling on the four tiles (the user, 2026-09-28):** leave them exactly as they are. Restoring the served alt made each tile share one alt with the same file's body copy, which `board_gate` fails under Rule 50b (`asset-alt-duplicate`), and the user chose to keep the live alts over emptying them. The four stay in `KNOWN` as a permanent, counted exception.
    - **Faces (`img-face-visible`, advisory, 2026-09-28; re-read at the Plan 2 close, 2026-09-29):** one on the twelve built pages — `index` at 1280, `maggie-blue-staffy-dam-with-pups` 77% painted in a 182×189 tile (210 photographs examined across the page run). Four canvas variants: `key-takeaways/a` (Maggie, 78%) and `faq-blocks/a` (Maggie, 85%) at 768, `reviews/b` (Vennie, 68%) at 768, 1024 and 1280, and `video/c` (Christa, 11% under the play overlay) at 375. `key-takeaways/a` and `faq-blocks/a` are London picks, but the built components carry other photos there, so their canvas advisories do not reach the build. On the built city routes (`/kit-preview/city/`, `/kit-preview/city-page/`, the London scaffold) the owner photo `blue-staffy-testimonial-london-happy-owner` is 89–90% painted in the FAQ rail at 768 and 1024. Reported, not edited.
    - **Next:** the upscaled files are Plan 2 / page-refresh work (a larger source beside the served one, working rule 11); the two xfails lift when the first new-family board is approved.
94. **False freshness from a template refactor; a moved route's `datePublished` (London branch, Plan 2 Task 8 spec review, 2026-09-28). CLOSED in `7488a3c`.**
    - **The gap:** `scripts/generate_page_dates.py` dated a template-built page by every commit on the template. Task 8's own-file skip in `src/pages/uk-locations/[slug].astro` (`6520267`) changed no other city's output. It still moved `dateModified` to 2026-09-28 for the template cities in `data/page-dates.json` (`a3dd9f9`), and `BaseLayout.astro` emits that date in its own WebPage node. The same run moved London's `datePublished` from 2026-09-16 to 2026-09-28 when its route left the template for its own file, though the URL has existed since the migration. The escape shows the same defect had already happened once. `/blue-staffy-blog-guides/` carried `datePublished` 2026-09-16 in every committed map until its file was recreated on 2026-09-21, and it then showed 2026-09-21.
    - **The fix (the generator, test first):** `data/page-dates-ignore.json` lists a commit with the source paths it is ignored for and a reason. Listing a commit is allowed only after the built pages it touched were diffed against the build before it. The ignore is per path, because `6520267` also created London's own file, and that date is real. Separately, a route's `datePublished` never moves later than the earliest value any committed `data/page-dates.json` gave it. Tests: `tests/py/test_page_dates.py` (ignore list, per-path, publication floor) and `tests/py/test_city_scaffold.py::test_london_keeps_the_date_its_url_was_first_published`.
    - **After:** the 27 template cities are byte-identical outside `<style>` to the `86632ce` build, with Aberdeen at 2026-09-16 / 2026-09-16. London reads 2026-09-16 / 2026-09-28. `/blue-staffy-blog-guides/` (and the `/blog/` copy of its node) reads `datePublished` 2026-09-16 again.
    - **Next:** any commit that changes a template, layout or data file without changing the words, facts or images of the pages it builds belongs on the ignore list. It is added in the same task, after the diff.
    - **Known gap, seen again (2026-09-29, answer board q01, `5160742`):** a kit component dates no page. The kit TrustStrip's default line changed ("results on request" → the tests named), and `/uk-blue-staffy-breeders-contact/`, which renders that default, changed with it without its `dateModified` moving; the pages that changed through their own files were re-dated. The `fanout_accepted` reason for `5160742` names it. The structural fix is the per-route content hash planned above.
    - **The floor is one-way (quality review, M3).** Once a committed map has carried a date, no later run moves that route's `datePublished` later. If an old map got a date wrong, correct it with a `floor_override` entry (route → `datePublished` + `reason`) in `data/page-dates-ignore.json`, or correct the old map entry in a new commit of the map, never by rewriting history. Ignore SHAs must resolve to exactly one commit (`git rev-parse --verify`, 7+ characters, compared in full). A missing or ambiguous SHA, or a malformed file, stops the date step with exit 2.
    - **Fan-out guard (Task 8b).** A no-content commit to a shared source re-dated every route it builds three times on this branch (`6520267`, `c2705da`, `142b3d6`); each was caught only by review. `scripts/generate_page_dates.py` now compares the new map with the committed `data/page-dates.json` at HEAD. When one commit moves `dateModified` on 3 or more routes and is listed in neither `commits` (no content changed; the dates stay) nor `fanout_accepted` (every page's content really changed), the write, `--dry-run` and `--check` all refuse with exit 1. The refusal names the commit, the source and the routes, and says to diff the built pages first.
    - **Grouped by commit, and data rows dated by their own history (Task 8b review, B1 and B2).** The first guard grouped by commit and source, so one commit that edited three pages' own files made three groups of one and passed. It now groups by commit alone and lists the sources. A data-driven route (a city in `data/locations.json`, a puppy in `data/puppies.json`) is dated by the commits that changed ITS OWN ROW, matched by slug and compared as canonical JSON, read through one `git cat-file --batch`. A real edit to one city's row re-dates that city alone, and a reorder or reformat re-dates nothing. A route re-dated by its own row is never refused, because its own content changed. The template stays a shared source and is still guarded; on a tie the shared source takes the blame. Still open: a hand-regenerated map committed together with the refactor passes, because the guard compares with HEAD (the reviewer's probe, case h). The content hash below closes that too.
    - **Rows: rendered keys, the same bar, real parents (Task 8b re-review, N1, N2, M1–M3).**
      - **Rendered keys only:** a row is compared by the keys its template renders (`RENDERED` in the generator, pinned by a test to the keys each `[slug].astro` reads). `defects`, `word_count` and `canonical` never date a page.
      - **Same fan-out bar:** row re-dates are grouped by commit under the same bar as shared sources. A commit that changes rendered keys on 3 or more rows needs a `fanout_accepted` entry, or the date step refuses. A one-row or two-row edit simply re-dates those pages.
      - **Real parents:** each commit's rows are compared with its real parents, read through the same `git cat-file --batch`. At a merge, a row counts as changed only when it differs from every parent, so a merge no longer gives a branch's untouched rows its own date.
      - **Unparseable versions:** a version that does not parse is skipped, and its parent's rows carry through.
      - **Duplicate slugs:** a duplicate slug in a data file stops the step with exit 2 and one sentence.
      - **Publication date:** a data route's `datePublished` is its row's first appearance, and the committed-map floor still applies.
    - **Own-file pages read their row too (Task 8c).** A page with its own file for a data row, such as London's scaffold, which renders `loc.title`, `loc.description` and `loc.body_html`, is now dated by its file and by its own row, compared on the same rendered keys. `selfDated` still comes from the page's own file. Its `datePublished` is the row's first appearance, the day the template first built the URL. The rendered-key pin test reads every page that renders a row: each `[slug].astro` and each own-file page. It follows `const { … } = loc` destructures and fails, naming the reason, when a row is passed on whole (`<X loc={loc} />`, `{...loc}`, `f(loc)`). **Still not dated by rows:** shared readers of the data files, such as the location hub `/uk-locations/`, the footer (`SiteFooter`) and the sitemaps, which render keys of many rows. They stay covered only by the planned content hash below.
    - **Planned structural fix (not built):** a per-route content hash of the built page, taken after stripping `<style>`, the date nodes and `data-astro-cid-*`, would replace the guard's judgement with a fact. `dateModified` would move only when the hash moves. That catches a refactor of a single-file page, which the fan-out bar of 3 lets through, and a real layout or kit change (a shared component, `src/styles/kit.css`) that changes pages without ever touching their date sources, which dates nothing today.
95. **The guarantee is two years, and what it covers is stated from data (London branch, Plan 2 Task 10b and its follow-up, 2026-09-29; the cover, answer board q02, `78c0e9a`). CLOSED for the copy; the board records' `dropped.creds` wait for each page's next board touch.**
    - **The ruling:** the breeder's answer on the answer board (q07, 2026-09-29) is two years. `data/settings.json` holds `guarantee_days: 730`, `guarantee_label` ("Two-year health guarantee": the site calls it a "health guarantee" and never names a cover, so the label names none), `guarantee_note` and `guarantee_source`. `src/lib/cityKit.ts` `checkGuaranteeLabel()` refuses a label that does not open with its length as whole words; `guaranteeRow()` prints it on city pages (London's trust strip, takeaways and FAQ rail, and both specimens). The instruction tree points at `guarantee_label` and never types the length (`tests/py/test_agent_facts.py`); only `data/settings.json` and CLAUDE.md's Brand context state it.
    - **Corrected on the built pages (the user's ruling "Correct them now", commit `de8853f`):** six statements on four rebuilt pages, each read from `guarantee_label` through `src/lib/site.ts` `guaranteeLabel()` (the FAQ answer through the `guarantee_label_lc` token in `src/lib/faq.ts`): the `/` FAQ answer (`data/faq.json` `home-health-guarantee`, now sourced to `data/settings.json`), `/` "No Guarantee Length Is Printed Here" → "Our Two-Year Health Guarantee", `/blue-staffy-health-uk/` "There is no guarantee length anywhere on this site" → "Ours is a two-year health guarantee, …", `/blue-staffy-health-uk/` "The Guarantee Row Is Absent, Not Overlooked" → "Ask Us About Our Two-Year Health Guarantee", `/blue-staffy-pup-sale-uk/` "No Health Guarantee Is Stated" → "Not an Item, a Promise: Our Two-Year Health Guarantee" (its heading in `de8853f` was "And Our Two-Year Health Guarantee", then "A Two-Year Health Guarantee With Every Puppy" in `e8dde15`; the re-review's wording landed in `9830276`), `/buy-blue-staffy-puppies-uk/` "No term is stated for a guarantee" → "What we do promise is our two-year health guarantee; ask us for its full wording before you pay a deposit." Their `dateModified` moved to 2026-09-29 (`fanout_accepted` in `data/page-dates-ignore.json`). `tests/py/test_guarantee_statements.py` holds them.
    - **The rest corrected too (the coordinator: the ruling covers every contradicting line, commit `e8dde15`):** eight more lines on five rebuilt pages — `/blue-staffy-pup-sale-uk/` lede, `/buy-blue-staffy-puppies-uk/` "We state no health guarantee…", `/blue-staffy-health-uk/` "no guarantee length, …" and "A tenth is deliberately absent…", `/blue-staffy-uk-breeders/` "— a guarantee length, …", and `/buy-staffy-puppies-for-sale-uk/` (the InfoCard, the h4 "No Term Is Stated, Because None Is Held" → "Our Two-Year Health Guarantee, in Writing", and its line). Only the contradicting clause changed. `tests/py/test_guarantee_statements.py::test_no_built_page_says_the_guarantee_length_is_unstated` now holds every built file in `dist/` to a pattern list (board previews excluded). `/blue-staffy-uk-breeders/` and `/buy-staffy-puppies-for-sale-uk/` moved to 2026-09-29; the other three were already dated that day, so the commit moved 2 routes and the fan-out guard did not fire. The board records under `data/boards/` (and `/board-preview/blue-staffy-health-uk/`) keep the old reason (`guarantee_days: null`) as history.
    - **The re-review (2026-09-29, not approved; fixed).** The health FAQ intro no longer points "just below the list" and its H5 line names what it stands in for; the pup-sale guarantee is a promise, not a seventh item; no page promises to SEND the wording (`guarantee_note` says "Ask us"); the home H5 and the for-sale "in Writing" H4 read plainly; stale page comments that said the guarantee is unset are gone (`test_no_page_source_comment_says_the_guarantee_is_unset`); `src/lib/guarantee.ts` checks the label for the built pages too and refuses one that names a cover; the unstated-guarantee patterns cover more shapes and spare look-alikes.
    - **Board records:** each page's board `dropped.creds` still lists the guarantee; update it on that page's next board touch.
    - **Answered: what it covers (answer board q02, 2026-09-29, `78c0e9a`).** The breeder wrote "Against any heaalth issues and birth defects within two years of ownershipping"; the page wording, spelling corrected, is "covers health issues and birth defects for two years from the day your puppy comes home". It is a field of its own, `data/settings.json` `guarantee_cover` (with `guarantee_cover_source`), checked by `src/lib/guarantee.ts` `checkGuaranteeCover()` (opens "covers ", no closing punctuation, states the length once as "for two years"). `guarantee_label` is unchanged and `checkGuaranteeLabel` still refuses a label that names a cover. Read through `src/lib/site.ts` `guaranteeCover()`, the FAQ token `{guarantee_cover}` and `src/lib/cityKit.ts` `guaranteeRow()`, it is printed only where a guarantee sentence already stood: the home FAQ answer (`home-health-guarantee`, visible and FAQPage) and the city guarantee row (London's trust strip, takeaways and FAQ rail; the kit previews). CLAUDE.md rule 9 and Brand context, and 40 agent and skill lines that said "name no cover the site has not stated", now point at `guarantee_cover`; `tests/py/test_agent_facts.py`'s unset-guarantee scan refuses an instruction that still says no cover is named. `tests/py/test_guarantee_cover.py` holds it. The dup gate counts one new shared run, the cover clause itself on `/` and the London page: the same data field printed twice.
96. **`img-sizes-matches-box` misparses a nested parenthesis in a `sizes` length (found 2026-09-28, London Plan 2).**
    - `(min-width: 1024px) calc((100vw - 152px) / 6)` resolves to the NEXT entry: the check's `^(\(.*\))\s+(.+)$` is greedy, so the media condition swallows `calc((100vw - 152px)` and the length becomes `/ 6)`. The city hero writes its entries without nested parentheses (`calc(16.667vw - 25.333px)`), and no built page trips it today.
    - **Next:** a known_broken fixture with a nested-paren entry that must resolve correctly, then a balanced-paren split in the check (the harness, not a new rule).
97. **Headings at body size on the twelve built pages (London Plan 2 close, 2026-09-29). CLOSED in `67fc0a9`, with the side gutter (`cf88f44`, `070dc7b`) and the boxed H2 (`625a94b`) found with it.**
    - **Confirmed on the built pages**, in Chromium through Playwright on `dist/`, computed `font-size` of every visible H2 and H3 in `<main>` at 375, 768 and 1280 (body text is 17px on every page): 49 H2s and 217 H3s paint at 17px, the body size. The numbers are the same at all three widths. The H2s are all outside a `.bl-box`; 167 of the H3s are outside one and 50 are inside one without a kit component of their own. The only heading-size rule is `.bl-box h2 { font-size: var(--text-2xl) }` in `src/styles/board-styles.css`; the preflight leaves every other H2/H3 at the inherited body size, at weight 400 in the migrated sections.
    - **Per page (H2 at 17px unboxed / H3 at 17px unboxed / H3 at 17px boxed, of all H2 + H3):** `privacy-policy-uk` 8 / 20 / 0 of 9 + 23; `thank-you-blue-staffy-puppies-journey` 2 / 4 / 1 of 7 + 18; `uk-blue-staffy-breeders-contact` 2 / 8 / 2 of 8 + 15; `index` 0 / 0 / 9 of 20 + 43; `blue-staffy-pup-sale-uk` 1 / 2 / 6 of 12 + 24; `buy-blue-staffy-puppies-uk` 0 / 0 / 11 of 13 + 33; `buy-staffy-puppies-for-sale-uk` 2 / 6 / 4 of 17 + 53; `blue-staffy-uk-breeders` 6 / 14 / 2 of 13 + 31; `blue-staffy-health-uk` 9 / 33 / 1 of 15 + 49; `uk-staffordshire-bull-terrier-guide` 8 / 37 / 1 of 16 + 57; `uk-blue-staffy-puppy-buying-guide` 10 / 41 / 7 of 20 + 62; `blue-staffy-blog-guides` 1 / 2 / 6 of 7 + 16. For example, the health page's H2 "Our Rigorous Health Testing Process : Ensuring Peace of Mind" paints at 17px, directly under the previous section's prose.
    - **Evidence:** screenshots and the full per-heading table, `/Users/apple/Downloads/BSUK/BSUK-refs/london/_plan2-shots/close/heading-sizes.json` (outside git). The visual-intelligence re-test of `/blue-staffy-health-uk/` measured the same 43 of 64 independently.
    - **Charged to the harness:** no check was silent, because none covers it. `layout-min-font-size` is a floor for all text, `sem-heading-order` reads levels, not sizes, and `city-type-fit` (city routes only) caps heading sizes from above and sets no floor. The missing invariant: a body H2 or H3 paints larger than the body text. It goes to the learning loop as a known_broken fixture and a render check.
    - **The pick (2026-09-29):** "a and all recommendations", from the preview `docs/artifacts/bsuk-heading-scale-preview.html` (https://claude.ai/artifact/7WfxLwvXTxxBGN9HtZuMwZ): option (a), the city scale, plus the two defects the preview found.
    - **Heading scale (`67fc0a9`).** Harness first: `layout-body-heading-above-body` (blocking, scope all) fails a visible H2/H3 in `<main>`, outside a kit or city-kit component, that paints at or below the body size (the font-size carrying the most paragraph text). Red: 6 of 6 meta tests with a stub; on HEAD's build it fired on all twelve pages. Then option (a)'s block, verbatim, in `src/styles/board-styles.css`'s existing `@layer components` beside `.bl-box h2`. **Before / after, the twelve pages, each of 375 / 768 / 1280:** 266 of 266 body H2/H3s at or below the 17px body → 0 of 404 examined (the check examines 447 per width across the 20 render targets). Painted: H2 17px/400 → 22 / 25 / 28px at 700, line-height 1.18; H3 17px/400 → 18 / 18 / 20px at 600. The block is global (`src/layouts/BaseLayout.astro` imports `src/styles/global.css`), so the four other targets that had the defect lifted too: `/available-puppies/` 6, `/blog/` 1, the blog post 2, `/uk-locations/blue-staffy-puppies-uk/` 28. The six scroll-spy stub labels on `/kit-preview/` (15px, `.spy-targets h3`) are pinned by name in the check; they now paint at weight 600 and line-height 1.25, the only change on that page. At 375 the long migrated headings the preview listed wrap to 4 or 5 lines; they are not reworded (content, verbatim set) and no check flags unboxed ones.
    - **Side gutter (`cf88f44`, `070dc7b`).** Confirmed on all twelve pages at 375 / 768 / 1280: below 1024px PageShell adds no gutter, and the unboxed `.page-body > section` (no class) owned none, so their text ran from x = 0 on ten pages (every page but `/` and `/buy-blue-staffy-puppies-uk/`, whose sections are all boxed) at 375 **and** 768, not only on the three the preview named; nothing at 1280. The blog post's page-mounted `.page-toc` misses PageShell's scoped gutter the same way (its text at 14px at every width). No check was silent: `layout-no-horizontal-overflow` asks whether the document scrolls sideways, and text on the edge does not. New check `layout-text-has-side-gutter` (blocking, scope all), measured on each text node's own glyph Range; red 6 of 6 with a stub. **Before / after:** 827 text nodes within 16px of an edge at 375 and 795 at 768 → 0 (3788 / 3829 / 3950 examined per width). The fix: `.page-body > :where(section:not(.bl-box, .city-kit, [class*="kit-"]), .page-toc) { padding-inline: var(--space-5) }`, released where a dial grid pads the column at 1024px and up. The first version also padded the London page's city sections below 1024px (243 of 586 painted elements moved at 375); `070dc7b` skips kit and city-kit roots, and London and both city specimens now paint element for element as before.
    - **Boxed H2 (`625a94b`).** `.bl-box h2` was `--text-2xl` (30px) at every width on the inherited 1.65 line-height. New check `layout-boxed-h2-fits` (blocking, scope all) holds a boxed H2 outside a kit component to 22 / 25 / 28px by tier and to three lines; red 6 of 6 with a stub. **Before / after:** 104 of 104 boxed H2s over the cap at every width, 14 past three lines at 375 (up to six lines, 297px) and one at 1280 → 0 over the cap; `.bl-box h2` is now 22 / 25 / 28px, line-height 1.18, `text-wrap: balance`. The health page's first boxed H2: four lines, 198px → three lines, 78px at 375. **Flagged, pinned by name:** two verbatim-set H2s on `/buy-staffy-puppies-for-sale-uk/`, "What Are the Key Takeaways When Choosing BlueStaffyUK for KC Registered Blue Staffy Puppies in the UK?" (102 characters) and "Why Does BlueStaffyUK Health Test Puppies and What Does It Mean to Have Staffies From L-2-HGA Tested Parents?" (109), four lines (104px) at 375, down from six; pinned for the line cap only, never the size cap.
    - **Proof it is style only:** all 64 built HTML files are byte-identical to HEAD's (`3f169d1`) build outside `<style>`.
    - **Dates:** `scripts/generate_page_dates.py` dates a page by its own file, its template and its data row; no CSS file is a date source, so the fan-out guard cannot fire and no page was re-dated. That is Known Issue 94's stated gap for kit and layout changes ("a real layout or kit change … dates nothing today"): no `fanout_accepted` entry, because the words, facts and images did not change, and the per-route content hash planned there would ignore `<style>` in any case.
    - **Design passes:** `docs/research/london-components/hardening-log.md` `## Known Issue 97 applied`. After shots: `/Users/apple/Downloads/BSUK/BSUK-refs/london/_plan2-shots/ki97-after/` (outside git).
    - **Next, each its own preview (working rule 6):** (1) **heading colour**: the built pages paint headings in `--color-ink`; `rules/design.md` rule 1 gives headings `--color-brand`, and the city kit already uses it. (2) **boxed H2 weight**: a box's own H2 stays at 400 while the unboxed H2 is 700 (design pass finding 3). (3) **desktop alignment**: at 1280 unboxed text starts 24px left of boxed text (x = 292 against 316). (4) the long migrated headings at 4–5 lines on a phone are content, for each page's next board touch.
98. **The health page's visual-intelligence re-test findings (London Plan 2, 2026-09-29). Listed, not fixed.**
    - **Source:** the `bsuk-visual-intelligence` re-test of `/blue-staffy-health-uk/` (read-only, verdict FAIL on both gates; report kept in the session scratchpad, not committed). No page was changed.
    - **Unproven results. RESOLVED (answer board q01, 2026-09-29: the breeder holds no DNA certificates; the pages name the tests and never state a result).** The grep of every built page, `data/*.json`, `llms.txt`, schema and the FAQ data found 138 result statements across eleven built files, the sitemaps and the kit previews, not only the health page's ten: "tested / certified / recorded clear", "clear of", "clear DNA results", "clearances", "a clear pair", "will not be genetically affected", "results on request", and every line that offered our certificates or results. Each now names the test only (`5160742`, dates `bfa6499`), and the rewording was varied page by page so it adds no sibling duplicate (`eb2d47e`). Eleven FAQ answers and two FAQ questions; eight board records re-approved; two counter tiles that stated a result removed whole ("Clear" on the health page, "DNA clearances on both parents" on the about page); `verbatim.changed` rows on six records with the reason "wrong fact per the breeder's answer 2026-09-29" (the why-us H2 "…L-2-HGA Clear Staffies?" → "…L-2-HGA Tested Staffies?", two alts, five openings, one FAQ question). The ledger row `parents-dna-clear` stays proof `NOT FETCHED`, `confirmed` null — all the schema allows for a claim with no proof — and gains a `barrier` saying none is held. Agents and skills follow (`f8076c2`). `tests/py/test_no_health_result_stated.py` holds every built file and the FAQ data. Re-approving exposed a tool bug, fixed first (`ae1bcac`): `--reapprove` refreshed every section's fingerprint and erased the homepage re-board's evidence. **The review (2026-09-29, not approved; fixed in `cb265a8`, `223e2cc`, `029e815`, `e0035b6`, `640db07`).** The harness missed "clear health tests" (the buying guide) and "showing the screening results" (why-us), so it was charged, not a new rule: `tests/py/test_no_health_result_stated.py` now ties result words (clear, negative, passed, results, certificates, unaffected, free of) to a health-test sentence, with the review's ten fixtures failing first and four false positives passing. The principle the scam agent carries now governs the pages too: we never give buyers advice our own process fails, so no line sends a buyer to DNA certificates or results — the buying-guide checklist, the guide and health notes, the blog note and four FAQ answers ask which tests were run and for the vet records. **Decided by the controller under that principle, not left for the breeder:** the why-us FAQ "Can I see the health test results for both parents?" became "Which health tests have both parents had?", answered with the tests, the vet records and "We hold no DNA certificates". The about page's "2 / DNA tests on both parents" tile is restored (`board_approve.py --reapprove` now restores a figure the record held before, label reworded), and the counter ledes count their tiles. **Still open, by name, pinned by count and text** (`tests/py/fixtures/migrated_health_results.json`): `/uk-locations/staffy-breeding-dogs-glasgow/` (19 hits: "L-2-HGA …: CLEAR", "HC-HSF4 Clear Blue Staffy puppies", "health clearances", "BVA/KC Eye Scheme: Clear") and, found by the widened harness, `/uk-locations/blue-staffy-puppies-uk/` (1: "hereditary cataract clear blue Staffies"). Both are migrated WordPress body from `data/locations.json` (generated, never hand-edited); a template-side fix would re-date 26 unchanged location pages, so they wait for their project 5 rebuilds. A new hit on either fails the test, and so does a page that has come clean. The migration snapshots in `data/facts/` (for example the buying guide's "clear health tests") are history of the old site and are not rendered.
    - **KC "fewer health risks".** The FAQ answer "Do KC Registered Staffies Have Fewer Health Risks? Yes." has no source in `docs/reference/external-link-library.md`, and it contradicts the page's own "What Registration Does Not Do". **Owner:** a future health-page touch.
    - **Patella claim.** Patella grading is stated twice, and no ruling covers it (Q9 names eyes and elbows). **Owner:** the answer board (a question for Lisa when the page is next touched), then a future health-page touch.
    - **Deposit called plainly "refundable".** This conflicts with ruling Q3. **Owner:** the separate `deposit-wording` branch.
    - **No CTA or money-page link in the body.** There is no CTA pill and no enquiry form in `<main>`, and the body links neither `/buy-staffy-puppies-for-sale-uk/` nor `/buy-blue-staffy-puppies-uk/` (Function Coverage 6 of 8). **Owner:** a future health-page touch (`bsuk-cta-strategy`, `internal-link-agent`).
    - **False exemption.** `final_page_audit`'s newsletter exemption for this page gives the reason "the enquiry form is its one closer", but the page has no enquiry form (its only form is the header search). **Owner:** a future health-page touch, with `bsuk-gate-integrity` for the exemption.
    - **Five mis-described images.** `what-health-tests-blue-staffies-need` (alt says a graphic; it is a photo of a vet), `puppy-vaccinations-uk` and `vet-check-uk` (alts say blue Staffy; the pups are not blue), `what-to-feed` (a Royal Canin packshot with a Jack Russell, beside the H4 "No Brand and No Gram Figure Here"), and `find-health-certified-breeders` (alt says a buyer checking a list; the image shows an injection). Working rule 11 keeps a served alt, so the fix is new images placed beside the old ones. **Owner:** a future health-page touch (`@bsuk-image-pipeline`, `image-metadata`).
    - **Heading sizes:** these are Known Issue 97.
