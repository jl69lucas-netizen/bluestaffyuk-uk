# CAG For-Sale Rules Check

*London page run, 2026-09-30. Sources: CAG's own files (`congoafricangreys-com`: `rules/for-sale.md`, `rules/headings.md`, `.claude/skills/cag-for-sale-page-builder/SKILL.md`, `cag-bird-page-excellence`), CAG's Universal Page Build Brief (§12, §16, §19d), and BSUK's ports of them. Full rule-by-rule table: `docs/reports/for-sale-rules-vs-london-2026-09-30.md`.*

## Verdict

- **BSUK's port of CAG's for-sale rules is faithful.** Every rule in CAG's `rules/for-sale.md` is in BSUK's `rules/puppies.md`. BSUK added three rules with tests (one Product per pup, no `InStock` on a sold pup, no head-cropped portraits), and the delivery rule gained a test.
- **The builder skill lost six items in the port.** They are listed under "Dropped in the port" below.
- **The H5/H6 exception came from CAG, not from the port.** CAG's `rules/headings.md` makes "≥5 H5 and ≥5 H6" a warning on location pages, in the same words as BSUK's copy. CAG's build brief (§12 and §19d) states it with no exception. Your ruling makes it hard for project 5 pages; that change is in progress.
- **London missed 10 of the rules that apply to it.** They are listed under "Missed on London". Two need a ruling from you, and the rest can go into the outline before you approve it.
- **One CAG skill was never ported: `cag-bird-page-excellence`.** It is being ported now as `bsuk-puppy-page-excellence`. `cag-header-search` is the header's site-search bar, not a heading rule.

## Dropped in the port

| CAG rule (for-sale builder) | In BSUK? | Applies to London? | Recommendation |
|---|---|---|---|
| **Two-Keyword Headers** (Rule 28b): each major header carries two distinct keyword types | Only in `bsuk-seo-master-checklist`, not in the puppy or location builders | Yes | Add to the location builder, and check it on London's outline now (**Recommended**) |
| **Negative-keyword counter-positioning**: "cheap", "scam" and "free" queries handled head-on with green-flag framing, linking to the scam content | Dropped | Yes. Google's "People also search for" shows "blue staffy puppies london cheap" and "free blue staffy puppies london" | Add one outline H4 (or FAQ answer) that meets "cheap" honestly with our real price and deposit terms (**Recommended**) |
| **GEO fact tables**: small fact tables that signal answerability | Dropped | Yes | Add one fact table to the delivery or litter section (a table shape on the page board, per working rule 13) |
| **Separate blog and contact H2s** (manual pass list) | Dropped | Yes, at build | Add to the London page test list (Task 26) |
| **Dial TOC compact spec** (196px sidebar, 64px ring) | Dropped | No | BSUK's design system sets its own dial. Keep as is |
| **IndexNow after every page** | Inactive until project 6 | Not yet | Keep as is (CLAUDE.md, Deploy) |

**CAG contradicts itself on meta length.** The builder's §2e says titles are one clause, ≤70 characters (2026-09-09), while §6a and `rules/for-sale.md` still say up to 280. BSUK kept the 280 rule, but the built for-sale pages use 50–60-character titles and nothing tests the 280 rule. **Recommended:** retire the 280 rule in `rules/puppies.md` to match CAG's 2026-09-09 ruling. Trade-off: none of the live pages change.

## Missed on London

| # | Rule | Fix | When |
|---|---|---|---|
| M1 | Entity + Feature + Benefit + Purpose opening under every H2/H3/H4 | State the formula in the outline; the build's opener must answer the heading's question first, then carry all four | Outline now; build Task 27 |
| M2 | A reserve/enquire CTA every 500–700 words | Add an `#enquiry` link at the end of rows 8, 10, 14 and 17 (about every 600 words); test ≥3 | Outline now; test in Task 26 |
| M3 | Five variants for the H1 and each major H2, you pick | Show 5 variants per body H2 on the outline board, one marked (Recommended) | STOP 2 |
| M4 | Header duplicate check before outline approval | Run the heading crossover against every other board and outline, and show the result with the outline | Before STOP 2 |
| M5 | A seam divider before every section, with a parity check | Add `SectionDivider` to the London component map and test seams = sections | Component map (Task 21), test in Task 26 |
| M6 | ≥5 H5 and ≥5 H6 | In progress: rule made hard for project 5 pages; London's tree being extended | Now |
| M7 | H2 25–35, H3 40–50 (Rule 28) | **Needs your ruling.** No built page meets it (for-sale pages: 11–16 H2), and 25+ H2 in 3,000 words is about 80 words each | Your answer |
| M8 | Every section names the buyer fear it answers | Add a `fear` line per body row, from the research board's buyer fears | Outline now |
| M9 | An image on each key H4, as well as H2/H3 | Give 2–4 key H4s an image slot (for example "Is the Transport DEFRA-Approved?") | Outline now |
| M10 | Keyword-type caps (primary 30–35, LSI 20–25, long-tail 15–20; total ≤105) | Run `bsuk-keyword-verifier` on the built page and record its table | Task 33 |

## Stale lines found

- `rules/puppies.md:27` and the location builder (`SKILL.md:80`) still say "the £500 deposit is refundable". Plan Ruling 2 says it is never called plainly refundable. **Fix:** reword both to point at the deposit data key.
- `rules/puppies.md` item (3), carried over from CAG, keeps the **H1 first in the DOM** and moves the image with CSS `order`. `rules/design.md` rule 10 (a later BSUK rule, tested) puts the **hero image first in the DOM**. They contradict each other. **Fix:** amend `rules/puppies.md` (3) to point at design rule 10, which is the one the tests enforce.

## What I recommend now

1. Fold M1, M2, M4, M8, M9, Two-Keyword Headers, the "cheap" counter-position and one GEO fact table into London's outline before you see it again. **(Recommended)** Why: each is a CAG for-sale rule that applies to a transactional city page, and all are cheap to add before the build. Trade-off: the outline grows by about 150 words, still inside 2,000–3,000.
2. Show 5 variants per body H2 (M3) on the next outline board.
3. Answer M7 (the H2/H3 bands) and the meta-length retirement.
4. Fix the two stale "refundable" lines.
