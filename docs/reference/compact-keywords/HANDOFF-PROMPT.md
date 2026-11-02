Continue the BlueStaffyUK short-pages work started in a cloud session on 2026-11-02. That session could not see the `foundation` branch, the two finished blog posts or the new BlackStaffy images, because they exist only on this machine. Everything it produced was measured against the GitHub snapshot `manchester-page` (3e8f87f, 2026-10-09), so re-check every finding against `foundation` before acting on it. Do not invent data; any field with no data key is a question for me.

INPUTS FROM THE CLOUD SESSION
Get them one of two ways: unzip `bsuk-compact-bundle.zip` into the project root, or take the files from the GitHub branch `compact-keywords-handoff` (jl69lucas-netizen/bluestaffyuk-uk, commit 56e544a, docs only). The files:
- `.claude/skills/bsuk-compact-page/SKILL.md`: DRAFT compact-keyword skill, not yet pressure-tested
- `docs/reference/compact-keywords/2026-11-02-defects-snapshot.md`: 15 measured defects on the pup pages and the hub
- `docs/reference/compact-keywords/2026-11-02-keyless-keyword-research.md`: keyless keyword evidence, graded A/B/C, no volumes
- `docs/reference/compact-keywords/2026-11-02-header-gallery-research.md`: research on 8 sites
- Art board (Claude Design canvas, BlueStaffyUK design system installed): https://claude.ai/artifact/J893onxJZi8idwKsxzu31S. Four rows, three options each, every option at desktop 1280 / tablet 820 / mobile 390.

ALREADY DECIDED BY ME
0. Art board picks: HA Eyebrow and Question (H2/H3 body headings), G1 Stage and Side Pair (pup photos), T1 Kennel Card (pup page template), X1 Swipe Rail of Cards (other-pups strip). Build the first pup page's components from these. The unpicked options (HB/HC, G2/G3, T2/T3, X2/X3) are the pool for the following pup pages, because no two pages share a component (rule `own-components-per-page`).
1. Compact keyword strategy = A + B, with C as sections. A: each pup page owns its own attribute phrase (colour + sex + KC registered). B: `/available-puppies/` owns "blue staffy puppies for sale UK / available now". C: buyer-situation phrases (Carlisle/Cumbria collection, UK delivery, health-tested parents with the tests named and never a result, price) become H2 sections on those pages, never separate pages.
2. The 85–112 entity rule stays as it is for longer pages. Compact pages (~850 words, under 1,000 in <main>) do not apply it.

STILL OPEN: ask me one at a time via the answer board: D1 (H5/H6 floor on compact pages), D3 (H2 count on compact pages), D4 (sold/reserved pup page behaviour). The proposals are in SKILL.md §9.

DO, IN ORDER. Follow every BSUK rule, skill, agent and gate. Answer board and grill board before code; verification before any "done".
1. Set up a worktree off `foundation` (another agent is working on the main checkout). Merge back into `foundation` only. Load all BSUK mods.
2. Re-run the measurements on `foundation`: `npx astro build`, the <main> word count, `scripts/final_page_audit.py` and `scripts/page_hardening_scan.py` on `available-puppies` and each pup. Update the defects file with what is still true.
3. Finish the skill with `superpowers:writing-skills`: diff it against `foundation`'s rules and skills, run RED→GREEN pressure tests with subagents, fold in my rulings, then commit. Write the `compact-word-ceiling` test (red first) per `bsuk-learning-loop`. Then list the other pages and sections the skill should apply to.
4. Images (BlackStaffy folder), through `bsuk-photo-ingest` and `image-metadata`:
   - Cheryl: same name, 3 new images. Replace her images on every page and delete the current Cheryl images. Update her colour and markings in `data/puppies.json` (and so on every pup card) to match the new photos. Show me the proposed wording before writing it.
   - Ince: 3 new images. Delete the old ones.
   - Vennie: add her 3 new images.
   - Deleting a served image conflicts with working rule 11. I asked for the deletions, so do them, but first show me every page, sitemap and og:image that references each old file.
5. Design: continue on the Art board above (Claude Design, not HTML pages), at desktop, tablet and mobile:
   - "Header ideas" means H2 and H3 section headings in the page body, not the navbar. Research other sites' H2/H3 heading treatments and add an option if one beats HA–HC.
   - Images must be crisp: edge to edge on mobile, no small photos on desktop.
   - Every board, answer, page, grill, component, image and infographic is 380–400px tall on desktop. Heroes are 400–450px.
   - Design 3 templates for `/available-puppies/`. I pick one and you build all its unique components from it.
   - For the following pup pages, offer the unpicked templates plus the for-sale page's unpicked A (Ledger column) and C (Answer card). Each following pup page takes the next style.
   - Make the components beautiful, fluid, clean and well designed.
6. Copy: every paragraph answers its heading in its first sentence, and the conversational opening reinforces the heading's core message. Use the pups' new and existing images on each pup page. Cross-show the other pups with X1.
7. Check for bugs and board defects. Any workflow or board check that fails is fixed, not waived.

DEFECTS TO CONFIRM ON FOUNDATION (from the snapshot)
- Pup pages are 36–42 words; the hub is 64.
- "Deposit £500, refundable": should use `deposit_refund_clause`. CLAUDE.md's locked facts still say "£500, refundable"; fix that too.
- The H1 template hard-codes "Blue Staffy Puppy", so Byrd, who is white, gets the wrong H1.
- Roman's H1 is not Title Case.
- The hub has no ItemList of Product nodes.
- The Enquire button is ink-coloured, not the brass pill.
- The mobile photo is not edge to edge.
- The desktop photo is capped at 560px with a single 120px thumbnail.

KNOWN BLOCKER: autocomplete research was blocked in the cloud. Re-run the alphabet-soup expansion locally (Chrome extension / `research-recency`) for UK results.

SKILLS TO USE: `bsuk-compact-page` (new) for keyword choice, word budget and answer-first copy on these pages. `bsuk-puppy-page-builder` and `bsuk-puppy-page-excellence` for the pup pages and the hub. There is no "purchase guide" skill, but the `bsuk-purchase-guide` agent rebuilds `/buy-blue-staffy-puppies-uk/`, not the pup pages. The buying guide page uses `bsuk-seo-master-checklist`.
