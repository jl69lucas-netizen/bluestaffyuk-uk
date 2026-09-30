# PetsForLove — competitor intel

- Root domain: petsforlove.co.uk · tier 2 · analysed 2026-09-25. This is the first report for this entry.
- Homepage gate: **failed — the site was not analysed.** The homepage gave no response at all, so there is no status code. Two Firecrawl scrapes (standard proxy, one live and one allowing the cache) failed on every engine. An emulated phone in Chrome DevTools timed out on both `https://petsforlove.co.uk/` and `https://www.petsforlove.co.uk/`, with a connection timeout and no page. The domain still resolves, but ports 80 and 443 did not answer from this machine either. This is not a bot check or a parked page: nothing was served at all.
- Every field below is NOT FETCHED ("homepage status none (no response: connection timed out)"), as the gate rule says. No key page was scraped, so the breed check before key-page scrapes never came up.
- **Registry fix for `bsuk-competitor-registry`:** the site did not respond on 2026-09-25. Whether it is down for now, moved or closed is that agent's call. A re-run later is the controller's call.
- The first map is saved at `maps/petsforlove.json` (52 URLs). The map came from Firecrawl's index, not from the live site. There is no `maps/petsforlove.home.html`, because no homepage HTML was returned.

## Trust
NOT FETCHED. The homepage gave no response, so no page was read.

## Content
NOT FETCHED. There is no homepage text to count. Under the gate rule `url_count` is NOT FETCHED too, though the map listed 52 URLs.

## Keywords
NOT FETCHED. No page text was fetched to run the keyword script on.

## Page types
NOT FETCHED. With a gated homepage, the Map list step and the classifier do not run. From its URL paths alone, the map looks like a pet classifieds board for many species. It has single adverts for dogs, cats, rabbits and birds, and per-breed list pages. One advert path names Staffordshire Bull Terrier puppies. None of this was typed or counted.

## Blog
NOT FETCHED. The map was not classified.

## Visual
NOT FETCHED. No raw HTML was returned for the homepage.

## Schema
NOT FETCHED. No raw HTML was returned, and no browser page loaded for a JSON-LD read.

## Cities
NOT FETCHED. No page was read.

## Conversion
NOT FETCHED. No page was read.

## Technical
- `mobile_layout_ok`: NOT FETCHED. The emulated phone (375 × 812, mobile user agent, touch) got a browser connection-error page, not the site, so the Mobile check evaluate had no page to measure and returned no numbers.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
Fetch: `map_calls` 1 · search map ran: no (the Map list script is not run on a gated homepage) · term: none · `search_added`, `search_breed_urls`, `search_adverts`, `home_added`, `map_list`: not produced (Map list and classifier not run) · scrapes 2 attempted, 0 returned content · credits 1 to 3 of a ceiling of 8.
- The first map (`limit` 500) returned 52 URLs, counted by script.
- Scrapes: both were homepage attempts (markdown and raw HTML, `onlyMainContent` off, standard proxy). Both failed on every engine and returned no content. No key page was attempted.
- Credits: 1 for the map. The two failed scrapes returned an error and no document; if Firecrawl billed them, the total is 3.
- Browser (no credits): one emulated-phone tab in Chrome DevTools. It tried the bare and `www.` homepages, both timed out, and the tab was then closed.

## Key insight
Nothing can be learned from petsforlove.co.uk this run: the site did not respond. It ranked 6th for "blue staffy puppies for sale" with a pet classifieds listing page. If it is gone, that position is open, and a dedicated breed page can take it rather than a general board.
