# UKPets — competitor intel

- Root domain: ukpets.com · tier 2 (a free UK pet classifieds site where private owners and breeders post adverts for dogs, cats and other pets to sell, rehome, stud or want) · analysed 2026-09-25. This is a consistency top-up of today's first run, redone under the final classifier rules (9d7e7b9). It replaces that report.
- Homepage gate: passed. The status was 200, the final URL stayed on ukpets.com, and the page was the live homepage, not a bot check or a parked page. The top-up reuses today's saved homepage (raw HTML and markdown), first map and search map at no cost.
- Key pages, as the final classifier picked them from the Map list (it flags the site as a `marketplace`: the map has cat sections and other breeds' city pages):
  - listing slot: the Staffy sale page for Bath. It is a **town page, not a national hub**: the Map list holds no national Staffy sale page, only the town-by-breed grid, so the classifier's fewest-segments, shortest-path order lands on Bath (Bath is not a `data/locations.json` city, so the page is typed `listing`, not `city`). Under the final rules a sale hub beats the stud board that was picked before;
  - price-or-FAQ slot: none. The footer links an FAQ page, but it is not in the Map list, and the homepage adds no breed links;
  - guide slot: none. The eight `breed-guide` URLs are other breeds' profiles, the breed groups pages and a page of the breed index. On a marketplace the guide must be the breed's own. The site's Staffy blog posts are typed `blog`, not guides;
  - city slot: the Staffy sale page for Dundee. Under the final rules the old pick, a single Dundee advert whose slug starts with an all-digit id, is an advert and is kept out of the city slot;
  - about slot: none. The footer's about page is not in the Map list.
- Dropped from the report: the Staffy stud board and the Dundee advert, which the earlier rules picked. Their values are gone from every field. The saved `ukpets/dundee.md` is that advert, not the hub, so it was not reused.
- Controller check: before scraping, each new pick was checked for a breed or dog word. Both name the breed (`staffordshire-bull-terrier`), so both were scraped.

## Trust
The platform itself shows no trust signals. What there is comes from sellers' own advert text on the cards.
- `council_licence_shown` false and `council` null. No page mentions a licence, a licence number or a council.
- `kc_registration_mentioned` true. One Staffy card on the town pages says the litter is KC registered, and one homepage card for another breed says the same.
- `health_tests_named`: none. No fetched page names a health test.
- `vet_checks_mentioned` true. One Staffy-cross card says the pups are vet checked before they leave.
- No breeding-since claim. The site names no base town, so `town` is null.
- The homepage measures script found no phone and no email in the homepage raw HTML (`contact_source` raw-html). The footer has a contact page link, which was not fetched.
- `reviews_shown` 0. No review, testimonial, star rating or badge appears on the three pages. The review list is empty and was counted by script.

## Content
- **Homepage:** 431 words by script and no H2. The markdown has one H1, a short slogan. It is a classifieds front page:
  - a header menu (for sale, adoption, stud, wanted), a blog menu, a tools menu and account links;
  - a search box with pet type, breed, advert type and price filters;
  - a strip of four new dog adverts, each with a photo, title, town and price (none of them a Staffy);
  - a list of town links for local pet searches;
  - footer link lists for tools, paid services, dog, cat and other pet sale sections, and the site's own pages.
  There is no text about the site, the breeds or how buying works.
- **Staffy sale page, Bath** (0 H2s): a breadcrumb, an H1 naming the breed and the town, one sentence that links the site's Staffy profile, sort options, then twelve advert cards and a pager that runs to 36 pages. Each card shows a photo, title, the seller's town, the seller's text and a price. Below the cards are links to twenty breeds' pages for the same town, and the footer.
- **Staffy sale page, Dundee** (0 H2s): the same page with the town name swapped into the breadcrumb, H1, title and links. The twelve cards are identical, in the same order.
- **Neither town page is local.** None of the twelve cards is in Bath or Dundee: the sellers are spread across England and Wales. The town pages are one national, newest-first feed of Staffy adverts dressed with a town name. There is no local text, no local count and no note that nothing nearby was found.
- The cards themselves mix litters of pups, adult dogs being rehomed, a Staffy-cross litter and a free-to-good-home dog.
- `url_count` NOT FETCHED: the first map returned exactly 500 URLs, so it was cut short. The site is much larger: dozens of towns, each with a pets, dogs and cats page and a page per popular breed.

## Keywords
10 phrases by the run rule (by script) from the three pages and their titles.
- The two town pages' H1 and titles give `staffordshire bull terrier dogs and puppies`. Their lead sentence gives `staffordshire bull terrier for sale`.
- The advert card titles give most of the rest: `blue staffies`, `staffie for sale`, `staffordshire bull terrier pups for sale`, `staffy pups for sale`, `staffy x pups for sale` and `blue staffordshire bull terrier puppies` (with its shortest sub-run `blue staffordshire bull terrier`).
- `staffordshire bull terriers in dundee` is the Dundee page's own link in its breeds strip. The Bath link gives no phrase, because Bath is not a `data/locations.json` city.
- The homepage gives none, because it never names the breed.
- No run held a business, kennel or person's name, so nothing was cut.

## Page types
By script over the 567-URL Map list, with `--home` and `--search` set and no `--post-folder`: listing 378, city 150, blog 26, breed-guide 8. The classifier prints `marketplace: true`. These counts are unchanged from the first run.
- **Listing (378):** town-level search pages for pets, dogs and cats (with a breed or without) in the towns that are not `data/locations.json` cities, the search map's Staffy stud board and other breeds' boards, and 9 single adverts from the search map (their paths say `for-sale`).
- **City (150):** the same town-level search pages for the 18 towns that are `data/locations.json` cities, among them the Staffy searches for nine of those cities, plus two single Staffy adverts whose slugs end in Dundee and Leeds.
- **Blog (26):** the blog index and 25 URLs under `/blog/` (see Blog).
- **Breed guide (8):** other breeds' profiles, the breed groups pages and a page of the breed index.
- **Untyped:** the homepage and the site sitemap.

The first map covers only the start of the town-by-breed grid, so these counts describe a sample, not the site.

## Blog
- `post_count` 25, `post_folder` null. This is the count the rule gives: the classifier counts every URL under `/blog/` except the index, and it has no filter for files or utility pages.
- **Only 7 of the 25 are real articles**: four about the Staffy, one about a Staffy cross, one on pit bulls and one on Britain's top dogs. The other 18 are 5 sitemap `.xml` files, 8 account or thank-you pages (log-in, register, account, profile, password reset and three thank-you pages), 4 covid or campaign notices and 1 topic page.
- The posts sit under `/blog/`, not at the root, so the post-sitemap step does not apply.
- `posting_frequency`, `topics` and `sampled_word_counts` are NOT FETCHED: no post was fetched, and no post URL carries a date.

## Visual
- From the homepage raw HTML, by script (re-run with `HOME_URL`): 14 distinct images, with descriptive alt text as the main class and 0 missing alts. They are the logo, the pet-type icons and the four advert cards' photos (a full size and a thumbnail each).
- `video_present` false. There is no video tag and no YouTube or Vimeo embed. The only YouTube words are in the cookie tool's settings.

## Schema
The homepage raw HTML holds two JSON-LD blocks: an Organization, and an Article whose parts are a WebPage, ImageObjects, a Person and an Organization. The Article describes the homepage itself, with 2016 and 2019 dates. There is no Product, Offer, ItemList, FAQPage or BreadcrumbList markup. The two town pages were scraped as markdown, so their schema was not read.

## Cities
19 `data/locations.json` places are named on the fetched pages or have a page in the Map list: Birmingham, Bristol, Cardiff, Coventry, Dundee, Edinburgh, Glasgow, Hull, Leeds, Leicester, Liverpool, London, Manchester, Middlesbrough, Nottingham, Oxford, Sunderland, Wolverhampton and York.
- The homepage's town links name 18 of them (Hull as Kingston upon Hull), and the map has local search pages for each.
- The town pages' cards name Oxford and Middlesbrough as sellers' towns. Middlesbrough is new against the first run: it comes only from a card, not from a page in the map. The Dundee page names Dundee.
- The site's Newcastle pages are not Newcastle-under-Lyme, so that row was not taken. Bath is not a `data/locations.json` row.

## Conversion
- `cta_types`: visit. On the fetched pages the only way a buyer is asked to act is in the sellers' own card text, which offers viewing the pups with their parents. The town pages carry no call, email or form button; the cards only say to get in touch, with no channel named. The homepage asks visitors to post an advert, which is not a buyer action.
- `prices_shown`: true. 13 distinct amounts, from £50 to £1,800, across the homepage's four cards and the town pages' twelve. The markdown prints bare numbers; the homepage raw HTML shows each card's number drawn beside a pound-sign icon, and the town pages use the same card design. Staffy cards run from £50 (a free-to-good-home dog with a token price) to £1,800 (a blue litter); most litters sit between £600 and £900.
- `deposit_terms`: the site states no deposit terms on the pages fetched. Several sellers ask a deposit of £100 to £200 to secure a puppy, and one offers a payment plan.
- `steps_to_enquire`: null. No form or message box was on the pages fetched.
- `urgency_signals`: ready-date and few-left. Cards give ready-to-leave dates, and several say only a few pups are left.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran again in this top-up, in Chrome DevTools emulating a 375 × 812 phone with a mobile user agent and touch, on the homepage. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
Fetch: `map_calls` 2 · search map ran: yes · term `staffordshire bull terrier` · `search_added` 67 · `search_breed_urls` 28 · `search_adverts` 11 · `home_added` 0 · `map_list` 567 · scrapes today 5 (3 in the first run, 2 in this top-up) · credits 7 of a ceiling of 8.
- The first map held exactly 500 URLs (`url_count` at the cap) and 15 breed URLs (`breed_urls`: the Staffy search page for each of the first 15 towns). The Map list script therefore asked for a search map (`search_map` true, `search_term` "staffordshire bull terrier"), and one ran with a limit of 100. Both maps were spent in the first run and reused here at no cost.
- The search map returned 74 URLs, all on the site. Six were already in the first map and one was the site sitemap listed twice (with and without `www.`), which left 67 new URLs (`search_added`).
- Of the search map's URLs, 28 are breed pages on the site (`search_breed_urls`): Staffy city searches, the stud board, Staffy adverts and Staffy blog posts. 11 of its URLs are adverts by the key-page test (`search_adverts`); the final rules catch the all-digit id prefix the earlier test missed.
- The homepage links no breed page, so `home_added` is 0.
- Scrapes in this top-up: 2, both live, markdown only.
  - the Staffy sale page for Bath (the listing pick);
  - the Staffy sale page for Dundee (the city pick).
  The first run's 3 scrapes were the homepage (markdown and raw HTML, reused here), the stud board and the Dundee advert (both dropped from the report).
- Credits spent today: 7 (2 maps + 5 scrapes at 1 credit each); 2 of them in this top-up.

## Key insight
UKPets's town pages are one national Staffy feed with the town name swapped into the title and H1. The Bath and Dundee pages list the same twelve adverts, and none of them is in either town. BSUK can beat it with location pages that carry real local detail, a breeder's own current litters, named health results and a clear price.
