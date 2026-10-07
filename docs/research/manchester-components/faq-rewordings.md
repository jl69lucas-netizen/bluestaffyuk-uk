# Manchester FAQ rewordings: the three thin wordings, re-proposed for STOP 3

Phase F Task 34 (`docs/superpowers/plans/2026-10-07-manchester-page-run.md`), gap G15. Checked
2026-10-07 on `manchester-page` (base a1a3ae20).

STOP 2 q03 (b) (`docs/reference/answer-board/answers/2026-10-07-outline-blue-staffy-puppies-manchester-uk-2026-10-07.md`)
asked for these three questions to be reworded properly, with new wordings proposed on the page
board. **These are proposals for STOP 3. The approved outline
(`data/outlines/blue-staffy-puppies-manchester-uk.json`, hash 593992436b4531ab) is unchanged.** A
wording takes effect only once the breeder picks it at STOP 3 and it is written to the board record
(Task 35, as an `outline_changes_since_stop2` row).

The builder rule (`.claude/skills/bsuk-location-page-builder/SKILL.md`, Step 5) allows a pick to
be reworded on the page only if its meaning and its fact are unchanged. Plan Step 2 adds that the
new wording must keep the pick's search phrase. Every candidate below adds no "Manchester", no
video call, no rescue wording, no licence and no result.

## The checks each candidate went through

| # | Check | What counts as a fail |
|---|---|---|
| 1 | `PB.header_precheck([q], PB.live_headings(), exclude_page=<own route>)` | any exact, template or five-token shingle match with a live heading |
| 2 | `PB.faq_hits(<board holding q>, live)` | the same, as the FAQ gate reads it (whitelist, no head-term exemption) |
| 3 | `PB.near_copy_hits([q], PB.near_copy_corpus(), exclude_page=(own route, own board))` | within 2 content tokens of a live heading, a board FAQ question or a `data/faq.json` question, or a shared five-content-token run in either order (new, G15) |
| 4 | Within-page repeat: checks 1 and 3 against every other heading and FAQ question in the outline, plus the other two Recommended wordings | any hit |
| 5 | Search phrase (builder rule): deposit = "how much" + "deposit"; delivery = "deliver" + "UK"; DNA = "DNA test" + "L-2-HGA" + "HC-HSF4" | a part of the phrase missing |
| 6 | No-result patterns (`tests/py/test_no_health_result_stated.py` `result_lines`) | any hit. This one is reported, not used to replace: see the DNA option (a) |

The checker is a throwaway script (scratchpad), not a repo file. Its results are copied below.

"Nearest" is the closest corpus entry by content-token distance. A distance of 2 or less is a
near-copy.

A candidate that failed checks 1–5 was replaced. The plan's original candidate and the reason
it failed are recorded under each question.

---

## 1. Top block: `q-how-much-is-the-deposit-2cce23`

- **Pick:** "How Much Is the Deposit?"
- **Outline page wording, now thin:** "How Much Is Your Deposit?" It is a near-copy (distance 0) of "How Much Is the Deposit?", which appears on `/blue-staffy-pup-sale-uk/`, `/blue-staffy-uk-breeders/`, `/uk-blue-staffy-breeders-contact/` and `/uk-blue-staffy-puppy-buying-guide/`.
- **The answer facts:** `deposit_gbp` (£500), "books your viewing and reserves your puppy" (`src/lib/cityKit.ts` `DEPOSIT_HOLDS`, the 2026-09-27 ruling), "comes off the price", and `deposit_refund_clause` as a clause, never plainly "refundable".

| Option | Wording | 1 | 2 | 3 (nearest) | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| **(a) (Recommended)** | **How Much Deposit Reserves One of Your Puppies?** | pass | pass | pass (3: "How Much Is the Deposit?") | pass | pass | n/a |
| (b) | How Much Do I Pay as a Deposit Up Front? | pass | pass | pass (5) | pass | pass | n/a |
| (c) | How Much Deposit Do You Ask to Hold a Puppy? | pass | pass | pass (4) | pass | pass | n/a |

- **(a) Why (Recommended):** it keeps "how much … deposit", and its verb is the one fact the answer opens with: £500 "reserves your puppy". The existing answer then fits word for word. It is the most distinct option that still matches the search phrase, at distance 3. **Trade-off:** it is the closest of the three to the spent "How Much Is the Deposit?" (3 tokens apart against 4–5), and it says "reserves" while the answer also says "books your viewing".
- **(b) Why:** this is the buyer's own phrasing ("pay … up front"), and the furthest from the spent wording (5). **Trade-off:** "up front" invites the question of what is paid later. The answer covers that ("comes off the price"), but the answer has to carry it.
- **(c) Why:** "hold" is the London/bank verb for the deposit. **Trade-off:** "Do You Ask" reads as a negotiation, and "hold" sits beside the H3 "What Does the Deposit Settle Between You and Us as Staffy Breeders?" on the same theme.
- **Replaced:** the plan's "What Deposit Holds a Blue Staffy Puppy for Me?" failed check 5, because it drops "how much". It also failed check 4: its shingle "a blue staffy puppy for" is in the page's §22 H2 "How Do I Ask About a Blue Staffy Puppy for My Greater Manchester Home?". It was replaced by (c).

## 2. Top block: `q-do-you-deliver-across-the-uk-fb0c4a`

- **Pick:** "Do You Deliver Across the UK?"
- **Outline page wording, now thin:** "Do You Deliver Puppies Across the UK?" It is a near-copy (distance 1) of "Do You Deliver Across the UK?" on `/uk-blue-staffy-breeders-contact/` and of the `data/faq.json` `delivery` question.
- **The answer facts:** `delivery_note` ("UK home delivery by DEFRA-approved transport, priced by distance"), the band `delivery_min_gbp`–`delivery_max_gbp` (£200–£350), and collection in `address.city` (Carlisle). "Wherever you are in the UK" is the bank row `about-delivery-home`, which the page's home-delivery answer already uses.

| Option | Wording | 1 | 2 | 3 (nearest) | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| **(a) (Recommended)** | **Which Parts of the UK Do You Deliver Puppies To?** | pass | pass | pass (4: "Do You Deliver Across the UK?") | pass | pass | n/a |
| (b) | Is Home Delivery Available Anywhere in the UK? | pass | pass | pass (4: "Staffy Puppy UK Delivery Available!") | pass | pass | n/a |
| (c) | Can You Deliver a Puppy to Any UK Address? | pass | pass | pass (5: "Can You Deliver a Blue Staffy Puppy to My Location in the UK?") | pass | pass | n/a |

- **(a) Why (Recommended):** it asks about reach, so it stays apart from the same block's "Can My Blue Staffy Puppy Be Delivered to My Home?", which asks about the doorstep. It keeps "deliver" and "UK". **Trade-off:** it is a "which" question, not yes/no. The re-keyed answer has to lead with the reach ("Anywhere in the UK", from `about-delivery-home`) instead of the `delivery` row's "Yes.", then give `delivery_note`, the band and collection in Carlisle.
- **(b) Why:** it stays yes/no, so the present answer fits unchanged. **Trade-off:** "Home Delivery" repeats the theme of the neighbouring home-delivery question, so two adjacent questions read alike.
- **(c) Why:** it is concrete, the buyer's own frame. **Trade-off:** "Any UK Address" is the strongest promise of the three. Our data says "priced by distance", not "every address", so the answer must not say more than `about-delivery-home` does.

All three of the plan's candidates passed every check. None was replaced.

## 3. Middle block: the DNA pick, `q-which-genetic-tests-have-the-parents-had-19da02`

- **Pick:** "Are Both Parents DNA Tested Clear for L-2-HGA and HC-HSF4?"
- **Outline page wording, now thin:** "Are Both Parents DNA Tested Clear for L-2-HGA and for HC-HSF4?" It differs from its own pick by one word ("for"). Its test-name run "L-2-HGA … HC-HSF4" is spent: London's "What Are L-2-HGA and HC-HSF4, and Why Should I Ask About Them?", the health page's "HC-HSF4 and L-2-HGA Tested Staffy Breeders" (the run turned round), the buying guide's heading and `board:blue-staffy-uk-breeders`. The new check 3 reports it as a `near-run` against all four. The set-distance rule alone does not catch it (nearest distance 6), which is why `near_copy_hits` also compares five-token content runs.

**Facts for this question:**
- **STOP 1 q11 (b)** (`docs/reference/answer-board/answers/2026-10-07-research-board-blue-staffy-puppies-manchester-uk-2026-10-07.md`): keep the question, and answer it by naming the tests and saying the certificates are shared on request. Never a result. The evidence ledger's `parents-dna-clear` row holds no proof of a result.
- **The answer today** (`src/lib/manchesterFaq.ts`): "Maggie and Jones are both DNA tested for L-2-HGA, a neurological disorder affecting metabolism, and HC-HSF4, an inherited cataract, and we share their certificates on request." This sentence is excused by its exact text in `tests/py/test_no_health_result_stated.py` (`MANCHESTER_CERTS`, the certificates-on-request ruling). Every option below keeps it word for word.
- **The strict xfail:** `tests/py/test_no_health_result_stated.py` holds `test_manchesters_dna_faq_heading_states_no_result`, marked `xfail(strict=True)` on the current heading, together with `PENDING_REWORD`. It turns red (XPASS) as soon as a heading without "Tested Clear for" ships. **The Recommended wording drops "clear". When it lands at the build (Task 35 / page-run row 12), the xfail test and the `PENDING_REWORD` constant, with its `text.replace` line, must be removed in the same change.**

| Option | Wording | 1 | 2 | 3 (nearest) | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| (a) | Is Each Parent DNA Tested Clear of L-2-HGA, Then of HC-HSF4? | pass | pass | pass (7) | pass | pass | **hit: "Tested Clear"** |
| **(b) (Recommended)** | **Was Each Parent DNA Tested for L-2-HGA as Well as HC-HSF4?** | pass | pass | pass (8) | pass | pass | pass |
| (c) | Did Each Parent Have a DNA Test for L-2-HGA and One for HC-HSF4? | pass | pass | pass (10) | pass | pass | pass |

- **(a) Why:** it keeps "clear" and the pick's meaning unchanged, which is the plan's meaning-preserving option. "Then" separates the two test names, so it is not the spent run. **Trade-off:** "Tested Clear" is matched by the site's no-result pattern (Known Issue 98), so it cannot ship as it stands. The main no-result test would fail on both Manchester routes, and the strict xfail would XPASS, because its filter reads "Tested Clear for". Shipping it needs a breeder ruling that a question is not a stated result, recorded as an exact-text `RULED` entry that cites STOP 1 q11 (b), in place of `PENDING_REWORD` and the xfail.
- **(b) Why (Recommended):** it drops only the result word. It keeps the pick's yes/no form, "DNA Tested", both test names and their order, and "as well as" separates the names so the spent run is not repeated. Its answer can be given in full from our facts: the present answer opens "Maggie and Jones are both DNA tested for L-2-HGA … and HC-HSF4 …" and ends on the certificates on request. That is a "yes" with the tests named, never a result, and it is already a ruled sentence. **Trade-off:** dropping "clear" changes the pick's wording and narrows its meaning, from "were they clear?" to "were they tested?". A buyer who searches "tested clear" finds the answer naming the tests and offering the certificates, not a "clear". Because of that, the strict xfail must be removed at the build, as stated above.
- **(c) Why:** it is the plainest English, and "and One for" makes it unmistakable that there are two tests. It is the furthest from any live wording (10). **Trade-off:** it moves furthest from the pick's words ("Have a DNA Test" for "DNA Tested"), and it is the longest of the three.
- **Replaced (plan (b)):** "What Did the Parents' DNA Tests Cover: L-2-HGA, HC-HSF4 or Both?" failed check 3. "L-2-HGA, HC-HSF4" is still the spent five-token run once the comma is read as a space: a `near-run` with the health page, London, the buying guide and `board:blue-staffy-uk-breeders`. So the plan's reason for it ("avoids the spent run") did not hold. "Or Both?" also suggests that a parent may have had only one test, which our facts do not support. It was replaced by (b).
- **Replaced (plan (c)):** "Which Two DNA Tests Did Maggie and Jones Have Before This Litter?" failed check 5: it drops both test names, which are the search phrase. It also echoes the buy page's live "The Two DNA Tests Maggie and Jones Have Had" (distance 6) and this page's own §8 H2 "Which Health Tests Did Both Parents Have Before This Blue Staffy Litter?". It was replaced by (c).

---

## Adopting any wording: what changes at the build

- **`src/lib/manchesterFaq.ts`:** it keys every answer to the outline's exact question text (`ANSWERS['How Much Is Your Deposit?']`, `ANSWERS['Do You Deliver Puppies Across the UK?']`, `ANSWERS['Are Both Parents DNA Tested Clear for L-2-HGA and for HC-HSF4?']`). The build throws on an unkeyed question ("no answer keyed to the outline question …"). Adopting a new wording therefore means re-keying the entry to the new words, with the answer text unchanged except for the delivery (a) lead noted above. The questions are read from the outline's `sections[].headings`. Because the outline is approved and frozen, the new wording reaches the page through the board record's `outline_changes_since_stop2` row and whatever source the build reads after STOP 3. That routing is the controller's Task 35 / row 12 decision, not this file's.
- **`data/queries/blue-staffy-puppies-manchester-uk.json`:** the builder rule records the wording used on the page in the pick's `covered_by.text`, and `scripts/query_coverage_check.py` holds it.
- **The DNA question:** see the xfail note in §3.

## A finding outside these three questions (for the controller)

With the Recommended wordings substituted, `PB.near_copy_hits` over all 20 of the outline's FAQ questions (corpus `PB.near_copy_corpus()`, own route and own board excluded) still returns **six** hits. All six are outline-approved wordings that STOP 2 q03 did not name:

| Question (outline) | Near-copy of | Where | Apart by |
|---|---|---|---|
| How Much Does Each Blue Staffy Puppy Cost? | How much does a blue Staffy puppy cost? | `board:index` (+4 more) | each |
| Can My Blue Staffy Puppy Be Delivered to My Home? | Can I Get a Blue Staffy Puppy Delivered to My Home? | `/blue-staffy-uk-breeders/` (+1) | be, get |
| Should I See the Mother With Her Puppy Before Money Changes Hands? | Should I See My Puppy With Its Mother Before Any Money Changes Hands? | `/uk-locations/blue-staffy-puppies-london/` (+1) | any |
| Is Blue Staffy Aggressive? | Are Blue Staffies Aggressive? | `/buy-blue-staffy-puppies-uk/` (+1) | staffies, staffy |
| Are Blue Staffies Good Pets? | Are blue Staffies good family pets with children? | `board:index` | children, family |
| Is a Staffordshire Bull Terrier Able to Live in a Flat? | Can a Staffordshire Bull Terrier live in a flat? | `board:uk-staffordshire-bull-terrier-guide` (+1) | able, can |

Task 35's test pins `near_copy_hits` over the board's FAQ questions to `[]`, so as written it will fail on these six. That is a scope decision for the controller: put them on the STOP 3 batch as well, or pin the test to the three q03 questions.
