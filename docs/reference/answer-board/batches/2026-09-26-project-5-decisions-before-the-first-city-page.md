# Project 5 · decisions before the first city page

Project 5 starts with the London page, and the London board cannot be approved until these are
settled (Known Issues 60, 61, 63, 67 and 70 in `docs/reference/session-log.md`). Pick an option
for each; add a note if you want something different. Claude's recommendation is marked.

## Heroes and page source

1. **How should the 28 city pages get their heroes?** Working rule 16 says no two pages share a
   hero, but city pages map to the interior-guide family, whose three heroes the guides already
   use. Recommended: (a) — it scales to 28 pages and keeps rule 16's intent, because each city's
   own photo and text make its hero unique; the rule-16 gate learns the new family.
   **Where it goes:** Known Issue 60; `src/lib/boardStyles.ts`; the location builder skill.
   - (a) A location hero family: one design, varied per city by rule (its own photo and text)
   - (b) Exempt the city pages from rule 16 by name, as the utility pages are
   - (c) A design pass first: a new hero pool for the city pages, rotated so neighbours differ
2. **Where should a rebuilt city page's source live?** Today every city page comes from one
   template, `src/pages/uk-locations/[slug].astro`, fed by `data/locations.json`. Recommended:
   (a) — one template for 28 pages, and the board freshness check (Known Issue 63) needs only
   that template added to what it watches. **Where it goes:** Known Issues 61 and 63.
   - (a) Keep the one template; it renders the rebuilt layout when the city's record says so
   - (b) One `.astro` file per city, like the 12 pages already rebuilt
   - (c) Content files per city, rendered by one template

## Spelling and images

3. **Which spelling should every page use for the two DNA tests?** Today the evidence ledger,
   the FAQ rows and the boards write L-2-HGA and HC-HSF4; the copy rules write L2-HGA and HC.
   Recommended: (a) — the Kennel Club's own test names, and the spelling most files already use.
   **Where it goes:** Known Issue 67; everything moves to the one you pick.
   - (a) L-2-HGA and HC-HSF4
   - (b) L2-HGA and HC
4. **Will you add your Gemini API key now?** New pages need an image on every heading; where no
   existing photo fits, one is generated after you approve it on the board. Without the key,
   project 5 uses existing photos only. **Where it goes:** `GEMINI_API_KEY` in `.env` (you add
   it yourself); Known Issue 70.
   - (a) Yes, I will add it before the London board
   - (b) Later: use existing photos only for now

## Anything else

5. **Anything else Claude should know before the London page?** Optional.
