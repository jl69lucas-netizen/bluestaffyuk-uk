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

## Project 4 — Page rebuilds (2026-09-19/22) — COMPLETE

Rebuilds every rich page on the project 3 kit, each written fresh from an approved outline
through its own page board, and fixes the facts the migration carried wrong.
Plan: `docs/superpowers/plans/2026-09-19-page-rebuilds.md`.
Spec: `docs/superpowers/specs/2026-09-19-page-rebuilds-design.md`, amended eleven times during
execution; §9 is where every in-flight decision is recorded.

Closed 2026-09-22 on branch `page-rebuilds`, cut from `foundation` at `63a7b12`, 120 commits
including step 0 (`f94baee`, the video copy that described silent puppy clips as a voice, a
tour and a guide) and the close-out, merged into `foundation` with `--no-ff`; no remote and
nothing pushed. Every gate was run twice; the transcript is
`docs/reports/page-rebuilds-run.log`. One line drifted between the runs — pytest's two
real-scorecard baseline tests skip until `docs/reports/render-baseline-project4.md` has a generated block,
and run 1's pytest ran before run 1 filled it — and the cause is removed by committing the
filled block. Full report and evidence: `docs/reports/page-rebuilds-gate-report.md`.

Headline numbers: twelve pages rebuilt from twelve approved boards (URLs in
`data/design/artifacts.json` `boards`); five new kit components (dial, sheet, strip, data table,
video embed — eighteen in all), the first three on every rebuilt page and the three hubs; rule
15's verbatim set carried on nine pages, 507 elements, 181 changed with reasons, 0 missing;
the review-slot stand-in at 0 — every review slot filled from the three real reviews; render blocking
rows **58 → 6**, none on a rebuilt page (the six are Known Issue 31's two routes);
`schema-date-modified-present` 18 → 0; `img-srcset-within-2x` 6 → 0; `scripts/final_page_audit.py`
12 FAIL → 0 FAIL; AEO 38 baseline-only FAIL pages → 0; pytest 1355 → 1703 passed; render meta
324 → 370 passed. Lighthouse (warm median of 3, mobile and desktop, fourteen pages): 100 in all five categories everywhere except the thank-you page's SEO 69 (`noindex` by design), the breed guide's Best Practices 96 (Known Issue 38), the location route's SEO 92 (migrated link text) and three mobile Performance 99s — the blog hub's, the one fall against project 3, is TBT variance. Working rules 12–16 were given during the build; rules 10–11 (project 3's
close) were applied to real pages for the first time.

Definition of done: 4 PASS, 1 PASS-WITH-DEVIATION, 1 DEVIATION (the trailer, Known Issue 37),
1 FAIL (partial) — the former city is gone from every rebuilt page, settings, schema and the
form, but not from the puppy and location pages this build gave the shell only (Known Issue 16,
build 5). **Next: project 5 — the 28 location pages, the comparison cluster and the two new
blog posts.**

## Known Issues

Seeded from the Foundation gate report's "Open items" 1–8 and extended by projects 2 and 3.
Items 1 and 2 are closed by project 2 and item 4 by project 3; 3 and 5–8 are carried forward
with their owning project; 9–14 are new from the system transfer, 15–16 were added after it,
17–26 are new from the design system, and 27–38 are new from the page rebuilds. Project 4
closed 8, 9, 11, 12, 20, 22, 25, 28 and 29.

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
   **2026-09-22 (project 4 close): 3 rows on 1 page** — the rebuilt pages carry none; what is
   left is `/uk-locations/blue-staffy-puppies-uk/`'s `#Staffy-adoption` (Known Issue 31). Build 5.
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
   (exit 1, confirmed). While the phone stand-in is in `data/settings.json`,
   `scripts/final_page_audit.py` exempts `phone_in_footer` on every page with this entry as
   its printed reason (2026-09-22); the exemption reads the setting, so it lapses on its own
   the run after a real number lands.
8. **CLOSED 2026-09-22 (project 4) — `schema-date-modified-present` 18 → 0.** Was: 18 rows over 6 pages; needs
   `scripts/generate_page_dates.py` wired into the content pass, which arrives with
   **project 4** — the same project that gives pages a real edit history for sitemap
   `lastmod`.

9. **Three carried header duplicates. CLOSED 2026-09-20 (project 4 Task 18).**
   `board_gate.py index` reported three `header-collision` FAILs in migrated copy: the
   homepage's *Meet the Proud Parents of Our Blue Staffy Puppies* and *Our Commitment to the
   Health of Our Blue Staffy Puppies* against `/uk-locations/staffy-breeding-dogs-glasgow/`,
   and *How to Buy Your Blue Staffy Puppy* against `/uk-blue-staffy-puppy-buying-guide/`.
   All three are gone from the rebuilt homepage, each reworded under working rule 15 with its
   reason recorded in `data/boards/index.json` `verbatim.changed`: the first two keep every
   word up to the colliding five-word tail (*…of This Litter*, *…of Every Puppy We Raise*),
   and the third keeps the four words that carry the promise (*How to Buy Your Puppy, Step by
   Step*), because every nearer wording collided too. `board_gate.py index` is at **0 FAIL**
   against 50 live pages, header-collision 0.
10. **Deferred-check id drift.** `bottom-bar-under-tabbar` and `analytics-double-load` are
    Python page-hardening checks in the source repo, not render-harness checks, so they could
    not be deferred in `tests/render/targets.json`. Defer them if a later project ports them
    into the harness.
11. **CLOSED 2026-09-22 (project 4).** The old band is 0 times on every rebuilt page, listed in
    each record's `dropped.prices`. Was: **Old price range in migrated copy.** A pre-migration price band, below the locked
    £1,500 / £1,700, persists in several migrated page bodies (see the project-2 gate
    report, open item 11, for the exact pages). The fact lint covers `.claude/agents` and
    `.claude/skills` only; page bodies are content. **Project 4.**
12. **CLOSED 2026-09-22 (project 4).** The old byline is on no built page; it is in the
    homepage's and breeders page's `dropped.names`. Was: **`Sharine Amelia` byline.** The migrated author byline persists on the homepage and the
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
    **4 of 12 rebuilt (Task 7, `/privacy-policy-uk/`, 2026-09-19; Task 8,
    `/thank-you-blue-staffy-puppies-journey/`, Task 9,
    `/uk-blue-staffy-breeders-contact/`, and Task 18, `/`, all 2026-09-20).** None of the
    four carries the old city anywhere: every body is written fresh, and the legacy schema
    graph that
    hard-coded a street address, a postcode and coordinates for the former city is gone with
    them — `BaseLayout` now emits the `WebPage` node from `data/page-dates.json` instead, and
    the contact page emits its own `ContactPage` and `FAQPage` nodes and nothing else. Both
    new pages drop the migrated body's link to that city's breeding-dogs page, and the
    contact page drops the "Our Location" paragraph built on the old address, each recorded
    with its reason in the board record's `dropped`; the by-appointment-only fact itself is
    kept. The homepage is the loudest of the four: the migrated body named the old city three
    times — as the home city in the delivery list, as where the puppies were socialised, and
    in the FAQ lede — plus a landmark in it, and the Google Maps iframe at the foot encoded
    the old street, postcode and coordinates in its URL. All of it is gone, each strand
    logged with its reason in `dropped.names`, `dropped.text` and `dropped.embeds`, and the
    FAQ lede is carried under rule 15 with the city clause removed rather than re-pointed
    (`verbatim.changed`). The one surviving reference anywhere on the rebuilt page is the
    href of `/uk-locations/staffy-breeding-dogs-glasgow/`, whose URL rule 11 keeps and whose
    anchor on this page names our breeding dogs rather than a town.
    **8 page bodies to go.**
    **2026-09-22 (project 4 close): all twelve rebuilt pages carry the former city 0 times.**
    What is left is outside project 4's rewrite scope and is **build 5**'s: the meta
    descriptions and hub copy of `/available-puppies/` and its six puppy pages
    (`src/pages/available-puppies/index.astro`, `[slug].astro`, `src/components/PuppyList.astro`),
    `/uk-locations/` (`src/pages/uk-locations/index.astro`), `/search/` (two
    `data/page-map.json` titles), and the 28 location bodies. Spec §7.3's literal grep is
    therefore not yet 0; the gate report records it as the one partial FAIL.

17. **There is no query-augmentation skill.** `.claude/skills/bsuk-location-page-builder/SKILL.md`
    was rebuilt in project 3 around a per-city competitor scan, and it names the
    query-augmentation step — expand the primary keyword into the real questions before
    writing, mirror the strongest six into the FAQ — while recording that no skill performs it.
    Today it is done by hand or not at all. **Project 5** needs one before it builds 28 city
    pages from that skill. **Closed 2026-09-23** by `.claude/skills/bsuk-query-augmentation/SKILL.md`,
    `scripts/query_augment.py` and the gate `scripts/query_coverage_check.py` (in `npm run check:all`).
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
20. **CLOSED 2026-09-22 (project 4).** `prebuild` runs `scripts/generate_page_dates.py`, `BaseLayout`
    emits `dateModified` from it, and `generate_page_dates.py --check` is green. Was: **`data/page-dates.json` is generated but unwired.** `npm run dates` writes it from git
    history, and `/kit-preview/` is its only consumer — it reads the file for its `WebPage`
    `dateModified` rather than calling `new Date()`. The 18 `schema-date-modified-present` rows
    in Known Issue 8 are exactly the real pages that do not read it yet. **Project 4** wires it
    into the content pass and into sitemap `lastmod`.
21. **(2026-09-22: now also on `/thank-you-blue-staffy-puppies-journey/` and
    `/uk-blue-staffy-breeders-contact/`, through C-UT1's inline dot — 6 advisory rows on 3 pages;
    still open, build 5.)** **The separator dot misses AA by one hundredth.** Two advisory `a11y-text-contrast-aa` rows
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
25. **CLOSED 2026-09-22 (project 4 close-out audit) — `scripts/render_baseline.py`'s default
    report is project 4's.** `REPORT`, `tests/py/test_render_baseline.py`'s `REAL_REPORT`,
    `npm run baseline` and `scripts/health-sweep.sh` all name
    `docs/reports/render-baseline-project4.md`, which exists as a skeleton with the two
    generated-block markers and no numbers — Task 19 fills it. Until then the two
    real-scorecard tests skip (an empty block is "not run yet", not drift) and the sweep
    warns. `--out` now creates a missing report, `--check` on a missing one exits 1 instead of
    crashing, and the plan's Task 19 command no longer combines `--out` with `--write` (they
    are one option; argparse read the pair as a second `--out` with no value). Projects 2's
    and 3's files stay as published.

26. **Existing images and videos must be reused with their URLs intact.** Every file under
    `public/images/` and the YouTube embeds in `data/settings.json` already rank; projects 4–6
    reuse them first and never rename, delete or re-encode a served file (CLAUDE.md working
    rule 11, breeder 2026-09-19). Project 3 briefly deleted the two legacy logo rasters
    (`blue-staffy-uk-official-logo0.png`, `blue-staffy-uk-header-logo-88.webp`) when the SVG
    lockups replaced them; both are restored at their original paths and stay served even
    though no template references them. **Standing constraint for projects 4–6.**

27. **No `uploadDate` for any VideoObject — no file in this repo holds one.** Project 4 Task 12
    mints a `VideoObject` on each of the four rebuilt pages that carry a YouTube embed (the
    homepage's three ids, `/blue-staffy-uk-breeders/`, `/buy-staffy-puppies-for-sale-uk/` and
    `/uk-staffordshire-bull-terrier-guide/`), built from the record's own `video` block through
    `src/lib/video.ts` so the schema and `video-sitemap.xml` describe one id in one spelling.
    Google wants an `uploadDate` for a video rich result and **none is written**, because the
    only two dates available would both be inventions: the migrated theme's own
    `VideoObject.uploadDate` is the old site's markup rather than a fact this repo keeps (the
    same reasoning that removed "since May 2025" from the about page's video caption at
    1c500e5), and `data/page-dates.json` records when the PAGE changed, which says nothing
    about when the footage was published. `scripts/schema_check.py` accepts the node without
    one — it blocks five specific defects and a missing optional field is not among them — so
    this is a rich-result gap rather than a gate failure. **Closes when the breeder supplies
    the real upload dates from the YouTube channel**, which is a two-minute read of the
    channel's video list and cannot be derived from anything on disk.

28. **RESOLVED 2026-09-21 — the hero ceiling was a 1280 measure applied from 1024.** At 1024
    the legacy `split` hero's two-line `.lede` clamp hid **198px of `/` and
    `/privacy-policy-uk/`, 165px of `/uk-blue-staffy-breeders-contact/` and 99px of
    `/thank-you-blue-staffy-puppies-journey/`** — three to six lines of each page's own
    opening sentence — and the hero's `.container.inner` ran past its box by **41px on `/`,
    45px on `/buy-blue-staffy-puppies-uk/` and 12px on `/buy-staffy-puppies-for-sale-uk/`**,
    far enough on the first two to end 17px and 21px inside the section below. One cause: the
    copy column is narrower at 1024 than at 1280, so the same words take more lines, and the
    band was not allowed to grow. Not a copy defect — the same copy fits at 1280 — and the H1
    that grows is in the page's VERBATIM SET, so it cannot be shortened to fit a band.
    **The breeder's ruling (2026-09-21): the band gives way below 1280.** `max-height: 450px`
    and the lede's line-clamp are now scoped to `min-width: 1280px`; the 390 floor, the type
    step-down and the photo column's absolute cap stay on from 1024, so a hero still reads as
    a hero and its photograph still cannot set its height. Recorded as spec §9 amendment 10.4
    sub-note. Measured after, on `/`, the listing, why-us, privacy, thank-you and contact at
    1024 / 1100 / 1280: **0 hidden copy, 0 clipping and 0 overlap with the next section at
    every width**, and 390–450 held at 1280 on all six. The harness now asks the same
    question: `scripts/measure_canvas_heights.mjs` records `content_below` and `next_overlap` (its
    three older figures were all taken INSIDE the hero, which is why this was found by hand),
    and the band assertion applies only at 1280 while the overlap assertion applies at all
    three widths.
    **What is left, deliberately, is at 1280 only.** The two-line clamp is how the 390-450
    band is kept there, so on the four pre-rule-16 pages it still hides the tail of a long
    lede at that width — measured **165px on `/`, 132px on `/privacy-policy-uk/` and
    `/uk-blue-staffy-breeders-contact/`, 66px on `/thank-you-blue-staffy-puppies-journey/`**.
    That is unchanged from before the ruling rather than introduced by it, and it is a COPY
    length to settle when each of those four is rebuilt against its own rule-16 board, not a
    second release of the ceiling: the lede is written fresh under working rule 15 and can be
    cut to two lines, which the verbatim H1 beside it cannot.
    **Residual CLOSED 2026-09-22**, with the four rule-16 rebuilds (H-HM2/C-HM2 on `/`, H-UT1
    on privacy, H-UT1/C-UT1 on thank-you and contact). Each page's own lede was rewritten to
    two lines at every desktop width, and the sentences it gave up moved into the hero
    section's own paragraph beneath the band rather than being dropped (working rule 6).
    Measured on `dist/`, `.kit-hero` height / lede overflow at 1024 · 1100 · 1280:
    `/` 451/0 · 450/0 · 450/0; `/privacy-policy-uk/` 422/0 · 450/0 · 450/0;
    `/thank-you-blue-staffy-puppies-journey/` 422/0 · 450/0 · 450/0;
    `/uk-blue-staffy-breeders-contact/` 422/0 · 450/0 · 450/0 — two lede lines at all three
    widths on all four, no clipping, and no overlap with the section below.

29. **RESOLVED 2026-09-21 — `/blog/` is kept as the legacy archive and exempted by name.**
    The built page is `noindex, nofollow` with its canonical on `/blue-staffy-blog-guides/`,
    the real guides hub rebuilt at `5ed62ed`, and it was failing the rich-page floor
    (`all_six_levels`, `min_h5_5`, `min_h6_5`, `faqpage_present`). **The breeder's ruling: keep
    the route** — `public/_redirects` sends `/category/*` to it with a 301, and retiring it
    would turn every category URL the previous site served into a 404 — **and exempt it by
    name.** A de-indexed redirect target could satisfy those four only by inventing eleven
    sub-points and three questions it does not have, which is a page written for a gate and
    schema for content that is not there. `ARCHIVE_EXEMPT` in `scripts/final_page_audit.py`
    carries the slug and the reason, and the audit prints both; the exemption is by SLUG
    rather than by profile, because the guides hub is on the same profile and the four checks
    are exactly right there. `--blog` now reports 3 PASS, 0 problems. **Project 5 may retire
    the route** once its two new posts land and the archive carries nothing the hub does not.

30. **The H-GD3 hero's photo column pins two pages at exactly 450px.** `.pic` in the
    interior-guide panel arrangement carries `aspect-ratio: 3 / 4`, and at 1280 that makes the
    photo 299px tall, which with the panel's 32px padding puts
    `/uk-blue-staffy-puppy-buying-guide/` and `/uk-staffordshire-bull-terrier-guide/` at
    **exactly 450px** — the very top of rule 10's 390-450 band, with the buying guide's inner
    content already 3px past its own box. `/blue-staffy-health-uk/`, the third H-GD3 page, sits
    at 444 because its copy column is shorter. Nothing is clipped today and the band is met,
    but two of the three pages have zero headroom: one extra line of H1, eyebrow or aside on
    either of them puts the arrangement over the ceiling, which is how the defects amendment
    10.4 lists were found. Known Issue 28's ruling relieves this BELOW 1280 — the band may now
    grow there, so an extra line at 1024 is absorbed rather than clipped — and leaves it
    exactly as it was AT 1280, where the ceiling still holds and these two have nothing spare.
    **Closes when the aspect is budgeted rather than fixed** — the photo box sized from the
    space the copy leaves, not the other way round.

31. **Two blocking rows on the two data-driven routes (corrected 2026-09-22).**
    `test:render:pages` fails six rows on two pages project 4 did not rebuild, and the two are
    DIFFERENT failures — this entry first said both were SEM, and the close-out audit's run
    shows otherwise:
    - `/available-puppies/` — `[SEM] 1 skipped heading level(s): H1→H3 at "Roman"` at all three
      viewports: the card grid opens each puppy at H3 under the page's H1 with no H2 between
      them (from `data/puppies.json`).
    - `/uk-locations/blue-staffy-puppies-uk/` — `[NAV] 1 of 2 in-page links land outside` the
      landing band, at all three viewports, first `#Staffy-adoption` (at 2903px / 3436px /
      3439px): the migrated body's own anchor target sits outside the band the sticky header
      leaves. It is not a heading skip.
    Both are inherited rather than introduced (identical at `7b5be27`), and they are the only
    rows standing between `test:render:pages` and a clean exit — every one of the twelve
    boarded pages passes. **Project 5's puppy and location cluster owns both routes** and
    closes them: the missing H2 (or cards opened at H2) on the first, the anchor target on the
    second.

32. **606px of horizontal overflow at 375 on the contact board-preview route.** `NAV.kit-strip`
    inside `.bp-targets` on `/board-preview/uk-blue-staffy-breeders-contact/` is 933px wide in
    a 375px viewport, and the page scrolls sideways. It is the mobile section STRIP specimen
    rendered over its six stub targets — scaffolding the preview route builds so the breeder
    can see the arrangement, not a section of any page. Verified identical at `7b5be27`. The
    contact page itself has zero horizontal overflow at 375, and so does every counter and
    hero rendering on that route. PREVIEW-ONLY, and it closes when the specimen's target row
    is given a scroller of its own rather than being allowed to set the page's width.

33. **Two approved picks render as their DEGRADED arrangements, faithfully.** H-HM2 on `/` is
    "four-photo mosaic above the copy, figure tiles beneath it", but the homepage record's
    `top` names ONE photograph and no ledge figures, so the hero renders — on the board the
    breeder approved and on the page — as the single photo beside centred copy with no ledge:
    `Hero` degrades a mosaic of fewer than two tiles rather than inventing one, and a ledge
    whose data the record did not supply renders nothing. The same is true of H-UT1 on all
    three utility pages (one photograph each). And those three pages all picked H-UT1, and
    thank-you and contact both picked C-UT1, so rule 16's "no two pages share the same hero
    layout or counter strip" is not met between them; their `refresh` notes still describe
    the H-UT2/H-UT3 arrangements they did not pick. Separately, C-UT1 (`tiles: inline`,
    `label: above`) printed its inter-figure `·` on a line of its own under the first figure,
    because the dot was inside a column-flex tile — FIXED 2026-09-22 in `CounterStrip`: the dot
    is positioned out of flow in the gap after its tile (verified at 375 / 768 / 1280 on
    thank-you, contact and the contact board preview; hidden below 720px as before).
    **Closes with a breeder decision**: more photographs and ledge rows on the four records
    (and new refresh notes), or new picks. The page renders what was approved until then.

34. **Per-slug evidence budgets for the twelve rebuilt pages (2026-09-22).**
    `scripts/evidence_audit.py --all` raised term-budget ERRORs on every rebuilt page, and not
    because the writing is stuffed: working rule 15 requires each page's migrated H1, keyword
    H2/H3s, their opening paragraphs and its FAQ questions word for word, the page shell repeats
    the approved headings in the section dial, strip, sheet and table of contents, and the
    approved tables and counters state the head terms in their own rows. The page-type ceilings
    in `data/quality/evidence-budgets.json` are uncalibrated proposals re-based from the source
    repo (`calibrated: null`) and were never sized for any of that. So each rebuilt slug now has
    a `budgets_by_slug` entry, MEASURED on `dist/`: budget = carried count (the verbatim set on
    the page plus the shell's repetition of it) + the page type's own-prose ceiling, floored at
    the count as built — a ratchet, so any later edit that raises a term re-fails. Each entry's
    `_why` prints the decomposition per term, and names the terms where the page's own text
    (which includes the kit's table, counter, FAQ and review rows) is already over the proposed
    ceiling. **Project 5's location and puppy pages carry no override** and are judged on the
    page-type defaults; the audit still ERRORs on three location routes, the blog post and the
    board-preview routes, none of them rebuilt pages. A calibration pass that measures the
    ceilings against cited pages should retire most of these entries.

35. **The three guides share one hero arrangement (2026-09-22).** `/blue-staffy-health-uk/`,
    `/uk-staffordshire-bull-terrier-guide/` and `/uk-blue-staffy-puppy-buying-guide/` all picked
    H-GD3, so working rule 16's "no two pages share the same hero layout" is not met between
    them — the same gap Known Issue 33 records for the three utility pages' H-UT1. Their
    counters differ (C-GD1, C-GD3, C-GD2). `ledger-tuple-owned` does not catch it because its
    signature is hero + faq + table + takeaway, and the three differ on the other axes.
    **Closes with the breeder's new picks** for two of the three (H-GD1 and H-GD2 are unused),
    and should be followed by a board-gate row that fails a shared per-page hero or counter
    outright.

36. **Seventeen duplicate passages touch rebuilt pages (2026-09-22).** `scripts/dup_content_audit.py`
    reports 131 passages; 114 lie between pages project 4 did not rebuild, and 17 touch one it
    did: the FAQ answer "a comprehensive puppy package…" rendered from one `data/faq.json` row
    on four pages, and "are the puppies raised in a family home…" on two; the review
    attribution tail "…is the heart of our family — the Victoria Family, Manchester" crossing
    the quote whitelist on three pairs; three working-rule-15 openings the homepage carries from
    the pages it summarises; the post against the buying guide (35 words); and pup-sale's
    "healthy, vaccinated and ready" line against two location bodies. **Build 5**: whitelist
    shared FAQ rows and review attributions as sitewide lines (as the quotes already are), and
    rewrite the rest when the location and post bodies are rewritten.

37. **The commit trailer (2026-09-22).** Spec §7.7 names `Co-Authored-By: Claude Fable 5.1`.
    Every commit on `page-rebuilds` carries a `Co-Authored-By` trailer; 111 carry Fable 5.1 and
    the last nine (`2ce9e93` onward, including step 0 and the two close-out commits), plus the merge commit
    on `foundation`, carry `Claude Opus 5.5`, by the controller's instruction for those
    sessions. **Closes with the user's ruling** on which trailer project 5 uses.

38. **The breed guide's video player loads with the page (2026-09-22).** The breeder picked S2
    (the player full width on a steel band) for `/uk-staffordshire-bull-terrier-guide/`, so
    `youtube-nocookie.com/embed/g9iV9RVr_Sk` loads on page load and Chrome raises a cookie
    issue: Lighthouse Best Practices 96 on mobile and desktop, every other rebuilt page 100.
    The S3 facade — rule 14's default — fetches the player only on a press. **Closes with the
    breeder's choice**: keep S2 and accept the score, or pick S3.

39. **Project 5 prerequisite — nested routes (2026-09-23).** The STOP rules in
    `.claude/skills/bsuk-location-page-builder/SKILL.md` and
    `.claude/skills/bsuk-query-augmentation/SKILL.md` point here. Four tools build paths from a
    flat slug and cannot read or write a city page at `uk-locations/<slug>`:
    - `scripts/facts_preserved_check.py`: `dist_html` (lines 360–362); the `--extract` path
      creates only `data/facts/` and no subfolder (mkdir on 395, write on 396).
    - `scripts/link_parity_check.py` lines 231–232 (the dist path and the board path).
    - `scripts/verbatim_set_check.py`: `dist_html` and `load_record`, and `do_extract`
      (lines 486–491), which creates only `data/verbatim/` and no subfolder.
    - `scripts/pageboard.py` `own_live_key` (lines 920–927, the return on 927).

    Each must resolve `uk-locations/<slug>` to `dist/uk-locations/<slug>/index.html` (and the
    matching board, record and live key) through `data/page-map.json`, as
    `scripts/migration_parity.py` effectively does. **No city page goes into
    `data/facts/rebuilt.json` until this is fixed and tested.** In the same change,
    `scripts/query_coverage_check.py` should report a problem when a route's last segment is in
    `data/facts/rebuilt.json` but its page is missing, print the awaiting-rebuild slugs, and
    turn a malformed `data/facts/rebuilt.json` into a problem line rather than a crash.

40. **Project 5 builder checklist (2026-09-23).** Quality-review items on the builders deferred
    by the user's ruling during the query-augmentation build; clear each before or while the
    first city page is built.
    - Rule 15 (faithful rewrite) against the migrated city FAQs: 11 indexed city pages carry
      bodies, and the precedence table cites rules 1–10 only.
    - 11 location rows have an empty `h1`, so the primary-keyword source is undefined for them.
    - The worked example still carries variant letters and a shared counter, against rule 16
      (per-page hero and counter).
    - `src/components/kit/Hero.astro` takes layout props (`layout`, `align`, `media`, `ledge`)
      while the builder says "no variant prop" — reconcile the wording.
    - The bottom review mode is ambiguous; reviews sit in their own sections, never inside a
      body section.
    - Health-test fact conflict: `data/faq.json` asserts "certified clear" while
      `rules/copy.md` records the certificate as NOT FETCHED.
    - Step 1's hand-recorded competitor table and the board "competitor block" (which does not
      exist) — use the question file's competitors and `why_source` URL instead.
    - `scripts/query_coverage_check.py` needs body blocks as `<section data-section-label>`;
      the builder must say so.
    - `.claude/skills/bsuk-blog-post/SKILL.md` leftovers: governs-in-conflict wording,
      Firecrawl-first, no link library, "airport" delivery, "since 2014", push to main.
    - `.claude/skills/bsuk-comparison-page-builder/SKILL.md` leftovers: a US Google market
      setting, 22–25 fixed sections, push to main, eggs/breeding pair, "12+ years", a
      NewsletterV2 variant.
    - `.claude/skills/bsuk-seo-master-checklist/SKILL.md`'s external-link library is
      US-centric (AVMA, AAHA, ASPCA, FTC, VEG, Pet Poison Helpline, Chewy; the petmd homepage
      mislabelled) — replace with UK sources (PDSA, Blue Cross, BVA, gov.uk) via
      `docs/reference/external-link-library.md`.
    - `.claude/skills/bsuk-google-map/SKILL.md`'s location template uses `CITY%2C%20STATE` and
      "For state/city location pages" (US wording).
    - Later gate work: count built `dist/uk-locations/*` pages with no question file and print
      it; an optional per-page-type "must have a file" switch once project 5 covers all 28;
      check the visible FAQ questions come from the question file; an extra-section H2 must
      sit in a body section, not the frame; a heading-covered answer should stop at its
      section end.
    - Minors: lifespan source; `rules/copy.md` as a source; sem-all-six-levels is page-level;
      proximity/roads claims without a source; the former-city row (Known Issue 16) and the
      national rows compete; the blog builder's raw caps note; the puppy ContactForm name;
      top-10 vs top-5.

41. **Questions for Lisa Bright (2026-09-23).** Grouped and reworded from the files' blocked
    buyer questions: the Manchester and Leeds question files hold buyer questions (from Google,
    Bing, ChatGPT and Reddit) that the merge blocked as "unverified fact" because BSUK has no
    recorded fact to answer them. Each answer becomes a `data/faq.json` row or a
    `data/settings.json` key; then both question files rebuild
    (`python3 scripts/query_augment.py <slug> ...`, all sources cached, no calls).
    - Are there blue Staffy puppies available now for buyers in Manchester?
    - How much does a BSUK puppy cost?
    - Should I pay a deposit before I have seen the puppy — what is BSUK's deposit policy?
    - Is there a waiting list?
    - Can I see the puppy with its mother where the litter was raised?
    - Do you give a written contract and a return-to-breeder policy?
    - Does the contract give me time to have my own vet check the puppy?
    - Have both parents been tested for L-2-HGA and hereditary cataracts?
    - Have the parents had eye examinations and elbow screening, as well as DNA tests?
    - What are the parents' Kennel Club registered names, and what if the papers are delayed?
    - What is the parents' coefficient of inbreeding?
    - How can I confirm the puppy has been examined by a vet (can I contact your vet)?
    - Has the puppy had its first vaccination before I collect it?
    - What socialisation has the puppy had?
    - Can a blue puppy come from parents that are not both blue — what colours are your
      parents?

42. **Competitor intelligence build (2026-09-23).** The source repo's competitor-registry,
    competitor-intel, strategy-synthesizer and keyword-gap agents were not ported. User ruling
    (2026-09-23): a separate build after this one, started separately (2026-09-23).

43. **Reddit-modifier pages are a recorded option, not built.** Short pages aimed at
    `"<keyword> reddit"` searches (the source repo's playbook). Decide with search-volume data
    in project 5 or later; the thread half is `.claude/skills/bsuk-reddit-threads/SKILL.md`.

44. **No page-communication audit.** The source repo's visual-intelligence skill (does the page
    communicate, what job is it doing, why do two pages feel the same) was deferred to project
    3 in project 2's manifest; project 3 shipped without porting it. The 28 city pages in
    project 5 are where it would pay.

45. **DataForSEO costs are unknown (2026-09-23).** The connector returns no cost field, so
    `data/queries/spend.json` holds conservative estimates ($0.20 for Manchester). The user is
    to check the DataForSEO dashboard for the real spend; then set `query_typical_call_usd` in
    `data/settings.json` from the real per-call figure.

46. **Needs a user ruling — the banned-breed line (2026-09-23).** The breed guide
    (`src/pages/uk-staffordshire-bull-terrier-guide/index.astro`) states the Staffordshire Bull
    Terrier is not a banned breed, backed by the gov.uk banned-dogs row in
    `docs/reference/external-link-library.md`. The city-page template
    (`docs/reference/location-page-template.md`) and the builders make every statute line
    `LEGAL_CLAIM_PLACEHOLDER`. **Closes with the user's ruling**: city pages may state it with
    that same gov.uk row, or the breed guide moves to the placeholder.
