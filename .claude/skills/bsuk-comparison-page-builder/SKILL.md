---
name: bsuk-comparison-page-builder
description: THE comparison-page builder skill for BlueStaffyUK — 22–25-section blueprint, per-page research protocol (SERP snapshot → keyword universe → entity map → visual asset blueprint), 3-variant component system (Hero A/B/C), interactive decision modules, and the full pass-gate list (SEO/AIO/GEO/AEO/entity/anti-AI/non-commodity/Lighthouse). Re-based for BlueStaffyUK 2026-09-16. Covers the comparison cluster (hub + spokes). Build order — blue-vs-blue-brindle first, male-vs-female second-to-last, hub LAST.
---

# SKILL: BSUK Comparison Page Builder (re-based for BlueStaffyUK, 2026-09-16)

**Source of truth inputs:**
- The source repo's comparison system and its worked research file set were **not ported —
  source repo only**. This file is the whole system; replicate its research deliverables per page.
- Binding alongside: `rules/copy.md`, `rules/design.md`, `rules/images.md`, `rules/puppies.md`, `.claude/skills/anti-ai-writing/SKILL.md`. There is no theme pack: the design system is project 3

This skill **supersedes the section template inside `.claude/agents/bsuk-comparison-builder.md`** — the agent now executes THIS blueprint. Same design system, same reference page idioms, deeper structure.

---

## 1. Page Inventory & Build Order (verified live 2026-07-04, all 200)

| # | Slug | Role | Build order |
|---|------|------|-------------|
| 1 | `/uk-staffordshire-bull-terrier-guide/` | Variant comparison (flagship) | **FIRST — the standard-setter** |
| 2 | `/uk-staffordshire-bull-terrier-guide/` | Species comparison | 2nd–4th batch |
| 3 | `/uk-staffordshire-bull-terrier-guide/` | Species comparison | 2nd–4th batch |
| 4 | `/uk-staffordshire-bull-terrier-guide/` | Species comparison (THIN — 135 lines) | 2nd–4th batch |
| 5 | `/uk-staffordshire-bull-terrier-guide/` | Self-comparison / decision page | 5th–6th |
| 6 | `/blue-staffy-uk-breeders/` | Breeder comparison (trust page) | 5th–6th |
| 7 | `/buy-staffy-puppies-for-sale-uk/` | Gender comparison (FOR-SALE method) | **SECOND-TO-LAST** |
| 8 | `/uk-staffordshire-bull-terrier-guide/` | HUB | **LAST — consumes spoke data** |

- `/blog/uk-staffordshire-bull-terrier-guide/` is a **blog post**, not part of this cluster — never merge it in.
- All 8 exist on disk in `src/pages/` — default mode is REBUILD to this standard, never build from scratch, never change slug/canonical/H1 topic without approval.

## 2. MFS → BSUK Conversion Map (apply to ALL converted content)

| MFS term | BSUK term |
|---|---|
| Maltipoo (baseline breed) | Blue Staffy (*Canis lupus familiaris*) |
| Maltese | Blue-Brindle Staffy (*Psittacus blue-brindle*) |
| Cavapoo | American Bully |
| Cockapoo | English Bull Terrier |
| Poodle | Amazon Puppy |
| puppy / puppies / dog / litter | pup / pups / puppy / puppy / litter |
| adoption | reservation / bringing your puppy home |
| Lawrence & Cathy | Lisa Bright (Glasgow, since 2014) |
| Virtual Adoption Consultant | **Virtual Litter Consultant** (the BlueStaffyUK decision-guide voice — still first-person we/us/our) |
| "Genetic ROI" | **Health-Documentation ROI** — L-2-HGA and HC-HSF4 screening, vet sex-checking, canine-vet exam, whelp certificate, LICENCE_CLAIM_PLACEHOLDER LEGAL_CLAIM_PLACEHOLDER paperwork |
| OFA / CHIC / Embark DNA | L-2-HGA PCR panel · HC-HSF4 PCR · vet sex-checking certificate · canine veterinarian wellness exam · closed leg band |
| Mitral Valve Disease / PRA / White Shaker | Species-appropriate risks ONLY: staffies = hypocalcemia, coat-destructive behavior, L-2-HGA susceptibility; american bullys = coat plucking, extreme noise, cloacal papilloma; english bull terriers = proventricular dilatation awareness, bite-force/space needs; amazons = hormonal seasonal aggression, obesity/fatty liver |
| shedding / hypoallergenic | powder-down dander (staffies & american bullys are powder-down puppies — allergy-relevant), coat dust management |
| Cheap-puppy trend debunk | **Unweaned-pup sales debunk** — a pup sold before it is weaned is a welfare failure; BlueStaffyUK places fully weaned pups only |
| grooming | coat, nail and ear care, bathing, crate hygiene |
| Kennel Club recognition | The Staffordshire Bull Terrier is a KC-recognised breed; any licence or statute wording stays LICENCE_CLAIM_PLACEHOLDER / LEGAL_CLAIM_PLACEHOLDER until confirmed |
| prices | READ `data/price-matrix.json` and `data/settings.json` — NEVER hardcode a figure |

**Every claim stays inside the verified-claim ledger** (`data/quality/evidence-ledger.json`). A parent health-test claim (L-2-HGA, HC-HSF4) is assertable only where the ledger records the certificate.

## 3. Per-Page Research Protocol (Sprint 0.5 — MANDATORY before any outline)

Write the same six research deliverables for each page, saved under `docs/superpowers/` beside the page's plan: a keyword universe, an entity map, an internal-linking plan, a visual-asset blueprint, an implementation roadmap and a search-quality checklist.

**12-part deliverable per page** (breeder-approved format, one page per session, clustered):

1. **SERP Snapshot** — top 7 real Google US results (Firecrawl/Playwright; un-fetchable = `NOT FETCHED`, NEVER simulated — the MFS source used simulated data; we do not). Why each ranks: authority, backlinks, topical depth, schema, UX.
2. **Search Intent** — informational / commercial / transactional / comparison / local.
3. **Competitor Reverse Engineering** (top 7) — title, meta, H1–H6, page voice, angle, frameworks, entity coverage + exploitable gaps, word count, media UKge, schema UKge.
4. **Keyword Universe** — primary, secondary, long-tail, long-form queries, compact keywords, PAA, Reddit-language queries, NLP/LSI terms, AI-Overview entities, branded/hybrid targets ("BlueStaffyUK vs …").
5. **Why Competitors Rank** — grounded per-competitor reasons.
6. **How BlueStaffyUK Wins** — our moat: real breeder data, health documentation, decision systems, first-person authority.
7. **Content Gap** — what's missing from ALL competitors.
8. **Recommended Page Structure** — full H1→H6, optimized for SEO + AEO + AI Overview + snippets.
9. **Schema / Technical** — FAQPage, Article/WebPage, BreadcrumbList; Product/Offer ONLY on the for-sale page; ItemList on hub.
10. **Internal Linking** — up to hub, sideways to sibling comparisons, down to `/blue-staffy-pup-sale-uk/`, `/buy-staffy-puppies-for-sale-uk/`, `/available/` puppies, contextual to care/health/price pages. Anchors at sentence START (Link-First rule), never mid-sentence or end.
11. **Backlink Strategy** — canine blogs, breeders, rescue/education orgs, Reddit resources, pet journalists.
12. **Page Sections & Outline** — mandatory sections + competitor-derived sections + our-moat sections, **A/B/C categorized** (A=mandatory core, B=competitor-match, C=moat), total **22–25 sections**.

Research sweep sources per page: a fresh top-7 from Google, Bing, Reddit and Facebook. No competitor registry was ported and none has been fetched for BSUK — an un-fetched competitor is `NOT FETCHED`, never inferred.

## 4. The 22–25 Section Blueprint (converted 22-section MFS template)

Pillar structure (adapt per page; hub compares staffy vs ALL species with 2–3 H3 comparison metrics per rival):

| # | Level | Section | Notes |
|---|-------|---------|-------|
| 1 | H1 | Hero — "[A] vs [B]: Which Puppy Truly Fits Your Lifestyle, Home & Family?" | Split hero: left staffy, right rival; image FIRST on mobile (before H1) |
| 2 | — | Counter Snippet strip | £1,500 from · £500 deposit · £200–£350 delivery · 24h reply |
| 3 | — | TOC (desktop sidebar / mobile sticky jump-rail) | |
| 4 | H2 | Quick Answer / Decision Summary Block | a short AI-extractable definition (about fifty words) + "Choose [A] if… Choose [B] if…" |
| 5 | H2 | Key Takeaways (8 takeaways) | `bsuk-key-takeaway` stat-forward grid |
| 6 | H2 | Quick Comparison Table | 8–12 attributes immediately after intro H2 |
| 7 | H2 | Why an Objective Comparison (not a popularity contest) | E-E-A-T; define both species |
| 8 | H3 | The BlueStaffyUK Philosophy: Health-Documentation ROI | PCR screening, vet sex-checking, LICENCE_CLAIM_PLACEHOLDER docs |
| 9 | H2 | Deep Dive: [A] — temperament, temperament, size, bonding | comparison table after H2 |
| 10 | H3 | Temperament & Home/Apartment Suitability | |
| 11 | H3 | Health Risk Analysis (species-appropriate, ledger-bounded) | external authority links here |
| 12 | H3 | Noise, Dander & Daily Care | powder-down discussion |
| 13 | H2 | Deep Dive: [B] — same structure | |
| 14 | H2 | Decision Scorecard Matrix (0–10 traits) | temperament, temperament, noise, beginner fit, apartment fit, bonding speed |
| 15 | H2 | Lifestyle Matching Flowchart | first puppy? apartment? full-time worker? noise-sensitive? |
| 16 | H2 | Cost of Ownership Comparison (US) | from price-matrix + financial-entities; H4 first-year breakdown |
| 17 | H2 | First 30-Day Adjustment Timeline | Lisa's first-30-days voice |
| 18 | H2 | Myth vs Reality Cards | H5 supporting facts, H6 breeder notes/citations |
| 19 | H2 | Health & Delivery section | canonical line: Ships nationwide · £200–£350 airport · £200–£350 home (read `delivery_options`) |
| 20 | H2 | Available Puppies / Breeding Pair / Fertile Eggs cards | link-out, don't re-teach; sold ≠ InStock |
| 21 | H2 | Owner Story (BAB) + Reviews | REAL reviews only — never fabricate |
| 22 | H2 | Who Should Choose [A]? / Who Should Choose [B]? | H4 micro-intent answers per household type |
| 23 | H2 | FAQ (8–12 PAA questions, QAB) | FAQPage JSON-LD, visible accordion |
| 24 | H2 | Blog / further-reading cards | 3 relevant posts |
| 25 | H2 | Final CTA + page-specific inquiry form + newsletter | clay pill; `idPrefix` if 2 forms |

**Hard structural gates (non-negotiable):**
- Full **H1→H6 outline presented and approved BEFORE any code** — no skipped levels, all six levels, **≥5 H5 AND ≥5 H6**.
- **Every H2 and H3 carries an image** — OG photo, AI image, or HTML/CSS infographic (same rule as blog posts).
- Word counts: spokes **5,000–6,000**; hub **6,500–7,000**. 2–3 H3 comparison metrics per rival on the hub.
- Headers conversational/Quora-style, hybrid question+entity, **unique per page** (dup H2s across spokes = dup content).
- Section seam dividers (`.bsuk-seam` + footer logo) between major parts, 4–8 per page.
- No visible dates anywhere — freshness in schema only.

## 5. Interactive Decision Modules (converted "calculators")

Text/HTML-CSS modules (pure HTML/CSS/vanilla JS via `@bsuk-interactive-component`; NO ASCII boxes on the live page — those were the MFS draft format):
- **Lifestyle Selector** — "Which Puppy Fits Me?" (flat → the calmer pup; active household → the busier pup; first-time owner → depends)
- **Size & Weight Comparator** — adult weights are NOT FETCHED until the breeder confirms them; the module renders the breed standard's range and says where it came from
- **Price Range Estimator** — BlueStaffyUK's own £1,500–£1,700 litter span from `data/price-matrix.json`; any market average is NOT FETCHED
- **Noise-Level Meter** — a qualitative comparison only; no decibel figure has been measured (NOT FETCHED)
- **Temperament Score** — the breed's family-dog reputation; an honest per-puppy variance note
- **First-year Budget Estimator** — crate, food, vet, insurance, training; every line item NOT FETCHED until the breeder supplies real numbers
- **Trust Documentation Panel** — the vet check, the microchip record, the vaccination card and the health-test certificates the ledger records

Snippet Box (📌 Quick Answer) opens every section — 1–2 sentence AI-extractable summary. Use line-icon SVGs, never emoji.

## 6. E-E-A-T & Voice Rules (converted)

- **Author box** near top: Lisa Bright, BlueStaffyUK – Glasgow, linking to `/blue-staffy-uk-breeders/`.
- **Original breeder data signals** — real, non-obvious observations from our own kennel, in Lisa Bright's voice; NEVER invented statistics. If we don't have the number, we don't print a number.
- **External authority links** in health sections — the RSPCA, the PDSA, Blue Cross, the RVC, thekennelclub.org.uk (curl 403 = bot-block, retry with UA, not dead). 6–8 diverse outbound links per page, anchored at sentence start (Link-First).
- First-person plural brand voice throughout; encyclopedic exceptions for taxonomy/research.
- Anti-AI writing filter + Style-2 gated humor (≤1 beat/section, never on health/legal).
- Negative keyword counter-positioning: puppy farms, scams, cheap unweaned pups.

## 7. Keyword Fan-Out Categories (converted)

A. **Temperament** — affectionate, one-person bonding, calm vs demanding, apartment puppy, separation anxiety, trainability
B. **Noise, Barking & Shedding** — barking, noise level, a quiet dog, shedding, allergies
C. **Size & Coat** — blue vs blue-brindle vs white, full-grown size, coat and markings
D. **Price, Lifespan & Health** — price comparison, the 12–14 year breed lifespan, vet costs, L-2-HGA, HC-HSF4
E. **Lifestyle Match** — best for seniors / families / apartments / first-time owners / busy professionals
F. **Commercial bridge** — for sale UK, breeder, home-raised, health-tested (link down to the money pages)
G. **AI/LLM layer** — "compare X and Y in detail", "help me choose", "pros and cons" phrasing blocks

## 8. Component System — 3 Variants (visual companion gate)

Component variants are decided ONCE for the cluster via the **superpowers visual companion** (browser mockup screens, breeder click-selects), then distributed: **Hero/Component set A → the breed-vs pages · set B → blue-vs-blue-brindle + pros-and-cons + breeders-comparison · set C → male-vs-female + hub.** Full component list and the Claude Design master prompt live in the session brief. Per-section **distribution matrix approval BEFORE code**, always with a Recommended pick + why + trade-off.

## 9. Imagery (Gemini / Nano Banana — no Higgsfield credit)

After outline approval, mark every H2/H3 needing OG photo vs AI image vs HTML infographic. AI prompts follow `rules/images.md` (crop ratios; negative list: no logos, no watermarks, no other breed) and the `rules/design.md` palette. The source repo's image-generation script was **not ported — source repo only**; no API key belongs in this repo. Infographic widths: 760px wrapper (comparison body), 1100px hub hero; 400px desktop height. Image SEO 5-element on every image.

## 10. Pass Gates (page is NOT done until ALL pass)

`npx astro build` → verify in `dist/` → `python3 scripts/final_page_audit.py` → then the full breeder gate list: **SEO · AIO · GEO · AEO · entity coverage · topical authority · anti-AI · non-commodity · humor policy · keyword variation · keyword-verifier · technical SEO · Lighthouse (warm median-of-3)**. Preview before apply. Commit + push after every approved build (work on `main` only). Sitemaps regenerate after any page change.

## 11. Breeder-Review Component Standard (2026-07-04 — BINDING for all 8 pages)

The blue-vs-blue-brindle rebuild was rejected once and redone; these fixes are now the floor for every
comparison page. Reference implementation: `src/pages/uk-staffordshire-bull-terrier-guide/index.astro`.

1. **Hero** — full-bleed band (background spans viewport, content in `.container`), homepage height
   (~380–480px desktop), copy LEFT / two staggered OG puppy portraits CENTER-RIGHT with a small `vs`
   roundel at the overlap; mobile stacks **images first**. Eyebrow is **sentence case** (never
   uppercase), clay `#b04228`. H1 `clamp(1.75rem, 3vw, 2.25rem)`. Hero images get responsive
   `srcset` (480w + 800w) + `heroPreload`/`heroPreloadSrcset` in BaseLayout.
2. **No HTML/CSS infographics.** Every H2 + important H3 image slot is a real OG photo or a Gemini
   image (distinct design style per section, the `rules/design.md` palette, 16:9 1600×900 → 760×400 slot).
   The source repo's prompt pack was not ported — source repo only; write the page's own.
   The real `<table>` stays in the DOM for AIO — an image never replaces it.
3. **Photo-first cards everywhere.** A puppy card is that pup's real photo (800×800 crop) +
   a colour badge + the price from `data/price-matrix.json` + the delivery line. Delivery
   renders as two cards — **UK home delivery £200–£350 by distance,
   by DEFRA-approved transport**, and **collection in Glasgow** — each with its own photo and
   + a 7-place state/city pill row with FRESH anchors (each comparison page uses a different angle set).
4. **Sticky offsets** — site header is `sticky` and **96px** tall: jump rail `top:96px`, desktop TOC
   `top:calc(96px + 24px)`, every section `scroll-margin-top:calc(96px + 18px)`, `:global(html){scroll-behavior:smooth}`
   (+ reduced-motion opt-out). TOC column 200px / gap 34px (not 230/40) to widen the article column.
5. **Contrast floors** — buttons + solid chips fill `#b04228` with white (5.7:1); table verdict cells
   `--color-brand` bold (≥6:1); never clay-on-clay: inside the article column add
   `.cvt-main a.btn-clay{color:#fff;text-decoration:none}` or the generic link rule silently overrides it.
6. **Form = what we sell** — short inquiry form with: interest select (Blue / Blue-Brindle / breeding pair /
   fertile eggs / not sure, prices visible), first + last name, cell + confirm, email + confirm,
   delivery select (£200–£350 airport / £200–£350 home / Glasgow pickup), optional home note. Pass
   `hideGlobalCta` and ship NO page-level newsletter band (the form is the single closer).
7. **Testimonials = real reviews only**, pulled from the verified homepage `bottomReviews[]` set with
   real name + city; never the fabricated pair this page originally carried.
8. **Blog cards** use each post's own `-card.webp` hub thumbnail, never a shared generic image.
9. **Links at the START of sentences only (Link-First rule) — never mid-sentence, never the final words.** Seam dividers use
   `bsuk-footer-logo-80.webp` (the 200×66 original wastes ~7KiB per Lighthouse).
10. **Schema** — no page-level BreadcrumbList (the Breadcrumb component emits it; duplicates FAIL the
    gate). Title = 4-part ending in `BlueStaffyUK – <LSI keyword>` (never "BlueStaffyUK – Glasgow" again).
11. **Gate** — `python3 scripts/final_page_audit.py --comparison` (profile added 2026-07-04) must
    return PASS/PASS-WITH-WARNINGS; the old `no_userselect_none` site-wide FAIL was a Tailwind
    `.select-none` false positive, fixed in the auditor.

## 12. Final Polish-Pass Fixes (2026-07-05 — BINDING, from the blue-vs-blue-brindle finishing pass)

Every comparison page must clear these on its finishing pass, in addition to §11:

1. **Counter snippet is page-specific, not the homepage set.** The homepage's `12+ / 100% LICENCE_CLAIM_PLACEHOLDER /
   NOT FETCHED floor / 24h` is generic. A comparison page leads with its own premise: for variant/species
   pages use **`2` Staffy species raised here · `12+` Years raising both** (the "we raise both" moat),
   keeping `100%` LICENCE_CLAIM_PLACEHOLDER + `24h` reply as the two trust anchors. Never ship the verbatim homepage four.
2. **Responsive infographics (Lighthouse "improve image delivery").** Every 1408×768 `inf-img` ships a
   `-760.webp` sibling (Pillow LANCZOS, q82) + `srcset="/name-760.webp 760w, /name.webp 1408w"
   sizes="(max-width:900px) 92vw, 760px"`. Cuts ~40–55% off each (the blue-vs-blue-brindle set went
   583→327 KiB). The 1408 stays as the retina/desktop candidate; the table stays in the DOM.
3. **Square OG portraits get a `.portrait` modifier** (`aspect-ratio:1/1;max-width:420px;margin:auto`).
   Bare `.sec-img` forces 760/400 cover and decapitates square close-ups — always check intrinsic
   dims; if the file is square/portrait, add `.portrait` and fix the `width`/`height` attrs to match.
4. **Non-primary data tables stack into cards on phones.** The mobile tab-toggle is ONLY for the main
   side-by-side table. The 6-trait scorecard (and any other `<table>`) needs `data-label` on each `td`
   + a `@media(max-width:640px)` block: `thead` offscreen, `tr`→bordered card, `td`→flex row with
   `::before{content:attr(data-label)}`. Note td stacks column-wise for long text.
5. **Internal links to the three money/authority hubs, anchored at sentence start (Link-First), from their own sections:**
   Reviews → `/blue-staffy-uk-breeders/` (Owner Stories), FAQ → `/uk-blue-staffy-puppy-buying-guide/` (FAQ intro),
   Delivery → `/buy-blue-staffy-puppies-uk/` (delivery body copy).
6. **Route pills carry a map-pin SVG + cream tint (`#f4efe9`), `inline-flex`; 2-col centered on
   mobile** (`.pin` stays `flex:none`). Body copy above the pills links the delivery page.
7. **Reversed head-term + American spelling coverage.** Weave "Blue-Brindle vs Blue" AND "Blue Staffy"
   (with an *a*) once, naturally, in the Quick-Answer close; add **"What is the difference between…"**
   and **"How can you tell … apart"** FAQ objects (they feed both FAQPage schema and the open-3
   featured block). Dedupe against existing copy first — ignore keywords already on the page.
8. **Do NOT add Partytown for GA.** BaseLayout already interaction/idle-defers gtag.js off the critical
   path. Lighthouse's `unused JavaScript` (~72 KiB `/70de/`), `forced reflow`, `render-blocking`,
   `missing source maps`, and `cache TTL` flags are all **the host (NOT FETCHED until project 6) Rocket Loader** — a dashboard
   toggle + cache purge, never a repo fix. Note this in the page's fix log; don't chase it in code.

## §13 Component Polish Contract (2026-07-12 breeder pass — binding on every spoke, new or rebuilt)

Every fix below came from a breeder complaint on the live cluster (CvM screenshot session). They are
now the shipped baseline on CvT / CvM / CvC / MvF — new spokes copy these patterns, never the older ones.

1. **NEVER `scroll-behavior:smooth` on `html`.** On 60k-px comparison pages Chrome cancels the smooth
   fragment scroll at frame zero (lazy-image layout shifts), so every jump-rail tap looks dead: hash
   updates, page never moves. `scrollIntoView`/`scrollTo` still work, which misdirects debugging.
   Homepage baseline is `auto`; `scroll-margin-top` on targets does the offset work. Diagnostic: set
   `document.documentElement.style.scrollBehavior='auto'` and re-tap — if it jumps, that was the bug.
2. **Jump rail must be sticky — never re-`position` it.** `.cvt-rail{position:sticky;top:var(--hdr)}`
   is the contract. Adding `position:relative` later (e.g. "for the ::after fade gradient") silently
   kills sticky — a sticky element is already a containing block for absolute children. CvM shipped
   broken this way while its 3 siblings worked.
3. **Counter snippet = slim inline credential STRIP, not the hero-metric template.** The old design
   (40px circle icon chips + 2.1–2.2rem serif numbers + uppercase tracked labels + 4 stacked columns)
   is the exact "big number, small label" cliché DESIGN.md bans, and it rendered ~330px tall on
   phones. The shipped pattern: no icon chips at all; number and sentence-case label inline on one
   baseline (`display:flex;align-items:baseline;gap:9px`); numbers `1.4rem` Fraunces desktop /
   `1.2rem` tablet / `1.1rem` phone; labels `.8rem`→`.74rem` `font-weight:500`, NO uppercase, NO
   letter-spacing games; desktop one flex row with `1px rgba(255,255,255,.18)` htransport partners (~54px
   band), ≤900px a 2×2 grid (~115–140px). Content stays page-specific per §12-1.
4. **`.container` eats vertical padding — pad the SECTION.** `.cvt .container` sets
   `padding:0 clamp(16px,4vw,48px)` at higher specificity, so `padding-top/bottom` on any
   `.container counter-row`-style element computes to 0 (the old counter never had its intended
   padding — that was the "rushed" look). Put band padding on the section: `.cvt-counter{padding:14px
   0}` desktop, `9px 0` mobile.
5. **Hero eyebrow (prefix) is UNIQUE per spoke, drawn from the page's own premise.** Never reuse the
   "Home-raised · LICENCE_CLAIM_PLACEHOLDER-documented · Glasgow" trust string across spokes — trust tokens live in
   the hero-meta pills. Shipped set: CvM "11 english bull terrier species sized against one quiet genius" · CvC "The
   cuddler and the family dog, weighed honestly" · CvT "Two Staffy subspecies, raised side by side since
   2014" · MvF "Cock or hen · DNA-certain before you ever pay". A new spoke writes its own from the
   comparison premise; duplicate eyebrows across siblings FAIL the pass.
6. **Seam divider = brand medallion + light-orange fading htransport partners.** `img
   src="/bsuk-header-logo-160.webp"` (the ONLY square logo asset — every `bsuk-footer-logo*` /
   `bsuk-seam-logo` / `bsuk-logo-badge*` file is a wide wordmark that letterboxes into a smudge inside
   the circle), `width/height=54`, CSS `object-fit:cover;padding:2px;border:2px solid
   rgba(232,96,76,.35);border-radius:50%`. Lines: `height:2px;border-radius:1px` fading gradients to
   `rgba(240,128,112,.6)` (--clay-lt), replacing the old faint 1px `#cdbfae`.
7. **Middle newsletter is ALWAYS `NewsletterV2 variant="middle" compact`.** The full-height variant's
   36px H2 overtakes the page H1 in the 768–860px band (MvF shipped that inversion). `compact` is not
   optional on comparison spokes. (CvT currently has no middle newsletter — decision pending.)
8. **H1 must outrank every H2 at EVERY width, including one-off hero H1 classes.** The
   breeders-comparison `bc-h1` clamp `(1.8rem, 3.5vw, 2.75rem)` sat on its floor through the whole
   375–860px band underneath a static 36px CTA H2. Fixed form: `clamp(1.9rem, 0.5rem + 4.5vw,
   2.75rem)`. Sweep rule: resolve the clamp at 375/640/768/860/1280 and compare against the largest
   H2 (usually the CTA/newsletter component) before delivery.
9. **Image budget <100KB per delivered file.** Recompress with Pillow WebP `method=6`, walk quality
   78→54 until <95KB (LICENCE_CLAIM_PLACEHOLDER-flatlay 101→94KB q66, vs-french bulldog-hero 122→89KB q66 — certificate text
   still crisp). Masters in `assets/brand/` untouched.
