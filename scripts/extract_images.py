#!/usr/bin/env python3
"""Rewrite WordPress upload paths in extracted body HTML onto the baked /images/ tree."""
import re, pathlib
from bs4 import BeautifulSoup

LOGO_STEMS = {"blue-staffy-uk-official-logo0", "cropped-blue-staffy-uk-official-logo0",
              "cropped-blue-staffy-uk-official-logo0-1", "cropped-blue-staffy-uk-logo-1"}
SIZE_SUFFIX = re.compile(r"-\d{2,4}x\d{2,4}$")
UPLOADS = "/wp-content/uploads/"


def stem_for(src):
    name = pathlib.Path(src.split("?")[0].split("#")[0]).stem
    return SIZE_SUFFIX.sub("", name)


def baked_path(stem):
    """Where a stem lands under public/images: logos stay PNG, everything else is WebP."""
    return "/images/%s.png" % stem if stem in LOGO_STEMS else "/images/%s.webp" % stem


def rewrite_image_srcs(body_html):
    if UPLOADS not in body_html:
        return body_html                      # no-op fast path, byte-identical
    soup = BeautifulSoup(body_html, "lxml")
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if UPLOADS not in src:
            continue
        stem = stem_for(src)
        if stem in LOGO_STEMS:
            img["src"] = baked_path(stem)
            img.attrs.pop("srcset", None)
            img.attrs.pop("sizes", None)
            continue
        img["src"] = "/images/%s.webp" % stem
        img["srcset"] = "/images/%s-760.webp 760w, /images/%s.webp 1408w" % (stem, stem)
        img["sizes"] = "(max-width: 800px) 100vw, 760px"
        if "loading" not in img.attrs:
            img["loading"] = "lazy"
        if "decoding" not in img.attrs:
            img["decoding"] = "async"
        for a in ("title", "role", "class"):
            img.attrs.pop(a, None)
    # Inline <video> carries a poster image and an mp4 src, both straight from uploads.
    for v in soup.find_all(["video", "source"]):
        for attr in ("poster", "src"):
            val = v.get(attr, "")
            if UPLOADS in val:
                v[attr] = baked_url(val)
    # Lightbox links wrapping an image point at the raw upload; move them to the baked file.
    for a in soup.find_all("a", href=True):
        if UPLOADS not in a["href"]:
            continue
        a["href"] = baked_path(stem_for(a["href"]))
    return soup.body.decode_contents() if soup.body else str(soup)


# JSON-LD carries its own copies of the upload paths (ImageObject.url, logo.url,
# thumbnailUrl, VideoObject.contentUrl), sometimes absolute. The body rewrite never sees them.
UPLOAD_URL_RE = re.compile(
    r"(?:https?://[^\s\"']*?)?/wp-content/uploads/(\S+?\.(?:jpe?g|png|webp|gif|mp4|webm))",
    re.IGNORECASE)
VIDEO_SUFFIXES = (".mp4", ".webm")


def baked_url(path):
    """Baked location for any upload URL: videos pass through, images go to /images/."""
    clean = path.split("?")[0].split("#")[0]
    if pathlib.Path(clean).suffix.lower() in VIDEO_SUFFIXES:
        return "/videos/%s" % pathlib.Path(clean).name
    return baked_path(stem_for(clean))


def rewrite_schema_urls(node):
    """Repoint every wp-content upload URL in a JSON-LD tree at the baked tree."""
    if isinstance(node, dict):
        return dict((k, rewrite_schema_urls(v)) for k, v in node.items())
    if isinstance(node, list):
        return [rewrite_schema_urls(v) for v in node]
    if isinstance(node, str) and UPLOADS in node:
        return UPLOAD_URL_RE.sub(lambda m: baked_url(m.group(1)), node)
    return node


def referenced_uploads(body_html):
    soup = BeautifulSoup(body_html, "lxml")
    return sorted({(i["src"].split("?")[0], stem_for(i["src"]))
                   for i in soup.find_all("img", src=True) if UPLOADS in i["src"]})
