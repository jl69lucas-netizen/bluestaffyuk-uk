"""The fact lint: an agent may not state a fact BlueStaffyUK has not established.

Task 11 re-based a parrot breeder's agents into a dog breeder's repo. Vocabulary
substitution is mechanical and it lies well: `$1,500–$3,500` becomes `£1,500–£3,500`, a
40–60-year parrot lifespan becomes a 40–60-year dog, `CITES` becomes a licence the breeder
has never shown, and every one of those reads as a fact because it sits in the same
confident sentence the source repo wrote. `scripts/marker_check.py` cannot catch any of it:
not one of those lines carries a parrot marker.

So this lint checks the OTHER direction — not "does source vocabulary survive" but "does a
claim survive that nobody can back". It is mechanical on purpose: judgment about whether a
number is true has already failed once, in the review that produced this file.

What is locked, and therefore all that may be asserted:

  prices        £1,500 (Roman, Byrd, Ince) · £1,700 (Vennie, Christa, Cheryl)
  deposit       £500, refundable
  delivery      £200–£350 by distance, by DEFRA-approved transport
  lifespan      12–14 years (the Staffordshire Bull Terrier breed figure)
  locations     28 cities in data/locations.json

Everything else is `NOT FETCHED`, `LICENCE_CLAIM_PLACEHOLDER` or `LEGAL_CLAIM_PLACEHOLDER`.

Scope is `.claude/agents/*.md` AND `.claude/skills/**/SKILL.md`, so the system skills that
arrive in Task 12 are born under the same lint rather than having it retrofitted.
"""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]

PLACEHOLDERS = ("LICENCE_CLAIM_PLACEHOLDER", "LEGAL_CLAIM_PLACEHOLDER",
                "SITE_URL_PLACEHOLDER", "PHONE_PLACEHOLDER")

# Every sterling amount BSUK can actually stand behind. A range is checked whole, because
# `£1,500–£3,500` is a different claim from `£1,500` even though it contains it.
ALLOWED_MONEY = {"£500", "£1,500", "£1,700", "£200", "£350", "£200–£350",
                 # the litter's own span: the cheapest and the dearest puppy, both locked
                 "£1,500–£1,700"}

# `(?<![\d,])` / the trailing guard keep a sentence comma out of the amount: `£1,700,` is
# £1,700 followed by punctuation, not a different number.
AMOUNT = r"£\d[\d,]*(?<![,])"
MONEY = re.compile(AMOUNT + r"(?:\s*[–—-]\s*" + AMOUNT + r")?")

# Bare-token bans. Each is a fact BSUK has not established, or a body whose authority the
# source repo borrowed: US wildlife/agriculture regulators, a parrot lifespan, a US state
# count, and a host nobody has chosen.
# CAG geography. A US state or city in a meta template is not a harmless example: it is the
# territory the page claims to serve, and Task 12 shipped meta templates still promising delivery to
# California. BSUK's 28 cities are in data/locations.json and nowhere else.
CAG_GEO = ("California", "Los Angeles", "San Diego", "Texas", "Florida")

BANNED = (
    "40–60", "40-60", "50 cities", "50 states",
    "captive", "USDA", "APHIS", "CITES", "Cloudflare", "cloudflare",
    # The previous site's palette and type, replaced by src/styles/tokens.css in project 3.
    # An instruction file still quoting these teaches a writer the dead design system.
    "#2D6A4F", "#e8604c", "#faf7f4", "Newsreader", "IBM Plex",
    # The city the breeder has LEFT (Known Issue 16). An instruction file that still names
    # it teaches every agent the wrong home base, and the geography an agent believes ends
    # up in copy, in schema and in a meta template. The breeder is in Carlisle, Cumbria.
    "Glasgow",
    # Parrot residue from the source repo's species (found 2026-09-23 in the comparison
    # builder, the SEO checklist and the content-audit agent). A dog page that promises a
    # leg band or warns about psittacosis tells the reader nobody checked it.
    "Psittac", "psittac", "leg band", "powder-down", "cloacal", "proventricular",
    "Amazon Puppy |", "vs Amazon puppy", "amazons =", "Google US", "UKge",
    # Three more that the list above misses because the lint is case-sensitive, and that no
    # dog page can ever use: "Proventricular Dilatation Disease" in the content-audit agent,
    # "Keyword Ukge" in the SEO checklist, and "aviculture" (bird-keeping) in the same file.
    "Proventricular", "Ukge", "vicultur",
    # A US regulator and its paperwork, borrowed from the source repo: BSUK delivers by road
    # inside the UK, so no page may cite APHIS or an interstate certificate.
    "Plant Health Inspection", "Interstate",
    # A dog's sex is checked by the vet at the health check; DNA sexing is how a parrot
    # breeder sexes a bird. Every "DNA sexed" badge on a dog site is a claim nobody made.
    "DNA sex", "DNA-sex", "DNA Sex", "DNA-Sex",
) + CAG_GEO

# `Glasgow` has exactly three honest uses left in the instruction tree, and a line carrying
# one of them is allowed to name the city: the outreach page's slug and the live city row's
# slug (both in data/locations.json), which are URLs that still rank and are never renamed,
# and the debt note itself, which cannot be written without saying what the debt is.
# Nothing else — a trust pillar, a meta template, a delivery table — may say it. One list:
# tests/py/test_agent_residue.py reads the agents against this same pattern.
GLASGOW_ALLOWED = re.compile(r"staffy-breeding-dogs-glasgow|staffy-puppies-for-sale-glasgow|Known Issue 16")

# DEFRA is real here in exactly one form: the transport that carries a puppy. "DEFRA-approved
# breeder" / "DEFRA-compliant kennel" are claims nobody has verified.
DEFRA = re.compile(r"DEFRA", re.I)

# A number of years that is not the breed's. Windowed rather than regexed tightly because the
# claim shows up as "40-60 yrs", "lifetime (50 years)", "60 year commitment" and "12+ years".
YEARS = re.compile(r"(?i)\b(years?|yrs?)\b")
# A digit glued to letters is an identifier (`h3`, `70de`, `G-M...`), not a quantity.
NUMBER = re.compile(r"(?<![A-Za-z0-9-])\d+(?![A-Za-z0-9])")
ALLOWED_YEARS = {"12", "13", "14"}
# "years" is not always a lifespan. A span of DATA ("3 years of GSC data"), a duration of
# TRADING ("5 years running", "15 years' experience") and a calendar year are all ordinary
# English that the lifespan rule would otherwise report as a claim about how long a
# Staffordshire Bull Terrier lives. Narrow and documented, because the alternative is a
# lint people learn to ignore: the escape needs one of these words in the same window, and
# a bare calendar year 2020-2030 is a date, not an age.
NOT_A_LIFESPAN = re.compile(
    r"(?i)(of (GSC|GA4|search|history|data|records)|year[- ]on[- ]year|running|experience)")
# "first-year cost", "year 1 total": a budgeting horizon, not a claim about how long the dog
# lives. Narrow on purpose — only the literal ordinal-first-year phrasings, and only the
# digit 1.
FIRST_YEAR = re.compile(r"(?i)(first[- ]year|year[- ]1\b|year 1\b|1st[- ]year)")

HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
FENCE = re.compile(r"^\s{0,3}```\s*([A-Za-z]*)")
# A fence is only a reason to stop reading headings when what is inside it is CODE. The
# source repo fenced its report TEMPLATES as ```markdown, and `## LICENCE_CLAIM_PLACEHOLDER
# Query Gap` sat inside one — a heading that ships into a deliverable, invisible to a
# detector that skipped the whole block. So: skip headings in code, read them everywhere else.
CODE_LANGS = {"bash", "sh", "shell", "zsh", "python", "py", "json", "js", "javascript",
              "ts", "html", "css", "astro", "xml", "yaml", "yml", "diff", "sql"}

# Inside a code fence a bare numeral is a value, and the currency rules never see it: the
# cost calculator shipped `{ low: 1700, high: 2500 }` and passed a lint that only reads `£`.
#
# Scoped two ways, because a code block is full of honest four-digit numbers (`z-index: 9999`,
# `setTimeout(loadGA, 3000)`) and a lint that called those price defects would be deleted
# within a week. So: only in a script context, and only on a line that is ABOUT money.
BARE_4 = re.compile(r"(?<![\w.,-])([1-9]\d{3})(?![\w.,])")
ALLOWED_BARE = {"1500", "1700"}          # the two locked prices
ALLOWED_DIMS = {"1408", "1280", "1200", "1100"}   # image/viewport widths in use today
JS_LANGS = {"js", "javascript", "ts", "json"}
SCRIPT_OPEN = re.compile(r"(?i)<script\b")
SCRIPT_CLOSE = re.compile(r"(?i)</script>")
# The words a price wears when it is a variable rather than a pound sign.
MONEYISH = re.compile(r"(?i)\b(price|prices|cost|costs|low|high|amount|gbp|deposit|fee|"
                      r"total|subtotal|delivery|purchase)\b")


def _is_year(n):
    return 2020 <= int(n) <= 2030


# `blue and white Staffy: { ... }` is not JavaScript. It is what a blind vocabulary
# substitution does to an object key, and it means the snippet cannot run. The value must
# look like a JS value too, or every `Pages checked: [count]` line in a report template
# reads as broken code.
SPACED_KEY = re.compile(r"^\s*[A-Za-z]+(?: [A-Za-z]+)+\s*:\s*[\[{\'\"0-9]")
# A route or URL path: a placeholder is a claim-shaped word, not a path segment. The one
# sanctioned exception is `https://SITE_URL_PLACEHOLDER/...`, where the placeholder stands in
# the HOST position for the domain project 6 will register — that is the repo-wide convention
# (`CLAUDE.md`, `rules/`), not a claim. A placeholder in a path SEGMENT still fails.
ROUTE = re.compile(r"(?<!/)/[A-Za-z0-9_<>\[\]-]*(?:" + "|".join(PLACEHOLDERS)
                   + r")[A-Za-z0-9_<>\[\]-]*/?")


def targets():
    # `docs/reference/*.md` joined the walk in Task 13. Those five docs are loaded into a
    # session exactly the way an agent is — seo-rules.md is cited as the source of truth by
    # half the agents in the repo — so an unlocked price or a borrowed regulator in one of
    # them is the same defect, one document further from the page.
    return (sorted((ROOT / ".claude/agents").glob("*.md"))
            + sorted((ROOT / ".claude/skills").glob("**/SKILL.md"))
            + sorted((ROOT / "docs/reference").glob("*.md")))


def _norm(m):
    return re.sub(r"\s*[–—-]\s*", "–", m.strip())


def violations(path: pathlib.Path):
    out, fenced, lang, in_script = [], False, "", False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = FENCE.match(line)
        if m:
            if fenced:
                fenced, lang = False, ""
            else:
                fenced, lang = True, m.group(1).lower()
            in_script = False
            continue
        if fenced:
            if SCRIPT_OPEN.search(line):
                in_script = True
            if SCRIPT_CLOSE.search(line):
                in_script = False
        def bad(why):
            out.append("%s:%d  %s  |  %s" % (path.name, lineno, why, line.strip()[:120]))

        for m in MONEY.findall(line):
            if _norm(m) not in ALLOWED_MONEY:
                bad("unlocked amount %s (locked: %s)" % (_norm(m), ", ".join(sorted(ALLOWED_MONEY))))

        for tok in BANNED:
            # A hex is the same colour in either case, so #2D6A4F must also catch #2d6a4f.
            # Word bans stay case-sensitive: "captive" should not fire on a capitalised
            # sentence start that means something else.
            hit = tok.lower() in line.lower() if tok.startswith("#") else tok in line
            if hit and tok == "Glasgow" and GLASGOW_ALLOWED.search(line):
                continue
            if hit:
                bad("banned token %r" % tok)

        if DEFRA.search(line) and "transport" not in line.lower():
            bad("DEFRA asserted outside 'DEFRA-approved transport'")

        for ym in YEARS.finditer(line):
            window = line[max(0, ym.start() - 12):ym.end() + 12]
            # Digits belonging to a sterling amount are priced, not aged; MONEY already
            # judged them and double-counting one line as two defects hides the real one.
            for m in MONEY.finditer(window):
                window = window.replace(m.group(0), " ")
            for num in NUMBER.findall(window):
                if num == "1" and FIRST_YEAR.search(line):
                    continue
                if NOT_A_LIFESPAN.search(window) or _is_year(num):
                    continue
                if num not in ALLOWED_YEARS:
                    bad("year figure %r near %r (the breed figure is 12–14)" % (num, ym.group(0)))

        if fenced and (lang in JS_LANGS or in_script):
            if SPACED_KEY.match(line):
                bad("object key with an unquoted space \u2014 this snippet cannot run")
            if MONEYISH.search(line):
                for n in BARE_4.findall(line):
                    if n in ALLOWED_BARE or n in ALLOWED_DIMS or _is_year(n):
                        continue
                    bad("bare numeral %s priced in a code block "
                        "(the locked prices are 1500 and 1700)" % n)

        if HEADING.match(line) and not (fenced and lang in CODE_LANGS):
            for ph in PLACEHOLDERS:
                if ph in line:
                    bad("placeholder %s used as a noun in a heading" % ph)

        for m in ROUTE.finditer(line):
            bad("placeholder inside a route or URL: %s" % m.group(0))
    return out


@pytest.mark.parametrize("path", targets(), ids=lambda p: p.parent.name + "/" + p.name)
def test_agent_states_only_locked_facts(path):
    bad = violations(path)
    assert bad == [], (
        "an unbacked claim survived the re-base. Only £500 / £1,500 / £1,700 / £200–£350, the "
        "12–14-year breed lifespan and the 28 cities in data/locations.json may be asserted; "
        "everything else is NOT FETCHED, LICENCE_CLAIM_PLACEHOLDER or LEGAL_CLAIM_PLACEHOLDER. "
        "Rewrite the example, never delete the rule:\n  " + "\n  ".join(bad))


def test_there_is_something_to_lint():
    assert len(targets()) >= 36


def test_the_lint_actually_fires(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("```js\nconst prices = {\n  blue and white Staffy: { low: 1700, high: 2500 }\n};\n```\n"
                 "```markdown\n## LICENCE_CLAIM_PLACEHOLDER Query Gap\n```\n"
                 "Lifetime estimate (40-60 yrs) £85,000–£250,000 from captive DEFRA-compliant breeders\n"
                 "## LICENCE_CLAIM_PLACEHOLDER Writing Rules\n"
                 "Fetch /LICENCE_CLAIM_PLACEHOLDER/report\n"
                 "A parrot lives 40 years.\n", encoding="utf-8")
    kinds = violations(p)
    assert any("unlocked amount" in v for v in kinds), kinds
    assert any("banned token" in v for v in kinds), kinds
    assert any("DEFRA asserted" in v for v in kinds), kinds


    assert any("year figure" in v for v in kinds), kinds
    assert any("used as a noun in a heading" in v for v in kinds), kinds
    assert any("bare numeral 2500" in v for v in kinds), kinds
    assert any("Query Gap" in v and "heading" in v for v in kinds), kinds
    assert any("placeholder inside a route" in v for v in kinds), kinds
    assert any("year figure '40'" in v for v in kinds), kinds
    assert any("object key with an unquoted space" in v for v in kinds), kinds


# ── the escapes, proven to stay quiet ───────────────────────────────────────
# A lint is only as good as the lines it DOESN'T report. These are the four shapes that
# cost the rule its credibility if it fires on them, so each is pinned.
@pytest.mark.parametrize("line", [
    "Pull 3 years of GSC data.",
    "5 years running",
    "15 years' experience with the breed",
    "Compare year-on-year: 2019 vs 2024.",
    "Blue Staffies live 12\u201314 years.",
    "Estimate Your First-Year Cost",
    "Data from 2024 covering three years of records",
])
def test_these_lines_are_not_lifespan_claims(tmp_path, line):
    p = tmp_path / "SKILL.md"
    p.write_text(line + "\n", encoding="utf-8")
    years = [v for v in violations(p) if "year figure" in v]
    assert years == [], years


@pytest.mark.parametrize("line", [
    "A parrot lives 40 years.",
    "Blue Staffies live 50\u201370 years.",
    "Lifetime estimate (40-60 yrs)",
])
def test_these_lines_are_lifespan_claims(tmp_path, line):
    p = tmp_path / "SKILL.md"
    p.write_text(line + "\n", encoding="utf-8")
    assert any("year figure" in v for v in violations(p)), violations(p)


def test_the_lint_bans_cag_geography(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("Delivery to California, Los Angeles and San Diego.\n", encoding="utf-8")
    bad = violations(p)
    assert len(bad) == 3, bad
    assert all("banned token" in v for v in bad), bad


def test_the_lint_bans_the_old_city_but_spares_the_slug_and_the_debt_note(tmp_path):
    """Known Issue 16: the city is banned, its two honest uses are not."""
    p = tmp_path / "SKILL.md"
    p.write_text(
        "Collection in Glasgow after a refundable deposit.\n"
        "The Glasgow outreach page /uk-locations/staffy-breeding-dogs-glasgow/ keeps its URL.\n"
        "Known Issue 16: everything that says Glasgow is now wrong.\n",
        encoding="utf-8")
    bad = [v for v in violations(p) if "'Glasgow'" in v]
    assert len(bad) == 1, bad
    assert "Collection in Glasgow" in bad[0], bad


# ── source-repo residue in the skills (project 5 readiness, 2026-09-23) ─────
# The bans above read agents, skills and reference docs for claims. This list reads the
# SKILLS (and the slash commands) for residue that is not a claim BSUK could ever make true:
# another business's regulators, geography, animals, brand and deploy model. Every entry was
# found in a skill on 2026-09-23 — the SEO checklist cited the AVMA and the FTC, the map skill
# served "CITY, STATE" and Arizona, the entity graph listed parrot names and US airlines, the
# blog and comparison builders promised "since 2014" and "12+ years", and five skills told a
# builder to `git push origin main`. The agents are not in scope here yet: widen
# `residue_targets()` to `.claude/agents/*.md` in the task that clears them.
RESIDUE = (
    ("a US animal-health or retail source (UK sources: docs/reference/external-link-library.md)",
     re.compile(r"\b(?:AVMA|AAHA|ASPCA|Chewy|PetMD|IAABC|Craigslist)\b|Pet Poison Helpline|"
                r"Veterinary Emergency Group|avma\.org|aaha\.org|aspca\.org|chewy\.com|petmd\.com|"
                r"petpoisonhelpline|veterinaryemergencygroup|iaabc\.org|clickertraining\.com")),
    ("a US regulator", re.compile(r"\bFTC\b|ftc\.gov")),
    ("US geography — BSUK serves the 28 UK cities in data/locations.json",
     re.compile(r"\b(?:Arizona|Virginia|Illinois|Pennsylvania|Ohio|Michigan|Colorado|Tennessee|"
                r"North Carolina|Phoenix|STATENAME)\b|CITY%2C%20STATE|CITY, STATE|state/city|"
                r"Continental US|\binterstate\b")),
    ("air transport — delivery is by road, by DEFRA-approved transport",
     re.compile(r"(?i)\bairports?\b|\bairlines?\b|\bair transport\b|air-cargo|\bin cargo\b|"
                r"Delta, United")),
    ("the other source repo's brand (MFS / Maltipoos For Sale)",
     re.compile(r"\bMFS\b|Maltipoo|Lawrence (?:&|and) Cathy")),
    ("the source repo's animals",
     re.compile(r"\b(?:Roys|Amie|Elad|Jins|Jeni|Maxy|Rily)\b|\bP\. e\.|Canine Biotech")),
    ("the source repo's rule name — BSUK's is data/quality/evidence-ledger.json",
     re.compile(r"Verified-Claim Ledger")),
    ("an unbacked years-in-business claim", re.compile(r"since 2014|`?12\+`?\s*[Yy]ears")),
    ("a deploy push — there is no remote until project 6",
     re.compile(r"git push|push origin|[Cc]ommit \+ push|commit and push|push = deploy|"
                r"Deploy \+ push|push to GitHub|main auto-deploys|unpushed commits")),
    ("a fixed section-count template — the rule is competitors' count + 3, floor 9",
     re.compile(r"22[–-]2[45]|\b22[- ]section|\b22 sections|fewer than 22")),
    ("a component, prop or word this repo does not have",
     re.compile(r"NewsletterV2|hideGlobalCta|reUKble|the host \(NOT FETCHED")),
    ("a coat line priced as a product line — price is by sex (data/puppies.json)",
     re.compile(r"(?i)brindle[^|\n]{0,40}\((?:Roman|Vennie)")),
    ("a licence asserted as ours — it is LICENCE_CLAIM_PLACEHOLDER until confirmed",
     re.compile(r"—\s*licensed\b|licensed home-raised|Licensed Carlisle|\"Licensed Blue|"
                r"Licensed family home")),
    # Widened after the Task 12 review (2026-09-24): four more shapes the first list missed.
    ("a price spelled out in words — prices are numerals from data/price-matrix.json",
     re.compile(r"(?i)\b(?:twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
                r"twenty|thirty)(?:[- ](?:one|two|three|four|five|six|seven|eight|nine))?[- ]hundred\b")),
    ("a Blue-Brindle variant — none of the six pups is brindle (data/puppies.json `colour`)",
     re.compile(r"(?i)\bblue-brindle\b")),
    ("\"licensed breeder\" asserted — a licence is LICENCE_CLAIM_PLACEHOLDER until confirmed",
     re.compile(r"(?i)\blicen[cs]ed breeders?\b")),
    ("the source repo's Latin variant naming (P. …)", re.compile(r"\(P\. [a-z]")),
    # Widened again (2026-09-24): the source repo bred birds. Its health vocabulary is not a
    # dog's. BSUK's health facts are the vet check (data/faq.json `puppy-package`,
    # `health-vaccinations`) and the parents' L-2-HGA / HC-HSF4 DNA tests, whose results are
    # NOT FETCHED in data/quality/evidence-ledger.json (`parents-dna-clear`).
    ("the source repo's bird-health vocabulary — BSUK's is the vet check and the parents' DNA tests",
     re.compile(r"(?i)sex-check|\bPCR\b|polyomavirus|psittac|\bavian\b|\bplucking\b|\bUV-B\b")),
    ("a weaning age no BSUK data states — a puppy goes home at eight weeks at the earliest "
     "(data/faq.json `buying-best-age`)",
     re.compile(r"(?i)\bwean\w*\b[^|\n]{0,25}?\b\d+\s*[–-]\s*\d+[\s-]*(?:weeks?|months?)\b|"
                r"\b\d+\s*[–-]\s*\d+[\s-]*(?:weeks?|months?)\b[^|\n]{0,15}\bwean")),
    # And again (Task 12 final review): none of the six pups is brindle, so BSUK never offers
    # one — "our … brindle", a brindle pup for sale, "blue or blue brindle" as a choice, a
    # coat spec, a Blue Brindle Staffy named as a product. A breed-level coat list ("blue,
    # blue brindle and white coats") and a "vs" topic stay allowed (see residue()).
    ("a brindle pup offered as ours — each pup's coat is its `colour` in data/puppies.json",
     re.compile(r"(?i:\b(?:our|we|us)\b[^|\n]{0,40}\bbrindle\b|"
                r"\bbrindle staff(?:y|ies)?\s+(?:for sale|pups?|puppy|puppies)|"
                r"\bbrindle staffordshire bull terriers?\s+(?:for sale|pups?|puppy|puppies)|"
                r"\bbrindle (?:pups?|puppies)\b|"
                r"\bspecialis\w+ in\b[^|\n]{0,40}\bbrindle\b|"
                r"\bblue\s*(?:/|or)\s*blue brindle\b|"
                r"\bcoat:\s[^|\n]*\bbrindle\b)|"
                r"\bBlue Brindle Staff(?:y|ies)\b")),
    ("a placement count or years in business — both are NOT FETCHED, even as a [N] template",
     re.compile(r"(?i)\bhundreds of (?:families|blue staff|staff|puppies|placements)|"
                r"\[N\]\+?\s*families|families for \[X\]\+?\s*years|"
                r"\[X\]\+?\s*years\b(?![^|\n]{0,20}\b(?:old|lifespan|live))")),
    ("the source repo's CITES paperwork — a UK puppy has no permit, appendix or CoP listing",
     re.compile(r"\bCoP ?17\b|(?i:\bappendix[\s-]i\b)")),
    ("a reply-time promise — the only reply time on file is data/faq.json `home-after-support`",
     # fires only when WE are the ones replying; "within 24 to 48 business hours" (the backed
     # figure) and vet advice ("book a vet visit within 48 hours") stay silent
     re.compile(r"(?i)\b(?:we|I|us|Lisa(?: Bright)?|she|BlueStaffyUK|BSUK)\b[^.|\n]{0,30}?"
                r"\b(?:repl(?:y|ies|ied)|respond(?:s|ed)?|answer(?:s|ed)?|get back)\b[^.|\n]{0,20}?"
                r"\b(?:within|in under)\s+(?:\d+|a|an|one)\s*(?:hours?|days?|minutes?)\b")),
)
# A line that FORBIDS the push is the point of saying it, as in tests/py/test_claude_md.py.
PUSH_FORBIDDEN = ("never `git push`", "no `git push`", "no push", "not push", "nothing to push", "never push")


def residue_targets():
    return (sorted((ROOT / ".claude/skills").glob("*/SKILL.md"))
            + sorted((ROOT / ".claude/commands").rglob("*.md")))


def residue(path: pathlib.Path):
    out = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for why, rx in RESIDUE:
            if not rx.search(line):
                continue
            if why.startswith("a deploy push") and any(f in line.lower() for f in PUSH_FORBIDDEN):
                continue
            # Naming the stand-in on the same line is the honest way to write it.
            if why.startswith('"licensed breeder"') and "LICENCE_CLAIM_PLACEHOLDER" in line:
                continue
            # a comparison topic names both coats without offering either
            # a line that denies the coat is the point of saying it; a "vs" topic names both
            # coats without offering either, unless we/our is on the line
            if why.startswith("a brindle pup") and (
                    re.search(r"(?i)\b(?:none|not|never|no)\b", line)
                    or (re.search(r"(?i)\bvs\b|\bversus\b", line)
                        and not re.search(r"(?i)\b(?:our|we)\b", line))):
                continue
            out.append("%s:%d  %s  |  %s" % (path.name, lineno, why, line.strip()[:110]))
    return out


@pytest.mark.parametrize("path", residue_targets(),
                         ids=lambda p: p.parent.name if p.name == "SKILL.md" else p.stem)
def test_skill_carries_no_source_repo_residue(path):
    bad = residue(path)
    assert bad == [], (
        "source-repo residue in a skill a project-5 builder loads. Re-base the line onto BSUK's "
        "own sources (data/*.json, docs/reference/external-link-library.md) or delete it:\n  "
        + "\n  ".join(bad))


def test_the_residue_lint_actually_fires(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(
        "1. [AVMA](https://www.avma.org/)\n"
        "src=\"https://maps.google.com/maps?q=CITY%2C%20STATE\"\n"
        "BlueStaffyUK ships to [City] airports.\n"
        "## MFS Indexing Report\n"
        "Individual Puppy (Roys, Amie)\n"
        "bounded by the Verified-Claim Ledger\n"
        "Lisa Bright (Carlisle, since 2014)\n"
        "git push origin main\n"
        "## The 22–25 Section Blueprint\n"
        "Middle newsletter is ALWAYS `NewsletterV2`\n"
        "Blue brindle / black brindle (Vennie, Christa, Cheryl — £1,700)\n"
        "> **Site:** BlueStaffyUK — licensed breeder, Carlisle\n"
        "Disclose any paid placement as the FTC requires.\n"
        "| £1,500–£1,700 | fifteen hundred to thirty-five hundred |\n"
        "- **Blue-Brindle variant page:** `blue-brindle staffy for sale`\n"
        "<h3>What \"Licensed Breeder\" Actually Means at BlueStaffyUK</h3>\n"
        "binomial          6 (P. erithacus) 1\n"
        "Every puppy is vet sex-checked before it leaves.\n"
        "PCR screening on both parents.\n"
        "L-2-HGA and Polyomavirus screened\n"
        "certified free of psittacosis\n"
        "an avian vet on call\n"
        "Blue Staffy pups wean at **12–16 weeks**, never sooner.\n"
        "Weaned juvenile: 3-6 months\n"
        "- Action-oriented: \"see our blue and blue brindle Staffy pups\"\n"
        "- `Blue Brindle Staffy for Sale in [UK Region] | Home-Raised, KC Registered`\n"
        "\"Meet [Name]: The Blue Brindle Staffy Perfect for Families.\"\n"
        "Subject: [blue / blue brindle] Staffordshire Bull Terrier puppy\n"
        "- Coat: solid blue-grey (blue), blue brindle striping, or black brindle\n"
        "Specialising in home-raised blue and blue brindle Staffordshire Bull Terriers\n"
        "we've placed Blue Staffy puppies with hundreds of families\n"
        "Only a licenced breeder can sell you one.\n"
        "Lisa Bright will reply within 24 hours.\n"
        "<p class=\"bsuk-form-note\">We respond within a day.</p>\n"
        "Subhead: \"[X] years. [N]+ families. One Carlisle breeder.\"\n"
        "> \"We've placed Blue Staffies with [City] families for [X] years.\"\n"
        "Compare our blue vs blue brindle pups side by side.\n"
        "Subject: a blue brindle staffordshire bull terrier puppy on a sofa\n"
        "Appendix-I puppies are legal to own (CoP17, effective Jan 2017).\n"
        # silent: a line that forbids the push, a UK source, the licence stand-in named on
        # the line, and "blue brindle" as a plain coat word
        "There is no push and no deploy until project 6; never `git push`.\n"
        "Commit it; there is no `git push` until project 6.\n"
        "[PDSA](https://www.pdsa.org.uk/)\n"
        "| LICENCE_CLAIM_PLACEHOLDER-licensed breeder | Trust bar |\n"
        "Coat colours in the breed: blue, blue brindle, red, fawn.\n"
        "C. **Size & Coat** — blue, blue brindle and white coats, full-grown size\n"
        "H3: Blue vs Blue Brindle: Which Coat Colour Is Right for Your Household?\n"
        "- Keyword-rich but natural: \"Staffy vs American Bully comparison\"\n"
        "We reply within 24 to 48 business hours, ourselves.\n"
        "Book a vet visit within 48 hours of collection.\n"
        "Each pup's coat is its own `colour`; none of the six is brindle.\n"
        "Staffies live 12–14 years; [X] years old is a senior dog.\n"
        "A puppy comes home at eight weeks at the earliest, fully weaned.\n", encoding="utf-8")
    bad = residue(p)
    # every line up to 39 fires (a line may fire twice), nothing after it does, and every
    # entry of RESIDUE fired at least once
    assert sorted({int(b.split("  ")[0].split(":")[1]) for b in bad}) == list(range(1, 40)), bad
    assert {b.split("  ")[1] for b in bad} == {why for why, _ in RESIDUE}, bad


# ── the guarantee is gated on its setting, in every skill (Task 12 final round) ─────
# data/settings.json `guarantee_days` holds the length (two years, answer board q07,
# 2026-09-29) and `guarantee_label` its words, so a skill that tells a builder to write
# "guarantee" must name the setting that gates it — the SEO checklist's rule (tests/py/test_builder_skills.py), in every skill and
# command. A line about a competitor's guarantee ("their") or the source repo's is not ours.
GUARANTEE = re.compile(r"(?i)guarantee")
# "their" counts only when it owns the guarantee: within six words before it
NOT_OURS = re.compile(r"(?i)\btheir\b(?:\W+\w+){0,6}?\W+guarantee|source repo")


def ungated_guarantees(path: pathlib.Path):
    return ["%s:%d  %s" % (path.name, n, line.strip()[:110])
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
            if GUARANTEE.search(line) and "guarantee_days" not in line and not NOT_OURS.search(line)]


@pytest.mark.parametrize("path", residue_targets(),
                         ids=lambda p: p.parent.name if p.name == "SKILL.md" else p.stem)
def test_every_guarantee_line_names_guarantee_days(path):
    bad = ungated_guarantees(path)
    assert bad == [], (
        "a guarantee with no `guarantee_days` on the line. data/settings.json has it null, so "
        "name the setting that gates the line, or drop the guarantee:\n  " + "\n  ".join(bad))


# The agents are gated the same way (Task 18 follow-up, 2026-09-24): an agent is loaded
# into a session exactly as a skill is, and its guarantee lines reach the page first.
@pytest.mark.parametrize("path", sorted((ROOT / ".claude/agents").glob("bsuk-*.md")), ids=lambda p: p.stem)
def test_every_agent_guarantee_line_names_guarantee_days(path):
    bad = ungated_guarantees(path)
    assert bad == [], (
        "a guarantee with no `guarantee_days` on the line. data/settings.json has it null, so "
        "name the setting that gates the line, or drop the guarantee:\n  " + "\n  ".join(bad))


def test_the_guarantee_gate_actually_fires(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(
        "Health guarantee + KC registration included.\n"
        "## Section 21: Health Guarantee Detail\n"
        "`GUARANTEED_FOR` | 72-hour\n"
        # silent: gated on the setting, a competitor's, the source repo's
        "A guarantee is named only when `guarantee_days` in data/settings.json is set.\n"
        "Their \"lifetime guarantee\" has no terms.\n"
        "The source repo's 72-hour guarantee.\n"
        # fires: "their" that does not own the guarantee is no excuse
        "Every puppy has a health guarantee, and their paperwork is in order.\n", encoding="utf-8")
    assert [b.split("  ")[0] for b in ungated_guarantees(p)] == [
        "SKILL.md:1", "SKILL.md:2", "SKILL.md:3", "SKILL.md:7"]


# ── an invented house-method label (CAG parity audit D1, 2026-09-26) ─────
# BSUK has no named house method: Lisa Bright has never given one, CLAUDE.md rule 9 forbids
# inventing a credential, and scripts/aeo_audit.py keeps LABELED_METHODS empty. The source
# repo's rule 12 required two "brand-owned method labels", and the port left one invented
# label ("The Carlisle Socialization Method"), a second invented one in the manual auditor
# ("the BSUK Home-Raised Method") and the requirement itself in the AEO pass, the entity
# graph and the Sprint 3 gate of WORKFLOW.md. An agent that follows any of them prints a
# made-up credential on every page it builds. This lint reads the whole instruction tree:
# agents, skills, the reference docs, the rule packs and CLAUDE.md.
METHOD_LABEL = re.compile(
    r"(?i:\bsociali[sz]ation method\b|\bhome-raised method\b|\bapproved method (?:labels?|names?)\b"
    r"|\bapproved labels?\b|\bbrand-owned method (?:labels?|names?|nodes?)\b)"
    r"|\b(?:Carlisle|BSUK|BlueStaffyUK|Blue Staff(?:y|ies)|Lisa|Bright)\b[^|\n.]{0,40}?"
    r"\b(?:Method|Protocol|Programme|Program)\b")


def method_label_targets():
    return (targets() + sorted((ROOT / ".claude/skills").glob("*/references/*.md"))
            + sorted((ROOT / "rules").glob("*.md")) + [ROOT / "CLAUDE.md"])


def method_labels(path: pathlib.Path):
    return ["%s:%d  %s" % (path.name, n, line.strip()[:110])
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
            if METHOD_LABEL.search(line)]


@pytest.mark.parametrize("path", method_label_targets(), ids=lambda p: p.parent.name + "/" + p.name)
def test_no_instruction_file_names_or_requires_a_house_method(path):
    bad = method_labels(path)
    assert bad == [], (
        "BSUK has no named house method — the breeder has never given one and CLAUDE.md rule 9 "
        "forbids inventing it. Delete the label and any line that requires one; if the breeder "
        "names a method, it goes in scripts/aeo_audit.py LABELED_METHODS first:\n  "
        + "\n  ".join(bad))


def test_the_method_label_lint_actually_fires(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(
        "| **The Carlisle Socialization Method** | family handling |\n"
        "Named house method (\"the BSUK Home-Raised Method\") used where home-rearing is discussed\n"
        "- [ ] One of the two approved method labels present and defined\n"
        "| 6a Labeled | one of the two approved method names present | yes |\n"
        "are first-class entities and the only two approved labels.\n"
        "  → WARN:  no binomial · no breeder-name entity · no brand-owned method label\n"
        "Lisa Bright's Puppy Method is taught on every page.\n"
        "Every litter follows The BSUK Puppy Protocol from day one.\n"
        "The Blue Staffy Rearing Programme starts at three weeks.\n"
        # silent: a named framework, a research step, the rule that forbids a label, and a
        # sentence break between a name and the word Method
        "**Two-Keyword Header Method (apply to every header):**\n"
        "### 3. Tiered Sprint 0.5 Research Method + 17-Field Output Format\n"
        "BSUK has no named house method; never invent one.\n"
        "Lisa Bright, our breeder. Method: we weigh daily.\n", encoding="utf-8")
    assert [b.split("  ")[0] for b in method_labels(p)] == [
        "SKILL.md:%d" % n for n in range(1, 10)]


# ── the guarantee is two years (answer board q07, 2026-09-29) ─────────────────────────
# The breeder's answer replaced the NOT FETCHED length: data/settings.json holds
# `guarantee_days: 730`. No instruction may still tell a builder the length is unset, null or
# not established; each guarantee line still names `guarantee_days` (the gate above), because
# the setting stays the only place the length is written. History (the session log, the
# answer board's own files, plans and specs) records what was true then and is not scanned.
UNSET_GUARANTEE = re.compile(
    r"(?i)guarantee_days`?:?\s*null|guarantee_days`?(?:\s+in\s+`?data/settings\.json`?)?\s*(?:is|,)\s*null"
    r"|null today|guarantee[^.;|]{0,40}(?:NOT FETCHED|not established)|(?:NOT FETCHED|not established)[^.;|]{0,20}guarantee"
    r"|no guarantee (?:is )?(?:stated|claimed|offered|while)|none stated")


def unset_guarantee_lines(path: pathlib.Path):
    return ["%s:%d  %s" % (path.name, n, line.strip()[:120])
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
            if GUARANTEE.search(line) and UNSET_GUARANTEE.search(line) and not NOT_OURS.search(line)]


def instruction_files():
    files = [ROOT / "CLAUDE.md", *sorted((ROOT / "rules").glob("*.md")),
             *sorted((ROOT / ".claude/agents").glob("*.md")),
             *sorted((ROOT / ".claude/skills").glob("*/SKILL.md")),
             *sorted(p for p in (ROOT / "docs/reference").glob("*.md") if p.name != "session-log.md")]
    return [f for f in files if f.exists()]


def test_the_guarantee_setting_holds_the_breeders_answer():
    settings = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
    assert settings["guarantee_days"] == 730
    assert settings["guarantee_label"] == "Two-year health guarantee"


def test_no_instruction_still_calls_the_guarantee_unset():
    bad = [b for f in instruction_files() for b in unset_guarantee_lines(f)]
    assert bad == [], (
        "the guarantee is two years (data/settings.json guarantee_days: 730, answer board q07, "
        "2026-09-29); these lines still call it unset:\n  " + "\n  ".join(bad))


def test_the_unset_guarantee_scan_fires(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("The guarantee length is NOT FETCHED (`guarantee_days: null`).\n"
                 "a guarantee only when `guarantee_days` is set (null today)\n"
                 "The guarantee is `guarantee_days` (730 days, two years).\n"
                 "Their guarantee is not established.\n", encoding="utf-8")
    assert [b.split("  ")[0] for b in unset_guarantee_lines(p)] == ["x.md:1", "x.md:2"]


# The length lives in data/settings.json (and CLAUDE.md's Brand context line may state it):
# an instruction that types it is a second copy that drifts the day the breeder changes it
# (Task 10b review, item 6). Point at `guarantee_label` instead.
TYPED_LENGTH = re.compile(r"(?i)\b730\b|\b(?:two|2)[- ]years?\b|\b24[- ]months?\b|\b104 weeks\b")


def typed_guarantee_lengths(path: pathlib.Path):
    """A guarantee line that types the length on it, or on the line after it (a length wrapped
    onto the next line is the same copy)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for n, line in enumerate(lines, 1):
        if not GUARANTEE.search(line) or NOT_OURS.search(line):
            continue
        nxt = lines[n] if n < len(lines) else ""
        nxt = "" if GUARANTEE.search(nxt) else nxt  # a guarantee line is judged on its own
        if TYPED_LENGTH.search(line) or TYPED_LENGTH.search(nxt):
            out.append("%s:%d  %s" % (path.name, n, line.strip()[:120]))
    return out


def test_no_instruction_but_claude_md_types_the_guarantee_length():
    bad = [b for f in instruction_files() if f.name != "CLAUDE.md" for b in typed_guarantee_lengths(f)]
    assert bad == [], (
        "the guarantee's length is typed; say \"the guarantee is `guarantee_label` in "
        "data/settings.json; read it, never type it\" instead:\n  " + "\n  ".join(bad))


def test_the_typed_length_scan_fires(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("The guarantee is `guarantee_days` (730 days).\n"
                 "A two-year guarantee, read from `guarantee_days`.\n"
                 "The guarantee is `guarantee_label` in data/settings.json; read it, never type it.\n"
                 "Their two-year guarantee has no terms.\n"
                 "A 2-year guarantee.\n"
                 "The guarantee runs 24 months.\n"
                 "The health guarantee lasts\n"
                 "two years from collection.\n"
                 "Nothing here.\n", encoding="utf-8")
    assert [b.split("  ")[0] for b in typed_guarantee_lengths(p)] == ["x.md:1", "x.md:2", "x.md:5", "x.md:6", "x.md:7"]
