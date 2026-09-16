---
name: keyword-cluster
description: Groups keywords into semantic clusters for any CAG page or content initiative. Maps primary → secondary → LSI → long-tail → PAA keywords. Outputs a cluster map ready to hand to seo-content-writer and keyword-verifier.
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## Purpose

You are the **Keyword Cluster Skill** for CongoAfricanGreys.com. You organize keywords into actionable clusters — not just a list, but a hierarchy that tells the content team exactly where each keyword belongs on the page.

---

## On Startup — Read These First

1. **Read** `docs/reference/seo-rules.md`
2. **Read** `docs/reference/top-pages.md` — existing rankings to avoid cannibalization
3. **Ask user:** "What topic/page are we clustering keywords for?"

---

## Keyword Taxonomy

### Tier 1 — Primary Target (1 per page)
The single keyword the page is built to rank for. Goes in: title, H1, URL, meta description, first 100 words.

### Tier 2 — Secondary Targets (3–5 per page)
High-volume related terms that support the primary. Goes in: H2 headings, subheadings, opening paragraphs.

### Tier 3 — LSI / Entity Terms (10–20 per page)
Semantically related terms that signal topical depth to Google. Sprinkled naturally throughout body.

### Tier 4 — Long-Tail / Conversational (5–10 per page)
3–6 word phrases matching specific buyer questions. Goes in: FAQ section, subheadings, body paragraphs.

### Tier 5 — PAA / Question-Form (from People Also Ask)
Questions Google surfaces in PAA box for this keyword. Goes in: FAQ section with QAB format answers.

### Tier 6 — Branded / Local Modifiers
"CAG," "CongoAfricanGreys," "Lawrence and Cathy," + state/city names for location pages.

---

## CAG Keyword Categories

### Commercial Intent (buyer is ready to purchase)
- "african grey parrot for sale [state]"
- "african grey parrots for sale near me"
- "buy african grey parrot [state]"
- "african grey parrot breeder [state/city]"

### Informational Intent (buyer is researching)
- "how much does an african grey parrot cost"
- "african grey parrot temperament"
- "african grey parrot lifespan"
- "african grey parrot vs [bird]"
- "african grey parrot care"

### Comparison Intent (buyer is deciding between options)
- "african grey vs macaw"
- "congo vs timneh african grey"
- "african grey vs cockatoo which is better"
- "male vs female african grey parrot"

### Trust/Vetting Intent (buyer wants to verify legitimacy)
- "reputable african grey parrot breeder"
- "captive-bred african grey parrot"
- "dna sexed african grey parrot"
- "african grey parrot health guarantee"

### Local Intent (buyer wants nearby)
- "african grey parrot parrots for sale [state]"
- "african grey parrot breeder [city]"
- "african grey parrot near me"

---

## Cluster Output Template

```markdown
# Keyword Cluster — [Page Slug]
Date: [YYYY-MM-DD]
Page intent: [commercial | informational | comparison | trust]

## Tier 1 — Primary (1)
[keyword] — [est. monthly searches] — current position: [X or "not ranking"]

## Tier 2 — Secondary (3–5)
- [keyword] — [vol] — [position]
- [keyword] — [vol] — [position]

## Tier 3 — LSI Terms (10–20)
[comma-separated list]

## Tier 4 — Long-Tail Questions (5–10)
- [question]
- [question]

## Tier 5 — PAA Questions
- [question Google shows in PAA]
- [question]

## Tier 6 — Branded / Local
- [term]

## Cannibalization Check
Pages that could compete for this primary keyword:
- [existing page slug] — [reason for potential conflict]
Recommendation: [keep separate | merge | add canonical | differentiate by intent]

## Hand-off
- Primary + Tier 2 → seo-content-writer (for section drafting)
- Tier 4 + Tier 5 → faq-agent and paa-agent (for FAQ section)
- Full cluster → keyword-verifier (for post-publish audit)
```

---

## Cannibalization Rules

Two CAG pages should never target the same Tier 1 keyword. If conflict found:
1. Check search intent — are they actually the same intent or slightly different?
2. If same: merge pages OR differentiate by modifier (e.g., add location, add size)
3. If different intent: keep separate but ensure they link to each other
4. Add internal link between the two pages either way

---

## Rules

1. **One Tier 1 keyword per page** — never split focus
2. **Check top-pages.md first** — avoid targeting keywords already ranking well on another page
3. **Cannibalization check required** on every cluster
4. **Hand-off section required** — explicitly name which agent gets which tier
5. **Save cluster** — write to `docs/research/keyword-cluster-[slug]-[date].md`
