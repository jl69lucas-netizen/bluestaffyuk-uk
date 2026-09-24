---
name: bsuk-site-patterns
description: Proven fix patterns for BlueStaffyUK (Astro + Tailwind v4). Use this skill whenever the user asks to fix colors, add search, reposition header elements, add puppy listings, or references something "looking yellow", "search going to Google", "search bar in the wrong place", or "puppies not showing on homepage". Contains the exact code for every fix confirmed working in production.
---

# BSUK Site Patterns — Confirmed Production Fixes

All patterns below are verified: built, committed, and deployed to SITE_URL_PLACEHOLDER.

---

## 1. Color: one accent token, defined once

**Problem:** two near-identical accent variables drift apart, and the same "accent" renders as two different colours across the site.

**How it is arranged now (project 3):** there is exactly one accent, `--color-cta` (brass `#C9A227`), and every colour in the site is a token in **`src/styles/tokens.css`** — the three-layer `@theme` block (primitive → semantic → component). `src/styles/global.css` does nothing but `@import "./tokens.css"` before Tailwind; it declares no colour of its own. A hex outside `src/styles/tokens.css` anywhere in `src/` is a rule-1 violation and `tests/py/test_design_tokens.py` fails on it.

**So the fix for any accent drift is one edit in one file:**
```css
/* src/styles/tokens.css */
@theme {
  /* @layer-primitive */
  --color-brass-500: #C9A227;
  /* @layer-semantic */
  --color-cta: var(--color-brass-500);
  --color-cta-hover: var(--color-brass-600);
  --color-cta-ink: var(--color-steel-900);  /* the label on every brass fill, 6.8:1 */
}
```

**Why it works:** Tailwind v4 resolves utilities from the custom properties in `@theme` at build time. Change the primitive, change every instance — no per-file edits needed.

---

## 2. Local Search with Pagefind (stop redirecting to Google)

**Problem:** Search forms used `action="https://www.google.com/search"` — visitors left the site.

**Solution:** Pagefind — a static site search library that indexes `dist/` after the Astro build and serves results client-side.

### Step 1: Install
```bash
npm install --save-dev pagefind
```

### Step 2: Update build script in `package.json`
```json
"build": "astro build && npx pagefind --site dist"
```

### Step 3: Externalize Pagefind from Rollup in `astro.config.mjs`
Rollup tries to resolve `/pagefind/pagefind.js` at build time but the file doesn't exist until after the build. Mark it external:
```js
vite: {
  plugins: [tailwindcss()],
  build: {
    rollupOptions: {
      external: ['/pagefind/pagefind.js']
    }
  }
},
```

### Step 4: The search page (already built — `src/pages/search/index.astro`; this recipe is the record of how)
```astro
---
import BaseLayout from '../../layouts/BaseLayout.astro';
const title = "Search | BlueStaffyUK";
const description = "Search the BlueStaffyUK website.";
const canonical = "https://SITE_URL_PLACEHOLDER/search/";
---
<BaseLayout {title} {description} {canonical}>
  <section class="py-16 px-4 min-h-[60vh]">
    <div class="max-w-3xl mx-auto">
      <h1 class="font-display font-bold text-3xl text-brand mb-8">Search Results</h1>
      <form action="/search/" method="get" class="flex gap-2 mb-10">
        <input id="search-refine" name="q" type="search" placeholder="Search BlueStaffyUK…"
          class="flex-1 border border-stone-300 rounded-full px-4 py-2.5 text-sm text-brand focus:outline-none focus:border-cta focus:ring-1 focus:ring-cta" />
        <button type="submit" class="bg-cta text-cta-ink font-semibold text-sm px-5 py-2.5 rounded-full hover:bg-cta-hover transition-colors">Search</button>
      </form>
      <div id="results" class="space-y-5"><p class="text-stone-400 text-sm">Loading…</p></div>
    </div>
  </section>
  <script>
    const params = new URLSearchParams(window.location.search);
    const q = params.get('q') ?? '';
    const refineInput = document.getElementById('search-refine') as HTMLInputElement;
    if (refineInput && q) refineInput.value = q;
    const resultsEl = document.getElementById('results')!;
    async function runSearch() {
      if (!q.trim()) { resultsEl.innerHTML = '<p class="text-stone-500 text-sm">Enter a search term above.</p>'; return; }
      let pagefind: any;
      try { pagefind = await import('/pagefind/pagefind.js'); } catch {
        resultsEl.innerHTML = '<p class="text-stone-500 text-sm">Search index not available — try after next deploy.</p>'; return;
      }
      const search = await pagefind.search(q);
      if (!search.results.length) { resultsEl.innerHTML = `<p class="text-stone-500 text-sm">No results for "<strong>${q}</strong>".</p>`; return; }
      const items = await Promise.all(search.results.slice(0, 12).map((r: any) => r.data()));
      resultsEl.innerHTML = items.map((item: any) => `
        <a href="${item.url}" class="block border border-stone-200 rounded-xl p-5 hover:border-cta/50 hover:shadow-sm transition-all group">
          <div class="font-display font-semibold text-brand text-lg group-hover:underline transition-colors mb-1">${item.meta?.title ?? item.url}</div>
          <div class="text-stone-500 text-sm leading-relaxed line-clamp-2">${item.excerpt ?? ''}</div>
          <div class="text-brand text-xs mt-2 font-body">${item.url}</div>
        </a>`).join('');
    }
    runSearch();
  </script>
</BaseLayout>
```

### Step 5: Update all search forms in `src/components/SiteHeader.astro`
Change `action="https://www.google.com/search"` → `action="/search/"` and remove any `<input type="hidden" name="sitesearch" .../>`.

**Build note:** `npm run build` includes pagefind; the pagefind directory under `dist/` is generated automatically. There is no CI until project 6.

---

## 3. Header Search Bar Positioning

### Desktop search LEFT (next to logo)
Group Logo + search in a left flex div. Inquire Now stands alone on the right.

```html
<div class="flex items-center justify-between h-16">

  <!-- Left: Logo + desktop search as a unit -->
  <div class="flex items-center gap-3">
    <Logo />
    <form action="/search/" method="get" class="hidden lg:flex gap-2">
      <input name="q" type="search" placeholder="Search…"
        class="w-40 bg-white/10 border border-white/30 text-white placeholder:text-white/50 rounded-full px-3 py-1.5 text-xs focus:outline-none focus:border-cta" />
      <button type="submit" class="bg-cta text-cta-ink text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-cta-hover transition-colors">Go</button>
    </form>
  </div>

  <!-- Desktop nav (center) -->
  <nav class="hidden lg:flex items-center gap-5 text-sm font-body font-medium">
    {nav links...}
  </nav>

  <!-- Inquire Now (desktop/tablet, right) -->
  <a href="/uk-blue-staffy-breeders-contact/" class="hidden sm:inline-flex items-center gap-2 bg-cta text-cta-ink font-semibold text-sm px-5 py-2 rounded-full hover:bg-cta-hover transition-colors">
    Inquire Now
  </a>

  <!-- Mobile search (between logo and hamburger) -->
  <form action="/search/" method="get" class="flex lg:hidden flex-1 mx-3">
    <div class="flex w-full gap-2">
      <input name="q" type="search" placeholder="Search…"
        class="flex-1 bg-white/10 border border-white/30 text-white placeholder:text-white/50 rounded-full px-3 py-1.5 text-xs focus:outline-none focus:border-cta" />
      <button type="submit" class="bg-cta text-cta-ink text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-cta-hover transition-colors">Go</button>
    </div>
  </form>

  <!-- Mobile hamburger -->
  <details class="lg:hidden relative">...</details>

</div>
```

**Key breakpoint logic:**
- `hidden lg:flex` on desktop search = shows only on lg+ (1024px+)
- `flex lg:hidden` on mobile search = shows on xs/sm/md, hides on lg+
- `hidden sm:inline-flex` on Inquire Now = hides on xs (< 640px), shows on sm+

---

## 4. Available Puppies Listing on Homepage

**Data source:** `data/puppies.json` — one row per pup with `slug`, `name`, `sex`, `price_gbp`, `status`, `colour`, `card_photo`, `gallery`. Prices come from `data/price-matrix.json` through a helper; never type one.

**Placement:** After `<TrustBar />`, before the Variants section in `src/pages/index.astro`.

### Frontmatter data array — **read `data/puppies.json`; never hardcode**:
```js
import puppies from '../../data/puppies.json';
import { price } from '../lib/money';   // renders £1,500 / £1,700 from data/price-matrix.json

// Shape, for reference only — the file is the source:
//   { slug, name, sex, price_gbp, status, colour, card_photo, gallery }
// Roman, Byrd and Ince are £1,500; Vennie, Christa and Cheryl are £1,700.
```

### Section HTML:
```astro
<section class="py-16 px-4 bg-warm-white">
  <div class="max-w-7xl mx-auto">
    <div class="flex items-end justify-between mb-10 gap-4 flex-wrap">
      <div>
        <p class="text-brand font-body text-xs font-semibold uppercase tracking-widest mb-2">This Week's Kennel</p>
        <h2 class="font-display font-bold text-3xl text-brand">Puppies Available Right Now</h2>
        <p class="text-stone-500 mt-2 max-w-md text-sm leading-relaxed">
          Every puppy is home-reared, and has a full veterinary health check, first vaccinations and a microchip before it goes home.
        </p>
      </div>
      <a href="/blue-staffy-pup-sale-uk/" class="text-sm font-semibold text-brand hover:text-cta-hover border border-cta/40 hover:border-cta px-4 py-2 rounded-full transition-colors whitespace-nowrap">
        View all puppies &rarr;
      </a>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {puppies.map(puppy => (
        <article class="bg-white rounded-2xl overflow-hidden shadow-sm border border-stone-100 flex flex-col hover:shadow-md transition-shadow">
          <div class="relative bg-brand/10 h-48 overflow-hidden">
            <img src="/blue-staffy-hero.webp" alt={`${puppy.name} — ${puppy.sex} Blue Staffy`}
              class="w-full h-full object-cover object-center" loading="lazy" />
            <span class="absolute top-3 left-3 bg-cta text-cta-ink text-xs font-semibold px-3 py-1 rounded-full">{puppy.tag}</span>
          </div>
          <div class="p-5 flex flex-col flex-1">
            <div class="flex items-baseline justify-between mb-1">
              <h3 class="font-display font-bold text-xl text-brand">{puppy.name}</h3>
              <span class="text-stone-400 text-xs font-body">📍 Carlisle</span>
            </div>
            <p class="text-stone-500 text-xs font-body mb-3">{puppy.sex} · {puppy.age} · Blue Staffy</p>
            <p class="text-stone-600 text-sm leading-relaxed mb-4 flex-1">{puppy.notes}</p>
            <div class="flex items-center justify-between mt-auto pt-4 border-t border-stone-100">
              <span class="font-display font-bold text-2xl text-brand">{puppy.price}</span>
              <a href={`/uk-blue-staffy-breeders-contact/?puppy=${puppy.id}`}
                class="bg-cta text-cta-ink text-xs font-semibold px-4 py-2 rounded-full hover:bg-cta-hover transition-colors">
                Inquire
              </a>
            </div>
          </div>
        </article>
      ))}
    </div>
    <p class="text-center text-stone-400 text-xs mt-8 font-body">
      All puppies include LICENCE_CLAIM_PLACEHOLDER home-bred certificate · Canine vet health certificate · Whelp certificate
    </p>
  </div>
</section>
```

**Puppy photos:** each row's `card_photo` and `gallery` name real files; render `{puppy.card_photo}` rather than a hero placeholder. A 4:5 blur-fill portrait, never head-cropped (`rules/images.md`).

**To mark a puppy as reserved/sold:** set `status` in `data/puppies.json`, then filter: `puppies.filter(p => p.status === 'Available')`. The same field drives schema availability — `InStock` only on an available pup (`rules/puppies.md`).

---

## Deploy checklist after any of these changes

```bash
npm run build          # must exit 0, with the pagefind index
npm run check:all      # the gates
git add <files>
git commit -m "..."
# no push, no deploy: this repo has no remote and no host until project 6
```
