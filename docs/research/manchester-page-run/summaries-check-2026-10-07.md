# Summaries fact-check — blue-staffy-puppies-manchester-uk (2026-10-07)

Adversarial check of the uncommitted top-level `summaries` key in
`data/research-boards/blue-staffy-puppies-manchester-uk.json` against the record's own text
(`git show HEAD:` record; the rest of the record is byte-identical to HEAD, checked by script).
Rule applied: CLAUDE.md working rule 9 and the summaries contract (no new facts; every number,
date, name and claim supported by that section's or that item's own text; section 15 checked
against `ai_overview` session / note / implication).

## Counts

| Verdict | Lines |
|---|---|
| SUPPORTED | 169 |
| DISTORTED | 14 |
| UNSUPPORTED | 1 |
| **Total** | **184** (142 bullets, 2 cost lines, 40 care lines) |

No line states a health result, a "clear", a licence or KC registration as fact, or a price,
deposit or delivery figure that differs from the source. No line states our own mileage or drive
time as a page fact.

## Non-supported lines

| # | Key | Line | Verdict | Source evidence | Suggested fix |
|---|---|---|---|---|---|
| 1 | sections.Status bullets[5] | "Search volumes, local place names and competitor strength come from free tools: autocomplete, Trends, Keyword Planner and Ahrefs' free checker." | DISTORTED (low) — part of the source dropped | Research method: these come from free sources "beside London's banked DataForSEO backlinks file (2026-09-30)". Competitor strength is partly the paid, banked DataForSEO file. (The section's care[2] says so, but this bullet on its own does not.) | "…and Ahrefs' free checker, beside London's saved DataForSEO file of 30 Sept." |
| 2 | sections.3 bullets[1] | "Deposits appear only inside sellers' adverts. No page states an amount, a refund or what the deposit secures." | DISTORTED (low) — a case left out | Universal gaps: deposits appear inside sellers' advert texts "and as a platform badge on two puppies.co.uk adverts ('Puppies safety deposit scheme', no terms on the page)". | "Deposits appear only inside sellers' adverts and one platform badge with no terms. No page states…" |
| 3 | sections.3 bullets[5] | "Four of Google's six People Also Ask questions get no answer anywhere: male or female, good pets, aggression, left alone." | DISTORTED — scope widened | PAA against the pool: "all eight saved pages checked by script". The source covers the eight pool pages, not "anywhere". | "…get no answer on any of the eight pages…" |
| 4 | sections.6 bullets[1] | "On Google the colour doesn't rank. All five top results name the breed and Manchester; none says \"blue\"." | DISTORTED — qualifier dropped, claim made stronger | §6: "none of the five says 'blue' in its title or H1". The pages do say blue elsewhere: Pets4Homes' snippet has "BLUE STAFFORDSHIRE BULL…" and 7 of its 24 card titles say blue (§1 #1). | "…none says \"blue\" in its title or H1." |
| 5 | sections.6 bullets[2] | "Domain strength doesn't decide. Gumtree is strongest on Ahrefs (78) but #4; Staffie Owners is weakest (0) but #2." | DISTORTED — caveat dropped | §6: "Authority **alone** does not set Google's order." The summary turns "not alone" into "not at all". The positions are also Google's banked order, which the line does not say. | "Domain strength alone doesn't set Google's order. Gumtree is strongest on Ahrefs (78) but Google #4; Staffie Owners is weakest (0) but #2." |
| 6 | sections.7 bullets[1] | "State our deposit: £500 books the viewing, reserves the puppy and comes off the price, with our written refund terms." | UNSUPPORTED (low) — added qualifier in our own voice | §7: "with the refund wording read from deposit_refund_clause". Nothing in the section calls the refund terms "written", which suggests a contract term. The clause is a data key ("up to 70% refundable if you change your mind up to 1 day before collection or delivery"). | "…with the refund terms deposit_refund_clause sets." |
| 7 | sections.19 bullets[0] | "Word target: only one competitor page reads as prose, so the word band is the breeder's pick on this board." | DISTORTED — claim made stronger | §19: "the script used one page (Freeads, **read as prose**) and excluded seven as listings". §1 structural read: "All eight pool pages are feeds of other people's adverts". S2 why: "Freeads, is a feed as well". Freeads was classed as prose by the script. It does not read as prose. | "Word target: the script could use only one page (Freeads, itself a feed), so the word band is the breeder's pick on this board." |
| 8 | sections.19 bullets[1] | "Owners' words and 11 new Reddit threads: Reddit blocked every tool we could use. One Facebook group post was unreachable too." | DISTORTED — wrong attribution | §19 owner_language: "Firecrawl refuses reddit.com, WebFetch refuses reddit.com … Claude in Chrome and the app browser refuse reddit.com by safety policy". Only the Playwright 403 and the curl JS challenge came from Reddit. §4's summary has it right ("blocked by Reddit or refused it"). | "…every tool we could use was blocked by Reddit or refused reddit.com…" |
| 9 | items.serp.results[3] bullets[0] | "Ranks: Google #4 on an exact breed-and-Manchester URL, from the strongest domain in the pool (Ahrefs 78)." | DISTORTED — claim made stronger, wrong cause given (the example the brief names) | §1 #4 Why it ranks: "**Not authority alone**: gumtree.com is the strongest domain in the pool **on Ahrefs** … and still ranks #4." The summary gives authority as the reason it ranks, and puts the index only in parentheses. | "Ranks: Google #4 on an exact breed-and-Manchester URL. Not authority alone: strongest in the pool on Ahrefs (78), yet only #4." |
| 10 | items.serp.results[5] bullets[1] | "Weakness: none of its 7 blue matches is in Greater Manchester. They sit 19 to 68 miles away." | DISTORTED (low) — two numbers merged in a misleading way | §1 #6: "6 are for-sale adverts 30–68 miles away and 1 is a wanted advert 19 miles away." The merged range makes it look as if a blue puppy for sale is 19 miles out. | "…6 are for-sale adverts 30–68 miles away; the 7th is a wanted advert 19 miles away." |
| 11 | items.angles[0] bullets[0] | "The idea: we breed blue Staffies yet tell Manchester to choose colour last, because colour doesn't move our prices." | DISTORTED (low) — first reason dropped | M1 hook: "…because **the Kennel Club puts health and temperament first** and colour doesn't move our prices." The summary keeps only the second reason, the price. The Kennel Club reason comes back in bullet [1] only as "it agrees with". | "…choose colour last, because the Kennel Club puts health and temperament first and colour doesn't move our prices." |
| 12 | items.frameworks[1] bullets[0] | "The idea: Pain, Depth, Brief. Name the buyer's deposit fear, show what page one gets wrong, then give our facts." | DISTORTED (low) — meaning narrowed | Shape: "Depth explains why that worry is rational, **from independent guidance** and our own reading of the ranking pages" (the RSPCA and PAAG guidance in `why`). The summary narrows Depth to faults in page one. | "…show why the fear is rational, from independent guidance and page one, then give our facts." |
| 13 | items.frameworks[2] bullets[1] | "Why: Manchester searches hunt for a price floor, and page-one snippets quote other sellers' ranges up to £2,800." | DISTORTED (low) — scope widened | why: "Manchester's **commercial** searches hunt for a price floor: Three of the six related searches…". The summary leaves out "commercial". | "Why: three of Google's six related searches hunt for a price floor…" |
| 14 | items.frameworks[5] bullets[0] | "The idea: answer life questions as questions: male or female, good pets, aggression, left alone, rescue or breeder." | DISTORTED — wrong list | Shape: "male or female, exercise, a flat, time alone, the reputation worry and the banned-breed line, and buying or rescuing". trade_off: the bottom FAQ block "already holds" good pets and aggressive, and "No FAQ question may repeat a header". "Good pets" cannot be a heading in this group. The summary copies the PAA list, not the group's shape. | "…questions as questions: male or female, exercise, a flat, time alone, the reputation worry, the banned-breed line, buying or rescuing." |
| 15 | items.frameworks[5] bullets[1] | "Why: four of Google's six People Also Ask are life questions, and no page on page one answers any of them." | DISTORTED — scope widened | why: "None of **the eight pages** answers any of them (SERP, PAA against the pool)." Page one also has results outside the pool (Champdogs, Preloved, Dogs Trust) that were not checked. | "…and none of the eight pool pages answers any of them." |

## Supported, but in a sensitive category (watch list, not counted above)

These match their source. They are listed because they fall in categories the brief asked to flag:

- **sections.2 care[0]**: "The session brief puts Manchester about 120 miles from Carlisle, but the page itself states no mileage or drive time." This is a mileage, sourced to session brief Q8 (§2 Local). It is correctly framed as a board-only figure, but it must never reach page copy.
- **items.serp.results[2] bullets[2]**: types the guarantee label "Two-year health guarantee". This matches §1 #3 ("the Two-year health guarantee (`guarantee_label`)") and `data/settings.json`. On a page it must be read from `guarantee_label`, never typed (rule 9).
- **items.serp.results[5] bullets[2]**: "£1,500 a boy and £1,700 a girl". This matches §1 #6 and the price matrix. Note that "our blue puppies" covers 5 of the 6; Byrd is white at the same price.
- **items.frameworks[7] bullets[1]**: "We answer every enquiry within 24 to 48 business hours." This is a claim in our own voice. It matches the source (`data/faq.json` `enquiry-reply-time`).
- **sections.8 bullets[1]**: "Payment is by bank transfer." This is a claim in our own voice. It matches §8 (q04).
- **sections.3 care[1]** / **items.serp.results[5] care[0]**: Staffie Owners' £1,150–£1,750 blue range and "61% higher" are both attributed to its own analysis. §3's PAA line attributes the range to the "marketplace analysis". §1 #6's own text attributes only the 61% to it explicitly, and quotes the range as its FAQ wording.
