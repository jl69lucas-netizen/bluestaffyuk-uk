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
from family_rules import BUILT_BEFORE_SYSTEM_GAPS  # noqa: E402
from pageboard import slug_file  # noqa: E402  (the one key -> board filename rule)

TARGETS = ROOT / "tests/render/targets.json"
REBUILT = ROOT / "data/facts/rebuilt.json"
BOARDS = ROOT / "data/boards"
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
        assert "remove this entry when" in reason.lower(), (
            f"{page_type}: the reason must state its expiry ('remove this entry when …')")


def test_the_comparison_page_type_runs_every_family(targets):
    """Project 5 builds comparison pages; a page type added later with fewer families would
    make its first page the least-examined page on the site."""
    fams = targets["families_by_page_type"]
    assert "comparison" in fams
    assert sorted(fams["comparison"]) == sorted(set().union(*fams.values()))


def _board_file(key, boards):
    """Where pageboard keeps the board for a resolved key (`/` flattened by slug_file)."""
    return boards / (slug_file(key) + ".json")


def _rebuilt_gaps(keys, targets, boards=BOARDS):
    """(missing, wrong): rebuilt keys with no target at their route (or that are not slugs),
    and targets whose page_type disagrees with the page's own board record — or that have no
    board to agree with, unless the page predates the board system."""
    by_slug = {p["slug"]: p["page_type"] for p in targets["pages"]}
    missing, wrong = [], []
    for key in keys:
        try:
            key_, route = resolve_page(key, ROOT)
        except ValueError as e:
            missing.append(f"{key}: {e}")
            continue
        route = route or "index"
        if route not in by_slug:
            missing.append(f"{key} -> {route}")
            continue
        board = _board_file(key_, boards)
        if not board.is_file():
            if key_ not in BUILT_BEFORE_SYSTEM_GAPS:
                wrong.append(f"{key}: no board record — page type unverified")
            continue
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
    assert not wrong, "targets.json page_type disagrees with the board:\n" + "\n".join(wrong)


def _board(boards, key, page_type):
    boards.mkdir(parents=True, exist_ok=True)
    (boards / (key + ".json")).write_text(json.dumps({"meta": {"page_type": page_type}}), encoding="utf-8")


def test_a_rebuilt_city_page_resolves_to_its_route_and_is_caught_when_untargeted(tmp_path):
    """The predicate on the key shape project 5 adds: a bare city key resolves through
    data/page-map.json to uk-locations/<slug>, and a city page with no target is named.
    Synthetic targets and boards, so building Hull in project 5 cannot turn this red."""
    _board(tmp_path, "index", "home")
    targets = {"pages": [{"slug": "index", "page_type": "home"}]}
    missing, wrong = _rebuilt_gaps(["blue-staffy-puppies-hull", "index"], targets, tmp_path)
    assert missing == ["blue-staffy-puppies-hull -> uk-locations/blue-staffy-puppies-hull"]
    assert wrong == []


def test_a_full_route_key_is_checked_against_its_bare_key_board(tmp_path):
    """`uk-locations/<city>` and `<city>` are one page: the board is looked up under the key
    resolve_page returns, so a full-route key cannot skip the page-type comparison."""
    _board(tmp_path, "blue-staffy-puppies-hull", "for-sale")
    targets = {"pages": [{"slug": "uk-locations/blue-staffy-puppies-hull", "page_type": "location"}]}
    missing, wrong = _rebuilt_gaps(["uk-locations/blue-staffy-puppies-hull"], targets, tmp_path)
    assert missing == []
    assert wrong == ["uk-locations/blue-staffy-puppies-hull: targets.json says location, the board says for-sale"]
    _board(tmp_path, "blue-staffy-puppies-hull", "location")
    assert _rebuilt_gaps(["uk-locations/blue-staffy-puppies-hull"], targets, tmp_path) == ([], [])


def test_a_type_mismatch_with_the_live_board_is_named():
    """The `wrong` branch fires against a real board record."""
    targets = {"pages": [{"slug": "privacy-policy-uk", "page_type": "for-sale"}]}
    missing, wrong = _rebuilt_gaps(["privacy-policy-uk"], targets)
    assert missing == []
    assert len(wrong) == 1 and wrong[0].startswith("privacy-policy-uk: targets.json says for-sale")


def test_a_new_page_with_no_board_is_a_gap_not_a_silent_skip(tmp_path):
    """A project 5 page has a board by construction; one without is unverified, not fine.
    Only the twelve pages built before the board system may lack one."""
    targets = {"pages": [{"slug": "uk-locations/blue-staffy-puppies-hull", "page_type": "location"},
                         {"slug": "privacy-policy-uk", "page_type": "legal"}]}
    missing, wrong = _rebuilt_gaps(["blue-staffy-puppies-hull", "privacy-policy-uk"], targets, tmp_path)
    assert missing == []
    assert wrong == ["blue-staffy-puppies-hull: no board record — page type unverified"]


def test_every_page_built_before_the_board_gaps_has_its_board_today():
    """The frozen-page exemption above is a fallback, not the norm: all twelve boards exist."""
    absent = sorted(k for k in BUILT_BEFORE_SYSTEM_GAPS if not _board_file(k, BOARDS).is_file())
    assert not absent, "frozen pages with no board record: " + ", ".join(absent)


def test_a_key_that_is_not_a_slug_is_reported_not_raised():
    missing, wrong = _rebuilt_gaps(["../x"], {"pages": []})
    assert len(missing) == 1 and missing[0].startswith("../x: not a slug")
    assert wrong == []


def test_the_new_page_rule_is_family_rules_own(targets):
    """pages.spec.ts decides which pages a `new-pages` promotion blocks from
    `new_page_rule`; scripts/family_rules.py decides the same page-type, frozen-page and
    `_`-fixture question for the board rules. That part is one answer spelled twice (one side
    is TypeScript), so it is pinned here. The TS side then ADDS one condition family_rules
    does not need, because a board is already in hand there: the page must also be in
    data/facts/rebuilt.json or have an approved board (`or_board_approved`), so a legacy city
    page with neither stays advisory."""
    import family_rules as FR
    rule = targets["new_page_rule"]
    assert tuple(rule["page_types"]) == FR.NEW_FAMILY_PAGE_TYPES
    assert set(rule["built_before"]) == FR.BUILT_BEFORE_SYSTEM_GAPS
    prefix = rule["excluded_prefix"]
    assert prefix == "_"
    assert not FR.is_new_page(prefix + "demo") and FR.is_new_page("demo")
    assert rule["or_board_approved"] is True
