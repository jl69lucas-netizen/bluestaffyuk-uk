# RSPCA — competitor intel

- Root domain: rspca.org.uk · tier 3 (animal-welfare charity) · analysed 2026-09-25. This re-run replaces the 2026-09-23 pilot report (Known Issue 51).
- **Topped up in the G1 consistency pass (1 credit).** The saved first map and the saved homepage raw HTML were run again through the final Map list and classifier (commit 9d7e7b9). The first map holds no breed path, so the Map list asked for a search map with the term `staffordshire bull terrier`. It ran, and it found no Staffy page either. Under the final classifier the site counts as a marketplace (the map has sections for other species), and the classifier prints `marketplace: true`. So the price-or-FAQ slot takes only a page that names the breed, a dog or breeding, and the city slot takes only the breed's own pages. Two pages from the first run are no longer picks and have left the report, with everything only they fed:
  - the gifts-in-Wills FAQ (the old price-or-FAQ pick). The head-office town, the one supporter testimonial and the phone and email asks all came from this page;
  - the privacy-notice page whose slug contains "about" (the old about pick, a 404). The about slot now takes only a last segment that is the about word or starts with it.
- Homepage gate: passed. The status was 200, the final URL stayed on rspca.org.uk, and there was no bot check.
- Pages in this report, as the final classifier picks them:
  1. the homepage, with markdown and raw HTML (scraped earlier today, reused);
  2. the buying-a-puppy guide (listing slot: a `puppy` path; reused);
  3. the dog-training guide (guide slot: a generic dog guide, allowed on a multi-species site; reused).

  The price-or-FAQ, city and about slots have no page, so none was scraped.
- **Was the Staffy advice page found this time? No.** The registry says RSPCA ranks with a buying-a-Staffy advice page. Neither the first map (471 URLs, `breed_urls` 0) nor the search map (`search_breed_urls` 0) returned a URL with the breed in its path. The search map did return two other breeds' buying pages in the dog puppy guide's breeds folder (cocker spaniel and German shepherd). The map's description of the site-map page also lists a Staffy entry. So the Staffy page very likely sits in that folder, but no fetch returned its URL, and a breed page is never added by eye. It stays unfetched.

## Trust
This is charity trust, not breeder trust. The homepage footer shows a registered charity number (recorded as a yes, `registered_charity_number_shown`). The homepage also has a "where your money goes" breakdown and a Fundraising Regulator badge. None of the fetched pages mentions the Kennel Club, a named DNA test or a vet check. The puppy guide mentions insuring for vets' fees, which is not a vet check. No licence number or council is shown, so `council_licence_shown` is false. Town: null, because none of the three pages gives a base town. The head-office town came from the Wills FAQ, which has left the report. The homepage measures script found no phone and no email on the homepage. Reviews: 0. No customer, adopter or supporter review text appears on the three fetched pages. The review list is empty, and `grep -c .` gives 0.

## Content
Homepage: 1,396 words, counted by script (`scratchpad/rspca/words.py`: images dropped, link and heading markup stripped). The earlier report gave 1,378. The homepage file is the same; only the counting script changed. There are 15 H2s. Much of the page is the navigation menu, printed twice, and six of the H2s are a footer printed twice. The buying guide (7 H2s) is a short hub. It urges adoption over buying, and points to a pet cost calculator, advice on spotting bad adverts and finding a good breeder, the Puppy Contract and pet insurance. The training guide (5 H2s) covers why and how dogs learn, with some basic tips. `url_count` is 471: the first map, under the 500 cap. It is still only a sample of a much larger site.

## Keywords
None. The run rule, run by script on the three fetched pages, found no qualifying phrase. No page names the breed.

## Page types
By script over the Map list: 524 URLs (the first map's 471, plus 53 new from the search map). No `--post-folder` was used.
- Counts: care-guide 19, health 13, contact 10, listing 6, about 4, blog 3, city 3, breed-guide 2, faq 2.
- The search map added these types: the cocker spaniel and German shepherd breed pages (breed-guide 2), three branch pages (city 3), a pet-insurance FAQ, a branch contact page, a lead-walking training page, and a report PDF typed listing, because its path ends in a long numeric id (the table's advert shape).
- There is still no price type. `costofliving` is one word, so the pet cost calculator is not a price page.
- The pet-insurance FAQ names no dog, so on this marketplace it cannot be the price-or-FAQ pick.

## Blog
0 posts by the classifier. The three blog-typed URLs are the latest-news index, the blogs index and one post whose slug starts with "blog-". That post sits in a root `/-/` folder alongside privacy-notice pages, so no posts-only folder can be named with `--post-folder`. The map has no post sitemap. Posts without a blog base or a date are missed, and the table counted them as it found them. Topics, sampled word counts and posting frequency are NOT FETCHED: no post was among the key pages, and the Map list holds no dated post URL.

## Visual
The homepage measures script (raw HTML, `HOME_URL` https://www.rspca.org.uk/) found 19 distinct images. 13 have no alt or an empty alt, so the most common alt class is missing. There is one `<video>` tag in the raw HTML, in the conformation-campaign block.

## Schema
None. The homepage raw HTML holds no JSON-LD. A JSON-LD read in the emulated phone during this top-up also returned an empty list.

## Cities
Cornwall, Coventry and Wolverhampton. Each has an RSPCA branch page in the Map list, all three from the search map:
- the Coventry branch's find-a-pet page;
- the Stafford, Wolverhampton and District branch's contact page;
- one rescue dog's profile under the Cornwall branch, on a media subdomain.

No `data/locations.json` city is named on the three fetched pages. A press-release URL names Stafford, the town, which is not one of the cities.

## Conversion
The pages fetched never ask a buyer to buy. The puppy guide steers readers towards adopting through the charity and away from online adverts, and tells anyone buying to see the mother with her pups. The only direct ask is to donors: the homepage has a donation form with preset monthly and one-off amounts (`form`). The phone and email asks came from the Wills FAQ, which has left the report. The donation form is not an enquiry form for an animal, so steps to enquire is null. The only amounts printed are donation and raffle figures. No animal is priced, so `prices_shown` is false and no amounts are recorded. There are no deposit terms and no urgency signals.

## Technical
The check ran in Chrome DevTools, re-run in this top-up: an emulated phone (375 × 812 viewport, mobile user agent, touch), the homepage loaded, then the mobile-check evaluate. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true, so `mobile_layout_ok` is true. Lighthouse: NOT FETCHED (no Lighthouse run).

## Fetch
- **Map list:** re-run in this top-up on today's saved first map and homepage raw HTML.
  - First map: `url_count` 471, `breed_urls` 0.
  - `search_map` true, because the first map holds no breed URL (it is under the cap). `search_term` is `staffordshire bull terrier`, the default: the homepage does not name the breed only as staffy, staffie or staffies.
  - The search map (limit 100) returned 75 URLs, all on rspca.org.uk or its subdomains. It added 53 new ones (`search_added` 53).
  - `search_breed_urls` 0: the search map found no breed page, and no further map was run.
  - `search_adverts` 11. All 11 are document-library files (report and leaflet PDFs whose paths carry long numeric ids), not sale adverts.
  - `home_added` 0. `map_list` 524. `map_calls` 2.
- **Scrapes today:** 5, all in the first run: the homepage (markdown and raw HTML) and four key pages. Two of those four, the Wills FAQ and the 404 privacy page, are no longer picks. This top-up scraped nothing, because the final picks are pages already fetched today. The homepage raw HTML was saved, so it was not re-scraped.
- **Credits:** 7 Firecrawl credits today (2 maps and 5 scrapes). The first run spent 6 (1 map and 5 scrapes), and this top-up spent 1 (the search map). That is within the per-entry ceiling of 8. Of the controller's extra allowance for this entry (+1 map, +3 scrapes), only the map was used.

## Key insight
RSPCA still shows no Staffy page to pick. Neither its map nor a search map for the breed's name returned one, though the search map did return other breeds' buying guides in the same puppy folder. Its fetched pages speak to any dog, carry no schema and price no animal, so its Staffy buying and price rankings rest on the charity's authority. BSUK can meet those searches with a Staffy-specific buying and price guide that walks through the welfare checks RSPCA tells every buyer to make.
