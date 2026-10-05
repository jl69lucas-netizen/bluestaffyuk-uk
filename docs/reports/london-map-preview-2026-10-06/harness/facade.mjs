// The facade markup for the preview, one function per style. Facts mirror data/settings.json
// (delivery_min_gbp 200, delivery_max_gbp 350, address.city Carlisle) and data/locations.json
// (London row `city`); the Astro diff in diffs.md reads them from those files instead.
export const CITY = 'London';
export const SRC = `https://maps.google.com/maps?q=${encodeURIComponent(`${CITY}, UK`)}&z=10&hl=en&t=m&output=embed&iwloc=near`;
export const TITLE = `${CITY} — delivery from BlueStaffyUK in Carlisle`;
export const CAP = 'We deliver from Carlisle for £200–£350, priced by distance, by DEFRA-approved transport, or you collect your puppy from us in Carlisle.';
export const NOTE = 'Nothing loads from Google until you tap. Showing the map loads Google Maps, which sets its own cookies.';

const PIN = `<svg class="cm-pin" viewBox="0 0 32 42" aria-hidden="true" focusable="false"><path class="body" d="M16 1.5C8 1.5 1.5 7.9 1.5 15.8 1.5 26.6 16 40.5 16 40.5s14.5-13.9 14.5-24.7C30.5 7.9 24 1.5 16 1.5z"/><circle class="dot" cx="16" cy="15.6" r="5.4"/></svg>`;
const PIN_LINE = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>`;
const MAP_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M1 6v16l7-4 8 4 7-4V2l-7 4-8-4-7 4z"/><path d="M8 2v16M16 6v16"/></svg>`;
// S1: contour rings and a soft river band, abstract (no real geography, no route line).
const ART_S1 = `<svg class="cm-art" viewBox="0 0 400 240" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false"><g fill="none" stroke="currentColor"><path d="M-20 168C50 132 104 190 168 160S262 98 324 132 396 156 430 124" stroke-width="14" opacity=".45" stroke-linecap="round"/><g stroke-width="1.2" opacity=".75"><ellipse cx="200" cy="112" rx="60" ry="44"/><ellipse cx="200" cy="112" rx="112" ry="80"/><ellipse cx="200" cy="112" rx="170" ry="118"/><ellipse cx="200" cy="112" rx="232" ry="160"/></g></g></svg>`;
// S2: a line-map motif: a grid of streets, two rings and a river line, all hairlines.
const ART_S2 = `<svg class="cm-art" viewBox="0 0 400 240" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false"><g fill="none" stroke="currentColor" stroke-linecap="round"><g stroke-width="1" opacity=".8"><path d="M0 40H400M0 80H400M0 160H400M0 200H400M60 0V240M120 0V240M280 0V240M340 0V240"/></g><g stroke-width="1.6"><circle cx="200" cy="116" r="58"/><circle cx="200" cy="116" r="104"/><path d="M200 0V58M200 174V240M0 116H142M258 116H400M40 0L159 75M241 157L360 240M360 0L241 75M159 157L40 240"/></g><path d="M-10 150C60 126 110 176 170 150S262 100 322 132 392 150 420 124" stroke-width="5"/></g></svg>`;

const figure = (style, inner, after = '') => `
<figure class="city-map cm-${style}" data-city-map data-map-src="${SRC}" data-map-title="${TITLE}">
  ${inner}
  <figcaption>
    <p class="cm-cap">${CAP}</p>
    <p class="cm-note" id="cm-note-${style}">${NOTE}</p>
  </figcaption>
  <noscript><p class="cm-note"><a href="${SRC}" target="_blank" rel="noopener noreferrer">Open the map of ${CITY} on Google Maps</a></p></noscript>
</figure>`;

export function facade(style) {
  const btn = `<button type="button" class="cm-load" aria-describedby="cm-note-${style}">${MAP_ICON}Show the map</button>`;
  if (style === 's1') return figure('s1', `<div class="cm-stage">${ART_S1}${PIN}<span class="cm-place">${CITY}</span>${btn}</div>`);
  if (style === 's2') return figure('s2', `<div class="cm-stage">${ART_S2}${PIN}<span class="cm-place">${CITY}</span>${btn}</div>`);
  return figure('s3', `<div class="cm-strip"><span class="cm-disc">${PIN_LINE}</span><span class="cm-strip-t"><span class="cm-strip-city">${CITY}</span> <span class="cm-strip-sub">on Google Maps</span></span>${btn}</div>`);
}

// The tap handler (the component's <script>), as a string to inject. In the measurement runs the
// iframe gets about:blank (same reserved box) so no Google request is made; the loaded-state
// screenshot sets window.__realMap = true.
export const HANDLER = `
document.querySelectorAll('[data-city-map]').forEach((fig) => {
  const btn = fig.querySelector('.cm-load');
  btn.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.src = window.__realMap ? fig.dataset.mapSrc : 'about:blank';
    f.title = fig.dataset.mapTitle;
    f.loading = 'lazy';
    f.referrerPolicy = 'no-referrer-when-downgrade';
    f.allowFullscreen = true;
    f.className = 'cm-frame';
    let stage = fig.querySelector('.cm-stage');
    if (!stage) { stage = document.createElement('div'); stage.className = 'cm-stage'; fig.querySelector('.cm-strip').after(stage); }
    stage.classList.add('cm-live');
    stage.replaceChildren(f);
    btn.remove();
    fig.setAttribute('data-loaded', '');
    f.focus();
  }, { once: true });
});`;
