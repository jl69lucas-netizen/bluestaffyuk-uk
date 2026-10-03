# Google helpful-content review · six decisions

Google updated its helpful-content guide on 2026-10-01. The update added a "Main content" section (it counts calculators and tools as main content, and raters judge Effort, Originality, Skill and Accuracy) and a warning against faked authors. The full review is here: https://claude.ai/artifact/66z5sKaSFR1p7GcDTPJGbW. Questions 1–3 touch London now; 4–6 change the system for later pages.

## London

1. **Add a byline ("Written by Lisa Bright, Carlisle", linking to the About page) with Person markup, and record that you read each page before it goes live?** Google asks whether pages carry a byline where readers expect one, and no BSUK page has one today. London's board already plans Person markup. Recommended: (a). Why: the copy is drafted with AI in your voice, so your recorded read is what keeps the byline honest under Google's new faked-author warning. Trade-off: you read every finished page before approval (you already approve it at the end).
   **Where it goes:** a new kit byline component, src/layouts/PageShell.astro, data/page-runs/<slug>.json
   - (a) Yes, byline plus Person, and a recorded read by me
   - (b) Byline only
   - (c) Not now

2. **Add a video-call checklist to London's deposit section (tick-boxes the buyer uses during the call: mum on camera, the puppy's own markings, paperwork shown, the refund clause read out)?** Google now counts interactive tools as main content. This one uses only facts we hold and works without JavaScript. A postcode delivery calculator would have to invent figures, so it stays out. Recommended: (a). Why: it serves the page's one purpose (see the puppy on video before any deposit) and no London competitor has it. Trade-off: it reopens the approved board for this one component (a preview first, as always).
   - (a) Yes, preview it for my approval
   - (b) No

3. **Show a compact strip of the six puppies (name, sex, colour, price) near the top of London, not only at the litter section about 1,100 words down?** Page one for London is all listing pages, so buyers arrive expecting puppies first. Recommended: (a). Why: it gets the buyer to their goal faster and reuses the roster data (no new claims). Trade-off: a board change, and the page gets slightly longer above the fold.
   - (a) Yes, preview it for my approval
   - (b) No, keep the approved order

## System, for the next pages

4. **Turn each section's word band into a maximum only (no minimum), and relabel the term-density table as a ceiling, not a target?** Google says outright that it has no preferred word count, and that writing to one is a warning sign. Recommended: (a). Why: we already dropped the keyword-frequency floor on 2026-09-09 because a floor "manufactured the repetition", and on London 45 of the 61 density rows have no competitor figure to aim at. Trade-off: section lengths become less predictable. London's approved bands stay as they are.
   - (a) Yes, from the next page
   - (b) No, keep the bands

5. **Make the "five H5 and five H6 headings" floor a warning on location pages, not a fail?** It already warns on blog posts, because meeting it there produced headings "written for a checker". This reverses your 2026-09-30 ruling, which is why I'm asking. Recommended: (a). Why: single-child H5 → H6 chains don't help a reader scan, and Google values headings that summarise. Trade-off: some pages will have fewer deep headings. London's approved outline doesn't change.
   - (a) Yes, warn only
   - (b) No, keep it a fail

6. **Before a city gets a full page, must you supply at least one first-hand fact about that city (a past delivery there, a buyer there, a note on the route)?** Google warns about many automated pages that add no value, and every city page shares the same breeder facts. Recommended: (a). Why: a city fact is the one thing no marketplace can copy. Without one, the city stays a short honest page or joins a regional page. Trade-off: fewer full city pages in project 5, and one fact per city from you.
   - (a) Yes
   - (b) No, build all 28 on the current controls
