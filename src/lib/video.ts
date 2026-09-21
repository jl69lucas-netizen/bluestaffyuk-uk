// src/lib/video.ts — the three YouTube url shapes, and the VideoObject a page mints from them.
//
// WHY A MODULE. Working rule 14 says every video the old site carried is reused AT ITS ORIGINAL
// ID, and an id reaches the web through three different urls: the PLAYER the page embeds
// (`youtube-nocookie.com/embed/<id>`, the privacy-preserving host `VideoEmbed` requests), the
// THUMBNAIL (`i.ytimg.com/vi/<id>/hqdefault.jpg`) and the canonical WATCH page
// (`youtube.com/watch?v=<id>`, which is where a crawler is meant to be sent). Those three
// shapes were written out by hand in `VideoEmbed.astro` and again in
// `scripts/generate_sitemaps.py`, and the first thing that went wrong when they drifted was
// e963c53: the sitemap builder looked for `youtube.com/embed/` while every rebuilt page served
// `youtube-nocookie.com/embed/`, so four already-ranking ids silently left the video sitemap.
// One place, three functions, and the fourth copy — a VideoObject per page — is built here
// rather than hand-rolled on each of the four pages that carry an embed.

/** The player a page embeds. `youtube-nocookie.com` is deliberate: no cookie is set until
 *  somebody presses play, which is the whole reason `VideoEmbed`'s facade exists. */
export const youtubeEmbedUrl = (id: string) => `https://www.youtube-nocookie.com/embed/${id}`;

/** The poster frame. The only request the facade makes before a click. */
export const youtubeThumbUrl = (id: string) => `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;

/** The canonical watch page — what `contentUrl` and a video sitemap's `player_loc` mean by
 *  "the video", and NOT the host the page asks the browser for. The two are different
 *  questions and conflating them is what e963c53 had to unpick. */
export const youtubeWatchUrl = (id: string) => `https://www.youtube.com/watch?v=${id}`;

/** A board record's `video` block, as `schemas/board.schema.json` writes it. */
export interface VideoBlock { id: string; title: string; caption?: string }

/**
 * The `VideoObject` node for one embed, for a page that carries it.
 *
 * NO `uploadDate`, AND THAT IS A GAP RATHER THAN AN OVERSIGHT. Google wants one for a video
 * rich result and NO FILE IN THIS REPO HOLDS IT: the only dates available are the migrated
 * theme's own `VideoObject.uploadDate`, which is the old site's markup rather than a fact this
 * repo keeps (the correction 1c500e5 made to the about page's video caption), and the page's
 * git-derived `dateModified`, which is when the PAGE changed and says nothing about when the
 * footage was published. Writing either would be inventing a date, which rule 9 forbids
 * outright, so the node ships without one and the gap is recorded in the session log's Known
 * Issues until the breeder supplies the real upload dates from the channel.
 *
 * `pageUrl` is the absolute page url; the `@id` is scoped to it AND to the id, because the
 * homepage carries three of these and three nodes sharing an `@id` is one node.
 */
export function videoObject(video: VideoBlock, pageUrl: string) {
  return {
    '@context': 'https://schema.org',
    '@type': 'VideoObject',
    '@id': `${pageUrl}#video-${video.id}`,
    name: video.title,
    ...(video.caption ? { description: video.caption } : {}),
    thumbnailUrl: youtubeThumbUrl(video.id),
    embedUrl: youtubeEmbedUrl(video.id),
    contentUrl: youtubeWatchUrl(video.id),
  };
}
