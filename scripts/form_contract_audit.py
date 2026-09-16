#!/usr/bin/env python3
"""Form contract audit over dist/.

Every non-search <form> must POST to the one Formspree endpoint with no Netlify residue.
A form is classed "newsletter" only when its non-hidden, non-_gotcha controls are
exactly one type="email" input; every other form (including one with no textarea) is
classed "inquiry" and must carry its page's contract:
  full  — the six named controls of the built inquiry form (every in-scope page,
          the contact page included)
  short — blog/* posts: name, email, message
  none  — the uk-locations/* cluster and the hubs (no inquiry forms today).

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
import argparse, json, os, re, sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _slugs import page_key  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DEFAULT_JSON = ROOT / "docs/reports/form_contract_audit.json"

# Read from the environment, never hard-coded. The id is a credential-adjacent fact that
# lives in .env (spec §8); a literal here would be a second source of truth that goes
# stale the day the form moves, and would put a real endpoint in a committed file.
_FID = os.environ.get("PUBLIC_FORMSPREE_ID", "")
if not _FID:
    # Exit 2 = the gate cannot run, the code board_gate.py and evidence_audit.py use.
    # Exit 1 would read as "ran, found one problem".
    print("REFUSED: PUBLIC_FORMSPREE_ID is unset — a form audit that matches nothing "
          "would report every form clean. Set it in .env (see .env.example).",
          file=sys.stderr)
    sys.exit(2)
ENDPOINT = f"https://formspree.io/f/{_FID}"

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
# Spec §5: the puppy control is a <select>, and one of its options is the Glasgow
# collection choice (value read off the built page, 2026-09-16).
PUPPY_OPTION = "collection-glasgow"
SHORT = ("name", "email", "message")
LOCATION = re.compile(r"^uk-locations/")
HUBS = ("available-puppies", "uk-locations", "blog")


def contract_keys(slug: str) -> list:
    """The (name, regex) pairs this page's inquiry forms must carry."""
    if LOCATION.match(slug) or slug in HUBS:
        return []
    if slug.startswith("blog/"):
        return [k for k in KEYS if k[0] in SHORT]
    return KEYS


def field_checks_apply(slug: str) -> bool:
    return bool(contract_keys(slug))


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
                   "required": "required" in a, "options": []}
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
        if action != ENDPOINT:
            problems.append(f'endpoint is "{action or "(none)"}", must be {ENDPOINT}')
        if "data-netlify" in a or "netlify-honeypot" in a or any(c["name"] in ("form-name", "bot-field") for c in ctl):
            problems.append("netlify residue (data-netlify / form-name / bot-field)")
        if (a.get("method") or "get").lower() != "post":
            problems.append(f'method is {a.get("method") or "GET"}, must be POST')
        if kind == "newsletter" and any(c["type"] == "email" and not c["name"] for c in ctl):
            problems.append("email input has no name attribute — Formspree receives nothing")
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
