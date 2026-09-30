from migration_parity import visible_stats, compare


def test_visible_stats_counts():
    st = visible_stats('<html><body><h1>A</h1><p>one two three</p><img src="x"><iframe src="y"></iframe><script>zzz</script></body></html>')
    assert st["words"] == 4 and st["headings"] == ["h1:A"] and st["images"] == 1 and st["embeds"] == 1


def test_compare_flags_big_drop():
    old = {"words": 1000, "headings": ["h1:A", "h2:B"], "images": 3, "embeds": 1}
    ok = compare(old, {"words": 985, "headings": ["h1:A", "h2:B"], "images": 3, "embeds": 1}, allowance=0)
    bad = compare(old, {"words": 900, "headings": ["h1:A"], "images": 2, "embeds": 1}, allowance=0)
    assert ok["pass"] and not bad["pass"] and "words" in bad["failures"] and "headings" in bad["failures"]


def test_compare_allowance_covers_known_removals():
    old = {"words": 1000, "headings": ["h1:A"], "images": 3, "embeds": 0}
    new = {"words": 880, "headings": ["h1:A"], "images": 2, "embeds": 0}
    assert compare(old, new, allowance=120, image_allowance=1)["pass"]


# --- end-to-end fixtures -------------------------------------------------------------
import json
import pytest
import migration_parity

PROSE = " ".join(["alpha"] * 120)
CARD_PROSE = " ".join(["pup"] * 200)


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _site(tmp_path, pages, sources, dists):
    """Lay out a root (page-map), a fake export tree and a fake dist tree."""
    root, src, dist = tmp_path / "root", tmp_path / "src", tmp_path / "dist"
    _write(root / "data" / "page-map.json",
           json.dumps({"generated_from": str(src), "pages": pages}))
    for slug, html in sources.items():
        _write(src / slug / "index.html", html)
    for slug, html in dists.items():
        _write(dist / slug / "index.html", html)
    return root, src, dist


def _source(body):
    return '<html><body><div class="entry-content">%s</div></body></html>' % body


def _run(root, src, dist):
    with pytest.raises(SystemExit) as exc:
        migration_parity.main(root=root, src=src, dist=dist)
    assert exc.value.code == 1
    return (root / "docs" / "reports" / "parity.md").read_text(encoding="utf-8")


def test_main_fails_on_missing_built_page(tmp_path):
    pages = [{"url": "/good/", "kind": "rich", "defects": []},
             {"url": "/gone/", "kind": "rich", "defects": []}]
    body = "<h2>Head</h2><p>%s</p>" % PROSE
    root, src, dist = _site(
        tmp_path, pages, {"good": _source(body), "gone": _source(body)},
        {"good": '<html><body><article class="prose-migrated">%s</article></body></html>' % body})
    report = _run(root, src, dist)
    assert "FAIL not built" in report
    assert "examined 2 pages, 1 failing" in report
    assert "| /good/ | 121→121→121 |" in report      # the intact row still passes


def test_main_fails_when_article_scope_is_renamed(tmp_path):
    pages = [{"url": "/good/", "kind": "rich", "defects": []}]
    body = "<h2>Head</h2><p>%s</p>" % PROSE
    root, src, dist = _site(
        tmp_path, pages, {"good": _source(body)},
        {"good": '<html><body><article class="prose">%s</article></body></html>' % body})
    assert "FAIL no article.prose-migrated" in _run(root, src, dist)


def test_main_fails_when_removals_swallow_the_page(tmp_path):
    kept = "<h2>Head</h2><p>%s</p>" % PROSE
    card = '<div class="bsuk-puppy-card"><h3>Kane</h3><p>Meet Kane %s</p></div>' % CARD_PROSE
    pages = [{"url": "/pups/", "kind": "rich", "defects": []}]
    root, src, dist = _site(
        tmp_path, pages, {"pups": _source(kept + card)},
        {"pups": '<html><body><article class="prose-migrated">%s</article></body></html>' % kept})
    report = _run(root, src, dist)
    assert "FAIL over-removal 324→121" in report and "| 1 |" in report
