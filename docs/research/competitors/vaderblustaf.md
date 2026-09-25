# VaderBluStaf — competitor intel

- Root domain: vaderblustaf.com · tier 1 (a family breeder of Staffordshire Bull Terriers, blue and black) · analysed 2026-09-25. This is the entry's first report. It used the fetch and classifier steps as updated today (commits up to 8a1de4b): the Map list step with its optional search map, `--home` for the classifier, breed-first key pages, the keyword script from the agent file, and this Fetch line.
- Homepage gate: passed. Status 200, and the final URL (`www.vaderblustaf.com/`) stays on vaderblustaf.com.
- Fetched: 1 map (35 URLs), then 2 scrapes. The homepage came as markdown and raw HTML, and the about key page (`/about-us`) as markdown. The JSON-LD was read from the homepage raw HTML. The mobile check ran in Chrome DevTools phone emulation (375 × 812, mobile user agent, touch). 3 Firecrawl credits.
- Breed check before the key-page scrape: the about path does not name the breed, and the about slot skips the breed step. The homepage's own "About Us" block links to `/about-us` and is about breeding Staffordshire Bull Terriers, so the page was scraped. It turned out to be about the breed.
- **Classifier note for the controller:** the listing slot came back `null`, so `/litters` was not scraped. The cause is one blog post, `/news/blog-ped-7champ/82stafxuk-vbs3l`. Its last segment starts with a digit followed by a letter, so the key-page advert test reads `82stafxuk-` as a short advert id. The slug does not name the breed or a dog, so the classifier treats the site as a general classifieds site. On such a site a listing must name the breed or a dog, and `/litters` names neither. This is a false positive on a breeder's blog slug. The pick follows the script as written. A rule fix is the controller's call.

## Trust
- **Licence:** a licence reference is shown. The homepage footer gives a licence reference next to the breeder name. The about page says the kennel got a breeding licence in 2018 under the new rules. Both pages call the pair "fully licensed breeders", inspected by a vet and the local authority. No council is named, so `council` is null. `council_licence_shown` is true only because a reference is printed; the bare claim alone would not count.
- **Health and registration:** Kennel Club registration is mentioned. For all breeding dogs, the about page names clear results for L2-HGA and HC-HSF4, and clear PHPV eye screening.
- **Vet checks:** mentioned, as the vet inspection above.
- **History and base:** established in 2009, and five generations in. The footer gives the base as Bedlington.
- **Contact signals** (homepage measures script, raw HTML): phone shown, email shown.
- **Reviews:** 10. The homepage carries a testimonial widget with ten distinct written reviews from buyers and fellow breeders. They were listed once each in a scratch file and counted by script. One review appears a second time as a pull quote; it is counted once. The JSON-LD also carries a rating block.

## Content
- **Homepage:** 1,228 words by script, and 4 H2s: about, testimonials, a pull-quote review and contact. Most of the words are the ten reviews. The rest is a short about block, teasers for the stud dog, rehoming and news, then a contact form.
- **About page:** 1 H2. It gives the kennel's history, its facilities and its health results.
- **Site size:** the map returned 35 URLs. Several are leftover template pages (placeholder "education" and "donate" pages, `home-copy`, `home-2`) and test pages (`litters-test`, `stud-services-test`).

## Keywords
The keyword script found 3 phrases over the two pages: `blue staffy`, `sbt breeders` and `staffordshire bull terrier breeders`. No run needed cutting at a name. There are no puppies-for-sale, price, KC-registered or city phrases. The homepage has no H1, and its title is just the kennel name.

## Page types
The classifier over the Map list typed: blog 16 (13 posts and 3 index or folder pages under `/news/`), health 2 (the two `-test` template pages, typed by the word "test"), about 1 and listing 1 (`/litters`). There are no price, FAQ, guide, contact, reviews or city pages. The stud, rehoming, waiting-list and evolution pages have slugs the table cannot type. `marketplace` is false.

## Blog
- **Posts:** 13 by the classifier, all under `/news/`, so no `--post-folder` was needed.
- **Not fetched:** no post was a key page, so topics and sampled word counts are NOT FETCHED. Posting frequency is NOT FETCHED too. A few post URLs carry a year (2024, 2025) but never a month, and no post was fetched.
- **From the slugs only (not a fetched reading):** the posts cover champion sires and stud news, pedigrees, blue-to-blue breeding, inbreeding coefficients, raw feeding, progesterone testing, licensed ethical breeding and the kennel's own story.

## Visual
- **Images:** 14 distinct images on the homepage (script). Four have no alt text. The alts are mostly descriptive, because the reviewer avatars carry the reviewers' names as alt text.
- **Video:** no video tag and no YouTube or Vimeo embed in the raw HTML.

## Schema
From the homepage's four JSON-LD blocks: WebSite, Organization and LocalBusiness, plus a Product block with Brand, AggregateRating, Review, Person and Rating.

## Cities
None. The pages name no `data/locations.json` city. The base town is not on the list, and a county is never turned into a city.

## Conversion
- **CTA types:** phone, email and form.
  - The homepage prints both contact routes.
  - It ends with the site's own one-page contact form, with an enquiry-type picker (litter, stud, rehoming, newsletter, other), so `steps_to_enquire` is 1.
  - The Instagram and Facebook links do not ask buyers to message there. There is no WhatsApp link.
- **Prices:** none printed on either page, so there are no prices and no deposit terms.
- **Urgency:** `waiting-list`. The main menu links to a waiting-list page. No few-left, ready-date, deadline or sold badges were found.

## Technical
Emulated phone evaluate: innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1, mobileUA true → `mobile_layout_ok` true. This is a Squarespace site with a device-width layout. Lighthouse: NOT FETCHED (no Lighthouse run).

## Fetch
Fetch: `map_calls` 1 · search map ran: no · term none · `search_added` 0 · `search_breed_urls` 0 · `search_adverts` not printed (no search map) · `home_added` 0 · `map_list` 35 · scrapes 2 · credits 3 of a ceiling of 8.
- **No search map:** the first map held 35 URLs (`url_count` below the cap) and 2 breed URLs (`breed_urls`: the blue-to-blue and inbreeding posts). The Map list script therefore did not ask for a search map (`search_map` false, `search_term` null).
- **Homepage breed links:** the homepage links no breed page, so `home_added` is 0.
- **Scrapes:** 2.
  - The homepage, as markdown and raw HTML.
  - The about page (`/about-us`), as markdown.
  - The listing, price-or-FAQ, guide and city slots were `null` (the listing because of the classifier note above), so nothing else was scraped.
- **Credits spent:** 3 (1 map and 2 scrapes, at 1 credit each).
- **Saved files:** the first map is saved at `maps/vaderblustaf.json`, and the homepage raw HTML at `maps/vaderblustaf.home.html`.

## Key insight
VaderBluStaf sells on long standing and proof. It shows a licence reference, named DNA clears, Kennel Club registration and ten written reviews. Its site is a thin Squarespace build with no H1, no puppy prices, no guides and no city pages, and it hardly uses buying keywords. BSUK can match the proof and win the "for sale", price and city searches this kennel never targets.
