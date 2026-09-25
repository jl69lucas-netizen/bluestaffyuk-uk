---
name: bsuk-indexing
description: Use after ANY page is added, removed, or its rendered output changes — submits the changed URLs to IndexNow (and Google Search Console where connected) and regenerates the sitemaps (page, post, location, puppy, video) and sitemap_index.xml. Triggers - "submit to IndexNow", "index this page", "update the sitemap", end of every Sprint 5 Ship.
allowed-tools: [Read, Write, Bash]
---

# BSUK INDEXING & RESUBMISSION SKILL
## Managed Agent: Search Engine Indexing & Resubmission for BlueStaffyUK
**Version 1.0 — Post-Migration Indexing Agent**

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

> **INACTIVE UNTIL PROJECT 6.** BlueStaffyUK has no host, no domain, no remote and no
> verified search-console property. Every submission below — IndexNow, Search Console, a
> live key file, a live URL check — is **release-guarded**: it refuses without
> `BSUK_RELEASE=1` and a real `SITE_URL`. The submitter, `scripts/indexnow_submit.py`
> (`npm run indexnow`, `npm run indexnow:changed`), is ported and committed
> (`data/port-manifest.json`) and refuses with exit 2 until project 6 sets both: first
> unless `BSUK_RELEASE=1`, then unless `SITE_URL` is a real origin, not the placeholder —
> each before the key is read or a socket opened. What runs today is the sitemap half:
> `python3 scripts/generate_sitemaps.py` and `python3 scripts/sitemap_check.py` over
> `dist/`. Do not remove this notice — the day it goes is the day someone submits
> `SITE_URL_PLACEHOLDER` to IndexNow.

## SKILL OVERVIEW

You are the **Indexing Agent** for BlueStaffyUK. Your job is to ensure every page is discovered, crawled, and indexed by Google, Bing, and AI crawlers after any site update, migration, or new page creation. You operate on `dist/`; no credential value is ever written into this repo, a report, or stdout.

### Responsibilities:
- Submit sitemaps to Google Search Console
- Ping all updated URLs via IndexNow (Bing, Yandex, Google-via-proxy)
- Verify pages are not accidentally noindexed
- Fix sitemap XML issues (relative URLs, missing entries)
- Fix robots.txt and llms.txt
- Report indexing status per page

---

## SITE CONTEXT

| Property | Value |
|---|---|
| Domain | $SITE_URL |
| Local files | `dist/` |
| Sitemaps | `sitemap_index.xml`, `page-sitemap.xml`, `post-sitemap.xml`, `location-sitemap.xml`, `puppy-sitemap.xml`, `video-sitemap.xml` (written into `dist/` by `scripts/generate_sitemaps.py`) |
| IndexNow key | NOT FETCHED until project 6 (a gitignored `.env`, never this file) |
| IndexNow key file | `$SITE_URL/<indexnow-key>.txt` |
| GSC credentials | NOT FETCHED until project 6 |
| GSC Site URL | `$SITE_URL/` |

---

## STEP 1: AUDIT INDEXING SIGNALS

Before submitting, always audit for issues that block indexing:

```python
import re, glob

# dist/, and NOT a source-repo path: gates measure the BUILT page.
SITE_ROOT = "dist"
DOMAIN = "$SITE_URL"

issues = []
for fpath in glob.glob(f"{SITE_ROOT}/**/index.html", recursive=True):
    with open(fpath) as f:
        content = f.read()
    slug = fpath.replace(SITE_ROOT, '').replace('/index.html', '') or '/'
    
    # 1. Check noindex meta tag
    robots_meta = re.findall(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']*)["\']', content, re.I)
    for meta in robots_meta:
        if 'noindex' in meta.lower():
            issues.append(f"NOINDEX: {slug}")
    
    # 2. Check canonical is absolute and correct
    canonicals = re.findall(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\']', content)
    for c in canonicals:
        if not c.startswith(DOMAIN):
            issues.append(f"BAD CANONICAL: {slug} → {c}")
    
    # 3. Check for broken lazy-load images
    broken = len(re.findall(r'src="data:image/gif;base64,', content))
    if broken:
        issues.append(f"BROKEN IMGS ({broken}): {slug}")

print(f"Issues found: {len(issues)}")
for i in issues:
    print(f"  {i}")
```

### Check sitemaps for relative URLs:
```python
import re, glob

# The sitemaps are build output: scripts/generate_sitemaps.py writes them into dist/
# after every `npm run build` (the postbuild script). Nothing writes them into public/.
SITE_ROOT = "dist"
for fpath in glob.glob(f"{SITE_ROOT}/*.xml"):
    with open(fpath) as f:
        content = f.read()
    relative_locs = re.findall(r'<loc>(?!https?://)(.*?)</loc>', content)
    if relative_locs:
        print(f"RELATIVE LOCS in {fpath.split('/')[-1]}: {len(relative_locs)}")
        for r in relative_locs[:3]:
            print(f"  {r}")
```

---

## STEP 2: FIX SITEMAPS (if relative URLs found)

```python
import re, glob, os

# dist/ is where BSUK's sitemaps live: scripts/generate_sitemaps.py writes them there on
# every build (postbuild). This block WRITES, and the next build overwrites what it writes,
# so a relative <loc> is really a generator defect: fix scripts/generate_sitemaps.py too.
SITE_ROOT = "dist"
DOMAIN = "$SITE_URL"

def fix_sitemap(content):
    # Fix <loc>
    content = re.sub(r'<loc>(?!https?://)(/[^<]*)</loc>',
                     lambda m: f'<loc>{DOMAIN}{m.group(1)}</loc>', content)
    # Fix <image:loc>
    content = re.sub(r'<image:loc>(?!https?://)(/[^<]*)</image:loc>',
                     lambda m: f'<image:loc>{DOMAIN}{m.group(1)}</image:loc>', content)
    return content

for fpath in glob.glob(f"{SITE_ROOT}/*.xml"):
    original = open(fpath).read()
    fixed = fix_sitemap(original)
    if fixed != original:
        open(fpath, 'w').write(fixed)
        print(f"Fixed: {os.path.basename(fpath)}")
```

---

## STEP 3: SUBMIT TO GOOGLE SEARCH CONSOLE

### Get a fresh access token:
```python
import urllib.request, urllib.parse, json

# Load credentials
import os, re
env = open('$BSUK_DASHBOARD/.env.local').read()
client_id = re.search(r'GSC_CLIENT_ID=(.+)', env).group(1).strip()
client_secret = re.search(r'GSC_CLIENT_SECRET=(.+)', env).group(1).strip()
refresh_token = re.search(r'GSC_REFRESH_TOKEN=(.+)', env).group(1).strip()

data = urllib.parse.urlencode({
    'client_id': client_id,
    'client_secret': client_secret,
    'refresh_token': refresh_token,
    'grant_type': 'refresh_token'
}).encode()

req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data, method='POST')
with urllib.request.urlopen(req) as r:
    token_data = json.load(r)
access_token = token_data['access_token']
print(f"Access token: {access_token[:30]}...")
```

### Submit sitemaps:
```python
import urllib.request

SITE = "$SITE_URL/"
SITEMAPS = [
    "sitemap_index.xml",
    "page-sitemap.xml",
    "post-sitemap.xml",
    "location-sitemap.xml",
    "puppy-sitemap.xml",
    "video-sitemap.xml",
]

from urllib.parse import quote
site_encoded = quote(SITE, safe='')

for sm in SITEMAPS:
    sm_url = quote(f"$SITE_URL/{sm}", safe='')
    req = urllib.request.Request(
        f"https://www.googleapis.com/webmasters/v3/sites/{site_encoded}/sitemaps/{sm_url}",
        headers={"Authorization": f"Bearer {access_token}"},
        method="PUT",
        data=b""
    )
    try:
        with urllib.request.urlopen(req) as r:
            print(f"Submitted {sm}: {r.status}")
    except urllib.error.HTTPError as e:
        print(f"Error {sm}: {e.code} — {e.read().decode()}")
```

### Re-auth if refresh token is expired:
If you get `invalid_grant`, the refresh token has expired. Generate a new one:

Every credential below is read from `.env` at the repo root (gitignored, never committed);
export it with `set -a; . ./.env; set +a` before running these commands and never paste a
literal id, secret or token into this file.

1. Go to this URL (logged in as jl69lucas@gmail.com):
   `https://accounts.google.com/o/oauth2/auth?client_id=$GSC_CLIENT_ID&redirect_uri=https://developers.google.com/oauthplayground&response_type=code&scope=https://www.googleapis.com/auth/webmasters%20https://www.googleapis.com/auth/indexing&access_type=offline&prompt=consent`
2. Authorize and get the auth code from the URL
3. Exchange for refresh token:
```bash
curl -X POST https://oauth2.googleapis.com/token \
  -d "code=AUTH_CODE_HERE" \
  -d "client_id=$GSC_CLIENT_ID" \
  -d "client_secret=$GSC_CLIENT_SECRET" \
  -d "redirect_uri=https://developers.google.com/oauthplayground" \
  -d "grant_type=authorization_code"
```
4. Save the new `refresh_token` to `$BSUK_DASHBOARD/.env.local` → `GSC_REFRESH_TOKEN=`

---

## STEP 4: SUBMIT ALL URLS VIA INDEXNOW

IndexNow covers Bing, Yandex, and (via `api.indexnow.org`) partially Google.

**The submitter is `scripts/indexnow_submit.py`** (`npm run indexnow`,
`npm run indexnow:changed`; ported and release-guarded, `data/port-manifest.json`). It
refuses with exit 2 until project 6, because there is nothing to submit until BSUK has a
host and a domain: first unless `BSUK_RELEASE=1`, then unless `SITE_URL` is a real origin.
Use the committed script and never paste inline Python for this. Its forms:

```bash
python3 scripts/indexnow_submit.py <slug> [<slug> ...]   # refuses (exit 2) without BSUK_RELEASE=1
```

```bash
python3 scripts/indexnow_submit.py --changed   # refuses (exit 2) without BSUK_RELEASE=1
```

```bash
python3 scripts/indexnow_submit.py --dry-run <slug>   # refuses (exit 2) without BSUK_RELEASE=1
```

`--all` submits every sitemap URL. `--dry-run` prints the URLs it would submit and sends nothing; the key is never read or printed.

What the script ensures, and why each guard exists:

- **The key is read from `INDEXNOW_KEY` in the environment, never typed.** It comes from
  the gitignored `.env` (`docs/reference/credentials.md`) and must be 32 lowercase hex
  characters. Before anything is sent the script fetches the live key file,
  `$SITE_URL/<key>.txt`, and refuses unless it returns HTTP 200 with a body equal to the
  key (IndexNow's own requirement). That file ships from `public/<key>.txt`; the script
  itself reads nothing in `public/` — it only checks the folder exists, to know it runs
  from the repo root.
- **Every URL must return 200 before submission.** Submitting 404s is a negative trust
  signal about the host, so a dead URL is reported and dropped, not sent.
- **Build artifacts are filtered** — `/.astro/`, `/_preview/` and the rest of the `JUNK`
  prefixes in `scripts/indexnow_submit.py`. A sitemap that emits `/.astro/` is a
  `scripts/generate_sitemaps.py` defect, not a page.
- **Response codes are interpreted**: 200 OK · 202 accepted, key validation pending ·
  400 bad payload · 403 key invalid for host · 422 URLs not on this host · 429 throttled.

> **This STEP used to be broken and nobody could have noticed by reading it.** Until
> 2026-08-08 it carried inline Python with three defects from the source-repo→BSUK find/replace:
> `INDEXNOW_KEY = "a1b2c3d4e5f6789012345678blue staffies"` (a placeholder with the
> brand string substituted in — while the REAL key sat correct in the site-context table
> 170 lines above); a sitemap regex of `https://blue staffiesforsale\.com/`, a
> domain containing spaces, which matches nothing; and `SITE_ROOT` pointing at
> the source repo's build folder, **a path that exists**, so a run would have read a
> different site's sitemaps. Any execution would have POSTed an empty `urlList` under an
> invalid key and printed a success line. That is why the close-out step never actually
> ran on any page. The key now lives in exactly one place — `INDEXNOW_KEY` in the gitignored
> `.env` — and the live key file is checked against it, so defect 1 cannot come back.


## STEP 5: FIX ROBOTS.TXT

`public/robots.txt` allows every crawler and names the sitemap index:
```
User-agent: *
Allow: /
```
There is no admin, form or tag route to disallow (those Disallow rules were the source repo's
WordPress site's). A page kept out of search carries `noindex` instead — the thank-you page,
`/search/`, `/kit-preview/` and the board previews — and `scripts/generate_sitemaps.py` leaves
it out of every shard.

And sitemap entries are absolute:
```
Sitemap: $SITE_URL/sitemap_index.xml
```

---

## STEP 6: FIX LLMS.TXT

All URLs must be absolute. Run this fix:
```python
import re
from html import unescape

DOMAIN = "$SITE_URL"
with open('dist/llms.txt') as f:
    content = f.read()

# Fix relative markdown links
content = re.sub(r'\]\((/[^)]*)\)', lambda m: f']({DOMAIN}{m.group(1)})', content)
# Decode HTML entities
content = unescape(content)

with open('dist/llms.txt', 'w') as f:
    f.write(content)
print("llms.txt fixed")
```

---

## STEP 7: REPORTING FORMAT

```
## BSUK Indexing Report — [DATE]

### Submissions
- ✅ Google Search Console: [N] sitemaps submitted (sitemap_index, page, post, location, puppy, video)
- ✅ IndexNow (Bing/Yandex): [N] URLs submitted — 202 Accepted
- ⚠️ Google Indexing API: Not configured (needs service account)

### Issues Found & Fixed
- [List any noindex, canonical, broken image issues found]

### Pages Flagged Noindex (intentional)
- /thank-you-blue-staffy-puppies-journey/ — the after-enquiry page (correct)
- /search/ and /kit-preview/ — internal (correct)
- [any other page reported noindex, and whether it should be]

### Next Recommended Actions
1. Wait 3-7 days and check Google Search Console → Coverage for crawl errors
2. Check Bing Webmaster Tools for indexing progress
3. Use GSC URL Inspection for any page not appearing in search within 14 days
```

---

## KNOWN ISSUES LOG

The source repo's log, kept as history: BSUK has never been deployed (no remote until project 6).

| Date | Issue | Fix Applied | Status |
|---|---|---|---|
| 2026-04-21 | All 9 sitemap files had relative URLs (115 total) | Converted to absolute | ✅ Fixed & deployed |
| 2026-04-21 | llms.txt had relative URLs + HTML entities | Fixed to absolute + decoded | ✅ Fixed & deployed |
| 2026-04-21 | source repo: robots.txt missing its admin, form, tag and thank-you Disallow rules | Added Disallow rules | ✅ Fixed & deployed |
| 2026-04-21 | GSC refresh token expired | New auth URL generated — needs user reauth | ⚠️ Pending |
| 2026-04-21 | 86 URLs submitted to IndexNow | 202 Accepted | ✅ Done |

---

## AGENT INTEGRATION NOTES

This is the **Indexing Agent** in the BSUK agent system:

- Trigger **after every deploy** → submit new/changed URLs to IndexNow
- Trigger **after new page creation** → submit single URL immediately
- Trigger **weekly** → audit all pages for noindex/canonical issues
- Trigger **after sitemap regeneration** → resubmit to GSC

### Credentials required:
- GSC: `$BSUK_DASHBOARD/.env.local` (GSC_CLIENT_ID, GSC_CLIENT_SECRET, GSC_REFRESH_TOKEN)
- IndexNow key: `INDEXNOW_KEY` in the environment (a gitignored `.env`, never this file), checked against the live key file `$SITE_URL/<key>.txt`, which ships from `public/<key>.txt` — never typed inline. Currently NOT FETCHED until project 6 (no auth needed).
- Bing Webmaster API: Not yet configured (IndexNow covers Bing submissions)