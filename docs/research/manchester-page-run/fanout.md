# Query fan-out: blue-staffy-puppies-manchester-uk

- **Primary keyword:** blue staffy puppies manchester
- **Route:** `/uk-locations/blue-staffy-puppies-manchester-uk/`
- **Compiled:** 2026-10-07 (page-run row 5, step 4; plan Task 6)
- **Sources:**
  - `data/queries/raw/blue-staffy-puppies-manchester-uk/serp_google.response.json` (DataForSEO, banked 2026-09-23)
  - the live Google read of 2026-10-07 (`ai-overview.md`)
  - `data/queries/raw/blue-staffy-puppies-manchester-uk/threads.json` and `data/queries/thread-ledger.json`
  - `thread-search-2026-10-07.json`
  - `data/queries/blue-staffy-puppies-manchester-uk.json` (the question file and its scores)
  - LLM intel: `docs/research/llm-intel/blue-staffy-puppies-manchester-uk-2026-09-25.json`. ChatGPT was asked "Where can I buy a blue Staffy puppy near Manchester, and what should I ask the breeder?" and did not cite BSUK. It cited royalkennelclub.com, pdsa.org.uk and one breeder domain. Task 7 refreshes this file.

## 1. People Also Ask

From the banked SERP (`people_also_ask`, 6 questions, click depth 1):

1. How much does a blue Staffy puppy cost?
2. Are there blue Staffordshire Bull Terrier puppies available for sale in Manchester?
3. Is it better to get a male or female Staffy?
4. Are blue staffies good pets?
5. Is blue Staffy aggressive?
6. Can a Staffy be left alone for hours?

The live read on 2026-10-07 showed questions 1–4 only, in the order 1, 2, 4, 3.

**Related searches** (banked, 6):
- Blue staffy puppies manchester kennel club
- Blue staffy puppies manchester cheap
- Staffy puppies for sale Manchester under 500
- Free staffy puppies to good homes Manchester
- Staffy puppies for sale Manchester gumtree
- Staffy puppies for sale near Salford

**People also search for** (live, 2026-10-07): this list adds two that the banked set does not carry:
- Blue staffy puppies manchester rescue
- Blue staffy puppies manchester for adoption

It also repeated kennel club, cheap, free-to-good-homes and under 500.

## 2. Threads

**Reused from the ledger.** `python3 scripts/thread_ledger.py --known` returned `reuse` for all 8 threads. They were read on 2026-09-23, so none was reopened. The buyer questions below are the paraphrases recorded in `threads.json` at that read.

| Thread (permalink) | Title · subreddit · posted · replies | What the buyer asks |
|---|---|---|
| https://www.reddit.com/r/StaffordBullTerriers/comments/1o4hazd/a_question_for_owners_of_blues/ | A question for owners of blues · r/StaffordBullTerriers · 2025-10 · 44 | Are blues more common than other colours in the UK? Does two blue parents matter for health? Can a blue come from non-blue parents? Are both parents DNA-clear for L-2-HGA and HC-HSF4, and can I see the results? Vet-checked vs health-tested parents? Are blues more prone to skin problems? Colour or health and temperament first? How do I tell a responsible blue breeder from a backyard breeder? |
| https://www.reddit.com/r/StaffordBullTerriers/comments/1r9a4ad/help_before_buying/ | Help before buying · r/StaffordBullTerriers · 2026-02 · 321 | What if a viewed puppy has mites? Should the first vaccination be done before collection? How do I confirm a vet examined the puppy? Should the contract allow my own vet check? What paperwork comes with a puppy advertised as KC registered? |
| https://www.reddit.com/r/UK_Pets/comments/1sdvsvv/reputable_staffordshire_bull_terrier_breeders_uk/ | Reputable Staffordshire Bull Terrier breeders (UK) · r/UK_Pets · 2026-04 · 32 | How do I find a reputable, health-tested Staffy breeder in the UK? Can a breed club point me to planned litters? Can a first-timer meet breeders at a dog show? First-time owner: puppy or adult rescue? |
| https://www.reddit.com/r/UK_Pets/comments/1uil782/pets4homesuk/ | Pets4homesuk · r/UK_Pets · 2026-06 · 96 | How can I tell whether a UK classifieds advert is genuine? Should I see the puppy with its mother before any money changes hands? Is it safe to pay a deposit to a seller found through an online advert? |
| https://www.reddit.com/r/StaffordBullTerriers/comments/1keeqmx/to_blue_or_not_to_blue/ | To blue or not to blue? · r/StaffordBullTerriers · 2025-05 · 50 | No question recorded in `threads.json` or the ledger; title only (blue or another colour). |
| https://www.reddit.com/r/StaffordBullTerriers/comments/1gliy8v/blue_staffy/ | Blue staffy · r/StaffordBullTerriers · 2024-11 · 9 | No question recorded; title only. |
| https://www.reddit.com/r/StaffordBullTerriers/comments/1wayqzb/hi_everyone_id_love_some_advice_please/ | Hi everyone, I'd love some advice please! · r/StaffordBullTerriers · 2026-09 · 31 | No question recorded; title only. |
| https://www.reddit.com/r/puppy101/comments/1pcj7ph/getting_a_staffy_puppy_soon_but_i_live_on_a_2nd/ | Getting a Staffy puppy soon but I live on a 2nd floor flat… · r/puppy101 · 2025-12 · 17 | Toilet training a Staffy puppy in a second-floor flat (from the title; no question recorded). |

**New candidates (2026-10-07).** Eleven threads not in the ledger turned up, eight of them in r/manchester. All are listed in `thread-search-2026-10-07.json`. **NOT FETCHED — Reddit blocked every rung tried.** What was tried:
- the Playwright MCP browser: www.reddit.com answered with HTTP 403, "You've been blocked by network security", on a js_challenge URL;
- curl with a desktop-browser user agent: Reddit's JavaScript challenge page on www, and a 302 on old.reddit.com;
- Firecrawl scrape: it refuses reddit.com.

The challenge was not solved or bypassed. No question was written from these threads, and `threads.json` is unchanged. One more buyer post was found in a Facebook group, which no rung reaches: NOT FETCHED — Facebook groups are unreachable by every rung.

## 3. Owner language

**From opened threads: NOT FETCHED — no thread could be read for owners' own words.** The 8 reused threads were recorded on 2026-09-23 as paraphrased questions only, not in posters' own words. The ledger says not to reopen them. The 11 new candidates are behind Reddit's network-security block, as described above.

**Search-result excerpts.** The text below is what Firecrawl's search returned for each URL on 2026-10-07. The threads themselves were not opened, so this is the indexed excerpt, not a verified reading of the live thread. It gives language and tone only, never a fact. Posters are not named. Each quote is under 15 words.

| # | Excerpt | URL | Signal |
|---|---|---|---|
| 1 | "Avoid the puppy farmers on Gumtree." | https://www.reddit.com/r/manchester/comments/ttv2wz/dog_breeders_manchester/ | puppy-farm fear; Manchester buyer thread ("5y ago" per a search snippet) |
| 2 | "Pets4Homes also has stolen puppies, and puppy-farmed puppies. Do avoid." | https://www.reddit.com/r/manchester/comments/h8cnx3/where_to_find_unwanted_puppies/ | marketplace distrust; r/manchester |
| 3 | "the best way to go about buying or adopting a puppy in Manchester." | https://www.reddit.com/r/manchester/comments/ctzotk/ethical_places_to_adoptbuy_a_puppy_in_manchester/ | buy-or-adopt framing; thread title says "Ethical places" |
| 4 | "If you must buy a pedigree, get it from a responsible family breeder." | https://www.reddit.com/r/manchester/comments/xbgsfa/abandoned_dog_queens_park_harpurhey/ | responsible-breeder language; rescue-first culture |
| 5 | "take your payment online and you never hear from them again." | https://www.reddit.com/r/StaffordBullTerriers/comments/1efaa7k/scam_alert_charming_staffordshire_is_a_scam/ | deposit-scam fear (Staffy scam-alert thread; no UK signal in the excerpt) |
| 6 | "Breeders can only sell puppies they have bred themselves" | https://www.reddit.com/r/manchester/comments/ydwiuw/do_not_buy_from_manchester_pets_and_aquatics/ | buyers know the third-party sale rule (language only; any legal statement on our page is `LEGAL_CLAIM_PLACEHOLDER`) |
| 7 | "So many XL bullies have made me scared of running in MCR" (thread title) | https://www.reddit.com/r/manchester/comments/1e80tyx/so_many_xl_bullies_have_made_me_scared_of_running/ | bull-breed reputation fear in Manchester |
| 8 | "she's super gentle with kids" | https://www.reddit.com/r/StaffordBullTerriers/comments/1hq4v71/honest_truth/ | family-temperament reassurance from an owner (no UK signal) |
| 9 | "Manchester born and bred!" | https://www.reddit.com/r/manchester/comments/9cpwm9/some_pictures_of_my_blue_staffordshire_bull/ | local pride in a blue Staffy owner's post |

For the research-board record:
- `owner_language` should be the NOT FETCHED — Reddit network-security block string above, with these excerpts attached as excerpt-level evidence and labelled as such.
- They must not be presented as quotes read from an opened thread.

## 4. Search intent for a Greater Manchester buyer

**Dominant: transactional.**
- The live 2026-10-07 read's top eight organic results are all marketplace or classifieds pages: Pets4Homes ×2, Staffie Owners ×2, Gumtree, Freeads, Puppies.co.uk and Preloved.
- The banked 2026-09-23 capture's ten organic results are the same kind of page, plus Champdogs' breeder directory at 8.
- PAA 2 asks whether blue SBT puppies are "available for sale in Manchester".
- The question file scores "Where can I buy a blue Staffy puppy near Manchester?" at 5.
- The searcher wants a puppy to buy.

**Secondary: commercial investigation, price first, then suitability.**
- PAA 1 is price ("How much does a blue Staffy puppy cost?", question-file score 5).
- Three related searches are price-floor hunts: cheap, under 500, free to good homes. The page-one snippets quote third-party ranges up to £2,800.
- The remaining PAA are pre-purchase suitability checks: male or female, good pets, aggressive, left alone. These are informational questions asked on the way to buying.
- A third strand is new on the live page: **rescue or adoption** ("… rescue", "… for adoption", Dogs Trust Manchester at organic 9, and excerpts 3 and 4 above). Some Manchester searchers are weighing a breeder against a rescue.

**Emotional: fear of a scam or a farmed puppy, with health close behind.**
- "Should I see the puppy with its mother before any money changes hands?" scores 5 in the question file (r/UK_Pets, https://www.reddit.com/r/UK_Pets/comments/1uil782/pets4homesuk/).
- "Is it safe to pay a deposit to a seller I found through an online advert?" and "Should I pay a deposit before I have seen the puppy?" each score 4.
- The excerpts carry the same fear in owners' words: "Avoid the puppy farmers on Gumtree." and "take your payment online and you never hear from them again."
- The highest-scoring question in the file is health: "Are the parents of your blue Staffy puppies health-tested?" (6). We hold no DNA certificates on the site, so this fear has to be met honestly. The tests can be named, never a result.
- Breed reputation is a Manchester-specific undertone: PAA "Is blue Staffy aggressive?" and the r/manchester thread title about XL bullies (excerpt 7).
- This matches the session brief's reader (Q8): a buyer afraid of a deposit scam and a farmed or sick puppy.
- Our deposit books the viewing, so the page has to explain that order and the deposit terms from `data/settings.json`. It must never repeat a "see before you pay" rule we do not follow.

**Local: Greater Manchester, about 120 miles from Carlisle (session brief Q8).**
- Page one splits the city into Salford, Bolton and Greater Manchester facets, and one related search is "near Salford". The buyer thinks in boroughs, not just "Manchester".
- We have no Manchester address. The local answer is UK home delivery by DEFRA-approved transport, priced by distance (`delivery_min_gbp`–`delivery_max_gbp` in `data/settings.json`), or collection in Carlisle.
- The question file asks it directly: "Can I get a blue Staffy puppy delivered to my home?" (4) and "Can you deliver a Blue Staffy puppy to my location in the UK?" (4).
- The Kennel Club strand is local too: the "… manchester kennel club" related search, plus the Royal Kennel Club's sponsored find-a-puppy ad on the live page. Any registration statement stays `LICENCE_CLAIM_PLACEHOLDER` until confirmed.

## 5. Counts

- **PAA:** 6 banked questions (4 shown live). **Related searches:** 6 banked, plus 2 live-only (rescue, for adoption).
- **Threads:** 8 reused from the ledger, with 21 paraphrased buyer questions in `threads.json`. 11 new candidates were found and NOT FETCHED (Reddit network-security block).
- **Owner-language quotes from opened threads:** 0 (NOT FETCHED — Reddit network-security block). **Search-result excerpts with URLs:** 9.
- **AI Overview:** not shown in this session (`ai-overview.md`).
