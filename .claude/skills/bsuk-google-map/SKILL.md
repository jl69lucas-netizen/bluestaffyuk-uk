---
name: bsuk-google-map
description: Use when a BSUK page's approved board carries a Google Maps embed (the contact page, or a UK city page from data/locations.json) — the town-level embed for Carlisle, Cumbria, the city-centre embed for a city page, and the audit and source-side repair of a migrated WordPress map embed. Triggers - "add a map", "map is broken", "embed Google Maps", "city map on the location page".
allowed-tools: [Read, Write, Bash]
---

# BSUK Google Map Skill

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## When a page carries a map

A map is an outside embed, so it is on the page's approved board or it is not built
(`CLAUDE.md` rule 12). No rebuilt page carries one today, and the location frame in
`docs/reference/location-page-template.md` has none: a city page gets a map only when its
board adds it as a body section. The homepage's migrated map encoded the former street
address and was dropped (Known Issue 16); the same address is still in the migrated body of
`/uk-locations/staffy-breeding-dogs-glasgow/` (Known Issue 55) and is never carried into
its rebuild.

A map names a town, never a street, a postcode or coordinates: `data/settings.json` `address`
is `{city: Carlisle, region: Cumbria, country: GB}` and holds nothing finer.

An embed loads Google's own scripts and cookies with the page, which costs Lighthouse Best
Practices the way the breed guide's video player does (Known Issue 38). Offer a click-to-load
facade on the board as the default, the same choice working rule 14 makes for video.

---

## Template — the breeder (Carlisle, Cumbria)

```astro
<section id="find-us" data-section-label="Where We Are">
  <h2>{heading from the board}</h2>
  <div class="map">
    <iframe
      src="https://maps.google.com/maps?q=Carlisle%2C%20Cumbria&z=12&hl=en&t=m&output=embed&iwloc=near"
      width="800" height="340" loading="lazy" referrerpolicy="no-referrer-when-downgrade"
      title="BlueStaffyUK — Carlisle, Cumbria" allowfullscreen></iframe>
  </div>
</section>
```

Style `.map` in the page's own `<style>` from the tokens in `src/styles/tokens.css` — never a
hex, never an inline `style=""`, never an emoji pin (`rules/design.md`). A caption, if the
board has one, is the delivery fact from `data/settings.json`: £200–£350 by distance, by
DEFRA-approved transport, or collection from Carlisle.

---

## Template — a UK city page

The target is the city centre, read from the row's `city` in `data/locations.json`, never
typed by hand:

```python
import json
from urllib.parse import quote

SLUG = "blue-staffy-puppies-manchester-uk"
row = next(r for r in json.load(open("data/locations.json")) if r["slug"] == SLUG)
query = quote(f"{row['city']}, UK", safe="")          # Manchester%2C%20UK
src = f"https://maps.google.com/maps?q={query}&z=10&hl=en&t=m&output=embed&iwloc=near"
title = f"{row['city']} — delivery from BlueStaffyUK in Carlisle"
print(src, title, sep="\n")
```

The map shows where the buyer is; it never implies BlueStaffyUK is there. No drive time, no
mileage and no route line (`.claude/skills/bsuk-location-page-builder/SKILL.md`, "UK
geography").

---

## Audit — maps in the build

Maps are checked in the BUILT output, never in `src/` alone:

```python
import pathlib
import re

for f in sorted(pathlib.Path("dist").rglob("index.html")):
    html = f.read_text(errors="ignore")
    for tag, src in re.findall(r'<(iframe|embed)[^>]+src="([^"]*google\.[a-z.]+/maps[^"]*)"', html):
        print(f.parent.relative_to("dist"), "BROKEN <embed>" if tag == "embed" else "iframe", src[:120])
```

A migrated WordPress body can carry the Spectra/UAG block
(`<embed class="uagb-google-map__iframe">`), which renders inconsistently. The repair is made
in the page's SOURCE when the page is rebuilt, on its board — never by rewriting `dist/`,
which the next build overwrites. A street, a postcode or coordinates in a map URL is a Known
Issue 16 defect: drop it and log it in the board record's `dropped.embeds`.

---

## Commit

Commit after the build and the gates pass. There is no push, no deploy and no IndexNow
submission until project 6 (`.claude/skills/bsuk-indexing/SKILL.md`).
