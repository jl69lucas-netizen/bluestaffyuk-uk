# Lisa Bright · five facts before the London page

Building London's components and checking the finished pages turned up five facts that only the
breeder can confirm. Until each one is answered, no page prints it. The site's rule is that a
claim with no proof on file is never stated. Each question says where the answer goes.

## Health

1. **Do you hold the DNA test certificates for Maggie and Jones (L-2-HGA and HC-HSF4)?** The
   health page says 10 times that the parents are "DNA tested clear" (and twice more on the breed
   guide), but the site keeps no proof of a result. Naming the tests is fine today. Stating a
   result ("clear") needs the certificate recorded: the lab's name and the date are enough; no
   upload is needed. Until then, those lines are marked as unproven.
   **Where it goes:** `data/quality/evidence-ledger.json` (the `parents-dna-clear` proof).
   - (a) Yes, I hold both certificates; I give the lab and dates in the text box
   - (b) I hold some of them; I say which in the text box
   - (c) No certificates; the pages should only name the tests
2. **What does the two-year health guarantee cover?** The pages now say "Two-year health
   guarantee" and name no cover, and that is how they stay until you tell us. If it covers
   named conditions (for example hereditary or congenital conditions), write them in the text
   box as you would want them on the page.
   **Where it goes:** `data/settings.json` (the guarantee's wording).
   - (a) Leave it as "two-year health guarantee", with no cover named
   - (b) It covers what I write in the text box

## Buying and scams

3. **Do you offer buyers a live video call with the puppy and its mother before they pay?**
   Buyers are told to expect one as a scam check. Our scam-advice section cannot list it as a
   safety sign unless we offer it ourselves.
   **Where it goes:** the scam-advice checklist on the buy and city pages.
   - (a) Yes, always
   - (b) Yes, on request
   - (c) No
4. **How is the £500 deposit paid?** Buyers are warned about deposits paid by untraceable
   methods. The pages say nothing about payment until you tell us how we take it.
   **Where it goes:** the "safe payment" section (it says "not confirmed" today).
   - (a) Bank transfer
   - (b) Card or a payment link
   - (c) Other; I say what in the text box
5. **Is the take-back promise written into the sale contract?** Your rule is that we take a
   puppy back only if it is our fault or the owner can no longer care for it. The pages state
   that rule but do not say it is in a contract.
   **Where it goes:** the trust and FAQ copy on the buy and city pages.
   - (a) Yes, it is in the written contract
   - (b) No, it is our promise but not in the contract
