---
name: sitemap-agent
description: Regenerates BSUK's sitemaps with scripts/generate_sitemaps.py (never hand-edited) and validates them with scripts/sitemap_check.py — the page, post, location, puppy and video shards and sitemap_index.xml, written into dist/ after every build. Submitting them to IndexNow or Search Console is bsuk-indexing's job and inactive until project 6.
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## Purpose

You are the **Sitemap Agent Skill** for BlueStaffyUK. Keep the sitemaps true to the build:
every indexable page in exactly one shard, every `noindex` page in none. A stale sitemap means
a new page is found late; a wrong one submits a page that asks not to be indexed.

---

## How the sitemaps are made

`scripts/generate_sitemaps.py` reads the BUILT site in `dist/` — never `src/` — and writes into
`dist/`:

| File | Contents |
|---|---|
| `page-sitemap.xml` | the homepage and every indexable page that is not a post, a city page or a puppy page |
| `post-sitemap.xml` | the blog posts (slugs from `src/content/blog/`) |
| `location-sitemap.xml` | the indexable `/uk-locations/<slug>/` pages |
| `puppy-sitemap.xml` | the `/available-puppies/<slug>/` pages |
| `video-sitemap.xml` | every indexable page that carries a YouTube embed, with each video id |
| `sitemap_index.xml` | the index of the shards above that have entries |

A shard with no entries is not written, a `noindex` page is left out, and the thank-you page
is never listed. `postbuild` runs the generator after `npm run build`; `npm run sitemaps` runs
it on its own. `public/` holds no sitemap and nothing in `dist/` is committed. `lastmod` and
the rest of the shape are the generator's (read its docstring) — change the script, never the
XML.

---

## Run and validate

```bash
npm run build                       # postbuild regenerates the sitemaps
python3 scripts/sitemap_check.py    # also a step of npm run check:all
```

`scripts/sitemap_check.py` fails on a shard missing from the index, a URL listed twice, a
listed page that is `noindex` or not built, an indexable page in no shard, and a page carrying
a YouTube embed that is missing from the video shard. `SITE_URL` is unset until project 6, so
every `<loc>` carries `SITE_URL_PLACEHOLDER` today; that is expected. What stops it shipping
is `BSUK_RELEASE=1 python3 scripts/placeholder_check.py` (`npm run check:placeholders` with the
release flag), which fails while any placeholder is left in `dist/`.
`scripts/release_guard.sh` checks only that `BSUK_RELEASE=1` is set and `PUBLIC_FORMSPREE_ID`
is present.

---

## Rules

1. **Never hand-edit a shard** — the next build overwrites it.
2. **Validate the build, not the source** — `python3 scripts/sitemap_check.py` after every build.
3. **Indexability lives on the page** — a page that must not be indexed says so in its own robots meta, and the generator follows it.
4. **Submission is not this skill's** — IndexNow and Search Console are `.claude/skills/bsuk-indexing/SKILL.md`, inactive until project 6. There is no push and no deploy before then.
