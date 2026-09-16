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

- **Confidence Gate + Clarification Checkpoint (ALWAYS) — applies to every agent, skill, and build** — ≥97% confidence required before writing any site file. When confidence drops below 97% **mid-build, do NOT dead-stop the whole job** (the old behavior silently lost in-context drafts when a session ended before the human replied). Instead run the **Clarification Checkpoint**: (1) **write finished work to disk first** — cleared sections to the page, in-progress notes + the open question to the live session brief's `## Open Flags` (so a stop costs at most the one uncertain piece and the question survives session teardown); (2) **ask the user exactly ONE narrow question** (mark a Recommended answer + why, per the Recommend+Why rule); (3) **keep building every part that isn't blocked** — only the uncertain unit waits for the answer. The live brief is the file `grill-me` created (`sessions/` (arrives in Task 12 with the grill-me skill)); if none exists, create one before stopping. In the source repo this rule was injected into every agent's Golden Rules by an injector script; the injectors are not ported (spec §2). Here the pack is the only source. (Data-integrity Confidence-Gate variants — "only report data you actually fetched, never fabricate" — are unchanged; this only upgrades the *file-write* stop behavior.)

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

- **Verify the gate before you fix the page (ALWAYS) — applies to every agent, skill, and gate** — A gate's output is a *hypothesis about the page*, not a fact about it. **Twelve checkers cried wolf on the source site** — ten reported defects that did not exist, two reported PASS having examined **zero pages**, and one reported 586 defects where there were 2. Before editing any page in response to a scanner/audit/probe: open the flagged rule, **quote the wrong line**, and confirm the defect on the built page. Before believing a PASS: **read the gate's own examined count** — `PASS … in 0 pages` is not a pass (zsh does not word-split `$VAR`; pass slugs literally or use `${=SL}`). After widening any whitelist or exemption, re-inject the real defect, confirm FAIL, remove it, confirm PASS, confirm the diff is empty — and know the gate's tolerance first, or the proof passes for the wrong reason. Measure in **Playwright**, never from a formula: the Browser pane reports `vw:0` so every probe false-passes, and `0.5em` over-reports a `ch` by ~20%. **A suspiciously high finding count means a broken check, not a broken page.** Canonical spec: `.claude/skills/bsuk-gate-integrity/SKILL.md` (arrives in Task 12).

---
id: no-test-no-rule
enforced: test
family: GATE
test: tests/py/test_quality_report.py
---

- **No test, no rule — and an escaped defect is charged to the harness (ALWAYS) — applies to every agent, skill, and lesson** — A lesson becomes a rule **only** by this path: defect observed → failing test committed → fix applied → test passes → rule text written next to the test. **A rule with no backing test is a deletion candidate** — `python3 scripts/quality_report.py` §5 lists them every run and exits non-zero when a rule points at a check that no longer exists. The inverse matters more: **when a defect escapes, charge it to the harness, not to a new paragraph.** If an invariant already covered it and stayed quiet, the tool is broken — add the missed case to `tests/render/fixtures/known_broken/`, watch `npm run test:render:meta` fail, fix the check, and write no new rule. Measured twice: 2026-07-31 produced ten findings, **ten of them in the harness and zero in the pages**; 2026-08-01 collapsed a **418-row baseline to 85 with zero page edits**, because 337 NAV rows were counting granularity plus a check racing its own scroll animation — charging those to the pages would have produced a site-wide `src/styles/global.css` change to cure a defect that did not exist. CAG measured thirty-plus rules against a 24.8% rework rate; rule thirty-one does not move that number. Exempt: the capped nine `enforced: judgment` rules in `data/quality/rule-index.json`, each of which states why a test cannot exist. Procedure: `.claude/skills/bsuk-learning-loop/SKILL.md` (arrives in Task 12). Enforced by `scripts/quality_report.py`, itself tested in `tests/py/test_quality_report.py` — the rule obeys its own constraint, or it would not be allowed in.
