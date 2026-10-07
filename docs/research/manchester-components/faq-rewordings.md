# Manchester FAQ rewordings: nine thin wordings, re-proposed for STOP 3

Phase F Task 34 (`docs/superpowers/plans/2026-10-07-manchester-page-run.md`), gap G15. Checked
2026-10-07 on `manchester-page` (base a1a3ae20). §§1–3 are the three questions STOP 2 q03 named;
§§4–9, added the same day (base a5c24629), are the six more approved wordings that `near_copy_hits`
still flagged (the finding at the end of the first pass). The user's q03 (b) ruling ("Reword them
properly") and London's lesson 18 (copied FAQ questions forced a late re-board) apply to them too.

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
| 4 | Within-page repeat: checks 1 and 3 against every other heading and FAQ question in the outline, plus the other two Recommended wordings. For §§4–9: against the H1, every outline heading and all 20 FAQ questions, with the nine thin wordings taken out and the three q03 Recommended wordings and the other five new Recommended wordings put in | any hit |
| 5 | Search phrase (builder rule): deposit = "how much" + "deposit"; delivery = "deliver" + "UK"; DNA = "DNA test" + "L-2-HGA" + "HC-HSF4"; cost = "how much" + "blue staffy" + "puppy" + "cost"; home delivery = "blue staffy puppy" + "deliver(ed/y)" + "home"; mother = "see" + "mother" + "puppy" + "before" + "money"; aggressive = "blue staffy" + "aggressive"; pets = "blue staffies" + "good" + "pets"; flat = "Staffordshire Bull Terrier" + "live" + "flat" (a stem counts: "living", "seen", "pet") | a part of the phrase missing |
| 6 | No-result patterns (`tests/py/test_no_health_result_stated.py` `result_lines`) | any hit. This one is reported, not used to replace: see the DNA option (a) |

The checker is a throwaway script (scratchpad), not a repo file. Its results are copied below.

"Nearest" is the closest corpus entry by content-token distance. A distance of 2 or less is a
near-copy.

A "(keep)" row (§§4–9) is the approved outline wording as it stands, with its hit, so the breeder can
choose to keep it; it is not a proposal, and it fails check 3 by definition.

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

## 4. Top block: the price pick, `q-how-much-does-a-blue-staffy-cost-uk-4051c2`

- **Pick:** "How Much Does a Blue Staffy Puppy Cost?"
- **Outline page wording, now thin:** "How Much Does Each Blue Staffy Puppy Cost?" It is a near-copy (distance 1, apart by "each") of "How much does a blue Staffy puppy cost?" on `board:index`, and of four more: the Edinburgh and Sunderland stubs, `board:blue-staffy-uk-breeders` and `board:uk-blue-staffy-puppy-buying-guide`. Check 4 also fails it: its five-word run "does each blue staffy puppy" is in this page's own outline row 9 H3 "Where Does Each Blue Staffy Puppy Spend Its First Weeks in Our Carlisle Home?" (the outline's crossover record shows no in-page repeat, so its run did not catch this one).
- **The answer facts:** `listing-cost`'s first sentence ("Each puppy is listed with its own price, so you see the figure before you enquire"), then this litter's prices by sex, read from `data/price-matrix.json` and the names from `data/puppies.json` (`src/lib/manchesterFaq.ts`). No price is typed, in the question or the answer.

| Option | Wording | 1 | 2 | 3 (nearest) | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| (keep) | How Much Does Each Blue Staffy Puppy Cost? | pass | pass | **hit** (1: "How much does a blue Staffy puppy cost?", `board:index` +4) | **hit** ("does each blue staffy puppy", row 9 H3) | pass | pass |
| **(a) (Recommended)** | **How Much Will the Blue Staffy Puppy I Choose Cost?** | pass | pass | pass (3: "How much does a blue Staffy puppy cost?") | pass | pass | pass |
| (b) | How Much Does a Boy or Girl Blue Staffy Puppy Cost? | pass | pass | pass (3: the same) | pass | pass | pass |
| (c) | How Much Is a Boy or a Girl Blue Staffy Puppy Going to Cost? | pass | pass | pass (5: the same) | pass | pass | pass |

- **(a) Why (Recommended):** it keeps "how much … blue staffy puppy … cost", and it holds whatever the data says. The answer reads the prices from `data/price-matrix.json`, so the question must not assume how they are set; "the puppy I choose" is true of this litter and of the next one, whatever rule prices it. The present answer fits word for word ("Each puppy is listed with its own price …"), and "choose" echoes the bank row `listing-cost` ("secures the one you choose"). **Trade-off:** "Will" replaces the pick's "Does", so the exact searched string "how much does a blue staffy puppy cost" is no longer one run. At distance 3, it is as close to the spent wording as (b).
- **(b) Why:** it keeps the pick's "How Much Does a … Blue Staffy Puppy Cost" almost whole, and "boy or girl" fits the answer exactly: the price follows the sex in this litter. **Trade-off:** the question carries the pricing rule. If a later litter is priced another way (outline row 10's H6 "Will the Same Price Rule Apply to Our Next Litter?" leaves that open), the answer will still read the right figures from data, but the question will be wrong and has to be re-worded.
- **(c) Why:** the furthest of the three from the spent wording (5), in spoken English. **Trade-off:** it carries the same pricing rule as (b), and it is the longest and least like the searched phrase.
- **Replaced:** "How Much Will Each Blue Staffy Puppy in This Litter Cost?" failed checks 1–3: it shares the run "each blue staffy puppy in" with London's live "How Much Is Each Blue Staffy Puppy in This Litter?", 2 tokens apart. "How Much Do the Blue Staffy Puppies in This Litter Cost?" failed check 3 (near-run "how much do blue staffy", London's "How Much Do Blue Staffy Puppies Cost in the UK?"). "How Much Would One of Our Blue Staffy Puppies Cost You?", "How Much Will My Blue Staffy Puppy Cost, Boy or Girl?", "How Much Should I Expect a Blue Staffy Puppy to Cost?" and "How Much Does It Cost to Buy One of Your Blue Staffy Puppies?" each failed check 1 on a spent five-word run (Glasgow's "of our blue staffy puppies", London's "will my blue staffy puppy", the pup-sale page's "a blue staffy puppy to" and "one of your blue staffy"). "How Much Will Our Blue Staffy Puppy Cost Us to Buy?" passed every check, but in a buyer's question "Our" reads as our own voice (working rule 1), so it was dropped.

## 5. Top block: the home-delivery pick, `q-can-i-get-a-blue-staffy-puppy-delivered-ad16e3`

- **Pick:** "Can I Get a Blue Staffy Puppy Delivered to My Home?"
- **Outline page wording, now thin:** "Can My Blue Staffy Puppy Be Delivered to My Home?" It is a near-copy (distance 2, apart by "be" and "get") of the About page's live "Can I Get a Blue Staffy Puppy Delivered to My Home?" and of the `data/faq.json` `about-delivery-home` question.
- **The answer facts:** `about-delivery-home`, its two sentences joined and its "safe and reliable" and "services" left out: "Yes. We offer UK-wide puppy delivery using DEFRA-approved pet transport, so wherever you are in the UK your new de-wormed puppy can arrive at your doorstep comfortably and securely."

| Option | Wording | 1 | 2 | 3 (nearest) | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| (keep) | Can My Blue Staffy Puppy Be Delivered to My Home? | pass | pass | **hit** (2: "Can I Get a Blue Staffy Puppy Delivered to My Home?", `/blue-staffy-uk-breeders/` +1) | pass | pass | pass |
| **(a) (Recommended)** | **Is Home Delivery an Option for My Blue Staffy Puppy?** | pass | pass | pass (4: "Blue Staffy Puppy Gallery") | pass | pass | pass |
| (b) | Can I Have My Blue Staffy Puppy Delivered Right to My Home? | pass | pass | pass (3: "Can I Get a Blue Staffy Puppy Delivered to My Home?") | pass | pass | pass |
| (c) | Can a Blue Staffy Puppy Travel From Your Home to Mine by Delivery? | pass | pass | pass (4: the same) | pass | pass | pass |

- **(a) Why (Recommended):** it is a real rewording, not the pick with a word swapped: "home delivery" is the buyer's own term for the service, it keeps the yes/no form so the answer still opens "Yes.", and it stays clear of the same block's reach question ("Which Parts of the UK Do You Deliver Puppies To?", q03 (a)). **Trade-off:** "delivered to my home" becomes "home delivery", so the searched verb form is not kept word for word. If the breeder picks q03 delivery (b), "Is Home Delivery Available Anywhere in the UK?", the two questions in one block would both open "Is Home Delivery …"; with that pick, (b) or (c) here is the better partner.
- **(b) Why:** it is the closest to the pick ("Can I … My Blue Staffy Puppy Delivered … to My Home"), so the search phrase is kept almost word for word. **Trade-off:** at distance 3 it is the closest to the spent wording, and "Right" is mostly there to set it apart, so a reader can still see the About page's question in it. That is the thinness q03 (b) asked us to fix.
- **(c) Why:** the furthest from the spent wording in form, and "travel" matches the H2 of the delivery section ("How Will Your Blue Staffy Puppy Travel to Greater Manchester?"). **Trade-off:** "From Your Home to Mine" is the most stylised of the three, and the word "home" now names both our home and the buyer's.
- **Replaced:** "Is Delivery of a Blue Staffy Puppy to My Home Possible?" failed check 1 (the Aberdeen stub's "of a blue staffy puppy"). "Will You Deliver My Blue Staffy Puppy Right Up to My Home?" passed every check (6) but "Right Up to" only pads the pick, so (c) took its place.

## 6. Middle block: the mother-and-puppy pick, `q-how-can-i-avoid-buying-from-a-puppy-5e9d7e`

- **Pick:** "Should I See the Puppy With Its Mother Before Any Money Changes Hands?"
- **Outline page wording, now thin:** "Should I See the Mother With Her Puppy Before Money Changes Hands?" It is a near-copy (distance 1, apart by "any") of London's live "Should I See My Puppy With Its Mother Before Any Money Changes Hands?" and of `board:blue-staffy-puppies-london`'s wording.
- **The answer facts:** the STOP 2 q04 (a) answer, approved as worded, every figure read: "See them together before you commit to a puppy. With us the £`deposit_gbp` deposit comes first: it books your viewing and reserves your puppy, it comes off the price, and it is `deposit_refund_clause`. At the viewing you see both parents, their registration papers and the veterinary records before you commit to a puppy, and again on the day you collect." Each option below is a question that answer answers: it advises seeing them together, and says plainly that our deposit comes first.

| Option | Wording | 1 | 2 | 3 (nearest) | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| (keep) | Should I See the Mother With Her Puppy Before Money Changes Hands? | pass | pass | **hit** (1: London's "Should I See My Puppy With Its Mother Before Any Money Changes Hands?" +1) | pass | pass | pass |
| **(a) (Recommended)** | **Is It Wise to See the Mother and Puppy Together Before Money Changes Hands?** | pass | pass | pass (4: London's, as above) | pass | pass | pass |
| (b) | Do I Need to See the Mother Beside Her Puppy Before Paying Any Money? | pass | pass | pass (7: "See the Puppy With Its Mother", buying guide) | pass | pass | pass |
| (c) | Should the Puppy Be Seen With Its Mother Before Money Changes Hands? | pass | pass | pass (4: London's) | pass | pass | pass |

- **(a) Why (Recommended):** the q04 answer's first sentence, "See them together before you commit to a puppy", answers it word for word ("together"), and it keeps every part of the pick: see, mother, puppy, before money changes hands. **Trade-off:** it still ends on "money changes hands", the three-word tail London uses, so it is 4 apart where (b) is 7. "Is It Wise" also makes it an opinion question, where the pick asks for advice ("Should I").
- **(b) Why:** the furthest from every live wording (7), and "before paying any money" is how a buyer says it. **Trade-off:** it drops the idiom "money changes hands" that the pick and London share, and "Do I Need to" reads as a rule, so the answer's "the deposit comes first" has to do more work to answer it.
- **(c) Why:** it keeps the pick's "Should" and its order (puppy, then mother). **Trade-off:** a passive question is harder to read, and it is the closest of the three to London in form, so a reader may still see London's question in it.
- **Replaced:** none. All three first candidates passed every check.

## 7. Bottom block: the temperament pick, `q-are-blue-staffy-aggressive-55b447`

- **Pick:** "Is blue Staffy aggressive?" (PAA wording)
- **Outline page wording, now thin:** "Is Blue Staffy Aggressive?" It is the pick verbatim (no `faq_rewordings` row). It is a near-copy (distance 2, apart by "staffies"/"staffy") of the buy page's live "Are Blue Staffies Aggressive?" and of the `data/faq.json` `listing-aggressive` question, the row its answer is taken from.
- **The answer facts:** `listing-aggressive`, word for word: "No. The Staffordshire Bull Terrier is not a banned breed in the UK and is bred as a companion; our breed guide covers the law and the reputation together."

| Option | Wording | 1 | 2 | 3 (nearest) | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| (keep) | Is Blue Staffy Aggressive? | pass | pass | **hit** (2: "Are Blue Staffies Aggressive?", `/buy-blue-staffy-puppies-uk/` +1) | pass | pass | pass |
| **(a) (Recommended)** | **Is a Blue Staffy an Aggressive Dog by Nature?** | pass | pass | pass (4: "Are Blue Staffies Aggressive?") | pass | pass | pass |
| (b) | Does a Blue Staffy Have an Aggressive Temperament? | pass | pass | pass (4: "🐾 What is the temperament of a Blue Staffy?", Middlesbrough stub) | pass | pass | pass |
| (c) | Is a Blue Staffy Likely to Be Aggressive at Home? | pass | pass | pass (5: "Welcome a Blue Staffy Into Your Home", About page) | pass | pass | pass |

- **(a) Why (Recommended):** "by nature" is exactly what the answer answers: "No … bred as a companion". It keeps "blue staffy" and "aggressive" and the yes/no form, so the answer is unchanged, and it puts right the pick's broken grammar ("Is Blue Staffy"). **Trade-off:** "by nature" narrows the question a little, to how the dog is born and bred, not how it is raised. The answer's link to the breed guide carries the rest.
- **(b) Why:** "temperament" is the breed-guide word, and the answer fits it. **Trade-off:** the Middlesbrough stub's "What is the temperament of a Blue Staffy?" is 4 tokens away, a different question but the nearest echo, and "Have an Aggressive Temperament" is the most formal of the three.
- **(c) Why:** it puts the question in the buyer's own house, the furthest from live wordings (5). **Trade-off:** "Likely" asks for a forecast and "at Home" narrows the scene. The bank answer is about the breed, not one dog in one house, so the fit is the loosest of the three.
- **Replaced:** "Is the Blue Staffy Known for Being Aggressive?" passed every check (4), but the answer opens "No.", and the breed does carry that reputation (the answer's own breed-guide link "covers … the reputation"). So the answer would deny a true premise. It was replaced by (c).

## 8. Bottom block: the family-home pick, `q-do-blue-staffy-suit-a-family-home-d39c23`

- **Pick:** "Are blue staffies good pets?" (PAA wording)
- **Outline page wording, now thin:** "Are Blue Staffies Good Pets?" It is the pick verbatim (no `faq_rewordings` row). It is a near-copy (distance 2, apart by "children" and "family") of `board:index`'s "Are blue Staffies good family pets with children?".
- **The answer facts:** `listing-family-dog`, its dash a full stop: "Yes. The breed's old nickname is the nanny dog, and our breed guide explains where that reputation came from and what it asks of a household with children."

| Option | Wording | 1 | 2 | 3 (nearest) | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| (keep) | Are Blue Staffies Good Pets? | pass | pass | **hit** (2: "Are blue Staffies good family pets with children?", `board:index`) | pass | pass | pass |
| **(a) (Recommended)** | **Are Blue Staffies Good Pets for an Ordinary Household?** | pass | pass | pass (4: `board:index`'s, as above) | pass | pass | pass |
| (b) | Would a Blue Staffy Make a Good Pet for My Household? | pass | pass | pass (7: "Available Blue Staffy Puppies") | pass | pass | pass |
| (c) | Are Blue Staffies Good Pets Day to Day? | pass | pass | pass (3: `board:index`'s) | pass | pass | pass |

- **(a) Why (Recommended):** it keeps the searched question "Are Blue Staffies Good Pets" whole, and "household" is the answer's own word ("what it asks of a household"), so the answer fits unchanged. It also stays apart from the same block's "Do Blue Staffies Make Good Family Pets for Homes With Children?" (no "family", no "children"). **Trade-off:** the new words are added at the end, so the question is the pick with a qualifier, not a rebuilt sentence. "Household" also repeats a word of the block's H2 ("… for Manchester Households?").
- **(b) Why:** a rebuilt sentence, the furthest from any live wording (7), in the buyer's voice ("My Household"). **Trade-off:** it loses the plural search phrase "blue staffies good pets" (stems only), and "Make a Good Pet" sits near the same block's "Make Good Family Pets", though the gate finds no hit.
- **(c) Why:** the shortest change, about everyday life rather than one kind of home. **Trade-off:** at distance 3 it is the closest to `board:index`'s question, and "Day to Day" is vague. The answer is about a household with children, not the daily routine.
- **Replaced:** "Is a Blue Staffy a Good Pet to Have in the House?" failed check 1 (the buying guide's "is a blue staffy a"). The first form of (b) said "Our Household"; "Our" in a buyer's question reads as our own voice (working rule 1), so it became "My".

## 9. Bottom block: the flat pick, `q-can-a-staffy-live-in-a-flat-310055`

- **Pick:** "Can a Staffordshire Bull Terrier Live in a Flat?"
- **Outline page wording, now thin:** "Is a Staffordshire Bull Terrier Able to Live in a Flat?" It is a near-copy (distance 2, apart by "able" and "can") of `board:uk-staffordshire-bull-terrier-guide`'s "Can a Staffordshire Bull Terrier live in a flat?" and of the `data/faq.json` `guide-flat-living` question.
- **The answer facts:** `guide-flat-living`, word for word: "Yes, provided the dog gets its daily exercise and mental stimulation. The breed is a medium size and is people-focused rather than territorial, so a large garden is not essential as long as walks and outdoor time are regular."

| Option | Wording | 1 | 2 | 3 (nearest) | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| (keep) | Is a Staffordshire Bull Terrier Able to Live in a Flat? | pass | pass | **hit** (2: "Can a Staffordshire Bull Terrier live in a flat?", `board:uk-staffordshire-bull-terrier-guide` +1) | pass | pass | pass |
| **(a) (Recommended)** | **Will a Staffordshire Bull Terrier Be Happy Living in a Flat?** | pass | pass | pass (6: "Why the Staffordshire Bull Terrier") | pass | pass | pass |
| (b) | Will a Flat Give a Staffordshire Bull Terrier Enough Room to Live? | pass | pass | pass (5: the breed guide board's question) | pass | pass | pass |
| (c) | Is Living in a Flat Fair on a Staffordshire Bull Terrier? | pass | pass | pass (4: "Why the Staffordshire Bull Terrier") | pass | pass | pass |

- **(a) Why (Recommended):** the answer's "Yes, provided the dog gets its daily exercise and mental stimulation" is a welfare answer, and "Be Happy" asks the welfare question directly. It is the furthest from the spent wording (6), keeps "Staffordshire Bull Terrier … flat", and "Living in a Flat" holds the search phrase's stem. **Trade-off:** "live" becomes "living", and "happy" goes a step past the pick's plain "can it?". The answer covers it through "provided …", but it does not say "happy".
- **(b) Why:** "enough room" is answered by the answer's own fact, "a medium size … a large garden is not essential", and the verb "live" is kept. **Trade-off:** it puts the question on the flat's size, where the answer's first condition is exercise, so the answer has to lead with something other than what was asked.
- **(c) Why:** the shortest of the three, and "fair on" asks the welfare question as (a) does. **Trade-off:** "Fair on" is a British idiom that reads as a judgement, and a buyer may hear "is it cruel?" in it, which the answer does not address.
- **Replaced:** "Does a Staffordshire Bull Terrier Need a House, or Can It Live in a Flat?" failed checks 1–3 (the breed guide's "How Much Exercise Does a Staffordshire Bull Terrier Need Daily?": the run "does staffordshire bull terrier need"). "Could a Staffordshire Bull Terrier Live Happily in a Flat?" and the same with "Without a Garden" failed check 1 on London's "a staffordshire bull terrier live" ("Can a Staffordshire Bull Terrier Live in a London Flat?"). "Is a Flat Big Enough for a Staffordshire Bull Terrier to Live In?" failed check 1 on the breed guide's "for a staffordshire bull terrier".

---

## Adopting any wording: what changes at the build

- **`src/lib/manchesterFaq.ts`:** it keys every answer to the outline's exact question text (`ANSWERS['How Much Is Your Deposit?']`, `ANSWERS['Do You Deliver Puppies Across the UK?']`, `ANSWERS['Are Both Parents DNA Tested Clear for L-2-HGA and for HC-HSF4?']`). The build throws on an unkeyed question ("no answer keyed to the outline question …"). Adopting a new wording therefore means re-keying the entry to the new words, with the answer text unchanged except for the delivery (a) lead noted above. The questions are read from the outline's `sections[].headings`. Because the outline is approved and frozen, the new wording reaches the page through the board record's `outline_changes_since_stop2` row and whatever source the build reads after STOP 3. That routing is the controller's Task 35 / row 12 decision, not this file's.
- **`data/queries/blue-staffy-puppies-manchester-uk.json`:** the builder rule records the wording used on the page in the pick's `covered_by.text`, and `scripts/query_coverage_check.py` holds it.
- **The DNA question:** see the xfail note in §3.
- **The six more (§§4–9):** the same re-keying, one `ANSWERS` entry each, from the outline wording to the adopted one:
  `'How Much Does Each Blue Staffy Puppy Cost?'`, `'Can My Blue Staffy Puppy Be Delivered to My Home?'`,
  `'Should I See the Mother With Her Puppy Before Money Changes Hands?'`, `'Is Blue Staffy Aggressive?'`,
  `'Are Blue Staffies Good Pets?'` and `'Is a Staffordshire Bull Terrier Able to Live in a Flat?'`. Every answer
  text stays as it is, Recommended or not. The price answer goes on reading the prices from
  `data/price-matrix.json` and the names from `data/puppies.json`, and the mother answer stays the STOP 2 q04 (a)
  wording, its figures read. The `covered_by.text` of six picks in `data/queries/blue-staffy-puppies-manchester-uk.json`
  is set to the adopted wording: `q-how-much-does-a-blue-staffy-cost-uk-4051c2`,
  `q-can-i-get-a-blue-staffy-puppy-delivered-ad16e3`, `q-how-can-i-avoid-buying-from-a-puppy-5e9d7e`,
  `q-are-blue-staffy-aggressive-55b447`, `q-do-blue-staffy-suit-a-family-home-d39c23` and
  `q-can-a-staffy-live-in-a-flat-310055`. All six are `null` today, as are the three in §§1–3. Four of the six have
  an outline `faq_rewordings` row (price, home delivery, mother, flat), whose `page_wording` the
  `outline_changes_since_stop2` row supersedes. The temperament and family-home questions are the picks verbatim and
  have no row today, so adopting a wording for either one is a new rewording of the pick. The builder rule allows that
  (meaning and fact unchanged), and it is recorded the same way.

## The finding that opened §§4–9

With the Recommended wordings substituted, `PB.near_copy_hits` over all 20 of the outline's FAQ questions (corpus `PB.near_copy_corpus()`, own route and own board excluded) still returns **six** hits. All six are outline-approved wordings that STOP 2 q03 did not name:

| Question (outline) | Near-copy of | Where | Apart by |
|---|---|---|---|
| How Much Does Each Blue Staffy Puppy Cost? | How much does a blue Staffy puppy cost? | `board:index` (+4 more) | each |
| Can My Blue Staffy Puppy Be Delivered to My Home? | Can I Get a Blue Staffy Puppy Delivered to My Home? | `/blue-staffy-uk-breeders/` (+1) | be, get |
| Should I See the Mother With Her Puppy Before Money Changes Hands? | Should I See My Puppy With Its Mother Before Any Money Changes Hands? | `/uk-locations/blue-staffy-puppies-london/` (+1) | any |
| Is Blue Staffy Aggressive? | Are Blue Staffies Aggressive? | `/buy-blue-staffy-puppies-uk/` (+1) | staffies, staffy |
| Are Blue Staffies Good Pets? | Are blue Staffies good family pets with children? | `board:index` | children, family |
| Is a Staffordshire Bull Terrier Able to Live in a Flat? | Can a Staffordshire Bull Terrier live in a flat? | `board:uk-staffordshire-bull-terrier-guide` (+1) | able, can |

Task 35's test pins `near_copy_hits` over the board's FAQ questions to `[]`, so as written it would have failed on
these six. The controller's ruling is to re-word them as well (q03 (b), "Reword them properly", and lesson 18), so
they go on the STOP 3 batch with §§1–3: §§4–9 above.

## If every Recommended wording is adopted

The nine Recommended wordings put in place of the nine thin ones: deposit (§1 a), across the UK (§2 a), DNA (§3 b),
price (§4 a), home delivery (§5 a), mother (§6 a), temperament (§7 a), family home (§8 a), flat (§9 a). The other
eleven of the outline's 20 FAQ questions are unchanged.

| Block | The 20 questions as they would ship |
|---|---|
| top | How Much Will the Blue Staffy Puppy I Choose Cost? · Where Do I Find Blue Staffy Puppies to Buy Near Manchester? · Is Home Delivery an Option for My Blue Staffy Puppy? · Which Parts of the UK Do You Deliver Puppies To? · How Do I Know Which Puppies Are Still Available? · How Much Deposit Reserves One of Your Puppies? |
| middle | Are the Parents of Every Blue Staffy Puppy You Breed Health-Tested? · Is It Wise to See the Mother and Puppy Together Before Money Changes Hands? · Can I Contact You for Advice for the Dog's Whole Life? · How Do I Spot a Bad Staffy Breeder? · Has the Puppy Been Microchipped and Vet Checked? · What Vaccinations, Worming and Flea Treatments Has the Puppy Had? · Was Each Parent DNA Tested for L-2-HGA as Well as HC-HSF4? |
| bottom | Is a Blue Staffy an Aggressive Dog by Nature? · Do Blue Staffies Suit First-Time Dog Owners? · Can a Staffy Be Left Alone for Hours? · Are Blue Staffies Good Pets for an Ordinary Household? · What Food Is the Puppy Eating Now? · Do Blue Staffies Make Good Family Pets for Homes With Children? · Will a Staffordshire Bull Terrier Be Happy Living in a Flat? |

| Check, over all 20 | Result |
|---|---|
| `PB.near_copy_hits(<the 20>, PB.near_copy_corpus(), exclude_page=(own route, own board))`: 64 sources, 1,319 headings and questions examined | **`[]`** |
| `PB.board_near_copy_hits(<stand-in board holding the 20>, PB.live_headings())`, the call Task 35's pin makes | `[]` |
| `PB.header_precheck(<the 20>, PB.live_headings(), exclude_page=<own route>)` | `[]` |
| `PB.faq_hits(<stand-in board holding the 20>, live)` | `[]` |
| Within-page: each of the 20 against the H1 and every other outline heading (nine wordings substituted), by `header_precheck` and `near_copy_hits` | `[]` |
| `result_lines` (`tests/py/test_no_health_result_stated.py`) on each of the 20 | none |

The first run returned `[]`, so no further pass was needed. A second check covers any mix of picks, not only the
Recommended set. Every option in §§1–9, (keep) rows aside, was run pair by pair against every option of the other
eight questions (`header_precheck` and `near_copy_hits`), and no pair clashed. So whichever option the breeder picks
for each question, the 20 stay clear of the collision and near-copy gates. §3 (a) still fails check 6 on its own,
as §3 says. One pairing is a reading point, not a gate hit: §2 (b) with §5 (a)
puts two questions that both open "Is Home Delivery …" in the top block (see §5).
