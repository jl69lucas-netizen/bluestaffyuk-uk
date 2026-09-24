"""The release guard on IndexNow is the only thing between a placeholder and Bing.

`scripts/indexnow_submit.py` is ported from CAG and inactive until project 6. The guard is
worth a test rather than a comment because the failure is silent and external: a run without
it POSTs `SITE_URL_PLACEHOLDER` to a public API, and IndexNow reads junk submissions as a
trust signal about the host. So every test here patches `urllib.request.urlopen` to raise —
a test that passes because the network was down would prove nothing.
"""
import importlib
import sys

import pytest


def _load(monkeypatch, tmp_path, **env):
    """Import the script fresh with a given environment: HOST is read at import time."""
    for k in ("BSUK_RELEASE", "SITE_URL", "INDEXNOW_KEY"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    (tmp_path / "public").mkdir(exist_ok=True)
    (tmp_path / "dist").mkdir(exist_ok=True)
    monkeypatch.chdir(tmp_path)
    sys.modules.pop("indexnow_submit", None)
    mod = importlib.import_module("indexnow_submit")

    def _no_network(*a, **k):  # pragma: no cover - firing this IS the failure
        raise AssertionError("the script opened a socket")

    monkeypatch.setattr(mod.urllib.request, "urlopen", _no_network)
    return mod


def _run(mod, monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", ["indexnow_submit.py", *argv])
    with pytest.raises(SystemExit) as e:
        mod.main()
    return e.value.code


def test_refuses_without_the_release_flag(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, SITE_URL="https://example.invalid")
    assert _run(mod, monkeypatch, ["index"]) == 2
    err = capsys.readouterr().err
    assert err.startswith("REFUSED: IndexNow is inactive until project 6.")


def test_refuses_the_placeholder_even_with_the_flag(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://SITE_URL_PLACEHOLDER")
    assert _run(mod, monkeypatch, ["index"]) == 2
    assert "still a placeholder" in capsys.readouterr().err


def test_refuses_an_unset_site_url_even_with_the_flag(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1")
    assert _run(mod, monkeypatch, ["index"]) == 2
    assert "unset or still a placeholder" in capsys.readouterr().err


def test_dry_run_prints_the_urls_and_sends_nothing(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://example.invalid")
    monkeypatch.setattr(sys, "argv", ["indexnow_submit.py", "--dry-run", "puppies", "/"])
    assert mod.main() == 0
    out = capsys.readouterr().out
    assert "https://example.invalid/puppies/" in out
    assert "https://example.invalid/" in out
    assert "--dry-run" in out


def test_dry_run_never_prints_the_key(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://example.invalid",
                INDEXNOW_KEY="0123456789abcdef0123456789abcdef")
    monkeypatch.setattr(sys, "argv", ["indexnow_submit.py", "--dry-run", "puppies"])
    assert mod.main() == 0
    captured = capsys.readouterr()
    assert "0123456789abcdef" not in captured.out + captured.err


def test_malformed_sitemap_is_a_clean_refusal(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://example.invalid")
    (tmp_path / "dist" / "page-sitemap.xml").write_text(
        "<urlset><url><loc>https://example.inv", encoding="utf-8")
    assert _run(mod, monkeypatch, ["--all"]) == 2
    err = capsys.readouterr().err
    assert err.startswith("REFUSED: no submittable URLs")
    assert "Traceback" not in err


def test_build_artifacts_are_filtered_out(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://example.invalid")
    monkeypatch.setattr(sys, "argv", ["indexnow_submit.py", "--dry-run", "puppies", "thank-you"])
    assert mod.main() == 0
    out = capsys.readouterr().out
    assert "/thank-you/" not in out
    assert "/puppies/" in out


def test_a_pretty_printed_sitemap_still_yields_urls(monkeypatch, tmp_path, capsys):
    """A `<loc>` on its own indented line is valid XML and common in generated sitemaps.
    A regex that demanded the URL abut its tags would report 'nothing to submit' on a
    perfectly good sitemap — a false negative that looks like a clean refusal."""
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://example.invalid")
    (tmp_path / "dist" / "page-sitemap.xml").write_text(
        "<urlset>\n  <url>\n    <loc>\n      https://example.invalid/puppies/\n    </loc>\n"
        "  </url>\n  <url><loc>https://example.invalid/about/</loc></url>\n</urlset>\n",
        encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["indexnow_submit.py", "--dry-run", "--all"])
    assert mod.main() == 0
    out = capsys.readouterr().out
    assert "https://example.invalid/puppies/" in out
    assert "https://example.invalid/about/" in out


# ── the sitemaps it reads are the ones the generator writes (2026-09-23) ──────
# It read public/{page,post,local}-sitemap.xml, while scripts/generate_sitemaps.py writes
# dist/{page,post,location,puppy,video}-sitemap.xml after every build: `--all` would have
# submitted no city page, no puppy page — and, reading public/, nothing at all.
def test_it_reads_every_url_sitemap_the_generator_writes(monkeypatch, tmp_path):
    import generate_sitemaps
    mod = _load(monkeypatch, tmp_path)
    assert set(mod.SITEMAPS) == {"%s-sitemap.xml" % s for s in generate_sitemaps.SHARDS
                                 if s != "video"}, "the video sitemap only repeats page URLs"
    assert mod.SITEMAP_DIR.as_posix() == "dist"


def test_all_submits_the_city_and_puppy_pages(monkeypatch, tmp_path, capsys):
    mod = _load(monkeypatch, tmp_path, BSUK_RELEASE="1", SITE_URL="https://example.invalid")
    for shard, path in (("page", "about"), ("location", "uk-locations/leeds"),
                        ("puppy", "available-puppies/roman")):
        (tmp_path / "dist" / f"{shard}-sitemap.xml").write_text(
            f"<urlset><url><loc>https://example.invalid/{path}/</loc></url></urlset>",
            encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["indexnow_submit.py", "--dry-run", "--all"])
    assert mod.main() == 0
    out = capsys.readouterr().out
    for path in ("about", "uk-locations/leeds", "available-puppies/roman"):
        assert f"https://example.invalid/{path}/" in out


# ── the indexing skill says the same thing the script does (2026-09-24) ─────────
# After the script moved to dist/, the skill's STEP 1 and STEP 2 still globbed
# public/*.xml ("public/ is where BSUK's sitemaps live"), and it said the key was read
# from public/<key>.txt on disk. The sitemaps are build output in dist/; the script reads
# the key from INDEXNOW_KEY and checks the live key file at $SITE_URL/<key>.txt.
import pathlib  # noqa: E402
import re  # noqa: E402

INDEXING_SKILL = pathlib.Path(__file__).resolve().parents[2] / ".claude/skills/bsuk-indexing/SKILL.md"
PUBLIC_SITEMAP = re.compile(r"public/\*\.xml|public/[\w.-]*sitemap|public/`?\s+is where|"
                            r"SITE_ROOT\s*=\s*[\"']public")
KEY_ON_DISK = re.compile(r"key is read from `public/|read it from `public/")


def test_the_indexing_skill_reads_sitemaps_from_dist_and_the_key_from_the_env():
    lines = INDEXING_SKILL.read_text(encoding="utf-8").splitlines()
    bad = [f"SKILL.md:{n}  {l.strip()}" for n, l in enumerate(lines, 1)
           if PUBLIC_SITEMAP.search(l) or KEY_ON_DISK.search(l)]
    assert bad == [], "the skill contradicts scripts/indexnow_submit.py:\n  " + "\n  ".join(bad)
    roots = re.findall(r"(?m)^SITE_ROOT\s*=\s*\"([^\"]*)\"", "\n".join(lines))
    assert roots and set(roots) == {"dist"}, roots
