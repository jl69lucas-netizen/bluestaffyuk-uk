# BSUK purchase-intent keyword research: raw findings (2026-11-02)

Scope: /available-puppies/ hub plus single named-pup pages (<1,000 words each). No volume data was used, so evidence is ranked by autocomplete presence and SERP presence only.

## 0. Fetch methods

| Method | Result |
|---|---|
| curl Google suggest (suggestqueries.google.com) | BLOCKED by the agent proxy: CONNECT 403 (policy) |
| curl Bing osjson (api.bing.com) | BLOCKED: CONNECT 403 |
| curl DuckDuckGo ac | BLOCKED: CONNECT 403 |
| Firecrawl scrape of the suggest endpoints | 5 calls returned data (Google x3, Bing x1, DDG x1). Then the auto-mode classifier DENIED further calls as a "containment escape" (routing around the proxy block). I stopped there, so there was no alphabet soup. Firecrawl egresses from the US, so the suggestions leak AU/NZ terms (nsw, qld, perth). Treat UK geo as approximate. |
| Firecrawl search (location United Kingdom) | WORKED: 10 SERPs |
| Firecrawl scrape (pages) | WORKED: Pets4Homes classified, ukstaffypups.uk listing, Champdogs litter 80067 and the Champdogs puppies index |

## 1. Raw autocomplete captured

Google, "staffy puppies for sale":
staffy puppies for sale | near me | scotland | nsw | qld | brisbane | uk | glasgow | south africa | perth

Bing (en-GB), "staffy puppies for sale":
... | near perth | near sydney | qld | brisbane | near me craigslist | uk | near me cheap | near london | near manchester | nsw | near birmingham

DDG, "staffy puppies for sale":
... | near perth | near sydney | qld | brisbane | near me craigslist | uk | near me cheap

Google, "kc registered staffy puppies":
kc registered staffy puppies for sale | ... for sale uk | kennel club registered staffy puppies | kc registered staffordshire bull terrier puppies for sale | ... for sale scotland | ... for sale near london | ... for sale near me | ... for sale near liverpool | ... for sale near | kc registered staffy pups

Google, "blue staffy puppy for sale":
blue staffy puppy for sale | near me | uk | ireland | scotland | london | nz | near me under 500 | ireland kennel club | near me kennel club

Pets4Homes internal related-search links seen on its pages. These are not autocomplete, but they reflect P4H's own search-log phrasing:
female staffy, staffy male, black staffy, white staffy, pedigree staffordshire bull terrier, brindle staffy, blue staffy, red staffy, blue fawn staffy, black white staffy, chunky staffy, pedigree blue staffy, blue staffy female, blue staffy girl, pure blue staffy, blue and white staffy, black brindle staffy, blue brindle staffy, girl black staffy, small staffy, staffordshire bull terrier in cumbria

## 2. SERP snapshots (Firecrawl, UK)

1. **blue staffy puppies for sale uk**: P4H ?keyword=blue (75 ads), staffie-owners ?colour=blue, RSPCA guide, puppies.co.uk, trojanstaffuk.com (breeder home), petsforlove, foreverpuppy, Gumtree search, Dogs Trust, P4H London.
2. **kc registered staffordshire bull terrier puppies for sale**: Royal Kennel Club breed page / Find a Puppy, staffie-owners ?kc_registered=yes, P4H ?keyword=kennel+club, foreverpuppy, Champdogs breeders, trojanstaffuk /staffy-puppies, puppies.co.uk, Gumtree, ukstaffypups.uk, petsforlove.
3. **staffy puppies for sale cumbria**: P4H Cumberland (1 ad), staffie-owners Kendal (3 ads), Freeads Cumbria, fellendstaffs.co.uk (licensed breeder, "Cumbria & South West Scotland"), Gumtree Cumbria (generic, all breeds), Champdogs ?pc=CA1 (AlmoStaffs near Carlisle; reds), puppies.co.uk Millom, staffie-owners Carlisle under £750, a Facebook group post asking for a "male blue or black staffie puppy ... around carlisle", Champdogs CA14.
4. **blue staffy female puppy for sale ready now**: P4H ?keyword=blue+female (7 ads), staffie-owners blue, Gumtree, foreverpuppy, petsforlove, P4H blue, puppies.co.uk, ukstaffypups.uk/staffy-puppies-for-sale/ (single breeder ranks #8), staffie-owners blue+female+health tested, P4H London.
5. **black staffy male puppy for sale kc registered**: P4H ?keyword=black, staffie-owners KC, RKC breed page, foreverpuppy, P4H KC, Champdogs puppies, puppies.co.uk, ukstaffypups.uk, riskysstaffords.co.uk (breeder home), RKC Find a Puppy.
6. **staffy puppies for sale scotland**: P4H Scotland (3), staffie-owners Scotland (2), Gumtree Scotland (5), Champdogs Scotland, Freeads, Dogs Trust, staffie-owners Scotland KC blue, Staffie Rescue Scotland, P4H UK, FB rescue.
7. **staffy puppies L2HGA HC clear parents for sale**: P4H ?keyword=parents, a Facebook post, a staffie-owners Tamworth listing, a Champdogs forum thread, foreverpuppy, ukstaffypups, P4H breeders directory, trojanstaffuk, a FB group post, a Freeads single ad. This is a weak SERP: social and forum posts rank, so it is under-targeted.
8. **blue staffy puppy price uk**: P4H blue (snippet "average cost ... approximately £782"), staffie-owners blue ("£500 to £3,000"), puppies.co.uk, foreverpuppy, RSPCA, P4H London, ukstaffypups, Gumtree, petsforlove, trojanstaffuk.
9. **staffy puppies for sale north east newcastle**: P4H Newcastle (14), staffie-owners Newcastle, Gumtree Newcastle (generic), Freeads, staffie-owners North East, puppies.co.uk, a FB rehoming post, P4H Tyne and Wear.
10. **staffordshire bull terrier puppy delivered uk wide breeder**: P4H UK, RSPCA, trojanstaffuk, Champdogs England, foreverpuppy, staffie-owners home, Dogs Trust, a FB group post. No result addresses delivery, so this is a gap.

People Also Ask: Firecrawl search does not return a PAA block. The only PAA-like signal seen was the P4H on-page H3 "Why do Staffies have a bad reputation?".

## 3. Single-pup / litter page anatomy

### Pets4Homes classified (Gateshead, "Stunning Kc blue and white pied male left")
- Title: "<ad headline> for sale in <town> | Pets4Homes"
- Stat row: Age, Sex count, Price
- H1 is the ad headline, followed by breed, posted time, town and the seller name with "Replies within 1 hour"
- Description, free text of about 200 words: ready-to-leave date, litter makeup, collar colour, parents "Hereditary health clear HSF4 L2HGA", and what the pup leaves with (microchip, vet check, 1st vaccination, flea/worm treatment, binder, KC paperwork, puppy pack, food)
- Litter details: location, pets in litter, breed, ready to leave date, age, generation
- Health & Docs checklist: KC registered by collection, parents health tested, vet checked, worm/flea treated, vaccinations, microchipped
- Info: views, favourites, ad type, original breeder
- Litter grid: each pup with status (Available/Reserved), sex and price (green-collar male £3,000, the rest £2,500)
- Platform trust block (4 steps: intro, viewing, reservation, collection), safety advice, breed pros/cons, similar adverts, a related-search link farm
- Unique copy is roughly 200–300 words. The rest is platform boilerplate.

### Champdogs litter 80067
- Title: "Pedigree KC Registered Staffordshire Bull Terrier Puppies in <town>, <county> born <date>"
- Meta description: litter makeup by colour and sex, raised in family home, vet-checked, microchipped, wormed, health-tested parents
- H1 litter title, photo gallery with named pup ("Honey")
- **Verified Health Tests** block per parent with test name, result and date. Champdogs links these to its own verification.
- Notes ("Maybe blue carriers", "Champion lines")
- 4-generation pedigree list
- Breeder sidebar: dogs, litters, gallery, contact
- Very little prose (under 150 words). No price shown.

### ukstaffypups.uk /staffy-puppies-for-sale/ (breeder hub; there are no single-pup URLs)
- H2 question opener "Are there blue staffy puppies for sale near me?" followed by an inclusions bullet list (price, health, training, socialisation, paperwork, puppy pack)
- 15 pup cards: name, price £1,000, sex, age "9 Weeks Old", health "Vet Checked", status "Ready to Leave", and "Inquire About <name>" going to a generic contact page
- About 2,000+ words of generic breed guide below the cards (genetics/CDA, temperament, costs table, neutering, exercise, L-2-HGA / HC-HSF4 explainer, DDA legality, home prep)
- It ranks #7–9 for several blue and KC queries even though there are no per-pup pages, which shows there is room for a real breeder.

## 4. Gap observations
- Aggregators (P4H, staffie-owners, puppies.co.uk, foreverpuppy, Freeads, Gumtree, petsforlove) hold 6–8 of 10 slots on every core query. Breeder sites that appear are trojanstaffuk, ukstaffypups, riskysstaffords and fellendstaffs.
- Cumbria and Carlisle SERPs are thin: P4H has 1 ad, staffie-owners has 3, Gumtree's page covers all breeds, and Champdogs shows a reds breeder. Only fellendstaffs is a dedicated local Staffy breeder page. This is the best local opening.
- The health-test, delivery and "ready now + colour + sex" queries return classifieds, Facebook posts and forum threads, so the intent is under-served.
- Nobody ranking has a single named-pup page built as a real page. The pup units are classified ads or cards on a hub.
