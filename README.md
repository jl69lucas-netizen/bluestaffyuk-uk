# BSUK — BlueStaffyUK rebuild (Astro 6.3 + Tailwind 4.3)

Project 1 (Foundation) migrates the old WordPress export at `~/bluestaffyuk-site` verbatim. Later projects: system transfer, design system, page rebuilds, new pages, launch. Specs and plans live in `docs/superpowers/`; reports in `docs/reports/`.

## Pipeline order

```bash
npm install && python3 -m pip install -r requirements.txt
npm run extract     # WordPress export -> src/pages/*/index.astro, data/locations.json, data/page-map.json, src/content/blog
npm run bake        # baked WebP under public/images + data/image-manifest.json, then re-runs extract with measured srcset
npm run redirects   # data/redirects.json -> public/_redirects
npm run llms        # data/page-map.json -> public/llms.txt
npm run build       # astro build -> dist/ (postbuild writes the sitemaps into dist/)
npm run check:all   # parity, redirects, schema, sitemaps, placeholders gates (reports in docs/reports/)
npm run test:py     # pytest
npm run test:render:meta && npm run test:render:pages   # ends in build_scorecard.mjs, the zero-examined guard
```

## Generated vs hand-authored

Generated (never edit by hand): `src/pages/<slug>/index.astro` (11 rich pages), `data/page-map.json`, `data/locations.json`, `data/image-manifest.json`, `public/_redirects`, `public/llms.txt`, `public/images/**`, `src/content/blog/*.md` (migrated posts).

Hand-authored: everything under `src/components`, `src/layouts`, `src/lib`, `src/pages/uk-locations`, `src/pages/available-puppies`, `src/pages/blog`, `src/pages/[...post].astro`, `data/settings.json`, `data/price-matrix.json`, `data/puppies.json`, `data/redirects.json`, `scripts/`, `tests/`.

Placeholders until launch: `SITE_URL`, `PHONE_PLACEHOLDER` in `data/settings.json`, `PUBLIC_FORMSPREE_ID` (see `.env.example`). `BSUK_RELEASE=1 npm run check:all` refuses a build that still carries them.
