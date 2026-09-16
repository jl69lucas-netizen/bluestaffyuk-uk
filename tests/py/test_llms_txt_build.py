import build_llms_txt


def test_llms_txt_content(tmp_path):
    out = build_llms_txt.main(tmp_path / "llms.txt")
    text = out.read_text(encoding="utf-8")
    assert "PHONE_PLACEHOLDER" not in text
    assert "/uk-locations/blue-staffy-puppies-london/" not in text, "stub-noindexed page leaked"
    assert "/thank-you-blue-staffy-puppies-journey/" not in text
    assert "](/): " in text, "homepage missing"
    assert text.startswith("# Blue Staffy UK: ")
    assert "- [XML sitemap](/sitemap_index.xml)" in text
    assert "40 Coltmuir Street" in text


def test_llms_txt_pages_sorted_by_url(tmp_path):
    text = build_llms_txt.main(tmp_path / "llms.txt").read_text(encoding="utf-8")
    urls = [l.split("](")[1].split("): ")[0] for l in text.splitlines() if l.startswith("- [") and "): " in l]
    assert urls == sorted(urls)
