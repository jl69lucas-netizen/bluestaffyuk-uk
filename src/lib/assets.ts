import { existsSync } from 'node:fs';
import { join } from 'node:path';

// src/lib/assets.ts — a board record's baked photographs, by slot.
//
// Working rule 11: every image a rebuilt page renders is one the migrated site already served,
// at its ORIGINAL public path with its ORIGINAL alt text, and the board record's `assets` block
// is where the bake recorded both along with the intrinsic size. Three rebuilt pages had each
// written the same four-line closure to read it (hoisted here in the review of 0128e21), and a
// lookup copied three times is a lookup that can be fixed twice.
//
// IT THROWS ON A MISSING OR UNFILLED SLOT, and that is the whole reason it is a function rather
// than a `find`. `record.assets.find(...)` returns `undefined`, and an `<img>` built from it
// ships with no `src`, no `alt` and no `width`/`height`: a blank box that passes the build, is
// invisible to a reader using a screen reader, and reflows the page. A named build-time error
// says which slot, while the person who renamed it is still looking at the build.

/** The row the bake writes for one image slot. Structural, so an imported record's JSON fits
 *  without either side importing the other's type. `file` is nullable because a slot is
 *  recorded on the board before it is filled. */
export interface BakedAsset {
  slot: string;
  w: number;
  h: number;
  alt: string;
  file: string | null;
  caption?: string;
}

/** The asset row a slot resolves to, with a non-null `file`. */
export type FilledAsset = BakedAsset & { file: string };

/** The shape of a board record this helper needs. */
export interface AssetSource {
  meta?: { slug?: string } | null;
  assets: readonly BakedAsset[];
}

/**
 * `asset('hero')` for one record: the filled row that slot names, or a build-time error.
 *
 * The error names the record's own slug, so a page that mounts more than one record's assets
 * still says which board the slot is missing from.
 */
export function bakedAssets(record: AssetSource, label?: string) {
  const who = label ?? record.meta?.slug ?? 'board record';
  return (slot: string): FilledAsset => {
    const a = record.assets.find((x) => x.slot === slot);
    if (!a || !a.file) throw new Error(`${who}: the record has no baked asset for ${slot}`);
    return a as FilledAsset;
  };
}

// ── the baked candidate list ───────────────────────────────────────────────────────────────

/**
 * `srcset` for a baked public-path photograph, from the SIBLINGS THAT EXIST ON DISK.
 *
 * WHY THIS IS NOT A STRING IN THE PAGE. `/images/<name>.webp` is copied verbatim by the
 * build, so nothing in the pipeline knows what candidates were baked beside it and every
 * rebuilt page has spelled its own `srcset` by hand. A hand-written candidate is a filename
 * duplicated away from the file: rename or re-bake one and the page keeps serving the string,
 * the browser 404s the candidate it chose, and NO gate sees it — `img-srcset-within-2x`
 * measures the image that actually painted, and a 404 candidate means the master painted, so
 * the check reports the master's own ratio and is satisfied. This builds the list from the
 * master's own path, checks every candidate is really there, and throws naming the missing
 * file instead.
 *
 * `widths` are the sibling widths to offer; the master is appended at its own intrinsic width
 * so the largest candidate is always the served file (working rule 11: the master is never
 * re-encoded and never renamed, a sibling is only ever added beside it).
 */
export function bakedSrcset(
  asset: FilledAsset, widths: readonly number[], exists: (publicPath: string) => boolean,
): string {
  const dot = asset.file.lastIndexOf('.');
  if (dot < 0) throw new Error(`${asset.slot}: ${asset.file} has no extension to build a candidate from`);
  const [stem, ext] = [asset.file.slice(0, dot), asset.file.slice(dot)];
  const rows = [...widths].sort((a, b) => a - b).map((w) => {
    if (w >= asset.w) {
      throw new Error(`${asset.slot}: candidate ${w}w is not smaller than the master's ${asset.w}w `
        + '— a candidate wider than the file it stands in for is never the right pick');
    }
    const path = `${stem}-${w}${ext}`;
    if (!exists(path)) {
      throw new Error(`${asset.slot}: ${path} is named as a srcset candidate and is not in `
        + 'public/ — bake it beside the master or stop offering it');
    }
    return `${path} ${w}w`;
  });
  return [...rows, `${asset.file} ${asset.w}w`].join(', ');
}

// ── the two constants every rebuilt page had written for itself ─────────────────────────────

/** The project's `public/`, found once. */
const PUBLIC_DIR = join(process.cwd(), 'public');

/**
 * Does `publicPath` exist under `public/`?
 *
 * `bakedSrcset` takes this as an argument rather than importing `node:fs` itself, so that it
 * stays testable — but FOUR rebuilt pages had each written the same
 * `existsSync(fileURLToPath(new URL('../../../public' + p, import.meta.url)))`, differing only
 * in how many `../` the page's own depth needed. A relative path repeated per caller is a
 * relative path that breaks the day a page moves a directory, and it broke nothing only
 * because none of them had.
 *
 * IT IS RESOLVED FROM THE WORKING DIRECTORY, NOT FROM `import.meta.url`, and that is the
 * correction this hoist needed. A page's frontmatter keeps its own module identity through
 * the build, so `../../../public` from inside a page happened to be right; a LIBRARY module is
 * bundled, `import.meta.url` becomes the chunk's url under `.astro/`, and the first build
 * after the hoist reported the freshly baked candidate as missing and refused to render the
 * page — loudly, which is `bakedSrcset`'s own design working. `astro build` runs from the
 * project root, so `public/` is one join away from it, and the throw below says so rather
 * than letting a wrong root read as an empty one.
 */
export const inPublic = (publicPath: string) => {
  if (!existsSync(PUBLIC_DIR)) {
    throw new Error(`inPublic: ${PUBLIC_DIR} is not there — this resolves public/ from the `
      + 'working directory, and the build is being run from somewhere other than the project root');
  }
  return existsSync(join(PUBLIC_DIR, publicPath));
};

/**
 * The `sizes` an in-body photograph paints at on a page inside `PageShell`.
 *
 * MEASURED, not chosen: `.bl-img` inside a prose column is capped at 420px from 900px up
 * (src/styles/board-styles.css) and is full width below 640px. The rebuilt pages that pass
 * it import this one string, so a change to that cap is made here. No render check measures
 * it today: `img-sizes-matches-box` (tests/render/checks/img.ts) examines only the hero's
 * `.kit-hero .pic`. A page whose geometry is genuinely different states its own.
 */
export const BODY_SIZES = '(max-width: 640px) 100vw, 420px';

/**
 * The `sizes` of the uniform box (`.bl-img.sec-img`, BodyImage `box="uniform"` or `"tall"`):
 * 760px wide wherever the column allows it, the full column below that. 800px is 760 plus
 * the column's two 20px gutters, so above it the box is at its cap.
 */
export const UNIFORM_SIZES = '(max-width: 800px) 100vw, 760px';

/**
 * The `sizes` of the tall box (BodyImage `box="tall"`, `.bl-img.sec-img.og-tall`). Below
 * 900px in portrait orientation the box turns 4:5, and the 1408x768 file covers it: a 4:5 box
 * W wide is 1.25W tall, so the file is scaled to 1.25W / 768 and paints 1408 * 1.25 / 768 =
 * 2.29W wide, of which the box shows the middle strip. The browser must therefore pick a
 * candidate ~230vw wide (in practice the full 1408 file on a phone), not 100vw, or the strip
 * is upscaled and soft. Elsewhere it is the uniform 16:9 box, 760px at most.
 */
export const TALL_SIZES = '(max-width: 899.98px) and (orientation: portrait) 230vw, 760px';
