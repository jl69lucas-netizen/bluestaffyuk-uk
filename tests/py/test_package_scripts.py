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


def test_the_check_all_chain_is_the_documented_one():
    expected = ["check:parity", "check:redirects", "check:schema", "check:sitemaps",
                "check:placeholders", "check:markers", "agents"]
    assert re.findall(r"npm run ([\w:-]+)", SCRIPTS["check:all"]) == expected
