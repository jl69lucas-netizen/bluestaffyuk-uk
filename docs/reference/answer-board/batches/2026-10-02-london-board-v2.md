# London page board v2 · decisions before you approve

The London page board (https://claude.ai/artifact/CbemmwUeW5qGEmEFog7ezz) now carries six new blocks:

- 1b: How Google reads this page.
- 4c: Term density against competitors.
- 4d: FAQ placement.
- 5c: What competitors say that we do not.
- 7c: Infographics, with three styles per section for you to pick.
- 7d: OG images.

These questions set the rules those blocks use. Answer them here, make the infographic picks on the board, then press the board's approve button. This batch replaces the 2026-09-30 approval question.

## Keywords and entities

1. **Which density target should the page aim for (block 4c)?** Block 4c counts every keyword and entity on the competitors' pages and gives two ranges per term, scaled to our 2,955-word page. Recommended: (a). Why: the median band matches what already ranks without stuffing, which Google's spam policies penalise, and London's leader band rests on a single 600-word page. Trade-off: we may sit below the single densest competitor on a few terms.
   - (a) Median band (p25–p75 of competitors)
   - (b) Leader band (p75 to the densest competitor)

2. **Should listing pages count in the density bands?** Only 2 of London's 9 top results are prose pages: freeads and englishbluestaffypuppies.com. The other 7 are staffie-owners and pets4homes listing grids, so the board flags block 4c as a "thin pool". Recommended: (a). Why: listing card text is classified-ad copy, not prose a breeder page should copy. Block 5c already counts listings for word ideas. Trade-off: the bands rest on 2 pages until more prose competitors rank.
   - (a) Keep listings out of the bands, flagged as a thin pool
   - (b) Count listings too

3. **Which competitor words should the page use (block 5c)?** These appear on three or more competitor domains and are not on our board yet: vet checked · KC registered · mum and dad (parents) seen · ready to leave · microchipped, wormed, vaccinated · family home / raised in our home. Each one goes into a section only when it is true for us and backed by a data file; anything without a source stays out. Recommended: (a). Why: Google sees these on every page that ranks, and each one is a buyer check. Trade-off: some may need a data source added before they can be written.
   **Where it goes:** the section keywords in data/boards/blue-staffy-puppies-london.json, and data/faq.json where a fact is new
   - (a) All of them, wherever a data file backs the claim
   - (b) Only some (name them in the text box)
   - (c) None

## How Google reads the page

4. **"How rare are blue Staffies?" is a People Also Ask question with no section. What should we do?** Block 1b matched 5 of London's 6 PAA questions to a section; this is the one gap. Recommended: (a). Why: the bottom FAQ block already answers breed questions, and we hold the coat facts. Trade-off: a short FAQ answer ranks for it less strongly than a full H3 would.
   - (a) Answer it in the bottom FAQ block
   - (b) Add an H3 under the breed section
   - (c) Leave it

## FAQ placement

5. **How should every page decide between FAQs at the top, middle and bottom, and one bottom FAQ?** Recommended: (a). Why: (a) uses the page's own question data. London's 73 fact-backed questions split buying 28, dog 25 and living 10 across 2,955 words, so it gets three blocks. A short care blog with only dog and living questions gets one bottom block. Trade-off: two pages of the same type can come out differently.
   **Where it goes:** rules/copy.md and the bsuk-query-augmentation skill, with a test (scripts/faq_layout.py)
   - (a) Intent spread: three blocks when the questions reach all three groups (buying, the dog, living with it), each with 2+ questions, on a page of 2,000+ words; otherwise one bottom block
   - (b) Page type: location and buy pages always get three blocks; every other page gets one bottom block

## Images

6. **What does "OG images, 4–5 per page" mean?** Recommended: (a). Why: London's 28 photo slots are all reused photos and none show London, and Google Images favours original images. Google and the social sites read only the first og:image tag, so (b) would do nothing. Trade-off: each generated image costs about $0.03 on the cheapest Gemini model and is approved by you at STOP 4.
   **Where it goes:** IMAGE-DESIGNS.md §1 and block 7d
   - (a) 4–5 generated photos per page: the share card first, then the top buying sections, each beside the served photo
   - (b) 4–5 og:image meta tags

7. **Should the "Pit Bull or American Staffy?" comparison infographic stay?** Block 7c found six sections that need an infographic. This one has no data: no file holds breed-standard figures, so it would render as NOT FETCHED. Recommended: (a). Why: a comparison with no sourced figures breaks our no-invented-claims rule. Trade-off: the breed section keeps just its photo.
   - (a) Drop it
   - (b) Keep it, and I'll supply a sourced breed-standard data file first

8. **Should an infographic sit beside the section's photo or replace it?** Recommended: (a). Why: working rule 11 keeps every served photo and its alt, because they already rank in Google Images. Trade-off: those sections carry two visuals.
   - (a) Beside the photo
   - (b) Instead of the photo

9. **Can the first generated test image close Known Issue 70?** The first real image came from the cheapest model, gemini-3.1-flash-lite-image, and passes the banned-look list: natural rose ears, plain collar, Staffy build. The plan's extra "bake a test draft" step is refused for the `_demo` test board, and drafting onto London's real hero slot was blocked. The image is at docs/reports/ki70-smoke-2026-10-02.png. Recommended: (a). Why: synthetic tests already cover the bake step. Trade-off: the first real bake happens at STOP 4 on a real slot.
   - (a) Close KI 70 on the generation proof
   - (b) Fix the pipeline so the `_demo` board accepts drafts first

## Components and tools

10. **For every remaining page, should each section get a new or refreshed component, sized to that page's own sections and tools?** You said "yes, this is what I want" for London. Recommended: (a). Why: working rule 16 already asks for a refresh on every section, and this makes the per-outline component pass standard. Trade-off: each page takes a component step before its board.
    **Where it goes:** docs/reference/page-run.md row 10 and a standing rule
    - (a) Yes, on every remaining page
    - (b) London only for now

11. **Which Claude Code mod should we build first?** Mods are small plugins that load live inside Claude Code: a status-line entry, a strip above the prompt, a side pane, a pop-up, a slash command, or a hook that blocks an action. Recommended: (a). Why: it is always visible, read-only and the lowest risk. Trade-off: it shows status and doesn't do anything.
    - (a) Status line: branch · page · STOP number · last check:all result · Gemini calls today
    - (b) A pop-up plus a strip when an answer-board batch is received
    - (c) A hook that refuses `git commit` while the last check:all failed
    - (d) A STOP-tracker side pane

12. **What else should every page board carry?** There are four options: (1) a preview of the Google result (title and description at desktop and mobile widths); (2) a schema preview (the JSON-LD the page will emit); (3) an internal-link map (links in and out, with their anchors); (4) a page-weight and LCP budget per section. Recommended: (a). Why: (1) and (2) are cheap, because the data and the schema builder already exist. Trade-off: (3) and (4) need the built page, so they come after the build.
    - (a) Add (1) and (2) now
    - (b) Add all four
    - (c) None for now
