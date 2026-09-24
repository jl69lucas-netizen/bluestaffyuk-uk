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
from urllib.parse import urlsplit

import family_rules as FR
import link_library as LL
import pageboard as PB

# ── Task 4: external-link diversity ──────────────────────────────────────────────────────
SOURCE_TYPES = ("gov", "registry", "vet-charity", "welfare", "research", "local", "other")
# `other` is a legal type (a privacy regulator's policy page, a show) that counts toward the
# six links and the six domains but not toward the four source types.
DIVERSE_TYPES = frozenset(SOURCE_TYPES) - {"other"}
EXTERNAL_MIN, DOMAIN_MIN, SOURCE_TYPE_MIN = 6, 6, 4
EXTERNAL_CHECK = "external-links-six-diverse"

# Second levels under a two-letter country code that make a three-label registrable domain —
# the set scripts/competitor_registry_check.py uses for root domains, plus `nhs` and `police`
# (nhs.uk and police.uk are public suffixes: england.nhs.uk and cumbria.police.uk are
# publishers of their own).
CC_SECOND_LEVELS = {"co", "org", "me", "ltd", "plc", "ac", "gov", "net", "sch", "com", "nhs", "police"}
# Public suffixes that are not under a two-letter code, checked first: gov.wales is the Welsh
# Government, anglesey.gov.wales a council — two publishers, not one.
PUBLIC_SUFFIXES = {"gov.wales", "gov.scot"}
# gov.uk is itself a public suffix, so `service.gov.uk` reads as a registrable domain of its
# own. It is GOV.UK's asset host, not a second publisher: a PDF there and a guidance page on
# www.gov.uk are one source. legislation.gov.uk and a council's own domain are NOT aliased:
# each counts as a domain of its own here, though ontology_seed names the government as the
# organisation behind legislation.gov.uk.
DOMAIN_ALIASES = {"service.gov.uk": "gov.uk"}


def status_severity(board):
    return "WARN" if board["meta"]["status"] == "draft" else "FAIL"


def registrable_domain(url):
    """The domain a link counts toward: case folded, port and `www.` dropped, a UK-style
    `x.org.uk` kept whole, `x.gov.wales` kept apart from gov.wales. "" for a URL with no host
    (empty or relative); callers leave that out of the domain set."""
    host = (urlsplit(str(url or "")).hostname or "").lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    for suffix in PUBLIC_SUFFIXES:
        if host == suffix:
            return suffix
        if host.endswith("." + suffix):
            return host[: -len(suffix) - 1].split(".")[-1] + "." + suffix
    labels = host.split(".")
    if len(labels) >= 3 and len(labels[-1]) == 2 and labels[-2] in CC_SECOND_LEVELS:
        dom = ".".join(labels[-3:])
    else:
        dom = ".".join(labels[-2:])
    return DOMAIN_ALIASES.get(dom, dom)


def library_source_types(path=None):
    """{normalised URL: source type} for every row of the library table that names one.

    Read through link_library.library_table, the strict parser ontology_seed shares: by
    column NAME, so a later column does not shift the read, and a row whose cell count is
    not its header's raises rather than moving its type into the wrong cell. A row with an
    empty or absent `Source type` cell is simply left out, and the library test reports it."""
    p = pathlib.Path(PB.EXTERNAL_LIBRARY if path is None else path)
    return {PB.normalise_url(r["URL"]): r["Source type"]
            for r in LL.library_table(p) if r.get("Source type")}


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
        "domains": sorted({registrable_domain(u) for u in links} - {""}),
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
        by_domain = {}
        for u in s["by_url"]:
            by_domain.setdefault(registrable_domain(u), []).append(u)
        shared = "; ".join(f"{d}: {', '.join(us)}" for d, us in sorted(by_domain.items()) if d and len(us) > 1)
        yield (EXTERNAL_CHECK, sev,
               f"{len(s['domains'])} distinct domain(s) ({', '.join(s['domains']) or 'none'}) — at least "
               f"{DOMAIN_MIN}; every gov.uk path is one domain"
               + (f". Links sharing a domain — replace all but one: {shared}" if shared else ""))
    if len(s["source_types"]) < SOURCE_TYPE_MIN:
        idle = ", ".join(f"{u} ({t})" for u, t in s["by_url"].items() if t not in DIVERSE_TYPES)
        yield (EXTERNAL_CHECK, sev,
               f"{len(s['source_types'])} source type(s) ({', '.join(s['source_types']) or 'none'}) — at "
               f"least {SOURCE_TYPE_MIN} of {', '.join(sorted(DIVERSE_TYPES))}, read from the library's "
               "Source type column"
               + (f". Links that count toward no type: {idle}" if idle else ""))
