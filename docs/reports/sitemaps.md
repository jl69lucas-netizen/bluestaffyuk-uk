# Sitemaps

Every indexable built page appears in exactly one URL shard; `video-sitemap.xml` is
supplementary and excluded from that count. Every `<loc>` must be a built page (or a
served asset) that is not `noindex`, must start with the site base, and must not
repeat within its shard. The index must list every shard in dist/ and nothing else,
and robots.txt must point at exactly `<base>/sitemap_index.xml`. A built page that
carries a YouTube embed must also appear in `video-sitemap.xml`.

## Problems

None.


## Shards

| shard | urls |
| --- | --- |
| location-sitemap.xml | 12 |
| page-sitemap.xml | 13 |
| post-sitemap.xml | 1 |
| puppy-sitemap.xml | 6 |
| video-sitemap.xml | 5 |

32 of 63 built pages are indexable; each must appear in exactly one URL shard.

examined 63 built pages, 5 shards, 37 sitemap urls; 0 problems
