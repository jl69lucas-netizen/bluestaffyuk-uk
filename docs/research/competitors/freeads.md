# Freeads — competitor intel

- Root domain: freeads.co.uk · tier 2 (a free classifieds site that now carries pets only, "Freeads Pets": sale, rescue, stud and wanted adverts for every species, with a hub per town, county and breed) · analysed 2026-09-25.
- **This report replaces today's first freeads report.** That run's key pages were a Staffy-cross advert and the Oxford pug hub, because the page-type table gave the site's Staffy hubs no type. The classifier has since been fixed (commits 2af518b and 60a86b1): a breed hub with no type word now counts as the breed's listing, a marketplace's city and guide picks must be the breed's own, and plural breed terms count in keywords. This run re-typed today's saved map under those rules and re-fetched only the pages the new picks named.
- **Re-typed in the G1 consistency pass (0 credits).** The saved Map list was run again through the final classifier (commit 9d7e7b9). One Staffy-cross advert is no longer typed, so listing drops from 5 to 4; the key picks are unchanged. The licence field was re-read under the controller's ruling that it is true only when a licence number or a named council is shown.
- Homepage gate: passed. The status was 200, the final URL stayed on freeads.co.uk, and the page was the live homepage, not a bot check or a parked page.
- Key pages, as the fixed classifier picked them from the Map list (it flags the site as a `marketplace`):
  - listing slot: the UK-wide Staffordshire Bull Terrier hub. The homepage links it, and the Map list step added it at no cost. It is now typed `listing` as the breed's own hub, and it ranks ahead of the three Staffy adverts in the list;
  - price-or-FAQ slot: none. No URL in the Map list has a price or FAQ word in its path;
  - guide slot: none. The only `breed-guide` URLs are two rabbit pages, and another species is never a key page;
  - city slot: none. The Map list holds no town hub for the Staffy, and on a marketplace the city pick must be the breed's own, so the Oxford pug hub is no longer picked;
  - about slot: the about-us page.
- The first map is the controller's saved list at `maps/freeads.json` (88 URLs, fetched today with limit 500). No search map ran, in the first run or in this one.

## Trust
This is platform trust, not breeder trust. The site lists other people's pets and sets out its own safeguards:
- the about page says every advert is checked by hand before it goes live, users are verified and checked daily, and adverts follow the Pet Advertising Advisory Group's guidance. It tells the site's story as a general free-ads site since 2001 that turned pets-only in 2026;
- the Staffy hub ends with the advisory group's three buying checks (see the puppy with its mum, over eight weeks old, no imports) and a warning never to contact a number or email shown in an advert photo;
- hub cards mark ID-verified sellers. The homepage and the hub show a Trustpilot TrustScore badge, and the about page carries the Trustpilot logo.

The fields:
- `council_licence_shown`: false. The only licence mention is a bare seller's claim: one homepage advert card (a boxer litter) calls itself KC registered with a "5 star licence". It prints no licence number and names no council, and the platform itself shows no licence check, so under the ruling it is not a licence shown. `council` is null.
- `kc_registration_mentioned`: true. Many Staffy adverts on the hub say KC registered or KC papers, and the hub has a KC filter.
- `health_tests_named`: hip and elbow scores (a homepage Labrador advert), and L-2-HGA and HC-HSF4 (one Staffy litter on the hub says the dam is clear of both). All are sellers' claims. Other Staffy adverts say only "health tested" or "DNA clear" without naming a test.
- `vet_checks_mentioned`: true. Several hub adverts say the pups are vet checked or seen by a vet nurse, and one homepage card says the same.
- No breeding-since claim for any seller. The homepage's JSON-LD gives no address, and no page names a base town for the site, so `town` is null.
- The homepage measures script found no phone and no email in the homepage raw HTML.

Reviews: 15. The about page shows a Trustpilot slider with 15 short platform reviews in their own words. Each was listed once in a scratch file under a label of my own and counted with `grep -c .`. All are reviews of the platform by sellers and buyers, not of any breeder. The homepage has only the TrustScore badge. The hub's "what customers say" box shows no review words in the fetched content, because the widget loads by script. So neither adds anything.

## Content
- **Homepage:** 3,608 words by script, and 22 H2s. The H2 count is doubled because the page repeats its main strips and footer blocks for desktop and mobile. The H1 is a short line about finding pets forever homes. Below it sit:
  - a location picker for counties and cities;
  - species shortcuts;
  - strips of advert cards (latest, video, VIP, rescue and boosted adverts), each with a title, a town and a price;
  - category counts;
  - breed link clouds for dogs and cats;
  - footer link lists.
  Nearly all the words are card text, breed names and links. The homepage links the Staffy hub but says nothing of its own about the breed.
- **UK Staffy hub** (4 H2s): the page's H1 is Staffy puppies and dogs for sale. Its meta description counts about 250 adverts across the UK, over four pages of results. The page runs in this order:
  - a filter panel listing every dog breed;
  - sale, rescue, stud and wanted tabs, and sex, KC, price and coat-colour filters;
  - the feed of private sellers' cards. Each card gives a title, a town and county, a price, a photo count and the first lines of the seller's text. The cards mix KC litters (blue, red, brindle and blue-merle), Staffy crosses (with a Frenchie, a Shar Pei, a cane corso, an American bulldog and others) and adult dogs being rehomed;
  - mixed in with the feed: a strip of other breeds nearby, a row of featured VIP adverts, size and dog-group pickers, and mixed-breed links;
  - an alert sign-up box, colour links for the breed, and a short buyer's-advice note.
  The hub has no guide text about the breed, no price guidance and no FAQ.
- **About page** (6 H2s): the platform's story, why it turned pets-only, its four welfare safeguards, who it is for, and the Trustpilot slider. It is marked noindex.
- `url_count` is 88. The map returned 88 URLs against a limit of 500, so it was not cut short. It is still a thin sample of a site with tens of thousands of adverts.

## Keywords
29 phrases by the run rule (by script) from the three pages and their titles. The plural breed terms (staffys, staffordshire bull terriers) now count. Each link's text was read as its own element, so words from two neighbouring links are never joined.
- The homepage gives one: its breed link for Staffordshire Bull Terriers for sale, which the singular-only rule missed in the first run.
- The hub gives the rest, from its title, H1 and advert cards:
  - plain sale phrases: Staffy or Staffie puppies for sale, Staffordshire bull terrier puppies;
  - colour phrases: blue Staffy puppies, blue Staffordshire bull terrier puppies, and blue-merle phrases;
  - KC phrases: KC registered Staffy, KC registered Staffordshire bull terrier puppies;
  - many cross-breed phrases: Staffy x Frenchie, Staffy x Shar Pei, Staffy x American bulldog puppies.
- One phrase, `puppies we have 6 gorgeous staffy`, is an advert title that runs into its first sentence. The card prints the two with no break between them, so the rule keeps the run. It is noise, not a target.
- No run held a business, kennel or person's name. Sellers' display names sit in their own links, apart from the card text, so nothing was cut.

## Page types
By script over the 91-URL Map list, with `--home` set and no `--post-folder`, under the final classifier: city 13, listing 4, breed-guide 2, about 1. The classifier prints `marketplace: true`.
- **City (13):** hubs whose first path segment is a `data/locations.json` place. They cover every kind of pet, and none is for the Staffy:
  - Leeds and Birmingham all-pets hubs;
  - Birmingham dachshund, Cornwall whippet and Oxford pug dog hubs;
  - Birmingham Maine Coon and Aberdeen ragdoll cat hubs;
  - York canaries, London parrots, Leeds turtles and Liverpool rats hubs;
  - Cornwall livestock and Essex horses hubs.
- **Listing (4):**
  - the UK Staffy hub, typed as the breed's listing;
  - the Northern Ireland puppy hub;
  - two adverts: a Staffy-cross litter and a blue Staffy litter, whose slugs carry listing words.
  The Staffy-cross rehome advert counted before is no longer typed: a breed path is a listing only when its last segment is made of hub words, and that advert's is not.
- **Breed guide (2):** two rabbit pages whose paths hold a breeds folder (one of them an advert). Neither is a guide.
- **About (1):** the about-us page.
- **Untyped (71):** mostly breed and species hubs for other breeds and places (`/<place>/buy-sell/pets/<species>/<breed>`), whose paths hold no word from the table. The homepage, a search page, a few adverts for other breeds and the Staffy-cross rehome advert are also untyped.

The counts describe the map sample more than the site. The site's real shape is one hub for each place, species and breed, plus the adverts under them.

## Blog
- `post_count` 0, `post_folder` null.
- The Map list holds no blog, news or advice URL, and the homepage links none. The about page says the site is building pet-advice resources, but none was in the map.
- `posting_frequency`, `topics` and `sampled_word_counts` are NOT FETCHED: no post was counted or fetched.

## Visual
- From the homepage raw HTML, by script: 270 distinct images. Most are advert-card photos, whose alt text is the advert's title, so the dominant alt class is descriptive. 8 images have no alt.
- There is no video tag and no YouTube or Vimeo embed in the homepage raw HTML. Some cards on the hub carry video, but video is measured only on the homepage's raw HTML.

## Schema
The homepage raw HTML holds one JSON-LD graph: an Organization with an ImageObject logo, and a WebSite. There is no address, rating, Product, Offer, ItemList, FAQPage or BreadcrumbList markup on the homepage. The hub and the about page were scraped as markdown, so their schema was not read.

## Cities
19 `data/locations.json` places are named on the fetched pages or have a page in the map: Aberdeen, Birmingham, Bristol, Cornwall, Coventry, Essex, Glasgow, Hull, Leeds, Leicester, Liverpool, London, Manchester, Nottingham, Oxford, South Yorkshire, Sunderland, Wolverhampton and York.
- The homepage location picker names most of them: Hull by its full name, Kingston upon Hull, and Cornwall, Essex and South Yorkshire in its county list.
- The Staffy hub's cards name sellers' towns, among them Aberdeen, Birmingham, Coventry, Hull, Leeds, Liverpool, London, Manchester and Nottingham, and three towns in South Yorkshire.
- Glasgow, Leicester and Wolverhampton appear on homepage advert cards.
- Oxford, York, Essex and Aberdeen also have hubs for other species or breeds in the map.
- A card's county alone (such as Greater Manchester) was never taken as a city.

## Conversion
- `cta_types`: phone, whatsapp, visit. These are the ways the fetched pages ask a buyer to act:
  - phone: hub adverts that ask buyers to ring or text;
  - whatsapp: one hub advert and one homepage card that ask buyers to get in touch on WhatsApp;
  - visit: viewing the pups with their parents, which many adverts offer, and the hub's see-mum checklist.
  The site's own message box, number reveal and deposit panel sit on advert pages. None was fetched in this run, so no form or online deposit is recorded.
- `prices_shown`: true. 50 distinct amounts are printed across the homepage and the hub, from small feeder-insect packs up to £2,800 for a KC Staffy puppy. Some cards print a price without a comma (£1300 beside £1,300), so both forms are kept as printed. Staffy prices on the hub run from a few hundred pounds for crosses and rehomes to over £2,000 for KC litters.
- `deposit_terms`: the fetched pages show no platform deposit terms. Sellers set their own in their adverts: one says a deposit secures a puppy, and another takes deposits from a stated date. No deposit amount is printed.
- `steps_to_enquire`: null. No enquiry form or message box was on the pages fetched. The hub's email box signs up for new-advert alerts, which is not an enquiry.
- `urgency_signals`: `ready-date`, `few-left` and `waiting-list`.
  - Cards give ready-to-leave dates.
  - Several cards say one pup remains, on the hub and the homepage.
  - One hub litter says several buyers are already waiting to choose.
  Reserved pups are stated in text, not shown as sold badges.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch. It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
- `map_calls` 1. This run reused today's first map (saved at `maps/freeads.json`, same limit of 500), so the map cost nothing this time. It holds 88 URLs (`url_count`), below the 500 cap, and 1 breed URL (`breed_urls`). So the Map list did not ask for a search map (`search_map` false, `search_term` null), and none ran. `search_added` 0, `search_breed_urls` 0, and `search_adverts` does not apply (no `--search`).
- The homepage's breed links added 3 URLs (`home_added`): the UK Staffy hub and two breed adverts. That makes `map_list` 91.
- Scrapes: 3.
  - The homepage, as markdown and raw HTML. Firecrawl served it from cache, identical to the first run's copy.
  - The UK Staffy hub, as markdown.
  - The about page, as markdown, also from cache.
  The price-or-FAQ, guide and city slots were empty.
- Credits spent in this run: 3 (0 for the map + 3 scrapes at 1 credit each), against a ceiling of 8. With today's first run (5 credits), freeads has cost 8 credits in all today.

## Key insight
Freeads ranks for Staffy searches with one indexable UK-wide Staffy hub: a feed of a couple of hundred private adverts, many of them crosses and rehomes. On it, every KC, health-test or licence claim is the seller's word, and the only checks are the platform's. BSUK can beat that hub with one breeder's own blue Staffy pages that show what a feed cannot: named health results, a stated price and deposit, the parents, and a direct enquiry.
