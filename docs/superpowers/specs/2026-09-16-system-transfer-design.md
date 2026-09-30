# System transfer — design

BlueStaffyUK rebuild, project 2 of 6. Date 2026-09-16. Branch `foundation` in
`~/Downloads/BSUK`, no remote, nothing pushed.

Foundation (project 1) migrated the WordPress site verbatim and closed with every Python
gate at zero and a large but intended render-harness baseline. Project 2 moves the C.A.Gs
site operating system — the rules, the Page Board, the gates, and the agents and skills that
run them — from `~/Downloads/CAG` into BSUK, re-based from an African Grey parrot breeder
to a Glasgow Staffordshire Bull Terrier breeder. It also retires the old `bluestaffyuk`
MCP server and moves the credentials it carried into the repo's environment file.

Source inventory: 66 agents, 72 skills (stored twice), 89 scripts, 10 rule packs, 3 schemas,
24 pytest files and the Playwright render harness, of which the harness already reached
BSUK in project 1.

## 1. Decisions

| Decision | Choice |
| --- | --- |
| Scope | Curated core: rules, board, gates, harness re-base, and only the agents and skills projects 3–5 will invoke. About 25 agents and 40 skills. |
| Port method | Manifest-driven. `data/port-manifest.json` is the record; `scripts/port_from_cag.py` applies it; `scripts/marker_check.py` proves it complete. |
| Skill layout | Single tree at `.claude/skills/<name>/SKILL.md`. The CAG flat mirror `skills/*.md` and `register_skills.py` are not ported; citations are rewritten. |
| Component kit | Not ported. Project 3 brings components with the design system. |
| Deploy, IndexNow, pagefind | Ported but inactive: documented in CLAUDE.md as "Project 6", and the scripts refuse to run unless `BSUK_RELEASE=1`. |
| Rule ledger | `data/quality/rule-index.json` ports with its `test` / `judgment` / `untested` tags. `rework-ledger.json`, `evidence-ledger.json` and `scorecards/` start empty. |
| Credentials | Copied from the desktop MCP entry into a gitignored `BSUK/.env`; keys documented in `.env.example`. The GitHub token is not carried over. |
| Formspree | `PUBLIC_FORMSPREE_ID=xqegrzka` resolved now. The form check reads it from the environment. |
| Old MCP | Config block removed (timestamped backup kept beside the file) and `~/bsuk-mcp-server` deleted, as the last two tasks. |

## 2. Layout in BSUK after the port

```
CLAUDE.md                              rewritten from CAG's skeleton; BSUK facts; deploy rules inactive
rules/                                 10 packs re-based; for-sale.md becomes puppies.md
schemas/                               board.schema.json, component-ledger.schema.json, ontology.schema.json
.claude/agents/bsuk-*.md               curated agents (list in §3)
.claude/skills/<name>/SKILL.md         curated skills (list in §3)
.claude/commands/opsx/*.md             propose, explore, apply, archive (copied)
data/port-manifest.json                every ported file: src, dst, mode, notes
data/quality/rule-index.json           ported tags
data/quality/rework-ledger.json        empty
data/quality/evidence-ledger.json      empty
data/quality/evidence-budgets.json     ported
data/agent-registry.json               regenerated from the agents actually present
data/component-ledger.json             empty until project 3
data/boards/<slug>.json                approved boards (homepage proving board in project 2)
scripts/port_from_cag.py               applies the manifest
scripts/marker_check.py         zero-tolerance gate, wired into check:all
scripts/pageboard.py                   board library (imports dup_content_audit whitelist)
scripts/board_gate.py                  refuses to build an unapproved board
scripts/board_approve.py
scripts/build_page_board.py            board Artifact builder
scripts/final_page_audit.py
scripts/page_hardening_scan.py
scripts/aeo_audit.py
scripts/evidence_audit.py
scripts/form_contract_audit.py
scripts/perf_audit.py
scripts/quality_report.py
scripts/generate_page_dates.py
scripts/indexnow_submit.py             release-guarded
scripts/health-sweep.sh
tests/test_<each gate>.py              one per ported script, plus test_port_manifest.py
tests/render/                          re-based (§4)
docs/reference/{system-registry,quick-start,WORKFLOW,seo-rules,session-log}.md   re-based
docs/reference/credentials.md          which env keys exist and what reads them; no values
docs/superpowers/specs/2026-09-16-system-transfer-design.md   this file
docs/reports/system-transfer-gate-report.md
```

Not ported, by name: agents `cag-timneh-specialist`, `cag-species-guide-builder`,
`cag-variant-specialist`, `cag-bird-personality`, `cag-clutch-manager`,
`cag-competitor-registry`, `cag-competitor-pricing-alert-agent`; skills `cag-bird-page-build`,
`cag-bird-listing-page`, `cag-bird-page-excellence`; all content data under `CAG/data/`
(bird and clutch inventory, competitors, prices, reviews, case studies, US locations, GSC
exports, keywords); `CAG/src/components/`; `CAG/docs/archive`, `docs/competitor-reports`,
`docs/artifacts`, `sessions/`; the one-off `add_*_rule.py`, `patch_*`, `migrate_*`,
`slim_golden_rule.py`, `apply_model_tiers.py`, `scaffold_amie_from_roys.py`,
`process_amie_images.py`, `scripts/oneoff/`; board canvas and thumbnail scripts
(`board_canvas.py`, `board_thumbs.mjs`, `design_canvas_probe.mjs`, `probe_artboards.mjs`,
`merge_canvas_r4.py`, `r3_*`); `CAG/.google-key`.

## 3. Curated agents and skills

Agents (renamed `cag-` → `bsuk-`, content re-based):

- Page builders: homepage-builder, hub-builder, location-builder, comparison-builder,
  purchase-guide, section-builder, structure-architect, content-architect, batch-rebuilder,
  framework-agent, interactive-component, infographic-builder, about-builder.
- Content: seo-content-writer, blog-post-agent, angle-agent, non-commodity-content-agent,
  content-audit-agent, image-pipeline, faq-agent, paa-agent, meta-description-agent.
- Ops and QA: agent-system-qa, self-update, deploy-verifier (release-guarded),
  accessibility-fixer, performance-fixer, site-hygiene-agent, canonical-fixer,
  redirect-manager, contact-form-updater, trust-signals-agent, footer-standardizer.
- Analytics, ported now but data-less until project 6: gsc-analytics, keyword-verifier,
  rank-tracker.

Skills (single tree):

- System: cag-gate-integrity, cag-learning-loop, cag-final-page-pass, cag-page-hardening,
  cag-perf-gate, cag-duplicate-content-gate, cag-evidence-pass, cag-aeo-pass,
  cag-seo-master-checklist, cags-comprehensive-page-audit-system, cag-website-health,
  cag-broken-links, cag-indexing, cag-contact-form, cag-footer-agent, cag-site-patterns,
  cag-cta-strategy, cag-entity-agent, cag-entity-graph, cag-youtube, cag-google-map.
  Renamed `bsuk-*`.
- Page builders: cag-blog-post, cag-location-page-builder, cag-comparison-page-builder,
  cag-for-sale-page-builder (becomes bsuk-puppy-page-builder).
- Generic, copied unchanged: the 14 `framework-*` skills, anti-ai-writing, keyword-cluster,
  internal-link-agent, sitemap-agent, section-auditor, manual-auditor-check,
  research-recency, image-metadata, image-prompt-generator, caption-writer, grill-me,
  session-closer, openspec-propose, openspec-explore, openspec-apply-change,
  openspec-archive-change.

Design-system skills (cag-component-refresh, cag-component-variations,
cag-multi-agent-design, cag-design-rebuild, cag-direction-d-theme, cag-visual-intelligence,
cag-image-generation, cag-photo-ingest, cag-infographic, cag-logo-generator) and the
marketing agents wait for the projects that use them. The manifest lists them with mode
`deferred` so the record is complete.

## 4. The manifest, the port script and the gate

`data/port-manifest.json` is an array of rows:

```json
{ "src": ".claude/agents/cag-hub-builder.md",
  "dst": ".claude/agents/bsuk-hub-builder.md",
  "mode": "rebase",
  "notes": "US states → UK regions; bird → puppy; C.A.Gs → BlueStaffyUK" }
```

`mode` is one of `copy` (byte-identical), `rename` (path changes, bytes identical),
`rebase` (content edited by hand after the first copy), `deferred` (recorded, not written).
`src` is relative to `~/Downloads/CAG`, `dst` to `~/Downloads/BSUK`.

`scripts/port_from_cag.py`:

- validates the manifest against `schemas/port-manifest.schema.json` (unique `dst`, known
  modes, `src` exists for every non-deferred row);
- for `copy` and `rename`, writes `dst` and overwrites it on every run;
- for `rebase`, writes `dst` only when it does not exist, and never overwrites — the hand
  edits are the deliverable;
- prints `applied N, skipped-existing N, deferred N, missing N` and exits non-zero on any
  missing source.

`scripts/marker_check.py` scans every `dst` the manifest names plus `CLAUDE.md`,
`rules/`, `docs/reference/`, `package.json` and `tests/render/`, and fails on any of:
`parrot`, `african grey`, `african-grey`, `timneh`, `congo`, `clutch`, `C.A.Gs`, `cags`,
`congoafricangreys`, `agcare`, `xrejpnvn`, `cag-` as a path or identifier prefix. Matching
is case-insensitive. There is no allowlist; a legitimate hit is a design error to fix, not
an exception to record. Output shape matches the Foundation gates:
`examined N files; 0 problems`. Wired into `npm run check:all`.

Tests: `tests/test_port_manifest.py` covers schema rejection, the never-overwrite rule for
`rebase`, `copy` overwrite, the missing-source exit code, and one fixture per marker.

## 5. Harness re-base

BSUK already carries the ten check families, seven libs, both specs, `targets.json` and 69
fixtures from project 1. Project 2 changes:

- `tests/render/checks/form.ts` reads `PUBLIC_FORMSPREE_ID` from the environment and throws
  when it is unset, so a missing id fails the meta gate rather than silently matching
  nothing. The contract's field set becomes BSUK's as built: `name`, `email`, `phone`,
  `location`, `puppy` (select with the Glasgow collection option), `message`, the
  `_gotcha` honeypot, and hidden `_next` and `_subject`. `known_good/form-inquiry-contract.html` and
  `known_broken/form-inquiry-contract.html` are regenerated from the built contact page.
- The DUP whitelist in `scripts/dup_content_audit.py` (`WHITELIST_SNIPPETS`,
  `WHITELIST_STEMS`, `HEADER_WHITELIST`, `HEAD_TERMS`) is re-measured against BSUK's own
  header, footer, breadcrumb and CTA chrome from `dist/`. `dupCorpus.ts` keeps its floor
  assertion at the new count. The `dup-adjacent-to-whitelist` fixture is regenerated from
  the new stems, and the three `dup_corpus/sibling-*.html` fixtures are replaced with three
  BSUK location pages.
- `known_broken/schema-sold-not-instock.html` and `schema-single-product-offer.html` are
  regenerated from a BSUK puppy page.
- `targets.json` page types are renamed (`bird` → `puppy`) and the
  `families_by_page_type` map is checked so that every family still examines at least one
  page. The meta gate rule from project 1 stands: a family wired to no page type fails.

## 6. Board system

Ported: `pageboard.py`, `board_gate.py`, `board_approve.py`, `build_page_board.py`,
`schemas/board.schema.json`, `tests/test_page_board.py`. `jsonschema` is added to
`requirements.txt`. `pageboard.py` keeps importing `HEADER_WHITELIST` and `HEAD_TERMS` from
`dup_content_audit.py` so the pre-build heading check matches the post-build gate.

`board_gate.py <slug>` refuses when `data/boards/<slug>.json` is missing or unapproved, and
reads built headings from `dist/<slug>/index.html`. Project 2 writes one proving board for
the homepage (`data/boards/index.json`), takes it through `board_approve.py`, passes
`board_gate.py index`, and builds `docs/artifacts/boards/index.html` with
`build_page_board.py`, so project 4 starts from a worked example. The board's sections
mirror the migrated homepage headings; no content is rewritten.

## 7. CLAUDE.md and rules

CLAUDE.md is rewritten from CAG's 169-line skeleton, keeping its structure: paths and deploy
model, the pointer table to `rules/`, page type → what to read first, the judgment-only
rules, gates, brand context, and where everything else lives. Changes:

- Rules 2 (CITES framing), 11 (Verified-Claim Ledger) and 12 (brand-owned method labels)
  are dropped. Rule 1 becomes first-person voice for Lisa Bright. Rules 3 and 4 (branch,
  commit+push) become "work on `foundation`, commit, never push until project 6".
- The gate list gains `marker_check.py`, `board_gate.py` and the Foundation gates.
- The deploy section is titled "Deploy — inactive until project 6" and names the
  `BSUK_RELEASE=1` guard.
- Page types: home, hub, location, puppy, blog, about, contact, comparison.
- Brand context points at `data/settings.json`, `data/puppies.json`, `data/price-matrix.json`
  and the Foundation spec's locked facts (breeder Lisa Bright; £1,500 and £1,700 prices;
  £500 refundable deposit; £200–£350 delivery; phone placeholder).

Rule packs: `headings`, `images`, `schema`, `links`, `copy`, `design`, `gates`, `deploy`
re-based in place; `for-sale.md` becomes `puppies.md` (Product schema per pup, `InStock`
only on available pups, no head-cropped portraits, as Foundation established).
`data/quality/rule-index.json` ports with every rule id renamed alongside its file.

## 8. Credentials and MCP removal

Ordered, and last in the plan:

1. Read the `bluestaffyuk` block from
   `~/Library/Application Support/Claude/claude_desktop_config.json`. Write to `BSUK/.env`:
   `GSC_CLIENT_ID`, `GSC_CLIENT_SECRET`, `GSC_REFRESH_TOKEN`, `GSC_SITE_URL`,
   `GA4_PROPERTY_ID`, `GA4_CLIENT_ID`, `GA4_CLIENT_SECRET`, `GA4_REFRESH_TOKEN`,
   `PUBLIC_FORMSPREE_ID`. `.env` is gitignored (verify). `.env.example` lists the keys with
   empty values. `docs/reference/credentials.md` says which script reads which key.
2. Verify: `.env` parses, every key present and non-empty, `git status` shows no `.env`.
3. Copy the desktop config to `claude_desktop_config.json.bak-<timestamp>` beside it, remove
   the `bluestaffyuk` block, and check the result is valid JSON with every other server
   intact.
4. Delete `~/bsuk-mcp-server`.

The GitHub token, owner and repo in that block are not carried over; BSUK has no remote.
No credential value appears in any committed file, report, or Artifact.

## 9. Definition of done

- `npm run check:all` runs parity, redirects, schema, sitemaps, placeholders and the parrot
  marker gate, and passes twice.
- `python3 -m pytest` green, including the ported gate tests and `test_port_manifest.py`.
- `npm run test:render:meta` and `test:render:pages` green with the re-based whitelist and
  contract; every family examines at least one page.
- `port_from_cag.py` reports `missing 0` and a second run reports `applied 0` for `rebase`
  rows.
- The homepage proving board is approved, passes `board_gate.py`, and its Artifact is built.
- `.env` holds all nine keys; the MCP block is gone; the desktop config is valid JSON;
  `~/bsuk-mcp-server` no longer exists.
- `docs/reports/system-transfer-gate-report.md` written and published as an Artifact, with
  this spec and the plan.
- Commit trailer on every commit: `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

## 10. Out of scope

Components and the design system (project 3); rewriting any page content; the marketing,
email, social and competitor agents; canvas and thumbnail scripts; GSC and GA4 data pulls;
the new domain, phone number, pagefind index and IndexNow submissions (project 6).

## 11. Amendments from planning (2026-09-16)

The implementation plan (`docs/superpowers/plans/2026-09-16-system-transfer.md`, closing
section "Deviations from the spec, recorded") found eleven places where CAG's code
contradicts this spec. They stand as written there and override the sections above where
they conflict. The material ones: `pageboard.py` absorbs the two token helpers from the
unported `board_canvas.py`; `scripts/dup_content_audit.py` joins the marker gate's fixed
scan roots; the board file lives at `data/boards/<slug>.json` with nested slugs flattened
`/` → `--`; §3's agent list is the 36 names it prints, not "about 25"; CAG has 12
`framework-*` skills, not 14; `final_page_audit.py` gains a non-zero exit on FAIL;
`perf_audit.py` brings its two `scripts/lighthouse/agentic-*.mjs` helpers; the harness
re-base covers every marker hit under `tests/render/`, about 57 files, not six.

- Two content placeholders introduced during the skill re-base, `LICENCE_CLAIM_PLACEHOLDER` and `LEGAL_CLAIM_PLACEHOLDER`, stand in for the breeder-licence and Lucy's-Law claims until Lisa Bright confirms them; `placeholder_check.py` refuses to release while they remain.
- The marker gate is `scripts/marker_check.py`, not `parrot_marker_check.py`: `package.json` is a scan root and the gate's own wiring line would otherwise be a permanent hit. Renaming beats an exclusion, which §4 forbids.
- Proving board (Task 5): `board_gate.py index` reports five `header-collision` FAILs on the
  migrated homepage. Two are site chrome (`Blue Staffy News: Join 500+ Readers!` on 3 pages,
  `Available Blue Staffy Puppies` on 12) whose whitelist entries are still parrot-worded and
  clear with Task 15's `HEADER_WHITELIST` / `HEAD_TERMS` re-base. Three are genuine
  cross-page heading duplicates in migrated copy (`/uk-locations/staffy-breeding-dogs-glasgow/`
  and `/uk-blue-staffy-puppy-buying-guide/` against the homepage) that this project may not
  edit; they are carried to project 4 as a Foundation content finding. §6 and §9 therefore
  read "the proving board is approved and built; the gate is green after Task 15 except for
  the three carried duplicates, which the gate report lists". The gate is not weakened.
- Fact lint (Task 11): mechanical re-basing re-labelled parrot facts as dog facts (a
  lifespan/cost table, price ranges outside the locked £1,500/£1,700, DEFRA asserted as a
  compliance body, "50 cities", a hosting provider stated as fact, placeholders used as
  nouns in headings and routes). `tests/py/test_agent_facts.py` now lints `.claude/agents`
  and `.claude/skills`: only locked £ amounts; banned tokens (captive, USDA, APHIS, CITES,
  Cloudflare, 40–60, 50 cities/states); DEFRA only beside "transport"; no placeholder inside
  a heading or a path segment; no lifespan other than 12–14 years. Rule 10 is now enforced,
  not asserted.
- Form check unset behaviour (Task 14 quality review): §5 says `form.ts` "throws when
  unset". A module-scope throw aborts every family in the harness at import, so the check
  instead reads `PUBLIC_FORMSPREE_ID` lazily inside `run()` and, when unset, returns a
  single REFUSED defect row with `examined: 0` — the FORM family fails visibly and the other
  nine families still run, matching `scripts/form_contract_audit.py`'s lazy read. Both
  gates derive the field contract from `data/page-map.json` `kind` (rich → full,
  blog → short, location/hub → none), never from a hard-coded slug list. Fixtures carry
  `FORM_ID_FROM_ENV` in the action and the meta spec substitutes the env value at test time,
  so the id never sits in a committed file under `tests/`, `scripts/` or `src/`.
- Render gates in §9 (Task 16): "`test:render:pages` green" was never achievable on
  Foundation's terms — that gate measures migrated WordPress markup and its baseline is the
  starting line for projects 3–4. §9 now reads: `test:render:meta` green; `test:render:pages`
  runs to completion against the recorded Project 2 baseline in
  `docs/reports/render-baseline-project2.md` (5 passed / 46 failed, 265 defect rows across
  17 pages, 67 blocking / 198 advisory) with no new blocking row versus Foundation's gate
  report; every family examines at least one page. The only rows that moved after the
  harness re-base are `dup-no-sibling-crossover` (42 → 33) and `form-inquiry-contract`
  (6 → 3), both intended.
- Deferred checks (Task 16): the plan's two ids `bottom-bar-under-tabbar` and
  `analytics-double-load` never existed in the render harness — they are Python
  page-hardening checks in the source repo — so `deferred_checks` gained nothing. If a
  later project ports them into the harness, defer them then.
- Deploy (Task 17): §1's "deploy, IndexNow, pagefind ported but inactive" resolves as
  IndexNow (`scripts/indexnow_submit.py`, refuses with exit 2 unless `BSUK_RELEASE=1`, and
  again on the `SITE_URL` placeholder) and pagefind (`build:release`, behind
  `scripts/release_guard.sh`) ported and guarded; there is no deploy script to port because
  the source repo deployed by pushing to a host and BSUK has no remote and no host until
  project 6. The deploy model is documented as inactive in CLAUDE.md; project 6 adds the
  actual deploy step for the host it chooses. Refusal exit code is 2 ("cannot run"),
  consistent with `board_gate.py` and `evidence_audit.py`, superseding the plan's 1.

