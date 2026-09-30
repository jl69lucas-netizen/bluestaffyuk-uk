# Deposit Wording Alignment — Inventory and Proposed Change Set

**Date:** 2026-09-27 · **Branch:** `deposit-wording` (off `foundation` 5b41cd5) · **Status:** class (a)
applied on this branch; classes (b) and (c) are proposals that wait on the user.

## The ruling

Recorded in `docs/reference/answer-board/answers/2026-09-24-questions-for-lisa-bright-followup-2026-09-27.md`:

- **Deposit.** The £500 deposit is described as **"refundable up to 70% if a visitor fails to show up"**.
  No page calls it plainly "refundable".
- **Viewing.** Viewing is deposit-first, framed as **"the £500 deposit books your viewing and reserves
  your puppy"**. The ruling says the exact wording goes on each page's board for approval.

One discrepancy to settle (Open question 3). Lisa's original answer (`…-lisa-bright-2026-09-27.md`, Q3)
set the 70% condition as *"if the buyer chooses to change their mind 1 day before delivery or pickup"*.
The follow-up ruling says *"if a visitor fails to show up"*. Class (a) below uses the ruling's wording.

## Method

`grep -rIin refundable` across `CLAUDE.md rules/ .claude/ scripts/ tests/ data/ src/` returned
**303 hits in 97 files**. Every flag consumer (`deposit_refundable`, `deposit_terms`) was traced as well.
After `npm run -s build`, every built page was grepped, so the tables below say what actually renders.
A second sweep looked for **viewing-before-deposit** wording ("before you pay", "meet the litter first").
The ruling contradicts that wording as directly as it contradicts plain "refundable".

`docs/` is outside the requested scope and holds 383 more hits in 49 files: specs, plans, reports and
session logs. Those are historical records. They are not rewritten.

## Classes

| Class | Meaning | Action |
|---|---|---|
| **(a)** | Instruction or rule text that tells a writer what to say | **Applied on this branch** |
| **(b)** | Data, shared code and test pins that new pages read or render | **Proposal. Waits on the user** |
| **(c)** | Frozen copy on the 12 pages in `scripts/family_rules.py` `BUILT_BEFORE_SYSTEM_GAPS`, plus their approved boards | **Proposal. Waits on the user** |
| **(n)** | Correct as it is: retired-term guards, buyer questions, historical records | No change |

**The coupling that decides the order.** Several (b) sources render *on frozen pages*. The three FAQ rows
that use `{deposit_terms}`, the kit counter label and the settings flag print "refundable" on the
homepage, contact, breeders, pup-sale, buy and buying-guide pages. That means a (b) change is also a
(c) change. The two cannot be approved separately.

---

## (a) Instruction and rule text — applied

| File | What changed |
|---|---|
| `CLAUDE.md` (Brand context, locked facts) | "Deposit **£500, refundable**" → "£500, described as refundable up to 70% if a visitor fails to show up — never plainly 'refundable'", plus the deposit-first viewing sentence |
| `rules/puppies.md:27` (`delivery-band-on-every-card`) | "The £500 deposit is refundable…" → the ruling's wording, the deposit-first framing and a pointer to the answer file |
| 33 × `.claude/agents/bsuk-*.md` (shared **Litter:** and **Trust pillars:** banner lines) | "£500 refundable deposit" → "£500 deposit, refundable up to 70% if a visitor fails to show up, which books the viewing and reserves the puppy" |
| `bsuk-about-builder` (2), `bsuk-framework-agent`, `bsuk-trust-signals-agent`, `bsuk-location-builder` (2), `bsuk-seo-content-writer` (7, including the description), `bsuk-homepage-builder` (2), `bsuk-purchase-guide` (description), `bsuk-interactive-component`, `bsuk-meta-description-agent` (3) | Per line. Prose gets the full wording. Meta templates capped at ≤160 characters get "a £500 deposit books a viewing" |
| Skills: `bsuk-aeo-pass`, `bsuk-contact-form`, `bsuk-cta-strategy` (2), `bsuk-location-page-builder` (3), `bsuk-puppy-page-builder`, `bsuk-seo-master-checklist` (5), `framework-aida`, `framework-aio-geo`, `framework-ebp`, `framework-heading-hierarchy`, `framework-qab` | Same treatment. Worked examples, H4 samples and counters now use the ruling's wording |
| `framework-aida:106`, `framework-bab:104` (viewing) | "meet your puppy … before you pay a penny / anything" → "your £500 deposit books your viewing…" |
| `scripts/build_design_system.py` (the design-system README's Locked facts) | "and it is **refundable**" → "refundable up to 70% if a visitor fails to show up … books the viewing and reserves the puppy". The output is not committed. `test_design_system_build` still finds `refundable` |

**Left in (a) on purpose.** Each of these moves only together with a (b) item:

| File:line | Why it waits |
|---|---|
| `rules/copy.md:71` | Describes the `dup_content_audit.py` whitelist entry "the exact deposit-£500-refundable line". It changes when that whitelist changes (b4) |
| `.claude/skills/bsuk-seo-master-checklist/SKILL.md:719` `£500 Refundable Deposit` | Pinned verbatim by `tests/py/test_builder_skills.py:450` (b9) |
| `.claude/agents/bsuk-meta-description-agent.md:73` "Is the deposit refundable?" | A buyer's question, which is correct as written (n) |
| `scripts/pageboard.py:1260` | A code comment quoting a past defect as an example (n) |

## (b) Data, shared code and test pins — proposed, not applied

| # | Where | Today | Renders on | Proposed change |
|---|---|---|---|---|
| b1 | `data/settings.json:16` `deposit_refundable: true` · `data/price-matrix.json` (same flag) | boolean | every consumer below | **Keep `true`.** The deposit is partly refundable, and setting the flag to `false` would print "non-refundable": a retired term (`retired_facts_check`), and it makes `uk-blue-staffy-puppy-buying-guide` throw at build (`:296`). **Add** `deposit_refund_max_pct: 70` and `deposit_refund_condition: "if a visitor fails to show up"` so prose derives its wording from the data and never types the rule by hand |
| b2 | `src/lib/faq.ts:31` token `deposit_terms` | `'refundable'` | the FAQ accordion **and FAQPage JSON-LD** on index, contact, breeders, pup-sale, buy, buying-guide | Derive it from b1: `refundable up to 70% if a visitor fails to show up` |
| b3 | `data/faq.json` rows `deposit` (:5), `listing-cost` (:203), `home-price-range` (:299) | "£{deposit_gbp}, {deposit_terms}, secures…" | same as b2 | Keep the token. Reword `deposit` to "£500 books your viewing and reserves your puppy; it is {deposit_terms}." Row 197 `listing-reputable-breeders` ("…before you pay anything") is generic buyer advice about other breeders, but read on our site it contradicts deposit-first viewing. Proposed: "…before you commit to a breeder" |
| b4 | `scripts/dup_content_audit.py:99` whitelist `"deposit 500 refundable"` + `rules/copy.md:71` | stock-line exemption | gate | Add the new stock line's normalised core once b2/b3 fix its wording. Keep the old core until the frozen pages stop printing it |
| b5 | `src/components/kit/_registry.ts:208` counter label | `'refundable deposit'` | kit preview and board-preview demos | `'deposit books your viewing'` (a tile has no room for the 70% condition) |
| b6 | `src/pages/available-puppies/[slug].astro:39` spec list | "Deposit £500, refundable" | all 6 puppy pages | "£500, books your viewing and reserves this puppy; refundable up to 70% if a visitor fails to show up" |
| b7 | `src/components/PuppyList.astro:17` and `src/pages/uk-locations/index.astro:31` | "…or collect in Carlisle after a refundable £500 deposit" | `/uk-locations/` hub (PuppyList's h2 variant renders nowhere today) | "…after a £500 deposit that books your viewing and reserves your puppy" |
| b8 | `data/bsuk-ontology.json:51–52` entity `ont:refundable-deposit` "£500 refundable deposit" | entity name | entity checks and boards | Rename to "£500 deposit (refundable up to 70%)". **Keep the id** because boards reference it, and add the old name as an alias |
| b9 | `tests/py/test_builder_skills.py:450` pins `£500 Refundable Deposit` in the checklist counters | test pin | — | Pin `£500 Deposit Books Your Viewing`, then change checklist line 719 to match |
| b10 | `tests/py/test_data_files.py:11,18` · `test_faq_data.py:27` · `test_design_components.py:597` | assert flag `True` / token mirror | — | Mirror b1/b2. The flag assertion stays, and the new fields get asserts |
| b11 | `tests/py/test_dup_content_audit.py:108` `STEM = "deposit 500 refundable"` | uses a real whitelist entry as its fixture | — | Follows b4 |
| b12 | `data/boards/_demo.json:132` "£500, refundable" · render fixtures `kit-counter-*.html` | demo and layout fixtures | board-preview `_demo`, render meta gate | Demo text follows b5. The fixtures measure layout, not wording, so they can change at any time or stay |
| b13 | **New gate (proposal)** in `scripts/retired_facts_check.py` | — | — | Flag "refundable" next to "deposit" unless "up to 70%" appears within the sentence, for new-family pages only (the frozen 12 stay allowlisted until (c) is ruled on). Without it, the rule is text that asks nicely |

## (c) Frozen copy on the 12 built pages — proposed, not applied

Rendered occurrences after `npm run -s build`, counted from `dist/`:

| Page | Rendered | Page-local lines (src) | Via (b) | Viewing-order conflict |
|---|---|---|---|---|
| `index` | 10 | `:167–168` ledge tile, `:817`, `:843` H5 "The Deposit Is Refundable", `:949`, `:968` | FAQ `home-price-range` | **`:970` H5 "Meeting the Litter Comes Before Paying"**, `:1130` "Come and meet the litter before you decide anything" |
| `blue-staffy-pup-sale-uk` | 7 | `:479` "How the Deposit Works … is refundable", `:492` "Getting It Back"; the counter tile "refundable deposit" is read from its board record (`sections[1].stats[2].label`) | FAQ `deposit` | **`:497` "You meet the litter first"**, **`:631` "come and look before you pay anything"**, **`:660` H5 "Meet Maggie Before You Pay Anything"** |
| `uk-blue-staffy-puppy-buying-guide` | 7 | `:617`, `:641`, `:780`, counter and table rows; `:296` build guard | FAQ `deposit` | `:632` "Every step before the deposit is reversible" |
| `buy-blue-staffy-puppies-uk` | 5 | `:490` Step Three body | FAQ `listing-cost` | `:752` section label "Before you send anything, come and look" |
| `blue-staffy-uk-breeders` | 3 | `:255` `deposit` const | FAQ `deposit` | — |
| `uk-blue-staffy-breeders-contact` | 2 | — | FAQ `deposit` (accordion + JSON-LD) | — |
| `blue-staffy-health-uk` | 1 | `:268` `deposit` const | — | — |
| `uk-staffordshire-bull-terrier-guide` | 1 | `:1175` | — | — |
| `thank-you-blue-staffy-puppies-journey` | 1 | `:213` "a refundable deposit of £500 holds that puppy" | — | `:223` H5 "The Conversation Comes Before the Deposit" (compatible) |
| `privacy-policy-uk`, `buy-staffy-puppies-for-sale-uk`, `blue-staffy-blog-guides` | 0 | — | — | — |

Frozen pages print their hero and counter figures from their own board records, so part of the
rendered copy lives in `data/boards/<slug>.json`, not in the `.astro` file. Approved boards carry the same wording in `brief`, `sections[]`, `meta_set`, `approval` and `dropped`:
`blue-staffy-pup-sale-uk` 23, `buy-blue-staffy-puppies-uk` 19, `index` 17, `uk-blue-staffy-puppy-buying-guide` 12,
`blue-staffy-health-uk` 6, `blue-staffy-uk-breeders` 6, `uk-staffordshire-bull-terrier-guide` 6,
`thank-you-…` 3, `uk-blue-staffy-breeders-contact` 1, `buy-staffy-puppies-for-sale-uk` 1 (a `dropped` note).

**Verbatim sets are not affected.** No `data/verbatim/*.json` set contains "refundable". The migrated site
said "non-refundable £300", and that wording was already excised as a wrong fact (`verbatim.changed`
reasons on the pup-sale and SBT-guide boards). Rule 15 therefore does not block a (c) change.

**Proposed (c) change set, if the user allows it:** a copy-only amendment to each page and its board:

1. Each "refundable" deposit line → the ruling's wording, sourced from b1.
2. The viewing-first headings and lines → deposit-first framing. Examples: index `:970` → "The Deposit
   Books Your Viewing"; pup-sale `:660` → "Your Deposit Books Your Visit to Maggie". Each is written on the
   page's board for approval, as the ruling requires.
3. Re-approve each amended board with `board_approve.py`, then run `gate:page` per page.

Because of the working rule-16 and rule-15 gates, this is a board amendment per page, not a search-and-replace.

## (n) Correct as it is

- `scripts/retired_facts_check.py` + `tests/py/test_retired_facts_check.py`, `test_page_intake.py`: "non-refundable" stays a **retired** term. The ruling makes the deposit partly refundable, not non-refundable.
- `data/locations.json` Hull `body_html` "non-refundable" (allowlisted, Known Issue 65): a migrated city body that project 5 rewrites from its outline.
- `data/facts/buy-blue-staffy-puppies-uk.json`: the old site's facts record (the £300 deposit, historical).
- `data/queries/raw/…liverpool/serp_google.response.json`: a captured third-party SERP.
- `data/quality/scorecards/*`: measurement records.
- `tests/py/test_query_augment.py:1512`, `test_page_board.py:1783`: buyer questions used as fixtures.
- `tests/py/test_agent_facts.py:17` docstring ("deposit £500, refundable") and `:320` fixture: descriptive. The docstring can follow (a) whenever the test file is next touched.

## Open questions for the user

1. **(b)** Apply b1–b13? This changes the FAQ answers and FAQPage JSON-LD on six **frozen** pages, the six puppy pages and the locations hub.
2. **(c)** Amend the frozen pages' deposit and viewing copy through their boards, or leave them frozen until project 5 reaches them?
3. **Condition.** Which 70% condition goes on the site: "if a visitor fails to show up" (the ruling) or "if the buyer changes their mind 1 day before delivery or pickup" (Lisa's original answer)?
4. **Short form.** Where a tile or meta has no room for the condition, may the copy say "£500 deposit books your viewing" with no refund wording at all? That is what (a) now teaches.
