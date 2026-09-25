# Dogs Trust — competitor intel

- Root domain: dogstrust.org.uk · tier 4 (dog rehoming charity) · analysed 2026-09-25. This is the entry's first report.
- **Topped up in the G1 consistency pass (1 credit).** The saved map and the saved homepage raw HTML were run again through the final Map list and classifier (commit 9d7e7b9). The Map list now adds the homepage's own breed links at no cost, and one of them is the Staffordshire Bull Terrier breed guide that the first map missed. The classifier makes that guide the guide pick, so it was scraped. The site now counts as a directory (breed guides for the Staffy and other breeds), and the classifier prints `marketplace: true`, so the city slot takes only the breed's own pages and is now `null`. Two pages from the first run are no longer picks and have left the report, with everything only they fed: the dog-training basics hub (the old guide pick) and the Basildon (Essex) rehoming centre (the old city pick).
- Homepage gate: passed. The status was 200, the final URL stayed on dogstrust.org.uk, and there was no bot check.
- Pages in this report, as the final classifier picks them:
  1. the homepage, with markdown and raw HTML (scraped earlier today, reused);
  2. the settle-your-new-puppy guide (listing slot: a `puppy` path, not an advert; reused);
  3. the Staffordshire Bull Terrier breed guide (guide slot; scraped in this top-up);
  4. the about-us page (about slot; reused).

  The price-or-FAQ slot and the city slot have no page, so neither was scraped.
- The phone check was run again in this top-up, in an emulated phone in Chrome DevTools.

## Trust
This is a charity's trust, not a breeder's:
- The homepage footer shows the charity's registered numbers, recorded as a yes in `registered_charity_number_shown`. The same footer shows a Fundraising Regulator badge.
- No page in the report mentions a council licence or the Kennel Club, so `council` is null.
- The breed guide names no health test. It tells a would-be owner to ask their own vet about the breed's health risks. It also says a vet can help them find a responsible breeder who tests for inherited disease. That is advice to the owner, not a check on the charity's dogs, so `vet_checks_mentioned` stays false.
- No page states a head-office town, so `town` is null.
- The homepage measures script (raw HTML, with `HOME_URL` set) found no phone and no email on the homepage.

Reviews: 1, counted by script from the review list (`grep -c .` gives 1). It is a behaviour-support caller's thanks, shown on the about page. There are no adopter reviews on any page in the report.

## Content
- **Homepage:** 846 words by script, and 18 H2s. A large share of the words is the mega-menu, which lists every centre and 19 popular breeds. The page itself does four things:
  - it leads with a donation appeal;
  - it runs an adoptable-dog search, with a carousel of 15 dogs;
  - it links popular behaviour topics;
  - it closes with fostering, volunteering and fundraising blocks.
- **Puppy guide** (8 H2s, two of them repeated as related-link cards): an essentials checklist, ten settling-in tips and the signs that a puppy has settled.
- **Staffy breed guide** (24 H2s):
  - It opens with a carousel of ten dogs to rehome, nearly all Staffies or Staffy crosses, and links to the full Staffy search.
  - A short introduction sets the breed apart from the American Staffordshire Terrier.
  - Nine expandable question blocks follow: health, food and body condition, exercise, grooming, crate size, temperament, training and children.
  - Each block ends in link cards to general advice pages, and those cards are most of the H2s. Six more cards link to other breeds' guides.
  - It closes with cards on buying safely, readiness to own a dog and the benefits of adopting.
- **About page** (10 H2s): the charity's mission, strategy and history.

None of the three key pages printed an H1 in its markdown, so their `h1` is empty. The homepage H1 comes from its raw HTML. The map returned 107 URLs, well under the cap, so it is only a sample of a much larger site.

## Keywords
None. The run rule found no qualifying phrase on any page in the report (by script, over all four pages together and over the breed guide alone). The breed guide names the breed many times, but never in the same run as an intent or place word. Its sentence about buying a puppy does not name the breed. Adoption cards label the breed with "Terrier" first, then "Staffordshire Bull" in brackets, and that does not match the pattern word. No name cut was needed.

## Page types
By script over the 108-URL Map list, with `--home` set and no `--post-folder`. The list is the 107-URL first map, one URL per page (the map lists the homepage twice), plus the two homepage breed links. Counts: care-guide 10, breed-guide 8, health 4, about 3, city 3, listing 3, contact 2.
- **Breed-guide:** the seven other breeds' guides under the "getting a dog" folder, and now the Staffy guide as well.
- **City:** two rehoming centres (Essex and Manchester) and a Manchester foster-carer vacancy. None is the breed's own page, so on this directory none is the city pick.
- **Listing:** two puppy advice pages and the puppy-smuggling campaign. None of the three lists dogs.
- **Untyped:** the adoption adverts under `rehoming/dogs/` match no table word, so they are not counted. The second homepage breed link is one of these adverts.

## Blog
0 posts by the classifier. The map has no blog, news or dated folder, and no post sitemap, so no `--post-folder` was named. Posts without a blog base or a date are missed, and the table counted them as it found them. Topics, sampled word counts and posting frequency are NOT FETCHED, because no post was among the key pages and the map holds no dated post URL.

## Visual
- **Images:** 39 distinct images on the homepage (homepage measures script, raw HTML, with sources resolved against the homepage URL).
- **Alt text:** most alts are descriptive, and 3 are missing.
- **Photography:** real photos of rescue dogs, including a Staffordshire Bull Terrier in the behaviour-support block. Illustrated icons are used for the service links.
- **Video:** no `<video>` tag and no YouTube or Vimeo embed in the raw HTML. The YouTube link in the footer is a social link, not an embed.

## Schema
`NGO`, from the one JSON-LD block in the homepage raw HTML. It holds the organisation's name, URL and social profiles. The key pages were fetched as markdown only, so their schema was not read. That includes the breed guide.

## Cities
Seven cities are named on the homepage: Cardiff, Dundee, Essex, Glasgow, Leeds, London and Manchester. They come from its list of rehoming centres (London appears as the West London centre) and from the location lines on the dog cards. The breed guide's dog cards name Cardiff, Essex, Glasgow and West London again. Essex and Manchester also have centre pages in the map. Merseyside and the other regions are not mapped to a city.

## Conversion
The pages in the report ask people to adopt or give, never to buy:
- The homepage has an adoptable-dog search, a donation form and a newsletter sign-up (`form`).
- The breed guide's main ask is to browse the Staffies up for rehoming.
- The adoption application itself is behind the how-to-adopt page, which was not fetched. No enquiry form was fetched, so steps to enquire is null.
- The visit, phone and email calls to action in the first report came from the Essex centre page, which has left the report, so they have been removed.

No dog is priced. The only amounts printed are the donation form's preset gift amounts, so `prices_shown` is false and no amounts are recorded. The breed guide mentions costs only as something to ask a vet about, and gives no figure. There are no deposit terms.

Urgency: several dog cards on the homepage and in the breed guide's carousel carry a "Reserved" badge. That is recorded as `sold-badges`. The pages state no ready dates, no waiting list and no deadline.

## Technical
The check was run again in this top-up, in an emulated phone in Chrome DevTools (375 × 812 viewport, mobile user agent, touch). The homepage was loaded, then the mobile-check evaluate ran. It returned:
- innerWidth 375
- clientWidth 375
- scrollWidth 375
- screenWidth 375
- maxTouchPoints 1
- mobileUA true

So `mobile_layout_ok` is true. Lighthouse: NOT FETCHED (no Lighthouse run).

## Fetch
- **Map list:** re-run in this top-up on today's saved first map and homepage raw HTML.
  - `map_calls` 1, `url_count` 107, `breed_urls` 5.
  - `search_map` false, because the map is under the cap and holds breed paths. So no search map ran: `search_term` null, `search_added` 0, `search_breed_urls` 0, and `search_adverts` does not apply.
  - `home_added` 2: the Staffy breed guide and one Staffy rehoming advert. `map_list` 108.
- **Scrapes today:** 6.
  - 5 in the first run: the homepage and four key pages. Two of those four, the training-basics hub and the Essex centre, are no longer picks.
  - 1 in this top-up: the Staffy breed guide. Before it was scraped, its path was confirmed to name the breed.
- **Credits:** 7 Firecrawl credits today (1 map and 6 scrapes), within the ceiling of 8. This top-up spent 1 of them. The first map was reused at no cost.

## Key insight
Dogs Trust ranks for Staffy buying and price searches through its authority as a charity and a Staffy breed guide that promotes adoption, not buying. The guide covers the questions an owner asks in short expandable blocks under a carousel of rescue Staffies. But it names no health test, prices no dog and leaves costs to the owner's vet. BSUK can win the same searches with a Staffy guide that answers the same questions and adds what Dogs Trust leaves out: the breed's named health tests, real litter prices and the cost of owning a Staffy.
