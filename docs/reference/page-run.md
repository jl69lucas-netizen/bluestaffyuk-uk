# The Per-Page Run — project 5

> **Read this before building any project 5 page:** a location page, a comparison page or a
> blog post. One page, one run, top to bottom. Every row names the command that does the
> step, what it leaves on disk, the gate that fails when the step is skipped, and whether the
> run stops there for the breeder.

This is the page-build brief the source repo runs before every page (its Universal Page Build
Brief, v2.0) laid out as BlueStaffyUK's own commands. The brief's sections are numbered §0 to
§26; the **Brief step** column keeps those numbers so a row can be traced back to the section
it comes from. The sprint model itself is `docs/reference/WORKFLOW.md`; this file is the order
in which one page walks through it. `npm run check:workflow` resolves every agent, skill,
script and npm script named here, so a row that names something that is not there fails the
gate rather than failing the run.

A skill written `plugin:name` (`impeccable:impeccable`, `frontend-design:frontend-design`,
`superpowers:writing-plans`, `superpowers:verification-before-completion`) is a global plugin
skill. Invoke it with the Skill tool by exactly that name; never paraphrase it and never skip
it (the user's rulings, 2026-09-26).

## Which builder, route and profile

`<slug>` is the page's bare key (its board is `data/boards/<slug>.json`); `<route>` is where it
is built (`dist/<route>/index.html`). The page audits take the route; the board scripts, the
page-run record and the gate runner (row 17) take the key.

| Page type | Builder skill | `<route>` | Final-audit and evidence profile | Rule packs to read |
|---|---|---|---|---|
| location | `.claude/skills/bsuk-location-page-builder/SKILL.md` | `uk-locations/<slug>` (the slug is the row in `data/locations.json`, never rewritten) | `location` | copy, links, images |
| comparison | `.claude/skills/bsuk-comparison-page-builder/SKILL.md` | the route the URL-family decision gives it | `comparison` | images, headings, copy |
| blog | `.claude/skills/bsuk-blog-post/SKILL.md` | `<slug>` (a post in `src/content/blog/` builds at `/<slug>/`) | `blog` | headings, images |

The URL-family decision for the city cluster and the comparison slugs is one table,
`docs/research/2026-09-26-url-family-decision.md` (arrives in Task 27). Read the page's row
before row 3.

## The run

Three rows stop for the breeder, and only three: the brief (stop 1), the board (stop 2) and
the Asset Gate (stop 3), as `docs/reference/WORKFLOW.md` sets for a session that runs with
the breeder away. The two Harden passes (rows 14 and 15) are mandatory on every project 5
page and pause only for a PREVIEW: when a pass proposes a visual change, it is previewed and
approved before it is applied. With the breeder away, the proposed change is written as a
preview on disk, recorded `deferred` in the pass's record and logged under Open Flags; it is
not applied, the run continues, the three stops stay three, and the change is applied only after
the breeder approves it. Everywhere else the Clarification Checkpoint applies
(`CLAUDE.md` working rule 7): write the finished part to disk, log the question, ask one
narrow question, keep building what is not blocked.

| # | Brief step | BSUK command, skill or board block | Deliverable | Gate that fails | Approval stop |
|---|---|---|---|---|---|
| 1 | §2 Session open | invoke `grill-me` (`--brief <path>` when the breeder is away), then the `superpowers:writing-plans` skill, then the page-type builder skill from the table above | the session brief (goal, scope, gates, done, out of scope) and this page's plan | enforced at row 18 by `npm run gate:page -- <slug>`, whose page-run record names the session-open skills — `scripts/gate_page.py` (arrives in Task 25); until then `npm run check:workflow` only proves every agent, skill and script this run names exists | none |
| 2 | §0 Target Block — the mode is found by looking | `scripts/page_intake.py` (arrives in Task 24): `python3 scripts/page_intake.py <slug>`; the same lines are block 0 of the board | the intake block: mode (stub, migrated, rebuilt or new), robots, built file and whether it is fresh, sitemap entry, verbatim count, empty `h1`, question file, LLM-intel file, board status, Search Console baseline with its barrier, inbound links, retired-term hits | advisory: `python3 scripts/page_intake.py <slug>` exits 2 on a slug no data file knows (arrives in Task 24) | none — the intake rides on the board and is approved at stop 2 |
| 3 | §4 URL, canonical and redirect decision | the page's row in the URL-family decision; a slug that moves gets its 301 in `data/redirects.json`, then `npm run redirects` | the slug, canonical and redirect rows the board records in `meta.slug` | enforced at row 12 by `npm run check:all`, which runs `npm run check:redirects` (one hop, target built, nothing shadowed) | none — decided once for the cluster, on the answer board |
| 4 | §5 Research on hand, inventory before any fetch | `scripts/page_intake.py` (arrives in Task 24) lists what is banked for the slug; reuse it, and fetch through the spend guard only what is missing | an absent figure written `NOT FETCHED — <barrier>`, never bare and never guessed | `npm run check:barriers` (Task 21's barrier lint) and `npm run test:py` (the spend guard) | none |
| 5 | §6 Competitor research and query fan-out | `bsuk-query-augmentation` for the slug (top 5 on Google and Bing, merged), then the row 5 steps below | `data/queries/<slug>.json` (competitors with their metrics, `section_target`, `word_target`, `extra_sections`, FAQ picks) and `docs/research/llm-intel/<slug>-<date>.json`; when `word_target` has no median (every competitor a marketplace listing), the barrier is recorded on the board and the word band is the breeder's decision on the answer board | `npm run check:queries`, `npm run check:competitors`, `npm run check:gaps`, `npm run check:threads` | none |
| 6 | §7 Keyword deliverables and metrics | `python3 scripts/keyword_variants.py <slug>` for the four extra types; `python3 scripts/keyword_metrics.py <slug>` for the ours-vs-top-5 table on the board (block 4b; its JSON report is git-ignored) | the section keywords in the record, and the metric table (unique terms, variations, exact match per tag, first 100 words, title front-load) | `keyword-variants-missing` in `scripts/family_rules.py`; `python3 scripts/keyword_metrics.py <slug>` exits 1 on any FAIL (title-front-load, first-100-words, or a missing primary keyword) | none |
| 7 | §8 Entities and co-occurrence | `python3 scripts/ontology_seed.py --check`; board block 5 groups the entities by class | every entity a section names, in `data/bsuk-ontology.json` with a source | enforced at row 10 by `python3 scripts/board_approve.py <slug>`: a BLOCKED entity is the block 7b FAIL `entity-blocked`, which refuses approval; `python3 scripts/ontology_seed.py --check` is advisory | none |
| 8 | §9–§10 Gaps, angles and the strategy | the page's row in the approved cluster strategy (`docs/superpowers/sessions/2026-09-25-location-pages-strategy.md`); `grill-me --brief` for a page that strategy does not name; `bsuk-strategy-synthesizer` when a new strategy is needed | board block 1: goal, scope, gates, done, out of scope, strategy and why, the angles considered | advisory: `python3 scripts/strategy_cite_check.py <strategy.md>` on any new strategy | STOP 1 — the brief, only for a page with no row in the approved strategy |
| 9 | §11–§12 Distribution matrix and the H1–H6 outline | for a page that exists, `python3 scripts/facts_preserved_check.py --extract <slug>` first, then the row 9 steps below: blocks 2 (H1 and meta), 3 (outline, heading collisions, every link), 3a (verbatim set) and 4 (distribution, why each section is here) | the approved outline: sections derived from the competitors' count + 3, grouped, each with its framework and `why_source` | `schemas/board.schema.json` through `scripts/pageboard.py`; `python3 scripts/board_approve.py <slug>` (after `npm run -s build`: it reads the built site) refuses a header that collides with a built page or with another approved-but-unbuilt board, and any block 7b FAIL | none — approved with row 10 |
| 10 | §13–§14 Components, hero refresh and the tool decision | `python3 scripts/build_board_previews.py <slug>`, then the board: block 3c (navigation), block 5b (the kit), block 6 (three styles per section at 1280 / 768 / 375), block 7b (the project 5 rules) | the component tuple, the page's own hero and counter styles, a refresh delta on every section | `python3 scripts/board_approve.py <slug>`; `tests/py/test_rule16_gate.py` refuses a shared hero or counter | STOP 2 — the breeder approves the board, which carries rows 2 and 6–10 |
| 11 | §15 Images and the Asset Gate | `python3 scripts/image_candidates.py <slug> --write`, then the row 11 steps below; board block 7 on its second pass | an image on the hero and every body H2 and H3, each with its `assets[]` row and an approved file; each body image directly after its heading in the uniform box (`box="uniform"`, or `box="tall"` for a portrait); a new portrait baked with `--og-style A` (contain), never blurfill, and any bleed around an in-body image in the design colour (bone), never grey or black | enforced at row 12 by `npm run check:boards` (inside `npm run check:all`, after a fresh `npm run -s build`), which runs `scripts/board_gate.py` for every rebuilt page; run `python3 scripts/board_gate.py <slug>` by hand before then | STOP 3 — the Asset Gate: a generated image is approved by its sha12 pick before it is published |
| 12 | §16 Build from the outline | the builder skill from the table above (`bsuk-location-page-builder`, `bsuk-comparison-page-builder` or `bsuk-blog-post`), then the row 12 steps below | the built page in `dist/<route>/index.html`, written from its own outline and nothing else | `npm run check:all` (parity, facts, links, verbatim, outline, board gate, retired facts) | none |
| 13 | §17 Responsive typography, spacing and scroll | `npm run test:render:meta` first, then `npm run test:render:pages` (375 / 768 / 1280), which rebuilds the scorecards | `data/quality/scorecards/<slug>-<date>.json` with every check's examined count | `npm run test:render:pages`: a blocking IMG, LAYOUT or NAV row, a check that examined zero nodes, or on a new page (from board approval on) any of the four promoted checks: `hero-counter-separation`, `h3-image-first`, `sem-section-opening-paragraph`, `sem-title-case-headings` | none |
| 14 | §18 Harden — the `impeccable` pass | invoke the `impeccable:impeccable` skill on the built page at 375 / 768 / 1280, checked in a painting browser (Playwright or a real Chrome window, never a DOM-only read); commit its fixes; then `scripts/page_run_record.py` (arrives in Task 25): `python3 scripts/page_run_record.py <slug> impeccable --findings <n> --fixed <n>` | every finding fixed or deferred with its reason (breeder away: the change is written as a preview on disk, recorded `deferred` in the pass's record, logged under Open Flags and not applied until the breeder approves), and the `impeccable` key of `data/page-runs/<slug>.json` (date, widths, findings, fixed, deferred, commit) | `npm run gate:page -- <slug>` fails while the key is missing, a width is missing, a finding is neither fixed nor deferred, or the key's commit is not an ancestor of (at or before) the verification commit of row 18; a harden fix committed after this pass does not stale it (arrives in Task 25) | PREVIEW — only when it proposes a visual change: preview before apply (working rule 6); with the breeder away it is `deferred`, logged under Open Flags and not applied, and the run continues; the palette never changes |
| 15 | §18 Harden — the `frontend-design` pass | then invoke the `frontend-design:frontend-design` skill the same way, at the same three widths, in a painting browser; commit its fixes; then `python3 scripts/page_run_record.py <slug> frontend-design --findings <n> --fixed <n>` with `scripts/page_run_record.py` (arrives in Task 25) | the `frontend_design` key of `data/page-runs/<slug>.json`, every finding fixed or deferred (breeder away: the change is written as a preview on disk, recorded `deferred` in the pass's record, logged under Open Flags and not applied until the breeder approves) | `npm run gate:page -- <slug>` fails on the same four conditions for this key; its commit too must be an ancestor of the verification commit (arrives in Task 25) | PREVIEW — only when it proposes a visual change: preview before apply (working rule 6); with the breeder away it is `deferred`, logged under Open Flags and not applied, and the run continues; the palette never changes |
| 16 | §18 Harden — the static scan | `python3 scripts/page_hardening_scan.py <route> --fail-on-error` (the page, its template and data, and the kit) | 0 ERROR, every WARN triaged real, dead code or false positive | `python3 scripts/page_hardening_scan.py <route> --fail-on-error` (exit 1 on an ERROR, exit 2 on a route with no built page), run twice more by the row 17 runner | none |
| 17 | §19 Gates, each run twice | `npm run gate:page -- <slug> --skip-record` — `scripts/gate_page.py` (arrives in Task 25), then the row 17 steps below | `docs/reports/gate-page/<slug>.json` with both runs and their diff | `npm run gate:page -- <slug> --skip-record` exits 1 on any FAIL or any difference between the runs | none |
| 18 | §19 Verification before completion | invoke the `superpowers:verification-before-completion` skill before any "page done" or "ready for approval" claim, then the row 18 steps below, where `scripts/page_run_record.py` records the evidence (arrives in Task 25) | the `verification_before_completion` key of `data/page-runs/<slug>.json`: each command, its exit code and its examined count, and the claims it verified | `npm run gate:page -- <slug>` fails while the key is missing, a command exited non-zero, `check:all` or the gate run is not among the commands, or the record is stale: it is fresh only when this key's commit is at or after the page's last source change (arrives in Task 25) | none |
| 19 | §20 The measurement ledger | `scripts/measurement_ledger.py` (arrives in Task 26): `python3 scripts/measurement_ledger.py <project> --slugs <slug>` | M1–M3, M6, M8–M10, M12, M13 and M18 as numbers, pasted into the gate report | `python3 scripts/measurement_ledger.py` exits 1 when M1, M2, M8 or M10 fails | none |
| 20 | §21 LLM visibility | the page's LLM-intel file from row 5 (one engine, one query); `python3 scripts/aeo_audit.py <route> --fail-on-error`, also run twice by the row 17 runner | the fetched denominator (1 of 1, or `NOT FETCHED — <barrier>`), the answer structure, the engine terms the page lacks | `python3 scripts/aeo_audit.py <route> --fail-on-error` | none |
| 21 | §22 Deploy and close | `python3 scripts/rendered_changes.py --base <ref> --json` (writes the report only; the dist-hash manifest is recorded after a successful IndexNow submit, in project 6); the build's postbuild regenerates the sitemaps; invoke the `superpowers:verification-before-completion` skill again before the gate report says PASS; `session-closer`; the gate report published as an Artifact with its `.md`; commit on the project branch and never push | docs/reports/rendered-changes.json (the slugs whose built output changed: project 6's IndexNow list), the gate report, the Known Issues update | `npm run check:sitemaps` and `npm run check:all` | none — the live 200 and IndexNow wait for project 6 |

## The steps inside the multi-command rows

Each row above names its first command; the rest run in this order.

### Row 5 steps

1. `bsuk-query-augmentation` for the slug (top 5 on Google and Bing, merged)
2. `python3 scripts/query_augment.py --extract-h2 <file>` on each saved competitor page
3. `python3 scripts/query_augment.py --competitor-metrics <slug>` fills each page's metrics from the saved HTML; when `word_target` has no median (every competitor a marketplace listing), record the barrier on the board — the word band is the breeder's decision on the answer board
4. `bsuk-reddit-threads` against the shared thread ledger: `python3 scripts/thread_ledger.py --known <url>` before a thread is read, `--seed` for a new page's questions
5. `bsuk-llm-keyword-intel` for the slug

### Row 9 steps

1. for a page that exists: `python3 scripts/facts_preserved_check.py --extract <slug>`
2. for a page that exists: `python3 scripts/verbatim_set_check.py --extract <slug>` (both before the board, as the location builder's step 4 says)
3. write the record `data/boards/<slug>.json`
4. `python3 scripts/build_page_board.py <slug>`

### Row 11 steps

1. `python3 scripts/image_candidates.py <slug> --write`
2. `python3 scripts/ingest_image.py folder` for an existing master, or `python3 scripts/ingest_image.py draft` for a generated one
3. the breeder picks each draft by its sha12 on the board's second pass (stop 3)
4. `python3 scripts/ingest_image.py publish` for each approved pick

### Row 12 steps

1. the builder skill from the table above, writing from the approved outline only
2. `npm run build`
3. `python3 scripts/outline_provenance_check.py <slug>`
4. add the slug to `data/facts/rebuilt.json` and the page to `tests/render/targets.json`

### Row 17 steps

1. `npm run gate:page -- <slug> --skip-record` runs dup (body and `--headers`), the final audit on the profile above, hardening, AEO and evidence, twice, and diffs the two runs — `scripts/gate_page.py` (arrives in Task 25)
2. its evidence step is `python3 scripts/evidence_audit.py <route> --type <profile> --fail-on-error`: on a new page an unledgered health or credential claim is an ERROR
3. `python3 scripts/quality_report.py`
4. `python3 scripts/perf_audit.py <route>` (5 runs, the warm median of runs 2–5)

### Row 18 steps

1. invoke the `superpowers:verification-before-completion` skill
2. `python3 scripts/page_run_record.py <slug> verification --run "npm run -s check:all" --run "npm run gate:page -- <slug> --skip-record" --claim "<claim>"` runs each command and records its evidence — `scripts/page_run_record.py` (arrives in Task 25)
3. `npm run gate:page -- <slug>` with the record — `scripts/gate_page.py` (arrives in Task 25)

## What a finished page leaves on disk (§23)

Each item is a file, not a claim that the step was considered:

- `data/queries/<slug>.json` and `docs/research/llm-intel/<slug>-<date>.json` (Sprint 0)
- `data/boards/<slug>.json`, approved, and its board page under `docs/artifacts/boards/` (Sprint 1)
- every image slot's file and approved sha12 pick in the record's `assets[]` (Asset Gate)
- `dist/<route>/index.html`, the slug in `data/facts/rebuilt.json` and the page in
  `tests/render/targets.json` (Sprint 2)
- `data/page-runs/<slug>.json` with its `impeccable`, `frontend_design` and
  `verification_before_completion` keys (Sprints 3–4)
- the page's scorecard in `data/quality/scorecards/` (Sprints 3–4)
- `docs/reports/gate-page/<slug>.json` with two identical runs (Sprint 4)
- the ledger rows and docs/reports/rendered-changes.json in the project's gate report (close)

## Deliberate differences from the brief

Recorded and still correct: three stops instead of one per sprint; exactly two strategies; one
LLM engine per page, so the visibility denominator is 1, not 30; four counters, not eight; the
section count is the competitors' highest real count + 3, never a fixed number; no seam
dividers, so the seam-parity check has nothing to count; no push and no IndexNow until
project 6. STOP 1 (strategy) applies only to a page with no row in the approved cluster
strategy; the cluster strategy was approved once.
