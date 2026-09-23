# RSPCA — competitor intel

- Root domain: rspca.org.uk · tier 3 (animal-welfare charity) · analysed 2026-09-23
- Homepage gate: passed (status 200; final URL stays on rspca.org.uk)
- Fetched: 1 map (477 URLs) + 6 scrapes — homepage (markdown + raw HTML), the buying-a-puppy guide, the pedigree-dog health page, the puppy-trade facts page (it returned a 404 page; the credit was spent and the page is listed as fetched), the dog adoption process page (the old rehoming URL redirects to it), the pet cost calculator. Playwright: the JSON-LD read and the 375px check on the homepage.
- The breed-specific advice page the registry says ranks for the seeds was not in the 477-URL map, so it was not fetched.

## Trust
Charity trust rather than breeder trust: a registered charity number in the footer, a "where your money goes" breakdown, and a science team voice on breed health. The pedigree page cites Kennel Club breed standards; the adoption page says every dog is microchipped, vaccinated, neutered and vet-checked. No council licence, no named DNA tests, no town. No phone number or email is printed on the homepage (a chat widget offers to schedule a call back). No reviews.

## Content
Homepage: 1,395 words by script — much of it the navigation menu, which the page prints twice — with 15 H2s (nine in the body, six in a doubled footer). The map returned 477 URLs, a sample of a much larger site. Advice pages are long, sectioned (7–10 H2s) and link heavily to each other.

## Keywords
None. The run rule found no qualifying phrase on any fetched page: none of them names the breed — the buying guide is written for any puppy.

## Page types
By script over the map: care-guide 20, health 18, contact 9, price 6, listing 5, about 2, blog 2, faq 2, reviews 1. "Price" here is the cost-of-living section (pet budgeting), not puppy prices.

## Blog
2 posts in the map (script count of blog-post URLs). No post was fetched, so topics, sampled word counts and posting frequency are NOT FETCHED.

## Visual
24 images on the homepage; 17 have empty or missing alt text, and two use the placeholder word as alt. A video plays in the conformation-campaign block.

## Schema
None — the homepage raw HTML and a Playwright JSON-LD read both found no JSON-LD.

## Cities
None named on the fetched pages and no city pages in the map.

## Conversion
The buyer path is adoption, not purchase: search the rescue database, apply on a dog's profile (reply promised within 48 hours), meet the dog at a centre, a home check, then pay an adoption fee that varies by centre and age (no amount printed). A chat widget offers a scheduled phone call. The buying guide tells readers to see mum with the pups, use a puppy contract and avoid online adverts. No prices for animals and no urgency.

## Technical
At 375px the homepage fits the screen (scroll width 375): `mobile_layout_ok` true. Lighthouse: NOT FETCHED — no Lighthouse run in this pilot.

## Key insight
RSPCA's fetched pages never name the breed and carry no schema, yet it ranks for Staffy buying and price searches — its pull is domain authority, not breed content. BSUK can beat it on intent with a Staffy-specific responsible-buying and price guide that answers the same welfare checks for this breed.
