#!/usr/bin/env python3
"""data/page-map.json + data/settings.json -> public/llms.txt."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent

THANK_YOU = "/thank-you-blue-staffy-puppies-journey/"
REBUILT = ROOT / "data/facts/rebuilt.json"


def _slug(url):
    return url.strip("/").split("/")[-1] or "index"


def rebuilt_stub(page, rebuilt):
    """A migrated stub (`stub-noindexed`) that a rebuilt page has since replaced. Its row still
    describes the WordPress stub, so it is listed (the rebuilt page carries its own robots meta;
    London became indexable on the breeder's approval, 2026-10-06) but without the stub's word
    count, which counts the stub and not the page."""
    return "stub-noindexed" in page.get("refresh_flags", []) and _slug(page["url"]) in rebuilt


def indexable(page, rebuilt=()):
    if page["url"] == THANK_YOU:
        return False
    return "stub-noindexed" not in page.get("refresh_flags", []) or rebuilt_stub(page, rebuilt)


def render(pages, settings, rebuilt=()):
    a = settings["address"]
    out = ["# %s: %s" % (settings["site_name"], settings["tagline"]), ""]
    # Town and region only: the breeder relocated and has supplied no street, postcode or
    # coordinates for the new place (Known Issue 16). This line used to read keys that no
    # longer exist, and a KeyError here takes the whole llms.txt build down.
    out.append(
        "> %s is a Staffordshire Bull Terrier breeder in %s, %s, breeding blue Staffy puppies for homes across the UK."
        % (settings["site_name"], a["city"], a["region"])
    )
    out += ["", "## Sitemaps", "", "- [XML sitemap](/sitemap_index.xml)", "", "## Pages", ""]
    for p in sorted((q for q in pages if indexable(q, rebuilt)), key=lambda q: q["url"]):
        wc = 0 if rebuilt_stub(p, rebuilt) else p["word_count"]
        out.append("- [%s](%s)%s" % (p["title"], p["url"], ": %d words" % wc if wc else ""))
    out += ["", "## Available puppies", "", "- [Available Blue Staffy puppies](/available-puppies/)"]
    out += ["", "## Locations", "", "- [UK locations](/uk-locations/)"]
    out += ["", "## Blog", "", "- [Blue Staffy blog](/blog/)", ""]
    return "\n".join(out)


def main(out_path=None):
    pages = json.loads((ROOT / "data/page-map.json").read_text(encoding="utf-8"))["pages"]
    settings = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
    out_path = pathlib.Path(out_path) if out_path else ROOT / "public/llms.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rebuilt = set(json.loads(REBUILT.read_text(encoding="utf-8")))
    text = render(pages, settings, rebuilt)
    out_path.write_text(text, encoding="utf-8")
    print("wrote %s (%d bytes)" % (out_path, len(text)))
    return out_path


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
