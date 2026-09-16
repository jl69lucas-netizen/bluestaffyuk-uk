import pathlib
from generate_sitemaps import shard_for, build_shards


def test_shard_routing():
    assert shard_for("/") == "page"
    assert shard_for("/uk-locations/") == "page"
    assert shard_for("/uk-locations/blue-staffy-puppies-york/") == "location"
    assert shard_for("/available-puppies/roman/") == "puppy"
    assert shard_for("/available-puppies/") == "page"
    assert shard_for("/blue-staffy-blog-guides/", blog_slugs={"blue-staffy-blog-guides"}) == "post"
    assert shard_for("/blog/") == "page"
    assert shard_for("/thank-you-blue-staffy-puppies-journey/") is None


def test_video_shard_from_embeds(tmp_path):
    d = tmp_path / "dist"; (d / "x").mkdir(parents=True)
    (d / "x/index.html").write_text('<html><head><title>T</title><meta name="description" content="D"></head><body><iframe src="https://www.youtube.com/embed/g9iV9RVr_Sk"></iframe></body></html>', encoding="utf-8")
    (d / "index.html").write_text("<html><head><title>H</title></head><body></body></html>", encoding="utf-8")
    shards = build_shards(d, "https://example.test", blog_slugs={"x"})
    assert [u for u, _ in shards["video"]] == ["https://example.test/x/"]
    assert shards["video"][0][1][0]["id"] == "g9iV9RVr_Sk"


def test_noindex_pages_excluded(tmp_path):
    d = tmp_path / "dist"; (d / "n").mkdir(parents=True)
    (d / "n/index.html").write_text('<html><head><meta name="robots" content="noindex, follow"></head><body></body></html>', encoding="utf-8")
    (d / "index.html").write_text("<html><head></head><body></body></html>", encoding="utf-8")
    shards = build_shards(d, "https://example.test", blog_slugs=set())
    assert all(not u.endswith("/n/") for u, _ in shards["page"])
