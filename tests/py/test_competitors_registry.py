# tests/py/test_competitors_registry.py — scripts/competitor_registry_check.py
# (spec 2026-09-23-competitor-intel §4, §12). Every test builds its own root under tmp_path.
import copy
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import competitor_registry_check as C  # noqa: E402

SCRIPT = REPO / "scripts" / "competitor_registry_check.py"
CITIES = ["Manchester", "Leeds", "Carlisle"]


def entry(**over):
    e = {"id": "pets4homes", "name": "Pets4Homes", "root_domain": "pets4homes.co.uk",
         "tier": 2,
         "seed_hits": [{"keyword": f"k{i}", "position": 1} for i in range(5)],
         "cities": ["Manchester"], "priority": "high", "link_allowed": True,
         "last_analyzed": None, "notes": ""}
    e.update(over)
    return e


def registry(*entries):
    entries = list(entries) or [entry()]
    return {"_meta": {"last_discovery_run": "2026-09-24", "seed_keywords": ["k0"],
                      "total": len(entries)},
            "competitors": entries}


def make_root(tmp_path, reg=None):
    (tmp_path / "data/boards").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src").mkdir(exist_ok=True)
    (tmp_path / "docs/reference").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/reference/external-link-library.md").write_text("")
    (tmp_path / "data/locations.json").write_text(
        json.dumps([{"slug": c.lower(), "city": c} for c in CITIES]))
    if reg is not None:
        (tmp_path / "data/competitors.json").write_text(json.dumps(reg))
    return tmp_path


def test_a_valid_registry_has_no_problems(tmp_path):
    assert C.problems(registry(), make_root(tmp_path)) == []


def test_a_schema_error_is_reported_with_its_path(tmp_path):
    e = entry()
    del e["link_allowed"]
    out = C.problems(registry(e), make_root(tmp_path))
    assert out and all(p.startswith("schema:") for p in out)
    assert any("link_allowed" in p for p in out)


def test_the_id_bsuk_is_reserved_for_the_profile(tmp_path):
    out = C.problems(registry(entry(id="bsuk")), make_root(tmp_path))
    assert any(p.startswith("schema:") for p in out)


def test_more_than_thirty_is_refused(tmp_path):
    many = [entry(id=f"c{i}", root_domain=f"c{i}.co.uk") for i in range(31)]
    out = C.problems(registry(*many), make_root(tmp_path))
    assert any("30 at most" in p for p in out)


def test_total_must_equal_the_entry_count(tmp_path):
    reg = registry()
    reg["_meta"]["total"] = 7
    assert any("total" in p for p in C.problems(reg, make_root(tmp_path)))


@pytest.mark.parametrize("domain", ["https://a.co.uk", "a.co.uk/puppies", "www.a.co.uk",
                                                    "A.co.uk", "a.co.uk:443", "localhost", "-a.co.uk",
                                    "a-.co.uk", "a..co.uk", "a.c0m", "bücher.de"])
def test_root_domain_is_bare(tmp_path, domain):
    out = C.problems(registry(entry(root_domain=domain)), make_root(tmp_path))
    assert any("bare root domain" in p for p in out), out


def test_the_sites_own_domain_is_refused(tmp_path):
    out = C.problems(registry(entry(root_domain="bluestaffyuk.co.uk")), make_root(tmp_path))
    assert any("own domain" in p for p in out)


def test_duplicate_domains_and_ids_are_refused(tmp_path):
    a = entry()
    b = entry(id="other")
    c = entry(root_domain="other.co.uk")
    out = C.problems(registry(a, b, c), make_root(tmp_path))
    assert any("duplicate root_domain" in p for p in out)
    assert any("duplicate id" in p for p in out)


def test_a_suspect_seller_may_not_be_linkable(tmp_path):
    out = C.problems(registry(entry(tier=5, link_allowed=True, priority="high")),
                     make_root(tmp_path))
    assert any("tier 5" in p for p in out)


def test_a_city_outside_locations_json_is_refused(tmp_path):
    out = C.problems(registry(entry(cities=["Springfield"])), make_root(tmp_path))
    assert any("Springfield" in p for p in out)


@pytest.mark.parametrize("hits,tier,expected", [
    ([("a", 9), ("b", 9), ("c", 9), ("d", 9), ("e", 9)], 2, "high"),   # 5+ keywords
    ([("a", 2)], 1, "high"),                                          # breeder in the top 3
    ([("a", 2)], 2, "low"),                                           # top 3, not a breeder
    ([("a", 9), ("b", 9)], 3, "medium"),
    ([("a", 9), ("a", 4)], 3, "low"),                                 # one distinct keyword
])
def test_priority_is_derived_from_seed_hits(hits, tier, expected):
    e = entry(tier=tier, seed_hits=[{"keyword": k, "position": p} for k, p in hits])
    assert C.derived_priority(e) == expected


def test_a_typed_priority_that_disagrees_fails(tmp_path):
    e = entry(priority="low")   # five distinct keywords → high
    out = C.problems(registry(e), make_root(tmp_path))
    assert any("priority" in p and "high" in p for p in out)


def test_a_link_to_a_suspect_seller_is_found(tmp_path):
    root = make_root(tmp_path)
    reg = registry(entry(), entry(id="bad", root_domain="bad.co.uk", tier=5,
                                  link_allowed=False, priority="high"))
    page = root / "src/pages/x/index.astro"
    page.parent.mkdir(parents=True)
    page.write_text('<p>see <a href="https://www.bad.co.uk/pups">this</a></p>\n')
    out, scanned = C.suspect_links(reg, root)
    assert scanned == 2
    assert len(out) == 1 and "src/pages/x/index.astro:1" in out[0] and "bad.co.uk" in out[0]


def test_a_link_to_an_allowed_competitor_or_a_lookalike_is_fine(tmp_path):
    root = make_root(tmp_path)
    reg = registry(entry(), entry(id="bad", root_domain="bad.co.uk", tier=5,
                                  link_allowed=False, priority="high"))
    (root / "docs/reference/external-link-library.md").write_text(
        "https://pets4homes.co.uk/a\nhttps://notbad.co.uk/b\n")
    assert C.suspect_links(reg, root)[0] == []


def test_cli_passes_with_no_registry(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(make_root(tmp_path))],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "nothing to check" in r.stdout


def test_cli_fails_on_a_bad_registry(tmp_path):
    root = make_root(tmp_path, registry(entry(cities=["Springfield"])))
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "Springfield" in r.stdout


def test_cli_fails_on_unreadable_json(tmp_path):
    root = make_root(tmp_path)
    (root / "data/competitors.json").write_text("{not json")
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "not valid JSON" in r.stdout


def test_the_real_repo_passes():
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


BANNED = (entry(), entry(id="bad", root_domain="bad.co.uk", tier=5, link_allowed=False,
                        priority="high"))


@pytest.mark.parametrize("line", [
    '<a href="https://bad.co.uk?x=1">x</a>',
    '<a href="https://bad.co.uk#a">x</a>',
    '<a href="https://user@bad.co.uk/">x</a>',
    '<a href="https://bad.co.uk./">x</a>',
    '<a href="//bad.co.uk/x">x</a>',
    "<img src=//bad.co.uk/x.jpg>",
    "see https://shop.bad.co.uk/pups",
])
def test_the_link_guard_catches_every_url_form(tmp_path, line):
    root = make_root(tmp_path)
    (root / "src/x.astro").write_text(line + "\n")
    out, _ = C.suspect_links(registry(*BANNED), root)
    assert len(out) == 1 and "src/x.astro:1" in out[0], out


def test_a_code_comment_naming_a_banned_domain_is_not_a_link(tmp_path):
    root = make_root(tmp_path)
    (root / "src/x.ts").write_text("// comment bad.co.uk\nconst a = 1; // bad.co.uk/x\n")
    assert C.suspect_links(registry(*BANNED), root)[0] == []


def test_a_missing_scan_path_is_a_problem_when_domains_are_banned(tmp_path):
    root = make_root(tmp_path)
    (root / "data/boards").rmdir()
    out, _ = C.suspect_links(registry(*BANNED), root)
    assert any("data/boards" in p and "does not exist" in p for p in out), out


def test_a_missing_scan_path_is_fine_when_nothing_is_banned(tmp_path):
    root = make_root(tmp_path)
    (root / "data/boards").rmdir()
    assert C.suspect_links(registry(), root) == ([], 0)


@pytest.mark.parametrize("domain", ["shop.pets4homes.co.uk", "shop.example.com",
                                    "a.b.example.org"])
def test_a_subdomain_is_refused(tmp_path, domain):
    out = C.problems(registry(entry(root_domain=domain)), make_root(tmp_path))
    assert any("registrable domain" in p for p in out), out


@pytest.mark.parametrize("domain", ["pets4homes.co.uk", "example.com", "kc.org.uk",
                                    "xn--bcher-kva.de", "a-b.ltd.uk"])
def test_a_registrable_domain_is_accepted(tmp_path, domain):
    assert C.problems(registry(entry(root_domain=domain)), make_root(tmp_path)) == []


def test_non_ascii_domains_are_told_to_use_punycode(tmp_path):
    out = C.problems(registry(entry(root_domain="bücher.de")), make_root(tmp_path))
    assert any("punycode" in p for p in out), out


def test_an_entry_overlapping_another_entrys_domain_is_refused(tmp_path):
    a = entry()
    b = entry(id="couk", root_domain="co.uk")
    out = C.problems(registry(a, b), make_root(tmp_path))
    assert any("overlaps" in p and "co.uk" in p for p in out), out


def test_empty_seed_hits_are_a_schema_error(tmp_path):
    out = C.problems(registry(entry(seed_hits=[])), make_root(tmp_path))
    assert any(p.startswith("schema:") and "seed_hits" in p for p in out), out


@pytest.mark.parametrize("reg", [[], "x", {"competitors": "abc"}])
def test_valid_json_of_the_wrong_shape_is_reported_not_raised(tmp_path, reg):
    out = C.problems(reg, make_root(tmp_path))
    assert out and all(p.startswith("schema:") for p in out)


def run_cli(root):
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)],
                          capture_output=True, text=True)


def test_cli_reports_a_json_array_without_a_traceback(tmp_path):
    r = run_cli(make_root(tmp_path, []))
    assert r.returncode == 1 and "Traceback" not in r.stderr, r.stderr
    assert "schema:" in r.stdout and "? entries" in r.stdout


@pytest.mark.parametrize("locations", [None, "{not json", '[{"slug": "leeds"}]', '"x"'])
def test_cli_reports_unreadable_locations(tmp_path, locations):
    root = make_root(tmp_path, registry())
    if locations is None:
        (root / "data/locations.json").unlink()
    else:
        (root / "data/locations.json").write_text(locations)
    r = run_cli(root)
    assert r.returncode == 1 and "Traceback" not in r.stderr, r.stderr
    assert "locations.json unreadable" in r.stdout


def test_cli_fails_on_a_banned_link_and_says_what_it_examined(tmp_path):
    root = make_root(tmp_path, registry(*BANNED))
    (root / "src/p.astro").write_text("ok\n<a href='https://bad.co.uk/'>x</a>\n")
    r = run_cli(root)
    assert r.returncode == 1 and "src/p.astro:2" in r.stdout, r.stdout
    assert "2 entries; 1 banned domain; 2 files scanned; 1 problems" in r.stdout


def test_cli_summary_on_a_clean_registry(tmp_path):
    r = run_cli(make_root(tmp_path, registry()))
    assert r.returncode == 0
    assert "1 entries; 0 banned domains; 0 files scanned; 0 problems" in r.stdout
