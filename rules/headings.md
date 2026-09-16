# Heading hierarchy, case and style

Rules moved out of `CLAUDE.md` on 2026-08-02 (Phase 4). **The rule text is verbatim.**

`enforced:` says what actually holds the rule up.
`test` — a committed check fails when the rule is broken. `judgment` — no mechanical
decision procedure exists, and `data/quality/rule-index.json` records why.
`untested` — **a deletion candidate**: it is asserted and nothing enforces it.
`scripts/quality_report.py` §5 lists every one of those on every run, which is the point.


---
id: heading-hierarchy-outline-gate
enforced: test
family: SEM
test: tests/render/checks/sem.ts::sem-heading-order + sem-all-six-levels
---

- **Heading Hierarchy Outline Gate (ALWAYS) — applies to EVERY page, agent, and skill, BEFORE any create/edit/update** — The breeder repeatedly caught skipped heading levels and pages shipping only 1 H6 / 4 H5. Going forward this is a hard, non-negotiable gate (set 2026-06-20): **(1)** Before writing or changing ANY page, you MUST FIRST present the page's **complete H1→H6 outline** — every heading, in render order, labeled by level — and get explicit approval. No page code is touched until the outline is approved. **(2)** Headings descend sequentially with **NO skipped levels** (H1→H2→H3→H4→H5→H6; stepping back up to a higher level to start a new section is fine; jumping H3→H6 or H2→H4 is BANNED — this is the axe "Heading elements are not in a sequentially-descending order" error). **(3)** Every page carries **all six levels** with a **minimum of 5 H5 AND 5 H6** (no fewer than 5 of each). **Exception (2026-09-09, evidence pass): on the homepage and the location pages the 5-per-level minimums are advisory (WARN), never a reason to add a heading; "no skipped levels" and "all six levels" stay hard.** **(4)** Semantic level map: **H1**=page topic · **H2**=main search intents · **H3**=subtopics / keyword clusters · **H4**=micro-intent answers / PAA coverage · **H5**=supporting facts / warnings / examples · **H6**=ultra-specific details / breeder notes / citations. Enforced mechanically by `scripts/final_page_audit.py` (`all_six_levels` / `min_h5_5` / `min_h6_5` = hard FAIL; `min_h5_5` / `min_h6_5` are WARN on `home` and `location` profiles, 2026-09-09) and `docs/reference/seo-rules.md` Rule 52 + Rule 28 (arrives in Task 13). A page that violates any of these will NOT be given a pass. In the source repo this rule was injected into every agent's Golden Rules by an injector script; the injectors are not ported (spec §2). Here the pack is the only source.

---
id: title-case-headings
enforced: test
family: SEM
test: tests/render/checks/sem.ts::sem-title-case-headings
---

- **Title Case on every heading (ALWAYS) — applies to EVERY page, agent, and skill** — Every **H1–H6** uses **AP-style Title Case**, matching the homepage and the blue / black / brindle available-puppies pages. Sentence-case headings are a defect (breeder rule 2026-07-23). Capitalise 4+ letter words and ALL nouns/verbs/adjectives/adverbs regardless of length (`Is`, `Are`, `Do`, `Be`, `Not`, `Our`); lowercase mid-title only `a an the and but or nor for so yet at by in of on to as vs per via`; always capitalise the first word, the last word, and the word after `:` `?` `!` — **an em dash does NOT force a capital**. Hyphenated compounds capitalise each part (`Home-Raised`, `KC-Registered`); never touch acronyms/brands/domains (`UK`, `KC`, `DEFRA`, `BVA`, `DNA`, `SBT`). **Scope is HEADINGS ONLY** — FAQ accordion questions live in `<summary>`, not a heading tag, and stay conversational sentence case. Enforced by `python3 scripts/page_hardening_scan.py <slug>` → zero `header-not-title-case`; spec in `.claude/skills/bsuk-page-hardening/SKILL.md` §1e-ter (arrives in Task 12). In the source repo this rule was injected into every agent's Golden Rules by an injector script; the injectors are not ported (spec §2). Here the pack is the only source. **Backlog: 1,099 headings across 68 pages are still sentence case** (heaviest: the 6 `/available-puppies/` pages ~86 each, hub 54, homepage 31) — the source repo's figure, carried here as the shape of the problem, not a BSUK count; measure BSUK's own with `python3 scripts/page_hardening_scan.py`.

---
id: header-style-declared
enforced: untested
family: SEM
---

- **Header style is declared and justified (ALWAYS) — applies to EVERY page, agent, and skill** — Every H1–H6 outline presented at the Sprint 1 gate declares its **header style** — **Style 1** Pure Conversational / **Style 2** Conversational Hybrid / **Style 3** Recommended Hybrid — plus its register (FAQ / Quora / Reddit), with a reason grounded in that page's own query set, SERP snapshot, PAA demand or a named competitor gap (**never taste**) and a named trade-off. Defaults: **Style 3** for transactional + comparison, **Style 2** for informational / care / location / blog, **FAQ register** for puppy listings, **Reddit register** for Reddit-modifier pages. Deviating is allowed; deviating *silently* is not. An outline with no style line does not pass the gate. Title Case still applies to every heading whatever the style. Spec: `.claude/skills/framework-heading-hierarchy/SKILL.md` §Header Style Selection. In the source repo this rule was injected into every agent's Golden Rules by an injector script; the injectors are not ported (spec §2). Here the pack is the only source.
