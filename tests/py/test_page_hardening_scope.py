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


# ── Task 15 review ────────────────────────────────────────────────────────────────────────────
import subprocess  # noqa: E402


def test_a_pageshell_page_follows_imports_at_any_depth():
    """page → PageShell (layout) → SiteHeaderKit → PageNav / Mark: two fixed import levels
    never reached the kit's own imports."""
    files = H.src_files(["blue-staffy-health-uk"], root=str(ROOT))
    assert "src/components/kit/PageNav.astro" in files
    assert "src/components/kit/Mark.astro" in files


def test_an_import_cycle_terminates(tmp_path):
    (tmp_path / "src/pages/p").mkdir(parents=True)
    (tmp_path / "src/components").mkdir(parents=True)
    (tmp_path / "src/pages/p/index.astro").write_text("---\nimport A from '../../components/A.astro';\n---\n")
    (tmp_path / "src/components/A.astro").write_text("---\nimport B from './B.astro';\n---\n")
    (tmp_path / "src/components/B.astro").write_text("---\nimport A from './A.astro';\n---\n")
    files = H.src_files(["p"], root=str(tmp_path))
    assert {"src/components/A.astro", "src/components/B.astro"} <= set(files)


def _run(*slugs):
    return subprocess.run([sys.executable, "scripts/page_hardening_scan.py", *slugs],
                          cwd=ROOT, capture_output=True, text=True)


def test_an_unknown_page_exits_2():
    for slug in ("no-such-page", "uk-locations/blue-staffy-puppies-nowheresville"):
        r = _run(slug)
        assert r.returncode == 2, (slug, r.returncode, r.stdout[-300:])
        assert f"no built page for {slug}" in r.stdout + r.stderr


def test_css_math_reads_balanced_parentheses(tmp_path):
    css = tmp_path / "a.css"
    css.write_text(".a{width:calc(var(--a)+var(--b))}\n"
                   ".b{width:calc(var(--s-4)-2px)}\n"
                   ".c{width:calc(var(--a) + var(--b))}\n")
    H.findings.clear()
    H.check_css_math([str(css)])
    lines = [f["line"] for f in H.findings if f["check"] == "css-math-spacing"]
    H.findings.clear()
    assert lines == [1, 2]


def test_class_list_forms():
    h, _ = H._rendered_classes("<a class:list={ ['sp'] }><b class:list={{'obj': x}}>"
                               "<i class:list={{active: on, 'is-x': y}}>")
    assert {"sp", "obj", "active", "is-x"} <= h


def test_a_page_restyling_an_imported_kit_class_is_not_drift(tmp_path, monkeypatch):
    (tmp_path / "src/pages/p").mkdir(parents=True)
    (tmp_path / "src/components/kit").mkdir(parents=True)
    (tmp_path / "src/components/kit/Hero.astro").write_text(
        "<section class:list={['kit-hero', cls]}></section>\n<style>.kit-hero{display:grid}</style>\n")
    page = ("---\nimport Hero from '../../components/kit/Hero.astro';\n---\n<Hero />\n"
            "<style>\n.kit-hero{margin:0}\n</style>\n")
    (tmp_path / "src/pages/p/index.astro").write_text(page)
    monkeypatch.chdir(tmp_path)
    H.findings.clear()
    H.check_class_drift([("src/pages/p/index.astro", page)])
    errors = [f for f in H.findings if f["sev"] == "ERROR"]
    H.findings.clear()
    H.check_class_drift([("src/pages/q.astro", "<p/>\n<style>\n.kit-hero{margin:0}\n</style>\n")])
    orphan = [f for f in H.findings if f["sev"] == "ERROR"]
    H.findings.clear()
    assert errors == []
    assert orphan, "a page with no kit import styling .kit-hero is still an ERROR"


def test_data_and_script_files_are_not_css_checked():
    H.findings.clear()
    assert H.css_checked(["data/locations.json", "src/lib/site.ts", "a.js", "x.astro", "y.css"]) \
        == ["x.astro", "y.css"]


def test_a_city_with_its_own_astro_file_scans_that_file_not_the_scaffold(tmp_path):
    """Astro routes `src/pages/uk-locations/<city>.astro` ahead of `[slug].astro` (a static
    route beats a dynamic one), so a city with its own file is built from it. page_source()
    tried `<route>/index.astro` and then the `[slug].astro` scaffold, never `<route>.astro`:
    London's scoped run scanned the scaffold, which does not render London, and passed a page
    it never read. A city without its own file still resolves to the scaffold."""
    (tmp_path / "src/pages/uk-locations").mkdir(parents=True)
    (tmp_path / "data").mkdir()
    (tmp_path / "data/locations.json").write_text(json.dumps(
        [{"slug": "blue-staffy-puppies-own"}, {"slug": "blue-staffy-puppies-plain"}]))
    (tmp_path / "src/pages/uk-locations/[slug].astro").write_text("<p/>\n")
    (tmp_path / "src/pages/uk-locations/blue-staffy-puppies-own.astro").write_text("<p/>\n")
    for slug in ("blue-staffy-puppies-own", "uk-locations/blue-staffy-puppies-own"):
        assert H.page_source(slug, root=str(tmp_path)) == \
            "src/pages/uk-locations/blue-staffy-puppies-own.astro", slug
        files = H.src_files([slug], root=str(tmp_path))
        assert "src/pages/uk-locations/[slug].astro" not in files, slug
    assert H.page_source("blue-staffy-puppies-plain", root=str(tmp_path)) == \
        "src/pages/uk-locations/[slug].astro"


def test_london_scans_its_own_source_in_the_real_tree():
    files = H.src_files(["/uk-locations/blue-staffy-puppies-london/"], root=str(ROOT))
    assert "src/pages/uk-locations/blue-staffy-puppies-london.astro" in files
    assert "src/pages/uk-locations/[slug].astro" not in files


# ── markup-css-drift: three ways a kit component renders a class the harvest missed ──────────
# London's scan (2026-10-04, once it read the city's own source) reported kit-btn, k-lead, k-no,
# k-note and bare as "styled but never rendered"; all five are in dist/'s London page (2, 8, 7,
# 7 and 1 times). Reductions of the three components, verbatim in the class plumbing.
BUTTON_CONST = """---
// the button's job: an apostrophe in a line comment must not open a string
const base = 'kit-btn inline-flex gap-2';
const byKind: Record<string, string> = {
  primary: 'rounded px-6',
};
const classes = [base, byKind[kind], cls];
---
<button class:list={classes}>{label}</button>
<style>
.kit-btn { min-height: 44px; }
.kit-gone { color: red; }
</style>
"""

PREFIX_TEMPLATE = """---
const CHIP = { lead: 'Lead', no: 'No' };
---
<li><span class:list={['chip', `k-${f.kind}`]}>{CHIP[f.kind]}</span></li>
<style>
.chip { display: inline-flex; }
.k-no { color: red; }
.k-lead { color: grey; }
.x-dead { color: blue; }
</style>
"""

SHORTHAND_OBJECT = """---
const { bare = false, class: cls } = Astro.props;
---
<div class:list={['city-kit', 'city-roster', { bare }, cls]}></div>
<style>
.city-roster.bare { padding: 0; }
.bare .tray { max-width: none; margin: 0; }
.unused { margin: 0; }
</style>
"""


def _drift(src):
    H.findings.clear()
    H.check_class_drift([("src/components/kit/X.astro", src)])
    out = [f["msg"] for f in H.findings if f["check"] == "markup-css-drift"]
    H.findings.clear()
    return " ".join(out)


def test_a_class_in_a_frontmatter_constant_is_rendered():
    msg = _drift(BUTTON_CONST)
    assert "kit-btn" not in msg, msg
    assert "kit-gone" in msg, msg              # still blind to nothing: a dead rule is reported


def test_a_template_prefix_renders_every_class_it_can_build():
    msg = _drift(PREFIX_TEMPLATE)
    assert "k-no" not in msg and "k-lead" not in msg, msg
    assert "x-dead" in msg, msg


def test_an_object_shorthand_key_in_class_list_is_rendered():
    msg = _drift(SHORTHAND_OBJECT)
    assert "bare" not in msg, msg
    assert "unused" in msg, msg
