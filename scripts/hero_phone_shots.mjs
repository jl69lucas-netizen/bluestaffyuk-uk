#!/usr/bin/env node
// node scripts/hero_phone_shots.mjs <out dir>
//
// The hero of every rebuilt page (data/facts/rebuilt.json) at phone width (375×812): one PNG
// per page of the `.kit-hero` element, and <out dir>/heroes.json with, per page, the hero's
// layout and whether the photo paints above the heading. Run it on dist/ before and after a
// hero change and diff the two JSON files to list which phone views changed (the London
// component pass, Plan 1 Task 11). Serves dist/ itself on RENDER_SHOTS_PORT (default 4341),
// so build first. Writes nothing inside the repo unless told to.
import { spawn } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { chromium } from '@playwright/test';

const ROOT = resolve(new URL('..', import.meta.url).pathname);
const OUT = process.argv[2];
if (!OUT) {
  console.error('usage: node scripts/hero_phone_shots.mjs <out dir>');
  process.exit(2);
}
const PORT = Number(process.env.RENDER_SHOTS_PORT ?? 4341);
const slugs = JSON.parse(readFileSync(resolve(ROOT, 'data/facts/rebuilt.json'), 'utf8')).sort();
mkdirSync(OUT, { recursive: true });

const server = spawn('python3', ['-m', 'http.server', String(PORT), '--bind', '127.0.0.1'],
  { cwd: resolve(ROOT, 'dist'), stdio: 'ignore' });
await new Promise((r) => setTimeout(r, 800));
const browser = await chromium.launch();
const rows = [];
try {
  const page = await browser.newPage({ viewport: { width: 375, height: 812 }, deviceScaleFactor: 1 });
  for (const slug of slugs) {
    const path = slug === 'index' ? '/' : `/${slug}/`;
    await page.goto(`http://127.0.0.1:${PORT}${path}`, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const row = await page.evaluate(() => {
      const hero = document.querySelector('.kit-hero');
      if (!hero) return { hero: false };
      const pic = hero.querySelector('.pic');
      const title = hero.querySelector('.title');
      const pt = pic ? pic.getBoundingClientRect().top : null;
      const tt = title ? title.getBoundingClientRect().top : null;
      return { hero: true, layout: hero.getAttribute('data-hero-layout'),
        media: hero.getAttribute('data-hero-media'),
        photoFirst: pt !== null && tt !== null ? pt < tt : null,
        photoTop: pt === null ? null : Math.round(pt), titleTop: tt === null ? null : Math.round(tt) };
    });
    const file = resolve(OUT, `${slug.replace(/\//g, '--')}.png`);
    // The page from its top to the hero's foot, unscrolled: what a phone reader sees first,
    // with the sticky chrome where it really sits (an element shot scrolls it under the bar).
    if (row.hero) {
      const bottom = await page.evaluate(() =>
        Math.ceil(document.querySelector('.kit-hero').getBoundingClientRect().bottom + window.scrollY));
      await page.screenshot({ path: file, fullPage: true, clip: { x: 0, y: 0, width: 375, height: Math.min(bottom, 2400) } });
    }
    rows.push({ slug, ...row, shot: row.hero ? file : null });
    console.log(`${slug}: ${row.hero ? `${row.layout} photo-first=${row.photoFirst}` : 'no kit hero'}`);
  }
} finally {
  await browser.close();
  server.kill();
}
writeFileSync(resolve(OUT, 'heroes.json'), JSON.stringify(rows, null, 1) + '\n');
console.log(`${rows.length} pages examined -> ${resolve(OUT, 'heroes.json')}`);
