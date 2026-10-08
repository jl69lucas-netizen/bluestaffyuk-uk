#!/usr/bin/env python3
"""The calls to action on a page board (working rule 12, CTAs included: the breeder's ruling of
2026-10-08, "add CTAs to the board going forward so I can choose the buttons, on all remaining
pages"). The bsuk-cta skill is the method; this module is the record, the board block, the
approval check and the gate.

THE RECORD. A board record carries a top-level `ctas` list, one SLOT per call to action the
page will paint:

    {"slot": "hero", "section": "top", "type": "ask", "target": "#enquiry", "why": "...",
     "options": [{"id": "a", "text": "...", "style": "down"}, {"id": "b", ...}, {"id": "c", ...}]}

`type` is browse / ask / ask-about-pup / submit / tool (data/design/cta-plan.json `types`).
Each slot offers exactly three options, each a button text in one catalog style
(src/styles/cta.css; `sub` and `tag` carry their second line or tag). The options are content
the breeder approves, so they are inside `record_hash`.

THE PICK. The board writes one radio group per slot, `pick-cta:<slot>`; the approve button
collects every `pick-*` radio into `approval.picks`, so the answer lands as
picks["cta:<slot>"] = "a" | "b" | "c", outside the hash, exactly as an `img:<slot>` pick does
(scripts/image_rules.py). board_approve.py refuses an approval that leaves a slot unpicked,
picks two near-identical texts, or picks one style twice.

THE PAGE. src/lib/ctas.ts reads the picked option and src/components/kit/CtaButton.astro paints
it, so a button's words and style come off the board, never typed into the page.

THE RENDER CHECKS. tests/render/checks/cta.ts judges the built page with the same two rules
(near-identical text from data/design/cta-plan.json `near_identical`; one style per CTA) and
the same bands, so a board that passes here builds a page that passes there.

Usage:
    python3 scripts/cta_rules.py <slug>              print the board's CTA findings
    python3 scripts/cta_rules.py <slug> --propose    print a proposed `ctas` block (JSON)
    python3 scripts/cta_rules.py <slug> --propose --write
                                                     write it into the record (not approved yet)
    python3 scripts/cta_rules.py --catalog docs/artifacts/bsuk-cta-styles.html
                                                     the style catalog preview (working rule 10)
"""
import argparse
import html as _html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAN_FILE = ROOT / "data" / "design" / "cta-plan.json"
CSS_FILE = ROOT / "src" / "styles" / "cta.css"
TOKENS_FILE = ROOT / "src" / "styles" / "tokens.css"

PICK_PREFIX = "cta:"
#: Where an `ask` goes on a page with no enquiry form of its own.
CONTACT_PAGE = "/uk-blue-staffy-breeders-contact/"
#: The catalog, in src/styles/cta.css and CtaButton.astro's CTA_STYLES order. An id is never
#: renamed or reused: a pick stores it.
STYLES = ("solid", "arrow", "down", "chip", "sub", "tag", "caps", "wide")
#: `caps` sits at the end of a rule line, which a form's own button cannot.
SUBMIT_STYLES = tuple(s for s in STYLES if s != "caps")
TYPES = ("browse", "ask", "ask-about-pup", "submit", "tool")
#: The types that count toward the page's body band (a repeated `ask-about-pup` set is one slot).
BODY_TYPES = ("browse", "ask", "ask-about-pup")
OPTION_IDS = ("a", "b", "c")
MIN_WORDS, MAX_WORDS = 2, 8

#: The two project 5 boards approved before CTAs reached the board. Their CTAs were chosen with
#: the page copy; the render checks still report on their built pages.
BUILT_BEFORE_CTA_RULE = frozenset({"blue-staffy-puppies-london", "blue-staffy-puppies-manchester-uk"})


def plan():
    return json.loads(PLAN_FILE.read_text(encoding="utf-8"))


def content_words(text, stop=None):
    """The words that carry a button's meaning: lower-cased, stop words dropped, each once.
    tests/render/checks/cta.ts contentWords() is the same function."""
    stop = set(plan()["near_identical"]["stop_words"]) if stop is None else stop
    seen = []
    for w in re.findall(r"[a-z0-9']+", text.lower()):
        if w not in stop and w not in seen:
            seen.append(w)
    return seen


def near_identical(a, b, p=None):
    """Two button texts that say the same thing: the same content words, or a Jaccard overlap
    at or over the plan's threshold. "Ask about a puppy" and "Ask us about a puppy" are one
    button twice."""
    p = plan() if p is None else p
    stop = set(p["near_identical"]["stop_words"])
    x, y = set(content_words(a, stop)), set(content_words(b, stop))
    if not x or not y:
        return a.strip().lower() == b.strip().lower()
    return len(x & y) / len(x | y) >= p["near_identical"]["jaccard"]


def slots(board):
    return board.get("ctas") or []


def applies(board):
    """The CTA rule binds the pages family_rules binds, boarded from 2026-10-08 on."""
    import family_rules as FR
    return FR.applies(board) and board["meta"]["slug"] not in BUILT_BEFORE_CTA_RULE


def slots_needing_pick(board):
    """The `cta:<slot>` radio groups the approve button refuses to leave empty."""
    return [PICK_PREFIX + s["slot"] for s in slots(board)] if applies(board) else []


def _section_order(board):
    return {s["id"]: i for i, s in enumerate(board["sections"])}


# ── the record's own rules (before any pick) ─────────────────────────────────────────────
def slot_problems(board):
    """[(check id, message)] for the `ctas` block as recorded: the shape of every slot and its
    three options, the page's count against its band, and two body CTAs in neighbouring
    sections."""
    p = plan()
    out = []
    order = _section_order(board)
    seen_slots = set()
    for s in slots(board):
        where = f"CTA slot {s.get('slot')!r}"
        if s.get("slot") in seen_slots:
            out.append(("cta-slot-invalid", f"{where} is recorded twice"))
        seen_slots.add(s.get("slot"))
        if s.get("section") not in order:
            out.append(("cta-slot-invalid", f"{where}: section {s.get('section')!r} is not a section of this record"))
        if s.get("type") not in TYPES:
            out.append(("cta-slot-invalid", f"{where}: type {s.get('type')!r} is not one of {', '.join(TYPES)}"))
        target = s.get("target")
        if s.get("type") == "submit":
            if target:
                out.append(("cta-slot-invalid", f"{where}: a submit sends its form and names no target"))
        elif not target:
            out.append(("cta-slot-invalid", f"{where}: no target"))
        elif target.startswith("#") and target[1:] not in order:
            out.append(("cta-slot-invalid", f"{where}: {target} names no section id of this record"))
        elif not target.startswith(("#", "/")):
            out.append(("cta-slot-invalid", f"{where}: {target} is neither a section of this page nor a page of this site"))
        if not (s.get("why") or "").strip():
            out.append(("cta-slot-invalid", f"{where}: no `why` (what this button does for the reader here)"))
        opts = s.get("options") or []
        if [o.get("id") for o in opts] != list(OPTION_IDS):
            out.append(("cta-slot-invalid", f"{where}: offers {len(opts)} option(s); a slot offers exactly three, ids a, b, c"))
        allowed = SUBMIT_STYLES if s.get("type") == "submit" else STYLES
        for o in opts:
            text, style = (o.get("text") or "").strip(), o.get("style")
            n = len(text.split())
            if not MIN_WORDS <= n <= MAX_WORDS:
                out.append(("cta-slot-invalid", f"{where} option {o.get('id')}: \"{text}\" is {n} word(s); a button says {MIN_WORDS}-{MAX_WORDS}"))
            if re.search(r"[£$€\d]", text):
                out.append(("cta-slot-invalid", f"{where} option {o.get('id')}: \"{text}\" types a figure; prices, the deposit, "
                            "the band and the guarantee come from data/ beside the button, never in it (working rule 9)"))
            if style not in allowed:
                out.append(("cta-slot-invalid", f"{where} option {o.get('id')}: style {style!r} is not one of {', '.join(allowed)}"))
            if style == "sub" and not (o.get("sub") or "").strip():
                out.append(("cta-slot-invalid", f"{where} option {o.get('id')}: style sub needs its second line (`sub`)"))
            if style == "tag" and not (o.get("tag") or "").strip():
                out.append(("cta-slot-invalid", f"{where} option {o.get('id')}: style tag needs its tag (`tag`)"))
        for i, a in enumerate(opts):
            for b in opts[i + 1:]:
                if near_identical(a.get("text", ""), b.get("text", ""), p):
                    out.append(("cta-slot-invalid", f"{where}: options {a.get('id')} and {b.get('id')} say the same thing "
                                f"(\"{a.get('text')}\" / \"{b.get('text')}\"); offer three different buttons"))
                if a.get("style") == b.get("style"):
                    out.append(("cta-slot-invalid", f"{where}: options {a.get('id')} and {b.get('id')} share style {a.get('style')}"))
    body = [s for s in slots(board) if s.get("type") in BODY_TYPES]
    band = p["bands"].get(board["meta"]["page_type"])
    if band and not band["min"] <= len(body) <= band["max"]:
        out.append(("cta-count-out-of-band", f"{len(body)} body CTA slot(s); the {board['meta']['page_type']} band is "
                    f"{band['min']}-{band['max']} (data/design/cta-plan.json)"))
    placed = sorted((order[s["section"]], s) for s in body if s.get("section") in order)
    for (i, a), (j, b) in zip(placed, placed[1:]):
        if j - i <= 1:
            out.append(("cta-count-out-of-band", f"CTA slots {a['slot']!r} and {b['slot']!r} sit in neighbouring sections "
                        f"({a['section']}, {b['section']}); leave a section between two buttons"))
    return out


# ── the picks ───────────────────────────────────────────────────────────────────────────
def validate_cta_picks(board, picks):
    """Why the `cta:` picks in `picks` cannot be approved, as printable lines (empty = fine):
    a pick naming no slot or no option, a slot left unpicked, two picked texts that say the same
    thing, or one style picked twice (all link CTAs share the pill, all submits the form shape,
    so a style is judged within each)."""
    errs = []
    by_slot = {s["slot"]: s for s in slots(board)}
    for pid, val in picks.items():
        if not pid.startswith(PICK_PREFIX):
            continue
        slot = pid[len(PICK_PREFIX):]
        if slot not in by_slot:
            errs.append(f"{pid}: no CTA slot {slot!r} in the record")
        elif val not in OPTION_IDS:
            errs.append(f"{pid}: {val!r} is not one of a, b, c")
    if not applies(board):
        return errs
    chosen = []
    for s in slots(board):
        val = picks.get(PICK_PREFIX + s["slot"])
        if val is None:
            errs.append(f"CTA slot {s['slot']!r} has no pick")
            continue
        opt = next((o for o in s.get("options", []) if o.get("id") == val), None)
        if opt:
            chosen.append((s, opt))
    p = plan()
    for i, (sa, a) in enumerate(chosen):
        for sb, b in chosen[i + 1:]:
            if near_identical(a["text"], b["text"], p):
                errs.append(f"CTA slots {sa['slot']!r} and {sb['slot']!r} pick near-identical buttons "
                            f"(\"{a['text']}\" / \"{b['text']}\"); pick a different option for one of them")
            same_shape = (sa["type"] == "submit") == (sb["type"] == "submit")
            if same_shape and a["style"] == b["style"]:
                errs.append(f"CTA slots {sa['slot']!r} and {sb['slot']!r} both pick style {a['style']}; "
                            "every CTA on a page gets its own style")
    return errs


def findings(board):
    """family_rules' (check id, severity, message) triples. No `ctas` block is a FAIL from
    `boarded` on (WARN on a draft, which is written before the outline places anything); a
    record's own slot problems are FAILs; an approved record's picks are re-judged."""
    if not applies(board):
        return []
    status = board["meta"]["status"]
    if not slots(board):
        sev = "WARN" if status == "draft" else "FAIL"
        return [("cta-board-missing", sev, "the board lists no CTA slots: every call to action the page will "
                 "carry is on the board for the breeder to pick (working rule 12; "
                 f"`python3 scripts/cta_rules.py {board['meta']['slug']} --propose --write`)")]
    out = [(c, "FAIL", m) for c, m in slot_problems(board)]
    if board.get("approval"):
        out += [("cta-picks-invalid", "FAIL", m)
                for m in validate_cta_picks(board, (board["approval"] or {}).get("picks", {}))]
    return out


# ── a proposal, for the agent to edit ─────────────────────────────────────────────────────
#: Option texts per role: first person, verb first, no figure. The agent rewrites them to fit
#: the page; they are a starting point, chosen so the first options of different roles are
#: never near-identical to each other.
BANK = {
    "hero-ask": ("Start with a question about a puppy", "Tell us what you are looking for", "Ask us anything before you choose"),
    "hero-browse": ("See the puppies available now", "Browse this litter's puppies", "Meet the puppies looking for homes"),
    "litter": ("Ask which puppy suits your home", "Tell us which puppy caught your eye", "Ask about one of this litter"),
    "deposit": ("Ask us to book your visit", "Ask how reserving works", "Tell us when you could visit"),
    "terms": ("Ask us for the full terms", "Ask to read the contract first", "Ask what the guarantee covers"),
    "home": ("Tell us about your household", "Ask if a Staffy suits your days", "Describe your home to us"),
    "enquiry": ("Send my enquiry", "Send my questions to Lisa", "Post my enquiry to you"),
    "newsletter": ("Send me the litter note", "Keep me posted on litters", "Add me to the litter note"),
}
ROLE_MATCH = (
    ("litter", r"litter|price"),
    ("deposit", r"deposit|viewing|visit|reserve"),
    ("terms", r"papers?|paperwork|guarantee|terms|contract|certificat"),
    ("home", r"life|temperament|household|busy|family|home"),
)
#: Section shapes that never carry a body CTA (bsuk-cta §2): proof, answers and navigation.
NO_CTA_SHAPES = ("faq", "reviews", "trust", "form", "stats", "dial", "takeaways")

#: `sub` and `tag` need a second line and a tag that are true everywhere; both are read from
#: data/settings.json at proposal time, never invented.
def _sub_and_tag():
    s = json.loads((ROOT / "data" / "settings.json").read_text(encoding="utf-8"))
    town = (s.get("address") or {}).get("city") or "Carlisle"
    return f"Collection in {town} or UK delivery", town


def propose(board):
    """A `ctas` block for the record: the hero, one slot per matched body section with a
    section left between buttons, and each form's submit. Styles rotate through the catalog so
    every slot's option (a) has a different style. The agent edits the texts to the page."""
    order = [s for s in board["sections"]]
    ids = {s["id"] for s in order}
    # An `ask` goes to this page's own form; a page with none sends it to the contact page,
    # never to the litter (that is a `browse`, and it says see or browse, not ask).
    target = "#enquiry" if "enquiry" in ids else next((f"#{s['id']}" for s in order if s.get("shape") == "form"),
                                                      CONTACT_PAGE)
    transactional = board["meta"]["page_type"] not in ("location", "comparison", "blog")
    plans, last = [], -2
    for i, s in enumerate(order):
        sid, text = s["id"], f"{s['id']} {s.get('heading', '')}".lower()
        if i == 0 or s.get("shape") == "hero" or sid == "top":
            plans.append((s, "hero-browse" if transactional else "hero-ask", "browse" if transactional else "ask"))
            last = i
            continue
        if sid in ("enquiry", "newsletter"):
            plans.append((s, sid, "submit"))
            continue
        if s.get("shape") in NO_CTA_SHAPES or i - last <= 1:
            continue
        role = next((r for r, rx in ROLE_MATCH if re.search(rx, text)), None)
        if role and role not in {p[1] for p in plans}:
            plans.append((s, role, "ask"))
            last = i
    sub, tag = _sub_and_tag()
    out, k = [], 0
    for s, role, typ in plans:
        allowed = SUBMIT_STYLES if typ == "submit" else STYLES
        opts = []
        for j, oid in enumerate(OPTION_IDS):
            style = allowed[(3 * k + j) % len(allowed)]
            o = {"id": oid, "text": BANK[role][j], "style": style}
            if style == "sub":
                o["sub"] = sub
            if style == "tag":
                o["tag"] = tag
            opts.append(o)
        k += 1
        slot = {"slot": "hero" if role.startswith("hero") else s["id"], "section": s["id"], "type": typ,
                "why": f"proposed for the {role.replace('hero-', 'hero, ')} role; edit to fit the section",
                "options": opts}
        if typ != "submit":
            slot["target"] = "/available-puppies/" if typ == "browse" else target
        out.append(slot)
    return out


# ── board block 7e ────────────────────────────────────────────────────────────────────────
def _token_css():
    """The tokens cta.css reads, resolved to values: the board is a standalone Artifact with
    its own palette, so the buttons carry the site's own colours and radii inline."""
    text = TOKENS_FILE.read_text(encoding="utf-8")
    decl = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", text))

    def resolve(v, depth=0):
        return re.sub(r"var\((--[\w-]+)\)", lambda m: resolve(decl.get(m.group(1), m.group(0)), depth + 1)
                      if depth < 8 else m.group(0), v.strip())
    names = sorted(set(re.findall(r"var\((--[\w-]+)\)", CSS_FILE.read_text(encoding="utf-8"))))
    return ".ctapick{" + "".join(f"{n}:{resolve(decl[n])};" for n in names if n in decl) + "}"


BLOCK_CSS = (".ctapick{border:1px solid var(--line);border-radius:8px;padding:10px 12px 12px;margin:10px 0;min-width:0}"
             ".ctapick legend{font-size:13px;font-weight:600;padding:0 6px}"
             ".ctac{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;margin:6px 0}"
             ".ctaopt{display:grid;gap:8px;justify-items:start;border:1px solid var(--line);border-radius:6px;padding:10px;font-size:12px;cursor:pointer}"
             ".ctaopt:has(input:checked){outline:3px solid var(--clay);outline-offset:1px}"
             ".ctaopt .cta-rule{width:100%;margin:0}.ctaopt .cta[data-cta-style=wide]{width:100%}"
             ".ctawhy{font-size:12px;color:var(--ink-3);margin:2px 0 4px}.ctacount{font-weight:600}")


def _button(o, submit):
    e = _html.escape
    style = o["style"]
    inner = e(o["text"])
    if style == "chip":
        inner = ('<span class="chip" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
                 'stroke="currentColor" stroke-width="2.2"><rect x="3" y="5" width="18" height="14" rx="2"/>'
                 '<path d="m3 7 9 6 9-6"/></svg></span>' + inner)
    elif style == "sub":
        inner = f"<span>{inner}</span><small>{e(o.get('sub', ''))}</small>"
    elif style == "tag":
        inner = f"<span>{inner}</span><span class=\"tag\">{e(o.get('tag', ''))}</span>"
    attrs = ' data-submit=""' if submit else ""
    btn = f'<span class="cta" data-cta-style="{e(style)}"{attrs}>{inner}</span>'
    return f'<span class="cta-rule">{btn}</span>' if style == "caps" else btn


def board_block(board):
    """Block 7e, "Calls to action": the page's count against its band, then one radio group per
    slot showing each option painted in its own style. Empty for a page the rule does not bind."""
    if not applies(board):
        return ""
    e = _html.escape
    p = plan()
    body = [s for s in slots(board) if s.get("type") in BODY_TYPES]
    band = p["bands"].get(board["meta"]["page_type"])
    head = (f'<p class="ctacount">{len(body)} body CTA(s) · band {band["min"]}–{band["max"]} for '
            f'{e(board["meta"]["page_type"])} · plus {len(slots(board)) - len(body)} form or tool button(s)</p>'
            if band else "")
    rows = []
    heading = {s["id"]: f"{s['n']:02d} · {s['heading']}" for s in board["sections"]}
    for s in slots(board):
        opts = "".join(
            f'<label class="ctaopt"><input type="radio" name="pick-cta:{e(s["slot"])}" value="{e(o["id"])}"> '
            f'<b>{e(o["id"])}</b> · {e(o["style"])}{_button(o, s["type"] == "submit")}</label>'
            for o in s.get("options", []))
        to = f' → <code>{e(s["target"])}</code>' if s.get("target") else ""
        rows.append(f'<fieldset class="ctapick" id="cta-{e(s["slot"])}"><legend>{e(heading.get(s["section"], s["section"]))}'
                    f' · {e(s["type"])}{to}</legend><p class="ctawhy">{e(s.get("why", ""))}</p>'
                    f'<div class="ctac">{opts}</div></fieldset>')
    css = CSS_FILE.read_text(encoding="utf-8")
    return (f"<style>{BLOCK_CSS}{_token_css()}{css}</style>{head}"
            + ("".join(rows) or '<p class="lk-none">No CTA slots recorded.</p>'))


# ── the catalog preview (working rule 10: a style is seen in the browser before it is offered) ─
CATALOG_SAMPLES = (
    ("solid", "Send my enquiry", False, "The signature pill. The one plain button on a page, often the enquiry form's."),
    ("arrow", "See the puppies available now", False, "Goes somewhere else on the site: the litter, a puppy's page. The arrow steps forward on hover."),
    ("down", "Ask which puppy suits your home", False, "Jumps down to the enquiry form on this page."),
    ("chip", "Send my questions to Lisa", True, "Writing to us: an envelope chip before the words. Shown here as a form submit."),
    ("sub", "Ask us to book your visit", False, "Two lines: the button, then one fact read from data/settings.json, never invented."),
    ("tag", "Tell us when you could visit", False, "The button, a dashed seam and a short tag read from data/settings.json."),
    ("caps", "Ask us for the full terms", False, "Small capitals at the end of a brass rule: a quiet sign-off to a long section."),
    ("wide", "Tell us about your household", False, "The full width of its column: the end of a card or a narrow section."),
)


def catalog_html(demo=None):
    """A standalone page: every catalog style painted from src/styles/cta.css with the site's
    tokens, then board block 7e for `demo` (a record with `ctas`), if given."""
    e = _html.escape
    sub, tag = _sub_and_tag()
    assert [c[0] for c in CATALOG_SAMPLES] == list(STYLES), "a catalog style has no preview sample"
    cards = "".join(
        f'<article class="card"><header><b>{st}</b><span>{"form submit" if submit else "link"}</span></header>'
        f'<div class="stage">{_button({"id": "a", "text": text, "style": st, "sub": sub, "tag": tag}, submit)}</div>'
        f"<p>{e(why)}</p></article>"
        for st, text, submit, why in CATALOG_SAMPLES)
    board = ""
    if demo is not None:
        board = ('<section class="board"><h2>How it will look on a page board (block 7e)</h2>'
                 '<p class="lede">A sample location board with the proposal the tool writes before the button words '
                 "are edited to the page. You pick one option per button. The board won't approve while a button is "
                 "unpicked, two picks say the same thing, or two picks share a style.</p>" + board_block(demo) + "</section>")
    return f"""<title>BSUK CTA Styles</title>
<style>
:root{{--bg:#F3EFE6;--card:#FFFFFF;--ink:#1B2430;--muted:#556171;--line:#D9D2C3;--paper:#FFFFFF;--clay:#22384F;--ink-2:#33404F;--ink-3:#5B6676;--code-bg:#EEE9DD}}
body{{background:var(--bg);color:var(--ink);font:16px/1.55 "Source Sans 3",system-ui,sans-serif}}
.wrap{{max-width:1120px;margin:0 auto;padding-inline:16px;padding-block:32px 64px;display:grid;gap:28px}}
h1,h2{{font-family:"Fraunces",Georgia,serif;color:#22384F;margin:0;text-wrap:balance}} h1{{font-size:clamp(26px,4vw,36px)}} h2{{font-size:22px}}
.lede{{color:var(--muted);max-width:68ch;margin:6px 0 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;display:grid;gap:12px;min-width:0}}
.card header{{display:flex;justify-content:space-between;font-size:14px}} .card header span{{color:var(--muted)}}
.stage{{min-height:72px;display:grid;align-items:center;justify-items:start}} .stage .cta-rule,.stage .cta[data-cta-style=wide]{{width:100%;margin:0}}
.card p{{margin:0;font-size:14px;color:var(--muted)}}
section.board{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;display:grid;gap:8px;min-width:0}}
code{{background:var(--code-bg);padding:1px 4px;border-radius:4px}}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700&family=Source+Sans+3:wght@400;600;700&display=swap">
<style>{_token_css().replace(".ctapick{", ":root{", 1)}{CSS_FILE.read_text(encoding="utf-8")}</style>
<div class="wrap">
<header><h1>CTA styles for BlueStaffyUK pages</h1>
<p class="lede">Eight button styles, painted from the site's own CSS (src/styles/cta.css) in the site's gold, ink and pill shape, which never change. No two buttons on a page may share a style or say the same thing. From now on each page board offers three options per button, and you pick one.</p></header>
<div class="grid">{cards}</div>
{board}
</div>"""


def main(argv=None):
    sys.path.insert(0, str(ROOT / "scripts"))
    import pageboard as PB
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--propose", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--catalog", metavar="OUT", help="write the style catalog preview page (with a sample board block)")
    a = ap.parse_args(argv)
    if a.catalog:
        import copy
        demo = copy.deepcopy(json.loads((ROOT / "data" / "boards" / "_demo.json").read_text(encoding="utf-8")))
        demo["meta"].update({"slug": "uk-locations/blue-staffy-puppies-leeds", "page_type": "location", "status": "boarded"})
        demo["ctas"] = propose(demo)
        pathlib.Path(a.catalog).write_text(catalog_html(demo), encoding="utf-8")
        print(f"wrote {a.catalog}")
        return 0
    if not a.slug:
        ap.error("a slug is needed unless --catalog is given")
    board = PB.load_board(a.slug)
    if a.propose:
        block = propose(board)
        if a.write:
            if board.get("approval"):
                print("REFUSED: the record is approved; a new CTA block re-opens the board", file=sys.stderr)
                return 2
            board["ctas"] = block
            PB.save_board(a.slug, board)
            print(f"wrote {len(block)} CTA slot(s) into the record")
        else:
            print(json.dumps(block, indent=2, ensure_ascii=False))
        return 0
    found = findings(board)
    for c, sev, m in found:
        print(f"{sev} {c}: {m}")
    print(f"examined {len(slots(board))} CTA slot(s); {sum(1 for f in found if f[1] == 'FAIL')} FAIL")
    return 1 if any(f[1] == "FAIL" for f in found) else 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts"))
    raise SystemExit(main())
