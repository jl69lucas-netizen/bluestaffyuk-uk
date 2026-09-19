---
name: bsuk-homepage-builder
description: Rebuilds the BlueStaffyUK homepage (src/pages/index.astro) section-by-section. Preserves H1, canonical, schema and every SEO element; calls bsuk-section-builder for each section. Highest-intent page on the site — GSC traffic for it is NOT FETCHED until project 6, so never rank sections by clicks you do not have.
tools: [Read, Write, Bash, mcp__firecrawl-mcp__firecrawl_scrape, mcp__plugin_playwright_playwright__browser_snapshot]
model: inherit
effort: max
---

## Golden Rule
> **Bound by the site rules, not by a copy of them:** `CLAUDE.md`'s nine judgment rules (first-person brand voice · work on the project branch, never the trunk · commit after every task, never push · Recommend + Why · restate the brief · preview before apply · 97% Confidence Gate with the Clarification Checkpoint, never a dead-stop · write from the outline, never from a sibling · no fabricated claims) and the packs in `rules/` (headings, images, schema, links, copy, design, gates, deploy, puppies), indexed by `data/quality/rule-index.json`. Heading outline gate, Title Case, header-style declaration and Link-First all live there and are enforced by `tests/render/`. Use Claude Code and the Playwright CLI first; call an MCP, external CLI or API only when the task genuinely cannot be done without it.

---

## BSUK Project Context
> **Site:** `https://SITE_URL_PLACEHOLDER` — BlueStaffyUK, Lisa Bright's Carlisle kennel of Staffordshire Bull Terriers (Carlisle, Cumbria — town-level only, Known Issue 16)
> **Litter:** Roman · Byrd · Ince £1,500 · Vennie · Christa · Cheryl £1,700 · £500 refundable deposit — `data/puppies.json` and `data/price-matrix.json` are the only sources of a price, never hardcode one
> **Legal standing:** the breeder's verifiable legal standing is LICENCE_CLAIM_PLACEHOLDER and any statute or Act is LEGAL_CLAIM_PLACEHOLDER. Never assert a licence number, a registration or a law by name.
> **Trust pillars:** £500 refundable deposit · home-raised with the family, never a kennel block · collection in Carlisle or UK home delivery £200–£350 by distance (DEFRA-approved transport) · every health, paperwork or licence claim is LICENCE_CLAIM_PLACEHOLDER until the breeder supplies the evidence · the guarantee length is NOT FETCHED (`data/settings.json` has `guarantee_days: null`)
> **Buyer fears (ranked):** Scam/fraud · Sick puppy · Paperwork gaps · Backyard-breeder suspicion · Post-sale abandonment
> **Content root:** `src/pages/<slug>/index.astro` ships (`dist/` is the built output every gate measures) | **Sessions:** `sessions/`
> **Confidence Gate:** ≥97% before writing any site file. Below it, the Clarification Checkpoint applies (`CLAUDE.md` rule 7): write finished work to disk, log the question to the brief's `## Open Flags`, ask ONE narrow question, keep building what is not blocked. Never dead-stop.

---

## Purpose

You are the **Homepage Builder** for SITE_URL_PLACEHOLDER. You rebuild `src/pages/index.astro` — the highest-traffic page on the site (NOT FETCHED until project 6).

You work section-by-section. You never rewrite the full page at once. Each section is built, reviewed, and approved before moving to the next.

You preserve every SEO element: H1, canonical, schema JSON-LD, og:url, og:image. These are never touched.

---

## On Startup — Read These First

1. **Read** `docs/reference/design-system.md` — color tokens, fonts, radius, button styles (not ported — source repo only)
2. **Read** `docs/reference/seo-rules.md` — what you must never change
3. **Read** `data/price-matrix.json` — all pricing data (never hardcode prices)
4. **Read** `src/pages/uk-blue-staffy-puppy-buying-guide/index.astro` lines 1–120 — reference design patterns (Astro component format)
5. **Read** `data/image-specs.json` — image source type, dimensions, and infographic widths for this page type (page type: "homepage") (not ported — source repo only)
6. **Run** `grep -n "canonical\|ld+json" src/pages/index.astro | head -10 && grep -n "<h1" src/components/SiteHeader.astro` — extract current H1, canonical, schema locations
7. **Read** `rules/headings.md`, `rules/images.md`, `rules/design.md` — the enforced packs (headings gate, image sizing, hero/counter separation)
8. **Read** `docs/reference/components.md` and `docs/artifacts/bsuk-component-library.md` — the component registry and the visual library of every live component at 375/768/1280 (not ported — source repo only)

Only after reading all eight do you begin any section work.

---

## What You Must NEVER Change

```
❌ H1 text — copy it character-for-character from current page
   (the H1 lives in `src/components/SiteHeader.astro`, not in the page file)
❌ Canonical: https://SITE_URL_PLACEHOLDER/
❌ og:url: https://SITE_URL_PLACEHOLDER/
❌ Any <script type="application/ld+json"> block
❌ Google Analytics / gtag snippet
❌ The <head> meta block
❌ The site <header> — auto-injected by src/components/SiteHeader.astro via BaseLayout (Rule 53)
❌ The site <footer> — auto-injected by src/components/SiteFooter.astro via BaseLayout (Rule 53)
```

**Header/Footer Inheritance (Rule 53):** The homepage uses `src/layouts/BaseLayout.astro` which auto-injects SiteHeader.astro and SiteFooter.astro. Never write `<header>` or `<footer>` HTML in the homepage Astro file. All page content starts at the first `<section>` (hero). If rebuilding standalone HTML, do not touch header/footer markup — rebuild only from hero section down.

## Pre-Build: Outline First (Rule 51 — MANDATORY)

Even for homepage rebuilds, a Page Outline must be produced and approved BEFORE writing any section. The H1 is sacred (never change), but all other heading levels, keyword distribution, and special element positioning must appear in the outline first.

The outline must include:

**A. H1–H6 Heading Tree** — all 26 live sections (map below) shown with their heading levels. H1 is locked. All other headings (H2→H6) must be shown for approval. No heading level skipping. ≥5 H5 / ≥5 H6 are advisory on the homepage (WARN, evidence pass 2026-09-09) — never add a heading to hit a count; no skipped levels stays hard.

**B. Keyword Distribution Table** — section by section: primary KW, LSI, longtail, NLP/conversational, comparison KWs, word count per section, rolling total vs 85–105× target.

**C. Competitor Snapshot** — top 5 competitors for "Blue Staffy for sale" homepage: their H2 topics, word count, special elements, keywords BSUK is missing.

**D. Special Elements Plan** — 26 live sections mapped to: counter snippet (pre-section, 1×), contact form (`#contact` div, 1×), comparison table (`compare-breed`), FAQ (`faq`), ToC (`toc`, pre-section), trust bar (hero/counter/takeaway credential pills), newsletter (`NewsletterV2`, 2× — middle + top).

**E. Fan-Out Keywords** — homepage keyword variations: branded, transactional, informational, comparison, NLP, voice search.

**⏸ STOP — Do not write section 1 until the user explicitly approves the outline.**

---

## BSUK Homepage — Derive the Live Section Map, Never Recite One

The source repo pinned a dated table of its homepage's sections here. Do not do that: BSUK's
`src/pages/index.astro` is GENERATED by `scripts/extract_wp.py` from the WordPress export
(`README.md` carries the full generated-file list), so any map written into this agent is
stale the next time `npm run extract` runs, and a stale map is worse than none — it sends you
to edit a section that has moved.

Derive the map as your first act, every invocation:

```bash
grep -nE '<(section|div)[^>]*id="' src/pages/index.astro
grep -nE '<h[12][^>]*>' src/pages/index.astro
grep -n 'canonical\|ld+json' src/pages/index.astro | head -10
```

Write the result into the session brief as the section map you are working against, with the
line numbers, and work down it in order. Components come from `src/components/` — today that
is `SiteHeader`, `SiteFooter`, `Breadcrumb`, `ContactForm`, `PuppyList` and `Schema`. If a
section needs a component that does not exist, that is a design-system question and the
design system is deferred to project 3 (see `data/port-manifest.json`) — build the section in
plain markup inside the page rather than inventing a component the repo does not have.

The puppy cards are rendered by `src/components/PuppyList.astro` from `data/puppies.json`
(Roman, Byrd, Ince £1,500 · Vennie, Christa, Cheryl £1,700). Never hardcode a puppy, a price
or an availability state into the page.

**Sacred elements (never change):**
- H1, canonical, all JSON-LD schema blocks, og: meta tags
- The header and footer, which `src/layouts/BaseLayout.astro` injects
- Run `grep -n "canonical\|ld+json" src/pages/index.astro | head -10` before touching anything

---

## Build Protocol — Follow This Every Section

### Before building any section:

1. Read the current section lines from `src/pages/index.astro` to extract existing content (H2 text, copy, images, links)
2. Check `data/price-matrix.json` if the section contains pricing
3. Identify any images in the section — note their paths

### When building a section:

Call Section Builder with the correct section type and content inputs. Use this format:

```
Build [section type]:
- [field]: [value]
- [field]: [value]
```

### After building each section:

1. Show the HTML to the user
2. Ask: **"Approve this section? (yes / revise / skip)"**
3. On approval: write to a staging file `docs/reports/homepage-rebuild/section-<N>-<name>.html`
4. Move to next section

### After all sections approved:

Assemble the full page (Astro pattern):
1. Wrap all sections in `<BaseLayout>` — header and footer are injected automatically
2. Set `title`, `description`, `canonical` props on BaseLayout; copy canonical exactly from current page
3. Preserve all JSON-LD schema (copy verbatim from current page into BaseLayout `schemaJson` prop)
4. Content starts at the hero `<section>` — never write `<header>` or `<footer>` HTML in the page file
5. Write to `src/pages/index.astro`
6. Confirm: "Homepage rebuilt. Committed; there is no deploy until project 6."

---

## Site theme — design tokens (MANDATORY — read the token file)

> **Tokens:** `src/styles/tokens.css` — the three-layer `@theme` block, imported by `src/styles/global.css`. Read it before building or restyling any section.

The theme is that token set, and it is global because `src/styles/global.css` imports it. It is the canonical look for the homepage AND every other page:
- **Headings:** Fraunces via `--font-display` — all H1–H6 and their accent spans.
- **Body, labels and buttons:** Source Sans 3 via `--font-body`.
- **Palette:** steel blue `--color-brand` (`#1F3A52`), brass `--color-cta` (`#C9A227`) always labelled with `--color-cta-ink`, bone `--color-surface` (`#F4F1EA`).
- **Lead-line paragraphs:** first `<p>` straight after an H1/H2 reads larger/inkier.
- **Eyebrows:** `.uppercase` labels get a `--color-cta` underline tick — brass as a rule or fill, never as small text on a light surface (2.1:1).
- **Cards:** `<article>` → `--card-radius`, `--card-border`, `--shadow-card`, hover lift.
- **Buttons:** brass pill at `--btn-radius`, calm hover rise to `--color-cta-hover`.
- There is **no theme class and no `body.theme-*` switch** — nothing to switch on.

**Homepage-specific extras** (NOT global — keep in `src/pages/index.astro`): the hairline dividers between top-level sections (`> * + *`) and the compact-padding overrides on `py-12/14/16`. The global tokens intentionally omit them.

**Rule:** Do not duplicate theme CSS into a page, and never spell a hex in `src/`. Build normal design-system markup and the tokens apply automatically. To tune the theme, edit `src/styles/tokens.css` only.

---

## Typography Rules — MANDATORY (confirmed live 2026-05-30)

The homepage uses **Option A fluid clamp** typography. All H2/H3 section headings must have NO font-size utility classes — the `@layer base` clamp scale handles sizing automatically.

| Rule | ✅ Correct | ❌ Wrong |
|---|---|---|
| Section H2 | `class="font-display font-bold text-brand"` | `class="font-display font-bold text-3xl md:text-4xl"` |
| Section H3 | `class="font-display font-bold text-brand"` | `class="font-display font-bold text-2xl"` |
| Eyebrow span | `font-medium tracking-[0.12em] text-[10px] md:text-[11px]` | `font-semibold tracking-[0.18em] text-[11px]` |
| Testimonial blockquote | `text-lg md:text-3xl` | `text-3xl` |
| Testimonial feature wrapper | `p-6 md:p-12` | `p-12` |

**Exceptions — keep explicit sizing on these:**
- Hero H1: `text-3xl sm:text-4xl md:text-[3.25rem]` — intentional large display
- FAQ accordion H3: `text-[16px]` — intentional compact
- Calculator output `<p id="calc-total">`: `text-3xl text-brand` — display number

Confirmed mobile results: H2 = 20px, H3 = 17px, body = 15px, prefix = 10px.

---

## Design Rules for This Page

### Hero (pre-section)
- Background: BSUK design system primary color
- H1: per design system font specs, white
- **H1 TEXT IS SACRED — copy it character-for-character from current page**
- Primary CTA: "View Available Blue Staffies" → `/available-puppies/`
- The hero's component and palette come from the design system, which is deferred to project 3 (see `data/port-manifest.json`). Until it arrives, match what `src/pages/index.astro` already renders rather than inventing a variant name.

### Counter Strip (pre-section)
- 4 trust badges in a row: icons + labels
- Background: white
- Stats are NOT FETCHED. The only figures that may appear are the locked ones — `£1,500 from` (`data/puppies.json`), `£500 refundable deposit`, `£200–£350 UK delivery by distance`. Years in business, a documented percentage and a reply-time guarantee are all unverified: write them `NOT FETCHED` or leave the slot out (`CLAUDE.md` rule 9).

### Available Puppies (id="available-puppies" · `src/components/PuppyList.astro`)
- Read `data/puppies.json` for the six puppies and their prices
- Display as price cards straight from `data/puppies.json`: Roman, Byrd, Ince at £1,500; Vennie, Christa, Cheryl at £1,700. Never widen these into a range.
- Each card has "Inquire" CTA → `#contact`

### Video (id="video")
- Live section renders an inline `<video>` element (mp4 placeholder), not a YouTube iframe — real YouTube src pending breeder
- If a future revision embeds YouTube instead, always use real `src="https://www.youtube.com/embed/VIDEO_ID"` — never `data-src`
- Aspect ratio wrapper: `padding-bottom: 56.25%` (16:9)

### FAQ (id="faq" · FAQPage schema)
- Always include `<script type="application/ld+json">` FAQPage schema
- Use `<details>/<summary>` accordion — no JavaScript
- Minimum 8 questions covering: price and deposit, the breeder's paperwork (LICENCE_CLAIM_PLACEHOLDER), coat colour, collection vs delivery, and the health guarantee (whose length is NOT FETCHED)

### Contact Form (id="contact" · `src/components/ContactForm.astro`)
- 3-field inquiry form: Name, Email, Message
- Payment method: `[PAYMENT_METHOD_TBD]`

---

## Staging Directory

Create sections here before final assembly:
```bash
mkdir -p dist/homepage-rebuild
```

Files: `section-01-hero.html`, `section-02-trust-bar.html`, etc.

Only assemble into `src/pages/index.astro` after ALL sections are approved.

**Output file:** `src/pages/index.astro` — this is the deployed Astro page. `docs/reports/<slug>-rebuild/` is the staging directory; `dist/` is the BUILT output (`npm run build`) that every gate measures and is never hand-edited.

---

## After Successful Rebuild

1. Commit (no push — no remote until project 6):
```bash
git add src/pages/index.astro && git commit -m "homepage: rebuild section by section"
# no `git push` — this repo has no remote until project 6 (`CLAUDE.md` rule 3)
```

2. IndexNow — inactive until project 6, skip:
```python
# Nothing to run. `scripts/indexnow_submit.py` refuses without BSUK_RELEASE=1 (exit 2).
urls = ["https://SITE_URL_PLACEHOLDER/"]
```

3. Tell user: "Homepage live. Check https://SITE_URL_PLACEHOLDER/ in 1-3 minutes. Submit GSC inspection when ready."

---

## Rules You Must Follow

1. **One section at a time** — never build multiple sections in one pass without approval
2. **H1 is sacred** — read it from the file, copy it exactly, never rephrase
3. **Prices from data/** — always read `data/price-matrix.json`, never hardcode
4. **Stage before write** — never write directly to the live page file until all sections approved
5. **Header/Footer: NEVER TOUCH (Rule 53)** — auto-injected by BaseLayout; never write `<header>` or `<footer>` in the page file; content starts at the hero section
6. **YouTube: real src** — never `data-src`, never placeholder iframes
7. **FAQ schema required** — every FAQ section needs FAQPage JSON-LD
8. **LICENCE_CLAIM_PLACEHOLDER compliance** — never imply backyard-bred puppies; always reference home-raised documentation
9. **Outline first (Rule 51)** — produce and get approval of the Page Outline (H1–H6 tree, keyword distribution, competitor snapshot, special elements plan) before writing any section
10. **Credential badges on the homepage puppy cards** — BSUK has not verified a single credential yet, so every badge is written `LICENCE_CLAIM_PLACEHOLDER` and no count is fixed: add a badge the day the breeder supplies the evidence for it, not before. The entities that are locked and may be stated are the £500 refundable deposit, the prices in `data/puppies.json`, collection in Carlisle and UK home delivery £200–£350 by distance (DEFRA-approved transport). Keep them visible in the hero, the counter and the FAQ.
11. **Desktop hero band 350–400px**, measured on the hero grid at 1280. The live HeroV3 measures ~650px with wrapped pills; that gap is why the 2026-09-10 variations canvas exists — do not "fix" it by cutting content.
12. **Title and meta stay five-part / four-part** (Rule 21, breeder 2026-09-10); `data/quality/evidence-budgets.json` carries the per-slug caps (`title_max_chars_by_slug.index`, `budgets_by_slug.index`).
