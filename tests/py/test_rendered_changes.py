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


ENV = {"PATH": "/usr/bin:/bin"}


def _repo(tmp_path):
    """A committed git tree whose .gitignore hides the two builds, so it starts clean."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".gitignore").write_text("old/\ndist/\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "m"],
                   cwd=tmp_path, check=True)
    return tmp_path


def _cli(tmp_path, *args):
    return subprocess.run([sys.executable, SCRIPT, *args], cwd=tmp_path, capture_output=True,
                          text=True, env={**ENV, "RENDERED_CHANGES_ROOT": str(tmp_path)})


def test_the_cli_writes_the_report_and_the_manifest(tmp_path):
    """The fixed interface Task 26 (measurement ledger) reads:
    docs/reports/rendered-changes.json = {"base", "head", "changed"}."""
    _repo(tmp_path)
    old = _dist(tmp_path / "old", {"index": "same", "uk-locations/x": "before"})
    _dist(tmp_path / "dist", {"index": "same", "uk-locations/x": "after", "blog-post": "new"})
    r = _cli(tmp_path, "--base", str(old), "--json", "--record-manifest")
    assert r.returncode == 0, r.stdout + r.stderr
    rep = json.loads((tmp_path / "docs/reports/rendered-changes.json").read_text())
    assert set(rep) == {"base", "head", "changed"}
    assert rep["base"] == str(old) and len(rep["head"]) == 40
    assert rep["changed"] == ["blog-post", "uk-locations/x"]
    man = json.loads((tmp_path / "data/quality/dist-hashes.json").read_text())
    assert man["head"] == rep["head"] and sorted(man["pages"]) == ["blog-post", "index", "uk-locations/x"]
    assert "2 changed" in r.stdout


def test_json_writes_only_the_report_and_record_manifest_only_the_manifest(tmp_path):
    """Recording the manifest is a separate act: done on every --json, a skipped or failed
    IndexNow submit would silently drop its pages from the next diff."""
    _repo(tmp_path)
    old = _dist(tmp_path / "old", {"index": "a"})
    _dist(tmp_path / "dist", {"index": "b"})
    assert _cli(tmp_path, "--base", str(old), "--json").returncode == 0
    assert (tmp_path / "docs/reports/rendered-changes.json").is_file()
    assert not (tmp_path / "data/quality/dist-hashes.json").exists()
    (tmp_path / "docs/reports/rendered-changes.json").unlink()
    assert _cli(tmp_path, "--base", str(old), "--record-manifest").returncode == 0
    assert (tmp_path / "data/quality/dist-hashes.json").is_file()
    assert not (tmp_path / "docs/reports/rendered-changes.json").exists()


def test_head_is_marked_dirty_by_uncommitted_work_but_not_by_its_own_outputs(tmp_path):
    _repo(tmp_path)
    old = _dist(tmp_path / "old", {"index": "a"})
    _dist(tmp_path / "dist", {"index": "b"})
    for _ in range(2):  # the second run sees the first run's report and manifest, untracked
        assert _cli(tmp_path, "--base", str(old), "--json", "--record-manifest").returncode == 0
        head = json.loads((tmp_path / "docs/reports/rendered-changes.json").read_text())["head"]
        assert len(head) == 40 and not head.endswith("-dirty")
    # An untracked file is not uncommitted work on the build (page_run_record.dirty_tracked,
    # the one definition of dirty the gate report uses too — Task 28a).
    (tmp_path / "stray.txt").write_text("x", encoding="utf-8")
    assert _cli(tmp_path, "--base", str(old), "--json").returncode == 0
    head = json.loads((tmp_path / "docs/reports/rendered-changes.json").read_text())["head"]
    assert not head.endswith("-dirty")
    # A committed manifest rewritten by --record-manifest is its own output, not dirt.
    subprocess.run(["git", "add", "data/quality/dist-hashes.json"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "man"],
                   cwd=tmp_path, check=True)
    _dist(tmp_path / "dist", {"index": "c"})
    assert _cli(tmp_path, "--base", str(old), "--json", "--record-manifest").returncode == 0
    head = json.loads((tmp_path / "docs/reports/rendered-changes.json").read_text())["head"]
    assert not head.endswith("-dirty")
    (tmp_path / ".gitignore").write_text("old/\ndist/\nx\n", encoding="utf-8")  # a tracked edit
    assert _cli(tmp_path, "--base", str(old), "--json", "--record-manifest").returncode == 0
    rep = json.loads((tmp_path / "docs/reports/rendered-changes.json").read_text())
    man = json.loads((tmp_path / "data/quality/dist-hashes.json").read_text())
    assert rep["head"].endswith("-dirty") and len(rep["head"]) == 46 and man["head"] == rep["head"]


def test_a_base_with_no_pages_is_refused(tmp_path):
    """An empty base would call every page "changed" and send the whole site."""
    _repo(tmp_path)
    (tmp_path / "old").mkdir()
    _dist(tmp_path / "dist", {"index": "b"})
    r = _cli(tmp_path, "--base", str(tmp_path / "old"), "--json")
    assert r.returncode == 2 and "has no pages" in r.stdout
    assert not (tmp_path / "docs/reports/rendered-changes.json").exists()


@pytest.mark.parametrize("pages", [["index"], {"index": 1}, "x"])
def test_a_malformed_manifest_at_the_ref_is_refused(tmp_path, pages):
    _repo(tmp_path)
    (tmp_path / "data/quality").mkdir(parents=True)
    (tmp_path / "data/quality/dist-hashes.json").write_text(
        json.dumps({"head": "abc", "pages": pages}), encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "m2"],
                   cwd=tmp_path, check=True)
    _dist(tmp_path / "dist", {"index": "b"})
    r = _cli(tmp_path, "--base", "HEAD", "--json")
    assert r.returncode == 2 and "malformed" in r.stdout


def test_no_git_head_is_refused_not_reported_as_unknown(tmp_path):
    old = _dist(tmp_path / "old", {"index": "a"})
    _dist(tmp_path / "dist", {"index": "b"})
    r = _cli(tmp_path, "--base", str(old), "--json")
    assert r.returncode == 2 and "cannot read git HEAD" in r.stdout
    assert not (tmp_path / "docs/reports/rendered-changes.json").exists()


def test_removed_slugs_are_printed_but_never_written(tmp_path):
    _repo(tmp_path)
    old = _dist(tmp_path / "old", {"index": "a", "gone": "g"})
    _dist(tmp_path / "dist", {"index": "a"})
    r = _cli(tmp_path, "--base", str(old), "--json")
    assert r.returncode == 0 and "  removed gone" in r.stdout
    rep = json.loads((tmp_path / "docs/reports/rendered-changes.json").read_text())
    assert rep["changed"] == [] and "gone" not in json.dumps(rep)


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


@pytest.mark.parametrize("open_tag", [
    "<script type='application/ld+json'>",
    '<SCRIPT TYPE="application/LD+JSON">',
    '<script  data-x="1"   type = "application/ld+json" >',
])
def test_json_ld_counts_whatever_its_spelling(open_tag):
    close = "</SCRIPT>" if open_tag.startswith("<SCRIPT") else "</script>"
    page = "<html><head>{}{{\"@type\":\"{}\"}}{}</head><body>x</body></html>"
    a = page.format(open_tag, "Product", close)
    b = page.format(open_tag, "Offer", close)
    assert RC.content_hash(a) != RC.content_hash(b)
