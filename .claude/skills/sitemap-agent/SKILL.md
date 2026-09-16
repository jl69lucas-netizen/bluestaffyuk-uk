---
name: sitemap-agent
description: Regenerates all CAG sitemap XML via scripts/generate_sitemaps.py (the single source of truth — never hand-edit). Validates XML, checks for phantom/broken URLs, and submits to IndexNow + GSC. The generator writes BOTH public/ and site/content/ because deploy.yml copies site/content over public at build time.
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## Purpose

You are the **Sitemap Agent Skill** for CongoAfricanGreys.com. You keep all sitemap XML files accurate and up to date — adding new pages, updating `<lastmod>` dates, removing dead URLs, and submitting changed sitemaps to GSC.

A stale sitemap means new pages don't get indexed. Run this skill after every page addition or rebuild.

---

## On Startup — Read These First

1. **Read** `docs/reference/seo-rules.md` — canonical URL format
2. **Read** `docs/reference/site-overview.md` — domain, sitemap locations
3. **Default action:** run the generator (below). Only ask the user if they want something other than a full regenerate (e.g. validation-only or audit).

---

## ⚠️ Do NOT hand-edit sitemap XML

`scripts/generate_sitemaps.py` is the **single source of truth**. It enumerates
live pages from `src/pages/`, classifies them into shards, sets priorities +
today's `lastmod`, and guarantees zero phantom/duplicate URLs. Hand-editing a
shard will be silently overwritten the next time the generator runs.

**Critical deploy fact (the 2026-06-05 clobber bug):** `.github/workflows/deploy.yml`
copies `site/content/*.xml` → `public/*.xml` *before* the Astro build. So the
generator writes **both** `public/` and `site/content/` (via `write_both()`),
keeping them byte-identical. If you ever write only one location, the deploy
will revert your sitemap to the other (stale) copy — this is exactly what kept
live stuck on a 3-week-old sitemap. After running the generator, always confirm:
```bash
for f in page-sitemap local-sitemap post-sitemap sitemap_index sitemap; do
  cmp -s public/$f.xml site/content/$f.xml && echo "OK $f" || echo "DRIFT $f"
done
```
(See memory `project_sitemap_clobber_bug`.)

---

## Sitemap Shard Map (generated, not hand-maintained)

| File (written to BOTH public/ + site/content/) | Contents |
|------|---------|
| `page-sitemap.xml` | homepage + `/blog/` + all non-location, non-blog pages |
| `local-sitemap.xml` | location/geo pages (`african-grey-parrot-for-sale-<state>` + GEO_BUY) |
| `post-sitemap.xml` | blog posts (`src/pages/blog/*`) |
| `video-sitemap.xml` | YouTube embeds — **only file still hand-maintained** (generator preserves it in the index, doesn't rewrite it) |
| `sitemap_index.xml` | master index → the 4 shards above |
| `sitemap.xml` | mirror of the index (some crawlers fetch `/sitemap.xml`) |

Priority/changefreq tiers live in `generate_sitemaps.py` (`TIER_10/09/03`, `page_meta()`),
not in this doc — edit the script if tiers change.

---

## URL Format Rules

> ⚠️ **WordPress/Simply Static export bug:** The Rank Math sitemap plugin exports relative URLs (`/slug/`). ALWAYS convert to absolute before deploying. Batch fix: `sed -i '' 's|<loc>/|<loc>https://congoafricangreys.com/|g' file.xml` (also run for `<image:loc>`).

```xml
<!-- Correct: absolute URL, https, trailing slash -->
<url>
  <loc>https://congoafricangreys.com/[slug]/</loc>
  <lastmod>YYYY-MM-DD</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>
```

**Priority values:**
- Homepage: `1.0`
- Tier 1 pages (breed guide, adoption, purchase guide): `0.9`
- Tier 2 pages (size pages, comparisons): `0.8`
- Location pages: `0.8`
- Supporting pages (about, contact, FAQ): `0.7`
- Hub pages: `0.8`

**Changefreq values:**
- Homepage: `weekly`
- Content pages (last edited rarely): `monthly`
- Location pages: `monthly`
- Pricing pages: `weekly` (prices change)

---

## Operations

### Add / remove a page, or update lastmod — all one command
The generator reads `src/pages/` directly, so adding/removing a page dir is
automatically reflected. There is no per-page edit step.
```bash
python3 scripts/generate_sitemaps.py
```
Expected output ends with `phantom URLs (loc with no dir): NONE ✓`. If a slug
needs a non-default priority/changefreq, edit the `TIER_*` sets or `page_meta()`
in the script, then re-run.

### Validation (after every run)
```bash
# 1. public/ and site/content/ must be byte-identical (clobber guard)
for f in page-sitemap local-sitemap post-sitemap sitemap_index sitemap; do
  cmp -s public/$f.xml site/content/$f.xml && echo "OK $f" || echo "DRIFT $f"
done
# 2. XML parses
for f in page-sitemap local-sitemap post-sitemap sitemap_index sitemap; do
  python3 -c "import xml.etree.ElementTree as ET; ET.parse('public/$f.xml')" && echo "valid $f"
done
# 3. no duplicate URLs
grep -hoE "<loc>[^<]+" public/page-sitemap.xml public/local-sitemap.xml public/post-sitemap.xml | sort | uniq -d
```

---

## After Any Sitemap Change

1. Run the validation block above (identical + valid + no dupes).
2. Commit + push (push = deploy):
```bash
git add scripts/generate_sitemaps.py public/*.xml site/content/*.xml
git commit -m "fix(seo): regenerate sitemaps — <reason>"
git push origin main
```
3. **Verify it reached production** — the deploy must serve today's `lastmod`,
   not the old `site/content` bytes:
```bash
curl -s -A "Mozilla/5.0" "https://congoafricangreys.com/sitemap_index.xml?cb=$RANDOM" | grep -m1 lastmod
```
4. **Submit to IndexNow** (covers Bing/Yandex/Seznam — NOT Google). Key file
   `f8071f0dbdb94257934a690f4a18fa59.txt` is live at the domain root:
```bash
python3 - <<'PY'
import json,urllib.request,re
urls=sorted({u for f in ["public/page-sitemap.xml","public/local-sitemap.xml","public/post-sitemap.xml"]
            for u in re.findall(r"<loc>(.*?)</loc>",open(f).read())})
body=json.dumps({"host":"congoafricangreys.com","key":"f8071f0dbdb94257934a690f4a18fa59",
  "keyLocation":"https://congoafricangreys.com/f8071f0dbdb94257934a690f4a18fa59.txt","urlList":urls}).encode()
for ep in ("https://api.indexnow.org/indexnow","https://www.bing.com/indexnow"):
    r=urllib.request.urlopen(urllib.request.Request(ep,data=body,
      headers={"Content-Type":"application/json; charset=utf-8"},method="POST"),timeout=30)
    print(ep,"->",r.status,f"({len(urls)} URLs)")
PY
```
5. **For Google:** IndexNow does nothing — re-submit `sitemap_index.xml` in GSC
   (Search Console → Sitemaps). A fresh, valid sitemap clears "temporary
   processing error". "Crawled – currently not indexed" is Google's quality
   call, not a sitemap bug — it resolves over weeks, not from a resubmit.

---

## Rules

1. **Never hand-edit a shard** — run the generator; hand edits get overwritten.
2. **Always write both `public/` + `site/content/`** — the generator does this; never bypass it (deploy clobbers otherwise).
3. **Absolute URLs, trailing slash** — enforced by the generator.
4. **Validate identical + parse + no-dupes after every run.**
5. **Verify production serves today's lastmod** — local-correct ≠ live-correct.
6. **IndexNow ≠ Google** — submit to IndexNow for Bing/Yandex; use GSC for Google.
