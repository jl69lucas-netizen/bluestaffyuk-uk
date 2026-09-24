"""scripts/link_diversity.py — the system-gaps rules on a new page's links.

Task 4: at least six external links, on six distinct registrable domains, from at least four
source types, where a link's source type is the `Source type` column of its row in
docs/reference/external-link-library.md.

Every check is exercised through `family_rules.findings()`, the hook `pageboard.gate_findings`
calls, so a passing test is a statement about the gate rather than about a helper.
"""
import copy
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import family_rules as FR      # noqa: E402
import link_diversity as LD    # noqa: E402
import pageboard as PB         # noqa: E402

LIBRARY = ROOT / "docs" / "reference" / "external-link-library.md"

# Eleven typed rows on nine domains and seven source types. `other` is a real type that does
# not count toward the four, so the fixture can prove that too.
FIXTURE_ROWS = [
    ("https://www.gov.uk/a", "gov"),
    ("https://www.gov.uk/b", "gov"),
    ("https://www.legislation.gov.uk/c", "gov"),
    ("https://www.royalkennelclub.com/d", "registry"),
    ("https://www.pdsa.org.uk/e", "vet-charity"),
    ("https://www.rspca.org.uk/f", "welfare"),
    ("https://pmc.ncbi.nlm.nih.gov/g", "research"),
    ("https://www.cumberland.gov.uk/h", "local"),
    ("https://crufts.org.uk/i", "other"),
    ("https://policies.google.com/j", "other"),
    ("https://assets.publishing.service.gov.uk/k.pdf", "gov"),
]


@pytest.fixture()
def library(tmp_path, monkeypatch):
    lines = ["# fixture", "", "| URL | Host | What it is | First page using it | Verified | Source type |",
             "|---|---|---|---|---|---|"]
    for url, t in FIXTURE_ROWS:
        lines.append(f"| {url} | host | a fixture row | none | 2026-09-24 · 200 | {t} |")
    p = tmp_path / "external-link-library.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    monkeypatch.setattr(PB, "EXTERNAL_LIBRARY", p)
    return p


def _board(status="boarded", slug="uk-locations/blue-staffy-puppies-manchester", page_type="location"):
    b = copy.deepcopy(json.loads((ROOT / "data" / "boards" / "_demo.json").read_text(encoding="utf-8")))
    b["meta"].update(slug=slug, page_type=page_type, status=status)
    return b


def _external(board, urls):
    """Spread the urls over the sections, one anchor each, so no anchor repeats."""
    secs = board["sections"]
    for s in secs:
        s["links"]["external"] = []
    for i, u in enumerate(urls):
        secs[i % len(secs)]["links"]["external"].append(
            {"href": u, "anchor": f"source number {i}", "library_row": u})
    return board


def _ext_findings(board):
    return [f for f in FR.findings(board, None) if f[0] == "external-links-six-diverse"]


DIVERSE = ["https://www.gov.uk/a", "https://www.legislation.gov.uk/c", "https://www.royalkennelclub.com/d",
           "https://www.pdsa.org.uk/e", "https://www.rspca.org.uk/f", "https://pmc.ncbi.nlm.nih.gov/g"]


# ── the library ─────────────────────────────────────────────────────────────────────────
def _table_urls():
    """The URL of every table row. library_urls() also greps the provenance prose, which
    names old spellings that are deliberately NOT rows, so it is the wrong set here."""
    return {PB.normalise_url(line.split("|")[1].strip())
            for line in LIBRARY.read_text(encoding="utf-8").splitlines() if line.startswith("| http")}


def test_every_real_library_row_carries_a_known_source_type():
    types = LD.library_source_types(LIBRARY)
    urls = _table_urls()
    assert types, "the library has no Source type column"
    untyped = sorted(u for u in urls if u not in types)
    assert untyped == [], f"library rows with no source type: {untyped}"
    bad = sorted((u, t) for u, t in types.items() if t not in LD.SOURCE_TYPES)
    assert bad == [], f"unknown source type(s) — the enum is {LD.SOURCE_TYPES}: {bad}"


def test_every_real_library_row_has_one_cell_per_column():
    """The parser reads the type by column index, so a row with a stray `|` in its prose
    would silently shift its type into the wrong cell."""
    header, bad = None, []
    for n, line in enumerate(LIBRARY.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("| URL |"):
            header = len(line.strip().strip("|").split("|"))
        elif header and line.startswith("| http"):
            if len(line.strip().strip("|").split("|")) != header:
                bad.append(n)
    assert header == 6, "the library header should carry six columns, the sixth Source type"
    assert bad == [], f"library lines whose cell count is not {header}: {bad}"


def test_every_typed_row_is_still_an_allowlisted_url():
    # library_urls() greps rather than parses; the new column must not hide a row from it.
    assert set(LD.library_source_types(LIBRARY)) <= PB.library_urls(LIBRARY)


# ── registrable domains ─────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("url,domain", [
    ("https://www.gov.uk/data-protection", "gov.uk"),
    ("https://www.gov.uk/guidance/dog-breeding-licence-england", "gov.uk"),
    ("https://assets.publishing.service.gov.uk/media/x.pdf", "gov.uk"),
    ("https://www.legislation.gov.uk/uksi/2018/486/contents/made", "legislation.gov.uk"),
    ("https://www.cumberland.gov.uk/business-and-licensing/licensing", "cumberland.gov.uk"),
    ("https://www.royalkennelclub.com/breed-standards/", "royalkennelclub.com"),
    ("https://www.thekennelclub.org.uk/", "thekennelclub.org.uk"),
    ("https://policies.google.com/privacy", "google.com"),
    ("https://pmc.ncbi.nlm.nih.gov/articles/PMC7510130/", "nih.gov"),
    ("https://paag.org.uk/", "paag.org.uk"),
])
def test_registrable_domain(url, domain):
    assert LD.registrable_domain(url) == domain


# ── the check ───────────────────────────────────────────────────────────────────────────
def test_six_links_six_domains_six_types_passes(library):
    assert _ext_findings(_external(_board(), DIVERSE)) == []


def test_five_links_fail_on_a_boarded_record(library):
    f = _ext_findings(_external(_board(), DIVERSE[:5]))
    assert ("external-links-six-diverse", "FAIL") in {(c, s) for c, s, _ in f}
    assert any("5 distinct external link(s)" in m for _, _, m in f)


def test_a_draft_only_warns(library):
    f = _ext_findings(_external(_board(status="draft"), DIVERSE[:5]))
    assert f and {s for _, s, _ in f} == {"WARN"}


@pytest.mark.parametrize("status", ["boarded", "approved", "built", "released"])
def test_every_status_past_draft_fails(library, status):
    f = _ext_findings(_external(_board(status=status), DIVERSE[:2]))
    assert f and {s for _, s, _ in f} == {"FAIL"}


def test_the_same_url_twice_counts_once(library):
    f = _ext_findings(_external(_board(), DIVERSE[:5] + ["https://gov.uk/a/"]))
    assert any("5 distinct external link(s)" in m for _, _, m in f)


def test_two_gov_uk_paths_are_one_domain(library):
    urls = ["https://www.gov.uk/a", "https://www.gov.uk/b", "https://assets.publishing.service.gov.uk/k.pdf",
            "https://www.royalkennelclub.com/d", "https://www.pdsa.org.uk/e", "https://www.rspca.org.uk/f"]
    f = _ext_findings(_external(_board(), urls))
    assert any("4 distinct domain(s)" in m for _, _, m in f), f


def test_other_does_not_count_toward_the_four_source_types(library):
    urls = ["https://www.gov.uk/a", "https://www.legislation.gov.uk/c", "https://www.royalkennelclub.com/d",
            "https://www.pdsa.org.uk/e", "https://crufts.org.uk/i", "https://policies.google.com/j"]
    f = _ext_findings(_external(_board(), urls))
    assert any("3 source type(s)" in m for _, _, m in f), f


def test_the_built_pages_are_not_asked(library):
    b = _external(_board(slug="blue-staffy-blog-guides", page_type="blog"), [])
    assert _ext_findings(b) == []


def test_the_summary_names_domains_and_types(library):
    s = LD.external_summary(_external(_board(), DIVERSE))
    assert s["links"] == 6
    assert s["domains"] == sorted(["gov.uk", "legislation.gov.uk", "royalkennelclub.com",
                                   "pdsa.org.uk", "rspca.org.uk", "nih.gov"])
    assert s["source_types"] == ["gov", "registry", "research", "vet-charity", "welfare"]


def test_the_gate_carries_the_finding(library):
    from test_page_board import ONT_OK, LEDGER_EMPTY
    f = PB.gate_findings(_external(_board(), DIVERSE[:3]), ONT_OK, LEDGER_EMPTY, live={}, stage="build")
    assert any(x["check"] == "external-links-six-diverse" and x["sev"] == "FAIL" for x in f)
