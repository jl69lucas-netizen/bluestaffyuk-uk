---
name: bsuk-blog-post
description: "Use when building or rebuilding any BlueStaffyUK blog post or the /blog/ hub — the 14-step section architecture, desktop+mobile component map, 8 bsuk-blog-* special-element components, tiered Sprint 0.5 research, Style-2 gated humor, and 1,800–2,500 intent-scaled word counts. Triggers: \"write a blog post\", \"build the blog\", \"blog hub\", \"crate setup post\", any /blog/<slug> page. Reconciled to DESIGN.md; source of truth docs/superpowers/specs/2026-06-27-BSUK-blog-cluster-system-design.md."
allowed-tools: [Read, Write, Bash]
---

THIS PAGE CONTAIN THE CHATGTP RESEARCH WORK DONE FOR ALL BLOG POST AND HUB PAGES AS WELL AS THE SKILL, GUILDLINES, RULES, ETC ON HOW TO CREATE THE BLOG POST., YOU MUST ENHANCE AND IMPROVE THE SKILL BELOW, I THINK WE HAVE A BLOG POST AGENT/SKILL, SEE IF WE CAN ADD OR CREATE A COMPREHENSIVE BLOG POST SKILL/AGENT, FRAMEWORKS, ANGLES, BASED ON THE DATA HERE, FRESH BING SEARCH, I HAVE DONE TOP 3 COMPETITORS ON GOOGLE ALREADY AS SEEN BELOW AND LASTLY THE 30 COMPETITORS WE HAVE IN THE LIST, ETC. EVERY TEXTS/WORDS, ETC IN THIS FILE/DOC IS IMPORTANT MAKE USE OFF THEM ALL, ARRANGE THEM ACCORDINGLY BASED ON THE STEP/PROCESS OF THE PAGE CREATION, ETC.

* Change of plans, i want to see their weakness, all Headers, keywords types  
* We

---

## BlueStaffyUK Blog System (binding — 2026-06-27)

> **Source of truth:** the source repo's blog-cluster spec was **not ported — source repo only**; the sections below ARE the binding rules here. This file governs in any conflict.

### 1. 14-Step Section Architecture + Special-Element Slots

Every blog post follows this fixed skeleton (all 9 posts + hub). Bucket codes: **MANDATORY** / **SUGGESTED** (our moat) / **COMPETITOR-DATA** / **[SPECIAL-ELEMENT SLOT]**.

1. **Hero** — MANDATORY. Eyebrow + H1 (primary KW) + dek + hero image/infographic + 1 soft CTA chip.
2. **Top lead-capture strip** — MANDATORY. Slim inline capture (care/resource-page pattern, commit `ba434ee`).
3. **TOC / jump links** — MANDATORY (long-form).
4. **[SPECIAL-ELEMENT — TOP] Quick-Answer / Key-Takeaway box** — MANDATORY. AEO snippet target. Placed **after the TOC — never directly after the Hero.**
5. **Body H2 sections × N** — MANDATORY. Topic clusters from each page's `.md`. Inline callouts (bsuk-blog-callout tip/alert) woven in.
6. **Comparison / spec table** — COMPETITOR-DATA.
7. **[SPECIAL-ELEMENT — MIDDLE] Mid-article conversion module** — Decision-Tree OR Myth-vs-Fact OR inline available-puppies soft-CTA, chosen per page from competitor-gap analysis.
8. **Breeder Note / E-E-A-T block** — SUGGESTED moat. First-person BlueStaffyUK insight (bsuk-blog-breeder-note component).
9. **"What you get from a real breeder" trust band** — SUGGESTED moat.
10. **FAQ accordion** — MANDATORY. Every pick in `data/queries/<slug>.json`, each question an H3; one block, as the post template renders it (the three-block split is location-only). Visible FAQPage JSON-LD carrying exactly the visible questions.
11. **[SPECIAL-ELEMENT — BOTTOM] Bottom conversion module** — Available-puppy card + inquiry CTA. Delivery line: `Ships nationwide · £200–£350 airport · £200–£350 home`.
12. **Related blog posts** — MANDATORY silo. bsuk-blog-related-posts component.
13. **Newsletter block** — MANDATORY (lower placement; top strip does early capture).
14. **Global CTA band** — MANDATORY. Via BaseLayout `hideGlobalCta` if a section already owns the CTA.

Every page carries all three special-element slots (TOP/MIDDLE/BOTTOM). MIDDLE module is chosen per page.

---

### 2. Component Map — Desktop + Mobile Parity

**Blog post components** (the source kit was not ported — source repo only; build each from this list): Hero / 3-Split, Mobile Hero, Jump Links / 3 contexts, Mobile Jump Nav, Buyer's Guide Article, 3-Column Grid, Mobile Blog, Mobile Cards, FAQ / 3 zones, Mobile FAQ, Component Library newsletter/inquiry forms, Mobile Newsletter, Mobile Inquiry. **Type Specimen** + **Mobile Type** are the type-scale lock — they enforce identical H1–H6 + body heights across all breakpoints (the breeder's explicit parity requirement). Do not override font sizes in per-page CSS.

**8 new reUKble Astro components** (built in `src/components/`):
- `bsuk-blog-quick-answer` — TOP special-element; AEO snippet capture.
- `bsuk-blog-callout` — tip + alert variants; Coat SVG icons (never emoji).
- `bsuk-blog-comparison-table` — spec table with "breeder verdict" row.
- `bsuk-blog-breeder-note` — first-person E-E-A-T moat block.
- `bsuk-blog-myth-fact` — Myth-vs-Fact card.
- `bsuk-blog-decision-tree` — AI-extraction-friendly; used on beginners + vs-French Bulldog pages.
- `bsuk-blog-related-posts` — silo internal-link cluster to the other 8 posts + money pages.
- `bsuk-blog-sticky-cta` — mobile-only sticky bar ("See available Staffies").

All 8 inherit the site tokens (do NOT re-implement per page). Reference the tokens in `src/styles/tokens.css`; never spell a hex in `src/`. Never hardcode stale palette values (`#1F7A4D`, `#FF6210`).

---

### 3. Tiered Sprint 0.5 Research Method + 17-Field Output Format

**First, run `/bsuk-query-augmentation <slug> blog "<primary keyword>" <route>`.** Its
file (`data/queries/<slug>.json`) supplies the page's FAQ picks and three extra sections. Every
pick appears on the page, each an H3 (one `Faq` block is fine here — the three-block split is
a location-page rule), and every `must_answer` question is answered with `covered_by` recorded —
`npm run check:queries` fails the page otherwise. The research below builds on that file; it
does not replace it.

**Depth:** a competitor scan to identify who owns each topic and where their gap is (no competitor registry was ported and none has been fetched — an un-fetched competitor is NOT FETCHED); deep audit of top 6 per page (3 Google from the per-page `.md` + 3 fresh Bing). Non-leaders get a light pass.

**Per-page strategy doc** → `sessions/YYYY-MM-DD-blog-strategy-<slug>.md`. 17 required fields:
1. Page + primary KW + search-intent split (info/commercial/transactional %)
2. Content-type verdict (competitor posture vs. recommended BlueStaffyUK posture)
3. Top-3 Google competitors (from per-page `.md`)
4. Fresh Bing top-3 (live per keyword)
5. 30-competitor registry signal (who ranks/owns + gap)
6. **Competitor on-page keyword audit table** — per competitor: KW in slug/title/meta/H1, on-page count, variations, entity types, content category
7. Why they rank (reverse-engineered signals)
8. Keyword universe — primary/secondary/LSI; weighted to **6+ word long-tail + conversational/voice queries**
9. Entity coverage (types + categories for AEO)
10. Competitor voice + angle → BlueStaffyUK winning-angle options
11. Competitor content gaps (our wedge)
12. Full H1–H6 outline (render order, sequential, ≥5 H5 + ≥5 H6)
13. **Section distribution matrix** — per section: A/B/C category, framework, word-count split, special-element slot
14. Featured-snippet + PAA targets
15. Schema set per page
16. Internal-link + image plan (silo links + image → section map)
17. **Framework / angle / keyword OPTIONS for breeder to select** — each marked (Recommended) + why + named trade-off

**The breeder selects** frameworks, angles, entities, keywords, variations before any code is written.

---

### 4. Voice, Humor & Length

- **Voice:** First-person plural BlueStaffyUK — "we / us / our / here at BlueStaffyUK." Encyclopedic exceptions for taxonomy/cited research only. See CLAUDE.md, rule 1 of the twelve.
- **Humor:** Style-2 dry/transparent. **≤1 beat per section, gated.** Permitted on commercial/comparison/lighter pages (price, vs-French Bulldog, beginners, best-place-to-buy). **ZERO humour on health pages, and on any medical, legal or licence content.**
- **Length:** **1,800–2,500 words, intent-scaled** — comparison/price leaner; care guides (crate/health/training) fuller. Long-tail 6+ word + conversational/voice query weighting throughout.
- **Content posture:** transactional/commercial/comparison-led. AI-overview-resistant via breeder moat + buyer-advocate framing + strategic CTAs.

---

### 5. Baked-in Gates (non-negotiable, every blog page)

- **Heading Outline Gate** — present full H1→H6 outline (all six levels, sequential, ≥5 H5 AND ≥5 H6) + get explicit approval **BEFORE any page code**. No skipped levels. See `rules/headings.md` (`heading-hierarchy-outline-gate`); the rule moved out of CLAUDE.md on 2026-08-02.
- **Line-icons not emoji** — Coat-style SVGs (`1em`, `currentColor`). Keep only ✔ ✗ ★ text glyphs. Never use 💡 ⚠ or any pictograph emoji.
- **Delivery line on every card** — `UK home delivery £200–£350 by distance · or collect in Carlisle`. Pull from `data/settings.json` and `data/price-matrix.json`. No hardcoded figures.
- **Schema visible + verified in `dist/`** — extend existing JSON-LD, never duplicate. Verify with grep on `dist/` output, not source files.
- **One CTA per page** — BaseLayout global band; `hideGlobalCta` when a section owns the CTA.
- **NEVER a visible date** — freshness in schema only (`dateModified` / `datePublished`). No "Updated June 2026" visible text anywhere.
- The licence line (LICENCE_CLAIM_PLACEHOLDER) and the statute line (LEGAL_CLAIM_PLACEHOLDER), in prose only, on every page that needs them — and only as recorded in `data/quality/evidence-ledger.json`.
- **Type parity** — identical H1–H6 + body heights desktop/tablet/mobile enforced by Type Specimen + Mobile Type components.
- **Final gate:** `python3 scripts/final_page_audit.py` (blog profile) → must PASS before deploy.
- **Deploy:** commit + `git push origin main` after each build (= deploy) → `scripts/generate_sitemaps.py` → `@bsuk-deploy-verifier`. Build always on `main`, never feature branches.

---

### 6. Color Token Note

CSS custom properties are **not auto-imported** in Astro components. In the blog components and any blog page sections, reference the tokens defined in `src/styles/tokens.css` (imported by `src/styles/global.css`); never spell a hex in `src/`. Canonical palette: steel blue `--color-brand` (`#1F3A52`) · brass `--color-cta` (`#C9A227`), whose label is always `--color-cta-ink` (`#14202B`, 6.8:1) · bone `--color-surface` (`#F4F1EA`). Brass is a **fill colour, not a text colour on light**: `--color-cta` on `--color-surface` is 2.1:1 and fails. Small readable text on a light surface is `--color-text` (13.9:1) or `--color-brand` (10.4:1). Never use a stale palette value from the previous site.

---

### 7. Finalization & Polish Playbook (learned 2026-06-28 on crate-setup — apply to EVERY blog page before "pass")

These are the things the breeder caught polishing the crate-setup pilot. Bake them into every blog build/rebuild so they never recur.

**A. Mobile performance → 100% (the `/70de/` mystery script).**
- The PageSpeed items **"missing source maps for large first-party JS"** and **"reduce unused JavaScript 72 KB"** pointing at `/70de/(SITE_URL_PLACEHOLDER)` are **the host (NOT FETCHED until project 6) Rocket Loader**, injected at the edge — it is **NOT in our source** (`grep` finds nothing). On CPU-throttled mobile it is the single biggest drag (why mobile lags desktop).
  - **Fix = MANUAL, the host (NOT FETCHED until project 6) dashboard only:** dash.the host (NOT FETCHED until project 6).com → SITE_URL_PLACEHOLDER zone → **Speed → Optimization → Content Optimization → Rocket Loader → Off** → then **Caching → Configuration → Purge Everything**. The "missing source map" line is *Unscored* (informational) — Rocket Loader removal makes it vanish.
- **Image delivery (code, do this every page — upgraded 2026-07-03 after Lighthouse re-flagged all 9 posts):**
  - Every hero/in-content image needs a **~680w variant** in its srcset. PageSpeed's mobile device is a Moto G at **380 CSS px × DPR 1.75 = 665 physical px**; with only 500/760/800w variants the browser downloads the 760/800w file and Lighthouse flags "larger than needed for displayed 665×…". The 680w tier is what clears it. The shared `ig()` helper srcset is now `680w, 760w, 1200w` — generate a `-680w.webp` for every infographic base the page uses.
  - **Compression bands (Pillow, `method=6`):** photos/infographics that Lighthouse flags "increase compression factor" → re-encode at **quality 55–62** (q82 is what got flagged). Busy photos tolerate q48–55. Verify each file lands well under 100KB — the temperament-ability 760w went 55KB→35KB at q48 with no visible loss.
  - **Seam divider logo:** use `/bsuk-seam-logo.webp` (160×53, ~6KB) in every `.bsuk-seam`, NOT `/bsuk-footer-logo.webp` (200×66) — the seam renders at 91×30 CSS so the full footer logo gets flagged for both resize and compression on every page.
  - **Video posters:** never reuse a full-size photo as `poster` — cut a dedicated ~480w q55 `-poster.webp`.
  - Generate variants with **Pillow** (`Image.resize(..., LANCZOS).save(..., "WEBP", quality=Q, method=6)`) — `cwebp` is NOT installed. Hero `sizes`: `(min-width: 768px) 480px, 92vw` for a 2-col hero, `(min-width: 768px) 700px, 92vw` full-width in the 760px container, `(min-width: 768px) 712px, 92vw` for `ig()` infographics.
- **Hero preload must mirror the srcset** or the LCP image double-downloads. `BaseLayout` now takes `heroPreloadSrcset` + `heroPreloadSizes` (→ `<link rel=preload imagesrcset imagesizes>`). Always pass them when the hero `<img>` uses `srcset`.
- Fonts (media=print swap) and GA (interaction-deferred) are already handled in BaseLayout — don't re-solve them.
- **Render-blocking CSS is SOLVED globally (2026-07-03):** `astro.config.mjs` sets `build.inlineStylesheets: 'always'`, so ALL CSS (incl. the ~105KB BaseLayout bundle) is inlined into each page's `<style>` — no external stylesheet, no critical chain. Do NOT re-add `<link rel="stylesheet">` for local CSS, and do NOT revert to 'auto'. Corollary: **anything in ANY component's CSS now appears in EVERY page's HTML** — a single `select-none` Tailwind utility or `user-select: none` rule anywhere in src/ makes `scripts/final_page_audit.py` hard-FAIL the whole site (`no_userselect_none`). The utility was stripped from puppy-page FAQ summaries + `SiteFooter.astro` on 2026-07-03; never reintroduce it.

**B. Author signature / E-E-A-T (every post).** Ship a **visible** byline, not just schema. Pattern: hero byline `Written by Lisa Bright · BlueStaffyUK… LICENCE_CLAIM_PLACEHOLDER-licensed since 2014` (small, `text-xs`, on the hero dek) **and** a signed editorial sign-off at the end of the body (`— Written by Lisa Bright, …`). Keep `author: { "@type": "Person", name: "Lisa Bright" }` in the Article schema too. This is an AI-citation + Google-author signal.

**C. Hero eyebrow parity (do not ship `text-sm uppercase`).** Blog hero eyebrow = the Roys/homepage style: `font-body text-xs font-medium tracking-wide`, **sentence/Title case (NOT uppercase)**, color **`--color-link-on-inverse`** on the steel `--color-brand` hero. `text-sm uppercase tracking-widest` renders oversized on mobile (no fluid shrink) — the breeder flagged it explicitly.
  - **AA contrast on the steel hero (computed from `data/design/contrast.json`, project 3):** the eyebrow token `--color-link-on-inverse` is 9.1:1 on `--color-surface-inverse` and `--color-text-on-inverse` is 10.4:1, so both clear AA at `text-xs`. `--color-cta` is 4.9:1 there — fine for a large accent, never for `text-xs`. The old "body text on the band needs ≥0.85 alpha" rule does **not** carry over: the steel band is dark enough that `--color-text-on-inverse` at 0.7 alpha still measures 6.0:1. Do not put `--color-cta` on `--color-surface` (2.1:1) at any size.

**D. "Page already shows for a query but has no coverage" → FAQ-first.** From project 6, when search console shows the page ranking for a query the body doesn't answer, **verify existing coverage first**, then add the question to the data — a bank row in `data/faq.json` or a real sourced question in the page's raw files — rebuild the question file (`/bsuk-query-augmentation`), rebuild the page from its picks and fill `covered_by`. Never add an entry to the page's `faqs[]` directly. If it is a real subtopic, add one sequential H3 (never skip a level — re-run `scripts/final_page_audit.py` to confirm ≥5 H5 / ≥5 H6 still hold). Watch for intent splits the single-topic page misses: e.g. crate-setup showed for **"two Blue Staffies"** and **"breeding crate size"** — both distinct from the single-companion-crate the page covered. Always show the placement map for approval before writing.

---

### 8. Competitor Deep-Dive Protocol — Weakness · All Headers · Keyword Types (binding — 2026-07-02)

The breeder's standing "change of plans": for every post, don't just name competitors — **expose their weakness, extract ALL their headers, and classify their keyword types.** This is field #6 of the 17-field research (§3) upgraded to a required, tool-driven pass. Run it BEFORE the outline gate.

**Sources to pull (in order):** (1) the page's own research doc; (2) a **fresh Firecrawl `firecrawl_search`** for the primary KW + one reputable/"legit" variant (location: United Kingdom) — the real current SERP; (3) the 30-competitor registry a competitor registry (not ported — source repo only).

**For each of the top 5–6 rankable results, scrape with `firecrawl_scrape` (formats:["json"], onlyMainContent:false)** and extract into a schema: `page_title, meta_description, h1, h2_headings[], h3_headings[], visible_keywords[], has_pricing, trust_or_scam_content_present, content_type`. Forums/FB/Reddit and video = note as UGC/video (not header-outrankable) but record that they rank — a SERP owned by forums is a **wide-open authoritative-guide lane**.

Then produce three tables in the strategy doc (see the worked example in `sessions/2026-07-02-blog-strategy-best-place-to-buy-blue-staffy-puppy.md §7`):
- **7a. Fresh SERP table** — result · type · why it ranks · **weakness (our wedge)**.
- **7b. On-page structure** of the true exact-match competitor(s) — their H1/H2/H3 verbatim + keyword types on page + what trust/scam/pricing they omit.
- **7c. Keyword-type map** — rows = keyword type (head / commercial-investigation / **scam-avoidance** / transactional / long-tail-conversational-voice / entity-AEO / local), cols = examples · who owns it now · our on-page coverage.
- **7d. Content-gap list** — the moves nobody makes (= our moat), each mapped to an on-page section.

**Rules:** never fabricate a competitor metric — un-fetched = `NOT FETCHED`. Never invent competitor traffic/DR. Extract their **weakness** honestly (thin, no trust, login-walled, free-builder platform, exact-string-match-but-no-education) — that weakness list becomes our section plan. If a scrape 404s or returns a fallback, say so and downgrade confidence rather than trusting the JSON.

### 9. The 2026 "Perfect Blog Post" Framework (binding voice/structure rules)

Layer these onto the 14-step architecture — they are how we beat commodity + AI-overview content:
1. **Satisfy intent above the fold** — a 2–3 sentence **TL;DR / Quick-Answer** before any scroll (this is the TOP special-element, §1 step 4). Answer the primary question in the first 50 words of every H2 (BLUF).
2. **Predict the next question** — after each answer, structure toward what the reader asks next, and link there (price → first-year cost; temperament → training). No reason to return to Google.
3. **"RELATED:" binge links** — above key H2s, a bolded inline **RELATED: [Post Title]** link (rendered as a styled inline callout, not all-caps shouting) to pull readers into a second tab and deepen the silo. Distinct from the bottom `bsuk-blog-related-posts`.
4. **Humanize / SEO-storytelling** — 1–3 sentence paragraphs, parenthetical asides, italic emphasis, the BlueStaffyUK breeder "smart friend" voice. Real, unpolished breeder/puppy photos over stock (conversion + trust).
5. **Anti-AI fingerprints** — run `.claude/skills/anti-ai-writing/SKILL.md`. Ban em-dash-as-dramatic-pause overuse, "delve / unlock / leverage / groundbreaking / in today's world / navigate the world of". Human-in-the-loop: AI drafts, breeder facts + the Verified-Claim Ledger govern.
6. **Interactive engagement (optional, per page)** — an AI-generated 3–5-question comprehension quiz (mid or end) as a self-contained HTML/JS widget in brand hex, whose success message recommends the newsletter or an available puppy. Gate to lighter pages; never on a health, licence or legal page.
7. **Formatting for skimmers** — bold key terms, real HTML tables (not image-of-table) for data, clean bullet/step lists for snippet + AI-chunk capture.

### 10. Visual Production Pipeline + Image-Placeholder Workflow (proven on best-place, 2026-07-02)

**Placeholder-first (default).** Build the page with image constants + `<figure>` slots wired to **exact final paths**, but treat every generated asset as a PLACEHOLDER until the breeder confirms design/size. The breeder supplies real puppy photos + generated infographics into `assets/BSUK-BLOG-POSTS/<Page>/`; a manifest in the strategy doc lists each target filename. **Do NOT commit/push while any referenced image 404s** (main auto-deploys → broken imgs go live).

**Asset categories & sizes** (art direction from `rules/images.md` + `rules/design.md`; palette steel blue `#1F3A52` (= `--color-brand`), brass `#C9A227` (= `--color-cta`), bone `#F4F1EA` (= `--color-surface`); type Fraunces headings, Source Sans 3 body; line icons, no emoji/logos/other species/visible price overlays):
| Category | Per page | Native gen size | On-page render |
|---|---|---|---|
| Hero (photoreal editorial) | 1 | 1408×768 or 1600×900 (16:9) | `srcset` 480w/800w + full; `sizes` `(min-width:768px) 480px, 92vw` |
| Section infographics (flat) | 3–5 | 1200×700 (landscape) | base `.webp` + `-760w`; `sizes` `(min-width:768px) 712px, 92vw` |
| Portrait infographic / checklist | as needed | tall (e.g. 1536×2752) | centered card `mx-auto max-w-sm` + `-560w` (precedent: price-page seller-check, best-place buyer's-shield) |
| Real OG / trust photo | 1–2 | native | plain `<img>` in the long visual-less H2/H3; real brand shot for E-E-A-T |

**The encode → wire → deploy pipeline (copy this):**
1. **Encode with Pillow** (`cwebp` NOT installed): flatten RGBA onto bone `#F4F1EA` (= `--color-surface`) for infographics / white for photos; `Image.resize((w, h), LANCZOS).save(path, "WEBP", quality=82, method=6)`. Generate the srcset variants. Output straight to `public/` at the manifest paths.
2. **Fix CLS** — set each `<img width/height>` to the file's **native ratio** (don't trust the placeholder's guessed dims). Verify in preview that displayed ratio ≈ native ratio (no stretch). Best-place used hero `1408×768`, infographics `1200×655`.
3. **Hero preload mirrors the srcset** (`heroPreloadSrcset`/`heroPreloadSizes`) or the LCP image double-downloads.
4. **Add a visual to every long visual-less H2/H3** — the breeder's rule: tall/important sections must carry an image; weave real OG photos into them.
5. **Rebuild** (`npx astro build`) → confirm every referenced `.webp` exists in `dist/` (grep the built HTML, fail on any missing) → **`python3 scripts/final_page_audit.py --blog`** must PASS → preview-verify images 200 + ratios → then deploy.

### 11. Universal Special-Element Boxes (reuse on every page)

Every page carries the 3 slot boxes (TOP/MIDDLE/BOTTOM, §1) plus draws from this catalog — all token-themed Astro components, Coat line-icons only (never 💡/⚠/emoji):
1. **Quick-Answer / TL;DR** → `bsuk-blog-quick-answer` (TOP, AEO).
2. **Breeder Note** (first-person moat) → `bsuk-blog-breeder-note`.
3. **Expert Tip** → `bsuk-blog-callout` variant `tip`.
4. **Mistake / Warning Alert** → `bsuk-blog-callout` variant `alert`.
5. **Myth vs Fact** → `bsuk-blog-myth-fact`.
6. **Decision Tree** (AI-extraction-friendly) → `bsuk-blog-decision-tree` (MIDDLE on beginners / vs-French Bulldog).
7. **Comparison / spec table** (with "breeder verdict" row) → `bsuk-blog-comparison-table`.
8. **FAQ accordion** (visible + FAQPage schema) → page `faqs[]` array, filled with exactly the question file's picks (one block; the three-block split is location-only), each question an H3.
Plus `bsuk-blog-related-posts` (bottom silo) and `bsuk-blog-sticky-cta` (mobile).

### 12. Toolbelt & BSUK Context (know these before building any post)

- **Competitor intel:** Firecrawl MCP (`firecrawl_search` fresh SERP, `firecrawl_scrape` json headers). Retry with `-A Mozilla/5.0` logic / stealth proxy on 403; `thekennelclub.org.uk` 403-to-curl = bot-block not dead.
- **Images:** Pillow (`quality=82, method=6`), output to `public/`. Infographic and image-generation skills are deferred to project 3, see data/port-manifest.json.
- **Audit/deploy:** `python3 scripts/final_page_audit.py` (blog profile; all six heading levels, ≥5 H5 AND ≥5 H6, no skips) → `python3 scripts/generate_sitemaps.py` (writes BOTH `public/` and `dist/` — commit both) → commit. No push and no deploy until project 6.
- **Data (never hardcode):** `data/settings.json` (the £200–£350 delivery band, the £500 deposit), `data/price-matrix.json` (£1,500 / £1,700), `data/puppies.json` (the available pups), There is no competitor registry and no external-link library here; both are deferred to project 6, see data/port-manifest.json.
- **Deploy/push caveat:** there is **no push and no deploy until project 6** — this repo has no remote. Never add one, and never write a credential anywhere. In a session where the keychain isn't reachable, `git push` fails with "could not read Username" — the commit is safe locally; ask the breeder to push from their terminal. Build on `main` only (feature branches strand at live-404).
- **Cannibalization guard:** blog posts LINK OUT to money/interior pages (for-sale hub, price, scam) — never re-teach or re-list what a money page owns (see best-place §5).

### 13. Fill-in Placeholders (set these before running the skill)

Copy this block into the session brief and fill it before Sprint 0.5:
```
{{TARGET_BLOG_POST}}      e.g. /blog/uk-staffordshire-bull-terrier-guide/   ← the post to work on
{{PRIMARY_KEYWORD}}       e.g. "Blue Staffy vs French Bulldog"
{{BATCH / SESSION DATE}}  e.g. Batch-2 Page 2 · 2026-07-0X
{{SOURCE_RESEARCH_MD}}    assets/BSUK-BLOG-POSTS/<Page Name>/<Page Name>.md
{{IMAGE_SOURCE_FOLDER}}   assets/BSUK-BLOG-POSTS/<Page Name>/   ← breeder drops photos+infographics here
{{FRAMEWORK}}             PAS / EBP / QAB / BAB / PDB (breeder-selected, §17)
{{ANGLE}}                 breeder-selected winning angle + why
{{HUMOR}}                 on (commercial/comparison) | OFF (health, licence and legal pages)
{{IMAGE_MANIFEST}}        list every target /public path + native size (see best-place §Image Manifest)
```
**Session cadence (breeder's plan):** batch-1 (hub, crate-setup, training, temperament-ability, price) built+live; **batch-2 = best-place ✓, vs-french bulldog, facts, health-problems, beginners** — 4 pages/session, next 3 following session.

---
---

## Per-page research data — NOT PORTED

The source repo carried ~2,280 lines of appendix here: its own per-page competitor
research, SERP reverse-engineering, prompt packs and section drafts, all written about a
different animal, a different market and a different set of competitors. **It was not
ported — source repo only.** Re-labelling that research as BlueStaffyUK's would have
manufactured facts nobody fetched, which is the exact failure this port exists to prevent.

What replaces it: §3 and §8 above describe the research method. Run it per page and save
the output beside that page's plan under `docs/superpowers/`. Until a sweep is actually
run for a BSUK page, its competitor set, its SERP signals and its keyword universe are
`NOT FETCHED` — never inferred, never averaged, never borrowed from a sibling.


## Keyword variants — the four extra keyword types (system-gaps, 2026-09-24)

A new location, comparison or blog board carries four keyword types beyond the nine the
brief names: `variation`, `related`, `cooccurring` and `similar`, each a list in a section's
`keywords`. The page needs at least one term of each type SOMEWHERE — not in every section.
The `keyword-variants-missing` check in `scripts/family_rules.py` warns on a draft and fails
from `boarded` on. The twelve pages built before this rule are never asked.

Where the terms come from: after the query augmentation has cached its files and before the
outline is boarded, run `python3 scripts/keyword_variants.py <slug>`. It reads the cached
files under `data/queries/` only (no paid call) and proposes each list with the source of
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
every blog post this skill builds; the `/blue-staffy-blog-guides/` hub, built before this
rule, is not examined.

1. Write each body section from the approved board record, `data/boards/<slug>.json`, and
   from nothing else. The section's H2 is its `heading`; its H3s are its `tree` nodes, in
   record order, word for word (the build may title-case them). The copy answers the
   section's `intent` inside its `words` band.
2. Never open another post's page, board or built HTML for wording. The only text another
   page may share is the whitelist in `scripts/dup_content_audit.py`.
3. A heading the tree does not carry, including an info card's H3 or a special-element
   component's heading, goes back to the board: add it to the tree and re-approve, then
   build. Never add one at build time.
4. The H4-H6 ladder is written at build time. Each ladder heading is new to this post and to
   the site.
5. After `npm run build`, run `python3 scripts/outline_provenance_check.py <slug>` on this
   post and fix every FAIL in the copy, never by widening the whitelist. Only then add the
   post to `data/facts/rebuilt.json`; from that point `npm run check:all` re-runs the gate on
   it with every other listed new-family page. The check ids it prints (`outline-extra`,
   `outline-missing`, `outline-order`, `outline-unknown-section`, `outline-duplicate-heading`,
   `outline-heading-crossover`, `outline-copy-crossover`, `outline-sentence-crossover`,
   `outline-unapproved`, `outline-not-found`) are listed in the script's docstring.

## Project 5 page rules (system-gaps)

These bind every location, comparison and blog-post page built from 2026-09-24 on. The
board refuses the record until each holds (`scripts/family_rules.py`); none of them applies
to the twelve pages built before.

1. **Keywords.** Run `python3 scripts/keyword_variants.py <slug>` (add `--also <cache dir>`
   when a registry folder holds the page's SERP) and write its proposals into the sections'
   `keywords.variation`, `related`, `cooccurring` and `similar`, keeping only terms the
   section really uses. An empty type fails `keyword-variants-missing` from `boarded` on.
2. **Entities.** Run `python3 scripts/ontology_seed.py --check`. Every entity a section names
   is in `data/bsuk-ontology.json` with a source; a health result stays PROPOSED until the
   evidence ledger holds it. The board shows them by class.
3. **External links.** At least six on six domains from four source types, all rows of
   `docs/reference/external-link-library.md` (`external-links-six-diverse`). A location page
   adds its own council's dog or animal-licensing page as a `local` row, after
   `curl -sIL <url>` returns 200, dated in the Verified column.
4. **Anchors.** Every internal and external link carries `anchor_type` (exact, partial, lsi,
   natural, branded, naked-url): three or more internal types with at most two exact, three
   or more external types (`anchor-type-variation`), and never an anchor another board
   already uses for the same target (`anchor-reuse-sitewide`).
5. **Images.** Run `python3 scripts/image_candidates.py <slug> --write`. The hero and every
   body H2 and body H3 (FAQ blocks excepted) carry an image slot (`image-slot-missing`),
   filled in this order: the page's own migrated image, another served image, a file from
   `Assets/Images/` ingested with `python3 scripts/ingest_image.py folder`. When none fits,
   the slot is `source: generate` with an OG style, or `source: infographic` with an IG style,
   named in `IMAGE-DESIGNS.md`. The generated file is drafted with
   `python3 scripts/ingest_image.py draft`, approved on a second pass of the board by its
   sha12 pick, and only then published with `python3 scripts/ingest_image.py publish`
   (`image-generated-unapproved`).
6. **Board and approval.** The board's block 7b lists every rule above for this page,
   evaluated as approval will see it; `scripts/board_approve.py` refuses the approval, and
   any re-approval, while one of them FAILs. The build-gate image checks are listed but never
   block approval: they can only pass after the image is approved and published.
7. **Routes.** A blog post's route is in `data/page-map.json` before it is built, or the
   outline gate cannot find it.
8. **After the build,** `npm run -s check:outline` (also in `check:all`) must report the page
   examined with 0 problems.
