---
name: bsuk-perf-gate
description: Use before pushing or releasing any BSUK page, and whenever PageSpeed Insights or Lighthouse reports anything under 100 — Performance, Accessibility, Best Practices, SEO or Agentic Browsing; CLS or layout-shift culprits; unused JavaScript or a missing source map on a first-party path like /70de/; forced reflow; web-font or network-dependency rows; image delivery; contrast. Also when local Lighthouse and PageSpeed disagree. Triggers "check PageSpeed", "score 100", "why is CLS bad", "Lighthouse says", "agentic browsing".
---

# BSUK Perf Gate

> **Release-guarded.** BSUK has no host and no domain: `--live` and `--psi` refuse on the
> `SITE_URL_PLACEHOLDER` host without `BSUK_RELEASE=1`, and the live half of this gate is
> **inactive until project 6**. Until then `dist/` is the whole measurement, and a page is
> "done" on the local floors below — never on a PSI number nobody can produce yet.

**Done, from project 6 onward = PageSpeed Insights reads 100 in all five categories
(Performance, Accessibility, Best Practices, SEO, Agentic Browsing), mobile AND desktop,
on the live URL.** A local run finds defects; PSI judges. Never tell the breeder a page is
done on a local number once PSI is available.

## Run it

```bash
npx astro build
python3 scripts/perf_audit.py <slug>                     # desktop, dist/, 5 runs
python3 scripts/perf_audit.py <slug> --mobile            # mobile, dist/, 5 runs
python3 scripts/perf_audit.py <slug> --live --mobile     # project 6 only: edge injections
python3 scripts/perf_audit.py <slug> --psi --mobile      # project 6 only: THE record
python3 scripts/perf_audit.py <slug> --psi               # project 6 only, desktop
```

Five runs is the default. Run 1 is cold and is never judged: the verdict is the **warm
median of runs 2–5**, printed with the spread of those runs and the cold run beside it. A
CLS verdict (warm median at or under 0.1) is given only on five or more runs — on fewer,
the output says `no CLS verdict` and the record carries `"verdict": null`.

Every floor is 0.995 (what PSI displays as 100). Lighthouse is pinned to 13.4.1 with
`scripts/lighthouse/agentic-*.mjs`. `--preset=desktop` is ignored alongside a config path,
so desktop has its own config. Records land under `data/quality/` (the perf sub-directory is created on first run);
`python3 scripts/board_gate.py <slug> --release` FAILs without fresh local records, and (from
project 6) on any PSI record under 100. `scripts/pageboard.py` is the board library it reads
through, not a command — it has no argv dispatch, so never try to run it with a sub-command.

## Why local and PSI disagree (check these before theorising)

| Local says | PSI says | Real cause | How to see it |
|---|---|---|---|
| CLS 0 | CLS 0.2+ on a hero element | a box that only reaches full size when its image arrives; locally the preloaded image lands before first paint | `layout-image-box-reserved` (render harness), or delay images in headless Chrome |
| no `/70de/` | 79 KiB unused JS, forced reflow, missing source map on `/70de/` | **the edge host (chosen in project 6) Google tag gateway** injecting gtag.js at the edge; dist/ never contains it | `perf_audit.py --live` → `EDGE-INJECTED` |
| fonts self-hosted from `public/fonts/` | `/cf-fonts/...woff2` rows | the edge host (chosen in project 6) Fonts rewriting a Google Fonts link | same `--live` list |
| mobile Performance ~60 | 90s | this Mac's CPU benchmark (~490) under 4× throttle | judge mobile Performance only on `--psi` |

**When CLS disagrees, delay one resource class at a time** (images, fonts, CSS, JS) and
record which element moves. Lighthouse's "Web font" attribution is often a coincident
swap, not the cause: on 2026-09-13 fonts measured 0.02, images reproduced 0.156 of PSI's 0.153.

## Edge features are not code

`/70de/` is gtag.js, not Rocket Loader. The Google tag gateway is a zone switch that
overrides the page's own tag, and Configuration Rules cannot disable it. Fix: the edge host (chosen in project 6) →
Tag Management → Google Tag Gateway → off, then Caching → Purge Everything. GA keeps
working through BaseLayout's interaction-deferred loader. Never "leave it": an injected
script FAILs `--live`. Changing the dashboard is the breeder's action — ask, don't assume.

## Fix bank

| Row | Fix on this site |
|---|---|
| layout shift on a hero/grid item | give the shrink-wrapped box a definite width (`width:100%` beside `margin-left:auto` on a grid item); `aspect-ratio` alone does not help when the WIDTH changes |
| image `<img>` without reserved box | `width`/`height` attrs + `aspect-ratio`; `scripts/final_page_audit.py` `img_dims` |
| web-font swap shift | fallback faces are generated — the font-fallback metrics script was not ported — source repo only; regenerate fallback faces from the Arial/Times bases rather than hand-tuning |
| `uses-responsive-images` desktop | add a candidate within ~10% of the measured slot (hero slot 520–540px → `-560.webp`), in BOTH the `<img srcset>` and `heroPreloadSrcset` |
| LCP discovery | `heroPreload` + `heroPreloadSrcset` + `fetchpriority="high"` on the LCP image only |
| `color-contrast` | measure the ratio, add the missing page-scoped override (`reference_markup_css_drift`) |
| `unused-css-rules` | class-diff with `scripts/page_hardening_scan.py`, triage, never bulk-delete |

## Red flags — stop

- "PSI is just confirmation" → PSI is the record; dist/ is a pre-check.
- "Local CLS is 0, so PSI's number is noise" → delay images first.
- "Performance ≥ 95 is the floor" → the floor is 100.
- "It's Rocket Loader, never chase it" → it was the tag gateway; `--live` names it.
- "Lighthouse blamed the web font, so fix fonts / add min-height" → measure which class moves.
- A gate that reports PASS: read its examined count (`.claude/skills/bsuk-gate-integrity/SKILL.md`).
