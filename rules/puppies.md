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
enforced: untested
family: COPY
---

- **Puppy-cluster meta — extended 3-part format (ALWAYS, all puppy/buy pages) — titles may run to ~280 chars** — Every puppy-cluster page uses the extended 3-part meta (do NOT truncate to a short title): **Title** = `Primary Keyword | Related Conversational Query | Number + Positive Word | Brand — LSI/NLP Keywords` (front-load the primary keyword; extend toward but never past **280 characters**). **Description** = `Primary Benefit | Secondary Benefit | Trust Signal + CTA` (≤300). Real price floor (£1,500 for Roman, Byrd and Ince; £1,700 for Vennie, Christa and Cheryl — from `data/price-matrix.json`, never typed by hand) + real credentials + branded ending. A licence or statute claim in a title or description is written `LICENCE_CLAIM_PLACEHOLDER` / `LEGAL_CLAIM_PLACEHOLDER` until it is confirmed. Canonical spec: `.claude/skills/bsuk-puppy-page-builder/SKILL.md` §6a.

---
id: delivery-band-on-every-card
enforced: test
family: COPY
---

- **Delivery band on every card + delivery section (ALWAYS) — applies to every card/section builder** — Any puppy/listing card MUST display the delivery cost directly (canonical line under the trust badges: `UK home delivery £200–£350 by distance · or collect in Carlisle`), and every delivery section MUST show both options in full: **UK home delivery £200–£350, priced by distance, by DEFRA-approved transport**, and **collection in person from Carlisle**. It is a **band, not a flat fee** — never print a single figure as "the" delivery price, and never quote a number outside £200–£350. The £500 deposit is stated wherever the band is, as "refundable up to 70% if a visitor fails to show up" and never plainly "refundable"; viewing is deposit-first, framed as the £500 deposit booking the viewing and reserving the puppy (the user's ruling, 2026-09-27, `docs/reference/answer-board/answers/2026-09-24-questions-for-lisa-bright-followup-2026-09-27.md`). Figures live in `data/settings.json` and `data/price-matrix.json` — read them, never hardcode a different number. Never ship a card without the delivery line.

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
enforced: untested
family: IMG
---

- **No head-cropped puppy portraits (ALWAYS — Foundation)** — A puppy portrait shows the **whole dog**, or at minimum the head and chest with the ears and muzzle complete inside the frame. The 16:9 in-body box and the card thumbnail both crop hard, and a centred crop on a tall portrait decapitates the pup — Foundation found this on migrated WordPress masters. Tune **`object-position` per image** so the head sits inside the box (the box size never changes, only the focal point); where no focal point saves the frame, re-cut the master with `PIL.ImageOps.fit(..., centering=...)` rather than shipping the crop. A buyer cannot judge a dog whose head is outside the picture. Reviewed by eye at build time; there is no check yet, which is exactly why this rule is a deletion candidate until one exists.

---
id: puppy-cluster-component-order
enforced: test
family: LAYOUT
test: tests/render/checks/layout.ts::layout-hero-counter-separation + layout-h3-image-first
---

- **Component order in the puppy cluster (ALWAYS — breeder, 2026-08-07)** — Three ordering rules ship together, each with a check: (1) **Hero → separator → counters**, per `rules/design.md` `layout-hero-counter-separation`; a page tuple that names a counter strip must also name its separator. (2) **H3 → image → prose**, per `rules/design.md` `layout-h3-image-first`. (3) **On mobile the hero IMAGE comes first** — in a one-column hero grid the copy column is first in the DOM, which pushes the puppy cards below the fold on a phone; move the image with CSS `order`, never by reordering the DOM, so the H1 stays first in the reading order for assistive tech and for SEO. (4) **Further-reading thumbnails are the target page's hero**, per `rules/images.md` `read-card-thumb-is-target-hero`.
