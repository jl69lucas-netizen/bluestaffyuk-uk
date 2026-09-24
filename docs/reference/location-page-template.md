# Location page template (BSUK)

The user's location-page template (supplied as a Maltipoo/Maltese state-page brief for another
breeder), converted to BlueStaffyUK. `.claude/skills/bsuk-location-page-builder/SKILL.md` builds
from this document; where the two disagree, the skill's fact table wins for facts and this
document wins for structure, FAQ format and tone.

## What a city page is for

One UK city or area, one buyer: someone near that city or area deciding whether to buy a blue
Staffordshire Bull Terrier puppy from Lisa Bright in Carlisle · Cumbria. The page answers what
that buyer asks, in the order they ask it, with the place's own geography — not the same page
with a new city name.

## Section count — competitors decide, never a fixed number

1. Pool: the top-5 results for the page's primary keyword (the city row's H1 keyword) on
   Google plus the top-5 on Bing, merged, **marketplaces and directories included** — only
   off-topic results are dropped. The skill's three query shapes
   (`staffy puppies for sale <city>`, `blue staffy puppies <city>`,
   `staffordshire bull terrier breeder near <city>`) may be run as an optional free gap scan:
   they supply topics, never the count.
2. Strip non-content H2s: sidebar, footer, related posts, repeated calls to action, reviews
   and FAQ headings (ours are frame, so theirs are not counted either). Advert-card titles and
   navigation headings never count — `scripts/query_augment.py --extract-h2` reads the saved
   page and drops any H2 inside a link, nav, footer, aside or form; inside an advert-card
   article (one of two or more H2-bearing articles that hold no such article themselves —
   a page-wrapper article keeps its own H2s); inside a list item when three or more items of that list carry an H2 (a card
   grid — a short accordion counts); inside a site header (a header within a section
   counts); and any H2 that is nothing but a link. Search filters, result counts and grid
   headers ("Refine your results", "30 Puppies found") are stripped as furniture. A page
   that comes back as a bot challenge (its title, or a challenge script's markers) is
   recorded as blocked: it is in the pool but never sets the number.
3. Match the highest cleaned H2 count in the pool. If it is more than 1.5× the next highest
   it is an outlier: record it and match the next highest.
4. Add three sections: the strongest topics in the page's question file that no pooled page
   covers (`extra_sections` in `data/queries/<slug>.json`). Fewer than three uncovered topics:
   the strongest covered topics fill the gap, marked `uncovered: false`. The floor: never
   fewer than 9 body sections — the target is the matched count + 3, or 9 if that is higher.
5. Only body H2s count, on both sides. The fixed frame below is never counted.
6. Record every competitor's URL, its positions, its raw and cleaned H2 counts, and which set
   the number. A usable competitor page has at least 3 cleaned H2s and is not blocked
   (`MIN_USABLE_H2` in `scripts/query_augment.py`). Fewer than three usable pages is a finding,
   not a blocker: record it and derive from what exists.

`scripts/query_augment.py` computes this; `scripts/query_coverage_check.py`
fails a built page that falls short.

## The fixed frame

In this order:

1. Hero (H1, image first)
2. Counter strip
3. Trust strip
4. Table of contents
5. Key takeaways (3–5 bullets, `id="key-takeaways"`)
6. Review top
7. FAQ top
   — body sections, first third —
8. Review middle
9. FAQ middle
   — body sections, second third —
10. Newsletter (`id="newsletter"`)
    — body sections, last third —
11. Review bottom
12. FAQ bottom
13. Enquiry form

Frame parts sit in their own sections and are never counted as body sections. The body
sections are split roughly evenly across the three gaps.

## FAQ format

- Three blocks: **top** 5–7 questions (buying and logistics — price, deposit, delivery to this
  city, reserving), **middle** 5–7 (process and trust — paperwork, health testing, visiting,
  age at collection), **bottom** 7–10 (breed and lifestyle — flats, children and other pets,
  training, the 12–14 year lifespan, coat).
- 17–20 questions: the block minimums force 17; the gate checks 15–20 in total and each
  block's own range.
- If the question file cannot fill a block to its minimum, stop and report it. Never pad a
  block with an invented question or a reworded duplicate.
- Every question is an H3. A concise, direct answer follows it. Internal and external links
  sit inside answers, anchor first.
- Questions are written the way buyers ask them aloud ("Do You Deliver Staffy Puppies to
  Manchester?"), taken from the page's question file, never invented.
- FAQPage schema carries exactly the visible questions.

## Headers and paragraphs

- Every H1–H6 has a one-to-two-sentence opening paragraph that restates what the heading
  promises.
- Every heading, FAQ questions included, is AP-style Title Case (`title-case-headings` in
  `rules/headings.md`).
- The outline declares its header style and register with a reason (`header-style-declared`);
  the location default is Style 2, Conversational Hybrid. Subheaders are long-form
  conversational questions where the topic allows.
- Headings descend with no skipped level and the page carries all six levels
  (`heading-hierarchy-outline-gate`).
- Short paragraphs (two to four sentences), bullets for scanning, bold for the one fact a
  skimmer must not miss, a subheader every 200–300 words.

## Links

- Anchors start the sentence or paragraph, never trail it.
- Vary anchor text: exact, partial, descriptive. Never "click here".
- Internal: every relevant BSUK page at least once, then varied repeats where they genuinely
  help:
  - available puppies — `/available-puppies/` and each `/available-puppies/<slug>/` puppy page
  - the buy pages — `/buy-blue-staffy-puppies-uk/`, `/buy-staffy-puppies-for-sale-uk/`,
    `/blue-staffy-pup-sale-uk/`
  - the buying guide — `/uk-blue-staffy-puppy-buying-guide/`
  - the breed guide — `/uk-staffordshire-bull-terrier-guide/`
  - health — `/blue-staffy-health-uk/`
  - the breeder story (about) — `/blue-staffy-uk-breeders/`
  - contact — `/uk-blue-staffy-breeders-contact/`
  - the homepage — `/`
  - the blog hub `/blue-staffy-blog-guides/` and its posts where one fits
  - 3–5 nearby city pages — `/uk-locations/<slug>/`
- There is no delivery page and no pricing page. Delivery and price facts come from
  `data/settings.json` and `data/price-matrix.json` and are stated on the page itself.
- Inventory: `data/page-map.json` lists 40 routes — the homepage, 10 other pages, the blog
  hub and 28 city pages. The build also renders `/available-puppies/` with six puppy pages,
  and the blog posts (one today). The source template's "50+ internal links" assumed a
  larger site.
- External: only URLs recorded in `docs/reference/external-link-library.md`; a board naming
  any other is refused. For a city page that means the breed and health rows (the Kennel
  Club's breed and DNA-test pages, the BVA eye scheme, PDSA, RSPCA, Blue Cross) and the
  gov.uk rows for law topics. Never a competitor, a marketplace, or a local business.

## Topics carried over from the source, converted

| Source topic | BSUK version |
|---|---|
| Why choose the breeder | Lisa Bright, home-raised litters, Carlisle · Cumbria — only facts in the skill's fact table |
| Available puppies by type | The litter in `data/puppies.json`, prices from `data/price-matrix.json`: £1,500 and £1,700 pups, deposit £500 refundable |
| Temperament | Breed facts consistent with the breed guide; prose written fresh (`CLAUDE.md` rule 8); link to it |
| Health and wellness | Only what `data/quality/evidence-ledger.json` records. The health entities (BVA hip and elbow scores; the L2-HGA, HC and PHPV DNA tests) stay `NOT FETCHED` until the certificate is on file (`rules/copy.md`) |
| Grooming | Short coat, nail, ear and teeth care |
| Training | Positive-reinforcement basics, socialisation |
| Delivery to the state, airports | Delivery to the city: £200–£350 priced by distance by DEFRA-approved transport, or collection from Carlisle; the main roads and stations that link the city to Cumbria |
| Cities served | Nearby BSUK city pages from `data/locations.json` |
| Dog-friendly activities, parks | Local walks and parks named from a source recorded on the board (`CLAUDE.md` rule 12), not linked. No local business is named |
| Climate | Qualitative only: the city's weather and what it means for a short-coated dog. Any figure is `NOT FETCHED` on the board unless sourced and recorded; an unfetched figure is left out of the prose |
| Pricing and payment | Locked prices from `data/price-matrix.json` and the deposit from `data/settings.json` only |
| Testimonials | The three real reviews in `data/reviews.json`, rotated; `REVIEW_PLACEHOLDER` slots otherwise |
| Regulations | One statute line may be stated: the Staffordshire Bull Terrier is not a banned breed in the UK (it is not one of the types the Dangerous Dogs Act 1991 bans), linked to the government's list, https://www.gov.uk/control-dog-public/banned-dogs — the breed guide's row in `docs/reference/external-link-library.md`, allowed on city pages by the user's ruling on Known Issue 46 (2026-09-23). Every other statute line is `LEGAL_CLAIM_PLACEHOLDER` until confirmed (`CLAUDE.md` rule 9, `rules/copy.md`); any licence line is `LICENCE_CLAIM_PLACEHOLDER`. Other topics may be named (microchipping) but never asserted |
| Preparing your home | Puppy-proofing and the first week |
| Newsletter | The site's real newsletter form; no subscriber count |
| Final call to action | Enquiry form, email, `PHONE_PLACEHOLDER` until launch |

## Dropped from the source, and why

The source's breeder claims belong to another business: its years in business, its
multi-year health guarantee, its neurological-stimulation and puppy-culture programmes, its
US DNA-testing provider, its US federal licence, its subscriber count, its business-bureau
rating and its testimonials BSUK cannot attribute to a real buyer. None is a BSUK fact. The
fixed 22-section structure is replaced by the competitor rule above; the 4,500-word target
and "150+ entities" become "as many real local entities as the city supports, none invented".
