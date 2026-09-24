# Competitor registry candidates

Sites another agent found that have no entry in `data/competitors.json`. `bsuk-competitor-registry` reads the `open` rows on its next full discovery, add or refresh. A candidate is registered only when one of that run's seed searches returns it and the user approves the proposal; this list is never a registry row and never a reason to add one.

The controller adds a row when a hand-back names a site with no registry id. The registry agent changes only the status, after approval: `added <YYYY-MM-DD>` or `not in the seed results <YYYY-MM-DD>`.

| Domain | Found by | Where | Found on | Status |
|---|---|---|---|---|
| dbrg.uk | bsuk-llm-keyword-intel | cited in the Leeds engine answer, `docs/research/llm-intel/blue-staffy-puppies-for-sale-leeds-2026-09-23.json` (`registry_id` null) | 2026-09-23 | open |
