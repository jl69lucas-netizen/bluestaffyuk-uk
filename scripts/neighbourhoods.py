#!/usr/bin/env python3
"""Board block 3d: the areas of a city the page could name, and the Staffy searches naming them.

The breeder asked (2026-10-03) to see "which area within the city we are targeting" and any
neighbourhood keywords. This block reads only what is already on disk:

  * the keyword data — data/queries/raw/<slug>/neighbourhood_keywords.response.json, one
    DataForSEO keyword_ideas response (UK, en, fetched 2026-10-03). It is the ONLY source of a
    volume. A phrase it holds with no search_volume is shown as "no volume", never as a guess;
  * the SERP and competitor files in the same folder (serp_google.json,
    serp_google.response.json, competitors.json), whose URLs and titles show which areas the
    ranking pages name (Barnet and Camden Town via staffie-owners listing URLs);
  * the page's keyword lists, keyword-universe.json and keyword-variants.json, in the
    docs/research/ folder the board's meta.sources names. A phrase whose recorded source says
    it is how a ranking page words the query (organic_title, organic_snippet, competitor_h2) is
    a COMPETITOR HEADING, listed apart from the searches with its source and its own recorded
    volume barrier, read verbatim from keyword-universe.json. Any other list phrase not in the
    keyword data is written NOT_IN_DATA (or its recorded barrier).

The fetch date is read from the sidecar neighbourhood_keywords.request.json (how the call was
made); without it the date is NOT FETCHED.

A page with no DataForSEO response reads free-keyword-signals.json in its research folder
instead (Manchester, 2026-10-07; Task 20, G6): each keyword_planner.runs[].rows[] phrase keeps
its avg_monthly_searches_range exactly as recorded (a Range, never narrowed or summed) and the
use rule reads the range's lower bound; each autocomplete suggestion the Planner did not size
is shown as "attested, no volume". The planner's recorded not_run barriers are printed as-is.

ONE GAZETTEER PER CITY, chosen by original_slots.own_city(board) (gazetteer_for): London's
below, and Greater Manchester's (MANCHESTER: the ten metropolitan boroughs, the City of
Manchester among them, Manchester city centre, compass areas and a test-pinned town → borough
map; bare "manchester" is the page's own city, never an area; "sale" is the town only after
in / near / around / from / to and never in "for sale"; "bury" only after one of those or
beside Manchester; Bury St Edmunds and Leigh-on-Sea are outside). A board with no
data/locations.json row keeps London's; a city with no gazetteer gets a NOT FETCHED line,
never another city's areas. The London rules that follow are London's gazetteer.

Areas come from a fixed gazetteer (BOROUGHS, CITY, COMPASS, DISTRICTS) pinned by
tests/py/test_neighbourhoods.py. It holds names only, never volumes. The regex filter that
fetched the keyword data let in false positives, so:

  * "barking" and "westminster" count only as a place: straight after for sale / puppies /
    pups or a location preposition (in, near, around, from, to). A dog word straight before
    them ("staffy barking", "staffordshire bull terrier westminster 2022"), "how to stop" or
    "#sounds" is noise;
  * bare "richmond" and "kingston" count only with "london" or "surrey" in the phrase (the
    "upon Thames" forms are the borough names and always count);
  * OUTSIDE names a place that is not London (Sutton in Ashfield, Brentwood);
  * only Staffy phrases count (is_staffy): bull terrier, English bull terrier, American
    Staffordshire and pit bull phrases are other breeds.

Each dropped phrase that would otherwise have matched is listed on the block's "Not shown" line
with its reason. The "Suggested use" column is mechanical (use_of): >= 50/mo its own H3; 10-49
named in the delivery copy and one FAQ answer; below 10 or no volume, at most one "We deliver
across London, including ..." line.

    python3 scripts/neighbourhoods.py <slug>
"""
import json
import pathlib
import re
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import keyword_metrics as KM  # noqa: E402
from term_density import md_table  # noqa: E402

ROOT = KM.ROOT
RESPONSE = "neighbourhood_keywords.response.json"
REQUEST = "neighbourhood_keywords.request.json"
SCANNED_RAW = ("serp_google.json", "serp_google.response.json", "competitors.json")
UNIVERSE, VARIANTS = "keyword-universe.json", "keyword-variants.json"
SCANNED_RESEARCH = (UNIVERSE, VARIANTS)
KEYWORD_SOURCE = "keyword data (DataForSEO keyword_ideas)"
# The free signals a page reads when no DataForSEO response is held (Manchester, 2026-10-07):
# Keyword Planner range buckets and Google autocomplete phrases, in its research folder.
SIGNALS = "free-keyword-signals.json"
PLANNER_SOURCE = f"Google Keyword Planner ({SIGNALS})"
AUTOCOMPLETE_SOURCE = f"Google autocomplete ({SIGNALS})"
ATTESTED = "attested, no volume"
NOT_IN_DATA = "NOT FETCHED — not in keyword data"
NO_SIDECAR = f"NOT FETCHED — no {REQUEST} records the fetch"
COMPASS_BOROUGH = "— (compass area)"
H3_MIN, FAQ_MIN = 50, 10
LONDON_WIDE_TOP = 6
# A list phrase whose every recorded source is ranking-page text is a competitor heading.
HEADING_SOURCES = frozenset({"organic_title", "organic_snippet", "competitor_h2"})
HEADING_MARK = "how the ranking pages word the query"

BOROUGHS = (
    "Barking and Dagenham", "Barnet", "Bexley", "Brent", "Bromley", "Camden", "Croydon",
    "Ealing", "Enfield", "Greenwich", "Hackney", "Hammersmith and Fulham", "Haringey", "Harrow",
    "Havering", "Hillingdon", "Hounslow", "Islington", "Kensington and Chelsea",
    "Kingston upon Thames", "Lambeth", "Lewisham", "Merton", "Newham", "Redbridge",
    "Richmond upon Thames", "Southwark", "Sutton", "Tower Hamlets", "Waltham Forest",
    "Wandsworth", "Westminster",
)
CITY = "City of London"
COMPASS = tuple(f"{c} london" for c in (
    "north", "south", "east", "west", "central", "south east", "south west", "north east",
    "north west"))
# Town or district -> its borough.
DISTRICTS = {
    "Romford": "Havering", "Ilford": "Redbridge", "Walthamstow": "Waltham Forest",
    "Uxbridge": "Hillingdon", "Camden Town": "Camden", "Brixton": "Lambeth",
    "Peckham": "Southwark", "Tottenham": "Haringey", "Wimbledon": "Merton",
    "Stratford": "Newham", "Woolwich": "Greenwich", "Catford": "Lewisham",
    "Edmonton": "Enfield", "Dagenham": "Barking and Dagenham",
    "Barking": "Barking and Dagenham", "Southall": "Ealing", "Paddington": "Westminster",
    "Richmond": "Richmond upon Thames", "Kingston": "Kingston upon Thames",
}
# Names that are also ordinary words or events; they count only as a place.
AMBIGUOUS = frozenset({"barking", "westminster"})
# Names shared with places outside London; they count only beside "london" or "surrey".
NEEDS_CONTEXT = frozenset({"richmond", "kingston"})
OUTSIDE = {
    "sutton in ashfield": "Sutton in Ashfield is in Nottinghamshire",
    "sutton coldfield": "Sutton Coldfield is in the West Midlands",
    "brentwood": "Brentwood is in Essex, outside Greater London",
}
REASONS = {
    "barking": "“barking” here is a dog barking, not the town of Barking",
    "westminster": "“westminster” here is the Westminster dog show, not the borough",
    "richmond": "“richmond” without London or Surrey may be Richmond, North Yorkshire",
    "kingston": "“kingston” without London or Surrey may be Kingston upon Hull",
    "breed": "another breed, not a Staffy term (bull terrier, English bull terrier, "
             "American Staffordshire, pit bull)",
}

STAFFY = re.compile(r"\b(staffys?|staffie|staffies|staffordshire bull terriers?"
                    r"|staffordshire pupp\w*|staffordshire dogs?|staff pupp\w*|staff pups)\b")
OTHER_BREED = re.compile(r"\b(american|english bull terriers?|miniature bull terriers?"
                         r"|mini bull terriers?|mini english bull|pit ?bulls?|pitbulls?)\b")
# An ambiguous name is a place straight after these; a dog word before it is noise.
PLACE_BEFORE = re.compile(r"\b(in|near|around|from|to|for sale|puppies|pups)\s+$")
NOISE = re.compile(r"\b(how to stop|sounds)\b")
CONTEXT = re.compile(r"\b(london|surrey)\b")


# An ambiguous name is a place only straight after one of these (Greater Manchester's rule).
LOCATION_BEFORE = re.compile(r"\b(in|near|around|from|to)\s+$")


def _norm(text):
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


def _word_re(name):
    return re.compile(rf"(?<![a-z0-9]){re.escape(name)}(?![a-z0-9])")


class Gazetteer:
    """One city's fixed list of area NAMES (never volumes) and its false-positive rules.

    rules maps an ambiguous name to how it counts as a place:
      ("place_before",)        straight after PLACE_BEFORE, and never with NOISE (London)
      ("context", regex)       only when regex finds a word anywhere in the phrase
      ("location",)            only straight after LOCATION_BEFORE (in, near, around, from, to)
      ("location_or_beside", regex)  after LOCATION_BEFORE, or with regex right beside it
    never: phrases blanked before any scan ("for sale" is never the town of Sale).
    checks: the rule names exclusion_reason() tries, in order."""

    def __init__(self, city, region, intro, boroughs, city_area, compass, districts, rules,
                 outside, reasons, checks, extra=None, never=()):
        self.city, self.region, self.intro = city, region, intro
        self.boroughs, self.city_area, self.compass = boroughs, city_area, compass
        self.districts, self.rules, self.outside = districts, rules, outside
        self.reasons, self.checks, self.extra = reasons, checks, extra or {}
        self.city_word = city.lower()
        self.never = tuple(re.compile(p) for p in never)
        g = {b.lower(): (b, b) for b in boroughs}
        g[city_area.lower()] = (city_area, city_area)
        for c in compass:
            g[c] = (c.title(), COMPASS_BOROUGH)
        for a, b in self.extra.items():
            g[a.lower()] = (a, b)
        for d, b in districts.items():
            g[_norm(d)] = (d, b)
        self.names = g
        self._order = sorted(g, key=len, reverse=True)
        self._re = {n: _word_re(n) for n in self._order}

    def blank(self, n):
        for o in self.outside:
            n = _word_re(o).sub(lambda m: "#" * len(m.group()), n)
        for p in self.never:
            n = p.sub(lambda m: "#" * len(m.group()), n)
        return n

    def is_place(self, name, n, start):
        rule = self.rules.get(name)
        if rule is None:
            return True
        kind, before = rule[0], n[:start]
        if kind == "place_before":
            return not NOISE.search(n) and bool(PLACE_BEFORE.search(before))
        if kind == "context":
            return bool(rule[1].search(n))
        if LOCATION_BEFORE.search(before):
            return True
        if kind == "location_or_beside":
            after = n[start + len(name):]
            return bool(re.search(rf"\b{rule[1]}\s+$", before)
                        or re.match(rf"\s+{rule[1]}\b", after))
        return False


LONDON = Gazetteer(
    city="London", region="London",
    intro="Which parts of the city this page could name, and the Staffy searches that name "
          "them. Areas come from a fixed list of the 32 London boroughs, the City, the compass "
          "areas (south east London and the like) and common towns mapped to their borough.",
    boroughs=BOROUGHS, city_area=CITY, compass=COMPASS, districts=DISTRICTS,
    rules={**{n: ("place_before",) for n in AMBIGUOUS},
           **{n: ("context", CONTEXT) for n in NEEDS_CONTEXT}},
    outside=OUTSIDE, reasons=REASONS, checks=("westminster", "barking", "richmond", "kingston"))

# Greater Manchester: the ten metropolitan boroughs (the City of Manchester is the tenth),
# well-known towns to their borough, pinned by tests/py/test_neighbourhoods.py. Bare
# "manchester" is the page's own city, never an area. Names only, never volumes.
GM_BOROUGHS = ("Bolton", "Bury", "Oldham", "Rochdale", "Salford", "Stockport", "Tameside",
               "Trafford", "Wigan")
GM_DISTRICTS = {
    "Altrincham": "Trafford", "Sale": "Trafford", "Stretford": "Trafford",
    "Stalybridge": "Tameside", "Ashton-under-Lyne": "Tameside", "Cheadle": "Stockport",
    "Eccles": "Salford", "Swinton": "Salford", "Wythenshawe": "City of Manchester",
    "Didsbury": "City of Manchester", "Leigh": "Wigan", "Prestwich": "Bury",
}
MANCHESTER = Gazetteer(
    city="Manchester", region="Greater Manchester",
    intro="Which parts of the city this page could name, and the Staffy searches that name "
          "them. Areas come from a fixed list of Greater Manchester's ten metropolitan boroughs "
          "(the City of Manchester among them), Manchester city centre, the compass areas "
          "(south Manchester and the like) and common towns mapped to their borough. Bare "
          "“manchester” is the page's own city, never an area.",
    boroughs=GM_BOROUGHS, city_area="City of Manchester",
    compass=tuple(f"{c} manchester" for c in ("north", "south", "east", "west", "central")),
    extra={"Manchester City Centre": "City of Manchester"},
    districts=GM_DISTRICTS,
    rules={"sale": ("location",),
           "bury": ("location_or_beside", r"(?:greater )?manchester"),
           "swinton": ("context", re.compile(r"\b(manchester|salford)\b"))},
    outside={"bury st edmunds": "Bury St Edmunds is in Suffolk",
             "bury saint edmunds": "Bury St Edmunds is in Suffolk",
             "leigh on sea": "Leigh-on-Sea is in Essex, outside Greater Manchester"},
    reasons={"sale": "“sale” here is the word sale, not the town of Sale (Trafford): the town "
                     "counts only after in, near, around, from or to",
             "bury": "“bury” without in, near, around, from or to before it, or Manchester "
                     "beside it, may be Bury St Edmunds or the verb",
             "swinton": "“swinton” without Manchester or Salford may be Swinton, South Yorkshire",
             "breed": REASONS["breed"]},
    checks=("sale", "bury", "swinton"),
    never=(r"\bfor sale\b",))

GAZETTEERS = {"London": LONDON, "Manchester": MANCHESTER}
# London's names, kept for the callers that read them directly.
GAZETTEER = LONDON.names


def _gaz(gaz):
    if gaz is None:
        return LONDON
    return GAZETTEERS[gaz] if isinstance(gaz, str) else gaz


def gazetteer_for(board, root=ROOT):
    """The board's own city's gazetteer (original_slots.own_city). A board with no
    data/locations.json row keeps London's, as before; a city with no gazetteer gets None,
    never another city's areas. Imported lazily: original_slots pulls in the image modules."""
    import original_slots as OS
    city = OS.own_city(board, root)
    return LONDON if city is None else GAZETTEERS.get(city)


def _scan(text, strict=True, gaz=None):
    """[(name, start)] in text order, longest names first, no overlaps."""
    gaz = _gaz(gaz)
    n = gaz.blank(_norm(text))
    taken, hits = [], []
    for name in gaz._order:
        for m in gaz._re[name].finditer(n):
            s, e = m.span()
            if any(s < te and ts < e for ts, te in taken):
                continue
            if strict and not gaz.is_place(name, n, s):
                continue
            taken.append((s, e))
            hits.append((name, s))
    return sorted(hits, key=lambda h: h[1])


def lookup(text, gaz=None):
    """[(area, borough)] the text names, after the false-positive rules (London by default)."""
    gaz = _gaz(gaz)
    out = []
    for name, _ in _scan(text, gaz=gaz):
        if gaz.names[name] not in out:
            out.append(gaz.names[name])
    return out


def is_staffy(text):
    n = _norm(text)
    return bool(STAFFY.search(n)) and not OTHER_BREED.search(n)


def exclusion_reason(text, gaz=None):
    """Why a phrase that looks like an area match is not one; None when it is not dropped."""
    gaz = _gaz(gaz)
    n = _norm(text)
    for o, why in gaz.outside.items():
        if _word_re(o).search(n):
            return why
    loose = {name for name, _ in _scan(text, strict=False, gaz=gaz)}
    strict = {name for name, _ in _scan(text, gaz=gaz)}
    for word in gaz.checks:
        if word in loose and word not in strict:
            return gaz.reasons[word]
    if loose and (STAFFY.search(n) is None or OTHER_BREED.search(n)):
        return gaz.reasons["breed"]
    return None


class Range(str):
    """A Keyword Planner range bucket, kept exactly as recorded ("100 – 1K"), never narrowed.
    `low` is its lower bound, the only figure the use rule reads; None when unreadable."""

    @property
    def low(self):
        m = re.match(r"\s*(\d+(?:\.\d+)?)\s*([KkMm]?)\s*[–-]", self)
        if not m:
            return None
        return int(float(m.group(1)) * {"": 1, "k": 1000, "m": 1000000}[m.group(2).lower()])


def _key(volume):
    """The number a volume is ranked and judged by: an int, a Range's lower bound, else None."""
    if isinstance(volume, Range):
        return volume.low
    return volume if isinstance(volume, int) else None


def use_of(volume):
    volume = _key(volume)
    if isinstance(volume, int) and volume >= H3_MIN:
        return "h3"
    if isinstance(volume, int) and volume >= FAQ_MIN:
        return "faq"
    return "line"


def use_label(use, gaz=None):
    return {"h3": "Own H3",
            "faq": "Delivery copy + one FAQ answer",
            "line": f"“We deliver across {_gaz(gaz).region}, including …” line, if at all"}[use]


USE_LABEL = {u: use_label(u) for u in ("h3", "faq", "line")}


def _load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _raw_dir(board, root):
    return pathlib.Path(root) / "data/queries/raw" / board["meta"]["slug"]


def _research_dir(board, root):
    for s in board.get("meta", {}).get("sources", []):
        p = str(s.get("path", ""))
        if p.startswith("docs/research/"):
            return pathlib.Path(root) / pathlib.PurePosixPath(p).parent
    return pathlib.Path(root) / "docs/research" / board["meta"]["slug"]


def _planner_data(sig):
    """free-keyword-signals.json as keyword data: every keyword_planner.runs[].rows[] phrase
    with its avg_monthly_searches_range as a Range, exactly as recorded, then every autocomplete
    suggestion the Planner did not size, as ATTESTED (people search it; how many is unknown)."""
    kp, ac = sig["keyword_planner"], sig.get("autocomplete") or {}
    rows, seen, n_planner = [], set(), 0
    for run in kp.get("runs") or []:
        for r in run.get("rows") or []:
            kw = str(r.get("keyword", "")).strip().lower()
            rng = r.get("avg_monthly_searches_range")
            if kw and kw not in seen:
                seen.add(kw)
                n_planner += 1
                rows.append((kw, Range(rng) if isinstance(rng, str) and rng.strip() else NOT_IN_DATA))
    for seed in ac.get("seeds") or []:
        for sug in seed.get("suggestions") or []:
            kw = str(sug).strip().lower()
            if kw and kw not in seen:
                seen.add(kw)
                rows.append((kw, ATTESTED))
    not_run = kp.get("not_run") if isinstance(kp.get("not_run"), dict) else {}
    return {"rows": rows, "total_count": None, "source": "planner", "planner_rows": n_planner,
            "fetched": kp.get("read_at") or f"NOT FETCHED — {SIGNALS} records no read date",
            "not_run": not_run}


def keyword_data(board, root=ROOT):
    """{rows: [(keyword, volume)], total_count, fetched, source}, or None when nothing is held.
    The DataForSEO response (volume an int or None) wins; without it, the research folder's
    free-keyword-signals.json (volume a Range or ATTESTED)."""
    doc = _load(_raw_dir(board, root) / RESPONSE)
    if not isinstance(doc, dict) or not isinstance(doc.get("items"), list):
        sig = _load(_research_dir(board, root) / SIGNALS)
        if isinstance(sig, dict) and isinstance(sig.get("keyword_planner"), dict):
            return _planner_data(sig)
        return None
    rows = []
    for it in doc["items"]:
        kw = str(it.get("keyword", "")).strip().lower()
        vol = (it.get("keyword_info") or {}).get("search_volume")
        if kw:
            rows.append((kw, vol if isinstance(vol, int) else None))
    req = _load(_raw_dir(board, root) / REQUEST)
    fetched = req.get("fetched") if isinstance(req, dict) and req.get("fetched") else NO_SIDECAR
    total = doc.get("total_count") if isinstance(doc.get("total_count"), int) else None
    return {"rows": rows, "total_count": total, "fetched": fetched, "source": "dataforseo"}


def keyword_rows(board, root=ROOT):
    """The response file's items as [(keyword, volume|None)], or None when it is not held."""
    kd = keyword_data(board, root)
    return None if kd is None else kd["rows"]


def _strings(node):
    """Every string in a JSON tree."""
    if isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)
    elif isinstance(node, str):
        yield node


def _entries(node):
    """Every dict in a JSON tree that carries a "keyword" or "term" string."""
    if isinstance(node, dict):
        if isinstance(node.get("keyword"), str) or isinstance(node.get("term"), str):
            yield node
        for v in node.values():
            yield from _entries(v)
    elif isinstance(node, list):
        for v in node:
            yield from _entries(v)


def is_heading(entry):
    """True when the entry's recorded source says it is how a ranking page words the query."""
    srcs = entry.get("sources")
    if isinstance(srcs, list) and srcs:
        return set(srcs) <= HEADING_SOURCES
    src = str(entry.get("source", ""))
    return HEADING_MARK in src or any(h in src for h in HEADING_SOURCES)


def _entry_source(fname, entry):
    if isinstance(entry.get("sources"), list):
        return f"{fname}: {', '.join(entry['sources'])}"
    return f"{fname}: {entry.get('source', 'no source recorded')}"


def _source_of(vol, kd):
    if kd.get("source") != "planner":
        return KEYWORD_SOURCE
    return AUTOCOMPLETE_SOURCE if type(vol) is str and vol == ATTESTED else PLANNER_SOURCE


def areas(board, root=ROOT, gaz=None):
    root = pathlib.Path(root)
    gaz = _gaz(gaz) if gaz is not None else gazetteer_for(board, root) or LONDON
    rows = {}

    def row(area, borough):
        return rows.setdefault(area, {"area": area, "borough": borough, "keywords": [],
                                      "headings": [], "total_volume": None, "seen_in": []})

    def seen(r, src):
        if src not in r["seen_in"]:
            r["seen_in"].append(src)

    def add_kw(r, kw, vol):
        if all(_norm(k["kw"]) != _norm(kw) for k in r["keywords"]):
            r["keywords"].append({"kw": kw, "volume": vol})

    def add_heading(r, text, source, vol):
        for h in r["headings"]:
            if h["heading"] == text:
                if source not in h["sources"]:
                    h["sources"].append(source)
                return
        r["headings"].append({"heading": text, "sources": [source], "volume": vol})

    kd = keyword_data(board, root) or {"rows": []}
    kws = kd["rows"]
    volume_of = {_norm(k): v for k, v in kws}
    for kw, vol in kws:
        if not is_staffy(kw):
            continue
        for area, borough in lookup(kw, gaz):
            r = row(area, borough)
            add_kw(r, kw, vol)
            seen(r, _source_of(vol, kd))

    raw, research = _raw_dir(board, root), _research_dir(board, root)
    # The universe file records each phrase's own volume barrier; it is read, never reworded.
    universe = _load(research / UNIVERSE)
    barrier_of = {_norm(e["keyword"]): e["volume"] for e in _entries(universe or {})
                  if isinstance(e.get("keyword"), str) and isinstance(e.get("volume"), str)}

    def volume_for(phrase, fname):
        if phrase in volume_of:
            return volume_of[phrase]
        if phrase in barrier_of:
            return barrier_of[phrase]
        return f"NOT FETCHED — {fname} records no volume for this phrase"

    for path in [raw / f for f in SCANNED_RAW] + [research / f for f in SCANNED_RESEARCH]:
        doc = universe if path.name == UNIVERSE and path.parent == research else _load(path)
        if doc is None:
            continue
        rel = path.relative_to(root).as_posix()
        for s in _strings(doc):
            if s.startswith(("http://", "https://")):
                u = urlsplit(s)
                text = u.path.replace("-", " ").replace("_", " ").replace("/", " ")
                if is_staffy(text):
                    for area, borough in lookup(text, gaz):
                        seen(row(area, borough), f"{u.scheme}://{u.netloc}{u.path}")
            elif is_staffy(s):
                for area, borough in lookup(s, gaz):
                    seen(row(area, borough), rel)
        if path.parent != research:
            continue
        for e in _entries(doc):
            text = e.get("keyword") if isinstance(e.get("keyword"), str) else e["term"]
            if not is_staffy(text):
                continue
            phrase = _norm(text)  # "barnet, london" and "barnet london" are one phrase
            for area, borough in lookup(text, gaz):
                r = row(area, borough)
                if is_heading(e):
                    add_heading(r, phrase, _entry_source(path.name, e), volume_for(phrase, path.name))
                else:
                    add_kw(r, phrase, volume_for(phrase, path.name)
                           if phrase in volume_of or phrase in barrier_of else NOT_IN_DATA)

    for r in rows.values():
        ints = [k["volume"] for k in r["keywords"] if isinstance(k["volume"], int)]
        r["total_volume"] = sum(ints) if ints else None
        # Ranges are never summed: an area is judged by its best range, shown as recorded.
        ranges = [k["volume"] for k in r["keywords"] if _key(k["volume"]) is not None
                  and isinstance(k["volume"], Range)]
        r["use_volume"] = (max(ranges, key=_key) if r["total_volume"] is None and ranges
                           else r["total_volume"])
    return sorted(rows.values(), key=lambda r: (-(_key(r["use_volume"]) or -1), r["area"]))


def not_shown(board, root=ROOT, gaz=None):
    """[(keyword, reason)] for every keyword-data phrase dropped as a false area match."""
    gaz = _gaz(gaz) if gaz is not None else gazetteer_for(board, root) or LONDON
    out = []
    for kw, _ in keyword_rows(board, root) or []:
        why = exclusion_reason(kw, gaz)
        if why:
            out.append((kw, why))
    return out


def city_wide(board, root=ROOT, gaz=None):
    """The top city-wide Staffy terms (the city named, no area) with a volume, highest first;
    a Planner range ranks by its lower bound and is shown as recorded."""
    gaz = _gaz(gaz) if gaz is not None else gazetteer_for(board, root) or LONDON
    rows = [(kw, v) for kw, v in keyword_rows(board, root) or []
            if _key(v) is not None and is_staffy(kw) and gaz.city_word in _norm(kw).split()
            and not lookup(kw, gaz) and not exclusion_reason(kw, gaz)]
    return sorted(rows, key=lambda r: -_key(r[1]))[:LONDON_WIDE_TOP]


london_wide = city_wide


def _vol_cell(r):
    if isinstance(r["total_volume"], int):
        return str(r["total_volume"])
    if isinstance(r.get("use_volume"), Range):
        return str(r["use_volume"])
    if any(k["volume"] is None for k in r["keywords"]):
        return "none returned"
    barriers = [k["volume"] for k in r["keywords"] if isinstance(k["volume"], str)]
    return barriers[0] if barriers else NOT_IN_DATA


def _vol_text(v):
    return str(v) if isinstance(v, int) else "no volume" if v is None else v


def _kw_cell(r):
    if not r["keywords"]:
        return "—"
    return "; ".join(f"{k['kw']} ({_vol_text(k['volume'])})" for k in r["keywords"])


def _heading_cell(r):
    if not r["headings"]:
        return "—"
    return "; ".join(f"“{h['heading']}” — source: {' + '.join(h['sources'])} — volume: "
                     f"{_vol_text(h['volume'])}" for h in r["headings"])


def _seen_cell(r):
    out = []
    for s in r["seen_in"]:
        if s == KEYWORD_SOURCE:
            out.append("keyword data")
        elif s == PLANNER_SOURCE:
            out.append("Keyword Planner")
        elif s == AUTOCOMPLETE_SOURCE:
            out.append("autocomplete")
        elif s.startswith(("http://", "https://")):
            u = urlsplit(s)
            out.append(f"ranking page {u.netloc.removeprefix('www.')}{u.path}")
        else:
            out.append(pathlib.PurePosixPath(s).name)
    return "; ".join(out)


def _names(rows):
    names = [r["area"] for r in rows]
    return ", ".join(names[:-1]) + f" and {names[-1]}" if len(names) > 1 else "".join(names)


def _use_vol(r):
    return r.get("use_volume", r.get("total_volume"))


def target_line(rows, wide, gaz=None):
    """The block's one "**Target:**" line, from the use rule and the city-wide terms."""
    gaz = _gaz(gaz)
    h3 = [r for r in rows if use_of(_use_vol(r)) == "h3"]
    faq = [r for r in rows if use_of(_use_vol(r)) == "faq"]
    rest = [r for r in rows if use_of(_use_vol(r)) == "line"]
    t = ["**Target:**"]
    if h3:
        t.append(f"give {_names(h3)} its own H3.")
    else:
        t.append(f"no area reaches {H3_MIN}/mo, so none gets its own H3.")
    if faq:
        vols = ", ".join(f"{r['area']} {_use_vol(r)}/mo" for r in faq)
        t.append(f"Name {_names(faq)} in the delivery section copy and one FAQ answer ({vols}).")
    if rest:
        t.append(f"{_names(rest)} show no measurable volume — at most one “We deliver across "
                 f"{gaz.region}, including …” line.")
    if wide:
        judged = [_use_vol(r) for r in rows if _key(_use_vol(r)) is not None]
        best = max(judged, key=_key) if judged else None
        t.append(f"The {gaz.city}-wide terms carry the volume (“{wide[0][0]}” {wide[0][1]}/mo"
                 + (f" against {best}/mo for the best area" if best is not None else "")
                 + f"), so the page targets {gaz.city} as a whole and names areas only as "
                   f"delivery reach.")
    else:
        t.append(f"{gaz.city}-wide volume is NOT FETCHED, so the target rests on area presence only.")
    return " ".join(t)


def _volumes_line(kd):
    if kd is None:
        return (f"Volumes: NOT FETCHED — no `{RESPONSE}` is held for this page, so every "
                f"area below carries `{NOT_IN_DATA}`.")
    if kd.get("source") == "planner":
        n_ac = len(kd["rows"]) - kd["planner_rows"]
        return (f"Volumes are Google Ads average monthly searches from Google Keyword Planner "
                f"(UK), read {kd['fetched']} (`{SIGNALS}`): {kd['planner_rows']} Planner rows, "
                f"each range shown exactly as recorded and never narrowed; the suggested use "
                f"reads a range's lower bound. {n_ac} phrases Google autocomplete suggests are "
                f"shown as “{ATTESTED}”: people search them, but autocomplete says nothing about "
                f"how many. An area seen only on a ranking page or in the keyword lists carries "
                f"`{NOT_IN_DATA}` or the barrier its list records.")
    total = kd["total_count"] if kd["total_count"] is not None else "an unrecorded number of"
    return (f"Volumes are UK monthly Google searches from DataForSEO keyword data "
            f"(`keyword_ideas`, UK, en), fetched {kd['fetched']}: {len(kd['rows'])} of "
            f"{total} rows held (DataForSEO total_count). An area seen only on a ranking "
            f"page or in the keyword lists carries `{NOT_IN_DATA}` or the barrier its "
            f"list records.")


def block(board, root=ROOT):
    gaz = gazetteer_for(board, root)
    if gaz is None:
        import original_slots as OS
        city = OS.own_city(board, root)
        return (f"Which parts of the city this page could name: NOT FETCHED — no area list is "
                f"held for {city} in scripts/neighbourhoods.py (GAZETTEERS), so no area is shown. "
                f"{city}'s list is added there, test-pinned, before this block reads its areas.")
    kd = keyword_data(board, root)
    rows = areas(board, root, gaz)
    lines = [gaz.intro, _volumes_line(kd)]
    lines.append("**Competitor headings** are phrases the keyword lists record as how a ranking "
                 "page words the query (titles, snippets, H2s). They are not searches, so they "
                 "sit in their own column with their source and their own recorded volume.")
    lines.append("")

    lines.append(f"**{gaz.city} as a whole** — the top {gaz.city}-wide Staffy terms, for comparison:")
    lines.append("")
    wide = city_wide(board, root, gaz)
    if wide:
        lines.append(md_table(["Keyword", "Monthly searches"], [[k, v] for k, v in wide]))
    else:
        lines.append(f"_NOT FETCHED — no {gaz.city}-wide Staffy term with a volume in the keyword data._")
    lines.append("")

    body = [[r["area"], r["borough"], _kw_cell(r), _heading_cell(r), _vol_cell(r), _seen_cell(r),
             use_label(use_of(_use_vol(r)), gaz)] for r in rows]
    lines.append(md_table(["Area", "Borough", "Keywords found", "Competitor headings",
                           "Monthly searches", "Where seen", "Suggested use"], body)
                 if body else f"_No {gaz.city} area found in the data._")
    lines.append("")
    lines.append(f"**Suggested use rule:** ≥ {H3_MIN}/mo → its own H3; {FAQ_MIN}–{H3_MIN - 1} → named "
                 f"in the delivery section copy and one FAQ answer; below {FAQ_MIN} or no volume → "
                 f"mention only in a “We deliver across {gaz.region}, including …” line, if at all.")
    lines.append("")
    lines.append(target_line(rows, wide, gaz))
    lines.append("")

    if kd and kd.get("not_run"):
        lines.append("**Not run in the Planner:** " + " · ".join(
            f"{k}: {v}" for k, v in kd["not_run"].items()))
        lines.append("")
    dropped = not_shown(board, root, gaz)
    if dropped:
        by = {}
        for kw, why in dropped:
            by.setdefault(why, []).append(f"“{kw}”")
        lines.append("**Not shown:** " + " · ".join(f"{why}: {', '.join(k)}" for why, k in by.items()) + ".")
    else:
        lines.append("**Not shown:** nothing dropped.")
    return "\n".join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    usage = "usage: python3 scripts/neighbourhoods.py <slug>"
    if len(argv) != 1:
        print(usage, file=sys.stderr)
        return 2
    path = ROOT / "data/boards" / f"{KM._bare(argv[0])}.json"
    if not path.is_file():
        print(f"{usage} — no board at {path.relative_to(ROOT)}", file=sys.stderr)
        return 2
    try:
        board = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(board, dict) or not isinstance(board.get("meta"), dict) \
                or not isinstance(board["meta"].get("slug"), str):
            raise ValueError("board has no meta.slug")
        out = block(board)
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        print(f"{usage} — {path.relative_to(ROOT)} is not a readable board: {e}", file=sys.stderr)
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
