---
name: research-recency
description: Use when a CAG research task needs recent (last-30-days) or engagement-ranked signal, or when a source blocks the normal fetchers — Reddit/X thread mining, competitor or SERP freshness checks, "what are people saying now" questions, or Firecrawl/curl returning 403/429/bot-walls.
---

# Research Recency & Blocked-Source Fallback

## Overview
CAG research (competitor intel, PAA/SERP, reddit-strategy, keyword gaps) often needs **recent, real, engagement-ranked** signal that stale search results and blocked fetchers miss. This skill routes that need through a fixed escalation ladder and the `last30days` tool, so agents stop reporting "not fetchable" and never fabricate thread content.

## When to use
- A source blocks us: Reddit, X/Twitter, Facebook, or a competitor page returns 403/429 or a bot-check wall to Firecrawl/curl.
- The question is recency-shaped: "what are owners saying now", trending Timneh/Congo queries, a competitor's just-changed page, fresh scam patterns.
- Reddit thread mining for the comparison/for-sale clusters (r/parrots ranks pos-1 on our decision queries).

**Not for:** evergreen facts already in our data files, or anything the Verified-Claim Ledger governs (never source health/credential claims from social).

## Quick reference — fetch escalation ladder
1. **Firecrawl MCP** (`firecrawl_search`/`firecrawl_scrape`) — default.
2. **WebFetch/WebSearch** — retry a 403/429 once with a real browser UA (curl 403 ≠ dead).
3. **Headless browser** — Playwright MCP (`browser_navigate`+`browser_snapshot`) or chrome-devtools MCP. Reddit/FB render here even when they block curl.
4. **`/last30days [topic]`** — aggregates Reddit/X/YouTube/TikTok/HN/GitHub/web by real engagement, last-30-days scoped. Best for Reddit thread mining + "what's trending" + freshly-changed pages.

Full doc: `docs/reference/research-blocked-sites.md`. Reddit ethics + cornerstoning: `skills/reddit-strategy.md`.

## Installing `/last30days` (one-time, interactive session)
It is a third-party Claude Code plugin, not installed by default. In an **interactive** `claude` session run:
```
/plugin marketplace add mvanhorn/last30days-skill
```
(Source: https://github.com/mvanhorn/last30days-skill.) Non-interactive/agent sessions cannot run `/plugin`; if a task needs it and it isn't installed, say so — do not silently skip and do not fabricate results.

## Common mistakes
- Reporting "NOT FETCHED" after only step 1. Climb the whole ladder first.
- Inventing quotes/metrics when a source stays blocked. Un-fetchable = mark `NOT FETCHED`, never invented.
- Sourcing a health/credential/pricing claim from social. Those come from data files + the Verified-Claim Ledger only.
