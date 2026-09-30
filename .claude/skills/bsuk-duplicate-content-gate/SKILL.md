---
name: bsuk-duplicate-content-gate
description: Use BEFORE building any page that has siblings (comparison spokes, location pages, puppy listings, variant/attribute pages, blog posts) and AGAIN before giving any page a final pass — catches word-for-word and template-for-template duplication across pages (headers, paragraphs, sentences, anchors) so it never ships and never has to be rewritten post-hoc. Also use when the breeder says "duplicate content", "same headers", "crossover", or "these pages sound the same".
allowed-tools: [Read, Write, Bash]
---

# Duplicate-Content Gate — headers, paragraphs, sentences, anchors

## Golden Rule
> **Confidence Gate:** ≥97% before writing any site file; below it, run the Clarification Checkpoint.
> **Verify rendered, not source** — both audit modes run on `dist/` (build first: `npm run -s build`).
> **Never "fix" duplication by deleting content** — rewrite with page-specific framing; same-content rule still holds.

---

## Why This Exists (the RED baseline)

**2026-07 comparison cluster:** 29 crossover headers — shared word-for-word or template-for-template with the flagship comparison page — shipped on sibling spokes and had to be found and rewritten AFTER build (token waste, breeder time waste). Then on 2026-07-11, first run of the new `--headers` mode found **68 more template crossovers between two sibling comparison spokes** — each spoke had been de-duplicated against the flagship page but never against *each other*. Lesson: duplication is pairwise across the WHOLE sibling set, and it must be gated BEFORE build, not purged after.

## The Two Tools (both on `dist/`)

```bash
npm run -s build   # always build first — audit rendered output

# 1. Body-copy shingles: word-for-word passages ≥12 words shared between pages
python3 scripts/dup_content_audit.py                       # whole site
python3 scripts/dup_content_audit.py slugA slugB slugC     # a sibling set

# 2. Heading crossovers: exact AND templated H1–H6 shared between pages
#    (catches short headers the 12-word shingle check is blind to)
python3 scripts/dup_content_audit.py --headers             # whole site
python3 scripts/dup_content_audit.py --headers slugA slugB # a sibling set
```

Exit 1 = FAIL. `--headers` normalizes breed/coat names to `{breed}`, so "Is an English Bull Terrier Right for You?" vs "Is an American Bully Right for You?" is flagged as a TEMPLATE crossover even though no words match.

## When It Runs (three mandatory gates)

1. **Pre-build (outline stage):** before the Heading Hierarchy Outline Gate approval, run `--headers` across the page's ENTIRE sibling set and diff the *proposed* outline against every live sibling's headers. A proposed header that exact- or template-matches a sibling gets page-specific conversational framing BEFORE any code is written.
2. **Pre-pass:** `bsuk-final-page-pass` runs both modes on the new page vs its siblings; any un-whitelisted hit = the page does NOT pass.
3. **Cluster sweep:** after finishing a cluster (all spokes + hub), run both modes across the full cluster — pairwise, not just vs the flagship. This is the check that was missed in July.

## What's ALLOWED to Repeat (whitelist — edit in the script, not ad-hoc)

| Element | Where | Why |
|---|---|---|
| Delivery line (`UK home delivery £200–£350 by distance · or collect in Carlisle`) | every card + delivery section | `rules/puppies.md` `delivery-band-on-every-card` |
| Documentation badge stack (L-2-HGA and HC-HSF4 parent test certificates, vet check, microchip, vaccination record) | puppy cards/pages | canonical trust set |
| The licence and statute notice (LICENCE_CLAIM_PLACEHOLDER · LEGAL_CLAIM_PLACEHOLDER) | footer bottom bar | legal |
| Nav, footer, newsletter, global CTA band | site chrome | stripped by the parser already |
| Site-standard section headers | any page | deliberate site furniture — the measured list is below |

> **The header whitelist was measured on BSUK's own `dist/` (Task 15, 2026-09-17)**, not guessed.
> `HEADER_WHITELIST` in `scripts/dup_content_audit.py` now holds exactly:
> Frequently Asked Questions · Get In Touch · Join Our Newsletter · Blue Staffy UK ·
> Quick Pages · Cities We Serve · Blue Staffy News: Join 500+ Readers! ·
> 📬 Get Blue Staffy Updates · Available Blue Staffy Puppies · 🐾 Reserve Your Blue Staffy
> Puppy · Lisa Bright · and the six puppy names Roman, Byrd, Ince, Vennie, Christa, Cheryl
> (sync with `data/puppies.json` when the litter changes).
>
> The match is EXACT on the normalised heading text, not a substring test: the old substring
> match let the one-word entry `contact` whitelist every heading containing it.
> `WHITELIST_SNIPPETS` holds 13 body stems, each one a run measured as shared across 3+ built
> pages and classified as chrome. Location-page prose that repeats across the templated city
> pages is deliberately NOT whitelisted — it is the migrated-content baseline and belongs in
> the report.

**Adding to the whitelist requires breeder approval** — state what, where, and why it must be identical. Everything else that repeats is a defect.

## Triage Rules

| Finding | Action |
|---|---|
| EXACT header crossover | Always rewrite — page-specific conversational framing (the winning pattern from the July purge) |
| TEMPLATE header crossover | Default rewrite. Keep the template ONLY if it's approved site furniture → whitelist it properly |
| Body run ≥12 words | Rewrite on the LOWER-priority page (protect the older/ranking page's indexed copy) |
| Repeated anchor text cross-page | Route to `.claude/skills/internal-link-agent/SKILL.md` Anchor Diversity Ledger |
| Same intent, whole page | Not a rewrite job — cannibalization: route to `@bsuk-site-hygiene-agent` (301 decision) |

**Distribution discipline (prevents dupes at the source):** sibling pages divide shared resources up front — each spoke owns a DISTINCT set of location links, distinct FAQ questions, distinct owner quotes, distinct stats (e.g. one spoke owns Aberdeen/Dundee/Inverness/Edinburgh/Carlisle; another owns London/Birmingham/Manchester/Leeds/Liverpool — all 28 from `data/locations.json`). Write the distribution matrix into the session brief before building spoke #2.

## Common Mistakes
- **De-duping only against the flagship** — duplication is pairwise; spoke #4 must be checked against spokes #1–3 too, and the hub against everything.
- **Running on `src/` instead of `dist/`** — components render shared copy you can't see in source.
- **Whitelisting to make the audit pass** — the whitelist is for mandated-identical elements only, and only with breeder sign-off.
- **Treating a template crossover as "different enough"** — the breeder's standard is page-specific framing; swapped breed names alone do not clear it.
- **Purging after build** — that's the failure this skill exists to prevent. Gate at outline stage.
