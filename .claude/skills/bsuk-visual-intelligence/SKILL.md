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

**0d. Every score carries its class:** `measured` (Playwright or a script), `derived`
(computed from measured values), `judgment` (a reader's call, labelled as one, never gating),
or `NOT MEASURED`. §6 gives every row its class and its formula; a score with no class is
invalid output, and an average of scores is noise.

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

**Read-only runs.** Inside a page run, the build and the harness are rows 12–13 and their
outputs are that run's deliverables. Outside one (an audit someone asked for without changes),
do not build and do not run the harness, which writes scorecards: reuse the page's scorecard
only if it is newer than `dist/<route>/index.html`, otherwise measure with Playwright directly
(§2e) and label the harness-only rows `NOT MEASURED — scorecard older than the build`. Save the
report to the session scratchpad instead of §7's path, and say so in its first line.

**What the scripts do not fail.** `check:all` does not run the final audit, the evidence audit
or the dup audit, and `scripts/evidence_audit.py` reports a claim whose proof is `NOT FETCHED`
as a WARN. Read the WARNs: §5b turns the unproven ones into a FAIL by hand.

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
line-height 1.6–1.7 and `<p>` set to a 65ch measure, a defect only above 75ch (the city
type-fit gate, `tests/render/lib/cityTypeFit.ts`) — both scored in row 9 only, with `ch`
measured as a real `ch` (never approximated as `0.5em`) — and Title Case on every H1–H6 (`rules/headings.md`; a FAQ `<summary>` stays
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
- **The box** (`rules/images.md` `uniform-inbody-image-sizing`): on a project 5 page (any page not in `BUILT_BEFORE_SYSTEM_GAPS` in `scripts/family_rules.py`) every in-body image renders through `src/components/BodyImage.astro` `box="uniform"` — `max-width: 760px; aspect-ratio: 1408 / 768; object-fit: cover` — or `box="tall"` for a portrait; focal point by `object-position`, never by changing the box. The twelve pages built before project 5 keep the natural `.bl-img` box until they are re-boarded.
- **Bleed:** any area around an in-body image is a design colour (bone), never grey or black; a portrait is baked contain, never blurfill.
- **Not upscaled:** a file painted wider than its natural width is a finding. The harness's `img-not-upscaled` check runs only on the city kit and the component canvas, not on a page scorecard, so on a page measure `naturalWidth` against the painted width yourself (§2e). `sizes` must not under-declare the box — probe `wasteRatio` and flag `> 1.5`.
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
every contents-rail anchor actually scrolling: `scroll-behavior: smooth` can cancel a `#anchor`
jump on a long page, so click each anchor and read `scrollY` before and after (the fix is
`auto`).

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
| Search value /5 | could it rank in Images for a real query in `data/queries/<slug>.json`? (No query file for the page: `NOT FETCHED — no query file`.) |
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
| **comparison** | Compare · Recommend ("choose A if… choose B if…") · Support Decision Making · Route Users to both sides and to `/available-puppies/` · a comparison table that stacks below 640px (working rule 13) · an interactive decision module (`.claude/skills/bsuk-comparison-page-builder/SKILL.md` §5, built by `@bsuk-interactive-component`) |
| **blog** | Teach · Cross-link to the money pages · six external links on six domains from four source types (working rule 17) · Build Authority |
| **for-sale / buy** | Present Puppies · Explain Pricing from `data/price-matrix.json` · the delivery band on every card (`rules/puppies.md`) · Qualify Buyers · Reduce Uncertainty (the paperwork in `data/faq.json` `whyus-paperwork`) · Provide CTA |
| **puppy** | a single `Product` + `Offer` · `InStock` only on an available puppy · real photos · Present Paperwork |
| **interior / care** | Teach · Answer Questions · Build Authority · Cross-link to the money pages (`/available-puppies/`, `/buy-blue-staffy-puppies-uk/`, `/buy-staffy-puppies-for-sale-uk/`, `/blue-staffy-pup-sale-uk/`) |
| **every page** | Build Trust · Support Internal Navigation · Provide CTA · **no visible date anywhere** — freshness is schema-only (`rules/schema.md` `no-visible-date`) |

### 4b. Function metrics
A `partial` function counts as present for Density and Diversity and as absent for Coverage.
Words are the visible words inside `<main>`, from the §1 parser.

- **Function Density** = functions present ÷ 1,000 words. Below about 1.5 the page is narrating, not working; above about 6 it is doing too many jobs.
- **Function Diversity** = distinct functions ÷ taxonomy size.
- **Function Coverage** = required set satisfied ÷ required set. **The headline number, and a gate:** coverage below 100% blocks a pass.
- **Functional Redundancy** = the same function served 3 or more times with no new information (the same three facts in the hero, the takeaways and the counter strip is the usual shape).

### 4c. Visual Differentiation — "it feels the same as the other page", made numeric
Sibling pages that read as one template are a defect (working rules 8 and 16). **The cluster:**
a city page's siblings are every other city in `data/locations.json` that is built; a comparison
page's are the other pages that follow the comparison slug pattern of
`docs/research/2026-09-26-url-family-decision.md` ("Comparison slugs"); any other page's are the
pages of its own `<profile>`. Measure pairwise against **every** sibling in the cluster:
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
BETTER_THAN · INCLUDES · PART_OF · RELATED_TO · CAUSES · PREVENTS · RECOMMENDS · TRAINS ·
LEARNS · EXPLAINS · QUALIFIES · MEASURES · UNCLASSIFIED`, and GUARANTEED_FOR (checked against `guarantee_days`, §5c).

**`BETTER_THAN` is always flagged.** A page that says one coat, sex, breeder or breed is better
than another states a ranking; it is `ASSERTED` only when a cited outside source in
`docs/reference/external-link-library.md` makes the same comparison, and never about another
breeder by name.

**5a. Authorization.** A predicate whose entity is `ASSERTED` in `data/bsuk-ontology.json`, and
whose health or credential claim has a proof and a confirmation date in
`data/quality/evidence-ledger.json`, is `ASSERTED`. Anything else is `PROPOSED` — a finding,
not a fact. Today the ledger's `parents-dna-clear` claim is `NOT FETCHED`, so "the parents are
tested clear" on any page is PROPOSED however many times it is repeated, and — being a result —
it is a §5b hit on every page that states it. An entity the ontology
does not have at all is UNKNOWN: a finding for `@bsuk-entity-incorporation-agent`, which adds it
through `python3 scripts/ontology_seed.py` or a sourced row, never an entity to score as ASSERTED.

**Ruled by the breeder, not yet in the ledger.** A claim counts as ruled only when a rulings
file under `docs/reference/answer-board/answers/` states that specific claim in its own
"What the pages do" column. A blanket answer ("it's all real", "check the health page") never counts, and
nor does the breeder's answer in the answer column alone. A ruled claim that the ledger or the
ontology does not hold yet is routed to a ledger or ontology update through
`@bsuk-entity-incorporation-agent`, listed under "Ledger updates" in the report, and counted
`PROPOSED` in the Authorization ratio until the update lands — and it is exempt from §5b only
when it is not a result. A test result or score always needs its ledger `proof` (rule 9): the
Q9 row of the rulings permits a page to NAME the tests and the screening, never to state a
result. So the ten "tested clear" lines on `/blue-staffy-health-uk/` (`parents-dna-clear`,
proof `NOT FETCHED`) are §5b hits, not ledger updates; whether the breeder holds the
certificates is a question for her on the answer board.

**5b. Hard FAIL, not a score** — a page that carries any of these fails the gate:
- a licence, registration number or statute asserted as held, instead of LICENCE_CLAIM_PLACEHOLDER / LEGAL_CLAIM_PLACEHOLDER;
- a health result or score ("clear", a grade, a pass), or a health outcome stated as a certainty ("will not develop"), without its ledger proof (`scripts/evidence_audit.py`, check `claim-bound-to-proof`). A test result or score always needs its ledger `proof`; no ruling, blanket or specific, stands in for it;
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

Every row has a **class** and a **rule**. A `measured` or `derived` row is scored by its formula
from counts you took (§1, §2e, the §3–§5 tables) and nothing else. A `judgment` row is scored by
a reader and says so; a `report` row is a count with no threshold. A `gate` row is pass/fail.
Each "n checks" formula scores 10 × checks passed ÷ checks examined; a check that does not
apply to the page (no puppy card, no infographic) is not examined, and a row whose checks were
all not examined is `NOT MEASURED`.

**Definitions the rows use** (from the second re-test, 2026-09-29):
- *Dominant element:* the largest painted area above the fold is at least 1.25× the next (a ratio above 0.8 is two elements competing).
- *Body text:* `<p>` and `<li>` inside `<main>`; a FAQ `<summary>`, a pull-quote and chrome are not body.
- *A CTA:* a `Button` (the `--color-cta` pill) or the contact form inside `<main>`; the sticky header's button is chrome and never counts.
- *One form:* one enquiry form (`ContactFormKit`); the header's site search is not a form for this count.
- *No hex:* scoped to the page's own source file and the kit components it mounts, not the whole repo.
- *Refresh deltas:* board picks that differ between the two pages on a component shape both carry; the target is 3, or every shared shape when the pair shares fewer than 3.
- *Taxonomy sizes:* every entry except `UNCLASSIFIED`; GUARANTEED_FOR (checked against `guarantee_days`) counts as a predicate.
- *A filled §3 field:* a value, or `NOT FETCHED — <barrier>` with its barrier written.

| # | Score | Class | Rule |
|---|---|---|---|
| 1 | Visual Hierarchy | measured | 10 × §2a dimensions passed ÷ 7 (hero, dominant element, heading scale, reading order, section rhythm, grid, spacing); the hero is judged at 1280 only (its §2a condition is a desktop fold), every other dimension at 375, 768 and 1280 and passes only at all three |
| 2 | Visual Consistency | measured | 10 × token checks passed ÷ 5 (display font on headings, body font, Title Case, no hex outside tokens, one CTA pill style); line length and line-height are row 9's, never counted here too |
| 3 | Visual Trust | measured | 10 × present ÷ 3 above 50% scroll at 1280 (the paperwork list, a review from `data/reviews.json`, the breeder named) |
| 4 | Visual Information Gain | judgment | share of non-decorative images whose §3 row teaches something the prose does not, × 10 |
| 5 | Visual Communication | judgment | 2 × the mean of the §3 educational and search values (each /5) |
| 6 | Visual Storytelling | judgment | does the section order run question → evidence → decision? |
| 7 | Visual Conversion | measured | 10 × checks passed ÷ checks examined (a CTA visible without scrolling at 1280; a CTA within every 700 words of `<main>`; the delivery band on every puppy card; one form on the page) |
| 8 | Visual Accessibility | measured | 10 × checks passed ÷ 4 (0 AA contrast failures on visible nodes; every tap target ≥ 24px; no skipped heading level; no missing and no duplicated non-empty alt) |
| 9 | Visual Readability | measured | 10 × checks passed ÷ 3 (no `<p>` wider than 75ch at 768, against the 65ch measure; body line-height 1.6–1.7; no clamp band inverted between widths) |
| 10 | Visual AI Readiness | derived | 10 × checks passed ÷ checks examined (`npm run check:schema` output filtered to the page's route shows nothing blocking; every infographic claim also present as page text; `python3 scripts/aeo_audit.py <route>` no BLUF WARN) |
| 11 | Visual Verbalization | derived | 10 × §3 rows with all eight fields filled ÷ non-decorative images |
| 12 | Visual Differentiation | measured | for each sibling pair, 10 × checks passed ÷ 4 (0 prose crossover; 0 header crossover; ≥ 3 refresh deltas; no served image file in the same role — the hero, or the same section — on both pages; reuse in a different role is allowed by working rules 11 and 17); the row scores the worst pair, and names it |
| 13 | Function Density | derived | 10 when functions present ÷ 1,000 words is 1.5–6; 5 when within half that band again (0.75–1.5 or 6–9); else 0 |
| 14 | Function Diversity | report | distinct functions ÷ taxonomy size, reported with no threshold |
| 15 | **Function Coverage** | gate | required set satisfied ÷ required set (§4a) = 100% |
| 16 | Predicate Diversity | report | distinct predicates ÷ taxonomy size, reported with no threshold |
| 17 | Predicate Density | report | predicates per 1,000 words, reported with no threshold |
| 18 | **Predicate Authorization** | gate | no §5b hit (a ruled claim awaiting its ledger update is not a hit unless it states a test result or score, which always needs its `proof`) |

**Verdict:** `PASS` — both gates pass and every `measured` and `derived` row scores 6 or more.
`PASS-WITH-WARNINGS` — both gates pass, and a `measured` or `derived` row scores below 6 or is
`NOT MEASURED`. `FAIL` — a gate is breached. `judgment` and `report` rows are reported beside
the verdict and never change the verdict, so a page can PASS on its measured and derived rows
alone. No overall average.

### Worked example

An illustration of the arithmetic, not a measurement of any page. A city page: hierarchy passes
6 of 7 dimensions (the hero at 1280, the rest at all three widths) → 8.6; consistency 5 of 5 → 10; trust 3 of 3 → 10;
conversion 3 of 3 examined (it has no puppy card, so that check is not examined) → 10;
accessibility 4 of 4 → 10; readability 2 of 3 → 6.7; AI readiness 2 of 2 examined (no
infographic) → 10; verbalization 7 of 8 rows complete → 8.8; differentiation: its worst pair (against the Leeds page, say) passes 4 of 4 → 10;
function density 3.1 per 1,000 words → 10. Coverage 9 of 9 required functions (the location row's five and the every-page row's four) → the gate passes;
no §5b hit → the gate passes. Every measured and derived row is 6 or more → **PASS**, with
the judgment rows (information gain 7, communication 6, storytelling "question → decision, no
evidence section") listed beside it. Had readability passed only 1 of 3 (3.3), the verdict
would be **PASS-WITH-WARNINGS**; had one required function been missing, **FAIL**.

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
| copy and voice (third person, copy that talks about the page itself, AI tells) | `@bsuk-seo-content-writer`, the `anti-ai-writing` skill |
| a missing internal cross-link (a money page, a sibling) | the `internal-link-agent` skill |

A proposed visual change is previewed and approved before it is applied (working rule 6). With
the breeder away it is written as a preview, recorded `deferred` and logged under Open Flags.

---

## Common mistakes

| Mistake | Reality |
|---|---|
| "The scores are my judgement" | Score by the §6 formula; a row that is a reader's call is labelled `judgment` and never gates. |
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

## Tests this skill was written against (2026-09-29)

A fresh agent without this skill audited `/blue-staffy-health-uk/` against
`/uk-staffordshire-bull-terrier-guide/`. It rendered both pages at the three widths, kept the
palette and added no visible date — and it still: wrote "the scores are my judgement, not a
gate's output" and averaged them into one number; ran none of the repo's page audits; listed
section jobs in free text with no required set, so nothing could be "missing"; reported the
parents' clear DNA result three times as *redundancy* without checking the ledger, where it is
`NOT FETCHED`; wrote no verbalization table; named owners as roles; and gave no verdict. Each
line of "Common mistakes" above closes one of those.

With the skill, a fresh agent on the same task ran the five page audits (and found three of them
failing or warning), labelled all 18 scores, applied both gates — Coverage 63% and an
Authorization FAIL on ten unproven "clear" claims — named every owner from §7 and gave a FAIL
verdict. Its ten gaps (read-only runs, the upscale check's scope, a missing query file, the
WARN-only evidence check, entities absent from the ontology, partial functions, the money pages,
a copy owner, the middle verdict, which pages the box binds) are closed above.

After the review of 2026-09-29 gave every row a class and a formula, a third fresh agent, read-only,
reached a verdict (FAIL: coverage 7 of 8 — two money pages unlinked) with every number traced to
a script, a probe or a §6 formula, and the judgment rows labelled and kept out of the verdict.
The ambiguities it reported (the dominant-element threshold, what counts as body, a CTA and a
form, the hex scope, refresh deltas against a sparse sibling, taxonomy sizes, a `NOT FETCHED`
field, the owner of a missing cross-link) are the definitions above §6's table.
