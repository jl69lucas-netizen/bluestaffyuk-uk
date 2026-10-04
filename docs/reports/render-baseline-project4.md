# Render harness baseline — project 4 (page rebuilds)

This is the live baseline for project 4. It supersedes
`docs/reports/render-baseline-project3.md`, which is the published record of the 2026-09-19
run and is not regenerated. It was filled at Task 19 (close-out) from the 2026-09-22 scorecard
run, and `npm run baseline` holds it to the scorecards from here on.

## Gate results

From `docs/reports/page-rebuilds-run.log`, identical in both runs:

| Gate | Result |
|---|---|
| `npm run test:render:meta` | 370 passed, 38 skipped — exit 0 |
| `npm run test:render:pages` | 54 passed, 6 failed — exit 1 |
| `node scripts/build_scorecard.mjs --run first` | 189 defect rows across 20 page scorecards |
| `python3 scripts/render_baseline.py --check --out docs/reports/render-baseline-project4.md` | 0 problems |

Blocking rows fell **58 → 6** against project 3. The six are two routes project 4 did not
rebuild, at three viewports each (Known Issue 31): `/available-puppies/` (`sem-heading-order`,
H1→H3 at the first puppy card) and `/uk-locations/blue-staffy-puppies-uk/`
(`nav-jump-target-lands`, `#Staffy-adoption`). **No rebuilt page carries a blocking row**, and
`schema-date-modified-present`, `img-srcset-within-2x` and `layout-tap-target-size` are at zero
site-wide.

## Defect rows by family

Rows are comparable across families; instances are not. Severity is the check's own
`severity` field in `tests/render/checks/*.ts` — the scorecard JSON carries none — so a family
can carry both kinds. Everything between the generated markers below is produced by
`python3 scripts/render_baseline.py --out docs/reports/render-baseline-project4.md`; `npm run
baseline` fails if it drifts. Do not hand-edit it.

<!-- generated:start -->
Scorecard run 2026-10-04 — 21 page scorecards, 212 defect rows.

| Family | Blocking rows | Advisory rows | Pages affected |
|---|---|---|---|
| A11Y | 0 | 0 | 0 |
| CSS | 0 | 105 | 21 |
| DUP | 0 | 30 | 10 |
| FORM | 0 | 0 | 0 |
| IMG | 0 | 29 | 15 |
| LAYOUT | 0 | 12 | 4 |
| NAV | 0 | 0 | 0 |
| SCHEMA | 0 | 0 | 0 |
| SEM | 0 | 36 | 8 |
| **Total** | **0** | **212** | **21** |

Rows by check: `css-no-dead-component-rule` 57, `css-class-resolves` 48, `dup-no-sibling-crossover` 30, `img-not-upscaled` 25, `sem-all-six-levels` 24, `layout-h3-image-first` 12, `sem-title-case-headings` 9, `img-face-visible` 4, `sem-section-opening-paragraph` 3.
<!-- generated:end -->
