"""`docs/research/2026-09-26-url-family-decision.md` — one URL decision for the whole city
cluster and the comparison slugs, made once before the first city board (the brief's §4).

A decision table that misses a slug is a slug each builder decides alone, 28 times. So the
table must name every row of data/locations.json exactly once, its on-disk facts must match
the data file, each option set must mark exactly one (Recommended), and the per-page run must
point at it.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/research/2026-09-26-url-family-decision.md"
HEADER = ("Order", "Slug", "City", "Pattern", "Robots", "Mode", "H1", "In sitemap",
          "Redirects in", "Links in", "Intent (strategy)", "Decision")


def family_rows():
    lines = DOC.read_text(encoding="utf-8").splitlines()
    start = lines.index("| " + " | ".join(HEADER) + " |")
    out = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        out.append(dict(zip(HEADER, (c.strip() for c in line.strip().strip("|").split("|")))))
    return out


def cities():
    return {r["slug"]: r for r in json.loads((ROOT / "data/locations.json").read_text(encoding="utf-8"))}


def test_every_location_slug_has_exactly_one_row():
    slugs = [r["Slug"].strip("`") for r in family_rows()]
    assert sorted(slugs) == sorted(cities()), (
        "the decision table must name every data/locations.json row exactly once: missing "
        f"{sorted(set(cities()) - set(slugs))}, extra {sorted(set(slugs) - set(cities()))}")
    assert len(slugs) == len(set(slugs))


def test_the_on_disk_facts_match_the_data_file():
    data = cities()
    for r in family_rows():
        row = data[r["Slug"].strip("`")]
        assert r["Robots"] == ("noindex" if "noindex" in row["robots"] else "index"), r
        assert r["Mode"] == ("stub" if "stub" in row["defects"] else "migrated"), r
        assert r["H1"] == ("EMPTY" if not row["h1"] else "set"), r
        assert r["In sitemap"] == ("no" if "noindex" in row["robots"] else "yes"), r


def test_every_row_carries_a_decision_and_an_intent():
    bad = [r["Slug"] for r in family_rows() if not r["Decision"] or not r["Intent (strategy)"]]
    assert bad == []


def test_the_redirects_column_matches_data_redirects():
    redirects = json.loads((ROOT / "data/redirects.json").read_text(encoding="utf-8"))["redirects"]
    for r in family_rows():
        slug = r["Slug"].strip("`")
        want = sorted(x["from"] for x in redirects if x["to"].rstrip("/").endswith("/" + slug))
        got = sorted(re.findall(r"`([^`]+)`", r["Redirects in"]))
        assert got == want, (slug, got, want)


def test_each_option_table_marks_exactly_one_recommended():
    text = DOC.read_text(encoding="utf-8")
    tables = re.findall(r"\| Option \|[^\n]*\n\|[-| ]+\|\n((?:\|[^\n]*\n)+)", text)
    assert len(tables) == 2, "one option table for the city cluster, one for the comparison slugs"
    for body in tables:
        assert body.count("(Recommended)") == 1, body


def test_the_comparison_section_answers_known_issue_62_with_a_slug():
    text = DOC.read_text(encoding="utf-8")
    section = text[text.index("## Comparison slugs"):]
    assert "blue and black staffy" in section
    m = re.search(r"^\| \*\*\(a\)[^|]*`/([a-z0-9-]+)/`[^|]*\(Recommended\)\*\* \| `([a-z0-9-]+)` \|",
                  section, re.M)
    assert m, "the comparison (a) row names its slug in bold and in the Slug cell"
    assert m.group(1) == m.group(2), "the bold slug and the Slug cell name the same URL"


def test_the_page_run_points_at_the_decision_without_a_pending_marker():
    run = (ROOT / "docs/reference/page-run.md").read_text(encoding="utf-8")
    line = next(l for l in run.splitlines() if "2026-09-26-url-family-decision.md" in l)
    assert "(arrives in Task" not in line
    assert "(arrives in Task" not in run, "every arrival marker in the page run has arrived"


def test_the_hub_body_gap_is_named_and_acted_on():
    """The national bullet names the indexable city pages the UK hub's body did not link on the
    2026-09-26 build (read from the doc, not from dist/, so it stays true once project 5's hub
    refresh closes the gap): each is an indexable row, and its Decision cell carries the fix."""
    text = DOC.read_text(encoding="utf-8")
    bullet = " ".join(text[text.index("- **National:**"):text.index("- **Glasgow:**")].split())
    gap = re.search(r"does not link these (\w+) indexable city pages from its body: ([^.]*)\.", bullet)
    assert gap, "the national bullet names the indexable pages the hub body misses"
    named = re.findall(r"`([a-z0-9-]+)`", gap.group(2))
    assert len(named) == 9 and gap.group(1) == "nine", named
    assert "links all 10 other indexable pages from its body" in bullet, "the project 5 action is stated"
    data = cities()
    rows = {r["Slug"].strip("`"): r for r in family_rows()}
    for slug in named:
        assert "noindex" not in data[slug]["robots"], slug
        assert "the hub links it from its body" in rows[slug]["Decision"], slug
