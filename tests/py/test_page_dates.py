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
