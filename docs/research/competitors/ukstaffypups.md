# UKStaffyPups — competitor intel

- Root domain: ukstaffypups.uk · tier 1 (breeder) · analysed 2026-09-25 (first report)
- Homepage gate: passed (status 200; final URL stays on ukstaffypups.uk)
- Fetched: 2 maps (the first returned 1 URL; the search map was asked for by the Map list script) + 2 scrapes — homepage (markdown + raw HTML) and the listing key page (`/staffy-puppies-for-sale/`). The classifier's price-or-FAQ, guide, city and about slots were empty, so nothing else was scraped. JSON-LD read from the homepage raw HTML. Mobile check: Chrome DevTools phone emulation (375 × 812, mobile user agent, touch). 4 Firecrawl credits.

## Trust
No licence claim of any kind on the pages fetched: no licence number, no council, and not even a bare "licensed" line (the homepage raw HTML and the listing page were both checked by script for licence and council wording; none found). So `council_licence_shown` is false and `council` null. Kennel Club registration is mentioned throughout, and vet checks, microchipping and first vaccinations are promised. The listing page's buyer guide names L-2-HGA and HC-HSF4 DNA tests, a PHPV eye examination and hip scoring — but as tests a buyer should ask any breeder for, not as results shown for this kennel's own dogs; no certificate is shown. No breeding-since claim. No town: the site says only that it is based in the UK and gives its location after a vetting step. Phone and email: neither shown (homepage measures script, raw HTML). Reviews: 3 — three short testimonials with their words on the homepage (listed once each and counted by script); each carries a star row, a first name and surname and a city, but no source or date, and the full testimonials page is linked but was not fetched.

## Content
Homepage: 771 words (by script) under an H1 and 4 H2s — a near-me intro, a trust strip (health checks, KC lines, raised at home), the testimonials and a four-question FAQ. The listing page has no H1 in the fetched content and 14 H2s: a litter block, then a long buyer guide on the blue coat (genetics and colour dilution alopecia), temperament, training, neutering, exercise, health screening, diet, grooming, the law and home preparation, with an ownership cost table. The first map returned only 1 URL (`url_count` 1): the site's menu pages (about, meet the parents, health guarantee, testimonials, contact) are not in Firecrawl's index.

## Keywords
16 phrases by the run rule (script over every sentence, heading, list item and link of both pages), re-run with the site name cut ("UK Staffy Pups"). Core buying terms are covered: staffordshire bull terrier puppies for sale, blue staffy puppies for sale, kc registered staffordshire bull terrier puppies, staffordshire bull terrier breeder, staffy puppies. Both pages lean hard on "near me" wording, but no city is joined to a breed phrase.

## Page types
By script over the Map list (3 URLs: the first map's one URL, the homepage from the search map, the listing page from the homepage's own breed link): listing 1. The homepage and the uncategorised category archive are untyped. The about, parents, health-guarantee, testimonials and contact pages the menu links are not in the map, so they are not counted.

## Blog
0 posts: the map and search map list no post, only an empty-looking "uncategorized" category archive (a WordPress default). No `--post-folder`. Topics, posting frequency and sampled word counts are NOT FETCHED — there is no post to read. The listing page's long guide is the site's only editorial content.

## Visual
1 distinct image on the homepage (script), with descriptive alt text; the trust strip uses emoji, not images. No video tag or YouTube/Vimeo embed in the raw HTML. The listing page shows eleven puppy photos with descriptive alts (markdown only, not a homepage measure).

## Schema
Organization, WebSite, SearchAction, ImageObject, WebPage, Person, Article — the standard WordPress SEO-plugin graph, read from the homepage's JSON-LD. No LocalBusiness, Product, Offer, FAQPage or Review markup, though the homepage has an FAQ and the listing has priced puppies.

## Cities
Birmingham, London and Manchester — named only as the home towns of the three homepage testimonials. No city pages and no city in any breed phrase.

## Conversion
Every puppy card and call to action sends the buyer to the contact page, which was not a key page, so its method is unknown and no form was fetched (`steps_to_enquire` null); no phone number, email, WhatsApp or form is on the pages fetched. The homepage invites families to visit the puppy once it is a few weeks old, after vetting (`visit`). Price: a flat £1,000 per puppy is printed on the listing page for every pup; the cost table there also gives a typical purchase range and running costs, which are guidance, not this seller's prices. Deposit: a holding deposit secures a chosen puppy after a short vetting step, with no amount or refund terms. Urgency: the listing says the current litter is ready to leave now (`ready-date`), and the homepage FAQ offers a waiting list for upcoming litters (`waiting-list`). Eleven puppies are shown as ready to leave, all at the same age and price.

## Technical
Emulated phone evaluate: innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1, mobileUA true → `mobile_layout_ok` true. Lighthouse: NOT FETCHED — no Lighthouse run.

## Fetch
`map_calls` 2. The first map returned 1 URL (`url_count` 1, `breed_urls` 0), so the Map list script asked for the search map (no breed URL) with the term "staffordshire bull terrier" (limit 100). The search map returned 2 URLs, added 1 (the homepage; `search_added` 1), found no breed page on the site (`search_breed_urls` 0) and no adverts (`search_adverts` 0). The homepage's own breed links added 1 (`home_added` 1: the listing page), for a Map list of 3. Scrapes: 2 (homepage with raw HTML, listing). Credits: 4 (2 maps + 2 scrapes).

## Key insight
UKStaffyPups ranks on a thin site: one listing page with a flat printed price, a ready-now litter and a long blue-Staffy buyer guide, but no licence, no named town, no phone or email and three unsourced testimonials. BSUK can beat it on shown proof (licence and council, test certificates, real reviews) and on depth of indexable pages, city pages included.
