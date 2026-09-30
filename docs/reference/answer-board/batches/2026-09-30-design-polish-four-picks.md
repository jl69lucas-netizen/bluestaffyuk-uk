# Design polish · four picks for the built pages

These four design items were left over from the heading-scale fix (Known Issue 97). Each one is
shown before and after on the built pages at 375, 768 and 1280px:
https://claude.ai/artifact/62uBFgPUhReLHb2mcDPsZW. Nothing changes until you pick. Claude's
recommendation is marked.

## Headings

1. **What colour should headings be?** Headings are near-black ink today. The design rules and
   the London components use the brand blue. Recommended: (a). It follows `rules/design.md` rule 1,
   and the site's components already paint 138 of their 169 headings blue. Trade-off: contrast
   drops from 15.7:1 to 11.8:1 on white, still more than twice the accessibility minimum.
   **Where it goes:** `src/styles/board-styles.css` on all built pages.
   - (a) Brand blue for section headings and subheadings
   - (b) Brand blue for section headings only; subheadings stay ink
   - (c) Keep ink
2. **How bold should the headings inside boxes be?** Boxed section headings are regular weight
   today, while all other section headings are bold. Recommended: (a). It matches the other section
   headings and London. Trade-off: on phones three more long boxed headings run to four lines
   (two with 600).
   **Where it goes:** `src/styles/board-styles.css`.
   - (a) Bold (700), like the others
   - (b) Semi-bold (600)
   - (c) Keep regular

## Layout

3. **Should plain text and boxed text start at the same left edge on desktop?** On the dial
   pages, plain text starts 24px left of boxed text from 1024px up. On the blog post, the body
   starts 212px right of its title and date at 1280px. Recommended: (a). Every page gets one
   edge, and the blog post body lines up with its title. Trade-off: photos in plain sections
   are 48px narrower on desktop.
   **Where it goes:** `src/styles/board-styles.css` and the blog post template.
   - (a) One edge, the box's, with the blog body on the title's edge
   - (b) Boxes move out 24px to meet the plain text
   - (c) Keep as is
4. **How should the breadcrumb look?** Today it reads "Home ›How To Choose…": there is no space
   after the arrow on all 49 pages, and the blog crumb is not in the site's title casing.
   Recommended: (a). It gives one spacing and one casing everywhere. Trade-off: on 10 old city pages
   the crumb's casing will differ slightly from their old headings until those pages are
   rebuilt.
   **Where it goes:** `src/components/Breadcrumb.astro` and `src/layouts/BaseLayout.astro`.
   - (a) Space after the arrow, and the site's title casing everywhere
   - (b) Space after the arrow, casing fixed on the blog only
   - (c) Space after the arrow only
