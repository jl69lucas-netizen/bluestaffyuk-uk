"""link_diversity — the system-gaps rules on a new page's links (Tasks 4 and 5).

Task 4, `external-links-six-diverse` (rules/links.md): a location, comparison or blog page
carries at least six external links, on at least six distinct registrable domains, drawn from
at least four source types. A link's source type is the `Source type` column of its row in
docs/reference/external-link-library.md — the allowlist `pageboard.validate_board` already
holds every external href to — so the type is written once, next to the URL, and not retyped
on every board.

Task 5, `anchor-type-variation` (rules/links.md): every link on such a page records its
`anchor_type` (exact, partial, lsi, natural, branded, naked-url); the in-copy internal anchors
use at least three types with at most two exact-match, and the external anchors at least three
types. Nav tiles are typed but do not count toward the mix. `anchor-reuse-sitewide`: an in-copy
internal anchor another board in data/boards/ already uses for the same route is refused — but
only when that board is at this board's status or later, so the first owner keeps its anchor
and a later draft that copies it is the one told to change; a page built before this build
always owns its anchors. Page-level repeats stay with
pageboard's existing `links-anchor-duplicate`.

The checks register on `family_rules`, so they bind the new pages only; the twelve pages built
before this build are never asked (though their anchors still count as owned by them). A draft
is WARNed (a record is boarded before its links are complete); every status after draft FAILs.

`pageboard` imports `family_rules`, which imports this module at its foot, so `pageboard` may
still be half-initialised while this file loads. Every `PB.` reference is therefore inside a
function, never at module level.
"""
import json
import pathlib
import re
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


# ── Task 5: anchor-type variation ────────────────────────────────────────────────────────
# One vocabulary for the three places that name anchor types: Rule 58's three strategies
# (exact, conversational, branded — `natural` is the conversational default) and the
# internal-link agent's Anchor Diversity Ledger rotation (exact → partial → LSI → natural),
# plus a bare URL shown as its own anchor.
ANCHOR_TYPES = ("exact", "partial", "lsi", "natural", "branded", "naked-url")
INTERNAL_TYPE_MIN, EXACT_MAX, EXTERNAL_TYPE_MIN = 3, 2, 3
ANCHOR_CHECK = "anchor-type-variation"
SITEWIDE_CHECK = "anchor-reuse-sitewide"
# meta.status in schema order: a board is only refused an anchor by a sibling at its own
# rank or later, so the first owner keeps it.
STATUS_RANK = {s: i for i, s in enumerate(("draft", "boarded", "approved", "built", "released"))}
# A page outside the new family (the twelve built before this build: `approved` in the record,
# but live) outranks every status, so it always owns its anchors.
ALWAYS_OWNS = len(STATUS_RANK)
# Resolved at call time, so a test can repoint it at a scratch directory.
BOARDS_DIR = None


def _route(href):
    """An internal href → the route it lands on, folded exactly as build_page_board.route_of()
    folds it (query and fragment dropped, surrounding whitespace stripped, one leading and one
    trailing slash, repeated slashes collapsed), so `/x`, `/x/?a=1` and `/x//#faq` are one
    target. None for an href that names a host — a scheme or a protocol-relative `//host/x`,
    which the schema's `^/` pattern lets through and route_of would fold to `/x/`, silently
    dropping the host: that is no internal route, so the reuse check leaves it out."""
    raw = str(href or "")
    parts = urlsplit(raw.strip())
    if parts.scheme or parts.netloc:
        return None
    path = urlsplit(raw).path.strip()
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path += "/"
    return re.sub(r"/{2,}", "/", path)


def anchor_key(text):
    """Case, whitespace, punctuation and curly apostrophes folded — pageboard.tokens(), the
    tokeniser its own `links-anchor-duplicate` check compares on."""
    return " ".join(PB.tokens(text))


def _placements(board):
    for s in board["sections"]:
        for kind in ("internal", "external"):
            for l in s["links"][kind]:
                yield s["id"], kind, l


def anchor_summary(board):
    """Counts by anchor type for the in-copy internal links (nav tiles excluded — a grid or a
    breadcrumb names its targets by title by nature) and for every external link, plus every
    link of either kind that carries no type."""
    out = {"internal": {}, "external": {}, "untyped": []}
    for sid, kind, l in _placements(board):
        t = l.get("anchor_type")
        if not t:
            out["untyped"].append((sid, kind, l["anchor"]))
            continue
        if kind == "internal" and l.get("nav"):
            continue
        out[kind][t] = out[kind].get(t, 0) + 1
    return out


@FR.register
def anchor_variation(board, ont):
    sev, s = status_severity(board), anchor_summary(board)
    for sid, kind, anchor in s["untyped"]:
        yield (ANCHOR_CHECK, sev,
               f"section {sid}: {kind} anchor {anchor!r} carries no anchor_type "
               f"({', '.join(ANCHOR_TYPES)})")
    if len(s["internal"]) < INTERNAL_TYPE_MIN:
        yield (ANCHOR_CHECK, sev,
               f"internal anchors use {len(s['internal'])} type(s) ({', '.join(sorted(s['internal'])) or 'none'}) "
               f"— at least {INTERNAL_TYPE_MIN} (Rule 58, the Anchor Diversity Ledger)")
    if s["internal"].get("exact", 0) > EXACT_MAX:
        exact = [f"{sid}: {l['anchor']!r}" for sid, kind, l in _placements(board)
                 if kind == "internal" and not l.get("nav") and l.get("anchor_type") == "exact"]
        yield (ANCHOR_CHECK, sev,
               f"{s['internal']['exact']} exact-match internal anchor(s) — at most {EXACT_MAX} per page "
               f"(Rule 58); retype all but {EXACT_MAX} of: {'; '.join(exact)}")
    if len(s["external"]) < EXTERNAL_TYPE_MIN:
        yield (ANCHOR_CHECK, sev,
               f"external anchors use {len(s['external'])} type(s) ({', '.join(sorted(s['external'])) or 'none'}) "
               f"— at least {EXTERNAL_TYPE_MIN}")


_SITE_MAP = {}   # {(boards dir, ((name, mtime_ns), …)): {(route, key): [(slug, rank), …]}}


def _site_map():
    """{(route, anchor key): [(slug, status rank), …]} over every page record in the boards
    directory, memoised on the directory and each file's (name, mtime_ns), so a board's
    checks (and its diversity line) do not re-read every sibling on every call, and an edited
    or added sibling is seen at once. A record that is not JSON, or has no meta.slug, raises PB.BoardError naming it."""
    d = pathlib.Path(BOARDS_DIR or (PB.ROOT / "data" / "boards"))
    files = sorted(d.glob("*.json"))
    key = (str(d.resolve()), tuple((p.name, p.stat().st_mtime_ns) for p in files))
    if key in _SITE_MAP:
        return _SITE_MAP[key]
    uses = {}
    for p in files:
        try:
            b = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise PB.BoardError(f"{p}: not valid JSON ({e})") from e
        if not isinstance(b, dict) or not isinstance(b.get("meta"), dict) or "slug" not in b["meta"]:
            raise PB.BoardError(f"{p}: not a board record (no meta.slug)")
        slug = b["meta"]["slug"]
        if slug.startswith("_"):
            continue
        rank = STATUS_RANK.get(b["meta"].get("status"), 0) if FR.applies(b) else ALWAYS_OWNS
        for _, kind, l in _placements(b):
            if kind != "internal" or l.get("nav"):
                continue
            route, akey = _route(l["href"]), anchor_key(l["anchor"])
            if route and akey:
                owners = uses.setdefault((route, akey), [])
                if slug not in (o for o, _ in owners):
                    owners.append((slug, rank))
    _SITE_MAP.clear()
    _SITE_MAP[key] = uses
    return uses


def sitewide_anchor_uses(exclude_slug=None, min_status=None):
    """{(route, anchor key): [slug, …]} for the in-copy internal links of every OTHER board in
    data/boards/ — the Anchor Diversity Ledger's "anchors in use" column, read from the
    records rather than grepped from dist/, so a board sees its siblings before either is
    built. `_`-prefixed records (the _demo fixture) are not pages and are skipped. With
    `min_status`, only boards at that status or later are listed."""
    floor = STATUS_RANK.get(min_status, 0)
    out = {}
    for k, owners in _site_map().items():
        slugs = [s for s, r in owners if s != exclude_slug and r >= floor]
        if slugs:
            out[k] = slugs
    return out


@FR.register
def anchor_reuse_sitewide(board, ont):
    """The first owner keeps its anchor. Between new-family boards a sibling counts only at this
    board's status or later, so an approved page is never failed by a draft that copied it (the
    draft is told instead) and two boards at the same status are both told. A page outside the
    family (the twelve built before this build) always counts, whatever this board's status."""
    meta = board["meta"]
    sev, uses = status_severity(board), sitewide_anchor_uses(meta["slug"], meta["status"])
    for sid, kind, l in _placements(board):
        if kind != "internal" or l.get("nav"):
            continue
        route = _route(l["href"])
        slugs = route and uses.get((route, anchor_key(l["anchor"])))
        if slugs:
            yield (SITEWIDE_CHECK, sev,
                   f"section {sid}: anchor {l['anchor']!r} → {_route(l['href'])} is already used for that "
                   f"target by {', '.join(slugs)} — pick an unused variation (Anchor Diversity Ledger)")


def diversity_line(board):
    """One line for the board's links block: counts by type, domains, source types and the
    verdict of the three link checks above."""
    # The verdict includes anchor-reuse-sitewide, which reads the SIBLING boards: a typed
    # board's rendered links block therefore depends on other records, and its committed
    # artifact goes stale when a sibling's anchors or status change, not only its own.
    a, e = anchor_summary(board), external_summary(board)
    fnd = (list(external_diversity(board, None)) + list(anchor_variation(board, None))
           + list(anchor_reuse_sitewide(board, None)))
    if not fnd:
        verdict = "PASS"
    else:
        verdict = f"{'FAIL' if any(f[1] == 'FAIL' for f in fnd) else 'WARN'} ({len(fnd)})"

    def fmt(counts):
        return ", ".join(f"{t} {counts[t]}" for t in ANCHOR_TYPES if t in counts) or "none"
    untyped = f" · untyped {len(a['untyped'])}" if a["untyped"] else ""
    return (f"Link diversity — internal anchors: {fmt(a['internal'])} · external anchors: "
            f"{fmt(a['external'])}{untyped} · external: {e['links']} link(s) on {len(e['domains'])} "
            f"domain(s) from {len(e['source_types'])} source type(s) "
            f"({', '.join(e['source_types']) or 'none'}) · {verdict}")


def shows_anchor_types(board):
    """Whether the board's links block carries the anchor-type column and the diversity line:
    on a page these rules bind, or on any record that already types an anchor."""
    return FR.applies(board) or any(l.get("anchor_type") for _, _, l in _placements(board))
