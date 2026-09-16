import pytest
from build_agent_registry import build, main, parse


def test_registry_matches_the_directory():
    """The drift CAG had (68 entries, 67 files) cannot happen if the registry is derived."""
    assert main(["--check"]) == 0


def test_every_agent_is_named_bsuk(tmp_path):
    for name in build()["agents"]:
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
