#!/usr/bin/env python3
"""data/page-map.json + data/settings.json -> public/llms.txt."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent

THANK_YOU = "/thank-you-blue-staffy-puppies-journey/"


def indexable(page):
    if page["url"] == THANK_YOU:
        return False
    return "stub-noindexed" not in page.get("refresh_flags", [])


def render(pages, settings):
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
    for p in sorted((q for q in pages if indexable(q)), key=lambda q: q["url"]):
        wc = p["word_count"]
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
    text = render(pages, settings)
    out_path.write_text(text, encoding="utf-8")
    print("wrote %s (%d bytes)" % (out_path, len(text)))
    return out_path


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
