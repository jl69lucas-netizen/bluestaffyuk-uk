// Infographic previews in a real browser, for scripts/infographic_plan.py (board block 7c).
//
//   node scripts/ig_shots.mjs measure   < jobs.json   # {root, jobs:[{key, path, widths:[…]}]}
//   node scripts/ig_shots.mjs shoot     < jobs.json   # {root, jobs:[{path, width, height, out}]}
//
// `root` is served over a localhost static server, so a preview's relative font URL
// (../../../../../public/fonts/…) resolves to the repo's own woff2 files and the fonts the
// breeder sees on the board are the fonts measured here. Every pass awaits
// `document.fonts.ready` before it measures or shoots (scripts/measure_canvas_heights.mjs
// learned why: a height taken before the swap is a height in the fallback face).
//
// measure prints {key: {width: {h, sw, figs, problems}}} — h is the document's full scroll
// height at that viewport width, sw its scroll width (sw > width is a horizontal overflow),
// figs how many `.fig` elements (the exact figures: prices, the band, the cities) were
// examined, and problems one line per figure whose text overflows its own box or its card,
// or whose text touches an icon box. A figure must never sit under an icon (the coordinator's
// review, 2026-10-03: "£200–£35" showed under the sticker's truck tile). Any problem makes
// the run exit 3 after printing, so the measurement cannot be written over a defect.
// shoot writes a PNG per job: viewport width × height, full page (never clipped), and prints
// {out: {w, h}}.
import { chromium } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { join, extname, resolve } from 'node:path';

const mode = process.argv[2];
const spec = JSON.parse(readFileSync(0, 'utf8'));
const root = resolve(spec.root);
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.woff2': 'font/woff2',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp' };
const srv = createServer((req, res) => {
  const p = join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root)) { res.writeHead(403); res.end(); return; }
  try { const b = readFileSync(p); res.writeHead(200, { 'content-type': types[extname(p)] ?? 'application/octet-stream' }); res.end(b); }
  catch { res.writeHead(404); res.end(); }
}).listen(0, '127.0.0.1');
await new Promise((r) => srv.once('listening', r));
const base = `http://127.0.0.1:${srv.address().port}/`;
const browser = await chromium.launch();
const out = {};
try {
  if (mode === 'measure') {
    for (const job of spec.jobs) {
      out[job.key] = {};
      for (const width of job.widths) {
        // A short viewport, so the scroll height is the content's and never the window's.
        const page = await browser.newPage({ viewport: { width, height: 120 } });
        await page.goto(base + job.path, { waitUntil: 'load' });
        await page.evaluate(() => document.fonts.ready);
        out[job.key][width] = await page.evaluate(() => {
          const d = document.documentElement;
          const b = document.body.getBoundingClientRect();
          const problems = [];
          const icons = [...document.querySelectorAll('.ic')].map((i) => i.getBoundingClientRect())
            .filter((r) => r.width > 0 && r.height > 0);
          const hit = (a, c) => Math.min(a.right, c.right) - Math.max(a.left, c.left) > 1 &&
            Math.min(a.bottom, c.bottom) - Math.max(a.top, c.top) > 1;
          const figs = [...document.querySelectorAll('.fig')];
          for (const el of figs) {
            const box = el.getBoundingClientRect();
            const card = (el.closest('.it,.stop,.leg,.col') || el.closest('.ig')).getBoundingClientRect();
            const range = document.createRange();
            range.selectNodeContents(el);
            const text = [...range.getClientRects()];
            const name = JSON.stringify(el.textContent.trim());
            if (el.scrollWidth > el.clientWidth + 1) problems.push(`${name} overflows its box`);
            for (const r of text) {
              if (r.right > box.right + 1 || r.left < box.left - 1) problems.push(`${name} text runs outside its box`);
              if (r.right > card.right + 1 || r.left < card.left - 1) problems.push(`${name} text runs outside its card`);
              for (const ic of icons) if (hit(r, ic)) problems.push(`${name} sits under an icon`);
            }
          }
          return { h: Math.ceil(Math.max(d.scrollHeight, b.bottom + window.scrollY)), sw: d.scrollWidth,
                   figs: figs.length, problems: [...new Set(problems)] };
        });
        await page.close();
      }
    }
  } else if (mode === 'shoot') {
    for (const job of spec.jobs) {
      const page = await browser.newPage({ viewport: { width: job.width, height: job.height } });
      await page.goto(base + job.path, { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({ path: job.out, fullPage: true });
      out[job.out] = await page.evaluate(() => ({ w: document.documentElement.scrollWidth,
        h: Math.max(document.documentElement.scrollHeight, window.innerHeight) }));
      await page.close();
    }
  } else {
    throw new Error(`unknown mode ${mode}; use measure or shoot`);
  }
} finally {
  await browser.close();
  srv.close();
}
process.stdout.write(JSON.stringify(out));
if (mode === 'measure' && Object.values(out).some((per) => Object.values(per).some((m) => m.problems.length))) {
  process.exitCode = 3;
}
