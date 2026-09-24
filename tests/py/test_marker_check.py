import json

import pytest

from marker_check import MARKERS, PRINT_CAP, hits_in, main, scan_roots


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


@pytest.mark.parametrize("line", [
    "Every page meets WCAG-AA contrast.",
    "wcag-aa contrast is checked",
    "WCAG 2.2 AA is the target.",
    "the swcag-thing",
])
def test_cag_prefix_does_not_fire_mid_identifier(tmp_path, line):
    """Spec 4 defines `cag-` as a path/identifier PREFIX. WCAG-AA is not a CAG reference,
    and a gate that cries wolf on an accessibility note stops being read."""
    repo = _repo(tmp_path, files=[("CLAUDE.md", line + "\n")])
    assert hits_in(repo / "CLAUDE.md") == []


@pytest.mark.parametrize("line", [
    "cag-hub-builder is first",
    "see /cag-library/x for the rest",
    "trailing space then cag-",
    "(cag-hub-builder)",
    '"cag-hub-builder"',
    "cag-hub-builder at line start",
    "CAG-HUB-BUILDER shouting",
])
def test_cag_prefix_fires_at_a_left_word_boundary(tmp_path, line):
    repo = _repo(tmp_path, files=[("CLAUDE.md", line + "\n")])
    assert [m for _, m, _ in hits_in(repo / "CLAUDE.md")] == ["cag-"]


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


def test_binary_files_are_not_scanned_at_all(tmp_path):
    """Skipped by suffix, so a marker-shaped byte run inside a PNG is never even opened."""
    repo = _repo(tmp_path, files=[("CLAUDE.md", "clean\n")])
    (repo / "tests/render/fixtures/assets").mkdir(parents=True)
    png = repo / "tests/render/fixtures/assets/x.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\ncongo")
    assert png not in scan_roots(repo)
    assert main(repo) == 0


def test_a_text_file_that_is_not_utf8_is_still_read_and_reported(tmp_path):
    """A latin-1 byte in a .md must not silently buy the file a pass: decode with
    replacement so the markers around the bad byte are still judged."""
    repo = _repo(tmp_path)
    (repo / "rules").mkdir(parents=True, exist_ok=True)
    (repo / "rules/x.md").write_bytes(b"parrot caf\xe9\n")
    assert [m for _, m, _ in hits_in(repo / "rules/x.md")] == ["parrot"]
    assert main(repo) == 1


def test_a_rebase_row_whose_dst_is_not_written_yet_is_skipped(tmp_path):
    rows = [{"src": "rules/cag-x.md", "dst": "rules/bsuk-x.md", "mode": "rebase", "notes": "n"}]
    repo = _repo(tmp_path, rows)
    assert scan_roots(repo) == []
    assert main(repo) == 0


def test_output_is_capped_and_the_count_is_not(tmp_path, capsys):
    repo = _repo(tmp_path)
    (repo / "rules").mkdir(parents=True, exist_ok=True)
    (repo / "rules/x.md").write_text("parrot\n" * (PRINT_CAP + 5), encoding="utf-8")
    assert main(repo) == 1
    out = capsys.readouterr().out
    assert "\u2026 and 5 more" in out
    assert "examined 1 files; %d problems" % (PRINT_CAP + 5) in out
    assert out.count("[parrot]") == PRINT_CAP


def test_a_malformed_manifest_fails_with_task_1s_message(tmp_path):
    repo = _repo(tmp_path, [{"src": "a.md", "dst": "b.md", "mode": "teleport", "notes": "n"}])
    with pytest.raises(ValueError, match="unknown mode"):
        scan_roots(repo)


def test_the_real_repo_is_clean():
    """The gate this project exists to satisfy. Green since Task 15 re-based tests/render/
    and scripts/dup_content_audit.py; targets.json (Task 16) carried no marker."""
    assert main() == 0


# ── a marker the line scan could not see (project-5 readiness, 2026-09-23) ───
# `bsuk-paa-agent.md` wrapped "African" / "Greys" across a line break and
# `bsuk-site-hygiene-agent.md` spelled "african-gray"; both passed this gate, which read one
# line at a time and only the UK spelling. Task A4 removed both from the agents; these hold
# the gate to them from now on, in every root it scans.
@pytest.mark.parametrize("text,marker", [
    ("Why do owners call African\nGreys clever?\n", "african grey"),
    ("an African-\nGrey in the house\n", "african-grey"),
    ("> the African\n> Greys of the source site\n", "african grey"),
    ("- owners of an African\n  Gray and a Staffy\n", "african grey"),
])
def test_a_marker_split_across_a_line_break_fires(tmp_path, text, marker):
    repo = _repo(tmp_path, files=[("CLAUDE.md", text)])
    assert [(n, m) for n, m, _ in hits_in(repo / "CLAUDE.md")] == [(1, marker)]


@pytest.mark.parametrize("line,marker", [
    ("An African Gray needs space.", "african grey"),
    ("See /african-gray-care/.", "african-grey"),
    ("AFRICAN  GRAYS are loud", "african grey"),
])
def test_the_us_spelling_fires(tmp_path, line, marker):
    repo = _repo(tmp_path, files=[("CLAUDE.md", line + "\n")])
    assert hits_in(repo / "CLAUDE.md") == [(1, marker, line)]


@pytest.mark.parametrize("text", [
    "African\nsoil is red\n",
    "a grey\nAfrican violet\n",
    "the blue-grey coat of a Blue Staffy\n",
    "a gray muzzle at twelve\n",
])
def test_the_wider_match_spares_ordinary_words(tmp_path, text):
    repo = _repo(tmp_path, files=[("CLAUDE.md", text)])
    assert hits_in(repo / "CLAUDE.md") == []


def test_a_split_marker_fails_the_gate(tmp_path):
    repo = _repo(tmp_path, files=[("rules/x.md", "Blue Staffy owners and African\nGreys\n")])
    assert main(repo) == 1


# ── both passes number lines one way (review of fbef94f) ─────────────────────
# The whole-file pass counts "\n"; the line pass must split on "\n" too, or a form feed or a
# Unicode line separator earlier in the file shifts one pass's numbering and context.
@pytest.mark.parametrize("text,line_no", [
    ("intro\n\nsee the African\nGreys\n", 3),
    ("a\x0cb c\nsee the African\nGreys\n", 2),
])
def test_a_split_marker_is_reported_on_the_line_where_it_starts(tmp_path, text, line_no):
    repo = _repo(tmp_path, files=[("CLAUDE.md", text)])
    assert hits_in(repo / "CLAUDE.md") == [(line_no, "african grey", "see the African Greys")]


def test_both_passes_number_lines_one_way(tmp_path):
    text = "a\x0cb c\nAn African Gray\nsee the African\nGreys\n"
    repo = _repo(tmp_path, files=[("CLAUDE.md", text)])
    assert [(n, m) for n, m, _ in hits_in(repo / "CLAUDE.md")] == [
        (2, "african grey"), (3, "african grey")]
