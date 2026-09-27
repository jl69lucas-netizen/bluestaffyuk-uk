"""An approved board's `global_cta` decides whether the footer's CTA band renders
(CAG parity audit D3; answer-board batch 2026-09-26-brief-parity-two-decisions-before-project-5, ruling (a)).

Every board records `brief.cta.global_cta`, and the board Artifact tells the breeder "the
site-wide CTA band is hidden on this page" when it says `hidden`. Eleven of the twelve
approved boards chose `hidden` — and src/components/kit/SiteFooterKit.astro rendered its
`.cta-band` on every page regardless, so eleven approved boards disagreed with their built pages.
PageShell now reads the page's approved record and passes `cta={false}` to the footer when
the record says `hidden`. A page with no approved board keeps the band.
"""
import json
import pathlib
import re

import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
BAND = re.compile(r'class="[^"]*\bcta-band\b')


def approved_boards():
    out = []
    for f in sorted((ROOT / "data/boards").glob("*.json")):
        if f.stem.startswith("_"):
            continue
        b = json.loads(f.read_text(encoding="utf-8"))
        if b.get("approval"):
            out.append((b["meta"]["slug"], b["brief"]["cta"]["global_cta"]))
    return out


def built(slug):
    """The built page of a board's slug through pageboard.built_page, so a city board (keyed by
    its bare slug) is looked for at dist/uk-locations/<slug>/index.html rather than skipped."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from pageboard import built_page
    return built_page(slug, dist=DIST)


def test_a_city_boards_built_page_is_looked_for_under_uk_locations():
    assert built("blue-staffy-puppies-for-sale-leeds") == (
        DIST / "uk-locations/blue-staffy-puppies-for-sale-leeds/index.html")
    assert built("index") == DIST / "index.html"


def test_there_are_approved_boards_of_both_kinds():
    kinds = {g for _, g in approved_boards()}
    assert kinds == {"hidden", "shown"}, kinds


@pytest.mark.parametrize("slug,global_cta", approved_boards())
def test_the_built_page_honours_its_boards_global_cta(slug, global_cta):
    page = built(slug)
    if not page.exists():
        # Only an UNBUILT page skips: the path comes from the same resolver the gates use, so a
        # built city page is always found and always tested.
        pytest.skip(f"{page.relative_to(ROOT)} is not built — run npm run build first")
    has_band = bool(BAND.search(page.read_text(encoding="utf-8")))
    assert has_band == (global_cta == "shown"), (slug, global_cta, has_band)


def test_a_page_with_no_board_keeps_the_band():
    page = DIST / "available-puppies/index.html"
    if not page.exists():
        pytest.skip("run npm run build first")
    assert BAND.search(page.read_text(encoding="utf-8"))


def test_the_footer_takes_the_flag_as_a_prop():
    src = (ROOT / "src/components/kit/SiteFooterKit.astro").read_text(encoding="utf-8")
    assert re.search(r"cta\s*=\s*true", src), "SiteFooterKit needs a `cta` prop defaulting to true"
    assert re.search(r"\{cta\s*&&", src), "the band must render only when `cta` is true"
    shell = (ROOT / "src/layouts/PageShell.astro").read_text(encoding="utf-8")
    assert "globalCtaShown" in shell and "<SiteFooterKit slot=\"footer\" cta={" in shell


# ---- Behaviour of src/lib/globalCta.ts itself (Task 7 review) -------------------------------
#
# The dist tests above only see today's twelve approved boards. These run the real TypeScript
# against fixture records: esbuild (already in node_modules for Astro/Vite) compiles the file
# with `import.meta.glob` defined to a global the Node driver fills in first, so the fixtures
# stand in for data/boards/ and nothing else about the module is stubbed.
import json as _json
import shutil
import subprocess
import sys

ESBUILD = ROOT / "node_modules/.bin/esbuild"
NODE = shutil.which("node")


def run_global_cta(tmp_path, records, pathnames):
    """{board stem: record}, [pathname] -> [globalCtaShown(pathname)] from the compiled TS."""
    if not ESBUILD.exists() or not NODE:
        pytest.skip("needs node and node_modules/.bin/esbuild (npm install)")
    out = tmp_path / "globalCta.mjs"
    subprocess.run(
        [str(ESBUILD), str(ROOT / "src/lib/globalCta.ts"), "--format=esm", f"--outfile={out}",
         "--define:import.meta.glob=globalThis.__bsukGlob", "--log-level=error"],
        check=True,
    )
    fixtures = {f"../../data/boards/{stem}.json": rec for stem, rec in records.items()}
    driver = (
        f"const recs = {_json.dumps(fixtures)};"
        "globalThis.__bsukGlob = () => recs;"
        f"const m = await import({_json.dumps(out.as_uri())});"
        f"console.log(JSON.stringify({_json.dumps(pathnames)}.map(p => m.globalCtaShown(p))));"
    )
    res = subprocess.run([NODE, "--input-type=module", "-e", driver],
                         check=True, capture_output=True, text=True)
    return _json.loads(res.stdout)


def _record(global_cta, approval=None, approval_previous=None):
    rec = {"approval": approval, "brief": {"cta": {"global_cta": global_cta}}}
    if approval_previous is not None:
        rec["approval_previous"] = approval_previous
    return rec


def test_a_reboarded_record_keeps_the_pick_in_force(tmp_path):
    # Under re-board `approval` is null and the old approval sits in `approval_previous`
    # (scripts/pageboard.py, scripts/board_approve.py; src/lib/pickedStyle.ts reads it the same
    # way). The page ships what the breeder last agreed to, so "hidden" still hides the band.
    got = run_global_cta(tmp_path, {
        "reboarded": _record("hidden", approval=None, approval_previous={"approved_at": "x"}),
        "never-approved": _record("hidden"),
        "approved": _record("hidden", approval={"approved_at": "x"}),
    }, ["/reboarded/", "/never-approved/", "/approved/", "/no-board/"])
    assert got == [False, True, False, True], got


def test_a_nested_route_finds_its_board_the_way_slug_file_names_it(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    from pageboard import slug_file
    stem = slug_file("uk-locations/blue-staffy-puppies-london")
    assert stem == "uk-locations--blue-staffy-puppies-london", stem
    got = run_global_cta(tmp_path, {stem: _record("hidden", approval={"approved_at": "x"})},
                         ["/uk-locations/blue-staffy-puppies-london/"])
    assert got == [False], got


def test_a_city_page_finds_its_board_under_the_bare_slug(tmp_path):
    # City boards are keyed by the bare slug (data/boards/<slug>.json, Known Issue 39), while
    # the page lives at /uk-locations/<slug>/. Both spellings are tried, flattened route first,
    # the way tests/render/lib/promotions.ts isNewPage does (Task 28a).
    got = run_global_cta(tmp_path, {
        "blue-staffy-puppies-for-sale-leeds": _record("hidden", approval={"approved_at": "x"}),
        "uk-locations--blue-staffy-puppies-london": _record("hidden", approval={"approved_at": "x"}),
        "blue-staffy-puppies-london": _record("shown", approval={"approved_at": "x"}),
    }, ["/uk-locations/blue-staffy-puppies-for-sale-leeds/",
        "/uk-locations/blue-staffy-puppies-london/"])
    assert got == [False, False], got


def test_only_a_city_route_falls_back_to_the_bare_slug(tmp_path):
    # The bare-segment fallback exists for city boards (Known Issue 39). A nested route
    # anywhere else must not pick up a top-level board that happens to share its last segment.
    got = run_global_cta(tmp_path, {
        "roman": _record("hidden", approval={"approved_at": "x"}),
        "blue-staffy-puppies-leeds": _record("hidden", approval={"approved_at": "x"}),
    }, ["/available-puppies/roman/", "/blog/blue-staffy-puppies-leeds/",
        "/uk-locations/blue-staffy-puppies-leeds/"])
    assert got == [True, True, False], got
