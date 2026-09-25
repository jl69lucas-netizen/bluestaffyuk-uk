# Gumtree — competitor intel

- Root domain: gumtree.com · tier 2 (the UK's big general classifieds site: cars, property, jobs, goods and services, with a pets section where private sellers post dog adverts, and a hub for each breed and town) · analysed 2026-09-25. This is the entry's first report.
- **Re-typed in the G1 consistency pass (0 credits).** The saved Map list was run again through the final classifier (commit 9d7e7b9) **without any `--post-folder`**, by the controller's ruling: Gumtree's car and goods articles are not posts for this report. The page types, the post count and the price-or-FAQ note below follow from that run. The key picks are unchanged, and the listing and city pages are the same two hubs.
- Homepage gate: passed. The status was 200, the final URL stayed on gumtree.com, and the page was the live homepage: no bot check, no captcha and no parked page. The emulated phone later loaded the same live homepage.
- Key pages, as the classifier picked them from the Map list (it flags the site as a `marketplace`, and as a general classifieds site because the map holds adverts that name no dog). Before each scrape I checked that the page named the breed or a dog, as the controller asked:
  - listing slot: the Staffordshire Bull Terrier hub for Nelson, Lancashire. The search map found it. Its path names the breed, so it was scraped. **This is a single town's hub, not a national one:** it is the best listing page the Map list holds, since neither map returned Gumtree's UK-wide Staffy hub;
  - price-or-FAQ slot: none. With no post folder named, the Map list holds two price-typed pages (a guide to the running costs of a used electric car and a best-sports-cars article) and four car and goods Q&A pages typed `faq`. On a marketplace or general classifieds site this slot takes only the breed's pages or a page naming a dog, `breeder` or `breeding`, and none of these does, so the final classifier leaves the slot empty;
  - guide slot: none. On a marketplace the guide must be the breed's own, and no Staffy guide URL is in the Map list. The search map did return the site's pet-guides hub (`/info/life/pets`), and its description mentions a Staffy guide. But the hub has no type word in its path, and the guide itself was not in any map;
  - city slot: the Staffordshire Bull Terrier hub for Liverpool. Its path names the breed, so it was scraped;
  - about slot: the classifier picked Gumtree's about-us page under `/info/life/`. **It was skipped and not scraped.** Its path names neither the breed nor a dog, and the controller's rule for this run is to skip any key page that names neither. So the platform's own trust story is not in this report. Re-running with the about page would cost 1 credit, and that is the controller's call.
- The first map is saved at `maps/gumtree.json` (375 URLs). The search map is at `maps/gumtree.search.json` (62 URLs), and the homepage raw HTML is at `maps/gumtree.home.html`.

## Trust
The fetched pages show no breeder trust at all, and no platform safeguards either. That is partly because the about page was skipped (see above).
- The two Staffy hubs are bare feeds of advert cards. Each card gives a title, the dog's age, a ready-to-leave time, a town and a price. None of the fetched text names a licence, the Kennel Club, a health test or a vet check. So `council_licence_shown`, `kc_registration_mentioned` and `vet_checks_mentioned` are false, `health_tests_named` is empty, and `council` and `breeding_since_as_worded` are null.
- The hubs have a "health and documentation" filter heading, but the fetched content shows no values under it.
- `town`: London. The homepage footer gives the company's registered office in London. No street or postcode is recorded here.
- The homepage measures script found no phone and no email in the homepage raw HTML (`contact_source` raw-html).
- Reviews: 0. No page fetched shows a customer review or testimonial in its own words. The homepage's only "reviews" are links to car reviews. There is no star rating or review badge either, so no scratch list was needed.

## Content
- **Homepage:** 1,216 words by script, and 3 H2s (popular categories, items in your area, and top locations). It has no H1. The page is made up of:
  - a mega-menu covering every section, with Dogs listed under Pets;
  - category tiles;
  - a strip of recent adverts for cars, rooms, tools and household goods, each with a price and a town;
  - a car-selling banner;
  - a grid of top towns;
  - the footer.
  Nothing on the homepage is about dogs except the one Dogs link in the menu.
- **Nelson Staffy hub** (1 H2): the H1 counts one advert in Nelson. There is a filter panel for price, breed, health and documentation, location and radius. It shows one featured Staffy litter card (printed twice), then four cards from the wider area: a Staffy cross with an American Bulldog, a Staffie pup, a nine-year-old Staffy and a Staffy-cross litter. Below them is a list of top-location links that point to searches for other breeds. The page is marked noindex, nofollow.
- **Liverpool Staffy hub** (1 H2): the H1 counts zero adverts in Liverpool. The page falls back to five cards from the wider area, four of them from Staffordshire and Lancashire. Then come links to hubs for other breeds in Liverpool (Pomeranian, French Bulldog, Cockapoo and others) and the same kind of top-location list. It is marked noindex, nofollow as well.
- Both hubs also carry the text of a blocked anti-fraud frame (an ERR_BLOCKED_BY_CLIENT notice) as an extra H1. That text is the scraper's, not the site's content, so only the first H1 is recorded.
- `url_count` is 375. The map returned 375 URLs against a limit of 500, so it was not cut short. It is still a thin sample of a site with millions of adverts, and most of it is car guides.

## Keywords
4 phrases by the run rule, found by script across the three fetched pages: `puppy staffy`, `staffy x puppies`, `staffordshire bull terrier puppies` and `staffordshire bull terrier dogs puppies`.
- All four come from the hubs' advert titles and H1s. The homepage gives none: its only dog word is the menu's Dogs link.
- No run held a business, kennel or person's name, so nothing was cut.
- The breed's commercial terms show up only through the hub titles and the sellers' own card titles. Gumtree writes no breed copy of its own.

## Page types
By script over the 428-URL Map list, with `--home` and `--search` set and no `--post-folder` (the controller's ruling): reviews 55, listing 53, city 46, breed-guide 6, faq 4, price 2, about 1, blog 1, health 1. The classifier prints `marketplace: true`.
- **Blog (1):** a Peugeot 2008 car review. The table reads the model year `2008` as a dated segment, so by the rule it is a blog page and a post.
- **Breed guide (6), health (1), price (2):** car, bike, phone, furniture and rental guides under `guides/g` and one best-cars article. The table types them by `guide`, `test`, `cost` and `price` in their paths. None is about dogs.
- **Reviews (55):** car model reviews under `/info/cars/<make>/<model>/review`. These are editorial car reviews, not customer reviews.
- **Listing (53):** the search-map pages make up most of the pet listings:
  - the Staffy hubs for Nelson, Walsall, Livingston and Cheshire, plus the Scotland and Wales Staffy for-sale searches;
  - several bull terrier and "Staffordshire blue" searches;
  - dog hubs for 15 towns and counties;
  - the rest are goods and search pages whose paths say for-sale or available, and three best-cars articles with `sale` or `available` in their paths.
- **City (46):** every URL that names a `data/locations.json` place. They are mostly property, jobs and goods searches for London, Glasgow, Manchester and others. Among them are the Liverpool Staffy hub and the dog hubs for Coventry and Cornwall.
- **FAQ (4):** car and goods Q&A pages. Their paths end in a long id, so the key-page test counts them as adverts.
- **About (1):** the about-us page.
- Untyped: the rest, which is 129 other best-cars articles, car make hubs, adverts, property and the pet-guides hub.

The counts describe the map sample more than the site. The site's real pet structure is one hub for each breed and place, with private adverts under them.

## Blog
- `post_count` 1 (the classifier's `posts`), and `post_folder` is null. By the controller's ruling no post folder is named: Gumtree's car and goods articles are not posts for this report. The one post left is the Peugeot 2008 review, counted by the rule because its model year reads as a dated segment.
- No dog post is in the map. The search map returned the pet-guides hub under `/info/life/`, but none of its posts.
- `topics`, `posting_frequency` and `sampled_word_counts` are NOT FETCHED. No post was fetched, and the one post's `2008` is a model year, not a posting date. No topic, frequency or word count is taken from the car articles.

## Visual
- From the homepage raw HTML, by script: 54 distinct images. Most are advert photos whose alt text is the advert's title, so the dominant alt class is descriptive. 1 image has no alt.
- There is no video tag and no YouTube or Vimeo embed in the homepage raw HTML.

## Schema
The homepage raw HTML holds one JSON-LD block. It has an Organization (with an ImageObject logo and a PostalAddress), a WebSite with a SearchAction, and a WebPage. There is no Product, Offer, ItemList, FAQPage, BreadcrumbList or rating markup on the homepage. The two hubs were scraped as markdown, so their schema was not read.

## Cities
19 `data/locations.json` places are named on the fetched pages or have a page in the Map list: Aberdeen, Birmingham, Bristol, Cardiff, Cornwall, Coventry, Dundee, Edinburgh, Essex, Glasgow, Inverness, Leeds, Leicester, Liverpool, London, Manchester, Nottingham, Oxford and Wolverhampton.
- The homepage's top-towns grid and advert cards name Aberdeen, Birmingham, Bristol, Cardiff, Dundee, Edinburgh, Glasgow, Inverness, Leeds, Leicester, Liverpool, London, Manchester and Nottingham.
- The hubs' location lists name London, Manchester, Essex and Glasgow, and the Liverpool hub names Liverpool.
- The map adds pages for Coventry and Cornwall (dog hubs), Oxford (games-console searches) and Wolverhampton (a camera search).
- Only one of these is the breed's own city page: the Liverpool Staffy hub. A card's county alone (such as Lancashire or Staffordshire) was never taken as a city.

## Conversion
- `cta_types`: none. The fetched pages never ask a buyer to act in any of the listed ways. The hub cards only link through to the adverts. The site's own message box and number reveal sit on advert pages, and none was fetched. The homepage's calls to action (post an ad, sell your car) are aimed at sellers.
- `prices_shown`: true. 40 distinct amounts are printed across the three pages, as printed. The homepage's range from small goods to cars and rents. On the Staffy hubs, the prices run from £200 for an older dog, through £350 for a cross, to £1,000–£1,850 for Staffy and Staffy-cross pups.
- `deposit_terms`: null. No deposit is mentioned on any fetched page.
- `steps_to_enquire`: null. No enquiry form or message box was fetched. The hubs' saved-search alert is not an enquiry.
- `urgency_signals`: `ready-date`. Every hub card gives a ready-to-leave time, either now or in a number of weeks. There are no few-left, waiting-list or sold signals.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
- `map_calls` 2. The first map (limit 500) returned 375 URLs (`url_count`), below the cap, and 0 breed URLs (`breed_urls`). So the Map list asked for a search map because the map held no breed URL (`search_map` true), with the term `staffordshire bull terrier` (`search_term`). The homepage never says staffy, so the default term stood.
- The one search map (limit 100) returned 62 URLs:
  - it added 53 new URLs (`search_added`);
  - 11 of them are breed pages on the site (`search_breed_urls`);
  - 7 are adverts (`search_adverts`).
- The homepage links no breed page, so `home_added` is 0. That makes `map_list` 428.
- Scrapes: 3.
  - The homepage, as markdown and raw HTML. Firecrawl served it from cache.
  - The Nelson Staffy hub, as markdown.
  - The Liverpool Staffy hub, as markdown.
  The about page was picked but skipped, because it names neither the breed nor a dog; that still stands. The price-or-FAQ and guide slots were empty, and they are empty under the final classifier too.
- Credits spent: 5 (2 maps + 3 scrapes at 1 credit each), against a ceiling of 8.

## Key insight
Gumtree ranks for Staffy searches because its domain is strong, not because of breed content. Its Staffy town pages are thin feeds, marked noindex, of a handful of private adverts. The Liverpool one has none of its own. None of them carries a guide, price advice, health results or licence details. BSUK can beat it with indexable blue Staffy pages for each city, owned by the breeder, that show what a feed cannot: named health results, a stated price, the parents and a direct enquiry.
