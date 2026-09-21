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
