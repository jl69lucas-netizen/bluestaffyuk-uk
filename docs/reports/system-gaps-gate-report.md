# System Gaps — Gate Report

**Build:** the system-gaps bridge between projects 4 and 5, 2026-09-24. **Branch:** `system-gaps` (worktree `/Users/apple/Downloads/BSUK-gaps`), cut from `foundation` at `9927710`. **Plan:** `docs/superpowers/plans/2026-09-24-system-gaps.md` (Artifact https://claude.ai/artifact/FS2ekGxx7jAM5T8poem95R). **Merged:** `--no-ff` into `foundation` at `06dee26`; `foundation` after the merge: build 0, 2993 passed, 14 skipped, 1 xfailed, `check:all` 0. **This report:** https://claude.ai/artifact/VFCVy6avEXQ7gGKVcD2mae. **Execution:** subagent-driven. Every task had an Opus implementer, a spec-compliance review and a code-quality review, re-reviewed until both passed. Each task was also checked against a full rehearsal of the plan (`wt-int`, run in plan order before execution).

## Verdict

**PASS, with one item waiting on the user.** All five gaps are closed on location, comparison and blog pages built from now on, and the twelve built pages are untouched: approvals match, and the pages and boards are unchanged apart from the intended board blocks. Tasks 0–12a are all done, each with a spec review and a quality review. The final whole-branch re-review said **ready to merge: YES**. The one open step is Task 11b's real smoke image, which needs the user's `GEMINI_API_KEY` (KI 70). The package is installed and the full generate → approve → publish flow is tested.

## The user's five gaps

| # | Gap (the user's words, shortened) | Closed by | Evidence | Result |
|---|---|---|---|---|
| G-1 | Board entity section: "hard to read or zoom on individual entities … shows titles/headers not each entity; clean, fluid scrolling" | Task 3 | `scripts/board_entities.py`. One card per entity, grouped by class, with a sticky filter and search, section chips that jump to the outline, and a per-class matrix that stacks on phones. The graph is removed. Headless browser test for the filter and search; 375px scrollWidth = 375 | PASS |
| G-2 | "All keyword variations, related, concurrent, similar, and all entity types grouped by people, place, health, etc." | Tasks 1, 2, 3 | Four optional keyword types plus `keyword-variants-missing`. `scripts/keyword_variants.py` proposes terms from cached data only (Manchester 8/6/12/8). The ontology grows from 7 to 56 sourced entities in 8 classes (People 1, Place 27, Health 6 PROPOSED, Organization 12, Regulation 6, Organism 2, Commerce 1, Logistics 1). Board block 4 shows the chips by type | PASS |
| G-3 | "Build from outline; never from crossovers, siblings, or duplicates; 6 diversity external links per page; anchor type/variations" | Tasks 4, 5, 6, 6b | `external-links-six-diverse` (≥6 links / 6 domains / 4 source types; 10 new verified library rows). `anchor-type-variation` and `anchor-reuse-sitewide` (the first owner keeps its anchor). `scripts/outline_provenance_check.py` in `check:all` covers extra, missing and reordered headings, duplicates, and crossovers including city swaps. `outline-heading-repeat` catches repeats at board time | PASS |
| G-4 | "Use images where needed, like heroes and other components … analyse the existing page structure for images or the image folder under assets" | Tasks 9, 10, 10b, 10c | `scripts/image_candidates.py` ranks the page's own images first, then served images, then `Assets/Images`. `image-every-body-heading`: the hero plus every body H2/H3 (FAQ excepted) has a slot. Board block 7 "Images & styles" shows the slot's current file first and pre-checked, with named OG/IG style radios. The build gate refuses unapproved or uningested images | PASS |
| G-5 | "IMAGE.MD — OG image styles and infographic styles, approval, etc. before the builds … only on the location, compare, blogs, not on the built pages" | Tasks 0, 7, 8, 10d, 11b | `IMAGE-DESIGNS.md` (scope: new pages only; breed lines sourced). OG styles A/B/C/D/E/H and IG-1..IG-5. Two-pass sha12 approval. `reframe_og.py`, `ingest_image.py` and three ported image skills. Block 7b plus `board_approve.py` refuse approval, and re-approval, while any rule fails. Built pages are frozen out by name (`BUILT_BEFORE_SYSTEM_GAPS`) | PASS (smoke image waits for the key, KI 70) |

## Tasks

| Task | What | Commits | Spec · Quality |
|---|---|---|---|
| 0 | family_rules hook | `99c81e0` | controller |
| 1 | Keyword types + keyword_variants.py | `fa9bd8a 4044dda ad8da9b` | ✅ ✅ |
| 2 | Ontology classes + seeder (56 entities) | `7fa4f75 4653ed6` | ✅ ✅ |
| 3 | Board entity + keyword view | `a20296d 26498d8` | ✅ ✅ |
| 4 | External link diversity | `55387d2 b94a4fd b1a6186` | ✅ ✅ |
| 5 | Anchor types + site-wide reuse | `286e57c 9804d63 6a28192` | ✅ ✅ |
| 6 | Outline provenance gate | `34e7724 ce002fa 5b34eef` | ✅ ✅ |
| 6b | Outline heading-repeat check | `8389b59 58fcd7f` | ✅ ✅ |
| 7 | IMAGE-DESIGNS.md + label map | `0296f9f 7e1e999 747422c` | ✅ ✅ |
| 8 | reframe_og, ingest_image, 3 image skills | `33d6fb5 fd233c1 f2e2149` | ✅ ✅ |
| 9 | image_candidates | `27e5e2e 1b0b4b0 e5daff7` | ✅ ✅ |
| 10 | Per-heading image rule + build gate | `21e3496 10f8387 5000a2b` | ✅ ✅ |
| 10b | Board block 7 Images & styles | `07d29b0 0d08da2` | ✅ ✅ |
| 10c | Current file first, style names | `5ebd997 919e37f da9bfd1 ff9c2e5 733caa9 ee5243b 4735dff` | ✅ ✅ |
| 10d | Rules on the board (7b) + approval refusal (added in execution) | `3748ab4 22701b8 a276d27` | ✅ ✅ |
| 11 | Wiring: CLAUDE.md 17, WORKFLOW 13, skills | `93e885b a72595e` | ✅ ✅ |
| 11b | google-genai pinned; smoke image awaits the user's key | `c78ba09` | partial (KI 70) |
| 12a | Whole-branch review fixes (added in execution) | `1a64165 f32e4b7 cd3cc32 376503a fd2746b dc4432e c78593b c391b48 7e44e4d` | ✅ (branch re-review YES) |

The review-driven changes beyond the plan text are listed in the plan's "Execution record". Two tasks were added during execution: 10d (the rules shown on the board and refused at approval) and 12a (fixes from the whole-branch review).

## Rulings (the user, 2026-09-24)

G1: images on every body H2 and body H3, FAQ blocks excepted, the hero included, new pages only. G2: when no image fits, one is generated per `IMAGE-DESIGNS.md` and approved on the board first. G3: ≥6 external links, on 6 domains, from ≥4 source types. G4: the rules bind location/comparison/blog pages built from now on, never the 12 built pages. Image key: the user adds `GEMINI_API_KEY`; the controller installed `google-genai` (1.47.0, prebuilt wheels, pinned).

## Runs

| Check | Run 1 | Run 2 |
|---|---|---|
| `npm run build` | exit 0 | exit 0 |
| `python3 -m pytest tests/py -q` | 2982 passed, 25 skipped, 1 xfailed | 2982 passed, 25 skipped, 1 xfailed |
| `npm run -s check:all` | exit 0 | exit 0 |
| `npm run -s registry` | 0 problems | 0 problems |
| `npm run -s agents` | 0 problems (41 agents) | 0 problems (41 agents) |

Baseline at `9927710`: 2377 passed, 25 skipped, 1 xfailed, so this build adds 605 tests. The skips depend on the environment (no WordPress clone, no picks.json, and so on). Approval drift on the 12 built boards: none. `src/pages`: unchanged. The whole-branch review traced a new location page end to end on a scratch copy: keyword variants → ontology check → image candidates → board (blocks 4/5/7/7b) → approval → draft → second-pass approval → publish, ending with clean findings.

## Open items

- **KI 70:** the real smoke image, once the user sets `GEMINI_API_KEY`. Also consider a newer Python than 3.9.
- **KI 71:** organisation and regulation entities have no owner page yet.
- **KI 72:** only one research row in the link library (RVC VetCompass blocks curl).
- **KI 73:** the committed board HTML for the 12 built pages lags the renderer; republish when next touched.
- **KI 74:** small helper duplicates (`slug_file`, `route_of`), and the unread `--write` output.
- **Merge with `p5-readiness`:** this build merged first. The conflict guide is in `docs/reference/session-log.md` under "System gaps bridge build".
