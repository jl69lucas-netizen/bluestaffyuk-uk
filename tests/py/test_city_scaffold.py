"""The London page's scaffold (the London component design pass, Plan 2; spec §3.2).

src/pages/uk-locations/blue-staffy-puppies-london.astro mounts the fifteen picked city
components on CityShell (PageShell with the city's own nav set) with placeholder copy, kept out of the index until London's page run
writes it. What must hold:
  - one route, one source: the dynamic [slug].astro no longer builds London, and the other 27
    cities are still built by it;
  - noindex, and in no sitemap shard;
  - all fifteen picks on the page, the city nav set mounted and the kit's not;
  - the FAQPage node carries exactly the visible questions, and no other heading repeats one
    (learning loop L11);
  - the migrated body stays word for word for `check:parity` until London is rebuilt.
"""
import html as H
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SLUG = "blue-staffy-puppies-london"
PAGE = ROOT / "src/pages/uk-locations" / f"{SLUG}.astro"
BUILT = ROOT / "dist/uk-locations" / SLUG / "index.html"
PICKS = json.loads((ROOT / "data/design/city-picks" / f"{SLUG}.json").read_text())
LOCATIONS = json.loads((ROOT / "data/locations.json").read_text())

#: The kit root each picked canvas variant was built as (the London component design pass).
PICK_ROOTS = {
    "london/hero/b": 'class="city-kit kit-hero city-hero-filmstrip',
    "london/counter-strip/c": 'class="city-kit city-scale',
    "london/trust-strip/c": 'class="city-kit city-trust',
    "london/contents-list/c": 'class="city-kit city-contents-photo-index',
    "london/desktop-dial/c": "data-city-dial-photo-marker",
    "london/jump-links/a": "data-city-jump-stepper",
    "london/key-takeaways/a": 'class="city-kit city-takeaways-ledger',
    "london/puppy-cards/b": 'class="city-kit city-sheet',
    "london/tables/a": 'class="city-kit city-roster',
    "london/video/c": 'class="city-kit city-video',
    "london/image-text/c": 'class="city-kit city-chapters',
    "london/reviews/a": 'class="city-kit city-letter',
    "london/faq-blocks/a": 'class="city-kit city-faq',
    "london/newsletter/a": 'class="city-kit city-newsletter-notice',
    "london/contact-form/b": 'class="city-kit city-contact',
}


def built():
    if not BUILT.exists():
        pytest.skip("run npm run build first")
    return BUILT.read_text(encoding="utf-8")


def text(fragment):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def test_the_scaffold_file_exists():
    assert PAGE.is_file()


def test_the_template_builds_exactly_the_routes_the_date_map_gives_it():
    """One route, one source, as BEHAVIOUR (the quality review, M4): the city pages built
    without a scaffold are exactly the routes scripts/generate_page_dates.py assigns to
    src/pages/uk-locations/[slug].astro, so the template and the dates agree on which cities it
    builds, whichever form (<slug>.astro or <slug>/index.astro) a city's own page takes."""
    built()
    sys.path.insert(0, str(ROOT / "scripts"))
    import generate_page_dates as G
    static = [p for p in sorted(G._rel("src/pages/**/*.astro")) if p not in G.DYNAMIC and "[" not in p]
    template = {r for r, _ in G.expand("src/pages/uk-locations/[slug].astro",
                                        frozenset(G.route_for(p) for p in static))}
    plain = {f"/uk-locations/{d.name}/" for d in (ROOT / "dist/uk-locations").iterdir()
             if (d / "index.html").is_file()
             and "data-city-scaffold" not in (d / "index.html").read_text(encoding="utf-8")}
    assert template and plain == template


def test_london_is_built_from_the_scaffold_and_every_other_city_from_the_template():
    html = built()
    assert f'data-city-scaffold="{SLUG}"' in html
    others = [l["slug"] for l in LOCATIONS if l["slug"] != SLUG]
    assert len(others) == len(LOCATIONS) - 1
    for slug in others:
        page = ROOT / "dist/uk-locations" / slug / "index.html"
        assert page.is_file(), slug
        body = page.read_text(encoding="utf-8")
        assert "prose-migrated" in body and "data-city-scaffold" not in body, slug


def test_the_scaffold_is_noindex_and_in_no_sitemap():
    html = built()
    assert re.search(r'<meta name="robots" content="noindex[^"]*"', html)
    shards = list((ROOT / "dist").glob("*sitemap*.xml"))
    assert shards, "the build writes sitemap shards"
    for shard in shards:
        assert f"/uk-locations/{SLUG}/" not in shard.read_text(encoding="utf-8"), shard.name


def _scaffolds():
    """{route: html} for every built page that carries `data-city-scaffold`."""
    out = {}
    for f in (ROOT / "dist").rglob("index.html"):
        html = f.read_text(encoding="utf-8")
        if "data-city-scaffold" in html:
            rel = f.parent.relative_to(ROOT / "dist").as_posix()
            out["/" if rel == "." else f"/{rel}/"] = html
    return out


def test_every_scaffold_is_noindex_and_in_no_sitemap():
    """The invariant, for any city (the quality review, M6), not London alone."""
    built()
    pages = _scaffolds()
    assert pages, "the London scaffold is built"
    shards = [s.read_text(encoding="utf-8") for s in (ROOT / "dist").glob("*sitemap*.xml")]
    assert shards
    for route, html in pages.items():
        assert re.search(r'<meta name="robots" content="noindex[^"]*"', html), route
        assert not [s for s in shards if f"{route}<" in s or f"{route}\"" in s], route


def test_no_rebuilt_page_carries_a_scaffold():
    """A page in data/facts/rebuilt.json is a finished page; placeholder copy on it is a
    scaffold that shipped (the quality review, M6)."""
    built()
    rebuilt = json.loads((ROOT / "data/facts/rebuilt.json").read_text())
    routes = {"/" if s == "index" else f"/{s}/" for s in rebuilt}
    assert not routes & set(_scaffolds())


def test_every_pick_is_on_the_page_and_the_nav_set_is_the_citys():
    html = built()
    assert set(PICK_ROOTS) == set(PICKS["picks"].values())
    for key, root in PICK_ROOTS.items():
        assert root in html, key
    assert html.count('data-faq-block="') == 3, "the three FAQ blocks, at the template's three places"
    for kit in ('class="kit-dial', 'class="kit-strip', 'class="kit-sheet'):
        assert kit not in html, kit
    band = re.search(r"<div[^>]*data-city-jump-stepper[^>]*>", html).group(0)
    assert "data-strip" in band, "on a real page the band is the top chrome"


def test_every_nav_link_names_a_section_on_the_page():
    html = built()
    ids = set(re.findall(r'\bid="([^"]+)"', html))
    spies = re.findall(r'data-spy="([^"]+)"', html)
    assert len(set(spies)) >= 6
    assert not [s for s in spies if s not in ids]


def test_the_faq_schema_carries_exactly_the_visible_questions():
    html = built()
    visible = [text(q) for q in re.findall(r"<h3[^>]*data-faq-q[^>]*>(.*?)</h3>", html, re.S)]
    assert 15 <= len(visible) <= 20, len(visible)
    blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
    nodes = [n for b in blocks for n in (b if isinstance(b, list) else [b]) if n.get("@type") == "FAQPage"]
    assert len(nodes) == 1
    named = [q["name"] for q in nodes[0]["mainEntity"]]
    assert [n.lower() for n in named] == [v.lower() for v in visible]


def test_no_section_heading_repeats_an_faq_question():
    """Learning loop 2026-09-27, L11: a real heading that is also an FAQ question."""
    html = built()
    faq = {text(q).lower() for q in re.findall(r"<h3[^>]*data-faq-q[^>]*>(.*?)</h3>", html, re.S)}
    assert faq, "the scaffold's FAQ questions are found"
    heads = [text(h) for h in re.findall(r"<h[1-3](?![^>]*data-faq-q)[^>]*>(.*?)</h[1-3]>", html, re.S)]
    assert not [h for h in heads if h.lower() in faq]


def scaffold_alt_defects(main, served):
    """The body's served photos: the first use of each keeps its served alt (working rule 11),
    and each repeat carries a new alt, never a copy of one already used for it (the user's
    ruling, answer board q02, 2026-09-29: "No repeated alt, same photo use new alt")."""
    out, used = [], {}
    for name, alt in re.findall(r'<img [^>]*src="/images/([^"?]+)"[^>]*alt="([^"]*)"', main):
        alt = H.unescape(alt)
        if name not in used:
            if alt not in served[name]:
                out.append(f"{name}: its first use does not carry its served alt")
        elif alt in used[name]:
            out.append(f"{name}: a repeat copies the alt {alt!r}")
        used.setdefault(name, set()).add(alt)
    return out


def test_a_repeat_with_a_new_alt_is_allowed_on_the_scaffold():
    """The user's ruling (answer board q02, 2026-09-29): a photo shown twice keeps its served
    alt on its first use, and the repeat carries a new alt."""
    served = {"Christa.jpeg": frozenset({"Christa"})}
    ok = '<img src="/images/Christa.jpeg" alt="Christa"><img src="/images/Christa.jpeg" alt="Christa, sitting up">'
    assert scaffold_alt_defects(ok, served) == []
    copy = '<img src="/images/Christa.jpeg" alt="Christa"><img src="/images/Christa.jpeg" alt="Christa">'
    assert scaffold_alt_defects(copy, served) != []


def test_each_served_photo_keeps_its_served_alt_first_and_a_new_alt_on_a_repeat():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from check_city_canvas import served_alts
    served = served_alts()
    html = built()
    found = re.findall(r'<img [^>]*src="/images/([^"?]+)"[^>]*>', html)
    main = html.split("<main", 1)[1].split("</main>", 1)[0]
    assert re.search(r'<img [^>]*src="/images/', main), "the scaffold reuses served photographs"
    assert scaffold_alt_defects(main, served) == []
    assert found


def test_the_migrated_body_stays_word_for_word_for_parity():
    html = built()
    row = next(l for l in LOCATIONS if l["slug"] == SLUG)
    art = re.search(r'<article class="prose-migrated"[^>]*>(.*?)</article>', html, re.S)
    assert art and text(art.group(1)) == text(row["body_html"])


def test_london_keeps_the_date_its_url_was_first_published():
    """The URL has existed since the migration (2026-09-16); moving it from the template to its
    own file changes its source, not its publication (Plan 2 Task 8 spec review)."""
    dates = json.loads((ROOT / "data/page-dates.json").read_text())["routes"]
    row = dates[f"/uk-locations/{SLUG}/"]
    assert row["datePublished"] == "2026-09-16"
    assert row["dateModified"] >= row["datePublished"]
