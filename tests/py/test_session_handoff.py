"""`scripts/session_handoff.py` — a paste-ready prompt for continuing in a new chat.

Built against a throwaway git repo: one commit, a fake brief, a fake plan, a fake answer-board
batch and a fake `.env`. The prompt must carry what the repo says and nothing a secret says.
"""
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import session_handoff as SH  # noqa: E402

FAKE_KEY = "AQ.Ab8RN6fakefakefakeKEYvalue1234567890"
FAKE_OTHER = "sk-fakeOtherSecretValue987654"
FAKE_PLAIN = "plainSecretValueNoPrefix42"
SECRET_SHAPE = re.compile(r"AQ\.\S+|AIza\S+|(?<![A-Za-z0-9])sk-\S+|ghp_\S+|github_pat_\S+"
                          r"|xox[bpa]-\S+|AKIA[0-9A-Z]{16}")

BRIEF = """# Session brief

## Open Flags
- **Flag one:** the first open question.
  - a nested note under flag one
- **Flag two:** the second open question.

Not a bullet, so not carried.

## Business Focus
No deadline.

## What's Next
1. Build the London board.
2. Post the decisions batch.
"""

PLAN = """# A plan

> Steps use checkbox (`- [ ]`) syntax for tracking.

### Task 1: Done already

- [x] **Step 1: Write the test**
- [x] **Step 2: Commit**

### Task 2: The next one

- [x] **Step 1: Write the test**
- [ ] **Step 2: Implement**

### Task 3: Later

- [ ] **Step 1: Everything**
"""


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "work-branch")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "Test")
    (root / "CLAUDE.md").write_text(
        "Answer board (https://claude.ai/artifact/BoardId123) here.\n", encoding="utf-8")
    sessions = root / "docs/superpowers/sessions"
    sessions.mkdir(parents=True)
    (sessions / "2026-09-01-session-brief.md").write_text(
        "## Open Flags\n- **Old flag:** stale.\n\n## What's Next\nold\n", encoding="utf-8")
    (sessions / "2026-09-30-session-brief.md").write_text(BRIEF, encoding="utf-8")
    (sessions / "2026-09-25-location-pages-strategy.md").write_text("# not a brief\n",
                                                                    encoding="utf-8")
    plans = root / "docs/superpowers/plans"
    plans.mkdir(parents=True)
    (plans / "2026-09-01-old-plan.md").write_text("### Task 1: Old\n- [ ] step\n",
                                                  encoding="utf-8")
    (plans / "2026-10-02-new-plan.md").write_text(PLAN, encoding="utf-8")
    batches = root / "docs/reference/answer-board/batches"
    batches.mkdir(parents=True)
    (batches / "2026-09-30-a.md").write_text(
        "Board https://claude.ai/artifact/BoardId123 and page https://claude.ai/artifact/PageXyz-9\n",
        encoding="utf-8")
    (batches / "2026-09-30-b.md").write_text(
        "Again https://claude.ai/artifact/PageXyz-9.\n", encoding="utf-8")
    (root / ".env").write_text(
        "# a comment\nGEMINI_API_KEY=%s\nOTHER_TOKEN=%s\nPLAIN=\"%s\"\nEMPTY=\n"
        % (FAKE_KEY, FAKE_OTHER, FAKE_PLAIN), encoding="utf-8")
    (root / ".gitignore").write_text(".env\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "first commit")
    return root


def test_git_state_is_in_the_prompt(repo):
    out = SH.build(repo)
    sha = git(repo, "rev-parse", "--short", "HEAD").strip()
    assert str(repo) in out
    assert "work-branch" in out
    assert sha in out
    assert "clean" in out
    assert "first commit" in out


def test_dirty_tree_is_reported(repo):
    (repo / "new.txt").write_text("x\n", encoding="utf-8")
    assert "dirty" in SH.build(repo)


def test_branch_override(repo):
    assert "other-branch" in SH.build(repo, branch="other-branch")


def test_newest_brief_flags_and_whats_next(repo):
    out = SH.build(repo)
    assert "docs/superpowers/sessions/2026-09-30-session-brief.md" in out
    assert "**Flag one:** the first open question." in out
    assert "a nested note under flag one" in out
    assert "**Flag two:**" in out
    assert "Not a bullet" not in out
    assert "Old flag" not in out
    assert "1. Build the London board." in out
    assert "2. Post the decisions batch." in out


def test_empty_whats_next_is_said(repo):
    p = repo / "docs/superpowers/sessions/2026-09-30-session-brief.md"
    p.write_text(BRIEF.split("## What's Next")[0] + "## What's Next\n", encoding="utf-8")
    assert "empty" in SH.build(repo).lower()


def test_newest_plan_and_its_first_open_task(repo):
    out = SH.build(repo)
    assert "docs/superpowers/plans/2026-10-02-new-plan.md" in out
    assert "### Task 2: The next one" in out
    assert "Task 1: Done already" not in out
    assert "Task 3: Later" not in out


def test_artifact_urls_are_deduplicated(repo):
    out = SH.build(repo)
    assert out.count("https://claude.ai/artifact/BoardId123") == 1
    assert out.count("https://claude.ai/artifact/PageXyz-9") == 1


def test_only_the_last_five_batches_are_read(repo):
    batches = repo / "docs/reference/answer-board/batches"
    (batches / "2026-01-01-oldest.md").write_text("https://claude.ai/artifact/AncientOne\n",
                                                  encoding="utf-8")
    for i in range(5):
        (batches / ("2026-10-0%d-z.md" % (i + 1))).write_text("nothing\n", encoding="utf-8")
    assert "AncientOne" not in SH.build(repo)


def test_standing_instructions(repo):
    out = SH.build(repo)
    assert "Read CLAUDE.md, docs/reference/page-run.md, the newest brief and MEMORY.md first" in out
    assert "Watch the answer board and any open page board with ArtifactComments at session start" in out
    assert ("Commit after every task; never push unless the user explicitly says so "
            "(CLAUDE.md rule 3).") in out


def test_gemini_line_when_key_is_set(repo):
    out = SH.build(repo)
    assert ("GEMINI_API_KEY is set in .env — delete it when image work is done "
            "(breeder's instruction, 2026-10-02)") in out


def test_no_gemini_set_line_when_key_is_empty_or_absent(repo):
    (repo / ".env").write_text("GEMINI_API_KEY=\n", encoding="utf-8")
    assert "GEMINI_API_KEY is set" not in SH.build(repo)
    (repo / ".env").unlink()
    assert "GEMINI_API_KEY is set" not in SH.build(repo)


def test_no_secret_ever_reaches_the_prompt(repo):
    # A brief that quotes a key by accident must not leak it either.
    p = repo / "docs/superpowers/sessions/2026-09-30-session-brief.md"
    p.write_text(BRIEF.replace("the second open question.",
                               "pasted %s and %s by mistake" % (FAKE_PLAIN, "AIzaSyFAKEfake123")),
                 encoding="utf-8")
    out = SH.build(repo)
    for value in (FAKE_KEY, FAKE_OTHER, FAKE_PLAIN, "AIzaSyFAKEfake123"):
        assert value not in out
    assert not SECRET_SHAPE.search(out), SECRET_SHAPE.search(out).group(0)


def test_write_saves_the_dated_file(repo, capsys):
    rc = SH.main(["--write"], root=repo, today="2026-10-02")
    assert rc == 0
    saved = repo / "docs/reference/handoff/2026-10-02-work-branch.md"
    assert saved.is_file()
    printed = capsys.readouterr().out
    assert "### Task 2: The next one" in saved.read_text(encoding="utf-8")
    assert "### Task 2: The next one" in printed


def test_print_only_writes_nothing(repo, capsys):
    assert SH.main([], root=repo) == 0
    assert not (repo / "docs/reference/handoff").exists()
    assert "work-branch" in capsys.readouterr().out


# ── .env parsing: every form a dotenv loader accepts must still be redacted ──

def leak_check(repo, env_text, secrets, quoted_in_brief=True):
    """Write `env_text` as .env, quote every secret in the brief, and assert none survives."""
    (repo / ".env").write_text(env_text, encoding="utf-8")
    p = repo / "docs/superpowers/sessions/2026-09-30-session-brief.md"
    if quoted_in_brief:
        p.write_text(BRIEF.replace("the second open question.",
                                   "pasted " + " and ".join(secrets) + " by mistake"),
                     encoding="utf-8")
    out = SH.build(repo)
    for value in secrets:
        assert value not in out, value
    return out


def test_double_quoted_value_with_inline_comment(repo):
    leak_check(repo, 'B="quotedSECRET1" # note\n', ["quotedSECRET1"])


def test_single_quoted_value_with_inline_comment(repo):
    leak_check(repo, "B='singleSECRET9' # note\n", ["singleSECRET9"])


def test_unquoted_value_with_inline_comment(repo):
    leak_check(repo, "C=plainSECRET2 # note\n", ["plainSECRET2"])


def test_export_prefix(repo):
    leak_check(repo, "export EXPORTED_THING=exportSECRET3\n", ["exportSECRET3"])


def test_short_value_of_a_secret_looking_key_is_redacted(repo):
    out = leak_check(repo, "ABC_KEY=abc12\n", ["abc12"])
    assert "[redacted]" in out


def test_short_value_of_an_ordinary_key_is_left_alone(repo):
    (repo / ".env").write_text("MODE=dev\n", encoding="utf-8")
    p = repo / "docs/superpowers/sessions/2026-09-30-session-brief.md"
    p.write_text(BRIEF.replace("the second open question.", "dev mode"), encoding="utf-8")
    assert "dev mode" in SH.build(repo)


def test_multi_line_quoted_value_is_redacted_line_by_line(repo):
    env = 'CERT_BLOB="firstLINEsecret\nsecondLINEsecret\nthirdLINEsecret" # note\nNEXT=after\n'
    pairs = SH.parse_env(env)
    assert pairs[0] == ("CERT_BLOB", "firstLINEsecret\nsecondLINEsecret\nthirdLINEsecret")
    assert pairs[1] == ("NEXT", "after")
    leak_check(repo, env, ["firstLINEsecret", "secondLINEsecret", "thirdLINEsecret"])


def test_parse_env_forms():
    assert SH.parse_env('A="x y" # c\nB=\'z\' #c\nC=w # c\nexport D=v\n# E=no\nF=\n') == [
        ("A", "x y"), ("B", "z"), ("C", "w"), ("D", "v"), ("F", "")]


def test_new_key_shapes_are_redacted_without_an_env(repo):
    (repo / ".env").unlink()
    shapes = ["ghp_FAKEfake0123456789", "github_pat_FAKE_fake012345", "xoxb-111-fake-token",
              "AKIAABCDEFGHIJKLMNOP"]
    out = leak_check(repo, "", shapes)
    assert not SECRET_SHAPE.search(out)


def test_git_missing_or_hung_is_not_fetched(repo, monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError("git")
    monkeypatch.setattr(SH.subprocess, "run", boom)
    out = SH.build(repo)
    assert "NOT FETCHED" in out

    def hang(*a, **k):
        assert k.get("timeout") == 20
        raise SH.subprocess.TimeoutExpired("git", 20)
    monkeypatch.setattr(SH.subprocess, "run", hang)
    assert "NOT FETCHED" in SH.build(repo)


def test_plan_tie_on_the_same_date_goes_to_the_newest_mtime(repo):
    import os
    plans = repo / "docs/superpowers/plans"
    a, b = plans / "2026-10-02-aaa.md", plans / "2026-10-02-zzz.md"
    a.write_text("### Task 1: From aaa\n- [ ] s\n", encoding="utf-8")
    b.write_text("### Task 1: From zzz\n- [ ] s\n", encoding="utf-8")
    os.utime(b, (1_000_000, 1_000_000))
    os.utime(plans / "2026-10-02-new-plan.md", (1_000_000, 1_000_000))
    os.utime(a, (2_000_000_000, 2_000_000_000))
    out = SH.build(repo)
    assert "2026-10-02-aaa.md" in out and "From aaa" in out


def test_escaped_quote_does_not_end_a_double_quoted_value(repo):
    env = 'G_TOKEN="esc\\"tailSECRET5" # note\n'
    assert SH.parse_env(env) == [("G_TOKEN", 'esc"tailSECRET5')]
    out = leak_check(repo, env, ['esc\\"tailSECRET5', 'esc"tailSECRET5'])
    assert "tailSECRET5" not in out


def test_one_or_two_character_secret_values_are_not_substituted(repo):
    (repo / ".env").write_text("H_ID=1\nJ_KEY=42\n", encoding="utf-8")
    out = SH.build(repo)
    assert "1. Build the London board." in out
    assert "2. Post the decisions batch." in out
    assert "[redacted]" not in out
