"""scripts/board_style.py — the one presentation layer every board generator embeds.

The user's two picks of 2026-10-07 (docs/superpowers/plans/2026-10-07-board-readability.md):
layout A, field cards with a colour per role (Recommended, why, wedge, trade-off, NOT FETCHED),
and paragraph Option 2, a plain summary first with the original folded underneath. The colours
are tokens defined on bare `:root` and redefined for both dark-theme selectors, so a board reads
in either theme; the script carries the legend and the card transform.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import board_style as BS  # noqa: E402

ROLE_TOKENS = ("--rec-bg", "--rec-line", "--why", "--why-bg", "--wedge", "--wedge-bg",
               "--trade", "--trade-bg", "--nf", "--nf-bg")
DARK_MEDIA = '@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){'
DARK_ATTR = ':root[data-theme="dark"]{'


def _block(css, opener):
    """The declarations of the rule that starts with `opener`, up to its closing brace."""
    i = css.index(opener) + len(opener)
    return css[i:css.index("}", i)]


def _bare_root(css):
    m = re.search(r"(?<![\w\]\)-]):root\{([^}]*)\}", css)
    assert m, "no bare :root rule"
    return m.group(1)


def test_every_role_token_is_defined_on_bare_root_and_in_both_dark_blocks():
    css = BS.CSS
    for name, decls in (("bare :root", _bare_root(css)),
                        ("prefers-color-scheme dark", _block(css, DARK_MEDIA)),
                        ('[data-theme="dark"]', _block(css, DARK_ATTR))):
        for tok in ROLE_TOKENS:
            assert re.search(re.escape(tok) + r"\s*:", decls), f"{tok} missing from {name}"


def test_the_dark_values_differ_from_the_light_ones():
    light, dark = _bare_root(BS.CSS), _block(BS.CSS, DARK_ATTR)

    def val(decls, tok):
        return re.search(re.escape(tok) + r"\s*:\s*([^;]+)", decls).group(1).strip()
    for tok in ROLE_TOKENS:
        assert val(light, tok) != val(dark, tok), tok
    assert _block(BS.CSS, DARK_MEDIA) == dark       # both dark selectors carry the same set


def test_the_css_styles_the_roles_the_legend_and_the_folded_summary():
    for sel in (".legend", ".recmark", ".nf", ".fld.why", ".fld.wedge", ".fld.trade",
                ".plain", ".box.care", ".box.cost", "details.full"):
        assert sel in BS.CSS, sel


def test_the_script_carries_the_legend_and_the_card_transform():
    s = BS.SCRIPT
    for label in ("Recommended", "Why / why it ranks", "Weakness · our wedge",
                  "Trade-off · risk", "NOT FETCHED"):
        assert label in s, label
    assert "legend" in s
    # the card transform: a long table becomes one field card per row
    assert "fcard" in s and "replaceWith" in s
    # the plain summary renders above the original, which is folded in <details class="full">
    assert "board-summaries" in s and "'full'" in s


def test_the_script_never_rewrites_form_controls_into_cards():
    # The page board's tables hold radio pickers and anchors the approve flow finds by id.
    assert "input,select,textarea,button,iframe" in BS.SCRIPT


def test_summaries_json_is_safe_inside_a_script_block():
    out = BS.summaries_json({"sections": {"A": {"bullets": ["x </script> y", "<!-- z"]}}})
    assert "</script" not in out and "<!--" not in out
    assert json.loads(out)["sections"]["A"]["bullets"][0] == "x </script> y"


def test_the_validator_holds_a_summary_to_its_shape():
    titles = ["Status", "6. Why Competitors Rank"]
    ok = {"sections": {"Status": {"bullets": ["One short plain line."], "care": ["Read this with care."]}}}
    assert BS.validate_summaries(ok, titles) == []
    long = " ".join(["word"] * 26)
    cases = {
        "over 25 words": {"sections": {"Status": {"bullets": [long]}}},
        "more than 6": {"sections": {"Status": {"bullets": ["a b"] * 7}}},
        "file path": {"sections": {"Status": {"bullets": ["Read from data/settings.json today."]}}},
        "backtick": {"sections": {"Status": {"bullets": ["The `deposit_gbp` field."]}}},
        "no such section": {"sections": {"Nope": {"bullets": ["a b"]}}},
        "unknown kind": {"sections": {"Status": {"bullets": ["a b"], "notes": ["c"]}}},
        "no bullets": {"sections": {"Status": {"care": ["a b"]}}},
    }
    for why, s in cases.items():
        assert BS.validate_summaries(s, titles), why


def test_the_validator_resolves_item_paths():
    ok = {"items": {"angles[0]": {"bullets": ["The idea in plain words."]}}}
    assert BS.validate_summaries(ok, [], item_paths={"angles[0]"}) == []
    bad = {"items": {"angles[9]": {"bullets": ["a b"]}}}
    assert BS.validate_summaries(bad, [], item_paths={"angles[0]"})
