"""The breed guide ships its film as the click-to-play facade (Known Issue 38, user ruling R8,
2026-09-23).

The breeder first picked S2 — the player full width on a steel band — so
`youtube-nocookie.com/embed/g9iV9RVr_Sk` loaded with the page and Lighthouse Best Practices
read 96 on mobile and desktop, every other rebuilt page 100. The user's ruling is S3, the
facade working rule 14 makes the default: a thumbnail and a play button, the player injected
on the first press. The pick is read from the record through `pickedStyle()`, so the page
needs no markup change; this holds the pick and the built page to each other.
"""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SLUG = "uk-staffordshire-bull-terrier-guide"
VIDEO = "g9iV9RVr_Sk"


def _pick_in_force(rec, sid):
    """`pickedStyle()`'s order: the live approval, the section's own pick, the carried one."""
    live = (rec.get("approval") or {}).get("picks") or {}
    own = next(s for s in rec["sections"] if s["id"] == sid)["options"].get("pick")
    prev = (rec.get("approval_previous") or {}).get("picks") or {}
    return live.get(sid) or own or prev.get(sid)


def test_the_breed_guide_video_pick_is_the_facade():
    rec = json.loads((ROOT / "data/boards" / f"{SLUG}.json").read_text(encoding="utf-8"))
    assert _pick_in_force(rec, "video-breed-guide") == "S3"


def test_the_built_breed_guide_loads_no_player_until_pressed():
    page = ROOT / "dist" / SLUG / "index.html"
    if not page.exists():
        pytest.skip("run npm run build first")
    html = page.read_text(encoding="utf-8")
    # The facade's no-JS fallback carries the player inside <noscript>; nothing outside it may
    # (the VideoObject's `embedUrl` names the player too, and that is data, not a frame).
    live = re.sub(r"<noscript>.*?</noscript>", "", html, flags=re.S)
    assert "<iframe" not in live
    assert re.search(r'<button[^>]*data-video-play', live), "no facade button"
    assert f'data-src="https://www.youtube-nocookie.com/embed/{VIDEO}?autoplay=1"' in live
