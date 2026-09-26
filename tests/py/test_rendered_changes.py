"""`scripts/rendered_changes.py` — the slugs whose RENDERED output changed (audit D6, M13).

IndexNow's `--changed` diffed SOURCE paths matching `src/pages/<x>/index.astro`, so it could
never see a city page (`uk-locations/[slug].astro`), a puppy, a blog post or any shared
component edit: project 6 would have submitted none of project 5's pages. The honest list is
the built output itself — hash every dist/**/index.html, compare with the build the last
close recorded, and name what moved."""
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import rendered_changes as RC  # noqa: E402

SCRIPT = str(ROOT / "scripts" / "rendered_changes.py")


def _dist(base, pages):
    for key, html in pages.items():
        d = base if key == "index" else base / key
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(html, encoding="utf-8")
    return base


def test_hashes_key_every_built_page_and_skip_the_specimens(tmp_path):
    dist = _dist(tmp_path / "dist", {"index": "a", "uk-locations/blue-staffy-puppies-hull": "b",
                                     "kit-preview": "c", "board-preview/x": "d"})
    h = RC.page_hashes(dist)
    assert sorted(h) == ["index", "uk-locations/blue-staffy-puppies-hull"]
    assert len(h["index"]) == 64


def test_diff_names_modified_and_added_as_changed_and_removed_apart():
    base = {"index": "1", "a": "1", "gone": "1"}
    head = {"index": "1", "a": "2", "new": "1"}
    assert RC.diff(base, head) == {"changed": ["a", "new"], "removed": ["gone"]}


def test_a_directory_base_is_hashed_directly(tmp_path):
    old = _dist(tmp_path / "old", {"index": "same", "uk-locations/x": "before"})
    RC.ROOT = tmp_path
    try:
        assert RC.base_hashes(str(old)) == RC.page_hashes(old)
    finally:
        RC.ROOT = ROOT


def test_a_ref_base_reads_the_manifest_that_ref_committed(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "data/quality").mkdir(parents=True)
    (tmp_path / "data/quality/dist-hashes.json").write_text(
        json.dumps({"head": "abc", "pages": {"index": "h1"}}), encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "m"],
                   cwd=tmp_path, check=True)
    RC.ROOT = tmp_path
    try:
        assert RC.base_hashes("HEAD") == {"index": "h1"}
        with pytest.raises(RC.BaseError, match="no data/quality/dist-hashes.json at"):
            RC.base_hashes("no-such-ref")
    finally:
        RC.ROOT = ROOT


def test_the_cli_writes_the_report_and_the_manifest(tmp_path):
    """The fixed interface Task 26 (measurement ledger) reads:
    docs/reports/rendered-changes.json = {"base", "head", "changed"}."""
    for cmd in (["git", "init", "-q"], ["git", "-c", "user.email=t@t", "-c", "user.name=t",
                                        "commit", "-q", "--allow-empty", "-m", "m"]):
        subprocess.run(cmd, cwd=tmp_path, check=True)
    old = _dist(tmp_path / "old", {"index": "same", "uk-locations/x": "before"})
    _dist(tmp_path / "dist", {"index": "same", "uk-locations/x": "after", "blog-post": "new"})
    r = subprocess.run([sys.executable, SCRIPT, "--base", str(old), "--json"], cwd=tmp_path,
                       capture_output=True, text=True, env={"RENDERED_CHANGES_ROOT": str(tmp_path),
                                                            "PATH": "/usr/bin:/bin"})
    assert r.returncode == 0, r.stdout + r.stderr
    rep = json.loads((tmp_path / "docs/reports/rendered-changes.json").read_text())
    assert set(rep) == {"base", "head", "changed"}
    assert rep["base"] == str(old) and len(rep["head"]) == 40
    assert rep["changed"] == ["blog-post", "uk-locations/x"]
    man = json.loads((tmp_path / "data/quality/dist-hashes.json").read_text())
    assert man["head"] == rep["head"] and sorted(man["pages"]) == ["blog-post", "index", "uk-locations/x"]
    assert "2 changed" in r.stdout


def test_the_cli_refuses_without_a_build(tmp_path):
    r = subprocess.run([sys.executable, SCRIPT, "--base", "HEAD"], cwd=tmp_path, capture_output=True,
                       text=True, env={"RENDERED_CHANGES_ROOT": str(tmp_path), "PATH": "/usr/bin:/bin"})
    assert r.returncode == 2 and "dist/ does not exist" in r.stdout


def test_a_style_or_script_bundle_change_alone_is_not_a_rendered_change():
    """A shared CSS edit rewrites every page's inline <style> and hashed asset links; that is
    not a change a search engine indexes, so IndexNow must not be told about all 51 pages.
    Text and JSON-LD still count."""
    base = ('<html><head><style>.a{color:red}</style><link rel="stylesheet" href="/_astro/x.AAA.css">'
            '<script type="module" src="/_astro/p.AAA.js"></script>'
            '<script type="application/ld+json">{"@type":"Product"}</script></head>'
            '<body><h1>Blue Staffy</h1><script>var n=1</script></body></html>')
    css_only = (base.replace(".a{color:red}", ".a{color:blue}").replace("x.AAA.css", "x.BBB.css")
                .replace("p.AAA.js", "p.BBB.js").replace("var n=1", "var n=2"))
    text = base.replace("Blue Staffy", "Blue Staffy Puppies")
    schema = base.replace('"Product"', '"Offer"')
    h = RC.content_hash
    assert h(base) == h(css_only)
    assert h(base) != h(text)
    assert h(base) != h(schema)
