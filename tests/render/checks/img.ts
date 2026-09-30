import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { register, type CheckResult } from '../lib/registry.js';
import { settlePage } from '../lib/probes.js';
import type { Page } from '@playwright/test';

register({
  id: 'img-srcset-within-2x',
  family: 'IMG',
  severity: 'blocking',
  describe: 'no image may decode at more than 2x the width it paints at',
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    await settlePage(page);

    /**
     * A still-loading image is NOT a broken image, and this check used to call them the
     * same thing. `settlePage` caps its wait at 3s; on the heaviest page in the suite
     * (the source project's image-heaviest listing page, 58 images) the eager `decoding="async"` hero candidate was still in
     * flight at that cap and got reported as "failed to decode" — wording that reads as
     * a 404. It failed at vp375 only, because `sizes` resolves to ~170px there and that
     * is the sole viewport selecting the 230w candidate; the same page passed at 768 and
     * 1280 in the same run. The file was valid the whole time (6,294-byte WebP, decodes
     * to 230x144). reference_same_input_different_verdict.
     *
     * So: give the stragglers a real `decode()` budget before judging anything.
     */
    await page.evaluate(async () => {
      const pending = Array.from(document.images).filter((i) => !i.complete);
      await Promise.race([
        Promise.allSettled(pending.map((i) => i.decode().catch(() => null))),
        new Promise((res) => setTimeout(res, 5000)),
      ]);
      /**
       * 2026-09-12: four consecutive scoped runs of buy-with-shipping each reported ONE
       * different image as `complete && naturalWidth === 0` at 375/768 — iata-cargo-crate,
       * one-seller-three-platform, health-guarantee-enforceable, how-you-know-the-sex —
       * while every file decoded with Pillow and shipped in dist/, and the same page had
       * passed 3/3 that morning. A fetch that resets under the ~40-image eager burst leaves
       * exactly that state, and it is indistinguishable from a 404 in one read. So give a
       * "broken" image ONE reload before judging it: a real 404 fails the retry too, which
       * is what keeps known_broken/img-broken-vs-still-loading.html red.
       */
      const broken = Array.from(document.images).filter((i) => i.complete && i.naturalWidth === 0 && (i.currentSrc || i.src));
      if (broken.length) {
        await Promise.race([
          Promise.allSettled(broken.map(async (i) => {
            const src = i.getAttribute('src') || '';
            const srcset = i.getAttribute('srcset') || '';
            i.removeAttribute('srcset'); i.removeAttribute('src');
            if (srcset) i.setAttribute('srcset', srcset);
            i.setAttribute('src', src);
            await i.decode().catch(() => null);
          })),
          new Promise((res) => setTimeout(res, 4000)),
        ]);
      }
    });

    const r = await page.evaluate(() => {
      const dpr = window.devicePixelRatio || 1;
      let examined = 0;
      const bad: string[] = [];
      const skipped: string[] = [];
      const unmeasured: string[] = [];
      for (const img of Array.from(document.images)) {
        const box = img.getBoundingClientRect();
        if (box.width < 1) continue;
        const name = (img.currentSrc || img.src || '(no src)').split('/').pop() as string;
        if (img.complete && img.naturalWidth === 0) {
          // GENUINELY BROKEN. A 404'd image has complete === true and naturalWidth === 0.
          // Silently dropping it is how a broken page scores clean, so surface it.
          skipped.push(name);
          continue;
        }
        if (!img.complete) {
          // STILL LOADING after the decode budget above — a limit of our measurement,
          // not a fact about the page. Counted and named so the run is honest about its
          // own coverage, but never asserted as breakage on a blocking check.
          unmeasured.push(name);
          continue;
        }
        examined++;
        const ratio = img.naturalWidth / (box.width * dpr);
        if (ratio > 2.0) {
          const file = (img.currentSrc || img.src).split('/').pop();
          bad.push(
            `${file} natural=${img.naturalWidth} painted=${Math.round(box.width)} ${ratio.toFixed(2)}x`,
          );
        }
      }
      // skippedTotal is derived BEFORE the slice, for the same reason `count` is:
      // a row's count must be the true magnitude, never the length of a list that
      // was truncated for readability. Phase 2 swept two checks for exactly this
      // and the comment below claimed both were the only stragglers — `skipped`
      // was a third, and reported 10 whenever 10 or more images failed to decode.
      return {
        examined,
        bad: bad.slice(0, 10),
        count: bad.length,
        skipped: skipped.slice(0, 10),
        skippedTotal: skipped.length,
        unmeasured: unmeasured.slice(0, 10),
        unmeasuredTotal: unmeasured.length,
      };
    });

    const defects = [];
    if (r.count) {
      defects.push({
        checkId: 'img-srcset-within-2x',
        family: 'IMG' as const,
        viewport,
        count: r.count,
        message: `${r.count} oversized image(s): ${r.bad.join(' | ')}`,
      });
    }
    if (r.skippedTotal) {
      defects.push({
        checkId: 'img-srcset-within-2x',
        family: 'IMG' as const,
        viewport,
        count: r.skippedTotal,
        message: `${r.skippedTotal} image(s) failed to LOAD (complete, naturalWidth 0 — 404 or corrupt): ${r.skipped.join(', ')}${
          r.skippedTotal > r.skipped.length ? ` (+${r.skippedTotal - r.skipped.length} more)` : ''
        }`,
      });
    }
    // Deliberately NOT a defect row. These images were still in flight after a 5s
    // decode budget, which is a statement about this run, not about the page — and
    // this check is `blocking`, so emitting it would fail a build over harness timing.
    // Logged instead, so the run never silently claims coverage it did not have.
    if (r.unmeasuredTotal) {
      console.log(
        `[img-srcset-within-2x] ${r.unmeasuredTotal} image(s) still loading after the decode budget @ ${viewport}px, excluded from examined: ${r.unmeasured.join(', ')}`,
      );
    }
    return { examined: r.examined, defects };
  },
});

/**
 * The other side of img-srcset-within-2x's ratio (learning loop 2026-09-27, L6). That check
 * fails an image carrying more than 2x the pixels it paints and never reads the case where it
 * carries FEWER: four London canvas variants shipped soft photos (a 1080px square painted
 * across 1280, a 400x500 litter photo stretched) and nothing measured them. The scale is the
 * one the browser applies to the CONTENT box (padding and border are not image): under
 * `object-fit: cover` or `fill` the LARGER of the two axis ratios (what blows a wide file up in
 * a square box), under `contain` the smaller, under `scale-down` the smaller capped at 1, under
 * `none` 1 — times the device pixel ratio. Over 1.05 is a defect. An image clipped out of sight
 * by an overflow ancestor is skipped; a partly clipped one is judged at its scale and reports
 * its visible crop. Advisory: it enters as bsuk-learning-loop Step 4 says.
 */
register({
  id: 'img-not-upscaled',
  family: 'IMG',
  severity: 'advisory',
  describe: 'no image is painted larger than its own pixels (object-fit: cover counted)',
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    await settlePage(page);
    await page.evaluate(async () => {
      const pending = Array.from(document.images).filter((i) => !i.complete);
      await Promise.race([
        Promise.allSettled(pending.map((i) => i.decode().catch(() => null))),
        new Promise((res) => setTimeout(res, 5000)),
      ]);
    });
    const r = await page.evaluate(async () => {
      const dpr = window.devicePixelRatio || 1;
      let examined = 0;
      const bad: string[] = [];
      // The FILE's own pixels. With a w-descriptor srcset, img.naturalWidth is corrected by
      // density (file width x sizes / w), so a 1600px file under sizes="100px" reads 100px:
      // this check's first draft fired on exactly that (known_good/img-not-upscaled.html).
      const own = new Map<string, [number, number]>();
      const pixels = async (src: string): Promise<[number, number]> => {
        if (!own.has(src)) {
          const probe = new Image();
          probe.src = src;
          await probe.decode().catch(() => null);
          own.set(src, [probe.naturalWidth, probe.naturalHeight]);
        }
        return own.get(src)!;
      };
      for (const img of Array.from(document.images)) {
        const box = img.getBoundingClientRect();
        if (box.width < 1 || box.height < 1) continue;
        if (!img.complete || img.naturalWidth === 0 || img.naturalHeight === 0) continue;
        const src = img.currentSrc || img.src || '';
        if (/\.svg(\?|$)/i.test(src) || src.startsWith('data:image/svg')) continue;
        // The VISIBLE crop: the box clipped by every overflow-clipping ancestor. An image
        // clipped out of sight paints nothing and is skipped; a partly clipped one keeps its
        // scale (clipping hides pixels, it does not enlarge them) and reports its visible size.
        let vis = { l: box.left, t: box.top, r: box.right, b: box.bottom };
        for (let e = img.parentElement; e; e = e.parentElement) {
          const o = getComputedStyle(e);
          if (/(hidden|clip|scroll|auto)/.test(o.overflowX + o.overflowY)) {
            const c = e.getBoundingClientRect();
            vis = { l: Math.max(vis.l, c.left), t: Math.max(vis.t, c.top),
              r: Math.min(vis.r, c.right), b: Math.min(vis.b, c.bottom) };
          }
        }
        if (vis.r - vis.l < 1 || vis.b - vis.t < 1) continue;
        const [nw, nh] = await pixels(src);
        if (!nw || !nh) continue;
        examined++;
        // The CONTENT box paints the pixels: padding and border are not image (review
        // 2026-09-28 — a 40px-padded 380px image read 460px, 1.15x, from its border box).
        const cs = getComputedStyle(img);
        const px = (v: string) => parseFloat(v) || 0;
        const cw = box.width - px(cs.paddingLeft) - px(cs.paddingRight)
          - px(cs.borderLeftWidth) - px(cs.borderRightWidth);
        const ch = box.height - px(cs.paddingTop) - px(cs.paddingBottom)
          - px(cs.borderTopWidth) - px(cs.borderBottomWidth);
        if (cw < 1 || ch < 1) continue;
        const fit = cs.objectFit;
        const sw = cw / nw;
        const sh = ch / nh;
        // cover fills the box (the larger ratio); contain letterboxes (the smaller);
        // scale-down is contain but never above 1; none paints the file at its own size;
        // fill stretches each axis, so the larger stretch is the soft one.
        const byFit: Record<string, number> = {
          cover: Math.max(sw, sh), contain: Math.min(sw, sh),
          'scale-down': Math.min(1, Math.min(sw, sh)), none: 1, fill: Math.max(sw, sh),
        };
        const scale = (byFit[fit] ?? Math.max(sw, sh)) * dpr;
        const box_ = { width: cw, height: ch };
        if (scale > 1.05) {
          bad.push(`${src.split('/').pop()} file=${nw}x${nh} ` +
            `painted=${Math.round(box_.width)}x${Math.round(box_.height)} ` +
            `visible=${Math.round(vis.r - vis.l)}x${Math.round(vis.b - vis.t)} ${fit} ${scale.toFixed(2)}x`);
        }
      }
      return { examined, bad: bad.slice(0, 10), count: bad.length };
    });
    const defects = r.count ? [{
      checkId: 'img-not-upscaled',
      family: 'IMG' as const,
      viewport,
      count: r.count,
      message: `${r.count} upscaled image(s): ${r.bad.join(' | ')}`,
    }] : [];
    return { examined: r.examined, defects };
  },
});

register({
  id: 'img-alt-present-and-unique',
  family: 'IMG',
  severity: 'blocking',
  describe: 'every rendered image declares alt; non-decorative alts are unique on the page',
  minExamined: 3,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    await settlePage(page);
    const r = await page.evaluate(() => {
      let examined = 0;
      const missing: string[] = [];
      const seen = new Map<string, number>();
      for (const img of Array.from(document.images)) {
        if (img.getBoundingClientRect().width < 1) continue;
        examined++;
        if (!img.hasAttribute('alt')) {
          missing.push(((img.getAttribute('src') || '(no src)').split('/').pop()) as string);
          continue;
        }
        const alt = (img.getAttribute('alt') || '').trim();
        if (alt === '') continue; // declared decorative — allowed
        seen.set(alt, (seen.get(alt) || 0) + 1);
      }
      const dupes: string[] = [];
      seen.forEach((n, alt) => {
        if (n > 1) dupes.push(`"${alt.slice(0, 48)}" x${n}`);
      });
      // Return the true totals ALONGSIDE the truncated display lists. `count` is the
      // magnitude the ledger ranks families by, so deriving it from a list already
      // sliced for readability would silently cap this check's contribution at 6 —
      // undercounting exactly the field that was just made load-bearing, and doing it
      // invisibly, since a capped number looks like a small problem rather than a
      // truncated one. img-srcset-within-2x already returns a separate `count` for
      // this reason; these two were the stragglers.
      //
      // CORRECTION (2026-08-01): "these two were the stragglers" was false when
      // written. img-srcset-within-2x returned a separate `count` for its OVERSIZED
      // row but derived its decode-failure row's count from `skipped.slice(0, 10)`,
      // so it reported 10 whenever 10 or more images failed. A comment asserting a
      // safety property the code lacks is worse than no comment — it is why that
      // third case survived a dedicated sweep for exactly this defect.
      return {
        examined,
        missing: missing.slice(0, 6),
        missingTotal: missing.length,
        dupes: dupes.slice(0, 6),
        dupesTotal: dupes.length,
      };
    });

    const defects = [];
    if (r.missing.length) {
      defects.push({
        checkId: 'img-alt-present-and-unique',
        family: 'IMG' as const,
        viewport,
        count: r.missingTotal,
        message: `image(s) with no alt attribute: ${r.missing.join(', ')}`,
      });
    }
    if (r.dupes.length) {
      defects.push({
        checkId: 'img-alt-present-and-unique',
        family: 'IMG' as const,
        viewport,
        count: r.dupesTotal,
        message: `duplicate alt text (Rule 50b): ${r.dupes.join(' | ')}`,
      });
    }
    return { examined: r.examined, defects };
  },
});

/**
 * `sizes` IS A PROMISE ABOUT A BOX, AND NOTHING MEASURED IT.
 *
 * `img-srcset-within-2x` reads the candidate the browser CHOSE against the box it painted, so
 * it catches a promise that is too LARGE and only once the chosen candidate is more than twice
 * the box. It is blind to the other half: a `sizes` that UNDER-states the box makes the browser
 * choose a candidate too small, which is a soft photograph rather than a heavy one and reads as
 * a pass on every gate the repo has. It is also blind to an over-statement that happens to land
 * inside 2x, and to the whole middle of the breakpoint range — `/blue-staffy-pup-sale-uk/`'s
 * stacked hero promised 560px for a box that paints 828px at 1280 for six weeks, and
 * `/blue-staffy-uk-breeders/`'s mosaic promised 130px for a 68px tile at 1024, and neither was
 * reportable by anything here.
 *
 * So this measures the promise itself: the `sizes` list is resolved the way the BROWSER
 * resolves it — first matching media condition wins, and the length is handed to the CSS engine
 * rather than parsed, so `calc(52.5vw - 224px)` is evaluated by the thing that will evaluate it
 * in production — and compared against the box the image actually paints.
 *
 * THE WINDOW IS 0.9-1.25x, and it is asymmetric on purpose. Under 0.9 the browser is being told
 * to fetch less than it needs and the photograph is soft; over 1.25 it is being told to fetch
 * more, which is bytes rather than blur and is what a DPR-2 screen partly redeems. A `sizes`
 * cannot be exact at every width — it is a list of bands over a fluid layout — so a window is
 * the honest form of the check, and 1.25 is tight enough that a whole stale breakpoint cannot
 * hide inside it (every stale reading found was 1.35x or worse).
 *
 * HERO PHOTOGRAPHY ONLY. The hero is where `sizes` is written by a COMPONENT rather than beside
 * the image it describes, which is what let one arrangement's column become five arrangements'
 * promise; body images state their own beside their own `srcset`. Both shapes are examined: the
 * single photo IS `.pic`, and a mosaic's tiles are inside it.
 */
register({
  id: 'img-sizes-matches-box',
  family: 'IMG',
  severity: 'blocking',
  describe: "a hero image's sizes must resolve to within 0.9-1.25x of the box it paints",
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    await settlePage(page);
    const r = await page.evaluate(() => {
      // The browser's own rules, in the browser: split the list on TOP-LEVEL commas (a
      // `calc()` or a media condition may hold its own), take the first entry whose media
      // condition matches — a bare length matches unconditionally and is the default — and
      // resolve its length through the CSS engine rather than through a regex, so `100vw`,
      // `calc(50vw - 52px)` and `14rem` all mean here exactly what they will mean in
      // production.
      const split = (list: string): string[] => {
        const out: string[] = [];
        let depth = 0;
        let cur = '';
        for (const ch of list) {
          if (ch === '(') depth++;
          if (ch === ')') depth--;
          if (ch === ',' && depth === 0) { out.push(cur); cur = ''; continue; }
          cur += ch;
        }
        if (cur.trim()) out.push(cur);
        return out.map((s) => s.trim()).filter(Boolean);
      };
      const ruler = document.createElement('div');
      ruler.style.cssText = 'position:absolute;top:0;left:0;visibility:hidden;height:0';
      document.body.appendChild(ruler);
      const toPx = (length: string): number | null => {
        ruler.style.width = '';
        ruler.style.width = length;
        if (!ruler.style.width) return null;
        return ruler.getBoundingClientRect().width;
      };
      const resolve = (list: string): number | null => {
        for (const entry of split(list)) {
          const m = /^(\(.*\))\s+(.+)$/.exec(entry);
          if (!m) return toPx(entry);
          if (window.matchMedia(m[1]).matches) return toPx(m[2]);
        }
        return null;
      };

      const pic = document.querySelector('.kit-hero .pic');
      const imgs: HTMLImageElement[] = [];
      if (pic instanceof HTMLImageElement) imgs.push(pic);
      else if (pic) imgs.push(...Array.from(pic.querySelectorAll('img')));

      let examined = 0;
      const bad: string[] = [];
      const unresolved: string[] = [];
      for (const img of imgs) {
        const list = img.getAttribute('sizes');
        // No `sizes` is not a defect here: an image with one candidate has nothing to choose
        // between, and `img-srcset-within-2x` owns the case where it should have had more.
        if (!list || !img.getAttribute('srcset')) continue;
        const box = img.getBoundingClientRect().width;
        if (box < 1) continue;
        const name = (img.getAttribute('src') || '(no src)').split('/').pop() as string;
        const declared = resolve(list);
        if (declared === null || declared <= 0) {
          unresolved.push(`${name} sizes="${list}"`);
          continue;
        }
        examined++;
        const ratio = declared / box;
        if (ratio < 0.9 || ratio > 1.25) {
          bad.push(`${name} declares ${Math.round(declared)}px, paints ${Math.round(box)}px `
            + `(${ratio.toFixed(2)}x) via sizes="${list}"`);
        }
      }
      ruler.remove();
      return { examined, bad: bad.slice(0, 6), count: bad.length, unresolved };
    });

    const defects = [];
    if (r.count) {
      defects.push({
        checkId: 'img-sizes-matches-box',
        family: 'IMG' as const,
        viewport,
        count: r.count,
        message: `${r.count} hero image(s) whose sizes does not match the box: ${r.bad.join(' | ')}`,
      });
    }
    // A `sizes` the CSS engine will not parse is a `sizes` the browser ignores, which is the
    // same thing as having written none — reported rather than skipped, because skipping it
    // would let a typo buy silence from the very check written to stop that.
    if (r.unresolved.length) {
      defects.push({
        checkId: 'img-sizes-matches-box',
        family: 'IMG' as const,
        viewport,
        count: r.unresolved.length,
        message: `${r.unresolved.length} hero image(s) with a sizes the browser cannot resolve: ${r.unresolved.join(' | ')}`,
      });
    }
    return { examined: r.examined, defects };
  },
});

/**
 * A FACE STAYS IN THE CROP AND CLEAR OF OVERLAYS (rules/puppies.md `no-head-cropped-portraits`;
 * learning loop 2026-09-27, L4 / shortlist #2 — the commonest image defect of the London pass:
 * ~12 crops cut a dog's head or slid a name plate over its face, every one caught by eye).
 *
 * Nothing knew where a face was, so nothing could measure it. data/image-focus.json now records
 * the boxes that must stay whole, per file, in the master's own pixels. For every painted image
 * whose file is recorded (matched by the file's STEM, so an astro:assets rename
 * `Vennie.<hash>.webp` and a baked width sibling `maggie-…-760.webp` both map back to their
 * master), this check computes where each face lands inside the painted crop — `object-fit` and
 * `object-position` as the browser resolved them, on the CONTENT box, clipped by every
 * overflow-clipping ancestor — and then samples the visible face for anything painted over it.
 *   - CROP:    less than 90% of a face is painted.
 *   - OVERLAY: more than 10% of the painted face is covered by another element that paints
 *              something there (a background, an image or its own text). A transparent overlay —
 *              a card's stretched link, say — covers nothing and is not counted; neither is
 *              sticky or fixed chrome, which the image is scrolled clear of before sampling.
 * An unrecorded file is not examined. Advisory: it enters as bsuk-learning-loop Step 4 says.
 */
const FOCUS_ROWS: Record<string, { w: number; h: number; faces: [number, number, number, number][] }> = (() => {
  const file = fileURLToPath(new URL('../../../data/image-focus.json', import.meta.url));
  const rows = JSON.parse(readFileSync(file, 'utf8')).images as Record<string, { w: number; h: number; faces: [number, number, number, number][] }>;
  return Object.fromEntries(Object.entries(rows).map(([name, r]) => [name.replace(/\.[a-z0-9]+$/i, ''), r]));
})();

register({
  id: 'img-face-visible',
  family: 'IMG',
  severity: 'advisory',
  describe: 'every recorded face is at least 90% painted and less than 10% covered',
  minExamined: 1,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    await settlePage(page);
    const r = await page.evaluate((rows) => {
      const stemOf = (src: string) => {
        const name = decodeURIComponent(src.split('?')[0].split('/').pop() || '');
        return name.split('.')[0].replace(/-\d{3,4}$/, '');
      };
      const pos = (token: string, room: number) =>
        token.endsWith('%') ? (parseFloat(token) / 100) * room : parseFloat(token) || 0;
      const chrome = (el: Element | null) => {
        for (let e = el; e; e = e.parentElement) {
          const p = getComputedStyle(e).position;
          if (p === 'fixed' || p === 'sticky') return true;
        }
        return false;
      };
      // Does `el` paint anything at (x, y)? An image, a background — or its own TEXT, where
      // the glyphs actually are: a stretched card link carries text elsewhere in the card and
      // is transparent over the photograph, so it must not count as covering it.
      const paints = (el: Element, x: number, y: number) => {
        const cs = getComputedStyle(el);
        if (el instanceof HTMLImageElement || el instanceof SVGElement || el instanceof HTMLVideoElement) return true;
        if (cs.backgroundImage !== 'none') return true;
        const bg = cs.backgroundColor.match(/[\d.]+/g);
        if (bg && (bg.length < 4 || parseFloat(bg[3]) > 0)) return true;
        return Array.from(el.childNodes).some((n) => {
          if (n.nodeType !== 3 || !(n.textContent || '').trim()) return false;
          const range = document.createRange();
          range.selectNodeContents(n);
          return Array.from(range.getClientRects()).some((q) => x >= q.left && x <= q.right && y >= q.top && y <= q.bottom);
        });
      };
      let examined = 0;
      const bad: string[] = [];
      const y0 = window.scrollY;
      for (const img of Array.from(document.images)) {
        const row = rows[stemOf(img.currentSrc || img.src || '')];
        if (!row) continue;
        img.scrollIntoView({ block: 'center', inline: 'nearest' });
        const box = img.getBoundingClientRect();
        if (box.width < 2 || box.height < 2) continue;
        const cs = getComputedStyle(img);
        if (cs.visibility === 'hidden' || cs.display === 'none') continue;
        const px = (v: string) => parseFloat(v) || 0;
        const cx = box.left + px(cs.borderLeftWidth) + px(cs.paddingLeft);
        const cy = box.top + px(cs.borderTopWidth) + px(cs.paddingTop);
        const cw = box.width - px(cs.paddingLeft) - px(cs.paddingRight) - px(cs.borderLeftWidth) - px(cs.borderRightWidth);
        const ch = box.height - px(cs.paddingTop) - px(cs.paddingBottom) - px(cs.borderTopWidth) - px(cs.borderBottomWidth);
        if (cw < 2 || ch < 2) continue;
        const sw = cw / row.w;
        const sh = ch / row.h;
        const own = (img.naturalWidth || row.w) / row.w;
        const fit = cs.objectFit;
        const s = fit === 'cover' ? Math.max(sw, sh)
          : fit === 'contain' ? Math.min(sw, sh)
          : fit === 'none' ? own
          : fit === 'scale-down' ? Math.min(own, Math.min(sw, sh)) : NaN;
        const [ax, ay] = fit === 'fill' ? [sw, sh] : [s, s];
        const pw = row.w * ax;
        const ph = row.h * ay;
        const [tx, ty = '50%'] = cs.objectPosition.split(/\s+/);
        const ox = cx + pos(tx, cw - pw);
        const oy = cy + pos(ty, ch - ph);
        // The visible crop: the content box, clipped by every overflow-clipping ancestor.
        let vis = { l: cx, t: cy, r: cx + cw, b: cy + ch };
        for (let e = img.parentElement; e; e = e.parentElement) {
          const o = getComputedStyle(e);
          if (/(hidden|clip|scroll|auto)/.test(o.overflowX + o.overflowY)) {
            const c = e.getBoundingClientRect();
            vis = { l: Math.max(vis.l, c.left), t: Math.max(vis.t, c.top), r: Math.min(vis.r, c.right), b: Math.min(vis.b, c.bottom) };
          }
        }
        examined++;
        const name = stemOf(img.currentSrc || img.src);
        row.faces.forEach(([fx, fy, fw, fh], k) => {
          const f = { l: ox + fx * ax, t: oy + fy * ay, r: ox + (fx + fw) * ax, b: oy + (fy + fh) * ay };
          const v = { l: Math.max(f.l, vis.l), t: Math.max(f.t, vis.t), r: Math.min(f.r, vis.r), b: Math.min(f.b, vis.b) };
          const area = (x: typeof f) => Math.max(0, x.r - x.l) * Math.max(0, x.b - x.t);
          const shown = area(f) ? area(v) / area(f) : 0;
          if (shown < 0.9) {
            bad.push(`${name} face ${k + 1}: ${Math.round(shown * 100)}% painted in a ${Math.round(cw)}x${Math.round(ch)} ${fit} crop`);
            return;
          }
          // Sample the painted face on a 6x6 grid for anything painted over the image.
          let covered = 0;
          let samples = 0;
          for (let i = 0; i < 6; i++) {
            for (let j = 0; j < 6; j++) {
              const x = v.l + ((i + 0.5) / 6) * (v.r - v.l);
              const y = v.t + ((j + 0.5) / 6) * (v.b - v.t);
              if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) continue;
              samples++;
              const top = document.elementsFromPoint(x, y).find((el) => !chrome(el) && paints(el, x, y));
              if (top && top !== img && !top.contains(img)) covered++;
            }
          }
          if (samples && covered / samples > 0.1) {
            bad.push(`${name} face ${k + 1}: ${Math.round((100 * covered) / samples)}% covered by an overlay`);
          }
        });
      }
      window.scrollTo(0, y0);
      return { examined, bad: bad.slice(0, 10), count: bad.length };
    }, FOCUS_ROWS);
    const defects = r.count ? [{
      checkId: 'img-face-visible',
      family: 'IMG' as const,
      viewport,
      count: r.count,
      message: `${r.count} face(s) cropped or covered: ${r.bad.join(' | ')}`,
    }] : [];
    return { examined: r.examined, defects };
  },
});
