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
    docs/research/ folder the board's meta.sources names. A phrase found there but not in the
    keyword data is written NOT_IN_DATA.

Areas come from a fixed gazetteer (BOROUGHS, CITY, COMPASS, DISTRICTS) pinned by
tests/py/test_neighbourhoods.py. It holds names only, never volumes. The regex filter that
fetched the keyword data let in false positives, so:

  * "barking" and "westminster" count only as a place: after in/near/around/from/to, in a
    phrase that also says for sale / puppies / pups ("staffy barking" is a dog barking,
    "staffordshire bull terrier westminster 2022" is the dog show);
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
SCANNED_RAW = ("serp_google.json", "serp_google.response.json", "competitors.json")
SCANNED_RESEARCH = ("keyword-universe.json", "keyword-variants.json")
KEYWORD_FETCHED = "2026-10-03"
KEYWORD_SOURCE = f"keyword data (DataForSEO keyword_ideas, {KEYWORD_FETCHED})"
NOT_IN_DATA = "NOT FETCHED — not in keyword data"
COMPASS_BOROUGH = "— (compass area)"
H3_MIN, FAQ_MIN = 50, 10
LONDON_WIDE_TOP = 6

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
}
# Names that are also ordinary words or events; they count only as a place.
AMBIGUOUS = frozenset({"barking", "westminster"})
OUTSIDE = {
    "sutton in ashfield": "Sutton in Ashfield is in Nottinghamshire",
    "sutton coldfield": "Sutton Coldfield is in the West Midlands",
    "brentwood": "Brentwood is in Essex, outside Greater London",
}
REASONS = {
    "barking": "“barking” here is a dog barking, not the town of Barking",
    "westminster": "“westminster” here is the Westminster dog show, not the borough",
    "breed": "another breed, not a Staffy term (bull terrier, English bull terrier, "
             "American Staffordshire, pit bull)",
}

STAFFY = re.compile(r"\b(staffys?|staffie|staffies|staffordshire bull terriers?"
                    r"|staffordshire pupp\w*|staffordshire dogs?|staff pupp\w*|staff pups)\b")
OTHER_BREED = re.compile(r"\b(american|english bull terriers?|miniature bull terriers?"
                         r"|mini bull terriers?|mini english bull|pit ?bulls?|pitbulls?)\b")
PLACE_PREP = re.compile(r"\b(in|near|around|from|to)\s+$")
SALE = re.compile(r"\b(for sale|pupp\w*|pups)\b")


def _gazetteer():
    g = {b.lower(): (b, b) for b in BOROUGHS}
    g[CITY.lower()] = (CITY, CITY)
    for c in COMPASS:
        g[c] = (c.title(), COMPASS_BOROUGH)
    for d, b in DISTRICTS.items():
        g[d.lower()] = (d, b)
    return g


GAZETTEER = _gazetteer()
_NAMES = sorted(GAZETTEER, key=len, reverse=True)
_NAME_RE = {n: re.compile(rf"(?<![a-z0-9]){re.escape(n)}(?![a-z0-9])") for n in _NAMES}


def _norm(text):
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


def _blank_outside(n):
    for o in OUTSIDE:
        n = re.sub(rf"(?<![a-z0-9]){re.escape(o)}(?![a-z0-9])", lambda m: "#" * len(m.group()), n)
    return n


def _scan(text, strict=True):
    """[(name, start)] in text order, longest names first, no overlaps."""
    n = _blank_outside(_norm(text))
    taken, hits = [], []
    for name in _NAMES:
        for m in _NAME_RE[name].finditer(n):
            s, e = m.span()
            if any(s < te and ts < e for ts, te in taken):
                continue
            if strict and name in AMBIGUOUS and not (PLACE_PREP.search(n[:s]) and SALE.search(n)):
                continue
            taken.append((s, e))
            hits.append((name, s))
    return sorted(hits, key=lambda h: h[1])


def lookup(text):
    """[(area, borough)] the text names, after the false-positive rules."""
    out = []
    for name, _ in _scan(text):
        if GAZETTEER[name] not in out:
            out.append(GAZETTEER[name])
    return out


def is_staffy(text):
    n = _norm(text)
    return bool(STAFFY.search(n)) and not OTHER_BREED.search(n)


def exclusion_reason(text):
    """Why a phrase that looks like an area match is not one; None when it is not dropped."""
    n = _norm(text)
    for o, why in OUTSIDE.items():
        if re.search(rf"(?<![a-z0-9]){re.escape(o)}(?![a-z0-9])", n):
            return why
    loose = {name for name, _ in _scan(text, strict=False)}
    strict = {name for name, _ in _scan(text)}
    for word in ("westminster", "barking"):
        if word in loose and word not in strict:
            return REASONS[word]
    if loose and (STAFFY.search(n) is None or OTHER_BREED.search(n)):
        return REASONS["breed"]
    return None


def use_of(volume):
    if isinstance(volume, int) and volume >= H3_MIN:
        return "h3"
    if isinstance(volume, int) and volume >= FAQ_MIN:
        return "faq"
    return "line"


USE_LABEL = {"h3": "Own H3",
             "faq": "Delivery copy + one FAQ answer",
             "line": "“We deliver across London, including …” line, if at all"}


def _load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _research_dir(board, root):
    for s in board.get("meta", {}).get("sources", []):
        p = str(s.get("path", ""))
        if p.startswith("docs/research/"):
            return root / pathlib.PurePosixPath(p).parent
    return root / "docs/research" / board["meta"]["slug"]


def keyword_rows(board, root=ROOT):
    """The response file's items as [(keyword, volume|None)], or None when it is not held."""
    doc = _load(root / "data/queries/raw" / board["meta"]["slug"] / RESPONSE)
    if not isinstance(doc, dict) or not isinstance(doc.get("items"), list):
        return None
    out = []
    for it in doc["items"]:
        kw = str(it.get("keyword", "")).strip().lower()
        vol = (it.get("keyword_info") or {}).get("search_volume")
        if kw:
            out.append((kw, vol if isinstance(vol, int) else None))
    return out


def _strings(node, key=None):
    """Every (key, string) in a JSON tree."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _strings(v, k)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v, key)
    elif isinstance(node, str):
        yield key, node


def areas(board, root=ROOT):
    root = pathlib.Path(root)
    rows = {}

    def row(area, borough):
        return rows.setdefault(area, {"area": area, "borough": borough, "keywords": [],
                                      "total_volume": None, "seen_in": []})

    def seen(r, src):
        if src not in r["seen_in"]:
            r["seen_in"].append(src)

    def add_kw(r, kw, vol):
        if all(k["kw"] != kw for k in r["keywords"]):
            r["keywords"].append({"kw": kw, "volume": vol})

    kws = keyword_rows(board, root) or []
    volume_of = {_norm(k): v for k, v in kws}
    for kw, vol in kws:
        if not is_staffy(kw):
            continue
        for area, borough in lookup(kw):
            r = row(area, borough)
            add_kw(r, kw, vol)
            seen(r, KEYWORD_SOURCE)

    raw = root / "data/queries/raw" / board["meta"]["slug"]
    research = _research_dir(board, root)
    files = [(raw / f, False) for f in SCANNED_RAW] + [(research / f, True) for f in SCANNED_RESEARCH]
    for path, is_list in files:
        doc = _load(path)
        if doc is None:
            continue
        rel = path.relative_to(root).as_posix()
        for key, s in _strings(doc):
            if s.startswith(("http://", "https://")):
                u = urlsplit(s)
                text = u.path.replace("-", " ").replace("_", " ").replace("/", " ")
                if not is_staffy(text):
                    continue
                for area, borough in lookup(text):
                    seen(row(area, borough), f"{u.scheme}://{u.netloc}{u.path}")
                continue
            if not is_staffy(s):
                continue
            for area, borough in lookup(s):
                r = row(area, borough)
                seen(r, rel)
                if is_list and key in ("keyword", "term", "query"):
                    phrase = _norm(s)  # "barnet, london" and "barnet london" are one phrase
                    add_kw(r, phrase, volume_of[phrase] if phrase in volume_of else NOT_IN_DATA)

    for r in rows.values():
        ints = [k["volume"] for k in r["keywords"] if isinstance(k["volume"], int)]
        r["total_volume"] = sum(ints) if ints else None
    return sorted(rows.values(), key=lambda r: (-(r["total_volume"] or -1), r["area"]))


def not_shown(board, root=ROOT):
    """[(keyword, reason)] for every keyword-data phrase dropped as a false area match."""
    out = []
    for kw, _ in keyword_rows(board, root) or []:
        why = exclusion_reason(kw)
        if why:
            out.append((kw, why))
    return out


def london_wide(board, root=ROOT):
    """The top London-wide Staffy terms (no area named) with a volume, highest first."""
    rows = [(kw, v) for kw, v in keyword_rows(board, root) or []
            if isinstance(v, int) and is_staffy(kw) and "london" in _norm(kw).split()
            and not lookup(kw) and not exclusion_reason(kw)]
    return sorted(rows, key=lambda r: -r[1])[:LONDON_WIDE_TOP]


def _vol_cell(r):
    if isinstance(r["total_volume"], int):
        return str(r["total_volume"])
    if any(k["volume"] is None for k in r["keywords"]):
        return "none returned"
    return NOT_IN_DATA


def _kw_cell(r):
    if not r["keywords"]:
        return "— (area named by a ranking page, no keyword)"
    parts = []
    for k in r["keywords"]:
        v = k["volume"]
        parts.append(f"{k['kw']} ({v if isinstance(v, int) else 'no volume' if v is None else v})")
    return "; ".join(parts)


def _seen_cell(r):
    out = []
    for s in r["seen_in"]:
        if s == KEYWORD_SOURCE:
            out.append("keyword data")
        elif s.startswith(("http://", "https://")):
            u = urlsplit(s)
            out.append(f"ranking page {u.netloc.removeprefix('www.')}{u.path}")
        else:
            out.append(pathlib.PurePosixPath(s).name)
    return "; ".join(out)


def _names(rows):
    names = [r["area"] for r in rows]
    return ", ".join(names[:-1]) + f" and {names[-1]}" if len(names) > 1 else "".join(names)


def block(board, root=ROOT):
    kws = keyword_rows(board, root)
    rows = areas(board, root)
    lines = ["Which parts of the city this page could name, and the Staffy searches that name "
             "them. Areas come from a fixed list of the 32 London boroughs, the City, the compass "
             "areas (south east London and the like) and common towns mapped to their borough."]
    if kws is None:
        lines.append(f"Volumes: NOT FETCHED — no `{RESPONSE}` is held for this page, so every "
                     f"area below carries `{NOT_IN_DATA}`.")
    else:
        lines.append(f"Volumes are UK monthly Google searches from DataForSEO keyword data "
                     f"(`keyword_ideas`, UK, en), fetched {KEYWORD_FETCHED}: {len(kws)} rows held. "
                     f"An area seen only on a ranking page or in the keyword lists carries "
                     f"`{NOT_IN_DATA}`.")
    lines.append("")

    lines.append("**London as a whole** — the top London-wide Staffy terms, for comparison:")
    lines.append("")
    wide = london_wide(board, root)
    if wide:
        lines.append(md_table(["Keyword", "Monthly searches"], [[k, v] for k, v in wide]))
    else:
        lines.append("_NOT FETCHED — no London-wide Staffy term with a volume in the keyword data._")
    lines.append("")

    body = [[r["area"], r["borough"], _kw_cell(r), _vol_cell(r), _seen_cell(r),
             USE_LABEL[use_of(r["total_volume"])]] for r in rows]
    lines.append(md_table(["Area", "Borough", "Keywords found", "Monthly searches", "Where seen",
                           "Suggested use"], body) if body else "_No London area found in the data._")
    lines.append("")
    lines.append(f"**Suggested use rule:** ≥ {H3_MIN}/mo → its own H3; {FAQ_MIN}–{H3_MIN - 1} → named "
                 f"in the delivery section copy and one FAQ answer; below {FAQ_MIN} or no volume → "
                 f"mention only in a “We deliver across London, including …” line, if at all.")
    lines.append("")

    h3 = [r for r in rows if use_of(r["total_volume"]) == "h3"]
    faq = [r for r in rows if use_of(r["total_volume"]) == "faq"]
    rest = [r for r in rows if use_of(r["total_volume"]) == "line"]
    t = ["**Target:**"]
    if h3:
        t.append(f"give {_names(h3)} its own H3.")
    else:
        t.append(f"no area reaches {H3_MIN}/mo, so none gets its own H3.")
    if faq:
        vols = ", ".join(f"{r['area']} {r['total_volume']}/mo" for r in faq)
        t.append(f"Name {_names(faq)} in the delivery section copy and one FAQ answer ({vols}).")
    if rest:
        t.append(f"{_names(rest)} show no measurable volume — at most one “We deliver across "
                 f"London, including …” line.")
    if wide:
        best = max((r["total_volume"] for r in rows if isinstance(r["total_volume"], int)), default=None)
        t.append(f"The London-wide terms carry the volume (“{wide[0][0]}” {wide[0][1]}/mo"
                 + (f" against {best}/mo for the best area" if best is not None else "")
                 + "), so the page targets London as a whole and names areas only as delivery reach.")
    else:
        t.append("London-wide volume is NOT FETCHED, so the target rests on area presence only.")
    lines.append(" ".join(t))
    lines.append("")

    dropped = not_shown(board, root)
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
    print(block(json.loads(path.read_text(encoding="utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
