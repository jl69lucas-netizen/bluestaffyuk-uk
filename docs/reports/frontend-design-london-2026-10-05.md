# frontend-design Harden pass: London, second run (2026-10-05)

Page: `/uk-locations/blue-staffy-puppies-london/` (`src/pages/uk-locations/blue-staffy-puppies-london.astro`),
`docs/reference/page-run.md` row 15, run after today's impeccable pass
(`docs/reports/impeccable-london-2026-10-05.md`, recorded at `7b76daf8`) on a fresh build that carries its
fixes. The `frontend-design:frontend-design` skill was invoked with the Skill tool (args: Harden pass on the
built London page at 375 / 768 / 1280; existing BSUK design system fixed; visual layer only; content and the
approved board unchanged; design changes previewed, not applied). This pass applies that skill's
`SKILL.md` (design thinking: purpose, tone, differentiation; typography, colour commitment, motion, spatial
composition, visual detail) inside BSUK's locked system: Fraunces and Source Sans 3, the steel / bone / brass
tokens, `rules/design.md` (rule 6: motion at most 0.2s, no bounce or parallax) and the city type tiers in
`src/styles/city.css`. The skill's "choose fonts that are unique" and "vary themes" directions do not apply:
the system is fixed. Impeccable's D1 to D3 of today are not re-raised here.

**Visual layer only.** No word, heading, link target, image choice or section order changed. The two fixes
change only where lines wrap. Design changes are previews, deferred (working rule 6).

## How it was assessed

`npm run -s build`, `dist/` served on 127.0.0.1, Chromium through Playwright (device scale 1). The full-page
contact sheets of this morning's impeccable pass (57 / 36 / 38 viewport shots at 375 / 768 / 1280) were
re-read for composition, then measuring probes ran in the same browser at each width: the last line of every
heading, paragraph, list row, ledger value and summary in `main` (a one-word last line under a longer text);
every element's transition and animation duration against rule 6; the decoration of every inline link in
reading text; the gaps between `main`'s bands; and a hover probe on every visible link, button and summary
(67 / 71 / 71) comparing computed colour, background, decoration, border, shadow, transform and opacity before
and under the pointer. The new pieces since the last pass (the CARD-3 puppy band, the CTA pills, the statement
labels, the new FAQ set, the breeder photo, the image swaps) were each looked at in their own screenshots.

Before / after pairs: `docs/reports/screens/frontend-design-london-2026-10-05/`. Previews of the deferred
changes: `docs/reports/london-harden-2026-10-05/` (the "London Harden Proposals" page).

## The aesthetic read

**Point of view, unchanged and stronger: a breeder's ledger, in steel and brass.** The new pieces joined it
rather than diluting it. The CARD-3 band is the best addition: six named puppies on a deep-steel panel, each a
bone card with the price as the only brass, the breeder's own line in italic, a ticked list of what comes home
and a steel-100 stub for delivery; it reads as a litter sheet, not a product grid. The CTA pills give the
chapter closes a clear brass action, and the statement labels sit in the ledger's own caps-label voice.

**Weakest now:** two places where the composition fights the reader rather than the system. On a phone the
sticky header takes 121px of every screen (two rows: brand and pill, then "Open menu"), 15% of an 812px
viewport, on a page of 45,000px read almost entirely on the scroll (D1). On a desktop the CARD-3 band sets its
six cards three across inside the reading column beside the rail, so each card is 231px wide (265px at 1024, against 321px two across at 768): the meta
wraps ("Boy · Blue / and white"), the trust list falls to one column and the delivery stub to three lines,
where the same cards two across at 768 breathe (D2). Within the type, the remaining craft flaw was ragged last
lines: list rows and the rail's labels ending on a single word (F1, F2).

## Findings

4 findings: 2 fixed, 2 deferred. Severity as row 14 uses it (P1 blocks a reader, P2 a visible flaw, P3 polish).

| # | Sev | Finding | Location | Widths | Outcome |
|---|---|---|---|---|---|
| F1 | P3 | List rows and ledger values ended on one word: the trust ledger's "To your London door" ("… or collect in" / "Carlisle") at every width and its guarantee row ("deposit.") at 375; the call checklists ("blaze.", "screening.", "deposit."); two places rows ("area", "Garden", "acres"); a takeaways value ("claimed", "price."). The city kit set `text-wrap: pretty` on paragraphs only | `src/styles/city.css` | all | **fixed**: `.city-kit :where(li, dd) { text-wrap: pretty }`, the paragraphs' own rule. One-word last lines in `main`: 7 / 5 / 8 before, 0 / 0 / 0 after at 375 / 768 / 1280 (the two left at 375 are publisher names, below). Pairs `pair-fd-trust-ledger-*`, `pair-fd-checklist-*` |
| F2 | P3 | The desktop rail's labels broke on their last word: "The deposit and the video" / "call", "Getting your puppy to" / "London", "What comes home with a" / "puppy" | `CityDialPhotoMarker.astro` `a` | 1280 | **fixed**: `text-wrap: balance` ("The deposit and" / "the video call"). Pair `pair-fd-rail-1280-*` |
| D1 | P2 | The phone header is two rows and 121px tall, sticky on every screen: the brand and the "Available puppies" pill fill the first row, so the menu button wraps to its own | `SiteHeaderKit.astro` (every page) | 375 | **deferred**: shared chrome on every page, and the menu's visible "Open menu" word would become an icon (its name stays in the visually hidden text). Preview: one 73px row, brand · pill · menu icon, `--hdr` 72px below 640px; 48px more reading on every screen: `FD-D1-phone-header-375-{before,preview}{,-scrolled}.png` |
| D2 | P3 | On a desktop the CARD-3 band sets six cards three across in the reading column (231px each at 1280, 265px at 1024): meta wraps, the trust list falls to one column, the delivery stub runs three lines; at 768 the same cards two across read cleanly | `CityTicketStrip.astro` `.grid` | 1024 1280 | **deferred**: a layout change to the breeder's CARD-3 pick (answer board 2026-10-04 q08 (c)). Preview: two across from 1024 too; the band grows from two rows to three: `FD-D2-cards-1280-{before,preview}.png` |

### Measured and dismissed (not counted)

- One-word last lines on the FAQ summaries at 1280 ("03", "07" … "19"): a probe artefact; each summary's
  counter sits in its own grid column, lower than the question's last line, and is not a word of it.
- "City of London / Corporation" and "London Borough of / Sutton" at 375: publisher names, kept whole by the
  row's count column; a two-line proper noun, not a ragged sentence.
- The hover probe reported no delta on the contents index links (375, 768) and the four places summaries (all
  widths): both draw their hover on a child (`a:hover span` underline and arrow shift; `summary:hover
  .owner-n` underline), which the probe does not read. The other 57 / 57 / 67 targets change under the pointer.
- The six puppy-card name links carry no underline: each is its card's stretched target, a card, not a link
  in reading text.
- Motion: no transition or animation over rule 6's 0.2s at any width; the filmstrip settle-in and the card
  lift stay inside `prefers-reduced-motion: no-preference`.
- Band rhythm: the page-shell bands sit 48px from their dividers; the hero, counter and trust bands keep their
  tone shifts and rules.

## Verification

| Command | Exit | Examined |
|---|---|---|
| `npm run -s build` | 0 | 63 built pages |
| one-word last-line probe | — | 20 real before (7 / 5 / 8), 0 after |
| `npx playwright test -c tests/render/playwright.config.ts pages.spec.ts -g "uk-locations"` | 0 | 12 passed (4 location pages × 375 / 768 / 1280) |
| `python3 -m pytest tests/py/test_london_page.py tests/py/test_design_components.py tests/py/test_design_tokens.py -q` | 0 | 86 passed, 1 skipped, 1 xfailed |

The pass is recorded in `data/page-runs/blue-staffy-puppies-london.json` (`frontend_design`: 375 / 768 / 1280,
4 findings, 2 fixed, 2 deferred with the reasons above).
