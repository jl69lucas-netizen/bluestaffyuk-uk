"""A city board writes its own alt for every image that has no served alt.

Working rule 11 keeps a served alt word for word on an image's first use, so two city pages
showing the same served photo share its alt by design. An image with NO served alt has no
such reason: its alt is written for the page. Manchester's board (2026-10-07) carried
London's alt for Lisa Bright's photo word for word, because that copy has no served-alt
record (it was added beside a served file at London's Asset Gate, ab26a887). A copied alt is
a sibling's prose (working rule 8) and a duplicate across two pages.

This holds every city board (meta.layout_type "city") against every other: an alt on an
image without a served alt never appears verbatim on another city board.
"""
import itertools
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import check_city_canvas as C  # noqa: E402


def _city_boards():
    out = {}
    for f in sorted((ROOT / "data/boards").glob("*.json")):
        b = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(b, dict) and (b.get("meta") or {}).get("layout_type") == "city":
            out[b["meta"]["slug"]] = b
    return out


def _norm(alt):
    return " ".join((alt or "").split())


def test_there_are_city_boards_to_compare():
    assert len(_city_boards()) >= 2


def test_no_city_board_reuses_another_city_boards_alt_on_an_image_without_a_served_alt():
    served = C.served_alts()
    boards = _city_boards()
    examined, clashes = 0, []
    for (sa, a), (sb, b) in itertools.permutations(boards.items(), 2):
        theirs = {_norm(x.get("alt")) for x in b.get("assets", []) if x.get("alt")}
        for row in a.get("assets", []):
            f, alt = row.get("file"), _norm(row.get("alt"))
            if not f or not alt or "/images/" not in f:
                continue
            name = f.split("/images/", 1)[1]
            if name in served:
                continue                           # rule 11: the served alt is kept, shared
            examined += 1
            if alt in theirs:
                clashes.append(f"{sa} {row['slot']} ({name}) repeats {sb}'s alt: {alt!r}")
    assert examined, "no image without a served alt on any city board: the check examined nothing"
    assert clashes == [], "\n".join(clashes)
