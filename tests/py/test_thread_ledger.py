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


@pytest.mark.parametrize("url", [
    "https://old.reddit.com/r/UK_Pets/comments/aaa111/first_dog",
    "https://reddit.com/r/UK_Pets/comments/aaa111/first_dog/?utm_source=share#c1",
    "HTTPS://WWW.Reddit.com/r/UK_Pets/comments/aaa111/first_dog/",
])
def test_canonical_folds_the_spellings_of_one_thread(url):
    assert T.canonical(url) == A


def test_build_merges_every_page_that_used_a_thread(tmp_path):
    led = T.build(two_pages(tmp_path))
    assert sorted(led["threads"]) == sorted([A, B])
    a = led["threads"][A]
    assert a["used_by"] == ["city-a", "city-b"]
    assert a["first_fetched"] == "2026-09-01" and a["last_fetched"] == "2026-09-20"
    assert a["replies"] == 9                      # the latest read wins
    assert a["questions"] == [{"text": "Is a Staffy good for a first-time owner?",
                               "fact_source": None}]
    assert led["threads"][B]["questions"][0]["fact_source"] == "bank:health-dna-tests"


def test_a_not_fetched_threads_file_adds_nothing(tmp_path):
    write_threads(tmp_path, "city-c", "2026-09-20", [], [], status="NOT FETCHED")
    assert T.build(tmp_path)["threads"] == {}


def test_known_reuses_a_recent_thread_and_fetches_the_rest(tmp_path):
    led = T.build(two_pages(tmp_path))
    got = T.known(led, [A, "https://www.reddit.com/r/dogs/comments/ccc333/new/"], today="2026-10-01")
    assert got[0]["action"] == "reuse" and got[0]["used_by"] == ["city-a", "city-b"]
    assert got[1]["action"] == "fetch"
    assert T.known(led, [A], today="2027-06-01")[0]["action"] == "fetch"   # older than 180 days


def test_seed_writes_threads_json_rows_with_the_score_left_to_the_page(tmp_path):
    led = T.build(two_pages(tmp_path))
    seed = T.seed(led, [A, B], today="2026-10-01")
    assert [t["permalink"] for t in seed["threads"]] == [A, B]
    assert all(t["score"] is None for t in seed["threads"])
    assert set(seed["threads"][0]) == {"permalink", "title", "subreddit", "posted", "replies",
                                       "score", "stale"}
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
