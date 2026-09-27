---
name: bsuk-cta-strategy
description: "CTA strategy guide for BSUK — 22 homepage sections × 3 voice options = 66 conversion-ready CTAs. Three voices: Trust & Security, Direct & Transactional, Ethical & Quality. Use when writing or auditing any page section's CTA copy."
allowed-tools: [Read, Write, Bash]
---

## Golden Rule
> Use Claude Code and Playwright CLI to solve problems first.
> Only call MCPs, external CLIs, or APIs if the specific task genuinely cannot be done with Claude Code alone.

---

## How to Use This Skill

Each section provides three CTA variations. Select the voice matching the reader's intent:
- 🛡️ **Trust & Security** — high-value buyers who prioritize safety and reliability
- ⚡ **Direct & Transactional** — mobile users and decision-ready buyers
- 🌱 **Ethical & Quality** — SEO/AI indexing and conscious buyers

Place the selected CTA as an H2 or lead paragraph directly above the button pair.

> **Brand note:** the breeder is **Lisa Bright**, Carlisle, Cumbria. Locked figures:
> six named pups at **£1,500** (Roman, Byrd, Ince) and **£1,700** (Vennie, Christa, Cheryl);
> a refundable **£500** deposit; **UK home delivery £200–£350** by distance,
> by DEFRA-approved transport, or collection in Carlisle; **28 UK cities**; a **12–14 year** breed lifespan.
> Everything else is NOT FETCHED. The licence line is LICENCE_CLAIM_PLACEHOLDER.
> Never let another breeder's vocabulary back in — see
> `.claude/skills/bsuk-seo-master-checklist/SKILL.md` Appendix C. Button emoji: canonical set only (✅ ✈️ 📞) — never marketing emoji.

---

## Section 1: Hero

🛡️ **Trust & Security:**
> "Don't settle for 'maybe' when it comes to your puppy's health." Every puppy comes home with a full veterinary health check and a vet-signed health card.
> **Button:** Browse Available Puppies

⚡ **Direct & Transactional:**
> "Ready to meet your new best friend?" Browse the current litter — Blue Staffy puppies, each with a full veterinary health check, first vaccinations and a microchip. UK home delivery by DEFRA-approved transport, £200–£350 by distance.
> **Button:** Check Availability ✅

🌱 **Ethical & Quality:**
> "Discover the difference of a family breeder who puts health first." Raised in our home with species-appropriate enrichment and canine behavioral protocols.
> **Button:** View Available Blue Staffies

---

## Section 2: Trust Bar / Credentials

🛡️ **Trust & Security:**
> "Every credential here is verifiable — look us up." LICENCE_CLAIM_PLACEHOLDER License · LICENCE_CLAIM_PLACEHOLDER Home-Bred Documentation · Canine Vet Health Certificates
> **Button:** Verify Our Credentials

⚡ **Direct & Transactional:**
> "Vet-checked · UK home delivery by DEFRA-approved transport, £200–£350 by distance · Transparent pricing"
> **Button:** See Our Puppies

🌱 **Ethical & Quality:**
> "Breeding Blue Staffies is not a transaction — it's a 12-to-14-year commitment. We honor that responsibility every day."
> **Button:** Our Breeding Philosophy

---

## Section 3: Available Puppies

🛡️ **Trust & Security:**
> "These puppies are going fast — and for good reason." Every puppy: a full veterinary health check, first vaccinations, a microchip, worming and flea treatment.
> **Button:** Reserve a Puppy Now

⚡ **Direct & Transactional:**
> "Only [X] puppies available this litter." Blue, blue and white, white, and blue with a white blaze. £1,500 a male, £1,700 a female.
> **Button:** View All Available Puppies

🌱 **Ethical & Quality:**
> "We raise a small number of puppies so we can give every one the socialization and care they deserve."
> **Button:** Meet the Current Litter

---

## Section 4: After You Take Your Puppy Home

A health-guarantee CTA is written only once `guarantee_days` in `data/settings.json` is set (null today), and names its length from that setting. Until then this section is the support the breeder gives (`data/faq.json` `home-after-support`).

🛡️ **Trust & Security:**
> "Your puppy leaves with a puppy pack, its health records and its paperwork — and you can write to us before or after it comes home."
> **Button:** How We Support You

⚡ **Direct & Transactional:**
> "A question asked after the handover is answered the same way as one asked before it — by us, not an agency."
> **Button:** Ask Us Anything

🌱 **Ethical & Quality:**
> "Support after the sale isn't a sales tactic — it's what a breeder who raised the puppy owes the family who takes it home."
> **Button:** How We Health-Check

---

## Section 5: Health Checks

Name the parents' L-2-HGA and HC-HSF4 DNA tests, never a result: the results are `NOT FETCHED` (`data/quality/evidence-ledger.json` `parents-dna-clear`) until the certificates are on file.

🛡️ **Trust & Security:**
> "A full veterinary health check for every puppy, and a vet-signed health card that goes home with it — because we care about your family."
> **Button:** See Our Health Testing

⚡ **Direct & Transactional:**
> "Every BSUK puppy: vet health-checked, vaccinated, microchipped, raised in our home. Both parents are DNA-tested for L-2-HGA and HC-HSF4 — ask to see the certificates."
> **Button:** View Health Certificates

🌱 **Ethical & Quality:**
> "A veterinary health check isn't optional at BSUK — every puppy has one before it goes home."
> **Button:** Our Health Protocol

---

## Section 6: Male or Female

🛡️ **Trust & Security:**
> "Don't guess which puppy fits your home — ask the breeder who raised all six."
> **Button:** Compare Our Puppies

⚡ **Direct & Transactional:**
> "Males £1,500 · females £1,700 — the price follows the sex, not the coat. Which is yours?"
> **Button:** See All Available Puppies

🌱 **Ethical & Quality:**
> "Choosing between a male and a female is one of the most personal decisions in puppy ownership."
> **Button:** Male or Female? Our Guide

---

## Section 7: Age at Placement

🛡️ **Trust & Security:**
> "Age at placement matters — a puppy comes home at eight weeks at the earliest."
> **Button:** Why Eight Weeks

⚡ **Direct & Transactional:**
> "Eight weeks at the earliest, never sooner. Ask us when this litter is ready to come home."
> **Button:** Ask When They're Ready

🌱 **Ethical & Quality:**
> "Those last weeks with the mother and the litter are where a puppy learns bite inhibition and how to read another dog — we don't cut them short."
> **Button:** Care Guide + Pricing

---

## Section 8: DEFRA-approved transport Delivery / Delivery

🛡️ **Trust & Security:**
> "Your puppy travels to you by road with DEFRA-approved transport, priced by distance: £200–£350."
> **Button:** How Delivery Works

⚡ **Direct & Transactional:**
> "We ship nationwide via DEFRA-approved transport. Your puppy, your city."
> **Button:** Check Your Delivery Price

🌱 **Ethical & Quality:**
> "We chose DEFRA-approved transport delivery because we care about the puppy's welfare — comfort and safety are non-negotiable."
> **Button:** Our Delivery Promise

---

## Section 9: Pricing

🛡️ **Trust & Security:**
> "The price you see is the price you pay. No surprise fees at pickup."
> **Button:** See All Pricing

⚡ **Direct & Transactional:**
> "£1,500 for a male, £1,700 for a female. A £500 refundable deposit reserves any of them."
> **Button:** View Current Prices

🌱 **Ethical & Quality:**
> "Transparent pricing is part of ethical breeding. We publish our prices because we have nothing to hide."
> **Button:** Price Guide

---

## Section 10: Testimonials

🛡️ **Trust & Security:**
> "Families across the UK trusted BlueStaffyUK with one of the biggest decisions of their year."
> **Button:** Read All Reviews

⚡ **Direct & Transactional:**
> "Read what our families say." (star ratings and counts are NOT FETCHED — never invent one)
> **Button:** View Reviews

🌱 **Ethical & Quality:**
> "The best measure of ethical breeding isn't the certificate — it's whether buyers come back."
> **Button:** Family Stories

---

## Section 11: Temperament & Intelligence

🛡️ **Trust & Security:**
> "Blue Staffies are the most gifted family dogs in the puppy world — and ours are raised around constant human conversation."
> **Button:** Temperament & Bonding Guide

⚡ **Direct & Transactional:**
> "Home-raised for vocal confidence. Socialized daily. Ready to bond, learn, and talk."
> **Button:** Meet Our Family Dogs

🌱 **Ethical & Quality:**
> "An Blue Staffy's intelligence is a lifelong responsibility — we raise ours with the enrichment that mind demands."
> **Button:** How We Socialize

---

## Section 12: About Lisa Bright

🛡️ **Trust & Security:**
> "You're not buying from a website. You're buying from Lisa Bright in Carlisle — and her phone number is on every page."
> **Button:** Meet the Breeder

⚡ **Direct & Transactional:**
> "One family kennel in Carlisle. One phone number. Six pups, named."
> **Button:** Call Us Now

🌱 **Ethical & Quality:**
> "We didn't start BlueStaffyUK as a business. We started it because we fell in love with these puppies."
> **Button:** Our Story

---

## Section 13: FAQ

🛡️ **Trust & Security:**
> "Every question you're afraid to ask, answered honestly."
> **Button:** See All Questions

⚡ **Direct & Transactional:**
> "How much? How long? How do I know it's real? Answered."
> **Button:** Read the FAQ

🌱 **Ethical & Quality:**
> "We publish our FAQ because transparency is part of the breeding process, not just the sales process."
> **Button:** Common Questions

---

## Section 14: Contact / Inquiry

🛡️ **Trust & Security:**
> "Before you commit, talk to Lisa Bright. No sales pressure — just honest answers."
> **Button:** Send a Question

⚡ **Direct & Transactional:**
> "Ready to reserve? Questions first? Either way — start here."
> **Button:** Inquire Now

🌱 **Ethical & Quality:**
> "We want you to be 100% sure before you reserve. Ask us anything."
> **Button:** Start the Conversation

---

## Section 15: Location Pages

🛡️ **Trust & Security:**
> "Trusting a breeder you've never met is a leap of faith. Here's how to verify everything about BlueStaffyUK."
> **Button:** Verify BlueStaffyUK

⚡ **Direct & Transactional:**
> "BlueStaffyUK delivers to [City] by road, by DEFRA-approved transport, for £200–£350 by distance — or collect from Carlisle."
> **Button:** Reserve Your [City] Blue Staffy

🌱 **Ethical & Quality:**
> "Every puppy is raised in our home in Carlisle and delivered to [City] by DEFRA-approved transport."
> **Button:** Read Our Reviews

A family count and years in business are NOT FETCHED — never write one, not even as a placeholder to fill later.

---

## Section 16: Comparison Pages

🛡️ **Trust & Security:**
> "We only compare puppies we actually raise — we're not guessing about the Blue Staffy."
> **Button:** Honest Species Comparison

⚡ **Direct & Transactional:**
> "Blue Staffy vs [Other Species]: side-by-side on price, lifespan, temperament, and temperament."
> **Button:** See the Comparison

🌱 **Ethical & Quality:**
> "The best breed comparison comes from someone who raises Staffies in her own home."
> **Button:** Read the Comparison

---

## Section 17: Adoption / Rescue

🛡️ **Trust & Security:**
> "Rescue is noble. But 'unknown health history' is a real risk — here's how to evaluate it honestly."
> **Button:** Adoption vs Breeder Guide

⚡ **Direct & Transactional:**
> "Rescue Blue Staffy or a BlueStaffyUK home-raised puppy — we help you make the right call for your family."
> **Button:** Compare Your Options

🌱 **Ethical & Quality:**
> "We support rescue. We also believe every family deserves to know what they're bringing home."
> **Button:** Make an Informed Choice

---

## Section 18: Waitlist / Future Litters

🛡️ **Trust & Security:**
> "Joining the waitlist costs nothing and holds your place in line for the next litter."
> **Button:** Join the Waitlist

⚡ **Direct & Transactional:**
> "Next litter: [date]. Only [X] spots remaining."
> **Button:** Reserve Your Spot

🌱 **Ethical & Quality:**
> "We limit each litter because quality can't scale."
> **Button:** Get on the List

---

## Section 19: Coat Colours in Our Litter

🛡️ **Trust & Security:**
> "Solid blue, blue and white, white, or blue with a white blaze — the coat is looks alone; the price follows the sex."
> **Button:** See All Available Puppies

⚡ **Direct & Transactional:**
> "Each pup's coat is on its card (`colour` in `data/puppies.json`). See current puppies."
> **Button:** View Available Puppies

🌱 **Ethical & Quality:**
> "We never compromise health for looks — every Staffy is bred for vitality first."
> **Button:** Our Breeding Standards

---

## Section 20: Early Socialization & Home-Rearing

🛡️ **Trust & Security:**
> "A confident puppy starts with its breeder — ours are home-reared and socialized from the first weeks of life."
> **Button:** Our Rearing Approach

⚡ **Direct & Transactional:**
> "Home-reared. Step-up trained. Calm with handling. Confident around new people."
> **Button:** See How We Raise Them

🌱 **Ethical & Quality:**
> "Early, gentle socialization shapes an Blue Staffy's lifelong temperament — we invest in it every day."
> **Button:** How We Home-Rear

---

## Section 21: Health Guarantee Detail (waits for `guarantee_days`)

Not written until `guarantee_days` in `data/settings.json` is set (null today). Then each CTA names the length from that setting and links the written terms — never "no fine print", "no exceptions" or a length typed by hand (`guarantee_days` is the only source).

---

## Section 22: Footer / Final CTA

**The site-wide band is the board's call.** The footer's CTA band ("Ready to meet the
litter?") renders only when the page's approved board says `brief.cta.global_cta: "shown"`;
`"hidden"` removes it from the built page (`src/lib/globalCta.ts` through
`src/layouts/PageShell.astro`, tested by `tests/py/test_global_cta.py`). Choose `hidden` when
the page already closes on its own final CTA, so the reader is not asked twice in a row.

🛡️ **Trust & Security:**
> "Still have questions? Lisa Bright answer every inquiry personally."
> **Button:** Contact the Breeders

⚡ **Direct & Transactional:**
> "Ready? Available Blue Staffies are waiting."
> **Button:** View Available Puppies →

🌱 **Ethical & Quality:**
> "Every family we've matched has been the right match. We won't rush yours."
> **Button:** Start the Conversation

---

## Rules

1. **Read price-matrix.json** before using any pricing CTAs — never hardcode prices
2. **Match voice to page intent** — high-value buyers get Trust, mobile searchers get Direct, informational pages get Ethical
3. **One CTA voice per section** — don't mix all three in one section
4. **CTA button text: 2–5 words** — never a full sentence
5. **Availability numbers must be accurate** — check each pup's `status` in `data/puppies.json` before using "[X] available"
6. **Update seasonally** — "2026" and "this month" references expire
7. **No dog terms, no marketing emoji** — never puppy/litter/grooming/hypoallergenic; buttons use only canonical emoji (✅ ✈️ 📞)
