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

#: The kit component each PICKED variant is built as (the London component design pass, Plan 2;
#: the Task 7b review): one `"project": 5` row of data/design/components.json per variant, named
#: for it (london/hero/b "Litter filmstrip" is CityHeroFilmstrip). Working rule 16 forbids a
#: second city mounting the same pick, so a component is never "the city hero" — the next city's
#: picks become components of their own, added here beside London's, and mount through the city
#: layout's nav slots (src/layouts/CityShell.astro) without an edit to PageShell.
KIT_OF_VARIANT = {
    "london/hero/b": "city-hero-filmstrip",
    "london/counter-strip/c": "city-price-scale",
    "london/trust-strip/c": "city-trust-ledger",
    "london/contents-list/c": "city-contents-photo-index",
    "london/desktop-dial/c": "city-dial-photo-marker",
    "london/jump-links/a": "city-jump-stepper",
    "london/key-takeaways/a": "city-takeaways-ledger",
    "london/puppy-cards/b": "city-puppy-sheet",
    "london/tables/a": "city-roster",
    "london/video/c": "city-video-panel",
    "london/image-text/c": "city-chapters",
    "london/reviews/a": "city-letter",
    "london/faq-blocks/a": "city-faq-ledger",
    "london/newsletter/a": "city-newsletter-notice",
    "london/contact-form/b": "city-contact-lineup",
    # Manchester's picks (canvas HrFjMqHqr8W3tqTNsMt7wb, frozen 2026-10-07; Phase F Task 27):
    # each named for its picked variant; video and puppy-cards are "none" for this page.
    "manchester/hero/c": "city-feature-and-three",
    "manchester/counter-strip/b": "city-range-sheet",
    "manchester/trust-strip/b": "city-puppy-folder",
    "manchester/contents-list/b": "city-icon-rows",
    "manchester/desktop-dial/a": "city-numeral-rail",
    "manchester/jump-links/b": "city-question-bar",
    "manchester/key-takeaways/c": "city-tick-card",
    "manchester/tables/a": "city-photo-shelf",
    "manchester/image-text/c": "city-offset-sheet",
    "manchester/reviews/c": "city-three-plates",
    "manchester/faq-blocks/b": "city-rows-beside-a-photo",
    "manchester/newsletter/b": "city-postmarked-note",
    "manchester/contact-form/b": "city-photo-at-the-edge",
}

#: The pick a city records for a component its approved outline has no section for (the
#: Manchester page run, Phase F gap G4: no video, no puppy cards). It names no variant, so it
#: is never compared, pooled or built, and a board that mounts that component is refused.
NOT_USED = "none"

#: The kit component each piece INSIDE a section is built as, per board slug and subcomponent
#: id (the Manchester page run, Phase F gap G9). A piece names its kit id in the board's
#: optional `subcomponents[].component`; London's five pieces were approved before that field
#: existed, so their ids live here and London's record (and its approval hash) is never edited.
#: Each id is the data/design/components.json row whose `subcomponent` is that piece.
KIT_OF_SUBCOMPONENT = {
    "blue-staffy-puppies-london": {
        "byline": "city-signed-byline",
        "puppy-strip": "city-ticket-strip",
        "video-call-checklist": "city-look-listen-checklist",
        "london-places": "city-places-by-publisher",
        "london-map": "city-map-facade",
    },
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
