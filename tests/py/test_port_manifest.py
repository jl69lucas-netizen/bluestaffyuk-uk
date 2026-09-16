import json
import pathlib
import subprocess
import sys

import pytest

from port_from_cag import apply_manifest, load_manifest, validate

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts/port_from_cag.py"


def _row(src, dst, mode="copy", notes="n"):
    return {"src": src, "dst": dst, "mode": mode, "notes": notes}


def _src_tree(tmp_path, *names):
    cag = tmp_path / "cag"
    for n in names:
        p = cag / n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("source %s\n" % n, encoding="utf-8")
    return cag


def test_validate_rejects_unknown_mode(tmp_path):
    with pytest.raises(ValueError, match="mode"):
        validate([_row("a.md", "b.md", mode="teleport")])


def test_validate_rejects_duplicate_dst(tmp_path):
    with pytest.raises(ValueError, match="duplicate dst"):
        validate([_row("a.md", "same.md"), _row("b.md", "same.md")])


def test_validate_rejects_absolute_or_escaping_paths():
    with pytest.raises(ValueError, match="relative"):
        validate([_row("/etc/passwd", "b.md")])
    with pytest.raises(ValueError, match="relative"):
        validate([_row("a.md", "../outside.md")])


def test_copy_overwrites_every_run(tmp_path):
    cag = _src_tree(tmp_path, "a.md")
    bsuk = tmp_path / "bsuk"
    rows = [_row("a.md", "x/a.md", mode="copy")]
    apply_manifest(rows, cag, bsuk)
    (bsuk / "x/a.md").write_text("hand edit\n", encoding="utf-8")
    stats = apply_manifest(rows, cag, bsuk)
    assert (bsuk / "x/a.md").read_text() == "source a.md\n"
    assert stats["applied"] == 1 and stats["skipped_existing"] == 0


def test_rename_overwrites_and_renames(tmp_path):
    cag = _src_tree(tmp_path, ".claude/agents/cag-faq-agent.md")
    bsuk = tmp_path / "bsuk"
    rows = [_row(".claude/agents/cag-faq-agent.md", ".claude/agents/bsuk-faq-agent.md", mode="rename")]
    apply_manifest(rows, cag, bsuk)
    assert (bsuk / ".claude/agents/bsuk-faq-agent.md").exists()
    stats = apply_manifest(rows, cag, bsuk)
    assert stats["applied"] == 1


def test_rebase_never_overwrites(tmp_path):
    """The hand edits ARE the deliverable. A second run that re-copied the parrot source
    would silently undo the whole re-base, and the marker gate would only notice afterwards."""
    cag = _src_tree(tmp_path, "rules/for-sale.md")
    bsuk = tmp_path / "bsuk"
    rows = [_row("rules/for-sale.md", "rules/puppies.md", mode="rebase")]
    first = apply_manifest(rows, cag, bsuk)
    assert first["applied"] == 1
    (bsuk / "rules/puppies.md").write_text("re-based by hand\n", encoding="utf-8")
    second = apply_manifest(rows, cag, bsuk)
    assert second["applied"] == 0 and second["skipped_existing"] == 1
    assert (bsuk / "rules/puppies.md").read_text() == "re-based by hand\n"


def test_deferred_writes_nothing(tmp_path):
    cag = _src_tree(tmp_path, ".claude/skills/cag-logo-generator/SKILL.md")
    bsuk = tmp_path / "bsuk"
    rows = [_row(".claude/skills/cag-logo-generator/SKILL.md",
                 ".claude/skills/bsuk-logo-generator/SKILL.md", mode="deferred")]
    stats = apply_manifest(rows, cag, bsuk)
    assert stats["deferred"] == 1 and not (bsuk / ".claude/skills/bsuk-logo-generator/SKILL.md").exists()


def test_missing_source_is_counted_not_raised(tmp_path):
    cag = _src_tree(tmp_path, "a.md")
    bsuk = tmp_path / "bsuk"
    stats = apply_manifest([_row("a.md", "a.md"), _row("gone.md", "gone.md")], cag, bsuk)
    assert stats["missing"] == 1 and stats["applied"] == 1


def test_deferred_source_may_be_absent(tmp_path):
    """A deferred row records a decision, not a file. Requiring its source to exist would
    make the manifest unable to record anything CAG later deletes."""
    stats = apply_manifest([_row("nope.md", "nope.md", mode="deferred")], tmp_path / "cag", tmp_path / "bsuk")
    assert stats["missing"] == 0 and stats["deferred"] == 1


def test_real_manifest_validates():
    rows = load_manifest()
    validate(rows)
    assert len(rows) > 0


def test_validate_rejects_row_missing_mode():
    with pytest.raises(ValueError, match="manifest invalid at 0"):
        validate([{"src": "a.md", "dst": "b.md", "notes": "n"}])


def test_validate_rejects_non_dict_row():
    with pytest.raises(ValueError, match="manifest invalid at 0"):
        validate(["a.md"])


def _run_script(tmp_path, cag, rows):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(rows), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--cag", str(cag),
         "--manifest", str(manifest), "--dest", str(tmp_path / "bsuk")],
        capture_output=True, text=True)


def test_cli_exits_nonzero_when_source_missing(tmp_path):
    cag = _src_tree(tmp_path, "other.md")
    proc = _run_script(tmp_path, cag, [_row("a.md", "x/a.md")])
    assert proc.returncode == 1
    assert proc.stdout.strip().splitlines()[-1].endswith(
        "examined 1 rows; applied 0, skipped-existing 0, deferred 0, missing 1")


def test_cli_exits_zero_when_source_present(tmp_path):
    cag = _src_tree(tmp_path, "a.md")
    proc = _run_script(tmp_path, cag, [_row("a.md", "x/a.md")])
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.strip().splitlines()[-1].endswith(
        "examined 1 rows; applied 1, skipped-existing 0, deferred 0, missing 0")
    assert (tmp_path / "bsuk/x/a.md").read_text() == "source a.md\n"
