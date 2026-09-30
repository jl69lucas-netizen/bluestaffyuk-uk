import pathlib

import pytest
from build_agent_registry import AGENTS, build, main, parse


def test_registry_matches_the_directory():
    """The drift CAG had (68 entries, 67 files) cannot happen if the registry is derived."""
    assert main(["--check"]) == 0


def test_every_agent_is_named_bsuk():
    agents = build()["agents"]
    # Non-vacuous on purpose: a glob that stopped matching would make "every agent is named
    # bsuk-" true of an empty set, which is exactly the shape of the drift this file exists
    # to prevent. Assert the registry covers every file in the directory, and that there
    # are files.
    on_disk = sorted(p.stem for p in AGENTS.glob("*.md"))
    assert on_disk, "no agents on disk — the registry cannot be checked against nothing"
    assert sorted(agents) == on_disk
    for name in agents:
        assert name.startswith("bsuk-"), name


def test_parse_rejects_a_name_that_disagrees_with_its_filename(tmp_path):
    p = tmp_path / "bsuk-x.md"
    p.write_text("---\nname: bsuk-y\neffort: high\n---\nbody\n")
    with pytest.raises(ValueError, match="declares name"):
        parse(p)


def test_parse_rejects_a_file_with_no_frontmatter(tmp_path):
    p = tmp_path / "bsuk-x.md"
    p.write_text("no frontmatter here\n")
    with pytest.raises(ValueError, match="frontmatter"):
        parse(p)


def test_a_quoted_effort_is_the_same_declaration_as_a_bare_one(tmp_path):
    """`effort: "high"` is YAML for high. Reading the quotes as part of the value would
    make it an unknown tier and fail a registry build for a file that is correct."""
    p = tmp_path / "bsuk-x.md"
    p.write_text('---\nname: "bsuk-x"\neffort: "high"\n---\nbody\n', encoding="utf-8")
    assert parse(p) == ("bsuk-x", "high")


def test_a_malformed_agent_exits_one_with_a_message_not_a_traceback(tmp_path, monkeypatch,
                                                                    capsys):
    """A gate that tracebacks reads as a broken gate and sends the reader to the wrong file."""
    import build_agent_registry as m

    broken = tmp_path / "bsuk-broken.md"
    broken.write_text("no frontmatter here\n", encoding="utf-8")
    monkeypatch.setattr(m, "AGENTS", tmp_path)

    assert m.main(["--check"]) == 1
    err = capsys.readouterr().err
    assert err.startswith("ERROR: "), err
    assert "bsuk-broken.md" in err and "frontmatter" in err
    assert "Traceback" not in err
