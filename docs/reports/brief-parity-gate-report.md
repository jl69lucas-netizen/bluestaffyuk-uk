# Brief Parity — Gate Report

**Build:** the brief-parity bridge between the project 5 readiness pass and project 5, 2026-09-26/27. It closes the gaps that the CAG page-brief parity audit found (`docs/reports/cag-brief-parity-audit.md`). **Branch:** `cag-parity` (worktree `/Users/apple/Downloads/BSUK-cag`), cut from `foundation` at `0454a96`. HEAD at the gate run was `5893869`, 83 commits `b99d7d6..5893869`, and every one carries the Fable 5.1 trailer. Nothing is pushed. **Plan:** `docs/superpowers/plans/2026-09-26-cag-parity.md` (28 tasks, replayed green by the controller before execution). **Execution:** subagent-driven. Every task had an Opus implementer, a spec review and a quality review, re-reviewed until both passed. A whole-branch review followed (Task 28a).
**Artifact:** https://claude.ai/artifact/MiQXGY16rYKz1betiZR6q1

## Verdict

**PASS WITH DEVIATIONS: all 27 audit gaps and both decisions are closed on the branch. The count is 24 PASS, 5 PASS-WITH-DEVIATION and 0 FAIL.** The build, both `check:all` runs, both pytest runs and the render meta suite are green. The only red gate is the page render run's pre-existing `nav-jump-target-lands` on `uk-locations/blue-staffy-puppies-uk` (execution note 8; Known Issue 81). Three decisions are open on the answer board before the London board (Known Issue 85).

## Definition of done

Evidence keys refer to the commands under "Gates run twice" below. A row says PASS only when one of those commands, run this session, backs it. "E-P" means the named test file is part of the suite that passed with 0 failures on both runs.

| Audit row | Change | Task | Commits | Result | Evidence |
|---|---|---|---|---|---|
| 1 | Invented method label deleted (D1); residue lint | 1 | `4c921ce 90db8fd 1b148de` | PASS | E-P `tests/py/test_agent_facts.py` |
| 2 | City term per slug + brand budget (D2) | 2 | `c6b0756 82ab14b` | PASS | E-P `tests/py/test_evidence_city_budget.py` |
| 3 | PuppyCard delivery line + dist test (D4) | 3 | `65ba9da` | PASS | E-P `tests/py/test_puppy_card_delivery.py` |
| 4 | Rule 18: a ceiling of 105, no floor | 4 | `4506872 1cc2bd3 7dd7744` | PASS | E-P `tests/py/test_rule18_frequency.py` |
| 5 | `perf_audit.py`: 5 runs, warm median of runs 2–5 with spread | 5 | `a265b7b c11204f` | PASS | E-P `tests/py/test_perf_audit.py` (no live perf run was part of this gate) |
| 6 | Doc drift batch (seven items) | 6 | `98533d1 4751ee3` | PASS | E-P `tests/py/test_doc_drift.py`, `tests/py/test_rules_index.py` |
| Decision: in-body image box | (a) uniform box on new pages; bleed in design colours, never blurfill (user note) | 8 | `036c444 a7a6e36 1146507 cc26cf5` | PASS | E-P `tests/py/test_uniform_image_box.py`, `tests/py/test_no_blurfill_bleed.py`; answers `ac01ec0` |
| Decision: global CTA | (a) `hidden` hides the footer band (D3) | 7 | `fb32212 13623cf`, then `dd29aec` (city lookup) | PASS | E-P `tests/py/test_global_cta.py`; E-D shows the 12 rebuilt pages changed, and the plan's replay attributes 11 of them to the hidden band. The city template never had the band (Known Issue 87) |
| 7 | Retired-facts sweep over `data/`, `src/`, `dist/` (D5) | 9 | `d196042 7c270a5 eed8178` | PASS-WITH-DEVIATION | E-C `retired-facts: examined 51 built pages, 117 data fields/files, 70 src files; 61 allowlisted (Known Issue 65), 0 new, 0 stale`. Deviation: the plan froze 48 offenders. The review rounds widened detection ('to' ranges, unprefixed ranges, former-home claims), so the allowlist is 61 (48 → 57 → 61). The offenders are still live (Known Issue 82) |
| 8 | Every rebuilt page is a render target; `comparison` page type | 10 | `f8f68d6 9384e77` | PASS | E-P `tests/py/test_targets_coverage.py` |
| 9 | Zero-examined guard after the page run + meta test | 11 | `3e540d3 5f9c858 43e2df0` | PASS | E-S exit 0; E-L M1 `31 checks, 0 at zero`; E-M 415 passed |
| 10 | `board_gate.py` over every rebuilt page in `check:all` | 12 | `8f8d1b7 f57659f` | PASS | E-C `board-gate --all: examined 12 rebuilt pages against 51 live pages; 0 failed` |
| 11 | Approval refuses `header-collision` on new pages | 13 | `ed36bc0 06beb90 53e3125` | PASS | E-P `tests/py/test_board_approve_header_collision.py` |
| 12 | `layout-h3-image-first` on `.bl-img`; `promotions`; four checks block new pages | 14 | `7305f0d 791ec39 8add6ce` | PASS-WITH-DEVIATION | E-M "the four project 5 promotions are on record" and the promotions tests pass; E-P `tests/py/test_render_baseline.py`. Deviations: `layout-h3-image-first` has never passed on a real page, because only the frozen pages exist and they carry true reports (Known Issue 90). The regenerated `render-baseline-project4.md` also moved rows that earlier tasks caused (A11Y 6→0, sem-heading-order blocking 3→0, DUP 42→45) under the Task 14 commit |
| 13 | Hardening scan reads the city template, its data and the kit | 15 | `63e2776 93af5da` | PASS | E-P `tests/py/test_page_hardening_scope.py`; the 369 pre-existing ERRORs are debt (Known Issue 88) |
| 14 | Rendered-changes list at every close (D6) | 16 | `dd3bd1e 57995dd` | PASS | E-D `12 changed, 0 removed, of 51 built pages`, exactly the 12 rebuilt pages; E-P `tests/py/test_rendered_changes.py`, `tests/py/test_indexnow_submit.py` |
| 15 | Competitor page metrics in `competitors.json`; Rule 27 word target | 17 | `0f4dc70 f58abd8 96d9a3c 317622c 8e773e5` | PASS-WITH-DEVIATION | E-P `tests/py/test_competitor_metrics.py`. Deviations: Manchester's 8 pages are measured, but its `word_target` is NOT FETCHED because all 8 are marketplace listings or blocked. Leeds has no HTML cache, so its 8 pages carry no `metrics` (Known Issue 84). The fallback band waits for the board (Known Issue 85) |
| 16 | `keyword_metrics.py` ours-vs-top-5 table; first-100 and title front-load fail new pages | 18 | `6884f13 fddd147` | PASS | E-P `tests/py/test_keyword_metrics.py`; the frozen-page debt is Known Issue 90 |
| 17 | Geo-token + two-keyword-header board checks | 19 | `01b6e0d a8126d4` | PASS | E-P `tests/py/test_geo_and_header_keywords.py` (advisory WARN by the plan's design) |
| 18 | Claim ledger inverted: an un-ledgered health or credential claim fails | 20 | `8a74f5a e5b7eef 9241914 664993b` | PASS | E-P `tests/py/test_evidence_unledgered.py`. It is ERROR on new pages through `gate:page`, WARN on migrated and frozen pages (Known Issue 89) |
| 19 | `NOT FETCHED — <barrier>` lint (`check:barriers`) | 21 | `aed837b b714435` | PASS | E-C `not-fetched-lint: examined 148 files (13 grandfathered); 0 problems` |
| 20 | Shared Reddit thread ledger (`check:threads`) | 22 | `d8bb154 749b628 3a95384` | PASS | E-C `thread-ledger: examined 2 threads files, 14 threads; 0 problems` |
| 21 | `docs/reference/page-run.md`, guarded by `check:workflow` | 23 | `160d7ad 09c2bf3 21c8547 f0c19b3`, then `ee0bf14` | PASS | E-C `workflow-ref-check: examined 341 references in 3 files; 0 problems`; E-P `tests/py/test_page_run.py` |
| 21b | `impeccable` + `frontend-design` mandatory on every page, recorded in `data/page-runs/<slug>.json` | 23, 25 | as rows 21 and 23 | PASS-WITH-DEVIATION | Routed in CLAUDE.md, WORKFLOW, page-run.md and the location, comparison and blog-post builder skills; E-P `tests/py/test_page_run_record.py`, `tests/py/test_gate_page.py`, `tests/py/test_claude_md.py`. Deviation: the audit wanted the record to make "ran it" provable. The operator writes the record (an honour system), and the gate only forces a re-record after any later page change (Known Issue 91) |
| 21c | `verification-before-completion` mandatory at the end of Sprint 4 and at close | 23, 25 | as rows 21 and 23 | PASS | Routed in CLAUDE.md, WORKFLOW, the three builder skills and session-closer. `gate:page` runs `check:all` itself and treats the record's exit codes as informational (`scripts/gate_page.py` docstring); E-P `tests/py/test_gate_page.py` |
| 22 | Board intake block 0; close Known Issue 63 | 24 | `71d961d 05b79a4` | PASS | E-P `tests/py/test_page_intake.py`; Known Issue 63 marked CLOSED |
| 23 | `npm run gate:page -- <slug>`: every page gate twice, diffed; run-twice rule | 25 | `fed0d17 1fc65a6 862bf1c`, then `dd29aec 0c7bf89` | PASS | E-P `tests/py/test_gate_page.py`. No project 5 page exists yet, so ledger M8 is EMPTY |
| 24 | `measurement_ledger.py`: M1–M3, M6, M8–M10, M12, M13, M18 | 26 | `54d5e1c fdc2222 677946f 769465d` | PASS | E-L exit 0, `failed: none · stale: none`; E-P `tests/py/test_measurement_ledger.py` |
| 25 | URL-family decision table for the city cluster and comparison slugs | 27 | `2c35b2f c9ce585` | PASS-WITH-DEVIATION | `docs/research/2026-09-26-url-family-decision.md`; E-P `tests/py/test_url_family_decision.py`. Deviation: the decision is written but not taken. It is q1 of the open board batch (Known Issue 85), and the review found that the UK hub's body does not link the 9 indexable cities (Known Issue 86) |

**Counts:** 29 rows (27 gaps + 2 decisions), with **24 PASS, 5 PASS-WITH-DEVIATION and 0 FAIL**.

### The audit's live defects

| # | Defect | Closed by | Commits |
|---|---|---|---|
| D1 | Invented method label | Task 1 | `4c921ce 90db8fd 1b148de` |
| D2 | City-term budget hard-coded to Glasgow | Task 2 | `c6b0756 82ab14b` |
| D3 | `global_cta: "hidden"` ignored by the footer | Task 7 (+ 28a) | `fb32212 13623cf dd29aec` |
| D4 | Puppy cards without a delivery line | Task 3 | `65ba9da` |
| D5 | Retired facts unswept on the city pages | Task 9, as a failing gate. The 61 allowlisted offenders stay live until each page is rebuilt (Known Issues 65, 82) | `d196042 7c270a5 eed8178` |
| D6 | IndexNow `--changed` blind to city pages | Task 16 | `dd3bd1e 57995dd` |

### Work beyond the plan

- **Task 28a, the whole-branch review fixes** (`dd29aec`, `ee0bf14`, `0c7bf89`):
  - The global CTA looks up a city page's board.
  - `gate_page` gained the `board` and `listed` steps.
  - An entity-blocked board refuses approval.
  - The dirty-tree rule spares the build's outputs and `data/page-dates.json` while it is current.
  - The close order is documented, and the grill-me route fixed.
  - The builder skills list the gates.
  - A sweep replaced `npx astro build` with `npm run -s build`.
- **Task 26 review rounds** (`fdc2222`, `677946f`, `769465d`): the ledger never passes on nothing. It checks freshness by ancestry and page hash, and the gate head ignores untracked and generated files.
- **Task 27 review** (`c9ce585`): the URL-family decision flags the hub's missing city links.
- **Answer board** (https://claude.ai/artifact/2psVTYc8oYQvdpibyviAcf):
  - Batch `2026-09-26-brief-parity-two-decisions-before-project-5` is answered (`ac01ec0`): q01 (a), with the note that bleed uses the design colours and never grey or black, and q02 (a).
  - Batch `2026-09-27-brief-parity-close-three-decisions-before-the-london-page` is posted (`5893869`) and **OPEN**. It asks about the URL family, the comparison slug and the fallback word band.

## Gates run twice

Run by the controller in `/Users/apple/Downloads/BSUK-cag` at `5893869` on 2026-09-27 (Task 28 Steps 1–2).

| Key | Command | Run 1 | Run 2 |
|---|---|---|---|
| E-B | `npm run -s build` | exit 0 | — |
| E-C | `npm run -s check:all` | exit 0 | exit 0 |
| E-P | `python3 -m pytest tests/py -q -p no:cacheprovider` | exit 0 — `6222 passed, 12 skipped, 1 xfailed` | exit 0 — `6222 passed, 12 skipped, 1 xfailed` |
| E-M | `npm run test:render:meta` | exit 0 — `415 passed`, `38 skipped` | — |
| E-R | `npm run test:render:pages` | exit 1 — `57 passed`, `3 failed` | — |
| E-S | `node scripts/build_scorecard.mjs` | exit 0 — `195 defect ROWS across 20 pages (run=first, harness 2.0.0)` | — |
| E-D | `python3 scripts/rendered_changes.py --base /Users/apple/Downloads/BSUK/dist --json` | exit 0 — `12 changed, 0 removed, of 51 built pages (51 in the base)` | — |
| E-L | `python3 scripts/measurement_ledger.py brief-parity --md …` | exit 0 — `failed: none; stale: none; empty: M6, M8, M10, M12` | — |

- **pytest:** the plan's replay expected 5771 passed. The real branch has more tests from the review rounds, and both runs agree with 0 failed, which the plan allows.
- **The three render failures** are all `uk-locations/blue-staffy-puppies-uk`, with the message `[NAV] 1 of 2 in-page links land outside` the landing band. The first link is `#Staffy-adoption`, at 2847px (375), 3495px (768) and 3493px (1280). This failure predates the plan (execution note 8; Known Issue 31's second half, now Known Issue 81). Every other page passes at all three widths.
- **Rendered changes:** the 12 changed pages are `blue-staffy-blog-guides`, `blue-staffy-health-uk`, `blue-staffy-pup-sale-uk`, `blue-staffy-uk-breeders`, `buy-blue-staffy-puppies-uk`, `buy-staffy-puppies-for-sale-uk`, `index`, `privacy-policy-uk`, `thank-you-blue-staffy-puppies-journey`, `uk-blue-staffy-breeders-contact`, `uk-blue-staffy-puppy-buying-guide` and `uk-staffordshire-bull-terrier-guide`. These are the 12 rebuilt pages, and no migrated page is among them. `docs/reports/rendered-changes.json` is git-ignored, so it is not committed.
- **Scorecards and baseline:** the close commit carries the run's 20 scorecards (`data/quality/scorecards/*-2026-09-27.json`, page-run.md row 21). With those scorecards present, `tests/py/test_render_baseline.py` read `docs/reports/render-baseline-project4.md` as stale, so the close regenerated its generated block with `python3 scripts/render_baseline.py --write docs/reports/render-baseline-project4.md`. Only the run date changed (2026-09-26 → 2026-09-27; still 20 scorecards and 195 rows), and `npm run -s baseline` now reports `0 problems`.

Also measured by the close-out this session (read-only; output kept outside the repo):
- `npm run -s registry` → `0 problems`: the generated registry is current.
- `python3 scripts/page_hardening_scan.py` → `369 ERROR · 35 WARN`, exit 0 (report-only). All 369 ERRORs are `header-not-title-case`: board-preview 306, uk-locations 41, kit-preview 19 and available-puppies 3.
- `python3 scripts/evidence_audit.py --all` → exit 1, `examined 61 pages; 42 problems (192 WARN)`. The ERRORs are term budgets on migrated pages, and 133 of the WARNs are un-ledgered claims.
- `python3 scripts/keyword_metrics.py <slug>` on the 12 frozen pages → `first_100` false on 11 of 12 and `title_front` false on 6.

## Measurement ledger

`python3 scripts/measurement_ledger.py brief-parity`, run at HEAD `5893869`: exit 0, 10 rows, 0 pages in scope.

Measurement ledger — brief-parity · 2026-09-27 · scope none · HEAD 5893869aedd282b73c24409c3b8c7801f24c8f13 · failed: none · stale: none · empty: M6, M8, M10, M12

| # | Measurement | Value | Status | Detail |
|---|---|---|---|---|
| M1 | Nodes examined per check, on real pages | 31 checks, 0 at zero (run 2026-09-27, 20 pages) | PASS | — |
| M2 | Families registered vs families wired | registered 9 · wired 9 · difference ∅ | PASS | — |
| M3 | Advisory findings vs blocking failures | blocking 3 · advisory 192 (run 2026-09-27; never summed) | REPORTED | — |
| M6 | Minimum rendered text >= 12.5px | no project 5 page in scope yet | EMPTY | — |
| M8 | Gate runs per page, both clean | no project 5 page in scope yet | EMPTY | — |
| M9 | Rework rate: page vs harness, never merged | NOT FETCHED — data/quality/rework-ledger.json holds no window yet | REPORTED | — |
| M10 | Dup crossover, body and headers | no project 5 page in scope yet | EMPTY | — |
| M12 | LLM visibility cells fetched / total | no project 5 page in scope yet | EMPTY | — |
| M13 | Slugs whose rendered output changed | 12 (base /Users/apple/Downloads/BSUK/dist → head 5893869aedd282b73c24409c3b8c7801f24c8f13) · IndexNow submitted: NOT FETCHED — project 6 | REPORTED | blue-staffy-blog-guides, blue-staffy-health-uk, blue-staffy-pup-sale-uk, blue-staffy-uk-breeders, buy-blue-staffy-puppies-uk, buy-staffy-puppies-for-sale-uk, index, privacy-policy-uk, thank-you-blue-staffy-puppies-journey, uk-blue-staffy-breeders-contact, uk-blue-staffy-puppy-buying-guide, uk-staffordshire-bull-terrier-guide |
| M18 | Untested rules in the rule index | 17 of 81 rules | REPORTED | design-context-read-first, entity-4-move-loop, header-style-declared, image-keyword-distribution, link-first-anchors, meaningful-words-no-stop-words, no-credential-in-a-committed-file, no-head-cropped-portraits, puppies-extended-meta, read-card-thumb-is-target-hero, release-guarded-publication, reuse-every-image-and-video, same-content-on-redesign, src-pages-is-deployed, verify-the-gate-first, visual-companion-always, visual-first-workflow |

The 3 blocking rows in M3 are the nav-jump page at three widths. The EMPTY rows fill once project 5 builds its first page (Known Issue 92 covers M18).

## Integration conflicts

The table below is the plan header's, copied unchanged. Each resolution holds at HEAD:
- The `check:all` chain in `package.json` is the 19 items in execution note 4's order, and `test_package_scripts` and `test_doc_drift` pin CLAUDE.md's sentence to it.
- `scripts/evidence_audit.py` keeps `REBUILT_PATH`, `LOCATIONS_PATH` and `CITY_TERM`.
- `npm run -s registry` reads the registry as current.

None differed from the plan as far as the commits and these checks show.

| When | File | Conflict | Resolution |
|---|---|---|---|
| Task 9 | `CLAUDE.md` | Task 6 re-wrapped the "`check:all` chains" sentence | Keep Task 6's sentence and insert `` `check:retired` `` after `` `check:placeholders` ``, so the sentence matches `package.json` (note 4) |
| Task 12 | `CLAUDE.md` | Same sentence | Insert `` `check:boards` `` after `` `check:retired` `` |
| Task 18 | `docs/reference/system-registry.md` | Generated file | Regenerate (note 5) |
| Task 20 | `scripts/evidence_audit.py` | Task 2 added `LOCATIONS_PATH` and `CITY_TERM` where Task 20 adds `REBUILT_PATH` | Keep all three constants |
| Task 21 | `package.json`, `tests/py/test_package_scripts.py`, `CLAUDE.md`, registry | Task 21's anchors predate Tasks 9 and 12 | Insert `check:barriers` after `check:gaps` in the current chain, list and sentence; regenerate the registry |
| Task 22 | same four files | Same | Insert `check:threads` after `check:barriers` |
| Tasks 24–27 | registry | Written against a stand-in registry | Apply the task and regenerate the registry |

## Open items for project 5

Each item is a Known Issue in `docs/reference/session-log.md`.

- **81:** `nav-jump-target-lands` on `uk-locations/blue-staffy-puppies-uk` (`#Staffy-adoption`). This is the only red render row, and the hub refresh fixes the anchor target.
- **82:** Burn down the retired-facts allowlist city page by city page. It holds **61** entries on 11 pages, not the plan's 48 (Known Issue 65).
- **83:** Keep the four new-page promotions (`layout-h3-image-first`, `layout-hero-counter-separation`, `sem-section-opening-paragraph`, `sem-title-case-headings`) scoped to new pages until one full project 5 cluster runs clean.
- **84:** Leeds has no competitor HTML cache, so no metrics and no word target. Manchester's word target is NOT FETCHED.
- **85:** Three answer-board decisions are open before the London board: the URL family (Task 27), the comparison slug and the fallback word band.
- **86:** The UK hub's body does not link the 9 indexable city pages.
- **87:** The city template uses `BaseLayout` and the legacy footer. Project 5's city template must move to `PageShell` for `global_cta` to apply.
- **88:** Hardening debt: 369 pre-existing `header-not-title-case` ERRORs. The legacy city FAQ H3s fail `gate:page` until each page is rebuilt.
- **89:** Evidence debt: 42 ERRORs and 192 WARNs, 133 of them un-ledgered claims. The `dna-clear` ledger row also matches PHPV.
- **90:** Frozen-page debt: advisory `h3-image-first` reports on 4 pages, and 11 of 12 pages lack the primary keyword in their first 100 words.
- **91:** The harden passes are self-recorded.
- **92:** M18: 17 rules are untested.
- Known Issue 73 (stale committed boards) is extended, not renumbered. The boards were not regenerated at this close, and no approval changed.

## Adopt later

The audit's list, unchanged:

- Entity count, co-occurrence pair table and predicate triples (§8) — worth it once the first city
  pages exist to measure against.
- Voice/tone, "why they rank" and depth fields in competitor gaps (§9).
- H2 A/B variants ×5 (§12 — BSUK does the H1 only).
- Dial scroll-spy Playwright spec and Link-First anchor check (§13, §16c) — cheap, can ride along
  with the first city page.
- LLM visibility re-measure after deploy, the score, and Search Console baselines — project 6
  (live domain).
- Run tracker and live ledger dashboard (§26 stages 3–4).
