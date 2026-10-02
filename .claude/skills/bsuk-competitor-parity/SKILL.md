---
name: bsuk-competitor-parity
description: Use when a BlueStaffyUK page must match or beat its competitors' keywords and entities — "how do we beat them", "match their keywords", "add more entities", "semantic keywords", "entity relationships", "competitor density" — or when reading board blocks 1b, 4c, 4d or 5c at page-run rows 6, 7 and 10. (BlueStaffyUK)
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## Overview

We beat a competitor page by covering what it covers, type by type, and then by showing
evidence it cannot show. **Nothing is added that a competitor domain does not carry, and
nothing is claimed that a data file does not hold.** The counting is done by four approved
scripts; this skill is the method for reading them and acting on what they print. It
writes no prose and invents no term: a gap with no data behind it stays a gap.

## When

Page-run rows 6, 7 and 10 (`docs/reference/page-run.md`):

| Row | What this skill does there |
|---|---|
| 6 — keyword deliverables | read block 4c (density) beside block 4b; pick the band on the decisions batch |
| 7 — entities | read block 5c (gaps, entities, relations) before `bsuk-entity-incorporation-agent` runs Move 2 |
| 10 — the page board | check 1b, 4c, 4d and 5c on the built board before STOP 3 |

Not for: ranking or traffic questions (NOT FETCHED until project 6), or writing the copy
itself (`bsuk-seo-content-writer`, from the approved outline).

## Run

```bash
python3 scripts/serp_reading.py <slug>    # block 1b — what page one of Google shows
python3 scripts/term_density.py <slug>    # block 4c — per-term counts vs competitor prose
python3 scripts/faq_layout.py <slug>      # block 4d — three FAQ blocks or one
python3 scripts/term_gap.py <slug>        # block 5c — what they say that we do not
```

Each reads `data/boards/<slug>.json` and the competitor cache under
`data/queries/cache/<slug>/`; the board builder calls the same functions.

| Block | What it tells you |
|---|---|
| 1b | the blocks on page one, who ranks with what kind of page, what the AI Overview cites, which of our sections answers each People Also Ask question, and the PAA no section answers |
| 4c | for every board term and board entity name: min / median / mean / max on the top five prose bodies (listings skipped), and two targets scaled to OUR word target |
| 4d | method A (intent spread, Recommended) and method B (page type) side by side: three FAQ blocks or one bottom block |
| 5c | **by type** (our terms of each keyword type that any competitor carries), **phrases** on 2+ domains that no board term covers, **entities** (ontology only) a competitor names and no section lists, **relations** (NOT FETCHED) |

## Reading the numbers

- **Median band `[p25, p75]` vs leader band `[p75, max]`.** Median means "as thorough as a
  typical page one result"; leader means "as thorough as the most thorough". The breeder
  picks ONE band per page on the decisions batch (answer board) — never mix them per term,
  and never pick for the breeder.
- **`0–0` / "no competitor uses it"** means there is no target for that term, not a target
  of zero. The term stays if the outline needs it; it is just not measured against anyone.
- **Thin pool.** Fewer than 3 competitor bodies prints a thin-pool warning: the band is
  read as a hint, not a target, and the board says so. A competitor with no cache file is
  skipped, never counted as zero.
- A longer term's matches also count toward a shorter term it contains ("blue staffy
  puppies" inside "blue staffy") — do not add the two together.

## Beat them, in this order

1. **Match each keyword type** where block 5c "by type" shows we have zero coverage and
   competitors have some. Fill it from the research board's keyword universe only.
2. **Close gaps carried by 2 or more domains** (block 5c phrases and entities) — but only
   when the term is TRUE for us and a data file backs it: `data/settings.json`,
   `data/puppies.json`, `data/faq.json`, `data/bsuk-ontology.json`,
   `data/quality/evidence-ledger.json`. No backing → write `NOT FETCHED — <barrier>` on the
   board and never write the claim. A phrase five marketplace pages share is still one domain.
3. **Beat them on evidence they lack**, every item from data: our parents
   (`data/puppies.json`), the paperwork we can show (`data/faq.json` `whyus-paperwork`), the
   video ids in `data/settings.json` `youtube_embeds`, collection in Carlisle, and the
   guarantee as `guarantee_label` (its length is `guarantee_days`; what it covers only as
   `guarantee_cover` words it, and `guarantee_days` gates every guarantee line).
   Licence and statute stay `LICENCE_CLAIM_PLACEHOLDER` / `LEGAL_CLAIM_PLACEHOLDER`.
4. **Never exceed the chosen band's upper bound.** Above it is stuffing, and it reads as
   stuffing to a buyer before it does to Google.

## Entities and relationships

- Only entities in `data/bsuk-ontology.json`. A name that is not there is not on the page.
- A new entity goes in through `python3 scripts/ontology_seed.py` from one of its sourced
  inputs, with its source, **before** any section names it; `--check` reports.
- Relationships come only from an ontology `relations` key. That key does not exist yet, so
  every relationship is `NOT FETCHED — the ontology has no relations key`. Do not write
  "X is part of Y" or "X causes Y" from general knowledge.

## What fails

| Fault | Why |
|---|---|
| a term with no competitor domain behind it | invented — not a gap, a guess |
| a count above the chosen band's upper bound | stuffing |
| another city on a city page (5c names them on one line and never proposes them) | cannibalises a sibling page |
| a name, figure or claim not in a data file | CLAUDE.md rule 9 — fabricated |
| mixing median and leader bands on one page | the breeder picked one |

## See also

- `bsuk-entity-agent` — the entity vocabulary and EBP
- `bsuk-entity-incorporation-agent` (`.claude/agents/`) — the 4-Move Loop per section
- `bsuk-keyword-verifier` (`.claude/agents/`) — placement on the built page
- `bsuk-query-augmentation` — the competitor scan and query pool these scripts read
