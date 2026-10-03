---
name: bsuk-city-places
description: Use when a BlueStaffyUK city page needs city-specific material — parks, dog-friendly spaces, dog rules, landmarks, vets, a handover point or a first-hand line — so that no two of the 28 city pages read alike; or when a heading such as "Where can a flat-dwelling Staffy stretch its legs in <city>'s parks?" has to be answered. (BlueStaffyUK)
allowed-tools: [Read, Write, Bash, WebFetch, WebSearch]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

# Sourced city places

**Core principle:** a city fact reaches a page only through `data/city-places/<slug>.json`, and only with an official source, a short quote and a fetch date. You research and record. You **do not write page copy** here: the board shows the places, the breeder approves them, and then the builder writes from the file. (Breeder, answer board q06, 2026-10-03: every city page uses its own landmarks, parks and vets, so that no page duplicates another.)

## Sources, best first

| Kind | Use | Never use |
|---|---|---|
| Dog rules, lead zones, dog-free areas, dogs-per-walker limits, PSPOs | the park owner's own page: the council, the Royal Parks, the City of London open spaces | dog-walking blogs, directories, "friends of" societies (record these only as a lead to find the owner's page) |
| Parks and open spaces | the owner's page, plus the city's searched areas (`scripts/neighbourhoods.py`, with volume) | your memory of the city |
| Vets | **the RCVS Find a Vet search link only** | naming any practice: that's an endorsement. Name one only if Lisa says she has used it. |
| Handover points, landmarks on the route | **Lisa only** | a station, a car park or a motorway services you think is likely |
| The first-hand line | **Lisa only**: a past delivery (borough level), a buyer there, a route note | a "plausible" anecdote, or "we plan every delivery around comfort" |
| Breed care facts (heat, exercise) | `data/breed-standards.json`, or a board-listed source | general knowledge |

## The file

`data/city-places/<slug>.json`, where `<slug>` is the city's slug **exactly as `data/locations.json` gives it** (Manchester is `blue-staffy-puppies-manchester-uk`, not the page's short name). London's file is the worked example when it exists; if it doesn't, use this shape:

```json
{"slug": "...", "city": "...", "fetched": "YYYY-MM-DD", "method": "every entry quoted from the source page; nothing inferred",
 "places": [{"name": "...", "kind": "park|open-space|dog-area|landmark", "area": "...", "managed_by": "...",
             "facts": [{"value": "...", "quote": "under 25 words, verbatim", "source": "https://...", "fetched": "YYYY-MM-DD"}]}],
 "rules": [{"topic": "...", "value": "...", "quote": "...", "source": "...", "fetched": "..."}],
 "vets": {"how": "RCVS Find a Vet", "source": "https://...", "quote": "...", "fetched": "..."},
 "not_fetched": ["NOT FETCHED — <what you tried and what stopped it>"],
 "breeder_questions": ["..."]}
```

Anything you couldn't fetch is written `NOT FETCHED — <what you tried and what stopped it>`. A quote must describe the value it backs (an address line is not a quote for a rule). Run `npm run -s check:barriers` before you commit.

If someone asks for the paragraph now, give it as a labelled **DRAFT for the builder**, built only from the file's facts. It doesn't go on the page until the board is approved.

## Then

1. The board shows the places (with their links, per working rule 12: a link that is not on the board is not built).
2. The breeder's questions go to the answer board.
3. A city with no first-hand fact from Lisa stays a short page or joins a regional page (q06). It never gets an invented one.

## Red flags: stop

| You were about to | Instead |
|---|---|
| Write the park paragraph straight into the page | Record it in the file; the builder writes it after approval |
| Quote a rule from a blog or a society page | Find the owner's page, or record NOT FETCHED |
| Name a vet practice "to be helpful" | The RCVS link |
| Add "a long drive down the M6", a mileage or a journey time | Delivery band or collection only |
| Add an unsourced breed claim ("Staffies overheat quickly") | `data/breed-standards.json`, or leave it out |
| Stop at one park because it was the first you found | Cover the city's searched areas; 6–10 places for a big city, fewer is fine when sourced |
