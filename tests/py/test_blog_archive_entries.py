"""The migrated blog post's archive entries name the pages they link to.

`src/content/blog/how-to-choose-the-right-blue-staffy-puppy-for-your-family.md` is the old
/blue-staffy-blog-guides/ archive body, moved to its own URL by hand in 6adf709 (so
`scripts/extract_blog.py`, which writes the archive's own slug from the old WordPress export,
no longer generates it). Its two `## [title](/page/)` headings are the old archive's entry titles,
and they render as the post's H2s and contents chips. The second read "UK Blue Staffy Puppy
Buying Guideinformation UK", a run-on the old site's own post title carried (the export's
`h2.entry-title`), which the Known Issue 97 re-review found on the chip (B3).

An entry title is its target's name: each must equal the stem of the linked page's own
`<title>` (the part before " | " or " — "), case aside, as "Buy Staffy Puppies for Sale UK"
already does for /buy-staffy-puppies-for-sale-uk/.
"""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
POST = ROOT / "src/content/blog/how-to-choose-the-right-blue-staffy-puppy-for-your-family.md"


def _entries():
    return re.findall(r"(?m)^## \[([^\]]+)\]\((/[^)]*)\)\s*$", POST.read_text(encoding="utf-8"))


def _title_stem(href):
    page = ROOT / "dist" / href.strip("/") / "index.html"
    if not page.exists():
        pytest.skip("run npm run build first")
    title = re.search(r"<title>([^<]*)</title>", page.read_text(encoding="utf-8")).group(1)
    title = title.replace("&amp;", "&")
    return re.split(r" \| | — ", title)[0].strip()


def test_the_post_has_its_two_archive_entries():
    assert len(_entries()) == 2, _entries()


@pytest.mark.parametrize("i", [0, 1])
def test_each_archive_entry_is_its_target_pages_name(i):
    text, href = _entries()[i]
    assert text.casefold() == _title_stem(href).casefold(), (text, href, _title_stem(href))
