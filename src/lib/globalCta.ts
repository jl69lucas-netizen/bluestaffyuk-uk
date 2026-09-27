// src/lib/globalCta.ts — does this page's footer render the site-wide CTA band?
//
// Every board record carries `brief.cta.global_cta` ("hidden" | "shown"), and the board
// Artifact shows the breeder that choice in words ("the site-wide CTA band is hidden on this
// page"). Until 2026-09-26 nothing read it: SiteFooterKit rendered its band on every page,
// so eleven approved boards disagreed with their built pages (CAG parity audit D3). The
// record is the page's own approved board, found by route the way scripts/pageboard.py's
// slug_file() names it: `/` is `index`, and a nested route's `/` is flattened to `--`.
// Only an APPROVED record counts; a page with no approved board keeps the band. A record under
// re-board has `approval: null` and its old approval in `approval_previous`; that is the
// approval in force (as in src/lib/pickedStyle.ts), so the page keeps what was last agreed.
// A stale record_hash (global_cta edited after approval) is caught by check:boards, not here.
// A city page lives at /uk-locations/<slug>/ but its board is keyed by the bare slug
// (Known Issue 39), so the flattened route is tried first and the bare last segment second,
// the same two spellings tests/render/lib/promotions.ts isNewPage tries.
// tests/py/test_global_cta.py.
type BoardCta = {
  approval?: unknown;
  approval_previous?: unknown;
  brief?: { cta?: { global_cta?: string } };
};

const RECORDS = import.meta.glob<BoardCta>('../../data/boards/*.json', { eager: true, import: 'default' });

export const boardSlugFor = (pathname: string): string => {
  const slug = pathname.replace(/^\/+|\/+$/g, '');
  return slug === '' ? 'index' : slug;
};

export function globalCtaShown(pathname: string): boolean {
  const slug = boardSlugFor(pathname);
  const bare = slug.split('/').pop() ?? slug;
  const record = RECORDS[`../../data/boards/${slug.replace(/\//g, '--')}.json`]
    ?? RECORDS[`../../data/boards/${bare}.json`];
  if (!record || !(record.approval ?? record.approval_previous)) return true;
  return record.brief?.cta?.global_cta !== 'hidden';
}
