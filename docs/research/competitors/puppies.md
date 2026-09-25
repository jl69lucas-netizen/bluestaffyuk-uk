# Puppies.co.uk — competitor intel

- Root domain: puppies.co.uk · tier 2 (an all-breed puppy marketplace for sale, stud, rescue and wanted adverts, with a breed directory and an advice section) · analysed 2026-09-25. This is the entry's first report. The run used the fetch and classifier steps as updated today (commits up to 2234777): the Map list step with its search map, `--home` for the classifier, and this Fetch line.
- Homepage gate: passed. The status was 200, the final URL stayed on puppies.co.uk, and the page was the live homepage, not a bot check or a parked page.
- Key pages, as the classifier picked them from the Map list:
  - listing slot: the Staffordshire Bull Terrier for-sale hub for Leek, a small Staffordshire town. The Liverpool hub is typed `city`, and the site's UK-wide Staffy for-sale hub is not in the Map list, so the listing slot took the shortest remaining breed listing;
  - price-or-FAQ slot: none. No URL in the Map list has a price or FAQ word in its path, so nothing was scraped;
  - guide slot: the Staffordshire Bull Terrier breed-information page (the homepage links it from its popular-breeds strip);
  - city slot: the Staffordshire Bull Terrier for-sale hub for Liverpool;
  - about slot: none. The Map list holds no about page, so nothing was scraped.
- **The first map missed the breed.** It hit the 500 cap, and every URL but the 24 sitemap files is a Lancashire Heeler for-sale town hub (476 of them). It held no breed path, so the Map list asked for one search map. That search map returned 62 URLs: 20 of them Staffy pages, and 51 new to the list. The homepage added one breed link, the breed-information page. The Map list holds 552 URLs.
- The maps are saved as JSON URL lists at the controller's scratch paths `maps/puppies.json` (the first map) and `maps/puppies.search.json` (the search map), so they can be re-typed later without spending credits.

## Trust
This is platform trust, not breeder trust. The site lists other people's litters, and it puts its own checks up front:
- a strip over the header on verified listings and a health guarantee;
- four trust tiles on the homepage: a five-week health guarantee, ID checks for breeders, a human trust-and-safety team (with video calls for a share of breeders), and a claim that only half of the breeders who apply are accepted;
- a Trustpilot widget showing a star score, and a claim to have homed over 220,000 puppies.

The fields:
- `council_licence_shown`: true. A homepage advert card carries a licensed-breeder badge, and the menus offer a search of licensed breeders. No council is named anywhere, so `council` is null.
- `kc_registration_mentioned`: true. Advert cards carry a Kennel Club registered badge, and one Staffy advert title calls its pups KC registered.
- `health_tests_named`: none. Cards carry a generic health-tested badge that names no test. The breed page lists conditions the breed can have (hip and elbow dysplasia, kneecap luxation, juvenile cataracts, L-2-HGA and others) but never recommends a test for them.
- `vet_checks_mentioned`: false. The pages talk about vaccinations, microchipping and a health guarantee, but no fetched page says the puppies are vet checked.
- No breeding-since claim. The homepage's JSON-LD gives Market Harborough as the business's town, so `town` is Market Harborough. The visible page names no base.
- The homepage measures script found no phone and no email in the homepage raw HTML.

Reviews: 6. The homepage carousel shows six testimonials with their words: four from buyers and two from sellers. Each was listed once in a scratch file and counted with `grep -c .`. The Trustpilot widget shows a star score only, with no review words, so it adds nothing.

## Content
- **Homepage:** 1,495 words by script, and 10 H2s. The H1 is a short line about how hard trusted breeders are to find, over search boxes for puppies, studs, rescues, breeds and advice. Below that sit:
  - the trust tiles;
  - three promoted adverts;
  - press logos;
  - the testimonial carousel;
  - three of the latest adverts and a live count of more puppies waiting;
  - a strip of 21 popular breeds, which includes the Staffordshire Bull Terrier;
  - popular-location links for sale, rescue and stud across about 50 towns and cities;
  - links to the breeder directories;
  - four dated advice articles.
  A large share of the words is the menu, repeated in the page, and the location lists. None of the homepage's content is about Staffies.
- **Leek hub** (3 H2s): the breed's H1 with the town, a stock paragraph on the breed's history, a live count of six adverts, sort options, one promoted advert (from Bolsover), a recommended-for-you strip of four adverts (the Bolsover litter again, one from Llanedeyrn and two stud dogs from Wigan and Scunthorpe), and 20 nearest-town links. None of the adverts shown is in Leek.
- **Breed page** (16 H2s): the longest page. Links to breeders, sale and adoption for the breed, a facts panel (size, grooming, lifespan, exercise, trainability and so on), links to 28 coat-colour listings (blue among them), then sections on why the breed suits families, its downsides, history, appearance, temperament, health, care, costs and a short buying guide, all as question-led H4s. It closes with four latest Staffy adverts and four advice articles.
- **Liverpool hub** (3 H2s): the same template as Leek. It shows the same stock paragraph and a live count of 20 adverts, but the feed shows only two adverts, each twice, both from a seller in Lancashire. The recommended strip and the nearby-town links follow, as on Leek.
- `url_count` is NOT FETCHED: the first map holds exactly 500 URLs, so it was cut at the cap.

## Keywords
8 phrases by the run rule (by script) from the four pages and their titles:
- the hubs' H1 and title pattern: the breed's full name with puppies and for sale;
- an advert title that uses "pups" with the breed name;
- the breed page's link to breeders of the breed, its opening sentence (puppies known as Staffies), and its many "Staffordshire Bull Terrier puppy" questions;
- an advert titled with the word puppy before the breed name;
- the breed page's title, which uses "Staffy puppy".

One run the script found was dropped. It joined two separate links on the breed page (breeders, then puppies for sale), and words from different places never make one phrase. No run held a business, kennel or person's name. The site never pairs the breed with a city it serves: the town hubs put "near me in <town>, <county>" after the breed, which is too long for one run.

## Page types
By script over the 552-URL Map list, with `--home` and `--search` set and no `--post-folder`: listing 504, city 19, breed-guide 3.
- **Listing (504):**
  - 461 Lancashire Heeler town hubs from the first map;
  - 17 Staffy URLs from the search map: 15 town hubs, the pedigree Staffy hub and one advert;
  - 26 other for-sale pages the search map returned: 19 all-breed town hubs, two other breeds' UK hubs and five other breeds' town pages.
- **City (19):** 15 Lancashire Heeler town hubs whose slugs carry a `data/locations.json` city word, most as a county tag such as greater-manchester, plus the Staffy hubs for Liverpool and Sheffield (tagged south-yorkshire), a Staffy advert in Leeds, and the all-breed Cardiff hub.
- **Breed guide (3):** the Staffy breed page and two other breeds' pages.
- **Untyped:** the 24 sitemap files, the homepage and one stud hub.

The counts say more about the maps than the site. The first map is one breed's town-hub sweep, and the search map is a sample of Staffy and all-breed hubs.

## Blog
- `post_count` 0, `post_folder` null.
- The site keeps its articles in an advice folder. The homepage and the breed page each show four dated articles, but the Map list holds none of them. The first map returned only hub pages, and the homepage adds only breed links. So `--post-folder` would have had nothing to count, and the posts are missed.
- `posting_frequency`, `topics` and `sampled_word_counts` are NOT FETCHED: no post was counted or fetched.

## Visual
- From the homepage raw HTML, by script: 74 distinct images. Most alt text is descriptive (breed names, badge labels and trust-tile titles), and 25 images have no alt. Those are mostly icons on advert cards and in the menu, plus four insurance banner ads and the footer logo.
- There is no video tag and no YouTube or Vimeo embed.

## Schema
The homepage raw HTML holds one JSON-LD block: an OnlineStore with an OnlineBusiness as its parent organisation and a PostalAddress at town level, plus a founding date. There is no Product, Offer, ItemList, FAQPage or BreadcrumbList markup on the homepage. The other pages were scraped as markdown, so their schema was not read.

## Cities
21 `data/locations.json` cities are named on the fetched pages: Aberdeen, Birmingham, Bristol, Cardiff, Coventry, Dundee, Edinburgh, Glasgow, Hull, Leeds, Leicester, Liverpool, London, Manchester, Middlesbrough, Newcastle-under-Lyme, Nottingham, Oxford, Sunderland, Wolverhampton and York.
- Most come from the homepage's popular-location lists. Hull is named there by its full name, Kingston upon Hull.
- Newcastle-under-Lyme comes from the Leek hub's nearest-town links.
- Birmingham is also named in the breed blurb on the two hubs.
- Liverpool has its own Staffy hub.

Essex and South Yorkshire are left out. They appear only as county tags in other towns' slugs, never as a place a page names or serves.

## Conversion
- `cta_types`: online-deposit. The menus and the advert badges offer a protected deposit through a third-party payment service. Otherwise the pages ask a buyer to search, filter, open an advert or subscribe to a newsletter. Messaging a seller happens on the advert pages, which were not fetched.
- `prices_shown`: true. The amounts come from:
  - advert prices, from £950 to £2,850 for puppies;
  - stud fees on the recommended strips (£250 to £500);
  - the breed page's rough cost-to-buy range (£400 to £1600) and its monthly food cost (£40).
- `deposit_terms`: the platform offers a protected deposit scheme through a third-party payment service, and adverts that use it carry a badge. No amount or terms are stated on the pages fetched.
- `steps_to_enquire`: null. No enquiry form or message box was fetched.
- `urgency_signals`: `ready-date`. Cards say whether the pups are ready to leave now or not yet, and give their age. No card says few are left, and the live listing counts are not urgency.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
- `map_calls` 2. The search map ran because `url_count` hit the cap (500) and the first map held no breed URL (`breed_urls` 0). Its term was `staffordshire bull terrier`: the homepage names the breed in full.
- The search map added 51 URLs (`search_added`). It returned 20 breed pages on the site (`search_breed_urls`), and 0 of its URLs are adverts by the key-page test (`search_adverts`). The two Staffy adverts it returned have plain slugs, with no id.
- The homepage's breed links added 1 URL (`home_added`), which makes `map_list` 552.
- Scrapes: 4. That is the homepage (markdown and raw HTML) plus three key pages (markdown). The price-or-FAQ and about slots were empty.
- Credits spent: 6 (2 maps + 4 scrapes), against a ceiling of 8.

## Key insight
Puppies.co.uk wins Staffy-plus-town searches with a hub for every town. The hubs are templated: one stock breed paragraph over a short feed of the same few adverts, mostly from other towns and padded with stud dogs. Its trust sits at platform level: ID checks, a vetting team, a five-week health guarantee and a protected deposit. BSUK can beat those hubs with city pages built on one breeder's own blue Staffy litters, named health tests, real local detail, and a stated price and deposit. It should also give its own answers to the reassurances the platform offers.
