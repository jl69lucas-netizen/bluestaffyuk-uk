# The puppy and buy cluster

Rules moved out of `CLAUDE.md` on 2026-08-02 (Phase 4) and re-based for BlueStaffyUK
2026-09-16. **The rule text is verbatim except where the source fact did not survive the re-base.**

`enforced:` says what actually holds the rule up.
`test` — a committed check fails when the rule is broken. `judgment` — no mechanical
decision procedure exists, and `data/quality/rule-index.json` records why.
`untested` — **a deletion candidate**: it is asserted and nothing enforces it.
`scripts/quality_report.py` §5 lists every one of those on every run, which is the point.


---
id: puppies-extended-meta
enforced: test
family: COPY
test: tests/py/test_page_board.py
---

- **Puppy-cluster meta — one-clause title ≤70 characters, description ≤160 (ALWAYS, all puppy/buy pages)** — Every puppy-cluster page follows the sitewide meta standard, `docs/reference/seo-rules.md` Rule 21 and Rule 23: the **title** is one clause, no pipe separators, front-loads the primary keyword and ends with the brand, **≤70 characters**; the **description** is one sentence flow carrying the primary keyword, a long-tail or LSI variation, a trust signal and a CTA, **≤160 characters** (the page board's band is 140–160). Real price floor (£1,500 for Roman, Byrd and Ince; £1,700 for Vennie, Christa and Cheryl — from `data/price-matrix.json`, never typed by hand) + real credentials + branded ending. A licence or statute claim in a title or description is written `LICENCE_CLAIM_PLACEHOLDER` / `LEGAL_CLAIM_PLACEHOLDER` until it is confirmed. Canonical spec: `.claude/skills/bsuk-puppy-page-builder/SKILL.md` §6a. **Amended 2026-09-30 (user, answer board batch `2026-09-30-for-sale-rules-three-decisions` q03):** the former extended 3-part format — titles run toward 280 characters, descriptions ≤300 — is retired, matching CAG's own 2026-09-09 ruling; the rule id is kept so the ledger row carries its history. The length ceilings are enforced by `scripts/pageboard.py` `meta-length` (title ceiling from `data/quality/evidence-budgets.json` `title_max_chars`, description 140–160) and reported by `scripts/evidence_audit.py` `title-length-max`; "one clause" itself has no mechanical check.

---
id: delivery-band-on-every-card
enforced: test
family: COPY
---

- **Delivery band on every card + delivery section (ALWAYS) — applies to every card/section builder** — Any puppy/listing card MUST display the delivery cost directly (canonical line under the trust badges: `UK home delivery £200–£350 by distance · or collect in Carlisle`), and every delivery section MUST show both options in full: **UK home delivery £200–£350, priced by distance, by DEFRA-approved transport**, and **collection in person from Carlisle**. It is a **band, not a flat fee** — never print a single figure as "the" delivery price, and never quote a number outside £200–£350. The deposit is stated wherever the band is, from its data keys only: the amount from `data/settings.json` `deposit_gbp`, and its refund term only from the refund-clause key added to `data/settings.json` at build (session brief 2026-09-30, Open Flags) — never called plainly "refundable" (amended 2026-09-30). Figures live in `data/settings.json` and `data/price-matrix.json` — read them, never hardcode a different number. Never ship a card without the delivery line.

---
id: product-schema-per-pup
enforced: test
family: SCHEMA
test: tests/render/checks/schema.ts::schema-single-product-offer
---

- **One `Product` per pup, with exactly one `Offer` (ALWAYS — Foundation)** — Every individual puppy carries its **own** `Product` node in JSON-LD, with its own `name`, `image`, `description` and **exactly one** `offers` object holding that pup's real price in `GBP` (£1,500 for Roman, Byrd and Ince; £1,700 for Vennie, Christa and Cheryl). A page listing several pups wraps them in an `ItemList`, one `Product` per entry — never a single `Product` with several offers, and never a second bare `Product` outside the list, which is what Foundation found and fixed. Prices come from `data/price-matrix.json`; a price written into markup by hand is a defect even when it is currently right. Enforced by `tests/render/checks/schema.ts::schema-single-product-offer`.

---
id: instock-only-on-an-available-pup
enforced: test
family: SCHEMA
test: tests/render/checks/schema.ts::schema-sold-not-instock
---

- **`InStock` only on a pup that is actually available (ALWAYS — Foundation)** — `availability` is a fact about a specific animal, not a template default. A pup marked sold, reserved, or held on deposit in `data/puppies.json` MUST render `https://schema.org/SoldOut` (or `PreOrder` where a deposit is held and the pup has not left), and only a pup still available renders `InStock`. A sold pup advertised as `InStock` puts a rich result in front of a buyer for an animal they cannot have, and the page's own visible copy already says so — the schema is what disagrees. The status is read from `data/puppies.json`; it is never written twice. Enforced by `tests/render/checks/schema.ts::schema-sold-not-instock`.

---
id: no-head-cropped-portraits
enforced: test
family: IMG
test: tests/render/checks/img.ts::img-face-visible
---

- **No head-cropped puppy portraits (ALWAYS — Foundation)** — A puppy portrait shows the **whole dog**, or at minimum the head and chest with the ears and muzzle complete inside the frame. The 16:9 in-body box and the card thumbnail both crop hard, and a centred crop on a tall portrait decapitates the pup — Foundation found this on migrated WordPress masters. Tune **`object-position` per image** so the head sits inside the box (the box size never changes, only the focal point); where no focal point saves the frame, re-cut the master with `PIL.ImageOps.fit(..., centering=...)` rather than shipping the crop. A buyer cannot judge a dog whose head is outside the picture. Measured since the London component pass (Plan 2): `data/image-focus.json` records each photograph's face boxes, `src/lib/imageFocus.ts` derives the crop from them, and `tests/render/checks/img.ts::img-face-visible` (advisory) fails a face less than 90% painted or more than 10% covered by an overlay such as a name plate.

---
id: puppy-cluster-component-order
enforced: test
family: LAYOUT
test: tests/render/checks/layout.ts::layout-hero-counter-separation + layout-h3-image-first + layout-hero-image-first-mobile
---

- **Component order in the puppy cluster (ALWAYS — breeder, 2026-08-07)** — Three ordering rules ship together, each with a check: (1) **Hero → separator → counters**, per `rules/design.md` `layout-hero-counter-separation`; a page tuple that names a counter strip must also name its separator. (2) **H3 → image → prose**, per `rules/design.md` `layout-h3-image-first`. (3) **The hero IMAGE comes first**, per `rules/design.md` rule 10 (`layout-hero-height-and-image-first`): the image element precedes the copy in the DOM, CSS `order` places it where the desktop layout wants it, and below 900px the photo paints first. *Amended 2026-09-30: the carried-over CAG wording (H1 first in the DOM, image moved by CSS `order`) contradicted design rule 10, which the tests enforce (`tests/py/test_design_components.py::test_built_hero_puts_the_image_before_the_heading`, `tests/render/checks/layout.ts::layout-hero-image-first-mobile`); design rule 10 governs.* (4) **Further-reading thumbnails are the target page's hero**, per `rules/images.md` `read-card-thumb-is-target-hero`.
