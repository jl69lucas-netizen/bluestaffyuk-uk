# Learning Loop — 2026-09-27 (brief-parity build + London component pass)

Analysis only (read-only pass; no build, no gate run, nothing written to the repo). Procedure:
`.claude/skills/bsuk-learning-loop/SKILL.md` Steps 1–3 and 5 (Step 4 is recommended, not done).

## Step 1 — the ranges and the grep

| Build | Repo / branch | Range | Commits (no merges) | Grep hits (skill Step 1 regex + "review") |
|---|---|---|---|---|
| Brief parity | `/Users/apple/Downloads/BSUK`, `foundation` | `b99d7d6^..499b449` | 85 | 51 (all real rework) |
| London components | `/Users/apple/Downloads/BSUK/BSUK-london`, `london-components` | `5b41cd5..HEAD` (`4256934` at time of reading) | 31 | 12 hits, of which `7ab7b21` is a false hit ("review variants" is the component name) and `43c170d` / `82917de` are docs commits recording deferred review findings; `7ce341a` (parents fact reversed) added by hand. Net rework 10 |

Sources read: `docs/reports/brief-parity-gate-report.md`, `docs/reference/session-log.md` KI 81–92,
`docs/research/london-components/{hardening-log,plan2-notes,hero-mobile-fix}.md`, every fix
commit's body and file list, `scripts/check_city_canvas.py`, `tests/render/canvas.{config,spec}.ts`,
`tests/render/checks/{img,a11y,layout}.ts`, `data/quality/rule-index.json`, `scripts/quality_report.py`,
`scripts/measurement_ledger.py`.

Not counted as escapes: impeccable findings fixed before a variant's first commit (the "Fixed"
column of each task's first table in hardening-log.md) — they never reached a commit. KI 81 (UK
hub `nav-jump-target-lands`) pre-dates both builds.

---

## Step 2–3 — every escape, grouped

Legend — **Q** = the load-bearing question: HARNESS BUG (an invariant existed and stayed quiet),
NEW INVARIANT (no check covered it; smallest failing test named), JUDGMENT (no test can exist).
**Action**: (A) harness fix + known_broken / failing test · (B) new test + rule · (C) note only.

### London component pass

#### L1. "Axes that flatter" — declared must-differ axes the render does not bear out  ·  GATE  ·  6 escapes
- `fc23018` hero a "Broadsheet" rendered as the built `split/right`; counter a "Docket" rendered as the built ruled columns; trust c framing relabelled `card` — spec reviewer (Task 5 review).
- `44bbfa8` counter a declared `inset` but drawn as a card (raised surface + shadow) — reviewer, round 2.
- `17ba9a1` puppy-cards b "Contact sheet" was S1's shipped grid on a tray, differing on framing only (**critical**); puppy-cards a two ruled columns read as S2's two-up; puppy c density declared `airy` for a 2px-seam wall — Task 7 review.
- `62df243` video a "Screening room": an 88px Jones token thumbnail made it S3's facade on a band, one axis (**critical**) — Task 8 review.
- **Q: HARNESS BUG (scope).** `scripts/check_city_canvas.py` `validate_meta` enforces "≥2 axes from every must-differ row" but reads the axes the variant *declares* in `meta.json`; nothing measures them. It passed every one of these. `media` and `framing` are measurable from paint (section-level photo position vs heading; box-shadow / own background / full-bleed band / top rule only); `layout` and `density` stay reviewer judgment. The "media is read at section level" convention (hardening-log, Task 7 review) is exactly the rule a probe would codify.
- **Action (A):** a canvas probe that derives `media` + `framing` from the painted frame and fails on a mismatch with `meta.json`. Shortlist #3.

#### L2. Served alt text rewritten  ·  IMG  ·  4 tasks, 1 sweep
- Tasks 5–8 rewrote the alts of `maggie-blue-staffy-dam-with-pups.webp`, `ethical-staffy-puppy-london-delivery.webp`, `jones-*.webp`, `blue-staffy-testimonial-london-happy-owner.webp` (image-text b lede also promised "agreed in writing"). Fixed `62df243` (Task 8 review, reviewer) and `be49bb3` (controller sweep of Tasks 5–7).
- **Q: NEW INVARIANT.** Working rule 11 (`reuse-every-image-and-video`) is `enforced: untested` in `data/quality/rule-index.json` (KI 92 lists it). `check_city_canvas.py` checks only that alt is non-empty; `verbatim_set_check.py` covers a migrated page's own alts, never a served file reused elsewhere.
- Smallest failing test: a canvas fragment using `/images/maggie-blue-staffy-dam-with-pups.webp` with any alt other than the served one must fail `check_city_canvas.py`. **Action (B).** Shortlist #1.

#### L3. Unconfirmed facts in copy  ·  COPY  ·  ~12 instances, 5 commits
- "One litter" (hero b), "handled daily from birth", "in writing" (trust c), "agreed in writing" (image-text b), "most/some London buyers" (contents a/c, FAQ stub), "Plenty of London families find us between litters" (newsletter c), "everything else is the same" (tables c), puppy called "she"/"her" (key-takeaways c, tables b), "3 boys … three girls" (counter b), newborn 8-pup photo under "6 puppies ready now" — `fc23018`, `447cdfd`, `17ba9a1`, `62df243`; reviewer / impeccable.
- Parents "Angie and Lays" written into three fragments and recorded as fact in `5793200`, reversed by the user in `7ce341a` (the parents are Maggie and Jones, `data/faq.json`) — **user-caught**.
- **Q: split.** (i) HARNESS SCOPE for the parent names: a canonical fact exists in `data/faq.json` and nothing compares copy to it → NEW INVARIANT, mechanical (a capitalised name within 4 words of dam/sire/parents must be in the allowed set). (ii) Audience claims ("most/many/some/plenty of … buyers/families/owners") and promise words ("in writing", "handled daily") → NEW INVARIANT, mechanical, but only as a denylist; `scripts/evidence_audit.py` claim vocabulary (KC, health-tested, vet-checked, DNA) does not cover them and is not run on canvas fragments. (iii) Pronoun for "your puppy", photo contradicting a count, "everything else is the same" → JUDGMENT (meaning, not pattern).
- **Action (B)** for (i)+(ii), shortlist #5; **(C)** for (iii).

#### L4. Crop covers a face  ·  IMG  ·  ~12 instances
- hero a (Roman only eyes at 1280; ears cut), hero c (eyes cut at 768/1280; ticket over Vennie's face at 1024 — twice, `fc23018` then `44bbfa8`), puppy c (Vennie's face under the plate, `9cc9757`; Christa to her nose; Roman's ear tips `17ba9a1`), tables c (Roman's ears), video a (plate over Jones's face at 768, `62df243`), video c (Christa's ear tips), reviews b (Vennie's muzzle, `62df243`), FAQ a / key-takeaways a (Maggie cut). Caught by impeccable shot review and reviewers, never by a check.
- **Q: NEW INVARIANT.** `no-head-cropped-portraits` (rules/puppies.md) is `untested` (KI 92). No check knows where a face is. Testable once the face box is data: record a face rectangle per served dog photo (source-pixel coordinates, one-time judgment per file), then compute the painted crop from `object-fit` / `object-position` and the overlap with any absolutely positioned sibling (plate, ticket, caption).
- **Action (B).** Shortlist #2. It is the single most frequent image defect of the pass.

#### L5. Canvas smoke lacked 1024px  ·  LAYOUT  ·  1 escape (hero b 464px at 1024)
- Fixed `fc23018` (project `vp1024` added to `tests/render/canvas.config.ts`); reviewer.
- **Q: HARNESS BUG (config).** The hero probe in `tests/render/canvas.spec.ts` already tests rule 10's 390–450 band `if (viewport >= 1024)`, and the dial probe switches at 1024 — but the config never painted 1024, only 1280, so the boundary width was never measured. Fixed, but nothing pins it: a later edit can drop the project silently. Same shape in the page harness: `tests/render/playwright.config.ts` runs 375/768/1280, and rule 10 at 1024 is covered only because `scripts/measure_canvas_heights.mjs` measures the kit hero at 1024/1100/1280 for pytest.
- **Action (A):** pin the viewport list. Shortlist #8.

#### L6. Upscaled / soft images  ·  IMG  ·  4 escapes
- hero c 1080px square upscaled at 1280 (`44bbfa8`), counter b / trust c newborn litter photo soft at 400×500 (`fc23018`), video a frame wider than the 780px poster (fixed pre-commit), trust c owner photo soft (`44bbfa8`).
- **Q: HARNESS BUG (half a check).** `img-srcset-within-2x` (`tests/render/checks/img.ts`) already computes `naturalWidth / (box.width × dpr)` and only fails the > 2.0 side; the < 1.0 side (upscaled) is never read, and the ratio ignores the `object-fit: cover` scale, which is what upscales a square in a wide box.
- **Action (A)/(B):** new sibling id `img-not-upscaled` reusing that measurement. Shortlist #6.

#### L7. Painted-geometry collisions  ·  LAYOUT  ·  ~8 instances
- trust a line ran past the last stop (fixed once at 1024+, escaped below 1024 → `fc23018`), counter c ticks drawn over figures, counter a running rule collided with "£200–£350", hero b name tags overhung thumbnails, hero a CTA 3px past the content edge at 1024.
- **Q: NEW INVARIANT (partial).** `layout-no-horizontal-overflow` covers the page edge, not a column edge; nothing checks text-on-text or decoration-over-text overlap. A text-rect intersection check (two different elements' text boxes intersecting by > 1px) is mechanical but will be noisy on overlays by design (ticket over photo is fine; ticket text over figure text is not). Baselines, dead space, orphans, "reads like a link" stay JUDGMENT.
- **Action (C) now**, candidate (B) `layout-no-text-overlap` advisory after Plan 2. Not shortlisted: the false-report risk is high and every instance was caught by the shot review the page run already mandates.

#### L8. Current-section marking wrong / invisible  ·  NAV  ·  7 variants, 1 commit
- `447cdfd`: scroll-driven marker inside `prefers-reduced-motion: no-preference`, so reduced-motion readers saw section 1 stuck; "first section is current" defaults; jump a / jump c first builds scrolled the current stop off-screen. Reviewer.
- **Q: NEW INVARIANT** for the kit (the canvas mechanism is not ported — plan2-notes). Smallest failing test: emulate `reducedMotion: 'reduce'`, scroll to section 6, assert exactly one `[aria-current="location"]` and that it names section 6 and is inside the viewport; repeat with `no-preference`.
- **Action (B)** in Plan 2 against `PageDial.astro` / `SectionStrip.astro`, not now. Listed below the shortlist.

#### L9. Accessible name / decorative image  ·  A11Y · GATE  ·  2 escapes
- jump a opener `aria-label` did not contain its visible text (WCAG 2.5.3) — reviewer, `447cdfd`. **NEW INVARIANT**, mechanical (`a11y-label-in-name`): if an interactive element has visible text and an `aria-label`, the label must contain the text. (B), listed below the shortlist.
- jump b decorative 44px thumbnail carried alt text; the fix had to become a CSS background on an `aria-hidden` span **because `check_city_canvas.py` refuses `alt=""`** (line 310). **HARNESS BUG (false positive):** the validator refuses the correct markup for a decorative image, pushing the author to a worse pattern. (A), shortlist #8.

#### L10. Hero heading painted before the photo on phones (8 built pages)  ·  LAYOUT  ·  user-caught
- `be67a9f` (the user's ruling "ALL HEROES images come first on MOBILE").
- **Q: HARNESS BUG, already charged correctly.** `test_built_hero_puts_the_image_before_the_heading` proved source order only; paint order was never measured. The fix added `known_broken/hero-image-first-order-only.html` + `layout-hero-image-first-mobile.html`, a `known_good` twin, and a blocking check. **Done — (A) complete, no further action.**

#### L11. Deferred review findings (Task 9, `43c170d`)
- A section heading repeats an FAQ question (two stubs); form error lines not tied to fields (`aria-describedby`); contact b strip invites a tap and does nothing; contact a collapses early. All logged for Plan 2.
- Heading = FAQ question: **NEW INVARIANT**, mechanical, (B) small (a page's H2/H3 text never equals a `<summary>` question on the same page). The form items ride on `ContactFormKit` + `scripts/form_contract_audit.py` (C). Tap affordance is JUDGMENT (C).

#### L12. Process rulings (not defects)
- `4256934` research board before every outline (user ruling, pinned by `tests/py/test_research_board_rule.py`); `1367385` deposit comes off the price (fact confirmed). (C).

### Brief-parity build (every hit is harness self-repair except where noted)

#### B1. Freshness / dirty-tree lies: "gate run on a dirty tree", "close order failing on a clean run"  ·  GATE  ·  9 commits
- `43e2df0`, `5f9c858` scorecard freshness by wall clock → before/after mtime; `862bf1c` stale-dist by commit times → file times; `1fc65a6` page-run record did not stale on a page change; `fdc2222` ledger passed on nothing; `677946f` a report gated on a dirty tree read as fresh (close order documented); `769465d` untracked files stamped `-dirty`; `dd29aec` the build's own outputs (`data/page-dates.json`, `public/search-index.json`) stamped every gate report `-dirty`, so the documented close order produced STALE on a clean run; `0c7bf89` page dates set aside only when current, kit edits count toward freshness. All caught by reviewers, three rounds on one task.
- **Q: HARNESS BUG, and the "fix worse than the bug" trap by name.** Each round was unit-tested at the level of one function (`dirty_tracked`, `git_head`, M8 staleness), and each next round found the interaction the unit test could not see: the tree the *documented close order* leaves behind. The skill's rule — verify the fix at the level the bug lived at — was not applied; the bug lived at the sequence level.
- **Action (A):** one replay test of page-run.md row 21 in a temporary git repo. Shortlist #4.

#### B2. Gates that pass on nothing  ·  GATE  ·  6 commits
- `fdc2222` ledger never passes on nothing; `f57659f` `board_gate.py --all` with 0 live pages; `57995dd` zero-page base in `rendered_changes.py`; `93af5da` hardening scan on an unknown page scanned nothing; `9384e77` targets coverage skipped silently; `5f9c858` meta guard vs unmeasured checks.
- **Q: HARNESS BUG class** already named in `bsuk-gate-integrity` ("two reported PASS having examined zero pages"). The render harness has the zero-examined guard; the Python `check:*` gates have none in common, so each new gate re-learns it in review.
- **Action (B):** a parametrised contract test over every `check:*` script. Shortlist #7.

#### B3. One page, two keys (bare slug vs full route; approval vs approval_previous)  ·  GATE  ·  7 commits
- `c6b0756` city term hard-coded to the former city (27 of 28 pages unbudgeted, audit D2); `13623cf` global CTA ignored `approval_previous` during a re-board; `06beb90`, `53e3125` header-collision scan missed approved-unbuilt boards and the same route under another spelling; `791ec39` new-page definition; `dd29aec` / `0c7bf89` global CTA city lookup under the bare slug; `749b628`, `3a95384` thread ledger keyed by URL spelling.
- **Q: NEW INVARIANT (cross-cutting).** Each lookup was tested with the key its author thought of. Smallest failing test: for every function that resolves a board/record by page (`globalCta`, `board_approve`, `gate_page`, `pageboard.slug_file`, `family_rules.is_new_page`), parametrise over one city as `staffy-…-london`, `uk-locations/staffy-…-london` and `/uk-locations/staffy-…-london/`, and a board with `approval: null, approval_previous: {...}` — all must return the same answer. **(B)**, M, listed below the shortlist (Plan 2 / first city page will exercise these paths for real; worth doing before London's board).

#### B4. Text-lint precision/recall churn  ·  GATE  ·  11 commits
- method-label lint (`4c921ce`, `90db8fd`, `1b148de`), Rule 18 floor lint (`4506872`, `1cc2bd3`, `7dd7744`), doc-drift re-wrap (`4751ee3`), barrier lint (`b714435`), claim gate (`e5b7eef`, `9241914` "without is not a denial", `664993b`), retired facts (`7c270a5`, `eed8178`; allowlist 48 → 61).
- **Q: HARNESS, correctly handled.** Every round added must-flag / must-pass sentences to the lint's own pytest. That is the loop working, not a missing rule. **(C)** — note only: the allowlist growth (KI 82) is a real-defect count, not a lint fault.

#### B5. Competitor-metrics heuristics  ·  GATE  ·  5 commits
- `f58abd8`, `96d9a3c`, `317622c`, `8e773e5`, `fddd147` — what counts as prose vs a listing card, one page per domain, opening-copy window. **(C)**: heuristic thresholds are judgment; each round is pinned in `tests/py/test_competitor_metrics.py` / `test_keyword_metrics.py`. Watch Manchester flipping between 1 and 0 prose pages across rounds — the target is fragile at n ≤ 2 (KI 84/85 already route it to the fallback band).

#### B6. Instruction drift  ·  GATE (docs)  ·  8 commits
- `4506872`, `1cc2bd3` (Rule 18 floor in five instruction files), `90db8fd`, `09c2bf3`, `21c8547`, `f0c19b3`, `ee0bf14`, `0c7bf89` (`npx astro build` → `npm run -s build` sweep, which skips prebuild/postbuild).
- **Q: HARNESS SCOPE.** `tests/py/test_doc_drift.py` and `check:workflow` exist; the `npx astro build` form had no lint, so a future skill can reintroduce it (one occurrence remains, as a quote, in `docs/reference/session-log.md:374`). **(A)** S: add `npx astro build` to a banned-command list in `test_doc_drift.py` over `.claude/`, `rules/`, `docs/reference/page-run.md`, `CLAUDE.md` (session-log excluded). Below the shortlist; trivial.

#### B7. Perf gate judged the cold run  ·  GATE  ·  `a265b7b`, `c11204f`
- **(C)**: fixed with tests (warm median of runs 2–5; CLS verdict only on ≥5 runs).

#### B8. Tall image box `sizes` wrong  ·  IMG  ·  `cc26cf5` (page code)
- `TALL_SIZES` for the 4:5 box painted from a 1408×768 file. **Q: HARNESS — examined zero.** `img-sizes-matches-box` exists, but no rendered page used `box="tall"` yet, so it never measured the case. **(A)** S: `tests/render/fixtures/known_broken/img-sizes-matches-box-tall.html` (a 4:5 tall box with the old sizes string) — watch the meta gate fail before trusting it. Below the shortlist.

#### B9. Page-code fixes  ·  `13623cf`, `dd29aec`, `0c7bf89` (global CTA), `cc26cf5` (BodyImage)
- The 4 page-rework commits of the window; all covered by B3 and B8.

#### B10. Marker in an answer-board batch id  ·  GATE  ·  `7ee22d5`
- `check:markers` caught it — after the commit and after posting. **(C)**, optionally a one-line guard in `scripts/answer_board_batch.py` that runs `marker_check` on the id before posting.

#### B11. Hub body misses 9 city links  ·  NAV  ·  `c9ce585` (reviewer; KI 86)
- **NEW INVARIANT**, mechanical: the location hub's `<main>` links every indexable location page. (B) S, as an `xfail(strict=True)` today that the hub refresh flips. Below the shortlist.

#### B12. Intake block 0 not escaped  ·  SEM  ·  `05b79a4`
- **(C)**: fixed through the board's `md()`, pinned in `tests/py/test_page_intake.py`.

---

## Prioritised shortlist — (A)/(B) worth doing now (max 8)

| # | Item | Class | Exact test / fixture to add | File it guards | Effort |
|---|---|---|---|---|---|
| 1 | Served alt kept word for word (L2; retires most of `reuse-every-image-and-video`, KI 92) | (B) | `tests/py/test_served_alt_preserved.py`: build `served_alts = {filename: {alt, …}}` from `data/verbatim/*.json` image alts + `data/locations.json` (fall back to `dist/` only in a skip-if-absent test); fail (1) any canvas fragment `<img src="/images/<f>">` whose alt is not in `served_alts[f]`, and (2) any rebuilt page in `data/facts/rebuilt.json` doing the same in `dist/`. `/puppies/` exempt (puppy photos already carry per-page alts, plan2-notes). Plus a failing case in `tests/py/test_check_city_canvas.py` (`maggie-…webp` with a rewritten alt) and the same rule inside `check_city_canvas.py`'s asset block. Flip the rule-index row to `enforced: test` | `scripts/check_city_canvas.py`; rebuilt pages in `dist/` | S–M |
| 2 | Face stays in the crop and clear of overlays (L4; retires `no-head-cropped-portraits`) | (B) | `data/image-focus.json` `{file: {face: [x, y, w, h]}}` in source pixels for the ~20 served dog photos and the six puppy photos (one-time judgment, recorded on the board). New check `img-face-visible` in `tests/render/checks/img.ts` (advisory): painted crop from `object-fit`/`object-position`, fail when < 90% of the face box is painted or any absolutely positioned sibling covers > 10% of it. `known_broken/img-face-visible.html` = the Vennie-under-the-plate case from `9cc9757`^ (plate over the lower third of the face); `known_good` = the fixed crop. Add to `REUSED` in `tests/render/canvas.spec.ts` | `tests/render/canvas.spec.ts` frames; later every page with `BodyImage`/`PuppyCard` | L |
| 3 | Declared axes must match the paint (L1) | (A) | New probe in `tests/render/canvas.spec.ts` (all components): derive `media` (a section-level `<img>` not inside a repeated data-hook item: none / top / bottom / left / right / inline by its box vs the heading's box) and `framing` (box-shadow → `card`; own opaque background, no shadow, width < viewport → `inset`; width ≥ viewport → `band`; ≥3px top border only → `rule`; else `plain`), fail on a mismatch with the variant's `meta.json`. Failing case first: re-emit counter-strip a from `44bbfa8`^ (declared `inset`, painted with a card shadow) and puppy-cards b from `17ba9a1`^; both must fail | `scripts/check_city_canvas.py` `validate_meta` (which trusts the declaration) via the smoke | M |
| 4 | Close-order replay (B1: dirty tree, clean-run STALE) | (A) | `tests/py/test_close_order_replay.py`: `git init` a temp tree with one fake page, a stub `build` that rewrites `data/page-dates.json` (unchanged content) and `public/search-index.json`, then run page-run.md row 21 in order — build → stub render → `gate_page.git_head` / report write → `rendered_changes.head_sha` → `measurement_ledger` M8/M10 → commit — and assert: no `-dirty` stamp, M8/M10 not STALE. Second case: edit a tracked source after gating → STALE. Third: gate before commit → STALE. It must fail at `769465d` (before `dd29aec`), where the build outputs dirty the tree | `scripts/gate_page.py`, `scripts/page_run_record.py`, `scripts/measurement_ledger.py`, `scripts/rendered_changes.py` | M |
| 5 | Canonical facts in canvas copy (L3 i–ii) | (B) | In `scripts/check_city_canvas.py` `copy`: (a) a capitalised name within 4 words of `dam|sire|parents` must be in the parent set read from `data/faq.json`; (b) a denylist `\b(most|many|some|plenty of)\s+(\w+\s+)?(buyers|families|owners|people)\b`, `\bin writing\b`, `\bhandled daily\b`, `\bone litter\b`. Failing cases in `tests/py/test_check_city_canvas.py`: "the parents, Angie and Lays", "Plenty of London families find us between litters", "agreed in writing" | `scripts/check_city_canvas.py` (and the same denylist later in `scripts/evidence_audit.py` for pages) | S |
| 6 | No upscaled image (L6) | (B) | New check `img-not-upscaled` in `tests/render/checks/img.ts` (advisory), sharing `img-srcset-within-2x`'s measurement: scale = `max(box.w/nat.w, box.h/nat.h)` under `object-fit: cover` (width ratio otherwise) × dpr; fail > 1.05. `known_broken/img-not-upscaled.html` (a 780px image in a 1000px frame — video a's case); `known_good` (780 in 760). Add to `REUSED` in `canvas.spec.ts` | `tests/render/checks/img.ts`, canvas frames, pages | S |
| 7 | Every `check:*` refuses zero input (B2) | (B) | `tests/py/test_gates_refuse_nothing.py`, parametrised over the `check:*` scripts in `package.json` that take a page set: point each at an empty temp `dist/` / empty input via its existing root/`--root` seam and assert exit ≠ 0 or the literal "examined 0 — not a pass". Where a gate has no seam, the test lists it as a named xfail so the gap is visible | every script behind `npm run check:all` | M |
| 8 | Canvas harness hygiene (L5 + L9 false positive) | (A) | (a) `tests/py/test_canvas_viewports.py`: parse `tests/render/canvas.config.ts` projects; assert widths ⊇ {375, 768, 1024, 1280} (1024 = rule 10's and the dial's boundary). (b) In `tests/py/test_check_city_canvas.py`, a must-pass case: `<img alt="" aria-hidden="true" …>` (decorative) is accepted; a must-fail case: `alt=""` without `aria-hidden`/`role="presentation"`. Change line 310 of `check_city_canvas.py` accordingly | `tests/render/canvas.config.ts`, `scripts/check_city_canvas.py` | S |

Next in line (not shortlisted): B3 one-page-two-keys parametrised test (M, before the London board);
L8 current-section marker under both motion preferences (B, Plan 2); L9 `a11y-label-in-name` (B, S);
L11 heading ≠ FAQ question (B, S); B6 `npx astro build` ban (A, S); B8 tall-box fixture (A, S);
B11 hub links every indexable city (B, S, strict xfail).

**Step 3 finding worth stating plainly:** of the London escapes, the two largest groups (axes, alt
text) were both cases where the canvas gate *checked something* in that family and passed — `meta.json`
axes by declaration, alt by non-emptiness. Two of the brief-parity groups (B1, B2) are the skill's
two named traps: a fix verified below the level the bug lived at, and gates passing on nothing.
No escape in either build calls for a new paragraph-only rule.

---

## Step 5 — rework-ledger window entries (draft; NOT written)

Shape read from `scripts/quality_report.py` `trend()` / section 1 (`from`, `to`, `total`, `rework`,
`rate`, `page_rework`, `page_rate`, `harness_rework`, `harness_rate`) and
`scripts/measurement_ledger.py` `m9()` (`window`, `page_rate`, `harness_rate`). Counting rule used:
a rework commit is a grep hit (skill Step 1 regex plus "review"), false hits removed; **page** =
touches `src/` or `public/`; **harness** = touches `scripts/` or `tests/` and not page; the rest
(docs, skills, canvas fragments) counts in `rework` only. `canvas_rework` and `note` are extra keys
the readers ignore.

```json
{
  "windows": [
    {
      "window": "brief-parity",
      "from": "2026-09-26",
      "to": "2026-09-27",
      "range": "b99d7d6^..499b449",
      "total": 85,
      "rework": 51,
      "rate": 0.6,
      "page_rework": 4,
      "page_rate": 0.047,
      "harness_rework": 45,
      "harness_rate": 0.529,
      "note": "Harness-building project: 45 of 51 rework commits are review rounds on gates written in the same build. Page rework = 13623cf, cc26cf5, dd29aec, 0c7bf89. Other = 7ee22d5, 90db8fd."
    },
    {
      "window": "london-components",
      "from": "2026-09-27",
      "to": "2026-09-27",
      "range": "5b41cd5..4256934",
      "total": 31,
      "rework": 10,
      "rate": 0.323,
      "page_rework": 1,
      "page_rate": 0.032,
      "harness_rework": 1,
      "harness_rate": 0.032,
      "canvas_rework": 7,
      "note": "Design pass: the deliverable is design/city-canvas/, outside src/ and public/, so page_rate understates it; canvas_rework (44bbfa8, 5f5a038, 447cdfd, 17ba9a1, 9cc9757, 62df243, be49bb3) is the honest figure, 7/31 = 22.6%. Page = be67a9f; harness = fc23018; 7ce341a (parents fact reversed) counted in rework. 7ab7b21 is a false grep hit."
    }
  ]
}
```

**Before the controller appends this**, two tests pin the ledger as empty and will fail:
`tests/py/test_rules_index.py::test_rework_ledger_is_empty_and_readable_by_quality_report`
(asserts `windows == []`) and `::test_the_gates_actually_load_all_three`
(asserts `trend(...) == (None, None)`). Update both in the same commit. `trend()` sorts by `from`;
with these two windows it reports london-components against brief-parity: page 3.2% vs 4.7%
(-1.5 points).
