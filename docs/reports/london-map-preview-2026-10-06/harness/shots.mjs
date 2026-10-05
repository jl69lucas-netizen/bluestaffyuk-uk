// Screenshots of the facade styles in place on a COPY of dist (jpg, <= 900px wide), plus the real
// loaded map once (a one-off Google fetch on this machine) with its request count and bytes.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { chromium } from '/Users/apple/Downloads/BSUK/BSUK-london/node_modules/playwright/index.mjs';
import { facade, HANDLER } from './facade.mjs';

const OUT = process.env.OUT;
mkdirSync(OUT, { recursive: true });
const CSS = readFileSync(new URL('./facade.css', import.meta.url), 'utf8');
const BASE = process.env.BASE;
const URL_ = `${BASE}/uk-locations/blue-staffy-puppies-london/`;
const PLACES = {
  P1: { section: 'delivery', ch: 2, anchor: '.txt > p:first-child' },
  P2: { section: 'london-life', ch: 0, anchor: '.full > p' },
};
const VPS = { 375: 812, 768: 1024, 1280: 800 };

const browser = await chromium.launch();
async function open(w) {
  const ctx = await browser.newContext({ viewport: { width: w, height: VPS[w] }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  await page.goto(URL_, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => {
    const imgs = [...document.images];
    imgs.forEach((i) => { i.loading = 'eager'; });
    await Promise.all(imgs.map((i) => (i.complete ? null : new Promise((r) => { i.onload = i.onerror = r; setTimeout(r, 8000); }))));
  });
  return { ctx, page };
}
async function inject(page, place, style) {
  await page.evaluate(({ css, html, P, handler }) => {
    const st = document.createElement('style'); st.textContent = css; document.head.append(st);
    document.querySelectorAll(`#${P.section} .ch`)[P.ch].querySelector(P.anchor).insertAdjacentHTML('afterend', html);
    const s = document.createElement('script'); s.textContent = handler; document.body.append(s);
  }, { css: CSS, html: facade(style), P: PLACES[place], handler: HANDLER });
}
// The clip: the tray's width (<= 900), from the opening paragraph above the figure to just below it.
async function clipFor(page, w, { whole = false } = {}) {
  return page.evaluate(({ w, whole }) => {
    const fig = document.querySelector('[data-city-map]');
    const ch = fig.closest('.ch');
    const tray = fig.closest('.tray');
    const t = tray.getBoundingClientRect(); const f = fig.getBoundingClientRect(); const c = ch.getBoundingClientRect();
    const sy = window.scrollY;
    const prev = fig.previousElementSibling?.getBoundingClientRect();
    const x = w <= 400 ? 0 : Math.max(0, t.left - 8);
    const width = w <= 400 ? w : Math.min(900, t.width + 16);
    const top = whole ? c.top - 12 : (prev ? prev.top - 16 : f.top - 24);
    const bottom = whole ? c.bottom + 12 : f.bottom + 24;
    return { x, y: top + sy, width, height: bottom - top };
  }, { w, whole });
}
const shot = async (page, clip, name) => {
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: `${OUT}/${name}.jpg`, type: 'jpeg', quality: 82, fullPage: true, clip });
  console.log('wrote', name, Math.round(clip.width), 'x', Math.round(clip.height));
};

// 1. Each style in P1 at each width, facade state.
if (!process.env.ONLY_LOADED) for (const style of ['s1', 's2', 's3']) for (const w of [375, 768, 1280]) {
  const { ctx, page } = await open(w);
  await inject(page, 'P1', style);
  await shot(page, await clipFor(page, w), `p1-${style}-${w}`);
  await ctx.close();
}
// 2. P2 for comparison (S1) at 375 and 1280, and the whole P1 answer in context at 375 and 1280.
if (!process.env.ONLY_LOADED) for (const w of [375, 1280]) {
  let { ctx, page } = await open(w);
  await inject(page, 'P2', 's1');
  await shot(page, await clipFor(page, w), `p2-s1-${w}`);
  await ctx.close();
  ({ ctx, page } = await open(w));
  await inject(page, 'P1', 's1');
  await shot(page, await clipFor(page, w, { whole: true }), `p1-s1-${w}-answer`);
  await ctx.close();
}
// 3. Keyboard focus on the button (S1 on steel, S2 on bone) at 375.
if (!process.env.ONLY_LOADED) for (const style of ['s1', 's2', 's3']) {
  const { ctx, page } = await open(375);
  await inject(page, 'P1', style);
  await page.evaluate(() => { const a = document.querySelector('[data-city-map]').previousElementSibling; a.setAttribute('tabindex', '-1'); a.focus(); });
  await page.keyboard.press('Tab');
  const focused = await page.evaluate(() => document.activeElement?.className);
  const clip = await page.evaluate(() => {
    const b = document.querySelector('.cm-load').getBoundingClientRect();
    return { x: 0, y: b.top + window.scrollY - 70, width: 375, height: b.height + 140 };
  });
  await page.screenshot({ path: `${OUT}/focus-${style}-375.jpg`, type: 'jpeg', quality: 82, fullPage: true, clip });
  console.log('focus', style, 'activeElement', focused);
  await ctx.close();
}
// 4. The real map, loaded by a tap (S1 in P1) at 375 and 1280: count what Google sends.
const net = {};
for (const w of [375, 1280]) {
  const { ctx, page } = await open(w);
  const before = [];
  page.on('request', (r) => { if (!r.url().startsWith(BASE)) before.push(r.url()); });
  await inject(page, 'P1', 's1');
  const preTap = before.length;
  const reqs = [];
  page.on('requestfinished', async (r) => { if (!r.url().startsWith(BASE)) { try { const s = await r.sizes(); reqs.push({ url: r.url(), bytes: s.responseBodySize + s.responseHeadersSize }); } catch { reqs.push({ url: r.url(), bytes: 0 }); } } });
  await page.evaluate(() => { window.__realMap = true; });
  await page.locator('.cm-load').scrollIntoViewIfNeeded();
  await page.click('.cm-load');
  await page.waitForTimeout(7000);
  // In-viewport capture: a cross-origin map frame scrolled out of view is not painted into a
  // full-page capture. Put the figure in view, then clip in viewport coordinates.
  await page.evaluate(() => { const f = document.querySelector('[data-city-map]'); window.scrollTo(0, f.getBoundingClientRect().top + window.scrollY - 160); });
  await page.waitForTimeout(2500);
  const pc = await clipFor(page, w);
  const sy = await page.evaluate(() => window.scrollY);
  const clip = { ...pc, y: pc.y - sy };
  const frames = page.frames().map((fr) => fr.url()).filter((u) => u.includes('google'));
  console.log('map frames', frames.length);
  await page.screenshot({ path: `${OUT}/p1-s1-${w}-loaded.jpg`, type: 'jpeg', quality: 82, clip });
  const iframe = await page.evaluate(() => { const f = document.querySelector('.cm-frame'); return f && { title: f.title, loading: f.loading, referrerPolicy: f.referrerPolicy, src: f.src, h: Math.round(f.getBoundingClientRect().height), focused: document.activeElement === f }; });
  const cookies = (await ctx.cookies()).map((c) => `${c.domain} ${c.name}`);
  const hosts = [...new Set(reqs.map((r) => new URL(r.url).host))];
  net[w] = { externalBeforeTap: preTap, requestsAfterTap: reqs.length, kbAfterTap: Math.round(reqs.reduce((a, r) => a + r.bytes, 0) / 1024), hosts, cookies, iframe };
  console.log(w, JSON.stringify(net[w]));
  await ctx.close();
}
writeFileSync(new URL('./network.json', import.meta.url), JSON.stringify(net, null, 1));
await browser.close();
