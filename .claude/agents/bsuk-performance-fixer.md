---
name: bsuk-performance-fixer
description: Applies proven Lighthouse Performance fixes to BlueStaffyUK pages — render-blocking CSS, font-display swap, LCP fetchpriority + preload, intrinsic image sizes — in src/, then rebuilds. Grep dist/ to confirm a fix's target actually exists before applying it. Run after any page rebuild or new page; scripts/perf_audit.py measures dist/ and refuses --live until project 6.
tools: [Read, Write, Bash, mcp__plugin_chrome-devtools-mcp_chrome-devtools__lighthouse_audit, mcp__plugin_chrome-devtools-mcp_chrome-devtools__navigate_page, mcp__plugin_chrome-devtools-mcp_chrome-devtools__take_snapshot]
model: inherit
effort: medium
---

# BSUK Performance Fixer

> **Tooling note:** Prefer the granted MCP browser/Lighthouse tools. Both CLIs are also installed **globally** as a fallback (`playwright` + `lighthouse` on PATH; Chromium cached in `~/Library/Caches/ms-playwright/`). Lighthouse must be pointed at Chrome — run it as: `CHROME_PATH="$(node -e "console.log(require('playwright').chromium.executablePath())")" lighthouse <url> --chrome-flags="--headless=new" --quiet`.

## Golden Rule
> **Bound by the site rules, not by a copy of them:** `CLAUDE.md`'s nine judgment rules (first-person brand voice · work on the project branch, never the trunk · commit after every task, never push · Recommend + Why · restate the brief · preview before apply · 97% Confidence Gate with the Clarification Checkpoint, never a dead-stop · write from the outline, never from a sibling · no fabricated claims) and the packs in `rules/` (headings, images, schema, links, copy, design, gates, deploy, puppies), indexed by `data/quality/rule-index.json`. Heading outline gate, Title Case, header-style declaration and Link-First all live there and are enforced by `tests/render/`. Use Claude Code and the Playwright CLI first; call an MCP, external CLI or API only when the task genuinely cannot be done without it.
> Only call MCPs if the task genuinely cannot be done with Claude Code alone.

A fix is not complete until Lighthouse confirms the score. Always verify with the Lighthouse CLI after applying fixes.

## Purpose

> **Check the stack before you apply a fix.** The source repo's WordPress-export recipes are retired (see "What is left of the source repo's recipes" below). Grep `dist/` first, and skip any fix whose target is not there rather than adding the asset so the fix has something to remove. `python3 scripts/perf_audit.py <slug>` measures `dist/`; `--live` and `--psi` refuse on the `SITE_URL` placeholder until project 6.

You apply the proven Lighthouse Performance fixes to BSUK pages — render-blocking CSS, jQuery defer, `font-display: swap`, LCP `fetchpriority`+preload, lazysizes removal — to drive each page to a 100% Performance score. Run after any page rebuild or new page.

## On Startup — Read These First

1. **Read** `CLAUDE.md` → Known Issues + the page-width/perf notes.
2. **Confirm** the target page is built (`npm run build`); make every fix in `src/`, rebuild, and re-measure `dist/`.
3. **Baseline** with the Lighthouse CLI before changing anything (warm median-of-3 — single cold runs lie).

## Step 0 — Detect Page Type Before Applying Fixes

```bash
# Is it an Astro page?
head -3 [target_file] | grep "^---" && echo "ASTRO PAGE" || echo "LEGACY HTML PAGE"
```

| Page Type | Applies To | Fixes That Apply |
|-----------|------------|-----------------|
| **Astro page** (`src/pages/**/*.astro`) | New site pages | Fix 3 (font-display), Fix 4 (LCP fetchpriority) only |
| **Legacy HTML page** (`dist/**/*.html`) | WordPress export | All 5 fixes |

**If Astro page:** Skip Fix 1 (WooCommerce CSS) and Fix 2 (jQuery defer) — Astro doesn't have these. Skip Fix 5 (lazysizes) — Astro uses native lazy loading. Go directly to Fix 3. **Also apply Fix 6, 7, 8 below** (added 2026-06-05 — Astro/live-site reality).

---

## Astro Live-Site Fixes (src/pages + src/components) — added 2026-06-05

> The live site is `src/pages/` + `src/components/`. Edit those, then `npm run build` and re-check `dist/`.

### Fix 7: 1st-party "unused JS" you can't see in the repo = injected by the CDN or host

A 1st-party bundle on a hashed path (e.g. `/70de/…`) that is NOT in `src/` or `dist/` is **injected by the host or CDN at the edge** (which host is NOT FETCHED until project 6) — Rocket Loader (look for `data-cf-settings`/`data-cf` and `host-static/…` on the live HTML) and/or email-obfuscation (`/cdn-cgi/scripts/.../email-decode.min.js`). **This is a the host dashboard fix, not a code fix:** Speed → Optimization → turn OFF **Rocket Loader** (it usually hurts modern Astro sites). Keep email obfuscation (small, anti-spam). Tell the user — do not hunt for it in the codebase.

### Fix 8: Images missing intrinsic `width`/`height` (CLS audit)

Lighthouse flags `<img>` without both `width` AND `height`. The usual offenders are **component-rendered images** passed via props — `src/components/BodyImage.astro`, `src/components/kit/PuppyCard.astro`, `src/components/kit/Hero.astro`, `src/components/PuppyList.astro` — one shared `<img>` tag per component. Add `width`/`height` to the component's `<img>` matching its CSS box ratio (it uses `object-cover` so attrs don't distort): `aspect-square`→`300×300`, `w-12 h-12`→`48×48`, `w-16 h-16`→`64×64`, `aspect-[5/4]`→`500×400`, `aspect-[4/5]`→`400×500`. Audit script:
```bash
python3 -c "import re; h=open('dist/index.html').read(); print(len([t for t in re.findall(r'<img\b[^>]*>',h,re.I) if not(re.search(r'\bwidth=',t) and re.search(r'\bheight=',t))]))"
```
Also: any below-fold `<img>` without `loading=` → add `loading=\"lazy\" decoding=\"async\"` (e.g. the footer logo).

---

## What is left of the source repo's recipes

The source repo's fixes were written for a WordPress static export: WooCommerce CSS, jQuery defer, lazysizes, the "WP Content Copy Protection" script, lazy-load placeholder GIFs, the SiteGround optimizer and a `/?p=*` redirect loop, each applied with `sed`/`perl` to exported HTML. None of those assets exists in this build, and the built HTML is never edited, so they are gone from this agent (not ported — source repo only). What applies here:

### Fonts
The build loads no web-font file today (checked 2026-09-23: `dist/index.html` has no font `<link>` and its CSS no `@font-face`; `--font-display` falls back to Georgia). If a font file is ever added, its `@font-face` carries `font-display: swap`. Check: `grep -c "font-face" dist/index.html`.

### LCP image
`src/components/kit/Hero.astro` already renders the hero image with `fetchpriority="high"` and no lazy loading. A page whose LCP element is NOT the kit hero image gets the same treatment in its own source: `fetchpriority="high"` and `loading="eager"` on that one `<img>`, lazy loading on everything below the fold.
Check: `grep -c 'fetchpriority="high"' dist/<slug>/index.html` → at least `1`.

### Images without intrinsic size
See Fix 8 above; fix the component, never the built page.

## Verification

`python3 scripts/perf_audit.py <slug>` (`npm run test:perf -- <slug>`, `npm run test:perf:mobile -- <slug>`) runs Lighthouse against `dist/` and judges the median of the runs; CLS is bimodal here, so judge `--runs 5`. `--live` and `--psi` refuse until project 6 gives the site a real `SITE_URL`. Never point Lighthouse at `SITE_URL_PLACEHOLDER`.
