# Migration parity

Built pages measured against what the extractor promised. `raw` is the old
`.entry-content` before the extractor's deliberate removals (dead WordPress
forms, the four sold pups' cards); `expected` is the same page after them;
`built` is what `article.prose-migrated` renders. The gate compares
expected → built with a 2% whitespace band; headings must match exactly and
embeds must never decrease.

| URL | words raw→expected→built | headings exp→built | images exp→built | embeds exp→built | result |
| --- | --- | --- | --- | --- | --- |
| /blue-staffy-blog-guides/ | 0→0→142 | 0→3 | 0→0 | 0→0 | PASS (archive) |
| /blue-staffy-health-uk/ | 3510→3165→3165 | 62→62 | 8→8 | 0→0 | PASS |
| /blue-staffy-pup-sale-uk/ | 1133→788→788 | 18→18 | 5→5 | 0→0 | PASS |
| /blue-staffy-uk-breeders/ | 2316→1780→1780 | 27→27 | 7→7 | 1→1 | PASS |
| /buy-blue-staffy-puppies-uk/ | 2488→2254→2254 | 27→27 | 7→7 | 1→1 | PASS |
| /buy-staffy-puppies-for-sale-uk/ | 4706→4706→4706 | 50→50 | 13→13 | 1→1 | PASS |
| / | 3369→3112→3112 | 59→59 | 14→14 | 2→2 | PASS |
| /privacy-policy-uk/ | 1015→1015→1015 | 23→23 | 3→3 | 0→0 | PASS |
| /thank-you-blue-staffy-puppies-journey/ | 422→422→422 | 5→5 | 1→1 | 0→0 | PASS |
| /uk-blue-staffy-breeders-contact/ | 397→397→397 | 6→6 | 1→1 | 0→0 | PASS |
| /uk-blue-staffy-puppy-buying-guide/ | 6117→6117→6117 | 68→68 | 17→17 | 1→1 | PASS |
| /uk-locations/blue-staffies-newcastle-under-lyme/ | 5→5→5 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-aberdeen/ | 476→443→443 | 10→10 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-birmingham/ | 4→4→4 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-bristol-uk/ | 0→0→0 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-dundee/ | 463→430→430 | 10→10 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-edinburgh/ | 485→452→452 | 10→10 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-for-sale-in-leicester/ | 7→7→7 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-for-sale-leeds/ | 0→0→0 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-hull/ | 470→437→437 | 10→10 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-inverness/ | 469→436→436 | 10→10 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-london/ | 4→4→4 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-manchester-uk/ | 5→5→5 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-middlesbrough/ | 449→416→416 | 10→10 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-oxford/ | 473→440→440 | 10→10 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-south-yorkshire/ | 0→0→0 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-sunderland/ | 464→431→431 | 10→10 | 0→0 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-uk/ | 2112→1767→1767 | 29→29 | 11→11 | 0→0 | PASS |
| /uk-locations/blue-staffy-puppies-york/ | 474→441→441 | 10→10 | 0→0 | 0→0 | PASS |
| /uk-locations/buy-blue-staffy-puppy-coventry-area/ | 0→0→0 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/staffy-breeding-dogs-glasgow/ | 1853→1508→1508 | 19→19 | 4→4 | 1→1 | PASS |
| /uk-locations/staffy-puppies-cardiff-wales/ | 4→4→4 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/staffy-puppies-for-sale-cornwall/ | 0→0→0 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/staffy-puppies-for-sale-essex/ | 0→0→0 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/staffy-puppies-for-sale-glasgow/ | 5→5→5 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/staffy-puppies-for-sale-liverpool/ | 5→5→5 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/staffy-puppies-for-sale-nottingham/ | 5→5→5 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/staffy-puppies-wolverhampton/ | 3→3→3 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-locations/uk-staffordshire-bull-terrier-breeder/ | 0→0→0 | 0→0 | 0→0 | 0→0 | PASS |
| /uk-staffordshire-bull-terrier-guide/ | 4975→4630→4630 | 72→72 | 10→10 | 1→1 | PASS |

examined 40 pages, 0 failing
