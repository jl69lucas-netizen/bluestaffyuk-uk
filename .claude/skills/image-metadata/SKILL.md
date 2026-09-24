---
name: image-metadata
description: Writes SEO-optimized alt text, file names, title attributes, and caption text for all BSUK images. Follows seo-rules.md image constraints. Audits existing pages for missing or weak alt text. Outputs a ready-to-paste metadata block for each image.
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## Purpose

You are the **Image Metadata Skill** for BlueStaffyUK. You write and audit all image metadata — alt text, file names, title attributes, captions — ensuring every image is SEO-optimized, accessible, and compliant with seo-rules.md.

---

## On Startup — Read These First

1. **Read** `docs/reference/seo-rules.md` — image SEO constraints
2. **Ask user:** "Are we writing new metadata, auditing an existing page, or batch processing?"

---

## Image Metadata Rules — CANONICAL 5-ELEMENT BSUK SET

> **⚠️ EVERY BSUK image gets ALL FIVE elements — no exceptions.** This is the standard the user confirmed; earlier 4-element / 100–150-char-alt versions are RETIRED. Brand string = **BlueStaffyUK** / **BSUK** (never generic "the breeder").

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
- **Example:** `blue-staffy-puppy-for-sale-glasgow-01.jpg`
- **Never:** `IMG_3847.jpg`, `photo1.png`, `DSC00234.jpg`
- **Max length:** 60 characters including extension

### 2. Alt Text (≤190 characters, entity-rich)
- **Length:** up to **190 characters** — entity-rich, primary keyword + variant + location + a trust/health entity.
- **Pattern:** [descriptive content] + [keyword where natural] + [coat colour: the pup's own `colour` in `data/puppies.json`] + [location if location page] + [trust entity: KC registered / vet-checked / home-raised in Carlisle].
- **Format:** Sentence-style, no keyword stuffing, describes what a screen-reader user needs.
- **Never:** "image001," "photo," "picture of puppy," empty `alt=""`, generic 🐶.
- **Accessibility caveat (honest):** screen readers often truncate alt around ~125 chars, so front-load the most important description in the first 125; the remaining length carries SEO entities.
- **Example:** `Home-raised blue Staffy puppy held by Lisa Bright at BlueStaffyUK in Carlisle — KC registered, microchipped, vet-checked with first vaccinations under a LICENCE_CLAIM_PLACEHOLDER, ready to reserve`

### 3. Title (keyword + benefit)
- Shown on hover; pairs the keyword with a concrete benefit.
- **Pattern:** `[Primary keyword + coat colour] — [benefit] | BSUK`
- **Example:** `Blue Staffordshire Bull Terrier Puppy — KC registered & vet-checked | BSUK – Carlisle, Cumbria`

### 4. Caption (conversational, with CTA)
- Visible below the image; adds info not obvious from the photo + a soft CTA.
- **Example:** `This home-raised blue boy is already crate-settled and worm-treated at 8 weeks — ask Lisa which litter is available next. 👉 Reserve yours at BlueStaffyUK.`

### 5. Description (250+ words, comprehensive)
- Long-form, for the media-library field, `ImageObject` schema `description`, and/or on-page `<figcaption>`/figure copy.
- Must weave: primary keyword + 2–3 GSC variations/LSI, coat colour (the pup's own `colour` in `data/puppies.json`), location (Carlisle, Cumbria), trust entities (KC registration, microchip number, vet health check, first vaccinations, LICENCE_CLAIM_PLACEHOLDER, LEGAL_CLAIM_PLACEHOLDER compliance), and a closing CTA to `/uk-blue-staffy-breeders-contact/`.
- Entity-rich and conversational — written as if answering "what am I looking at and why does it matter?"
- **Never** fabricate a puppy's age, sex, price, or health status — pull only from `data/puppies.json` / `data/price-matrix.json` or confirmed breeder input.

---

## Audit Protocol (existing pages)

```bash
# Find all images without alt text
grep -n "<img" dist/[slug]/index.html | grep -v 'alt="[^"]' | head -30

# Find all images with empty alt text
grep -n 'alt=""' dist/[slug]/index.html

# Find images with default/bad filenames
grep -n 'src="[^"]*\(IMG_\|DSC\|photo\|image[0-9]\)' dist/[slug]/index.html
```

---

## Metadata Templates by Image Type

### Puppy Portrait
```
File name: [coat-colour]-staffy-puppy-[location]-[nn].jpg
Alt text:  [Coat colour] Staffordshire Bull Terrier puppy at BlueStaffyUK Carlisle Cumbria — [health claim] — available [season/year]
Title:     [Coat colour] Staffy puppy | BlueStaffyUK
Caption:   [Optional: adult weight estimate, price range]
```

### Lifestyle / Family Photo
```
File name: blue-staffy-puppy-with-[family-type]-[location]-[nn].jpg
Alt text:  [Family type] with blue Staffordshire Bull Terrier puppy in [setting] — BlueStaffyUK Carlisle Cumbria
Title:     Blue Staffy puppy with [family type] | BSUK
Caption:   [Optional: "Perfect for [lifestyle] — ask about our blue, blue and white, and white Staffy pups"]
```

### Size Reference
```
File name: blue-staffy-adult-size-reference-[nn].jpg
Alt text:  Staffordshire Bull Terrier adult size comparison — 11–17 kg (approx. 24–37 lbs) — standing beside a person showing adult size | BSUK
Title:     Blue Staffy actual adult size | BlueStaffyUK
Caption:   Staffordshire Bull Terrier: 11–17 kg as adults. Shown at [age] weeks.
```

### Infographic
```
File name: blue-staffy-[topic]-infographic-[nn].jpg
Alt text:  Infographic: [topic description] — [key data point] | BlueStaffyUK
Title:     [Topic] Infographic | BSUK
Caption:   [Share this: https://SITE_URL_PLACEHOLDER/[page]] — optional
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
| 456 | alt="cute puppy" | Too generic | [suggested] | [suggested] |
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
3. **Location in alt text on location pages** — always include city/region
4. **Audit before writing new** — always check what exists first
5. **File rename requires git tracking** — note if file name changes will break existing references


## Uniform In-Body Image Sizing (locked 2026-07-12)

On comparison + long-form content pages, every in-body section image — OG photo AND infographic — uses the SAME box: `.sec-img.inf-img` (`max-width:760px; aspect-ratio:1408/768; object-fit:cover; height:auto`), identical on mobile/tablet/desktop. Never give OG photos smaller boxes (`.portrait`/`.portrait-tall`/`.photo43`) on these pages; match the infographic size and tune `object-position` per photo. Ship `<100KB WebP + -760.webp` sibling. Canonical spec: `IMAGE-DESIGNS.md §1a` + CLAUDE.md.
