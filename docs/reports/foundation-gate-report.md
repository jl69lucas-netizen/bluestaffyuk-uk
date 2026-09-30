# Foundation gate report

BlueStaffyUK rebuild, project 1 of 6. Written by hand from the real outputs of the runs
recorded in `docs/reports/foundation-run.log`, the render harness, and the Lighthouse
sweep. Date 2026-09-16. Branch `foundation`, no remote, nothing pushed.

Spec: `docs/superpowers/specs/2026-09-15-foundation-design.md` §5 is the definition of
done; the checklist at the end of this report answers it line by line.

Read the two severities in this report differently. The **Python gates** (parity,
redirects, schema, sitemaps) are zero-tolerance and are all at zero. The **render harness**
reports a large blocking baseline, and that is the intended outcome, not a failure:
Foundation migrates WordPress markup verbatim, so the harness is measuring the old site's
body HTML through a new shell. Those rows are the starting line for projects 3 and 4.

---

## Build

| | |
| --- | --- |
| Command | `npm run build` (Astro 6.3.8, pinned) |
| Pages built | **49** `index.html` |
| Composition | 11 rich pages + 28 locations + 6 puppy pages + 1 blog post + 3 new index pages |
| Postbuild | `scripts/generate_sitemaps.py` — 5 shards |
| Exit | clean, both runs |

## Parity — `scripts/migration_parity.py`

```
examined 40 pages, 0 failing
```

40 old URLs compared old body → expected body → built body. Headings match exactly on every
page; no page lost more than the 2% whitespace band; embeds never decreased. Full table in
`docs/reports/parity.md` and embedded in `docs/reports/foundation-migration.md`.

## Redirects — `scripts/redirect_check.py`

```
examined 18 redirects, 1964 internal refs (distinct per page); 0 redirected refs; 0 problems
```

Every row in `data/redirects.json` resolves in one hop; every root-relative `href`/`src` on
every built page resolves to a real route; zero `wp-json`, `/feed/`, `xmlrpc.php` remnants.
"0 redirected refs" is the stronger statement: no internal link points at a URL that then
redirects, so nothing on the site spends a hop.

## Schema — `scripts/schema_check.py`

```
examined 49 pages; 0 blocking, 0 advisory
```

Every `application/ld+json` block on every page parses; no `telephone` still holding
`PHONE_PLACEHOLDER`; no `InStock` outside an available puppy's page; no dangling `@id`
after the legacy Rank Math graph was deduped; every `Product` carries `offers`; no `Offer`
states price without currency.

Fixed at close-out: the `InStock` test required `isinstance(availability, str)`, and
`_strip_availability` removed the key before the prose fallback scan, so
`"availability": ["https://schema.org/InStock"]` — the list form — was invisible to **both**
the blocking test and the advisory backstop. The test now runs against `json.dumps` of the
value, with two pytest cases pinning the list form blocking off a puppy page and permitted
on an available one.

## Sitemaps — `scripts/sitemap_check.py`

```
31 of 49 built pages are indexable; each must appear in exactly one URL shard.
examined 49 built pages, 5 shards, 35 sitemap urls; 0 problems
```

18 pages are deliberately noindexed (17 stub locations + the thank-you page) and correctly
absent from every shard. `lastmod` is the build date throughout — see the plan addendum:
the WordPress export carries no trustworthy per-page modification date, and inventing one
would tell Google something untrue.

## Placeholders — `scripts/placeholder_check.py`

```
SITE_URL_PLACEHOLDER       586 occurrence(s) in 56 file(s)
PHONE_PLACEHOLDER            0 occurrence(s) in 0 file(s)
FORMSPREE_ID_PLACEHOLDER     0 occurrence(s) in 0 file(s)
TOTAL                      586
placeholders: 586 (advisory — set BSUK_RELEASE=1 to make this blocking)
```

The gate always counts and always prints; it fails only under `BSUK_RELEASE=1`. Foundation
is *supposed* to ship stand-ins — the domain does not exist yet — and launch is not.
Verified in both modes: pre-launch exits 0 with 586 counted, `BSUK_RELEASE=1` exits 1 and
names the files. Wired as the last step of `npm run check:all`.

The two zeros are real, not a broken scan: `PHONE_PLACEHOLDER` lives in `data/settings.json`
and the extractor drops the key rather than rendering it, and `ContactForm.astro` renders a
local stub rather than a Formspree action while `PUBLIC_FORMSPREE_ID` is unset.

## Pytest

```
173 passed, 146 warnings in 50.2s
```

173 tests across 16 files in `tests/py/`, green on both runs. (+2 at close-out for the
list-valued `availability` case.)

## Render harness — meta gate (`tests/render/meta.spec.ts`)

```
306 passed, 36 skipped        (run 1)
306 passed, 36 skipped        (run 2)
```

The skips are viewport-independent tests declared once and skipped in the two non-primary
projects — by design, not by failure.

| | |
| --- | --- |
| Families registered in `lib/registry.ts` | 9 — IMG, LAYOUT, NAV, CSS, SEM, SCHEMA, DUP, A11Y, FORM |
| Families wired in `targets.json` | 9, on all 7 page types |
| Symmetric difference | **empty**, asserted in both directions |
| Checks registered | 25 |
| Checks examining > 0 units on real pages | 22 |
| Checks examining 0 | 3, all declared in `deferred_checks` (below) |
| Total units examined across the corpus | 66,313 |

Both directions are asserted, and that matters: a family registered but wired nowhere runs
on zero pages while reporting as a shipped gate (this is exactly how `a11y-text-contrast-aa`
shipped blocking and examined nothing for a day on CAG), and a family named in
`targets.json` that no check registers is a typo that silently widens nothing.

## Render harness — pages run (`tests/render/pages.spec.ts`)

17 target pages × 3 viewports (375, 768, 1280) = **51 partials**, all written; the run
produced the expected 51 of 51 against the manifest, so no page crashed the harness (Guard 1).

**Overrides used: none.** No defect anywhere in this baseline is suppressed.

### Blocking baseline by check id

These fail the pages spec, and they are the migrated content's baseline — **not Foundation
defects**. Each one is a property of the WordPress body HTML that Foundation carried across
verbatim, per spec §2, and the `targets.json` comment ("Foundation is a verbatim migration
of WordPress markup: many failures are expected on migrated bodies and form the baseline for
projects 3 and 4; failures caused by the shell … are fixed here"). Every shell-caused row —
header logo size, mobile scroll offset, contact-form overflow, header measurement — *was*
fixed here, which is why the list below contains no shell rows.

| Check id | Family | Pages | Rows | Instances | Units examined | Cause |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `schema-date-modified-present` | SCHEMA | 6 | 18 | 18 | 216 | The export has no per-page modification date; `scripts/generate_page_dates.py` is project 4's. |
| `nav-jump-target-lands` | NAV | 6 | 18 | 21 | 93 | In-page anchors in migrated bodies pointing at targets the old theme's chrome offset differently. |
| `img-srcset-within-2x` | IMG | 6 | 15 | 62 | 402 | WordPress `srcset` candidate sets whose widest and narrowest candidates exceed a 2x ratio. |
| `sem-heading-order` | SEM | 3 | 9 | 9 | 1,407 | Heading levels skipped inside migrated bodies (H2 → H4). |
| `layout-tap-target-size` | LAYOUT | 2 | 4 | 26 | 2,907 | Inline links in dense migrated prose below the 24px target. |
| `schema-no-visible-date` | SCHEMA | 1 | 3 | 3 | 51 | A visible date in migrated body copy with no matching schema date. |
| **Total** | | | **67** | **130** | | |

### Advisory baseline by check id

| Check id | Family | Pages | Rows | Instances | Units examined |
| --- | --- | ---: | ---: | ---: | ---: |
| `sem-all-six-levels` | SEM | 17 | 51 | 177 | 1,407 |
| `css-class-resolves` | CSS | 17 | 51 | 6,534 | 28,974 |
| `dup-no-sibling-crossover` | DUP | 14 | 42 | 477 | 2,448 |
| `sem-title-case-headings` | SEM | 11 | 33 | 264 | 1,401 |
| `sem-section-opening-paragraph` | SEM | 8 | 24 | 72 | 1,398 |
| `form-inquiry-contract` | FORM | 1 | 6 | 21 | 3 |
| `a11y-text-contrast-aa` | A11Y | 1 | 3 | 6 | 11,151 |
| **Total** | | | **210** | **7,551** | |

**The 42 DUP rows are not a BSUK duplication measurement.** `lib/dupCorpus.ts` reads the
whitelist from `scripts/dup_content_audit.py`, and that file is still CAG's **verbatim** —
its exempt phrases are parrot inventory lines ("ships nationwide $185 airport $350 home",
"browse by kind all birds 6 congo 3 timneh 2"). None of them match anything on a Staffy
site, so nothing is exempted and every mandated sitewide line counts as a crossover. It
cannot simply be swapped: the meta gate's `dup-adjacent-to-whitelist` fixture is built on
those exact stems, so re-basing the whitelist means re-basing the fixture with it. That is
project 2's port work. Until then read the DUP number as "unfiltered", not as a finding.

### Deferred checks

Registered, wired, and still passing both fixtures — but they encode conventions the
migrated WordPress markup does not use, so they examine zero nodes on every built page and
would fail `build_scorecard.mjs` Guard 2. They are listed in `targets.json > deferred_checks`
with a reason that must state its own end condition, and Guard 2 **prints** rather than
silences them:

| Check id | Reason | Ends when |
| --- | --- | --- |
| `layout-hero-counter-separation` | BSUK has no counter strip until project 3 adopts the kit | any built page ships a counter strip |
| `layout-h3-image-first` | no H3-owned `.sec-img` convention on migrated WordPress bodies | project 3 re-authors bodies so an H3 owns its `.sec-img` |
| `sem-statement-label-visible` | no `.stmt-label` convention yet | the kit introduces `.stmt-label` |

Exempting an id from Guard 2 switches off the one alarm that would notice the check had
rotted, so the exemption buys the proof back by other means. `meta.spec.ts` asserts, for
every deferred id: it names a registered check; its reason states a promotion condition; it
still **fires** on its `known_broken` fixture; it is still **silent** on `known_good`; and
it examined **zero** in the latest scorecard. `build_scorecard.mjs` additionally prints
`DEFERRED-STALE` for any entry that starts examining nodes again.

## Scorecard

`node scripts/build_scorecard.mjs --run first`

```
DEFERRED (…) layout-hero-counter-separation
DEFERRED (…) layout-h3-image-first
DEFERRED (…) sem-statement-label-visible
---
277 defect ROWS across 17 pages (run=first, harness 2.0.0).
```

277 rows = 67 blocking + 210 advisory. Rows are comparable across families; instances
(7,681) are not — a row is one failure mode of one check at one viewport, which is the unit
that survives being compared between `layout-min-font-size` (one row, many nodes) and
`nav-jump-target-lands` (one row per anchor). Per-page cards, including `examined_by_check`,
are in `data/quality/scorecards/*.json` and are committed as the project 3/4 baseline.

Guard 1 (51 of 51 partials present) and Guard 2 (no undeclared zero-examined check) both
pass. Zero overrides in effect.

## Lighthouse baseline

Warm median of 3 runs per page type against `npx astro preview` on localhost, headless
Chrome, Lighthouse 13.4.1, default mobile emulation. **Not a gate in Foundation** (spec §5);
recorded as the number projects 3–6 have to not make worse. Raw JSON is written to
`docs/reports/lh/` and gitignored — only these medians are committed.

| Page type | URL | Perf | A11y | Best practices | SEO | FCP | LCP | TBT | CLS | Speed Index |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| home | `/` | 99 | 100 | 100 | 100 | 908 ms | 1552 ms | 77 ms | 0.000 | 921 ms |
| for-sale | `/buy-blue-staffy-puppies-uk/` | 99 | 100 | 100 | 92 | 902 ms | 1689 ms | 75 ms | 0.000 | 902 ms |
| puppy | `/available-puppies/roman/` | 98 | 100 | 100 | 100 | 671 ms | 2277 ms | 88 ms | 0.000 | 671 ms |
| location | `/uk-locations/blue-staffy-puppies-uk/` | 100 | 100 | 100 | 92 | 874 ms | 1453 ms | 69 ms | 0.000 | 874 ms |
| blog | `/blue-staffy-blog-guides/` | 100 | 100 | 100 | 100 | 667 ms | 758 ms | 63 ms | 0.001 | 667 ms |

Two notes on reading these. **Localhost flatters network metrics** — LCP and Speed Index
here carry no real-world latency, so treat the *category scores* as the baseline and the
millisecond columns as relative between page types. And the two **SEO 92s are one audit**,
`link-text` ("links do not have descriptive text") on migrated body copy: generic anchor
text like "read more" inside the WordPress prose. That is content work for project 4, and
it is the only SEO deduction anywhere in the sweep.

The puppy page's LCP (2277 ms) is the worst of the five and is the pup hero image; the
`img-srcset-within-2x` blocking rows above are on the same images. Project 3's image work
should move both numbers together.

## Second-run confirmation

Spec §5: "every check runs twice; both runs must be clean."

The full pipeline — `extract` → `redirects` → `llms` → `build` → `check:all` → `test:py` —
was run twice back to back into `docs/reports/foundation-run.log`. The two halves of that
log are **byte-identical after normalising elapsed times**, verified programmatically rather
than by eye:

| Output | Run 1 | Run 2 |
| --- | --- | --- |
| Parity | `examined 40 pages, 0 failing` | `examined 40 pages, 0 failing` |
| Redirects | `18 redirects, 1964 internal refs; 0 redirected refs; 0 problems` | identical |
| Schema | `examined 49 pages; 0 blocking, 0 advisory` | identical |
| Sitemaps | `49 built pages, 5 shards, 35 sitemap urls; 0 problems` | identical |
| Placeholders | `586 (advisory)` | identical |
| Pytest | `173 passed` | `173 passed` |

The meta gate was then run twice on its own: `306 passed, 36 skipped` both times.

The stronger evidence that the build is deterministic is `git status --short`: after two
full pipeline runs the only modified tracked files are under `docs/reports/`. Every
generated file under `public/` and every file under `data/` came out byte-identical, and the
harness's own staleness tests (`checkDistFreshness`) refuse to measure a `dist/` older than
`src/`, so a stale build cannot masquerade as a passing one.

## Definition of done — spec §5

| Requirement | Status | Evidence |
| --- | --- | --- |
| `astro build` clean | ✅ | 49 pages, clean exit, both runs |
| `meta.spec.ts` + `pages.spec.ts` ported; targets.json lists the required pages | ✅ | 17 targets: 11 rich + `/uk-locations/` + 2 locations + 1 pup + 1 post + `/blog/` + `/available-puppies/` |
| Meta gate reports non-zero examined for every registered family; a family wired to no page type fails | ✅ | 9/9 families wired, symmetric difference empty and asserted both ways; 66,313 units examined; the 3 zero-examined *checks* are declared, printed and fixture-proven |
| `migration_parity.py` — ≤2% drop, whitelisted removals | ✅ | `examined 40 pages, 0 failing` |
| `redirect_check.py` — one hop, every internal href 200, no WP remnants | ✅ | `18 redirects, 1964 internal refs; 0 redirected refs; 0 problems` |
| `schema_check.py` — parses, no duplicate types, no false InStock, no placeholder telephone | ✅ | `49 pages; 0 blocking, 0 advisory`; list-form `availability` hole closed at close-out |
| `sitemap_check.py` — every page in exactly one sitemap, nothing noindexed listed, every loc 200 | ✅ | `49 built pages, 5 shards, 35 sitemap urls; 0 problems` |
| Lighthouse warm median of 3 per page type recorded, not a gate | ✅ | table above; 98–100 performance, 100 accessibility and best practices across all five |
| Every check runs twice; both runs clean | ✅ | `docs/reports/foundation-run.log`, halves identical after time normalisation; meta gate twice |
| `foundation-migration.md` written | ✅ | `docs/reports/foundation-migration.md`, generated by `scripts/build_migration_report.py` |
| `foundation-gate-report.md` written | ✅ | this file |
| Published as an Artifact | ⏳ | source built at `docs/artifacts/bsuk-foundation-gate-report.html`; publishing is the controller's step |
| Old MCP untouched | ✅ | nothing in this project touches it |
| No remote, nothing pushed | ✅ | `git remote -v` prints nothing |
| Git history in `~/Downloads/BSUK` | ✅ | 44 commits on branch `foundation` (this report is the 44th) |

## Out of scope for Foundation

Restated from spec §5 so nothing below is read as an omission: any content rewrite; the
design system and components; the four logos; the location-page rebuild; the comparison
cluster; the two new blog posts; deleting the old MCP; GSC / GA4 / Bing; the new domain and
the new phone number.

## Open items for later projects

1. **`FORM_ENDPOINT` contract is CAG's.** `form-inquiry-contract` reports 6 advisory rows on
   the contact page against a contract written for the parrot site's fields. Re-basing it is
   part of the project 2 system transfer, together with the Formspree endpoint itself.
2. **The DUP whitelist is CAG's verbatim.** See the note above the advisory table — the 42
   DUP rows are unfiltered, not measured. Re-basing the whitelist means re-basing the
   `dup-adjacent-to-whitelist` fixture that depends on its exact stems. Project 2.
3. **The orphan check is blinded by the catch-all route.** `builtRoutesWithoutSource()` in
   `tests/render/lib/freshness.ts` compares built routes to source routes, and a root-level
   `src/pages/[...post].astro` matches *any* path — so while it exists the function cannot
   prove **any** route orphaned, static pages included. The mtime comparison is the only
   remaining freshness signal today. The comment in that file now says so. A real answer
   needs a check that reads the content collection rather than the filesystem.
4. **Puppy `srcset` 2x rows.** 15 blocking rows over 6 pages, same images as the puppy page's
   2277 ms LCP. Project 3's image pass should fix both at once.
5. **`nav-jump-target-lands` baseline.** 18 rows over 6 pages remain after the shell fix.
   `--hdr` is now *measured* from the header (`--hdr-measured`, written by an inline script on
   load / resize / ResizeObserver) with the media query kept as the no-JS fallback, so the
   remaining rows are migrated in-page anchors, not chrome miscalculation.
6. **17 stub locations are noindexed.** They carry 0–7 words of legacy body. Project 5 writes
   them; `sitemap_check.py` keeps them out of the shards until then.
7. **Placeholders.** 586 `SITE_URL_PLACEHOLDER` occurrences across 56 files, plus the phone
   number and the Formspree id, all resolved at project 6 launch.
   `BSUK_RELEASE=1 npm run check:placeholders` is the gate that will refuse to ship them.
8. **`schema-date-modified-present`.** 18 rows over 6 pages; needs
   `scripts/generate_page_dates.py`, which arrives with project 4's content work — the same
   project that gives pages a real edit history for sitemap `lastmod`.
