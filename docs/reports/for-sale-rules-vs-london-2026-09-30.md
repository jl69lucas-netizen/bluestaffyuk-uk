# For-sale rules vs the London page run (2026-09-30)

Read-only audit. Scope: every rule in `rules/puppies.md` and
`.claude/skills/bsuk-puppy-page-builder/SKILL.md`, the for-sale-relevant rules of
`.claude/agents/bsuk-purchase-guide.md`, and the shared-pack heading and section rules the
for-sale builder applies (`rules/headings.md`, `docs/reference/seo-rules.md`,
`.claude/skills/bsuk-seo-master-checklist/SKILL.md`, `rules/design.md`, `rules/images.md`).
Each is checked against the London run: `data/outlines/blue-staffy-puppies-london.json`
(unapproved, `approval: null`), `data/research-boards/blue-staffy-puppies-london.json`,
`docs/research/london-page-run/`, `.claude/skills/bsuk-location-page-builder/SKILL.md`,
`docs/reference/location-page-template.md` and
`docs/superpowers/plans/2026-09-30-london-page-run.md`.

## Source limits: read this first

- **The CAG originals were not read.** A clone was reported at
  `/home/user/jl69lucas-netizen/congoafricangreys-com`, but the session's permission
  classifier refused every read of it and of the saved CAG brief. That covers `rules/for-sale.md`,
  `cag-for-sale-page-builder`, `cag-bird-page-excellence`, `cag-purchase-guide` and brief
  §§12–16, 19d. So the "in BSUK port?" column below does not diff against CAG. It records only
  what the BSUK port says about itself. A true verbatim / reworded / dropped diff needs the user
  to allow that read.
- **The two unported skills** (`data/port-manifest.json` lines 435 and 1095):
  `cag-header-search` is the site search bar, so it does not matter here (the coordinator
  confirmed this). By its name, `cag-bird-page-excellence` was CAG's page-quality bar for its
  product (bird) pages. The name suggests the transactional-page excellence rules: listing
  cards, the product layout and the per-animal presentation. It could not be read, so its
  rules are **unknown**. It is the most likely home of any for-sale rule the BSUK port lacks.
- `dist/` is empty in this worktree, so the built for-sale pages were measured from their
  `src/pages/<slug>/index.astro` source and their boards. Heading counts below are the literal
  `<hN>` tags in source. They leave out the H3s that `Faq`, `InfoCard` and `PuppyCard` render.

## Verdict

The London run carries the for-sale **data and schema rules** correctly: prices from data, a
delivery band on every card, one Product with one Offer, InStock only for an available pup,
honest scarcity, uniform image boxes, H3 then image then prose, write-from-outline and the dup
gate. It also has recorded reasons for the rules it changes. The misses are in the
**copywriting and conversion layer**: the for-sale builder's per-heading EFBP opening formula,
the reserve-CTA cadence, the five heading variants, the header dup-gate *before* outline
approval, the seam divider before every section, and the heading-count floors. As it stands
the outline holds H5 = 2 and H6 = 2, against the ≥5 the user has now ruled hard for project 5.
It holds H2 = 12 and H3 = 35, against Rule 28's 25–35 and 40–50. Neither London nor any built
for-sale page (11–16 H2 in source) meets Rule 28's H2/H3 floor, so that rule needs a ruling
rather than a fix. Count over the rows of the full table: **10 distinct MISSED** (M1–M10), **35 FOLLOWED**
(plus 3 rows partly followed), **6 DIFFERENT ON PURPOSE** (plus 1 partial), **4 NOT YET DUE**,
**8 not applicable** (transactional or cluster only).

## The MISSED rules

| # | Rule | Source | Why it applies to London | Recommended fix | Where it lands in the plan |
|---|---|---|---|---|---|
| M1 | **EFBP/EEBP opening under every H2/H3/H4**: Entity + Feature + Benefit + Purpose in the first 1–2 sentences | `bsuk-puppy-page-builder/SKILL.md:82-88`; `seo-rules.md:279-289` (Rule 37); `:311-316` (Rule 40, 50–80-word opener with a direct answer and locked numbers) | London is a transactional city page ("blue staffy puppies london"), and its first sentence is the part AI answers lift. The research board's own framework pick says so (`frameworks[0].why`). The plan asks only for a "conversational" opener (`plan:68`, `:1913`) | In Task 27 step 2, change the opener line to: answer the heading's question first, then carry Entity + Feature + Benefit + Purpose, with feature facts interpolated from `cityKit`. Apply it to H4–H6 too (`location-page-template.md:91`) | Task 27 step 2 (`plan:1913`); record the formula at STOP 2 as an outline note |
| M2 | **Reserve/enquire CTA every 500–700 words**, mid-page CTAs to `#reserve`/the form anchor | `bsuk-puppy-page-builder/SKILL.md:145-146`; seo-rules Rule 32 form placement `seo-rules.md:233-237` | The page runs 2,000–3,000 words (`plan:69`). The only conversion point is the enquiry form at row 22, and no outline row, plan step or City component carries a mid-page CTA. The built page `buy-staffy-puppies-for-sale-uk` carries 6 `href="#enquiry"` links | Add an outline note: one `#enquiry` link (or the kit `Button`) at the end of rows 8, 10, 14 and 17 (about every 600 words). Add a test in `tests/py/test_london_page.py` that counts ≥3 `#enquiry` hrefs | Task 18 (outline note) and Task 26/27 (test and wiring) |
| M3 | **Five heading variants** for H1 and every major H2 (H2 and H3 in Rule 38), with the breeder picking | `bsuk-puppy-page-builder/SKILL.md:95`; `seo-rules.md:291-292` (Rule 38) | The outline shows one wording per heading. Only the H1 had options (3 angles, `research-boards/...json` `angles[]`) | At STOP 2, publish 5 variants for each body H2, one marked (Recommended) with why and trade-off (working rule 4). H3 variants can stay optional | Task 20 (STOP 2 batch) |
| M4 | **Header dup-gate before outline approval** (`dup_content_audit.py --headers`) | `bsuk-puppy-page-builder/SKILL.md:96`, `:167-168` | 28 city siblings share one question pool, so a heading crossover found only at Task 33 (`plan:2183`) or in the post-build `outline-heading-crossover` (Task 28) means a re-approval | Before STOP 2, run a header crossover of the outline's headings against every other approved board and outline, and paste the result into the STOP 2 batch | Task 18 step 3 (`plan:~1196`) |
| M5 | **Seam divider before every section**, plus the seam-parity check | `bsuk-puppy-page-builder/SKILL.md:205-206`, `:241-242`; location builder `SKILL.md:177` names `SectionDivider` in body sections | The location builder itself names the divider. The London component map (`plan:1400-1415`) omits it, and no `City*.astro` component renders one | Add `SectionDivider` (or a London variant) to the Task 21 component map and a parity assertion to `test_london_page.py` | Task 21 step 2 map; Task 26 test |
| M6 | **≥5 H5 and ≥5 H6** | `rules/headings.md:19` (the WARN exception for location pages is now overruled for project 5 per the coordinator); `seo-rules.md:212-213` | The outline census is H5 = 2 and H6 = 2 (rows 8 only). The built for-sale pages carry 6–7 of each | Extend one H4→H5→H6 chain into at least 5 sections (the for-sale practice, below) | Task 18 / STOP 2. The other agent is changing `rules/headings.md`, `outline_matrix.py` and the outline |
| M7 | **H2 25–35 · H3 40–50** (H4 10–20 is met: 16) | `seo-rules.md:208-215` (Rule 28); `bsuk-seo-master-checklist/SKILL.md:398` | Rule 28 says "every full-length page". London holds 12 H2 and 35 H3 (FAQ H3s included) | Get a ruling: no built page meets this (the for-sale pages have 11–16 H2 in source), and 25–35 H2 in 2,000–3,000 words is one H2 per 60–120 words. Either amend Rule 28 to the 11–16 practice or scope it | Answer board question at STOP 2 |
| M8 | **Every section addresses a named buyer fear** and moves toward the form | `bsuk-purchase-guide.md:111-125` | London's angle is fear-led (deposit before viewing, `plan:54-58`), but no outline row names the fear it answers | Add a `fear` field (or a clause in `why`) per body row, drawn from the research board's `intent.emotional` | Task 18 |
| M9 | **Image on every key H4** (as well as H2/H3) | `bsuk-puppy-page-builder/SKILL.md:202` | Working rule 17 and the plan cover body H2/H3 only. 16 H4s, none with an image slot | Mark 2–4 key H4s (for example "Is the Transport DEFRA-Approved?" and "What Is Maggie Like as a Mother?") with an image slot, or record that rule 17's H2/H3 scope replaces it | Task 18 / Task 21 `assets[]` |
| M10 | **Keyword-type caps** (Rule 18: primary 30–35, LSI 20–25, long-tail 15–20, conversational 23, transactional 15, total ≤105, >110 = OVER-STUFFED) | `bsuk-puppy-page-builder/SKILL.md:64-76`; `seo-rules.md:110-135` | `evidence_audit` caps only head terms, brand and city (`data/quality/evidence-budgets.json`). `keyword_metrics.py` (`plan:1456`, `:1999`) checks front-loading, not per-type counts. Nothing counts LSI, long-tail or transactional on London | Run `bsuk-keyword-verifier` on the built page in Task 33 and record its table | Task 33 (`plan:2157`) |

## Full table

Status: **F** FOLLOWED · **M** MISSED · **D** DIFFERENT ON PURPOSE · **Y** NOT YET DUE ·
**n/a** does not apply. "In BSUK port?" is what the port says of itself (CAG not readable):
*carried* = stated in the BSUK port; *re-based* = the port says it changed the fact.

### `rules/puppies.md`

| Rule | Source | In BSUK port? | Applies? | Status | Evidence |
|---|---|---|---|---|---|
| Extended 3-part meta, title ≤280 chars | `puppies.md:19`; builder `:250-262` | carried (`enforced: untested`) | no: "all puppy/buy pages" only | n/a | London title ≤70 chars (`plan:1392-1397`). **The built for-sale pages do not follow it either**: their `meta_set` titles are 50–60 chars (`data/boards/buy-staffy-puppies-for-sale-uk.json`). It is untested and unpractised, so it is a deletion candidate |
| Delivery band on every card + delivery section; deposit stated wherever the band is | `puppies.md:27` | re-based | yes | F (band) · D (deposit wording) | `CityPuppySheet.astro:14,75`, `tests/py/test_puppy_card_delivery.py`; outline row 9. The deposit is never called plainly "refundable": `plan:59-63` Ruling 2 and `test_the_deposit_is_never_plainly_refundable` (`plan:1806`). **Conflict**: `puppies.md:27` and location builder `SKILL.md:80` still say "£500 refundable" |
| One Product per pup, exactly one Offer, ItemList | `puppies.md:36` | carried | yes, where a card shows | F | outline `schema`; location builder `SKILL.md:322-325` |
| InStock only on an available pup | `puppies.md:45` | carried | yes | F | location builder `SKILL.md:323-325`; `schema-sold-not-instock` |
| No head-cropped portraits | `puppies.md:54` | carried (London-measured) | yes | F | `img-face-visible` (advisory), render Task 29; `data/image-focus.json` |
| Order (1) hero → separator → counters | `puppies.md:63` | carried | yes | F | location builder `SKILL.md:188,232-235` (blocking) |
| Order (2) H3 → image → prose | `puppies.md:63` | carried | yes | F | `plan:1933`; `layout-h3-image-first` blocking |
| Order (3) mobile hero image first by CSS `order`, DOM keeps H1 first | `puppies.md:63` | carried | yes | D | Superseded by `rules/design.md:54` rule 10 (image first **in the DOM**); `CityHeroFilmstrip.astro:153`. `puppies.md` now contradicts `design.md` and should be amended |
| Order (4) further-reading thumbs = target hero | `puppies.md:63` | carried | only if cards | n/a | London has no further-reading cards; nearby cities are text links (`links-plan.md:33-37`) |

### `bsuk-puppy-page-builder/SKILL.md`

| Rule | Source | In port? | Applies? | Status | Evidence |
|---|---|---|---|---|---|
| Board first; `board_gate` | `:22-26` | carried | yes | Y | Tasks 21–23 |
| Query augmentation first; every pick an H3; `must_answer` covered | `:28-33` | carried | yes | F | Task 10; outline FAQ rows 7, 12, 21 |
| Cannibalisation guard: one intent, distinct keywords, a unique 4–5 city set | `:58-60` | carried | yes | F | angle A1 (deposit/video); 4 nearby cities (`links-plan.md:33-36`) |
| Keyword-type caps ≤105 | `:64-76` | carried | yes | **M10** | see above |
| No search-console figures until project 6 | `:78-80` | carried | yes | F | research board `method` (volumes NOT FETCHED) |
| EFBP opening under every H2/H3/H4 | `:82-88` | carried | yes | **M1** | `plan:68,1913` ask only for "conversational" |
| Conversational Q&A headers | `:91` | carried | yes | F | `header_style` Style 1 FAQ register; `test_every_body_h2_and_h3_is_a_question` |
| H1→H6 outline approved before code, no skipped level, all six levels | `:91-93` | carried | yes | F | STOP 2 (`plan:1292`); census has all six levels |
| ≥5 H5 and ≥5 H6 | `:93` | carried | yes (ruled hard) | **M6** | census H5 2 · H6 2 |
| Semantic level map | `:94` | carried | yes | F | outline tree (H4 micro-answers, H6 breeder notes) |
| 5 A/B variants for H1 and major H2 | `:95` | carried | yes | **M3** | H1: 3 angles only |
| Unique hybrid headers; header dup-gate before approval | `:95-96`, `:167-168` | carried | yes | **M4** | only after the build (`plan:2183`) |
| 85–112 distinct entities; brand 5–10×, city 5–8× | `:98-106` | carried | partly | D | `location-page-template.md:158-159` ("as many real local entities as the city supports, none invented"); brand and city caps via `evidence-budgets.json` |
| Three meta sets, one (Recommended) | `:108-111` | carried | yes | Y | `meta_set` is required by `schemas/board.schema.json:7,375`, but `plan:1392` names one title. Task 21 should list three |
| 8 counters, <4 words, from the locked set only | `:113-117`; Rule 31 `seo-rules.md:226-231` (4 counters) | carried | partly | D | Working rule 16: a page's own figures on its own board; `CityPriceScale`, stats from data only (`plan:1405`). The format (<4 words, number-led) should still be stated at Task 21 |
| Link-First; anchor ledger; library-only externals; new-tab + ↗ | `:119-126` | carried | yes | F | `plan:1268,1926`; `anchor-reuse-sitewide`; `external-links-six-diverse` |
| Puppy cards near the fold | `:130` | carried | partly | D | fixed frame `location-page-template.md:49-68`; the litter is row 10 after the deposit row by angle A1 (STOP 1) |
| Honest scarcity only | `:147-149` | carried | yes | F | CLAUDE.md rule 9; `availablePuppies()` |
| Reserve CTA cadence 500–700 words | `:145-146` | carried | yes | **M2** | — |
| Enquiry form, puppy select from data | `:150-157` | carried | yes | F | row 22, `CityContactLineup` → form contract `form-inquiry-contract` |
| Research phase deliverables | `:161-164` | carried | yes | F | Tasks 5–16 |
| Two strategies + one blended | `:165-166` | carried | yes | D | Research board S1/S2/S3 as three directions, no blend. Location builder `SKILL.md:14,30` says "2–3 strategy directions" |
| MANDATORY / COMPETITOR-BASED / SUGGESTED groups | `:166-167` | re-based | yes | F | Cat A/B/C (location builder `SKILL.md:46`). **Note**: London has no B row, because only 1 prose competitor was used |
| Skeleton screens, then HARD STOP for images | `:168-169` | carried | yes | Y | STOP 3 previews, STOP 4 Asset Gate (Task 25) |
| Build section by section, verify `dist/`, commit | `:170-171` | carried | yes | F | Tasks 26–28 |
| QA: dup (body + headers), final audit, sitemaps, no push | `:172-175` | re-based (`--type location`) | yes | F | `gate:page` (`plan:2183`) |
| Hero ~400px, hero → separator → counters | `:179-181` | carried | yes | F | location builder `SKILL.md:233` (390–450) |
| Dial TOC that works + jump-rail scroll-margin | `:182-185` | carried | yes | F | `CityDialPhotoMarker`, `CityJumpStepper` (sticky); `nav-jump-target-lands` |
| Card crop 800×800; body box uniform 16:9 | `:186-189` | carried | yes | F | `test_uniform_image_box.py` (Task 24); `plan:1933` |
| Portraits 4:5 contain, `box="tall"`, never blur-fill | `:190-201` | carried | yes | F | `plan:1933`; location builder `SKILL.md:190` |
| Image on every H2, H3 **and key H4** | `:202` | carried | yes | F (H2/H3) · **M9** (H4) | rule 17; outline `image` per row |
| <100 KB WebP, -760 sibling, srcset, dims; no shared alt | `:202-204` | carried | yes | F | location builder `SKILL.md:215`; `test_served_alt_preserved.py` |
| Seam divider before every section; seam parity | `:205-206`, `:241-242` | carried | yes | **M5** | not in `plan:1400-1415` |
| Further reading 2-up + location-aware delivery block | `:207-209` | carried | partly | D | the delivery row 9 carries the nearby-city links (`links-plan.md:33-37`) in place of cards |
| No page sidebar; sticky mobile CTA bar | `:210-211` | carried | yes | M (in M2) | no City component has a sticky CTA. `CityJumpStepper` is sticky navigation, not a CTA. The built for-sale pages have none either |
| Stale-fact reconciliation on any design-kit intake | `:212-217` | carried | yes | F | `plan:65` Ruling 6; `test_no_price_is_typed_in_the_page_source` |
| Write-from-outline, never from a sibling | `:221-229` | carried | yes | F | `plan:1905`; `outline_provenance_check.py` (Task 28) |
| `final_page_audit` PASS | `:231` | re-based | yes | Y | Task 33, `--type location` |
| Manual list: unique newsletter image and one-line title; opener under every header; table stacking; AA; warm median Lighthouse | `:232-235` | carried | yes | F | `CityNewsletterNotice` (image); rule 13 `CityRoster`; `perf_audit` warm median of runs 2–5 (`plan:2185`); `sem-section-opening-paragraph` checks all levels (`tests/render/checks/sem.ts:196`, advisory) |
| Voice sweep + anti-ai + evidence pass | `:236-237` | carried | yes | F | `plan:1913`; `evidence_audit --fail-on-error` in `gate:page` |
| Verify gate findings first | `:243-246` | carried | yes | F | `rules/gates.md`; Task 29 meta gate first |
| Perf needs ≥5 runs | `:247-248` | carried | yes | F | `plan:2185` |
| Component fidelity (never a neighbour's kit) | `:264-270` | carried | yes | F | `test_every_component_on_the_page_is_a_london_pick…` (`plan:1863`) |
| Hub rule | `:272-278` | carried | no: `/available-puppies/` only | n/a | — |
| Price-matrix via helper, pup cards | `:130-131` | carried | yes | F | `cityKit` interpolations (`plan:1914-1921`) |

### Purchase guide and shared packs

| Rule | Source | Applies? | Status | Evidence |
|---|---|---|---|---|
| Two-keyword conversational headers | `bsuk-purchase-guide.md:11`; `bsuk-seo-master-checklist/SKILL.md:405` | no: the master checklist excludes location pages (its description) | n/a | — |
| BreadcrumbList schema | `bsuk-purchase-guide.md:11` | yes | F | outline `schema` |
| Every section answers a buyer fear | `bsuk-purchase-guide.md:125` | yes | **M8** | — |
| FAQ in QAB, ≥8, FAQPage schema | `bsuk-purchase-guide.md:174-179` | yes | F | 20 QAB questions across 3 blocks; FAQPage |
| Pricing table vs market averages | `bsuk-purchase-guide.md:161-166` | no: a market figure would be un-fetched | n/a | rule 9 |
| Testimonials in BAB | `bsuk-purchase-guide.md:181-186` | no: London shows the 3 real reviews verbatim | n/a | location builder `SKILL.md:237-243` |
| H1 sacred, 15-section map | `bsuk-purchase-guide.md:51,83-103` | no: buy page only | n/a | — |
| Title Case | `rules/headings.md:28` | yes | F | blocking `sem-title-case-headings` |
| Header style declared + reason | `rules/headings.md:36` | yes | F | outline `header_style` (Style 1, user 2026-09-27; the location default Style 2 is overridden with a reason) |
| Rule 28 H2 25–35 / H3 40–50 / H4 10–20 | `seo-rules.md:208-215` | yes | **M7** (H2/H3) · F (H4 16) | — |
| Rule 32 form 3× per page | `seo-rules.md:233-237` | yes | D | one form in the fixed frame (`location-page-template.md:68`); the built for-sale pages carry 1 each too |
| Keyword density 1–2% page / 0.8–1.2% section | `seo-rules.md:113,136-137` | yes | M (in M10) | — |
| Entity density 95–105 (Rule 57) | `bsuk-seo-master-checklist/SKILL.md:265` | no: that skill excludes location pages | n/a | — |

## What the built for-sale pages do that no written rule states

Measured from source (`<hN>` tags written in the page; kit-rendered FAQ, InfoCard and
PuppyCard headings are not counted):

| Page | H2 | H3 | H4 | H5 | H6 | Body images | `#enquiry` links | Dividers |
|---|---|---|---|---|---|---|---|---|
| `blue-staffy-pup-sale-uk` | 11 | 13 | 6 | 6 | 6 | 4 | 2 | 0 |
| `buy-blue-staffy-puppies-uk` | 12 | 11 | 6 | 6 | 6 | 6 | 1 | 3 |
| `buy-staffy-puppies-for-sale-uk` | 16 | 26 | 7 | 7 | 7 | 12 | 6 | 0 |

- **H4 = H5 = H6 on every page (6–7 each).** Each deep section runs one H4 → H5 → H6 chain,
  and there are 6–7 such chains. No rule states this "one full ladder per section, ≥6
  sections" shape, yet it is how they clear ≥5 H5/H6. London has one chain (row 8).
- **11–16 H2**, far below Rule 28's 25–35. That rule is unpractised site-wide.
- **Short meta titles (50–60 chars) in a three-title `meta_set`**, not the 280-char format
  `puppies-extended-meta` asks for.
- **Mid-page `#enquiry` links (1–6 per page), one form, no sticky CTA bar.** This is the
  working form of the CTA-cadence rule, and London has none of it yet.
- **Seam dividers are inconsistent** (0, 3, 0). Seam parity (`builder:241-242`) is not
  practised either.
