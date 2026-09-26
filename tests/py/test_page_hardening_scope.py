"""`page_hardening_scan.py` reads what a project 5 page is made of (audit 18.1 / 18.2).

A scoped run resolved `src/pages/<slug>/index.astro` only, so `uk-locations/<city>` — a
dynamic route — scanned BaseLayout.astro and global.css and nothing else; the site sweep
globbed `src/components/*.astro` without recursing, so no `src/components/kit/**` file was
ever read; and `SPEC_MANDATED` named source-repo classes no BSUK component renders. The
harden sprint on every city page would have been a clean scan of two files."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import page_hardening_scan as H  # noqa: E402

KIT = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "src/components/kit").glob("*.astro"))


def test_a_city_page_scans_the_city_template_and_its_data():
    for slug in ("uk-locations/blue-staffy-puppies-hull", "blue-staffy-puppies-hull"):
        files = H.src_files([slug], root=str(ROOT))
        assert "src/pages/uk-locations/[slug].astro" in files, slug
        assert "data/locations.json" in files, slug          # the template's own import


def test_a_blog_post_and_a_puppy_page_scan_their_dynamic_templates():
    post = H.src_files(["how-to-choose-the-right-blue-staffy-puppy-for-your-family"], root=str(ROOT))
    assert "src/pages/[...post].astro" in post
    pup = H.src_files(["available-puppies/roman"], root=str(ROOT))
    assert "src/pages/available-puppies/[slug].astro" in pup


def test_a_static_page_still_wins_over_a_dynamic_sibling():
    files = H.src_files(["blue-staffy-health-uk"], root=str(ROOT))
    assert "src/pages/blue-staffy-health-uk/index.astro" in files
    assert "src/pages/[...post].astro" not in files


def test_the_site_sweep_reads_every_kit_component():
    files = set(H.src_files([], root=str(ROOT)))
    assert KIT and set(KIT) <= files, sorted(set(KIT) - files)


def test_a_dynamic_route_resolves_in_a_fixture_tree(tmp_path):
    (tmp_path / "src/pages/uk-locations").mkdir(parents=True)
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text(json.dumps([{"slug": "blue-staffy-puppies-x"}]))
    (tmp_path / "src/pages/uk-locations/[slug].astro").write_text(
        "---\nimport locations from '../../../data/locations.json';\n---\n<p/>\n")
    files = H.src_files(["uk-locations/blue-staffy-puppies-x"], root=str(tmp_path))
    assert "src/pages/uk-locations/[slug].astro" in files
    assert "data/locations.json" in files


def test_class_list_is_read_as_rendered():
    harvested, literal = H._rendered_classes(
        "<aside class:list={['kit-dial', cls]}><span class:list={['kit-chip', avail && 'ok']}>")
    assert {"kit-dial", "kit-chip", "ok"} <= harvested
    assert "kit-dial" not in literal          # the orphan half stays on plain class="…"


def test_spec_mandated_names_kit_classes_only():
    rendered = set()
    for rel in KIT:
        rendered |= H._rendered_classes((ROOT / rel).read_text(encoding="utf-8"))[0]
    assert H.SPEC_MANDATED and H.SPEC_MANDATED <= rendered, sorted(H.SPEC_MANDATED - rendered)
    for residue in ("doc-stack", "otA", "geo-pin", "chkB", "seam", "xsell", "vflags"):
        assert residue not in H.SPEC_MANDATED


def test_the_kit_renders_every_mandated_component_it_styles():
    H.findings.clear()
    H.check_class_drift([(rel, (ROOT / rel).read_text(encoding="utf-8")) for rel in KIT])
    errors = [f for f in H.findings if f["sev"] == "ERROR" and f["check"] == "markup-css-drift"]
    H.findings.clear()
    assert errors == []


def test_a_custom_property_name_is_not_css_math(tmp_path):
    """Reading the kit surfaced `calc(-1 * var(--space-4))` as invalid math: the `e-4` in the
    property NAME matched the no-space-minus pattern. A real missing space still fails."""
    css = tmp_path / "a.css"
    css.write_text(".a{margin-top:calc(-1 * var(--space-4));height:calc(450px - 2 * var(--space-6))}\n"
                   ".b{font-size:clamp(1.7rem,1.2rem+2.2vw,2.6rem)}\n")
    H.findings.clear()
    H.check_css_math([str(css)])
    lines = [f["line"] for f in H.findings if f["check"] == "css-math-spacing"]
    H.findings.clear()
    assert lines == [2]
