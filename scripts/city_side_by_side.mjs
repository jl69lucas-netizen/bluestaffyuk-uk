#!/usr/bin/env node
// node scripts/city_side_by_side.mjs [--city london] [--slug blue-staffy-puppies-london]
//
// The side-by-side the user confirms before a city's component pass is done (spec §3.5, "The
// user sees each built component beside its canvas version and confirms the match"). For each of
// the city's picks (every pick but a "none") it shoots, at 375, 768 and 1280:
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
// A pick the page does not use is recorded as "none" (gap G4): it names no variant, so it has no
// canvas frame and no built component to set beside it.
const NOT_USED = 'none';
// Gap G10 (the Manchester page run, Phase F Task 32): each city's picked rows are the `"project": 5`
// rows of data/design/components.json whose `canvas_variant` is one of ITS picks, and each row names
// the root selector its built component is shot by. Every city's rows sit in one file, so the city
// selects its own; comparing every project 5 row with one city's picks failed the second city.
const all = JSON.parse(readFileSync(resolve(ROOT, 'data/design/components.json'), 'utf8')).filter((r) => r.project === 5);
// The picks in city-page order (scripts/city_components.py COMPONENT_IDS), each paired with its row.
const order = Object.keys(picks).filter((c) => picks[c] !== NOT_USED);
const matches = order.map((c) => all.filter((r) => r.canvas_variant === picks[c]));
for (const [i, c] of order.entries()) {
  if (matches[i].length !== 1) {
    console.error(`${picks[c]}: ${matches[i].length} rows of data/design/components.json carry it as canvas_variant (need exactly 1)`);
    process.exit(1);
  }
  if (!matches[i][0].root_selector) {
    console.error(`${matches[i][0].id} (${picks[c]}): no root_selector in data/design/components.json`);
    process.exit(1);
  }
}
const rows = matches.map((m) => m[0]);

// The picks whose canvas frame wraps them in stand-in page sections: their own element. London's
// contents frame wraps its panel in stand-ins; Manchester's contents frame is the card itself.
const CANVAS_SELECTOR = {
  'jump-links': '[data-jump-strip]',
  'desktop-dial': '[data-dial]',
  ...(CITY === 'london' ? { 'contents-list': '[data-component] > .panel' } : {}),
};
// Why a component is not displayed at a width, for its card: every city's nav furniture works so.
const HIDDEN_WHY = {
  'desktop-dial': 'The dial is desktop navigation: it shows from 1024px, and the jump band stands in for it on phones and tablets.',
  'jump-links': 'The jump band is phone and tablet navigation: it shows below 1024px, and the dial beside the body takes its place from 1024px.',
  'contents-list': 'The contents list shows below 1024px only: from 1024px the dial beside the body is the page\'s contents, as on the other pages (your ruling, answer board q05, 2026-09-29).',
};
// The sticky furniture is shot as the element itself; every section is clipped from the page.
const DIAL = 'desktop-dial';
const STICKY = new Set(['jump-links', DIAL]);
// Chrome: shot as the element itself, with nothing hidden (the header sits outside its box).
const CHROME = new Set(['jump-links']);
// Hidden while a section is shot: the site header and every city's jump band (the shared
// `data-city-nav="bar"` hook, gap G12; London's band also keeps its own hook).
const HIDE_CHROME = '.kit-hdr, [data-city-nav="bar"], [data-city-jump-stepper] { visibility: hidden !important; }';

// What differs on purpose, per pick component, per city. `column` is added at run time for any
// component the 1280 shot finds narrower than the page (it sits in the column beside the dial).
const TYPE_FIT = 'The type-fit scale you asked for on 2026-09-28: headings capped at 22 / 25 / 28px and reading paragraphs held to 65ch.';
const BOLD = 'Bold, brand-coloured headings restored (Code fact 5): the site base inherits weight and colour, so the kit gives city headings the canvas weight back.';
const GUARANTEE = 'The two-year health guarantee is printed from data/settings.json (guarantee_days 730, guarantee_label), your answer of 2026-09-29 (answer board q07), never typed on the page.';
const PHOTO = (who) => `A different served photo where the canvas repeated Maggie's (Code fact 4): one served photo appears once per page, so this one carries ${who}.`;
// Manchester's page is a scaffold until row 12: every caller-written paragraph is a marked line.
const SCAFFOLD = 'Its paragraph is a marked scaffold line, not copy: the page is written at page-run row 12 from the approved page board. Headings are the approved outline\'s, word for word.';
const DELIBERATE_BY_CITY = {
  london: {
    hero: [BOLD, TYPE_FIT],
    'counter-strip': ['From 640 to 839px the price scale\'s count sits above the line, not on it, so the figures keep their own width.'],
    'trust-strip': [PHOTO("Jones's portrait"), GUARANTEE, BOLD, TYPE_FIT],
    'contents-list': [BOLD],
    'desktop-dial': [],
    'jump-links': [],
    'key-takeaways': [PHOTO('Jones seated'), GUARANTEE, BOLD, TYPE_FIT],
    'puppy-cards': [BOLD, TYPE_FIT],
    tables: [BOLD, TYPE_FIT],
    video: [BOLD, TYPE_FIT],
    'image-text': [PHOTO('Byrd for chapter one'), BOLD, TYPE_FIT],
    reviews: ['The review is split into three paragraphs rather than one block.', BOLD, TYPE_FIT],
    'faq-blocks': [PHOTO('the London owner photo in the rail'), 'The canvas frame stacks all three FAQ blocks; the page places them apart (buying, checking us, Staffy life), each under the section it answers, so the built shot is the first block, the one with the photo rail.', GUARANTEE, BOLD, TYPE_FIT],
    newsletter: [BOLD, TYPE_FIT],
    'contact-form': [BOLD, TYPE_FIT],
  },
  // From docs/research/manchester-components/hardening-log.md, "Built — Task 28" to "Task 31".
  manchester: {
    hero: ['The H1 is the approved outline\'s, at the canvas\'s size inside the type-fit caps.', 'The promise rail\'s labels wrap balanced rather than staying on one line, so a longer label never runs into its neighbour at 1024px.', SCAFFOLD],
    'counter-strip': ['Each figure cell is a column, label at the top and figure at the foot, so the two prices share a baseline on a phone.'],
    'trust-strip': ['From 640px an odd last slip spans both columns, so the folder ends square.'],
    'contents-list': ['From 640px the photo column is 272 to 340px wide and the rows take two columns from 768px, so the served photo is never painted past twice its size.'],
    'desktop-dial': ['The rail is inset from its column\'s edge, and the marked row is kept in view inside the rail on a short screen.'],
    'jump-links': ['On the page the bar is the top chrome: it slides away on the way down and comes back on the way up (answer board q03).'],
    'key-takeaways': ['The head is split 7 to 5, so the title takes two lines, not three.'],
    tables: ['On a phone each card\'s price is pinned to its foot, so the prices in a pair share a line.'],
    'image-text': ['The built shot is the deposit section, the canvas\'s own, with its four cells read from the data. The other eight body sections show the outline\'s plan for the section (its row, framework and planned words) in the sheet until the page is written.', 'An odd last cell spans the row.', 'From a desktop box the question and its opening line run the full width above, and the photo and the sheet sit side by side below: in the page\'s 832px column the canvas\'s split set every long H2 on three lines (your type-fit ruling).', SCAFFOLD],
    reviews: ['The page mounts the plates three times (outline rows 6, 11 and 20), the photo side alternating; the built shot is the first, The Victoria Family.'],
    'faq-blocks': ['The canvas frame stacks the three FAQ blocks; the page places them apart (outline rows 7, 12 and 21), so the built shot is the first block.', 'Long answers are set in paragraphs at their own sentence breaks, words untouched.', 'In a tablet box the answers run the full width of their row, with no indent, so the longest answer stays within six lines at 1024px.', SCAFFOLD],
    newsletter: ['The empty-email line reads the email field only.'],
    'contact-form': ['From a desktop box the question and its answer run the full width above, and the photo bleeds from the box edge beside the form, as tall as the form.', SCAFFOLD],
  },
};
const DELIBERATE = DELIBERATE_BY_CITY[CITY] ?? {};
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
// The page's approved board, where it has one, says which picked components the page mounts (the
// kit is a menu: rules/gates.md outline-before-components). A pick the board mounts on no section
// (London's puppy cards and video, once its page was written) is noted on its card, not failed; a
// page with no board yet (a scaffold) must carry every pick.
const BOARD = resolve(ROOT, `data/boards/${SLUG}.json`);
const boardMounts = existsSync(BOARD)
  ? new Set(JSON.parse(readFileSync(BOARD, 'utf8')).sections.flatMap((s) => [s.component, ...(s.subcomponents ?? []).map((x) => x.component)]).filter(Boolean))
  : null;
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
    const sel = row.root_selector;
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
      if ((await page.locator(sel).count()) === 0 && boardMounts && !boardMounts.has(row.id)) {
        shot.note = `Not on the page: its approved board mounts no section with ${row.id}.`;
      } else if ((await page.locator(sel).count()) === 0) {
        console.error(`${component}: ${sel} matched nothing on /${PAGE_PATH}`);
        process.exitCode = 1;
        shot.note = `Not found on the page (${sel}).`;
      } else if (!(await el.isVisible())) {
        shot.note = `Not shown at ${width}px by design. ${HIDDEN_WHY[component] ?? `${row.file.replace('.astro', '')} is not displayed at this width.`}`;
      } else {
        if (!CHROME.has(component)) {
          // The site header and the jump band are sticky; neither may sit over another section.
          await page.addStyleTag({ content: HIDE_CHROME });
        }
        for (const src of await settleImages(page, sel)) broken.push(`${component} built @${width}: ${src}`);
        if (CHROME.has(component)) await page.evaluate(() => window.scrollTo(0, 0));
        else await el.scrollIntoViewIfNeeded();
        if (component === DIAL) {
          // The dial follows the reader. Scroll just far enough that the whole dial is on screen,
          // let the scroll spy settle, and read the row it marks; the shot then checks that row's
          // section is the one in the spy's reading band (40-45% down), so the marked row is
          // always the section being read.
          dialRow = await page.evaluate(async (s) => {
            const dial = document.querySelector(s);
            const r = dial.getBoundingClientRect();
            window.scrollTo(0, Math.max(0, r.bottom + window.scrollY - window.innerHeight + 16));
            const settle = async () => {
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
            };
            await settle();
            const band = window.innerHeight * 0.42;
            // A short dial (Manchester's numeral rail) is whole on screen while the reader is still
            // above the first listed section, where no row can be the one being read: scroll on
            // until the reading band is inside the first section, then let the spy settle again.
            const first = document.getElementById(dial.querySelector('a[href^="#"]').getAttribute('href').slice(1));
            const top = first.getBoundingClientRect().top;
            if (top > band) {
              window.scrollBy(0, top - band + 40);
              await settle();
            }
            const cur = dial.querySelector('[aria-current]');
            if (!cur) return null;
            const t = document.getElementById(cur.getAttribute('href').slice(1)).getBoundingClientRect();
            cur.dataset.sbsRow = '1';
            // The row's name: its label where the row also prints a numeral (Manchester's rail).
            const name = (cur.querySelector('.l') ?? cur).textContent.trim();
            return t.top <= band && t.bottom >= band ? name : `MISMATCH:${name}`;
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
        if (component === DIAL) {
          // Clipped from the viewport where it sticks: an element shot scrolls it into view, which
          // moves the reader and so the dial's current row.
          const b = await el.evaluate((n) => { const r = n.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; });
          if (b.y < 0 || b.y + b.h > height) { console.error(`${component} @${width}: the dial does not fit the viewport`); process.exitCode = 1; }
          const x = Math.ceil(b.x);
          const y = Math.max(0, Math.ceil(b.y));
          await page.screenshot({ path: resolve(OUT, shot.builtFile), type: 'jpeg', quality: 78, clip: { x, y, width: Math.floor(b.x + b.w) - x, height: Math.min(height, Math.floor(b.y + b.h)) - y } });
          const still = await el.evaluate((n) => n.querySelector('[data-sbs-row]').hasAttribute('aria-current'));
          if (!still) { console.error(`${component} @${width}: the dial's row "${dialRow}" was not current when shot`); process.exitCode = 1; }
        } else if (STICKY.has(component)) {
          await el.screenshot({ path: resolve(OUT, shot.builtFile), type: 'jpeg', quality: 78 });
        } else {
          // The section's own box, rounded INWARD: an element shot rounds a fractional edge out and
          // picks up a 1px line of the next section. A section that fits the viewport is shot where
          // it sits on screen: a full-page capture re-lays the page out at its whole height, and an
          // already painted lazy photo could be captured before it was decoded again (the Manchester
          // deposit section's photo came out as an empty box at 1280). A taller one needs the page.
          const tall = await el.evaluate((n) => n.getBoundingClientRect().height > window.innerHeight);
          if (!tall) {
            await el.evaluate((n) => window.scrollTo(0, n.getBoundingClientRect().top + window.scrollY - 1));
            // Decode the section's own painted photos again, each capped (a decode never settles
            // for an image that never loads).
            await el.evaluate((n) => Promise.all(Array.from(n.querySelectorAll('img')).filter((i) => i.getClientRects().length)
              .map((i) => Promise.race([i.decode ? i.decode().catch(() => null) : null, new Promise((r) => setTimeout(r, 3000))]))));
            await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
          }
          const b = await el.evaluate((n, inView) => {
            const r = n.getBoundingClientRect();
            return inView ? { x: r.left, y: r.top, w: r.width, h: r.height }
              : { x: r.left + window.scrollX, y: r.top + window.scrollY, w: r.width, h: r.height };
          }, !tall);
          const x = Math.ceil(b.x);
          const y = Math.ceil(b.y);
          const clip = { x, y, width: Math.floor(b.x + b.w) - x, height: Math.floor(b.y + b.h) - y };
          await page.screenshot({ path: resolve(OUT, shot.builtFile), type: 'jpeg', quality: 78, fullPage: tall, clip });
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
const COUNT = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve',
  'thirteen', 'fourteen', 'fifteen'][order.length] ?? String(order.length);
// What the built copies carry: London's page when its side-by-side was confirmed; a scaffold's lines.
const CARRY = CITY === 'london' ? "the page's placeholder copy" : 'marked scaffold lines in place of copy, under the approved outline\'s headings,';
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
<p class="intro">Each of the ${COUNT} components you picked on the ${title} component canvas, beside the component as built on the real ${title} page, at phone (375px), tablet (768px) and desktop (1280px) width. The built copies carry ${CARRY} and the site's data (puppies, prices, served photos with their served alt text). Each card says what differs on purpose. Tell us which ones match, and what differs on any that do not.</p>
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
