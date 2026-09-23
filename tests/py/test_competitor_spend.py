# tests/py/test_competitor_spend.py — the spend conventions the competitor-intel agents rely on
# (spec 2026-09-23-competitor-intel §10). No script change: these pin the merged guard.
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import query_augment as Q  # noqa: E402

SETTINGS = {"query_budget_usd": 0.5, "query_total_budget_usd": 1.0, "query_typical_call_usd": 0.05}
SEEDS = ["blue-staffy-puppies-for-sale", "staffordshire-bull-terrier-puppies-for-sale-uk",
         "blue-staffy-breeder", "staffy-puppies-for-sale-manchester",
         "staffy-puppies-for-sale-leeds", "staffy-puppies-for-sale-carlisle",
         "staffy-puppies-for-sale-newcastle", "staffy-puppies-for-sale-liverpool",
         "kc-registered-staffy-puppies", "staffy-puppy-price-uk"]
TODAY = "2026-09-24"


def make_root(tmp_path, spent=0.2):
    (tmp_path / "data/queries").mkdir(parents=True)
    (tmp_path / "data/settings.json").write_text(json.dumps(SETTINGS))
    log = [{"ts": "2026-09-23T01:00:00Z", "slug": "blue-staffy-puppies-manchester-uk",
            "source": "ai_engines", "endpoint": "pilot", "cost_usd": spent}]
    (tmp_path / "data/queries/spend.json").write_text(json.dumps(log))
    return tmp_path


def test_registry_pseudo_slugs_are_valid_slugs():
    for s in SEEDS:
        assert Q.SLUG_RE.fullmatch(f"registry-{s}")


def test_each_seed_is_cached_on_its_own(tmp_path):
    root = make_root(tmp_path)
    d = root / "data/queries/raw/registry-blue-staffy-breeder"
    d.mkdir(parents=True)
    (d / "serp_google.response.json").write_text("{}")
    assert Q.preflight("registry-blue-staffy-breeder", "serp_google", root=root, today=TODAY) == Q.EXIT_CACHED
    assert Q.preflight("registry-staffy-puppy-price-uk", "serp_google", root=root, today=TODAY) == Q.EXIT_OK


def test_saved_ai_engines_answer_is_reused_free(tmp_path):
    # The LLM-intel agent reuses the Manchester AI-engines answer: a saved connector
    # response (<source>.response.json) means cached, so no second purchase.
    root = make_root(tmp_path)
    d = root / "data/queries/raw/blue-staffy-puppies-manchester-uk"
    d.mkdir(parents=True)
    (d / "ai_engines.response.json").write_text("{}")
    assert Q.preflight("blue-staffy-puppies-manchester-uk", "ai_engines", root=root, today=TODAY) == Q.EXIT_CACHED


def test_ten_seeds_then_one_llm_call_fit_the_total_cap(tmp_path):
    root = make_root(tmp_path, spent=0.2)
    for s in SEEDS:
        slug = f"registry-{s}"
        assert Q.preflight(slug, "serp_google", root=root, today=TODAY) == Q.EXIT_OK
        Q.record(slug, "serp_google", "serp_organic_live_advanced", 0.05, root=root,
                 now=f"{TODAY}T00:00:00Z")
    # typical ai_engines cost is the 0.2 already logged: 0.2 + 0.5 + 0.2 = 0.9 <= 1.0
    assert Q.preflight("blue-staffy-puppies-leeds", "ai_engines", root=root, today=TODAY) == Q.EXIT_OK


def test_the_total_cap_stops_an_eleventh_expensive_run(tmp_path):
    root = make_root(tmp_path, spent=0.96)
    assert Q.preflight("registry-blue-staffy-breeder", "serp_google", root=root, today=TODAY) == Q.EXIT_BUDGET


def test_bing_is_still_never_bought():
    assert "serp_bing" not in Q.PAID_SOURCES
