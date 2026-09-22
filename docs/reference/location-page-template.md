# Location page template (BSUK)

The user's location-page template (supplied as a Maltipoo/Maltese state-page brief for another
breeder), converted to BlueStaffyUK. `.claude/skills/bsuk-location-page-builder/SKILL.md` builds
from this document; where the two disagree, the skill's fact table wins for facts and this
document wins for structure, FAQ format and tone.

## What a city page is for

One UK city, one buyer: someone near that city deciding whether to buy a blue Staffordshire
Bull Terrier puppy from Lisa Bright in Carlisle · Cumbria. The page answers what that buyer
asks, in the order they ask it, with the city's own geography — not the same page with a new
city name.

## Section count — competitors decide, never a fixed number

1. Pool: the top-5 breeder or location pages for the city query on Google plus the top-5 on
   Bing, merged. Marketplaces and directories are excluded.
2. Strip non-content H2s: sidebar, footer, related posts, repeated calls to action, reviews
   and FAQ headings (ours are frame, so theirs are not counted either).
3. Match the highest cleaned H2 count in the pool. If it is more than 1.5× the next highest
   it is an outlier: record it and match the next highest.
4. Add three sections: the strongest topics in the page's question file that no pooled page
   covers (`extra_sections` in `data/queries/<slug>.json`).
5. Only body H2s count, on both sides. The fixed frame below is never counted.

`scripts/query_augment.py` (arrives in Task 2) computes this; `scripts/query_coverage_check.py` (arrives in Task 6)
fails a built page that falls short.

## The fixed frame

Hero (H1, image first) · counter strip · trust strip · table of contents · key takeaways
(3–5 bullets, `id="key-takeaways"`) · review top · review middle · review bottom · newsletter ·
enquiry form · FAQ top · FAQ middle · FAQ bottom. Body sections sit between them; the FAQ
blocks sit at the top, middle and bottom of the body as in the source template.

## FAQ format

- Three blocks: **top** 5–7 questions (buying and logistics — price, deposit, delivery to this
  city, reserving), **middle** 5–7 (process and trust — paperwork, health testing, visiting,
  age at collection), **bottom** 7–10 (breed and lifestyle — flats, children and other pets,
  training, the 12–14 year lifespan, coat). 17–20 questions in practice.
- Every question is an H3. A concise, direct answer follows it. Internal and external links
  sit inside answers, anchor first.
- Questions are written the way buyers ask them aloud ("Do you deliver Staffy puppies to
  Manchester?"), taken from the page's question file, never invented.
- FAQPage schema carries exactly the visible questions.

## Headers and paragraphs

- Every H1–H6 has a one-to-two-sentence opening paragraph that restates what the heading
  promises.
- Subheaders are long-form, conversational, Reddit-style questions where the topic allows.
- Short paragraphs (two to four sentences), bullets for scanning, bold for the one fact a
  skimmer must not miss, a subheader every 200–300 words.

## Links

- Anchors start the sentence or paragraph, never trail it.
- Vary anchor text: exact, partial, descriptive. Never "click here".
- Internal: every relevant BSUK page at least once — available puppies, the buying guide,
  the breed guide, health, delivery and pricing wording, about, contact, 3–5 nearby city
  pages — then varied repeats where they genuinely help. The source template's "50+ internal
  links" assumed a larger site; BSUK has 11 pages plus 28 cities.
- External: breed and health authorities only (The Kennel Club, the breed's DNA-test bodies,
  UK government pages for the law sections). Never a competitor, a marketplace, or a local
  business BSUK has not verified.

## Topics carried over from the source, converted

| Source topic | BSUK version |
|---|---|
| Why choose the breeder | Lisa Bright, home-raised litters, Carlisle · Cumbria — only facts in the skill's fact table |
| Available puppies by type | The litter in `data/puppies.json`: £1,500 and £1,700 pups, deposit £500 refundable |
| Temperament | Staffordshire Bull Terrier temperament, sourced from the breed guide page |
| Health and wellness | DNA tests the breed is screened for, only where the evidence ledger records them |
| Grooming | Short coat, nail, ear and teeth care |
| Training | Positive-reinforcement basics, socialisation |
| Delivery to the state, airports | Delivery to the city: £200–£350 priced by distance by DEFRA-approved transport, or collection from Carlisle; the main roads and stations that link the city to Cumbria |
| Cities served | Nearby BSUK city pages from `data/locations.json` |
| Dog-friendly activities, parks | Real local walks and parks the page can name and link |
| Climate | The city's weather and what it means for a short-coated dog |
| Pricing and payment | Locked prices and deposit only |
| Testimonials | The three real reviews in `data/reviews.json`, rotated; `REVIEW_PLACEHOLDER` slots otherwise |
| Regulations | UK law a buyer asks about: the Dangerous Dogs Act (the Staffordshire Bull Terrier is not a banned breed), microchipping; any licence line is `LICENCE_CLAIM_PLACEHOLDER` |
| Preparing your home | Puppy-proofing and the first week |
| Newsletter | The site's real newsletter form; no subscriber count |
| Final call to action | Enquiry form, email, `PHONE_PLACEHOLDER` until launch |

## Dropped from the source, and why

The source's breeder claims belong to another business: its years in business, its
multi-year health guarantee, its neurological-stimulation and puppy-culture programmes, its
US DNA-testing provider, its US federal licence, its subscriber count, its business-bureau
rating and its invented-format testimonials. None is a BSUK fact. The fixed 22-section
structure is replaced by the competitor rule above; the 4,500-word target and "150+
entities" become "as many real local entities as the city supports, none invented".
