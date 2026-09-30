# BlueStaffyUK (own build) — intel profile

- Source: `dist/` from `npm run build` on 2026-09-25 (branch p5-readiness). This is a re-run: all 21 competitor reports were made or re-made today (Known Issue 57). Domain: SITE_URL_PLACEHOLDER until project 6. No Firecrawl, no homepage gate, no registry write.
- Pages: the 31 indexable URLs in the four sitemaps (post 1, location 11, puppy 6, page 13), each listed once with its `dist/` title, H1 and H2s. None of them carries a noindex robots meta, and the noindex stubs stay out. A script turned each page into markdown (with scripts, styles, templates, noscript and SVG removed) for the keyword and word counts.

## Trust
The pages state Kennel Club registration, the two DNA tests on both parents (L-2-HGA and HC-HSF4) and vet checks. The base town is Carlisle. No page prints a council licence or a council's name, so `council_licence_shown` is false. The rebuilt pages say plainly that no licence wording will appear until there is a document behind it. The older UK location hub still calls the business council-licensed. There is no breeding-since claim. The homepage measures script found an email link on the raw HTML, and no phone number or `tel:` link. Reviews: 6 distinct reviews show their words on the pages, counted by script from a scratch list. Three are the families the rebuilt pages repeat on many pages. The other three are star-rated reviews that appear only on the older UK location hub.

## Content
Homepage: 5,658 word tokens, counted by script. The count covers the whole built page turned into markdown, including navigation, the table of contents and the footer. It is therefore not strictly comparable with the competitors' main-content scrapes. There are 31 indexable URLs. The JSON holds the H2 count for each page: 3 on each puppy page and on the locations index, 7 on each older city page, and up to 23 on the homepage and the buying guide.

## Keywords
231 phrases in all. BSUK's own runs by the rule over all 31 pages gave 234. Four were removed because they contain the business name ("Blue Staffy UK" / "BlueStaffyUK"), which leaves 230. The phrase script found 27 competitor phrases in `dist/`, and one of them (`staffordshire bull terrier blue`) was not already in BSUK's own list. Each city page adds its own breed-plus-city phrases.

## Page types
The sitemaps come first: the post sitemap gives 1 blog page and the puppy sitemap gives 6 listing pages. The classifier with `--bsuk` then typed the 24 URLs in the location and page sitemaps, with the hub rule off as `--bsuk` requires. It gave listing 6, city 9, breed-guide 2, blog 1 (the guides hub), about 1, contact 1 and health 1. The homepage, the privacy page and the Glasgow breeding-dogs page stay untyped. Totals: listing 12, city 9, blog 2, breed-guide 2, about 1, contact 1, health 1. There is no care-guide, FAQ, price or reviews page type. The page that explains what a puppy costs is typed as a listing, because its URL contains `sale` and no price word.

## Blog
The post sitemap holds one post, about choosing the right blue Staffy puppy for a family. Its main content is 162 words, counted by script. No post folder. Posting frequency: NOT FETCHED, because one post gives only one date.

## Visual
The homepage measures script ran on `dist/index.html` with `HOME_URL` set to https://SITE_URL_PLACEHOLDER/. It found 21 distinct images. 4 have no alt text and most of the rest have descriptive alt text, so `alt_text` is descriptive. The homepage has two YouTube (no-cookie) embeds, so a video is present.

## Schema
The JSON-LD on the 31 pages holds 23 `@type` values. They include LocalBusiness, Organization, Product, Offer, AggregateOffer, FAQPage, BlogPosting, Article, BreadcrumbList, VideoObject, AboutPage and ContactPage. Compared with the competitors, BSUK lacks Person and SearchAction (each used by 5 of 20). It also lacks a handful of types that only one competitor uses, such as AggregateRating, Review and ContactPoint.

## Cities
The pages name all 25 real cities in `data/locations.json`. Ten of them have their own page: the nine city pages, plus Glasgow, whose page is the breeding-dogs page.

## Conversion
There is one enquiry form, the same on four pages: the contact page, the price page and both puppies-for-sale pages. It is a single screen in three numbered parts with one submit button, so `steps_to_enquire` is 1. The pages also give an email link, and the buying steps offer a call and a visit. Every puppy card and the homepage table print prices, by sex. The terms are a refundable deposit that holds one named puppy and comes off the price, free collection, and delivery priced by distance. The form offers a waiting-list choice for the next litter, which is the only urgency signal.

The amounts list in the JSON also includes what the older location pages print, and it does not match the rebuilt pages:
- all nine city pages print a flat delivery fee;
- the Aberdeen and Edinburgh pages, the UK hub and the Glasgow breeding-dogs page print a lower price band for puppies that are no longer listed;
- the Hull page calls the deposit non-refundable;
- the UK hub gives a different deposit amount and collection from Glasgow.

These are content problems for the page rebuilds, not intel fixes.

## Technical
The mobile check ran against `npm run preview` on port 4391, in Chrome DevTools emulating a phone (375 × 812, mobile user agent, touch). It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true, so `mobile_layout_ok` is true. The server was stopped and the page closed afterwards. Lighthouse: NOT FETCHED, because this run made no Lighthouse run for `--bsuk`.

## Fetch
No Firecrawl: 0 maps, 0 scrapes, 0 credits. `map_calls` is 0 and no search map ran (none ever does for `--bsuk`). `search_added`, `search_breed_urls`, `search_adverts` and `home_added` do not apply. Everything was read from the local `dist/` build, plus one page load in the local preview.

## Key insight
BSUK's build now names all 25 cities the competitors show. It holds every phrase that three or more competitors share except one (`kc registered staffordshire bull terrier puppies`). Its gaps are care-guide, FAQ, price and reviews page types, Person and SearchAction schema, and the older location pages, whose delivery fee and, on some pages, price band and deposit terms contradict the rebuilt pages.
