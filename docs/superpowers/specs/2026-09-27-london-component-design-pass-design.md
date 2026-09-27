# London Component Design Pass — Design

**Date:** 2026-09-27 · **Status:** approved in brainstorming (four sections, each confirmed by the
user) · **Branch:** `london-components` (worktree `/Users/apple/Downloads/BSUK-london`, cut from
`foundation` at `5b41cd5`) · **Project:** project 5, step 0 for the London page.

## Why

The user's answer-board decision q01 (c) (`docs/reference/answer-board/answers/2026-09-26-project-5-decisions-before-the-first-city-page-2026-09-27.md`)
puts a component design pass before any city page. The hero pool is exhausted: the six page
families' 18 hero and 18 counter styles are all taken by the 12 built pages, and the city pages map
to the `interior-guide` family, whose three heroes the guides own (Known Issue 60). The city pages
also still render the migrated body on `BaseLayout`, with no kit components (Known Issue 87).

The user's definition of done for a page starts here: 3 variants of each component → research →
component picks → fan-out → build → all gates → Claude verifies → the user approves or fails the
page.

## Decisions (from the brainstorm)

| # | Question | Decision |
|---|---|---|
| 1 | Scope | **London only.** Each later city gets its own pass, page by page, checked against every earlier city's picks. |
| 2 | Where picks happen | **A London component canvas** (a private Artifact), separate from the page board. The London board later shows only the picks, with real copy. |
| 3 | Which components | **All 15 on the city page** (list below). The site header and footer stay site-wide. |
| 4 | How variants are built | **Canvas mockups on the real tokens first; only the 15 picks are built into the kit.** The 30 unpicked variants join a city design pool. |

## The 15 components

The city page's spine (`.claude/skills/bsuk-location-page-builder/SKILL.md` Step 2) plus the
navigation the user named:

1. Hero (image first on phones)
2. Counter strip
3. Trust strip
4. Contents list (`PageNav`)
5. Desktop dial (`PageDial`)
6. Mobile sticky jump links (`SectionStrip`, with `SectionSheet`)
7. Key takeaways
8. Puppy cards (the six available puppies)
9. Tables (stack on phones)
10. Video
11. Image + text section
12. Reviews (city pages use a single review per slot)
13. FAQ blocks (three blocks, 15–20 questions)
14. Newsletter
15. Contact form

The dial and jump links were pruned to one arrangement on 2026-09-19. This pass reopens them to
three variants, at the user's request.

## 1. Inputs and design rules

**Reference capture.** Playwright takes full-page screenshots of the four reference pages in
`docs/research/2026-09-27-location-component-design-sources.md` (the MFS homepage and three
sister-site pages) at 1280 and 375 widths. Each page is also cut section by section into
per-component crops. With the 20 PNGs in `/Users/apple/Downloads/MFS/assets/MFS-Components-IDEAS`
and the 42 in `/Users/apple/Downloads/bluestaffyuk-cms/Assets/Components-Ideas`, these form a
per-component ideas index, kept outside the repo. The repo keeps only a summary: what idea each
variant took, from where.

**Must differ from.** For each component, a list of what the 12 built pages use: their approved
picks and the existing S1–S3 styles in `src/lib/boardStyles.ts`. Each new variant differs from
everything on that list, and from its two siblings, on at least two structural axes (layout,
media position, density, framing). A colour change alone never counts.

**Rules every variant meets.**
- BSUK design tokens only (`src/styles/tokens.css`: steel, brass, bone, the two fonts, the fixed type scale, spacing, radius, shadow and motion).
- The hero image comes first on phones.
- Tables stack on phones (`data-label` cells).
- Bleeds, letterboxes and backgrounds use design-system colours, never grey or black.
- Every heading is a buyer question, followed by a conversational opening paragraph that answers it.
- Accessible: contrast, focus states and tap targets.
- Light and fast: CSS-first motion, no heavy scripts.
- `rules/design.md` holds, and the files the `design-context-read-first` rule names are read first.

**How each variant is made.** frontend-design proposes three directions per component from its
references. impeccable then critiques and hardens every variant before it reaches the canvas.
Placeholder copy is London-flavoured, so the design is judged in context. The real copy comes
from the research after the picks.

## 2. The London component canvas

- **Page:** one private Artifact. Fifteen sections in city-page order, each with variants A, B and C and a one-line name for each.
- **Previews:** each variant renders in a true-width frame at 1280, 768 or 375 (per section, or all at once). Phone is the default view.
- **Newness note:** each variant has a note saying how it differs from what the built pages use.
- **Phone layout:** on a phone, the canvas stacks the variants.
- **Picking:** each component takes one pick (A, B, C, or "none — redesign") and a note. A general notes box sits at the end.
- **Storage:** picks are stored in the canvas's own shared database, so the user can leave and come back and Claude reads them directly.
- **Sending:** a "Send picks to Claude" control tells Claude the picks are done. If the notification does not arrive, the user says "read my picks".
- **Redesign:** "none — redesign" produces three fresh variants of that component only, on the same canvas, with the note as the brief.
- **Freeze:** when every component has a pick, the picks are saved in the repo (`data/design/city-picks/blue-staffy-puppies-london.json`) and the canvas is marked final. The London page board and the uniqueness gate read that file.

## 3. Building the picks

1. **Components.** The 15 picks become real Astro kit components, or variants of existing ones: new style entries in `src/lib/boardStyles.ts`, plus props or CSS.
   - Each is registered in `src/components/kit/_registry.ts` with its fixture in `src/pages/kit-preview/` and its tests (the kit conventions, including `tests/py/test_design_components.py`).
   - Nothing is copied from a sibling page.
2. **The shell.** London gets its own `.astro` file, `src/pages/uk-locations/blue-staffy-puppies-london.astro`, on `PageShell`.
   - That brings the dial, jump links, contents list and footer-CTA wiring.
   - The other 27 cities stay on `src/pages/uk-locations/[slug].astro` until their own passes. The dynamic route must then not also build London's path.
   - The page file built in this pass is a scaffold with the picked components and placeholder copy, kept out of the sitemap (`noindex`) until London's page run writes its real copy.
3. **Mobile hero fix.** In `src/components/kit/Hero.astro`, the split, bleed and mosaic layouts put the copy above the photo on phones (`.pic { order: 2 }` has no mobile override).
   - Every layout will paint the photo first below 900px.
   - A new blocking render check, `layout-hero-image-first-mobile`, measures it on every page.
   - The 12 built pages are re-checked. Any hero whose phone view changes is shown to the user.
4. **A city pool in the uniqueness rule.**
   - City pages get their own family in the rule-16 gate (`scripts/pageboard.py` `rule16_findings`) and in `src/lib/boardStyles.ts`. This closes Known Issue 60.
   - The gate refuses a city pick that matches any earlier city's pick or any built page's pick, for all 15 components, not only hero and counter.
   - London's approved picks are the first entries.
   - The 30 unpicked variants are recorded in `data/design/city-pool.json` as available to later cities, each still subject to the same check.
5. **Gates.**
   - `npm run -s build`, `npm run -s check:all` and the render suites all pass, twice.
   - The impeccable and frontend-design passes are recorded.
   - `superpowers:verification-before-completion` runs.
   - The user sees each built component beside its canvas version and confirms the match.

## 4. Order, scope and done

**Order**
1. Capture the references and build the ideas index.
2. Write the must-differ list.
3. Design the 45 variants, then harden them (frontend-design, then impeccable).
4. Publish the canvas. The user picks, and any redesign goes round again.
5. Build the 15 picks, the mobile hero fix and the city pool.
6. Run the gates, then the user confirms the side-by-side.

**Next:** London's page run (`docs/reference/page-run.md`), with the picks in its board.

**Out of scope**
- London's copy, research and SEO.
- The other 27 cities.
- The site header and footer.
- Any change to the 12 built pages, except the mobile hero-first fix.

**Workflow**
- Subagent-driven, with Opus implementers and a spec review then a quality review per task.
- Artifacts for the canvas and the reports.
- Commits carry the Fable 5.1 trailer. Nothing is pushed.
- Merge into `foundation` only when the user says so.

**Done means**
- All 15 picks are approved on the canvas and saved in the repo.
- They are built, with every gate passing twice.
- impeccable, frontend-design and verification-before-completion are recorded.
- The user has confirmed the side-by-side comparison.

## Risks

- **Canvas weight.** 45 variants × 3 widths is a heavy page. Frames load lazily, one section at a time, and the phone view is the default.
- **Mockup-to-kit drift.** The mockups use the kit's tokens and class conventions. The side-by-side confirmation catches any drift before the pass is done.
- **The mobile hero fix changes built pages.** It is limited to phone widths, it is shown to the user, and the fix's render check proves it.
- **Reference copying.** Variants take ideas, not markup. The ideas summary records the source of each idea, and no sister-site text or image is used.
