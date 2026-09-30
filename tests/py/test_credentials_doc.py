"""`docs/reference/credentials.md` is the only map from an env key to what reads it.

A credentials doc drifts silently in three directions, and all three were live defects in
the version Task 13 first wrote: a key documented but absent from `.env.example`, so
nobody rebuilding `.env` knows it exists; a key in `.env.example` with no row, so nobody
knows what reads it; and a `Read by` cell naming a file that does not contain the key,
which is the worst of the three because it reads as evidence. The spec review caught the
third — seven GSC/GA4 keys were attributed to two agents that never mention them.

So: both lists must match exactly, and every file a cell names must actually contain the
key. A cell that names no file (`nothing yet — project 6 wires the GSC/GA4 pulls`) is the
honest answer for a key nothing reads, and is checked only for not naming a file.

No value is asserted, read or printed here. This test reads key NAMES from two committed
files and greps for those names; it never opens `.env`.
"""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/reference/credentials.md"
EXAMPLE = ROOT / ".env.example"

# A table row: | `KEY` | read by | active? |
ROW = re.compile(r"^\|\s*`([A-Z][A-Z0-9_]*)`\s*\|([^|]*)\|([^|]*)\|\s*$")
# A backticked repo path inside a `Read by` cell.
CELL_PATH = re.compile(r"`([^`\n]+\.(?:py|md|mjs|ts|sh|astro))`")


def rows():
    """[(key, read_by_cell, active_cell)] from the credentials table."""
    return [(m.group(1), m.group(2).strip(), m.group(3).strip())
            for m in (ROW.match(l) for l in DOC.read_text(encoding="utf-8").splitlines())
            if m]


def documented():
    return {k for k, _, _ in rows()}


def exampled():
    out = set()
    for line in EXAMPLE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        out.add(line.split("=", 1)[0].strip())
    return out


def test_the_table_actually_parses():
    # A formatting change that stopped ROW matching would make every test below vacuous.
    assert len(rows()) >= 10, f"only {len(rows())} rows parsed from {DOC.name}"


def test_env_example_carries_key_names_and_no_values():
    bad = [l for l in EXAMPLE.read_text(encoding="utf-8").splitlines()
           if "=" in l and not l.strip().startswith("#")
           and l.split("=", 1)[1].strip() not in ("", "https://SITE_URL_PLACEHOLDER")]
    assert bad == [], (
        ".env.example carries key names only — a value there is a committed secret:\n  "
        + "\n  ".join(bad))


def test_every_documented_key_is_in_env_example():
    missing = sorted(documented() - exampled())
    assert missing == [], (
        f"{DOC.name} documents keys that .env.example does not list, so anyone rebuilding "
        f".env from the example would ship without them: {missing}")


def test_every_env_example_key_is_documented():
    missing = sorted(exampled() - documented())
    assert missing == [], (
        f".env.example lists keys with no row in {DOC.name}, so nobody knows what reads "
        f"them: {missing}")


@pytest.mark.parametrize("key,cell", [(k, c) for k, c, _ in rows()], ids=lambda v: v[:40])
def test_every_file_named_as_a_reader_contains_the_key(key, cell):
    bad = []
    for rel in CELL_PATH.findall(cell):
        f = ROOT / rel
        if not f.exists():
            bad.append(f"{rel} does not exist")
        elif key not in f.read_text(encoding="utf-8", errors="replace"):
            bad.append(f"{rel} does not contain {key}")
    assert bad == [], (
        f"{DOC.name} claims these read `{key}`, and they do not. Either fix the cell or "
        "say 'nothing yet' — an attribution nobody can grep reads as evidence:\n  "
        + "\n  ".join(bad))


def test_a_key_nothing_reads_says_so_rather_than_naming_a_file():
    # The inverse of the test above: the honest empty answer must stay recognisable, so a
    # future edit cannot quietly replace it with a plausible-looking file name.
    for key, cell, active in rows():
        if "nothing yet" in cell:
            assert not CELL_PATH.findall(cell), (
                f"{key} says 'nothing yet' and also names a file — pick one")
            assert "project 6" in active, (
                f"{key} is read by nothing, so it cannot be active: {active!r}")


def test_no_value_shaped_token_appears_in_the_doc():
    # A credential is long and unbroken; prose and repo paths are not. This is the same
    # check the task's acceptance ran by hand, kept so it runs on every commit.
    long = [f"{DOC.name}:{n}  {l.strip()[:80]}"
            for n, l in enumerate(DOC.read_text(encoding="utf-8").splitlines(), 1)
            for _ in re.findall(r"[A-Za-z0-9_-]{30,}", l)]
    assert long == [], "a value-shaped token in the credentials doc:\n  " + "\n  ".join(long)
