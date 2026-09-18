// Measures each [data-component][data-variant] section's rendered height at its board
// width, so canvas.json frames fit. Run after `npm run build`; writes data/design/canvas-heights.json.
//
// Two more passes, at 375 and 768 (spec §11 amendment 3d): the PICKED variants get mobile
// and tablet artboards so those renderings are judged rather than assumed. Only the picks
// are measured there — measuring all 65 twice more would put 130 boards on the canvas
// nobody asked to see. Their keys carry a suffix: `hero-c-m375`, `hero-c-t768`.
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
const picks = JSON.parse(readFileSync(new URL('../data/design/picks.json', import.meta.url), 'utf8'));
// The mark is excluded: it has no artboard at any width (the builder skips it).
const picked = new Set(Object.entries(picks.picks).map(([id, p]) => `${id}-${p.variant}`));
for (const width of [640, 1280]) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.goto(`http://127.0.0.1:${port}/design-canvas/`, { waitUntil: 'networkidle' });
  const rows = await page.$$eval(`section[data-width="${width}"]`, (els) => els.map((e) => {
    const h3 = e.querySelector('h3'); const cap = h3 ? h3.getBoundingClientRect().height : 0;
    return [e.dataset.component + '-' + e.dataset.variant, Math.ceil((e.getBoundingClientRect().height - cap) / 8) * 8 + 16];
  }));
  for (const [k, h] of rows) out[k] = Math.max(h, 80);
  await page.close();
}
// The picked variants again, at phone and tablet widths.
for (const [width, suffix] of [[375, 'm375'], [768, 't768']]) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.goto(`http://127.0.0.1:${port}/design-canvas/`, { waitUntil: 'networkidle' });
  const rows = await page.$$eval('section[data-component][data-variant]', (els) => els.map((e) => {
    const h3 = e.querySelector('h3'); const cap = h3 ? h3.getBoundingClientRect().height : 0;
    return [e.dataset.component + '-' + e.dataset.variant, Math.ceil((e.getBoundingClientRect().height - cap) / 8) * 8 + 16];
  }));
  for (const [k, h] of rows) if (picked.has(k)) out[`${k}-${suffix}`] = Math.max(h, 80);
  await page.close();
}
// RULE 10, measured rather than asserted. A board height alone cannot tell a hero that
// FITS in 390-450px from one that is CLIPPED to it: `max-height` plus a hidden overflow
// produces the same number either way. So each hero is re-measured at the three desktop
// widths where the clamp is live, and three facts are recorded per width: the scroll
// overflow of `.inner` and of the section (0 when nothing is cut off), how far the CTA row
// sits below the section's own bottom edge (<= 0 when it is inside), and the section
// height (which rule 10 holds between 390 and 450).
const heroOverflow = {};
for (const width of [1024, 1100, 1280]) {
  const page = await browser.newPage({ viewport: { width, height: 900 } });
  await page.goto(`http://127.0.0.1:${port}/design-canvas/`, { waitUntil: 'networkidle' });
  const rows = await page.$$eval('.kit-hero', (els) => els.map((el) => {
    const board = el.closest('section[data-component]');
    const key = board
      ? board.dataset.component + (board.dataset.variant ? '-' + board.dataset.variant : '')
      : 'hero';
    const inner = el.querySelector('.inner');
    const ctas = el.querySelector('.ctas');
    const box = el.getBoundingClientRect();
    return [key, {
      height: Math.round(box.height),
      overflow: inner ? inner.scrollHeight - inner.clientHeight : 0,
      section_overflow: el.scrollHeight - el.clientHeight,
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
