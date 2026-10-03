# BlueStaffyUK System Registry — agents, skills, scripts, data files

Read this when you need to know WHICH agent, skill or script does a thing; `CLAUDE.md`
keeps only the routing table and `docs/reference/quick-start.md` the task→entry-point map.

**Every list below is generated from this repo's own filesystem, not retyped from the
source repo.** The source registry claimed 68 agents and named phases, skills, scripts and
data files that do not exist here; those claims were cut rather than translated. If a
count in this file disagrees with `ls`, `ls` is right and this file is stale. Regenerate
with `python3 scripts/build_system_registry.py`; `python3 scripts/build_system_registry.py --check`
is the gate, wired into `npm run registry` and `scripts/health-sweep.sh`.

Only the block between the generated markers is written by that script. This prose is
hand-written and is preserved across regenerations.

<!-- generated:start -->

## Agents — 46

Every agent carries `model: inherit`; effort is the only per-agent cost lever, and
`data/agent-registry.json` is GENERATED from the agents' own frontmatter by
`scripts/build_agent_registry.py`. To change an agent's effort, edit its frontmatter
and regenerate — never the other way round.

### `tier_max` — 14

| Agent | Does |
|---|---|
| `.claude/agents/bsuk-angle-agent.md` | Generates content angles, hooks and unique points of view for any BlueStaffyUK page — 5–10 options before a word of body copy is written |
| `.claude/agents/bsuk-blog-post-agent.md` | Writes commercial, transactional, review and comparison blog posts for BlueStaffyUK as markdown into src/content/blog/<slug>.md, served at … |
| `.claude/agents/bsuk-competitor-intel.md` | Use after the competitor registry (data/competitors.json) is approved, to analyse one competitor, one tier or all of them — or … |
| `.claude/agents/bsuk-content-architect.md` | Orchestrates content creation for BlueStaffyUK |
| `.claude/agents/bsuk-content-audit-agent.md` | Four-phase deep content audit of any BlueStaffyUK page — intent gaps, subtopics competitors cover and BSUK does not, meta … |
| `.claude/agents/bsuk-entity-incorporation-agent.md` | The active entity-SEO engine for BlueStaffyUK |
| `.claude/agents/bsuk-framework-agent.md` | Deep-dives competitor pages for any BlueStaffyUK keyword (UK Staffy puppy, blue Staffy breeder, city queries) and extracts what they do … |
| `.claude/agents/bsuk-homepage-builder.md` | Rebuilds the BlueStaffyUK homepage (src/pages/index.astro) section-by-section |
| `.claude/agents/bsuk-location-builder.md` | Builds or rebuilds one UK city location page under /uk-locations/<slug>/ |
| `.claude/agents/bsuk-non-commodity-content-agent.md` | Produces original, breeder-authentic Staffy content no generic model could write, via a 3-phase Triad (Archaeologist / Provocateur / … |
| `.claude/agents/bsuk-purchase-guide.md` | Rebuilds /buy-blue-staffy-puppies-uk/ section-by-section |
| `.claude/agents/bsuk-seo-content-writer.md` | Writes SEO body copy for any BlueStaffyUK page or section, in Lisa Bright's first-person brand voice |
| `.claude/agents/bsuk-strategy-synthesizer.md` | Use after the competitor research has run (gap matrix, keyword-gap list, competitor reports, LLM intel) and BlueStaffyUK needs a content … |
| `.claude/agents/bsuk-structure-architect.md` | The BSUK silo architect — maps content clusters into Silo (top-down authority) or Reverse Silo (bottom-up ranking) shapes across … |

### `tier_high` — 15

| Agent | Does |
|---|---|
| `.claude/agents/bsuk-about-builder.md` | Rebuilds /blue-staffy-uk-breeders/ — Lisa Bright's breeder story page for BlueStaffyUK, Carlisle |
| `.claude/agents/bsuk-coat-variant-builder.md` | Builds the coat-colour and variant pages of the BlueStaffyUK comparison cluster — blue against black, blue against blue and white, and any … |
| `.claude/agents/bsuk-comparison-builder.md` | Builds Staffy comparison pages — male vs female, Blue Staffy vs another breed — at the URLs the project-5 strategy gives them |
| `.claude/agents/bsuk-competitive-keyword-gap-agent.md` | Use after bsuk-competitor-intel has written competitor reports and the BSUK profile, to find the topics BlueStaffyUK's competitors have a … |
| `.claude/agents/bsuk-faq-agent.md` | Builds and audits FAQ sections for any BlueStaffyUK page using the QAB framework — 6–12 questions per page from real buyer language … |
| `.claude/agents/bsuk-gsc-analytics.md` | Search Console analysis — INACTIVE UNTIL PROJECT 6 |
| `.claude/agents/bsuk-hub-builder.md` | Builds aggregator hub pages that link to their spokes — the puppy hub (/available-puppies/), the location hub (/uk-locations/) with the … |
| `.claude/agents/bsuk-infographic-builder.md` | Builds 400–450px (in-body) and 760px (guide) infographics for any BlueStaffyUK page section as kit components |
| `.claude/agents/bsuk-interactive-component.md` | Builds interactive HTML components for BlueStaffyUK pages — first-year cost calculators in £, coat/temperament fit quizzes, paperwork … |
| `.claude/agents/bsuk-llm-keyword-intel.md` | Use when a BlueStaffyUK page needs to know what an AI engine answers to its buyer question — who the answer cites (BSUK or which registry … |
| `.claude/agents/bsuk-rank-tracker.md` | Competitor and ranking monitoring — INACTIVE UNTIL PROJECT 6 |
| `.claude/agents/bsuk-scam-trust-agent.md` | Answers UK puppy-scam fears — deposit scams, fake and stolen-photo adverts, puppy farming and third-party dealers — on BlueStaffyUK pages … |
| `.claude/agents/bsuk-section-builder.md` | Builds one section of a BlueStaffyUK page by mounting the kit component for it (src/components/kit/) and returns the Astro markup |
| `.claude/agents/bsuk-trust-signals-agent.md` | Audits BlueStaffyUK pages for missing social proof and trust elements and adds them — the counter strip, the trust strip and testimonial … |
| `.claude/agents/bsuk-video-seo-agent.md` | The site side of video SEO for BlueStaffyUK — for every YouTube id in data/settings.json youtube_embeds (and any a page carries of its … |

### `tier_medium` — 17

| Agent | Does |
|---|---|
| `.claude/agents/bsuk-accessibility-fixer.md` | Audits built BlueStaffyUK pages in dist/ for WCAG 2.1 AA — skip links, ARIA labels, focus states, keyboard navigation, colour contrast … |
| `.claude/agents/bsuk-agent-system-qa.md` | Quality review agent for the BSUK agent system |
| `.claude/agents/bsuk-batch-rebuilder.md` | Coordinates a batch page rebuild by dispatching one Agent-tool call per page to its specialist agent, all in one message, then tracks … |
| `.claude/agents/bsuk-canonical-fixer.md` | Verifies that every built BlueStaffyUK page carries an absolute canonical and og:url, and that every JSON-LD @id reference resolves on its … |
| `.claude/agents/bsuk-competitor-registry.md` | Use to seed BlueStaffyUK's national competitor registry (data/competitors.json) for the first time, or when intel or a page build finds a … |
| `.claude/agents/bsuk-contact-form-updater.md` | Audits and standardises every contact, enquiry and newsletter form across BlueStaffyUK against the kit's … |
| `.claude/agents/bsuk-deploy-verifier.md` | Post-deploy verification and IndexNow submission — INACTIVE UNTIL PROJECT 6 |
| `.claude/agents/bsuk-external-link-agent.md` | Plans, places and audits every outbound link on a BlueStaffyUK page from the external link library … |
| `.claude/agents/bsuk-footer-standardizer.md` | Verifies the BlueStaffyUK footer across the built site — every page carries exactly one footer, rendered by … |
| `.claude/agents/bsuk-image-pipeline.md` | Moves generated or supplied photographs into public/images/ under the BSUK SEO filename convention, updates every <img> reference in … |
| `.claude/agents/bsuk-keyword-verifier.md` | Verifies keyword placement, density and on-page SEO hygiene for any BlueStaffyUK page — title, H1, meta description, first 100 words, H2 … |
| `.claude/agents/bsuk-meta-description-agent.md` | Writes and audits every title tag and meta description on BlueStaffyUK — standard (50–60 char title, 140–160 char description) and … |
| `.claude/agents/bsuk-paa-agent.md` | Extracts real People Also Asked questions from Google for a UK Staffy target keyword using the Playwright MCP tools, formats the answers … |
| `.claude/agents/bsuk-performance-fixer.md` | Applies proven Lighthouse Performance fixes to BlueStaffyUK pages — render-blocking CSS, font-display swap, LCP fetchpriority + preload … |
| `.claude/agents/bsuk-redirect-manager.md` | Manages every 301/302 rule for BlueStaffyUK |
| `.claude/agents/bsuk-self-update.md` | Keeps the BSUK agent and skill system current: reviews what a session learned, proposes edits to the agents, skills and rule packs that … |
| `.claude/agents/bsuk-site-hygiene-agent.md` | Technical SEO hygiene for BlueStaffyUK: (1) page cannibalisation audit across the 28 location pages and the buy cluster, with 301 … |

## Skills — 64

One SKILL.md per directory under `.claude/skills/`. The `bsuk-*` set is the ported
system; the rest are the generic writing, research and framework skills.

- `.claude/skills/anti-ai-writing/SKILL.md`
- `.claude/skills/bsuk-aeo-pass/SKILL.md`
- `.claude/skills/bsuk-blog-post/SKILL.md`
- `.claude/skills/bsuk-broken-links/SKILL.md`
- `.claude/skills/bsuk-comparison-page-builder/SKILL.md`
- `.claude/skills/bsuk-competitor-parity/SKILL.md`
- `.claude/skills/bsuk-component-refresh/SKILL.md`
- `.claude/skills/bsuk-component-variations/SKILL.md`
- `.claude/skills/bsuk-comprehensive-page-audit-system/SKILL.md`
- `.claude/skills/bsuk-contact-form/SKILL.md`
- `.claude/skills/bsuk-cta-strategy/SKILL.md`
- `.claude/skills/bsuk-duplicate-content-gate/SKILL.md`
- `.claude/skills/bsuk-entity-agent/SKILL.md`
- `.claude/skills/bsuk-entity-graph/SKILL.md`
- `.claude/skills/bsuk-evidence-pass/SKILL.md`
- `.claude/skills/bsuk-final-page-pass/SKILL.md`
- `.claude/skills/bsuk-footer-agent/SKILL.md`
- `.claude/skills/bsuk-gate-integrity/SKILL.md`
- `.claude/skills/bsuk-google-map/SKILL.md`
- `.claude/skills/bsuk-image-generation/SKILL.md`
- `.claude/skills/bsuk-indexing/SKILL.md`
- `.claude/skills/bsuk-infographic/SKILL.md`
- `.claude/skills/bsuk-learning-loop/SKILL.md`
- `.claude/skills/bsuk-location-page-builder/SKILL.md`
- `.claude/skills/bsuk-page-hardening/SKILL.md`
- `.claude/skills/bsuk-perf-gate/SKILL.md`
- `.claude/skills/bsuk-photo-ingest/SKILL.md`
- `.claude/skills/bsuk-puppy-page-builder/SKILL.md`
- `.claude/skills/bsuk-puppy-page-excellence/SKILL.md`
- `.claude/skills/bsuk-query-augmentation/SKILL.md`
- `.claude/skills/bsuk-reddit-threads/SKILL.md`
- `.claude/skills/bsuk-seo-master-checklist/SKILL.md`
- `.claude/skills/bsuk-site-patterns/SKILL.md`
- `.claude/skills/bsuk-visual-intelligence/SKILL.md`
- `.claude/skills/bsuk-website-health/SKILL.md`
- `.claude/skills/bsuk-youtube/SKILL.md`
- `.claude/skills/caption-writer/SKILL.md`
- `.claude/skills/framework-aida/SKILL.md`
- `.claude/skills/framework-aio-geo/SKILL.md`
- `.claude/skills/framework-bab/SKILL.md`
- `.claude/skills/framework-ebp/SKILL.md`
- `.claude/skills/framework-eeat/SKILL.md`
- `.claude/skills/framework-eebp/SKILL.md`
- `.claude/skills/framework-fab/SKILL.md`
- `.claude/skills/framework-heading-hierarchy/SKILL.md`
- `.claude/skills/framework-library/SKILL.md`
- `.claude/skills/framework-pas/SKILL.md`
- `.claude/skills/framework-pdb/SKILL.md`
- `.claude/skills/framework-qab/SKILL.md`
- `.claude/skills/grill-me/SKILL.md`
- `.claude/skills/image-metadata/SKILL.md`
- `.claude/skills/image-prompt-generator/SKILL.md`
- `.claude/skills/internal-link-agent/SKILL.md`
- `.claude/skills/keyword-cluster/SKILL.md`
- `.claude/skills/manual-auditor-check/SKILL.md`
- `.claude/skills/openspec-apply-change/SKILL.md`
- `.claude/skills/openspec-archive-change/SKILL.md`
- `.claude/skills/openspec-explore/SKILL.md`
- `.claude/skills/openspec-propose/SKILL.md`
- `.claude/skills/research-recency/SKILL.md`
- `.claude/skills/section-auditor/SKILL.md`
- `.claude/skills/session-closer/SKILL.md`
- `.claude/skills/session-handoff/SKILL.md`
- `.claude/skills/sitemap-agent/SKILL.md`

## Commands — 4

Every `.md` under `.claude/commands/`, each a slash command. The `opsx/` set is
vendored from upstream OpenSpec, like the four `openspec-*` skills.

- `.claude/commands/opsx/apply.md`
- `.claude/commands/opsx/archive.md`
- `.claude/commands/opsx/explore.md`
- `.claude/commands/opsx/propose.md`

## Scripts — 109

Every `.py`, `.sh` and `.mjs` in `scripts/`. A script the source repo had and this
list does not was not ported; `data/port-manifest.json` records the decision.

- `scripts/_html.py`
- `scripts/_kit_sections.py`
- `scripts/_md_artifact.py`
- `scripts/_slugs.py`
- `scripts/aeo_audit.py`
- `scripts/answer_board_batch.py`
- `scripts/answer_sheet.py`
- `scripts/bake_images.py`
- `scripts/board_approve.py`
- `scripts/board_entities.py`
- `scripts/board_gate.py`
- `scripts/build_agent_registry.py`
- `scripts/build_answer_board.py`
- `scripts/build_board_previews.py`
- `scripts/build_component_canvas.py`
- `scripts/build_design_canvas.py`
- `scripts/build_design_system.py`
- `scripts/build_favicons.py`
- `scripts/build_llms_txt.py`
- `scripts/build_lockups.py`
- `scripts/build_migration_report.py`
- `scripts/build_page_board.py`
- `scripts/build_picks_board.py`
- `scripts/build_plan_artifact.py`
- `scripts/build_redirects.py`
- `scripts/build_report_artifact.py`
- `scripts/build_scorecard.mjs`
- `scripts/build_search_index.py`
- `scripts/build_spec_artifact.py`
- `scripts/build_system_registry.py`
- `scripts/check_city_canvas.py`
- `scripts/city_components.py`
- `scripts/city_must_differ.py`
- `scripts/city_side_by_side.mjs`
- `scripts/competitor_registry_check.py`
- `scripts/design_system_publish_manifest.py`
- `scripts/dup_content_audit.py`
- `scripts/evidence_audit.py`
- `scripts/extract_blog.py`
- `scripts/extract_images.py`
- `scripts/extract_wp.py`
- `scripts/extract_writers.py`
- `scripts/facts_preserved_check.py`
- `scripts/family_rules.py`
- `scripts/faq_layout.py`
- `scripts/final_page_audit.py`
- `scripts/form_contract_audit.py`
- `scripts/freeze_city_picks.py`
- `scripts/gap_matrix.py`
- `scripts/gate_page.py`
- `scripts/gemini_log.py`
- `scripts/generate_page_dates.py`
- `scripts/generate_sitemaps.py`
- `scripts/generated_briefs.py`
- `scripts/health-sweep.sh`
- `scripts/hero_phone_shots.mjs`
- `scripts/image_candidates.py`
- `scripts/image_designs.py`
- `scripts/image_rules.py`
- `scripts/indexnow_submit.py`
- `scripts/infographic_plan.py`
- `scripts/ingest_image.py`
- `scripts/keyword_metrics.py`
- `scripts/keyword_variants.py`
- `scripts/link_diversity.py`
- `scripts/link_library.py`
- `scripts/link_parity_check.py`
- `scripts/marker_check.py`
- `scripts/measure_canvas_heights.mjs`
- `scripts/measure_chrome.py`
- `scripts/measurement_ledger.py`
- `scripts/migration_parity.py`
- `scripts/neighbourhoods.py`
- `scripts/not_fetched_lint.py`
- `scripts/ontology_seed.py`
- `scripts/original_slots.py`
- `scripts/outline_matrix.py`
- `scripts/outline_provenance_check.py`
- `scripts/page_hardening_scan.py`
- `scripts/page_intake.py`
- `scripts/page_run_record.py`
- `scripts/page_sections.py`
- `scripts/pageboard.py`
- `scripts/perf_audit.py`
- `scripts/placeholder_check.py`
- `scripts/port_from_cag.py`
- `scripts/prune_variants.py`
- `scripts/pull_design_picks.py`
- `scripts/quality_report.py`
- `scripts/query_augment.py`
- `scripts/query_coverage_check.py`
- `scripts/redirect_check.py`
- `scripts/reframe_og.py`
- `scripts/release_guard.sh`
- `scripts/render_baseline.py`
- `scripts/render_pages.mjs`
- `scripts/rendered_changes.py`
- `scripts/research_board.py`
- `scripts/retired_facts_check.py`
- `scripts/schema_check.py`
- `scripts/serp_reading.py`
- `scripts/session_handoff.py`
- `scripts/sitemap_check.py`
- `scripts/strategy_cite_check.py`
- `scripts/term_density.py`
- `scripts/term_gap.py`
- `scripts/thread_ledger.py`
- `scripts/verbatim_set_check.py`
- `scripts/workflow_ref_check.py`

## Data files — 30

- `data/agent-registry.json`
- `data/boards/`
- `data/breed-standards.json`
- `data/bsuk-ontology.json`
- `data/competitors.json`
- `data/component-ledger.json`
- `data/design/`
- `data/facts/`
- `data/faq.json`
- `data/image-centering.json`
- `data/image-focus.json`
- `data/image-ingest.json`
- `data/image-manifest.json`
- `data/locations.json`
- `data/outlines/`
- `data/page-dates-ignore.json`
- `data/page-dates.json`
- `data/page-map.json`
- `data/page-runs/`
- `data/port-manifest.json`
- `data/price-matrix.json`
- `data/puppies.json`
- `data/quality/`
- `data/queries/`
- `data/redirects.json`
- `data/research-boards/`
- `data/reviews.json`
- `data/settings.json`
- `data/specimen-routes.json`
- `data/verbatim/`

## Schemas — 11

Every JSON Schema in `schemas/` — the contract a data file or report is validated against.

- `schemas/board.schema.json`
- `schemas/city-picks.schema.json`
- `schemas/city-pool.schema.json`
- `schemas/competitor-report.schema.json`
- `schemas/competitors.schema.json`
- `schemas/component-ledger.schema.json`
- `schemas/llm-intel.schema.json`
- `schemas/ontology.schema.json`
- `schemas/page-run-record.schema.json`
- `schemas/port-manifest.schema.json`
- `schemas/queries.schema.json`

## Gates

`npm run check:all` runs the mechanical gates. Each prints `examined N …; 0 problems`
and exits non-zero on a problem.

| Gate | Proves |
|---|---|
| `scripts/migration_parity.py` | words, headings, images and embeds of a migrated page against the extractor |
| `scripts/facts_preserved_check.py` | a rebuilt page keeps every fact its migrated body carried |
| `scripts/link_parity_check.py` | a rebuilt page links where its board record says, and nowhere else |
| `scripts/verbatim_set_check.py` | a rebuilt page carries its migrated page's verbatim set (working rule 15) |
| `scripts/outline_provenance_check.py` | a new location, comparison or blog page is built from its approved outline and shares no heading or passage with a sibling (working rule 17) |
| `scripts/query_coverage_check.py` | a built page with a query pool carries its FAQ blocks and questions |
| `scripts/competitor_registry_check.py` | `data/competitors.json` is well formed; no unlinkable competitor is linked |
| `scripts/gap_matrix.py` | the newest gap matrix matches the intel reports (`--check`) |
| `scripts/not_fetched_lint.py` | a NOT FETCHED in a new or changed board, query or research file names its barrier |
| `scripts/thread_ledger.py` | the shared Reddit and forum thread ledger matches every page's threads file (`--check`) |
| `scripts/workflow_ref_check.py` | WORKFLOW.md and quick-start.md name only agents, scripts and npm scripts that exist |
| `scripts/marker_check.py` | no source-repo marker survives anywhere in the scanned roots |
| `scripts/placeholder_check.py` | counts launch placeholders; fails only under `BSUK_RELEASE=1` |
| `scripts/board_gate.py` | every rebuilt page's board is approved as it stands and its Asset Gate holds (`--all`) |
| `scripts/research_board.py` | STOP 1: a project 5 page's research board carries why each top-5 competitor ranks and its weakness, and the whole research deliverable, grounded or `NOT FETCHED — <barrier>`; records the picks |
| `scripts/outline_matrix.py` | STOP 2: a project 5 page's outline is a valid section matrix (census, Cat, grounded Why, keywords, images) approved on its own; refuses the page board until it is |
| `scripts/city_must_differ.py` | the city must-differ inventory matches boardStyles.ts and the built pages' picks (`--check`) |
| `scripts/check_city_canvas.py` | a city component canvas: fifteen components × three token-only, question-headed fragments that differ from every built page's arrangement (`npm run check:canvas`) |
| `scripts/retired_facts_check.py` | no retired figure, retired wording or former-city claim on a built page, in rendered data or in src/ (Known Issue 65 allowlist only shrinks) |
| `scripts/final_page_audit.py` | headings, six levels, the H5/H6 minimums |
| `scripts/schema_check.py` | structured data on every built page |
| `scripts/sitemap_check.py` | sitemap shards and what is excluded from them |
| `scripts/redirect_check.py` | `data/redirects.json` against the built routes |
| `scripts/dup_content_audit.py` | duplicate stems across siblings |
| `scripts/form_contract_audit.py` | the contact form's field contract |
| `scripts/evidence_audit.py` | term budgets and claim binding |
| `scripts/quality_report.py` | the rule ledger: enforced, judgment, untested |
| `scripts/build_agent_registry.py` | `data/agent-registry.json` matches `.claude/agents/` |
| `scripts/build_system_registry.py` | this document matches the repo |
| `scripts/port_from_cag.py` | applies `data/port-manifest.json`; never overwrites a rebase |
| `tests/py/` | the Python suite, via `npm run test:py` |
| `tests/render/` | the Playwright render harness |

## Deferred — recorded, not written

`data/port-manifest.json` records every file that crossed and every file that
deliberately did not. 34 rows are `deferred`.

- **project 3** — 4 rows (deferred to project 3, see data/port-manifest.json)
- **project 6** — 18 rows (deferred to project 6, see data/port-manifest.json)
- **no project** — 12 rows the spec rules out of the transfer entirely; they stay
  in the source repo (not ported — source repo only)

Deferred paths are not listed here by name: a name is a path, and a path this repo
does not have is exactly what the forward-reference guard exists to catch. Read the
manifest for the list.

## Mechanical guards — 13

Every rule in this repo that is actually enforced is enforced by one of these. A
guard that is not in this table is not a guard; a rule with no row here is a
convention. "How a root is added" is the column that matters when a later project
brings new files: most guards inherit their scope from the marker gate, so the
answer is usually "add the manifest row and it is covered".

| Guard | What it scans | How a root is added | Which pytest fails |
|---|---|---|---|
| `scripts/marker_check.py` | every written manifest `dst` plus CLAUDE.md, rules/, docs/reference/, package.json, tests/render/, scripts/dup_content_audit.py | add a non-`deferred` row to `data/port-manifest.json`, or a path to `FIXED_ROOTS` | `tests/py/test_marker_check.py` |
| `scripts/placeholder_check.py` | `dist/` plus the union of its literal floor (.claude/skills, .claude/agents, docs/reference) with `marker_check.scan_roots()` | inherited — anything the marker gate judges is scanned automatically | `tests/py/test_placeholder_check.py` |
| fact lint + residue lint + guarantee gate | `.claude/agents`, `.claude/skills` and `docs/reference`: locked £ amounts, banned tokens, DEFRA only beside transport, no stand-in inside a heading or path segment, lifespan 12–14; skills and `.claude/commands` also against the source-repo residue list (`RESIDUE`, among others: US sources, regulators and geography, air transport, the other brand and animals, the source repo's rule and component names, its Latin variant naming and bird-health words, permit paperwork, deploy pushes, fixed section counts, spelled-out prices, and brindle, licence, placement-count, years-in-business, weaning-age and reply-time claims) and the guarantee gate (`ungated_guarantees()`: a line that says guarantee names `guarantee_days`), which also runs over every agent; every agent against its own residue list (the other brand and its animals, US residue, the former city, known facts left as placeholders, faq.json health wording without the evidence ledger, and known paperwork — "paperwork (LICENCE_CLAIM_PLACEHOLDER)" included — written as a licence placeholder, a guard that reads every skill and command too) | drop a file into any of those trees | `tests/py/test_agent_facts.py`, `tests/py/test_agent_residue.py` |
| path guard + dead-root + dead-file + stale-marker | every repo path cited in CLAUDE.md, a `rules/` pack, a `docs/reference` doc, an agent or a non-vendored skill (the `openspec-*` skills are vendored); in non-vendored skills and every command, the source repo's roots (`DEAD_ROOTS`: `sessions/`, `site/content`, `site/system`, `content/social/`, `content/prompts/`) and its files (`DEAD_FILES`: the 29-check interior auditor, the top-pages export unless the line says NOT FETCHED, the structure manifest); in every agent, every one of those roots (`AGENT_ROOTS`), plus any file, agent, skill, npm script, `data/locations.json` field or route an agent names, and no file this repo replaced; every arrives-in-Task-N or not-ported marker whose paths now all exist | cite a path in a pack, a reference doc, an agent or a skill; add a skill, a command or an agent | `tests/py/test_rules_index.py`, `tests/py/test_claude_md.py`, `tests/py/test_agent_references.py` |
| builder-skill contracts + route guard | the location, comparison and blog builders, the SEO checklist, grill-me's board gate and the audit commands in manual-auditor-check and sitemap-agent against the code they describe (Known Issue 40); the route guard (`route_offenders()`): every site-root route a skill, a command or an agent names is built, in `data/page-map.json`, redirected, a `public/` folder or a stated non-page (seo-rules.md Rule 62; skipped without `dist/`); in an agent, a competitor's own URL (its domain and the path after it) and a `/tmp/` path are not routes | add a test beside the claim a builder makes; a new skill, command or agent is route-checked automatically | `tests/py/test_builder_skills.py` |
| table lint + frontmatter | every skill's frontmatter and every markdown table in the skill tree | add a skill directory under `.claude/skills` | `tests/py/test_skills_frontmatter.py` |
| harness vocabulary | `tests/render/` check ids, families and the deferred-check register | register a check in the harness | `tests/render/meta.spec.ts` via `npm run test:render:meta` |
| credentials doc + secret scan | `docs/reference/credentials.md` key table; every `.env` value against all tracked files, the run log and `docs/artifacts/*.html`; credential SHAPES across `marker_check.scan_roots()` plus docs/reports, docs/artifacts, data/quality/scorecards, tests/py/fixtures | inherited from the marker gate; add a key to `.env` and `.env.example` | `tests/py/test_credentials_doc.py`, `tests/py/test_no_env_value_committed.py`, `tests/py/test_secret_shapes.py` |
| agent + system registries | `.claude/agents` frontmatter against `data/agent-registry.json`; this document against the repo | add an agent, a skill, a command, a script or a `data/` file | `npm run agents`, `npm run registry` (both `--check`) |
| workflow references | `docs/reference/WORKFLOW.md` and `docs/reference/quick-start.md`: every `bsuk-*` agent or skill name, `scripts/...` path and `npm run` name, unless the line carries the parenthesised not-ported marker | name it in either doc — coverage is the whole of both files | `tests/py/test_workflow_ref_check.py`, `npm run check:workflow` |
| page-map provenance | CLAUDE.md, README.md, `docs/reference`, `rules/`, every agent, skill and command: no line ties `data/page-map.json` to the board builder as its maker — the map is the WordPress extractor's record of the old site, and a new page's record is its board | add a file to any of those trees | `tests/py/test_page_map_claims.py` |
| render baseline | the generated table in `docs/reports/render-baseline-project2.md` against the scorecards | regenerate with `scripts/render_baseline.py --write` | `npm run baseline` |
| parity / redirects / schema / sitemaps | the built `dist/` against the migration record, the redirect map, JSON-LD and the sitemap shards | build a page — coverage follows `dist/` | `npm run check:all` |

<!-- generated:end -->
