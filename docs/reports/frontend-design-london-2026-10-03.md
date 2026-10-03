# frontend-design Harden pass: London (2026-10-03)

Page: `/uk-locations/blue-staffy-puppies-london/` (`src/pages/uk-locations/blue-staffy-puppies-london.astro`),
`docs/reference/page-run.md` row 15. The controller invoked `frontend-design:frontend-design` with the Skill
tool; this pass applies that skill's `SKILL.md` (design thinking: purpose, tone, differentiation; typography,
colour commitment, motion, spatial composition, visual detail) inside BSUK's locked system: Fraunces and
Source Sans 3, the steel / bone / brass tokens, `rules/design.md` (rule 6: motion at most 0.2s, no bounce or
parallax) and the city type tiers in `src/styles/city.css`. Row 14's fixes (impeccable, F1 to F9) were not
redone and its deferred D1 to D4 (with the breeder) are not re-raised here.

**Visual layer only.** No text, heading, link target, image choice or section order changed. Fixes are CSS
in the shared city kit; design changes are previewed and deferred (working rule 6).

**How it was assessed.** `npm run -s build`, then Chromium through Playwright (device scale 1) on the built
`dist/`: a full page and viewport shots scrolled through the page at 375 (50 shots), 768 (37) and 1280 (44),
read as contact sheets, each looked at. Then measuring probes in the same browser: every heading's last line
(one-word orphans), the vertical gap and padding of every band in the page shell, the computed decoration and
colour of every link in `main`, and a hover probe on every visible link, button and summary (82 at 1280),
comparing computed colour, background, decoration, border, shadow and transform before and under the pointer.

Screens: `docs/reports/screens/frontend-design-london/` (before / after top viewport per width,
`full-<w>-{before,after}.jpg` at half scale, and `pair-fd-<piece>-<w>.png` pairs of each fixed piece).
Previews of the deferred changes: `docs/reports/frontend-design-london/`.

## The aesthetic read

**Point of view: a breeder's ledger, in steel and brass.** The page has one: a working kennel's record
book rather than a sales page. Fraunces at heavy weight sets every buyer question in brand steel; brass is
spent only where money or a step is (the CTA pill, the numbered chapter coins, the hero byline rule, the
route line); the content sits in ruled ledgers (the takeaways, the FAQ on deep steel, the litter roster)
and the photographs are real dogs, framed plainly. It does not read as a template.

**Strongest:** the first screen. The deep-steel hero with the six-puppy filmstrip, the counter strip as a
broken price scale on its own bone-50 bed with a steel rule, and the trust ledger with Maggie's photograph
make a confident, specific opening; the two dark FAQ ledgers are the page's best type moments (numbered
mono-width counters, Fraunces questions, brass plus marks). **Weakest:** the long middle. Ten chapter bands
repeat one composition (steel-100 tray on a bone band, H2, full-width photo, lede, numbered H3 rows), and
all sixteen band boundaries are the same seal divider at the same 48 + 58 + 48px, so from the first chapter
to the contact form the rhythm is a metronome: nothing marks the turn from buying to living with the dog.
The page also has no motion moment at all: the hero arrives fully formed. Both are design changes, deferred
(D5, D6). Within the ledger, the one real craft failure was that its links were invisible (F1).

## Findings

10 findings: 5 fixed, 5 deferred. Severity as row 14 used it (P1 blocks a reader, P2 a visible flaw,
P3 polish).

| # | Sev | Finding | Location | Widths | Outcome |
|---|---|---|---|---|---|
| F1 | P1 | Links in reading text painted exactly as the prose around them: no underline, the text's own colour (the preflight's `a { color: inherit; text-decoration: inherit }`, which no city component set back). 40 links: 25 Link-First anchors in the chapters, the 7 FAQ "more" pointers (their rule set an underline offset but no underline), the vet line and the 7 places sources. A link told apart by nothing (WCAG 1.4.1), and the board's approved anchors could not be seen | `src/styles/city.css`, `CityPlacesByPublisher.astro` | all | **fixed db4c0631**: a 1px underline in the text's own colour at half strength (`color-mix` of `currentColor`, no new colour, reads on bone, steel-100 and the steel bands), 3px offset; hover draws it at full strength and 2px. Components that style their own link keep it. Pairs `pair-fd-link-*`, `pair-fd-link-hover-*` |
| F2 | P3 | Two links with no hover state at all: the hero's secondary "BlueStaffyUK" link and the byline's "Lisa Bright" (the pill beside them darkens) | `CityHeroFilmstrip.astro`, `CitySignedByline.astro` | all | **fixed db4c0631**: the F1 hover (underline 2px, full strength). The hover probe at 1280 now finds no link in a city component without a hover delta except the shared contact-form note (D9) |
| F3 | P2 | Chapter bands broke the sibling rhythm: every other band (letter, newsletter, FAQ, contact) sets its panel in by the tier's `--city-pad-y` (32 / 40 / 48px), the chapter tray sat a flat 32px down at every tier, so from a tablet box the chapter bands ran tighter than the cards between them | `CityChapters.astro` | 768 1280 | **fixed db4c0631**: the tray (the root's direct child) takes `--city-pad-y` as its block margin, `flow-root` keeps it inside the painted band. Pair `pair-fd-chapter-top-*` |
| F4 | P3 | Inside one component, two heading-to-image distances: an H2 sat 8px over its photograph, every H3 sits 12px (`--space-3`, the chapter's row gap) over its own; at 1280 the H2's descenders nearly touched the photo | `CityChapters.astro` `.h2-img` | all | **fixed db4c0631**: `--space-3` |
| F5 | P3 | The stacked litter slip left its separator hanging at a line end: "Girl · Blue with white blaze ·" / "Available" (Cheryl) | `CityRoster.astro` (stacked below a 640px box) | 375 | **fixed db4c0631**: the separator is `" ·\00a0"`, so the dot travels with the value it introduces ("· Available"). Pair `pair-fd-roster-375` |
| D5 | P3 | Divider cadence: sixteen identical seal dividers at an identical 154px, chapter to chapter included; the seal stops meaning "a new part" | page (`SectionDivider` between bands) | all | **deferred**: a motif and composition change (working rule 6). Preview: between two chapter bands, a steel-300 hairline instead of the seal, the seal kept at the turns into the FAQ blocks, letters and contact: `D5-divider-cadence-{375,1280}-before.png` / `-preview.png` |
| D6 | P3 | No page-load moment: the hero arrives fully formed | `CityHeroFilmstrip.astro` | all | **deferred**: a new motion moment. Proposal: the six filmstrip photographs settle in once on load, opacity and an 8px rise, 200ms each (rule 6's ceiling), staggered 60ms, transform and opacity only (no layout property), inside `@media (prefers-reduced-motion: no-preference)` so a reader who asks for less motion sees the strip still. Frames at 0 / 150 / 300 / 500ms: `D6-hero-settle-{375,1280}-t{0,150,300,500}.png` |
| D7 | P2 | The chapter tray sits 12px in from its band at every width, where every sibling panel sits 16px in on a phone and 32px from a 640px box; on a desktop it reads as a panel slipped inside a thin bone frame | `CityChapters.astro` `.tray` | all | **deferred, tried and reverted**: applied with the matching `sizes` in `src/lib/cityKit.ts`, the narrower text column at 1280 painted the served `kc-registered-staffy-puppies.webp` (a 500px master with no width siblings, under "How Do I Check a Registration Myself?") at 244px, 2.05x, and the render gate's `img-srcset-within-2x` failed. It needs a width sibling beside that master (working rule 11, the image step) first. Preview of the full change: `D7-tray-gutter-{375,768,1280}-before.png` / `-preview.png` |
| D8 | P2 | Two crops cut baked-in lettering: the "Contact Us" graphic under the first chapter H3 loses its headline's top, and the Staffordshire / American Bully comparison loses the second line of both labels ("BULL TERRIER", "BULLY") | `uk-blue-staffy-breeders-contact-form-support`, `staffordshire-bull-terrier-vs-american-bully-comparison` in their uniform boxes | all | **deferred**: the crop box and focus are the board's image slots (Asset Gate). Preview with the whole picture on the bone-50 ground (`object-fit: contain`, the image-bleed rule's colour): `D8-crop-contact-graphic-{375,1280}-*.png`, `D8-crop-breed-labels-{375,1280}-*.png` |
| D9 | P3 | Shared chrome and kit: the footer's legal row sets "© 2026 Blue Staffy UK" 11 to 12px above "Privacy policy" (the link's 44px row is centred, the text is not); the contact form's privacy-policy link has no hover | `SiteFooterKit.astro` `.legal`, `ContactFormKit.astro` `.note a` | all | **deferred**: both repaint every page that carries them (the footer on all, the form kit on four), previewed first as row 14's D3 was. Preview (`align-items: center` on the legal row): `D9-footer-legal-{375,1280}-before.png` / `-preview.png` |

### Measured and dismissed (not counted)

- H4 "Is the Transport DEFRA-Approved?" ends on one word at 1280: `text-wrap: balance` sets the
  hyphenated compound on its own line, two even lines, not an orphan.
- The hover probe reported the seven FAQ pointers with no hover delta: they sit in closed `<details>`.
  Opened, the pointer's underline goes from 1px half strength to 2px full strength under the pointer.
- Dial rows, ticket-strip cards, the contents index and the hero pill are navigation and cards, not reading
  text: they carry no underline by design and each has its own hover.
- Motion that exists already respects `prefers-reduced-motion` (contents arrows, FAQ markers, jump-stepper
  sheet and slide, puppy sheet, ticket lift); the CTA and newsletter colour fades are colour, not movement.
- Section rhythm: every band in the page shell sits 48px from its divider at every width (measured), and the
  hero and counter strip keep their tone shift and rule.

### Outside this page (for the controller)

The same preflight gap leaves prose links undecorated beyond London: on the built homepage 48 links and on
`/blue-staffy-health-uk/` 29 links compute to the text's colour with no underline. The fix here is scoped to
`city.css` (imported only on city pages); a site-wide rule belongs in `global.css` and repaints every page,
so it is a separate, previewed change.

## Verification

Run after the fix commit (`db4c0631`), in sequence:

| Command | Exit | Examined |
|---|---|---|
| `npm run -s build` | 0 | 63 built pages |
| `npx playwright test -c tests/render/playwright.config.ts pages.spec.ts -g "blue-staffy-puppies-london"` | 0 | 3 passed (375, 768, 1280) |
| `python3 -m pytest tests/py/test_london_page.py -q` | 0 | 21 passed |
| `python3 scripts/board_gate.py blue-staffy-puppies-london` | 0 | 22 sections, 93 headings, 51 live pages, 79 entity refs, 35 assets; 0 FAIL, 31 WARN (the board's own keyword and entity advisories, unchanged by this pass) |
| `npm run -s check:all` | 0 | every gate in the chain 0 problems (board gate --all 13 rebuilt pages, 0 failed; city canvas 45 fragments; markers 410 files; agents 46) |

D7 was first applied with the matching `sizes`; that build failed the filtered render gate at 1280 (one row,
`kc-registered-staffy-puppies.webp natural=500 painted=244 2.05x`), so the side inset and the `sizes` change
were reverted before the fix commit and the change is deferred; the passing run above is on `db4c0631`.

The pass is recorded in `data/page-runs/blue-staffy-puppies-london.json` (`frontend_design`: 375 / 768 / 1280,
10 findings, 5 fixed, 5 deferred with the reasons above).
