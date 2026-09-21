# Migration parity

Built pages measured against what the extractor promised. `raw` is the old
`.entry-content` before the extractor's deliberate removals (dead WordPress forms,
the four sold pups' cards); `expected` is the same page after them; `built` is what
`article.prose-migrated` renders. Note that `raw` is itself measured after site
chrome and dead forms are stripped, so it slightly understates the WordPress body.
The gate compares expected → built with a 2% whitespace band; headings must match
exactly, embeds must never decrease, a built page missing its article scope fails,
and expected must keep at least 60% of raw's words. Pages listed in
`data/facts/rebuilt.json` are no longer migrated bodies and are skipped here:
`scripts/facts_preserved_check.py` is their gate.

| URL | words raw→expected→built | headings exp→built | images exp→built | embeds exp→built | cards removed | result |
| --- | --- | --- | --- | --- | --- | --- |
| /blue-staffy-blog-guides/ | 0→0→142 | 0→3 | 0→0 | 0→0 | 0 | PASS (archive) |
| /uk-blue-staffy-puppy-buying-guide/ | 6117→6117→6117 | 68→68 | 17→17 | 1→1 | 0 | PASS |
| /uk-locations/blue-staffies-newcastle-under-lyme/ | 5→5→5 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-aberdeen/ | 476→443→443 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-birmingham/ | 4→4→4 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-bristol-uk/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-dundee/ | 463→430→430 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-edinburgh/ | 485→452→452 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-for-sale-in-leicester/ | 7→7→7 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-for-sale-leeds/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-hull/ | 470→437→437 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-inverness/ | 469→436→436 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-london/ | 4→4→4 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-manchester-uk/ | 5→5→5 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-middlesbrough/ | 449→416→416 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-oxford/ | 473→440→440 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-south-yorkshire/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/blue-staffy-puppies-sunderland/ | 464→431→431 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/blue-staffy-puppies-uk/ | 2112→1767→1767 | 29→29 | 11→11 | 0→0 | 4 | PASS |
| /uk-locations/blue-staffy-puppies-york/ | 474→441→441 | 10→10 | 0→0 | 0→0 | 4 | PASS (puppy-grid-emptied) |
| /uk-locations/buy-blue-staffy-puppy-coventry-area/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-breeding-dogs-glasgow/ | 1853→1508→1508 | 19→19 | 4→4 | 1→1 | 4 | PASS |
| /uk-locations/staffy-puppies-cardiff-wales/ | 4→4→4 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-puppies-for-sale-cornwall/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-puppies-for-sale-essex/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-puppies-for-sale-glasgow/ | 5→5→5 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-puppies-for-sale-liverpool/ | 5→5→5 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-puppies-for-sale-nottingham/ | 5→5→5 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/staffy-puppies-wolverhampton/ | 3→3→3 | 0→0 | 0→0 | 0→0 | 0 | PASS |
| /uk-locations/uk-staffordshire-bull-terrier-breeder/ | 0→0→0 | 0→0 | 0→0 | 0→0 | 0 | PASS |

examined 30 pages, 0 failing, skipped 10 rebuilt
