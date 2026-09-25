# Forever Puppy — competitor intel

- Root domain: foreverpuppy.co.uk · tier 2 (a UK dog-only advert board where private sellers and breeders of every breed post puppies for sale, stud, wanted and rehome adverts) · analysed 2026-09-25. This is the first report for this entry.
- Homepage gate: passed. The status was 200, the final URL stayed on foreverpuppy.co.uk, and the page was the live homepage, not a bot check or a parked page.
- Key pages, as the classifier picked them from the Map list (it flags the site as a `marketplace`: its all-breed "near <place>" pages sit where the breed's name sits in the Staffy "near" pages):
  - listing slot: the site's Staffordshire Bull Terrier hub (`/find-your-dog/staffordshire-bull-terrier`);
  - price-or-FAQ slot: none. No URL in the Map list has a price or FAQ word in its path (the FAQs live on a help subdomain that is not in the list);
  - guide slot: none. The only guide-folder URL in the Map list is a post, typed `blog` once its folder was named;
  - city slot: the Staffy "near Bristol" page;
  - about slot: none. The homepage footer links an about page, but it is not in the Map list, and only breed links join the list from the homepage.
- Breed check before scraping: both picks name the breed (`staffordshire-bull-terrier`) in their paths, so no slot was skipped.
- The first map is saved at `maps/foreverpuppy.json` (500 URLs), the search map at `maps/foreverpuppy.search.json` (73 URLs) and the homepage raw HTML at `maps/foreverpuppy.home.html`.

## Trust
Nothing on the fetched pages builds trust in a seller or a dog.
- No council licence, no Kennel Club mention, no named health test, no vet check and no breeding-since claim. The advert cards carry seller-ticked tags (microchipped, vaccinations up to date), which are not vet checks.
- `town`: null. The site is a national board with no base town.
- The homepage measures script found no phone and no email in the homepage raw HTML (`contact_source` raw-html). The footer links a contact page, which was not fetched.
- `reviews_shown`: 0. No customer review or testimonial text is on the pages fetched; the only trust badges are a card-payment and a data-protection logo.

## Content
- Homepage: 949 words (by script) under 4 H2s. It is a breed search box listing every breed the board carries, eight featured adverts from other breeds, a popular-breeds link list, four guide teasers and a footer.
- The two key pages have 5 H2s each: a featured advert, the full advert list, guide teasers, an app promotion and a sign-in box.
- `url_count`: NOT FETCHED (map truncated at 500). The first map returned exactly 500 URLs, every one an all-breed "near <place>" search page.

## Keywords
5 phrases by the run rule (script over the homepage and both key pages; no business name needed cutting): blue staffy, puppy staffordshire bull terrier, staffordshire bull terrier puppies, staffordshire bull terrier puppy, staffy pup for sale. They all come from sellers' and buyers' advert titles, not from any copy the site wrote about the breed.

## Page types
By script over the Map list (546 URLs; the post folder named, below): listing 18, city 16, health 1, blog 1.
- Listing: the Staffy hub plus Staffy for-sale and wanted adverts from the search map, and one English Bull Terrier advert.
- City: London borough and City of London search pages, a Newcastle-under-Lyme district page, the Staffy pages for Bristol, Greater Manchester and South Yorkshire, and Staffy adverts filed under Essex, South Yorkshire and Cardiff.
- Health: one Staffy advert whose title mentions a DNA test.
- The remaining 510 URLs are all-breed "near <place>" pages whose place is not a `data/locations.json` city, so the table leaves them untyped.

## Blog
- `post_folder`: `guides-resources-and-news` — the site's guides folder, named with `--post-folder` because the blog row cannot see it.
- `post_count`: 1. Only one post (a dog-hobbies article) is in the Map list. The homepage links ten other guides in that folder, but homepage links join the list only when they are breed paths, so those posts are missed here, not absent from the site.
- `topics`, `posting_frequency` and `sampled_word_counts`: NOT FETCHED. No post was a key page and the post URLs carry no dates.

## Visual
9 distinct images on the homepage (script): the alts are mostly descriptive, with 1 missing. The advert photos on the cards are not `<img>` tags in the raw HTML. No video tag or YouTube/Vimeo embed.

## Schema
Organization — the homepage's only JSON-LD block, read from the raw HTML.

## Cities
6 `data/locations.json` places are named on the fetched pages or have a page in the Map list: Bristol, Cardiff, Essex, London, Newcastle-under-Lyme and South Yorkshire.
- Essex is named on a homepage advert card and has two Staffy adverts filed under it.
- London has City of London and seven London borough search pages; Newcastle-under-Lyme has a district page.
- Bristol and South Yorkshire have Staffy "near" pages; Cardiff has a Staffy wanted advert.
- Greater Manchester and Greater London appear only as county labels on cards and in one page slug, so Manchester was not taken as a city from them.
- The Bristol page is not local: it returned exactly the same national list as the Staffy hub, and no advert on it is in Bristol.

## Conversion
- `cta_types`: none recorded. The pages ask buyers to open an advert or log in; the message tool sits on advert pages behind a login, and none was fetched, so no phone, email, form or message box was seen.
- `prices_shown`: true. `price_amounts_as_printed`: £300 to £2,750, from sale adverts and from wanted posts' budgets.
- `deposit_terms`: null. The homepage's secure-checkout badge is for sellers buying adverts, not puppy deposits.
- `steps_to_enquire`: null. No enquiry form or message box was on the pages fetched (the homepage forms are a breed search and a newsletter sign-up).
- `urgency_signals`: ready-date (every card states when the puppy can leave) and few-left (card titles saying only a few puppies remain).

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
Fetch: `map_calls` 2 · search map ran: yes · term `staffordshire bull terrier` · `search_added` 46 · `search_breed_urls` 37 · `search_adverts` 22 · `home_added` 0 · `map_list` 546 · scrapes 3 · credits 5 of a ceiling of 8.
- The first map held 500 URLs (`url_count`), at the cap, and 0 breed URLs (`breed_urls`). The Map list script therefore asked for a search map (`search_map` true, `search_term` "staffordshire bull terrier"), and one ran with a limit of 100.
- The search map returned 73 URLs; 27 were already in the first map, which left 46 new URLs (`search_added`).
- Of those, 37 are breed pages on the site (`search_breed_urls`): the Staffy hub, Staffy "near" pages and Staffy adverts.
- 22 of the search map's URLs are adverts by the key-page test (`search_adverts`): the site's adverts start their slug with an all-digit id followed by an underscore, and the final key-page test reads that as an advert. This count comes from the G1 consistency pass (0 credits), which re-ran the saved maps through the final classifier (commit 9d7e7b9); the first run's test missed these ids and printed 0. The page types, the post count and the key pages are unchanged, and the page-type table still types these adverts as listings (or, by a place word, as city pages).
- The homepage links no breed page, so `home_added` is 0.
- Scrapes: 3, all live (not from cache).
  - the homepage, as markdown and raw HTML;
  - the Staffy hub, as markdown;
  - the Staffy "near Bristol" page, as markdown.
  The price-or-FAQ, guide and about slots were empty.
- Credits spent: 5 (2 maps + 3 scrapes at 1 credit each).

## Key insight
Forever Puppy ranks for Staffy searches with an all-breed advert board. Its Staffy hub and "near Bristol" page show the same national list of sellers' adverts and wanted posts, with no breed text, no health or licence proof and no local content. BSUK can beat it with real city pages and one breeder's visible proof: named health tests, a council licence, a printed price and a direct way to enquire.
