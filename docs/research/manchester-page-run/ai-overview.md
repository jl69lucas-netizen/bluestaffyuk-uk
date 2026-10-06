# Google AI Overview capture: "blue staffy puppies manchester"

- **Query:** blue staffy puppies manchester
- **Engine:** google.co.uk, read in the Playwright MCP browser (headless, signed out). Google showed no consent page and no challenge page.
- **URLs read:** `https://www.google.co.uk/search?q=blue+staffy+puppies+manchester&hl=en-GB&gl=uk` and then `https://www.google.co.uk/search?q=blue+staffy+puppies+manchester` (two loads, a few seconds apart)
- **Fetched:** 2026-10-07
- **Location Google assigned:** "B24, Birmingham - From your IP address" (page footer). The session was not in Greater Manchester.
- **AI Overview shown:** **no.** Neither load had an AI Overview block. The page text contains no "AI Overview" label; only the "AI Mode" tab appears in the navigation.

## What the page showed instead

The organic results, in order (first load):

| # | Domain | Result |
|---|---|---|
| 1 | pets4homes.co.uk | Staffordshire Bull Terrier puppies for sale in Manchester (marketplace facet; snippet price range £75–£2,800) |
| 2 | gumtree.com | Staffordshire Bull Terrier dogs and puppies for sale in Manchester (classifieds) |
| 3 | staffie-owners.co.uk | Blue Staffordshire Bull Terrier puppies for sale in Bolton, Manchester (blue colour facet) |
| 4 | freeads.co.uk | Staffordshire Bull Terrier, Manchester (classifieds) |
| 5 | puppies.co.uk | Staffordshire Bull Terrier puppies for sale near me in Manchester |
| 6 | pets4homes.co.uk | Staffordshire Bull Terrier puppies for sale in Greater Manchester |
| 7 | staffie-owners.co.uk | Staffie puppies for sale in Salford, Manchester |
| 8 | preloved.co.uk | staffy, dogs and puppies for sale in Manchester |
| — | People also ask | How much does a blue Staffy puppy cost? · Are there blue Staffordshire Bull Terrier puppies available for sale in Manchester? · Are blue Staffies good pets? · Is it better to get a male or female Staffy? |
| 9 | dogstrust.org.uk | Manchester dog rehoming, rescue and adoption (a rescue centre result) |
| 10 | pets4homes.co.uk | Staffordshire Bull Terrier puppies for sale (national) |

- **Second load:** a sponsored result from royalkennelclub.com ran above the organic results. It advertised the Kennel Club's find-a-puppy search, for Bull Terriers.
- **People also search for:** blue staffy puppies manchester rescue · … kennel club · … cheap · … for adoption · free staffy puppies to good homes Manchester · staffy puppies for sale Manchester under 500.
- BlueStaffyUK does not appear on page one.

## How this compares with the banked SERP and with London

- The organic set matches the DataForSEO capture banked on 2026-09-23 (`data/queries/raw/blue-staffy-puppies-manchester-uk/serp_google.response.json`). Marketplaces and classifieds take the top eight places in both. The live page shows 4 People Also Ask questions; the banked capture has 6. The first four are the same.
- The live "people also search for" list adds **rescue** and **for adoption**, which the banked related searches do not carry. Together with the Dogs Trust Manchester result, that puts a rescue alternative on page one.
- London (`docs/research/london-page-run/aio-google-2026-09-30.md`) did show an AI Overview. That capture was read in the user's own Chrome; this one was read in a signed-out headless browser placed in Birmingham. So the absence of an overview here is a fact about this session. It does not show that Manchester searchers never get one.

## GEO implication for us (observations, not claims)

- **No overview to be cited in, today, in this session.** Whether Google shows an AI Overview for this query depends on the session. We should build the page to be extractable as if one will appear. London's overview had the same marketplace-led page one, and it cited only marketplaces and the Royal Kennel Club. Expect the same pool here: pets4homes, staffie-owners, gumtree and royalkennelclub.com, which bought the ad slot on the second load.
- **Price:** the snippets show third-party listing ranges (£75–£2,800, £50–£1,500, £50–£2,800). An overview built from them would quote a range like London's. Our prices come from `data/puppies.json` only, stated plainly, so an answer engine can lift a single sourced figure instead of a marketplace range.
- **Health testing:** London's overview told buyers to ask for clear DNA results from both parents. We hold no DNA certificates on the site. The Manchester page has to meet that question head-on in extractable prose: name the tests and say honestly what we can and cannot show. It must never imply a result.
- **Viewing:** overviews in this space tell buyers to visit in person and see the puppy with its mother before paying. With us, the deposit books the viewing. The page has to explain that order and the deposit terms (`deposit_gbp` and `deposit_refund_clause` in `data/settings.json`) in a quotable passage. It must never echo advice our own process would fail.
- **Local:** we are in Carlisle, not Greater Manchester. "Available in Manchester" (PAA 2) is answered by UK home delivery by DEFRA-approved transport, priced by distance (`delivery_min_gbp`–`delivery_max_gbp`, `delivery_note`), or by collection in Carlisle. It is never answered by a Manchester address we do not have.
- **Rescue alternative:** with Dogs Trust Manchester and the rescue and adoption searches on page one, a short, honest "rescue or breeder" passage is citable. Today no listing page on page one answers that question.
