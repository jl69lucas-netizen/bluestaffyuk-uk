import { existsSync, readdirSync, statSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';

/**
 * Directory names that are never source, wherever they appear. `src/pages/node_modules/.vite/`
 * exists in this repo — walking it costs thousands of stats and would refuse every run the
 * moment Vite touched a vendored dep.
 */
const SKIP = new Set(['node_modules', '.vite', '.git', '.DS_Store', '.astro', '.cache']);

/** Source paths whose mtime should force a rebuild. Missing entries are skipped, not fatal. */
const SOURCES = ['src', 'public', 'astro.config.mjs', 'package.json'];

export interface Freshness {
  fresh: boolean;
  /** Always populated — on failure it names the offending file AND the remedy. */
  reason: string;
}

interface NewestResult {
  path: string;
  ms: number;
  /**
   * True if `readdirSync`/`statSync` threw anywhere under this path (permission
   * error, a broken symlink, a file deleted mid-walk). Deliberately NOT the same
   * signal as `ms === 0` — a path that legitimately contains nothing but
   * SKIP-listed vendor trees (the `src/pages/node_modules/.vite` case) also
   * reports `ms: 0` with no error, and that case must stay fresh, not refuse.
   * Only a genuine read failure should refuse; "found nothing because everything
   * present was filtered out by design" is the normal, expected state.
   */
  error: boolean;
}

function newest(path: string): NewestResult {
  let best = { path, ms: 0 };
  let error = false;
  // Only walks real directories — a Dirent for a symlink-to-directory reports
  // isDirectory() === false (it reflects the link itself, not readlink's target),
  // so symlinked source trees are silently not descended into. That is latent
  // today (no symlinks under src/, public/, or dist/ in this repo) and it is the
  // same non-recursion that keeps a symlink cycle from hanging this walk forever
  // — accepted as a trade, not tracked as a bug.
  const walk = (dir: string): void => {
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      error = true;
      return;
    }
    for (const e of entries) {
      if (SKIP.has(e.name)) continue;
      const p = join(dir, e.name);
      if (e.isDirectory()) {
        walk(p);
      } else {
        let ms = 0;
        try {
          // Follows symlinks (unlike lstat). A symlink whose target is gone
          // throws ENOENT here, which is exactly the "could not be read" signal
          // this function exists to surface — not silence.
          ms = statSync(p).mtimeMs;
        } catch {
          error = true;
          continue;
        }
        if (ms > best.ms) best = { path: p, ms };
      }
    }
  };
  let st;
  try {
    st = statSync(path);
  } catch {
    return { ...best, error: true };
  }
  if (st.isDirectory()) walk(path);
  else best = { path, ms: st.mtimeMs };
  return { ...best, error };
}

/** `123456ms` → `"2 min"` or `"37s"`. Below a minute, "0 min" reads as "no difference found" —
 * the opposite of what a refusal is trying to say — so seconds are used under that floor. */
function formatAge(deltaMs: number): string {
  return deltaMs < 60_000 ? `${Math.max(1, Math.round(deltaMs / 1000))}s` : `${Math.round(deltaMs / 60_000)} min`;
}

/**
 * A stale `dist/` is the quietest way this harness can lie: every check passes, every
 * number is real, and all of them describe a build nobody is shipping. Refuse to measure.
 *
 * Note on what this does NOT catch: deleting a source file (e.g. removing
 * `src/pages/foo/index.astro`) is invisible here — `newest()` only reads file mtimes,
 * so removing a file leaves every surviving file older than `dist/`, and the gate
 * reports fresh while `dist/foo/index.html` still serves a page whose source is gone.
 * Folding directory mtimes into the comparison would catch that, but was deliberately
 * rejected: directory mtimes are noisy (an editor swap file or a tool's temp file
 * appearing and vanishing under src/ bumps its parent directory's mtime), and on this
 * codebase a false REFUSAL is the more expensive failure mode — a gate that cries wolf
 * once gets ignored forever, which is how twelve gates accumulated false reports here.
 * A rare false PASS on a deleted-but-not-replaced source file is the accepted trade.
 * In practice the blind spot is narrower than it reads: a `git checkout` that removes
 * a file almost always rewrites others in the same commit with a current mtime, which
 * trips the gate anyway — the gap is specifically a file deleted with nothing else
 * in `src/` touched.
 *
 * CLOSED 2026-08-01, and NOT by folding directory mtimes in — that would have bought
 * the deletion case at the price of firing on unrelated filesystem noise, which is the
 * trade rejected above. `builtRoutesWithoutSource()` compares the SET of built routes
 * against the SET of source pages instead, so a failure always names the exact orphaned
 * route and is always actionable. The paragraph above is left standing because the
 * reasoning in it is still correct about mtimes; it is the mechanism that changed.
 */
/**
 * Routes present in dist/ that have no corresponding file under src/pages/.
 * Exported so the deletion case can be tested directly rather than only through
 * checkDistFreshness's message string.
 *
 * Route derivation mirrors Astro's default file-based routing: `index.*` maps to its
 * parent directory, anything else maps to its own stem. Returns [] when either tree is
 * absent — "cannot compare" is not "found a deletion", and the callers above already
 * refuse a missing dist/ with a clearer message.
 */
export function builtRoutesWithoutSource(root: string = process.cwd()): string[] {
  const pagesDir = resolve(root, 'src', 'pages');
  const dist = resolve(root, 'dist');
  if (!existsSync(pagesDir) || !existsSync(dist)) return [];

  const PAGE_EXT = new Set(['.astro', '.md', '.mdx', '.html']);
  const src = new Set<string>();
  const walkPages = (dir: string, prefix: string[]): void => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.name === 'node_modules' || entry.name.startsWith('.')) continue;
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        walkPages(full, [...prefix, entry.name]);
        continue;
      }
      const dot = entry.name.lastIndexOf('.');
      if (dot < 0) continue;
      const ext = entry.name.slice(dot);
      if (!PAGE_EXT.has(ext)) continue;
      const stem = entry.name.slice(0, dot);
      src.add((stem === 'index' ? prefix : [...prefix, stem]).join('/'));
    }
  };
  walkPages(pagesDir, []);

  // DYNAMIC ROUTES — added in the BSUK port (2026-09-16), and the reason is a measured
  // false REFUSAL, not a hypothetical. CAG's site has no dynamic routes at all ("108
  // source routes, 108 built routes, zero discrepancy"), so a source set of literal
  // strings was enough there. BSUK routes three of its clusters through parameters:
  // `src/pages/available-puppies/[slug].astro`, `src/pages/uk-locations/[slug].astro`
  // and a root-level catch-all `src/pages/[...post].astro`. Compared as literals, every
  // one of the 30+ puppy, location and blog pages those emit is an orphan with "no source
  // under src/pages", and checkDistFreshness refuses EVERY run of the pages suite on a
  // perfectly current build — the cry-wolf failure the comment above calls the more
  // expensive one on this codebase.
  //
  // A dynamic segment is matched as a PATTERN instead: `[param]` spans exactly one path
  // segment, `[...rest]` spans zero or more (Astro's own rest-parameter semantics, which
  // is why the `/` before it is optional in the regex). Everything else is still compared
  // literally, so the deletion case this function exists for — a static page removed from
  // src/ while dist/ still serves it — is caught exactly as before.
  //
  // Stated cost, because it is real: a root-level `[...rest]` route matches ANY path, so
  // while `src/pages/[...post].astro` exists this check cannot prove any route orphaned,
  // and a blog post deleted from the content collection will not be reported here. That
  // is a limit of comparing PATHS: the catch-all's paths come from getStaticPaths, not
  // from the filesystem. It is the honest answer rather than a false refusal, and the
  // content-collection deletion case belongs to a check that can read the collection.
  const ESCAPE = /[.*+?^${}()|[\]\\]/g;
  const dynamic: RegExp[] = [];
  for (const route of src) {
    if (!route.includes('[')) continue;
    let pattern = '';
    for (const seg of route.split('/')) {
      if (/^\[\.\.\..+\]$/.test(seg)) {
        // A rest parameter matches ZERO or more segments, so the separator in front of it
        // is part of the optional group — otherwise `blog/[...slug]` would fail to match
        // `blog` itself, which is exactly the path the rest route serves when it matches
        // nothing.
        pattern += pattern ? '(?:/[^/]+)*' : '(?:[^/]+(?:/[^/]+)*)?';
      } else if (/^\[.+\]$/.test(seg)) {
        pattern += (pattern ? '/' : '') + '[^/]+';
      } else {
        pattern += (pattern ? '/' : '') + seg.replace(ESCAPE, '\\$&');
      }
    }
    dynamic.push(new RegExp(`^${pattern}$`));
  }
  const hasSource = (route: string): boolean =>
    src.has(route) || dynamic.some((re) => re.test(route));

  // An EMPTY source set means "could not enumerate the pages", not "every built route
  // is orphaned". Without this, a src/pages containing only skipped content (a vendored
  // node_modules tree is the real case) makes every route in dist/ look deleted and the
  // gate refuses a perfectly good build. That is the false FAIL this check was deferred
  // over once, and it was caught here by an existing test rather than by review.
  if (src.size === 0) return [];

  const orphans: string[] = [];
  const walkDist = (dir: string, prefix: string[]): void => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        walkDist(full, [...prefix, entry.name]);
        continue;
      }
      if (entry.name !== 'index.html') continue;
      const route = prefix.join('/');
      if (!hasSource(route)) orphans.push(route);
    }
  };
  walkDist(dist, []);
  return orphans.sort();
}

export function checkDistFreshness(root: string = process.cwd()): Freshness {
  const dist = resolve(root, 'dist');
  if (!existsSync(dist)) {
    return { fresh: false, reason: 'dist/ does not exist — run `npm run build` first' };
  }
  const newestDist = newest(dist);
  // Check the error flag before ms===0: a dist/ that could not be READ (permission
  // error, broken symlink) also computes ms===0, and telling the operator "contains
  // no files" when the truth is "could not be read" sends them to delete and rebuild
  // a dist/ that may be fine — message-quality only, this branch still refuses either way.
  if (newestDist.error) {
    return {
      fresh: false,
      reason: 'dist/ could not be fully read (permission error or a broken symlink) — refusing to call it fresh.',
    };
  }
  if (newestDist.ms === 0) {
    return { fresh: false, reason: 'dist/ contains no files — run `npm run build` first' };
  }

  // Deletion check — closes the blind spot described above WITHOUT the false-FAIL cost
  // that made the mtime approach a bad trade. mtimes cannot see a deletion: removing a
  // page from src/ leaves dist/ serving a stale copy while every remaining file's mtime
  // still says fresh. Folding DIRECTORY mtimes in would catch it but fires on unrelated
  // filesystem noise, and on this codebase a gate that cries wolf gets ignored forever.
  //
  // A set comparison has no such cost: it names the exact orphaned route, so a failure
  // is always actionable and never ambiguous. Measured on this repo 2026-08-01 —
  // 108 source routes, 108 built routes, zero discrepancy in either direction, because
  // the site has no dynamic routes or collection-generated pages. If that ever changes,
  // this fails loudly with the route name rather than silently, which is the correct
  // direction for a gate whose whole purpose is refusing to measure a stale build.
  const orphans = builtRoutesWithoutSource(root);
  if (orphans.length) {
    const shown = orphans.slice(0, 5).map((r) => `/${r}/`).join(', ');
    return {
      fresh: false,
      reason:
        `dist/ serves ${orphans.length} route(s) with no source under src/pages — ` +
        `the source was deleted and dist/ still has the old build: ${shown}` +
        `${orphans.length > 5 ? ` (+${orphans.length - 5} more)` : ''}. Run \`npm run build\`.`,
    };
  }

  for (const rel of SOURCES) {
    const p = resolve(root, rel);
    if (!existsSync(p)) continue;
    const n = newest(p);
    // A read failure under an existing source path must refuse, never fall through as
    // "nothing newer than dist". Falling through would be a false PASS having examined
    // zero of the files it failed to read — the exact "PASS having examined nothing"
    // failure mode this whole harness exists to stop reproducing (see build_scorecard.mjs
    // Guard 1's own comment). This is NOT the same branch as "n.ms === 0 with no error" —
    // that is the legitimate all-vendored-content case handled by NewestResult.error above.
    if (n.error) {
      return {
        fresh: false,
        reason:
          `${rel} could not be fully read (permission error or a broken symlink) — refusing ` +
          `to call dist/ fresh without having examined it. Silently treating an unreadable ` +
          `source path as "nothing newer" is the same false PASS this gate exists to prevent.`,
      };
    }
    if (n.ms > newestDist.ms) {
      return {
        fresh: false,
        reason:
          `${relative(root, n.path)} is ${formatAge(n.ms - newestDist.ms)} newer than the newest file in dist/ ` +
          `(${relative(root, newestDist.path)}) — run \`npm run build\` first. ` +
          `Measuring a stale dist/ produces real numbers about a build nobody ships.`,
      };
    }
  }
  return { fresh: true, reason: `dist/ is current (newest: ${relative(root, newestDist.path)})` };
}
