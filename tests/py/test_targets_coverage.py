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

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TARGETS = ROOT / "tests/render/targets.json"
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
    orphans = sorted(_declared(targets) - _used(targets))
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
