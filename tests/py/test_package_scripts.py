"""Every `npm run` entry must name a file that exists, and `build` must stay release-free.

`package.json` is the discoverable surface of the system: an agent reading it learns what
can be run. An entry pointing at a script that was renamed or never ported is worse than a
missing entry, because the agent believes the capability exists until the shell says
`No such file`. So every `python3|node|bash scripts/X` referenced anywhere in the scripts
block is resolved against the repo.

The second assertion is the release guard: `npm run build` must not bake a search index for
a site that has no host. `build:release` is where that belongs, behind
`scripts/release_guard.sh`.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
REF = re.compile(r"\b(?:python3|node|bash)\s+(scripts/[\w./-]+)")


def test_every_referenced_script_exists():
    missing = []
    for name, cmd in SCRIPTS.items():
        for path in REF.findall(cmd):
            if not (ROOT / path).is_file():
                missing.append(f"{name} -> {path}")
    assert not missing, "package.json names scripts that do not exist: " + ", ".join(missing)


def test_every_npm_run_target_is_defined():
    """`check:all` chains other entries; a typo there fails only at run time."""
    missing = []
    for name, cmd in SCRIPTS.items():
        for target in re.findall(r"npm run ([\w:-]+)", cmd):
            if target not in SCRIPTS:
                missing.append(f"{name} -> npm run {target}")
    assert not missing, "package.json chains undefined scripts: " + ", ".join(missing)


def test_build_does_not_run_pagefind():
    assert "pagefind" not in SCRIPTS["build"], (
        "build must not index a site that has no host; pagefind belongs in build:release")
    assert "pagefind" not in SCRIPTS.get("postbuild", "")


def test_release_only_entries_sit_behind_the_guard():
    assert SCRIPTS["build:release"].startswith("bash scripts/release_guard.sh &&")
    assert "pagefind" in SCRIPTS["build:release"]
    assert (ROOT / "scripts/release_guard.sh").is_file()


def _guard(tmp_path, env_line=None, env_var=None):
    """Run a COPY of the guard from a scratch repo root, so the real `.env` is not the one read."""
    import os
    import shutil
    import subprocess
    (tmp_path / "scripts").mkdir(exist_ok=True)
    shutil.copy(ROOT / "scripts/release_guard.sh", tmp_path / "scripts/release_guard.sh")
    if env_line is not None:
        (tmp_path / ".env").write_text(env_line + "\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "PUBLIC_FORMSPREE_ID"}
    env["BSUK_RELEASE"] = "1"
    if env_var is not None:
        env["PUBLIC_FORMSPREE_ID"] = env_var
    return subprocess.run(["bash", str(tmp_path / "scripts/release_guard.sh")],
                          capture_output=True, text=True, env=env, cwd=tmp_path)


def test_the_release_guard_refuses_a_build_with_no_form_endpoint(tmp_path):
    """Without the id every enquiry form builds with a `#contact` fallback that submits
    nowhere, and the build itself stays green — so the release guard is where it is refused."""
    proc = _guard(tmp_path)
    assert proc.returncode == 2 and "PUBLIC_FORMSPREE_ID" in proc.stderr
    assert _guard(tmp_path, env_line="PUBLIC_FORMSPREE_ID=").returncode == 2


def test_the_release_guard_accepts_the_id_from_env_or_dotenv(tmp_path):
    assert _guard(tmp_path, env_var="abc123").returncode == 0
    ok = _guard(tmp_path, env_line="PUBLIC_FORMSPREE_ID=abc123")
    assert ok.returncode == 0 and "abc123" not in ok.stdout + ok.stderr


def test_the_dates_map_is_regenerated_before_every_build():
    """A committed map goes stale the moment a page is added or edited, and a stale map is a
    WRONG `dateModified` on a real page rather than a missing one. `prebuild` is an npm
    lifecycle hook, so it covers `npm run build` only — `build:release` calls `astro build`
    directly and has to name the generator itself."""
    assert SCRIPTS["prebuild"] == "python3 scripts/generate_page_dates.py"
    assert "scripts/generate_page_dates.py" in SCRIPTS["build:release"]


def test_the_check_all_chain_is_the_documented_one():
    # `check:facts` sits immediately after `check:parity` because the two are one gate split
    # in half: parity judges the pages project 4 has not rewritten yet, the facts gate judges
    # the ones it has, and data/facts/rebuilt.json is what moves a page from one to the other.
    # `check:links` sits immediately after `check:facts` on purpose: the two are the halves
    # of one question about a rebuilt page — facts-preserved asks what it LOST, link parity
    # asks what it ADDED — and reading them apart is how a link nobody approved slipped
    # through (project 4, 2026-09-20 review).
    # `check:verbatim` closes that run (working rule 15, Task 18b): facts asks what a rebuilt
    # page LOST, links asks what it ADDED, verbatim asks whether it kept the old page's
    # WORDING — the one thing a page can lose with every fact still on it.
    # `check:outline` follows it (system-gaps Task 6): the fourth question about a rebuilt
    # new-family page — was it written from its own approved outline, or from a sibling.
    # check:competitors sits after check:queries: both guard research the page builders read.
    # check:gaps follows check:competitors: the matrix is rebuilt from the registry's reports.
    # check:workflow sits just before check:markers: both judge the instruction tree rather
    # than the site — markers asks whether a source-repo word survived, workflow asks whether
    # WORKFLOW.md / quick-start.md name an agent, script or npm script that is not there
    # (Known Issue 56).
    # check:retired follows check:placeholders: both judge what the built site SAYS — a
    # placeholder is a fact not yet supplied, a retired fact is one that has been withdrawn
    # (Known Issue 65; its allowlist only shrinks).
    # check:boards follows check:retired: `board_gate.py --all` runs the build-stage board
    # gate (approval hash, Asset Gate image checks, header collisions) over every page in
    # data/facts/rebuilt.json, so no rebuilt page ships on a board that stopped matching.
    expected = ["check:parity", "check:facts", "check:links", "check:verbatim",
                "check:outline", "check:redirects", "check:schema", "check:queries",
                "check:competitors", "check:gaps", "check:sitemaps", "check:placeholders",
                "check:retired", "check:boards", "check:workflow", "check:markers", "agents"]
    assert re.findall(r"npm run ([\w:-]+)", SCRIPTS["check:all"]) == expected


def test_the_page_run_ends_in_the_zero_examined_guard():
    """`build_scorecard.mjs` holds Guard 1 (a page that wrote no partial) and Guard 2 (a
    check that examined zero nodes across every page), and until parity plan Task 11 it ran
    only when somebody remembered to type it. `scripts/render_pages.mjs` runs the page suite
    and then the scorecard, whatever the page run's result (tests/py/test_render_pages_runner.py).
    Not an npm `post` hook: npm skips that when the page run fails."""
    assert SCRIPTS["test:render:pages"] == "node scripts/render_pages.mjs"
    assert "posttest:render:pages" not in SCRIPTS
