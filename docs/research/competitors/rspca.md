# RSPCA — competitor intel

- Root domain: rspca.org.uk · tier 3 (animal-welfare charity) · analysed 2026-09-25. This re-run replaces the 2026-09-23 pilot report, which was made before the page-type table, the key-page picks, the homepage-measures script and the phone-emulation rule changed (Known Issue 51). The classifier now puts the breed's pages first (commits 4e2fe7f and b8fb193).
- Homepage gate: passed (status 200; the final URL stays on rspca.org.uk; no bot check).
- Fetched: 1 fresh map (limit 500) that returned **471 URLs** (the pilot map returned 477), then 5 scrapes. The first was the homepage, with markdown and raw HTML. The other four were the classifier's key pages: the buying-a-puppy guide (listing slot), the gifts-in-Wills FAQ (price-or-FAQ slot; the map has no price page under the current table), the dog-training guide (guide slot) and a privacy-notice page whose slug contains "about" (about slot). That last page returned a 404. The credit was spent, and the page is listed as fetched. The city slot had no page, so it was not scraped. The homepage and puppy-guide scrapes were served from Firecrawl's cache (cached 2026-09-24 and 2026-09-23). The phone check and a JSON-LD read ran in an emulated phone in Chrome DevTools. 6 Firecrawl credits in all.
- **The Staffy advice page is not in the new map either.** None of the 471 URLs names the breed: no `staffy`, `staffie`, `staffies`, `sbt`, `staffordshire-bull` or `blue-staff` word. The only bull-breed URL is the XL Bully legislation page. So the breed step had nothing to pick, and each slot fell back to its other pages. The page the registry says ranks for the seeds is still unfetched.

## Trust
This is charity trust, not breeder trust. The homepage footer shows a registered charity number (recorded as a yes, `registered_charity_number_shown`). The homepage also has a "where your money goes" breakdown and a Fundraising Regulator badge. None of the fetched pages mentions the Kennel Club, a named DNA test or a vet check. The puppy guide mentions insuring for vets' fees, which is not a vet check. The Wills FAQ gives the charity's head-office town as Horsham. That page also prints a phone number and an email for the legacy team, but the homepage measures script found neither a phone nor an email on the homepage. Reviews: 1. It is a supporter's testimonial about leaving a gift in a Will, on the FAQ page, counted by script from the review list (`grep -c .` gives 1). No pet buyer or adopter review appears on any fetched page.

## Content
Homepage: 1,378 words by script, under 15 H2s. Much of that is the navigation menu, which the page prints twice, and six of the H2s are a footer printed twice. The buying guide (7 H2s) is a short hub. It urges adoption over buying, points to a pet cost calculator and to advice on spotting bad adverts and finding a good breeder, and recommends the Puppy Contract and pet insurance. The training guide (5 H2s) covers why and how dogs learn and some basic tips. The Wills FAQ (7 H2s) is about legacy giving and has nothing to do with buying a pet. The map returned 471 URLs, below the 500 cap, but that is still a sample of a much larger site.

## Keywords
None. The run rule found no qualifying phrase on any fetched page, because no page names the breed: no breed term appears in the homepage or any key page (checked by script).

## Page types
By script over the 471-URL map, with no `--post-folder`: care-guide 18, health 13, contact 9, listing 5, about 4, blog 3, faq 1. There is no price type under the current table: `costofliving` is one word, so the pet cost calculator is not a price page. The pilot's count of price 6 came from the old table.

## Blog
0 posts by the classifier. The three blog-typed URLs are the latest-news index, the blogs index and one post whose slug starts with "blog-". That post sits in a root `/-/` folder alongside privacy-notice pages, so no posts-only folder can be named with `--post-folder`. The map has no post sitemap. Posts without a blog base or a date are missed, and the table counted them as it found them. Topics, sampled word counts and posting frequency are NOT FETCHED: no post was among the key pages, and the map holds no dated post URL.

## Visual
19 distinct images on the homepage (homepage measures script, raw HTML, with sources resolved against the homepage URL). 13 have no alt or an empty alt, so the most common alt class is missing. The pilot recorded 24 images, but that count came from before the current measures script. There is one `<video>` tag in the raw HTML, in the conformation-campaign block.

## Schema
None. The homepage raw HTML holds no JSON-LD, and a JSON-LD read in the emulated phone returned an empty list.

## Cities
None. No `data/locations.json` city is named on the fetched pages, and the map has no city page. The head-office town on the FAQ page is not one of the cities.

## Conversion
The pages fetched never ask a buyer to buy. The puppy guide steers readers towards adopting through the charity and away from online adverts, and tells anyone buying to see the mother with her pups. Every direct ask on the fetched pages is to donors. The homepage has a donation form with preset monthly and one-off amounts. The Wills FAQ asks legators to phone or email the team and links to a pledge form (`form`, `phone`, `email`). Neither form is an enquiry form for an animal, so steps to enquire is null. The only amounts printed are donation, raffle and Will-writing figures. No animal is priced, so `prices_shown` is false and no amounts are recorded. No deposit terms and no urgency.

## Technical
Emulated phone in Chrome DevTools (375 × 812 viewport, mobile user agent, touch), homepage loaded, then the mobile-check evaluate. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true, so `mobile_layout_ok` is true. Lighthouse: NOT FETCHED (no Lighthouse run).

## Key insight
Even with breed-first picks, RSPCA has no Staffy page to pick. Its fetched pages speak to any dog, carry no schema and price no animal. Its rankings for Staffy buying and price searches rest on the charity's authority and on a welfare page this map does not reach. BSUK can compete on those searches with a Staffy-specific buying and price guide that walks through the same welfare checks RSPCA tells every buyer to make.
