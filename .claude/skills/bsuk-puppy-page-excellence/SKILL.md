---
name: bsuk-puppy-page-excellence
description: Use when polishing, differentiating, or doing perf/SEO/schema/a11y QA on an individual /available-puppies/<slug>/ page or the /available-puppies/ hub at BlueStaffyUK — especially when two pups risk cannibalising each other (same colour, or same sex and price), when PageSpeed/Lighthouse flags oversized images, render-blocking CSS, LCP or contrast, when Search Console flags a Product rich-result error, or when distributing location pages across puppy pages.
allowed-tools: [Read, Write, Bash]
---

# BSUK Puppy-Page Excellence (re-based for BlueStaffyUK, 2026-09-30)

Re-based from the source repo's listing-page polish skill. The **method is the source's** —
differentiate every layer at once, verify in `dist/`, fix with banked patterns — and every
fact is BSUK's own, read from data rather than typed here.

## Overview

The build-and-polish method for the puppy cluster: the six `/available-puppies/<slug>/` pages
(`src/pages/available-puppies/[slug].astro`, data-driven from `data/puppies.json`) and the
`/available-puppies/` hub. **Core principle: every layer of a puppy page — H1, `<title>`,
meta, image alt, schema, geo block, FAQ — tells ONE differentiated story that no other puppy
page duplicates.** Two pups that differ only by name will cannibalise each other; the fix is
to differentiate on a real buyer axis that the data records, across all layers at once.

This is a **technique/reference skill**. It complements — does not replace —
`.claude/skills/bsuk-puppy-page-builder/SKILL.md` (the builder; `rules/puppies.md` carries its
rules) and `.claude/skills/bsuk-final-page-pass/SKILL.md` (the mechanical gate). No page is
touched without an approved board: `python3 scripts/board_gate.py <slug>`.

## When to Use

- Two or more puppy pages read identical-minus-name in H1 / title / meta / alt.
- PageSpeed or Lighthouse flags oversized images, LCP, render-blocking CSS, or contrast.
- Search Console flags a **Product** rich-result critical or non-critical error.
- You need to distribute real location pages across puppy pages as delivery-destination blocks.
- A keyword / entity / voice self-audit or competitor benchmark of the cluster.

**When NOT to use:** building a puppy page from nothing, or any buy-prefixed page (use
`bsuk-puppy-page-builder`); location / comparison / blog pages (their own builders).

## The Non-Negotiables (carry into every task)

1. **Project branch, commit after every task, never push** (working rules 2–3). There is no
   remote, host or deploy until project 6; a commit is the finish line, not a deploy.
2. **Verify in `dist/`, not source** — the pages are generated from data; grep the built HTML
   after `npm run -s build`.
3. **Real routes only** — link a location page only when its slug is in `data/locations.json`
   and `dist/uk-locations/<slug>/index.html` exists. Never invent a slug.
4. **Truthful Product + Offer only** — one `Product` with exactly one `Offer` per pup
   (`rules/puppies.md` `product-schema-per-pup`), `availability` read from the pup's `status`.
   **Never** `AggregateRating` or `Review` (`docs/reference/seo-rules.md` Rule 33, working rule 9).
5. **Facts from data, never typed.** Names, sex, colour, status and photos from
   `data/puppies.json`; prices and the deposit from `data/price-matrix.json`;
   the delivery band from `data/settings.json` — delivery £200–£350 by distance via
   DEFRA-approved transport, or collection in Carlisle. The guarantee (`guarantee_days`) only as
   `guarantee_label`, plus `guarantee_cover` (`guarantee_days`) where a guarantee sentence carries it.
   Any licence claim is `LICENCE_CLAIM_PLACEHOLDER`, any statute claim
   `LEGAL_CLAIM_PLACEHOLDER`. A health test may be **named**, never given a result or a
   certificate that no file records. No invented rearing-method labels. Phone is
   `PHONE_PLACEHOLDER`, the site URL `SITE_URL_PLACEHOLDER`.
6. **First-person voice as Lisa Bright** ("here at BlueStaffyUK, our…, we raise…"); neutral
   register only for breed facts and cited research.
7. **Heading gate** — all six levels, **min 5 H5 + 5 H6**, no skipped level, Title Case
   (`rules/headings.md`). Present the H1→H6 outline before changing the hierarchy.
8. **Images and videos keep their URLs** (working rules 11, 14) — never rename, delete or
   re-encode a served file; YouTube ids from `data/settings.json` `youtube_embeds` keep their id.

## Quick Reference — the differentiation matrix

The source split same-sex animals on life-stage. **BSUK cannot**: the six pups are one litter
at one age, and `data/puppies.json` records no birth date, age, weight or temperament. The
fields it does record are `sex`, `colour`, `price_gbp` and `status`, and price is not an
independent axis — it follows sex (`male_gbp` / `female_gbp`). So the real axes are:

- **Within a sex, colour** separates every pup (each sex has three distinct colours).
- **Across sexes, colour repeats in two pairs** — the pairs split on **sex** (and the price
  tier that goes with it), never on an invented trait.

| Pair that collides on colour | Colour (data) | Split on |
|---|---|---|
| Roman / Vennie | Blue and white | male at the `male_gbp` tier / female at the `female_gbp` tier |
| Ince / Christa | Blue | male / female, same |
| Christa / Cheryl | Blue / Blue with white blaze | the **white blaze** marking — put it in H1, title, meta and alt |

Propagate the axis through every layer at once: H1, `<title>`, meta description, image alt,
Product `description`, geo H3, and the FAQ. Keep the **"Staffordshire Bull Terrier"** and
**"Blue Staffy"** entities in H1/title/meta.

**The gap, named:** there is no second axis in data beyond colour and sex. A temperament,
age-at-homing or personality axis needs the breeder's answer on the answer board first
(working rule 7: one narrow question, keep building). Until then, never write a personality
line that no file records.

## Quick Reference — the proven fixes

| Defect | Fix | Verify |
|---|---|---|
| Oversized image | **Add a smaller sibling** beside the served file (the site's `-760` / `-card-800` convention under `public/images/puppies/`), shrink-only, never upscale; point `srcset`/`sizes` at it. **Never re-encode, rename or overwrite the served file** (rule 11). Photos served through `astro:assets` are bounded by `widths=`, not by re-encoding. | `git diff --stat public/images/` shows only additions; `ls -la dist/…/*.webp` |
| LCP on the portrait | The hero portrait is `loading="eager" fetchpriority="high"`; everything below the fold is `loading="lazy"`. | `grep -o 'fetchpriority="high"' dist/available-puppies/<slug>/index.html` = 1 |
| Render-blocking / unused CSS or JS | Remove a shared component only after confirming every page that uses it has a replacement (the kit's `PageNav` / `PageDial` are the ToC here). | `grep -rl <component> dist/` before and after |
| AA contrast | Use only pairs listed in `data/design/contrast.json` (asserted by `tests/py/test_design_tokens.py`); add the pair before using it. Brass `--color-cta` on bone is ~2.1:1 — never small text; on `--color-surface-inverse` it is a `large`-only pair (~4.9:1). Small text on dark bands is `--color-text-on-inverse` or `--color-link-on-inverse` (~9:1). No opacity modifiers on small text; no hex outside `src/styles/tokens.css`. | contrast snippet below ≥ 4.5 |
| Product rich-result error | Add only truthful `Offer` fields: `shippingDetails` built from the settings delivery band, `hasMerchantReturnPolicy` only once the breeder's terms exist. No reviews, no ratings, no `priceValidUntil` date nobody set. | JSON-LD parses in `dist/`; Rich Results Test is a **human-browser** step |
| Geo distribution | One **distinct set of real routes + unique H3** per puppy page; same-tab internal links. | every href resolves in `dist/`; 0 `target="_blank"` on geo links |
| Duplicate alts across pages | Inject the pup's own axis (colour / marking / sex) into each alt; keep alt ≤190 chars; a photo shown twice on one page gets a new alt on the repeat. | shared-pattern grep → 0 pages |

## Implementation — the verification commands

```bash
npm run -s build

# Every location href on a puppy page must be a real, built route
for s in $(grep -rhoE 'href="/uk-locations/[a-z0-9-]+/"' dist/available-puppies/ \
  | sed 's|href="/uk-locations/||;s|/"||' | sort -u); do
  test -f "dist/uk-locations/$s/index.html" && echo "OK $s" || echo "MISSING $s"
done

# BEFORE any deletion — confirm zero live references (reality can contradict the plan)
grep -rln "<file>" src/ public/ data/ || echo "no refs → safe"

# Distinct H1s — two pups must not be identical-minus-name
a=$(grep -oE '<h1[^>]*>[^<]*' dist/available-puppies/ince/index.html | sed 's/Ince//')
b=$(grep -oE '<h1[^>]*>[^<]*' dist/available-puppies/christa/index.html | sed 's/Christa//')
[ "$a" != "$b" ] && echo DISTINCT || echo "STILL PARALLEL"

# alt > 190 chars
python3 -c "import re,sys;[print(len(a),a) for a in re.findall(r'alt=\"([^\"]*)\"',open(sys.argv[1]).read()) if len(a)>190]" dist/available-puppies/roman/index.html

# AA contrast ratio for a token pair
python3 - <<'PY'
def lin(c):
    c/=255; return c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
def L(h): r,g,b=(int(h[i:i+2],16) for i in (1,3,5)); return 0.2126*lin(r)+0.7152*lin(g)+0.0722*lin(b)
def ratio(a,b): la,lb=L(a),L(b); return (max(la,lb)+0.05)/(min(la,lb)+0.05)
print(round(ratio('#EFE3B4','#1F3A52'),2))   # link-on-inverse on surface-inverse; want >=4.5
PY

# Final gates
python3 scripts/final_page_audit.py --puppies   # want 0 FAIL
npm run sitemaps && npm run -s check:sitemaps
```

## Common Mistakes (universal lessons, carried from the source)

| Mistake | What goes wrong | Fix / rule |
|---|---|---|
| **Deleting without grep** | A file a plan called unreferenced was live on many pages. | `grep -rln` first; restore with `git checkout -- <path>` if referenced. |
| **Blind-deleting a shared component** | A component safe to drop on one page family is the only ToC on another. | Confirm a replacement exists on every page that uses it. |
| **Identical headers across siblings** | H1s identical minus the name → cannibalisation. | Differentiate on the data's axis across H1+title+meta+alt at once. |
| **Cross-page duplicate alts** | Alt/title pairs identical minus the name. | De-dup per page with the pup's own axis; ≤190 chars. |
| **Grepping source, trusting loose patterns** | A loose grep matches the wrong block; a wrapper's error hides sound work. | Verify in `dist/` with precise patterns; read the gate's examined count. |
| **Claiming a link or result you couldn't fetch** | Some hosts and Google's Rich Results Test refuse automated agents. | Mark it a **human-browser** step; never claim a 200 you did not get. |
| **A resize that upscales, or overwrites** | An upscaled re-encode grows the file; an overwrite breaks a ranking URL. | Shrink-only guard; write a new sibling, never replace the served file. |
| **Inventing the differentiator** | A personality or age line no file records is a fabricated claim. | Use colour / marking / sex from data; ask the breeder for anything else. |

## Related

- `.claude/skills/bsuk-puppy-page-builder/SKILL.md` — the builder; `rules/puppies.md` — its rules.
- `.claude/skills/bsuk-final-page-pass/SKILL.md` — the gate (`scripts/final_page_audit.py --puppies`).
- `.claude/skills/bsuk-page-hardening/SKILL.md`, `.claude/skills/bsuk-perf-gate/SKILL.md` — UI and perf fixes.
- `.claude/skills/bsuk-duplicate-content-gate/SKILL.md` — sibling crossover.
- `.claude/skills/bsuk-photo-ingest/SKILL.md` — adding a new image beside a served one.
