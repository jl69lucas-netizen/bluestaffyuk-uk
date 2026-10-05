// Measures the map facade's two placements x three styles (facade + loaded) against the city
// type-fit gate (tests/render/lib/cityTypeFit.ts, compiled to ctf.mjs) on a COPY of dist, at the
// city-kit harness viewports (375x812, 768x1024, 1280x800). Writes results.json.
import { readFileSync, writeFileSync } from 'node:fs';
import { chromium } from '/Users/apple/Downloads/BSUK/BSUK-london/node_modules/playwright/index.mjs';
import { cityTypeFit } from './ctf.mjs';
import { facade, HANDLER } from './facade.mjs';

const REPO = '/Users/apple/Downloads/BSUK/BSUK-london';
const m = /export const TIER = \{\s*tablet:\s*(\d+),\s*desktop:\s*(\d+)\s*\}/.exec(readFileSync(`${REPO}/src/lib/cityKit.ts`, 'utf8'));
const TIER = { tablet: +m[1], desktop: +m[2] };
const CAPS = { H1: [26, 30, 34], H2: [22, 25, 28], H3: [17, 18, 20] }; // tests/render/lib/cityTiers.ts HEADING_CAPS
const CSS = readFileSync(new URL('./facade.css', import.meta.url), 'utf8');
const BASE = process.env.BASE ?? 'http://127.0.0.1:4391';
const URL_ = `${BASE}/uk-locations/blue-staffy-puppies-london/`;
const VPS = [[375, 812], [768, 1024], [1280, 800]];

// The two placements: where the figure goes, and which answer (.ch) holds it.
const PLACES = {
  P1: { section: 'delivery', ch: 2, anchor: '.txt > p:first-child', label: 'delivery answer 3 "Which Way Does My Staffordshire Puppy Travel to London?", after its opening paragraph' },
  P2: { section: 'london-life', ch: 0, anchor: '.full > p', label: 'London-life answer 1, under the parks H4 and its paragraph, before the places list' },
};

async function prep(page, vp) {
  await page.setViewportSize({ width: vp[0], height: vp[1] });
  await page.goto(URL_, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  // Every lazy image eager and decoded, so no answer is measured with a 0px picture (4b).
  await page.evaluate(async () => {
    const imgs = [...document.images];
    imgs.forEach((i) => { i.loading = 'eager'; });
    await Promise.all(imgs.map((i) => (i.complete ? null : new Promise((r) => { i.onload = i.onerror = r; setTimeout(r, 8000); }))));
  });
}

async function inject(page, place, style) {
  const P = PLACES[place];
  await page.evaluate(({ css, html, P, handler }) => {
    const st = document.createElement('style'); st.id = 'map-prev'; st.textContent = css; document.head.append(st);
    const ch = document.querySelectorAll(`#${P.section} .ch`)[P.ch];
    const a = ch.querySelector(P.anchor);
    a.insertAdjacentHTML('afterend', html);
    const s = document.createElement('script'); s.textContent = handler; document.body.append(s);
  }, { css: CSS, html: facade(style), P, handler: HANDLER });
}

const answerHeights = (page) => page.evaluate(() => {
  const out = {};
  for (const id of ['delivery', 'london-life']) {
    out[id] = [...document.querySelectorAll(`#${id} .ch`)].map((c) => Math.round(c.getBoundingClientRect().height));
  }
  const fig = document.querySelector('[data-city-map]');
  out.figure = fig ? Math.round(fig.getBoundingClientRect().height) : 0;
  out.stage = fig?.querySelector('.cm-stage') ? Math.round(fig.querySelector('.cm-stage').getBoundingClientRect().height) : 0;
  const b = fig?.querySelector('.cm-load');
  out.button = b ? [Math.round(b.getBoundingClientRect().width), Math.round(b.getBoundingClientRect().height)] : null;
  out.pageHeight = document.documentElement.scrollHeight;
  return out;
});

const browser = await chromium.launch();
const ctx = await browser.newContext({ deviceScaleFactor: 1 });
const page = await ctx.newPage();
const ext = [];
page.on('request', (r) => { if (!r.url().startsWith(BASE) && !r.url().startsWith('data:') && !r.url().startsWith('about:')) ext.push(r.url()); });
const results = [];
for (const vp of VPS) {
  ext.length = 0;
  await prep(page, vp);
  const base = await page.evaluate(cityTypeFit, { viewport: vp[0], tier: TIER, caps: CAPS });
  const bh = await answerHeights(page);
  results.push({ vp, scenario: 'baseline', examined: base.examined, defects: base.defects, heights: bh, external: [...ext] });
  for (const place of ['P1', 'P2']) for (const style of ['s1', 's2', 's3']) for (const state of ['facade', 'loaded']) {
    ext.length = 0;
    await prep(page, vp);
    const before = ext.length;
    await inject(page, place, style);
    if (state === 'loaded') { await page.click('[data-city-map] .cm-load'); await page.waitForTimeout(150); }
    const r = await page.evaluate(cityTypeFit, { viewport: vp[0], tier: TIER, caps: CAPS });
    const h = await answerHeights(page);
    const newDefects = r.defects.filter((d) => !base.defects.includes(d));
    results.push({ vp, scenario: `${place}-${style}-${state}`, place, style, state, examined: r.examined, defects: r.defects, newDefects, heights: h, externalAfterInject: ext.slice(before) });
    console.log(vp[0], place, style, state, 'answer', place === 'P1' ? h.delivery[2] : h['london-life'][0], 'fig', h.figure, 'new defects', newDefects.length);
  }
}
writeFileSync(new URL('./results.json', import.meta.url), JSON.stringify({ TIER, results }, null, 1));
await browser.close();
