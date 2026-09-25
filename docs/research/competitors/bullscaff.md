# Bullscaff — competitor intel

- Root domain: bullscaff.co.uk · tier 1 · analysed 2026-09-25 (first report for this entry)
- Homepage gate: passed (status 200; final URL stays on bullscaff.co.uk; a real page, not a bot check or parked page)
- Fetched: 1 map (39 URLs) + 3 scrapes. The scrapes were the homepage (markdown and raw HTML), the listing key page (`/stud-dogs/staffy`) and the about key page (`/about-our-blue-staffy-stud-dogs`). Both key pages name the breed in the path (`staffy`), so both passed the breed-or-dog check before they were scraped. The classifier's price-or-FAQ, guide and city slots were empty (`null`), so nothing else was scraped. JSON-LD was read from the homepage raw HTML and checked again in the emulated phone. The mobile check used Chrome DevTools phone emulation (375 × 812, mobile user agent, touch). 4 Firecrawl credits (1 map + 3 scrapes).

## Trust
The site says it is a 4-star licensed breeder, the top rating open to a new licence holder. That is a bare claim: it prints no licence number and names no council. Under the controller's ruling (true only when a licence number or a named council is shown), `council_licence_shown` is false, and `council` is null. Every page fetched says the stud dogs are Kennel Club registered and health tested clear of L2HGA, HC and HSF4. Vaccination, worming and flea care are mentioned, and so is work with fertility and veterinary clinics, but no page says a dog or puppy is vet checked (`vet_checks_mentioned` false). The site claims over 20 years with the breed. Its base is given as Shrewsbury in Shropshire. The homepage measures script (raw HTML) found both a phone number and an email shown. Reviews: 3. The stud page shows three written client reviews, each praising the owner's support through a litter. The homepage and about page only claim to be the most reviewed stud owner and show no review text. The homepage also has a form for sending in a testimonial, which is not a review.

## Content
The homepage has 983 words (counted by script) under 6 H2s. Two of those H2s belong to the contact pop-up. The rest cover a welcome, the 4-star licence, services and an about block. The page is about stud services: mating terms, fertility work, semen shipping in the UK and abroad, and a free second sample. The stud page (13 H2s) profiles three stud dogs with their titles, looks, temperament and pedigree. It then sets out how the stud service works, what help breeders get, reviews and a five-question FAQ. The about page (5 H2s) covers the owners' background, how many litters their studs have sired, their social media reach and their lifelong support. The map returned 39 URLs (`url_count`), several of them the same page written two ways.

## Keywords
The run rule found 5 phrases (script over every sentence, heading, list item and menu link of the three pages): blue staffy, blue staffies, blue and black staffy, blue or black staffy, and staffy stud owner in the uk. No phrase held a business or person's name, so the script was not re-run with a cut. Nothing on these pages targets buyers: no "puppies for sale", no "breeder" phrase and no city phrase.

## Page types
Counted by script over the Map list: blog 10 (8 posts under `/news/`, the blog index and a month archive), about 2, health 1 (DNA testing), listing 1 (the `/stud-dogs/staffy` hub) and reviews 1. There are no price, FAQ, guide, contact-typed or city pages. Most stud-dog profile pages have a bare dog-name slug that the table cannot type. The waiting-list page is not typed either, because `waiting-list` is not a listing word.

## Blog
8 posts by the classifier, all under the `/news/` folder that the blog row reads, so no `--post-folder` was needed (`post_folder` null). No post was among the key pages, so topics, sampled word counts and posting frequency are NOT FETCHED. The post URLs carry no dates, and the one dated path is a month archive, not a post. The post slugs point to breeding and owner topics (genetic testing, planning a litter, the blue-to-blue debate, raw feeding, grooming, socialising, play), but that is a reading of URLs, not of fetched posts.

## Visual
The homepage has 14 distinct images (script). 5 have no alt text, and most of the rest are descriptive. No video tag and no YouTube or Vimeo embed is in the raw HTML.

## Schema
None. The homepage raw HTML holds no JSON-LD block, and the rendered page in the emulated phone returned none either (`schema_types` ok, empty).

## Cities
None. No page fetched names a city from `data/locations.json`, and the map has no city page. The only place named is the site's own base, Shrewsbury, which is not a BSUK location.

## Conversion
Buyers and breeders are asked to phone (a call-now button and a printed number), email, or fill in a form. The forms are the site's own one-page contact form (`steps_to_enquire` 1), a call-back request and an embedded Typeform stud enquiry. The Typeform's steps were not fetched, so they are not counted. A mailing-list sign-up is not an enquiry. There are social links but no request to message there, and no WhatsApp link. Printed prices: a £200 chilled-semen shipping fee on the homepage, a £600 stud fee on the stud page, and £2000–£3500 given as the price the stud's puppies sell for. No deposit terms. Urgency: `waiting-list`. The menu links to a puppy waiting list, and the stud page offers to place breeders' puppies through it.

## Technical
The emulated phone evaluate returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true, so `mobile_layout_ok` is true. Lighthouse: NOT FETCHED (no Lighthouse run).

## Fetch
Fetch: `map_calls` 1 · search map ran: no · term: none · `search_added` 0 · `search_breed_urls` 0 · `search_adverts` n/a (no `--search`) · `home_added` 1 · `map_list` 39 · scrapes 3 · credits 4 of a ceiling of 8.
- The first map (limit 500) returned 39 URLs (`url_count`), well under the cap, and 8 of them are breed URLs (`breed_urls`). So the Map list script did not ask for a search map (`search_map` false, `search_term` null), and none ran.
- The homepage's own breed links added 1 URL (`home_added`), the AI and semen-shipment page. The map lists the homepage twice (with and without the trailing slash), which counts as one page, so `map_list` is 39.
- Scrapes: the homepage (markdown and raw HTML), `/stud-dogs/staffy` and `/about-our-blue-staffy-stud-dogs` (markdown). Credits: 1 map + 3 scrapes = 4.

## Key insight
Bullscaff ranks first for "blue staffy breeder" as a stud-dog service, not a puppy seller. It wins on proof: champion studs, named health tests, Kennel Club registration, a 4-star licence claim and three written reviews. It has no puppy listings, no city pages, no structured data and only eight undated posts. BSUK can win the buyer searches with real puppy and city pages that carry the same kind of proof.
