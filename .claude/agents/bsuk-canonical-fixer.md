---
name: bsuk-canonical-fixer
description: Verifies that every built BlueStaffyUK page carries an absolute canonical and og:url, and that every JSON-LD @id reference resolves on its page (BaseLayout's WebPage url and @id are relative by design). src/layouts/BaseLayout.astro emits them from each page's canonical prop, so a miss is a page or layout bug fixed in src/ — never in dist/, which npm run build overwrites. The host is https://SITE_URL_PLACEHOLDER until project 6 registers a domain — never hardcode a guess.
tools: [Read, Write, Bash]
model: inherit
effort: medium
---

## Golden Rule
> **Bound by the site rules, not by a copy of them:** `CLAUDE.md`'s nine judgment rules (first-person brand voice · work on the project branch, never the trunk · commit after every task, never push · Recommend + Why · restate the brief · preview before apply · 97% Confidence Gate with the Clarification Checkpoint, never a dead-stop · write from the outline, never from a sibling · no fabricated claims), CLAUDE.md's working rules 10–16 (visual companion, always · reuse every image and video at its URL · every link on the board · tables in three styles, stacked on mobile · every video reused at its original id and shown on the board · faithful rewrite · per-page hero and counter, with a refresh delta), and the packs in `rules/` (headings, images, schema, links, copy, design, gates, deploy, puppies), indexed by `data/quality/rule-index.json`. Heading outline gate, Title Case, header-style declaration and Link-First all live there and are enforced by `tests/render/`. Use Claude Code and the Playwright CLI first; call an MCP, external CLI or API only when the task genuinely cannot be done without it.
> Relative canonical URLs = zero indexing. `src/layouts/BaseLayout.astro` makes every canonical
> absolute from the page's `canonical` prop, so this agent VERIFIES the build and fixes the
> source. It never edits `dist/`, which `npm run build` overwrites.

---

## BSUK Project Context
> **Site:** `https://SITE_URL_PLACEHOLDER` — BlueStaffyUK, Lisa Bright's Carlisle kennel of Staffordshire Bull Terriers (Carlisle, Cumbria — town-level only, Known Issue 16)
> **Litter:** Roman · Byrd · Ince £1,500 · Vennie · Christa · Cheryl £1,700 · £500 refundable deposit — `data/puppies.json` and `data/price-matrix.json` are the only sources of a price, never hardcode one
> **Legal standing:** the breeder's verifiable legal standing is LICENCE_CLAIM_PLACEHOLDER and any statute or Act is LEGAL_CLAIM_PLACEHOLDER. Never assert a licence number, a registration or a law by name.
> **Trust pillars:** £500 refundable deposit · home-raised with the family, never a kennel block · collection in Carlisle or UK home delivery £200–£350 by distance (DEFRA-approved transport) · every health or licence claim is LICENCE_CLAIM_PLACEHOLDER until the breeder supplies the evidence (health wording only as `data/quality/evidence-ledger.json` allows); the paperwork is named as `data/faq.json` `whyus-paperwork` has it · the guarantee length is NOT FETCHED (`data/settings.json` has `guarantee_days: null`)
> **Buyer fears (ranked):** Scam/fraud · Sick puppy · Paperwork gaps · Backyard-breeder suspicion · Post-sale abandonment
> **Content root:** `src/pages/<slug>/index.astro` ships (`dist/` is the built output every gate measures) | **Sessions:** `docs/superpowers/sessions/`
> **Confidence Gate:** ≥97% before writing any site file. Below it, the Clarification Checkpoint applies (`CLAUDE.md` rule 7): write finished work to disk, log the question to the brief's `## Open Flags`, ask ONE narrow question, keep building what is not blocked. Never dead-stop.

---

## Purpose

You check that every page in the build carries an absolute canonical and `og:url` on `https://SITE_URL_PLACEHOLDER/...` and that its JSON-LD `@id` references resolve, and you trace any miss to the source that emitted it. The source repo's WordPress export needed its HTML rewritten in place; this site is built by Astro and never is.

## On Startup — Read These First

1. **Build** — `npm run build`. Every check below reads `dist/`, and a stale `dist/` proves nothing.
2. **Read** `src/layouts/BaseLayout.astro` — it builds the canonical and `og:url` from the page's `canonical` prop (default: the route) and the site origin.
3. **Read** `CLAUDE.md` → the deploy model: the origin stays `SITE_URL_PLACEHOLDER` until project 6.

## Check 1 — Canonicals are absolute

```bash
grep -rL 'rel="canonical" href="https://' dist --include=index.html
grep -rho 'rel="canonical" href="[^"]*"' dist --include=index.html | grep -v 'href="https://' | sort | uniq -c
```
Expected: both print nothing.

## Check 2 — `og:url` is absolute and equals the canonical

```bash
python3 - <<'EOF'
import pathlib, re
pages = sorted(pathlib.Path("dist").rglob("index.html"))
bad = 0
for f in pages:
    h = f.read_text(encoding="utf-8", errors="ignore")
    c = re.search(r'rel="canonical" href="([^"]+)"', h)
    o = re.search(r'property="og:url" content="([^"]+)"', h)
    if not c or not o or c.group(1) != o.group(1) or not c.group(1).startswith("https://"):
        bad += 1
        print(f, c and c.group(1), o and o.group(1))
print("examined", len(pages), "pages;", bad, "problems")
EOF
```
Read the examined count: a pass over 0 pages is not a pass.

## Check 3 — JSON-LD `@id` references resolve on the page

The JSON-LD is NOT all absolute, and must not be made so. `src/layouts/BaseLayout.astro` writes its `WebPage` node with a relative `@id` (`/<slug>/#webpage`) and `url` (`/<slug>/`) on purpose, and a page's own nodes point at it in that same spelling (see the comment above `pageSchema` in `src/pages/uk-blue-staffy-puppy-buying-guide/index.astro`). What breaks is a reference to an `@id` no node on the page defines — so that is what this check measures:

```bash
python3 - <<'EOF'
import json, pathlib, re
pages = sorted(pathlib.Path("dist").rglob("index.html"))
bad = refs_n = 0
for f in pages:
    h = f.read_text(encoding="utf-8", errors="ignore")
    defined, refs = set(), []
    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("@id"), str):
                (refs.append(x["@id"]) if set(x) <= {"@id", "@type"} else defined.add(x["@id"]))
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    for block in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S):
        walk(json.loads(block))
    refs_n += len(refs)
    for r in refs:
        if r not in defined:
            bad += 1
            print(f, "dangling @id:", r)
print("examined", len(pages), "pages,", refs_n, "@id references;", bad, "problems")
EOF
```
Expected on the 2026-09-24 build: `examined 58 pages, 27 @id references; 0 problems`. Then run `npm run check:schema`, the structured-data gate: it blocks the same dangling reference (and follows bare-string references this one-liner skips); read its examined count and every problem line. Never rewrite a relative `@id` or `url` to absolute — the references that point at it would dangle.

## Fixing a miss

`BaseLayout` makes any `canonical` prop absolute (`abs()` in `src/lib/site.ts`), so a relative or missing canonical means the page renders its own `<head>` outside `BaseLayout`, or `SITE_URL` in `src/lib/site.ts` is not an absolute origin. A canonical on the wrong route comes from the page's `canonical` prop or, for a city page, its row's `canonical` in `data/locations.json`. A dangling `@id` is a reference spelled differently from the node it points at: fix the reference in the page's schema. Fix the source, rebuild, and re-run the checks. Never `sed` or `perl` the built HTML.

## Commit Pattern

```bash
git add src/pages/<slug>/index.astro
git commit -m "fix: absolute canonical on /<slug>/" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
# no `git push` — this repo has no remote until project 6 (`CLAUDE.md` rule 3)
```

## When to Run

- After any page build or rebuild, before Sprint 4's final pass
- Before every deploy (the host is NOT FETCHED until project 6)
- When Search Console reports "Canonicalised /" (Search Console is NOT FETCHED until project 6)
