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
     * (congo-pair, 58 images) the eager `decoding="async"` hero candidate was still in
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
