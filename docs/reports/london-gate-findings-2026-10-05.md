# London gate:page findings — what is the harness, what is the page, what needs Lisa

Page: `/uk-locations/blue-staffy-puppies-london/` · gate: `npm run gate:page -- blue-staffy-puppies-london --skip-record`
First run: HEAD `9fb6e770`, verdict FAIL (dup-body 5, dup-headers 15, aeo 3 WARN, evidence 5 ERROR + 7 WARN).
Every count below was measured on the built page (`dist/uk-locations/blue-staffy-puppies-london/index.html`),
not taken from the report. Nothing on the page was changed; every content change below is a proposal.

## 1. Classification

| Gate item | Count | Class | Evidence |
|---|---|---|---|
| dup-headers: `contact`, `explore`, `follow` | 3 | **Harness bug — fixed** | `--headers` ran one regex over the whole file; the kit footer's three `<h2>`s sit inside a real `<footer>` (SiteFooterKit) on 23 pages. The body path always skipped `<footer>`. Now headers mode skips the same structural chrome (header, footer, nav, form). |
| dup-headers: 8 FAQ questions (+4 template twins) | 12 | **Real page defect — needs Lisa** | Word-for-word questions from `data/faq.json` rows other pages already show. No whitelist covers FAQ text (rule 8). Rule 15 does not cover London: it is not in `data/verbatim/applies.json`. The board pre-check should have warned at STOP 3. It never read a three-block FAQ, which is a harness bug, now fixed. |
| dup-body: 5 runs (FAQ question + answer opening) | 5 | **Real page defect — needs Lisa** (one harness part fixed) | Each run is a bank question plus the first words of its answer. The 36-word guarantee run also held the `guarantee_cover` clause, which CLAUDE.md says must read word for word. The whitelist listed only the other spelling of that field, which is now fixed. The run is 20 words now and still fails. |
| evidence: 5 term-budget ERRORs | 5 | **Rule already in force before London — needs Lisa** | The location ceilings date from 2026-09-16, and the per-city `{city}` term from 2026-09-26. Both predate the 2026-10-03 ruling. That ruling (q04) is about the **board's density table** (block 4c), not these ceilings. `budgets_by_slug` says project 5 pages are judged on the defaults. "city" is the literal word `London` in `<main>`, counted correctly: 60. |
| evidence: 7 WARNs | 7 | **Gate design, works as documented — needs Lisa** | gate:page passes `--fail-on-error` to evidence on a new page, so WARNs fail too. `tests/py/test_gate_page.py` pins this. See section 4. |
| aeo: exit 1 with 0 errors | 3 WARN | **Works as documented** (two harness bugs fixed inside it) | Row 20's gate is `aeo_audit.py <route> --fail-on-error`. That flag fails on WARN, as aeo_audit's docstring says, and `test_a_failing_audit_fails_the_page` pins it. Inside the audit: the place entity was the **former city** (`Glasgow\|Scotland`), and a `£` figure never counted as a stat. Both are fixed. The 3 WARNs on London are still real. |

Also fixed: the body gate and the page board read London's whole **top FAQ block** as site chrome. Its
class `has-rail` contains "rail", so its H2, lede, questions and answers were never compared, and the board
counted "faq-top: 0 prose words". It is compared now, and it adds no duplicate.

## 2. FAQ questions — proposed rewordings (needs your approval; the board changes, then the page)

Each question keeps its search phrase and stays in Title Case, as the page prints it. **(Recommended)** is the
city-free column. The London column clears the duplicate gates too, but it adds one more "London" per
question to a page already at 60 against a ceiling of 8 (section 3). Both sets were tested by putting them
into a copy of the built site: 0 heading and 0 body duplicates for London either way.

| # | Block | Old question | Proposed (Recommended, city-free) | London version | Collides today with |
|---|---|---|---|---|---|
| 1 | bottom | Are Blue Staffies Good Family Pets, Especially With Children? | Are Blue Staffies Good Family Pets in a House With Young Children? | Are Blue Staffies Good Family Pets for a London Home With Children? | / |
| 2 | bottom | Are Blue Staffies Suitable for First-Time Dog Owners? | Are Blue Staffies Suitable for a First-Time Dog Owner? | Are Blue Staffies Suitable for First-Time Dog Owners in London? | /buy-blue-staffy-puppies-uk/ |
| 3 | bottom | Are Staffies Hard to Train? | How Hard Are Staffies to Train? | Are Staffies Hard to Train in a London Home? | /buy-blue-staffy-puppies-uk/ |
| 4 | bottom | Are the Puppies Raised in a Family Home or in Kennels? | Is Your Puppy Raised in a Family Home or in Kennels? | Is My London Puppy Raised in a Family Home or in Kennels? | /blue-staffy-uk-breeders/, /buy-staffy-puppies-for-sale-uk/ |
| 5 | middle | Can I Visit You Before I Decide? | Can I Visit You in Carlisle Before I Decide? | (same) | /uk-blue-staffy-breeders-contact/ |
| 6 | middle | Do You Offer Health Guarantees for Your Blue Staffy Puppies? | Does My Blue Staffy Puppy Come With a Health Guarantee? | (same) | / |
| 7 | top | How Do I Know a Puppy Is Still Available? | How Do I Know a Puppy Is Still Available to Reserve? | How Do I Know a Puppy Is Still Available to Reserve From London? | /buy-blue-staffy-puppies-uk/ |
| 8 | top | How Much Is the Deposit? | What Does the £500 Deposit Cover? *(figure read from `data/settings.json` `deposit_gbp`)* | How Much Is the Deposit to Reserve a London Puppy? | 4 pages |
| 9 | middle | What Is Included When I Buy a Blue Staffy Puppy From BlueStaffyUK? | What Is Included With a Blue Staffy Puppy When It Comes Home? | What Is Included With a Blue Staffy Puppy for a London Home? | / (12-word body run) |

Why the city-free set is recommended: it clears both duplicate gates, adds no "London" to a term that is
already over its ceiling, and with the AEO fix row 8 also clears "no stat-bearing header". The cost is that
the questions read less local. The local part already lives in the block headings and the answers.

### Answer changes (only where the answer's opening words are themselves duplicated)

| # | Old answer opening | Proposed answer | Facts from |
|---|---|---|---|
| 2 | "Yes, for a household with time to give. …" | "Yes, if your household has the time to give. Early socialising, steady reward-based training and company matter more than experience." | `data/faq.json` `listing-first-time-owners` |
| 4 | "In our home, never in kennels. …" | "In our family home in {town}, never in kennels. Every litter grows up indoors with us, among the everyday sights and sounds of a house." | `data/faq.json` `about-home-raised`; `data/settings.json` `address.city` (Carlisle) |
| 6 | "Yes. Every puppy leaves with our written {guarantee_phrase} …" | "Yes. Your puppy comes home with our written {guarantee_phrase} and we ask you to read the full terms before you pay a deposit." | `data/settings.json` `guarantee_label`, `guarantee_cover`, `guarantee_note` (answer board q02, q07, 2026-09-29) |
| 8 | "£500. Books your viewing and reserves your puppy, and it comes off the price." | unchanged if the city-free question is used ("Books your viewing and reserves your puppy, and it comes off the price.") | `data/settings.json` `deposit_gbp`; `src/lib/cityKit.ts` `depositBrief` |

Answers 1, 3, 5, 7 and 9 stay as they are. They are not duplicated, and only their questions are.

## 3. Term budget — your decision

The counts are in `<main>` on the built page. Ceilings come from `data/quality/evidence-budgets.json` → `location`.

| Term | On page | Ceiling | In approved headings | Reviews | Shell + puppy-card line | Places data | Prose + data rows |
|---|---|---|---|---|---|---|---|
| blue staffy | 32 | 10 | 23 | 2 | 0 | 0 | 7 |
| staffy puppies | 22 | 8 | 15 | 1 | 0 | 0 | 6 |
| staffordshire bull terrier | 9 | 5 | 4 | 1 | 0 | 0 | 4 |
| London (`city`) | 60 | 8 | 20 | 6 | 6 | 7 (publisher names: City of London Corporation, London Borough of Sutton…) | 21 |
| UK | 20 | 8 | 1 | 5 | 6 (the mandated "UK home delivery" line on each puppy card) | 0 | 8 |

The approved headings alone are over the ceiling for three terms. No small edit gets London under these
ceilings. The approved board's own density table (block 4c) also aimed higher than these ceilings: Staffordshire
Bull Terrier 16–19 and London 8–13 against ceilings of 5 and 8. The two tools disagree, and the ceilings
are marked uncalibrated (`"calibrated": null`).

- **(a) (Recommended)** Give London an entry in `budgets_by_slug`, with a `_why` naming the approved board
  (STOP 3) and q04 ("London's approved bands stay as they are"). Each budget is the page as built, so the
  entry works as a ratchet. This is how the twelve project 4 pages were handled (Known Issue 34). Then calibrate
  the location ceilings before the next city. Why: 23 of the 32 "blue staffy" are in headings you approved,
  and 6 of the 20 "UK" are the delivery line every puppy card must carry. Trade-off: London ships at a
  density the uncalibrated ceiling calls heavy, until the calibration says otherwise.
- (b) Rewrite London to fit the defaults. That means rewording about 20 approved headings and roughly 50
  "London"s. It is a re-board, not a fix.

## 4. Evidence WARNs (these fail gate:page on a new page even after section 3)

| WARN | Real? | What it needs |
|---|---|---|
| claim `tests-named-no-result` made 4× with proof NOT FETCHED: "say it once and link the trust section" | Yes, as advice. The proof will never exist, by your ruling: name the tests, state no result. | Name the tests in full once (#health-tests) and link there from the trust strip, the takeaways and FAQ 07. That is a content change. Or rule that this row is exempt from the repeat check. |
| statement label missing on #trust, #key-takeaways, #deposit-viewing, #faq-middle, #health-tests | No (a PROXY hit) | The signal is the test **name** "HC" in "HC-HSF4". The rule puts a label on a *proven* claim, and these sentences only name a test. The proxy cannot tell the two apart. Your call: accept, or have the check skip naming-only sentences. |
| statement label missing on #everyday-health | Yes | "A Staffy lives 12 to 14 years" is a breed fact read from `data/breed-standards.json`. A StatementLabel on it is a visual change, so it would need a preview first. |

## 5. AEO WARNs (row 20 gate)

| WARN | What fixes it | Content? |
|---|---|---|
| no stat-bearing header | Question 8, city-free version, "What Does the £500 Deposit Cover?" (tested: the WARN clears) | heading change |
| no binomial (Canis lupus familiaris) | One neutral-register sentence in the breed section, for example: "The Staffordshire Bull Terrier is a breed of domestic dog, *Canis lupus familiaris*." (`rules/copy.md` allows neutral register for taxonomy) | one sentence |
| pronoun-heavy: 141 we/our/us against 65 named entities (with the place fix) | Swap about 21 "we/our" for "Lisa Bright" or "BlueStaffyUK", which takes the ratio under 2%. This pulls against working rule 1 (first-person voice), so it is yours to weigh. | prose |
