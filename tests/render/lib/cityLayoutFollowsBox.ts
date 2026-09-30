/**
 * city-layout-follows-box (the Task 7b review, item 1; hardened by the quality review, I3).
 *
 * The in-body city components are containers, and on a city page the body is the column beside
 * the dial (656px at 1024, 832px at 1280), so a tier set for the canvas's full-width 1024 was never
 * reached there. Each component's tier follows ITS OWN BOX — the root's content box, the same box
 * cityTypeFit reads, against the same edges (tests/render/lib/cityTiers.ts) — and this reads the
 * tier from the box and asserts the layout facts of that tier: two parts side by side, items to a
 * row, the square print, a full-width row that really fills its box.
 *
 * It cannot pass having examined nothing: it returns the number of facts it judged, the caller
 * treats zero at 768px and up as a defect, every SPEC key that matches no root on the page is a
 * defect, and a fact whose node is missing is a defect, never a skip. Runs INSIDE the page
 * (`page.evaluate(cityLayoutFollowsBox, { viewport, tier })`).
 */
export interface LayoutResult { examined: number; defects: string[] }

export function cityLayoutFollowsBox({ viewport, tier: edges }:
  { viewport: number; tier: { tablet: number; desktop: number } }): LayoutResult {
  type Fact = ['beside', string, string] | ['row', string, number] | ['square', string] | ['fill', string, string];
  const SPEC: Record<string, { tablet: Fact[]; desktop: Fact[] }> = {
    '.city-takeaways-ledger': { tablet: [['beside', '.row dt', '.row dd']], desktop: [['beside', '.pic', 'dl']] },
    '.city-sheet': { tablet: [['row', '.city-pup', 3]], desktop: [['row', '.city-pup', 3], ['square', '.city-pup img']] },
    // A table from a 640px box (rule 13 stacks it below): the five cells of a row side by side,
    // under a painted head. Phone boxes are held by layout-table-stacks-on-mobile.
    '.city-roster': {
      tablet: [['row', 'tbody tr:first-child > *', 5], ['beside', 'tbody tr:first-child th', 'tbody tr:first-child td.num']],
      desktop: [['row', 'tbody tr:first-child > *', 5], ['beside', 'tbody tr:first-child th', 'tbody tr:first-child td.num'], ['row', 'thead th', 5]],
    },
    '.city-video': { tablet: [['beside', '.side > img', '.facts']], desktop: [['beside', '.grid > .kit-video', '.side']] },
    '.city-chapters': { tablet: [['beside', '.ch .media', '.ch p']], desktop: [['beside', '.ch h3', '.ch .media'], ['beside', '.ch .media', '.ch p']] },
    '.city-letter': { tablet: [], desktop: [['beside', '.pic', 'blockquote']] },
    '.city-faq.has-rail': { tablet: [], desktop: [['beside', '.rail', '.blk']] },
    '.city-newsletter-notice': { tablet: [['beside', 'figure', '.body']], desktop: [['beside', 'figure', '.body']] },
    '.city-contact': {
      tablet: [['row', '.pups li', 6], ['row', '.field', 2], ['fill', '.field.wide', 'form']],
      desktop: [['row', '.pups li', 6], ['row', '.field', 3], ['fill', '.field.wide', 'form']],
    },
  };
  const contentWidth = (el: Element) => {
    const s = getComputedStyle(el);
    return (el as HTMLElement).clientWidth - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight);
  };
  const defects: string[] = [];
  let examined = 0;
  for (const [sel, tiers] of Object.entries(SPEC)) {
    const roots = Array.from(document.querySelectorAll<HTMLElement>(sel));
    if (!roots.length) { defects.push(`${sel} matches no section on the page`); continue; }
    for (const root of roots) {
      const w = contentWidth(root);
      const tier = w >= edges.desktop ? 'desktop' : w >= edges.tablet ? 'tablet' : null;
      if (!tier) continue;
      const at = `${sel} (${Math.round(w)}px box, ${tier})`;
      for (const f of tiers[tier]) {
        examined++;
        if (f[0] === 'beside') {
          const a = root.querySelector(f[1]); const b = root.querySelector(f[2]);
          if (!a || !b) { defects.push(`${at}: ${f[1]} or ${f[2]} missing`); continue; }
          const ra = a.getBoundingClientRect(); const rb = b.getBoundingClientRect();
          if (!(ra.right <= rb.left + 1 && ra.top < rb.bottom && rb.top < ra.bottom)) defects.push(`${at}: ${f[1]} is not beside ${f[2]}`);
        } else if (f[0] === 'row') {
          const els = Array.from(root.querySelectorAll(f[1])).filter((e) => e.getBoundingClientRect().height > 0);
          if (!els.length) { defects.push(`${at}: ${f[1]} missing`); continue; }
          const top = els[0].getBoundingClientRect().top;
          const n = els.filter((e) => Math.abs(e.getBoundingClientRect().top - top) < 2).length;
          if (n !== f[2]) defects.push(`${at}: ${n} ${f[1]} to the first row, not ${f[2]}`);
        } else if (f[0] === 'fill') {
          // A full-width row really runs the width of its box (the 65ch paragraph measure once
          // caught the message field, a <p>, at 549px: the Task 7b design pass).
          const el = root.querySelector(f[1]); const box = root.querySelector(f[2]);
          if (!el || !box) { defects.push(`${at}: ${f[1]} or ${f[2]} missing`); continue; }
          if (el.getBoundingClientRect().width < box.clientWidth - 2) {
            defects.push(`${at}: ${f[1]} is ${Math.round(el.getBoundingClientRect().width)}px of its ${box.clientWidth}px ${f[2]}`);
          }
        } else {
          const el = root.querySelector(f[1]);
          if (!el) { defects.push(`${at}: ${f[1]} missing`); continue; }
          const r = el.getBoundingClientRect();
          if (Math.abs(r.width - r.height) > 2) defects.push(`${at}: ${f[1]} is ${Math.round(r.width)}×${Math.round(r.height)}, not square`);
        }
      }
    }
  }
  if (viewport >= 768 && examined === 0) defects.push(`examined no layout fact at ${viewport}px, where every section is tablet or desktop`);
  return { examined, defects };
}
