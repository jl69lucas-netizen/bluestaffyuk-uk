# Competitor intelligence — registry, intel, keyword gap, LLM intel and strategy — design

Status: approved in brainstorm 2026-09-23. Branch `competitor-intel`, cut from `foundation`
at `db37ca1` and rebased onto `c9c981c` after `query-augmentation` merged (this build reuses
that build's spend guard). Closes Known Issue 42. A bridge build before project 5: the gap
matrix and the chosen strategy are what the 28 city pages, the comparison cluster and the two
blog posts get planned from.

## 1. Why these agents were not ported

Project 2 (system transfer) put "the marketing, email, social and competitor agents" out of
scope (its spec §10). `data/port-manifest.json` records `competitor-intel`,
`competitive-keyword-gap-agent`, `llm-keyword-intel` and `strategy-synthesizer` as `deferred`
("project 6 at the earliest"); `competitor-registry` and `competitor-pricing-alert-agent` were
never recorded at all (they are among the ten unrecorded files `query-augmentation` Task 12
catches).

The underlying reason: the chain is data-bound. Each agent reads what the one before it wrote
(`data/competitors.json` → per-competitor reports → gap matrix → strategy), plus a GSC baseline.
All of the source repo's data is US parrot data that BSUK's fact lint bans, and GSC is not
fetchable while the domain is expired. Porting the prompts alone would have produced agents
with nothing to read. Since then competitor research has been done by hand per page under
seo-rules Rule 11, and `WORKFLOW.md` still names the missing agents.

Faults found in the source versions, fixed here rather than copied:

- The registry prompt says 30 competitors in 4 tiers; the source registry holds 60 in 6 tiers.
- Competitor-intel category 3 and the keyword-gap agent produce the same gap list twice, each
  with its own fetches.
- Every count ("8/30 competitors") is typed by the model; nothing checks it.
- The synthesizer's "never fabricate a number" is a sentence, not a check.
- LLM intel calls four vendor APIs by key; BSUK has none of those keys.

## 2. Decisions

| # | Decision | Picked |
|---|---|---|
| 1 | Scope | Registry, competitor-intel, keyword-gap, strategy-synthesizer and LLM keyword intel. Pricing alert, rank tracker, branded search, GSC analytics stay deferred to project 6 |
| 2 | LLM engine access | The DataForSEO connector (ChatGPT scraper, `llm_mentions`, `llm_response`) through the existing spend guard. No new keys |
| 3 | Registry size | About 25, at most 30, in five tiers (§4) |
| 4 | Approach | Agents fetch and judge; scripts count, build the matrix and check citations; schema + tests guard the data |
| 5 | Names | The five agents keep the `bsuk-` names `WORKFLOW.md`, the manifest and existing handoffs already use |
| 6 | Geography | The 28 cities of `data/locations.json` replace the source's 22 US states |
| 7 | Marketplaces | Count as competitors (user ruling during `query-augmentation`) |

## 3. Data flow

```
bsuk-competitor-registry ──► data/competitors.json      (after the user approves the list)
        │
        ▼
bsuk-competitor-intel ──► docs/research/competitors/<id>.json + <id>.md
        │
        ▼
scripts/gap_matrix.py ──► docs/research/gap-matrix-<date>.md
        │
bsuk-competitive-keyword-gap-agent ──► docs/research/keyword-gap-<date>.md
        │
bsuk-llm-keyword-intel ──► docs/research/llm-intel/<slug>-<date>.json
        │
        ▼
bsuk-strategy-synthesizer ──► docs/superpowers/sessions/<date>-<topic>-strategy.md
        │                     (checked by scripts/strategy_cite_check.py)
        ▼
bsuk-content-architect (framework + builder routing); grill-me and bsuk-framework-agent read
the gap matrix per page
```

Each step reads files only; none re-runs an earlier step. A missing or stale input (older than
30 days) is flagged in the output's first lines and the step carries on with what exists.

## 4. The registry

`data/competitors.json`, contract in `schemas/competitors.schema.json`:

```json
{
  "_meta": { "last_discovery_run": "2026-09-24", "seed_keywords": ["..."], "total": 25 },
  "competitors": [
    {
      "id": "pets4homes",
      "name": "Pets4Homes",
      "root_domain": "pets4homes.co.uk",
      "tier": 2,
      "seed_hits": [{ "keyword": "blue staffy puppies for sale", "position": 1 }],
      "cities": ["Manchester"],
      "priority": "high",
      "link_allowed": true,
      "last_analyzed": null,
      "notes": ""
    }
  ]
}
```

Tiers: 1 breeder · 2 marketplace or directory · 3 breed-information site · 4 rescue or
non-commercial · 5 suspect seller (tracked for contrast, never linked).

Priority: high when found on 5+ seed keywords, or a tier-1 breeder in the top 3; medium on 2–4;
low on 1.

Seed keywords (about ten, final list set in the plan): blue staffy puppies for sale ·
staffordshire bull terrier puppies for sale uk · blue staffy breeder · staffy puppies for sale
in the five largest `locations.json` cities · KC registered staffy puppies · staffy puppy price
uk · blue staffordshire bull terrier.

Discovery: Google organic through the DataForSEO connector first; Firecrawl search as the
fallback. Bing through DataForSEO is not used (the `query-augmentation` pilot returned results
for "blue" alone). Results are grouped by root domain and ranked by how often they appear. The
proposed list goes to the user as a board; the file is written only after "approved".

`tests/py/test_competitors_registry.py`: schema valid; 30 entries at most; root domains only
(no path, no subdomain but `www` stripped); no duplicate domain; never the site's own domain;
tier 5 always `link_allowed: false`; every city is in `data/locations.json`; `seed_hits`
non-empty.

## 5. Competitor intel

Modes: `<id>`, `--tier <1-5>`, `--all`. Ten categories from the source, re-based:

1. Trust signals — council breeding licence shown, KC registration, health tests named
   (e.g. L-2-HGA, HC), vet checks, years breeding, address town, phone, reviews count.
2. Content depth — homepage words, URL count from `firecrawl_map`, H2 blocks per key page.
3. Keyword use — transactional, informational, city modifiers, comparison phrases.
4. Page types — breed guide, care guides, comparison, city pages, blog, FAQ, about, listings,
   reviews, contact; count of each.
5. Blog — post count, topics, rough frequency, sample word counts.
6. Visual assets — image counts, video, alt-text quality.
7. Schema — JSON-LD types present.
8. Geography — which of the 28 cities they have a page or a mention for.
9. Conversion — CTA type, £ prices shown, deposit terms, steps to enquire, urgency.
10. Technical — mobile, a Lighthouse run where reachable.

Output per competitor: `docs/research/competitors/<id>.json` (every field a script counts;
`"NOT FETCHED"` where a fetch failed) and `<id>.md` (readable report ending in one key
insight). `last_analyzed` is updated in the registry. Fetching: Firecrawl first, Playwright
second. No figure is estimated; competitor wording is summarised, never copied.

## 6. Gap matrix

`scripts/gap_matrix.py` reads every `docs/research/competitors/*.json` plus `data/page-map.json`
and writes `docs/research/gap-matrix-<date>.md`: keyword gaps, page-type gaps, city gaps, schema
gaps, each row with `N/M` where M counts only competitors whose field was fetched, and a
separate `not fetched` column. Priority: high at 40%+ of fetched competitors, medium 20–39%,
low below. The matrix ends with a priority queue of the top ten rows. `--check` re-derives the
matrix and fails if the committed file differs (added to `check:all`).

## 7. Keyword gap

Reads the page lists in the intel `.json` files; fetches again only when a list is older than
30 days. Compares competitor pages against `data/page-map.json`. Scoring from the source:
dedicated page +3, in the competitor's top pages +2, BSUK has no page +3, buyer intent +2;
7+ high (goes to `bsuk-content-architect`), 4–6 medium, below 4 low. Every gap names the
competitor URL that proves it. Output `docs/research/keyword-gap-<date>.md`. Licence and
health-testing content gaps are always high (trust content).

## 8. LLM keyword intel

Input: a slug; its queries come from the page's question file (`data/queries/<slug>.json`) or,
failing that, its primary keyword and the matching gap-matrix rows. One engine per page (the
`query-augmentation` rule), ChatGPT scraper by default with UK location; `llm_mentions` for
domain-level citation counts. Three layers from the source: entities the answers use that the
page lacks (3+ answers → high), citations (is BSUK cited; which registry competitors are;
citation gap when a competitor is and BSUK is not), and answer format (the mirror template).
Output `docs/research/llm-intel/<slug>-<date>.json`, with the raw response kept under
`data/queries/raw/<slug>/`.

## 9. Strategy synthesizer

Kept from the source: exactly two materially different strategies; each with thesis, target
clusters, cluster-to-page map, internal-link plan, schema plan, build order, expected outcome,
risks; one recommendation with a WHY of 3+ data points and the pick's named downside; the first
three build steps; a concrete artefact table when asked (topic · keyword · score · intent ·
link role). Reads research only.

`scripts/strategy_cite_check.py <strategy.md>`: every number and every `N/M` in the
recommendation and artefact table must appear in a file the strategy lists under
`## Sources`; each source must exist. Fails with the offending line. The synthesizer runs it
before handing off; a failed check means the strategy is not handed off.

## 10. Spend

Paid calls go through the existing guard in `scripts/query_augment.py`: `--preflight SLUG
--source SOURCE` before the call, `--record ...` straight after it. As merged, the guard caches
one response per `(slug, source)` pair, only `serp_google` and `ai_engines` are payable (Bing is
never bought), and two caps apply: `query_budget_usd` $0.50 per slug per day and
`query_total_budget_usd` $1.00 over the whole log.

This build reuses those two source names instead of adding new ones. Each registry seed keyword
gets its own pseudo-slug, `_registry-<keyword-slug>`, so each is cached on its own and the
per-slug cap never binds; LLM intel records under the page slug with source `ai_engines` (a page
that already has an `ai_engines` response from query augmentation reuses it — exit 3 — rather
than paying again).

Estimates: ten registry searches about $0.50 at the logged $0.05 per call; LLM intel about $0.10
per page. The log holds $0.20, so the total cap leaves $0.80 — enough for the pilot (§13 step
12). The user's dashboard read $0.90 on 2026-09-23; if the starting balance was $1.00, the three
pilot calls really cost about $0.10 together, and Known Issue 45 can set
`query_typical_call_usd` from that once the user confirms the starting figure. The controller
asks for the balance again before the first paid run. Firecrawl credits are separate and
reported at the end of each intel run.

## 11. Failure handling

| Failure | Behaviour |
|---|---|
| Over budget | Spend guard exit 4; the agent stops and asks. Never falls back to a guess |
| Cached result | Exit 3; the cached response is reused |
| Fetch fails (Firecrawl, then Playwright) | Field recorded `NOT FETCHED`; counted separately in the matrix |
| Input missing or older than 30 days | Flagged at the top of the output; step continues |
| Registry, matrix or citation check fails | `check:all` fails; nothing downstream reads the data |
| Tier-5 competitor | May be analysed; never linked (link guard in §12) |

## 12. Guards

- `tests/py/test_competitors_registry.py` (§4).
- `gap_matrix.py --check` and a registry schema check in `check:all`.
- `strategy_cite_check.py` (§9) with its own tests.
- The external-link checks refuse any outbound link to a tier-5 `root_domain`.
- The five agent files pass the existing name/frontmatter test, marker gate, fact lint,
  path guard and stale-marker checker (no parrot residue, locked £ only, no invented facts).
- `data/port-manifest.json`: the five entries move from `deferred` to `rebase` with notes. The
  registry row's current note ("BSUK records competitors per page in `data/queries/<slug>.json`
  instead — not ported") is replaced: the per-page pool stays as it is and feeds the page's
  section count; the registry is the national list the gap matrix counts against. The
  pricing-alert row stays `deferred`.
- `WORKFLOW.md`: the "deferred to project 6" notes for the five agents are replaced with how
  to run them.

## 13. Build order

1. Rebase onto `foundation` after `query-augmentation` merges (done: `c9c981c`).
2. Registry schema + test (TDD).
3. `gap_matrix.py` + tests on fixture reports.
4. `strategy_cite_check.py` + tests.
5. Spend-guard source names + tests.
6. Registry agent.
7. Competitor-intel agent.
8. Keyword-gap agent.
9. LLM-intel agent.
10. Strategy-synthesizer agent.
11. Link guard, manifest, `WORKFLOW.md`, `check:all` wiring.
12. Live pilot (user-approved): registry discovery → board → approval → intel on three
    competitors → gap matrix → LLM intel for the Manchester page → one strategy.
13. Close-out: full run on the approved registry only if the user asks; gate report.

Agents written with `superpowers:writing-skills`; scripts by
`superpowers:test-driven-development`; each task implemented by an Opus subagent with spec and
quality review.

## 14. Testing

Python tests with fixtures and no paid calls: duplicate domains, subdomain stripping, an
unknown city, tier-5 `link_allowed`, `NOT FETCHED` excluded from `M`, matrix `--check` drift,
a strategy quoting a figure found in no source, a listed source that does not exist, spend
guard refusing an unknown source name. Agent files through the existing instruction-tree
tests. The live pilot (build step 12) is the end-to-end test; the user reviews its output
before any full run.

## 15. Out of scope

Pricing alert, rank tracker, branded-search monitor and GSC analytics (project 6, once the
domain is live); financial and social strategists; `bsuk-visual-intelligence`; Reddit-modifier
pages; running intel on all 25 competitors (only on request after the pilot).
