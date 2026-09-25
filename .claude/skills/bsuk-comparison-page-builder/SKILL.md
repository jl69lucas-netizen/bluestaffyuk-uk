---
name: bsuk-comparison-page-builder
description: The comparison-page builder for BlueStaffyUK — a section list derived from the competitors (their count + 3, floor 9, via bsuk-query-augmentation), a per-page research protocol (SERP snapshot → keyword universe → entity map → visual asset blueprint), per-page hero and counter styles (working rule 16), interactive decision modules, and the full pass-gate list (SEO/AIO/GEO/AEO/entity/anti-AI/non-commodity/Lighthouse). Covers the comparison pages project 5 builds, starting with the blue-or-black Staffy comparison.
---

# SKILL: BSUK Comparison Page Builder (re-based for BlueStaffyUK, 2026-09-16)

**Source of truth inputs:**
- The source repo's comparison system and its worked research file set were **not ported —
  source repo only**. This file is the whole system; replicate its research deliverables per page.
- Binding alongside: `rules/copy.md`, `rules/design.md`, `rules/images.md`, `rules/puppies.md`, `.claude/skills/anti-ai-writing/SKILL.md`. There is no theme pack: the design system is project 3

This skill **supersedes the section template inside `.claude/agents/bsuk-comparison-builder.md`** — the agent now executes THIS blueprint. Same design system, same reference page idioms, deeper structure.

---

## 1. Page Inventory & Build Order

No comparison page exists yet. Project 5's research names the first — **Blue or black Staffy
comparison** (`blue or black staffordshire bull terrier`) — in
`docs/superpowers/sessions/2026-09-23-location-pages-strategy.md`; the project-5 plan fixes its
slug and any others. Each is a NEW page: its slug is chosen once, on its board, and never changed
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
- **Every H2 and H3 carries an image** — an OG photo or an AI image, never an HTML/CSS infographic (§11 item 2).
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

After outline approval, mark every H2/H3 needing an OG photo vs an AI image (no HTML/CSS infographics — §11 item 2). AI prompts follow `rules/images.md` (crop ratios; negative list: no logos, no watermarks, no other breed) and the `rules/design.md` palette. The source repo's image-generation script was **not ported — source repo only**; no API key belongs in this repo. Image SEO 5-element on every image.

## 10. Pass Gates (page is NOT done until ALL pass)

`npx astro build` → verify in `dist/` → `python3 scripts/final_page_audit.py` → then the full breeder gate list: **SEO · AIO · GEO · AEO · entity coverage · topical authority · anti-AI · non-commodity · humor policy · keyword variation · keyword-verifier · technical SEO · Lighthouse (warm median-of-3)**. Preview before apply. Commit after every approved build — never push (no remote until project 6) — on the branch the plan names, never the trunk. Sitemaps regenerate after any page change.

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
2. **No HTML/CSS infographics.** Every H2 + important H3 image slot is a real OG photo or a Gemini
   image (distinct design style per section, the `rules/design.md` palette, 16:9 1600×900 → 760×400 slot).
   The source repo's prompt pack was not ported — source repo only; write the page's own.
   The real `<table>` stays in the DOM for AIO — an image never replaces it.
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
