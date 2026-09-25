# Champdogs — competitor intel

- Root domain: champdogs.co.uk · tier 2 (a pedigree breeder directory: breeders build a profile site on it, list litters and stud dogs, and buyers browse by breed) · analysed 2026-09-25. This is the entry's first report. The run used the fetch and classifier steps as updated today (commits up to 2234777): the Map list step with its search map, `--home` for the classifier, and this Fetch line.
- Homepage gate: passed. The status was 200, the final URL stayed on champdogs.co.uk, and the page was the live homepage. It loads a background Cloudflare script, but the page served was the real homepage, not a bot check or a parked page.
- **Re-typed in the G1 consistency pass (0 credits).** The saved Map list was run again through the final classifier (commit 9d7e7b9). A breeds folder's `puppies`, `breeders` and `stud-dogs` pages are now listings, not breed guides, and the classifier prints `marketplace: true` (a directory: the Staffy and many other breeds in its breeds folder). So the breed's own puppies page moved from the guide slot to the listing slot. The 2007 litter page the first pick chose is no longer a key page, and it has been taken out of `pages` along with every value that came only from it.
- Key pages, as the final classifier picks them from the Map list:
  - listing slot: the Staffordshire Bull Terrier puppies page (the breed's live litter list). On a directory the listing is the breed's own page whenever it has one. The puppies page beats the breeders hub on the shorter path and the stud-dog hub because a sale hub comes before a stud board;
  - price-or-FAQ slot: none. No URL in the Map list has a price or FAQ word in its path, so nothing was scraped;
  - guide slot: none. On a directory the guide must be the breed's own, and no Staffy guide is in the Map list (the one real guide is for the Shih Tzu);
  - city slot: none. No Map list URL carries a `data/locations.json` city in its path;
  - about slot: none. The Map list holds no about page.
- **The first map missed the breed.** It returned 94 URLs, well short of the cap, but none had a breed path: 30 breeder profiles and the breeder index, 24 breed hubs for other breeds, 18 dog pages, 18 numbered litters, a help page, a guide and a forum thread. Two of the numbered litters were Staffy litters, but their paths never name the breed. So the Map list asked for one search map. It returned 24 URLs, 20 of them new to the list, and 3 of them the breed's own hubs (puppies, breeders, stud dogs). The homepage links to no breed page (its breed picker is a select box, not links), so it added nothing. The Map list holds 114 URLs.
- The maps are saved as JSON URL lists at the controller's scratch paths `maps/champdogs.json` (the first map) and `maps/champdogs.search.json` (the search map), so they can be re-typed later without spending credits.

## Trust
The trust here belongs to the directory and its breeders, and it rests on pedigree and health data rather than on reviews or badges:
- The Staffy puppies page tags each litter card by how fully its sire and dam are health tested, and one card names the L2HGA, HC and HSF4 DNA tests. Buyers can filter by those tests and by 25 others.
- The homepage calls the site the UK's best pedigree breeders' site, established in 1999, and headlines responsible breeding.

The fields:
- `council_licence_shown`: false. No fetched page mentions a council licence, so `council` is null.
- `kc_registration_mentioned`: false. The only KC mention was the dropped litter page's title. Neither the homepage nor the puppies page mentions the Kennel Club or KC registration.
- `health_tests_named`: L-2-HGA, HC and HSF4, as a puppies-page card prints them (the dropped litter page named the first two as well).
- `vet_checks_mentioned`: false. A puppies-page card mentions microchipping, but no page says the puppies are vet checked.
- `breeding_since_as_worded`: null. The site's own 1999 date is the platform's, not a breeder's claim.
- `town`: null. The site names no base on the fetched pages; only its operating company's name sits in the footer.
- The homepage measures script found no phone and no email in the homepage raw HTML.

Reviews: 0. No fetched page shows a customer review or testimonial. The scratch list was empty, and `grep -c .` counted 0.

## Content
- **Homepage:** 622 words by script, and 9 H2s. Six are real sections and three belong to a hidden pop-up that asks phone users which version of the site they want. The page is plain and old-fashioned. It has a single-line H1 about responsible breeding, then short blocks: build a breeder website, list a litter, look for a puppy (with a breed picker listing about 230 breeds, which is most of the words), the litter waiting list, search by breed, and the blog and forum. It says nothing about Staffies beyond the breed's name in the picker.
- **Staffy puppies page** (3 H2s, all the pop-up): an H1, a long filter panel (country, show or working, sex, 27 coat colours, five of them with blue, and 28 health tests), a count of six litters, links to the buyer's guide and waiting list, and six litter cards. Each card gives the sire and dam, the breeder's town and county, the due or birth date, the health-test tag, a photo and a short blurb from the breeder. The six towns are Milton Keynes, Crawley, Bolsover, Frome, Rochdale and Blaenau Ffestiniog.
- `url_count`: 94, the first map's length (under the cap of 500).

## Keywords
2 phrases by the run rule (by script) from the homepage, the puppies page and their titles:
- the breed's full name with puppies, from the puppies page's H1 and a litter card;
- the puppies page's title, which adds for sale.

The dropped litter page's KC-registered title phrase is no longer counted. No run held a business, kennel or person's name. The site never uses staffy, staffie or blue next to the breed on the fetched pages. Blue appears only as a colour filter.

## Page types
By script over the 114-URL Map list, with `--home` and `--search` set and no `--post-folder`, under the final classifier: listing 45, breed-guide 5, health 1. The classifier prints `marketplace: true`.
- **Listing (45):**
  - 25 pages under the `breeds` folder whose last segment is `puppies`, `breeders` or `stud-dogs`: 13 breeder lists, 10 puppy lists and 2 stud-dog lists, across many breeds. The three Staffy hubs from the search map are among them;
  - 20 numbered litter pages. By the map titles, four are Staffy litters, two from each map.
- **Breed guide (5):** the 4 breed hubs under the `breeds` folder (all for other breeds) and one real breed guide (Shih Tzu) in a `guide` folder.
- **Health (1):** the page on one eye-testing scheme.
- **Untyped:** 35 breeder profiles, 21 dog pages, 3 breed-club pages, a help page, a forum thread, the breeder index and the homepage.

The first map is a random sample of a very large directory, so these counts say more about the sample than the site.

## Blog
- `post_count` 0, `post_folder` null.
- The homepage links to a Champdogs blog and to a forum on a subdomain. The Map list holds no blog URL and one forum thread, so no post was counted.
- `posting_frequency`, `topics` and `sampled_word_counts` are NOT FETCHED: no post was counted or fetched.

## Visual
- From the homepage raw HTML, by script: 3 distinct images: a small dog photo and the logo in the header, and a loading spinner. All three have descriptive alt text, so none is missing. The breed art beside each block is CSS sprites, which do not count here.
- There is no video tag and no YouTube or Vimeo embed.

## Schema
The homepage raw HTML holds no JSON-LD block, so `schema_types` is an empty list. The puppies page was scraped as markdown, so its schema was not read.

## Cities
None. No fetched page names a `data/locations.json` city, by script. The homepage names none. The six live litters are in the six towns listed under Content. Manchester appears only inside a breed's name (Manchester Terrier) in the homepage's breed picker, which is not a place.

The search map returned the Staffy puppies page and the breeder index with titles naming a nearby town (Manchester and Lincoln). The site seems to re-title these pages around the visitor's location. The scrape got the plain, untargeted version, so that is recorded here and nowhere in the JSON.

## Conversion
- `cta_types`: none. The only enquiry route recorded before, a kennel contact link, was on the dropped litter page. The homepage and the puppies page ask a buyer only to browse the litter list, read the buyer's guide, or join the waiting list for email alerts, and an alert sign-up is not an enquiry. Neither prints a phone number or email address.
- `prices_shown`: false. No fetched page prints a price or deposit, and `deposit_terms` is null.
- `steps_to_enquire`: null. No enquiry form was fetched.
- `urgency_signals`:
  - `waiting-list`: the site-wide litter waiting list, the breed's own waiting-list link, and one card that says its waiting list is open;
  - `few-left`: one card says a single puppy is still available.
  The dropped litter page's sold notice is no longer counted, so `sold-badges` is not recorded.
  The due and birth dates on the cards are dates, not ready dates, so `ready-date` is not recorded.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true. The site sets a device-width viewport and also offers a separate mobile version.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
- `map_calls` 2. The search map ran because the first map held no breed URL (`breed_urls` 0). `url_count` was 94, under the cap. Its term was `staffordshire bull terrier`: the homepage names the breed in full and never as staffy.
- The search map added 20 URLs (`search_added`). It returned 3 breed pages on the site (`search_breed_urls`: the Staffy puppies, breeders and stud-dog hubs). 11 of its URLs are adverts by the key-page test (`search_adverts`). These are breeder, dog, club and litter pages whose path ends in a numeric id, not sale adverts as such.
- The homepage's breed links added 0 URLs (`home_added`), which makes `map_list` 114.
- Scrapes: 3. That is the homepage (markdown and raw HTML) plus two key pages (markdown) under the first pick: the 2007 litter page and the Staffy puppies page. Under the final classifier only the puppies page is a key page (the listing), so the litter page is left out of this report. The price-or-FAQ, guide, city and about slots are empty.
- Credits spent: 5 (2 maps + 3 scrapes), against a ceiling of 8.

## Key insight
Champdogs wins Staffy searches on the authority of a pedigree directory, not on content. Its one Staffy puppies page tags each litter by how fully the parents are health tested, lets buyers filter by named DNA tests, and seems to re-title itself around the searcher's nearest town. The page is thin, shows no prices, and on the day listed six Staffy litters, none of them in a BSUK city. BSUK can beat it with real city pages, a stated price and deposit, and the same named L-2-HGA and HC results shown on every blue litter.
