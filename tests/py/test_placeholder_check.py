"""The two claim placeholders are gate-backed, not just convention.

`LICENCE_CLAIM_PLACEHOLDER` and `LEGAL_CLAIM_PLACEHOLDER` were introduced during the skill
re-base to hold a breeder-licence claim and a Lucy's-Law claim that nobody has confirmed.
A placeholder that is only a naming convention gets asserted back into prose by the first
writer who finds it tidy, so each one is tested twice: it must be counted where it actually
lives (the instruction tree, not `dist/`), and it must block a release build.
"""
import pytest

from placeholder_check import PLACEHOLDERS, SOURCE_ROOTS, main, scan


def _repo(tmp_path, dist_files=(), skill_files=(), agent_files=()):
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
    return tmp_path


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
    counts, files = scan(root / "dist", [root / r for r in SOURCE_ROOTS])
    assert counts[token] == 1
    assert files[token] == ["bsuk-x.md"]


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
