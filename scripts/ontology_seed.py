#!/usr/bin/env python3
"""ontology_seed.py [--check]

Grows data/bsuk-ontology.json from the repo's own sourced data, so a board can name the
people, places, organisations, regulations and health tests a page talks about and the
board can group them by class. Four inputs, and nothing else:

  Place         data/locations.json — every city row (the country-wide `UK` rows are not a
                place a page is about), plus the breeder's town and region from
                data/settings.json. ASSERTED: the file is the source.
  Organization  docs/reference/external-link-library.md — the organisation behind each host
                in the Rows table. ASSERTED: every row was checked for a 200 before it was
                added. A host with no entry in HOST_ORG and not in SKIP_HOSTS stops the run,
                so a new library row forces a decision instead of vanishing.
  Regulation    the same Rows table — a row whose "What it is" names a law or official rule.
                ASSERTED as a thing a page may NAME and link. A claim that BlueStaffyUK holds
                a licence or complies with a statute is not an entity and stays
                LEGAL_CLAIM_PLACEHOLDER under CLAUDE.md rule 9.
  Health        data/quality/evidence-ledger.json — the tests its own comment names. A test
                is ASSERTED only when a ledger claim matching it has a proof object (not
                NOT FETCHED) and a breeder confirmation date. Otherwise it is PROPOSED with
                source null — null, not the ledger path, because board_approve.py promotes a
                PROPOSED entity that has a source to ASSERTED the moment a board using it is
                approved, and an unconfirmed result must never be promoted that way.
  People        data/settings.json `breeder_name`.

Idempotent. An entity already in the file is never rewritten — its authorization, source
and owner page may have been decided by an approval since — and new entities are appended
in class order, then id order, so a re-run with unchanged inputs writes the same bytes.

  --check   exit 1 when the file on disk is not what a seed run would write (nothing written).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pageboard as PB  # noqa: E402

LOCATIONS = PB.ROOT / "data" / "locations.json"
SETTINGS = PB.ROOT / "data" / "settings.json"
LEDGER = PB.ROOT / "data" / "quality" / "evidence-ledger.json"

CLASS_ORDER = ("People", "Place", "Health", "Organization", "Regulation", "Organism",
               "Commerce", "Logistics", "Documentation", "Method")

# host -> (id, name, aliases). The name is the one the library's own row text uses.
HOST_ORG = {
    "ico.org.uk": ("ont:ico", "Information Commissioner's Office", ["ICO"]),
    "gov.uk": ("ont:uk-government", "UK government", ["GOV.UK", "the government"]),
    "assets.publishing.service.gov.uk": ("ont:uk-government", "UK government", ["GOV.UK", "the government"]),
    "citizensadvice.org.uk": ("ont:citizens-advice", "Citizens Advice", []),
    "policies.google.com": ("ont:google", "Google", ["Google Analytics"]),
    "thekennelclub.org.uk": ("ont:the-kennel-club", "The Kennel Club", ["Royal Kennel Club", "KC"]),
    "royalkennelclub.com": ("ont:the-kennel-club", "The Kennel Club", ["Royal Kennel Club", "KC"]),
    "rspca.org.uk": ("ont:rspca", "RSPCA", []),
    "bva.co.uk": ("ont:bva", "British Veterinary Association", ["BVA"]),
    "pdsa.org.uk": ("ont:pdsa", "PDSA", []),
    "bluecross.org.uk": ("ont:blue-cross", "Blue Cross", ["The Blue Cross"]),
}
# Hosts that are in the library but are not an organisation a page is about.
SKIP_HOSTS = {
    "crufts.org.uk": "a dog show (an event), not an organisation; its organiser is already The Kennel Club",
}

# normalised URL -> (id, name, aliases). Only rows whose own text names a law or official rule.
REGULATION_ROWS = {
    "https://gov.uk/control-dog-public/banned-dogs":
        ("ont:dangerous-dogs-act-1991", "Dangerous Dogs Act 1991", ["banned dog types"]),
    "https://gov.uk/get-your-dog-cat-microchipped":
        ("ont:dog-microchipping-law", "Dog microchipping law", ["microchipping law", "compulsory microchipping"]),
    "https://gov.uk/data-protection":
        ("ont:uk-data-protection-law", "UK data protection law", ["data protection"]),
    "https://gov.uk/bring-pet-to-great-britain":
        ("ont:pet-travel-rules-gb", "Rules for bringing a pet into Great Britain", ["pet travel rules"]),
    "https://assets.publishing.service.gov.uk/media/5a819d3bed915d74e623335d/pb10308-dogs-cats-welfare-060215.pdf":
        ("ont:welfare-in-transport-pb10308", "Welfare in transport guidance for dogs and cats (PB10308)",
         ["PB10308", "welfare-in-transport guidance"]),
}

# The tests the evidence ledger's own comment names. `match` is what a ledger claim's
# `pattern` must find in the name for the claim to count as this test's certificate.
HEALTH_TESTS = (
    ("ont:l-2-hga-dna-test", "L-2-HGA DNA test", ["L2-HGA", "L-2-HGA"], "L-2-HGA DNA test"),
    ("ont:hc-hsf4-dna-test", "HC-HSF4 DNA test", ["HC-HSF4", "hereditary cataract DNA test"], "HC-HSF4 DNA test"),
    ("ont:phpv-test", "PHPV test", ["PHPV"], "PHPV test"),
    ("ont:bva-kc-eye-scheme", "BVA/KC eye scheme", ["BVA eye scheme", "eye screening"], "BVA/KC eye scheme"),
    ("ont:bva-hip-elbow-scores", "BVA hip and elbow scores", ["hip score", "elbow score"], "BVA hip and elbow scores"),
)

ROW = re.compile(r"^\|\s*(https?://[^\s|]+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$")


def slug_id(text):
    return "ont:" + re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def page_slug(first_page):
    """`/blue-staffy-health-uk/` (as the library writes it, in backticks) -> the board slug."""
    p = first_page.strip().strip("`").strip("/")
    return p or "index"


def library_rows(path=None):
    """(url, host, what, first_page) for every row of the Rows table, in file order."""
    p = Path(path or PB.EXTERNAL_LIBRARY)
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m:
            out.append((m.group(1), m.group(2).strip(), m.group(3).strip(), page_slug(m.group(4))))
    if not out:
        raise PB.BoardError(f"{p}: no Rows-table lines parsed — the table changed shape")
    return out


def place_entities(locations, settings):
    out = {}
    for r in locations:
        city = re.sub(r"\s*\(.*?\)\s*", "", r.get("city", "")).strip()
        if not city or city.upper() == "UK":
            continue
        eid = slug_id(city)
        if eid not in out:
            out[eid] = {"id": eid, "name": city, "aliases": [], "class": "Place",
                        "authorization": "ASSERTED", "source": "data/locations.json",
                        "owner_page": "uk-locations/" + r["slug"]}
    addr = settings.get("address") or {}
    for key in ("city", "region"):
        name = addr.get(key)
        if name and slug_id(name) not in out:
            out[slug_id(name)] = {"id": slug_id(name), "name": name, "aliases": [], "class": "Place",
                                  "authorization": "ASSERTED", "source": "data/settings.json",
                                  "owner_page": None}
    return list(out.values())


def library_entities(rows):
    orgs, regs = {}, {}
    # owner_page stays null: the first page to LINK an organisation or a law is not the page
    # that OWNS it, and the ownership map is bsuk-entity-graph's §4b job, not a seed's guess.
    for url, host, _what, _first in rows:
        h = host.lower()
        if h.startswith("www."):
            h = h[4:]
        if h in HOST_ORG:
            eid, name, aliases = HOST_ORG[h]
            orgs.setdefault(eid, {"id": eid, "name": name, "aliases": list(aliases), "class": "Organization",
                                  "authorization": "ASSERTED",
                                  "source": "docs/reference/external-link-library.md", "owner_page": None})
        elif h not in SKIP_HOSTS:
            raise PB.BoardError(f"external-link-library host {host!r} has no organisation in "
                                "ontology_seed.HOST_ORG and is not in SKIP_HOSTS — decide which")
        reg = REGULATION_ROWS.get(PB.normalise_url(url))
        if reg:
            eid, name, aliases = reg
            regs.setdefault(eid, {"id": eid, "name": name, "aliases": list(aliases), "class": "Regulation",
                                  "authorization": "ASSERTED",
                                  "source": "docs/reference/external-link-library.md", "owner_page": None})
    missing = sorted(set(u for u in REGULATION_ROWS) - {PB.normalise_url(r[0]) for r in rows})
    if missing:
        raise PB.BoardError(f"REGULATION_ROWS names URL(s) the library no longer carries: {', '.join(missing)}")
    return list(orgs.values()), list(regs.values())


def health_entities(ledger):
    """PROPOSED with no source unless a ledger claim for the test has a proof and a date."""
    out = []
    for eid, name, aliases, match in HEALTH_TESTS:
        confirmed = [c for c in ledger.get("claims") or []
                     if re.search(c.get("pattern") or r"(?!x)x", match, re.I)
                     and (c.get("proof") or "NOT FETCHED") != "NOT FETCHED" and c.get("confirmed")]
        out.append({"id": eid, "name": name, "aliases": list(aliases), "class": "Health",
                    "authorization": "ASSERTED" if confirmed else "PROPOSED",
                    "source": "data/quality/evidence-ledger.json" if confirmed else None,
                    "owner_page": "blue-staffy-health-uk"})
    return out


def people_entities(settings):
    name = settings.get("breeder_name")
    if not name:
        return []
    return [{"id": slug_id(name), "name": name, "aliases": ["the breeder"], "class": "People",
             "authorization": "ASSERTED", "source": "data/settings.json", "owner_page": "blue-staffy-uk-breeders"}]


def seeded(existing, locations, settings, ledger, rows):
    """The ontology a seed run writes: every existing entity as it is, then new ones."""
    have = {e["id"] for e in existing["entities"]}
    orgs, regs = library_entities(rows)
    new = [e for e in (people_entities(settings) + place_entities(locations, settings) + health_entities(ledger)
                       + orgs + regs) if e["id"] not in have]
    new.sort(key=lambda e: (CLASS_ORDER.index(e["class"]), e["id"]))
    ont = {"entities": list(existing["entities"]) + new}
    PB.validate_ontology(ont)
    return ont


def _text(ont):
    return json.dumps(ont, indent=2, ensure_ascii=False) + "\n"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ont = seeded(PB._read_json(PB.ONTOLOGY), PB._read_json(LOCATIONS), PB._read_json(SETTINGS),
                 PB._read_json(LEDGER), library_rows())
    text = _text(ont)
    if "--check" in argv:
        if PB.ONTOLOGY.read_text(encoding="utf-8") != text:
            print("data/bsuk-ontology.json is not what ontology_seed.py writes — run it", file=sys.stderr)
            return 1
        print(f"examined {len(ont['entities'])} entities; ontology is seeded")
        return 0
    PB.ONTOLOGY.write_text(text, encoding="utf-8")
    counts = {c: sum(e["class"] == c for e in ont["entities"]) for c in CLASS_ORDER}
    print(f"wrote data/bsuk-ontology.json — {len(ont['entities'])} entities: "
          + ", ".join(f"{c} {n}" for c, n in counts.items() if n)
          + f" ({sum(e['authorization'] == 'ASSERTED' for e in ont['entities'])} asserted, "
          f"{sum(e['authorization'] == 'PROPOSED' for e in ont['entities'])} proposed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
