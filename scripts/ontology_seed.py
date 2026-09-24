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
                A claim's pattern may match one test only. When the ledger proves a test
                that is already in the file as class Health, PROPOSED, source null, that
                entity is upgraded to ASSERTED with the ledger as its source; this is the
                only change a seed ever makes to an existing entity.
  People        data/settings.json `breeder_name`.

Idempotent. An entity already in the file is never rewritten — its authorization, source
and owner page may have been decided by an approval since — except for the health upgrade
described under Health above. New entities are appended in class order, then id order,
so a re-run with unchanged inputs writes the same bytes. A generated id in two classes, a
new id already in the file under another class, a ledger claim whose pattern matches more
than one test (one certificate proves one test) and a missing input file each stop the run.

  --check   exit 1 when the file on disk is not what a seed run would write (nothing written).
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pageboard as PB  # noqa: E402

LOCATIONS = PB.ROOT / "data" / "locations.json"
SETTINGS = PB.ROOT / "data" / "settings.json"
LEDGER = PB.ROOT / "data" / "quality" / "evidence-ledger.json"

CLASS_ORDER = ("People", "Place", "Health", "Organization", "Regulation", "Organism",
               "Commerce", "Logistics", "Documentation", "Method")

# host -> (id, name, aliases). The name is the one the library's own row text uses. A
# publisher on several hosts is one named tuple, so its hosts cannot drift apart.
UK_GOVERNMENT = ("ont:uk-government", "UK government", ["GOV.UK", "the government"])
KENNEL_CLUB = ("ont:the-kennel-club", "The Kennel Club", ["Royal Kennel Club", "KC"])
HOST_ORG = {
    "ico.org.uk": ("ont:ico", "Information Commissioner's Office", ["ICO"]),
    "gov.uk": UK_GOVERNMENT,
    "assets.publishing.service.gov.uk": UK_GOVERNMENT,
    "citizensadvice.org.uk": ("ont:citizens-advice", "Citizens Advice", []),
    "policies.google.com": ("ont:google", "Google", ["Google Analytics"]),
    "thekennelclub.org.uk": KENNEL_CLUB,
    "royalkennelclub.com": KENNEL_CLUB,
    "rspca.org.uk": ("ont:rspca", "RSPCA", []),
    "bva.co.uk": ("ont:bva", "British Veterinary Association", ["BVA"]),
    "pdsa.org.uk": ("ont:pdsa", "PDSA", []),
    "bluecross.org.uk": ("ont:blue-cross", "Blue Cross", ["The Blue Cross"]),
    # Task 4 starter rows. legislation.gov.uk is the government's own legislation site, one
    # publisher with gov.uk here as assets.publishing.service.gov.uk is.
    "legislation.gov.uk": UK_GOVERNMENT,
    "cumberland.gov.uk": ("ont:cumberland-council", "Cumberland Council", []),
    "dogstrust.org.uk": ("ont:dogs-trust", "Dogs Trust", []),
    "paag.org.uk": ("ont:paag", "Pet Advertising Advisory Group", []),
}
# Hosts that are in the library but are not an organisation a page is about.
SKIP_HOSTS = {
    "crufts.org.uk": "a dog show (an event), not an organisation; its organiser is already The Kennel Club",
    "pmc.ncbi.nlm.nih.gov": "PubMed Central, the archive that hosts a study; the study, not the archive, is the source",
}

# normalised URL -> (id, name, aliases). Only rows whose own text names a law or official rule.
REGULATION_ROWS = {
    "https://gov.uk/control-dog-public/banned-dogs":
        ("ont:dangerous-dogs-act-1991", "Dangerous Dogs Act 1991", ["banned dog types"]),
    "https://gov.uk/get-your-dog-cat-microchipped":
        ("ont:dog-microchipping-law", "Dog microchipping law",
         ["microchipping law", "compulsory microchipping", "Microchipping of Dogs (England) Regulations 2015"]),
    "https://gov.uk/data-protection":
        ("ont:uk-data-protection-law", "UK data protection law", ["data protection"]),
    "https://gov.uk/bring-pet-to-great-britain":
        ("ont:pet-travel-rules-gb", "Rules for bringing a pet into Great Britain", ["pet travel rules"]),
    "https://assets.publishing.service.gov.uk/media/5a819d3bed915d74e623335d/pb10308-dogs-cats-welfare-060215.pdf":
        ("ont:welfare-in-transport-pb10308", "Welfare in transport guidance for dogs and cats (PB10308)",
         ["PB10308", "welfare-in-transport guidance"]),
    # Task 4 starter rows on legislation.gov.uk: the text of two laws.
    "https://legislation.gov.uk/uksi/2018/486/contents/made":
        ("ont:animal-licensing-regulations-2018",
         "The Animal Welfare (Licensing of Activities Involving Animals) (England) Regulations 2018",
         ["animal activity licensing"]),
    "https://legislation.gov.uk/uksi/2015/108/contents/made":
        ("ont:dog-microchipping-law", "Dog microchipping law",
         ["microchipping law", "compulsory microchipping", "Microchipping of Dogs (England) Regulations 2015"]),
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

HEALTH_IDS = {t[0] for t in HEALTH_TESTS}

# The Rows-table columns the seed reads, by header name; any other column is ignored.
LIBRARY_COLUMNS = ("URL", "Host", "What it is", "First page using it")
URL_ROW = re.compile(r"^\|\s*https?://")


def slug_id(text):
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    if not slug:
        raise PB.BoardError(f"cannot slug {text!r}")
    return "ont:" + slug


def page_slug(first_page):
    """`/blue-staffy-health-uk/` (as the library writes it, in backticks) -> the board slug."""
    p = first_page.strip().strip("`").strip("/")
    return p or "index"


def _cells(line):
    """The cells of a `| a | b |` table line, stripped; the outer pipes are not cells."""
    body = line.strip()
    body = body[1:-1] if body.endswith("|") else body[1:]
    return [c.strip() for c in body.split("|")]


def library_rows(path=None):
    """(url, host, what, first_page) for every row of the Rows table, in file order.

    Read by the header row's column NAMES (LIBRARY_COLUMNS), so a column added anywhere in
    the table is ignored rather than shifting the read. A URL-led row whose cell count is not
    the header's (a stray `|` in its prose, a missing cell) or that sits under no header stops
    the run, as does a header without one of the needed columns. A header holds until the
    first line that is not a table line."""
    p = Path(path or PB.EXTERNAL_LIBRARY)
    out, header = [], None
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("|"):
            header = None
            continue
        cells = _cells(line)
        if cells[0] == "URL":
            lacking = [c for c in LIBRARY_COLUMNS if c not in cells]
            if lacking:
                raise PB.BoardError(f"{p}: line {n}: the Rows-table header has no {', '.join(lacking)} column")
            header = cells
            continue
        if not URL_ROW.match(line):
            continue
        if header is None:
            raise PB.BoardError(f"{p}: line {n} is a URL row with no header row above it")
        if len(cells) != len(header):
            raise PB.BoardError(f"{p}: line {n} has {len(cells)} cells but the header has {len(header)} "
                                "— a stray or missing `|`")
        row = dict(zip(header, cells))
        out.append((row["URL"], row["Host"], row["What it is"], page_slug(row["First page using it"])))
    if not out:
        raise PB.BoardError(f"{p}: no Rows-table lines parsed — the table changed shape")
    return out


def place_entities(locations, settings):
    out, plain = {}, set()
    for r in locations:
        lacking = [k for k in ("slug", "city", "canonical") if not r.get(k)]
        if lacking:
            raise PB.BoardError(f"data/locations.json row {r!r} has no {', '.join(lacking)}")
        city = re.sub(r"\s*\(.*?\)\s*", "", r["city"]).strip()
        if not city or city.upper() == "UK":
            continue
        eid = slug_id(city)
        # The first row owns the place, except that a row naming the city plainly beats one
        # with a parenthetical ("Glasgow (breeding dogs)"): the plain row is the city's page.
        is_plain = "(" not in r["city"]
        if eid not in out or (is_plain and eid not in plain):
            out[eid] = {"id": eid, "name": city, "aliases": [], "class": "Place",
                        "authorization": "ASSERTED", "source": "data/locations.json",
                        "owner_page": r["canonical"].strip("/")}
            if is_plain:
                plain.add(eid)
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
    """PROPOSED with no source unless a ledger claim for the test has a proof and a date.
    One certificate proves one test: a claim whose pattern matches two tests stops the run."""
    claims = ledger.get("claims") or []
    for c in claims:
        hits = [m for _e, _n, _a, m in HEALTH_TESTS if re.search(c.get("pattern") or r"(?!x)x", m, re.I)]
        if len(hits) > 1:
            raise PB.BoardError(f"evidence-ledger claim {c.get('id')!r} (pattern {c.get('pattern')!r}) "
                                f"matches more than one health test: {', '.join(hits)} — narrow its pattern")
    out = []
    for eid, name, aliases, match in HEALTH_TESTS:
        confirmed = [c for c in claims
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


def _upgrade(entity, generated):
    """The one rewrite a seed makes: a seeded health test still PROPOSED with no source,
    now proved by the ledger, becomes ASSERTED with the ledger as its source."""
    g = generated.get(entity["id"])
    if (g is not None and entity["id"] in HEALTH_IDS and entity["class"] == "Health"
            and entity["authorization"] == "PROPOSED" and entity["source"] is None
            and g["authorization"] == "ASSERTED"):
        return dict(entity, authorization="ASSERTED", source=g["source"])
    return entity


def seeded(existing, locations, settings, ledger, rows):
    """The ontology a seed run writes: every existing entity as it is (bar the one health
    upgrade `_upgrade` allows), then new ones."""
    have = {e["id"]: e for e in existing["entities"]}
    orgs, regs = library_entities(rows)
    generated = {}
    for e in (people_entities(settings) + place_entities(locations, settings) + health_entities(ledger)
              + orgs + regs):
        if e["id"] in generated:
            raise PB.BoardError(f"{e['id']} is generated twice, as {generated[e['id']]['class']} "
                                f"and as {e['class']}")
        if e["id"] in have and have[e["id"]]["class"] != e["class"]:
            raise PB.BoardError(f"{e['id']} is already in the ontology as {have[e['id']]['class']}; "
                                f"the seed would make it {e['class']}")
        generated[e["id"]] = e
    new = [e for e in generated.values() if e["id"] not in have]
    new.sort(key=lambda e: (CLASS_ORDER.index(e["class"]), e["id"]))
    ont = {"entities": [_upgrade(e, generated) for e in existing["entities"]] + new}
    PB.validate_ontology(ont)
    return ont


def _load(path):
    """An input file, or a BoardError naming the one that is missing."""
    if not Path(path).is_file():
        raise PB.BoardError(f"ontology_seed input {path} does not exist")
    return PB._read_json(path)


def _text(ont):
    return json.dumps(ont, indent=2, ensure_ascii=False) + "\n"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ont = seeded(_load(PB.ONTOLOGY), _load(LOCATIONS), _load(SETTINGS), _load(LEDGER), library_rows())
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
