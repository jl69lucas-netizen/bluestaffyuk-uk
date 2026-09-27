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
| location | `.claude/skills/bsuk-location-page-builder/SKILL.md` | `uk-locations/<slug>` (the slug is the row in `data/locations.json`, never rewritten) | `location` | copy, links |
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
approved before it is applied. Everywhere else the Clarification Checkpoint applies
(`CLAUDE.md` working rule 7): write the finished part to disk, log the question, ask one
narrow question, keep building what is not blocked.

| # | Brief step | BSUK command, skill or board block | Deliverable | Gate that fails | Approval stop |
|---|---|---|---|---|---|
| 1 | §2 Session open | invoke `grill-me` (`--brief <path>` when the breeder is away), then the `superpowers:writing-plans` skill, then the page-type builder skill from the table above | the session brief (goal, scope, gates, done, out of scope) and this page's plan | `npm run check:workflow` (every agent, skill and script this run names exists) | none |
| 2 | §0 Target Block — the mode is found by looking | `scripts/page_intake.py` (arrives in Task 24): `python3 scripts/page_intake.py <slug>`; the same lines are block 0 of the board | the intake block: mode (stub, migrated, rebuilt or new), robots, built file and whether it is fresh, sitemap entry, verbatim count, empty `h1`, question file, LLM-intel file, board status, Search Console baseline with its barrier, inbound links, retired-term hits | `python3 scripts/page_intake.py <slug>` exits 2 on a slug no data file knows | none — the intake rides on the board and is approved at stop 2 |
| 3 | §4 URL, canonical and redirect decision | the page's row in the URL-family decision; a slug that moves gets its 301 in `data/redirects.json`, then `npm run redirects` | the slug, canonical and redirect rows the board records in `meta.slug` | `npm run check:redirects` (one hop, target built, nothing shadowed) | none — decided once for the cluster, on the answer board |
| 4 | §5 Research on hand, inventory before any fetch | `scripts/page_intake.py` (arrives in Task 24) lists what is banked for the slug; reuse it, and fetch through the spend guard only what is missing | an absent figure written `NOT FETCHED — <barrier>`, never bare and never guessed | `npm run check:barriers` (Task 21's barrier lint) and `npm run test:py` (the spend guard) | none |
| 5 | §6 Competitor research and query fan-out | `bsuk-query-augmentation` for the slug (top 5 on Google and Bing, merged); `python3 scripts/query_augment.py --extract-h2 <file>` on each saved page, then `python3 scripts/query_augment.py --competitor-metrics <slug>`; `bsuk-reddit-threads` against the shared thread ledger (`python3 scripts/thread_ledger.py --known <url>` before a thread is read, `--seed` for a new page's questions); `bsuk-llm-keyword-intel` for the slug | `data/queries/<slug>.json` (competitors with their metrics, `section_target`, `word_target`, `extra_sections`, FAQ picks) and `docs/research/llm-intel/<slug>-<date>.json`; when `word_target` has no median (every competitor a marketplace listing), the barrier is recorded on the board and the word band is the breeder's decision on the answer board | `npm run check:queries`, `npm run check:competitors`, `npm run check:gaps`, `npm run check:threads` | none |
| 6 | §7 Keyword deliverables and metrics | `python3 scripts/keyword_variants.py <slug>` for the four extra types; `python3 scripts/keyword_metrics.py <slug>` for the ours-vs-top-5 table on the board (block 4b; its JSON report is git-ignored) | the section keywords in the record, and the metric table (unique terms, variations, exact match per tag, first 100 words, title front-load) | `keyword-variants-missing` in `scripts/family_rules.py`; `python3 scripts/keyword_metrics.py <slug>` exits 1 when `title-front-load` or `first-100-words` fails a new page | none |
| 7 | §8 Entities and co-occurrence | `python3 scripts/ontology_seed.py --check`; board block 5 groups the entities by class | every entity a section names, in `data/bsuk-ontology.json` with a source | `python3 scripts/ontology_seed.py --check`; a BLOCKED entity refuses approval | none |
| 8 | §9–§10 Gaps, angles and the strategy | the page's row in the approved cluster strategy (`docs/superpowers/sessions/2026-09-25-location-pages-strategy.md`); `grill-me --brief` for a page that strategy does not name; `bsuk-strategy-synthesizer` when a new strategy is needed | board block 1: goal, scope, gates, done, out of scope, strategy and why, the angles considered | `python3 scripts/strategy_cite_check.py <strategy.md>` on any new strategy | STOP 1 — the brief, only for a page with no row in the approved strategy |
| 9 | §11–§12 Distribution matrix and the H1–H6 outline | the record `data/boards/<slug>.json`, then `python3 scripts/build_page_board.py <slug>`: block 2 (H1 and meta), block 3 (outline, heading collisions, every link), block 3a (verbatim set), block 4 (distribution, why each section is here) | the approved outline: sections derived from the competitors' count + 3, grouped, each with its framework and `why_source` | `schemas/board.schema.json` through `scripts/pageboard.py`; `python3 scripts/board_approve.py <slug>` (after `npm run -s build`: it reads the built site) refuses a header that collides with a built page or with another approved-but-unbuilt board, and any block 7b FAIL | none — approved with row 10 |
| 10 | §13–§14 Components, hero refresh and the tool decision | `python3 scripts/build_board_previews.py <slug>`, then the board: block 3c (navigation), block 5b (the kit), block 6 (three styles per section at 1280 / 768 / 375), block 7b (the project 5 rules) | the component tuple, the page's own hero and counter styles, a refresh delta on every section | `python3 scripts/board_approve.py <slug>`; `tests/py/test_rule16_gate.py` refuses a shared hero or counter | STOP 2 — the breeder approves the board, which carries rows 2 and 6–10 |
| 11 | §15 Images and the Asset Gate | `python3 scripts/image_candidates.py <slug> --write`; `python3 scripts/ingest_image.py folder`, `draft`, then `publish`; board block 7 on its second pass | an image on the hero and every body H2 and H3, each with its `assets[]` row and an approved file; each body image directly after its heading in the uniform box (`box="uniform"`, or `box="tall"` for a portrait); a new portrait baked `--og-style A` (`python3 scripts/reframe_og.py --style contain`), never blurfill, and any bleed around an in-body image in the design colour (bone), never grey or black | `python3 scripts/board_gate.py <slug>` (also run for every rebuilt page by `npm run check:boards`, inside `npm run check:all`, after a fresh `npm run -s build`) | STOP 3 — the Asset Gate: a generated image is approved by its sha12 pick before it is published |
| 12 | §16 Build from the outline | for a page that exists: `python3 scripts/facts_preserved_check.py --extract <slug>` and `python3 scripts/verbatim_set_check.py --extract <slug>` FIRST; then the builder skill from the table above; `npm run build`; `python3 scripts/outline_provenance_check.py <slug>`; then add the slug to `data/facts/rebuilt.json` and the page to `tests/render/targets.json` | the built page in `dist/<route>/index.html`, written from its own outline and nothing else | `npm run check:all` (parity, facts, links, verbatim, outline, board gate, retired facts) | none |
| 13 | §17 Responsive typography, spacing and scroll | `npm run test:render:meta` first, then `npm run test:render:pages` (375 / 768 / 1280), which rebuilds the scorecards | `data/quality/scorecards/<slug>-<date>.json` with every check's examined count | `npm run test:render:pages`: a blocking IMG, LAYOUT or NAV row, a check that examined zero nodes, or on a new page (from board approval on) any of the four promoted checks: `hero-counter-separation`, `h3-image-first`, `sem-section-opening-paragraph`, `sem-title-case-headings` | none |
| 14 | §18 Harden — the `impeccable` pass | invoke the `impeccable:impeccable` skill on the built page at 375 / 768 / 1280, checked in a painting browser (Playwright or a real Chrome window, never a DOM-only read); commit its fixes; then `scripts/page_run_record.py` (arrives in Task 25): `python3 scripts/page_run_record.py <slug> impeccable --findings <n> --fixed <n>` | every finding fixed or deferred with its reason, and the `impeccable` key of `data/page-runs/<slug>.json` (date, widths, findings, fixed, deferred, commit) | `npm run gate:page -- <slug>` fails while the key is missing, a width is missing, a finding is neither fixed nor deferred, or the key's commit is older than the page's last source change | PREVIEW — only when it proposes a visual change: preview before apply (working rule 6); the palette never changes |
| 15 | §18 Harden — the `frontend-design` pass | then invoke the `frontend-design:frontend-design` skill the same way, at the same three widths, in a painting browser; commit its fixes; then `python3 scripts/page_run_record.py <slug> frontend-design --findings <n> --fixed <n>` with `scripts/page_run_record.py` (arrives in Task 25) | the `frontend_design` key of `data/page-runs/<slug>.json` | `npm run gate:page -- <slug>` fails on the same four conditions for this key | PREVIEW — only when it proposes a visual change: preview before apply (working rule 6); the palette never changes |
| 16 | §18 Harden — the static scan | `python3 scripts/page_hardening_scan.py <route> --fail-on-error` (the page, its template and data, and the kit) | 0 ERROR, every WARN triaged real, dead code or false positive | `python3 scripts/page_hardening_scan.py <route> --fail-on-error` (exit 1 on an ERROR, exit 2 on a route with no built page), run twice more by the row 17 runner | none |
| 17 | §19 Gates, each run twice | `scripts/gate_page.py` (arrives in Task 25): `npm run gate:page -- <slug> --skip-record` runs dup (body and `--headers`), the final audit on the profile above, hardening, AEO and evidence (`python3 scripts/evidence_audit.py <route> --type <profile> --fail-on-error`: on a new page an unledgered health or credential claim is an ERROR), twice, and diffs the two runs; then `python3 scripts/quality_report.py` and `python3 scripts/perf_audit.py <route>` (5 runs, the warm median of runs 2–5) | `docs/reports/gate-page/<slug>.json` with both runs and their diff | `npm run gate:page -- <slug> --skip-record` exits 1 on any FAIL or any difference between the runs | none |
| 18 | §19 Verification before completion | invoke the `superpowers:verification-before-completion` skill before any "page done" or "ready for approval" claim; `scripts/page_run_record.py` (arrives in Task 25) runs and records the evidence: `python3 scripts/page_run_record.py <slug> verification --run "npm run -s check:all" --run "npm run gate:page -- <slug> --skip-record" --claim "<claim>"`; then `npm run gate:page -- <slug>` with the record | the `verification_before_completion` key of `data/page-runs/<slug>.json`: each command, its exit code and its examined count, and the claims it verified | `npm run gate:page -- <slug>` fails while the key is missing, a command exited non-zero, `check:all` or the gate run is not among the commands, or the key's commit is older than the page's last source change | none |
| 19 | §20 The measurement ledger | `scripts/measurement_ledger.py` (arrives in Task 26): `python3 scripts/measurement_ledger.py <project> --slugs <slug>` | M1–M3, M6, M8–M10, M12, M13 and M18 as numbers, pasted into the gate report | `python3 scripts/measurement_ledger.py` exits 1 when M1, M2, M8 or M10 fails | none |
| 20 | §21 LLM visibility | the page's LLM-intel file from row 5 (one engine, one query); `python3 scripts/aeo_audit.py <route> --fail-on-error`, also run twice by the row 17 runner | the fetched denominator (1 of 1, or `NOT FETCHED — <barrier>`), the answer structure, the engine terms the page lacks | `python3 scripts/aeo_audit.py <route> --fail-on-error` | none |
| 21 | §22 Deploy and close | `python3 scripts/rendered_changes.py --base <ref> --json` (writes the report only; the dist-hash manifest is recorded after a successful IndexNow submit, in project 6); the build's postbuild regenerates the sitemaps; invoke the `superpowers:verification-before-completion` skill again before the gate report says PASS; `session-closer`; the gate report published as an Artifact with its `.md`; commit on the project branch and never push | docs/reports/rendered-changes.json (the slugs whose built output changed: project 6's IndexNow list), the gate report, the Known Issues update | `npm run check:sitemaps` and `npm run check:all` | none — the live 200 and IndexNow wait for project 6 |

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
project 6.
