# tests/py/test_spend_reconcile.py — the spend guard counts real DataForSEO spend once the
# user reads the dashboard (Known Issue 45; Known Issue 58, the user's "second option").
# Every test builds its own root under tmp_path; nothing here calls a paid service.
import json
import pathlib
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import query_augment as Q  # noqa: E402

SCRIPT = REPO / "scripts" / "query_augment.py"
SETTINGS = {"query_budget_usd": 0.5, "query_total_budget_usd": 1.0, "query_typical_call_usd": 0.01}
DAY = "2026-09-23"
TODAY = "2026-09-24"
CITIES = [f"blue-staffy-puppies-city-{i}" for i in range(26)]


def entry(slug, source, cost, ts="2026-09-23T19:00:00Z"):
    return {"ts": ts, "slug": slug, "source": source, "endpoint": "e (estimate)", "cost_usd": cost}


def real_shaped_log():
    """The 14 logged calls as they stand: $0.80 of estimates (0.05 per SERP, 0.10 per ChatGPT)."""
    log = [entry("blue-staffy-puppies-manchester-uk", "serp_google", 0.05, "2026-09-23T01:08:28Z"),
           entry("blue-staffy-puppies-manchester-uk", "serp_bing", 0.05, "2026-09-23T01:09:37Z"),
           entry("blue-staffy-puppies-manchester-uk", "ai_engines", 0.1, "2026-09-23T01:10:39Z")]
    log += [entry(f"registry-seed-{i}", "serp_google", 0.05) for i in range(10)]
    log.append(entry("blue-staffy-puppies-for-sale-leeds", "ai_engines", 0.1, "2026-09-23T20:14:35Z"))
    return log


def make_root(tmp_path, log=None, settings=None, dashboard=None):
    (tmp_path / "data/queries").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data/settings.json").write_text(json.dumps(settings or SETTINGS))
    (tmp_path / "data/queries/spend.json").write_text(json.dumps(
        real_shaped_log() if log is None else log))
    if dashboard is not None:
        (tmp_path / "data/queries/dashboard.json").write_text(
            dashboard if isinstance(dashboard, str) else json.dumps(dashboard))
    return tmp_path


def readings(root):
    return json.loads((root / "data/queries/dashboard.json").read_text())


def buy_all(root, slugs, cost=0.01):
    """Preflight then record each slug's one ai_engines call; the count that got through."""
    n = 0
    for s in slugs:
        if Q.preflight(s, "ai_engines", root, today=TODAY) != Q.EXIT_OK:
            break
        Q.record(s, "ai_engines", "ai_optimization_chat_gpt_scraper UK en (estimate)", cost, root,
                 now=f"{TODAY}T10:00:00Z")
        n += 1
    return n


# --- reconcile: an append-only dashboard reading ----------------------------------------------

def test_reconcile_appends_a_reading_that_covers_every_logged_call(tmp_path):
    root = make_root(tmp_path)
    r = Q.reconcile(0.96785, 1.0, root, today=DAY)
    assert r == {"date": DAY, "balance_usd": 0.96785, "opening_balance_usd": 1.0,
                 "covers_log_entries": 14, "source": Q.DASHBOARD_SOURCE}
    assert readings(root) == [r]
    # the spend log itself is never touched
    assert json.loads((root / "data/queries/spend.json").read_text()) == real_shaped_log()


def test_a_second_reading_is_appended_and_takes_the_last_opening_by_default(tmp_path):
    root = make_root(tmp_path, log=real_shaped_log()[:3])
    Q.reconcile(0.99185, 1.0, root, today=DAY)
    log = real_shaped_log()
    (root / "data/queries/spend.json").write_text(json.dumps(log))
    Q.reconcile(0.96785, None, root, today=DAY)
    got = readings(root)
    assert [(g["balance_usd"], g["opening_balance_usd"], g["covers_log_entries"]) for g in got] == \
        [(0.99185, 1.0, 3), (0.96785, 1.0, 14)]


@pytest.mark.parametrize("balance, opening, why", [
    (1.2, 1.0, "balance"),                 # more than the opening
    (-0.01, 1.0, "balance"),
    (float("nan"), 1.0, "balance"),
    (0.5, float("inf"), "balance"),
    (0.5, None, "--opening"),              # the first reading must state the opening
])
def test_reconcile_refuses_a_bad_reading_and_writes_nothing(tmp_path, balance, opening, why):
    root = make_root(tmp_path)
    with pytest.raises(ValueError, match=why):
        Q.reconcile(balance, opening, root, today=DAY)
    assert not (root / "data/queries/dashboard.json").exists()


def test_reconcile_refuses_real_spend_that_falls(tmp_path):
    # the same opening and a higher balance than last time: money does not come back
    root = make_root(tmp_path, dashboard=[{"date": DAY, "balance_usd": 0.96785,
                                           "opening_balance_usd": 1.0, "covers_log_entries": 14,
                                           "source": Q.DASHBOARD_SOURCE}])
    before = (root / "data/queries/dashboard.json").read_text()
    with pytest.raises(ValueError, match="top-up"):
        Q.reconcile(0.98, None, root, today=TODAY)
    with pytest.raises(ValueError, match="opening"):
        Q.reconcile(0.5, 0.9, root, today=TODAY)
    assert (root / "data/queries/dashboard.json").read_text() == before


def test_a_top_up_is_a_higher_opening(tmp_path):
    root = make_root(tmp_path, dashboard=[{"date": DAY, "balance_usd": 0.96785,
                                           "opening_balance_usd": 1.0, "covers_log_entries": 14,
                                           "source": Q.DASHBOARD_SOURCE}])
    Q.reconcile(5.96, 6.0, root, today=TODAY)          # $5 added, $0.04 spent in all
    assert Q.spend_basis("ai_engines", root)[0] == 0.04


def test_reconcile_never_overwrites_a_damaged_dashboard_file(tmp_path):
    root = make_root(tmp_path, dashboard='[{"date": "2026-09-23",')
    with pytest.raises(ValueError):
        Q.reconcile(0.96785, 1.0, root, today=DAY)
    assert (root / "data/queries/dashboard.json").read_text() == '[{"date": "2026-09-23",'


def test_the_same_balance_after_new_calls_is_refused(tmp_path):
    # The balance the user stated today is not a new reading: re-recording it after four more
    # calls would claim those calls cost nothing. Only a fresh dashboard read may cover them.
    root = make_root(tmp_path)
    Q.reconcile(0.96785, 1.0, root, today=DAY)
    before = (root / "data/queries/dashboard.json").read_text()
    assert buy_all(root, CITIES[:4]) == 4
    with pytest.raises(ValueError, match="same balance as the last reading .* 4 calls logged "
                                         "since it — read the dashboard again"):
        Q.reconcile(0.96785, None, root, today=TODAY)
    assert (root / "data/queries/dashboard.json").read_text() == before
    # the four calls keep counting at their logged 0.01 each
    assert Q.spend_basis("ai_engines", root)[0] == round(0.03215 + 4 * 0.01, 6)


def test_the_same_balance_with_a_top_up_and_new_calls_is_refused_too(tmp_path):
    # $5 added and the balance up by exactly $5: real spend unchanged, so still no new reading
    root = make_root(tmp_path)
    Q.reconcile(0.96785, 1.0, root, today=DAY)
    buy_all(root, CITIES[:1])
    with pytest.raises(ValueError, match="read the dashboard again"):
        Q.reconcile(5.96785, 6.0, root, today=TODAY)


def test_a_new_lower_balance_after_new_calls_is_a_new_reading(tmp_path):
    root = make_root(tmp_path)
    Q.reconcile(0.96785, 1.0, root, today=DAY)
    buy_all(root, CITIES[:4])
    r = Q.reconcile(0.95185, None, root, today=TODAY)      # the dashboard read again
    assert r["covers_log_entries"] == 18
    assert Q.spend_basis("ai_engines", root) == (0.04815, 0.01, " (dashboard 2026-09-24 covers 18 "
                                                                 "of 18 log entries)")


def test_the_same_balance_with_no_new_calls_is_accepted(tmp_path):
    # nothing was bought since, so the same figure is a true (if redundant) reading
    root = make_root(tmp_path)
    Q.reconcile(0.96785, 1.0, root, today=DAY)
    Q.reconcile(0.96785, None, root, today=TODAY)
    assert [r["covers_log_entries"] for r in readings(root)] == [14, 14]


# --- the guard: real spend for the covered calls, logged cost for the rest ---------------------

def test_without_a_reading_the_guard_is_unchanged(tmp_path):
    root = make_root(tmp_path)
    total, typical, basis = Q.spend_basis("ai_engines", root)
    assert (total, typical, basis) == (0.8, 0.1, "")


def test_a_reading_replaces_the_covered_estimates_with_the_real_spend(tmp_path):
    root = make_root(tmp_path)
    Q.reconcile(0.96785, 1.0, root, today=DAY)
    total, typical, basis = Q.spend_basis("ai_engines", root)
    assert total == 0.03215
    assert typical == 0.01           # the 0.10 estimates are covered: the setting binds
    assert "dashboard 2026-09-23 covers 14 of 14 log entries" in basis


def test_calls_logged_after_the_reading_count_at_their_logged_cost(tmp_path):
    root = make_root(tmp_path)
    Q.reconcile(0.96785, 1.0, root, today=DAY)
    Q.record("x", "ai_engines", "e", 0.3, root, now=f"{TODAY}T09:00:00Z")
    Q.record("y", "serp_google", "e", 0.02, root, now=f"{TODAY}T09:00:00Z")
    total, typical, _ = Q.spend_basis("ai_engines", root)
    assert total == round(0.03215 + 0.3 + 0.02, 6)
    assert typical == 0.3            # a later, larger logged cost still binds
    assert Q.spend_basis("serp_google", root)[1] == 0.02


def test_before_the_reading_only_two_more_city_calls_fit(tmp_path):
    root = make_root(tmp_path)       # $0.80 logged; a ChatGPT call budgets at its logged 0.10
    assert buy_all(root, CITIES, cost=0.1) == 2


def test_after_the_reading_all_26_city_calls_fit(tmp_path):
    root = make_root(tmp_path)
    Q.reconcile(0.96785, 1.0, root, today=DAY)
    assert buy_all(root, CITIES) == 26
    assert Q.spend_basis("ai_engines", root)[0] == round(0.03215 + 26 * 0.01, 6)


def test_the_setting_alone_changes_nothing_without_a_reading(tmp_path):
    # lowering query_typical_call_usd is not enough: the logged 0.10 estimates still bind
    root = make_root(tmp_path)
    assert Q.spend_basis("ai_engines", root)[1] == 0.1


def test_the_page_cap_still_counts_todays_logged_spend_on_the_page(tmp_path):
    root = make_root(tmp_path)
    Q.reconcile(0.96785, 1.0, root, today=DAY)
    Q.record("p", "serp_google", "e", 0.495, root, now=f"{TODAY}T09:00:00Z")
    assert Q.preflight("p", "ai_engines", root, today=TODAY) == Q.EXIT_BUDGET


def test_the_total_cap_still_binds_after_a_reading(tmp_path):
    root = make_root(tmp_path, dashboard=[{"date": DAY, "balance_usd": 0.005,
                                           "opening_balance_usd": 1.0, "covers_log_entries": 14,
                                           "source": Q.DASHBOARD_SOURCE}])
    assert Q.preflight("p", "ai_engines", root, today=TODAY) == Q.EXIT_BUDGET   # 0.995 + 0.01


GOOD = {"date": DAY, "balance_usd": 0.96785, "opening_balance_usd": 1.0,
        "covers_log_entries": 14, "source": "x"}


@pytest.mark.parametrize("dashboard", [
    "{not json",
    json.dumps({"a": 1}),
    json.dumps([1]),
    json.dumps([{**GOOD, "balance_usd": 1.5}]),            # balance above the opening
    json.dumps([{**GOOD, "balance_usd": -1}]),
    json.dumps([{**GOOD, "opening_balance_usd": "1.0"}]),
    json.dumps([{**GOOD, "covers_log_entries": 15}]),      # more than the log holds
    json.dumps([{**GOOD, "covers_log_entries": True}]),
    json.dumps([{**GOOD, "covers_log_entries": 1.5}]),
    json.dumps([GOOD, {**GOOD, "covers_log_entries": 3}]),  # coverage went backwards
    json.dumps([{**GOOD, "date": "23-09-2026"}]),
    '[{"date": "2026-09-23", "balance_usd": NaN, "opening_balance_usd": 1.0, '
    '"covers_log_entries": 14, "source": "x"}]',
])
def test_a_malformed_dashboard_file_fails_closed(tmp_path, capsys, dashboard):
    root = make_root(tmp_path, dashboard=dashboard)
    assert Q.preflight("p", "ai_engines", root, today=TODAY) == Q.EXIT_BUDGET
    assert "cannot read" in capsys.readouterr().err


def test_a_covered_entry_with_a_bad_cost_still_blocks_calls(tmp_path):
    log = real_shaped_log()
    log[0]["cost_usd"] = "0.05"
    root = make_root(tmp_path, log=log, dashboard=[GOOD])
    assert Q.preflight("p", "ai_engines", root, today=TODAY) == Q.EXIT_BUDGET


def test_the_budget_stop_names_the_dashboard_basis(tmp_path, capsys):
    root = make_root(tmp_path, dashboard=[{**GOOD, "balance_usd": 0.005}])
    Q.preflight("p", "ai_engines", root, today=TODAY)
    err = capsys.readouterr().err
    assert "total 0.995 + 0.01 vs 1.0" in err and "dashboard 2026-09-23" in err


# --- CLI ------------------------------------------------------------------------------------

def run(root, *args):
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), *args],
                          capture_output=True, text=True)


def test_cli_reconcile_records_the_reading(tmp_path):
    root = make_root(tmp_path)
    r = run(root, "--reconcile", "--balance", "0.96785", "--opening", "1.0", "--today", DAY)
    assert r.returncode == 0, r.stderr
    assert "real spend 0.03215 over the 14 logged calls" in r.stdout
    assert readings(root)[0]["covers_log_entries"] == 14


@pytest.mark.parametrize("args", [
    ("--reconcile",),                                        # no balance
    ("--reconcile", "--balance", "1.5", "--opening", "1.0"),
    ("--reconcile", "--balance", "nan", "--opening", "1.0"),
    ("--reconcile", "--balance", "0.9"),                     # first reading, no opening
])
def test_cli_reconcile_refuses_cleanly(tmp_path, args):
    root = make_root(tmp_path)
    r = run(root, *args)
    assert r.returncode == Q.EXIT_USAGE
    assert "Traceback" not in r.stderr and "unrecognized" not in r.stderr
    assert not (root / "data/queries/dashboard.json").exists()


def test_cli_reconcile_refuses_a_repeated_balance_after_new_calls(tmp_path):
    root = make_root(tmp_path)
    Q.reconcile(0.96785, 1.0, root, today=DAY)
    Q.record("p", "ai_engines", "e", 0.01, root, now=f"{TODAY}T09:00:00Z")
    r = run(root, "--reconcile", "--balance", "0.96785")
    assert r.returncode == Q.EXIT_USAGE and "Traceback" not in r.stderr
    assert r.stderr.strip() == (
        "query_augment.py: --reconcile refused: same balance as the last reading (0.96785, "
        "2026-09-23) but 1 calls logged since it — read the dashboard again")
    assert len(readings(root)) == 1


def test_cli_reconcile_is_its_own_mode(tmp_path):
    root = make_root(tmp_path)
    r = run(root, "--reconcile", "--balance", "0.9", "--opening", "1.0",
            "--preflight", "p", "--source", "ai_engines")
    assert r.returncode == Q.EXIT_USAGE and "exactly one of" in r.stderr


def test_cli_budget_prints_what_the_guard_counts(tmp_path):
    root = make_root(tmp_path)
    Q.reconcile(0.96785, 1.0, root, today=DAY)
    r = run(root, "--budget", "ai_engines")
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines() == [
        "budget ai_engines: total counted 0.03215 of cap 1.0 (dashboard 2026-09-23 covers 14 of "
        "14 log entries); typical call 0.01; 96 more calls of this source fit the total cap; "
        "page cap 0.5 per slug per day",
        "spend log holds 14 entries"]


def test_cli_budget_on_a_damaged_dashboard_exits_4(tmp_path):
    root = make_root(tmp_path, dashboard="{not json")
    r = run(root, "--budget", "ai_engines")
    assert r.returncode == Q.EXIT_BUDGET and "Traceback" not in r.stderr


# --- review fixes: a positive typical cost, --covers, the whole file checked ----------------------

@pytest.mark.parametrize("typical", [0, -0.01, None, "0.01", float("nan")])
def test_a_typical_call_setting_that_is_not_positive_blocks_calls(tmp_path, capsys, typical):
    # an explicit 0 (or worse) would let calls through at no cost; only a missing key falls back
    root = make_root(tmp_path, settings={**SETTINGS, "query_typical_call_usd": typical})
    assert Q.preflight("p", "ai_engines", root, today=TODAY) == Q.EXIT_BUDGET
    assert "query_typical_call_usd" in capsys.readouterr().err
    Q.reconcile(0.96785, 1.0, root, today=DAY)          # a reading does not unblock it
    assert Q.preflight("p", "ai_engines", root, today=TODAY) == Q.EXIT_BUDGET
    assert run(root, "--budget", "ai_engines").returncode == Q.EXIT_BUDGET


def test_a_missing_typical_call_setting_falls_back_to_the_default(tmp_path):
    settings = {k: v for k, v in SETTINGS.items() if k != "query_typical_call_usd"}
    root = make_root(tmp_path, settings=settings)
    Q.reconcile(0.96785, 1.0, root, today=DAY)
    assert Q.spend_basis("ai_engines", root)[1] == Q.DEFAULT_TYPICAL_CALL_USD


def test_covers_leaves_calls_the_user_did_not_see_at_their_logged_cost(tmp_path):
    # the dashboard was read after 13 calls; the 14th (a 0.10 ChatGPT estimate) came later
    root = make_root(tmp_path)
    r = Q.reconcile(0.96785, 1.0, root, today=DAY, covers=13)
    assert r["covers_log_entries"] == 13
    total, typical, basis = Q.spend_basis("ai_engines", root)
    assert (total, typical) == (round(0.03215 + 0.1, 6), 0.1)
    assert "covers 13 of 14 log entries" in basis


@pytest.mark.parametrize("covers", [15, -1, 2, True, 1.5])
def test_covers_out_of_range_is_refused(tmp_path, covers):
    root = make_root(tmp_path, log=real_shaped_log()[:3])
    Q.reconcile(0.99185, 1.0, root, today=DAY)           # covers 3
    (root / "data/queries/spend.json").write_text(json.dumps(real_shaped_log()))
    before = (root / "data/queries/dashboard.json").read_text()
    with pytest.raises(ValueError, match="covers"):
        Q.reconcile(0.96785, None, root, today=DAY, covers=covers)
    assert (root / "data/queries/dashboard.json").read_text() == before


def test_the_same_balance_covering_no_new_calls_is_accepted(tmp_path):
    # four calls since, but the reading does not claim them: they keep their logged cost
    root = make_root(tmp_path)
    Q.reconcile(0.96785, 1.0, root, today=DAY)
    buy_all(root, CITIES[:4])
    Q.reconcile(0.96785, None, root, today=TODAY, covers=14)
    assert Q.spend_basis("ai_engines", root)[0] == round(0.03215 + 4 * 0.01, 6)


def test_a_reading_dated_before_the_last_one_is_refused(tmp_path):
    root = make_root(tmp_path)
    Q.reconcile(0.96785, 1.0, root, today=TODAY)
    before = (root / "data/queries/dashboard.json").read_text()
    with pytest.raises(ValueError, match="earlier than the last reading"):
        Q.reconcile(0.96785, None, root, today=DAY)
    assert (root / "data/queries/dashboard.json").read_text() == before


@pytest.mark.parametrize("second", [
    {**GOOD, "opening_balance_usd": 0.9, "balance_usd": 0.5},      # the opening fell
    {**GOOD, "balance_usd": 0.98},                                  # real spend fell
    {**GOOD, "date": "2026-09-22"},                                 # dated before the first
])
def test_a_hand_edited_dashboard_history_fails_closed(tmp_path, capsys, second):
    root = make_root(tmp_path, dashboard=[GOOD, second])
    assert Q.preflight("p", "ai_engines", root, today=TODAY) == Q.EXIT_BUDGET
    assert "cannot read" in capsys.readouterr().err
    before = (root / "data/queries/dashboard.json").read_text()
    with pytest.raises(ValueError):
        Q.reconcile(0.9, None, root, today=TODAY)
    assert (root / "data/queries/dashboard.json").read_text() == before


def test_a_hand_edited_repeat_balance_covering_new_calls_fails_closed(tmp_path, capsys):
    first = {**GOOD, "balance_usd": 0.99185, "covers_log_entries": 3}
    root = make_root(tmp_path, dashboard=[first, {**first, "covers_log_entries": 14}])
    assert Q.preflight("p", "ai_engines", root, today=TODAY) == Q.EXIT_BUDGET
    assert "read the dashboard again" in capsys.readouterr().err


def test_cli_reconcile_covers(tmp_path):
    root = make_root(tmp_path)
    r = run(root, "--reconcile", "--balance", "0.96785", "--opening", "1.0", "--covers", "13",
            "--today", DAY)
    assert r.returncode == 0, r.stderr
    assert "over the 13 logged calls" in r.stdout and "1 later calls" in r.stdout
    assert readings(root)[0]["covers_log_entries"] == 13
    r = run(root, "--reconcile", "--balance", "0.9", "--covers", "15", "--today", DAY)
    assert r.returncode == Q.EXIT_USAGE and "Traceback" not in r.stderr
    assert len(readings(root)) == 1


@pytest.mark.parametrize("args", [
    ("--budget", "ai_engines", "--balance", "0.9"),
    ("--budget", "ai_engines", "--opening", "1.0"),
    ("--budget", "ai_engines", "--covers", "3"),
    ("--preflight", "p", "--source", "ai_engines", "--balance", "0.9"),
])
def test_cli_reading_flags_need_reconcile(tmp_path, args):
    root = make_root(tmp_path)
    r = run(root, *args)
    assert r.returncode == Q.EXIT_USAGE and "only with --reconcile" in r.stderr
    assert not (root / "data/queries/dashboard.json").exists()
    assert json.loads((root / "data/queries/spend.json").read_text()) == real_shaped_log()


def test_cli_budget_always_prints_the_log_length(tmp_path):
    root = make_root(tmp_path)
    r = run(root, "--budget", "ai_engines")
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines() == [
        "budget ai_engines: total counted 0.8 of cap 1.0; typical call 0.1; 2 more calls of this "
        "source fit the total cap; page cap 0.5 per slug per day",
        "spend log holds 14 entries"]


# --- the committed state -----------------------------------------------------------------------

def test_the_committed_state_admits_the_26_remaining_city_calls(tmp_path):
    """The repo's own settings, spend log and dashboard reading, copied. Since the user's
    dashboard reading of 2026-10-07 (balance $0.25074, real spend $0.749 of the $1 cap), the cap
    funds 25 of the 26 remaining city ChatGPT calls at the typical $0.01, not all 26."""
    for rel in ("data/settings.json", "data/queries/spend.json", "data/queries/dashboard.json"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO / rel, tmp_path / rel)
    s = json.loads((REPO / "data/settings.json").read_text())
    assert buy_all(tmp_path, CITIES, cost=s["query_typical_call_usd"]) == 25
