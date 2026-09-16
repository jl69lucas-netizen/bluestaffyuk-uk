---
name: bsuk-youtube
description: Use when a BSUK page has a YouTube embed to add, fix or optimize — repairs data-src iframe bugs from the WordPress migration, adds VideoObject schema, and manages video-sitemap.xml. Triggers - "YouTube embed", "video not playing", "video sitemap", "VideoObject schema".
allowed-tools: [Read, Write, Bash]
---

# BSUK YouTube Agent Skill

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

## Purpose
Audit, fix, and optimize all YouTube video embeds and the video sitemap on BlueStaffyUK. Covers WordPress migration issues plus ensures video SEO is optimized for puppy-related content.

---

## When to Use This Skill
- After WordPress-to-static export (YouTube iframes stop loading)
- When GSC reports video sitemap errors (invalid URLs, missing thumbnails)
- When adding new YouTube videos to any page
- After uploading new YouTube videos for MFS (update sitemap + embeds)

---

## Problem: WordPress Lazy-Load iframe Bug

WordPress exports YouTube iframes with `data-src` instead of `src`. On static HTML, there is no JavaScript to swap them — videos never load, showing a blank box.

**Broken (WordPress export):**
```html
<iframe class="lazyload" data-src="https://www.youtube.com/embed/VIDEO_ID"
  width="560" height="315" frameborder="0" allowfullscreen></iframe>
```

**Fixed (static HTML):**
```html
<iframe width="560" height="315"
  src="https://www.youtube.com/embed/VIDEO_ID?rel=0&modestbranding=1"
  title="VIDEO TITLE" frameborder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowfullscreen loading="lazy"></iframe>
```

---

## Step 1 — Audit: Find All Broken YouTube Iframes

Run this Python script from inside `dist/`:

```python
import os, re
from pathlib import Path

SITE_DIR = Path("dist/")
IFRAME_RE = re.compile(r'<iframe[^>]+(?:data-src|src)=["\']([^"\']*youtube[^"\']*)["\'][^>]*>', re.IGNORECASE)

broken = {}  # {page: [video_ids]}
fixed  = {}

for html_file in SITE_DIR.rglob("*.html"):
    content = html_file.read_text(errors="ignore")
    for m in re.finditer(r'<iframe[^>]+(?:data-src|src)=["\']([^"\']*youtube\.com/embed/([^"\'?&\s]+))["\'][^>]*>', content, re.IGNORECASE):
        full_tag = m.group(0)
        vid_id = m.group(2)
        page = str(html_file.relative_to(SITE_DIR))
        if 'data-src' in full_tag.lower():
            broken.setdefault(page, []).append(vid_id)
        else:
            fixed.setdefault(page, []).append(vid_id)

print(f"\nBROKEN YouTube iframes (data-src): {sum(len(v) for v in broken.values())} across {len(broken)} pages")
for page, ids in sorted(broken.items()):
    for vid in ids:
        print(f"  {page}: {vid}")

print(f"\nWorking YouTube iframes (src): {sum(len(v) for v in fixed.values())} across {len(fixed)} pages")
```

---

## Step 2 — Fix: Batch Replace data-src → src

```python
import re
from pathlib import Path

SITE_DIR = Path("dist/")

def fix_youtube_iframes(content):
    """Replace any YouTube iframe using data-src with a proper src iframe."""
    def replace_iframe(m):
        full_tag = m.group(0)
        # Extract video ID
        vid_match = re.search(r'(?:data-src|src)=["\']https://(?:www\.)?youtube\.com/embed/([^"\'?&\s]+)', full_tag, re.I)
        if not vid_match:
            return full_tag
        vid_id = vid_match.group(1)
        # Extract title if present
        title_match = re.search(r'title=["\']([^"\']+)["\']', full_tag)
        title = title_match.group(1) if title_match else "MFS Blue Staffy puppy Video"
        # Extract dimensions
        w_match = re.search(r'width=["\'](\d+)["\']', full_tag)
        h_match = re.search(r'height=["\'](\d+)["\']', full_tag)
        w = w_match.group(1) if w_match else "560"
        h = h_match.group(1) if h_match else "315"
        return (f'<iframe width="{w}" height="{h}" '
                f'src="https://www.youtube.com/embed/{vid_id}?rel=0&modestbranding=1" '
                f'title="{title}" frameborder="0" '
                f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
                f'allowfullscreen loading="lazy"></iframe>')
    
    IFRAME_RE = re.compile(r'<iframe[^>]+(?:data-src=["\'][^"\']*youtube[^"\']*["\'])[^>]*>', re.IGNORECASE)
    return IFRAME_RE.sub(replace_iframe, content)

count = 0
for html_file in SITE_DIR.rglob("*.html"):
    content = html_file.read_text(errors="ignore")
    if 'data-src' in content.lower() and 'youtube' in content.lower():
        new_content = fix_youtube_iframes(content)
        if new_content != content:
            html_file.write_text(new_content)
            count += 1
            print(f"✅ Fixed: {html_file.relative_to(SITE_DIR)}")

print(f"\nTotal pages fixed: {count}")
```

---

## Step 3 — Add a New Video to a Page

When adding a YouTube video to any page, use this embed pattern:

```html
<div class="video-wrap" style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:12px;margin:24px 0">
  <iframe
    style="position:absolute;top:0;left:0;width:100%;height:100%"
    src="https://www.youtube.com/embed/VIDEO_ID?rel=0&modestbranding=1"
    title="DESCRIPTIVE TITLE — BlueStaffyUK"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen
    loading="lazy">
  </iframe>
</div>
```

Replace `VIDEO_ID` with the 11-character YouTube ID (from the URL after `watch?v=`).

---

## Step 4 — Update video-sitemap.xml

File location: `dist/video-sitemap.xml`

### Rules for Google compliance:
- `<video:uploader info="...">` — `info` must be an **absolute URL** (not relative path)
- `<video:thumbnail_loc>` — **required** for every video entry; must be absolute URL
- `<video:content_loc>` — absolute URL to mp4/webm file (for hosted videos)
- `<video:player_loc>` — YouTube embed URL (for YouTube videos)
- `<loc>` — the page URL embedding the video (absolute)

### Template for a YouTube video entry:
```xml
<url>
  <loc>https://SITE_URL_PLACEHOLDER/PAGE-SLUG/</loc>
  <video:video>
    <video:title><![CDATA[VIDEO TITLE]]></video:title>
    <video:description><![CDATA[VIDEO DESCRIPTION]]></video:description>
    <video:player_loc>https://www.youtube.com/embed/VIDEO_ID</video:player_loc>
    <video:thumbnail_loc>https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg</video:thumbnail_loc>
    <video:publication_date>2025-12-09T00:00:00+00:00</video:publication_date>
    <video:duration>SECONDS</video:duration>
    <video:tag><![CDATA[blue staffies for sale]]></video:tag>
    <video:family_friendly>yes</video:family_friendly>
    <video:uploader info="https://SITE_URL_PLACEHOLDER/about/">BlueStaffyUK</video:uploader>
  </video:video>
</url>
```

### Template for a hosted mp4 video entry:
```xml
<url>
  <loc>https://SITE_URL_PLACEHOLDER/PAGE-SLUG/</loc>
  <video:video>
    <video:title><![CDATA[VIDEO TITLE]]></video:title>
    <video:description><![CDATA[VIDEO DESCRIPTION]]></video:description>
    <video:content_loc>https://SITE_URL_PLACEHOLDER/content/uploads/YYYY/MM/video.mp4</video:content_loc>
    <video:thumbnail_loc>https://SITE_URL_PLACEHOLDER/content/uploads/thumbnail.jpg</video:thumbnail_loc>
    <video:family_friendly>yes</video:family_friendly>
    <video:uploader info="https://SITE_URL_PLACEHOLDER/about/">BlueStaffyUK</video:uploader>
  </video:video>
</url>
```

### Getting YouTube thumbnails (always absolute):
- Max quality: `https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg`
- HQ fallback: `https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg`

---

## Step 5 — Audit video-sitemap.xml for Errors

```python
import re
from pathlib import Path

content = Path("dist/video-sitemap.xml").read_text()

# Check for relative info= attributes (should be absolute URLs)
relative_info = re.findall(r'info="(/[^"]+)"', content)
if relative_info:
    print(f"❌ Relative info= URLs ({len(relative_info)}): {relative_info}")
else:
    print("✅ All info= URLs are absolute")

# Check for missing thumbnail_loc
video_blocks = re.findall(r'<video:video>.*?</video:video>', content, re.DOTALL)
missing_thumb = 0
for i, block in enumerate(video_blocks, 1):
    if '<video:thumbnail_loc>' not in block:
        title = re.search(r'<video:title><!\[CDATA\[(.*?)\]\]>', block)
        t = title.group(1)[:60] if title else f"Video #{i}"
        print(f"❌ Missing thumbnail_loc: {t}")
        missing_thumb += 1

if not missing_thumb:
    print("✅ All video entries have thumbnail_loc")

print(f"\nTotal video entries: {len(video_blocks)}")
```

---

## Step 6 — Deploy and Submit

```bash
cd dist/
git add video-sitemap.xml [any .html files fixed]
git commit -m "Fix YouTube iframes and video sitemap"
git push origin main
# the host (NOT FETCHED until project 6) auto-deploys in 1-3 min
```

Then submit changed video pages to IndexNow:

```python
import json, urllib.request

key = "a1b2c3d4e5f6789012345678blue staffies"
urls = [
    "https://SITE_URL_PLACEHOLDER/",
    # Add any other pages with fixed YouTube embeds
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

After deploy, resubmit `video-sitemap.xml` in Google Search Console:
> GSC → Sitemaps → video-sitemap.xml → Resubmit

---

## MFS YouTube Channel / Video Inventory

| Video ID | Title | Used On Pages |
|---|---|---|
| `MTHXZlZtIk0` | THE BEST 2026 Blue Staffy puppies For Sale (main promo) | Homepage |
| `ZP7tjkzFgbs` | How Much Does a Blue Staffy puppy ACTUALLY Cost? | Homepage |

### Adding New Videos Checklist:
1. Upload video to YouTube / get Video ID
2. Add embed to relevant page(s) using responsive wrapper template
3. Add entry to `video-sitemap.xml` with thumbnail_loc
4. Deploy + push to GitHub
5. Submit pages to IndexNow
6. Resubmit video-sitemap.xml in GSC

---

## Known Fixed Issues (2026-04-21)

| Issue | Fix |
|---|---|
| Homepage YouTube iframes using `data-src` (lazy-load bug) | Fixed `data-src` → `src` on 2 iframes |
| video-sitemap.xml: 9 relative `info=` attributes | Made absolute with `https://SITE_URL_PLACEHOLDER` prefix |
| video-sitemap.xml: 1 missing `thumbnail_loc` (MTHXZlZtIk0) | Added `https://i.ytimg.com/vi/MTHXZlZtIk0/maxresdefault.jpg` |
| video-sitemap.xml: 6 mp4 entries missing `thumbnail_loc` | Added site thumbnail to all mp4 entries |

---

## Reporting Format

After running this skill, output:

```
YOUTUBE AUDIT — SITE_URL_PLACEHOLDER
=====================================
Pages scanned:          103
Broken iframes fixed:   2
Pages with YouTube:     1 (homepage)

VIDEO SITEMAP:
  Total entries:        9
  Relative info= fixed: 9 → 0
  Missing thumbnails:   8 → 0

DEPLOYED: commit abc1234
INDEXNOW: 202 (success) — 1 URL submitted
GSC: Resubmit video-sitemap.xml manually in Search Console
```