# BlueStaffyUK (own build) — intel profile

- Source: `dist/` from `npm run build` on 2026-09-23 (branch competitor-intel). Domain: SITE_URL_PLACEHOLDER until project 6. No Firecrawl, no homepage gate, no registry write.
- Pages: the 31 indexable URLs in the four sitemaps (post 1, location 11, puppy 6, page 13); noindex stubs are out. Playwright: the 375px check against `npm run preview`.

## Trust
Kennel Club registration and DNA tests (L-2-HGA, HC-HSF4) on both parents are stated on the homepage and FAQ, with vet checks and a written health guarantee for every puppy. The base town printed on the puppy cards is Carlisle. Three pages call the business council-licensed, but no page prints a licence number or the council, so `council_licence_shown` is false — Trojanstaff prints its number on the homepage. No phone number or tel: link; an email address is linked. Three reviews are shown as text rows, each naming the family's town.

## Content
Homepage visible text: 5,611 words by script (counted from the built HTML, not from a markdown scrape, so it includes navigation and is not strictly comparable to the competitors' figures). 31 indexable URLs. H2 counts per page are in the JSON.

## Keywords
170 phrases: BSUK's own runs by the rule (178, less nine runs that sit on the brand name and were cut) plus the 15 competitor phrases the phrase script found in `dist/`. BSUK holds all five phrases two of the three competitors share (blue staffy, staffy puppies, staffy puppies for sale, staffordshire bull terrier puppies, … for sale), plus one breed-plus-city phrase per location page.

## Page types
By sitemap first, then the classifier over the location and page sitemaps: listing 12 (6 puppy pages + 6 pages, the UK location hub among them), city 9 (the location sitemap without the UK hub and the Glasgow breeding-dogs page, which stays untyped), blog 2 (1 post + the guides hub), breed-guide 2, about 1, contact 1, health 1. No care-guide, faq, price or reviews page type. Re-derived from `dist/` after the whole-word table and the location-row rule (Known Issue 51); no fetch.

## Blog
One post in the post sitemap; its main content is 162 words (choosing the right blue Staffy puppy for a family). Posting frequency: NOT FETCHED — one post, one date.

## Visual
21 homepage images, one without alt text; alts are descriptive (puppy names and colours). A video is embedded on the homepage.

## Schema
23 types across the build, including LocalBusiness, Product/Offer/AggregateOffer, FAQPage, BlogPosting, BreadcrumbList, VideoObject, AboutPage and ContactPage. Only Person — on Trojanstaff — is a competitor type BSUK lacks.

## Cities
25 of the `data/locations.json` cities are named or have a page: all 19 cities the competitors show, plus Cornwall, Inverness, Middlesbrough, Newcastle-under-Lyme, South Yorkshire and Wolverhampton.

## Conversion
One enquiry form (on the contact page) and a linked email; the buying steps also offer a call and a visit to meet the litter before paying. Each puppy card prints its price by sex, and the homepage explains a refundable deposit that holds one named puppy and comes off the price, free collection and distance-priced delivery. The contact form offers a waiting-list choice for the next litter; the homepage says none of its listings is a place in the queue for an unborn litter. No countdowns or "few left" claims.

## Technical
At 375px the preview homepage fits the screen (scroll width 375): `mobile_layout_ok` true. Lighthouse: NOT FETCHED — no Lighthouse run in this pilot.

## Key insight
BSUK already holds every phrase two of the three competitors share, every city and schema type they show, per-puppy prices and a mobile-safe homepage. Its gaps are care-guide pages (2 of 3 competitors have them), colour and KC-registered phrase variants, the staffy price question, a printed council licence number, and a blog of one thin post.
