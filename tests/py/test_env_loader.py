"""scripts/env_loader.py: every script and agent finds the repo's .env keys without being told
(the breeder, 2026-10-07: "make so all future agents can see and use the API key").

The loader fills os.environ from the checkout's own .env, then from the main checkout's .env
(a worktree has no .env of its own: it is gitignored). A key already in the environment wins,
and nothing is ever printed.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import env_loader as EL  # noqa: E402


def test_fills_a_missing_key_from_the_checkouts_env(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("GEMINI_API_KEY=abc123\nOTHER='x y'\n")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OTHER", raising=False)
    env = {}
    loaded = EL.load_env(roots=[tmp_path], environ=env)
    assert env["GEMINI_API_KEY"] == "abc123" and env["OTHER"] == "x y"
    assert loaded == ["GEMINI_API_KEY", "OTHER"]


def test_a_key_already_set_wins(tmp_path):
    (tmp_path / ".env").write_text("GEMINI_API_KEY=from-file\n")
    env = {"GEMINI_API_KEY": "from-shell"}
    assert EL.load_env(roots=[tmp_path], environ=env) == []
    assert env["GEMINI_API_KEY"] == "from-shell"


def test_the_first_root_that_holds_a_key_wins(tmp_path):
    a, b = tmp_path / "worktree", tmp_path / "main"
    a.mkdir(), b.mkdir()
    (b / ".env").write_text("GEMINI_API_KEY=main\nSITE_URL=s\n")
    env = {}
    EL.load_env(roots=[a, b], environ=env)          # the worktree has no .env
    assert env == {"GEMINI_API_KEY": "main", "SITE_URL": "s"}
    (a / ".env").write_text("GEMINI_API_KEY=wt\n")
    env = {}
    EL.load_env(roots=[a, b], environ=env)
    assert env["GEMINI_API_KEY"] == "wt" and env["SITE_URL"] == "s"


def test_default_roots_are_this_checkout_then_the_main_checkout():
    roots = EL.default_roots()
    assert roots[0] == ROOT
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            cwd=ROOT, capture_output=True, text=True).stdout.strip()
    assert pathlib.Path(common).parent in roots


def test_it_never_prints(tmp_path, capsys):
    (tmp_path / ".env").write_text("GEMINI_API_KEY=secret-value\n")
    EL.load_env(roots=[tmp_path], environ={})
    out = capsys.readouterr()
    assert "secret-value" not in out.out + out.err


def test_the_image_paths_load_it():
    """The Gemini call sites load the .env themselves, so no agent has to export a key."""
    for f in ("scripts/gemini_log.py", "scripts/gen_manchester_stop4.py"):
        assert "env_loader" in (ROOT / f).read_text(), f
