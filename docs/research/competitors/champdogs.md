# Champdogs — competitor intel

- Root domain: champdogs.co.uk · tier 2 (a pedigree breeder directory: breeders build a profile site on it, list litters and stud dogs, and buyers browse by breed) · analysed 2026-09-25. This is the entry's first report. The run used the fetch and classifier steps as updated today (commits up to 2234777): the Map list step with its search map, `--home` for the classifier, and this Fetch line.
- Homepage gate: passed. The status was 200, the final URL stayed on champdogs.co.uk, and the page was the live homepage. It loads a background Cloudflare script, but the page served was the real homepage, not a bot check or a parked page.
- Key pages, as the classifier picked them from the Map list:
  - listing slot: a single litter page from 2007, a Kent kennel's show Staffy litter that sold long ago. The breed's own puppies page sits in a `breeds` folder, so the table types it `breed-guide`. No listing URL names the breed in its path (litter pages are numbered), so the slot fell back to the shortest non-advert litter URL, which has a four-digit id;
  - price-or-FAQ slot: none. No URL in the Map list has a price or FAQ word in its path, so nothing was scraped;
  - guide slot: the Staffordshire Bull Terrier puppies page (the breed's live litter list), typed `breed-guide` by its `breeds` folder;
  - city slot: none. No Map list URL carries a `data/locations.json` city in its path;
  - about slot: none. The Map list holds no about page.
- **The first map missed the breed.** It returned 94 URLs, well short of the cap, but none had a breed path: 30 breeder profiles and the breeder index, 24 breed hubs for other breeds, 18 dog pages, 18 numbered litters, a help page, a guide and a forum thread. Two of the numbered litters were Staffy litters, but their paths never name the breed. So the Map list asked for one search map. It returned 24 URLs, 20 of them new to the list, and 3 of them the breed's own hubs (puppies, breeders, stud dogs). The homepage links to no breed page (its breed picker is a select box, not links), so it added nothing. The Map list holds 114 URLs.
- The maps are saved as JSON URL lists at the controller's scratch paths `maps/champdogs.json` (the first map) and `maps/champdogs.search.json` (the search map), so they can be re-typed later without spending credits.

## Trust
The trust here belongs to the directory and its breeders, and it rests on pedigree and health data rather than on reviews or badges:
- The litter page shows a verified-health-tests panel for the parent it covers, with HC and L-2-HGA each marked clear, and links to what each test means. The text of the advert says the same again and adds microchipping, vaccination, worming and a few weeks of free insurance. The page closes with a four-generation pedigree full of champions.
- The Staffy puppies page tags each litter card by how fully its sire and dam are health tested, and one card names the L2HGA, HC and HSF4 DNA tests. Buyers can filter by those tests and by 25 others.
- The homepage calls the site the UK's best pedigree breeders' site, established in 1999, and headlines responsible breeding.

The fields:
- `council_licence_shown`: false. No fetched page mentions a council licence, so `council` is null.
- `kc_registration_mentioned`: true. The litter page's title calls the pups pedigree KC registered.
- `health_tests_named`: L-2-HGA, HC and HSF4, as the litter page and a puppies-page card print them.
- `vet_checks_mentioned`: false. The pages mention vaccination, worming and microchipping, but none says the puppies are vet checked.
- `breeding_since_as_worded`: null. The site's own 1999 date is the platform's, not a breeder's claim.
- `town`: null. The site names no base on the fetched pages; only its operating company's name sits in the footer.
- The homepage measures script found no phone and no email in the homepage raw HTML.

Reviews: 0. No fetched page shows a customer review or testimonial. The scratch list was empty, and `grep -c .` counted 0.

## Content
- **Homepage:** 622 words by script, and 9 H2s. Six are real sections and three belong to a hidden pop-up that asks phone users which version of the site they want. The page is plain and old-fashioned. It has a single-line H1 about responsible breeding, then short blocks: build a breeder website, list a litter, look for a puppy (with a breed picker listing about 230 breeds, which is most of the words), the litter waiting list, search by breed, and the blog and forum. It says nothing about Staffies beyond the breed's name in the picker.
- **Litter page** (5 H2s, three of them the pop-up): two photos, a sold-out notice with a link to the breed's live litters, the verified health panel, a three-line advert in capitals, and the pedigree. The menu lists the kennel's 16 Staffy litters from 2004 to 2025, with a gallery and a contact link.
- **Staffy puppies page** (3 H2s, all the pop-up): an H1, a long filter panel (country, show or working, sex, 27 coat colours, five of them with blue, and 28 health tests), a count of six litters, links to the buyer's guide and waiting list, and six litter cards. Each card gives the sire and dam, the breeder's town and county, the due or birth date, the health-test tag, a photo and a short blurb from the breeder. The six towns are Milton Keynes, Crawley, Bolsover, Frome, Rochdale and Blaenau Ffestiniog.
- `url_count`: 94, the first map's length (under the cap of 500).

## Keywords
3 phrases by the run rule (by script) from the three pages and their titles:
- the litter page's title, which puts KC registered in front of the breed's full name and puppies;
- the breed's full name with puppies, from the litter page's H1, its menu, the puppies page's H1 and a litter card;
- the puppies page's title, which adds for sale.

No run held a business, kennel or person's name. The kennel's name opens the litter page's H1, but it sits before the run, which starts at the breed name. The site never uses staffy, staffie or blue next to the breed on the fetched pages. Blue appears only as a colour filter.

## Page types
By script over the 114-URL Map list, with `--home` and `--search` set and no `--post-folder`: breed-guide 30, listing 20, health 1.
- **Breed guide (30):** everything under the `breeds` folder: 4 breed hubs, 13 breeder lists, 10 puppy lists and 2 stud-dog lists, across many breeds. That includes the three Staffy hubs from the search map. There is also one real breed guide (Shih Tzu) in a `guide` folder. The table types the `breeds` folder by its word, so these counts are mostly lists of litters and breeders, not guides.
- **Listing (20):** numbered litter pages. By the map titles, four are Staffy litters, two from each map.
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
The homepage raw HTML holds no JSON-LD block, so `schema_types` is an empty list. The other pages were scraped as markdown, so their schema was not read.

## Cities
None. No fetched page names a `data/locations.json` city, by script. The homepage names none. The litter is in Maidstone, and the six live litters are in the six towns listed under Content. Manchester appears only inside a breed's name (Manchester Terrier) in the homepage's breed picker, which is not a place.

The search map returned the Staffy puppies page and the breeder index with titles naming a nearby town (Manchester and Lincoln). The site seems to re-title these pages around the visitor's location. The scrape got the plain, untargeted version, so that is recorded here and nowhere in the JSON.

## Conversion
- `cta_types`: form. The litter page's menu offers a contact link to the site's own contact script for that kennel. The form itself was not fetched. Otherwise the pages ask a buyer to browse the litter list, read the buyer's guide, or join the waiting list by email alert. None prints a phone number or email address.
- `prices_shown`: false. No fetched page prints a price or deposit, and `deposit_terms` is null.
- `steps_to_enquire`: null. No enquiry form was fetched.
- `urgency_signals`:
  - `waiting-list`: the site-wide litter waiting list, the breed's own waiting-list link, and one card that says its waiting list is open;
  - `few-left`: one card says a single puppy is still available;
  - `sold-badges`: the litter page marks the whole litter as sold.
  The due and birth dates on the cards are dates, not ready dates, so `ready-date` is not recorded.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true. The site sets a device-width viewport and also offers a separate mobile version.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
- `map_calls` 2. The search map ran because the first map held no breed URL (`breed_urls` 0). `url_count` was 94, under the cap. Its term was `staffordshire bull terrier`: the homepage names the breed in full and never as staffy.
- The search map added 20 URLs (`search_added`). It returned 3 breed pages on the site (`search_breed_urls`: the Staffy puppies, breeders and stud-dog hubs). 11 of its URLs are adverts by the key-page test (`search_adverts`). These are breeder, dog, club and litter pages whose path ends in a numeric id, not sale adverts as such.
- The homepage's breed links added 0 URLs (`home_added`), which makes `map_list` 114.
- Scrapes: 3. That is the homepage (markdown and raw HTML) plus two key pages (markdown). The price-or-FAQ, city and about slots were empty.
- Credits spent: 5 (2 maps + 3 scrapes), against a ceiling of 8.

## Key insight
Champdogs wins Staffy searches on pedigree authority, not content. Each litter shows verified KC pedigrees and verified health results, and the breed's one puppies page seems to re-title itself around the searcher's nearest town. The pages are thin, show no prices, and on the day listed six Staffy litters, none of them in a BSUK city. BSUK can beat it with real city pages, a stated price and deposit, and the same verified L-2-HGA and HC results shown on every blue litter.
