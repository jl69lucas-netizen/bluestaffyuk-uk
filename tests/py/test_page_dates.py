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


def test_a_city_with_its_own_page_file_is_dated_by_that_file_alone(repo):
    """src/pages/uk-locations/[slug].astro skips a city whose page has its own file (the London
    component design pass, Plan 2); the map must agree, or the city carries the template's dates."""
    _write(repo, "src/pages/uk-locations/blue-staffies-glasgow.astro", "<h1>own page</h1>")
    _commit(repo, "2026-03-09")
    routes = G.build()[0]
    assert routes["/uk-locations/blue-staffies-glasgow/"]["datePublished"] == "2026-03-09"
    assert routes["/uk-locations/blue-staffies-glasgow/"]["dateModified"] == "2026-03-09"


def _head(repo):
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True,
                          text=True, check=True).stdout.strip()


def test_a_commit_on_the_ignore_list_does_not_move_the_routes_it_names(repo):
    """A commit that changed a route's SOURCES without changing its CONTENT (the London
    scaffold's template skip, Plan 2 Task 8) must not stamp a false dateModified on every page
    the template builds. data/page-dates-ignore.json names the commit and the paths it is
    ignored for; the city keeps its earlier date."""
    _write(repo, "src/pages/uk-locations/[slug].astro", "getStaticPaths // skips own files")
    _commit(repo, "2026-03-09")
    route = "/uk-locations/blue-staffies-glasgow/"
    assert G.build()[0][route]["dateModified"] == "2026-03-09", "control: the commit counts unlisted"
    _write(repo, "data/page-dates-ignore.json", json.dumps({"commits": [{
        "sha": _head(repo)[:7], "paths": ["src/pages/uk-locations/[slug].astro"],
        "reason": "template refactor; no built page changed"}]}))
    _commit(repo, "2026-03-10")
    got = G.build()[0][route]
    assert (got["datePublished"], got["dateModified"]) == ("2026-01-05", "2026-01-05")


def test_an_ignored_commit_still_dates_the_paths_it_is_not_listed_for(repo):
    """The skip is per path: the same commit that only refactored the template CREATED a city's
    own file, and that file's date is real."""
    _write(repo, "src/pages/uk-locations/[slug].astro", "getStaticPaths // skips own files")
    _write(repo, "src/pages/uk-locations/blue-staffies-leeds.astro", "<h1>own page</h1>")
    _commit(repo, "2026-03-09")
    _write(repo, "data/page-dates-ignore.json", json.dumps({"commits": [{
        "sha": _head(repo), "paths": ["src/pages/uk-locations/[slug].astro"], "reason": "r"}]}))
    _commit(repo, "2026-03-10")
    assert G.build()[0]["/uk-locations/blue-staffies-leeds/"]["dateModified"] == "2026-03-09"


def test_a_routes_date_published_never_moves_later_than_any_committed_map(repo):
    """A route that changes source (a city leaving the template for its own file) is the same
    URL, published when it was first published: its datePublished may never move later than
    the value a committed data/page-dates.json already gave it."""
    route = "/uk-locations/blue-staffies-glasgow/"
    _write(repo, "data/page-dates.json", json.dumps({"routes": {route: {
        "datePublished": "2026-01-05", "dateModified": "2026-01-05", "selfDated": False}}}))
    _commit(repo, "2026-01-06")
    # A later committed map that already carries the moved date must not launder it.
    _write(repo, "src/pages/uk-locations/blue-staffies-glasgow.astro", "<h1>own page</h1>")
    _write(repo, "data/page-dates.json", json.dumps({"routes": {route: {
        "datePublished": "2026-03-09", "dateModified": "2026-03-09", "selfDated": False}}}))
    _commit(repo, "2026-03-09")
    got = G.build()[0][route]
    assert (got["datePublished"], got["dateModified"]) == ("2026-01-05", "2026-03-09")


def _ignore(repo, entries, raw=None):
    _write(repo, "data/page-dates-ignore.json", raw if raw is not None else json.dumps({"commits": entries}))


@pytest.mark.parametrize("label, raw", [
    ("bad JSON", "{not json"),
    ("no commits key", json.dumps({"entries": []})),
    ("paths not a list", json.dumps({"commits": [{"sha": "a" * 40, "paths": "src/x", "reason": "r"}]})),
    ("empty paths", json.dumps({"commits": [{"sha": "a" * 40, "paths": [], "reason": "r"}]})),
    ("a path not a string", json.dumps({"commits": [{"sha": "a" * 40, "paths": [3], "reason": "r"}]})),
    ("no reason", json.dumps({"commits": [{"sha": "a" * 40, "paths": ["src/x"]}]})),
    ("sha under 7", json.dumps({"commits": [{"sha": "abc12", "paths": ["src/x"], "reason": "r"}]})),
    ("override without reason", json.dumps({"commits": [], "floor_override": {"/x/": {"datePublished": "2026-01-01"}}})),
])
def test_a_malformed_ignore_file_is_exit_2_with_one_sentence(repo, capsys, label, raw):
    """A bad ignore file must stop the date step, never date by every commit silently, and say
    why in a sentence rather than a traceback (the Task 8 quality review, M1)."""
    _ignore(repo, None, raw=raw)
    assert G.main([]) == 2, label
    out = capsys.readouterr().out
    assert "page-dates-ignore.json" in out and "Traceback" not in out, label


def test_an_ignore_sha_that_is_not_a_commit_here_is_exit_2(repo, capsys):
    """A SHA must resolve to exactly one commit of this history (I2): a typo or a commit from
    another clone would otherwise ignore nothing, or the wrong thing, silently."""
    _ignore(repo, [{"sha": "deadbeefdeadbeef", "paths": ["src/pages/uk-locations/[slug].astro"], "reason": "r"}])
    assert G.main([]) == 2
    assert "deadbeefdeadbeef" in capsys.readouterr().out


def test_an_ignored_short_sha_is_compared_as_the_full_commit(repo):
    """The 7-character prefix is resolved once; the comparison is on the full SHA."""
    _write(repo, "src/pages/uk-locations/[slug].astro", "getStaticPaths // refactor")
    _commit(repo, "2026-03-09")
    full = _head(repo)
    _ignore(repo, [{"sha": full[:7].upper(), "paths": ["src/pages/uk-locations/[slug].astro"], "reason": "r"}])
    _commit(repo, "2026-03-10")
    assert G.ignored_commits() == [(full, {"src/pages/uk-locations/[slug].astro"})]
    assert G.build()[0]["/uk-locations/blue-staffies-glasgow/"]["dateModified"] == "2026-01-05"


def test_the_floor_with_no_committed_map_leaves_git_dates_alone(repo):
    """No committed data/page-dates.json yet: there is no floor, and a page is dated by git."""
    assert G.published_floor() == {}
    _write(repo, "src/pages/uk-locations/blue-staffies-glasgow.astro", "<h1>own page</h1>")
    _commit(repo, "2026-03-09")
    assert G.build()[0]["/uk-locations/blue-staffies-glasgow/"]["datePublished"] == "2026-03-09"


def test_the_floor_with_no_git_raises_nogit(repo, monkeypatch):
    def no_git(*a, **k):
        raise FileNotFoundError(2, "No such file or directory: 'git'")
    monkeypatch.setattr(G.subprocess, "run", no_git)
    with pytest.raises(G.NoGit):
        G.published_floor()


def test_a_floor_override_corrects_a_wrong_committed_date(repo):
    """The floor is one-way: once a committed map carries a date, a later run can only keep or
    lower it. A wrong early date is corrected by a `floor_override` with its reason (M3)."""
    route = "/uk-locations/blue-staffies-glasgow/"
    _write(repo, "data/page-dates.json", json.dumps({"routes": {route: {
        "datePublished": "2025-01-01", "dateModified": "2025-01-01", "selfDated": False}}}))
    _commit(repo, "2026-01-06")
    assert G.build()[0][route]["datePublished"] == "2025-01-01"
    _ignore(repo, [])
    _write(repo, "data/page-dates-ignore.json", json.dumps({"commits": [], "floor_override": {
        route: {"datePublished": "2026-01-05", "reason": "the 2025 date was a typo in the old map"}}}))
    _commit(repo, "2026-01-07")
    assert G.build()[0][route]["datePublished"] == "2026-01-05"


CITIES = ["blue-staffies-glasgow", "blue-staffies-leeds", "blue-staffies-york"]


def _three_cities_mapped(repo):
    """Three template cities, dated and their map COMMITTED (the guard compares with HEAD)."""
    _write(repo, "data/locations.json", json.dumps([{"slug": c} for c in CITIES]))
    _commit(repo, "2026-02-01")
    assert G.main([]) == 0
    _commit(repo, "2026-02-02", msg="map")


def _template_refactor(repo):
    _write(repo, "src/pages/uk-locations/[slug].astro", "getStaticPaths // a refactor")
    _commit(repo, "2026-03-09")
    return _head(repo)


def test_an_unlisted_commit_that_redates_three_routes_is_refused(repo, capsys):
    """Task 8b: a no-content commit to a shared source re-dated every route it builds, three
    times (6520267, c2705da, 142b3d6). One unlisted commit that moves dateModified on 3+ routes
    stops the run, names the commit, the source and the routes, and says what to do."""
    _three_cities_mapped(repo)
    sha = _template_refactor(repo)
    before = (repo / "data/page-dates.json").read_text()
    assert G.main([]) == 1
    out = capsys.readouterr().out
    assert sha[:7] in out and "[slug].astro" in out and "/uk-locations/blue-staffies-york/" in out
    assert "fanout_accepted" in out and "commits" in out
    assert (repo / "data/page-dates.json").read_text() == before, "a refusal writes nothing"
    assert G.main(["--check"]) == 1
    assert sha[:7] in capsys.readouterr().out


def test_a_fanout_commit_listed_as_no_content_keeps_the_old_dates(repo):
    _three_cities_mapped(repo)
    sha = _template_refactor(repo)
    _write(repo, "data/page-dates-ignore.json", json.dumps({"commits": [{
        "sha": sha, "paths": ["src/pages/uk-locations/[slug].astro"], "reason": "no output change"}]}))
    assert G.main([]) == 0
    routes = json.loads((repo / "data/page-dates.json").read_text())["routes"]
    assert {routes[f"/uk-locations/{c}/"]["dateModified"] for c in CITIES} == {"2026-02-01"}


def test_a_fanout_commit_accepted_as_real_content_moves_the_dates(repo):
    _three_cities_mapped(repo)
    sha = _template_refactor(repo)
    _write(repo, "data/page-dates-ignore.json", json.dumps({"commits": [], "fanout_accepted": [{
        "sha": sha[:9], "reason": "every city gains the new footer line"}]}))
    assert G.main([]) == 0
    routes = json.loads((repo / "data/page-dates.json").read_text())["routes"]
    assert {routes[f"/uk-locations/{c}/"]["dateModified"] for c in CITIES} == {"2026-03-09"}


def test_a_fanout_under_three_routes_passes(repo):
    """Two puppies share their template: a commit to it moves two routes, under the bar."""
    assert G.main([]) == 0
    _commit(repo, "2026-01-06", msg="map")
    _write(repo, "src/pages/available-puppies/[slug].astro", "getStaticPaths // refactor")
    _commit(repo, "2026-03-09")
    assert G.main([]) == 0
    routes = json.loads((repo / "data/page-dates.json").read_text())["routes"]
    assert routes["/available-puppies/roman/"]["dateModified"] == "2026-03-09"


@pytest.mark.parametrize("bad", [
    [{"sha": "abc12", "reason": "r"}],
    [{"sha": "a" * 40}],
    "not a list",
])
def test_a_malformed_fanout_accepted_list_is_exit_2(repo, capsys, bad):
    _write(repo, "data/page-dates-ignore.json", json.dumps({"commits": [], "fanout_accepted": bad}))
    assert G.main([]) == 2
    assert "fanout_accepted" in capsys.readouterr().out


def test_a_fanout_accepted_sha_not_in_history_is_exit_2(repo, capsys):
    _write(repo, "data/page-dates-ignore.json", json.dumps({"commits": [], "fanout_accepted": [
        {"sha": "deadbeefdeadbeef", "reason": "r"}]}))
    assert G.main([]) == 2
    assert "deadbeefdeadbeef" in capsys.readouterr().out


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


#: Build scaffolding, not pages, and deliberately dated by something else.
#:
#: `/board-preview/<slug>/` renders ONE board record three ways per section so the breeder can
#: see what they are picking, and `src/pages/board-preview/[slug].astro` dates it
#: `record.meta.research_as_of` on purpose — "this page is generated from one file, and the
#: honest date for it is the day that record's research was done. It moves when the record
#: moves." That is a deliberate answer to `schema-date-modified-present`, not a page date, so
#: the git map does not describe it and never will: the routes are `noindex, nofollow`, they
#: are in no sitemap shard, and no reader is sent to one.
#:
#: Until working rule 16 re-boarded the homepage, the three preview routes that existed
#: happened to carry 2026-09-19, which `_ported_dates()` finds written somewhere else in
#: `src/` — so they passed by coincidence rather than by rule. `/board-preview/index/` carries
#: its record's 2026-09-20 and has no such twin, which is what surfaced this. Excluded by
#: PREFIX and with the reason, rather than by widening `_ported_dates()` to read every board
#: record: that would make any date typed into any record a date any page may carry, which is
#: the opposite of what this contract is for.
PREVIEW_PREFIXES = ("/board-preview/",)


def _built_routes(scaffolding=False):
    dist = REPO_ROOT / "dist"
    if not dist.is_dir():
        pytest.skip("no dist/ — run `npm run build` first")
    out = {}
    for html in sorted(dist.rglob("index.html")):
        rel = html.parent.relative_to(dist).as_posix()
        route = "/" if rel == "." else f"/{rel}/"
        if not scaffolding and route.startswith(PREVIEW_PREFIXES):
            continue
        out[route] = html
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


def test_a_preview_route_is_dated_by_its_record_and_is_never_indexed():
    """The other half of PREVIEW_PREFIXES: an exclusion nobody checks is a hole.

    A board-preview route is excused the git-date contract because it is scaffolding dated by
    its record — so it has to actually BE that: `noindex, nofollow`, and carrying the
    `research_as_of` of the record it renders. The day one of these is served to a reader, or
    starts inventing a date of its own, the excuse stops applying and this fails."""
    import json as _json
    stamps = {}
    for f in sorted((REPO_ROOT / "data/boards").glob("*.json")):
        rec = _json.loads(f.read_text(encoding="utf-8"))
        stamps[rec["meta"]["slug"]] = rec["meta"]["research_as_of"]
    seen = 0
    for route, html in _built_routes(scaffolding=True).items():
        if not route.startswith(PREVIEW_PREFIXES):
            continue
        text = html.read_text(encoding="utf-8")
        assert 'content="noindex, nofollow"' in text, (route, "a preview route must not be indexed")
        slug = route[len("/board-preview/"):].strip("/")
        if not slug:            # the listing page, which is not one record
            continue
        seen += 1
        assert slug in stamps, (route, "a preview route with no board record behind it")
        assert set(DATE_MODIFIED.findall(text)) == {stamps[slug]}, (
            route, "a preview route is dated by its record's research_as_of and by nothing else")
    assert seen >= 4, seen
