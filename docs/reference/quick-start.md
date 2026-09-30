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

### "Build a coat-colour comparison" (blue against black, blue against blue and white)
→ `@bsuk-coat-variant-builder` → it runs `.claude/skills/bsuk-comparison-page-builder/SKILL.md`
for a same-breed coat pairing, adding the shared coat table and the cross-link block; coats
from `data/puppies.json`, prices from `data/price-matrix.json`

### "Answer scam fears" / "add a red-flag checklist"
→ `@bsuk-scam-trust-agent` — deposit scams, borrowed-photo adverts and puppy farming, answered
only with proof a buyer can check; no licence detail on the site

### "Plan or audit a page's external links"
→ `@bsuk-external-link-agent` → `docs/reference/external-link-library.md` (six links, six
domains, four source types on a project 5 page; Link-First; live-checked before the board)

### "Work entities into a section" / "make this section entity-rich"
→ `@bsuk-entity-incorporation-agent` (the 4-Move Loop) → vocabulary from
`.claude/skills/bsuk-entity-agent/SKILL.md`, entities from `data/bsuk-ontology.json`, claims
bounded by `data/quality/evidence-ledger.json`

### "A page carries a video" / "VideoObject" / "video sitemap"
→ `@bsuk-video-seo-agent` (the site side only: board title and caption, `VideoObject` through
`src/lib/video.ts`, `npm run check:sitemaps`) → `.claude/skills/bsuk-youtube/SKILL.md` for a
broken migrated embed. The YouTube channel is never touched.

### "Why does this page feel flat / the same as that one?"
→ `.claude/skills/bsuk-visual-intelligence/SKILL.md` — the page-communication audit, at the
Harden sprint after the static scan (`docs/reference/page-run.md` row 16), before or with AEO

### "Build / rebuild a puppy or buy page"
→ `.claude/skills/bsuk-puppy-page-builder/SKILL.md` (the puppy and buy cluster; prices,
deposit and delivery come from `data/puppies.json` and `data/price-matrix.json`, never
from memory) → `rules/puppies.md` →
`.claude/skills/bsuk-duplicate-content-gate/SKILL.md` → `.claude/skills/bsuk-final-page-pass/SKILL.md`

### "Build a project 5 page" (a city, a comparison or a blog post)
→ `docs/reference/page-run.md`, top to bottom, with four approval stops: STOP 1 the research
board (`python3 scripts/research_board.py <slug>`, from `data/research-boards/<slug>.json`:
why each top-5 competitor ranks and its weakness, intent, reverse engineering, gaps, angles,
strategy, frameworks, the keyword universe and its distribution) → STOP 2 the outline as the
section matrix (`python3 scripts/outline_matrix.py <slug>`, from `data/outlines/<slug>.json`,
approved on its own; `python3 scripts/build_page_board.py <slug>` refuses until then) → STOP 3
the page board → STOP 4 the Asset Gate

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

### "Polish or de-cannibalise the puppy pages"
→ `.claude/skills/bsuk-puppy-page-excellence/SKILL.md` — differentiates the
`/available-puppies/` pages on the axes `data/puppies.json` actually records (colour and
marking within a sex, sex across a shared colour), plus the banked image, contrast,
Product/Offer and geo-block fixes. Ends in `bsuk-final-page-pass`.

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
- `data/quality/rule-index.json` — the machine-readable ledger: 85 rules, of which 9 are
  `enforced: judgment` and capped there. This is a different count from seo-rules.md's 57
  and always will be: the ledger indexes the `rules/` packs, the render-harness checks and
  CLAUDE.md working rules 10–17; seo-rules.md numbers its own categories A–J.
- `data/port-manifest.json` — the record of every file that crossed from the source repo,
  and of every file that deliberately did not
