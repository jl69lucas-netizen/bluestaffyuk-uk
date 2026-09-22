# Page rebuilds gate report

BlueStaffyUK rebuild, project 4 of 6. Written by hand from the real outputs of the two full
runs recorded in `docs/reports/page-rebuilds-run.log`, the Lighthouse sweep, and gate scripts
re-run at close-out. Date 2026-09-22. Branch `page-rebuilds`, cut from `foundation` at
`63a7b12`, no remote, nothing pushed.

Spec: `docs/superpowers/specs/2026-09-19-page-rebuilds-design.md`. §7 is the definition of
done **as amended by §9 (amendments 1–11)**; the checklist at the end answers it line by line.
Where §7's literal text and an amendment disagree, the amendment wins.

Read the two severities differently, as in projects 2 and 3. The **system gates** — build,
`check:all` (parity, facts-preserved, link parity, verbatim set, redirects, schema, sitemaps,
placeholders, markers, agents), pytest, render meta, the render baseline checker, the
thirteen board gates' page rows and `generate_page_dates.py --check` — are zero-tolerance and
are all at zero. The **content audits** (dup, evidence, page hardening) still exit non-zero,
and every non-zero row is named below with the page it sits on. **None of them sits on a
rebuilt page except seventeen duplicate passages, which are carried as a new open item.**

**Step 0, before measuring (commit `f94baee`).** The copy around four of the seven video
sections described the films wrongly — why-us called its clip "the short version, in our own
voice", the breeders page and the homepage described a house tour, the homepage said the
six puppy cards were "the same puppies" as the film, and the breed guide's H2 called the clip
"the guide in short" while its own paragraph said it was not a spoken guide. Every embed is a
short silent clip of our puppies. Four records were re-approved with `board_approve.py
--reapprove` (wording only — headings, two video titles, intents, why lines, refresh notes;
no pick, id, caption or source moved), the four boards regenerated, and the two runs below
were taken on that commit.

---

## Build

| | |
| --- | --- |
| Command | `npm run build` (Astro 6.3.8; `prebuild` runs `generate_page_dates.py`) |
| Pages built | **58** `index.html` (51 at project 3; plus the post at its own URL, the five `/board-preview/<slug>/` routes the boards cut from, and `/board-preview/` itself) |
| Postbuild | `generate_sitemaps.py` — 5 shards, **video shard 5 urls**; `build_search_index.py` — 31 rows |
| Exit | clean, both runs |

## Components 14–18 and the shell

Project 3 left thirteen kit components; project 4 adds five. `data/design/components.json`
has **18** rows.

| # | Component | File | Pick | Where it lives |
|---|---|---|---|---|
| 14 | Desktop dial | `PageDial.astro` | S2 (contact board) | sticky 196px column in `PageShell` (amendment 1.2), progress ring, scroll-spy |
| 15 | Section sheet | `SectionSheet.astro` | S2 | bottom tab bar + native `<dialog>` sheet below 1024px |
| 16 | Section strip | `SectionStrip.astro` | S2 | sticky chip rail under the header below 1024px (amendment 3b) |
| 17 | Data table | `DataTable.astro` | per page (S1/S2/S3) | every table section; stacks into `data-label` rows below 640px (rule 13) |
| 18 | Video embed | `VideoEmbed.astro` | per page (S1/S2/S3) | every YouTube id at its original id, `youtube-nocookie.com` (rule 14) |

The dial, sheet and strip are on **all twelve rebuilt pages and the three hubs**
(`/available-puppies/`, `/uk-locations/`, `/blog/`) and on the post: measured on `dist/`,
every one of those pages carries `kit-dial`, `kit-sheet` and `kit-strip`. The dist assertions
are in `tests/py/test_design_components.py`, and `nav-bottom-chrome-clear` is its own blocking
NAV check beside `nav-jump-target-lands` (amendment 1.1) — zero rows on every page.

## Facts preserved

`scripts/facts_preserved_check.py --check`: **`examined 12 rebuilt pages; 0 problems`**, both
runs. Every price, name, test, credential, image, embed and claim sentence of each migrated
page is on the rebuilt page or in the record's `dropped` with a reason. `migration_parity.py`
still runs for the 28 pages not rebuilt (`examined 28 pages, 0 failing, skipped 12 rebuilt`).

| Page | Fact set (prices · names · tests · creds · images · embeds · claims) | Dropped with reasons |
|---|---|---|
| `/privacy-policy-uk/` | 0 · 0 · 0 · 2 · 3 · 0 · 15 | images 2, links 6, text 3 |
| `/thank-you-blue-staffy-puppies-journey/` | 0 · 0 · 0 · 1 · 1 · 0 · 4 | links 1, text 1 |
| `/uk-blue-staffy-breeders-contact/` | 0 · 0 · 0 · 2 · 1 · 0 · 4 | prices 1, names 2, links 1, text 1 |
| `/` | 2 · 0 · 4 · 3 · 14 · 0 · 49 | prices 3, names 5, creds 7, embeds 1 (the Maps iframe on the old street), links 3, text 22 |
| `/blue-staffy-pup-sale-uk/` | 2 · 0 · 2 · 3 · 5 · 0 · 16 | prices 3, names 3, tests 1, creds 3, links 1, text 12 |
| `/buy-blue-staffy-puppies-uk/` | 3 · 0 · 4 · 3 · 7 · 0 · 46 | prices 4, names 3, creds 5, links 3, text 25 |
| `/buy-staffy-puppies-for-sale-uk/` | 2 · 0 · 5 · 3 · 13 · 1 · 67 | prices 2, names 3, tests 1, creds 5, links 12, text 21 |
| `/blue-staffy-uk-breeders/` | 2 · 0 · 3 · 3 · 7 · 1 · 24 | prices 1, names 1, links 9, text 16 |
| `/blue-staffy-health-uk/` | 2 · 0 · 5 · 3 · 8 · 0 · 65 | prices 1, names 1, creds 1, links 10, text 21 |
| `/uk-staffordshire-bull-terrier-guide/` | 13 · 0 · 4 · 3 · 10 · 1 · 93 | prices 3, names 1, links 9, text 40 |
| `/uk-blue-staffy-puppy-buying-guide/` | 19 · 0 · 5 · 3 · 17 · 1 · 97 | prices 4, names 4, links 16, text 26 |
| `/blue-staffy-blog-guides/` | 0 · 0 · 0 · 0 · 0 · 0 · 1 | links 1 |

The dropped prices are the old £850–£1,200 band and its relatives (Known Issue 11); the
dropped names are the former byline and the former city (Known Issues 12, 16); the dropped
credentials are claims no file backs — the Kennel Club Assured Breeder claim (an open question
for Lisa), DEFRA approval used as a breeder credential, lifetime-support and health-guarantee
wording, and an unsourced subscriber count.

## The twelve pages

Board URLs from `data/design/artifacts.json` `boards`. Every record is `status: approved`;
picks are the breeder's, re-approvals are wording-only (amendment 11). Verbatim counts are
`scripts/verbatim_set_check.py --check` on the built page (rule 15, amendment 8): elements in
the migrated set, of which `changed` carry a `verbatim.changed` row with a reason, and
**0 missing on every page**. Rule 15 applies from the homepage onward; the three pages built
before it are excluded by name in `data/verbatim/applies.json`. Sections, words, images and
reviews are measured in `<main>` of `dist/` (words include the dial/strip/sheet labels).

| # | Page | Board | Verbatim (set / changed / missing) | Sections | Words | Images | Videos | Review blocks | `REVIEW_PLACEHOLDER` | Hero / counter | Re-approvals |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| 1 | `/privacy-policy-uk/` | https://claude.ai/artifact/6GGxx5TDwfmiiSwqwcU8L1 | excluded (pre-rule 15) | 10 | 1,805 | 1 | 0 | 0 | 0 | H-UT1 / — | 0 |
| 2 | `/thank-you-blue-staffy-puppies-journey/` | https://claude.ai/artifact/BfK3pukgQGjewAiVTJcUTq | excluded (pre-rule 15) | 8 | 1,250 | 7 | 0 | 1 | 0 | H-UT1 / C-UT1 | 0 |
| 3 | `/uk-blue-staffy-breeders-contact/` | https://claude.ai/artifact/2wEuMXHCbREePWUbwkg6Md | excluded (pre-rule 15) | 8 | 1,235 | 1 | 0 | 1 | 0 | H-UT1 / C-UT1 | 0 |
| 4 | `/blue-staffy-uk-breeders/` | https://claude.ai/artifact/D7WY5D7cxzhnSoKwmDFNei | 38 / 20 / 0 | 13 | 3,393 | 15 | 1 | 5 | 0 | H-AB1 / C-AB1 | 4 |
| 5 | `/blue-staffy-health-uk/` | https://claude.ai/artifact/4tPfxNqdj5gB3hgBtCPBEx | 77 / 21 / 0 | 15 | 4,489 | 8 | 0 | 1 | 0 | H-GD3 / C-GD1 | 2 |
| 6 | `/uk-staffordshire-bull-terrier-guide/` | https://claude.ai/artifact/GHS7TjfKHy18E29uxW5Cxs | 62 / 9 / 0 | 16 | 6,030 | 16 | 1 | 1 | 0 | H-GD3 / C-GD3 | 5 |
| 7 | `/uk-blue-staffy-puppy-buying-guide/` | https://claude.ai/artifact/22dKovjVo7mpDnqAfuHgUM | 96 / 42 / 0 | 20 | 7,046 | 23 | 1 | 1 | 0 | H-GD3 / C-GD2 | 6 |
| 8 | `/blue-staffy-blog-guides/` | https://claude.ai/artifact/C1UBtpqXCr7RKsUkXBHG1K | 4 / 2 / 0 | 8 | 1,546 | 1 | 0 | 1 | 0 | H-BL3 / C-BL2 | 2 |
| 9 | `/blue-staffy-pup-sale-uk/` | https://claude.ai/artifact/9u58JFUxtThK5vEXXK5Ykf | 26 / 9 / 0 | 12 | 2,563 | 11 | 0 | 3 | 0 | H-FS3 / C-FS1 | 3 |
| 10 | `/buy-staffy-puppies-for-sale-uk/` | https://claude.ai/artifact/Pt4Ld67G7xdpohbNo6ZMXR | 91 / 48 / 0 | 16 | 4,902 | 20 | 1 | 3 | 0 | H-FS2 / C-FS2 | 4 |
| 11 | `/buy-blue-staffy-puppies-uk/` | https://claude.ai/artifact/MzJNhQSzPNe8b3cMGHhPvu | 46 / 15 / 0 | 13 | 3,280 | 15 | 0 | 1 | 0 | H-FS1 / C-FS3 | 2 |
| 12 | `/` | https://claude.ai/artifact/LgQPwXxjCowZwGnodn6Au9 | 67 / 15 / 0 | 21 | 5,224 | 21 | 3 | 4 | 0 | H-HM2 / C-HM2 | 2 |

**Verbatim total across the nine applicable pages: 507 elements, 181 changed with reasons,
0 missing.** The blog post moved to its own URL
(`/how-to-choose-the-right-blue-staffy-puppy-for-your-family/`) on the kit shell; its body
was not re-boarded.

**Reviews.** `REVIEW_PLACEHOLDER` renders **0** times on every page, and
`placeholder_check.py` counts **0** — every review slot the boards opened is filled from the
three real rows in `data/reviews.json`, rotated, and nothing is invented. The number of
reviews the site still *needs* to fill its slots is therefore zero; the number it would need
to stop rotating three quotes across twelve pages is a separate, editorial question for Lisa.

**Rule 16 is not fully met** (Known Issues 33 and 35): the three utility pages all carry
H-UT1, the three guides all carry H-GD3, and thank-you and contact share C-UT1.

## Rules 10–16

Rules 10 and 11 were written at project 3's close; project 4 is the first build to apply them
to real pages. Rules 12–16 were given by the breeder during this build.

| Rule | Given | What it requires | Mechanical backstop |
|---|---|---|---|
| 10 Visual companion, always | 2026-09-18 | every visual decision shown in the browser or a published board | twelve published boards, three rendered styles per section |
| 11 Reuse every image and video; never break a URL | 2026-09-19 | original path, filename, alt; never rename/delete/re-encode | `test_legacy_logo_rasters_are_still_served`; facts-preserved image kind |
| 12 Every link on the board | 2026-09-19 | every internal/external link per section and as one table before approval | `link_parity_check.py --check` (amendment 6b) — `196 distinct body links; 0 problems` |
| 13 Tables: three styles, stacked on mobile | 2026-09-20 | `table` shape, `DataTable`, `data-label` rows below 640px | stacked-table harness check; `tuple.table` axis (amendment 9.1) |
| 14 Every video at its original id | 2026-09-20 | same id, same place, `video` shape, facade by default | facts-preserved embed kind; `generate_sitemaps.py` nocookie fix (`e963c53`) |
| 15 Faithful rewrite | 2026-09-20 | the verbatim set word for word unless a wrong fact or a collision | `verbatim_set_check.py --check`; `dropped-vs-verbatim` |
| 16 Per-page hero and counter; a refresh delta on every section | 2026-09-20 | no shared hero/counter; figures sourced; `refresh` on every section | `stat-source-unresolved`, `ledge-source-unresolved`, `refresh-missing`, `ledger-tuple-owned` in `board_gate.py` |

## Spec amendments 1–11

| # | Date | What it changed |
|---|---|---|
| 1 | 09-19 | `nav-bottom-chrome-clear` is a separate check; the 196px dial column lives in `PageShell` |
| 2 | 09-19 | `min-h5-h6` reads the built page for a rebuilt slug; `ledger-tuple-owned` replaces the triple |
| 3 | 09-19 | working rule 12 (links on the board); component 16 `SectionStrip` |
| 4 | 09-20 | word bands count section prose only; Title Case is a render transform after the case-folded verbatim check; page-type exemptions in `final_page_audit.py` |
| 5 | 09-20 | working rule 13; `DataTable` component 17 |
| 6 | 09-20 | 6a–6g: no credentials or links from a kit default; link parity gate; `dropped.text`; `dropped` outside the hash; the privacy page's visible date; every ladder sentence sourced; FAQ headings Title Case |
| 7 | 09-20 | working rule 14; `VideoEmbed` component 18; facade by default |
| 8 | 09-20 | working rule 15; the verbatim set, its three exclusions and `verbatim.changed` |
| 9 | 09-20 | `table` is a tuple axis; takeaway-set rule fires on two or more; the root slug's built file is `dist/index.html` |
| 10 | 09-20/22 | working rule 16: six layout families, eighteen hero and eighteen counter arrangements two structural axes apart, sourced figures and ledges, refresh deltas, `locked_picks`, `dist-stale`; 4a — the ceiling is a desktop measure (Known Issue 28); the Hero/CounterStrip default carries retired 2026-09-22 |
| 11 | 09-21 | `board_approve.py --reapprove` for wording fixes after approval; 11a — a re-board withdraws only the question it asks, and the page renders the approval in force |

## Gates added this build

| Gate | Where | Kind | What it refuses |
|---|---|---|---|
| `--reapprove` | `scripts/board_approve.py` (`16aab98`) | controller tool + tests | a re-approval that moves a pick, a menu, a figure, a source, a section id or the ledger row; an empty diff; a missing reason |
| `dropped-vs-verbatim` | `scripts/pageboard.py` (`fddef4d`) | board gate | a `dropped` line striking a sentence the page renders |
| `img-sizes-matches-box` | `tests/render/checks/img.ts` (`168205d`) | render, IMG | an image whose `sizes` does not match the box it renders in |
| `hero-aside-no-clip` | `tests/render/checks/layout.ts` (`168205d`) | render, LAYOUT | a hero aside cut by the band |
| `a11y-hero-ledge-contrast` | `tests/render/checks/a11y.ts` (`65d7894`, extended `5975c9f`) | render, A11Y, blocking | a hero ledge or a video caption on a band below AA |
| embed → video sitemap | `scripts/generate_sitemaps.py` + `tests/py/test_sitemaps_gen.py` (`e963c53`) | build + pytest | a page carrying a nocookie embed missing from `video-sitemap.xml` |
| `copy-no-build-talk` | `tests/py/test_copy_no_build_talk.py` (`5975c9f`) | pytest | build language ("settings file", "on disk", "migrated", "repository" …) in a rebuilt page's `<main>` |

Also new this build: `facts_preserved_check.py`, `link_parity_check.py`,
`verbatim_set_check.py` (all in `check:all`), `nav-bottom-chrome-clear`, and the board-gate
rows `stat-source-unresolved`, `ledge-source-unresolved`, `refresh-missing`, `dist-stale`.

## Harness

**Pytest** — `npm run test:py`: run 1 **`1701 passed, 15 skipped, 1 xfailed`**, run 2
**`1703 passed, 13 skipped, 1 xfailed`**. The drift and its cause are under Second run. Project
3 closed at 1355 passed; this build added 348.

**Render meta** — `npm run test:render:meta`: **`370 passed, 38 skipped`**, exit 0, both runs
(project 3: 324 passed).

**Render pages** — `npm run test:render:pages`: **`54 passed, 6 failed`**, exit 1, both runs.
The six failures are two pages at three viewports each, neither rebuilt (Known Issue 31):
`/available-puppies/` (SEM, H1→H3 skip at "Roman") and `/uk-locations/blue-staffy-puppies-uk/`
(NAV, `#Staffy-adoption` lands outside the band). **Every rebuilt page passes at every
viewport.** The scorecard is **189 defect rows across 20 page scorecards** (run=first, harness
2.0.0), baseline written to `docs/reports/render-baseline-project4.md` by
`render_baseline.py --out` and verified by `--check` (`examined render-baseline-project4.md;
0 problems`) in both runs.

| Family | Blocking (P3 → P4) | Advisory (P3 → P4) | Pages (P3 → P4) |
|---|---|---|---|
| A11Y | 0 → 0 | 5 → 6 | 2 → 3 |
| CSS | 0 → 0 | 42 → 99 | 13 → 20 |
| DUP | 0 → 0 | 36 → 42 | 12 → 14 |
| FORM | 0 → 0 | 3 → 0 | 1 → 0 |
| IMG | 6 → **0** | 0 → 0 | 3 → 0 |
| LAYOUT | 4 → **0** | 0 → 0 | 2 → 0 |
| NAV | 18 → **3** | 0 → 0 | 6 → 1 |
| SCHEMA | 21 → **0** | 0 → 0 | 7 → 0 |
| SEM | 9 → **3** | 117 → 36 | 18 → 8 |
| **Total** | **58 → 6** | **203 → 183** | **18 → 20** |

`schema-date-modified-present` **18 → 0** (Known Issues 8, 20). `img-srcset-within-2x`
**6 → 0** — the two migrated `<img>` tags project 3 named are gone with their bodies.
`sem-title-case-headings` 36 → 9, none on a rebuilt page. The advisory CSS rise is the kit's
page-scoped rules (`css-no-dead-component-rule`, 3 → 54 rows) and classes the board styles set
for hooks rather than rules (`css-class-resolves`) — one row per viewport per page, advisory.
The three A11Y pages are Known Issue 21's `.dot` at 4.49:1 on `/kit-preview/`,
`/thank-you-blue-staffy-puppies-journey/` and `/uk-blue-staffy-breeders-contact/` (C-UT1's
inline dot) — advisory, unchanged in cause. Pages 18 → 20: the post at its own URL and
`/uk-locations/blue-staffy-puppies-birmingham/` joined the target list.

## Ported gates

Every gate run in both runs with `.env` sourced; the figures are identical in both.

| Gate | Summary line (run 1 = run 2) | Exit | Tag |
|---|---|---|---|
| `npm run build` | `58 page(s) built` | 0 | green |
| `migration_parity.py` | `examined 28 pages, 0 failing, skipped 12 rebuilt` | 0 | zero-tolerance, green |
| `facts_preserved_check.py --check` | `examined 12 rebuilt pages; 0 problems` | 0 | zero-tolerance, green |
| `link_parity_check.py --check` | `examined 12 rebuilt page(s), 196 distinct body link(s); 0 problems` | 0 | zero-tolerance, green |
| `verbatim_set_check.py --check` | `examined 9 applicable pages; 0 problems` (507 elements, 181 changed, 0 missing) | 0 | zero-tolerance, green |
| `redirect_check.py` | `examined 18 redirects, 2140 internal refs (distinct per page); 0 redirected refs; 0 problems` | 0 | zero-tolerance, green |
| `schema_check.py` | `examined 58 pages; 0 blocking, 0 advisory` | 0 | zero-tolerance, green |
| `sitemap_check.py` | `examined 58 built pages, 5 shards, 36 sitemap urls; 0 problems` | 0 | zero-tolerance, green |
| `placeholder_check.py` | `placeholders: 1748 (advisory …)` | 0 | by design until project 6 |
| `marker_check.py` | `examined 259 files; 0 problems` | 0 | zero-tolerance, green |
| `build_agent_registry.py --check` | `examined 36 agents; 0 problems` | 0 | zero-tolerance, green |
| `render_baseline.py --check --out …project4.md` | `examined render-baseline-project4.md; 0 problems` | 0 | zero-tolerance, green |
| `board_gate.py` × 12 rebuilt | `0 FAIL` on every one; WARN: privacy 1 · thank-you 10 · contact 15 · `/` 18 · pup-sale 6 · listing 10 · why-us 15 · breeders 12 · health 4 · breed guide 7 · buying guide 9 · blog 5 | 0 | green |
| `board_gate.py _demo` | `6 FAIL · 5 WARN` (approval-hash, min-h5-h6, four signature-no-pick) | **1** | designed refusal — the fixture is never approved; it exists so the interior-utility arrangements are rendered and measured (amendment 10) |
| `final_page_audit.py` | `examined 14 pages; 0 problems (12 PASS · 2 PASS-WITH-WARNINGS · 0 FAIL)` | 0 | green — **was 12 FAIL at project 3** |
| `final_page_audit.py --blog` | `examined 3 pages; 0 problems (3 PASS …)` | 0 | green |
| `evidence_audit.py --all` | `examined 58 pages; 21 problems (45 WARN)` | **1** | ERRORs on 9 pages, none rebuilt: five `/board-preview/` routes, the post, `/uk-locations/`, `/uk-locations/blue-staffy-puppies-uk/`, `/uk-locations/staffy-breeding-dogs-glasgow/` — every rebuilt page `0 ERROR` (Known Issue 34) |
| `aeo_audit.py --all` | `examined 58 pages; 0 problems (206 WARN)` · `pages with a real ERROR: 0` | 0 | green — **was 38 baseline-only FAIL pages at project 3** |
| `dup_content_audit.py` | `FAIL — 131 duplicated passages ≥12 words.` | **1** | 114 between pages not rebuilt; **17 touch a rebuilt page** (Known Issue 36); project 3: 135 |
| `page_hardening_scan.py` | `35 source files, 58 built pages` · `310 ERROR · 24 WARN` | 0 | all 310 are `header-not-title-case`: 247 on `/board-preview/` routes, 19 on `/kit-preview/`, 44 on puppy and location pages — **0 on a rebuilt page** |
| `form_contract_audit.py` | `examined 8 forms; 0 problems (inquiry 8, in-scope 4, newsletter 0)` | 0 | green |
| `generate_page_dates.py --check` | `page-dates.json current — 53 routes` | 0 | green |

**Placeholders 1605 → 1748.** The whole rise is `SITE_URL_PLACEHOLDER` (903 → 1046), which is
the absolute-URL stand-in in canonicals, schema `@id`s, breadcrumbs, VideoObjects and sitemap
rows: seven more built pages, and each rebuilt page emits more schema than its migrated body
did. The other five tokens are unchanged (`PHONE` 22, `FORMSPREE_ID` 0, `LICENCE_CLAIM` 536,
`LEGAL_CLAIM` 144) and `REVIEW_PLACEHOLDER` is **0**. All resolve at project 6 launch or on
Lisa's confirmation.

## Lighthouse

Warm median of 3 runs per page and profile (one further warm-up run discarded), against `npx astro preview` on localhost, headless Chrome, Lighthouse 13.4.1, the agentic configs in `scripts/lighthouse/` (mobile = the default mobile emulation, desktop = the desktop preset merged in) — the same method as projects 1 and 3, so the mobile table is comparable to theirs. **Recorded, not a gate.** Raw JSON is under `docs/reports/lh/p4/`, which is gitignored; only these medians are committed. The five page types come first; the other nine rebuilt pages follow (home, for-sale and blog are themselves rebuilt pages).

**Mobile**

| Page | URL | Perf | A11y | BP | SEO | Agentic | FCP | LCP | TBT | CLS | SI |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| home | `/` | 100 | 100 | 100 | 100 | 100 | 1110 ms | 1397 ms | 20 ms | 0.000 | 1110 ms |
| for-sale | `/buy-blue-staffy-puppies-uk/` | 100 | 100 | 100 | 100 | 100 | 1006 ms | 1525 ms | 30 ms | 0.000 | 1061 ms |
| puppy | `/available-puppies/roman/` | 100 | 100 | 100 | 100 | 100 | 823 ms | 1519 ms | 0 ms | 0.000 | 823 ms |
| location | `/uk-locations/blue-staffy-puppies-uk/` | 100 | 100 | 100 | 92 | 100 | 902 ms | 1372 ms | 0 ms | 0.000 | 902 ms |
| blog | `/blue-staffy-blog-guides/` | 99 | 100 | 100 | 100 | 100 | 1006 ms | 1434 ms | 66 ms | 0.000 | 1006 ms |
| rebuilt | `/privacy-policy-uk/` | 100 | 100 | 100 | 100 | 100 | 1023 ms | 1234 ms | 0 ms | 0.000 | 1023 ms |
| rebuilt | `/thank-you-blue-staffy-puppies-journey/` | 99 | 100 | 100 | 69 | 100 | 1014 ms | 1247 ms | 27 ms | 0.000 | 3467 ms |
| rebuilt | `/uk-blue-staffy-breeders-contact/` | 100 | 100 | 100 | 100 | 100 | 996 ms | 1367 ms | 32 ms | 0.000 | 2124 ms |
| rebuilt | `/blue-staffy-pup-sale-uk/` | 99 | 100 | 100 | 100 | 100 | 1019 ms | 1682 ms | 34 ms | 0.000 | 3515 ms |
| rebuilt | `/buy-staffy-puppies-for-sale-uk/` | 100 | 100 | 100 | 100 | 100 | 1038 ms | 1549 ms | 50 ms | 0.000 | 1082 ms |
| rebuilt | `/blue-staffy-uk-breeders/` | 100 | 100 | 100 | 100 | 100 | 1015 ms | 1824 ms | 18 ms | 0.000 | 1015 ms |
| rebuilt | `/blue-staffy-health-uk/` | 100 | 100 | 100 | 100 | 100 | 1030 ms | 1684 ms | 27 ms | 0.000 | 1030 ms |
| rebuilt | `/uk-staffordshire-bull-terrier-guide/` | 100 | 100 | 96 | 100 | 100 | 1172 ms | 1365 ms | 0 ms | 0.000 | 1172 ms |
| rebuilt | `/uk-blue-staffy-puppy-buying-guide/` | 100 | 100 | 100 | 100 | 100 | 1062 ms | 1428 ms | 35 ms | 0.000 | 2121 ms |

**Desktop**

| Page | URL | Perf | A11y | BP | SEO | Agentic | FCP | LCP | TBT | CLS | SI |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| home | `/` | 100 | 100 | 100 | 100 | 100 | 291 ms | 345 ms | 0 ms | 0.000 | 297 ms |
| for-sale | `/buy-blue-staffy-puppies-uk/` | 100 | 100 | 100 | 100 | 100 | 303 ms | 404 ms | 0 ms | 0.000 | 304 ms |
| puppy | `/available-puppies/roman/` | 100 | 100 | 100 | 100 | 100 | 247 ms | 375 ms | 0 ms | 0.000 | 247 ms |
| location | `/uk-locations/blue-staffy-puppies-uk/` | 100 | 100 | 100 | 92 | 100 | 252 ms | 312 ms | 0 ms | 0.000 | 252 ms |
| blog | `/blue-staffy-blog-guides/` | 100 | 100 | 100 | 100 | 100 | 288 ms | 382 ms | 0 ms | 0.000 | 288 ms |
| rebuilt | `/privacy-policy-uk/` | 100 | 100 | 100 | 100 | 100 | 284 ms | 309 ms | 0 ms | 0.000 | 284 ms |
| rebuilt | `/thank-you-blue-staffy-puppies-journey/` | 100 | 100 | 100 | 69 | 100 | 324 ms | 387 ms | 0 ms | 0.000 | 342 ms |
| rebuilt | `/uk-blue-staffy-breeders-contact/` | 100 | 100 | 100 | 100 | 100 | 287 ms | 342 ms | 0 ms | 0.000 | 287 ms |
| rebuilt | `/blue-staffy-pup-sale-uk/` | 100 | 100 | 100 | 100 | 100 | 282 ms | 431 ms | 0 ms | 0.000 | 282 ms |
| rebuilt | `/buy-staffy-puppies-for-sale-uk/` | 100 | 100 | 100 | 100 | 100 | 282 ms | 407 ms | 0 ms | 0.000 | 297 ms |
| rebuilt | `/blue-staffy-uk-breeders/` | 100 | 100 | 100 | 100 | 100 | 303 ms | 383 ms | 0 ms | 0.000 | 311 ms |
| rebuilt | `/blue-staffy-health-uk/` | 100 | 100 | 100 | 100 | 100 | 288 ms | 334 ms | 0 ms | 0.000 | 303 ms |
| rebuilt | `/uk-staffordshire-bull-terrier-guide/` | 100 | 100 | 96 | 100 | 100 | 302 ms | 368 ms | 6 ms | 0.000 | 335 ms |
| rebuilt | `/uk-blue-staffy-puppy-buying-guide/` | 100 | 100 | 100 | 100 | 100 | 302 ms | 347 ms | 0 ms | 0.000 | 302 ms |

Against project 3's mobile table (Perf / A11y / BP / SEO):

| Page type | Project 3 | Project 4 | Change |
|---|---|---|---|
| home | 99 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | Perf **99 → 100** |
| for-sale | 99 / 100 / 100 / 92 | 100 / 100 / 100 / 100 | Perf **99 → 100**, SEO **92 → 100** |
| puppy | 100 / 100 / 100 / 100 | 100 / 100 / 100 / 100 | equal |
| location | 100 / 100 / 100 / 92 | 100 / 100 / 100 / 92 | equal |
| blog | 100 / 100 / 100 / 100 | 99 / 100 / 100 / 100 | Perf **100 → 99 (fell)** |

**Falls:** blog Perf 100 → 99 (explained below).
 Below 100: `/uk-locations/blue-staffy-puppies-uk/` mobile seo 92; `/uk-locations/blue-staffy-puppies-uk/` desktop seo 92; `/blue-staffy-blog-guides/` mobile performance 99; `/thank-you-blue-staffy-puppies-journey/` mobile performance 99, seo 69; `/thank-you-blue-staffy-puppies-journey/` desktop seo 69; `/blue-staffy-pup-sale-uk/` mobile performance 99; `/uk-staffordshire-bull-terrier-guide/` mobile best-practices 96; `/uk-staffordshire-bull-terrier-guide/` desktop best-practices 96.


What each sub-100 score is:

- **`/blue-staffy-blog-guides/` mobile Performance 99 — the one fall against project 3.** Its
  three runs scored 99, 85 and 100 on Total Blocking Time alone (102 ms, 66 ms, 23 ms); LCP
  stayed at 1.37–1.49 s. It is run-to-run variance in main-thread time on a local Mac, on the
  page that now carries the dial, strip and sheet scripts, and it scores 100 on desktop. Recorded
  rather than explained away; project 6's PSI run is the judge.
- **`/thank-you-blue-staffy-puppies-journey/` SEO 69 (both profiles)** — `is-crawlable`: the page
  is `noindex` by design (it is the form's confirmation page). Not a defect.
- **`/uk-staffordshire-bull-terrier-guide/` Best Practices 96 (both profiles)** —
  `inspector-issues`, a Chrome cookie issue raised by `youtube-nocookie.com/embed/g9iV9RVr_Sk`.
  The breeder picked S2 (the player loaded on a steel band) for this page, so the player loads
  with the page; the S3 facade would not load it until pressed. New Known Issue 38.
- **`/uk-locations/blue-staffy-puppies-uk/` SEO 92** — `link-text` in migrated body copy, the
  same single audit Foundation and project 3 recorded. Build 5.
- **`/blue-staffy-pup-sale-uk/` mobile Performance 99** — TBT 34 ms median; a rebuilt page with no
  project 3 figure to compare.

The for-sale page type rose **SEO 92 → 100** (the rebuilt listing no longer carries the vague
link text) and home and for-sale Performance **99 → 100**.
 Localhost flatters the network metrics; treat the category scores as the record and the millisecond columns as relative between pages. `scripts/perf_audit.py --psi` is the authoritative judge once project 6 has a live URL.

## Second run

The full pipeline — build → `check:all` → pytest → render meta → render pages → scorecard →
`render_baseline.py --out` then `--check` → `board_gate.py` × 13 → `final_page_audit.py` and
`--blog` → evidence → AEO → dup → page hardening → form → `generate_page_dates.py --check` —
ran twice back to back into `docs/reports/page-rebuilds-run.log`. Method as project 3: split on
`=== RUN 2 ===`, strip ANSI, drop `[WebServer]` request lines, clock stamps, elapsed times,
Astro asset ordinals and Playwright's completion-order ordinals, then compare as multisets:

```
run1 normalised lines: 3597
run2 normalised lines: 3597
multiset differences : 4
```

**One drift, two lines each way, and its cause is fixed.** Run 1's pytest read `1701 passed,
15 skipped`; run 2's read `1703 passed, 13 skipped`, with the matching progress-dot line. The
two tests are `tests/py/test_render_baseline.py`'s real-scorecard pair, which skip while
`render-baseline-project4.md`'s generated block is empty (Known Issue 25's design: an unwritten
baseline is "not run yet", not drift). Run 1's pytest ran before run 1's `render_baseline.py
--out` filled the block; run 2's ran after. The cause is the empty block, and it is removed by
committing the filled block with this report: from here on both tests run and pass on every
run. Confirmed after the fix: `python3 -m pytest tests/py/test_render_baseline.py` —
`17 passed`, none skipped; and the full suite on `foundation` after the merge reads the run-2
figure (Merge section). Every other line of the two runs is identical.

| Step | Run 1 | Run 2 |
|---|---|---|
| build | 58 pages | 58 pages |
| check:all | exit 0 (lines in table above) | exit 0 (identical) |
| pytest | 1701 passed, 15 skipped, 1 xfailed | **1703 passed, 13 skipped**, 1 xfailed |
| render meta | 370 passed, 38 skipped | 370 passed, 38 skipped |
| render pages | 54 passed, 6 failed | 54 passed, 6 failed |
| scorecard | 189 rows / 20 pages | 189 rows / 20 pages |
| render baseline `--check` | 0 problems | 0 problems |
| board gate × 12 rebuilt | 0 FAIL each | 0 FAIL each |
| board gate `_demo` | 6 FAIL · 5 WARN | 6 FAIL · 5 WARN |
| final page / `--blog` | 12 PASS · 2 PWW / 3 PASS | 12 PASS · 2 PWW / 3 PASS |
| evidence | 21 problems (45 WARN) | 21 problems (45 WARN) |
| AEO | 0 problems (206 WARN) | 0 problems (206 WARN) |
| dup | 131 passages | 131 passages |
| page hardening | 310 ERROR · 24 WARN | 310 ERROR · 24 WARN |
| form | 8 forms, 0 problems | 8 forms, 0 problems |
| page dates `--check` | current, 53 routes | current, 53 routes |

## Credentials

No credential value appears in this report, the run log or any committed file.
`tests/py/test_secret_shapes.py` and `tests/py/test_no_env_value_committed.py` ran inside both
pytest runs with the run log present and passed. `.env` is unchanged. Project 2's pending
OAuth rotation (Known Issue 15) is still owed by the user.

## Known Issues open at close

Closed by this build: **8, 9, 11, 12, 16 (for the twelve pages; see 16 below), 20, 22, 25, 28,
29**. Open at close, with owner:

| # | Issue | Owner |
|---|---|---|
| 3 | Orphan check blinded by the catch-all route | build 5 |
| 5 | `nav-jump-target-lands` — now **3 rows on 1 page** (was 18/6), the location route in 31 | build 5 |
| 6 | 17 stub locations noindexed | build 5 |
| 7 | Placeholders: site-URL and phone stand-ins (build 6); licence and legal-claim stand-ins | build 6 / user (Lisa) |
| 10 | `bottom-bar-under-tabbar` / `analytics-double-load` have no harness equivalent (the bottom-bar idea is answered by `nav-bottom-chrome-clear`; analytics arrives with GA4) | build 6 |
| 13 | `INDEXNOW_KEY` empty, `SITE_URL` placeholder, no deploy | build 6 |
| 14 | GSC and GA4 pulls unwired | build 6 |
| 15 | OAuth client rotation pending | **user** |
| 16 | Former city still on live pages not rebuilt: `/available-puppies/` and its six puppy pages (meta descriptions), `/uk-locations/`, `/search/` (page-map titles), the 28 location bodies; `data/page-map.json` titles (2) | build 5 |
| 17 | No query-augmentation skill | build 5 |
| 18 | Hero lede two-line clamp at 1280 — a standing constraint | build 5 (standing) |
| 19 | `Button.kind` five treatments unconfirmed | **user** |
| 21 | `.dot` separator 4.49:1 — now on thank-you and contact via C-UT1, plus `/kit-preview/` | build 5 |
| 23 | Inline lockup page weight | build 6 |
| 24 | Fonts not vendored | build 6 |
| 26 | Reuse images/videos, never break a URL — standing constraint | builds 5–6 (standing) |
| 27 | No `uploadDate` on any VideoObject | **user** (upload dates from the channel) |
| 30 | H-GD3 photo column pins two guides at exactly 450px | build 5 |
| 31 | Two blocking routes: `/available-puppies/` SEM, `/uk-locations/blue-staffy-puppies-uk/` NAV | build 5 |
| 32 | 606px overflow at 375 on the contact board-preview route (preview only) | build 5 |
| 33 | H-HM2 / H-UT1 render degraded; three utility pages share H-UT1, two share C-UT1 | **user** (more photos and ledge rows, or new picks) |
| 34 | Evidence budgets per slug are measured ratchets; ceilings uncalibrated; the post and location routes still ERROR | build 5 |
| 35 | **NEW.** The three guides (health, breed guide, buying guide) all picked H-GD3 — rule 16 "no two pages share a hero layout" is not met between them | **user** (new picks) |
| 36 | **NEW.** 17 duplicate passages ≥12 words touch rebuilt pages: the shared FAQ answer "a comprehensive puppy package…" on four pages and "are the puppies raised in a family home…" on two (FAQ rows rendered from `data/faq.json` on more than one page), the review attribution tail "…is the heart of our family — the Victoria Family, Manchester" crossing the quote whitelist on three pairs, three rule-15 verbatim openings the homepage shares with its sources, the post against the buying guide (35 words), and pup-sale's "healthy, vaccinated and ready" line against two location bodies | build 5 |
| 37 | **NEW.** Definition of done 7 names the `Claude Fable 5.1` trailer; the last eight commits of this branch carry `Claude Opus 5.5`, by the controller's instruction for this session | user (ruling) |
| 38 | **NEW.** The breed guide's S2 video loads `youtube-nocookie.com` with the page and raises a Chrome cookie issue — Lighthouse Best Practices 96 on both profiles; the S3 facade would not | **user** (keep S2, or pick S3) |

## What build 5 inherits

1. The kit at eighteen components, with the dial, sheet and strip fixed site-wide and
   `PageShell` as the only shell a new page mounts.
2. The board pipeline end to end: `build_page_board.py`, `/board-preview/<slug>/`,
   `board_approve.py` (with `--reapprove` for wording and `locked_picks` for re-boards),
   `board_gate.py` with rule-16 sourcing checks.
3. Six layout families with eighteen hero and eighteen counter arrangements; the `location`
   family does not exist yet and build 5 must add one (two structural axes from every other).
4. Four content gates in `check:all` that a location page will meet on its first build:
   facts-preserved, link parity, the verbatim set (add each slug to `applies.json`) and
   migration parity for the pages not yet rebuilt.
5. The render baseline at **6 blocking rows**, all on two routes build 5 owns (Known Issue 31).
6. The former city on the puppy hub and pages, the locations hub, `/search/` and the 28
   location bodies (Known Issue 16's remainder).
7. Seventeen duplicate passages across rebuilt pages to whitelist or rewrite (Known Issue 36),
   and uncalibrated evidence ceilings (Known Issue 34).
8. Three breeder decisions pending before the rule-16 set is complete: H-GD3 on three guides,
   H-UT1/C-UT1 on the utility pages, and the degraded H-HM2 mosaic (Known Issues 33, 35).
9. No query-augmentation skill (Known Issue 17) ahead of 28 city pages; the
   location-page-builder skill names the step.
10. `render_baseline.py` defaults to `render-baseline-project4.md`; build 5 opens its own
    project 5 file and repoints the default, the test and `npm run baseline`.

## Definition of done — spec §7, as amended by §9

| # | Requirement (amended) | Verdict | Evidence |
|---|---|---|---|
| 1 | Twelve pages rebuilt from approved boards; each record `status: approved` with picks; every board URL in `data/design/artifacts.json` `boards` | **PASS** | twelve records `approved`; twelve URLs in `boards` (table above); re-approvals are wording-only with `changed_paths` and reasons |
| 2 | Components 14 and 15 in the kit, on every rebuilt page and the hubs, with dist assertions and the bottom-chrome measurement | **PASS** | `kit-dial` / `kit-sheet` / `kit-strip` on all twelve pages, the three hubs and the post; `test_design_components.py`; `nav-bottom-chrome-clear` blocking, 0 rows |
| 3 | `grep -rn Glasgow src data` = 0 outside history and the Glasgow page's slug; `settings.address` town-level; form contract re-based (KI 16 closed) | **FAIL (partial)** | address town-level and form contract re-based (done Task 6); **the twelve rebuilt pages carry the former city 0 times**. But the grep is not 0: `src/pages/available-puppies/index.astro`, `[slug].astro`, `src/pages/uk-locations/index.astro`, `src/components/PuppyList.astro` (meta descriptions and hub copy on pages this build gave the shell only), `data/page-map.json` / `data/locations.json` (the 28 location pages, build 5), plus accounting rows in `data/boards/`, `data/verbatim/` and old scorecards. Known Issue 16 stays open for the remainder, owner build 5 |
| 4 | Known Issues 8, 9, 11, 12, 20 closed; every `REVIEW_PLACEHOLDER` counted | **PASS** | `schema-date-modified-present` 0; `board_gate.py index` header-collision 0; old band and old byline 0 times on every rebuilt page; `data/page-dates.json` wired through `prebuild` and `BaseLayout`; `REVIEW_PLACEHOLDER` 0 rendered, 0 counted |
| 5 | Every rebuilt page at 0 blocking rows; blocking total below 58; `schema-date-modified-present` 0 on rebuilt pages | **PASS** | blocking **58 → 6**, none on a rebuilt page; `schema-date-modified-present` 0 site-wide |
| 6 | `check:all`, pytest, render meta green twice; gate report published with spec and plan as Artifacts; session-closer names project 5 and appends open flags | **PASS-WITH-DEVIATION** | `check:all` and render meta identical and green in both runs; pytest green in both with the two-test skip drift explained and fixed above; this report plus `docs/artifacts/bsuk-page-rebuilds-gate-report.html`, `…-spec.html` (regenerated with amendments 1–11) and `…-plan.html` built for the user to publish; session log names build 5 and appends Known Issues 35–38 |
| 7 | Every commit carries `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` | **DEVIATION** | every commit on the branch carries a `Co-Authored-By` trailer; 111 carry Fable 5.1 and the last eight — `2ce9e93` onward, including step 0 and this report — carry `Claude Opus 5.5`, as does the merge commit on `foundation`, as the controller instructed for this session (Known Issue 37) |

**Verdict count: 4 PASS · 1 PASS-WITH-DEVIATION · 1 DEVIATION · 1 FAIL (partial).**

The one real failure is row 3's literal grep: the former city is gone from every page this
build rewrote and from settings, schema and the form, and is still in the pages it gave the
shell only and in the 28 location bodies — which is build 5's scope, not a slip. Two things
are owed by people: the **OAuth rotation** (15), and the breeder's **picks on the shared
heroes** (33, 35); two are the user's to confirm: **`Button.kind`** (19) and the **trailer**
(37).
