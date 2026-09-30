# Deposit wording · four decisions before data and frozen pages change

Your 2026-09-27 ruling: the £500 deposit is "refundable up to 70% if a visitor fails to show up"
(never plainly "refundable"), and viewing is deposit-first ("the deposit books your viewing and
reserves your puppy"). The instruction and rule files now follow it (branch `deposit-wording`,
commit cb15628). What remains is data, shared code and the 12 frozen pages, which you asked to
approve first. The full inventory is `docs/research/deposit-wording-alignment.md`. Claude's
recommendation is marked.

## Data and shared code

1. **Apply the data and shared-code changes (b1–b13)?** Keep `deposit_refundable: true` (a
   `false` would print the retired "non-refundable"), and add the 70% figure and its condition to
   `data/settings.json`. The FAQ token, three FAQ rows, the kit counter label, the six puppy pages'
   spec line, the locations hub line and the ontology entity name then derive from those fields.
   A new gate flags plain "refundable" on new pages. Recommended: (a) — until this lands, every
   new city page renders the old wording through the shared FAQ rows, whatever its prose says.
   Trade-off: the shared FAQ answers and their FAQPage JSON-LD also change on six frozen pages
   (index, contact, breeders, pup-sale, buy, buying guide).
   **Where it goes:** `data/settings.json`, `data/faq.json`, `src/lib/faq.ts`, kit registry,
   puppy template, `/uk-locations/`, dup whitelist, their tests.
   - (a) Apply all of b1–b13, frozen pages' shared FAQ answers included
   - (b) Apply b1–b13 but pin the frozen pages to the old FAQ answer until question 2 is ruled
   - (c) Leave data and shared code as they are for now

## Frozen pages

2. **Amend the 12 frozen pages' deposit and viewing copy?** 9 of the 12 print a plain
   "refundable" deposit (37 rendered occurrences). The homepage and the pup-sale page also carry
   viewing-first headings that contradict deposit-first viewing: "Meeting the Litter Comes Before
   Paying" and "Meet Maggie Before You Pay Anything". No verbatim set pins either wording.
   Recommended: (a) — the headings state the opposite of your policy on the two highest-intent
   pages. Trade-off: each amended page needs its board re-approved and `gate:page` re-run.
   **Where it goes:** the 12 pages' `.astro` files and `data/boards/<slug>.json`.
   - (a) Amend all 12 through their boards now (copy only, the wording shown on each board)
   - (b) Amend only the viewing-first headings on index and pup-sale now; the rest waits
   - (c) Leave all 12 frozen until project 5 reaches them

## Wording

3. **Which 70% condition goes on the site?** Your follow-up ruling says "if a visitor fails to
   show up". Lisa's original answer said refunds of up to 70% are issued "if the buyer chooses to
   change their mind 1 day before delivery or pickup". The instruction files now use the ruling's
   wording. Recommended: (a) — it is the later, explicit ruling. Trade-off: a buyer who cancels
   the day before does not see the terms Lisa described.
   - (a) "if a visitor fails to show up" (the ruling)
   - (b) "if you change your mind up to 1 day before collection or delivery" (Lisa's answer)
   - (c) State both conditions
4. **Where a counter tile or meta description has no room for the condition, may it say "£500
   deposit books your viewing" with no refund wording at all?** That is what the instruction files
   now teach for tiles and ≤160-character metas. Recommended: (a) — it keeps the tile true
   without a shortened refund claim. Trade-off: the tile no longer signals that any refund exists.
   - (a) Yes — no refund wording where the condition does not fit
   - (b) No — use "refundable up to 70%" even without the condition
