import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
export const REPO = resolve(here, '../../..');

/**
 * The whitelist is READ FROM `scripts/dup_content_audit.py`, never copied.
 *
 * That file's list is the only tuned one this project has: it was built by working
 * through real reports and encodes exactly what CLAUDE.md says may legitimately repeat
 * across siblings — the shipping cost line, doc-badge enumerations, the counter strip,
 * the CITES notice, real reviews. Forking it into TypeScript would create two lists that
 * agree today and drift the first time either is tuned, and the drift would show up as a
 * check reporting a mandated line as a defect.
 *
 * The trade-off, stated: this parses Python string literals with a regex, so a future
 * entry written with an f-string or built by concatenation would be missed. The parse
 * therefore ASSERTS a floor on how many entries it found — a silently-empty whitelist
 * would turn every mandated line into a defect on every page at once.
 */
export function loadWhitelist(): string[] {
  const src = readFileSync(join(REPO, 'scripts/dup_content_audit.py'), 'utf8');
  const start = src.indexOf('WHITELIST_SNIPPETS');
  if (start < 0) throw new Error('dup_content_audit.py no longer defines WHITELIST_SNIPPETS');
  const end = src.indexOf('\n]', start);
  const block = src.slice(start, end < 0 ? undefined : end);
  const out: string[] = [];
  for (const m of block.matchAll(/"([^"]{8,})"|'([^']{8,})'/g)) {
    out.push((m[1] ?? m[2]).toLowerCase());
  }
  if (out.length < 10) {
    throw new Error(
      `parsed only ${out.length} whitelist entries from dup_content_audit.py — refusing to ` +
        `run with a near-empty whitelist, which would report every mandated line as a defect`,
    );
  }
  return out;
}

/**
 * The Python auditor's tokeniser, exactly: `re.findall(r"[a-z0-9$']+", text.lower())`.
 *
 * An apostrophe is part of a word, so "we'd" is ONE token on both sides. Until 2026-09-11 this
 * replaced every other character with a space, apostrophe included, and read "we d" — so a
 * shared sentence of 11 words with one contraction was 12 here (fires) and 11 in Python
 * (silent), measured on dist/ between the eggs and congo for-sale pages. A curly ’ is outside
 * the class on both sides, so "we’d" is two tokens in both. Whitelist stems go through this
 * same function, as Python's WHITELIST_STEMS go through its findall.
 */
export function normalise(text: string): string[] {
  return text.toLowerCase().match(/[a-z0-9$']+/g) ?? [];
}

/**
 * Decode character references the way Python's HTMLParser (convert_charrefs=True) does before
 * the auditor tokenises. The rendered page's innerText is already decoded; the corpus is read
 * from raw HTML, where Astro writes many apostrophes as &#39; — undecoded, "we&#39;d" reads
 * "we 39 d" and matches neither side. One pass, so "&#38;amp;" cannot decode twice. Only
 * characters normalise() keeps can change a token, so every named reference other than
 * &apos; and &dollar; reduces to a word break.
 */
const NAMED_KEPT: Record<string, string> = { apos: "'", dollar: '$' };
export function decodeEntities(text: string): string {
  return text.replace(
    /&(?:#(\d+);?|#[xX]([0-9a-fA-F]+);?|([a-zA-Z][a-zA-Z0-9]*);)/g,
    (_, dec: string | undefined, hex: string | undefined, name: string | undefined) => {
      if (name !== undefined) return NAMED_KEPT[name] ?? ' ';
      const cp = dec !== undefined ? Number(dec) : parseInt(hex!, 16);
      return cp > 0 && cp <= 0x10ffff ? String.fromCodePoint(cp) : ' ';
    },
  );
}

/**
 * Slug → built file / served route. Astro's file-based routing puts the homepage at
 * `dist/index.html` served as `/`; every other slug is `dist/<slug>/index.html` at
 * `/<slug>/`. `index` is the ONE special case, and both resolvers live here so the
 * spec and the corpus reader cannot disagree about where a page is.
 */
export function distFileFor(slug: string): string {
  return slug === 'index' ? join(REPO, 'dist', 'index.html') : join(REPO, 'dist', slug, 'index.html');
}
export function routeFor(slug: string): string {
  return slug === 'index' ? '/' : `/${slug}/`;
}

export interface Target {
  slug: string;
  page_type: string;
}

/**
 * Every built page in a dist/ directory, keyed exactly as `scripts/_slugs.py` page_key keys
 * it: `dist/index.html` → "index", `dist/available/roys/index.html` → "available/roys".
 */
export function distSlugs(dist: string = join(REPO, 'dist')): string[] {
  const out: string[] = [];
  const walk = (dir: string, rel: string): void => {
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      if (e.isDirectory()) walk(join(dir, e.name), rel ? `${rel}/${e.name}` : e.name);
      else if (e.name === 'index.html') out.push(rel || 'index');
    }
  };
  if (existsSync(dist)) walk(dist, '');
  return out.sort();
}

/**
 * The pages a target's DUP check is judged against: every OTHER built page, the same input
 * set scripts/dup_content_audit.py compares pairwise.
 *
 * Until 2026-09-11 this was "targets of the same page type". targets.json holds a dozen
 * for-sale targets but one each of every other type, so six page types compared against
 * nothing (examined=0) while the Python gate found 481 crossovers on 70 pages — bird-card
 * copy on care, blog and home pages, location lines, credential sentences on available/*.
 * Every one of those partners is a page no target is paired with, so the fix is the corpus,
 * not a longer target list. `targets` is kept in the signature so the meta gate can prove
 * the page-type filter has not crept back.
 */
export function siblingSlugsFor(target: Target, _targets: Target[], corpus: string[]): string[] {
  return corpus.filter((slug) => slug !== target.slug);
}

/** Forms are UI copy shared by design — the Python auditor skips them (SKIP_TAGS), so every
 *  text path here does too, or the two gates judge the same page differently. */
const stripForms = (html: string) => html.replace(/<form[\s\S]*?<\/form>/gi, ' ');

/** Visible text of a built page — script, style, JSON-LD and forms stripped. */
export function distText(slug: string): string | null {
  const file = distFileFor(slug);
  if (!existsSync(file)) return null;
  let html = readFileSync(file, 'utf8');
  html = html.replace(/<script[\s\S]*?<\/script>/gi, ' ');
  html = html.replace(/<style[\s\S]*?<\/style>/gi, ' ');
  html = stripForms(html);
  html = html.replace(/<!--[\s\S]*?-->/g, ' ');
  const main = /<main[\s\S]*?>([\s\S]*)<\/main>/i.exec(html);
  return decodeEntities((main ? main[1] : html).replace(/<[^>]+>/g, ' '));
}

/** Every .html file in a fixture corpus directory, for the meta gate. */
export function fixtureCorpus(dir: string): { slug: string; text: string }[] {
  const full = join(REPO, dir);
  if (!existsSync(full)) return [];
  return readdirSync(full)
    .filter((f) => f.endsWith('.html'))
    .map((f) => ({
      slug: f.replace(/\.html$/, ''),
      text: decodeEntities(
        stripForms(
          readFileSync(join(full, f), 'utf8')
            .replace(/<script[\s\S]*?<\/script>/gi, ' ')
            .replace(/<style[\s\S]*?<\/style>/gi, ' '),
        ).replace(/<[^>]+>/g, ' '),
      ),
    }));
}
