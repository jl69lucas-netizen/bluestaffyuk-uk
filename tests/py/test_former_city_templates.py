"""Known Issue 16: the breeder relocated to Carlisle, Cumbria. A page template that prints the
home base, the collection point or the business's own city reads it from
`data/settings.json` `address.city`; it never spells a city.

Project 4 rewrote the twelve boarded pages, but the templates it gave only the shell — the
puppy hub, the six puppy pages, the dormant H2 branch of `PuppyList` and the locations hub —
still said the business was "in Glasgow" and offered collection there, in their meta
descriptions and in visible copy. This test keeps the former city out of `src/`.

Two things are allowed and are not what this guards:
- a route or file whose PATH names the city (the outreach page
  `/uk-locations/staffy-breeding-dogs-glasgow/` keeps its URL, and project 5's Glasgow city
  page names the city it serves), and a line carrying either slug;
- comment lines, which record the history of this issue.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
SUFFIXES = {".astro", ".ts", ".tsx", ".js", ".mjs", ".md", ".mdx", ".css"}
CITY_ROUTE = re.compile(r"glasgow", re.I)  # the former city, in any case, on a path or a line
SLUG_ON_LINE = re.compile(r"staffy-breeding-dogs-glasgow|staffy-puppies-for-sale-glasgow")
COMMENT = ("//", "*", "/*", "{/*", "<!--")


def hits(root=SRC):
    out = []
    for f in sorted(root.rglob("*")):
        if not f.is_file() or f.suffix not in SUFFIXES:
            continue
        rel = f.relative_to(root.parent).as_posix()
        if CITY_ROUTE.search(rel):
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith(COMMENT) or not CITY_ROUTE.search(line) or SLUG_ON_LINE.search(line):
                continue
            out.append(f"{rel}:{n}: {stripped[:120]}")
    return out


def test_no_template_spells_the_former_city():
    found = hits()
    assert not found, "read the city from SITE.address.city instead:\n" + "\n".join(found)


def test_the_guard_fires_and_spares_what_it_should(tmp_path):
    src = tmp_path / "src"
    (src / "pages" / "uk-locations" / "staffy-puppies-for-sale-glasgow").mkdir(parents=True)
    (src / "pages" / "hub.astro").write_text(
        "// Known Issue 16: this page said Glasgow\n"
        "<a href=\"/uk-locations/staffy-breeding-dogs-glasgow/\">Our breeding dogs</a>\n"
        "<p>or collect in Glasgow after a deposit</p>\n", encoding="utf-8")
    (src / "pages" / "uk-locations" / "staffy-puppies-for-sale-glasgow" / "index.astro").write_text(
        "<h1>Blue Staffy Puppies for Sale in Glasgow</h1>\n", encoding="utf-8")
    found = hits(src)
    assert found == ["src/pages/hub.astro:3: <p>or collect in Glasgow after a deposit</p>"], found


def test_the_guard_reads_the_city_in_any_case(tmp_path):
    src = tmp_path / "src"
    (src / "pages").mkdir(parents=True)
    (src / "pages" / "hub.astro").write_text("<p class=\"caps\">COLLECT IN GLASGOW</p>\n",
                                            encoding="utf-8")
    assert hits(src) == ['src/pages/hub.astro:1: <p class="caps">COLLECT IN GLASGOW</p>']
