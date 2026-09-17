"""The release guard on IndexNow is the only thing between a placeholder and Bing.

`scripts/indexnow_submit.py` is ported from CAG and inactive until project 6. The guard is
worth a test rather than a comment because the failure is silent and external: a run without
it POSTs `SITE_URL_PLACEHOLDER` to a public API, and IndexNow reads junk submissions as a
trust signal about the host. So every test here patches `urllib.request.urlopen` to raise —
a test that passes because the network was down would prove nothing.
"""
import importlib
import sys

import pytest


def _load(monkeypatch, tmp_path, **env):
    """Import the script fresh with a given environment: HOST is read at import time."""
    for k in ("BSUK_RELEASE", "SITE_URL", "INDEXNOW_KEY"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    (tmp_path / "public").mkdir(exist_ok=True)
    monkeypatch.chdir(tmp_path)
    sys.modules.pop("indexnow_submit", None)
    mod = importlib.import_module("indexnow_submit")

    def _no_network(*a, **k):  # pragma: no cover - firing this IS the failure
        raise AssertionError("the script opened a socket")

    monkeypatch.setattr(mod.urllib.request, "urlopen", _no_network)
    return mod


def _run(mod, monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", ["indexnow_submit.py", *argv])
    with pytest.raises(SystemExit) as e:
        mod.main()
    return e.value.code


def test_refuses_without_the_release_flag(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, SITE_URL="https://example.invalid")
    assert _run(mod, monkeypatch, ["index"]) == 2
    err = capsys.readouterr().err
    assert err.startswith("REFUSED: IndexNow is inactive until project 6.")


def test_refuses_the_placeholder_even_with_the_flag(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://SITE_URL_PLACEHOLDER")
    assert _run(mod, monkeypatch, ["index"]) == 2
    assert "still a placeholder" in capsys.readouterr().err


def test_refuses_an_unset_site_url_even_with_the_flag(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1")
    assert _run(mod, monkeypatch, ["index"]) == 2
    assert "unset or still a placeholder" in capsys.readouterr().err


def test_dry_run_prints_the_urls_and_sends_nothing(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://example.invalid")
    monkeypatch.setattr(sys, "argv", ["indexnow_submit.py", "--dry-run", "puppies", "/"])
    assert mod.main() == 0
    out = capsys.readouterr().out
    assert "https://example.invalid/puppies/" in out
    assert "https://example.invalid/" in out
    assert "--dry-run" in out


def test_dry_run_never_prints_the_key(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://example.invalid",
                INDEXNOW_KEY="0123456789abcdef0123456789abcdef")
    monkeypatch.setattr(sys, "argv", ["indexnow_submit.py", "--dry-run", "puppies"])
    assert mod.main() == 0
    captured = capsys.readouterr()
    assert "0123456789abcdef" not in captured.out + captured.err


def test_malformed_sitemap_is_a_clean_refusal(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://example.invalid")
    (tmp_path / "public" / "page-sitemap.xml").write_text(
        "<urlset><url><loc>https://example.inv", encoding="utf-8")
    assert _run(mod, monkeypatch, ["--all"]) == 2
    err = capsys.readouterr().err
    assert err.startswith("REFUSED: no submittable URLs")
    assert "Traceback" not in err


def test_build_artifacts_are_filtered_out(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://example.invalid")
    monkeypatch.setattr(sys, "argv", ["indexnow_submit.py", "--dry-run", "puppies", "thank-you"])
    assert mod.main() == 0
    out = capsys.readouterr().out
    assert "/thank-you/" not in out
    assert "/puppies/" in out
