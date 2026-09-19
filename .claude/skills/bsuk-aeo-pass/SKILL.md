---
name: bsuk-aeo-pass
description: Use when finishing any BSUK page build, rebuild or polish and the page must be citable by AI answer engines — ChatGPT, Perplexity, Claude, Google AI Overviews. Also use when a page ranks but is never cited, when AI answers about Blue Staffies quote competitors instead of us, when copy reads as anonymous "we/our" rather than named entities, or when checking freshness signals, brand-owned method names, BLUF openers, atomic sections, declarative sentences, or stat-bearing headers. Triggers - "run the AEO pass", "make this citable", "AI search optimization", "answer engine optimization", "GEO check".
---

# SKILL: BSUK AEO Pass — Make the Page Citable

**Run this AFTER `bsuk-page-hardening` and BEFORE `bsuk-final-page-pass`.** Hardening
asks *does the page render*; this asks *can an answer engine lift a correct sentence
out of it and attribute it to us*.

```bash
npx astro build
python3 scripts/aeo_audit.py <slug> [<slug> ...]     # pass slugs LITERALLY
```

`ERROR` = fix before deploy. `WARN` = read the section, then decide.

> **Read `.claude/skills/bsuk-gate-integrity/SKILL.md` first.** The BLUF check here is a **proxy** on
> sentence length and opening phrases — it cannot tell a wind-up from a legitimately
> long declarative sentence. Confirm any flagged section by reading it. And read the
> audit's own examined count: `0 pages matched` is not a pass.

**This skill does not restate what already exists.** Entity-first patterns, the
Inverse Pyramid, the four Featured-Snippet strategies and per-engine GEO targeting
live in **`.claude/skills/framework-aio-geo/SKILL.md`** — read it for the *how*. This skill is the
six-part **gate**, plus the three parts that had no home anywhere in the system before
2026-07-30.

---

## Non-negotiable facts (verified against the data files 2026-07-30)

Three claims in circulation are wrong. Never write them, and correct them on sight.

| ✗ Never write | ✓ Correct | Why |
|---|---|---|
| any licence or statute worded from memory | **LICENCE_CLAIM_PLACEHOLDER** / **LEGAL_CLAIM_PLACEHOLDER** | Neither has been confirmed. Until it is, the placeholder IS the text — in prose only, never in a heading, route or code key. |
| any price typed by hand | **£1,500** (Roman, Byrd, Ince) · **£1,700** (Vennie, Christa, Cheryl) — the litter spans **£1,500–£1,700** | Every figure comes from `data/price-matrix.json` through a helper. A hand-typed price is a defect even when it is currently right. |
| any health-guarantee length | **NOT FETCHED** | `data/settings.json` has `guarantee_days: null`. Until the breeder confirms a window, the page says a written health guarantee is supplied and gives no number. |

Verified safe to use: `Lisa Bright` · `Carlisle, Cumbria` ·
`DEFRA-approved transport` · the 28 UK cities in `data/locations.json` ·
`Staffordshire Bull Terrier` · the coat descriptions in `data/puppies.json`
(blue, blue and white, white). The phone is `PHONE_PLACEHOLDER` and the host is
`SITE_URL_PLACEHOLDER` until project 6.

Every figure still comes from `data/price-matrix.json` and `data/settings.json` through
a helper, never a typed literal, and every health/credential claim stays inside the
**Verified-Claim Ledger**. AEO is not a licence to overclaim: a confidently-worded
false sentence is the worst possible outcome, because answer engines repeat it.

---

## Part 1 — BLUF (Bottom Line Up Front)

AI models weigh the start of a passage most heavily. **Every section opens with the
answer**, in one sentence, before any context.

| ✗ | ✓ |
|---|---|
| "Before we get into numbers, it's worth stepping back to consider the history of puppy keeping…" | "Blue Staffies from Lisa Bright cost **£1,500–£1,700**, set by age and training." |
| "There are many things to think about when buying a puppy." | "Lisa Bright delivers to the 28 UK cities in `data/locations.json` by DEFRA-approved transport — **£200–£350, priced by distance** — or you collect in Carlisle." |

**Gate:** the audit flags any H2/H3 whose first sentence exceeds 32 words or opens
with a wind-up phrase. It is a proxy — read the flagged section. This stacks with the
EEBP openings the for-sale builder already mandates; BLUF is the *first sentence*
rule, EEBP is the *paragraph shape* rule.

## Part 2 — Atomic Content

Every section must survive being **chunked out of the page**. A section that only
makes sense after reading the one above it cannot be cited.

The test: **cover everything above the heading. Does the section still name its
subject, its actor, and its qualifier?**

| ✗ Not atomic | ✓ Atomic |
|---|---|
| "It also includes full documentation." | "Lisa Bright's kennel is LICENCE_CLAIM_PLACEHOLDER licenced and supplies **LICENCE_CLAIM_PLACEHOLDER LEGAL_CLAIM_PLACEHOLDER** home-bred documentation with every puppy." |
| "They wean between those weeks." | "Blue Staffy pups wean at **12–16 weeks**, never sooner." |

Not machine-checkable — this is the skill's **human** item. Read three random sections
in isolation. If one needs its neighbour, rewrite its first sentence.

## Part 3 — Entity-Rich Writing

Replace generic nouns and pronouns with named entities, so an engine can bind our
brand to the topic.

- `our puppies` → **`Canis lupus familiaris`** / **`Blue Staffy`**
- `we` → **`Lisa Bright's home kennel`** / **`BlueStaffyUK — Carlisle`**
- `licensed` → **`LICENCE_CLAIM_PLACEHOLDER licenced`**, **`LICENCE_CLAIM_PLACEHOLDER LEGAL_CLAIM_PLACEHOLDER home-bred`**
- `tested` → **`PCR vet sex-checked`**, **`L-2-HGA and Polyomavirus screened`**

**Measured on the 8 for-sale pages, 2026-07-30 — the gate exists because of this:**

```
                       binomial  breeder-name
eggs                          6             2
blue                         2             1
blue-brindle                        6 (P. blue-brindle) 1
home-raised                   0             0     <- no binomial, no breeder
health-guarantee              1             0
dna-tested                    9             0
baby                          0             0     <- no binomial, no breeder
adoption-cost                 0             0     <- no binomial, no breeder
```

**3 of 8 pages name no species at all, and 4 of 8 never name the breeder.** The audit
WARNs on both, and on pronoun-heavy copy where `we/our/us` outnumber named entities.

## Part 4 — Simple, Declarative Sentences

One idea per sentence. Subject–verb–object. Extraction-ready.

> Every puppy leaves us vet-checked, microchipped and vaccinated, with a written health
> guarantee. The puppies are socialised with the family from the day they are born.

The audit reports average sentence length and the count over 30 words. It does **not**
judge truth — that is the Verified-Claim Ledger's job. Anti-AI rhythm rules from
`.claude/skills/anti-ai-writing/SKILL.md` still apply: declarative does not mean robotic, and a page
of identical short sentences fails the humour/voice gate.

## Part 5 — Strategic Formatting for Citations

Answer engines prefer structure they can lift whole.

- **Comparisons** — the Blue vs Blue-Brindle table answers "X vs Y" queries directly. The
  comparison cluster already ships these; make sure the *money* pages link them.
- **Lists** — enumerate documents, stages, tiers.
- **Stat-bearing headers** — put the number *in the heading*:
  "**12 Years** of Breeding Experience" · "**1,000+ Word** Vocabulary Potential" ·
  "**72-Hour** Health Guarantee" · "**£200–£350** Airport / **£200–£350** Home Delivery".

The audit counts tables, lists, and stat-bearing headers, and WARNs when a page has no
header carrying a figure. Headers still obey **Title Case** and the **declared header
style** (`framework-heading-hierarchy` §Header Style Selection).

## Part 6 — Brand Ownership and Freshness

### 6a. Label the method, so the expertise stays ours

Unlabeled expertise gets absorbed as generic knowledge. **Approved by the breeder
2026-07-30 — two labels, used for different things:**

| Label | Covers |
|---|---|
| **The NOT FETCHED — the breeder has not named a house method** | bottle-feeding, weaning schedule, the 12–16-week wean gate — the *raising* process |
| **The Carlisle Socialization Method** | family handling, out-of-crate routine, noise/handling desensitisation — the *socialization* side |

Use them as proper nouns, capitalised, at least once per relevant page, and define
them once where first used. Before 2026-07-30 there were **zero instances site-wide**,
across 108 pages, 61 skills and 68 agents — so every page's raising process read as
generic advice any competitor could claim.

Keep them honest: they name a real process, they are not a certification. Never imply
third-party accreditation.

### 6b. Freshness is a schema signal, never a visible one

AI citations favour recently-updated pages. CLAUDE.md **bans visible dates**, so
freshness lives only in JSON-LD.

- `data/page-dates.json` (deferred — the map is generated on first run) holds real per-page git dates; `BaseLayout` injects a
  `WebPage` node with `datePublished` / `dateModified` for every route that does not
  already set its own. Coverage is measured per run; `--check` fails when the map is stale.
- After any content change: `python3 scripts/generate_page_dates.py` and **commit the
  map**. `--check` fails when it is stale.
- **Never compute the date at build time.** A shallow CI clone makes a build-time
  `git log` report the deploy date for every file and stamp a fake "today" on every
  page. That is the visible-date dishonesty moved into JSON-LD, where it is worse.
  (BSUK has no CI and no remote until project 6; the rule holds from the first run.)
- The audit **ERRORs** on a missing `dateModified` and **ERRORs** on any visible
  "Updated <month> <year>" / "Last updated" / "Posted on" stamp.

### 6c. Puppy listings are the freshness engine

The `/available-puppies/` pages carry genuinely changing facts. Update age, weight and
training progress as they change — that is real freshness, not date-churn.

**Standing check:** `data/puppies.json` holds the litter — Roman, Byrd and Ince at
£1,500, Vennie, Christa and Cheryl at £1,700. Every pup in that file needs an
`/available-puppies/<slug>/` page before listings can be the freshness engine; a pup
with no page has nothing to keep fresh.

### 6d. Refresh sleeper pages

A page with backlinks and declining traffic is the cheapest AI-visibility win.
Identify it, refresh with current figures and an original statistic, regenerate the
date map, redeploy. Needs GSC data to target properly — blocked until the GSC MCP
lands.

---

## Quick Reference

| Part | Gate | Machine-checked? |
|---|---|---|
| 1 BLUF | first sentence ≤32 words, no wind-up opener | proxy |
| 2 Atomic | section survives being chunked out | **human** |
| 3 Entity-rich | binomial + breeder name present; not pronoun-heavy | yes |
| 4 Declarative | avg sentence length, count over 30 words | yes (advisory) |
| 5 Formatting | ≥1 table/list, ≥1 stat-bearing header | yes |
| 6a Labeled | one of the two approved method names present | yes |
| 6b Freshness | `dateModified` in JSON-LD, **zero** visible dates | yes (ERROR) |

## Common Mistakes

- **Writing "LICENCE_CLAIM_PLACEHOLDER LEGAL_CLAIM_PLACEHOLDERI."** It is LEGAL_CLAIM_PLACEHOLDER. This has been corrected once
  already; do not reintroduce it.
- **Adding a visible "Updated July 2026".** Banned. The signal is schema-only.
- **Treating a build-time git date as freshness.** Depth-1 CI makes it a lie.
- **Overclaiming to sound citable.** An engine repeats what it lifts. Stay inside the
  Verified-Claim Ledger.
- **Turning declarative into robotic.** `anti-ai-writing` still applies.
- **Trusting the BLUF proxy.** It flags long first sentences; some are fine. Read them.
- **Inventing a third method name.** Two are approved. Adding more dilutes both.
