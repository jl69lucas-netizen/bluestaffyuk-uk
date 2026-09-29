---
name: bsuk-visual-intelligence
description: Use when a BSUK page must be judged as a communication system rather than as markup — "does this page actually communicate", "what job is each section doing", "why does this page feel flat", "why does it feel the same as the other page", a visual scorecard, an image-usefulness review, or a page that passes every mechanical gate and still underperforms. Also use at the Harden sprint of docs/reference/page-run.md, before a cluster-wide design decision, when deciding whether a section needs a visual at all, and when a rendered page must be described in words for accessibility or AI citation.
---

# BSUK Visual Intelligence and Functional Semantics

## Golden Rule

Every other BSUK gate asks **does the page render correctly**. This one asks **what is the page
saying, to whom, how well, and what work is it doing** — for a reader, a crawler and an answer
engine. It never edits a page: it produces a scored report and routes every finding to the
agent or skill that owns the fix.

**Position in the run:** `docs/reference/page-run.md`, the Harden sprint — after the static
scan (row 16, `bsuk-page-hardening`, defects fixed) and before or alongside AEO (row 20,
`bsuk-aeo-pass`). Hardening makes the page *correct*; this makes it *effective*.

**REQUIRED BACKGROUND:** `.claude/skills/bsuk-gate-integrity/SKILL.md`. This skill emits
about twenty numbers, and a number is the easiest thing to invent.

---

## 0. The Iron Rules

**0a. Measure in a painting viewport, or write `NOT MEASURED`.** A DOM-only read reports
`width: 0` for everything and every visual probe false-passes. Use Playwright
(`browser_resize` → `browser_navigate` → `browser_evaluate`) or `npm run test:render:pages`,
at **375 / 768 / 1280**. Test 768 on purpose: tablet is where line length and grids break
while phone and desktop look clean. `NOT MEASURED` is a legal value in every table here; an
invented number is not.

**0b. A score is a hypothesis, not a fact.** Before you report any score below 6/10, quote the
element and confirm the weakness on the rendered page. A suspiciously low score means a broken
probe more often than a broken page.

**0c. Your own probes are gates too, and they lie.** Skip nodes where `!el.offsetParent` or the
rect is zero; check ancestors for `display:none` before calling a contrast failure; measure the
element the rule names, not its padded wrapper. Print each probe's examined count and refuse to
call a 0-element run a pass.

**0d. Every score carries its source:** `measured` (Playwright or a script), `derived`
(computed from measured values), or `NOT MEASURED`. "My judgement" is not a source. A score
with no source is invalid output, and an average of unsourced scores is noise.

**0e. Every finding names an owner** — a real BSUK agent or skill from the §7 table, never a
role ("the design-system owner"). A report with no routing column is not done.

**0f. Terminate deterministically.** Use the closed inventories (§4 functions, §5 predicates).
Anything genuinely new goes in `UNCLASSIFIED` with a proposed taxonomy addition; the taxonomy
grows by an edit to this file, not by improvisation.

---

## 1. Run the machine half first

Never hand-score what a script already counts.

```bash
npm run -s build
python3 scripts/page_hardening_scan.py <route>                 # static defect classes
python3 scripts/final_page_audit.py <route> --type <profile>   # page-type profile gates
python3 scripts/aeo_audit.py <route>                           # BLUF, entities, tables, dates
python3 scripts/evidence_audit.py <route> --type <profile>     # claims against the evidence ledger
python3 scripts/dup_content_audit.py --headers                 # sibling header crossover
npm run test:render:meta && npm run test:render:pages          # scorecards at 375/768/1280
```

`<profile>` is the page's row in `docs/reference/page-run.md` (location, comparison, blog) or
one of the other final-audit profiles (home, for-sale, puppy, interior). The render harness
writes `data/quality/scorecards/<slug>-<date>.json` with each check's examined count — read the
count before you trust the result.

A seam-parity check is NOT AVAILABLE — BSUK pages carry no seam dividers (`docs/reference/page-run.md`, "Deliberate differences"), so there is nothing to count.

Structural counts — headings, images, alts, schema, links, tables — come from a parser, never
from shell globs:

```python
import re, collections
body = open(f"dist/{route}/index.html", encoding="utf-8").read().split("<body", 1)[1]
heads = {f"h{n}": len(re.findall(rf"<h{n}[\s>]", body, re.I)) for n in range(1, 7)}
alts = re.findall(r'alt="([^"]*)"', body)
decorative = [a for a in alts if not a.strip()]      # legitimate markup, NOT a defect
named = [a for a in alts if a.strip()]
dupes = {k: v for k, v in collections.Counter(named).items() if v > 1}   # Rule 50b
```

**Decorative `alt=""` is correct markup**, not a missing alt and not a duplicate.

---

## 2. Visual Intelligence — scored against the locked tokens, never taste

The design system is decided. `rules/design.md`, `src/styles/tokens.css` and `IMAGE-DESIGNS.md`
are the rubric, so colour and type score **pass/fail against the tokens**, not as opinion.

### 2a. Visual Hierarchy — /10

| Dimension | How it is measured | Fail condition |
|---|---|---|
| Hero | element screenshot at 375/768/1280 | the primary claim and the CTA are not both visible without scrolling at 1280 |
| Dominant element | largest painted area above the fold | two elements compete; no single focus |
| Heading scale | computed `font-size` of each H2/H3 against the body `<p>` | a body heading renders no larger than the body text |
| Reading order | DOM order vs visual order | they disagree — a screen reader gets a different page |
| Section rhythm | painted section heights | a section over 2.5× the median height with no internal break |
| Grid and alignment | `getBoundingClientRect().left` clustering of a section's children | more than 3 distinct left edges in one section |
| Spacing | computed gaps vs the token scale | an off-scale value, or a `clamp()`/`calc()` the browser dropped |

### 2b. Typography — /10
`--font-display` (Fraunces) for every H1–H6 and `--font-body` (Source Sans 3) for body, labels
and buttons, applied globally — a page that hard-codes `font-family` is a defect. Check: the
heading clamp band does not invert at any width (resolve `var()` before judging), body
line-height 1.6–1.7, `<p>` capped near 70ch **measured as a real `ch`** (never approximated as
`0.5em`), and Title Case on every H1–H6 (`rules/headings.md`; a FAQ `<summary>` stays
conversational).

### 2c. Colour — /10
Pass/fail, not preference: every colour is a token (`--color-brand`, `--color-cta` with
`--color-cta-ink`, `--color-surface`, `--color-surface-inverse`, `--color-link`); no hex in
`src/` outside `src/styles/tokens.css`. The CTA emphasis is the `--color-cta` pill
(`--btn-radius`) owning the page's primary action. Run a full-page AA contrast sweep and skip
invisible nodes (§0c); every pair is in `data/design/contrast.json`. Never dim text with
`opacity`. **Never recommend a palette change** — the palette is locked (working rule 16).

### 2d. Image Intelligence — /10 per image
Score each image on **uniqueness** (is this file used on a sibling page?), **authenticity** (a
real photo of our puppies and home vs a stock or generated image), **usefulness** (does it carry
information the prose does not?), **trust contribution**, **conversion support** and **AI
understanding** (§3).

Hard BSUK gates, pass/fail:
- **The box** (`rules/images.md` `uniform-inbody-image-sizing`): on a project 5 page every in-body image renders through `src/components/BodyImage.astro` `box="uniform"` — `max-width: 760px; aspect-ratio: 1408 / 768; object-fit: cover` — or `box="tall"` for a portrait; focal point by `object-position`, never by changing the box. The twelve pages built before project 5 keep the natural `.bl-img` box until they are re-boarded.
- **Bleed:** any area around an in-body image is a design colour (bone), never grey or black; a portrait is baked contain, never blurfill.
- **Not upscaled:** a file painted wider than its natural width is a finding (the render harness's `img-not-upscaled` check); `sizes` must not under-declare the box — probe `wasteRatio` (§2e) and flag `> 1.5`.
- **Rule 50b** (`rules/images.md` `image-keyword-distribution`): the primary keyword in the primary image's alt only; every other alt rotates a different keyword type; no two non-empty alts on a page match. A served file keeps its served alt on first use (working rule 11).
- **An image under every body heading** of a project 5 page (`image-every-body-heading`), FAQ blocks excepted.

### 2e. Runtime probes

```js
// srcset/sizes waste, per <img>, at 375/768/1280
const r = img.getBoundingClientRect();
({ declared: img.sizes, renderedCss: Math.round(r.width), intrinsic: img.naturalWidth,
   wasteRatio: +(img.naturalWidth / (r.width * devicePixelRatio)).toFixed(2) })
```
Also probe horizontal overflow at 375, line length in real `ch` at 768, tap targets ≥ 24px, and
every contents-rail anchor actually scrolling.

---

## 3. Visual Verbalization — can a machine read your pictures?

An image an answer engine cannot put into words is decoration. For each **non-decorative** image,
one row:

| Field | Requirement |
|---|---|
| Visual description | one sentence a blind reader could act on |
| Primary entity | the one named thing the image is about (an id in `data/bsuk-ontology.json` where one exists) |
| Supporting entities | 2–4, from the ontology |
| Relationships shown | the §5 predicates the image asserts visually |
| Educational value /5 | does it teach something the prose does not? |
| Search value /5 | could it rank in Images for a real query in `data/queries/<slug>.json`? |
| AI citation value /5 | is the claim it makes checkable and attributable to us? |
| Accessibility value /5 | does the alt carry the information, or only the caption? |

**The verbalization is the alt-text spec.** A description better than the shipped alt is a
finding for `@bsuk-image-pipeline` and the `image-metadata` skill — and it respects Rule 50b, so
the fix is a *different* keyword type, never the primary again, and never a served alt replaced
on its first use.

**An infographic has a second duty:** every claim inside it also exists as selectable page
text. An answer engine cannot read a number that exists only as pixels.

---

## 4. Functional Intelligence — what work is this page doing?

Inventory the page's functions from the **closed taxonomy**: Inform · Teach · Compare ·
Recommend · Sell · Convert · Build Trust · Answer Questions · Handle Objections · Cross-link ·
Route Users · Qualify Buyers · Present Puppies · Explain Pricing · Present Reviews · Present
Paperwork · Reduce Uncertainty · Provide CTA · Generate Enquiries · Build Authority · Support
Snippets · Support AI Overviews · Support Voice Search · Support Internal Navigation · Support
Decision Making · `UNCLASSIFIED`.

For each: **present / partial / absent**, the evidence (section id and line), and its owner.

### 4a. Required-function matrix — what makes "missing" a defect

| Page type | Required functions (absence = FAIL) |
|---|---|
| **location** | Route Users (to `/available-puppies/` and the contact page) · Support Voice Search · the city, its region and its nearby cities from `data/locations.json` · the delivery band read from `data/settings.json`, with collection in Carlisle as the alternative · Answer Questions (the three FAQ blocks, `docs/reference/location-page-template.md`) |
| **comparison** | Compare · Recommend ("choose A if… choose B if…") · Support Decision Making · Route Users to both sides and to `/available-puppies/` · a comparison table that stacks below 640px (working rule 13) |
| **blog** | Teach · Cross-link to the money pages · six external links on six domains from four source types (working rule 17) · Build Authority |
| **for-sale / buy** | Present Puppies · Explain Pricing from `data/price-matrix.json` · the delivery band on every card (`rules/puppies.md`) · Qualify Buyers · Reduce Uncertainty (the paperwork in `data/faq.json` `whyus-paperwork`) · Provide CTA |
| **puppy** | a single `Product` + `Offer` · `InStock` only on an available puppy · real photos · Present Paperwork |
| **interior / care** | Teach · Answer Questions · Build Authority · Cross-link to the money pages |
| **every page** | Build Trust · Support Internal Navigation · Provide CTA · **no visible date anywhere** — freshness is schema-only (`rules/schema.md` `no-visible-date`) |

### 4b. Function metrics
- **Function Density** = functions present ÷ 1,000 words. Below about 1.5 the page is narrating, not working; above about 6 it is doing too many jobs.
- **Function Diversity** = distinct functions ÷ taxonomy size.
- **Function Coverage** = required set satisfied ÷ required set. **The headline number, and a gate:** coverage below 100% blocks a pass.
- **Functional Redundancy** = the same function served 3 or more times with no new information (the same three facts in the hero, the takeaways and the counter strip is the usual shape).

### 4c. Visual Differentiation — "it feels the same as the other page", made numeric
Sibling pages that read as one template are a defect (working rules 8 and 16). Measure pairwise
against **every** sibling in the cluster:
- section-type sequence similarity (component order);
- component-arrangement overlap (the board's hero, counter and section style picks — `data/boards/<slug>.json`);
- image reuse (the same file on both pages);
- `python3 scripts/dup_content_audit.py` body and `--headers` crossover;
- for a city page, the must-differ list (`data/design/city-must-differ.json`, `python3 scripts/city_must_differ.py --check`).

Target: zero non-whitelist prose or header crossover and at least three deliberate refresh
deltas per sibling pair. Route to `bsuk-component-refresh` and `bsuk-component-variations` —
layout, accent role or motif deltas only, **never a palette change**.

---

## 5. Predicate Intelligence — every claim is authorized or it is not asserted

Extract the predicates the page asserts, from the closed taxonomy:
`IS_A · HAS · CAN · REQUIRES · PROVIDES · SUPPORTS · REDUCES · LOCATED_IN · DELIVERED_TO ·
SOLD_BY · RAISED_BY · SCREENED_FOR · REGISTERED_WITH · LICENSED_BY · PRICED_AT · COMPARES_WITH ·
INCLUDES · PART_OF · RELATED_TO · CAUSES · PREVENTS · RECOMMENDS · EXPLAINS · QUALIFIES ·
MEASURES · UNCLASSIFIED`, and GUARANTEED_FOR (checked against `guarantee_days`, §5c).

**5a. Authorization.** A predicate whose entity is `ASSERTED` in `data/bsuk-ontology.json`, and
whose health or credential claim has a proof and a confirmation date in
`data/quality/evidence-ledger.json`, is `ASSERTED`. Anything else is `PROPOSED` — a finding,
not a fact. Today the ledger's `parents-dna-clear` claim is `NOT FETCHED`, so "the parents are
tested clear" on any page is PROPOSED however many times it is repeated.

**5b. Hard FAIL, not a score** — a page that carries any of these fails the gate:
- a licence, registration number or statute asserted as held, instead of LICENCE_CLAIM_PLACEHOLDER / LEGAL_CLAIM_PLACEHOLDER;
- a health result stated as fact without its ledger proof (`scripts/evidence_audit.py`, check `claim-bound-to-proof`);
- a guarantee cover the site has not stated (the length is `guarantee_days`, the wording `guarantee_label`; neither names a cover);
- any phrasing that implies a puppy sold unweaned, sourced from a dealer or brought in from abroad;
- a named house method (BSUK has none).

**5c. Three fact predicates checked on sight:**
- `PRICED_AT` — equals `data/price-matrix.json` (`male_gbp`, `female_gbp`) and the puppy's `price_gbp` in `data/puppies.json`;
- `GUARANTEED_FOR` — equals `guarantee_label` in `data/settings.json` (its length is `guarantee_days`), and names no cover;
- `DELIVERED_TO` — the band from `data/settings.json` `delivery_min_gbp`–`delivery_max_gbp`, by DEFRA-approved transport, priced by distance; collection in Carlisle is the alternative.

**Metrics:** Predicate Inventory · Frequency · Diversity (distinct ÷ taxonomy) · Density (per
1,000 words) · Complexity (share of multi-hop chains, e.g. puppy —RAISED_BY→ Lisa Bright
—LOCATED_IN→ Carlisle) · Authorization ratio (ASSERTED ÷ all).

---

## 6. Scorecard

| # | Score | Basis |
|---|---|---|
| 1 | Visual Hierarchy | §2a |
| 2 | Visual Consistency | §2b–2c token pass rate |
| 3 | Visual Trust | paperwork, review and breeder visibility above 50% scroll |
| 4 | Visual Information Gain | share of images carrying non-redundant information |
| 5 | Visual Communication | §3 educational and search value means |
| 6 | Visual Storytelling | section progression: question → evidence → decision |
| 7 | Visual Conversion | CTA visibility, the delivery band on every card, form friction |
| 8 | Visual Accessibility | AA contrast, tap targets, heading order, alt correctness |
| 9 | Visual Readability | line length in real `ch`, line-height, clamp band |
| 10 | Visual AI Readiness | schema present, infographic claims duplicated as text |
| 11 | Visual Verbalization | §3 row completeness |
| 12 | Visual Differentiation | §4c pairwise vs siblings |
| 13 | Function Density | §4b |
| 14 | Function Diversity | §4b |
| 15 | **Function Coverage** | §4a — **a gate, not a score** |
| 16 | Predicate Diversity | §5 |
| 17 | Predicate Density | §5 |
| 18 | **Predicate Authorization** | §5a–5b — **a gate: any 5b hit = FAIL** |

Every row carries its source (§0d). **Verdict:** `PASS` (Coverage 100%, Authorization clean,
no score below 6) · `PASS-WITH-WARNINGS` · `FAIL` (a gate breached). No overall average.

---

## 7. Output contract

Save to `docs/superpowers/sessions/<YYYY-MM-DD>-visual-intel-<slug>.md`, and publish it as an
Artifact with copy buttons and a `.md` download (the deliverables rule in `CLAUDE.md`):
executive summary (at most 150 words, verdict first) · scorecard with its source column · the
visual report · the verbalization table · the function inventory and required-set gaps · the
predicate inventory with authorization state · strengths · weaknesses · **prioritised
recommendations with owners**.

| Finding class | Route to |
|---|---|
| contrast, overflow, srcset, token drift, Title Case | `bsuk-page-hardening` |
| a check that stayed quiet on a real defect | `bsuk-gate-integrity` (a known-broken fixture in `tests/render/fixtures/known_broken/`, then fix the check) |
| sibling sameness, template feel | `bsuk-component-refresh`, `bsuk-component-variations` |
| alt text, image box, compression, upscaled files | `@bsuk-image-pipeline`, the `image-metadata` skill, `IMAGE-DESIGNS.md` |
| a missing or weak infographic | `@bsuk-infographic-builder`, the `bsuk-infographic` skill |
| CTA placement, form friction | the `bsuk-cta-strategy` skill, `bsuk-contact-form` |
| trust placement, reviews | `@bsuk-trust-signals-agent` |
| missing entity or predicate coverage | `@bsuk-entity-incorporation-agent`, the `bsuk-entity-graph` skill |
| an unauthorized claim (§5b) | `@bsuk-entity-incorporation-agent` and the answer board for the breeder |
| snippet or citation shape | `bsuk-aeo-pass` |
| duplicate prose or headers | `bsuk-duplicate-content-gate` |

A proposed visual change is previewed and approved before it is applied (working rule 6). With
the breeder away it is written as a preview, recorded `deferred` and logged under Open Flags.

---

## Common mistakes

| Mistake | Reality |
|---|---|
| "The scores are my judgement" | A score needs a source: measured, derived or `NOT MEASURED`. |
| Skipping the machine half and measuring by hand | §1 first; hand-scoring what a script counts is how two reports on one page disagree. |
| Listing each section's job in free text | Use the §4 taxonomy and the §4a matrix — only a closed list makes "missing" a defect. |
| Calling a repeated claim "redundant" and moving on | Check it against the ledger first: repeated and unledgered is a §5b FAIL, not a style note. |
| Owners named as roles | Name the agent or skill in §7. |
| Averaging the scores into one number | Report the verdict and the gates; an average hides a breached gate. |
| Scoring layout from HTML source | The layout does not exist until it paints. Playwright, or `NOT MEASURED`. |
| Counting `alt=""` as a defect | Decorative alt is correct markup. |
| Recommending a visual for every section | Honest, not everywhere: a visual earns its place by carrying information. |
| Suggesting a visible "Updated …" line | Banned site-wide; freshness is schema-only. |
| Changing the palette to fix differentiation | Layout, accent-role and motif deltas only. |

## Red flags — stop, the probe is wrong

- a count of `0` for something you can see on the page;
- a defect count far higher than the page's element count;
- every sibling page scoring identically;
- a contrast failure on text you cannot find on screen;
- one Lighthouse run used to judge CLS — five runs (`python3 scripts/perf_audit.py <route>`) or no claim.

## Baseline this skill was written against (2026-09-29)

A fresh agent without this skill audited `/blue-staffy-health-uk/` against
`/uk-staffordshire-bull-terrier-guide/`. It rendered both pages at the three widths, kept the
palette and added no visible date — and it still: wrote "the scores are my judgement, not a
gate's output" and averaged them into one number; ran none of the repo's page audits; listed
section jobs in free text with no required set, so nothing could be "missing"; reported the
parents' clear DNA result three times as *redundancy* without checking the ledger, where it is
`NOT FETCHED`; wrote no verbalization table; named owners as roles; and gave no verdict. Each
line of "Common mistakes" above closes one of those.
