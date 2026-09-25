# Competitive keyword gaps — 2026-09-23

Mode: all competitors. Gap matrix: docs/research/gap-matrix-2026-09-23.md.

- **BSUK source:** docs/research/competitors/bsuk.json (the BSUK profile, indexable pages only) — 31 pages.
- **Competitors used:** trojanstaffuk (tier 1, fetched_on 2026-09-23), pets4homes (tier 2, fetched_on 2026-09-23), rspca (tier 3, fetched_on 2026-09-23). Registry: data/competitors.json present.
- **Stale:** none. Tier-5 stale: none. The gap matrix lists 18 registry entries with no report yet; they are not in this run.
- **Names cut:** pets4homes (the first run's topic for the pets4homes support article ended in the business name).
- **Skipped pages:** 9 (all "no keyword topic": the pets4homes and rspca homepages, a pets4homes pet-advice article, four rspca advice/adopt/campaign/pet-cost-calculator pages, and the trojanstaffuk about-the-breed and contact pages).
- **Fetch count:** 0.
- **Pages on another domain:** none. **Same URL in two reports:** none.
- **Re-derived:** from the same reports and BSUK profile with the whole-word page-type table (Known Issue 51). The RSPCA pet cost calculator is no longer typed `price` (its path holds "costofliving", not the word "cost"), so its row left the gaps. "Greater" before a named city is now part of that city, so the pets4homes Manchester listing is a Manchester city topic carrying the Manchester stub label. A `/post/` path is a blog post (the page-type table's blog row), so the trojanstaffuk health-and-wellbeing post is typed `blog`; no fetch.
- **Declined requests:** none.
- **Gap matrix counts (quoted, not recounted):** page types BSUK lacks — care-guide 2/3 (high), faq 1/3, price 1/3, reviews 1/3 (medium). City gaps: none; BSUK has every competitor city listed.

## Gaps

| Topic | Score | Band | Competitor URLs | BSUK page | Suggested page type |
|---|---|---|---|---|---|
| staffordshire bull terrier puppies for sale | 10 (3+2+3+2) | high | https://www.pets4homes.co.uk/sale/puppies/staffordshire-bull-terrier/ | none | listing |
| staffordshire bull terrier puppies for sale in manchester greater manchester | 10 (3+2+3+2) | high | https://www.pets4homes.co.uk/sale/puppies/staffordshire-bull-terrier/united-kingdom/england/greater-manchester/manchester/ | exists, not indexed — project 5 rebuild: /uk-locations/blue-staffy-puppies-manchester-uk/ | city |
| staffy puppies quality blue | 10 (3+2+3+2) | high | https://www.trojanstaffuk.com/ | none | untyped |
| uk staffordshire bull terrier licenced breeders | 8 (3+0+3+2) | always high | https://www.trojanstaffuk.com/how-we-roll | none | untyped |
| advice for buying and advertising pets | 3 (0+0+3+0) | low | https://support.pets4homes.co.uk/en/support/solutions/articles/47001254375-advice-for-buying-and-advertising-pets | none | blog |
| pedigree dogs health problems | 3 (0+0+3+0) | low | https://www.rspca.org.uk/adviceandwelfare/pets/dogs/puppy/pedigreedogs/health | none | health |
| staffordshire bull terrier health wellbeing a comprehensive guide | 3 (0+0+3+0) | low | https://www.trojanstaffuk.com/post/staffordshire-bull-terrier-health-wellbeing-a-comprehensive-guide | none | blog |

Score parts: dedicated + key page + BSUK has no page + buyer intent.

## Already covered

| Topic | Competitor URL | BSUK page |
|---|---|---|
| staffy puppies for sale | https://www.trojanstaffuk.com/staffy-puppies | https://SITE_URL_PLACEHOLDER/available-puppies/ |

## High gaps

- **staffordshire bull terrier puppies for sale** — a national listing page built around the full breed name plus "for sale"; BSUK's listing page is titled with "staffy", so no BSUK title or H1 holds the full-name phrase.
- **staffordshire bull terrier puppies for sale in manchester greater manchester** — a city listing page for Manchester ("Greater Manchester" is read as Manchester). BSUK's Manchester page exists as a noindex stub (/uk-locations/blue-staffy-puppies-manchester-uk/); the gap closes with that stub's project 5 rebuild, not a second Manchester URL.
- **staffy puppies quality blue** — a breeder homepage leading on blue staffy puppies as a quality claim; no BSUK page puts those words together in its title or H1.
- **uk staffordshire bull terrier licenced breeders** — a page about being a licensed UK breeder. It is always high ("licenced" is a trust word) and would be high on points alone (8).

## Handoff

- `bsuk-content-architect`: staffordshire bull terrier puppies for sale — https://www.pets4homes.co.uk/sale/puppies/staffordshire-bull-terrier/ — listing.
- `bsuk-content-architect`: rebuild the stub /uk-locations/blue-staffy-puppies-manchester-uk/ (project 5) for staffordshire bull terrier puppies for sale in manchester greater manchester — https://www.pets4homes.co.uk/sale/puppies/staffordshire-bull-terrier/united-kingdom/england/greater-manchester/manchester/ — city.
- `bsuk-content-architect`: staffy puppies quality blue — https://www.trojanstaffuk.com/ — untyped.
- `bsuk-content-architect`: uk staffordshire bull terrier licenced breeders — https://www.trojanstaffuk.com/how-we-roll — untyped.
- `bsuk-strategy-synthesizer`: this file; no medium gaps for the content calendar.
- No stale report; no re-run of `bsuk-competitor-intel` needed.
