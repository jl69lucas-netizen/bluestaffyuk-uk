---
name: bsuk-google-map
description: Use when a BSUK location or contact page needs a Google Maps embed added, replaced, or repaired — including the WordPress UAG block export bug, data-src iframe bugs and the CSP object-src blocker. Triggers - "add a map", "map is broken", "embed Google Maps", "state map on the location page".
allowed-tools: [Read, Write, Bash]
---

# BSUK Google Map Skill

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

## Purpose
Insert, fix, or update Google Maps embeds on any page of BlueStaffyUK. Covers the homepage map, location pages (state/city), and any contact/about pages. Also fixes broken WordPress `<embed>` map tags (from the UAG Google Map block export).

---

## When to Use This Skill
- Adding a Google Map to a new location page
- Fixing broken `<embed class="uagb-google-map__iframe">` tags (WordPress export bug)
- Updating map location address or zoom level
- Auditing all pages for missing/broken maps

---

## Problem: WordPress UAG Google Map Export Bug

WordPress Spectra/UAG plugin exports maps using an `<embed>` tag:

```html
<!-- BROKEN on static export -->
<div class="wp-block-uagb-google-map uagb-google-map__wrap uagb-block-XXXXX">
  <embed class="uagb-google-map__iframe" src="https://maps.google.com/maps?q=...&output=embed" width="640" height="300" loading="lazy"></embed>
</div>
```

The `<embed>` tag works inconsistently across browsers. Replace with a proper `<iframe>`.

---

## Standard Map Embed Template

Use this for any page:

```html
<div class="bsuk-map-wrap" style="max-width:800px;margin:32px auto 0;padding:0 16px;">
  <div style="border-radius:16px;overflow:hidden;box-shadow:0 6px 30px rgba(0,0,0,.12);">
    <iframe
      src="https://maps.google.com/maps?q=ENCODED_ADDRESS&z=ZOOM&hl=en&t=m&output=embed&iwloc=near"
      width="100%" height="340" style="border:0;display:block;" allowfullscreen=""
      loading="lazy" referrerpolicy="no-referrer-when-downgrade"
      title="DESCRIPTIVE TITLE">
    </iframe>
  </div>
  <p style="text-align:center;font-size:.85rem;color:#888;margin:10px 0 0;">📍 FULL ADDRESS — Serving families nationwide</p>
</div>
```

**Parameters:**
| Parameter | Value |
|---|---|
| `ENCODED_ADDRESS` | URL-encode the address — e.g. `Oak%20Plaza%2C%20Omaha%2C%20NE%2068106` |
| `ZOOM` | `12` = city-level, `13` = neighborhood, `14` = street-level, `15` = building |
| `DESCRIPTIVE TITLE` | e.g. `MFS Location — [BREEDER_LOCATION]` |

---

## MFS Standard Map (Omaha HQ)

```html
<div class="bsuk-map-wrap" style="max-width:800px;margin:32px auto 0;padding:0 16px;">
  <div style="border-radius:16px;overflow:hidden;box-shadow:0 6px 30px rgba(0,0,0,.12);">
    <iframe
      src="https://maps.google.com/maps?q=Oak%20Plaza%2C%20Omaha%2C%20NE%2068106&z=13&hl=en&t=m&output=embed&iwloc=near"
      width="100%" height="340" style="border:0;display:block;" allowfullscreen=""
      loading="lazy" referrerpolicy="no-referrer-when-downgrade"
      title="MFS Location — Oak Plaza, Omaha, NE 68106">
    </iframe>
  </div>
  <p style="text-align:center;font-size:.85rem;color:#888;margin:10px 0 0;">📍 Oak Plaza, Omaha, NE 68106 — Serving families nationwide</p>
</div>
```

---

## Location Page Map Template

For state/city location pages, use the city center as the map target:

```html
<div class="bsuk-map-wrap" style="max-width:800px;margin:32px auto 0;padding:0 16px;">
  <div style="border-radius:16px;overflow:hidden;box-shadow:0 6px 30px rgba(0,0,0,.12);">
    <iframe
      src="https://maps.google.com/maps?q=CITY%2C%20STATE&z=10&hl=en&t=m&output=embed&iwloc=near"
      width="100%" height="300" style="border:0;display:block;" allowfullscreen=""
      loading="lazy" referrerpolicy="no-referrer-when-downgrade"
      title="Blue Staffies for Sale in CITY, STATE — BlueStaffyUK">
    </iframe>
  </div>
  <p style="text-align:center;font-size:.85rem;color:#888;margin:10px 0 0;">📍 Serving CITY, STATE — delivery &amp; delivery driver delivery available</p>
</div>
```

### Common State Addresses (URL-encoded)

| State | Encoded Query |
|---|---|
| Arizona | `Arizona%2C%20UK` |
| London | `London%2C%20UK` |
| Carlisle | `Carlisle%2C%20UK` |
| Georgia | `Georgia%2C%20UK` |
| New York | `New%20York%2C%20UK` |
| Manchester | `Manchester%2C%20UK` |
| Virginia | `Virginia%2C%20UK` |
| North Carolina | `North%20Carolina%2C%20UK` |
| Illinois | `Illinois%2C%20UK` |
| Pennsylvania | `Pennsylvania%2C%20UK` |
| Ohio | `Ohio%2C%20UK` |
| Michigan | `Michigan%2C%20UK` |
| Washington | `Washington%2C%20UK` |
| Colorado | `Colorado%2C%20UK` |
| Tennessee | `Tennessee%2C%20UK` |

---

## Step 1 — Audit: Find All Map Issues

```python
import re
from pathlib import Path

SITE_DIR = Path("dist/")

broken_embed = []
proper_iframe = []
no_map = []

for html_file in SITE_DIR.rglob("*.html"):
    parts = html_file.relative_to(SITE_DIR).parts
    if parts[0] in {'.claude', '.git', 'wp-content'}:
        continue
    
    content = html_file.read_text(errors="ignore")
    page = str(html_file.relative_to(SITE_DIR))
    
    if 'uagb-google-map' in content and '<embed' in content:
        broken_embed.append(page)
    elif 'maps.google.com' in content and '<iframe' in content:
        proper_iframe.append(page)
    elif html_file.parent.name in ['UK-locations'] or 'location' in page:
        no_map.append(page)  # Location pages should have maps

print(f"Broken <embed> maps: {len(broken_embed)}")
for p in broken_embed:
    print(f"  {p}")

print(f"\nProper <iframe> maps: {len(proper_iframe)}")
print(f"\nLocation pages without maps: {len(no_map)}")
for p in no_map[:10]:
    print(f"  {p}")
```

---

## Step 2 — Fix: Replace Broken Embed Tags

```python
import re
from pathlib import Path

SITE_DIR = Path("dist/")

EMBED_RE = re.compile(
    r'<div[^>]*uagb-google-map[^>]*>\s*'
    r'<embed[^>]+src="(https://maps\.google\.com/maps\?[^"]+)"[^>]*></embed>\s*'
    r'</div>',
    re.DOTALL
)

def make_map(src_url, title="BlueStaffyUK Location"):
    return f'''<div class="bsuk-map-wrap" style="max-width:800px;margin:32px auto 0;padding:0 16px;">
  <div style="border-radius:16px;overflow:hidden;box-shadow:0 6px 30px rgba(0,0,0,.12);">
    <iframe
      src="{src_url}"
      width="100%" height="320" style="border:0;display:block;" allowfullscreen=""
      loading="lazy" referrerpolicy="no-referrer-when-downgrade"
      title="{title}">
    </iframe>
  </div>
  <p style="text-align:center;font-size:.85rem;color:#888;margin:10px 0 0;">📍 [BREEDER_LOCATION] — Serving families nationwide</p>
</div>'''

fixed_count = 0
for html_file in SITE_DIR.rglob("*.html"):
    content = html_file.read_text(errors="ignore")
    if 'uagb-google-map' not in content:
        continue
    new_content = EMBED_RE.sub(lambda m: make_map(m.group(1)), content)
    if new_content != content:
        html_file.write_text(new_content)
        fixed_count += 1
        print(f"✅ Fixed: {html_file.relative_to(SITE_DIR)}")

print(f"\nTotal fixed: {fixed_count}")
```

---

## Step 3 — Add Map to a Location Page

When creating or editing a location page, insert the map template after the main content, before the footer/CTA:

```python
from pathlib import Path

page_path = Path("src/pages/blue-staffy-puppy-for-sale-STATENAME/index.astro")
content = page_path.read_text(errors="ignore")

STATE = "Arizona"
ENCODED = "Arizona%2C%20UK"

MAP_HTML = f"""
<div class="bsuk-map-wrap" style="max-width:800px;margin:32px auto 0;padding:0 16px;">
  <div style="border-radius:16px;overflow:hidden;box-shadow:0 6px 30px rgba(0,0,0,.12);">
    <iframe
      src="https://maps.google.com/maps?q={ENCODED}&z=7&hl=en&t=m&output=embed&iwloc=near"
      width="100%" height="300" style="border:0;display:block;" allowfullscreen=""
      loading="lazy" referrerpolicy="no-referrer-when-downgrade"
      title="Blue Staffies for Sale in {STATE} — BlueStaffyUK">
    </iframe>
  </div>
  <p style="text-align:center;font-size:.85rem;color:#888;margin:10px 0 0;">📍 Serving {STATE} — delivery driver &amp; ground transport available</p>
</div>
"""

# Insert before the contact form or footer
insert_before = '<div class="site-footer'  # or another marker
if insert_before in content:
    content = content.replace(insert_before, MAP_HTML + insert_before, 1)
    page_path.write_text(content)
    print(f"✅ Map added to {STATE} page")
```

---

## Step 4 — URL Encoding Reference

To encode an address for use in the map URL:

```python
from urllib.parse import quote

address = "Phoenix, AZ, UK"
encoded = quote(address, safe='')
print(f"Encoded: {encoded}")
# → Phoenix%2C%20AZ%2C%20UK
```

---

## Step 5 — Deploy

```bash
cd dist/
git add [changed files]
git commit -m "Add/fix Google Maps on [page names]"
git push origin main
```

Then submit to IndexNow:
```python
import json, urllib.request
key = "a1b2c3d4e5f6789012345678blue staffies"
urls = ["https://SITE_URL_PLACEHOLDER/PAGE-SLUG/"]
payload = json.dumps({"host":"SITE_URL_PLACEHOLDER","key":key,
    "keyLocation":f"https://SITE_URL_PLACEHOLDER/{key}.txt","urlList":urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow",data=payload,
    headers={"Content-Type":"application/json; charset=utf-8"},method="POST")
urllib.request.urlopen(req)
```

---

## Known Fixed Issues (2026-04-21)

| Page | Fix |
|---|---|
| `index.html` (homepage) | Replaced UAG `<embed>` with styled `<iframe>` + rounded corners + address caption |

---

## Reporting Format

```
GOOGLE MAP AUDIT — SITE_URL_PLACEHOLDER
========================================
Pages audited:         103
Broken <embed> maps:   1 → fixed
Proper <iframe> maps:  1 (homepage)
Location pages added:  0

DEPLOYED: commit abc1234
```