# BlueStaffyUK Session Log and Known Issues

History and open defects. Nothing here is a rule; it is state. The source repo's log was
replaced wholesale rather than re-based — it was eighteen months of another site's build
history, and translating it would have invented a past this repo does not have.

## Project 1 — Foundation (2026-09-15/16) — COMPLETE

The Astro 6.3.8 static site, the rule packs, the Python suite and the render harness.
Full report and evidence: `docs/reports/foundation-gate-report.md`.

## Project 2 — System transfer (2026-09-16) — IN PROGRESS

Moves the site operating system — rules, agents, skills, gate scripts and reference docs —
from the source repo into this one, re-based onto a Glasgow Staffordshire Bull
Terrier breeder, with `scripts/marker_check.py` as the zero-tolerance
proof. `data/port-manifest.json` is the record of every file that crossed.
Plan: `docs/superpowers/plans/2026-09-16-system-transfer.md`.

## Known Issues

Seeded from the Foundation gate report's "Open items" 1–8. Items 1 and 2 are closed by
project 2; 3–8 are carried forward with their owning project.

1. **`FORM_ENDPOINT` contract — CLOSED by project 2.** The contact-page form contract was
   re-based onto this repo's own fields and endpoint env key. See
   `scripts/form_contract_audit.py` and `tests/render/checks/form.ts`.
2. **The DUP whitelist — CLOSED by project 2.** The duplicate-content whitelist was
   re-based onto this site's own built pages, together with the fixture that depends on
   its stems. See `scripts/dup_content_audit.py`.
3. **The orphan check is blinded by the catch-all route.** `builtRoutesWithoutSource()` in
   `tests/render/lib/freshness.ts` compares built routes to source routes, and the
   root-level `src/pages/[...post].astro` matches any path — so while it exists the
   function cannot prove any route orphaned, static pages included. The mtime comparison is
   the only remaining freshness signal. A real answer needs a check that reads the content
   collection rather than the filesystem. **Carried forward.**
4. **Puppy `srcset` 2x rows.** 15 blocking rows over 6 pages, the same images as the puppy
   page's 2277 ms LCP. **Project 3's image pass** should fix both at once.
5. **`nav-jump-target-lands` baseline.** 18 rows over 6 pages remain after the shell fix.
   `--hdr` is measured from the header (`--hdr-measured`), with the media query kept as the
   no-JS fallback, so the remaining rows are migrated in-page anchors rather than chrome
   miscalculation. **Carried forward.**
6. **17 stub locations are noindexed.** They carry 0–7 words of legacy body.
   **Project 5** writes them; `scripts/sitemap_check.py` keeps them out of the shards until
   then.
7. **Placeholders.** `SITE_URL_PLACEHOLDER`, `PHONE_PLACEHOLDER` and the form id are
   resolved at **project 6** launch. `BSUK_RELEASE=1 npm run check:placeholders` is the
   gate that will refuse to ship them.
8. **`schema-date-modified-present`.** 18 rows over 6 pages; needs
   `scripts/generate_page_dates.py` wired into the content pass, which arrives with
   **project 4** — the same project that gives pages a real edit history for sitemap
   `lastmod`.
