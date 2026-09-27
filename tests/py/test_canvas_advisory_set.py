"""The canvas smoke demotes exactly the checks it names, never by registry severity.

Review of Task 13b (2026-09-28): 4214d23 made the smoke skip any REUSED check whose registry
severity is `advisory`, which silently demoted a11y-text-contrast-aa and a11y-no-duplicate-ids —
two checks that had failed the smoke until then. The set is named in the spec and pinned here.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC = (ROOT / "tests" / "render" / "canvas.spec.ts").read_text(encoding="utf-8")


def _set(name):
    m = re.search(name + r"\s*=\s*new Set\(\[([^\]]*)\]\)", SPEC)
    assert m, f"{name} is not declared as a literal Set in canvas.spec.ts"
    return set(re.findall(r"'([^']+)'", m.group(1)))


def _list(name):
    m = re.search(r"const " + name + r"\s*=\s*\[([^\]]*)\]", SPEC)
    assert m, f"{name} is not declared in canvas.spec.ts"
    return set(re.findall(r"'([^']+)'", m.group(1)))


def test_the_canvas_advisory_set_is_exactly_img_not_upscaled():
    assert _set("CANVAS_ADVISORY") == {"img-not-upscaled"}
    assert _set("CANVAS_ADVISORY") <= _list("REUSED")


def test_the_contrast_and_id_checks_still_fail_the_smoke():
    assert {"a11y-text-contrast-aa", "a11y-no-duplicate-ids"} <= _list("REUSED") - _set("CANVAS_ADVISORY")


def test_advisory_handling_never_reads_registry_severity():
    assert not re.search(r"severity\s*===\s*'advisory'", SPEC), \
        "the smoke must key its advisory branch on CANVAS_ADVISORY, not the registry"
