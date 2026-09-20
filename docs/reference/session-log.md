# BlueStaffyUK Session Log and Known Issues

History and open defects. Nothing here is a rule; it is state. The source repo's log was
replaced wholesale rather than re-based — it was eighteen months of another site's build
history, and translating it would have invented a past this repo does not have.

## Project 1 — Foundation (2026-09-15/16) — COMPLETE

The Astro 6.3.8 static site, the rule packs, the Python suite and the render harness.
Full report and evidence: `docs/reports/foundation-gate-report.md`.

## Project 2 — System transfer (2026-09-16/17) — COMPLETE

Moves the site operating system — rules, agents, skills, gate scripts and reference docs —
from the source repo into this one, re-based onto a Carlisle Staffordshire Bull
Terrier breeder, with `scripts/marker_check.py` as the zero-tolerance
proof. `data/port-manifest.json` is the record of every file that crossed.
Plan: `docs/superpowers/plans/2026-09-16-system-transfer.md`.

Closed 2026-09-17 on branch `system-transfer`, 57 commits, `6c1f2c3..939033b` plus the
close-out commit, no remote and nothing pushed. Every gate was run twice with identical
results; the transcript is `docs/reports/system-transfer-run.log`. Full report and evidence:
`docs/reports/system-transfer-gate-report.md`.

Headline numbers: the marker gate went 418 → 0 (`examined 233 files; 0 problems`); the
manifest carries 180 rows (10 copy, 129 rebase, 41 deferred) and `scripts/port_from_cag.py` reports
`missing 0, blocked 0` with no rebase row re-applied on the second run; 36 agents and 53
skills in the single `.claude` tree with both registries generated and in sync; 1240 pytest
tests pass; the render meta gate is at 315 passed and the pages gate at the recorded Project
2 baseline with no new blocking row.

Credentials moved out of the MCP server and into a gitignored `.env` holding eleven keys by
name (values never printed, never committed). The `bluestaffyuk` MCP block was removed from
the Claude desktop config, which was backed up first as
`claude_desktop_config.json.bak-20260917-022840`; `~/bsuk-mcp-server` was deleted. Only
`gscServer` remains.

## Project 3 — Design system (2026-09-18/19) — COMPLETE

Gives the site a visual system of its own: a three-layer token file, the L1 badge mark and
its four lockups, and a thirteen-component kit picked by the user from five variants each on
a published design canvas. Nothing of the kit is mounted on a real page yet except the shell
— project 4 does that — so the site's content gates are unchanged by design.
Plan: `docs/superpowers/plans/2026-09-18-design-system.md`.
Spec: `docs/superpowers/specs/2026-09-18-design-system-design.md`, approved and amended seven
times during execution; §11 is where every in-flight decision is recorded.

Closed 2026-09-19 on branch `design-system`, 61 commits from `e049f55` including the
close-out, the working-rule-11 commit and the close-out review's fixes, no remote and nothing
pushed. Every gate was run twice with identical results; the transcript is
`docs/reports/design-system-run.log`, and the two halves are proven identical as multisets of
time-normalised lines. Full report and evidence:
`docs/reports/design-system-gate-report.md`.

Headline numbers: 51 pages built; 66 design tokens with 20 contrast pairs asserted at AA;
thirteen kit components and thirteen owner picks; the canvas went 65 → 91 → 39 boards as the
mobile and tablet rows arrived and the losing variants were pruned; the `/design-canvas/`
route was replaced by `/kit-preview/`, which is a measured target page rather than a hidden
one; 1353 pytest tests pass; the render meta gate is at 324 passed with the three formerly
deferred checks promoted and no `DEFERRED` line; the pages gate is at the recorded project 3
baseline, `8 passed, 46 failed`, with blocking rows 67 → 58 and no new blocking row anywhere.
The fall is the image pass: `img-srcset-within-2x` went from 15 rows to 6, and the puppy
page's Lighthouse Performance rose 98 → 100 with LCP 2277 ms → 1516 ms. No Lighthouse category
score fell on any of the five page types. The placeholder total fell 1698 → 1605.

A correction to an in-flight report: during Task 16 the controller reported the pages gate as
"0 failed". That was a stale-scorecard artefact. The true figure is 46 failing pages,
unchanged from project 2.

Three Artifacts were published and their URLs recorded in `data/design/artifacts.json`: the
design canvas, the picks board, and the Design System — the last replacing the spec's original
draft of a prompt pack, because the artifact type's own format is a token-and-component
document rather than a set of prompts.

## Known Issues

Seeded from the Foundation gate report's "Open items" 1–8 and extended by projects 2 and 3.
Items 1 and 2 are closed by project 2 and item 4 by project 3; 3 and 5–8 are carried forward
with their owning project; 9–14 are new from the system transfer, 15–16 were added after it,
and 17–25 are new from the design system.

1. **`FORM_ENDPOINT` contract — CLOSED by project 2.** The contact-page form contract was
   re-based onto this repo's own fields and endpoint env key. See
   `scripts/form_contract_audit.py` and `tests/render/checks/form.ts`.
2. **The DUP whitelist — CLOSED by project 2.** The duplicate-content whitelist was
   re-based onto this site's own built pages, together with the fixture that depends on
   its stems. See `scripts/dup_content_audit.py`.
3. **The orphan check is blinded by the catch-all route.** `builtRoutesWithoutSource()` in
   `tests/render/lib/freshness.ts` compares built routes to source routes, and the
   root-level `src/pages/[...post].astro` matches any path — so while it exists the
   function cannot prove any route orphaned, static pages included. The mtime comparison is
   the only remaining freshness signal. A real answer needs a check that reads the content
   collection rather than the filesystem. **Carried forward.**
4. **Puppy `srcset` 2x rows — CLOSED by project 3.** The puppy photos moved to `astro:assets`
   with a bounded `srcset`. `img-srcset-within-2x` fell from 15 blocking rows over 6 pages to
   **6 rows over 3 pages**, and the puppy page's Lighthouse LCP fell 2277 ms → 1516 ms with
   Performance 98 → 100 — the two numbers moved together, as Foundation predicted. The six
   remaining rows are two plain `<img>` tags in migrated WordPress body copy on three pages,
   named in `docs/reports/design-system-gate-report.md`; they are not kit output and belong
   to **project 4**'s content pass.
5. **`nav-jump-target-lands` baseline.** 18 rows over 6 pages remain after the shell fix.
   `--hdr` is measured from the header (`--hdr-measured`), with the media query kept as the
   no-JS fallback, so the remaining rows are migrated in-page anchors rather than chrome
   miscalculation. **Carried forward.**
6. **17 stub locations are noindexed.** They carry 0–7 words of legacy body.
   **Project 5** writes them; `scripts/sitemap_check.py` keeps them out of the shards until
   then.
7. **Placeholders.** Five stand-in tokens are still in the tree. This entry describes them
   rather than naming them: `docs/reference` is itself a placeholder scan root, so spelling
   a token here would register as a permanent hit and the gate would never reach zero on
   launch day. The exact token names and counts are in
   `docs/reports/system-transfer-gate-report.md`, which is not a scan root.
   The site-URL stand-in and the phone stand-in resolve at **project 6** launch; the
   form-endpoint stand-in is already clear, because the build reads the endpoint from `.env`.
   The two legal-claim stand-ins — the breeder-licence claim and the Lucy's-Law claim — were
   added by project 2's skill re-base and await **Lisa Bright's** confirmation of the
   wording. `BSUK_RELEASE=1 npm run check:placeholders` refuses to ship any of them
   (exit 1, confirmed).
8. **`schema-date-modified-present`.** 18 rows over 6 pages; needs
   `scripts/generate_page_dates.py` wired into the content pass, which arrives with
   **project 4** — the same project that gives pages a real edit history for sitemap
   `lastmod`.

9. **Three carried header duplicates.** `board_gate.py index` reports three
   `header-collision` FAILs in migrated copy: the homepage's *Meet the Proud Parents of Our
   Blue Staffy Puppies* and *Our Commitment to the Health of Our Blue Staffy Puppies*
   against `/uk-locations/staffy-breeding-dogs-glasgow/`, and *How to Buy Your Blue Staffy
   Puppy* against `/uk-blue-staffy-puppy-buying-guide/`. Down from five; the two chrome rows
   cleared with the harness re-base. **Project 4.**
10. **Deferred-check id drift.** `bottom-bar-under-tabbar` and `analytics-double-load` are
    Python page-hardening checks in the source repo, not render-harness checks, so they could
    not be deferred in `tests/render/targets.json`. Defer them if a later project ports them
    into the harness.
11. **Old price range in migrated copy.** A pre-migration price band, below the locked
    £1,500 / £1,700, persists in several migrated page bodies (see the project-2 gate
    report, open item 11, for the exact pages). The fact lint covers `.claude/agents` and
    `.claude/skills` only; page bodies are content. **Project 4.**
12. **`Sharine Amelia` byline.** The migrated author byline persists on the homepage and the
    breeders page. **Project 4.**
13. **`INDEXNOW_KEY` empty, `SITE_URL` still the placeholder.** IndexNow and pagefind are
    ported and guarded (`scripts/indexnow_submit.py` exits 2 without `BSUK_RELEASE=1` and again on
    the placeholder; `build:release` sits behind `scripts/release_guard.sh`). There is no
    deploy script — the source repo pushed to a host and this repo has none. **Project 6.**
14. **GSC and GA4 pulls are unwired.** The eight keys are in `.env` and named in
    `docs/reference/credentials.md`, but no script reads them yet. **Project 6.**

15. **Two live credential values were committed in this branch — ROTATION PENDING.**
    `.claude/skills/bsuk-indexing/SKILL.md` carried the live values of `GSC_CLIENT_SECRET`
    and `GA4_CLIENT_ID` inside an OAuth token-exchange example, from the skills re-base
    (`7a89519`) through the first close-out commit (`eed05a5`). The literals were replaced
    with `$GSC_CLIENT_SECRET` / `$GA4_CLIENT_ID` at the close-out, but they remain in this
    branch's git history. The branch has **no remote** and was never pushed; however the
    identical values are in the source repo's own indexing skill, which is tracked and
    pushed to its GitHub origin, so the OAuth client is exposed regardless of BSUK's local
    history.
    **Action required by the user: rotate the GSC OAuth client and the GA4 client in the
    Google Cloud Console — new client secret, refresh tokens re-minted — before project 6
    wires up the GSC and GA4 pulls.** No agent can do this. Two guards now prove the absence
    on every run: `tests/py/test_no_env_value_committed.py` (every `.env` value against all
    tracked files, the run log and the Artifacts) and `tests/py/test_secret_shapes.py`
    (credential shapes across the marker gate's roots plus reports, artifacts, scorecards and
    fixtures). Full account: `docs/reports/system-transfer-gate-report.md` § Credentials and
    MCP → Incident. **Open until rotated.** 2026-09-18: the source repo's working copy and
    its legacy skill file were scrubbed to env refs and committed locally (not pushed);
    rotation still pending.

16. **The breeder has relocated: Carlisle, Cumbria, England.** Confirmed by
    the user 2026-09-18 during the build 3 brainstorm, as a full relocation of the business
    and the website. Address is town-level only (Carlisle, Cumbria) until the breeder says
    otherwise. Everything that named the old city was wrong: the homepage and page
    copy, `data/settings.json`, the schema `address` / `areaServed`, the fact lint's locked
    geography in `tests/py/test_agent_facts.py`, agents and skills, and
    `/uk-locations/staffy-breeding-dogs-glasgow/`, which becomes an outreach page rather
    than the home base and keeps its URL. **Build 3** carried the new city in the logo
    lockups and tokens only; **build 5** re-plans the 28 locations around
    Carlisle (Cumbria, the Borders, the North West and North East are now the near ring).
    One strand of this debt was machine-readable and easy to miss: the form contract's
    `PUPPY_OPTION` constant in `scripts/form_contract_audit.py`, and the matching
    `<option>` value and visible label in `src/components/ContactForm.astro`, named the old
    city in a collection choice — so the gate *required* the wrong geography of
    every page it audited in full, and the shipped contact page offered a collection point
    the breeder had left.

    **Status 2026-09-19 (project 4 Task 6): settings, schema, the instruction tree and the
    form contract are done.** `data/settings.json` `address` is
    `{city: Carlisle, region: Cumbria, country: GB}` — no street, no postcode, no
    coordinates, because the breeder has not supplied them; `src/components/Schema.astro`
    emits only the fields that are there and no `geo` node, and `scripts/schema_check.py`
    accepts an address without a street or a postcode while blocking one that states a
    field it has nothing to put in. `PUPPY_OPTION` is now `waiting-list`, the option
    `src/components/kit/ContactFormKit.astro` builds, and
    `src/components/ContactForm.astro` emits the same set from the same data, which also
    closes Known Issue 22. Every instruction file under `.claude/`, `CLAUDE.md`, `rules/`
    and `docs/reference/` names Carlisle, and the fact lint bans the old city outright,
    allowing it only on a line carrying the outreach page's slug or this issue's number.
    **Page bodies and their ported schema follow per page in Tasks 7–18** — the eleven rich
    pages and the blog are rewritten one at a time and are not edited ahead of their task,
    so the old city is still in the generated page bodies until each is rebuilt.
    **3 of 12 rebuilt (Task 7, `/privacy-policy-uk/`, 2026-09-19; Task 8,
    `/thank-you-blue-staffy-puppies-journey/`, and Task 9,
    `/uk-blue-staffy-breeders-contact/`, both 2026-09-20).** None of the three carries the
    old city anywhere: every body is written fresh, and the legacy schema graph that
    hard-coded a street address, a postcode and coordinates for the former city is gone with
    them — `BaseLayout` now emits the `WebPage` node from `data/page-dates.json` instead, and
    the contact page emits its own `ContactPage` and `FAQPage` nodes and nothing else. Both
    new pages drop the migrated body's link to that city's breeding-dogs page, and the
    contact page drops the "Our Location" paragraph built on the old address, each recorded
    with its reason in the board record's `dropped`; the by-appointment-only fact itself is
    kept. 9 page bodies to go.

17. **There is no query-augmentation skill.** `.claude/skills/bsuk-location-page-builder/SKILL.md`
    was rebuilt in project 3 around a per-city competitor scan, and it names the
    query-augmentation step — expand the primary keyword into the real questions before
    writing, mirror the strongest six into the FAQ — while recording that no skill performs it.
    Today it is done by hand or not at all. **Project 5** needs one before it builds 28 city
    pages from that skill.
18. **The hero lede is clamped to two lines, and the copy must fit it.** Design rule 10 clamps
    the lede and `scripts/measure_canvas_heights.mjs` records `lede_overflow`, which the test
    requires to be zero — so copy needing a third line fails the build rather than being
    silently truncated by the clamp. Measured at zero today at 1024, 1100 and 1280. It is a
    standing constraint on every hero **project 4** writes.
19. **`Button.kind` keeps all five treatments — AWAITING THE USER'S CONFIRMATION.** The prune
    deleted every other variant prop, but `Button` kept five treatments renamed as `kind`
    (primary, outline, inverse, submit, text) on the reasoning that a page needs more than one
    button and these are five jobs rather than five styles. That is a judgment made during
    execution and the user has not confirmed it. Deleting an unwanted treatment is a one-line
    registry change plus its fixtures and is cheapest **before project 4** mounts buttons on
    real pages.
20. **`data/page-dates.json` is generated but unwired.** `npm run dates` writes it from git
    history, and `/kit-preview/` is its only consumer — it reads the file for its `WebPage`
    `dateModified` rather than calling `new Date()`. The 18 `schema-date-modified-present` rows
    in Known Issue 8 are exactly the real pages that do not read it yet. **Project 4** wires it
    into the content pass and into sitemap `lastmod`.
21. **The separator dot misses AA by one hundredth.** Two advisory `a11y-text-contrast-aa` rows
    on `/kit-preview/` at 768 and 1280: the middle-dot separator measures 4.49:1 where AA wants
    4.50:1. Decorative, but a real row; the fix is one token step darker, with the pair added to
    `data/design/contrast.json` so the token test guards it thereafter. **Project 4.**
22. **The kit contact form reports one missing screening option.** `form-inquiry-contract`
    reports one advisory row at all three viewports on `/kit-preview/`: the puppy select is
    missing the collection option that `scripts/form_contract_audit.py`'s `PUPPY_OPTION`
    constant requires. The kit form is right and the constant is wrong — the option names a
    collection point the breeder has left (Known Issue 16). **Closed 2026-09-19** by project 4
    Task 6: the constant is `waiting-list`, the option the kit form builds, and the legacy
    form now emits the same set from the same data.
23. **Page weight of the inline lockups.** The header inlines the horizontal lockup and the
    footer the mono one, about 15 KB of SVG each, and the mark sprite adds about 3 KB per
    document; the built homepage is roughly 163 KB, of which about 52 KB is inline SVG. It cost
    no Lighthouse category on project 3's sweep, but it is paid on every page and shrinks with
    nothing. If it needs to come back, the lockups can become `<use>` references into the sprite
    the mark already emits, at the cost of one request. Recorded, not yet a defect.
24. **The fonts are not vendored.** Fraunces and Source Sans 3 load from Google Fonts, which is
    why the Design System artifact's font list is empty (spec §11 amendment 7c). That is a
    third-party request on every page and a privacy consideration. **Project 6** should decide
    whether to self-host before the site is public.
25. **`scripts/render_baseline.py`'s default report is now project 3's.** Its `REPORT` constant
    points at `docs/reports/render-baseline-project3.md`; the project 2 file is a published
    record of a finished run and is never regenerated. Whoever opens **project 4** must repoint
    the default at a new project 4 baseline file, or `npm run baseline` will keep judging
    project 4's scorecards against project 3's table.

26. **Existing images and videos must be reused with their URLs intact.** Every file under
    `public/images/` and the YouTube embeds in `data/settings.json` already rank; projects 4–6
    reuse them first and never rename, delete or re-encode a served file (CLAUDE.md working
    rule 11, breeder 2026-09-19). Project 3 briefly deleted the two legacy logo rasters
    (`blue-staffy-uk-official-logo0.png`, `blue-staffy-uk-header-logo-88.webp`) when the SVG
    lockups replaced them; both are restored at their original paths and stay served even
    though no template references them. **Standing constraint for projects 4–6.**

