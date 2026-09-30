// src/lib/puppyImages.ts — every puppy photo as an astro:assets import, keyed by filename.
// Task 7: the masters moved from assets/brand/<slug>/ into src/assets/puppies/ so <Image>
// can emit a bounded srcset (Known Issue 4: the single baked 800px card decoded at 3.3x the
// width it painted at). scripts/bake_images.py reads the same folder and still writes the
// public/images/puppies/*.webp derivatives that og:image and the Product schema point at —
// those are absolute URLs in markup, which a content-hashed build asset cannot be.
import type { ImageMetadata } from 'astro';

const files = import.meta.glob<{ default: ImageMetadata }>(
  '../assets/puppies/*.{jpg,jpeg,png,webp}',
  { eager: true },
);

export const PUPPY_IMAGES: Record<string, ImageMetadata> = Object.fromEntries(
  Object.entries(files).map(([path, mod]) => [path.split('/').pop()!, mod.default]),
);

/** Throws rather than rendering a broken <img>: a filename in data/puppies.json with no
 *  file behind it is drift between the data and the assets, and it should fail the build. */
export const puppyImage = (file: string): ImageMetadata => {
  const img = PUPPY_IMAGES[file];
  if (!img) throw new Error(`puppy image not in src/assets/puppies: ${file}`);
  return img;
};
