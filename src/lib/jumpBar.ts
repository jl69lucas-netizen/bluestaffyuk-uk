// src/lib/jumpBar.ts — a city page's phone jump bar as top chrome: the height every jump target
// clears, and the slide away on the way down and back on the way up.
//
// THE USER'S RULING (answer board q03, 2026-09-29): on a phone the site header and the jump band
// covered about 27% of the screen, so the band slides away while the reader scrolls down and comes
// back when they scroll up. London's band (CityJumpStepper) carries this inline; it is here so the
// next city's bar is held to the same rules without a copy of London's component (rules/design.md
// own-components-per-page). Manchester's question bar (CityQuestionBar) is the first caller.
//
// The rules, each from London's harden passes:
//   - `--strip-h` is the bar's measured height (0 while it is hidden at a desktop width), the
//     variable `[id] { scroll-margin-top }` reads, so a jump never lands under the bar.
//   - One passive scroll listener, throttled to a frame, reads only `scrollY` (no layout read) and
//     toggles `data-tucked`; the component's CSS moves the bar with `transform`, never `top`.
//   - It is held shown while `held()` says so (an open sheet, a keyboard focus inside), and at the
//     top of the page. `scrollY` is clamped to the real range: an iOS fling rubber-bands past
//     either end, and the bounce back is not a scroll (Task 10b review, item 3).
//   - Two scrolls inside one frame are one scroll to it (lessons entry 20): the render probes
//     scroll through `scrollSettled`, which waits two frames.

/** Publish the bar's height as `--strip-h` on the root, now and whenever it changes. */
export function publishStripHeight(bar: HTMLElement, desktopFrom = 1024): void {
  const publish = () => {
    const h = bar.offsetParent === null ? 0 : Math.round(bar.getBoundingClientRect().height);
    document.documentElement.style.setProperty('--strip-h', h + 'px');
  };
  publish();
  if (typeof ResizeObserver === 'function') new ResizeObserver(publish).observe(bar);
  window.matchMedia(`(min-width: ${desktopFrom}px)`).addEventListener('change', publish);
}

/** A keyboard focus inside `el`. `:focus-visible` is a SyntaxError before Safari 15.4, so it is
 *  read in a try: there, a focus inside never holds the bar (Task 10b review, item 4). */
export function keyboardFocusInside(el: HTMLElement): boolean {
  try {
    return el.matches(':focus-within') && !!document.activeElement?.matches?.(':focus-visible');
  } catch {
    return false;
  }
}

/** Toggle `data-tucked` on `bar` as the reader scrolls: on past `top` going down, off going up or
 *  at the top; never while `held()`. Returns the function that re-reads the hold (call it when
 *  the hold may have ended, e.g. on focusin). */
export function tuckOnScroll(bar: HTMLElement, held: () => boolean, top = 64, nudge = 8): (on: boolean) => void {
  const tuck = (on: boolean) => bar.toggleAttribute('data-tucked', on && !held());
  let lastY = window.scrollY;
  let queued = false;
  window.addEventListener('scroll', () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => {
      queued = false;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const y = Math.min(Math.max(window.scrollY, 0), Math.max(max, 0));
      if (y <= top) tuck(false);
      else if (y > lastY + nudge) tuck(true);
      else if (y < lastY - nudge) tuck(false);
      else return; // too small to call a direction: keep lastY where it was
      lastY = y;
    });
  }, { passive: true });
  return tuck;
}
