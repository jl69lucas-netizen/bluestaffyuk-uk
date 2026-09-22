---
name: bsuk-final-page-pass
description: "Use as THE final QA gate at the end of EVERY BlueStaffyUK page build/rebuild/polish, before you \"give the page a pass\" or deploy — any page type, including puppy /available-puppies/ and for-sale pages the interior gate excludes. Runs the mechanical page-type-aware auditor over dist/, routes low scorers to the strategic + subjective checks, and returns one PASS / PASS-WITH-WARNINGS / FAIL verdict with a prioritized, WHY-grounded fix list. Triggers: \"final check\", \"give this page a pass\", \"is this page done\", \"audit before deploy\", \"run the final manual checks\"."
allowed-tools: [Read, Write, Bash]
---

# BlueStaffyUK Final Page Pass — the give-it-a-pass gate

## Overview
The single entrypoint you run at the end of every page build. Page-type-aware, two-tier,
ends in ONE verdict. Supersedes the interior-only `manual-auditor-check` by covering EVERY
page type via profiles; reuses `.claude/skills/bsuk-comprehensive-page-audit-system/SKILL.md` (strategic) and the
subjective checklist as components — it does not re-implement them.

## When to Use / Not
USE — a page (or batch) is "done" and you're about to pass/deploy it; ANY type incl. puppy
`/available-puppies/`, for-sale, location, comparison, blog. NOT — pre-build planning
(`bsuk-content-audit-agent`) or deep "why isn't this ranking" strategy
(`.claude/skills/bsuk-comprehensive-page-audit-system/SKILL.md`, which this gate calls for low scorers).

## Two-tier flow
1. Mechanical: `npx astro build` then `python3 scripts/final_page_audit.py [--puppies]`.
   Per-page PASS/WARN/FAIL + pre-triaged roll-up. Edit `PUPPIES`/`SLUGS` or add a profile to
   retarget.
   **1b. Dup-content gate (hard FAIL — breeder decision 2026-07-07):** run
   `python3 scripts/dup_content_audit.py <slug> <sibling-slug(s)>` against every page the
   build cloned structure from (same page family at minimum — e.g. any comparison page vs
   the other comparison pages). Any shared word-for-word run ≥12 words = FAIL the pass;
   rewrite the passage on the NEW page, rebuild, re-run until clean. Acceptable leftovers
   only: TOC/counter nav labels, credential badges, real verified review quotes, inquiry-form
   field labels. Also verify the page's 7-location pill set and variant-page anchor texts are
   unique per the distribution registry (memory: project-dup-content-and-location-distribution).
2. Strategic (low/failing only): route to the 5 owned scorers in
   `.claude/skills/bsuk-comprehensive-page-audit-system/SKILL.md` (AEO/entity/visual/backlink/verdict) + specialists; assemble, don't duplicate.
3. Subjective (sample 1 transactional + 1 pillar + 1 trust, or lowest puppy scorer + 1):
   the copy-paste block below.

## Page-type profiles

### Puppy / `/available-puppies/` profile

All puppy checks run against `scripts/final_page_audit.py --puppies`. The script builds its
`PUPPIES` list **from `data/puppies.json`** — today Roman, Byrd, Ince, Vennie, Christa and
Cheryl at `/available-puppies/<slug>/`. A new pup is added to the data file, never to the
script.

#### Puppy-page HARD GATES (FAIL — ship-blockers)

| Check ID | What fails | Rationale |
|---|---|---|
| `no_aggregateoffer` | `AggregateOffer` present anywhere in schema | Puppy page must be a **single `Product`+`Offer`**; `AggregateOffer` is the variant page (`bsuk-puppy-listing-page`). |
| health-test claim | A parent health-test claim (L-2-HGA, HC-HSF4) asserted without a certificate in `data/quality/evidence-ledger.json` | **Not a mechanical gate** — read it by eye. An unrecorded health claim is NOT FETCHED and must not appear. |
| `shipping_line` | The `£200–£350` delivery band missing from the visible body | Delivery-on-every-card is non-negotiable (`rules/puppies.md` `delivery-band-on-every-card`). Canonical line: `UK home delivery £200–£350 by distance · or collect in Carlisle`. |
| `sold_not_instock` | Sold/reserved STATUS signal present AND schema still shows `InStock` | Sell-and-retire lifecycle: sold → 301, never `InStock`. Note: commerce phrases like "sold together" do NOT trigger; only explicit status signals ("now sold", "has been sold", "status: sold", "is reserved", etc.). |
| `canonical_abs` | Relative canonical (not `https://…`) | Site-wide hard gate — applies to all page types. |
| `no_svg_in_content` | `<svg>` inside CSS `content:` | Site-wide trap; see false-positive traps below. |
| `no_escaped_svg` | Escaped `&lt;svg` in rendered HTML | Site-wide trap. |
| `no_emoji` | a colourful emoji in rendered output | Site-wide non-negotiable — line-icon SVGs only; a generic dog emoji is not a Blue Staffy. |
| `no_phone_in_body` | Breeder phone number in page body (above footer) | The phone is `PHONE_PLACEHOLDER` until project 6 and lives in the footer only; third-party consumer-protection hotlines are exempt. |
| `no_visible_date` | Visible "Updated / Last updated / Last modified <Month> <Year>" text | CLAUDE.md: freshness lives only in schema `dateModified`, never as visible text. |

#### Puppy-page SCALED / SCOPED (WARN — shippable, log fix)

| Check ID | Value / Behavior |
|---|---|
| `wordcount_in_band` | **700–1,000 words** (script checks 600–1,200 with buffer for chrome); not the pillar "+1,000" floor |
| `newsletter_present` | **NA** — puppy pages are exempt from newsletter requirement (footer newsletter only, per 2026-06-18 decision) |
| `all_h1_h4` | WARN — H1×1 + H2/H3 required; H4 where structure exists on a lean puppy page; H5/H6 only on genuine depth |
| `house_method` | **WARN** — flag until breeder confirms a term; Verified-Claim Ledger forbids inventing a house-method name |
| `lifespan_12_14` | WARN — at least one "12–14 year" breed-lifespan reference (not hard-FAIL on a lean puppy page) |
| `real_hero_image` | WARN — hero must not be a placeholder/logo; flags if first content image src contains "placeholder", "coming-soon", or "default" |

### Interior profile

The `rich` pages in `data/page-map.json`. Key differences from puppy: `no_aggregateoffer`,
`shipping_line`, `wordcount_in_band` and `real_hero_image` are all `NA` (not applicable).
`house_method` = WARN. The source repo's separate interior audit script was not ported —
source repo only; `scripts/final_page_audit.py` with no flag IS the interior profile.

### Other page types — compact one-row summary

| Page type | Key hard gates | Key scaled / scoped | Notes |
|---|---|---|---|
| **Interior** (`rich` pages) | single_canonical, no_phone_in_body, no_visible_date, jsonld_valid, faqpage_present | house_method WARN | `python3 scripts/final_page_audit.py` with no flag |
| **For-sale / variant** (`/blue-staffy-pup-sale-uk/`, `/buy-staffy-puppies-for-sale-uk/`) | sold_not_instock; single_canonical; the £200–£350 delivery band | word count 1,000–2,000; `no_aggregateoffer` WARN — a hub may aggregate, a single pup may not | one `Product` per pup, one `Offer` each (`rules/puppies.md`) |
| **Location** (`/uk-locations/<slug>/`, 28 cities) | single_canonical; no_visible_date; BreadcrumbList; delivery band | word count 3,000–5,000; the city entity in H1; FAQPage present | every city comes from `data/locations.json` |
| **Comparison** (`/uk-staffordshire-bull-terrier-guide/` etc.) | single_canonical; comparison table present; no_visible_date | word count 1,500–3,000; H1 contains "vs" or "versus" | `bsuk-comparison-builder` handles schema |
| **Blog** | single_canonical; no_visible_date; Article schema; BreadcrumbList | word count 800–2,500; FAQPage recommended (WARN if absent) | Internal links to money pages required |
| **Hub** (`/buy-blue-staffy-puppies-uk/` etc.) | single_canonical; no_visible_date; spoke links present | word count 500–1,500; spoke count ≥ 3 internal links | Feeds `bsuk-structure-architect` silo map |
| **Homepage** (`/`) | single_canonical; no_visible_date; Organization schema; no_phone_in_body | word count 2,000–4,000; H1 on primary keyword; ≥3 FAQPage answers | Highest-traffic page — strict threshold |

**Fail-safe rule for unmapped page types:** if a page type is not in `PROFILES`, the script
falls back to `DEFAULT_SEVERITY = "FAIL"` for every boolean check — the strictest possible
subset. Type-specific checks that cannot be meaningfully evaluated (e.g. `no_aggregateoffer`
on a blog page) are treated as WARN to avoid fabricating ship-blockers. Never silently pass
an unmapped type.

## Verdict model
- **FAIL** — any REAL hard-gate check fails (per the active profile). Ship-blocking; fix before deploy.
- **PASS-WITH-WARNINGS** — no hard fails, but ≥1 soft item (Flesch 55–60, `house_method` WARN, alt marginally >190, a missing-but-recommended entity). Shippable; fixes logged for follow-up.
- **PASS** — clean.

Every `✗` is triaged **REAL** (fix now) / **ACCEPTED** (correct for page type) / **FALSE
POSITIVE** (auditor heuristic flaw) / **NET-NEW / BY-DESIGN**. The gate never reports a raw
machine fail as a defect without triage — the discipline that prevented 31 false positives on
the interior batch.

## The 5 false-positive traps (do NOT fabricate these as defects)

| Looks like a fail | Why it's usually fine |
|---|---|
| **`has_org` missing** | `Organization` is valid when nested as `Article.publisher`/`author`, and `@type` can be a **list** `["LocalBusiness","PetStore"]`. The auditor recurses and handles lists before flagging — verify in `dist/` before reporting. |
| **Non-hero image is `eager`** | Index 0 is the **header logo**; the eager image right after it is the correct **LCP hero**. The auditor detects the hero by excluding `logo` srcs, not by position 0. A false "non-hero eager" alert usually means the logo exclusion failed — check `src` attributes in `dist/`. |
| **Phone number in body** | Third-party **authority hotlines** (Citizens Advice, Action Fraud, a trading-standards line) are intentional. The rule bans only the **breeder's** number in body — and that number is `PHONE_PLACEHOLDER` until project 6. The auditor exempts any phone within 60 chars of "hotline", "fraud" or a named consumer body. |
| **The licence line not in the first 300 words** | Astro renders inline JSON-LD *inside* `<main>` — **scripts are stripped before measuring** visible word count. If the auditor still flags this, confirm via `grep` that the JSON-LD stripping ran correctly on `dist/`. |
| **`Offer` nested inside `Product` fails `no_aggregateoffer`** | A single `Offer` nested inside a `Product` block is **correct schema for a puppy listing page** — that is the single-Product+Offer pattern the spec requires. Only a **top-level `AggregateOffer`** (not nested inside `Product`) fails the puppy gate. Verify by inspecting the raw JSON-LD in `dist/available-puppies/<slug>/index.html` before reporting. |

## Copy-Paste FINAL MANUAL PAGE CHECK

> Paste this block anywhere (a fresh chat, a PR comment, a doc) to run the gate by hand.
> Tick every box; a page isn't "done" until the REAL items pass.

```text
FINAL MANUAL PAGE CHECK — <page slug>            Updated: <Month Year>
RUN FIRST: npx astro build  →  python3 scripts/final_page_audit.py [--puppies]

STRUCTURE
[ ] H1 ×1 exactly; H1–H4 all present; no level skips (utility pages may lack H4 — ACCEPTED)
[ ] Exactly ONE FAQPage in dist/; JSON-LD parses valid
[ ] BreadcrumbList present; Organization present (top-level OR nested as Article.publisher)
[ ] Exactly one canonical, and it is absolute (https://…)

META + IMAGES
[ ] Title ≤275 · description ≤300 (long-format standard); brand ("BlueStaffyUK" or "Blue Staffy") in title
[ ] Every image alt ≤190 chars AND unique per page
[ ] Non-hero images loading="lazy"; LCP hero stays eager (header logo is NOT the hero)
[ ] Every <img> has explicit width/height (CLS); delivered <100KB

COMPLIANCE COPY (content pages; contact/privacy exempt)
[ ] The breeder's legal standing (LICENCE_CLAIM_PLACEHOLDER) and the statute line (LEGAL_CLAIM_PLACEHOLDER) in the first 300 VISIBLE words (strip JSON-LD)
[ ] The 12–14 year breed lifespan referenced at least once

CONVERSION + FRESHNESS
[ ] Footer phone present; NO breeder phone in body (authority hotlines OK)
[ ] NO visible date anywhere (no "Updated <Month Year>" / "Last updated"); freshness lives ONLY in schema dateModified
[ ] Newsletter top/middle/bottom — long content pillars only (skip thin/utility pages)

A11Y / GOTCHA TRAPS
[ ] No <svg> inside CSS content:  · no escaped &lt;svg in dist  · no emoji  · no user-select:none
[ ] External links: new tab + rel="noopener noreferrer" + ↗; no bare "click here" anchors

SUBJECTIVE (read 3 sample pages: 1 transactional, 1 pillar, 1 trust)
[ ] First-person "we/our/here at BlueStaffyUK" voice >> third-person filler
[ ] ≤1 Honesty-Policy humor beat/section; none on legal/health
[ ] Flesch 60–70 (floor ~55 for entity-dense pages)
[ ] ≥1 high-resolution breeder detail / ~500 words; no "both make exceptional companions" filler
[ ] A named house method is used ONLY once the breeder confirms one — never invented (WARN until then)
[ ] LSI/NLP keyword coverage: "blue Staffy", "blue-brindle Staffy", "home-raised",
    "Staffordshire Bull Terrier puppy", "UK home delivery by DEFRA-approved transport",
    "collection in Carlisle" present where natural — not forced, not stuffed

TRIAGE every ✗ as: REAL (fix) · ACCEPTED (page-type) · FALSE POSITIVE (heuristic) · NET-NEW/BY-DESIGN

--- PUPPY-PAGE SUPPLEMENT (run for every /available-puppies/<slug>/ page) ---

RUN: python3 scripts/final_page_audit.py --puppies

HARD GATES (FAIL — fix before deploy)
[ ] Schema uses single Product + single Offer — NO AggregateOffer anywhere
[ ] A parent health-test claim appears ONLY if the certificate is in
    data/quality/evidence-ledger.json; otherwise NOT FETCHED
[ ] Delivery line visible in body: UK home delivery £200–£350 by distance, or collect in Carlisle
[ ] If the pup is sold/reserved in data/puppies.json: schema shows SoldOut or PreOrder, never InStock
[ ] Canonical is absolute (https://SITE_URL_PLACEHOLDER/available-puppies/<slug>/)

SCALED / SCOPED (WARN — shippable, log for follow-up)
[ ] Word count 700–1,000 words (check nwords in auditor output)
[ ] Real hero photo — not a placeholder, coming-soon image, or logo
[ ] H1 ×1 + H2/H3 present; H4 only where page depth warrants it
[ ] The 12–14 year breed lifespan mentioned at least once
[ ] House-method naming (WARN until breeder confirms a term)

EXEMPT on puppy pages
[ ] Newsletter — footer newsletter is sufficient; mid-page newsletter NOT required

FIRST-PERSON VOICE (puppy page)
[ ] Written as "here at BlueStaffyUK, [puppy name] is one of our…" — not third-person breed narration
```

## GAP-FLAGs the gate emits (never invents)

These are recommendations surfaced for the breeder — the gate never auto-resolves them:

- **House-method name** (WARN on all pages until confirmed) — upgrade check from WARN to enforced only after the breeder supplies a confirmed term for inclusion in the Verified-Claim Ledger.
- **Extra authority-link targets** — beyond the standard library (The Kennel Club, the RSPCA, a veterinary school, a government animal-welfare page), the gate may suggest further credible `.org/.ac.uk/.gov.uk` targets for link variety. Verify 200 before inserting; the external-link library is deferred to project 6.
- **Delivery and local-authority entities** — the gate flags *whether a given page type warrants* logistics entities (DEFRA-approved transport, the delivery band, collection in Carlisle) or local-authority signals. Puppy listing pages generally inherit these from the price/delivery cluster rather than carrying them inline; the flag is informational only.

## Common mistakes

- **Auditing source greps not `dist/`** — Astro `<Schema>` components hide JSON-LD from source; always build first. `grep` on `src/` will miss schema and produce false positives.
- **Reporting the roll-up un-triaged** — the roll-up flags ALL pages; utility pages (contact/privacy) are exempt from several checks by design. Triage every `✗` before quoting it as a defect.
- **Chasing Flesch 60–70 as a hard gate** — it fights entity density; treat ~55 as the floor. Do not gut semantic coverage to chase a readability score.
- **Running it on a pup that has no built page yet** — a pup declared in `data/puppies.json` whose page has not been built is out of scope. Report it as OUT-OF-SCOPE, not as FAIL.
- **Treating a nested `Offer` as an `AggregateOffer` fail** — see false-positive trap #5 above. Inspect the raw JSON-LD in `dist/` before flagging.

## Workflow placement
Sprint 4 FINAL step, immediately before the (project-6) deploy step. After `bsuk-accessibility-fixer` →
`bsuk-performance-fixer` → `bsuk-canonical-fixer` → `bsuk-footer-standardizer`. Companion to
`.claude/skills/manual-auditor-check/SKILL.md` and `.claude/skills/bsuk-website-health/SKILL.md`
(whole-site sweep).
Invoke via the Skill tool, or run the two commands by hand.
