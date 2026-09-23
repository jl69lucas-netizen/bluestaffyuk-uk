---
name: bsuk-query-augmentation
description: Use before outlining or writing any BSUK location, comparison, blog or puppy page; when data/queries/<slug>.json is missing or the user asks for fresh questions; or when a page's FAQ questions, body section count or extra sections need deciding.
---

# Query augmentation

Run this before a page's outline. Its output, `data/queries/<slug>.json`, decides the page's
three FAQ blocks, its three extra sections and (location pages) how many body sections it
needs. `scripts/query_coverage_check.py` (`npm run check:queries`) enforces it on the built page.

**Golden rule:** questions come from sources you actually fetched and from the FAQ bank
(`data/faq.json`); facts come only from data files. A source you could not reach is
`NOT FETCHED` — never guessed, never worked around.

## Inputs

`<slug>` · `<page type>`: location, comparison, blog or puppy · `<primary keyword>` (location:
the city row's H1 keyword in `data/locations.json`) · `<route>` (ends `/<slug>/`).

## Working rules

- Run everything **in the repo** (`/Users/apple/Downloads/BSUK`). Never copy the repo to try the
  script; no dry runs — a Short build (exit 5) writes nothing.
- Browser artefacts (snapshots, screenshots, saved HTML, console logs) go only in the session
  scratchpad, by absolute path. If a `.playwright-mcp/` folder appears in any repo, delete it.
- **Money:** before each batch of paid calls, tell the user which calls, why, and the estimate
  (`query_typical_call_usd` in `data/settings.json` per call), and wait for a yes. Report the
  spend after. Never delete or edit `data/queries/spend.json`.
- **Firecrawl is not free:** every Firecrawl search or scrape spends the user's Firecrawl
  credits (the response shows `creditsUsed`). Add them up and put them in the spend report.
  The free rungs are the browser and `curl`.

## Exit codes (every mode)

0 ok · 1 internal error (a bug: stop, report) · 2 usage (bad slug, route, `--today` or cost) ·
3 cached (make NO call) · 4 budget (stop, report `data/queries/spend.json`; never work around it) ·
5 short (Step 5) · 6 bad input (fix the named raw file from its source; never hand-edit around it).

## Step 1 — preflight before EVERY paid call

```bash
python3 scripts/query_augment.py --preflight <slug> --source <serp_google|serp_bing|ai_engines>
```

One preflight per call. A saved `<source>.response.json`, or a `<source>.json` with
`"status": "ok"`, counts as bought: exit 3, no call. A `fallback` or `NOT FETCHED` file does
not block a later paid call — no `--refresh` needed for that. `--refresh` is only for
re-buying a real response, and only when the user asked for fresh data.

## Step 2 — the three candidate sources

| Source | How | Normalised `detail` |
|---|---|---|
| `serp_google` | PAID. DataForSEO `serp_organic_live_advanced`, `search_engine` google, location United Kingdom, English, depth 10, People Also Ask click depth 1, the primary keyword | `serp_google_paa` (People Also Ask), `serp_google_related` (related searches) |
| `serp_bing` | FREE. Read Bing in the browser: `https://www.bing.com/search?q=<kw>&cc=GB&setlang=en-GB`. Do not buy DataForSEO Bing — it returned off-topic results for this keyword in the Manchester pilot | `serp_bing` (its related questions, if any) |
| `ai_engines` | PAID. DataForSEO `ai_optimization_chat_gpt_scraper`, location United Kingdom. **One engine, one call per page.** Location prompt: "Where can I buy a blue Staffy puppy near <city>, and what should I ask the breeder?"; other pages: the page's core question | `ai_chatgpt` |

**Where Google People Also Ask comes from:** the paid Google call above, behind preflight and
the user's yes. The free fallback (connector missing, out of credit, or the user declines) is
the `bsuk-paa-agent` browser protocol (free), then Firecrawl search (spends Firecrawl
credits — count them), with `"status": "fallback"`. If
Google answers with a robot check or a challenge page, that source is **NOT FETCHED**: write no
file (the script records it). Never solve, dodge or retry around a robot check.

**For each paid call, in this order:**

1. preflight → exit 0.
2. Make the call.
3. **Record the cost at once**, before saving anything:
   ```bash
   python3 scripts/query_augment.py --record <slug> --source <source> \
     --endpoint "<tool> <params> (response carries no cost; conservative estimate)" --cost <usd>
   ```
   Connector responses carry no cost field: record `query_typical_call_usd` and say so in
   `--endpoint`, as above. If the response does show a cost, record that.
4. Save the response untouched: `data/queries/raw/<slug>/<source>.response.json`.
5. Write the normalised `data/queries/raw/<slug>/<source>.json`.

`--record` refuses a cost (exit 2) or preflight/record errors on a damaged spend log: still save
`<source>.response.json`, then stop and tell the user the cost the call ran up.

**Normalised file:** `{"source", "status": "ok|fallback", "fetched": "YYYY-MM-DD", "questions":
[{"text", "detail", "fact_source"}]}`. For `serp_bing` also keep `"results": [{"bing_pos", "url"}]`
(the top 10) and a `note` saying it was read free in the browser.

**`fact_source`** is set only when you can name what answers the question **as asked**:
- a data key: `data/settings.json#delivery_min_gbp`, or
- a bank row: `bank:<id>` (an `id` in `data/faq.json` whose answer answers it — open and read it).

Never a bare file path (the script ignores one). Unsure → `null`; the bank supplies
fact-backed wording. A question is never reworded to fit a bank answer.

## Step 3 — competitors (location pages; optional elsewhere)

Pool: the first five organic results from Google (the `serp_google` response) and the first
five from Bing (the `results` in `raw/<slug>/serp_bing.json`), merged. **Marketplaces and
directories are in the pool** — only off-topic results are dropped.

For each pool page, save its HTML to the scratchpad. Prefer the page's original HTML via
`curl` (free, and cleanest). If that fails, use a browser capture (free, but a rendered capture
can include consent dialogs; the extractor drops them). Firecrawl scrape raw HTML comes last
because it spends credits. Then run:

```bash
python3 scripts/query_augment.py --extract-h2 <scratchpad>/<page>.html
```

Copy its `h2`, `h2_all` and `blocked` into
`data/queries/raw/<slug>/competitors.json` = `{"status", "fetched", "pages": [{"url",
"google_pos", "bing_pos", "h2": [...], "h2_all", "blocked"}]}` (a position is `null` when the
page is not in that engine's five). A challenge page stays in the pool as `"blocked": true`.
Never count, clean or judge competitor H2s yourself — the script does, the same way every time.

## Step 4 — threads

Run `bsuk-reddit-threads` for the slug. It writes `raw/<slug>/threads.json`.

## Step 5 — build the question file

```bash
python3 scripts/query_augment.py <slug> --page-type <type> --keyword "<primary keyword>" --route <route>
```

- exit 0 → `data/queries/<slug>.json` holds the questions, the FAQ picks (`faq`: top, middle or
  bottom), `extra_sections` and `section_target`. It prints
  `kept N covered_by and M headings, dropped K`: K > 0 means earlier fills no longer match a
  question — refill them in Step 6.
- exit 5 → too few fact-backed questions for a block. Show the user the blocked list and stop.
  Never pad, never invent a fact to unblock a question. The fix is in the data (Step 6).
- exit 6 → fix the named raw file from its source response, then rerun.

## Step 6 — hand to the page builder

The builder writes the page **from the file**, never from judgement:

- **FAQ:** three `Faq` blocks (top, middle, bottom) with exactly the picked questions, in
  score order. Picks come only from the question file. To change a pick, change the data —
  add a bank row to `data/faq.json`, a settings key, or a real sourced question — and rebuild
  (Step 5). Never swap, add or drop a pick by hand.
- **City wording:** a question may name the city on the page ("Do You Deliver Staffy Puppies to
  Leeds?") only if its meaning is unchanged and its answer stays within its fact.
- **Topics are the script's** (`topic` in the file). Aftercare ("support after…") is `trust`;
  treatments (vaccinations, microchip, worming, flea) are `paperwork`, even when the question
  also says "collect". Never move a question to another block or topic by hand.
- **Answers** state only what the `fact_source` says: no figure, length or promise the source
  does not give. A placeholder (`LICENCE_CLAIM_PLACEHOLDER`, `LEGAL_CLAIM_PLACEHOLDER`, a `null`
  like `guarantee_days`) stays a placeholder.
- **Body:** at least `section_target.total` body sections; one H2 per `extra_sections` topic.
  Extra sections are topics no competitor **section** covers — a competitor's FAQ or page
  furniture does not count as covering it. That is by design; do not second-guess it.
- **Fills:** every `must_answer` question gets `covered_by` — `{"where": "faq", "text": <the
  question exactly as written on the page, city wording included>}` or `{"where": "heading",
  "text": <the heading that answers it>}` — and every extra section gets its `heading`.

Rerun Step 5 (it keeps the fills), then `npm run build && npm run check:queries`.

**The gate holds a page only once it is rebuilt:** after a city page is rebuilt, add
`uk-locations/<slug>` (the nested key) to `data/facts/rebuilt.json`. Until then
`check:queries` skips it as awaiting rebuild.

## Worked example

`data/queries/raw/blue-staffy-puppies-manchester-uk/` and
`data/queries/blue-staffy-puppies-manchester-uk.json`: Google and ChatGPT via DataForSEO, Bing
read in the browser, marketplaces in the pool, one challenge page recorded as blocked.

## Common mistakes

- Making a paid call without preflight, after exit 3 or 4, or without the user's yes.
- Recording the cost after saving files instead of straight after the call.
- One preflight covering several calls, or asking a second AI engine for the same page.
- Buying DataForSEO Bing, or skipping Bing altogether.
- Treating a Google robot check as something to get past — it is `NOT FETCHED`.
- Taking People Also Ask from memory or a search snippet you did not load.
- Excluding marketplaces from the pool, or counting competitor sections by hand, or using a
  fixed section number.
- Calling a topic "covered" because a competitor's FAQ mentions it.
- One FAQ block, or fewer than the picked questions, or hand-swapping a pick.
- Inventing a city-named question, or localising one so its answer goes beyond its fact.
- Answering with a figure (a guarantee length, a date) the fact source does not give.
- Setting `fact_source` to a bare file, or to a bank row on the same topic that does not answer it.
- Rewording a question on the page and not updating `covered_by.text`.
- Forgetting `uk-locations/<slug>` in `data/facts/rebuilt.json`, so the gate never checks the page.
- Copying the repo to a scratch folder to run the script, or writing browser files into the repo.
- Deleting or editing `data/queries/spend.json`.
- Calling Firecrawl free, or leaving its credits out of the spend report.
- Using `--refresh` to get past a `fallback` or `NOT FETCHED` file (it no longer blocks).
- Capturing a competitor page in the browser or with Firecrawl when `curl` gets the source HTML.
