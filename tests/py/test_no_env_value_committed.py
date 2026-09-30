"""No real credential value may sit in a tracked file, the run log, or an Artifact.

This test reads `.env` — the one file allowed to hold values — and proves, without ever
printing, logging or echoing a value, that none of them appears anywhere the repository
publishes. Each value is handed to `git grep -F --quiet --` as an *argument*, so it never
passes through a shell, never lands in a process listing built by string interpolation, and
never reaches this test's own output. On failure the assertion names the KEY and the FILE
only.

Written at the project-2 close-out after `.claude/skills/bsuk-indexing/SKILL.md` was found
carrying a live GSC client secret and a live GA4 client id in a curl example. See
`docs/reports/system-transfer-gate-report.md` § Credentials and MCP → Incident.
"""
import pathlib
import re
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ENV = ROOT / ".env"

# A short value is not a credential, it is a word; grepping for it produces noise, not proof.
MIN_LEN = 9

# Keys whose value is public by design and is SUPPOSED to appear in committed files. Each
# one is a deliberate ruling, not a convenience:
#   SITE_URL, GSC_SITE_URL  — the site's own address; it is in every canonical and sitemap.
#   PUBLIC_FORMSPREE_ID     — a public endpoint id, served to every visitor in the contact
#                             form's action attribute (see the gate report's Formspree
#                             ruling). Permitted in spec/plan/Artifact docs and in the
#                             committed scorecard's action field; never in code or fixtures.
#   GA4_PROPERTY_ID         — a numeric property id, not a credential.
# Anything else in .env — client ids, client secrets, refresh tokens, the IndexNow key — is
# secret and must never appear anywhere git can see.
PUBLIC_KEYS = frozenset({"SITE_URL", "GSC_SITE_URL", "PUBLIC_FORMSPREE_ID", "GA4_PROPERTY_ID"})

# Scanned in addition to everything git tracks. The run log is gitignored-adjacent evidence
# and the Artifacts are the files the controller publishes.
EXTRA_GLOBS = ("docs/reports/system-transfer-run.log", "docs/artifacts/*.html")


def _env_values():
    """{KEY: value} for every non-empty, long-enough assignment in .env."""
    out = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Z0-9_]+)=(.*)$", line.strip())
        if not m:
            continue
        value = m.group(2).strip().strip("\"'")
        if (len(value) >= MIN_LEN
                and "PLACEHOLDER" not in value
                and m.group(1) not in PUBLIC_KEYS):
            out[m.group(1)] = value
    return out


@pytest.mark.skipif(not ENV.exists(), reason=".env absent — nothing to prove")
def test_public_key_allowlist_does_not_rot():
    """Every allowlisted key must still exist in .env, so a rename cannot silently
    widen the exemption to nothing while leaving a real secret unscanned."""
    present = set()
    for line in ENV.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Z0-9_]+)=", line.strip())
        if m:
            present.add(m.group(1))
    assert PUBLIC_KEYS <= present, (
        f"allowlisted keys no longer in .env: {sorted(PUBLIC_KEYS - present)}"
    )


def _tracked_files_containing(value):
    """Tracked paths containing `value`, by literal match. Never echoes the value."""
    # -I skips binary files; -F literal; -l lists names only. Value is argv, not shell text.
    proc = subprocess.run(
        ["git", "grep", "-I", "-F", "-l", "--", value],
        cwd=ROOT, capture_output=True, text=True,
    )
    if proc.returncode not in (0, 1):  # 1 == no match, which is what we want
        raise RuntimeError(f"git grep failed with {proc.returncode}")
    return [p for p in proc.stdout.splitlines() if p and p != ".env"]


def _extra_files_containing(value):
    hits = []
    for pattern in EXTRA_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if value in text:
                hits.append(path.relative_to(ROOT).as_posix())
    return hits


@pytest.mark.skipif(not ENV.exists(), reason=".env absent — nothing to prove")
def test_no_env_value_appears_in_a_tracked_file_log_or_artifact():
    values = _env_values()
    assert values, ".env exists but yielded no scannable values — the parser is wrong"

    offences = []  # (KEY, path) — never the value
    for key, value in values.items():
        for path in _tracked_files_containing(value) + _extra_files_containing(value):
            offences.append(f"{key} -> {path}")

    assert sorted(set(offences)) == [], (
        "a real credential value is committed or published. Listed as KEY -> file; the "
        "value itself is deliberately not shown. Replace each literal with the $ENV "
        "reference, then ROTATE the credential — it is in this branch's git history:\n  "
        + "\n  ".join(sorted(set(offences)))
    )
    print(f"examined {len(values)} values; 0 tracked files contain one")
