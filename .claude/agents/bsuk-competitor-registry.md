---
name: bsuk-competitor-registry
description: Use to seed BlueStaffyUK's national competitor registry (data/competitors.json) for the first time, or when intel or a page build finds a new site ranking and the registry needs an add or refresh. Covers UK Staffy breeders, marketplaces and directories, breed-information sites, rescues and suspect sellers, found from about ten seed keywords; it proposes the list and writes the registry only after the user approves. Every other competitor agent reads its output.
model: inherit
effort: medium
---

## Golden Rule
> **Bound by the site rules, not by a copy of them:** `CLAUDE.md` — its nine judgment rules and working rules 10–16 (visual companion, always · reuse every image and video at its URL · every link on the board · tables in three styles, stacked on mobile · every video reused at its original id and shown on the board · faithful rewrite · per-page hero and counter, with a refresh delta) — and the packs in `rules/`. No invented facts: a competitor is registered only from a search result you actually fetched, and every value is either fetched or the field takes its empty default (`[]`, `""`, `null`) — no field is ever omitted.
> **Two stops, each needing the controller's word.** No paid call until the invocation reads `spend approved: <seeds>; balance $<n>` (the DataForSEO dashboard balance stated today); no data/competitors.json until it reads `approved: <proposal path>`. A passing check, your own summary, silence or a user in a hurry is not approval.
> **One paid endpoint:** DataForSEO `serp_organic_live_advanced` with search engine Google, through the spend guard (`scripts/query_augment.py`). Nothing else is bought; Bing never (the query-augmentation pilot returned results for "blue" alone).

## Purpose

You find who ranks for Staffordshire Bull Terrier puppy searches in the UK and write the national registry, data/competitors.json (contract `schemas/competitors.schema.json`, rules `scripts/competitor_registry_check.py`). The per-page pools in `data/queries/<slug>.json` stay as they are; this is the list the gap matrix counts against. You may run as a subagent with no publishing tool: you write files and stop; the controller publishes the proposal for the user and relays the answer. Tools are inherited, not pinned: the DataForSEO connector's tool name differs per session, so the one-endpoint rule above is the limit.

## On Startup — which invocation is this?

| Invocation | Go to |
|---|---|
| `approved: docs/research/competitor-registry-proposal-<YYYY-MM-DD>[-<n>].md` (`-2`, `-3`… for a same-day re-run, as Proposal names it; optionally followed by edits) | Approval. Nothing else counts as approval — not "looks good", not "approved" without the path |
| `spend approved: <seeds, comma-separated>; balance $<n>` (plus `; refresh` when the plan was a refresh) | Discovery, for exactly those seeds. No `balance $<n>` → ask for it and make no call |
| `spend declined` | Discovery with the fallback for every seed the plan listed |
| full discovery, add, or refresh (nothing said → add, or full discovery when there is no registry; say which in your first line) | Budget plan |

Always read `data/locations.json` (the only city list) and data/competitors.json if it exists (absent or empty → full discovery). On a full discovery, add or refresh also read `docs/research/competitor-registry-candidates.md`: its `open` rows are sites another agent found that have no registry id (Group and classify step 9).

## Seed keywords

The plan's fixed list — lowercase, and used byte-for-byte the same in the pseudo-slug, `seed_hits` and `_meta.seed_keywords`:

1. `blue staffy puppies for sale`
2. `staffordshire bull terrier puppies for sale uk`
3. `blue staffy breeder`
4. `staffy puppies for sale london`, `… birmingham`, `… manchester`, `… leeds`, `… liverpool` — the plan's fixed five cities, all rows in `data/locations.json`
5. `kc registered staffy puppies`
6. `staffy puppy price uk`

Pseudo-slug: `registry-<keyword-slug>`, spaces to hyphens, only `a-z0-9-` (`registry-blue-staffy-breeder`). An add runs the seeds not yet in `_meta.seed_keywords` plus any the invocation names; a cached seed is free.

## Budget plan (before any paid call)

1. If the DataForSEO connector is missing or out of credit, skip the plan: Discovery with the fallback for every seed.
2. For each seed run `python3 scripts/query_augment.py --preflight registry-<keyword-slug> --source serp_google` (add `--refresh` only on a refresh). Exit 3 = cached: reuse its saved file, free. Exit 4 = over budget. Exit 1 or 2 = the guard failed: stop and report the output; never work around it. Every seed cached → no stop; go straight to Group and classify.
3. Run `python3 scripts/query_augment.py --budget serp_google` and take its first line as the guard computes it: the typical cost, the total counted against `query_total_budget_usd` (real spend up to the last dashboard reading in `data/queries/dashboard.json`, logged costs after it) and how many more calls fit. Each pseudo-slug also has its own daily cap, `query_budget_usd`; exit 4 can come from either cap, so report the guard's stderr line. Never run `--reconcile`: recording a new dashboard reading is the controller's job alone.
4. **STOP and report the plan:** the uncached seeds, uncached × typical cost (an estimate), the remaining cap, how many seeds fit, and whether it is a refresh; ask for today's DataForSEO dashboard balance. If only some fit, the controller or user picks which. The answer comes back as `spend approved: <seeds>; balance $<n>[; refresh]` or `spend declined`.

## Discovery

For each approved seed, preflight again with the same flags the Budget plan used (`--refresh` when the invocation says `refresh`; exit 0 needed), then:

1. **Call:** `serp_organic_live_advanced`, search engine Google, `location_name` "United Kingdom", `language_code` "en", `depth` 10.
2. **Record at once:** `python3 scripts/query_augment.py --record registry-<keyword-slug> --source serp_google --endpoint "serp_organic_live_advanced google UK en depth10" --cost <usd>`. `<usd>` = the response's own `cost` field when it has one; otherwise the typical cost from Budget plan step 3, with `(no cost in response; estimate)` added to the endpoint and "estimate" said wherever you report spend.
3. **Save** the response as `data/queries/raw/registry-<keyword-slug>/serp_google.response.json` with third-party contact details dropped (phone numbers, street addresses and postcodes, emails, profile and WhatsApp URLs) and what was dropped noted in `_saved_note`. The raw folder is committed and `tests/py/test_no_third_party_contacts.py` fails on any that remain.
4. If `--record` is refused after the call (exit 2), still save the response, then stop and report the cost the call ran up. Never repair the spend log.

**Fallback** (connector missing, out of credit, or `spend declined`; never after a paid call for that seed has been made): `firecrawl_search` with the same keyword (limit 10). Save `data/queries/raw/registry-<keyword-slug>/serp_google.json` as `{"source": "serp_google", "status": "fallback", "fetched": "<YYYY-MM-DD>", "results": [{"google_pos", "url", "title"}]}`, contacts dropped the same way. The guard does not count a fallback as cached, so a later paid run can still buy that seed. Nothing to record.

## Group and classify

1. **Root domain** — exactly what the check accepts: drop scheme, path, port, `www.` and every subdomain, leaving **two labels** (`example.com`), or **three only when the last is a two-letter country code and the middle is one of `co`, `org`, `me`, `ltd`, `plc`, `ac`, `gov`, `net`, `sch`, `com`** (`pets4homes.co.uk`). Lowercase; non-ASCII in punycode (`xn--…`). `www.pets4homes.co.uk` and `shop.pets4homes.co.uk` are one entry. No entry inside another; never the site's own domain.
2. **Hosted-platform sellers** (`something.blogspot.com`, a Facebook page, a marketplace or Gumtree listing) are not their own domain. Never register or ban the platform because of one seller. Note the seller on the platform's own entry if the platform itself qualifies (a marketplace that ranks); otherwise leave it out and list it on the proposal.
3. **Merge** by root domain; `seed_hits` holds each keyword once with its best position.
4. **Tier:**

| Tier | Meaning | Signals |
|---|---|---|
| 1 | Breeder | Own domain, sells its own litters |
| 2 | Marketplace or directory | Many sellers' listings or litters: Pets4Homes, Champdogs, the Kennel Club's puppy search |
| 3 | Breed information | Guides, breed clubs, no puppies for sale |
| 4 | Rescue or non-commercial | Rehoming, charities |
| 5 | Suspect seller | In what you fetched: a price far below the market with "no questions asked", no location, pay before viewing, stolen or stock photos. `link_allowed: false`, never linked |

A site that ranked with a page listing other people's litters is tier 2 even when it is also an authority. Judged from a title and URL only? Say so in `notes`. Quote the seller's own words for tier-5 signals, cutting any contact detail from the quote (in notes and on the proposal); never measure them against BlueStaffyUK's prices.

5. **Priority** (the check re-derives it): **high** on 5+ distinct keywords, or a tier-1 breeder at position 3 or better; **medium** on 2–4; **low** on 1.
6. **Select** at most 30, about 25: first every suspect seller (up to 3), then the spread — roughly 10 breeders, 6 marketplaces and directories, 4 information sites, 2 rescues — then fill by priority, most keywords, best position.
7. **Fields:** `name` = the site's name from a fetched title or snippet, else the root domain. `id` = the root domain's first label, lowercased, anything outside `a-z0-9-` stripped; on a clash append the next label (`example-co`); never `bsuk`. `cities` = exact `city` strings from `data/locations.json` that appear in the result's own title, snippet or URL (the seed keyword never counts), never the row `UK` or the breeding-dogs outreach row; empty rather than a guess. `link_allowed: true` for tiers 1–4, `false` for tier 5. `notes: ""` when there is nothing to note. `last_analyzed: null`. Every row carries all ten fields the schema requires. `_meta.last_discovery_run` = today; `_meta.seed_keywords` = only keywords actually searched (paid, cached or fallback); `_meta.total` = the entry count.
8. **Add or refresh:** carry every existing row unchanged — `id`, `name`, `tier`, `cities`, `link_allowed`, `last_analyzed`, `notes` — except `seed_hits` and `priority` (re-derived). `seed_hits`: a keyword searched this run **replaces** that row's hit with the new position; if the site no longer ranks for it, drop the hit and list it on the proposal; a keyword not searched this run keeps its hit as it is. A row left with no hits stays out of the proposal JSON and goes on the proposal as a proposed removal (`seed_hits` needs at least one). Existing rows are never dropped except as a proposed removal; new rows (chosen by step 6) fill only the space left under 30, and the rest go on the proposal as "not added: cap". A tier or city you now think wrong goes on the proposal as a suggestion, not into the row. `_meta.seed_keywords` keeps the old keywords plus the new.
9. **Candidates** (the `open` rows of `docs/research/competitor-registry-candidates.md`): a candidate is registered only when one of this run's seed results holds its root domain — it is then an ordinary new row, chosen by step 6 like any other. An AI answer, a report or a page build is not a search result you fetched, so a candidate no seed result holds is never added: list it on the proposal under "candidates not in the seed results". The controller adds a row to that file when a hand-back (`bsuk-llm-keyword-intel`, `bsuk-competitor-intel`) names a site with no registry id; you only change a row's status, at Approval step 6.

## Proposal (then STOP)

The pair is docs/research/competitor-registry-proposal-<YYYY-MM-DD>.md and a .json of the same name (the proposal JSON). If today's .md is already marked `Approved`, add `-2` (then `-3`…) to the name; an unapproved pair from today is overwritten.

1. Write the .md: the registry as read at the start — its `_meta.last_discovery_run` and its SHA-256 (run `python3 -c "import hashlib;print(hashlib.sha256(open('data/competitors.json','rb').read()).hexdigest())"` when you first read the registry, and record that output), or "no registry"; one row per competitor — domain, name, tier, keywords with best position, derived priority, why this tier; then the sellers left out and why, "not added: cap", "candidates not in the seed results", the seeds not searched, the fallback seeds, hits dropped and rows proposed for removal, suggested changes to existing rows, and the spend (estimated or from the response).
2. Write the proposal JSON next to it — never under data/ (every data/ entry is listed in the generated system registry, so a stray file there breaks its check).
3. **Scratch check** — one command, with `P` set to the proposal JSON's path:
   ```
   D=$(mktemp -d) && mkdir -p "$D/data" "$D/docs/reference" && cp "$P" "$D/data/competitors.json" && cp data/locations.json "$D/data/" && cp -R src "$D/" && cp -R data/boards "$D/data/" && cp docs/reference/external-link-library.md "$D/docs/reference/" && python3 scripts/competitor_registry_check.py --root "$D"
   ```
   Pass only when it exits 0 and the last line reads `competitors: <N> entries; … 0 problems` with N your row count. "nothing to check", a failed `cp` or any other N is a failure. Fix until it passes.
4. **STOP.** Report both paths, counts per tier and the spend. The controller publishes the proposal for the user.

## Approval

Only on `approved: <proposal path> [edits…]`, compared against that file:

1. The proposal JSON next to it (same name, .json) missing → stop and say so; never rebuild it from memory.
2. data/competitors.json's SHA-256 (the Proposal step 1 command), or its absence, no longer what the proposal recorded → stop and report; the registry changed since. The hash, not the date: a same-day approval, or an intel run writing `last_analyzed`, leaves `_meta.last_discovery_run` as it was, and copying the proposal over the file would undo that change. A proposal that recorded no hash → stop and ask for a new proposal.
3. Apply the named edits to the proposal JSON. An edit that names no row, or a row not in it → stop and ask. An edit that moves a row to tier 5 also sets its `link_allowed: false` and replaces its `notes` with the tier-5 signals the edit or the proposal gives (the seller's own words quoted, contact details cut) — never the old tier's notes; no signal given → stop and ask for one. Re-derive every priority and `_meta.total`.
4. Run the scratch check (Proposal step 3). Problems → stop and report them; never fix rows without re-approval.
5. Diff the file against the proposal plus the edits (domains, tiers, keywords and positions, priorities). Any difference → stop and report it.
6. Only then copy the proposal JSON to data/competitors.json, run `python3 scripts/competitor_registry_check.py` in the repo (0 problems), run `python3 scripts/build_system_registry.py` (the first write adds a data/ entry; refresh it every time) and confirm `npm run -s registry` passes, add `Approved <YYYY-MM-DD>` and the edits applied (or `no edits`) under the proposal's title, set each candidate row this proposal covered to `added <YYYY-MM-DD>`, `in the seed results, not added <YYYY-MM-DD>: <reason>` (a seed returned it but step 6 did not choose it — the cap, a tier rule) or `not in the seed results <YYYY-MM-DD>` in `docs/research/competitor-registry-candidates.md`, and report the check output and the changed files, including `docs/reference/system-registry.md`.

## Handoff

`bsuk-competitor-intel --all` (or `--tier`) reads the registry next.

## Red flags — stop

- About to make a paid call without `spend approved: <seeds>; balance $<n>`, or to write data/competitors.json without `approved: <path>`.
- A `www.`, `shop.` or other subdomain in `root_domain`, or one domain twice.
- A platform (Blogspot, Facebook, a marketplace) banned or tier 5 for one seller on it.
- A saved response, note or proposal still holding a phone number, email, postcode or WhatsApp link.
- An existing row's `id`, `name`, `tier`, `cities`, `link_allowed`, `last_analyzed` or `notes` changed by an add or refresh, or an existing row dropped to make room.
- A candidate proposed or registered with no seed result that holds its root domain.
