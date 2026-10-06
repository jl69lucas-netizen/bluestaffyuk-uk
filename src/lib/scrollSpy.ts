// src/lib/scrollSpy.ts — which section is the reader in? The city nav set's one answer.
//
// PageDial, SectionStrip and SectionSheet each carry this logic inline (the twelve built pages
// mount them and are frozen, so they are left as they are). The city set — CityDialPhotoMarker and
// CityJumpStepper — imports it instead, so two components on one page cannot disagree about the
// current section: the same reading band (`-40% 0px -55% 0px`), the same bottom-of-document
// rule (a short last section can never reach the band, so at the bottom the last row wins),
// and the same seed from the URL fragment. See the fuller notes in PageDial.astro.
//
// It is SCRIPT, not CSS, on purpose (plan2-notes; learning loop 2026-09-27, L8): the canvas
// marked the current section with scroll-driven animations or `:target`, which a reader who
// asks for reduced motion saw stuck on section one. An IntersectionObserver has no motion.
// `aria-current="location"`, never a bare `aria-current` (the empty string is the token false).

export interface SpyRow { link: HTMLAnchorElement; target: HTMLElement }

/** `[data-spy]` links under `root`, each PAIRED with the section it names; unresolved ids drop
 *  out one by one rather than shifting every later pair (the note in PageDial.astro). */
export function spyRows(root: ParentNode): SpyRow[] {
  return [...root.querySelectorAll<HTMLAnchorElement>('[data-spy]')]
    .map((link) => ({ link, target: document.getElementById(link.dataset.spy!) }))
    .filter((r): r is SpyRow => r.target !== null);
}

/** Mark row `i` of `links` current and every other row not. */
export function markCurrent(links: HTMLAnchorElement[], i: number): void {
  links.forEach((a, j) => {
    if (j === i) a.setAttribute('aria-current', 'location');
    else a.removeAttribute('aria-current');
  });
}

/** Call `onChange(i)` with the index of the current section in `targets`, now and whenever it
 *  changes. One observer per caller; the page mounts one dial and one band. */
export function watchSections(targets: HTMLElement[], onChange: (i: number) => void): void {
  const N = targets.length;
  if (!N) return;
  const atBottom = () => window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2;
  let fromObserver = 0;
  let last = -1;
  // Above the first section (the hero, the takeaways, the first FAQ block) the first row is
  // current, as on a fresh load: the observer alone kept the last row it saw, so a reader who
  // scrolled back to the top was told they were still in a later section (harden pass 2026-10-03).
  const aboveFirst = () => targets[0].getBoundingClientRect().top > window.innerHeight * 0.45;
  const apply = () => {
    const i = atBottom() ? N - 1 : aboveFirst() ? 0 : fromObserver;
    if (i !== last) {
      last = i;
      onChange(i);
    }
  };
  // THE BAND'S WHOLE STATE, NOT THE LAST BATCH (lessons entry 20, 2026-10-06). An observer batch
  // holds only the targets whose state CHANGED. Reading the current section from the batch alone
  // stuck on the wrong row after a jump: a jump that lands a boundary in the band reports both
  // sections entering (the upper one wins), and the next scroll, which takes the upper one out,
  // reports only it leaving. The lower one never changed, so it was never in a batch, and the
  // row stayed on the section the reader had left (measured on /kit-preview/city-page/: takeaways
  // still current with the puppy sheet filling the band). So every target in the band is kept,
  // and the topmost of them is current; an empty band (a gap between sections) keeps the last.
  const inBand = new Set<number>();
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        const i = targets.indexOf(e.target as HTMLElement);
        if (i < 0) continue;
        if (e.isIntersecting) inBand.add(i);
        else inBand.delete(i);
      }
      // Targets are in document order, so the lowest index in the band is the topmost.
      if (inBand.size) fromObserver = Math.min(...inBand);
      apply();
    },
    { rootMargin: '-40% 0px -55% 0px' },
  );
  targets.forEach((t) => io.observe(t));
  window.addEventListener('scroll', apply, { passive: true });
  const fromHash = targets.findIndex((t) => t.id === decodeURIComponent(location.hash.slice(1)));
  if (fromHash >= 0) fromObserver = fromHash;
  apply();
}
