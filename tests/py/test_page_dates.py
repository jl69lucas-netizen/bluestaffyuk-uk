"""generate_page_dates.py — the route set, and the dates behind it.

The gap this file exists to close: the first cut globbed `src/pages/**/*.astro` and emitted
`/[...post]/`, `/uk-locations/[slug]/` and `/available-puppies/[slug]/` as if they were
three pages. They are three TEMPLATES that build about 31 pages between them, so the map
carried three routes that are never built and dated none of the pages that are. A route
containing `[` is therefore not a cosmetic defect — it is proof the expansion did not run.

Every test builds a real throwaway git repo in tmp_path: the dates are git facts, and a
monkeypatched `git log` would test the plumbing while assuming away the thing that broke.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import generate_page_dates as G


def _git(repo, *args, date=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"{date}T12:00:00+0000"
    subprocess.run(["git", *args], cwd=str(repo), env=env, check=True,
                   capture_output=True, text=True)


def _write(repo, rel, text):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _commit(repo, date, msg="c"):
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", msg, date=date)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A miniature BSUK: one static page, the three dynamic templates, and their data."""
    _git(tmp_path, "init", "-q", "-b", "main")
    _write(tmp_path, "src/pages/index.astro", "<h1>home</h1>")
    _write(tmp_path, "src/pages/[...post].astro", "getStaticPaths")
    _write(tmp_path, "src/pages/uk-locations/[slug].astro", "getStaticPaths")
    _write(tmp_path, "src/pages/available-puppies/[slug].astro", "getStaticPaths")
    _write(tmp_path, "src/content/blog/guides.md", "---\nslug: blue-staffy-guides\n---\nbody")
    _write(tmp_path, "data/locations.json", json.dumps([{"slug": "blue-staffies-glasgow"}]))
    _write(tmp_path, "data/puppies.json", json.dumps([{"slug": "roman"}, {"slug": "byrd"}]))
    _commit(tmp_path, "2026-01-05")
    # The module anchors every path to ROOT, not to the cwd; point ROOT at the fixture.
    monkeypatch.setattr(G, "ROOT", tmp_path)
    monkeypatch.setattr(G, "OUT", tmp_path / "data" / "page-dates.json")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_no_emitted_route_ever_contains_a_bracket(repo):
    """The guard, stated as its own test: `[` in a route means an unexpanded template."""
    routes, _, _ = G.build()
    assert routes and not [r for r in routes if "[" in r or "]" in r]


def test_the_blog_template_expands_to_each_post_frontmatter_slug(repo):
    routes, _, _ = G.build()
    assert "/blue-staffy-guides/" in routes
    assert "/guides/" not in routes, "the filename is not the route; the frontmatter slug is"


def test_the_locations_template_expands_to_every_slug_in_locations_json(repo):
    _write(repo, "data/locations.json",
           json.dumps([{"slug": "blue-staffies-glasgow"}, {"slug": "blue-staffies-leeds"}]))
    _commit(repo, "2026-02-01")
    routes, _, _ = G.build()
    assert "/uk-locations/blue-staffies-glasgow/" in routes
    assert "/uk-locations/blue-staffies-leeds/" in routes


def test_the_puppies_template_expands_to_every_slug_in_puppies_json(repo):
    routes, _, _ = G.build()
    assert "/available-puppies/roman/" in routes and "/available-puppies/byrd/" in routes


def test_a_generated_pages_dates_span_its_template_and_its_data_file(repo):
    """A location page changes when EITHER its template or its row changes. Dating it by
    the template alone would call a content edit no change at all."""
    _write(repo, "data/locations.json", json.dumps([{"slug": "blue-staffies-glasgow", "h1": "edited"}]))
    _commit(repo, "2026-03-09")
    row = G.build()[0]["/uk-locations/blue-staffies-glasgow/"]
    assert row["datePublished"] == "2026-01-05", "earliest first-commit across the sources"
    assert row["dateModified"] == "2026-03-09", "latest last-commit across the sources"


def test_a_post_that_is_edited_moves_only_its_own_route(repo):
    _write(repo, "src/content/blog/guides.md", "---\nslug: blue-staffy-guides\n---\nlonger body")
    _commit(repo, "2026-04-02")
    routes = G.build()[0]
    assert routes["/blue-staffy-guides/"]["dateModified"] == "2026-04-02"
    assert routes["/"]["dateModified"] == "2026-01-05"


def test_a_post_with_no_frontmatter_slug_is_skipped_not_guessed(repo):
    _write(repo, "src/content/blog/nameless.md", "---\ntitle: x\n---\nbody")
    _commit(repo, "2026-05-01")
    routes, skipped, _ = G.build()
    assert not [r for r in routes if "nameless" in r]
    assert any("nameless" in s for s in skipped)


def test_an_uncommitted_page_carries_no_date_rather_than_todays(repo):
    _write(repo, "src/pages/fresh.astro", "<h1>x</h1>")
    routes, skipped, _ = G.build()
    assert "/fresh/" not in routes
    assert any("fresh.astro" in s for s in skipped)


def test_coverage_names_built_pages_that_carry_no_date(repo):
    """dist/ is the list of pages that actually exist. K>0 must be printed, not hidden."""
    for r in ("index.html", "uk-locations/blue-staffies-glasgow/index.html",
              "orphan-page/index.html"):
        _write(repo, f"dist/{r}", "<html></html>")
    _, _, built = G.coverage(G.build()[0])
    assert built["built"] == 3 and built["undated"] == ["/orphan-page/"]


def test_coverage_is_clean_when_every_built_page_is_dated(repo):
    _write(repo, "dist/index.html", "<html></html>")
    _, _, built = G.coverage(G.build()[0])
    assert built["undated"] == []


def test_the_summary_line_reports_dated_built_and_undated(repo, capsys):
    _write(repo, "dist/index.html", "<html></html>")
    _write(repo, "dist/orphan-page/index.html", "<html></html>")
    assert G.main(["--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "routes:" in out and "dated" in out and "built" in out
    assert "/orphan-page/" in out


def test_dry_run_writes_nothing(repo):
    G.main(["--dry-run"])
    assert not (repo / "data" / "page-dates.json").exists()


def test_it_runs_from_any_cwd_because_every_path_is_anchored_to_root(repo, monkeypatch, tmp_path):
    """Relative globs and a bare `git log` made the map a fact about the shell's cwd. Run
    from elsewhere it produced zero routes and said so as if the repo were empty."""
    elsewhere = tmp_path.parent / "elsewhere"
    elsewhere.mkdir(exist_ok=True)
    monkeypatch.chdir(elsewhere)
    routes, _, _ = G.build()
    assert "/" in routes and "/available-puppies/roman/" in routes


def test_check_on_a_malformed_committed_map_cannot_run(repo, capsys):
    """A corrupt page-dates.json is not a stale map: nothing was compared. Exit 2."""
    (repo / "data" / "page-dates.json").write_text('{"routes": ')
    assert G.main(["--check"]) == 2
    assert "unreadable" in capsys.readouterr().out


def test_check_reports_staleness_as_exit_1(repo):
    (repo / "data" / "page-dates.json").write_text(json.dumps({"routes": {}}))
    assert G.main(["--check"]) == 1


def test_a_write_that_fails_leaves_the_previous_map_intact(repo, monkeypatch):
    """Atomic write: the map is committed, so a half-written file is a corrupted record in
    git, not a retry."""
    out = repo / "data" / "page-dates.json"
    out.write_text('{"routes": {"/old/": {}}}')
    monkeypatch.setattr(G.os, "replace", lambda *a: (_ for _ in ()).throw(OSError("disk full")))
    with pytest.raises(OSError):
        G.main([])
    assert json.loads(out.read_text())["routes"] == {"/old/": {}}
    assert not list((repo / "data").glob("*.tmp*")), "the temp file must be cleaned up"


def test_no_git_on_path_is_exit_2_with_a_sentence_not_a_traceback(repo, capsys, monkeypatch):
    """This runs inside `prebuild`. A bare FileNotFoundError in the middle of a build reads
    as a build failure with no cause attached, and every date in the map would be missing
    rather than one of them."""
    def no_git(*a, **k):
        raise FileNotFoundError(2, "No such file or directory: 'git'")
    monkeypatch.setattr(G.subprocess, "run", no_git)
    assert G.main([]) == 2
    assert "git" in capsys.readouterr().out


def test_a_run_that_dates_fewer_routes_refuses_to_overwrite_the_committed_map(repo, capsys):
    """A map that shrank by itself is a shallow checkout or a broken glob. Overwriting would
    delete the honest dates of pages that still exist — and `prebuild` means nobody is
    reading the diff."""
    out = repo / "data" / "page-dates.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    before = json.dumps({"routes": {f"/page-{i}/": {} for i in range(99)}})
    out.write_text(before)
    assert G.main([]) == 1
    assert out.read_text() == before, "the committed map must survive the refusal"
    assert "REFUSING" in capsys.readouterr().out


def test_check_and_dry_run_are_mutually_exclusive(repo):
    with pytest.raises(SystemExit):
        G.main(["--check", "--dry-run"])


# --- The map, wired into the build (project 4 task 3) -------------------------------------
#
# The tests above prove the map is derived honestly. These two prove the built site actually
# USES it: a correct data/page-dates.json that no page reads is the same freshness lie it
# was written to end, just harder to see.
#
# WHAT DECIDES WHICH DATE A PAGE SHOULD CARRY. Not the map's `selfDated` flag: that is the
# generator's source-level guess (true as soon as ANY source behind the route mentions the
# word), and testing the layout against it would only prove the two halves agree about the
# guess. The observable rule is the one BaseLayout implements — a page that ports its own
# WebPage node keeps the old site's date, everything else gets the git-derived one — so these
# tests ask the built page: you have a date; is it one of the two dates you are allowed?
#
# Timestamps are compared in FULL. Two nodes agreeing to the day and disagreeing on the hour
# is still two answers to one question, and truncating to ten characters hid exactly that.

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DATE_MODIFIED = re.compile(r'"dateModified":\s*"([^"]+)"')


def _ported_dates():
    """Every dateModified value written into the repo's own sources — the ported meta in
    src/pages/**, the blog frontmatter, and the rows of data/*.json. A built date that is
    neither the git date nor one of these came from nowhere."""
    out = set()
    for path in [*(REPO_ROOT / "src").rglob("*.astro"), *(REPO_ROOT / "src").rglob("*.md"),
                 *(REPO_ROOT / "data").glob("*.json")]:
        out.update(DATE_MODIFIED.findall(path.read_text(encoding="utf-8", errors="ignore")))
    return out


def _built_routes():
    dist = REPO_ROOT / "dist"
    if not dist.is_dir():
        pytest.skip("no dist/ — run `npm run build` first")
    out = {}
    for html in sorted(dist.rglob("index.html")):
        rel = html.parent.relative_to(dist).as_posix()
        out["/" if rel == "." else f"/{rel}/"] = html
    return out


def test_every_built_page_carries_either_its_ported_date_or_the_git_one_and_never_neither():
    """The whole contract in one assertion, page by page.

    A page that ports its own WebPage node keeps the old site's date and the layout adds
    nothing; a page that does not gets the git-derived date from data/page-dates.json. There
    is no third option, and "no date at all" is the hole the location pages fell through —
    the generator marked all eleven `selfDated` because ONE row of data/locations.json carries
    a date, and the rows that carry none shipped undated."""
    routes = json.loads((REPO_ROOT / "data/page-dates.json").read_text())["routes"]
    ported = _ported_dates()
    wrong = []
    for route, html in _built_routes().items():
        found = DATE_MODIFIED.findall(html.read_text(encoding="utf-8"))
        if not found:
            wrong.append(f"{route}: no dateModified at all")
            continue
        git = (routes.get(route) or {}).get("dateModified")
        for value in set(found):
            if value[:10] != git and value not in ported:
                wrong.append(f"{route}: {value} is neither the git date ({git}) nor a ported one")
    assert not wrong, "; ".join(wrong)


def test_no_built_page_carries_two_dates_that_disagree():
    """Compared in full, not to the day: two nodes that agree on the date and disagree on the
    hour are still two answers, and a crawler reads whichever it reaches first."""
    for route, html in _built_routes().items():
        found = set(DATE_MODIFIED.findall(html.read_text(encoding="utf-8")))
        assert len(found) <= 1, f"{route} carries {sorted(found)}"
