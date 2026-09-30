# Render harness baseline — project 3 (design system)

Captured 2026-09-19 at Task 21, after `npm run build` (51 pages) and all three render gates
run with `PUBLIC_FORMSPREE_ID` exported. It supersedes
`docs/reports/render-baseline-project2.md` as the live baseline; that file is the published
record of the 2026-09-17 run and is not regenerated.

**What changed about the corpus itself:** `src/pages/kit-preview/` is a target page from this
run on, under a new `page_type: "preview"` wired to all nine families, `corpus: false`. It is
the only built page carrying the kit — project 4 does not mount the kit on the real pages
until its build 4 — so it is where the three formerly deferred checks have nodes to examine.
Every kit-preview row below is therefore new by definition, and is listed separately.

## Gate results

| Gate | Command | Result |
|---|---|---|
| Build | `npm run build` | `51 page(s) built` |
| Marker | `python3 scripts/marker_check.py` | `examined 240 files; 0 problems` |
| Parity | `python3 scripts/migration_parity.py` | `examined 40 pages, 0 failing` |
| Sitemaps | `python3 scripts/sitemap_check.py` | `examined 51 built pages, 5 shards, 35 sitemap urls; 0 problems` |
| Form audit | `python3 scripts/form_contract_audit.py` | `examined 2 forms; 0 problems` |
| Meta | `npm run test:render:meta` | 324 passed, 36 skipped — **no `DEFERRED` line** |
| Search | `npm run test:render:search` | 18 passed |
| Pages | `npm run test:render:pages` | 8 passed, 46 failed |
| Scorecard | `node scripts/build_scorecard.mjs --run first` | 261 defect rows across 18 pages (run=first, harness 2.0.0) |

Scorecard output: `data/quality/scorecards/<slug>-2026-09-19.json` (18 files).

The 46 pages-gate failures are the same intended baseline project 2 recorded: Foundation
migrated the WordPress bodies verbatim, so IMG/NAV/SCHEMA rows land on migrated content and
the gate is red until project 4 re-authors them. **No blocking row appeared on any page that
did not already carry it in the 2026-09-17 scorecard**, and kit-preview — the one genuinely
new page — carries none at any of the three viewports.

## Defect rows by family

Rows are comparable across families; instances are not. Severity is the check's own
`severity` field in `tests/render/checks/*.ts` — the scorecard JSON carries none — so a family
can carry both kinds (SEM does). Everything between the generated markers below is produced by
`python3 scripts/render_baseline.py --out docs/reports/render-baseline-project3.md`; `npm run
baseline` fails if it drifts. Do not hand-edit it.

<!-- generated:start -->
Scorecard run 2026-09-19 — 18 page scorecards, 261 defect rows.

| Family | Blocking rows | Advisory rows | Pages affected |
|---|---|---|---|
| A11Y | 0 | 5 | 2 |
| CSS | 0 | 42 | 13 |
| DUP | 0 | 36 | 12 |
| FORM | 0 | 3 | 1 |
| IMG | 6 | 0 | 3 |
| LAYOUT | 4 | 0 | 2 |
| NAV | 18 | 0 | 6 |
| SCHEMA | 21 | 0 | 7 |
| SEM | 9 | 117 | 18 |
| **Total** | **58** | **203** | **18** |

Rows by check: `sem-all-six-levels` 54, `css-class-resolves` 39, `dup-no-sibling-crossover` 36, `sem-title-case-headings` 36, `sem-section-opening-paragraph` 27, `nav-jump-target-lands` 18, `schema-date-modified-present` 18, `sem-heading-order` 9, `img-srcset-within-2x` 6, `a11y-text-contrast-aa` 5, `layout-tap-target-size` 4, `css-no-dead-component-rule` 3, `form-inquiry-contract` 3, `schema-no-visible-date` 3.
<!-- generated:end -->

## Against project 2 (2026-09-17 → 2026-09-19)

| Family | Blocking 09-17 | Blocking 09-19 | Advisory 09-17 | Advisory 09-19 |
|---|---|---|---|---|
| A11Y | 0 | 0 | 3 | 5 |
| CSS | 0 | 0 | 51 | 42 |
| DUP | 0 | 0 | 33 | 36 |
| FORM | 0 | 0 | 3 | 3 |
| IMG | 15 | 6 | 0 | 0 |
| LAYOUT | 4 | 4 | 0 | 0 |
| NAV | 18 | 18 | 0 | 0 |
| SCHEMA | 21 | 21 | 0 | 0 |
| SEM | 9 | 9 | 108 | 117 |
| **Both totals** | **67** | **58** | **198** | **203** |

Per-check deltas (`--compare 2026-09-17`), with kit-preview's own contribution separated out.
kit-preview fires each of its checks once per viewport, so it adds exactly 3 rows per check it
reports on (2 for A11Y, which is silent at one width):

| Check | 09-17 | 09-19 | of which kit-preview | the 17 older pages |
|---|---|---|---|---|
| `img-srcset-within-2x` | 15 | 6 | 0 | 15 → 6 |
| `css-class-resolves` | 51 | 39 | 3 | 51 → 36 |
| `css-no-dead-component-rule` | 0 | 3 | 3 | 0 → 0 |
| `dup-no-sibling-crossover` | 33 | 36 | 3 | 33 → 33 |
| `sem-all-six-levels` | 51 | 54 | 3 | 51 → 51 |
| `sem-title-case-headings` | 33 | 36 | 3 | 33 → 33 |
| `sem-section-opening-paragraph` | 24 | 27 | 3 | 24 → 24 |
| `a11y-text-contrast-aa` | 3 | 5 | 2 | 3 → 3 |
| `form-inquiry-contract` | 3 | 3 | 3 | 3 → 0 |

Read across: on the seventeen pages that existed in both runs, **nothing got worse.** Two
things got better, both from tasks 17–20 rather than from Task 21 — `img-srcset-within-2x`
fell 15 → 6 (nine blocking rows, the whole of the blocking improvement) and
`css-class-resolves` fell 51 → 36 — and the contact page's three `form-inquiry-contract` rows
are gone, so the three that remain are the preview's specimen form and nothing else.

## kit-preview's own rows — new by definition, judged one at a time

23 rows, **0 blocking**, at 375/768/1280.

| Check | Severity | Rows | Judgement |
|---|---|---|---|
| `sem-all-six-levels` | advisory | 3 | **Correct to leave.** The preview has H1:1 H2:6 H3:21 and no H4–H6. It is a board index, not a document; inventing five H5s to satisfy a content rule on a `noindex` specimen would be writing for the checker. |
| `sem-title-case-headings` | advisory | 3 | **Correct to leave.** The offenders are board captions ("1 · Site header + nav") and the demo copy inside the components, which is the components' own copy and is judged on the real pages. |
| `sem-section-opening-paragraph` | advisory | 3 | **Correct to leave.** Four headings run straight into the next heading because the thing between them is a rendered component, not prose. |
| `css-class-resolves` | advisory | 3 | **Partly a kit finding.** `cta` was a dead class left by the prune and is removed in this task. What remains is `kit-mark` and `counter-wrap` — both deliberate harness/query hooks that no rule paints. Worth a decision in project 4: either give them a rule or stop emitting them. |
| `css-no-dead-component-rule` | advisory | 3 | **Expected on a preview.** The three `.results …` rules only match once the search pill has rendered results, which it has not when the page is measured; `.kit-quote-empty` only matches when a review row is the placeholder. |
| `dup-no-sibling-crossover` | advisory | 3 | **Expected, and not worth whitelisting.** The preview renders the real Testimonial reviews, so three passages match the homepage. They are the same words on purpose. |
| `a11y-text-contrast-aa` | advisory | 2 | **A kit finding, small.** A `.dot` separator glyph measures 4.49:1 against 4.5:1 — one hundredth short. It is a decorative middot; project 4 should either darken it one step or mark it `aria-hidden` and non-text. |
| `form-inquiry-contract` | advisory | 3 | **A kit finding.** The preview's `ContactFormKit` puppy select is missing the collection option the contract names (spec §5). The reachable contact page is clean; this is the kit copy of the form, and project 4 should close the gap before it replaces the real one. |

Four defects the first measurement of this page found were **fixed rather than baselined**,
because a blocking row on the preview is a defect in the kit or in the preview, not a number:

1. `nav-anchors-resolve` (blocking) — the `PageNav` demo linked to `#temperament`, `#health`,
   `#exercise`, `#cost`, none of which existed. Every kit-preview section now carries a
   `kit-<component-id>` anchor and the demo names four real ones.
2. `schema-date-modified-present` (blocking) — the preview carried no `dateModified`. It now
   declares a `WebPage` node whose dates come from `data/page-dates.json`, derived from git
   history by `npm run dates`. Never `new Date()`.
3. `layout-no-horizontal-overflow` (blocking) — the demo box is a flex row, and a flex item's
   automatic minimum size is its max-content width, so the three-up `Testimonial` held 816px
   of grid tracks at a 375px viewport and pushed the document 465px sideways. Fixed with
   `min-width: 0` on the demo's children; the component itself is correct in normal flow.
4. `nav-jump-target-lands` (blocking) — the preview mounted a **second** `position: sticky`
   site header, which the chrome probe absorbed into the top band: 75px at 375, 116px at 1280,
   259px at 768, so no single `scroll-margin-top` could land an anchor inside it. That copy is
   now `position: static` on the preview. A page has one set of top chrome, and a 220px board
   box gives a sticky bar nothing to stick to anyway.

## Deferred checks

**None.** `tests/render/targets.json > deferred_checks` is `{}`. The three entries
(`layout-hero-counter-separation`, `layout-h3-image-first`, `sem-statement-label-visible`)
each stated the same promotion condition — remove the entry when the scorecard shows the check
examining more than zero nodes — and each now does, on kit-preview:

| Check | Nodes examined on kit-preview | Rows |
|---|---|---|
| `layout-hero-counter-separation` | 3 | 0 |
| `layout-h3-image-first` | 3 | 0 |
| `sem-statement-label-visible` | 6 | 0 |

`layout-h3-image-first` needed a subject that did not exist: the picked `InfoCard` owns no
`.sec-img`, because the image-top treatment was one of the five the prune dropped. The preview
therefore carries one extra section — an `<h3>` owning an `<Image class="sec-img">` above a
`<p class="prose">` — labelled as the convention specimen and carrying no `data-component`, so
neither the measurer nor the artboard builder sees it.

Guard 2 in `build_scorecard.mjs` now judges all three like every other check: the run above
printed no `DEFERRED` and no `DEFERRED-STALE` line, and `meta.spec.ts`'s deferral gate has
nothing left to gate.
