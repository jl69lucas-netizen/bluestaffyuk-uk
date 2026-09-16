import json
import pathlib

import pytest

from redirect_check import (check_rules, exists, is_asset, main, match_rule, page_refs,
                            resolve, shadowed_rules)

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
    # /old/ must appear as a redirected-warning table row, never as a dead link.
    assert "| /index.html | /old/ | /good/ |" in report
    assert "dead link: /old/" not in report
    assert "SITE_URL_PLACEHOLDER occurrences: 0" in report
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


def test_exists_page_asset_and_root(tmp_path):
    _write(tmp_path / "index.html", "root")
    _write(tmp_path / "blog" / "index.html", "page")
    _write(tmp_path / "images" / "x.webp", "bytes")
    assert exists(tmp_path, "/")
    assert exists(tmp_path, "/blog/")
    assert exists(tmp_path, "/images/x.webp")
    assert not exists(tmp_path, "/blog/nope/")
    assert not exists(tmp_path, "/images/missing.webp")


def test_check_rules_target_missing_and_hops(tmp_path):
    _write(tmp_path / "c" / "index.html", "ok")
    rules = [("/a/", "/b/"), ("/b/", "/c/"), ("/x/", "/gone/")]
    problems, examined = check_rules(rules, tmp_path)
    joined = " ".join(problems)
    assert examined == 3
    assert "FAIL target missing: /x/ -> /gone/" in joined
    assert "FAIL target missing: /a/ -> /b/" in joined
    assert "FAIL 2 hops: /a/ -> /c/" in joined
    assert "FAIL chain: /a/ -> /b/ -> /c/" in joined


def test_shadowed_rule_is_dead_configuration():
    rules = [("/category/*", "/blog/"), ("/category/old/", "/blog/old-post/")]
    problems = shadowed_rules(rules)
    assert len(problems) == 1 and "/category/old/" in problems[0]
    assert "/category/*" in problems[0]
    # order matters: the concrete rule first is reachable
    assert shadowed_rules(list(reversed(rules))) == []


def test_check_rules_reports_shadowing(tmp_path):
    _write(tmp_path / "blog" / "index.html", "ok")
    _write(tmp_path / "blog" / "old-post" / "index.html", "ok")
    problems, _ = check_rules([("/category/*", "/blog/"),
                               ("/category/old/", "/blog/old-post/")], tmp_path)
    assert any("shadowed rule" in p for p in problems)


def test_page_refs_srcset_and_dedupe():
    refs = page_refs('<img src="/a.webp" srcset="/a.webp 1x, /b.webp 2x, ../rel.webp 3x">'
                     '<a href="/a.webp?v=2#frag">dup</a><a href="https://x.test/e/">ext</a>')
    assert refs == ["/a.webp", "/b.webp"]


def test_external_feed_href_not_flagged(tmp_path):
    root, dist = tmp_path / "root", tmp_path / "dist"
    _write(root / "data" / "redirects.json", json.dumps({"redirects": []}))
    _write(dist / "index.html", '<a href="https://partner.example/feed/">partner</a>')
    main(root=root, dist=dist)          # must not raise


def test_first_party_feed_page_is_not_a_leftover(tmp_path):
    """A built /news/feed/ page is a real page, so the leftover check must stay quiet."""
    root, dist = tmp_path / "root", tmp_path / "dist"
    _write(root / "data" / "redirects.json", json.dumps({"redirects": []}))
    _write(dist / "index.html", '<a href="/news/feed/">feed page</a>')
    _write(dist / "news" / "feed" / "index.html", "<p>built</p>")
    main(root=root, dist=dist)          # must not raise


def test_wp_feed_href_still_fails(tmp_path, capsys):
    root, dist = tmp_path / "root", tmp_path / "dist"
    _write(root / "data" / "redirects.json", json.dumps({"redirects": []}))
    _write(dist / "index.html", '<a href="/some-post/feed/">wp</a>')
    with pytest.raises(SystemExit):
        main(root=root, dist=dist)
    assert "WP leftover /feed/ href /some-post/feed/" in capsys.readouterr().out


def test_placeholder_count_line(tmp_path, capsys):
    root, dist = tmp_path / "root", tmp_path / "dist"
    _write(root / "data" / "redirects.json", json.dumps({"redirects": []}))
    _write(dist / "index.html", "SITE_URL_PLACEHOLDER twice: SITE_URL_PLACEHOLDER")
    main(root=root, dist=dist)
    assert "SITE_URL_PLACEHOLDER occurrences: 2 (expected until launch)" in \
        capsys.readouterr().out


def test_main_fails_without_dist(tmp_path, capsys):
    root = tmp_path / "root"
    _write(root / "data" / "redirects.json", json.dumps({"redirects": []}))
    with pytest.raises(SystemExit) as exc:
        main(root=root, dist=tmp_path / "nodist")
    assert exc.value.code == 1
    assert "FAIL dist missing or unbuilt (run npm run build)" in capsys.readouterr().out


def test_summary_notes_refs_are_per_page_distinct(tmp_path, capsys):
    root, dist = tmp_path / "root", tmp_path / "dist"
    _write(root / "data" / "redirects.json", json.dumps({"redirects": []}))
    _write(dist / "index.html", '<a href="/a/">one</a><a href="/a/">again</a>')
    _write(dist / "a" / "index.html", '<a href="/">home</a>')
    main(root=root, dist=dist)
    out = capsys.readouterr().out
    assert "examined 0 redirects, 2 internal refs (distinct per page)" in out


def test_bare_root_feed_href_is_flagged(tmp_path, capsys):
    """`href="/feed/"` — the single most common WordPress remnant — must be caught.

    Regression: HREF_FEED_RE required at least one path segment before `/feed/`
    (`/[^"']*/feed/`), so a bare root feed link matched nothing and the check reported PASS
    on a page that still advertised the WordPress feed.
    """
    root, dist = tmp_path / "root", tmp_path / "dist"
    _write(root / "data" / "redirects.json", json.dumps({"redirects": []}))
    _write(dist / "index.html", '<a href="/feed/">Entries RSS</a>')
    with pytest.raises(SystemExit):
        main(root=root, dist=dist)
    assert "/feed/" in capsys.readouterr().out


def test_built_root_feed_page_is_not_a_leftover(tmp_path):
    """The existence escape hatch still applies to the bare root form, not just nested ones."""
    root, dist = tmp_path / "root", tmp_path / "dist"
    _write(root / "data" / "redirects.json", json.dumps({"redirects": []}))
    _write(dist / "index.html", '<a href="/feed/">our feed</a>')
    _write(dist / "feed" / "index.html", "<p>built</p>")
    main(root=root, dist=dist)          # must not raise


def test_duplicate_concrete_rule_is_dead_configuration():
    """Two rules with the same `from` look like an override; the second never applies."""
    rules = [("/old-page/", "/new-page/"), ("/old-page/", "/somewhere-else/")]
    problems = shadowed_rules(rules)
    assert len(problems) == 1
    assert "duplicate rule" in problems[0]
    assert "/somewhere-else/" in problems[0] and "/new-page/" in problems[0]
    # Distinct sources are not duplicates, and an exact repeat of source AND target is
    # still reported — a copy-paste twice over is still a line that does nothing.
    assert shadowed_rules([("/a/", "/x/"), ("/b/", "/x/")]) == []
    assert len(shadowed_rules([("/a/", "/x/"), ("/a/", "/x/")])) == 1
