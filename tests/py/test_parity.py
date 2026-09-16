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
