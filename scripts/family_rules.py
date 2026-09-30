"""family_rules — the board rules that bind the pages project 5 builds (location pages,
comparison pages and blog posts) and never the pages built before them.

System-gaps build, 2026-09-24. Each later task registers one check here with
`@register`; `pageboard.gate_findings` calls `findings()` once, so no rule of this build
adds a line to the shared gate beyond that one hook.

WHY A FROZEN SLUG LIST AND NOT `data/facts/rebuilt.json`. The user's ruling is that these
rules apply to the new pages only, "not on the already built/done pages". rebuilt.json
grows as project 5 builds pages, so reading it would exempt every new page the moment it
was built and the rules would stop holding on the pages they exist for. The twelve slugs
below are the pages built before this build (rebuilt.json at 9927710); the list never
grows, so nobody has to remember to edit it.
"""

import page_sections as PS   # the status order and the FAQ-block test, spelled once

NEW_FAMILY_PAGE_TYPES = ("location", "comparison", "blog")

BUILT_BEFORE_SYSTEM_GAPS = frozenset({
    "privacy-policy-uk",
    "thank-you-blue-staffy-puppies-journey",
    "uk-blue-staffy-breeders-contact",
    "index",
    "blue-staffy-pup-sale-uk",
    "buy-blue-staffy-puppies-uk",
    "buy-staffy-puppies-for-sale-uk",
    "blue-staffy-uk-breeders",
    "blue-staffy-health-uk",
    "uk-staffordshire-bull-terrier-guide",
    "uk-blue-staffy-puppy-buying-guide",
    "blue-staffy-blog-guides",
})

CHECKS = []


def register(fn):
    """A check takes (board, ont) and yields (check_id, severity, message) triples."""
    CHECKS.append(fn)
    return fn


# The other three new-page predicates narrow this one for their inputs: evidence_audit.is_new_page
# also needs a new-family type AND a slug in rebuilt.json (it judges built pages only);
# tests/render/lib/promotions.ts isNewPage (render_baseline.is_new_page) also needs a type and
# rebuilt OR an approved board (promotions block from approval on); measurement_ledger takes
# rebuilt.json rows through this predicate (it measures the ledger's pages only).
def is_new_page(board_or_slug):
    """True for a page built from project 5 on: a slug that is not one of the twelve frozen
    pages and not a `_`-prefixed fixture (`_demo`). Takes a board or a bare slug, so a script
    that knows only the slug (scripts/ingest_image.py) asks the same question as the gate."""
    if isinstance(board_or_slug, dict):
        board_or_slug = (board_or_slug.get("meta") or {}).get("slug")
    slug = board_or_slug or ""
    return bool(slug) and slug not in BUILT_BEFORE_SYSTEM_GAPS and not slug.startswith("_")


# ── The H5/H6 heading floor (user ruling 2026-09-30, STOP 2 of London) ────────────────────
#
# rules/headings.md `heading-hierarchy-outline-gate` item 3: at least 5 H5 and 5 H6 on every
# page. The 2026-09-09 evidence pass made that floor advisory (WARN) on the homepage and the
# location pages; the user's ruling at London's STOP 2 ("we did not port or follow the H1 to
# H6 rules per page, it's a standard rule") makes it a hard FAIL again on every page project 5
# builds. The homepage and the pre-rule location stubs keep the WARN, so no built page breaks.
# One predicate, read by scripts/pageboard.py (min-h5-h6), scripts/outline_matrix.py (the
# census) and scripts/final_page_audit.py (min_h5_5 / min_h6_5), so the three cannot drift.
H5H6_ADVISORY_PAGE_TYPES = ("home", "location")
_ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]


def has_page_record(slug):
    """True when the slug's last segment has a page board or an outline record on disk — the
    mark of a page built through the project 5 run. The data-driven location stubs have
    neither, so a built stub is still judged as a pre-rule page."""
    bare = (slug or "").strip("/").rsplit("/", 1)[-1]
    return bool(bare) and any((_ROOT / d / f"{bare}.json").exists()
                              for d in ("data/boards", "data/outlines"))


def h5h6_floor_severity(page_type, slug, *, record=True):
    """FAIL or WARN for the 5-H5 / 5-H6 floor. WARN only on a home or location page that is
    not a project 5 page (the frozen twelve, or a location stub with no board or outline).
    `record=True` says the caller is judging a board or outline record, which only a project 5
    page (or a frozen page's board) has; a caller reading dist/ passes `record=False` and the
    slug must then carry a record on disk to count as a project 5 page."""
    if page_type not in H5H6_ADVISORY_PAGE_TYPES:
        return "FAIL"
    bare = (slug or "").strip("/").rsplit("/", 1)[-1]
    new = (page_type in NEW_FAMILY_PAGE_TYPES and is_new_page(bare)
           and (record or has_page_record(bare)))
    return "FAIL" if new else "WARN"


def applies(board):
    m = board["meta"]
    return m["page_type"] in NEW_FAMILY_PAGE_TYPES and is_new_page(m["slug"])


def findings(board, ont):
    if not applies(board):
        return []
    out = []
    for fn in CHECKS:
        out.extend(fn(board, ont))
    return out


# ── System-gaps Task 1: keyword variations, related, co-occurring and similar terms ──────────
#
# The four types are optional in the schema, so the twelve built records keep their hashes;
# on a new-family page each must carry at least one term somewhere on the page. Page-wide,
# not per section: a variation belongs where it reads naturally, and a per-section floor
# would push four bolted-on terms into every FAQ and CTA block.
#
# FAIL from `boarded` on, WARN on a draft. A draft is written before the outline is placed,
# so failing it would make the board unreachable; once the breeder is shown the board the
# terms are part of what they approve, and a WARN there is a term nobody ever writes. The
# FAIL costs nothing to clear: scripts/keyword_variants.py proposes all four from the query
# files bsuk-query-augmentation already cached, with no paid call.
#
# The tuple is spelled here rather than imported: pageboard imports this module, so reading
# PB.OPTIONAL_KEYWORD_TYPES would be a circular import. tests/py/test_keyword_variants.py
# pins the two to each other.
KEYWORD_VARIANT_TYPES = ("variation", "related", "cooccurring", "similar")
STATUS_ORDER = PS.STATUS_ORDER
_BOARDED_OR_LATER = PS.statuses_from("boarded")


@register
def keyword_variants_filled(board, ont):
    missing = [k for k in KEYWORD_VARIANT_TYPES
               if not any(t.strip() for s in board["sections"] for t in s["keywords"].get(k, []))]
    if not missing:
        return
    sev = "FAIL" if board["meta"]["status"] in _BOARDED_OR_LATER else "WARN"
    yield ("keyword-variants-missing", sev,
           f"no section carries a {', '.join(missing)} keyword — a new location, comparison or "
           "blog page names at least one term of each type; run "
           "`python3 scripts/keyword_variants.py <board slug or query-cache folder>` (e.g. "
           f"{board['meta']['slug']}) for a proposal from the cached query data")


# ── Tasks 4 and 5 (system-gaps): external-link diversity and anchor types ───────────────
# Imported here; later tasks append after it. link_diversity registers its checks with
# `register` above.
import link_diversity  # noqa: E402,F401


# ── Task 6b (system-gaps): an approved outline never repeats a heading ─────────────────────
# The board-time half of `outline-provenance-gate` (rules/copy.md). The built-page half is
# scripts/outline_provenance_check.py, which reads dist/ and so cannot run at board time; a
# heading the outline carries twice would be built twice, so it is refused here, before the
# record can be approved. Cross-page collisions are already pageboard's `header-collision`.
import re as _re

_HEADING_TOKEN = _re.compile(r"[\w£$']+")   # keeps £, accented letters and digits


def _heading_key(text):
    return " ".join(_HEADING_TOKEN.findall((text or "").replace("’", "'").lower()))


@register
def outline_heading_repeat(board, ont):
    h1 = board.get("h1") or {}
    variants = h1.get("variants") or []
    pick = h1.get("pick") if h1.get("pick") is not None else h1.get("recommended")
    # Each heading is (place, text); the place names the section so the message says where.
    heads = [("H1", variants[pick])] if isinstance(pick, int) and 0 <= pick < len(variants) else []

    def walk(nodes, sid):
        for n in nodes or []:
            level = n.get("level")
            heads.append((f"section {sid!r} H{level if level is not None else '?'}", n.get("heading")))
            walk(n.get("children"), sid)
    h1_key = _heading_key(heads[0][1]) if heads else ""
    for s in board.get("sections", []):
        sid = s.get("id")
        # A hero whose heading IS the H1 renders the H1 alone (measured on dist/ 2026-09-24:
        # the blog hub, contact and thank-you pages), so that pair is one heading, not two.
        if not (s.get("shape") == "hero" and _heading_key(s.get("heading")) == h1_key):
            heads.append((f"section {sid!r} H2", s.get("heading")))
        if not PS.is_faq_block(s):   # an FAQ tree holds data/faq.json row ids, not headings
            walk(s.get("tree"), sid)
    seen = {}
    for place, text in heads:
        key = _heading_key(text)
        if key:
            seen.setdefault(key, []).append(f"{place} {text!r}")
    for key, where in seen.items():
        if len(where) > 1:
            yield ("outline-heading-repeat", "FAIL",
                   f"the outline carries one heading {len(where)} times: {', '.join(where)}")

# ── Task 10: an image under every body heading (user ruling G1) ─────────────────────────
# The logic is in scripts/image_rules.py; imported here, at the bottom, so that module can
# never import this one half-built.
import image_rules as IR  # noqa: E402

# The new-page rules that can only pass AFTER approval (an image drafted and approved by sha,
# a folder file ingested, a generated file published): approval never waits on them, the build
# gate does. Read by scripts/board_approve.py (which refuses on every other FAIL) and by board
# block 7b, so the two can never disagree. image-pick-invalid is among them, and that is safe:
# board_approve's validate_image_picks refuses a malformed or wrong-kind img: pick first.
APPROVAL_EXEMPT = frozenset(IR.BUILD_CHECK_IDS)


@register
def image_every_body_heading(board, ont):
    """Every body H2 and body H3 plans an image slot, the hero a photo, and each slot says
    where its image comes from; an approved record names an image for every generated slot."""
    return IR.slot_findings(board)


@register
def image_build_ready(board, ont):
    """On an approved record every slot resolves to a file the build may use: a served file,
    an ingested folder file, or the generated image whose bytes the breeder approved."""
    return IR.build_findings(board)


# ── parity build Task 18: the primary keyword's placement (CAG §7a.7, §7d.6) ─────────────────
# The logic and the ours-vs-top-5 table are scripts/keyword_metrics.py; imported at the
# bottom for the same reason image_rules is. keyword_metrics imports pageboard only inside
# its functions, so this import can never see a half-built module.
import keyword_metrics as KM  # noqa: E402


@register
def keyword_placement(board, ont):
    """title-front-load (FAIL from `boarded`, WARN on a draft) and first-100-words (FAIL on a
    rebuilt, built page)."""
    return KM.findings(board)


# ── parity build Task 19: the geo token and two-keyword headers (audit rows 7b.9, 12.6) ─────
# Advisory: WARN at every status. Header terms match as the title gate reads them
# (keyword_metrics.norm_phrase_count: query_augment.normalise folds plurals and synonyms and
# small words drop), so "Blue Staffy Puppy Care" carries "blue staffy puppies" and
# "Staffies in Leeds" carries "staffy leeds".
import json as _json  # noqa: E402
import pathlib as _pathlib  # noqa: E402

import evidence_audit as EA  # noqa: E402  (stdlib + _slugs/_html only: no cycle)

SETTINGS_PATH = _pathlib.Path(__file__).resolve().parents[1] / "data" / "settings.json"
# The brand carries "UK" but names no place: it is stripped before any geo match.
BRAND_NAME = _re.compile(r"blue[\s-]*staffy[\s-]*uk(?:\.co\.uk)?", _re.I)
DOTTED_UK = _re.compile(r"\bU\.K\.?", _re.I)
NATIONAL_GEO = "UK"
H2_LIST_MAX, H2_TEXT_MAX = 4, 40


def _home_geo():
    """The breeder's own place (data/settings.json address: city, region). It never
    satisfies another city's page: a Manchester page that says only Carlisle is not local."""
    try:
        addr = _json.loads(SETTINGS_PATH.read_text(encoding="utf-8")).get("address") or {}
    except (OSError, ValueError):
        return []
    return [addr[k] for k in ("city", "region") if addr.get(k)]


def page_city(board):
    """The city a location board is about (evidence_audit.city_for over data/locations.json),
    or None for a national page or a slug the table does not list."""
    slug = board["meta"]["slug"]
    return EA.city_for(slug if slug.startswith("uk-locations/") else "uk-locations/" + slug)


def _geo_text(text):
    return DOTTED_UK.sub("UK", BRAND_NAME.sub(" ", text or ""))


def names_geo(text, city):
    """True when `text` names the page's geo: its own city (evidence_audit.city_pattern) on a
    city page, UK on a national one. The brand never counts; U.K. is UK. A section's planned
    `geo` terms are not accepted on their own: the only one that could count is the city
    itself, which the city pattern already matches."""
    t = _geo_text(text)
    if city:
        return bool(_re.search(EA.city_pattern(city), t, _re.I))
    return KM.norm_phrase_count(NATIONAL_GEO, t) > 0


def _short(text, n):
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[:n - 1].rstrip() + "…"


def _h2_list(headings):
    shown = ", ".join(repr(_short(h, H2_TEXT_MAX)) for h in headings[:H2_LIST_MAX])
    more = len(headings) - H2_LIST_MAX
    return (shown or "none") + (f" … +{more} more" if more > 0 else "")


@register
def geo_token(board, ont):
    """A location page names its geo — its own city, or UK on a national page — in at least
    one body H2 and in the picked (or recommended) meta description: the token that decides a
    local query's retrieval."""
    if board["meta"]["page_type"] != "location":
        return
    import pageboard as PB   # lazy, as keyword_metrics does: pageboard imports this module
    city = page_city(board)
    want = f"the page's city {city!r}" if city else f"{NATIONAL_GEO!r} (a national page)"
    home = [h for h in _home_geo() if not (city and names_geo(h, city))]

    def home_note(texts):
        hit = [h for h in home if any(_re.search(EA.city_pattern(h), t, _re.I) for t in texts)]
        return (f"; {', '.join(hit)} {'is' if len(hit) == 1 else 'are'} the breeder's home "
                "and does not count"
                if hit else "")

    heads = [s["heading"] for s in PS.body_sections(board)]
    if not any(names_geo(h, city) for h in heads):
        yield ("geo-token-missing", "WARN",
               f"no body H2 names {want} — H2s read: {_h2_list(heads)}{home_note(heads)}")
    _, desc = PB.meta_pick(board)
    if not names_geo(desc, city):
        yield ("geo-token-missing", "WARN",
               f"the picked (or recommended) meta description does not name {want}"
               f"{home_note([desc])}")


def _keyword_types(section):
    """{type: [terms]} for the section's header keyword types: `brand` left out, blank terms
    dropped, and a type whose normalised terms repeat an earlier type's counted once."""
    seen, out = set(), {}
    for k, vals in section["keywords"].items():
        if k == "brand":
            continue
        terms = [t for t in vals if KM.norm_words(t)]
        key = frozenset(tuple(KM.norm_words(t)) for t in terms)
        if key and key not in seen:
            seen.add(key)
            out[k] = terms
    return out


@register
def two_keyword_header(board, ont):
    """Every body section carries at least two keyword types, and its H2 names a term of at
    least one of them (the SEO master checklist's Two-Keyword Headers)."""
    for s in PS.body_sections(board):
        types = _keyword_types(s)
        if len(types) < 2:
            yield ("two-keyword-header", "WARN",
                   f"section {s['id']!r} carries {len(types)} keyword type"
                   f"{'' if len(types) == 1 else 's'} ({', '.join(types) or 'none'}) — a body "
                   "header is planned on two")
            continue
        if not any(KM.norm_phrase_count(t, s["heading"]) for ts in types.values() for t in ts):
            yield ("two-keyword-header", "WARN",
                   f"section {s['id']!r}: the H2 {s['heading']!r} carries none of its own "
                   f"{', '.join(types)} terms")
