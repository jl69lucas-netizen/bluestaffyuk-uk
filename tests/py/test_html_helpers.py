# tests/py/test_html_helpers.py
#
# scripts/_html.py is the one implementation of strip_tags / unescape / text_of. Before
# it existed, aeo_audit.py and evidence_audit.py each carried a copy with a DIFFERENT
# entity table (&#39; only in one, &middot; only in the other), so the same page yielded
# different text to two gates. These tests pin the union table and the shared behaviour.
import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import _html
import aeo_audit as A
import evidence_audit as E


def test_strip_tags_drops_script_and_style_bodies():
    html = "<p>keep</p><script>var x = 'drop';</script><style>.a{color:red}</style>"
    out = _html.strip_tags(html)
    assert "keep" in out and "drop" not in out and "color:red" not in out


def test_unescape_covers_the_union_of_both_gates_tables():
    """&#39; came from the evidence gate, &middot; from the AEO gate: one table now."""
    pairs = {"&amp;": "&", "&nbsp;": " ", "&middot;": "·", "&ndash;": "–",
             "&mdash;": "—", "&rsquo;": "’", "&#8217;": "’", "&quot;": '"',
             "&#39;": "'"}
    for raw, want in pairs.items():
        assert _html.unescape(raw) == want, raw


def test_text_of_collapses_whitespace_and_unescapes():
    assert _html.text_of("<p>Lisa   &amp;\n  Co</p>") == "Lisa & Co"


def test_both_gates_use_the_shared_implementation():
    assert A.text_of is _html.text_of
    assert E.text_of is _html.text_of
    assert A.unescape is _html.unescape and E.unescape is _html.unescape
    assert A.strip_tags is _html.strip_tags and E.strip_tags is _html.strip_tags


def test_the_two_gates_now_read_one_apostrophe_the_same_way():
    html = "<p>Bright&#39;s pups &middot; home-raised</p>"
    assert A.text_of(html) == E.text_of(html) == "Bright's pups · home-raised"
