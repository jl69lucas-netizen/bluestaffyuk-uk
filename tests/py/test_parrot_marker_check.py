import json

import pytest

from parrot_marker_check import MARKERS, hits_in, main, scan_roots


def _repo(tmp_path, manifest_rows=(), files=()):
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data/port-manifest.json").write_text(json.dumps(list(manifest_rows)), encoding="utf-8")
    for rel, text in files:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path


def test_marker_list_is_exactly_the_spec_list():
    assert MARKERS == (
        "parrot", "african grey", "african-grey", "timneh", "congo", "clutch",
        "c.a.gs", "cags", "congoafricangreys", "agcare", "xrejpnvn", "cag-",
    )


@pytest.mark.parametrize("marker,line", [
    ("parrot", "The parrot is weaned."),
    ("african grey", "An African Grey needs space."),
    ("african-grey", "See /african-grey-care/."),
    ("timneh", "Timneh greys run smaller."),
    ("congo", "Congo range is wide."),
    ("clutch", "The clutch was candled."),
    ("c.a.gs", "Here at C.A.Gs we answer."),
    ("cags", "cags-comprehensive-page-audit-system"),
    ("congoafricangreys", "https://congoafricangreys.com/"),
    ("agcare", "google-agcare-snapshot"),
    ("xrejpnvn", "https://formspree.io/f/xrejpnvn"),
    ("cag-", "run cag-hub-builder first"),
])
def test_every_marker_fires(tmp_path, marker, line):
    repo = _repo(tmp_path, files=[("CLAUDE.md", line + "\n")])
    assert hits_in(repo / "CLAUDE.md") == [(1, marker, line)]


def test_matching_is_case_insensitive(tmp_path):
    repo = _repo(tmp_path, files=[("CLAUDE.md", "AFRICAN GREY PARROT\n")])
    found = {m for _, m, _ in hits_in(repo / "CLAUDE.md")}
    assert "african grey" in found and "parrot" in found


def test_clean_file_has_no_hits(tmp_path):
    repo = _repo(tmp_path, files=[("CLAUDE.md", "Blue Staffy puppies from a Glasgow kennel.\n")])
    assert hits_in(repo / "CLAUDE.md") == []


def test_manifest_itself_is_never_scanned(tmp_path):
    """Structural, not an allowlist: every manifest src path begins `cag-` or names CAG's
    tree, so scanning the record of the port would make a complete record unrepresentable."""
    rows = [{"src": ".claude/agents/cag-hub-builder.md", "dst": ".claude/agents/bsuk-hub-builder.md",
             "mode": "rebase", "notes": "bird -> puppy"}]
    repo = _repo(tmp_path, rows, files=[(".claude/agents/bsuk-hub-builder.md", "Blue Staffy hubs.\n")])
    roots = scan_roots(repo)
    assert (repo / "data/port-manifest.json") not in roots
    assert main(repo) == 0


def test_a_dirty_manifest_dst_fails(tmp_path):
    rows = [{"src": ".claude/agents/cag-hub-builder.md", "dst": ".claude/agents/bsuk-hub-builder.md",
             "mode": "rebase", "notes": "n"}]
    repo = _repo(tmp_path, rows, files=[(".claude/agents/bsuk-hub-builder.md", "Our African Grey hubs.\n")])
    assert main(repo) == 1


def test_deferred_rows_are_not_scanned(tmp_path):
    """A deferred row writes no dst; scanning a path that does not exist would be a crash,
    and scanning one that happens to exist for another reason would be a false attribution."""
    rows = [{"src": ".claude/skills/cag-logo-generator/SKILL.md",
             "dst": ".claude/skills/bsuk-logo-generator/SKILL.md", "mode": "deferred", "notes": "project 3"}]
    repo = _repo(tmp_path, rows)
    assert main(repo) == 0


def test_fixed_roots_are_scanned_even_when_not_in_the_manifest(tmp_path):
    repo = _repo(tmp_path, files=[("rules/puppies.md", "Never imply a wild-caught parrot.\n")])
    assert main(repo) == 1


def test_binary_and_non_text_files_are_skipped(tmp_path):
    repo = _repo(tmp_path, files=[("CLAUDE.md", "clean\n")])
    (repo / "tests/render/fixtures/assets").mkdir(parents=True)
    (repo / "tests/render/fixtures/assets/x.png").write_bytes(b"\x89PNG\r\n\x1a\ncongo")
    assert main(repo) == 0


@pytest.mark.xfail(reason="tests/render/ and dup_content_audit.py are re-based in Tasks 14-16", strict=True)
def test_the_real_repo_is_clean():
    """The gate this project exists to satisfy. Red until Task 16."""
    assert main() == 0
