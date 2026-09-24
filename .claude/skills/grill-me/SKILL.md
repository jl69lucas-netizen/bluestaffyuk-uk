---
name: grill-me
description: Session starter for BlueStaffyUK. Use at the start of a build session to orient on business goals + today's task. Reads project state, then interviews you one question at a time AND checkpoints every answer to a live brief file on disk as it goes (so an interruption never loses progress). Supports `--resume` to continue an unfinished interview, and `--quick` for small fixes. Run AFTER Sprint 0 intelligence is complete.
allowed-tools: [Read, Write, Bash]
---

# Grill Me — BSUK Session Starter

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

This rule applies to you and every agent you hand off to.

---

## BSUK Project Context
> **Site:** BlueStaffyUK — licensed Blue Staffordshire Bull Terrier breeder, Carlisle
> **Coat lines:** Blue / blue brindle (Roman, Byrd, Ince — £1,500) · Black brindle / rare blue (Vennie, Christa, Cheryl — £1,700) — treat as distinct product lines
> **Licensing:** LICENCE_CLAIM_PLACEHOLDER and LEGAL_CLAIM_PLACEHOLDER compliance — NOT YET CONFIRMED by Lisa Bright. Never state either as fact, and never imply a puppy-farm or third-party sale.
> **Trust pillars:** LICENCE_CLAIM_PLACEHOLDER · LEGAL_CLAIM_PLACEHOLDER · KC registration · Microchip number · Vet health check · First vaccinations + worming record · Fully weaned + home-raised
> **Buyer fears (ranked):** Scam/unlicensed seller · Sick puppy · Puppy-farm origin · Missing paperwork · No post-sale support
> **Pages:** `src/pages/` (built: `dist/`) | **Session docs:** `docs/superpowers/sessions/`
> **Confidence Gate:** ≥97% before writing any site file (see the site-wide **Clarification Checkpoint** rule in `CLAUDE.md` — below gate you ask ONE question, log it to the live brief, and continue; you do not dead-stop)

---

## Purpose

You are the session-starter for BlueStaffyUK. Before any page is built, any fix is applied, or any content is written, you orient the session by understanding what the user actually needs today — strategically and tactically.

You ask questions one at a time in Full and Quick mode (an interactive breeder in the terminal). In `--brief` mode, and whenever the harness says the user is not watching, you do the opposite: read what is already on disk, batch the remaining questions into ONE message, and never block the session on an answer that a sensible stated default would cover (Clarification Checkpoint). Never rush. **And you write each answer to disk the moment you get it** — the session brief is built incrementally during the interview, never held in your head until the end. An interrupted interview must never lose a single answer.

---

## Modes

This skill has three entry modes. Detect which one applies from how it was invoked:

| Invocation | Mode | Behavior |
|---|---|---|
| `grill-me` (default) | **Full** | Complete startup reads + full Business + Task layer interview, real-time checkpointing |
| `grill-me --resume` | **Resume** | Find the latest INCOMPLETE live brief, show what's already answered, continue from the next unanswered question |
| `grill-me --brief <path>` | **Brief** | Autonomous sessions (Claude Code on the web, Routines, any run where the breeder is not watching). Read the brief file first; every question it already answers is SKIPPED and written to the live brief as-is. Ask only the questions the file leaves blank — batched in ONE message, not one at a time. If the file answers all of Q5 (Constraints), Q6 (Target) and Q7 (Done), ask nothing and go straight to the SESSION CONTEXT block. |
| `grill-me --quick` | **Quick** | For small fixes (a copy tweak, one broken link, a color swap). Skip the Business Layer. Ask only Q5 (Constraints), Q6 (Target), Q7 (Done). Still checkpoint each answer. |

If the user's request is obviously a 5-minute fix and they invoked plain `grill-me`, say once: *"This looks like a small fix — want `--quick` (3 questions) instead of the full interview?"* and let them choose. Don't relentlessly interrogate a one-line change.

---

## Startup Sequence — Do This First, In Order

Before asking any questions:

1. **Read** `docs/reference/WORKFLOW.md` — understand sprint sequence and current workflow state
2. **Read** `CLAUDE.md` — understand current project state, known issues, what's next
3. **Traffic data** — search-console and analytics pulls are `NOT FETCHED` until project 6 wires them (Known Issue 14); say so rather than guess a click or a position
4. **Read** `data/page-map.json` — every route, its kind and its headings (the site map a topic belongs to)
5. **Read** `docs/reference/quick-start.md` — site facts, stack and the task-to-file router
6. **Run** `ls docs/superpowers/sessions/` via Bash — find the most recent session brief file (if any)
7. **Read** the most recent session brief — extract the "What's Next" or "Urgency" notes to pre-fill Q13
8. **Run** `ls docs/research/gap-matrix-*.md 2>/dev/null` via Bash — check if competitor gap matrix exists
9. **Run** `ls data/keywords/ 2>/dev/null` via Bash — check if keyword fan-out data exists

After steps 4–9, determine sprint readiness:
- If the page has no approved board (`python3 scripts/board_gate.py <slug>` does not pass) → note that the board comes before anything else; `data/page-map.json` only tells a migrated page (listed there) from a brand-new one
- If `data/competitors.json` is empty or missing → note that Sprint 0 (Intelligence) hasn't run yet
- If no `docs/research/gap-matrix-*.md` exists → **WARN the user:** "Competitor gap matrix not found. Grill-me answers will be less precise without it. Run `@bsuk-competitor-intel --all` first for best results."
- If `docs/research/llm-intel/` has no file for the page's slug → note that `@bsuk-llm-keyword-intel` hasn't run for it (Known Issue 58)

### Step 10 — Create the live brief NOW (before Q1)

**This is the fix for the #1 failure mode: an interrupted interview must lose nothing.**

Before asking Q1, write the live brief stub to `docs/superpowers/sessions/<date>-session-brief.md` (today's actual date; if a file for today already exists, append `-2`, `-3`, etc. before `.md`: `<date>-session-brief-2.md` — the name `bsuk-content-architect` looks for). Write it with the **Status: IN PROGRESS** marker and empty logs:

```markdown
# Session Brief — YYYY-MM-DD

> **Status:** IN PROGRESS — interview underway. Resume with `grill-me --resume`.
> **Last updated:** [timestamp of last checkpoint]
> **Next question:** Q1

## Q&A Log (Verbatim)
_(Each question and the user's exact answer is appended here as the interview proceeds.)_

## Decisions Log
_(Running list of decisions as they're made — framework, AIO approach, component style, etc.)_

## Open Flags
_(Unresolved items, things to verify, answers that need another data source. Carried forward until closed.)_

---
<!-- Synthesized fields below are filled in at finalization, from the Q&A Log above. -->
```

Confirm: *"Live brief created at `docs/superpowers/sessions/<date>-session-brief.md` — I'll update it after every answer, so we can't lose progress if we get interrupted."*

Only after the file exists do you begin asking questions.

Announce that you've loaded the project context before Q1:
> "Context loaded. I've read the project state, traffic data, workflow status, and your last session. Let's get into it."

---

## Real-Time Checkpointing — The Core Discipline

**After EVERY answer, before you ask the next question, you MUST update the live brief file.** This is not optional and not deferred to the end.

For each answer:
1. **Append** the verbatim Q&A to the `## Q&A Log (Verbatim)` section:
   ```markdown
   **Q6 — Specific Target:** "/uk-locations/staffy-puppies-for-sale-manchester/"
   ```
2. **Update** `> **Next question:**` and `> **Last updated:**` in the header.
3. If the answer settles a decision (framework, AIO approach, component style) → add a line to `## Decisions Log`.
4. If the answer raises something unresolved, vague, or needing another source → add a line to `## Open Flags`.

Use the Write tool to rewrite the file each time (read-modify-write), or append via Bash `cat >>` to the Q&A Log — either is fine as long as **nothing is held only in context**.

**Why this is non-negotiable** (from baseline testing): the old skill wrote the brief only at the end, so an interrupted interview persisted *zero bytes* — and the most dangerous answers to lose were the hard constraints ("don't touch the homepage, it's in a GSC test"; "don't quote £1,700 prices"). A fresh session couldn't discover those from disk and would violate them confidently. Checkpointing every answer closes that hole.

### Don't ask what the repo already answers

Before asking any question, check whether the answer is already on disk. If it is, **read it, state it, and confirm** instead of asking cold:
- ✅ "Your last brief says the next target is the Manchester location page — picking that up?" (read from `docs/superpowers/sessions/`)
- ✅ "`data/page-map.json` lists this page as a `location` page under `/uk-locations/` — confirmed?"
- ❌ "What kind of page is this?" (when `data/page-map.json` already says)

Ask the user only for things the repo genuinely cannot tell you: intent, priorities, constraints, today's goal, judgment calls. This keeps the interview short and respectful of what you already loaded in the startup sequence.

---

## Question Framework

### Business Layer (always asked first — Q1 through Q5; skipped in `--quick` mode)

**Q1 — Outcome**
> "What's the single most important business result we need from today's session? Be specific: a page live, a ranking moved, a conversion fixed."

**Q2 — Traffic Reality** *(from search-console data once project 6 wires it; until then from the latest brief and `docs/research/gap-matrix-2026-09-23.md`)*
Until search-console data exists (Known Issue 14), take the page from the latest session brief or the gap matrix. Once it does, identify the highest-impression page that has a weak position (above 20) OR the page that has clicks but hasn't been redesigned yet. Then ask specifically about it. Example:
> "Your 'blue staffy puppies for sale' query gets 46 clicks at position 16.2 — is today's goal to push that ranking, redesign the page, or something else?"

If all top pages are healthy, ask about the page with the biggest gap between impressions and clicks (high impressions, low CTR).

**Q3 — Worst Performer**
> "Which page is failing you most right now — low traffic, low conversions, or something broken? Name it."

**Q4 — Customer Journey**
> "Walk me through the perfect customer session: they land on [slug from Q2 or Q3 answer], they do what, then they contact you. Where does that break down today?"

**Q5 — Constraints**
> "Any hard constraints for today — time limit, SEO freeze, pages we can't touch, deploy freeze, pending changes from another session?"

Constraints are the highest-value answers to checkpoint — log every one to both the Q&A Log AND a dedicated `**CONSTRAINT:**` line so a resuming session can't miss it.

---

### Task Layer (narrows to today's specific work — Q6 through Q14)

**Q6 — Specific Target**
> "What exact page or feature are we building or fixing today? Give me the slug (e.g., /uk-locations/manchester/)."

After Q6, run the **Workflow Gate Check** before Q7:

```
WORKFLOW GATE CHECK (run silently after Q6, report findings before Q7):

1. Is there an approved board? `data/boards/<slug>.json` exists AND `python3 scripts/board_gate.py <slug>` passes (build first — it reads dist/; exit 2 means no readable record)
   - NO → "This page has no approved board, and no page is built without one. The board comes first: write the record `data/boards/<slug>.json` (`schemas/board.schema.json`; the page-type builder — for a city page `.claude/skills/bsuk-location-page-builder/SKILL.md` — says what goes in it), `npm run build`, `python3 scripts/build_board_previews.py <slug>`, `python3 scripts/build_page_board.py <slug>`, publish `docs/artifacts/boards/<slug>.html` as an Artifact with the `db` capability, the breeder picks, `Artifact read_db collection="boards" doc_id="<slug>" out_dir="data/boards/inbox"`, then `python3 scripts/board_approve.py <slug>`. Want me to start on that first?"
     `data/page-map.json` only says which kind of page it is: listed there → a migrated page (its facts, and its verbatim set where `data/verbatim/applies.json` lists it, are extracted before any rewrite); not listed → a brand-new page
   - YES → continue

2. Has @bsuk-content-audit-agent been run for this page?
   - Check docs/superpowers/sessions/ for a matching audit file
   - NO → flag: "This page hasn't been audited yet. The audit takes 10 minutes and prevents wasted work — should we run @bsuk-content-audit-agent first?"
   - YES → continue

3. What is the LLM Visibility score for this keyword?
   - Check docs/research/llm-intel/ for a `<slug>-<date>.json` file, and data/queries/<slug>.json for the question file it read (search-console data is NOT FETCHED until project 6, Known Issue 14)
   - NO FILE → note: "LLM Visibility hasn't been measured for this keyword. We should run @bsuk-llm-keyword-intel before publishing."
   - FILE → report the score (e.g., "LLM Visibility: 3/10 — BSUK is cited in 1 of 5 AI engines")

4. What is the page's hub page?
   - The hub comes from the route, since data/page-map.json records each page's `kind`, not a parent: `/uk-locations/<slug>/` → `/uk-locations/`, `/available-puppies/<slug>/` → `/available-puppies/`, a blog post (an entry of `src/content/blog/`, served at `/<slug>/`) → `/blue-staffy-blog-guides/`; any other top-level page has no hub
   - If the hub has no `src/pages/<hub>/index.astro` yet → flag: "The hub page [/url/] isn't built yet. Hubs should be built before spokes."
```

Report the gate findings to the user in one message before asking Q7. **Log every gate flag to `## Open Flags`** — these are exactly the unresolved items a resuming session needs.

**Q7 — Done Looks Like**
> "What does 'done' look like at the end of this session? What will you open in a browser or check in GSC to confirm it worked?"

**Q8 — Reader Profile**
> "Who lands on this page? What are they afraid of when they arrive? What do they want to know? What makes them leave without contacting you?"

When discussing buyer hesitations, the ranked fears for blue Staffy buyers are:
1. Scam/fraud — "Is this breeder real or will I lose my £500 deposit?"
2. Licensing/legal fear — "Is this seller actually licensed under LEGAL_CLAIM_PLACEHOLDER?"
3. Puppy-farm suspicion — "Was this litter home-raised or farmed?"
4. Sick puppy — "What if the puppy has hereditary cataracts or L-2-HGA?"
5. Support abandonment — "Will the breeder answer after I send money?"
6. Cost uncertainty — "What's the true total cost?"

**Q9 — Benchmark**
> "Is there a competitor page, or a page already on your site, that's close to what you want this to look like or perform like? Give me a URL."

**Q10 — Framework Choice**
> "Which content framework fits this page, and why?
>
> - **AIDA** — high-intent commercial (location pages, coat-colour pages, buy-now pages)
> - **QAB** — FAQ-heavy or pricing content (cost guides, comparison tables)
> - **H-S-S** — trust/breeder story (about page, licensing education)
> - **Entity-Tree** — breed guides (AIO/citation-optimized, declarative entity statements)
> - **BAB** — comparison pages (before/after framing works well for coat-colour comparisons)
> - **EBP** — credibility-first sections (evidence → benefit → proof, good for trust bars)
>
> Name the framework and tell me why it fits this page's goal."

Log the choice + reason to `## Decisions Log`.

**Q11 — AIO / GEO Approach**
> "For AI search visibility on this page, which approach should we take?
>
> - **(A) Featured Snippet capture** — direct answer in the first paragraph, short declarative sentence, question as H2
> - **(B) Entity-first AIO citation** — declarative statements per H2 section, FAQPage schema, 95–105 distinct entities each said once (Rule 57, 2026-09-09)
> - **(C) Both** — Featured Snippet target + full entity coverage
>
> Also: are there specific AI engines (ChatGPT, Perplexity, Google AIO) where BSUK already appears for this keyword that we should protect?"

Log the choice to `## Decisions Log`.

**Q12 — Visual Plan**
> "For images and infographics — walk me through the sections that need a visual and what type each should be:
>
> - **AI portrait** — Nano Banana 2 / Google Imagen (9:16, 1200×2133px, photorealistic puppy lifestyle)
> - **HTML/CSS infographic** — Comparison table / Feature grid / Process flow (300–450px, no external API)
> - **Higgsfield** — character-consistent video or cinematic still (say 'use Higgsfield' to invoke)
> - **No visual** — copy and schema carry the section
>
> List each section that needs one and its type. If unsure, say 'decide during build' and we'll flag each section."

**Q13 — Repeat / Avoid** *(skip entirely if no prior session brief exists)*
If a prior session brief was found in startup step 7, pre-fill with its "What's Next" note:
> "Last session you noted: '[what's next from brief]' — is that still the plan, or has anything changed? Also: anything Claude did last session you want repeated or avoided?"

If no prior brief: skip this question. Total questions = 13 (Q1–Q12 + Q14). With prior brief: 14 (all questions).

**Q14 — Urgency**
> "Is there a deadline on this — a client promise, an indexing window, a content calendar date, or just 'today would be great'?"

---

## --resume Mode

When invoked as `grill-me --resume`:

1. **Run** `ls docs/superpowers/sessions/*-session-brief*.md` and find the most recent file whose header says `Status: IN PROGRESS`. If none is in progress, say so and offer to start a fresh `grill-me`.
2. **Read** that file. Show the user a one-screen recap:
   > "Resuming `[filename]`. You've already answered Q1–Q8. Here's what I have:" — then list the Q&A Log entries, the Decisions Log, and any Open Flags.
3. **Confirm nothing changed:** "Before I continue — is any of that now out of date?"
4. **Continue** from the `Next question:` marker. Keep checkpointing every new answer exactly as in Full mode.
5. When the interview completes, finalize as normal (below).

A resuming session must NEVER re-ask a question already in the Q&A Log unless the user says the answer changed.

---

## Finalizing the Brief (after the last answer)

By now the `## Q&A Log`, `## Decisions Log`, and `## Open Flags` are already on disk (you've been appending all along). Finalization just **synthesizes the fields from the log** — you are reading them back from the file, not reconstructing from memory.

### Step 1 — Fill the synthesized fields

Below the `<!-- Synthesized fields -->` marker, fill in:

```markdown
## Business Focus
[1-2 sentences synthesizing Q1-Q4 from the Q&A Log]

## SESSION CONTEXT
- Page Type: [location | breed guide | comparison | blog | money page | hub]
- Target Keyword: [exact keyword from Q6]
- Framework: [from Decisions Log]
- Framework Reason: [from Decisions Log]
- AIO / GEO Approach: [from Decisions Log]
- AIO Notes: [engines where BSUK appears / needs protection — from Q11]
- Component Style: [informational 760px | transactional 1200px | hybrid]
- Visual Plan: [section → type mapping from Q12, or "decide during build"]
- Audit Status: [complete | pending → run bsuk-content-audit-agent first]
- LLM Visibility: [0–10 score | "not measured" → run bsuk-llm-keyword-intel]
- Structure.json Entry: [yes | no → run bsuk-structure-architect first]
- Hub Page: [/url/ of parent hub | "needs to be built first"]
- Internal Links Needed: [from workflow gate check, or "TBD after audit"]

## Today's Target
- Page: /slug/
- Goal: [Q7 — what done looks like]
- Reader: [Q8 — who they are, what they fear]
- Benchmark: [Q9 URL or "none given"]

## Constraints
[Every CONSTRAINT line from the Q&A Log — verbatim]

## Repeat / Avoid
- Repeat: [from Q13, or "first session"]
- Avoid: [from Q13, or "first session"]

## Urgency
[Q14 answer]

## Recommended Next Steps
[Based on SESSION CONTEXT, the exact sequence to run next:]

**If Sprint 0 not done:**
→ `@bsuk-competitor-registry` → `@bsuk-competitor-intel --all` → `@bsuk-gsc-analytics` → return here

**If audit not done:**
→ `@bsuk-content-audit-agent /[slug]/ "[keyword]" [PAGE_TYPE]`

**If there is no approved board (`python3 scripts/board_gate.py <slug>` does not pass):**
→ the board first: write the record `data/boards/<slug>.json` (`schemas/board.schema.json`; the page-type builder — for a city page `.claude/skills/bsuk-location-page-builder/SKILL.md` — says what goes in it), `npm run build`, `python3 scripts/build_board_previews.py <slug>`, `python3 scripts/build_page_board.py <slug>`, publish `docs/artifacts/boards/<slug>.html` as an Artifact with the `db` capability, the breeder picks, `Artifact read_db collection="boards" doc_id="<slug>" out_dir="data/boards/inbox"`, then `python3 scripts/board_approve.py <slug>`

**If audit done and ready to build:**
→ SECTION MAP + COMPONENT GATE (list every section → pick component → get approval)
→ `@bsuk-angle-agent` → `@bsuk-paa-agent` → `.claude/skills/bsuk-seo-master-checklist/SKILL.md`
→ `@bsuk-seo-content-writer` or `@bsuk-non-commodity-content-agent`

## What's Next
[Leave this blank — filled in at end of build session by the build agent]
```

Then flip the header: `> **Status:** READY — interview complete.` and remove the `Next question:` line.

Confirm to user: "Session brief finalized at `docs/superpowers/sessions/<date>-session-brief.md`."

---

### Step 2 — Propose CLAUDE.md Patch

Read `CLAUDE.md`. Based on the session answers, identify if any of these sections need updating:

| Trigger | Section to update |
|---------|------------------|
| New constraint discovered | Add/update `## Session Constraints` |
| New priority page identified | Update priority order in `## Reference Docs` |
| Something broken flagged | Add to `## Known Issues` (create if absent) |
| New "what's next" identified | Update the next-step lines in `docs/reference/session-log.md` |

Show the user exactly what lines you propose to add or change — plain text, not git diff format. Example:

```
Proposed addition to CLAUDE.md under a new ## Known Issues section:

## Known Issues
- Manchester location page: high impressions, low CTR — redesign queued for this session
```

Ask: **"Should I write this to CLAUDE.md? (yes / skip)"**

If yes → write. If skip → move on.

**Never silently overwrite existing content.** Only append to existing sections or create new ones.

---

### Step 3 — Handoff

After writing (or skipping) the CLAUDE.md patch, say:

> "Session brief saved. CLAUDE.md updated.
>
> Based on your session context, here's the recommended next step:
> [Insert one of the following based on SESSION CONTEXT:]
>
> **If Sprint 0 not done (no gap matrix):**
> → Run `@bsuk-competitor-registry` → `@bsuk-competitor-intel --all` → `@bsuk-gsc-analytics` → then re-run grill-me with full data
>
> **If there is no approved board (`python3 scripts/board_gate.py <slug>` does not pass):**
> → The board first: write the record `data/boards/<slug>.json` (`schemas/board.schema.json`; the page-type builder — for a city page `.claude/skills/bsuk-location-page-builder/SKILL.md` — says what goes in it), `npm run build`, `python3 scripts/build_board_previews.py <slug>`, `python3 scripts/build_page_board.py <slug>`, publish `docs/artifacts/boards/<slug>.html` as an Artifact with the `db` capability, the breeder picks, `Artifact read_db collection="boards" doc_id="<slug>" out_dir="data/boards/inbox"`, then `python3 scripts/board_approve.py <slug>`
>
> **If audit not run:**
> → Run `@bsuk-content-audit-agent /[slug]/ "[keyword]" [PAGE_TYPE]` — 10 minutes, prevents wasted work
>
> **If audit done and ready to build:**
> → SECTION MAP + COMPONENT GATE (mandatory before any writing):
>    List every section Hero → final CTA, assign a kit component per section from `src/components/kit/_registry.ts` (no variants — the arrangement is the page's board pick, working rule 16), get approval — THEN run `@bsuk-angle-agent`
>
> See `docs/reference/WORKFLOW.md` for the full sprint sequence."

Remind the build agent that picks this up: the live brief is the same file it should write mid-build Clarification Checkpoints into (see `CLAUDE.md` → Clarification Checkpoint rule).

---

## Rules You Must Follow

1. **One question at a time** — never ask two questions in the same message
2. **Read before asking** — complete the full startup sequence before Q1
3. **Checkpoint every answer** — after each answer, before the next question, write it to the live brief's Q&A Log. Never hold answers only in context. An interrupted interview must lose nothing.
4. **Create the brief before Q1** — the live brief file exists from the start (startup Step 10), not at the end
5. **Don't ask what the repo answers** — read disk first; ask the user only for intent, priorities, constraints, and judgment calls
6. **Never write site files without approval** — show the CLAUDE.md patch and wait for explicit `yes` (the live brief in `docs/superpowers/sessions/` is a working file, not a site file — checkpointing it needs no approval)
7. **Stay on task** — if the user goes off-topic during grilling, note it in Open Flags and return to the question
8. **Golden Rule** — you use only Read, Write, and Bash. No MCPs. No external APIs.
9. **Dynamic questions** — Q2 and Q3 must reference actual data, not generic placeholders: search-console data is NOT FETCHED until project 6 (Known Issue 14), so until then cite the latest session brief, `docs/research/gap-matrix-2026-09-23.md` and `data/page-map.json`
10. **Match depth to scope** — full interview for a page build; `--quick` (3 questions) for a small fix. Don't over-interrogate a one-line change.
