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
BANNED = (
    "40–60", "40-60", "50 cities", "50 states",
    "captive", "USDA", "APHIS", "CITES", "Cloudflare", "cloudflare",
)

# DEFRA is real here in exactly one form: the transport that carries a puppy. "DEFRA-approved
# breeder" / "DEFRA-compliant kennel" are claims nobody has verified.
DEFRA = re.compile(r"DEFRA", re.I)

# A number of years that is not the breed's. Windowed rather than regexed tightly because the
# claim shows up as "40-60 yrs", "lifetime (50 years)", "60 year commitment" and "12+ years".
YEARS = re.compile(r"(?i)\b(years?|yrs?)\b")
# A digit glued to letters is an identifier (`h3`, `70de`, `G-M...`), not a quantity.
NUMBER = re.compile(r"(?<![A-Za-z0-9-])\d+(?![A-Za-z0-9])")
ALLOWED_YEARS = {"12", "13", "14"}
# "first-year cost", "year 1 total": a budgeting horizon, not a claim about how long the dog
# lives. Narrow on purpose — only the literal ordinal-first-year phrasings, and only the
# digit 1.
FIRST_YEAR = re.compile(r"(?i)(first[- ]year|year[- ]1\b|year 1\b|1st[- ]year)")

HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
FENCE = re.compile(r"^\s{0,3}```")
# A route or URL path: a placeholder is a claim-shaped word, not a path segment. The one
# sanctioned exception is `https://SITE_URL_PLACEHOLDER/...`, where the placeholder stands in
# the HOST position for the domain project 6 will register — that is the repo-wide convention
# (`CLAUDE.md`, `rules/`), not a claim. A placeholder in a path SEGMENT still fails.
ROUTE = re.compile(r"(?<!/)/[A-Za-z0-9_<>\[\]-]*(?:" + "|".join(PLACEHOLDERS)
                   + r")[A-Za-z0-9_<>\[\]-]*/?")


def targets():
    return (sorted((ROOT / ".claude/agents").glob("*.md"))
            + sorted((ROOT / ".claude/skills").glob("**/SKILL.md")))


def _norm(m):
    return re.sub(r"\s*[–—-]\s*", "–", m.strip())


def violations(path: pathlib.Path):
    out, fenced = [], False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(line):
            fenced = not fenced
        def bad(why):
            out.append("%s:%d  %s  |  %s" % (path.name, lineno, why, line.strip()[:120]))

        for m in MONEY.findall(line):
            if _norm(m) not in ALLOWED_MONEY:
                bad("unlocked amount %s (locked: %s)" % (_norm(m), ", ".join(sorted(ALLOWED_MONEY))))

        for tok in BANNED:
            if tok in line:
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
                if num not in ALLOWED_YEARS:
                    bad("year figure %r near %r (the breed figure is 12–14)" % (num, ym.group(0)))

        if HEADING.match(line) and not fenced:
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
    p.write_text("Lifetime estimate (40-60 yrs) £85,000–£250,000 from captive DEFRA-compliant breeders\n"
                 "## LICENCE_CLAIM_PLACEHOLDER Writing Rules\n", encoding="utf-8")
    kinds = violations(p)
    assert any("unlocked amount" in v for v in kinds), kinds
    assert any("banned token" in v for v in kinds), kinds
    assert any("DEFRA asserted" in v for v in kinds), kinds
    assert any("year figure" in v for v in kinds), kinds
    assert any("used as a noun in a heading" in v for v in kinds), kinds
