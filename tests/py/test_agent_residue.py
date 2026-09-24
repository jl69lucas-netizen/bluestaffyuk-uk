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
    "CITES paperwork": r"\bpermits?\b|appendix i\b|bsukcitesstep|cites-",
    "fabricated figures": r"\b\d[\d,]*\+? (?:happy )?families\b|blue-brindle|health guaranteed",
}
FLAGS = {k: re.compile(v, re.I if k not in ("source people and brands",) else 0)
         for k, v in RESIDUE.items()}
FORMER_CITY = re.compile(r"glasgow", re.I)
CITY_OK = re.compile(r"staffy-breeding-dogs-glasgow|staffy-puppies-for-sale-glasgow|Known Issue 16")


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


def test_the_scan_fires_on_each_kind_and_spares_bsuk_facts():
    for text in ("weigh 400–650g as adults", "verifiable at usfws.gov", "home-raised permit",
                 "Teri's first week", "2,000+ families", "\"addressCountry\": \"US\""):
        assert residue(text), text
    for text in ("£1,500 (Roman, Byrd, Ince)", "collection in Carlisle, Cumbria",
                 "DEFRA-approved transport", "L-2-HGA and HC-HSF4", "https://www.gov.uk/x",
                 r"pmc\.ncbi\.nlm\.nih\.gov", "pmc.ncbi.nlm.nih.gov", r"www\.gov\.uk",
                 "the breed's 12–14 years", "Title Case on every heading"):
        assert residue(text) == [], text
