"""The fifteen components of a city page, in city-page order — the one list the London
component design pass is built on (spec docs/superpowers/specs/2026-09-27-london-component-
design-pass-design.md, "The 15 components").

Every tool of the pass reads this module rather than retyping the list: the ideas-index test,
the must-differ inventory, the canvas validator, the canvas builder and the city uniqueness
gate in scripts/pageboard.py. A second copy of a list is a copy that drifts.

`shapes` names the board shapes (src/lib/boardStyles.ts `SHAPES`) whose existing styles a new
variant must differ from. Two components have no board shape: the contents list is the kit's
PageNav, shipped in one arrangement, and the newsletter has no kit component at all. Their
must-differ rows come from `KIT_ONLY` below.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: (id, name, board shapes) in city-page order.
COMPONENTS = (
    ("hero", "Hero", ("hero",)),
    ("counter-strip", "Counter strip", ("stats",)),
    ("trust-strip", "Trust strip", ("trust",)),
    ("contents-list", "Contents list", ()),
    ("desktop-dial", "Desktop dial", ("dial",)),
    ("jump-links", "Mobile sticky jump links and sheet", ("strip", "sheet")),
    ("key-takeaways", "Key takeaways", ("takeaways",)),
    ("puppy-cards", "Puppy cards", ("puppies",)),
    ("tables", "Tables", ("table",)),
    ("video", "Video", ("video",)),
    ("image-text", "Image and text section", ("standard",)),
    ("reviews", "Reviews", ("reviews",)),
    ("faq-blocks", "FAQ blocks", ("faq",)),
    ("newsletter", "Newsletter", ()),
    ("contact-form", "Contact form", ("form",)),
)

COMPONENT_IDS = tuple(c[0] for c in COMPONENTS)
NAMES = {c[0]: c[1] for c in COMPONENTS}
SHAPES_OF = {c[0]: c[2] for c in COMPONENTS}
VARIANT_IDS = ("a", "b", "c")

#: The canonical axes a variant declares in its meta.json, and the closed vocabularies of
#: three of them. `layout` is a short free slug (the arrangement's own name); when a variant
#: IS an arrangement the inventory already lists, it uses that row's layout slug verbatim.
AXES = ("layout", "media", "density", "framing")
VOCAB = {
    "media": ("none", "left", "right", "top", "bottom", "background", "inline", "grid"),
    "density": ("compact", "regular", "airy"),
    "framing": ("plain", "band", "card", "rule", "inset", "bleed"),
}

#: Must-differ rows for the components a board shape does not cover (see the module doc).
KIT_ONLY = {
    "contents-list": [{
        "id": "PageNav",
        "name": "Shipped contents list: a wrapping row of pills, no heading (PageNav)",
        "axes": {"layout": "chip-row", "media": "none", "density": None, "framing": "plain"},
        "used_by": ["every rebuilt page (PageShell mounts it)"],
    }],
    "newsletter": [],
}

#: The kit component each canvas component is built as (the London component design pass,
#: Plan 2): one `"project": 5` row of data/design/components.json per city component, whatever
#: variant a city picked — the picked variant's design is what the component renders.
KIT_ID = {
    "hero": "city-hero",
    "counter-strip": "city-price-scale",
    "trust-strip": "city-trust-ledger",
    "contents-list": "city-contents",
    "desktop-dial": "city-dial",
    "jump-links": "city-jump-band",
    "key-takeaways": "city-takeaways",
    "puppy-cards": "city-puppy-sheet",
    "tables": "city-roster",
    "video": "city-video-panel",
    "image-text": "city-chapters",
    "reviews": "city-letter",
    "faq-blocks": "city-faq-ledger",
    "newsletter": "city-newsletter",
    "contact-form": "city-contact-lineup",
}

#: Where a city's canvas lives. One folder per city key, one sub-folder per component.
CANVAS_ROOT = ROOT / "design" / "city-canvas"


def variant_key(city, component, variant):
    """The global id of one canvas variant, e.g. `london/hero/b`. One id names one design
    across every city's pass, so a pick and a pool entry can be compared by id alone."""
    return f"{city}/{component}/{variant}"


def axis_distance(a, b):
    """How many of the four canonical axes two declarations differ on. An axis either side
    leaves unknown (None or absent) never counts as a difference: an unknown is not proof
    that two designs differ."""
    return sum(1 for k in AXES
               if a.get(k) is not None and b.get(k) is not None and a.get(k) != b.get(k))
