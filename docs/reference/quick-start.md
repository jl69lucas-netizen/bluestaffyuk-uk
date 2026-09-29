# BlueStaffyUK Quick Start — task to entry point

The full routing table. `CLAUDE.md` keeps an abridged version of the same map (its "Page
type → what to read first" table); this file is the long form. Where they disagree,
`CLAUDE.md` wins and this file is the one to fix.

Re-based in project 2, Task 13. Every row that pointed at a page cluster the source repo
had and this repo does not — the bird listing flow, the Reddit-modifier pages, the
egg-page hybrid, the 22-page transactional cluster — was cut rather than translated, along
with the source's `MANUAL …` and brand-context files at its repo root, which were not
ported (not ported — source repo only). The design system (project 3) lives in
`src/components/kit/`, listed in `data/design/components.json`.

## Quick Start Commands

### "I want to build a new page"
→ `.claude/skills/grill-me/SKILL.md` (loads the gap matrix before asking anything)
→ `@bsuk-content-audit-agent` → **Section Map + outline gate** (approved before a word is
written, `rules/headings.md`)
→ `@bsuk-angle-agent` → `.claude/skills/bsuk-seo-master-checklist/SKILL.md` → build

### "Audit a page"
→ `.claude/skills/bsuk-comprehensive-page-audit-system/SKILL.md` (give it a route) → route
the fixes to the builder that owns the page type.

### "Build / rebuild the homepage"
→ `@bsuk-homepage-builder` → `rules/headings.md` + `rules/design.md` →
`.claude/skills/bsuk-final-page-pass/SKILL.md`

### "Build / rebuild a comparison page"
→ `.claude/skills/bsuk-comparison-page-builder/SKILL.md` →
`.claude/skills/bsuk-duplicate-content-gate/SKILL.md` BEFORE outline approval AND at the
final pass (pairwise against every sibling) → `.claude/skills/bsuk-final-page-pass/SKILL.md`

### "Build / rebuild a puppy or buy page"
→ `.claude/skills/bsuk-puppy-page-builder/SKILL.md` (the puppy and buy cluster; prices,
deposit and delivery come from `data/puppies.json` and `data/price-matrix.json`, never
from memory) → `rules/puppies.md` →
`.claude/skills/bsuk-duplicate-content-gate/SKILL.md` → `.claude/skills/bsuk-final-page-pass/SKILL.md`

### "I want to build all location pages"
→ `@bsuk-batch-rebuilder` → reads `data/locations.json` → forks `@bsuk-location-builder`
per UK city (28 of them; the list in that file is the only list)

### "What should I build next?"
→ `@bsuk-competitive-keyword-gap-agent` (reads the competitor-intel reports and the BSUK
profile; `docs/research/keyword-gap-*.md`) → `@bsuk-strategy-synthesizer` →
`@bsuk-content-architect`. The Search Console traffic baseline is still deferred to project 6.

### "Is the site healthy?"
→ `.claude/skills/bsuk-website-health/SKILL.md` → `.claude/skills/bsuk-perf-gate/SKILL.md`
→ `.claude/skills/bsuk-broken-links/SKILL.md`

### "Give a page a final pass / is this page done?"
→ `.claude/skills/bsuk-final-page-pass/SKILL.md` (THE final gate, any page type)
→ `npm run -s build` → `python3 scripts/final_page_audit.py` → one PASS/WARN/FAIL verdict
→ `python3 -m pytest tests/py -q` and `npm run check:all`

### "I want to list an available puppy"
→ `.claude/skills/bsuk-puppy-page-builder/SKILL.md` — one page per puppy in
`data/puppies.json` under `src/pages/available-puppies/<slug>/`. Six puppies are locked:
Roman, Byrd and Ince at £1,500; Vennie, Christa and Cheryl at £1,700. The deposit is £500
and refundable. Never write a health screen or a licence: neither is established. The
guarantee is `guarantee_label` in `data/settings.json` (its length is `guarantee_days`); read it, never type it.

### "Ask the user questions" / "read my answers"
→ the answer board: `docs/reference/answer-board/README.md`. A batch is made with
`python3 scripts/answer_board_batch.py <sheet> --project <name>` and written to the board with
the ArtifactData tool; answers come back through the board's **Send to Claude Code** and are
saved under `docs/reference/answer-board/answers/`. The board page is built with
`python3 scripts/build_answer_board.py`.

### "A puppy was reserved or sold"
→ update `data/puppies.json` → rebuild → retire or redirect the route via
`data/redirects.json` and `python3 scripts/redirect_check.py`. Never leave a sold puppy
showing as available.

### "Deploy a page"
→ **inactive until project 6.** There is no remote and no live domain. Commit on the
project branch and stop; `rules/deploy.md` is the pack, and
`BSUK_RELEASE=1 python3 scripts/placeholder_check.py` is the gate that will refuse to ship
a placeholder when the time comes.

---

## Reference Docs

These eight are the whole set. The source repo's other reference docs were not ported
(not ported — source repo only) and nothing in this repo may cite them.

- `docs/reference/WORKFLOW.md` — **MASTER WORKFLOW: read before starting any page, sprint
  or monitoring cycle**
- `docs/reference/seo-rules.md` — **MASTER SEO RULES (57 rules): read before creating or
  modifying any page**
- `docs/reference/system-registry.md` — every agent, skill, script, gate and data file that
  exists here, generated from the filesystem
- `docs/reference/session-log.md` — build history and the **Known Issues** list
- `docs/reference/credentials.md` — which env key exists and what reads it. Key names
  only; no value appears there or anywhere else in the repo
- `docs/reference/quick-start.md` — this file
- `docs/reference/location-page-template.md` — the city-page structure, FAQ format and tone
  that `.claude/skills/bsuk-location-page-builder/SKILL.md` builds from
- `docs/reference/external-link-library.md` — every outside URL a page may link to; the board
  validator refuses any other

## The other sources of truth

- `CLAUDE.md` — the session file: the locked facts, the rule-pack router, the seventeen
  working rules (1–9 are the nine judgment rules)
- `rules/README.md` and the ten packs in `rules/` — the written rules
- `data/quality/rule-index.json` — the machine-readable ledger: 83 rules, of which 9 are
  `enforced: judgment` and capped there. This is a different count from seo-rules.md's 57
  and always will be: the ledger indexes the `rules/` packs, the render-harness checks and
  CLAUDE.md working rules 10–17; seo-rules.md numbers its own categories A–J.
- `data/port-manifest.json` — the record of every file that crossed from the source repo,
  and of every file that deliberately did not
