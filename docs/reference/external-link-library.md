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

## Provenance

Every row above is a URL the migrated WordPress body already carried on the page named in
"First page using it"; none is a new citation invented for the rebuild. All eight were
re-checked on 2026-09-19 and returned 200 following redirects.
