# The Royal Kennel Club — competitor intel

- Root domain: royalkennelclub.com · tier 2 (the breed registry, ranking with its Find a puppy search and breed page) · analysed 2026-09-25. This is the entry's first report. The run used the classifier as updated today (commits 4e2fe7f, b8fb193, 50e1498 and bcab5b4).
- Homepage gate: passed. The status was 200, the final URL stayed on royalkennelclub.com, and there was no bot check. The homepage came from Firecrawl's cache.
- Fetched: 1 map (limit 500), which returned **495 URLs**, then 4 scrapes. The first was the homepage, with markdown and raw HTML. The other three were the classifier's key pages:
  - a late-litter-registration puppies page (listing slot);
  - the questions-to-ask-the-breeder guide (price-or-FAQ slot);
  - the dog-training hub (guide slot).
- The city and about slots had no page, so they were not scraped. The phone check ran in an emulated phone in Chrome DevTools. **5 Firecrawl credits in all.** The map is saved as a URL list at the controller's scratch path `maps/royalkennelclub.json`, so it can be re-typed later without spending credits.
- **The listing page is a sign-in wall.** The scrape was redirected to the club's account login host and returned only a cookie-and-sign-in screen marked noindex. Its entry in `pages` holds what that screen returned. Nothing about litters could be read from it, and no other page was fetched in its place.
- **No Staffy page was picked, because the map holds none.** No URL in the 495 names the breed. The breed appears only as one option in the homepage's Find a puppy breed drop-down. The club's Staffordshire Bull Terrier breed page, which the registry says also ranks, is not in the map, so it was not fetched and stays unanalysed.
- The map names another species once (a horse-show questionnaire under the forms folder). So the classifier ranks dog pages first in its fallback. That is why the FAQ-type breeder-questions guide, under the getting-a-dog folder, beat the two price-typed pages, which are fee forms.

## Trust
This is registry trust, not breeder trust:
- The homepage is built around pedigree registration: registering a dog, changing ownership, kennel names and a yearly registration figure. So `kc_registration_mentioned` is true.
- No fetched page names a specific health test. The homepage links to a health-test result finder and a health standard, but names no test.
- There is no council licence and no breeding-since claim. `vet_checks_mentioned` is false: the breeder-questions guide tells buyers to ask about vaccination and worming, and about a vet's written note if a puppy leaves early. It never describes a vet check of a litter.
- No fetched page states the club's base as a town. The homepage mentions its London club rooms and gallery as venues, not as a base, so `town` is null.
- The homepage measures script found no phone and no email on the homepage (raw HTML). No registered charity number is shown on the homepage.

Reviews: 0. The review list is empty (`grep -c .` gives 0). The homepage shows a consumer-magazine best-buy badge for the club's pet insurance. That is a badge with no review words, so it counts 0.

## Content
- **Homepage:** 2,592 words by script, and 6 H2s. Most of the words are the mega-menu and the Find a puppy breed drop-down, which lists every recognised breed. The page itself does four things:
  - a carousel of club news (joining Find a Breeder, an agility festival, the annual report, an art exhibition, insurance);
  - a puppy search by breed, distance and sex;
  - promo cards;
  - a short brand statement about the new Royal prefix.
- **Sign-in wall** (1 H2): a login screen, not content.
- **Breeder-questions guide** (4 H2s): two question lists, one to ask on the phone and one during a visit. Each question gets a one-line reason. The guide covers the mother's age and litter count, c-sections, health tests, inbreeding, the contract, microchipping and the age to go home. It ends by pointing to research on the parents' health.
- **Training hub** (0 H2s): six link cards (getting started, online academy, good-citizen scheme, instructors, child safety, finding a club) and a Crufts Club promo.

None of the fetched pages printed an H1 that means anything. The homepage's H1 tag is empty, and only the sign-in screen has one. The map returned 495 URLs, under the 500 cap. Much of it is forms, account-profile screens and judge-education pages.

## Keywords
None. The run rule found no qualifying phrase on any fetched page (by script). The breed name appears once, as a bare option in the breed drop-down, with no intent or place word next to it.

## Page types
By script over the 495-URL map, with no `--post-folder`: care-guide 80, listing 51, breed-guide 39, health 38, reviews 7, contact 2, price 2, about 1, blog 1, city 1, faq 1.
- **Care-guide and health:** mostly the dog-training folder and the health-and-care A to Z.
- **Listing:** mostly the getting-a-dog puppy pages, plus the logged-in litter-advert and late-litter-registration screens.
- **Reviews:** account "review" steps (judge education, puppy packs, litter registration), not customer reviews.
- **Price:** two fee forms.
- **About:** a registration-statistics page under the about folder. That is not the about page, so the about slot stayed empty.
- **City:** one London horse-show form.

## Blog
- `post_count` 1, `post_folder` null.
- The one post is a dated media-centre news item from 2019. The homepage links to a blog and a media centre under the about folder, but the map holds only that single dated item. So posts outside the map are missed.
- `posting_frequency` is NOT FETCHED: one dated URL gives no rate, and no post was fetched.
- `topics` and `sampled_word_counts` are NOT FETCHED: none of the key pages is a post.

## Visual
- From the homepage raw HTML, by script: 39 distinct images. Most alt text is descriptive, and 6 images have no alt.
- There is no video tag and no YouTube or Vimeo embed.

## Schema
The homepage JSON-LD holds one block: Organization (with a logo ImageObject and a PostalAddress), WebSite, and a SearchAction with an EntryPoint for site search. It has no breed, product, FAQ or breadcrumb markup.

## Cities
- London only. The homepage names the club's London venues, and the map's one city-typed URL is a London show form.
- The breed drop-down lists a Manchester Terrier. That is a breed, not the city, so it is not counted.

## Conversion
- `cta_types`: form only. The buyer's own action on the site is the Find a puppy search form, and the account sign-up and log-in.
- The enquiry itself happens off the fetched pages: the listing sits behind sign-in, and the breeder-questions guide tells the buyer to phone and visit the breeder, not the club.
- No puppy price or deposit is printed. The one amount on the homepage is an insurance cover limit, not a price, so `prices_shown` is false.
- `steps_to_enquire` is null, because no enquiry form was fetched. There are no urgency signals.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Key insight
The Royal Kennel Club ranks on registry authority, not on a Staffy page. Its puppy listing is behind a sign-in wall, its 495-URL map has no Staffordshire Bull Terrier page, and its buyer checklist is written for every breed. BSUK can win that buyer with a Staffy-specific version of the same checklist, answered openly on the page with its own health tests, registration papers and visible litters, and no login needed.
