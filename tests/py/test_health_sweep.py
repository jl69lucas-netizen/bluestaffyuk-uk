"""`scripts/health-sweep.sh` tells the truth about a repo with no remote.

This repo has no git remote until project 6 (CLAUDE.md working rule 3). The sweep's git
block fetched `origin` anyway, counted `origin/<branch>..HEAD`, failed, and printed
"? commit(s) committed but NOT pushed/deployed" on every run: a warning nobody can clear,
which teaches a reader to skip the block. With no remote it now says there is nothing to
push; with one it counts as before.

Each test copies the script alone into a fresh repository under tmp_path and runs it with
`--no-build` and no SITE_URL, so it builds nothing and opens no socket; only the git block's
lines are read.
"""
import os
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/health-sweep.sh"


def sweep(tmp_path, remote=False, name="origin"):
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy(SCRIPT, repo / "scripts/health-sweep.sh")

    def git(*args):
        subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)

    git("init", "-q")
    git("-c", "user.name=t", "-c", "user.email=t@example.invalid",
        "commit", "-q", "--allow-empty", "-m", "start")
    if remote:
        bare = tmp_path / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
        git("remote", "add", name, str(bare))
    env = {k: v for k, v in os.environ.items() if k != "SITE_URL"}
    run = subprocess.run(["bash", "scripts/health-sweep.sh", "--no-build"], cwd=repo,
                         capture_output=True, text=True, env=env, timeout=120)
    return run.stdout


def test_no_remote_means_nothing_to_push(tmp_path):
    out = sweep(tmp_path)
    assert "no remote — nothing to push" in out
    assert "NOT pushed" not in out


def test_a_remote_is_still_compared(tmp_path):
    out = sweep(tmp_path, remote=True)
    assert "no remote" not in out
    assert "NOT pushed" in out or "Up to date with origin" in out


def test_a_remote_that_is_not_origin_is_not_compared(tmp_path):
    # the block fetches and counts against origin/<branch>: with only another remote there is
    # no origin to compare, and "? commit(s) … NOT pushed" would be the false alarm again
    out = sweep(tmp_path, remote=True, name="upstream")
    assert "no origin remote — nothing to push" in out
    assert "NOT pushed" not in out
