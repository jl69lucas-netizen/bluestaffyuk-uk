// src/lib/globalCta.ts — does this page's footer render the site-wide CTA band?
//
// Every board record carries `brief.cta.global_cta` ("hidden" | "shown"), and the board
// Artifact shows the breeder that choice in words ("the site-wide CTA band is hidden on this
// page"). Until 2026-09-26 nothing read it: SiteFooterKit rendered its band on every page,
// so eleven approved boards disagreed with their built pages (CAG parity audit D3). The
// record is the page's own approved board, found by route the way scripts/pageboard.py's
// slug_file() names it: `/` is `index`, and a nested route's `/` is flattened to `--`.
// Only an APPROVED record counts; a page with no approved board keeps the band.
// tests/py/test_global_cta.py.
type BoardCta = { approval?: unknown; brief?: { cta?: { global_cta?: string } } };

const RECORDS = import.meta.glob<BoardCta>('../../data/boards/*.json', { eager: true, import: 'default' });

export const boardSlugFor = (pathname: string): string => {
  const slug = pathname.replace(/^\/+|\/+$/g, '');
  return slug === '' ? 'index' : slug;
};

export function globalCtaShown(pathname: string): boolean {
  const file = `../../data/boards/${boardSlugFor(pathname).replace(/\//g, '--')}.json`;
  const record = RECORDS[file];
  if (!record || !record.approval) return true;
  return record.brief?.cta?.global_cta !== 'hidden';
}
