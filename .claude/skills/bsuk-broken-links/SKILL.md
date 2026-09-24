---
name: bsuk-broken-links
description: Use when any BSUK page has a broken internal link, dead image src, wrong canonical, or a 404 in the live-site sweep — audits every built page in dist/ (and legacy dist/) for broken anchors, image paths and canonicals, then fixes them and records redirects. Triggers - "broken link", "404", "dead image", "link check", "canonical wrong".
allowed-tools: [Read, Write, Bash]
---

# BSUK Broken Internal Links Agent Skill

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

## Purpose
Audit all HTML pages in `dist/` for broken internal links, then fix them by:
1. Adding redirect rules to `_redirects` for moved/nested paths
2. Creating missing `index.html` hub pages for directory URLs
3. Removing or correcting links to WordPress remnants

---

## When to Use This Skill
- After any new pages are added or removed
- After a WordPress-to-static migration
- When Google Search Console reports crawl errors (404s)
- Scheduled monthly audit

---

## Step 1 — Audit: Find All Broken Internal Links

Run this Python script from inside `dist/`:

```python
import os, re
from pathlib import Path

SITE_DIR = Path("dist/")
LINK_RE = re.compile(r'href="(/[^"#?]*)"')

# Build set of all valid paths (directories with index.html OR files)
valid_paths = set()
for root, dirs, files in os.walk(SITE_DIR):
    for f in files:
        if f == "index.html":
            rel = Path(root).relative_to(SITE_DIR)
            slug = "/" + str(rel) + "/" if str(rel) != "." else "/"
            valid_paths.add(slug.replace("//", "/"))

# Read existing _redirects to know what's already handled
redirects_src = set()
redirects_file = SITE_DIR / "_redirects"
if redirects_file.exists():
    for line in redirects_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split()
            if parts:
                redirects_src.add(parts[0])

broken = {}  # {link: [pages that contain it]}

for html_file in SITE_DIR.rglob("*.html"):
    content = html_file.read_text(errors="ignore")
    for link in LINK_RE.findall(content):
        # Normalize: ensure trailing slash for directory-style links
        if "." not in link.split("/")[-1]:  # no file extension = directory
            if not link.endswith("/"):
                link = link + "/"
        if link in valid_paths:
            continue
        if link in redirects_src:
            continue
        # Skip external-looking or asset paths
        if any(link.startswith(p) for p in ["/wp-content/", "/wp-admin/", "/feed", "/tag/"]):
            continue
        page = str(html_file.relative_to(SITE_DIR))
        broken.setdefault(link, []).append(page)

print(f"\nBROKEN INTERNAL LINKS ({len(broken)} unique):\n")
for link, pages in sorted(broken.items()):
    print(f"  {link}")
    for p in pages[:3]:
        print(f"    └─ {p}")
    if len(pages) > 3:
        print(f"    └─ ...and {len(pages)-3} more")
```

---

## Step 2 — Categorize Each Broken Link

For each broken link found, decide the fix:

| Category | Example | Fix |
|---|---|---|
| Nested WP CPT path | `/available-puppies/` | Add redirect to flat slug |
| WordPress remnant | `/comments/feed/`, `/tag/*/` | Redirect to `/` |
| Missing hub page | `/UK-locations/` | Create `index.html` hub |
| Completely missing page | `/some-deleted-page/` | Redirect to best match or homepage |

---

## Step 3A — Fix: Add Redirects to `_redirects`

Append to `data/redirects.json`:

```
# Nested WordPress CPT paths → flat slugs
/available-puppies/    /blue-staffy-pup-sale-uk/    301
/available-puppies/    /buy-staffy-puppies-for-sale-uk/    301

# WordPress remnants → homepage
/comments/feed/     /     301
/comments/feed      /     301
```

**Rules for `_redirects`:**
- Always add both `/path/` (trailing slash) and `/path` (no trailing slash) variants
- Use `301` (permanent) for SEO — not `302`
- Put more-specific rules ABOVE catch-all rules
- The `!` suffix forces a redirect even if the edge host (chosen in project 6) finds a matching file

---

## Step 3B — Fix: Create Missing Hub Pages

When a directory like `/UK-locations/` has child pages but no `index.html`, create a hub:

```html
<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>[Hub Title] | BlueStaffyUK</title>
<meta name="description" content="[Hub description]">
<meta name="robots" content="follow, index, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="https://SITE_URL_PLACEHOLDER/[hub-slug]/">
<meta property="og:url" content="https://SITE_URL_PLACEHOLDER/[hub-slug]/">
<style>
/* Standalone page: it is outside src/, so it cannot resolve the project's var()s.
   Spell the hexes here, and keep them equal to src/styles/tokens.css. */
body { font-family: 'Source Sans 3', sans-serif; background: #F4F1EA; /* = --color-surface */
       color: #1B2430; /* = --color-text */ margin: 0; }
.hub { max-width: 900px; margin: 60px auto; padding: 0 20px; }
h1 { font-family: 'Fraunces', serif; color: #1F3A52; /* = --color-brand in src/styles/tokens.css */ }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
.card { background: #FFFFFF; border: 1px solid #DAD6CC; /* = --color-border */ border-radius: 10px;
        padding: 18px 20px; text-decoration: none;
        color: #1F3A52; /* = --color-brand in src/styles/tokens.css */ font-weight: 600; }
.card:hover { color: #14202B; /* = --color-cta-ink */ box-shadow: 0 4px 18px rgba(20,32,43,.15); }
</style>
</head>
<body>
<div class="hub">
  <h1>[Hub H1]</h1>
  <p>[Short intro — 1-2 sentences with target keyword]</p>
  <div class="grid">
    <a class="card" href="/child-page-1/">Child Page Title 1</a>
    <a class="card" href="/child-page-2/">Child Page Title 2</a>
  </div>
</div>
</body>
</html>
```

**Critical rules for hub pages:**
- `canonical` must be absolute: `https://SITE_URL_PLACEHOLDER/slug/`
- `og:url` must be absolute
- No schema JSON-LD required for hub pages (optional)
- H1 must contain the target keyword

---

## Step 4 — Verify Fixes

After adding redirects and/or hub pages, re-run the audit script from Step 1. Broken count should be 0.

```bash
# Quick check — count remaining broken links after fix
python3 scripts/redirect_check.py 2>/dev/null | grep "BROKEN" | head -1
```

---

## Step 5 — Deploy

```bash
cd dist/
# Stage changes and deploy via the BSUK deployment process
# (Deploy method TBD — Phase 2)
```

---

## Step 6 — Submit Changed URLs to IndexNow

```python
import json, urllib.request

key = "[INDEXNOW_KEY_TBD]"
urls = [
    # List the slugs that were fixed or created
    "https://SITE_URL_PLACEHOLDER/UK-locations/",
    # ...add any pages whose internal links were fixed
]
payload = json.dumps({
    "host": "SITE_URL_PLACEHOLDER",
    "key": key,
    "keyLocation": f"https://SITE_URL_PLACEHOLDER/{key}.txt",
    "urlList": urls
}).encode()
req = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=payload,
    headers={"Content-Type": "application/json; charset=utf-8"},
    method="POST"
)
resp = urllib.request.urlopen(req)
print(f"IndexNow: {resp.status}")  # 202 = success
```

---

## Known Fixed Issues (2026-04-21)

| Broken Path | Fixed By | Target |
|---|---|---|
| `/UK-locations/` (no index.html) | Created hub page | `/UK-locations/index.html` |
| `/available-puppies/` | `_redirects` 301 | `/blue-staffy-pup-sale-uk/` |
| `/available-puppies/` | `_redirects` 301 | `/buy-staffy-puppies-for-sale-uk/` |
| `/comments/feed/` | `_redirects` 301 | `/` |

---

## Reporting Format

After running this skill, output a summary like:

```
BROKEN LINKS AUDIT — SITE_URL_PLACEHOLDER
==========================================
Pages scanned:        103
Unique broken links:  14
Already redirected:   2
Fixed this run:       12

FIXES APPLIED:
  ✅ Created /UK-locations/index.html (hub page)
  ✅ Added 9 redirect rules to _redirects
  ✅ Added 2 WordPress remnant redirects

REMAINING (manual review needed):
  ⚠️  /some-external-looking-path/ — appears in 3 pages
```