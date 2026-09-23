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

# `Glasgow` has exactly two honest uses left in the instruction tree, and a line carrying
# one of them is allowed to name the city: the outreach page's slug, which is a URL that
# still ranks and is never renamed, and the debt note itself, which cannot be written
# without saying what the debt is. Nothing else — a trust pillar, a meta template, a
# delivery table — may say it.
GLASGOW_ALLOWED = re.compile(r"staffy-breeding-dogs-glasgow|Known Issue 16")

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
