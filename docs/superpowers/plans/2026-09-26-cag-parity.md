# CAG Page-Brief Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the 27 gaps the CAG page-brief parity audit found, so that every project 5 page
(28 city pages, the comparison cluster, two blog posts) runs one ordered, command-backed
per-page workflow whose gates actually examine the page.

**Architecture:** Four waves, easiest first. Wave 1 fixes live defects and doc drift. Wave 2
makes the gates see project 5 pages (render targets, the zero-examined guard, Asset Gate in
`check:all`, retired-facts sweep, rendered-change list). Wave 3 adds the research and keyword
numbers (competitor metrics, ours-vs-top-5, geo token, claim ledger, NOT FETCHED lint, thread
ledger). Wave 4 is the per-page run: `docs/reference/page-run.md`, the board intake block,
`npm run gate:page`, the measurement ledger, and the URL-family decision. The run makes
`impeccable`, `frontend-design` and `superpowers:verification-before-completion` mandatory
(user rulings, 2026-09-26) and proves they ran with a per-page record.

**Tech Stack:** Astro 6.3.8 + Tailwind 4.3 (static), Python 3.9 scripts + pytest, Playwright
render harness (`tests/render/`), npm script chain `check:all`.

**Source documents:** audit `docs/reports/cag-brief-parity-audit.md`
(https://claude.ai/artifact/S5xqdrrgFmmgcWFuuoqTGN) · CAG brief
https://claude.ai/code/artifact/f63b8e4f-3bf0-43e7-af6e-7632255cdfe0 · answer-board batch
`2026-09-26-brief-parity-two-decisions-before-project-5` (Tasks 7 and 8).

---

## How this plan was verified

Four Opus plan writers each drafted one wave. Each writer ran its tasks in a private copy of
the repo in this order: saw the failing test, applied the code, saw it pass, then ran
`npm run -s build` and `npm run -s check:all` (both exit 0), and made one commit per task. The
code in each task is pasted mechanically from those verified files, not retyped.

The controller then replayed all 27 tasks' commits, in plan order, onto a clean copy of
`cag-parity` (worktree `BSUK-int`, branch `parity-int`). Seven conflicts came up, all resolved
as described under "Integration conflicts" below. On the integrated tree, `npm run -s build`
and `npm run -s check:all` exit 0 on two runs (the Asset Gate runs on all 12 rebuilt pages, 0 FAIL),
and the full pytest suite gives **5771 passed, 12 skipped, 1 xfailed, 0 failed on two runs** (base:
5209 passed). That is the number Task 28 Step 1 should reproduce.

## Execution notes — read before Task 1

1. **Branch and worktree.** Work in `/Users/apple/Downloads/BSUK-cag` on `cag-parity`. Commit
   after every task and never push. Every commit message ends with exactly
   `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`; subagents tend to substitute
   their own model name, so tell them.
2. **Subagent-driven.** Each task gets an Opus implementer, then a spec review, then a quality
   review. Implementers never start background agents and end their turn to "wait". They run
   everything in the foreground and reply only once the task is committed. Every status reply
   to the user shows the full progress table.
3. **Order is the task number.** Waves overlap on the same files. Tasks written against the
   base tree say "edit by pattern" where an earlier task may have moved lines; follow the
   pattern, not the line number.
4. **Adding a check to `check:all`** (Tasks 9, 12, 21, 22) must, in the same commit, update
   `package.json`, the `expected` list in `tests/py/test_package_scripts.py`, and the CLAUDE.md
   sentence "`check:all` chains … in that order". From Task 6 on,
   `tests/py/test_doc_drift.py` pins that sentence to `package.json`. Final chain order (19
   items): `check:parity`, `check:facts`, `check:links`, `check:verbatim`, `check:outline`,
   `check:redirects`, `check:schema`, `check:queries`, `check:competitors`, `check:gaps`,
   `check:barriers`, `check:threads`, `check:sitemaps`, `check:placeholders`,
   `check:retired`, `check:boards`, `check:workflow`, `check:markers`, `agents`.
5. **Generated files.** `docs/reference/system-registry.md` is generated. After any task that
   touches `GATES`, a script or an agent, run `python3 scripts/build_system_registry.py`, and
   never hand-merge it.
6. **Build before `check:all`.** From Task 12 on, `check:all` reads `dist/` (the Asset Gate's
   `min-h5-h6` falls back to the record tree on a stale build and fails 11 pages). Run
   `npm run -s build` first whenever `src/`, `data/*.json` or `data/boards/` changed.
7. **Render runs** need `PUBLIC_FORMSPREE_ID` in `.env` (otherwise Guard 2 fails
   `form-inquiry-contract`). If another worktree holds ports 4321/4322, set `RENDER_SITE_PORT`
   and `RENDER_FIXTURE_PORT`.
8. **The page render run is already red today, before this plan.**
   `uk-locations/blue-staffy-puppies-uk` fails `nav-jump-target-lands` (scorecards 09-19 and
   09-22). Tasks 11 and 14 do not fix it. Task 28 records it as a Known Issue for project 5's
   first city page. Do not "fix" it inside another task.
9. **Decision-gated tasks.** Tasks 7 and 8 start with Step 0: read the answer-board batch
   `2026-09-26-brief-parity-two-decisions-before-project-5`. If the batch is still open, do
   every other task first and ask the user once. Answer (a) is the path written in full; (b)
   is the short paragraph.
10. **Frozen pages.** The 12 pages in `BUILT_BEFORE_SYSTEM_GAPS` (`scripts/family_rules.py`)
    keep their contracts. New checks block only new (project 5) pages.
11. **Marker gate.** Never write the `cag-` prefix into `docs/reference/`, `CLAUDE.md`,
    `rules/` or skills; `check:markers` bans it. The audit report's own filename lives under
    `docs/reports/` and is not cited from those places.
12. **Tests that depend on git history.** A few pytest tests read old commits (for example
    `63a7b12`). They pass in the real worktree and fail in copies without history. Run the
    suite in `BSUK-cag`, never in a scratch copy.

## Integration conflicts (found by the controller's replay; resolve exactly like this)

| When | File | Conflict | Resolution |
|---|---|---|---|
| Task 9 | `CLAUDE.md` | Task 6 re-wrapped the "`check:all` chains" sentence | Keep Task 6's sentence and insert `` `check:retired` `` after `` `check:placeholders` ``, so the sentence matches `package.json` (note 4) |
| Task 12 | `CLAUDE.md` | Same sentence | Insert `` `check:boards` `` after `` `check:retired` `` |
| Task 18 | `docs/reference/system-registry.md` | Generated file | Regenerate (note 5) |
| Task 20 | `scripts/evidence_audit.py` | Task 2 added `LOCATIONS_PATH` and `CITY_TERM` where Task 20 adds `REBUILT_PATH` | Keep all three constants |
| Task 21 | `package.json`, `tests/py/test_package_scripts.py`, `CLAUDE.md`, registry | Task 21's anchors predate Tasks 9 and 12 | Insert `check:barriers` after `check:gaps` in the current chain, list and sentence; regenerate the registry |
| Task 22 | same four files | Same | Insert `check:threads` after `check:barriers` |
| Tasks 24–27 | registry | Written against a stand-in registry | Apply the task and regenerate the registry |

Three defects surfaced only when all 27 tasks ran together. They are already folded into the task
text below:

| Found by | Defect | Fix now in the plan |
|---|---|---|
| Full pytest, twice | `test_doc_drift` needed "in that order" on one line; a harmless re-wrap broke it | Task 6's regex is `in\s+that\s+order` |
| Full pytest, twice | Task 16's skill text cited the git-ignored `docs/reports/rendered-changes.json`, which does not exist in a fresh checkout (the dead-path guard fails it) | Task 16 names the script that writes the report instead |
| `rendered_changes.py` dry run | Hashing raw bytes marked all 51 pages "changed", because Task 8's CSS is inlined into every page, so IndexNow would get the whole site | Task 16 hashes content: inline styles, non-JSON-LD scripts and `/_astro/` links are stripped; the replay then reports exactly the 12 rebuilt pages |


---

## Wave 1 — Fix and clean up (Tasks 1–8)

### Task 1: Remove the invented method label; add it to the residue lint

**Closes:** audit D1 (CAG §1e, Appendix A row 1e)

BSUK has no named house method: Lisa Bright never gave one, `CLAUDE.md` rule 9 forbids inventing a credential, and `scripts/aeo_audit.py:48-51` already keeps `LABELED_METHODS = []`. The port left one invented label ("The Carlisle Socialization Method") and the requirement for "two approved labels" in the AEO pass and the entity graph, a second invented label ("the BSUK Home-Raised Method") in the manual auditor, a stale `house_method` WARN in the final-page pass, and the Sprint 3 gate checkbox in WORKFLOW. This task deletes every one and adds a lint over the whole instruction tree (agents, skills, `docs/reference/`, `rules/`, `CLAUDE.md`).

**Files:**
- Modify: `tests/py/test_agent_facts.py` (append after the last line, 569)
- Modify: `.claude/skills/bsuk-aeo-pass/SKILL.md` (line 3; lines 134–150, §6a; line 197; line 210)
- Modify: `.claude/skills/bsuk-entity-graph/SKILL.md` (line 72; lines 157–160, §3d)
- Modify: `.claude/skills/bsuk-evidence-pass/SKILL.md` (line 56, one sentence)
- Modify: `.claude/skills/bsuk-final-page-pass/SKILL.md` (lines 69, 157, 194)
- Modify: `.claude/skills/manual-auditor-check/SKILL.md` (lines 52, 91)
- Modify: `docs/reference/WORKFLOW.md` (lines 496, 503)
- Test: `tests/py/test_agent_facts.py`

- [ ] **Step 1: Write the failing test** — append to `tests/py/test_agent_facts.py`:
```python
# ── an invented house-method label (CAG parity audit D1, 2026-09-26) ─────
# BSUK has no named house method: Lisa Bright has never given one, CLAUDE.md rule 9 forbids
# inventing a credential, and scripts/aeo_audit.py keeps LABELED_METHODS empty. The source
# repo's rule 12 required two "brand-owned method labels", and the port left one invented
# label ("The Carlisle Socialization Method"), a second invented one in the manual auditor
# ("the BSUK Home-Raised Method") and the requirement itself in the AEO pass, the entity
# graph and the Sprint 3 gate of WORKFLOW.md. An agent that follows any of them prints a
# made-up credential on every page it builds. This lint reads the whole instruction tree:
# agents, skills, the reference docs, the rule packs and CLAUDE.md.
METHOD_LABEL = re.compile(
    r"(?i:\bsociali[sz]ation method\b|\bhome-raised method\b|\bapproved method (?:labels?|names?)\b"
    r"|\bapproved labels?\b|\bbrand-owned method (?:labels?|names?|nodes?)\b)"
    r"|\b(?:Carlisle|BSUK|BlueStaffyUK|Lisa Bright|Bright)\b[^|\n]{0,30}?\bMethod\b")


def method_label_targets():
    return targets() + sorted((ROOT / "rules").glob("*.md")) + [ROOT / "CLAUDE.md"]


def method_labels(path: pathlib.Path):
    return ["%s:%d  %s" % (path.name, n, line.strip()[:110])
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
            if METHOD_LABEL.search(line)]


@pytest.mark.parametrize("path", method_label_targets(), ids=lambda p: p.parent.name + "/" + p.name)
def test_no_instruction_file_names_or_requires_a_house_method(path):
    bad = method_labels(path)
    assert bad == [], (
        "BSUK has no named house method — the breeder has never given one and CLAUDE.md rule 9 "
        "forbids inventing it. Delete the label and any line that requires one; if the breeder "
        "names a method, it goes in scripts/aeo_audit.py LABELED_METHODS first:\n  "
        + "\n  ".join(bad))


def test_the_method_label_lint_actually_fires(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(
        "| **The Carlisle Socialization Method** | family handling |\n"
        "Named house method (\"the BSUK Home-Raised Method\") used where home-rearing is discussed\n"
        "- [ ] One of the two approved method labels present and defined\n"
        "| 6a Labeled | one of the two approved method names present | yes |\n"
        "are first-class entities and the only two approved labels.\n"
        "  → WARN:  no binomial · no breeder-name entity · no brand-owned method label\n"
        "Lisa Bright's Puppy Method is taught on every page.\n"
        # silent: a named framework, a research step, and the rule that forbids a label
        "**Two-Keyword Header Method (apply to every header):**\n"
        "### 3. Tiered Sprint 0.5 Research Method + 17-Field Output Format\n"
        "BSUK has no named house method; never invent one.\n", encoding="utf-8")
    assert [b.split("  ")[0] for b in method_labels(p)] == [
        "SKILL.md:%d" % n for n in range(1, 8)]
```

- [ ] **Step 2: Run it and confirm it fails**
Run: `python3 -m pytest tests/py/test_agent_facts.py -q -k method`
Expected: FAIL — `5 failed, 117 passed, 295 deselected`. The five failing ids are `test_no_instruction_file_names_or_requires_a_house_method[bsuk-aeo-pass/SKILL.md]`, `[bsuk-entity-graph/SKILL.md]`, `[bsuk-evidence-pass/SKILL.md]`, `[manual-auditor-check/SKILL.md]` and `[reference/WORKFLOW.md]`; `test_the_method_label_lint_actually_fires` passes.

- [ ] **Step 3: Implement — delete the label and every line that requires one**

`.claude/skills/bsuk-aeo-pass/SKILL.md` line 3 (the `description:` frontmatter), replace the fragment:

Old: `checking freshness signals, brand-owned method names, BLUF openers`
New: `checking freshness signals, BLUF openers`

Same file, lines 134–150. Old:
```markdown
### 6a. Label the method, so the expertise stays ours

Unlabeled expertise gets absorbed as generic knowledge. **Approved by the breeder
2026-07-30 — two labels, used for different things:**

| Label | Covers |
|---|---|
| **The NOT FETCHED — the breeder has not named a house method** | weaning schedule, the weeks with the mother and the litter, the eight-week earliest go-home age — the *raising* process |
| **The Carlisle Socialization Method** | family handling, out-of-crate routine, noise/handling desensitisation — the *socialization* side |

Use them as proper nouns, capitalised, at least once per relevant page, and define
them once where first used. Before 2026-07-30 there were **zero instances site-wide**,
across 108 pages, 61 skills and 68 agents — so every page's raising process read as
generic advice any competitor could claim.

Keep them honest: they name a real process, they are not a certification. Never imply
third-party accreditation.
```
New:
```markdown
### 6a. No named house method — describe the process, never label it

BSUK has **no named house method**. Lisa Bright has never given one, and `CLAUDE.md`
rule 9 forbids inventing a credential, so no page may carry a capitalised method name
for the raising or the socialisation process. `scripts/aeo_audit.py` keeps
`LABELED_METHODS` empty for that reason, and `tests/py/test_agent_facts.py` fails any
instruction file that names or requires one.

Make the expertise ours the honest way: say what Lisa does, in the first person, with
the facts on file — the weeks with the mother and the litter, the eight-week earliest
go-home age (`data/faq.json` `buying-best-age`), family handling at home. If the breeder
ever names a method, it is added to `LABELED_METHODS` first, and only then written.
```

Same file, line 197. Old:
```markdown
| 6a Labeled | one of the two approved method names present | yes |
```
New:
```markdown
| 6a No label | no invented method name on the page | yes (`LABELED_METHODS` stays empty) |
```

Same file, line 210. Old:
```markdown
- **Inventing a third method name.** Two are approved. Adding more dilutes both.
```
New:
```markdown
- **Inventing a method name.** There is none on file. A name the breeder never gave is a
  made-up credential that an answer engine repeats as fact.
```

`.claude/skills/bsuk-entity-graph/SKILL.md` line 72. Old:
```markdown
| **Method** | The NOT FETCHED — the breeder has not named a house method · The Carlisle Socialization Method |
```
New:
```markdown
| **Method** | none on file — the breeder has not named a house method, so no Method node is asserted |
```

Same file, lines 157–160. Old:
```markdown
**3d. Brand-owned method nodes.** `The NOT FETCHED — the breeder has not named a house method` and `The Carlisle
Socialization Method` are first-class entities and the only two approved labels. A page
that teaches our method without naming it shows an unowned Method node — a finding, since
answer engines then absorb the expertise as generic knowledge.
```
New:
```markdown
**3d. No Method node.** BSUK has no named house method (the breeder has never given one,
and `scripts/aeo_audit.py` keeps `LABELED_METHODS` empty). A page that describes how Lisa
raises the litter asserts `RAISED_BY` and `LOCATED_IN` triples, never a named Method entity;
a capitalised method name on a page is a finding, because it is a credential nobody made.
```

`.claude/skills/bsuk-evidence-pass/SKILL.md` line 56 (inside the long table row), replace the sentence:

Old: `Brand-owned method labels are NOT FETCHED — the breeder has not named a house method, so none may be written.`
New: `The breeder has not named a house method, so none may be written.`

`.claude/skills/manual-auditor-check/SKILL.md` line 52. Old:
```markdown
6. **Brand-protocol naming** — the named house method ("the BSUK Home-Raised Method") used where home-rearing is discussed.
```
New:
```markdown
6. **No invented method name** — home-rearing is described in the first person with the facts on file; no capitalised house-method name appears (the breeder has never given one).
```
Same file, line 91. Old:
```markdown
[ ] Named house method ("the BSUK Home-Raised Method") used where home-rearing is discussed
```
New:
```markdown
[ ] No invented house-method name; home-rearing described in the first person, from facts on file
```

`.claude/skills/bsuk-final-page-pass/SKILL.md` line 69. Old:
```markdown
| `house_method` | **WARN** — flag until breeder confirms a term; `CLAUDE.md` rule 9 forbids inventing a house-method name |
```
New:
```markdown
| `house_method` | **none** — the check was deleted (no house method is on file); `CLAUDE.md` rule 9 forbids inventing a house-method name |
```
Same file, line 157. Old:
```markdown
[ ] A named house method is used ONLY once the breeder confirms one — never invented (WARN until then)
```
New:
```markdown
[ ] No house-method name on the page — none is on file, and one is never invented
```
Same file, line 194. Old:
```markdown
- **House-method name** (WARN on all pages until confirmed) — upgrade check from WARN to enforced only after the breeder supplies a confirmed term for inclusion in `data/quality/evidence-ledger.json`.
```
New:
```markdown
- **House-method name** — none is on file. If the breeder supplies one, add it to `LABELED_METHODS` in `scripts/aeo_audit.py` before any page names it.
```

`docs/reference/WORKFLOW.md` line 496. Old:
```
  → WARN:  no binomial · no breeder-name entity · no brand-owned method label
```
New:
```
  → WARN:  no binomial · no breeder-name entity
```
Same file, line 503. Old:
```markdown
- [ ] One of the two approved method labels present and defined
```
New:
```markdown
- [ ] No invented house-method name on the page (the breeder has never given one)
```

- [ ] **Step 4: Run it and confirm it passes**
Run: `python3 -m pytest tests/py/test_agent_facts.py -q` → Expected: `417 passed`
Run: `python3 -m pytest tests/py/test_rules_index.py tests/py/test_skills_frontmatter.py tests/py/test_builder_skills.py tests/py/test_aeo_audit.py tests/py/test_final_page_audit.py tests/py/test_agent_residue.py tests/py/test_workflow_ref_check.py -q` → Expected: `1182 passed`

- [ ] **Step 5: Run the gates**
Run: `npm run -s check:all; echo exit=$?` → Expected: last lines `examined 276 files; 0 problems` / `examined 41 agents; 0 problems` and `exit=0`

- [ ] **Step 6: Commit**
```bash
git add tests/py/test_agent_facts.py .claude/skills/bsuk-aeo-pass/SKILL.md .claude/skills/bsuk-entity-graph/SKILL.md .claude/skills/bsuk-evidence-pass/SKILL.md .claude/skills/bsuk-final-page-pass/SKILL.md .claude/skills/manual-auditor-check/SKILL.md docs/reference/WORKFLOW.md
git commit -m "fix: delete the invented house-method labels and lint the instruction tree for them

BSUK has no named house method (CLAUDE.md rule 9; aeo_audit LABELED_METHODS is empty).
The AEO pass, the entity graph, the manual auditor and WORKFLOW Sprint 3 still required
or named one. CAG parity audit D1.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Evidence budgets: city term per slug + brand budget

**Closes:** audit D2 (CAG §8.2, §8.4, Appendix B rows 8.2 and 8.4)

`data/quality/evidence-budgets.json:20` hard-codes the city term to `glasgow` — the city the breeder has left (Known Issue 16) — so 27 of the 28 city pages have no ceiling on their own city, and the brand has no ceiling anywhere. The fix: one `city` term whose pattern is the literal `{city}`, which `scripts/evidence_audit.py` resolves per slug from `data/locations.json`, budgeted on `location` pages only (8, as the Glasgow row was); and a `bluestaffyuk` term on every page type. The four built pages already over the new brand ceiling get a `budgets_by_slug` entry at their count as built (the Known Issue 34 ratchet), so no frozen page starts failing.

Brand ceilings (CAG §8.4 says 5–10 per page): home 10, for-sale 10, puppy 5, comparison 8, location 10, interior 10, blog 8, hub 5. As built on 2026-09-26: `index` 19, `buy-staffy-puppies-for-sale-uk` 56, `blue-staffy-uk-breeders` 11, `uk-blue-staffy-puppy-buying-guide` 11 — every other built page is at or under its ceiling.

**Files:**
- Create: `tests/py/test_evidence_city_budget.py`
- Modify: `scripts/evidence_audit.py` (imports, lines 33–34; constants after line 43; new helpers before `term_budget` at line 65; pattern resolution inside `term_budget`, lines 84–85)
- Modify: `data/quality/evidence-budgets.json` (`_comment` line 2; `terms` lines 15–22; every `budgets` map, lines 23–88; four `budgets_by_slug` entries: `index`, `buy-staffy-puppies-for-sale-uk`, `blue-staffy-uk-breeders`, `uk-blue-staffy-puppy-buying-guide`)
- Test: `tests/py/test_evidence_city_budget.py`

- [ ] **Step 1: Write the failing test** — `tests/py/test_evidence_city_budget.py`:
```python
"""The city term is the page's own city, and the brand has a ceiling (CAG parity audit D2).

data/quality/evidence-budgets.json hard-coded its city term to `glasgow` — the city the
breeder has LEFT (Known Issue 16) — so 27 of the 28 city pages in data/locations.json had no
ceiling on their own city, and `bluestaffyuk` had no ceiling anywhere. CAG §8 counts the
city 5–8 times on a location page and the brand 5–10 times on any page. The fix is one
`{city}` term that scripts/evidence_audit.py resolves per slug from data/locations.json,
and a `bluestaffyuk` term budgeted on every page type.
"""
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_audit as ea  # noqa: E402

LIVE = json.loads((ROOT / "data/quality/evidence-budgets.json").read_text(encoding="utf-8"))
LOCATIONS = json.loads((ROOT / "data/locations.json").read_text(encoding="utf-8"))


def page(body):
    return f"<html><head><title>t</title></head><body><main>{body}</main></body></html>"


def budgets():
    """The live file's shape, cut down to the two terms under test."""
    return {"terms": {"city": LIVE["terms"]["city"], "bluestaffyuk": LIVE["terms"]["bluestaffyuk"]},
            "budgets": {"location": {"city": 8, "bluestaffyuk": 10},
                        "interior": {"bluestaffyuk": 10}},
            "budgets_by_slug": {}}


def test_the_live_budgets_name_no_former_city():
    assert "glasgow" not in LIVE["terms"]
    for page_type, caps in LIVE["budgets"].items():
        assert "glasgow" not in caps, page_type


def test_the_city_term_is_resolved_per_slug_and_capped_on_location_pages():
    assert LIVE["terms"]["city"] == "{city}"
    assert LIVE["budgets"]["location"]["city"] == 8


def test_every_page_type_budgets_the_brand():
    assert re.fullmatch(LIVE["terms"]["bluestaffyuk"], "BlueStaffyUK", re.I)
    missing = [t for t, caps in LIVE["budgets"].items() if "bluestaffyuk" not in caps]
    assert missing == [], f"page types with no brand ceiling: {missing}"


def test_a_city_page_over_its_own_city_budget_fails():
    html = page("<p>" + "Aberdeen families. " * 9 + "</p>")
    over = ea.term_budget(html, "location", budgets(), slug="uk-locations/blue-staffy-puppies-aberdeen")
    assert over == [("city", 9, 8)]


def test_another_citys_name_is_not_this_pages_city():
    html = page("<p>" + "Aberdeen families. " * 9 + "</p>")
    assert ea.term_budget(html, "location", budgets(), slug="uk-locations/blue-staffy-puppies-dundee") == []


def test_a_hyphenated_city_matches_its_spaced_spelling():
    html = page("<p>" + "Newcastle under Lyme buyers. " * 9 + "</p>")
    over = ea.term_budget(html, "location", budgets(), slug="uk-locations/blue-staffies-newcastle-under-lyme")
    assert over == [("city", 9, 8)]


def test_a_bracketed_note_is_not_part_of_the_city():
    assert ea.city_for("uk-locations/staffy-breeding-dogs-glasgow") == "Glasgow"


def test_a_national_row_has_no_city_term():
    # `city: "UK"` rows are the country; the `uk` head term already budgets that word
    assert ea.city_for("uk-locations/blue-staffy-puppies-uk") is None
    html = page("<p>" + "UK buyers. " * 20 + "</p>")
    assert ea.term_budget(html, "location", budgets(), slug="uk-locations/blue-staffy-puppies-uk") == []


def test_a_page_outside_the_city_cluster_has_no_city_term():
    assert ea.city_for("index") is None
    assert ea.city_for("uk-locations") is None


def test_every_location_row_resolves_to_a_city_or_is_national():
    for row in LOCATIONS:
        city = ea.city_for("uk-locations/" + row["slug"])
        assert city is None or city in row["city"], row["slug"]
        if row["city"] != "UK":
            assert city, row["slug"]


def test_the_brand_is_capped():
    html = page("<p>" + "BlueStaffyUK raises them. " * 11 + "</p>")
    assert ea.term_budget(html, "interior", budgets(), slug="some-new-page") == [("bluestaffyuk", 11, 10)]


BUILT = json.loads((ROOT / "data/facts/rebuilt.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("slug", BUILT)
def test_the_twelve_built_pages_pass_their_brand_budget_as_built(slug):
    """The brand term is new, so each built page is held at its count AS BUILT through a
    budgets_by_slug override (the Known Issue 34 ratchet), never failed retroactively."""
    built = ROOT / "dist" / ("index.html" if slug == "index" else f"{slug}/index.html")
    if not built.exists():
        pytest.skip("run npm run build first")
    html = built.read_text(encoding="utf-8")
    over = [t for t, n, c in ea.term_budget(html, ea.page_type_for(slug), LIVE, slug) if t == "bluestaffyuk"]
    assert over == [], slug
```

- [ ] **Step 2: Run it and confirm it fails**
Run: `npm run -s build >/dev/null && python3 -m pytest tests/py/test_evidence_city_budget.py -q`
Expected: FAIL — `11 failed, 12 passed`. The 11 fail with `KeyError: 'city'` (the live file has no `city` term) or `AttributeError: module 'evidence_audit' has no attribute 'city_for'`; the 12 `test_the_twelve_built_pages_pass_their_brand_budget_as_built[...]` cases pass (there is no brand term yet).

- [ ] **Step 3: Implement the per-slug city in `scripts/evidence_audit.py`**

Old (lines 33–34):
```python
import re, sys, json, pathlib, argparse
from collections import defaultdict
```
New:
```python
import re, sys, json, pathlib, argparse
from collections import defaultdict
from functools import lru_cache
```

Old (line 43):
```python
TARGETS_PATH = ROOT / "tests" / "render" / "targets.json"
```
New:
```python
TARGETS_PATH = ROOT / "tests" / "render" / "targets.json"
LOCATIONS_PATH = ROOT / "data" / "locations.json"
# The `{city}` term (data/quality/evidence-budgets.json) is the page's OWN city, resolved per
# slug: a Glasgow-only city term left 27 of the 28 city pages with no ceiling at all.
CITY_TERM = "{city}"
```

Old (lines 64–65):
```python
# ── term-budget-per-page ────────────────────────────────────────────────────
def term_budget(html, page_type, budgets, slug=""):
```
New:
```python
# ── term-budget-per-page ────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _location_cities():
    """{location slug: city} from data/locations.json; empty when the file is absent."""
    if not LOCATIONS_PATH.exists():
        return {}
    return {r["slug"]: r["city"] for r in json.loads(LOCATIONS_PATH.read_text(encoding="utf-8"))}


def city_for(slug):
    """The city a `uk-locations/<slug>` page is about, or None.

    A bracketed note is not part of the name (`Glasgow (breeding dogs)` is Glasgow), and a
    national row (`city` "UK") has no city term: the `uk` head term already budgets that word.
    Any page outside the city cluster has no city term either."""
    if not slug.startswith("uk-locations/"):
        return None
    city = _location_cities().get(slug.split("/", 1)[1])
    if not city:
        return None
    city = re.sub(r"\s*\(.*?\)\s*", " ", city).strip()
    return None if city.upper() == "UK" else city


def city_pattern(city):
    """`Newcastle-under-Lyme` also matches `Newcastle under Lyme`: any run of spaces or
    hyphens in the name matches any run of spaces or hyphens on the page."""
    words = [w for w in re.split(r"[\s-]+", city) if w]
    return r"\b" + r"[\s-]+".join(re.escape(w) for w in words) + r"\b"


def term_budget(html, page_type, budgets, slug=""):
```

Old (inside `term_budget`, lines 84–85):
```python
        pat = budgets["terms"].get(term, re.escape(term))
        n = len(re.findall(pat, text, flags=re.I))
```
New:
```python
        pat = budgets["terms"].get(term, re.escape(term))
        if pat == CITY_TERM:
            city = city_for(slug)
            if city is None:
                continue
            pat = city_pattern(city)
        n = len(re.findall(pat, text, flags=re.I))
```

- [ ] **Step 4: Rewrite the budgets file** — run this once from the repo root (the file round-trips byte-for-byte through `json.dumps(indent=2, ensure_ascii=False)`, so only the changed keys move):
```bash
python3 - <<'EOF'
import json
p = "data/quality/evidence-budgets.json"
b = json.load(open(p, encoding="utf-8"))
b["_comment"] = b["_comment"].replace(
    "Terms are BSUK's six head terms; the caps are proportional to the CAG originals, not measured.",
    "Terms are BSUK's five head terms, the page's own city and the brand; the caps are proportional to the CAG originals, not measured. `city` is the literal `{city}`: scripts/evidence_audit.py resolves it per slug to the row's `city` in data/locations.json (a bracketed note dropped, a national `UK` row skipped), so it budgets location pages only. `bluestaffyuk` is the brand written as one word; `Blue Staffy UK` with spaces is counted by the `blue staffy` and `uk` head terms.")
terms = {}
for k, v in b["terms"].items():
    if k == "glasgow":
        terms["city"] = "{city}"
    else:
        terms[k] = v
terms["bluestaffyuk"] = "\\bbluestaffyuk\\b"
b["terms"] = terms
BRAND = {"home": 10, "for-sale": 10, "puppy": 5, "comparison": 8, "location": 10,
         "interior": 10, "blog": 8, "hub": 5}
for pt, caps in b["budgets"].items():
    new = {}
    for k, v in caps.items():
        if k == "glasgow":
            if pt == "location":
                new["city"] = 8
            continue
        new[k] = v
    new["bluestaffyuk"] = BRAND[pt]
    b["budgets"][pt] = new
AS_BUILT = {"index": (19, "home"), "buy-staffy-puppies-for-sale-uk": (56, "for-sale"),
            "blue-staffy-uk-breeders": (11, "interior"),
            "uk-blue-staffy-puppy-buying-guide": (11, "interior")}
for slug, (n, pt) in AS_BUILT.items():
    row = b["budgets_by_slug"][slug]
    row["_why"] += (f" `bluestaffyuk` (added 2026-09-26, CAG parity audit D2) {n} as built, over the "
                    f"{pt} ceiling {BRAND[pt]}; budget {n} = as built, so the new term ratchets this page "
                    "rather than failing it retroactively.")
    row["bluestaffyuk"] = n
open(p, "w", encoding="utf-8").write(json.dumps(b, indent=2, ensure_ascii=False) + "\n")
EOF
```
Check the result: `git diff --stat data/quality/evidence-budgets.json` → `1 file changed, 33 insertions(+), 27 deletions(-)`; `grep -c glasgow data/quality/evidence-budgets.json` → only the slug keys in `title_max_chars_by_slug` remain (2).

- [ ] **Step 5: Run it and confirm it passes**
Run: `python3 -m pytest tests/py/test_evidence_city_budget.py -q` → Expected: `23 passed`
Run: `python3 -m pytest tests/py/test_evidence_audit.py tests/py/test_evidence_per_slug_overrides.py tests/py/test_rules_index.py -q` → Expected: all pass (0 failed)
Run: `python3 scripts/evidence_audit.py $(python3 -c "import json;print(' '.join(json.load(open('data/facts/rebuilt.json'))))") | tail -1` → Expected: `examined 12 pages; 0 problems (48 WARN)` — the twelve built pages are unchanged. (`--all` now reports `city xN, ceiling 8 for location` on the migrated city pages such as Aberdeen, Dundee and York: that is the point, and project 5 rewrites them.)

- [ ] **Step 6: Run the gates**
Run: `npm run -s check:all; echo exit=$?` → Expected: `exit=0`

- [ ] **Step 7: Commit**
```bash
git add scripts/evidence_audit.py data/quality/evidence-budgets.json tests/py/test_evidence_city_budget.py
git commit -m "fix: evidence budgets judge each city page on its own city, and budget the brand

The city term was hard-coded to the former city, so 27 of 28 city pages had no ceiling;
it is now {city}, resolved per slug from data/locations.json. bluestaffyuk is budgeted on
every page type; four built pages are held at their count as built. CAG parity audit D2.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: PuppyCard delivery line + dist test

**Closes:** audit D4 (CAG §16d); `rules/puppies.md` `delivery-band-on-every-card` moves from `untested` to `test`

`rules/puppies.md:27` already mandates a canonical card line — "UK home delivery £200–£350 by distance · or collect in Carlisle" — and says never to ship a card without it; `src/components/kit/PuppyCard.astro` has none. The card now renders that line from `data/settings.json` (`delivery_min_gbp`, `delivery_max_gbp`, `address.city`). Three consequences, all handled here and all measured on the build of 2026-09-26:
- the line repeats on every page that mounts a card, by design, so it becomes a whitelisted stem in `scripts/dup_content_audit.py` (also what keeps a future city page's `outline-sentence-crossover` from firing on it). `python3 scripts/dup_content_audit.py` reports exactly the same 131 passages before and after;
- it says "UK" once per card, and eight built pages mount the six cards, so each of those pages' `uk` budget in `budgets_by_slug` rises by 6 (the line is mandated text, so it is carried — the Known Issue 34 method). The twelve built pages stay at `0 problems`;
- the render harness sees the same result before and after (3 pre-existing failures on `uk-locations/blue-staffy-puppies-uk`, 57 passed).

**Files:**
- Create: `tests/py/test_puppy_card_delivery.py`
- Modify: `src/components/kit/PuppyCard.astro` (comment after line 12; import line 18; new const after line 26; new `<p>` after line 46; new style rule after line 67)
- Modify: `scripts/dup_content_audit.py` (new stem after line 137, `"cheryl female blue with white blaze 1 700",`)
- Modify: `rules/puppies.md` (line 23, `enforced:`)
- Modify: `data/quality/rule-index.json` (row `delivery-band-on-every-card`, lines 343–348)
- Modify: `data/quality/evidence-budgets.json` (`budgets_by_slug` `uk` on eight slugs)
- Test: `tests/py/test_puppy_card_delivery.py`

- [ ] **Step 1: Write the failing test** — `tests/py/test_puppy_card_delivery.py`:
```python
"""Every puppy card carries its delivery line (CAG parity audit D4; rules/puppies.md
`delivery-band-on-every-card`).

rules/puppies.md has said since the port that a puppy card MUST show the delivery cost, in
one canonical line — "UK home delivery £200–£350 by distance · or collect in Carlisle" — and
that no card ships without it. Nothing enforced it, and src/components/kit/PuppyCard.astro
showed sex, colour, price and status and nothing about getting the puppy home. Project 5's
city pages mount that card. The line reads the band and the town from data/settings.json,
so it can never disagree with the price table or the FAQ.
"""
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import dup_content_audit as dup  # noqa: E402
import evidence_audit as ea  # noqa: E402

CARD = ROOT / "src/components/kit/PuppyCard.astro"
SETTINGS = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
DIST = ROOT / "dist"
ARTICLE = re.compile(r'<article\b[^>]*class="[^"]*\bkit-pup\b[^"]*"[^>]*>(.*?)</article>', re.S)
DELIV = re.compile(r'<p\b[^>]*class="[^"]*\bdeliv\b[^"]*"[^>]*>(.*?)</p>', re.S)
RULES = json.loads((ROOT / "data/quality/rule-index.json").read_text(encoding="utf-8"))["rules"]


def expected_line():
    lo, hi = SETTINGS["delivery_min_gbp"], SETTINGS["delivery_max_gbp"]
    return f"UK home delivery £{lo:,}–£{hi:,} by distance · or collect in {SETTINGS['address']['city']}"


def test_the_card_reads_the_band_from_settings_and_types_no_amount():
    src = CARD.read_text(encoding="utf-8")
    for key in ("SITE.delivery_min_gbp", "SITE.delivery_max_gbp", "SITE.address.city"):
        assert key in src, key
    markup = src.split("---", 2)[2]
    assert not re.search(r"£\s*\d", markup), "the card template spells a delivery amount by hand"


def test_the_rule_is_enforced_by_this_file():
    row = next(r for r in RULES if r["id"] == "delivery-band-on-every-card")
    assert row["enforced"] == "test" and row["test"] == "tests/py/test_puppy_card_delivery.py", row
    pack = (ROOT / "rules/puppies.md").read_text(encoding="utf-8")
    assert re.search(r"id: delivery-band-on-every-card\nenforced: test\n", pack)


def test_the_line_is_whitelisted_as_the_canonical_card_line():
    stem = " ".join(re.findall(r"[a-z0-9$']+", expected_line().lower()))
    assert stem in dup.WHITELIST_SNIPPETS


def built_pages_with_cards():
    return [p for p in sorted(DIST.glob("**/index.html")) if "kit-pup" in p.read_text(encoding="utf-8")]


def test_every_built_card_carries_the_delivery_line():
    if not DIST.exists():
        pytest.skip("run npm run build first")
    pages = built_pages_with_cards()
    assert len(pages) >= 5, "fewer built pages carry a puppy card than the kit mounts on"
    bad, examined = [], 0
    for page in pages:
        for card in ARTICLE.findall(page.read_text(encoding="utf-8")):
            examined += 1
            got = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m)).strip() for m in DELIV.findall(card)]
            if got != [expected_line()]:
                bad.append((page.relative_to(DIST).as_posix(), got))
    assert examined > 0, "no puppy card was examined — that is not a pass"
    assert bad == [], bad


REBUILT = json.loads((ROOT / "data/facts/rebuilt.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("slug", REBUILT)
def test_the_card_line_keeps_every_built_page_inside_its_term_budgets(slug):
    built = DIST / ("index.html" if slug == "index" else f"{slug}/index.html")
    if not built.exists():
        pytest.skip("run npm run build first")
    budgets = json.loads((ROOT / "data/quality/evidence-budgets.json").read_text(encoding="utf-8"))
    over = ea.term_budget(built.read_text(encoding="utf-8"), ea.page_type_for(slug), budgets, slug)
    assert over == [], (slug, over)
```

- [ ] **Step 2: Run it and confirm it fails**
Run: `npm run -s build >/dev/null && python3 -m pytest tests/py/test_puppy_card_delivery.py -q`
Expected: FAIL — `4 failed, 12 passed`: `test_the_card_reads_the_band_from_settings_and_types_no_amount`, `test_the_rule_is_enforced_by_this_file`, `test_the_line_is_whitelisted_as_the_canonical_card_line` and `test_every_built_card_carries_the_delivery_line` fail; the twelve budget cases pass (no line yet).

- [ ] **Step 3: Implement the line in `src/components/kit/PuppyCard.astro`**

Old (lines 11–12):
```astro
// Brass is a FILL here (the price chip carries --color-cta-ink), never a text colour on
// the bone card: it is 2.1:1 there.
```
New:
```astro
// Brass is a FILL here (the price chip carries --color-cta-ink), never a text colour on
// the bone card: it is 2.1:1 there.
//
// THE DELIVERY LINE (rules/puppies.md `delivery-band-on-every-card`; CAG parity audit D4).
// A card never ships without what it costs to get the puppy home, in the pack's canonical
// words: "UK home delivery £200–£350 by distance · or collect in Carlisle". The band and the
// town are data/settings.json's, so the card cannot disagree with the price table or the
// FAQ. The line is a whitelisted stem in scripts/dup_content_audit.py (it repeats on every
// page that mounts a card, by design). tests/py/test_puppy_card_delivery.py.
```

Old (line 18): `import type { PuppyRow } from '../../lib/site';`
New: `import { SITE, gbp, type PuppyRow } from '../../lib/site';`

Old (line 26):
```astro
const href = `/available-puppies/${p.slug}/`;
```
New:
```astro
const href = `/available-puppies/${p.slug}/`;
const delivery = `UK home delivery £${gbp(SITE.delivery_min_gbp)}–£${gbp(SITE.delivery_max_gbp)} `
  + `by distance · or collect in ${SITE.address.city}`;
```

Old (lines 45–46):
```astro
      <span class:list={['kit-chip', avail && 'ok']}>{p.status}</span>
    </p>
```
New:
```astro
      <span class:list={['kit-chip', avail && 'ok']}>{p.status}</span>
    </p>
    <p class="deliv">{delivery}</p>
```

Old (line 67):
```css
    .kit-chip.ok { color: var(--color-ok); }
```
New:
```css
    .kit-chip.ok { color: var(--color-ok); }
    /* --color-text-muted on the raised card is a measured pair in data/design/contrast.json. */
    .deliv { margin: 0; font-size: var(--text-sm); color: var(--color-text-muted); }
```

- [ ] **Step 4: Whitelist the line** — `scripts/dup_content_audit.py`, Old (line 137):
```python
    "cheryl female blue with white blaze 1 700",
```
New:
```python
    "cheryl female blue with white blaze 1 700",
    # the card's delivery line (rules/puppies.md `delivery-band-on-every-card`): the pack's
    # canonical words, rendered once per card by src/components/kit/PuppyCard.astro from
    # data/settings.json, so it repeats on every page that mounts a card by design. Added
    # 2026-09-26 with the line itself (CAG parity audit D4); measured on dist/ that day.
    "uk home delivery 200 350 by distance or collect in carlisle",
```

- [ ] **Step 5: Mark the rule enforced** — `rules/puppies.md` lines 22–23, Old:
```markdown
id: delivery-band-on-every-card
enforced: untested
```
New:
```markdown
id: delivery-band-on-every-card
enforced: test
```
Then the ledger row and the eight carried `uk` budgets (both files round-trip exactly through the dump settings used here):
```bash
python3 - <<'EOF'
import json
p = "data/quality/rule-index.json"
d = json.load(open(p, encoding="utf-8"))
i = next(i for i, r in enumerate(d["rules"]) if r["id"] == "delivery-band-on-every-card")
d["rules"][i] = {"id": "delivery-band-on-every-card", "family": "COPY", "enforced": "test",
                 "pack": "rules/puppies.md", "test": "tests/py/test_puppy_card_delivery.py",
                 "_note": "The card half: every built puppy card carries the canonical line from data/settings.json (CAG parity audit D4, 2026-09-26). The delivery-section half stays with the builders' outlines."}
open(p, "w", encoding="utf-8").write(json.dumps(d, indent=1) + "\n")

# The canonical card line says "UK" once per card, and it is mandated text (rules/puppies.md),
# so on each built page that mounts the six cards it is CARRIED: +6 on that page's `uk` budget.
p = "data/quality/evidence-budgets.json"
b = json.load(open(p, encoding="utf-8"))
CARD_PAGES = ["index", "thank-you-blue-staffy-puppies-journey", "blue-staffy-pup-sale-uk",
              "buy-blue-staffy-puppies-uk", "buy-staffy-puppies-for-sale-uk", "blue-staffy-uk-breeders",
              "uk-staffordshire-bull-terrier-guide", "uk-blue-staffy-puppy-buying-guide"]
for slug in CARD_PAGES:
    row = b["budgets_by_slug"][slug]
    old = row["uk"]
    row["uk"] = old + 6
    row["_why"] += (f" `uk` +6 on 2026-09-26 (CAG parity audit D4): the six puppy cards each carry the "
                    f"canonical delivery line from rules/puppies.md `delivery-band-on-every-card`, which "
                    f"says UK once — mandated text, so carried; budget {old} + 6 = {old + 6}.")
open(p, "w", encoding="utf-8").write(json.dumps(b, indent=2, ensure_ascii=False) + "\n")
EOF
```
The new `uk` budgets: `index` 48, `thank-you-blue-staffy-puppies-journey` 13, `blue-staffy-pup-sale-uk` 34, `buy-blue-staffy-puppies-uk` 26, `buy-staffy-puppies-for-sale-uk` 59, `blue-staffy-uk-breeders` 32, `uk-staffordshire-bull-terrier-guide` 47, `uk-blue-staffy-puppy-buying-guide` 53.

- [ ] **Step 6: Build, run it and confirm it passes**
Run: `npm run -s build >/dev/null; echo build=$?` → Expected: `build=0`
Run: `python3 -m pytest tests/py/test_puppy_card_delivery.py -q` → Expected: `16 passed`
Run: `python3 -m pytest tests/py/test_evidence_city_budget.py tests/py/test_dup_whitelist_measured.py tests/py/test_dup_content_audit.py tests/py/test_rules_index.py tests/py/test_design_components.py -q` → Expected: 0 failed
Run: `python3 scripts/dup_content_audit.py | tail -1` → Expected: `FAIL — 131 duplicated passages ≥12 words.` (the same count as before this task: the baseline is migrated city prose)
Run: `python3 scripts/evidence_audit.py $(python3 -c "import json;print(' '.join(json.load(open('data/facts/rebuilt.json'))))") | tail -1` → Expected: `examined 12 pages; 0 problems (48 WARN)`

- [ ] **Step 7: Run the gates**
Run: `npm run -s check:all; echo exit=$?` → Expected: `exit=0`
Run: `npm run test:render:pages` → Expected: the same result as before the task: `3 failed` (the pre-existing `uk-locations/blue-staffy-puppies-uk` at 375/768/1280) and `57 passed`. A NAV settle-budget timeout on another page under the full parallel run is a known flake; re-run that page alone with `npx playwright test -c tests/render/playwright.config.ts pages.spec.ts -g "<slug>" --project vp768` before treating it as a defect.

- [ ] **Step 8: Commit**
```bash
git add src/components/kit/PuppyCard.astro scripts/dup_content_audit.py rules/puppies.md data/quality/rule-index.json data/quality/evidence-budgets.json tests/py/test_puppy_card_delivery.py
git commit -m "feat: every puppy card carries the canonical delivery line

rules/puppies.md mandated it and nothing enforced it; the kit card had none. The line is
read from data/settings.json, whitelisted as a stem, and carried in the eight card pages'
uk budgets. delivery-band-on-every-card is now enforced: test. CAG parity audit D4.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

- [ ] **Step 9: Keep the page-date map current**
Run: `python3 scripts/generate_page_dates.py --check; echo exit=$?` → if `exit=0`, nothing to do. If it reports the map stale (the card change re-dates the pages that mount it), run `npm run dates` and commit the map on its own:
```bash
git add data/page-dates.json
git commit -m "chore: page dates after the puppy card delivery line

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: Resolve the Rule 18 contradiction (no floor, ≤105 ceiling; seo-rules.md follows the verifier)

**Closes:** audit Wave 1 item 4 (CAG §7b, Appendix B rows 7b.1–7b.7)

`docs/reference/seo-rules.md:122` calls the Rule 18 total "≈85–105× · Hard target per page"; `.claude/agents/bsuk-keyword-verifier.md:247-252` — the agent that judges the count — says "≤105 (no minimum)", no floor since 2026-09-09, OVER-STUFFED above 110. Five more files tell a writer the total "must hit 85–105×". The verifier is the authority; everything else follows it.

**Files:**
- Create: `tests/py/test_rule18_frequency.py`
- Modify: `docs/reference/seo-rules.md` (line 122, the TOTAL row, plus the rules block after it; line 344)
- Modify: `.claude/agents/bsuk-content-audit-agent.md` (line 70)
- Modify: `.claude/agents/bsuk-homepage-builder.md` (line 74)
- Modify: `.claude/skills/bsuk-seo-master-checklist/SKILL.md` (line 475)
- Modify: `.claude/skills/bsuk-puppy-page-builder/SKILL.md` (line 64)
- Test: `tests/py/test_rule18_frequency.py`

- [ ] **Step 1: Write the failing test** — `tests/py/test_rule18_frequency.py`:
```python
"""Rule 18 says one thing everywhere: a ceiling of 105 keyword mentions, and no floor.

docs/reference/seo-rules.md called its ≈85–105 total a "Hard target per page" while
.claude/agents/bsuk-keyword-verifier.md — the agent that actually judges the count — says
≤105 with no minimum (the floor was retired on 2026-09-09 because it manufactured the very
repetition the evidence pass fails). Five more instruction files told a writer the total
"must hit 85–105×". A writer given both reads a floor and pads. The verifier is the authority;
this test holds every other instruction file to it (CAG parity audit, Wave 1 item 4).
"""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SEO_RULES = ROOT / "docs/reference/seo-rules.md"
VERIFIER = ROOT / ".claude/agents/bsuk-keyword-verifier.md"
TOTAL_ROW = re.compile(r"^\|\s*\*\*TOTAL\*\*\s*\|\s*(.+?)\s*\|", re.M)
# a count band presented as something to reach: "must hit 85–105×", "vs 85–105× target",
# "~85–105 total mentions", "≈85–105×"
FLOOR = re.compile(r"(?i)(?:must hit|hits|≈|~|vs)\s*85\s*[–-]\s*105|85\s*[–-]\s*105[×x]?\s*(?:total\s*)?(?:target|mentions)|hard target")


def rule18(text):
    m = re.search(r"\*\*Rule 18\b.*?(?=\n\*\*Rule 19\b)", text, re.S)
    assert m, "seo-rules.md lost its Rule 18 block"
    return m.group(0)


def instruction_files():
    return (sorted((ROOT / ".claude/agents").glob("*.md"))
            + sorted((ROOT / ".claude/skills").glob("*/SKILL.md"))
            + sorted((ROOT / "docs/reference").glob("*.md"))
            + sorted((ROOT / "rules").glob("*.md")))


def test_seo_rules_total_row_is_the_verifiers():
    ours = TOTAL_ROW.findall(rule18(SEO_RULES.read_text(encoding="utf-8")))
    theirs = TOTAL_ROW.findall(VERIFIER.read_text(encoding="utf-8"))
    assert theirs == ["**≤105 (no minimum)**"], theirs
    assert ours == theirs, (ours, theirs)


def test_seo_rules_rule_18_states_no_floor_and_the_over_stuffed_flag():
    block = rule18(SEO_RULES.read_text(encoding="utf-8"))
    assert "no floor" in block
    assert "OVER-STUFFED" in block and ">110" in block


@pytest.mark.parametrize("path", instruction_files(), ids=lambda p: p.parent.name + "/" + p.name)
def test_no_instruction_file_presents_the_band_as_a_floor(path):
    bad = ["%s:%d  %s" % (path.name, n, l.strip()[:110])
           for n, l in enumerate(path.read_text(encoding="utf-8").splitlines(), 1) if FLOOR.search(l)]
    assert bad == [], ("Rule 18 has no floor (bsuk-keyword-verifier.md): the total is a ceiling "
                       "of 105, never a target to hit:\n  " + "\n  ".join(bad))


def test_the_floor_lint_fires_and_spares_the_ceiling(tmp_path):
    for line in ("total row at bottom must hit 85–105× per Rule 18",
                 "rolling total vs 85–105× target.",
                 "### 2a. Keyword distribution per page (~85–105 total mentions)",
                 "| **TOTAL** | **≈85–105×** | Hard target per page |"):
        assert FLOOR.search(line), line
    for line in ("| **TOTAL** | **≤105 (no minimum)** | |",
                 "the total row stays at or under 105 (Rule 18 — a ceiling, no floor)"):
        assert not FLOOR.search(line), line
```

- [ ] **Step 2: Run it and confirm it fails**
Run: `python3 -m pytest tests/py/test_rule18_frequency.py -q`
Expected: FAIL — `7 failed, 116 passed`: `test_seo_rules_total_row_is_the_verifiers`, `test_seo_rules_rule_18_states_no_floor_and_the_over_stuffed_flag`, and `test_no_instruction_file_presents_the_band_as_a_floor[...]` for `agents/bsuk-content-audit-agent.md`, `agents/bsuk-homepage-builder.md`, `bsuk-puppy-page-builder/SKILL.md`, `bsuk-seo-master-checklist/SKILL.md` and `reference/seo-rules.md`.

- [ ] **Step 3: Implement**

`docs/reference/seo-rules.md` line 122, Old:
```markdown
| **TOTAL** | **≈85–105×** | Hard target per page |
```
New:
```markdown
| **TOTAL** | **≤105 (no minimum)** | |

The authority for this table is `.claude/agents/bsuk-keyword-verifier.md`, which judges the
count; this block follows it (`tests/py/test_rule18_frequency.py`):
- There is **no floor**. A page is never "under-optimized" by count (retired 2026-09-09: the
  floor manufactured the repetition the evidence pass now fails). The per-type counts above
  are ceilings to stay under, never numbers to reach.
- A full page with >110 total keyword mentions is flagged **OVER-STUFFED**; trust-concept
  terms additionally answer to `data/quality/evidence-budgets.json` via
  `scripts/evidence_audit.py`.
- Short pages (<1,500 words): scale proportionally; do not apply full-page thresholds.
```
Same file, line 344. Old: `One row per section from hero to final CTA; the total row hits 85–105× per Rule 18.`
New: `One row per section from hero to final CTA; the total row stays at or under 105 (Rule 18 — a ceiling, no floor).`

`.claude/agents/bsuk-content-audit-agent.md` line 70. Old: `[One row per section; total row at bottom must hit 85–105× per Rule 18]`
New: `[One row per section; total row at bottom stays at or under 105 per Rule 18 — a ceiling, no floor]`

`.claude/agents/bsuk-homepage-builder.md` line 74, replace the end of the line. Old: `rolling total vs 85–105× target.`
New: `rolling total against the Rule 18 ceiling of 105 (no floor).`

`.claude/skills/bsuk-seo-master-checklist/SKILL.md` line 475. Old: `Total row at bottom must hit 85–105× total keyword distribution target (Rule 18).`
New: `Total row at bottom stays at or under 105 total keyword mentions (Rule 18 — a ceiling, no floor).`

`.claude/skills/bsuk-puppy-page-builder/SKILL.md` line 64. Old: `### 2a. Keyword distribution per page (~85–105 total mentions; 1–2% primary density, never stuffed)`
New: `### 2a. Keyword distribution per page (≤105 total mentions, no floor; 1–2% primary density, never stuffed)`

- [ ] **Step 4: Run it and confirm it passes**
Run: `python3 -m pytest tests/py/test_rule18_frequency.py -q` → Expected: `123 passed`
Run: `python3 -m pytest tests/py/test_agent_facts.py tests/py/test_rules_index.py tests/py/test_builder_skills.py -q` → Expected: 0 failed

- [ ] **Step 5: Run the gates**
Run: `npm run -s check:all; echo exit=$?` → Expected: `examined 41 agents; 0 problems` and `exit=0` (two agents changed; `npm run agents` re-checks the registry)

- [ ] **Step 6: Commit**
```bash
git add docs/reference/seo-rules.md .claude/agents/bsuk-content-audit-agent.md .claude/agents/bsuk-homepage-builder.md .claude/skills/bsuk-seo-master-checklist/SKILL.md .claude/skills/bsuk-puppy-page-builder/SKILL.md tests/py/test_rule18_frequency.py
git commit -m "fix: Rule 18 is a ceiling of 105 with no floor, everywhere

seo-rules.md called 85-105 a hard target while the keyword verifier, which judges the
count, retired the floor on 2026-09-09. seo-rules.md now follows the verifier, and five
instruction files stop telling writers to hit the band.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: perf_audit.py: default 5 runs, warm median of runs 2–5 with spread, refuse CLS verdict on <5

**Closes:** audit Wave 1 item 5 (CAG §19b.5, M7)

`scripts/perf_audit.py:204` defaults to `--runs 1` while its own docstring says 5, `.claude/skills/bsuk-perf-gate/SKILL.md:22-23` says 3 and `scripts/pageboard.py:1577` hints 3. Nothing drops the cold first run. After this task: 5 runs by default; the verdict is the warm median of runs 2–N (one run is its own set), printed with the warm spread and the cold run beside it; the record gains `warm_runs`, `spread`, `cold` and `cls`; a CLS verdict (warm median ≤ 0.1) is given only on 5+ runs and a CLS FAIL fails the gate as `cumulative-layout-shift`.

**Files:**
- Modify: `tests/py/test_perf_audit.py` (add `import re` after line 10; append after the last line, 199)
- Modify: `scripts/perf_audit.py` (docstring lines 4–5 and 18–19; constants after line 72; helpers before `_requests` at line 90; `--runs` at line 204; guard after line 212; report block lines 255–271; record lines 302–305)
- Modify: `scripts/pageboard.py` (line 1577, the `perf-record-missing` hint)
- Modify: `.claude/skills/bsuk-perf-gate/SKILL.md` (lines 22–23; new paragraph before line 29)
- Modify: `.claude/agents/bsuk-performance-fixer.md` (line 71)
- Modify: `docs/reference/WORKFLOW.md` (line 618)
- Test: `tests/py/test_perf_audit.py`

- [ ] **Step 1: Write the failing test** — in `tests/py/test_perf_audit.py`, Old (lines 9–11):
```python
import json
import subprocess
import urllib.error
```
New:
```python
import json
import subprocess
import re
import urllib.error
```
and append to the end of the file:
```python
# --- the run protocol: five runs, the warm median of runs 2-5, no CLS verdict on fewer ----
# CAG parity audit 19b.5 / M7. CLS on this site is bimodal and the first Lighthouse run of a
# session is cold (Chrome start, empty caches), so one run proves nothing and a median that
# includes the cold run is not a warm number. The docstring already said `--runs 5`; the
# code defaulted to 1, the perf-gate skill said 3, and the release gate's hint said 3.

class _NoServer:
    def shutdown(self):
        pass


def _fake_runs(monkeypatch, tmp_path, reports):
    """Run main() against canned Lighthouse reports; returns (calls, perf_dir, dist)."""
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html></html>")
    perf_dir = tmp_path / "perf"
    calls = []

    def fake(url, out, profile):
        calls.append(url)
        return reports[len(calls) - 1]
    monkeypatch.setattr(pa, "serve", lambda root: _NoServer())
    monkeypatch.setattr(pa, "run_lighthouse", fake)
    monkeypatch.setattr(pa, "PERF_DIR", perf_dir)
    return calls, perf_dir, dist


def lh(perf=1, cls=0.0):
    return {"lighthouseVersion": "13.4.1",
            "categories": {k: {"score": perf if k == "performance" else 1} for k in pa.CATEGORIES},
            "audits": {"cumulative-layout-shift": {"numericValue": cls}}}


def test_the_default_is_five_runs(monkeypatch, tmp_path):
    calls, _, dist = _fake_runs(monkeypatch, tmp_path, [lh()] * 5)
    assert pa.main(["", "--dist", str(dist)]) == 0
    assert len(calls) == 5


def test_the_cold_first_run_is_not_judged():
    runs = [lh(perf=0.5), lh(perf=0.99), lh(perf=1), lh(perf=1), lh(perf=0.99)]
    assert pa.judge(runs) == ["performance"]           # all five: median 0.99
    assert pa.warm(runs) == runs[1:]
    assert pa.judge(pa.warm(runs)) == []               # runs 2-5: median 0.995


def test_one_run_is_its_own_warm_set():
    one = [lh()]
    assert pa.warm(one) == one


def test_the_record_carries_the_warm_median_and_its_spread(monkeypatch, tmp_path, capsys):
    reports = [lh(perf=0.5), lh(perf=0.99), lh(perf=1), lh(perf=1), lh(perf=0.99)]
    _, perf_dir, dist = _fake_runs(monkeypatch, tmp_path, reports)
    assert pa.main(["", "--dist", str(dist)]) == 0
    out = capsys.readouterr().out
    assert "warm median of runs 2–5" in out
    rec = json.loads((perf_dir / "home--desktop.json").read_text())
    assert rec["runs"] == 5 and rec["warm_runs"] == 4
    assert rec["median"]["performance"] == 0.995
    assert rec["spread"]["performance"] == [0.99, 1]
    assert rec["cold"]["performance"] == 0.5


def test_fewer_than_five_runs_gives_no_cls_verdict(monkeypatch, tmp_path, capsys):
    _, perf_dir, dist = _fake_runs(monkeypatch, tmp_path, [lh(cls=0.3)] * 3)
    assert pa.main(["", "--dist", str(dist), "--runs", "3"]) == 0
    assert "no CLS verdict" in capsys.readouterr().out
    rec = json.loads((perf_dir / "home--desktop.json").read_text())
    assert rec["cls"]["verdict"] is None


def test_five_runs_judge_cls_on_the_warm_median(monkeypatch, tmp_path, capsys):
    # the cold run's 0.0 does not rescue four warm runs at 0.25
    reports = [lh(cls=0.0)] + [lh(cls=0.25)] * 4
    _, perf_dir, dist = _fake_runs(monkeypatch, tmp_path, reports)
    assert pa.main(["", "--dist", str(dist)]) == 1
    rec = json.loads((perf_dir / "home--desktop.json").read_text())
    assert rec["cls"]["verdict"] == "FAIL" and rec["cls"]["median"] == 0.25
    assert "cumulative-layout-shift" in rec["failed"]


def test_five_warm_runs_under_the_cls_line_pass(monkeypatch, tmp_path):
    _, perf_dir, dist = _fake_runs(monkeypatch, tmp_path, [lh(cls=0.3)] + [lh(cls=0.02)] * 4)
    assert pa.main(["", "--dist", str(dist)]) == 0
    assert json.loads((perf_dir / "home--desktop.json").read_text())["cls"]["verdict"] == "PASS"


ROOT = pathlib.Path(__file__).resolve().parents[2]
FEW_RUNS = re.compile(r"--runs[ =]+[1-4]\b")


def test_no_instruction_or_hint_asks_for_fewer_than_five_runs():
    files = ([ROOT / "CLAUDE.md", ROOT / "scripts/pageboard.py", ROOT / "scripts/perf_audit.py"]
             + sorted((ROOT / ".claude").rglob("*.md")) + sorted((ROOT / "docs/reference").glob("*.md"))
             + sorted((ROOT / "rules").glob("*.md")))
    bad = [f"{p.relative_to(ROOT)}:{n}" for p in files
           for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1) if FEW_RUNS.search(line)]
    assert bad == [], bad
```

- [ ] **Step 2: Run it and confirm it fails**
Run: `python3 -m pytest tests/py/test_perf_audit.py -q`
Expected: FAIL — `8 failed, 21 passed` (`AttributeError: module 'perf_audit' has no attribute 'warm'` on the protocol tests; `test_the_default_is_five_runs` asserts `1 == 5`; `test_no_instruction_or_hint_asks_for_fewer_than_five_runs` lists `scripts/pageboard.py:1577` and `.claude/skills/bsuk-perf-gate/SKILL.md:22`, `:23`)

- [ ] **Step 3: Implement in `scripts/perf_audit.py`**

Old (lines 4–5):
```python
  python3 scripts/perf_audit.py <slug>                    # desktop, against dist/
  python3 scripts/perf_audit.py <slug> --mobile --runs 5  # CLS is bimodal; take the median
```
New:
```python
  python3 scripts/perf_audit.py <slug>                    # desktop, against dist/, 5 runs
  python3 scripts/perf_audit.py <slug> --mobile           # mobile, 5 runs
```

Old (lines 18–19):
```python
Agentic Browsing (Lighthouse 13.4.1, `agentic-browsing-config.js`). Every floor is 0.995,
the score PSI displays as 100. The median of the runs is judged.
```
New:
```python
Agentic Browsing (Lighthouse 13.4.1, `agentic-browsing-config.js`). Every floor is 0.995,
the score PSI displays as 100.

THE RUN PROTOCOL (CAG §19b, measurement M7). Five runs by default. Run 1 is cold — a fresh
Chrome, empty caches — so the verdict is the WARM median, of runs 2–5, printed with the
spread of those runs and the cold run beside it; one run is its own warm set. CLS on this
site is bimodal, so a CLS verdict (warm median at or under 0.1) is given only on five or
more runs: on fewer, the record says `"verdict": null` and the output says so, and a CLS
FAIL on five runs fails the gate as `cumulative-layout-shift`.
```

Old (line 72):
```python
LH_TIMEOUT = 300
```
New:
```python
LH_TIMEOUT = 300
DEFAULT_RUNS = 5
CLS_MIN_RUNS = 5
CLS_GOOD = 0.1   # the "good" line of Core Web Vitals
```

Old (line 90): `def _requests(report):`
New (the four helpers go directly above it):
```python
def warm(reports):
    """The runs that are judged: every run after the cold first one. One run is its own set."""
    return list(reports[1:]) if len(reports) > 1 else list(reports)


def _scores(reports, cat):
    return [((r.get("categories") or {}).get(cat) or {}).get("score") or 0 for r in reports]


def _cls_values(reports):
    vals = [((r.get("audits") or {}).get("cumulative-layout-shift") or {}).get("numericValue") for r in reports]
    return [v for v in vals if isinstance(v, (int, float))]


def cls_verdict(reports):
    """{"verdict": PASS|FAIL|None, "median", "min", "max", "runs"} over the WARM runs.
    None on fewer than CLS_MIN_RUNS runs in total: CLS is bimodal, and a verdict on three
    runs is the kind that has already caused a confident wrong attribution here."""
    vals = _cls_values(warm(reports))
    out = {"verdict": None, "runs": len(reports), "runs_needed": CLS_MIN_RUNS,
           "median": round(statistics.median(vals), 4) if vals else None,
           "min": round(min(vals), 4) if vals else None, "max": round(max(vals), 4) if vals else None}
    if len(reports) >= CLS_MIN_RUNS and vals:
        out["verdict"] = "PASS" if statistics.median(vals) <= CLS_GOOD else "FAIL"
    return out


def _requests(report):
```

Old (line 204):
```python
    ap.add_argument("--runs", type=int, default=1)
```
New:
```python
    ap.add_argument("--runs", type=int, default=DEFAULT_RUNS,
                    help=f"Lighthouse runs (default {DEFAULT_RUNS}); run 1 is cold and is not judged")
```

Old (lines 211–212):
```python
    if a.slug is None:
        ap.error("slug is required unless --parse is given (use '' for the home page)")
```
New:
```python
    if a.slug is None:
        ap.error("slug is required unless --parse is given (use '' for the home page)")
    if a.runs < 1:
        ap.error("--runs must be at least 1")
```

Old (lines 255–271):
```python
    lh_version = reports[0].get("lighthouseVersion", "?")
    print(f"\n  {path}  [{profile}{' · PSI' if a.psi else ' · LIVE' if a.live else ' · dist'}]  {a.runs} run(s) · Lighthouse {lh_version}")
    failed = judge(reports)
    median = {}
    for cat, floor in THRESHOLDS.items():
        scores = [((r.get("categories") or {}).get(cat) or {}).get("score") or 0 for r in reports]
        median[cat] = statistics.median(scores)
        spread = "" if len(scores) == 1 else f"  (runs: {', '.join(str(round(s * 100)) for s in sorted(scores))})"
        print(f"    {'FAIL' if cat in failed else 'PASS'}  {cat:17s} {round(median[cat] * 100):3d}  floor 100{spread}")

    metrics = {}
    for m in ("cumulative-layout-shift", "largest-contentful-paint", "total-blocking-time"):
        vals = [v for v in (((r.get("audits") or {}).get(m) or {}).get("numericValue") for r in reports)
                if isinstance(v, (int, float))]
        if vals:
            metrics[m] = round(statistics.median(vals), 4)
            print(f"    {m}: median {metrics[m]}  min {round(min(vals), 4)}  max {round(max(vals), 4)}")
```
New:
```python
    lh_version = reports[0].get("lighthouseVersion", "?")
    judged = warm(reports)
    basis = "one run" if len(reports) == 1 else f"warm median of runs 2–{len(reports)}"
    print(f"\n  {path}  [{profile}{' · PSI' if a.psi else ' · LIVE' if a.live else ' · dist'}]  {a.runs} run(s) · {basis} · Lighthouse {lh_version}")
    failed = judge(judged)
    median, spread, cold = {}, {}, {}
    for cat, floor in THRESHOLDS.items():
        scores = _scores(judged, cat)
        median[cat] = statistics.median(scores)
        spread[cat] = [min(scores), max(scores)]
        note = ""
        if len(reports) > 1:
            cold[cat] = _scores(reports[:1], cat)[0]
            note = (f"  (warm runs: {', '.join(str(round(s * 100)) for s in sorted(scores))};"
                    f" cold run 1: {round(cold[cat] * 100)})")
        print(f"    {'FAIL' if cat in failed else 'PASS'}  {cat:17s} {round(median[cat] * 100):3d}  floor 100{note}")

    metrics = {}
    for m in ("cumulative-layout-shift", "largest-contentful-paint", "total-blocking-time"):
        vals = [v for v in (((r.get("audits") or {}).get(m) or {}).get("numericValue") for r in judged)
                if isinstance(v, (int, float))]
        if vals:
            metrics[m] = round(statistics.median(vals), 4)
            print(f"    {m}: median {metrics[m]}  min {round(min(vals), 4)}  max {round(max(vals), 4)}")

    cls = cls_verdict(reports)
    if cls["verdict"] is None:
        print(f"    CLS: no CLS verdict on {len(reports)} run(s) — CLS is bimodal; "
              f"run {CLS_MIN_RUNS} (the default) for one")
    else:
        print(f"    {cls['verdict']}  CLS warm median {cls['median']}  line {CLS_GOOD}")
        if cls["verdict"] == "FAIL":
            failed.append("cumulative-layout-shift")
```

Old (record, lines 303–304):
```python
        "slug": slug, "profile": profile, "live": a.live, "psi": a.psi, "lighthouse": lh_version, "runs": a.runs,
        "median": median, "metrics": metrics, "failed": failed,
```
New:
```python
        "slug": slug, "profile": profile, "live": a.live, "psi": a.psi, "lighthouse": lh_version, "runs": a.runs,
        "warm_runs": len(judged), "median": median, "spread": spread, "cold": cold,
        "metrics": metrics, "cls": cls, "failed": failed,
```

`scripts/pageboard.py` line 1577, replace the tail of the f-string. Old: `python3 scripts/perf_audit.py {slug}{' --mobile' if prof == 'mobile' else ''} --runs 3")`
New: `python3 scripts/perf_audit.py {slug}{' --mobile' if prof == 'mobile' else ''} (5 runs, the default)")`

`.claude/skills/bsuk-perf-gate/SKILL.md` lines 22–23, Old:
```bash
python3 scripts/perf_audit.py <slug> --runs 3            # desktop, dist/
python3 scripts/perf_audit.py <slug> --mobile --runs 3   # mobile, dist/
```
New:
```bash
python3 scripts/perf_audit.py <slug>                     # desktop, dist/, 5 runs
python3 scripts/perf_audit.py <slug> --mobile            # mobile, dist/, 5 runs
```
Same file, Old (line 29, first line of the paragraph after the code block):
```markdown
Every floor is 0.995 (what PSI displays as 100). Lighthouse is pinned to 13.4.1 with
```
New:
```markdown
Five runs is the default. Run 1 is cold and is never judged: the verdict is the **warm
median of runs 2–5**, printed with the spread of those runs and the cold run beside it. A
CLS verdict (warm median at or under 0.1) is given only on five or more runs — on fewer,
the output says `no CLS verdict` and the record carries `"verdict": null`.

Every floor is 0.995 (what PSI displays as 100). Lighthouse is pinned to 13.4.1 with
```

`.claude/agents/bsuk-performance-fixer.md` line 71, replace the fragment. Old:
```markdown
runs Lighthouse against `dist/` and judges the median of the runs; CLS is bimodal here, so judge `--runs 5`.
```
New:
```markdown
runs Lighthouse five times against `dist/` and judges the warm median of runs 2–5 (run 1 is cold); CLS is bimodal here, so it gives no CLS verdict on fewer than five runs.
```

`docs/reference/WORKFLOW.md` line 618. Old:
```
   → Target: every category's median score over the runs ≥0.995 (the 100 PageSpeed Insights shows);
```
New:
```
   → Target: every category's warm median (runs 2–5 of the default five) ≥0.995 (the 100 PageSpeed Insights shows);
```

- [ ] **Step 4: Run it and confirm it passes**
Run: `python3 -m pytest tests/py/test_perf_audit.py -q` → Expected: `29 passed`
Run: `python3 -m pytest tests/py/test_page_board.py -q` → Expected: 0 failed

- [ ] **Step 5: Run the gates**
Run: `npm run -s check:all; echo exit=$?` → Expected: `exit=0`

- [ ] **Step 6: Commit**
```bash
git add scripts/perf_audit.py scripts/pageboard.py tests/py/test_perf_audit.py .claude/skills/bsuk-perf-gate/SKILL.md .claude/agents/bsuk-performance-fixer.md docs/reference/WORKFLOW.md
git commit -m "fix: perf gate runs five times and judges the warm median of runs 2-5

The default was one run, the docs said three or five, and the cold first run was judged.
The record now carries the warm spread and the cold run, and CLS gets a verdict only on
five or more runs. CAG parity audit 19b.5 / M7.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: Doc drift batch (check:all list in CLAUDE.md, emoji path in rules/design.md, WORKFLOW evidence-ledger line, rework_ledger promise in quality_report.py, lessons-doc location, rule-index table-stacking row, LLM 0–10 score claim)

**Closes:** audit Wave 1 item 6 (CAG §19d.8, §20 M9, §21.6, §22.7; Appendix A 1g.3)

Seven places where an instruction had drifted from the repo. Each fix comes with the test that pins it:
1. `CLAUDE.md:255-258` lists the `check:all` chain without `check:outline` → a test pins the sentence to `package.json`.
2. `rules/design.md:28-30` points at `/emoji/bsuk-*.png`, which do not exist → a test fails any pack naming a missing public asset.
3. `docs/reference/WORKFLOW.md:840` calls the evidence ledger empty (it has `parents-dna-clear`) → a test reads every "empty today" row against its file.
4. `scripts/quality_report.py:205` and `data/quality/rework-ledger.json` promise `scripts/rework_ledger.py` (never ported) → a test fails a quality file that names a missing script without saying it was not ported.
5. WORKFLOW Sprint 6 writes lessons to `docs/superpowers/sessions/`, where none has ever been written → lessons go to the gate report's `## Open items`, and a test holds every gate report to having that section.
6. `data/quality/rule-index.json` marks working rule 13 (`tables-three-styles-stacked-on-mobile`) `untested`, though the blocking render check `layout-table-stacks-on-mobile` exists → the row points at it; `tests/py/test_rules_index.py` and CLAUDE.md's ledger paragraph follow.
7. `grill-me/SKILL.md:181-184, 293`, `WORKFLOW.md:177` and `bsuk-keyword-verifier.md:174` promise an LLM Visibility score out of 10; the intel file has one engine and `bsuk_cited` → they report cited / not cited / NOT FETCHED.

**Interface for later tasks:** from this task on, any task that adds a script to `check:all` must update, in the same commit, `package.json`, `tests/py/test_package_scripts.py` (`expected`) **and** the `` `check:all` chains … in that order`` sentence in `CLAUDE.md` — `tests/py/test_doc_drift.py::test_claude_md_lists_the_check_all_chain_package_json_runs` fails otherwise.

**Files:**
- Create: `tests/py/test_doc_drift.py`
- Modify: `tests/py/test_rules_index.py` (line 488, `CLAUDE_MD_RULES[13]`; line 528, the file check)
- Modify: `CLAUDE.md` (lines 97–100, ledger paragraph; lines 255–258, `check:all` sentence)
- Modify: `rules/design.md` (lines 27–31)
- Modify: `docs/reference/WORKFLOW.md` (line 177; line 699; lines 840–841)
- Modify: `scripts/quality_report.py` (line 205)
- Modify: `data/quality/rework-ledger.json` (line 2, `definition`)
- Modify: `data/quality/rule-index.json` (row `tables-three-styles-stacked-on-mobile`, lines 232–238)
- Modify: `.claude/skills/grill-me/SKILL.md` (lines 181, 184, 293)
- Modify: `.claude/agents/bsuk-keyword-verifier.md` (lines 174–175)
- Test: `tests/py/test_doc_drift.py`, `tests/py/test_rules_index.py`

- [ ] **Step 1: Write the failing tests** — `tests/py/test_doc_drift.py`:
```python
"""Stale instructions are wrong instructions (CAG parity audit, Wave 1 item 6).

The agents that build project 5 read CLAUDE.md, the rule packs, WORKFLOW.md and the gate
scripts' own messages as fact. The 2026-09-26 audit found seven places where those texts
had drifted from the repo. Each test below pins one of them to the thing it describes, so
the next drift fails here instead of misleading a builder:

  1. CLAUDE.md's `check:all` sentence lists the chain package.json really runs;
  2. a rule pack names no public asset that is not in public/;
  3. a WORKFLOW.md ledger row that says "empty today" is empty;
  4. a quality script or ledger names no script that does not exist, unless it says so;
  5. Sprint 6 writes the lessons where lessons are really kept, and every gate report has
     that section;
  6. (tests/py/test_rules_index.py) working rule 13's ledger row names its render check;
  7. nothing promises an LLM Visibility score out of 10 — the intel file has one engine
     and a `bsuk_cited` flag, not a score.
"""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLAUDE_MD = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
WORKFLOW = (ROOT / "docs/reference/WORKFLOW.md").read_text(encoding="utf-8")
SCRIPTS = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]


# 1 ─────────────────────────────────────────────────────────────────────────────────────
def test_claude_md_lists_the_check_all_chain_package_json_runs():
    m = re.search(r"`check:all` chains (.*?), in\s+that\s+order", CLAUDE_MD, re.S)
    assert m, "CLAUDE.md lost its `check:all` chains … in that order sentence"
    documented = re.findall(r"`([\w:-]+)`", m.group(1))
    assert documented == re.findall(r"npm run ([\w:-]+)", SCRIPTS["check:all"])


# 2 ─────────────────────────────────────────────────────────────────────────────────────
ASSET = re.compile(r"[\"'`( ](/[A-Za-z0-9_./-]+\.(?:png|webp|svg|jpe?g|avif|gif|ico))\b")


def test_no_rule_pack_names_a_public_asset_that_does_not_exist():
    bad = []
    for f in sorted((ROOT / "rules").glob("*.md")) + [ROOT / "CLAUDE.md"]:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for path in ASSET.findall(line):
                if not (ROOT / "public" / path.lstrip("/")).exists():
                    bad.append(f"{f.relative_to(ROOT)}:{n} {path}")
    assert bad == [], bad


# 3 ─────────────────────────────────────────────────────────────────────────────────────
LEDGER_ROW = re.compile(r"^\| `(data/quality/[\w-]+\.json)` \|.*\bempty today\b", re.M)


def _entries(doc):
    """The list a ledger file keeps its records in."""
    for key in ("claims", "windows", "entries", "rows"):
        if key in doc:
            return doc[key]
    raise AssertionError(f"no known record list in {sorted(doc)}")


def test_a_ledger_workflow_calls_empty_is_empty():
    rows = LEDGER_ROW.findall(WORKFLOW)
    assert rows, "WORKFLOW.md has no ledger rows marked empty — the guard would read nothing"
    full = [p for p in rows if _entries(json.loads((ROOT / p).read_text(encoding="utf-8")))]
    assert full == [], f"WORKFLOW.md calls these ledgers empty, and they are not: {full}"


# 4 ─────────────────────────────────────────────────────────────────────────────────────
SCRIPT_REF = re.compile(r"scripts/[a-z0-9_]+\.py")
HONEST = re.compile(r"(?i)not ported|did not cross|source repo")


def test_quality_files_name_only_scripts_that_exist():
    files = [ROOT / "scripts/quality_report.py"] + sorted((ROOT / "data/quality").glob("*.json"))
    bad = []
    for f in files:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for ref in SCRIPT_REF.findall(line):
                if not (ROOT / ref).exists() and not HONEST.search(line):
                    bad.append(f"{f.relative_to(ROOT)}:{n} {ref}")
    assert bad == [], ("these name a script that does not exist, as if it did — say it was "
                       "not ported, or point at what really does the job:\n  " + "\n  ".join(bad))


# 5 ─────────────────────────────────────────────────────────────────────────────────────
GATE_REPORTS = sorted((ROOT / "docs/reports").glob("*-gate-report.md"))
LESSONS_H2 = re.compile(r"^## (?:Open items|Known Issues open)", re.M)


def test_sprint_6_writes_the_lessons_into_the_gate_report():
    line = next((l for l in WORKFLOW.splitlines() if "Write the lessons" in l), None)
    assert line, "WORKFLOW.md Sprint 6 lost its lessons step"
    assert "docs/reports/" in line and "gate-report" in line, line


@pytest.mark.parametrize("report", GATE_REPORTS, ids=lambda p: p.stem)
def test_every_gate_report_keeps_its_lessons(report):
    assert LESSONS_H2.search(report.read_text(encoding="utf-8")), (
        f"{report.name} has no `## Open items` section — Sprint 6 writes the lessons there")


def test_there_are_gate_reports():
    assert len(GATE_REPORTS) >= 5


# 7 ─────────────────────────────────────────────────────────────────────────────────────
SCORE_OUT_OF_10 = re.compile(r"(?i)LLM Visibility[^\n]{0,60}?(?:\b0\s*[–-]\s*10\b|\d\s*/\s*10\b|\bX\s*/\s*10\b)")


def test_nothing_promises_an_llm_visibility_score_out_of_ten():
    files = (sorted((ROOT / ".claude").rglob("*.md")) + sorted((ROOT / "docs/reference").glob("*.md"))
             + sorted((ROOT / "rules").glob("*.md")) + [ROOT / "CLAUDE.md"])
    bad = [f"{f.relative_to(ROOT)}:{n}  {l.strip()[:100]}" for f in files
           for n, l in enumerate(f.read_text(encoding="utf-8").splitlines(), 1) if SCORE_OUT_OF_10.search(l)]
    assert bad == [], ("no script computes an LLM Visibility score: the intel file "
                       "(docs/research/llm-intel/<slug>-<date>.json) records one engine's answer and "
                       "`bsuk_cited`. Report cited / not cited / NOT FETCHED:\n  " + "\n  ".join(bad))


def test_the_score_lint_fires():
    for line in ('- FILE → report the score (e.g., "LLM Visibility: 3/10 — BSUK is cited")',
                 "- LLM Visibility: [0–10 score | \"not measured\"]",
                 "### LLM Visibility Score: [X/10 | \"not measured\"]"):
        assert SCORE_OUT_OF_10.search(line), line
    assert not SCORE_OUT_OF_10.search("- LLM Visibility: [cited | not cited | NOT FETCHED]")
```
and in `tests/py/test_rules_index.py`, Old (line 488):
```python
    13: ("untested", None),
```
New:
```python
    # the stacking half is a blocking render check; the board half's three styles are proven
    # on the `table` shape by tests/py/test_board_previews.py (CAG parity audit 19d.8)
    13: ("test", "tests/render/checks/layout.ts::layout-table-stacks-on-mobile"),
```
Same file, Old (lines 527–528):
```python
        if test:
            assert (ROOT / test).is_file(), (n, test)
```
New:
```python
        if test:
            assert (ROOT / test.split("::")[0]).is_file(), (n, test)
```

- [ ] **Step 2: Run them and confirm they fail**
Run: `python3 -m pytest tests/py/test_doc_drift.py -q` → Expected: FAIL — `6 failed, 10 passed` (`test_claude_md_lists_the_check_all_chain_package_json_runs`, `test_no_rule_pack_names_a_public_asset_that_does_not_exist`, `test_a_ledger_workflow_calls_empty_is_empty`, `test_quality_files_name_only_scripts_that_exist`, `test_sprint_6_writes_the_lessons_into_the_gate_report`, `test_nothing_promises_an_llm_visibility_score_out_of_ten`)
Run: `python3 -m pytest tests/py/test_rules_index.py -q` → Expected: FAIL — `3 failed, 300 passed` (`test_claude_md_ledger_paragraph_names_the_same_range`, `test_every_working_rule_10_to_17_has_one_ledger_row`, `test_quality_report_reads_the_eight_rows_as_ruled`)

- [ ] **Step 3: Implement the text fixes**

`CLAUDE.md` lines 255–258, Old:
```markdown
`check:all` chains `check:parity`, `check:facts`, `check:links`, `check:verbatim`,
`check:redirects`, `check:schema`, `check:queries`, `check:competitors`, `check:gaps`,
`check:sitemaps`, `check:placeholders`, `check:workflow`, `check:markers` and `agents`, in
that order (`tests/py/test_package_scripts.py` pins it).
```
New:
```markdown
`check:all` chains `check:parity`, `check:facts`, `check:links`, `check:verbatim`,
`check:outline`, `check:redirects`, `check:schema`, `check:queries`, `check:competitors`,
`check:gaps`, `check:sitemaps`, `check:placeholders`, `check:workflow`, `check:markers` and
`agents`, in that order (`tests/py/test_package_scripts.py` pins the chain and
`tests/py/test_doc_drift.py` pins this sentence to it).
```

`CLAUDE.md` lines 98–100, Old:
```markdown
Each has a row in the same file, keyed `claude_md`: 12, 14, 15, 16 and 17 are `enforced: test`
and name the test behind their gate, 10, 11 and 13 are `untested`, and none is a judgment
row, so the cap is untouched.
```
New:
```markdown
Each has a row in the same file, keyed `claude_md`: 12, 13, 14, 15, 16 and 17 are `enforced: test`
and name the test behind their gate, 10 and 11 are `untested`, and none is a judgment
row, so the cap is untouched.
```

`rules/design.md` lines 27–31, Old:
```markdown
   - **Dog icon — NEVER use a generic 🐕 / 🐶 emoji** (it is not a Staffordshire Bull Terrier). Use the custom line-icon SVG set, or the custom images when a filled mark is wanted:
     - Blue Staffy: `<img src="/emoji/bsuk-blue.png" alt="Blue Staffy" class="bsuk-emoji" loading="lazy">`
     - Brindle Staffy: `<img src="/emoji/bsuk-brindle.png" alt="Brindle Staffy" class="bsuk-emoji" loading="lazy">`
     - Large decorative (100px+): `<img src="/emoji/bsuk-blue.png" style="width:Xpx;height:Xpx;object-fit:contain;" alt="" loading="lazy">` — match original font-size value
     - Plain text / email / JS string contexts: use `[BSUK]` as a text marker — HTML img not possible in strings
```
New:
```markdown
   - **Dog icon — NEVER use a generic 🐕 / 🐶 emoji** (it is not a Staffordshire Bull Terrier). Use the line-icon SVG set; when a filled mark is wanted, use the brand mark (`src/components/kit/Mark.astro`). There is no custom dog-emoji image set — the source repo's `/emoji/` images were never ported, and `tests/py/test_doc_drift.py` fails a pack that names a public file that is not there.
     - Plain text / email / JS string contexts: use `[BSUK]` as a text marker — HTML img not possible in strings
```

`docs/reference/WORKFLOW.md` lines 840–841, Old:
```markdown
| `data/quality/evidence-ledger.json` | evidence-pass | `scripts/evidence_audit.py` | Per claim — empty today |
| `data/quality/rework-ledger.json` | learning-loop | `scripts/quality_report.py` | Per rework window — empty today |
```
New:
```markdown
| `data/quality/evidence-ledger.json` | evidence-pass | `scripts/evidence_audit.py` | Per claim — one row today, `parents-dna-clear` at proof NOT FETCHED (Known Issue 40) |
| `data/quality/rework-ledger.json` | learning-loop (appended by hand; the source repo's writer was not ported) | `scripts/quality_report.py` | Per rework window — empty today |
```

Same file, line 699, Old:
```
2. Write the lessons doc       → a dated file under docs/superpowers/sessions/
```
New:
```
2. Write the lessons            → the project's gate report, docs/reports/<project>-gate-report.md,
                                  under `## Open items` (a live defect also gets a Known Issue)
```

Same file, line 177, Old:
```markdown
- LLM Visibility: [0–10 score | "not measured" → run bsuk-llm-keyword-intel]
```
New:
```markdown
- LLM Visibility: [cited | not cited | NOT FETCHED — <reason> (`bsuk_cited` in docs/research/llm-intel/<slug>-<date>.json) | "not measured" → run bsuk-llm-keyword-intel]
```

`.claude/skills/grill-me/SKILL.md` line 293 — the same Old/New pair as WORKFLOW line 177 above.
Same file, line 181. Old: `3. What is the LLM Visibility score for this keyword?`
New: `3. Is BSUK cited by an AI engine for this keyword?`
Same file, line 184. Old:
```markdown
   - FILE → report the score (e.g., "LLM Visibility: 3/10 — BSUK is cited in 1 of 5 AI engines")
```
New:
```markdown
   - FILE → report its `bsuk_cited` for its one `engine` (e.g., "LLM Visibility: not cited — chatgpt, 2026-09-25"). There is no score: one engine is asked per page, so the answer is cited, not cited, or NOT FETCHED with its reason
```

`.claude/agents/bsuk-keyword-verifier.md` lines 174–175, Old:
```markdown
### LLM Visibility Score: [X/10 | "not measured"]
- Recommendation: [if <5: route to @bsuk-non-commodity-content-agent for entity strengthening]
```
New:
```markdown
### LLM Visibility: [cited | not cited | NOT FETCHED — <reason> | "not measured"] (`bsuk_cited` in docs/research/llm-intel/<slug>-<date>.json)
- Recommendation: [if not cited: route to @bsuk-non-commodity-content-agent for entity strengthening]
```

`scripts/quality_report.py` line 205, Old:
```python
        print("   no windows recorded — run scripts/rework_ledger.py --last-30-days (arrives with project 4)")
```
New:
```python
        print("   no windows recorded — append one to data/quality/rework-ledger.json by hand "
              "(bsuk-learning-loop Step 5; the source repo's writer was not ported)")
```

- [ ] **Step 4: Fix the two ledger files** (both round-trip exactly through these dump settings):
```bash
python3 - <<'EOF'
import json
p = "data/quality/rework-ledger.json"
d = json.load(open(p, encoding="utf-8"))
d["definition"] = ("`page_rate` (rework touching src/public) is the headline; `harness_rate` is checker "
                   "self-repair, tracked separately so improving the harness cannot worsen the headline. "
                   "`rate` is the union. Empty at the system transfer: BSUK starts with no measured windows. "
                   "Windows are appended by hand (.claude/skills/bsuk-learning-loop/SKILL.md Step 5); the "
                   "source repo's writer script was not ported, and scripts/quality_report.py reads this file.")
open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")

p = "data/quality/rule-index.json"
d = json.load(open(p, encoding="utf-8"))
row = next(r for r in d["rules"] if r["id"] == "tables-three-styles-stacked-on-mobile")
row["enforced"] = "test"
row["test"] = "tests/render/checks/layout.ts::layout-table-stacks-on-mobile"
row["severity"] = "blocking"
row["_note"] = ("CLAUDE.md working rule 13. The stacking half is the blocking render check "
                "tests/render/checks/layout.ts::layout-table-stacks-on-mobile (every table stacks into labelled "
                "rows below 640px, caption included); the board half is proven on the `table` shape by "
                "tests/py/test_board_previews.py, which offers three rendered styles on its `chrome` axis. "
                "Re-classed from untested on 2026-09-26 (CAG parity audit 19d.8).")
keys = ["id", "family", "enforced", "severity", "claude_md", "test", "_note"]
d["rules"][d["rules"].index(row)] = {k: row[k] for k in keys}
open(p, "w", encoding="utf-8").write(json.dumps(d, indent=1) + "\n")
EOF
```

- [ ] **Step 5: Run them and confirm they pass**
Run: `python3 -m pytest tests/py/test_doc_drift.py -q` → Expected: `16 passed`
Run: `python3 -m pytest tests/py/test_rules_index.py tests/py/test_package_scripts.py tests/py/test_claude_md.py tests/py/test_quality_report.py -q` → Expected: 0 failed (`test_rules_index.py` `303 passed`)
Run: `python3 scripts/quality_report.py | grep -A1 "5. RULES"` → Expected: the deletion-candidate list no longer names `tables-three-styles-stacked-on-mobile`

- [ ] **Step 6: Run the gates**
Run: `npm run -s check:all; echo exit=$?` → Expected: `exit=0`

- [ ] **Step 7: Commit**
```bash
git add tests/py/test_doc_drift.py tests/py/test_rules_index.py CLAUDE.md rules/design.md docs/reference/WORKFLOW.md scripts/quality_report.py data/quality/rework-ledger.json data/quality/rule-index.json .claude/skills/grill-me/SKILL.md .claude/agents/bsuk-keyword-verifier.md
git commit -m "docs: seven drifted instructions corrected and pinned by tests

check:all list gains check:outline; the dead /emoji/ paths go; the evidence ledger is not
empty; no promise of an unported rework_ledger.py; lessons live in the gate report; rule 13
names its blocking render check; no LLM Visibility score out of 10. CAG parity audit, Wave 1
item 6.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Wire global_cta

**Closes:** audit D3 (decision "Global CTA flag")

- [ ] **Step 0: Confirm the ruling on the answer board.** Read the received answers for batch `2026-09-26-brief-parity-two-decisions-before-project-5` — `docs/reference/answer-board/answers/2026-09-26-brief-parity-two-decisions-before-project-5-<date>.md` (saved by the receive procedure in `docs/reference/answer-board/README.md`), question `q02` ("Should the footer's 'Ready to meet the litter?' band obey the board's global CTA setting?"). If the batch is still `open`, stop and ask the controller; do not guess. If `q02` is **(a)**, follow Steps 1–7. If it is **(b)**, follow the (b) paragraph at the end of this task instead.

Eleven of the twelve approved boards set `brief.cta.global_cta: "hidden"` (the thirteenth file, `_demo.json`, is unapproved), and the board Artifact tells the breeder "the site-wide CTA band is hidden on this page" (`scripts/build_page_board.py:765`), but `src/components/kit/SiteFooterKit.astro:75-80` renders `.cta-band` unconditionally. Ruling (a): `PageShell` reads the page's approved record and passes `cta={false}` when it says `hidden`. A page with no approved board — every hub, puppy page, city page, `/kit-preview/` — keeps the band. Measured on the build: the band leaves the eleven `hidden` pages and stays on `/`; no other markup changes; the render harness reads the same before and after (3 pre-existing failures, 57 passed).

**Files:**
- Create: `src/lib/globalCta.ts`
- Create: `tests/py/test_global_cta.py`
- Modify: `src/components/kit/SiteFooterKit.astro` (lines 35–36, props; lines 75–80, the band)
- Modify: `src/layouts/PageShell.astro` (import after line 40; const after line 46; line 76)
- Modify: `.claude/skills/bsuk-cta-strategy/SKILL.md` (new paragraph after line 364, `## Section 22: Footer / Final CTA`)
- Test: `tests/py/test_global_cta.py`

- [ ] **Step 1: Write the failing test** — `tests/py/test_global_cta.py`:
```python
"""An approved board's `global_cta` decides whether the footer's CTA band renders
(CAG parity audit D3; answer-board batch 2026-09-26-brief-parity-two-decisions-before-project-5, ruling (a)).

Every board records `brief.cta.global_cta`, and the board Artifact tells the breeder "the
site-wide CTA band is hidden on this page" when it says `hidden`. Eleven of the twelve
approved boards chose `hidden` — and src/components/kit/SiteFooterKit.astro rendered its
`.cta-band` on every page regardless, so eleven approved boards disagreed with their built pages.
PageShell now reads the page's approved record and passes `cta={false}` to the footer when
the record says `hidden`. A page with no approved board keeps the band.
"""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
BAND = re.compile(r'class="[^"]*\bcta-band\b')


def approved_boards():
    out = []
    for f in sorted((ROOT / "data/boards").glob("*.json")):
        if f.stem.startswith("_"):
            continue
        b = json.loads(f.read_text(encoding="utf-8"))
        if b.get("approval"):
            out.append((b["meta"]["slug"], b["brief"]["cta"]["global_cta"]))
    return out


def built(slug):
    return DIST / ("index.html" if slug == "index" else f"{slug}/index.html")


def test_there_are_approved_boards_of_both_kinds():
    kinds = {g for _, g in approved_boards()}
    assert kinds == {"hidden", "shown"}, kinds


@pytest.mark.parametrize("slug,global_cta", approved_boards())
def test_the_built_page_honours_its_boards_global_cta(slug, global_cta):
    page = built(slug)
    if not page.exists():
        pytest.skip("run npm run build first")
    has_band = bool(BAND.search(page.read_text(encoding="utf-8")))
    assert has_band == (global_cta == "shown"), (slug, global_cta, has_band)


def test_a_page_with_no_board_keeps_the_band():
    page = DIST / "available-puppies/index.html"
    if not page.exists():
        pytest.skip("run npm run build first")
    assert BAND.search(page.read_text(encoding="utf-8"))


def test_the_footer_takes_the_flag_as_a_prop():
    src = (ROOT / "src/components/kit/SiteFooterKit.astro").read_text(encoding="utf-8")
    assert re.search(r"cta\s*=\s*true", src), "SiteFooterKit needs a `cta` prop defaulting to true"
    assert re.search(r"\{cta\s*&&", src), "the band must render only when `cta` is true"
    shell = (ROOT / "src/layouts/PageShell.astro").read_text(encoding="utf-8")
    assert "globalCtaShown" in shell and "<SiteFooterKit slot=\"footer\" cta={" in shell
```

- [ ] **Step 2: Run it and confirm it fails**
Run: `npm run -s build >/dev/null && python3 -m pytest tests/py/test_global_cta.py -q`
Expected: FAIL — `12 failed, 3 passed`: the eleven `test_the_built_page_honours_its_boards_global_cta[<slug>-hidden]` cases (the band is on every built page) and `test_the_footer_takes_the_flag_as_a_prop`; `[index-shown]`, `test_there_are_approved_boards_of_both_kinds` and `test_a_page_with_no_board_keeps_the_band` pass.

- [ ] **Step 3: Implement** — create `src/lib/globalCta.ts`:
```ts
// src/lib/globalCta.ts — does this page's footer render the site-wide CTA band?
//
// Every board record carries `brief.cta.global_cta` ("hidden" | "shown"), and the board
// Artifact shows the breeder that choice in words ("the site-wide CTA band is hidden on this
// page"). Until 2026-09-26 nothing read it: SiteFooterKit rendered its band on every page,
// so eleven approved boards disagreed with their built pages (CAG parity audit D3). The
// record is the page's own approved board, found by route the way scripts/pageboard.py's
// slug_file() names it: `/` is `index`, and a nested route's `/` is flattened to `--`.
// Only an APPROVED record counts; a page with no approved board keeps the band.
// tests/py/test_global_cta.py.
type BoardCta = { approval?: unknown; brief?: { cta?: { global_cta?: string } } };

const RECORDS = import.meta.glob<BoardCta>('../../data/boards/*.json', { eager: true, import: 'default' });

export const boardSlugFor = (pathname: string): string => {
  const slug = pathname.replace(/^\/+|\/+$/g, '');
  return slug === '' ? 'index' : slug;
};

export function globalCtaShown(pathname: string): boolean {
  const file = `../../data/boards/${boardSlugFor(pathname).replace(/\//g, '--')}.json`;
  const record = RECORDS[file];
  if (!record || !record.approval) return true;
  return record.brief?.cta?.global_cta !== 'hidden';
}
```

`src/components/kit/SiteFooterKit.astro` lines 35–36, Old:
```astro
type Props = HTMLAttributes<'footer'>;
const { class: cls, ...rest } = Astro.props;
```
New:
```astro
// `cta` is the page's approved `brief.cta.global_cta` (src/lib/globalCta.ts, via PageShell):
// false when the board said "hidden". It defaults to true, so the kit preview and any page
// without an approved board keep the band.
type Props = HTMLAttributes<'footer'> & { cta?: boolean };
const { class: cls, cta = true, ...rest } = Astro.props;
```
Same file, lines 75–80, Old:
```astro
  <div class="cta-band">
    <div class="container row">
      <p>Ready to meet the litter?</p>
      <Button kind="primary" href="/buy-blue-staffy-puppies-uk/" label="See available puppies" />
    </div>
  </div>
```
New:
```astro
  {cta && (
    <div class="cta-band">
      <div class="container row">
        <p>Ready to meet the litter?</p>
        <Button kind="primary" href="/buy-blue-staffy-puppies-uk/" label="See available puppies" />
      </div>
    </div>
  )}
```

`src/layouts/PageShell.astro` line 40, Old: `import type { SectionRef } from '../lib/sections';`
New:
```astro
import type { SectionRef } from '../lib/sections';
import { globalCtaShown } from '../lib/globalCta';
```
Same file, line 46, Old: `const nav = sections.length >= 6;`
New:
```astro
const nav = sections.length >= 6;
// The approved board's `global_cta` decides the footer's CTA band (CAG parity audit D3).
const cta = globalCtaShown(Astro.url.pathname);
```
Same file, line 76, Old: `  <SiteFooterKit slot="footer" />`
New: `  <SiteFooterKit slot="footer" cta={cta} />`

`.claude/skills/bsuk-cta-strategy/SKILL.md` line 364, Old:
```markdown
## Section 22: Footer / Final CTA
```
New:
```markdown
## Section 22: Footer / Final CTA

**The site-wide band is the board's call.** The footer's CTA band ("Ready to meet the
litter?") renders only when the page's approved board says `brief.cta.global_cta: "shown"`;
`"hidden"` removes it from the built page (`src/lib/globalCta.ts` through
`src/layouts/PageShell.astro`, tested by `tests/py/test_global_cta.py`). Choose `hidden` when
the page already closes on its own final CTA, so the reader is not asked twice in a row.
```

- [ ] **Step 4: Build, run it and confirm it passes**
Run: `npm run -s build >/dev/null; echo build=$?` → Expected: `build=0`
Run: `python3 -m pytest tests/py/test_global_cta.py tests/py/test_design_components.py tests/py/test_agent_facts.py tests/py/test_builder_skills.py -q` → Expected: 0 failed (`test_global_cta.py` `15 passed`; `test_design_components.py` still finds the band in the `/kit-preview/` footer specimen, which has no board)

- [ ] **Step 5: Run the gates**
Run: `npm run -s check:all; echo exit=$?` → Expected: `exit=0`
Run: `npm run test:render:pages` → Expected: `3 failed` (the pre-existing `uk-locations/blue-staffy-puppies-uk` at all three widths), `57 passed`. If a NAV settle-budget timeout appears on another page under the full parallel run, re-run that page alone (`npx playwright test -c tests/render/playwright.config.ts pages.spec.ts -g "<slug>" --project vp768`) before treating it as a defect — it passed 2/2 alone when this plan was verified.

- [ ] **Step 6: Commit**
```bash
git add src/lib/globalCta.ts src/components/kit/SiteFooterKit.astro src/layouts/PageShell.astro .claude/skills/bsuk-cta-strategy/SKILL.md tests/py/test_global_cta.py
git commit -m "feat: the footer CTA band obeys the approved board's global_cta

Eleven approved boards chose hidden and the footer rendered the band anyway. PageShell now
reads the page's approved record; hidden removes the band, and pages without an approved
board keep it. Answer-board ruling (a); CAG parity audit D3.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

- [ ] **Step 7: Keep the page-date map current** — `python3 scripts/generate_page_dates.py --check; echo exit=$?`; if stale, `npm run dates`, then `git add data/page-dates.json` and commit `chore: page dates after the global_cta wiring` with the same trailer.

**If the ruling is (b) — retire the field.** Do not touch `SiteFooterKit.astro` or `PageShell.astro`. Keep `global_cta` in the 13 records (removing the key changes every approved `record_hash` and forces 12 re-approvals), but stop offering it: in `scripts/build_page_board.py` `decisions_lines()` (line 765) print `the site-wide CTA band shows on every page` whatever the value; in `schemas/board.schema.json` give `global_cta` (line 276) `"description": "Retired 2026-09-26 (answer-board ruling b): ignored; the footer band shows on every page."`. Replace `tests/py/test_global_cta.py` with two tests: every built page with a PageShell footer carries `class="cta-band"`, and `decisions_lines()` for a record with `global_cta: "hidden"` does not contain the word `hidden`. Same RED → GREEN → check:all → commit steps, message `fix: retire global_cta — the footer band shows on every page (answer-board ruling b)`.

---

### Task 8: Uniform in-body image box

**Closes:** CAG §15a.1, §15a.2, §15a.4 (decision "In-body image box"); `rules/images.md` `uniform-inbody-image-sizing` moves from `untested` to `test`

- [ ] **Step 0: Confirm the ruling on the answer board.** Read the received answers for batch `2026-09-26-brief-parity-two-decisions-before-project-5` — `docs/reference/answer-board/answers/2026-09-26-brief-parity-two-decisions-before-project-5-<date>.md`, question `q01` ("What box should in-body images use on the new city, comparison and blog pages?"). If the batch is still `open`, stop and ask the controller. If `q01` is **(a)**, follow Steps 1–6. If it is **(b)**, follow the (b) paragraph at the end of this task instead.

`rules/images.md:21-26` describes one box for every in-body image (760px, 1408:768, `object-fit: cover`, the same at every width) and is `enforced: untested`; no CSS in `src/` defines it, and every rebuilt page paints `.bl-img` at its natural ratio, 420px beside the prose (`src/styles/board-styles.css:106-121`, `src/components/BodyImage.astro:43-53`). Ruling (a) builds the box once, in `BodyImage`, for new pages only:

| `box` prop | classes | what it paints |
|---|---|---|
| `natural` (default) | `.bl-img` | unchanged — the twelve built pages keep it until touched |
| `uniform` | `.bl-img.sec-img` | 760px max, 1408:768, `object-fit: cover`, `focal` → `object-position` |
| `tall` | `.bl-img.sec-img.og-tall` | the same box on desktop; 4:5, full width, at 900px and below |

`sizes` defaults to the new `UNIFORM_SIZES` (`(max-width: 800px) 100vw, 760px`) for `uniform`/`tall`. Measured on the build: no built page's markup changes (only the stylesheet grows).

**Interface for Task 14 (W2):** every in-body image keeps `.bl-img`; the uniform box adds `.sec-img`. `layout-h3-image-first` (`tests/render/checks/layout.ts:333-366`) already matches `img.sec-img`, so it will see project 5 pages that use `box="uniform"`/`"tall"`; to also see the natural box on the built pages it must match `img.bl-img`. No rendered page uses the uniform box yet, so no render check of the box itself is added here — the zero-examined guard (Task 11) would fail it; add one with the first project 5 page.

**Files:**
- Create: `tests/py/test_uniform_image_box.py`
- Modify: `src/styles/board-styles.css` (lines 115–122, the media block, plus the new box rules after it)
- Modify: `src/lib/assets.ts` (after line 135, `BODY_SIZES`)
- Modify: `src/components/BodyImage.astro` (header comment after line 25; imports line 27; `Props` lines 29–37; `<img>` line 44)
- Modify: `rules/images.md` (line 22, `enforced:`; new first bullet at line 26)
- Modify: `data/quality/rule-index.json` (row `uniform-inbody-image-sizing`)
- Test: `tests/py/test_uniform_image_box.py`

- [ ] **Step 1: Write the failing test** — `tests/py/test_uniform_image_box.py`:
```python
"""The uniform in-body image box (rules/images.md `uniform-inbody-image-sizing`; CAG §15a;
answer-board batch 2026-09-26-brief-parity-two-decisions-before-project-5, ruling (a)).

rules/images.md has described one box for every in-body image — 760px wide, 1408:768 (16:9),
`object-fit: cover`, the same at every width — since the port, marked `untested`, and no CSS
in src/ defined it: every rebuilt page paints `.bl-img` at its natural ratio, capped at 420px
beside the prose. Rule 17 puts an image under every heading of 30+ project 5 pages, so the
box is built now, once, in src/components/BodyImage.astro:

  box="natural" (default)  .bl-img                 the twelve built pages, frozen until touched
  box="uniform"            .bl-img.sec-img         760px, 1408:768, cover, focal point by prop
  box="tall"               .bl-img.sec-img.og-tall the same box, 4:5 portrait at 900px and below

Every body image keeps `.bl-img`, so a check that looks for in-body images reads one class.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
CSS = (ROOT / "src/styles/board-styles.css").read_text(encoding="utf-8")
BODY = (ROOT / "src/components/BodyImage.astro").read_text(encoding="utf-8")
ASSETS = (ROOT / "src/lib/assets.ts").read_text(encoding="utf-8")
BUILT = json.loads((ROOT / "data/facts/rebuilt.json").read_text(encoding="utf-8"))


def block(selector_rx, text=CSS):
    """The declarations of the first rule whose selector list matches `selector_rx`."""
    m = re.search(selector_rx + r"[^{]*\{([^}]*)\}", text)
    assert m, f"no CSS rule for {selector_rx}"
    return {k.strip(): v.strip() for k, v in
            (d.split(":", 1) for d in m.group(1).split(";") if ":" in d)}


def media(query):
    """Every `@media (<query>)` block of the stylesheet, joined."""
    found = re.findall(r"@media \(" + re.escape(query) + r"\) \{(.*?)\n  \}", CSS, re.S)
    assert found, f"no @media ({query}) block"
    return "\n".join(found)


def test_the_uniform_box_is_760_wide_16_by_9_and_cropped_not_squashed():
    d = block(r"\n  \.bl-img\.sec-img ")
    assert d["max-width"] == "760px"
    assert d["aspect-ratio"] == "1408 / 768"
    assert d["object-fit"] == "cover"
    assert d["height"] == "auto" and d["width"] == "100%"


def test_the_box_never_takes_the_side_media_cap():
    wide = media("min-width: 900px")
    assert re.search(r"\.bl-media-left \.bl-prose > \.bl-img\.sec-img", wide)
    d = block(r"\.bl-media-right \.bl-prose > \.bl-img\.sec-img", wide)
    assert d["max-width"] == "760px" and d["grid-column"] == "1 / -1"


def test_a_portrait_goes_4_by_5_at_900px_and_below():
    d = block(r"\.bl-img\.sec-img\.og-tall", media("max-width: 900px"))
    assert d["aspect-ratio"] == "4 / 5"


def test_body_image_offers_the_three_boxes():
    assert re.search(r"box\?:\s*'natural'\s*\|\s*'uniform'\s*\|\s*'tall'", BODY)
    assert "box = 'natural'" in BODY
    assert "'sec-img'" in BODY and "'og-tall'" in BODY and "'bl-img'" in BODY
    assert "UNIFORM_SIZES" in BODY and "focal" in BODY


def test_uniform_sizes_matches_the_box():
    m = re.search(r"export const UNIFORM_SIZES = '([^']+)';", ASSETS)
    assert m and m.group(1) == "(max-width: 800px) 100vw, 760px"


def test_the_twelve_built_pages_keep_the_natural_box():
    for slug in BUILT:
        page = ROOT / "src/pages" / slug / "index.astro"
        if slug == "index":
            page = ROOT / "src/pages/index.astro"
        assert not re.search(r'box="(?:uniform|tall)"', page.read_text(encoding="utf-8")), slug


def test_the_rule_is_enforced_by_this_file():
    pack = (ROOT / "rules/images.md").read_text(encoding="utf-8")
    assert re.search(r"id: uniform-inbody-image-sizing\nenforced: test\n", pack)
    rows = json.loads((ROOT / "data/quality/rule-index.json").read_text(encoding="utf-8"))["rules"]
    row = next(r for r in rows if r["id"] == "uniform-inbody-image-sizing")
    assert row["enforced"] == "test" and row["test"] == "tests/py/test_uniform_image_box.py", row
```

- [ ] **Step 2: Run it and confirm it fails**
Run: `python3 -m pytest tests/py/test_uniform_image_box.py -q`
Expected: FAIL — `6 failed, 1 passed` (`AssertionError: no CSS rule for …\.bl-img\.sec-img` and friends); `test_the_twelve_built_pages_keep_the_natural_box` passes.

- [ ] **Step 3: Implement the box** — `src/styles/board-styles.css` lines 115–122, Old:
```css
  .bl-prose > .bl-img { grid-column: 1 / -1; }
  .bl-media-top .bl-prose > .bl-img { order: -1; }
  @media (min-width: 900px) {
    .bl-media-right .bl-prose > .bl-img,
    .bl-media-left .bl-prose > .bl-img { max-width: 420px; grid-column: auto; }
    .bl-media-left .bl-prose > .bl-img { order: -1; justify-self: start; }
    .bl-media-right .bl-prose > .bl-img { order: 99; justify-self: end; }
  }
```
New:
```css
  .bl-prose > .bl-img { grid-column: 1 / -1; }
  .bl-media-top .bl-prose > .bl-img { order: -1; }
  @media (min-width: 900px) {
    .bl-media-right .bl-prose > .bl-img,
    .bl-media-left .bl-prose > .bl-img { max-width: 420px; grid-column: auto; }
    .bl-media-left .bl-prose > .bl-img { order: -1; justify-self: start; }
    .bl-media-right .bl-prose > .bl-img { order: 99; justify-self: end; }
    /* The uniform box never takes the 420px side cap: its size is the whole point. */
    .bl-media-left .bl-prose > .bl-img.sec-img,
    .bl-media-right .bl-prose > .bl-img.sec-img { max-width: 760px; grid-column: 1 / -1; justify-self: center; }
  }

  /* THE UNIFORM BOX (rules/images.md `uniform-inbody-image-sizing`; answer-board ruling (a),
     2026-09-26). A project 5 page paints every in-body image — photo or infographic — in ONE
     rectangle: 760px wide, 1408:768 (16:9), cropped by `object-fit: cover` rather than
     squashed, the same at every width. BodyImage's `focal` prop moves the crop, never the box.
     A fixed ratio reserves its height before the file arrives, so it cannot shift the page.
     The twelve pages built before project 5 keep the natural `.bl-img` until they are touched.
     tests/py/test_uniform_image_box.py. */
  .bl-img.sec-img {
    width: 100%;
    max-width: 760px;
    aspect-ratio: 1408 / 768;
    height: auto;
    object-fit: cover;
    margin-inline: auto;
  }
  /* A portrait (`box="tall"`) keeps the box on desktop and turns 4:5 on a phone or a tablet,
     full width, so a standing dog is not cropped to its shoulders. */
  @media (max-width: 900px) {
    .bl-img.sec-img.og-tall { aspect-ratio: 4 / 5; max-width: 100%; }
  }
```

`src/lib/assets.ts` line 135, Old:
```ts
export const BODY_SIZES = '(max-width: 640px) 100vw, 420px';
```
New:
```ts
export const BODY_SIZES = '(max-width: 640px) 100vw, 420px';

/**
 * The `sizes` of the uniform box (`.bl-img.sec-img`, BodyImage `box="uniform"` or `"tall"`):
 * 760px wide wherever the column allows it, the full column below that. 800px is 760 plus
 * the column's two 20px gutters, so above it the box is at its cap.
 */
export const UNIFORM_SIZES = '(max-width: 800px) 100vw, 760px';
```

`src/components/BodyImage.astro` lines 25–38, Old:
```astro
// drift apart from the file they measure.
import type { FilledAsset } from '../lib/assets';
import { BODY_SIZES } from '../lib/assets';

interface Props {
  /** The record's baked row: original path, original alt, measured intrinsic size. */
  asset: FilledAsset;
  /** Candidate list, for a master wide enough to need one. Omitted renders no `srcset`. */
  srcset?: string;
  /** The box the photo paints, for a page whose prose column is not `PageShell`'s. */
  sizes?: string;
}
const { asset, srcset, sizes = BODY_SIZES } = Astro.props;
---
```
New:
```astro
// drift apart from the file they measure.
//
// THE BOX (rules/images.md `uniform-inbody-image-sizing`, 2026-09-26). `natural` is the
// twelve built pages' `.bl-img`: natural ratio, 420px beside the prose. `uniform` is the
// project 5 box: `.bl-img.sec-img`, 760px at 1408:768, cropped with `object-fit: cover`.
// `tall` is that box for a portrait, which turns 4:5 at 900px and below (`.og-tall`). Every
// body image keeps `.bl-img`, so a check that looks for in-body images reads one class.
import type { FilledAsset } from '../lib/assets';
import { BODY_SIZES, UNIFORM_SIZES } from '../lib/assets';

interface Props {
  /** The record's baked row: original path, original alt, measured intrinsic size. */
  asset: FilledAsset;
  /** Candidate list, for a master wide enough to need one. Omitted renders no `srcset`. */
  srcset?: string;
  /** The box the photo paints, for a page whose prose column is not `PageShell`'s. */
  sizes?: string;
  /** Which box: the built pages' natural `.bl-img`, or project 5's uniform box. */
  box?: 'natural' | 'uniform' | 'tall';
  /** The crop's focal point in the uniform box, as `object-position` (e.g. "50% 30%"). */
  focal?: string;
}
const { asset, srcset, box = 'natural', focal } = Astro.props;
const sizes = Astro.props.sizes ?? (box === 'natural' ? BODY_SIZES : UNIFORM_SIZES);
const cls = ['bl-img', box !== 'natural' && 'sec-img', box === 'tall' && 'og-tall'];
const style = box !== 'natural' && focal ? `object-position: ${focal}` : undefined;
---
```
Same file, line 44, Old:
```astro
  class="bl-img"
  src={asset.file}
```
New:
```astro
  class:list={cls}
  style={style}
  src={asset.file}
```

- [ ] **Step 4: Record the rule as built** — `rules/images.md` line 22, Old: `enforced: untested` (the block whose `id:` is `uniform-inbody-image-sizing`) → New: `enforced: test`. Same file, line 26, Old (the start of the bullet):
```markdown
- **Uniform in-body image sizing (ALWAYS — locked 2026-07-12) — applies to comparison + long-form content pages and every image agent/skill** —
```
New (a new first bullet, then the unchanged original):
```markdown
- **BSUK's box (answer-board ruling (a), 2026-09-26).** The box below is built once, in `src/components/BodyImage.astro`: a project 5 page (location, comparison, blog) renders every in-body image with `box="uniform"` — `.bl-img.sec-img`, `max-width: 760px; aspect-ratio: 1408 / 768; object-fit: cover; height: auto` — and a portrait with `box="tall"`, which adds `.og-tall` and turns 4:5, full width, at 900px and below. `focal` sets `object-position`; `sizes` defaults to `UNIFORM_SIZES` (`src/lib/assets.ts`). The twelve pages built before project 5 keep the natural `.bl-img` (420px beside the prose) until they are touched. Held up by `tests/py/test_uniform_image_box.py`.
- **Uniform in-body image sizing (ALWAYS — locked 2026-07-12) — applies to comparison + long-form content pages and every image agent/skill** —
```
Then the ledger row:
```bash
python3 - <<'EOF'
import json
p = "data/quality/rule-index.json"
d = json.load(open(p, encoding="utf-8"))
i = next(i for i, r in enumerate(d["rules"]) if r["id"] == "uniform-inbody-image-sizing")
d["rules"][i] = {"id": "uniform-inbody-image-sizing", "family": "IMG", "enforced": "test",
                 "pack": "rules/images.md", "test": "tests/py/test_uniform_image_box.py",
                 "_note": "Built 2026-09-26 (answer-board ruling (a), CAG parity audit §15a): BodyImage box=\"uniform\" / \"tall\" and the .bl-img.sec-img / .og-tall rules in src/styles/board-styles.css, for project 5 pages; the twelve built pages keep the natural .bl-img."}
open(p, "w", encoding="utf-8").write(json.dumps(d, indent=1) + "\n")
EOF
```

- [ ] **Step 5: Build, run it and confirm it passes**
Run: `npm run -s build >/dev/null; echo build=$?` → Expected: `build=0`
Run: `python3 -m pytest tests/py/test_uniform_image_box.py -q` → Expected: `7 passed`
Run: `python3 -m pytest tests/py/test_rules_index.py tests/py/test_images.py tests/py/test_quality_report.py -q` → Expected: 0 failed
Run: `npm run -s check:all; echo exit=$?` → Expected: `exit=0`
Run: `npm run test:render:pages` → Expected: `3 failed` (pre-existing, `uk-locations/blue-staffy-puppies-uk`), `57 passed` — no built page's markup changed.

- [ ] **Step 6: Commit**
```bash
git add src/styles/board-styles.css src/lib/assets.ts src/components/BodyImage.astro rules/images.md data/quality/rule-index.json tests/py/test_uniform_image_box.py
git commit -m "feat: the uniform in-body image box for project 5 pages

BodyImage box=\"uniform\" paints .bl-img.sec-img at 760px, 1408:768, object-fit cover, with
a focal point; box=\"tall\" turns 4:5 at 900px and below. The twelve built pages keep the
natural .bl-img. uniform-inbody-image-sizing is now enforced: test. Answer-board ruling (a).

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```
Then `python3 scripts/generate_page_dates.py --check`; if stale, `npm run dates` and commit `data/page-dates.json` alone (`chore: page dates after the image box`, same trailer).

**If the ruling is (b) — keep `.bl-img` and enforce `sizes`.** Do not touch `BodyImage.astro`'s box or `board-styles.css`. Rewrite the `uniform-inbody-image-sizing` rule in `rules/images.md` as a recorded deliberate difference (BSUK keeps `.bl-img`: full width, natural ratio, 420px beside the prose from 900px up), keep it `enforced: test`, and point its ledger row at a new `tests/py/test_body_image_sizes.py` that (1) parses the `max-width: 420px` cap out of `src/styles/board-styles.css` and asserts `BODY_SIZES` in `src/lib/assets.ts` names that cap and the 640px breakpoint, and (2) asserts every built `<img class="bl-img"…>` in `dist/` carries `sizes` equal to `BODY_SIZES` or an explicit per-page value from its source file. Tell Task 14 that the H3 image-first check must match `img.bl-img`, because no `.sec-img` will exist. Same RED → GREEN → check:all → commit steps, message `fix: record .bl-img as the in-body box and enforce its sizes (answer-board ruling b)`.

---

## Wave 2 — Make the gates see project 5 pages (Tasks 9–16)

### Task 9: Retired-facts sweep over data/, src/, dist/ (new check in check:all)

Audit D5 / Wave 2 row 7 / Appendix A 1a.2; Known Issue 65. The fact lint reads only the
instruction tree, so eleven indexable city pages printing a retired delivery fee, a retired
price band, "non-refundable", "council-licensed" and the former city were found by hand.
This task adds `npm run check:retired` to `check:all`.

**It would FAIL today on Known Issue 65's content**, so it lands green with a dated, named
allowlist — `data/quality/retired-facts-allowlist.json`, **48 entries**, every one a
migrated city body (`data/locations.json`) or the city page built from it. The allowlist
only shrinks, three ways: (1) a finding not on it FAILs; (2) an entry that no longer fires
FAILs as `allowlist-stale` until it is deleted, so each project 5 city rebuild must delete
its own entries; (3) `tests/py/test_retired_facts_check.py` pins `ALLOWLIST_CEILING = 48`
and refuses any rebuilt page (data/facts/rebuilt.json) on the list. Project 5 burns it down
to zero.

Scope and exemptions, all in the script's docstring: dist/ is every built page minus the
specimen routes (visible text plus JSON-LD); data/ is `data/locations.json` field by field
plus settings, puppies, price matrix, FAQ and reviews (boards, facts and verbatim record
retired wording ON PURPOSE in `dropped.*` and only matter if they render, which dist/
judges); src/ is read with comments stripped, and the one sanctioned spelling of the retired
word in code — the false branch of `deposit_refundable ? 'refundable' : 'non-refundable'` on
the LOCKED setting — is exempt. The locked £ set is read from `data/settings.json` and
`data/price-matrix.json`: deposit, both prices, both balances (price less deposit), the
delivery band ends, the two ranges and £0 (collection). Trade-off, stated in the docstring:
a retired single figure that equals a locked balance (£1,000 / £1,200) passes alone; the
retired band around it still fails, and every page carrying one is already on the list.

**Files:**
- Create: `scripts/retired_facts_check.py`
- Create: `data/quality/retired-facts-allowlist.json`
- Create: `tests/py/test_retired_facts_check.py`
- Modify: `package.json` (scripts: add `check:retired`; `check:all` chain)
- Modify: `tests/py/test_package_scripts.py` (`test_the_check_all_chain_is_the_documented_one`)
- Modify: `CLAUDE.md` (the "`check:all` chains …" sentence under "Gates — run these")
- Modify: `scripts/build_system_registry.py` (`GATES`), regenerate `docs/reference/system-registry.md`

- [ ] **Step 1: Write the failing test**

Create `tests/py/test_retired_facts_check.py`:

```python
"""`scripts/retired_facts_check.py` — the retired-facts sweep over dist/, data/ and src/.

Audit D5 / Known Issue 65: the fact lint reads the instruction tree only, so eleven indexable
city pages printing retired figures and wording were found by hand. These tests hold the
sweep's predicate on a scratch tree, and hold the allowlist of today's offenders to the one
direction it may move: down.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import retired_facts_check as R  # noqa: E402

# The offenders live on 2026-09-26 (Known Issue 65). Project 5 burns this down; raising it
# is a new retired fact, and that is what the gate exists to refuse.
ALLOWLIST_CEILING = 48

LOCKED = ({0, 500, 1500, 1700, 1000, 1200, 200, 350}, {(200, 350), (1500, 1700)})


def _tree(tmp_path, pages=None, rows=None, src=None):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/settings.json").write_text(json.dumps(
        {"deposit_gbp": 500, "delivery_min_gbp": 200, "delivery_max_gbp": 350}), encoding="utf-8")
    (tmp_path / "data/price-matrix.json").write_text(json.dumps(
        {"male_gbp": 1500, "female_gbp": 1700, "deposit_gbp": 500}), encoding="utf-8")
    (tmp_path / "data/locations.json").write_text(json.dumps(rows or []), encoding="utf-8")
    for key, markup in (pages or {"index": "<p>Hello</p>"}).items():
        d = tmp_path / "dist" if key == "index" else tmp_path / "dist" / key
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(markup, encoding="utf-8")
    (tmp_path / "src").mkdir()
    for rel, code in (src or {"pages/a.astro": "<p>ok</p>"}).items():
        (tmp_path / "src" / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "src" / rel).write_text(code, encoding="utf-8")
    return tmp_path


def test_the_locked_set_is_read_from_the_data_files():
    singles, ranges = R.locked_amounts(ROOT)
    s = json.loads((ROOT / "data/settings.json").read_text())
    p = json.loads((ROOT / "data/price-matrix.json").read_text())
    assert {p["male_gbp"], p["female_gbp"], p["deposit_gbp"], s["delivery_min_gbp"],
            s["delivery_max_gbp"], 0} <= singles
    assert p["male_gbp"] - p["deposit_gbp"] in singles        # the balance is arithmetic, not new
    assert (s["delivery_min_gbp"], s["delivery_max_gbp"]) in ranges
    assert (p["male_gbp"], p["female_gbp"]) in ranges


@pytest.mark.parametrize("text", ["£1,500", "£1500 - £1700", "£200–£350", "£0 to collect",
                                  "a £500 deposit, refundable", "£1,500–£1,700."])
def test_locked_amounts_pass(text):
    assert R.amount_findings(text, LOCKED) == []


@pytest.mark.parametrize("text,found", [("Ground Transport — £100", ["£100"]),
                                        ("from £850 - £1,200", ["£850–£1,200"]),
                                        ("£1,000–£1,100 each", ["£1,000–£1,100"]),
                                        ("£200 to £300", ["£300"])])
def test_retired_amounts_fail(text, found):
    assert R.amount_findings(text, LOCKED) == found


def test_retired_wording_fails_in_any_case():
    found = R.html_findings("<p>A Non-Refundable deposit from a council licensed breeder.</p>", LOCKED)
    assert found == [("term", "non-refundable"), ("term", "council-licensed")]


def test_the_former_city_fails_in_prose_but_not_as_a_link_to_its_own_page():
    link = '<li><a href="/uk-locations/staffy-puppies-for-sale-glasgow/">Glasgow</a></li>'
    assert R.html_findings(link, LOCKED) == []
    assert R.html_findings("<p>collect from our Glasgow home</p>" + link, LOCKED) == [("city", "Glasgow")]
    # The city's own page may name the city it is about.
    assert R.html_findings("<p>puppies in Glasgow</p>", LOCKED, city_page=True) == []


def test_json_ld_is_read_and_other_scripts_are_not():
    ld = '<script type="application/ld+json">{"priceRange":"£850 - £1,200"}</script>'
    js = '<script>const retired = "£850";</script>'
    assert R.html_findings(ld, LOCKED) == [("amount", "£850–£1,200")]
    assert R.html_findings(js + "<style>.a{content:'£9'}</style>", LOCKED) == []


def test_src_comments_are_history_and_code_is_copy(tmp_path):
    root = _tree(tmp_path, src={
        "pages/a.astro": "---\n// the old £850 band is dropped\nconst url = 'https://x.test/£5';\n---\n"
                         "{/* non-refundable */}<!-- council-licensed --><p>ok</p>",
        "lib/faq.ts": "const t = settings.deposit_refundable ? 'refundable' : 'non-refundable';\n",
        "pages/b.astro": "<p>A £300 deposit</p>"})
    found, n = R.scan_src(root, LOCKED)
    assert n == 3
    assert sorted(found) == ["src:src/pages/a.astro:amount:£5", "src:src/pages/b.astro:amount:£300"]


def test_run_reports_new_allowed_and_stale(tmp_path):
    root = _tree(tmp_path, pages={
        "index": "<p>£1,500</p>",
        "uk-locations/blue-staffy-puppies-hull": "<p>Ground Transport — £100</p>",
        "uk-locations/blue-staffy-puppies-york": "<p>a non-refundable deposit</p>",
        "kit-preview": "<p>£999 specimen</p>"},
        rows=[{"slug": "blue-staffy-puppies-hull", "title": "Hull", "h1": "Hull",
               "description": "Glasgow breeders", "body_html": "<p>£100</p>"}])
    allow = tmp_path / "allow.json"
    allow.write_text(json.dumps({"entries": {
        "dist:uk-locations/blue-staffy-puppies-hull:amount:£100": "KI 65",
        "dist:uk-locations/blue-staffy-puppies-leeds:amount:£100": "KI 65"}}), encoding="utf-8")
    r = R.run(root=root, allowlist=allow)
    assert r["examined"] == {"dist": 3, "data": 6, "src": 1}      # kit-preview is a specimen
    assert r["allowed"] == ["dist:uk-locations/blue-staffy-puppies-hull:amount:£100"]
    assert r["new"] == ["data:locations.json/blue-staffy-puppies-hull/body_html:amount:£100",
                        "data:locations.json/blue-staffy-puppies-hull/description:city:Glasgow",
                        "dist:uk-locations/blue-staffy-puppies-york:term:non-refundable"]
    assert r["stale"] == ["dist:uk-locations/blue-staffy-puppies-leeds:amount:£100"]


def test_no_dist_is_not_a_pass(tmp_path):
    root = _tree(tmp_path)
    import shutil
    shutil.rmtree(root / "dist")
    with pytest.raises(FileNotFoundError):
        R.run(root=root, allowlist=tmp_path / "none.json")


# ── the real allowlist ────────────────────────────────────────────────────────────────────
def _allow():
    return json.loads(R.ALLOWLIST.read_text(encoding="utf-8"))


def test_the_allowlist_only_shrinks():
    entries = _allow()["entries"]
    assert len(entries) <= ALLOWLIST_CEILING, (
        f"{len(entries)} allowlisted retired facts, ceiling {ALLOWLIST_CEILING}: a new retired "
        "fact is fixed on the page, never added to the allowlist")


def test_every_entry_is_known_issue_65_and_dated():
    doc = _allow()
    assert doc["known_issue"] == 65 and doc["since"] == "2026-09-26"
    for key, reason in doc["entries"].items():
        assert key.split(":", 1)[0] in ("dist", "data", "src"), key
        assert "Known Issue 65" in reason, key


def test_no_rebuilt_page_is_ever_allowlisted():
    rebuilt = set(json.loads((ROOT / "data/facts/rebuilt.json").read_text()))
    for key in _allow()["entries"]:
        where = key.split(":")[1]
        page = where.split("/")[-1] if key.startswith("dist:") else where.split("/")[1] \
            if where.startswith("locations.json/") else where
        assert page not in rebuilt, f"{key}: a rebuilt page fixes its retired facts, it is never excused"


@pytest.mark.skipif(not (ROOT / "dist").exists(), reason="needs a build (npm run build)")
def test_the_repo_sweep_is_green_and_the_allowlist_is_exact():
    r = R.run()
    assert r["new"] == [], r["new"]
    assert r["stale"] == [], r["stale"]
    assert len(r["allowed"]) == len(_allow()["entries"])
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 -m pytest tests/py/test_retired_facts_check.py -q -p no:cacheprovider`
Expected: FAIL — `E   ModuleNotFoundError: No module named 'retired_facts_check'`, `1 error during collection`.

- [ ] **Step 3: Write the sweep**

Create `scripts/retired_facts_check.py`:

```python
#!/usr/bin/env python3
"""retired_facts_check.py — no retired fact on a built page, in rendered data or in src/.

The fact lint (tests/py/test_agent_facts.py) reads the instruction tree only: agents,
skills and docs/reference. Nothing read what SHIPS, so Known Issue 65 — eleven indexable
city pages printing a retired delivery fee, a retired price band, a "non-refundable"
deposit, collection from the former city and "council-licensed" — was found by hand. This
gate sweeps both tenses of the site (audit D5):

  dist      every built page (dist/**/index.html) minus the specimen routes, visible text
            plus JSON-LD
  data      the data files pages render facts from: data/locations.json (field by field,
            per city row), settings, puppies, price matrix, FAQ and reviews
  src       src/**/*.{astro,ts,tsx,js,mjs,md,mdx} with comments stripped — a comment that
            records a dropped figure is history, not copy

and fails on
  amount    a £ figure whose value is not locked: the deposit, the two prices, the two
            balances (price less deposit), the delivery band ends, the two locked ranges and
            £0 (collection is free); values are read from data/settings.json and
            data/price-matrix.json, never typed here. Trade-off: a retired figure that
            happens to equal a locked one (a balance) passes on its own — the retired band
            it sits in still fails
  term      "non-refundable", "council-licensed" / "council licensed"
  city      the former city (Known Issue 16) anywhere but its own two city pages and the
            anchor text of a link to one of them

WHAT IS NOT SCANNED, and why. data/boards/, data/facts/ and data/verbatim/ record retired
wording ON PURPOSE (`dropped.prices` is the accounting of what a rebuild struck); a figure
there only matters if it renders, and dist/ is where rendering is judged. data/queries/raw/
is competitor SERP text.

THE ALLOWLIST. data/quality/retired-facts-allowlist.json names every offender that was live
on 2026-09-26 (Known Issue 65) — the migrated city bodies project 5 rewrites. It exists so
this gate can enter check:all green today and still fail the first NEW retired fact. It only
shrinks: an entry that no longer fires is a FAIL too (remove it), a rebuilt page can never
carry one, and tests/py/test_retired_facts_check.py pins its ceiling.

Exit 1 on any finding outside the allowlist or any stale entry, 2 when dist/ is missing.
Usage: python3 scripts/retired_facts_check.py [--json]   |   npm run check:retired
"""
import html.parser
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ALLOWLIST = ROOT / "data" / "quality" / "retired-facts-allowlist.json"

SPECIMEN_PREFIXES = ("board-preview/", "kit-preview/")
FORMER_CITY = "Glasgow"
FORMER_CITY_SLUGS = ("staffy-breeding-dogs-glasgow", "staffy-puppies-for-sale-glasgow")
TERMS = re.compile(r"(?i)\bnon-refundable\b|\bcouncil[- ]licensed\b")
AMOUNT = r"£\d[\d,]*(?<![,])"
MONEY = re.compile(AMOUNT + r"(?:\s*[–—-]\s*" + AMOUNT + r")?")
RENDERED_DATA = ("settings.json", "puppies.json", "price-matrix.json", "faq.json", "reviews.json")
LOCATION_FIELDS = ("title", "h1", "description", "body_html")
SRC_SUFFIXES = {".astro", ".ts", ".tsx", ".js", ".mjs", ".md", ".mdx"}
# The one sanctioned spelling of the retired word in code: the false branch of a ternary on
# the LOCKED setting (data/settings.json deposit_refundable: true), so it never renders.
REFUNDABLE_TERNARY = re.compile(
    r"deposit_refundable\s*\?\s*(['\"`])refundable\1\s*:\s*(['\"`])non-refundable\2")


def locked_amounts(root=ROOT):
    """({single values}, {(low, high) ranges}) — every £ figure the site may print."""
    s = json.loads((root / "data" / "settings.json").read_text(encoding="utf-8"))
    p = json.loads((root / "data" / "price-matrix.json").read_text(encoding="utf-8"))
    singles = {0, s["deposit_gbp"], p["deposit_gbp"], p["male_gbp"], p["female_gbp"],
               p["male_gbp"] - p["deposit_gbp"], p["female_gbp"] - p["deposit_gbp"],
               s["delivery_min_gbp"], s["delivery_max_gbp"]}
    ranges = {(s["delivery_min_gbp"], s["delivery_max_gbp"]),
              (min(p["male_gbp"], p["female_gbp"]), max(p["male_gbp"], p["female_gbp"]))}
    return singles, ranges


def _value(token):
    return int(token.replace("£", "").replace(",", ""))


def amount_findings(text, locked):
    """Every £ figure (or range) in `text` that is not locked, spelled as found."""
    singles, ranges = locked
    out = []
    for m in MONEY.finditer(text):
        parts = re.findall(AMOUNT, m.group(0))
        vals = tuple(_value(x) for x in parts)
        ok = vals[0] in singles if len(vals) == 1 else vals in ranges
        if not ok:
            out.append(re.sub(r"\s*[–—-]\s*", "–", m.group(0).strip()))
    return out


class _Text(html.parser.HTMLParser):
    """Visible text plus JSON-LD. Text inside <a> whose href names one of the former city's
    own pages is collected apart, because naming the city a page is ABOUT is not a claim."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip, self.city_link = [], 0, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "style" or (tag == "script" and a.get("type") != "application/ld+json"):
            self.skip += 1
        if tag == "a" and any(s in (a.get("href") or "") for s in FORMER_CITY_SLUGS):
            self.city_link += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script") and self.skip:
            self.skip -= 1
        if tag == "a" and self.city_link:
            self.city_link -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(("link" if self.city_link else "text", data))


def html_findings(markup, locked, city_page=False):
    p = _Text()
    p.feed(markup)
    text = " ".join(d for _, d in p.parts)
    plain = " ".join(d for kind, d in p.parts if kind == "text")
    return text_findings(text, locked, city=not city_page, city_text=plain)


def text_findings(text, locked, city=True, city_text=None):
    """[(kind, value)] for one blob. `city=False` switches the former-city rule off (the
    city's own page); `city_text` is what that rule reads when it is not `text` itself."""
    found = [("amount", a) for a in amount_findings(text, locked)]
    found += [("term", m.group(0).lower().replace(" ", "-")) for m in TERMS.finditer(text)]
    if city and FORMER_CITY in (text if city_text is None else city_text):
        found.append(("city", FORMER_CITY))
    return found


def strip_comments(src, suffix):
    """Code minus its comments: // and /* */ in script, {/* */} and <!-- --> in markup.
    A `//` inside a string or URL (`'https://…'`) is kept: it must follow a line start or
    whitespace and not a quote or a colon."""
    if suffix in (".md", ".mdx"):
        return re.sub(r"<!--.*?-->", " ", src, flags=re.S)
    src = re.sub(r"\{/\*.*?\*/\}", " ", src, flags=re.S)
    src = re.sub(r"<!--.*?-->", " ", src, flags=re.S)
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    return re.sub(r"(?m)(^|\s)//.*$", r"\1", src)


def scan_dist(dist, locked):
    out, n = {}, 0
    for page in sorted(pathlib.Path(dist).glob("**/index.html")):
        rel = page.parent.relative_to(dist).as_posix()
        key = "index" if rel == "." else rel
        if (key + "/").startswith(SPECIMEN_PREFIXES):
            continue
        n += 1
        city_page = key.split("/")[-1] in FORMER_CITY_SLUGS
        for kind, value in html_findings(page.read_text(encoding="utf-8"), locked, city_page):
            out.setdefault(f"dist:{key}:{kind}:{value}", 0)
            out[f"dist:{key}:{kind}:{value}"] += 1
    return out, n


def scan_data(root, locked):
    out, n = {}, 0
    rows = json.loads((root / "data" / "locations.json").read_text(encoding="utf-8"))
    for row in rows:
        city_page = row["slug"] in FORMER_CITY_SLUGS
        for field in LOCATION_FIELDS:
            n += 1
            value = row.get(field) or ""
            found = (html_findings(value, locked, city_page) if field == "body_html"
                     else text_findings(value, locked, city=not city_page))
            for kind, v in found:
                k = f"data:locations.json/{row['slug']}/{field}:{kind}:{v}"
                out[k] = out.get(k, 0) + 1
    for name in RENDERED_DATA:
        path = root / "data" / name
        if not path.exists():
            continue
        n += 1
        for kind, v in text_findings(path.read_text(encoding="utf-8"), locked):
            k = f"data:{name}:{kind}:{v}"
            out[k] = out.get(k, 0) + 1
    return out, n


def scan_src(root, locked):
    out, n = {}, 0
    for path in sorted((root / "src").rglob("*")):
        if not path.is_file() or path.suffix not in SRC_SUFFIXES:
            continue
        n += 1
        code = REFUNDABLE_TERNARY.sub(" ", strip_comments(path.read_text(encoding="utf-8"), path.suffix))
        for kind, v in text_findings(code, locked):
            k = f"src:{path.relative_to(root).as_posix()}:{kind}:{v}"
            out[k] = out.get(k, 0) + 1
    return out, n


def load_allowlist(path=ALLOWLIST):
    if not pathlib.Path(path).exists():
        return {}
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8")).get("entries", {})


def run(root=ROOT, dist=None, allowlist=None):
    """{'examined': {...}, 'new': [...], 'allowed': [...], 'stale': [...]}; raises
    FileNotFoundError when dist/ is missing — a sweep of no pages is not a pass."""
    root = pathlib.Path(root)
    dist = root / "dist" if dist is None else pathlib.Path(dist)
    if not dist.exists():
        raise FileNotFoundError(f"{dist} does not exist — build first (npm run build)")
    locked = locked_amounts(root)
    found, examined = {}, {}
    for scope, fn in (("dist", lambda: scan_dist(dist, locked)),
                      ("data", lambda: scan_data(root, locked)),
                      ("src", lambda: scan_src(root, locked))):
        f, n = fn()
        found.update(f)
        examined[scope] = n
    allowed = load_allowlist(ALLOWLIST if allowlist is None else allowlist)
    return {"examined": examined,
            "new": sorted(k for k in found if k not in allowed),
            "allowed": sorted(k for k in found if k in allowed),
            "stale": sorted(k for k in allowed if k not in found)}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        r = run()
    except FileNotFoundError as e:
        print(f"retired-facts ERROR {e}")
        return 2
    ex = r["examined"]
    print(f"retired-facts: examined {ex['dist']} built pages, {ex['data']} data fields/files, "
          f"{ex['src']} src files; {len(r['allowed'])} allowlisted (Known Issue 65), "
          f"{len(r['new'])} new, {len(r['stale'])} stale")
    if 0 in ex.values():
        print("  FAIL examined-zero: a scope examined nothing, which is not a pass")
    for k in r["new"]:
        print(f"  FAIL retired-fact {k}")
    for k in r["stale"]:
        print(f"  FAIL allowlist-stale {k} no longer fires — remove it from "
              f"{ALLOWLIST.relative_to(ROOT)} (the list only shrinks)")
    if "--json" in argv:
        out = ROOT / "docs" / "reports" / "retired-facts.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    return 1 if (r["new"] or r["stale"] or 0 in ex.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Build, then see today's offenders**

Run: `npm run -s build && python3 scripts/retired_facts_check.py; echo "exit=$?"`
Expected: `retired-facts: examined 51 built pages, 117 data fields/files, 69 src files; 0 allowlisted (Known Issue 65), 48 new, 0 stale`, 48 `FAIL retired-fact …` lines (all `data:locations.json/<city>/body_html:…` or `dist:uk-locations/<city>:…`, cities Aberdeen, Dundee, Edinburgh, Hull, Inverness, Middlesbrough, Oxford, Sunderland, York, the UK hub and `staffy-breeding-dogs-glasgow`), `exit=1`. If the list differs, an earlier task changed what renders — stop and read the diff before allowlisting anything.

- [ ] **Step 5: Record the allowlist**

Create `data/quality/retired-facts-allowlist.json` with exactly this content (the 48 keys Step 4 printed):

```json
{
  "_comment": "Offenders of scripts/retired_facts_check.py that were live on 2026-09-26 (Known Issue 65, audit D5): the migrated city bodies in data/locations.json and the city pages built from them. Project 5 rewrites each body; when a page is rebuilt its entries stop firing and the gate FAILS until they are deleted here, so this list only shrinks. No rebuilt page (data/facts/rebuilt.json) may appear, and tests/py/test_retired_facts_check.py pins the ceiling.",
  "known_issue": 65,
  "since": "2026-09-26",
  "entries": {
    "data:locations.json/blue-staffy-puppies-aberdeen/body_html:amount:£1,100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-aberdeen/body_html:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-aberdeen/body_html:amount:£850": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-aberdeen/body_html:amount:£850–£1,200": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-dundee/body_html:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-edinburgh/body_html:amount:£1,100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-edinburgh/body_html:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-edinburgh/body_html:amount:£850": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-edinburgh/body_html:amount:£850–£1,200": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-hull/body_html:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-hull/body_html:term:non-refundable": "Known Issue 65 — migrated city body: retired wording; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-inverness/body_html:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-middlesbrough/body_html:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-oxford/body_html:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-sunderland/body_html:amount:£1,000–£1,100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-sunderland/body_html:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-uk/body_html:amount:£300": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-uk/body_html:amount:£850": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-uk/body_html:amount:£850–£1,200": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-uk/body_html:city:Glasgow": "Known Issue 65 — migrated city body: the former city named as home (Known Issue 16); project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-uk/body_html:term:council-licensed": "Known Issue 65 — migrated city body: retired wording; project 5 rewrites this page",
    "data:locations.json/blue-staffy-puppies-york/body_html:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/staffy-breeding-dogs-glasgow/body_html:amount:£850": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "data:locations.json/staffy-breeding-dogs-glasgow/body_html:amount:£850–£1,200": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-aberdeen:amount:£1,100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-aberdeen:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-aberdeen:amount:£850": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-aberdeen:amount:£850–£1,200": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-dundee:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-edinburgh:amount:£1,100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-edinburgh:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-edinburgh:amount:£850": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-edinburgh:amount:£850–£1,200": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-hull:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-hull:term:non-refundable": "Known Issue 65 — migrated city body: retired wording; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-inverness:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-middlesbrough:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-oxford:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-sunderland:amount:£1,000–£1,100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-sunderland:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-uk:amount:£300": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-uk:amount:£850": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-uk:amount:£850–£1,200": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-uk:city:Glasgow": "Known Issue 65 — migrated city body: the former city named as home (Known Issue 16); project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-uk:term:council-licensed": "Known Issue 65 — migrated city body: retired wording; project 5 rewrites this page",
    "dist:uk-locations/blue-staffy-puppies-york:amount:£100": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/staffy-breeding-dogs-glasgow:amount:£850": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page",
    "dist:uk-locations/staffy-breeding-dogs-glasgow:amount:£850–£1,200": "Known Issue 65 — migrated city body: a retired £ figure; project 5 rewrites this page"
  }
}
```

- [ ] **Step 6: Run the sweep and the tests to verify they pass**

Run: `python3 scripts/retired_facts_check.py; echo "exit=$?" && python3 -m pytest tests/py/test_retired_facts_check.py -q -p no:cacheprovider`
Expected: `retired-facts: examined 51 built pages, 117 data fields/files, 69 src files; 48 allowlisted (Known Issue 65), 0 new, 0 stale`, `exit=0`, then `21 passed`.

- [ ] **Step 7: Chain it into check:all (failing test first)**

In `tests/py/test_package_scripts.py`, `test_the_check_all_chain_is_the_documented_one`, replace:

```python
    # (Known Issue 56).
    expected = ["check:parity", "check:facts", "check:links", "check:verbatim",
                "check:outline", "check:redirects", "check:schema", "check:queries",
                "check:competitors", "check:gaps", "check:sitemaps", "check:placeholders",
                "check:workflow", "check:markers", "agents"]
```
with:
```python
    # (Known Issue 56).
    # check:retired follows check:placeholders: both judge what the built site SAYS — a
    # placeholder is a fact not yet supplied, a retired fact is one that has been withdrawn
    # (Known Issue 65; its allowlist only shrinks).
    expected = ["check:parity", "check:facts", "check:links", "check:verbatim",
                "check:outline", "check:redirects", "check:schema", "check:queries",
                "check:competitors", "check:gaps", "check:sitemaps", "check:placeholders",
                "check:retired", "check:workflow", "check:markers", "agents"]
```

Run: `python3 -m pytest tests/py/test_package_scripts.py -q -p no:cacheprovider`
Expected: FAIL — `At index 12 diff: 'check:workflow' != 'check:retired'`.

In `package.json` add, directly after the `"check:placeholders"` entry:

```json
    "check:retired": "python3 scripts/retired_facts_check.py",
```
and in `"check:all"` replace `npm run check:placeholders && npm run check:workflow` with `npm run check:placeholders && npm run check:retired && npm run check:workflow`.

In `scripts/build_system_registry.py`, `GATES`, add directly after the `scripts/placeholder_check.py` row:

```python
    ("scripts/retired_facts_check.py", "no retired figure, retired wording or former-city claim on a built page, in rendered data or in src/ (Known Issue 65 allowlist only shrinks)"),
```

In `CLAUDE.md` insert `` `check:retired` `` after `` `check:placeholders` `` in the "`check:all` chains …" sentence. Line wrapping there may have moved in Task 6, so edit by pattern:

```bash
python3 - <<'EOF'
import pathlib, re
p = pathlib.Path("CLAUDE.md"); s = p.read_text(encoding="utf-8")
s2, n = re.subn(r"`check:placeholders`,(\s+)`check:workflow`", r"`check:placeholders`, `check:retired`,\1`check:workflow`", s)
assert n == 1, n
p.write_text(s2, encoding="utf-8")
EOF
```

Then regenerate the registry: `python3 scripts/build_system_registry.py` (prints `wrote docs/reference/system-registry.md`; it adds the script to the Scripts list and the row to the gate table).

- [ ] **Step 8: Run the chain tests to verify they pass**

Run: `python3 -m pytest tests/py/test_package_scripts.py tests/py/test_claude_md.py tests/py/test_retired_facts_check.py tests/py/test_system_registry.py tests/py/test_agent_facts.py -q -p no:cacheprovider && python3 scripts/build_system_registry.py --check`
Expected: all pass; `examined docs/reference/system-registry.md; 0 problems`.

- [ ] **Step 9: check:all**

Run: `npm run -s build && npm run -s check:all; echo "exit=$?"`
Expected: `exit=0`, and the log carries `retired-facts: … 48 allowlisted (Known Issue 65), 0 new, 0 stale`.

- [ ] **Step 10: Commit**

```bash
git add scripts/retired_facts_check.py data/quality/retired-facts-allowlist.json tests/py/test_retired_facts_check.py package.json tests/py/test_package_scripts.py CLAUDE.md scripts/build_system_registry.py docs/reference/system-registry.md
git commit -m "$(cat <<'EOF'
check: retired-facts sweep over dist/, data/ and src/ (Known Issue 65)

npm run check:retired joins check:all. Every £ figure must be in the locked set read
from settings and the price matrix; non-refundable, council-licensed and the former
city outside its own pages fail. Today's 48 offenders are the migrated city bodies,
recorded in a dated allowlist that only shrinks: a stale entry fails and the test
pins the ceiling. Project 5 burns it down.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```


### Task 10: Every data/facts/rebuilt.json page is in tests/render/targets.json (pytest) + a comparison page type

Audit Wave 2 row 8 / Appendix C 17.0. Nothing added a new page to the render targets, so
every blocking §15/§17 check would examine none of project 5's pages; and there is no
`comparison` page type. All twelve rebuilt pages are targets today, so the new rule passes on
the repo and is proven by a synthetic city key. A page type declared before its first page
would trip the existing "declared type with no target" test, so `pending_page_types` is added:
a reasoned, self-expiring entry (it fails the moment a target of that type exists).

**Files:**
- Modify: `tests/py/test_targets_coverage.py` (imports at the top; `test_every_declared_page_type_has_at_least_one_target_page`; append four tests)
- Modify: `tests/render/targets.json` (add `pending_page_types`; add `comparison` to `families_by_page_type`)

- [ ] **Step 1: Write the failing tests**

In `tests/py/test_targets_coverage.py` replace the import block:

```python
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TARGETS = ROOT / "tests/render/targets.json"
```
with:
```python
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from _slugs import resolve_page  # noqa: E402

TARGETS = ROOT / "tests/render/targets.json"
REBUILT = ROOT / "data/facts/rebuilt.json"
```
In `test_every_declared_page_type_has_at_least_one_target_page` replace `    orphans = sorted(_declared(targets) - _used(targets))` with:
```python
    orphans = sorted(_declared(targets) - _used(targets) - set(targets.get("pending_page_types", {})))
```
Append to the end of the file:
```python
# ── parity plan Task 10: project 5 pages are render targets ─────────────────────────────────
def test_a_pending_page_type_is_declared_unbuilt_and_says_when_it_ends(targets):
    """`pending_page_types` is the one way to declare a page type before its first page
    exists (project 5's comparison pages). It expires by itself: the moment a target of that
    type is added, the entry is a lie and this fails until it is removed."""
    for page_type, reason in targets.get("pending_page_types", {}).items():
        assert page_type in targets["families_by_page_type"], f"{page_type} is pending but wired to nothing"
        assert page_type not in _used(targets), (
            f"{page_type} has a target page now — remove it from pending_page_types")
        assert "remove this entry when" in reason.lower(), page_type


def test_the_comparison_page_type_runs_every_family(targets):
    """Project 5 builds comparison pages; a page type added later with fewer families would
    make its first page the least-examined page on the site."""
    fams = targets["families_by_page_type"]
    assert "comparison" in fams
    assert sorted(fams["comparison"]) == sorted(fams["location"])


def _rebuilt_gaps(keys, targets):
    """(missing, wrong): rebuilt keys with no target at their route, and targets whose
    page_type disagrees with the page's own board record."""
    by_slug = {p["slug"]: p["page_type"] for p in targets["pages"]}
    missing, wrong = [], []
    for key in keys:
        route = resolve_page(key, ROOT)[1] or "index"
        if route not in by_slug:
            missing.append(f"{key} -> {route}")
            continue
        board = ROOT / "data/boards" / (key + ".json")
        if board.exists():
            want = json.loads(board.read_text(encoding="utf-8"))["meta"]["page_type"]
            if by_slug[route] != want:
                wrong.append(f"{route}: targets.json says {by_slug[route]}, the board says {want}")
    return missing, wrong


def test_every_rebuilt_page_is_a_render_target_of_its_board_type(targets):
    """A page written from an approved board is only measured at 375/768/1280 if it is in
    `pages`, and nothing added one automatically: a project 5 page left out would be judged
    by no blocking render check at all, and every check would still read green."""
    missing, wrong = _rebuilt_gaps(json.loads(REBUILT.read_text(encoding="utf-8")), targets)
    assert not missing, ("rebuilt pages with no render target — add each to "
                         "tests/render/targets.json `pages`:\n" + "\n".join(missing))
    assert not wrong, "\n".join(wrong)


def test_a_rebuilt_city_page_resolves_to_its_route_and_is_caught_when_untargeted(targets):
    """The predicate on the key shape project 5 adds: a bare city key resolves through
    data/page-map.json to uk-locations/<slug>, and a city page with no target is named."""
    missing, wrong = _rebuilt_gaps(["blue-staffy-puppies-hull", "index"], targets)
    assert missing == ["blue-staffy-puppies-hull -> uk-locations/blue-staffy-puppies-hull"]
    assert wrong == []
    assert _rebuilt_gaps(["blue-staffy-puppies-birmingham"], targets) == ([], [])
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/py/test_targets_coverage.py -q -p no:cacheprovider`
Expected: `1 failed, 10 passed` — `FAILED …::test_the_comparison_page_type_runs_every_family` (`assert 'comparison' in {...}`).

- [ ] **Step 3: Declare the comparison page type**

In `tests/render/targets.json` replace `  "deferred_checks": {},` with:

```json
  "deferred_checks": {},
  "pending_page_types": {
    "comparison": "Project 5 builds comparison pages and none is built yet. Declared now so the first one is examined by every family the day it lands, instead of by whatever was remembered then. Remove this entry when the first comparison page is added to `pages` (tests/py/test_targets_coverage.py fails until you do)."
  },
```
and directly after the `"location": [...]` row of `families_by_page_type` add:
```json
    "comparison": ["IMG", "LAYOUT", "NAV", "SEM", "SCHEMA", "CSS", "DUP", "A11Y", "FORM"],
```

- [ ] **Step 4: Run to verify it passes, and that the render harness still loads**

Run: `python3 -m pytest tests/py/test_targets_coverage.py -q -p no:cacheprovider`
Expected: `11 passed`.

Run: `npx playwright test -c tests/render/playwright.config.ts meta.spec.ts --reporter=dot 2>&1 | tail -3`
Expected: `349 passed, 38 skipped` when `PUBLIC_FORMSPREE_ID` is unset (the FORM fixtures skip; with `.env` loaded they run), `0 failed`. (If 4321/4322 are held by another worktree's run, prefix `RENDER_SITE_PORT=4521 RENDER_FIXTURE_PORT=4522`.)

- [ ] **Step 5: check:all**

Run: `npm run -s build && npm run -s check:all; echo "exit=$?"`
Expected: `exit=0`.

- [ ] **Step 6: Commit**

```bash
git add tests/py/test_targets_coverage.py tests/render/targets.json
git commit -m "$(cat <<'EOF'
test: every rebuilt page is a render target; comparison page type declared

A rebuilt page (data/facts/rebuilt.json, bare city keys resolved to their route) must
be in tests/render/targets.json with its board's page type, or pytest fails. The
comparison type runs every family and sits in pending_page_types until its first page.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```


### Task 11: Zero-examined guard: build_scorecard.mjs chained after test:render:pages + meta test (every non-deferred check examined > 0)

Audit Wave 2 row 9 / Appendix D 19c.1, M1. `build_scorecard.mjs` (Guard 1: a page with no
partial; Guard 2: a check that examined zero nodes everywhere) ran only by hand.

Chained through a small runner, `scripts/render_pages.mjs`, **not** an npm `posttest:` hook:
verified 2026-09-26 that the full page run is red today on a pre-existing blocking row
(`uk-locations/blue-staffy-puppies-uk`, `nav-jump-target-lands`, in the 2026-09-19 and
2026-09-22 scorecards), and npm skips a `post` hook whenever the main script fails — the
guard would never have run. The runner runs Playwright, then always the scorecard, exits
with the page run's code if it failed else the scorecard's, and skips the scorecard (saying
why) on a filtered run (`--grep`, `--project`, `--shard`, `--last-failed`, `--only-changed`),
where Guard 1 would report the unrun pages as crashed. `-- <playwright args>` still reach
Playwright.

**Where scorecards are written (Task 26 reads them):** `data/quality/scorecards/<slug with
"/" replaced by "__">-<YYYY-MM-DD>.json`, one per target page per run date (committed), shape
unchanged: `{slug, date, page_type, run, harness_version, viewports[], examined{pages,checks},
examined_by_check{<check id>: n}, defects{<FAMILY>: rows}, instances{<FAMILY>: n}, total,
total_instances, overrides[], details[{viewport, checkId, count, message}]}`. The meta test
reads the newest card per target slug (`tests/render/lib/examined.ts`).

**Files:**
- Create: `tests/render/lib/examined.ts`
- Create: `scripts/render_pages.mjs`
- Create: `tests/py/test_render_pages_runner.py`
- Modify: `tests/render/meta.spec.ts` (one import line after line 19; one `test.describe` appended at the end)
- Modify: `package.json` (`test:render:pages`)
- Modify: `tests/py/test_package_scripts.py` (append one test)
- Modify: `README.md` (line 16), `CLAUDE.md` (the `test:render:pages` sentence under "Gates")
- Regenerate: `docs/reference/system-registry.md`

- [ ] **Step 1: Write the failing meta tests**

In `tests/render/meta.spec.ts`, directly after `import { flattenSlug } from './lib/scorecard.js';` add:

```ts
import { latestCards, readScorecards, zeroExamined } from './lib/examined.js';
```
Append to the end of the file:
```ts
/**
 * Every check a page run registers must have examined something on a real page.
 *
 * build_scorecard.mjs Guard 2 is the corpus-level alarm for a check that ran and judged
 * nothing, but it only fires when somebody runs it — and for most of this harness's life
 * nobody did, because `test:render:pages` stopped at Playwright. It is now chained after the
 * page run (package.json), and this is the other half: the scorecards on disk are the
 * durable record of the last page run, so the meta gate reads them and refuses a registered,
 * non-deferred check whose examined count is zero across the newest card of every target.
 * A skip, never a pass, when no target has a card: no data must not read as verified.
 */
test.describe('zero-examined guard: every non-deferred check examined > 0 in the latest scorecards', () => {
  const here = dirname(fileURLToPath(import.meta.url));
  const root = resolve(here, '..', '..');
  const targetsFile = JSON.parse(readFileSync(resolve(here, 'targets.json'), 'utf8')) as {
    deferred_checks?: Record<string, string>;
    pages: { slug: string }[];
  };

  test('latestCards keeps the newest card per slug and only the slugs asked for', () => {
    const cards = [
      { slug: 'a', date: '2026-09-16', examined_by_check: { x: 5 } },
      { slug: 'a', date: '2026-09-22', examined_by_check: { x: 0 } },
      { slug: 'b', date: '2026-09-19', examined_by_check: { x: 1 } },
      { slug: 'gone', date: '2026-09-22', examined_by_check: { x: 9 } },
    ];
    const got = latestCards(cards, ['a', 'b']).map((c) => `${c.slug}@${c.date}`).sort();
    expect(got).toEqual(['a@2026-09-22', 'b@2026-09-19']);
  });

  test('zeroExamined names a check that judged nothing, a check missing from every card, and never a deferred one', () => {
    const cards = [
      { slug: 'a', date: '2026-09-22', examined_by_check: { live: 3, dead: 0, parked: 0 } },
      { slug: 'b', date: '2026-09-22', examined_by_check: { live: 1, dead: 0 } },
    ];
    expect(zeroExamined(['live', 'dead', 'parked', 'unwired'], { parked: 'reason' }, cards)).toEqual([
      'dead',
      'unwired',
    ]);
  });

  test('the REAL latest scorecards examined every registered, non-deferred check', () => {
    const cards = latestCards(
      readScorecards(join(root, 'data', 'quality', 'scorecards')),
      targetsFile.pages.map((p) => p.slug),
    );
    if (cards.length === 0) {
      test.skip(true, 'no scorecard for any target — run `npm run test:render:pages` (it builds them)');
      return;
    }
    const dead = zeroExamined(
      registry.map((c) => c.id),
      targetsFile.deferred_checks ?? {},
      cards,
    );
    expect(
      dead,
      `examined zero nodes across the newest scorecard of ${cards.length} target page(s): ` +
        `${dead.join(', ')} — a check that judged nothing is not a pass. Point it at markup the ` +
        `pages really carry, or defer it in targets.json with a promotion condition.`,
    ).toEqual([]);
  });
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `npx playwright test -c tests/render/playwright.config.ts meta.spec.ts --reporter=dot --grep "zero-examined guard"`
Expected: FAIL — `Error: Cannot find module '…/tests/render/lib/examined.js' imported from …/tests/render/meta.spec.ts`.

- [ ] **Step 3: Write the scorecard reader**

Create `tests/render/lib/examined.ts`:

```ts
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

/**
 * The slice of a scorecard (scripts/build_scorecard.mjs) the zero-examined guard reads.
 * Cards live at data/quality/scorecards/<slug with / as __>-<YYYY-MM-DD>.json, one per page
 * per run date, and carry `examined_by_check`: units judged per check, summed across that
 * page's viewports.
 */
export interface Scorecard {
  slug: string;
  date: string;
  examined_by_check?: Record<string, number>;
}

/** Every card on disk; an absent directory is an empty list, never an error. */
export function readScorecards(dir: string): Scorecard[] {
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => f.endsWith('.json'))
    .map((f) => JSON.parse(readFileSync(join(dir, f), 'utf8')) as Scorecard);
}

/**
 * The newest card of each slug, restricted to `slugs` when given. Per slug rather than
 * "the newest date": a one-page re-run writes today's card for that page only, and judging
 * today's date alone would read every other page as absent.
 */
export function latestCards(cards: Scorecard[], slugs?: string[]): Scorecard[] {
  const want = slugs ? new Set(slugs) : null;
  const best = new Map<string, Scorecard>();
  for (const c of cards) {
    if (want && !want.has(c.slug)) continue;
    const prev = best.get(c.slug);
    if (!prev || c.date > prev.date) best.set(c.slug, c);
  }
  return [...best.values()];
}

/**
 * Registered, non-deferred check ids whose examined count sums to zero across `cards`.
 * Seeded from the ids, not from the cards: a check that ran nowhere contributes no key to any
 * card and would be invisible to a sum over the cards alone (build_scorecard.mjs Guard 2's
 * own reasoning).
 */
export function zeroExamined(
  checkIds: string[],
  deferred: Record<string, string>,
  cards: Scorecard[],
): string[] {
  const total = new Map<string, number>(checkIds.map((id) => [id, 0]));
  for (const c of cards) {
    for (const [id, n] of Object.entries(c.examined_by_check ?? {})) {
      if (total.has(id)) total.set(id, (total.get(id) ?? 0) + n);
    }
  }
  return [...total.entries()]
    .filter(([id, n]) => n === 0 && !(id in deferred))
    .map(([id]) => id)
    .sort();
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `npx playwright test -c tests/render/playwright.config.ts meta.spec.ts --reporter=dot --grep "zero-examined guard"`
Expected: `9 passed` (three tests × three viewport projects; the REAL test reads the 2026-09-22 cards, where every registered check examined > 0).

- [ ] **Step 5: Write the failing runner tests**

Create `tests/py/test_render_pages_runner.py`:

```python
"""`scripts/render_pages.mjs` — `npm run test:render:pages` always ends in the zero-examined guard.

Parity plan Task 11 (CAG §19c, audit M1). The scorecard builder is Guards 1 and 2; it has to
run after EVERY full page run, including a failing one, and must not run after a filtered run
(Guard 1 would report the skipped pages as crashed). The two commands are replaced through
RENDER_PAGES_RUNNER / RENDER_SCORECARD so these tests start no browser."""
import os
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "render_pages.mjs"


def _run(tmp_path, pages_exit, card_exit, *args):
    log = tmp_path / "log.txt"
    pages = tmp_path / "pages.sh"
    pages.write_text(f'#!/bin/sh\necho "pages $*" >> {log}\nexit {pages_exit}\n')
    pages.chmod(0o755)
    card = tmp_path / "card.mjs"
    card.write_text("import { appendFileSync } from 'node:fs';\n"
                    f"appendFileSync({str(log)!r}, 'scorecard\\n');\nprocess.exit({card_exit});\n")
    env = dict(os.environ, RENDER_PAGES_RUNNER=str(pages), RENDER_SCORECARD=str(card))
    r = subprocess.run(["node", str(RUNNER), *args], capture_output=True, text=True, env=env, cwd=ROOT)
    return r, (log.read_text().splitlines() if log.exists() else [])


def test_a_clean_run_builds_the_scorecard(tmp_path):
    r, log = _run(tmp_path, 0, 0, "--reporter=dot")
    assert r.returncode == 0
    assert log == ["pages --reporter=dot", "scorecard"]


def test_a_failing_page_run_still_builds_the_scorecard_and_still_fails(tmp_path):
    r, log = _run(tmp_path, 1, 0)
    assert log == ["pages ", "scorecard"]
    assert r.returncode == 1


def test_a_zero_examined_scorecard_fails_a_green_page_run(tmp_path):
    r, log = _run(tmp_path, 0, 1)
    assert log[-1] == "scorecard"
    assert r.returncode == 1


def test_a_filtered_run_skips_the_scorecard_and_says_why(tmp_path):
    for flag in (["--grep", "kit-preview"], ["--project=vp375"], ["--last-failed"]):
        r, log = _run(tmp_path, 0, 0, *flag)
        assert "scorecard" not in log, flag
        assert "scorecard: skipped — a filtered run" in r.stdout, flag
        (tmp_path / "log.txt").unlink()
```
Append to `tests/py/test_package_scripts.py`:
```python
def test_the_page_run_ends_in_the_zero_examined_guard():
    """`build_scorecard.mjs` holds Guard 1 (a page that wrote no partial) and Guard 2 (a
    check that examined zero nodes across every page), and until parity plan Task 11 it ran
    only when somebody remembered to type it. `scripts/render_pages.mjs` runs the page suite
    and then the scorecard, whatever the page run's result (tests/py/test_render_pages_runner.py).
    Not an npm `post` hook: npm skips that when the page run fails."""
    assert SCRIPTS["test:render:pages"] == "node scripts/render_pages.mjs"
    assert "posttest:render:pages" not in SCRIPTS
```

Run: `python3 -m pytest tests/py/test_render_pages_runner.py tests/py/test_package_scripts.py -q -p no:cacheprovider`
Expected: FAIL — the four runner tests fail (`Cannot find module '…/scripts/render_pages.mjs'`, so no `log.txt` and a non-zero exit) and `test_the_page_run_ends_in_the_zero_examined_guard` fails (`'playwright test -c tests/render/playwright.config.ts pages.spec.ts' == 'node scripts/render_pages.mjs'`).

- [ ] **Step 6: Write the runner and chain it**

Create `scripts/render_pages.mjs`:

```js
#!/usr/bin/env node
// npm run test:render:pages [-- <playwright args>]
//
// The page run, then the zero-examined guard — ALWAYS both. build_scorecard.mjs holds Guard 1
// (a page that wrote no partial) and Guard 2 (a check that examined zero nodes across every
// page), and for most of this harness's life it ran only when somebody remembered to type it.
// An npm `post` hook is not enough: npm skips it whenever the page run fails, and a page run
// with one blocking defect is exactly the run whose examined counts need reading.
//
// Exit code: the page run's if it failed, else the scorecard's. A FILTERED run (--grep,
// --project, --shard, --last-failed, --only-changed) writes partials for some pages only, so
// the scorecard is skipped and says why — Guard 1 would otherwise report the pages it was told
// not to run as crashed.
//
// RENDER_PAGES_RUNNER / RENDER_SCORECARD replace the two commands (tests only).
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';

const args = process.argv.slice(2);
const runner = process.env.RENDER_PAGES_RUNNER
  ? [process.env.RENDER_PAGES_RUNNER]
  : [resolve('node_modules/.bin/playwright'), 'test', '-c', 'tests/render/playwright.config.ts', 'pages.spec.ts'];
const scorecard = process.env.RENDER_SCORECARD ?? 'scripts/build_scorecard.mjs';
const FILTERS = ['--grep', '-g', '--grep-invert', '--project', '--shard', '--last-failed', '--only-changed'];

const pages = spawnSync(runner[0], [...runner.slice(1), ...args], { stdio: 'inherit' });
const pagesStatus = pages.status ?? 1;
if (args.some((a) => FILTERS.some((f) => a === f || a.startsWith(`${f}=`)))) {
  console.log('scorecard: skipped — a filtered run measures some pages only; run the whole suite for the zero-examined guard');
  process.exit(pagesStatus);
}
const card = spawnSync(process.execPath, [scorecard], { stdio: 'inherit' });
process.exit(pagesStatus || (card.status ?? 1));
```

In `package.json` replace `"test:render:pages": "playwright test -c tests/render/playwright.config.ts pages.spec.ts",` with:

```json
    "test:render:pages": "node scripts/render_pages.mjs",
```
In `README.md` replace the line `npm run test:render:meta && npm run test:render:pages && node scripts/build_scorecard.mjs --run first` with:
```
npm run test:render:meta && npm run test:render:pages   # ends in build_scorecard.mjs, the zero-examined guard
```
In `CLAUDE.md` replace:
```
any page result. `test:render:pages` measures the target pages at 375/768/1280 in a real
browser.
```
with:
```
any page result. `test:render:pages` measures the target pages at 375/768/1280 in a real
browser and then, pass or fail, runs `node scripts/build_scorecard.mjs`
(`scripts/render_pages.mjs`), which fails a run where a registered check examined zero nodes
and writes the scorecards `test:render:meta` reads back.
```

Regenerate the registry (a new script): `python3 scripts/build_system_registry.py`.

- [ ] **Step 7: Run to verify it passes**

Run: `python3 -m pytest tests/py/test_render_pages_runner.py tests/py/test_package_scripts.py tests/py/test_claude_md.py tests/py/test_system_registry.py -q -p no:cacheprovider`
Expected: all pass.

Run (the real chain, filtered so it is quick): `npm run -s build && npm run test:render:pages -- --grep kit-preview --reporter=dot 2>&1 | tail -3`
Expected: `3 passed`, then `scorecard: skipped — a filtered run measures some pages only; run the whole suite for the zero-examined guard`. The full run with the scorecard is Step 7 of Task 14.

- [ ] **Step 8: check:all**

Run: `npm run -s build && npm run -s check:all; echo "exit=$?"`
Expected: `exit=0`.

- [ ] **Step 9: Commit**

```bash
git add tests/render/lib/examined.ts tests/render/meta.spec.ts scripts/render_pages.mjs tests/py/test_render_pages_runner.py tests/py/test_package_scripts.py package.json README.md CLAUDE.md docs/reference/system-registry.md
git commit -m "$(cat <<'EOF'
test: the page run always ends in the zero-examined guard; meta reads it back

npm run test:render:pages runs scripts/render_pages.mjs: the page suite, then
build_scorecard.mjs whatever the page run's result (an npm post hook is skipped when
the run fails, and today's run fails on a pre-existing NAV row). The meta gate fails a
registered, non-deferred check that examined zero nodes in the newest scorecards.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```


### Task 12: Chain board_gate.py into check:all for every rebuilt page

Audit Wave 2 row 10 / Appendix A 3.5, 3.12, C 15c. The Asset Gate (approval hash, the image
build-gate checks, header collisions) ran only when someone typed `board_gate.py <slug>`.
`board_gate.py --all` runs the build stage over every slug in `data/facts/rebuilt.json`
(reading dist/, the ontology, the ledger and every record once) and is `npm run
check:boards` in `check:all`. A rebuilt page with no board record FAILs (`board-missing`).
The single-slug CLI is unchanged: `main()` now delegates to `judge()`, and the existing
`tests/py/test_page_board.py` board-gate tests pass untouched.

**Consequence to know:** `check:all` now needs a FRESH build. `min-h5-h6` reads the built
page only when it is newer than its sources (`pageboard.dist_page_is_fresh`); on a stale
dist/ it falls back to the record tree and FAILs all eleven non-home rebuilt pages
(verified 2026-09-26). From this task on, run `npm run -s build` before `npm run -s
check:all` whenever src/, data/*.json or data/boards/ changed.

**Files:**
- Modify: `scripts/board_gate.py` (whole file below)
- Create: `tests/py/test_board_gate_all.py`
- Modify: `package.json` (add `check:boards`; `check:all` chain)
- Modify: `tests/py/test_package_scripts.py` (`test_the_check_all_chain_is_the_documented_one`)
- Modify: `CLAUDE.md` (the `check:all` sentence; the "No page is built without an approved board" paragraph)
- Modify: `scripts/build_system_registry.py` (`GATES`), regenerate `docs/reference/system-registry.md`

- [ ] **Step 1: Write the failing tests**

Create `tests/py/test_board_gate_all.py`:

```python
"""`board_gate.py --all` — the Asset Gate over every rebuilt page, chained into check:all.

Audit Wave 2 row 10: `board_gate.py` held the approval hash and the image build-gate checks,
and ran only when somebody typed it. `--all` runs the build stage over every slug in
data/facts/rebuilt.json and is `npm run check:boards`."""
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import board_gate as BG  # noqa: E402
import pageboard as PB   # noqa: E402

GATE = str(ROOT / "scripts" / "board_gate.py")


@pytest.fixture
def quiet_inputs(monkeypatch):
    monkeypatch.setattr(PB, "load_ontology", lambda: {"entities": []})
    monkeypatch.setattr(PB, "load_ledger", lambda: {"pages": {}})
    monkeypatch.setattr(PB, "live_headings", lambda: {"/a/": ["A"]})
    monkeypatch.setattr(PB, "load_all_boards", lambda: [])


def _judge(results):
    def judge(slug, stage, ont, ledger, live, boards):
        assert stage == "build"
        r = results[slug]
        if isinstance(r, Exception):
            raise r
        return r, [f"board-gate {slug} [build] — 1 sections, 1 headings, {len(live)} live pages, "
                   "0 entity refs, 0 ledger siblings, 0 assets examined",
                   f"{r} FAIL · 0 WARN"]
    return judge


def test_all_judges_every_rebuilt_page_and_fails_a_missing_board(monkeypatch, capsys, quiet_inputs):
    monkeypatch.setattr(PB, "rebuilt_slugs", lambda: {"good", "gone", "bad"})
    monkeypatch.setattr(BG, "judge", _judge({"good": 0, "bad": 2,
                                             "gone": PB.BoardError("no board for gone")}))
    assert BG.run_all() == 1
    out = capsys.readouterr().out
    assert "board-gate good [build] — 1 sections" in out and "examined — 0 FAIL" in out
    assert "FAIL board-missing             no board for gone" in out
    assert "2 FAIL · 0 WARN" in out                                   # a failing page prints in full
    assert out.rstrip().endswith("board-gate --all: examined 3 rebuilt pages against 1 live pages; "
                                 "2 failed: bad, gone")


def test_all_passes_when_every_rebuilt_page_passes(monkeypatch, capsys, quiet_inputs):
    monkeypatch.setattr(PB, "rebuilt_slugs", lambda: {"good"})
    monkeypatch.setattr(BG, "judge", _judge({"good": 0}))
    assert BG.run_all() == 0
    assert "examined 1 rebuilt pages against 1 live pages; 0 failed" in capsys.readouterr().out


def test_all_over_no_rebuilt_pages_is_not_a_pass(monkeypatch, capsys, quiet_inputs):
    monkeypatch.setattr(PB, "rebuilt_slugs", lambda: set())
    assert BG.run_all() == 1
    assert "examined 0 rebuilt pages" in capsys.readouterr().out


def test_all_takes_no_slug_and_no_other_flag():
    for argv in (["--all", "index"], ["--all", "--release"]):
        r = subprocess.run([sys.executable, GATE, *argv], capture_output=True, text=True)
        assert r.returncode == 2 and "usage: board_gate.py" in r.stdout, argv


def test_check_boards_is_the_all_run():
    scripts = json.loads((ROOT / "package.json").read_text())["scripts"]
    assert scripts["check:boards"] == "python3 scripts/board_gate.py --all"
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/py/test_board_gate_all.py -q -p no:cacheprovider`
Expected: `4 failed, 1 passed` — `AttributeError: <module 'board_gate' …> has no attribute 'judge'`, `AttributeError: module 'board_gate' has no attribute 'run_all'`, `KeyError: 'check:boards'` (`test_all_takes_no_slug_and_no_other_flag` passes already: `--all` is an unknown flag today).

- [ ] **Step 3: Implement `--all`**

Replace the whole of `scripts/board_gate.py` with:

```python
#!/usr/bin/env python3
"""board_gate.py <slug> [--release]  |  board_gate.py --all
The Page Board gate: refuses to build (or release) a page whose board record is not
approved as it stands. Reads live headings from dist/ (build first). Exit 1 on any FAIL,
exit 2 when the record itself cannot be read or the invocation is wrong.
Prints its examined counts — a gate that examines nothing is not a pass
(.claude/skills/bsuk-gate-integrity/SKILL.md).

`--all` (`npm run check:boards`, in check:all) runs the build-stage gate over EVERY page in
data/facts/rebuilt.json — the Asset Gate and the approval hash stop being a step somebody
has to remember. A rebuilt page with no board record is a FAIL there, never a skip: no page
is built without an approved board. dist/, the ontology, the ledger and every record are
read once for the whole run."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pageboard as PB

USAGE = "usage: board_gate.py <slug> [--release]  |  board_gate.py --all"
FLAGS = {"--release", "--all"}


def judge(slug, stage, ont, ledger, live, boards):
    """(fail count, printed lines) for one record. Raises PB.BoardError when the record
    cannot be read."""
    board = PB.load_board(slug)
    # The page's own live headings are NOT popped here: header_hits() excludes them
    # with own_live_key(), and a caller-side pop mis-keyed the homepage (slug "").
    f = PB.gate_findings(board, ont, ledger, live, stage=stage)
    # Working rule 16's uniqueness half needs every other record, which gate_findings()
    # (pure over one record) never reads.
    f += PB.rule16_findings(board, boards)
    judged = PB.rule16_judged(boards, board)
    n_head = len(PB.all_headings(board))
    # Every family says what it examined: an empty ledger or an empty asset list would
    # otherwise let the ledger-* checks and asset-required-missing pass on nothing.
    siblings = [p for p in ledger.get("pages", {}) if p != board["meta"]["slug"]]
    lines = [f"board-gate {slug} [{stage}] — {len(board['sections'])} sections, {n_head} headings, "
             f"{len(live)} live pages, {sum(len(s['entities']) for s in board['sections'])} entity refs, "
             f"{len(siblings)} ledger siblings, {len(board['assets'])} assets examined"]
    # Until the component ledger records a page, the five ledger-* checks have nothing to
    # compare against. Said out loud so an empty ledger cannot be read as a clean gate.
    if not ledger.get("pages"):
        lines.append("ledger: empty — ledger-* families examined 0, not a pass")
    # Rule 16 is judged across records, so its count is records, not this record's sections.
    lines.append(f"rule 16: {len(judged)} records judged" if judged
                 else "rule 16: 0 records judged — examined nothing, not a pass")
    for x in f:
        lines.append(f"  {x['sev']:4s} {x['check']:24s} {x['msg']}")
    fails = [x for x in f if x["sev"] == "FAIL"]
    lines.append(f"{len(fails)} FAIL · {len(f) - len(fails)} WARN")
    return len(fails), lines


def run_all():
    """Exit code of the build-stage gate over every rebuilt page."""
    slugs = sorted(PB.rebuilt_slugs())
    if not slugs:
        print("board-gate --all: examined 0 rebuilt pages — data/facts/rebuilt.json is empty "
              "or unreadable, which is not a pass")
        return 1
    try:
        ont, ledger = PB.load_ontology(), PB.load_ledger()
        live = PB.live_headings() if PB.DIST.exists() else {}
        boards = PB.load_all_boards()
    except PB.BoardError as e:
        print(f"board-gate ERROR {e}")
        return 2
    failed = []
    for slug in slugs:
        try:
            n, lines = judge(slug, "build", ont, ledger, live, boards)
        except PB.BoardError as e:
            n, lines = 1, [f"board-gate {slug} [build]", f"  FAIL board-missing             {e}"]
        if n:
            failed.append(slug)
            print("\n".join(lines))
        else:
            print(lines[0].replace(" examined", " examined — 0 FAIL", 1))
    print(f"board-gate --all: examined {len(slugs)} rebuilt pages against {len(live)} live pages; "
          f"{len(failed)} failed{': ' + ', '.join(failed) if failed else ''}")
    return 1 if failed else 0


def main():
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    unknown = [a for a in flags if a not in FLAGS]
    if "--all" in flags and not unknown and not args and flags == ["--all"]:
        sys.exit(run_all())
    if unknown or len(args) != 1 or "--all" in flags:
        print(f"board-gate ERROR unknown option {unknown[0]}" if unknown else
              "board-gate ERROR --all takes no slug and no other option" if "--all" in flags else
              "board-gate ERROR one slug expected")
        print(USAGE)
        sys.exit(2)
    slug, stage = args[0], ("release" if "--release" in flags else "build")
    try:
        ont, ledger = PB.load_ontology(), PB.load_ledger()
        live = PB.live_headings() if PB.DIST.exists() else {}
        n, lines = judge(slug, stage, ont, ledger, live, PB.load_all_boards())
    except PB.BoardError as e:
        print(f"board-gate ERROR {e}")
        sys.exit(2)
    print("\n".join(lines))
    sys.exit(1 if n else 0)


if __name__ == "__main__":
    main()
```

In `package.json` add, directly after `"check:retired"`:

```json
    "check:boards": "python3 scripts/board_gate.py --all",
```
and in `"check:all"` replace `npm run check:retired && npm run check:workflow` with `npm run check:retired && npm run check:boards && npm run check:workflow`.
In `tests/py/test_package_scripts.py` replace:
```python
    # (Known Issue 65; its allowlist only shrinks).
    expected = ["check:parity", "check:facts", "check:links", "check:verbatim",
                "check:outline", "check:redirects", "check:schema", "check:queries",
                "check:competitors", "check:gaps", "check:sitemaps", "check:placeholders",
                "check:retired", "check:workflow", "check:markers", "agents"]
```
with:
```python
    # (Known Issue 65; its allowlist only shrinks).
    # check:boards follows check:retired: `board_gate.py --all` runs the build-stage board
    # gate (approval hash, Asset Gate image checks, header collisions) over every page in
    # data/facts/rebuilt.json, so no rebuilt page ships on a board that stopped matching.
    expected = ["check:parity", "check:facts", "check:links", "check:verbatim",
                "check:outline", "check:redirects", "check:schema", "check:queries",
                "check:competitors", "check:gaps", "check:sitemaps", "check:placeholders",
                "check:retired", "check:boards", "check:workflow", "check:markers", "agents"]
```
In `scripts/build_system_registry.py`, `GATES`, add directly before the `scripts/retired_facts_check.py` row (`tests/py/test_system_registry.py::test_every_check_all_gate_is_in_the_gate_table` fails without it):
```python
    ("scripts/board_gate.py", "every rebuilt page's board is approved as it stands and its Asset Gate holds (`--all`)"),
```
Edit `CLAUDE.md` by pattern (two edits):
```bash
python3 - <<'EOF'
import pathlib, re
p = pathlib.Path("CLAUDE.md"); s = p.read_text(encoding="utf-8")
s, n1 = re.subn(r"`check:retired`,(\s+)`check:workflow`", r"`check:retired`, `check:boards`,\1`check:workflow`", s)
old = ("**No page is built without an approved board.** `python3 scripts/board_gate.py <slug>`\n"
       "refuses when `data/boards/<slug>.json` is missing or unapproved;")
new = ("**No page is built without an approved board.** `python3 scripts/board_gate.py <slug>`\n"
       "refuses when `data/boards/<slug>.json` is missing or unapproved (`npm run check:boards`, in\n"
       "`check:all`, runs it with `--all` over every page in `data/facts/rebuilt.json`);")
assert n1 == 1 and old in s
p.write_text(s.replace(old, new), encoding="utf-8")
EOF
```
Then `python3 scripts/build_system_registry.py`.

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/py/test_board_gate_all.py tests/py/test_package_scripts.py tests/py/test_claude_md.py tests/py/test_page_board.py tests/py/test_system_registry.py -q -p no:cacheprovider`
Expected: all pass (`test_page_board.py`'s single-slug board-gate tests unchanged).

Run: `npm run -s build && python3 scripts/board_gate.py --all | tail -1`
Expected: `board-gate --all: examined 12 rebuilt pages against 51 live pages; 0 failed`.

- [ ] **Step 5: check:all**

Run: `npm run -s build && npm run -s check:all; echo "exit=$?"`
Expected: `exit=0`.

- [ ] **Step 6: Commit**

```bash
git add scripts/board_gate.py tests/py/test_board_gate_all.py package.json tests/py/test_package_scripts.py CLAUDE.md scripts/build_system_registry.py docs/reference/system-registry.md
git commit -m "$(cat <<'EOF'
check: board gate over every rebuilt page joins check:all

board_gate.py --all (npm run check:boards) runs the build-stage gate over every slug in
data/facts/rebuilt.json; a rebuilt page with no board fails. The Asset Gate is no
longer a step somebody has to remember. check:all now needs a fresh build.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```


### Task 13: board_approve.py refuses header-collision on new pages

Audit Wave 2 row 11 / Appendix B 12.9. `header-collision` FAILed only at `board_gate.py`,
after approval: a colliding city H2 was approved, refused at build, and the reword moved the
hash and forced a re-approval. Approval and re-approval of a page `family_rules.applies()`
names now run the same `pageboard.header_hits()` the gate runs, and refuse an empty live set
("examined 0 live pages — run npm run build first"). The twelve built pages approve as
before. `apply_approval` / `apply_reapproval` take `live=None` (the pure API's opt-out, so
every existing caller and test is unchanged); `main()` and `reapprove_main()` always pass
`PB.live_headings()`.

Test-safety note, found while verifying: `pageboard.LEDGER` and `pageboard.ONTOLOGY` are
bound to the real files at import, so a CLI test that monkeypatches only `PB.ROOT` WRITES
the real `data/component-ledger.json` and `data/bsuk-ontology.json` when approval succeeds
(it does, before the fix). The CLI test below repoints both.

**Files:**
- Modify: `scripts/board_approve.py` (new `refuse_header_collisions()` before `apply_approval`; `apply_approval`, `apply_reapproval`, `reapprove_main`, `main`)
- Create: `tests/py/test_board_approve_header_collision.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/py/test_board_approve_header_collision.py`:

```python
"""`board_approve.py` refuses a header collision on a new page (audit Wave 2 row 11, CAG §12.9).

`header-collision` used to FAIL only at `board_gate.py`, after approval: a new city H2 that
collided with a live sibling was approved, then refused at the build gate, and fixing the
wording moved the record hash and forced a second approval. Across 28 city pages that is 28
chances of a wasted round trip. Approval (and re-approval) of a page `family_rules.applies()`
names now runs the same `pageboard.header_hits()` the gate runs; the twelve built pages
approve exactly as before."""
import copy
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import board_approve as BA   # noqa: E402
import family_rules as FR    # noqa: E402
import pageboard as PB       # noqa: E402

ONT = {"entities": []}
LEDGER = {"pools": {}, "pages": {}}
NEW = "uk-locations/blue-staffy-puppies-manchester"
LIVE_CLEAN = {"/other/": ["Where Do We Deliver Each Week?"]}
LIVE_COLLIDING = {"/other/": ["The First Eight Weeks"]}      # _demo carries "The first eight weeks"


def _board(slug=NEW, page_type="location"):
    b = copy.deepcopy(json.loads((ROOT / "data" / "boards" / "_demo.json").read_text()))
    b["meta"]["slug"] = slug
    b["meta"]["page_type"] = page_type
    return b


def _inbox(b):
    picks = {s["id"]: (s.get("styles") or s["options"]["candidates"])[0]
             for s in b["sections"] if s["shape"] != "standard"}
    return {"approved_at": "2026-09-26T12:00:00Z", "h1": 0, "picks": picks, "notes": {},
            "canvas_version": None, "record_hash": PB.record_hash(b)}


@pytest.fixture(autouse=True)
def no_other_new_page_rules(monkeypatch):
    """Only the collision refusal is under test; the other family rules have their own file."""
    monkeypatch.setattr(FR, "CHECKS", [])


def test_a_new_page_whose_heading_collides_is_refused_at_approval():
    b = _board()
    before = json.dumps(b, sort_keys=True)
    with pytest.raises(PB.BoardError) as e:
        BA.apply_approval(b, _inbox(b), ONT, LEDGER, live=LIVE_COLLIDING)
    msg = str(e.value)
    assert msg.startswith("this record's headings collide with live pages — reword them and board it again:")
    assert "header-collision: exact: 'The first eight weeks' vs /other/" in msg
    assert json.dumps(b, sort_keys=True) == before                 # still pure


def test_a_new_page_with_no_collision_approves():
    b = _board()
    out = BA.apply_approval(b, _inbox(b), ONT, LEDGER, live=LIVE_CLEAN)
    assert out["board"]["meta"]["status"] == "approved"


def test_a_new_page_is_not_approved_against_no_live_pages():
    b = _board()
    with pytest.raises(PB.BoardError, match="examined 0 live pages"):
        BA.apply_approval(b, _inbox(b), ONT, LEDGER, live={})


def test_a_built_page_still_approves_over_a_collision():
    """Frozen: the twelve pages built before the system-gaps build keep the old contract,
    where a collision is the build gate's to report."""
    b = _board(slug="x", page_type="hub")
    assert not FR.applies(b)
    out = BA.apply_approval(b, _inbox(b), ONT, LEDGER, live=LIVE_COLLIDING)
    assert out["board"]["meta"]["status"] == "approved"


def test_re_approval_of_a_new_page_is_refused_while_a_heading_collides():
    import test_board_reapprove as TR
    old = TR.approved()
    old["meta"]["slug"], old["meta"]["page_type"] = NEW, "location"
    old["approval"]["record_hash"] = PB.record_hash(old)
    new = json.loads(json.dumps(old))
    new["sections"][0]["heading"] = "Where Do We Deliver Each Week?"
    with pytest.raises(PB.BoardError, match="header-collision: exact"):
        BA.apply_reapproval(new, "wording fix", old, "2026-09-26T12:00:00Z", ONT, live=LIVE_CLEAN)


def test_the_cli_reads_the_live_pages_and_refuses(tmp_path, monkeypatch, capsys):
    """main() is what the operator runs: it must hand apply_approval the real live headings,
    not leave the check to a caller who might not pass them."""
    b = _board()
    stem = PB.slug_file(NEW)
    (tmp_path / "data" / "boards" / "inbox").mkdir(parents=True)
    (tmp_path / "data" / "boards" / "inbox" / (stem + ".json")).write_text(json.dumps(_inbox(b)))
    (tmp_path / "dist").mkdir()
    monkeypatch.setattr(PB, "ROOT", tmp_path)
    monkeypatch.setattr(PB, "DIST", tmp_path / "dist")
    # LEDGER and ONTOLOGY are bound at import to the real files: repoint them, so that a
    # main() which (wrongly) approved would write into tmp_path and never into data/.
    monkeypatch.setattr(PB, "LEDGER", tmp_path / "data" / "component-ledger.json")
    monkeypatch.setattr(PB, "ONTOLOGY", tmp_path / "data" / "bsuk-ontology.json")
    monkeypatch.setattr(PB, "load_board", lambda slug: copy.deepcopy(b))
    monkeypatch.setattr(PB, "load_ontology", lambda: ONT)
    monkeypatch.setattr(PB, "load_ledger", lambda: LEDGER)
    monkeypatch.setattr(PB, "live_headings", lambda: LIVE_COLLIDING)
    monkeypatch.setattr(sys, "argv", ["board_approve.py", NEW])
    with pytest.raises(SystemExit) as e:
        BA.main()
    assert e.value.code == 2
    out = capsys.readouterr().out
    assert "board-approve ERROR this record's headings collide with live pages" in out
    for written in ("boards/" + stem + ".json", "component-ledger.json", "bsuk-ontology.json"):
        assert not (tmp_path / "data" / written).exists(), written          # nothing written
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/py/test_board_approve_header_collision.py -q -p no:cacheprovider; git status --short data/`
Expected: `6 failed` — `TypeError: apply_approval() got an unexpected keyword argument 'live'`, `TypeError: apply_reapproval() got an unexpected keyword argument 'live'`, and `Failed: DID NOT RAISE <class 'SystemExit'>` for the CLI test (today's main approves); `git status` shows nothing under `data/`.

- [ ] **Step 3: Implement the refusal**

In `scripts/board_approve.py` replace:

```python
def apply_approval(board, inbox, ont, ledger, canvas_dir=None):
    """The board, ledger and ontology as they stand after this approval. Pure: it reads
    nothing but its arguments and writes nothing — raise here and the files on disk are
    untouched."""
```
with:
```python
def refuse_header_collisions(b, live):
    """A new page (family_rules.applies) whose headings collide with a live page is refused
    at approval and at re-approval, with the same `pageboard.header_hits()` the build gate
    FAILs on as `header-collision`. Otherwise the colliding record is approved, refused at
    board_gate, and the reword moves the hash and forces a second approval. `live` is
    {page: [heading, ...]} (pageboard.live_headings()); None means the caller read no live
    pages and is the pure API's opt-out — main() and reapprove_main() always read them. A new
    page is never approved against an EMPTY live set: that is a pre-check of nothing."""
    if live is None or not PB.FR.applies(b):
        return
    if not live:
        raise PB.BoardError(
            "header pre-check examined 0 live pages — run npm run build first; a new page is "
            "not approved against nothing")
    hits = PB.header_hits(b, live)
    if hits:
        raise PB.BoardError(
            "this record's headings collide with live pages — reword them and board it again:\n"
            + "\n".join(f"  - header-collision: {h['kind']}: {h['heading']!r} vs {h['page']} {h['with']!r}"
                        for h in hits))


def apply_approval(board, inbox, ont, ledger, canvas_dir=None, live=None):
    """The board, ledger and ontology as they stand after this approval. Pure: it reads
    nothing but its arguments and writes nothing — raise here and the files on disk are
    untouched. `live` is the built site's headings, for refuse_header_collisions()."""
```
At the end of `apply_approval`, replace:
```python
    refuse_on_new_page_rules(b, o)
    return {"board": b, "ledger": led, "ontology": o, "changed": changed, "promoted": promoted}
```
with:
```python
    refuse_on_new_page_rules(b, o)
    refuse_header_collisions(b, live)
    return {"board": b, "ledger": led, "ontology": o, "changed": changed, "promoted": promoted}
```
Replace `def apply_reapproval(board, reason, old_board, now, ont):` with `def apply_reapproval(board, reason, old_board, now, ont, live=None):`, and at its end replace:
```python
    PB.validate_board(b)
    refuse_on_new_page_rules(b, ont)
    return {"board": b, "changed_paths": paths}
```
with:
```python
    PB.validate_board(b)
    refuse_on_new_page_rules(b, ont)
    refuse_header_collisions(b, live)
    return {"board": b, "changed_paths": paths}
```
In `reapprove_main` replace:
```python
    out = apply_reapproval(board, a.reason, baseline_board(slug), now, PB.load_ontology())
```
with:
```python
    live = PB.live_headings() if PB.DIST.exists() else {}
    out = apply_reapproval(board, a.reason, baseline_board(slug), now, PB.load_ontology(), live=live)
```
In `main` replace:
```python
        out = apply_approval(before, inbox, PB.load_ontology(), PB.load_ledger(), canvas_dir)
```
with:
```python
        live = PB.live_headings() if PB.DIST.exists() else {}
        out = apply_approval(before, inbox, PB.load_ontology(), PB.load_ledger(), canvas_dir, live=live)
```

- [ ] **Step 4: Run to verify it passes, with every approval test**

Run: `python3 -m pytest tests/py/test_board_approve_header_collision.py tests/py/test_family_rules_on_board.py tests/py/test_board_reapprove.py tests/py/test_page_board.py tests/py/test_image_rules.py tests/py/test_rule16_gate.py -q -p no:cacheprovider; git status --short data/`
Expected: all pass (`320 passed` at the time of writing), nothing under `data/` modified.

- [ ] **Step 5: check:all**

Run: `npm run -s build && npm run -s check:all; echo "exit=$?"`
Expected: `exit=0`.

- [ ] **Step 6: Commit**

```bash
git add scripts/board_approve.py tests/py/test_board_approve_header_collision.py
git commit -m "$(cat <<'EOF'
board: approval refuses a header collision on a new page

A location, comparison or blog record whose heading collides with a live page is
refused at approval and re-approval with the gate's own header_hits(), instead of
being approved and then refused at build. The twelve built pages are unchanged.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```


### Task 14: layout-h3-image-first retargeted to real image class; `promotions` record in targets.json + meta test; promote hero-counter-separation, h3-image-first, sem-section-opening-paragraph, sem-title-case-headings to blocking on NEW (project 5) pages only

Audit Wave 2 row 12 / Appendix C 13.6, 13.7, B 12.4, D 19c.3. `layout-h3-image-first`
counted only `img.sec-img`, which ships on /kit-preview/ alone; rebuilt pages render body
photos through `src/components/BodyImage.astro` as `img.bl-img`, so the check examined zero
blocks exactly where rule 17 puts an H3 image. It now matches `img.sec-img, img.bl-img`.
(Interface for Task 8: if Task 8 (a) gives new-page body images a different class, that class
must be added to the same selector in `tests/render/checks/layout.ts` or also carry
`bl-img`.)

Promotion becomes a record: `targets.json` gains `promotions` (every registered `blocking`
check has a scope `all` entry — grandfathered, stated as such — and the four checks get scope
`new-pages`) and `new_page_rule` (family_rules' `NEW_FAMILY_PAGE_TYPES` and
`BUILT_BEFORE_SYSTEM_GAPS`, pinned by pytest). `pages.spec.ts` decides severity per page via
`tests/render/lib/promotions.ts`: a `new-pages` check blocks on a page that is a new-family
type, in `data/facts/rebuilt.json` and not frozen. Today no target qualifies, so nothing new
blocks yet; migrated city bodies and the twelve frozen pages keep reporting as advisory.
The registry severities of the four checks stay `advisory`.

**Files:**
- Create: `tests/render/lib/promotions.ts`
- Create: `tests/render/fixtures/known_good/h3-image-first-bl-img.html`, `tests/render/fixtures/known_broken/h3-image-first-bl-img.html`
- Modify: `tests/render/meta.spec.ts` (one import line; two `test.describe` blocks appended)
- Modify: `tests/render/checks/layout.ts` (`layout-h3-image-first` comment + `isImg`)
- Modify: `tests/render/pages.spec.ts` (imports/targets typing; the `blocking` filter)
- Modify: `tests/render/targets.json` (add `_promotions_comment`, `new_page_rule`, `promotions`)
- Modify: `tests/py/test_targets_coverage.py` (append one test)
- Modify: `rules/design.md` (the two rule blocks)
- Modify (generated): `data/quality/scorecards/*-<today>.json`, `docs/reports/render-baseline-project4.md`

- [ ] **Step 1: Write the failing tests and fixtures**

Create `tests/render/fixtures/known_good/h3-image-first-bl-img.html`:

```html
<!doctype html><meta charset=utf-8><title>known-good: BodyImage .bl-img above the prose under each H3</title>
<meta name=viewport content="width=device-width,initial-scale=1">
<style>body{margin:0;font:16px/1.5 system-ui;padding:16px}.bl-prose{display:grid;gap:16px}.bl-img{width:100%;height:auto;display:block}</style>
<main>
  <!-- The markup src/components/BodyImage.astro renders on a rebuilt page: a bare
       img.bl-img as a sibling of the heading and its paragraphs inside .bl-prose. -->
  <section><div class="bl-prose">
    <h2>A Section Heading</h2>
    <p>An H2 lead paragraph that precedes its image, which is correct: the rule is scoped to H3 blocks only.</p>
    <img class="bl-img" src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" alt="h2 photo" width="1" height="1" loading="lazy" decoding="async">
    <h3>Step One: The Image Leads</h3>
    <img class="bl-img" src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" alt="first step photo" width="1" height="1" loading="lazy" decoding="async">
    <p>This paragraph is comfortably longer than the forty-character prose floor and follows its image.</p>
    <h3>Step Two: The Image Leads Again</h3>
    <img class="bl-img" src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" alt="second step photo" width="1" height="1" loading="lazy" decoding="async">
    <p>Another block of real prose, placed after the body photograph that belongs to this heading.</p>
  </div></section>
</main>
```
Create `tests/render/fixtures/known_broken/h3-image-first-bl-img.html`:
```html
<!doctype html><meta charset=utf-8><title>known-broken: BodyImage .bl-img below the prose under each H3</title>
<meta name=viewport content="width=device-width,initial-scale=1">
<style>body{margin:0;font:16px/1.5 system-ui;padding:16px}.bl-prose{display:grid;gap:16px}.bl-img{width:100%;height:auto;display:block}</style>
<main>
  <!-- The shape measured on dist/uk-blue-staffy-puppy-buying-guide/ (2026-09-26): an H3,
       its paragraph, then the body photograph. -->
  <section><div class="bl-prose">
    <h3>Step Four: A Deposit Reserves the Puppy</h3>
    <p>This paragraph is comfortably longer than the forty-character prose floor and sits ahead of the photo.</p>
    <img class="bl-img" src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" alt="deposit photo" width="1" height="1" loading="lazy" decoding="async">
    <h3>Step Five: Collection or Delivery</h3>
    <p>Another block of real prose, again placed ahead of the body photograph that belongs to this heading.</p>
    <img class="bl-img" src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" alt="delivery photo" width="1" height="1" loading="lazy" decoding="async">
  </div></section>
</main>
```
In `tests/render/meta.spec.ts`, directly after the `./lib/examined.js` import (Task 11), add:
```ts
import { severityFor, isNewPage, type Promotion, type NewPageRule } from './lib/promotions.js';
```
Append to the end of `tests/render/meta.spec.ts`:
```ts
/**
 * The image class a rebuilt page really renders.
 *
 * `layout-h3-image-first` counted only `img.sec-img`, which ships on /kit-preview/ alone:
 * every rebuilt page renders its body photographs through src/components/BodyImage.astro as
 * `img.bl-img`, so on the pages rule 17 puts an image under every H3 the check examined zero
 * blocks. This pair is BodyImage's own markup.
 */
test.describe('layout-h3-image-first [BodyImage .bl-img]', () => {
  const check = () => registry.find((c) => c.id === 'layout-h3-image-first')!;

  test('is silent when each H3 opens on its body photograph', async ({ page }, testInfo) => {
    const res = await page.goto(`${FIXTURE_BASE}/tests/render/fixtures/known_good/h3-image-first-bl-img.html`);
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined, 'both H3 blocks own a .bl-img').toBe(2);
    expect(r.defects.map((d) => d.message)).toEqual([]);
  });

  test('fires when the body photograph follows the prose', async ({ page }, testInfo) => {
    const res = await page.goto(`${FIXTURE_BASE}/tests/render/fixtures/known_broken/h3-image-first-bl-img.html`);
    expect(res?.status(), 'fixture must load').toBe(200);
    const r = await runCheck(check(), page, testInfo.project.use.viewport!.width, FIXTURE_CTX);
    expect(r.examined).toBe(2);
    expect(r.defects[0]?.count, 'both blocks are offenders').toBe(2);
  });
});

/**
 * Promotion is a record, not a flag flip.
 *
 * targets.json's `_comment` says a check enters advisory and is promoted after it has
 * passed its fixtures and made zero false reports across one full cluster — and until the
 * parity plan's Task 14 nothing recorded when that had happened, so `blocking` checks carried
 * no evidence of an advisory period at all. `promotions` is that record: every blocking check
 * has an entry, and a `new-pages` entry makes an advisory check blocking on the project 5
 * pages only (new-family page type, rebuilt from its board, not one of the twelve frozen
 * pages — `new_page_rule`, pinned to scripts/family_rules.py by tests/py/test_targets_coverage.py).
 */
test.describe('promotions: every blocking check is on record, and new-page promotions bind new pages only', () => {
  const here = dirname(fileURLToPath(import.meta.url));
  const t = JSON.parse(readFileSync(resolve(here, 'targets.json'), 'utf8')) as {
    promotions: Record<string, Promotion>;
    new_page_rule: NewPageRule;
  };
  const rule: NewPageRule = { page_types: ['location', 'comparison', 'blog'], built_before: ['blue-staffy-blog-guides'] };
  const rebuilt = new Set(['blue-staffy-puppies-hull', 'blue-staffy-blog-guides', 'index']);
  const promo: Record<string, Promotion> = {
    promoted: { scope: 'new-pages', since: '2026-09-26', cluster_cleared: 'x', false_reports: 0 },
  };

  test('isNewPage is a new-family, rebuilt, unfrozen page — by route or by bare key', () => {
    expect(isNewPage({ slug: 'uk-locations/blue-staffy-puppies-hull', page_type: 'location' }, rule, rebuilt)).toBe(true);
    expect(isNewPage({ slug: 'uk-locations/blue-staffy-puppies-leeds', page_type: 'location' }, rule, rebuilt)).toBe(false); // migrated, not rebuilt
    expect(isNewPage({ slug: 'blue-staffy-blog-guides', page_type: 'blog' }, rule, rebuilt)).toBe(false); // frozen
    expect(isNewPage({ slug: 'index', page_type: 'home' }, rule, rebuilt)).toBe(false); // not a new family
  });

  test('severityFor blocks a promoted check on a new page and nowhere else', () => {
    const hull = { slug: 'uk-locations/blue-staffy-puppies-hull', page_type: 'location' };
    const leeds = { slug: 'uk-locations/blue-staffy-puppies-leeds', page_type: 'location' };
    expect(severityFor({ id: 'promoted', severity: 'advisory' }, hull, promo, rule, rebuilt)).toBe('blocking');
    expect(severityFor({ id: 'promoted', severity: 'advisory' }, leeds, promo, rule, rebuilt)).toBe('advisory');
    expect(severityFor({ id: 'other', severity: 'advisory' }, hull, promo, rule, rebuilt)).toBe('advisory');
    expect(severityFor({ id: 'other', severity: 'blocking' }, leeds, promo, rule, rebuilt)).toBe('blocking');
  });

  test('every blocking check has a promotions entry with scope all', () => {
    const missing = registry
      .filter((c) => c.severity === 'blocking' && t.promotions[c.id]?.scope !== 'all')
      .map((c) => c.id)
      .sort();
    expect(missing, `blocking with no promotion on record: ${missing.join(', ')}`).toEqual([]);
  });

  test('every promotion names a registered check, fits its severity and records zero false reports', () => {
    const bad: string[] = [];
    for (const [id, p] of Object.entries(t.promotions)) {
      const c = registry.find((x) => x.id === id);
      if (!c) bad.push(`${id}: not a registered check`);
      else if (p.scope === 'all' && c.severity !== 'blocking') bad.push(`${id}: scope all but registered ${c.severity}`);
      else if (p.scope === 'new-pages' && c.severity !== 'advisory') bad.push(`${id}: new-pages scope on a ${c.severity} check`);
      if (!['all', 'new-pages'].includes(p.scope)) bad.push(`${id}: unknown scope ${p.scope}`);
      if (!/^\d{4}-\d{2}-\d{2}$/.test(p.since)) bad.push(`${id}: since ${p.since} is not a date`);
      if (p.false_reports !== 0) bad.push(`${id}: ${p.false_reports} false reports — not promotable`);
      if (!(p.cluster_cleared ?? '').trim()) bad.push(`${id}: no cluster_cleared evidence`);
    }
    expect(bad).toEqual([]);
  });

  test('the four project 5 promotions are on record', () => {
    for (const id of [
      'layout-hero-counter-separation',
      'layout-h3-image-first',
      'sem-section-opening-paragraph',
      'sem-title-case-headings',
    ]) {
      expect(t.promotions[id]?.scope, id).toBe('new-pages');
    }
  });
});
```
Append to `tests/py/test_targets_coverage.py`:
```python
def test_the_new_page_rule_is_family_rules_own(targets):
    """pages.spec.ts decides which pages a `new-pages` promotion blocks from
    `new_page_rule`; scripts/family_rules.py decides the same question for the board rules.
    One answer, spelled twice because one side is TypeScript — so pinned here."""
    import family_rules as FR
    rule = targets["new_page_rule"]
    assert tuple(rule["page_types"]) == FR.NEW_FAMILY_PAGE_TYPES
    assert set(rule["built_before"]) == FR.BUILT_BEFORE_SYSTEM_GAPS
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m pytest tests/py/test_targets_coverage.py -q -p no:cacheprovider`
Expected: `1 failed, 11 passed` — `KeyError: 'new_page_rule'`.

Run: `npx playwright test -c tests/render/playwright.config.ts meta.spec.ts --reporter=dot --grep "promotions|bl-img"`
Expected: FAIL — `Error: Cannot find module '…/tests/render/lib/promotions.js' imported from …/tests/render/meta.spec.ts`.

- [ ] **Step 3: Write the severity rule**

Create `tests/render/lib/promotions.ts`:

```ts
import type { Severity } from './registry.js';

/**
 * One row of targets.json `promotions`: the evidence that a check may fail a run.
 *
 * `all` — blocking everywhere; the check's registered severity is `blocking`.
 * `new-pages` — the check stays `advisory` in the registry and blocks on the project 5 pages
 * only (see isNewPage), so the twelve frozen pages and the migrated bodies keep reporting
 * without failing while every new page is held to the rule from its first build.
 */
export interface Promotion {
  scope: 'all' | 'new-pages';
  since: string;
  cluster_cleared: string;
  false_reports: number;
}

/** targets.json `new_page_rule` — scripts/family_rules.py's own two constants, pinned by pytest. */
export interface NewPageRule {
  page_types: string[];
  built_before: string[];
}

interface TargetLike {
  slug: string;
  page_type: string;
}

/**
 * A project 5 page: a new-family page type, rebuilt from its board (data/facts/rebuilt.json)
 * and not one of the twelve pages built before the system-gaps build. A city target's slug is
 * its route (`uk-locations/<key>`) while rebuilt.json holds the bare key, so both are tried.
 * A migrated page that has not been rebuilt is not new: its body is still WordPress markup.
 */
export function isNewPage(target: TargetLike, rule: NewPageRule, rebuilt: Set<string>): boolean {
  if (!rule.page_types.includes(target.page_type)) return false;
  const keys = [target.slug, target.slug.split('/').pop() ?? target.slug];
  return keys.some((k) => rebuilt.has(k)) && !keys.some((k) => rule.built_before.includes(k));
}

/** The severity a check carries on one target page. */
export function severityFor(
  check: { id: string; severity: Severity },
  target: TargetLike,
  promotions: Record<string, Promotion>,
  rule: NewPageRule,
  rebuilt: Set<string>,
): Severity {
  if (check.severity === 'blocking') return 'blocking';
  return promotions[check.id]?.scope === 'new-pages' && isNewPage(target, rule, rebuilt)
    ? 'blocking'
    : 'advisory';
}
```

- [ ] **Step 4: Record the promotions**

In `tests/render/targets.json`, directly before `  "families_by_page_type": {`, insert (the 16 scope-`all` rows are every check registered `severity: 'blocking'` today; a check registered blocking later needs its own row or the meta test fails):

```json
  "_promotions_comment": "Added 2026-09-26 (parity plan Task 14). `promotions` is the record the _comment's promotion rule never had: every check whose registered severity is `blocking` has a scope `all` entry, and a scope `new-pages` entry makes an ADVISORY check block on project 5 pages only — a `new_page_rule.page_types` page that is in data/facts/rebuilt.json and not in `new_page_rule.built_before` (tests/render/lib/promotions.ts). `new_page_rule` is scripts/family_rules.py's NEW_FAMILY_PAGE_TYPES and BUILT_BEFORE_SYSTEM_GAPS, pinned by tests/py/test_targets_coverage.py. meta.spec.ts fails a blocking check with no entry, an entry whose scope contradicts the registry, and any entry with a false report.",
  "new_page_rule": {
    "page_types": [
      "location",
      "comparison",
      "blog"
    ],
    "built_before": [
      "blue-staffy-blog-guides",
      "blue-staffy-health-uk",
      "blue-staffy-pup-sale-uk",
      "blue-staffy-uk-breeders",
      "buy-blue-staffy-puppies-uk",
      "buy-staffy-puppies-for-sale-uk",
      "index",
      "privacy-policy-uk",
      "thank-you-blue-staffy-puppies-journey",
      "uk-blue-staffy-breeders-contact",
      "uk-blue-staffy-puppy-buying-guide",
      "uk-staffordshire-bull-terrier-guide"
    ]
  },
  "promotions": {
    "a11y-hero-ledge-contrast": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "hero-aside-no-clip": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "img-alt-present-and-unique": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "img-sizes-matches-box": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "img-srcset-within-2x": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "layout-h3-image-first": {
      "scope": "new-pages",
      "since": "2026-09-26",
      "cluster_cleared": "retargeted 2026-09-26 to img.bl-img, the class src/components/BodyImage.astro renders; its reports on the twelve frozen pages are true reports (prose before the photo), which is why the scope is new pages only",
      "false_reports": 0
    },
    "layout-hero-counter-separation": {
      "scope": "new-pages",
      "since": "2026-09-26",
      "cluster_cleared": "examined the real counter strip on every rebuilt page since project 4 with zero rows (docs/reports/render-baseline-project4.md); blocks the 28+ project 5 counters",
      "false_reports": 0
    },
    "layout-min-font-size": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "layout-no-horizontal-overflow": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "layout-table-stacks-on-mobile": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "layout-tap-target-size": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "nav-anchors-resolve": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "nav-bottom-chrome-clear": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "nav-jump-target-lands": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "schema-date-modified-present": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "schema-no-visible-date": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "schema-sold-not-instock": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "sem-heading-order": {
      "scope": "all",
      "since": "2026-09-26",
      "cluster_cleared": "grandfathered: blocking before this record existed (2026-09-26); no advisory period is on record for it",
      "false_reports": 0
    },
    "sem-section-opening-paragraph": {
      "scope": "new-pages",
      "since": "2026-09-26",
      "cluster_cleared": "heading-straight-into-heading only (narrow predicate measured on the puppy cards); rule 17 pages open every body heading on an image then prose, which this never flags",
      "false_reports": 0
    },
    "sem-title-case-headings": {
      "scope": "new-pages",
      "since": "2026-09-26",
      "cluster_cleared": "caser ported from page_hardening_scan.check_title_case and tuned on this site's headings; FAQ questions are headings here and Title Case (rules/headings.md)",
      "false_reports": 0
    }
  },
```

- [ ] **Step 5: Retarget the check and wire per-page severity**

In `tests/render/checks/layout.ts`, `layout-h3-image-first`, replace the doc-comment paragraph:

```ts
 * Judged unit: H3 blocks that OWN a `.sec-img`. An H3 with no image of its own is not a
 * violation of an ordering rule, so counting it would inflate `examined` with units the
 * predicate never ran against. Seam emblems and icons are excluded on purpose: they are
 * decorative and would otherwise register as "the image" and fail every clean page.
 */
```
with:
```ts
 * Judged unit: H3 blocks that OWN a sectional image — `img.sec-img` (the kit specimen on
 * /kit-preview/) or `img.bl-img` (src/components/BodyImage.astro, the body photograph every
 * rebuilt page renders). Until 2026-09-26 only `.sec-img` counted, and no real page carries
 * one, so the check examined zero blocks on exactly the pages rule 17 puts an H3 image on.
 * An H3 with no image of its own is not a violation of an ordering rule, so counting it
 * would inflate `examined` with units the predicate never ran against. Seam emblems and
 * icons are excluded on purpose: they are decorative and would otherwise register as "the
 * image" and fail every clean page.
 */
```
and replace:
```ts
          const isImg =
            (n.tagName === 'IMG' && n.classList.contains('sec-img')) || !!n.querySelector?.('img.sec-img');
```
with:
```ts
          const isImg = n.matches('img.sec-img, img.bl-img') || !!n.querySelector?.('img.sec-img, img.bl-img');
```
In `tests/render/pages.spec.ts` replace:
```ts
import type { Defect } from './lib/registry.js';

const here = dirname(fileURLToPath(import.meta.url));
const targets = JSON.parse(readFileSync(resolve(here, 'targets.json'), 'utf8')) as {
  families_by_page_type: Record<string, string[]>;
  pages: { slug: string; page_type: string; corpus: boolean }[];
};
```
with:
```ts
import type { Defect } from './lib/registry.js';
import { severityFor, type Promotion, type NewPageRule } from './lib/promotions.js';

const here = dirname(fileURLToPath(import.meta.url));
const targets = JSON.parse(readFileSync(resolve(here, 'targets.json'), 'utf8')) as {
  families_by_page_type: Record<string, string[]>;
  pages: { slug: string; page_type: string; corpus: boolean }[];
  promotions: Record<string, Promotion>;
  new_page_rule: NewPageRule;
};
// The project 5 pages a `new-pages` promotion blocks on are the rebuilt ones (lib/promotions.ts).
const rebuilt = new Set<string>(
  JSON.parse(readFileSync(resolve(here, '..', '..', 'data', 'facts', 'rebuilt.json'), 'utf8')) as string[],
);
```
and replace:
```ts
    const blocking = defects.filter(
      (d) =>
        registry.find((c) => c.id === d.checkId)?.severity === 'blocking' &&
        !overridden.has(d.checkId),
    );
```
with:
```ts
    // Severity is per PAGE now: a `new-pages` promotion (targets.json) blocks on a project 5
    // page and stays advisory on the twelve frozen pages and the migrated bodies.
    const blocking = defects.filter((d) => {
      const check = registry.find((c) => c.id === d.checkId);
      return (
        !!check &&
        severityFor(check, target, targets.promotions, targets.new_page_rule, rebuilt) === 'blocking' &&
        !overridden.has(d.checkId)
      );
    });
```
In `rules/design.md` (the `layout-h3-image-first` block) replace:
```
Only `.sec-img` counts; seam emblems and icons are decorative and must never register as "the image". An H3 that owns no image is not a violation and must not be counted as examined. Enforced by `tests/render/checks/layout.ts::layout-h3-image-first`.
```
with:
```
Only a sectional image counts — `.sec-img` (the kit specimen) or `.bl-img` (`src/components/BodyImage.astro`, the body photograph every rebuilt page renders); seam emblems and icons are decorative and must never register as "the image". An H3 that owns no image is not a violation and must not be counted as examined. Enforced by `tests/render/checks/layout.ts::layout-h3-image-first` — blocking on project 5 pages (targets.json `promotions`, scope `new-pages`), advisory on the twelve pages built before them.
```
and in the `layout-hero-counter-separation` block append to the sentence ending `a page with a tone shift but no rule still fails.` the words ` Blocking on project 5 pages (targets.json `promotions`, scope `new-pages`).`

- [ ] **Step 6: Run to verify it passes**

Run: `python3 -m pytest tests/py/test_targets_coverage.py tests/py/test_rules_index.py tests/py/test_harness_vocabulary.py -q -p no:cacheprovider && npm run -s check:markers | tail -1`
Expected: all pass; `examined 280 files; 0 problems` (no source-repo marker may enter tests/render or rules/).

Run: `npx playwright test -c tests/render/playwright.config.ts meta.spec.ts --reporter=dot 2>&1 | tail -3`
Expected: `0 failed` — `379 passed, 38 skipped` without `PUBLIC_FORMSPREE_ID` (more pass with `.env` loaded).

- [ ] **Step 7: Full page run (writes today's scorecards through Task 11's guard)**

Needs `PUBLIC_FORMSPREE_ID` in the environment (`.env`, as `test:render:*` loads it); without it `form-inquiry-contract` examines zero nodes and Guard 2 FAILs — that is the guard working. About 8 minutes.

Run: `npm run -s build && npm run test:render:pages -- --reporter=dot; echo "exit=$?"`
Expected: `3 failed` — `uk-locations/blue-staffy-puppies-uk` at 375/768/1280, `[NAV] 1 of 2 in-page links land outside …` (`nav-jump-target-lands`, blocking and pre-existing: the same row is in the 2026-09-19 and 2026-09-22 scorecards) — `57 passed`, then the scorecard still runs and prints one line per page and `--- 195 defect ROWS across 20 pages` (the number may move with earlier tasks), `exit=1` from the pre-existing NAV row. `layout-h3-image-first` now examines real pages: 21 blocks on the buying guide, 6 on the breed guide, 3 each on the homepage, the for-sale page and kit-preview; its reports on those frozen pages are advisory.

Run: `npx playwright test -c tests/render/playwright.config.ts meta.spec.ts --reporter=dot --grep "zero-examined guard"` → `9 passed` against today's cards.

Regenerate the baseline report the committed scorecards now disagree with: `python3 scripts/render_baseline.py --write docs/reports/render-baseline-project4.md`, then `python3 -m pytest tests/py/test_render_baseline.py -q -p no:cacheprovider` → `17 passed`.

- [ ] **Step 8: check:all**

Run: `npm run -s build && npm run -s check:all; echo "exit=$?"`
Expected: `exit=0`.

- [ ] **Step 9: Commit**

```bash
git add tests/render/lib/promotions.ts tests/render/fixtures/known_good/h3-image-first-bl-img.html tests/render/fixtures/known_broken/h3-image-first-bl-img.html tests/render/meta.spec.ts tests/render/checks/layout.ts tests/render/pages.spec.ts tests/render/targets.json tests/py/test_targets_coverage.py rules/design.md data/quality/scorecards docs/reports/render-baseline-project4.md
git commit -m "$(cat <<'EOF'
render: H3 image-first sees .bl-img; promotions record; four checks block on new pages

layout-h3-image-first matched only the kit specimen's .sec-img and examined zero blocks
on every real page; it now matches BodyImage's .bl-img. targets.json records every
promotion; hero/counter separation, H3 image-first, opening paragraph and Title Case
block on project 5 pages only (new-family, rebuilt, not frozen) and stay advisory on
the twelve built pages. Scorecards from the full run and the regenerated baseline.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```


### Task 15: page_hardening_scan.py scope: city template + its data + src/components/kit/**; replace CAG-only SPEC_MANDATED

Audit Wave 2 row 13 / Appendix C 18.1, 18.2. Verified 2026-09-26: a scoped run on
`uk-locations/blue-staffy-puppies-hull` read **2** source files (BaseLayout, global.css);
the site sweep read **36** and no kit file; `SPEC_MANDATED` named ten source-repo classes no
BSUK file renders. After: the city run reads 5 (`src/pages/uk-locations/[slug].astro`,
`data/locations.json`, `src/lib/site.ts` via the template's own imports, plus the two shared
files); the sweep reads 57, all 21 kit components among them.

Reading the kit surfaced one scanner false positive, fixed here because Task 25 runs this
scan with `--fail-on-error` on every page: `css-math-spacing` read the `e-4` inside
`var(--space-4)` as a minus with no spaces and raised an ERROR on CounterStrip, Hero,
SiteFooterKit and SiteHeaderKit (already visible on a scoped run of `index`: 3 ERRORs → 0).
Custom property names are blanked before the test. The kit renders its roots with Astro's
`class:list={[…]}`, which `_rendered_classes` did not read, so without that parser every kit
root would read as styled-but-never-rendered.

**Files:**
- Modify: `scripts/page_hardening_scan.py` (docstring; import; `SRC_GLOBS`; new `page_source()`; `src_files()`; `check_css_math()`; `SPEC_MANDATED`; `_rendered_classes()`; `_global_css()`)
- Create: `tests/py/test_page_hardening_scope.py`
- Modify: `tests/py/test_page_hardening.py` (the drift fixture's mandated class)
- Modify: `.claude/skills/bsuk-page-hardening/SKILL.md` (triage table row)

- [ ] **Step 1: Write the failing tests**

Create `tests/py/test_page_hardening_scope.py`:

```python
"""`page_hardening_scan.py` reads what a project 5 page is made of (audit 18.1 / 18.2).

A scoped run resolved `src/pages/<slug>/index.astro` only, so `uk-locations/<city>` — a
dynamic route — scanned BaseLayout.astro and global.css and nothing else; the site sweep
globbed `src/components/*.astro` without recursing, so no `src/components/kit/**` file was
ever read; and `SPEC_MANDATED` named source-repo classes no BSUK component renders. The
harden sprint on every city page would have been a clean scan of two files."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import page_hardening_scan as H  # noqa: E402

KIT = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "src/components/kit").glob("*.astro"))


def test_a_city_page_scans_the_city_template_and_its_data():
    for slug in ("uk-locations/blue-staffy-puppies-hull", "blue-staffy-puppies-hull"):
        files = H.src_files([slug], root=str(ROOT))
        assert "src/pages/uk-locations/[slug].astro" in files, slug
        assert "data/locations.json" in files, slug          # the template's own import


def test_a_blog_post_and_a_puppy_page_scan_their_dynamic_templates():
    post = H.src_files(["how-to-choose-the-right-blue-staffy-puppy-for-your-family"], root=str(ROOT))
    assert "src/pages/[...post].astro" in post
    pup = H.src_files(["available-puppies/roman"], root=str(ROOT))
    assert "src/pages/available-puppies/[slug].astro" in pup


def test_a_static_page_still_wins_over_a_dynamic_sibling():
    files = H.src_files(["blue-staffy-health-uk"], root=str(ROOT))
    assert "src/pages/blue-staffy-health-uk/index.astro" in files
    assert "src/pages/[...post].astro" not in files


def test_the_site_sweep_reads_every_kit_component():
    files = set(H.src_files([], root=str(ROOT)))
    assert KIT and set(KIT) <= files, sorted(set(KIT) - files)


def test_a_dynamic_route_resolves_in_a_fixture_tree(tmp_path):
    (tmp_path / "src/pages/uk-locations").mkdir(parents=True)
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "blue-staffy-puppies-x"}]))
    (tmp_path / "src/pages/uk-locations/[slug].astro").write_text(
        "---\nimport locations from '../../../data/locations.json';\n---\n<p/>\n")
    files = H.src_files(["uk-locations/blue-staffy-puppies-x"], root=str(tmp_path))
    assert "src/pages/uk-locations/[slug].astro" in files
    assert "data/locations.json" in files


def test_class_list_is_read_as_rendered():
    harvested, literal = H._rendered_classes(
        "<aside class:list={['kit-dial', cls]}><span class:list={['kit-chip', avail && 'ok']}>")
    assert {"kit-dial", "kit-chip", "ok"} <= harvested
    assert "kit-dial" not in literal          # the orphan half stays on plain class="…"


def test_spec_mandated_names_kit_classes_only():
    rendered = set()
    for rel in KIT:
        rendered |= H._rendered_classes((ROOT / rel).read_text(encoding="utf-8"))[0]
    assert H.SPEC_MANDATED and H.SPEC_MANDATED <= rendered, sorted(H.SPEC_MANDATED - rendered)
    for residue in ("doc-stack", "otA", "geo-pin", "chkB", "seam", "xsell", "vflags"):
        assert residue not in H.SPEC_MANDATED


def test_the_kit_renders_every_mandated_component_it_styles():
    H.findings.clear()
    H.check_class_drift([(rel, (ROOT / rel).read_text(encoding="utf-8")) for rel in KIT])
    errors = [f for f in H.findings if f["sev"] == "ERROR" and f["check"] == "markup-css-drift"]
    H.findings.clear()
    assert errors == []


def test_a_custom_property_name_is_not_css_math(tmp_path):
    """Reading the kit surfaced `calc(-1 * var(--space-4))` as invalid math: the `e-4` in the
    property NAME matched the no-space-minus pattern. A real missing space still fails."""
    css = tmp_path / "a.css"
    css.write_text(".a{margin-top:calc(-1 * var(--space-4));height:calc(450px - 2 * var(--space-6))}\n"
                   ".b{font-size:clamp(1.7rem,1.2rem+2.2vw,2.6rem)}\n")
    H.findings.clear()
    H.check_css_math([str(css)])
    lines = [f["line"] for f in H.findings if f["check"] == "css-math-spacing"]
    H.findings.clear()
    assert lines == [2]
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/py/test_page_hardening_scope.py -q -p no:cacheprovider`
Expected: `7 failed, 2 passed` — the city, blog/puppy, kit-sweep, fixture-tree, `class:list`, SPEC_MANDATED and custom-property tests fail (`assert 'src/pages/uk-locations/[slug].astro' in [...]`, `KIT ⊄ files`, `'kit-dial' not in harvested`, `lines == [1, 2]`); `test_a_static_page_still_wins_over_a_dynamic_sibling` and `test_the_kit_renders_every_mandated_component_it_styles` pass.

- [ ] **Step 3: Implement the scope, the parser, the mandated set and the math fix**

In `scripts/page_hardening_scan.py`:

(a) In the module docstring replace:

```
Scoped-run source selection (2026-09-10): a scoped run (one or more slugs)
examines the page's own file plus the components it actually imports, plus
BaseLayout.astro/global.css — see src_files()/imports_of(). Before this date
a scoped run examined only the page file itself and could miss a defect
shipped in an imported component.
"""
```
with:
```
Scoped-run source selection (2026-09-10): a scoped run (one or more slugs)
examines the page's own file plus the components it actually imports, plus
BaseLayout.astro/global.css — see src_files()/imports_of(). Before this date
a scoped run examined only the page file itself and could miss a defect
shipped in an imported component.

2026-09-26: a page rendered by a DYNAMIC route (a city at uk-locations/<city>, a
puppy, a blog post) resolves to its template — `src/pages/uk-locations/[slug].astro`
— and that template's imports, data/locations.json among them (page_source()).
The site sweep recurses into src/components/, so the kit is read too.
"""
```
(b) Replace:
```python
import re, sys, glob, os, json, pathlib, argparse
from _slugs import select_pages

SRC_GLOBS = ["src/pages/**/*.astro", "src/components/*.astro",
             "src/layouts/*.astro", "src/styles/*.css"]
```
with:
```python
import re, sys, glob, os, json, pathlib, argparse
from _slugs import select_pages, resolve_page

# `src/components/**` recurses: the kit (`src/components/kit/`) is where every rebuilt and
# project 5 page's sections live, and a non-recursive glob never read one of its files.
SRC_GLOBS = ["src/pages/**/*.astro", "src/components/**/*.astro",
             "src/layouts/*.astro", "src/styles/*.css"]
```
(c) Directly before `def src_files(slugs, root="."):` insert:
```python
def page_source(slug, root="."):
    """The source file a built page is rendered from, or None.

    A static page is `src/pages/<route>/index.astro` (`src/pages/index.astro` for the root).
    Every other page is a DYNAMIC route: a city is `uk-locations/<city>` rendered by
    `src/pages/uk-locations/[slug].astro`, a puppy by `available-puppies/[slug].astro`, a
    blog post by `src/pages/[...post].astro`. Before 2026-09-26 only the static form was
    tried, so a city page's scoped run read BaseLayout and global.css and nothing of the page.
    A bare city key is resolved to its route first (scripts/_slugs.py, Known Issue 39); the
    dynamic file is looked up in the route's parent directory with os.listdir, because glob
    reads the `[` in `[slug].astro` as a character class."""
    try:
        route = resolve_page(slug, root)[1]
    except ValueError:
        return None
    if not route:
        return "src/pages/index.astro"
    static = f"src/pages/{route}/index.astro"
    if os.path.isfile(os.path.join(root, static)):
        return static
    parent = os.path.dirname(route)
    folder = os.path.join(root, "src", "pages", parent)
    if not os.path.isdir(folder):
        return None
    dynamic = sorted(f for f in os.listdir(folder) if f.startswith("[") and f.endswith("].astro"))
    if not dynamic:
        return None
    return "/".join(p for p in ("src/pages", parent, dynamic[0]) if p)
```
(d) In `src_files`, replace:
```python
        for g in ("src/components/*.astro", "src/layouts/*.astro", "src/styles/*.css"):
```
with:
```python
        for g in ("src/components/**/*.astro", "src/layouts/*.astro", "src/styles/*.css"):
```
and replace:
```python
    for s in slugs:
        if s in ("index", "", "/"):
            page_file = "src/pages/index.astro"
        else:
            page_file = f"src/pages/{s.strip('/')}/index.astro"
        if not os.path.isfile(os.path.join(root, page_file)):
            continue
```
with:
```python
    for s in slugs:
        page_file = page_source(s, root)
        if page_file is None:
            continue
```
(e) In `check_css_math`, replace:
```python
            for m in pat.finditer(ln):
                expr = m.group(0)
                # a +/- with a non-space on either side, ignoring signs after ( or ,
                if re.search(r"(?<=[0-9a-z%\)])\+(?=[^\s])|(?<=[0-9a-z%\)])\s\-(?=[^\s])|(?<=[0-9a-z%\)])\-(?=[.\d])", expr):
```
with:
```python
            for m in pat.finditer(ln):
                expr = m.group(0)
                # A custom property's NAME is not arithmetic: `var(--space-4)` read as
                # `e-4` failed every kit component on 2026-09-26, the day the scan first
                # read src/components/kit/. Names are blanked before the test.
                bare = re.sub(r"--[\w-]+", "--v", expr)
                # a +/- with a non-space on either side, ignoring signs after ( or ,
                if re.search(r"(?<=[0-9a-z%\)])\+(?=[^\s])|(?<=[0-9a-z%\)])\s\-(?=[^\s])|(?<=[0-9a-z%\)])\-(?=[.\d])", bare):
```
(f) Replace the `SPEC_MANDATED = {…}` assignment (the ten source-repo classes) with:
```python
#
# Re-based 2026-09-26. The set above was the source repo's for-sale components, none of which
# any BSUK file renders, so the ERROR half of this check could never fire here. These are the
# kit components the working rules require on a rebuilt page, each styled and rendered in its
# own kit file: the counter strip (rule 16; layout-hero-counter-separation hooks on
# .counter-wrap), the stacking table (rule 13), the hero (rule 16), the page dial, the page
# nav, the section sheet, the FAQ block and the statement label.
# tests/py/test_page_hardening_scope.py holds every member to a class a kit file renders.
SPEC_MANDATED = {
    "counter-wrap", "stack-table", "kit-hero", "kit-dial", "kit-nav", "kit-sheet",
    "kit-faq", "stmt-label",
}
```
(g) At the end of `_rendered_classes`, replace:
```python
    for m in re.finditer(r"class(?:Name)?=\{([^}]*)\}", markup):
        for q in _QUOTED.findall(m.group(1)):
            harvested.update((q[0] or q[1]).split())
    return harvested, literal
```
with:
```python
    for m in re.finditer(r"class(?:Name)?=\{([^}]*)\}", markup):
        for q in _QUOTED.findall(m.group(1)):
            harvested.update((q[0] or q[1]).split())
    # Astro's class:list={['kit-dial', cls]} — how every kit component renders its root. Not
    # read before 2026-09-26, so each kit root would have read as styled-but-never-rendered.
    for m in re.finditer(r"class:list=\{(\[.*?\])\}", markup, re.S):
        for q in _QUOTED.findall(m.group(1)):
            harvested.update((q[0] or q[1]).split())
    return harvested, literal
```
(h) In `_global_css`, replace:
```python
        for g in ("src/styles/*.css", "src/layouts/*.astro", "src/components/*.astro"):
            for p in glob.glob(g):
```
with:
```python
        for g in ("src/styles/*.css", "src/layouts/*.astro", "src/components/**/*.astro"):
            for p in glob.glob(g, recursive=True):
```

In `tests/py/test_page_hardening.py` the drift fixture names the retired mandated class. Apply:

```bash
python3 - <<'EOF'
import pathlib
p = pathlib.Path("tests/py/test_page_hardening.py"); s = p.read_text(encoding="utf-8")
s = s.replace('.doc-stack{display:grid}', '.stack-table{display:grid}')
s = s.replace('assert {"faqC-q", "doc-stack"} <= listed, listed', 'assert {"faqC-q", "stack-table"} <= listed, listed')
s = s.replace('""".doc-stack is mandated by the for-sale spec — a missing component, not dead code."""',
              '""".stack-table is mandated (working rule 13, the kit\'s DataTable) — a missing component, not dead code."""')
s = s.replace('assert "doc-stack" in _listed(errors)', 'assert "stack-table" in _listed(errors)')
s = s.replace('assert "doc-stack" not in _listed(warns)', 'assert "stack-table" not in _listed(warns)')
assert "doc-stack" not in s
p.write_text(s, encoding="utf-8")
EOF
```
In `.claude/skills/bsuk-page-hardening/SKILL.md`, in the triage table row that begins `| **Missing component** |`, replace the middle cell `the spec mandates it (`.doc-stack`, `.otA`, `.geo-pin`, `.read-img`, `.vflags`, `.chkB`, `.fs-video`, `.xsell`, `.seam`)` with:
```
a working rule mandates it — `SPEC_MANDATED` in `scripts/page_hardening_scan.py`: the kit's `.counter-wrap`, `.stack-table`, `.kit-hero`, `.kit-dial`, `.kit-nav`, `.kit-sheet`, `.kit-faq`, `.stmt-label`
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/py/test_page_hardening_scope.py tests/py/test_page_hardening.py tests/py/test_agent_facts.py tests/py/test_skills_frontmatter.py -q -p no:cacheprovider`
Expected: all pass (`69 passed` for the two hardening files).

Run: `python3 scripts/page_hardening_scan.py uk-locations/blue-staffy-puppies-hull | head -1; python3 scripts/page_hardening_scan.py | grep -c css-math-spacing; python3 scripts/page_hardening_scan.py index | tail -1`
Expected: `BSUK page-hardening scan — 5 source files, 1 built pages`; `0`; `0 ERROR · 7 WARN`.

- [ ] **Step 5: check:all**

Run: `npm run -s build && npm run -s check:all; echo "exit=$?"`
Expected: `exit=0`.

- [ ] **Step 6: Commit**

```bash
git add scripts/page_hardening_scan.py tests/py/test_page_hardening_scope.py tests/py/test_page_hardening.py .claude/skills/bsuk-page-hardening/SKILL.md
git commit -m "$(cat <<'EOF'
harden: scan reads the city template, its data and the kit

A scoped run on a city page read two shared files; it now resolves the dynamic route
(uk-locations/[slug].astro and its imports, data/locations.json among them). The site
sweep recurses into src/components/kit/. SPEC_MANDATED names the kit components the
working rules require; class:list roots are read as rendered; var(--x-4) is no longer
read as invalid CSS math.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```


### Task 16: scripts/rendered_changes.py — dist-hash diff; writes docs/reports/rendered-changes.json

> **Controller amendment (integration replay):** hashes page *content* — inline `<style>`, non-JSON-LD scripts and `/_astro/` asset links are stripped before hashing. Without it Task 8's shared CSS made all 51 pages "changed"; with it the replay reports exactly the 12 rebuilt pages. Test `test_a_style_or_script_bundle_change_alone_is_not_a_rendered_change` pins it.

Audit D6 / Wave 2 row 14 / Appendix D M13, 22.6. IndexNow's `--changed` diffed source paths
matching `src/pages/<x>/index.astro` against `origin/main` (which does not exist): it could
never name a city page, a puppy, a blog post or a shared-component change.

**Fixed interface (Task 26 reads it):** `python3 scripts/rendered_changes.py --base
<dir-or-ref> [--json]`. `<dir>` is a directory holding an earlier build (a copy of dist/);
`<ref>` is a git ref whose committed `data/quality/dist-hashes.json` is the earlier build's
manifest. `--json` writes `docs/reports/rendered-changes.json` =
`{"base": "<dir-or-ref as given>", "head": "<40-char HEAD sha>", "changed": [slugs]}` —
exactly those three keys; `changed` = modified ∪ added, sorted; a slug is the dist route
(`uk-locations/<city>`, `available-puppies/roman`), `index` for the root; specimen routes
(`board-preview/`, `kit-preview/`) excluded. The file is under `docs/reports/**/*.json`,
which `.gitignore` excludes, so it is a working-tree artefact of the close. `--json` also
refreshes `data/quality/dist-hashes.json` = `{"head": sha, "pages": {slug: sha256}}`, which
IS committed so the next close can pass that commit as `--base`. Removed slugs are printed,
not written. Exit 0 on a completed diff, 2 when it cannot run.

Verified: two consecutive builds of an unchanged tree hash identically (`0 changed`); a build
with a different `PUBLIC_FORMSPREE_ID` changes the four form pages — so generate the manifest
with the same `.env` every build uses. `indexnow_submit.py --changed` now reads the report
instead of the source diff (still behind both release guards).

**Files:**
- Create: `scripts/rendered_changes.py`
- Create: `tests/py/test_rendered_changes.py`
- Create (generated): `data/quality/dist-hashes.json`
- Modify: `scripts/indexnow_submit.py` (docstring usage line; `changed_slugs()`; `--changed` help; the empty-list message; drop the now-unused `import subprocess`)
- Modify: `tests/py/test_indexnow_submit.py` (append two tests)
- Modify: `.claude/skills/bsuk-indexing/SKILL.md` (STEP 4 `--changed` block)
- Regenerate: `docs/reference/system-registry.md`

- [ ] **Step 1: Write the failing tests**

Create `tests/py/test_rendered_changes.py`:

```python
"""`scripts/rendered_changes.py` — the slugs whose RENDERED output changed (audit D6, M13).

IndexNow's `--changed` diffed SOURCE paths matching `src/pages/<x>/index.astro`, so it could
never see a city page (`uk-locations/[slug].astro`), a puppy, a blog post or any shared
component edit: project 6 would have submitted none of project 5's pages. The honest list is
the built output itself — hash every dist/**/index.html, compare with the build the last
close recorded, and name what moved."""
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import rendered_changes as RC  # noqa: E402

SCRIPT = str(ROOT / "scripts" / "rendered_changes.py")


def _dist(base, pages):
    for key, html in pages.items():
        d = base if key == "index" else base / key
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(html, encoding="utf-8")
    return base


def test_hashes_key_every_built_page_and_skip_the_specimens(tmp_path):
    dist = _dist(tmp_path / "dist", {"index": "a", "uk-locations/blue-staffy-puppies-hull": "b",
                                     "kit-preview": "c", "board-preview/x": "d"})
    h = RC.page_hashes(dist)
    assert sorted(h) == ["index", "uk-locations/blue-staffy-puppies-hull"]
    assert len(h["index"]) == 64


def test_diff_names_modified_and_added_as_changed_and_removed_apart():
    base = {"index": "1", "a": "1", "gone": "1"}
    head = {"index": "1", "a": "2", "new": "1"}
    assert RC.diff(base, head) == {"changed": ["a", "new"], "removed": ["gone"]}


def test_a_directory_base_is_hashed_directly(tmp_path):
    old = _dist(tmp_path / "old", {"index": "same", "uk-locations/x": "before"})
    RC.ROOT = tmp_path
    try:
        assert RC.base_hashes(str(old)) == RC.page_hashes(old)
    finally:
        RC.ROOT = ROOT


def test_a_ref_base_reads_the_manifest_that_ref_committed(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "data/quality").mkdir(parents=True)
    (tmp_path / "data/quality/dist-hashes.json").write_text(
        json.dumps({"head": "abc", "pages": {"index": "h1"}}), encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "m"],
                   cwd=tmp_path, check=True)
    RC.ROOT = tmp_path
    try:
        assert RC.base_hashes("HEAD") == {"index": "h1"}
        with pytest.raises(RC.BaseError, match="no data/quality/dist-hashes.json at"):
            RC.base_hashes("no-such-ref")
    finally:
        RC.ROOT = ROOT


def test_the_cli_writes_the_report_and_the_manifest(tmp_path):
    """The fixed interface Task 26 (measurement ledger) reads:
    docs/reports/rendered-changes.json = {"base", "head", "changed"}."""
    for cmd in (["git", "init", "-q"], ["git", "-c", "user.email=t@t", "-c", "user.name=t",
                                        "commit", "-q", "--allow-empty", "-m", "m"]):
        subprocess.run(cmd, cwd=tmp_path, check=True)
    old = _dist(tmp_path / "old", {"index": "same", "uk-locations/x": "before"})
    _dist(tmp_path / "dist", {"index": "same", "uk-locations/x": "after", "blog-post": "new"})
    r = subprocess.run([sys.executable, SCRIPT, "--base", str(old), "--json"], cwd=tmp_path,
                       capture_output=True, text=True, env={"RENDERED_CHANGES_ROOT": str(tmp_path),
                                                            "PATH": "/usr/bin:/bin"})
    assert r.returncode == 0, r.stdout + r.stderr
    rep = json.loads((tmp_path / "docs/reports/rendered-changes.json").read_text())
    assert set(rep) == {"base", "head", "changed"}
    assert rep["base"] == str(old) and len(rep["head"]) == 40
    assert rep["changed"] == ["blog-post", "uk-locations/x"]
    man = json.loads((tmp_path / "data/quality/dist-hashes.json").read_text())
    assert man["head"] == rep["head"] and sorted(man["pages"]) == ["blog-post", "index", "uk-locations/x"]
    assert "2 changed" in r.stdout


def test_the_cli_refuses_without_a_build(tmp_path):
    r = subprocess.run([sys.executable, SCRIPT, "--base", "HEAD"], cwd=tmp_path, capture_output=True,
                       text=True, env={"RENDERED_CHANGES_ROOT": str(tmp_path), "PATH": "/usr/bin:/bin"})
    assert r.returncode == 2 and "dist/ does not exist" in r.stdout


def test_a_style_or_script_bundle_change_alone_is_not_a_rendered_change():
    """A shared CSS edit rewrites every page's inline <style> and hashed asset links; that is
    not a change a search engine indexes, so IndexNow must not be told about all 51 pages.
    Text and JSON-LD still count."""
    base = ('<html><head><style>.a{color:red}</style><link rel="stylesheet" href="/_astro/x.AAA.css">'
            '<script type="module" src="/_astro/p.AAA.js"></script>'
            '<script type="application/ld+json">{"@type":"Product"}</script></head>'
            '<body><h1>Blue Staffy</h1><script>var n=1</script></body></html>')
    css_only = (base.replace(".a{color:red}", ".a{color:blue}").replace("x.AAA.css", "x.BBB.css")
                .replace("p.AAA.js", "p.BBB.js").replace("var n=1", "var n=2"))
    text = base.replace("Blue Staffy", "Blue Staffy Puppies")
    schema = base.replace('"Product"', '"Offer"')
    h = RC.content_hash
    assert h(base) == h(css_only)
    assert h(base) != h(text)
    assert h(base) != h(schema)
```
Append to `tests/py/test_indexnow_submit.py`:
```python
# ── --changed reads the dist-hash list (parity plan Task 16, audit D6) ────────────────────
def test_changed_submits_the_rendered_changes_including_city_pages(monkeypatch, tmp_path, capsys):
    """The old --changed diffed `src/pages/<x>/index.astro` and could never name a city page.
    It now reads docs/reports/rendered-changes.json, which scripts/rendered_changes.py writes
    from the built output itself."""
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://example.invalid")
    (tmp_path / "docs/reports").mkdir(parents=True)
    (tmp_path / "docs/reports/rendered-changes.json").write_text(
        '{"base": "abc", "head": "def", "changed": ["index", "uk-locations/blue-staffy-puppies-hull"]}',
        encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["indexnow_submit.py", "--dry-run", "--changed"])
    assert mod.main() == 0
    out = capsys.readouterr().out
    assert "https://example.invalid/uk-locations/blue-staffy-puppies-hull/" in out
    assert "  + https://example.invalid/\n" in out
    assert "/index/" not in out


def test_changed_refuses_without_the_rendered_changes_report(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://example.invalid")
    assert _run(mod, monkeypatch, ["--dry-run", "--changed"]) == 2
    assert "scripts/rendered_changes.py --base" in capsys.readouterr().err
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m pytest tests/py/test_rendered_changes.py tests/py/test_indexnow_submit.py -q -p no:cacheprovider`
Expected: `ModuleNotFoundError: No module named 'rendered_changes'` (collection error). Then `python3 -m pytest tests/py/test_indexnow_submit.py -q -p no:cacheprovider` → `2 failed, 11 passed`: `'…/uk-locations/blue-staffy-puppies-hull/' in 'no changed page sources vs origin/main — nothing to submit\n'` and `Failed: DID NOT RAISE <class 'SystemExit'>`.

- [ ] **Step 3: Write the diff**

Create `scripts/rendered_changes.py`:

```python
#!/usr/bin/env python3
"""rendered_changes.py — which built pages' RENDERED output changed (a dist-hash diff).

  python3 scripts/rendered_changes.py --base <dir-or-ref> [--json]

IndexNow must be told about every page whose rendered HTML changed, and a source diff cannot
say which those are: a city page renders from `src/pages/uk-locations/[slug].astro` plus a row
of data/locations.json, and a shared component edit changes every page that mounts it (audit
D6 / M13). So this hashes every dist/**/index.html (the specimen routes excepted) and compares
the hashes with an earlier build:

  <dir>  a directory holding the earlier build — a copy of dist/ taken before the work
  <ref>  a git ref; the earlier build is the data/quality/dist-hashes.json that ref committed

Prints the changed slugs (modified or added) and the removed ones. `--json` writes
docs/reports/rendered-changes.json = {"base": <dir-or-ref>, "head": <sha>, "changed": [slugs]}
(read by `indexnow_submit.py --changed` and scripts/measurement_ledger.py) and refreshes
data/quality/dist-hashes.json, the manifest the NEXT close diffs against — commit it with the
close. A slug is the page's dist route (`uk-locations/<city>`), `index` for the root.

Exit 0 on a completed diff, 2 when it cannot run (no dist/, an unreadable base).
RENDERED_CHANGES_ROOT points it at another tree (tests only).
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(os.environ.get("RENDERED_CHANGES_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
MANIFEST = pathlib.Path("data") / "quality" / "dist-hashes.json"
REPORT = pathlib.Path("docs") / "reports" / "rendered-changes.json"
SPECIMEN_PREFIXES = ("board-preview/", "kit-preview/")


class BaseError(Exception):
    pass


def page_hashes(dist):
    """{slug: content_hash of the built index.html} for every page but the specimen routes."""
    dist = pathlib.Path(dist)
    out = {}
    for page in sorted(dist.glob("**/index.html")):
        rel = page.parent.relative_to(dist).as_posix()
        slug = "index" if rel == "." else rel
        if (slug + "/").startswith(SPECIMEN_PREFIXES):
            continue
        out[slug] = content_hash(page.read_text(encoding="utf-8", errors="replace"))
    return out


# What a search engine indexes is the text, the links and the JSON-LD — not the inline CSS,
# the script bundles or the content-hashed asset names. A shared CSS edit rewrites every
# page's <style> and /_astro/ links; hashing raw bytes would report all 51 pages "changed"
# and send the whole site to IndexNow. JSON-LD scripts are kept: a schema change is indexed.
_STYLE = re.compile(r"<style\b[^>]*>.*?</style>", re.S | re.I)
_SCRIPT = re.compile(r"<script\b(?![^>]*application/ld\+json)[^>]*>.*?</script>", re.S | re.I)
_ASSET_LINK = re.compile(r"<link\b[^>]*\bhref=\"/_astro/[^\"]*\"[^>]*>", re.I)


def content_hash(html):
    """sha256 of the page with inline styles, non-JSON-LD scripts and /_astro/ asset links removed."""
    for rx in (_STYLE, _SCRIPT, _ASSET_LINK):
        html = rx.sub("", html)
    return hashlib.sha256(html.encode("utf-8")).hexdigest()


def diff(base, head):
    """{'changed': modified or added slugs, 'removed': slugs the head no longer builds}."""
    return {"changed": sorted(s for s, h in head.items() if base.get(s) != h),
            "removed": sorted(s for s in base if s not in head)}


def base_hashes(base):
    """The earlier build's hashes: a directory is hashed; anything else is a git ref."""
    path = pathlib.Path(base)
    if not path.is_absolute():
        path = ROOT / path
    if path.is_dir():
        return page_hashes(path)
    r = subprocess.run(["git", "show", f"{base}:{MANIFEST.as_posix()}"], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise BaseError(f"no {MANIFEST.as_posix()} at {base!r} — pass a directory holding the "
                        "earlier build, or a ref whose close committed the manifest")
    return json.loads(r.stdout)["pages"]


def head_sha():
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "unknown"


def main(argv=None):
    ap = argparse.ArgumentParser(description="slugs whose rendered dist/ output changed")
    ap.add_argument("--base", required=True, help="a directory holding the earlier build, or a git ref")
    ap.add_argument("--json", action="store_true",
                    help=f"write {REPORT.as_posix()} and refresh {MANIFEST.as_posix()}")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)
    dist = ROOT / "dist"
    if not dist.is_dir():
        print("rendered-changes ERROR dist/ does not exist — run npm run build first")
        return 2
    try:
        base = base_hashes(a.base)
    except (BaseError, OSError, ValueError, KeyError) as e:
        print(f"rendered-changes ERROR {e}")
        return 2
    head = page_hashes(dist)
    d = diff(base, head)
    sha = head_sha()
    print(f"rendered-changes: base {a.base}, head {sha[:12]} — {len(d['changed'])} changed, "
          f"{len(d['removed'])} removed, of {len(head)} built pages ({len(base)} in the base)")
    for s in d["changed"]:
        print(f"  changed {s}")
    for s in d["removed"]:
        print(f"  removed {s}")
    if a.json:
        rep, man = ROOT / REPORT, ROOT / MANIFEST
        rep.parent.mkdir(parents=True, exist_ok=True)
        man.parent.mkdir(parents=True, exist_ok=True)
        rep.write_text(json.dumps({"base": a.base, "head": sha, "changed": d["changed"]}, indent=2) + "\n",
                       encoding="utf-8")
        man.write_text(json.dumps({"head": sha, "pages": head}, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8")
        print(f"wrote {REPORT.as_posix()} and {MANIFEST.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Point IndexNow's --changed at it**

In `scripts/indexnow_submit.py` replace the whole `changed_slugs` function:

```python
def changed_slugs(ref="origin/main"):
    """Page slugs whose source changed vs a git ref, plus anything uncommitted."""
    cmds = [
        ["git", "diff", "--name-only", f"{ref}...HEAD"],
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]
    files = set()
    for c in cmds:
        r = subprocess.run(c, capture_output=True, text=True)
        if r.returncode == 0:
            files.update(x for x in r.stdout.split("\n") if x.strip())
    slugs = set()
    for f in files:
        m = re.match(r"src/pages/(.+)/index\.(astro|html)$", f)
        if m:
            slugs.add(m.group(1))
        elif f == "src/pages/index.astro":
            slugs.add("")
    return sorted(slugs)
```
with:
```python
RENDERED_CHANGES = pathlib.Path("docs") / "reports" / "rendered-changes.json"


def changed_slugs():
    """Page slugs whose RENDERED output changed: docs/reports/rendered-changes.json, written by
    `python3 scripts/rendered_changes.py --base <dir-or-ref> --json` from a dist-hash diff.

    The source diff this replaced matched `src/pages/<x>/index.astro` only, so it never named a
    city page (`uk-locations/[slug].astro`), a puppy, a blog post or a page changed through a
    shared component (audit D6). `index` is the root and maps to ""."""
    if not RENDERED_CHANGES.is_file():
        die(f"{RENDERED_CHANGES} not found — run `python3 scripts/rendered_changes.py --base "
            "<dir-or-ref> --json` after the build, then --changed submits what it lists")
    try:
        rows = json.loads(RENDERED_CHANGES.read_text(encoding="utf-8"))["changed"]
    except (OSError, ValueError, KeyError) as e:
        die(f"cannot read {RENDERED_CHANGES}: {e}")
    return sorted("" if s == "index" else s for s in rows)
```
Replace `    ap.add_argument("--changed", action="store_true", help="derive slugs from git changes vs origin/main")` with:
```python
    ap.add_argument("--changed", action="store_true",
                    help="the slugs docs/reports/rendered-changes.json lists (scripts/rendered_changes.py)")
```
Replace `            print("no changed page sources vs origin/main — nothing to submit")` with `            print(f"{RENDERED_CHANGES} lists no changed page — nothing to submit")`; in the docstring replace `  python3 scripts/indexnow_submit.py --changed              # pages changed vs origin/main` with `  python3 scripts/indexnow_submit.py --changed              # pages rendered_changes.py listed`; delete the line `import subprocess` (nothing else uses it).
In `.claude/skills/bsuk-indexing/SKILL.md` (STEP 4) replace:
````
```bash
python3 scripts/indexnow_submit.py --changed   # refuses (exit 2) without BSUK_RELEASE=1
```
````
with:
````
```bash
python3 scripts/rendered_changes.py --base <dir-or-ref> --json   # the dist-hash diff: which built pages changed
```

```bash
python3 scripts/indexnow_submit.py --changed   # submits what rendered_changes.py listed; refuses (exit 2) without BSUK_RELEASE=1
```

`--changed` reads the rendered-changes report that `python3 scripts/rendered_changes.py --json` writes (git-ignored, under docs/reports/), never a source diff: a city page renders
from `src/pages/uk-locations/[slug].astro` and a data row, so only the built output says which
pages moved. Every close runs `rendered_changes.py --json` and commits
`data/quality/dist-hashes.json`, so the next close can pass its commit as `--base`.
````

Regenerate the registry: `python3 scripts/build_system_registry.py`.

- [ ] **Step 5: Run to verify it passes**

Run: `python3 -m pytest tests/py/test_rendered_changes.py tests/py/test_indexnow_submit.py tests/py/test_agent_facts.py tests/py/test_system_registry.py -q -p no:cacheprovider`
Expected: all pass (`6 passed` + `13 passed` for the two target files).

- [ ] **Step 6: Record the baseline manifest project 5 diffs against**

Run: `npm run -s build && python3 scripts/rendered_changes.py --base HEAD; echo "exit=$?"`
Expected: `rendered-changes ERROR no data/quality/dist-hashes.json at 'HEAD' — pass a directory holding the earlier build, or a ref whose close committed the manifest`, `exit=2`.

Run: `python3 scripts/rendered_changes.py --base dist --json`
Expected: `rendered-changes: base dist, head <sha> — 0 changed, 0 removed, of 51 built pages (51 in the base)` and `wrote docs/reports/rendered-changes.json and data/quality/dist-hashes.json`. From the commit below on, `--base <this commit>` works.

- [ ] **Step 7: check:all**

Run: `npm run -s check:all; echo "exit=$?"`
Expected: `exit=0`.

- [ ] **Step 8: Commit**

```bash
git add scripts/rendered_changes.py tests/py/test_rendered_changes.py data/quality/dist-hashes.json scripts/indexnow_submit.py tests/py/test_indexnow_submit.py .claude/skills/bsuk-indexing/SKILL.md docs/reference/system-registry.md
git commit -m "$(cat <<'EOF'
close: rendered-changes dist-hash diff; IndexNow --changed reads it

scripts/rendered_changes.py hashes every built page and diffs against an earlier build
(a directory, or the manifest a ref committed). --json writes
docs/reports/rendered-changes.json {base, head, changed} and refreshes
data/quality/dist-hashes.json. indexnow_submit.py --changed submits that list, so city,
puppy and blog pages are no longer invisible to it.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```

---

## Wave 3 — Research and keyword numbers (Tasks 17–22)

### Task 17: query_augment.py --extract-h2 keeps competitor page metrics in raw/<slug>/competitors.json

Audit rows 6.7, 6.15, 6.17, 9.3 (Wave 3 #15). `--extract-h2` already parses each saved pool page; this task measures the same saved HTML once more (no second fetch, no paid call) and keeps title, meta description, word count, words and H3s per content H2, image/video/table counts and JSON-LD `@type`s. A new `--competitor-metrics SLUG` mode backfills every page of `competitors.json` from the gitignored cache `data/queries/cache/<slug>/<n>.html` (`n` = the page's 1-based place in `pages`), refusing a cache file whose H2s do not match the record. The question file gains an optional `word_target` (Rule 27's median) and each competitor row an optional `words`; both are optional in `schemas/queries.schema.json`, so the Manchester and Leeds question files stay valid.

**Files:**
- Create: `tests/py/fixtures/competitor-pages/breeder-sections.html`
- Create: `tests/py/test_competitor_metrics.py`
- Modify: `scripts/query_augment.py` — docstring `:30-35`; `_H2s.content_h2s` `:604-627`; new block between `extract_h2s` (`:649-663`) and `META_CHARSET` (`:666`); `load_competitors` `:1153-1178` and new functions after it; `build` `:1273-1292`; `main` `:1320`, `:1328-1332`, `:1360-1377`
- Modify: `schemas/queries.schema.json` `:18-32` (competitor row) and before `:45` (`word_target`)
- Modify: `tests/py/test_query_augment.py` `:953-961`, `:1080-1088`
- Modify: `.claude/skills/bsuk-query-augmentation/SKILL.md` `:57`, `:129-142`
- Modify: `docs/reference/seo-rules.md` `:188-191`
- Modify (data, written by the script): `data/queries/raw/blue-staffy-puppies-manchester-uk/competitors.json`

- [ ] **Step 1: Save the fixture page**

Create `tests/py/fixtures/competitor-pages/breeder-sections.html` (a synthetic saved page: a nav H2, three content H2s, a two-card grid, a footer H2, a phone number in an H3, JSON-LD with a `@graph`, one broken JSON-LD block):

```html
<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<title>Blue Staffy Puppies Manchester | Example Kennels</title>
<meta name="description" content="Blue staffy puppies in Manchester,   raised at home.">
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Organization","name":"Example Kennels"},{"@type":["WebPage","ItemPage"]},{"@type":"FAQPage","mainEntity":[{"@type":"Question"}]}]}</script>
<script type="application/ld+json">{ not json</script>
<style>h2{color:red}</style>
</head>
<body>
<header><nav><a href="/">Home</a> <a href="/puppies">Puppies</a><h2>Menu</h2></nav></header>
<main>
<h1>Blue Staffy Puppies in Manchester</h1>
<p>We raise a few litters a year.</p>
<section>
<h2>Our Puppies</h2>
<p>Every puppy is raised in the house with the family.</p>
<img src="/a.jpg" alt="Blue staffy puppy">
<h3>Current Litter</h3>
<p>Four pups are ready in spring.</p>
<h3>Call 07700 900123 today</h3>
</section>
<section>
<h2>Health <a href="/health">Testing</a></h2>
<p>Both parents are tested.</p>
<table><tr><td>Test</td><td>Result</td></tr></table>
<iframe src="https://www.youtube.com/embed/abc"></iframe>
<video src="/v.mp4"></video>
<h3>Hips</h3>
<script>var h3 = "not text";</script>
</section>
<div class="grid">
<article><h2><a href="/p/1">Pup One</a></h2><p>Blue boy.</p></article>
<article><h2><a href="/p/2">Pup Two</a></h2><p>Blue girl.</p></article>
</div>
<section>
<h2>Delivery</h2>
<p>We deliver across the UK.</p>
<img src="/b.jpg" alt="">
</section>
</main>
<footer><h2>Contact</h2><p>Footer words here that never count.</p><form><button>Send</button></form></footer>
</body>
</html>
```

- [ ] **Step 2: Write the failing test**

Create `tests/py/test_competitor_metrics.py`:

```python
# tests/py/test_competitor_metrics.py — query_augment.py keeps competitor page metrics
# (parity build Task 17; audit rows 6.7, 6.15, 6.17, 9.3). Every page is a saved fixture under
# tests/py/fixtures/competitor-pages/; nothing here fetches.
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import query_augment as Q  # noqa: E402

SCRIPT = ROOT / "scripts" / "query_augment.py"
FIX = ROOT / "tests" / "py" / "fixtures" / "competitor-pages"
PAGE = (FIX / "breeder-sections.html").read_text(encoding="utf-8")
SLUG = "blue-staffy-puppies-testcity"

EXPECTED = {
    "title": "Blue Staffy Puppies Manchester | Example Kennels",
    "meta_description": "Blue staffy puppies in Manchester, raised at home.",
    "word_count": 59,
    "intro_words": 7,
    "sections": [
        {"h2": "Our Puppies", "words": 16, "h3": ["Current Litter"]},
        {"h2": "Health Testing", "words": 6, "h3": ["Hips"]},
        {"h2": "Delivery", "words": 5, "h3": []},
    ],
    "h3_count": 3,
    "images": 2,
    "videos": 2,
    "tables": 1,
    "schema_types": ["FAQPage", "ItemPage", "Organization", "Question", "WebPage"],
    "scrubbed": 1,
}


def test_page_metrics_reads_the_saved_page():
    assert Q.page_metrics(PAGE) == EXPECTED


def test_metrics_sections_are_exactly_the_content_h2s_in_order():
    m = Q.page_metrics(PAGE)
    assert [s["h2"] for s in m["sections"]] == Q.extract_h2s(PAGE)


def test_a_contact_detail_never_reaches_the_metrics():
    text = json.dumps(Q.page_metrics(PAGE))
    assert "07700" not in text and "900123" not in text


def test_a_page_with_no_head_and_no_h2_measures_zero_sections():
    m = Q.page_metrics("<main><p>Just five words of prose.</p><img src=x></main>")
    assert m["title"] is None and m["meta_description"] is None
    assert m["word_count"] == 5 and m["intro_words"] == 5 and m["sections"] == []
    assert m["images"] == 1 and m["schema_types"] == []


def test_cli_extract_h2_prints_the_metrics_beside_the_h2s(tmp_path):
    f = tmp_path / "1.html"
    f.write_text(PAGE, encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPT), "--extract-h2", str(f)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["h2"] == ["Our Puppies", "Health Testing", "Delivery"]
    assert out["h2_all"] == 7 and out["blocked"] is False
    assert out["metrics"] == EXPECTED


def _repo(tmp_path, pages, cached):
    """A repo root with raw/<slug>/competitors.json and cache/<slug>/<n>.html files."""
    raw = tmp_path / "data/queries/raw" / SLUG
    raw.mkdir(parents=True)
    (raw / "competitors.json").write_text(json.dumps(
        {"status": "ok", "fetched": "2026-09-26", "pages": pages}), encoding="utf-8")
    cache = tmp_path / "data/queries/cache" / SLUG
    cache.mkdir(parents=True)
    for n, html in cached.items():
        (cache / f"{n}.html").write_text(html, encoding="utf-8")
    return tmp_path


def _record(url, html, g):
    rep = Q.page_report(html)
    return {"url": url, "google_pos": g, "bing_pos": None, "h2": rep["h2"],
            "h2_all": rep["h2_all"], "blocked": rep["blocked"]}


def _metrics_cli(root):
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root),
                           "--competitor-metrics", SLUG], capture_output=True, text=True)


def test_competitor_metrics_backfills_every_cached_page(tmp_path):
    other = "<main><h2>Only</h2><p>three words here</p></main>"
    root = _repo(tmp_path, [_record("https://a.example/", PAGE, 1),
                            _record("https://b.example/", other, 2)], {1: PAGE, 2: other})
    r = _metrics_cli(root)
    assert r.returncode == 0, r.stderr
    d = json.loads((root / f"data/queries/raw/{SLUG}/competitors.json").read_text())
    assert d["pages"][0]["metrics"] == EXPECTED
    assert d["pages"][1]["metrics"]["sections"] == [{"h2": "Only", "words": 3, "h3": []}]
    assert "2 of 2 pages" in r.stdout


def test_competitor_metrics_skips_a_page_whose_cache_file_is_missing(tmp_path):
    root = _repo(tmp_path, [_record("https://a.example/", PAGE, 1),
                            _record("https://b.example/", PAGE, 2)], {1: PAGE})
    r = _metrics_cli(root)
    assert r.returncode == 0, r.stderr
    d = json.loads((root / f"data/queries/raw/{SLUG}/competitors.json").read_text())
    assert "metrics" in d["pages"][0] and "metrics" not in d["pages"][1]
    assert "1 of 2 pages" in r.stdout and "https://b.example/" in r.stdout


def test_competitor_metrics_refuses_a_cache_file_that_is_not_the_recorded_page(tmp_path):
    other = "<main><h2>Something Else</h2></main>"
    root = _repo(tmp_path, [_record("https://a.example/", PAGE, 1)], {1: other})
    before = (root / f"data/queries/raw/{SLUG}/competitors.json").read_text()
    r = _metrics_cli(root)
    assert r.returncode == Q.EXIT_BAD_INPUT
    assert "1.html" in r.stderr and "does not match" in r.stderr
    assert (root / f"data/queries/raw/{SLUG}/competitors.json").read_text() == before


def test_competitor_metrics_without_a_competitors_file_is_bad_input(tmp_path):
    r = _metrics_cli(tmp_path)
    assert r.returncode == Q.EXIT_BAD_INPUT
    assert "competitors.json" in r.stderr


@pytest.mark.parametrize("bad", [
    "not an object",
    {"word_count": -1},
    {"word_count": 5, "sections": [{"h2": "x", "words": "many", "h3": []}]},
])
def test_load_competitors_refuses_malformed_metrics(tmp_path, bad):
    page = _record("https://a.example/", PAGE, 1)
    page["metrics"] = bad
    root = _repo(tmp_path, [page], {})
    with pytest.raises(Q.BadInput, match="metrics"):
        Q.load_competitors(SLUG, root)


def test_load_competitors_accepts_a_file_with_no_metrics(tmp_path):
    root = _repo(tmp_path, [_record("https://a.example/", PAGE, 1)], {})
    assert Q.load_competitors(SLUG, root)["pages"][0]["url"] == "https://a.example/"


def test_word_target_is_the_median_of_the_measured_pages():
    pages = [dict(_record(f"https://{i}.example/", PAGE, i + 1),
                  metrics=dict(EXPECTED, word_count=n)) for i, n in enumerate((100, 300, 900))]
    pages.append(dict(_record("https://blocked.example/", PAGE, 9), blocked=True,
                      metrics=dict(EXPECTED, word_count=5000)))
    assert Q.word_target(pages) == {"median": 300, "from": 3, "of": 4}


def test_word_target_without_metrics_names_its_barrier():
    wt = Q.word_target([_record("https://a.example/", PAGE, 1)])
    assert wt["median"] is None and wt["from"] == 0 and wt["of"] == 1
    assert wt["status"].startswith("NOT FETCHED — ")


def test_the_real_competitor_files_still_load():
    for f in sorted((ROOT / "data/queries/raw").glob("*/competitors.json")):
        Q.load_competitors(f.parent.name, ROOT)


def test_build_writes_the_word_target_and_each_rows_words(tmp_path):
    import jsonschema
    from test_query_augment import make_root, seed, write_raw
    root = make_root(tmp_path)
    seed(root)
    measured = dict(_record("https://a.example", PAGE, 1), metrics=EXPECTED)
    write_raw(root, "m", "competitors", {"status": "ok", "pages": [
        measured, _record("https://b.example", PAGE, 2)]})
    data, _ = Q.build("m", "location", "blue staffy puppies manchester",
                      "/uk-locations/m/", root, "2026-09-26")
    jsonschema.validate(data, json.loads((ROOT / "schemas/queries.schema.json").read_text()))
    assert data["word_target"] == {"median": 59, "from": 1, "of": 2}
    assert [r.get("words") for r in data["competitors"]] == [59, None]
```

- [ ] **Step 3: Run it and watch it fail**

Run: `python3 -m pytest tests/py/test_competitor_metrics.py -q`
Expected: `15 failed, 2 passed` — `AttributeError: module 'query_augment' has no attribute 'page_metrics'` (and `word_target`, `competitor_metrics`), `KeyError: 'metrics'` from the CLI test, and the malformed-metrics cases pass through `load_competitors` without raising.

- [ ] **Step 4: Expose the content-H2 indices in `_H2s`**

In `scripts/query_augment.py`, replace

```python
    def content_h2s(self):
        seen = {id(e): e for anc, _, _ in self.found for e in anc}.values()
```

with

```python
    def content_h2s(self):
        return [self.found[i][1] for i in self.content_indices()]

    def content_indices(self):
        """Indices into self.found (= the n-th <h2> tag, from 0) of the content H2s."""
        seen = {id(e): e for anc, _, _ in self.found for e in anc}.values()
```

then in the same method replace `for ancestors, text, bare in self.found:` with `for i, (ancestors, text, bare) in enumerate(self.found):`, and replace

```python
            if any(t == "header" and not HEADER_HOSTS & set(tags[:i])
                   for i, t in enumerate(tags)):
                continue
            out.append(text)
        return out
```

with

```python
            if any(t == "header" and not HEADER_HOSTS & set(tags[:j])
                   for j, t in enumerate(tags)):
                continue
            out.append(i)
        return out
```

(`extract_h2s` and `page_report` are unchanged: `content_h2s` still returns the texts.)

- [ ] **Step 5: Add `page_metrics` and `word_target`**

Insert this block immediately before `META_CHARSET = re.compile(` (after `extract_h2s`):

```python
# ── competitor page metrics (parity build Task 17) ────────────────────────────────────────────
# The same saved page --extract-h2 reads, measured once more: no second fetch. Text inside
# these elements is never page prose (navigation, furniture, forms and the <head>).
# A <button> is not skipped: accordion FAQs put their question H3s inside one.
METRIC_SKIP = RAW_TAGS | {"head", "title", "noscript", "svg", "nav", "footer", "aside", "form",
                          "select"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
WORD = re.compile(r"[^\W_]+(?:['’-][^\W_]+)*")
VIDEO_SRC = re.compile(r"youtube\.com|youtube-nocookie\.com|youtu\.be|vimeo\.com|wistia|dailymotion",
                       re.I)
# A string that carries a phone number, an email or a WhatsApp link is never kept: committed
# raw files hold no third-party contact details (tests/py/test_no_third_party_contacts.py).
CONTACTISH = re.compile(r"@|wa\.me|whatsapp|(?:\d[\s()+-]{0,2}){9,}", re.I)


class _Metrics(HTMLParser):
    """Word, heading, media and schema counts for one saved page. `ordinal` counts every <h2>
    start tag exactly as _H2s does, so words and H3s land under the n-th <h2>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.ordinal = 0
        self.words = Counter()          # ordinal -> prose words (headings excluded)
        self.h3 = {}                    # ordinal -> [H3 text]
        self.total = 0
        self.h3_count = self.images = self.videos = self.tables = 0
        self.title = self.meta_description = None
        self._title = None
        self._h3 = None
        self._ld = None
        self.ld_blocks = []

    def _hidden(self):
        return any(t in METRIC_SKIP for t in self.stack)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "h2":
            self.ordinal += 1
        if tag == "title" and self.title is None and "svg" not in self.stack:
            self._title = []
        if tag == "meta" and (a.get("name") or "").lower() == "description" \
                and self.meta_description is None:
            self.meta_description = " ".join((a.get("content") or "").split()) or None
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._ld = []
        if not self._hidden():
            if tag == "img":
                self.images += 1
            elif tag == "video" or (tag == "iframe" and VIDEO_SRC.search(a.get("src") or "")):
                self.videos += 1
            elif tag == "table":
                self.tables += 1
            elif tag == "h3":
                self.h3_count += 1
                self._h3 = []
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "title" and self._title is not None:
            self.title = " ".join("".join(self._title).split()) or None
            self._title = None
        if tag == "script" and self._ld is not None:
            self.ld_blocks.append("".join(self._ld))
            self._ld = None
        if tag == "h3" and self._h3 is not None:
            text = " ".join("".join(self._h3).split())
            if text:
                self.h3.setdefault(self.ordinal, []).append(text)
            self._h3 = None
        if tag in self.stack:
            del self.stack[len(self.stack) - 1 - self.stack[::-1].index(tag):]

    def handle_data(self, data):
        if self._title is not None:
            self._title.append(data)
        if self._ld is not None:
            self._ld.append(data)
        if self._hidden():
            return
        if self._h3 is not None:
            self._h3.append(data)
        n = len(WORD.findall(data))
        self.total += n
        if not HEADING_TAGS & set(self.stack):
            self.words[self.ordinal] += n


def _schema_types(blocks):
    found = set()

    def walk(o):
        if isinstance(o, dict):
            t = o.get("@type")
            for x in (t if isinstance(t, list) else [t]):
                if isinstance(x, str) and x:
                    found.add(x)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for b in blocks:
        try:
            walk(json.loads(b))
        except ValueError:
            continue   # a broken JSON-LD block names no type
    return sorted(found)


def page_metrics(html):
    """What a competitor page carries, measured from the saved HTML --extract-h2 reads:

    title, meta_description, word_count (visible words outside the <head>, nav, footer,
    aside, form, select, noscript, svg, script, style and template), intro_words
    (prose before the first content H2), sections (one per content H2 from extract_h2s, in order:
    its prose words up to the next <h2> of any kind, headings excluded, and its H3 texts),
    h3_count, images, videos (<video> or a YouTube/Vimeo/Wistia/Dailymotion iframe), tables,
    schema_types (every JSON-LD @type, sorted) and scrubbed (how many title, description or
    H3 strings were dropped because they carried a phone number, an email or a WhatsApp link).
    """
    h = _H2s()
    h.feed(html)
    h.close()
    m = _Metrics()
    m.feed(html)
    m.close()
    scrubbed = 0

    def keep(text):
        nonlocal scrubbed
        if text is not None and CONTACTISH.search(text):
            scrubbed += 1
            return None
        return text
    sections, content = [], h.content_indices()
    first = content[0] + 1 if content else m.ordinal + 1
    for i in content:
        h3s = [keep(t) for t in m.h3.get(i + 1, [])]
        sections.append({"h2": h.found[i][1], "words": m.words[i + 1],
                         "h3": [t for t in h3s if t is not None]})
    return {"title": keep(m.title), "meta_description": keep(m.meta_description),
            "word_count": m.total, "intro_words": sum(m.words[k] for k in range(first)), "sections": sections,
            "h3_count": m.h3_count, "images": m.images, "videos": m.videos,
            "tables": m.tables, "schema_types": _schema_types(m.ld_blocks),
            "scrubbed": scrubbed}


def word_target(pages):
    """Rule 27's number: the median word_count of the pages that are measured and not
    blocked. {"median", "from", "of"}; with nothing measured, median is None and "status"
    names the barrier."""
    counts = sorted(p["metrics"]["word_count"] for p in pages
                    if isinstance(p.get("metrics"), dict) and not p.get("blocked", False))
    out = {"median": None, "from": len(counts), "of": len(pages)}
    if not counts:
        out["status"] = ("NOT FETCHED — no competitor page carries metrics; run "
                         "query_augment.py --competitor-metrics <slug> over the cached HTML")
        return out
    mid = len(counts) // 2
    out["median"] = counts[mid] if len(counts) % 2 else round((counts[mid - 1] + counts[mid]) / 2)
    return out
```

- [ ] **Step 6: Validate saved metrics and add the backfill**

In `load_competitors`, replace

```python
        if not isinstance(p.get("blocked", False), bool):
            raise BadInput(path, f"pages[{i}].blocked must be true or false")
    return d
```

with

```python
        if not isinstance(p.get("blocked", False), bool):
            raise BadInput(path, f"pages[{i}].blocked must be true or false")
        if "metrics" in p:
            problem = _metrics_problem(p["metrics"])
            if problem:
                raise BadInput(path, f"pages[{i}].metrics {problem}")
    return d


METRIC_COUNTS = ("word_count", "intro_words", "h3_count", "images", "videos", "tables",
                 "scrubbed")


def _count(x):
    return isinstance(x, int) and not isinstance(x, bool) and x >= 0


def _metrics_problem(m):
    """None when `m` has page_metrics' shape (word_count required, the rest optional), else
    what is wrong with it. Metrics are copied from the script's output, never typed."""
    if not isinstance(m, dict):
        return "must be an object"
    if "word_count" not in m:
        return "must carry word_count"
    for k in METRIC_COUNTS:
        if k in m and not _count(m[k]):
            return f"{k} must be a non-negative integer"
    for k in ("title", "meta_description"):
        if not _opt_str(m.get(k)):
            return f"{k} must be a string or null"
    types = m.get("schema_types", [])
    if not (isinstance(types, list) and all(isinstance(t, str) for t in types)):
        return "schema_types must be a list of strings"
    secs = m.get("sections", [])
    if not isinstance(secs, list):
        return "sections must be a list"
    for j, sec in enumerate(secs):
        if not (isinstance(sec, dict) and isinstance(sec.get("h2"), str)
                and _count(sec.get("words"))
                and isinstance(sec.get("h3", []), list)
                and all(isinstance(t, str) for t in sec.get("h3", []))):
            return f"sections[{j}] must be {{h2: string, words: count, h3: [strings]}}"
    return None


def competitor_metrics(slug, root=ROOT):
    """Fill each competitors.json page's `metrics` from data/queries/cache/<slug>/<n>.html,
    n being the page's 1-based place in `pages` — the file --extract-h2 already read. No fetch.

    Returns (measured, missing urls). A cache file whose h2 / h2_all / blocked differ from the
    page's record is not that page: BadInput, and nothing is written."""
    path = Path(root) / "data/queries/raw" / slug / "competitors.json"
    d = load_competitors(slug, root)
    if not path.exists():
        raise BadInput(path, "missing — write competitors.json (bsuk-query-augmentation Step 3) first")
    cache = Path(root) / "data/queries/cache" / slug
    measured, missing = 0, []
    for n, p in enumerate(d["pages"], 1):
        f = cache / f"{n}.html"
        if not f.exists():
            missing.append(p["url"])
            continue
        html = decode_html(f.read_bytes())
        rep = page_report(html)
        want = {"h2": p.get("h2", []), "h2_all": p.get("h2_all", 0),
                "blocked": p.get("blocked", False)}
        if rep != want:
            raise BadInput(f, f"does not match pages[{n - 1}] ({p['url']}): the file gives "
                              f"{json.dumps(rep)}, the record {json.dumps(want)}")
        p["metrics"] = page_metrics(html)
        measured += 1
    _write_json(path, d)
    return measured, missing
```

- [ ] **Step 7: Write `words` and `word_target` into the question file**

In `build`, replace `    target, rows = section_target(comp["pages"])` with

```python
    target, rows = section_target(comp["pages"])
    for row, p in zip(rows, comp["pages"]):
        if isinstance(p.get("metrics"), dict):
            row["words"] = p["metrics"]["word_count"]
```

and replace

```python
            "competitors": rows, "section_target": target, "extra_sections": extras,
            "questions": questions}
```

with

```python
            "competitors": rows, "section_target": target,
            "word_target": word_target(comp["pages"]), "extra_sections": extras,
            "questions": questions}
```

- [ ] **Step 8: The CLI — metrics on `--extract-h2`, the new mode, the docstring**

In `main`: after `ap.add_argument("--extract-h2", metavar="FILE")` add `ap.add_argument("--competitor-metrics", metavar="SLUG")`. Replace

```python
    modes = [m for m in (a.preflight, a.record, a.slug, a.extract_h2,
                         a.reconcile or None, a.budget) if m is not None]
    if len(modes) != 1:
        ap.error("give exactly one of --preflight SLUG, --record SLUG, --reconcile, "
                 "--budget SOURCE, --extract-h2 FILE or a build SLUG")
```

with

```python
    modes = [m for m in (a.preflight, a.record, a.slug, a.extract_h2, a.competitor_metrics,
                         a.reconcile or None, a.budget) if m is not None]
    if len(modes) != 1:
        ap.error("give exactly one of --preflight SLUG, --record SLUG, --reconcile, "
                 "--budget SOURCE, --extract-h2 FILE, --competitor-metrics SLUG or a build SLUG")
```

Replace

```python
        print(json.dumps(rep))   # ASCII-escaped: safe on any stdout
        return EXIT_OK
    slug = modes[0]
    if not SLUG_RE.fullmatch(slug):
        ap.error(f"slug must match ^[a-z0-9-]+$, got {slug!r}")
```

with

```python
        rep["metrics"] = page_metrics(html)
        print(json.dumps(rep))   # ASCII-escaped: safe on any stdout
        return EXIT_OK
    slug = modes[0]
    if not SLUG_RE.fullmatch(slug):
        ap.error(f"slug must match ^[a-z0-9-]+$, got {slug!r}")
    if a.competitor_metrics:
        try:
            measured, missing = competitor_metrics(slug, root)
        except BadInput as e:
            print(f"query_augment.py: bad input: {e}", file=sys.stderr)
            return EXIT_BAD_INPUT
        total = measured + len(missing)
        print(f"measured {measured} of {total} pages in data/queries/raw/{slug}/competitors.json"
              + "".join(f"\n  no cache file (NOT FETCHED — data/queries/cache/{slug}/ holds no "
                        f"saved page): {u}" for u in missing))
        return EXIT_OK
```

In the module docstring, after the line `      exit 0 printed (a blocked page also warns on stderr) · 6 the file is missing or unreadable` add:

```text
      The same JSON also carries "metrics" (page_metrics: title, meta description, word
      counts per content H2, H3s, image/video/table counts, JSON-LD @types).
  query_augment.py --competitor-metrics SLUG
      fills each data/queries/raw/SLUG/competitors.json page's "metrics" from
      data/queries/cache/SLUG/<n>.html (n = the page's 1-based place in "pages"); no fetch.
      exit 0 written (pages with no cache file are listed) · 6 competitors.json missing or
      malformed, or a cache file that is not its page (nothing written)
```

- [ ] **Step 9: Make the two new fields optional in the schema**

In `schemas/queries.schema.json`, in the `competitors` item replace

```json
          "outlier": {"type": "boolean"},
          "blocked": {"type": "boolean"}
        }
```

with

```json
          "outlier": {"type": "boolean"},
          "blocked": {"type": "boolean"},
          "words": {"type": "integer", "minimum": 0}
        }
```

and insert immediately before `    "extra_sections": {`:

```json
    "word_target": {
      "description": "Rule 27: the median word_count of the measured, unblocked competitor pages (query_augment.py word_target). Optional so question files written before parity build Task 17 stay valid.",
      "type": "object", "additionalProperties": false,
      "required": ["median", "from", "of"],
      "properties": {
        "median": {"type": ["integer", "null"], "minimum": 0},
        "from": {"type": "integer", "minimum": 0},
        "of": {"type": "integer", "minimum": 0},
        "status": {"type": "string", "pattern": "^NOT FETCHED — \\S"}
      }
    },
```

- [ ] **Step 10: The two existing CLI tests read the new key**

In `tests/py/test_query_augment.py`, `test_cli_extract_h2_prints_the_json_list`: replace

```python
    assert json.loads(r.stdout) == {"h2": ["21 Staffie Puppies For Sale In Manchester",
                                           "Buyer's Advice"], "h2_all": 4, "blocked": False}
```

with

```python
    out = json.loads(r.stdout)
    assert out.pop("metrics")["sections"][0]["h2"] == "21 Staffie Puppies For Sale In Manchester"
    assert out == {"h2": ["21 Staffie Puppies For Sale In Manchester",
                          "Buyer's Advice"], "h2_all": 4, "blocked": False}
```

and in `test_cli_extract_h2_warns_on_a_blocked_page_and_exits_0` replace `    assert json.loads(r.stdout) == {"h2": [], "h2_all": 0, "blocked": True}` with

```python
    out = json.loads(r.stdout)
    assert out.pop("metrics")["sections"] == []
    assert out == {"h2": [], "h2_all": 0, "blocked": True}
```

- [ ] **Step 11: Run the tests and watch them pass**

Run: `python3 -m pytest tests/py/test_competitor_metrics.py tests/py/test_query_augment.py tests/py/test_no_third_party_contacts.py tests/py/test_query_coverage_check.py -q`
Expected: `432 passed` (17 new).

- [ ] **Step 12: The skill and Rule 27 say where the numbers come from**

In `.claude/skills/bsuk-query-augmentation/SKILL.md`, replace the exit-code row at `:57`

```text
| 6 | build, `--extract-h2` | bad input. Build: a raw input file is unparseable or the wrong shape → fix the named file from its source, never hand-edit around it. `--extract-h2`: the saved HTML is missing or unreadable → capture it again |
```

with

```text
| 6 | build, `--extract-h2`, `--competitor-metrics` | bad input. Build: a raw input file is unparseable or the wrong shape → fix the named file from its source, never hand-edit around it. `--extract-h2`: the saved HTML is missing or unreadable → capture it again. `--competitor-metrics`: the page's competitors file is missing or malformed, or a cache file is not the page its record names → re-save that page |
```

(no backticked `competitors.json` in that row: `test_rules_index.py` reads a backticked file name as a repo path). Then replace the Step 3 text from `For each pool page, save its HTML to the scratchpad.` up to (not including) `Never count, clean or judge competitor H2s yourself` with:

```markdown
For each pool page, save its HTML to `data/queries/cache/<slug>/<n>.html` (gitignored:
third-party pages carry advertisers' contact details), `n` being the page's 1-based place in
`pages`. Prefer the page's original HTML via `curl` (free, and cleanest). If curl fails or comes
back blocked (a challenge page), use a browser capture (free, but a rendered capture
can include consent dialogs; the extractor drops them). Firecrawl scrape raw HTML comes last
because it spends credits. Then run:

```bash
python3 scripts/query_augment.py --extract-h2 data/queries/cache/<slug>/<n>.html
```

Copy its `h2`, `h2_all` and `blocked` into
`data/queries/raw/<slug>/competitors.json` = `{"status", "fetched", "pages": [{"url",
"google_pos", "bing_pos", "h2": [...], "h2_all", "blocked"}]}` (a position is `null` when the
page is not in that engine's five). A challenge page stays in the pool as `"blocked": true`.
Then keep each page's metrics from the same saved files — no second fetch:

```bash
python3 scripts/query_augment.py --competitor-metrics <slug>
```

It writes `metrics` into every page whose cache file matches its record (title, meta
description, word count, words and H3s per content H2, image/video/table counts, JSON-LD
`@type`s) and lists the pages with no cache file. Exit 6 means a cache file is not the page its
record says — re-save that page, never edit the record to match. The question file's
`word_target` (Rule 27) is the median of these word counts.
```

In `docs/reference/seo-rules.md` replace the Rule 27 paragraph (`:188-191`) with:

```markdown
**Rule 27 — Word Count (Dynamic)**
The competitors' median word count, from the competitor scan: `word_target.median` in the
question file (`data/queries/<slug>.json`), measured by `query_augment.py --competitor-metrics`
from the saved competitor HTML; `NOT FETCHED — <barrier>` (its `status`) until that scan
exists. Never fix a word count before running competitor research, and never pick a number
first and write to fill it.
```

- [ ] **Step 13: Backfill Manchester from the HTML already cached (no fetch)**

The eight Manchester pool pages were saved on 2026-09-23 in the main checkout's gitignored cache. Copy them (read-only source) and backfill:

```bash
mkdir -p data/queries/cache
cp -R /Users/apple/Downloads/BSUK/data/queries/cache/blue-staffy-puppies-manchester-uk data/queries/cache/
python3 scripts/query_augment.py --competitor-metrics blue-staffy-puppies-manchester-uk
python3 -m pytest tests/py/test_no_third_party_contacts.py -q
```

Expected: `measured 8 of 8 pages in data/queries/raw/blue-staffy-puppies-manchester-uk/competitors.json`, then `59 passed`. `git status` shows only that `competitors.json` modified under `data/` (the cache is gitignored). If the source folder is absent, skip this step and say so in the commit message; Leeds has no cache and is not backfilled. Do NOT rebuild `data/queries/blue-staffy-puppies-manchester-uk.json` here — `word_target` arrives when its page builder next runs Step 5.

- [ ] **Step 14: Build and run every gate**

Run: `npm run -s build && npm run -s check:all && python3 -m pytest tests/py/test_competitor_metrics.py tests/py/test_query_augment.py tests/py/test_rules_index.py tests/py/test_builder_skills.py tests/py/test_agent_facts.py tests/py/test_marker_check.py -q`
Expected: build exit 0; `check:all` exit 0 (last lines `examined … files; 0 problems`, `examined 41 agents; 0 problems`); pytest all passed.

- [ ] **Step 15: Commit**

```bash
git add scripts/query_augment.py schemas/queries.schema.json tests/py/test_competitor_metrics.py \
  tests/py/fixtures/competitor-pages/breeder-sections.html tests/py/test_query_augment.py \
  .claude/skills/bsuk-query-augmentation/SKILL.md docs/reference/seo-rules.md \
  data/queries/raw/blue-staffy-puppies-manchester-uk/competitors.json
git commit -m "feat(queries): keep competitor page metrics from the saved HTML; Rule 27 word_target

--extract-h2 now also prints page_metrics (title, meta description, words and
H3s per content H2, image/video/table counts, JSON-LD types) from the same saved
page. --competitor-metrics SLUG backfills competitors.json from
data/queries/cache/<slug>/<n>.html with no fetch, refusing a cache file that is
not its page. The question file gains an optional word_target (Rule 27) and
per-row words. Manchester backfilled from the 2026-09-23 cache (8 of 8).

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 18: scripts/keyword_metrics.py — ours vs top-5 table on the board; FAIL first-100-words + title front-load on new pages

Audit rows 7a.1, 7a.2, 7a.5, 7a.7, 7d.6 (Wave 3 #16). One table: our page (the built page once `data/facts/rebuilt.json` lists it, else the board's picked tags) against the first five unblocked competitors, measured from the cache Task 17 reads (tag columns fall back to the saved `metrics`; body columns then say `NOT FETCHED — …`). Two checks register in `family_rules` (new location/comparison/blog pages only): `title-front-load` (FAIL from `boarded`, WARN on a draft) and `first-100-words` (FAIL on a rebuilt, built page). The board shows the table as block **4b** on new-family pages only, so the twelve approved boards render byte-for-byte as before. The table is written to `docs/reports/keyword-metrics/<key>.json` (gitignored).

**Files:**
- Create: `scripts/keyword_metrics.py`
- Create: `tests/py/test_keyword_metrics.py`
- Modify: `scripts/family_rules.py` (append after `:172`)
- Modify: `scripts/build_page_board.py` `:23` (import) and before `:926` (block 4b)
- Modify (generated): `docs/reference/system-registry.md` (`python3 scripts/build_system_registry.py`)

- [ ] **Step 1: Write the failing test**

Create `tests/py/test_keyword_metrics.py`:

```python
# tests/py/test_keyword_metrics.py — scripts/keyword_metrics.py, the ours-vs-top-5 keyword
# table (parity build Task 18; CAG §7a, audit rows 7a.1, 7a.2, 7a.5, 7a.7, 7d.6). Competitor
# pages are saved fixtures; nothing here fetches.
import copy
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import keyword_metrics as KM  # noqa: E402
import family_rules as FR     # noqa: E402

SCRIPT = ROOT / "scripts" / "keyword_metrics.py"
PAGE = (ROOT / "tests/py/fixtures/competitor-pages/breeder-sections.html").read_text(encoding="utf-8")
PRIMARY = "blue staffy puppies manchester"
TERMS = [PRIMARY, "raised in the house", "deliver across the uk", "health testing",
         "blue staffies manchester"]
SLUG = "blue-staffy-puppies-testcity"


def test_measure_html_counts_the_saved_competitor_page():
    m = KM.measure_html(PAGE, PRIMARY, TERMS, ["blue staffies manchester"])
    assert m == {"words": 59, "unique_terms": 4, "mentions": 4, "variations": 0,
                 "exact": {"title": 1, "h1": 1, "h2": 0, "alt": 0, "description": 1},
                 "first_100": True, "title_front": True}


def test_matching_ignores_small_words_and_case():
    assert KM.phrase_count("blue staffy puppies for sale", "Blue Staffy Puppies FOR Sale") == 1
    assert KM.phrase_count("blue staffy puppies for sale", "blue staffy puppies sale") == 1
    assert KM.phrase_count("puppies manchester", "Puppies in Manchester and puppies at Manchester") == 2
    assert KM.front_loaded("blue staffy puppies manchester", "Blue Staffy Puppies in Manchester | X")
    assert not KM.front_loaded("blue staffy puppies manchester", "Home-Raised Blue Staffy Puppies Manchester")


def test_first_100_words_is_measured_on_main_only():
    filler = " ".join(["word"] * 100)
    late = f"<nav>{PRIMARY}</nav><main><p>{filler}</p><p>{PRIMARY}</p></main>"
    early = f"<main><p>Our {PRIMARY} are home raised.</p><p>{filler}</p></main>"
    assert KM.measure_html(late, PRIMARY, [], [])["first_100"] is False
    assert KM.measure_html(early, PRIMARY, [], [])["first_100"] is True


def _board(status="boarded", title="Blue Staffy Puppies Manchester | BlueStaffyUK",
           slug="blue-staffy-first-week-at-home", page_type="blog"):
    b = copy.deepcopy(json.loads((ROOT / "data/boards/_demo.json").read_text()))
    b["meta"].update(slug=slug, page_type=page_type, status=status)
    b["brief"]["primary_keyword"] = PRIMARY
    b["meta_set"]["titles"][0] = title
    b["meta_set"]["pick"]["title"] = 0
    b["h1"]["variants"][0] = "Blue Staffy Puppies in Manchester"
    b["h1"]["pick"] = 0
    b["sections"][2]["heading"] = "How Our Blue Staffy Puppies in Manchester Are Raised"
    b["sections"][2]["keywords"]["variation"] = ["blue staffies manchester"]
    return b


def test_board_row_measures_the_planned_tags_before_the_page_is_built():
    row = KM.board_row(_board())
    assert row["who"] == "ours (board)" and row["title_front"] is True
    assert row["exact"] == {"title": 1, "h1": 1, "h2": 1, "alt": None, "description": 0}
    assert row["words"] is None and row["first_100"] is None
    assert row["note"].startswith("not built")


def test_title_not_front_loaded_fails_a_boarded_new_page_and_warns_a_draft():
    late = "Home-Raised Blue Staffy Puppies Manchester | BlueStaffyUK"
    assert [f[:2] for f in KM.findings(_board(title=late), rebuilt=set())] == [
        ("title-front-load", "FAIL")]
    assert [f[:2] for f in KM.findings(_board("draft", title=late), rebuilt=set())] == [
        ("title-front-load", "WARN")]
    assert KM.findings(_board(), rebuilt=set()) == []


def test_first_100_words_fails_a_rebuilt_new_page(tmp_path):
    slug = "blue-staffy-first-week-at-home"
    page = tmp_path / slug / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text("<main><p>" + " ".join(["word"] * 120) + f" {PRIMARY}</p></main>")
    got = KM.findings(_board(), dist=tmp_path, rebuilt={slug})
    assert [f[:2] for f in got] == [("first-100-words", "FAIL")]
    page.write_text(f"<main><p>{PRIMARY} " + " ".join(["word"] * 120) + "</p></main>")
    assert KM.findings(_board(), dist=tmp_path, rebuilt={slug}) == []
    # not in rebuilt.json: the built page is the migrated body, not this record's page
    page.write_text("<main><p>" + " ".join(["word"] * 120) + "</p></main>")
    assert KM.findings(_board(), dist=tmp_path, rebuilt=set()) == []


def test_family_rules_carries_the_placement_checks_on_new_pages_only():
    late = "Home-Raised Blue Staffy Puppies Manchester | BlueStaffyUK"
    ids = [c for c, _, _ in FR.findings(_board(title=late), ont={})]
    assert "title-front-load" in ids
    built = _board(title=late, slug="blue-staffy-uk-breeders", page_type="interior")
    assert "title-front-load" not in [c for c, _, _ in FR.findings(built, ont={})]


def _repo(tmp_path):
    raw = tmp_path / "data/queries/raw" / SLUG
    raw.mkdir(parents=True)
    pages = [
        {"url": "https://blocked.example/", "google_pos": 1, "bing_pos": None, "h2": [],
         "h2_all": 0, "blocked": True},
        {"url": "https://cached.example/", "google_pos": 2, "bing_pos": None, "h2": [],
         "h2_all": 0, "blocked": False},
        {"url": "https://metrics-only.example/", "google_pos": None, "bing_pos": 1, "h2": [],
         "h2_all": 0, "blocked": False,
         "metrics": {"title": "Blue Staffy Puppies Manchester", "meta_description": None,
                     "word_count": 900, "sections": [{"h2": "Blue Staffy Puppies in Manchester",
                                                      "words": 10, "h3": []}]}},
    ]
    (raw / "competitors.json").write_text(json.dumps({"status": "ok", "pages": pages}))
    cache = tmp_path / "data/queries/cache" / SLUG
    cache.mkdir(parents=True)
    (cache / "2.html").write_text(PAGE)
    return tmp_path


def test_competitor_rows_come_from_the_cache_then_the_saved_metrics(tmp_path):
    rows = KM.competitor_rows(SLUG, PRIMARY, TERMS, ["blue staffies manchester"], _repo(tmp_path))
    assert [r["who"] for r in rows] == ["https://cached.example/", "https://metrics-only.example/"]
    assert rows[0]["unique_terms"] == 4 and rows[0]["note"] == "measured from data/queries/cache"
    tag_only = rows[1]
    assert tag_only["exact"] == {"title": 1, "h1": None, "h2": 1, "alt": None, "description": 0}
    assert tag_only["title_front"] is True and tag_only["words"] == 900
    assert tag_only["unique_terms"] is None
    assert tag_only["note"].startswith("NOT FETCHED — ") and "3.html" in tag_only["note"]


def test_no_competitor_file_is_one_named_barrier(tmp_path):
    rows = KM.competitor_rows(SLUG, PRIMARY, TERMS, [], tmp_path)
    assert len(rows) == 1 and rows[0]["who"] == "competitors"
    assert rows[0]["note"].startswith("NOT FETCHED — ")


def test_table_markdown_names_every_column():
    t = {"slug": "x", "primary_keyword": PRIMARY, "terms": 5,
         "rows": [KM.board_row(_board())]}
    md = KM.markdown(t)
    for col in ("Page", "Words", "Unique terms", "Mentions", "Variations", "Title", "H1",
                "H2", "Alt", "Description", "First 100", "Title front"):
        assert col in md.splitlines()[0]
    assert "ours (board)" in md


def test_cli_prints_the_table_and_writes_the_json(tmp_path):
    out = tmp_path / "km.json"
    r = subprocess.run([sys.executable, str(SCRIPT), "blue-staffy-uk-breeders", "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "| Page |" in r.stdout
    data = json.loads(out.read_text())
    assert data["slug"] == "blue-staffy-uk-breeders"
    assert data["rows"][0]["who"].startswith("ours") and data["findings"] == []


def test_cli_refuses_an_unknown_board():
    r = subprocess.run([sys.executable, str(SCRIPT), "no-such-board-xyz"], capture_output=True, text=True)
    assert r.returncode == 2 and "no board" in r.stdout + r.stderr


def test_the_board_shows_the_table_on_new_pages_only():
    import build_page_board as BPB
    from test_page_board import ONT_OK, LEDGER_EMPTY
    html = BPB.render(_board(), ONT_OK, LEDGER_EMPTY, live={}, thumbs={},
                      slug="blue-staffy-first-week-at-home")
    assert "4b. Keyword metrics" in html and "ours (board)" in html
    demo = json.loads((ROOT / "data/boards/_demo.json").read_text())
    assert "4b. Keyword metrics" not in BPB.render(demo, ONT_OK, LEDGER_EMPTY, live={},
                                                    thumbs={}, slug="_demo")
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python3 -m pytest tests/py/test_keyword_metrics.py -q`
Expected: `1 error` — `ModuleNotFoundError: No module named 'keyword_metrics'`.

- [ ] **Step 3: Write the script**

Create `scripts/keyword_metrics.py`:

```python
#!/usr/bin/env python3
"""keyword_metrics.py — our page against the top five competitors, in numbers (CAG §7a).

Parity build, Task 18. One row per page: body words, how many of the board's keyword terms the
body carries (unique and total mentions), how many of its `variation` terms, the primary
keyword's exact matches per tag (title, H1, H2s, image alts, meta description), whether it
sits in the first 100 words of <main>, and whether the title is front-loaded with it.

  ours         the built page (dist/) once data/facts/rebuilt.json lists the slug; before
               that, the board's planned tags only (title, description, H1, section H2s)
  competitors  the first five unblocked pages of data/queries/raw/<slug>/competitors.json
               (Google order, then Bing), measured from the HTML --extract-h2 already saved
               in data/queries/cache/<slug>/<n>.html; with no cache file, the tag columns come
               from the page's saved `metrics` and the body columns are NOT FETCHED

Matching is by words: case and the small words (a, an, the, in, for, of, to, and, at, on,
with, from, by, is, are) are ignored, so "Blue Staffy Puppies in Manchester" matches
"blue staffy puppies manchester". No stemming: "puppy" is not "puppies".

Two checks fail a NEW page (family_rules scope; FAIL from `boarded` on, WARN on a draft):
  title-front-load   the picked title does not begin with the primary keyword (Rule 21 step 1)
  first-100-words    the rebuilt, built page does not carry the primary keyword in the first
                     100 words of <main> (a page not yet rebuilt measures nothing)

Usage:
  python3 scripts/keyword_metrics.py <board slug> [--json] [--out PATH]
      prints the markdown table (or the JSON with --json) and writes the JSON to --out,
      default docs/reports/keyword-metrics/<key>.json (gitignored).
      exit 0 · 1 a FAIL finding · 2 bad usage or an unreadable board
"""
import argparse
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import page_sections as PS  # noqa: E402  (imports nothing from the board scripts)

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORTS = ROOT / "docs" / "reports" / "keyword-metrics"
TOP = 5
FIRST_WORDS = 100
STOP = frozenset({"a", "an", "the", "in", "for", "of", "to", "and", "at", "on", "with", "from",
                  "by", "is", "are"})
TOKEN = re.compile(r"[a-z0-9£]+(?:'[a-z]+)?")
SKIP = {"script", "style", "template", "noscript", "svg", "nav", "footer", "aside", "form",
        "head", "title", "select"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source",
        "track", "wbr"}
_BOARDED_OR_LATER = PS.statuses_from("boarded")


# ── matching ────────────────────────────────────────────────────────────────────────────────
def words(text):
    return TOKEN.findall((text or "").replace("’", "'").lower())


def key_words(text):
    return [w for w in words(text) if w not in STOP]


def phrase_count(phrase, text):
    """How many times `phrase` occurs in `text`, small words and case ignored."""
    p, t = key_words(phrase), key_words(text)
    if not p:
        return 0
    return sum(1 for i in range(len(t) - len(p) + 1) if t[i:i + len(p)] == p)


def front_loaded(primary, title):
    p = key_words(primary)
    return bool(p) and key_words(title)[:len(p)] == p


# ── one page ────────────────────────────────────────────────────────────────────────────────
class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.title = None
        self.description = None
        self.h1, self.h2, self.alts = [], [], []
        self.body, self.main = [], []
        self._title = None
        self._head = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title" and self.title is None and "svg" not in self.stack:
            self._title = []
        if tag == "meta" and (a.get("name") or "").lower() == "description" and self.description is None:
            self.description = a.get("content") or ""
        if tag == "img" and not any(t in SKIP for t in self.stack):
            self.alts.append(a.get("alt") or "")
        if tag in ("h1", "h2") and self._head is None:
            self._head = (tag, [])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "title" and self._title is not None:
            self.title, self._title = "".join(self._title), None
        if self._head is not None and tag == self._head[0]:
            text = " ".join("".join(self._head[1]).split())
            if not any(t in SKIP for t in self.stack):
                (self.h1 if tag == "h1" else self.h2).append(text)
            self._head = None
        if tag in self.stack:
            del self.stack[len(self.stack) - 1 - self.stack[::-1].index(tag):]

    def handle_data(self, data):
        if self._title is not None:
            self._title.append(data)
        if any(t in SKIP for t in self.stack):
            return
        if self._head is not None:
            self._head[1].append(data)
        self.body.append(data)
        if "main" in self.stack:
            self.main.append(data)


def measure_html(html, primary, terms, variations):
    """The row numbers for one page. Body = <main> when the page has one, else every visible
    word outside navigation, footer, aside, form and the <head>."""
    p = _Page()
    p.feed(html)
    p.close()
    body = " ".join(p.main) if p.main else " ".join(p.body)
    found = {t: phrase_count(t, body) for t in dict.fromkeys(terms) if key_words(t)}
    title = p.title or ""
    return {
        "words": len(words(body)),
        "unique_terms": sum(1 for n in found.values() if n),
        "mentions": sum(found.values()),
        "variations": sum(1 for v in dict.fromkeys(variations) if phrase_count(v, body)),
        "exact": {"title": phrase_count(primary, title),
                  "h1": sum(phrase_count(primary, h) for h in p.h1),
                  "h2": sum(1 for h in p.h2 if phrase_count(primary, h)),
                  "alt": sum(1 for a in p.alts if phrase_count(primary, a)),
                  "description": phrase_count(primary, p.description or "")},
        "first_100": phrase_count(primary, " ".join(words(body)[:FIRST_WORDS])) > 0,
        "title_front": front_loaded(primary, title),
    }


# ── the board ───────────────────────────────────────────────────────────────────────────────
def board_terms(board):
    """(every keyword term on the board, its `variation` terms), first spelling kept."""
    terms, variations = [], []
    for s in board["sections"]:
        for kind, vals in s["keywords"].items():
            for t in vals:
                if t.strip():
                    terms.append(t.strip())
                    if kind == "variation":
                        variations.append(t.strip())
    return list(dict.fromkeys(terms)), list(dict.fromkeys(variations))


def board_row(board):
    """Our row before the page is built: the tags the board has picked, body columns empty."""
    import pageboard as PB   # lazy: pageboard imports family_rules, which imports this module
    primary = board["brief"]["primary_keyword"]
    title, desc = PB.meta_pick(board)
    h2s = [s["heading"] for s in board["sections"] if s.get("shape") != "hero"]
    return {"who": "ours (board)", "words": None, "unique_terms": None, "mentions": None,
            "variations": None,
            "exact": {"title": phrase_count(primary, title),
                      "h1": phrase_count(primary, PB.picked_h1(board)),
                      "h2": sum(1 for h in h2s if phrase_count(primary, h)),
                      "alt": None, "description": phrase_count(primary, desc)},
            "first_100": None, "title_front": front_loaded(primary, title),
            "note": "not built — the board's picked title, description, H1 and section H2s"}


def _rel(path):
    try:
        return pathlib.Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _bare(slug):
    return slug.strip("/").rsplit("/", 1)[-1]


def ours_row(board, dist=None, rebuilt=None):
    """The built page when the slug is rebuilt and built, else the board row."""
    import pageboard as PB
    slug = board["meta"]["slug"]
    rebuilt = PB.rebuilt_slugs() if rebuilt is None else rebuilt
    page = PB.built_page(slug, dist)
    if _bare(slug) in rebuilt and page.exists():
        terms, variations = board_terms(board)
        row = measure_html(page.read_text(encoding="utf-8", errors="ignore"),
                           board["brief"]["primary_keyword"], terms, variations)
        return dict({"who": "ours (built)"}, **row, note=_rel(page))
    return board_row(board)


# ── competitors ─────────────────────────────────────────────────────────────────────────────
def _rank(item):
    _, p = item
    return (p.get("google_pos") or 99, p.get("bing_pos") or 99, p.get("url", ""))


def competitor_rows(slug, primary, terms, variations, root=ROOT):
    """Rows for the first TOP unblocked pages of raw/<slug>/competitors.json."""
    bare = _bare(slug)
    path = pathlib.Path(root) / "data/queries/raw" / bare / "competitors.json"
    try:
        pages = json.loads(path.read_text(encoding="utf-8"))["pages"]
    except (OSError, ValueError, KeyError, TypeError):
        return [{"who": "competitors", "note": f"NOT FETCHED — no readable data/queries/raw/{bare}/"
                                               "competitors.json (bsuk-query-augmentation Step 3)"}]
    ranked = sorted(((n, p) for n, p in enumerate(pages, 1) if not p.get("blocked")), key=_rank)
    rows = []
    for n, p in ranked[:TOP]:
        cached = pathlib.Path(root) / "data/queries/cache" / bare / f"{n}.html"
        if cached.exists():
            row = measure_html(cached.read_text(encoding="utf-8", errors="replace"),
                               primary, terms, variations)
            rows.append(dict({"who": p["url"]}, **row, note="measured from data/queries/cache"))
            continue
        m = p.get("metrics") if isinstance(p.get("metrics"), dict) else {}
        title = m.get("title") or ""
        h2s = [s.get("h2", "") for s in m.get("sections", [])] or p.get("h2", [])
        rows.append({
            "who": p["url"], "words": m.get("word_count"), "unique_terms": None,
            "mentions": None, "variations": None,
            "exact": {"title": phrase_count(primary, title) if m else None, "h1": None,
                      "h2": sum(1 for h in h2s if phrase_count(primary, h)), "alt": None,
                      "description": phrase_count(primary, m.get("meta_description") or "") if m else None},
            "first_100": None, "title_front": front_loaded(primary, title) if m else None,
            "note": f"NOT FETCHED — data/queries/cache/{bare}/{n}.html is not on this machine; "
                    "tag columns from the saved metrics"})
    return rows


# ── checks (registered in family_rules) ────────────────────────────────────────────────────
def findings(board, dist=None, rebuilt=None):
    """[(check, severity, message)] for the two placement rules. Scope is the caller's:
    family_rules runs this on new location, comparison and blog pages only."""
    import pageboard as PB
    out = []
    primary = board["brief"]["primary_keyword"]
    sev = "FAIL" if board["meta"]["status"] in _BOARDED_OR_LATER else "WARN"
    title, _ = PB.meta_pick(board)
    if not front_loaded(primary, title):
        out.append(("title-front-load", sev,
                    f"the picked title {title!r} does not begin with the primary keyword "
                    f"{primary!r} (Rule 21 step 1; small words and case are ignored)"))
    slug = board["meta"]["slug"]
    rebuilt = PB.rebuilt_slugs() if rebuilt is None else rebuilt
    page = PB.built_page(slug, dist)
    if _bare(slug) in rebuilt and page.exists():
        m = measure_html(page.read_text(encoding="utf-8", errors="ignore"), primary, [], [])
        if not m["first_100"]:
            out.append(("first-100-words", "FAIL",
                        f"the built page does not carry {primary!r} in the first {FIRST_WORDS} "
                        f"words of <main> ({_rel(page)})"))
    return out


# ── the table ───────────────────────────────────────────────────────────────────────────────
def table(board, root=ROOT, dist=None, rebuilt=None):
    terms, variations = board_terms(board)
    primary = board["brief"]["primary_keyword"]
    return {"slug": board["meta"]["slug"], "primary_keyword": primary, "terms": len(terms),
            "rows": [ours_row(board, dist, rebuilt)]
            + competitor_rows(board["meta"]["slug"], primary, terms, variations, root)}


COLUMNS = ["Page", "Words", "Unique terms", "Mentions", "Variations", "Title", "H1", "H2",
           "Alt", "Description", "First 100", "Title front", "Note"]


def _cell(v):
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "yes" if v else "no"
    return str(v)


def cells(r):
    """One row as display strings, in COLUMNS order."""
    e = r.get("exact") or {}
    return [_cell(c) for c in (r["who"], r.get("words"), r.get("unique_terms"), r.get("mentions"),
                               r.get("variations"), e.get("title"), e.get("h1"), e.get("h2"),
                               e.get("alt"), e.get("description"), r.get("first_100"),
                               r.get("title_front"), r.get("note"))]


def markdown(t):
    lines = ["| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    for r in t["rows"]:
        lines.append("| " + " | ".join(c.replace("|", "\\|") for c in cells(r)) + " |")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--json", action="store_true", help="print the JSON instead of the table")
    ap.add_argument("--out", help="where to write the JSON (default docs/reports/keyword-metrics/<key>.json)")
    a = ap.parse_args(argv)
    import pageboard as PB
    try:
        board = PB.load_board(a.slug)
    except PB.BoardError as e:
        print(f"keyword-metrics ERROR {e}")
        return 2
    t = table(board)
    # The two checks bind new pages only (family_rules scope); the table is for any page.
    found = findings(board) if PB.FR.applies(board) else []
    t["findings"] = [{"check": c, "sev": s, "msg": m} for c, s, m in found]
    out = pathlib.Path(a.out) if a.out else REPORTS / (PB.slug_file(a.slug) + ".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(t, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(t, indent=2, ensure_ascii=False) if a.json else markdown(t))
    for f in t["findings"]:
        print(f"  {f['sev']:4s} {f['check']:18s} {f['msg']}")
    print(f"keyword-metrics {a.slug}: {len(t['rows'])} rows, {t['terms']} terms examined → {out}")
    return 1 if any(f["sev"] == "FAIL" for f in t["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
```

(It never writes "cag-" or the other `check:markers` words; `scripts/marker_check.py` fails any file it scans that does.)

- [ ] **Step 4: Register the two checks in family_rules**

Append to `scripts/family_rules.py`:

```python
# ── parity build Task 18: the primary keyword's placement (CAG §7a.7, §7d.6) ─────────────────
# The logic and the ours-vs-top-5 table are scripts/keyword_metrics.py; imported at the
# bottom for the same reason image_rules is. keyword_metrics imports pageboard only inside
# its functions, so this import can never see a half-built module.
import keyword_metrics as KM  # noqa: E402


@register
def keyword_placement(board, ont):
    """title-front-load (FAIL from `boarded`, WARN on a draft) and first-100-words (FAIL on a
    rebuilt, built page)."""
    return KM.findings(board)
```

- [ ] **Step 5: Show the table on the board (block 4b, new-family pages only)**

In `scripts/build_page_board.py`, after `import image_rules as IR          # block 7's image pickers (system-gaps build, Task 10b)` add

```python
import keyword_metrics as KM       # block 4b, the ours-vs-top-5 table (parity build Task 18)
```

and insert immediately before `    ent_md = (BE.entities_html(BE.group_entities(board, ont))`:

```python
    # parity build Task 18: CAG §7a's ours-vs-top-5 table, on a new-family page only, so the
    # twelve built boards render byte-for-byte as before.
    if new_family:
        kt = KM.table(board)
        parts.append(("4b. Keyword metrics",
                      f"Primary keyword **{md(kt['primary_keyword'])}** against the first five "
                      f"unblocked competitor pages, over the board's {kt['terms']} keyword terms. "
                      "Title / H1 / H2 / Alt / Description count the primary keyword's exact "
                      "matches; a dash is not measured. `python3 scripts/keyword_metrics.py "
                      f"{md(slug)}` prints the same table.\n\n"
                      + md_table(KM.COLUMNS, [[md(c) for c in KM.cells(r)] for r in kt["rows"]])))
```

- [ ] **Step 6: Run the tests and watch them pass**

Run: `python3 -m pytest tests/py/test_keyword_metrics.py -q`
Expected: `13 passed`.

- [ ] **Step 7: Regenerate the system registry (a new script)**

Run: `python3 scripts/build_system_registry.py`
Expected: `wrote docs/reference/system-registry.md` (the scripts list gains `keyword_metrics.py`).

- [ ] **Step 8: The table on a real board**

Run: `python3 scripts/keyword_metrics.py blue-staffy-uk-breeders --out /tmp/km.json | head -4`
Expected: the header row `| Page | Words | Unique terms | Mentions | Variations | Title | H1 | H2 | Alt | Description | First 100 | Title front | Note |`, an `ours (built)` row read from `dist/blue-staffy-uk-breeders/index.html`, and a `competitors` row `NOT FETCHED — no readable data/queries/raw/blue-staffy-uk-breeders/competitors.json …`; exit 0 (a built page is out of family scope, so no finding).

- [ ] **Step 9: Build and run every gate**

Run: `npm run -s build && npm run -s check:all && python3 -m pytest tests/py/test_keyword_metrics.py tests/py/test_page_board.py tests/py/test_family_rules.py tests/py/test_family_rules_on_board.py tests/py/test_board_entities.py tests/py/test_board_links.py tests/py/test_board_previews.py tests/py/test_anchor_types.py tests/py/test_keyword_variants.py tests/py/test_system_gaps_wiring.py tests/py/test_image_board_block.py tests/py/test_image_rules.py tests/py/test_system_registry.py tests/py/test_rules_index.py -q`
Expected: build 0; `check:all` exit 0; pytest all passed.

- [ ] **Step 10: Commit**

```bash
git add scripts/keyword_metrics.py tests/py/test_keyword_metrics.py scripts/family_rules.py \
  scripts/build_page_board.py docs/reference/system-registry.md
git commit -m "feat(board): keyword_metrics.py — ours vs top-5 table (block 4b); title front-load and first-100-words fail new pages

Measures words, keyword terms (unique and mentions), variations, the primary
keyword's exact matches per tag, first-100-words and title front-load on our
page (built page once rebuilt, else the board's picks) and the first five
unblocked competitors (from the Task 17 cache, else their saved metrics).
family_rules: title-front-load FAIL from boarded (WARN on a draft),
first-100-words FAIL on a rebuilt built page. New-family boards only.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 19: Geo-token check + two-keyword-header check (family_rules / board)

Audit rows 7b.9, 7a.8, 12.6 (Wave 3 #17). Two advisory checks (WARN at every status) in `family_rules`, so they appear in board block 7b and in `board_gate.py` on new-family pages only:
- `geo-token-missing` (location pages): no body H2 names a geo term (any section's `geo` keywords, or `UK`), or the picked meta description names none.
- `two-keyword-header` (every new-family page): a body section (`page_sections.body_sections`, so hero/stats/trust/reviews/FAQ/form are never read) carries fewer than two keyword types, or its H2 names none of its own terms.

Matching reuses `keyword_metrics.phrase_count` (words; case and small words ignored).

**Files:**
- Create: `tests/py/test_geo_and_header_keywords.py`
- Modify: `scripts/family_rules.py` (append after the Task 18 block)
- Modify: `tests/py/test_image_rules.py:94`

- [ ] **Step 1: Write the failing test**

Create `tests/py/test_geo_and_header_keywords.py`:

```python
# tests/py/test_geo_and_header_keywords.py — family_rules geo-token-missing and
# two-keyword-header (parity build Task 19; CAG §7b geo token rule, §12 two-keyword headers;
# audit rows 7b.9, 7a.8, 12.6). Both are advisory (WARN) on new pages.
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import family_rules as FR  # noqa: E402

GOOD_DESC = ("Home-raised blue Staffy puppies for Manchester families, from our house in "
             "Carlisle, with delivery or collection and first-week support.")


def _board(page_type="location", heading="How We Raise Blue Staffy Puppies for Manchester",
           desc=GOOD_DESC, geo=("manchester",), lsi=("home-raised puppies",)):
    b = copy.deepcopy(json.loads((ROOT / "data/boards/_demo.json").read_text()))
    b["meta"].update(slug="blue-staffy-puppies-testcity", page_type=page_type, status="boarded")
    b["meta_set"]["descriptions"][0] = desc
    b["meta_set"]["pick"]["description"] = 0
    body = b["sections"][2]                      # how-we-raise: the one body section
    body["heading"] = heading
    body["keywords"]["primary"] = ["blue staffy puppies"]
    body["keywords"]["geo"] = list(geo)
    body["keywords"]["lsi"] = list(lsi)
    return b


def _ours(board, ids=("geo-token-missing", "two-keyword-header")):
    return [f for f in FR.findings(board, ont={}) if f[0] in ids]


def test_a_location_page_with_geo_in_an_h2_and_the_description_passes():
    assert _ours(_board()) == []


def test_no_geo_term_in_any_body_h2_warns():
    got = _ours(_board(heading="How We Raise Blue Staffy Puppies"), ("geo-token-missing",))
    assert [f[:2] for f in got] == [("geo-token-missing", "WARN")]
    assert "H2" in got[0][2] and "manchester" in got[0][2]


def test_no_geo_term_in_the_picked_description_warns():
    desc = ("Home-raised blue Staffy puppies from our house in Carlisle, with delivery or "
            "collection, first-week support and a written guarantee for every pup.")
    got = _ours(_board(desc=desc), ("geo-token-missing",))
    assert [f[:2] for f in got] == [("geo-token-missing", "WARN")]
    assert "description" in got[0][2]


def test_uk_counts_as_a_geo_token():
    desc = GOOD_DESC.replace("Manchester families", "UK families")
    assert _ours(_board(heading="How We Raise Blue Staffy Puppies in the UK", desc=desc,
                        geo=()), ("geo-token-missing",)) == []


def test_the_geo_rule_binds_location_pages_only():
    assert _ours(_board(page_type="blog", heading="How We Raise Blue Staffy Puppies"),
                 ("geo-token-missing",)) == []


def test_a_body_section_with_one_keyword_type_warns():
    got = _ours(_board(geo=(), lsi=()), ("two-keyword-header",))
    assert [f[:2] for f in got] == [("two-keyword-header", "WARN")]
    assert "how-we-raise" in got[0][2] and "1 keyword type" in got[0][2]


def test_a_heading_that_carries_none_of_its_sections_terms_warns():
    got = _ours(_board(heading="Life In Our Kitchen"), ("two-keyword-header",))
    assert [f[:2] for f in got] == [("two-keyword-header", "WARN")]
    assert "carries none" in got[0][2]


def test_frame_sections_are_not_headers_the_rule_reads():
    b = _board()
    b["sections"][1]["keywords"] = {k: [] for k in b["sections"][1]["keywords"]}   # stats
    assert _ours(b, ("two-keyword-header",)) == []


def test_the_twelve_built_pages_are_never_read():
    b = _board(heading="Life In Our Kitchen", desc="x" * 150)
    b["meta"]["slug"] = "blue-staffy-uk-breeders"
    assert _ours(b) == []
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python3 -m pytest tests/py/test_geo_and_header_keywords.py -q`
Expected: `4 failed, 5 passed` — the four WARN tests fail (`assert [] == [('geo-token-missing', 'WARN')]` and the `two-keyword-header` equivalents); the five "passes / not read" tests pass already.

- [ ] **Step 3: Add the two checks**

Append to `scripts/family_rules.py`:

```python
# ── parity build Task 19: the geo token and two-keyword headers (audit rows 7b.9, 12.6) ─────
# Advisory: WARN at every status. Terms are matched as keyword_metrics matches them (words,
# case and small words ignored), so "Puppies in Manchester" carries "puppies manchester".
GEO_ALWAYS = ("UK",)


def _geo_terms(board):
    terms = [t.strip() for s in board["sections"] for t in s["keywords"].get("geo", []) if t.strip()]
    return list(dict.fromkeys(terms + list(GEO_ALWAYS)))


@register
def geo_token(board, ont):
    """A location page names a geo term (a `geo` keyword, or UK) in at least one body H2 and
    in the picked meta description — the token that decides a local query's retrieval."""
    if board["meta"]["page_type"] != "location":
        return
    import pageboard as PB   # lazy, as keyword_metrics does: pageboard imports this module
    geo = _geo_terms(board)
    named = ", ".join(repr(t) for t in geo)
    if not any(KM.phrase_count(t, s["heading"]) for s in PS.body_sections(board) for t in geo):
        yield ("geo-token-missing", "WARN",
               f"no body H2 names a geo term ({named}) — put the city or UK in at least one")
    _, desc = PB.meta_pick(board)
    if not any(KM.phrase_count(t, desc) for t in geo):
        yield ("geo-token-missing", "WARN",
               f"the picked meta description names no geo term ({named})")


@register
def two_keyword_header(board, ont):
    """Every body section carries at least two keyword types, and its H2 names a term of at
    least one of them (the SEO master checklist's Two-Keyword Headers)."""
    for s in PS.body_sections(board):
        types = [k for k, vals in s["keywords"].items() if any(t.strip() for t in vals)]
        if len(types) < 2:
            yield ("two-keyword-header", "WARN",
                   f"section {s['id']!r} carries {len(types)} keyword type"
                   f"{'' if len(types) == 1 else 's'} ({', '.join(types) or 'none'}) — a body "
                   "header is planned on two")
            continue
        terms = [t for k in types for t in s["keywords"][k] if t.strip()]
        if not any(KM.phrase_count(t, s["heading"]) for t in terms):
            yield ("two-keyword-header", "WARN",
                   f"section {s['id']!r}: the H2 {s['heading']!r} carries none of its own "
                   f"{', '.join(types)} terms")
```

- [ ] **Step 4: Narrow the one image test that asserted every family finding is a FAIL**

`tests/py/test_image_rules.py::test_a_boarded_location_record_owes_a_slot_under_every_body_heading` runs `FR.findings` on a boarded location record and asserted every finding is FAIL; the new checks add WARNs there. Replace `:94`

```python
    assert all(sev == "FAIL" for c, sev, m in found)
```

with

```python
    # The image rules FAIL; other family rules on the same record (the advisory geo and
    # header-keyword checks, parity build Task 19) may WARN.
    assert all(sev == "FAIL" for c, sev, m in found if c.startswith("image-"))
```

- [ ] **Step 5: Run the tests and watch them pass**

Run: `python3 -m pytest tests/py/test_geo_and_header_keywords.py tests/py/test_image_rules.py tests/py/test_keyword_metrics.py -q`
Expected: `75 passed`.

- [ ] **Step 6: Build and run every gate**

Run: `npm run -s build && npm run -s check:all && python3 -m pytest tests/py/test_geo_and_header_keywords.py tests/py/test_family_rules.py tests/py/test_family_rules_on_board.py tests/py/test_page_board.py tests/py/test_image_rules.py tests/py/test_system_gaps_wiring.py tests/py/test_outline_provenance_check.py -q`
Expected: build 0; `check:all` exit 0; pytest all passed.

- [ ] **Step 7: Commit**

```bash
git add scripts/family_rules.py tests/py/test_geo_and_header_keywords.py tests/py/test_image_rules.py
git commit -m "feat(board): geo-token and two-keyword-header checks on new pages (advisory)

geo-token-missing (location pages): a geo term or UK in at least one body H2
and in the picked meta description. two-keyword-header: every body section
plans two keyword types and its H2 names one of its own terms. WARN only.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 20: Claim ledger inverted: un-ledgered health/credential claim fails

Audit row 1d.1 (Wave 3 #18). A new `evidence_audit.py` check, `claim-unledgered`: every sentence of `<main>` that uses the ledger's health or credential `vocabulary` (BVA hip/elbow scores, DNA tests and "clear" results, KC registration, a breeder licence, vet checks, health testing) must match a ledger `claims` row in the same sentence, or carry `LICENCE_CLAIM_PLACEHOLDER` / `LEGAL_CLAIM_PLACEHOLDER`. A question is not a claim; a heading ends a sentence; JSON-LD is not prose. ERROR on a new page (location/comparison/blog, bare slug in `data/facts/rebuilt.json`, not one of family_rules' frozen twelve); WARN on every other page (today's `--all` run reports 222 such WARNs on the migrated and frozen pages — advisory, and exactly KI 68's point). The vocabulary lives in `data/quality/evidence-ledger.json` beside the claims it is checked against.

**Files:**
- Create: `tests/py/test_evidence_unledgered.py`
- Modify: `scripts/evidence_audit.py` — docstring `:8-17`, `:20-22` (usage), `:43` (`REBUILT_PATH`), `:45-53` (`CHECK_IDS`), new block before `:189`, `audit` `:225` and `:239`, `main` `:292`, `:316`, `:322`
- Modify: `data/quality/evidence-ledger.json` (add `_vocabulary_comment`, `vocabulary`)
- Modify: `data/quality/rule-index.json` (new row after `claim-bound-to-proof`, `:428-434`)
- Modify: `rules/copy.md` `:48`, `:50`, after `:55`

- [ ] **Step 1: Write the failing test**

Create `tests/py/test_evidence_unledgered.py`:

```python
# tests/py/test_evidence_unledgered.py — evidence_audit.py `claim-unledgered` (parity build
# Task 20; audit row 1d.1): a health or credential claim on a page must match a row of
# data/quality/evidence-ledger.json in the same sentence, or be a claim placeholder. ERROR on
# a new location, comparison or blog page; WARN on every other page.
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_audit as E  # noqa: E402

REAL_LEDGER = json.loads((ROOT / "data/quality/evidence-ledger.json").read_text(encoding="utf-8"))
LEDGER = {"claims": [
    {"id": "parents-dna-clear", "pattern": r"(?:certified|tested)\s+clear", "proof": "NOT FETCHED",
     "anchor": "dna-tests", "confirmed": None}],
    "vocabulary": REAL_LEDGER["vocabulary"]}


def page(main):
    return f"<html><head><title>T</title></head><body><main>{main}</main></body></html>"


@pytest.mark.parametrize("sentence,vocab", [
    ("<p>Our DNA-tested parents live with us.</p>", "dna-test"),
    ("<p>Both parents are hip scored by the BVA.</p>", "hip-elbow-score"),
    ("<p>Every puppy is KC registered.</p>", "kc-registered"),
    ("<p>We are a licensed breeder.</p>", "licensed-breeder"),
    ("<p>Each pup leaves vet checked.</p>", "vet-checked"),
    ("<p>Our dogs are health tested.</p>", "health-tested"),
])
def test_an_unledgered_claim_is_found(sentence, vocab):
    got = E.unledgered_claims(page(sentence), LEDGER)
    assert [v for v, _ in got] == [vocab]


def test_a_sentence_the_ledger_covers_passes():
    html = page("<p>Both parents are DNA tested clear of L-2-HGA and HC-HSF4.</p>")
    assert E.unledgered_claims(html, LEDGER) == []


def test_the_ledger_must_match_in_the_same_sentence():
    html = page("<p>The parents were tested clear. Our DNA-tested parents live with us.</p>")
    assert [v for v, _ in E.unledgered_claims(html, LEDGER)] == ["dna-test"]


def test_a_heading_is_its_own_sentence():
    html = page("<h2>Our DNA-Tested Parents</h2><p>They were tested clear in spring.</p>")
    assert [v for v, _ in E.unledgered_claims(html, LEDGER)] == ["dna-test"]


def test_questions_and_placeholders_are_not_claims():
    html = page("<h3>Are the parents health tested?</h3>"
                "<p>We are a LICENCE_CLAIM_PLACEHOLDER licensed breeder.</p>")
    assert E.unledgered_claims(html, LEDGER) == []


def test_a_species_statement_is_not_a_credential():
    html = page("<p>The Staffordshire Bull Terrier is a KC-recognised breed.</p>")
    assert E.unledgered_claims(html, LEDGER) == []


def test_json_ld_is_not_prose():
    html = page('<script type="application/ld+json">{"d": "DNA tested parents"}</script><p>Hi.</p>')
    assert E.unledgered_claims(html, LEDGER) == []


def test_a_ledger_without_vocabulary_checks_nothing():
    assert E.unledgered_claims(page("<p>Our DNA-tested parents.</p>"), {"claims": []}) == []


def test_audit_errors_on_a_new_page_and_warns_elsewhere():
    html = page("<p>Our DNA-tested parents live with us.</p>")
    budgets = {"budgets": {}, "terms": {}}
    new = E.audit("blue-staffy-first-week-at-home", html, "blog", budgets, LEDGER, new_page=True)
    old = E.audit("blue-staffy-health-uk", html, "interior", budgets, LEDGER)
    assert [s for s, m in new if "un-ledgered" in m] == ["ERROR"]
    assert [s for s, m in old if "un-ledgered" in m] == ["WARN"]


def test_new_page_is_a_rebuilt_family_page_outside_the_frozen_twelve():
    rebuilt = {"blue-staffy-puppies-leeds", "blue-staffy-health-uk", "blue-staffy-blog-guides"}
    assert E.is_new_page("uk-locations/blue-staffy-puppies-leeds", "location", rebuilt)
    assert not E.is_new_page("uk-locations/blue-staffy-puppies-york", "location", rebuilt)
    assert not E.is_new_page("blue-staffy-health-uk", "interior", rebuilt)
    assert not E.is_new_page("blue-staffy-blog-guides", "blog", rebuilt)


def test_the_real_ledger_vocabulary_compiles_and_the_check_id_is_registered():
    import re
    for vid, pat in REAL_LEDGER["vocabulary"].items():
        re.compile(pat)
    assert {"id": "claim-unledgered"} in E.CHECK_IDS
    index = json.loads((ROOT / "data/quality/rule-index.json").read_text())
    row = next(r for r in index["rules"] if r["id"] == "claim-unledgered")
    assert row["test"] == "scripts/evidence_audit.py::claim-unledgered"


def test_the_cli_exits_1_on_a_new_page_with_an_unledgered_claim(tmp_path):
    q = tmp_path / "data/quality"
    q.mkdir(parents=True)
    (q / "evidence-budgets.json").write_text(json.dumps({"budgets": {}, "terms": {}}))
    (q / "evidence-ledger.json").write_text(json.dumps(LEDGER))
    dist = tmp_path / "dist" / "uk-locations" / "blue-staffy-puppies-leeds"
    dist.mkdir(parents=True)
    (dist / "index.html").write_text(page("<p>Our DNA-tested parents live with us.</p>"))
    rebuilt = tmp_path / "rebuilt.json"
    rebuilt.write_text(json.dumps(["blue-staffy-puppies-leeds"]))
    r = subprocess.run([sys.executable, str(ROOT / "scripts/evidence_audit.py"),
                        "uk-locations/blue-staffy-puppies-leeds", "--dist", str(tmp_path / "dist"),
                        "--budgets", str(q / "evidence-budgets.json"),
                        "--ledger", str(q / "evidence-ledger.json"), "--rebuilt", str(rebuilt)],
                       capture_output=True, text=True)
    assert r.returncode == 1, r.stdout
    assert "ERROR un-ledgered claim" in r.stdout
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python3 -m pytest tests/py/test_evidence_unledgered.py -q`
Expected: `1 error` — collection fails with `KeyError: 'vocabulary'` (the ledger has no vocabulary yet).

- [ ] **Step 3: Add the vocabulary to the ledger**

In `data/quality/evidence-ledger.json`, replace the file's last two lines (`  ]` closing `"claims"`, then `}`) with:

```json
  ],
  "_vocabulary_comment": "Health and credential vocabulary (parity build Task 20). evidence_audit.py `claim-unledgered` reads every sentence of <main> that matches one of these patterns and requires a `claims` row whose pattern matches the same sentence, or a LICENCE_CLAIM_PLACEHOLDER / LEGAL_CLAIM_PLACEHOLDER. A question is not a claim. ERROR on a new location, comparison or blog page; WARN elsewhere. To state a new claim, add its `claims` row first (proof NOT FETCHED until the document is on file) — never widen or delete a vocabulary pattern to clear a finding.",
  "vocabulary": {
    "hip-elbow-score": "\\bBVA\\b|\\bhip\\s+(?:and\\s+elbow\\s+)?(?:scores?|scored|graded?)\\b|\\belbow\\s+(?:scores?|scored|graded?)\\b",
    "dna-test": "\\bDNA[- ]?(?:tested|tests?|profiled)\\b",
    "dna-clear": "\\b(?:tested|certified|recorded)\\s+clear\\b|\\bclear\\s+(?:DNA\\s+)?results?\\b|\\bclear\\s+of\\s+(?:L-?2-?HGA|HC(?:-HSF4)?|PHPV)\\b",
    "kc-registered": "\\bKC[- ]registered\\b|\\bKennel\\s+Club[- ]registered\\b",
    "licensed-breeder": "\\blicen[cs]ed\\s+(?:dog\\s+)?breeders?\\b|\\bcouncil[- ]licen[cs]ed\\b|\\bbreeding\\s+licen[cs]e\\b",
    "vet-checked": "\\bvet(?:erinary)?[- ](?:checked|health[- ]checked|examined|certified)\\b",
    "health-tested": "\\bhealth[- ]tested\\b|\\bhealth\\s+certificates?\\b"
  }
}
```

- [ ] **Step 4: Add the check to evidence_audit.py**

(a) In the docstring, after the two `claim-bound-to-proof` lines add:

```text
  claim-unledgered            a sentence using the ledger's health/credential `vocabulary` that no
                              ledger claim matches (ERROR on a new location, comparison or blog
                              page — rebuilt, outside family_rules' frozen twelve; WARN elsewhere)
```

and after the first usage line add `                                    [--rebuilt PATH]   (default data/facts/rebuilt.json)`.

(b) After `TARGETS_PATH = ROOT / "tests" / "render" / "targets.json"` add `REBUILT_PATH = ROOT / "data" / "facts" / "rebuilt.json"`; in `CHECK_IDS`, after `{"id": "claim-bound-to-proof"},` add `{"id": "claim-unledgered"},`.

(c) Insert immediately before `# ── statement-labels-present ─`:

```python
# ── claim-unledgered ───────────────────────────────────────────────────────
PLACEHOLDERS = ("LICENCE_CLAIM_PLACEHOLDER", "LEGAL_CLAIM_PLACEHOLDER")
# A block ends a sentence even without a full stop: a heading never runs into its paragraph.
BLOCK_END = re.compile(r"</(?:p|h[1-6]|li|td|th|dt|dd|figcaption|blockquote|caption|summary)\s*>", re.I)
NEW_PAGE_TYPES = ("location", "comparison", "blog")


def sentences(html):
    """The sentences of <main>, split at block ends and at . ! ? — script/style dropped."""
    body = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", main_html(html), flags=re.S | re.I)
    out = []
    for block in BLOCK_END.split(body):
        out += [s for s in re.split(r"(?<=[.!?])\s+", text_of(block)) if s]
    return out


def unledgered_claims(html, ledger):
    """[(vocabulary id, sentence)] for every sentence that uses the ledger's health or
    credential vocabulary and that no ledger claim pattern matches. A question, and a
    sentence carrying a claim placeholder, is not a claim. A ledger with no `vocabulary`
    checks nothing."""
    vocab = ledger.get("vocabulary") or {}
    out = []
    for s in sentences(html):
        if s.rstrip().endswith("?") or any(p in s for p in PLACEHOLDERS):
            continue
        if any(re.search(c["pattern"], s, flags=re.I) for c in ledger.get("claims", [])):
            continue
        for vid, pat in vocab.items():
            if re.search(pat, s, flags=re.I):
                out.append((vid, s))
                break
    return out


def is_new_page(slug, page_type, rebuilt):
    """A page project 5 builds: a location, comparison or blog page whose bare slug is in
    data/facts/rebuilt.json and is not one of family_rules' twelve frozen pages."""
    import family_rules as FR   # lazy: only the audit's main path needs it
    bare = slug.strip("/").rsplit("/", 1)[-1]
    return (page_type in NEW_PAGE_TYPES and bare in rebuilt
            and bare not in FR.BUILT_BEFORE_SYSTEM_GAPS)


def rebuilt_slugs(path=REBUILT_PATH):
    try:
        rows = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {r for r in rows if isinstance(r, str)} if isinstance(rows, list) else set()
```

(d) Change `def audit(slug, html, page_type, budgets, ledger):` to `def audit(slug, html, page_type, budgets, ledger, new_page=False):` and insert before `    for sid in missing_statement_labels(html):`:

```python
    for vid, sentence in unledgered_claims(html, ledger):
        f.append(("ERROR" if new_page else "WARN",
                  f"un-ledgered claim ({vid}): \"{sentence[:120]}\" — add its row to "
                  "data/quality/evidence-ledger.json (proof NOT FETCHED until the document is "
                  "on file) or write the claim placeholder"))
```

(e) In `main`: before `    ap.add_argument("--fail-on-error", action="store_true",` add

```python
    ap.add_argument("--rebuilt", default=str(REBUILT_PATH),
                    help="data/facts/rebuilt.json: which pages are new (claim-unledgered ERRORs there)")
```

replace `    errs = warns = 0` with

```python
    rebuilt = rebuilt_slugs(a.rebuilt)
    errs = warns = 0
```

and replace `        f = audit(slug, html, pt, budgets, ledger)` with `        f = audit(slug, html, pt, budgets, ledger, new_page=is_new_page(slug, pt, rebuilt))`.

- [ ] **Step 5: Register the rule**

In `data/quality/rule-index.json`, immediately after the `claim-bound-to-proof` object add:

```json
  {
   "id": "claim-unledgered",
   "family": "COPY",
   "enforced": "test",
   "test": "scripts/evidence_audit.py::claim-unledgered",
   "severity": "blocking"
  },
```

In `rules/copy.md`: `:48` "Each of the seven checks below" → "Each of the eight checks below"; `:50` "Seven checks in `scripts/evidence_audit.py`" → "Eight checks in `scripts/evidence_audit.py`"; after the `claim-bound-to-proof` bullet (`:55`) add:

```markdown
- `claim-unledgered` (blocking on new location, comparison and blog pages; advisory elsewhere) — a sentence that uses the ledger's health or credential `vocabulary` (BVA hip and elbow scores, DNA tests and "clear" results, KC registration, a breeder licence, vet checks, health testing) must match a ledger `claims` row in the same sentence or carry the claim placeholder. A question is not a claim. The fix is a ledger row (proof `NOT FETCHED` until the document is on file), never a wider vocabulary pattern.
```

- [ ] **Step 6: Run the tests and watch them pass**

Run: `python3 -m pytest tests/py/test_evidence_unledgered.py tests/py/test_evidence_audit.py tests/py/test_rules_index.py tests/py/test_quality_report.py tests/py/test_evidence_per_slug_overrides.py -q`
Expected: `369 passed` (17 new).

- [ ] **Step 7: See what it reports on today's pages (advisory there)**

Run: `python3 scripts/evidence_audit.py --all | grep -c "un-ledgered"`
Expected: `222` (all WARN: no built page is a new project-5 page yet). Record the number in the commit message; do not add ledger rows or edit pages in this task.

- [ ] **Step 8: Build and run every gate**

Run: `npm run -s build && npm run -s check:all && python3 -m pytest tests/py/test_evidence_unledgered.py tests/py/test_agent_facts.py tests/py/test_claude_md.py tests/py/test_marker_check.py -q`
Expected: build 0; `check:all` exit 0; pytest all passed.

- [ ] **Step 9: Commit**

```bash
git add scripts/evidence_audit.py data/quality/evidence-ledger.json data/quality/rule-index.json \
  rules/copy.md tests/py/test_evidence_unledgered.py
git commit -m "feat(evidence): claim-unledgered — a health or credential claim must match the ledger

Every <main> sentence using the ledger's vocabulary (hip/elbow scores, DNA
tests and clear results, KC registration, licence, vet checks, health testing)
must match a claims row in the same sentence or carry the claim placeholder.
ERROR on new location/comparison/blog pages, WARN elsewhere (222 WARNs on
today's migrated and frozen pages; KI 68).

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 21: NOT FETCHED — <barrier> lint on new/changed board, query, research files

Audit rows 1f.2, 5d (Wave 3 #19). `scripts/not_fetched_lint.py` (`npm run check:barriers`, in `check:all` right after `check:gaps`): in `data/boards/*.json`, `data/queries/**/*.json` and `docs/research/**/*.{md,json}`, every `NOT FETCHED` is followed by `— <barrier>` (en dash, colon or an opening bracket also count; backticks or bold around the token are fine), or — in JSON — is exactly `"NOT FETCHED"` with a non-empty `"reason"` or `"barrier"` beside it. Files that already carried a bare one are grandfathered **by content hash** in `data/quality/not-fetched-baseline.json`, written once in this task; editing such a file ends its exemption. `query_augment.py` stops writing a bare `NOT FETCHED` into a question file's `sources` (it writes `NOT FETCHED — no data/queries/raw/<slug>/<src>.json`, or the raw file's own `reason`), so the tool that writes question files passes the lint it is held to. Blocking by construction only for new and changed files.

**Files:**
- Create: `scripts/not_fetched_lint.py`
- Create: `tests/py/test_not_fetched_lint.py`
- Create (generated once): `data/quality/not-fetched-baseline.json`
- Modify: `scripts/query_augment.py` — `load_candidates` `:1106-1117` (+ new `_source_status` before it), `bank_candidates` `:1135-1139`, `load_competitors` `:1155-1160`, `build` `:1273-1274` (line numbers before Task 17; after it they sit ~170 lines lower)
- Modify: `tests/py/test_query_augment.py:615`, `:845`
- Modify: `package.json` (`check:barriers`; `check:all`)
- Modify: `tests/py/test_package_scripts.py:93-114`
- Modify: `CLAUDE.md` `:129` (working rule 9) and `:255-257` (the chain)
- Modify: `scripts/build_system_registry.py:42` (gate table) and the generated `docs/reference/system-registry.md`
- Modify: `.claude/skills/bsuk-reddit-threads/SKILL.md:99-100`

- [ ] **Step 1: Write the failing test**

Create `tests/py/test_not_fetched_lint.py`:

```python
# tests/py/test_not_fetched_lint.py — scripts/not_fetched_lint.py (parity build Task 21; audit
# rows 1f.2, 5d): a NOT FETCHED in a new or changed board, query or research file names its
# barrier. Files that already carried a bare one are grandfathered by content hash in
# data/quality/not-fetched-baseline.json; editing one ends its exemption.
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import not_fetched_lint as L  # noqa: E402

SCRIPT = ROOT / "scripts" / "not_fetched_lint.py"


@pytest.mark.parametrize("text", [
    "GSC: NOT FETCHED — the property is unverified.",
    "GSC: NOT FETCHED – the property is unverified.",
    "GSC: `NOT FETCHED` — the property is unverified.",
    "**NOT FETCHED**: no raw HTML was saved.",
    "Word target NOT FETCHED (no competitor scan yet).",
])
def test_a_named_barrier_passes_in_text(text):
    assert L.bare_in_text(text) == []


@pytest.mark.parametrize("text", [
    "GSC: NOT FETCHED.",
    "GSC is NOT FETCHED until project 6.",
    "| Bing | NOT FETCHED |",
    "NOT FETCHED —",
])
def test_a_bare_token_is_found_in_text(text):
    assert len(L.bare_in_text(text)) == 1


def test_json_accepts_an_inline_barrier_or_a_sibling_reason():
    ok = {"a": "NOT FETCHED — the host timed out",
          "b": {"status": "NOT FETCHED", "reason": "homepage timed out"},
          "c": {"status": "NOT FETCHED", "barrier": "login wall"},
          "d": [{"proof": "NOT FETCHED — certificate not on file"}]}
    assert L.bare_in_json(ok) == []


def test_json_finds_every_bare_value_with_its_path():
    bad = {"sources": {"ai_engines": "NOT FETCHED", "bank": "ok"},
           "pages": [{"status": "NOT FETCHED", "reason": ""}]}
    assert L.bare_in_json(bad) == ["$.sources.ai_engines", "$.pages[0].status"]


def _root(tmp_path, files, baseline=None):
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    if baseline is not None:
        q = tmp_path / "data/quality"
        q.mkdir(parents=True, exist_ok=True)
        (q / "not-fetched-baseline.json").write_text(json.dumps(baseline))
    return tmp_path


def test_a_new_file_with_a_bare_token_fails(tmp_path):
    root = _root(tmp_path, {"docs/research/new.md": "Bing: NOT FETCHED.\n"}, {"files": {}})
    probs, examined, kept = L.lint(root)
    assert probs == ["docs/research/new.md:1  a bare NOT FETCHED — name the barrier: "
                     "`NOT FETCHED — <barrier>`"]
    assert examined == 1 and kept == 0


def test_an_unchanged_grandfathered_file_passes_and_an_edited_one_fails(tmp_path):
    text = "Bing: NOT FETCHED.\n"
    root = _root(tmp_path, {"docs/research/old.md": text},
                 {"files": {"docs/research/old.md": L.sha(text.encode())}})
    assert L.lint(root) == ([], 1, 1)
    (root / "docs/research/old.md").write_text(text + "More notes.\n")
    probs, _, kept = L.lint(root)
    assert len(probs) == 1 and kept == 0


def test_the_scope_is_boards_queries_and_research_only(tmp_path):
    root = _root(tmp_path, {"docs/reference/x.md": "NOT FETCHED.\n",
                            "data/queries/cache/s/1.html": "NOT FETCHED.\n",
                            "data/boards/inbox/x.json": '{"a": "NOT FETCHED"}',
                            "data/boards/x.json": '{"a": "NOT FETCHED"}',
                            "data/queries/raw/s/threads.json": '{"status": "NOT FETCHED"}'},
                 {"files": {}})
    probs, examined, _ = L.lint(root)
    assert examined == 2
    assert sorted(p.split("  ")[0] for p in probs) == ["data/boards/x.json:$.a",
                                                       "data/queries/raw/s/threads.json:$.status"]


def test_an_unreadable_json_file_is_a_problem(tmp_path):
    root = _root(tmp_path, {"data/queries/x.json": "{NOT FETCHED"}, {"files": {}})
    probs, _, _ = L.lint(root)
    assert probs and "not valid JSON" in probs[0]


def test_write_baseline_refuses_to_overwrite(tmp_path):
    root = _root(tmp_path, {"docs/research/old.md": "NOT FETCHED.\n"}, {"files": {}})
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--write-baseline"],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "exists" in r.stderr


def test_write_baseline_then_check_passes(tmp_path):
    root = _root(tmp_path, {"docs/research/old.md": "NOT FETCHED.\n",
                            "docs/research/clean.md": "NOT FETCHED — named.\n"})
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--write-baseline"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    base = json.loads((root / "data/quality/not-fetched-baseline.json").read_text())
    assert list(base["files"]) == ["docs/research/old.md"]
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)], capture_output=True, text=True)
    assert r.returncode == 0 and "examined 2 files (1 grandfathered); 0 problems" in r.stdout


def test_a_missing_baseline_is_not_a_pass(tmp_path):
    root = _root(tmp_path, {"docs/research/clean.md": "NOT FETCHED — named.\n"})
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)], capture_output=True, text=True)
    assert r.returncode == 2 and "baseline" in r.stdout + r.stderr


def test_the_real_tree_passes():
    probs, examined, _ = L.lint(ROOT)
    assert examined > 0 and probs == []


def test_the_question_file_query_augment_writes_names_every_barrier(tmp_path):
    import query_augment as Q
    from test_query_augment import make_root, seed, write_raw
    root = make_root(tmp_path)
    seed(root)
    write_raw(root, "m", "threads", {"source": "threads", "status": "NOT FETCHED",
                                     "reason": "reddit refused the headless browser",
                                     "questions": []})
    data, _ = Q.build("m", "location", "blue staffy puppies manchester", "/uk-locations/m/",
                      root, "2026-09-26")
    assert L.bare_in_json(data) == []
    assert data["sources"]["threads"] == "NOT FETCHED — reddit refused the headless browser"
    assert data["sources"]["ai_engines"] == "NOT FETCHED — no data/queries/raw/m/ai_engines.json"
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python3 -m pytest tests/py/test_not_fetched_lint.py -q`
Expected: `1 error` — `ModuleNotFoundError: No module named 'not_fetched_lint'`.

- [ ] **Step 3: Write the lint**

Create `scripts/not_fetched_lint.py`:

```python
#!/usr/bin/env python3
"""not_fetched_lint.py — a NOT FETCHED names its barrier (audit rows 1f.2 and 5d).

Parity build, Task 21. A bare `NOT FETCHED` cannot be compared against a later run: nobody
knows what to try next. So in the research a page is built from — data/boards/*.json,
data/queries/**/*.json and docs/research/**/*.{md,json} — every NOT FETCHED is written

  text   NOT FETCHED — <barrier>      (an en dash, a colon or an opening bracket also count;
                                       backticks or bold around the token are fine)
  JSON   "NOT FETCHED — <barrier>", or "NOT FETCHED" with a non-empty "reason" or
         "barrier" string beside it in the same object

Files that already carried a bare one when this check arrived are grandfathered BY CONTENT
HASH in data/quality/not-fetched-baseline.json. Editing such a file ends its exemption:
a changed file is linted like a new one. Never rerun --write-baseline to clear a finding —
name the barrier instead.

Out of scope: gitignored working folders (data/boards/inbox, data/boards/previews,
data/queries/cache) and every other tree.

Usage:
  python3 scripts/not_fetched_lint.py [--root DIR]      exit 0 clean · 1 problems · 2 no baseline
  python3 scripts/not_fetched_lint.py --write-baseline  once, when the check is introduced;
                                                        refuses (exit 2) if the file exists
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASELINE = pathlib.Path("data/quality/not-fetched-baseline.json")
SCOPE = (("data/boards", ("*.json",)), ("data/queries", ("**/*.json",)),
         ("docs/research", ("**/*.md", "**/*.json")))
IGNORED = ("data/boards/inbox/", "data/boards/previews/", "data/queries/cache/")
TOKEN = re.compile(r"NOT FETCHED")
# After the token: optional closing markup, then a dash, colon or bracket, then a word.
NAMED = re.compile(r"[`*_\"']*\s*(?:—|–|:|\()\s*[`*_\"']*\w")
REASON_KEYS = ("reason", "barrier")
FIX = "a bare NOT FETCHED — name the barrier: `NOT FETCHED — <barrier>`"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bare_in_text(text):
    """[line number] of every NOT FETCHED not followed by a named barrier."""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in TOKEN.finditer(line):
            if not NAMED.match(line, m.end()):
                out.append(i)
    return out


def bare_in_json(node, path="$", parent=None):
    """[JSON path] of every string value carrying a bare NOT FETCHED."""
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            out += bare_in_json(v, f"{path}.{k}", node)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += bare_in_json(v, f"{path}[{i}]", None)
    elif isinstance(node, str) and TOKEN.search(node):
        if bare_in_text(node):
            sibling = parent is not None and node.strip() == "NOT FETCHED" and any(
                isinstance(parent.get(k), str) and parent[k].strip() for k in REASON_KEYS)
            if not sibling:
                out.append(path)
    return out


def scoped_files(root):
    root = pathlib.Path(root)
    seen = set()
    for base, patterns in SCOPE:
        for pat in patterns:
            for p in sorted((root / base).glob(pat)):
                rel = p.relative_to(root).as_posix()
                if p.is_file() and not rel.startswith(IGNORED) and rel not in seen:
                    seen.add(rel)
                    yield rel, p


def problems_in(rel, path):
    """[problem line] for one file, empty when every NOT FETCHED names its barrier."""
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    if "NOT FETCHED" not in text:
        return []
    if rel.endswith(".json"):
        try:
            where = bare_in_json(json.loads(text))
        except ValueError:
            return [f"{rel}  not valid JSON — cannot tell which NOT FETCHED names a barrier"]
        return [f"{rel}:{w}  {FIX}" for w in where]
    return [f"{rel}:{n}  {FIX}" for n in bare_in_text(text)]


def load_baseline(root):
    p = pathlib.Path(root) / BASELINE
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8")).get("files", {})


def lint(root=ROOT):
    """(problems, files examined, files grandfathered). Raises FileNotFoundError without a
    baseline: a check with nothing to compare against has not passed."""
    base = load_baseline(root)
    if base is None:
        raise FileNotFoundError(str(BASELINE))
    probs, examined, kept = [], 0, 0
    for rel, path in scoped_files(root):
        examined += 1
        found = problems_in(rel, path)
        if found and base.get(rel) == sha(path.read_bytes()):
            kept += 1
            continue
        probs += found
    return probs, examined, kept


def write_baseline(root):
    files = {}
    for rel, path in scoped_files(root):
        if problems_in(rel, path):
            files[rel] = sha(path.read_bytes())
    out = pathlib.Path(root) / BASELINE
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "_comment": "Files that carried a bare NOT FETCHED when scripts/not_fetched_lint.py "
                    "arrived (parity build Task 21), by sha256 of their content. An entry "
                    "exempts that exact content only: edit the file and it is linted like a "
                    "new one. Never regenerate this file to clear a finding.",
        "files": files}, indent=2) + "\n", encoding="utf-8")
    return len(files)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--write-baseline", action="store_true")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root)
    if a.write_baseline:
        if (root / BASELINE).exists():
            print(f"not-fetched-lint: {BASELINE} exists — it is written once, never regenerated",
                  file=sys.stderr)
            return 2
        n = write_baseline(root)
        print(f"not-fetched-lint: wrote {BASELINE} — {n} files grandfathered")
        return 0
    try:
        probs, examined, kept = lint(root)
    except FileNotFoundError:
        print(f"not-fetched-lint: no {BASELINE} — examined nothing, not a pass")
        return 2
    for p in probs:
        print(f"  {p}")
    print(f"not-fetched-lint: examined {examined} files ({kept} grandfathered); "
          f"{len(probs)} problems")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: query_augment names every barrier it writes**

In `scripts/query_augment.py` replace

```python
def load_candidates(slug, root=ROOT):
    raw = Path(root) / "data/queries/raw" / slug
    cands, status = [], {}
    for src in CANDIDATE_SOURCES:
        path = raw / f"{src}.json"
        d = _load(path, None)
        if d is None:
            status[src] = "NOT FETCHED"
            continue
        if not isinstance(d, dict):
            raise BadInput(path, "top level must be an object")
        status[src] = _status(d, path)
```

with

```python
def _source_status(d, path, rel):
    """A raw file's status for the question file's `sources`. A NOT FETCHED carries its
    barrier (parity build Task 21): the file's own "reason" or "barrier", else a note that
    the file names none."""
    st = _status(d, path)
    if st != "NOT FETCHED":
        return st
    why = next((d[k].strip() for k in ("reason", "barrier")
                if isinstance(d.get(k), str) and d[k].strip()), None)
    return f"NOT FETCHED — {why or rel + ' names no reason'}"


def load_candidates(slug, root=ROOT):
    raw = Path(root) / "data/queries/raw" / slug
    cands, status = [], {}
    for src in CANDIDATE_SOURCES:
        path = raw / f"{src}.json"
        rel = f"data/queries/raw/{slug}/{src}.json"
        d = _load(path, None)
        if d is None:
            status[src] = f"NOT FETCHED — no {rel}"
            continue
        if not isinstance(d, dict):
            raise BadInput(path, "top level must be an object")
        status[src] = _source_status(d, path, rel)
```

In `bank_candidates` replace

```python
    """(candidates, status). A missing bank is "NOT FETCHED"; a malformed one is BadInput."""
    path = Path(root) / "data/faq.json"
    rows = _load(path, None)
    if rows is None:
        return [], "NOT FETCHED"
```

with

```python
    """(candidates, status). A missing bank is NOT FETCHED; a malformed one is BadInput."""
    path = Path(root) / "data/faq.json"
    rows = _load(path, None)
    if rows is None:
        return [], "NOT FETCHED — no data/faq.json"
```

In `load_competitors` replace

```python
    if d is None:
        return {"status": "NOT FETCHED", "pages": []}
    if not isinstance(d, dict):
        raise BadInput(path, "top level must be an object")
    _status(d, path)
```

with

```python
    if d is None:
        return {"status": f"NOT FETCHED — no data/queries/raw/{slug}/competitors.json",
                "pages": []}
    if not isinstance(d, dict):
        raise BadInput(path, "top level must be an object")
    _source_status(d, path, f"data/queries/raw/{slug}/competitors.json")
```

In `build` replace

```python
    comp = load_competitors(slug, root)
    status["competitors"] = comp.get("status", "ok")
```

with

```python
    comp = load_competitors(slug, root)
    rel = f"data/queries/raw/{slug}/competitors.json"
    status["competitors"] = (comp["status"] if comp.get("status", "").startswith("NOT FETCHED — ")
                             else _source_status(comp, Path(root) / rel, rel))
```

(The raw files' own `status` enum — `ok|fallback|NOT FETCHED` — is unchanged; only the question file's `sources` strings carry the barrier. `competitor_metrics` never writes the resolved string back.)

In `tests/py/test_query_augment.py` replace `:615` `    assert data["sources"]["serp_bing"] == "NOT FETCHED"` with `    assert data["sources"]["serp_bing"] == "NOT FETCHED — no data/queries/raw/m/serp_bing.json"` and `:845` `    assert Q.bank_candidates(root) == ([], "NOT FETCHED")` with `    assert Q.bank_candidates(root) == ([], "NOT FETCHED — no data/faq.json")`.

- [ ] **Step 5: Write the baseline — once**

Run: `python3 scripts/not_fetched_lint.py --write-baseline && python3 scripts/not_fetched_lint.py`
Expected: `not-fetched-lint: wrote data/quality/not-fetched-baseline.json — 14 files grandfathered` then `not-fetched-lint: examined 146 files (14 grandfathered); 0 problems` (counts measured on the verification copy after Tasks 17–20; if Waves 1–2 changed research files the numbers differ — any count is fine, `0 problems` is not optional). The 14 were: `data/queries/blue-staffy-puppies-for-sale-leeds.json`, `docs/research/keyword-gap-2026-09-25.md`, and twelve `docs/research/competitors/*.md|json` reports.

- [ ] **Step 6: Wire it into check:all**

In `package.json` add after `"check:workflow": …,`:

```json
    "check:barriers": "python3 scripts/not_fetched_lint.py",
```

and in `check:all` replace `npm run check:gaps && ` with `npm run check:gaps && npm run check:barriers && `. In `tests/py/test_package_scripts.py::test_the_check_all_chain_is_the_documented_one` insert `"check:barriers"` into `expected` immediately after `"check:gaps"`, and after the comment line `# check:gaps follows check:competitors: the matrix is rebuilt from the registry's reports.` add:

```python
    # check:barriers follows check:gaps (parity build Task 21): the last research guard — a
    # NOT FETCHED in a new or changed board, query or research file names its barrier.
```

In `CLAUDE.md`, working rule 9: replace the line

```markdown
   competitor metrics. Un-fetched data is written `NOT FETCHED`, never inferred. The
```

with

```markdown
   competitor metrics. Un-fetched data is written `NOT FETCHED — <barrier>` (what was tried
   and what stopped it), never inferred; `npm run check:barriers` holds new and changed
   board, query and research files to it. The
```

and in the chain paragraph (`:255-257`) replace

```markdown
`check:redirects`, `check:schema`, `check:queries`, `check:competitors`, `check:gaps`,
`check:sitemaps`, `check:placeholders`, `check:workflow`, `check:markers` and `agents`, in
```

with

```markdown
`check:redirects`, `check:schema`, `check:queries`, `check:competitors`, `check:gaps`,
`check:barriers`, `check:sitemaps`, `check:placeholders`, `check:workflow`, `check:markers`
and `agents`, in
```

(If Waves 1–2 already changed this paragraph, insert `` `check:barriers`, `` right after `` `check:gaps`, `` and re-wrap.) In `scripts/build_system_registry.py` `GATES`, after the `scripts/gap_matrix.py` row add:

```python
    ("scripts/not_fetched_lint.py", "a NOT FETCHED in a new or changed board, query or research file names its barrier"),
```

then run `python3 scripts/build_system_registry.py` (expected `wrote docs/reference/system-registry.md`). In `.claude/skills/bsuk-reddit-threads/SKILL.md` replace

```markdown
- `status` is `ok`, `fallback` (only the lower rungs worked) or `NOT FETCHED` (write the file
  with empty `questions` and `threads` lists and say which rungs failed).
```

with

```markdown
- `status` is `ok`, `fallback` (only the lower rungs worked) or `NOT FETCHED` (write the file
  with empty `questions` and `threads` lists and a `"reason"` naming which rungs failed —
  `npm run check:barriers` fails a bare `NOT FETCHED`).
```

- [ ] **Step 7: Run the tests and watch them pass**

Run: `python3 -m pytest tests/py/test_not_fetched_lint.py tests/py/test_query_augment.py tests/py/test_competitor_metrics.py tests/py/test_package_scripts.py tests/py/test_claude_md.py tests/py/test_system_registry.py tests/py/test_rules_index.py -q`
Expected: all passed (`test_not_fetched_lint.py`: 20).

- [ ] **Step 8: Build and run every gate**

Run: `npm run -s build && npm run -s check:all`
Expected: exit 0, and the chain prints `not-fetched-lint: examined 146 files (14 grandfathered); 0 problems`.

- [ ] **Step 9: Commit**

```bash
git add scripts/not_fetched_lint.py tests/py/test_not_fetched_lint.py data/quality/not-fetched-baseline.json \
  scripts/query_augment.py tests/py/test_query_augment.py package.json tests/py/test_package_scripts.py \
  CLAUDE.md scripts/build_system_registry.py docs/reference/system-registry.md \
  .claude/skills/bsuk-reddit-threads/SKILL.md
git commit -m "feat(gates): check:barriers — a NOT FETCHED in new or changed research names its barrier

not_fetched_lint.py lints data/boards, data/queries and docs/research: text
needs 'NOT FETCHED — <barrier>', JSON the inline form or a reason/barrier key.
14 files that already carried a bare one are grandfathered by content hash;
editing one ends the exemption. query_augment writes the barrier into a
question file's sources. Wired into check:all after check:gaps.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 22: Shared Reddit thread ledger across city pages

Audit row 6.20 (Wave 3 #20). `data/queries/thread-ledger.json` is derived by `scripts/thread_ledger.py --write` from every `data/queries/raw/<slug>/threads.json` (never hand-edited): per canonical permalink, its title, forum, posted month, reply count, the questions read from it, first/last read date and the pages that used it. `--known URL…` says `reuse` (read in the last 180 days) or `fetch`; `--seed URL…` prints the rows and questions in `threads.json` shape with `score: null` (Step C is scored per page) and `stale` recomputed for today. `npm run check:threads` (in `check:all` after `check:barriers`) fails when the ledger and the threads files disagree. Today: 14 threads from 2 pages, 6 of them read by both Manchester and Leeds. `query_coverage_check.py` skips the ledger like it skips `spend.json`.

**Files:**
- Create: `scripts/thread_ledger.py`
- Create: `tests/py/test_thread_ledger.py`
- Create (generated): `data/queries/thread-ledger.json`
- Modify: `scripts/query_coverage_check.py:63-65` (`LEDGERS`)
- Modify: `package.json` (`check:threads`; `check:all`)
- Modify: `tests/py/test_package_scripts.py` (the Task 21 lines)
- Modify: `CLAUDE.md` (the chain paragraph)
- Modify: `scripts/build_system_registry.py` (after the Task 21 row) and the generated `docs/reference/system-registry.md`
- Modify: `.claude/skills/bsuk-reddit-threads/SKILL.md` (before `## Step C` `:42`, before `## Linking` `:103`, Common mistakes)

- [ ] **Step 1: Write the failing test**

Create `tests/py/test_thread_ledger.py`:

```python
# tests/py/test_thread_ledger.py — scripts/thread_ledger.py, the shared Reddit and forum
# thread ledger (parity build Task 22; audit row 6.20). Built from the committed
# data/queries/raw/<slug>/threads.json files; nothing here fetches.
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import thread_ledger as T  # noqa: E402

SCRIPT = ROOT / "scripts" / "thread_ledger.py"
A = "https://www.reddit.com/r/UK_Pets/comments/aaa111/first_dog/"
B = "https://www.reddit.com/r/StaffordBullTerriers/comments/bbb222/blue_staffy/"


def row(url, replies=5, score=6, posted="2026-01"):
    return {"permalink": url, "title": url.rsplit("/", 2)[-2], "subreddit": "r/UK_Pets",
            "posted": posted, "replies": replies, "score": score, "stale": False}


def q(text, url, fact=None):
    return {"text": text, "detail": f"thread:{url}", "fact_source": fact}


def write_threads(root, slug, fetched, questions, threads, status="ok"):
    d = root / "data/queries/raw" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "threads.json").write_text(json.dumps({"source": "threads", "status": status,
                                                "fetched": fetched, "questions": questions,
                                                "threads": threads}))


def two_pages(tmp_path):
    write_threads(tmp_path, "city-a", "2026-09-01",
                  [q("Is a Staffy good for a first-time owner?", A)], [row(A, replies=5)])
    write_threads(tmp_path, "city-b", "2026-09-20",
                  [q("Is a Staffy good for a first-time owner?", A),
                   q("Are blue Staffies healthy?", B, "bank:health-dna-tests")],
                  [row(A + "?utm=x", replies=9), row(B)])
    return tmp_path


@pytest.mark.parametrize("url", [
    "https://old.reddit.com/r/UK_Pets/comments/aaa111/first_dog",
    "https://reddit.com/r/UK_Pets/comments/aaa111/first_dog/?utm_source=share#c1",
    "HTTPS://WWW.Reddit.com/r/UK_Pets/comments/aaa111/first_dog/",
])
def test_canonical_folds_the_spellings_of_one_thread(url):
    assert T.canonical(url) == A


def test_build_merges_every_page_that_used_a_thread(tmp_path):
    led = T.build(two_pages(tmp_path))
    assert sorted(led["threads"]) == sorted([A, B])
    a = led["threads"][A]
    assert a["used_by"] == ["city-a", "city-b"]
    assert a["first_fetched"] == "2026-09-01" and a["last_fetched"] == "2026-09-20"
    assert a["replies"] == 9                      # the latest read wins
    assert a["questions"] == [{"text": "Is a Staffy good for a first-time owner?",
                               "fact_source": None}]
    assert led["threads"][B]["questions"][0]["fact_source"] == "bank:health-dna-tests"


def test_a_not_fetched_threads_file_adds_nothing(tmp_path):
    write_threads(tmp_path, "city-c", "2026-09-20", [], [], status="NOT FETCHED")
    assert T.build(tmp_path)["threads"] == {}


def test_known_reuses_a_recent_thread_and_fetches_the_rest(tmp_path):
    led = T.build(two_pages(tmp_path))
    got = T.known(led, [A, "https://www.reddit.com/r/dogs/comments/ccc333/new/"], today="2026-10-01")
    assert got[0]["action"] == "reuse" and got[0]["used_by"] == ["city-a", "city-b"]
    assert got[1]["action"] == "fetch"
    assert T.known(led, [A], today="2027-06-01")[0]["action"] == "fetch"   # older than 180 days


def test_seed_writes_threads_json_rows_with_the_score_left_to_the_page(tmp_path):
    led = T.build(two_pages(tmp_path))
    seed = T.seed(led, [A, B], today="2026-10-01")
    assert [t["permalink"] for t in seed["threads"]] == [A, B]
    assert all(t["score"] is None for t in seed["threads"])
    assert set(seed["threads"][0]) == {"permalink", "title", "subreddit", "posted", "replies",
                                       "score", "stale"}
    assert seed["questions"][0] == q("Is a Staffy good for a first-time owner?", A)
    old = T.seed(led, [B], today="2028-06-01")["threads"][0]
    assert old["stale"] is True                   # posted over 24 months before today


def test_seed_refuses_a_thread_the_ledger_does_not_hold(tmp_path):
    led = T.build(two_pages(tmp_path))
    with pytest.raises(KeyError):
        T.seed(led, ["https://www.reddit.com/r/dogs/comments/zzz/none/"], today="2026-10-01")


def test_cli_write_then_check(tmp_path):
    root = two_pages(tmp_path)
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "--write" in r.stdout
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--write"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "2 threads" in r.stdout
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "examined 2 threads files" in r.stdout
    write_threads(root, "city-d", "2026-09-25", [], [row("https://www.reddit.com/r/x/comments/d/e/")])
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "STALE" in r.stdout


def test_cli_known_prints_one_line_per_url(tmp_path):
    root = two_pages(tmp_path)
    subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--write"], check=True,
                   capture_output=True)
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--today", "2026-10-01",
                        "--known", A, "https://www.reddit.com/r/dogs/comments/ccc333/new/"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    lines = r.stdout.strip().splitlines()
    assert lines[0].startswith("reuse ") and "city-a, city-b" in lines[0]
    assert lines[1].startswith("fetch ")


def test_the_real_ledger_is_current():
    r = subprocess.run([sys.executable, str(SCRIPT), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def test_the_question_file_gate_does_not_read_the_ledger_as_a_question_file():
    import query_coverage_check as QC
    assert "thread-ledger.json" in QC.LEDGERS
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python3 -m pytest tests/py/test_thread_ledger.py -q`
Expected: `1 error` — `ModuleNotFoundError: No module named 'thread_ledger'`.

- [ ] **Step 3: Write the script**

Create `scripts/thread_ledger.py`:

```python
#!/usr/bin/env python3
"""thread_ledger.py — one ledger of the Reddit and forum threads every page has read.

Parity build, Task 22 (audit row 6.20). Each page's bsuk-reddit-threads run writes
data/queries/raw/<slug>/threads.json; many of the threads (the city-agnostic searches) are
the same across the 28 city pages. data/queries/thread-ledger.json is DERIVED from those
files — never hand-edited — and says, per thread: its title, forum, posted month, reply
count, the questions read from it, when it was read and by which pages. A thread read in
the last REUSE_DAYS days is reused from the ledger instead of being opened again.

  thread_ledger.py --write                 rebuild the ledger from every threads.json
  thread_ledger.py --check                 exit 1 when the ledger is missing or stale
                                           (npm run check:threads)
  thread_ledger.py --known URL [URL ...]   one line per URL: `reuse` (read in the last
                                           REUSE_DAYS days; prints who read it) or `fetch`
  thread_ledger.py --seed URL [URL ...]    prints {"questions", "threads"} for a new page's
                                           threads.json from the ledger — `score` is null:
                                           Step C is scored for THIS page; `stale` is
                                           recomputed against --today
  --root DIR, --today YYYY-MM-DD for tests.

Exit 0 · 1 stale or missing ledger (--check) · 2 bad usage or a URL --seed cannot find.
"""
import argparse
import datetime
import json
import pathlib
import sys
from urllib.parse import urlsplit, urlunsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = pathlib.Path("data/queries/thread-ledger.json")
REUSE_DAYS = 180
STALE_MONTHS = 24          # bsuk-reddit-threads Step C: older than 24 months is stale
REDDIT_HOSTS = {"reddit.com", "old.reddit.com", "np.reddit.com", "new.reddit.com",
                "m.reddit.com", "www.reddit.com"}
ROW_KEYS = ("permalink", "title", "subreddit", "posted", "replies", "score", "stale")
COMMENT = ("Derived by scripts/thread_ledger.py --write from every "
           "data/queries/raw/<slug>/threads.json; never hand-edited. `npm run check:threads` "
           "fails when it is stale. bsuk-reddit-threads reads it before opening a thread.")


def canonical(url):
    """One spelling per thread: https, lower-case host (every reddit host is www.reddit.com),
    no query or fragment, one trailing slash."""
    p = urlsplit(url.strip())
    host = p.netloc.lower()
    if host in REDDIT_HOSTS:
        host = "www.reddit.com"
    path = p.path.rstrip("/") + "/"
    return urlunsplit(("https", host, path, "", ""))


def _threads_files(root):
    return sorted((pathlib.Path(root) / "data/queries/raw").glob("*/threads.json"))


def build(root=ROOT):
    """The ledger dict, from every threads.json whose status is not NOT FETCHED."""
    rows, files = {}, 0
    for f in _threads_files(root):
        d = json.loads(f.read_text(encoding="utf-8"))
        files += 1
        if d.get("status") == "NOT FETCHED":
            continue
        slug, fetched = f.parent.name, d.get("fetched") or ""
        asked = {}
        for qn in d.get("questions", []):
            detail = qn.get("detail") or ""
            if detail.startswith("thread:"):
                asked.setdefault(canonical(detail[len("thread:"):]), []).append(
                    {"text": qn["text"], "fact_source": qn.get("fact_source")})
        for t in d.get("threads", []):
            key = canonical(t["permalink"])
            e = rows.setdefault(key, {"title": None, "subreddit": None, "posted": None,
                                      "replies": None, "first_fetched": fetched,
                                      "last_fetched": "", "questions": [], "used_by": []})
            if fetched >= e["last_fetched"]:     # the latest read's facts win
                e.update(title=t.get("title"), subreddit=t.get("subreddit"),
                         posted=t.get("posted"), replies=t.get("replies"), last_fetched=fetched)
            e["first_fetched"] = min(e["first_fetched"], fetched)
            if slug not in e["used_by"]:
                e["used_by"].append(slug)
            seen = {x["text"] for x in e["questions"]}
            e["questions"] += [x for x in asked.get(key, []) if x["text"] not in seen]
    for e in rows.values():
        e["used_by"].sort()
    return {"_comment": COMMENT, "files": files, "threads": dict(sorted(rows.items()))}


def _day(s):
    return datetime.date.fromisoformat(s)


def _months_between(posted, today):
    y, m = (int(x) for x in posted.split("-")[:2])
    return (today.year - y) * 12 + (today.month - m)


def known(ledger, urls, today):
    """[{"url", "action": "reuse"|"fetch", "last_fetched", "used_by"}] in the order given."""
    out, day = [], _day(today)
    for u in urls:
        e = ledger["threads"].get(canonical(u))
        recent = e is not None and e["last_fetched"] and \
            (day - _day(e["last_fetched"])).days <= REUSE_DAYS
        out.append({"url": canonical(u), "action": "reuse" if recent else "fetch",
                    "last_fetched": e["last_fetched"] if e else None,
                    "used_by": e["used_by"] if e else []})
    return out


def seed(ledger, urls, today):
    """{"questions", "threads"} in threads.json's shape for these ledger threads. Raises
    KeyError for a URL the ledger does not hold."""
    qs, rows, day = [], [], _day(today)
    for u in urls:
        key = canonical(u)
        e = ledger["threads"][key]
        rows.append({"permalink": key, "title": e["title"], "subreddit": e["subreddit"],
                     "posted": e["posted"], "replies": e["replies"], "score": None,
                     "stale": bool(e["posted"]) and _months_between(e["posted"], day) > STALE_MONTHS})
        qs += [{"text": x["text"], "detail": f"thread:{key}", "fact_source": x["fact_source"]}
               for x in e["questions"]]
    return {"questions": qs, "threads": rows}


def _dump(ledger):
    return json.dumps(ledger, indent=2, ensure_ascii=False) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--today", default=datetime.datetime.now(datetime.timezone.utc).date().isoformat())
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--known", nargs="+", metavar="URL")
    g.add_argument("--seed", nargs="+", metavar="URL")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root)
    path = root / LEDGER
    fresh = build(root)
    if a.write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_dump(fresh), encoding="utf-8")
        print(f"thread-ledger: wrote {LEDGER} — {len(fresh['threads'])} threads from "
              f"{fresh['files']} threads files")
        return 0
    if a.check:
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != _dump(fresh):
            print(f"thread-ledger: STALE — {LEDGER} does not match the threads files; run "
                  "python3 scripts/thread_ledger.py --write")
            return 1
        print(f"thread-ledger: examined {fresh['files']} threads files, "
              f"{len(fresh['threads'])} threads; 0 problems")
        return 0
    ledger = json.loads(path.read_text(encoding="utf-8")) if path.exists() else fresh
    if a.known:
        for k in known(ledger, a.known, a.today):
            who = ", ".join(k["used_by"])
            print(f"{k['action']} {k['url']}" + (f" — read {k['last_fetched']} by {who}"
                                                  if k["last_fetched"] else " — not in the ledger"))
        return 0
    try:
        print(json.dumps(seed(ledger, a.seed, a.today), indent=2, ensure_ascii=False))
    except KeyError as e:
        print(f"thread-ledger: {e.args[0]} is not in the ledger — open it (Step D)", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: The question-file gate skips the ledger**

In `scripts/query_coverage_check.py` replace

```python
# The spend guard's two ledgers (scripts/query_augment.py) share data/queries/ with the
# question files; neither is one.
LEDGERS = {"spend.json", "dashboard.json"}
```

with

```python
# The spend guard's two ledgers (scripts/query_augment.py) and the shared thread ledger
# (scripts/thread_ledger.py) share data/queries/ with the question files; none is one.
LEDGERS = {"spend.json", "dashboard.json", "thread-ledger.json"}
```

(Without this `check:queries` fails: `thread-ledger: invalid question file — Additional properties are not allowed`.)

- [ ] **Step 5: Write the ledger**

Run: `python3 scripts/thread_ledger.py --write && python3 scripts/thread_ledger.py --check`
Expected: `thread-ledger: wrote data/queries/thread-ledger.json — 14 threads from 2 threads files`, then `thread-ledger: examined 2 threads files, 14 threads; 0 problems`.

- [ ] **Step 6: Run the tests and watch them pass**

Run: `python3 -m pytest tests/py/test_thread_ledger.py tests/py/test_query_coverage_check.py -q`
Expected: all passed (`test_thread_ledger.py`: 12).

- [ ] **Step 7: Wire it into check:all, the registry and the skill**

`package.json`: after `"check:barriers": …,` add `    "check:threads": "python3 scripts/thread_ledger.py --check",` and in `check:all` replace `npm run check:barriers && ` with `npm run check:barriers && npm run check:threads && `. `tests/py/test_package_scripts.py`: insert `"check:threads"` into `expected` right after `"check:barriers"` and extend the Task 21 comment with:

```python
    # check:threads follows it (parity build Task 22): the shared thread ledger matches the
    # threads files, so no city page re-opens a thread another page has read.
```

`CLAUDE.md` chain paragraph: replace

```markdown
`check:barriers`, `check:sitemaps`, `check:placeholders`, `check:workflow`, `check:markers`
and `agents`, in
```

with

```markdown
`check:barriers`, `check:threads`, `check:sitemaps`, `check:placeholders`, `check:workflow`,
`check:markers` and `agents`, in
```
 `scripts/build_system_registry.py` `GATES`, after the `not_fetched_lint.py` row:

```python
    ("scripts/thread_ledger.py", "the shared Reddit and forum thread ledger matches every page's threads file (`--check`)"),
```

then `python3 scripts/build_system_registry.py`. In `.claude/skills/bsuk-reddit-threads/SKILL.md`, insert immediately before `## Step C — score each candidate (keep 5 or more with a score of 5+)`:

```markdown
**Read the ledger before you open anything.** Every thread another page has read is in
`data/queries/thread-ledger.json`. Run

```bash
python3 scripts/thread_ledger.py --known <permalink> [<permalink> ...]
```

`reuse` = read in the last 180 days: do not open it again. `python3 scripts/thread_ledger.py
--seed <permalink> ...` prints its `threads` rows and `questions` in Step E's shape — copy them
in, then score each row for THIS page in Step C (`score` comes out `null`; `stale` is
recomputed for today). `fetch` = new or older than 180 days: open it as below.
```

immediately before the heading line `## Linking` (`` `fact_source` ``):

```markdown
Then rebuild the ledger so the next page reuses what this one read:

```bash
python3 scripts/thread_ledger.py --write
```

`npm run check:threads` fails while the ledger and the threads files disagree.
```

and under Common mistakes, after `- Spending calls rediscovering the ladder — Step B's table already says which rung works.` add:

```markdown
- Opening a thread the ledger says another page read in the last 180 days — `--seed` it.
```

- [ ] **Step 8: Build and run every gate**

Run: `npm run -s build && npm run -s check:all && python3 -m pytest tests/py/test_thread_ledger.py tests/py/test_package_scripts.py tests/py/test_claude_md.py tests/py/test_system_registry.py tests/py/test_rules_index.py tests/py/test_builder_skills.py tests/py/test_skills_frontmatter.py tests/py/test_agent_facts.py tests/py/test_not_fetched_lint.py tests/py/test_no_third_party_contacts.py tests/py/test_workflow_ref_check.py -q`
Expected: build 0; `check:all` exit 0 with `thread-ledger: examined 2 threads files, 14 threads; 0 problems`; pytest all passed.

- [ ] **Step 9: Commit**

```bash
git add scripts/thread_ledger.py tests/py/test_thread_ledger.py data/queries/thread-ledger.json \
  scripts/query_coverage_check.py package.json tests/py/test_package_scripts.py CLAUDE.md \
  scripts/build_system_registry.py docs/reference/system-registry.md \
  .claude/skills/bsuk-reddit-threads/SKILL.md
git commit -m "feat(queries): shared thread ledger — no city page re-opens a thread another read

thread_ledger.py derives data/queries/thread-ledger.json from every
raw/<slug>/threads.json (14 threads, 6 read by both Manchester and Leeds).
--known says reuse or fetch; --seed prints threads.json rows with the score
left to the page. check:threads (after check:barriers) fails a stale ledger.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Wave 4 — The per-page run (Tasks 23–27)

### Task 23: docs/reference/page-run.md — the ordered per-page run (CAG §0→§22 mapped to BSUK commands), guarded by check:workflow

**Why.** The user's framing: the page-build brief is "a workflow before I build a page". BSUK has
every part of it spread over a dozen files and no single run. This task writes the run: one
row per brief step, each naming the BSUK command/skill/board block, the deliverable, the gate
that fails when the step is skipped, and whether the run stops for the breeder. It folds in
four rulings received during planning (2026-09-26): (1) the session opens with `grill-me`, then
`superpowers:writing-plans`, then the page-type builder skill (controller, brief §2 parity);
(2) the `impeccable:impeccable` and `frontend-design:frontend-design` skills are mandatory,
named Harden steps on every project 5 page (user); (3) `superpowers:verification-before-completion`
runs before any "page done" claim and again at close (user); (4) each of those is routed in
CLAUDE.md, WORKFLOW.md, the three builder skills and (for verification) `session-closer`.
The enforcement of (2) and (3) — the `data/page-runs/<slug>.json` record and the gate that
fails without it — is Task 25.

**Assumptions (read before starting).**
- Tasks 1–22 have landed. The run names `scripts/keyword_metrics.py` (Task 18) and
  `scripts/rendered_changes.py` (Task 16) as bare paths, so both files must exist or
  `npm run check:workflow` fails; it names no flag of `keyword_metrics.py`.
- Row 4's gate reads "`npm run check:barriers` (Task 21's barrier lint) and `npm run test:py` (the spend guard)": this assumes
  Task 21's `NOT FETCHED — <barrier>` lint runs as `npm run check:barriers` (it is in `check:all`,
  confirmed by the controller's integration replay).
- Row 11 says `board_gate.py` runs for every rebuilt page inside `npm run check:all` (Task 12),
  row 12 says a new page is added to `tests/render/targets.json` (Task 10) and that
  `npm run test:render:pages` rebuilds the scorecards (Task 11), and row 16's scan reads "the
  page, its template and data, and the kit" (Task 15).
- Four scripts the run names do not exist yet. Each line naming one carries the marker
  `(arrives in Task N)` and a bare backticked path, so `tests/py/test_claude_md.py`
  (`test_no_arrives_in_task_marker_is_stale`) fails the moment the script lands until the
  marker is removed: `scripts/page_intake.py` (Task 24), `scripts/gate_page.py` and
  `scripts/page_run_record.py` (Task 25), `scripts/measurement_ledger.py` (Task 26), and the
  decision doc (Task 27). This task teaches `workflow_ref_check.py` to accept that marker.
- Never write `cag-` (the marker gate bans the prefix in `docs/reference/`, `CLAUDE.md` and
  `rules/`), the former city outside its two slugs, or a £ figure outside the locked set in
  any file below.

**Files:**
- Create: `docs/reference/page-run.md`
- Create: `tests/py/test_page_run.py`
- Modify: `scripts/workflow_ref_check.py:4-5` (docstring), `:13` (marker docstring), `:25-26` (`DOCS`, `MARKER`)
- Modify: `tests/py/test_workflow_ref_check.py:17` (import pytest), `:24-25` and `:39` (`tree()`), `:100` (three new tests), `:109` (file count)
- Modify: `CLAUDE.md:85` (routing paragraph after the page-type table), `:327` ("Where everything else went")
- Modify: `docs/reference/WORKFLOW.md:4` (pointer), `:430` (Sprint 3), `:513` (Sprint 4), `:696` (Sprint 6)
- Modify: `.claude/skills/bsuk-location-page-builder/SKILL.md:306` (Step 6 — gates)
- Modify: `.claude/skills/bsuk-comparison-page-builder/SKILL.md:163` (§10 Pass Gates)
- Modify: `.claude/skills/bsuk-blog-post/SKILL.md:105` (§5 Baked-in Gates)
- Modify: `.claude/skills/session-closer/SKILL.md:52` (Closing Sequence)
- Test: `tests/py/test_page_run.py`, `tests/py/test_workflow_ref_check.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/py/test_page_run.py` with exactly this content:

```python
"""`docs/reference/page-run.md` — the ordered per-page run for project 5 pages.

The page-build brief is a workflow run before every page: a target block, the research, the
plan, the Asset Gate, the build, the gates, the close. BlueStaffyUK had every part of it
spread over a dozen files and no single run. Project 5 walks that run for 30-odd pages, and
a run that lives across twelve files is the one that gets skipped on page 14.

These tests pin the SHAPE of the run rather than its prose: every brief step it must cover,
in order; a command and a failing gate on every row; exactly three approval stops; a builder,
route and profile per page type that the scripts actually accept; and the checker that
keeps every name in it real.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_audit  # noqa: E402
import final_page_audit  # noqa: E402
import workflow_ref_check as wrc  # noqa: E402

DOC = ROOT / "docs/reference/page-run.md"
HEADER = ("#", "Brief step", "BSUK command, skill or board block", "Deliverable",
          "Gate that fails", "Approval stop")
# The brief sections a page run walks through. §1 and §3 are standing law and the sprint list
# (CLAUDE.md, rules/, WORKFLOW.md); §2 is routing, whose session-open row opens the run; §23 is
# the deliverables list below the table; §24–§26 are the reference library, open flags and the
# web tool — none of them is a step of one page's run.
STEPS = [0, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
# Global plugin skills the user ruled mandatory on every project 5 page (2026-09-26), and the
# session-open skill the brief's routing names. Invoked by exactly these names.
HARDEN_SKILLS = ("impeccable:impeccable", "frontend-design:frontend-design")
VERIFY_SKILL = "superpowers:verification-before-completion"
PLAN_SKILL = "superpowers:writing-plans"
BUILDER_SKILLS = (".claude/skills/bsuk-location-page-builder/SKILL.md",
                  ".claude/skills/bsuk-comparison-page-builder/SKILL.md",
                  ".claude/skills/bsuk-blog-post/SKILL.md")
RUNNABLE = re.compile(r"npm run [\w:-]+|scripts/\w+\.py|\bbsuk-[a-z-]+|grill-me"
                      r"|session-closer|board block|block \d")
GATE = re.compile(r"npm run [\w:-]+|python3 scripts/\w+\.py|tests/py/test_\w+\.py"
                  r"|scripts/\w+\.py")


def _rows(text, header):
    """The body rows of the first markdown table whose header row is `header`."""
    lines = text.splitlines()
    want = "| " + " | ".join(header) + " |"
    start = lines.index(want)
    out = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        out.append([c.strip() for c in line.strip().strip("|").split("|")])
    return out


def _run_rows():
    return _rows(DOC.read_text(encoding="utf-8"), HEADER)


def _sections(cell):
    """§9–§10 -> [9, 10]; §0 Target Block -> [0]."""
    m = re.match(r"§(\d+)(?:\s*[–-]\s*§(\d+))?", cell)
    assert m, f"a Brief step cell must open with its § number: {cell!r}"
    lo = int(m.group(1))
    hi = int(m.group(2) or lo)
    return list(range(lo, hi + 1))


def test_the_run_table_exists_with_six_columns():
    rows = _run_rows()
    assert len(rows) >= 15, f"only {len(rows)} rows — the run table stopped parsing"
    bad = [r for r in rows if len(r) != len(HEADER) or not all(r)]
    assert bad == [], f"every row needs all six cells filled: {bad}"


def test_rows_are_numbered_one_to_n():
    assert [int(r[0]) for r in _run_rows()] == list(range(1, len(_run_rows()) + 1))


def test_the_run_opens_with_the_session_open_row():
    first = _run_rows()[0]
    assert first[1].startswith("§2 Session open"), first[1]
    assert "grill-me" in first[2] and f"`{PLAN_SKILL}`" in first[2], first[2]
    assert "builder skill" in first[2], first[2]


def test_every_brief_step_is_covered_in_brief_order():
    rows = _run_rows()
    seen = []
    for r in rows[1:]:
        seen += _sections(r[1])
    assert seen == sorted(seen), f"after the session opens, the run walks the brief out of order: {seen}"
    missing = sorted(set(STEPS) - set(seen) - set(_sections(rows[0][1])))
    assert missing == [], f"brief steps with no row in the run: {missing}"


def test_every_row_names_something_to_run():
    bad = [r[0] for r in _run_rows() if not RUNNABLE.search(r[2])]
    assert bad == [], f"rows whose command cell names no command, skill or board block: {bad}"


def test_every_row_names_the_gate_that_fails():
    bad = [r[0] for r in _run_rows() if not GATE.search(r[4])]
    assert bad == [], f"rows with no failing gate — a step nothing checks is optional: {bad}"


def test_exactly_three_approval_stops_in_order():
    stops = []
    for r in _run_rows():
        cell = r[5]
        m = re.match(r"STOP (\d)\b", cell)
        if m:
            stops.append(int(m.group(1)))
        else:
            assert cell.startswith(("none", "PREVIEW")), (
                f"row {r[0]}: a stop is 'none', 'PREVIEW' or 'STOP n': {cell!r}")
    assert stops == [1, 2, 3], (
        f"the run stops for the breeder exactly three times, in order (WORKFLOW.md): {stops}")


def test_the_two_harden_passes_are_named_mandatory_rows_that_preview_only_a_visual_change():
    preview = [r for r in _run_rows() if r[5].startswith("PREVIEW")]
    assert [r[1].split(" ")[0] for r in preview] == ["§18", "§18"], preview
    for row, skill in zip(preview, HARDEN_SKILLS):
        assert f"`{skill}`" in row[2], f"row {row[0]} does not invoke {skill} by name"
        assert "375 / 768 / 1280" in row[2] or "same three widths" in row[2], row[2]
        assert "painting browser" in row[2], row[2]
        assert "data/page-runs/<slug>.json" in row[3], row[3]
        assert "working rule 6" in row[5] and "palette never changes" in row[5], row[5]


def test_verification_before_completion_closes_the_gates_and_the_session():
    rows = [r for r in _run_rows() if f"`{VERIFY_SKILL}`" in r[2]]
    assert [r[1].split(" ")[0] for r in rows] == ["§19", "§22"], [r[1] for r in rows]
    gate_row = rows[0]
    assert "npm run -s check:all" in gate_row[2] and "npm run gate:page -- <slug>" in gate_row[2]
    assert "verification_before_completion" in gate_row[3], gate_row[3]


def test_the_three_stops_are_the_brief_the_board_and_the_asset_gate():
    cells = {int(re.match(r"STOP (\d)", r[5]).group(1)): r[5] for r in _run_rows()
             if r[5].startswith("STOP")}
    assert "brief" in cells[1] and "board" in cells[2] and "Asset Gate" in cells[3], cells


PAGE_TYPE_HEADER = ("Page type", "Builder skill", "`<route>`", "Final-audit and evidence profile",
                    "Rule packs to read")


def test_each_project_5_page_type_has_a_builder_a_route_and_a_real_profile():
    rows = _rows(DOC.read_text(encoding="utf-8"), PAGE_TYPE_HEADER)
    assert [r[0] for r in rows] == ["location", "comparison", "blog"]
    for page_type, skill, _route, profile, packs in rows:
        path = re.search(r"`([^`]+SKILL\.md)`", skill).group(1)
        assert (ROOT / path).is_file(), path
        name = profile.strip("`")
        assert name in final_page_audit.PROFILES, f"{page_type}: no final-audit profile {name!r}"
        assert name in evidence_audit.PAGE_TYPES, f"{page_type}: no evidence type {name!r}"
        for pack in (p.strip() for p in packs.split(",")):
            assert (ROOT / "rules" / f"{pack}.md").is_file(), f"{page_type}: no pack {pack}"


def test_the_location_route_is_the_one_the_audits_resolve():
    rows = _rows(DOC.read_text(encoding="utf-8"), PAGE_TYPE_HEADER)
    assert rows[0][2].startswith("`uk-locations/<slug>`")


def test_the_run_is_guarded_by_check_workflow():
    assert "docs/reference/page-run.md" in wrc.DOCS
    problems, examined = wrc.check(ROOT)
    page_run = [p for p in problems if p.startswith("page-run.md")]
    assert page_run == [], page_run
    assert examined > 50


def test_the_run_is_linked_from_claude_md_and_workflow():
    for doc in ("CLAUDE.md", "docs/reference/WORKFLOW.md"):
        text = (ROOT / doc).read_text(encoding="utf-8")
        assert "docs/reference/page-run.md" in text, f"{doc} does not point at the page run"


def test_the_mandatory_skills_are_routed_where_a_page_is_built_and_closed():
    """The user's rulings (2026-09-26): impeccable and frontend-design harden every project 5
    page, verification-before-completion precedes every done claim, and writing-plans opens
    the session. A skill named only in page-run.md is a skill a builder reading its own
    SKILL.md never meets, so each routing point names them too."""
    want = {
        "CLAUDE.md": HARDEN_SKILLS + (VERIFY_SKILL, PLAN_SKILL),
        "docs/reference/WORKFLOW.md": HARDEN_SKILLS + (VERIFY_SKILL,),
        ".claude/skills/session-closer/SKILL.md": (VERIFY_SKILL,),
    }
    for skill in BUILDER_SKILLS:
        want[skill] = HARDEN_SKILLS + (VERIFY_SKILL,)
    missing = [f"{doc}: {name}" for doc, names in want.items()
               for name in names
               if f"`{name}`" not in (ROOT / doc).read_text(encoding="utf-8")]
    assert missing == [], "a routing point does not name a mandatory skill:\n  " + "\n  ".join(missing)


def test_workflow_names_verification_at_the_gates_and_at_close():
    text = (ROOT / "docs/reference/WORKFLOW.md").read_text(encoding="utf-8")
    gates = text[text.index("## Sprint 4"):text.index("## Sprint 5")]
    close = text[text.index("## Sprint 6"):]
    assert f"`{VERIFY_SKILL}`" in gates and f"`{VERIFY_SKILL}`" in close
```

Edit `tests/py/test_workflow_ref_check.py`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/tests/py/test_workflow_ref_check.py b/tests/py/test_workflow_ref_check.py
index ddf1a9d..68e1444 100644
--- a/tests/py/test_workflow_ref_check.py
+++ b/tests/py/test_workflow_ref_check.py
@@ -15,14 +15,16 @@ import json
 import pathlib
 import sys
 
+import pytest
+
 ROOT = pathlib.Path(__file__).resolve().parents[2]
 sys.path.insert(0, str(ROOT / "scripts"))
 
 import workflow_ref_check as wrc  # noqa: E402
 
 
-def tree(tmp_path, workflow, quick_start="# Quick start\n"):
-    """A minimal repo: one agent, one skill, one script, two npm scripts, the two docs."""
+def tree(tmp_path, workflow, quick_start="# Quick start\n", page_run="# Page run\n"):
+    """A minimal repo: one agent, one skill, one script, two npm scripts, the three docs."""
     (tmp_path / ".claude/agents").mkdir(parents=True)
     (tmp_path / ".claude/agents/bsuk-real-agent.md").write_text("---\n---\n", encoding="utf-8")
     (tmp_path / ".claude/skills/bsuk-real-skill").mkdir(parents=True)
@@ -37,6 +39,7 @@ def tree(tmp_path, workflow, quick_start="# Quick start\n"):
     ref.mkdir(parents=True)
     (ref / "WORKFLOW.md").write_text(workflow, encoding="utf-8")
     (ref / "quick-start.md").write_text(quick_start, encoding="utf-8")
+    (ref / "page-run.md").write_text(page_run, encoding="utf-8")
     return tmp_path
 
 
@@ -98,6 +101,30 @@ def test_quick_start_is_checked_too(tmp_path):
     assert problems == ["quick-start.md:1  bsuk-angle-ghost"]
 
 
+def test_the_page_run_is_checked_too(tmp_path):
+    # docs/reference/page-run.md is the ordered per-page run: every row names a command, and
+    # a row naming a command that does not exist is the row that gets skipped on page 14.
+    root = tree(tmp_path, "# Workflow\n", page_run="| 1 | `npm run gate:ghost -- <slug>` |\n")
+    problems, _ = wrc.check(root)
+    assert problems == ["page-run.md:1  npm run gate:ghost"]
+
+
+def test_the_arrives_in_task_marker_excuses_the_line(tmp_path):
+    # The page run is written before two of the scripts it names (plan Tasks 25 and 26), and
+    # tests/py/test_claude_md.py already expires the same marker the moment its path exists.
+    root = tree(tmp_path, "# Workflow\n",
+                page_run="`python3 scripts/ghost.py` then `npm run gate:ghost` (arrives in Task 25)\n")
+    problems, examined = wrc.check(root)
+    assert problems == [] and examined == 2
+
+
+def test_a_missing_doc_is_an_error_not_a_silent_pass(tmp_path):
+    root = tree(tmp_path, "# Workflow\n")
+    (root / "docs/reference/page-run.md").unlink()
+    with pytest.raises(FileNotFoundError):
+        wrc.check(root)
+
+
 def test_main_exits_1_on_a_problem_and_0_when_clean(tmp_path, capsys):
     bad = tree(tmp_path / "bad", "bsuk-ghost-agent\n")
     assert wrc.main(bad) == 1
@@ -106,7 +133,7 @@ def test_main_exits_1_on_a_problem_and_0_when_clean(tmp_path, capsys):
 
     good = tree(tmp_path / "good", "bsuk-real-agent\n")
     assert wrc.main(good) == 0
-    assert "examined 1 references in 2 files; 0 problems" in capsys.readouterr().out
+    assert "examined 1 references in 3 files; 0 problems" in capsys.readouterr().out
 
 
 def test_a_name_with_an_underscore_is_read_whole(tmp_path):
```

- [ ] **Step 2: Run the tests to see them fail**

```bash
python3 -m pytest tests/py/test_page_run.py tests/py/test_workflow_ref_check.py -q
```

Expected: `20 failed, 11 passed`. All 16 tests in `test_page_run.py` fail — the table tests
with `FileNotFoundError: [Errno 2] No such file or directory: '.../docs/reference/page-run.md'`,
`test_the_run_is_guarded_by_check_workflow` on `assert "docs/reference/page-run.md" in wrc.DOCS`,
and the three routing tests on their own assertions (`CLAUDE.md does not point at the page run`,
`a routing point does not name a mandatory skill`) — and in
`test_workflow_ref_check.py` these four fail: `test_the_page_run_is_checked_too`,
`test_the_arrives_in_task_marker_excuses_the_line`, `test_a_missing_doc_is_an_error_not_a_silent_pass`
(`DID NOT RAISE <class 'FileNotFoundError'>`) and `test_main_exits_1_on_a_problem_and_0_when_clean`
(`in 2 files` vs `in 3 files`).

- [ ] **Step 3: Teach the checker the third doc and the arrival marker**

Edit `scripts/workflow_ref_check.py`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/scripts/workflow_ref_check.py b/scripts/workflow_ref_check.py
index 5a8b7c7..44b0eef 100644
--- a/scripts/workflow_ref_check.py
+++ b/scripts/workflow_ref_check.py
@@ -1,8 +1,8 @@
 #!/usr/bin/env python3
 """workflow_ref_check.py — the workflow docs may only name what exists.
 
-Reads docs/reference/WORKFLOW.md and docs/reference/quick-start.md and resolves, on every
-line (prose, tables and fenced blocks alike):
+Reads docs/reference/WORKFLOW.md, docs/reference/quick-start.md and docs/reference/page-run.md
+(the ordered per-page run) and resolves, on every line (prose, tables and fenced blocks alike):
 
   - every `bsuk-*` agent or skill name  -> .claude/agents/<name>.md or .claude/skills/<name>/
   - every `scripts/...` path            -> a file or directory on disk
@@ -10,7 +10,10 @@ line (prose, tables and fenced blocks alike):
 
 A line may name one that does not exist only when it carries a parenthesised
 "not ported" marker, e.g. `(not ported — deferred to project 6)` or
-`(not ported — source repo only)`. The phrase outside parentheses is prose, not a marker.
+`(not ported — source repo only)`, or an `(arrives in Task N)` marker for a script a later
+task of the running plan writes. The phrase outside parentheses is prose, not a marker. The
+arrival marker expires on its own: tests/py/test_claude_md.py fails on a line that still
+carries it once every backticked path on the line exists.
 A `bsuk-*` name inside a path (`.claude/skills/bsuk-x/SKILL.md`, `data/bsuk-ontology.json`)
 is a path, which tests/py/test_rules_index.py already guards, and is skipped here.
 
@@ -22,8 +25,9 @@ import re
 import sys
 
 ROOT = pathlib.Path(__file__).resolve().parent.parent
-DOCS = ("docs/reference/WORKFLOW.md", "docs/reference/quick-start.md")
-MARKER = re.compile(r"\([^()]*\bnot ported\b[^()]*\)")
+DOCS = ("docs/reference/WORKFLOW.md", "docs/reference/quick-start.md",
+        "docs/reference/page-run.md")
+MARKER = re.compile(r"\([^()]*\bnot ported\b[^()]*\)|\(arrives in Task \w+\)")
 AGENT = re.compile(r"(?<![\w./-])@?(bsuk-[a-z0-9_-]*[a-z0-9])(?![\w-])(?!\.\w|/)")
 SCRIPT = re.compile(r"(?<![\w./-])(scripts/[\w./-]+)")
 NPM = re.compile(r"\bnpm run (?:(?:-s|--silent) )?([\w:-]+)")
```

- [ ] **Step 4: Write the page run**

Create `docs/reference/page-run.md` with exactly this content:

```markdown
# The Per-Page Run — project 5

> **Read this before building any project 5 page:** a location page, a comparison page or a
> blog post. One page, one run, top to bottom. Every row names the command that does the
> step, what it leaves on disk, the gate that fails when the step is skipped, and whether the
> run stops there for the breeder.

This is the page-build brief the source repo runs before every page (its Universal Page Build
Brief, v2.0) laid out as BlueStaffyUK's own commands. The brief's sections are numbered §0 to
§26; the **Brief step** column keeps those numbers so a row can be traced back to the section
it comes from. The sprint model itself is `docs/reference/WORKFLOW.md`; this file is the order
in which one page walks through it. `npm run check:workflow` resolves every agent, skill,
script and npm script named here, so a row that names something that is not there fails the
gate rather than failing the run.

A skill written `plugin:name` (`impeccable:impeccable`, `frontend-design:frontend-design`,
`superpowers:writing-plans`, `superpowers:verification-before-completion`) is a global plugin
skill. Invoke it with the Skill tool by exactly that name; never paraphrase it and never skip
it (the user's rulings, 2026-09-26).

## Which builder, route and profile

`<slug>` is the page's bare key (its board is `data/boards/<slug>.json`); `<route>` is where it
is built (`dist/<route>/index.html`). The page audits take the route; the board scripts, the
page-run record and the gate runner (row 17) take the key.

| Page type | Builder skill | `<route>` | Final-audit and evidence profile | Rule packs to read |
|---|---|---|---|---|
| location | `.claude/skills/bsuk-location-page-builder/SKILL.md` | `uk-locations/<slug>` (the slug is the row in `data/locations.json`, never rewritten) | `location` | copy, links |
| comparison | `.claude/skills/bsuk-comparison-page-builder/SKILL.md` | the route the URL-family decision gives it | `comparison` | images, headings, copy |
| blog | `.claude/skills/bsuk-blog-post/SKILL.md` | `<slug>` (a post in `src/content/blog/` builds at `/<slug>/`) | `blog` | headings, images |

The URL-family decision for the city cluster and the comparison slugs is one table,
`docs/research/2026-09-26-url-family-decision.md` (arrives in Task 27). Read the page's row
before row 3.

## The run

Three rows stop for the breeder, and only three: the brief (stop 1), the board (stop 2) and
the Asset Gate (stop 3), as `docs/reference/WORKFLOW.md` sets for a session that runs with
the breeder away. The two Harden passes (rows 14 and 15) are mandatory on every project 5
page and pause only for a PREVIEW: when a pass proposes a visual change, it is previewed and
approved before it is applied. Everywhere else the Clarification Checkpoint applies
(`CLAUDE.md` working rule 7): write the finished part to disk, log the question, ask one
narrow question, keep building what is not blocked.

| # | Brief step | BSUK command, skill or board block | Deliverable | Gate that fails | Approval stop |
|---|---|---|---|---|---|
| 1 | §2 Session open | invoke `grill-me` (`--brief <path>` when the breeder is away), then the `superpowers:writing-plans` skill, then the page-type builder skill from the table above | the session brief (goal, scope, gates, done, out of scope) and this page's plan | `npm run check:workflow` (every agent, skill and script this run names exists) | none |
| 2 | §0 Target Block — the mode is found by looking | `scripts/page_intake.py` (arrives in Task 24): `python3 scripts/page_intake.py <slug>`; the same lines are block 0 of the board | the intake block: mode (stub, migrated, rebuilt or new), robots, built file and whether it is fresh, sitemap entry, verbatim count, empty `h1`, question file, LLM-intel file, board status, Search Console baseline with its barrier, inbound links, retired-term hits | `python3 scripts/page_intake.py <slug>` exits 2 on a slug no data file knows | none — the intake rides on the board and is approved at stop 2 |
| 3 | §4 URL, canonical and redirect decision | the page's row in the URL-family decision; a slug that moves gets its 301 in `data/redirects.json`, then `npm run redirects` | the slug, canonical and redirect rows the board records in `meta.slug` | `npm run check:redirects` (one hop, target built, nothing shadowed) | none — decided once for the cluster, on the answer board |
| 4 | §5 Research on hand, inventory before any fetch | `scripts/page_intake.py` (arrives in Task 24) lists what is banked for the slug; reuse it, and fetch through the spend guard only what is missing | an absent figure written `NOT FETCHED — <barrier>`, never bare and never guessed | `npm run check:barriers` (Task 21's barrier lint) and `npm run test:py` (the spend guard) | none |
| 5 | §6 Competitor research and query fan-out | `bsuk-query-augmentation` for the slug (top 5 on Google and Bing, merged); `python3 scripts/query_augment.py --extract-h2` on each saved page; `bsuk-reddit-threads` against the shared thread ledger; `bsuk-llm-keyword-intel` for the slug | `data/queries/<slug>.json` (competitors with their metrics, `section_target`, `extra_sections`, FAQ picks) and `docs/research/llm-intel/<slug>-<date>.json` | `npm run check:queries`, `npm run check:competitors`, `npm run check:gaps` | none |
| 6 | §7 Keyword deliverables and metrics | `python3 scripts/keyword_variants.py <slug>` for the four extra types; `scripts/keyword_metrics.py` for the ours-vs-top-5 table on the board | the section keywords in the record, and the metric table (unique terms, variations, exact match per tag, first 100 words, title front-load) | `keyword-variants-missing` in `scripts/family_rules.py`; the first-100-words and title front-load checks fail a new page | none |
| 7 | §8 Entities and co-occurrence | `python3 scripts/ontology_seed.py --check`; board block 5 groups the entities by class | every entity a section names, in `data/bsuk-ontology.json` with a source | `python3 scripts/ontology_seed.py --check`; a BLOCKED entity refuses approval | none |
| 8 | §9–§10 Gaps, angles and the strategy | the page's row in the approved cluster strategy (`docs/superpowers/sessions/2026-09-25-location-pages-strategy.md`); `grill-me --brief` for a page that strategy does not name; `bsuk-strategy-synthesizer` when a new strategy is needed | board block 1: goal, scope, gates, done, out of scope, strategy and why, the angles considered | `python3 scripts/strategy_cite_check.py <strategy.md>` on any new strategy | STOP 1 — the brief, only for a page with no row in the approved strategy |
| 9 | §11–§12 Distribution matrix and the H1–H6 outline | the record `data/boards/<slug>.json`, then `python3 scripts/build_page_board.py <slug>`: block 2 (H1 and meta), block 3 (outline, heading collisions, every link), block 3a (verbatim set), block 4 (distribution, why each section is here) | the approved outline: sections derived from the competitors' count + 3, grouped, each with its framework and `why_source` | `schemas/board.schema.json` through `scripts/pageboard.py`; `python3 scripts/board_approve.py <slug>` refuses a heading collision and any block 7b FAIL | none — approved with row 10 |
| 10 | §13–§14 Components, hero refresh and the tool decision | `python3 scripts/build_board_previews.py <slug>`, then the board: block 3c (navigation), block 5b (the kit), block 6 (three styles per section at 1280 / 768 / 375), block 7b (the project 5 rules) | the component tuple, the page's own hero and counter styles, a refresh delta on every section | `python3 scripts/board_approve.py <slug>`; `tests/py/test_rule16_gate.py` refuses a shared hero or counter | STOP 2 — the breeder approves the board, which carries rows 2 and 6–10 |
| 11 | §15 Images and the Asset Gate | `python3 scripts/image_candidates.py <slug> --write`; `python3 scripts/ingest_image.py folder`, `draft`, then `publish`; board block 7 on its second pass | an image on the hero and every body H2 and H3, each with its `assets[]` row and an approved file | `python3 scripts/board_gate.py <slug>` (also run for every rebuilt page by `npm run check:all`) | STOP 3 — the Asset Gate: a generated image is approved by its sha12 pick before it is published |
| 12 | §16 Build from the outline | for a page that exists: `python3 scripts/facts_preserved_check.py --extract <slug>` and `python3 scripts/verbatim_set_check.py --extract <slug>` FIRST; then the builder skill from the table above; `npm run build`; `python3 scripts/outline_provenance_check.py <slug>`; then add the slug to `data/facts/rebuilt.json` and the page to `tests/render/targets.json` | the built page in `dist/<route>/index.html`, written from its own outline and nothing else | `npm run check:all` (parity, facts, links, verbatim, outline, board gate, retired facts) | none |
| 13 | §17 Responsive typography, spacing and scroll | `npm run test:render:meta` first, then `npm run test:render:pages` (375 / 768 / 1280), which rebuilds the scorecards | `data/quality/scorecards/<slug>-<date>.json` with every check's examined count | `npm run test:render:pages`: a blocking IMG, LAYOUT or NAV row, or a check that examined zero nodes | none |
| 14 | §18 Harden — the `impeccable` pass | invoke the `impeccable:impeccable` skill on the built page at 375 / 768 / 1280, checked in a painting browser (Playwright or a real Chrome window, never a DOM-only read); commit its fixes; then `scripts/page_run_record.py` (arrives in Task 25): `python3 scripts/page_run_record.py <slug> impeccable --findings <n> --fixed <n>` | every finding fixed or deferred with its reason, and the `impeccable` key of `data/page-runs/<slug>.json` (date, widths, findings, fixed, deferred, commit) | `npm run gate:page -- <slug>` fails while the key is missing, a width is missing, a finding is neither fixed nor deferred, or the key's commit is older than the page's last source change | PREVIEW — only when it proposes a visual change: preview before apply (working rule 6); the palette never changes |
| 15 | §18 Harden — the `frontend-design` pass | then invoke the `frontend-design:frontend-design` skill the same way, at the same three widths, in a painting browser; commit its fixes; then `python3 scripts/page_run_record.py <slug> frontend-design --findings <n> --fixed <n>` with `scripts/page_run_record.py` (arrives in Task 25) | the `frontend_design` key of `data/page-runs/<slug>.json` | `npm run gate:page -- <slug>` fails on the same four conditions for this key | PREVIEW — only when it proposes a visual change: preview before apply (working rule 6); the palette never changes |
| 16 | §18 Harden — the static scan | `python3 scripts/page_hardening_scan.py <route> --fail-on-error` (the page, its template and data, and the kit) | 0 ERROR, every WARN triaged real, dead code or false positive | `python3 scripts/page_hardening_scan.py <route> --fail-on-error`, run twice more by the row 17 runner | none |
| 17 | §19 Gates, each run twice | `scripts/gate_page.py` (arrives in Task 25): `npm run gate:page -- <slug> --skip-record` runs dup (body and `--headers`), the final audit on the profile above, hardening, AEO and evidence, twice, and diffs the two runs; then `python3 scripts/quality_report.py` and `python3 scripts/perf_audit.py <route>` | `docs/reports/gate-page/<slug>.json` with both runs and their diff | `npm run gate:page -- <slug> --skip-record` exits 1 on any FAIL or any difference between the runs | none |
| 18 | §19 Verification before completion | invoke the `superpowers:verification-before-completion` skill before any "page done" or "ready for approval" claim; `scripts/page_run_record.py` (arrives in Task 25) runs and records the evidence: `python3 scripts/page_run_record.py <slug> verification --run "npm run -s check:all" --run "npm run gate:page -- <slug> --skip-record" --claim "<claim>"`; then `npm run gate:page -- <slug>` with the record | the `verification_before_completion` key of `data/page-runs/<slug>.json`: each command, its exit code and its examined count, and the claims it verified | `npm run gate:page -- <slug>` fails while the key is missing, a command exited non-zero, `check:all` or the gate run is not among the commands, or the key's commit is older than the page's last source change | none |
| 19 | §20 The measurement ledger | `scripts/measurement_ledger.py` (arrives in Task 26): `python3 scripts/measurement_ledger.py <project> --slugs <slug>` | M1–M3, M6, M8–M10, M12, M13 and M18 as numbers, pasted into the gate report | `python3 scripts/measurement_ledger.py` exits 1 when M1, M2, M8 or M10 fails | none |
| 20 | §21 LLM visibility | the page's LLM-intel file from row 5 (one engine, one query); `python3 scripts/aeo_audit.py <route> --fail-on-error`, also run twice by the row 17 runner | the fetched denominator (1 of 1, or `NOT FETCHED — <barrier>`), the answer structure, the engine terms the page lacks | `python3 scripts/aeo_audit.py <route> --fail-on-error` | none |
| 21 | §22 Deploy and close | `python3 scripts/rendered_changes.py --base <ref>`; the build's postbuild regenerates the sitemaps; invoke the `superpowers:verification-before-completion` skill again before the gate report says PASS; `session-closer`; the gate report published as an Artifact with its `.md`; commit on the project branch and never push | docs/reports/rendered-changes.json (the slugs whose built output changed: project 6's IndexNow list), the gate report, the Known Issues update | `npm run check:sitemaps` and `npm run check:all` | none — the live 200 and IndexNow wait for project 6 |

## What a finished page leaves on disk (§23)

Each item is a file, not a claim that the step was considered:

- `data/queries/<slug>.json` and `docs/research/llm-intel/<slug>-<date>.json` (Sprint 0)
- `data/boards/<slug>.json`, approved, and its board page under `docs/artifacts/boards/` (Sprint 1)
- every image slot's file and approved sha12 pick in the record's `assets[]` (Asset Gate)
- `dist/<route>/index.html`, the slug in `data/facts/rebuilt.json` and the page in
  `tests/render/targets.json` (Sprint 2)
- `data/page-runs/<slug>.json` with its `impeccable`, `frontend_design` and
  `verification_before_completion` keys (Sprints 3–4)
- the page's scorecard in `data/quality/scorecards/` (Sprints 3–4)
- `docs/reports/gate-page/<slug>.json` with two identical runs (Sprint 4)
- the ledger rows and docs/reports/rendered-changes.json in the project's gate report (close)

## Deliberate differences from the brief

Recorded and still correct: three stops instead of one per sprint; exactly two strategies; one
LLM engine per page, so the visibility denominator is 1, not 30; four counters, not eight; the
section count is the competitors' highest real count + 3, never a fixed number; no seam
dividers, so the seam-parity check has nothing to count; no push and no IndexNow until
project 6.
```

- [ ] **Step 5: Route the run and the mandatory skills where a page is built and closed**

Edit `CLAUDE.md` (a routing paragraph after the page-type table, a pointer in "Where everything else went"). The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/CLAUDE.md b/CLAUDE.md
index 608c99f..2bbda1e 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -83,6 +83,14 @@ capped at nine (`judgment_cap: 9`); a tenth exemption is a rule that has to earn
 | about / contact | `bsuk-contact-form`, `bsuk-trust-signals` | copy, links |
 | comparison | `bsuk-comparison-page-builder` | images, headings, copy |
 
+**Every project 5 page (location, comparison, blog) walks `docs/reference/page-run.md`.** The
+session opens with `grill-me`, then the `superpowers:writing-plans` skill, then the builder
+skill above. After the build, the Harden sprint invokes the `impeccable:impeccable` skill, then
+`frontend-design:frontend-design`, on the built page at 375 / 768 / 1280 in a painting browser,
+and `superpowers:verification-before-completion` runs before any "page done" claim and again
+before a gate report says PASS. Each is invoked with the Skill tool by that name, never
+paraphrased and never skipped (the user's rulings, 2026-09-26).
+
 The generic skills already ported live at `.claude/skills/` — `grill-me`,
 `section-auditor`, `internal-link-agent`, `keyword-cluster`, `anti-ai-writing` and the
 `framework-*` set among them. Each is one SKILL.md file in its own directory.
@@ -325,6 +333,8 @@ components are listed in `data/design/components.json`, and rebuilt pages render
 - `docs/reference/quick-start.md` — task → entry point, and the reference-doc index
 - `docs/reference/session-log.md` — build history and **Known Issues**
 - `docs/reference/WORKFLOW.md` — the sprint model
+- `docs/reference/page-run.md` — the ordered per-page run for a project 5 page: each brief
+  step, the command that does it, what it leaves on disk, the gate that fails and the stop
 - `docs/reference/seo-rules.md` — the numbered SEO rules, **57** of them in categories
   A–J. That is a different count from `data/quality/rule-index.json`'s 79 (of which 9 are
   `enforced: judgment`, capped there): the ledger indexes the `rules/` packs, the
```

Edit `docs/reference/WORKFLOW.md` (pointer at the top; the Harden passes in Sprint 3; verification in Sprint 4 and Sprint 6). The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

````diff
diff --git a/docs/reference/WORKFLOW.md b/docs/reference/WORKFLOW.md
index 4a5608d..39b21e8 100644
--- a/docs/reference/WORKFLOW.md
+++ b/docs/reference/WORKFLOW.md
@@ -2,6 +2,8 @@
 
 > **Read this before starting any new page, sprint, or monitoring cycle.**
 > This is the authoritative end-to-end sequence for every agent in `.claude/agents/`.
+> **Building one project 5 page?** Walk `docs/reference/page-run.md` top to bottom: it is this
+> pipeline as one ordered run per page, each row backed by a command and a gate.
 
 The 7-sprint model is domain-neutral and stands as written. What changed in the project 2
 re-base is the cast. The agent roster is whatever `data/agent-registry.json` lists —
@@ -428,6 +430,13 @@ moment Harden becomes a bullet, it becomes the bullet that gets skipped.*
 
 **REQUIRED SKILL:** `bsuk-page-hardening` (v2.0) · **REQUIRED FIRST:** `bsuk-gate-integrity`
 
+**REQUIRED ON EVERY PROJECT 5 PAGE (the user's ruling, 2026-09-26):** invoke the
+`impeccable:impeccable` skill, then the `frontend-design:frontend-design` skill, with the Skill
+tool (never paraphrased, never skipped) on the built page at 375 / 768 / 1280 in a painting
+browser. A pass that proposes a visual change is previewed before it is applied (working rule
+6); the palette never changes. Each pass is recorded in the page's run record
+(`docs/reference/page-run.md`, rows 14 and 15).
+
 ```
 0. npx astro build                      ← nothing below works on a stale dist/
 
@@ -511,6 +520,11 @@ python3 scripts/aeo_audit.py <slug>
 **REQUIRED SKILL:** `bsuk-final-page-pass` — THE final gate for EVERY page type,
 including the puppy `/available/` and for-sale pages the old interior gate excluded.
 
+**REQUIRED BEFORE ANY "PAGE DONE" CLAIM (the user's ruling, 2026-09-26):** invoke the
+`superpowers:verification-before-completion` skill with the Skill tool (never paraphrased,
+never skipped) at the end of this sprint, before a page is called done or ready for approval,
+and record what it ran in the page's run record (`docs/reference/page-run.md`, row 18).
+
 ```
 1. npx astro build
 2. python3 scripts/final_page_audit.py [--puppies]
@@ -694,6 +708,10 @@ bsuk-llm-keyword-intel <slug>
 *The step that makes the next page cheaper. Skipping it is why three of the 2026-07-28
 lessons never reached the skill that enforces them.*
 
+Before the gate report says PASS, invoke the `superpowers:verification-before-completion`
+skill again with the Skill tool (the user's ruling, 2026-09-26): every PASS in the report is a
+command run in this session, with its output read.
+
 ```
 1. session-closer skill        → fill the brief's What's Next
 2. Write the lessons doc       → a dated file under docs/superpowers/sessions/
````

Edit `.claude/skills/bsuk-location-page-builder/SKILL.md`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

````diff
diff --git a/.claude/skills/bsuk-location-page-builder/SKILL.md b/.claude/skills/bsuk-location-page-builder/SKILL.md
index 02600ef..83a05b1 100644
--- a/.claude/skills/bsuk-location-page-builder/SKILL.md
+++ b/.claude/skills/bsuk-location-page-builder/SKILL.md
@@ -304,6 +304,15 @@ the visible questions, no visible date. `scripts/query_coverage_check.py` holds
 
 ## Step 6 — gates
 
+**Mandatory on every project 5 page (the user's rulings, 2026-09-26).** After the build and
+before the audits, invoke the `impeccable:impeccable` skill, then the
+`frontend-design:frontend-design` skill, with the Skill tool (never paraphrased, never skipped),
+on the built page at 375 / 768 / 1280 in a painting browser; a pass that proposes a visual
+change is previewed before it is applied (working rule 6), and the palette never changes.
+Before any "page done" or "ready for approval" claim, invoke the
+`superpowers:verification-before-completion` skill. Each pass is recorded in the page's run
+record; the order is `docs/reference/page-run.md`, rows 14 to 18.
+
 Build first (`npm run build` — the gates measure `dist/`), then, in order:
 
 ```bash
````

Edit `.claude/skills/bsuk-comparison-page-builder/SKILL.md`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/.claude/skills/bsuk-comparison-page-builder/SKILL.md b/.claude/skills/bsuk-comparison-page-builder/SKILL.md
index f05e50a..fc25efb 100644
--- a/.claude/skills/bsuk-comparison-page-builder/SKILL.md
+++ b/.claude/skills/bsuk-comparison-page-builder/SKILL.md
@@ -161,6 +161,15 @@ After outline approval, give the hero and every body H2 and body H3 its image sl
 
 ## 10. Pass Gates (page is NOT done until ALL pass)
 
+**Mandatory on every project 5 page (the user's rulings, 2026-09-26).** After the build and
+before the audits, invoke the `impeccable:impeccable` skill, then the
+`frontend-design:frontend-design` skill, with the Skill tool (never paraphrased, never skipped),
+on the built page at 375 / 768 / 1280 in a painting browser; a pass that proposes a visual
+change is previewed before it is applied (working rule 6), and the palette never changes.
+Before any "page done" or "ready for approval" claim, invoke the
+`superpowers:verification-before-completion` skill. Each pass is recorded in the page's run
+record; the order is `docs/reference/page-run.md`, rows 14 to 18.
+
 `npx astro build` → verify in `dist/` → `python3 scripts/final_page_audit.py` → then the full breeder gate list: **SEO · AIO · GEO · AEO · entity coverage · topical authority · anti-AI · non-commodity · humor policy · keyword variation · keyword-verifier · technical SEO · Lighthouse (warm median-of-3)**. Preview before apply. Commit after every approved build — never push (no remote until project 6) — on the branch the plan names, never the trunk. Sitemaps regenerate after any page change.
 
 ## 11. Breeder-Review Component Standard (BINDING for every comparison page)
```

Edit `.claude/skills/bsuk-blog-post/SKILL.md`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/.claude/skills/bsuk-blog-post/SKILL.md b/.claude/skills/bsuk-blog-post/SKILL.md
index 5eae574..0e6d395 100644
--- a/.claude/skills/bsuk-blog-post/SKILL.md
+++ b/.claude/skills/bsuk-blog-post/SKILL.md
@@ -103,6 +103,15 @@ does not replace it.
 
 ### 5. Baked-in Gates (non-negotiable, every blog page)
 
+**Mandatory on every project 5 page (the user's rulings, 2026-09-26).** After the build and
+before the audits, invoke the `impeccable:impeccable` skill, then the
+`frontend-design:frontend-design` skill, with the Skill tool (never paraphrased, never skipped),
+on the built page at 375 / 768 / 1280 in a painting browser; a pass that proposes a visual
+change is previewed before it is applied (working rule 6), and the palette never changes.
+Before any "page done" or "ready for approval" claim, invoke the
+`superpowers:verification-before-completion` skill. Each pass is recorded in the page's run
+record; the order is `docs/reference/page-run.md`, rows 14 to 18.
+
 - **Heading Outline Gate** — present full H1→H6 outline (all six levels, sequential, ≥5 H5 AND ≥5 H6) + get explicit approval **BEFORE any page code**. No skipped levels. See `rules/headings.md` (`heading-hierarchy-outline-gate`); the rule moved out of CLAUDE.md on 2026-08-02. For a post, `scripts/final_page_audit.py` exempts the six-level outline, the ≥5 H5 / ≥5 H6 floor and the FAQPage check (`POST_EXEMPT_CHECKS`), so that floor is checked by hand at this gate.
 - **Line-icons not emoji** — Coat-style SVGs (`1em`, `currentColor`). Keep only ✔ ✗ ★ text glyphs. Never use 💡 ⚠ or any pictograph emoji.
 - **Delivery line on every card** — `UK home delivery by DEFRA-approved transport, priced by distance, £200–£350 · or collect in Carlisle`. Pull from `data/settings.json` (as §1 step 11) and `data/price-matrix.json`. No hardcoded figures.
```

Edit `.claude/skills/session-closer/SKILL.md`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/.claude/skills/session-closer/SKILL.md b/.claude/skills/session-closer/SKILL.md
index c96cc1a..775f7fd 100644
--- a/.claude/skills/session-closer/SKILL.md
+++ b/.claude/skills/session-closer/SKILL.md
@@ -50,6 +50,12 @@ Only after reading all five do you begin the closing process.
 
 ## Closing Sequence
 
+**Verify before you close (the user's ruling, 2026-09-26).** Before the session summary, the
+gate report or anything else says PASS, done or complete, invoke the
+`superpowers:verification-before-completion` skill with the Skill tool (never paraphrased,
+never skipped), run the commands it asks for, and read their output. A claim with no command
+behind it is not a PASS.
+
 ### Step 1 — Session Summary
 
 Tell the user what you found:
```

- [ ] **Step 6: Run the tests to see them pass**

```bash
python3 -m pytest tests/py/test_page_run.py tests/py/test_workflow_ref_check.py -q
```

Expected: `31 passed`.

```bash
python3 scripts/workflow_ref_check.py
```

Expected: `workflow-ref-check: examined <N> references in 3 files; 0 problems` (N was 302 on
the verification copy; it grows with the references earlier tasks added).

- [ ] **Step 7: Run the guards this task's text crosses, then check:all**

```bash
python3 -m pytest tests/py/test_claude_md.py tests/py/test_rules_index.py tests/py/test_agent_facts.py tests/py/test_marker_check.py tests/py/test_commit_trailer_examples.py tests/py/test_builder_skills.py tests/py/test_skills_frontmatter.py tests/py/test_system_gaps_wiring.py tests/py/test_agent_references.py -q
npm run -s check:all; echo "exit $?"
```

Expected: every test passes (1657 passed on the verification copy), and `check:all` ends with
`examined 41 agents; 0 problems` and `exit 0`.

- [ ] **Step 8: Commit**

```bash
git add docs/reference/page-run.md tests/py/test_page_run.py scripts/workflow_ref_check.py tests/py/test_workflow_ref_check.py CLAUDE.md docs/reference/WORKFLOW.md .claude/skills/bsuk-location-page-builder/SKILL.md .claude/skills/bsuk-comparison-page-builder/SKILL.md .claude/skills/bsuk-blog-post/SKILL.md .claude/skills/session-closer/SKILL.md
git commit -m "$(cat <<'EOF'
docs: page-run.md — the ordered per-page run, guarded by check:workflow

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```

### Task 24: Board intake block (auto-filled page state, robots, verbatim count, empty h1, question file, retired-term hits) + close KI 63

**Why.** The brief's target block (§0): the mode is found by looking, never assumed, and a
baseline is `NOT FETCHED` only with its barrier. The 28 cities start in different states —
7 stubs with no verbatim set (KI 79), 11 indexable bodies printing retired terms (KI 65),
9 rows with an empty `h1` (KI 59). `scripts/page_intake.py` reads each page's state from the
files and `build_page_board.py` renders it as block 0 of the board. Known Issue 63 is closed
in the same task because the intake reports freshness: `freshness_inputs()` now counts the
`[...]` route file that renders a city page.

**Assumptions.**
- Retired terms: the intake carries its own short list (`non-refundable`, `council-licensed`,
  and any £ amount not in the locked set it reads from `data/settings.json` and
  `data/puppies.json`, plus £0 — collection is free and the rebuilt homepage prints it). If
  Task 9 exported a shared pattern list from its retired-facts check, the implementer may
  import it instead; the tests below pin the behaviour either way.
- The Search Console baseline is read from the page's `data/page-map.json` row
  (`baseline_gsc`: `NOT FETCHED — GSC property unverified (domain expired); no exports on
  disk` on all 40 rows today); with no row it reports the `data/analytics/` state.
- Block 0 renders only when `render()` is given an intake (`main()` always passes one), so
  every existing `render()` test and every committed board HTML stays as it was.

**Files:**
- Create: `scripts/page_intake.py`
- Create: `tests/py/test_page_intake.py`
- Modify: `scripts/pageboard.py:1657` (`freshness_inputs()`, the KI 63 block)
- Modify: `scripts/build_page_board.py:24` (import), `:843` (`render()` signature), `:854` (block 0), `:1109` (`main()`)
- Modify: `docs/reference/page-run.md` rows 2 and 4 (drop the Task 24 markers)
- Modify: `docs/reference/session-log.md:1178` (Known Issue 63 → CLOSED)
- Modify: `docs/reference/system-registry.md` (regenerated)
- Test: `tests/py/test_page_intake.py`

- [ ] **Step 1: Write the failing test**

Create `tests/py/test_page_intake.py` with exactly this content:

```python
"""`scripts/page_intake.py` — block 0 of the board: a page's starting state, found by looking.

The page-build brief opens every page with a target block whose rule is that the mode is
determined by looking, never assumed. Project 5's 28 city pages start in different states —
stubs with no verbatim set (Known Issue 79), indexable bodies printing retired terms (Known
Issue 65), rows with an empty h1 (Known Issue 59) — and without an intake each builder derives
that again from nothing, 28 times.

The unit tests build a small tree in tmp_path so they pin behaviour, not today's data. The
last tests run the intake on this repo, and one closes Known Issue 63: a city page's built
file now reads as stale when the dynamic route that renders it changes.
"""
import json
import pathlib
import sys
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import build_page_board as BPB  # noqa: E402
import page_intake as PI  # noqa: E402
import pageboard as PB  # noqa: E402

LOCKED_SETTINGS = {"deposit_gbp": 500, "delivery_min_gbp": 200, "delivery_max_gbp": 350}
PUPPIES = [{"slug": "roman", "price_gbp": 1500}, {"slug": "vennie", "price_gbp": 1700}]


def page(body, robots="index, follow"):
    return (f'<html><head><meta name="robots" content="{robots}"></head><body>'
            f'<header><a href="/uk-locations/stubtown/">Stubtown</a></header>'
            f"<main>{body}</main></body></html>")


def repo(tmp_path):
    """Two cities (a noindex stub with an empty h1, an indexable migrated page), one rebuilt
    page, the data files the intake reads, and a built dist/ with a sitemap."""
    d = tmp_path / "data"
    for sub in ("facts", "verbatim", "boards", "queries"):
        (d / sub).mkdir(parents=True)
    (d / "locations.json").write_text(json.dumps([
        {"slug": "stubtown", "h1": "", "robots": "noindex, follow", "defects": ["empty-h1", "stub"],
         "body_html": ""},
        {"slug": "oldtown", "h1": "Blue Staffy Puppies Oldtown", "defects": [],
         "robots": "index, follow", "body_html": "<p>Delivery is a flat £100.</p>"},
    ]), encoding="utf-8")
    (d / "page-map.json").write_text(json.dumps({"pages": [
        {"url": "/uk-locations/stubtown/", "h1": "", "baseline_gsc": "NOT FETCHED — test barrier"},
        {"url": "/uk-locations/oldtown/", "h1": "Blue Staffy Puppies Oldtown",
         "baseline_gsc": "NOT FETCHED — test barrier"},
        {"url": "/done-page/", "h1": "Done", "baseline_gsc": "NOT FETCHED — test barrier"},
    ]}), encoding="utf-8")
    (d / "facts/rebuilt.json").write_text(json.dumps(["done-page"]), encoding="utf-8")
    (d / "verbatim/applies.json").write_text(json.dumps({"slugs": ["done-page"]}), encoding="utf-8")
    (d / "verbatim/done-page.json").write_text(json.dumps(
        {"h1": "Done", "headings": [{"text": "A"}, {"text": "B"}], "openings": [],
         "faq_questions": ["Q?"], "alts": []}), encoding="utf-8")
    (d / "settings.json").write_text(json.dumps(LOCKED_SETTINGS), encoding="utf-8")
    (d / "puppies.json").write_text(json.dumps(PUPPIES), encoding="utf-8")
    (d / "queries/oldtown.json").write_text("{}", encoding="utf-8")
    llm = tmp_path / "docs/research/llm-intel"
    llm.mkdir(parents=True)
    (llm / "oldtown-2026-09-25.json").write_text(json.dumps({"fetched": {"status": "ok"}}),
                                                 encoding="utf-8")
    dist = tmp_path / "dist"
    for route, html in {
        "uk-locations/stubtown": page("<p>Coming soon.</p>", robots="noindex, follow"),
        "uk-locations/oldtown": page("<p>Puppies £850 to £1,500. Delivery a flat £100. "
                                     "The deposit is non-refundable. We are council-licensed. "
                                     "Deposit £500.</p>"),
        "done-page": page('<p>See <a href="/uk-locations/oldtown/">Oldtown</a>.</p>'),
    }.items():
        (dist / route).mkdir(parents=True)
        (dist / route / "index.html").write_text(html, encoding="utf-8")
    (dist / "location-sitemap.xml").write_text(
        "<urlset><url><loc>https://x/uk-locations/oldtown/</loc></url></urlset>", encoding="utf-8")
    return tmp_path


def test_a_stub_city_reads_as_a_stub_with_its_empty_h1_and_no_verbatim_set(tmp_path):
    it = PI.intake("stubtown", repo(tmp_path))
    assert it["mode"] == "stub" and it["route"] == "uk-locations/stubtown"
    assert it["robots"] == "noindex, follow", "robots is read from the built page"
    assert it["h1"] == "EMPTY"
    assert it["verbatim"].startswith("stub — no verbatim set")
    assert it["sitemap"] is False and it["question_file"] is False and it["llm_intel"] is None
    assert it["page_type"] == "location"


def test_a_migrated_city_reports_its_retired_terms_sitemap_and_research(tmp_path):
    it = PI.intake("oldtown", repo(tmp_path))
    assert it["mode"] == "migrated" and it["sitemap"] is True
    assert it["retired"] == {"non-refundable": 1, "council-licensed": 1,
                             "£850 (not a locked amount)": 1, "£100 (not a locked amount)": 1}
    assert it["question_file"] is True
    assert it["llm_intel"] == {"file": "docs/research/llm-intel/oldtown-2026-09-25.json",
                               "status": "ok"}
    assert it["verbatim"].startswith("not extracted — run python3 scripts/verbatim_set_check.py")
    assert it["baseline"] == "NOT FETCHED — test barrier"


def test_inbound_links_count_other_pages_main_not_the_site_chrome(tmp_path):
    root = repo(tmp_path)
    # done-page links oldtown from its <main>; every page's header links stubtown.
    assert PI.intake("oldtown", root)["inbound_links"] == 1
    assert PI.intake("stubtown", root)["inbound_links"] == 0


def test_a_rebuilt_page_reads_as_rebuilt_with_its_verbatim_count(tmp_path):
    it = PI.intake("done-page", repo(tmp_path))
    assert it["mode"] == "rebuilt"
    assert it["verbatim"] == 4 and it["verbatim_applies"] is True
    assert it["built"]["path"] == "dist/done-page/index.html"


def test_a_page_known_only_by_its_board_is_new(tmp_path):
    root = repo(tmp_path)
    (root / "data/boards/fresh-compare.json").write_text(json.dumps(
        {"meta": {"slug": "fresh-compare", "page_type": "comparison", "status": "draft"},
         "h1": {"variants": ["Blue or Black"], "recommended": 0, "pick": None}}), encoding="utf-8")
    it = PI.intake("fresh-compare", root)
    assert it["mode"] == "new" and it["board"] == "draft" and it["built"] is None
    assert it["page_type"] == "comparison" and it["h1"] == "Blue or Black"
    assert it["verbatim"] == "none — a new page has no migrated wording"
    assert it["baseline"] == "NOT FETCHED — no Search Console export under data/analytics/"


def test_an_unknown_slug_is_refused(tmp_path):
    root = repo(tmp_path)
    with pytest.raises(PI.UnknownSlug):
        PI.intake("nowhere", root)
    with pytest.raises(PI.UnknownSlug):
        PI.intake("../etc", root)


def test_the_locked_amounts_come_from_the_data_files(tmp_path):
    assert PI.locked_amounts(repo(tmp_path)) == {"£0", "£200", "£350", "£500", "£1,500", "£1,700"}


def test_render_md_is_a_two_column_table_with_every_field(tmp_path):
    md = PI.render_md(PI.intake("oldtown", repo(tmp_path)))
    lines = md.splitlines()
    assert lines[:2] == ["| Field | Value |", "|---|---|"]
    for field in ("Mode", "Robots", "Built page", "Sitemap entry", "H1", "Verbatim set",
                  "Question file", "LLM intel", "Board", "Search Console baseline",
                  "Inbound links (other pages' main)", "Retired-term hits"):
        assert any(l.startswith(f"| {field} |") for l in lines), field


def test_main_exits_2_on_an_unknown_slug_and_0_on_a_known_one(capsys):
    assert PI.main(["no-such-page-anywhere"]) == 2
    assert "page-intake ERROR" in capsys.readouterr().out
    assert PI.main(["blue-staffy-puppies-manchester-uk", "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["mode"] in PI.MODES and out["route"] == "uk-locations/blue-staffy-puppies-manchester-uk"


# ── block 0 on the board ──────────────────────────────────────────────────────────────────

def test_the_board_renders_block_0_when_given_an_intake():
    board = PB.load_board("_demo")
    it = PI.intake("index")
    html = BPB.render(board, PB.load_ontology(), PB.load_ledger(), live={}, thumbs={},
                      slug="_demo", intake=it)
    assert 'data-title="0. Intake — found by looking"' in html
    assert "| Mode | rebuilt |" in html
    first = html.index('data-title="0. Intake')
    assert first < html.index('data-title="1. Brief"'), "block 0 comes before the brief"


def test_the_board_has_no_block_0_without_an_intake():
    html = BPB.render(PB.load_board("_demo"), PB.load_ontology(), PB.load_ledger(), live={},
                      thumbs={}, slug="_demo")
    assert "0. Intake" not in html


# ── this repo ─────────────────────────────────────────────────────────────────────────────

def test_every_city_row_has_an_intake_and_the_empty_h1s_are_counted():
    rows = json.loads((ROOT / "data/locations.json").read_text(encoding="utf-8"))
    intakes = [PI.intake(r["slug"]) for r in rows]
    assert {i["mode"] for i in intakes} <= set(PI.MODES)
    assert sum(i["h1"] == "EMPTY" for i in intakes) == sum(not r["h1"] for r in rows)


# ── Known Issue 63: a city page's freshness sees the template that renders it ──────────────

def test_a_city_page_is_stale_after_its_dynamic_route_changes(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "oldtown"}]),
                                                  encoding="utf-8")
    (tmp_path / "src/pages/uk-locations").mkdir(parents=True)
    template = tmp_path / "src/pages/uk-locations/[slug].astro"
    template.write_text("template", encoding="utf-8")
    built = tmp_path / "dist/uk-locations/oldtown/index.html"
    built.parent.mkdir(parents=True)
    time.sleep(0.01)
    built.write_text("x", encoding="utf-8")
    assert PB.dist_page_is_fresh(built, tmp_path, slug="oldtown")
    time.sleep(0.01)
    template.write_text("edited", encoding="utf-8")
    assert not PB.dist_page_is_fresh(built, tmp_path, slug="oldtown"), (
        "Known Issue 63: an edit to the dynamic route must make the city page stale")


def test_the_city_hub_page_is_not_one_of_its_sources(tmp_path):
    """Only the `[...]` route files render a city; the hub's own index.astro does not."""
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "oldtown"}]),
                                                  encoding="utf-8")
    (tmp_path / "src/pages/uk-locations").mkdir(parents=True)
    hub = tmp_path / "src/pages/uk-locations/index.astro"
    hub.write_text("hub", encoding="utf-8")
    built = tmp_path / "dist/uk-locations/oldtown/index.html"
    built.parent.mkdir(parents=True)
    time.sleep(0.01)
    built.write_text("x", encoding="utf-8")
    time.sleep(0.01)
    hub.write_text("edited", encoding="utf-8")
    assert PB.dist_page_is_fresh(built, tmp_path, slug="oldtown")
```

- [ ] **Step 2: Run it to see it fail**

```bash
python3 -m pytest tests/py/test_page_intake.py -q
```

Expected: `ERROR tests/py/test_page_intake.py` — `ModuleNotFoundError: No module named 'page_intake'`
(1 error during collection).

- [ ] **Step 3: Write the intake**

Create `scripts/page_intake.py` with exactly this content:

```python
#!/usr/bin/env python3
"""page_intake.py <slug> [--json] — a page's starting state, found by looking.

The page-build brief opens every page with a target block, and its rule is that the mode is
determined by looking, never assumed, and a baseline reads NOT FETCHED only with its barrier.
Project 5 starts its 28 city pages from different states: stubs with no verbatim set (Known
Issue 79), indexable bodies that print retired terms (Known Issue 65), rows with an empty h1
(Known Issue 59). This reads each page's state from the files, so no builder works it out
again from nothing, and scripts/build_page_board.py renders the same lines as block 0 of the
page's board.

Fields: mode (stub · migrated · rebuilt · new), robots (from the built page, else the data
row), the built file with its size and freshness, the sitemap entry, the verbatim set, the H1,
the question file, the LLM-intel file, the board's status, the Search Console baseline with
its barrier, inbound links from other pages' <main>, and retired-term hits in the page's
visible text.

Usage:
  python3 scripts/page_intake.py <slug>          # print the intake
  python3 scripts/page_intake.py <slug> --json   # print it as JSON

Exit 0 with the intake printed; 2 when the slug is malformed or no data file knows it (not in
data/locations.json, not in data/page-map.json, and no data/boards/<slug>.json).
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pageboard as PB  # noqa: E402
import verbatim_set_check as VSC  # noqa: E402
from _html import text_of  # noqa: E402
from _slugs import resolve_page  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]

MODES = ("stub", "migrated", "rebuilt", "new")
#: Wording the facts rules retired (Known Issue 65). A price, fee or deposit amount is judged
#: separately, against the amounts the data files hold today.
RETIRED_PHRASES = ("non-refundable", "council-licensed")
AMOUNT = re.compile(r"£\s?\d[\d,]*(?<!,)")
ROBOTS = re.compile(r"""<meta\s+name=["']robots["']\s+content=["']([^"']*)["']""", re.I)
MAIN = re.compile(r"<main\b[\s\S]*?</main>", re.I)
HREF = re.compile(r"""href=["']([^"'#?]+)""")
#: Built pages that are specimens of the kit, not pages a reader reaches.
SPECIMENS = ("board-preview", "kit-preview")


class UnknownSlug(Exception):
    pass


def _read_json(path, default):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def locked_amounts(root):
    """Every £ figure the data files stand behind today: the deposit, the delivery band and
    each puppy's price, spelled the way a page prints them (£1,500)."""
    settings = _read_json(root / "data/settings.json", {})
    puppies = _read_json(root / "data/puppies.json", [])
    nums = {settings.get("deposit_gbp"), settings.get("delivery_min_gbp"),
            settings.get("delivery_max_gbp")}
    nums |= {p.get("price_gbp") for p in puppies if isinstance(p, dict)}
    # £0 is collection from our home in Carlisle: free, and printed as a figure on the
    # rebuilt homepage's delivery tiles. It is a fact, not a retired amount.
    return {"£{:,}".format(n) for n in nums if isinstance(n, int)} | {"£0"}


def retired_hits(text, locked):
    """{term: count} for retired wording and for every £ amount outside the locked set."""
    hits = {}
    low = text.lower()
    for phrase in RETIRED_PHRASES:
        n = low.count(phrase)
        if n:
            hits[phrase] = n
    for m in AMOUNT.findall(text):
        amount = m.replace(" ", "")
        if amount not in locked:
            key = f"{amount} (not a locked amount)"
            hits[key] = hits.get(key, 0) + 1
    return hits


def _main_text(html):
    m = MAIN.search(html)
    return text_of(m.group(0) if m else html)


def inbound_links(route, dist):
    """How many OTHER built pages link to /<route>/ from inside their <main>. Site chrome (the
    header and the footer's city list) links every city from every page and says nothing about
    where equity points, so it is not counted."""
    target = "/" + route.strip("/") + "/"
    own = dist / route / "index.html"
    pages = 0
    for page in sorted(dist.rglob("index.html")):
        rel = page.relative_to(dist).as_posix()
        if page == own or rel.startswith(SPECIMENS):
            continue
        m = MAIN.search(page.read_text(encoding="utf-8", errors="ignore"))
        if m and any(re.sub(r"^https?://[^/]+", "", h).rstrip("/") + "/" == target
                     for h in HREF.findall(m.group(0))):
            pages += 1
    return pages


def intake(slug, root=None, dist=None):
    """The page's starting state as a dict. Raises UnknownSlug when no data file knows it."""
    root = pathlib.Path(root) if root is not None else ROOT
    dist = pathlib.Path(dist) if dist is not None else root / "dist"
    try:
        key, route = resolve_page(slug, root)
        board_file = root / "data/boards" / (PB.slug_file(key) + ".json")
    except (ValueError, PB.BoardError) as e:
        raise UnknownSlug(str(e))
    city = next((r for r in _read_json(root / "data/locations.json", [])
                 if isinstance(r, dict) and r.get("slug") == key), None)
    pm_rows = _read_json(root / "data/page-map.json", {}).get("pages", [])
    pm = next((r for r in pm_rows if isinstance(r, dict)
               and r.get("url", "").strip("/") == route), None)
    board = _read_json(board_file, None) if board_file.is_file() else None
    if city is None and pm is None and board is None:
        raise UnknownSlug(f"{slug}: not in data/locations.json, not in data/page-map.json, "
                          f"and no {board_file.relative_to(root)}")

    rebuilt = key in PB.rebuilt_slugs(root / "data/facts/rebuilt.json")
    if rebuilt:
        mode = "rebuilt"
    elif city is not None:
        mode = "stub" if "stub" in (city.get("defects") or []) else "migrated"
    elif pm is not None:
        mode = "migrated"
    else:
        mode = "new"

    built = dist / route / "index.html" if route else dist / "index.html"
    html = built.read_text(encoding="utf-8", errors="ignore") if built.is_file() else ""
    m = ROBOTS.search(html)
    if m:
        robots = m.group(1)
    elif city is not None:
        robots = city.get("robots") or "NOT FETCHED — the data row carries no robots value"
    else:
        robots = "NOT FETCHED — not built yet"

    if not dist.is_dir():
        sitemap = None
    else:
        loc = "/" + route + "/" if route else "/"
        sitemap = any(f"{loc}</loc>" in p.read_text(encoding="utf-8", errors="ignore")
                      for p in dist.glob("*.xml"))

    h1 = (city or pm or {}).get("h1")
    if board is not None and not h1:
        bh = board.get("h1") or {}
        pick = bh.get("pick") if bh.get("pick") is not None else bh.get("recommended")
        variants = bh.get("variants") or []
        if isinstance(pick, int) and 0 <= pick < len(variants):
            h1 = variants[pick]

    applies = _read_json(root / "data/verbatim/applies.json", {}).get("slugs", [])
    vfile = root / "data/verbatim" / f"{key}.json"
    if mode == "stub":
        verbatim = "stub — no verbatim set (Known Issue 79)"
    elif vfile.is_file():
        verbatim = len(VSC.elements(_read_json(vfile, {})))
    elif mode == "migrated":
        verbatim = (f"not extracted — run python3 scripts/verbatim_set_check.py --extract {key} "
                    "before any rewrite")
    else:
        verbatim = "none — a new page has no migrated wording"

    llm = sorted((root / "docs/research/llm-intel").glob(f"{key}-*.json"))
    llm_status = None
    if llm:
        llm_status = (_read_json(llm[-1], {}).get("fetched") or {}).get("status")

    if pm is not None and pm.get("baseline_gsc"):
        baseline = pm["baseline_gsc"]
    elif (root / "data/analytics").is_dir():
        baseline = "data/analytics/ exists — read it before writing NOT FETCHED"
    else:
        baseline = "NOT FETCHED — no Search Console export under data/analytics/"

    if html:
        text = _main_text(html)
    elif city is not None:
        text = text_of(city.get("body_html") or "")
    else:
        text = ""

    return {
        "slug": key,
        "route": route,
        "page_type": (board or {}).get("meta", {}).get("page_type") or (
            "location" if city is not None else None),
        "mode": mode,
        "robots": robots,
        "built": ({"path": built.relative_to(root).as_posix() if root in built.parents
                   else str(built), "bytes": built.stat().st_size,
                   "fresh": PB.dist_page_is_fresh(built, root, key)}
                  if built.is_file() else None),
        "sitemap": sitemap,
        "h1": h1 if h1 else "EMPTY",
        "verbatim": verbatim,
        "verbatim_applies": key in applies,
        "question_file": (root / "data/queries" / f"{key}.json").is_file(),
        "llm_intel": ({"file": llm[-1].relative_to(root).as_posix(), "status": llm_status}
                      if llm else None),
        "board": (board or {}).get("meta", {}).get("status") if board else None,
        "baseline": baseline,
        "inbound_links": inbound_links(route, dist) if dist.is_dir() and route else 0,
        "retired": retired_hits(text, locked_amounts(root)),
    }


def rows(it):
    """[(field, value)] in the order the board shows them."""
    built = it["built"]
    llm = it["llm_intel"]
    return [
        ("Mode", it["mode"]),
        ("Page type", it["page_type"] or "not recorded"),
        ("Route", "/" + it["route"] + "/" if it["route"] else "/"),
        ("Robots", it["robots"]),
        ("Built page", "not built" if built is None else
         "%s — %d bytes, %s" % (built["path"], built["bytes"],
                                "fresh" if built["fresh"] else "STALE: run npm run build")),
        ("Sitemap entry", "no dist/ to read" if it["sitemap"] is None else
         ("listed" if it["sitemap"] else "not listed")),
        ("H1", it["h1"]),
        ("Verbatim set", "%s element(s)" % it["verbatim"] if isinstance(it["verbatim"], int)
         else it["verbatim"]),
        ("Question file", "data/queries/%s.json" % it["slug"] if it["question_file"]
         else "none — run bsuk-query-augmentation"),
        ("LLM intel", "none — run bsuk-llm-keyword-intel" if llm is None else
         "%s (%s)" % (llm["file"], llm["status"])),
        ("Board", it["board"] or "none"),
        ("Search Console baseline", it["baseline"]),
        ("Inbound links (other pages' main)", str(it["inbound_links"])),
        ("Retired-term hits", ", ".join("%s × %d" % (k, n) for k, n in sorted(it["retired"].items()))
         or "none"),
    ]


def render_md(it):
    """The intake as a two-column markdown table, the form block 0 of the board shows."""
    esc = lambda v: str(v).replace("|", "\\|")
    lines = ["| Field | Value |", "|---|---|"]
    lines += ["| %s | %s |" % (esc(k), esc(v)) for k, v in rows(it)]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="page_intake.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--json", action="store_true", help="print the intake as JSON")
    ns = ap.parse_args(argv)
    try:
        it = intake(ns.slug)
    except UnknownSlug as e:
        print(f"page-intake ERROR {e}")
        return 2
    if ns.json:
        print(json.dumps(it, indent=2, ensure_ascii=False))
    else:
        print("intake for " + ("/" + it["route"] + "/" if it["route"] else "/"))
        for k, v in rows(it):
            print(f"  {k:<34} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Close Known Issue 63 in `freshness_inputs()`**

Edit `scripts/pageboard.py`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/scripts/pageboard.py b/scripts/pageboard.py
index 221a8ac..4793494 100644
--- a/scripts/pageboard.py
+++ b/scripts/pageboard.py
@@ -1655,6 +1655,19 @@ def freshness_inputs(root, slug=None):
             yield base
         elif base.is_dir():
             yield from (f for f in base.rglob("*") if f.is_file())
+    # Known Issue 63: a page whose route sits under a parent (a city page is built at
+    # uk-locations/<slug>) is rendered by the parent's dynamic route file, never by a
+    # src/pages/<slug>/ of its own. Every `[...]` file in the parent directory is one of its
+    # sources; the parent's own index.astro renders the hub, not this page.
+    try:
+        _, route = _resolve_page(slug, root)
+    except ValueError:
+        route = slug
+    if "/" in route:
+        parent = root / "src" / "pages" / route.rsplit("/", 1)[0]
+        if parent.is_dir():
+            yield from (f for f in sorted(parent.iterdir())
+                        if f.is_file() and f.name.startswith("["))
     for rel in FRESHNESS_SHARED:
         base = root / rel
         if base.exists():
```

- [ ] **Step 5: Render block 0 on the board**

Edit `scripts/build_page_board.py`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/scripts/build_page_board.py b/scripts/build_page_board.py
index 3d83827..41998a6 100644
--- a/scripts/build_page_board.py
+++ b/scripts/build_page_board.py
@@ -22,6 +22,7 @@ import link_diversity as LD
 import verbatim_set_check as VSC
 import image_rules as IR          # block 7's image pickers (system-gaps build, Task 10b)
 import board_entities as BE
+import page_intake as PI          # block 0, the intake (the brief's target block)
 from _kit_sections import find_sections, page_css, page_sprite, uses_sprite
 
 OUT = PB.ROOT / "docs" / "artifacts" / "boards"
@@ -840,7 +841,8 @@ def rules_block(findings):
     return RULES_CSS + f'<div class="rules">{"".join(rows)}</div>', refused
 
 
-def render(board, ont, ledger, live, thumbs, slug, previews=None, routes=None, nav=None, images=None):
+def render(board, ont, ledger, live, thumbs, slug, previews=None, routes=None, nav=None, images=None,
+           intake=None):
     previews = previews if previews is not None else {"css": "", "blocks": {}, "names": {}, "images": {}}
     nav = nav if nav is not None else {"css": "", "blocks": {}}
     routes = routes if routes is not None else load_routes()
@@ -852,6 +854,15 @@ def render(board, ont, ledger, live, thumbs, slug, previews=None, routes=None, n
     m = board["meta"]
     parts = []
 
+    # Block 0: the page's starting state, read from the files by scripts/page_intake.py —
+    # the brief's target block, where the mode is found by looking and never assumed. Only
+    # when the caller passes one, so a board rendered in a test stays exactly as it was.
+    if intake is not None:
+        parts.append(("0. Intake — found by looking", PI.render_md(intake)
+                      + "\n\nRead from `data/locations.json`, `data/page-map.json`, the record, "
+                        "the built page and its sitemap by `python3 scripts/page_intake.py "
+                      + esc(slug) + "`. Nothing here is typed by hand."))
+
     brief = board["brief"]
     parts.append(("1. Brief", "\n".join([
         f"**Goal.** {md(brief['goal'])}", f"**Scope.** {md(brief['scope'])}",
@@ -1106,7 +1117,12 @@ def main():
     routes = load_routes()
     # Candidates, thumbnails and generated previews only for the pages the image rule binds.
     images = IR.board_images(board) if PB.FR.applies(board) else None
-    out.write_text(render(board, ont, ledger, live, thumbs, slug, previews, routes, nav, images), encoding="utf-8")
+    try:
+        intake = PI.intake(slug)
+    except PI.UnknownSlug:
+        intake = None      # the demo record and a record-only page the data files never name
+    out.write_text(render(board, ont, ledger, live, thumbs, slug, previews, routes, nav, images,
+                          intake), encoding="utf-8")
     n_int = sum(len(s["links"]["internal"]) for s in board["sections"])
     n_ext = sum(len(s["links"]["external"]) for s in board["sections"])
     unresolved = sorted({l["href"] for s in board["sections"] for l in s["links"]["internal"]
```

- [ ] **Step 6: Run the test to see it pass**

```bash
python3 -m pytest tests/py/test_page_intake.py -q
```

Expected: `14 passed`.

- [ ] **Step 7: Drop the Task 24 markers from the page run and close the Known Issue**

`tests/py/test_claude_md.py::test_no_arrives_in_task_marker_is_stale` now fails on rows 2 and
4 of `docs/reference/page-run.md` (their only backticked path, `scripts/page_intake.py`,
exists). Apply:

Edit `docs/reference/page-run.md`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/docs/reference/page-run.md b/docs/reference/page-run.md
index 31b168d..9c13c79 100644
--- a/docs/reference/page-run.md
+++ b/docs/reference/page-run.md
@@ -47,9 +47,9 @@ narrow question, keep building what is not blocked.
 | # | Brief step | BSUK command, skill or board block | Deliverable | Gate that fails | Approval stop |
 |---|---|---|---|---|---|
 | 1 | §2 Session open | invoke `grill-me` (`--brief <path>` when the breeder is away), then the `superpowers:writing-plans` skill, then the page-type builder skill from the table above | the session brief (goal, scope, gates, done, out of scope) and this page's plan | `npm run check:workflow` (every agent, skill and script this run names exists) | none |
-| 2 | §0 Target Block — the mode is found by looking | `scripts/page_intake.py` (arrives in Task 24): `python3 scripts/page_intake.py <slug>`; the same lines are block 0 of the board | the intake block: mode (stub, migrated, rebuilt or new), robots, built file and whether it is fresh, sitemap entry, verbatim count, empty `h1`, question file, LLM-intel file, board status, Search Console baseline with its barrier, inbound links, retired-term hits | `python3 scripts/page_intake.py <slug>` exits 2 on a slug no data file knows | none — the intake rides on the board and is approved at stop 2 |
+| 2 | §0 Target Block — the mode is found by looking | `python3 scripts/page_intake.py <slug>`; the same lines are block 0 of the board | the intake block: mode (stub, migrated, rebuilt or new), robots, built file and whether it is fresh, sitemap entry, verbatim count, empty `h1`, question file, LLM-intel file, board status, Search Console baseline with its barrier, inbound links, retired-term hits | `python3 scripts/page_intake.py <slug>` exits 2 on a slug no data file knows | none — the intake rides on the board and is approved at stop 2 |
 | 3 | §4 URL, canonical and redirect decision | the page's row in the URL-family decision; a slug that moves gets its 301 in `data/redirects.json`, then `npm run redirects` | the slug, canonical and redirect rows the board records in `meta.slug` | `npm run check:redirects` (one hop, target built, nothing shadowed) | none — decided once for the cluster, on the answer board |
-| 4 | §5 Research on hand, inventory before any fetch | `scripts/page_intake.py` (arrives in Task 24) lists what is banked for the slug; reuse it, and fetch through the spend guard only what is missing | an absent figure written `NOT FETCHED — <barrier>`, never bare and never guessed | `npm run check:barriers` (Task 21's barrier lint) and `npm run test:py` (the spend guard) | none |
+| 4 | §5 Research on hand, inventory before any fetch | `python3 scripts/page_intake.py <slug>` lists what is banked for the slug; reuse it, and fetch through the spend guard only what is missing | an absent figure written `NOT FETCHED — <barrier>`, never bare and never guessed | `npm run check:barriers` (Task 21's barrier lint) and `npm run test:py` (the spend guard) | none |
 | 5 | §6 Competitor research and query fan-out | `bsuk-query-augmentation` for the slug (top 5 on Google and Bing, merged); `python3 scripts/query_augment.py --extract-h2` on each saved page; `bsuk-reddit-threads` against the shared thread ledger; `bsuk-llm-keyword-intel` for the slug | `data/queries/<slug>.json` (competitors with their metrics, `section_target`, `extra_sections`, FAQ picks) and `docs/research/llm-intel/<slug>-<date>.json` | `npm run check:queries`, `npm run check:competitors`, `npm run check:gaps` | none |
 | 6 | §7 Keyword deliverables and metrics | `python3 scripts/keyword_variants.py <slug>` for the four extra types; `scripts/keyword_metrics.py` for the ours-vs-top-5 table on the board | the section keywords in the record, and the metric table (unique terms, variations, exact match per tag, first 100 words, title front-load) | `keyword-variants-missing` in `scripts/family_rules.py`; the first-100-words and title front-load checks fail a new page | none |
 | 7 | §8 Entities and co-occurrence | `python3 scripts/ontology_seed.py --check`; board block 5 groups the entities by class | every entity a section names, in `data/bsuk-ontology.json` with a source | `python3 scripts/ontology_seed.py --check`; a BLOCKED entity refuses approval | none |
```

Edit `docs/reference/session-log.md`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/docs/reference/session-log.md b/docs/reference/session-log.md
index 147436d..954b6ee 100644
--- a/docs/reference/session-log.md
+++ b/docs/reference/session-log.md
@@ -1175,7 +1175,12 @@ numbers.
     page. The strategy's first comparison is the blue or black Staffy page; its slug, and whether a
     hub comes first, are the plan's.
 
-63. **Pageboard freshness does not see a city page's sources (project 5).** `freshness_inputs()` in
+63. **CLOSED (the brief-parity build, Task 24) — `freshness_inputs()` in `scripts/pageboard.py`
+    now counts every `[...]` route file in a nested page's parent directory, so an edit to
+    `src/pages/uk-locations/[slug].astro` makes a city page's built file read as stale; the page
+    intake (`scripts/page_intake.py`, block 0 of the board) reports that freshness, and
+    `tests/py/test_page_intake.py` holds both.** Was: **Pageboard freshness does not see a city
+    page's sources (project 5).** `freshness_inputs()` in
     `scripts/pageboard.py` measures a page against `src/pages/<slug>/`, its record, the shared shell
     and top-level `data/*.json`. A city page's markup comes from `src/pages/uk-locations/[slug].astro`,
     which is not `src/pages/<slug>`, so an edit there does not make its built page read as stale
```

Then regenerate the registry (it lists every script):

```bash
python3 scripts/build_system_registry.py
python3 scripts/build_system_registry.py --check
```

Expected: `wrote docs/reference/system-registry.md`, then
`examined docs/reference/system-registry.md; 0 problems`; the diff adds a list line for
`scripts/page_intake.py` and bumps the `## Scripts — N` count by one.

- [ ] **Step 8: Run the board suites, the doc guards and check:all**

```bash
python3 -m pytest tests/py/test_page_intake.py tests/py/test_board_previews.py tests/py/test_family_rules_on_board.py tests/py/test_page_board.py tests/py/test_anchor_types.py tests/py/test_board_entities.py tests/py/test_image_board_block.py tests/py/test_rule16_gate.py tests/py/test_page_run.py tests/py/test_claude_md.py tests/py/test_rules_index.py tests/py/test_agent_facts.py tests/py/test_system_registry.py -q
npm run -s check:all; echo "exit $?"
python3 scripts/page_intake.py blue-staffy-puppies-aberdeen
```

Expected: all pass; `check:all` exits 0; the Aberdeen intake prints `Mode  migrated`,
`Sitemap entry  listed` and a `Retired-term hits` line naming its unlocked £ amounts
(the KI 65 figures) — confirm them on the built page before quoting any.

- [ ] **Step 9: Commit**

```bash
git add scripts/page_intake.py tests/py/test_page_intake.py scripts/pageboard.py scripts/build_page_board.py docs/reference/page-run.md docs/reference/session-log.md docs/reference/system-registry.md
git commit -m "$(cat <<'EOF'
feat: board block 0 — the page intake, found by looking; close Known Issue 63

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```

### Task 25: npm run gate:page -- <slug> (dup body + --headers, final audit by profile, hardening, AEO, evidence, page-run record; --fail-on-error; runs twice, diffs) + run-twice rule in rules/gates.md

**Why.** One command per page instead of seven, and the brief's gate-integrity rule that one
clean run proves nothing: every step runs twice and a disagreement fails the page. The same
task enforces the user's two rulings of 2026-09-26 ("no test, no rule"): the per-page record
`data/page-runs/<slug>.json` holds the `impeccable`, `frontend_design` and
`verification_before_completion` passes, and `gate:page` fails the page until all three are
present, complete and newer than the page's last source change. Pages in
`BUILT_BEFORE_SYSTEM_GAPS` are exempt.

**Assumptions (CLIs as they exist today).**
- `dup_content_audit.py [--headers] --json PATH` is site-wide; its JSON is
  `{"mode","dist","pages","min_words","problems","findings":[{"a","b","words","run"} | {"kind","text","pages"}]}`.
  The runner judges only findings that name the page (its route key: `uk-locations/<slug>`
  for a city, `index` for the root) — a pair of two other pages is theirs.
- `final_page_audit.py <route> --type <profile> --fail-on-error --json PATH`,
  `aeo_audit.py <route> --fail-on-error --json PATH`,
  `evidence_audit.py <route> --type <profile> --fail-on-error --json PATH` and
  `page_hardening_scan.py <route> --fail-on-error --json PATH` all write
  `{"pages":[{"slug", ..., "checks"|"findings":[{"severity","message",...}]}]}`. The verdict of
  each step is its exit code; the problem count is the rows with severity FAIL/ERROR/WARN.
  **Task 15** widens what the hardening scan reads but not this CLI or JSON shape — if it
  changed either, adjust `argv_for()`/`judge()` to match and re-run Step 6.
- The profile is `--type`, else the board's `meta.page_type`, else `location` for a city; it
  must be in both `final_page_audit.PROFILES` and `evidence_audit.PAGE_TYPES`.
- The verification pass records `npm run gate:page -- <slug> --skip-record`, because the full
  gate (which checks the record) cannot pass before the record exists. The full
  `npm run gate:page -- <slug>` is then run after the record is committed.
- "The page's own sources" (for the record's freshness) are: `data/boards/<slug>.json`,
  `src/pages/<route>` (file or folder), the parent's `[...]` route files (a city's
  `src/pages/uk-locations/[slug].astro`) and a blog post's `src/content/blog/<slug>.md(x)`.
  The shared kit and `data/*.json` are deliberately excluded — an edit there would stale
  every page's record at once.
- The rule-index count goes from 79 to 80. If an earlier task of this plan already added a
  rule, write the count `python3 -c "import json;print(len(json.load(open('data/quality/rule-index.json'))['rules']))"`
  prints after Step 5 instead of 80 in both `CLAUDE.md` and `quick-start.md`.

**Files:**
- Create: `scripts/gate_page.py`
- Create: `scripts/page_run_record.py`
- Create: `schemas/page-run-record.schema.json`
- Create: `tests/py/fixtures/page-runs/known-broken.json`
- Create: `tests/py/test_gate_page.py`
- Create: `tests/py/test_page_run_record.py`
- Modify: `package.json:41` (`gate:page` entry)
- Modify: `rules/gates.md:83` (append `run-every-gate-twice`)
- Modify: `data/quality/rule-index.json:554` (one row)
- Modify: `CLAUDE.md:27` (the `gate:*` prefix), `:270` (per-page line), `:339` (rule count)
- Modify: `docs/reference/quick-start.md:111` (rule count)
- Modify: `docs/reference/page-run.md` rows 14, 15, 17, 18 (drop the Task 25 markers)
- Modify: `docs/reference/system-registry.md` (regenerated)
- Test: `tests/py/test_gate_page.py`, `tests/py/test_page_run_record.py`

- [ ] **Step 1: Write the failing tests and the known-broken fixture**

Create `tests/py/fixtures/page-runs/known-broken.json` with exactly this content:

```json
{
  "slug": "blue-staffy-puppies-oxford",
  "impeccable": {
    "ran_on": "2026-09-27",
    "widths": [375, 768],
    "findings": -1,
    "fixed": 0,
    "deferred": [],
    "commit": "not-a-sha"
  },
  "frontend_design": {
    "ran_on": "27/09/2026",
    "widths": [375, 768, 1280],
    "findings": 2,
    "fixed": 2,
    "deferred": [""],
    "commit": "0123456789abcdef0123456789abcdef01234567"
  },
  "verification_before_completion": {
    "ran_on": "2026-09-27",
    "commit": "0123456789abcdef0123456789abcdef01234567",
    "commands": [{"cmd": "npm run -s check:all", "exit": "0"}],
    "claims_verified": []
  }
}
```

Create `tests/py/test_page_run_record.py` with exactly this content:

```python
"""`scripts/page_run_record.py` + `schemas/page-run-record.schema.json` — the three passes
the user ruled mandatory on every project 5 page (2026-09-26): `impeccable:impeccable` and
`frontend-design:frontend-design` in Harden, `superpowers:verification-before-completion`
before any "page done" claim. No test, no rule: each pass leaves a key in
`data/page-runs/<slug>.json`, and `npm run gate:page -- <slug>` fails the page until all
three are there, complete and newer than the page's last source change.

The record tests run in a throwaway git repository in tmp_path, because freshness is a
question about commits. `tests/py/fixtures/page-runs/known-broken.json` is the record that
must never validate.
"""
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import page_run_record as PRR  # noqa: E402

BROKEN = ROOT / "tests/py/fixtures/page-runs/known-broken.json"
KEY = "newtown"


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def repo(tmp_path):
    """A git repo holding one city page: its row, its board record and the city route."""
    (tmp_path / "data/boards").mkdir(parents=True)
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": KEY}]), encoding="utf-8")
    (tmp_path / "data/boards" / f"{KEY}.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "src/pages/uk-locations").mkdir(parents=True)
    (tmp_path / "src/pages/uk-locations/[slug].astro").write_text("route\n", encoding="utf-8")
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@example.invalid")
    git(tmp_path, "config", "user.name", "t")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "page")
    return tmp_path


def full_record(root):
    PRR.write_pass(KEY, "impeccable", root, findings=2, fixed=1, deferred=["token change"])
    PRR.write_pass(KEY, "frontend-design", root, findings=0, fixed=0)
    PRR.write_pass(KEY, "verification", root,
                   run=["npm run -s check:all", f"npm run gate:page -- {KEY} --skip-record"],
                   claims=["the page passes every gate twice"])


def fake_npm(root, exit_code=0):
    """`npm run ...` answered by a script on PATH, so verification can run in a tmp repo."""
    bin_dir = root / "bin"
    bin_dir.mkdir(exist_ok=True)
    npm = bin_dir / "npm"
    npm.write_text(f"#!/bin/sh\necho 'examined 7 pages; 0 problems'\nexit {exit_code}\n",
                   encoding="utf-8")
    npm.chmod(0o755)
    return bin_dir


@pytest.fixture
def page(tmp_path, monkeypatch):
    root = repo(tmp_path)
    monkeypatch.setenv("PATH", str(fake_npm(root)) + ":" + os.environ["PATH"])
    return root


# ── the schema ────────────────────────────────────────────────────────────────────────────

def test_the_known_broken_record_breaks_the_schema_in_every_way_it_was_broken():
    errs = PRR.schema_errors(json.loads(BROKEN.read_text(encoding="utf-8")))
    joined = "\n".join(errs)
    for where in ("impeccable/widths", "impeccable/findings", "impeccable/commit",
                  "frontend_design/ran_on", "frontend_design/deferred/0",
                  "verification_before_completion/commands/0",
                  "verification_before_completion/claims_verified"):
        assert any(e.startswith(where) for e in errs), f"{where} not reported:\n{joined}"


def test_the_gate_reports_the_known_broken_record_as_a_schema_failure(tmp_path):
    root = repo(tmp_path)
    target = PRR.record_path(KEY, root)
    target.parent.mkdir(parents=True)
    broken = json.loads(BROKEN.read_text(encoding="utf-8"))
    broken["slug"] = KEY
    target.write_text(json.dumps(broken), encoding="utf-8")
    found = PRR.findings(KEY, root)
    assert found and all("breaks the schema" in f for f in found), found


def test_a_complete_record_written_by_the_writer_passes(page):
    full_record(page)
    assert PRR.findings(KEY, page) == []
    rec = PRR.load(KEY, page)
    assert rec["impeccable"]["widths"] == [375, 768, 1280]
    assert rec["verification_before_completion"]["commands"][0] == {
        "cmd": "npm run -s check:all", "exit": 0, "examined": 7}
    assert PRR.schema_errors(rec) == []


# ── what the gate fails on ────────────────────────────────────────────────────────────────

def test_no_record_fails(tmp_path):
    root = repo(tmp_path)
    assert PRR.findings(KEY, root) == [
        f"no data/page-runs/{KEY}.json — run the impeccable and frontend-design passes and "
        "verification-before-completion (docs/reference/page-run.md rows 14, 15, 18)"]


def test_a_missing_pass_fails(page):
    PRR.write_pass(KEY, "impeccable", page, findings=0, fixed=0)
    found = PRR.findings(KEY, page)
    assert any("the frontend_design pass is missing" in f for f in found), found
    assert any("the verification_before_completion pass is missing" in f for f in found), found


def test_a_finding_neither_fixed_nor_deferred_fails(page):
    full_record(page)
    rec = PRR.load(KEY, page)
    rec["impeccable"]["fixed"] = 0
    PRR.record_path(KEY, page).write_text(json.dumps(rec), encoding="utf-8")
    assert any("found 2 but fixed 0 and deferred 1" in f for f in PRR.findings(KEY, page))


def test_a_pass_older_than_the_last_source_change_fails(page):
    full_record(page)
    git(page, "add", "-A")
    git(page, "commit", "-qm", "record")
    (page / "src/pages/uk-locations/[slug].astro").write_text("changed\n", encoding="utf-8")
    git(page, "commit", "-qam", "template edit after the passes")
    found = PRR.findings(KEY, page)
    assert sum("older than the page's last source change" in f for f in found) == 3, found


def test_uncommitted_source_changes_fail(page):
    full_record(page)
    (page / "data/boards" / f"{KEY}.json").write_text('{"edited": true}\n', encoding="utf-8")
    assert any("uncommitted changes" in f for f in PRR.findings(KEY, page))


def test_verification_must_run_check_all_and_the_gate_and_pass_them(page, monkeypatch):
    PRR.write_pass(KEY, "impeccable", page, findings=0, fixed=0)
    PRR.write_pass(KEY, "frontend-design", page, findings=0, fixed=0)
    PRR.write_pass(KEY, "verification", page, run=["npm run -s check:placeholders"],
                   claims=["done"])
    found = PRR.findings(KEY, page)
    assert any("did not run `npm run -s check:all`" in f for f in found), found
    assert any(f"did not run `npm run gate:page -- {KEY}`" in f for f in found), found

    monkeypatch.setenv("PATH", str(fake_npm(page, exit_code=1)) + ":" + os.environ["PATH"])
    PRR.write_pass(KEY, "verification", page,
                   run=["npm run -s check:all", f"npm run gate:page -- {KEY}"], claims=["done"])
    found = PRR.findings(KEY, page)
    assert any("`npm run -s check:all` and it exited 1" in f for f in found), found


def test_the_twelve_pages_built_before_the_rule_are_exempt(tmp_path):
    root = repo(tmp_path)
    assert PRR.findings("privacy-policy-uk", root) == []


# ── the writer ────────────────────────────────────────────────────────────────────────────

def test_the_writer_refuses_while_the_sources_are_dirty(page):
    (page / "data/boards" / f"{KEY}.json").write_text('{"x": 1}\n', encoding="utf-8")
    with pytest.raises(PRR.RecordError, match="commit the page's sources first"):
        PRR.write_pass(KEY, "impeccable", page, findings=0, fixed=0)


def test_the_cli_writes_a_pass_and_checks_a_page(page, capsys):
    assert PRR.main([KEY, "impeccable", "--findings", "1", "--fixed", "1"], root=page) == 0
    assert "wrote data/page-runs/newtown.json — impeccable at" in capsys.readouterr().out
    assert PRR.main([KEY, "--check"], root=page) == 1
    assert "2 problem(s)" in capsys.readouterr().out


def test_the_page_sources_of_a_city_are_its_record_and_its_route_file(tmp_path):
    root = repo(tmp_path)
    assert PRR.page_sources(KEY, root) == [f"data/boards/{KEY}.json",
                                           "src/pages/uk-locations/[slug].astro"]
```

Create `tests/py/test_gate_page.py` with exactly this content:

```python
"""`scripts/gate_page.py` — `npm run gate:page -- <slug>`: every page gate, run twice, diffed.

The brief's gate-integrity rule: one clean run proves nothing, because the same input has
produced different verdicts. BlueStaffyUK ran its gates twice only at project close, by hand;
project 5 has ~30 pages, each its own gate target. This runner makes "twice" the default and a
disagreement a failure (rules/gates.md `run-every-gate-twice` is backed by this file).

The orchestration tests replace the audits with a scripted runner so they pin behaviour, not
today's pages. The last test runs the real audits twice on a real built page and asserts only
what must hold on any page: two runs, recorded, and identical.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import gate_page as GP  # noqa: E402

CLEAN = {
    "dup-body": (1, {"pages": 40, "findings": [{"a": "other", "b": "another", "words": 20, "run": "x"}]}),
    "dup-headers": (1, {"pages": 40, "findings": [{"kind": "exact", "text": "h", "pages": ["a", "b"]}]}),
    "final-audit": (0, {"pages": [{"slug": "p", "status": "PASS", "checks": []}]}),
    "hardening": (0, {"pages": [{"slug": "p/", "status": "OK", "checks": []}]}),
    "aeo": (0, {"pages": [{"slug": "p", "findings": []}], "errors": 0, "warns": 0}),
    "evidence": (0, {"pages": [{"slug": "p", "findings": []}], "errors": 0, "warns": 0}),
}


def scripted(overrides=None, second=None):
    """A runner answering from CLEAN, with per-step overrides, and different answers on the
    second call of a step when `second` names it."""
    calls = {}

    def runner(step, route, profile):
        calls[step] = calls.get(step, 0) + 1
        if second and step in second and calls[step] == 2:
            return second[step]
        return (overrides or {}).get(step, CLEAN[step])
    return runner


def run(runner, record=False):
    return GP.gate("p", "p", "location", runner=runner, record=record)


def test_a_clean_page_passes_both_runs():
    report = run(scripted())
    assert report["verdict"] == "PASS" and report["runs"] == 2 and report["identical"] is True
    assert [s["step"] for s in report["steps"]] == list(GP.AUDIT_STEPS)
    assert all(s["ok"] == [True, True] for s in report["steps"])


def test_the_site_wide_dup_audit_judges_only_findings_that_name_the_page():
    # The audit exits 1 on the pair (other, another); that pair is theirs, not this page's.
    report = run(scripted())
    dup = {s["step"]: s for s in report["steps"]}
    assert dup["dup-body"]["ok"] == [True, True] and dup["dup-headers"]["ok"] == [True, True]
    mine = {"dup-body": (1, {"pages": 40, "findings": [{"a": "p", "b": "x", "words": 14, "run": "r"}]}),
            "dup-headers": (1, {"pages": 40, "findings": [{"kind": "exact", "text": "t", "pages": ["p", "q"]}]})}
    report = run(scripted(mine))
    steps = {s["step"]: s for s in report["steps"]}
    assert steps["dup-body"]["problems"] == [1, 1] and steps["dup-headers"]["problems"] == [1, 1]
    assert report["verdict"] == "FAIL"


def test_a_failing_audit_fails_the_page():
    report = run(scripted({"aeo": (1, {"pages": [{"slug": "p", "findings": [
        {"severity": "WARN", "message": "no binomial"}]}], "errors": 0, "warns": 1})}))
    aeo = next(s for s in report["steps"] if s["step"] == "aeo")
    assert aeo["ok"] == [False, False] and aeo["problems"] == [1, 1] and aeo["identical"]
    assert report["verdict"] == "FAIL"


def test_a_step_that_answers_differently_the_second_time_fails_even_when_both_pass():
    flip = {"evidence": (0, {"pages": [{"slug": "p", "findings": []}], "errors": 0, "warns": 0,
                             "note": "a different answer"})}
    report = run(scripted(second=flip))
    ev = next(s for s in report["steps"] if s["step"] == "evidence")
    assert ev["ok"] == [True, True] and ev["identical"] is False
    assert report["verdict"] == "FAIL" and report["identical"] is False


def test_an_audit_that_writes_no_report_is_a_failure_not_a_pass():
    report = run(scripted({"hardening": (0, None)}))
    h = next(s for s in report["steps"] if s["step"] == "hardening")
    assert h["ok"] == [False, False]


def test_the_page_run_record_is_a_step_unless_skipped(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "p"}]), encoding="utf-8")
    report = GP.gate("p", "uk-locations/p", "location", runner=scripted(), record=True, root=tmp_path)
    rec = report["steps"][-1]
    assert rec["step"] == GP.RECORD_STEP and rec["ok"] == [False, False]
    assert report["verdict"] == "FAIL", "a page with no data/page-runs record never passes the full gate"
    assert GP.gate("p", "uk-locations/p", "location", runner=scripted(), record=False,
                   root=tmp_path)["verdict"] == "PASS"


def test_the_profile_must_be_one_both_audits_know():
    assert {"location", "comparison", "blog"} <= set(GP.PROFILES)


def test_an_unknown_slug_exits_2(capsys):
    assert GP.main(["no-such-page-anywhere"]) == 2
    assert "gate-page ERROR" in capsys.readouterr().out


def test_the_npm_script_runs_this_file():
    scripts = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
    assert scripts["gate:page"] == "python3 scripts/gate_page.py"
    assert "gate:page" not in scripts["check:all"], "a per-page gate is never chained into check:all"


def test_the_run_twice_rule_is_in_the_gates_pack_and_the_ledger():
    pack = (ROOT / "rules/gates.md").read_text(encoding="utf-8")
    assert "id: run-every-gate-twice" in pack
    rows = json.loads((ROOT / "data/quality/rule-index.json").read_text(encoding="utf-8"))["rules"]
    row = next(r for r in rows if r["id"] == "run-every-gate-twice")
    assert row == {"id": "run-every-gate-twice", "family": "GATE", "enforced": "test",
                   "test": "tests/py/test_gate_page.py", "pack": "rules/gates.md"}


@pytest.mark.skipif(not (ROOT / "dist/privacy-policy-uk/index.html").exists(),
                    reason="needs a built dist/ (npm run build)")
def test_the_real_audits_run_twice_on_a_built_page_and_agree(tmp_path):
    out = tmp_path / "report.json"
    code = GP.main(["privacy-policy-uk", "--json", str(out)])
    report = json.loads(out.read_text(encoding="utf-8"))
    assert code in (0, 1)
    assert report["runs"] == 2 and len(report["evidence"]) == 2
    assert [s["step"] for s in report["steps"]] == list(GP.AUDIT_STEPS) + [GP.RECORD_STEP]
    assert report["identical"] is True, [s for s in report["steps"] if not s["identical"]]
```

- [ ] **Step 2: Run them to see them fail**

```bash
python3 -m pytest tests/py/test_gate_page.py tests/py/test_page_run_record.py -q
```

Expected: `2 errors during collection` — `ModuleNotFoundError: No module named 'gate_page'`
and `ModuleNotFoundError: No module named 'page_run_record'`.

- [ ] **Step 3: Write the record's schema**

Create `schemas/page-run-record.schema.json` with exactly this content:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "BSUK per-page run record (data/page-runs/<slug>.json)",
  "description": "The mandatory skill passes of one project 5 page's run (docs/reference/page-run.md rows 14, 15 and 18): the impeccable and frontend-design Harden passes and verification-before-completion. Written by scripts/page_run_record.py; judged by scripts/gate_page.py. A key may be absent while the run is in progress; the gate fails until all three are present.",
  "type": "object",
  "required": ["slug"],
  "additionalProperties": false,
  "properties": {
    "slug": {"type": "string", "pattern": "^_?[a-z0-9-]+(/[a-z0-9-]+)*$"},
    "impeccable": {"$ref": "#/$defs/harden_pass"},
    "frontend_design": {"$ref": "#/$defs/harden_pass"},
    "verification_before_completion": {"$ref": "#/$defs/verification"}
  },
  "$defs": {
    "date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
    "sha": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
    "harden_pass": {
      "type": "object",
      "required": ["ran_on", "widths", "findings", "fixed", "deferred", "commit"],
      "additionalProperties": false,
      "properties": {
        "ran_on": {"$ref": "#/$defs/date"},
        "widths": {
          "type": "array",
          "items": {"enum": [375, 768, 1280]},
          "uniqueItems": true,
          "minItems": 3
        },
        "findings": {"type": "integer", "minimum": 0},
        "fixed": {"type": "integer", "minimum": 0},
        "deferred": {"type": "array", "items": {"type": "string", "minLength": 1}},
        "commit": {"$ref": "#/$defs/sha"}
      }
    },
    "verification": {
      "type": "object",
      "required": ["ran_on", "commit", "commands", "claims_verified"],
      "additionalProperties": false,
      "properties": {
        "ran_on": {"$ref": "#/$defs/date"},
        "commit": {"$ref": "#/$defs/sha"},
        "commands": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["cmd", "exit", "examined"],
            "additionalProperties": false,
            "properties": {
              "cmd": {"type": "string", "minLength": 1},
              "exit": {"type": "integer"},
              "examined": {"type": ["integer", "null"], "minimum": 0}
            }
          }
        },
        "claims_verified": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}}
      }
    }
  }
}
```

- [ ] **Step 4: Write the record writer and checker, then the runner**

Create `scripts/page_run_record.py` with exactly this content:

```python
#!/usr/bin/env python3
"""page_run_record.py — the record of a project 5 page's mandatory skill passes.

The user ruled (2026-09-26) that three skills are never skipped on a project 5 page: the
`impeccable:impeccable` and `frontend-design:frontend-design` Harden passes, and
`superpowers:verification-before-completion` before any "page done" claim
(docs/reference/page-run.md rows 14, 15 and 18). A ruling nothing checks is a paragraph, so
each pass leaves a key in `data/page-runs/<slug>.json` (schemas/page-run-record.schema.json)
and `npm run gate:page -- <slug>` fails the page until all three are there and current.

Write a pass (after committing the fixes it produced — the writer refuses while the page's
sources have uncommitted changes, because the record's commit would not contain them):

  python3 scripts/page_run_record.py <slug> impeccable --findings 7 --fixed 6 --deferred "why"
  python3 scripts/page_run_record.py <slug> frontend-design --findings 3 --fixed 3
  python3 scripts/page_run_record.py <slug> verification \\
      --run "npm run -s check:all" --run "npm run gate:page -- <slug> --skip-record" \\
      --claim "the page passes every gate twice"

`verification` RUNS each `--run` command itself and records its exit code and the first
`examined N` its output prints, so the record is evidence rather than a claim about evidence.

Check a page (what the gate reports):  python3 scripts/page_run_record.py <slug> --check

The gate fails a page when: the record is missing or breaks the schema; a pass is missing; a
Harden pass lacks one of 375 / 768 / 1280 or leaves a finding neither fixed nor deferred; a
verification command exited non-zero, or `npm run -s check:all` or the page's own
`npm run gate:page -- <slug>` run is not among its commands; a pass's commit is older than
the last commit that changed the page's own sources; or those sources have uncommitted
changes. The twelve pages built before these rules (scripts/family_rules.py
BUILT_BEFORE_SYSTEM_GAPS) are exempt.

Exit codes: 0 written / clean; 1 --check found problems; 2 bad invocation, dirty sources or
no git history to stamp.
"""
import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys

import jsonschema

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import family_rules as FR  # noqa: E402
from _slugs import resolve_page  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "page-run-record.schema.json"
WIDTHS = (375, 768, 1280)
HARDEN = {"impeccable": "impeccable", "frontend-design": "frontend_design"}
VERIFY = "verification_before_completion"
KEYS = ("impeccable", "frontend_design", VERIFY)
EXAMINED = re.compile(r"\bexamined (\d+)")
CHECK_ALL = re.compile(r"^npm run (?:-s |--silent )?check:all$")


class RecordError(Exception):
    pass


def record_path(key, root=ROOT):
    return pathlib.Path(root) / "data" / "page-runs" / (key.replace("/", "--") + ".json")


def page_sources(key, root=ROOT):
    """The files that are this page's own source, relative to root: its board record, its
    src/pages/<route> file or folder, the `[...]` route files of a nested page's parent (a
    city page is rendered by src/pages/uk-locations/[slug].astro — Known Issue 63) and a blog
    post's content file. The shared kit and data/*.json are deliberately not here: an edit
    to them would stale every page's record at once."""
    root = pathlib.Path(root)
    _, route = resolve_page(key, root)
    cands = [root / "data" / "boards" / (key.replace("/", "--") + ".json"),
             root / "src" / "pages" / route,
             root / "src" / "pages" / (route + ".astro"),
             root / "src" / "content" / "blog" / (key + ".md"),
             root / "src" / "content" / "blog" / (key + ".mdx")]
    if "/" in route:
        parent = root / "src" / "pages" / route.rsplit("/", 1)[0]
        if parent.is_dir():
            cands += [f for f in sorted(parent.iterdir()) if f.is_file() and f.name.startswith("[")]
    return [c.relative_to(root).as_posix() for c in cands if c.exists()]


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def head_commit(root=ROOT):
    p = _git(root, "rev-parse", "HEAD")
    if p.returncode != 0:
        raise RecordError("no git history to stamp the record with: " + p.stderr.strip())
    return p.stdout.strip()


def dirty_sources(key, root=ROOT):
    srcs = page_sources(key, root)
    if not srcs:
        return []
    p = _git(root, "status", "--porcelain", "--", *srcs)
    return [l[3:] for l in p.stdout.splitlines() if l.strip()]


def last_source_commit(key, root=ROOT):
    srcs = page_sources(key, root)
    if not srcs:
        return None
    p = _git(root, "log", "-1", "--format=%H", "--", *srcs)
    return p.stdout.strip() or None


def covers(record_commit, last, root=ROOT):
    """True when `last` (the newest commit touching the page's sources) is `record_commit`
    or one of its ancestors — the pass ran on a tree that already held that change."""
    if last is None:
        return True
    return _git(root, "merge-base", "--is-ancestor", last, record_commit).returncode == 0


def load(key, root=ROOT):
    p = record_path(key, root)
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def schema_errors(record, schema_path=SCHEMA):
    schema = json.loads(pathlib.Path(schema_path).read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    return sorted("%s: %s" % ("/".join(str(x) for x in e.absolute_path) or "(record)", e.message)
                  for e in v.iter_errors(record))


def findings(key, root=ROOT, schema_path=SCHEMA):
    """[message] — every reason the gate fails this page's record; [] means it passes."""
    root = pathlib.Path(root)
    if key in FR.BUILT_BEFORE_SYSTEM_GAPS:
        return []
    rel = record_path(key, root).relative_to(root).as_posix()
    record = load(key, root)
    if record is None:
        return [f"no {rel} — run the impeccable and frontend-design passes and "
                "verification-before-completion (docs/reference/page-run.md rows 14, 15, 18)"]
    out = [f"{rel} breaks the schema at {e}" for e in schema_errors(record, schema_path)]
    if out:
        return out
    last = last_source_commit(key, root)
    for name in KEYS:
        rec = record.get(name)
        if rec is None:
            out.append(f"{rel}: the {name} pass is missing")
            continue
        if not covers(rec["commit"], last, root):
            out.append(f"{rel}: the {name} pass ran at {rec['commit'][:12]}, older than the page's "
                       f"last source change {last[:12]} — run it again")
        if name != VERIFY:
            missing = [w for w in WIDTHS if w not in rec["widths"]]
            if missing:
                out.append(f"{rel}: the {name} pass did not check {missing}")
            if rec["fixed"] + len(rec["deferred"]) != rec["findings"]:
                out.append(f"{rel}: the {name} pass found {rec['findings']} but fixed "
                           f"{rec['fixed']} and deferred {len(rec['deferred'])} — every finding "
                           "is fixed or deferred with its reason")
            continue
        for c in rec["commands"]:
            if c["exit"] != 0:
                out.append(f"{rel}: verification ran `{c['cmd']}` and it exited {c['exit']}")
        cmds = [c["cmd"].strip() for c in rec["commands"]]
        if not any(CHECK_ALL.match(c) for c in cmds):
            out.append(f"{rel}: verification did not run `npm run -s check:all`")
        gate = re.compile(r"^npm run (?:-s |--silent )?gate:page -- " + re.escape(key) + r"(?:\s|$)")
        if not any(gate.match(c) for c in cmds):
            out.append(f"{rel}: verification did not run `npm run gate:page -- {key}`")
    dirty = dirty_sources(key, root)
    if dirty:
        out.append(f"{rel}: the page's sources have uncommitted changes the record cannot "
                   f"cover: {', '.join(dirty)}")
    return out


def run_command(cmd, root=ROOT):
    """{cmd, exit, examined} for one shell command run from the repo root."""
    p = subprocess.run(cmd, shell=True, cwd=str(root), capture_output=True, text=True)
    m = EXAMINED.search(p.stdout + "\n" + p.stderr)
    return {"cmd": cmd, "exit": p.returncode, "examined": int(m.group(1)) if m else None}


def write_pass(key, which, root=ROOT, today=None, **kw):
    """Add or replace one pass in the page's record and return the record."""
    root = pathlib.Path(root)
    dirty = dirty_sources(key, root)
    if dirty:
        raise RecordError("commit the page's sources first — uncommitted: " + ", ".join(dirty))
    commit = head_commit(root)
    ran_on = (today or datetime.date.today()).isoformat()
    record = load(key, root) or {"slug": key}
    if which in HARDEN:
        record[HARDEN[which]] = {"ran_on": ran_on, "widths": list(kw.get("widths") or WIDTHS),
                                 "findings": kw["findings"], "fixed": kw["fixed"],
                                 "deferred": list(kw.get("deferred") or []), "commit": commit}
    elif which == "verification":
        record[VERIFY] = {"ran_on": ran_on, "commit": commit,
                          "commands": [run_command(c, root) for c in kw["run"]],
                          "claims_verified": list(kw["claims"])}
    else:
        raise RecordError(f"unknown pass {which!r}")
    errs = schema_errors(record)
    if errs:
        raise RecordError("the record would break its schema: " + "; ".join(errs))
    p = record_path(key, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record


def main(argv=None, root=ROOT):
    ap = argparse.ArgumentParser(prog="page_run_record.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("slug")
    ap.add_argument("which", nargs="?", choices=sorted(HARDEN) + ["verification"])
    ap.add_argument("--check", action="store_true", help="print what the gate would report")
    ap.add_argument("--findings", type=int)
    ap.add_argument("--fixed", type=int)
    ap.add_argument("--deferred", action="append", default=[], metavar="REASON")
    ap.add_argument("--widths", type=int, nargs="+", default=list(WIDTHS))
    ap.add_argument("--run", action="append", default=[], metavar="CMD")
    ap.add_argument("--claim", action="append", default=[], metavar="TEXT")
    ns = ap.parse_args(argv)
    try:
        key, _ = resolve_page(ns.slug, root)
    except ValueError as e:
        print(f"page-run-record ERROR {e}")
        return 2
    if ns.check:
        probs = findings(key, root)
        for p in probs:
            print(f"  FAIL {p}")
        print(f"page-run-record: {key} — {len(probs)} problem(s)")
        return 1 if probs else 0
    if ns.which is None:
        ap.error("name a pass (impeccable, frontend-design, verification) or pass --check")
    if ns.which in HARDEN and (ns.findings is None or ns.fixed is None):
        ap.error(f"{ns.which} needs --findings and --fixed")
    if ns.which == "verification" and (not ns.run or not ns.claim):
        ap.error("verification needs at least one --run and one --claim")
    try:
        rec = write_pass(key, ns.which, root, findings=ns.findings, fixed=ns.fixed,
                         deferred=ns.deferred, widths=ns.widths, run=ns.run, claims=ns.claim)
    except RecordError as e:
        print(f"page-run-record ERROR {e}")
        return 2
    name = HARDEN.get(ns.which, VERIFY)
    print(f"wrote {record_path(key, root).relative_to(root)} — {name} at {rec[name]['commit'][:12]}")
    if name == VERIFY:
        for c in rec[name]["commands"]:
            print(f"  exit {c['exit']}  examined {c['examined']}  {c['cmd']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Create `scripts/gate_page.py` with exactly this content:

```python
#!/usr/bin/env python3
"""gate_page.py <slug> — every page gate for one page, run twice, the two runs diffed.

`npm run gate:page -- <slug>`. One command per page instead of seven, and the brief's rule
that one clean run proves nothing (rules/gates.md `run-every-gate-twice`): the same input has
produced different verdicts, so every step runs twice and a step that answers differently the
second time fails the page as surely as a step that fails.

Steps, in order, each with --fail-on-error where the audit takes it:
  dup-body          scripts/dup_content_audit.py over the whole built site; the page fails on
                    any duplicated passage that names it (a pair of two other pages is theirs)
  dup-headers       the same with --headers: any crossover heading that names the page
  final-audit       scripts/final_page_audit.py <route> --type <profile>
  hardening         scripts/page_hardening_scan.py <route>
  aeo               scripts/aeo_audit.py <route>
  evidence          scripts/evidence_audit.py <route> --type <profile>
  page-run-record   data/page-runs/<slug>.json holds the impeccable, frontend-design and
                    verification-before-completion passes, current (scripts/page_run_record.py)

`<slug>` is the page's key (a city's bare slug); the audits get its route (uk-locations/<slug>).
The profile is --type, else the board's meta.page_type, else `location` for a city.

  python3 scripts/gate_page.py <slug> [--type PROFILE] [--skip-record] [--json PATH]

--skip-record leaves out the page-run-record step. It is the form the verification pass runs
and records, because the full gate cannot pass before that record exists.
--json PATH moves the report from docs/reports/gate-page/<slug>.json.

Exit 0 when every step passes in both runs and the runs agree; 1 on any FAIL or any
difference; 2 on a bad invocation (a slug no data file knows, no built page, no profile).
"""
import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import evidence_audit  # noqa: E402
import final_page_audit  # noqa: E402
import page_intake as PI  # noqa: E402
import page_run_record as PRR  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORTS = ROOT / "docs" / "reports" / "gate-page"
RUNS = 2
PROFILES = sorted(set(final_page_audit.PROFILES) & set(evidence_audit.PAGE_TYPES))
AUDIT_STEPS = ("dup-body", "dup-headers", "final-audit", "hardening", "aeo", "evidence")
RECORD_STEP = "page-run-record"


def argv_for(step, route, profile, out):
    """The command a step runs, writing its JSON to `out`."""
    s = str(ROOT / "scripts") + "/"
    return {
        "dup-body": [s + "dup_content_audit.py", "--json", out],
        "dup-headers": [s + "dup_content_audit.py", "--headers", "--json", out],
        "final-audit": [s + "final_page_audit.py", route, "--type", profile,
                        "--fail-on-error", "--json", out],
        "hardening": [s + "page_hardening_scan.py", route, "--fail-on-error", "--json", out],
        "aeo": [s + "aeo_audit.py", route, "--fail-on-error", "--json", out],
        "evidence": [s + "evidence_audit.py", route, "--type", profile,
                     "--fail-on-error", "--json", out],
    }[step]


def run_audit(step, route, profile):
    """(exit code, JSON payload or None) for one audit step, run from the repo root."""
    with tempfile.TemporaryDirectory() as tmp:
        out = str(pathlib.Path(tmp) / "out.json")
        p = subprocess.run([sys.executable] + argv_for(step, route, profile, out),
                           cwd=str(ROOT), capture_output=True, text=True)
        try:
            payload = json.loads(pathlib.Path(out).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = None
    return p.returncode, payload


def judge(step, code, payload, page):
    """(ok, problems, evidence) — `evidence` is what the two runs are diffed on."""
    if payload is None:
        return False, 1, {"error": f"exit {code} and no JSON report"}
    if step == "dup-body":
        mine = sorted((f for f in payload.get("findings", []) if page in (f.get("a"), f.get("b"))),
                      key=lambda f: (f.get("a"), f.get("b"), f.get("run")))
        return not mine, len(mine), {"pages": payload.get("pages"), "findings": mine}
    if step == "dup-headers":
        mine = sorted((f for f in payload.get("findings", []) if page in f.get("pages", [])),
                      key=lambda f: (f.get("kind"), f.get("text")))
        return not mine, len(mine), {"pages": payload.get("pages"), "findings": mine}
    rows = [r for pg in payload.get("pages", []) for r in (pg.get("checks") or pg.get("findings") or [])]
    problems = sum(1 for r in rows if str(r.get("severity", "")).upper() in ("FAIL", "ERROR", "WARN"))
    return code == 0, problems, {"exit": code, "payload": payload}


def one_run(key, route, profile, runner, record, root):
    page = route or "index"
    steps = []
    for step in AUDIT_STEPS:
        code, payload = runner(step, route, profile)
        ok, problems, evidence = judge(step, code, payload, page)
        steps.append({"step": step, "ok": ok, "problems": problems, "evidence": evidence})
    if record:
        found = PRR.findings(key, root)
        steps.append({"step": RECORD_STEP, "ok": not found, "problems": len(found),
                      "evidence": {"findings": found}})
    return steps


def gate(key, route, profile, runs=RUNS, runner=run_audit, record=True, root=ROOT):
    """The report: both runs, per-step agreement, and the verdict."""
    all_runs = [one_run(key, route, profile, runner, record, root) for _ in range(runs)]
    steps = []
    for i, first in enumerate(all_runs[0]):
        mine = [r[i] for r in all_runs]
        same = all(json.dumps(m["evidence"], sort_keys=True) == json.dumps(first["evidence"], sort_keys=True)
                   and m["ok"] == first["ok"] for m in mine)
        steps.append({"step": first["step"], "ok": [m["ok"] for m in mine],
                      "problems": [m["problems"] for m in mine], "identical": same})
    verdict = "PASS" if all(all(s["ok"]) and s["identical"] for s in steps) else "FAIL"
    return {"slug": key, "route": route, "page_type": profile, "runs": runs,
            "record_checked": record, "steps": steps,
            "identical": all(s["identical"] for s in steps), "verdict": verdict,
            "evidence": [[{"step": s["step"], "evidence": s["evidence"]} for s in r] for r in all_runs]}


def resolve(slug, page_type=None, root=ROOT):
    """(key, route, profile) or raise PI.UnknownSlug / ValueError."""
    it = PI.intake(slug, root)
    profile = page_type or it["page_type"]
    if profile not in PROFILES:
        raise ValueError(f"no audit profile for {slug!r} (got {profile!r}); pass --type, one of "
                         + ", ".join(PROFILES))
    if it["built"] is None:
        raise ValueError(f"/{it['route']}/ is not built — run npm run build first")
    return it["slug"], it["route"], profile


def main(argv=None):
    ap = argparse.ArgumentParser(prog="gate_page.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("slug")
    ap.add_argument("--type", dest="page_type", choices=PROFILES)
    ap.add_argument("--skip-record", action="store_true",
                    help="leave out the page-run-record step (the form verification records)")
    ap.add_argument("--json", metavar="PATH", help="where to write the report")
    ns = ap.parse_args(argv)
    try:
        key, route, profile = resolve(ns.slug, ns.page_type)
    except (PI.UnknownSlug, ValueError) as e:
        print(f"gate-page ERROR {e}")
        return 2
    report = gate(key, route, profile, record=not ns.skip_record)
    out = pathlib.Path(ns.json) if ns.json else REPORTS / (key.replace("/", "--") + ".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"gate:page /{route}/ — profile {profile}, {RUNS} runs")
    for s in report["steps"]:
        state = "PASS" if all(s["ok"]) and s["identical"] else (
            "UNSTABLE" if not s["identical"] else "FAIL")
        print(f"  {state:<8} {s['step']:<16} problems per run {s['problems']}")
    print(f"{report['verdict']} — {len(report['steps'])} steps x {RUNS} runs; runs identical: "
          f"{report['identical']}; report {out}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Register the npm script and the run-twice rule**

Edit `package.json`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/package.json b/package.json
index a8dce9d..e40a189 100644
--- a/package.json
+++ b/package.json
@@ -39,6 +39,7 @@
     "audit:aeo": "python3 scripts/aeo_audit.py",
     "audit:evidence": "python3 scripts/evidence_audit.py --all",
     "audit:form": "python3 scripts/form_contract_audit.py",
+    "gate:page": "python3 scripts/gate_page.py",
     "test:perf": "python3 scripts/perf_audit.py",
     "test:perf:mobile": "python3 scripts/perf_audit.py --mobile",
     "sweep": "bash scripts/health-sweep.sh",
```

Edit `rules/gates.md`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/rules/gates.md b/rules/gates.md
index 3326a31..f302194 100644
--- a/rules/gates.md
+++ b/rules/gates.md
@@ -81,3 +81,12 @@ test: tests/py/test_quality_report.py
 ---
 
 - **No test, no rule — and an escaped defect is charged to the harness (ALWAYS) — applies to every agent, skill, and lesson** — A lesson becomes a rule **only** by this path: defect observed → failing test committed → fix applied → test passes → rule text written next to the test. **A rule with no backing test is a deletion candidate** — `python3 scripts/quality_report.py` §5 lists them every run and exits non-zero when a rule points at a check that no longer exists. The inverse matters more: **when a defect escapes, charge it to the harness, not to a new paragraph.** If an invariant already covered it and stayed quiet, the tool is broken — add the missed case to `tests/render/fixtures/known_broken/`, watch `npm run test:render:meta` fail, fix the check, and write no new rule. Measured twice: 2026-07-31 produced ten findings, **ten of them in the harness and zero in the pages**; 2026-08-01 collapsed a **418-row baseline to 85 with zero page edits**, because 337 NAV rows were counting granularity plus a check racing its own scroll animation — charging those to the pages would have produced a site-wide `src/styles/global.css` change to cure a defect that did not exist. CAG measured thirty-plus rules against a 24.8% rework rate; rule thirty-one does not move that number. Exempt: the capped nine `enforced: judgment` rules in `data/quality/rule-index.json`, each of which states why a test cannot exist. Procedure: `.claude/skills/bsuk-learning-loop/SKILL.md`. Enforced by `scripts/quality_report.py`, itself tested in `tests/py/test_quality_report.py` — the rule obeys its own constraint, or it would not be allowed in.
+
+---
+id: run-every-gate-twice
+enforced: test
+family: GATE
+test: tests/py/test_gate_page.py
+---
+
+- **Run every gate twice (ALWAYS) — applies to every project 5 page and every project close** — One clean run proves nothing: the same input has produced different verdicts. `npm run gate:page -- <slug>` runs every page gate — the duplicate audit on the body and on `--headers`, the final audit on the page's profile, the hardening scan, the AEO and evidence audits, and the page-run record (`data/page-runs/<slug>.json`: the `impeccable:impeccable`, `frontend-design:frontend-design` and `superpowers:verification-before-completion` passes) — twice, and diffs the runs. A step that fails in either run, or answers differently the second time, fails the page; the report is `docs/reports/gate-page/<slug>.json`. A PASS is still read for its examined count (`verify-the-gate-first`), and a project's gate report carries its own second run. Order and context: `docs/reference/page-run.md`.
```

Edit `data/quality/rule-index.json` (keep the file's one-space indent and ASCII escapes: the diff must add these seven lines and nothing else). The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/data/quality/rule-index.json b/data/quality/rule-index.json
index 455ee26..6780946 100644
--- a/data/quality/rule-index.json
+++ b/data/quality/rule-index.json
@@ -552,6 +552,13 @@
    "test": "tests/py/test_image_rules.py",
    "pack": "rules/images.md",
    "severity": "blocking"
+  },
+  {
+   "id": "run-every-gate-twice",
+   "family": "GATE",
+   "enforced": "test",
+   "test": "tests/py/test_gate_page.py",
+   "pack": "rules/gates.md"
   }
  ]
 }
```

Edit `CLAUDE.md`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/CLAUDE.md b/CLAUDE.md
index 2bbda1e..db01c5e 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -25,6 +25,9 @@ the traffic.
 `check:*` is a pass/fail gate (non-zero exit blocks the work), `audit:*` writes a report and
 is read by a human, `test:*` runs a test suite or a measurement harness. `npm run check:all`
 chains every gate; nothing else is chained, so an audit can never silently gate a commit.
+`gate:page` is the one per-page runner: `npm run gate:page -- <slug>` runs every page gate for
+one page twice and diffs the runs (`rules/gates.md` `run-every-gate-twice`); it is never
+chained into `check:all`.
 
 ## Deploy — inactive until project 6
 
@@ -268,6 +271,7 @@ green. `test:render:meta` is the gate that checks the checkers — run it **befo
 any page result. `test:render:pages` measures the target pages at 375/768/1280 in a real
 browser.
 
+Per page: `npm run gate:page -- <slug>` (every page gate, twice; `docs/reference/page-run.md`).
 Also: `python3 scripts/board_gate.py <slug>` · `python3 scripts/final_page_audit.py` ·
 `python3 scripts/page_hardening_scan.py` · `python3 scripts/dup_content_audit.py [--headers]` ·
 `python3 scripts/aeo_audit.py --all` · `python3 scripts/evidence_audit.py --all` ·
@@ -336,7 +340,7 @@ components are listed in `data/design/components.json`, and rebuilt pages render
 - `docs/reference/page-run.md` — the ordered per-page run for a project 5 page: each brief
   step, the command that does it, what it leaves on disk, the gate that fails and the stop
 - `docs/reference/seo-rules.md` — the numbered SEO rules, **57** of them in categories
-  A–J. That is a different count from `data/quality/rule-index.json`'s 79 (of which 9 are
+  A–J. That is a different count from `data/quality/rule-index.json`'s 80 (of which 9 are
   `enforced: judgment`, capped there): the ledger indexes the `rules/` packs, the
   render-harness checks and working rules 10–17; seo-rules.md numbers its own categories.
   `docs/reference/quick-start.md` states both, and all three files change together.
```

Edit `docs/reference/quick-start.md`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/docs/reference/quick-start.md b/docs/reference/quick-start.md
index e125c42..b0ecc1b 100644
--- a/docs/reference/quick-start.md
+++ b/docs/reference/quick-start.md
@@ -108,7 +108,7 @@ These eight are the whole set. The source repo's other reference docs were not p
 - `CLAUDE.md` — the session file: the locked facts, the rule-pack router, the seventeen
   working rules (1–9 are the nine judgment rules)
 - `rules/README.md` and the ten packs in `rules/` — the written rules
-- `data/quality/rule-index.json` — the machine-readable ledger: 79 rules, of which 9 are
+- `data/quality/rule-index.json` — the machine-readable ledger: 80 rules, of which 9 are
   `enforced: judgment` and capped there. This is a different count from seo-rules.md's 57
   and always will be: the ledger indexes the `rules/` packs, the render-harness checks and
   CLAUDE.md working rules 10–17; seo-rules.md numbers its own categories A–J.
```

- [ ] **Step 6: Run the tests to see them pass**

```bash
npm run build
python3 -m pytest tests/py/test_gate_page.py tests/py/test_page_run_record.py -q
```

Expected: `24 passed` (11 + 13). `test_the_real_audits_run_twice_on_a_built_page_and_agree`
runs the six real audits twice on `/privacy-policy-uk/` (about 16 s) and asserts two runs,
recorded and identical — it is skipped only when `dist/` is missing.

Then run it by hand on a city page to read the output shape:

```bash
npm run gate:page -- blue-staffy-puppies-oxford --skip-record; echo "exit $?"
```

Expected: `gate:page /uk-locations/blue-staffy-puppies-oxford/ — profile location, 2 runs`, six
step lines with the same problem count in both runs (the migrated Oxford body FAILs every
audit today — it is project 5's to rebuild), `runs identical: True`, and `exit 1`.
Delete `docs/reports/gate-page/` afterwards (it is gitignored, but keep the tree clean).

- [ ] **Step 7: Drop the Task 25 markers from the page run; regenerate the registry**

`tests/py/test_claude_md.py::test_no_arrives_in_task_marker_is_stale` now fails on rows 14,
15, 17 and 18. Apply:

Edit `docs/reference/page-run.md`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/docs/reference/page-run.md b/docs/reference/page-run.md
index 9c13c79..e687852 100644
--- a/docs/reference/page-run.md
+++ b/docs/reference/page-run.md
@@ -59,11 +59,11 @@ narrow question, keep building what is not blocked.
 | 11 | §15 Images and the Asset Gate | `python3 scripts/image_candidates.py <slug> --write`; `python3 scripts/ingest_image.py folder`, `draft`, then `publish`; board block 7 on its second pass | an image on the hero and every body H2 and H3, each with its `assets[]` row and an approved file | `python3 scripts/board_gate.py <slug>` (also run for every rebuilt page by `npm run check:all`) | STOP 3 — the Asset Gate: a generated image is approved by its sha12 pick before it is published |
 | 12 | §16 Build from the outline | for a page that exists: `python3 scripts/facts_preserved_check.py --extract <slug>` and `python3 scripts/verbatim_set_check.py --extract <slug>` FIRST; then the builder skill from the table above; `npm run build`; `python3 scripts/outline_provenance_check.py <slug>`; then add the slug to `data/facts/rebuilt.json` and the page to `tests/render/targets.json` | the built page in `dist/<route>/index.html`, written from its own outline and nothing else | `npm run check:all` (parity, facts, links, verbatim, outline, board gate, retired facts) | none |
 | 13 | §17 Responsive typography, spacing and scroll | `npm run test:render:meta` first, then `npm run test:render:pages` (375 / 768 / 1280), which rebuilds the scorecards | `data/quality/scorecards/<slug>-<date>.json` with every check's examined count | `npm run test:render:pages`: a blocking IMG, LAYOUT or NAV row, or a check that examined zero nodes | none |
-| 14 | §18 Harden — the `impeccable` pass | invoke the `impeccable:impeccable` skill on the built page at 375 / 768 / 1280, checked in a painting browser (Playwright or a real Chrome window, never a DOM-only read); commit its fixes; then `scripts/page_run_record.py` (arrives in Task 25): `python3 scripts/page_run_record.py <slug> impeccable --findings <n> --fixed <n>` | every finding fixed or deferred with its reason, and the `impeccable` key of `data/page-runs/<slug>.json` (date, widths, findings, fixed, deferred, commit) | `npm run gate:page -- <slug>` fails while the key is missing, a width is missing, a finding is neither fixed nor deferred, or the key's commit is older than the page's last source change | PREVIEW — only when it proposes a visual change: preview before apply (working rule 6); the palette never changes |
-| 15 | §18 Harden — the `frontend-design` pass | then invoke the `frontend-design:frontend-design` skill the same way, at the same three widths, in a painting browser; commit its fixes; then `python3 scripts/page_run_record.py <slug> frontend-design --findings <n> --fixed <n>` with `scripts/page_run_record.py` (arrives in Task 25) | the `frontend_design` key of `data/page-runs/<slug>.json` | `npm run gate:page -- <slug>` fails on the same four conditions for this key | PREVIEW — only when it proposes a visual change: preview before apply (working rule 6); the palette never changes |
+| 14 | §18 Harden — the `impeccable` pass | invoke the `impeccable:impeccable` skill on the built page at 375 / 768 / 1280, checked in a painting browser (Playwright or a real Chrome window, never a DOM-only read); commit its fixes; then `python3 scripts/page_run_record.py <slug> impeccable --findings <n> --fixed <n>` | every finding fixed or deferred with its reason, and the `impeccable` key of `data/page-runs/<slug>.json` (date, widths, findings, fixed, deferred, commit) | `npm run gate:page -- <slug>` fails while the key is missing, a width is missing, a finding is neither fixed nor deferred, or the key's commit is older than the page's last source change | PREVIEW — only when it proposes a visual change: preview before apply (working rule 6); the palette never changes |
+| 15 | §18 Harden — the `frontend-design` pass | then invoke the `frontend-design:frontend-design` skill the same way, at the same three widths, in a painting browser; commit its fixes; then `python3 scripts/page_run_record.py <slug> frontend-design --findings <n> --fixed <n>` | the `frontend_design` key of `data/page-runs/<slug>.json` | `npm run gate:page -- <slug>` fails on the same four conditions for this key | PREVIEW — only when it proposes a visual change: preview before apply (working rule 6); the palette never changes |
 | 16 | §18 Harden — the static scan | `python3 scripts/page_hardening_scan.py <route> --fail-on-error` (the page, its template and data, and the kit) | 0 ERROR, every WARN triaged real, dead code or false positive | `python3 scripts/page_hardening_scan.py <route> --fail-on-error`, run twice more by the row 17 runner | none |
-| 17 | §19 Gates, each run twice | `scripts/gate_page.py` (arrives in Task 25): `npm run gate:page -- <slug> --skip-record` runs dup (body and `--headers`), the final audit on the profile above, hardening, AEO and evidence, twice, and diffs the two runs; then `python3 scripts/quality_report.py` and `python3 scripts/perf_audit.py <route>` | `docs/reports/gate-page/<slug>.json` with both runs and their diff | `npm run gate:page -- <slug> --skip-record` exits 1 on any FAIL or any difference between the runs | none |
-| 18 | §19 Verification before completion | invoke the `superpowers:verification-before-completion` skill before any "page done" or "ready for approval" claim; `scripts/page_run_record.py` (arrives in Task 25) runs and records the evidence: `python3 scripts/page_run_record.py <slug> verification --run "npm run -s check:all" --run "npm run gate:page -- <slug> --skip-record" --claim "<claim>"`; then `npm run gate:page -- <slug>` with the record | the `verification_before_completion` key of `data/page-runs/<slug>.json`: each command, its exit code and its examined count, and the claims it verified | `npm run gate:page -- <slug>` fails while the key is missing, a command exited non-zero, `check:all` or the gate run is not among the commands, or the key's commit is older than the page's last source change | none |
+| 17 | §19 Gates, each run twice | `npm run gate:page -- <slug> --skip-record` runs dup (body and `--headers`), the final audit on the profile above, hardening, AEO and evidence, twice, and diffs the two runs; then `python3 scripts/quality_report.py` and `python3 scripts/perf_audit.py <route>` | `docs/reports/gate-page/<slug>.json` with both runs and their diff | `npm run gate:page -- <slug> --skip-record` exits 1 on any FAIL or any difference between the runs | none |
+| 18 | §19 Verification before completion | invoke the `superpowers:verification-before-completion` skill before any "page done" or "ready for approval" claim; the record writer runs and records the evidence: `python3 scripts/page_run_record.py <slug> verification --run "npm run -s check:all" --run "npm run gate:page -- <slug> --skip-record" --claim "<claim>"`; then `npm run gate:page -- <slug>` with the record | the `verification_before_completion` key of `data/page-runs/<slug>.json`: each command, its exit code and its examined count, and the claims it verified | `npm run gate:page -- <slug>` fails while the key is missing, a command exited non-zero, `check:all` or the gate run is not among the commands, or the key's commit is older than the page's last source change | none |
 | 19 | §20 The measurement ledger | `scripts/measurement_ledger.py` (arrives in Task 26): `python3 scripts/measurement_ledger.py <project> --slugs <slug>` | M1–M3, M6, M8–M10, M12, M13 and M18 as numbers, pasted into the gate report | `python3 scripts/measurement_ledger.py` exits 1 when M1, M2, M8 or M10 fails | none |
 | 20 | §21 LLM visibility | the page's LLM-intel file from row 5 (one engine, one query); `python3 scripts/aeo_audit.py <route> --fail-on-error`, also run twice by the row 17 runner | the fetched denominator (1 of 1, or `NOT FETCHED — <barrier>`), the answer structure, the engine terms the page lacks | `python3 scripts/aeo_audit.py <route> --fail-on-error` | none |
 | 21 | §22 Deploy and close | `python3 scripts/rendered_changes.py --base <ref>`; the build's postbuild regenerates the sitemaps; invoke the `superpowers:verification-before-completion` skill again before the gate report says PASS; `session-closer`; the gate report published as an Artifact with its `.md`; commit on the project branch and never push | docs/reports/rendered-changes.json (the slugs whose built output changed: project 6's IndexNow list), the gate report, the Known Issues update | `npm run check:sitemaps` and `npm run check:all` | none — the live 200 and IndexNow wait for project 6 |
```

```bash
python3 scripts/build_system_registry.py
python3 scripts/build_system_registry.py --check
```

Expected: `examined docs/reference/system-registry.md; 0 problems`; the diff adds
`scripts/gate_page.py`, `scripts/page_run_record.py` and `schemas/page-run-record.schema.json`.

- [ ] **Step 8: Run the guards and check:all**

```bash
python3 -m pytest tests/py/test_gate_page.py tests/py/test_page_run_record.py tests/py/test_page_run.py tests/py/test_page_intake.py tests/py/test_rules_index.py tests/py/test_quality_report.py tests/py/test_claude_md.py tests/py/test_package_scripts.py tests/py/test_system_registry.py tests/py/test_agent_facts.py tests/py/test_marker_check.py tests/py/test_workflow_ref_check.py -q
python3 scripts/quality_report.py > /dev/null; echo "quality $?"
npm run -s check:all; echo "exit $?"
```

Expected: all pass (773 on the verification copy), `quality 0`, `check:all` exit 0.

- [ ] **Step 9: Commit**

```bash
git add scripts/gate_page.py scripts/page_run_record.py schemas/page-run-record.schema.json tests/py/fixtures/page-runs/known-broken.json tests/py/test_gate_page.py tests/py/test_page_run_record.py package.json rules/gates.md data/quality/rule-index.json CLAUDE.md docs/reference/quick-start.md docs/reference/page-run.md docs/reference/system-registry.md
git commit -m "$(cat <<'EOF'
feat: npm run gate:page — every page gate twice, diffed, with the page-run record; run-twice rule

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```

### Task 26: scripts/measurement_ledger.py — JSON + markdown table of M1–M3, M6, M8–M10, M12, M13, M18

**Why.** The brief's §20: each measurement is a number reported at close, not a box ticked.
The data exists — scorecards, the checks' own declarations, `targets.json`, the rule index,
the rework ledger, the LLM-intel files, and (from Tasks 25 and 16) the gate:page reports and
`rendered-changes.json` — and nothing prints it together.

**Assumptions.**
- **Task 11** (read from `scripts/build_scorecard.mjs` today): scorecards are
  `data/quality/scorecards/<slug with / as __>-<YYYY-MM-DD>.json` carrying `slug`,
  `examined_by_check` and `details[].checkId`. Task 11 chains the builder after
  `test:render:pages` without changing that shape. M1/M3 read the newest date present
  (`render_baseline.dates_present`); severity comes from `render_baseline.load_checks()`.
- **Task 16**: `docs/reports/rendered-changes.json` = `{"base": <ref>, "head": <sha>, "changed": [slugs]}`
  (the contract). `docs/reports/**/*.json` is gitignored, so M13 reads the file on the machine
  that ran the close; absent → `NOT FETCHED — no docs/reports/rendered-changes.json (run python3 scripts/rendered_changes.py --base <ref>)`.
- **Task 25**: `docs/reports/gate-page/<slug>.json` with `runs`, `verdict`, `identical` and
  per-step `problems` — M8 and M10 read it.
- **Task 18** is not an input: none of the ten rows the contract fixes is a keyword metric
  (page-run row 6 names `scripts/keyword_metrics.py` for the board instead).
- M9 has no data until a rework window is recorded (`data/quality/rework-ledger.json` holds
  `"windows": []`), so it prints its barrier; M12's denominator is 1 per page (one engine,
  one query — a recorded, deliberate difference).
- Exit 1 when M1, M2, M6, M8 or M10 is FAIL. Rows whose scope is the project's pages read
  `EMPTY` while no project 5 page is in `data/facts/rebuilt.json`.

**Files:**
- Create: `scripts/measurement_ledger.py`
- Create: `tests/py/test_measurement_ledger.py`
- Modify: `docs/reference/page-run.md` row 19 (drop the Task 26 marker; name M6 among the failing rows)
- Modify: `docs/reference/system-registry.md` (regenerated)
- Test: `tests/py/test_measurement_ledger.py`

- [ ] **Step 1: Write the failing test**

Create `tests/py/test_measurement_ledger.py` with exactly this content:

```python
"""`scripts/measurement_ledger.py` — the brief's measurement ledger as numbers at close.

The brief lists eighteen measurements "that must appear in the close-out, not boxes that get
ticked". BlueStaffyUK held the data for most of them and printed none together. The unit tests
build a small tree in tmp_path — two checks, one scorecard run, two gate:page reports — so they
pin how each row is computed; the last test runs the ledger on this repo.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import measurement_ledger as ML  # noqa: E402

CHECKS_TS = """
register({ id: 'layout-min-font-size', family: 'LAYOUT', severity: 'blocking', describe: 'x' });
register({ id: 'sem-title-case', family: 'SEM', severity: 'advisory', describe: 'y' });
"""


def card(slug, examined, details=()):
    return {"slug": slug, "examined_by_check": examined,
            "details": [{"viewport": 375, "checkId": c, "count": 1, "message": "m"} for c in details]}


def gate_report(verdict="PASS", runs=2, identical=True, dup=(0, 0)):
    return {"runs": runs, "verdict": verdict, "identical": identical, "steps": [
        {"step": "dup-body", "ok": [True, True], "problems": [dup[0], dup[0]], "identical": True},
        {"step": "dup-headers", "ok": [True, True], "problems": [dup[1], dup[1]], "identical": True}]}


def tree(tmp_path, cards=None, reports=None, families=("LAYOUT", "SEM")):
    (tmp_path / "tests/render/checks").mkdir(parents=True)
    (tmp_path / "tests/render/checks/all.ts").write_text(CHECKS_TS, encoding="utf-8")
    (tmp_path / "tests/render/targets.json").write_text(json.dumps(
        {"families_by_page_type": {"location": list(families)}, "deferred_checks": {}}),
        encoding="utf-8")
    sc = tmp_path / "data/quality/scorecards"
    sc.mkdir(parents=True)
    for c in cards if cards is not None else [
            card("uk-locations/newtown", {"layout-min-font-size": 50, "sem-title-case": 4},
                 details=["sem-title-case"]),
            card("comp", {"layout-min-font-size": 30, "sem-title-case": 0})]:
        (sc / (c["slug"].replace("/", "__") + "-2026-09-27.json")).write_text(json.dumps(c),
                                                                             encoding="utf-8")
    (tmp_path / "data/quality/rule-index.json").write_text(json.dumps({"rules": [
        {"id": "a", "enforced": "test"}, {"id": "b", "enforced": "untested"}]}), encoding="utf-8")
    (tmp_path / "data/quality/rework-ledger.json").write_text(json.dumps({"windows": []}),
                                                              encoding="utf-8")
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "newtown"}]), encoding="utf-8")
    gp = tmp_path / "docs/reports/gate-page"
    gp.mkdir(parents=True)
    for key, rep in (reports if reports is not None else
                     {"newtown": gate_report(), "comp": gate_report()}).items():
        (gp / f"{key}.json").write_text(json.dumps(rep), encoding="utf-8")
    llm = tmp_path / "docs/research/llm-intel"
    llm.mkdir(parents=True)
    (llm / "newtown-2026-09-25.json").write_text(json.dumps({"fetched": {"status": "ok"}}),
                                                 encoding="utf-8")
    (tmp_path / "docs/reports/rendered-changes.json").write_text(json.dumps(
        {"base": "abc", "head": "0123456789abcdef", "changed": ["uk-locations/newtown", "comp"]}),
        encoding="utf-8")
    return tmp_path


def rows(led):
    return {r["id"]: r for r in led["rows"]}


def test_the_ledger_has_the_ten_rows_in_order(tmp_path):
    led = ML.ledger("p5", ["newtown", "comp"], tree(tmp_path))
    assert [r["id"] for r in led["rows"]] == ["M1", "M2", "M3", "M6", "M8", "M9", "M10", "M12",
                                              "M13", "M18"]
    assert led["scope"] == ["newtown", "comp"] and led["failed"] == []


def test_every_row_is_a_number_or_a_named_barrier(tmp_path):
    r = rows(ML.ledger("p5", ["newtown", "comp"], tree(tmp_path)))
    assert r["M1"]["value"] == "2 checks, 0 at zero (run 2026-09-27, 2 pages)"
    assert r["M2"]["value"] == "registered 2 · wired 2 · difference ∅"
    assert r["M3"]["value"] == "blocking 0 · advisory 1 (run 2026-09-27; never summed)"
    assert r["M6"]["value"] == "2 of 2 pages clean (run 2026-09-27)" and r["M6"]["status"] == "PASS"
    assert r["M8"]["value"] == "2 of 2 pages: >= 2 runs, both clean"
    assert r["M9"]["value"].startswith("NOT FETCHED — ")
    assert r["M10"]["value"] == "body 0 · headers 0 across 2 pages"
    assert r["M12"]["value"] == "1 / 2 (one engine, one query per page)"
    assert r["M12"]["detail"] == "comp: no llm-intel file"
    assert r["M13"]["value"] == "2 (base abc → head 0123456789ab)"
    assert r["M18"]["value"] == "1 of 2 rules" and r["M18"]["detail"] == "b"


def test_a_check_that_examined_zero_nodes_fails_m1(tmp_path):
    root = tree(tmp_path, cards=[card("comp", {"layout-min-font-size": 3, "sem-title-case": 0})])
    r = rows(ML.ledger("p5", ["comp"], root))
    assert r["M1"]["status"] == "FAIL" and r["M1"]["detail"] == "sem-title-case"
    assert "M1" in ML.ledger("p5", ["comp"], root)["failed"]


def test_a_family_registered_but_not_wired_fails_m2(tmp_path):
    r = rows(ML.ledger("p5", ["comp"], tree(tmp_path, families=("LAYOUT",))))
    assert r["M2"]["status"] == "FAIL" and r["M2"]["value"].endswith("difference {SEM}")


def test_a_page_with_small_text_fails_m6(tmp_path):
    root = tree(tmp_path, cards=[card("comp", {"layout-min-font-size": 3, "sem-title-case": 1},
                                      details=["layout-min-font-size"])])
    r = rows(ML.ledger("p5", ["comp"], root))
    assert r["M6"]["status"] == "FAIL" and r["M6"]["detail"] == "comp"


def test_a_gate_run_once_or_unstable_fails_m8_and_a_crossover_fails_m10(tmp_path):
    root = tree(tmp_path, reports={"newtown": gate_report(runs=1),
                                   "comp": gate_report(verdict="FAIL", identical=False, dup=(2, 1))})
    r = rows(ML.ledger("p5", ["newtown", "comp"], root))
    assert r["M8"]["status"] == "FAIL" and "newtown: 1 runs" in r["M8"]["detail"]
    assert r["M10"]["status"] == "FAIL" and r["M10"]["value"] == "body 2 · headers 1 across 2 pages"


def test_a_page_with_no_gate_report_fails_m8_and_m10(tmp_path):
    r = rows(ML.ledger("p5", ["newtown", "comp"], tree(tmp_path, reports={"comp": gate_report()})))
    assert r["M8"]["status"] == "FAIL" and r["M10"]["status"] == "FAIL"
    assert r["M10"]["detail"] == "no gate:page report for newtown"


def test_no_scorecards_is_a_named_barrier_and_a_fail(tmp_path):
    r = rows(ML.ledger("p5", ["comp"], tree(tmp_path, cards=[])))
    assert r["M1"]["status"] == "FAIL" and r["M1"]["value"].startswith("NOT FETCHED — ")


def test_main_writes_the_json_and_the_table_and_exits_on_failure(tmp_path, capsys):
    root = tree(tmp_path, families=("LAYOUT",))
    md = tmp_path / "ledger.md"
    assert ML.main(["p5", "--slugs", "newtown", "comp", "--md", str(md)], root=root) == 1
    data = json.loads((root / "docs/reports/p5-ledger.json").read_text(encoding="utf-8"))
    assert data["failed"] == ["M2"]
    table = md.read_text(encoding="utf-8")
    assert table.startswith("| # | Measurement | Value | Status | Detail |")
    assert "failed: M2" in capsys.readouterr().out


def test_the_real_repo_ledger_runs():
    led = ML.ledger("p5", ["index"])
    r = rows(led)
    assert r["M2"]["status"] == "PASS", r["M2"]
    assert r["M18"]["value"].endswith(" rules")
    assert all(x["value"] for x in led["rows"])
```

- [ ] **Step 2: Run it to see it fail**

```bash
python3 -m pytest tests/py/test_measurement_ledger.py -q
```

Expected: `ModuleNotFoundError: No module named 'measurement_ledger'` (1 error during collection).

- [ ] **Step 3: Write the ledger**

Create `scripts/measurement_ledger.py` with exactly this content:

```python
#!/usr/bin/env python3
"""measurement_ledger.py <project> [--slugs S ...] [--md PATH] — the numbers a close reports.

The page-build brief's measurement ledger (§20) is a list of numbers that must appear in the
close-out, not boxes that get ticked. BlueStaffyUK had the data for most of them — the
scorecards, the render checks' own declarations, the rule index, the gate:page reports — and
no step that printed them together. This one reads them and prints the rows it can compute:

  M1   nodes examined per check on real pages, > 0         the latest scorecard run
  M2   families registered vs families wired, difference ∅  tests/render/checks + targets.json
  M3   advisory vs blocking rows, reported separately       the latest scorecard run
  M6   minimum rendered text >= 12.5px on the pages          layout-min-font-size, per page
  M8   gate runs per page >= 2, both clean                   docs/reports/gate-page/<slug>.json
  M9   rework: page vs harness, never merged                 data/quality/rework-ledger.json
  M10  dup crossover, body and headers, = 0                  the gate:page reports
  M12  LLM visibility cells fetched / total                  docs/research/llm-intel/<slug>-*.json
  M13  slugs whose rendered output changed                   docs/reports/rendered-changes.json
  M18  untested rules in the rule index                      data/quality/rule-index.json

The pages are --slugs, else every page in data/facts/rebuilt.json that is not one of the twelve
built before the project 5 rules (scripts/family_rules.py BUILT_BEFORE_SYSTEM_GAPS).

Writes docs/reports/<project>-ledger.json and prints the markdown table; --md PATH also writes
the table to PATH for the gate report. A number that cannot be read is written
`NOT FETCHED — <barrier>`, never guessed.

Exit 1 when M1, M2, M6, M8 or M10 is FAIL; 0 otherwise.
"""
import argparse
import datetime
import glob
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import family_rules as FR  # noqa: E402
import render_baseline as RB  # noqa: E402
from _slugs import resolve_page  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
FAILING = ("M1", "M2", "M6", "M8", "M10")
MIN_FONT = "layout-min-font-size"


def _json(path, default=None):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def default_slugs(root):
    rows = _json(root / "data/facts/rebuilt.json", []) or []
    return [s for s in rows if isinstance(s, str) and s not in FR.BUILT_BEFORE_SYSTEM_GAPS]


def latest_cards(root):
    """(date, [card]) for the newest scorecard run, or (None, [])."""
    cards_dir = root / "data/quality/scorecards"
    dates = RB.dates_present(cards_dir) if cards_dir.is_dir() else []
    if not dates:
        return None, []
    d = dates[-1]
    return d, [_json(p) for p in sorted(cards_dir.glob(f"*-{d}.json"))]


def row(mid, measurement, value, status, detail=""):
    return {"id": mid, "measurement": measurement, "value": value, "status": status,
            "detail": detail}


def m1(root, date, cards):
    name = "Nodes examined per check, on real pages"
    if not cards:
        return row("M1", name, "NOT FETCHED — no scorecards under data/quality/scorecards "
                   "(run npm run test:render:pages)", "FAIL")
    deferred = (_json(root / "tests/render/targets.json", {}) or {}).get("deferred_checks", {})
    examined = {}
    for c in cards:
        for check, n in c.get("examined_by_check", {}).items():
            examined[check] = examined.get(check, 0) + n
    zero = sorted(k for k, n in examined.items() if n == 0 and k not in deferred)
    value = "%d checks, %d at zero (run %s, %d pages)" % (len(examined), len(zero), date, len(cards))
    return row("M1", name, value, "FAIL" if zero else "PASS", ", ".join(zero))


def m2(root):
    name = "Families registered vs families wired"
    registered = {fam for fam, _ in RB.load_checks(root / "tests/render/checks").values()}
    targets = _json(root / "tests/render/targets.json", {}) or {}
    wired = {f for fams in targets.get("families_by_page_type", {}).values() for f in fams}
    diff = sorted(registered ^ wired)
    value = "registered %d · wired %d · difference %s" % (
        len(registered), len(wired), "∅" if not diff else "{" + ", ".join(diff) + "}")
    return row("M2", name, value, "FAIL" if diff else "PASS")


def m3(root, date, cards):
    name = "Advisory findings vs blocking failures"
    if not cards:
        return row("M3", name, "NOT FETCHED — no scorecards under data/quality/scorecards",
                   "REPORTED")
    meta = RB.load_checks(root / "tests/render/checks")
    blocking = advisory = 0
    for c in cards:
        for d in c.get("details", []):
            sev = meta.get(d["checkId"], ("", "advisory"))[1]
            if sev == "blocking":
                blocking += 1
            else:
                advisory += 1
    return row("M3", name, "blocking %d · advisory %d (run %s; never summed)" % (
        blocking, advisory, date), "REPORTED")


def m6(routes, date, cards):
    name = "Minimum rendered text >= 12.5px"
    if not routes:
        return row("M6", name, "no project 5 page in scope yet", "EMPTY")
    by = {c.get("slug"): c for c in cards}
    missing = [r for r in routes if r not in by]
    if missing:
        return row("M6", name, "NOT FETCHED — no scorecard for " + ", ".join(missing), "FAIL")
    bad = [r for r in routes if any(d["checkId"] == MIN_FONT for d in by[r].get("details", []))]
    unexamined = [r for r in routes if not by[r].get("examined_by_check", {}).get(MIN_FONT)]
    value = "%d of %d pages clean (run %s)" % (len(routes) - len(bad), len(routes), date)
    return row("M6", name, value, "FAIL" if bad or unexamined else "PASS",
               ", ".join(bad + ["%s examined 0" % r for r in unexamined]))


def _gate_report(root, key):
    return _json(root / "docs/reports/gate-page" / (key.replace("/", "--") + ".json"))


def m8(root, keys):
    name = "Gate runs per page, both clean"
    if not keys:
        return row("M8", name, "no project 5 page in scope yet", "EMPTY")
    bad = []
    for k in keys:
        r = _gate_report(root, k)
        if r is None:
            bad.append(f"{k}: no gate:page report")
        elif r.get("runs", 0) < 2 or r.get("verdict") != "PASS" or not r.get("identical"):
            bad.append(f"{k}: {r.get('runs', 0)} runs, {r.get('verdict')}, "
                       f"identical {r.get('identical')}")
    value = "%d of %d pages: >= 2 runs, both clean" % (len(keys) - len(bad), len(keys))
    return row("M8", name, value, "FAIL" if bad else "PASS", "; ".join(bad))


def m9(root):
    name = "Rework rate: page vs harness, never merged"
    windows = (_json(root / "data/quality/rework-ledger.json", {}) or {}).get("windows") or []
    if not windows:
        return row("M9", name, "NOT FETCHED — data/quality/rework-ledger.json holds no window yet",
                   "REPORTED")
    w = windows[-1]
    return row("M9", name, "page %s · harness %s (window %s)" % (
        w.get("page_rate"), w.get("harness_rate"), w.get("window") or w.get("end") or "latest"),
        "REPORTED")


def m10(root, keys):
    name = "Dup crossover, body and headers"
    if not keys:
        return row("M10", name, "no project 5 page in scope yet", "EMPTY")
    body = heads = 0
    missing = []
    for k in keys:
        r = _gate_report(root, k)
        if r is None:
            missing.append(k)
            continue
        steps = {s["step"]: s for s in r.get("steps", [])}
        body += max(steps.get("dup-body", {}).get("problems", [0]) or [0])
        heads += max(steps.get("dup-headers", {}).get("problems", [0]) or [0])
    value = "body %d · headers %d across %d pages" % (body, heads, len(keys) - len(missing))
    detail = ("no gate:page report for " + ", ".join(missing)) if missing else ""
    return row("M10", name, value, "FAIL" if body or heads or missing else "PASS", detail)


def m12(root, keys):
    name = "LLM visibility cells fetched / total"
    if not keys:
        return row("M12", name, "no project 5 page in scope yet", "EMPTY")
    fetched = 0
    gaps = []
    for k in keys:
        files = sorted(glob.glob(str(root / "docs/research/llm-intel" / f"{k}-*.json")))
        status = ((_json(files[-1], {}) or {}).get("fetched") or {}).get("status") if files else None
        if status == "ok":
            fetched += 1
        else:
            gaps.append(f"{k}: {status or 'no llm-intel file'}")
    return row("M12", name, "%d / %d (one engine, one query per page)" % (fetched, len(keys)),
               "REPORTED", "; ".join(gaps))


def m13(root):
    name = "Slugs whose rendered output changed"
    data = _json(root / "docs/reports/rendered-changes.json")
    if not data:
        return row("M13", name, "NOT FETCHED — no docs/reports/rendered-changes.json (run "
                   "python3 scripts/rendered_changes.py --base <ref>)", "REPORTED")
    changed = data.get("changed", [])
    return row("M13", name, "%d (base %s → head %s)" % (
        len(changed), data.get("base"), str(data.get("head"))[:12]), "REPORTED",
        ", ".join(changed))


def m18(root):
    name = "Untested rules in the rule index"
    rules = (_json(root / "data/quality/rule-index.json", {}) or {}).get("rules", [])
    untested = sorted(r["id"] for r in rules if r.get("enforced") == "untested")
    return row("M18", name, "%d of %d rules" % (len(untested), len(rules)), "REPORTED",
               ", ".join(untested))


def ledger(project, slugs=None, root=ROOT, today=None):
    root = pathlib.Path(root)
    slugs = default_slugs(root) if slugs is None else list(slugs)
    pages = [resolve_page(s, root) for s in slugs]
    keys = [k for k, _ in pages]
    routes = [r or "index" for _, r in pages]
    date, cards = latest_cards(root)
    rows = [m1(root, date, cards), m2(root), m3(root, date, cards), m6(routes, date, cards),
            m8(root, keys), m9(root), m10(root, keys), m12(root, keys), m13(root), m18(root)]
    return {"project": project, "date": (today or datetime.date.today()).isoformat(),
            "scope": keys, "rows": rows,
            "failed": [r["id"] for r in rows if r["id"] in FAILING and r["status"] == "FAIL"]}


def markdown(led):
    esc = lambda v: str(v).replace("|", "\\|")
    out = ["| # | Measurement | Value | Status | Detail |", "|---|---|---|---|---|"]
    out += ["| %s | %s | %s | %s | %s |" % (r["id"], esc(r["measurement"]), esc(r["value"]),
                                            r["status"], esc(r["detail"]) or "—")
            for r in led["rows"]]
    return "\n".join(out) + "\n"


def main(argv=None, root=ROOT):
    ap = argparse.ArgumentParser(prog="measurement_ledger.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("project", help="the project's name, e.g. p5 — names the JSON file")
    ap.add_argument("--slugs", nargs="+", help="the pages (default: project 5 pages in rebuilt.json)")
    ap.add_argument("--md", metavar="PATH", help="also write the markdown table to PATH")
    ns = ap.parse_args(argv)
    try:
        led = ledger(ns.project, ns.slugs, root)
    except ValueError as e:
        print(f"measurement-ledger ERROR {e}")
        return 2
    out = pathlib.Path(root) / "docs/reports" / f"{ns.project}-ledger.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(led, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    table = markdown(led)
    if ns.md:
        pathlib.Path(ns.md).write_text(table, encoding="utf-8")
    print(table, end="")
    print("measurement-ledger: %d rows, %d page(s) in scope; failed: %s; JSON %s" % (
        len(led["rows"]), len(led["scope"]), ", ".join(led["failed"]) or "none",
        out.relative_to(root) if pathlib.Path(root) in out.parents else out))
    return 1 if led["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the test to see it pass, then run the ledger on this repo**

```bash
python3 -m pytest tests/py/test_measurement_ledger.py -q
python3 scripts/measurement_ledger.py p5; echo "exit $?"
```

Expected: `10 passed`. The ledger prints the ten-row table — on the verification copy
`M1 … 31 checks, 0 at zero (run 2026-09-22, 20 pages) | PASS`,
`M2 … registered 9 · wired 9 · difference ∅ | PASS`,
`M3 … blocking 6 · advisory 183 (run 2026-09-22; never summed)`, M6/M8/M10/M12
`no project 5 page in scope yet | EMPTY`, M9 and M13 as `NOT FETCHED — …` barriers,
`M18 … 20 of 80 rules` — then
`measurement-ledger: 10 rows, 0 page(s) in scope; failed: none; JSON docs/reports/p5-ledger.json`
and `exit 0`. (Numbers move with the scorecards and rules earlier tasks added; the shape does
not.)

- [ ] **Step 5: Drop the Task 26 marker from the page run; regenerate the registry**

Edit `docs/reference/page-run.md`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/docs/reference/page-run.md b/docs/reference/page-run.md
index e687852..ff7ed28 100644
--- a/docs/reference/page-run.md
+++ b/docs/reference/page-run.md
@@ -64,7 +64,7 @@ narrow question, keep building what is not blocked.
 | 16 | §18 Harden — the static scan | `python3 scripts/page_hardening_scan.py <route> --fail-on-error` (the page, its template and data, and the kit) | 0 ERROR, every WARN triaged real, dead code or false positive | `python3 scripts/page_hardening_scan.py <route> --fail-on-error`, run twice more by the row 17 runner | none |
 | 17 | §19 Gates, each run twice | `npm run gate:page -- <slug> --skip-record` runs dup (body and `--headers`), the final audit on the profile above, hardening, AEO and evidence, twice, and diffs the two runs; then `python3 scripts/quality_report.py` and `python3 scripts/perf_audit.py <route>` | `docs/reports/gate-page/<slug>.json` with both runs and their diff | `npm run gate:page -- <slug> --skip-record` exits 1 on any FAIL or any difference between the runs | none |
 | 18 | §19 Verification before completion | invoke the `superpowers:verification-before-completion` skill before any "page done" or "ready for approval" claim; the record writer runs and records the evidence: `python3 scripts/page_run_record.py <slug> verification --run "npm run -s check:all" --run "npm run gate:page -- <slug> --skip-record" --claim "<claim>"`; then `npm run gate:page -- <slug>` with the record | the `verification_before_completion` key of `data/page-runs/<slug>.json`: each command, its exit code and its examined count, and the claims it verified | `npm run gate:page -- <slug>` fails while the key is missing, a command exited non-zero, `check:all` or the gate run is not among the commands, or the key's commit is older than the page's last source change | none |
-| 19 | §20 The measurement ledger | `scripts/measurement_ledger.py` (arrives in Task 26): `python3 scripts/measurement_ledger.py <project> --slugs <slug>` | M1–M3, M6, M8–M10, M12, M13 and M18 as numbers, pasted into the gate report | `python3 scripts/measurement_ledger.py` exits 1 when M1, M2, M8 or M10 fails | none |
+| 19 | §20 The measurement ledger | `python3 scripts/measurement_ledger.py <project> --slugs <slug> --md <gate-report-table.md>` | M1–M3, M6, M8–M10, M12, M13 and M18 as numbers, pasted into the gate report | `python3 scripts/measurement_ledger.py <project>` exits 1 when M1, M2, M6, M8 or M10 fails | none |
 | 20 | §21 LLM visibility | the page's LLM-intel file from row 5 (one engine, one query); `python3 scripts/aeo_audit.py <route> --fail-on-error`, also run twice by the row 17 runner | the fetched denominator (1 of 1, or `NOT FETCHED — <barrier>`), the answer structure, the engine terms the page lacks | `python3 scripts/aeo_audit.py <route> --fail-on-error` | none |
 | 21 | §22 Deploy and close | `python3 scripts/rendered_changes.py --base <ref>`; the build's postbuild regenerates the sitemaps; invoke the `superpowers:verification-before-completion` skill again before the gate report says PASS; `session-closer`; the gate report published as an Artifact with its `.md`; commit on the project branch and never push | docs/reports/rendered-changes.json (the slugs whose built output changed: project 6's IndexNow list), the gate report, the Known Issues update | `npm run check:sitemaps` and `npm run check:all` | none — the live 200 and IndexNow wait for project 6 |
 
```

```bash
python3 scripts/build_system_registry.py
python3 scripts/build_system_registry.py --check
```

Expected: `examined docs/reference/system-registry.md; 0 problems`.

- [ ] **Step 6: Run the guards and check:all**

```bash
python3 -m pytest tests/py/test_measurement_ledger.py tests/py/test_page_run.py tests/py/test_claude_md.py tests/py/test_rules_index.py tests/py/test_system_registry.py tests/py/test_workflow_ref_check.py tests/py/test_agent_facts.py -q
npm run -s check:all; echo "exit $?"
```

Expected: all pass (663 on the verification copy); `check:all` exit 0.

- [ ] **Step 7: Commit**

```bash
git add scripts/measurement_ledger.py tests/py/test_measurement_ledger.py docs/reference/page-run.md docs/reference/system-registry.md
git commit -m "$(cat <<'EOF'
feat: measurement_ledger.py — M1–M3, M6, M8–M10, M12, M13, M18 as numbers at close

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```

### Task 27: URL-family decision table for the city cluster + comparison slugs (docs/research/2026-09-26-url-family-decision.md)

**Why.** The brief's §4: resolve the URL family before any research — one table, one
recommendation — so 28 city boards do not each decide alone. Inputs gathered from the repo on
2026-09-26 and put in the doc below: `data/locations.json` (28 rows: 11 indexable and in the
location sitemap, 17 noindex stubs, 9 empty H1s), `data/redirects.json` (one redirect into the
family, Essex, one hop), in-body inbound links measured on the build with
`scripts/page_intake.py`, the approved strategy's build order and intents, KI 16/59/62.
Search Console and backlink rows are `NOT FETCHED` with their barriers named.

**Assumptions.** The table's "Links in" column is a measurement of the 2026-09-26 build, and
the test does not re-check it (it moves with every build). Before committing, re-run
`python3 scripts/page_intake.py <slug>` for any row whose page an earlier task of this plan
rebuilt, and correct the Robots/Mode/H1/In-sitemap/Links-in cells from its output; the test
re-checks Robots, Mode, H1 and Redirects in against the data files.

**Files:**
- Create: `docs/research/2026-09-26-url-family-decision.md`
- Create: `tests/py/test_url_family_decision.py`
- Modify: `docs/reference/page-run.md:34` (drop the Task 27 marker)
- Test: `tests/py/test_url_family_decision.py`

- [ ] **Step 1: Write the failing test**

Create `tests/py/test_url_family_decision.py` with exactly this content:

```python
"""`docs/research/2026-09-26-url-family-decision.md` — one URL decision for the whole city
cluster and the comparison slugs, made once before the first city board (the brief's §4).

A decision table that misses a slug is a slug each builder decides alone, 28 times. So the
table must name every row of data/locations.json exactly once, its on-disk facts must match
the data file, each option set must mark exactly one (Recommended), and the per-page run must
point at it.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/research/2026-09-26-url-family-decision.md"
HEADER = ("Order", "Slug", "City", "Pattern", "Robots", "Mode", "H1", "In sitemap",
          "Redirects in", "Links in", "Intent (strategy)", "Decision")


def family_rows():
    lines = DOC.read_text(encoding="utf-8").splitlines()
    start = lines.index("| " + " | ".join(HEADER) + " |")
    out = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        out.append(dict(zip(HEADER, (c.strip() for c in line.strip().strip("|").split("|")))))
    return out


def cities():
    return {r["slug"]: r for r in json.loads((ROOT / "data/locations.json").read_text(encoding="utf-8"))}


def test_every_location_slug_has_exactly_one_row():
    slugs = [r["Slug"].strip("`") for r in family_rows()]
    assert sorted(slugs) == sorted(cities()), (
        "the decision table must name every data/locations.json row exactly once: missing "
        f"{sorted(set(cities()) - set(slugs))}, extra {sorted(set(slugs) - set(cities()))}")
    assert len(slugs) == len(set(slugs))


def test_the_on_disk_facts_match_the_data_file():
    data = cities()
    for r in family_rows():
        row = data[r["Slug"].strip("`")]
        assert r["Robots"] == ("noindex" if "noindex" in row["robots"] else "index"), r
        assert r["Mode"] == ("stub" if "stub" in row["defects"] else "migrated"), r
        assert r["H1"] == ("EMPTY" if not row["h1"] else "set"), r


def test_every_row_carries_a_decision_and_an_intent():
    bad = [r["Slug"] for r in family_rows() if not r["Decision"] or not r["Intent (strategy)"]]
    assert bad == []


def test_the_redirects_column_matches_data_redirects():
    redirects = json.loads((ROOT / "data/redirects.json").read_text(encoding="utf-8"))["redirects"]
    for r in family_rows():
        slug = r["Slug"].strip("`")
        want = sorted(x["from"] for x in redirects if x["to"].rstrip("/").endswith("/" + slug))
        got = sorted(re.findall(r"`([^`]+)`", r["Redirects in"]))
        assert got == want, (slug, got, want)


def test_each_option_table_marks_exactly_one_recommended():
    text = DOC.read_text(encoding="utf-8")
    tables = re.findall(r"\| Option \|[^\n]*\n\|[-| ]+\|\n((?:\|[^\n]*\n)+)", text)
    assert len(tables) == 2, "one option table for the city cluster, one for the comparison slugs"
    for body in tables:
        assert body.count("(Recommended)") == 1, body


def test_the_comparison_section_answers_known_issue_62_with_a_slug():
    text = DOC.read_text(encoding="utf-8")
    section = text[text.index("## Comparison slugs"):]
    assert "blue and black staffy" in section
    assert re.search(r"\*\*\(a\)[^|]*`/[a-z0-9-]+/`[^|]*\(Recommended\)\*\*", section)


def test_the_page_run_points_at_the_decision_without_a_pending_marker():
    run = (ROOT / "docs/reference/page-run.md").read_text(encoding="utf-8")
    line = next(l for l in run.splitlines() if "2026-09-26-url-family-decision.md" in l)
    assert "(arrives in Task" not in line
    assert "(arrives in Task" not in run, "every arrival marker in the page run has arrived"
```

- [ ] **Step 2: Run it to see it fail**

```bash
python3 -m pytest tests/py/test_url_family_decision.py -q
```

Expected: `7 failed` — each with `FileNotFoundError: [Errno 2] No such file or directory:
'.../docs/research/2026-09-26-url-family-decision.md'`.

- [ ] **Step 3: Re-verify the facts, then write the decision**

Re-verify before writing (each command prints what the table states):

```bash
python3 -c "import json;L=json.load(open('data/locations.json'));print(len(L),'rows;',sum('noindex' not in r['robots'] for r in L),'indexable;',sum('stub' in r['defects'] for r in L),'stubs;',sum(not r['h1'] for r in L),'empty h1')"
python3 -c "import json;print([r for r in json.load(open('data/redirects.json'))['redirects'] if 'uk-locations' in r['from']+r['to']])"
for s in $(python3 -c "import json;print(' '.join(r['slug'] for r in json.load(open('data/locations.json'))))"); do python3 scripts/page_intake.py $s --json | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['slug'],d['robots'][:7],d['mode'],d['h1']=='EMPTY',d['sitemap'],d['inbound_links'])"; done
```

Expected: `28 rows; 11 indexable; 17 stubs; 9 empty h1`; one redirect
(`/uk-locations/staffordshire-bull-terrier-puppies-for-sale-essex/` → `/uk-locations/staffy-puppies-for-sale-essex/`);
and per slug the values in the table below. Then create the document:

Create `docs/research/2026-09-26-url-family-decision.md` with exactly this content:

```markdown
# URL-Family Decision — the City Cluster and the Comparison Slugs

**Date:** 2026-09-26 · **Question:** before the first project 5 city board, which URL does each
page in the location family keep, which redirects exist or are needed, and what slug do the
comparison pages take? One table, one recommendation (the page-build brief, §4).

**Read from:** `data/locations.json` (28 rows), `data/redirects.json` and the `public/_redirects`
it generates, `data/page-map.json` (the old site's URLs and their Search Console baselines),
`dist/` as built on 2026-09-26 (sitemaps and in-body links), the approved strategy
`docs/superpowers/sessions/2026-09-25-location-pages-strategy.md` (build order and intent), and
Known Issues 16, 59 and 62 in `docs/reference/session-log.md`.

**Not measured:** clicks, impressions, CTR and position per URL, on Google and on Bing, and the
query rows for the family stem — `NOT FETCHED — GSC property unverified (domain expired); no
exports on disk` (the barrier every `data/page-map.json` row records). Backlinks per URL —
`NOT FETCHED — no backlink export; a paid backlinks call was never approved`. This decision is
therefore made on intent, on-disk state and internal links, and is re-checked when project 6
reads Search Console.

## The recommendation

| Option | What changes | Why | Trade-off |
|---|---|---|---|
| **(a) Keep all 28 slugs; no rename, no new redirect; both intent pairs stay two pages (Recommended)** | nothing in `data/redirects.json`; each board keeps its row's slug and canonical | 11 URLs are indexable and in the sitemap, and they are the only ones that can hold search equity; with Search Console unread, no data shows a renamed slug would earn more. The builder never rewrites a row's slug (`.claude/skills/bsuk-location-page-builder/SKILL.md`), and the one redirect the family has exists because 32 old pages linked a mistyped slug — old links keep arriving at whatever URL was published. The strategy already gives each pair two distinct intents. | The slugs stay in 11 patterns, and some do not carry the page's target keyword (`buy-blue-staffy-puppy-coventry-area`, `blue-staffy-puppies-south-yorkshire`); the H1, title and meta carry the keyword instead. |
| (b) Rename the 17 noindex stubs to one pattern, `blue-staffy-puppies-<city>`, with a 301 from each old slug | 17 redirects, 17 canonicals, 17 board keys, the footer and hub links | one consistent pattern across the cluster | 17 new redirects to keep one hop for good; the gain cannot be measured until project 6; every internal link and every old-site link to a stub moves to a redirect |
| (c) Merge each intent pair: 301 `uk-staffordshire-bull-terrier-breeder` into `blue-staffy-puppies-uk`, and `staffy-puppies-for-sale-glasgow` into `staffy-breeding-dogs-glasgow` | 2 redirects, 2 fewer pages | two fewer pages competing for "Staffy breeder UK" and "Staffy Glasgow" searches (Known Issue 59) | contradicts the approved strategy, which gives the breeder page a trust role and the breeding-dogs page the parent-dog topic; the city page would lose its own transactional URL |

## The family, per slug

Row order is the strategy's build order. **Links in** counts other built pages linking to the
URL from inside their `<main>` (the header and footer city list link every city from every
page and are not counted), measured on the 2026-09-26 build with
`python3 scripts/page_intake.py <slug>`.

| Order | Slug | City | Pattern | Robots | Mode | H1 | In sitemap | Redirects in | Links in | Intent (strategy) | Decision |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `blue-staffy-puppies-london` | London | blue-staffy-puppies-<city> | noindex | stub | EMPTY | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 2 | `blue-staffy-puppies-manchester-uk` | Manchester | blue-staffy-puppies-<city>-uk | noindex | stub | set | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 3 | `staffy-puppies-for-sale-liverpool` | Liverpool | staffy-puppies-for-sale-<city> | noindex | stub | EMPTY | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 4 | `staffy-puppies-for-sale-essex` | Essex | staffy-puppies-for-sale-<city> | noindex | stub | EMPTY | no | `/uk-locations/staffordshire-bull-terrier-puppies-for-sale-essex/` | 2 | transactional, local | keep the slug; rebuild the stub |
| 5 | `blue-staffy-puppies-dundee` | Dundee | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 6 | `blue-staffy-puppies-birmingham` | Birmingham | blue-staffy-puppies-<city> | noindex | stub | EMPTY | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 7 | `blue-staffy-puppies-bristol-uk` | Bristol | blue-staffy-puppies-<city>-uk | noindex | stub | set | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 8 | `staffy-puppies-cardiff-wales` | Cardiff | staffy-puppies-<city> | noindex | stub | set | no | — | 3 | transactional, local | keep the slug; rebuild the stub |
| 9 | `buy-blue-staffy-puppy-coventry-area` | Coventry | buy-blue-staffy-puppy-<city>-area | noindex | stub | EMPTY | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 10 | `staffy-puppies-for-sale-glasgow` | Glasgow | staffy-puppies-for-sale-<city> | noindex | stub | set | no | — | 3 | transactional, local | keep the slug; rebuild the stub |
| 11 | `blue-staffy-puppies-for-sale-leeds` | Leeds | blue-staffy-puppies-for-sale-<city> | noindex | stub | set | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 12 | `staffy-puppies-wolverhampton` | Wolverhampton | staffy-puppies-<city> | noindex | stub | EMPTY | no | — | 3 | transactional, local | keep the slug; rebuild the stub |
| 13 | `staffy-puppies-for-sale-nottingham` | Nottingham | staffy-puppies-for-sale-<city> | noindex | stub | EMPTY | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 14 | `blue-staffy-puppies-oxford` | Oxford | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 15 | `blue-staffy-puppies-sunderland` | Sunderland | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 16 | `blue-staffy-puppies-for-sale-in-leicester` | Leicester | blue-staffy-puppies-for-sale-in-<city> | noindex | stub | set | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 17 | `blue-staffy-puppies-edinburgh` | Edinburgh | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 18 | `blue-staffy-puppies-hull` | Hull | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 19 | `blue-staffy-puppies-york` | York | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 20 | `blue-staffy-puppies-south-yorkshire` | South Yorkshire | blue-staffy-puppies-<city> | noindex | stub | EMPTY | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 21 | `blue-staffy-puppies-aberdeen` | Aberdeen | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 22 | `staffy-puppies-for-sale-cornwall` | Cornwall | staffy-puppies-for-sale-<city> | noindex | stub | set | no | — | 2 | transactional, local | keep the slug; rebuild the stub |
| 23 | `blue-staffy-puppies-middlesbrough` | Middlesbrough | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 24 | `blue-staffy-puppies-inverness` | Inverness | blue-staffy-puppies-<city> | index | migrated | set | yes | — | 2 | transactional, local | keep the slug; refresh (indexable; keeps its verbatim set) |
| 25 | `blue-staffies-newcastle-under-lyme` | Newcastle-under-Lyme | blue-staffies-<city> | noindex | stub | set | no | — | 3 | transactional, local | keep the slug; rebuild the stub |
| 26 | `uk-staffordshire-bull-terrier-breeder` | UK | uk-staffordshire-bull-terrier-breeder (national) | noindex | stub | EMPTY | no | — | 3 | commercial, trust page | keep the slug; rebuild the stub |
| 27 | `blue-staffy-puppies-uk` | UK | blue-staffy-puppies-uk (national) | index | migrated | set | yes | — | 3 | transactional, national hub | keep the slug; refresh (indexable; keeps its verbatim set) |
| 28 | `staffy-breeding-dogs-glasgow` | Glasgow (breeding dogs) | staffy-breeding-dogs-<city> | index | migrated | set | yes | — | 3 | informational, trust (parent dogs) | keep the slug; refresh (indexable; keeps its verbatim set) |

Eleven slug patterns: `blue-staffy-puppies-<city>` (12), `staffy-puppies-for-sale-<city>` (5),
`blue-staffy-puppies-<city>-uk` (2), `staffy-puppies-<city>` (2), and one each of
`blue-staffy-puppies-for-sale-<city>`, `blue-staffy-puppies-for-sale-in-<city>`,
`blue-staffies-<city>`, `buy-blue-staffy-puppy-<city>-area`, `staffy-breeding-dogs-<city>` and
the two national rows. Nine rows have an empty H1 (Known Issue 59): each board picks its H1 from
the page's own primary keyword, and the empty field is never copied.

## The two intent pairs (Known Issue 59)

- **National:** `blue-staffy-puppies-uk` is the indexable UK hub (in the sitemap, linking every
  city). `uk-staffordshire-bull-terrier-breeder` is a noindex stub with an empty H1 that the
  strategy rebuilds as the trust page ("uk staffordshire bull terrier breeder", Person schema,
  the licence claim kept as a placeholder). Keep both. The trust page's board takes its own
  primary keyword; the question tool currently gives both rows one location question
  (`scripts/query_augment.py` `location_question()`), so the trust page's question file is
  written for its own keyword, not the hub's.
- **Glasgow:** `staffy-breeding-dogs-glasgow` is indexable and carries the parent-dog topic
  (Known Issue 16 made it the outreach page); `staffy-puppies-for-sale-glasgow` is the noindex
  city stub the strategy rebuilds as the Glasgow city page. Keep both; the city page links to
  the breeding-dogs page (the strategy's link role for the pair).

## Redirects in the family

One redirect touches the cluster: `/uk-locations/staffordshire-bull-terrier-puppies-for-sale-essex/`
→ `/uk-locations/staffy-puppies-for-sale-essex/` (301, one hop, target built). No chain, no
redirect out of any of the 28 URLs; `npm run check:redirects` holds this. Option (a) adds none.

## Comparison slugs (Known Issue 62)

No comparison page, hub or page-map row exists. The strategy's first comparison page targets
"blue and black staffy" (secondary: "blue or black staffordshire bull terrier").

| Option | Slug for the first page | Why | Trade-off |
|---|---|---|---|
| **(a) Top level, the target keyword plus `-uk`: `/blue-and-black-staffy-uk/` (Recommended)** | `blue-and-black-staffy-uk` | Every page rebuilt so far has a top-level slug, most with `uk` in it (`blue-staffy-health-uk`, `uk-staffordshire-bull-terrier-guide`); a top-level route is the page's own key, so it needs no `data/page-map.json` row before the build (the builder skills' project 5 rule 7) and no hub first. The slug carries the strategy's target keyword. | If a comparison hub is built later, this page is not under it in the URL; the hub links to it, and the slug is never changed after it ships. |
| (b) Under a new hub: `/staffy-comparisons/blue-and-black-staffy/` | `staffy-comparisons/blue-and-black-staffy` | groups later comparison pages under one folder | the hub has to be built first, and the page needs a page-map row before its build |
| (c) Under the guides hub: `/blue-staffy-blog-guides/blue-and-black-staffy/` | `blue-staffy-blog-guides/blue-and-black-staffy` | reuses an existing hub | mixes the comparison profile into the blog cluster, and the page needs a page-map row |

Later comparison pages follow the same pattern: top level, the page's target keyword, `-uk`.

## What happens next

The two recommendations go to the answer board as one batch before the first city board. The
chosen option is recorded on each page's board in `meta.slug`, and
`docs/reference/page-run.md` row 3 reads this file.
```

- [ ] **Step 4: Drop the last marker from the page run**

Edit `docs/reference/page-run.md`. The hunks below are the exact change: every `-` line is the old text to find, every `+` line the new text, and the unprefixed lines are unchanged context. Line numbers are against `cag-parity` @ `cecedfa`; if an earlier task of this plan moved the text, find it by the context lines.

```diff
diff --git a/docs/reference/page-run.md b/docs/reference/page-run.md
index ff7ed28..71cf90d 100644
--- a/docs/reference/page-run.md
+++ b/docs/reference/page-run.md
@@ -31,8 +31,7 @@ page-run record and the gate runner (row 17) take the key.
 | blog | `.claude/skills/bsuk-blog-post/SKILL.md` | `<slug>` (a post in `src/content/blog/` builds at `/<slug>/`) | `blog` | headings, images |
 
 The URL-family decision for the city cluster and the comparison slugs is one table,
-`docs/research/2026-09-26-url-family-decision.md` (arrives in Task 27). Read the page's row
-before row 3.
+`docs/research/2026-09-26-url-family-decision.md`. Read the page's row before row 3.
 
 ## The run
 
```

- [ ] **Step 5: Run the test to see it pass**

```bash
python3 -m pytest tests/py/test_url_family_decision.py tests/py/test_page_run.py tests/py/test_claude_md.py tests/py/test_rules_index.py -q
```

Expected: `338 passed` on the verification copy (7 of them this task's).
`test_the_page_run_points_at_the_decision_without_a_pending_marker` also proves that no
`(arrives in Task` marker is left anywhere in `docs/reference/page-run.md`.

- [ ] **Step 6: check:all and the full Python suite**

```bash
npm run -s check:all; echo "exit $?"
npm run test:py
```

Expected: `check:all` exit 0; `test:py` all green (5287 passed, 14 skipped, 1 xfailed on the
verification copy, which had Tasks 1–22 simulated only by stand-ins for Tasks 16 and 18).

- [ ] **Step 7: Commit**

```bash
git add docs/research/2026-09-26-url-family-decision.md tests/py/test_url_family_decision.py docs/reference/page-run.md
git commit -m "$(cat <<'EOF'
docs: URL-family decision for the city cluster and the comparison slugs

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
EOF
)"
```

---

## Close

### Task 28: Close-out — gates twice, measurement ledger, gate report, merge

**Files:**
- Create: `docs/reports/brief-parity-gate-report.md`
- Create: `docs/artifacts/bsuk-brief-parity-gate-report.html` (built)
- Modify: `docs/reference/session-log.md` (Known Issues + build record)
- Modify: `docs/reports/cag-brief-parity-audit.md` (a "Closed by" column note at the top of "Gaps to close")

- [ ] **Step 1: Fresh build, then every gate twice**

```bash
cd /Users/apple/Downloads/BSUK-cag
npm run -s build
for i in 1 2; do npm run -s check:all; echo "check:all run $i exit=$?"; done
for i in 1 2; do python3 -m pytest tests/py -q -p no:cacheprovider | tail -3; done
npm run test:render:meta
npm run test:render:pages
```

Expected: build exit 0. `check:all` exit 0 on both runs. pytest shows the same counts on both runs with 0 failed. The controller's integrated replay gave 5771 passed, 12 skipped, 1 xfailed; a small difference on the real branch is fine only if both runs agree and 0 fail. Meta: 0 failed. Pages: the only failure is the pre-existing `uk-locations/blue-staffy-puppies-uk` `nav-jump-target-lands` (execution note 8). Any other failure is a regression, so stop and fix it in the task that caused it.

- [ ] **Step 2: Zero-examined guard and measurement ledger**

```bash
node scripts/build_scorecard.mjs
python3 scripts/rendered_changes.py --base /Users/apple/Downloads/BSUK/dist --json   # foundation's build; foundation has no dist-hashes.json yet
python3 scripts/measurement_ledger.py brief-parity --md /tmp/brief-parity-ledger.md
```

Expected: the scorecard guard reports every non-deferred check examined > 0. `rendered_changes.py` reports exactly the 12 rebuilt pages as changed (the controller's replay: the footer band hidden on 11 pages by Task 7, the delivery line on puppy cards by Task 3), not all 51 (Task 16 hashes content, not inline CSS). The ledger writes the M-table to `/tmp/brief-parity-ledger.md`; paste it into the gate report. In the replay: M1 PASS (31 checks, none at zero), M2 PASS (9 registered = 9 wired), M3 blocking 3 (the known nav-jump page at three widths), M18 17 untested rules. It exits 1 only on a FAIL in M1, M2, M6, M8 or M10.

- [ ] **Step 3: Invoke `superpowers:verification-before-completion`**

Invoke the skill through the Skill tool. Nothing in Step 4 may say PASS unless a command above backs it with its output and exit code in this session.

- [ ] **Step 4: Write the gate report**

Create `docs/reports/brief-parity-gate-report.md` with these sections:
- **Verdict:** one line.
- **Definition of done:** one row per audit gap (Wave 1 rows 1–6, Wave 2 rows 7–14, Wave 3 rows 15–20, Wave 4 rows 21, 21b, 21c, 22–25, plus the two decisions). Each row gives the task number, the commit, PASS / PASS-WITH-DEVIATION / FAIL, and the evidence command.
- **Gates run twice:** the Step 1 outputs.
- **Measurement ledger:** the Step 2 table.
- **Integration conflicts:** copy the table from this plan's header, noting any that differed.
- **Open items for project 5:**
  - `nav-jump-target-lands` on `uk-locations/blue-staffy-puppies-uk`.
  - Burn down the 48-entry retired-facts allowlist (Known Issue 65) city page by city page.
  - Keep the four new-page checks in advisory until one full cluster runs clean (Task 14's `promotions`).
  - Leeds has no competitor cache.
  - The Task 27 URL-family decision needs the user's approval before the London board.
- **Adopt later:** the audit's "Adopt later" list, unchanged.

Build and publish the report:

```bash
python3 scripts/build_report_artifact.py docs/reports/brief-parity-gate-report.md docs/artifacts/bsuk-brief-parity-gate-report.html "Brief Parity Gate Report" "BlueStaffyUK · before project 5" "Did the brief-parity build close its gaps?" "BlueStaffyUK — brief parity gate report" "gate report" "$(date +%F)" docs/reports/brief-parity-gate-report.md
```

Publish it as an Artifact and put the URL in the report's header line.

- [ ] **Step 5: Session log and Known Issues**

In `docs/reference/session-log.md`, add a "Brief parity build" entry covering the branch, the commits, the gate-report URL, and new Known Issues (numbered after the highest existing one) for each open item in Step 4. Mark the audit's live defects D1–D6 closed with their commits.

- [ ] **Step 6: Commit**

```bash
git add docs/reports/brief-parity-gate-report.md docs/artifacts/bsuk-brief-parity-gate-report.html docs/reference/session-log.md docs/reports/cag-brief-parity-audit.md
git commit -m "docs: brief-parity gate report, session log, Known Issues

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

- [ ] **Step 7: Finish the branch**

Invoke `superpowers:finishing-a-development-branch`. Recommended: merge `--no-ff` into `foundation`, as every earlier BSUK build did, after the user confirms. Never push. Remove the `BSUK-int` scratch worktree and the `parity-int` branch.

```bash
cd /Users/apple/Downloads/BSUK
git merge --no-ff cag-parity -m "merge: brief-parity build — CAG page-brief gaps closed before project 5

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
npm run -s build && npm run -s check:all && python3 -m pytest tests/py -q | tail -3
git worktree remove ../BSUK-int --force && git branch -D parity-int
```

Expected: the merge completes, and build, `check:all` and pytest on `foundation` are green. Then update the memory note `bsuk-cag-parity-status` to COMPLETE and name the next build: project 5, London first.
