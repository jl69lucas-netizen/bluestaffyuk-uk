# Dogs Trust — competitor intel

- Root domain: dogstrust.org.uk · tier 4 (dog rehoming charity) · analysed 2026-09-25. This is the entry's first report. The run used the classifier as updated today (commits 4e2fe7f, b8fb193, 50e1498 and bcab5b4).
- Homepage gate: passed. The status was 200, the final URL stayed on dogstrust.org.uk, and there was no bot check.
- Fetched: 1 map (limit 500), which returned **107 URLs**, then 5 scrapes. The first was the homepage, with markdown and raw HTML. The other four were the classifier's key pages:
  - the settle-your-new-puppy guide (listing slot: a `puppy` path, not an advert);
  - the dog-training basics hub (guide slot);
  - the Basildon (Essex) rehoming centre page (city slot);
  - the about-us page (about slot).
- The price-or-FAQ slot had no page, so it was not scraped. The puppy guide and about page came from Firecrawl's cache (cached 2026-09-23). The phone check ran in an emulated phone in Chrome DevTools. **6 Firecrawl credits in all.** The map is saved as a URL list at the controller's scratch path `maps/dogstrust.json`, so it can be re-typed later without spending credits.
- **No Staffy page was picked, and the breed step had nothing to pick from.**
  - The map holds five Staffordshire Bull Terrier adoption adverts. The breed is in their path, but each ends in a numeric dog id, and no table word types them, so none of them is in any slot.
  - The map also holds a sponsor-a-Staffy page whose slug does not name the breed.
  - The homepage navigation links a Staffordshire Bull Terrier breed guide in the "popular breeds" menu. That URL is not in the 107-URL map, so the classifier could not pick it and it was not fetched. That guide is probably the page that ranks for the seed searches, so it stays unanalysed.

## Trust
This is charity trust, not breeder trust:
- The homepage footer shows the charity's registered numbers, recorded as a yes in `registered_charity_number_shown`. The same footer shows a Fundraising Regulator badge.
- No fetched page mentions a council licence, the Kennel Club, a named health test or a vet check. The vet mentions are all about owners' vet care.
- No fetched page states a head-office town, so `town` is null. The Essex page gives that centre's own location, but it is one of many centres, not the charity's base.
- The homepage measures script found no phone and no email on the homepage (raw HTML). The Essex centre page does print a phone line and an email, as yes/no only here.

Reviews: 1, counted by script from the review list (`grep -c .` gives 1). It is a behaviour-support caller's thanks, shown on the about page. There are no adopter reviews on any fetched page.

## Content
- **Homepage:** 846 words by script, and 18 H2s. A large share of the words is the mega-menu, which lists every centre and 19 popular breeds. The page itself does four things: it leads with a donation appeal, runs an adoptable-dog search with a carousel of 15 dogs, links popular behaviour topics, and closes with fostering, volunteering and fundraising blocks.
- **Puppy guide** (8 H2s, two of them repeated as related-link cards): an essentials checklist, ten settling-in tips and the signs that a puppy has settled.
- **Training-basics hub** (21 H2s): nearly all of them are link cards to single-skill lessons.
- **Essex centre page** (9 H2s): opening hours, access, facilities, a yearly rehoming figure, a carousel of that centre's dogs, and ways to donate items.
- **About page** (10 H2s): the charity's mission, strategy and history.

None of the four key pages printed an H1 in its markdown, so their `h1` is empty. The homepage H1 comes from its raw HTML. The map returned 107 URLs, well under the cap, so it is only a sample of a much larger site.

## Keywords
None. The run rule found no qualifying phrase on any fetched page (by script). The breed appears only as the menu item for the breed guide and in the adoption cards' labels, which put "Terrier" before "Staffordshire Bull". Neither of those holds an intent word in the same run.

## Page types
By script over the 107-URL map, with no `--post-folder`: care-guide 10, breed-guide 7, health 4, about 3, city 3, listing 3, contact 2.
- **Breed-guide:** the seven are other breeds' guides under the "getting a dog" folder. None of them is the Staffy guide.
- **City:** two rehoming centres (Essex and Manchester) and a Manchester foster-carer vacancy.
- **Listing:** two puppy advice pages and the puppy-smuggling campaign. None of the three lists dogs.
- **Untyped:** the adoption adverts under `rehoming/dogs/` match no table word, so they are not counted.

## Blog
0 posts by the classifier. The map has no blog, news or dated folder, and no post sitemap, so no `--post-folder` was named. Posts without a blog base or a date are missed, and the table counted them as it found them. Topics, sampled word counts and posting frequency are NOT FETCHED, because no post was among the key pages and the map holds no dated post URL.

## Visual
- **Images:** 39 distinct images on the homepage (homepage measures script, raw HTML, with sources resolved against the homepage URL).
- **Alt text:** most alts are descriptive, and 3 are missing.
- **Photography:** real photos of rescue dogs, including a Staffordshire Bull Terrier in the behaviour-support block. Illustrated icons are used for the service links.
- **Video:** no `<video>` tag and no YouTube or Vimeo embed in the raw HTML. The YouTube link in the footer is a social link, not an embed.

## Schema
`NGO`, from the one JSON-LD block in the homepage raw HTML. It holds the organisation's name, URL and social profiles. The key pages were fetched as markdown only, so their schema was not read.

## Cities
Cardiff, Dundee, Essex, Glasgow, Leeds, London and Manchester are named on the fetched pages. They come from the homepage's list of rehoming centres (London appears as the West London centre) and from the location lines on the dog cards. Essex and Manchester also have centre pages in the map. Merseyside and the other regions are not mapped to a city.

## Conversion
The fetched pages ask people to adopt, visit or give, never to buy:
- The homepage has an adoptable-dog search, a donation form and a newsletter sign-up (`form`).
- The Essex centre invites walk-in visits on set days (`visit`), and prints a phone line and an email (`phone`, `email`).
- The adoption application itself is behind the how-to-adopt page, which was not fetched. No enquiry form was fetched, so steps to enquire is null.

No dog is priced. The only amounts printed are the donation form's preset gift amounts, so `prices_shown` is false and no amounts are recorded. There are no deposit terms.

Urgency: several dog cards on the homepage and the Essex page carry a "Reserved" badge. That is recorded as `sold-badges`. The pages state no ready dates, no waiting list and no deadline.

## Technical
The check ran in an emulated phone in Chrome DevTools (375 × 812 viewport, mobile user agent, touch). The homepage was loaded, then the mobile-check evaluate ran. It returned:
- innerWidth 375
- clientWidth 375
- scrollWidth 375
- screenWidth 375
- maxTouchPoints 1
- mobileUA true

So `mobile_layout_ok` is true. Lighthouse: NOT FETCHED (no Lighthouse run).

## Key insight
Dogs Trust ranks for Staffy buying and price searches because it is a trusted charity, not because it has a Staffy sales page. Its map has Staffy adoption adverts and a sponsor page, but its fetched pages price no dog and carry only an organisation schema. BSUK can win the same searches with a Staffy-specific guide backed by real litter prices and breed schema. That guide should answer the welfare and cost questions a buyer brings from Dogs Trust's adopt-first advice.
