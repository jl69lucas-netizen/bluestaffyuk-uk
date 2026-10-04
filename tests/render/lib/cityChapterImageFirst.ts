/**
 * The city-chapters probe (layout-h3-image-first, as CityChapters builds it): every chapter H3 is
 * followed STRAIGHT by its photograph, `img.bl-img`, or by a `<picture>` whose own `<img>` is
 * `.bl-img` (BodyImage's art-directed form: an approved infographic with its phone layout, answer
 * board 2026-10-04 q01 of the visual-intelligence batch, published byte-identical in c2206430).
 *
 * WHY IT TAKES THE PICTURE (2026-10-04): the probe matched `img.bl-img` only, written before any
 * chapter carried an art-directed image. Once the six infographic chapters rendered through
 * `<picture>`, it reported "6 chapter heading(s) not followed straight by their .bl-img photo" at
 * every width on London, while the built page put each image straight after its H3 (confirmed in
 * dist/: each of the six H3s is followed by `<picture><source …><img class="bl-img sec-img
 * art-phone media-u" …></picture>`). The registered `layout-h3-image-first` check already accepted
 * a wrapper holding `img.bl-img`; this probe now agrees with it, and is held by its own fixtures in
 * tests/render/city-kit.spec.ts (a heading followed by prose, or by a `<picture>` with no `.bl-img`,
 * still fails). Runs INSIDE the page (`page.evaluate(cityChapterImageFirst)`).
 */
export interface ChapterImageResult { examined: number; bad: string[] }

export function cityChapterImageFirst(): ChapterImageResult {
  const heads = Array.from(document.querySelectorAll('.city-chapters h3'));
  const bad: string[] = [];
  for (const h of heads) {
    const next = h.nextElementSibling;
    const ok = !!next && (next.matches('img.bl-img')
      || (next.tagName === 'PICTURE' && !!next.querySelector(':scope > img.bl-img')));
    if (!ok) bad.push((h.textContent ?? '').trim().replace(/\s+/g, ' ').slice(0, 50));
  }
  return { examined: heads.length, bad };
}
