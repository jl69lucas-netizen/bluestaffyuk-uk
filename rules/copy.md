# Voice, originality and claims

Rules moved out of `CLAUDE.md` on 2026-08-02 (Phase 4). **The rule text is verbatim.**

`enforced:` says what actually holds the rule up.
`test` — a committed check fails when the rule is broken. `judgment` — no mechanical
decision procedure exists, and `data/quality/rule-index.json` records why.
`untested` — **a deletion candidate**: it is asserted and nothing enforces it.
`scripts/quality_report.py` §5 lists every one of those on every run, which is the point.


---
id: write-from-outline-never-from-sibling
enforced: judgment
family: DUP
---

- **Write-From-Outline, NEVER-From-Sibling — no template/prose mirroring between pages (ALWAYS) — applies to every page, agent, skill, and build** — The recurring, time-wasting failure (puppy page → location page → buying guide) is copying a sibling page's `.astro`/`.md` as a scaffold and keeping its sentences, then reactively rewording to pass the dup-gate. **STOP doing that.** Reuse **components, CSS classes, and structural patterns** freely (that's the kit) — but **every page's PROSE must be written fresh from that page's own approved outline + distribution matrix, never pasted or paraphrased from another page's body copy.** Concretely: (1) do **not** open a sibling's page file to copy paragraphs — open it only to read its component/CSS structure; (2) write each section's copy from the outline in genuinely different framing, sentence structure, angle, and vocabulary than any sibling (lean on the page's OWN entity/angle — e.g. a puppy page = that pup's own colour, temperament and litter; a location page = the region, its travel time and its DEFRA-approved delivery band; a buying guide = the decision the reader has not made yet); (3) the only text that may match a sibling verbatim is the **whitelist** (the delivery-band line, doc-badge lists, counter strip, the deposit notice, CTA button labels, real reviews, real page-name link labels) — everything else must be original; (4) run `scripts/dup_content_audit.py` (body) **AND** `--headers` **on your OWN draft BEFORE it is "done"**, targeting **zero** non-whitelist crossover, so dedup is a pre-write discipline, not a post-hoc cleanup. Different pages about related products should read like they were written by the same breeder on different days — same voice, different words — never like one was find-replaced from the other. This is binding for the puppy, comparison, location, and every other sibling-cluster build. In the source repo this rule was injected into every agent's Golden Rules by an injector script; the injectors are not ported (spec §2). Here the pack is the only source.

---
id: first-person-brand-voice
enforced: judgment
family: COPY
---

- **First-Person Brand Voice (ALWAYS) — applies to EVERY section of the homepage and EVERY page site-wide** — Write as the breeder in **first-person plural POV: "we / us / our / here at BlueStaffyUK."** Our puppies, credentials, and process are framed as *ours*, not described from the outside: ✅ "Here at BlueStaffyUK, **our** blue and brindle Staffies…", "**we** home-raise every pup in the house", "**our** DNA-tested parents" — ❌ generic third-person like "Both make exceptional companions" or "Staffordshire Bull Terriers are…" when the sentence is about *our* offering. The voice is Lisa Bright's, writing from Carlisle, Cumbria — a breeder talking about her own litters, not a catalogue describing a breed. Exceptions (stay neutral/encyclopedic where first-person would be false or awkward): factual species/taxonomy/entity statements (e.g. "*Canis lupus familiaris*, Staffordshire Bull Terrier, is a KC-recognised terrier breed"), cited research, and outbound-authority facts. First-person never means overclaiming — a licence or statute claim is written `LICENCE_CLAIM_PLACEHOLDER` / `LEGAL_CLAIM_PLACEHOLDER` until it is confirmed, never asserted. When rewriting or building any section, default to this voice; flag anything still in third-person brand copy.

---
id: entity-4-move-loop
enforced: untested
family: COPY
---

- **Entity 4-Move Loop is the required section-build method (ALWAYS)** — When building or improving ANY page section, run the loop: (1) **Structural Critique** → (2) **Recommended Entities + WHY** (grounded: KG authority / PAA demand / competitor gap / buyer intent) → (3) **Optimized Draft** (verified facts only) → (4) **Topical-Cluster Strategy** (internal links + schema; extend existing JSON-LD, never duplicate; FAQ schema must be visible; verify in `dist/`). The active engine is `@bsuk-entity-incorporation-agent`, which runs the loop and drafts the section, and `@bsuk-seo-content-writer` writes body copy from its approved draft; its vocabulary is `.claude/skills/bsuk-entity-agent/SKILL.md` (a passive catalog, not a builder). Every health/credential entity is bounded by `data/quality/evidence-ledger.json` — the health entities are the **BVA hip and elbow scores** and the **L2-HGA, HC and PHPV DNA tests**, and each one stays marked `NOT FETCHED` until the certificate is on file. Never assert a score, a test result, or a licence beyond what Lisa Bright has confirmed; an unconfirmed licence or statute claim is written `LICENCE_CLAIM_PLACEHOLDER` / `LEGAL_CLAIM_PLACEHOLDER`.

---
id: meaningful-words-no-stop-words
enforced: untested
family: COPY
---

- **Meaningful words, no stop-word filler (ALWAYS) — naming surfaces on every build/rebuild/edit** — URL slugs, anchor text, headings, image filenames, image alt text, meta titles, and labels use meaningful content words only; drop `of/the/and/for/with` fillers where grammar allows. Body prose and the locked conversational question-header pattern are exempt. Canonical spec: `.claude/skills/anti-ai-writing/SKILL.md §Meaningful Words`.

---

## Evidence — say it once, then prove it (2026-09-09)

**Not a rule and deliberately carries no front-matter.** Each of the eight checks below is its own row in `data/quality/rule-index.json` (`term-budget-per-page` … `no-unsourced-superlatives`); an umbrella `evidence-pass` row on top of them would count the same enforcement twice.

Eight checks in `scripts/evidence_audit.py`, run per slug against `dist/`. Budgets: `data/quality/evidence-budgets.json` · proof ledger: `data/quality/evidence-ledger.json` · method: `.claude/skills/bsuk-evidence-pass/SKILL.md`.

**Review placement on a page (spec §11 amendment 3e, 2026-09-18; the paragraph moved out of the check list below in Task 19, where it read as a fifth bullet).** A page's reviews are the rows in `data/reviews.json` whose `source` is that page. A page with one such row renders one `single` block; a page with three or more renders one `grid` plus the remainder as `single` blocks. `Testimonial` takes both: `mode` says which shape, and an explicit `reviews` array is the list the block renders in full, which is how the remainder is placed. None are dropped — a row with nowhere to go is a placement bug, not a trim — and none are invented, so a slot with no real review takes the review placeholder token rather than a written one. Where the blocks sit on the page, top / middle / bottom, is a board decision made per page, not a property of the component.

- `term-budget-per-page` (blocking) — every calibrated term stays within its per-page budget; uncalibrated pages report, they do not pass. Per-slug override: `budgets_by_slug` — a number replaces the page-type ceiling, `null` removes it.
- `claim-bound-to-proof` (blocking) — every health / credential / price claim resolves to a ledger entry; un-ledgered = not assertable.
- `claim-unledgered` (blocking on new location, comparison and blog pages; advisory elsewhere) — a sentence that uses the ledger's health or credential `vocabulary` (BVA hip and elbow scores, DNA tests and "clear" results, KC registration, a breeder licence, vet checks, health testing) must match, in the same sentence, a ledger `claims` row whose `covers` names that vocabulary id, or carry the placeholder for that claim. A question, a denial, advice to the buyer and a reference to a page about the test are not claims; preview pages are not checked. The fix is a ledger row (proof `NOT FETCHED` until the document is on file), never a wider vocabulary pattern.
- `statement-labels-present` (advisory) — a `StatementLabel` sits on each proven claim so the reader can see what is proven and what is opinion.
- `review-attribution-unique` (blocking) — no reviewer quote is attributed to two different people across the site (`data/reviews.json` is the single source; it landed in project 3 and holds only quotes that exist verbatim on a migrated page, each row naming that page in `source`; a slot with no real review takes the review placeholder token that `scripts/placeholder_check.py` counts, never an invented quote).

- `title-length-max` (blocking) — `<title>` never exceeds `title_max_chars` from the budgets file (per-slug override: `title_max_chars_by_slug` — Foundation's migrated titles carry measured baselines that project 4 brings back under 70).
- `no-not-fetched-in-prose` (blocking) — the literal `NOT FETCHED` never ships in visible text; it is a research placeholder, not copy.
- `no-unsourced-superlatives` (advisory) — "best / #1 / world's" etc. need a link to the source in the same sentence.

---
id: outline-provenance-gate
enforced: test
family: DUP
test: tests/py/test_outline_provenance_check.py
---

- **Outline provenance — a location, comparison or blog page is built from its approved outline and from nothing else (system-gaps, 2026-09-24)** — The mechanical half of `write-from-outline-never-from-sibling`, binding the new-family pages only (`scripts/family_rules.py`; the twelve pages built before this build are never examined). `scripts/outline_provenance_check.py <slug>` reads the page's approved board record and its built page and FAILs when: the record is not approved; a body H2 or H3 is not in the outline, an outline H2 or H3 is not on the page, or the two are in a different order; a labelled section is not a section of the record; a heading repeats on the page; a body heading equals a heading on another built page, exactly or with the breed or the city swapped; or body prose shares a 12-word run, or a sentence of six or more words (city swapped or not), with another built page outside the `scripts/dup_content_audit.py` whitelist. The frame (hero, takeaways, counter, trust strip, TOC, reviews, FAQ blocks, newsletter, form) is never compared. An H3 a component renders, such as an info card's heading, is an outline node: put it in the record's tree at board time or leave it out of the page. `npm run check:all` runs it over every new-family page listed in `data/facts/rebuilt.json`; the builder runs it on its own slug before listing the page. At board time, `scripts/family_rules.py` check `outline-heading-repeat` refuses an outline that carries one heading twice, so the record cannot be approved with a duplicate the build would copy. The whitelisted stock lines in `scripts/dup_content_audit.py` (the delivery-band line, the exact deposit-£500-refundable line) may repeat; any other fact sentence, such as a new way of stating the deposit or a price, must be written fresh on each page: the gate flags it, and the fix is rewording, never a whitelist entry.
