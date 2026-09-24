"""link_diversity — the system-gaps rules on a new page's links (Tasks 4 and 5).

Task 4, `external-links-six-diverse` (rules/links.md): a location, comparison or blog page
carries at least six external links, on at least six distinct registrable domains, drawn from
at least four source types. A link's source type is the `Source type` column of its row in
docs/reference/external-link-library.md — the allowlist `pageboard.validate_board` already
holds every external href to — so the type is written once, next to the URL, and not retyped
on every board.

The checks register on `family_rules`, so they bind the new pages only; the twelve pages built
before this build are never asked. A draft is WARNed (a record is boarded before its links are
complete); every status after draft FAILs.

`pageboard` imports `family_rules`, which imports this module at its foot, so `pageboard` may
still be half-initialised while this file loads. Every `PB.` reference is therefore inside a
function, never at module level.
"""
import pathlib
import re
from urllib.parse import urlsplit

import family_rules as FR
import pageboard as PB

# ── Task 4: external-link diversity ──────────────────────────────────────────────────────
SOURCE_TYPES = ("gov", "registry", "vet-charity", "welfare", "research", "local", "other")
# `other` is a legal type (a privacy regulator's policy page, a show) that counts toward the
# six links and the six domains but not toward the four source types.
DIVERSE_TYPES = frozenset(SOURCE_TYPES) - {"other"}
EXTERNAL_MIN, DOMAIN_MIN, SOURCE_TYPE_MIN = 6, 6, 4
EXTERNAL_CHECK = "external-links-six-diverse"

# Second levels under a two-letter country code that make a three-label registrable domain —
# the same set scripts/competitor_registry_check.py uses for root domains.
CC_SECOND_LEVELS = {"co", "org", "me", "ltd", "plc", "ac", "gov", "net", "sch", "com"}
# gov.uk is itself a public suffix, so `service.gov.uk` reads as a registrable domain of its
# own. It is GOV.UK's asset host, not a second publisher: a PDF there and a guidance page on
# www.gov.uk are one source. legislation.gov.uk (The National Archives) and a council's own
# domain are real second publishers and are NOT aliased.
DOMAIN_ALIASES = {"service.gov.uk": "gov.uk"}
_ROW = re.compile(r"^\|\s*(https?://[^\s|]+)\s*\|")


def status_severity(board):
    return "WARN" if board["meta"]["status"] == "draft" else "FAIL"


def registrable_domain(url):
    """The domain a link counts toward: `www.` dropped, a UK-style `x.org.uk` kept whole."""
    host = (urlsplit(url).hostname or "").lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    labels = host.split(".")
    if len(labels) >= 3 and len(labels[-1]) == 2 and labels[-2] in CC_SECOND_LEVELS:
        dom = ".".join(labels[-3:])
    else:
        dom = ".".join(labels[-2:])
    return DOMAIN_ALIASES.get(dom, dom)


def library_source_types(path=None):
    """{normalised URL: source type} for every row of the library table that names one.

    Parsed by column NAME, not position, so a later column added to the table does not
    shift the read. A row the header gives no `Source type` cell to is simply absent, and
    the library test reports it."""
    p = pathlib.Path(PB.EXTERNAL_LIBRARY if path is None else path)
    if not p.exists():
        return {}
    out, col = {}, None
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "URL":
            col = cells.index("Source type") if "Source type" in cells else None
            continue
        m = _ROW.match(line)
        if m and col is not None and col < len(cells) and cells[col]:
            out[PB.normalise_url(m.group(1))] = cells[col]
    return out


def external_links(board):
    """{normalised URL: first link record} across the page, so one URL cited in three
    sections counts once."""
    seen = {}
    for s in board["sections"]:
        for l in s["links"]["external"]:
            seen.setdefault(PB.normalise_url(l["href"]), l)
    return seen


def external_summary(board, types=None):
    types = library_source_types() if types is None else types
    links = external_links(board)
    by_url = {u: types.get(u, "untyped") for u in links}
    return {
        "links": len(links),
        "domains": sorted({registrable_domain(u) for u in links}),
        "source_types": sorted({t for t in by_url.values() if t in DIVERSE_TYPES}),
        "by_url": by_url,
    }


@FR.register
def external_diversity(board, ont):
    sev, s = status_severity(board), external_summary(board)
    if s["links"] < EXTERNAL_MIN:
        yield (EXTERNAL_CHECK, sev,
               f"{s['links']} distinct external link(s) — a {board['meta']['page_type']} page carries at "
               f"least {EXTERNAL_MIN} (rules/links.md external-links-six-diverse)")
    if len(s["domains"]) < DOMAIN_MIN:
        yield (EXTERNAL_CHECK, sev,
               f"{len(s['domains'])} distinct domain(s) ({', '.join(s['domains']) or 'none'}) — at least "
               f"{DOMAIN_MIN}; every gov.uk path is one domain")
    if len(s["source_types"]) < SOURCE_TYPE_MIN:
        yield (EXTERNAL_CHECK, sev,
               f"{len(s['source_types'])} source type(s) ({', '.join(s['source_types']) or 'none'}) — at "
               f"least {SOURCE_TYPE_MIN} of {', '.join(sorted(DIVERSE_TYPES))}, read from the library's "
               "Source type column")
