# UKPets — competitor intel

- Root domain: ukpets.com · tier 2 (a free UK pet classifieds site where private owners and breeders post adverts for dogs, cats and other pets to sell, rehome, stud or want) · analysed 2026-09-25. This is the first report for this entry.
- Homepage gate: passed. The status was 200, the final URL stayed on ukpets.com, and the page was the live homepage, not a bot check or a parked page.
- Key pages, as the classifier picked them from the Map list (it flags the site as a `marketplace`: the map has cat sections and other breeds' city pages):
  - listing slot: the Staffy stud board. It is a breed hub with no type word in its path, so the classifier types it `listing`, and it wins on the fewest path segments;
  - price-or-FAQ slot: none. The footer links an FAQ page, but it is not in the Map list, and the homepage adds only breed links;
  - guide slot: none. The eight `breed-guide` URLs are other breeds' profiles (English and miniature bull terrier, Skye terrier and others), the breed groups pages and a page of the breed index. On a marketplace the guide must be the breed's own. The site's Staffy blog posts are typed `blog`, not guides;
  - city slot: a single Dundee advert for an adult Staffy. The path names Dundee, so it is typed `city`, and it has fewer segments than the Staffy city search pages;
  - about slot: none. The footer's about page is not in the Map list.
- Controller check: before scraping, each pick was checked for a breed or dog word. Both name the breed (`staffordshire-bull-terrier`), so no slot was skipped.
- Classifier gap: the city pick is an advert, but the key-page advert test does not see it. The site's advert slugs start with a six-digit id and a hyphen (`<id>-white-staffordshire-bull-terrier-dundee`). The test catches an id that ends the slug or stands alone, and a short id prefix only when a letter follows a digit, so an all-digit prefix passes. The same gap is why `search_adverts` is 0, although 11 of the search map's URLs are adverts. The pick was scraped as the classifier gave it.
- The first map is saved at `maps/ukpets.json` (500 URLs), the search map at `maps/ukpets.search.json` (74 URLs) and the homepage raw HTML at `maps/ukpets.home.html`.

## Trust
The platform itself shows no trust signals. What there is comes from sellers' own advert text.
- `council_licence_shown` false and `council` null. No page mentions a licence.
- `kc_registration_mentioned` true. Several stud adverts say the dog is KC registered, one homepage advert card says the same, and the Dundee advert's key facts give KC registration as "No".
- `health_tests_named`: L-2HGA and HC-HSF4, as one stud advert prints them (DNA clear for both). No other page names a test.
- `vet_checks_mentioned` true. One stud advert says its dog was vet checked.
- No breeding-since claim. The site names no base town, so `town` is null.
- The homepage measures script found no phone and no email in the homepage raw HTML (`contact_source` raw-html). The footer has a contact page link, which was not fetched.
- `reviews_shown` 0. No review, testimonial, star rating or badge appears on the three pages. The review list is empty and was counted by script.
- The homepage title calls the breeders trusted, but the advert page's safety notes say the site does not verify all advertisers.

## Content
- **Homepage:** 431 words by script and no H2. The markdown has one H1, a short slogan. It is a classifieds front page:
  - a header menu (for sale, adoption, stud, wanted), a blog menu, a tools menu (breed lists, breed finder quizzes, breed comparisons) and account links;
  - a search box with pet type, breed, advert type and price filters;
  - a strip of four new dog adverts, each with a photo, title, town and price (a miniature dachshund, a dachshund cross litter, a retired cocker spaniel and an adult cane corso);
  - a list of 61 town links for local pet searches;
  - footer link lists for tools, paid services, dog, cat and other pet sale sections, and the site's own pages.
  There is no text about the site, the breeds or how buying works.
- **Staffy stud board** (0 H2s): the first page of stud adverts for the breed, 12 cards per page across six pages. It opens with one sentence and a link to the site's breed profile. Each card shows a photo, title, town, the seller's text and a fee. The adverts range from proven, KC-registered and DNA-tested dogs to unproven pets, and one is a wanted advert looking for a stud. There is no guide text.
- **Dundee Staffy advert** (0 H2s): a private seller rehoming an adult neutered Staffy. It was published in August 2023 and is still live. The page has a key facts block (age band, microchip, vaccinations, neutered, not KC registered), the seller's short reason for selling, and phone and email buttons that show no number or address in the fetched content. The site adds buyer safety notes: do your research, visit the seller, never pay online, and puppies go only at 8 weeks or older. Below are four similar adverts and four of the site's Staffy blog posts.
- `url_count` NOT FETCHED: the first map returned exactly 500 URLs, so it was cut short. The site is much larger: 61 towns, each with a pets, dogs and cats page and a page per popular breed.

## Keywords
9 phrases by the run rule (by script) from the three pages and their titles.
- The stud board gives most of them: its H1 (`staffordshire bull terrier dogs and puppies`) and advert titles such as `kc registered blue staffie`, `blue staffy` and `kc registered staffordshire bull terrier`.
- `staffordshire bull terrier blue` comes from a stud advert's first sentence, where a comma joins the breed name to a coat colour. It is noise.
- The Dundee advert's similar-adverts strip gives `blue staffies`, `staffie for sale` and `staffordshire bull terrier pups for sale`, and a related post card gives `blue staffordshire bull terrier`.
- The homepage gives none, because it never names the breed.
- No run held a business, kennel or person's name, so nothing was cut.

## Page types
By script over the 567-URL Map list, with `--home` and `--search` set and no `--post-folder`: listing 378, city 150, blog 26, breed-guide 8. The classifier prints `marketplace: true`.
- **Listing (378):** town-level search pages for pets, dogs and cats (with a breed or without) in the towns that are not `data/locations.json` cities, the search map's Staffy stud board and other breeds' boards, and 9 single adverts from the search map (their paths say `for-sale`).
- **City (150):** the same town-level search pages for the 18 towns that are `data/locations.json` cities, among them the Staffy searches for nine of those cities (four from the first map, five from the search map), plus two single Staffy adverts whose slugs end in Dundee and Leeds.
- **Blog (26):** the blog index, seven articles (four about the Staffy, one about a Staffy cross, one on pit bulls, one on Britain's top dogs), five sitemaps, a topic page and twelve utility pages (log-in, register, account, thank-you and old campaign pages).
- **Breed guide (8):** other breeds' profiles, the breed groups pages and a page of the breed index.
- **Untyped:** the homepage and the site sitemap.

The first map covers only the start of the town-by-breed grid, so these counts describe a sample, not the site.

## Blog
- `post_count` 25, `post_folder` null. The classifier counts every URL under `/blog/` except the index. Only seven of the 25 are articles; the rest are sitemaps, a topic page and utility pages, so the true post count in the map is lower.
- The blog has its own post sitemaps. The posts sit under `/blog/`, not at the root, so the post-sitemap step does not apply.
- `posting_frequency`, `topics` and `sampled_word_counts` are NOT FETCHED: no post was fetched, and no post URL carries a date.

## Visual
- From the homepage raw HTML, by script: 14 distinct images, with descriptive alt text as the main class and 0 missing alts. They are the logo, the five pet-type icons and the four advert cards' photos (a full size and a thumbnail each).
- `video_present` false. There is no video tag and no YouTube or Vimeo embed. The only YouTube words are in the cookie tool's settings.

## Schema
The homepage raw HTML holds two JSON-LD blocks: an Organization, and an Article whose parts are a WebPage, ImageObjects, a Person and an Organization. The Article describes the homepage itself, with 2016 and 2019 dates. There is no Product, Offer, ItemList, FAQPage or BreadcrumbList markup. The other two pages were scraped as markdown, so their schema was not read.

## Cities
18 `data/locations.json` places are named on the fetched pages or have a page in the Map list: Birmingham, Bristol, Cardiff, Coventry, Dundee, Edinburgh, Glasgow, Hull, Leeds, Leicester, Liverpool, London, Manchester, Nottingham, Oxford, Sunderland, Wolverhampton and York.
- The homepage's town links name all 18 (Hull as Kingston upon Hull), and the map has local search pages for each.
- The stud board's cards name Liverpool, Nottingham and York; the Dundee advert names Dundee.
- The site's Newcastle pages are not Newcastle-under-Lyme, so that row was not taken.

## Conversion
- `cta_types`: phone, email and visit. The advert page's contact box has telephone and email buttons, and the site's safety notes tell buyers to visit the seller and see the puppy with its mother before paying. No enquiry form or message box was in the fetched content.
- `prices_shown`: true. 15 distinct amounts are printed across the three pages, from £100 to £1,200. The pound sign is drawn by an icon beside each card's number. On the stud board, fees run from £100 to £600, and one seller offers a reduced first fee of £350 before £450. The Dundee adult Staffy is £500, and the similar Staffy adverts are £200 to £700.
- `deposit_terms`: the site itself takes no deposit and warns buyers never to pay one online before viewing. One stud advert asks for a £250 deposit at mating when a puppy is the fee, returned when the puppy is collected.
- `steps_to_enquire`: null. No form or message box was on the pages fetched; the email button's form was not in the content.
- `urgency_signals`: none. No ready dates, few-left wording, waiting lists, deadlines, countdowns or sold badges.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
Fetch: `map_calls` 2 · search map ran: yes · term `staffordshire bull terrier` · `search_added` 67 · `search_breed_urls` 28 · `search_adverts` 0 · `home_added` 0 · `map_list` 567 · scrapes 3 · credits 5 of a ceiling of 8.
- The first map held exactly 500 URLs (`url_count` at the cap) and 15 breed URLs (`breed_urls`: the Staffy search page for each of the first 15 towns). The Map list script therefore asked for a search map (`search_map` true, `search_term` "staffordshire bull terrier"), and one ran with a limit of 100.
- The search map returned 74 URLs, all on the site. Six were already in the first map and one was the site sitemap listed twice (with and without `www.`), which left 67 new URLs (`search_added`).
- Of the search map's URLs, 28 are breed pages on the site (`search_breed_urls`): Staffy city searches, the stud board, Staffy adverts and Staffy blog posts.
- `search_adverts` is 0 because of the advert-test gap described at the top. By path, 11 of them are single adverts.
- The homepage links no breed page, so `home_added` is 0.
- Scrapes: 3, all live (not from cache).
  - the homepage, as markdown and raw HTML;
  - the Staffy stud board, as markdown;
  - the Dundee Staffy advert, as markdown.
  The price-or-FAQ, guide and about slots were empty.
- Credits spent: 5 (2 maps + 3 scrapes at 1 credit each).

## Key insight
UKPets ranks with free classified adverts, not breeder pages. Its Dundee pick is a private rehoming advert for an adult Staffy, first posted in 2023 and still live. Its Staffy listing in the Map list is a stud board, and the site itself says it does not verify its advertisers. BSUK can beat it with a breeder's own page that shows current litters, named health results, a clear price and a direct way to enquire.
