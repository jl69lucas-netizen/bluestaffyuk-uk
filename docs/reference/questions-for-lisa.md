# Questions for Lisa Bright

Buyers ask these questions on Google, on Bing, in ChatGPT answers and on Reddit, and the new
website cannot answer them yet, because nothing we hold says what the true answer is. We will
not guess on your behalf: a page only states what you have told us, or what a document shows.
So each question below waits for your answer.

Answer in your own words, as briefly as you like. "Yes", "No" or "Not yet" is a fine answer.
Where a question asks for a document or a number, a photo of the paper or the number itself
is enough. If a question does not apply to how you work, say so and we will leave it off the
site. Nothing here is published until you have answered it.

Under each question, **Where it goes** says where the website keeps your answer. You do not
need to do anything with that line; it is there so that you can see exactly what each answer
changes. (From Known Issues 41, 7 and 54 in `docs/reference/session-log.md`.)

## Puppies, prices and deposits

1. **Are there blue Staffy puppies available now for buyers in Manchester?** Today the site
   lists six puppies as available. Are they, and would you sell one to a family in Manchester?
   **Where it goes:** each puppy's `status` in `data/puppies.json`, and a new row
   `buyer-availability` in `data/faq.json`.
2. **How much does one of your puppies cost?** The site says £1,500 to £1,700, priced by
   puppy. Is that still right? **Where it goes:** `price_range` in `data/settings.json`, and
   each puppy's price in `data/puppies.json`.
3. **Should a buyer pay a deposit before they have seen the puppy, and what is your deposit
   policy?** The site says the deposit is £500 and refundable. When is it paid, and when, and
   how, is it given back? **Where it goes:** `deposit_gbp` and `deposit_refundable` in
   `data/settings.json`, and a new row `buyer-deposit-policy` in `data/faq.json`.
4. **Is there a waiting list?** If there is, how does a family join it, and is anything paid
   to join? **Where it goes:** a new row `buyer-waiting-list` in `data/faq.json`.

## Seeing the puppy, and the paperwork

5. **Can a buyer see the puppy with its mother, where the litter was raised?** **Where it
   goes:** a new row `buyer-see-with-mother` in `data/faq.json`.
6. **Do you give a written contract, and will you take a puppy back if the owner cannot keep
   it?** **Where it goes:** a new row `buyer-contract-and-return` in `data/faq.json`.
7. **Does the contract give the buyer time to have their own vet check the puppy?** If it
   does, how many days? **Where it goes:** a new row `buyer-own-vet-check` in `data/faq.json`.

## The parents' health

8. **Have both parents been tested for L-2-HGA and for hereditary cataracts (HC-HSF4)?** What
   were the results? A photo of each certificate is the best answer. Five answers on the site
   already say the parents are "certified clear" or "DNA tested clear", and until we have seen
   the certificates we cannot show that this is true. **Where it goes:** the
   `parents-dna-clear` row in `data/quality/evidence-ledger.json` (today it records the
   results as not yet seen), the `health-dna-tests` row in `data/faq.json`, the
   `about-health-tests` row in `data/faq.json`, the `home-parents-health-tested` row in
   `data/faq.json`, the `about-health-tested` row in `data/faq.json` and the
   `health-genetic-tested` row in `data/faq.json`.
9. **Have the parents had eye examinations and elbow screening, as well as the DNA tests?**
   **Where it goes:** a new row `health-eye-elbow-screening` in `data/faq.json`.
10. **What are the parents' Kennel Club registered names, and what happens if a puppy's
    registration papers are delayed?** **Where it goes:** a new row `parents-kc-names` in
    `data/faq.json`.
11. **What is the parents' coefficient of inbreeding?** **Where it goes:** a new row
    `parents-coi` in `data/faq.json`.

## Each puppy's own health and start in life

12. **How can a buyer confirm that the puppy has been examined by a vet? May they contact your
    vet?** **Where it goes:** a new row `puppy-vet-check-proof` in `data/faq.json`.
13. **Has the puppy had its first vaccination before it is collected?** **Where it goes:** the
    `health-vaccinations` row in `data/faq.json`.
14. **Do you give a written health guarantee? If so, for how long, and what does it cover?**
    The site already says that every puppy leaves with a written health guarantee, but it
    cannot say how long the cover lasts or what it covers until you tell us. **Where it
    goes:** the `home-health-guarantee` row in `data/faq.json`, and `guarantee_days` in
    `data/settings.json` (today it is empty, so no page states a number).
15. **What socialisation has the puppy had by the time it goes home?** For example: people,
    children, other dogs, household noises, car journeys. **Where it goes:** a new row
    `puppy-socialisation` in `data/faq.json`.
16. **Do you follow Puppy Culture or early neurological stimulation (ENS) with your litters?**
    One of the old website's city pages said you do, but nothing we hold confirms it, so the
    new pages leave it out until you tell us. **Where it goes:** a new row
    `puppy-early-stimulation` in `data/faq.json`.

## Colour

17. **Can a blue puppy come from parents that are not both blue? What colours are your
    puppies' parents?** **Where it goes:** a new row `colour-blue-parents` in `data/faq.json`.

## Your standing as a breeder

18. **Are you a member of the Kennel Club Assured Breeder Scheme?** Please answer yes or no.
    If yes, send your membership number, or a link to your entry on the Kennel Club's own
    site, so the page can show the record behind the claim. The old website said this five
    times with nothing behind it, so the new pages leave it out until you confirm it.
    **Where it goes:** two new keys in `data/settings.json`: `kc_assured_breeder` (yes or no)
    and `kc_assured_breeder_record` (the number or the link).
19. **What is your dog breeding licence number, and which council issued it?** A photo of the
    licence is enough. The old website called you "council-licensed" but showed no number, so
    the new pages do not say it yet. **Where it goes:** two new keys in `data/settings.json`:
    `breeding_licence_number` and `breeding_licence_council`.
20. **Exactly how should the website describe your licence?** For example: "Licensed by
    [the council's name] to breed dogs, licence number [the number]". Write the sentence the
    way you are happy to see it on every page. **Where it goes:** a new key
    `breeding_licence_wording` in `data/settings.json`.
21. **How should the website say that you follow Lucy's Law?** In England, Lucy's Law means a
    puppy under six months old can only be sold by the person who bred it, and a buyer should
    see it with its mother where it was born. Write the sentence you are happy to have on the
    site, or tell us to leave it off.
    **Where it goes:** a new key `lucys_law_wording` in `data/settings.json`.

## What happens next

When your answers come back, each one is written into the file named under it, exactly as you
gave it. The pages that use it are then rebuilt, and the question files behind the Manchester
and Leeds pages are rebuilt from what is already saved, at no cost. Anything you would rather
not have on the website stays off it. If an answer needs a document we do not have yet, the
page keeps saying nothing about it until the document arrives.
