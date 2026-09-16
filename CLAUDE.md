# BlueStaffyUK — Project Guide

BlueStaffyUK is a Glasgow breeder of Staffordshire Bull Terriers, Blue Staffies in
particular (Lisa Bright, 40 Coltmuir Street, G22 6LU). The site is transactional +
informational: the buy and location pages take enquiries, the care and guide pages earn
the traffic.

## Paths and deploy model

- **`src/pages/<slug>/index.astro` is what ships.** Eleven rich pages are one Astro file
  each; 28 locations and 6 puppies are data-driven from `data/locations.json` and
  `data/puppies.json`; blog posts are a markdown content collection under `src/content/blog/`.
- Build `npm run build` → `dist/`. The page gates measure `dist/`; `check:markers` and
  `check:placeholders` also scan the instruction tree (`.claude/`, `rules/`, `tests/render/`).
- Where work lands and how it is committed: judgment rules 2–3 below, and
  [`rules/deploy.md`](rules/deploy.md).
- After adding or removing a page: `npm run sitemaps` (the build's postbuild already does it).
- Generated files are never hand-edited: the eleven rich pages, `data/page-map.json`,
  `data/locations.json`, `data/image-manifest.json`, `public/_redirects`, `public/llms.txt`,
  `public/images/**`, `src/content/blog/*.md`. `README.md` carries the full list.

## Deploy — inactive until project 6

There is no host, no domain and no deploy. `SITE_URL_PLACEHOLDER`, `PHONE_PLACEHOLDER` and
an unset `PUBLIC_FORMSPREE_ID` are the correct state today and catastrophic on launch day,
so the launch tooling is ported but inactive. Each piece declines differently, and the
difference matters when you are reading an exit code:

- `python3 scripts/perf_audit.py <slug> --live` (and `--psi`, which implies it) refuse on
  the **`SITE_URL` placeholder**, not on the release flag: they print `REFUSED` and exit 2.
  Drop `--live` and measure `dist/`.
- `python3 scripts/indexnow_submit.py <slug>` (arrives in Task 17) refuses unless
  `BSUK_RELEASE=1` is set, and exits non-zero.
- `bash scripts/health-sweep.sh` does **not** refuse: with no `SITE_URL` it warns
  `no SITE_URL — skipping live checks (project 6)`, skips its live block, and its exit code
  is decided by the checks it did run.
- `BSUK_RELEASE=1 npm run check:placeholders` is the gate that will refuse to ship a
  placeholder. Pre-launch it counts and prints and passes.

## The rules live in `rules/`, not here

The pixel-level rules are enforced by `tests/render/`, not by this file — a check that
fails the build is worth more than a paragraph that asks nicely.

| Pack | Covers |
|---|---|
| [`rules/README.md`](rules/README.md) | how to read a pack, the three `enforced` classes, the ledger contract |
| [`rules/headings.md`](rules/headings.md) | H1–H6 outline gate, Title Case, header style |
| [`rules/images.md`](rules/images.md) | uniform in-body sizing, alt-text keyword spread, further-reading thumbs = the target's own hero |
| [`rules/schema.md`](rules/schema.md) | structured data, schema-only freshness |
| [`rules/links.md`](rules/links.md) | Link-First anchor placement |
| [`rules/copy.md`](rules/copy.md) | voice, originality, entity method, claims |
| [`rules/design.md`](rules/design.md) | the nine non-negotiable visual rules + hero/counter separation, H3-image-first |
| [`rules/gates.md`](rules/gates.md) | pre/post-build process gates |
| [`rules/deploy.md`](rules/deploy.md) | where work lands and how it ships |
| [`rules/puppies.md`](rules/puppies.md) | the puppy and buy cluster's own rules |

`data/quality/rule-index.json` is the machine-readable index: every rule is `test`,
`judgment`, or `untested`. **`untested` means deletion candidate** —
`python3 scripts/quality_report.py` §5 prints the list on every run. The `judgment` class is
capped at nine (`judgment_cap: 9`); a tenth exemption is a rule that has to earn a test.

### Page type → what to read first

| Building… | Skill | Extra rule packs |
|---|---|---|
| home | `bsuk-site-patterns` | headings, images, copy |
| buy / for-sale | `bsuk-puppy-page-builder` | puppies, images, headings |
| puppy `/available-puppies/<slug>/` | `bsuk-puppy-page-builder` | puppies, schema, images |
| hub | `bsuk-site-patterns` | links, headings |
| location | `bsuk-location-page-builder` | copy, links |
| blog | `bsuk-blog-post` | headings, images |
| about / contact | `bsuk-contact-form`, `bsuk-trust-signals` | copy, links |
| comparison | `bsuk-comparison-page-builder` | images, headings, copy |

The generic skills already ported live at `.claude/skills/` — `grill-me`,
`section-auditor`, `internal-link-agent`, `keyword-cluster`, `anti-ai-writing` and the
`framework-*` set among them. Each is one SKILL.md file in its own directory.

Full task→entry-point table: `docs/reference/quick-start.md`.

## The nine judgment rules that stay here

These nine have **no mechanical decision procedure**, which is exactly why they cannot be
delegated to a test and must stay in context. They are the nine `enforced: judgment` rows in
`data/quality/rule-index.json`, and that file's `judgment_cap: 9` is what stops the list
growing. Every other rule moved to a pack.

1. **First-person brand voice.** Write as Lisa Bright: *we / us / our / here at
   BlueStaffyUK*. Our puppies, our kennel and our credentials are framed as ours, never
   described from outside. Neutral register is correct only for breed facts and cited
   research.
2. **Work on the project branch, never on the trunk.** Foundation work landed on
   `foundation`; the system transfer runs on `system-transfer`. A task's work belongs on the
   branch its plan names.
3. **Commit after every task; never push.** There is no remote and project 6 owns the
   launch. Finished work that is unpushed is finished; finished work that is uncommitted is
   lost.
4. **Recommend + Why.** Whenever you present options, mark exactly one
   **(Recommended)**, justify it from real data (GSC, competitors, the codebase — never
   taste), and name the trade-off of the recommended pick.
5. **Restate the brief before you build.** Goal · scope · gates · what "done" means · what
   is out of scope. Improve the prompt where it is ambiguous so it can be corrected before
   work is spent on it.
6. **Preview before apply.** Any page redesign is previewed and approved before it is
   written to site files. A redesign never adds or removes content — visual layer only.
7. **Confidence gate, 97%.** Below that, do not dead-stop: write finished work to disk, log
   the open question to the session brief's `## Open Flags`, ask exactly ONE narrow
   question, and keep building everything that is not blocked.
8. **Write from the outline, never from a sibling.** Reuse components, CSS and structure
   freely; write every page's PROSE fresh from its own outline. Never open a sibling's file
   to copy paragraphs. Only the whitelist may match verbatim. Enforced *after* the fact by
   `dup-no-sibling-crossover`, but the rule is about method: a page copied and then reworded
   passes the test and still breaks the rule.
9. **No fabricated claims.** Never invent credentials, prices, reviews, test results or
   competitor metrics. Un-fetched data is written `NOT FETCHED`, never inferred. The
   guarantee length is `NOT FETCHED` — `data/settings.json` has `guarantee_days: null` and
   no page may state a number until the breeder gives one. An unconfirmed licence or statute
   claim is written `LICENCE_CLAIM_PLACEHOLDER` / `LEGAL_CLAIM_PLACEHOLDER`, never asserted.

### Two standing rules that are not judgment exemptions

Both have a mechanical backstop, so neither takes a slot under the cap — but both govern how
work is done rather than how a page is built, so they are stated here.

- **No source-repo vocabulary, ever.** This operating system was ported from a bird
  breeder's repo, and the twelve markers `scripts/marker_check.py` scans for are not a style
  preference: a hit is a re-base that did not happen. There is no allowlist, and
  `npm run check:markers` is the last link in `npm run check:all`. The marker list lives in
  the gate, deliberately, so that quoting it here cannot make this file fail its own rule.
- **Every deliverable ships as an Artifact with copy buttons, plus `.md`.** Research docs,
  outlines, keyword tables, meta sets, gate reports, lessons docs — the deliverable is a
  published Artifact whose sections each carry a copy button and which downloads as `.md`,
  not prose in the chat the breeder has to select by hand. Update the existing Artifact in
  place (pass its `url`) when one already covers the topic; mint a new URL only for
  genuinely new work. Keep the HTML source in `docs/artifacts/` so it is versioned and
  re-publishable. **Author the content once as markdown inside the page and render it** —
  that is what makes a section's copy button emit exact markdown.

## Gates — run these, do not re-derive them

```bash
npm run check:all
```
```bash
npm run test:py
```
```bash
npm run test:render:meta
```
```bash
npm run test:render:pages
```

`check:all` chains `check:parity`, `check:redirects`, `check:schema`, `check:sitemaps`,
`check:placeholders` and `check:markers`, in that order. Until Task 16 closes,
`check:markers` reports the ported `tests/render/` fixtures as known debt; every other gate
in the chain must be green. `test:render:meta` is the gate that
checks the checkers — run it **before** trusting any page result. `test:render:pages`
measures the target pages at 375/768/1280 in a real browser.

Also: `python3 scripts/board_gate.py <slug>` · `python3 scripts/final_page_audit.py` ·
`python3 scripts/page_hardening_scan.py` · `python3 scripts/dup_content_audit.py [--headers]` ·
`python3 scripts/aeo_audit.py --all` · `python3 scripts/evidence_audit.py --all` ·
`python3 scripts/form_contract_audit.py` (needs `PUBLIC_FORMSPREE_ID` in the environment) ·
`python3 scripts/perf_audit.py <slug>` · `python3 scripts/quality_report.py` ·
`python3 scripts/generate_page_dates.py --check` · `bash scripts/health-sweep.sh`.
The page audits report only by default; pass `--fail-on-error` to make them exit non-zero,
and `--json` to write the machine-readable result under `docs/reports/`.

**No page is built without an approved board.** `python3 scripts/board_gate.py <slug>`
refuses when `data/boards/<slug>.json` is missing or unapproved;
`python3 scripts/build_page_board.py <slug>` builds one and
`python3 scripts/board_approve.py <slug>` records the approval. The homepage board
(`data/boards/index.json`) is the worked example.

**A gate's output is a hypothesis about the page, not a fact about it.** Before editing
anything in response to a gate, confirm the defect on the built page; before believing a
PASS, read the gate's own examined count. The rule lives in
[`rules/gates.md`](rules/gates.md) today; its canonical spec is
`.claude/skills/bsuk-gate-integrity/SKILL.md`.

**When a defect escapes, charge it to the harness, not to a new rule.** If an invariant
already covered it and stayed quiet, the tool is broken: add the case to
`tests/render/fixtures/known_broken/`, watch the meta gate fail, fix the check, and write no
new rule.

**Foundation's render baseline is not a defect list.** Project 1 migrated WordPress markup
verbatim, so the harness is measuring the old site's body HTML through a new shell. Those
rows are the starting line for projects 3 and 4, and are recorded in
[`docs/reports/foundation-gate-report.md`](docs/reports/foundation-gate-report.md).

## Brand context — read before any design or content work

`data/settings.json` is the source of truth for the breeder's name, address, hours, socials
and the delivery band. `data/puppies.json` and `data/price-matrix.json` carry the current
litter and the prices — never type a price by hand. The locked facts, from the Foundation
spec under `docs/superpowers/specs/`:

- Breeder **Lisa Bright**, Glasgow (40 Coltmuir Street, G22 6LU).
- Prices **£1,500** (Roman, Byrd, Ince) and **£1,700** (Vennie, Christa, Cheryl). Deposit
  **£500, refundable**.
- Delivery **£200–£350** for UK home delivery, by DEFRA-approved transport, priced by
  distance; collection in Glasgow is the alternative.
- Phone is `PHONE_PLACEHOLDER` until project 6 provisions a number. It is the only allowed
  representation of the phone number anywhere in this repo, and the site URL is
  `SITE_URL_PLACEHOLDER` on the same terms.
- Guarantee length is **not established** (`guarantee_days: null`). Do not write one.
- Licence and statute claims are **not established**. They are written
  `LICENCE_CLAIM_PLACEHOLDER` / `LEGAL_CLAIM_PLACEHOLDER` and guarded by
  `scripts/placeholder_check.py` until the breeder confirms them.

The design system is project 3. Until then there is no component kit and no locked palette;
`src/layouts/BaseLayout.astro` and `src/styles/global.css` are the whole shell.

## Where everything else went

- `docs/reference/system-registry.md` — every agent, skill, script and data file
- `docs/reference/quick-start.md` — task → entry point, and the reference-doc index
- `docs/reference/session-log.md` — build history and **Known Issues**
- `docs/reference/WORKFLOW.md` — the sprint model
- `docs/reference/seo-rules.md` — the numbered SEO rules, **57** of them in categories
  A–J. That is a different count from `data/quality/rule-index.json`'s 66 (of which 9 are
  `enforced: judgment`, capped there): the ledger indexes the `rules/` packs and the
  render-harness checks, seo-rules.md numbers its own categories. `docs/reference/quick-start.md` states
  both, and all three files change together.
- `docs/reference/credentials.md` — which env key exists and what reads it
- `docs/superpowers/specs/` and `docs/superpowers/plans/` — the six projects' specs and plans
