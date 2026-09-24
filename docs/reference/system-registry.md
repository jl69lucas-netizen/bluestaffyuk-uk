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

## Agents — 41

Every agent carries `model: inherit`; effort is the only per-agent cost lever, and
`data/agent-registry.json` is GENERATED from the agents' own frontmatter by
`scripts/build_agent_registry.py`. To change an agent's effort, edit its frontmatter
and regenerate — never the other way round.

### `tier_max` — 13

| Agent | Does |
|---|---|
| `.claude/agents/bsuk-angle-agent.md` | Generates content angles, hooks and unique points of view for any BlueStaffyUK page — 5–10 options before a word of body copy is written |
| `.claude/agents/bsuk-blog-post-agent.md` | Writes commercial, transactional, review and comparison blog posts for BlueStaffyUK as markdown into src/content/blog/<slug>.md, rendered … |
| `.claude/agents/bsuk-competitor-intel.md` | Use after the competitor registry (data/competitors.json) is approved, to analyse one competitor, one tier or all of them — or … |
| `.claude/agents/bsuk-content-architect.md` | Orchestrates content creation for BlueStaffyUK |
| `.claude/agents/bsuk-content-audit-agent.md` | Four-phase deep content audit of any BlueStaffyUK page — intent gaps, subtopics competitors cover and BSUK does not, meta … |
| `.claude/agents/bsuk-framework-agent.md` | Deep-dives competitor pages for any BlueStaffyUK keyword (UK Staffy puppy, blue Staffy breeder, city queries) and extracts what they do … |
| `.claude/agents/bsuk-homepage-builder.md` | Rebuilds the BlueStaffyUK homepage (src/pages/index.astro) section-by-section |
| `.claude/agents/bsuk-location-builder.md` | Builds or rebuilds one UK city location page under /uk-locations/<slug>/ |
| `.claude/agents/bsuk-non-commodity-content-agent.md` | Produces original, breeder-authentic Staffy content no generic model could write, via a 3-phase Triad (Archaeologist / Provocateur / … |
| `.claude/agents/bsuk-purchase-guide.md` | Rebuilds /buy-blue-staffy-puppies-uk/ section-by-section |
| `.claude/agents/bsuk-seo-content-writer.md` | Writes SEO body copy for any BlueStaffyUK page or section, in Lisa Bright's first-person brand voice |
| `.claude/agents/bsuk-strategy-synthesizer.md` | Use after the competitor research has run (gap matrix, keyword-gap list, competitor reports, LLM intel) and BlueStaffyUK needs a content … |
| `.claude/agents/bsuk-structure-architect.md` | The BSUK silo architect — maps content clusters into Silo (top-down authority) or Reverse Silo (bottom-up ranking) shapes across … |

### `tier_high` — 12

| Agent | Does |
|---|---|
| `.claude/agents/bsuk-about-builder.md` | Rebuilds /blue-staffy-uk-breeders/ — Lisa Bright's breeder story page for BlueStaffyUK, Carlisle |
| `.claude/agents/bsuk-comparison-builder.md` | Builds and rebuilds Staffy comparison pages — blue vs blue-and-white coat, male vs female, Blue Staffy vs another breed — landing under … |
| `.claude/agents/bsuk-competitive-keyword-gap-agent.md` | Use after bsuk-competitor-intel has written competitor reports and the BSUK profile, to find the topics BlueStaffyUK's competitors have a … |
| `.claude/agents/bsuk-faq-agent.md` | Builds and audits FAQ sections for any BlueStaffyUK page using the QAB framework — 6–12 questions per page from real buyer language … |
| `.claude/agents/bsuk-gsc-analytics.md` | Search Console analysis — INACTIVE UNTIL PROJECT 6 |
| `.claude/agents/bsuk-hub-builder.md` | Builds aggregator hub pages that link to their spokes — the puppy hub (/available-puppies/), the location hub (/uk-locations/), the … |
| `.claude/agents/bsuk-infographic-builder.md` | Builds 400–450px (in-body) and 760px (guide) HTML/CSS infographics for any BlueStaffyUK page section |
| `.claude/agents/bsuk-interactive-component.md` | Builds interactive HTML components for BlueStaffyUK pages — first-year cost calculators in £, coat/temperament fit quizzes, paperwork … |
| `.claude/agents/bsuk-llm-keyword-intel.md` | Use when a BlueStaffyUK page needs to know what an AI engine answers to its buyer question — who the answer cites (BSUK or which registry … |
| `.claude/agents/bsuk-rank-tracker.md` | Competitor and ranking monitoring — INACTIVE UNTIL PROJECT 6 |
| `.claude/agents/bsuk-section-builder.md` | Builds one HTML section for a BlueStaffyUK page and returns a ready-to-paste block |
| `.claude/agents/bsuk-trust-signals-agent.md` | Audits BlueStaffyUK pages for missing social proof and trust elements and adds them — review widgets, trust-badge sections, testimonial … |

### `tier_medium` — 16

| Agent | Does |
|---|---|
| `.claude/agents/bsuk-accessibility-fixer.md` | Audits built BlueStaffyUK pages in dist/ for WCAG 2.1 AA — skip links, ARIA labels, focus states, keyboard navigation, colour contrast … |
| `.claude/agents/bsuk-agent-system-qa.md` | Quality review agent for the BSUK agent system |
| `.claude/agents/bsuk-batch-rebuilder.md` | Coordinates a batch page rebuild by dispatching one Agent-tool call per page to its specialist agent, all in one message, then tracks … |
| `.claude/agents/bsuk-canonical-fixer.md` | Converts relative canonical URLs to absolute across BlueStaffyUK pages |
| `.claude/agents/bsuk-competitor-registry.md` | Use to seed BlueStaffyUK's national competitor registry (data/competitors.json) for the first time, or when intel or a page build finds a … |
| `.claude/agents/bsuk-contact-form-updater.md` | Audits and standardises every contact, enquiry and newsletter form across BlueStaffyUK against src/components/ContactForm.astro — outdated … |
| `.claude/agents/bsuk-deploy-verifier.md` | Post-deploy verification and IndexNow submission — INACTIVE UNTIL PROJECT 6 |
| `.claude/agents/bsuk-footer-standardizer.md` | Audits the BlueStaffyUK footer across the built site and standardises it on src/components/SiteFooter.astro, which … |
| `.claude/agents/bsuk-image-pipeline.md` | Moves generated or supplied photographs into public/images/ under the BSUK SEO filename convention, updates every <img> reference in … |
| `.claude/agents/bsuk-keyword-verifier.md` | Verifies keyword placement, density and on-page SEO hygiene for any BlueStaffyUK page — title, H1, meta description, first 100 words, H2 … |
| `.claude/agents/bsuk-meta-description-agent.md` | Writes and audits every title tag and meta description on BlueStaffyUK — standard (50–60 char title, 140–160 char description) and … |
| `.claude/agents/bsuk-paa-agent.md` | Extracts real People Also Asked questions from Google for a UK Staffy target keyword using the Playwright CLI, formats the answers for … |
| `.claude/agents/bsuk-performance-fixer.md` | Applies proven Lighthouse Performance fixes to BlueStaffyUK pages — render-blocking CSS, script defer, font-display swap, LCP … |
| `.claude/agents/bsuk-redirect-manager.md` | Manages every 301/302 rule for BlueStaffyUK |
| `.claude/agents/bsuk-self-update.md` | Keeps the BSUK agent and skill system current: reviews what a session learned, proposes edits to the agents, skills and rule packs that … |
| `.claude/agents/bsuk-site-hygiene-agent.md` | Technical SEO hygiene for BlueStaffyUK: (1) page cannibalisation audit across the 28 location pages and the buy cluster, with 301 … |

## Skills — 57

One SKILL.md per directory under `.claude/skills/`. The `bsuk-*` set is the ported
system; the rest are the generic writing, research and framework skills.

- `.claude/skills/anti-ai-writing/SKILL.md`
- `.claude/skills/bsuk-aeo-pass/SKILL.md`
- `.claude/skills/bsuk-blog-post/SKILL.md`
- `.claude/skills/bsuk-broken-links/SKILL.md`
- `.claude/skills/bsuk-comparison-page-builder/SKILL.md`
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
- `.claude/skills/bsuk-indexing/SKILL.md`
- `.claude/skills/bsuk-learning-loop/SKILL.md`
- `.claude/skills/bsuk-location-page-builder/SKILL.md`
- `.claude/skills/bsuk-page-hardening/SKILL.md`
- `.claude/skills/bsuk-perf-gate/SKILL.md`
- `.claude/skills/bsuk-puppy-page-builder/SKILL.md`
- `.claude/skills/bsuk-query-augmentation/SKILL.md`
- `.claude/skills/bsuk-reddit-threads/SKILL.md`
- `.claude/skills/bsuk-seo-master-checklist/SKILL.md`
- `.claude/skills/bsuk-site-patterns/SKILL.md`
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
- `.claude/skills/sitemap-agent/SKILL.md`

## Scripts — 70

Every `.py`, `.sh` and `.mjs` in `scripts/`. A script the source repo had and this
list does not was not ported; `data/port-manifest.json` records the decision.

- `scripts/_html.py`
- `scripts/_kit_sections.py`
- `scripts/_slugs.py`
- `scripts/aeo_audit.py`
- `scripts/bake_images.py`
- `scripts/board_approve.py`
- `scripts/board_entities.py`
- `scripts/board_gate.py`
- `scripts/build_agent_registry.py`
- `scripts/build_board_previews.py`
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
- `scripts/final_page_audit.py`
- `scripts/form_contract_audit.py`
- `scripts/gap_matrix.py`
- `scripts/generate_page_dates.py`
- `scripts/generate_sitemaps.py`
- `scripts/health-sweep.sh`
- `scripts/image_designs.py`
- `scripts/indexnow_submit.py`
- `scripts/keyword_variants.py`
- `scripts/link_diversity.py`
- `scripts/link_library.py`
- `scripts/link_parity_check.py`
- `scripts/marker_check.py`
- `scripts/measure_canvas_heights.mjs`
- `scripts/measure_chrome.py`
- `scripts/migration_parity.py`
- `scripts/ontology_seed.py`
- `scripts/outline_provenance_check.py`
- `scripts/page_hardening_scan.py`
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
- `scripts/release_guard.sh`
- `scripts/render_baseline.py`
- `scripts/schema_check.py`
- `scripts/sitemap_check.py`
- `scripts/strategy_cite_check.py`
- `scripts/verbatim_set_check.py`

## Data files — 22

- `data/agent-registry.json`
- `data/boards/`
- `data/bsuk-ontology.json`
- `data/competitors.json`
- `data/component-ledger.json`
- `data/design/`
- `data/facts/`
- `data/faq.json`
- `data/image-centering.json`
- `data/image-manifest.json`
- `data/locations.json`
- `data/page-dates.json`
- `data/page-map.json`
- `data/port-manifest.json`
- `data/price-matrix.json`
- `data/puppies.json`
- `data/quality/`
- `data/queries/`
- `data/redirects.json`
- `data/reviews.json`
- `data/settings.json`
- `data/verbatim/`

## Gates

`npm run check:all` runs the mechanical gates. Each prints `examined N …; 0 problems`
and exits non-zero on a problem.

| Gate | Proves |
|---|---|
| `scripts/marker_check.py` | no source-repo marker survives anywhere in the scanned roots |
| `scripts/placeholder_check.py` | counts launch placeholders; fails only under `BSUK_RELEASE=1` |
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
deliberately did not. 44 rows are `deferred`.

- **project 3** — 8 rows (deferred to project 3, see data/port-manifest.json)
- **project 6** — 22 rows (deferred to project 6, see data/port-manifest.json)
- **no project** — 14 rows the spec rules out of the transfer entirely; they stay
  in the source repo (not ported — source repo only)

Deferred paths are not listed here by name: a name is a path, and a path this repo
does not have is exactly what the forward-reference guard exists to catch. Read the
manifest for the list.

## Mechanical guards — 10

Every rule in this repo that is actually enforced is enforced by one of these. A
guard that is not in this table is not a guard; a rule with no row here is a
convention. "How a root is added" is the column that matters when a later project
brings new files: most guards inherit their scope from the marker gate, so the
answer is usually "add the manifest row and it is covered".

| Guard | What it scans | How a root is added | Which pytest fails |
|---|---|---|---|
| `scripts/marker_check.py` | every written manifest `dst` plus CLAUDE.md, rules/, docs/reference/, package.json, tests/render/, scripts/dup_content_audit.py | add a non-`deferred` row to `data/port-manifest.json`, or a path to `FIXED_ROOTS` | `tests/py/test_marker_check.py` |
| `scripts/placeholder_check.py` | `dist/` plus the union of its literal floor (.claude/skills, .claude/agents, docs/reference) with `marker_check.scan_roots()` | inherited — anything the marker gate judges is scanned automatically | `tests/py/test_placeholder_check.py` |
| fact lint | `.claude/agents` and `.claude/skills`: locked £ amounts, banned tokens, DEFRA only beside transport, no stand-in inside a heading or path segment, lifespan 12–14 | drop a file into either tree | `tests/py/test_agent_facts.py` |
| path guard + stale-marker | every repo path cited in a `docs/reference` doc, and every `(arrives in Task N)` marker whose path now exists | cite a path in a reference doc | `tests/py/test_rules_index.py`, `tests/py/test_claude_md.py` |
| table lint + frontmatter | every skill's frontmatter and every markdown table in the skill tree | add a skill directory under `.claude/skills` | `tests/py/test_skills_frontmatter.py` |
| harness vocabulary | `tests/render/` check ids, families and the deferred-check register | register a check in the harness | `tests/render/meta.spec.ts` via `npm run test:render:meta` |
| credentials doc + secret scan | `docs/reference/credentials.md` key table; every `.env` value against all tracked files, the run log and `docs/artifacts/*.html`; credential SHAPES across `marker_check.scan_roots()` plus docs/reports, docs/artifacts, data/quality/scorecards, tests/py/fixtures | inherited from the marker gate; add a key to `.env` and `.env.example` | `tests/py/test_credentials_doc.py`, `tests/py/test_no_env_value_committed.py`, `tests/py/test_secret_shapes.py` |
| agent + system registries | `.claude/agents` frontmatter against `data/agent-registry.json`; this document against the repo | add an agent, a skill, a script or a `data/` file | `npm run agents`, `npm run registry` (both `--check`) |
| render baseline | the generated table in `docs/reports/render-baseline-project2.md` against the scorecards | regenerate with `scripts/render_baseline.py --write` | `npm run baseline` |
| parity / redirects / schema / sitemaps | the built `dist/` against the migration record, the redirect map, JSON-LD and the sitemap shards | build a page — coverage follows `dist/` | `npm run check:all` |

<!-- generated:end -->
