# SEO Rules — Master Ruleset (57 Rules)
**All agents and skills must read this file before creating or modifying any page.**
Re-based from the source repo's ruleset in project 2, Task 13. Two blocks were **deleted
rather than translated**: the source's species-specific extended-rules section
(Rules 44–50b, a wildlife compliance regime with no Staffordshire Bull Terrier analogue —
inventing one would be a fabricated claim) and its dated `Quick Reference — GSC Priority
Pages` table (the source repo's own Search Console numbers; BSUK's GSC property is
unverified and its data is **NOT FETCHED**). The numbering below is therefore 1–43 and
51–64 with no gaps filled in: **57 rules.** `docs/reference/quick-start.md` and `CLAUDE.md`
both state 57, and all three must be changed together.

---

## Category A — Brand & Identity

**Rule 1 — Brand Name**
Use **"BlueStaffyUK"** as the brand name everywhere — page copy, footer, schema, agent
references. Never use the bare domain as a brand name. `BlueStaffyUK – Carlisle` is the
long form. Organization schema matches.

**Rule 2 — Breeder Identity**
The breeder is **Lisa Bright**, Carlisle, Cumbria. Content uses the
first-person breeder voice — *we / us / our* — not "the breeder" or third-person
directory language.

---

## Category B — Never-Break Technical Rules

**Rule 3 — H1 Text**
NEVER change H1 text without explicit breeder approval. H1 is an SEO anchor.

**Rule 4 — Canonical href**
MUST be absolute: `https://SITE_URL_PLACEHOLDER/slug/` — never relative. A relative
canonical makes Google resolve every page to `/` and they disappear from search. The host
is a placeholder until project 6 registers the domain.

**Rule 5 — Schema JSON-LD**
NEVER remove or modify an existing schema JSON-LD block. Preserve verbatim; only add.

**Rule 6 — Open Graph Tags**
`og:url`, `og:image`, `og:title` and `canonical` MUST be absolute URLs. Never relative.

**Rule 7 — Licence and Statute Language**
Breeder-licence and animal-welfare-statute claims are **not established**. Write them as
`LICENCE_CLAIM_PLACEHOLDER` and `LEGAL_CLAIM_PLACEHOLDER` and let
`scripts/placeholder_check.py` hold them until Lisa Bright confirms them. Never assert a
licence number, an inspection rating, or a statute the repo has not seen.

**Rule 8 — Image Source Paths**
NEVER use base64 data URIs. Always a real `src="/images/..."`. Base64 bloats HTML, kills
page speed and breaks image SEO.

**Rule 9 — Sitemap URLs**
Every `<loc>` is absolute. Exclude thank-you and admin routes.
`python3 scripts/generate_sitemaps.py` writes them; `python3 scripts/sitemap_check.py`
proves them.

**Rule 10 — Post-Deploy Checklist — inactive until project 6**
There is no remote and no live site. When project 6 activates deploy: submit changed URLs
via `scripts/indexnow_submit.py`, which exits 2 without `BSUK_RELEASE=1`; read
the key from `.env` per `docs/reference/credentials.md` and never from a file in the repo,
then check Search Console for crawl errors within 24 hours.

---

## Category C — Pre-Build Workflow (Mandatory)

**Rule 11 — Competitor Analysis Required Before Every Page**
Before building any page: research the top 5–10 competitors ranking for the primary
keyword. Capture their H1–H6 patterns, exact keyword density and usage count,
related/variation/LSI keywords, image and video counts, section count and structure, and
words per section. Then run a fan-out keyword query, build a section-by-section keyword
distribution, and produce a page outline with topic clusters. **No page ships without this
step plus breeder approval.**

**Rule 12 — User Approval Gate**
No page goes live without explicit breeder approval. Present the outline and keyword plan
after competitor analysis; wait for "approved" before writing content.

**Rule 13 — Section-by-Section Execution Workflow**
Never write a full page at once:
1. Competitor analysis only → STOP
2. Approved → Sections 1–5 → STOP
3. "Continue" → Sections 6–10 → STOP
4. Repeat to the end. Never skip, never merge, never continue unasked.

---

## Category D — Keyword Strategy

**Rule 14 — Primary Transactional Keyword**
`"blue staffy puppies for sale [UK city]"` — in the H1, the title tag and the URL slug of
every location page. The 28 cities are in `data/locations.json` and nowhere else.

**Rule 15 — Primary Brand Keyword**
`"BlueStaffyUK blue staffy puppies"` and `"blue staffy for sale UK"`. Search Console
baselines are **NOT FETCHED** — the property is unverified since the domain expired, so no
CTR or position figure may be quoted anywhere until project 6.

**Rule 16 — Breeding Niche Keywords**
`"blue staffordshire bull terrier breeder UK"` — the near-brand cluster that needs its own
hub page.

**Rule 17 — Informational Keywords**
Male vs female, diet and feeding, care guides, temperament, training, health screening.
Top-of-funnel impression volume; every informational page needs CTR-optimised meta.

**Rule 18 — Keyword Frequency Table (Per Page)**

| Keyword Type | Cap (no more than) | Note |
|---|---|---|
| Primary keyword (exact) | 30–35× | 1–2% density; natural, not stuffed |
| LSI keywords | 20–25× | Synonyms and related terms |
| Long-tail keywords | 15–20× | In headers and paragraphs, conversational |
| Branded keywords (BlueStaffyUK, Lisa Bright, Carlisle) | 10–15× | Throughout |
| Conversational search queries | 23× | Headers and subheaders, voice search |
| Comparison keywords (blue vs black Staffy, Staffy vs Bull Terrier) | 5–8× | |
| Solution keywords | 5–10× | |
| Related keywords | 10–15× | |
| Transactional keywords | 15× | Buy, for sale, available, pricing |
| **TOTAL** | **≤105 (no minimum)** | |

Each row caps that keyword type; the page total is capped at 105. The rows are not summed and never a number to reach — a short, focused page that uses far fewer is correct. Where a row shows a range, the upper figure is the cap.

The authority for this table is `.claude/agents/bsuk-keyword-verifier.md`, which judges the
count; this block follows it (`tests/py/test_rule18_frequency.py`):
- There is **no floor**. A page is never "under-optimized" by count (retired 2026-09-09: the
  floor manufactured the repetition the evidence pass now fails). The per-type counts above
  are ceilings to stay under, never numbers to reach.
- A full page with >110 total keyword mentions is flagged **OVER-STUFFED**; trust-concept
  terms additionally answer to `data/quality/evidence-budgets.json` via
  `scripts/evidence_audit.py`.
- Short pages (<1,500 words): scale proportionally; do not apply full-page thresholds.

**Rule 19 — Keyword Density Per Section**
Primary keyword 0.8–1.2% per section. LSI distributed naturally, never force-inserted.

**Rule 20 — Negative Keyword Counter-Positioning**
Every product or availability page addresses at least one:
- `"blue staffy puppy scam"` → counter with what we document and show: a litter raised in our family home, never in kennels (`data/faq.json` `about-home-raised`), and the paperwork that goes home with it (`whyus-paperwork`)
- `"cheap blue staffy puppies"` → position on health screening and aftercare, not price
- `"blue staffy puppy farm"` → counter with collection-in-Carlisle and seeing the litter

Each counter states only what the repo can back. Nothing here licenses a welfare or
licensing claim — see Rule 7.

---

## Category E — Meta Titles & Descriptions

> **⚠️ CANONICAL META FORMAT — THE ONLY SOURCE OF TRUTH.** Every page uses Rule 21's
> one-clause title. NEVER ship a generic short title. `.claude/agents/bsuk-meta-description-agent.md`
> must mirror these exactly.

**Rule 21 — Meta FORMAT 1 (Standard Long Title)**
Structure: `[Primary Keyword] + [Number where authentic] + [Power Word] + [Long-tail
conversational query] + BlueStaffyUK`
1. **Begin with the primary keyword** (e.g. `Blue Staffy Puppies for Sale`).
2. **Add a number** only where it is true — never invent one.
3. **Include a power word** — Trusted, Healthy, Home-Reared, Hand-Socialised.
4. **Insert a long-tail conversational query** — `blue staffy breeder near me with puppies
   available now`.
5. **End with the brand** — `BlueStaffyUK` (or `BlueStaffyUK – Carlisle`).
6. One clause, no pipe separators.
- **Title cap: ≤ 70 characters, one clause.**
- **Description cap: ≤ 160 characters.**

**Rule 22 — Meta FORMAT 2 (4-Part Long Title + Tone System) — RETIRED. Kept for the record only.**
Superseded by Rule 21 before the port. Do not build to it. The tone markers 🔴 urgency /
🆚 comparison / 💰 transactional / 🛡️ trust survive as **planning labels only** — never
rendered into a title or description tag.

**Rule 23 — Meta Description**
- ≤ 160 characters, conversational, benefit-driven, one sentence flow.
- Must carry: primary keyword + a long-tail or LSI variation + a trust signal + a CTA.
- Emphasise what is locked: home-reared in Carlisle, UK delivery £200–£350 by distance via
  DEFRA-approved transport or collection in Carlisle, £500 refundable deposit.
- Never emphasise a licence, a statute or a review count — none of those is established.
  The guarantee's length (two years) is emphasised only as `guarantee_days` and
  `guarantee_label` in `data/settings.json` word it.

**Rule 24 — Uniqueness**
Unique title and description on every page. Duplicates are a cannibalisation signal.
`python3 scripts/dup_content_audit.py` is the gate.

**Rule 25 — Branded Search Optimization**
Optimise for `"BlueStaffyUK reviews"`, `"BlueStaffyUK Carlisle pricing"` and
`"BlueStaffyUK vs [competitor]"`. No historical branded-search data exists here; treat
these as targets, not as measured demand.

---

## Category F — Page Structure

**Rule 26 — Section Count**
No default. A page's body-section count is `section_target.total` in its question file
(`data/queries/<slug>.json`): the competitors' highest real (cleaned) H2 count + 3, never fewer
than 9 (`docs/reference/location-page-template.md`, "Section count").

**Rule 27 — Word Count (Dynamic)**
The competitors' median word count, from the competitor scan: `word_target.median` in the
question file (`data/queries/<slug>.json`), measured by `query_augment.py --competitor-metrics`
from the saved competitor HTML. Only prose pages count: listings, blocked pages and same-site
repeats are excluded and named with a reason. `NOT FETCHED — <barrier>` (its `status`) until
that scan exists, or when no competitor page is prose. Never fix a word count before running competitor research, and never pick a number
first and write to fill it.

**Rule 28 — Header Count Targets**
- H1: exactly **1** per page (hero only)
- H2: **25–35** · H3: **40–50** · H4: **10–20**
- H5: **minimum 5** — deep LSI / technical authority terms
- H6: **minimum 5** — voice-search phrasing, breeder notes, citations
- All six levels are required on every full-length page. "H4/H5/H6 as needed" is BANNED.
  Shipping 1 H6 or 4 H5 is an automatic FAIL. See `rules/headings.md` for the pack that
  holds this and for the home/location WARN exception.

**Rule 29 — Table of Contents**
Required over 1,500 words, after the hero and key-takeaways block, anchored to every
major section.

**Rule 30 — Jump Links (Anchor Links)**
Every section carries an anchor id; navigation flows hero → final CTA. Landing behaviour
is checked by `tests/render/checks/nav.ts`.

**Rule 31 — Counter Snippets (After Hero)**
Four counters immediately after the hero, under four words each, each starting with a
number or percentage, each stating something BlueStaffyUK can back:
`£500 Refundable Deposit` / `12–14 Year Lifespan` / `28 UK Cities Covered` /
`Home-Reared in Carlisle`. A counter that asserts a licence, an award or a review count is
a defect, not a variation.

**Rule 32 — Contact Form Placement (3× Per Page)**
The inquiry form appears at least three times: after the hero, mid-page after the trust
section, and after the FAQ. `src/components/ContactForm.astro` is the only form; its
endpoint is the `PUBLIC_FORMSPREE_ID` env key (`docs/reference/credentials.md`), and
`scripts/form_contract_audit.py` plus `tests/render/checks/form.ts` are its gates.

**Rule 33 — Formatting Standards**
Checkmarks for feature lists · **bold** for key facts and prices · bullets for benefits ·
anchor ids on every section · breadcrumbs on interior pages
(`src/components/Breadcrumb.astro`). AggregateRating markup is **not** permitted: no
review corpus has been established.

---

## Category G — Content & Writing

**Rule 34 — Writing DO Rules**
- ✅ Natural, conversational language
- ✅ Answer questions people actually search
- ✅ Emotional connection and empathy — a puppy is a 12–14 year commitment
- ✅ Transparency about pricing, deposit, delivery and process
- ✅ Human, warm, knowledgeable
- ✅ Guide the reader: curiosity → trust → inquiry

**Rule 35 — Writing DON'T Rules**
- ❌ Never keyword stuff
- ❌ Never write "This product…" / "This offering…"
- ❌ Never repeat exact phrases unnaturally
- ❌ Never sound templated
- ❌ Never use aggressive tactics or unverifiable claims

**Rule 36 — Humour Rules (Apply to ALL Pages)**
Humour is present on every page, applied thoughtfully rather than forced. Four modes,
re-based onto the breed:
1. **"The Honesty Policy"** — relatable owner humour: *"Our Staffies are bred for
   affection, stamina, and an unshakeable belief that they are lap-sized."*
2. **"The Interviewer" tone** — the puppy vetting the owner: *"Are you ready to be
   followed into every room you own? Apply to be Roman's person."*
3. **Punny wordplay** — lean into the breed's nickname: *"The nanny dog reputation is
   earned, mostly at the expense of your sofa cushions."*
4. **Comparison humour** — *"Technically a terrier. Functionally a heated blanket with
   opinions."*

Humour never carries a factual claim. A joke about temperament is fine; a joke that
asserts a health screen, a licence or a guarantee is a claim, and Rule 7 applies.

**Rule 37 — Opening Paragraph Formula (Every Section)**
Every section's opening 1–2 sentences carry all four:
- **Entity** — puppy name, colour, BlueStaffyUK, Carlisle
- **Feature** — a measurable, locked fact (price, deposit, delivery band, age)
- **Benefit** — what it means for the buyer
- **Purpose** — the deeper reason it matters

Example: *"Roman is a blue Staffordshire Bull Terrier pup reared at home in Carlisle
(entity) at £1,500 with a £500 refundable deposit (feature), handled daily so he settles
into a new household within days rather than weeks (benefit) — the start of a 12–14 year
relationship (purpose)."*

**Rule 38 — Header Variation Requirement**
Five alternative phrasings for every H2 and H3, question-based where appropriate.

**Rule 39 — Angle-First Rule**
Establish the angle before writing any section.

| Angle | Primary Trigger | Best For |
|---|---|---|
| Transactional | Price and availability | Ready-to-buy visitors |
| Urgency | A real, checkable litter count | High-intent browsers |
| Comparison | BlueStaffyUK vs others | Researching buyers |
| Trust | What we can show and document | First-time owners |
| Value | What the price includes | Research-phase visitors |
| First-Time Owner | Home-reared, handled daily | New dog owners |
| Lifestyle | Flat, family, older owners | Urban and retired buyers |

---

## Category H — AI Snippet Optimization

**Rule 40 — Opening Paragraph Snippet Formula**
Every section opening (50–80 words) includes a direct answer in the first sentence, the
primary keyword early, specific locked numbers (£1,500 / £1,700, £500 deposit, £200–£350
delivery, 12–14 years), entity mentions (BlueStaffyUK, Lisa Bright, Carlisle), a benefit
statement, and a trust signal that is true.

**Rule 41 — Featured Snippet Format Rules**
At least one per page:
- **Paragraph snippet** — roughly fifty words, answer first, plain language
- **List snippet** — `<ol>`/`<ul>`, 5–10 items, each opening on a verb or bold term
- **Table snippet** — 3–6 columns, 3–8 rows, first column the compared categories, real
  numbers rather than adjectives

**Rule 42 — Snippet Technical Requirements**
Snippet target inside the first 800 words · FAQPage schema for question snippets
(`scripts/schema_check.py` is the gate) · under 3 seconds to load
(`scripts/perf_audit.py`) · mobile-friendly and scannable.

**Rule 43 — Advanced Snippet Strategies**
Rotate four patterns: definition + list combo; question heading → answer-first paragraph;
comparison-table domination ("blue vs black Staffy", "Staffy vs Bull Terrier"); and
step-by-step process capture ("how to reserve a puppy", "how to choose a Staffy breeder",
"how to prepare for a Staffy puppy").

---

## Category I — Page Outline Gate (Mandatory Pre-Build)

**Rule 51 — Page Outline First (No Sections Without Approval)**
Before writing sections 1–5 of ANY page, STOP and produce a complete Page Outline. No
section HTML is written until the breeder approves it. The outline contains:

**A. Page Identity** — target slug, exact primary keyword, page type (Transactional /
Informational / Comparison / Location / Puppy Listing / Care Guide), recommended framework
(`.claude/skills/framework-library/SKILL.md`), target word count.

**B. Competitor Snapshot (top 5)** — per competitor: URL, word count, every H2 topic,
primary keywords, special elements, unique angles, and the weakness BlueStaffyUK can
exploit.

**C. Complete H1–H6 Heading Tree** — every heading with its level, draft text, keyword type
(Primary / Secondary / LSI / NLP / Longtail / Comparison / Voice Search), a one-sentence
reason, and its section angle.

**D. Keyword Distribution Table (section by section)**

| Section | Heading | Primary KW | LSI KWs | Longtail KWs | NLP/Conversational | Comparison KWs | Word Count |
|---|---|---|---|---|---|---|---|

One row per section from hero to final CTA; the total row stays at or under 105 (Rule 18 — a ceiling, no floor).

**E. Special Elements Plan** — newsletter signup, comparison table, price card, calculator
or quiz, the 4 counters (Rule 31), trust badge bar, the 3 inquiry forms (Rule 32), video,
FAQ accordion, table of contents (Rule 29), each with its section position.

**F. Fan-Out Keyword List** — exact, phrase, LSI clusters, NLP signals, PAA questions,
voice-search queries, UK location modifiers, comparison phrases.

**GATE:** explicit approval ("Approved", "Continue", or specific changes) before any
section is written.

---

**Rule 52 — Strict Heading Hierarchy + Mandatory H1–H6**
- Sequential only: H1 → H2 → H3 → H4 → H5 → H6. Never skip a level. Stepping back up to
  start a new major section is fine.
- All six levels required on every full-length page.
- Semantic level map: **H1** page topic · **H2** main search intents · **H3** subtopics and
  keyword clusters · **H4** micro-intent answers and PAA coverage · **H5** supporting
  facts, warnings, examples · **H6** ultra-specific details, breeder notes, citations.
- H5 examples: "What the Deposit Covers", "How Delivery Distance Is Priced".
  H6 examples: "Is a Staffy Good With Children?", "What Happens After I Pay a Deposit?"
- Minimum 5 H5 and 5 H6 per page (advisory WARN on the home and location profiles).
- **OUTLINE-FIRST APPROVAL GATE:** the complete H1→H6 outline is shown and approved before
  any page is created or edited. Enforced by `scripts/final_page_audit.py`
  (`all_six_levels` / `min_h5_5` / `min_h6_5`) and written in full in `rules/headings.md`.
- Minimum 3 special elements per page; type and placement from competitor research.

---

**Rule 53 — Header/Footer Inheritance: Never Touch, Always Inherit**
- Every page inherits the shell from `src/layouts/BaseLayout.astro`.
- `src/components/SiteHeader.astro` and `src/components/SiteFooter.astro` are READ ONLY
  when building pages.
- New page: wrap in BaseLayout, write only from the hero down. Rebuild: edit from the hero
  down and leave the shell alone.
- Never paste header or footer HTML into a page file; never add a second `<header>` or
  `<footer>` inside page content.

---

**Rule 54 — Infographic Width Standards (CLS + UX)**

| Page type | Wrapper max-width | Desktop height |
|---|---|---|
| Guide, blog, care page, article | **760px** | 400px fixed |
| Homepage, location pages, hero sections | **1100px** | 400px fixed |
| Mobile (≤767px) | 100% | auto — stacks vertically |

- Never `max-width: 900px` or `max-w-4xl` (896px) — legacy values.
- The shell is always `width: 100%` inside the wrapper.
- Every infographic carries its own `@media` stacking query.
- The design system itself is project 3; until then these are the only width rules and
  `src/styles/global.css` is the whole stylesheet.

---

**Rule [IMAGE-01]:** Image dimensions, sources and infographic types per page type live in
`data/image-manifest.json`; `scripts/bake_images.py` bakes them. Order of precedence:
breeder instruction > the manifest > agent defaults.

**Rule [IMAGE-02]:** Infographic dimensions — 760px wrapper for guide/blog/care pages,
1100px for homepage/location/hero. 400px desktop height, auto on mobile.

**Rule [IMAGE-03]:** Generated portrait images are 1200×2133 native (9:16), displayed at
350px CSS width.

**Rule [IMAGE-04]:** Every page needs its own 1200×630 OG image. Never reuse an article
image for OG without cropping.

---

## Category J — Execution Standards

**Rule 55 — Competitor Analysis Output Format**
A structured markdown report per page: URL, word count, full H2 topic list, primary
keywords, special elements, angles and ICP, the specific weaknesses BlueStaffyUK can
exploit, and a "how to outrank them" strategy with 3–5 concrete actions. Output is a
markdown table + gap matrix + outranking summary. Minimum 8 competitors: top 3 Google,
top 3 Bing, 2 specialist UK breeders.

**Rule 56 — Keyword Fan-Out Sized to the Competitor**
Fetch the top-ranking competitor page for the primary keyword — a real fetch, never
assumed — count the keyword variants it actually uses, and target that count **+5 to +10**.
Record the competitor URL and its count in the session brief. The ten categories organise
the fan-out: transactional · long-tail conversational (6+ words) · voice search (How /
What / Are / Can / Is / Do) · problem-solution · comparison · UK geographic (the 28 cities
in `data/locations.json`) · LSI · NLP · branded (BlueStaffyUK, Lisa Bright, Carlisle) ·
review and testimonial. Full template:
`.claude/skills/bsuk-seo-master-checklist/SKILL.md`.

**Rule 57 — 95–105 Distinct Entities**
Every full-length page carries 95–105 **distinct** named entities from
`.claude/skills/bsuk-entity-agent/SKILL.md`, each said ONCE where it is load-bearing. A
repeated term is a term-budget defect, not a score — `data/quality/evidence-budgets.json`
sets the ceilings and `scripts/evidence_audit.py` enforces them. Categories: people ·
UK locations (the 28 cities plus Carlisle) · health and veterinary terms, each cited under
Rule 64 · food and product brands · statistical entities drawn only from locked facts
(£1,500 / £1,700, £500 deposit, £200–£350 delivery, 12–14 years) · credentials, which are
`LICENCE_CLAIM_PLACEHOLDER` until confirmed. Density target 8–12 entities per 100 words,
naturally integrated.

**Rule 58 — 3 Anchor Text Strategies**
All three types across internal links:
1. **Exact match** — 1–2 per page, for hub and category pages
2. **Conversational/descriptive** — the default, a natural phrase inside the sentence
3. **Branded** — "BlueStaffyUK", "Lisa Bright's home-reared litters"

Never repeat an anchor on a page, and never reuse the same anchor for the same target
across the site — rotate exact / partial / LSI / natural variants; the anchor diversity
ledger is in `.claude/skills/internal-link-agent/SKILL.md`. **Link-First rule:** every
internal and external link sits at the START of its sentence or paragraph, inside the
first clause. Never mid-sentence, never at the end. The sole exception is a branded action
anchor on a CTA. The pack that holds this is `rules/links.md`.

**Rule 59 — 5-Tier Section Creation Form**
Every body section of a page — `section_target.total` of them (the competitors' highest real
section count + 3, never fewer than 9) — completes the form BEFORE any copy:
- **Tier 1:** number and title, word count min/max, 3–5 primary keywords with targets
- **Tier 2:** content angle, conversational opening (75–100 words, framework-matched),
  H2–H6 structure
- **Tier 3:** internal links with varied anchors, only to routes that exist (Rule 62; no per-section
  count), Link-First; 1–2 external authority links, each a row of `docs/reference/external-link-library.md`
- **Tier 4:** 3–5 UK geographic entities, 1–2 authority entities, 2–3 trust signals
- **Tier 5:** special elements, image requirements, CTA placement, 15-item QA checklist

Full template: `.claude/skills/bsuk-seo-master-checklist/SKILL.md`.

**Rule 60 — 4-Part Content Delivery Format**
Every full page build delivers four documents: the competitor analysis report (8–12
competitors, gap matrix, outranking strategy); the complete page content in markdown with
anchors, all `section_target.total` body sections (the competitors' highest real count + 3,
never fewer than 9); the SEO metadata sheet (3 title options, 3 descriptions, the
keyword list, schema recommendations); and the linking strategy map (internal
source→target table plus the external authority catalogue).

**Rule 61 — Phone Number Policy (CRITICAL)**
The phone number is `PHONE_PLACEHOLDER` until project 6 provisions one, and that token is
its only permitted representation anywhere in this repo. When a real number exists it MAY
appear ONLY in `src/components/SiteFooter.astro` and in the `telephone` field of
`src/components/Schema.astro`. It MUST NOT appear in a hero, body copy, a CTA button or a
mid-page contact block. Every body CTA points at the inquiry form on
`src/pages/uk-blue-staffy-breeders-contact/index.astro`, because a form submission can be
attributed to a page and a call cannot.

**Rule 62 — Internal Linking Library**
The canonical internal URL list is `data/page-map.json`, built by
`scripts/build_page_board.py`. Consult it BEFORE writing internal links. Never invent an
internal URL — link only to a route that exists under `src/pages/`. All internal links use
`/slug/` with the trailing slash. `python3 scripts/redirect_check.py` proves the
`data/redirects.json` side.

**Rule 63 — Recommend + Why (ALWAYS, all agents/tasks)**
Whenever an agent or skill presents options it MUST mark exactly **one (Recommended)**,
explain WHY from real data (competitors, the codebase — never a feeling), and name the
trade-off of the recommended pick. In `AskUserQuestion` the recommendation goes first. A
bare list of options is an incomplete deliverable. Mirrors `CLAUDE.md` judgment rule 4.

**Rule 64 — Authority Citations on Technical/Clinical Terms (E-E-A-T)**
A technical or clinical term is cited **once**, at the sentence where the claim is made,
to a government or NIH source (prefer `pmc.ncbi.nlm.nih.gov`), a UK veterinary authority,
or the canonical industry body.
- External authority links open in a new tab: `target="_blank" rel="noopener noreferrer"`.
  Internal links stay same-tab (Rule 62).
- Cite a term once per page; repetition reads as over-optimisation.
- **Verify HTTP 200 before inserting** (`curl -sI`), and assert a clinical entity only if
  the evidence ledger (`data/quality/evidence-ledger.json`) holds its proof — it holds no
  proven claim yet (`parents-dna-clear` is NOT FETCHED), so no clinical claim is assertable yet.
