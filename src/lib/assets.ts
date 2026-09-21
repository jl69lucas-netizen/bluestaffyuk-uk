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
