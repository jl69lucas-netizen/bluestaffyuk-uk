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
