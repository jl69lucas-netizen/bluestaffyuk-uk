---
name: bsuk-blog-post
description: "Use when building or rebuilding any BlueStaffyUK blog post (an entry of the blog content collection in src/content/blog/, rendered by src/pages/[...post].astro) or the /blue-staffy-blog-guides/ hub — the 14-step section architecture, the three special-element slots, the research method (query augmentation, the competitor registry, the gap matrix), Style-2 gated humor, and 1,800–2,500 intent-scaled word counts. Triggers: \"write a blog post\", \"build the blog\", \"blog hub\", any blog post page."
allowed-tools: [Read, Write, Bash]
---

THIS PAGE CONTAIN THE CHATGTP RESEARCH WORK DONE FOR ALL BLOG POST AND HUB PAGES AS WELL AS THE SKILL, GUILDLINES, RULES, ETC ON HOW TO CREATE THE BLOG POST., YOU MUST ENHANCE AND IMPROVE THE SKILL BELOW, I THINK WE HAVE A BLOG POST AGENT/SKILL, SEE IF WE CAN ADD OR CREATE A COMPREHENSIVE BLOG POST SKILL/AGENT, FRAMEWORKS, ANGLES, BASED ON THE DATA HERE, FRESH BING SEARCH, I HAVE DONE TOP 3 COMPETITORS ON GOOGLE ALREADY AS SEEN BELOW AND LASTLY THE 30 COMPETITORS WE HAVE IN THE LIST, ETC. EVERY TEXTS/WORDS, ETC IN THIS FILE/DOC IS IMPORTANT MAKE USE OFF THEM ALL, ARRANGE THEM ACCORDINGLY BASED ON THE STEP/PROCESS OF THE PAGE CREATION, ETC.

* Change of plans, i want to see their weakness, all Headers, keywords types  
* We

---

## BlueStaffyUK Blog System (binding)

> **Precedence:** `CLAUDE.md` and the rule packs in `rules/` win over this file; where they are silent, the sections below are the method. The source repo's blog-cluster spec was **not ported — source repo only**.

### 1. 14-Step Section Architecture + Special-Element Slots

Every blog post follows this fixed skeleton (every post, and the hub). A post is an entry of `src/content/blog/` and is served at `/<slug>/` — its frontmatter `slug`, through `src/pages/[...post].astro`. Bucket codes: **MANDATORY** / **SUGGESTED** (our moat) / **COMPETITOR-DATA** / **[SPECIAL-ELEMENT SLOT]**.

1. **Hero** — MANDATORY. Eyebrow + H1 (primary KW) + dek + hero image/infographic + 1 soft CTA chip.
2. **Top lead-capture strip** — MANDATORY. Slim inline capture.
3. **TOC / jump links** — MANDATORY (long-form).
4. **[SPECIAL-ELEMENT — TOP] Quick-Answer / Key-Takeaway box** — MANDATORY. AEO snippet target. Placed **after the TOC — never directly after the Hero.**
5. **Body H2 sections × N** — MANDATORY. Topic clusters from the post's question file (`data/queries/<slug>.json`: its picks and `extra_sections`) and its strategy doc (§3). Inline callouts (bsuk-blog-callout tip/alert) woven in.
6. **Comparison / spec table** — COMPETITOR-DATA.
7. **[SPECIAL-ELEMENT — MIDDLE] Mid-article conversion module** — Decision-Tree OR Myth-vs-Fact OR inline available-puppies soft-CTA, chosen per page from competitor-gap analysis.
8. **Breeder Note / E-E-A-T block** — SUGGESTED moat. First-person BlueStaffyUK insight (bsuk-blog-breeder-note component).
9. **"What you get from a real breeder" trust band** — SUGGESTED moat.
10. **FAQ accordion** — MANDATORY. Every pick in `data/queries/<slug>.json`, each question an H3; one block, as the post template renders it (the three-block split is location-only). Visible FAQPage JSON-LD carrying exactly the visible questions.
11. **[SPECIAL-ELEMENT — BOTTOM] Bottom conversion module** — Available-puppy card + inquiry CTA. Delivery line: `UK home delivery by DEFRA-approved transport, priced by distance, £200–£350 · or collect in Carlisle`, built from `data/settings.json` (`delivery_note`, `delivery_min_gbp`–`delivery_max_gbp`, `address.city`).
12. **Related blog posts** — MANDATORY silo. bsuk-blog-related-posts component.
13. **Newsletter block** — MANDATORY (lower placement; top strip does early capture).
14. **One closing CTA** — MANDATORY. A post renders through `PageShell`, whose `SiteFooterKit` puts the site's `.cta-band` ("Ready to meet the litter?") on every post: that footer band IS the page's closing CTA. In the post body this step is step 11's inquiry card — never a second band.

Every page carries all three special-element slots (TOP/MIDDLE/BOTTOM). MIDDLE module is chosen per page.

**What the post route can render today.** A post is a `.md` entry: `src/content.config.ts` globs only `**/*.md`, and its only image fields are `featured_image` (a path string) and `featured_image_alt`; `src/pages/[...post].astro` passes the kit `Hero` just those two (`image`, `imageAlt`). A post that needs hero dimensions or a `srcset`, a `src/assets/` hero, or any component in its body (every special-element block in §2) first needs `src/content.config.ts` extended (glob `**/*.{md,mdx}` plus the image fields) and `[...post].astro` taught to pass them — a project-5 change, decided on that post's board.

---

### 2. Component Map — Desktop + Mobile Parity

**Blog post components** (the source kit was not ported — source repo only; build each from this list): Hero / 3-Split, Mobile Hero, Jump Links / 3 contexts, Mobile Jump Nav, Buyer's Guide Article, 3-Column Grid, Mobile Blog, Mobile Cards, FAQ (one block, as §1 step 10), Mobile FAQ, Component Library newsletter/inquiry forms, Mobile Newsletter, Mobile Inquiry. **Type Specimen** + **Mobile Type** are the type-scale lock — they enforce identical H1–H6 + body heights across all breakpoints (the breeder's explicit parity requirement). Do not override font sizes in per-page CSS.

**8 special-element blocks — planned, not built.** `src/components/` holds no `bsuk-blog-*` component today. A post that needs one gets it built into `src/components/kit/` on the site tokens when its board is approved, under the name below:
- `bsuk-blog-quick-answer` — TOP special-element; AEO snippet capture.
- `bsuk-blog-callout` — tip + alert variants; Coat SVG icons (never emoji).
- `bsuk-blog-comparison-table` — spec table with "breeder verdict" row.
- `bsuk-blog-breeder-note` — first-person E-E-A-T moat block.
- `bsuk-blog-myth-fact` — Myth-vs-Fact card.
- `bsuk-blog-decision-tree` — AI-extraction-friendly; a MIDDLE option where the gap analysis finds a choice the reader must make.
- `bsuk-blog-related-posts` — silo internal-link cluster to the other posts and the money pages.
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

**Depth:** a competitor scan to identify who owns each topic and where their gap is (the registry is `data/competitors.json`; a registry entry with no report under `docs/research/competitors/` is NOT FETCHED); deep audit of the top 5–6 rankable results in the question file's top-level `competitors` array (the Google and Bing top-5, merged, each with `google_pos` and `bing_pos`). Non-leaders get a light pass.

**Per-page strategy doc** → `docs/superpowers/sessions/YYYY-MM-DD-blog-strategy-<slug>.md`. 17 required fields:
1. Page + primary KW + search-intent split (info/commercial/transactional %)
2. Content-type verdict (competitor posture vs. recommended BlueStaffyUK posture)
3. Top-3 Google competitors (from `data/queries/raw/<slug>/serp_google.json`)
4. Bing top-3 (from `data/queries/raw/<slug>/serp_bing.json`)
5. Registry signal — `data/competitors.json` and `docs/research/gap-matrix-2026-09-23.md` (who ranks/owns + gap)
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

- **Voice:** First-person plural BlueStaffyUK — "we / us / our / here at BlueStaffyUK." Encyclopedic exceptions for taxonomy/cited research only. See `CLAUDE.md` rule 1.
- **Humor:** Style-2 dry/transparent. **≤1 beat per section, gated.** Permitted on commercial/comparison/lighter pages (price, comparison, first-time-owner and where-to-buy posts). **ZERO humour on health pages, and on any medical, legal or licence content.**
- **Length:** **1,800–2,500 words, intent-scaled** — comparison/price leaner; care guides (crate/health/training) fuller. Long-tail 6+ word + conversational/voice query weighting throughout.
- **Content posture:** transactional/commercial/comparison-led. AI-overview-resistant via breeder moat + buyer-advocate framing + strategic CTAs.

---

### 5. Baked-in Gates (non-negotiable, every blog page)

- **Heading Outline Gate** — present full H1→H6 outline (all six levels, sequential, ≥5 H5 AND ≥5 H6) + get explicit approval **BEFORE any page code**. No skipped levels. See `rules/headings.md` (`heading-hierarchy-outline-gate`); the rule moved out of CLAUDE.md on 2026-08-02. For a post, `scripts/final_page_audit.py` exempts the six-level outline, the ≥5 H5 / ≥5 H6 floor and the FAQPage check (`POST_EXEMPT_CHECKS`), so that floor is checked by hand at this gate.
- **Line-icons not emoji** — Coat-style SVGs (`1em`, `currentColor`). Keep only ✔ ✗ ★ text glyphs. Never use 💡 ⚠ or any pictograph emoji.
- **Delivery line on every card** — `UK home delivery by DEFRA-approved transport, priced by distance, £200–£350 · or collect in Carlisle`. Pull from `data/settings.json` (as §1 step 11) and `data/price-matrix.json`. No hardcoded figures.
- **Schema visible + verified in `dist/`** — extend existing JSON-LD, never duplicate. Verify with grep on `dist/` output, not source files.
- **One CTA per page** — the footer's `.cta-band` (`SiteFooterKit`, through `PageShell`) is the closing CTA on every post; the body adds only step 11's inquiry card, never a second band (§1 step 14).
- **NEVER a visible date** — freshness in schema only (`dateModified` / `datePublished`). No "Updated June 2026" visible text anywhere.
- The licence line (LICENCE_CLAIM_PLACEHOLDER) and the statute line (LEGAL_CLAIM_PLACEHOLDER), in prose only, on every page that needs them — and only as recorded in `data/quality/evidence-ledger.json`.
- **Type parity** — identical H1–H6 + body heights desktop/tablet/mobile enforced by Type Specimen + Mobile Type components.
- **Final gate:** `python3 scripts/final_page_audit.py --blog` → must PASS before the post is committed.
- **Commit, never push:** commit after the gates pass, then `python3 scripts/generate_sitemaps.py` (it writes `dist/` only). There is no remote and no deploy until project 6 (`CLAUDE.md` rule 3), and the work belongs on the branch the plan names, never the trunk (`CLAUDE.md` rule 2).

---

### 6. Color Token Note

CSS custom properties are **not auto-imported** in Astro components. In the blog components and any blog page sections, reference the tokens defined in `src/styles/tokens.css` (imported by `src/styles/global.css`); never spell a hex in `src/`. Canonical palette: steel blue `--color-brand` (`#1F3A52`) · brass `--color-cta` (`#C9A227`), whose label is always `--color-cta-ink` (`#14202B`, 6.8:1) · bone `--color-surface` (`#F4F1EA`). Brass is a **fill colour, not a text colour on light**: `--color-cta` on `--color-surface` is 2.1:1 and fails. Small readable text on a light surface is `--color-text` (13.9:1) or `--color-brand` (10.4:1). Never use a stale palette value from the previous site.

---

### 7. Finalization & Polish Playbook (apply to EVERY blog post before "pass")

Bake these into every blog build and rebuild.

**A. Mobile performance.**
- An unused-JavaScript or missing-source-map flag on a `/70de/` script is the Google tag gateway, not anything in `src/` — diagnose it with `.claude/skills/bsuk-perf-gate/SKILL.md` (from project 6, its `--live` run names it). There is no host to configure until project 6.
- **Images:** reuse every `/images/…` file at its original path (`CLAUDE.md` rule 11). The checks are `img_dims`, `img-srcset-within-2x` and `img-sizes-matches-box` (all blocking; the last is hero-only); a new master goes to `src/assets/` and through `astro:assets`, which builds the candidates. Encode with Pillow (`cwebp` is not installed); keep each delivered file under 100KB.
- **The hero is the LCP image.** The kit `Hero` renders it eager with `fetchpriority="high"` and states its own `sizes`. On a post the route passes it only `featured_image` and its alt (§1); `imageSrcset`, `imageWidth` and `imageHeight` reach it only after the route change §1 describes. `BaseLayout` has no hero-preload prop — never add a second `<link rel=preload>` by hand.
- `BaseLayout` loads no analytics tag and no Google Fonts stylesheet today, and a post adds neither by hand. Fonts: see `rules/design.md`.
- **Render-blocking CSS is solved globally:** `astro.config.mjs` sets `build.inlineStylesheets: 'always'`, so ALL CSS is inlined into each page's `<style>` — no external stylesheet, no critical chain. Do NOT re-add `<link rel="stylesheet">` for local CSS, and do NOT revert to 'auto'. Corollary: **anything in ANY component's CSS now appears in EVERY page's HTML** — a single `select-none` Tailwind utility or `user-select: none` rule anywhere in src/ makes `scripts/final_page_audit.py` hard-FAIL the whole site (`no_userselect_none`). Never introduce it.

**B. Author signature / E-E-A-T (every post).** Ship a **visible** byline, not just schema. Pattern: hero byline `Written by Lisa Bright · BlueStaffyUK, Carlisle` (small, `text-xs`, on the hero dek) — no founding year and no licence, which stay unstated until the breeder confirms them (`LICENCE_CLAIM_PLACEHOLDER`) **and** a signed editorial sign-off at the end of the body (`— Written by Lisa Bright, …`). Keep `author: { "@type": "Person", name: "Lisa Bright" }` in the Article schema too. This is an AI-citation + Google-author signal.

**C. Hero eyebrow parity (do not ship `text-sm uppercase`).** Blog hero eyebrow = the homepage style: `font-body text-xs font-medium tracking-wide`, **sentence/Title case (NOT uppercase)**, color **`--color-link-on-inverse`** on the steel `--color-brand` hero. `text-sm uppercase tracking-widest` renders oversized on mobile (no fluid shrink) — the breeder flagged it explicitly.
  - **AA contrast on the steel hero (computed from `data/design/contrast.json`, project 3):** the eyebrow token `--color-link-on-inverse` is 9.1:1 on `--color-surface-inverse` and `--color-text-on-inverse` is 10.4:1, so both clear AA at `text-xs`. `--color-cta` is 4.9:1 there — fine for a large accent, never for `text-xs`. The old "body text on the band needs ≥0.85 alpha" rule does **not** carry over: the steel band is dark enough that `--color-text-on-inverse` at 0.7 alpha still measures 6.0:1. Do not put `--color-cta` on `--color-surface` (2.1:1) at any size.

**D. "Page already shows for a query but has no coverage" → FAQ-first.** From project 6, when search console shows the page ranking for a query the body doesn't answer, **verify existing coverage first**, then add the question to the data — a bank row in `data/faq.json` or a real sourced question in the page's raw files — rebuild the question file (`/bsuk-query-augmentation`), rebuild the page from its picks and fill `covered_by`. Never add an entry to the page's `faqs[]` directly. If it is a real subtopic, add one sequential H3 (never skip a level — `scripts/final_page_audit.py --blog` checks that; for a post it does not check the ≥5 H5 / ≥5 H6 floor, so re-check that by hand against the approved outline, `rules/headings.md`). Watch for intent splits the single-topic post misses: a query about a different situation from the one the post covers is a new H3 (or a new post), not a stretched answer. Always show the placement map for approval before writing.

---

### 8. Competitor Deep-Dive Protocol — Weakness · All Headers · Keyword Types (binding)

The breeder's standing "change of plans": for every post, don't just name competitors — **expose their weakness, extract ALL their headers, and classify their keyword types.** This is field #6 of the 17-field research (§3) upgraded to a required, tool-driven pass. Run it BEFORE the outline gate.

**Sources to pull (in order):** (1) the post's question file, `data/queries/<slug>.json` — its `competitors` array, the Google and Bing top-5 for the primary keyword, merged. Step 3 of `.claude/skills/bsuk-query-augmentation/SKILL.md` is "optional elsewhere" than location pages: run it for every post, or `competitors` stays empty; (2) the competitor registry, `data/competitors.json`, and the intel report under `docs/research/competitors/` for any registry entry that ranks; (3) the gap matrix, `docs/research/gap-matrix-2026-09-23.md`.

**For each of the top 5–6 rankable results, fetch the page the cheapest way that works** — `curl` for the source HTML first, a headless browser if `curl` is blocked, Firecrawl last because every Firecrawl call spends the user's credits (`.claude/skills/bsuk-query-augmentation/SKILL.md`, Step 3) — and extract into a schema: `page_title, meta_description, h1, h2_headings[], h3_headings[], visible_keywords[], has_pricing, trust_or_scam_content_present, content_type`. Forums/FB/Reddit and video = note as UGC/video (not header-outrankable) but record that they rank — a SERP owned by forums is a **wide-open authoritative-guide lane**.

Then produce three tables in the strategy doc (no BSUK worked example exists yet — the first project-5 post writes one):
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
5. **Anti-AI fingerprints** — run `.claude/skills/anti-ai-writing/SKILL.md`. Ban em-dash-as-dramatic-pause overuse, "delve / unlock / leverage / groundbreaking / in today's world / navigate the world of". Human-in-the-loop: AI drafts, breeder facts + the evidence ledger (`data/quality/evidence-ledger.json`) govern.
6. **Interactive engagement (optional, per page)** — an AI-generated 3–5-question comprehension quiz (mid or end) as a self-contained HTML/JS widget in brand hex, whose success message recommends the newsletter or an available puppy. Gate to lighter pages; never on a health, licence or legal page.
7. **Formatting for skimmers** — bold key terms, real HTML tables (not image-of-table) for data, clean bullet/step lists for snippet + AI-chunk capture.

### 10. Visual Production Pipeline + Image-Placeholder Workflow

**Placeholder-first (default).** Build the page with image constants + `<figure>` slots wired to **exact final paths**, but treat every generated asset as a PLACEHOLDER until the breeder confirms design/size. Existing photos are reused at their `/images/…` URLs (`CLAUDE.md` rule 11); a new photo or infographic the breeder supplies becomes a new master under `src/assets/`, served through `astro:assets` (§7 A). A manifest in the strategy doc lists every image the post uses — its `/images/…` URL or its `src/assets/` path. **Do NOT commit while any referenced image 404s** — build, then confirm every referenced file is in `dist/`.

**Asset categories & sizes** (art direction from `rules/images.md` + `rules/design.md`; palette steel blue `#1F3A52` (= `--color-brand`), brass `#C9A227` (= `--color-cta`), bone `#F4F1EA` (= `--color-surface`); type Fraunces headings, Source Sans 3 body; line icons, no emoji/logos/other species/visible price overlays):
| Category | Per post | Source | On-page render |
|---|---|---|---|
| Hero (photoreal editorial) | 1 | an existing `/images/…` photo, as the post's `featured_image` (a `src/assets/` hero needs the §1 route change first) | the kit `Hero` (§7 A) |
| Section images — photos and infographics | 3–5 | an existing `/images/…` file, or a new master in `src/assets/` | the uniform in-body box in `rules/images.md` |
| Portrait infographic / checklist | as needed | a new master in `src/assets/` | a centred card whose `sizes` states its rendered width |
| Real OG / trust photo | 1–2 | an existing `/images/…` file | plain `<img>` in the long visual-less H2/H3; real brand shot for E-E-A-T |

Box sizes, crop and encode quality: `rules/images.md`. The checks are `img_dims`, `img-srcset-within-2x` and `img-sizes-matches-box` (all blocking; the last is hero-only).

**The encode → wire → commit pipeline (copy this):**
1. **Encode with Pillow** (`cwebp` NOT installed): flatten RGBA onto bone `#F4F1EA` (= `--color-surface`) for infographics / white for photos; crop, size and quality per `rules/images.md`. A new master goes to `src/assets/` and `astro:assets` builds its candidates; an existing `/images/…` file is never re-encoded, renamed or replaced (`CLAUDE.md` rule 11).
2. **Fix CLS** — set each `<img width/height>` to the file's **native ratio** (don't trust the placeholder's guessed dims). Verify in preview that displayed ratio ≈ native ratio (no stretch).
3. **The hero is the kit `Hero`**, fed the post's `featured_image` and `featured_image_alt`; hero dimensions, a `srcset` or a `src/assets/` hero need the §1 route change first (§7 A).
4. **Add a visual to every long visual-less H2/H3** — the breeder's rule: tall/important sections must carry an image; weave real OG photos into them.
5. **Rebuild** (`npx astro build`) → confirm every referenced `.webp` exists in `dist/` (grep the built HTML, fail on any missing) → **`python3 scripts/final_page_audit.py --blog`** must PASS → preview-verify images 200 + ratios → then commit.

### 11. Universal Special-Element Boxes (reuse on every page)

Every page carries the 3 slot boxes (TOP/MIDDLE/BOTTOM, §1) plus draws from this catalog — all token-themed Astro components, Coat line-icons only (never 💡/⚠/emoji):
1. **Quick-Answer / TL;DR** → `bsuk-blog-quick-answer` (TOP, AEO).
2. **Breeder Note** (first-person moat) → `bsuk-blog-breeder-note`.
3. **Expert Tip** → `bsuk-blog-callout` variant `tip`.
4. **Mistake / Warning Alert** → `bsuk-blog-callout` variant `alert`.
5. **Myth vs Fact** → `bsuk-blog-myth-fact`.
6. **Decision Tree** (AI-extraction-friendly) → `bsuk-blog-decision-tree` (a MIDDLE option).
7. **Comparison / spec table** (with "breeder verdict" row) → `bsuk-blog-comparison-table`.
8. **FAQ accordion** (visible + FAQPage schema) → page `faqs[]` array, filled with exactly the question file's picks (one block; the three-block split is location-only), each question an H3.
Plus `bsuk-blog-related-posts` (bottom silo) and `bsuk-blog-sticky-cta` (mobile).

### 12. Toolbelt & BSUK Context (know these before building any post)

- **Competitor intel:** the question file and its fetch order (`.claude/skills/bsuk-query-augmentation/SKILL.md`, Step 3: `curl`, then a browser, Firecrawl last because it spends credits), the registry `data/competitors.json`, and `@bsuk-competitor-intel` for a registry entry with no report. A 403 to `curl` (e.g. `thekennelclub.org.uk`) is a bot block, not a dead page.
- **Images:** Pillow (`cwebp` is not installed), sizes and quality per `rules/images.md`; new masters in `src/assets/` through `astro:assets`, existing files reused at their URLs (`CLAUDE.md` rule 11). Image prompts: `.claude/skills/image-prompt-generator/SKILL.md`; alt text and filenames: `.claude/skills/image-metadata/SKILL.md`.
- **Audit and commit:** `python3 scripts/final_page_audit.py --blog` (no skipped levels; for a post it exempts the six-level outline and the ≥5 H5 / ≥5 H6 floor — `POST_EXEMPT_CHECKS` — which stay manual Heading Outline Gate items, `rules/headings.md`) → `python3 scripts/generate_sitemaps.py` (writes `dist/` only) → commit. No push and no deploy until project 6.
- **Data (never hardcode):** `data/settings.json` (the £200–£350 delivery band, the £500 deposit), `data/price-matrix.json` (£1,500 / £1,700), `data/puppies.json` (the available pups). The competitor registry is `data/competitors.json`. The external-link library is `docs/reference/external-link-library.md`: every outside link a post carries is a row there, verified 200 before it is added (a board naming any other URL is refused).
- **No push, no deploy:** there is **no push and no deploy until project 6** — this repo has no remote. Never add one, and never write a credential anywhere. Build on the branch the plan names (`CLAUDE.md` rule 2), never on the trunk.
- **Cannibalization guard:** blog posts LINK OUT to money/interior pages (for-sale hub, price, scam) — never re-teach or re-list what a money page owns.

### 13. Fill-in Placeholders (set these before running the skill)

Copy this block into the session brief and fill it before Sprint 0.5:
```
{{TARGET_BLOG_POST}}      e.g. /how-to-choose-the-right-blue-staffy-puppy-for-your-family/   ← the post to work on (/<slug>/)
{{PRIMARY_KEYWORD}}       e.g. "how to choose the right Blue Staffy puppy"
{{SESSION DATE}}          e.g. 2026-10-01
{{QUESTION_FILE}}         data/queries/<slug>.json   ← from /bsuk-query-augmentation
{{IMAGE_MASTERS}}         src/assets/…   ← new masters only; existing /images/… files are reused at their URLs
{{FRAMEWORK}}             PAS / EBP / QAB / BAB / PDB (breeder-selected, field 17 of §3)
{{ANGLE}}                 breeder-selected winning angle + why
{{HUMOR}}                 on (commercial/comparison) | OFF (health, licence and legal pages)
{{IMAGE_MANIFEST}}        every image the post uses — its /images/… URL or src/assets/ path — and its native size (§10)
```
**Scope in project 5:** two posts, named by the project-5 plan; one post per session, each through its own board.

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

