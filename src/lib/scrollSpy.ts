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
  const apply = () => {
    const i = atBottom() ? N - 1 : fromObserver;
    if (i !== last) {
      last = i;
      onChange(i);
    }
  };
  const io = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (!visible[0]) return;
      const i = targets.indexOf(visible[0].target as HTMLElement);
      if (i >= 0) fromObserver = i;
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
