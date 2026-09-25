# Staffie Owners — competitor intel

- Root domain: staffie-owners.co.uk · tier 2 (a breed-only classifieds site with sale, adoption, stud and breeder listings and a page per town) · analysed 2026-09-25. This is the entry's first report. The run used the fetch and classifier steps as updated today (commits up to 2234777): the Map list step, `--home` for the classifier, and this Fetch line.
- Homepage gate: passed. The status was 200, the final URL stayed on staffie-owners.co.uk, and there was no bot check. Every scrape was a live fetch (Firecrawl cache miss).
- Key pages, as the classifier picked them from the Map list:
  - listing slot: the UK-wide Staffie for-sale hub;
  - price-or-FAQ slot: the Staffie price page;
  - guide slot: the Staffordshire Bull Terrier breed-information guide;
  - city slot: the Essex for-sale hub;
  - about slot: none. The site's about page is linked from the footer but is not a breed path, so the Map list does not hold it, and it was not scraped.
- **The first map is thin.** It returned 46 URLs against a limit of 500, and every one is a Staffie for-sale town hub in Lancashire or Greater Manchester. So it names the breed (46 breed URLs) and is under the cap, which means no search map was asked for. The homepage's own breed links added 148 URLs at no cost: the for-sale, adoption, stud and breeder hubs, the filter pages, the price page, the breed guide, a set of town hubs and seven adverts. The Map list holds 194 URLs.
- The map is saved as a JSON URL list at the controller's scratch path `maps/staffie-owners.json`, so it can be re-typed later without spending credits. No search map ran, so there is no `maps/staffie-owners.search.json`.

## Trust
This is marketplace trust, not breeder trust. The site lists other people's dogs, so most trust signals are the sellers' own claims.
- `kc_registration_mentioned`: true. There is a KC-registered filter, a KC badge on adverts, and a KC note in the price FAQ.
- `vet_checks_mentioned`: true. Adverts carry a health-checked badge, and several advert snippets say the pups are vet checked.
- `health_tests_named`: hip and eye scores, which the hubs' FAQ recommends, plus elbow and heart testing, which one seller's snippet claims. The breed guide lists conditions (hip dysplasia, kneecap luxation, hereditary cataracts, skin allergies), not tests.
- `council_licence_shown`: false. The FAQ explains the UK licensing threshold for breeders and says the search favours licensed breeders. No licence is shown for the site or for any seller, so `council` is null.
- No breeding-since claim. No page gives the site a base town, so `town` is null.
- The homepage measures script found no phone and no email on the homepage (raw HTML).

Reviews: 0. The review list is empty (`grep -c .` gives 0). No fetched page shows customer reviews, a star rating or a review badge.

## Content
- **Homepage:** 1,670 words by script, and 17 H2s. Its one H1 is the for-sale heading over a puppy search box. Below that sit:
  - popular-search tiles with live result counts;
  - the twelve most recent adverts, each with badges, a snippet, a price and the seller's town;
  - coat-colour tiles;
  - a short mission paragraph;
  - a list of links to 100 town hubs (counted by script);
  - a free-advert pitch for sellers.
  Much of the word count is the mega-menu (by colour, location and price, plus the adoption, stud, breeders and guides menus) and the town list.
- **UK for-sale hub** (21 H2s: 20 advert titles and the FAQ): an intro with the live listing count and price range, sort options, 20 advert cards, nearby-region and refine-by-colour, KC and price links, and a four-question FAQ. The FAQ covers typical cost from the site's own six-month data, where to find a puppy (including the licensing rule), what to check, and why a licensed breeder is better. It ends with a save-search form.
- **Price page** (4 H2s): the live average puppy and adult prices, the price range, averages by region and city, averages by coat colour (red is the dearest), a note on running costs, and a disclaimer that the averages are just a rough guide worked out from live adverts.
- **Breed guide** (9 H2s): a general breed article on history, looks, temperament, training, exercise, health and lifespan, grooming and living conditions. It closes with a call to browse puppies and five related guide links (temperament, finding a breeder, training, diet, health problems).
- **Essex hub** (21 H2s): the same template as the UK hub for the county, with 9 adverts in its search radius, most of them from neighbouring counties and labelled with their distance. It then adds similar adverts from further away, then nearby-town links and the same FAQ, localised.
- The scrapes of the four key pages kept only the main content, so their H1s were not captured (`h1` is empty in `pages`).
- `url_count` is 46, the first map as returned. It is not a count of the site: the homepage alone links to 100 town hubs.

## Keywords
49 phrases by the run rule (by script), across all five pages. They come from:
- the navigation and filter links: KC-registered, blue and crossbreed Staffie puppies, and "for sale" variants;
- the popular-search tiles, which use the full breed name with blue, KC registered and for sale;
- sellers' advert titles: blue Staffy puppies, a blue merle Staffie, crosses;
- the price page's city links (Staffies in London, Manchester, Birmingham, Edinburgh) and its "Staffie puppy price" heading;
- the breed guide's breeder phrase;
- the Essex hub's localised links: Staffie puppies in Essex, blue, KC registered and ready-now variants.

No run held a business, kennel or person's name, so nothing was cut.

## Page types
By script over the 194-URL Map list, with no `--post-folder` and `--home` set: listing 119, city 41, price 1, breed-guide 1.
- **Listing (119):** 115 URLs under the for-sale folder: the main hub, its near-me page, and town, county and region hubs whose slugs are not `data/locations.json` cities, plus the four advert URLs whose slugs carry a listing word. The filter pages (colour, price, KC, age, keywords) differ from the main hub only by query, so they count once as that hub.
- **City (41):** for-sale hubs whose slug names a `data/locations.json` city, such as Manchester and its satellite towns, London, Leeds, Glasgow and Essex.
- **Untyped:** the adoption, stud and breeder hubs, three adverts, the why-choose-us page and the market report. Their paths match no row: `breeders` is not the word `breed`.

## Blog
- `post_count` 0, `post_folder` null.
- The site keeps article-style guides in an info-guides folder. The breed guide carries a related-posts block linking five more, but the Map list holds only the breed guide itself, typed as a breed guide. These guides have no blog word or date in their paths, so they were not counted as posts. Passing that folder with `--post-folder` would have turned the only guide-slot page into a blog URL. These posts are missed.
- `posting_frequency`, `topics` and `sampled_word_counts` are NOT FETCHED: no post was counted or fetched.

## Visual
- From the homepage raw HTML, by script: 15 distinct images. Most alt text is descriptive (the advert titles), and no image lacks alt.
- There is no video tag and no YouTube or Vimeo embed.

## Schema
The homepage JSON-LD holds one Organization block and nothing else: no Product, Offer, FAQPage, BreadcrumbList or ItemList markup, even though the hubs carry an FAQ.

## Cities
20 `data/locations.json` cities, each both named on a fetched page and holding a hub in the Map list: Birmingham, Bristol, Cardiff, Coventry, Dundee, Edinburgh, Essex, Glasgow, Leeds, Leicester, Liverpool, London, Manchester, Middlesbrough, Nottingham, Oxford, South Yorkshire, Sunderland, Wolverhampton and York.

## Conversion
- `cta_types`: form. The pages ask a buyer to search, filter, open an advert or save a search (a name, email and password form that sends alerts). The contact route to a seller sits on the advert pages, which were not fetched.
- `prices_shown`: true. The amounts come from:
  - advert prices, which run from tens of pounds for a wanted ad to three thousand;
  - price-filter bands;
  - the price page's averages by region and colour;
  - the FAQ's typical-cost range and average.
- `deposit_terms`: each seller sets their own. The site states none, and one advert snippet on the Essex page folds its deposit into the asking price.
- `steps_to_enquire`: null. No enquiry form was fetched.
- `urgency_signals`:
  - `ready-date`: adverts show a ready-now, ready-in-N-weeks or ready-on-a-date badge;
  - `few-left`: one snippet says two pups are left, and another says only one is available.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
- `map_calls` 1. The search map did not run: `search_map` was false, because `url_count` 46 is under the 500 cap and `breed_urls` is 46. `search_term` is null.
- `search_added` 0 and `search_breed_urls` 0. `search_adverts` does not apply, because no search map ran.
- `home_added` 148, which makes `map_list` 194.
- Scrapes: 5. That is the homepage (markdown and raw HTML) plus four key pages (markdown).
- Credits spent: 6 (1 map + 5 scrapes), against a ceiling of 8.

## Key insight
Staffie Owners ranks for breed-plus-town searches with scale: a hub for every town and county, filter pages by colour, price and KC, live price averages, and the same FAQ on each hub. But it vouches for no seller. Its listings put crosses, rehomes and a wanted ad next to KC litters. BSUK can beat it with one breeder's verified blue Staffy litters, named health tests and an open price page, on city pages that answer the same four questions from first-hand experience.
