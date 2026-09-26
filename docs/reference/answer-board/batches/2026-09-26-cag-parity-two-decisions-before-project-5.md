# CAG parity · two decisions before project 5

The CAG page-brief audit (https://claude.ai/artifact/S5xqdrrgFmmgcWFuuoqTGN) found 25 gaps to close
before project 5. Two of them change what the pages look like, so they are yours to pick. The
plan builds the recommended option unless you pick otherwise. Claude's recommendation is marked.

## Page design

1. **What box should in-body images use on the new city, comparison and blog pages?** CAG renders
   every in-body photo and infographic in one box: 760px wide at 16:9, with portraits
   full-bleed at 4:5 on phones. BSUK's rebuilt pages use `.bl-img`: full width, capped at 420px
   from 900px up, at the photo's own ratio. Working rule 17 puts an image under every heading on
   30+ new pages. Recommended: (a) — a fixed box cannot shift the layout while images load, and it
   lets the "image first under every H3" check actually find the images (today it matches
   nothing). Trade-off: the 12 built pages keep `.bl-img` until they are next touched.
   **Where it goes:** CAG brief §15a; plan Task 8; the kit image CSS.
   - (a) CAG's uniform box on new pages (760px, 16:9; portrait 4:5 full-bleed on phones)
   - (b) Keep `.bl-img` everywhere; only enforce measured `sizes`
2. **Should the footer's "Ready to meet the litter?" band obey the board's global CTA setting?**
   12 of the 13 approved boards set `global_cta` to hidden, but the footer always shows the band,
   so those built pages do not match what you approved. Recommended: (a) — build what was
   approved. Trade-off: the band disappears from the 12 built pages that chose hidden (each keeps
   its own in-page CTA).
   **Where it goes:** plan Task 7; `SiteFooterKit.astro`; every board.
   - (a) Wire it: "hidden" hides the band on that page
   - (b) Retire the setting: the band shows on every page and boards stop asking

## Anything else
