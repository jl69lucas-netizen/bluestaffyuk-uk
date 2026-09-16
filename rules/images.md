# Image sizing, srcset and alt-text distribution

Rules moved out of `CLAUDE.md` (arrives in Task 10) on 2026-08-02 (Phase 4). **The rule text is verbatim.**

`enforced:` says what actually holds the rule up.
`test` — a committed check fails when the rule is broken. `judgment` — no mechanical
decision procedure exists, and `data/quality/rule-index.json` records why.
`untested` — **a deletion candidate**: it is asserted and nothing enforces it.
`scripts/quality_report.py` §5 lists every one of those on every run, which is the point.


---
id: image-keyword-distribution
enforced: untested
family: IMG
---

- **Image keyword distribution (ALWAYS — seo-rules Rule 50b)** — The page's PRIMARY keyword goes in the PRIMARY image's alt text only (hero/first content image); every other image rotates a different keyword type (secondary/LSI/NLP variation/long-tail) so the image set covers a diverse spread. No two images on a page share an alt. Applies to photos, AI-generated images, and infographics.

---
id: uniform-inbody-image-sizing
enforced: untested
family: IMG
---

- **Uniform in-body image sizing (ALWAYS — locked 2026-07-12) — applies to comparison + long-form content pages and every image agent/skill** — EVERY in-body section image, **OG photo AND infographic alike, renders in the SAME box as an infographic**: `.sec-img.inf-img` = `max-width:760px; aspect-ratio:1408/768 (16:9); object-fit:cover; height:auto`, **identical on mobile / tablet / desktop**. Do NOT give OG photos the smaller/variable boxes (`.portrait` 420px, `.portrait-tall` 340px, `.photo43` 480px) on these pages — the breeder wants every image the same rectangle down the page, matching the infographic sizing the comparison cluster (project 5) will ship. Tune **`object-position` per OG photo** so the puppy isn't cropped out (box size never changes, only the focal point). Ship each `<100 KB WebP + -760.webp` sibling with `srcset`/`sizes` like the infographics. Hero staggered-portrait component keeps its own `.hero-imgs` sizing. **Exact pipeline (2026-07-12): `PIL.ImageOps.fit(src,(1408,768),LANCZOS,centering=per-image)` → WebP `method=6`, quality-walk 82↓ until <95 KB → `-760.webp` sibling; a low-res OG master is upscaled to the box on purpose (uniform sizing beats pixel-peeping — breeder's call).** Canonical spec: project 3's design system. Differentiate sibling pages so they don't look identical with `.claude/skills/bsuk-component-refresh/SKILL.md` (deferred to project 3, see data/port-manifest.json) (the "Refresh Agent" — layout/accent/motif deltas, never a palette change).

---
id: read-card-thumb-is-target-hero
enforced: untested
family: IMG
---

- **A further-reading thumbnail must be the linked page's OWN hero image (ALWAYS — breeder, 2026-08-07, binding going forward)** — Every card in a "Keep reading" / further-reading / `.read-cards` block shows a crop of the **hero image of the page it links to**, never an infographic or photo belonging to the *source* page. Showing the source page's own art promises the reader one destination and delivers another, and it shipped that way on `/buy-blue-staffy-puppies-uk/` until 2026-08-07. Resolve the target's hero in this order: its `<link rel="preload" as="image">`, then its first `<img fetchpriority="high">`, then its first non-chrome content image. Cut with `scripts/bake_read_card_thumbs.py` (not ported — source repo only) (320×175 + 760×416 WebP, `centering=(0.5,0.35)`), and take the **alt from the target's own hero alt** rather than inventing a description of a photo you have not looked at. Audit the whole site with `scripts/bake_read_card_thumbs.py --audit` (not ported — source repo only). **Re-classed `untested` on the 2026-09-16 port:** neither the baker nor its test crossed from the source repo, so this rule is asserted and nothing holds it up until they land.
