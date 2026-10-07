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
 * (`page.evaluate(cityLayoutFollowsBox, { viewport, tier, absent })`).
 *
 * `absent` (2026-10-04): the SPEC keys the CALLER says this page does not carry, each with its
 * reason. Every key was required on every route, which held while the London scaffold mounted all
 * fifteen picks; the page written from its approved board (9b00c855) carries no puppy sheet and no
 * video panel, so `.city-sheet` and `.city-video` were reported missing at every width on a page
 * that is right. The caller derives the list from the page's board record (a key whose component
 * the board does not mount; tests/render/city-kit.spec.ts `absentFor`), never by hand, so a key
 * whose component IS on the board and matches nothing is still a defect, and a key declared absent
 * that the page DOES carry is a defect too (a stale declaration).
 */
export interface LayoutResult { examined: number; defects: string[] }

export function cityLayoutFollowsBox({ viewport, tier: edges, absent = {} }:
  { viewport: number; tier: { tablet: number; desktop: number }; absent?: Record<string, string> }): LayoutResult {
  type Fact = ['beside', string, string] | ['under', string, string] | ['row', string, number] | ['square', string] | ['fill', string, string];
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
    // From a 640px box a chapter opens on one row, its heading beside its photo, and the prose
    // runs under that row from the heading's edge (impeccable D1, the breeder's ruling 2026-10-03).
    // A wide chapter (an infographic) is one column at every width, so the root is a section with
    // at least one chapter that is not.
    '.city-chapters:has(.ch:not(.wide))': {
      tablet: [['beside', '.ch:not(.wide) h3', '.ch:not(.wide) :is(.media, .media-u)'], ['under', '.ch:not(.wide) :is(.media, .media-u)', '.ch:not(.wide) .txt']],
      desktop: [['beside', '.ch:not(.wide) h3', '.ch:not(.wide) :is(.media, .media-u)'], ['under', '.ch:not(.wide) :is(.media, .media-u)', '.ch:not(.wide) .txt']],
    },
    '.city-letter': { tablet: [], desktop: [['beside', '.pic', 'blockquote']] },
    '.city-faq.has-rail': { tablet: [], desktop: [['beside', '.rail', '.blk']] },
    '.city-newsletter-notice': { tablet: [['beside', 'figure', '.body']], desktop: [['beside', 'figure', '.body']] },
    '.city-contact': {
      tablet: [['row', '.pups li', 6], ['row', '.field', 2], ['fill', '.field.wide', 'form']],
      desktop: [['row', '.pups li', 6], ['row', '.field', 3], ['fill', '.field.wide', 'form']],
    },
    // Manchester's own in-body components (the Manchester page run, Phase F Task 30). The tick
    // card: from a 640px box its title and answer sit side by side and the ticks run two to a row.
    '.city-tick-card': {
      tablet: [['beside', '.ttl', '.lede'], ['row', '[data-takeaway]', 2]],
      desktop: [['beside', '.ttl', '.lede'], ['row', '[data-takeaway]', 2]],
    },
    // The photo shelf is a table from a 640px box (rule 13 stacks it below): the photo-led row
    // header and its three cells side by side, the pup's photo beside its name, under a painted head.
    '.city-photo-shelf': {
      tablet: [['row', 'tbody tr:first-child > *', 4], ['beside', 'tbody tr:first-child .who img', 'tbody tr:first-child .nm']],
      desktop: [['row', 'tbody tr:first-child > *', 4], ['beside', 'tbody tr:first-child .who img', 'tbody tr:first-child .nm'], ['row', 'thead th', 4]],
    },
    // The offset sheet: its four facts a two-by-two sheet from a 640px box, and from a desktop box
    // the photo on its bleed beside the copy (a 656px column at 1024 keeps them stacked).
    '.city-offset-sheet': {
      tablet: [['row', '.cell', 2]],
      desktop: [['row', '.cell', 2], ['beside', '.media', '.copy']],
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
    if (sel in absent) {
      if (roots.length) defects.push(`${sel} is declared absent (${absent[sel]}) but the page carries it`);
      continue;
    }
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
        } else if (f[0] === 'under') {
          // b starts below a's foot and reaches back past a's left edge: a full row under it,
          // not a column beside it.
          const a = root.querySelector(f[1]); const b = root.querySelector(f[2]);
          if (!a || !b) { defects.push(`${at}: ${f[1]} or ${f[2]} missing`); continue; }
          const ra = a.getBoundingClientRect(); const rb = b.getBoundingClientRect();
          if (!(rb.top >= ra.bottom - 1 && rb.left < ra.left - 1)) defects.push(`${at}: ${f[2]} does not run under ${f[1]}`);
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

/**
 * The kit component each SPEC key above stands for (its id in src/components/kit/_registry.ts and
 * in a board record's `sections[].component`). Node side only: the caller reads a page's board
 * record and passes, as `absent`, every key whose component the board does not mount.
 * tests/render/city-kit.spec.ts holds this list to the SPEC keys in the function's own source.
 */
export const SPEC_COMPONENT: Record<string, string> = {
  '.city-takeaways-ledger': 'city-takeaways-ledger',
  '.city-sheet': 'city-puppy-sheet',
  '.city-roster': 'city-roster',
  '.city-video': 'city-video-panel',
  '.city-chapters:has(.ch:not(.wide))': 'city-chapters',
  '.city-letter': 'city-letter',
  '.city-faq.has-rail': 'city-faq-ledger',
  '.city-newsletter-notice': 'city-newsletter-notice',
  '.city-contact': 'city-contact-lineup',
  '.city-tick-card': 'city-tick-card',
  '.city-photo-shelf': 'city-photo-shelf',
  '.city-offset-sheet': 'city-offset-sheet',
};

/** `absent` for a page from its board record: each SPEC key whose component the board mounts on
 *  no section, with the reason. A route with no board (the specimen routes) declares nothing.
 *  `keys` limits the judgement to the page's own city's keys (the Manchester page run, Task 30):
 *  another city's components are declared absent by the caller for that reason, not the board's. */
export function absentFromBoard(board: { meta: { slug: string }; sections: { component?: string }[] } | null,
  keys: string[] = Object.keys(SPEC_COMPONENT)): Record<string, string> {
  if (!board) return {};
  const mounted = new Set(board.sections.map((s) => s.component));
  return Object.fromEntries(Object.entries(SPEC_COMPONENT).filter(([k, c]) => keys.includes(k) && !mounted.has(c))
    .map(([sel, c]) => [sel, `data/boards/${board.meta.slug}.json mounts no ${c}`]));
}
