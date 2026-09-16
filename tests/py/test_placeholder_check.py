"""The two claim placeholders are gate-backed, not just convention.

`LICENCE_CLAIM_PLACEHOLDER` and `LEGAL_CLAIM_PLACEHOLDER` were introduced during the skill
re-base to hold a breeder-licence claim and a Lucy's-Law claim that nobody has confirmed.
A placeholder that is only a naming convention gets asserted back into prose by the first
writer who finds it tidy, so each one is tested twice: it must be counted where it actually
lives (the instruction tree, not `dist/`), and it must block a release build.
"""
import pytest

from placeholder_check import LIST_CAP, PLACEHOLDERS, SOURCE_ROOTS, main, scan


def _repo(tmp_path, dist_files=(), skill_files=(), agent_files=(), other_files=()):
    for rel, text in dist_files:
        p = tmp_path / "dist" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    (tmp_path / "dist").mkdir(parents=True, exist_ok=True)
    for base, group in ((".claude/skills", skill_files), (".claude/agents", agent_files)):
        for rel, text in group:
            p = tmp_path / base / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
    for rel, text in other_files:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path


def _scan(root):
    return scan(root / "dist", [root / r for r in SOURCE_ROOTS], root=root)


def test_both_claim_tokens_are_registered():
    assert "LICENCE_CLAIM_PLACEHOLDER" in PLACEHOLDERS
    assert "LEGAL_CLAIM_PLACEHOLDER" in PLACEHOLDERS


def test_instruction_tree_roots_are_scanned():
    assert ".claude/skills" in SOURCE_ROOTS
    assert ".claude/agents" in SOURCE_ROOTS


@pytest.mark.parametrize("token", ["LICENCE_CLAIM_PLACEHOLDER", "LEGAL_CLAIM_PLACEHOLDER"])
def test_token_counted_in_skills(tmp_path, token, capsys):
    root = _repo(tmp_path, skill_files=[("x/SKILL.md", "Differentiator: %s twice %s" % (token, token))])
    assert main(root=root, dist=root / "dist", release=False) == 0
    out = capsys.readouterr().out
    line = next(l for l in out.splitlines() if l.strip().startswith(token))
    assert line.split() == [token, "2", "occurrence(s)", "in", "1", "file(s)"]
    assert "advisory" in out


@pytest.mark.parametrize("token", ["LICENCE_CLAIM_PLACEHOLDER", "LEGAL_CLAIM_PLACEHOLDER"])
def test_token_counted_in_agents(tmp_path, token):
    root = _repo(tmp_path, agent_files=[("bsuk-x.md", token)])
    counts, files = _scan(root)
    assert counts[token] == 1
    assert files[token] == [".claude/agents/bsuk-x.md"]


@pytest.mark.parametrize("token", ["LICENCE_CLAIM_PLACEHOLDER", "LEGAL_CLAIM_PLACEHOLDER"])
def test_token_blocks_release(tmp_path, token, capsys):
    root = _repo(tmp_path, skill_files=[("x/SKILL.md", token)])
    assert main(root=root, dist=root / "dist", release=True) == 1
    assert "FAIL: BSUK_RELEASE=1" in capsys.readouterr().out


def test_clean_instruction_tree_releases(tmp_path, capsys):
    root = _repo(tmp_path, skill_files=[("x/SKILL.md", "no stand-ins here")])
    assert main(root=root, dist=root / "dist", release=True) == 0
    assert "release build is clean" in capsys.readouterr().out


def test_missing_dist_still_fails(tmp_path, capsys):
    root = _repo(tmp_path, skill_files=[("x/SKILL.md", "text")])
    assert main(root=root, dist=tmp_path / "nodist", release=False) == 1
    assert "no dist/ to scan" in capsys.readouterr().out


@pytest.mark.parametrize("token", ["LICENCE_CLAIM_PLACEHOLDER", "LEGAL_CLAIM_PLACEHOLDER"])
def test_skill_hit_is_reported_root_relative(tmp_path, token):
    """A bare `x/SKILL.md` could equally be a built page; the root-relative path cannot."""
    root = _repo(tmp_path, skill_files=[("x/SKILL.md", token)])
    _, files = _scan(root)
    assert files[token] == [".claude/skills/x/SKILL.md"]


def test_dist_hit_keeps_its_dist_prefix(tmp_path):
    root = _repo(tmp_path, dist_files=[("index.html", "SITE_URL_PLACEHOLDER")])
    _, files = _scan(root)
    assert files["SITE_URL_PLACEHOLDER"] == ["dist/index.html"]


def test_long_file_list_is_truncated_with_a_tail_count(tmp_path, capsys):
    """22 files, cap 20: the count stays honest and the list says what it left out."""
    token = "LICENCE_CLAIM_PLACEHOLDER"
    root = _repo(tmp_path, skill_files=[("s%02d/SKILL.md" % i, token) for i in range(22)])
    assert main(root=root, dist=root / "dist", release=True) == 1
    out = capsys.readouterr().out
    assert out.count("  %s — .claude/skills/" % token) == LIST_CAP
    assert "%s — … and 2 more" % token in out
    assert "22 file(s)" in out


def test_token_outside_the_scanned_roots_is_not_counted(tmp_path):
    """docs/ and scripts/ are out of scope: the gate guards the instruction tree and the
    build, not every mention of a token in the repo's own prose about it."""
    token = "LEGAL_CLAIM_PLACEHOLDER"
    root = _repo(tmp_path, other_files=[("docs/notes.md", token), ("scripts/x.py", token)])
    counts, files = _scan(root)
    assert counts[token] == 0 and files[token] == []


def test_non_text_suffix_in_skills_is_not_counted(tmp_path):
    """A .png named like a placeholder is not prose; scanning binaries would be noise."""
    token = "LICENCE_CLAIM_PLACEHOLDER"
    root = _repo(tmp_path, skill_files=[("x/diagram.png", token)])
    counts, files = _scan(root)
    assert counts[token] == 0 and files[token] == []
