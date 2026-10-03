#!/usr/bin/env python3
"""generated_briefs.py — the rule 9 guards every GENERATED image brief goes through.

    real_names()      every real dog, person or litter name the repo holds
    unnamed(text)     `text` with each of those names removed (possessives and joins tidied)
    negative_list()   IMAGE-DESIGNS.md §3's negative list, verbatim, as one line

A generated image's subject or prompt never names a real dog, person or litter (CLAUDE.md
rule 9). These lived in og_slots.py, which proposed generated OG photos; the breeder's
ruling of 2026-10-02 (answer board q06) made block 7d ORIGINAL photos instead
(scripts/original_slots.py), so the guards moved here, where the generated-image steps that
come after the original photos and the infographics read them.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import image_designs  # noqa: E402


def negative_list(path: Path | None = None) -> str:
    """IMAGE-DESIGNS.md §3's negative list, verbatim: the blockquote joined to one line."""
    text = Path(path or image_designs.DOC).read_text(encoding="utf-8")
    quote = [ln[1:].strip() for ln in image_designs._section_lines(text, 3)
             if ln.startswith(">")]
    if not quote:
        raise ValueError("IMAGE-DESIGNS.md §3 has no negative-list blockquote")
    return " ".join(quote)


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
