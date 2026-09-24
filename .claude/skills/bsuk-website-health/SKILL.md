---
name: bsuk-website-health
description: Technical site audit and auto-fixer for BlueStaffyUK. Astro → the edge host (chosen in project 6). Checks build, canonicals, images and built-output hygiene. The git-remote, deploy and live-site halves are INACTIVE UNTIL PROJECT 6 — BSUK has no remote, no host and no domain. Runs scripts/health-sweep.sh as the one-command sweep.
allowed-tools: [Read, Write, Bash]
---

# BSUK WEBSITE HEALTH & TECHNICAL FIX SKILL
## Technical Site Auditor & Auto-Fixer for BlueStaffyUK
**Version 2.0 — Astro static build. Host NOT FETCHED until project 6.**

> **Half of this skill is inactive.** BSUK has no git remote, no host, no domain and no
> deploy workflow until project 6. Every step below that pushes, checks a live URL, reads a
> host dashboard or rotates a hosting credential is **deferred to project 6**. What runs
> today: the build, `dist/` hygiene, canonicals, images and the agent-integrity check.

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the task genuinely cannot be done with Claude Code alone.

---

## SITE CONTEXT (authoritative — do not use v1's old values)

| Property | Value |
|---|---|
| Domain | `https://SITE_URL_PLACEHOLDER` — the real host is NOT FETCHED until project 6 |
| Stack | **Astro** static build |
| Host | **NOT FETCHED until project 6** |
| Deploy | NOT FETCHED until project 6. There is no remote and no workflow; never `git push` |
| **Authoritative pages** | **`src/pages/`** — the routes in `data/page-map.json` |
| Built output (what ships) | **`dist/**/index.html`** |
| `dist/` | The only built state. Scan it, never `src/`, for what actually ships |
| Redirects | `data/redirects.json` → `scripts/build_redirects.py`; the host's own format is NOT FETCHED until project 6 |
| Headers | NOT FETCHED until project 6 — no host, so no header file format yet |
| Brand assets | `src/assets/puppies/` (astro:assets masters, project 3), `public/` |
| Hero images | There is no hero asset directory and none is planned: the hero components import a puppy master from `src/assets/puppies/` until project 4 supplies a real hero photo |

> ⚠️ v1 of this skill hardcoded an absolute path into a sibling source repo, the domain
> "blue staffiesforsale.com", and Netlify. All three were wrong. Never
> reintroduce them.

---

## STEP 0: THE ONE-COMMAND SWEEP (do this first)

For any "is the site healthy?" request, run the full sweep:

```bash
bash scripts/health-sweep.sh            # full sweep (runs npm run build)
bash scripts/health-sweep.sh --no-build # faster, skips the build
```

It checks, in order, and exits non-zero on any critical failure:
1. **Git state** — a token in a remote URL, and uncommitted files. Its ahead-of-origin WARN means nothing until project 6 adds a remote — ignore it
2. **Agent integrity** — every agent in `.claude/agents/` has `name`/`description`/`model` (`npm run agents`)
3. **Astro build** — `npm run build` compiles; reports page count
4. **Live site** — deferred to project 6; there is no live site to fetch
5. **Built-output hygiene** — scans `dist/` for broken lazy-load images, missing/relative canonicals

Only drop into the manual steps below when the sweep flags something or you need
a deeper look (CWV, page-speed, a specific fix).

---

## STEP 0.5: GIT / DEPLOY / SECRET-LEAK HEALTH

Sweep section 1 covers this. The fix procedures for what it flags:

### Token embedded in git remote URL (CRITICAL)
A token in `.git/config`'s remote URL (`https://user:ghp_...@github.com/...`) is a
credential leak — plaintext on disk, and it lands in any transcript that prints the remote.

**Fix (agent does the local half; USER must rotate):**
**Deferred to project 6.** This repo has no remote, so there is no remote URL to leak a
token into and nothing to push. When a remote is added in project 6:

1. **The breeder rotates** the token in the provider dashboard (revoke + regenerate). An
   agent must NOT delete or create tokens — that is a security-settings change.
2. Auth goes in the OS credential helper, never in the remote URL and never in a file.
3. No credential value may appear in any committed file, report or on stdout.

`docs/reference/credentials.md` says which script reads which key.

### Uncommitted work
`CLAUDE.md` rule 3: commit after every task and never push — there is no remote until
project 6. The sweep WARNs on a dirty tree.
Build artifacts (`dist/`, `.astro/`, `node_modules/`, `.build-extract/`) and key files
(`.env`, `.*-key`) are gitignored — confirm with `git check-ignore <path>` before committing.

---

## STEP 1: DIAGNOSE (manual / deeper checks)

### A. Broken lazy-load images (WordPress GIF placeholders)
Legacy export artifact — `src` is a 1×1 GIF, real URL in `data-src`. Scan the **built output**:

```python
import re, glob
DIST = "dist"
broken = []
for f in glob.glob(f"{DIST}/**/index.html", recursive=True):
    c = open(f, encoding="utf-8", errors="ignore").read()
    n = len(re.findall(r'src="data:image/gif;base64,[^"]*"', c))
    if n: broken.append((f.replace(DIST, ""), n))
print(f"Pages with broken imgs: {len(broken)}, Total: {sum(n for _, n in broken)}")
```

### B. Relative canonical tags
Every canonical must be an absolute `https://SITE_URL_PLACEHOLDER/...` URL.

```python
import re, glob
DIST = "dist"
for f in glob.glob(f"{DIST}/**/index.html", recursive=True):
    c = open(f, encoding="utf-8", errors="ignore").read()
    for href in re.findall(r'<link[^>]*rel=["\']canonical["\'][^>]*href="([^"]*)"', c):
        if not href.startswith("http"):
            print(f"Relative canonical: {f.replace(DIST,'')} -> {href}")
```

### C. www redirect
```bash
curl -s -o /dev/null -w "www: %{http_code}\n" https://www.SITE_URL_PLACEHOLDER/
# Expect 301 (or 308). Deferred to project 6 — the redirect source is data/redirects.json.
```

### D. Live vs local
```bash
curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" https://SITE_URL_PLACEHOLDER/
curl -s https://SITE_URL_PLACEHOLDER/ | grep -oiE '<link[^>]*canonical[^>]*>' | head -1
```

---

## STEP 2: APPLY FIXES

> **Confidence Gate (CLAUDE.md):** ≥97% confidence before writing any site file.
> Auto-fix scripts edit `dist/` (regenerated on build) or source — when touching
> source under `src/pages/`, preview before apply.

### Fix A — Broken lazy-load images (source-level)
If broken images exist, fix them at the **source** (`src/pages/` / components), not `dist/`,
or they return on next build. Pattern: replace `src="data:image/gif;base64,..."` with the
`data-src` value, then strip `data-src`/`data-srcset`.

### Fix B — Relative canonicals
Astro pages should emit absolute canonicals from layout/frontmatter. If a relative one
appears, fix the source layout/component, not the built file. `bsuk-canonical-fixer` agent
owns static-export canonical conversion.

### Fix C — www redirect
The www→non-www rule is written once the host is known (NOT FETCHED until project 6). Its shape:
```
https://www.SITE_URL_PLACEHOLDER/* https://SITE_URL_PLACEHOLDER/:splat 301!
```

### Fix D — CSP / headers
The header file's format follows the host, which is NOT FETCHED until project 6. When it
exists, its `Content-Security-Policy` needs `www.googletagmanager.com`,
`maps.googleapis.com` and the analytics endpoints. `.claude/skills/bsuk-google-map/SKILL.md`
documents the embed→iframe CSP `object-src` fix.

---

## STEP 3: VERIFY
Re-run `bash scripts/health-sweep.sh` (or `--no-build`). It re-scans `dist/` and reports
0 remaining issues, or rebuild first if you changed source.

---

## STEP 4: ISSUES REQUIRING MANUAL ACTION

| Issue | What's needed | Where |
|---|---|---|
| **Token in a git remote** | Cannot happen yet — no remote exists. From project 6: rotate, and use a credential helper, never a URL | deferred to project 6 |
| Uncommitted work | Commit. There is no push and no deploy until project 6 | `git` |
| Deploy failed | Deferred to project 6 — there is no deploy | — |
| Schema `@id`/url hardcoded wrong | Review JSON-LD blocks | each page's `<script type="application/ld+json">` |

---

## STEP 5: REPORTING FORMAT

```
## BSUK Website Health Report — [DATE]

### Sweep result: [ALL PASSED | N FAILURES]
### Critical
- [token leak / build fail / live-site non-200 — each with the fix]
### Decisions needed
- [uncommitted files]
### Clean
- [agents, build, canonicals, live 200s — summarized]
### Next actions
1. ...
```

---

## STEP 6: CORE WEB VITALS / PAGE SPEED (deeper, run after rebuilds or quarterly)

Targets: **LCP < 2.5s**, **CLS < 0.1**, **INP < 200ms**, FCP < 1.8s, TTFB < 800ms.
Primary method = Playwright CLI; fall back to `npx lighthouse@latest`. (Scheduled Lighthouse runs belonged to the source repo's performance-monitor agent, which
was not ported — source repo only; run `npm run test:perf` by hand.)

```bash
npx lighthouse@latest https://SITE_URL_PLACEHOLDER/ \
  --output json --quiet --form-factor=mobile --throttling-method=simulate \
  --chrome-flags="--headless --no-sandbox" \
  | python3 -c "import json,sys;d=json.load(sys.stdin);a=d['audits'];print('LCP',a['largest-contentful-paint']['displayValue']);print('CLS',a['cumulative-layout-shift']['displayValue']);print('FCP',a['first-contentful-paint']['displayValue'])"
```

### Page-speed audits (source-level)
```bash
# Non-WebP images referenced in source (WebP conversion candidates)
grep -rohE 'src="[^"]*\.(jpg|jpeg|png)"' src/ | sort -u | wc -l
# Images missing loading="lazy"
grep -rn "<img" src/ | grep -v 'loading=' | head -20
# Scripts missing defer/async
grep -rn "<script" src/ | grep -vE "defer|async|application/ld\+json|type=" | head -20
# Cache rules present
echo "cache headers: NOT FETCHED until project 6 — no host, so no header file"
```

---

## AGENT INTEGRATION
This skill is the **Technical Health** layer. Related, narrower agents:
- `bsuk-agent-system-qa` — audits the agent system itself

- `bsuk-deploy-verifier` — post-deploy 200 checks + IndexNow
- `bsuk-canonical-fixer` — static-export canonical conversion
- `bsuk-site-hygiene-agent` — monthly technical SEO maintenance

Trigger this skill: before/after any deploy, after a batch rebuild, or for any
"is the site healthy?" request — start with `scripts/health-sweep.sh`.

---

## KNOWN ISSUES LOG
| Date | Issue | Status |
|---|---|---|
| 2026-06-01 | v1 skill scanned a staging directory that never built | ✅ Rewritten to Astro / `dist/` + `src/pages/` |
| 2026-06-01 | A token was once embedded in a remote URL in the source repo | ✅ Not reproducible here — BSUK has no remote until project 6 |
| 2026-06-02 | GA4/gtag blocked by CSP (console: `googletagmanager.com`, `region1.google-analytics.com` violations) | ✅ Root cause: the deploy step copied a staging header file over `public/_headers`, so the staging file was the source — a fixed `public/_headers` gets overwritten each deploy. Fix the SOURCE. CSP needs `script-src … https://www.googletagmanager.com https://www.google-analytics.com`; `connect-src … https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com` (**wildcard required** for GA4 regional `region1.*` endpoints); `frame-src` for google/maps/youtube. The full writeup was not ported — source repo only. |
