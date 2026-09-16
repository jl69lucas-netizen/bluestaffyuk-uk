import { register, type CheckResult } from '../lib/registry.js';
import type { Page } from '@playwright/test';

/**
 * A11Y family. Contrast is computed from RENDERED colours, never from source.
 *
 * The bug class this exists for is "component re-themed, child not": `.bpair` flipped the
 * dial to a white bed and `.ti` kept its dark-theme sage `#7ba98d` — 2.66:1, ten Lighthouse
 * failures on 2026-08-07. A source grep cannot see that, because neither declaration is
 * wrong on its own; only the composed result is. See reference_markup_css_drift.
 *
 * What it deliberately does NOT judge, because it cannot do so honestly:
 *  - text over a background-image or gradient (no single backdrop colour exists)
 *  - text over a semi-transparent layer (the composite depends on paint order)
 *  - zero-area, hidden, or fully-transparent elements
 * Skipping is not the same as passing: skipped elements are excluded from `examined`, so
 * the count reports what the predicate actually ran against.
 */
register({
  id: 'a11y-text-contrast-aa',
  family: 'A11Y',
  // ADVISORY, not blocking — 2026-08-08, breeder decision, per the promotion rule in
  // targets.json: a check is promoted once it has passed its fixtures AND produced zero
  // false reports across one full cluster. This one shipped 2026-08-07 declared blocking
  // on day one, which skipped that bar; its two same-day siblings
  // (layout-hero-counter-separation, layout-h3-image-first) correctly entered advisory.
  //
  // Wiring it in (it had been running on ZERO pages — see targets.json) produced 1,783
  // reports across 45 of 45 page-viewports, 0 clean. Two false-positive classes are
  // confirmed and MUST be fixed before promotion:
  //  1. Out-of-flow labels over photos (.rbadge, .absolute.top-3) report ~1:1. They are
  //     position:absolute with background:none and a dark text-shadow, sitting over an
  //     image; backdrop() walks DOM ancestors, never meets the photo, and compares white
  //     against the white section behind it. The check already declines to judge text
  //     over a background-image — it just cannot detect that case out of flow.
  //  2. Translucent FOREGROUNDS (e.g. Tailwind text-cream/80) — now handled: rgb() returns
  //     null (not judged) for any foreground with alpha < 1, the same "not judgeable"
  //     treatment the translucent BACKDROP already gets.
  // A third, likely-real family also surfaced: clay/gold on light at 3.17–3.38:1.
  // Triage is its own sprint. reference_registered_is_not_wired.
  severity: 'advisory',
  describe: 'rendered text must meet WCAG AA contrast against its own backdrop',
  // The known_broken fixture carries 6 judgeable spans (2 × .ti sage-on-white, 2 × .tt
  // dark-on-white, 2 × .nav-green .dim opaque-oklab-on-green — 4 failing, 2 passing); the
  // floor is set to that so the check cannot pass the meta gate by judging one element and
  // skipping the rest. reference_promote_check_needs_examined_count.
  minExamined: 6,
  async run(page: Page, viewport: number): Promise<CheckResult> {
    const r = await page.evaluate(() => {
      // getComputedStyle (and canvas fillStyle read back as a string) both preserve oklab()/
      // oklch()/color() verbatim instead of normalising to rgb() — regex-mining digits out
      // of "oklab(0.97 0 0 / .85)" read it as rgb(0.97,0,0), a false near-black (44 rows on
      // /). A canvas PIXEL READBACK is the only honest normaliser: fillRect + getImageData
      // always resolves any <color> notation to real sRGB bytes (and unpremultiplied alpha),
      // regardless of the source syntax.
      const px = document.createElement('canvas');
      px.width = 1;
      px.height = 1;
      const cvs = px.getContext('2d', { willReadFrequently: true })!;
      // ~2,700 nodes × ancestor walks per viewport; a page uses tens of distinct colour
      // strings, not thousands.
      const colourCache = new Map<string, number[] | null>();
      /** Normalised [r, g, b, a] where a is 0–255, or null when unparsable. */
      const rgba = (s: string): number[] | null => {
        if (!s || s === 'transparent') return null;
        const cached = colourCache.get(s);
        if (cached !== undefined) return cached ? cached.slice() : cached;
        cvs.clearRect(0, 0, 1, 1);
        try {
          cvs.fillStyle = s;
        } catch {
          // canvas ignores an unparsable colour silently rather than throwing in practice —
          // this catch is defensive, not load-bearing.
          colourCache.set(s, null);
          return null;
        }
        cvs.fillRect(0, 0, 1, 1);
        const result = Array.from(cvs.getImageData(0, 0, 1, 1).data);
        colourCache.set(s, result);
        return result.slice();
      };
      const rgb = (s: string): number[] | null => {
        const c = rgba(s);
        if (!c) return null;
        if (c[3] === 0) return null; // fully transparent
        if (c[3] < 255) return null; // translucent foreground: not judgeable (see header note 2)
        return c.slice(0, 3);
      };
      const lum = (c: number[]) => {
        const [r, g, b] = c.map((v) => {
          const x = v / 255;
          return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
      };

      /** The nearest OPAQUE backdrop, or null when no honest answer exists. */
      const backdrop = (el: Element): number[] | null => {
        let n: Element | null = el;
        while (n && n !== document.documentElement) {
          const cs = getComputedStyle(n);
          if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
          const parts = rgba(cs.backgroundColor);
          if (parts) {
            if (parts[3] === 255) return parts.slice(0, 3);
            if (parts[3] > 0) return null; // translucent layer — composite is paint-order dependent
          }
          n = n.parentElement;
        }
        const root = rgba(getComputedStyle(document.documentElement).backgroundColor);
        return root && root[3] === 255 ? root.slice(0, 3) : [255, 255, 255];
      };

      const fails: { sel: string; text: string; ratio: number; need: number }[] = [];
      let examined = 0;

      for (const el of Array.from(document.body.querySelectorAll('*'))) {
        // Only elements with their OWN text. Judging containers would count the same
        // string once per ancestor and inflate the count with units never evaluated.
        const own = Array.from(el.childNodes)
          .filter((n) => n.nodeType === 3 && (n.textContent ?? '').trim().length > 0)
          .map((n) => (n.textContent ?? '').trim())
          .join(' ');
        if (!own) continue;

        const cs = getComputedStyle(el);
        if (cs.visibility === 'hidden' || cs.display === 'none' || Number(cs.opacity) === 0) continue;
        const box = (el as HTMLElement).getBoundingClientRect();
        if (box.width === 0 || box.height === 0) continue;

        const fg = rgb(cs.color);
        if (!fg) continue;
        const bg = backdrop(el);
        if (!bg) continue; // image/gradient/translucent backdrop — not judgeable

        const size = parseFloat(cs.fontSize);
        const weight = Number(cs.fontWeight) || 400;
        const large = size >= 24 || (size >= 18.66 && weight >= 700);
        const need = large ? 3 : 4.5;

        const lf = lum(fg);
        const lb = lum(bg);
        const ratio = (Math.max(lf, lb) + 0.05) / (Math.min(lf, lb) + 0.05);
        examined++;

        if (ratio < need - 0.005) {
          const cls =
            typeof el.className === 'string' && el.className.trim()
              ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.')
              : el.tagName.toLowerCase();
          fails.push({ sel: cls, text: own.slice(0, 24), ratio: Math.round(ratio * 100) / 100, need });
        }
      }
      return { examined, fails: fails.slice(0, 6), total: fails.length };
    });

    return {
      examined: r.examined,
      defects: r.total
        ? [
            {
              checkId: 'a11y-text-contrast-aa',
              family: 'A11Y' as const,
              viewport,
              count: r.total,
              message: `${r.total} text node(s) below AA: ${r.fails
                .map((f) => `${f.sel} "${f.text}" ${f.ratio}:1 (needs ${f.need})`)
                .join(' | ')}`,
            },
          ]
        : [],
    };
  },
});
