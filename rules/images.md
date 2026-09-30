# Image sizing, srcset and alt-text distribution

Rules moved out of `CLAUDE.md` on 2026-08-02 (Phase 4). **The rule text is verbatim.**

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
- **No repeated alt, same photo use new alt (user, 2026-09-29, answer board q02)** — a photo shown twice on one page keeps its served alt on its first use; each repeat carries a new alt, never a copy. Working rule 11 keeps the served alt; this is how a repeat meets Rule 50b. Held up by `tests/py/test_served_alt_preserved.py` (`judge_page`, first use then repeats) and, for the London scaffold, `tests/py/test_city_scaffold.py`.

---
id: uniform-inbody-image-sizing
enforced: test
family: IMG
---

- **BSUK's box (answer-board ruling (a), 2026-09-26).** The box below is built once, in `src/components/BodyImage.astro`: a project 5 page (location, comparison, blog) renders every in-body image with `box="uniform"` — `.bl-img.sec-img`, `max-width: 760px; aspect-ratio: 1408 / 768; object-fit: cover; height: auto` — and a portrait with `box="tall"`, which adds `.og-tall` and turns 4:5, full width of the column, below 900px in portrait orientation (a landscape phone keeps 16:9). `focal` sets `object-position`; `sizes` defaults to `UNIFORM_SIZES`, or `TALL_SIZES` for the tall box (`src/lib/assets.ts`). The twelve pages built before project 5 keep the natural `.bl-img` (420px beside the prose) until they are touched. Held up by `tests/py/test_uniform_image_box.py`.
- **Bleed colour:** any area around or behind an in-body image is a design-system token (`--color-surface` / bone); in-body portraits for the uniform box are baked with `python3 scripts/reframe_og.py … --style contain` (bone gradient), never `--style blurfill` (a blurred copy of the photo can read grey or black on phones). User ruling 2026-09-26.
- **Uniform in-body image sizing (ALWAYS — locked 2026-07-12) — applies to comparison + long-form content pages and every image agent/skill** — EVERY in-body section image, **OG photo AND infographic alike, renders in the SAME box as an infographic**: `.sec-img.inf-img` = `max-width:760px; aspect-ratio:1408/768 (16:9); object-fit:cover; height:auto`, **identical on mobile / tablet / desktop**; `.og-tall` (BodyImage `box="tall"`, a portrait: 4:5 across the column below 900px in portrait orientation, `sizes` = `TALL_SIZES`) is the one sanctioned exception. Do NOT give OG photos the smaller/variable boxes (`.portrait` 420px, `.portrait-tall` 340px, `.photo43` 480px) on these pages — the breeder wants every image the same rectangle down the page, matching the infographic sizing the comparison cluster (project 5) will ship. Tune **`object-position` per OG photo** so the puppy isn't cropped out (box size never changes, only the focal point). Ship each `<100 KB WebP + -760.webp` sibling with `srcset`/`sizes` like the infographics. Hero staggered-portrait component keeps its own `.hero-imgs` sizing. **Exact pipeline (2026-07-12): `PIL.ImageOps.fit(src,(1408,768),LANCZOS,centering=per-image)` → WebP `method=6`, quality-walk 82↓ until <95 KB → `-760.webp` sibling; a low-res OG master is upscaled to the box on purpose (uniform sizing beats pixel-peeping — breeder's call).** Canonical spec: project 3's design system. Differentiate sibling pages so they don't look identical with `.claude/skills/bsuk-component-refresh/SKILL.md` (the "Refresh Agent" — layout/accent/motif deltas, never a palette change).

---
id: read-card-thumb-is-target-hero
enforced: untested
family: IMG
---

- **A further-reading thumbnail must be the linked page's OWN hero image (ALWAYS — breeder, 2026-08-07, binding going forward)** — Every card in a "Keep reading" / further-reading / `.read-cards` block shows a crop of the **hero image of the page it links to**, never an infographic or photo belonging to the *source* page. Showing the source page's own art promises the reader one destination and delivers another, and it shipped that way on `/buy-blue-staffy-puppies-uk/` until 2026-08-07. Resolve the target's hero in this order: its `<link rel="preload" as="image">`, then its first `<img fetchpriority="high">`, then its first non-chrome content image. Cut with `scripts/bake_read_card_thumbs.py` (not ported — source repo only) (320×175 + 760×416 WebP, `centering=(0.5,0.35)`), and take the **alt from the target's own hero alt** rather than inventing a description of a photo you have not looked at. Audit the whole site with `scripts/bake_read_card_thumbs.py --audit` (not ported — source repo only). **Re-classed `untested` on the 2026-09-16 port:** neither the baker nor its test crossed from the source repo, so this rule is asserted and nothing holds it up until they land.

---
id: image-every-body-heading
enforced: test
family: IMG
---

- **An image under every body heading of a project 5 page (ALWAYS — user ruling G1, 2026-09-24)** — On a location, comparison or blog page built from the system-gaps build on (never the twelve pages built before it), the hero plans a photo slot and every BODY H2 section and every BODY H3 plans at least one image slot, an OG photo or an infographic. The fixed frame (counter, trust strip, contents, takeaways, reviews, newsletter, form) and every FAQ block, H3 questions included, are not body. Each slot names its `source`: `existing` (a served `file`, reused at its own path per working rule 11), `assets-folder` (a `source_file` from the breeder's Assets/Images folder, ingested into `public/images/` before the build), `generate` (a `prompt` and an `og_style` from IMAGE-DESIGNS.md) or `infographic` (an `infographic_style`). The board offers each slot the page's own images first, then the site's, then the folder's (`scripts/image_candidates.py`), and the breeder's answer is `approval.picks["img:<slot>"]`. A generated image is used only when the board approved its exact bytes (`og:<style>:<sha12>`). Held up by `scripts/image_rules.py` through `scripts/family_rules.py`, tested in `tests/py/test_image_rules.py`.
