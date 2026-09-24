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


def applies(board):
    m = board["meta"]
    slug = m["slug"]
    return (m["page_type"] in NEW_FAMILY_PAGE_TYPES
            and slug not in BUILT_BEFORE_SYSTEM_GAPS
            and not slug.startswith("_"))


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
_BOARDED_OR_LATER = ("boarded", "approved", "built", "released")


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
           "`python3 scripts/keyword_variants.py <query-slug>` (the cache folder under "
           f"data/queries/raw/, e.g. {board['meta']['slug'].split('/')[-1]}) for a proposal "
           "from the cached query data")
