---
name: bsuk-comparison-page-builder
description: The comparison-page builder for BlueStaffyUK — a section list derived from the competitors (their count + 3, floor 9, via bsuk-query-augmentation), a per-page research protocol (SERP snapshot → keyword universe → entity map → visual asset blueprint), per-page hero and counter styles (working rule 16), interactive decision modules, and the full pass-gate list (SEO/AIO/GEO/AEO/entity/anti-AI/non-commodity/Lighthouse). Covers the comparison pages project 5 builds; a coat-colour pairing (blue against black, blue against blue and white) is built to this blueprint by the bsuk-coat-variant-builder agent, which owns the coat-pair content.
---

# SKILL: BSUK Comparison Page Builder (re-based for BlueStaffyUK, 2026-09-16)

**Source of truth inputs:**
- The source repo's comparison system and its worked research file set were **not ported —
  source repo only**. This file is the whole system; replicate its research deliverables per page.
- Binding alongside: `rules/copy.md`, `rules/design.md`, `rules/images.md`, `rules/puppies.md`, `.claude/skills/anti-ai-writing/SKILL.md`. There is no theme pack: the design system is project 3

This skill **supersedes the section template inside `.claude/agents/bsuk-comparison-builder.md`** — the agent now executes THIS blueprint. Same design system, same reference page idioms, deeper structure.

**Session open (the user's rulings, 2026-09-26):** grill-me → superpowers:writing-plans → this builder skill. Invoke each with the Skill tool by name; the full order is `docs/reference/page-run.md` row 1.

**Research board before the outline (STOP 1, every page — the user's ruling, 2026-09-27):** after the research (page-run rows 4–7) the page goes through its research board, `docs/reference/page-run.md` row 8: built by `python3 scripts/research_board.py <slug>` from `data/research-boards/<slug>.json`: the competitor scan (top 5 on Google and Bing, why each ranks and its weakness, section counts, word target or `NOT FETCHED`), the query fan-out (PAA, Reddit, LLM intel), the keyword universe by intent with the four extra keyword types, the entities, 3 angle options (`bsuk-angle-agent`), 2–3 strategy directions and the framework options per section group, one option per choice marked (Recommended). The user picks on it, the picks are saved under `docs/reference/answer-board/answers/`, and the outline and the board are written from them and cite them. Nothing is outlined before the picks are recorded. The research protocol in section 3 below is what the board shows; its options are the board's choices. **The outline is then its own approval, STOP 2** (page-run row 9, the user's ruling of 2026-09-29: "yes, separate approval"): the section matrix, `data/outlines/<slug>.json` built by `python3 scripts/outline_matrix.py <slug>` — the approval status, the word target and its source, the heading census (one H1, no skipped level) and one row per section with its H2–H6 tree, framework, words, keywords, Cat A/B/C, a Why grounded in the research board and its image — approved with `python3 scripts/outline_matrix.py <slug> --approve --answers <file>`. No component is selected and no page board is built before it: `python3 scripts/build_page_board.py <slug>` exits 2 (`outline-unapproved`). The page board is STOP 3 and the Asset Gate STOP 4.

---

## 1. Page Inventory & Build Order

No comparison page exists yet. Project 5's research names the first in
`docs/superpowers/sessions/2026-09-23-location-pages-strategy.md` — the blue-or-black Staffy comparison (`blue or black staffordshire bull terrier`), a coat pairing, so `@bsuk-coat-variant-builder` builds it to this blueprint and owns its coat-pair content (the shared coat table, the cross-link block, the coat reader profiles).
This skill stays the page blueprint for every comparison. The project-5 plan fixes each page's
slug. Each is a NEW page: its slug is chosen once, on its board, and never changed
after it ships.

- The breed guide `/uk-staffordshire-bull-terrier-guide/` and the blog hub are not comparison pages — link to them, never merge them in.

## 2. BSUK Wording (apply to ALL comparison copy)

| Topic | BSUK wording |
|---|---|
| The breeder | Lisa Bright, BlueStaffyUK, Carlisle, Cumbria |
| The comparison | Blue Staffy (*Canis lupus familiaris*) against the rival the page's keyword names — never a breed the page's research did not name |
| reservation | reservation / bringing your puppy home |
| Decision-guide voice | **Virtual Litter Consultant** (the BlueStaffyUK decision-guide voice — still first-person we/us/our) |
| Health documentation | **Health-Documentation ROI** — L-2-HGA and HC-HSF4 screening, vet health check, microchip, whelp certificate, LICENCE_CLAIM_PLACEHOLDER LEGAL_CLAIM_PLACEHOLDER paperwork |
| DNA testing | L-2-HGA and HC-HSF4 DNA screening of the parents, where the evidence ledger records the certificate · vet health check · microchip |
| Breed conditions | Staffordshire Bull Terrier: the hereditary conditions the breed is DNA-tested for (L-2-HGA, HC-HSF4); any other health claim needs an evidence-ledger entry |
| Coat and shedding | short single coat, moderate shedding — no allergy or "hypoallergenic" claim |
| Cheap-puppy debunk | **Unweaned-pup sales debunk** — a pup sold before it is weaned is a welfare failure; BlueStaffyUK places fully weaned pups only |
| Grooming | coat, nail and ear care, bathing, crate hygiene |
| Kennel Club recognition | The Staffordshire Bull Terrier is a KC-recognised breed; any licence or statute wording stays LICENCE_CLAIM_PLACEHOLDER / LEGAL_CLAIM_PLACEHOLDER until confirmed |
| Prices | READ `data/price-matrix.json` and `data/settings.json` — NEVER hardcode a figure |

**Every claim stays inside the verified-claim ledger** (`data/quality/evidence-ledger.json`). A parent health-test claim (L-2-HGA, HC-HSF4) is assertable only where the ledger records the certificate.

## 3. Per-Page Research Protocol (Sprint 0.5 — MANDATORY before any outline)

**First, run `/bsuk-query-augmentation <slug> comparison "<primary keyword>" <route>`.** Its
file (`data/queries/<slug>.json`) supplies the page's FAQ picks and three extra sections. Every
pick appears on the page, each an H3 (one `Faq` block is fine here — the three-block split is
a location-page rule), and every `must_answer` question is answered with `covered_by` recorded —
`npm run check:queries` fails the page otherwise. The research below builds on that file; it
does not replace it.

Write the same six research deliverables for each page, saved under `docs/superpowers/` beside the page's plan: a keyword universe, an entity map, an internal-linking plan, a visual-asset blueprint, an implementation roadmap and a search-quality checklist.

**12-part deliverable per page** (breeder-approved format, one page per session, clustered):

1. **SERP Snapshot** — top 7 real Google UK results (the question file's Google and Bing pool, fetched `curl` first, a browser next and Firecrawl last because it spends credits; un-fetchable = `NOT FETCHED`, NEVER simulated). Why each ranks: authority, backlinks, topical depth, schema, UX.
2. **Search Intent** — informational / commercial / transactional / comparison / local.
3. **Competitor Reverse Engineering** (top 7) — title, meta, H1–H6, page voice, angle, frameworks, entity coverage + exploitable gaps, word count, media usage, schema usage.
4. **Keyword Universe** — primary, secondary, long-tail, long-form queries, compact keywords, PAA, Reddit-language queries, NLP/LSI terms, AI-Overview entities, branded/hybrid targets ("BlueStaffyUK vs …").
5. **Why Competitors Rank** — grounded per-competitor reasons.
6. **How BlueStaffyUK Wins** — our moat: real breeder data, health documentation, decision systems, first-person authority.
7. **Content Gap** — what's missing from ALL competitors.
8. **Recommended Page Structure** — full H1→H6, optimized for SEO + AEO + AI Overview + snippets.
9. **Schema / Technical** — FAQPage, Article/WebPage, BreadcrumbList; Product/Offer ONLY on the for-sale page; ItemList on hub.
10. **Internal Linking** — up to hub, sideways to sibling comparisons, down to `/blue-staffy-pup-sale-uk/`, `/buy-staffy-puppies-for-sale-uk/`, `/available-puppies/`, contextual to care/health/price pages. Anchors at sentence START (Link-First rule), never mid-sentence or end.
11. **Backlink Strategy** — canine blogs, breeders, rescue/education orgs, Reddit resources, pet journalists.
12. **Page Sections & Outline** — mandatory sections + competitor-derived sections + our-moat sections, **A/B/C categorized** (A=mandatory core, B=competitor-match, C=moat). The count is `section_target.total` in `data/queries/<slug>.json`: the competitors' highest cleaned H2 count + 3, never fewer than 9 (`docs/reference/location-page-template.md`, "Section count").

Research sweep sources per page: a fresh top-7 from Google, Bing, Reddit and Facebook, plus the registry (`data/competitors.json`) and its intel reports (`docs/research/competitors/`). A registry entry with no report is `NOT FETCHED`, never inferred.

## 4. Candidate Sections (the count comes from the competitors)

The page carries at least `section_target.total` body sections. The table below is a menu of
candidate sections, not a template: take the ones the competitor scan and the question file
support, drop the rest, and never pad to a number. Pillar structure (adapt per page):

| # | Level | Section | Notes |
|---|-------|---------|-------|
| 1 | H1 | Hero — "[A] vs [B]: Which Puppy Truly Fits Your Lifestyle, Home & Family?" | Split hero: left staffy, right rival; image FIRST on mobile (before H1) |
| 2 | — | Counter strip | this page's own figures, chosen on its board (rule 16) |
| 3 | — | TOC (desktop sidebar / mobile sticky jump-rail) | |
| 4 | H2 | Quick Answer / Decision Summary Block | a short AI-extractable definition (about fifty words) + "Choose [A] if… Choose [B] if…" |
| 5 | H2 | Key Takeaways | `InfoCard kind="fact"` |
| 6 | H2 | Quick Comparison Table | 8–12 attributes immediately after intro H2 |
| 7 | H2 | Why an Objective Comparison (not a popularity contest) | E-E-A-T; define both breeds |
| 8 | H3 | The BlueStaffyUK Philosophy: Health-Documentation ROI | L-2-HGA and HC-HSF4 DNA screening of the parents (only where the evidence ledger records the certificate), vet health check, the paperwork that goes home (`data/faq.json` `whyus-paperwork`); a licence only as LICENCE_CLAIM_PLACEHOLDER |
| 9 | H2 | Deep Dive: [A] — temperament, temperament, size, bonding | comparison table after H2 |
| 10 | H3 | Temperament & Home/Apartment Suitability | |
| 11 | H3 | Health Risk Analysis (breed-appropriate, ledger-bounded) | external authority links here |
| 12 | H3 | Coat, Shedding & Daily Care | short single coat, moderate shedding — no allergy or "hypoallergenic" claim |
| 13 | H2 | Deep Dive: [B] — same structure | |
| 14 | H2 | Decision Scorecard Matrix (0–10 traits) | temperament, temperament, noise, beginner fit, apartment fit, bonding speed |
| 15 | H2 | Lifestyle Matching Flowchart | first puppy? apartment? full-time worker? noise-sensitive? |
| 16 | H2 | Cost of Ownership Comparison (UK) | from price-matrix + financial-entities; H4 first-year breakdown |
| 17 | H2 | First 30-Day Adjustment Timeline | Lisa's first-30-days voice |
| 18 | H2 | Myth vs Reality Cards | H5 supporting facts, H6 breeder notes/citations |
| 19 | H2 | Health & Delivery section | canonical line: delivery £200–£350 by distance, by DEFRA-approved transport (read `delivery_options`) |
| 20 | H2 | Available Puppies cards | `PuppyCard` rows of `data/puppies.json`; link-out, don't re-teach; sold ≠ InStock |
| 21 | H2 | Owner Story (BAB) + Reviews | REAL reviews only — never fabricate |
| 22 | H2 | Who Should Choose [A]? / Who Should Choose [B]? | H4 micro-intent answers per household type |
| 23 | H2 | FAQ — every pick in `data/queries/<slug>.json` (one `Faq` block is fine; the three-block split is location-only), each question an H3, QAB answers | FAQPage JSON-LD carrying exactly the visible questions, visible accordion |
| 24 | H2 | Blog / further-reading cards | 3 relevant posts |
| 25 | H2 | Final CTA + page-specific inquiry form + newsletter | brass pill; one `ContactFormKit` — the page's only form and its closer (§11 item 6) |

**Hard structural gates (non-negotiable):**
- Full **H1→H6 outline presented and approved BEFORE any code** — no skipped levels, all six levels, **≥5 H5 AND ≥5 H6**.
- **An image under every body heading** (`rules/images.md`, user ruling G1): the hero and every body H2 and body H3 (FAQ blocks excepted) carry an image slot — an OG photo, a generated image or an IG-style infographic, per `IMAGE-DESIGNS.md` §7–§9 (§11 item 2).
- Word count: `NOT FETCHED` until the scan gives a competitor median — never pick a number first and write to fill it.
- Headers conversational/Quora-style, hybrid question+entity, **unique per page** (dup H2s across spokes = dup content).
- `SectionDivider` between major parts (`inverse` on a dark band), 4–8 per page.
- No visible dates anywhere — freshness in schema only.

## 5. Interactive Decision Modules (converted "calculators")

Text/HTML-CSS modules (pure HTML/CSS/vanilla JS via `@bsuk-interactive-component`; NO ASCII boxes on the live page):
- **Lifestyle Selector** — "Which Puppy Fits Me?" (flat → the calmer pup; active household → the busier pup; first-time owner → depends)
- **Size & Weight Comparator** — adult weights are NOT FETCHED until the breeder confirms them; the module renders the breed standard's range and says where it came from
- **Price Range Estimator** — BlueStaffyUK's own £1,500–£1,700 litter span from `data/price-matrix.json`; any market average is NOT FETCHED
- **Noise-Level Meter** — a qualitative comparison only; no decibel figure has been measured (NOT FETCHED)
- **Temperament Score** — the breed's family-dog reputation; an honest per-puppy variance note
- **First-year Budget Estimator** — crate, food, vet, insurance, training; every line item NOT FETCHED until the breeder supplies real numbers
- **Trust Documentation Panel** — the vet check, the microchip record, the vaccination card and the health-test certificates the ledger records

Snippet Box (📌 Quick Answer) opens every section — 1–2 sentence AI-extractable summary. Use line-icon SVGs, never emoji.

## 6. E-E-A-T & Voice Rules (converted)

- **Author box** near top: Lisa Bright, BlueStaffyUK – Carlisle, linking to `/blue-staffy-uk-breeders/`.
- **Original breeder data signals** — real, non-obvious observations from our own kennel, in Lisa Bright's voice; NEVER invented statistics. If we don't have the number, we don't print a number.
- **External authority links** in health sections — the RSPCA, the PDSA, Blue Cross, the RVC, thekennelclub.org.uk (curl 403 = bot-block, retry with UA, not dead). 6–8 diverse outbound links per page, anchored at sentence start (Link-First).
- First-person plural brand voice throughout; encyclopedic exceptions for taxonomy/research.
- Anti-AI writing filter + Style-2 gated humor (≤1 beat/section, never on health/legal).
- Negative keyword counter-positioning: puppy farms, scams, cheap unweaned pups.

## 7. Keyword Fan-Out Categories (converted)

A. **Temperament** — affectionate, one-person bonding, calm vs demanding, apartment puppy, separation anxiety, trainability
B. **Noise, Barking & Shedding** — barking, noise level, a quiet dog, shedding, allergies
C. **Size & Coat** — blue, blue brindle and white coats, full-grown size, coat and markings
D. **Price, Lifespan & Health** — price comparison, the 12–14 year breed lifespan, vet costs, L-2-HGA, HC-HSF4
E. **Lifestyle Match** — best for seniors / families / apartments / first-time owners / busy professionals
F. **Commercial bridge** — for sale UK, breeder, home-raised, health-tested (link down to the money pages)
G. **AI/LLM layer** — "compare X and Y in detail", "help me choose", "pros and cons" phrasing blocks

## 8. Components — the kit, arranged per page (visual companion gate)

Every section is a kit component (`src/components/kit/`) with no `variant` prop. Working rule 16
applies: each comparison page's board offers three hero and three counter styles designed for
that page, and every other section carries a small per-page refresh delta
(`.claude/skills/bsuk-component-refresh/SKILL.md`). The page reads its picks with
`pickedStyle(record, '<section id>')` (`src/lib/pickedStyle.ts`). Picks are shown in the browser
(`CLAUDE.md` rule 10), and the per-section **distribution matrix is approved BEFORE code**, always
with a Recommended pick + why + trade-off.

## 9. Imagery (Gemini / Nano Banana — no Higgsfield credit)

After outline approval, give the hero and every body H2 and body H3 its image slot — an OG photo, a generated image or an IG-style infographic (IG-3 Comparison Split is made for these pages), by `rules/images.md` "An image under every body heading" and `IMAGE-DESIGNS.md` §7–§9 (§11 item 2). AI prompts follow `rules/images.md` (crop ratios; negative list: no logos, no watermarks, no other breed) and the `rules/design.md` palette. A generated image goes through `.claude/skills/bsuk-image-generation/SKILL.md`, which needs `GEMINI_API_KEY` in `.env` (named in `docs/reference/credentials.md`, never committed); until the user sets it, a slot takes an existing image or an infographic (Known Issue 70). Image SEO 5-element on every image.

In-body image bleed uses design colours (bone), never grey or black; new portraits are baked `--og-style A` (`reframe_og.py … --style contain`), never blurfill — user ruling 2026-09-26, rules/images.md.

## 10. Pass Gates (page is NOT done until ALL pass)

The gates are rows 12 to 21 of `docs/reference/page-run.md`, in that order; that file is the
authority. In short: `npm run -s build` → `npm run -s check:all` → `python3 scripts/board_gate.py <slug>`
(and the slug in `data/facts/rebuilt.json`, the page in `tests/render/targets.json`) →
`npm run test:render:meta` → `npm run test:render:pages` (row 13, BEFORE Harden) → the two
Harden passes (rows 14–15) → `python3 scripts/page_hardening_scan.py <route> --fail-on-error`
(row 16) → commit, `npm run -s build` again (the prebuild re-dates the page from that commit), then
`npm run gate:page -- <slug> --skip-record` (row 17: dup, final audit on profile `comparison`,
hardening, AEO, evidence and the board gate, each run twice) → the verification record, committed,
then `npm run gate:page -- <slug>` (row 18) → `python3 scripts/measurement_ledger.py <project> --slugs <slug>` (row 19).

**Mandatory on every project 5 page (the user's rulings, 2026-09-26).** After the render gates
(row 13), invoke the `impeccable:impeccable` skill, then the
`frontend-design:frontend-design` skill, with the Skill tool (never paraphrased, never skipped),
on the built page at 375 / 768 / 1280 in a painting browser; commit each pass's fixes and record
it (`python3 scripts/page_run_record.py <slug> impeccable --findings <n> --fixed <n>`, then
`frontend-design`). A pass that proposes a visual change is previewed before it is applied
(working rule 6), and the palette never changes. Before any "page done" or "ready for approval"
claim, invoke the `superpowers:verification-before-completion` skill and record it with
`python3 scripts/page_run_record.py <slug> verification` (page-run.md row 18 steps).

Alongside those, the breeder's gate list is judged on the built page in `dist/`: **SEO · AIO · GEO · AEO · entity coverage · topical authority · anti-AI · non-commodity · humor policy · keyword variation · keyword-verifier · technical SEO · Lighthouse (warm median-of-3)**. Preview before apply. Commit after every approved build — never push (no remote until project 6) — on the branch the plan names, never the trunk. Sitemaps regenerate after any page change.

## 11. Breeder-Review Component Standard (BINDING for every comparison page)

These are the floor for every comparison page. Reference implementation: `src/pages/uk-staffordshire-bull-terrier-guide/index.astro`.

1. **Hero** — the kit `Hero`, in the arrangement the page's board picked through `pickedStyle()`
   (`layout`, `ledge`, `media`, `align`): a comparison page is the `interior-guide` layout, so its
   board offers that type's three styles in `HERO_STYLES_BY_PAGE_TYPE` (`src/lib/boardStyles.ts`);
   pick one no sibling page already ships (rule 16).
   Its height is `rules/design.md` rule 10's — 390–450px on desktop (≥1024px), auto below — with
   the image first in the DOM; the component holds both. The eyebrow's words are the page's own
   (§13 item 4); its colour and the H1's size (`--text-3xl` at 1024px and up, inside the rule-10
   band, and at 900px and below; `--text-4xl` only between 901 and 1023px) are the kit's — never brass text, which is 2.1:1 on the light surface. Hero
   images: `imageSrcset`, `imageWidth` and `imageHeight` for a `/images/…` path (`BaseLayout` has
   no preload prop).
2. **An image under every body heading** (`rules/images.md`, user ruling G1, 2026-09-24). The hero
   and every body H2 and body H3 (FAQ blocks excepted) carry an image slot, filled with an OG photo,
   a generated image (a named OG style, approved on the board by its exact bytes) or an IG-style
   infographic (IG-3 Comparison Split for the head-to-head), as `IMAGE-DESIGNS.md` §7–§9 set out;
   on conflict IMAGE-DESIGNS wins. The real `<table>` stays in the DOM for AIO — an image never
   replaces it.
3. **Photo-first cards everywhere.** A puppy card is that pup's real photo (800×800 crop) +
   a colour badge + the price from `data/price-matrix.json` + the delivery line. Delivery
   renders as two cards — **UK home delivery £200–£350 by distance,
   by DEFRA-approved transport**, and **collection in Carlisle** — each with its own photo, plus
   a row of links to 3–5 city pages from `data/locations.json` with FRESH anchors (each comparison page uses a different set).
4. **Sticky offsets are the kit's, never hard-coded.** The site header (`SiteHeaderKit`) is
   `sticky` at `min-height: var(--hdr)` (the rule is in `src/components/kit/SiteHeaderKit.astro`;
   `--hdr` is set in `src/styles/global.css`), and BaseLayout's inline script
   writes the header's measured height to `--hdr-measured`. Every jump target lands through the
   global `[id] { scroll-margin-top }` rule built on those two, which `SectionStrip` extends by its
   own `--strip-h`; never set `scroll-behavior: smooth` (§13 item 1). The page navigation and its
   column are the `PageShell` set — see §13 item 2.
5. **Contrast floors** — buttons and solid chips fill `--color-cta` with a `--color-cta-ink`
   label (6.8:1); table verdict cells `--color-brand` bold (10.4:1 on the surface); never brass
   on brass, and never brass as text on a light surface (2.1:1). Inside the article column give
   the CTA its own link rule (`color: var(--color-cta-ink); text-decoration: none`) or the
   generic link rule silently overrides it.
6. **Form = `ContactFormKit`** — never a hand-rolled form; its fields are the contract
   `form-inquiry-contract` asserts (`scripts/form_contract_audit.py`). It is the page's single
   closer: no second CTA band after it.
7. **Testimonials = real reviews only** — rows of `data/reviews.json` through `Testimonial`, with the
   name and place as recorded; never a written review.
8. **Blog cards** use each post's own `-card.webp` hub thumbnail, never a shared generic image.
9. **Links at the START of sentences only (Link-First rule) — never mid-sentence, never the final words.**
10. **Schema** — no page-level BreadcrumbList (the Breadcrumb component emits it; duplicates FAIL the
    gate). Title = 4-part ending in `BlueStaffyUK – <LSI keyword>` (never "BlueStaffyUK – Carlisle" again).
11. **Gate** — `python3 scripts/final_page_audit.py --comparison` (profile added 2026-07-04) must
    return PASS/PASS-WITH-WARNINGS; the old `no_userselect_none` site-wide FAIL was a Tailwind
    `.select-none` false positive, fixed in the auditor.

## 12. Polish rules every comparison page keeps

Every comparison page clears these on its finishing pass, in addition to §11:

1. **The counter strip is this page's own (working rule 16).** Its figures are facts from
   `data/*.json` and the page's record — the six pups and their two prices in `data/puppies.json`,
   the deposit and the delivery band in `data/settings.json` — chosen on the page's board, and never
   a set another page shows. No years-in-business figure and no licence figure: neither is on file.
2. **Responsive section images (Lighthouse "improve image delivery").** Every in-body section
   image, OG photo and infographic alike, renders in the one uniform box and ships as a WebP under
   100 KB with a `-760.webp` sibling and `srcset`/`sizes`, by the pipeline in `rules/images.md`
   ("Uniform in-body image sizing"). An image never replaces a table: the real table stays in the DOM.
3. **Every table is `DataTable`, and it stacks on phones (working rule 13).** Below 640px each row
   becomes a card and each cell prints its column name from `data-label` (`.stack-table` in
   `src/styles/global.css`); the component writes the labels and the stacking cannot be switched
   off. Its three board styles are the `chrome` layout axis (`ruled` / `zebra` / `brass`), never a prop.
4. **Internal links follow the "Links" list in `docs/reference/location-page-template.md`**,
   anchored at sentence start (Link-First), each from the section it serves. There is no delivery
   page and no pricing page: the delivery and price facts are stated on the page itself.
5. **Reversed head-term coverage.** Weave the reversed head term (`<rival> vs blue Staffy` as well
   as `blue Staffy vs <rival>`) once, naturally, in the Quick-Answer close, and carry the
   **"What is the difference between…"** and **"How can you tell … apart"** phrasings as FAQ H3s
   where the question file's pool has them. Dedupe against existing copy first — ignore keywords
   already on the page.
6. **Do NOT add Partytown for GA.** Diagnose Lighthouse's `unused JavaScript` (`/70de/`), `forced
   reflow` and `missing source maps` flags with `.claude/skills/bsuk-perf-gate/SKILL.md`: `/70de/` is
   the Google tag gateway, not a file in `src/`. There is no host to configure until project 6;
   note the flag in the page's fix log.

## 13. Kit rules every comparison page keeps

These hold on every comparison page, alongside §11 and §12.

1. **NEVER `scroll-behavior:smooth` on `html`.** `src/styles/global.css` sets
   `html { scroll-behavior: auto }`; never override it. On a long page Chrome cancels a smooth
   fragment scroll at frame zero (lazy-image layout shifts), so every jump link looks dead: the hash
   updates and the page never moves, while `scrollIntoView`/`scrollTo` still work, which misdirects
   debugging. The landing offset is the global `[id] { scroll-margin-top }` rule; nothing re-states
   it. Diagnostic: set `document.documentElement.style.scrollBehavior='auto'` and re-tap — if it
   jumps, that was the bug.
2. **The in-page nav is the kit's, never a hand-rolled rail.** `PageShell` mounts it from the
   page's `sections` (six or more): `SectionStrip` pinned under the header and `SectionSheet`
   behind the bottom bar below 1024px, `PageDial` at 1024px and above, and `PageNav`'s chip row
   once, below the hero (not sticky) — below 1024px only: when the dial mounts, `PageShell`
   hides the chip row, since the dial is the same list. Never add `position` to a sticky kit element: a sticky
   element is already a containing block for absolute children, and `position:relative` silently
   kills sticky.
3. **The counter is `CounterStrip`, never a hand-built stat block.** The page hands it its own
   `stats` (§12 item 1); the board picks how they are drawn (`tiles`, `label`) from the three
   styles `COUNTER_STYLES_BY_PAGE_TYPE` (`src/lib/boardStyles.ts`) gives a comparison page, which
   is the `interior-guide` layout. No icon chips, no uppercase or letter-spaced labels. Band
   padding goes on the section, never on a `container` (the `container` utility in
   `src/styles/global.css` sets no block padding — only `max-width`, `margin-inline` and
   `padding-inline`); colours and type are the tokens in
   `src/styles/tokens.css`, never a hex value.
4. **The hero eyebrow is UNIQUE per page, drawn from the page's own premise.** Never reuse one
   trust string across comparison pages; trust tokens belong in the `Hero` `chips`. Duplicate
   eyebrows across comparison pages FAIL the pass.
5. **Section dividers are `SectionDivider`** (`inverse` on a dark band) — the kit's own mark, never
   a logo file cropped into a circle.
6. **One newsletter, as on the location pages:** `InfoCard kind="recommendation" label="Newsletter"`
   with `id="newsletter"`; there is no newsletter component with variants. Its heading stays below
   the page H1 at every width (item 7).
7. **H1 must outrank every H2 at EVERY width.** Sweep rule: measure the H1's computed size at
   375/640/768/860/1280 and compare it against the largest H2 (usually the CTA or newsletter
   heading) before delivery. No render check measures this, so the sweep is the gate.
8. **Image budget <100KB per delivered file.** Recompress with Pillow WebP `method=6`, walking
   quality down until the file is under 95 KB (the `rules/images.md` pipeline), and check that any
   certificate text stays crisp. Masters for comparison imagery live under `src/assets/` when
   created (project 5); puppy masters are `src/assets/puppies/`.

## Keyword variants — the four extra keyword types (system-gaps, 2026-09-24)

A new location, comparison or blog board carries four keyword types beyond the nine the
brief names: `variation`, `related`, `cooccurring` and `similar`, each a list in a section's
`keywords`. The page needs at least one term of each type SOMEWHERE — not in every section.
The `keyword-variants-missing` check in `scripts/family_rules.py` warns on a draft and fails
from `boarded` on. The twelve pages built before this rule are never asked.

Where the terms come from: after the query augmentation has cached its files and before the
outline is boarded, run `python3 scripts/keyword_variants.py <board slug or query-cache folder>`
(the board slug resolves to its cache folder, e.g. `uk-locations/blue-staffy-puppies-manchester`
→ `blue-staffy-puppies-manchester-uk`). It reads the cached files under `data/queries/` only (no paid call) and proposes each list with the source of
every term: variations are spellings of the head term the cached text actually uses, related
terms are the search engine's related-searches box, co-occurring terms are phrases found in
two or more cached documents, and similar terms are how the ranking pages word the same
query. Put each term in the section where it reads naturally; drop a term that reads badly
anywhere rather than force it. Exit 6 means nothing is cached for the slug yet: run
bsuk-query-augmentation first. The board's block 4 shows every term as a chip grouped by
type, with the sections that use it.

## Build from the approved outline (system-gaps)

The user's ruling of 2026-09-24: build from the outline, never from crossovers, siblings or
duplicates. `rules/copy.md` `write-from-outline-never-from-sibling` is the method and
`outline-provenance-gate` is the gate that checks what the method leaves behind. Both bind
every comparison page this skill builds.

1. Write each body section from the approved board record, `data/boards/<slug>.json`, and
   from nothing else. The section's H2 is its `heading`; its H3s are its `tree` nodes, in
   record order, word for word (the build may title-case them). The copy answers the
   section's `intent` inside its `words` band.
2. Never open a sibling comparison's page, board or built HTML for wording. The only text a
   sibling may share is the whitelist in `scripts/dup_content_audit.py`; a heading that
   differs from a sibling's only by the breed word is a template copy, and the gate fails it.
3. A heading the tree does not carry, including an info card's H3, goes back to the board:
   add it to the tree and re-approve, then build. Never add one at build time.
4. The H4-H6 ladder is written at build time. Each ladder heading is new to this page and to
   the site.
5. After `npm run build`, run `python3 scripts/outline_provenance_check.py <slug>` on this
   comparison page and fix every FAIL in the copy, never by widening the whitelist. Only then add the
   comparison page to `data/facts/rebuilt.json`; from that point `npm run check:all` re-runs the gate on
   it with every other listed new-family page. The check ids it prints (`outline-extra`,
   `outline-missing`, `outline-order`, `outline-unknown-section`, `outline-duplicate-heading`,
   `outline-heading-crossover`, `outline-copy-crossover`, `outline-sentence-crossover`,
   `outline-unapproved`, `outline-not-found`) are listed in the script's docstring.

## Project 5 page rules (system-gaps)

These bind every location, comparison and blog-post page built from 2026-09-24 on. The
board refuses the record until each holds (`scripts/family_rules.py`); none of them applies
to the twelve pages built before.

1. **Keywords.** Run `python3 scripts/keyword_variants.py <board slug or query-cache folder>`
   (add `--also <cache dir>` when a registry folder holds the page's SERP) and write its
   proposals into the sections' `keywords.variation`, `related`, `cooccurring` and `similar`,
   keeping only terms the section really uses. An empty type fails `keyword-variants-missing` from `boarded` on.
2. **Entities.** Run `python3 scripts/ontology_seed.py --check`. Every entity a section names
   is in `data/bsuk-ontology.json` with a source; a health result stays PROPOSED until the
   evidence ledger holds it. The board shows them by class.
3. **External links.** At least six on six domains from four source types (gov, registry,
   vet-charity, welfare, research, local — `other` does not count toward the four), all rows
   of `docs/reference/external-link-library.md` (`external-links-six-diverse`). A location page
   adds its own council's dog or animal-licensing page as a `local` row, after
   `curl -sIL <url>` returns 200, dated in the Verified column.
4. **Anchors.** Every internal and external link carries `anchor_type` (exact, partial, lsi,
   natural, branded, naked-url): three or more internal types with at most two exact, three
   or more external types (`anchor-type-variation`), and never an in-copy internal anchor
   another board already uses for the same route (nav tiles excepted)
   (`anchor-reuse-sitewide`).
5. **Images.** Run `python3 scripts/image_candidates.py <slug> --write`. The hero and every
   body H2 and body H3 (FAQ blocks excepted) carry an image slot (`image-slot-missing`),
   filled in this order: the page's own migrated image, another served image, a file from
   the breeder's `Assets/Images/` folder (outside git; `BSUK_ASSETS_DIR` overrides) ingested
   with `python3 scripts/ingest_image.py folder`. When none fits,
   the slot is `source: generate` with an OG style, or `source: infographic` with an IG style,
   named in `IMAGE-DESIGNS.md`. The generated file is drafted with
   `python3 scripts/ingest_image.py draft`, approved on a second pass of the board by its
   sha12 pick, and only then published with `python3 scripts/ingest_image.py publish`
   (`image-generated-unapproved`). Every image slot has its `assets[]` row (slot, kind, w,
   h, required) planned at boarding; ingest and publish only fill its `file` and `status`.
   A slot without one fails `image-asset-row-missing`.
6. **Board and approval.** The board's block 7b lists every rule above for this page,
   evaluated as approval will see it; `scripts/board_approve.py` refuses the approval, and
   any re-approval, while one of them FAILs. The build-gate image checks are listed but never
   block approval: they can only pass after the image is approved and published.
7. **Routes.** A page whose route is not its bare slug (a city page under `/uk-locations/`,
   a post under the blog hub) has its row in `data/page-map.json` before it is built; without
   it `check:outline` looks for `dist/<slug>/` and reports `outline-not-found`.
8. **After the build,** `npm run -s check:outline` (also in `check:all`) must report the page
   examined with 0 problems.
