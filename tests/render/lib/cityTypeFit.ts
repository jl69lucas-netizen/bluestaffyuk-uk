/**
 * The city type-fit check (the London component design pass, Plan 2; Task 7b item 10, the
 * user's ruling of 2026-09-28: "all font/text, headers, body texts … must fit well, no big
 * headers, nice even paragraphs … No chunky title or long/tall sections/paragraphs").
 *
 * It runs INSIDE the page (pass `cityTypeFit` to `page.evaluate` with the viewport) and judges
 * every `.city-kit` section on it, so a gate — not an eye — holds the type:
 *   1. every h1/h2/h3 is at or below its tier's cap and wraps to three lines or fewer;
 *   1b. at the desktop tier, no section H2 wraps to three lines while its section's content box is
 *      700px or more: a short question stacked into a tall, chunky block beside empty space is a
 *      defect WHATEVER the cause (the user's ruling, answer board q06, 2026-09-29). The message
 *      names the cause: "heading measure too narrow for its box" where the measure binds (lifting
 *      it widens the H2; src/styles/city.css sets it per tier, 22 / 28 / 34ch), "heading column
 *      too narrow for its box" where the layout's column is what wraps it (the takeaways' old 5fr
 *      head column, which this check used to excuse);
 *   2. no paragraph is wider than 75ch of its own font;
 *   3. no paragraph runs more than 8 lines below a 1024px viewport, or 6 from 1024;
 *   4. no section is taller than 2.5 viewports at a phone width (below 768) or 1.6 viewports
 *      from 1280.
 * A heading's tier is its section's: the content box of its `.city-kit` root, against the edges
 * the caller passes (tests/render/lib/cityTiers.ts, read from src/lib/cityKit.ts TIER: phone
 * below 640px, tablet from 640, desktop from 800 — the edges src/styles/city.css switches type
 * AND layout on). city-layout-follows-box reads the same box. Only painted elements are judged.
 *
 * EXEMPTIONS, each named with its reason, never by pattern:
 *   - a form ROW: a `form p` that holds a control or its label (`p.field`, label over control)
 *     is layout, not reading text. A form's TEXT paragraph (the privacy note) is NOT exempt: the
 *     blanket `form p` skip hid it at 76ch on London (visual-intelligence audit 2026-10-04).
 *     A review is NOT exempt: CityLetter splits it into paragraphs at its sentence breaks, words
 *     and order untouched, so it is held to the same line caps as any other paragraph;
 *   - `[data-city-jump-stepper]` and `[data-city-dial-photo-marker]`: sticky nav furniture, whose
 *     height is the page's section list, not reading text (the sheet is a closed dialog);
 *   - the puppy sheet's HEIGHT only, and only on the full-width specimen route /kit-preview/city/
 *     (the caller says so: `fullWidthSpecimen`), which no city page reproduces — a city page's
 *     body column is 832px at most. There the six prints are three to a row at about 360px each,
 *     and a print is the puppy's photograph at the size a buyer judges it by; on
 *     /kit-preview/city-page/ and every real city page the sheet is held to 1.6 viewports.
 *     The roster needs no exemption.
 * Fixtures: tests/render/fixtures/city/type-fit-{broken,good}.html, judged in city-kit.spec.ts.
 */
export interface TypeFitResult { examined: number; defects: string[] }

export function cityTypeFit({ viewport, tier: edges, caps: CAP, fullWidthSpecimen = false }:
  { viewport: number; tier: { tablet: number; desktop: number };
    caps: Record<string, [number, number, number]>; fullWidthSpecimen?: boolean }): TypeFitResult {
  // CAP is HEADING_CAPS from tests/render/lib/cityTiers.ts, passed in by the caller (this runs
  // inside the page, so it cannot import it): one table for the city and the built pages.
  const TIER = ['phone', 'tablet', 'desktop'];
  // 1b: a desktop-tier section at least this wide has room for a section H2 on two lines.
  const NARROW_BOX = 700;
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
    const tier = w >= edges.desktop ? 2 : w >= edges.tablet ? 1 : 0;
    const where = `${(root.className.match(/city-[a-z-]+/g) ?? ['city-kit']).filter((c) => c !== 'city-kit')[0]} (${Math.round(w)}px, ${TIER[tier]})`;
    for (const h of Array.from(root.querySelectorAll('h1, h2, h3')).filter(painted)) {
      examined++;
      const fs = parseFloat(getComputedStyle(h).fontSize);
      const cap = CAP[h.tagName][tier];
      if (fs > cap + 0.5) defects.push(`${where}: ${h.tagName} "${name(h)}" is ${fs}px, over the ${TIER[tier]} cap of ${cap}px`);
      const n = lines(h);
      if (n > 3) defects.push(`${where}: ${h.tagName} "${name(h)}" wraps to ${n} lines`);
      if (h.tagName === 'H2' && tier === 2 && w >= NARROW_BOX && n >= 3) {
        // Every such H2 is a defect (q06); the message names the cause. Its room is read by
        // lifting the measure for one layout (a grid item's room is its area, not its parent's
        // box), then restoring the inline style exactly.
        const el = h as HTMLElement;
        const width = el.getBoundingClientRect().width;
        const before = el.style.maxInlineSize;
        el.style.maxInlineSize = 'none';
        const room = el.getBoundingClientRect().width;
        el.style.maxInlineSize = before;
        const cause = room - width > 8 ? 'heading measure too narrow for its box' : 'heading column too narrow for its box';
        defects.push(`${where}: H2 "${name(h)}" wraps to ${n} lines at ${Math.round(width)}px with ${Math.round(room)}px of room in a ${Math.round(w)}px box: ${cause}`);
      }
    }
    for (const p of Array.from(root.querySelectorAll('p')).filter(painted)) {
      // A form ROW (a paragraph that holds a control or its label) is layout; a form's TEXT
      // paragraph, the privacy note, is reading text and keeps the measure. The old blanket
      // `form p` skip hid the note at 76ch on London (visual-intelligence audit 2026-10-04).
      if (p.closest('form') && p.querySelector('input, select, textarea, label, button')) continue;
      examined++;
      const ch = chOf(p);
      const pw = contentWidth(p);
      if (ch > 0 && pw / ch > 75.5) defects.push(`${where}: a paragraph "${name(p)}" is ${Math.round(pw / ch)}ch wide (75 max)`);
      const n = lines(p);
      const max = viewport >= 1024 ? 6 : 8;
      if (n > max) defects.push(`${where}: a paragraph "${name(p)}" runs ${n} lines (${max} max at ${viewport}px)`);
    }
    const tall = viewport < 768 ? 2.5 : viewport >= 1280 ? 1.6 : Infinity;
    const sheetFullWidth = fullWidthSpecimen && root.matches('.city-sheet');
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
