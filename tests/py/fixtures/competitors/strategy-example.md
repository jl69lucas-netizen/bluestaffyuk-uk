MISSING: docs/research/keyword-gap-<date>.md
MISSING: docs/research/llm-intel/blue-staffy-puppies-manchester-uk-<date>.json
MISSING: docs/research/llm-intel/<slug>-<date>.json for every other location page in scope
MISSING: data/competitors.json
fresh: docs/research/gap-matrix-2026-09-24.md (built 2026-09-24; its reports a, b, c and bsuk all fetched_on 2026-09-24), docs/research/competitors/a.json, docs/research/competitors/b.json, docs/research/competitors/c.json, docs/research/competitors/bsuk.json, data/page-map.json, data/locations.json — carrying on with what exists

# Location pages strategy — 2026-09-24

### Read this first

- **No keyword-gap file.** The Concrete Artifact's score column is the matrix N/M, headed "matrix N/M (no keyword-gap file)". No keyword-gap score or band is quoted anywhere.
- **No llm-intel file for Manchester (or any city).** The saved raw AI answer at `data/queries/raw/blue-staffy-puppies-manchester-uk/ai_engines.response.json` exists, but a raw answer is not a source: nothing from it reaches this strategy until `bsuk-llm-keyword-intel` turns it into `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-<date>.json`. So this strategy makes **no AI-answer claim** — not who is cited, not whether BSUK is cited, not what format the answer takes.
- **No data/competitors.json.** Competitors a, b and c still count toward every gap (tier unknown), but none of them is used as a link target, a page to copy, or a source of wording. Because tiers are unknown, no N/M count below can be said to be free of a tier-5 (suspect seller) report.
- **GSC and GA4 are not fetched until project 6.** No traffic, impression, click, ranking or search-volume figure appears here, as a reason or as an expected outcome.
- **Every gap city is a stub, so every gap city is a rebuild.** The BSUK profile says "no" for every matrix gap city, and the page map holds a noindexed stub at each: Manchester `/uk-locations/blue-staffy-puppies-manchester-uk/`, Birmingham `/uk-locations/blue-staffy-puppies-birmingham/`, Leeds `/uk-locations/blue-staffy-puppies-for-sale-leeds/`, Liverpool `/uk-locations/staffy-puppies-for-sale-liverpool/`, London `/uk-locations/blue-staffy-puppies-london/`. Each is a project 5 rebuild of that URL — never a new page, never a second URL for the same city.

## Strategy A — Contested cities first

**Thesis.** Rebuild the city stubs that competitors already rank pages for, starting with the city every competitor covers. The matrix says these are the places a searcher already finds a competitor's city page and finds nothing indexable from BSUK. Close those gaps first; the rest of the network follows.

**Target clusters.**
1. "blue staffy puppies manchester" — keyword row and city row both 3/3, priority high, top of the matrix's priority queue.
2. "blue staffy puppies birmingham / leeds / liverpool / london" — each 1/3, priority medium.
3. FAQPage schema on each rebuilt city page — schema row 1/2 with 1 report not fetched, priority high.

**Cluster → page map.** Each cluster maps to the existing stub URL in `data/page-map.json` (listed above). No new URLs. Keyword targets are the matrix's own keyword values ("blue staffy puppies manchester", etc.); the stub URLs whose slug does not match the keyword (Manchester's `-uk` suffix, Leeds's `for-sale-`, Liverpool's `staffy-puppies-for-sale-`) keep their URL — a slug change is an architect decision, not a strategy one.

**Internal-link plan.**
- Each rebuilt city page links up to the indexed UK hub `/uk-locations/blue-staffy-puppies-uk/`, and the hub links down to each city as it goes live (not before — no links to noindexed stubs).
- Each city page links across to the indexed trust pages that already exist: `/uk-blue-staffy-puppy-buying-guide/` and `/blue-staffy-health-uk/`.
- Contested cities link to each other only where geography makes it natural (Manchester ↔ Liverpool ↔ Leeds; Birmingham ↔ London via the hub).
- No competitor URL is linked (no registry; tiers unknown).

**Schema plan.** FAQPage on every rebuilt city page (the schema gap row that applies to a city page). Organization is already present (BSUK "yes"). Product (1/2) belongs to the listing page, not a city page — out of scope here.

**Build order and effort.** Manchester first (the only high city), then Birmingham, Leeds, Liverpool, London. The medium cities are tied in the matrix at 1/3 and nothing in the research separates them, so they follow the matrix's own row order. Each is a full rebuild from a near-empty stub — high effort per page, and the first one carries extra cost because it settles the city-page template the others reuse.

**Expected outcome (no traffic figure).** The matrix's only high city gap and every medium city gap close; each gap city turns from a noindexed stub into an indexable city page, and the matrix's city rows would read "BSUK has it: yes" on the next rebuild.

**Risks.**
- These are the cities where competitor pages already exist; a page that does not beat them on substance adds little.
- The medium cities each rest on 1/3; a tier-5 report among those would inflate a row, and with no registry that cannot be ruled out.
- No AI-answer evidence at all (llm-intel missing): the build cannot be steered toward what AI answers cite until that file exists.

## Strategy B — Uncontested network first

**Thesis.** Do not fight where competitors already are. Rebuild first the noindexed city stubs that **no** competitor report covers — Bristol, Leicester, Nottingham, Coventry, Wolverhampton, Cardiff, Glasgow, Cornwall, Essex, South Yorkshire, Newcastle-under-Lyme — so BSUK is the only indexable city page in the research set for those places. The contested cities come after.

**Target clusters.** One cluster per uncontested stub city from `data/locations.json` (e.g. "blue staffy puppies bristol"). None has a matrix row: the matrix lists only cities at least one competitor covers, so these carry no gap figure. The keyword for each comes from the stub's own title in `data/page-map.json`, not from any competitor.

**Cluster → page map.** Each uncontested city → its existing stub URL (for example `/uk-locations/blue-staffy-puppies-bristol-uk/`, `/uk-locations/staffy-puppies-for-sale-nottingham/`), rebuilt in project 5. The `/uk-locations/uk-staffordshire-bull-terrier-breeder/` stub is not a city and stays out.

**Internal-link plan.** Same hub-and-spoke through `/uk-locations/blue-staffy-puppies-uk/`, plus regional clusters among the new pages (Midlands: Birmingham-area stubs Coventry, Wolverhampton, Leicester, Nottingham; South West: Bristol, Cornwall). The contested stubs stay noindexed and unlinked until their turn.

**Schema plan.** FAQPage on every rebuilt page, as in A.

**Build order and effort.** The uncontested stubs first (many pages, each a full rebuild from nothing), then the contested cities. More pages before any matrix gap closes.

**Expected outcome (no traffic figure).** A wider indexable network sooner; no matrix gap row changes until the contested phase begins.

**Risks.**
- Closes **no** matrix gap row in its first phase — the top of the priority queue (Manchester) waits behind many pages.
- "No competitor covers it" rests only on the competitor reports in the matrix; the absence may be a research gap, not a market gap.
- No evidence in the research that searchers or AI answers want these cities; the bet is on absence of competition, not presence of demand.

## Recommendation

**Pick: Strategy A — Contested cities first.** This is a clear win, so the tie-break is not needed (it would also pick A: A closes the highest matrix share first).

### WHY

- Manchester is the only city gap every competitor covers: city row **3/3**, keyword row "blue staffy puppies manchester" **3/3**, both priority high and at the top of the matrix priority queue — and BSUK holds only a noindexed stub there.
- Birmingham, Leeds, Liverpool and London are each **1/3**, priority medium, and each is also a stub — A closes every city gap row in the matrix; B closes none in its first phase.
- The FAQPage schema row is **1/2** (1 report not fetched), priority high, and a city page is where BSUK can add it — A puts it on the pages the matrix ranks highest.
- The other high row a location page touches, "staffy puppy price" at **2/3**, is a page-type gap, not a city gap: neither strategy closes it, so it does not separate them (it needs its own strategy).

### The pick's downside

A spends the first builds where competitor pages already exist, so the Manchester page must beat every rival Manchester page in the research (3/3) to matter; and it leaves the uncontested noindexed stubs (Bristol, Nottingham, Cardiff and the rest) dark for longer — B would have them indexable first. The medium cities also rest on 1/3 each, with tiers unknown.

### First three build steps

1. Run `bsuk-llm-keyword-intel` for `blue-staffy-puppies-manchester-uk` so the Manchester rebuild has an llm-intel file (the raw answer alone cannot be used), and run the keyword-gap agent so the scores in the table below are replaced by keyword-gap scores.
2. Rebuild `/uk-locations/blue-staffy-puppies-manchester-uk/` (project 5) with FAQPage schema and hub, buying-guide and health links; `grill-me` before build. This page settles the city template.
3. Rebuild Birmingham, then Leeds, Liverpool and London on that template (project 5), linking each from the hub as it goes live.

## Concrete Artifact

### City-page build order

| topic or page | target keyword | matrix N/M (no keyword-gap file) | intent | link role | new or rebuild |
|---|---|---|---|---|---|
| Manchester `/uk-locations/blue-staffy-puppies-manchester-uk/` | blue staffy puppies manchester | 3/3 (high) | local transactional | spoke; links up to hub, across to buying guide and health | rebuild (project 5, stub) |
| Birmingham `/uk-locations/blue-staffy-puppies-birmingham/` | blue staffy puppies birmingham | 1/3 (medium) | local transactional | spoke | rebuild (project 5, stub) |
| Leeds `/uk-locations/blue-staffy-puppies-for-sale-leeds/` | blue staffy puppies leeds | 1/3 (medium) | local transactional | spoke; links to Manchester | rebuild (project 5, stub) |
| Liverpool `/uk-locations/staffy-puppies-for-sale-liverpool/` | blue staffy puppies liverpool | 1/3 (medium) | local transactional | spoke; links to Manchester | rebuild (project 5, stub) |
| London `/uk-locations/blue-staffy-puppies-london/` | blue staffy puppies london | 1/3 (medium) | local transactional | spoke | rebuild (project 5, stub) |
| UK hub `/uk-locations/blue-staffy-puppies-uk/` | blue staffy puppies uk | no matrix row | local navigational | hub; add a link to each city above as it goes live | existing indexed page, link update only |
| Uncontested stubs: Bristol, Leicester, Nottingham, Coventry, Wolverhampton, Cardiff, Glasgow, Cornwall, Essex, South Yorkshire, Newcastle-under-Lyme | the stub's own city keyword | no matrix row | local transactional | spokes | rebuild (project 5, stubs) — after the contested cities above |

Birmingham, Leeds, Liverpool and London are tied in the matrix; they follow its row order, and the table's order is the build order. York (the city the BSUK profile already has) and the other indexed city pages are not gaps and are not in this order.

## Sources

- `docs/research/gap-matrix-2026-09-24.md`
- `data/locations.json`
- `data/page-map.json`
