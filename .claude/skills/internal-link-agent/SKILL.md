---
name: internal-link-agent
description: Audits and improves internal link structure across BSUK pages. ALWAYS starts from the sitemap (the canonical page universe), then finds orphan pages (no inbound links), missing hub-to-spoke links, missing spoke-to-hub links, and anchor text opportunities — enforcing the Anchor Diversity Ledger (no repeated anchors; exact/partial/LSI/natural variation) and the Link-First placement rule. Produces a prioritized fix list with exact HTML insertions. Never modifies H1 or canonical.
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## Purpose

You are the **Internal Link Agent Skill** for BlueStaffyUK. You map the internal link graph, find gaps, and prescribe exact fixes — because internal links pass authority to the pages that need it most and help Google understand site structure.

---

## On Startup — Read These First

1. **Read** `docs/reference/seo-rules.md`
2. **Read** `docs/reference/top-pages.md` — high-value pages that most need inbound links
3. **Ask user:** "Full site audit, specific page audit, or fix known orphan pages?"

---

## BSUK Hub/Spoke Link Architecture

Every page belongs to a cluster. Links must flow correctly:

```
Hub → All Spokes (hub lists every spoke with descriptive anchor text)
Spoke → Hub (each spoke links back to its hub)
Spoke → 2–3 Sibling Spokes (cross-links between related pages)
All pages → Homepage (via header nav — already exists)
All pages → Contact/Enquiry (via CTA — check this exists)
```

### Known Cluster Maps

**Buying-guide cluster (slugs verified 2026-06-03):**
- Hub: `/uk-blue-staffy-puppy-buying-guide/`
- Spokes: `/blue-staffy-pup-sale-uk/`, `/buy-blue-staffy-puppies-uk/`, `/buy-staffy-puppies-for-sale-uk/`, `/uk-staffordshire-bull-terrier-guide/`, `/blue-staffy-health-uk/`, `/blue-staffy-uk-breeders/`, `/available-puppies/`

**Location cluster:**
- Hub: `/uk-locations/`
- Spokes: all UK region pages in `/uk-locations/<slug>/`

**Availability cluster:**
- Hub: `/available-puppies/`
- Spokes: `/available-puppies/<slug>/` (Roman, Byrd, Ince, Vennie, Christa, Cheryl)

**Trust cluster:**
- Hub: `/blue-staffy-uk-breeders/`
- Spokes: `/uk-blue-staffy-breeders-contact/`, `/blue-staffy-health-uk/`, `/uk-blue-staffy-puppy-buying-guide/`

---

## Audit Protocol

### Step 0 — Sitemap Inventory (REQUIRED FIRST — added 2026-07-11)

The sitemap is the canonical page universe. Every audit and every link strategy starts here — never from ad-hoc greps or memory of what pages exist.

```bash
# Canonical page list from the generated sitemap shards (source: scripts/generate_sitemaps.py)
grep -oh '<loc>[^<]*</loc>' public/*sitemap*.xml | sed 's/<[^>]*>//g' | sort -u > /tmp/sitemap_pages.txt
wc -l /tmp/sitemap_pages.txt   # should match the live URL count (100+); if 0, run: python3 scripts/generate_sitemaps.py
```

Use `/tmp/sitemap_pages.txt` as the master list for:
- **Orphan detection** — every sitemap URL must have ≥1 contextual inbound link (nav/footer don't count)
- **Cluster completeness** — map every sitemap URL into a hub/spoke cluster; a URL in no cluster is a strategy gap
- **Link-target validation** — never propose a link to a URL not in the sitemap (phantom-target guard)
- **The site-wide Anchor Diversity Ledger** (below) — one ledger row per sitemap URL

> Note: `src/pages/` is the deployed source of truth; `site/content/` greps below are the legacy/staging path. When both exist, run link extraction against `dist/` (built output) or `src/pages/` — per the Verify-Rendered-Not-Source rule.

### Step 1 — Find All Internal Links

**Bulk mode:** Pass `slugs: [slug1, slug2, slug3]` to process multiple pages in one call instead of one at a time.

**Gutenberg strip (required before analysis):** BSUK HTML may contain WordPress Gutenberg block comments that confuse link parsing. Strip them first:
```bash
# Strip Gutenberg comments before analysis
sed 's/<!-- wp:[^>]*-->//g' site/content/[slug]/index.html > /tmp/clean.html
# Use /tmp/clean.html for all subsequent grep/analysis
```

```bash
# Extract all href="/..." links from all pages (after Gutenberg strip)
for f in site/content/*/index.html; do
  slug=$(dirname "$f" | sed 's|site/content/||')
  sed 's/<!-- wp:[^>]*-->//g' "$f" | grep -o 'href="/[^"]*"'
done | sed 's/href="//;s/"//' | sort | uniq -c | sort -rn > /tmp/link_counts.txt

# Pages with most inbound links (well-linked pages)
head -20 /tmp/link_counts.txt
```

### Step 2 — Find Orphan Pages
```bash
# List all page slugs
find site/content/ -name "index.html" | sed 's|site/content/||;s|/index.html||' | \
  grep -v "^$" | sort > /tmp/all_pages.txt

# Compare against linked pages
grep -roh 'href="/[^"]*"' site/content/*/index.html | \
  sed 's/.*href="//;s/".*//' | sort -u > /tmp/linked_pages.txt

# Pages not linked from anywhere
comm -23 /tmp/all_pages.txt /tmp/linked_pages.txt
```

### Step 3 — Check Hub-to-Spoke Links
```bash
# Example: check buying-guide hub links to all spokes
grep -o 'href="/buy-blue-staffy[^"]*"\|href="/blue-staffy-pup-sale-uk[^"]*"\|href="/blue-staffy-health-uk[^"]*"' dist/uk-blue-staffy-puppy-buying-guide/index.html

# Check each spoke links back to hub
grep -l 'href="/uk-blue-staffy-puppy-buying-guide/"' dist/buy-blue-staffy-puppies-uk/index.html dist/blue-staffy-pup-sale-uk/index.html
```

### Step 4 — Anchor Text Audit
```bash
# Find "click here" / "read more" / generic anchor text
grep -rn '>click here<\|>read more<\|>here<\|>learn more<' site/content/*/index.html | head -20
```

---

## Link Priority Scoring

Score each missing link 1–3:

| Score | Condition |
|-------|-----------|
| 3 (Critical) | Top-10 page by traffic has no inbound links from related pages |
| 2 (High) | Hub missing spoke link, or spoke missing hub link |
| 1 (Normal) | Cross-link opportunity between sibling pages |

---

## Anchor Text Rules

**Good anchor text:**
- Descriptive: "Blue Staffy puppy care guide"
- Keyword-rich but natural: "Staffy vs American Bully comparison"
- Action-oriented: "see our blue and blue brindle Staffy pups"

**Bad anchor text:**
- Generic: "click here," "read more," "here," "this page"
- Over-optimized: exact match keyword repeated identically across 20 links
- Empty: `<a href="/page/"></a>`

### Anchor Diversity Ledger (site-wide — added 2026-07-11)

Repeated identical anchors to the same target are the #1 over-optimization signal. Before adding ANY link, build the ledger for its target and pick an unused variation.

```bash
# All anchors currently pointing at a target, site-wide (run on dist/ or src/pages/)
target="/buy-blue-staffy-puppies-uk/"
grep -roh "href=\"$target\"[^>]*>[^<]*" dist/ | sed 's/.*>//' | sort | uniq -c | sort -rn
```

**Ledger format (include in every audit output):**

| Target URL | Anchors in use (count) | Next variation to use |
|---|---|---|
| /buy-blue-staffy-puppies-uk/ | "buy Blue Staffy puppies UK" (1), "our available Blue Staffy pups" (1) | "home-raised Blue Staffy puppies" (LSI) |

**Variation rules:**
1. **Never repeat an anchor** — not twice on a page, and not for the same target across the site. Every new link gets a fresh variation.
2. **Rotate the 4 anchor types** per target: exact match (≤1 site-wide per target beyond the hub) → partial match → LSI/synonym ("Staffy puppy pricing", "what a blue pup costs") → natural language / first-person ("compare our two coat colours").
3. **Mine variations from real data** — GSC query variants, PAA phrasing, and the keyword-cluster tiers (`.claude/skills/keyword-cluster/SKILL.md`) — not invented synonyms.
4. **No stop-word-only anchors** — anchors are meaningful content words ("Blue Staffy puppy feeding plan"), never filler ("more about this", "the page on feeding").

### Anchor Position Rule (Internal + External)

**Link-First rule (2026-07-11):** links must appear at the **START** of the sentence — inside the opening words (first clause). Never mid-sentence, never at the end.

✅ **Good — link in subject/predicate position:**
- `"Our <a href="/uk-staffordshire-bull-terrier-guide/">Blue Staffy puppy guide</a> covers adult weight, pricing, and care requirements."`
- `"<a href="/blue-staffy-health-uk/">Staffordshire Bull Terrier health screening</a> includes HC and L-2-HGA DNA test results for both parents."`

❌ **Bad — link at end of sentence:**
- `"Learn about coat colour differences in our <a href="/uk-staffordshire-bull-terrier-guide/">blue vs brindle guide</a>."`
- `"For pricing details, see our <a href="/buy-blue-staffy-puppies-uk/">price page</a>."`

### Open-in-New-Tab Policy (confirmed 2026-06-03)

> Best practice — verified against SEO + WCAG. `target="_blank"` is **not** a ranking factor; forcing every link to a new tab gives **zero SEO value** and hurts UX (breaks the back button, tab clutter on mobile).

- **Internal links → SAME tab, always.** Never add `target="_blank"` to an internal `/slug/` link. (Internal new-tab breaks navigation and is an anti-pattern.)
- **External authority links → NEW tab** (`target="_blank" rel="noopener noreferrer"`) **+ a visual/a11y cue.** On a sales page this keeps the high-intent buyer on our page instead of shipping them to gov.uk/the Kennel Club with no easy return. Pattern used site-wide: a subtle CSS `::after { content:"↗" }` affordance scoped to `.home-d a[target="_blank"]` (see `src/pages/index.astro`).
- Note: warning of a new window is WCAG **3.2.5 (Level AAA)**, not AA — so `target+rel` alone is AA-compliant; the ↗ cue is the courtesy affordance.
- **Authority citations on technical terms:** cite important technical/clinical terms ONCE to a credible **government/NIH** source (prefer `pmc.ncbi.nlm.nih.gov`) or the canonical industry authority, at the claim sentence. Reusable verified-source table: `docs/reference/external-link-library.md §Authority Citations` (HC and L-2-HGA DNA testing, hip dysplasia, canine parvovirus, DEFRA pet travel rules, Lucy's Law, Glasgow City Council breeder licensing). Verify 200 first; link a term only once per page.

### Anchor / Jump-Link Cross-Reference Technique (in-content `#anchor` links) — confirmed 2026-06-03

> When a later paragraph references a topic that an **earlier on-page section already answers in depth**, link the prose to that section via its `#id` (e.g. `href="#compare-colours"`). This is a high-value, low-effort technique that improves dwell time, scannability, and on-page topical signals — and it costs nothing because every section already carries an `id` + `scroll-mt-20`.

**Worked example (homepage, the model to copy):** the FAQ "What's the difference between a blue and a blue brindle Staffy?" answer points readers **up** to the Compare Coat Colours section (`Is a Blue or a Blue Brindle Staffy Right for You?`) via `href="#compare-colours"`. The deep-dive table is the payoff; the FAQ is the teaser.

**How to apply it everywhere:**
1. **Inventory section IDs first:** `grep -n 'id="' <page>` — every major section should have a stable `id` + `scroll-mt-20` (so the jump doesn't hide under a sticky header).
2. **Link teaser → deep-dive in the same page.** FAQ answers, "still deciding?" lines, and pros/cons sections are prime spots to jump **up** to a comparison/spec table or **down** to the available-puppies grid / contact form.
3. **First-person + descriptive anchor at the sentence start** — e.g. `<a href="#compare-colours">Compare our blue and blue brindle pups side by side</a> in the table above to see which fits your home.` Never a bare "click here," never mid-sentence, never parked at the end.
4. **Schema-safe caveat (critical):** if a section's text is rendered from a data array that also feeds JSON-LD (e.g. `faqItems` → `FAQPage` `acceptedAnswer.text`, rendered via `{item.a}` = HTML-escaped), you **cannot** put an `<a>` inside that string — it will show as literal text and pollute the schema. Instead add the jump-link in a **separate prose `<p>`** outside the array (the homepage adds a "Still weighing it up?" line under the FAQ accordion).
5. Cap ~1–2 jump links per section; they supplement, not replace, contextual links to other pages.

**Well vs. badly done (save for every future build):**
| ✅ Good | ❌ Bad |
|---|---|
| `#anchor` jump from a teaser to the in-depth section it summarizes | Linking to a section that doesn't exist / has no `id` |
| Descriptive first-person anchor at sentence START (Link-First) | "see above", "click here", anchor mid-sentence or at sentence end |
| Jump-link added in standalone prose when the source is schema-bound | `<a>` injected into a `{item.a}`/schema-bound string (renders as literal text) |
| 1–2 jumps per section | 5+ jumps stuffed into one paragraph (over-optimization) |

### External URL Verification (Before Any External Link Insert)
```bash
# Always verify external URLs return 200 before inserting
url="https://www.gov.uk/government/news/lucys-law-spells-the-beginning-of-the-end-for-puppy-farming"
status=$(curl -sI -A "Mozilla/5.0" --max-time 10 "$url" | head -1 | awk '{print $2}')
[ "$status" = "200" ] && echo "✅ Safe to link" || echo "❌ SKIP — HTTP $status"
```

> **⚠️ Bot-block exception (learned 2026-06-05):** a curl 403/406 ≠ dead link. Some authority domains block non-browser user agents — **`thekennelclub.org.uk` is the known case** (the recurring "Kennel Club link is dead" was anti-bot blocking all along, not a broken URL — note the example above must use a browser UA, and the canonical host is `www.thekennelclub.org.uk`, not the bare apex which 301-hops). On a 403/406 for a known authority: retry with `-A "Mozilla/5.0"`, then browser-verify / accept user confirmation before skipping. Never drop a valid Kennel Club/.gov.uk/NIH citation on a bare curl 403. Also: cite a *breed/topic* claim to the **specific resource page** (`thekennelclub.org.uk/breed-information/staffordshire-bull-terrier/`), not the org homepage.

## Why Claude Code + Playwright First

All internal link operations use Claude Code file reads and Bash grep for speed and accuracy. The Playwright CLI (`npx playwright@latest`) handles live-site verification. No external MCPs are used.

- Link suggestion: grep + python against site/content/ HTML files
- Broken anchor verification: `curl -sI` to confirm target returns 200
- External links: curated library + curl verification before every insert
- Bulk mode: `slugs: string[]` param in Step 1 above handles all pages in one pass

---

## Fix Templates

### Add Hub → Spoke Link
```html
<!-- Add to hub page's spoke card section -->
<a href="/[spoke-slug]/" class="spoke-link">
  [Descriptive anchor text — what this spoke page answers] →
</a>
```

### Add Spoke → Hub Link
```html
<!-- Add in body prose or navigation section -->
<p class="bsuk-body">
  <a href="/uk-blue-staffy-puppy-buying-guide/">Our complete UK Blue Staffy buying guide</a> walks
  through every step from deposit to collection day. <!-- Link-First: anchor opens the sentence -->
</p>
```

### Fix Generic Anchor Text
```
Before: <a href="/buy-blue-staffy-puppies-uk/">click here</a>
After:  <a href="/buy-blue-staffy-puppies-uk/">view Blue Staffy puppies for sale</a>
```

---

## Output Format

```markdown
# Internal Link Audit — [scope]
Date: [YYYY-MM-DD]

## Orphan Pages (no inbound links)
| Page | Priority | Suggested Source Page | Suggested Anchor |
|------|----------|----------------------|-----------------|

## Missing Hub → Spoke Links
| Hub | Missing Spoke | Fix |
|-----|-------------|-----|

## Missing Spoke → Hub Links
| Spoke | Hub | Line to add link |
|-------|-----|-----------------|

## Generic Anchor Text Fixes
| Page | Line | Current | Suggested |
|------|------|---------|-----------|

## Priority Fix Order
1. [Fix] — Score: [3/2/1] — Est. impact: [description]
```

---

## Rules

1. **Never modify H1 or canonical** when adding links
2. **Descriptive anchor text required** — reject generic text
3. **Orphan check on every full audit** — no page without inbound links
4. **Hub/spoke architecture takes priority** — fix cluster links before cross-links
5. **Max ~3 new links per edit session** per page — avoid over-optimization signals. **Intent clarified (2026-06-04):** the real risk is *clustered exact-match anchors* or *many links to the same target*, not a handful of distinct contextual links spread across a long page. On a large page (e.g. the 1000-line homepage), more than 3 is acceptable **if** each link has a different target, a descriptive non-duplicated anchor, sits at the sentence start (Link-First), and is distributed one-per-section — and the user has approved the set. State the trade-off when exceeding 3.
6. **Save audit** — write to `docs/research/internal-link-audit-[date].md`
7. **Internal = same tab, external = new tab + ↗ cue** — never `target="_blank"` on an internal link (see Open-in-New-Tab Policy)
8. **Use the jump-link technique** — cross-reference earlier in-depth sections from later teaser prose via `#id`; respect the schema-safe caveat (no `<a>` inside `{item.a}`/JSON-LD-bound strings)
9. **Duplicate-slug check before redirecting** — confirm two similar slugs are truly the same *intent* before proposing a 301; hub vs guide, availability vs cost, etc. are distinct pages → link them, don't redirect (and use **301** for permanent consolidation, never 302)
10. **Sitemap first, ledger always** — Step 0 sitemap inventory is mandatory before any strategy; every proposed link must pass the Anchor Diversity Ledger (unused variation, correct type rotation) and the Link-First placement rule
