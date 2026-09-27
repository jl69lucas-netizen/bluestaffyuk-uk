# The Mobile Hero-First Fix — What Changed on the Built Pages

`src/components/kit/Hero.astro` now paints the photo first at 900px and below (Plan 1 Task 11).
Shots at 375×812, top of page to the hero's foot, before and after:
`/Users/apple/Downloads/BSUK/BSUK-refs/london/_hero-fix/{before,after}/<slug>.png`, with the
measurements in `heroes.json` beside them (`node scripts/hero_phone_shots.mjs <out dir>`).

Eight phone views changed. The other four already painted the photo first, and their before and
after shots are byte-identical. Widths above 900px are untouched: the fix sits inside the
existing `@media (max-width: 900px)` block, so every desktop contract stays as it was. Tablet
widths up to 900px (768 in the render harness) get the same photo-first order as phones.

| Page | Hero pick | Layout | Before (375px) | After (375px) | Changed |
|---|---|---|---|---|---|
| / | H-HM2 | mosaic (top) | heading first (photo 899px, heading 333px) | photo first (278 / 592) | yes |
| /blue-staffy-blog-guides/ | H-BL3 | mosaic (top) | heading first (749 / 376) | photo first (321 / 610) | yes |
| /blue-staffy-health-uk/ | H-GD1 | split (right) | heading first (757 / 376) | photo first (321 / 610) | yes |
| /buy-blue-staffy-puppies-uk/ | H-FS1 | mosaic (right) | heading first (912 / 386) | photo first (352 / 645) | yes |
| /buy-staffy-puppies-for-sale-uk/ | H-FS2 | bleed (top) | heading first (1033 / 355) | photo first (321 / 589) | yes |
| /privacy-policy-uk/ | H-UT1 | mosaic (right) | heading first (581 / 356) | photo first (322 / 588) | yes |
| /thank-you-blue-staffy-puppies-journey/ | H-UT1 | mosaic (right) | heading first (648 / 377) | photo first (322 / 610) | yes |
| /uk-blue-staffy-breeders-contact/ | H-UT1 | mosaic (right) | heading first (587 / 356) | photo first (322 / 588) | yes |
| /blue-staffy-pup-sale-uk/ | H-FS3 | stacked (top) | photo first (321 / 559) | photo first (321 / 559) | no |
| /blue-staffy-uk-breeders/ | H-AB1 | mosaic (left) | photo first (321 / 614) | photo first (321 / 614) | no |
| /uk-blue-staffy-puppy-buying-guide/ | H-GD2 | stacked (top) | photo first (322 / 581) | photo first (322 / 581) | no |
| /uk-staffordshire-bull-terrier-guide/ | H-GD3 | panel (left) | photo first (322 / 581) | photo first (322 / 581) | no |

The figures in brackets are the photo's top and the heading's top in px from the top of the
viewport. The hero pick is the section's pick in force, from `data/design/city-must-differ.json`.

The fix is held by `layout-hero-image-first-mobile` (`tests/render/checks/layout.ts`), blocking
on every page: the photo must precede the heading in source at every width, and paint above it
at 900px and below.
