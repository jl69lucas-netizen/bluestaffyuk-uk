# External link library

Every outside URL a BSUK page is allowed to link to. `scripts/pageboard.py` reads this file
(`library_urls()`), and `validate_board()` refuses any board record whose `links.external`
names a URL that is not recorded here — so a page cannot cite the outside world without the
citation being written down first, and a dead or moved target is fixed in one place.

**Adding a row.** Verify the URL returns 200 *before* you add it, put the date you checked
in the last column, and name the first page that uses it. A row is the URL as it will be
written on the page: `pageboard.normalise_url()` lowercases the host, drops a leading
`www.` and strips a trailing slash before it compares, so one row covers those spellings
and no others. A different path is a different row — `/dog-breeding/…` and
`/media-centre/…` on one host are two destinations, not one.

**Source type.** The last column names what kind of publisher the row is, from one list:
`gov` (a government department, regulator or the legislation site), `registry` (the pedigree
registry), `vet-charity` (a veterinary body or veterinary charity), `welfare` (an animal-welfare
charity or advisory group), `research` (a peer-reviewed study or a university research
programme), `local` (a local council) and `other`. A location, comparison or blog page carries
at least six external links on six distinct domains from at least four of the first six types
(`rules/links.md`, `external-links-six-diverse`); `other` counts toward the six links and six
domains but never toward the four types. `scripts/link_diversity.py` reads this column by its
header name, so a row without a type is reported by `tests/py/test_link_diversity.py`.

**Do not link** to a hosting provider, or to any page that names one (CLAUDE.md rule 2, and
`scripts/marker_check.py` enforces it).

## Rows

| URL | Host | What it is | First page using it | Verified | Source type |
|---|---|---|---|---|---|
| https://ico.org.uk/ | ico.org.uk | The Information Commissioner's Office, the UK's supervisory authority for data protection — where a reader complains if we mishandle their data | `/privacy-policy-uk/` | 2026-09-19 · 200 | gov |
| https://www.gov.uk/data-protection | gov.uk | The government's plain-English summary of UK data protection law and the rights it gives a person | `/privacy-policy-uk/` | 2026-09-19 · 200 | gov |
| https://www.citizensadvice.org.uk/about-us/information/citizens-advice-privacy-policy/ | citizensadvice.org.uk | Citizens Advice, for independent help with a data-protection question we are not the right people to answer | `/privacy-policy-uk/` | 2026-09-19 · 200 | other |
| https://policies.google.com/privacy | policies.google.com | Google's own privacy policy — what Google Analytics does with what it records on this site | `/privacy-policy-uk/` | 2026-09-19 · 200 | other |
| https://www.thekennelclub.org.uk/ | thekennelclub.org.uk | The Kennel Club, the UK pedigree registry our litters are registered with | `/privacy-policy-uk/` | 2026-09-19 · 200 | registry |
| https://www.thekennelclub.org.uk/dog-breeding/dog-breeding-regulations/ | thekennelclub.org.uk | The Kennel Club's guidance on the regulations a UK breeder works under | `/thank-you-blue-staffy-puppies-journey/` | 2026-09-19 · 200 | registry |
| https://www.thekennelclub.org.uk/media-centre/2025/january/responsible-breeding-bolstered-by-new-registrations-structure/ | thekennelclub.org.uk | The Kennel Club on its registrations structure and responsible breeding | `/uk-blue-staffy-breeders-contact/` | 2026-09-19 · 200 | registry |
| https://www.gov.uk/bring-pet-to-great-britain | gov.uk | The official rules for bringing a pet into Great Britain, for a buyer arranging transport | `/thank-you-blue-staffy-puppies-journey/` | 2026-09-19 · 200 | gov |
| https://www.royalkennelclub.com/search/breeds-a-to-z/breeds/terrier/staffordshire-bull-terrier/ | royalkennelclub.com | The registry's own Staffordshire Bull Terrier breed page — the breed standard and what a registration covers, in the registry's words rather than ours | `/blue-staffy-uk-breeders/` | 2026-09-20 · 200 | registry |
| https://crufts.org.uk/ | crufts.org.uk | Crufts, the UK breed show the migrated about page names as where the breed is celebrated | `/blue-staffy-uk-breeders/` | 2026-09-20 · 200 | other |
| https://www.rspca.org.uk/adviceandwelfare/pets/dogs/puppy | rspca.org.uk | The RSPCA's puppy advice — independent guidance for a first-time owner, which we are not the right people to give | `/blue-staffy-uk-breeders/` | 2026-09-20 · 200 | welfare |
| https://www.royalkennelclub.com/health-and-dog-care/health-dog-care/health/getting-started-with-health-testing-and-screening/dna-testing/dna-test-l-2hga/ | royalkennelclub.com | The registry's own page for the L-2-HGA DNA test — what the test is and what a clear, carrier or affected result means | `/blue-staffy-health-uk/` | 2026-09-20 · 200 | registry |
| https://www.royalkennelclub.com/health-and-dog-care/health-dog-care/health/getting-started-with-health-testing-and-screening/dna-testing/dna-test-hc-hsf4/ | royalkennelclub.com | The registry's own page for the HC-HSF4 hereditary cataract DNA test, the second of the two the breed is screened for | `/blue-staffy-health-uk/` | 2026-09-20 · 200 | registry |
| https://www.bva.co.uk/canine-health-schemes/eye-scheme/ | bva.co.uk | The British Veterinary Association's eye scheme — the examination that looks for inherited eye disease the HC-HSF4 DNA test does not cover | `/blue-staffy-health-uk/` | 2026-09-20 · 200 | vet-charity |
| https://www.gov.uk/get-your-dog-cat-microchipped | gov.uk | The government's guidance on the microchipping law every puppy leaving us has to satisfy | `/blue-staffy-health-uk/` | 2026-09-20 · 200 | gov |
| https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/other-veterinary-advice/dog-vaccines | pdsa.org.uk | The PDSA's guide to dog vaccinations — independent detail on the second dose and the booster, which are the owner's own vet's | `/blue-staffy-health-uk/` | 2026-09-20 · 200 | vet-charity |
| https://www.royalkennelclub.com/breed-standards/terrier/staffordshire-bull-terrier/ | royalkennelclub.com | The registry's breed standard for the Staffordshire Bull Terrier — the build, head, coat, tail and temperament our breed-facts table describes, in the standard's own words | `/uk-staffordshire-bull-terrier-guide/` | 2026-09-20 · 200 | registry |
| https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/puppies-dogs/medium-dogs/staffordshire-bull-terrier | pdsa.org.uk | The PDSA's veterinary breed page for the Staffordshire Bull Terrier — independent care, exercise, feeding and grooming advice, which we are not the right people to give | `/uk-staffordshire-bull-terrier-guide/` | 2026-09-20 · 200 | vet-charity |
| https://www.gov.uk/control-dog-public/banned-dogs | gov.uk | The government's own list of dog types banned under the Dangerous Dogs Act 1991 — the page behind the statement that the Staffordshire Bull Terrier is not one of them | `/uk-staffordshire-bull-terrier-guide/` | 2026-09-20 · 200 | gov |
| https://www.royalkennelclub.com/your-dog/getting-a-dog/buying-a-dog/questions-for-the-breeder/ | royalkennelclub.com | The registry's own list of questions to ask a breeder before and during a visit — the independent version of the fifteen-question checklist | `/uk-blue-staffy-puppy-buying-guide/` | 2026-09-20 · 200 | registry |
| https://www.rspca.org.uk/adviceandwelfare/pets/dogs/puppy/sales | rspca.org.uk | The RSPCA on spotting a puppy dealer's advert and on finding a good breeder — the independent authority behind the red-flag table | `/uk-blue-staffy-puppy-buying-guide/` | 2026-09-20 · 200 | welfare |
| https://www.bluecross.org.uk/advice/dog/socialising-your-puppy | bluecross.org.uk | The Blue Cross on socialising a puppy — independent advice on what a puppy should meet in its first weeks, which is what our home-raising section describes doing | `/buy-staffy-puppies-for-sale-uk/` | 2026-09-20 · 200 | welfare |
| https://www.rspca.org.uk/adviceandwelfare/pets/dogs/health/puppycare | rspca.org.uk | The RSPCA on caring for a new puppy — the independent version of "what to do in the first weeks", which a listing page should not be the only source of | `/buy-blue-staffy-puppies-uk/` | 2026-09-20 · 200 | welfare |
| https://assets.publishing.service.gov.uk/media/5a819d3bed915d74e623335d/pb10308-dogs-cats-welfare-060215.pdf | assets.publishing.service.gov.uk | The government's welfare-in-transport guidance for dogs and cats (PB10308) — the rules the transport a puppy travels in has to satisfy | `/buy-blue-staffy-puppies-uk/` | 2026-09-20 · 200 | gov |
| https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/puppies-dogs/how-much-exercise-does-your-dog-need | pdsa.org.uk | The PDSA on how much exercise a dog of this size needs — the independent figure behind "an hour a day", which a homepage should not be the source of | `/` | 2026-09-20 · 200 | vet-charity |
| https://www.royalkennelclub.com/health-and-dog-care/health-dog-care/health/getting-started-with-health-testing-and-screening/understanding-canine-genetics/ | royalkennelclub.com | The registry on canine genetics and what a DNA test result tells you — the page behind "DNA tested clear", in the registry's words rather than ours | `/` | 2026-09-20 · 200 | registry |
| https://www.legislation.gov.uk/uksi/2018/486/contents/made | legislation.gov.uk | The Animal Welfare (Licensing of Activities Involving Animals) (England) Regulations 2018 as made — the regulations animal activity licensing in England, dog breeding included, is issued under | none yet — starter row (system-gaps Task 4) | 2026-09-24 · 200 | gov |
| https://www.legislation.gov.uk/uksi/2015/108/contents/made | legislation.gov.uk | The Microchipping of Dogs (England) Regulations 2015 as made — the text of the law the government's microchipping guidance summarises | none yet — starter row (system-gaps Task 4) | 2026-09-24 · 200 | gov |
| https://www.gov.uk/guidance/dog-breeding-licence-england | gov.uk | The government's guidance on the dog breeding licence in England — who needs one, and that the council inspects the premises before it grants one | none yet — starter row (system-gaps Task 4) | 2026-09-24 · 200 | gov |
| https://www.gov.uk/guidance/buying-a-cat-or-dog | gov.uk | The government's advice on buying a cat or dog — what a responsible seller does, including showing a council licence number a buyer can check | none yet — starter row (system-gaps Task 4) | 2026-09-24 · 200 | gov |
| https://www.gov.uk/find-local-council | gov.uk | The government's find-your-local-council tool — how a reader finds the council that licenses breeders where they live | none yet — starter row (system-gaps Task 4) | 2026-09-24 · 200 | gov |
| https://www.cumberland.gov.uk/business-and-licensing/licensing/animal-establishment/animal-activities-licensing | cumberland.gov.uk | Cumberland Council's page on animal activities licensing — dog breeding, boarding and selling animals as pets — the council for Carlisle | none yet — starter row (system-gaps Task 4) | 2026-09-24 · 200 | local |
| https://www.cumberland.gov.uk/business-and-licensing/licensing/animal-establishment/animal-welfare-licence-register | cumberland.gov.uk | Cumberland Council's register of the businesses in its area that hold an animal welfare licence, with each one's star rating | none yet — starter row (system-gaps Task 4) | 2026-09-24 · 200 | local |
| https://www.dogstrust.org.uk/dog-advice/getting-dog/breeds/staffordshire-bull-terrier | dogstrust.org.uk | Dogs Trust's Staffordshire Bull Terrier breed page — a rehoming charity's own account of the breed | none yet — starter row (system-gaps Task 4) | 2026-09-24 · 200 | welfare |
| https://paag.org.uk/ | paag.org.uk | The Pet Advertising Advisory Group's how-to-buy-a-pet advice — independent guidance for a buyer answering an online pet advert | none yet — starter row (system-gaps Task 4) | 2026-09-24 · 200 | welfare |
| https://pmc.ncbi.nlm.nih.gov/articles/PMC7510130/ | pmc.ncbi.nlm.nih.gov | Pegram, Wonham, Brodbelt, Church and others, "Staffordshire Bull Terriers in the UK: their disorder predispositions and protections" (Canine Medicine and Genetics, 2020) — a study of anonymised VetCompass veterinary records, open access on PubMed Central | none yet — starter row (system-gaps Task 4) | 2026-09-24 · 200 | research |
| https://www.royalparks.org.uk/sites/default/files/2025-12/Dogs%20In%20The%20Royal%20Parks.pdf | royalparks.org.uk | The Royal Parks' own "Dogs in the Royal Parks" rules — where dogs may not go and where they must be on a lead in Hyde Park, Kensington Gardens, The Regent's Park and Primrose Hill, Richmond Park and Greenwich Park | `/uk-locations/blue-staffy-puppies-london/` | 2026-10-03 · 200 | other |
| https://www.cityoflondon.gov.uk/things-to-do/green-spaces/hampstead-heath/activities-at-hampstead-heath/dog-walking-at-hampstead-heath | cityoflondon.gov.uk | The City of London Corporation on dog walking at Hampstead Heath — control, recall, clearing up and the professional dog-walker licence | `/uk-locations/blue-staffy-puppies-london/` | 2026-10-03 · 200 | local |
| https://www.cityoflondon.gov.uk/things-to-do/green-spaces/epping-forest/activities-in-epping-forest/dog-walking-in-epping-forest | cityoflondon.gov.uk | The City of London Corporation's Dog Walking Code of Conduct for Epping Forest — effective control, recall and wildlife and livestock | `/uk-locations/blue-staffy-puppies-london/` | 2026-10-03 · 200 | local |
| https://www.enfield.gov.uk/__data/assets/pdf_file/0017/110078/PSPO-3-Dog-control-on-lead-at-all-times-Community-safety.pdf | enfield.gov.uk | Enfield Council's Public Spaces Protection Order 3 (from 23 October 2025) — the parks where dogs must be on a lead at all times, the Trent Country Park Water Garden among them | `/uk-locations/blue-staffy-puppies-london/` | 2026-10-03 · 200 (headless fetch; plain curl 403) | local |
| https://www.enfield.gov.uk/services/leisure-and-culture/parks | enfield.gov.uk | Enfield Council's general park information page — its park byelaws, Trent Park's own among them, and its dog notices | `/uk-locations/blue-staffy-puppies-london/` | 2026-10-03 · 200 (headless fetch; plain curl 403) | local |
| https://www.sutton.gov.uk/libraries-museums-parks-and-leisure/parks-trees-and-open-spaces/parks-and-facilities/oaks-park | sutton.gov.uk | The London Borough of Sutton's Oaks Park page — its dog-free picnic area | `/uk-locations/blue-staffy-puppies-london/` | 2026-10-03 · 200 | local |
| https://www.sutton.gov.uk/libraries-museums-parks-and-leisure/parks-trees-and-open-spaces/parks-and-facilities/overton-park | sutton.gov.uk | The London Borough of Sutton's Overton Park page — a recreation ground where dogs are not permitted, guide dogs excepted | `/uk-locations/blue-staffy-puppies-london/` | 2026-10-03 · 200 | local |
| https://www.rcvs.org.uk/animal-owners/find-a-vet | rcvs.org.uk | The Royal College of Veterinary Surgeons' Find a Vet search — the official register a buyer uses to find a registered vet near them and check that a vet is registered; we name no practice | `/uk-locations/blue-staffy-puppies-london/` | 2026-10-03 · 200 | vet-charity |
| https://maps.google.com/maps?q=London%2C%20UK&z=10&hl=en&t=m&output=embed&iwloc=near | maps.google.com | Google Maps, the London city centre at zoom 10, as a tap-to-load embed (an iframe, not a citation): it shows where the buyer is, never where we are | `/uk-locations/blue-staffy-puppies-london/` | 2026-10-06 · 301 → 200 (www.google.com/maps/embed) | other |

## Provenance

Every row above is a URL the migrated WordPress body already carried on the page named in
"First page using it"; none is a new citation invented for the rebuild. The first eight were
re-checked on 2026-09-19 and returned 200 following redirects; the three added on 2026-09-20
for `/blue-staffy-uk-breeders/` were checked the same way on that date. The five added on
2026-09-20 for `/blue-staffy-health-uk/` were checked the same way again, and two of them are
written at the URL the check RESOLVED to rather than at the migrated body's spelling:
`https://www.gov.uk/get-your-dog-microchipped` 301s to `get-your-dog-cat-microchipped`, and
the PDSA's `/looking-after-your-pet/puppies-dogs/vaccinating-your-dog` 301s into the pet health
hub. The two registry DNA-test pages are not in the migrated body as URLs; the body cites the
registry for "Staffordshire Bull Terrier genetic health" through a search-engine wrapper and a
shop page, and the scan (sbtpedigree, Bullscaff, Willaby) is what justifies citing the test
itself instead. The shop page and the wrapper are logged in the health record's
`dropped.links`.

Two of the three are written here at the URL the check RESOLVED to, not at the spelling the
migrated body used, because in both cases the old spelling is a redirect to a row rather than a
destination of its own:

- The registry's breed page was linked as
  `https://www.thekennelclub.org.uk/search/breeds-a-to-z/breeds/terrier/staffordshire-bull-terrier/`
  and 301s to `royalkennelclub.com`. The three `thekennelclub.org.uk` rows above still resolve
  under that host and are left as they are; a rename is one migration, not eight edits made
  from one observation.
- `https://www.gov.uk/take-pet-abroad`, which the migrated about page used as its
  pet-transport citation, redirects to `https://www.gov.uk/bring-pet-to-great-britain` — already a row. It
  gets no row of its own, and the about record logs the old spelling under `dropped.links`.

The three added on 2026-09-20 for `/uk-staffordshire-bull-terrier-guide/` were checked the same
way. Two are written at a URL the migrated body did not carry as a URL at all: the body linked
the registry's breed page, the RSPCA's socialisation advice, the PDSA's vaccination advice and
the Dangerous Dogs Act guidance through `google.com/search?q=` WRAPPERS, and two of the wrapped
paths (`gov.uk/control-dog-public-place/dangerous-dogs` and
`rspca.org.uk/…/dogs/training/socialisation`) 404 today. The banned-dogs row is the government's
own list at the path that resolves; the breed standard is a new citation for the breed-facts
table, justified by the scan (three of the four pages read open on a facts panel). All four
wrappers are logged in the guide record's `dropped.links`.

The two added on 2026-09-20 for `/uk-blue-staffy-puppy-buying-guide/` were checked the same way.
The registry's questions-for-the-breeder page is written at the `royalkennelclub.com` spelling
the migrated body's `thekennelclub.org.uk` path 301s to; the RSPCA's puppy-sales page is a new
citation for the red-flag table, justified by the scan (neither that page nor the PDSA's
puppy-farm page lays the two columns side by side). The migrated body's own pet-travel link
redirects to the government's international travel page, which does not describe a domestic
delivery, so it is logged in the buying guide record's `dropped.links` rather than given a row.

The one added on 2026-09-20 for `/buy-staffy-puppies-for-sale-uk/` is a URL the migrated body
already carried, and it was re-checked that day. The Blue Cross socialisation page answers a
plain `curl` with 403 — the site's bot filter, not a dead page — so it was checked through a
headless browser instead and returned 200 at the same URL; that is the only row in this table
whose check needed one until the London rows below.

The eight added on 2026-10-03 for `/uk-locations/blue-staffy-puppies-london/` are the London places block and its vet line (answer board 2026-10-03-london-board-revision q04, q06), each the source a fact in `data/city-places/blue-staffy-puppies-london.json` is quoted from. Six returned 200 to `curl` that day. Enfield Council's two answer a plain `curl` with 403, the site's bot filter, so they were checked through a headless fetch instead and returned 200 at the same URLs.

The one added on 2026-10-06 for `/uk-locations/blue-staffy-puppies-london/` is the London map (answer board 2026-10-06-london-map q01, q02): a Google Maps embed of the city centre, built from `data/locations.json` `city`, which the page loads only when the reader taps "Show the map" (`src/components/kit/CityMapFacade.astro`). It is an embed, not a citation, so it is typed `other`. `curl` returned 301 to `www.google.com/maps/embed` and then 200 that day.

That board adds no other row. Every other outside URL the migrated body carried is logged in
the record's `dropped.links`: an encyclopaedia entry, two image libraries, a North American
veterinary group, a feed brand, a named courier, a classified site's breeder directory, a
consumer-money site and `https://www.gov.uk/take-pet-abroad`, which redirects to the
government's international pet travel page and does not describe a domestic delivery.

The two added on 2026-09-20 for `/buy-blue-staffy-puppies-uk/` are both URLs the migrated body
already carried, and both were re-checked that day. The RSPCA's `/dogs/health/puppycare` path
is a live destination of its own and not a redirect to the `/dogs/puppy` row above it, so it
gets its own row rather than being folded into that one. The welfare-in-transport PDF is the
document the migrated body linked as "DEFRA's guidance on Transporting your pet (General
Guidance)" and it still resolves at the same URL; it is the first PDF in this table, and
`normalise_url()` treats it as any other path.

That board adds no other row either. The rest of its migrated outbound links are internal
location-cluster pages project 5 owns, two in-page fragments and a self-link, all logged in the
record's `dropped.links`.

The two added on 2026-09-20 for `/` are both URLs the migrated homepage body already carried, and
both were checked that day with a following-redirects request. The PDSA exercise page resolves at
the spelling the body used and gets a row at it. The registry's canine-genetics page was linked as
`https://www.thekennelclub.org.uk/health-and-dog-care/health/getting-started-with-health-testing-and-screening/understanding-canine-genetics/`
under the anchor "Animal Health Trust (now part of the Kennel Club Genetics Centre)", and it 301s
to the `royalkennelclub.com` path recorded above, which is the spelling the row uses — the same
treatment the breed page and the two DNA-test pages already have. The homepage board adds no other
row: its remaining migrated outbound links are two more copies of the registry's breed page
(already a row above) and the RSPCA puppy-care page (already a row above), and everything else it
carried was internal, a fragment, or the map embed of the former address, all logged in
`data/boards/index.json`'s `dropped`.

The ten added on 2026-09-24 are STARTER rows for the pages project 5 builds (system-gaps Task 4):
no page links them yet, so "First page using it" says so, and the first board that cites one
replaces that cell with its route. Each was checked with `curl -sIL` on 2026-09-24 and returned
200 at the URL written, which is the URL a following-redirects request resolved to. They exist
so a location, comparison or blog page can reach six domains and four source types without
inventing a citation: the two legislation rows are the law the government guidance rows
summarise; the Cumberland rows are the licensing authority for Carlisle; the study is a
peer-reviewed UK source on the breed's disorders. A location page for another city adds
that city's own council licensing page as a `local` row when its board is written, checked the
same way.
