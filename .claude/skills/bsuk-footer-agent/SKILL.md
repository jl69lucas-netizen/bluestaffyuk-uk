---
name: bsuk-footer-agent
description: BSUK footer specification + audit rules. Source of truth is src/components/SiteFooter.astro. Use when building or auditing any page footer, or checking footer completeness.
allowed-tools: [Read, Write, Bash]
---

# BSUK Footer Agent Skill
## Footer Specification & Audit Rules for BlueStaffyUK
**Version 2.0 — Astro static build. Hosting NOT FETCHED until project 6.**

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the task genuinely cannot be done with Claude Code alone.

---

## SOURCE OF TRUTH

The footer is a single Astro component rendered on every page:

- **Component:** `src/components/SiteFooter.astro`
- **Architecture:** Astro (NOT WordPress/Astra static HTML). The source repo's footer-rebuild script was **not ported — source repo only**; there is
  nothing to run. Edit the component once and every page updates on build.
- **Standardization agent:** `.claude/agents/bsuk-footer-standardizer.md` detects pages with outdated markup and
  aligns them to this component.

> ⚠️ A previous version of this skill described another site's footer colours, nav columns,
> rebuild script and phone number. All were stale. Never reintroduce them — read the
> component, not this file, when the two disagree.

---

## DESIGN (per `rules/design.md`)

| Element | Value |
|---|---|
| Footer background | **steel blue `--color-brand`** (`#1F3A52`) — never orange |
| Text | `--color-text-on-inverse`, or white at opacity, on the steel band (10.4:1) |
| CTA button | **brass `--color-cta`** (`#C9A227`) pill with `--color-cta-ink` label, `--btn-radius` — brand signature |
| Bottom bar | `--color-surface-deep` (`#14202B`), white/10 top border |
| Type | Headings Fraunces (`--font-display`) · body and links Source Sans 3 (`--font-body`) |
| Puppy icon | custom `/emoji/bsuk-blue.png` — **never 🦜** |

---

## 5-COLUMN STRUCTURE (required content)

Every footer must contain these 5 columns. Flag any footer missing 2+ columns as
`INCOMPLETE — needs footer rebuild`.

```
Column 1: Quick Links
  - Available Puppies → /available/
  - Blue Staffy → /blue-staffy-pup-sale-uk/
  - Blue-Brindle Staffy → /buy-staffy-puppies-for-sale-uk/
  - Pricing → /blue-staffy-pup-sale-uk/
  - Contact → /contact/

Column 2: Resources
  - Species Guide → /uk-staffordshire-bull-terrier-guide/
  - Care Guide → /uk-blue-staffy-puppy-buying-guide/
  - LICENCE_CLAIM_PLACEHOLDER Info → /blue-staffy-uk-breeders/
  - FAQ → /uk-staffordshire-bull-terrier-guide/#faq
  - Blog → /blog/

Column 3: Company
  - About Us → /about/
  - Our Puppies → /available/
  - Testimonials → /testimonials/
  - Contact → /contact/

Column 4: Legal
  - Privacy Policy → /privacy-policy/
  - Terms of Service → /terms/
  - Health Guarantee Terms → /health-guarantee/
  - Delivery Policy → /delivery-delivery/
  - Refund Policy → /refund-policy/

Column 5: Contact
  - Phone: PHONE_PLACEHOLDER   (the real number is NOT FETCHED until project 6)
  - Email: [INQUIRIES_EMAIL_TBD]
  - Address: [BREEDER_LOCATION_TBD — city-level only; see privacy rule]
  - Hours: Open 24/7
  - Social: Facebook, Instagram, TikTok, YouTube

Bottom Bar:
  - Copyright © BlueStaffyUK [year]
  - LICENCE_CLAIM_PLACEHOLDER (the licence line; a number only once it is confirmed)
  - LEGAL_CLAIM_PLACEHOLDER (the statute line, prose only — never a heading or a route)
```

> **NAP consistency:** Name / Address / Phone are BlueStaffyUK · Carlisle,
> Carlisle, Cumbria · `PHONE_PLACEHOLDER` (the real number is NOT FETCHED until project 6).
> `docs/reference/credentials.md` names the env keys; these three values are the NAP record.
> Per the site privacy rule, the footer uses **city-level** location in body copy — the full
> address belongs to the LocalBusiness schema and the footer's contact block only.

---

## RESPONSIVE

| Breakpoint | Layout |
|---|---|
| ≥ 861px | multi-column grid |
| 521–860px | 2-column, brand col full width |
| ≤ 520px | single column |

---

## AUDIT MODE

When auditing footers across pages:
1. Confirm the page renders `Footer.astro` (not legacy WordPress/Astra `site-footer` markup).
2. Confirm all 5 columns are present (flag `INCOMPLETE` if 2+ missing).
3. Confirm the steel `--color-brand` background + the brass `--color-cta` pill (no orange).
4. Confirm the phone is `PHONE_PLACEHOLDER`, the licence and statute lines are
   LICENCE_CLAIM_PLACEHOLDER / LEGAL_CLAIM_PLACEHOLDER, and the copyright year is current.
5. Confirm no other breeder's vocabulary survives, and no emoji (line-icon SVGs only).

---

## WHAT NOT TO TOUCH
- Schema JSON-LD blocks (footer changes never alter page schema).
- Content above the footer component.

---

## REFERENCE
- **Component:** `src/components/SiteFooter.astro` (source of truth)
- **Design spec:** `rules/design.md`
- **NAP master:** `CLAUDE.md`; env keys in `docs/reference/credentials.md`
- **Standardizer:** `.claude/agents/bsuk-footer-standardizer.md`
