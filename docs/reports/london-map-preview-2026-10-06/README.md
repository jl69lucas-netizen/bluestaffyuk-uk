# London map preview (2026-10-06)

A preview of a tap-to-load Google map on `/uk-locations/blue-staffy-puppies-london/`. **Nothing in
`src/`, `data/` or the boards was changed.** The site was built once, `dist/` was copied to the
scratchpad and served from there, and the facade was injected into that copy with Playwright and
measured with the city type-fit gate itself (`tests/render/lib/cityTypeFit.ts`, compiled
unchanged), at the city-kit harness viewports: 375×812, 768×1024 and 1280×800.

- `index.html`: the preview page ("London Map Preview"): placements, measurements, the three
  styles at three widths, the loaded state, focus, board entries and the cookie/Lighthouse note.
- `diffs.md`: the exact component, page change, components row, library row and board entries to
  apply after approval. The board entries were checked in memory against `pageboard.validate_board`.
- `*.jpg`: the screenshots (all ≤ 900px wide).
- `harness/`: the facade CSS and markup (`facade.css`, `facade.mjs`), the measurement run
  (`measure.mjs` → `results.json`), the screenshot run (`shots.mjs` → `network.json`), and
  `results-stage-360px.json`, the first run at a 360px stage, kept because it is why the stage is
  300px.

## The ask

The map target is the London row's `city` in `data/locations.json` ("London, UK", zoom 10,
`output=embed`). The facade is token-drawn, with no request to Google before a tap. It carries a
"Show the map" button (44px, keyboard, focus ring), a caption built from the `data/settings.json`
delivery fields (no drive time, no mileage), and a note that tapping loads Google Maps and its
cookies. On a tap the iframe takes the facade's box (title "London — delivery from BlueStaffyUK in
Carlisle", `loading="lazy"`, `referrerpolicy="no-referrer-when-downgrade"`).

## Placements

- **P1 (Recommended).** In the delivery chapter ("How Will My Blue Staffy Puppy Get From Carlisle
  to London?"), answer 3 ("Which Way Does My Staffordshire Puppy Travel to London?"). It goes after
  the answer's opening paragraph ("…We deliver across London, from Enfield in the north to Sutton
  in the south.") and before the past-deliveries paragraph. In the source it is the first child of
  the `ch-3` slot.
- **P2.** In the London-life chapter, answer 1 ("How Do Staffies in London Cope With Stairs, Lifts
  and Neighbours in a Flat?"), in its full-width slot. It goes under the parks H4 ("Where Can a
  Flat-Dwelling Staffy Stretch Its Legs in London's Parks?") and its paragraph, and before the
  places list.

## Measurements: the H3 answer that holds the map

The gate judges each H3 answer on its own (the breeder's ruling, answer board 2026-10-04 q10 (a)).
The cap is 2.5 viewports below 768 (2,030px at 375×812) and 1.6 viewports from 1280 (1,280px at
1280×800). **No height is judged at 768** (the gate's `tall` is `Infinity` from 768 to 1279), so
its figures are reported only.

| Width | Answer | Before | S1 / S2 (facade = loaded) | S3 facade | S3 loaded | Cap | Least headroom |
|---|---|---|---|---|---|---|---|
| 375 | P1 delivery 3 | 1,324 | 1,697 | 1,526 | 1,767 | 2,030 | 263 (S3 loaded) |
| 375 | P2 London-life 1 | 1,030 | 1,399 | 1,228 | 1,469 | 2,030 | 561 |
| 768 | P1 | 744 | 1,161 | 931 | 1,199 | none | – |
| 768 | P2 | 742 | 1,156 | 926 | 1,194 | none | – |
| 1280 | P1 | 781 | 1,199 | 969 | 1,237 | 1,280 | 43 (S3 loaded); 81 (S1/S2) |
| 1280 | P2 | 788 | 1,201 | 971 | 1,239 | 1,280 | 41 (S3 loaded); 79 (S1/S2) |

The gate ran on every scenario: 0 defects before the map, and **0 new defects in all 36
scenarios** (2 placements × 3 styles × facade and loaded × 3 widths). Every other answer's height
was unchanged. The gate examined 316 → 318 nodes at 375, 267 → 269 at 768 and 313 → 315 at 1280
(the caption and note paragraphs).

At a 360px stage (the first run), the 1280 answer was 1,259px (21px headroom), and S3 loaded was
1,337px, **over** the cap by 57px. That is why the stage is capped at 300px, and S3's live map
at 260px.

## Recommendation

**P1 + S1 (steel panel, brass pin).**

- P1 puts the map straight after the sentence it illustrates ("We deliver across London, from
  Enfield … to Sutton …"), in the chapter whose subject is delivery. The caption (the delivery
  band, DEFRA-approved transport, collection in Carlisle) is on topic there.
- In P2 the same map reads as a parks map, which it is not (a zoom-10 city centre), and the
  delivery caption is off topic. It would also push the places list, the answer's real content,
  400px further down.
- S1 and S2 reserve the map's box, so a tap moves nothing (facade height = loaded height, 81px
  headroom at 1280 in both states). S3 is the lightest facade (+188px), but it grows 268px on a
  tap and ends with 43px headroom.
- S1 over S2: on the chapters' steel-100 tray, S2's bone card repeats the bone-50 close card that
  carries the chapter's CTA pill. The steel panel reads as a different object.

**Trade-off:** S1 is the heaviest facade. It adds 418px to the 1280 answer (781 → 1,199), and the
81px left is about three more lines of copy in that answer before the gate fails at 1280.

## Network, cookies, Lighthouse

- Before the tap: **0 requests to any host but the page's own**, in every scenario (Playwright
  request log).
- After the tap (the real map, loaded once on this machine): 32 requests, ~637 KB at 375, and 44
  requests, ~895 KB at 1280. They went to maps.google.com, www.google.com, maps.googleapis.com,
  maps.gstatic.com, fonts.googleapis.com and fonts.gstatic.com (and places.googleapis.com at 1280).
- This headless Chromium recorded no cookies, because it blocks third-party cookies by default. A
  browser that allows them will receive Google's, which is why the note says so before the tap.
- Lighthouse never taps, so its lab run sees only the token-drawn panel: no third-party script, no
  third-party cookie, and nothing for Best Practices to flag (Known Issue 38 is avoided the same
  way the video facade avoids it). The cost is borne only by a reader who asks for the map.
- `public/_headers` sets `Permissions-Policy: geolocation=()`, so the embed's "your location"
  control cannot prompt. There is no CSP `frame-src` that would block the frame.

## Flags

1. Google's own info card in the loaded embed (`iwloc=near`) carries a "Directions" icon at
   desktop width. We draw no route, but Google offers one. Dropping `iwloc` is possible, but it
   departs from the skill's template.
2. The embed URL `maps.google.com/maps?…output=embed` answers 301 to
   `www.google.com/maps/embed?…` and then 200 (curl, 2026-10-06). The iframe follows it; the
   board records the URL as the skill writes it.
3. The board schema has no field for an embed. It goes on the board as an external link row of
   source type `other` (one more link, one more domain, `google.com`); see `diffs.md` §5–6.
