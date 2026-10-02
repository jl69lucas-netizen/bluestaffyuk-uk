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
           written NOT FETCHED, never guessed. The subject is built from the alt's cues
           (dam, puppies), never its words: no generated image's subject or prompt_brief
           names a real dog, person or litter (CLAUDE.md rule 9; `real_names`, `unnamed`).
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
    r"\b(?:deposits?|prices?|priced|pricing|costs?|costing|available|buy|buying|"
    r"reserv(?:e|ed|ing|ation|ations)|for sale|deliver(?:y|ed|ing|ies)?|"
    r"collect(?:ion|ing|ed)?|orders?)\b|£", re.I)
COMMERCIAL = re.compile(
    r"\b(?:breeders?|health[- ]tested|paperwork|kennel club|guarantee[sd]?|vs|versus|"
    r"compar(?:e|ed|ing|ison|isons)|best|reviews?)\b", re.I)

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
    body = [s for s in board.get("sections", []) if s.get("id") and not _is_frame(s)]
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


BREED = "a blue Staffordshire Bull Terrier"


def real_names() -> set[str]:
    """Every real dog, person or litter name the repo holds, so none reaches a generated
    image's subject or prompt (CLAUDE.md rule 9): the puppies in data/puppies.json, the named
    dogs in data/bsuk-ontology.json (single-word Organism entities: the dam and the sire; the
    breed and the coat are multi-word), the breeder's full name (data/settings.json
    breeder_name) and each reviewer's full display name (data/reviews.json). Person names are
    whole phrases only: a lone first name or surname ("Bright", "Victoria") is ordinary
    English and stays."""
    names: set[str] = set()

    def load(rel):
        try:
            return json.loads((ROOT / rel).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def add(full):
        full = str(full or "").strip()
        if not full:
            return
        names.add(full)

    pups = load("data/puppies.json") or []
    for p in pups if isinstance(pups, list) else []:
        add(p.get("name"))
    onto = load("data/bsuk-ontology.json") or {}
    for e in onto.get("entities", []) if isinstance(onto, dict) else []:
        name = e.get("name", "")
        if e.get("class") == "Organism" and name[:1].isupper() and " " not in name:
            add(name)
    settings = load("data/settings.json") or {}
    add(settings.get("breeder_name") if isinstance(settings, dict) else "")
    reviews = load("data/reviews.json") or []
    for r in reviews if isinstance(reviews, list) else []:
        add(r.get("name"))
    return names


def unnamed(text: str, names: set[str] | None = None) -> str:
    """`text` with every real name removed, case-insensitively and longest first, with its
    possessive ('s or ’s). When a name was removed, the joins it leaves (a stranded hyphen or
    dash, doubled spaces, a space before punctuation) are tidied; text with no name is
    returned untouched."""
    names = real_names() if names is None else names
    out = text
    for n in sorted(names, key=len, reverse=True):
        pat = r"(?<![\w])%s(?![\w])(?:['’]s\b)?" % re.escape(n)
        out = re.sub(pat, "", out, flags=re.I)
    if out == text:
        return text
    out = re.sub(r"(?<!\w)[-–—/&]+(?!\w)", " ", out)       # a join left with nothing beside it
    out = re.sub(r"(?<!\w)[-–—]+(?=\w)|(?<=\w)[-–—]+(?!\w)", " ", out)
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"\s+([,.?!:;])", r"\1", out)
    return out.strip(" ,;:-–—")


def _share_subject(alt: str | None) -> str:
    """The hero's subject without any proper name: built from the alt's cues, never its words."""
    if not alt:
        return "%s — the board has no hero asset alt" % NF
    low = alt.lower()
    if re.search(r"\b(dam|mother|mum)\b", low) and re.search(r"\bpup", low):
        return "%s dam with her puppies, at home" % BREED
    if re.search(r"\bpup", low):
        return "%s puppy, at home" % BREED
    return "%s, at home" % BREED


def _hero_section(board: dict) -> str:
    for sec in board.get("sections", []):
        if sec.get("shape") == "hero" or sec.get("id") in ("top", "hero"):
            return sec.get("id", "top")
    return "top"


def _brief(subject: str, neg: str) -> str:
    subject = subject.rstrip()
    end = "" if subject[-1:] in ".?!" else "."
    return "Subject: %s%s Negative: %s" % (subject, end, neg)


def propose(board: dict, n: int = N_DEFAULT) -> list[dict]:
    n = max(N_MIN, min(N_MAX, int(n)))
    neg = negative_list()
    names = real_names()
    subject = unnamed(_share_subject(_hero_alt(board)), names)
    slots = [dict(SHARE, section=_hero_section(board), where="Share card (Open Graph)",
                  kind="photo", source="generate", status="proposed", subject=subject,
                  prompt_brief=_brief(subject, neg))]
    for i, sec in enumerate(eligible(board)[: n - 1]):
        heading = unnamed(sec.get("heading", ""), names)
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
        k = len(slots) - 1
        out += ["Only %d eligible body section%s on this board, so %d %s proposed — fewer "
                "than the %d asked for." % (k, "" if k == 1 else "s", len(slots),
                                            "slot is" if len(slots) == 1 else "slots are",
                                            want), ""]
    rows = [[s["slot"], s["where"], "%d×%d" % (s["w"], s["h"]),
             "%s %s" % (s["og_style"], names.get(s["og_style"], "")), s["subject"]]
            for s in slots]
    out += [md_table(["Slot", "Where", "Size", "Framing style", "Subject"], rows), "",
            "Each slot below has a use/skip choice (`pick-og:<slot>`); it is not required "
            "for approval. "
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
