# Pets4Homes — competitor intel

- Root domain: pets4homes.co.uk · tier 2 (classifieds marketplace) · analysed 2026-09-23
- Homepage gate: passed (status 200; final URL stays on pets4homes.co.uk)
- Fetched: 1 map (491 URLs) + 5 scrapes — homepage (markdown + raw HTML), the national Staffordshire Bull Terrier listing, the Manchester Staffordshire Bull Terrier listing, one help-centre buying-advice article, one pet-advice post. Playwright: the 375px homepage check. One scrape of the six was left unused.

## Trust
As a marketplace it shows platform trust, not breeder trust: ID-verified buyers and sellers, an in-house payment service and a trust-and-safety team are the homepage's first section. On the listing pages individual adverts carry "ID Verified" and, on a few, "Licensed Breeder" badges and seller star ratings, but the platform prints no council licence of its own. Adverts mention Kennel Club registration, DNA tests (L2-HGA, HC-HSF4) and vet checks; these are sellers' claims. No phone or email is printed on the homepage, and it names no home town.

## Content
Homepage: 1,285 words by script, 12 H2s — almost all link hubs (breeds, cities, article categories) rather than prose. The map returned 491 URLs; that is a sample of a far larger site, not its size, so the count understates it. The breed listing pages carry one short breed blurb, a live count ("137 puppies found"), the adverts, a five-question FAQ (only the price answer is shown) and a block of long-tail links.

## Keywords
35 phrases by the run rule, nearly all from the listing pages: the generic buying terms (staffordshire bull terrier puppies for sale, staffy puppies for sale), colour terms (blue staffy, blue staffordshire bull terrier puppies, blue and black staffy puppies), KC terms (kc registered staffordshire bull terrier puppies), the price question (price of a staffy puppy) and a run of breed-plus-town links (staffordshire bull terrier in leeds / bristol / coventry / nottingham / glasgow / essex). One colour tag built on a bloodline name was cut.

## Page types
By script over the 491-URL map: listing 290, blog 42, city 29, breed-guide 6, health 5. The 42 "blog" URLs are almost all help-centre articles (the word "articles" is in their path); only 3 pet-advice posts appear in the sample. Most listing URLs are individual adverts.

## Blog
3 pet-advice posts in the map sample (script count of the `/pet-advice/` base); the site's real article count is far higher but was not fetched. The homepage's latest articles cover choosing a healthy puppy, grooming products, training tips and platform news. The sampled post (homemade dog deterrents) runs 1,342 words. Posting frequency: NOT FETCHED — post URLs carry no dates and only one post was fetched.

## Visual
26 images on the homepage, none missing alt text; alts are mostly the article or breed name, with one generic "Image". No video on the homepage (the breed listing declares an advert video in its social tags).

## Schema
Organization only (homepage raw HTML).

## Cities
19 cities from `data/locations.json` are named on the fetched pages or have a page in the map: Aberdeen, Birmingham, Bristol, Cardiff, Coventry, Dundee, Edinburgh, Essex, Glasgow, Hull, Leeds, Leicester, Liverpool, London, Manchester, Nottingham, Oxford, Sunderland, York. Note the fetched Manchester breed page is served noindex, nofollow — the national breed page is the indexable one.

## Conversion
The platform's own calls to act are its payment service (pay through the site) and, in the help centre, arranging a viewing at the seller's home. Buyers message sellers from each advert; no advert page was fetched, so steps to enquire are unknown (null). Prices are printed on every advert — from £75 for an adult rehome to £3,000 for a puppy — and the price FAQ gives a national average. Urgency comes from the sellers: ready dates and "last one / one boy left" titles.

## Technical
At 375px the homepage fits the screen (scroll width 375): `mobile_layout_ok` true. Lighthouse: NOT FETCHED — no Lighthouse run in this pilot.

## Key insight
Pets4Homes wins the breed-plus-town searches by scale: one templated listing page per place, each with a live count, a price answer and dozens of long-tail colour and town links. BSUK cannot match the volume, but it can beat the template on depth — real breeder proof, one litter's facts, and city pages that answer the questions the classifieds page leaves blank.
