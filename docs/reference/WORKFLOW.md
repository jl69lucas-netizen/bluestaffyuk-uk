# BlueStaffyUK — Master Workflow

> **Read this before starting any new page, sprint, or monitoring cycle.**
> This is the authoritative end-to-end sequence for every agent in `.claude/agents/`.

The 7-sprint model is domain-neutral and stands as written. What changed in the project 2
re-base is the cast. The agent roster is whatever `data/agent-registry.json` lists —
this file deliberately does not restate the count, because a number written here is a
number that goes stale the next time an agent lands. Every agent
this file names that is not in `data/agent-registry.json` is **deferred to project 6**
(analytics, outreach, monitoring and conversion work that needs Search Console, a live
domain or a remote) — `data/port-manifest.json` records the decision for each one, and
`docs/reference/system-registry.md` lists what actually exists. Calling a deferred agent
fails; the sprint step it sits in is simply not runnable yet, and the gate it feeds is
advisory until project 6.

Search Console and GA4 data are **NOT FETCHED**. Every step below that reads GSC, a rank
or a traffic baseline is inert today. No number from those sources may be quoted anywhere.

## Running this pipeline under an autonomous model (added 2026-09-07)

Fable 5.1 sessions run with the breeder away: a mid-task question blocks the build. So the
pipeline has exactly **three places where an agent may stop and ask** — the `[APPROVE]` gates at
Sprint 0.5 (the brief), Sprint 1 (outline + distribution matrix + header style) and the ASSET GATE.
Everywhere else the Clarification Checkpoint applies: write the finished part to disk, log the
question to the brief's `## Open Flags`, ask ONE narrow question, keep building what is not blocked.
Agents no longer open with a "which mode?" interview; they read the mode from the invocation or the
latest session brief and UK city their default. `grill-me --brief <path>` is the autonomous form of
Sprint 0.5.

**Parallel work is the `Agent` tool** — one call per track / UK city / page, all in one message.
There is no `CLAUDE_CODE_FORK_SUBAGENT` variable and never was. A Workflow script (deterministic
fan-out) may run only when the breeder asks for one in their own words.

**Where the work lands:** on the project branch the plan names, committed after every task and
never pushed (`CLAUDE.md` working rules 2–3, `rules/deploy.md`). There is no remote, no host and
no deploy until project 6; IndexNow and every live step wait for it (Sprint 5).

## The 7-Sprint Page Pipeline (rewritten 2026-07-29)

```
Sprint 0    Intel      competitor-intel --all + keyword-gap + gsc-analytics
                       + research-recency                            [REVIEW]
Sprint 0.5  Orient     grill-me + full fan-out queries               [APPROVE]
Sprint 1    Blueprint  visual companion + image-framing letters
                       + distribution matrix (A/B/C categories)
                       + full H1–H6 outline + HEADER STYLE + WHY
                       + header dup-gate                             [APPROVE]
── ASSET GATE ──  breeder drops the infographics and says "start"
Sprint 2    Build      the page-type builder skill + EEBP + dup-gate (during)
Sprint 3    Harden     page_hardening_scan + seam_parity + runtime probes
                       @375/768/1280 + contrast + overflow + dup-gate
Sprint 4    Final      bsuk-final-page-pass + AEO/GEO + keyword-verifier
                       + anti-ai-writing + technical batch
                       + bsuk-evidence-pass
Sprint 5    Ship       project 6 only: generate_sitemaps + deploy-verify + live 200
Sprint 6    Bank       session-closer + memory + BACK-PROPAGATE to the
                       skill/scanner that enforces each lesson + sweep siblings
```

**Sprint 3 (Harden) must stay its own sprint, never a bullet inside Final.** The
rationale is the source repo's, not this one's — BlueStaffyUK's own history starts
2026-09-15 and is in `docs/reference/session-log.md`. There, a hand-raised page passed
every static gate and still came back "feels rushed," with
five root causes that were invisible in source review; `scripts/page_hardening_scan.py`
existed but sat outside the named pipeline, so it stayed optional. Then, in the source
repo on 2026-07-28, a page that scanned `0 ERROR · 0 WARN` shipped with invisible FAQ
answers and five mandated components missing. The moment Harden is a sub-bullet, it is the bullet that
gets skipped.

**Before acting on ANY gate's output, read `.claude/skills/bsuk-gate-integrity/SKILL.md`.** Twelve
checkers have reported defects that did not exist on this cluster, and two reported
PASS having examined zero pages.

---

## Where the rules live (changed 2026-08-02)

`CLAUDE.md` no longer carries the rules. It keeps identity, paths, the deploy model and
the nine `judgment` rules (working rules 1–9) plus the breeder's working rules 10–16;
everything else moved **verbatim** into `rules/*.md`, indexed
by `data/quality/rule-index.json` where every rule is `test`, `judgment` or `untested`.
**`untested` means deletion candidate** and `scripts/quality_report.py` §5 prints the list every
run. Page-type → rule-pack routing is the table in `CLAUDE.md`.

The pixel-level rules are enforced by `tests/render/`, not by a document. When a defect
escapes, charge it to the harness — add the case to `tests/render/fixtures/known_broken/`,
watch the meta gate fail, fix the check — and write no new rule.

## Entry Point & Prerequisites

Before any work begins, verify these exist:

| Artifact | Location | How to create |
|----------|----------|---------------|
| Page map | `data/page-map.json` | Run `python3 scripts/build_page_board.py` |
| Locations | `data/locations.json` | Ships with the repo — the 28 UK cities, and the only list |
| Puppy inventory | `data/puppies.json` | Ships with the repo — the six locked puppies |
| Session brief | a dated brief under docs/superpowers/sessions/ | Run the `grill-me` skill |

The competitor registry, the intel reports and the gap matrix exist (competitor intelligence
build, 2026-09-23): `@bsuk-competitor-registry` writes data/competitors.json after the user
approves the list, `@bsuk-competitor-intel` writes docs/research/competitors/<id>.json and
`.md` (plus the BSUK profile with `--bsuk`), and `python3 scripts/gap_matrix.py --write` builds
docs/research/gap-matrix-<date>.md from them (`npm run check:gaps` keeps it honest). Run them in
this order: registry → intel (+ `--bsuk`) → `gap_matrix.py --write` →
`@bsuk-competitive-keyword-gap-agent` → `@bsuk-llm-keyword-intel` → `@bsuk-strategy-synthesizer`.
The traffic baseline is still deferred to project 6 (`@bsuk-gsc-analytics`; GSC is NOT
FETCHED until the domain is live).

**Hard Gate:** No page enters Sprint 2 (Content Production) until `data/page-map.json`
exists and `@bsuk-content-architect` has assigned a framework to the target page.

---

## Sprint 0 — Intelligence Gathering
*Run once per project, then quarterly. Takes ~1 session.*

### Tracks (run in dependency order — not all at once)

Order: Track A's registry, then intel `--all`, then intel `--bsuk` and the gap-matrix rebuild;
then the keyword-gap list (Sprint 1 Step 0a); then Track B's LLM intel per page (Step 0b); then
the strategy synthesizer (Step 0c). `@bsuk-gsc-analytics` is deferred to project 6. Only
independent runs of one step — intel on several competitors, LLM intel on several pages — go
out as parallel `Agent` calls in one message.

**Track A — Competitive Intelligence**
```
@bsuk-competitor-registry
  → Discover about 25 competitors (30 at most) from about ten seed keywords
  → Classify into five tiers: 1 breeder · 2 marketplace or directory · 3 breed information · 4 rescue or non-commercial · 5 suspect seller (never linked)
  → USER GATE: approve competitor list (the proposal in docs/research/)
  → Output: data/competitors.json (checked by npm run check:competitors)

@bsuk-competitor-intel --all
  → STOPS before any fetch with the ids, tiers and ceiling (7 × N); resumes only on `fetch approved: --all` (or `fetch approved: --tier <n>`)
  → Analyse every registry competitor across 10 metric categories
  → Output: docs/research/competitors/<id>.json + <id>.md; before hand-off the contact scan, scripts/gap_matrix.py --write, npm run check:gaps and npm run check:competitors must all pass
  → Any new or changed report makes the BSUK profile stale: re-run @bsuk-competitor-intel --bsuk (same after-run checks) before the gap matrix is read
  → A registry fix (a moved, sold or parked site) goes to @bsuk-competitor-registry first
  → Output: docs/research/gap-matrix-[date].md (checked by npm run check:gaps)
  → Hand-off: @bsuk-competitive-keyword-gap-agent, then @bsuk-strategy-synthesizer
```

**Track B — Traffic & LLM Intelligence**
```
@bsuk-gsc-analytics
  → Analyze data/analytics/ GSC CSV exports
  → Output: docs/reports/top-pages.md (deferred to project 6) (clicks, impressions, positions)

@bsuk-llm-keyword-intel <slug>
  → One engine per page (DataForSEO ChatGPT scraper through the spend guard; reuses a saved answer)
  → Records who the answer cites (BSUK or registry competitors), missing entities, answer format
  → Output: docs/research/llm-intel/<slug>-[date].json
  → Runs after the gap matrix (its rows feed the question as GAP_TOPICS) and the keyword-gap list (Sprint 1 Step 0a), and before the strategy synthesizer (Sprint 1 Step 0c)
```

**Stop tokens** (each agent stops until the controller sends its exact wording): registry `spend approved: <seeds>; balance $<n>[; refresh]`, then `approved: docs/research/competitor-registry-proposal-<date>.md`; intel `fetch approved: --all` or `fetch approved: --tier <n>` (keyword-gap re-fetches take `fetch approved: --all` too); llm-intel `spend approved: <slug>; balance $<n>[; refresh]`. `spend declined` / `fetch declined` run without the call.

**Note — Session Orientation moved to Sprint 0.5:**
grill-me runs AFTER Sprint 0 Gate passes (the gap matrix must exist; top-pages is deferred to project 6). See Sprint 0.5 block below.

### SESSION CONTEXT Block (output of grill-me)
```
SESSION CONTEXT:
- Page Type: [location | breed guide | comparison | blog | money page | hub]
- Target Keyword: [exact keyword]
- Framework: [AIDA | QAB | H-S-S | Entity-Tree | BAB | EBP]
- Framework Reason: [why this framework fits this page's goal]
- AIO / GEO Approach: [Featured Snippet | Entity-first | Both]
- AIO Notes: [AI engines where BSUK appears / needs protection]
- Component Style: [informational 760px | transactional 1200px | hybrid]
- Visual Plan: [section → type mapping, or "decide during build"]
- Audit Status: [complete | pending → run bsuk-content-audit-agent first]
- LLM Visibility: [0–10 score | "not measured" → run bsuk-llm-keyword-intel]
- Page Map Entry: [yes — the slug is in data/page-map.json | no → run python3 scripts/build_page_board.py first]
- Hub Page: [/url/ of parent hub | "needs to be built first"]
- Internal Links Needed: [from workflow gate check, or "TBD after audit"]
```

### Sprint 0 Gate
Before proceeding to Sprint 0.5:
- [ ] Competitor research current: `npm run check:competitors` and `npm run check:gaps` pass on a dated gap matrix (per-page research under seo-rules Rule 11 still applies) — the registry and gap matrix exist; the traffic baseline is deferred to project 6 (see `data/port-manifest.json`)
- [ ] `data/page-map.json` current (`python3 scripts/build_page_board.py`)

---

## Sprint 0.5 — Session Orientation
*Run once per page build, after Sprint 0 Gate passes. grill-me now runs here — with full intelligence data loaded.*

```
grill-me skill
  → Reads: CLAUDE.md + the traffic baseline (deferred to project 6) + the reference docs in docs/reference/ + the per-page competitor research of seo-rules Rule 11 + last session brief
  → WARNS if gap matrix missing (intelligence incomplete — answers will be imprecise)
  → Asks 13–14 questions one at a time (13 without prior brief; 14 with one):
      Business Layer: outcome, traffic reality, worst performer, customer journey, constraints
      Task Layer: target slug, workflow gate check, done-looks-like, reader profile, benchmark
      NEW: framework choice + reason, AIO/GEO approach, visual plan section-by-section, urgency
  → Output: a dated session report under docs/superpowers/sessions/
  → Includes: SESSION CONTEXT block with framework, AIO approach, visual plan, component style
```

### Sprint 0.5 Gate
Before proceeding to Sprint 1:
- [ ] Session brief written with full SESSION CONTEXT block
- [ ] Framework chosen + reason documented
- [ ] AIO/GEO approach chosen
- [ ] Visual plan sketched (or "decide during build" noted per section)

---

## Sprint 1 — Architecture Sprint
*Run once at project start, then when adding new page clusters.*

### Sequence (in order)

```
Step 0a: bsuk-competitive-keyword-gap-agent
  → Reads the `pages` lists in the competitor-intel reports, and BSUK's side from the BSUK profile (docs/research/competitors/bsuk.json); no profile → the page-map fallback, and every gap is "provisional" until `--bsuk` and a re-run
  → Stale reports (`pages` NOT FETCHED or older than 30 days): one → the agent re-fetches it (1 map + up to 6 scrapes); more than one → STOP until `fetch approved: --all` or `fetch declined`; tier 5 is never re-fetched
  → Scores every gap with its script, never by eye: 7+ (or a licence / health-test topic) = high, 4–6 = medium, under 4 = low; every gap is proved by a competitor URL
  → High gaps → bsuk-content-architect; a gap whose BSUK page is a noindex stub goes as "rebuild the stub <url>" (project 5), never a new page; medium gaps → bsuk-strategy-synthesizer's content calendar
  → Output: docs/research/keyword-gap-[date].md

Step 0b: bsuk-llm-keyword-intel <slug> (one run per page in scope)
  → Output: docs/research/llm-intel/<slug>-[date].json (see Sprint 0 Track B)

Step 0c: bsuk-strategy-synthesizer  ← STRATEGY BEFORE STRUCTURE
  → Reads existing research only (gap matrix, keyword-gap list, competitor reports, LLM intel; GSC is NOT FETCHED until project 6) — does NOT re-run Sprint 0
  → Needs Steps 0a and 0b first: registry → intel (+ --bsuk) → gap_matrix.py --write → keyword-gap → llm-intel → strategy-synthesizer
  → Produces TWO reverse-engineered strategies, recommends ONE with a data-grounded WHY + named trade-off
  → Derives the concrete artifact for the cluster (e.g. the 9 blog topics + 1 hub)
  → Runs scripts/strategy_cite_check.py before handoff
  → Output: docs/superpowers/sessions/<date>-<topic>-strategy.md → hands the chosen strategy to bsuk-content-architect (explicit path)

Step 1: bsuk-structure-architect
  → Maps all 52 target pages into Silo or Reverse Silo structure
  → Ensures every page is ≤3 clicks from homepage
  → Output: docs/superpowers/sessions/<YYYY-MM-DD>-structure.md (data/page-map.json is generated by scripts/build_page_board.py and never hand-edited)

Step 2: bsuk-hub-builder  ← BUILD HUBS BEFORE SPOKES
  → The hubs that exist (the agent's own table):
    - /uk-locations/ (location hub — the 28 rows of data/locations.json)
    - /available-puppies/ (puppy hub)
    - /blue-staffy-blog-guides/ (guides hub)
    - /uk-staffordshire-bull-terrier-guide/ (breed guide)
  → No comparison hub exists yet: project 5's strategy file gives its URL; a new hub is built only when the strategy names it
  → Hub pages link to all their spoke pages

Step 3: bsuk-seasonal-content-agent (not ported — no agent file; skip this step)
  → Builds data/seasonal-calendar.json
  → Major peaks: Spring Puppy Season (Mar–May), Christmas, Valentine's Day, Mother's Day
  → Routes seasonal page briefs to content-architect

Step 4: bsuk-content-architect
  → Reads: the strategy file by explicit path (docs/superpowers/sessions/<date>-<topic>-strategy.md) + the gap matrix + data/page-map.json; the traffic baseline is deferred to project 6
  → Assigns framework to each page in priority queue:
    | Page Type | Framework |
    |-----------|-----------|
    | Location pages | AIDA + Entity-Tree |
    | Breed guides | Entity-Tree + QAB |
    | Comparison pages | QAB (head-to-head + FAQ) + BAB (owner story) |
    | Scam/trust pages | H-S-S + EBP |
    | Pricing pages | QAB + EBP |
    | Blog posts | AIDA or BAB |
    | About / breeder story | H-S-S |
  → Output: content brief queue (priority ordered by opportunity score)
```

### Sprint 1 Gate
- [ ] `data/page-map.json` written
- [ ] Priority page queue defined (sorted by opportunity score ≥7)
- [ ] Hub pages built before spoke pages
- [ ] Framework assigned to each page type by content-architect

---

## Sprint 2 — Content Production
*The main build loop. Runs continuously as pages are built.*

### Per-Page Pipeline (Standard Flow)

```
1. bsuk-content-audit-agent [TARGET_URL] [KEYWORD] [PAGE_TYPE]
   → Phase 0: Outline (MUST be approved before Phase 1)
   → Phase 1: Intent gap analysis
   → Phase 2: Competitor analysis (most valuable phase)
   → Phase 3: Action plan + internal linking opportunities
   → Output: a dated file under docs/superpowers/sessions/

1.5. SECTION MAP + COMPONENT SELECTION GATE  ← MANDATORY BEFORE ANY WRITING
   → Based on audit output, list every section from Hero → final CTA
   → For each section: assign a component from the kit — src/components/kit/ (listed in
     data/design/components.json, demoed by src/components/kit/_registry.ts at /kit-preview/) —
     and pick one of the THREE styles the page's board (data/boards/<slug>.json) renders for that
     section (CLAUDE.md working rules 13, 14, 16; refresh delta per
     .claude/skills/bsuk-component-refresh/SKILL.md and .claude/skills/bsuk-component-variations/SKILL.md)
   → Show user table: | Section | Content Purpose | Component | Variant |
   → USER APPROVES the full map — explicit approval required
   → LOCKED after approval — no component changes after this point
   → Session brief updated with locked component map
   → Only THEN proceed to step 2

2. bsuk-angle-agent
   → Generates 5–10 content angles before any writing begins
   → Selects: counter-intuitive angles, fear-based hooks, story-first openings
   → USER selects preferred angle

3. bsuk-paa-agent
   → Extracts real PAA questions from Google for target keyword
   → Formats answers for Featured Snippet capture
   → Passes question set to bsuk-faq-agent
   → Target: Position 0 + AIO citation

3.5. bsuk-seo-master-checklist skill  ← INVOKE BEFORE WRITING BEGINS
   → Skills path: .claude/skills/bsuk-seo-master-checklist/SKILL.md
   → Phase 1: Competitor analysis (8+ competitors) + 10-category keyword fan-out (top competitor's real count +5–10, Rule 56 as of 2026-09-09) + entity research (95–105 distinct, each once, Rule 57)
   → Phase 2: Page Outline Gate (Rule 51 — FULL STOP until outline approved)
   → Phase 3: 5-Tier Section Creation Form for each section (Rule 59)
   → Phase 4: 4-Part Delivery Format output (Rule 60)
   → Also defines: 3 anchor text strategies (Rule 58), Internal Linking Library (Rule 62 + Appendix A)
   → Reads: rules/images.md for image/infographic sizing and placement per page type (data/image-manifest.json only indexes the images that exist)

4A. bsuk-seo-content-writer [for standard optimization]
    → Writes SEO-optimized body copy
    → Uses framework assigned in Sprint 1
    → Applies: Negative Keyword Counter-Positioning (wild-caught, scam, cheap)
    → Generic-Slayer Filter: removes generic platitudes

4B. bsuk-non-commodity-content-agent [for breeder-authentic content]
    → Use when: page needs original insights competitors can't copy
    → Triad model: Archaeologist (mines real facts) → Provocateur (flips generic advice) → Stylist (BSUK voice)
    → Requires: real breeder input from Lisa Bright, or a BSUK data file (the source repo's project-context file was never ported)

5. bsuk-faq-agent
   → QAB framework: Question → Answer → Benefit
   → Generates 6–12 questions per page
   → Sources: a location page's question file (data/queries/<slug>.json) first; otherwise PAA output + the BSUK question bank (data/faq.json). GSC is NOT FETCHED until project 6
   → Output: FAQPage JSON-LD + <details>/<summary> accordion HTML

6. bsuk-section-builder [for custom page sections]
   → Section types: hero, features, faq, cta, testimonials, comparison-table,
                    price-card, counter_snippet, toc, trust-bar, divider, video
   → Each is a kit component in src/components/kit/ (the agent's table)
   → Called by all page builder agents

7. bsuk-infographic-builder [if visual reinforcement needed]
   → Reads rules/images.md FIRST — image sizes, crops and alt rules for this page type; data/image-manifest.json indexes the images that exist
   → HTML/CSS infographics: 400px height fixed (desktop), auto (mobile)
   → Width: 760px for guides/blogs/care pages · 1100px for homepage/location/hero sections
   → Types: Comparison / Feature Grid / Process Flow / AI-Generated (Type 4) / Higgsfield MCP (Type 5)

8. bsuk-interactive-component [if calculator/quiz/checklist needed]
   → Pure HTML/CSS + minimal vanilla JS
   → Types: cost calculator, variant fit quiz, documentation checklist,
            shipping timeline estimator, LICENCE_CLAIM_PLACEHOLDER verification guide
   → Reads: data/price-matrix.json + data/puppies.json (the source repo's cost-entities file was never ported)
```

### Specialty Flows (Run in Parallel with Main Queue)

**Location Pages (all UK cities at once):**
```
bsuk-batch-rebuilder
  → Reads data/locations.json
  → One `Agent` call per UK city to bsuk-location-builder, all in one message (parallel)
  → Structure: docs/reference/location-page-template.md via .claude/skills/bsuk-location-page-builder/SKILL.md — the section count comes from the competitors, never a fixed number
  → Each page gets UK city-specific: the city's own geography and delivery band, the Carlisle map (bsuk-google-map skill)
  → Merges results → commit on the project branch (deploy and IndexNow are inactive until project 6)
```

**Variant Pages — not runnable:**
```
bsuk-variant-specialist (not ported — a coat-colour version for Staffies is possible later; see data/port-manifest.json)
bsuk-black-staffy-specialist (not ported — the source repo's subspecies specialist has no BSUK analogue)
  → Until one exists, coat-colour content is built by the page-type builder; pricing comes from data/puppies.json and data/price-matrix.json — never typed
```

**Comparison Pages:**
```
bsuk-comparison-builder
  → No comparison page exists yet: the pages and their hub are project 5's net-new builds, at the URLs the strategy file gives them
  → Comparison pages are EXCLUDED from seo-master-checklist + Interior-Page Standard — they own their structure (.claude/skills/bsuk-comparison-page-builder/SKILL.md)
```

**Pricing + Finance Pages — not runnable:**
```
bsuk-financial-strategist (not ported — deferred to project 6; its data file was never ported either)
  → Until then prices come from data/puppies.json and data/price-matrix.json only — never typed
```

**Breed Guide:**
```
bsuk-breed-guide-builder (not ported — the breed guide /uk-staffordshire-bull-terrier-guide/ is already built)
  → A breed-guide refresh goes through bsuk-site-patterns and the page's own board (data/boards/<slug>.json)
```

**Blog Posts:**
```
bsuk-blog-post-agent
  → Intent types: commercial, transactional, review, alternative, comparison
  → Keywords: from gap matrix (score ≥7 buyer-intent queries)
  → Full HTML with schema
```

**Scam / Trust Content:**
```
bsuk-scam-specialist (not ported — deferred to project 6)
  → A scam / trust page is built by the page-type builder from its board until then
```

**Puppy Listings:**
```
update data/puppies.json (breeder-confirmed only) → npm run build
  → .claude/skills/bsuk-puppy-page-builder/SKILL.md builds or refreshes /available-puppies/<slug>/
  → a reserved or sold puppy: data/redirects.json + python3 scripts/redirect_check.py
  → bsuk-litter-manager and bsuk-puppy-personality (not ported — BSUK litters live in data/puppies.json)
```

---

## Sprint 3 — Harden (does the page RENDER correctly?)
*Runs on the BUILT page, before any final audit. **Never a sub-bullet of Final** — the
moment Harden becomes a bullet, it becomes the bullet that gets skipped.*

**REQUIRED SKILL:** `bsuk-page-hardening` (v2.0) · **REQUIRED FIRST:** `bsuk-gate-integrity`

```
0. npx astro build                      ← nothing below works on a stale dist/

1. python3 scripts/page_hardening_scan.py <slug>
   → 21 static checks. ERROR = shipped-broken. WARN = eyeball it.
   → §1k markup-css-drift          (101 classes styled + never rendered, 5 mandated)
   → §1l component colour specificity (.ship-tier at 1.19:1 on forest green)

2. [seam parity — the source repo's scripts/seam_parity.py was not ported (not ported — source repo only)]
   → one seam per section; exactly one seamless hero allowed. Check it by eye until a
     BSUK equivalent exists; the Sprint 3 gate row below is advisory in the meantime.
   → NEVER grep '<section class="sec"' — 6 of 8 for-sale pages don't use that class

3. npm run test:render:meta        ← THE GATE THAT CHECKS THE CHECKERS. Run it FIRST.
   → ~200 tests, ~1 min. Every check must fire on its known_broken fixture, stay
     silent on known_good, and reach its declared minExamined floor.
   → A page measured by a failing gate is not evidence. In the source repo, on
     2026-08-02, six harness defects were found in one session, five of them firing on
     EVERY page of that site.

4. npm run test:render:pages       ← 19 checks x 15 pages x 375/768/1280, ~13 min
   → BLOCKING families: IMG · LAYOUT · NAV. A blocking row fails the run.
   → ADVISORY families: SEM · SCHEMA · CSS · DUP (promoted once a full cluster is
     clean — fixtures passing is not enough).
   → Refuses to run against a stale dist/. To ship past a blocking row you must write
     RENDER_OVERRIDE=£'check-id:reason' — it is recorded in the scorecard and printed
     by quality_report.py on every run, so an override is counted, never hidden.

5. python3 scripts/quality_report.py
   → rework rate · worst family · OPEN OVERRIDES · rules with no backing test

6. Extra runtime probes in PLAYWRIGHT at 375 / 768 / 1280, for anything the harness
   does not yet cover   ← 768 is the one that fails
   → the Browser pane reports vw:0, so every probe there false-passes
   → full-page contrast · real-ch line length · component sizing

7. python3 scripts/dup_content_audit.py <slug> [<slug>...]
   python3 scripts/dup_content_audit.py --headers <slug> [<slug>...]
   → pass slugs LITERALLY; zsh does not word-split £VAR, and the gate will
     report PASS having compared nothing
```

### Sprint 3 Gate
- [ ] **`npm run test:render:meta` green BEFORE any page result is trusted**
- [ ] **`npm run test:render:pages` passes** — every blocking row fixed or overridden with a written reason
- [ ] **`scripts/quality_report.py` §4 read** — an override you did not intend to leave is a defect you decided to ship
- [ ] `page_hardening_scan` → 0 ERROR; every WARN triaged REAL / DEAD-CODE / FALSE-POSITIVE
- [ ] **Every finding confirmed on the page before any edit** (`bsuk-gate-integrity` — 12 checkers have cried wolf here)
- [ ] **Every gate's own examined count read** — a PASS over 0 pages is not a pass
- [ ] `seam_parity` PASS
- [ ] Runtime probes clean at 375 / 768 / 1280, measured in Playwright
- [ ] Dup gate 0 body + 0 header crossovers vs ALL siblings
- [ ] Every printed figure traced to `data/puppies.json` / `data/price-matrix.json` — no typed literals

---

### 3b — AEO gate (added 2026-07-30)

**REQUIRED SKILL:** `bsuk-aeo-pass` — the 6-part answer-engine gate. Hardening asks
*does the page render*; this asks *can an engine lift a correct sentence and attribute
it to us*.

```
python3 scripts/aeo_audit.py <slug>
  → ERROR: no dateModified in JSON-LD · any VISIBLE date (banned)
  → WARN:  no binomial · no breeder-name entity · no brand-owned method label
           · pronoun-heavy · buried answers (PROXY, read them) · no stat header
```

- [ ] Zero ERROR from `scripts/aeo_audit.py`
- [ ] `python3 scripts/generate_page_dates.py --check` current, map committed
- [ ] Facts correct: **LICENCE_CLAIM_PLACEHOLDER** · **£1,500 / £1,700** · **£500 refundable deposit** · guarantee length is not established, so no guarantee is written
- [ ] One of the two approved method labels present and defined
- [ ] Part 2 (atomic sections) checked BY HAND — three sections read in isolation

---

## Sprint 4 — Final (AEO/GEO + structure + schema + voice)
*Runs over ALL new pages before deploy. This is a gate, not optional.*

**REQUIRED SKILL:** `bsuk-final-page-pass` — THE final gate for EVERY page type,
including the puppy `/available/` and for-sale pages the old interior gate excluded.

```
1. npx astro build
2. python3 scripts/final_page_audit.py [--puppies]
   → page-type-aware, nested-slug aware. SUPERSEDES the source repo's interior audit, which was never ported.
   → headings: all six levels, no skipped levels, Title Case; ≥5 H5/H6 advisory on homepage + location pages (2026-09-09)
   → schema · meta · image SEO · a11y traps · links · phone · compliance copy
   → one PASS / PASS-WITH-WARNINGS / FAIL verdict; triage every ✗
3. anti-ai-writing  → AI-tell sweep on the final prose
4. bsuk-evidence-pass → python3 scripts/evidence_audit.py <slug>  (term budgets · claim→proof · labels · review attribution · title ≤70)
   → runs AFTER anti-ai-writing, BEFORE bsuk-final-page-pass; ERROR blocks deploy
```

### 4a — AEO/GEO Gate Checklist

Every page must pass ALL items before moving to Sprint 5 (Ship):

```
AEO/GEO GATE — RUN IN THIS ORDER:

1. bsuk-keyword-verifier
   → Checks: title, H1, meta, first 100 words, H2 distribution,
             alt text, internal links, canonical
   → Flags: OVER-STUFFED (>110) only — no floor (2026-09-09); trust terms answer to evidence-budgets.json
   → AEO additions: entity coverage check, declarative statement density

2. bsuk-meta-description-agent
   → Standard: 50-60 char title, 140-160 char description
   → Extended: long-form metadata for high-competition pages
   → Audits: no duplicates, no missing tags

3. bsuk-external-link-agent (not ported — deferred to project 6; insert the links by hand meanwhile)
   → Inserts authority links from docs/reference/external-link-library.md
   → Link-First rule: the anchor sits at the START of the sentence — never
     mid-sentence, never at the end (supersedes the old 'beginning or middle')
   → Verifies: all URLs return 200 before inserting

4. bsuk-trust-signals-agent
   → Adds: Google Reviews widget HTML
   → Adds: Trust Badge row (LICENCE_CLAIM_PLACEHOLDER / LICENCE_CLAIM_PLACEHOLDER / Microchipped / Veterinary Vet)
   → Adds: ReviewAggregateSchema
   → Adds: Counter Snippet blocks
   → Testimonial case studies: bsuk-case-study-agent (not ported — deferred to project 6)

5. bsuk-infographic-builder [if section needs visual reinforcement]
   → Comparisons, flag lists, benefit grids, process steps

6. Rules 55-62 Compliance Check (seo-rules.md)
   → Rule 55: Competitor analysis output — 8+ competitors, gap matrix, outranking strategy present
   → Rule 56: keyword variants = top competitor page's real count +5–10 (fetched, recorded)
   → Rule 57: 95–105 DISTINCT entities, each once where load-bearing
   → Rule 58: 3 anchor text strategies used — exact match, conversational, branded (never repeat same anchor)
   → Rule 59: 5-Tier Section Creation Form completed for all sections
   → Rule 60: 4-Part Content Delivery Format present in output
   → Rule 61: Phone number (PHONE_PLACEHOLDER) appears ONLY in footer/schema — not in body copy
   → Rule 62: Internal links use Appendix A canonical URLs from .claude/skills/bsuk-seo-master-checklist/SKILL.md
```

### 4b — AEO/GEO Schema Checklist (verify presence before deploy)

```
☐ FAQPage JSON-LD present (bsuk-faq-agent output)
☐ ≥1 declarative statement per H2 section (Entity-Tree format)
☐ First paragraph directly answers primary keyword question (Featured Snippet target)
☐ ReviewAggregateSchema present (bsuk-trust-signals-agent)
☐ BreadcrumbList schema present (bsuk-section-builder)
☐ LLM intel file written for the page (bsuk-llm-keyword-intel); the GSC traffic-baseline score is deferred to project 6
☐ LocalBusiness schema on all location pages
☐ VideoObject schema if YouTube video embedded (.claude/skills/bsuk-youtube/SKILL.md)
☐ No language implying wild-caught origin (LICENCE_CLAIM_PLACEHOLDER check)
☐ IMAGE-01: Every image alt describes THAT image, ≤125 characters, one keyword type per image (rules/images.md); no two alts match
☐ IMAGE-02: retired 2026-09-09 — no image-description blocks in body copy
☐ IMAGE-03: Infographic widths match page type (760px for guides · 1100px for homepage/location pages)
☐ IMAGE-04: OG image (og:image) is 1200×630px — separate from portrait puppy images
```

### 4c — LLM Visibility Probe (run after page goes live)

```
bsuk-llm-keyword-intel <slug>
  → Queries one engine (ChatGPT, via DataForSEO through the spend guard) for the page's buyer question
  → Checks: does the answer cite BSUK, and which registry competitors does it cite?
  → If NOT cited → route to bsuk-non-commodity-content-agent for entity strengthening
  → Output: docs/research/llm-intel/<slug>-[date].json (the GSC traffic-baseline column in docs/reports/top-pages.md is deferred to project 6)
```

---

### 4d — Technical batch
*Run across all new pages before deploy.*

#### Agent Sequence

```
1. bsuk-accessibility-fixer
   → WCAG 2.1 AA: skip links, ARIA landmarks, form labels, alt text,
                  focus UK cities, color contrast, heading order, button types
   → Priority: Critical → High → Medium
   → Lighthouse verification after fixes

2. bsuk-performance-fixer
   → Measures dist/ with scripts/perf_audit.py (font-display, LCP fetchpriority + preload,
              render-blocking CSS, script defer); a fix goes into src/, never dist/
   → Target: Perf Score ≥90

3. bsuk-canonical-fixer  ← CRITICAL — NEVER SKIP
   → Verifies every built canonical is absolute (src/layouts/BaseLayout.astro emits it)
   → Checks og:url and JSON-LD url fields; a miss is fixed in src/, never dist/
   → Relative canonicals = all pages indexed as "/" = zero rankings

4. bsuk-footer-standardizer
   → Audits that every new page renders the kit footer, src/components/kit/SiteFooterKit.astro, through src/layouts/PageShell.astro
   → A page without it is fixed in its src/ page or layout, never in dist/

5. bsuk-contact-form-updater
   → Audits inquiry forms for canonical BSUK form markup
   → Checks: ARIA labels, accessibility violations, outdated markup

6. bsuk-google-map skill [location pages only] (the source repo's map agent: not ported — deferred to project 6)
   → Adds the Carlisle, Cumbria map embed (town-level, Known Issue 16)
   → Fixes CSP object-src blocker (embed → iframe)

7. bsuk-final-page-pass skill  ← THE FINAL GATE for every page type
   → python3 scripts/final_page_audit.py [--puppies]  (mechanical, over dist/)
   → TRIAGE every ✗: REAL / ACCEPTED / FALSE POSITIVE / NET-NEW (never report blind)
   → manual-auditor-check remains valid ONLY as the subjective companion checklist
     for interior pages; the source repo's interior audit is SUPERSEDED and was never ported
```

### Sprint 4 Gate
- [ ] One PASS / PASS-WITH-WARNINGS verdict from `scripts/final_page_audit.py`; every ✗ triaged
- [ ] All six heading levels present, no skipped levels; ≥5 H5/H6 advisory on homepage + location pages
- [ ] `python3 scripts/evidence_audit.py <slug>` → 0 ERROR; every WARN read and triaged
- [ ] **Title Case on every H1–H6**; FAQ `<summary>` stays sentence case
- [ ] **Header style declared + justified** at the outline gate (framework-heading-hierarchy §Header Style Selection)
- [ ] Lighthouse Performance ≥90 · Accessibility ≥90 — **judged on the DISTRIBUTION of ≥5 runs**, never one; CLS is bimodal on this site and one run already caused a confident wrong attribution
- [ ] All canonicals are absolute URLs
- [ ] Every new page renders the kit footer (`src/components/kit/SiteFooterKit.astro`)
- [ ] Inquiry form passes ARIA check
- [ ] Zero non-whitelist duplicate crossovers, body AND headers, vs every sibling

---

## Sprint 5 — Ship — inactive until project 6

> **This sprint does not run.** There is no git remote, no host and no domain: hosting is
> **NOT FETCHED** and project 6 owns the launch. `rules/deploy.md` is the pack; judgment
> rules 2–3 in `CLAUDE.md` are the standing instruction — commit on the project branch,
> **never push**. The guard that will let this sprint start is
> `BSUK_RELEASE=1 python3 scripts/placeholder_check.py` exiting 0; today it exits 1,
> because `SITE_URL_PLACEHOLDER` and `PHONE_PLACEHOLDER` are still in the build. The shape
> below is kept so project 6 inherits it rather than reinventing it.

```
1. [inactive] publish — the host is NOT FETCHED and is chosen in project 6

2. bsuk-deploy-verifier
   → Verifies: all new pages return HTTP 200
   → Verifies: canonical URLs are absolute
   → Submits: all changed URLs to IndexNow (`npm run indexnow:changed`), reading
     INDEXNOW_KEY and SITE_URL from the environment per docs/reference/credentials.md —
     never from a file in the repo. Today it exits 2: `BSUK_RELEASE=1` is unset, and the
     flag alone still refuses a placeholder SITE_URL
   → Output: docs/reports/YYYY-MM-DD-deploy-report.md

3. bsuk-redirect-manager [if any page slug changed]
   → Adds the 301 to data/redirects.json; scripts/redirect_check.py proves it
   → Detects + flattens redirect chains (A→B→C → A→C)
   → Validates all redirect targets exist on disk

4. sitemap-agent
   → Updates sitemap after any page change
   → Ensures all new pages are included
```

---

## Sprint 6 — Bank
*The step that makes the next page cheaper. Skipping it is why three of the 2026-07-28
lessons never reached the skill that enforces them.*

```
1. session-closer skill        → fill the brief's What's Next
2. Write the lessons doc       → a dated file under docs/superpowers/sessions/
3. BACK-PROPAGATE every lesson into the artifact that ENFORCES it:
     a render defect      → a check in scripts/page_hardening_scan.py + a RED test
     a gate that lied     → .claude/skills/bsuk-gate-integrity/SKILL.md
     a rule for everyone  → a pack in rules/ + a row in data/quality/rule-index.json
                            (a rule in no pack reaches no agent; the source repo's
                             injector scripts were not ported — source repo only)
     a component decision → a dated file under docs/superpowers/sessions/ ledger
     an anchor spent      → the Anchor Diversity Ledger
     a Reddit thread cited→ data/queries/raw/<slug>/threads.json (bsuk-reddit-threads skill)
     a live defect not fixed → a numbered Known Issue in docs/reference/session-log.md
4. SWEEP SIBLINGS for the same defect class
   (the infographic-crop bug was found on 4 OTHER live pages in one pass)
5. Memory: write/update the relevant memory file + its MEMORY.md pointer
```

### Sprint 6 Gate
- [ ] Every lesson in the doc maps to a named enforcing artifact, or is explicitly logged as backlog
- [ ] Siblings swept for the same defect class
- [ ] Any new rule is written in a `rules/` pack and registered in `data/quality/rule-index.json`, and `python3 scripts/quality_report.py` §5 does not list it as `untested`

---

## Continuous Loops

### Weekly (every Sunday)

| Agent | What it checks | Output |
|-------|---------------|--------|
| `@bsuk-rank-tracker` (inactive until project 6 — the agent's own notice) | Every competitor in `data/competitors.json` — new pages, pricing shifts, location pages, blog posts, keyword movement | Change report; auto-triggers competitor-intel for movers |
| `@bsuk-branded-search-monitor-agent` (not ported — deferred to project 6; needs GSC) | GSC CSV exports for branded queries ("bluestaffyuk", "blue staffy breeder") | Alert if >20% WoW drop; trust query triggers trust-signals-agent |
| `@bsuk-competitor-pricing-alert-agent` (not ported — deferred to project 6) | Top 5 competitors' puppy pricing via Playwright | Alert if any price changes >£200 |
| `@bsuk-llm-keyword-intel <slug>` | One engine per page — the ChatGPT scraper through the spend guard (a saved answer is reused) | docs/research/llm-intel/<slug>-[date].json: citations, citation gap, missing entities, answer format |

### Monthly

| Agent | What it checks | Output |
|-------|---------------|--------|
| `@bsuk-performance-monitor-agent` (not ported — deferred to project 6) | Lighthouse: homepage + 5 top pages | a dated session report under docs/superpowers/sessions/ |
| `@bsuk-gsc-analytics` | GSC CSV exports for CTR gaps, ranking opportunities | Updated docs/reports/top-pages.md (deferred to project 6) |
| `@bsuk-email-newsletter-agent` (not ported — deferred to project 6) | Manual trigger | a newsletter file (project 6) |

### Quarterly

| Agent | What it checks | Output |
|-------|---------------|--------|
| `@bsuk-competitive-keyword-gap-agent` | Competitor sitemaps + H1/H2/titles | docs/research/keyword-gap-[date].md |
| `@bsuk-directory-submission-agent` (not ported — deferred to project 6) | New puppy breeder directories | a directory list (project 6) |
| `@bsuk-nap-citation-agent` (not ported — deferred to project 6) | Name/Address/Phone across all directory listings | a dated session report under docs/superpowers/sessions/ |
| `@bsuk-funnel-analysis-agent` (not ported — deferred to project 6) | Full buyer funnel (Discovery → Conversion) | a dated session report under docs/superpowers/sessions/ |
| `@bsuk-backlink-outreach-agent` (not ported — deferred to project 6) | Resource pages + guest post opportunities + vet referrals | a backlink tracker (project 6) |

---

## Per-Event Triggers

Events that trigger agent chains regardless of schedule:

| Event | First Agent | Downstream Chain |
|-------|------------|-----------------|
| **New puppy available** | update `data/puppies.json` (breeder-confirmed only) | → rebuild → `bsuk-puppy-page-builder` skill (the puppy's page) → `bsuk-homepage-builder` (litter announcement) |
| **Puppy reserved** | update `data/puppies.json` | → rebuild → `bsuk-meta-description-agent` (update puppy count in meta) |
| **Puppy sold** | update `data/puppies.json` | → rebuild → retire or redirect the route via `data/redirects.json` and `python3 scripts/redirect_check.py` |
| **Competitor price change >£200** | `bsuk-competitor-pricing-alert-agent` (not ported — deferred to project 6) | → `bsuk-financial-strategist` (not ported — deferred to project 6) → `bsuk-meta-description-agent` |
| **Branded search drops >20%** | `bsuk-branded-search-monitor-agent` (not ported — deferred to project 6) | → `bsuk-trust-signals-agent` → `bsuk-non-commodity-content-agent` |
| **New inquiry received** | Manual trigger | → `bsuk-email-lead-nurture-agent` (not ported — deferred to project 6) (Day 0 template) |
| **New YouTube video published** | `bsuk-video-seo-agent` (not ported — deferred to project 6) | → `bsuk-external-link-agent` (not ported — deferred to project 6) |
| **New A/B test needed** | `bsuk-conversion-tracker` identifies CTA issue (not ported — deferred to project 6) | → `bsuk-heatmap-analyst-agent` → `bsuk-ab-test-agent` (both not ported — deferred to project 6) |

---

## Decision Tree — "Which agent do I call next?"

```
START: What are you trying to do?

├── "Start a new session / new page"
│   ├── Sprint 0 done? NO → @bsuk-competitor-registry → @bsuk-competitor-intel --all → --bsuk → scripts/gap_matrix.py --write first (@bsuk-gsc-analytics waits for project 6)
│   └── Sprint 0 done? YES → grill-me skill (with gap matrix loaded)
│       → SESSION CONTEXT → bsuk-content-audit-agent
│       → SECTION MAP + COMPONENT GATE → approved → build

├── "Don't know what to build next"
│   └── bsuk-competitive-keyword-gap-agent → sort by score ≥7 → bsuk-content-architect

├── "Build a location page"
│   └── Single: bsuk-location-builder [UK city]
│       Batch: bsuk-batch-rebuilder → reads data/locations.json → Agent per UK city

├── "Write page content"
│   └── Has bsuk-content-audit-agent been run? NO → run it first
│       → bsuk-angle-agent → bsuk-paa-agent
│       → Generic: bsuk-seo-content-writer
│       → Breeder-authentic: bsuk-non-commodity-content-agent
│       → FAQ: bsuk-faq-agent
│       → Sections: bsuk-section-builder

├── "Optimize a live page"
│   └── bsuk-keyword-verifier → bsuk-meta-description-agent → bsuk-trust-signals-agent

├── "Check site health"
│   └── bsuk-website-health skill → bsuk-perf-gate skill → bsuk-accessibility-fixer (the monitoring agent waits for project 6)

├── "Weekly monitoring"
│   └── bsuk-llm-keyword-intel per page; bsuk-rank-tracker is inactive until project 6, and the branded-search and pricing monitors wait for it too (not ported — deferred to project 6)

├── "Deploy a page"
│   └── bsuk-canonical-fixer → [Sprint 5 inactive until project 6] → bsuk-deploy-verifier → sitemap-agent

├── "A puppy was sold"
│   └── update data/puppies.json → rebuild → data/redirects.json + scripts/redirect_check.py (review collection: not ported — deferred to project 6)

└── "Something's wrong with conversions"
    └── bsuk-conversion-tracker → bsuk-heatmap-analyst-agent → bsuk-ab-test-agent (all three not ported — deferred to project 6)
```

---

## Data File Dependencies

Cut to the files that exist in `data/`. Everything the source repo's table listed that was
not ported is gone from this table rather than translated — a dependency row pointing at a
file nobody will create is worse than no row. `docs/reference/system-registry.md` has the
full `ls data/`.

| Data File | Writers | Key Readers | Update Cadence |
|-----------|---------|-------------|----------------|
| `data/locations.json` | Manual | location-builder, batch-rebuilder | New UK city |
| `data/puppies.json` | Manual (breeder-confirmed only) | puppy-page-builder, meta-description, trust-signals | When a puppy's status changes |
| `data/price-matrix.json` | Manual (breeder-confirmed only) | puppy-page-builder, interactive-component, meta-description | Price changes — locked today |
| `data/page-map.json` | `scripts/build_page_board.py` | content-architect, internal-link-agent, redirect-manager | Every build |
| `data/redirects.json` | redirect-manager | `scripts/redirect_check.py` | Slug changes |
| `data/image-manifest.json` | Manual | image-pipeline, the page builders | Image work |
| `data/image-centering.json` | Manual | image-pipeline | Image work |
| `data/component-ledger.json` | Manual | section-builder, the page builders | Component work (project 3) |
| `data/bsuk-ontology.json` | Manual | entity-agent, entity-graph | Entity work |
| `data/agent-registry.json` | `scripts/build_agent_registry.py` | the tier system below | On agent frontmatter change |
| `data/port-manifest.json` | Manual | `scripts/port_from_cag.py` | Project 2 only |
| `data/settings.json` | Manual | the build | Rare |
| `data/quality/rule-index.json` | Manual | `scripts/quality_report.py` | New or retired rule |
| `data/quality/evidence-budgets.json` | Manual | `scripts/evidence_audit.py` | Budget changes |
| `data/quality/evidence-ledger.json` | evidence-pass | `scripts/evidence_audit.py` | Per claim — empty today |
| `data/quality/rework-ledger.json` | learning-loop | `scripts/quality_report.py` | Per rework window — empty today |
| `data/boards/` | `scripts/build_page_board.py`, `scripts/board_approve.py` | `scripts/board_gate.py` | Per page board |

---

## Model Tier System

Every agent carries `model: inherit` — the session's model drives all of them, so a model release never requires editing the agent files again. The per-agent cost lever is `effort`, a **native** Claude Code frontmatter field (`low | medium | high | xhigh | max`). The single source of truth is `data/agent-registry.json`, which is GENERATED from the agents' own frontmatter by `python3 scripts/build_agent_registry.py` — the source repo's `apply_model_tiers.py` and `verify_model_tiers.sh` were not ported (not ported — source repo only), so the flow runs the other way here: edit the agent's frontmatter, then regenerate the registry.

| Tier | Model | Effort | Use For |
|---|---|---|---|
| `tier_max` | inherit | max | Orchestrators, deep creative, competitor intelligence, high-traffic builds |
| `tier_high` | inherit | high | Specialist page builders, narrative/schema content, SEO monitoring, analytics, conversion audits |
| `tier_medium` | inherit | medium | Technical audits + pure-mechanical utilities + data monitoring |

The count per tier is in `docs/reference/system-registry.md` (generated), never here.

Retired on 2026-09-07: the `<!-- EFFORT:START/END -->` prose directive (the native field replaced it), the `dynamic_workflow:` frontmatter key (not a recognized field — the flag lives in the registry only), and the `opus48_*` / `opus47_*` / `haiku_medium` tier names. `xhigh` is available and untested here; try it on the orchestrators and the audit chain and measure rework rate before adopting it.

**Dynamic routing:** the three orchestrators (`bsuk-content-architect`, `bsuk-structure-architect`, `bsuk-batch-rebuilder`) classify each task to a tier and dispatch with the `Agent` tool; the source repo's routing script was not ported, so the orchestrator classifies by hand against the tiers in `data/agent-registry.json`.

**To change an agent's effort:** the registry is GENERATED, so the flow runs the other way here — edit the agent's own frontmatter, then `python3 scripts/build_agent_registry.py` to regenerate `data/agent-registry.json`, then `python3 scripts/build_agent_registry.py --check` to prove it is not stale, then `python3 -m pytest tests/py -q` → commit. Never push: there is no remote until project 6.

---

## Non-Negotiable Rules (apply to all sprints)

1. **≥97% Confidence Gate** — Any agent writing to `src/pages/` must be ≥97% confident. If below: stop, UK city uncertainty, ask.
2. **Preview Before Apply** — Any page redesign MUST be previewed and approved before writing to site files.
3. **Same Content** — Redesigns never add or remove page content. Visual layer only.
4. **Licence Awareness** — Breeder-licence and statute claims are not established. Write `LICENCE_CLAIM_PLACEHOLDER` / `LEGAL_CLAIM_PLACEHOLDER` and let `scripts/placeholder_check.py` hold them (seo-rules Rule 7).
5. **src/pages is Deployed** — All page edits go to `src/pages/<slug>/index.astro`. The `dist/` directory is staging only.
6. **No Auto-Sends** — Email agents (lead-nurture, review-collection, newsletter) never auto-send. All templates require human review.
7. **Hub Before Spoke** — Always build hub pages before their spoke pages. Link equity flows correctly.
8. **Audit Before Build** — `bsuk-content-audit-agent` must run before any page rebuild.
9. **Canonical Before Deploy** — `bsuk-canonical-fixer` must run before every deploy. Relative canonicals = zero indexing.
10. **Data Files Are Truth** — Never fabricate data. All claims come from data files, real page fetches, or direct breeder input. GSC and GA4 are NOT FETCHED, so nothing may be sourced from them.
11. **Phone Number Policy (Rule 61)** — Phone number PHONE_PLACEHOLDER appears ONLY in the footer and schema markup. All body copy CTAs must link to `/contact-us/` form — never display or link a phone number in page body content.
12. **Image Rules Lookup Required** — Before any image generation or infographic work, read `rules/images.md` for the sizing and placement rules of the current page type, and `data/image-manifest.json` for the dimensions of the images that exist.

---

## Post-Deploy Verification Checklist — inactive until project 6

> Same notice as Sprint 5: there is no remote, no host and no domain, so none of this runs
> today. The shape is kept for project 6; the commands below are what it will run once a
> real origin replaces `SITE_URL_PLACEHOLDER`.

### 1. Check new/modified pages return 200
```bash
curl -sI "https://$SITE_URL/[new-slug]/" | grep "HTTP"
```
Expected: `HTTP/2 200`

### 2. Verify canonical is correct
```bash
curl -s "https://$SITE_URL/[new-slug]/" | grep -i "canonical"
```
Expected: an absolute URL matching the slug

### 3. Update the page board
`python3 scripts/build_page_board.py` regenerates `data/page-map.json` and the boards in
`data/boards/`; `python3 scripts/board_gate.py` is the gate. The source repo's
`page-inventory.md` was not ported (not ported — source repo only) — the board replaces it.

### 4. UK city pages
`data/locations.json` is generated and has no status field: a city page is live when its row
builds, and `npm run sitemaps` (the build's postbuild) lists it.

### If any URL returns 404 after deploy:
1. Check the page's own `index.astro` under `src/pages/` exists
2. Run `npx astro build` locally — check for build errors
3. Check `data/redirects.json` for a conflicting rule, then `python3 scripts/redirect_check.py`
4. Check `astro.config.mjs` for route configuration

### Slug Registry Rule (PREVENT FUTURE MISMATCHES)
Before building any new page, check `data/page-map.json` to confirm:
- The planned slug matches what will be linked to in navigation
- No existing page already covers this topic at a different URL
- If URLs will differ from what's linked, add a redirect BEFORE building the page
