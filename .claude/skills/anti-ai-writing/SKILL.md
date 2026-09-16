---
name: anti-ai-writing
description: Use when writing or editing any CAG prose (blog posts, page body, FAQ answers, emails, social, YouTube scripts) to filter out AI-tell phrases, robotic rhythm, and generic structure before they ship. Reference blacklist + human alternatives.
---

## Overview

This is a **proactive blacklist**, not a reactive "humanize this draft" pass. Run it *while* you write, and again before you ship — the goal is that the slop never lands in the draft in the first place.

It is the third, distinct axis of CAG voice. Keep all three separate and use all three together:

- **First-Person Brand Voice** = POV (we / our / "here at C.A.Gs").
- **`cag-non-commodity-content-agent`** = substance/authenticity (breeder insight a generic LLM can't invent).
- **`anti-ai-writing` (this skill)** = phrasing & rhythm (the words and sentence shapes that read machine-made).

A sentence can be perfectly first-person and perfectly true and still read like AI. This skill fixes that last layer.

## When to Use

Apply to **any CAG prose** — especially the high-tell surfaces:

- Blog intros and conclusions
- FAQ answers
- CTA / hero copy
- Email (newsletter, lead nurture, review requests)
- Social captions and YouTube scripts

**Do NOT apply to:** schema / JSON-LD, legal text (privacy policy, terms), data tables, pricing matrices, or code. Those are structured or verbatim and must not be "humanized."

## Blacklist (ban these — with human alternatives)

| Category | Banned pattern | Why it reads robotic | Human alternative |
|---|---|---|---|
| **Weak Openers** | "In today's fast-paced world…" / "In the world of…" | Generic stage-setting that says nothing | Open on the concrete situation: "A buyer called us last week, scared off by a $400 'Congo'." |
| Weak Openers | "When it comes to African Greys…" | Filler runway before the real sentence | Cut it. Start at the noun: "African Greys bond hard, fast, and for decades." |
| Weak Openers | "Whether you're a first-time owner or a seasoned keeper…" | Fake-inclusive both-sides hedge | Pick the actual reader and address them. |
| Weak Openers | "The truth is…" / "The truth, in our experience, is that…" | Hedge frame that buries the claim | Lead with the claim itself, no preamble. |
| **Empty Transitions** | "It's important to note that…" / "It's worth mentioning…" | Pads; never adds meaning | Delete; just state the point. |
| Empty Transitions | "That being said," / "At the end of the day," | Throat-clearing connective | Use "But," "Still," or nothing. |
| Empty Transitions | "Moreover," / "Furthermore," | Essay-bot register | "Also," or start a new sentence. |
| **Inflated Verbs** | "delve into" / "navigate the world of" / "embark on" | LLM thesaurus tells | "look at," "get into," "start." |
| Inflated Verbs | "unlock," "elevate," "harness," "leverage" | Marketing-deck verbs | "open up," "improve," "use." |
| Inflated Verbs | "seamless," "robust," "cutting-edge," "best-in-class" | Empty product-page adjectives | Name the concrete thing instead. |
| **Padding Tricolons** | "brilliant, sensitive, long-lived companions" (3 balanced adjectives) | LLM loves the rule-of-three rhythm | Keep one adjective, or replace with a fact: "an African Grey can outlive a 40-year mortgage." |
| Padding Tricolons | "honest, transparent, and upfront" | Synonym-stack that triples one idea | Say it once, with the strongest word. |
| **Generic Conclusions** | "In conclusion," / "In summary," | Announces a wrap nobody asked for | End on a concrete next step or a real sentence. |
| Generic Conclusions | "let's walk through it together / no sales pitch, just…" | Reassuring AI sign-off shape | End with the actual help: a number, a checklist item, a callback. |
| Generic Conclusions | "Ultimately, the choice is yours." | Hollow empowerment close | Tell them what *we'd* do and why. |
| **Fake-Professional Terms** | "more than almost any other" / "second to none" | Vague unfalsifiable intensifier | Quantify or drop: "the #1 question on our intake calls." |
| Fake-Professional Terms | "isn't a simple yes or no" / "it's not black and white" | Stock phrasing for "it's nuanced" | State the actual condition: "It comes down to your daily schedule." |
| Fake-Professional Terms | "we respect anyone honest enough to ask" | Performative virtue / reader-flattery | Cut it; respect is shown by answering well. |
| **Punctuation / Rhythm Tells** | "not only X but also Y" | Signature LLM correlative construction | Two plain sentences, or "X — and Y too." |
| Punctuation / Rhythm Tells | Em-dash in every sentence | Over-used AI connective | Max one em-dash per paragraph; use periods. |
| Punctuation / Rhythm Tells | Every sentence the same medium length | Smooth, machine-even cadence | Drop in a short sentence. Like this. |

## Rhythm Rules

- **Vary sentence length** — at least one sentence under 8 words per paragraph.
- **Max one em-dash per paragraph.**
- **No "not only X but also Y."**
- **Lead with the concrete claim**, not a hedge or a frame.
- **Cut any sentence that survives deletion** without losing meaning — if the paragraph still makes sense without it, it was padding.
- **Break up tricolon adjective stacks** — three balanced adjectives in a row is the loudest tell; keep one, or swap the stack for a fact.

## Meaningful Words — No Stop-Word Filler (added 2026-07-11, breeder rule)

Applies to every NAMING surface when working on, rebuilding, creating, or editing CAG pages: URL slugs, anchor text, headings, image filenames, image alt text, meta titles, button labels, section IDs.

- **Content words only where grammar allows** — drop `of / the / and / for / with / a / an / to / in / on` fillers when the phrase still reads naturally without them.
- ✅ `congo-african-grey-diet-plan` · ❌ `the-diet-plan-for-a-congo-african-grey`
- ✅ anchor "Congo African Grey shipping costs" · ❌ anchor "more about the costs of shipping"
- ✅ H3 "Congo vs Timneh Temperament Differences" · ❌ H3 "A Look at the Differences in the Temperament"
- **Body prose is exempt** — sentences stay natural, grammatical, first-person. This rule targets naming/labeling surfaces, not paragraphs. A heading may keep a stop word when the conversational Quora-style question format needs it ("Is a Congo or a Timneh Right for You?" is fine — question headers are a locked pattern).
- **Every kept word must carry meaning** — if a word can be deleted from a slug/anchor/label without losing meaning, delete it.

## CAG-Specific

- **Keep the first-person breeder voice** — stripping slop never means stripping "we / our / here at C.A.Gs." Humanizing without the POV is a different failure.
- **Stay inside the Verified-Claim Ledger** — humanizing never means inventing. A vivid concrete detail still has to be true (a real intake call, a real bird, a real price). No new credentials, no fabricated outcomes.
- **CITES-safe** — all rewrites stay captive-bred / Appendix-I-accurate; never imply wild-caught.
- **No visible dates** — freshness lives in schema only (see CLAUDE.md non-negotiables).
- **Never the 🦜 emoji** — use `/emoji/cag-congo.png` / `cag-timneh.png` or `[CAG]`/`[TAG]` text markers.

## Self-Check Before Shipping

1. **Grep the draft** for blacklist terms — e.g. `grep -niE "in today's|when it comes to|the truth is|it's important to note|delve|seamless|in conclusion|not only.*but also|isn't a simple yes or no|more than almost any other"` over the file.
2. **Read it aloud.** Anything you'd never say to a buyer on the phone gets cut or rewritten.
3. **If it sounds like a press release, rewrite it.** Press-release cadence is the failure state.

## Common Mistakes

- **Stripped the slop but also stripped the voice** — the draft goes flat and ownerless. Keep we/our/here at C.A.Gs; the fix is phrasing, not personality.
- **Swapped one cliché for another** — "delve into" → "dive into" is not a fix. Replace with a plain verb, not a fresher buzzword.
- **Over-corrected into choppiness** — every sentence under 8 words reads like a robot too. Vary length; one short sentence per paragraph, not all of them.
- **Invented a concrete detail to sound human** — a fake "buyer named Sarah called us" violates the Verified-Claim Ledger. Use only real, true specifics.
