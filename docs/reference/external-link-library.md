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

**Do not link** to a hosting provider, or to any page that names one (CLAUDE.md rule 2, and
`scripts/marker_check.py` enforces it).

## Rows

| URL | Host | What it is | First page using it | Verified |
|---|---|---|---|---|
| https://ico.org.uk/ | ico.org.uk | The Information Commissioner's Office, the UK's supervisory authority for data protection — where a reader complains if we mishandle their data | `/privacy-policy-uk/` | 2026-09-19 · 200 |
| https://www.gov.uk/data-protection | gov.uk | The government's plain-English summary of UK data protection law and the rights it gives a person | `/privacy-policy-uk/` | 2026-09-19 · 200 |
| https://www.citizensadvice.org.uk/about-us/information/citizens-advice-privacy-policy/ | citizensadvice.org.uk | Citizens Advice, for independent help with a data-protection question we are not the right people to answer | `/privacy-policy-uk/` | 2026-09-19 · 200 |
| https://policies.google.com/privacy | policies.google.com | Google's own privacy policy — what Google Analytics does with what it records on this site | `/privacy-policy-uk/` | 2026-09-19 · 200 |
| https://www.thekennelclub.org.uk/ | thekennelclub.org.uk | The Kennel Club, the UK pedigree registry our litters are registered with | `/privacy-policy-uk/` | 2026-09-19 · 200 |
| https://www.thekennelclub.org.uk/dog-breeding/dog-breeding-regulations/ | thekennelclub.org.uk | The Kennel Club's guidance on the regulations a UK breeder works under | `/thank-you-blue-staffy-puppies-journey/` | 2026-09-19 · 200 |
| https://www.thekennelclub.org.uk/media-centre/2025/january/responsible-breeding-bolstered-by-new-registrations-structure/ | thekennelclub.org.uk | The Kennel Club on its registrations structure and responsible breeding | `/uk-blue-staffy-breeders-contact/` | 2026-09-19 · 200 |
| https://www.gov.uk/bring-pet-to-great-britain | gov.uk | The official rules for bringing a pet into Great Britain, for a buyer arranging transport | `/thank-you-blue-staffy-puppies-journey/` | 2026-09-19 · 200 |
| https://www.royalkennelclub.com/search/breeds-a-to-z/breeds/terrier/staffordshire-bull-terrier/ | royalkennelclub.com | The registry's own Staffordshire Bull Terrier breed page — the breed standard and what a registration covers, in the registry's words rather than ours | `/blue-staffy-uk-breeders/` | 2026-09-20 · 200 |
| https://crufts.org.uk/ | crufts.org.uk | Crufts, the UK breed show the migrated about page names as where the breed is celebrated | `/blue-staffy-uk-breeders/` | 2026-09-20 · 200 |
| https://www.rspca.org.uk/adviceandwelfare/pets/dogs/puppy | rspca.org.uk | The RSPCA's puppy advice — independent guidance for a first-time owner, which we are not the right people to give | `/blue-staffy-uk-breeders/` | 2026-09-20 · 200 |
| https://www.royalkennelclub.com/health-and-dog-care/health-dog-care/health/getting-started-with-health-testing-and-screening/dna-testing/dna-test-l-2hga/ | royalkennelclub.com | The registry's own page for the L-2-HGA DNA test — what the test is and what a clear, carrier or affected result means | `/blue-staffy-health-uk/` | 2026-09-20 · 200 |
| https://www.royalkennelclub.com/health-and-dog-care/health-dog-care/health/getting-started-with-health-testing-and-screening/dna-testing/dna-test-hc-hsf4/ | royalkennelclub.com | The registry's own page for the HC-HSF4 hereditary cataract DNA test, the second of the two the breed is screened for | `/blue-staffy-health-uk/` | 2026-09-20 · 200 |
| https://www.bva.co.uk/canine-health-schemes/eye-scheme/ | bva.co.uk | The British Veterinary Association's eye scheme — the examination that looks for inherited eye disease the HC-HSF4 DNA test does not cover | `/blue-staffy-health-uk/` | 2026-09-20 · 200 |
| https://www.gov.uk/get-your-dog-cat-microchipped | gov.uk | The government's guidance on the microchipping law every puppy leaving us has to satisfy | `/blue-staffy-health-uk/` | 2026-09-20 · 200 |
| https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/other-veterinary-advice/dog-vaccines | pdsa.org.uk | The PDSA's guide to dog vaccinations — independent detail on the second dose and the booster, which are the owner's own vet's | `/blue-staffy-health-uk/` | 2026-09-20 · 200 |
| https://www.royalkennelclub.com/breed-standards/terrier/staffordshire-bull-terrier/ | royalkennelclub.com | The registry's breed standard for the Staffordshire Bull Terrier — the build, head, coat, tail and temperament our breed-facts table describes, in the standard's own words | `/uk-staffordshire-bull-terrier-guide/` | 2026-09-20 · 200 |
| https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/puppies-dogs/medium-dogs/staffordshire-bull-terrier | pdsa.org.uk | The PDSA's veterinary breed page for the Staffordshire Bull Terrier — independent care, exercise, feeding and grooming advice, which we are not the right people to give | `/uk-staffordshire-bull-terrier-guide/` | 2026-09-20 · 200 |
| https://www.gov.uk/control-dog-public/banned-dogs | gov.uk | The government's own list of dog types banned under the Dangerous Dogs Act 1991 — the page behind the statement that the Staffordshire Bull Terrier is not one of them | `/uk-staffordshire-bull-terrier-guide/` | 2026-09-20 · 200 |

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
