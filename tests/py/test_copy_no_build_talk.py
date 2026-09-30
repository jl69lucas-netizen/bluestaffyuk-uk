"""copy-no-build-talk — a rebuilt page's <main> never prints the build's own notes as copy.

WHY THIS EXISTS. The pre-close-out audit of project 4 (2026-09-22) found the build's working
vocabulary printed on the live pages as if it were writing for the reader: table captions
naming the JSON file a figure came from ("…, from data/price-matrix.json"), video captions
saying a film was kept "at its original id", a blog-hub paragraph pointing the reader at "the
record's own accounting", and a dozen sentences about "our settings file", values "on disk"
and numbers "typed into this page". Every one of them was true about the BUILD and meaningless
to a buyer. No gate read for it: the prose gates judge voice, originality and claims, and a
sentence that is honest about the pipeline passes all three.

WHAT IT READS. The visible text of `<main>` on every page in data/facts/rebuilt.json, from the
BUILT page in dist/ (scripts and styles stripped, entities decoded). The chrome outside <main>
is the kit's and is not page copy.

THE PATTERN is the audit's own — `data/`, `.json`, `verbatim`, `migrated`, `board`,
`original id`, `rule <n>`, and the `record` family — plus the developer phrasing the same
audit found beside it (`settings file`, `on disk`, `typed into`, `repository`, …).

THE ALLOWLIST is for genuine reader uses, and there is only one family of them: "record" is
an ordinary English word on a breeder's site ("health records", "recorded clear of both
conditions", "the record that travels with the dog"). So the bare word is allowed, and what
fails is the build's use of it — the board record as a subject ("the record's own
accounting", "the record says", "this record"). Any other allowance has to be added here by
name, with the sentence that earns it.
"""
import html
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
REBUILT = json.loads((ROOT / "data/facts/rebuilt.json").read_text(encoding="utf-8"))

#: The audit's pattern (record handled separately below) plus the developer phrasing it found.
BUILD_TALK = re.compile(
    r"data/|\.json\b|\bverbatim\b|\bmigrat(?:ed|ion)\b|\bboards?\b|\boriginal id\b|\brule \d"
    r"|\bsettings file\b|\bour (?:own )?settings\b|\bon disk\b|\btyped into\b|\brepositor(?:y|y's|y’s)\b"
    r"|\bcommitted history\b|\bread out of data\b|\bone edit in one place\b|\bvalue on disk\b",
    re.I,
)
#: "record" as the BUILD uses it: the board record as a thing that speaks or owns.
BUILD_RECORD = re.compile(
    r"\b(?:the|this|board|page's|page’s) record(?:'s|’s)\b|\brecord(?:'s|’s) own\b"
    r"|\b(?:this|board|the page's|the page’s) record\b"
    r"|\bthe record (?:says|names|gives|holds|carries|approved|excuses|accounts)\b",
    re.I,
)
#: Named exceptions to BUILD_TALK: (slug, phrase) pairs a reader genuinely needs. Empty — the
#: audit found none; an entry added here must quote the sentence it allows.
ALLOW = set()


def _main_text(slug):
    f = DIST / ("index.html" if slug == "index" else f"{slug}/index.html")
    if not f.exists():
        return None
    raw = f.read_text(encoding="utf-8")
    m = re.search(r"<main\b.*?</main>", raw, flags=re.S | re.I)
    body = m.group(0) if m else raw
    body = re.sub(r"<(script|style)\b[\s\S]*?</\1>", " ", body, flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    return re.sub(r"\s+", " ", text)


def _hits(slug, text):
    out = []
    for rx in (BUILD_TALK, BUILD_RECORD):
        for m in rx.finditer(text):
            if (slug, m.group(0).lower()) in ALLOW:
                continue
            a, b = max(0, m.start() - 60), m.end() + 40
            out.append(f"{slug}: …{text[a:b]}…")
    return out


def test_the_pattern_catches_what_the_audit_found():
    """The phrases the 2026-09-22 audit rewrote, as they were printed, must all still fail."""
    found = [
        "What you pay us, from data/price-matrix.json and data/settings.json",
        "The video this page has always carried, at its original id.",
        "and the record's own accounting says which word moved and why.",
        "Staffordshire Bull Terrier breed facts, as the migrated guide states them",
        "Our settings file records no term for one",
        "Kennel Note: Every Cell Is a Value on Disk",
        "None of these numbers is typed into the page",
        "it comes from the committed history of this repository",
    ]
    for s in found:
        assert _hits("x", s), s


def test_reader_uses_of_record_are_allowed():
    for s in [
        "with all his papers and medical records meticulously organized",
        "Both our parents are recorded clear of both conditions",
        "the dates are written on the record that travels with the dog",
        "What the Website Records Automatically",
        "A Card Is A Record, Not A Promise",
    ]:
        assert not _hits("x", s), s


@pytest.mark.parametrize("slug", REBUILT)
def test_copy_no_build_talk(slug):
    text = _main_text(slug)
    if text is None:
        pytest.skip(f"dist/ has no built page for {slug} — run npm run build")
    hits = _hits(slug, text)
    assert not hits, "build notes printed as page copy:\n" + "\n".join(hits)
