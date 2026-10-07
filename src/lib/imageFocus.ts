// src/lib/imageFocus.ts — where a photograph's crop sits, from where its faces are.
//
// data/image-focus.json records, once per file, the boxes that must stay whole in any crop
// (the faces, in the master's own pixels). A city component never spells a crop by hand: the
// canvas mockups carried `style="object-position:…"` per image, per variant, and a crop typed
// beside one image is a crop the next layout gets wrong (learning loop 2026-09-27, L4 — the
// commonest image defect of the pass). Here the crop is DERIVED: object-position is the centre
// of the faces, as a fraction of the master, rounded to the 5% steps kit.css has classes for
// (`.focus .fx-NN .fy-NN`). No inline style, and one number per file rather than one per use.
// tests/render/checks/img.ts `img-face-visible` then measures the painted result.
//
// A served file (/images/…) also brings its SERVED alt and its baked width siblings, so a
// component reuses the photograph whole (working rule 11), never re-describing it.
import focusJson from '../../data/image-focus.json';
import type { FilledAsset } from './assets';
import { bakedSrcset, inPublic } from './assets';

type Box = [number, number, number, number];
interface FocusRow { src: 'puppies' | 'images'; w: number; h: number; faces: Box[]; scene?: string; alt?: string; widths?: number[] }
const ROWS = (focusJson as { images: Record<string, FocusRow> }).images;

/** The recorded row for one file, or a build error naming it. */
export function focusRow(file: string): FocusRow {
  const row = ROWS[file];
  if (!row) throw new Error(`data/image-focus.json has no row for ${file} — record its faces first`);
  return row;
}

const step = (n: number) => Math.min(100, Math.max(0, Math.round(n / 5) * 5));

/** The centre of the union of a file's faces, as whole percentages on the 5% grid. */
export function focusPoint(file: string): { x: number; y: number } {
  const { w, h, faces } = focusRow(file);
  const x0 = Math.min(...faces.map((f) => f[0]));
  const y0 = Math.min(...faces.map((f) => f[1]));
  const x1 = Math.max(...faces.map((f) => f[0] + f[2]));
  const y1 = Math.max(...faces.map((f) => f[1] + f[3]));
  return { x: step((100 * (x0 + x1)) / 2 / w), y: step((100 * (y0 + y1)) / 2 / h) };
}

/** The classes that put a file's crop on its faces: `focus fx-NN fy-NN` (kit.css). */
export function focusClass(file: string): string {
  const { x, y } = focusPoint(file);
  return `focus fx-${x} fy-${y}`;
}

/** A served photograph as the asset row BodyImage and the city components take: its original
 *  public path, its served alt, its intrinsic size — plus the srcset of its baked siblings. */
export function servedPhoto(file: string): FilledAsset & { srcset?: string } {
  const row = focusRow(file);
  if (row.src !== 'images' || !row.alt) {
    throw new Error(`${file} is not a served /images/ file with a recorded alt`);
  }
  const asset: FilledAsset = { slot: file, file: `/images/${file}`, w: row.w, h: row.h, alt: row.alt };
  const widths = row.widths ?? [];
  return widths.length ? { ...asset, srcset: bakedSrcset(asset, widths, inPublic) } : asset;
}

/** A puppy photo's alt. The same six photographs appear in several city components on one
 *  page, and `img-alt-present-and-unique` (blocking) refuses a repeated alt, so each component
 *  says a different true thing: `short` names the puppy ("Roman, a blue and white Staffy boy"),
 *  `scene` adds what the photo shows (data/image-focus.json `scene`). Where the puppy's name is
 *  printed beside the photo in the same cell or row, the photo is decorative and takes alt="". */
export function puppyAlt(p: { name: string; colour: string; sex: 'male' | 'female'; card_photo: string },
  style: 'short' | 'scene'): string {
  const short = `${p.name}, a ${p.colour.toLowerCase()} Staffy ${p.sex === 'male' ? 'boy' : 'girl'}`;
  if (style === 'short') return short;
  const scene = focusRow(p.card_photo).scene;
  if (!scene) throw new Error(`data/image-focus.json has no scene for ${p.card_photo}`);
  return `${short}, ${scene}`;
}

/** The alt the site already SERVES for a puppy's card photo: PuppyCard's (src/components/kit/
 *  PuppyCard.astro), on every page that lists the litter. A city component that shows a puppy's
 *  card photo for the FIRST time on its page keeps it (working rule 11; the user's ruling,
 *  2026-09-29: "same photo use new alt"); each repeat on that page takes `puppyAlt()` instead.
 *  tests/py/test_city_kit_manchester.py holds the two templates equal. */
export function servedPuppyAlt(p: { name: string; colour: string }): string {
  return `${p.name} the ${p.colour.toLowerCase()} Staffordshire Bull Terrier puppy`;
}
