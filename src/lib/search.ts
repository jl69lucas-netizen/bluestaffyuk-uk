// src/lib/search.ts — the browser half of the on-site search (spec §11 amendment 3b).
//
// Two callers share this: the header's instant pill (SiteHeaderKit.astro) and the /search/
// results page. They differ only in how many rows they show and where they put them, so the
// fetch, the cache, the matching and the grouping live here once rather than twice.
//
// The index is /search-index.json, written at build time by scripts/build_search_index.py.
// Nothing here contacts anything else.

export interface SearchRow {
  url: string;
  title: string;
  kind: string;
  keywords: string;
}

/** The order results are grouped in. A kind outside this list falls into `Other`. */
export const GROUPS = ['Puppy', 'Guide', 'Location', 'Blog', 'Page'] as const;
export const OTHER = 'Other';

let index: SearchRow[] | null = null;
let pending: Promise<SearchRow[]> | null = null;

/** Fetched once per page: `pending` is the in-flight promise, so the header's two forms —
 *  and the five headers the design canvas mounts — share one request rather than racing. */
export function loadIndex(): Promise<SearchRow[]> {
  if (index) return Promise.resolve(index);
  if (!pending) {
    pending = fetch('/search-index.json')
      .then((r) => (r.ok ? r.json() : []))
      .then((rows: SearchRow[]) => (index = Array.isArray(rows) ? rows : []))
      .catch(() => (index = []));
  }
  return pending;
}

/** Every term must appear in the title or the keywords: typing narrows, it never widens. */
export function matchRows(rows: SearchRow[], query: string): SearchRow[] {
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  if (!terms.length) return [];
  return rows.filter((r) => {
    const hay = (r.title + ' ' + r.keywords).toLowerCase();
    return terms.every((t) => hay.includes(t));
  });
}

const groupOf = (kind: string) => ((GROUPS as readonly string[]).includes(kind) ? kind : OTHER);

/** Matches in group order, capped at `limit` rows in total. Groups with nothing in them are
 *  not emitted, so the reader never sees an empty heading. */
export function grouped(rows: SearchRow[], limit: number): [string, SearchRow[]][] {
  const out: [string, SearchRow[]][] = [];
  let left = limit;
  for (const group of [...GROUPS, OTHER]) {
    if (left <= 0) break;
    const inGroup = rows.filter((r) => groupOf(r.kind) === group).slice(0, left);
    if (!inGroup.length) continue;
    left -= inGroup.length;
    out.push([group, inGroup]);
  }
  return out;
}

/** How `renderInto` should mark the list up.
 *
 *  The header's pill is a COMBOBOX: its list is a `listbox`, each result is an `option`
 *  with an id, and the input points at the active one with aria-activedescendant. The
 *  /search/ page is not — it is a page of results a reader scrolls, and calling it a
 *  listbox would announce a widget nobody is operating. So the roles are opt-in, and the
 *  one that needs them says so by passing an id prefix. */
export interface RenderOptions {
  /** Set to make the list a listbox whose options are `${optionIdPrefix}-0`, `-1`, … */
  optionIdPrefix?: string;
}

/** Fills a `<ul>` with grouped results. Returns the number of rows written. */
export function renderInto(
  list: HTMLUListElement,
  rows: SearchRow[],
  query: string,
  limit: number,
  { optionIdPrefix }: RenderOptions = {},
): number {
  list.textContent = '';
  if (optionIdPrefix) list.setAttribute('role', 'listbox');
  else list.removeAttribute('role');
  let written = 0;
  for (const [group, inGroup] of grouped(rows, limit)) {
    const head = document.createElement('li');
    head.className = 'group';
    head.textContent = group;
    // A listbox's children are options; a heading between them is presentational, or the
    // reader is told there are more options than there are.
    if (optionIdPrefix) head.setAttribute('role', 'presentation');
    list.append(head);
    for (const row of inGroup) {
      // The index holds this site's own routes and nothing else, so a url that is not a
      // root-relative path is not a result: it is a row that should not be there. Assigning
      // it to `a.href` unguarded would let a `javascript:` or off-site value out of a static
      // JSON file and into a link the reader is being invited to click.
      if (!row.url.startsWith('/')) continue;
      const li = document.createElement('li');
      if (optionIdPrefix) {
        li.id = `${optionIdPrefix}-${written}`;
        li.setAttribute('role', 'option');
        li.setAttribute('aria-selected', 'false');
      }
      const a = document.createElement('a');
      a.href = row.url;
      a.textContent = row.title;
      li.append(a);
      list.append(li);
      written += 1;
    }
  }
  if (!written) {
    const li = document.createElement('li');
    li.className = 'empty';
    if (optionIdPrefix) li.setAttribute('role', 'presentation');
    li.textContent = `Nothing matches \u201C${query}\u201D.`;
    list.append(li);
  }
  list.hidden = false;
  return written;
}

/** Every option element in a rendered listbox, in reading order. */
export function optionsIn(list: HTMLUListElement): HTMLLIElement[] {
  return Array.from(list.querySelectorAll<HTMLLIElement>('li[role="option"]'));
}
