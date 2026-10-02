import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import term_density as TD

PAGE_A = "<html><body><main><p>Blue staffy puppies in London. Blue staffy puppies are kind.</p>" \
         "<p>Kennel Club papers.</p></main></body></html>"
PAGE_B = "<html><body><main><p>Blue staffy puppies here. Kennel Club registered.</p></main></body></html>"

def test_counts_each_term_on_each_page():
    c = TD.count_terms(PAGE_A, ["blue staffy puppies", "kennel club", "pedigree"])
    assert c["counts"] == {"blue staffy puppies": 2, "kennel club": 1, "pedigree": 0}
    assert c["words"] > 0

def test_stats_and_two_targets():
    pages = [TD.count_terms(PAGE_A, ["kennel club"]), TD.count_terms(PAGE_B, ["kennel club"])]
    row = TD.term_row("kennel club", pages, our_words=2000)
    assert row["min"] == 1 and row["max"] == 1 and row["median"] == 1
    assert row["target_median"][0] <= row["target_median"][1]
    assert row["target_leader"][0] >= row["target_median"][0]
    assert row["seen_on"] == 2

def test_zero_competitor_pages_is_not_fetched():
    row = TD.term_row("x", [], our_words=2000)
    assert row["note"].startswith("NOT FETCHED")
