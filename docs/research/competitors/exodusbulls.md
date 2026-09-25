# Exodusbulls — competitor intel

- Root domain: exodusbulls.co.uk · tier 1 · analysed 2026-09-25 (first report for this entry)
- Homepage gate: passed (status 200; final URL stays on exodusbulls.co.uk; a real page, not a bot check or parked page)
- Fetched: 1 map (13 URLs) + 2 scrapes. The scrapes were the homepage (markdown and raw HTML) and the listing key page (`/puppies`). The path names a dog word (`puppies`) and the homepage menu labels it as the puppy waiting list, so it passed the breed-or-dog check before it was scraped. The classifier left the price-or-FAQ, guide, city and about slots empty (`null`), so nothing else was scraped. JSON-LD was read from the homepage raw HTML and checked again in the emulated phone. The mobile check used Chrome DevTools phone emulation (375 × 812, mobile user agent, touch). 3 Firecrawl credits (1 map + 2 scrapes).

## Trust
- Licence: none shown. Neither page shows a licence number or a named council. Neither page claims to be "licensed" either, so there is no bare claim to quote. `council_licence_shown` is false and `council` is null.
- Kennel Club registration is mentioned many times. The stud dogs are described as KC registered, and so are the waiting-list puppies. Visiting bitches must be KC registered too.
- Health tests named: L2-HGA and HC-HSF4, both given as clear for every stud. The stud section also says the dogs are vet checked regularly (`vet_checks_mentioned` true).
- Experience: the owners say they have kept the breed for over 20 years and moved into hobby breeding after about ten years of ownership (`breeding_since_as_worded`: "over 20 years").
- Town: null. The homepage gives its base only as a county (Kent), not a town, and no `data/locations.json` city is named.
- Contact signals (from the Homepage measures script, raw HTML): `email_shown` true (a `mailto:` link). `phone_shown` is false. The site header carries a website-builder template's placeholder number and placeholder address. Neither matches the contact scan's formats, so no real number is shown.
- Reviews: 0. The map has a `/reviews` page, but no key-page slot takes it, so it was not fetched. Neither fetched page shows a review's words, and there is no star rating or badge either (scratch list empty; `grep -c .` gives 0).

## Content
The homepage has 2,326 words (counted by script, with image, link and heading markup stripped) and no H1 or H2 at all. The raw HTML has only one H3, a "follow us" footer label. The long page is set in bold paragraphs and emoji bullet lists. It covers the kennel's claims to the top blue bloodline in the UK, health testing and low inbreeding figures, and the stud terms: bitches must be KC registered and DNA clear. It then covers chilled and frozen semen shipping in the UK and abroad, a free repeat mating if the first one fails, and a long profile of each of four champion studs, ending with an about section. The waiting-list page (296 words, no H1 or H2) explains that the list passes buyers on to other breeders who have used the studs. It says plainly that it is not a sale page. The map returned 13 URLs (`url_count`).

## Keywords
The run rule found 9 phrases (script over every sentence, heading, list item and menu link of both pages): blue staffordshire bull terrier(s), blue staffordshire bull terrier breeders, blue and black staffordshire bull terriers, blue bloodline staffordshire bull terrier, blue sbt, sbt in the uk, staffordshire bull terrier in the uk and staffordshire bull terrier puppy. None of them held a business, kennel or person's name, so the script was not re-run with a cut. The vocabulary is breed and colour. None of the phrases is "puppies for sale", a price or a city.

## Page types
Classifier over the 13-URL map list: contact 1, listing 1 (`/puppies`), reviews 1. The rest are untyped stud profiles, services and an offspring page. The menu's about link points to `/the-blue-stafford`. That slug holds no about word, so the table leaves it untyped and the about slot is `null`. The site has no breed guide, care guide, price, FAQ, health or city pages.

## Blog
No blog. The map has no blog folder, dated path or post folder, so `post_count` is 0 and `post_folder` is null. Topics, posting frequency and sampled word counts: NOT FETCHED (there are no posts to fetch or date).

## Visual
From the Homepage measures script (raw HTML, `HOME_URL` given): 15 distinct images, all 15 with no alt text (`alt_text` missing, `alt_missing` 15). There is no `<video>` tag and no YouTube or Vimeo embed (`video_present` false).

## Schema
No JSON-LD. The homepage raw HTML has no `application/ld+json` block, and the evaluate in the emulated phone found none either, so `schema_types` is an empty list.

## Cities
None. Neither page names a `data/locations.json` city, and the map has no city page. The base is given only as a county, and a county is never read as a city.

## Conversion
- CTAs: email (the header and contact `mailto:` links) and form (the waiting-list form on `/puppies`). No phone call-to-action, WhatsApp, visit or online deposit.
- Prices: shown, but only for the stud service. The homepage prints a UK chilled-semen shipping fee of £160 and notes that the stud fee is charged on top. No puppy price is printed. `deposit_terms` is null: the waiting-list page mentions lost deposits only as a warning about scams, not as terms.
- `steps_to_enquire`: 1 (a one-page form asking for name, email, phone, location, a choice of sire, colour and sex, and a free-text box).
- Urgency: `waiting-list` only.

## Technical
The emulated phone evaluate returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true, so `mobile_layout_ok` is true. Lighthouse: NOT FETCHED (no Lighthouse run).

## Fetch
Fetch: `map_calls` 1 · search map ran: no · term: none · `search_added` 0 · `search_breed_urls` 0 · `search_adverts` n/a (no `--search`) · `home_added` 0 · `map_list` 13 · scrapes 2 · credits 3 of a ceiling of 8.
- The first map (limit 500) returned 13 URLs (`url_count`), well under the cap. One of them is a breed URL (`breed_urls` 1, `/the-blue-stafford`), so the Map list script did not ask for a search map (`search_map` false, `search_term` null), and none ran.
- The homepage's own links added no breed page (`home_added` 0), so `map_list` is 13.
- Scrapes: the homepage (markdown and raw HTML) and `/puppies` (markdown). Credits: 1 map + 2 scrapes = 3.
- No URL in the map has a digit-then-letter slug, so the known advert-classifier gap did not arise here. The one listing page was picked normally.

## Key insight
Exodusbulls ranks for "blue staffy breeder" as a champion stud-dog kennel, not a puppy seller. Its only buyer page is a waiting-list form that passes enquiries to other breeders who have used its studs. The two fetched pages have no H1 or H2 headings and no alt text, and the site has no structured data, posts or city pages. BSUK can outrank it on buyer searches with real puppy, price and city pages that carry the same health-test and Kennel Club proof under proper headings.
