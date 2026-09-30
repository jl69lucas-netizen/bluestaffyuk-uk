# London SERP findings (page-run rows 5 and 8)

Primary keyword: `blue staffy puppies london`. Google read through DataForSEO on 2026-09-30 (`data/queries/raw/blue-staffy-puppies-london/serp_google.response.json`).

## AI Overview (from the paid SERP)

The paid SERP carried an `ai_overview` item at position 1, but it is asynchronous: the response holds no text and no cited domains (`"asynchronous_ai_overview": true`). Every People Also Ask expansion is the same asynchronous AI overview, with no answer text. The text and citations are captured separately in Task 14 (`## AI Overview` below).

## Competitors

Task 14 step 1, 2026-09-30. Read from the nine saved pool pages (`data/queries/cache/blue-staffy-puppies-london/<n>.html`, pool order of `data/queries/raw/blue-staffy-puppies-london/competitors.json`); nothing new was fetched. Pages 1–6 and 8–9 were saved with curl; page 7 (Freeads) is a Playwright capture of the rendered page. Every figure below was measured by script from those files, the SERP responses (`serp_google.response.json`, `serp_bing.json`) and `backlinks.response.json`; words and H2 counts are not restated — they are in `data/queries/blue-staffy-puppies-london.json` (`competitors[]`: `words`, `h2_raw`, `h2_clean`). No seller's name, phone, email, address or profile link is copied here.

**Why they rank, in one paragraph.** Nobody on page one ranks on depth. Staffie Owners takes Google with templating at scale: every filter combination is a self-canonical, indexable page whose title and H1 carry the breed-colour-place phrase, backed by live inventory (count, price range, card ages), SearchResultsPage/ItemList/Product/Offer and FAQPage JSON-LD, and 85–106 distinct London-area hub links per page — on the weakest link profile in the pool (rank 14, 51 referring domains). On Bing, authority carries Pets4Homes (17,047 referring domains) and Freeads (3,517) through London hub URLs and big live feeds, and an exact-match domain and title carry the lone breeder site (149 referring domains). Every ranking page is a feed of other people's adverts or a template; none is a breeder answering a London buyer in its own voice. (Backlink figures: data/queries/raw/blue-staffy-puppies-london/backlinks.response.json.)

### 1. staffie-owners.co.uk — Southall, male, blue facet

- **url:** https://www.staffie-owners.co.uk/staffies-for-sale/southall-london?colour=blue&distance=75&sex=male&sort=price_high
- **position:** Google #1
- **type:** marketplace
- **why_ranks:** Google #1. One template, one more facet. The title and H1 put the facet words in front of breed, colour and place (“Male (Dog) Blue Staffordshire Bull Terrier Puppies For Sale In Southall, London”), and the facet is its own canonical (only the distance and sort parameters dropped), with robots “index, follow”. Google shows its first sentence — the live count and price range — as the snippet. The page carries SearchResultsPage, ItemList (Product/Offer) and FAQPage JSON-LD and links to 97 distinct London-area Staffie hubs. Not authority: staffie-owners.co.uk has the weakest link profile in the pool (rank 14, 51 referring domains; backlinks.response.json). Its FAQ is the only one in the pool written for its facet (male traits, male-versus-female training, neutering) — the nearest any page comes to Google's PAA “Is it better to get a male or female Staffy?”.
- **weakness:** A feed of private sellers' adverts, not a breeder: all 20 cards are labelled “Private seller”, only 2 of the 6 matches are in London, and the other 14 cards are “similar results from outside your search” (up to 149 miles away, 3 of them crosses by title). Deposits appear only inside sellers' own advert text, one of them non-refundable; nothing says how a puppy reaches London; and the FAQ says the search “filters for licensed … breeders” while every card is a private seller. Our wedge: one named breeder (Lisa Bright, Carlisle, Cumbria) with 6 named puppies at printed prices (£1,500 for each of the 3 males, £1,700 for each of the 3 females), a £500 refundable deposit and UK home delivery at £200–£350, priced by distance — open about being in Carlisle, not London, and about how the puppy gets to you. (BSUK facts: data/settings.json, data/puppies.json.)
- **evidence:** `data/queries/cache/blue-staffy-puppies-london/1.html` (supporting: `docs/research/competitors/staffie-owners.md`)
- **fetched:** 2026-09-30 (curl)
- **headings (whole document):** H1 1 · H2 22 · H3 6 · H4 4 · H5 0 · H6 0. Whole-document count: every `<h1>`–`<h6>` start tag in the saved file, counted by script (Python html.parser over the whole HTML — header, filters, advert cards, FAQ and footer included; script bodies are not parsed). The H2 figure is therefore the query file's h2_raw (every `<h2>` tag), not its content-H2 count h2_clean (data/queries/blue-staffy-puppies-london.json).
- **words and content H2s:** `data/queries/blue-staffy-puppies-london.json` `competitors[0]` — not restated here.
- **tables:** 0
- **faq:** true
- **byline:** none
- **schema (JSON-LD, from the saved HTML):** Answer, Brand, BreadcrumbList, FAQPage, ItemList, ListItem, Offer, Organization, Person, Place, Product, PropertyValue, Question, SearchResultsPage — SearchResultsPage → ItemList of 20 Product (Brand, Offer with a Person seller, PropertyValue) · FAQPage (Question/Answer) · BreadcrumbList · Organization
- **heading style:** Keyword-stuffed title: a templated facet H1 (“Male (Dog) Blue Staffordshire Bull Terrier Puppies For Sale In Southall, London”) over listing furniture — a count-led H2, every advert title as an H2, refine/nearby H4s — and a question-H3 FAQ.

### 2. staffie-owners.co.uk — Paddington, “Chunky Working”, blue facet

- **url:** https://www.staffie-owners.co.uk/staffies-for-sale/paddington-london?colour=blue&keywords=Chunky+Working&ready_to_leave=2_months&sort=price_high
- **position:** Google #2
- **type:** marketplace
- **why_ranks:** Google #2. The same template with a keyword facet. The title and H1 put the facet words in front of breed, colour and place (“Chunky Working Blue Staffordshire Bull Terrier Puppies For Sale In Paddington, London”), and the facet is its own canonical (only the ready_to_leave and sort parameters dropped), with robots “index, follow”. Google shows its first sentence — the live count and price range — as the snippet. The page carries SearchResultsPage, ItemList (Product/Offer) and FAQPage JSON-LD and links to 106 distinct London-area Staffie hubs. Not authority: staffie-owners.co.uk has the weakest link profile in the pool (rank 14, 51 referring domains; backlinks.response.json).
- **weakness:** The heading promises 2 local matches; 1 is in London and the other is 43 miles away, and 18 of the 20 cards are “similar results from outside your search”, among them 2 adult or rehome listings and 5 crosses by title. Every card is a private seller; no deposit terms of its own; no answer on getting a puppy to London. Our wedge: one named breeder (Lisa Bright, Carlisle, Cumbria) with 6 named puppies at printed prices (£1,500 for each of the 3 males, £1,700 for each of the 3 females), a £500 refundable deposit and UK home delivery at £200–£350, priced by distance — open about being in Carlisle, not London, and about how the puppy gets to you. (BSUK facts: data/settings.json, data/puppies.json.)
- **evidence:** `data/queries/cache/blue-staffy-puppies-london/2.html` (supporting: `docs/research/competitors/staffie-owners.md`)
- **fetched:** 2026-09-30 (curl)
- **headings (whole document):** H1 1 · H2 22 · H3 5 · H4 4 · H5 0 · H6 0. Whole-document count: every `<h1>`–`<h6>` start tag in the saved file, counted by script (Python html.parser over the whole HTML — header, filters, advert cards, FAQ and footer included; script bodies are not parsed). The H2 figure is therefore the query file's h2_raw (every `<h2>` tag), not its content-H2 count h2_clean (data/queries/blue-staffy-puppies-london.json).
- **words and content H2s:** `data/queries/blue-staffy-puppies-london.json` `competitors[1]` — not restated here.
- **tables:** 0
- **faq:** true
- **byline:** none
- **schema (JSON-LD, from the saved HTML):** Answer, Brand, BreadcrumbList, FAQPage, ItemList, ListItem, Offer, Organization, Person, Place, Product, PropertyValue, Question, SearchResultsPage — SearchResultsPage → ItemList of 20 Product (Brand, Offer with a Person seller, PropertyValue) · FAQPage (Question/Answer) · BreadcrumbList · Organization
- **heading style:** Keyword-stuffed title: the facet H1 carries a raw keyword filter (“Chunky Working Blue Staffordshire Bull Terrier Puppies For Sale In Paddington, London”), then the same listing furniture and question-H3 FAQ.

### 3. staffie-owners.co.uk — Uxbridge, “Good With”, purebred blue facet

- **url:** https://www.staffie-owners.co.uk/staffies-for-sale/uxbridge-london?colour=blue&cross_breed=no&keywords=good+with
- **position:** Google #3
- **type:** marketplace
- **why_ranks:** Google #3. The same template again, with a keyword fragment and the purebred filter. The title and H1 put the facet words in front of breed, colour and place (“Good With Blue Purebred Staffordshire Bull Terrier Puppies For Sale In Uxbridge, London”), and the facet URL is its own canonical, with robots “index, follow”. Google shows its first sentence — the live count and price range — as the snippet. The page carries SearchResultsPage, ItemList (Product/Offer) and FAQPage JSON-LD and links to 85 distinct London-area Staffie hubs. Not authority: staffie-owners.co.uk has the weakest link profile in the pool (rank 14, 51 referring domains; backlinks.response.json).
- **weakness:** The H1 is ungrammatical (“Good With” is the raw keyword filter from the URL). 2 of 3 matches are in London, and 17 of the 20 cards come from outside the search, including adult or rehome listings (2) and cross or bully listings (1) by title, on a page headed “purebred”. Every card is a private seller. Our wedge: one named breeder (Lisa Bright, Carlisle, Cumbria) with 6 named puppies at printed prices (£1,500 for each of the 3 males, £1,700 for each of the 3 females), a £500 refundable deposit and UK home delivery at £200–£350, priced by distance — open about being in Carlisle, not London, and about how the puppy gets to you. (BSUK facts: data/settings.json, data/puppies.json.)
- **evidence:** `data/queries/cache/blue-staffy-puppies-london/3.html` (supporting: `docs/research/competitors/staffie-owners.md`)
- **fetched:** 2026-09-30 (curl)
- **headings (whole document):** H1 1 · H2 22 · H3 5 · H4 4 · H5 0 · H6 0. Whole-document count: every `<h1>`–`<h6>` start tag in the saved file, counted by script (Python html.parser over the whole HTML — header, filters, advert cards, FAQ and footer included; script bodies are not parsed). The H2 figure is therefore the query file's h2_raw (every `<h2>` tag), not its content-H2 count h2_clean (data/queries/blue-staffy-puppies-london.json).
- **words and content H2s:** `data/queries/blue-staffy-puppies-london.json` `competitors[2]` — not restated here.
- **tables:** 0
- **faq:** true
- **byline:** none
- **schema (JSON-LD, from the saved HTML):** Answer, Brand, BreadcrumbList, FAQPage, ItemList, ListItem, Offer, Organization, Person, Place, Product, PropertyValue, Question, SearchResultsPage — SearchResultsPage → ItemList of 20 Product (Brand, Offer with a Person seller, PropertyValue) · FAQPage (Question/Answer) · BreadcrumbList · Organization
- **heading style:** Keyword-stuffed title: “Good With Blue Purebred Staffordshire Bull Terrier Puppies For Sale In Uxbridge, London” — a keyword fragment pasted into the facet H1 — over the same listing furniture and question-H3 FAQ.

### 4. staffie-owners.co.uk — Camden Town, “Vaccinations”, under £1,500 blue facet

- **url:** https://www.staffie-owners.co.uk/staffies-for-sale/camden-town-london?colour=blue&keywords=vaccinations&price=1500
- **position:** Google #4
- **type:** marketplace
- **why_ranks:** Google #4. The same template with two facets, a keyword and a price cap; Google writes its own snippet for this one rather than the intro. The title and H1 put the facet words in front of breed, colour and place (“Vaccinations Blue Staffordshire Bull Terrier Puppies For Sale In Camden Town, London Under £1,500”), and the facet URL is its own canonical, with robots “index, follow”. The page carries SearchResultsPage, ItemList (Product/Offer) and FAQPage JSON-LD and links to 106 distinct London-area Staffie hubs. Not authority: staffie-owners.co.uk has the weakest link profile in the pool (rank 14, 51 referring domains; backlinks.response.json).
- **weakness:** The single match is not in London (29 miles away), 19 of the 20 cards come from outside the search, and 4 cards print a price above the £1,500 the H1 promises (6 print none). Every card is a private seller. Our wedge: one named breeder (Lisa Bright, Carlisle, Cumbria) with 6 named puppies at printed prices (£1,500 for each of the 3 males, £1,700 for each of the 3 females), a £500 refundable deposit and UK home delivery at £200–£350, priced by distance — open about being in Carlisle, not London, and about how the puppy gets to you. (BSUK facts: data/settings.json, data/puppies.json.)
- **evidence:** `data/queries/cache/blue-staffy-puppies-london/4.html` (supporting: `docs/research/competitors/staffie-owners.md`)
- **fetched:** 2026-09-30 (curl)
- **headings (whole document):** H1 1 · H2 22 · H3 5 · H4 4 · H5 0 · H6 0. Whole-document count: every `<h1>`–`<h6>` start tag in the saved file, counted by script (Python html.parser over the whole HTML — header, filters, advert cards, FAQ and footer included; script bodies are not parsed). The H2 figure is therefore the query file's h2_raw (every `<h2>` tag), not its content-H2 count h2_clean (data/queries/blue-staffy-puppies-london.json).
- **words and content H2s:** `data/queries/blue-staffy-puppies-london.json` `competitors[3]` — not restated here.
- **tables:** 0
- **faq:** true
- **byline:** none
- **schema (JSON-LD, from the saved HTML):** Answer, Brand, BreadcrumbList, FAQPage, ItemList, ListItem, Offer, Organization, Person, Place, Product, PropertyValue, Question, SearchResultsPage — SearchResultsPage → ItemList of 20 Product (Brand, Offer with a Person seller, PropertyValue) · FAQPage (Question/Answer) · BreadcrumbList · Organization
- **heading style:** Keyword-stuffed title: “Vaccinations Blue Staffordshire Bull Terrier Puppies For Sale In Camden Town, London Under £1,500” — keyword and price facets stacked into the H1 — over the same listing furniture and question-H3 FAQ.

### 5. staffie-owners.co.uk — London, blue facet

- **url:** https://www.staffie-owners.co.uk/staffies-for-sale/london?colour=blue
- **position:** Bing #1
- **type:** marketplace
- **why_ranks:** Bing #1 (it is not among Google's nine organic results, 7 of which are other facets of the same template). The cleanest version of the template: an exact breed-colour-place H1 (“Blue Staffordshire Bull Terrier Puppies For Sale In London”) on the plain London facet, self-canonical with robots “index, follow”, with the same JSON-LD and 106 London-area hub links. Not authority: rank 14, 51 referring domains (backlinks.response.json).
- **weakness:** Only 2 of its 7 “London” matches are in London (the rest are 19–89 miles out), and the other 13 cards are “similar results from outside your search”, 103–174 miles away, including 2 wanted adverts and 2 non-blue litters by title — yet the ItemList marks up all 20. Every card is a private seller. Our wedge: one named breeder (Lisa Bright, Carlisle, Cumbria) with 6 named puppies at printed prices (£1,500 for each of the 3 males, £1,700 for each of the 3 females), a £500 refundable deposit and UK home delivery at £200–£350, priced by distance — open about being in Carlisle, not London, and about how the puppy gets to you. (BSUK facts: data/settings.json, data/puppies.json.)
- **evidence:** `data/queries/cache/blue-staffy-puppies-london/5.html` (supporting: `docs/research/competitors/staffie-owners.md`)
- **fetched:** 2026-09-30 (curl)
- **headings (whole document):** H1 1 · H2 22 · H3 5 · H4 4 · H5 0 · H6 0. Whole-document count: every `<h1>`–`<h6>` start tag in the saved file, counted by script (Python html.parser over the whole HTML — header, filters, advert cards, FAQ and footer included; script bodies are not parsed). The H2 figure is therefore the query file's h2_raw (every `<h2>` tag), not its content-H2 count h2_clean (data/queries/blue-staffy-puppies-london.json).
- **words and content H2s:** `data/queries/blue-staffy-puppies-london.json` `competitors[4]` — not restated here.
- **tables:** 0
- **faq:** true
- **byline:** none
- **schema (JSON-LD, from the saved HTML):** Answer, Brand, BreadcrumbList, FAQPage, ItemList, ListItem, Offer, Organization, Person, Place, Product, PropertyValue, Question, SearchResultsPage — SearchResultsPage → ItemList of 20 Product (Brand, Offer with a Person seller, PropertyValue) · FAQPage (Question/Answer) · BreadcrumbList · Organization
- **heading style:** Exact-match statement H1 (“Blue Staffordshire Bull Terrier Puppies For Sale In London”) over the same listing furniture (count-led H2, advert titles as H2s) and a question-H3 FAQ.

### 6. pets4homes.co.uk — London Staffordshire Bull Terrier listing

- **url:** https://www.pets4homes.co.uk/sale/puppies/staffordshire-bull-terrier/united-kingdom/england/greater-london/london/
- **position:** Bing #2
- **type:** marketplace
- **why_ranks:** Bing #2. Domain authority (rank 59, 17,047 referring domains; backlinks.response.json) and a London location URL whose title and H1 name the breed and the place (“Staffordshire Bull Terrier Puppies for sale in London, Greater London”), over a live feed (“19 Puppies found”) with a Product/AggregateOffer price band in JSON-LD. The saved copy carries robots “noindex,nofollow” and Bing ranks it regardless; whether a crawler is served the same tag was not tested.
- **weakness:** Not blue and barely London: the H1 has no colour, 9 of the 19 card titles say blue, the page's own county filter puts 4 of the 19 in Greater London, and 5 cards are grown dogs listed with an age in years; its fixed breed paragraph gives the coat colours as “white, black, brindle, or combinations thereof” — no blue. Its FAQ asks 5 questions but the saved page answers 1, with a UK-wide average price. A “Council licensed breeders” filter exists, but no card on the saved page shows a licensed-breeder label. Our wedge: one named breeder (Lisa Bright, Carlisle, Cumbria) with 6 named puppies at printed prices (£1,500 for each of the 3 males, £1,700 for each of the 3 females), a £500 refundable deposit and UK home delivery at £200–£350, priced by distance — open about being in Carlisle, not London, and about how the puppy gets to you. (BSUK facts: data/settings.json, data/puppies.json.)
- **evidence:** `data/queries/cache/blue-staffy-puppies-london/6.html` (supporting: `docs/research/competitors/pets4homes.md`)
- **fetched:** 2026-09-30 (curl)
- **headings (whole document):** H1 1 · H2 1 · H3 25 · H4 0 · H5 0 · H6 0. Whole-document count: every `<h1>`–`<h6>` start tag in the saved file, counted by script (Python html.parser over the whole HTML — header, filters, advert cards, FAQ and footer included; script bodies are not parsed). The H2 figure is therefore the query file's h2_raw (every `<h2>` tag), not its content-H2 count h2_clean (data/queries/blue-staffy-puppies-london.json).
- **words and content H2s:** `data/queries/blue-staffy-puppies-london.json` `competitors[5]` — not restated here.
- **tables:** 0
- **faq:** true
- **byline:** none
- **schema (JSON-LD, from the saved HTML):** AggregateOffer, Product — one Product with an AggregateOffer price band (availability, highPrice, lowPrice, offerCount, priceCurrency); no FAQPage although the page has an FAQ, and no BreadcrumbList
- **heading style:** Generic attribute H1 (breed and place, no colour) over listing furniture — a result-count H2 (“19 Puppies found”) and advert titles as H3s — with an “FAQs” H3 over five question H3s.

### 7. freeads.co.uk — London Staffordshire Bull Terrier hub

- **url:** https://www.freeads.co.uk/london/buy-sell/pets/dogs/staffordshire-bull-terrier/
- **position:** Bing #3
- **type:** marketplace
- **why_ranks:** Bing #3. Domain authority (rank 51, 3,517 referring domains; backlinks.response.json) and a London Staffy hub URL whose H1 names the breed and “near London” (“Staffordshire Bull Terrier Puppies & Dogs For Sale near London”), over a big live feed with seller videos (VideoObject JSON-LD) and a Trustpilot “TrustScore 4.6” badge on the page.
- **weakness:** Wide, not local: 45 cards carry a distance, 10–99 miles from London — 23 of them more than 60 miles out, 6 within 15 — and puppies, adult dogs and crosses share the feed with an other-breed strip (“You might also like near London”) in the middle. No FAQ, no price guidance, a one-line buyer's advice about contact details in advert photos, and its Product JSON-LD is invalid JSON (a `/* … */` comment inside). Our wedge: one named breeder (Lisa Bright, Carlisle, Cumbria) with 6 named puppies at printed prices (£1,500 for each of the 3 males, £1,700 for each of the 3 females), a £500 refundable deposit and UK home delivery at £200–£350, priced by distance — open about being in Carlisle, not London, and about how the puppy gets to you. (BSUK facts: data/settings.json, data/puppies.json.)
- **evidence:** `data/queries/cache/blue-staffy-puppies-london/7.html` (supporting: `docs/research/competitors/freeads.md`)
- **fetched:** 2026-09-30 (Playwright capture of the rendered page)
- **headings (whole document):** H1 1 · H2 14 · H3 12 · H4 0 · H5 0 · H6 0. Whole-document count: every `<h1>`–`<h6>` start tag in the saved file, counted by script (Python html.parser over the whole HTML — header, filters, advert cards, FAQ and footer included; script bodies are not parsed). The H2 figure is therefore the query file's h2_raw (every `<h2>` tag), not its content-H2 count h2_clean (data/queries/blue-staffy-puppies-london.json). This file is a Playwright capture of the rendered page, so headings a script injects are counted too.
- **words and content H2s:** `data/queries/blue-staffy-puppies-london.json` `competitors[6]` — not restated here.
- **tables:** 0
- **faq:** false
- **byline:** none
- **schema (JSON-LD, from the saved HTML):** BreadcrumbList, ImageObject, ListItem, Organization, VideoObject, WebSite — plus 5 of 13 JSON-LD blocks that are invalid JSON to a strict parser (VideoObject, VideoObject, VideoObject, VideoObject, Product), among them the page's only Product with AggregateOffer
- **heading style:** Listing furniture: UI-label headings — filter H3s (Category, Location, Miles, Distance, Price Range), “Refine your results”, “Latest featured ads…”, picker H3s — and footer category H2s printed twice (Cats for sale, Dogs for sale, Horses for sale, Other pets, Rescue pets).

### 8. pets4homes.co.uk — UK-wide blue Staffordshire Bull Terrier search

- **url:** https://www.pets4homes.co.uk/sale/puppies/staffordshire-bull-terrier/?keyword=blue
- **position:** Bing #4
- **type:** marketplace
- **why_ranks:** Bing #4. Domain authority (rank 59, 17,047 referring domains; backlinks.response.json) plus the colour in the title and H1 (“Blue Staffordshire Bull Terrier Puppies for sale in the UK”) on a keyword-search URL with a live UK-wide feed (“67 Puppies found”) and Product/AggregateOffer JSON-LD. The saved copy carries robots “noindex,follow”.
- **weakness:** Not a London page at all: the H1 says “in the UK”, 1 of the 24 cards shown is in Greater London, named DNA tests appear only in 2 sellers' own lines, and the 5-question FAQ has 1 answer in the saved page; on a page headed blue, its fixed breed paragraph gives the coat colours as “white, black, brindle, or combinations thereof” — no blue. Our wedge: a page that answers the London question directly — how a puppy from our home in Carlisle reaches London, and for how much (UK home delivery at £200–£350, priced by distance) — for 6 named puppies at printed prices (£1,500 for each of the 3 males, £1,700 for each of the 3 females), with a £500 refundable deposit. (BSUK facts: data/settings.json, data/puppies.json.)
- **evidence:** `data/queries/cache/blue-staffy-puppies-london/8.html` (supporting: `docs/research/competitors/pets4homes.md`)
- **fetched:** 2026-09-30 (curl)
- **headings (whole document):** H1 1 · H2 1 · H3 30 · H4 0 · H5 0 · H6 0. Whole-document count: every `<h1>`–`<h6>` start tag in the saved file, counted by script (Python html.parser over the whole HTML — header, filters, advert cards, FAQ and footer included; script bodies are not parsed). The H2 figure is therefore the query file's h2_raw (every `<h2>` tag), not its content-H2 count h2_clean (data/queries/blue-staffy-puppies-london.json).
- **words and content H2s:** `data/queries/blue-staffy-puppies-london.json` `competitors[7]` — not restated here.
- **tables:** 0
- **faq:** true
- **byline:** none
- **schema (JSON-LD, from the saved HTML):** AggregateOffer, Product — one Product with an AggregateOffer price band (availability, highPrice, lowPrice, offerCount, priceCurrency); no FAQPage although the page has an FAQ, and no BreadcrumbList
- **heading style:** Generic attribute H1 (breed and colour, “in the UK”, no place) over listing furniture — a result-count H2 (“67 Puppies found”) and advert titles as H3s — with the same question-H3 FAQ.

### 9. englishbluestaffypuppies.com — a breeder's website-builder homepage

- **url:** https://englishbluestaffypuppies.com/
- **position:** Bing #5
- **type:** breeder
- **why_ranks:** Bing #5. The pool's only breeder site ranks on exact match, not content: the domain holds “bluestaffypuppies”, the title reads “English Blue Staffordshire Bull Terrier Puppies for Sale in London”, the meta description repeats “Blue Staffy puppies for sale in London”, and the meta author tag is a keyword string naming London, Manchester, Croydon, Wembley. No rank returned, 149 referring domains (backlinks.response.json), plus LocalBusiness JSON-LD.
- **weakness:** The London is a keyword: the page's own copy places the kennel in Lincolnshire. It is an unedited Go Daddy Website Builder template — H4s still read “Adoption Process” (×6), “Adoption Success Stories” (×6), “Our Products” (×7), “Foster Program” — the same H3 repeats 6 times, and the ranking URL prints no price (0 “£” signs), no FAQ and no puppy (its menu links an available-puppies page and a shipping page, which are outside the pool and were not read), with the thinnest prose in the pool (words: data/queries/blue-staffy-puppies-london.json). Our wedge: the honest version of its promise — a breeder who says where we are (Carlisle, Cumbria), names and prices every puppy (£1,500 for each of the 3 males, £1,700 for each of the 3 females), and prices the trip to London (UK home delivery at £200–£350, priced by distance), with a £500 refundable deposit. (BSUK facts: data/settings.json, data/puppies.json.)
- **evidence:** `data/queries/cache/blue-staffy-puppies-london/9.html`
- **fetched:** 2026-09-30 (curl)
- **headings (whole document):** H1 1 · H2 3 · H3 6 · H4 35 · H5 0 · H6 0. Whole-document count: every `<h1>`–`<h6>` start tag in the saved file, counted by script (Python html.parser over the whole HTML — header, filters, advert cards, FAQ and footer included; script bodies are not parsed). The H2 figure is therefore the query file's h2_raw (every `<h2>` tag), not its content-H2 count h2_clean (data/queries/blue-staffy-puppies-london.json). The repeated H3 and most H4s are the builder template's slides and cards.
- **words and content H2s:** `data/queries/blue-staffy-puppies-london.json` `competitors[8]` — not restated here.
- **tables:** 0
- **faq:** false
- **byline:** none — no author on the page; the `<meta name="author">` tag holds a keyword string naming London, Manchester, Croydon, Wembley, not a person
- **schema (JSON-LD, from the saved HTML):** GeoCoordinates, LocalBusiness, OpeningHoursSpecification, PostalAddress — one LocalBusiness block with address, geo and opening hours
- **heading style:** Generic attribute H1 (“Purebred Staffordshire Bull Terriers”) with brand-welcome H2s naming the kennel, one H3 repeated 6 times, and unedited website-builder template H4s (“Adoption Process”, “Adoption Fees”, “Our Products”, “Our Mission” …).

## Universal gaps

What every one of the nine fetched pages misses (each checked against all nine saved pages by script):

- No byline: none of the nine pages says who wrote it or is signed by a person; the only names are sellers' display names on advert cards, and the breeder site's meta author tag is a keyword string, not a person.
- No table: 0 `<table>` elements on all nine pages — no price, delivery or comparison table anywhere on page one.
- No deposit terms in the page's own voice: deposits appear only inside individual sellers' advert text (pages 1, 2, 3, 4, 5, 7), some of them non-refundable, and pages 6, 8, 9 never mention one. No page states an amount, whether it is refunded or what it secures.
- No delivery answer: no page prices getting a puppy to London or says how it travels; the breeder site's one line promises “UK-wide delivery options” with no price or method (its menu links a shipping page outside the pool, not read), and on the marketplaces no seller line in the saved pages offers delivery.
- No honest location: every “London” page pads with puppies from far away (Staffie Owners' “similar results” run up to 174 miles out and its London facet has 2 of 7 matches in London; Pets4Homes' London page puts 4 of 19 in Greater London; Freeads' cards sit 10–99 miles out), and the breeder site's own copy places it in Lincolnshire. None tells a London buyer where the puppy is and how it gets to them.
- No remote viewing in the page's own voice: no page offers a live video call to see the puppy and its mother before a deposit; the only mention in the pool is one seller's line inside a Freeads advert.
- No answer on rarity or colour: the word “rare” is on none of the nine pages and none explains what makes a Staffy blue, though Google's People Also Ask asks “How rare are blue Staffies?”.
- No single accountable breeder with prices: eight pages are feeds of other people's adverts (every card on the five Staffie Owners pages is labelled “Private seller”), and the one breeder page prints no price and lists no puppy on its ranking URL.
- No question-led body headings: question H2s are 0 on all nine pages (by script); question headings appear only as FAQ H3s (pages 1, 2, 3, 4, 5, 6, 8) and as two filter-picker H3s on Freeads.

## Heading types

| Source | Heading style |
|---|---|
| staffie-owners.co.uk · Southall male facet (Google #1) | Keyword-stuffed title: a templated facet H1 (“Male (Dog) Blue Staffordshire Bull Terrier Puppies For Sale In Southall, London”) over listing furniture — a count-led H2, every advert title as an H2, refine/nearby H4s — and a question-H3 FAQ. |
| staffie-owners.co.uk · Paddington keyword facet (Google #2) | Keyword-stuffed title: the facet H1 carries a raw keyword filter (“Chunky Working Blue Staffordshire Bull Terrier Puppies For Sale In Paddington, London”), then the same listing furniture and question-H3 FAQ. |
| staffie-owners.co.uk · Uxbridge keyword facet (Google #3) | Keyword-stuffed title: “Good With Blue Purebred Staffordshire Bull Terrier Puppies For Sale In Uxbridge, London” — a keyword fragment pasted into the facet H1 — over the same listing furniture and question-H3 FAQ. |
| staffie-owners.co.uk · Camden Town price and keyword facet (Google #4) | Keyword-stuffed title: “Vaccinations Blue Staffordshire Bull Terrier Puppies For Sale In Camden Town, London Under £1,500” — keyword and price facets stacked into the H1 — over the same listing furniture and question-H3 FAQ. |
| staffie-owners.co.uk · London blue facet (Bing #1) | Exact-match statement H1 (“Blue Staffordshire Bull Terrier Puppies For Sale In London”) over the same listing furniture (count-led H2, advert titles as H2s) and a question-H3 FAQ. |
| pets4homes.co.uk · London breed listing (Bing #2) | Generic attribute H1 (breed and place, no colour) over listing furniture — a result-count H2 (“19 Puppies found”) and advert titles as H3s — with an “FAQs” H3 over five question H3s. |
| freeads.co.uk · London breed hub (Bing #3) | Listing furniture: UI-label headings — filter H3s (Category, Location, Miles, Distance, Price Range), “Refine your results”, “Latest featured ads…”, picker H3s — and footer category H2s printed twice (Cats for sale, Dogs for sale, Horses for sale, Other pets, Rescue pets). |
| pets4homes.co.uk · UK blue keyword listing (Bing #4) | Generic attribute H1 (breed and colour, “in the UK”, no place) over listing furniture — a result-count H2 (“67 Puppies found”) and advert titles as H3s — with the same question-H3 FAQ. |
| englishbluestaffypuppies.com · breeder homepage (Bing #5) | Generic attribute H1 (“Purebred Staffordshire Bull Terriers”) with brand-welcome H2s naming the kennel, one H3 repeated 6 times, and unedited website-builder template H4s (“Adoption Process”, “Adoption Fees”, “Our Products”, “Our Mission” …). |

**What shape wins:** What wins Google is one template, not one page: a statement H1 that stacks facet words in front of breed, colour and place (“Male (Dog) Blue Staffordshire Bull Terrier Puppies For Sale In Southall, London”), a count-led H2 that restates it with the live number (“6 Male (Dog) Blue Staffie Puppies For Sale In Southall, London”), sellers' advert titles as the body headings, and a closing “Frequently Asked Questions” H2 over four or five question H3s marked up as FAQPage. Bing's #1 is the same template on the plain London facet (“Blue Staffordshire Bull Terrier Puppies For Sale In London”). No ranking page has a question H2 or a topical body section (question H2s: 0 of 9, by script), so the question register is proven only in FAQ H3s, while Google's People Also Ask demand (price, rarity, male or female, behaviour, house dog) is phrased as questions. The shape to beat keeps the breed-colour-London phrase in the title and H1 and takes the unclaimed ground: question H2s that answer the London buyer, over a real FAQ block.

## SERP schema

JSON-LD `@type`s read from each saved page by script (every block parsed with a strict JSON parser; a block that fails is reported, not guessed).

| # | URL | Schema |
|---|---|---|
| 1 | https://www.staffie-owners.co.uk/staffies-for-sale/southall-london?colour=blue&distance=75&sex=male&sort=price_high | Answer, Brand, BreadcrumbList, FAQPage, ItemList, ListItem, Offer, Organization, Person, Place, Product, PropertyValue, Question, SearchResultsPage — SearchResultsPage → ItemList of 20 Product (Brand, Offer with a Person seller, PropertyValue) · FAQPage (Question/Answer) · BreadcrumbList · Organization |
| 2 | https://www.staffie-owners.co.uk/staffies-for-sale/paddington-london?colour=blue&keywords=Chunky+Working&ready_to_leave=2_months&sort=price_high | Answer, Brand, BreadcrumbList, FAQPage, ItemList, ListItem, Offer, Organization, Person, Place, Product, PropertyValue, Question, SearchResultsPage — SearchResultsPage → ItemList of 20 Product (Brand, Offer with a Person seller, PropertyValue) · FAQPage (Question/Answer) · BreadcrumbList · Organization |
| 3 | https://www.staffie-owners.co.uk/staffies-for-sale/uxbridge-london?colour=blue&cross_breed=no&keywords=good+with | Answer, Brand, BreadcrumbList, FAQPage, ItemList, ListItem, Offer, Organization, Person, Place, Product, PropertyValue, Question, SearchResultsPage — SearchResultsPage → ItemList of 20 Product (Brand, Offer with a Person seller, PropertyValue) · FAQPage (Question/Answer) · BreadcrumbList · Organization |
| 4 | https://www.staffie-owners.co.uk/staffies-for-sale/camden-town-london?colour=blue&keywords=vaccinations&price=1500 | Answer, Brand, BreadcrumbList, FAQPage, ItemList, ListItem, Offer, Organization, Person, Place, Product, PropertyValue, Question, SearchResultsPage — SearchResultsPage → ItemList of 20 Product (Brand, Offer with a Person seller, PropertyValue) · FAQPage (Question/Answer) · BreadcrumbList · Organization |
| 5 | https://www.staffie-owners.co.uk/staffies-for-sale/london?colour=blue | Answer, Brand, BreadcrumbList, FAQPage, ItemList, ListItem, Offer, Organization, Person, Place, Product, PropertyValue, Question, SearchResultsPage — SearchResultsPage → ItemList of 20 Product (Brand, Offer with a Person seller, PropertyValue) · FAQPage (Question/Answer) · BreadcrumbList · Organization |
| 6 | https://www.pets4homes.co.uk/sale/puppies/staffordshire-bull-terrier/united-kingdom/england/greater-london/london/ | AggregateOffer, Product — one Product with an AggregateOffer price band (availability, highPrice, lowPrice, offerCount, priceCurrency); no FAQPage although the page has an FAQ, and no BreadcrumbList |
| 7 | https://www.freeads.co.uk/london/buy-sell/pets/dogs/staffordshire-bull-terrier/ | BreadcrumbList, ImageObject, ListItem, Organization, VideoObject, WebSite — plus 5 of 13 JSON-LD blocks that are invalid JSON to a strict parser (VideoObject, VideoObject, VideoObject, VideoObject, Product), among them the page's only Product with AggregateOffer |
| 8 | https://www.pets4homes.co.uk/sale/puppies/staffordshire-bull-terrier/?keyword=blue | AggregateOffer, Product — one Product with an AggregateOffer price band (availability, highPrice, lowPrice, offerCount, priceCurrency); no FAQPage although the page has an FAQ, and no BreadcrumbList |
| 9 | https://englishbluestaffypuppies.com/ | GeoCoordinates, LocalBusiness, OpeningHoursSpecification, PostalAddress — one LocalBusiness block with address, geo and opening hours |

Across the SERP: FAQPage only on the five Staffie Owners pages (pages 1–5); VideoObject only on Freeads; LocalBusiness only on the breeder site; Person only as an advert's seller inside Staffie Owners' Offer markup; and none of Article, BlogPosting, Review, AggregateRating, HowTo, Event on any page.

## Structural read

Page one is a marketplace SERP, split by engine. Google opens with an asynchronous AI Overview (no text in the response) and gives its top four organic places — and 7 of its 9 — to Staffie Owners facet pages, one template with different filter words, with a People Also Ask block (price, rarity, male or female, behaviour, house dog) among them; its fifth organic result, a TikTok puppy-yoga video, was dropped from the pool as off-topic. Bing's top five is Staffie Owners' plain London facet, two Pets4Homes listings (London all-colours; UK-wide blue), the Freeads London Staffy hub and one breeder site. Eight of the nine pool pages are feeds of other people's adverts (the query file's word_target excludes all eight: seven as card-grid listings, Freeads as an outlier), so no guide, article or single-breeder page with prices ranks on either engine, and the one breeder page is an unedited website-builder template. Authority does not decide Google: the domain that owns it has the weakest link profile in the pool (rank 14, 51 referring domains, against Pets4Homes' 17,047 and Freeads' 3,517 referring domains), so exact-match facet templating, live inventory and ItemList/FAQPage markup beat links there, while Bing leans on authority and an exact-match domain. On every ranking page “London” is a filter label rather than a place, which leaves the lane open for one accountable breeder page that answers the London buyer's real questions — price, deposit, and how the puppy gets to London — in its own voice.
