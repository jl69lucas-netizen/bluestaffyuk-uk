# staffordshirebullterrierkennel.com — competitor intel

- Root domain: staffordshirebullterrierkennel.com · tier 5 (suspect seller) · analysed 2026-09-25 (first report)
- Homepage gate: passed (status 200; final URL stays on staffordshirebullterrierkennel.com; not a bot check, not parked)
- Fetched: the homepage only (markdown + raw HTML), as the tier-5 rule requires: no map, no second page, no link followed. JSON-LD read from the homepage raw HTML. `link_allowed` stays false in the registry: this host is never linked from BSUK.
- Why it is tier 5, in brief: the site takes a generic breed-name domain, gives no licence, council, UK town or address, its structured data marks it as a pet store in the USA, it quotes a US registry's standard rather than the Kennel Club, offers to export puppies anywhere in the world by courier, and promises round-the-clock customer service. The registry's notes (written by `bsuk-competitor-registry`) add that its map-pack listing carries a US phone number.

## Trust
No licence claim of any kind on the homepage — no licence number, no council and not even a bare "licensed" line (checked by script over the visible text: no licence or council wording at all). So `council_licence_shown` is false and `council` null. Kennel Club registration is not mentioned; the only registry named is an American one, cited for a breed-temperament claim. No health tests, no vet checks. It claims around a decade of dog experience but gives no start year, so `breeding_since_as_worded` is null (tier-5 wording is not copied). No town: the page names no place, and the JSON-LD address holds only a country (USA). Phone: not shown; email: shown (homepage measures script, raw HTML) — a generic address on the site's own domain, not written here. Reviews: 0 — the page speaks of happy testimonials but shows no review words, star ratings or review widget (the scratch review list is empty; counted by script).

## Content
Homepage: 1,019 words (by script, heading and link markup stripped) under one H1 and 8 H2s. It is a stock-sounding breeder pitch: a strapline about pets needing homes, a welcome block, a "breeding centre" section, a grid of eight named dogs split male/female (every one links to the same available-puppies page), a why-choose-us block, a philosophy block that at one point calls its dogs APBT (a pit bull abbreviation, not this breed), a news block and a footer. The `pages` entry keeps the URL only, with empty title, H1 and H2 (tier-5 rule); the H2 count is a number, so it stays in `h2_per_page`. `url_count`: NOT FETCHED — no map for tier 5.

## Keywords
NOT FETCHED — tier 5 is never used as a model, so its phrases are not recorded.

## Page types
NOT FETCHED — the page-type counts need the map, and tier 5 gets no map. The homepage menu links about, available puppies, a shipping and health guarantee page and contact, none of them fetched.

## Blog
NOT FETCHED — no map and no post fetched. For context only: the homepage's news block links 10 dated posts (counted by script) from 2022 and 2024 — general Staffy care, feeding, training and family-pet topics, all of them unread here.

## Visual
20 distinct images on the homepage (homepage measures script), `alt_text` descriptive, 0 missing — the alts are keyword-stuffed variants of the breed name rather than true descriptions, but the script counts them as descriptive. At least one blog thumbnail is a stock-photo file. No `<video>` tag and no YouTube or Vimeo embed in the raw HTML.

## Schema
Place, PostalAddress, PetStore, Organization, ImageObject, WebSite, SearchAction, WebPage, Person, Article — an SEO-plugin graph from the homepage JSON-LD. The PetStore/PostalAddress pair gives a country of USA and no locality. The page also carries WooCommerce shop scaffolding (a shopping basket in the footer), with no priced product on the homepage.

## Cities
None. The homepage names no `data/locations.json` city (checked by script), though the registry found it in a London map pack.

## Conversion
`cta_types`: phone, email, visit — the page asks buyers to call, email or write, links a contact page (not fetched), and invites a visit to its facility while offering worldwide export as the alternative. No form on the homepage (its two forms are site search), so `steps_to_enquire` is null; no WhatsApp or social messaging. Prices: none printed (it only claims low prices), so `prices_shown` false and `price_amounts_as_printed` [] (always [] for tier 5). Deposit terms: none. Urgency signals: none — the dog grid shows no ready dates, sold badges or countdowns.

## Technical
`mobile_layout_ok`: NOT FETCHED. The phone was emulated in Chrome DevTools (375 × 812 viewport, deviceScaleFactor 3, mobile and touch on, an iPhone user agent), but the homepage would not load in it — `net::ERR_SSL_PROTOCOL_ERROR` on two attempts — so the mobile-check evaluate never ran on the homepage and there are no six numbers to record. Firecrawl's standard proxy fetched the same URL with status 200, so this is a TLS failure between that browser and the host, not a gated homepage. Lighthouse: NOT FETCHED — no Lighthouse run.

## Fetch
`map_calls` 0 — tier 5 gets no map, so the Map list step and the search map did not run (`search_added`, `search_breed_urls`, `search_adverts` and `home_added` do not apply). Scrapes: 1 (homepage, markdown + raw HTML, standard proxy). Credits: 1. Browser: one isolated Chrome DevTools page, closed after the failed load.

## Key insight
This is a suspect seller, not a model: it takes a London map-pack slot with a generic breed-name site that shows no licence, council, UK town, health tests or reviews, marks itself as a US pet store and offers to ship puppies worldwide. BSUK beats it by showing exactly what it cannot — a named council licence, a real town, test results and sourced reviews — and never links to it.
