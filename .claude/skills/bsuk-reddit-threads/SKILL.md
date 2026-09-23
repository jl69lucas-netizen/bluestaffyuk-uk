---
name: bsuk-reddit-threads
description: Use when a BSUK page needs the real questions UK Staffy buyers ask on Reddit and dog forums, or a genuine thread worth citing — derives the searches from the page, climbs a fetch ladder tuned per site, scores and opens every thread before using it, prefers threads from the last 24 months, and writes data/queries/raw/<slug>/threads.json with a threads audit list for bsuk-query-augmentation. Never invents a thread, a quote or a vote count.
---

# Reddit and forum threads for a BSUK page

## Golden rule

A thread you have not opened does not exist. Every question you record comes from a thread
you loaded and read, with its permalink. Blocked after the whole ladder = `NOT FETCHED`.

## Step A — derive the searches from the page, not the topic

From the page's slug, primary keyword and page type, write 4–6 searches:

- `<primary keyword> reddit`
- `site:reddit.com <breed phrase> <city or UK>` — e.g. `site:reddit.com blue staffy puppy manchester`
- `site:reddit.com staffy breeder uk what to ask`
- one per page intent: delivery or collection, price, first-time owner, flat living
- for comparison pages, the two things compared plus `reddit`

## Step B — search, then fetch with the rung that works for that site

Search with Firecrawl search (it finds reddit.com and forum links fine). Then fetch each
candidate with the rung known to work — do not rediscover the ladder:

| Site | Works | Does not work (skip it) |
|---|---|---|
| www.reddit.com thread | Headless browser: Playwright `browser_navigate` + `browser_snapshot` on the `www.reddit.com/r/…/comments/…` permalink | Firecrawl scrape (refuses reddit.com); `.json` endpoints (return HTML); WebFetch on old.reddit.com; old.reddit.com in a headless browser (redirects to login) |
| UK dog forums (UK Pet Forums, Breedia, similar) | Firecrawl scrape, or the headless browser | — |
| Facebook groups | nothing reachable | record as `NOT FETCHED`; never guess its content |
| Anything else blocked | full ladder in `.claude/skills/research-recency/SKILL.md`: Firecrawl → WebFetch with a browser UA → headless browser → `/last30days` when installed | — |

Where to look: r/StaffordshireBullTerrier, r/StaffordBullTerriers, r/DogAdvice, r/dogs,
r/puppy101, r/AskUK, r/unitedkingdom, and UK dog forums the search turns up.

**Browser artefacts** (snapshots, screenshots, console logs) go only in the session scratchpad
— pass an absolute scratch path as the filename. Nothing goes in any repo; if a
`.playwright-mcp/` folder appears in a repo, delete it before you finish.

## Step C — score each candidate (keep 5 or more with a score of 5+)

| Signal | Points |
|---|---|
| It asks what our page answers | 0–3 |
| Posted in the last 24 months | 0–2 (older = 0) |
| Replies (10+ = 2, 3–9 = 1) | 0–2 |
| UK signal (UK place, £, UK law, UK subreddit or forum) | 0–1 |

**Recency:** prefer threads posted in the last 24 months. The ONLY way an older thread
enters is this exception: fewer than 5 recent threads clear the bar. Then older ones may fill
the gap, each marked `"stale": true` in the `threads` list. No other reason — a better fit,
more replies, a UK signal — lets an older thread in.

**UK signal:** a thread with no UK signal scores 0 for UK, whether or not it is provably US.
A question whose only source threads all score 0 for UK signal is dropped (not written to
`questions`); it may stay only if a UK-scoring thread, or another source type, asks it too.

## Step D — open and verify

Load each kept thread. Confirm the title, the subreddit or forum, the posted month, the reply
count and that it is live. From the opening post and the top replies, write each buyer
question as a plain question in your own words (a paraphrase, never a quote over 15 words).
Record the permalink.

## Step E — write the file

`data/queries/raw/<slug>/threads.json`:

```json
{
  "source": "threads",
  "status": "ok",
  "fetched": "YYYY-MM-DD",
  "questions": [
    {"text": "How do I know a Staffy breeder is not a puppy farm?",
     "detail": "thread:https://www.reddit.com/r/…/comments/<id>/…/", "fact_source": null}
  ],
  "threads": [
    {"permalink": "https://www.reddit.com/r/…/comments/<id>/…/", "title": "…",
     "subreddit": "r/…", "posted": "YYYY-MM", "replies": 0, "score": 0, "stale": false}
  ]
}
```

- Every question's `detail` is `thread:<permalink>` of a thread in the `threads` list.
- Every thread you used is in `threads` with all seven keys; `subreddit` holds the forum name
  for a forum thread; `score` is the Step C total, not a vote count.
- `status` is `ok`, `fallback` (only the lower rungs worked) or `NOT FETCHED` (write the file
  with empty `questions` and `threads` lists and say which rungs failed).

## Linking `fact_source`

`fact_source` is `null` unless a `data/faq.json` row's answer answers the paraphrased
question **as asked** — the same question, not the same topic. Then, and only then, it is
`bank:<id>`. Open the row and read its answer before linking. Never a bare file path. Never a
fact taken from the thread.

## Standing rules

- Threads give QUESTIONS and LANGUAGE, never facts. A price, a health claim, a licence or a
  law comes from the data files and the evidence ledger, never from a thread.
- Never link or name another breeder, a marketplace listing or a poster.
- Citing a thread on a page is allowed only when it is on-topic, civil, UK, and adds
  something the page cannot say itself — and the link is anchor-first like every link.

## Common mistakes

- Reporting `NOT FETCHED` after the first rung.
- Spending calls rediscovering the ladder — Step B's table already says which rung works.
- Recording a question from a search snippet without opening the thread.
- Quoting a poster at length instead of paraphrasing the question.
- Treating a thread's advice as a fact for the page.
- Using a thread older than 24 months while 5 recent ones exist, or leaving an old one
  without `"stale": true`.
- Keeping a question because its thread is "not provably US" — if every thread it came from
  scores 0 for UK signal, drop it unless a UK-scoring thread or another source type asks it.
- Writing `questions` with no `threads` audit list, or a thread missing its `posted`,
  `replies` or `score`.
- Linking `bank:<id>` because the row is on the same topic — it must answer the question.
- Writing browser logs or snapshots into the repo.
