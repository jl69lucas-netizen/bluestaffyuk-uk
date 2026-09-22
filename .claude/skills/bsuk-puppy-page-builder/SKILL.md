---
name: bsuk-puppy-page-builder
description: THE transactional puppy and buy-cluster page builder for BlueStaffyUK — the /available-puppies/ listing plus the buy-prefixed pages. Merges the on-page-SEO formula (keyword distribution, EFBP openings, conversational headers, counter snippets) with the comparison-cluster pipeline (per-page research protocol, dup-gate, uniform image boxes, final-page-pass) under a TRANSACTIONAL profile — puppy cards and prices above the fold, one Product+Offer per pup, reserve CTAs on a cadence, an enquiry form listing the real pups. Use for any "for sale" / "buy" / "available puppies" page build, rebuild or polish.
---

# SKILL: BSUK Puppy Page Builder (re-based for BlueStaffyUK, 2026-09-16)

Re-based from the source repo's for-sale builder. The **shape is the source's** — board
first, then sections, then gates — and every content requirement is BSUK's own, carried by
`rules/puppies.md` rather than restated here.

**How this differs from `.claude/skills/bsuk-comparison-page-builder/SKILL.md`:** comparison
pages serve DECISION intent (X vs Y, neutral tables, hub + spoke). Puppy pages serve
TRANSACTIONAL intent: real available-pup cards with prices near the fold, deposit/reserve
CTAs on a cadence, one `Product` + one `Offer` per pup, honest scarcity, and an enquiry form
listing the pups that actually exist. Everything the comparison cluster locked (dial TOC +
mobile jump-rail, uniform image boxes, dup-gate, seam dividers, image-per-header) carries
over but RESTYLED so the two clusters never look identical.

---

## 0. The board comes first

No page in this cluster is built, rebuilt or polished before its row exists on the page
board: `python3 scripts/build_page_board.py`, then `python3 scripts/board_gate.py <slug>`.
A build that starts without a board row has no record of what was approved.

## 1. Page inventory & build order

Confirm the on-disk route in `src/pages/` first; every slug below is in `data/page-map.json`.

**The listing:** `/available-puppies/` (index) and `/available-puppies/<slug>/` — one page per
pup in `data/puppies.json`: Roman, Byrd, Ince (£1,500) · Vennie, Christa, Cheryl (£1,700).

**The buy cluster:**
1. `/buy-blue-staffy-puppies-uk/` — the hub
2. `/blue-staffy-pup-sale-uk/`
3. `/buy-staffy-puppies-for-sale-uk/`
4. `/blue-staffy-uk-breeders/`
5. `/uk-blue-staffy-puppy-buying-guide/`

Supporting: `/blue-staffy-health-uk/` · `/uk-locations/` and its 28 city pages ·
`/uk-staffordshire-bull-terrier-guide/`.

Cannibalisation guard: each page owns ONE primary intent; "buy", "for sale" and "near me"
get DISTINCT keyword sets, headers and geo distributions (a unique 4–5 city set per page,
real slugs from `data/locations.json`, never the same trio twice).

## 2. Content formula

### 2a. Keyword distribution per page (~85–105 total mentions; 1–2% primary density, never stuffed)
| Type | Count | Note |
|---|---|---|
| Primary keyword | 30–35 | natural placements; front-loaded in title/H1/first 100 words |
| LSI | 20–25 | across variations |
| Long-tail (6+ words, conversational) | 15–20 | in headers + opening paragraphs |
| Branded ("BlueStaffyUK", "Lisa Bright") | 10–15 | |
| Conversational/voice queries | ~23 | headers + PAA answers |
| Comparison ("blue vs blue-brindle", "male vs female") | 5–8 | link to the comparison cluster |
| Solution ("health-tested", "KC-aware") | 5–10 | |
| Transactional ("reserve", "deposit", "available now") | ~15 | honest only |

Source for the actual keywords: per-page Sprint 0 research. **Search-console data is NOT
FETCHED until project 6** — no query, impression or position figure may be written before
then, and none may be invented.

### 2b. EFBP opening paragraph — under EVERY header
Every H2/H3/H4 opens with 1–2 sentences carrying **Entity + Feature + Benefit + Purpose**,
in first-person voice (`rules/copy.md`):

> "Roman (entity) is a blue-and-white male we home-raised here in Carlisle (feature); he
> settles quickly in a busy family house (benefit), which is why we match him to homes with
> children and activity rather than a quiet flat (purpose)."

### 2c. Headers
Conversational Q&A style (What/How/Is/Can/Where), per the Heading Hierarchy Outline Gate:
the full H1→H6 outline is approved BEFORE any code, no skipped levels, all six levels,
**≥5 H5 AND ≥5 H6** (`rules/headings.md`). Semantic map: H1 topic · H2 search intents ·
H3 subtopics · H4 PAA/micro-intents · H5 supporting facts/warnings · H6 breeder notes.
Draft 5 A/B variants for H1 and each major H2 at outline stage; the breeder picks. Unique
hybrid headers per page — zero exact or template crossover with siblings (dup-gate `--headers`).

### 2d. Entity variety
85–112 **DIFFERENT** entities per page (the pups by name, Carlisle and the 28 cities,
Staffordshire Bull Terrier, the Kennel Club, L-2-HGA and HC-HSF4 where the ledger records
them, DEFRA-approved transport, vet and microchip terms) — each mentioned a natural number
of times. The failure mode is documented: the business name in every sentence is unreadable
and unrankable. Targets: brand 5–10×, full address 1–2× plus city 5–8×, each pup named in
its card plus 1–2 body mentions. Every health, licence and legal entity is bounded by
`data/quality/evidence-ledger.json`; unconfirmed ones are LICENCE_CLAIM_PLACEHOLDER /
LEGAL_CLAIM_PLACEHOLDER in prose, or NOT FETCHED.

### 2e. Meta
The puppy cluster uses the **extended 3-part format** — see §6a, which `rules/puppies.md`
`puppies-extended-meta` names as the canonical spec. Three sets per page (Educational /
Benefit-Solution / Transactional-Urgency), one marked (Recommended) with why and trade-off.

### 2f. Counter snippets
8 per page, under 4 words, number-led, and **only** from the locked set: `£1,500 From` ·
`£500 Deposit` · `£200–£350 Delivery` · `28 UK Cities` · `12–14 Year Breed Lifespan` ·
`Six Pups Named` ·
`24h Reply`. NEVER a fabricated count — no invented family totals, no invented ratings.

### 2g. Links
Link-First anchors (sentence START, never mid or end; branded ACTION anchors on CTAs are
exempt). Internal anchors from the Anchor Diversity Ledger
(`.claude/skills/internal-link-agent/SKILL.md` — no repeated anchors site-wide). External:
credible UK authorities (The Kennel Club, the RSPCA, the PDSA, a veterinary school, a
`gov.uk` welfare page) — cite the specific resource page; a curl 403 is a bot-block, not a
dead link, so retry with a UA. Internal same-tab, external new-tab + ↗. The external-link
library is deferred to project 6.

## 3. Transactional layer (what makes these NOT comparison pages)

1. **Puppy cards near the fold** — real pups from `data/puppies.json`, price from
   `data/price-matrix.json` through a helper, and the delivery line under the trust badges:
   `UK home delivery £200–£350 by distance · or collect in Carlisle`. **Never a card without
   the delivery line** (`rules/puppies.md` `delivery-band-on-every-card`). The refundable
   £500 deposit is stated wherever the band is.
2. **Schema** — one `Product` with exactly one `Offer` per pup, several pups wrapped in an
   `ItemList`; never one `Product` with several offers, never a second bare `Product`
   outside the list (`rules/puppies.md` `product-schema-per-pup`, enforced by
   `tests/render/checks/schema.ts::schema-single-product-offer`).
3. **Availability is a fact about one animal** — `InStock` **only** where
   `data/puppies.json` says the pup is Available; a sold or reserved pup renders `SoldOut`,
   or `PreOrder` where a deposit is held and the pup has not left
   (`rules/puppies.md` `instock-only-on-an-available-pup`, enforced by
   `tests/render/checks/schema.ts::schema-sold-not-instock`). The status is read once, from
   the data file, and never written twice.
4. **CTA cadence** — a reserve/enquire CTA every 500–700 words; respect the one-global-CTA
   rule. Mid-page CTAs point at `#reserve` or the form anchor.
5. **Honest scarcity only** — real counts from the data file ("three males still
   available"). No fabricated urgency, testimonials or review counts; a review BSUK has not
   received is NOT FETCHED.
6. **Enquiry form on every page in the cluster** — `src/components/ContactForm.astro`. Its
   `puppy` select lists each ACTUAL pup with its price, sourced from `data/puppies.json` and
   `data/price-matrix.json`, never hardcoded; the delivery question offers exactly the two
   real options (UK home delivery £200–£350 by distance, or collection in Carlisle).
   Contract: `.claude/skills/bsuk-contact-form/SKILL.md`.

## 4. Build phases

- **Phase 1 Research (MANDATORY, no skip):** Sprint 0 competitor research per page (top-10
  organic and social, un-fetchable = NOT FETCHED) → deliverables identical to the comparison
  cluster (SERP snapshot, section inventory, gaps, keyword universe, entity map, visual
  blueprint, PAA set). No search-console figures until project 6.
- **Phase 2 Planning gates:** grill-me (Sprint 0.5) → **two strategies plus one blended**,
  one (Recommended) → distribution matrix with **MANDATORY / COMPETITOR-BASED /
  SUGGESTED-RECOMMENDED** section groups, a grounded why on each → H1–H6 outline gate (with
  the header dup-gate run BEFORE approval) → skeleton screens → **HARD STOP until the
  breeder supplies images and says start**.
- **Phase 3 Build:** section by section per the approved matrix; verify rendered `dist/` per
  page; commit per page.
- **Phase 4 QA:** dup-gate (body + headers, pairwise against every sibling and the
  comparison cluster) → `python3 scripts/final_page_audit.py --puppies` → the manual pass
  list (§6) → `python3 scripts/generate_sitemaps.py`. **No push, no deploy and no index
  submission until project 6.**

## 5. Component map

- **Heroes** — one of the cluster's assigned heroes, ~400px class, hero staggered sizing
  rules apply. Hero → separator → counters, and on mobile the hero IMAGE comes first via CSS
  `order`, never by reordering the DOM (`rules/puppies.md` `puppy-cluster-component-order`).
- **Dial TOC (desktop) + jump-rail (mobile)** — same mechanics as the comparison pages in a
  distinct puppy-cluster style; scroll-margin offset for the rail; `scroll-behavior: auto`.
  The dial must WORK: a conic ring driven by an IntersectionObserver scroll-spy that also
  highlights the active item and updates the `x of N` counter. A static ring reads as broken.
- **Puppy listing** — cards built on the data file: category badge, availability dot, name,
  price from the matrix, the delivery line, and a full-width "Enquire about <name>".
  **Card crop is 800×800**; the in-body portrait box is the uniform 16:9
  (`rules/images.md` `uniform-inbody-image-sizing`).
- **Portraits — the locked framing rule.** A puppy portrait shows the whole dog, or at
  minimum head and chest with ears and muzzle complete inside the frame. Bake single-pup
  portraits as a **4:5 blur-fill** master and ship the mobile full-bleed 4:5 rule
  (`.sec-img.og-tall{width:100vw;margin-left:calc(50% - 50vw);aspect-ratio:4/5;border-radius:0}`);
  desktop keeps the uniform 16:9 box. Tune `object-position` per image so the head sits
  inside the box — the box never changes, only the focal point — and where no focal point
  saves the frame, re-cut the master rather than shipping the crop.
  **Never head-crop a pup** (`rules/puppies.md` `no-head-cropped-portraits`).
- **In-body images** — every H2, H3 and key H4 gets an image, in the uniform box, under
  100 KB WebP with a `-760.webp` sibling and srcset, `width`/`height` always set. H3 → image
  → prose. No two images share an alt (`rules/images.md`).
- **Seam divider** — a puppy-cluster variant of the wordmark divider, 4–8 per page,
  decorative `alt=""`, lazy, with CLS dimensions. One seam before **every** section.
- **Further reading** — 2-up cards whose thumbnails are the **target page's own hero**
  (`rules/images.md` `read-card-thumb-is-target-hero`), plus a location-aware delivery block
  linking real `/uk-locations/<slug>/` pages.
- **Sidebar** — no page-level sidebar; a sticky filter is a section-level component only,
  and a sticky mobile CTA bar covers persistent-CTA needs.
- **Stale-fact reconciliation on any intake (binding):** any figure arriving with a design
  kit is reconciled against the locked set before it ships — prices to
  `data/price-matrix.json`, delivery to the £200–£350 band, deposit to £500, lifespan to
  12–14 years, phone to `PHONE_PLACEHOLDER`, licence and statute to
  LICENCE_CLAIM_PLACEHOLDER / LEGAL_CLAIM_PLACEHOLDER. Invented names, ratings and counts are
  deleted, not adjusted.

## 6. Pass gates (every page)

0. **Write-From-Outline, NEVER-From-Sibling.** Reuse components, CSS classes and structural
   patterns freely — that IS the kit — but every page's **prose** is written fresh from its
   own approved H1–H6 outline and distribution matrix, never pasted or paraphrased from a
   sibling. Open a sibling only to read its structure. Lean on the page's OWN angle. Only the
   whitelist may match verbatim (the delivery line, the doc-badge list, the counter strip,
   the licence notice, CTA labels, real reviews, real link labels). Run
   `python3 scripts/dup_content_audit.py <slug> <siblings…>` **and** `--headers` on your own
   draft before it is "done", targeting **zero** non-whitelist crossover. Dedup is a
   pre-write discipline, not post-hoc cleanup (`rules/copy.md`).
1. `scripts/dup_content_audit.py` + `--headers` — zero tolerance beyond the whitelist.
2. `python3 scripts/final_page_audit.py --puppies` — PASS required.
3. Manual gate list: 400px heroes · a unique newsletter image and one-line title per page ·
   an opening paragraph under every header · uniform image boxes · mobile table stacking ·
   jump-rail scroll-margin · further-reading cards with real thumbnails · AA contrast ·
   a warm median-of-3 Lighthouse run.
4. First-person voice sweep + `.claude/skills/anti-ai-writing/SKILL.md` +
   `.claude/skills/bsuk-evidence-pass/SKILL.md`.
5. Verify in `dist/`, never by grepping `src/`. Commit; **there is no push and no deploy
   until project 6**, and no URL is submitted anywhere before then
   (`.claude/skills/bsuk-indexing/SKILL.md`, `rules/deploy.md`).
6. **Seam parity** — one seam emblem before every section:
   `echo "seams=$(grep -c 'class=\"seam\"' <page>) sections=$(grep -c '<section' <page>)"`.
7. **Verify every gate finding before you fix a page** —
   `.claude/skills/bsuk-gate-integrity/SKILL.md`. Twelve checkers have cried wolf; confirm
   against the flagged rule first, and when the check is wrong, fix the check and add a
   regression test.
8. **Perf conclusions need ≥5 runs.** CLS is bimodal; a single Lighthouse run has produced a
   confident wrong attribution before. Read the distribution, not one number.

## 6a. Meta — the extended 3-part format (canonical spec for `rules/puppies.md`)

Every puppy-cluster page uses the extended 3-part meta. Do NOT truncate to a short title.

- **Title** = `Primary Keyword | Related Conversational Query | Number + Positive Word | Brand — LSI/NLP Keywords`
  — front-load the primary keyword; extend toward but **never past 280 characters**.
- **Description** = `Primary Benefit | Secondary Benefit | Trust Signal + CTA`, **≤300 chars**.
- The real price floor comes from `data/price-matrix.json` (£1,500 for Roman, Byrd and Ince;
  £1,700 for Vennie, Christa and Cheryl), never typed by hand, plus real credentials and a
  branded ending.
- A licence or statute claim in a title or description is written
  `LICENCE_CLAIM_PLACEHOLDER` / `LEGAL_CLAIM_PLACEHOLDER` until it is confirmed — in prose
  only, never in a heading, a route or a code key.

## 6b. Component fidelity — the recurring mistake

The breeder has caught a rebuild shipping the homepage/comparison components instead of the
cluster's own kit. Binding: read the cluster's component ledger and look at the designs
before building; never import the comparison hero, the comparison counter strip or the
comparison seam onto a puppy page. Where a kit component does not exist yet, build it from
the spec in this file rather than substituting a neighbour's.

## 7. Hub rule — the listing is the source of truth

`/available-puppies/` is the cluster's hub, and it is the only page allowed to describe the
litter as a whole. Everything it says about a pup — name, sex, colour, price, availability —
is read from `data/puppies.json` and `data/price-matrix.json`, so the hub and the individual
pages cannot disagree. A pup that leaves the litter is marked in the data file and its page
is retired through `data/redirects.json`; it is never left rendering `InStock`.

> The source repo's page-1 special mode was about selling fertile eggs. It has **no BSUK
> equivalent and was dropped**, not re-labelled — inventing a BSUK version would be exactly
> the "re-labelled fact" this port exists to prevent. If a rule and the page disagree, check
> the page before you trust the rule.
