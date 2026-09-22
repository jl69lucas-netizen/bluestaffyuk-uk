# Render harness baseline — project 4 (page rebuilds)

This is the live baseline for project 4. It supersedes
`docs/reports/render-baseline-project3.md`, which is the published record of the 2026-09-19
run and is not regenerated. **Task 19 (close-out) fills it**: the generated block below is
empty until that run, and the gate table and the prose around it are written then, from the
run's own output.

## Gate results

Written at Task 19 from `docs/reports/page-rebuilds-run.log`.

## Defect rows by family

Rows are comparable across families; instances are not. Severity is the check's own
`severity` field in `tests/render/checks/*.ts` — the scorecard JSON carries none — so a family
can carry both kinds. Everything between the generated markers below is produced by
`python3 scripts/render_baseline.py --out docs/reports/render-baseline-project4.md`; `npm run
baseline` fails if it drifts. Do not hand-edit it.

<!-- generated:start -->
<!-- generated:end -->
