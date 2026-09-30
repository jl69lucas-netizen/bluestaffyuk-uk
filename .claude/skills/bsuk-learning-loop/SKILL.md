---
name: bsuk-learning-loop
description: Use at the end of every BSUK build, and whenever a defect escapes to the breeder, to decide what the escape means — a harness bug, or a genuinely new invariant. Enforces the promotion path (defect → failing test → fix → rule) and its inverse (a rule with no test is a deletion candidate). Triggers "what did we learn", "close the loop", "add a rule for this", "this shipped broken", session-closer.
---

# BSUK Learning Loop

**The one thing this skill exists to prevent:** answering an escaped defect by writing
another paragraph. This system already has thirty-plus rules and a 24.8% rework rate.
Rule thirty-one does not move that number. A test does.

## The two constraints

1. **No test, no rule.** A lesson becomes a rule only after a failing test exists.
   A rule with no test is a deletion candidate — `scripts/quality_report.py` §5 lists them.
2. **When a defect escapes, charge it to the harness, not to a new paragraph.**
   If an invariant already covered it, the tool is broken. Fix the tool.

Constraint 2 is the load-bearing one, and it has now been measured twice.

**2026-07-31:** ten findings, **ten in the harness, zero in the pages**. A tool built to
stop gates lying contained ten ways to lie; three were findable only by measuring a real page.

**2026-08-01 (Phase 2):** the pattern held and got sharper. The corpus-wide headline of
**418 defect rows collapsed to 85** without a single page being edited — because 337 NAV
rows turned out to be 81% counting granularity plus a check that reset with a
*smooth-animated* `scrollTo(0,0)` and clicked 80ms into its own animation. The one page
scoring zero was not the healthy page; it was the only page being measured correctly.
**Had that been charged to the pages, the fix would have been a site-wide CSS change to
`src/styles/global.css` to cure a defect that did not exist.**

Of the defects found that day, every one was in the harness or its tests, and several were
in the *fix for the previous one*: a comment asserting a guard that never fired, a reset
that deleted its own run's results, a regression probe that passed for the wrong reason
because zero survivors satisfies "fewer than three".

## Procedure

Run this at the end of a build, or the moment the breeder reports something shipped wrong.

### Step 1 — Diff what was reworked

```bash
git log --since=<session start> --pretty=format:"%h %s" | grep -iE "^[a-f0-9]+ (fix|revert)|fix\(|correct|restore|undo|repair"
```

Every hit is an escape: something reached a commit and had to be undone. Include anything
the breeder reported by hand, whether or not it produced a commit.

### Step 2 — Classify each escape into a family

`IMG` · `LAYOUT` · `NAV` · `CSS` · `SEM` · `SCHEMA` · `DUP` — the same seven the harness,
the scorecards and the ledger use, plus `GATE` / `A11Y` / `COPY` for what the harness does
not measure. Same vocabulary everywhere, or the ledger and the scorecard stop describing
the same site.

### Step 3 — Ask FIRST whether an invariant already covered it  ← the load-bearing step

Check `tests/render/checks/*.ts` for a check in that family that should have caught it.

**If one exists and did not fire, the harness has a bug.** Then:

1. Add the missed case to `tests/render/fixtures/known_broken/<check-id>.html`.
2. Run `npm run test:render:meta` and **watch it fail**. A fixture that does not fail is
   not a reproduction — you have added decoration.
3. Fix the check.
4. Re-run; confirm the fixture fires and `known_good` stays silent.
5. **Write no new rule.** The rule already existed; the tool was wrong.

Before editing any page in response to a checker, read `.claude/skills/bsuk-gate-integrity/SKILL.md`.
Twelve checkers on this site have reported defects that did not exist, and two reported
PASS having examined zero pages.

**Two traps this step has already sprung, both worth checking for by name:**

- *A number that is suspiciously large is usually a counting bug, not a catastrophe.*
  Before believing a family total, confirm every check counts the same unit — one defect
  ROW per failure mode, with instances in `count`. `tests/render/lib/runCheck.ts` enforces it now.
- *A fix can be worse than the bug.* Verify the fix at the level the bug lived at. A reset
  that worked in a one-page, one-viewport test destroyed two-thirds of the results in a
  three-project run, because Playwright loads a spec module **once per worker process**,
  not once per run.

### Step 4 — Only if no invariant covers it, write one

In this order, never out of it:

1. Write the failing case first — `known_broken/<new-check-id>.html`.
2. Run the meta gate; **confirm it fails, and read WHY it failed.** A test that goes red
   for the wrong reason is worse than no test: it will go green again for the wrong reason.
3. Implement the check in the right `checks/*.ts`, registered `severity: 'advisory'`.
4. Confirm it fires on `known_broken` and is silent on `known_good`.
5. Add the rule text **next to the test**, and add the row to `data/quality/rule-index.json`
   as `enforced: test` with the check id.

A new check enters as **advisory**. It earns `blocking` after one full cluster with zero
false reports. On the first baseline, three of the four checks with findings would have
blocked falsely — 224 inline prose links flagged by tap-target size (WCAG 2.2 exempts
inline links), 27 `sr-only` skip links, and `12.48px` against a `12.5` threshold.

**A check that fires falsely once gets demoted, not whitelisted.** A gate that cries wolf
once is ignored forever, which is how this repo accumulated twelve of them.

**Judging a blocking check that fires:** ask whether it fired on something real, not
whether it is convenient. `img-srcset-within-2x` fired on all nine puppy-cluster pages and kept
its blocking severity, because a 640px asset painted at 48px is not arguable. The regen
went to the backlog behind a **counted** `RENDER_OVERRIDE`, which the quality report prints
every run. Suppressing a real defect visibly is honest; re-tuning the threshold until it
goes green is not.

### Step 5 — Append to the ledger

```bash
python3 scripts/quality_report.py
```

The source repo's rework-ledger script was not ported — source repo only. The ledger
file itself came across: `data/quality/rework-ledger.json`, empty until escapes
accumulate. Append to it by hand, and let `scripts/quality_report.py` read it.

Read section 3 (worst family) and section 5 (deletion candidates). **If a family tops the
list two reports running and its checks all pass, the checks are wrong before the pages
are.** Note that the worst family is ranked by ROWS, not instances — ranking by instances
would permanently elect whichever check enumerates the most nodes, which is a fact about
the check, not the site.

## Banked triggers — reach for these before re-deriving them

| When you see… | Reach for | Why |
|---|---|---|
| a page that **names our puppies in prose** with no visuals | `src/components/PuppyList.astro` | the source repo shipped a row of named animals as text only. Style 1 (4:5 + frosted label), per-puppy `objectPos`, 2-up at ≤600px, `width`/`height` mandatory or `final_page_audit` `img_dims` fails the whole page. `project_minipuppycard_component` |
| a **caption or table defect on mobile** | the `display:block` list in the page's `.tH` mobile block | `caption` is the member everyone forgets. Left at `display:table-caption` inside a table whose other children are blocks, the browser shrink-to-fits it into a narrow column. One rule, two visible defects, and it hits every future `.tH`. `reference_table_caption_mobile_stacking` |
| a **further-reading / Keep-Reading thumbnail** | a thumbnail audit (not ported — source repo only) | the thumb must be a crop of the linked page's OWN hero, never the source page's art. 24 of 35 were wrong site-wide on 2026-08-07. `reference_read_card_thumb_is_target_hero` |
| **"the component is styled but nothing shows"** | the component's own contract, before the content | `Schema.astro`'s `organization` branch was the only one of four ignoring its `data` prop, so a real review was silently dropped; and the page styled `.quote-c` with no base component. Check the contract first |
| a **contrast / PageSpeed finding** | `.claude/skills/bsuk-perf-gate/SKILL.md`, then `a11y-text-contrast-aa` | the harness check answers in ~2s; Lighthouse takes ~25s and needs ≥5 runs before you may attribute CLS |
| an **ordering probe** reporting a big number | re-read the probe | on 2026-08-07 an H3 image-order probe claimed 15 offenders; the real number was 4. It counted decorative seams and ran past section boundaries. Filter to `.sec-img`, split on `<h2\|<h3` |

## What does NOT go through this loop

Rules classed `enforced: judgment` in `data/quality/rule-index.json` — voice, LICENCE_CLAIM_PLACEHOLDER
framing, work-on-main, Recommend+Why, the verified-claim ledger, and the rest of the
capped twelve. Each states in the index why a test cannot exist. Adding a thirteenth
requires raising the cap deliberately, in the spec, with a reason. It is a cap, not a
loophole, and the report prints its size every run.

## Related

- `docs/superpowers/specs/2026-09-16-system-transfer-design.md` — how this system arrived
- `.claude/skills/bsuk-gate-integrity/SKILL.md` — read at the FIRST report from any checker
- `.claude/skills/bsuk-final-page-pass/SKILL.md` — the per-page gate this sits underneath
- `scripts/quality_report.py` · `data/quality/rule-index.json`
