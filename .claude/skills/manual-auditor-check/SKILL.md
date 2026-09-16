---
name: manual-auditor-check
description: Use when a page or batch of pages is "done" and needs a final QA pass before you give it a pass / deploy — the last gate after a build, rebuild, or polish rollout. Runs the mechanical 29-check auditor over dist/, then a copy-paste manual checklist for the subjective items. Use when you want a reproducible pass/fail scorecard instead of eyeballing, or when verifying an interior/informational page batch.
allowed-tools: [Read, Write, Bash]
---

# Manual Auditor Check — Final QA Gate

## Overview
The last gate before a page batch ships. Two halves: a **mechanical auditor** (`scripts/interior_29_audit.py`) that scores the objective checks over rendered `dist/` HTML in <1s, and a **copy-paste manual checklist** for the ~6 subjective items a script can't judge (voice, humor, Flesch, non-commodity detail, tone, brand-protocol naming). Distilled from the 29-check final-QA pass (`sessions/2026-06-14-interior-29-check-audit.md`).

**Core principle:** *Never report a machine "fail" as a defect until you've checked it against real `dist/` output.* On its first run this auditor produced **31 false positives**; all 4 root causes are baked in below. Verify, then triage.

## When to Use
- A new/rebuilt/polished interior or informational page (or batch) is finished and you're about to "give it a pass" or push.
- After any `@cag-batch-rebuilder`, polish rollout, or large content edit.
- You want a **reproducible scorecard**, not a vibe check.
- **NOT for:** comparison / location / "…for-sale" money pages / blog posts (own structure) — same exclusions as `MANUAL INTERIOR-PAGE CHECKLIST.md`.

## Quick Start (mechanical half)
```bash
npx astro build                       # MUST build first — auditor reads dist/, source greps lie
python3 scripts/interior_29_audit.py  # per-page blocks + a "CHECK ROLL-UP" of who fails each check
```
Edit the `SLUGS` list at the top of the script to point at the pages you're auditing.

## The 4 False-Positive Traps (DO NOT fabricate these as defects)
The auditor's heuristics were hardened against these — but if you ever hand-audit or extend it, they bite again:

| Looks like a fail | Why it's usually fine |
|---|---|
| **`has_org` missing** | `Organization` is valid when nested as `Article.publisher`/`author`, and `@type` can be a **list** `["LocalBusiness","PetStore"]`. Recurse + handle lists before flagging. |
| **non-hero image is `eager`** | Index 0 is the **header logo**; the eager image right after it is the correct **LCP hero**. Detect the hero by excluding `logo` srcs, not by position 0. |
| **phone number in body** | Third-party **authority hotlines** (USDA APHIS `(844) 820-2234`, FTC) are intentional. Rule 61 bans only the **breeder's** number. |
| **CITES/USDA not in first 300 words** | Astro renders inline JSON-LD *inside* `<main>` — **strip `<script>` before measuring** visible words, or the schema text poisons the count. |

## Triage Legend (label every `✗`)
- **REAL** → fix now (e.g. alt >190, missing visible "Updated" stamp).
- **ACCEPTED** → correct for the page type (e.g. contact/privacy have no H4/Organization; utility pages exempt from the CITES-early + lifespan rules).
- **FALSE POSITIVE** → an auditor heuristic flaw (see table above).
- **NET-NEW / BY-DESIGN** → a new requirement or a scoped decision (e.g. newsletter = long pillars only; not every page).

## Subjective Spot-Check (sample 3 pages: 1 transactional, 1 pillar, 1 trust)
A script can't judge these — read them:
1. **First-person voice** — `grep -ioE "\b(we|our|us)\b" dist/<slug>/index.html | wc -l` should dwarf "African Greys are…" filler. (Live baseline: price 71, reviews 63 = strong; care-guide 33 + 5 filler = sharpen.)
2. **Honesty-Policy humor** — ≤1 dry beat/section, never on legal/health.
3. **Flesch 60–70** (target; floor ~55 for entity-dense copy — don't gut density to chase it).
4. **Non-commodity detail** — ≥1 high-resolution breeder fact per ~500 words; kill generic filler.
5. **Tone** — warm, professional, empathetic.
6. **Brand-protocol naming** — the named house method ("the C.A.Gs Grey Method") used where hand-rearing is discussed.

## Copy-Paste Manual Checklist
> Paste this block anywhere (a fresh chat, a PR comment, a doc) to run the gate by hand. Tick every box; a page isn't "done" until the REAL items pass.

```text
MANUAL AUDITOR CHECK — <page slug>            Updated: <Month Year>
RUN FIRST: npx astro build  →  python3 scripts/interior_29_audit.py

STRUCTURE
[ ] H1 ×1 exactly; H1–H4 all present; no level skips (utility pages may lack H4 — ACCEPTED)
[ ] Exactly ONE FAQPage in dist/; JSON-LD parses valid
[ ] BreadcrumbList present; Organization present (top-level OR nested as Article.publisher)
[ ] Canonical is absolute (https://…)

META + IMAGES
[ ] Title ≤275 · description ≤300 (long-format standard); brand in title
[ ] Every image alt ≤190 chars AND unique per page
[ ] Non-hero images loading="lazy"; LCP hero stays eager (header logo is NOT the hero)
[ ] Every <img> has explicit width/height (CLS); delivered <100KB

COMPLIANCE COPY (content pages; contact/privacy exempt)
[ ] CITES Appendix I + captive-bred + USDA/AWA in the first 300 VISIBLE words (strip JSON-LD)
[ ] 40–60 year lifespan referenced at least once

CONVERSION + FRESHNESS
[ ] Footer phone present; NO breeder phone in body (authority hotlines OK)
[ ] NO visible date anywhere (no "Updated <Month Year>" / "Last updated"); freshness lives ONLY in schema dateModified
[ ] Newsletter top/middle/bottom — long content pillars only (skip thin/utility pages)

A11Y / GOTCHA TRAPS
[ ] No <svg> inside CSS content:  · no escaped &lt;svg in dist  · no 🦜  · no user-select:none
[ ] External links: new tab + rel="noopener noreferrer" + ↗; no bare "click here" anchors

SUBJECTIVE (read 3 sample pages)
[ ] First-person "we/our/here at C.A.Gs" voice >> third-person filler
[ ] ≤1 Honesty-Policy humor beat/section; none on legal/health
[ ] Flesch 60–70 (floor ~55 for entity-dense pages)
[ ] ≥1 high-resolution breeder detail / ~500 words; no "both make exceptional companions" filler
[ ] Named house method ("the C.A.Gs Grey Method") used where hand-rearing is discussed

TRIAGE every ✗ as: REAL (fix) · ACCEPTED (page-type) · FALSE POSITIVE (heuristic) · NET-NEW/BY-DESIGN
```

## Common Mistakes
- **Auditing source greps instead of `dist/`** — `<Schema>` components hide JSON-LD from source; always build first.
- **Reporting the roll-up verbatim** — the roll-up flags ALL pages; utility pages (contact/privacy) are exempt from several checks by design. Triage before quoting.
- **Chasing Flesch 60–70 as a hard gate** — it fights entity density; treat ~55 as the floor.

## Workflow Placement
Runs in **Sprint 4 — Technical Hardening**, as the FINAL step (after `cag-accessibility-fixer` → `cag-performance-fixer` → `cag-canonical-fixer` → `cag-footer-standardizer`), and immediately before the Sprint 4 Gate / Sprint 5 deploy. Companion to `MANUAL INTERIOR-PAGE CHECKLIST.md` Part N (Final QA Gate) and `cag-website-health` (whole-site sweep). Invoke via the Skill tool, or run the two commands by hand.
