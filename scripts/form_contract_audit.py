#!/usr/bin/env python3
"""Form contract audit over dist/.

Every non-search <form> must POST to the one Formspree endpoint with no Netlify residue.
A form is classed "newsletter" only when its non-hidden, non-_gotcha controls are
exactly one type="email" input; every other form (including one with no textarea) is
classed "inquiry" and must carry its page's contract:
  full  — the six named controls of the built inquiry form (every in-scope page,
          the contact page included)
  short — blog/* posts: name, email, message
  none  — the uk-locations/* cluster, the hubs (no inquiry forms today) and the
          NON_CONTENT_ROUTES below; those still owe the method and the one endpoint.
Whatever the contract, every inquiry form also owes its option VALUES (`value_problems`): a
collect-or-delivery `handover` offers exactly "collect" and "delivery", and a puppy select offers
only data/puppies.json slugs, "waiting-list", "any-boy" and "any-girl".

This is the Python half of the same contract tests/render/checks/form.ts enforces, and
the two must agree or they will give different verdicts on the same page.

`n` is 1-based over ALL <form> elements in a page's document order, search forms
included, matching what a browser script will find at `document.forms[n-1]` — it is
not scoped to in-scope or inquiry forms only. A `<form>` opened while another form is
still open is ignored on the start tag (browsers drop nested forms), and content inside
<template>/<noscript> is never scanned. `form=` attribute association (a control outside
its form's tags claimed via the HTML `form=""` attribute) is not modelled.

  python3 scripts/form_contract_audit.py              # table + exit 1 on any problem
  python3 scripts/form_contract_audit.py --json       # also write the JSON report

Exit code: 1 when any form fails the contract, 2 when no forms were examined at all
(a zero-page run is never a pass) or when PUBLIC_FORMSPREE_ID is unset; 0 otherwise.
`--fail-on-error` is accepted for symmetry with the other gates and changes nothing
here: a contract failure is always fatal.
"""
import argparse, json, os, pathlib, re, sys
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _slugs import page_key  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DEFAULT_JSON = ROOT / "docs/reports/form_contract_audit.json"

PAGE_MAP = ROOT / "data/page-map.json"


def _endpoint():
    """The one Formspree endpoint, read from the environment at call time, never
    hard-coded. The id is a credential-adjacent fact that lives in .env (spec §8); a
    literal here would be a second source of truth that goes stale the day the form
    moves, and would put a real endpoint in a committed file.

    Read LAZILY, not at import: a module-level sys.exit makes `--help`, and any import
    of this module, impossible without the id. Exit 2 = the gate cannot run, the code
    board_gate.py and evidence_audit.py use; exit 1 would read as "ran, found one
    problem".
    """
    fid = os.environ.get("PUBLIC_FORMSPREE_ID", "")
    if not fid:
        print("REFUSED: PUBLIC_FORMSPREE_ID is unset — a form audit that matches "
              "nothing would report every form clean. Set it in .env (see "
              ".env.example).", file=sys.stderr)
        sys.exit(2)
    return f"https://formspree.io/f/{fid}"

# BSUK's contract, read off the built contact page (dist/uk-blue-staffy-breeders-contact/
# index.html, 2026-09-16). The source repo's seven screening questions were written for a
# different species and a US resale market, and have no BSUK analogue; inventing dog
# equivalents would be inventing a screening policy the breeder has not set. What IS true today is the six named controls,
# the honeypot and the two hidden fields, and that is what this gate holds.
KEYS = [
    ("name", re.compile(r"^name$")),
    ("email", re.compile(r"^email$")),
    ("phone", re.compile(r"^phone$")),
    ("location", re.compile(r"^location$")),
    ("puppy", re.compile(r"^puppy$")),
    ("message", re.compile(r"^(message|msg)$")),
]
# phone and location are present but optional as built; a contract that demanded them
# would report the shipped page as broken.
REQUIRED = ("name", "email", "puppy", "message")
HIDDEN = ("_next", "_subject")
# Spec §5: the puppy control is a <select>, and one of its options is the waiting-list
# choice — the one option both forms build that is not a row of data/puppies.json.
#
# Re-based in project 4 Task 6. Until then the constant named a collection point in the
# city the breeder has LEFT (Known Issue 16), which made this gate require the wrong
# geography of every page it audits in full, and made it report the correct kit form
# (src/components/kit/ContactFormKit.astro) as missing an option — the advisory row of
# Known Issue 22. The kit form is the reference: the Available rows of data/puppies.json
# plus `waiting-list`, and src/components/ContactForm.astro now emits the same set from
# the same data, so both pass the same `full` contract.
PUPPY_OPTION = "waiting-list"
# Beside the waiting list, the two other choices a puppy select may offer that are no single row of
# data/puppies.json: "any of our boys" / "any of our girls" (the Manchester enquiry form, Phase F
# Task 31, ContactFormKit `layout="compact"`). Every other option value must be a puppy's slug: an
# option nobody can be sold is an enquiry about nothing.
PUPPY_CHOICES = (PUPPY_OPTION, "any-boy", "any-girl")
# The collect-or-delivery choice, where a form asks it (the bsuk-contact-form skill, "Delivery, where
# a form asks about it"): the two options are the only two that exist, collection in person and UK
# home delivery. An optional control; when a form carries it, it must offer exactly these two.
HANDOVER_VALUES = ("collect", "delivery")
PUPPIES = ROOT / "data/puppies.json"
SHORT = ("name", "email", "message")
LOCATION = re.compile(r"^uk-locations/")
HUBS = ("available-puppies", "uk-locations", "blog")

# Routes that build a page but are not content pages, listed BY NAME rather than left to
# the slug fallback. `kit-preview` is project 3's hidden noindex route
# (src/pages/kit-preview/index.astro): it mounts each kit component once so the whole kit can
# be read on one page, and so scripts/build_design_canvas.py has a source to cut the
# artboards from. Its ContactFormKit copy is a specimen of one form, not an enquiry form a
# visitor can reach, so the per-page FIELD contract does not apply to it. The endpoint,
# method and netlify-residue checks still do — a specimen posting somewhere else would be a
# real defect, and that is what keeps this from being a way to smuggle a form past the gate.
#
# Named here, and checked BEFORE the page map, rather than folded into the slug heuristic:
# an exclusion nobody can see is how a content page quietly stops being audited. For the
# same reason the exclusion EXPIRES: tests/py/test_form_contract_audit.py requires every
# name in this tuple to exist as src/pages/<name>/, so the day the preview route goes, this
# name has to go with it in the same commit or the suite fails. (Task 19 moved the name
# here from `design-canvas`, which that task deleted.)
#
# The exclusion drops the FIELD checks only. The specimen still owes POST and the one
# endpoint: there is no stub allowance any more, because the canvas's `action` override —
# five live endpoints on one page being five ways for a stray click to send a real enquiry
# — went with the canvas, and the preview mounts exactly one form.
#
# `board-preview` is project 4's equivalent (src/pages/board-preview/[slug].astro): one
# hidden noindex page per DRAFT board record, rendering that record's sections three ways
# each so the page board can show arrangements rather than name them. A `form`-shaped
# section mounts ContactFormKit there, three times over — specimens of one form, none of
# them reachable.
NON_CONTENT_ROUTES = ("kit-preview", "board-preview")


# data/page-map.json's `kind` is what the build actually produced; a hand list of slugs
# drifts the first time a page is added. Kind -> contract:
KIND_CONTRACT = {"rich": "full", "blog": "short", "location": "none"}


@lru_cache(maxsize=1)
def _kinds():
    """{slug: kind} from data/page-map.json; empty when the map is unreadable, in which
    case every page falls back to the slug heuristic."""
    try:
        pages = json.loads(pathlib.Path(PAGE_MAP).read_text(encoding="utf-8"))["pages"]
    except Exception:
        return {}
    return {(p["url"].strip("/") or "index"): p["kind"] for p in pages}


def _contract_name(slug: str) -> str:
    # Whole slug OR first path segment: board-preview's slugs nest (`board-preview/_demo`),
    # and an exclusion that only matched the bare name would leave every child of a
    # non-content route audited as a content page. `kit-preview-notes` is unaffected — that
    # is a different first segment, not a child of `kit-preview`.
    if slug in NON_CONTENT_ROUTES or slug.split("/", 1)[0] in NON_CONTENT_ROUTES:
        return "none"
    kind = _kinds().get(slug)
    if kind in KIND_CONTRACT:
        return KIND_CONTRACT[kind]
    # Fallback for a page absent from the map (a hub, or a page built after the map was
    # last generated): today's slug heuristic.
    if LOCATION.match(slug) or slug in HUBS:
        return "none"
    if slug.startswith("blog/"):
        return "short"
    return "full"


def contract_keys(slug: str) -> list:
    """The (name, regex) pairs this page's inquiry forms must carry."""
    name = _contract_name(slug)
    if name == "none":
        return []
    if name == "short":
        return [k for k in KEYS if k[0] in SHORT]
    return KEYS


def field_checks_apply(slug: str) -> bool:
    return bool(contract_keys(slug))


@lru_cache(maxsize=1)
def _slugs() -> frozenset:
    return frozenset(p["slug"] for p in json.loads(PUPPIES.read_text(encoding="utf-8")))


def puppy_values() -> set:
    """Every value a puppy select may offer besides its empty prompt: a slug of data/puppies.json
    (any status: a page may still offer a reserved puppy), or one of PUPPY_CHOICES."""
    return set(_slugs()) | set(PUPPY_CHOICES)


def value_problems(ctl: list) -> list:
    """The option checks every inquiry form owes WHEREVER it carries the control, whatever its page's
    field contract: a handover choice that offers something that does not exist, or a puppy option
    that is no puppy and no named choice, is a false promise on any page (the uk-locations cluster
    included, which the field contract skips)."""
    problems = []
    handover = [c for c in ctl if c["name"] == "handover"]
    if handover:
        values = [c.get("value") or "" for c in handover if c["tag"] == "input"]
        values += [o for c in handover if c["tag"] == "select" for o in c["options"] if o]
        for v in values:
            if v not in HANDOVER_VALUES:
                problems.append(f'handover offers "{v}"; the only two are {" and ".join(HANDOVER_VALUES)}')
        for v in HANDOVER_VALUES:
            if v not in values:
                problems.append(f"handover lacks {v}")
    allowed = puppy_values()
    for c in ctl:
        if c["name"] == "puppy" and c["tag"] == "select":
            for o in c["options"]:
                if o and o not in allowed:
                    problems.append(f'puppy select offers "{o}", which is no puppy in data/puppies.json '
                                    f'and none of {", ".join(PUPPY_CHOICES)}')
    return problems


_SKIPPED = ("template", "noscript")


class _Forms(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms, self._cur = [], None
        self._cursel = None
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in _SKIPPED:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        a = dict(attrs)
        if tag == "form":
            if self._cur is not None:
                return  # nested <form> start tag ignored, like a browser's parser
            self._cur = {"attrs": a, "controls": []}
            self.forms.append(self._cur)
        elif tag in ("input", "select", "textarea") and self._cur is not None:
            type_ = a.get("type") or ("text" if tag == "input" else tag)
            ctl = {"tag": tag, "name": a.get("name"), "type": type_.lower(),
                   "required": "required" in a, "options": [], "value": a.get("value")}
            self._cur["controls"].append(ctl)
            self._cursel = ctl if tag == "select" else None
        elif tag == "option" and self._cursel is not None:
            self._cursel["options"].append(a.get("value", ""))

    def handle_endtag(self, tag):
        if tag in _SKIPPED:
            if self._skip_depth:
                self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag == "select":
            self._cursel = None
        if tag == "form":
            self._cur = self._cursel = None


def audit_html(html: str, slug: str):
    endpoint = _endpoint()
    p = _Forms(); p.feed(html); p.close()
    rows = []
    for n, f in enumerate(p.forms, 1):
        a, ctl = f["attrs"], f["controls"]
        action = a.get("action", "") or ""
        if action.startswith("/search"):
            continue
        # Conservative: a form is "newsletter" only when its real (non-hidden,
        # non-honeypot) controls are exactly one email input. Everything else —
        # including an inquiry form with no <textarea> — is "inquiry".
        real = [c for c in ctl if c["type"] != "hidden" and c["name"] != "_gotcha"]
        kind = "newsletter" if len(real) == 1 and real[0]["type"] == "email" else "inquiry"
        problems = []
        if action != endpoint:
            problems.append(f'endpoint is "{action or "(none)"}", must be {endpoint}')
        if "data-netlify" in a or "netlify-honeypot" in a or any(c["name"] in ("form-name", "bot-field") for c in ctl):
            problems.append("netlify residue (data-netlify / form-name / bot-field)")
        if (a.get("method") or "get").lower() != "post":
            problems.append(f'method is {a.get("method") or "GET"}, must be POST')
        if kind == "newsletter" and any(c["type"] == "email" and not c["name"] for c in ctl):
            problems.append("email input has no name attribute — Formspree receives nothing")
        if kind == "inquiry":
            problems += value_problems(ctl)
        if kind == "inquiry" and field_checks_apply(slug):
            for key, rx in contract_keys(slug):
                hits = [c for c in ctl if c["name"] and rx.match(c["name"])]
                if not hits:
                    problems.append(f"{key} absent")
                elif key in REQUIRED and not any(c["required"] for c in hits):
                    problems.append(f"{key} not required")
                if key == "puppy" and hits:
                    sels = [c for c in hits if c["tag"] == "select"]
                    if not sels:
                        problems.append("puppy must be a <select> (spec §5)")
                    elif not any(PUPPY_OPTION in c["options"] for c in sels):
                        problems.append(
                            f"puppy select missing the {PUPPY_OPTION} option (spec §5)")
            # Without _next and _subject Formspree has no redirect and no reply subject.
            for h in HIDDEN:
                if not any(c["name"] == h for c in ctl):
                    problems.append(f"hidden field {h} absent")
        rows.append({"slug": slug, "n": n, "name": a.get("name") or (a.get("class") or "").split(" ")[0] or "form",
                     "kind": kind, "action": action, "fields": sorted({c["name"] for c in ctl if c["name"]}),
                     "in_scope": kind == "inquiry" and field_checks_apply(slug), "problems": problems})
    return rows


def audit_dist(dist: Path) -> list:
    rows = []
    for path in sorted(dist.rglob("index.html")):
        rows += audit_html(path.read_text(encoding="utf-8"), page_key(path, dist))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--dist", default=str(DIST), help="dist root to audit")
    ap.add_argument("--fail-on-error", action="store_true",
                    help="accepted for symmetry with the other gates; a contract "
                         "failure is always fatal here")
    ap.add_argument("--json", nargs="?", const=str(DEFAULT_JSON), default=None,
                    metavar="PATH",
                    help=f"write the machine-readable result (default {DEFAULT_JSON})")
    args = ap.parse_args(sys.argv[1:] if argv is None else argv)
    _endpoint()          # fail fast: refuse before reading a single page
    dist = Path(args.dist)
    rows = audit_dist(dist)
    if not rows:
        print("FAIL: no forms examined — is dist/ built?")
        sys.exit(2)
    bad = [r for r in rows if r["problems"]]
    inquiry = [r for r in rows if r["kind"] == "inquiry"]
    for r in bad:
        print(f"FAIL {r['slug']} form#{r['n']} [{r['name']}] {r['action'] or '(no action)'}")
        for p in r["problems"]:
            print(f"     - {p}")
    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
        print(f"JSON report → {out}")
    print(f"examined {len(rows)} forms; {len(bad)} problems  "
          f"(inquiry {len(inquiry)}, in-scope {sum(r['in_scope'] for r in rows)}, "
          f"newsletter {len(rows) - len(inquiry)})")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
