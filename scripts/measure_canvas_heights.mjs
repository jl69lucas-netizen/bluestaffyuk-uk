// Measures each [data-component] section of dist/kit-preview/ at its board width, so the
// frames in canvas.json fit. Run after `npm run build`; writes data/design/canvas-heights.json.
//
// Two more passes, at 375 and 768 (spec §11 amendment 3d), so the phone and tablet
// renderings are judged rather than assumed. Their keys carry a suffix: `hero-m375`,
// `hero-t768`. Thirteen components x three widths is the canvas's 39 boards; there is no
// variant letter any more, because Task 19 pruned the kit to the picks.
import { chromium } from '@playwright/test';
import { readFileSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { join, extname } from 'node:path';
const dist = new URL('../dist/', import.meta.url).pathname;
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
for (const width of [640, 1280]) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.goto(PREVIEW, { waitUntil: 'networkidle' });
  const rows = await page.$$eval(`section[data-width="${width}"]`, measure);
  for (const [k, h] of rows) out[k] = Math.max(h, 80);
  await page.close();
}
// Every component again, at phone and tablet width.
for (const [width, suffix] of [[375, 'm375'], [768, 't768']]) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.goto(PREVIEW, { waitUntil: 'networkidle' });
  const rows = await page.$$eval('section[data-component][data-width]', measure);
  for (const [k, h] of rows) out[`${k}-${suffix}`] = Math.max(h, 80);
  await page.close();
}
// RULE 10, measured rather than asserted. A board height alone cannot tell a hero that
// FITS in 390-450px from one that is CLIPPED to it: `max-height` plus a hidden overflow
// produces the same number either way. So each hero is re-measured at the three desktop
// widths where the clamp is live, and these facts are recorded per width: the scroll
// overflow of `.inner`, of the section and of the LEDE (0 when nothing is cut off), how far
// the CTA row sits below the section's own bottom edge (<= 0 when it is inside), and the
// section height (which rule 10 holds between 390 and 450).
const heroOverflow = {};
for (const width of [1024, 1100, 1280]) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.goto(PREVIEW, { waitUntil: 'networkidle' });
  const rows = await page.$$eval('.kit-hero', (els) => els.map((el) => {
    // A board IS its component now — Task 19 pruned the kit to the picks, so there is no
    // variant letter left to suffix the key with.
    const board = el.closest('section[data-component]');
    const key = board ? board.dataset.component : 'hero';
    const inner = el.querySelector('.inner');
    const ctas = el.querySelector('.ctas');
    const lede = el.querySelector('.lede');
    const box = el.getBoundingClientRect();
    return [key, {
      height: Math.round(box.height),
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
out.hero_overflow = heroOverflow;

await browser.close(); srv.close();
writeFileSync(new URL('../data/design/canvas-heights.json', import.meta.url), JSON.stringify(out, null, 1));
console.log(`measured ${Object.keys(out).length - 1} sections + hero overflow at 1024/1100/1280`);
