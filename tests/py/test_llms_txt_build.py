import build_llms_txt


def test_llms_txt_content(tmp_path):
    out = build_llms_txt.main(tmp_path / "llms.txt")
    text = out.read_text(encoding="utf-8")
    assert "PHONE_PLACEHOLDER" not in text
    # London's migrated row is a stub, but the rebuilt page replaced it and the breeder approved
    # it for the index on 2026-10-06: listed, without the stub's 4-word count. A stub no page
    # has replaced stays out.
    assert "- [Blue Staffy Puppies London](/uk-locations/blue-staffy-puppies-london/)\n" in text
    assert "/uk-locations/blue-staffy-puppies-for-sale-leeds/" not in text, "stub-noindexed page leaked"
    assert "/thank-you-blue-staffy-puppies-journey/" not in text
    assert "](/): " in text, "homepage missing"
    assert text.startswith("# Blue Staffy UK: ")
    assert "- [XML sitemap](/sitemap_index.xml)" in text
    # Town and region only: the breeder relocated and has supplied no street or postcode
    # for the new place (Known Issue 16), so the summary line names what is true.
    assert "in Carlisle, Cumbria," in text
    assert "40 Coltmuir Street" not in text


def test_llms_txt_pages_sorted_by_url(tmp_path):
    text = build_llms_txt.main(tmp_path / "llms.txt").read_text(encoding="utf-8")
    urls = [l.split("](")[1].split("): ")[0] for l in text.splitlines() if l.startswith("- [") and "): " in l]
    assert urls == sorted(urls)


def test_committed_llms_txt_matches_builder(tmp_path):
    import json, pathlib
    root = pathlib.Path(build_llms_txt.__file__).resolve().parents[1]
    fresh = build_llms_txt.main(tmp_path / "llms.txt").read_text(encoding="utf-8")
    assert fresh == (root / "public/llms.txt").read_text(encoding="utf-8"), "run `npm run llms`"


def test_listed_page_count_matches_indexable_rows(tmp_path):
    import json, pathlib
    root = pathlib.Path(build_llms_txt.__file__).resolve().parents[1]
    pages = json.loads((root / "data/page-map.json").read_text(encoding="utf-8"))["pages"]
    rebuilt = set(json.loads((root / "data/facts/rebuilt.json").read_text(encoding="utf-8")))
    expected = sum(1 for p in pages if build_llms_txt.indexable(p, rebuilt))
    text = build_llms_txt.main(tmp_path / "llms.txt").read_text(encoding="utf-8")
    section = text.split("## Pages\n\n", 1)[1].split("\n\n", 1)[0]
    listed = [l for l in section.splitlines() if l.startswith("- [")]
    assert len(listed) == expected == 23


def test_zero_word_rows_are_listed_without_a_word_count(tmp_path):
    text = build_llms_txt.main(tmp_path / "llms.txt").read_text(encoding="utf-8")
    assert ": 0 words" not in text
    assert "](/blue-staffy-blog-guides/)\n" in text, "archive page should be listed, suffix-free"
