---
name: bsuk-cta
description: Use for every call to action on a BlueStaffyUK page — planning where the buttons go (hero to contact form), how many a page carries, which type each section takes, the button words and the button style — and for putting every CTA on the page board so the breeder picks each one. Also use when a page "has too many buttons", "the buttons all look the same", "two buttons say the same thing", a CTA is missing, a button wraps or reads generic, or when building any location, comparison or blog page (its board must list its CTAs from 2026-10-08 on). Triggers - "CTA", "call to action", "button text", "button style", "where do the buttons go", "add CTAs to the board", "cta-text-distinct", "cta-style-distinct", "cta-count-in-band", "cta-board-missing".
allowed-tools: [Read, Write, Bash]
---

# BSUK calls to action

Every call to action on a BlueStaffyUK page is **its own button**: its own words, its own style,
in a place chosen for what the reader has just read, and **picked by the breeder on the page
board** before anything is built. This skill is the method. The machinery is:

| Piece | Path | What it does |
|---|---|---|
| The plan | `data/design/cta-plan.json` | count bands per page type, the near-identical threshold, the CTA types |
| The style catalog | `src/styles/cta.css` | eight styles on the locked tokens (one file: the page, the board and the catalog read it) |
| The button | `src/components/kit/CtaButton.astro` | paints one CTA in one style |
| The picks, page side | `src/lib/ctas.ts` | `pickedCtas(record)('hero')` → the breeder's picked option; throws if unpicked |
| The board | `scripts/cta_rules.py` | the record's `ctas` slots, the proposal, board block 7e, the approval check, the gate |
| The built page | `tests/render/checks/cta.ts` | `cta-text-distinct`, `cta-style-distinct`, `cta-count-in-band` |
| The rule | `rules/links.md` `ctas-on-the-board`; CLAUDE.md working rule 12 | CTAs are on the board, like links |

The words for a section's CTA can be drafted from the three voices in
`.claude/skills/bsuk-cta-strategy/SKILL.md` (Trust & Security, Direct & Transactional,
Ethical & Quality). That file is a word bank; this one decides everything else. Where the two
disagree, this one wins, because it is the one the gates enforce.

---

## 1. What counts as a CTA

A CTA is a visible `<a>`, `<button>` or submit inside `<main>` painted in `--color-cta` with
`--color-cta-ink` (`rules/design.md` rules 1 and 3). The render checks find CTAs by that paint,
not by a class name, so a new component can't hide a button from them.

| Type | What it does | Target | Counts toward the band? |
|---|---|---|---|
| `browse` | sends the reader to the litter | `/available-puppies/` or a puppy page | yes |
| `ask` | sends the reader to this page's enquiry form | `#enquiry` (a section id on the page) | yes |
| `ask-about-pup` | one per puppy card ("Ask about Roman") | `/available-puppies/<slug>/` | yes, the whole set counts once |
| `submit` | a form's own button | none (it sends the form) | no |
| `tool` | works a component (the map's "Show the map") | none | no |

Not CTAs: in-prose links (they follow `rules/links.md` Link-First), the header's "Available
puppies" button and the footer CTA (site chrome, outside `<main>`), and anything inside `nav` or
marked `data-cta-exempt`.

A **repeated set** is one CTA per card in a list (the six puppy cards). It is one design used N
times by construction, so it is judged as one CTA: its members differ only by the puppy's name,
and the set counts once.

---

## 2. Where CTAs go, section by section (hero to contact form)

| Section | CTA | Type | Why there |
|---|---|---|---|
| Hero | **exactly one** | `ask` on location, comparison and blog pages; `browse` on buy and for-sale pages | the first decision a reader can make; it must fit the hero clamp (`rules/design.md` rule 10), so 2–6 words |
| Key takeaways / counter strip | at most one, and only if the hero's is two sections away | `ask` | a reader who got the answer in one screen can act on it |
| Trust / credentials | none | — | proof, not a pitch; a button here reads as selling the proof |
| Litter, puppies, prices | one, or one `ask-about-pup` per card | `ask` / `ask-about-pup` | the highest-intent section on the page |
| Deposit and viewing | one | `ask` ("ask us to book your visit") | the reader has just learned how reserving works |
| Delivery | none (a map's tool button is fine) | `tool` | the band is data; let the reader read it |
| Paperwork, health, guarantee (`guarantee_days`) | at most one | `ask` ("ask us for the full terms") | a careful buyer asks for the terms before a deposit |
| Life in the city, temperament, care | at most one | `ask` ("tell us about your household") | turns a fit question into an enquiry |
| FAQ blocks | **none** | — | no `<a>` inside an answer (FAQPage JSON-LD); a block may end with one prose link |
| Reviews | none | — | a button straight after a review reads as paid for |
| Newsletter | its own submit | `submit` | the soft path for a reader not ready to ask |
| Enquiry / contact form | its own submit, last | `submit` | every `ask` above lands here |

**Spacing:** at least one section between any two body CTAs, so no two are on one screen at 1280.
The board refuses two slots in neighbouring sections, and `cta-count-in-band` reports them on the
built page.

---

## 3. How many

The bands live in `data/design/cta-plan.json` `bands` (body CTAs only; a repeated set counts as
one). The breeder changes a band there, never in a check.

| Page type | Band | Built pages measured 2026-10-08 |
|---|---|---|
| location | 3–6 | London 5, Manchester 3 |
| comparison | 2–4 | none built yet |
| blog | 2–4 | the two migrated posts carry 0 (pre-rule) |
| for-sale / buy | 1–4 | the three buy pages: the puppy-card set |
| puppy | 1–3 | Roman's page 0 (pre-rule) |
| home | 1–6 | the puppy-card set |
| hub | 0–3 | 0 |
| interior (about, guides, contact, utility) | 0–3 | 0–2 |

---

## 4. The button words

1. **Starts with a verb and says what happens.** "Ask us which puppy suits your home", never
   "Learn more", "Click here", "Submit" or "Get started".
2. **2–8 words.** It has to sit on one line in the pill at 375px, and the hero clamp can't absorb
   a second line. The board refuses anything outside 2–8.
3. **Names the destination.** An `ask` goes to the form, so it says ask, tell or send. A `browse`
   goes to the litter, so it says see, browse or meet.
4. **Never the same button twice on a page.** Two texts are near-identical when, with the stop
   words dropped (`data/design/cta-plan.json` `near_identical.stop_words`), their content words are the same
   set or overlap by 0.6 or more (Jaccard). "Ask about a puppy" and "Ask us about a puppy" are
   one button twice (Manchester shipped that pair, 2026-10-08). "Send enquiry" and "Send my
   enquiry" are one button twice. The only exception is a repeated set, which is one CTA.
5. **No figure in a button.** A price, the deposit, the delivery band or the guarantee length (`guarantee_days`) is
   copy beside the button, read from `data/`, never in the button text (working rule 9). The board
   refuses a digit or currency sign in an option.
6. **No promise the page can't keep.** No "Reserve now" before a viewing, no "Verify our
   credentials" while the licence is LICENCE_CLAIM_PLACEHOLDER, no video call where the page's
   research board dropped it (Manchester STOP 1 q08).
7. **First-person brand voice** (working rule 1): "Ask us…", "Tell us…", "Send my…".

---

## 5. The button styles: every CTA its own design

The catalog is `src/styles/cta.css`. Every style keeps the locked rules: `--color-cta` fill,
`--color-cta-ink` label, a `--btn-radius` pill for a link and a `--btn-form-radius` button for a
form submit, at least 48px tall. What varies is the shape inside those rules, so no two CTAs on a
page look alike and the palette never moves.

| Id | Looks like | Use it for |
|---|---|---|
| `solid` | the signature pill, nothing added | the one plain button on a page (often the enquiry submit) |
| `arrow` | pill + trailing → that steps forward on hover | `browse`: going somewhere else on the site |
| `down` | pill + trailing ↓ | `ask` that jumps down to the form on this page |
| `chip` | a round ink chip with an envelope before the label | writing to us: the enquiry submit, "send my questions" |
| `sub` | two lines: the label, then a short plain line (`sub`) | a CTA that needs one fact beside it, e.g. "Collection in Carlisle or UK delivery" |
| `tag` | label, dashed seam, a short tag (`tag`) | a place or a step: "Ask us to book your visit ¦ Carlisle" |
| `caps` | small capitals with open tracking, at the end of a brass rule | a quiet sign-off at the end of a long section (links only, never a submit) |
| `wide` | the full width of its column | the end of a narrow section or a card |

**Rules:**

- **Every CTA on a page has its own style.** Link CTAs are judged against link CTAs, and submits
  against submits (they are different shapes by rule). The board refuses an approval that picks
  one style twice, and `cta-style-distinct` reports it on the built page. A repeated set is one
  style.
- **`sub` and `tag` text is a fact from `data/`**, never invented. `scripts/cta_rules.py` proposes
  them from `data/settings.json` (the town, collection or delivery).
- **A ninth style** is added to `src/styles/cta.css`, `src/components/kit/CtaButton.astro` `CTA_STYLES`, `cta_rules.STYLES` and the
  board schema's enum together (`tests/py/test_cta_rules.py` pins all four), and it is previewed to
  the breeder in the browser before it is offered on a board (working rule 10).

---

## 6. The workflow on a page (page-run rows 10–14)

**Row 10, the page board (before STOP 3).** Propose the slots and write them into the record:

```bash
python3 scripts/cta_rules.py <slug> --propose
```
```bash
python3 scripts/cta_rules.py <slug> --propose --write
```

The proposal places the hero, one slot per matched body section (litter, deposit, paperwork,
life) with a section left between buttons, and each form's submit. It gives every slot three
options in three different styles, rotating through the catalog so each slot's option (a) has a
style of its own. **Then edit it to the page:** rewrite each option's words from the section's
outline (working rule 8, never from a sibling page), make sure the three options in a slot are
genuinely different buttons (different verbs or a different promise, not reworded twins), write
each slot's `why` (what this button does for the reader at that point), and check the page sits
in its band. Then check the record:

```bash
python3 scripts/cta_rules.py <slug>
```

**The board.** `python3 scripts/build_page_board.py <slug>` renders block **7e, Calls to action**:
the page's count against its band, then one radio group per slot, each option painted in its own
style with the site's real tokens. The approve button won't submit while a slot is unpicked, and
`scripts/board_approve.py` refuses picks that repeat a text or a style. Never record a pick from
anywhere but the board's own save (the answer board holds questions, not approvals).

**Row 12, the build.** Paint the picks, never typed text:

```astro
---
import CtaButton from '../../components/kit/CtaButton.astro';
import { pickedCtas } from '../../lib/ctas';
import record from '../../../data/boards/<slug-file>.json';
const cta = pickedCtas(record);
---
<CtaButton {...cta('hero')} />
```

A form's submit is a slot of type `submit`. `cta('enquiry')` returns `{ submit: true }`, and the
form renders `<CtaButton {...cta('enquiry')} />` as its button.

**Row 13, the render gates.** `npm run test:render:pages` runs the three CTA checks at 375, 768 and
1280. Read each check's examined count before trusting a pass (`rules/gates.md`): a page with no
CTA painted in `--color-cta` examines zero.

**Auditing a built page** (any page, including the twelve built before the rule): run the render
harness, read the `cta-*` rows, and report in this shape:

```markdown
## CTAs on <slug>
| # | Section | Type | Text | Style | Target |
|---|---|---|---|---|---|
| 1 | top | ask | Ask about a puppy | solid | #enquiry |
Body CTAs: N (band a–b for <type>) · near-identical pairs: … · shared styles: … · neighbouring sections: …
Recommended fix (Recommended + Why, working rule 4): …
```

Changing a built page's button words or style is a page change: it goes on the page's board and
is approved there, never edited straight into `src/pages/` (working rules 6 and 12).

---

## 7. Where the rule binds

- **Every location, comparison and blog page boarded from 2026-10-08 on** (`cta_rules.applies`:
  `family_rules.applies` minus `BUILT_BEFORE_CTA_RULE`). No `ctas` block is a WARN on a draft and a
  FAIL from `boarded` on (`cta-board-missing`). `npm run check:boards` and the board's block 7b
  show it, and the approval is refused while it fails.
- **London and Manchester** were approved before the rule. Their boards are not asked; their built
  pages are still reported by the render checks (advisory). Manchester's "Ask about a puppy" /
  "Ask us about a puppy" pair and both pages' single shared pill design are the measured debt.
- **The render checks are advisory today** (`data/quality/rule-index.json` says why for each). They
  are promoted to `new-pages` in `tests/render/targets.json` `promotions` with the first page built
  from CTA picks, so every later page is blocked on them from its first build.

---

## 8. What not to do

- Don't type a button's words or style into a page: they come off the board through `src/lib/ctas.ts`.
- Don't add a CTA the board doesn't list (working rule 12). An unlisted button isn't built.
- Don't reuse a style on one page to "keep it consistent". Consistency is the palette and the
  pill shape, which never change; the style is what tells two buttons apart.
- Don't put a CTA inside an FAQ answer, straight after a review, or in a trust strip.
- Don't stack two CTAs in neighbouring sections to hit a band: move one, or the band is wrong for
  the page and the breeder changes `data/design/cta-plan.json`.
- Don't paint a CTA outside the catalog (an outline button, a ghost link styled as a button, a new
  colour). It breaks `rules/design.md` rules 1 and 3, and the checks can't see a button that isn't
  painted in `--color-cta`.
