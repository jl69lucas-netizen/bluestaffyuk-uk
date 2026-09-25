# Petify — competitor intel

- Root domain: petify.uk · tier 2 (a UK all-pet advert board and app for dogs and cats: sales, adoptions and studs, open to private and licensed breeders and rescues) · analysed 2026-09-25. This is the first report for this entry.
- Homepage gate: passed. The status was 200, the final URL stayed on petify.uk (`www.petify.uk`), and the page was the live homepage, not a bot check or a parked page.
- Key pages, as the classifier picked them from the Map list. It flags the site as a `marketplace`, because the map holds whole cat sections (kittens for sale, cats for adoption, cats for stud).
  - Listing slot: the Staffy stud hub (`/dogs-for-stud/staffordshire-bull-terrier`). The site has three Staffy hubs with no id in the path: sale, adoption and stud. The classifier ranks them by the shortest path, and the stud hub has the shortest.
  - Price-or-FAQ slot: none. No URL in the Map list has a price or FAQ word in its path.
  - Guide slot: none. No guide URL is in the Map list. The homepage's articles sit under `/article/<slug>`, and none of them is in either map.
  - City slot: none. Every Staffy town page (`/puppies-and-dogs-for-sale/staffordshire-bull-terrier/in/<town>/<id>`) ends in a numeric id, so the key-page test counts it as an advert, and an advert is kept out of every slot but the listing. On a marketplace, the city slot takes only the breed's pages.
  - About slot: none. The homepage footer links an about page, but it is not in the Map list, and only breed links join the list from the homepage.
- Breed check before scraping: the one pick names the breed (`staffordshire-bull-terrier`) in its path, so no slot was skipped.
- The first map is saved at `maps/petify.json` (164 URLs), the search map at `maps/petify.search.json` (95 URLs) and the homepage raw HTML at `maps/petify.home.html`.

## Trust
The fetched pages give buyers no proof about any seller or dog.
- No council licence is shown, and there is no Kennel Club mention, no named health test, no vet check and no breeding-since claim. The homepage says only, in general terms, that the board serves both domestic and licensed breeders.
- `town`: null. The site is a national board with no base town.
- Phone and email: the homepage measures script found no phone and no email in the homepage raw HTML (`contact_source` raw-html). A customer-service address sits only inside the JSON-LD, which does not count as shown. The footer links a contact page, which was not fetched.
- `reviews_shown`: 0. No customer review or testimonial text is on the pages fetched. There is no star rating or review badge either.

## Content
- Homepage: 1,035 words (by script). It has 9 H2s, counted from the raw HTML, because the markdown carries the article headings as bold link text.
- What the homepage holds:
  - a one-line pitch for the board and its app;
  - two featured adverts, both cats;
  - eight article teasers;
  - long link lists: 30 dog breeds and 30 cat breeds, each for sale, adoption and stud, and 40 "popular cities" for each.
- The Staffy stud hub has 27 words and 0 H2s. It is a search bar and a "no results found" notice with a notify-me button, with no breed text at all.
- `url_count`: 164 (the first map, below the cap).

## Keywords
0 phrases by the run rule. The script ran over the homepage and the stud hub, and no business name needed cutting.
- The homepage names the breed only as menu links in its breed lists, which have no intent or place word beside them.
- The stud hub carries no breed wording in its main content.
- The breed's name appears only in the page titles and meta descriptions, which the run rule does not read here.

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
  - The fetched pages ask visitors to search, open an advert, download the app, post an advert or tap notify-me.
  - No advert page was fetched, so how a buyer reaches a seller was not seen.
  - The Instagram and Facebook links are follow links, not a way to message a seller.
- `prices_shown`: true. `price_amounts_as_printed`: £400 and £1,350. Both come from the two featured homepage adverts, which are cats. No dog price was printed on the pages fetched.
- `deposit_terms`: null.
- `steps_to_enquire`: null. No enquiry form or message box was on the pages fetched: the homepage form fields are a breed and location search, and the stud hub's button signs up for alerts.
- `urgency_signals`: none. The advert cards show the category, breed, town and price only.

## Technical
- `mobile_layout_ok`: true. The Mobile check evaluate ran in Chrome DevTools, emulating a 375 × 812 phone with a mobile user agent and touch.
- It returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true.
- `lighthouse_performance`: NOT FETCHED (no Lighthouse run).

## Fetch
Fetch: `map_calls` 2 · search map ran: yes · term `staffordshire bull terrier` · `search_added` 65 · `search_breed_urls` 53 · `search_adverts` 90 · `home_added` 1 · `map_list` 230 · scrapes 2 · credits 4 of a ceiling of 8.
- The search map:
  - The first map held 164 URLs (`url_count`), below the cap, and 0 breed URLs (`breed_urls`).
  - The Map list script therefore asked for a search map (`search_map` true, `search_term` "staffordshire bull terrier"), and one ran with a limit of 100.
  - It returned 95 URLs. 30 were already in the first map, which left 65 new URLs (`search_added`).
  - Of those, 53 are breed pages on the site (`search_breed_urls`): the Staffy sale and adoption hubs, Staffy town pages and Staffy adverts.
- 90 of the search map's URLs are adverts by the key-page test (`search_adverts`). The site ends almost every page, town hubs included, with a numeric id segment.
- The homepage links the Staffy sale, adoption and stud hubs. The search map had the first two already, so the stud hub was the one added (`home_added` 1).
- Scrapes: 2, both live (not from cache).
  - the homepage, as markdown and raw HTML;
  - the Staffy stud hub, as markdown.

  The price-or-FAQ, guide, city and about slots were empty.
- Credits spent: 4 (2 maps and 2 scrapes, at 1 credit each).

## Key insight
Petify ranks for a Liverpool Staffy search with an all-pet advert board. Its Staffy hubs are thin search shells: the stud hub listed nothing and carried no breed text, and the site's own pages show no licence, health-test or review proof. BSUK can beat it with a real Liverpool page backed by one breeder's visible proof and a direct way to enquire.
