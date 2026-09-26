"""Task 16 Step 1, encoded permanently.

The render harness's `tests/render/targets.json` decides which invariant families examine
which pages. Two silent failure modes live here and neither is caught by the harness itself
when the file is edited between runs:

  * a page type declared in `families_by_page_type` with no target page in `pages` — every
    family wired only to that page type then examines zero real pages while still reporting
    as a shipped gate;
  * a family wired to no page type at all — the meta gate fails on this by design, and this
    test states the same rule in Python so an edit is caught before Playwright is started.

`for-sale` and the contact page are named explicitly: FORM's only real examination site is
the contact page, and `for-sale` is the commercial cluster the blocking families exist for.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from _slugs import resolve_page  # noqa: E402

TARGETS = ROOT / "tests/render/targets.json"
REBUILT = ROOT / "data/facts/rebuilt.json"
DIST = ROOT / "dist"
CONTACT_SLUG = "uk-blue-staffy-breeders-contact"


@pytest.fixture(scope="module")
def targets():
    return json.loads(TARGETS.read_text(encoding="utf-8"))


def _declared(t):
    return set(t["families_by_page_type"])


def _used(t):
    return {p["page_type"] for p in t["pages"]}


def test_there_are_target_pages_at_all(targets):
    assert targets["pages"], (
        "`pages` is empty — every coverage assertion below is vacuously true against an "
        "empty target list, so this is the one that has to come first"
    )
    assert targets["families_by_page_type"], "families_by_page_type is empty"


def test_every_declared_page_type_has_at_least_one_target_page(targets):
    orphans = sorted(_declared(targets) - _used(targets) - set(targets.get("pending_page_types", {})))
    assert not orphans, (
        f"page types declared in families_by_page_type with no page in `pages`: {orphans} — "
        "every family wired only to these examines zero real pages"
    )


def test_every_target_page_type_is_mapped_to_families(targets):
    unmapped = sorted(_used(targets) - _declared(targets))
    assert not unmapped, (
        f"target pages whose page_type has no families_by_page_type entry: {unmapped}"
    )


def test_every_family_is_wired_to_at_least_one_reachable_page_type(targets):
    mapping = targets["families_by_page_type"]
    reachable = {f for pt in _used(targets) for f in mapping.get(pt, [])}
    declared_families = {f for fams in mapping.values() for f in fams}
    dangling = sorted(declared_families - reachable)
    assert not dangling, f"families wired to no page type that has a real page: {dangling}"


def test_the_for_sale_cluster_has_a_target_page(targets):
    for_sale = [p["slug"] for p in targets["pages"] if p["page_type"] == "for-sale"]
    assert for_sale, "for-sale has no target page; the meta gate fails by design when so"


def test_the_contact_page_is_a_target_so_form_examines_a_real_page(targets):
    slugs = {p["slug"] for p in targets["pages"]}
    assert CONTACT_SLUG in slugs, (
        f"{CONTACT_SLUG} is not a target page — FORM is wired to every page type but only "
        "the contact page carries a real inquiry form, so FORM would examine zero real pages"
    )


@pytest.mark.skipif(not DIST.is_dir(), reason="dist/ is not built")
def test_every_target_page_exists_in_the_built_site(targets):
    missing = []
    for page in targets["pages"]:
        slug = page["slug"]
        built = DIST / "index.html" if slug == "index" else DIST / slug / "index.html"
        if not built.is_file():
            missing.append(f"{slug} -> {built.relative_to(ROOT)}")
    assert not missing, "target pages with no built page:\n" + "\n".join(missing)


# ── parity plan Task 10: project 5 pages are render targets ─────────────────────────────────
def test_a_pending_page_type_is_declared_unbuilt_and_says_when_it_ends(targets):
    """`pending_page_types` is the one way to declare a page type before its first page
    exists (project 5's comparison pages). It expires by itself: the moment a target of that
    type is added, the entry is a lie and this fails until it is removed."""
    for page_type, reason in targets.get("pending_page_types", {}).items():
        assert page_type in targets["families_by_page_type"], f"{page_type} is pending but wired to nothing"
        assert page_type not in _used(targets), (
            f"{page_type} has a target page now — remove it from pending_page_types")
        assert "remove this entry when" in reason.lower(), page_type


def test_the_comparison_page_type_runs_every_family(targets):
    """Project 5 builds comparison pages; a page type added later with fewer families would
    make its first page the least-examined page on the site."""
    fams = targets["families_by_page_type"]
    assert "comparison" in fams
    assert sorted(fams["comparison"]) == sorted(fams["location"])


def _rebuilt_gaps(keys, targets):
    """(missing, wrong): rebuilt keys with no target at their route, and targets whose
    page_type disagrees with the page's own board record."""
    by_slug = {p["slug"]: p["page_type"] for p in targets["pages"]}
    missing, wrong = [], []
    for key in keys:
        route = resolve_page(key, ROOT)[1] or "index"
        if route not in by_slug:
            missing.append(f"{key} -> {route}")
            continue
        board = ROOT / "data/boards" / (key + ".json")
        if board.exists():
            want = json.loads(board.read_text(encoding="utf-8"))["meta"]["page_type"]
            if by_slug[route] != want:
                wrong.append(f"{route}: targets.json says {by_slug[route]}, the board says {want}")
    return missing, wrong


def test_every_rebuilt_page_is_a_render_target_of_its_board_type(targets):
    """A page written from an approved board is only measured at 375/768/1280 if it is in
    `pages`, and nothing added one automatically: a project 5 page left out would be judged
    by no blocking render check at all, and every check would still read green."""
    missing, wrong = _rebuilt_gaps(json.loads(REBUILT.read_text(encoding="utf-8")), targets)
    assert not missing, ("rebuilt pages with no render target — add each to "
                         "tests/render/targets.json `pages`:\n" + "\n".join(missing))
    assert not wrong, "\n".join(wrong)


def test_a_rebuilt_city_page_resolves_to_its_route_and_is_caught_when_untargeted(targets):
    """The predicate on the key shape project 5 adds: a bare city key resolves through
    data/page-map.json to uk-locations/<slug>, and a city page with no target is named."""
    missing, wrong = _rebuilt_gaps(["blue-staffy-puppies-hull", "index"], targets)
    assert missing == ["blue-staffy-puppies-hull -> uk-locations/blue-staffy-puppies-hull"]
    assert wrong == []
    assert _rebuilt_gaps(["blue-staffy-puppies-birmingham"], targets) == ([], [])
