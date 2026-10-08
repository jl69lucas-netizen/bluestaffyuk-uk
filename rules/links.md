# Anchor placement

Rules moved out of `CLAUDE.md` on 2026-08-02 (Phase 4). **The rule text is verbatim.**

`enforced:` says what actually holds the rule up.
`test` — a committed check fails when the rule is broken. `judgment` — no mechanical
decision procedure exists, and `data/quality/rule-index.json` records why.
`untested` — **a deletion candidate**: it is asserted and nothing enforces it.
`scripts/quality_report.py` §5 lists every one of those on every run, which is the point.


---
id: link-first-anchors
enforced: untested
family: NAV
---

- **Link-First anchors (ALWAYS) — applies to EVERY internal and external link, every agent, skill, and page** — The anchor sits at the **START of the sentence/paragraph** — inside the opening words (first clause). **Never mid-sentence, never at the end.** ✅ "Our [Staffordshire Bull Terrier guide] covers diet in depth…" · ❌ "…diet is covered in our [guide]." (Breeder rule 2026-07-11, superseding the old "beginning or middle, never end" rule everywhere.) Sole exception: branded ACTION anchors on CTAs per `.claude/skills/bsuk-branded-hybrid-keywords/SKILL.md` (deferred to project 6, see data/port-manifest.json). In the source repo this rule was injected into every agent's Golden Rules by an injector script; the injectors are not ported (spec §2). Here the pack is the only source.


---
id: external-links-six-diverse
enforced: test
family: NAV
test: tests/py/test_link_diversity.py
---

- **Six diverse external links (location, comparison and blog pages built after 2026-09-24)** — A new location, comparison or blog page carries at least **6 external links, on 6 distinct domains, from at least 4 source types** (gov, registry, vet-charity, welfare, research, local). A link's source type is the `Source type` column of its row in `docs/reference/external-link-library.md`; every `gov.uk` path is one domain, while `legislation.gov.uk` and a council's own domain are domains of their own; `other` counts toward the six links and six domains, never toward the four types. One URL cited in several sections counts once. `scripts/link_diversity.py` checks the board: WARN on a draft, FAIL from `boarded` on. The twelve pages built before this rule are not asked (`scripts/family_rules.py`). (User ruling, 2026-09-24.) Like every new-page rule, it is shown on the board (block 7b) and `scripts/board_approve.py` refuses the approval while it FAILs.


---
id: anchor-type-variation
enforced: test
family: NAV
test: tests/py/test_anchor_types.py
---

- **Anchor-type variation (location, comparison and blog pages built after 2026-09-24)** — Every internal and external link on a new location, comparison or blog page records its `anchor_type` on the board: `exact`, `partial`, `lsi`, `natural`, `branded` or `naked-url` (Rule 58's three strategies and the Anchor Diversity Ledger's rotation, one vocabulary). The page's in-copy internal anchors use **at least 3 types, at most 2 of them exact-match**; its external anchors use **at least 3 types**; no anchor repeats on the page (pageboard's `links-anchor-duplicate`, case and punctuation folded); and no internal anchor that another board in `data/boards/` already uses for the same target is used again. Nav tiles carry a type but do not count toward the mix. `scripts/link_diversity.py` checks the board (WARN on a draft, FAIL from `boarded` on), and the board's links block shows each link's type and a one-line diversity summary. (User ruling, 2026-09-24.)


---
id: ctas-on-the-board
enforced: test
family: NAV
test: tests/py/test_cta_rules.py
---

- **Every CTA on the board, picked by the breeder, each its own button (every location, comparison and blog page boarded from 2026-10-08 on)** — Working rule 12 covers calls to action as well as links: every CTA the page will carry is a slot on the board (`ctas` in the record: its section, type, target and why) offering **three options**, each a button text in one style from the catalog (`src/styles/cta.css`: solid, arrow, down, chip, sub, tag, caps, wide). The breeder picks one option per slot on the board (block 7e, `approval.picks["cta:<slot>"]`), and `scripts/board_approve.py` refuses an approval that leaves a slot unpicked, picks two texts that say the same thing (data/design/cta-plan.json `near_identical`), or picks one style twice. A button is 2–8 words, never types a figure, and the page's body CTAs sit in its page type's band with a section between any two. The page paints only the picked option (`src/lib/ctas.ts` → `CtaButton.astro`). `scripts/cta_rules.py` checks the board (WARN on a draft, FAIL from `boarded` on); `tests/render/checks/cta.ts` (`cta-text-distinct`, `cta-style-distinct`, `cta-count-in-band`) judges the built page with the same rules. London and Manchester were approved before the rule (`BUILT_BEFORE_CTA_RULE`). The method is the `bsuk-cta` skill. (Breeder ruling, 2026-10-08.)
