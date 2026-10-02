#!/usr/bin/env python3
"""og_slots.py — board block 7d, "OG images": 4–5 generated photo slots proposed per page,
the share card first.

    python3 scripts/og_slots.py <slug>        # print the block 7d markdown for the board

The breeder wrote "OG images: 4–5 per page". This is interpretation (a), the recommended one,
pending their answer: 4–5 GENERATED photo slots per page, each beside the served photos
(working rule 11 — a served image or its alt is never replaced).

  Slot 1   `og-share`, the Open Graph share card, 1200×630 (IMAGE-DESIGNS.md §1, "one per
           page"), framing style C (Editorial Split). Its subject is the hero asset's alt —
           §1 says the same subject as the hero, recomposed. No hero alt on the board is
           written NOT FETCHED, never guessed.
  Slot 2.. `og-<section id>`, on the highest-intent body H2s, in the in-body 1408×768 box
           (§1a; scripts/bake_images.py BOX and scripts/reframe_og.py W, H). Framing styles
           cycle A, E, D, H; never B (Blur-Fill is social-only and refused on new pages by
           scripts/ingest_image.py).

INTENT. A board section's `intent` is a free label ("Delivery and collection"), not a
search-intent word. A label that IS one of research_board.INTENTS is taken as it stands;
otherwise the H2 heading and the label are matched against the cue lists below,
transactional first, then commercial, else informational. Eligible sections are taken
transactional, then commercial, then the rest, each tier in board order. Frame sections (hero,
counter, trust, contents, takeaways, reviews, FAQ blocks, newsletter, form/enquiry) never get
a slot.

Every slot carries `source: "generate"`, `status: "proposed"`, w/h, og_style, the section id,
its subject and a `prompt_brief`: the subject plus IMAGE-DESIGNS.md §3's negative list,
verbatim (read from the file, never retyped). n defaults to 5 and is clamped to 4..5; a page
with too few eligible sections gets fewer, and the block says so.

Board Task 7 renders one radio group per slot, `pick-og:<slot>`, values use / skip. A used
slot's generated image is then approved by the hash of its bytes at STOP 4
(`og:<style>:<sha12>`, scripts/image_rules.py).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import image_designs  # noqa: E402
from term_density import md_table  # noqa: E402

SHARE = {"slot": "og-share", "w": 1200, "h": 630, "og_style": "C"}
INBODY_W, INBODY_H = 1408, 768
STYLE_CYCLE = ("A", "E", "D", "H")
N_MIN, N_MAX, N_DEFAULT = 4, 5, 5
INTENTS = ("transactional", "commercial", "informational", "navigational", "local")
TIER = {"transactional": 0, "commercial": 1}

TRANSACTIONAL = re.compile(
    r"\bdeposit|\bprice|\bcost|\bavailable\b|\bbuy|\breserv|\bfor sale\b|\bdeliver|\bcollect"
    r"|\border\b|£", re.I)
COMMERCIAL = re.compile(
    r"\bbreeder|\bhealth[- ]tested\b|\bpaperwork\b|\bkennel club\b|\bguarantee|\bvs\b"
    r"|\bversus\b|\bcompare|\bbest\b|\breview", re.I)

FRAME_SHAPES = {"hero", "stats", "trust", "dial", "takeaways", "reviews", "faq", "form"}
FRAME_IDS = {"top", "hero", "counter", "trust", "contents", "key-takeaways", "takeaways",
             "newsletter", "enquiry", "form"}
NF = "NOT FETCHED"
USAGE = "usage: python3 scripts/og_slots.py <slug>   (reads data/boards/<slug>.json)"


def negative_list(path: Path | None = None) -> str:
    """IMAGE-DESIGNS.md §3's negative list, verbatim: the blockquote joined to one line."""
    text = Path(path or image_designs.DOC).read_text(encoding="utf-8")
    quote = [ln[1:].strip() for ln in image_designs._section_lines(text, 3)
             if ln.startswith(">")]
    if not quote:
        raise ValueError("IMAGE-DESIGNS.md §3 has no negative-list blockquote")
    return " ".join(quote)


def _is_frame(sec: dict) -> bool:
    sid = sec.get("id", "")
    label = (sec.get("intent") or "").lower()
    return (sid.startswith(("faq-", "review-")) or sid in FRAME_IDS
            or sec.get("shape") in FRAME_SHAPES
            or "newsletter" in (sec.get("component") or "").lower()
            or "newsletter" in label or "enquiry" in label)


def intent_of(sec: dict) -> str:
    label = (sec.get("intent") or "").strip().lower()
    if label in INTENTS:
        return label
    text = "%s %s" % (sec.get("heading", ""), sec.get("intent", ""))
    if TRANSACTIONAL.search(text):
        return "transactional"
    if COMMERCIAL.search(text):
        return "commercial"
    return "informational"


def eligible(board: dict) -> list[dict]:
    """Body sections ranked transactional, commercial, the rest; board order within a tier."""
    body = [s for s in board.get("sections", []) if not _is_frame(s)]
    order = sorted(range(len(body)), key=lambda i: (TIER.get(intent_of(body[i]), 2), i))
    return [body[i] for i in order]


def _hero_alt(board: dict) -> str | None:
    assets = {a.get("slot"): a for a in board.get("assets", [])}
    for sec in board.get("sections", []):
        if sec.get("shape") == "hero" or sec.get("id") in ("top", "hero"):
            for img in sec.get("images") or []:
                slot = img.get("slot") if isinstance(img, dict) else img
                alt = (assets.get(slot) or {}).get("alt")
                if alt:
                    return alt
    for slot, a in assets.items():
        if str(slot).endswith("-hero") and a.get("alt"):
            return a["alt"]
    return None


def _hero_section(board: dict) -> str:
    for sec in board.get("sections", []):
        if sec.get("shape") == "hero" or sec.get("id") in ("top", "hero"):
            return sec.get("id", "top")
    return "top"


def _brief(subject: str, neg: str) -> str:
    return "Subject: %s Negative: %s" % (subject.rstrip(".") + ".", neg)


def propose(board: dict, n: int = N_DEFAULT) -> list[dict]:
    n = max(N_MIN, min(N_MAX, int(n)))
    neg = negative_list()
    alt = _hero_alt(board)
    subject = alt or "%s — the board has no hero asset alt" % NF
    slots = [dict(SHARE, section=_hero_section(board), where="Share card (Open Graph)",
                  kind="photo", source="generate", status="proposed", subject=subject,
                  prompt_brief=_brief(subject, neg))]
    for i, sec in enumerate(eligible(board)[: n - 1]):
        heading = sec.get("heading", "")
        slots.append({"slot": "og-%s" % sec.get("id"), "section": sec.get("id"),
                      "where": "H2 · %s" % heading, "kind": "photo", "source": "generate",
                      "status": "proposed", "w": INBODY_W, "h": INBODY_H,
                      "og_style": STYLE_CYCLE[i % len(STYLE_CYCLE)],
                      "intent": intent_of(sec), "subject": heading,
                      "prompt_brief": _brief(heading, neg)})
    return slots


def block(board: dict, n: int = N_DEFAULT) -> str:
    want = max(N_MIN, min(N_MAX, int(n)))
    slots = propose(board, n)
    names = image_designs.load()["og_names"]
    out = ["### OG images (block 7d)", "",
           "This is a proposal, pending the breeder's answer on what \"OG images: 4–5 per "
           "page\" means (option a: 4–5 generated photo slots, the share card first). Each "
           "generated photo sits beside the served photos, never in place of one or its alt "
           "(working rule 11), and each is approved by the hash of its exact bytes at STOP 4.",
           ""]
    if len(slots) < want:
        out += ["Only %d eligible body section%s on this board, so %d slot%s are proposed — "
                "fewer than the %d asked for." % (len(slots) - 1,
                                                    "" if len(slots) == 2 else "s",
                                                    len(slots), "" if len(slots) == 1 else "s",
                                                    want), ""]
    rows = [[s["slot"], s["where"], "%d×%d" % (s["w"], s["h"]),
             "%s %s" % (s["og_style"], names.get(s["og_style"], "")), s["subject"]]
            for s in slots]
    out += [md_table(["Slot", "Where", "Size", "Framing style", "Subject"], rows), "",
            "The board's radios will be `pick-og:<slot>` with the values `use` and `skip`. "
            "Gemini generation currently fails with HTTP 402 (prepayment credits depleted), "
            "so no image is generated until credits are restored."]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0].startswith("-"):
        print(USAGE, file=sys.stderr)
        return 2
    path = ROOT / "data/boards" / ("%s.json" % argv[0])
    if not path.is_file():
        print("no board at %s\n%s" % (path.relative_to(ROOT), USAGE), file=sys.stderr)
        return 2
    try:
        board = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print("%s is not JSON: %s" % (path.relative_to(ROOT), e), file=sys.stderr)
        return 2
    print(block(board))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
