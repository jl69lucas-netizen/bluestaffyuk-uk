"""Repo-wide scan for credential-SHAPED tokens, wherever the marker gate already looks.

`test_no_env_value_committed.py` proves no value *currently in `.env`* is committed. It
cannot catch a credential that was never in `.env` — a colleague's key, a rotated-out
secret, a token pasted into an example. This test catches those by shape instead of by
value, and it rides on `marker_check.scan_roots()` so that a root added to
`data/port-manifest.json` in a later project gets secret coverage automatically, with no
second list to keep in step.

Reports `file:line  <shape name>` only. It never prints the matched text: a failure message
that quotes the secret has published it a second time.

Written at the project-2 close-out. See the gate report's Credentials section → Incident.
"""
import functools
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import marker_check  # noqa: E402

# Roots scanned on top of marker_check.scan_roots(). These hold generated evidence and
# published output — exactly where a pasted secret would go unnoticed.
EXTRA_ROOTS = (
    "docs/reports",
    "docs/artifacts",
    "data/quality/scorecards",
    "tests/py/fixtures",
)

TEXT_SUFFIXES = marker_check.TEXT_SUFFIXES | {".html", ".json"}

# Shape → compiled pattern. Named so a failure says what kind of thing it found.
SHAPES = {
    "google-oauth-client-secret": re.compile(r"GOCSPX-[A-Za-z0-9_-]{20,}"),
    "google-oauth-client-id": re.compile(
        r"[0-9]{12}-[a-z0-9]{32}\.apps\.googleusercontent\.com"),
    "google-oauth-refresh-token": re.compile(r"1//0[A-Za-z0-9_-]{30,}"),
    "google-api-key": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    "bare-32-hex": re.compile(r"(?<![A-Za-z0-9])[0-9a-f]{32}(?![A-Za-z0-9])"),
}

# The migrated WordPress fixtures are full of 32-hex CSS class names (`wp-block-…-a1b2…`)
# and asset hashes. They are markup, not credentials, so the bare-hex shape — the only
# shape with a plausible innocent twin — is not applied under the fixture tree. Every
# other shape still is: no fixture has any business holding a `GOCSPX-` string.
HEX_EXEMPT_PREFIX = "tests/py/fixtures/"


@functools.lru_cache(maxsize=1)
def _git_ignored():
    """Paths git ignores, as repo-relative posix strings, from one `git ls-files` call.

    Generated build output lives under ignored roots — `docs/artifacts/canvas/` (the
    design-canvas artboards) and `docs/artifacts/design-system/`. Astro's `astro:assets`
    URLs carry 32-character content hashes, which are indistinguishable from the
    `bare-32-hex` shape, so a built tree would fail this guard on markup that is never
    committed. Nothing ignored can leak a secret into the repo, so nothing ignored is
    scanned. Tracked files are unaffected: the guard is otherwise unchanged.
    """
    try:
        r = subprocess.run(
            ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "-z"],
            cwd=ROOT, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return frozenset()  # no git here: scan everything rather than skip silently
    return frozenset(p for p in r.stdout.split("\0") if p)


def _files():
    ignored = _git_ignored()
    seen, out = set(), []
    for f in marker_check.scan_roots(ROOT):
        rp = f.resolve()
        if f.relative_to(ROOT).as_posix() in ignored:
            continue
        if rp not in seen:
            seen.add(rp)
            out.append(f)
    for rel in EXTRA_ROOTS:
        base = ROOT / rel
        if not base.exists():
            continue
        for f in sorted(base.rglob("*")):
            rp = f.resolve()
            if (f.is_file() and f.suffix.lower() in TEXT_SUFFIXES
                    and "__pycache__" not in f.parts and rp not in seen
                    and f.relative_to(ROOT).as_posix() not in ignored):
                seen.add(rp)
                out.append(f)
    return out


def _hits(path):
    rel = path.relative_to(ROOT).as_posix()
    # This file and the credentials doc test hold the patterns themselves.
    if rel in ("tests/py/test_secret_shapes.py",):
        return []
    out = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    for n, line in enumerate(text.splitlines(), 1):
        for name, pat in SHAPES.items():
            if name == "bare-32-hex" and rel.startswith(HEX_EXEMPT_PREFIX):
                continue
            if pat.search(line):
                out.append(f"{rel}:{n}  {name}")
    return out


def test_scan_covers_the_marker_gate_roots():
    """If this ever returns nothing the test above is vacuously green."""
    files = _files()
    assert len(files) > 50, f"secret scan examined only {len(files)} files — roots broke"


def test_no_credential_shaped_token_anywhere_the_marker_gate_looks():
    offences = []
    for f in _files():
        offences += _hits(f)
    assert sorted(set(offences)) == [], (
        "a credential-shaped token was found. Only the location and the shape are shown; "
        "the value is deliberately withheld. Replace it with the $ENV reference and ROTATE "
        "the credential:\n  " + "\n  ".join(sorted(set(offences)))
    )
