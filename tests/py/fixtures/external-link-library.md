# External link library — TEST FIXTURE

Not the real library. `docs/reference/external-link-library.md` is the one the site is
built against; this file exists so the board tests can exercise the membership rule in
`pageboard.validate_board()` without either coupling the unit tests to a content document
or having fixture URLs leak into it.

Every URL a board test fixture links to has a row here. A test that needs to prove the rule
REFUSES an unknown URL uses one that is deliberately absent.

| URL | What it is |
|---|---|
| https://www.gov.uk/guidance/dog-breeding-licence-england | the England dog breeding licence guidance |
| https://ico.org.uk/ | the Information Commissioner's Office |
| https://www.thekennelclub.org.uk/breed-standards/ | the Kennel Club breed standards |
| https://www.champdogs.co.uk/breeds/staffordshire-bull-terrier | a breed listing site |
| https://www.gov.uk/x | a short gov.uk target used by the link-table tests |
| https://example.com/foo_bar | a markdown-escaping probe |
| https://example.com/elsewhere | a second host used by the duplicate-anchor tests |
| https://example-host.test/70de/ | a reserved-TLD host used by the thumbnail tests |
