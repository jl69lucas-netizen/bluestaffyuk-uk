# PDSA — competitor intel

- Root domain: pdsa.org.uk · tier 3 (veterinary charity) · analysed 2026-09-25. This is the first report for this entry. The classifier now puts the breed's pages first, keeps adverts out of the key pages, and picks an about page only when a whole path segment is an about word (commits 4e2fe7f, b8fb193 and 50e1498).
- Homepage gate: passed. The status was 200, the final URL stayed on pdsa.org.uk, and there was no bot check.
- Fetched: 1 map (limit 500), which returned **473 URLs**. The list is saved as JSON in the session scratchpad (`maps/pdsa.json`), so it can be re-typed later without spending credits. Then 5 scrapes:
  1. the homepage, with markdown and raw HTML (served from Firecrawl's cache, cached 2026-09-24);
  2. the Staffordshire Bull Terrier breed page (listing slot). Its path holds `puppies-dogs`, so the table types it as a listing, and the breed step picks it first;
  3. the cost-of-owning-a-dog page (price-or-FAQ slot);
  4. the crate-training guide (guide slot);
  5. the Manchester Terrier breed page (city slot). The table types it as `city` only because `manchester` is a whole word in its path.

  The about slot was `null`: the only about-typed URL is a kitten page whose slug has "about" in the middle, and that is never picked. The phone check and a JSON-LD read ran in an emulated phone in Chrome DevTools. **6 Firecrawl credits in all** (1 map and 5 scrapes), inside the ceiling of 7.
- Saved scrapes: the key pages' markdown was saved to scratch files with link targets left out, so headings, words and phrases could be counted by script. The homepage markdown and raw HTML were saved in full.

## Trust
This is a vet charity's trust, not a breeder's. The homepage footer shows registered charity numbers (recorded as a yes, `registered_charity_number_shown`), along with a Fundraising Regulator badge and a Data and Marketing Association badge. The Staffy page advises buyers to check the parents' health screening. It names the BVA/Kennel Club hip dysplasia scheme and the BVA eye scheme, and it lists L-2-HGA as a condition the breed can have, though not as a test. It recommends Kennel Club Assured Breeders in three places (recorded as `kc_assured_breeder_recommended`). That is advice on where to buy, so it is not recorded as a KC registration mention. The page also tells buyers to make sure a puppy has had health checks and vaccinations, which is recorded as a vet-check mention. There is no council licence, no breeding-since claim and no base town on the pages fetched. The homepage measures script (raw HTML) found no phone number and no email. Reviews: 0. The review list in scratch is empty, and `grep -c .` gives 0. No customer or supporter testimonial appears on any fetched page.

## Content
The homepage has 487 words by script and 4 H2s. Most of the words are the navigation menu, printed twice. The page leads with a gifts-in-Wills appeal, then a donation form, a services link, fireworks advice, the charity lottery, the pet store and pet insurance. The Staffy page (10 H2s) is a thorough vet-written breed profile. It has a key-facts table, then sections on breed health risks, temperament, training, separation anxiety, exercise, grooming, children and other pets, and feeding. It ends with a cost-of-ownership section and a section on where to get a Staffy, which puts rescue first and then a breeder, with checks to make. The cost page (4 H2s) sets out minimum set-up, monthly and lifetime costs by dog size and explains how they were worked out. The crate guide (9 H2s) is a step-by-step training guide with a short FAQ. The Manchester Terrier page (7 H2s) is a shorter breed profile in the same template. The map returned 473 URLs, under the 500 cap, but that is still only a sample of a much larger site. Its Pet Health Hub alone accounts for 141 of the mapped URLs (counted by script).

## Keywords
Three phrases by the run rule, all from the Staffy page and found by script: `staffordshire bull terrier puppy`, `staffordshire bull terrier puppies` and `staffie to go to puppy`. The last one is a run-rule artefact from a sentence about puppy socialisation classes. No fetched page other than the Staffy page names the breed (checked by script), and no phrase needed a name cut.

## Page types
By script over the 473-URL map, with no `--post-folder`: listing 181, health 150, care-guide 18, breed-guide 5, faq 4, blog 3, price 3, contact 2, about 1 and city 1.
- The large listing count comes from the `puppies-dogs` folder, whose breed profiles and puppy-care pages all match `puppies`. PDSA has no sale adverts.
- The one city page is the Manchester Terrier breed page. It is a false positive of the table, and the page is not about the city.
- The one about page is a kitten page whose slug contains the word "about".

## Blog
2 posts by the classifier, both under `what-we-do/blog`. The third blog-typed URL is a press release in the press office's latest-news folder. Its folder segment is not a whole blog word, so it is not counted as a post. The map has no post sitemap and no dated post URL. Posts without a blog base or a date are missed, and the table counted them as it found them. Topics, sampled word counts and posting frequency are NOT FETCHED: no post was among the key pages, and the map holds no dated post URL.

## Visual
The homepage has 8 distinct images (homepage measures script, raw HTML, sources resolved against the homepage URL). 6 of them have no alt text or an empty one, so the most common alt class is missing. The raw HTML has no `<video>` tag and no YouTube or Vimeo embed. The Staffy page has a nine-photo gallery of Staffies, but only the homepage images are counted here.

## Schema
None. The homepage raw HTML holds no JSON-LD, and a JSON-LD read in the emulated phone returned an empty list.

## Cities
None. No `data/locations.json` city is named as a place on the fetched pages. The word Manchester appears only as part of the dog breed's name on the Manchester Terrier page. The table typed that page as a city, but it names no place, so no city is recorded. This was the reader's call, and the controller may overrule it.

## Conversion
The pages fetched never ask a buyer to buy a dog. The Staffy page puts adopting a Staffy from a rescue centre first, then gives checks for buying from a breeder. It warns that unusually cheap puppies may come from puppy farms. The only forms on the homepage are the site search and two donation forms with preset amounts (`form`). None of them is an enquiry form for an animal, so steps to enquire is null. Other asks lead to a pet insurance quote, the charity lottery and the pet store. The amounts printed are donation amounts, a lottery prize and cost-of-ownership estimates. No animal is priced, so `prices_shown` is false and no amounts are recorded. There are no deposit terms and no urgency signals.

## Technical
The check ran in an emulated phone in Chrome DevTools (375 × 812 viewport, mobile user agent, touch). With the homepage loaded, the mobile-check evaluate returned innerWidth 375, clientWidth 375, scrollWidth 375, screenWidth 375, maxTouchPoints 1 and mobileUA true, so `mobile_layout_ok` is true. Lighthouse is NOT FETCHED (no Lighthouse run).

## Key insight
PDSA ranks with a vet-written Staffy breed page. The page covers health risks, care, monthly and lifetime running costs, and where to get a dog. But it sells no puppy, prices no puppy, carries no schema and names no city. BSUK can match that health and cost-of-ownership depth on its own Staffy pages and then win the buying intent PDSA leaves open, with a named breeder's health-tested litters, a stated price and a direct way to enquire.
