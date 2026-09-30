"""The specimen-route prefixes have ONE source, data/specimen-routes.json, read by the Python
duplicate-content audit and by the render harness's DUP corpus (the Task 7b quality review, I1:
the harness had drifted and counted /kit-preview/ and /board-preview/ pages as siblings)."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import dup_content_audit as DUP  # noqa: E402
import rendered_changes as RC  # noqa: E402

DATA = json.loads((ROOT / "data/specimen-routes.json").read_text(encoding="utf-8"))


def test_every_gate_reads_the_one_specimen_list():
    assert DATA["prefixes"] == ["board-preview/", "kit-preview/"]
    assert DUP.SPECIMEN_PREFIXES == tuple(DATA["prefixes"])
    assert RC.SPECIMEN_PREFIXES == tuple(DATA["prefixes"])
    ts = (ROOT / "tests/render/lib/dupCorpus.ts").read_text(encoding="utf-8")
    assert "data/specimen-routes.json" in ts
    # No gate keeps a literal copy of the list of its own.
    for f in ("scripts/dup_content_audit.py", "scripts/rendered_changes.py", "tests/render/lib/dupCorpus.ts"):
        src = (ROOT / f).read_text(encoding="utf-8")
        assert not re.search(r"""["']board-preview/["']\s*,\s*["']kit-preview/["']""", src), f


def test_a_specimen_key_is_one_at_any_depth_and_only_when_anchored():
    for key in ("kit-preview", "kit-preview/city", "kit-preview/city-page", "board-preview/index"):
        assert DUP.is_specimen(key), key
    for key in ("index", "uk-locations/kit-preview", "blue-staffy-kit-preview-uk"):
        assert not DUP.is_specimen(key), key
