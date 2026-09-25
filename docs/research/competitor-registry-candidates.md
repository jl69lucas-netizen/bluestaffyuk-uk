# Competitor registry candidates

Sites another agent found that have no entry in `data/competitors.json`. `bsuk-competitor-registry` reads the `open` rows on its next full discovery, add or refresh. A candidate is registered only when one of that run's seed searches returns it and the user approves the proposal; this list is never a registry row and never a reason to add one.

The controller adds a row when a hand-back names a site with no registry id. The registry agent changes only the status, after approval: `added <YYYY-MM-DD>` or `not in the seed results <YYYY-MM-DD>`.

| Domain | Found by | Where | Found on | Status |
|---|---|---|---|---|
| dbrg.uk | bsuk-llm-keyword-intel | cited in the Leeds engine answer, `docs/research/llm-intel/blue-staffy-puppies-for-sale-leeds-2026-09-23.json` (`registry_id` null) | 2026-09-23 | open |
| akc.org | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/staffy-puppies-for-sale-essex-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| babbington-hall.co.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/staffy-puppies-for-sale-nottingham-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| bonosue.co.uk | bsuk-llm-keyword-intel | cited or listed in 2 engine answers (e.g. `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| bullybillows.com | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/staffy-puppies-for-sale-nottingham-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| bullyview.com | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/staffy-puppies-for-sale-essex-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| earlsgravebullterriers.com | bsuk-llm-keyword-intel | cited or listed in 15 engine answers (e.g. `docs/research/llm-intel/blue-staffies-newcastle-under-lyme-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| freedoglistings.co.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/blue-staffy-puppies-dundee-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| futurefrenchies.uk | bsuk-llm-keyword-intel | cited or listed in 2 engine answers (e.g. `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| gunfields.com | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/blue-staffy-puppies-for-sale-in-leicester-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| jerrygreendogs.org.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/staffy-puppies-for-sale-nottingham-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| luminastaffs.co.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/blue-staffy-puppies-edinburgh-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| mrsmurrays.co.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/blue-staffy-puppies-aberdeen-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| norfolkterrierclub.co.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/blue-staffy-puppies-for-sale-in-leicester-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| northerncountiesstaffordshirebullterrierclub.co.uk | bsuk-llm-keyword-intel | cited or listed in 2 engine answers (e.g. `docs/research/llm-intel/blue-staffy-puppies-birmingham-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| oakwooddogrescue.co.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/blue-staffy-puppies-hull-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| rspca-radcliffe.org.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/staffy-puppies-for-sale-nottingham-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| rspcahull.org.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/blue-staffy-puppies-hull-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| s-a-r-a.org.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/blue-staffy-puppies-middlesbrough-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| sbtca.com | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/staffy-puppies-for-sale-essex-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| scsbts.com | bsuk-llm-keyword-intel | cited or listed in 5 engine answers (e.g. `docs/research/llm-intel/blue-staffy-puppies-dundee-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| stormefexboxers.com | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/staffy-puppies-for-sale-cornwall-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| thebritishboxerclub.co.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/blue-staffy-puppies-oxford-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| thebullterrierclub.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/staffy-puppies-for-sale-nottingham-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| thedogretreat.co.uk | bsuk-llm-keyword-intel | cited or listed in 1 engine answer (e.g. `docs/research/llm-intel/blue-staffies-newcastle-under-lyme-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| thekennelclub.org.uk | bsuk-llm-keyword-intel | cited or listed in 17 engine answers (e.g. `docs/research/llm-intel/blue-staffies-newcastle-under-lyme-2026-09-25.json`, `registry_id` null); the Kennel Club's former domain, an alias of the `royalkennelclub` entry, not a new competitor | 2026-09-25 | open |
| thestaffordshirebullterrier.co.uk | bsuk-llm-keyword-intel | cited or listed in 3 engine answers (e.g. `docs/research/llm-intel/blue-staffy-puppies-for-sale-in-leicester-2026-09-25.json`, `registry_id` null) | 2026-09-25 | open |
| ueniweb.com | bsuk-llm-keyword-intel | cited or listed in 6 engine answers (e.g. `docs/research/llm-intel/blue-staffies-newcastle-under-lyme-2026-09-25.json`, `registry_id` null); a hosted site builder, not a competitor: a platform note only, never a registry row | 2026-09-25 | open |
