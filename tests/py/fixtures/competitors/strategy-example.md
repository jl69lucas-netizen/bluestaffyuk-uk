MISSING: docs/research/keyword-gap-<date>.md · MISSING: docs/research/llm-intel/blue-staffy-puppies-manchester-uk-<date>.json · MISSING: data/competitors.json — carrying on with what exists. fresh: `docs/research/gap-matrix-2026-09-24.md`, `docs/research/competitors/a.json`, `docs/research/competitors/b.json`, `docs/research/competitors/c.json`, `docs/research/competitors/bsuk.json`, `data/page-map.json`, `data/locations.json`.

# Location pages strategy — 2026-09-24

## What the research can and cannot carry

- **The Manchester AI answer is not usable yet.** A saved answer sits at `data/queries/raw/blue-staffy-puppies-manchester-uk/ai_engines.response.json`, but a raw answer is not a source: its citations reach a strategy only through a `docs/research/llm-intel/` file, and none exists for Manchester. Nothing below leans on what that answer says or cites. Running `bsuk-llm-keyword-intel` on it is the first unblocking step in either strategy.
- **No keyword-gap file**, so there are no gap scores, bands or "exists, not indexed" rows to quote. The stub status below comes from `data/locations.json` and `data/page-map.json` instead.
- **No tiers** (`data/competitors.json` is missing). Competitors a, b and c are therefore used only as evidence of *coverage* (what they have pages for). None of them is proposed as a link target, a model to copy or a source of wording, because any of them could be tier 5.
- **GSC and GA4 are NOT FETCHED until project 6.** No traffic, ranking, impression or search-volume claim appears anywhere here.
- **The matrix's "BSUK has it: no" for Manchester is a stub, not an absence.** `data/locations.json` holds `/uk-locations/blue-staffy-puppies-manchester-uk/` as a five-word noindex page with the `stub` defect; the BSUK profile does not see it because it is not a real page. The same holds for Birmingham (`/uk-locations/blue-staffy-puppies-birmingham/`), Leeds (`/uk-locations/blue-staffy-puppies-for-sale-leeds/`), Liverpool (`/uk-locations/staffy-puppies-for-sale-liverpool/`) and London (`/uk-locations/blue-staffy-puppies-london/`, where the matrix says "yes" but the page is still a noindex stub with an empty H1). Every one of these is a **project 5 rebuild of that URL**, never a new page and never a second URL for the same city.

## Strategy A — Contested cities first: rebuild the stubs competitors cover

**Thesis.** The only location signal every competitor shares is Manchester (3/3 on both the keyword and the city rows of the matrix, top of the priority queue). Birmingham, Leeds and Liverpool are each covered by one competitor. BSUK has a URL for all four, but each is a noindex stub. Rebuild those stubs into full location pages, Manchester first, with FAQPage schema built in from day one, so the cities competitors actually contest stop being empty.

**Target clusters.**
- "blue staffy puppies <city>" for Manchester, Birmingham, Leeds, Liverpool, London.
- The buyer questions a city page answers: delivery to that city, health testing of the parents, what the puppy leaves with, how to view.

**Cluster → page map.**
| Cluster | Page | New or rebuild |
|---|---|---|
| blue staffy puppies manchester | `/uk-locations/blue-staffy-puppies-manchester-uk/` | project 5 rebuild |
| blue staffy puppies birmingham | `/uk-locations/blue-staffy-puppies-birmingham/` | project 5 rebuild |
| blue staffy puppies leeds | `/uk-locations/blue-staffy-puppies-for-sale-leeds/` | project 5 rebuild |
| blue staffy puppies liverpool | `/uk-locations/staffy-puppies-for-sale-liverpool/` | project 5 rebuild |
| blue staffy puppies london | `/uk-locations/blue-staffy-puppies-london/` | project 5 rebuild |

**Internal-link plan.** Each rebuilt city page links up to `/uk-locations/blue-staffy-puppies-uk/` (the indexed UK location hub) and across to the existing health guide `/blue-staffy-health-uk/` and buying guide `/uk-blue-staffy-puppy-buying-guide/`. The UK hub links down to every rebuilt city. Anchors are Link-First (`rules/links.md`) and every link goes on the page board before approval (working rule 12). No link to any competitor.

**Schema plan.** FAQPage on every rebuilt city page (the matrix lists FAQPage as a high-priority schema gap). Organization stays as it is. Product is not added to location pages: a location page does not sell one specific puppy, and prices come only from the breeder's puppy data, never from old copy.

**Build order and effort.** Manchester, then Birmingham, Leeds, Liverpool, London, then the remaining stubs (Bristol, Leicester, Coventry, Cardiff, Cornwall, Essex, Glasgow, Nottingham, Wolverhampton, South Yorkshire, Newcastle-under-Lyme). Each is a full page build through `bsuk-location-page-builder` with its own outline, board and FAQ; roughly one page per build session. Stubs have no verbatim set worth keeping beyond the city name, so the faithful-rewrite burden is light.

**Expected outcome (no traffic figure).** BSUK stops showing an empty noindex page for the one city every competitor covers, and the four other contested cities get real pages on their existing URLs. The rebuilt pages become indexable, carry FAQPage, and give the llm-intel run a real page to check the Manchester answer against.

**Risks.**
- The already-indexed location pages (Aberdeen, Dundee, Edinburgh, Hull, Inverness, Middlesbrough, Oxford, Sunderland, York) keep their current thin, schema-less template for longer.
- Without the llm-intel file, the Manchester page is written blind to what the AI answer rewards.
- Five pages in the same cluster invite sibling prose copying; each must be written from its own outline (rules/copy.md).

## Strategy B — Deepen what is already indexed: price and FAQ upgrade across the live template

**Thesis.** The price topic is a wider gap than any single city after Manchester: "staffy puppy price" is 2/3 on the keyword row and "price" is 2/3 on the page-type row, while each of the non-Manchester cities is only 1/3. Every indexed location page already answers a price question in its FAQ but carries no schema at all. Instead of rebuilding stubs, upgrade the location template that is already indexed: add a proper price-and-what's-included section, a buyer-question FAQ with FAQPage schema, and a link to a price explainer, then roll it across every live location page. City stubs wait.

**Target clusters.**
- "staffy puppy price" and the cost questions around it (what affects the price, deposits, delivery charges).
- "health tested staffy puppies" and "kc registered staffy puppies" (each 1/3), answered in the upgraded FAQ.

**Cluster → page map.**
| Cluster | Page | New or rebuild |
|---|---|---|
| staffy puppy price | price section + FAQ on each indexed location page; explainer on the existing `/buy-staffy-puppies-for-sale-uk/` | upgrade of existing pages |
| health tested / KC registered | FAQ block on each indexed location page, linking to `/blue-staffy-health-uk/` | upgrade of existing pages |
| blue staffy puppies manchester | left as the stub until the template is done | project 5 rebuild, deferred |

**Internal-link plan.** Every indexed location page links to the price explainer and the health guide from its FAQ answers; the UK hub links to all indexed city pages. No competitor links.

**Schema plan.** FAQPage across all indexed location pages. Product only on puppy pages, where a real puppy and a breeder-confirmed price exist; never on a location page.

**Build order and effort.** One template change, then a content pass on each indexed location page (every FAQ answer written fresh per page), then the stubs. Lower effort per page than A, but it touches every live page at once, and price copy needs the breeder to confirm current prices first (rule 9: no invented prices; the prices in the old FAQ copy may be stale).

**Expected outcome (no traffic figure).** Every indexed location page gains structured FAQ answers and a price answer, closing the FAQPage schema gap site-wide; the price topic gets coverage without adding a new URL.

**Risks.**
- Manchester, the only city at 3/3, stays a five-word noindex stub for the whole of this strategy.
- Blocked on the breeder confirming prices before any price copy ships.
- A shared price/FAQ block across many location pages is exactly the sibling-copy pattern rules/copy.md forbids; each page's FAQ must be written separately, which erodes the effort saving.

## Recommendation

**Pick: Strategy A — contested cities first, Manchester first (Recommended).**

### Why

- Manchester is the only location covered by every competitor: `blue staffy puppies manchester` is 3/3 and the Manchester city row is 3/3, both marked high and at the top of the priority queue in the gap matrix. BSUK's own URL for it, `/uk-locations/blue-staffy-puppies-manchester-uk/`, exists but is a noindex stub, so the fix is a rebuild on a URL BSUK already owns.
- Birmingham, Leeds and Liverpool are each 1/3 in the matrix and each has a BSUK stub URL too, so the same rebuild procedure closes all four contested city gaps without minting a single new URL.
- FAQPage is a high-priority schema gap at 1/2 (with 1 competitor not fetched); building it into each rebuilt city page closes it on the pages that most need it, rather than retrofitting it onto pages that are already indexed.
- The price gap (2/3 on both the keyword and page-type rows) is real but is a page-type gap, not a location gap: it belongs to the buy/price cluster, not to the location pages, and it is blocked on breeder-confirmed prices anyway.

### The pick's downside

Strategy A leaves the already-indexed location pages thin and schema-less for longer, and it does nothing for "staffy puppy price" (2/3) inside this project — Strategy B would have put a price answer and FAQPage on every live location page first. A also asks for full page builds, one city at a time, where B's upgrade is a lighter pass per page. And until the Manchester llm-intel file exists, the first rebuild is written without evidence of what the AI answer cites.

### First three build steps

1. Run `bsuk-llm-keyword-intel` on the saved Manchester answer to produce `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-<date>.json`, and run the keyword-gap script so the stub rows carry scores; neither is done by this agent.
2. Hand Manchester to `bsuk-content-architect` as a project 5 rebuild of `/uk-locations/blue-staffy-puppies-manchester-uk/` (not a new page), with FAQPage in the schema plan and the UK hub, health guide and buying guide as its internal links; then `grill-me` on that page when it is built.
3. Repeat the same rebuild for Birmingham, Leeds and Liverpool on their existing stub URLs, each written from its own outline.

## Sources

- `docs/research/gap-matrix-2026-09-24.md`
- `data/locations.json`
- `data/page-map.json`
