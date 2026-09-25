# Petify — competitor intel

- Root domain: petify.uk · tier 2 (a UK all-pet advert board and app for dogs and cats: sales, adoptions and studs, open to private and licensed breeders and rescues) · analysed 2026-09-25. This report replaces the one written earlier today: it is a consistency top-up under the final classifier rules (committed at 9d7e7b9), which changed two key-page picks.
- Homepage gate: passed. The status was 200, the final URL stayed on petify.uk (`www.petify.uk`), and the page was the live homepage, not a bot check or a parked page.
- Key pages, as the classifier picked them from the Map list. It flags the site as a `marketplace`, because the map holds whole cat sections (kittens for sale, cats for adoption, cats for stud).
  - Listing slot: the Staffy sale hub (`/puppies-and-dogs-for-sale/staffordshire-bull-terrier`). The site has three Staffy hubs with no id in the path: sale, adoption and stud. Under the final rules a sale hub ranks before a stud board or an adoption page, so the sale hub replaces the stud hub picked earlier today.
  - Price-or-FAQ slot: none. No URL in the Map list has a price or FAQ word in its path.
  - Guide slot: none. No guide URL is in the Map list. The homepage's articles sit under `/article/<slug>`, and none of them is in either map.
  - City slot: the Staffy London town hub (`/puppies-and-dogs-for-sale/staffordshire-bull-terrier/in/london/147724`). A town after an `in` segment followed by its number is now a numbered town hub, not an advert, so the Staffy town pages can fill the city slot. The adoption town hubs rank after the sale ones, and among the Staffy sale town hubs whose town is a `data/locations.json` city, London's has the shortest path. Earlier today this slot was empty.
  - About slot: none. The homepage footer links an about page, but it is not in the Map list, and only breed links join the list from the homepage.
- Breed check before scraping: both new picks name the breed (`staffordshire-bull-terrier`) in their path. The stud hub scraped earlier today is no longer a pick, so it has left this report.
- The first map is saved at `maps/petify.json` (164 URLs), the search map at `maps/petify.search.json` (95 URLs) and the homepage raw HTML at `maps/petify.home.html`.

## Trust
The site itself gives buyers no proof about any seller or dog. The only proof on the pages fetched is what single sellers write in their advert cards.
- No council licence is shown, and there is no named health test and no breeding-since claim. The homepage says only, in general terms, that the board serves both domestic and licensed breeders.
- `kc_registration_mentioned`: true. One Staffy advert card, shown on both the sale hub and the London hub, says its puppies leave Kennel Club registered, and the card carries a Kennel Club label.
- `vet_checks_mentioned`: true. Both Staffy advert cards on the hubs mention a vet: one says its puppies are vet checked, and the other lists a full veterinary health check among what each puppy leaves with. That is a general check, not a named health test, so `health_tests_named` stays empty.
- `town`: null. The site is a national board with no base town.
- Phone and email: the homepage measures script found no phone and no email in the homepage raw HTML (`contact_source` raw-html). A customer-service address sits only inside the JSON-LD, which does not count as shown. The footer links a contact page, which was not fetched. The two hubs show no phone number or email either.
- `reviews_shown`: 0. No customer review or testimonial text is on the pages fetched. There is no star rating or review badge either. The advert cards are sellers' own descriptions, not reviews.

## Content
- Homepage: 1,035 words (by script). It has 9 H2s, counted from the raw HTML, because the markdown carries the article headings as bold link text.
- What the homepage holds:
  - a one-line pitch for the board and its app;
  - two featured adverts, both cats;
  - eight article teasers;
  - long link lists: 30 dog breeds and 30 cat breeds, each for sale, adoption and stud, and 40 "popular cities" for each.
- The Staffy sale hub has no H1 and 0 H2s in its markdown. It is a search bar and a results list of four advert cards, with a slot marked for advertising. Only two of the four cards are Staffy litters, both in London. The other two are mixed-breed dogs in Salisbury. The hub has no breed text of its own.
- The Staffy London hub also has no H1 and 0 H2s. It shows the same four cards sorted by distance, with the two Salisbury cards marked as 79 miles away.
- `url_count`: 164 (the first map, below the cap).

## Keywords
1 phrase by the run rule: `staffordshire bull terrier puppies`. The script ran over the homepage, the Staffy sale hub and the Staffy London hub, and no business, kennel or person's name needed cutting.
- The phrase comes from a Staffy advert card's own text, which both hubs show. Run page by page, the homepage gives none and each hub gives this one.
- The homepage names the breed only as menu links in its breed lists, which have no intent or place word beside them.
- The hubs' own words are search controls. Their titles and meta descriptions name the breed with "puppies and dogs for sale" and the town, but the run rule does not read titles here.

## Page types
By script over the Map list (230 URLs): listing 118 and city 80. The other 32 URLs match no row and are not counted.
- Listing: sale, adoption and stud hubs for breeds and towns; single adverts under `/for-sale/<breed>-dogs|cats/<town>/<id>`; the three Staffy hubs (sale, adoption and stud).
- City: town search pages and adverts whose slug holds a `data/locations.json` place. Many of these are cat pages.
- No guide, FAQ, price, about or blog URL is in either map.

## Blog
- `post_count`: 0, and `post_folder` is null.
  - The homepage links eight articles under `/article/<slug>` and an `/articles` index.
  - Neither map returned any of them, and homepage links join the list only when they are breed paths.
  - So the posts are missed by this run, not absent from the site. Naming `article` with `--post-folder` would still count 0, since no such URL is in the list.
- The teasers cover pet-care topics for dogs and cats (training, treats, spotting illness, introducing dogs, puppy farming, heat in cats). None is about the breed.
- `topics`, `posting_frequency` and `sampled_word_counts`: NOT FETCHED. No post was a key page, and no post URL with a date is in the list.

## Visual
- 14 distinct images on the homepage (by script), mostly with descriptive alts and 0 missing.
- The images are app-store badges, app screenshots, two advert photos and the article photos.
- No video tag and no YouTube or Vimeo embed.

## Schema
WebSite, ItemList, SiteNavigationElement, Organization, ImageObject and ContactPoint. They come from one JSON-LD graph in the homepage raw HTML, which describes the site, its main navigation and the company.

## Cities
24 `data/locations.json` places are named on the fetched pages or have a page in the Map list: Aberdeen, Birmingham, Bristol, Cardiff, Cornwall, Coventry, Dundee, Edinburgh, Essex, Glasgow, Hull, Inverness, Leeds, Leicester, Liverpool, London, Manchester, Middlesbrough, Nottingham, Oxford, South Yorkshire, Sunderland, Wolverhampton and York.
- The homepage's "popular cities" lists name 18 of them: Aberdeen, Birmingham, Bristol, Cardiff, Coventry, Edinburgh, Glasgow, Hull (listed as Kingston upon Hull), Leeds, Leicester, Liverpool, London, Manchester, Nottingham, Oxford, Sunderland, Wolverhampton and York.
- Dundee, Inverness and Middlesbrough have pages in the Map list only. The Middlesbrough page is a Staffy town page.
- Cornwall, Essex and South Yorkshire come from the county part of town slugs, such as a St Austell, Cornwall Staffy page or a Doncaster, South Yorkshire Staffy page.
- The Staffy hubs in the search map reach Leeds, Leicester, London, Manchester, Middlesbrough, Nottingham and the Sheffield, Doncaster and Rotherham pages. Liverpool, the city this entry ranks for, has a Staffy advert in the search map but no Staffy town page in either map.
- Newcastle upon Tyne is a different city from Newcastle-under-Lyme, so it was not counted.

## Conversion
- `cta_types`: none recorded.
  - The fetched pages ask visitors to search, save a search, open an advert, download the app or post an advert.
  - The hubs link each card to its advert page, which was not fetched, so how a buyer reaches a seller was not seen. One card asks buyers to get in touch without naming a channel.
  - The Instagram and Facebook links are follow links, not a way to message a seller.
- `prices_shown`: true. `price_amounts_as_printed`: £300, £400, £599, £750, £800 and £1,350.
  - £400 and £1,350 come from the two featured homepage adverts, which are cats.
  - £599 and £750 are the two Staffy litters on the hubs, and £800 is each mixed-breed card. The hubs print a space after the pound sign.
  - £300 is a deposit named in one Staffy card.
- `deposit_terms`: the site states none, and each seller sets their own. One Staffy card, shown on both hubs, asks a refundable £300 deposit to hold a chosen puppy until collection or handover.
- `steps_to_enquire`: null. No enquiry form or message box was on the pages fetched. The homepage and hub form fields are a breed, category and location search.
- `urgency_signals`: `ready-date`. Every card carries a ready-to-leave label, and one Staffy card says its puppies are ready in two days. No card says few are left, and there is no countdown or sold badge.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran again in this run in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch.
- It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
Fetch: `map_calls` 2 · search map ran: yes · term `staffordshire bull terrier` · `search_added` 65 · `search_breed_urls` 53 · `search_adverts` 33 · `home_added` 1 · `map_list` 230 · scrapes 4 today (2 in this top-up) · credits 6 of a ceiling of 8.
- The search map (run earlier today, reused here at no cost):
  - The first map held 164 URLs (`url_count`), below the cap, and 0 breed URLs (`breed_urls`).
  - The Map list script therefore asked for a search map (`search_map` true, `search_term` "staffordshire bull terrier"), and one ran with a limit of 100.
  - It returned 95 URLs. 30 were already in the first map, which left 65 new URLs (`search_added`).
  - Of those, 53 are breed pages on the site (`search_breed_urls`): the Staffy sale and adoption hubs, Staffy town hubs and Staffy adverts.
- 33 of the search map's URLs are adverts by the key-page test (`search_adverts`). The earlier report said 90, because the old test also counted the numbered town hubs (`/in/<town>/<number>`) as adverts. The final rules read them as hubs.
- The homepage links the Staffy sale, adoption and stud hubs. The search map had the first two already, so the stud hub was the one added (`home_added` 1).
- Scrapes, all live (not from cache):
  - earlier today: the homepage, as markdown and raw HTML (reused here), and the Staffy stud hub, as markdown (no longer a pick, so it has left the report);
  - in this top-up: the Staffy sale hub and the Staffy London hub, as markdown.

  The price-or-FAQ, guide and about slots were empty.
- Credits spent: 6 today (2 maps and 4 scrapes, at 1 credit each). This top-up spent 2 of them: the two new hub scrapes. The maps and the homepage were reused from the earlier run.

## Key insight
Petify ranks for a Liverpool Staffy search with an all-pet advert board. Its Staffy sale and London hubs are bare results lists, with four cards, two of them mixed-breed dogs from another town, and no breed text or proof of the site's own: no licence, no health test and no reviews. BSUK can beat it with a real Liverpool page backed by one breeder's visible proof and a direct way to enquire.
