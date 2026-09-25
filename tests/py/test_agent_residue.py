"""No agent still carries the source repo's species, country or paperwork.

`scripts/marker_check.py` bans twelve markers line by line, and `tests/py/test_agent_facts.py`
bans the claims BSUK cannot back. The project-5 readiness audit (2026-09-23) found residue that
both miss, because it was re-based word by word into sentences that no longer mean anything:

- parrot facts written about a dog — adult weights in grams, a "scarlet" or "maroon" tail,
  "charcoal plumage", "equatorial forest", talking, mimicry, a 40-year commitment turned into
  "will outlive you", wild-capture and conservation;
- the source breeder's people and birds (`Teri`, `Maxy`, a puppy called `Harlow`) and its
  other brand (`MFS`, `TAG`);
- US regulators, payment apps, states, cities and a US phone prefix (`usfws.gov`, `aphis`,
  `Zelle`, `CBP`, `Dallas`, `402-696`, `"addressCountry": "US"`);
- CITES paperwork re-based into "a LICENCE_CLAIM_PLACEHOLDER home-raised permit" — a UK puppy
  has no permit, so every sentence built on one is empty;
- a marker split across a line break (`African` / `Greys` in the PAA agent), which a
  line-scoped gate can never see — so this scan reads each file as ONE string.

The former city is allowed only where the fact lint allows it — the outreach page's slug and
the Known Issue 16 note — plus the live location row's own slug, which is lowercase and so
escaped that lint.
"""
import pathlib
import re

import pytest

from test_agent_facts import GLASGOW_ALLOWED  # noqa: E402 — one list of the city's honest uses

ROOT = pathlib.Path(__file__).resolve().parents[2]
AGENTS = sorted((ROOT / ".claude/agents").glob("bsuk-*.md"))

RESIDUE = {
    "parrot": r"african[\s-]+gr[ae]ys?|plumage|tail fan|\bfeathers?\b|\bbeaks?\b|equatorial"
              r"|talk back|grudges|outlive your|\bmaroon\b|\bscarlet\b|red-tipped|\bmimics?\b"
              r"|vocabular(?:y|ies) of \d|wild-capture|\bconservation\b|cockatiel|vs[- ]amazon"
              r"|puppies talk\b|talk is cheap|\beggs?\b|bird_inquiry|birdsnow|🦜"
              r"|\b\d{3}\s*[–-]\s*\d{3}\s*g\b",
    "source people and brands": r"\bTeri\b|\bMaxy\b|\bHarlow\b|\bMFS\b|\bTAG\b",
    "US": r"usfws|\baphis\b|zelle|cashapp|\bCBP\b|wire fraud|fish (?:&|&amp;|and) wildlife"
          r"|\bfederal\b|\binterstate\b|usa-locations|\bin the US\b|\"US\"|BREEDER_STATE"
          r"|states_found|\bDallas\b|\bMiami\b|\bOrlando\b|402[-.)]\s?696|\(402\)"
          r"|\b\d\d:\d\d Central\b|\$\[price\]|(?<!nih)(?<!nih\\)\.gov\b(?!\\?\.uk)",
    # the noun only: "a/the/home-raised permit", "permit number" — never the verb ("the rule permits one H1")
    "CITES paperwork": r"\b(?:an?|the|home-raised|CITES|LICENCE_CLAIM_PLACEHOLDER|export|import)\s+permits?\b"
                       r"|\bpermits?\s+(?:numbers?|#|verification|lookup)|\bappendix[\s-]i\b|\bCoP ?17\b"
                       r"|bsukcitesstep|cites-",
    "fabricated figures": r"\b\d[\d,]*\+? (?:happy )?families\b|blue-brindle|health guaranteed",
}
FLAGS = {k: re.compile(v, re.I if k not in ("source people and brands",) else 0)
         for k, v in RESIDUE.items()}
FORMER_CITY = re.compile(r"glasgow", re.I)
CITY_OK = GLASGOW_ALLOWED


def residue(text):
    """[(kind, match)] over the whole file, whitespace-collapsed so a wrapped term is seen."""
    flat = re.sub(r"\s+", " ", text)
    return [(k, m.group(0)) for k, rx in FLAGS.items() for m in rx.finditer(flat)]


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_no_agent_carries_source_repo_residue(agent):
    hits = residue(agent.read_text(encoding="utf-8"))
    assert hits == [], (f"{agent.name} still carries the source repo's species, country or "
                        "paperwork — rewrite the sentence for a UK Staffy breeder or delete it:"
                        "\n  " + "\n  ".join(f"{k}: {m!r}" for k, m in hits))


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_the_former_city_appears_only_where_the_fact_lint_allows_it(agent):
    bad = [f"{agent.name}:{n}  {l.strip()[:120]}"
           for n, l in enumerate(agent.read_text(encoding="utf-8").splitlines(), 1)
           if FORMER_CITY.search(l) and not CITY_OK.search(l)]
    assert bad == [], ("the breeder is in Carlisle, Cumbria (Known Issue 16); the old city may "
                       "appear only as a live slug or in the debt note:\n  " + "\n  ".join(bad))


# A fact BSUK HAS is not a placeholder. `[BREEDER_NAME]` is Lisa Bright and `[BREEDER_LOCATION]`
# is Carlisle, Cumbria (CLAUDE.md, data/settings.json); a template that still asks for them
# reads as if the fact were unknown, and a builder fills the gap by guessing. Placeholders for
# facts that ARE unknown (`[DURATION_TBD]`, `LICENCE_CLAIM_PLACEHOLDER`) are correct and stay.
KNOWN_FACT_PLACEHOLDER = re.compile(r"\[BREEDER_(?:NAME|LOCATION|CITY|STATE)\]")


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_no_agent_leaves_a_known_fact_as_a_placeholder(agent):
    bad = [f"{agent.name}:{n}  {m}"
           for n, l in enumerate(agent.read_text(encoding="utf-8").splitlines(), 1)
           for m in KNOWN_FACT_PLACEHOLDER.findall(l)]
    assert bad == [], ("the breeder is Lisa Bright, in Carlisle, Cumbria — write the fact:\n  "
                       + "\n  ".join(bad))


def test_the_scan_sees_a_marker_split_across_lines():
    assert residue("Blue Staffy African \nGreys are the best mimics")[:1] == [
        ("parrot", "African Greys")]


@pytest.mark.parametrize("text", ["legal to own (CoP17, effective Jan 2017)", "under CoP 17", "Appendix-I puppies",
                                  "an appendix I species"])
def test_the_scan_catches_the_cites_listing_in_every_spelling(text):
    # the skills' CITES guard (tests/py/test_agent_facts.py) reads CoP17 and Appendix-I; so does this one
    assert [k for k, _ in residue(text)] == ["CITES paperwork"], text


def test_the_scan_fires_on_each_kind_and_spares_bsuk_facts():
    for text in ("weigh 400–650g as adults", "verifiable at usfws.gov", "home-raised permit",
                 "Teri's first week", "2,000+ families", "\"addressCountry\": \"US\""):
        assert residue(text), text
    for text in ("£1,500 (Roman, Byrd, Ince)", "collection in Carlisle, Cumbria",
                 "DEFRA-approved transport", "L-2-HGA and HC-HSF4", "https://www.gov.uk/x",
                 r"pmc\.ncbi\.nlm\.nih\.gov", "pmc.ncbi.nlm.nih.gov", r"www\.gov\.uk",
                 "the breed's 12–14 years", "Title Case on every heading", "the rule permits one H1"):
        assert residue(text) == [], text


# Health and guarantee wording has ONE authority: the evidence ledger. data/faq.json repeats
# the migrated site's "certified clear of L-2-HGA and HC-HSF4" and a "written health guarantee",
# but `data/quality/evidence-ledger.json` holds `parents-dna-clear` at NOT FETCHED and
# `data/settings.json` `guarantee_days` is null. So an agent line that sends a builder to
# data/faq.json for health or guarantee wording must also name the evidence ledger, or the
# builder copies an unproven claim word for word. (Naming the puppy-package items — a vet
# health check, a microchip — is not health-result wording and passes.)
FAQ = re.compile(r"faq\.json")
HEALTH_WORDING = re.compile(r"\bhealth (?:claims?|wording|tests?|testing|results?|clearances?)\b"
                            r"|\bguarantee|\bDNA\b|\bclear of\b|\bwords it\b", re.I)
LEDGER = re.compile(r"evidence[- ]ledger")


def faq_health_pointers(text):
    return [n for n, l in enumerate(text.splitlines(), 1)
            if FAQ.search(l) and HEALTH_WORDING.search(l) and not LEDGER.search(l)]


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_a_faq_pointer_for_health_or_guarantee_wording_names_the_evidence_ledger(agent):
    bad = faq_health_pointers(agent.read_text(encoding="utf-8"))
    assert bad == [], (f"{agent.name} lines {bad} send a builder to data/faq.json for health or "
                       "guarantee wording without data/quality/evidence-ledger.json — faq.json "
                       "repeats unproven clearances and a guarantee; name the ledger's rule")


# The paperwork that goes home with a puppy is KNOWN (data/faq.json `whyus-paperwork`: Kennel
# Club registration paperwork, vaccination records, microchipping details, a written purchase
# contract; `puppy-package`: vaccinations, microchip, vet health check). Writing one of those
# as LICENCE_CLAIM_PLACEHOLDER teaches a builder to hide a fact BSUK has; the placeholder is
# for a licence claim only.
PAPERWORK_AS_PLACEHOLDER = re.compile(
    r"(?:microchip(?:ping)?(?: registration| number| details)?|vet (?:health )?cert(?:ificate)?"
    r"|vet health check|vaccination records?|KC registration|Kennel Club registration|paperwork)"
    r"\s*[,(]?\s*LICENCE_CLAIM_PLACEHOLDER", re.I)


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_no_agent_writes_known_paperwork_as_a_licence_placeholder(agent):
    bad = [f"{agent.name}:{n}  {m.group(0)}"
           for n, l in enumerate(agent.read_text(encoding="utf-8").splitlines(), 1)
           for m in PAPERWORK_AS_PLACEHOLDER.finditer(l)]
    assert bad == [], ("the paperwork is named in data/faq.json whyus-paperwork — write the "
                       "document; LICENCE_CLAIM_PLACEHOLDER is for a licence claim only:\n  "
                       + "\n  ".join(bad))


# The skills and slash commands teach the same builders, so the same guard reads them
# (review minors, 2026-09-24: framework-ebp wrote "paperwork (LICENCE_CLAIM_PLACEHOLDER)").
SKILLS_AND_COMMANDS = (sorted((ROOT / ".claude/skills").glob("*/SKILL.md"))
                       + sorted((ROOT / ".claude/commands").rglob("*.md")))


@pytest.mark.parametrize("path", SKILLS_AND_COMMANDS,
                         ids=lambda p: p.parent.name if p.name == "SKILL.md" else p.stem)
def test_no_skill_or_command_writes_known_paperwork_as_a_licence_placeholder(path):
    bad = [f"{path.relative_to(ROOT)}:{n}  {m.group(0)}"
           for n, l in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
           for m in PAPERWORK_AS_PLACEHOLDER.finditer(l)]
    assert bad == [], ("the paperwork is named in data/faq.json whyus-paperwork — write the "
                       "document; LICENCE_CLAIM_PLACEHOLDER is for a licence claim only:\n  "
                       + "\n  ".join(bad))


def test_the_health_pointer_and_paperwork_guards_fire_and_spare():
    assert faq_health_pointers("a health claim only as `data/faq.json` words it")
    assert faq_health_pointers("the guarantee from data/faq.json")
    assert not faq_health_pointers("a health claim only where data/quality/evidence-ledger.json "
                                   "holds its proof; the data/faq.json puppy-package items")
    assert not faq_health_pointers("included, per data/faq.json puppy-package: vet health check")
    assert PAPERWORK_AS_PLACEHOLDER.search("microchip registration LICENCE_CLAIM_PLACEHOLDER")
    assert PAPERWORK_AS_PLACEHOLDER.search("vet health check LICENCE_CLAIM_PLACEHOLDER")
    assert not PAPERWORK_AS_PLACEHOLDER.search("a licence number stays LICENCE_CLAIM_PLACEHOLDER")
    # "the breeder's paperwork (LICENCE_CLAIM_PLACEHOLDER)" hides the four named documents
    assert PAPERWORK_AS_PLACEHOLDER.search("build trust around the breeder's paperwork (LICENCE_CLAIM_PLACEHOLDER)")
    assert not PAPERWORK_AS_PLACEHOLDER.search("the paperwork (data/faq.json whyus-paperwork); the "
                                               "licence stays LICENCE_CLAIM_PLACEHOLDER")


# The "Trust pillars" banner line (Task 18 follow-up, 2026-09-24). It used to file the
# paperwork under LICENCE_CLAIM_PLACEHOLDER with the health and licence claims, which is the
# same hiding the paperwork guard above forbids, one line higher in every agent.
PILLAR_PAPERWORK = "paperwork or licence claim is LICENCE_CLAIM_PLACEHOLDER"


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_no_trust_pillars_line_files_the_paperwork_as_a_licence_placeholder(agent):
    text = agent.read_text(encoding="utf-8")
    assert PILLAR_PAPERWORK not in text, (
        f"{agent.name}: the paperwork is named as data/faq.json whyus-paperwork has it; only a "
        "health or licence claim waits on LICENCE_CLAIM_PLACEHOLDER")


# Every agent's rules banner ("Bound by the site rules, not by a copy of them") names the
# working rules 10-17 as well as the nine judgment rules: a banner that lists nine rules
# reads as the whole set, and the eight working rules are the ones a builder breaks first
# (a board without every link, a reused image moved, a shared hero, a page not written from
# its outline). Rule 17 arrived with the system-gaps build.
BANNER = "Bound by the site rules, not by a copy of them"


@pytest.mark.parametrize("agent", AGENTS, ids=lambda p: p.stem)
def test_every_rules_banner_names_working_rules_10_to_17(agent):
    banner = [l for l in agent.read_text(encoding="utf-8").splitlines() if BANNER in l]
    assert banner, f"{agent.name} has no rules banner"
    assert all("working rules 10–17" in l for l in banner), (
        f"{agent.name}: the rules banner names only the judgment rules — add CLAUDE.md's "
        "working rules 10–17 by their short names")
