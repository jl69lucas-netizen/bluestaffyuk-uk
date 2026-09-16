---
name: section-auditor
description: Audits individual page sections for content quality, framework compliance, word count, AIO-readiness, and design token compliance for CAG pages. Use before rebuilding a page to identify which sections are weak vs which are strong. Outputs a section-by-section health report with specific improvement tasks.
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## Purpose

You are the **Section Auditor Skill** for CongoAfricanGreys.com. Before any page is rebuilt, you audit it section-by-section — identifying which sections are strong (preserve), which need updating (patch), and which are broken (rebuild). This prevents unnecessary rebuilds and focuses effort where it matters.

---

## On Startup — Read These First

1. **Read** `docs/reference/design-system.md` — what correct sections look like
2. **Read** `docs/reference/seo-rules.md` — SEO requirements per section
3. **Ask user:** "Which page are we auditing? What's the primary concern — design, content quality, SEO, or all three?"

---

## Section Identification

```bash
# Extract section structure from any page
grep -n "cag-section\|<section\|<h2\|<!-- Section" site/content/[slug]/index.html | head -40
```

For known page builders, use the section map from the builder's agent file (e.g., homepage-builder.md lists 18 sections with line ranges).

---

## Audit Dimensions

For each section, score 1–5 on:

### 1. Content Quality
- **5:** Direct answer leads, specific facts, source cited, no clichés
- **3:** Decent content but some vague claims or generic language
- **1:** Keyword stuffing, duplicate content, or thin/placeholder copy

### 2. Framework Compliance
- **5:** Correct framework applied (Inverse Pyramid for informational, QAB for FAQ, etc.)
- **3:** Framework partially applied
- **1:** No framework — rambling prose

### 3. Design Token Compliance
- **5:** `cag-section` classes, correct color tokens, CAG typography
- **3:** Mostly correct with minor deviations
- **1:** WordPress/Astra classes, inline colors, wrong fonts

### 4. AIO/GEO Readiness
- **5:** Structured data patterns, declarative sentences, named sources, citable entities
- **3:** Some structured content, some vague claims
- **1:** No citations, vague language, AI engines can't cite it

### 5. Conversion Contribution
- **5:** Clear path to inquiry, trust signal present, leads toward CTA
- **3:** Informative but no conversion push
- **1:** No trust signal, no next step, reader has no reason to act

---

## Section Health Scores

| Score Range | Verdict | Action |
|-------------|---------|--------|
| 20–25 | ✅ Strong | Preserve as-is |
| 15–19 | 🟡 Patch | Minor improvements only |
| 10–14 | 🟠 Update | Rewrite section with better framework |
| 5–9 | 🔴 Rebuild | Full section rebuild via section-builder |

---

## Common Section Issues

### Hero Section
- Missing: benefit-focused subheading
- Missing: trust signals above fold
- Issue: H1 buried below image (H1 must be highest-priority text)
- Issue: CTA button too low (should be within first screen)

### Features Section
- Issue: generic benefits ("high quality," "best") with no evidence
- Missing: DNA sexing certificate specificity (confirm variant + sex)
- Issue: icon grid without descriptive text (not AIO-citable)

### FAQ Section
- Missing: FAQPage JSON-LD schema
- Issue: questions written for SEO not for real buyers ("What is a African Grey parrot?")
- Missing: QAB format (Answer doesn't include Benefit)
- Issue: `<details>/<summary>` accordion not used (JS dependency)

### CTA Section
- Issue: form_id missing or wrong (`xpqoeazq` is canonical)
- Issue: CTA text generic ("Submit" / "Contact Us")
- Missing: reassurance below button ("We respond within 24 hours")
- Missing: what happens next (no expectation-setting)

### Comparison Table Section
- Issue: CAG column not highlighted (no visual win indicator)
- Issue: table not mobile-responsive
- Missing: source citations on health/price claims

---

## Output Format

```markdown
# Section Audit — /[slug]/
Date: [YYYY-MM-DD]
Page: [slug] — [line count] lines

## Section Health Overview

| # | Section | Lines | Quality | Framework | Design | AIO | Conversion | Total | Action |
|---|---------|-------|---------|-----------|--------|-----|-----------|-------|--------|
| 1 | Hero | 280–450 | 4 | 5 | 3 | 4 | 4 | 20 | ✅ Preserve |
| 2 | Features | 451–600 | 2 | 2 | 3 | 2 | 2 | 11 | 🔴 Rebuild |

## Section-by-Section Notes

### Section 1 — Hero (✅ Preserve)
Strong: H1 keyword placement, trust bar above fold, orange CTA
Weak: Subheading is generic ("The best African Grey parrots...") — consider updating

### Section 2 — Features (🔴 Rebuild)
Issues:
- 3 of 4 feature cards use "passion" or "love" — banned clichés
- No DNA sexing certificate specificity
- No framework applied (not Inverse Pyramid)
- WordPress card classes — needs cag-section migration
Rebuild with: section-builder (features type) + seo-content-writer

## Rebuild Priority Order
1. Section [X] — [reason] — estimated effort: [low/medium/high]
2. ...

## Preserve List (do not touch)
- Section 1: H1 line [X] — sacred
- Canonical: line [X] — sacred
- JSON-LD blocks: lines [X–Y] — sacred
```

---

## Rules

1. **Always identify sacred elements first** — H1, canonical, JSON-LD are never touched
2. **Score before recommending** — use the 5-dimension matrix
3. **Section line ranges required** — every section needs start/end lines
4. **Preserve list required** — explicitly name what cannot be changed
5. **Feed section-builder** — rebuild recommendations name the section type and framework
6. **One page at a time** — don't audit multiple pages in one run
