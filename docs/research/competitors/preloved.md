# Preloved — competitor intel

- Root domain: preloved.co.uk · tier 2 (a general UK classifieds site for second-hand goods of every kind, with an animals section where private owners sell or rehome pets) · analysed 2026-09-25. This is the first report for this entry.
- Homepage gate: passed. The status was 200, the final URL stayed on preloved.co.uk, and the page was the live homepage, not a bot check or a parked page.
- Key pages, as the classifier picked them from the Map list (it flags the site as a `marketplace`):
  - listing slot: the UK-wide "pitbull or staffy" dog search page. It is one of three Staffy pages the search map found, and it wins on the shortest path. **This is a narrow search-results page, not a national Staffy hub:** it is the best listing page the Map list holds;
  - price-or-FAQ slot: none. No URL in the Map list has a price or FAQ word in its path;
  - guide slot: none. The only `breed-guide` URLs are two book adverts. On a marketplace the guide must be the breed's own;
  - city slot: the Manchester Staffy dog search page;
  - about slot: none. The homepage footer links an about page, but it is not in the Map list. The homepage's links join the list only when they are breed paths.
- Controller check (classifier gap): before scraping, each pick was checked for a breed or dog word. Both picks name the breed (`staffy`), so no slot was skipped. The car-seat advert the controller flagged was never picked in this run. It would have been the listing's last resort on the first map alone, but the search map's Staffy pages outrank it.
- The first map is saved at `maps/preloved.json` (496 URLs), the search map at `maps/preloved.search.json` (64 URLs) and the homepage raw HTML at `maps/preloved.home.html`.

## Trust
Nothing on the fetched pages builds trust in a seller or a dog.
- `council_licence_shown` false and `council` null. No page mentions a licence.
- `kc_registration_mentioned` false, `health_tests_named` empty and `vet_checks_mentioned` false. The Staffy adverts on the two search pages talk about vaccinations, microchips and neutering, but none mentions KC papers, a named health test or a vet check.
- No breeding-since claim. The site names no base town, so `town` is null.
- The homepage measures script found no phone and no email in the homepage raw HTML (`contact_source` raw-html). The footer's contact link goes to a form on the secure subdomain, which was not fetched.
- `reviews_shown` 0. No review, testimonial, star rating or Trustpilot badge appears on the homepage or either search page. The homepage raw HTML does not mention reviews at all.
- The homepage's top line calls the site the UK's most trusted marketplace, but no page backs the claim with any evidence.

## Content
- **Homepage:** 826 words by script, and 8 H2s. It is a shop window for the whole marketplace, not a pets page:
  - a header with category links (animals, home, sport, fashion, electronics, motoring, trades) and log-in, join and create-listing buttons;
  - a carousel of three banner slides, each marked as an H1. Two sell the marketplace's furniture and garden ranges, and one is a paid meal-kit offer. The `h1` in `pages` is the first slide;
  - a strip of 20 new item adverts and a strip of 20 new animal adverts. Each card gives a title, a price and a town. The animal strip holds farm animals, poultry, reptiles, a kitten and a guinea pig, and no dog;
  - a popular-categories strip, a pet news and guidance block whose posts load by script (none is in the fetched content), and footer links.
  Many of the words are card titles, and the logo's long text description appears twice.
- **UK "pitbull or staffy" page** (0 H2s): a saved-search results page. The markdown has no heading markup. It has breadcrumbs, a count of seven listings, sort options and top-search links for other dog searches. Then come seven advert cards, each with a photo, the first lines of the seller's text, a price, a town and an age. Six are Staffy or Staffy-cross dogs: three adult rehomes (one of them a cross), one young pup, and two cross-breed litters (one with boxer and cockapoo, one with lurcher and beagle). The seventh is a lurcher in rescue. There is no guide text, price guidance or FAQ.
- **Manchester Staffy page** (0 H2s): the same template with a Manchester breadcrumb. It shows the same seven adverts in a different order. None of them is in or near Manchester: the towns run from Liverpool and Doncaster to Swindon and East Sussex. So this "city" page gives a buyer nothing local.
- `url_count` is 496. The first map returned 496 URLs against a limit of 500, so it was not cut short. 494 of them are single adverts for general goods (books, furniture, vehicles), which makes it a thin sample of a very large site.

## Keywords
4 phrases by the run rule (by script) from the three pages and their titles.
- Two come from the Manchester page's title: `staffy dogs puppies` and `staffy dogs puppies for sale`. The title joins the search word to the section name, which is where they come from.
- Two come from cross-breed litter adverts on both search pages: a Staffy-boxer-cockapoo litter and a Staffy-lurcher-beagle litter. They are noise, not targets.
- The homepage gives none, because it never names the breed.
- No run held a business, kennel or person's name, so nothing was cut.

## Page types
By script over the 557-URL Map list, with `--home` and `--search` set and no `--post-folder`: listing 34, city 6, breed-guide 2, blog 1. The classifier prints `marketplace: true`.
- **Listing (34):**
  - 24 dog search pages from the search map. They cover UK-wide breed searches (among them the UK-wide and Grimsby Staffy searches, bull terrier, other terriers and crosses), town-level dog-sale pages, and the dog-sale hub;
  - rabbit, bird, cat and bike sale pages;
  - two general-goods adverts whose slugs say "for sale".
- **City (6):**
  - the Manchester Staffy page and a Sunderland dog-sale page;
  - local-classifieds pages for Hull and Inverness;
  - two general adverts whose titles name London and Essex.
- **Breed guide (2):** two book adverts with "guide" in the slug. Neither is a guide.
- **Blog (1):** a book advert with "news" in its slug. It is not a post.
- **Untyped:** almost all of the 496 first-map URLs, which are single adverts for general goods with no word from the table.

The counts describe the map sample more than the site. The site's real shape is one search page for each category, place and search term, plus the adverts under them.

## Blog
- `post_count` 0, `post_folder` null.
- The homepage links a blog and a pet-care guides folder, and its pet news and guidance block loads posts by script. No blog URL is in the Map list, and none was fetched. So posts are missed here, not absent from the site.
- `posting_frequency`, `topics` and `sampled_word_counts` are NOT FETCHED: no post was counted or fetched.

## Visual
- From the homepage raw HTML, by script: 51 distinct images, with descriptive alt text as the main class and 0 missing alts. Most are advert-card photos, whose alt is the advert's title, plus the category icons and banner slides.
- The controller warned that homepage images might sit behind an `/images?url=` proxy. This scrape's raw HTML has no such URL: the card photos are served straight from the site's image CDN with a size query. So the measures counted one image per CDN path.
- `video_present` false. There is no video tag and no YouTube or Vimeo embed. The only YouTube reference is a follow-us link.

## Schema
The homepage raw HTML holds two JSON-LD blocks: a WebSite with a SearchAction, and an Organization. There is no Product, Offer, ItemList, FAQPage, BreadcrumbList or rating markup. The two search pages were scraped as markdown, so their schema was not read.

## Cities
8 `data/locations.json` places are named on the fetched pages or have a page in the map: Essex, Hull, Inverness, Liverpool, London, Manchester, Sunderland and Wolverhampton.
- The homepage's advert cards name London, Essex and Wolverhampton.
- The search pages' cards name Liverpool, and the city page is for Manchester.
- The Map list has local pages for Hull, Inverness and Sunderland.
- One card gives its county as an abbreviation of South Yorkshire. A shortened county name was not taken as the place.

## Conversion
- `cta_types`: visit. One litter's card offers viewings. The cards link to advert pages, where the site's own message and number-reveal tools sit. None was fetched in this run, so no form, phone or message box is recorded.
- `prices_shown`: true. 36 distinct amounts are printed across the three pages, from £5 to £4,950. Most are general goods and farm animals on the homepage. On the Staffy search pages, adult rehomes run from £50 to £150, a young pup is £800, and cross-breed litters are £450 to £500.
- `deposit_terms`: the site shows no deposit terms of its own. One Staffy-cross litter's card says it takes a £100 deposit.
- `steps_to_enquire`: null. No enquiry form or message box was on the pages fetched.
- `urgency_signals`: `ready-date`. One litter's card gives a ready date. Nothing says few are left, and there are no waiting lists, deadlines or sold badges.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
Fetch: `map_calls` 2 · search map ran: yes · term `staffordshire bull terrier` · `search_added` 61 · `search_breed_urls` 3 · `search_adverts` 2 · `home_added` 0 · `map_list` 557 · scrapes 3 · credits 5 of a ceiling of 8.
- The first map held 496 URLs (`url_count`), below the 500 cap, and 0 breed URLs (`breed_urls`). The Map list script therefore asked for a search map (`search_map` true, `search_term` "staffordshire bull terrier"), and one ran with a limit of 100.
- The search map returned 64 URLs. One was on another site and was dropped, and two were already in the first map. That left 61 new URLs (`search_added`).
- Of those, 3 are breed pages on the site (`search_breed_urls`): the Grimsby, UK-wide and Manchester Staffy searches.
- 2 of the search map's URLs count as adverts by the key-page test (`search_adverts`). Both are really category pages (furniture and trailers). The test reads a single slug under a `classifieds` folder as an advert.
- The homepage links no breed page, so `home_added` is 0.
- Scrapes: 3, all live (not from cache).
  - the homepage, as markdown and raw HTML;
  - the UK "pitbull or staffy" page, as markdown;
  - the Manchester Staffy page, as markdown.
  The price-or-FAQ, guide and about slots were empty.
- Credits spent: 5 (2 maps + 3 scrapes at 1 credit each).

## Key insight
Preloved ranks for Staffy city searches with search-result pages that are generated automatically. Its Manchester Staffy page shows the same seven UK-wide adverts as its "pitbull or staffy" page. None of them is in Manchester, most are rehomes or crosses, and neither page has guide text, checks or trust signals. BSUK can beat those pages with real city pages that name the town and show the breeder's health results, the price and a direct way to enquire.
