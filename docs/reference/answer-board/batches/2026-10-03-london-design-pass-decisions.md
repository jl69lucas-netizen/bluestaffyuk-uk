# London design pass · five ideas and a site-wide link fix

The frontend-design pass fixed five things on London, including 40 links in the reading text that were invisible. These six would change how pages look, so each waits for your yes. Before and after for each: https://claude.ai/artifact/GUp8iGCRmRxjnqfR3famPu

## Every page

1. **Underline the links on every page, as London's now are?** The homepage has 48 links that look like plain text, and the health page has 29. Recommended: (a). Why: a link you can only find by colour fails WCAG for colour-blind readers, and visitors miss links they can't see. Trade-off: every page repaints, so every page's render gate runs again.
   - (a) Yes, on every page
   - (b) London only

2. **D9 · Line up the footer's bottom row and give the form's privacy link a hover?** Recommended: (a). Why: it's a small alignment fix, and the hover matches every other link. Trade-off: the footer repaints on every page.
   - (a) Yes
   - (b) No

## London

3. **D5 · A thin hairline between chapters, with the seal kept only where the page turns (FAQ, letters, contact)?** Recommended: (a). Why: sixteen identical 154px seals make the middle of the page feel samey, and the seal stops meaning "a new part". Trade-off: the page is a little shorter, and it loses some of the seal's character between chapters.
   - (a) Yes
   - (b) No, keep the seal everywhere

4. **D6 · Let the six hero photos settle in once on load (200ms each, off for anyone who asks for less motion)?** Recommended: (a). Why: it's the page's single motion moment, and it draws the eye to the puppies first. Trade-off: it adds a fraction of a second before the strip is fully still.
   - (a) Yes
   - (b) No

5. **D7 · Match the chapter panel's side margin to the other panels?** It needs one smaller copy of the registration-check photo first, added beside the original. Recommended: (a). Why: on desktop the panel looks slipped inside a thin frame. Trade-off: one new image file.
   - (a) Yes, add the smaller photo copy and apply it
   - (b) No

6. **D8 · Show the two lettered images whole (on the bone background), so their words aren't cut off?** Recommended: (a). Why: right now "BULL TERRIER", "BULLY" and the "Contact Us" headline are cropped mid-word. Trade-off: those two boxes show some bone background around the picture.
   - (a) Yes
   - (b) No
