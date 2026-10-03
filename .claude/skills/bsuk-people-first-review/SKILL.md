---
name: bsuk-people-first-review
description: Use when a BlueStaffyUK page board or built page is checked against Google's helpful-content guidance — "is this people-first", "E-E-A-T", "helpful content", "effort / originality / accuracy", "who wrote it", "is this tool a gimmick", "would Google see this as low quality" — before STOP 3 approval and again at page-run row 16, before the close. (BlueStaffyUK)
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

# People-first review

**Core principle:** a review finds what the page *does*. It never adds a fact, a figure or a promise of its own. Every fix you suggest must be made only of words that already sit in a `data/` file, on the approved board, or in the breeder's saved answers. Anything else is a **question for Lisa**, never a rewrite.

The source of what Google asks for is `docs/reports/google-helpful-content-analysis-2026-10-03.md` (the guide was last updated 2026-10-01). Re-read its section A before your first review in a session.

## The four checks, in order

| # | Check | Ask | Evidence to cite |
|---|---|---|---|
| 1 | **Purpose** | What does the London (city, buy…) buyer come to do, and how many words down does the page let them do it? | the board's `brief.goal`, the section order, word positions |
| 2 | **Effort · Originality · Skill · Accuracy** (Google's main-content attributes) | What on this page could no marketplace or competitor say? Is every claim in a data file or the evidence ledger? | `data/*.json`, `data/quality/evidence-ledger.json`, board Cat C rows |
| 3 | **Who · How · Why** | Is there a byline and Person markup? Has Lisa read the finished prose (`breeder_review` in `data/page-runs/<slug>.json`)? Is the AI drafting disclosed where a reader would expect it? | the layout, the page-run record, the About page |
| 4 | **Search-engine-first signs** | Is anything written to a word count or a keyword count? Does a heading promise an answer the data can't give? Do sections repeat each other? Is a tool there for show? | board `words` bands, the density block, headings vs data |

## Interactive tools: genuine or gimmick

A tool is **genuine** only when every value it shows already exists in a data file **and** it serves the page's purpose (check 1). If any value would have to be estimated (a postcode price, a running cost, a puppy's temperament), the tool is a **gimmick** and the review says so. Seen on London: the video-call checklist is genuine; the postcode calculator and the "which puppy" quiz are gimmicks.

## Output: one table, three kinds of row

| Kind | Who acts | Example |
|---|---|---|
| **Copy fix** | the builder, inside the approved board | shorten an FAQ answer that repeats a section; answer a heading honestly from the band |
| **Board change** | goes to the answer board; the breeder approves first | moving the puppy strip up; adding a tool |
| **Question for Lisa** | the answer board | "Have you delivered to London before?" |

Write each row as: check # · what you saw (quote the page) · the fix · its source file. A fix with no source file is a question, not a fix.

## Red flags: stop and rewrite your row

| You were about to | Instead |
|---|---|
| Add a distance, mileage or journey time ("300 miles away") | Only the delivery band or collection from the town: CLAUDE.md, the location builder |
| Promise a service ("send your postcode and we'll confirm") | A question for Lisa |
| Call a correct fact an error because it reads oddly ("Maggie is a dog", so a video call "with Maggie" must be wrong) | Check the data first; Maggie is the dam, and the video call with mum is the angle |
| Add a nice-sounding clause ("results available on request") | Only when a data file or answer says so |
| Rewrite an approved heading | Answer it honestly, or raise a board change |
| Pad toward a word or keyword count | Google has no preferred count; a section ends when its question is answered |

## Common mistakes

- Treating the review as polish. Purpose (check 1) and accuracy (check 2) outrank style.
- Recommending a byline with no recorded read. The byline is honest only once `breeder_review` is on the record (answer board q01, 2026-10-03).
- Mixing copy fixes with board changes. The breeder approves board changes; never slip one in as a "quick fix".
