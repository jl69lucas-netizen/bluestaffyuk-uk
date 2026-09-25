# Trojanstaff UK — competitor intel

- Root domain: trojanstaffuk.com · tier 1 · analysed 2026-09-25 (re-run under the current rules; replaces the 2026-09-23 pilot report)
- Homepage gate: passed (status 200; final URL stays on trojanstaffuk.com)
- Fetched: 1 map (39 URLs) + 3 scrapes — homepage (markdown + raw HTML), the listing key page (`/staffy-puppies`) and the about key page (`/about-1`). The classifier's price-or-FAQ, guide and city slots were empty, so nothing else was scraped. JSON-LD read from the homepage raw HTML. Mobile check: Chrome DevTools phone emulation (375 × 812, mobile user agent, touch). 4 Firecrawl credits.

## Trust
The homepage prints a breeder licence number but does not say which council issued it (`council` null). It mentions Kennel Club registration and names a set of DNA and screening tests for the parents (L-2-HGA, HC-HSF4, PHPV/PPSC, hip dysplasia); the stud page adds BVA eye screening. Vet care and health checks are mentioned. It claims over a decade of breeding and gives Basingstoke as its base; the stud page also talks of a new Manchester branch. Phone and email are both shown (homepage measures script, raw HTML). Reviews: 0 — the homepage points to reviews at the bottom of the page, but they are two screenshot images of Google reviews plus a five-star badge, so no review words are in the fetched content.

## Content
Homepage: 1,120 words (by script) under 15 H2s, running through stud dogs, bloodlines, puppies, stud services and an ethics promise. The listing page has 3 H2s and the stud page 2. The map returned 39 URLs, several of them duplicates with the page description glued onto the path — a site-builder SEO fault.

## Keywords
17 phrases by the run rule (script over every sentence, heading and list item of the three pages). The core buying terms are there — staffy puppies for sale, staffordshire bull terrier puppies for sale, blue staffy puppies, staffy puppies in the uk — plus breeder terms (staffy breeders, staffordshire bull terrier breeders). Runs were cut at the kennel's own brand words (Trojan, Trojanbulls, Trojanstaff).

## Page types
By script over the map: blog 19 (18 posts under `/post/` plus the blog index), about 3, contact 1, listing 1. No price, FAQ, guide, health or city pages are typed; the stud-dog and female pages have builder-style slugs (`services-4`, `about-1`) the table cannot read. The about slot's pick is therefore `/about-1`, which is really a single stud dog's page, not an about page.

## Blog
18 posts by the classifier (under the `/post/` folder the table's blog row reads; no `--post-folder` needed). No post was among the key pages, so topics, sampled word counts and posting frequency are NOT FETCHED — the post URLs carry no dates either. The map's post slugs point to a mix of stud-dog stories, champion titles, breeding and whelping, and owner guides (feeding, training, health), but that is not a fetched reading.

## Visual
29 distinct images on the homepage (script), none without alt text; the alts are mostly descriptive. No video tag or YouTube/Vimeo embed in the raw HTML.

## Schema
WebSite, LocalBusiness, PostalAddress, Article, WebPage, ImageObject, Person, Organization — from the homepage's JSON-LD.

## Cities
Manchester only, named on the stud page as the base of a new branch. No city pages.

## Conversion
Buyers are asked to phone (the listing page says to call, the homepage prints a number) or email; the stud page adds a WhatsApp link for stud bookings. The listing page sends puppy enquiries to the contact page, which was not a key page, so no enquiry form was fetched (`steps_to_enquire` null); a newsletter sign-up and a chat pop-up are not enquiry forms. The only printed price is a £600 stud fee on the stud page — no puppy prices and no deposit terms on the pages fetched. No urgency signal from the list: the homepage talks of limited litters and early reservations, which is not a stated few-left, date or waiting list.

## Technical
Emulated phone evaluate: innerWidth 320, clientWidth 320, scrollWidth 320, screenWidth 375, maxTouchPoints 1, mobileUA true → `mobile_layout_ok` true. The site builder serves phones a separate mobile layout that fits the screen (the pilot's overflow came from a resized desktop browser). Lighthouse: NOT FETCHED — no Lighthouse run.

## Key insight
Trojanstaff wins on proof rather than pages: a licence number, named DNA tests, Kennel Club registration and champion lines lead its homepage. It has no city pages, no puppy prices, no review text on the page and no dates on its posts — BSUK can match the proof and beat it with local pages, visible written reviews and fresh, dated guides.
