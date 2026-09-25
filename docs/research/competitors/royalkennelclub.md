# The Royal Kennel Club — competitor intel

- Root domain: royalkennelclub.com · tier 2 (the breed registry, ranking with its Find a puppy search and breed page) · analysed 2026-09-25.
- **This is a consistency top-up** of today's first report, rewritten under the final rules (agent file at 9d7e7b9). The earlier run predated the Map list step, so it never ran the search map. This run added that search map and re-picked the key pages. Today's first map, homepage (markdown and raw HTML) and the breeder-questions guide were reused from today's earlier run at no cost.
- Homepage gate: passed (checked in today's first run). The status was 200, the final URL stayed on royalkennelclub.com, and there was no bot check.
- **The breed page was found this time.** The first map has no Staffy URL. The search map returned the club's Staffordshire Bull Terrier breed page (Breeds A to Z). The classifier picked it for the guide slot, and it was scraped and analysed below.
- Key pages now, by the classifier over the merged Map list:
  - listing: the Find a puppy search page. It names a puppy, so it passed the check before scraping.
  - price-or-FAQ: the questions-to-ask-the-breeder guide (unchanged, reused).
  - guide: the Staffordshire Bull Terrier breed page. It names the breed.
  - city and about: none, so not scraped.
- **Dropped from the report:** the old listing pick (a late-litter-registration page behind a sign-in wall) and the old guide pick (the dog-training hub). Neither is a pick any more, so their pages, H2 counts and facts have left the report.
- The classifier prints `marketplace: true`. The club's breed pages cover the Staffy and many other breeds, so it reads as a directory. On a directory the city slot takes only the breed's pages, and none exist, so the slot is empty.

## Trust
This is registry trust, not breeder trust:
- The homepage is built around pedigree registration, and the breed page lists the club's registration rules for the breed. So `kc_registration_mentioned` is true.
- **Health tests named** (breed page): the hereditary cataract DNA test (HC-HSF4), the L-2-HGA DNA test, the BVA/KC elbow dysplasia scheme, and the BVA/KC/ISDS eye scheme. The page sorts them into good-practice and best-practice tiers. It also links lists of tested dogs and sells a DNA test bundle for the breed.
- There is no council licence. The Find a puppy page cites the breeding licensing regulations only in a disclaimer, with no licence number and no named council. So `council_licence_shown` is false. There is no breeding-since claim.
- `vet_checks_mentioned` is false. The breed page tells owners to speak to their vet about health worries. The Find a puppy disclaimer says the club does not vet breeders. Neither describes a vet check of a litter.
- No fetched page gives the club's base as a town. The breed page mentions Birmingham, but only in the breed's history. So `town` is null.
- The homepage measures script (raw HTML, `HOME_URL` given) found no phone and no email. No registered charity number is shown on the homepage.

Reviews: 0. The review list is empty (`grep -c .` gives 0). The homepage shows a magazine best-buy badge for the club's pet insurance. That is a badge with no review words, so it counts 0. The Find a puppy page's quoted line is a club slogan, not a customer review.

## Content
- **Homepage:** 2,592 words by script, and 6 H2s. Most of the words are the mega-menu and the breed drop-down. The page carries club news, a puppy search, promo cards and a short brand statement.
- **Breeder-questions guide** (4 H2s): two question lists, one for the phone call and one for the visit, each with a short reason. It ends by pointing to research on the parents' health.
- **Staffordshire Bull Terrier breed page** (1 H2; 1,432 words by script). It covers:
  - a trait grid (size, exercise, grooming, lifespan and so on);
  - a short history of the breed;
  - the standard and non-standard colours (blue is a standard colour);
  - the health-test tiers;
  - the breeding-for-health framework and the breed watch category;
  - the merle registration bans;
  - links to Find a puppy (with the breed filled in), Find a Club and pet insurance.

  Most sections sit under H3s, so the H2 count is 1.
- **Find a puppy** (0 H2s; 835 words by script): a search form with every breed, location, distance, sex and health-tested filters, a count of matching dogs, and a long disclaimer. No litter cards appear in the fetched content.

None of the fetched pages prints an H1 in its markdown. The map returned 495 URLs, under the 500 cap.

## Keywords
One phrase, by script over all four fetched pages: `staffordshire bull terrier puppy`, from the breed page's health introduction. No name cut was needed. Everywhere else the breed name stands alone, in the breed drop-down and in headings with no intent word next to it.

## Page types
By script over the 534-URL Map list (the first map plus the search map's 39 new URLs), with no `--post-folder`: care-guide 80, listing 53, breed-guide 46, health 42, blog 13, reviews 7, contact 2, price 2, about 1, city 1, faq 1.
- **Care-guide and health:** the dog-training folder and the health-and-care A to Z. The search map added more A to Z pages.
- **Breed-guide:** breed standards, Breeds A to Z and judging pages, now with the Staffy breed page.
- **Listing:** the getting-a-dog puppy pages, the logged-in litter screens, and now Find a puppy.
- **Blog:** dated media-centre news items (see Blog).
- **Reviews:** account "review" steps, not customer reviews.
- **Price:** two fee forms.
- **About:** a registration-statistics page under the about folder. It is not the about page, so the about slot stayed empty.
- **City:** one London horse-show form.

## Blog
- `post_count` 13, `post_folder` null. All 13 are dated media-centre news items: one from the first map and twelve from the search map.
- `posting_frequency` is 0.11 posts a month, by script: 13 dated URLs from August 2016 to February 2026 (115 months). The search map only returns items that mention the breed, so this is a floor, not the site's real rate. The media centre publishes far more than that.
- `topics` and `sampled_word_counts` are NOT FETCHED, because none of the key pages is a post.

## Visual
- From the homepage raw HTML, by script: 39 distinct images. Most alt text is descriptive, and 6 images have no alt.
- There is no video tag and no YouTube or Vimeo embed.

## Schema
The homepage JSON-LD (read by script from the raw HTML) holds Organization (with a logo ImageObject and a PostalAddress), WebSite, and a SearchAction with an EntryPoint. There is no breed, product, FAQ or breadcrumb markup. The breed page was scraped as markdown only, so its schema was not read.

## Cities
- **London:** the homepage names the club's London venues, and the map's one city-typed URL is a London show form.
- **Birmingham:** the breed page names it in the breed's origin story.
- Manchester Terrier appears in the breed lists. That is a breed, not the city, so it is not counted. Towns in news-item URLs (show venues) are not in the city list and were not fetched.

## Conversion
- `cta_types`: form only. The buyer's action on the site is the Find a puppy search form. The breed page sends buyers to it with the breed filled in.
- The enquiry itself happens off the fetched pages. The fetched listing shows no litters, and the breeder-questions guide tells the buyer to phone and visit the breeder.
- No puppy price or deposit is printed. The only amounts are a discounted DNA-test bundle on the breed page and an insurance cover limit on the homepage. Neither is a puppy price, so `prices_shown` is false.
- `steps_to_enquire` is null, because no enquiry form was fetched. The search form finds dogs but does not send an enquiry. There are no urgency signals: a count of matching dogs is not scarcity.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran in this run, in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
- **Map list:**
  - `map_calls` 2 today: the first map (limit 500, 495 URLs, from today's earlier run) and one search map run in this top-up.
  - The search map ran because the first map held no breed URL (`breed_urls` 0). Its term was `staffordshire bull terrier` and its limit 100.
  - It added `search_added` 39 new URLs. `search_breed_urls` is 2: the breed page and a tested-dogs PDF. `search_adverts` is 0.
  - `home_added` is 0, because the homepage links no breed path. `map_list` is 534.
- **Scrapes today: 6.**
  - Four were in the earlier run: the homepage (markdown and raw HTML), the breeder-questions guide, and the two dropped pages.
  - Two were in this top-up: the breed page and Find a puppy, both markdown only.
- **Credits:** 8 Firecrawl credits in all today (2 maps + 6 scrapes). The earlier run spent 5 and this top-up spent 3. That is inside the 8-credit ceiling, so the controller's extra allowance was not needed.
- The phone check and the saved inputs cost no credits.
- The scratch copy of the breed page leaves out two named contacts, which the report never uses.

## Key insight
The Royal Kennel Club ranks on registry authority and does have a Staffordshire Bull Terrier breed page. But that page is a registry profile: traits, colours, recommended health tests and registration rules. It then hands the buyer to a generic all-breed puppy search, whose fetched page shows no litters. BSUK can beat it for the same buyer. One open page can pair that health-test list (HC-HSF4, L-2-HGA, elbow and eye schemes) with its own dogs' results, visible litters and a Staffy-specific buyer checklist.
