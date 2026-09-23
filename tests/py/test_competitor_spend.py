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
    Q.record("blue-staffy-puppies-leeds", "ai_engines", "llm_response", 0.2, root=root,
             now=f"{TODAY}T00:00:00Z")
    # `typical` is the largest cost logged for that source, not one figure for all sources:
    # a 12th ai_engines call would reach 0.9 + 0.2 = 1.1 > 1.0, a 12th serp_google call 0.95.
    assert Q.preflight("blue-staffy-puppies-carlisle", "ai_engines", root=root,
                       today=TODAY) == Q.EXIT_BUDGET
    assert Q.preflight("registry-blue-staffy-puppies-carlisle", "serp_google", root=root,
                       today=TODAY) == Q.EXIT_OK


def test_total_cap_blocks_a_call_that_would_pass_1_usd(tmp_path, capsys):
    # 0.95 + 0.05 lands exactly on the 1.0 cap, which is allowed.
    root = make_root(tmp_path / "at", spent=0.95)
    assert Q.preflight("registry-blue-staffy-breeder", "serp_google", root=root, today=TODAY) == Q.EXIT_OK
    capsys.readouterr()
    # 0.96 + 0.05 goes past it: a budget stop, not an unreadable log.
    root = make_root(tmp_path / "over", spent=0.96)
    assert Q.preflight("registry-blue-staffy-breeder", "serp_google", root=root, today=TODAY) == Q.EXIT_BUDGET
    err = capsys.readouterr().err
    assert "total" in err and "cannot read" not in err


def test_page_cap_counts_only_todays_spend_on_that_slug(tmp_path):
    # 0.35 already spent on the page today + typical ai_engines 0.2 = 0.55 > the 0.5 page cap.
    root = make_root(tmp_path / "today")
    Q.record("blue-staffy-puppies-leeds", "serp_google", "serp_organic_live_advanced", 0.35,
             root=root, now=f"{TODAY}T09:00:00Z")
    assert Q.preflight("blue-staffy-puppies-leeds", "ai_engines", root=root, today=TODAY) == Q.EXIT_BUDGET
    # The same spend dated yesterday is a past run: it does not count against today's page cap.
    root = make_root(tmp_path / "yesterday")
    Q.record("blue-staffy-puppies-leeds", "serp_google", "serp_organic_live_advanced", 0.35,
             root=root, now="2026-09-23T09:00:00Z")
    assert Q.preflight("blue-staffy-puppies-leeds", "ai_engines", root=root, today=TODAY) == Q.EXIT_OK


def test_bing_is_still_never_bought(tmp_path):
    assert "serp_bing" not in Q.PAID_SOURCES
    root = make_root(tmp_path, spent=0.99)   # a paid source would be over the total cap here
    assert Q.main(["--record", "x", "--source", "serp_bing", "--endpoint", "e", "--cost", "0",
                   "--root", str(root)]) == Q.EXIT_USAGE
    assert json.loads((root / "data/queries/spend.json").read_text())[-1]["source"] == "ai_engines"
    # A Bing read is free: preflight never budget-checks it.
    assert Q.preflight("registry-blue-staffy-breeder", "serp_bing", root=root, today=TODAY) == Q.EXIT_OK
