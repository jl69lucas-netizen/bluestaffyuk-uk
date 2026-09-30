# System transfer gate report

BlueStaffyUK rebuild, project 2 of 6. Written by hand from the real outputs of the two full
runs recorded in `docs/reports/system-transfer-run.log`. Date 2026-09-17. Branch
`system-transfer`, no remote, nothing pushed.

Spec: `docs/superpowers/specs/2026-09-16-system-transfer-design.md`. §9 is the definition of
done **as amended by §11**; the checklist at the end of this report answers it line by line
in its amended form.

Read the two severities in this report differently. The **system gates** — the port script,
the marker gate, parity, redirects, schema, sitemaps, the agent and system registries, the
render baseline checker and pytest — are zero-tolerance and are all at zero. The **ported
content audits** (final page, page hardening, duplicate content, AEO, evidence) and the
**render pages run** report large non-zero counts, and that is the intended outcome, not a
failure: this project moved the measuring instruments onto a site whose body HTML is still
Foundation's verbatim WordPress migration. Those counts are a recorded baseline for
projects 3–5, not defects introduced here. Every such number below is tagged
**baseline** or **regression**; there are no regressions.

---

## Build

| | |
| --- | --- |
| Command | `npm run build` (Astro 6.3.8, pinned) |
| Pages built | **49** `index.html` |
| Content collections | page 13 · post 1 · location 11 · puppy 6 · video 4 |
| Postbuild | `scripts/generate_sitemaps.py` — 5 shards |
| Exit | 0, both runs |

`.env` was sourced for both runs, so `PUBLIC_FORMSPREE_ID` was in the environment and Astro
baked the real Formspree action into `dist/`. `dist/` is gitignored and is not committed.
Two consequences, both observed: `FORMSPREE_ID_PLACEHOLDER` is at **0 occurrences in 0
files** across `dist/` and the instruction tree, and `scripts/form_contract_audit.py` clears — `examined 1 forms; 0 problems
(inquiry 1, in-scope 1, newsletter 0)`. The last `#contact` row is gone. The render
harness's `form-inquiry-contract` still reports 3 advisory rows on the contact page; those
are field-contract rows against migrated markup, not endpoint rows.

## Port manifest — `scripts/port_from_cag.py`

```
examined 180 rows; applied 10, skipped-existing 129, deferred 41, missing 0, blocked 0
```

| Mode | Rows | Behaviour |
|---|---|---|
| `copy` | 10 | overwritten on every run |
| `rename` | 0 | none in the final manifest |
| `rebase` | 129 | never overwritten — the hand edits are the deliverable |
| `deferred` | 41 | recorded, not applied |
| **Total** | **180** | |

`applied 10` equals the copy + rename count exactly. `skipped-existing 129` equals the
rebase-row count exactly. `missing 0`, `blocked 0`.

**Second-run proof.** The second run printed the identical line — `applied 10,
skipped-existing 129, deferred 41, missing 0, blocked 0`. No `rebase` row was re-applied on
the second run; had one been, `applied` would have exceeded 10. Spec §9's "a second run
reports `applied 0` for `rebase` rows" is satisfied in the form the script actually reports
it: rebase rows are counted under `skipped-existing`, and that bucket holds all 129 on both
runs.

## Marker gate — `scripts/marker_check.py`

```
examined 233 files; 0 problems
```

Zero tolerance, no allowlist. Scan roots are every manifest `dst` plus `CLAUDE.md`,
`rules/`, `docs/reference/`, `package.json`, `tests/render/` and
`scripts/dup_content_audit.py`. The one structural exception is `data/port-manifest.json`
itself, which necessarily carries `cag-` source paths.

The gate is named `marker_check.py`, not `parrot_marker_check.py` (spec §11): `package.json`
is a scan root, so the gate's own wiring line would otherwise be a permanent hit, and §4
forbids exclusions.

Count history, by the task that drove it down:

| Point | Hits |
|---|---|
| Task 2 — gate first written and run | 418 |
| Task 9 — rules and ledger re-based | 205 |
| Task 11 — agents re-based and fact-linted | 203 |
| Task 12 — skills re-based | 192 |
| Task 15 — render harness re-based | **0** |

`npm run check:all` runs it. Both runs: 0.

## Fact lint and the placeholder gate

**Fact lint** — `tests/py/test_agent_facts.py` lints `.claude/agents` and `.claude/skills`:
only the locked £1,500 / £1,700 amounts; a banned-token list carried over from the source repo's
domain (wildlife-trade bodies, a hosting provider stated as fact, an invented weight range
and an invented city count); DEFRA permitted only beside "transport"; no
placeholder token inside a heading or a path segment; no lifespan other than 12–14 years.
Green on both runs as part of the 1240-test suite. Rule 10 is enforced, not asserted.

**Placeholder gate** — `scripts/placeholder_check.py`, pre-launch (advisory) mode:

| Token | Occurrences | Files |
|---|---|---|
| `SITE_URL_PLACEHOLDER` | 883 | 113 |
| `PHONE_PLACEHOLDER` | 21 | 13 |
| `FORMSPREE_ID_PLACEHOLDER` | 0 | 0 |
| `LICENCE_CLAIM_PLACEHOLDER` | 639 | 74 |
| `LEGAL_CLAIM_PLACEHOLDER` | 155 | 70 |
| **Total** | **1698** | |

**These are the final, post-close-out figures**, and two things moved them from the 1692 the
two gate runs recorded. Both are accounted for exactly:

| Cause | Delta | Detail |
|---|---|---|
| `docs/reference/session-log.md` named three tokens in prose | +3, then **−3** | `docs/reference` **is** a placeholder scan root, so spelling a token there is a permanent hit that could never reach zero on launch day. The session-log entry was rewritten to describe the stand-ins instead of naming them ("the site-URL stand-in", "the two legal-claim stand-ins"), which is why `FORMSPREE_ID_PLACEHOLDER` is back at 0. Net zero |
| `placeholder_check.py` now derives its scan set from `marker_check.scan_roots()` | **+18** | 93 files newly covered; 0 files dropped. `SITE_URL` +3, `PHONE` +3, `LICENCE` +6, `LEGAL` +6 |

`docs/reports` is **not** a placeholder scan root, so this report may name the tokens freely;
that is deliberately where the token names and counts now live, and the session-log points
here for them. The scan set is `dist/` plus the union of the gate's literal floor
(`.claude/skills`, `.claude/agents`, `docs/reference`) with every file the marker gate judges
— so a row added to `data/port-manifest.json` in project 3 inherits placeholder coverage the
same day it inherits marker coverage, with no second list to forget. Measured old-roots total
on the identical tree: 1680; new-roots total: 1698.

`LICENCE_CLAIM_PLACEHOLDER` and `LEGAL_CLAIM_PLACEHOLDER` are the two content placeholders
introduced during the skill re-base (spec §11). They stand in for the breeder-licence and
Lucy's-Law claims until Lisa Bright confirms them. They are placeholders precisely so the
site cannot ship an unverified legal claim.

**Release refusal, probed once.** `BSUK_RELEASE=1 npm run check:placeholders` exits **1**
with `FAIL: BSUK_RELEASE=1 and 1692 placeholder occurrence(s) remain in dist/ and the
instruction tree.` That non-zero exit is the expected, designed outcome — placeholders
remain by design until project 6 — and is the only reason `BSUK_RELEASE` was ever set in
this project. `build:release` and the IndexNow scripts were not run.

## Rules and CLAUDE.md

**57 SEO rules, three-way agreement.** `docs/reference/seo-rules.md` (`# SEO Rules — Master
Ruleset (57 Rules)`, Rule 1 through Rule 57 across ten categories),
`docs/reference/quick-start.md` and `CLAUDE.md` all state 57, and the file says in terms
that all three must be changed together. `tests/py/test_claude_md.py` holds CLAUDE.md's
router honest against the ten packs on disk in `rules/` — every routed pack exists, and
every pack on disk is routed.

**Rule ledger** — `data/quality/rule-index.json`, **66 rows**:

| `enforced` | Rows |
|---|---|
| `test` | 39 |
| `untested` | 18 |
| `judgment` | **9** |

`judgment_cap` is **9**, down from the source repo's 12 — three source-repo rules — a wildlife-trade
convention rule, the Verified-Claim Ledger and brand-owned method labels — do not exist here, and a cap of 12 over 9
rules is three free exemptions rather than a cap. `tests/py/test_rules_index.py` pins both
the cap and the class size. Every `pack` path in the ledger resolves to a file in `rules/`;
all rule ids are unique. `quality_report.py` §5 lists the 18 untested rows as deletion
candidates for later projects.

## Agents and skills

| | |
| --- | --- |
| Agents | **36** — `python3 scripts/build_agent_registry.py --check` → `examined 36 agents; 0 problems` |
| Skills | **53** on disk in the single `.claude/skills` tree |
| System registry | `python3 scripts/build_system_registry.py --check` → `examined docs/reference/system-registry.md; 0 problems` |
| Deferred manifest rows | 41 — recorded, not ported |

Both registries are generated, not hand-typed, and both `--check` runs are green on both
runs. §3's agent list is the 36 names the registry prints, not the spec's original "about
25" (§11). The skill count is 53 rather than the plan's 52: the source repo has 12
`framework-*` skills, not 14 (§11), and the re-base landed one additional page-builder skill
in the single tree. `tests/py/test_skills_frontmatter.py` holds every skill's frontmatter,
including the case-sensitivity of a skill name.

## Board system

`data/boards/index.json` — the homepage proving board — carries an `approval` record:
`approved_at` **2026-09-16T00:00:00Z**, `canvas_version` `none`, with a `record_hash`. The
board is approved. Its Artifact source is `docs/artifacts/boards/index.html`. The board's
ledger slots (`picks`, `notes`) are empty **by design** until project 3 adopts the component
kit; emptiness of the ledger is not the approval signal and is not read as one here.

`python3 scripts/board_gate.py index`, both runs, identical:

```
board-gate index [build] — 14 sections, 15 headings, 49 live pages, 0 entity refs,
0 ledger siblings, 0 assets examined
3 FAIL · 2 WARN
```

Exit 1. The two WARNs are `ledger-examined-zero` (the component ledger records one page and
no sibling of `index`, so the five `ledger-*` checks examined nothing — the project-3
condition above) and `min-h5-h6` (`H5 0 / H6 0 — floor is 5 each`, the migrated homepage's
heading depth, the same finding `final_page_audit.py` reports as `min_h5_5` / `min_h6_5`).

The three FAILs are all `header-collision`, and all three are **carried duplicates in
migrated copy that this project may not edit** (spec §11). By heading and page:

| Homepage heading | Collides with | On page |
|---|---|---|
| `Meet the Proud Parents of Our Blue Staffy Puppies` | `Our Commitment: The Cornerstone of Our Blue Staffy Puppies` | `/uk-locations/staffy-breeding-dogs-glasgow/` |
| `Our Commitment to the Health of Our Blue Staffy Puppies` | `Our Commitment: The Cornerstone of Our Blue Staffy Puppies` | `/uk-locations/staffy-breeding-dogs-glasgow/` |
| `How to Buy Your Blue Staffy Puppy` | `How to Buy Your Blue Staffy Puppy from BlueStaffyUK.uk` | `/uk-blue-staffy-puppy-buying-guide/` |

The other two FAILs the gate reported at Task 5 — site chrome, `Blue Staffy News: Join 500+
Readers!` on 3 pages and `Available Blue Staffy Puppies` on 12 — cleared with Task 15's
`HEADER_WHITELIST` / `HEAD_TERMS` re-base, as §11 predicted. Five down to three. The gate
was not weakened; the three remaining rows are a Foundation content finding carried to
project 4.

## Ported gates

Every script below crossed from the source repo in this project. "Baseline" means the number
measures Foundation's migrated WordPress body HTML and is the starting line for projects
3–5; "regression" would mean this port introduced it. **There are no regressions.**

| Gate | Summary line | Exit | Tag |
|---|---|---|---|
| `scripts/migration_parity.py` | `examined 40 pages, 0 failing` | 0 | zero-tolerance, green |
| `scripts/redirect_check.py` | `examined 18 redirects, 1964 internal refs (distinct per page); 0 redirected refs; 0 problems` | 0 | zero-tolerance, green |
| `scripts/schema_check.py` | `examined 49 pages; 0 blocking, 0 advisory` | 0 | zero-tolerance, green |
| `scripts/sitemap_check.py` | `examined 49 built pages, 5 shards, 35 sitemap urls; 0 problems` | 0 | zero-tolerance, green |
| `scripts/marker_check.py` | `examined 233 files; 0 problems` | 0 | zero-tolerance, green |
| `scripts/build_agent_registry.py --check` | `examined 36 agents; 0 problems` | 0 | zero-tolerance, green |
| `scripts/build_system_registry.py --check` | `examined docs/reference/system-registry.md; 0 problems` | 0 | zero-tolerance, green |
| `scripts/render_baseline.py --check` | `examined render-baseline-project2.md; 0 problems` | 0 | zero-tolerance, green |
| `scripts/placeholder_check.py` | `placeholders: 1692 (advisory — set BSUK_RELEASE=1 to make this blocking)` | 0 | by design until project 6 |
| `scripts/final_page_audit.py` | `examined 12 pages; 12 problems (0 PASS · 0 PASS-WITH-WARNINGS · 12 FAIL)` · `baseline-only FAIL pages: 0` | **1** | baseline (migrated headings: `all_six_levels`, `min_h5_5`, `min_h6_5`, `faqpage_present`) |
| `scripts/page_hardening_scan.py` | `BSUK page-hardening scan — 25 source files, 49 built pages` · `130 ERROR · 27 WARN` | 0 | baseline (migrated images and markup) |
| `scripts/dup_content_audit.py` | `FAIL — 135 duplicated passages ≥12 words.` | **1** | baseline (migrated copy; project 4) |
| `scripts/aeo_audit.py --all` | `examined 49 pages; 37 problems (181 WARN)` · `baseline-only FAIL pages: 37 (failing only freshness …); pages with a real ERROR: 0` | 0 | baseline (freshness only — needs `generate_page_dates.py`, project 4) |
| `scripts/evidence_audit.py --all` | `examined 49 pages; 47 problems (2 WARN)` | **1** | baseline (term budgets on migrated copy) |
| `scripts/form_contract_audit.py` | `examined 1 forms; 0 problems (inquiry 1, in-scope 1, newsletter 0)` | 0 | **cleared by the re-base** |
| `scripts/quality_report.py` | report printed; worst family SEM (117 rows); 0 open overrides; 18 rules with no backing test | 0 | baseline |
| `bash scripts/health-sweep.sh` | sections 1–3 and 5 all PASS; section 4 (LIVE SITE) `FAIL / -> 000` ×3 and `WARN www -> 000` | **1** | expected — **there is no live site until project 6** |

`form_contract_audit.py` refuses lazily when `PUBLIC_FORMSPREE_ID` is unset: it prints
`REFUSED: PUBLIC_FORMSPREE_ID is unset — a form audit that matches nothing would report
every form clean.` and exits **2** ("cannot run"), consistent with `board_gate.py` and
`evidence_audit.py`, and matching `tests/render/checks/form.ts`'s single REFUSED defect row
with `examined: 0`. Verified directly.

Every non-zero exit above is either a designed refusal (`placeholder_check.py` under
`BSUK_RELEASE=1`, `form_contract_audit.py` unset) or a migrated-content baseline
(`final_page_audit.py`, `dup_content_audit.py`, `evidence_audit.py`, `board_gate.py`, the
sweep's live-site section). None is a defect this project introduced.

## Harness

**Pytest** — `npm run test:py`:

```
1240 passed, 7 skipped, 146 warnings in 80.80s
```

Identical on both runs, including `test_port_manifest.py`, the ported gate tests,
`test_agent_facts.py`, `test_rules_index.py`, `test_claude_md.py`,
`test_skills_frontmatter.py` and `test_credentials_doc.py`.

**Render meta** — `npm run test:render:meta`: **315 passed, 36 skipped**, exit 0, both runs.
Every family registered is wired and examines at least one page. Three checks are recorded
in `tests/render/targets.json` `deferred_checks`, each with an explicit promotion condition
tied to the scorecard examining more than zero nodes:
`layout-hero-counter-separation`, `layout-h3-image-first`, `sem-statement-label-visible` —
all three waiting on project 3's component kit.

The plan's two proposed deferral ids, `bottom-bar-under-tabbar` and `analytics-double-load`,
**never existed in the render harness** — they are Python page-hardening checks in the source
repo — so `deferred_checks` gained nothing from them (spec §11). Carried as an open item.

**Render pages** — `npm run test:render:pages`: **5 passed, 46 failed**, exit 1, both runs.
That is the recorded Project 2 baseline in `docs/reports/render-baseline-project2.md`, whose
generated table is produced by `python3 scripts/render_baseline.py --write` and re-verified
by `npm run baseline` (`examined render-baseline-project2.md; 0 problems`, both runs). The
table was regenerated from this project's own scorecard run, not hand-typed.

| Family | Blocking | Advisory | Pages |
|---|---|---|---|
| A11Y | 0 | 3 | 1 |
| CSS | 0 | 51 | 17 |
| DUP | 0 | 33 | 11 |
| FORM | 0 | 3 | 1 |
| IMG | 15 | 0 | 6 |
| LAYOUT | 4 | 0 | 2 |
| NAV | 18 | 0 | 6 |
| SCHEMA | 21 | 0 | 7 |
| SEM | 9 | 108 | 17 |
| **Total** | **67** | **198** | **17** |

265 defect rows across 17 page scorecards. **No new blocking row versus Foundation's gate
report.** Exactly two rows moved after the harness re-base, both downward and both intended:

| Check | Foundation | Project 2 | Cause |
|---|---|---|---|
| `dup-no-sibling-crossover` | 42 rows / 14 pages | **33 rows / 11 pages** | Task 15 re-measured the DUP whitelist against BSUK's own chrome, so shared-shell text no longer reports as sibling crossover |
| `form-inquiry-contract` | 6 rows | **3 rows** | Task 15's re-based form contract, routed by `data/page-map.json` `kind` rather than a hard-coded slug list |

Every other check's row count is identical; the all-family total falls by exactly those 12
rows, 277 → 265.

## Credentials and MCP

**No credential value appears anywhere in this report, in any committed file, or in
`docs/reports/system-transfer-run.log`.** The log was grepped for long token-shaped strings
after both runs; the gates print counts, not values.

| | |
| --- | --- |
| `.env` | present, mode `600`, gitignored at `.gitignore:5`, absent from `git status --porcelain` |
| Keys | **11**, by name only: `SITE_URL`, `INDEXNOW_KEY`, `GSC_CLIENT_ID`, `GSC_CLIENT_SECRET`, `GSC_REFRESH_TOKEN`, `GSC_SITE_URL`, `GA4_PROPERTY_ID`, `GA4_CLIENT_ID`, `GA4_CLIENT_SECRET`, `GA4_REFRESH_TOKEN`, `PUBLIC_FORMSPREE_ID` |
| Empty by design | `INDEXNOW_KEY` (1 of 11) — IndexNow is inactive until project 6 |
| `SITE_URL` | still the placeholder — `indexnow_submit.py` refuses on it as well as on `BSUK_RELEASE` |
| MCP block | the `bluestaffyuk` block removed from the Claude desktop config; only `gscServer` remains; the file parses as valid JSON |
| Backup | `claude_desktop_config.json.bak-20260917-022840`, beside the config |
| Old server | `~/bsuk-mcp-server` (59 MB) deleted |

Spec §9 says "nine keys"; the file holds eleven, because the GA4 group split into four keys
rather than two during Task 18. Recorded as a deviation, not a shortfall.

**Ruling on the Formspree id.** `PUBLIC_FORMSPREE_ID` holds a **public endpoint id** — it is
served to every visitor in the contact form's `action` attribute and is not a secret. It is
therefore permitted to appear in the spec, the plan and the Artifact documents where the
contract is described. It does appear in one committed generated file —
`data/quality/scorecards/uk-blue-staffy-breeders-contact-2026-09-17.json`, in the captured
form's `action` field, because the scorecard records the built page as served. That is the
same public string the visitor receives, and it is permitted on the same footing as the
spec, the plan and the Artifacts. It is **never** permitted in code, fixtures, tests, or
`.env.example`: fixtures carry `FORM_ID_FROM_ENV` in the action and the meta spec
substitutes the env value at test time, so the id sits in no hand-written file under
`tests/`, `scripts/` or `src/`. `tests/py/test_no_env_value_committed.py` allowlists this
key explicitly, with that reasoning recorded beside the allowlist. Both gates read it lazily at run time. That line holds in this report:
the id is named by key, never by value.

### Incident — two live credential values were committed in this branch

Found by the close-out spec review, after the two gate runs and after the first close-out
commit. Recorded here in full because a credential that has been committed is not fixed by
deleting it.

**What.** `.claude/skills/bsuk-indexing/SKILL.md` carried, in a worked OAuth
token-exchange example, the live values of two keys — **`GSC_CLIENT_SECRET`** and
**`GA4_CLIENT_ID`** — at lines 201, 207 and 208 (the client id in the consent URL and again
in the `curl` body, the client secret in the `curl` body). Both matched `.env` exactly. They
are named here by KEY only; neither value appears in this report, in the run log, or in any
Artifact.

**How it got here.** The file was ported from the source repo, where the same example has
always held the same literals. Mechanical re-basing changed the parrot wording and left the
credentials untouched, because no gate was looking for them: the marker gate scans for
re-base markers, the fact lint for unbacked claims, and neither has a concept of a secret.

**Commit range.** The values were present from the skills re-base —
`7a89519 skills: 25 system skills re-based into the single .claude/skills tree` — through
every commit to and including the first close-out commit `eed05a5`, i.e. the whole of the
system-transfer branch from `7a89519` onward. They are in this branch's git **history**, so
removing them from the working tree does not remove them from the repository.

**Blast radius.** The branch has **no git remote** and has never been pushed (`git remote -v`
prints nothing); nothing left this machine by way of BSUK. But the exposure is not confined
to BSUK: the identical two values sit in the **source repo's own skill file**,
`~/Downloads/CAG/.claude/skills/cag-indexing/SKILL.md`, and in thirteen further copies under
its `.claude/worktrees/` — a tracked file in a repository that has a git origin and, per the
close-out review, has been pushed to GitHub since 2026-06-28. The OAuth client is therefore
exposed well beyond this repository, and BSUK's clean local history does not make it safe.

**Fixed at.** Every literal was replaced with its `$KEY` environment reference
(`$GA4_CLIENT_ID`, `$GSC_CLIENT_SECRET`) and the section now opens by saying that every
credential is read from `.env` and must never be pasted back. Done in the commit this report
is committed in.

**Rotation — PENDING, and required.** Replacing the text does not invalidate the credential.
The **GSC OAuth client** and the **GA4 client** must be **ROTATED by the user in the Google
Cloud Console** — new client secret, and the refresh tokens re-minted against it — **before
project 6** wires up the GSC and GA4 pulls. Until that is done this item stays open. It is
carried as **Known Issue 15** in `docs/reference/session-log.md`. Rotation is the user's
action; no agent can or should perform it.

**Guards added, so this cannot recur silently.** Two new pytest files, both of which report
locations only and never the matched text:

| Guard | What it proves |
|---|---|
| `tests/py/test_no_env_value_committed.py` | no value in `.env` appears in any tracked file, in `docs/reports/system-transfer-run.log`, or in `docs/artifacts/*.html`. Values are passed to `git grep -F` as arguments, never through a shell. Four public-by-design keys are allowlisted with the reasoning recorded inline. Run: `examined 6 values; 0 tracked files contain one` |
| `tests/py/test_secret_shapes.py` | no credential-SHAPED token (Google OAuth client secret, OAuth client id, refresh token, API key, bare 32-hex) appears anywhere `marker_check.scan_roots()` looks, plus `docs/reports`, `docs/artifacts`, `data/quality/scorecards` and `tests/py/fixtures`. Catches credentials that were never in `.env`. Verified non-vacuous: a probe file containing one of each shape fires all five |

Both were confirmed to **fail first** on the unfixed tree and pass after. They are listed in
the Mechanical guards table in `docs/reference/system-registry.md`, which is generated so it
cannot rot.

## Second-run confirmation

**Identical: yes.** Both runs produced the same summary line for every gate — build 49
pages exit 0; `check:all` all-green; `1240 passed, 7 skipped`; port `applied 10,
skipped-existing 129, deferred 41, missing 0, blocked 0`; `board_gate.py index` `3 FAIL · 2
WARN`; meta `315 passed, 36 skipped`; pages `5 passed, 46 failed`; registry, baseline and
sweep unchanged. No `rebase` row was re-applied on run 2.

The one line that moved is the placeholder total at run 2's release probe, 1692 → 1695,
caused by the close-out session-log entry written between the two runs naming three of the
token strings. That prose has since been rewritten descriptively and the gate's scan set
widened; the final figure is 1698, reconciled line by line under "Fact lint and the
placeholder gate". No gate verdict, exit code or defect count changed.

## Out of scope

Restated from spec §10 so nothing below is read as an omission: components and the design
system (project 3); rewriting any page content; the marketing, email, social and competitor
agents; canvas and thumbnail scripts; GSC and GA4 data pulls; the new domain, phone number,
pagefind index and IndexNow submissions (project 6).

## Open items for later projects

Foundation's items 1 and 2 are **closed by this project**. Items 3–8 carry forward with
updated status; 9–14 are new from this port.

1. **`FORM_ENDPOINT` contract — CLOSED.** Re-based onto this repo's own fields and endpoint
   env key, routed by `data/page-map.json` `kind`. `form_contract_audit.py` is at 0
   problems; the harness rows fell 6 → 3.
2. **DUP whitelist — CLOSED.** Re-measured against BSUK's own chrome, with the
   `dup-adjacent-to-whitelist` fixture re-based on the new stems. Harness rows 42 → 33.
3. **The orphan check is blinded by the catch-all route.** `builtRoutesWithoutSource()` in
   `tests/render/lib/freshness.ts` compares built routes to source routes, and the root-level
   `src/pages/[...post].astro` matches any path, so the function cannot prove any route
   orphaned. Unchanged by this project. **Carried forward** — needs a check that reads the
   content collection rather than the filesystem.
4. **Puppy `srcset` 2x rows.** 15 blocking rows over 6 pages, unchanged. **Project 3's image
   pass.**
5. **`nav-jump-target-lands` baseline.** 18 rows over 6 pages, unchanged. Migrated in-page
   anchors, not chrome miscalculation. **Carried forward.**
6. **17 stub locations are noindexed.** 0–7 words of legacy body each. **Project 5.**
7. **Placeholders.** Now 1692 occurrences across five tokens, up from Foundation's three —
   `LICENCE_CLAIM_PLACEHOLDER` (633) and `LEGAL_CLAIM_PLACEHOLDER` (149) were added by this
   project's skill re-base and await **Lisa Bright's confirmation** of the breeder-licence
   and Lucy's-Law wording. `SITE_URL_PLACEHOLDER` and `PHONE_PLACEHOLDER` resolve at
   **project 6** launch. `BSUK_RELEASE=1 npm run check:placeholders` refuses to ship any of
   them.
8. **`schema-date-modified-present`.** 18 rows over 6 pages; needs
   `scripts/generate_page_dates.py` wired into the content pass. **Project 4.**
9. **Three carried header duplicates.** The `header-collision` FAILs listed under "Board
   system" above: two homepage headings against
   `/uk-locations/staffy-breeding-dogs-glasgow/` and one against
   `/uk-blue-staffy-puppy-buying-guide/`. Migrated copy this project may not edit.
   **Project 4.**
10. **Deferred-check id drift.** The plan named `bottom-bar-under-tabbar` and
    `analytics-double-load` as harness deferrals; both are Python page-hardening checks in
    the source repo and have no harness equivalent, so neither could be deferred. If a later
    project ports them into the harness, defer them then.
11. **Old price range in migrated copy.** `£850 to £1,200` still appears in migrated page
    bodies (`src/pages/blue-staffy-pup-sale-uk/`, `src/pages/blue-staffy-uk-breeders/` and
    siblings), against the locked £1,500 / £1,700. The fact lint enforces the locked amounts
    across `.claude/agents` and `.claude/skills`, but page bodies are content, out of scope
    here. **Project 4's content pass.**
12. **`Sharine Amelia` byline.** The migrated author byline persists in
    `src/pages/index.astro` and `src/pages/blue-staffy-uk-breeders/index.astro`, and in
    Foundation's own Artifacts. It is not a system-transfer artefact. **Project 4.**
13. **`INDEXNOW_KEY` is empty and `SITE_URL` is the placeholder.** IndexNow is ported and
    doubly guarded — it refuses without `BSUK_RELEASE=1` and again on the placeholder
    `SITE_URL`, exit 2. There is no deploy script to port: the source repo deployed by
    pushing to a host, and BSUK has no remote and no host. **Project 6** adds the real
    deploy step and fills both values.
14. **GSC and GA4 pulls are unwired.** The eight GSC/GA4 keys are in `.env` and documented in
    `docs/reference/credentials.md` by name, but no script reads them yet; `gscServer`
    remains the only MCP block. Data pulls are explicitly out of scope (§10) and belong to
    **project 6**.

## Definition of done — spec §9, as amended by §11

| # | Requirement (amended) | Verdict | Evidence |
|---|---|---|---|
| 1 | `check:all` runs parity, redirects, schema, sitemaps, placeholders and the marker gate, and passes twice | **PASS** | exit 0 on both runs; the chain also runs the agent registry; every line at 0 problems. The advisory placeholder total is 1692 on both runs' `check:all`; the +3 at run 2's release probe is this project's own close-out prose naming the tokens |
| 2 | `python3 -m pytest` green, including the ported gate tests and `test_port_manifest.py` | **PASS** | `1240 passed, 7 skipped`, identical both runs |
| 3 | `test:render:meta` green; every family examines at least one page | **PASS** | `315 passed, 36 skipped`, exit 0, both runs; three deferrals recorded with promotion conditions |
| 4 | `test:render:pages` runs to completion against the recorded Project 2 baseline with no new blocking row | **PASS** | `5 passed, 46 failed` both runs; 265 rows / 67 blocking / 198 advisory matches `render-baseline-project2.md`; `npm run baseline` 0 problems; only `dup-no-sibling-crossover` 42→33 and `form-inquiry-contract` 6→3 moved, both intended, both downward |
| 5 | `port_from_cag.py` reports `missing 0`; a second run re-applies no `rebase` row | **PASS-WITH-DEVIATION** | `missing 0, blocked 0`, `applied 10` (= the copy count) on both runs. Deviation of wording only: the script buckets rebase rows as `skipped-existing 129`, so §9's literal "`applied 0` for `rebase` rows" reads as "the 129 rebase rows stay in `skipped-existing` and `applied` never exceeds the copy count" — which both runs show |
| 6 | The homepage proving board is approved, passes `board_gate.py`, and its Artifact is built | **PASS-WITH-DEVIATION** | `data/boards/index.json` `approval.approved_at` `2026-09-16T00:00:00Z`; Artifact source `docs/artifacts/boards/index.html`. Per §11 the gate is green "except for the three carried duplicates": `3 FAIL · 2 WARN`, exit 1, all three FAILs the listed `header-collision` rows in migrated copy, down from five after Task 15 cleared the two chrome rows. The gate is not weakened |
| 7 | `.env` holds all keys; the MCP block is gone; the desktop config is valid JSON; `~/bsuk-mcp-server` no longer exists; **no credential value is committed** | **PASS-WITH-DEVIATION** | 11 keys, not §9's nine — the GA4 group split into four. `INDEXNOW_KEY` intentionally empty until project 6. Block removed, backup `claude_desktop_config.json.bak-20260917-022840`, config parses, server directory deleted. **Deviation: the Incident above.** `GSC_CLIENT_SECRET` and `GA4_CLIENT_ID` were committed in `.claude/skills/bsuk-indexing/SKILL.md` from `7a89519` through `eed05a5`; replaced with `$KEY` references in this commit; the branch has no remote, but the same values are pushed in the source repo, so **rotation in the Google Cloud Console is PENDING and required before project 6** (Known Issue 15). Two new guards (`tests/py/test_no_env_value_committed.py`, `tests/py/test_secret_shapes.py`) now prove the absence on every run |
| 8 | `docs/reports/system-transfer-gate-report.md` written and published as an Artifact, with this spec and the plan | **PASS** | this file; `docs/artifacts/bsuk-system-transfer-gate-report.html`, `bsuk-system-transfer-spec.html` and `bsuk-system-transfer-plan.html` all rebuilt by `scripts/build_spec_artifact.py` |
| 9 | Commit trailer on every commit: `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` | **PASS** | branch range `7655bd3..HEAD` (`7655bd3` is `foundation`'s tip, the cut point). `git log --oneline 7655bd3..HEAD \| wc -l` → **59**; trailer coverage **59/59** |
| 10 | (§11) The marker gate is `marker_check.py` and is at zero with no allowlist | **PASS** | `examined 233 files; 0 problems`, both runs; 418 → 0 |
| 11 | (§11) The fact lint enforces the locked facts across agents and skills | **PASS** | `tests/py/test_agent_facts.py` green within the suite |
| 12 | (§11) The form check refuses lazily rather than throwing at import | **PASS** | unset → `REFUSED …`, exit 2, `examined: 0`, one defect row; the other nine families still run |
| 13 | (§11) Deploy resolves to guarded IndexNow and pagefind; no deploy script | **PASS** | `indexnow_submit.py` exits 2 without `BSUK_RELEASE=1` and again on the placeholder `SITE_URL`; `build:release` sits behind `scripts/release_guard.sh`; documented inactive in CLAUDE.md |

**Verdict count: 10 PASS · 3 PASS-WITH-DEVIATION · 0 FAIL.** Rows 5 and 6 are recorded in
spec §11 or are arithmetic restatements of it. Row 7 is **not**: it carries a real defect
found at close-out, fixed in the tree and fully disclosed in the Incident above, but with
**credential rotation still pending on the user**. Project 2 should not be considered closed
for credential purposes until that rotation is done.
