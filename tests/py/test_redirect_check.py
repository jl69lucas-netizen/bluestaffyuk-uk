import json
import pathlib

import pytest

from redirect_check import is_asset, main, match_rule, resolve

RULES = [("/form/*", "/uk-blue-staffy-breeders-contact/"), ("/a/", "/b/"), ("/b/", "/c/"),
         ("/:slug/feed/", "/"), ("/:a/:b/feed/", "/")]


def test_match_exact_and_splat():
    assert match_rule("/form/2029/", RULES) == "/uk-blue-staffy-breeders-contact/"
    assert match_rule("/a/", RULES) == "/b/"
    assert match_rule("/nope/", RULES) is None


def test_match_placeholders():
    assert match_rule("/privacy-policy-uk/feed/", RULES) == "/"
    assert match_rule("/uk-locations/blue-staffy-puppies-york/feed/", RULES) == "/"
    assert match_rule("/x/y/z/feed/", RULES) is None


def test_resolve_detects_chain():
    hops, final = resolve("/a/", RULES)
    assert hops == 2 and final == "/c/"


def test_is_asset():
    assert is_asset("/images/x.webp") and is_asset("/sitemap_index.xml") and not is_asset("/blog/")


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_main_end_to_end_fixture(tmp_path, capsys):
    """A tiny root+dist exercising each verdict the gate can reach."""
    root, dist = tmp_path / "root", tmp_path / "dist"
    _write(root / "data" / "redirects.json", json.dumps({"redirects": [
        {"from": "/old/", "to": "/good/", "type": 301},
        {"from": "/form/*", "to": "/good/", "type": 301},
    ]}))
    _write(dist / "index.html",
           '<a href="/good/">ok</a> <a href="/old/">redirected</a> '
           '<a href="/missing/">dead</a> <a href="https://x.test/">ext</a>')
    _write(dist / "good" / "index.html", '<a href="#top">anchor</a> wp-json leftover')

    with pytest.raises(SystemExit) as exc:
        main(root=root, dist=dist)
    assert exc.value.code == 1

    report = (root / "docs" / "reports" / "redirects.md").read_text(encoding="utf-8")
    assert "/missing/" in report and "wp-json" in report
    assert "/old/" in report            # listed as a redirected ref, not a dead one
    out = capsys.readouterr().out
    assert "examined 2 redirects" in out


def test_main_passes_on_clean_fixture(tmp_path):
    root, dist = tmp_path / "root", tmp_path / "dist"
    _write(root / "data" / "redirects.json", json.dumps({"redirects": [
        {"from": "/old/", "to": "/good/", "type": 301},
    ]}))
    _write(dist / "index.html", '<a href="/good/">ok</a>')
    _write(dist / "good" / "index.html", "<p>fine</p>")
    main(root=root, dist=dist)          # must not raise
