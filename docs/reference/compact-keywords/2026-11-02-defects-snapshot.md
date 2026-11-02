# Pup pages + hub — measured defects (2026-11-02, cloud session)

Measured on the `manchester-page` snapshot (3e8f87f, 2026-10-09), NOT on `foundation`.
Re-run every check on `foundation` before acting; anything already fixed there is dropped.

Commands: `npx astro build`; `python3 scripts/final_page_audit.py <slug>`;
`python3 scripts/page_hardening_scan.py <slug>`; a `<main>` word count; Playwright
screenshots at 1280 / 820 / 390.

| # | Page | Defect | Evidence | Rule |
|---|---|---|---|---|
| 1 | all 6 pup pages | 36–42 words in `<main>` — a skeleton | word count | user brief (compact 850) |
| 2 | `/available-puppies/` | 64 words | word count | user brief |
| 3 | all pup pages | "Deposit £500, refundable" — plain "refundable" | `[slug].astro` dl; screenshot | `delivery-band-on-every-card` (amended 2026-09-30): use `deposit_refund_clause` |
| 4 | all pup pages | H1 template hard-codes "Blue Staffy Puppy" — Byrd (White) renders "White Male Blue Staffy Puppy" | `[slug].astro` `h1` | accuracy; `bsuk-puppy-page-excellence` cannibalisation |
| 5 | Roman (and any two-word colour) | H1 not Title Case ("Blue and white") | `page_hardening_scan.py` ERROR | `rules/headings.md` Title Case |
| 6 | all pup pages | H3–H6 absent; final pass FAIL `all_h1_h4, all_six_levels, min_h5_5, min_h6_5` | `final_page_audit.py` | `rules/headings.md` (see compact DECISION D1) |
| 7 | pup pages + hub | FAIL `cites_credentials_early`, `lifespan_12_14`, `newsletter_present` | `final_page_audit.py` | gate checks |
| 8 | hub | FAIL `img_lazy_nonhero` | `final_page_audit.py` | perf |
| 9 | hub | No `ItemList` of `Product` nodes in schema (only BreadcrumbList/LocalBusiness/WebPage/WebSite) | audit schema list | `product-schema-per-pup` |
| 10 | pup pages, desktop | main photo capped at 560px, single 120px thumbnail, empty right column below the CTA | screenshot 1280 | user brief: "small image on desktop" |
| 11 | pup pages, mobile | photo inset by the 20px gutter, not edge to edge; thumbs fixed 120px | screenshot 390 | user brief: "not full screen / edge to edge" |
| 12 | pup pages | facts `<dl>` renders as unstyled stacked lines; H1 at body size | screenshot | design rules 2, 4 |
| 13 | pup pages | Enquire button uses `--color-ink` inline style, not the `--color-cta` pill | `[slug].astro` inline `style=` | design rule 3 (CTA = brass pill) |
| 14 | pup pages | no cross-link to other pups | markup | user brief |
| 15 | Cheryl, Ince, Vennie | photos/markings superseded by the breeder's new BlackStaffy images (local only) | user brief 2026-11-02 | `rules/images.md` working rule 11 (served images are never renamed; new files beside) |
