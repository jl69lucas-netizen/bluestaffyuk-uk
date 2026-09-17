# Render harness baseline — end of project 2 (system transfer)

Captured 2026-09-17 at Task 16 Step 4, after `npm run build` (49 pages) and both render gates
run with `PUBLIC_FORMSPREE_ID` exported. This is the starting line projects 3 and 4 move; the
Task 20 gate report cites these numbers.

## Gate results

| Gate | Command | Result |
|---|---|---|
| Marker | `python3 scripts/marker_check.py` | `examined 231 files; 0 problems` |
| Meta | `npm run test:render:meta` | 315 passed, 36 skipped |
| Pages | `npm run test:render:pages` | 5 passed, 46 failed |
| Scorecard | `node scripts/build_scorecard.mjs --run first` | 265 defect rows across 17 pages (run=first, harness 2.0.0) |

Scorecard output: `data/quality/scorecards/<slug>-2026-09-17.json` (17 files).

The 46 pages-gate failures are the intended baseline, not a regression: Foundation migrated
WordPress bodies verbatim, so IMG/NAV/SCHEMA rows land on migrated content. No blocking row
appeared that was not already present in the 2026-09-16 scorecard.

## Defect rows by family

Rows are comparable across families; instances are not. Severity is the check's own
`severity` field in `tests/render/checks/*.ts` — the scorecard JSON carries none — so a family
can carry both kinds (SEM does). Everything between the generated markers below is produced by
`python3 scripts/render_baseline.py --write docs/reports/render-baseline-project2.md`; `npm run
baseline` fails if it drifts. Do not hand-edit it.

<!-- generated:start -->
Scorecard run 2026-09-17 — 17 page scorecards, 265 defect rows.

| Family | Blocking rows | Advisory rows | Pages affected |
|---|---|---|---|
| A11Y | 0 | 3 | 1 |
| CSS | 0 | 51 | 17 |
| DUP | 0 | 33 | 11 |
| FORM | 0 | 3 | 1 |
| IMG | 15 | 0 | 6 |
| LAYOUT | 4 | 0 | 2 |
| NAV | 18 | 0 | 6 |
| SCHEMA | 21 | 0 | 7 |
| SEM | 9 | 108 | 17 |
| **Total** | **67** | **198** | **17** |

Rows by check: `css-class-resolves` 51, `sem-all-six-levels` 51, `dup-no-sibling-crossover` 33, `sem-title-case-headings` 33, `sem-section-opening-paragraph` 24, `nav-jump-target-lands` 18, `schema-date-modified-present` 18, `img-srcset-within-2x` 15, `sem-heading-order` 9, `layout-tap-target-size` 4, `a11y-text-contrast-aa` 3, `form-inquiry-contract` 3, `schema-no-visible-date` 3.
<!-- generated:end -->

## DUP before and after Task 15's whitelist re-measurement

| Scorecard run | DUP rows | Pages with a DUP row | Total rows, all families |
|---|---|---|---|
| 2026-09-16 (pre-Task 15) | 42 | 14 | 277 |
| 2026-09-17 (this run) | 33 | 11 | 265 |

DUP fell by 9 rows on 3 fewer pages. That is the intended change: Task 15 re-measured the DUP
whitelist against BSUK's own chrome, so shared-shell text no longer reports as sibling
crossover. The only other change is FORM, 6 rows down to 3, from Task 15's re-based form contract; every
other check's row count is identical, so the all-family total falls by exactly those 12 rows.

## Deferred checks

Three, unchanged from Task 8: `layout-hero-counter-separation`, `layout-h3-image-first`,
`sem-statement-label-visible`. Each examines zero nodes and each carries its promotion
condition in `tests/render/targets.json > deferred_checks`. The scorecard prints all three as
DEFERRED rather than failing Guard 2.

The plan's Task 16 Step 2 named two further deferrals, `bottom-bar-under-tabbar` and
`analytics-double-load`. Neither id exists in BSUK's check registry — both belong to the source
project's Python page-hardening checker, which was not ported. `meta.spec.ts` asserts every
deferred id names a registered check, so adding them would have turned the meta gate red. They
are therefore not added; if project 3 or 6 ports those checks, defer them then.
