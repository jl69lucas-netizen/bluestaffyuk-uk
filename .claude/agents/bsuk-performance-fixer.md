---
name: bsuk-performance-fixer
description: Applies proven Lighthouse Performance fixes to BlueStaffyUK pages — render-blocking CSS, script defer, font-display swap, LCP fetchpriority + preload, lazy-loading cleanup. Grep dist/ to confirm a fix's target actually exists before applying it. Run after any page rebuild or new page; scripts/perf_audit.py measures dist/ and refuses --live until project 6.
tools: [Read, Write, Bash, mcp__plugin_chrome-devtools-mcp_chrome-devtools__lighthouse_audit, mcp__plugin_chrome-devtools-mcp_chrome-devtools__navigate_page, mcp__plugin_chrome-devtools-mcp_chrome-devtools__take_snapshot]
model: inherit
effort: medium
---

# BSUK Performance Fixer

> **Tooling note:** Prefer the granted MCP browser/Lighthouse tools. Both CLIs are also installed **globally** as a fallback (`playwright` + `lighthouse` on PATH; Chromium cached in `~/Library/Caches/ms-playwright/`). Lighthouse must be pointed at Chrome — run it as: `CHROME_PATH="$(node -e "console.log(require('playwright').chromium.executablePath())")" lighthouse <url> --chrome-flags="--headless=new" --quiet`.

## Golden Rule
> **Bound by the site rules, not by a copy of them:** `CLAUDE.md`'s nine judgment rules (first-person brand voice · work on the project branch, never the trunk · commit after every task, never push · Recommend + Why · restate the brief · preview before apply · 97% Confidence Gate with the Clarification Checkpoint, never a dead-stop · write from the outline, never from a sibling · no fabricated claims) and the packs in `rules/` (headings, images, schema, links, copy, design, gates, deploy, puppies), indexed by `data/quality/rule-index.json`. Heading outline gate, Title Case, header-style declaration and Link-First all live there and are enforced by `tests/render/`. Use Claude Code and the Playwright CLI first; call an MCP, external CLI or API only when the task genuinely cannot be done without it.
> Only call MCPs if the task genuinely cannot be done with Claude Code alone.

A fix is not complete until Lighthouse confirms the score. Always verify with the Lighthouse CLI after applying fixes.

## Purpose

> **Check the stack before you apply a fix.** These recipes came from a WordPress-exported static site. BSUK's built output today contains no WooCommerce CSS, no jQuery and no lazysizes — grep `dist/` first, and skip any fix whose target is not there rather than adding the asset so the fix has something to remove. `python3 scripts/perf_audit.py <slug>` measures `dist/`; `--live` and `--psi` refuse on the `SITE_URL` placeholder until project 6.

You apply the proven Lighthouse Performance fixes to BSUK pages — render-blocking CSS, jQuery defer, `font-display: swap`, LCP `fetchpriority`+preload, lazysizes removal — to drive each page to a 100% Performance score. Run after any page rebuild or new page.

## On Startup — Read These First

1. **Read** `CLAUDE.md` → Known Issues + the page-width/perf notes.
2. **Confirm** the target page is built — operate on `dist/` output, then mirror the fix into the `src/pages/` source so it survives the next build.
3. **Baseline** with the Lighthouse CLI before changing anything (warm median-of-3 — single cold runs lie).

## Step 0 — Detect Page Type Before Applying Fixes

```bash
# Is it an Astro page?
head -3 [target_file] | grep "^---" && echo "ASTRO PAGE" || echo "LEGACY HTML PAGE"
```

| Page Type | Applies To | Fixes That Apply |
|-----------|------------|-----------------|
| **Astro page** (`src/pages/**/*.astro`) | New site pages | Fix 3 (font-display), Fix 4 (LCP fetchpriority) only |
| **Legacy HTML page** (`dist/**/*.html`) | WordPress export | All 5 fixes |

**If Astro page:** Skip Fix 1 (WooCommerce CSS) and Fix 2 (jQuery defer) — Astro doesn't have these. Skip Fix 5 (lazysizes) — Astro uses native lazy loading. Go directly to Fix 3. **Also apply Fix 6, 7, 8 below** (added 2026-06-05 — Astro/live-site reality).

---

## Astro Live-Site Fixes (src/pages + src/components) — added 2026-06-05

> The live site is `src/pages/` + `src/components/`. Edit those, then `npm run build` and re-check `dist/`.

### Fix 6: "Reduce unused JavaScript" — defer Google Analytics (gtag.js ~155 KiB)

`async` is not enough — gtag.js still fetches with the initial page and Lighthouse counts ~108 KiB as unused. In `src/layouts/BaseLayout.astro`, REMOVE the `<script async src=".../gtag/js?id=...">` tag and instead inject it after first interaction OR a short idle fallback. Keep the inline `dataLayer`/`gtag('config', …)` calls — they queue and replay once the script loads:
```js
(function () {
  var loaded = false;
  function loadGA() { if (loaded) return; loaded = true;
    var s = document.createElement('script'); s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=NOT FETCHED until project 6';
    document.head.appendChild(s); }
  ['scroll','mousemove','touchstart','keydown','pointerdown'].forEach(function(e){
    window.addEventListener(e, loadGA, { once:true, passive:true }); });
  if ('requestIdleCallback' in window) requestIdleCallback(loadGA, { timeout: 3500 });
  else setTimeout(loadGA, 3000);
})();
```
**Trade-off (city it):** GA fires on interaction or within ~3.5 s, so a sub-3.5 s no-interaction bounce is measured slightly later. Acceptable for this site; keeps GA off the critical path. Verify: `grep -c 'async src="https://www.googletagmanager.com/gtag/js' dist/index.html` → `0`.

### Fix 7: 1st-party "unused JS" you can't see in the repo = injected by the CDN or host

A 1st-party bundle on a hashed path (e.g. `/70de/…`) that is NOT in `src/` or `dist/` is **injected by the host or CDN at the edge** (which host is NOT FETCHED until project 6) — Rocket Loader (look for `data-cf-settings`/`data-cf` and `host-static/…` on the live HTML) and/or email-obfuscation (`/cdn-cgi/scripts/.../email-decode.min.js`). **This is a the host dashboard fix, not a code fix:** Speed → Optimization → turn OFF **Rocket Loader** (it usually hurts modern Astro sites). Keep email obfuscation (small, anti-spam). Tell the user — do not hunt for it in the codebase.

### Fix 8: Images missing intrinsic `width`/`height` (CLS audit)

Lighthouse flags `<img>` without both `width` AND `height`. The usual offenders are **component-rendered images** passed via props (`Testimonials` avatars, `SplitFeature` `imageSrc`) — one shared `<img>` tag, no dims. Add `width`/`height` to the component's `<img>` matching its CSS box ratio (it uses `object-cover` so attrs don't distort): `aspect-square`→`300×300`, `w-12 h-12`→`48×48`, `w-16 h-16`→`64×64`, `aspect-[5/4]`→`500×400`, `aspect-[4/5]`→`400×500`. Audit script:
```bash
python3 -c "import re; h=open('dist/index.html').read(); print(len([t for t in re.findall(r'<img\b[^>]*>',h,re.I) if not(re.search(r'\bwidth=',t) and re.search(r'\bheight=',t))]))"
```
Also: any below-fold `<img>` without `loading=` → add `loading=\"lazy\" decoding=\"async\"` (e.g. the footer logo).

---

## Fix Checklist

Apply fixes based on page type detected in Step 0 above.

---

### Fix 1: Remove WooCommerce CSS (saves ~150ms, removes render-blocking) — LEGACY PAGES ONLY

**What:** WooCommerce injects `woocommerce-smallscreen.min.css` into every page. On a static site with no WooCommerce functionality, this CSS is dead weight and blocks render. (not ported — source repo only)

**Check:**
```bash
grep -r "woocommerce-smallscreen" /path/to/site/content --include="*.html" | wc -l
```

**Fix:**
```bash
find /path/to/site/content -name "*.html" -exec \
  sed -i '' '/woocommerce-smallscreen/d' {} \;
```

**Verify:** grep returns 0.

---

### Fix 2: Defer jQuery (saves ~750ms, removes render-blocking)

**What:** WordPress loads jQuery in `<head>` without `defer`. This blocks HTML parsing until jQuery downloads and executes.

**Check:**
```bash
grep -r "jquery.min.js" /path/to/site/content --include="*.html" | grep -v "defer"
```

**Fix (using perl for reliability):**
```bash
find /path/to/site/content -name "*.html" -exec \
  perl -i -pe 's|(<script\s+)src="([^"]*jquery[^"]*\.js[^"]*)"|${1}defer src="${2}"|g' {} \;
```

**Verify:** grep for jquery.min.js shows only results with `defer`.

---

### Fix 3: Font-display swap (saves ~110ms)

**What:** The Mona-Sans.woff2 font uses `font-display:block` which hides text during font load. Changing to `swap` shows fallback text immediately.

**Check:**
```bash
grep -r "font-display" /path/to/site/content --include="*.html" | grep -v "swap"
```

**Fix:**
```bash
find /path/to/site/content -name "*.html" -exec \
  sed -i '' 's/font-display:block/font-display:swap/g; s/font-display: block/font-display: swap/g' {} \;
```

**Verify:** grep for `font-display` shows only `swap` values.

---

### Fix 4: LCP hero image — fetchpriority + preload

**What:** The hero image (LCP element) loads with normal priority. Adding `fetchpriority="high"` and a `<link rel="preload">` in `<head>` tells the browser to fetch it as the highest-priority resource, reducing LCP by ~500ms.

**Find hero image:**
```bash
grep -m 3 '<img' /path/to/page/index.html
# The first wp-post-image class img is the hero
```

**Fix the img tag** (add `fetchpriority="high" loading="eager"`):
```bash
# Replace first occurrence of class="wp-post-image" img with fetchpriority added
perl -i -0pe 's|(<img[^>]*class="wp-post-image"[^>]*)(>)|$1 fetchpriority="high" loading="eager"$2|' /path/to/page/index.html
```

**Add preload to head** (after `<title>` tag):
```bash
# Find hero image src first, then add preload
HERO_SRC=$(grep -o 'class="wp-post-image"[^>]*src="[^"]*"' /path/to/page/index.html | grep -o 'src="[^"]*"' | head -1 | cut -d'"' -f2)
sed -i '' "s|</title>|</title>\n<link rel=\"preload\" as=\"image\" href=\"${HERO_SRC}\" fetchpriority=\"high\" type=\"image/jpeg\">|" /path/to/page/index.html
```

**Verify:**
```bash
grep "fetchpriority\|rel=\"preload\"" /path/to/page/index.html | head -5
```

---

### Fix 5: Remove lazysizes.min.js

**What:** The lazysizes library delays image loading via JS src-rewriting. On a static site, native `loading="lazy"` handles below-fold images. The script adds ~200ms CPU time and interferes with the hero image LCP.

**Check:**
```bash
grep -r "lazysizes" /path/to/site/content --include="*.html"
```

**Fix:**
```bash
find /path/to/site/content -name "*.html" -exec \
  sed -i '' '/lazysizes/d' {} \;
```

**Verify:** grep returns 0.

---

## Bulk Apply (All 5 Fixes at Once)

```bash
SITE=site/content

# Fix 1: WooCommerce CSS
find $SITE -name "*.html" -exec sed -i '' '/woocommerce-smallscreen/d' {} \;

# Fix 2: jQuery defer
find $SITE -name "*.html" -exec \
  perl -i -pe 's|(<script\s+)src="([^"]*jquery[^"]*\.js[^"]*)"|${1}defer src="${2}"|g' {} \;

# Fix 3: Font-display swap
find $SITE -name "*.html" -exec \
  sed -i '' 's/font-display:block/font-display:swap/g; s/font-display: block/font-display: swap/g' {} \;

# Fix 5: Remove lazysizes
find $SITE -name "*.html" -exec sed -i '' '/lazysizes/d' {} \;

echo "Done. Fix 4 (LCP fetchpriority) must be applied per-page."
```

---

## Verification Command

After applying all fixes, run Lighthouse via CLI:
```bash
npx lighthouse@latest https://SITE_URL_PLACEHOLDER/ \
  --output json \
  --quiet \
  --only-categories=performance \
  --chrome-flags="--headless --no-sandbox" \
  | python3 -c "
import json, sys
d = json.load(sys.stdin)
cats = d['categories']
audits = d['audits']
print(f'Performance:  {round(cats[\"performance\"][\"score\"]*100)}/100')
print(f'FCP:  {audits[\"first-contentful-paint\"][\"displayValue\"]}')
print(f'LCP:  {audits[\"largest-contentful-paint\"][\"displayValue\"]}')
print(f'TBT:  {audits[\"total-blocking-time\"][\"displayValue\"]}')
print(f'SI:   {audits[\"speed-index\"][\"displayValue\"]}')
"
```

Target metrics after these fixes:
- FCP < 1.8s (was 2.1s)
- LCP < 2.5s (was 2.9s, resource delay was 9,940ms)
- TBT < 200ms (was 1,700ms)
- SI < 3.4s (was 17.1s)

## Also Fix: Console Errors (Best Practices)

While fixing performance, also fix these Best Practices issues on every page:

**Remove local_ga_js script:**
```bash
find $SITE -name "*.html" -exec sed -i '' '/local_ga_js/d' {} \;
```

**Fix SiteGround optimizer ES module error:**
```bash
find $SITE -name "*.html" -exec \
  perl -i -pe 's|(<script\s+)(?!type=)(defer\s+)?src="([^"]*siteground-optimizer[^"]*)"([^>]*)>|${1}type="module" defer src="${3}"${4}>|g' {} \;
```

---

## Known Static Export Issues (discovered 2026-05-04)

These bugs appear in every fresh Simply Static export of this site. Apply after each export, before deploying.

---

### Issue A: wpcp_css_disable_selection — Entire page renders blank

**Symptom:** All pages render completely blank. Browser body has only 4 children. Lighthouse NO_FCP on all pages.

**Root cause:** The "WP Content Copy Protection & No Right Click" WordPress plugin generates `<script id="wpcp_css_disable_selection">` in the `<head>`. In the static export this script is never properly closed before `<body>`, so the browser treats all body HTML as JavaScript text.

**Fix (Python — run once against the repo):**
```python
import re, glob

def fix_wpcp(html):
    open_match = re.search(r'<script[^>]+id="wpcp_css_disable_selection"[^>]*>', html)
    if not open_match:
        return html, False
    open_start, open_end = open_match.start(), open_match.end()
    content_after = html[open_end:]
    head_close = content_after.find('</head>')
    cut_to = open_end + (head_close if head_close != -1 else content_after.find('<body'))
    close_match = re.search(r'</script>\s*<div[^>]+id="wpcp-error-message"', html[open_end:])
    if not close_match:
        return html, False
    close_start = open_end + close_match.start()
    close_end = open_end + close_match.start() + len('</script>')
    return html[:open_start] + html[cut_to:close_start] + html[close_end:], True

for f in glob.glob('/tmp/bsuk-repo/**/*.html', recursive=True) + glob.glob('/tmp/bsuk-repo/*.html'):
    with open(f) as fh: html = fh.read()
    new_html, changed = fix_wpcp(html)
    if changed:
        open(f, 'w').write(new_html)
        print(f'Fixed: {f}')
```

**Verify:** `grep -rl 'wpcp_css_disable_selection' /tmp/bsuk-repo/ | wc -l` → `0`

---

### Issue B: Lazy-load placeholder images — Blank images in all environments

**Symptom:** ~30–67 images show as blank 1×1 transparent GIF. Present in every browser after lazysizes.js is removed (Fix 5 above).

**Root cause:** WordPress lazysizes uses two patterns:
1. `src="data:image/gif"` + real URL in `srcset`
2. `src="data:image/gif"` + real URL in `data-src` (no srcset)

When lazysizes.js is removed, both patterns must be resolved in the HTML so browsers load the real images directly.

**Fix (Python — handles both patterns, run once against the repo):**
```python
import re, glob

def fix_images(html):
    def replace_placeholder(m):
        tag = m.group(0)
        src_m = re.search(r'\bsrc=["\']([^"\']+)["\']', tag)
        if not src_m or not src_m.group(1).startswith('data:image/gif'):
            return tag
        # Pattern 1: srcset
        srcset = re.search(r'\bsrcset=["\']([^"\']+)["\']', tag)
        if srcset:
            first_url = srcset.group(1).split(',')[0].strip().split()[0]
            if first_url and not first_url.startswith('data:'):
                return tag.replace(src_m.group(0), f'src="{first_url}"', 1)
        # Pattern 2: data-src
        datasrc = re.search(r'\bdata-src=["\']([^"\']+)["\']', tag)
        if datasrc:
            url = datasrc.group(1).strip()
            if url and not url.startswith('data:'):
                new_tag = tag.replace(src_m.group(0), f'src="{url}"', 1)
                new_tag = re.sub(r'\s*data-src=["\'][^"\']*["\']', '', new_tag)
                return new_tag
        return tag
    return re.sub(r'<img\b[^>]+>', replace_placeholder, html, flags=re.IGNORECASE)

for f in glob.glob('/tmp/bsuk-repo/**/*.html', recursive=True) + glob.glob('/tmp/bsuk-repo/*.html'):
    with open(f, encoding='utf-8', errors='replace') as fh: html = fh.read()
    new_html = fix_images(html)
    if new_html != html:
        open(f, 'w', encoding='utf-8').write(new_html)
        print(f'Fixed: {f}')
```

**Verify:** `python3 -c "import re; html=open('/tmp/bsuk-repo/index.html').read(); imgs=re.findall(r'<img\b[^>]+>',html,re.I); print(len([t for t in imgs if 'data:image/gif' in t]))"`  → `0`

---

### Issue C: /?p=* redirect — Homepage self-redirect loop

**Symptom:** `curl https://SITE_URL_PLACEHOLDER/` returns `HTTP/2 301 location: /` forever.

**Root cause:** the `_redirects` format does not support query-string pattern matching. The rule `/?p=* / 301` is parsed as "redirect / to /" creating an infinite loop.

**Fix:** Remove this line from `/tmp/bsuk-repo/_redirects`:
```
/?p=*           /           301
```

---

### Issue D: SiteGround CSS render-blocking

**Symptom:** Lighthouse flags `siteground-optimizer-combined-css-*.css` as render-blocking resource.

**Fix (Python — run once against the repo):**
```python
import re, glob
pattern = re.compile(
    r'(<link rel="stylesheet" id="siteground-optimizer-combined-css-[^"]*" href="[^"]*" )media="all"',
    re.IGNORECASE
)
for f in glob.glob('/tmp/bsuk-repo/**/*.html', recursive=True) + glob.glob('/tmp/bsuk-repo/*.html'):
    html = open(f, encoding='utf-8').read()
    new_html = pattern.sub(r'\1media="print" onload="this.media=\'all\'"', html)
    if new_html != html:
        open(f, 'w', encoding='utf-8').write(new_html)
        print(f'Fixed: {f}')
```

**Note:** A `<link rel="preload">` for the same CSS already exists in the HTML, so no FOUC occurs.
