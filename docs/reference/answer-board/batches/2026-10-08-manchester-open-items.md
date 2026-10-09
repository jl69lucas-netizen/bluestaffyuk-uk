# Manchester page · five open items before the final polish

Screenshots of each item are on the preview page: https://claude.ai/artifact/3rVRn48yHYp2uYDG44XDYa. The page is built and passes its gates, and stays noindex until you approve it. Claude's recommendation is marked on each question.

## Wording

1. **May we reword the health-testing answer in the middle FAQ?** Our evidence check flags two problems in "Are the Parents of Every Blue Staffy Puppy You Breed Health-Tested?": the answer repeats Kennel Club registration (the page already says it), and it names the DNA tests without saying the certificates are shared on request. Now: "Yes. Maggie, our dam, and Jones, our sire, are both Kennel Club registered and fully vaccinated, and both have had DNA tests for L-2-HGA and HC-HSF4 and eye and elbow screening." Recommended: (a). Why: it clears both errors in scripts/evidence_audit.py, and every fact in it is one you have already given us. Trade-off: this answer no longer says the parents are Kennel Club registered; the parents section still says it.
   **Where it goes:** src/lib/manchesterFaq.ts, the middle FAQ (preview question 1).
   - (a) "Yes. Maggie, our dam, and Jones, our sire, are both fully vaccinated, and both have had DNA tests for L-2-HGA and HC-HSF4 and eye and elbow screening, with the certificates shared on request."
   - (b) Keep it as it is
   - (c) Other wording (type it)
2. **May we remove the doubled "change your mind"?** In the deposit section, under "What Happens to My Money If I Pull Out Before Collection?", the answer reads: "If you change your mind, your £500 is up to 70% refundable if you change your mind up to 1 day before collection or delivery." Your refund wording already contains the phrase, so the opening adds it a second time. Recommended: (a). Why: it keeps your refund wording whole and drops only the repeat. Trade-off: none.
   **Where it goes:** the Manchester page, deposit section (preview question 5).
   - (a) "Your £500 is up to 70% refundable if you change your mind up to 1 day before collection or delivery."
   - (b) Keep it as it is

## How it looks (screenshots on the preview page)

3. **Keep the thin navy-to-gold bar above the prices strip?** The design rule needs a visible line between the hero and the strip of figures under it. The bar uses the same blend as the delivery range bar inside the strip. Recommended: (a). Why: without it, the strip has only a change of background to set it apart from the hero, which the render gate counts as a defect. Trade-off: one more thin line near the top of the page.
   **Where it goes:** the strip under the hero (preview question 2, with and without, desktop and phone).
   - (a) Keep the bar
   - (b) Remove it (the gate then needs another way to separate the two)
4. **Phone section headings about 1px smaller on every city page, London included?** On a phone, Manchester's longest heading ran to four lines; this change brings it to three. The setting is shared, so London's phone headings get at most 1px smaller too. Desktop is unchanged. Recommended: (a). Why: headings stay inside the 20–22px phone range and no city heading gains a line. Trade-off: London changes after you had approved it.
   **Where it goes:** every city page on a phone (preview question 3, before and now, Manchester and London).
   - (a) Keep the smaller phone headings everywhere
   - (b) Undo it everywhere, and shorten the Manchester heading instead
   - (c) Manchester only, London back as it was
5. **Which photo goes beside the health and viewing FAQ?** The board you approved says Maggie. At build we used Byrd instead, because Maggie's photo already sits beside the review just before the last FAQ, so she would appear twice in a short scroll. Recommended: (a). Why: no photo repeats close together. Trade-off: it differs from the approved board, which is why we are asking.
   **Where it goes:** the middle FAQ block (preview question 4, Byrd and a Maggie mock-up side by side).
   - (a) Byrd, as built
   - (b) Maggie, as the board said (her caption names her)
6. **Is the AI-made preparation photo all right beside the last FAQ?** It shows a bed, a crate and two bowls set out for a new puppy, captioned "A bed, a crate and two bowls, ready before a puppy comes home". It is AI-made, not one of your photos. Recommended: (a). Why: none of the served photos shows a home made ready, and the image has no text on it. Trade-off: it is the one AI-made photo in a FAQ frame on the page.
   **Where it goes:** the last FAQ block (preview question 4, desktop and phone).
   - (a) Keep it
   - (b) Use one of your own photos instead (name it, or say "you pick")
