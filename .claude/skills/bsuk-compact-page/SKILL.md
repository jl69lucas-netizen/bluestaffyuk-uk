---
name: bsuk-compact-page
description: Use when building, rebuilding or auditing any BlueStaffyUK page or section meant to stay SHORT (target ~850 words, hard ceiling 999 in <main>) — each /available-puppies/<slug>/ pup page, the /available-puppies/ hub, utility pages, and short sections inside long pages — using the compact (purchase-intent) keyword method: one warm buyer phrase per page, answer-first copy, a direct next step, and no padding. Also use when a page "looks empty", is a skeleton under 1,000 words, or when choosing keywords for a pup page. Triggers - "compact keywords", "short page", "pup page", "available page looks empty", "under 1000 words".
allowed-tools: [Read, Write, Bash]
---

# BSUK Compact Page (DRAFT 2026-11-02 — not yet pressure-tested)

> **Status:** drafted in a cloud session against the 2026-10-09 `manchester-page` snapshot,
> because the `foundation` branch lives only on the breeder's machine. Before it is
> committed, the local session must (1) diff it against `foundation`'s rules and skills,
> (2) run `superpowers:writing-skills` RED→GREEN pressure tests with subagents, and
> (3) get the breeder's answers to the four **DECISION** items in §9. Until then, nothing
> here overrides a rule in `rules/`.

## 1. What "compact keywords" means here (source, and its limits)

Source: Edward Sturm, *Compact Keywords* (edwardsturm.com/compact-keywords/, page modified
2026-10-28, read in full 2026-11-02). It is a sales page for a paid course; the detailed
method is behind the paywall. The **public** principles, which are all this skill relies on:

1. Target **warm** searchers — people already looking to buy — not "how/what/why" readers.
2. Build **landing pages for high-intent scenarios**, scalable across variations.
3. Pages need **fewer words** and fewer backlinks because the language is under-targeted.
4. Give a **direct, clear next step** ("here's a button to buy it… or get in touch").
5. Use the **buyer language most sites ignore** ("fill in the gaps").
6. Keep the **site structure simple** for crawlers and people.
7. **Small niches** leave more money keywords under-targeted.

Where BSUK departs: Sturm calls blog SEO "not worthwhile". BSUK keeps its blog project; this
skill governs only the short transactional pages and sections. Never quote Sturm's revenue
testimonials as evidence of anything.

## 2. Which pages are compact (measured, not guessed)

Word counts of `<main>` text on the 2026-10-09 snapshot build (`npx astro build`, then a
script that strips tags inside `<main>`). Re-measure on `foundation` before planning:

| Page | Words in `<main>` | Compact? |
|---|---|---|
| `/available-puppies/<slug>/` × 6 | 36–42 | YES — first targets |
| `/available-puppies/` | 64 | YES — first target (hub) |
| `/search/`, `/blog/` index | 24, 41 | utility — compact rules for the intro only |
| 9 migrated city pages (Aberdeen…York) | 416–452 | NO — project 5 location builder owns them |

Compact also applies to **sections** inside long pages: a pricing block, a delivery block, a
"meet the pups" strip — each one answers one buying question in ≤150 words.

## 3. Keyword types a compact page uses

Fill each row from the page's own research file (`data/queries/<slug>.json` via
`bsuk-query-augmentation`). **No search volume is ever written** unless a tool returned it;
keyless research ranks phrases by *evidence* (autocomplete hits across engines, SERP titles,
competitor weakness). Research notes for the first wave: §10.

| Type | Example shape (fill from research, never invent) | Where it lives |
|---|---|---|
| Transactional core | "<colour> staffy puppy for sale" · "staffy puppies available now" | H1, title, first sentence |
| Attribute modifiers | colour (blue, blue and white, white), sex (male/boy, female/girl), "KC registered" | H1 / H2s, alt text, card |
| Readiness / scarcity | "ready to leave", "ready now", "last <sex> in the litter" — only if `data/puppies.json` says so | status chip, H2 |
| Price | "<colour> staffy puppy price", "how much is a staffy puppy" | price H2 + answer-first line |
| Location / delivery | "Carlisle", "Cumbria", "delivered UK-wide", nearby cities from `data/locations.json` | delivery H2, FAQ |
| Trust / health | "health tested parents" (L-2-HGA, HC-HSF4 — tests named, **never a result**) | trust row, H5 |
| Name + brand (navigational) | "<Pup> Blue Staffy UK" | title tail, breadcrumb |

**One page = one primary phrase.** Two pups with the same colour and sex differentiate on a
real recorded axis (markings, temperament line from `personality`), never on invented traits
(see `bsuk-puppy-page-excellence` cannibalisation section).

## 4. The compact page recipe (pup page, target ~850 words)

Order follows `rules/puppies.md` `puppy-cluster-component-order` and design rule 10.

| # | Block | Words | Job |
|---|---|---|---|
| 1 | Hero (image first in DOM; desktop 400–450px band) — name, colour, sex, price, status chip, primary CTA | 30–50 | answers "is this pup for me and available?" |
| 2 | Gallery — all of the pup's own photos (2–3), style chosen on the board | 0 + alts | let the buyer judge the dog |
| 3 | Facts strip (sex, colour/markings, price, deposit with its clause, delivery band, ready date if recorded) | 40–60 | scannable proof |
| 4 | "Meet <Pup>" — personality from `personality`, breeder voice | 120–160 | the only place for warmth |
| 5 | Price & reserve — price, deposit + `deposit_refund_clause`, what's included | 100–130 | answers the money question |
| 6 | Parents & health — tests named, no results | 90–120 | trust |
| 7 | Delivery or collection — the band £200–£350 + Carlisle collection | 80–100 | removes the last objection |
| 8 | FAQ (3–5 questions from the research file) | 150–200 | voice/PAA coverage |
| 9 | Littermates / also available (cross-pup strip, §6) | 20–40 | keeps the buyer on site |
| 10 | Enquiry CTA band / form pre-filled `?puppy=<slug>` | 15–30 | the next step |

Total ≈ 650–970. If the copy needs more than 999 words, the page is not compact — stop and
ask whether it should become a full builder page.

## 5. Answer-first writing (hard rule for compact pages)

- **Every paragraph's first sentence answers its heading.** If the heading is "How Much Is
  Roman?", sentence one states the price (read from `data/price-matrix.json`).
- The **conversational opener reinforces the heading's core message**; it never warms up
  ("Choosing a puppy is a big decision…" is a FAIL).
- Then one or two sentences of proof (fact, data key, or breeder observation), then stop.
- Still EFBP-compatible (`bsuk-puppy-page-builder` §2b): Entity + Feature in sentence one is
  the answer; Benefit + Purpose follow.
- Run `anti-ai-writing` over every paragraph.

## 6. Cross-showing the other pups

- Component: a "Littermates & Also Available" strip after the FAQ, before the enquiry band.
- Data: `data/puppies.json` only. Order: same litter (when a litter key exists) → same sex
  → the rest. The current pup is excluded. Sold/reserved pups show a muted chip, not hidden,
  and never `InStock` (`instock-only-on-an-available-pup`).
- Each card: photo (face visible per `no-head-cropped-portraits`), name, colour, sex, price,
  delivery line (`delivery-band-on-every-card`), link to the pup page. Anchor text varies per
  page (`internal-link-agent` anchor ledger).
- Layout per device is chosen on the board (three options shown; see the handoff).
- The hub `/available-puppies/` links every pup; each pup page links the hub once.

## 7. Sold / reserved state (pups leave; pages must not die)

When `status` changes: the page stays live, the hero chip and schema change, the CTA becomes
"See who is still available", and the cross-pup strip moves above the fold. No 404, no
redirect, until the breeder rules otherwise. **DECISION D4.**

## 8. Gates (all existing — this skill adds none of its own yet)

`python3 scripts/board_gate.py <slug>` before code · `bsuk-duplicate-content-gate` across
the six pup pages · `bsuk-cta` board picks · `bsuk-final-page-pass` · `bsuk-page-hardening`
· `bsuk-perf-gate` · `superpowers:verification-before-completion` before any "done" claim.
Planned new check (write the failing test first, `bsuk-learning-loop`):
`compact-word-ceiling` — `<main>` words ≤ 999 on any page the board marks `profile: compact`.

## 9. Conflicts with existing rules — DECISIONS for the breeder

| # | Existing rule | Problem at ~850 words | Status |
|---|---|---|---|
| D0 | — | which keyword approach | **DECIDED (breeder, 2026-11-02): A + B, with C as sections** — A: each pup page owns its attribute phrase; B: the hub owns "available now / for sale UK"; C: buyer-situation phrases (delivery, Carlisle/Cumbria, health-tested parents, price) are H2 sections on those pages, never separate pages |
| D5 | — | which board options | **DECIDED (breeder, 2026-11-02): HA headings, G1 photos, T1 template, X1 other-pups strip** (Art board https://claude.ai/artifact/J893onxJZi8idwKsxzu31S) |
| D2 | builder §2d: 85–112 distinct entities | impossible without padding | **DECIDED (breeder, 2026-11-02): the 85–112 rule is for longer pages and is left unchanged there; compact pages do not apply it.** Compact pages use only real entities the copy needs (no floor) |
| D1 | `rules/headings.md`: all six levels, ≥5 H5 and ≥5 H6 | 10+ minor headings in 850 words is filler | OPEN — proposal: all six levels kept; H5/H6 floor 2 each on `compact` |
| D3 | H2 count = competitors' max + 3, floor 9 | pup pages need ~7 blocks | OPEN — proposal: H2 count = recipe blocks (6–8) |
| D4 | none | sold pup page behaviour unset | OPEN — proposal in §7 (page stays live, points to pups still available) |

## 10. First-wave research notes

Source: `docs/reference/compact-keywords/2026-11-02-keyless-keyword-research.md` (Firecrawl
search ×10 UK, scrape ×4; autocomplete mostly blocked, so evidence is thin — re-run the
alphabet-soup expansion locally with the Chrome extension or `research-recency`).
Grades: **A** = autocomplete + ranking titles · **B** = one of them · **C** = implied only by
weak SERPs (classifieds, Facebook, forums ranking = under-targeted = the compact opening).

| Phrase family | Grade | Page |
|---|---|---|
| blue staffy puppies for sale uk | A | hub primary |
| kc registered staffy / staffordshire bull terrier puppies for sale (uk) | A | hub secondary; pup trust row |
| blue female / blue staffy girl / blue and white staffy | B | pup page attribute (rotate "girl"/"boy"/"female"/"male" across siblings) |
| staffy puppies for sale cumbria / carlisle | C — best local gap (one local breeder site ranks; rest classifieds) | hub H2 + every pup's collection block |
| staffy puppies for sale scotland / glasgow | A | hub delivery H2 (Carlisle is the border city) |
| blue staffy puppy price uk | B | price H2 on hub + "How Much Is <Pup>?" |
| health tested parents (L-2-HGA, HC-HSF4) | C — wide open | trust H2/H5; tests named, never results |
| staffy puppy delivered uk wide | C — no ranking page covers delivery | delivery H2 |
| "<Pup> blue staffy …", brand, Lisa Bright | navigational, uncontested | title tail, breadcrumb |
| near me under £500 / cheap | A but bargain intent | **never target** |

SERP shape: classifieds (Pets4Homes, staffie-owners, puppies.co.uk, Gumtree) hold 6–8 of
the top 10 on every core phrase; no ranking competitor has a real page per individual pup.
That gap is why the pup pages are worth building. Single-pup listings elsewhere carry: stat
row (age, sex, price), ready date, parents and tests, what the pup leaves with, a litter grid
with Available/Reserved, enquiry pre-selected — every one of those is a field BSUK must
source from data, and **a field with no data key (DOB, ready date, what's included, parents'
names) is a question for the breeder, never a guess.**

## 11. Relationship to other skills

- `bsuk-puppy-page-builder` — still the builder for the buy-cluster long pages; for pup
  pages and the hub it hands keyword choice, word budget and answer-first rules to this skill.
- `bsuk-puppy-page-excellence` — still owns cannibalisation, schema, perf polish.
- There is **no "purchase guide" skill**, but the `bsuk-purchase-guide` agent rebuilds
  `/buy-blue-staffy-puppies-uk/` (a long page, not compact). The buying guide page uses
  `bsuk-seo-master-checklist`.
