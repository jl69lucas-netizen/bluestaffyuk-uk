# Session Brief — 2026-09-30

> **Status:** IN PROGRESS. The interview is underway; resume with `grill-me --resume`.
> **Last updated:** 2026-09-30 (pre-filled from disk)
> **Next question:** Q9

## Q&A Log (Verbatim)
_(The user's exact answer to each question is appended here as the interview proceeds. Entries marked "from disk" were read from the repo, not asked, and are pending the user's confirmation.)_

**Q1 — Outcome (from disk):** The London city page `/uk-locations/blue-staffy-puppies-london/` is built from its own outline and passes every gate. Claude verifies it; then the user approves or fails it. (Definition of done: `bsuk-project5-board-decisions`, answer board 2026-09-26/27.)

**Q2 — Traffic reality (from disk):**
- Search Console and Bing data are NOT FETCHED: the GSC property is unverified because the domain expired, and there are no exports on disk (`data/page-map.json` `baseline_gsc`).
- London today is a stub: 4 words, an empty H1, noindex. The scaffold uses the placeholder kit.

**Q3 — Worst performer (from disk):** London itself. It is the first of 28 city pages, and all 28 are stubs or migrated WordPress bodies (gap matrix 2026-09-25).

**Q5 — Constraints (from disk, rulings on record):** see the CONSTRAINT lines below.

**Q6 — Specific target (from disk):** `/uk-locations/blue-staffy-puppies-london/`, slug `blue-staffy-puppies-london`, kind `location`, hub `/uk-locations/`.

**Q7 — Done looks like (from disk):** research → research board (STOP 1) → outline (STOP 2, approved separately) → page board (STOP 3) → build → all gates (render, Lighthouse, SEO) → Claude verifies → the user approves or fails the page.

**Q10 — Framework (from disk):** decided at the research board (STOP 1). The user picks the angles, strategy and frameworks there, and not before (`research-board-before-outline`).

**Q11 — AIO/GEO approach (from disk):** decided at the research board (STOP 1), with the LLM-intel file `docs/research/llm-intel/blue-staffy-puppies-london-2026-09-25.json` as input.

**Q12 — Visual plan (from disk):** decided on the page board (STOP 3). Every H2/H3 and the hero get an image (rule 17), taken first from the page's own images, then the site's served images, then `Assets/Images/`. The London component kit is the menu.

- **CONSTRAINT:** Never push; commit after every task. Every commit trailer is `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Never merge into `foundation` until the user says so.
- **CONSTRAINT:** No component is chosen and no page board is built before the outline is approved separately (STOP 2, `outline-approved-before-page-board`).
- **CONSTRAINT:** Headers are buyer questions in FAQ style, each answered first by a conversational paragraph. No FAQ-block question repeats a header.
- **CONSTRAINT:** 2,000–3,000 words when the competitor median is NOT FETCHED.
- **CONSTRAINT:** The parents are Maggie (dam) and Jones (sire), with the site's existing parent images. Prices, deposit, delivery, guarantee and age all come from data. The deposit is never called plainly "refundable".
- **CONSTRAINT:** Health: name the tests (L-2-HGA, HC-HSF4, eye and elbow screening) and never state a result. No DNA certificates are held (Lisa, 2026-09-29).
- **CONSTRAINT:** Nothing about the licence goes on the site.
- **CONSTRAINT:** Type fits every tier: no big or chunky headings, and no tall sections or paragraphs (user, 2026-09-28).
- **CONSTRAINT:** Write from the outline only, never from a sibling (rule 8, rule 17). Include six external links on six domains from four source types.

**Q8 — Reader profile:** asked with examples (the 300-mile distance, paying the deposit before seeing the puppy, doubts about delivery, price against London sellers). The user answered: "having to pay the deposit before seeing the puppy, this one". The user also said "the board looks fine", and the pre-filled answers were accepted.

- **CONSTRAINT:** The deposit-first fear is the London buyer's main worry and main reason to leave. The page must answer it head-on: the deposit books the viewing and reserves the puppy, a video call is offered before the deposit, the deposit is up to 70% refundable if a visitor fails to show up, and it comes off the price. All of this comes from the rulings on record and data.

## Decisions Log
- Framework, angles and strategy: to be picked by the user at STOP 1.
- The primary reader fear to resolve is paying the deposit before seeing the puppy (user, Q8).
- The London component kit (15 picks, confirmed 2026-09-29) is the menu; the outline decides the sections.

## Open Flags
- **Research on hand:** a gap matrix exists (2026-09-23 and 2026-09-25), and so does the LLM-intel file for London (2026-09-25). `data/queries/` has no London query file, so competitor research and fan-out (page-run rows 4–7) are still to run.
- **Board:** London has no approved page board. That is expected; it comes at STOP 3.
- **Audit:** London has not been through `@bsuk-content-audit-agent`. It is a stub with 4 words, so an audit adds little; the research board covers the intent and gaps.
- **Hub:** `/uk-locations/` is built. Known Issue 86: the UK hub's body does not link the indexable city pages.

---
<!-- The synthesized fields below are filled in at finalization, from the Q&A Log above. -->
