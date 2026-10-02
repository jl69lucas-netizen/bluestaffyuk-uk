# London Page Board v3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the breeder's 2026-10-02 answers (batch `2026-10-02-london-page-board-v2-decisions-before-you-approve`, saved in `docs/reference/answer-board/answers/`) and the two new asks to the London page board. Then republish the board for one final approval.

**Architecture:** This work extends the v2 modules (`scripts/term_density.py`, `og_slots.py`, `infographic_plan.py`, `faq_layout.py`, `build_page_board.py`, `pageboard.py`, `board_approve.py`). It adds one module for neighbourhoods and one for the four preview blocks. The pattern is unchanged:
- each block is a pure module that returns markdown;
- blocks are gated on `PB.FR.applies(board)`;
- nothing is invented: a missing figure is written `NOT FETCHED — <barrier>`.

**Tech Stack:** Python 3.9 stdlib, pytest, the Artifact tool (same URL), and DataForSEO via MCP (one paid call, approved in chat).

---

## The breeder's rulings this plan applies

| Q | Ruling | Effect |
|---|---|---|
| 1 | Median band | Block 4c recommends the median band. |
| 2 | **Count listings too** (against the recommendation) | `term_density` pool includes listing pages, labelled. The thin-pool warning goes. |
| 3 | All competitor words, wherever a data file backs the claim | Block 5c phrases enter section keywords only with a data source; the rest are `NOT FETCHED`. |
| 4 | "How rare are blue Staffies?" in the bottom FAQ | A `data/faq.json` row answered from coat facts already held; no rarity figure. Added to the faq-bottom picks. |
| 5 | FAQ method A (intent spread) | Rule text goes into `rules/copy.md` plus the query-augmentation skill, with a rule-index row (`enforced: test`, `tests/py/test_faq_layout.py`). |
| 6 | **OG = original real images, not AI or infographics.** Scan the site's real images and pick 4–5 per page. Choose the sections that best suit an original photo *before* deciding which sections get infographics or AI images. | Image order per page: (1) 4–5 original photos on the best-suited H2/H3s; (2) infographics; (3) generated images only for what is left. `og_slots.py` becomes an original-photo selector. |
| 7 | Keep the breed-split infographic and regenerate it with sourced data | A new `data/breed-standards.json` built only from cited pages (Royal Kennel Club SBT standard; the AKC American Staffordshire standard if fetched). Every figure has its URL and a fetched date. The pending note is removed. |
| 8 | **Infographics get their own H2 or H3 heading, CAG style** (one image per heading, 9–12 per page; congo-vs-timneh and baby-african-grey pages); playful, cartoonish | Each infographic slot is a new outline heading whose single image is the infographic. These are outline changes, shown on the board as such. The style trio becomes three playful/cartoon treatments. |
| 9 | Close KI 70 | session-log KI 70 closed, citing `docs/reports/ki70-smoke-2026-10-02.png`. |
| 10 | **Board structure: no two pages share a component.** After competitor research, every new page builds new components from its own data and outline. | A standing rule in `docs/reference/page-run.md` row 10, plus `rules/design.md`, plus memory. The rule-16 gate is extended from hero/counter to every section component (test). |
| 11 | Status-line mod first | A mod showing branch · page · STOP n · last check:all · Gemini calls today. |
| 12 | Add all four board extras | New blocks: Google result preview, schema preview, internal-link map, page-weight/LCP budget. |
| new | The Approve button names what is missing | A refusal lists each missing pick by section number, section name and pick name, with a jump link. |
| new | A neighbourhoods block | London areas and their keywords, e.g. "south london", "staffy for sale in croydon", from keyword data, never guessed. |

The breeder also pressed Approve on board v2 (db `boards/blue-staffy-puppies-london`, 23:29, record 27467c78a6a4). Rulings 6, 7 and 8 change the image plan and the outline, so v2's approval is superseded for images. The h1/meta picks and the non-image picks are carried forward by `locked_picks`.

## Tasks

### Task 1: Approve-button refusal names what is missing (small, do first)
**Files:** `scripts/build_page_board.py` (approve JS, around lines 1217+), `tests/py/test_page_board.py`.
- [ ] **Test:** the rendered JS holds a `SIGNATURE_LABELS` map, `{id: {n, section, label}}`, covering every id in SIGNATURE_SECTIONS plus h1, meta-title and meta-description.
- [ ] The refusal message lists each missing one as `§08 Do I Have to Pay a Deposit… — infographic style (ig:deposit-steps)`, each linked to its anchor. The status line scrolls to the first missing item.
- [ ] Test the label map contents for London. Commit.

### Task 2: Neighbourhood keywords (paid call, approved in chat first)
**Files:** create `scripts/neighbourhoods.py` and `tests/py/test_neighbourhoods.py`; raw data at `data/queries/raw/blue-staffy-puppies-london/neighbourhood_keywords.response.json`.
- [ ] **Controller:** get the breeder's yes in chat for ONE DataForSEO `dataforseo_labs_google_keyword_ideas` call, UK, en, seeds `staffy puppies london`, `staffie puppies for sale london`, `blue staffy london`, limit 200. Save the raw response.
- [ ] `areas(board, root)` reads that response, plus the SERP/competitor/keyword-universe files already held (Barnet and Camden Town are there today). It extracts London areas from a fixed, test-pinned gazetteer: the 32 boroughs, the City, and "north/south/east/west/central london". The gazetteer lists names only, never volumes. A keyword not found in data is never listed.
- [ ] `block()` returns a table with these columns: Area · Keywords found · Monthly volume (from data, else `NOT FETCHED`) · Where seen (SERP, competitor URL, keyword data) · Suggested use (H3/FAQ/body/none). Below it, a "Target" line recommends 3–6 areas by volume.
- [ ] Wire it in as block "3d. Neighbourhoods" after 3c. Tests, then commit.

### Task 3: Count listings in density (ruling 2)
- [ ] `term_density.competitor_pages(..., include_listings=True)` labels each page `listing`/`prose`. The table header names both. The thin-pool line goes. The default for London comes from a board field `density_pool: "all"`. Update the tests. Commit.

### Task 4: Original-photo selection first (ruling 6)
**Files:** `scripts/og_slots.py` is reworked into `scripts/original_slots.py`; `og_slots.py` is kept as a thin alias, or deleted with its tests moved over.
- [ ] Scan `data/image-manifest.json` and `public/images/**` for real photos. Exclude generated, infographic, comparison-graphic and stock-composite files by manifest kind and filename markers, pinned by a test.
- [ ] Score each body H2/H3 for photo fit: a subject match between the heading or entities and the photo's alt/filename, and whether the photo is unused elsewhere on this page.
- [ ] Propose 4–5 slots, each the best (section, photo) pair. The share card is the best of them, recomposed at 1200×630.
- [ ] Served alts are kept on first use; a repeat gets a new alt (rule 11).
- [ ] Block "7d. Original photos" carries `pick-og:<slot>` radios with use/swap/skip. Tests, then commit.

### Task 5: Infographics as their own headings, cartoon style (rulings 7 and 8)
**Files:** `scripts/infographic_plan.py`, `data/boards/blue-staffy-puppies-london.json` (outline nodes), `data/breed-standards.json` (new).
- [ ] For each infographic, propose a new heading in the CAG pattern ("Every Paper That Comes Home With Your Puppy", "The Route From Carlisle to Your London Door"). Placement: an H3 under the owning H2, or its own H2 where the outline has a slot.
- [ ] The heading's only image is the infographic, and its slot moves from the H2 to the new node. Write the heading text fresh (rule 8). Run the outline checks (`outline_matrix.py`, `family_rules.py` heading-repeat, the H1–H6 counts).
- [ ] Re-run `infographic_plan` after Task 4: sections that won an original photo do not also get an infographic unless the breeder adds one.
- [ ] The three styles become playful/cartoon treatments on the site tokens:
  - **sticker**: rounded cards, thick outlines, a doodle-dog mascot icon;
  - **chalk**: hand-drawn-style lines on bone;
  - **comic**: panels with speech-bubble labels.
  Invoke `frontend-design:frontend-design` first and render at 375/768/1280.
- [ ] Facts come from data only. Ship the infographics as baked webp (the HTML screenshot through Playwright, then `bake_images.py`) so the figures are exact. No AI-drawn text.
- [ ] breed-split: build `data/breed-standards.json` from the Royal Kennel Club SBT standard page (already on the links plan) and the AKC AmStaff standard page. Use Firecrawl scrape, `maxAge: 0`. Store each figure with its URL and fetched date, and remove `IG_PENDING`.
- [ ] Tests, then commit. The outline changes are listed on the board in a "Changed since STOP 2" panel.

### Task 6: Board extras (ruling 12)
**Files:** create `scripts/board_previews_extra.py` and its tests.
- [ ] **Block 2b, Google result preview:** the picked title and description rendered at desktop and mobile SERP widths, with pixel-width truncation (Arial 20px / 14px measure table, pinned).
- [ ] **Block 8a, Schema preview:** the JSON-LD nodes the page will emit, from the board's schema plan (`brief.schema_plan`) and data. Pretty-printed, no invented fields.
- [ ] **Block 8b, Internal-link map:** links out from the board, and links in grepped from `dist/**/*.html`, with anchors.
- [ ] **Block 8c, Page-weight/LCP budget:** per section, image bytes from `public/images` file sizes plus a byte budget from `rules/design.md`/`perf_audit.py` thresholds. The LCP candidate is the hero.
- [ ] Wire, test, commit.

### Task 7: Rules and records (rulings 4, 5, 9, 10)
- [ ] Ruling 4: add the `data/faq.json` row "How rare are blue Staffies?", answered from coat facts already held, no rarity figure; the `covered_by` row in the question file; the faq-bottom pick.
- [ ] Ruling 5: rule text in `rules/copy.md` and the query-augmentation skill; a rule-index row.
- [ ] Ruling 9: close KI 70.
- [ ] Ruling 10: `page-run.md` row 10, `rules/design.md`, and the rule-16 gate extended to every section component, with a test that two pages sharing a component file fails (the 12 pre-rule pages exempt). Memory note.
- [ ] Commit.

### Task 8: Status-line mod (ruling 11)
- [ ] Controller loads `plugin-authoring` and writes the mod in `~/.claude/dev-mods/<session>/bsuk-status/`. It shows branch · page (from the newest plan) · STOP n (from `data/boards/<slug>.json` approval state) · last check:all (from `docs/reports/` mtimes, never by running the gates) · Gemini calls today (`gemini_log.summary`). Run `claude plugin validate`.

### Task 9: Rebuild, republish, re-approve
- [ ] Build, then previews, then the board. Read the artifact, then publish to the same URL (db plus fonts).
- [ ] Post a short batch with one question: "Approve board v3?". Commit.

### Task 10: Gates
- [ ] Run `check:all`, `test:render:meta`, and `test:py` (the known `test_render_baseline` failure only).
- [ ] Run verification-before-completion, the handoff `--write`, and the memory update.
