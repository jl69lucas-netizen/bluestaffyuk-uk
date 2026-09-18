"""picks.json is the record of the user's thirteen picks. Skipped until it exists
(spec §6); after Task 19 the prune invariants must hold too."""
import importlib.util, json, pathlib, re, subprocess, sys
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[2]
PICKS = ROOT / "data/design/picks.json"
KIT = ROOT / "src/components/kit"
IDS = [r["id"] for r in json.loads((ROOT / "data/design/components.json").read_text())]


def test_pull_script_converts_inbox_rows(tmp_path):
    inbox = tmp_path / "inbox.json"
    rows = {f"picks/{i}": {"component": i, "variant": "c", "note": "", "at": "2026-09-19T10:00:00Z", "by": "u"} for i in IDS}
    rows["picks/mark"] = {"component": "mark", "variant": "c", "note": "", "at": "2026-09-19T10:00:00Z", "by": "u"}
    inbox.write_text(json.dumps(rows))
    out = tmp_path / "picks.json"
    r = subprocess.run([sys.executable, str(ROOT / "scripts/pull_design_picks.py"), "--inbox", str(inbox), "--out", str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    d = json.loads(out.read_text())
    assert set(d["picks"]) == set(IDS) and all(v["variant"] == "c" for v in d["picks"].values())


def test_pull_script_refuses_an_incomplete_set(tmp_path):
    inbox = tmp_path / "inbox.json"
    inbox.write_text(json.dumps({"picks/hero": {"component": "hero", "variant": "a"}}))
    r = subprocess.run([sys.executable, str(ROOT / "scripts/pull_design_picks.py"), "--inbox", str(inbox), "--out", str(tmp_path / "p.json")], capture_output=True, text=True)
    assert r.returncode == 2 and "missing" in r.stdout


def _builder():
    spec = importlib.util.spec_from_file_location("build_picks_board", ROOT / "scripts/build_picks_board.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_board_has_a_row_per_component_plus_the_mark():
    """The committed board must be what the builder produces from the current data."""
    mod = _builder()
    committed = (ROOT / "docs/artifacts/design-picks.html").read_text()
    rows = json.loads((ROOT / "data/design/components.json").read_text())
    canvas = json.loads((ROOT / "data/design/artifacts.json").read_text())["canvas"]
    assert committed == mod.build(rows, canvas), "run python3 scripts/build_picks_board.py"

    ids = re.findall(r'<section class="row" data-id="([^"]+)"', committed)
    assert ids == ["mark"] + [r["id"] for r in rows]
    assert len(ids) == 14
    for i in ids:
        for v in "abcde":
            assert f'name="pick-{i}" value="{v}"' in committed, (i, v)
    assert canvas in committed


@pytest.mark.skipif(not PICKS.exists(), reason="picks.json arrives after the user picks (spec §6)")
def test_picks_json_is_complete_and_valid():
    d = json.loads(PICKS.read_text())
    assert set(d["picks"]) == set(IDS)
    assert all(v["variant"] in "abcde" for v in d["picks"].values())
    assert "mark" in d and d["mark"] in "abcde"


@pytest.mark.skipif(not PICKS.exists() or (KIT / "_variant.ts").exists(), reason="prune (Task 19) not run yet")
def test_after_prune_no_variant_prop_remains():
    for f in KIT.glob("*.astro"):
        assert "variant" not in f.read_text(), f.name
    assert not (ROOT / "src/pages/design-canvas").exists()
