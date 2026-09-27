# tests/py/test_thread_ledger.py — scripts/thread_ledger.py, the shared Reddit and forum
# thread ledger (parity build Task 22; audit row 6.20). Built from the committed
# data/queries/raw/<slug>/threads.json files; nothing here fetches.
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import thread_ledger as T  # noqa: E402

SCRIPT = ROOT / "scripts" / "thread_ledger.py"
A = "https://www.reddit.com/r/UK_Pets/comments/aaa111/first_dog/"
B = "https://www.reddit.com/r/StaffordBullTerriers/comments/bbb222/blue_staffy/"


def row(url, replies=5, score=6, posted="2026-01"):
    return {"permalink": url, "title": url.rsplit("/", 2)[-2], "subreddit": "r/UK_Pets",
            "posted": posted, "replies": replies, "score": score, "stale": False}


def q(text, url, fact=None):
    return {"text": text, "detail": f"thread:{url}", "fact_source": fact}


def write_threads(root, slug, fetched, questions, threads, status="ok"):
    d = root / "data/queries/raw" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "threads.json").write_text(json.dumps({"source": "threads", "status": status,
                                                "fetched": fetched, "questions": questions,
                                                "threads": threads}))


def two_pages(tmp_path):
    write_threads(tmp_path, "city-a", "2026-09-01",
                  [q("Is a Staffy good for a first-time owner?", A)], [row(A, replies=5)])
    write_threads(tmp_path, "city-b", "2026-09-20",
                  [q("Is a Staffy good for a first-time owner?", A),
                   q("Are blue Staffies healthy?", B, "bank:health-dna-tests")],
                  [row(A + "?utm=x", replies=9), row(B)])
    return tmp_path


KA = "https://www.reddit.com/comments/aaa111/"     # A's ledger key: the thread id
KB = "https://www.reddit.com/comments/bbb222/"


@pytest.mark.parametrize("url", [
    A,
    "https://old.reddit.com/r/UK_Pets/comments/aaa111/first_dog",
    "https://reddit.com/r/UK_Pets/comments/aaa111/first_dog/?utm_source=share#c1",
    "HTTPS://WWW.Reddit.com/r/UK_Pets/comments/aaa111/first_dog/",
    "https://www.reddit.com/r/uk_pets/comments/aaa111/first_dog/",        # subreddit case
    "https://www.reddit.com/r/UK_Pets/comments/aaa111/",                  # no slug
    "https://www.reddit.com/comments/aaa111",
    "https://redd.it/aaa111",                                            # short link
    "https://www.reddit.com/r/UK_Pets/comments/aaa111/first_dog/c9x8y7z/",  # a comment
    "https://www.reddit.com/r/UK_Pets/comments/aaa111/first_dog.json",     # .json suffix
    "https://sh.reddit.com/r/UK_Pets/comments/aaa111/first_dog/",
    "https://i.reddit.com:443/r/UK_Pets/comments/aaa111/first_dog/",
])
def test_canonical_keys_a_reddit_thread_by_its_id(url):
    assert T.canonical(url) == KA


def test_a_reddit_share_link_is_refused_with_a_clear_reason():
    with pytest.raises(ValueError, match="share link — open it and use the resolved permalink"):
        T.canonical("https://www.reddit.com/r/UK_Pets/s/AbCdEf123")


def test_a_forum_thread_keeps_its_id_parameter():
    one = T.canonical("https://forum.example.co.uk/viewtopic.php?t=123&utm=x&sid=abc#p9")
    two = T.canonical("https://forum.example.co.uk/viewtopic.php?t=456")
    assert one == "https://forum.example.co.uk/viewtopic.php?t=123"
    assert one != two
    assert T.canonical("https://Forum.example.co.uk/showthread.php?threadid=9&p=2") == \
        "https://forum.example.co.uk/showthread.php?p=2&threadid=9"


def test_build_merges_every_page_that_used_a_thread(tmp_path):
    led = T.build(two_pages(tmp_path))
    assert sorted(led["threads"]) == sorted([KA, KB])
    a = led["threads"][KA]
    assert a["permalink"] == A                    # the latest read's permalink, query dropped
    assert a["used_by"] == ["city-a", "city-b"]
    assert a["first_fetched"] == "2026-09-01" and a["last_fetched"] == "2026-09-20"
    assert a["replies"] == 9                      # the latest read wins
    assert a["questions"] == [{"text": "Is a Staffy good for a first-time owner?",
                               "fact_source": None}]
    assert led["threads"][KB]["questions"][0]["fact_source"] == "bank:health-dna-tests"


def test_a_not_fetched_threads_file_adds_nothing(tmp_path):
    write_threads(tmp_path, "city-c", "2026-09-20", [], [], status="NOT FETCHED")
    assert T.build(tmp_path)["threads"] == {}


def test_known_reuses_a_recent_thread_and_fetches_the_rest(tmp_path):
    led = T.build(two_pages(tmp_path))
    got = T.known(led, [A, "https://www.reddit.com/r/dogs/comments/ccc333/new/"], today="2026-10-01")
    assert got[0]["action"] == "reuse" and got[0]["used_by"] == ["city-a", "city-b"]
    assert got[0]["url"] == A
    assert got[1]["action"] == "fetch"
    assert T.known(led, [A], today="2027-06-01")[0]["action"] == "fetch"   # older than 180 days


def test_seed_writes_threads_json_rows_with_the_score_left_to_the_page(tmp_path):
    led = T.build(two_pages(tmp_path))
    seed = T.seed(led, [A, B], today="2026-10-01")
    assert [t["permalink"] for t in seed["threads"]] == [A, B]
    assert all(t["score"] is None for t in seed["threads"])
    assert set(seed["threads"][0]) == {"permalink", "title", "subreddit", "posted", "replies",
                                       "score", "stale", "seeded_from"}
    assert seed["threads"][0]["seeded_from"] == "2026-09-20"
    T.validate({"source": "threads", "status": "ok", "fetched": "2026-10-01", **seed})
    assert seed["questions"][0] == q("Is a Staffy good for a first-time owner?", A)
    old = T.seed(led, [B], today="2028-06-01")["threads"][0]
    assert old["stale"] is True                   # posted over 24 months before today


def test_seed_refuses_a_thread_the_ledger_does_not_hold(tmp_path):
    led = T.build(two_pages(tmp_path))
    with pytest.raises(KeyError):
        T.seed(led, ["https://www.reddit.com/r/dogs/comments/zzz/none/"], today="2026-10-01")


def test_cli_write_then_check(tmp_path):
    root = two_pages(tmp_path)
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "--write" in r.stdout
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--write"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "2 threads" in r.stdout
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "examined 2 threads files" in r.stdout
    write_threads(root, "city-d", "2026-09-25", [], [row("https://www.reddit.com/r/x/comments/d/e/")])
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "STALE" in r.stdout


def test_cli_known_prints_one_line_per_url(tmp_path):
    root = two_pages(tmp_path)
    subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--write"], check=True,
                   capture_output=True)
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--today", "2026-10-01",
                        "--known", A, "https://www.reddit.com/r/dogs/comments/ccc333/new/"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    lines = r.stdout.strip().splitlines()
    assert lines[0].startswith("reuse ") and "city-a, city-b" in lines[0]
    assert lines[1].startswith("fetch ")


def test_the_real_ledger_is_current():
    r = subprocess.run([sys.executable, str(SCRIPT), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def test_the_question_file_gate_does_not_read_the_ledger_as_a_question_file():
    import query_coverage_check as QC
    assert "thread-ledger.json" in QC.LEDGERS


def test_a_seeded_read_never_refreshes_the_thread(tmp_path):
    root = two_pages(tmp_path)
    led = T.build(root)
    seed = T.seed(led, [B], today="2026-12-01")
    seed["threads"][0]["score"] = 5
    write_threads(root, "city-e", "2026-12-01", seed["questions"], seed["threads"])
    b = T.build(root)["threads"][KB]
    assert b["last_fetched"] == "2026-09-20" and b["first_fetched"] == "2026-09-20"
    assert b["used_by"] == ["city-b", "city-e"]
    assert T.known(T.build(root), [B], today="2027-03-19")[0]["action"] == "reuse"
    assert T.known(T.build(root), [B], today="2027-03-20")[0]["action"] == "fetch"   # 181 days


def test_a_thread_only_ever_seeded_keeps_the_read_it_was_seeded_from(tmp_path):
    r = dict(row(B), score=None, seeded_from="2026-05-01")
    write_threads(tmp_path, "city-f", "2026-12-01", [], [r])
    b = T.build(tmp_path)["threads"][KB]
    assert b["last_fetched"] == "2026-05-01" and b["first_fetched"] == "2026-05-01"


def test_the_same_date_tie_goes_to_the_later_slug(tmp_path):
    write_threads(tmp_path, "city-a", "2026-09-01", [], [row(A, replies=3)])
    write_threads(tmp_path, "city-b", "2026-09-01", [], [row(A, replies=7)])
    assert T.build(tmp_path)["threads"][KA]["replies"] == 7


def test_questions_dedupe_loosely_and_a_later_fact_source_fills_a_null(tmp_path):
    write_threads(tmp_path, "city-a", "2026-09-01",
                  [q("Are blue Staffies healthy?", A)], [row(A)])
    write_threads(tmp_path, "city-b", "2026-09-02",
                  [q("  are BLUE staffies   healthy ", A, "bank:health-dna-tests"),
                   q("Asked of a thread the page did not list", B)], [row(A)])
    led = T.build(tmp_path)
    assert led["threads"][KA]["questions"] == [{"text": "Are blue Staffies healthy?",
                                                "fact_source": "bank:health-dna-tests"}]
    assert KB not in led["threads"]               # a question's thread must be in `threads`


def test_stale_is_strictly_older_than_24_months(tmp_path):
    led = T.build(two_pages(tmp_path))            # B was posted 2026-01
    assert T.seed(led, [B], today="2028-01-31")["threads"][0]["stale"] is False
    assert T.seed(led, [B], today="2028-02-01")["threads"][0]["stale"] is True


@pytest.mark.parametrize("body, reason", [
    ("{not json", "not valid JSON"),
    (json.dumps({"status": "ok", "fetched": "2026-09-01", "questions": [],
                 "threads": [{"title": "x"}]}), "permalink"),
    (json.dumps({"status": "ok", "fetched": "2026-09-01", "questions": [{"detail": None}],
                 "threads": []}), "text"),
    (json.dumps({"status": "ok", "fetched": "2026-09-01", "questions": [],
                 "threads": [row(A, posted="Jan 2026")]}), "posted"),
    (json.dumps({"status": "ok", "questions": [], "threads": [row(A)]}), "fetched"),
    (json.dumps({"status": "ok", "fetched": "2026-09-01", "questions": [],
                 "threads": [row("https://www.reddit.com/r/UK_Pets/s/AbC123")]}), "share link"),
])
def test_a_malformed_threads_file_fails_cleanly(tmp_path, body, reason):
    d = tmp_path / "data/queries/raw/city-x"
    d.mkdir(parents=True)
    (d / "threads.json").write_text(body)
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 2, r.stdout + r.stderr
    out = r.stdout + r.stderr
    assert "thread-ledger: data/queries/raw/city-x/threads.json:" in out and reason in out
    assert "Traceback" not in out


def test_known_and_seed_read_the_committed_ledger_without_rebuilding(tmp_path):
    root = two_pages(tmp_path)
    subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--write"], check=True,
                   capture_output=True)
    (root / "data/queries/raw/city-a/threads.json").write_text("{broken")
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--today", "2026-10-01",
                        "--known", A], capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.startswith("reuse ")
    r = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--today", "2026-10-01",
                        "--seed", A], capture_output=True, text=True)
    assert r.returncode == 0 and json.loads(r.stdout)["threads"][0]["seeded_from"] == "2026-09-20"
