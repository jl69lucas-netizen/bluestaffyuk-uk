#!/usr/bin/env node
// node scripts/city_side_by_side.mjs [--city london] [--slug blue-staffy-puppies-london]
//
// The side-by-side the user confirms before a city's component pass is done (spec §3.5, "The
// user sees each built component beside its canvas version and confirms the match"). For each of
// the city's fifteen picks it shoots, at 375, 768 and 1280:
//   - the CANVAS frame the user picked (docs/artifacts/canvas/<city>-frames/<component>/<v>.html,
//     emitted by `python3 scripts/build_component_canvas.py --emit-frames …`), and
//   - the BUILT component ON THE REAL CITY PAGE (dist/uk-locations/<slug>/), found by its root
//     class or data hook, so an in-body component is shot in the column beside the dial.
// and writes docs/artifacts/bsuk-<city>-side-by-side.html (committed, the Artifact's source; no
// document tags, the Artifact page contract) with the shots in
// docs/artifacts/canvas/side-by-side/<city>/ (git-ignored) and the Artifact publish's `files` map
// beside them (files.json). Build and emit the frames first. Serves dist/ and the repo root itself
// on RENDER_SBS_PORT and RENDER_SBS_PORT+1 (default 4361).
//
// A component that is not displayed at a width by design (the dial below 1024px) gets a note in
// its card instead of a shot. Any painted image that never loads fails the run (exit 1), after
// the page is written, so the failure can be read on the page too.
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { chromium } from '@playwright/test';

const ROOT = resolve(new URL('..', import.meta.url).pathname);
const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`);
  return i > 0 ? process.argv[i + 1] : fallback;
};
const CITY = arg('city', 'london');
const SLUG = arg('slug', 'blue-staffy-puppies-london');
const PORT = Number(process.env.RENDER_SBS_PORT ?? 4361);
const WIDTHS = [375, 768, 1280];
const IMG_WAIT_MS = 5000;
const picks = JSON.parse(readFileSync(resolve(ROOT, `data/design/city-picks/${SLUG}.json`), 'utf8')).picks;
const rows = JSON.parse(readFileSync(resolve(ROOT, 'data/design/components.json'), 'utf8'))
  .filter((r) => r.project === 5);
// scripts/city_components.py KIT_ID, in city-page order: the same order the rows are in.
const order = Object.keys(picks);
if (rows.length !== order.length) {
  console.error(`components.json has ${rows.length} city rows for ${order.length} picks`);
  process.exit(1);
}

// Each built component's root on the city page, keyed by its component FILE (the rows carry the
// current file names; a renamed file fails loudly here rather than shooting the wrong node).
const ROOT_SELECTOR = {
  'CityHeroFilmstrip.astro': '.city-hero-filmstrip',
  'CityPriceScale.astro': '.city-scale',
  'CityTrustLedger.astro': '.city-trust',
  'CityContentsPhotoIndex.astro': '.city-contents-photo-index',
  'CityDialPhotoMarker.astro': '[data-city-dial-photo-marker]',
  'CityJumpStepper.astro': '[data-city-jump-stepper]',
  'CityTakeawaysLedger.astro': '.city-takeaways-ledger',
  'CityPuppySheet.astro': '.city-sheet',
  'CityRoster.astro': '.city-roster',
  'CityVideoPanel.astro': '.city-video',
  'CityChapters.astro': '.city-chapters',
  'CityLetter.astro': '.city-letter',
  'CityFaqLedger.astro': '.city-faq',
  'CityNewsletterNotice.astro': '.city-newsletter-notice',
  'CityContactLineup.astro': '.city-contact',
};
// The picks whose canvas frame wraps them in stand-in page sections: their own element.
const CANVAS_SELECTOR = {
  'jump-links': '[data-jump-strip]',
  'desktop-dial': '[data-dial]',
  'contents-list': '[data-component] > .panel',
};
// Why a component is not displayed at a width, for its card.
const HIDDEN_WHY = {
  'CityDialPhotoMarker.astro': 'The dial is desktop navigation: it shows from 1024px, and the jump band stands in for it on phones and tablets.',
  'CityJumpStepper.astro': 'The jump band is phone and tablet navigation: it shows below 1024px, and the dial beside the body takes its place from 1024px.',
  'CityContentsPhotoIndex.astro': 'The contents list shows below 1024px only: from 1024px the dial beside the body is the page\'s contents, as on the other pages (your ruling, answer board q05, 2026-09-29).',
};
// The sticky furniture is shot as the element itself; every section is clipped from the page.
const DIAL_FILE = 'CityDialPhotoMarker.astro';
const STICKY = new Set(['CityJumpStepper.astro', DIAL_FILE]);
// Chrome: shot as the element itself, with nothing hidden (the header sits outside its box).
const CHROME = new Set(['CityJumpStepper.astro']);
for (const r of rows) {
  if (!ROOT_SELECTOR[r.file]) {
    console.error(`no root selector for ${r.file} (${r.id}): add it to ROOT_SELECTOR`);
    process.exit(1);
  }
}

// What differs on purpose, per pick component. `column` is added at run time for any component
// the 1280 shot finds narrower than the page (it sits in the column beside the dial).
const TYPE_FIT = 'The type-fit scale you asked for on 2026-09-28: headings capped at 22 / 25 / 28px and reading paragraphs held to 65ch.';
const BOLD = 'Bold, brand-coloured headings restored (Code fact 5): the site base inherits weight and colour, so the kit gives city headings the canvas weight back.';
const NO_GUARANTEE = 'No guarantee line: the canvas named a two-year health guarantee, and the site states none while data/settings.json has guarantee_days: null (working rule 9).';
const PHOTO = (who) => `A different served photo where the canvas repeated Maggie's (Code fact 4): one served photo appears once per page, so this one carries ${who}.`;
const DELIBERATE = {
  hero: [BOLD, TYPE_FIT],
  'counter-strip': ['From 640 to 839px the price scale\'s count sits above the line, not on it, so the figures keep their own width.'],
  'trust-strip': [PHOTO("Jones's portrait"), NO_GUARANTEE, BOLD, TYPE_FIT],
  'contents-list': [BOLD],
  'desktop-dial': [],
  'jump-links': [],
  'key-takeaways': [PHOTO('Jones seated'), NO_GUARANTEE, BOLD, TYPE_FIT],
  'puppy-cards': [BOLD, TYPE_FIT],
  tables: [BOLD, TYPE_FIT],
  video: [BOLD, TYPE_FIT],
  'image-text': [PHOTO('Byrd for chapter one'), BOLD, TYPE_FIT],
  reviews: ['The review is split into three paragraphs rather than one block.', BOLD, TYPE_FIT],
  'faq-blocks': [PHOTO('the London owner photo in the rail'), 'The canvas frame stacks all three FAQ blocks; the page places them apart (buying, checking us, Staffy life), each under the section it answers, so the built shot is the first block, the one with the photo rail.', NO_GUARANTEE, BOLD, TYPE_FIT],
  newsletter: [BOLD, TYPE_FIT],
  'contact-form': [BOLD, TYPE_FIT],
};
const COLUMN = 'Laid out for the column beside the 272px dial (Code fact 6): the canvas painted it full width, so from 1024px the built copy is narrower and lays out for its own box.';

const FRAMES = resolve(ROOT, `docs/artifacts/canvas/${CITY}-frames`);
if (!existsSync(resolve(FRAMES, 'index.json'))) {
  console.error(`no frames at ${FRAMES}: python3 scripts/build_component_canvas.py --emit-frames docs/artifacts/canvas/${CITY}-frames`);
  process.exit(2);
}
const PAGE_PATH = `uk-locations/${SLUG}/`;
if (!existsSync(resolve(ROOT, 'dist', PAGE_PATH, 'index.html'))) {
  console.error(`no dist/${PAGE_PATH} — run npm run -s build first`);
  process.exit(2);
}
const OUT = resolve(ROOT, `docs/artifacts/canvas/side-by-side/${CITY}`);
mkdirSync(OUT, { recursive: true });

// Scroll every visible img in `root` into view and wait until it is complete, capped per image.
// Returns the srcs that never loaded. `root` is a CSS selector; `nth` picks the match.
async function settleImages(page, selector) {
  const count = await page.evaluate((sel) => {
    const root = document.querySelector(sel);
    return root ? root.querySelectorAll('img').length : 0;
  }, selector);
  const failed = [];
  for (let i = 0; i < count; i++) {
    const res = await page.evaluate(async ({ sel, i, cap }) => {
      const img = document.querySelector(sel).querySelectorAll('img')[i];
      if (!img.getClientRects().length) return { skip: true };
      img.scrollIntoView({ block: 'center' });
      const t0 = Date.now();
      while (!(img.complete && img.naturalWidth > 0) && Date.now() - t0 < cap) {
        await new Promise((r) => setTimeout(r, 50));
      }
      if (img.decode) { try { await img.decode(); } catch { /* reported below */ } }
      return { ok: img.complete && img.naturalWidth > 0, src: img.currentSrc || img.src };
    }, { sel: selector, i, cap: IMG_WAIT_MS });
    if (!res.skip && !res.ok) failed.push(res.src);
  }
  return failed;
}

const serve = (cwd, port) => spawn('python3', ['-m', 'http.server', String(port), '--bind', '127.0.0.1'], { cwd, stdio: 'ignore' });
const servers = [serve(resolve(ROOT, 'dist'), PORT), serve(ROOT, PORT + 1)];
await new Promise((r) => setTimeout(r, 900));
const browser = await chromium.launch();
const shots = [];
const broken = [];
const columnNote = new Set();
let dialRow = null;
try {
  for (const [i, component] of order.entries()) {
    const key = picks[component];
    const variant = key.split('/')[2];
    const row = rows[i];
    const sel = ROOT_SELECTOR[row.file];
    for (const width of WIDTHS) {
      const shot = { component, key, row, width, canvasFile: null, builtFile: null, note: null };
      const height = 900;
      const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });

      // The canvas frame.
      await page.goto(`http://127.0.0.1:${PORT + 1}/docs/artifacts/canvas/${CITY}-frames/${component}/${variant}.html`, { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready);
      for (const src of await settleImages(page, '[data-component]')) broken.push(`${component} canvas @${width}: ${src}`);
      await page.evaluate(() => window.scrollTo(0, 0));
      shot.canvasFile = `${component}-${width}-canvas.jpg`;
      // A chrome pick's frame wraps the band or dial in stand-in sections; shoot the chrome itself
      // where the frame displays it at this width, else the whole frame.
      let canvasEl = page.locator('[data-component]').first();
      const own = CANVAS_SELECTOR[component] ? page.locator(CANVAS_SELECTOR[component]).first() : null;
      if (own && (await own.count()) && (await own.isVisible())) canvasEl = own;
      if (own && canvasEl !== own) {
        shot.canvasFile = null;
        shot.canvasNote = `The canvas frame does not show it at ${width}px either, only its stand-in sections.`;
      } else {
        await canvasEl.screenshot({ path: resolve(OUT, shot.canvasFile), type: 'jpeg', quality: 78 });
      }

      // The built component on the real page.
      await page.goto(`http://127.0.0.1:${PORT}/${PAGE_PATH}`, { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready);
      const el = page.locator(sel).first();
      if ((await page.locator(sel).count()) === 0) {
        console.error(`${component}: ${sel} matched nothing on /${PAGE_PATH}`);
        process.exitCode = 1;
        shot.note = `Not found on the page (${sel}).`;
      } else if (!(await el.isVisible())) {
        shot.note = `Not shown at ${width}px by design. ${HIDDEN_WHY[row.file] ?? `${row.file.replace('.astro', '')} is not displayed at this width.`}`;
      } else {
        if (!CHROME.has(row.file)) {
          // The site header and the jump band are sticky; neither may sit over another section.
          await page.addStyleTag({ content: '.kit-hdr, [data-city-jump-stepper] { visibility: hidden !important; }' });
        }
        for (const src of await settleImages(page, sel)) broken.push(`${component} built @${width}: ${src}`);
        if (CHROME.has(row.file)) await page.evaluate(() => window.scrollTo(0, 0));
        else await el.scrollIntoViewIfNeeded();
        if (row.file === DIAL_FILE) {
          // The dial follows the reader. Scroll just far enough that the whole dial is on screen,
          // let the scroll spy settle, and read the row it marks; the shot then checks that row's
          // section is the one in the spy's reading band (40-45% down), so the marked row is
          // always the section being read.
          dialRow = await page.evaluate(async (s) => {
            const dial = document.querySelector(s);
            const r = dial.getBoundingClientRect();
            window.scrollTo(0, Math.max(0, r.bottom + window.scrollY - window.innerHeight + 16));
            let last = null;
            let same = 0;
            const t0 = Date.now();
            while (same < 6 && Date.now() - t0 < 3000) {
              await new Promise((res) => setTimeout(res, 50));
              const cur = dial.querySelector('[aria-current]');
              const id = cur ? cur.getAttribute('href') : null;
              same = id && id === last ? same + 1 : 0;
              last = id;
            }
            const cur = dial.querySelector('[aria-current]');
            if (!cur) return null;
            const t = document.getElementById(cur.getAttribute('href').slice(1)).getBoundingClientRect();
            const band = window.innerHeight * 0.42;
            cur.dataset.sbsRow = '1';
            return t.top <= band && t.bottom >= band ? cur.textContent.trim() : `MISMATCH:${cur.textContent.trim()}`;
          }, sel);
          if (!dialRow || dialRow.startsWith('MISMATCH')) {
            console.error(`${component} @${width}: the dial's marked row is not the section being read (${dialRow})`);
            process.exitCode = 1;
          }
        }
        await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
        if (width === 1280) {
          const w = await el.evaluate((n) => n.getBoundingClientRect().width);
          if (w < width - 200) columnNote.add(component);
        }
        shot.builtFile = `${component}-${width}-built.jpg`;
        if (row.file === DIAL_FILE) {
          // Clipped from the viewport where it sticks: an element shot scrolls it into view, which
          // moves the reader and so the dial's current row.
          const b = await el.evaluate((n) => { const r = n.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; });
          if (b.y < 0 || b.y + b.h > height) { console.error(`${component} @${width}: the dial does not fit the viewport`); process.exitCode = 1; }
          const x = Math.ceil(b.x);
          const y = Math.max(0, Math.ceil(b.y));
          await page.screenshot({ path: resolve(OUT, shot.builtFile), type: 'jpeg', quality: 78, clip: { x, y, width: Math.floor(b.x + b.w) - x, height: Math.min(height, Math.floor(b.y + b.h)) - y } });
          const still = await el.evaluate((n) => n.querySelector('[data-sbs-row]').hasAttribute('aria-current'));
          if (!still) { console.error(`${component} @${width}: the dial's row "${dialRow}" was not current when shot`); process.exitCode = 1; }
        } else if (STICKY.has(row.file)) {
          await el.screenshot({ path: resolve(OUT, shot.builtFile), type: 'jpeg', quality: 78 });
        } else {
          // The section's own box, rounded INWARD: an element shot rounds a fractional edge out and
          // picks up a 1px line of the next section.
          const b = await el.evaluate((n) => {
            const r = n.getBoundingClientRect();
            return { x: r.left + window.scrollX, y: r.top + window.scrollY, w: r.width, h: r.height };
          });
          const x = Math.ceil(b.x);
          const y = Math.ceil(b.y);
          const clip = { x, y, width: Math.floor(b.x + b.w) - x, height: Math.floor(b.y + b.h) - y };
          await page.screenshot({ path: resolve(OUT, shot.builtFile), type: 'jpeg', quality: 78, fullPage: true, clip });
        }
      }
      await page.close();
      shots.push(shot);
      console.log(`${component} (${key} -> ${row.id}) @ ${width}px${shot.note ? ` — ${shot.note}` : ''}`);
    }
  }
} finally {
  await browser.close();
  servers.forEach((s) => s.kill());
}

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const title = CITY.charAt(0).toUpperCase() + CITY.slice(1);
const cards = order.map((component, i) => {
  const row = rows[i];
  const notes = [...DELIBERATE[component] ?? []];
  if (columnNote.has(component)) notes.push(COLUMN);
  if (component === 'desktop-dial' && dialRow) {
    notes.push(`The dial follows the reader: its marked row is the section being read. The canvas marked its first row; the built dial is shot where the whole dial is on screen, with the reader in "${dialRow}", so that row is marked.`);
  }
  const mine = shots.filter((s) => s.component === component);
  const pairs = mine.map((s) => {
    const built = s.builtFile
      ? `<img src="side-by-side/${s.builtFile}" alt="${esc(row.title ?? component)} as built on the ${title} page at ${s.width}px" loading="lazy">`
      : `<p class="absent">${esc(s.note)}</p>`;
    return `
      <figure class="pair w${s.width}">
        <figcaption>${s.width}px</figcaption>
        <div class="two">
          <div><p class="lab">Canvas (your pick)</p>${s.canvasFile
            ? `<img src="side-by-side/${s.canvasFile}" alt="${esc(component)} as picked on the canvas at ${s.width}px" loading="lazy">`
            : `<p class="absent">${esc(s.canvasNote)}</p>`}</div>
          <div><p class="lab">Built on the ${title} page</p>${built}</div>
        </div>
      </figure>`;
  }).join('');
  const differs = notes.length
    ? `<div class="differs"><p class="dh">What differs on purpose</p><ul>${notes.map((n) => `<li>${esc(n)}</li>`).join('')}</ul></div>`
    : '';
  return `
    <section class="card" id="${esc(component)}">
      <h2><span class="n">${String(i + 1).padStart(2, '0')}</span> ${esc(row.title ?? component)}</h2>
      <p class="key"><code>${esc(picks[component])}</code> → <code>src/components/kit/${esc(row.file)}</code></p>
      ${differs}${pairs}
    </section>`;
}).join('');

const html = `<title>${title} Side by Side</title>
<style>
:root{--bg:#F4F1EA;--card:#FAF8F3;--ink:#1B2430;--muted:#46566B;--rule:#DAD6CC;--accent:#1F3A52;--brass:#A8861C;--band:#1F3A52;--band-ink:#F4F1EA;--note:#EFE3B4}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#14202B;--card:#1B2A38;--ink:#EEF1F4;--muted:#B6C2CC;--rule:#2C3A47;--accent:#8FA3B8;--brass:#C9A227;--band:#0E1720;--band-ink:#E4EAF1;--note:#2A2A1C}}
:root[data-theme="dark"]{--bg:#14202B;--card:#1B2A38;--ink:#EEF1F4;--muted:#B6C2CC;--rule:#2C3A47;--accent:#8FA3B8;--brass:#C9A227;--band:#0E1720;--band-ink:#E4EAF1;--note:#2A2A1C}
*{box-sizing:border-box}
html,body{overflow-x:hidden}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 "Source Sans 3",system-ui,-apple-system,"Segoe UI",sans-serif}
.top{background:var(--band);color:var(--band-ink);border-bottom:3px solid var(--brass)}
.top .in,main{max-width:1320px;margin:0 auto;padding-left:16px;padding-right:16px}
.top .in{padding-top:24px;padding-bottom:20px}
h1{margin:0 0 8px;font:700 clamp(24px,5vw,32px)/1.2 Fraunces,Georgia,serif}
.intro{margin:0;max-width:70ch;opacity:.9}
main{padding-top:24px;padding-bottom:64px}
.card{background:var(--card);border:1px solid var(--rule);border-radius:12px;padding:16px;margin:0 0 24px;min-width:0}
h2{margin:0 0 4px;font:700 20px/1.3 Fraunces,Georgia,serif;color:var(--accent)}
.n{color:var(--brass);margin-right:6px}
.key{margin:0 0 12px;color:var(--muted);font-size:14px;overflow-wrap:anywhere}
code{font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace}
.differs{background:var(--note);border-left:3px solid var(--brass);border-radius:6px;padding:10px 12px;margin:0 0 16px;font-size:14px}
.dh{margin:0 0 4px;font-weight:700}
.differs ul{margin:0;padding-left:18px}.differs li{max-width:80ch}
.pair{margin:0 0 20px;padding-top:12px;border-top:1px solid var(--rule)}
.pair figcaption{font-weight:700;margin:0 0 8px;color:var(--accent)}
.two{display:grid;gap:12px;grid-template-columns:minmax(0,1fr)}
.two>div{min-width:0}
.lab{margin:0 0 4px;font-size:13px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
.two img{display:block;max-width:100%;height:auto;border:1px solid var(--rule);border-radius:6px;background:#fff}
.absent{margin:0;padding:16px;border:1px dashed var(--rule);border-radius:6px;color:var(--muted);font-size:14px}
@media (min-width:900px){.w375 .two{grid-template-columns:repeat(2,minmax(0,375px))}.w768 .two,.w1280 .two{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700&family=Source+Sans+3:wght@400;600;700&display=swap">
<header class="top"><div class="in">
<h1>${title} Components, Side by Side</h1>
<p class="intro">Each of the fifteen components you picked on the ${title} component canvas, beside the component as built on the real ${title} page, at phone (375px), tablet (768px) and desktop (1280px) width. The built copies carry the page's placeholder copy and the site's data (puppies, prices, served photos with their served alt text). Each card says what differs on purpose. Tell us which ones match, and what differs on any that do not.</p>
</div></header>
<main>
${cards}
</main>
`;
writeFileSync(resolve(ROOT, `docs/artifacts/bsuk-${CITY}-side-by-side.html`), html);
const files = Object.fromEntries(shots.flatMap((s) => [s.canvasFile, s.builtFile].filter(Boolean).map((f) => [
  `side-by-side/${f}`, `docs/artifacts/canvas/side-by-side/${CITY}/${f}`,
])));
writeFileSync(resolve(OUT, 'files.json'), JSON.stringify(files, null, 1) + '\n');
const bytes = Object.values(files).reduce((n, p) => n + statSync(resolve(ROOT, p)).size, 0);
const built = shots.filter((s) => s.builtFile).length;
console.log(`${shots.length} pairs (${built} built shots, ${shots.length - built} noted) -> docs/artifacts/bsuk-${CITY}-side-by-side.html; ${Object.keys(files).length} images, ${(bytes / 1048576).toFixed(2)} MB; files map ${resolve(OUT, 'files.json')}`);
if (broken.length) {
  console.error(`${broken.length} image(s) never loaded:\n  ${broken.join('\n  ')}`);
  process.exitCode = 1;
}
