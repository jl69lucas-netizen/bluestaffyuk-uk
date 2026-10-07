#!/usr/bin/env python3
"""env_loader.py — fill os.environ from the repo's .env, so every script and agent finds its keys.

    import env_loader; env_loader.load_env()

The breeder's ruling (2026-10-07): "make so all future agents can see and use the API key".
The keys live in the gitignored `.env` at the repo root (`docs/reference/credentials.md`
says which key exists and what reads it). A worktree has no `.env` of its own, so the loader
reads this checkout's `.env` first and then the main checkout's (the parent of
`git rev-parse --git-common-dir`). A key already in the environment always wins, and nothing
is ever printed: callers learn only the key NAMES that were loaded.
"""
from __future__ import annotations

import os
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent


def default_roots(root: pathlib.Path = ROOT) -> list[pathlib.Path]:
    """This checkout, then the main checkout when this one is a worktree."""
    roots = [root]
    try:
        common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                cwd=root, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        common = ""
    if common:
        main = pathlib.Path(common).parent
        if main not in roots:
            roots.append(main)
    return roots


def load_env(roots=None, environ=None) -> list[str]:
    """Set every key the roots' `.env` files hold that `environ` lacks; return their names.
    Earlier roots win over later ones; the environment wins over every file."""
    from session_handoff import parse_env  # one dotenv parser for the repo

    env = os.environ if environ is None else environ
    loaded = []
    for root in (default_roots() if roots is None else roots):
        path = pathlib.Path(root) / ".env"
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for key, value in parse_env(text):
            if key not in env and value != "":
                env[key] = value
                loaded.append(key)
    return loaded
