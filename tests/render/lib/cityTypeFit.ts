/**
 * The city type-fit check (the London component design pass, Plan 2; Task 7b item 10, the
 * user's ruling of 2026-09-28: "all font/text, headers, body texts … must fit well, no big
 * headers, nice even paragraphs … No chunky title or long/tall sections/paragraphs").
 *
 * It runs INSIDE the page (pass `cityTypeFit` to `page.evaluate` with the viewport) and judges
 * every `.city-kit` section on it, so a gate — not an eye — holds the type:
 *   1. every h1/h2/h3 is at or below its tier's cap and wraps to three lines or fewer;
 *   2. no paragraph is wider than 75ch of its own font;
 *   3. no paragraph runs more than 8 lines below a 1024px viewport, or 6 from 1024;
 *   4. no section is taller than 2.5 viewports at a phone width (below 768) or 1.6 viewports
 *      from 1280.
 * A heading's tier is its section's: the content box of the nearest `.city-kit` root — phone
 * below 600px, tablet from 600, desktop from 780 (the tiers the city type scale in
 * src/styles/kit.css switches on). Only painted elements are judged.
 *
 * EXEMPTIONS, each named with its reason, never by pattern:
 *   - a `blockquote p`: a review is data/reviews.json word for word (seo-rules, the letter),
 *     so its length is the reviewer's, not a layout choice;
 *   - `[data-city-jump-stepper]` and `[data-city-dial-photo-marker]`: sticky nav furniture, whose
 *     height is the page's section list, not reading text (the sheet is a closed dialog);
 *   - the puppy sheet's HEIGHT only, and only in a box of 1000px or more — the full-width specimen
 *     on /kit-preview/city/, which no city page produces (its body column is 832px at most). There
 *     the six prints are three to a row at about 360px each, and a print is the puppy's photograph
 *     at the size a buyer judges it by; in the column the same sheet is held to 1.6 viewports.
 *     The roster needs no exemption.
 * Fixtures: tests/render/fixtures/city/type-fit-{broken,good}.html, judged in city-kit.spec.ts.
 */
export interface TypeFitResult { examined: number; defects: string[] }

export function cityTypeFit(viewport: number): TypeFitResult {
  const CAP: Record<string, [number, number, number]> = { H1: [26, 30, 34], H2: [22, 25, 28], H3: [17, 18, 20] };
  const TIER = ['phone', 'tablet', 'desktop'];
  const defects: string[] = [];
  let examined = 0;
  const painted = (el: Element) => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
  };
  const lines = (el: Element) => {
    const range = document.createRange();
    range.selectNodeContents(el);
    const tops = new Set<number>();
    for (const r of Array.from(range.getClientRects())) if (r.width > 0 && r.height > 0) tops.add(Math.round(r.bottom));
    // Two fragments on one line share a baseline within a pixel or two: merge near-equal bottoms.
    const sorted = [...tops].sort((a, b) => a - b);
    return sorted.filter((t, i) => i === 0 || t - sorted[i - 1] > 3).length;
  };
  const contentWidth = (el: Element) => {
    const s = getComputedStyle(el);
    return (el as HTMLElement).clientWidth - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight);
  };
  const chOf = (el: Element) => {
    const probe = document.createElement('span');
    probe.textContent = '0000000000';
    probe.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap';
    el.appendChild(probe);
    const w = probe.getBoundingClientRect().width / 10;
    probe.remove();
    return w;
  };
  const name = (el: Element) => (el.textContent ?? '').trim().replace(/\s+/g, ' ').slice(0, 40);
  const skipRoot = (root: Element) => root.matches('[data-city-jump-stepper], [data-city-dial-photo-marker]');
  const roots = Array.from(document.querySelectorAll('.city-kit')).filter((r) => painted(r) && !skipRoot(r));
  for (const root of roots) {
    const w = contentWidth(root);
    const tier = w >= 780 ? 2 : w >= 600 ? 1 : 0;
    const where = `${(root.className.match(/city-[a-z-]+/g) ?? ['city-kit']).filter((c) => c !== 'city-kit')[0]} (${Math.round(w)}px, ${TIER[tier]})`;
    for (const h of Array.from(root.querySelectorAll('h1, h2, h3')).filter(painted)) {
      examined++;
      const fs = parseFloat(getComputedStyle(h).fontSize);
      const cap = CAP[h.tagName][tier];
      if (fs > cap + 0.5) defects.push(`${where}: ${h.tagName} "${name(h)}" is ${fs}px, over the ${TIER[tier]} cap of ${cap}px`);
      const n = lines(h);
      if (n > 3) defects.push(`${where}: ${h.tagName} "${name(h)}" wraps to ${n} lines`);
    }
    for (const p of Array.from(root.querySelectorAll('p')).filter(painted)) {
      if (p.closest('blockquote')) continue;
      examined++;
      const ch = chOf(p);
      const pw = contentWidth(p);
      if (ch > 0 && pw / ch > 75.5) defects.push(`${where}: a paragraph "${name(p)}" is ${Math.round(pw / ch)}ch wide (75 max)`);
      const n = lines(p);
      const max = viewport >= 1024 ? 6 : 8;
      if (n > max) defects.push(`${where}: a paragraph "${name(p)}" runs ${n} lines (${max} max at ${viewport}px)`);
    }
    const tall = viewport < 768 ? 2.5 : viewport >= 1280 ? 1.6 : Infinity;
    const sheetFullWidth = root.matches('.city-sheet') && w >= 1000;
    if (Number.isFinite(tall) && !sheetFullWidth) {
      examined++;
      const h = root.getBoundingClientRect().height;
      if (h > tall * window.innerHeight) {
        defects.push(`${where}: the section is ${Math.round(h)}px tall, over ${tall} viewports (${Math.round(tall * window.innerHeight)}px)`);
      }
    }
  }
  return { examined, defects };
}
