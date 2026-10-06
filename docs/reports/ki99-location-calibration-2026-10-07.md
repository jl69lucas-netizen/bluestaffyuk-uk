# Known Issue 99: calibrating the location head-term ceilings (2026-10-07)

Plan: `docs/superpowers/plans/2026-10-07-manchester-page-run.md` Task 13.

**Outcome: no calibration was written.** The saved data does not support one. `data/quality/evidence-budgets.json` is unchanged (`"calibrated": null`, `budgets.location` as it was). London's `budgets_by_slug` entry stays. Three options follow, with one recommended. The breeder has to pick one before the location ceilings can change. Until then Manchester's gate:page will hit the same uncalibrated defaults that London hit.

## 1. How it was measured

- **Counter.** The counts come from `scripts/evidence_audit.py` itself. Nothing was re-implemented. Each page went through `evidence_audit.term_budget(html, "location", probe, slug=…)`, where `probe` is the live budgets file with every `budgets.location` ceiling set to `-1` and `budgets_by_slug` emptied. That makes `term_budget` return every term with its count. The patterns are the live `terms`. `{city}` resolves through `city_for`/`city_pattern` on the city's own slug (`uk-locations/blue-staffy-puppies-manchester-uk` → Manchester, `uk-locations/blue-staffy-puppies-london` → London).
- **Scope.** The scope is `<main>` (`evidence_audit.main_html`). A saved page with no `<main>` element is read from its `<body>`, wrapped in `<main>` before the call. If it were not wrapped, `main_html` would fall back to the whole file, `<title>` included. The scope is the same as `docs/research/manchester-page-run/serp-findings.md` "Head-term counts", and every count below matches that table.
- **Words.** The word count is the whitespace-split word count of `text_of(main_html(…))`, the same text the terms are counted in. Density is per 1,000 of those words.
- **Listing or prose.** Each page is classified by `query_augment.listing_reason(query_augment.page_metrics(html))`, the test board block 4c uses.
- **Board 4c comparison.** The cross-check in §3 counts the same pages with `scripts/term_density.py` `count_terms`, which is block 4c's counter.
- **Built page.** London as built is `dist/uk-locations/blue-staffy-puppies-london/index.html`, built 2026-10-07 00:09. No file under `src/` and none of `data/{settings,puppies,locations,reviews,faq}.json` is newer, so the build was not re-run.

## 2. Measurements (gate scope, counts and per-1,000-word density)

Columns: blue staffy · staffy puppies · Staffordshire Bull Terrier · puppies for sale · city · UK. The count comes first, with the density per 1,000 words in brackets.

**Manchester** (`data/queries/cache/blue-staffy-puppies-manchester-uk/<n>.html`)

| # | Page | Kind (`listing_reason`) | Scope | Words | blue staffy | staffy puppies | SBT | pfs | Manchester | UK |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | pets4homes · Manchester | listing (grid 100%) | body | 2,144 | 4 (1.87) | 5 (2.33) | 47 (21.92) | 3 (1.40) | 20 (9.33) | 3 (1.40) |
| 2 | staffie-owners · Salford | listing (grid 81%) | main | 2,685 | 1 (0.37) | 34 (12.66) | 11 (4.10) | 10 (3.72) | 69 (25.70) | 2 (0.74) |
| 3 | freeads · Manchester | prose* | body | 5,247 | 9 (1.72) | 3 (0.57) | 35 (6.67) | 7 (1.33) | 20 (3.81) | 1 (0.19) |
| 4 | gumtree · Manchester | listing (grid 76%) | body | 994 | 1 (1.01) | 1 (1.01) | 3 (3.02) | 1 (1.01) | 12 (12.07) | 1 (1.01) |
| 5 | puppies.co.uk · Manchester | listing (ItemList, 12% in sections) | main | 2,213 | 0 (0) | 0 (0) | 19 (8.59) | 2 (0.90) | 8 (3.62) | 2 (0.90) |
| 6 | staffie-owners · Manchester blue | listing (grid 82%) | main | 2,647 | 6 (2.27) | 37 (13.98) | 17 (6.42) | 8 (3.02) | 100 (37.78) | 2 (0.76) |
| 7 | staffie-owners · Manchester | listing (grid 82%) | main | 2,586 | 1 (0.39) | 35 (13.53) | 12 (4.64) | 10 (3.87) | 99 (38.28) | 2 (0.77) |
| 8 | pets4homes · UK "blue staf" | listing (grid 100%) | body | 2,159 | 7 (3.24) | 7 (3.24) | 51 (23.62) | 4 (1.85) | 6 (2.78) | 5 (2.32) |

**London** (`data/queries/cache/blue-staffy-puppies-london/<n>.html`)

| # | Page | Kind | Scope | Words | blue staffy | staffy puppies | SBT | pfs | London | UK |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | staffie-owners · Southall blue | listing (grid 81%) | main | 2,894 | 7 (2.42) | 39 (13.48) | 18 (6.22) | 9 (3.11) | 108 (37.32) | 3 (1.04) |
| 2 | staffie-owners · Paddington blue | listing (grid 80%) | main | 2,868 | 5 (1.74) | 35 (12.20) | 13 (4.53) | 10 (3.49) | 117 (40.79) | 5 (1.74) |
| 3 | staffie-owners · Uxbridge blue | listing (grid 81%) | main | 2,860 | 7 (2.45) | 38 (13.29) | 13 (4.55) | 10 (3.50) | 95 (33.22) | 5 (1.75) |
| 4 | staffie-owners · Camden Town blue | listing (grid 82%) | main | 2,894 | 6 (2.07) | 36 (12.44) | 13 (4.49) | 10 (3.46) | 118 (40.77) | 5 (1.73) |
| 5 | staffie-owners · London blue | listing (grid 82%) | main | 2,825 | 8 (2.83) | 38 (13.45) | 16 (5.66) | 9 (3.19) | 148 (52.39) | 4 (1.42) |
| 6 | pets4homes · London | listing (grid 100%) | body | 1,737 | 3 (1.73) | 8 (4.61) | 43 (24.76) | 2 (1.15) | 11 (6.33) | 4 (2.30) |
| 7 | freeads · London | prose* | body | 5,143 | 4 (0.78) | 9 (1.75) | 31 (6.03) | 11 (2.14) | 8 (1.56) | 2 (0.39) |
| 8 | pets4homes · UK "blue" | listing (grid 100%) | body | 2,072 | 6 (2.90) | 9 (4.34) | 50 (24.13) | 3 (1.45) | 3 (1.45) | 6 (2.90) |
| 9 | englishbluestaffypuppies.com · homepage | prose | body | 825 | 5 (6.06) | 2 (2.42) | 19 (23.03) | 0 (0) | 3 (3.64) | 10 (12.12) |

\* Freeads counts as prose only because the listing test misses it. It is a feed of 45 adverts whose titles are `<div>`s and whose `ItemList` is microdata (serp-findings.md, "Word target").

**London as built** (`<main>`, 6,113 words): blue staffy **28** (4.58) · staffy puppies **22** (3.60) · Staffordshire Bull Terrier **10** (1.64) · puppies for sale **1** (0.16) · London **62** (10.14) · UK **20** (3.27) · bluestaffyuk **8**. Inside its headings alone (h1–h6 in `<main>`), London's page has blue staffy 19, staffy puppies 15, Staffordshire Bull Terrier 4, London 23 and UK 1.

**Pooled summary of the 17 competitor pages:**

| | blue staffy | staffy puppies | SBT | pfs | city | UK |
|---|---|---|---|---|---|---|
| raw median | 5 | 9 | 18 | 8 | 20 | 3 |
| raw max | 9 | 39 | 51 | 11 | 148 | 10 |
| density median /1k | 1.87 | 4.61 | 6.22 | 2.14 | 12.07 | 1.40 |
| density max /1k | 6.06 (Lon 9) | 13.98 (Man 6) | 24.76 (Lon 6) | 3.87 (Man 7) | 52.39 (Lon 5) | 12.12 (Lon 9) |
| current ceiling | 10 | 8 | 5 | 6 | 8 | 8 |
| London as built | 28 | 22 | 10 | 1 | 62 | 20 |

## 3. Why no calibration is defensible from this data

1. **The pool has no page like ours.** 15 of the 17 pages are marketplace listing grids. One of the two pages the listing test calls prose is also a feed. That leaves a single one-breeder page: englishbluestaffypuppies.com, a homepage of 825 words that is Bing #5 for London only. No page in either pool is a one-breeder city page in the 2,000–3,000-word band.
2. **The competitor numbers point both ways, so a max-based ceiling is wrong in both directions.**
   - On blue staffy and UK, the busiest competitor (9 and 10) uses the term less than London's approved headings alone (19 blue staffy). The listings name the breed "Staffordshire Bull Terrier" and "Blue Staffie", not our keyword. A ceiling of 9 would fail the design the breeder approved at STOP 3.
   - On city and staffy puppies, the maximum comes from listing furniture. Staffie Owners' filter and location lists put "London" 95–148 times in `<main>`, and their card text puts "Staffie puppies" 34–39 times. A ceiling taken from those pages (city 148) would never catch anything a writer would do.
3. **Our page is twice their length, so raw counts don't compare.** London's `<main>` is 6,113 words, about 2.3× the competitors' median of 2,647 (the median of the 17 word counts in §2). The gate has fixed counts, not densities. A density turned into a count needs a word basis. The two available bases disagree: the approved prose band tops out at 3,000 words, while the gate counts the whole of `<main>` (London: 6,113). A density of 52.39 × 3,000 words gives city 157, and × 6,113 gives city 320. On blue staffy, 6.06 × 3,000 gives 18, which is below London's 28.
4. **The gate and board block 4c count different things, so numbers alone cannot make them agree.** Known Issue 99 asks for the two to stop disagreeing. Counted on the same saved page, they read very differently. Block 4c's `term_density.count_terms` skips `nav`, `aside`, `form`, `select`, `footer` and hidden elements, and matches exact tokens: "staffy" is not "staffie", and "blue staffy" is not "blue staffies". The gate's regexes read all of `<main>` and match both spellings.

   | Same page | Gate count (`<main>`) | Block 4c count (body) |
   |---|---|---|
   | London #1 (Staffie Owners), city | 108 | 7 |
   | London #1, staffy puppies | 39 | 2 |
   | London #5 (Staffie Owners), city | 148 | 38 |
   | London as built, blue staffy | 28 | 22 |
   | London as built, staffy puppies | 22 | 9 |

   Until both use one counter and one scope, any ceiling the gate takes from 4c's bands, or 4c takes from the gate, compares two different measurements.
5. **London as built cannot be the default.** Known Issue 99's own decision says "The next city's budget comes from the calibration, never from London's entry".

## 4. Options

- **(a) (Recommended) Density ceilings on block 4c's counter.**
  - **What changes.** `evidence_audit.term_budget` would count location head terms with `term_density.count_terms`, in its scope and with its tokeniser. The location ceiling would become a per-1,000-word density: the top of block 4c's leader band, which is the maximum density among the pooled competitor bodies (pooled because the breeder ruled on 2026-10-02, q02, that listings count). That ceiling is multiplied by the page's own measured words.
  - **Ceilings today.** Measured on the 17 pages in block 4c's scope, the ceilings would be blue staffy 4.38 (Lon 9), staffy puppies 4.72 (Lon 8), Staffordshire Bull Terrier 28.49 (Lon 6), puppies for sale 3.31 (Man 7), city 17.50 (Man 7) and UK 7.30 (Lon 9).
  - **London fits.** In the same scope London as built reads 3.72 / 1.52 / 1.52 / 0.17 / 9.12 / 3.38, so it is inside every ceiling and its `budgets_by_slug` entry could be deleted.
  - **Why this one.** §3.4 shows the disagreement is between two counters, and §3.3 shows that fixed counts cannot follow a page twice the competitors' length. Only a shared counter with a density ceiling fixes both. The board then plans against the same number the gate enforces.
  - **Trade-off.** This is a gate code change: a density mode in `term_budget` and its tests, and the location budget switching counter, all reviewed and then re-run on London. The city and Staffordshire Bull Terrier ceilings are still set by listing pages, so they are loose. The blue staffy ceiling rests on one 685-word breeder homepage (685 in block 4c's scope), and London already uses 85% of it (3.72 of 4.38), so Manchester's outline would have to plan blue staffy under that line.
- **(b) Numbers only: fixed counts = the pooled gate-scope maximum density × 3,000 words** (the top of the location word band).
  - **Ceilings.** Blue staffy 18, staffy puppies 41, Staffordshire Bull Terrier 74, puppies for sale 11, city 157, UK 36.
  - **Cost.** No code change: just new numbers and the date.
  - **Trade-off.**
    - London fails blue staffy (28 > 18), so its entry has to stay.
    - City 157 and Staffordshire Bull Terrier 74 never bind.
    - The 3,000-word basis does not match the gate's 6,000-word `<main>`.
    - Block 4c and the gate still disagree (§3.4).
- **(c) Leave the defaults, and give each city an entry from its own approved board.** Each city gets a `budgets_by_slug` entry at STOP 3, set from that board's planned counts, the way London's was.
  - **Cost.** No code change, and nothing gets looser.
  - **Trade-off.** The location default never gates an approved page, so it stops working as a check. `calibrated` stays null. The two tools keep disagreeing. Every city adds an entry with a `_why`.

## 5. London's entry

**Decision: kept, unchanged.** No new ceiling was set, so the condition for deleting it ("delete it if the calibrated ceilings cover London as built") is not met. `tests/py/test_evidence_london_budget.py` is unchanged.

The entry still covers London as built. Today's counts are under or at the entry: blue staffy 28 against 32, staffy puppies 22 against 22, Staffordshire Bull Terrier 10 against 10, city 62 against 62 and UK 20 against 20. Blue staffy has come down from 32 since the entry was written. As a ratchet the entry could be lowered to 28, but that is a separate change and was not made here. Under option (a) the entry could be deleted. Under (b) it has to stay. Under (c) it stays, and becomes the pattern every city follows.

## 6. Reproducing the counts

```python
import copy, json, re, sys; sys.path.insert(0, "scripts")
import evidence_audit as ea
from _html import text_of
B = json.load(open("data/quality/evidence-budgets.json"))
probe = copy.deepcopy(B); probe["budgets_by_slug"] = {}
probe["budgets"]["location"] = {t: -1 for t in B["budgets"]["location"]}
def counts(html, slug):          # slug: uk-locations/<the city's slug>
    if not re.search(r"<main\b", html, re.I):
        html = "<main>" + re.search(r"<body\b.*</body>", html, re.S | re.I).group(0) + "</main>"
    words = len(text_of(ea.main_html(html)).split())
    return words, {t: n for t, n, _ in ea.term_budget(html, "location", probe, slug=slug)}
```
