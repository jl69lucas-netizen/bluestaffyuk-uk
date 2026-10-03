// Infographic previews in a real browser, for scripts/infographic_plan.py (board block 7c).
//
//   node scripts/ig_shots.mjs measure   < jobs.json   # {root, jobs:[{key, path, widths:[…]}]}
//   node scripts/ig_shots.mjs shoot     < jobs.json   # {root, jobs:[{path, width, height, out}]}
//   node scripts/ig_shots.mjs crop      < jobs.json   # {root, jobs:[{path, widths:[…], ratio?, margin?, out}]}
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
import { join, extname, resolve, sep } from 'node:path';

const mode = process.argv[2];
const spec = JSON.parse(readFileSync(0, 'utf8'));
const root = resolve(spec.root);
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.woff2': 'font/woff2',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp' };
const srv = createServer((req, res) => {
  const p = join(root, decodeURIComponent(req.url.split('?')[0]));
  if (p !== root && !p.startsWith(root + sep)) { res.writeHead(403); res.end(); return; }
  try { const b = readFileSync(p); res.writeHead(200, { 'content-type': types[extname(p)] ?? 'application/octet-stream' }); res.end(b); }
  catch { res.writeHead(404); res.end(); }
}).listen(0, '127.0.0.1');
await new Promise((r) => srv.once('listening', r));
const base = `http://127.0.0.1:${srv.address().port}/`;
const TIMEOUT = 30_000;   // per page action; a hung preview fails instead of hanging the run
const out = {};
let browser;
try {
  browser = await chromium.launch({ timeout: TIMEOUT });
  if (mode === 'measure') {
    for (const job of spec.jobs) {
      out[job.key] = {};
      for (const width of job.widths) {
        // A short viewport, so the scroll height is the content's and never the window's.
        const page = await browser.newPage({ viewport: { width, height: 120 } });
        page.setDefaultTimeout(TIMEOUT);
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
      page.setDefaultTimeout(TIMEOUT);
      await page.goto(base + job.path, { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({ path: job.out, fullPage: true });
      out[job.out] = await page.evaluate(() => ({ w: document.documentElement.scrollWidth,
        h: Math.max(document.documentElement.scrollHeight, window.innerHeight) }));
      await page.close();
    }
  } else if (mode === 'crop') {
    // One job per baked file. The page background is made transparent and the body padding
    // set to `margin`, so the screenshot is the figure itself plus an even transparent margin
    // (wide enough for the hard shadows and the tilted stickers) and never the page's own
    // bone: the framing (reframe_og.contain_alpha) lays it on the frame's bone, so no
    // two-tone band can form. Every width in `widths` is measured; with a `ratio` the width
    // whose figure box is closest to it (in log terms) is shot, without one the first width.
    // The figure's 1100px reading cap is lifted, so a wide box can be filled by a wide render.
    // `min_font` is the smallest computed font size of any visible text in the figure, in
    // CSS px (image px at the default `scale` 1; a `scale` of 2 shoots at twice the pixels,
    // for a master the framing will shrink into its box rather than enlarge).
    for (const job of spec.jobs) {
      const M = job.margin ?? 16;
      const open = async (width) => {
        const page = await browser.newPage({ viewport: { width, height: 800 }, deviceScaleFactor: job.scale ?? 1 });
        page.setDefaultTimeout(TIMEOUT);
        await page.goto(base + job.path, { waitUntil: 'load' });
        await page.addStyleTag({ content: `html,body{background:transparent !important}body{padding:${M}px !important}.ig{max-width:none !important}` });
        await page.evaluate(() => document.fonts.ready);
        return page;
      };
      const box = (page) => page.evaluate((m) => {
        const r = document.querySelector('figure.ig').getBoundingClientRect();
        // An exact figure (.fig) broken over two lines ("£200–" / "£350") is a defect at that
        // width: the width is never shot, whatever its shape.
        const wrapped = [...document.querySelectorAll('.fig')].filter((el) => {
          const range = document.createRange();
          range.selectNodeContents(el);
          const tops = [...range.getClientRects()].filter((q) => q.width > 0).map((q) => Math.round(q.top));
          return tops.some((t) => Math.abs(t - tops[0]) > 2);
        }).map((el) => el.textContent.trim());
        return { x: Math.max(0, Math.floor(r.left + window.scrollX - m)), y: Math.max(0, Math.floor(r.top + window.scrollY - m)),
                 w: Math.ceil(r.width + 2 * m), h: Math.ceil(r.height + 2 * m), wrapped };
      }, M);
      let best = null;
      const tried = {};
      for (const width of job.widths) {
        const page = await open(width);
        const b = await box(page);
        await page.close();
        const err = job.ratio ? Math.abs(Math.log((b.w / b.h) / job.ratio)) : 0;
        tried[width] = { w: b.w, h: b.h, ratio: +(b.w / b.h).toFixed(3), wrapped: b.wrapped };
        if (b.wrapped.length) continue;
        if (!best || err < best.err - 1e-9) best = { width, err };
      }
      if (!best) throw new Error(`${job.path}: an exact figure wraps at every width: ${JSON.stringify(tried)}`);
      const page = await open(best.width);
      const b = await box(page);
      const fonts = await page.evaluate(() => {
        const fig = document.querySelector('figure.ig');
        const walk = document.createTreeWalker(fig, NodeFilter.SHOW_TEXT);
        let min = Infinity, text = '';
        for (let n = walk.nextNode(); n; n = walk.nextNode()) {
          if (!n.textContent.trim()) continue;
          const el = n.parentElement;
          if (!el || el.closest('[aria-hidden="true"]') || !el.getClientRects().length) continue;
          const cs = getComputedStyle(el);
          if (cs.visibility === 'hidden' || cs.display === 'none') continue;
          const px = parseFloat(cs.fontSize);
          if (px < min) { min = px; text = n.textContent.trim().slice(0, 60); }
        }
        return { min_font: min, min_font_text: text };
      });
      await page.screenshot({ path: job.out, fullPage: true, omitBackground: true,
        clip: { x: b.x, y: b.y, width: b.w, height: b.h } });
      await page.close();
      out[job.out] = { width: best.width, w: b.w, h: b.h, tried, ...fonts };
    }
  } else {
    throw new Error(`unknown mode ${mode}; use measure, shoot or crop`);
  }
} finally {
  // close() can hang on a wedged browser: give it 5s, then exit hard below. Playwright's own
  // process-exit hook SIGKILLs every browser it launched, so nothing is left running.
  if (browser) await Promise.race([browser.close().catch(() => {}), new Promise((r) => setTimeout(r, 5000))]);
  srv.close();
}
process.stdout.write(JSON.stringify(out));
const defect = mode === 'measure' &&
  Object.values(out).some((per) => Object.values(per).some((m) => m.problems.length));
process.stdout.write('', () => process.exit(defect ? 3 : 0));
