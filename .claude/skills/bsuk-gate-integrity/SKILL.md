---
name: bsuk-gate-integrity
description: Use when any checker, scanner, audit, linter, or gate reports a defect on a BSUK page — page_hardening_scan, final_page_audit, dup_content_audit, the render harness, Lighthouse, axe, or a probe you just wrote — and before editing any page in response. Also use when a gate reports PASS and you are about to trust it, when a whitelist or exemption was just widened, or when a report contradicts what you can see on the page.
---

# SKILL: BSUK Gate Integrity — Verify the Gate Before You Fix the Page

## Overview

**Twelve checkers have cried wolf on this cluster.** Fixing what they reported would
have been wasted work *and* would have degraded correct code. Two of them reported
PASS while examining nothing at all.

**Core principle:** a gate's output is a *hypothesis about the page*, not a fact about
it. Confirm the defect exists before you edit, and confirm the gate examined something
before you believe a pass.

**Violating the letter of this rule is violating its spirit.** "I'll just make the
small fix it suggests" is the failure mode, not the exception to it.

## The Iron Law

```
NO PAGE EDIT FROM A GATE REPORT WITHOUT CONFIRMING THE DEFECT ON THE PAGE.
NO PASS BELIEVED WITHOUT CONFIRMING THE GATE'S OWN ITEM COUNT.
```

## The two directions of failure

**Direction 1 — the gate cried wolf (10 of 12 cases).** Editing the page degrades
correct code and buries the real bug under a plausible-looking fix.

**Direction 2 — the gate examined nothing (2 of 12 cases).** A green report over an
empty input set. This is the more dangerous direction, because nobody investigates
a pass.

## The recorded baseline — every one of these was real

| # | Reported | Reality | The bug in the checker |
|---|---|---|---|
| 1 | 7 tap-target ERRORs | 0 real | matched `li`/`pill`/`chip` in a selector *name*; read only `min-height`, so `height:28px` fell through to a font-size guess |
| 2 | 6 icon-baseline WARNs | 0 real | matched keywords across **CSS comments** — a `/* GREEN TICK */` comment flagged whatever rule sat beneath it; also didn't know `place-items` is shorthand for `align-items` |
| 3 | "body copy runs 84ch" | already 70ch | approximated `ch` as `0.5em`; Source Sans 3's `0` advance is ~`0.6em`, inflating every reading ~20% |
| 4 | 23 body dup crossovers | 0 real | whitelist didn't encode reviews / counter strip / read-card labels / doc-badge lists, all of which CLAUDE.md explicitly permits |
| 5 | 8 contrast failures at 375px | 0 real | tested `display:none` on the element but **not on its ancestors** — it was measuring the hidden desktop dial |
| 6 | hero "432px, over the 350–420 band" | 396px, in band | measured `.adopt-hero` *including* its `16px 0 20px` padding; `.hero-grid` is the element the spec names |
| 7 | `absolute-hero-not-unwound` | 0 real | name-matched exemption (`badge\|chip\|tag\|caption`); a price pill called `-p` slipped through |
| 8 | dup gate: "PASS — 0 pages" | **examined nothing** | zsh does not word-split `$SL`; all 8 slugs arrived as ONE argument |
| 9 | seam parity: 0 sections | 15 sections | `grep '<section class="sec"'` — 6 of the 8 source puppy pages used `<section id=…>` |
| 10 | 586 specificity WARNs | 2 real | "ancestor somewhere in file" × "component somewhere in file" is a **cartesian product**, not DOM nesting |
| 11 | 5 `.btn-cta` WARNs | 0 real | the prescribed fix (`.adopt-main a.btn-cta{color:#fff}`) was **already in the file**; the check only looked at the unqualified rule |
| 12 | `.delivery-price` reported twice | 1 real | a CSS **comment** documenting the past fix contains the literal text `.delivery-c p{color:#5b524a}` — trap #2, repeated two years' worth of lessons later |

Rows 10–12 were produced while *building* the checks in rows 9–12's own session.
**Budget for this.** A new check's first output is a draft, not a finding.

## Confirming a reported defect — cheapest tool first

| Claim | How to confirm | Never |
|---|---|---|
| a11y / contrast | Lighthouse or axe on the built page — it agreed with the code, not the scanner (100/100/100, 0 failed audits) | trust a regex sweep alone |
| "this element is interactive" | grep the built HTML inside that component for `<a ` / `<button` | infer from a class name |
| any measurement (px, `ch`, ratio) | measure in a real viewport via **Playwright** | compute from a formula; `0.5em` over-reports a `ch` by ~20% |
| "the component is styled wrong" | `getComputedStyle` on the real element | read the CSS and reason about which rule wins |
| a size against a spec band | measure **the element the spec names**, excluding padding it does not include | measure the wrapper |
| a duplicate-content hit | open both pages at the reported offset | trust the shingle report |
| "this class is unused / missing" | grep the file for a **qualified** or `:not()` form — the fix may already be applied | assume the unqualified rule is the whole story |

**Open the flagged rule and quote it before editing.** If you cannot quote the exact
line that is wrong, you have not confirmed anything.

## Confirming a PASS — read the gate's own item count

Every BSUK gate prints what it examined. **Read that number first.**

```
"PASS — no cross-page duplicate runs ≥12 words in 0 pages."   <- 0 pages. Not a pass.
"harness: 0 pages matched"                                    <- not a pass.
"scan — 12 source files, 0 built pages"                        <- did you run astro build?
"36 agents examined · 0 injected"                              <- marker didn't match?
```

**The zsh trap, verbatim:**

```bash
SL="slug-a slug-b slug-c"
python3 scripts/dup_content_audit.py $SL     # zsh does NOT word-split -> ONE argument
```

All eight slugs arrived as a single argument, matched no page, and the gate reported
PASS having compared nothing. **zsh does not word-split unquoted parameter
expansions.** Pass the slugs literally, or use `${=SL}`.

## After widening any whitelist or exemption: prove the gate is not blinded

Inject the real defect back in, confirm FAIL, remove it, confirm PASS, confirm the
diff is empty.

```bash
# 1. re-introduce the actual defect the gate is supposed to catch  -> expect FAIL
# 2. remove it                                                     -> expect PASS
# 3. git diff --stat <file>                                        -> expect EMPTY
```

Done for the dup gate on 2026-07-26, for `absolute-hero-not-unwound` on 2026-07-28
(by re-injecting the real `.pofig{position:absolute;width:44%}` bug and confirming it
still WARNs), and for the seam check on 2026-07-29 (by removing two seams from one page
and confirming `FAIL missing=1`). **Repeat after every whitelist edit.**

Note the tolerance trap: a seamless-hero page runs at `sections == seams`, so removing *one* seam
stays inside the seamless-hero allowance and still PASSes. **Know your gate's
tolerance before you design the proof**, or the proof passes for the wrong reason.

## A gate you write is a gate that lies

Six of the twelve were probes written in the same session that reported them. Before
trusting your own probe:

- **Skip invisible elements properly** — `!el.offsetParent` or a zero-sized rect.
  Testing `display:none` on the element alone misses a hidden ancestor.
- **Measure the element the spec names**, not its padded wrapper.
- **Strip `/* … */` before parsing CSS.** Twice now, prose has been analysed as code.
- **Anchor selector regexes on line start.** A `(?<![\w.\s>+~])` lookbehind looks
  right and collects nothing, because a rule at the start of a line is preceded by a
  newline — which is whitespace.
- **Tokenise class attributes; never use `\b`.** `-` is a word boundary, so
  `\bseam\b` matches `class="seam-wrap"` and doubles every count.
- **Don't confuse co-occurrence with structure.** If the CSS says "descendant", the
  check must resolve the DOM subtree.
- **Print your own examined count**, and refuse to call a zero-item run a pass.

## Red Flags — STOP

- "The scanner says 7 tap targets fail, let me fix them" → confirm one first
- "It reported PASS, moving on" → what was the item count?
- "I'll widen the whitelist to make it pass" → prove it still catches the real bug
- "My probe says 84ch" → did you measure a real `ch`, or multiply by 0.5?
- "The gate is clean, so the page is clean" → a clean scan proved nothing on the pricing page
- "586 findings, this page is a disaster" → 584 of them are your check
- "Close enough, I'll just make the change it suggests"
- "I wrote this check, it's fine"

**All of these mean: confirm on the page, then act.**

## Rationalizations

| Excuse | Reality |
|---|---|
| "The scanner is usually right" | 10 of 12 reports on this cluster were wrong. |
| "Confirming takes longer than fixing" | The 84ch report scoped a cluster-wide reflow that turned out to be a 4-line CSS change. |
| "It's only a WARN, harmless to fix" | Fixing a false WARN degrades correct code and hides the real defect behind a plausible edit. |
| "It said PASS, that's the good outcome" | Two gates passed over zero pages. A pass is a claim about an input set, not about the page. |
| "I only widened the whitelist a little" | Stems must be anchored mid-phrase; the shingle window slides. Three iterations lost to this. |
| "The page looks fine to me" | The Browser pane reports `vw:0` — nothing painted. Measure in Playwright. |
| "I wrote the probe, I know it's right" | Six of the twelve were mine, in the session that reported them. |
| "A high finding count means a broken page" | It usually means a broken check. 586 → 2 on one page set. |
| "The fix it suggests is obviously correct" | On 5 of 8 findings the suggested fix was already in the file. |

## Quick Reference

1. Gate reports a defect → open the flagged rule → **quote the wrong line** → confirm on the built page → *then* edit.
2. Gate reports a pass → **read the item count** → 0 or 1 when you passed many means the run proved nothing.
3. Whitelist or exemption widened → **re-inject the real defect** → FAIL → remove → PASS → `git diff` empty.
4. Measurement claim → **Playwright**, real viewport, the element the spec names.
5. Suspiciously many findings → suspect the check, not the page. Fix the check.
6. Wrote your own probe → comments stripped, `offsetParent` checked, padding excluded, line-anchored, tokenised, examined-count printed.

## Real-World Impact

Twelve false or empty reports across three sessions (2026-07-26, 2026-07-28,
2026-07-29). One collapsed a cluster-wide paragraph reflow into 4 lines of CSS. One
would have painted a black rectangle over eight infographics. Two reported PASS over
zero pages. One reported 586 defects where there were 2 — and finding those 2 was only
possible *because* the false 584 were removed first.

Full records: the source repo's session logs for 2026-07-26, 2026-07-28 and 2026-07-29
(not ported — source repo only). BSUK's own record of a gate that lied belongs in
`data/quality/rule-index.json`, beside the rule it failed to hold up.
