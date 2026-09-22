// Measures each [data-component] section of dist/kit-preview/ at its board width, so the
// frames in canvas.json fit. Run after `npm run build`; writes data/design/canvas-heights.json.
//
// Two more passes, at 375 and 768 (spec §11 amendment 3d), so the phone and tablet
// renderings are judged rather than assumed. Their keys carry a suffix: `hero-m375`,
// `hero-t768`. Thirteen components x three widths is the canvas's 39 boards; there is no
// variant letter any more, because Task 19 pruned the kit to the picks.
//
// THE SUFFIXED KEYS ARE PROJECT 3 ONLY. Rows 2 and 3 of the canvas are the phone and tablet
// passes over its boards, and the canvas is the artifact the five-option picks were made
// from — it cannot grow a component retrospectively, so `page-dial-m375` would be a
// measurement with no board to carry it. The UNSUFFIXED key is not a canvas key alone:
// scripts/build_design_system.py reads it for every component's `@dsCard height=`, and
// spec §3 gives the Design System artifact a preview per component including project 4's
// two. So the first pass measures every row and only the responsive passes filter.
//
// AND THE PROJECT 4 PAIR IS VIEWPORT-CONDITIONAL. PageDial is `display: none` below 1024px
// and SectionSheet is `display: none` at 1024 and above, so neither has a height at its own
// 640px board width — measured there they are the 80px floor, which would give the Design
// System a squashed card for a component that is 336px tall where it actually renders. For
// those rows only, the unsuffixed key takes the LARGEST measurement across all four widths:
// the width at which the component exists. (SectionSheet legitimately stays near the floor:
// its bar is `position: fixed` and its sheet is closed, so it contributes almost no height
// to the flow at any width. That is the truth about it, not a measurement failure.)
//
// `networkidle` is not enough to settle a height. It waits for the network, not for the
// two Google-hosted families to be APPLIED, so a section measured before the swap is sized
// in the fallback face and a section measured after is not — which is how five committed
// board heights drifted between two runs of this script with no source change. Every pass
// therefore awaits `document.fonts.ready` and only then measures.
import { chromium } from '@playwright/test';
import { readFileSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { join, extname } from 'node:path';
const dist = new URL('../dist/', import.meta.url).pathname;
const PROJECT_3 = new Set(
  JSON.parse(readFileSync(new URL('../data/design/components.json', import.meta.url), 'utf8'))
    .filter((r) => r.project === 3)
    .map((r) => r.id),
);
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml' };
const srv = createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html';
  try { const b = readFileSync(join(dist, p)); res.writeHead(200, { 'content-type': types[extname(p)] ?? 'application/octet-stream' }); res.end(b); }
  catch { res.writeHead(404); res.end(); }
}).listen(0);
const port = srv.address().port;
const browser = await chromium.launch();
const out = {};
const PREVIEW = `http://127.0.0.1:${port}/kit-preview/`;
// The section height, less the preview's own caption, rounded up to the nearest 8 with a
// 16px artboard frame added — the same arithmetic the board's `h` carries.
const measure = (els) => els.map((e) => {
  const h3 = e.querySelector('h3'); const cap = h3 ? h3.getBoundingClientRect().height : 0;
  return [e.dataset.component, Math.ceil((e.getBoundingClientRect().height - cap) / 8) * 8 + 16];
});
// Every measurement of a project 4 row, at every width, so the largest can be taken below.
const conditional = {};
for (const width of [640, 1280]) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.goto(PREVIEW, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const rows = await page.$$eval(`section[data-width="${width}"]`, measure);
  for (const [k, h] of rows) out[k] = Math.max(h, 80);
  const all = await page.$$eval('section[data-component][data-width]', measure);
  for (const [k, h] of all) if (!PROJECT_3.has(k)) conditional[k] = Math.max(conditional[k] ?? 0, h, 80);
  await page.close();
}
// Every component again, at phone and tablet width.
for (const [width, suffix] of [[375, 'm375'], [768, 't768']]) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.goto(PREVIEW, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const rows = await page.$$eval('section[data-component][data-width]', measure);
  for (const [k, h] of rows) {
    if (PROJECT_3.has(k)) out[`${k}-${suffix}`] = Math.max(h, 80);
    else conditional[k] = Math.max(conditional[k] ?? 0, h, 80);
  }
  await page.close();
}
// RULE 10, measured rather than asserted. A board height alone cannot tell a hero that
// FITS in 390-450px from one that is CLIPPED to it: `max-height` plus a hidden overflow
// produces the same number either way. So each hero is re-measured at the three desktop
// widths where the clamp is live, and these facts are recorded per width: the scroll
// overflow of `.inner`, of the section and of the LEDE (0 when nothing is cut off), how far
// the CTA row sits below the section's own bottom edge (<= 0 when it is inside), and the
// section height (which rule 10 holds between 390 and 450).
//
// THE BAND IS A 1280 MEASURE; THE OVERLAP IS NOT (spec §9 amendment 10.4 sub-note, breeder
// 2026-09-21). Below 1280 the clamp is released and the band grows to what a verbatim H1 and
// its lede need, so `height` is only compared against 390-450 at 1280 — the width rule 10 is
// written for. What must hold at EVERY width is that the hero does not run into the section
// under it, and that had never been measured here at all: the three overflow figures are all
// taken INSIDE the hero, so content spilling out of a released box was invisible to every one
// of them. `next_overlap` is the deepest painted descendant against the next board's top
// edge, and `content_below` is the same bottom against the hero's own.
const heroOverflow = {};
for (const width of [1024, 1100, 1280]) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.goto(PREVIEW, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const rows = await page.$$eval('.kit-hero', (els) => els.map((el) => {
    // A board IS its component now — Task 19 pruned the kit to the picks, so there is no
    // variant letter left to suffix the key with.
    const board = el.closest('section[data-component]');
    const key = board ? board.dataset.component : 'hero';
    const inner = el.querySelector('.inner');
    const ctas = el.querySelector('.ctas');
    const lede = el.querySelector('.lede');
    const box = el.getBoundingClientRect();
    // The deepest edge anything in the hero actually paints to. Out-of-flow boxes are
    // skipped: a scrim or a decorative rule is positioned against the band on purpose and
    // says nothing about whether the copy fits in it.
    let deepest = box.bottom;
    for (const d of el.querySelectorAll('*')) {
      const cs = getComputedStyle(d);
      if (cs.position === 'absolute' || cs.position === 'fixed' || cs.display === 'none') continue;
      const r = d.getBoundingClientRect();
      if (r.height) deepest = Math.max(deepest, r.bottom);
    }
    const nxt = board ? board.nextElementSibling : el.nextElementSibling;
    return [key, {
      height: Math.round(box.height),
      content_below: Math.round(deepest - box.bottom),
      next_overlap: nxt ? Math.round(deepest - nxt.getBoundingClientRect().top) : null,
      overflow: inner ? inner.scrollHeight - inner.clientHeight : 0,
      section_overflow: el.scrollHeight - el.clientHeight,
      // The lede is the one element rule 10 deliberately CLAMPS, and a clamp hides its own
      // overflow: a third line is not pushed past the ceiling where `overflow` or
      // `ctas_below` would catch it, it is simply not painted. So the lede is measured on
      // its own, and two lines that do not fit fail as loudly as a CTA row that does not.
      lede_overflow: lede ? lede.scrollHeight - lede.clientHeight : 0,
      ctas_below: ctas ? Math.round(ctas.getBoundingClientRect().bottom - box.bottom) : null,
    }];
  }));
  for (const [k, m] of rows) (heroOverflow[k] ??= {})[String(width)] = m;
  await page.close();
}
for (const [k, h] of Object.entries(conditional)) out[k] = h;
out.hero_overflow = heroOverflow;

await browser.close(); srv.close();
writeFileSync(new URL('../data/design/canvas-heights.json', import.meta.url), JSON.stringify(out, null, 1));
console.log(`measured ${Object.keys(out).length - 1} sections + hero overflow at 1024/1100/1280`);
