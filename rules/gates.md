# Process gates that run before and after a build

Rules moved out of `CLAUDE.md` on 2026-08-02 (Phase 4). **The rule text is verbatim.**

`enforced:` says what actually holds the rule up.
`test` — a committed check fails when the rule is broken. `judgment` — no mechanical
decision procedure exists, and `data/quality/rule-index.json` records why.
`untested` — **a deletion candidate**: it is asserted and nothing enforces it.
`scripts/quality_report.py` §5 lists every one of those on every run, which is the point.


---
id: design-context-read-first
enforced: untested
family: GATE
---

- **Design Context — READ FIRST (applies to EVERY agent, skill, and task)** — Before any design, content, page, or component work, you MUST read BSUK's brand context: the locked facts in `docs/superpowers/specs/2026-09-15-foundation-design.md` (breeder, address, prices, deposit, delivery band) and the operational values in `data/settings.json` — for *who/what/why*; and `rules/design.md` plus `src/styles/global.css` for *how it looks*, until project 3's design system replaces them. They are the single source of truth; if they ever conflict, surface it rather than guessing. Do not produce brand/visual output without having consulted them this session.

---
id: visual-first-workflow
enforced: untested
family: GATE
---

- **Visual-First Workflow is the DEFAULT (ALWAYS) — applies to every design/page/component/layout task, new OR existing** — For any design, page, section, component, or layout work, use the **superpowers brainstorming visual companion** (local browser server showing mockups, hero comparisons, section-layout diagrams, side-by-side options) by default — this is the breeder's confirmed way of working (2026-06-19/20, "like we did on the Roys page"). The full methodology is binding: (1) **visual companion screens** for skeleton / hero / component decisions (push HTML screens, let the breeder click-select); (2) a **per-section distribution matrix** shown for approval BEFORE any code — section taxonomy, ordered topic→micro stack, framework per section, word-count split, and **A/B/C categories** (A=mandatory core, B=competitor-match, C=our-moat-competitors-lack) with a grounded *why* on each B/C row; (3) always mark the **Recommended** pick + why + named trade-off on every option set (per the Recommend+Why rule). Do not jump to writing page code before the visual + matrix approval. Stacks with — does not replace — **Preview before apply**.

---
id: preview-before-apply
enforced: judgment
family: GATE
---

- **Preview before apply** — Any page redesign MUST be previewed and approved before writing to site files.

---
id: same-content-on-redesign
enforced: untested
family: GATE
---

- **Same content** — Redesigns never add or remove page content. Visual layer only.

---
id: confidence-gate-97
enforced: judgment
family: GATE
---

- **Confidence Gate + Clarification Checkpoint (ALWAYS) — applies to every agent, skill, and build** — ≥97% confidence required before writing any site file. When confidence drops below 97% **mid-build, do NOT dead-stop the whole job** (the old behavior silently lost in-context drafts when a session ended before the human replied). Instead run the **Clarification Checkpoint**: (1) **write finished work to disk first** — cleared sections to the page, in-progress notes + the open question to the live session brief's `## Open Flags` (so a stop costs at most the one uncertain piece and the question survives session teardown); (2) **ask the user exactly ONE narrow question** (mark a Recommended answer + why, per the Recommend+Why rule); (3) **keep building every part that isn't blocked** — only the uncertain unit waits for the answer. The live brief is the file `grill-me` created (`sessions/`); if none exists, create one before stopping. In the source repo this rule was injected into every agent's Golden Rules by an injector script; the injectors are not ported (spec §2). Here the pack is the only source. (Data-integrity Confidence-Gate variants — "only report data you actually fetched, never fabricate" — are unchanged; this only upgrades the *file-write* stop behavior.)

---
id: recommend-plus-why
enforced: judgment
family: COPY
---

- **Recommend + Why (ALWAYS) — applies to every agent, skill, and task** — Whenever you present the user options or choices (meta variants, keyword swaps, design directions, components, A/B picks, section placements — anything), you MUST: (1) mark exactly one option **(Recommended)**; (2) explain WHY, grounded in real data (GSC, competitors, the codebase) — never "feelings" or vague preference; (3) stay honest by naming the trade-off/downside of the recommended pick too. In `AskUserQuestion`, put the recommended option first and append "(Recommended)" to its label. Output that lists options without a reasoned recommendation is incomplete.

---
id: restate-the-brief
enforced: judgment
family: COPY
---

- **Restate the brief before you build (ALWAYS)** — For any prompt, short or long, first restate it as a scoped brief — goal · scope · gates · what "done" means · what is explicitly OUT of scope — and improve the prompt where it is ambiguous, so the breeder can correct the reading before work is spent on it. Routine judgment calls are yours to make; reserve blocking questions for cases where proceeding under any assumption would be unsafe or would make the work useless if wrong (Clarification Checkpoint).

---
id: verify-the-gate-first
enforced: untested
family: GATE
---

- **Verify the gate before you fix the page (ALWAYS) — applies to every agent, skill, and gate** — A gate's output is a *hypothesis about the page*, not a fact about it. **Twelve checkers cried wolf on the source site** — ten reported defects that did not exist, two reported PASS having examined **zero pages**, and one reported 586 defects where there were 2. Before editing any page in response to a scanner/audit/probe: open the flagged rule, **quote the wrong line**, and confirm the defect on the built page. Before believing a PASS: **read the gate's own examined count** — `PASS … in 0 pages` is not a pass (zsh does not word-split `$VAR`; pass slugs literally or use `${=SL}`). After widening any whitelist or exemption, re-inject the real defect, confirm FAIL, remove it, confirm PASS, confirm the diff is empty — and know the gate's tolerance first, or the proof passes for the wrong reason. Measure in **Playwright**, never from a formula: the Browser pane reports `vw:0` so every probe false-passes, and `0.5em` over-reports a `ch` by ~20%. **A suspiciously high finding count means a broken check, not a broken page.** Canonical spec: `.claude/skills/bsuk-gate-integrity/SKILL.md`.

---
id: no-test-no-rule
enforced: test
family: GATE
test: tests/py/test_quality_report.py
---

- **No test, no rule — and an escaped defect is charged to the harness (ALWAYS) — applies to every agent, skill, and lesson** — A lesson becomes a rule **only** by this path: defect observed → failing test committed → fix applied → test passes → rule text written next to the test. **A rule with no backing test is a deletion candidate** — `python3 scripts/quality_report.py` §5 lists them every run and exits non-zero when a rule points at a check that no longer exists. The inverse matters more: **when a defect escapes, charge it to the harness, not to a new paragraph.** If an invariant already covered it and stayed quiet, the tool is broken — add the missed case to `tests/render/fixtures/known_broken/`, watch `npm run test:render:meta` fail, fix the check, and write no new rule. Measured twice: 2026-07-31 produced ten findings, **ten of them in the harness and zero in the pages**; 2026-08-01 collapsed a **418-row baseline to 85 with zero page edits**, because 337 NAV rows were counting granularity plus a check racing its own scroll animation — charging those to the pages would have produced a site-wide `src/styles/global.css` change to cure a defect that did not exist. CAG measured thirty-plus rules against a 24.8% rework rate; rule thirty-one does not move that number. Exempt: the capped nine `enforced: judgment` rules in `data/quality/rule-index.json`, each of which states why a test cannot exist. Procedure: `.claude/skills/bsuk-learning-loop/SKILL.md`. Enforced by `scripts/quality_report.py`, itself tested in `tests/py/test_quality_report.py` — the rule obeys its own constraint, or it would not be allowed in.

---
id: run-every-gate-twice
enforced: test
family: GATE
test: tests/py/test_gate_page.py
---

- **Run every gate twice (ALWAYS) — applies to every project 5 page and every project close** — One clean run proves nothing: the same input has produced different verdicts. `npm run gate:page -- <slug>` runs every page gate — the duplicate audit on the body and on `--headers`, the final audit on the page's profile, the hardening scan, the AEO and evidence audits, and the page-run record (`data/page-runs/<slug>.json`: the session open — `grill-me`, `superpowers:writing-plans`, the builder skill, in that order — and the `impeccable:impeccable`, `frontend-design:frontend-design` and `superpowers:verification-before-completion` passes) — twice, and diffs the runs. A step that fails in either run, or answers differently the second time, fails the page; the report is `docs/reports/gate-page/<slug>.json`. The gate first refuses a built page whose file is older than any of its sources on disk — file times, not commit times; for a city `data/locations.json` counts ("rebuild first"); an audit past 600 s fails with exit 124. The record is fresh when its verification commit is in HEAD's history and the page's sources (board, facts, verbatim, route files, a city's own `data/locations.json` row) are unchanged between it and HEAD; the impeccable commit precedes the frontend-design commit, and the page is unchanged between the frontend-design commit and verification, so a fix between the two Harden passes stales nothing and an edit after frontend-design stales that pass. Verification runs `npm run -s build` before the gate run, and the record is committed. **The exit codes a record holds are informational: the full gate (without `--skip-record`) re-runs `npm run -s check:all` once itself and fails on a non-zero exit — it re-verifies rather than trusting the record.** A PASS is still read for its examined count (`verify-the-gate-first`), and a project's gate report carries its own second run. Order and context: `docs/reference/page-run.md`.

---
id: research-board-before-outline
enforced: test
family: GATE
test: tests/py/test_research_board_rule.py
---

- **A research board the user picks from comes before every page's outline (ALWAYS) — applies to every project 5 page: every city, comparison page and blog post** — Asked when they choose the page, the angles, the frameworks, the keyword universe and its distribution and the strategy, the user picked "a research board first" and ruled: "Its a must on all pages, starting from research, fan-out query, all sprints, etc" (2026-09-27). After the research (`docs/reference/page-run.md` rows 4–7) and before the outline (row 9), the page's research board is STOP 1 (row 8): the competitor scan, the query fan-out, the keyword universe by intent with the four extra keyword types, the entities, 3 angle options, 2–3 strategy directions and the framework options per section group, one option per choice marked (Recommended) with its why and trade-off. A page's row in the approved cluster strategy is one of the strategy directions on it, never an exemption. The picks are saved under `docs/reference/answer-board/answers/`, and the outline and the page board are written from them and cite them. `tests/py/test_research_board_rule.py` fails when row 8 exempts a page, when a routing skill or agent skips the board, or when this row or its index entry is missing.

---
id: outline-before-components
enforced: test
family: GATE
test: tests/py/test_outline_first_rule.py
---

- **The user sees the outline before any component is chosen (ALWAYS) — applies to every project 5 page: every city, comparison page and blog post** — The user's ruling (2026-09-29): before any component is selected or built for a page, the user sees the research, the research board (the angles, the strategy, the frameworks, the keyword universe and its distribution) and the full section-by-section outline, every H2 and H3 with its keywords, word count and purpose. In `docs/reference/page-run.md` that is rows 8, 9 and 10 in that order: the research board is STOP 1 (row 8), the outline of row 9 is shown to the user before row 10 starts, and row 10 selects components only for the sections the outline needs. For a city, the component design pass comes after the outline, never before it. Where a kit is already built (London's fifteen `City*` components), the kit is a menu: the outline decides the sections, the page board maps each section to a component by its `shape` and id, and no section is added to use a component. Showing the outline is a hold, not a fourth approval stop: STOP 2 approves it with the board. `tests/py/test_outline_first_rule.py` fails when rows 8–10 lose that order, when this block or its index entry is missing, or when CLAUDE.md's project-5 paragraph stops naming it.
