"""`tests/render/lib/env.mjs` is the one place a `.env` line is parsed for the harness.

`tests/render/checks/form.ts` throws without `PUBLIC_FORMSPREE_ID`, so the Playwright config
loads `.env` itself rather than making every caller `set -a; . ./.env`. That parse is small
and therefore easy to get subtly wrong: quoted values keep their quotes, `export KEY=` lines
are skipped, an already-set variable gets clobbered. Each of those produces a harness that
runs with the wrong value rather than failing, so the parser is a plain `.mjs` module and
this test runs the REAL module under node — the simplest honest option, and the reason the
loader is not TypeScript: no compiler step stands between the test and the shipped code.

No value is asserted from the real `.env`; every fixture here is invented.
"""
import json
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE = ROOT / "tests/render/lib/env.mjs"

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")

FIXTURE = "\n".join([
    "# a comment",
    "",
    "PLAIN=abc",
    'QUOTED="dq"',
    "SQUOTED='sq'",
    "export EXPORTED=xyz",
    "  SPACED=pad  ",
    "ALREADY=fromfile",
    "HALF=\"mismatched'",
    "lowercase=ignored",
    "NOEQUALS",
])


def _run(tmp_path, preset):
    (tmp_path / ".env").write_text(FIXTURE, encoding="utf-8")
    src = (
        f"import {{ loadEnv }} from {json.dumps(str(MODULE))};"
        f"const env = {json.dumps(preset)};"
        f"loadEnv({json.dumps(str(tmp_path / '.env'))}, env);"
        "console.log(JSON.stringify(env));"
    )
    r = subprocess.run(["node", "--input-type=module", "-e", src],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_it_parses_the_shapes_a_hand_written_env_actually_has(tmp_path):
    env = _run(tmp_path, {})
    assert env["PLAIN"] == "abc"
    assert env["QUOTED"] == "dq", "one matching pair of quotes is stripped"
    assert env["SQUOTED"] == "sq"
    assert env["EXPORTED"] == "xyz", "`export KEY=value` is a valid .env line"
    assert env["SPACED"] == "pad"
    assert env["HALF"] == "\"mismatched'", "mismatched quotes are not a pair — left alone"


def test_it_skips_comments_blanks_and_non_keys(tmp_path):
    env = _run(tmp_path, {})
    for absent in ("lowercase", "NOEQUALS", "#"):
        assert absent not in env


def test_an_existing_variable_is_never_overridden(tmp_path):
    env = _run(tmp_path, {"ALREADY": "fromshell"})
    assert env["ALREADY"] == "fromshell", (
        "an explicit `FOO=bar npm run ...` must win over .env, or debugging is impossible")


def test_a_missing_env_file_is_not_an_error(tmp_path):
    src = (
        f"import {{ loadEnv }} from {json.dumps(str(MODULE))};"
        "const env = {};"
        f"loadEnv({json.dumps(str(tmp_path / 'nope.env'))}, env);"
        "console.log(JSON.stringify(env));"
    )
    r = subprocess.run(["node", "--input-type=module", "-e", src],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout) == {}


def test_the_loader_never_prints_a_value(tmp_path):
    assert "console." not in MODULE.read_text(encoding="utf-8"), (
        "the loader handles secrets; it must not log, not even on failure")


def test_the_playwright_config_uses_this_module_and_does_not_reimplement_it():
    cfg = (ROOT / "tests/render/playwright.config.ts").read_text(encoding="utf-8")
    assert "./lib/env.mjs" in cfg
    assert "readFileSync" not in cfg, "one parser, not two"
