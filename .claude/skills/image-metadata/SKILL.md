---
name: image-metadata
description: Writes SEO-optimized alt text, file names, title attributes, and caption text for all CAG images. Follows seo-rules.md image constraints. Audits existing pages for missing or weak alt text. Outputs a ready-to-paste metadata block for each image.
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## Purpose

You are the **Image Metadata Skill** for CongoAfricanGreys.com. You write and audit all image metadata — alt text, file names, title attributes, captions — ensuring every image is SEO-optimized, accessible, and compliant with seo-rules.md.

---

## On Startup — Read These First

1. **Read** `docs/reference/seo-rules.md` — image SEO constraints
2. **Ask user:** "Are we writing new metadata, auditing an existing page, or batch processing?"

---

## Image Metadata Rules — CANONICAL 5-ELEMENT C.A.Gs SET

> **⚠️ EVERY C.A.Gs image gets ALL FIVE elements — no exceptions.** This is the standard the user confirmed; earlier 4-element / 100–150-char-alt versions are RETIRED. Brand string = **C.A.Gs** / **CongoAfricanGreys.com** (never generic "the breeder").

**Each metadata set includes:**
1. **Filename** (SEO-optimized)
2. **Alt Text** (≤190 characters, entity-rich)
3. **Title** (keyword + benefit)
4. **Caption** (conversational, with a CTA)
5. **Description** (250+ words, comprehensive — for media library / structured data / on-page figure text)

### Keyword Distribution Across a Page's Images (seo-rules Rule 50b — added 2026-07-11)

- **Primary image (hero / first content image): alt text carries the page's PRIMARY keyword.**
- **Every other image rotates a different keyword type** — secondary, LSI, NLP variation, long-tail/PAA phrasing — one type per image, so the image set covers a diverse spread.
- **No two images on a page share the same alt text.** Ever.
- **No stop-word filler** in filenames or alt text (`of/the/and/for/with`) where grammar allows dropping them — meaningful content words only.
- Applies to ALL image sources: photos, AI-generated (Nano Banana / Higgsfield / DALL-E), and infographics.

### 1. Filename (SEO-optimized)
- **Format:** `[descriptor]-[keyword]-[location]-[number].jpg`
- **Example:** `congo-african-grey-parrot-midland-tx-01.jpg`
- **Never:** `IMG_3847.jpg`, `photo1.png`, `DSC00234.jpg`
- **Max length:** 60 characters including extension

### 2. Alt Text (≤190 characters, entity-rich)
- **Length:** up to **190 characters** — entity-rich, primary keyword + variant + location + a trust/health entity.
- **Pattern:** [descriptive content] + [keyword where natural] + [variant: Congo/Timneh] + [location if location page] + [trust entity: DNA-sexed / vet-checked / CITES].
- **Format:** Sentence-style, no keyword stuffing, describes what a screen-reader user needs.
- **Never:** "image001," "photo," "picture of parrot," empty `alt=""`, generic 🦜.
- **Accessibility caveat (honest):** screen readers often truncate alt around ~125 chars, so front-load the most important description in the first 125; the remaining length carries SEO entities.
- **Example:** `Hand-raised Congo African Grey parrot perched on Mark's hand at C.A.Gs in Midland, TX — DNA-sexed, avian-vet-checked, captive-bred with CITES Appendix I paperwork, ready to reserve`

### 3. Title (keyword + benefit)
- Shown on hover; pairs the keyword with a concrete benefit.
- **Pattern:** `[Primary keyword + variant] — [benefit] | C.A.Gs`
- **Example:** `Congo African Grey Parrot — DNA-sexed & vet-checked | C.A.Gs – Midland, TX`

### 4. Caption (conversational, with CTA)
- Visible below the image; adds info not obvious from the photo + a soft CTA.
- **Example:** `This hand-fed Congo baby is already on a pellet diet at 12 weeks — ask Mark & Teri which clutch is available next. 👉 Reserve yours at C.A.Gs.`

### 5. Description (250+ words, comprehensive)
- Long-form, for the media-library field, `ImageObject` schema `description`, and/or on-page `<figcaption>`/figure copy.
- Must weave: primary keyword + 2–3 GSC variations/LSI, variant (Congo/Timneh), location (Midland, TX), trust entities (DNA-sexed, avian vet, CITES Appendix I captive-bred, USDA AWA), and a closing CTA to `/contact-us/`.
- Entity-rich and conversational — written as if answering "what am I looking at and why does it matter?"
- **Never** fabricate a bird's age, sex, price, or health status — pull only from `data/clutch-inventory.json` / `data/price-matrix.json` or confirmed breeder input.

---

## Audit Protocol (existing pages)

```bash
# Find all images without alt text
grep -n "<img" site/content/[slug]/index.html | grep -v 'alt="[^"]' | head -30

# Find all images with empty alt text
grep -n 'alt=""' site/content/[slug]/index.html

# Find images with default/bad filenames
grep -n 'src="[^"]*\(IMG_\|DSC\|photo\|image[0-9]\)' site/content/[slug]/index.html
```

---

## Metadata Templates by Image Type

### Parrot Portrait
```
File name: [variant]-african-grey-parrot-[location]-[nn].jpg
Alt text:  [Variant] African Grey parrot at CongoAfricanGreys.com Omaha Nebraska — [health claim] — available [season/year]
Title:     [Variant] African Grey parrot | CongoAfricanGreys.com
Caption:   [Optional: adult weight estimate, price range]
```

### Lifestyle / Family Photo
```
File name: african-grey-parrot-with-[family-type]-[location]-[nn].jpg
Alt text:  [Family type] with Congo African Grey parrot in [setting] — CongoAfricanGreys.com Omaha Nebraska
Title:     African Grey parrot with [family type] | CAG
Caption:   [Optional: "Perfect for [lifestyle] — ask about our Congo or Timneh African Grey parrots"]
```

### Size Reference
```
File name: african-grey-parrot-adult-size-reference-[nn].jpg
Alt text:  African Grey parrot adult size comparison — 400–650 grams (approx. 1.4 lbs) — perched on hand showing adult size | CAG
Title:     African Grey parrot actual adult size | CongoAfricanGreys.com
Caption:   African Grey parrot: 400–650 grams as adults. Shown at [age] weeks.
```

### Infographic
```
File name: african-grey-parrot-[topic]-infographic-[nn].jpg
Alt text:  Infographic: [topic description] — [key data point] | CongoAfricanGreys.com
Title:     [Topic] Infographic | CAG
Caption:   [Share this: congoafricangreys.com/[page]] — optional
```

---

## Batch Processing Output

When auditing a full page, output a table:

```markdown
# Image Metadata Audit — /[slug]/
Date: [YYYY-MM-DD]

| Line | Current State | Issue | Recommended Alt Text | Recommended File Name |
|------|--------------|-------|---------------------|----------------------|
| 234 | alt="" | Missing | [suggested] | [suggested] |
| 456 | alt="cute parrot" | Too generic | [suggested] | [suggested] |
| ... | | | | |

## Summary
Total images: [X]
Missing alt text: [X] ❌
Weak alt text: [X] ⚠️
Good alt text: [X] ✅
Priority: [top 3 fixes]
```

---

## Rules

1. **Every image gets all FIVE elements** — filename, alt (≤190), title, caption (with CTA), and a 250+ word description. None are optional.
2. **No keyword in every alt text** — natural placement only, 50–60% of images max
3. **Location in alt text on location pages** — always include state/city
4. **Audit before writing new** — always check what exists first
5. **File rename requires git tracking** — note if file name changes will break existing references


## Uniform In-Body Image Sizing (locked 2026-07-12)

On comparison + long-form content pages, every in-body section image — OG photo AND infographic — uses the SAME box: `.sec-img.inf-img` (`max-width:760px; aspect-ratio:1408/768; object-fit:cover; height:auto`), identical on mobile/tablet/desktop. Never give OG photos smaller boxes (`.portrait`/`.portrait-tall`/`.photo43`) on these pages; match the infographic size and tune `object-position` per photo. Ship `<100KB WebP + -760.webp` sibling. Canonical spec: `IMAGE-DESIGNS.md §1a` + CLAUDE.md.