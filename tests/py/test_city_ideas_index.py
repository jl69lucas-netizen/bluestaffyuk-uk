"""docs/research/london-components/ideas-index.md — the London component pass's ideas index
(Plan 1, Task 1). The screenshots and the two idea-sheet folders live OUTSIDE the repo; the
index is the repo's only record of them. It must cover all fifteen components in city-page
order, cite only files that exist (checked only where the folder is present, so CI without the
user's Mac skips cleanly), and index every PNG in both idea folders."""
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from city_components import COMPONENT_IDS  # noqa: E402

INDEX = ROOT / "docs" / "research" / "london-components" / "ideas-index.md"
REFS = pathlib.Path("/Users/apple/Downloads/BSUK-refs/london")
FOLDERS = (pathlib.Path("/Users/apple/Downloads/MFS/assets/MFS-Components-IDEAS"),
           pathlib.Path("/Users/apple/Downloads/bluestaffyuk-cms/Assets/Components-Ideas"))
UNUSED = "## Sheets not used by a city component"
ENTRY = re.compile(r"^- (`(/[^`]+)`|<(https?://[^>]+)>) — (.{12,})$", re.M)


def sections():
    """(whole text, {component: body}, component order). A sheet no component uses is still
    indexed, under the closing UNUSED heading, which is not a component section."""
    text = INDEX.read_text(encoding="utf-8")
    parts = re.split(r"^## ([a-z-]+) — .*$", text.split("\n" + UNUSED, 1)[0], flags=re.M)
    return text, {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}, \
        [parts[i] for i in range(1, len(parts), 2)]


def test_the_index_covers_the_fifteen_in_city_page_order():
    _t, _s, order = sections()
    assert order == list(COMPONENT_IDS)


def test_every_component_cites_at_least_three_sources_including_a_capture():
    _t, secs, _o = sections()
    for cid, body in secs.items():
        entries = ENTRY.findall(body)
        assert len(entries) >= 3, (cid, len(entries))
        assert any(p.startswith(str(REFS)) for _all, p, _u, _i in entries), \
            f"{cid}: no Playwright capture from /Users/apple/Downloads/BSUK-refs/london/"


def test_the_four_reference_pages_are_named():
    text, _s, _o = sections()
    src = (ROOT / "docs/research/2026-09-27-location-component-design-sources.md").read_text(encoding="utf-8")
    for url in set(re.findall(r"https?://[^\s)>`]+", src)):
        assert url in text, url


@pytest.mark.parametrize("root", [REFS, *FOLDERS], ids=["captures", "mfs-ideas", "bsuk-ideas"])
def test_every_cited_path_under_a_present_folder_exists(root):
    if not root.is_dir():
        pytest.skip(f"{root} is not on this machine")
    text, _s, _o = sections()
    cited = [p for p in re.findall(r"`(/[^`]+)`", text) if p.startswith(str(root))]
    assert cited, f"nothing cited under {root}"
    missing = [p for p in cited if not pathlib.Path(p).is_file()]
    assert missing == [], missing


@pytest.mark.parametrize("folder", FOLDERS, ids=["mfs-ideas", "bsuk-ideas"])
def test_every_idea_sheet_is_indexed(folder):
    if not folder.is_dir():
        pytest.skip(f"{folder} is not on this machine")
    text, _s, _o = sections()
    pngs = sorted(p for p in folder.glob("*.png"))
    assert pngs
    unindexed = [p.name for p in pngs if f"`{p}`" not in text]
    assert unindexed == [], unindexed


def test_nothing_was_copied_into_the_repo():
    here = sorted(INDEX.parent.glob("*"))
    assert all(p.suffix in (".md", ".json") for p in here), here
