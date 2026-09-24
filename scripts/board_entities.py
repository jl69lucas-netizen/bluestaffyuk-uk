#!/usr/bin/env python3
"""board_entities — the page board's keyword and entity views (blocks 4 and 5).

Two pure grouping functions and the HTML, CSS and JS that render them. It lives apart from
build_page_board.py so the board builder only CALLS it: the grouping is testable without
rendering a whole board, and a later change to the view is an edit here, not in the shared
builder.

  group_entities(board, ont) -> [{"class", "entities": [card], "columns": [section]}]
      One card per entity the board names, grouped under CLASS_ORDER, each carrying the
      sections it appears in. An id the ontology does not know is class "Unknown" with
      authorization "UNKNOWN" — shown, never dropped, because the gate warns on it.
  group_keywords(board) -> [{"type", "label", "optional", "terms": [{"term", "sections"}]}]
      One group per keyword type in pageboard.ALL_KEYWORD_TYPES order; a term written in
      two sections is one chip carrying both. Case and spacing do not make a new term.

Why no graph. The cytoscape map this replaces labelled every node with a section heading
and drew every section-to-entity edge; at fifteen sections that is a hairball, and the
entity names were the smallest text on it. Everything it said — which entity, which class,
which sections, which authorization — is on a card here, legibly, at any width, and the
matrix answers "what does section 04 name" without a layout engine or a 400 KB CDN script.
"""
import html as H
import sys
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pageboard as PB  # noqa: E402

CLASS_ORDER = ("People", "Place", "Health", "Organization", "Regulation", "Organism",
               "Commerce", "Logistics", "Documentation", "Method", "Unknown")
AUTH_ORDER = ("BLOCKED", "UNKNOWN", "PROPOSED", "ASSERTED")


def _ref(s):
    return {"id": s["id"], "n": s["n"], "heading": s["heading"]}


def group_entities(board, ont):
    by_id = {e["id"]: e for e in ont.get("entities", [])}
    used = OrderedDict()
    for s in board["sections"]:
        for eid in s["entities"]:
            refs = used.setdefault(eid, [])
            if not any(r["id"] == s["id"] for r in refs):
                refs.append(_ref(s))
    groups = OrderedDict((c, []) for c in CLASS_ORDER)
    for eid, refs in used.items():
        e = by_id.get(eid)
        if e is None:
            card = {"id": eid, "name": eid.split(":", 1)[-1].replace("-", " "), "aliases": [],
                    "class": "Unknown", "authorization": "UNKNOWN", "source": None, "owner_page": None}
        else:
            card = {k: e.get(k) for k in ("id", "name", "aliases", "class", "authorization", "source", "owner_page")}
            if card["class"] not in groups:
                card["class"] = "Unknown"
        card["aliases"] = list(card["aliases"] or [])
        card["sections"] = refs
        groups[card["class"]].append(card)
    out = []
    for cls, cards in groups.items():
        if not cards:
            continue
        # Most-used first, so the entity a page leans on is the first card in its class;
        # a BLOCKED or UNKNOWN one jumps the queue because it is the one the board must fix.
        cards.sort(key=lambda c: (AUTH_ORDER.index(c["authorization"]) if c["authorization"] in AUTH_ORDER[:2] else 9,
                                  -len(c["sections"]), c["name"].lower()))
        cols = {r["id"]: r for c in cards for r in c["sections"]}
        out.append({"class": cls, "entities": cards, "columns": sorted(cols.values(), key=lambda r: r["n"])})
    return out


def group_keywords(board):
    out = []
    for k in PB.ALL_KEYWORD_TYPES:
        terms = OrderedDict()
        for s in board["sections"]:
            for term in s["keywords"].get(k, []):
                key = " ".join(str(term).lower().split())
                if not key:
                    continue
                t = terms.setdefault(key, {"term": term, "sections": []})
                if not any(r["id"] == s["id"] for r in t["sections"]):
                    t["sections"].append(_ref(s))
        out.append({"type": k, "label": PB.KEYWORD_LABELS[k], "optional": k in PB.OPTIONAL_KEYWORD_TYPES,
                    "terms": list(terms.values())})
    return out


# ── rendering ────────────────────────────────────────────────────────────────────────────
#
# Every string below is HTML, emitted as ONE line with no blank line in it: the board mounts
# each block through marked, and marked ends a raw HTML block at the first blank line — a
# blank line inside a card would turn the rest of the view into escaped markdown.

def esc(v):
    return H.escape("" if v is None else str(v), quote=True)


def anchor_id(section_id):
    """The id block 3's outline puts on each H2 line; the section chips link to it."""
    return f"outline-{section_id}"


def _cls_key(cls):
    return cls.lower()


def sec_chips(refs):
    return "".join(
        f'<a class="sec-chip" href="#{esc(anchor_id(r["id"]))}" title="{r["n"]:02d} · {esc(r["heading"])}">{r["n"]:02d}</a>'
        for r in refs)


def _bar(kind, label, facets, total, placeholder):
    chips = [f'<button type="button" class="kv-chip" data-f="*" aria-pressed="true">All <b>{total}</b></button>']
    for key, text, n, dot in facets:
        d = f'<i class="dot c-{esc(dot)}" aria-hidden="true"></i>' if dot else ""
        chips.append(f'<button type="button" class="kv-chip" data-f="{esc(key)}" aria-pressed="false">{d}{esc(text)} <b>{n}</b></button>')
    return (f'<div class="kv-bar" role="toolbar" aria-label="{esc(label)}">'
            f'<div class="kv-chips">{"".join(chips)}</div>'
            f'<input type="search" class="kv-q" placeholder="{esc(placeholder)}" aria-label="Search {esc(kind)}"></div>')


def _card(c):
    auth = c["authorization"]
    alias = (f'<p class="ent-alias">also: {esc(", ".join(c["aliases"]))}</p>' if c["aliases"] else "")
    src = f'<code>{esc(c["source"])}</code>' if c["source"] else '<span class="none">none yet</span>'
    owner = (f'<code>/{esc(c["owner_page"])}/</code>' if c["owner_page"] else '<span class="none">unowned</span>')
    q = " ".join([c["name"], *c["aliases"], c["class"], auth, c["source"] or "", c["owner_page"] or ""]).lower()
    return (f'<article class="ent kv-item c-{_cls_key(c["class"])}" data-f="{esc(c["class"])}" data-q="{esc(q)}">'
            f'<header><b class="ent-name">{esc(c["name"])}</b><span class="badge b-{auth.lower()}">{esc(auth)}</span></header>'
            f'{alias}'
            f'<dl><dt>Class</dt><dd>{esc(c["class"])}</dd><dt>Source</dt><dd>{src}</dd><dt>Owner page</dt><dd>{owner}</dd></dl>'
            f'<p class="ent-secs"><span>In section{"s" if len(c["sections"]) != 1 else ""}</span>{sec_chips(c["sections"])}</p>'
            f'</article>')


def _matrix(group):
    cols = group["columns"]
    head = "".join(f'<th scope="col"><a href="#{esc(anchor_id(r["id"]))}" title="{esc(r["heading"])}">{r["n"]:02d}</a></th>'
                   for r in cols)
    rows = []
    for c in group["entities"]:
        have = {r["id"] for r in c["sections"]}
        cells = "".join(
            (f'<td><a class="mx-on" href="#{esc(anchor_id(r["id"]))}" title="{r["n"]:02d} · {esc(r["heading"])}">'
             f'<span class="mx-dot" aria-hidden="true">●</span><span class="mx-n">{r["n"]:02d}</span></a></td>')
            if r["id"] in have else "<td></td>"
            for r in cols)
        rows.append(f'<tr><th scope="row">{esc(c["name"])}</th>{cells}</tr>')
    return (f'<div class="mx-wrap c-{_cls_key(group["class"])}" data-f="{esc(group["class"])}"><table class="mx">'
            f'<caption><i class="dot c-{_cls_key(group["class"])}" aria-hidden="true"></i>{esc(group["class"])}</caption>'
            f'<thead><tr><th scope="col">Entity</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def entities_html(groups):
    """Block 5's body: filter bar, one card per entity under its class heading, then the
    per-class entity-to-section matrix."""
    if not groups:
        return '<p class="kv-none">This board names no entities.</p>'
    total = sum(len(g["entities"]) for g in groups)
    tally = {a: sum(c["authorization"] == a for g in groups for c in g["entities"]) for a in AUTH_ORDER}
    summary = (f'<p class="kv-sum"><b>{total}</b> entit{"y" if total == 1 else "ies"} in <b>{len(groups)}</b> '
               f'class{"" if len(groups) == 1 else "es"} · {tally["ASSERTED"]} asserted · {tally["PROPOSED"]} proposed'
               + (f' · <span class="warn">{tally["BLOCKED"]} blocked</span>' if tally["BLOCKED"] else "")
               + (f' · {tally["UNKNOWN"]} not in the ontology' if tally["UNKNOWN"] else "")
               + '. A section number jumps to that section in block 3.</p>')
    bar = _bar("entities", "Filter entities by class", [(g["class"], g["class"], len(g["entities"]), _cls_key(g["class"]))
                                                         for g in groups], total, "Search names, aliases, sources…")
    body = "".join(
        f'<section class="kv-group" data-f="{esc(g["class"])}" aria-label="{esc(g["class"])}">'
        f'<h3 class="kv-h"><i class="dot c-{_cls_key(g["class"])}" aria-hidden="true"></i>{esc(g["class"])} <span>{len(g["entities"])}</span></h3>'
        f'<div class="kv-cards">{"".join(_card(c) for c in g["entities"])}</div></section>'
        for g in groups)
    mx = ('<h3 class="kv-h mx-h">Where each entity is said</h3>'
          '<p class="kv-sum">One table per class: a row per entity, a column per section that names one. '
          'On a phone each row stacks into the entity and its section numbers.</p>'
          + "".join(_matrix(g) for g in groups))
    return (f'<div class="kv" data-kv="entities">{summary}{bar}{body}'
            f'<p class="kv-empty" hidden>Nothing matches — clear the search or pick All.</p>{mx}</div>')


def keywords_html(groups, show_empty=()):
    """Block 4's keyword view: a chip per term, grouped by type, each chip carrying the
    sections that use it. `show_empty` names the types to list as having no term yet."""
    live = [g for g in groups if g["terms"]]
    total = sum(len(g["terms"]) for g in live)
    empty = [g["label"] for g in groups if not g["terms"] and g["type"] in show_empty]
    note = (f'<p class="kv-sum">No term yet: {esc(", ".join(empty))}.</p>' if empty else "")
    if not live:
        return f'<div class="kv" data-kv="keywords"><p class="kv-none">This board names no keywords.</p>{note}</div>'
    bar = _bar("keywords", "Filter keywords by type", [(g["type"], g["label"], len(g["terms"]), None) for g in live],
               total, "Search keywords…")
    body = "".join(
        f'<section class="kv-group" data-f="{esc(g["type"])}" aria-label="{esc(g["label"])}">'
        f'<h3 class="kv-h">{esc(g["label"])} <span>{len(g["terms"])}</span></h3><div class="kw-chips">'
        + "".join(f'<span class="kw kv-item" data-f="{esc(g["type"])}" data-q="{esc(str(t["term"]).lower())}">'
                  f'<span class="kw-t">{esc(t["term"])}</span>{sec_chips(t["sections"])}</span>' for t in g["terms"])
        + '</div></section>'
        for g in live)
    return (f'<div class="kv" data-kv="keywords">{bar}{body}'
            f'<p class="kv-empty" hidden>Nothing matches — clear the search or pick All.</p>{note}</div>')


# The class colours are the old graph palette, one pair per theme, each clearing 3:1 against
# its own theme's --paper: they mark a card's edge and a dot, never text.
CSS = """
:root{--c-people:#8b1e5f;--c-place:#7a5c3e;--c-health:#c8472f;--c-organization:#1f5a8a;--c-regulation:#5b6b1f;--c-organism:#2D6A4F;--c-commerce:#8a6508;--c-logistics:#1f6f8b;--c-documentation:#6b4fa0;--c-method:#3d7a4a;--c-unknown:#6b736e}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--c-people:#e08ab6;--c-place:#c3a483;--c-health:#F08A78;--c-organization:#8fbde6;--c-regulation:#c3d07a;--c-organism:#6FB48F;--c-commerce:#d9b44a;--c-logistics:#7fc3dc;--c-documentation:#b09ae0;--c-method:#8fd3a4;--c-unknown:#9aa39d}}
:root[data-theme="dark"]{--c-people:#e08ab6;--c-place:#c3a483;--c-health:#F08A78;--c-organization:#8fbde6;--c-regulation:#c3d07a;--c-organism:#6FB48F;--c-commerce:#d9b44a;--c-logistics:#7fc3dc;--c-documentation:#b09ae0;--c-method:#8fd3a4;--c-unknown:#9aa39d}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}}
.oanchor{scroll-margin-top:24px;border-radius:3px}
.oanchor:target{background:var(--clay-soft);outline:2px solid var(--clay);outline-offset:1px}
section.sec:has(.kv){overflow:clip}
.kv [hidden]{display:none!important}
.kv-sum{font-size:13px;color:var(--ink-2);margin:4px 0 10px}.kv-sum .warn{color:var(--warn);font-weight:600}
.kv-none{font-size:14px;color:var(--ink-3)}
.kv-bar{position:sticky;top:0;z-index:3;display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;padding:10px 0;margin:0 0 6px;background:var(--paper);border-bottom:1px solid var(--line)}
.kv-chips{display:flex;flex-wrap:wrap;gap:6px;min-width:0}
.kv-chip{font:inherit;font-size:13px;display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:50px;border:1px solid var(--line);background:var(--ground);color:var(--ink);cursor:pointer;white-space:nowrap}
.kv-chip b{font-weight:600;color:var(--ink-3);font-variant-numeric:tabular-nums}
.kv-chip[aria-pressed="true"]{background:var(--green);border-color:var(--green);color:var(--ground)}
.kv-chip[aria-pressed="true"] b{color:var(--ground)}
.kv-q{font:inherit;font-size:14px;flex:1 1 200px;min-width:0;padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--ground);color:var(--ink)}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--c-unknown);flex:none}
.c-people{--c:var(--c-people)}.c-place{--c:var(--c-place)}.c-health{--c:var(--c-health)}.c-organization{--c:var(--c-organization)}.c-regulation{--c:var(--c-regulation)}.c-organism{--c:var(--c-organism)}.c-commerce{--c:var(--c-commerce)}.c-logistics{--c:var(--c-logistics)}.c-documentation{--c:var(--c-documentation)}.c-method{--c:var(--c-method)}.c-unknown{--c:var(--c-unknown)}
.dot[class*="c-"]{background:var(--c)}
.kv-group{margin:14px 0 4px}
.kv-h{font-family:"Fraunces",Georgia,serif;font-size:17px;font-weight:700;margin:0 0 8px;display:flex;align-items:center;gap:8px}
.kv-h span{font-family:"Source Sans 3",system-ui,sans-serif;font-size:13px;font-weight:600;color:var(--ink-3)}
.kv-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}
.ent{border:1px solid var(--line);border-left:5px solid var(--c,var(--c-unknown));border-radius:8px;padding:10px 12px;background:var(--paper);display:grid;gap:6px;min-width:0}
.ent header{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.ent-name{font-size:16px;line-height:1.3;overflow-wrap:anywhere}
.ent-alias{margin:0;font-size:13px;color:var(--ink-2);overflow-wrap:anywhere}
.ent dl{display:grid;grid-template-columns:auto 1fr;gap:2px 10px;margin:0;font-size:13px}
.ent dt{color:var(--ink-3)}.ent dd{margin:0;min-width:0;overflow-wrap:anywhere}
.ent code{font:12px/1.4 ui-monospace,Menlo,monospace;background:var(--code-bg);padding:0 4px;border-radius:3px}
.ent .none{color:var(--ink-3);font-style:italic}
.ent-secs{margin:0;display:flex;flex-wrap:wrap;gap:4px;align-items:center;font-size:12px;color:var(--ink-3)}
.ent-secs>span{margin-right:4px}
.badge{flex:none;font-size:11px;font-weight:700;letter-spacing:.05em;padding:1px 7px;border-radius:4px;border:1.5px solid var(--line);background:var(--paper);color:var(--ink)}
.b-asserted{border-color:var(--green)}.b-asserted::before{content:"✓ "}
.b-proposed{border-style:dashed;border-color:var(--clay-ink)}
.b-blocked{border-color:var(--warn);color:var(--warn)}
.b-unknown{border-style:dotted;border-color:var(--ink-3)}
.sec-chip{display:inline-block;font:600 11px/1.6 ui-monospace,Menlo,monospace;padding:0 6px;border-radius:4px;border:1px solid var(--line);background:var(--ground);color:var(--ink-2);text-decoration:none}
.sec-chip:hover,.sec-chip:focus-visible{border-color:var(--clay);color:var(--ink)}
.kw-chips{display:flex;flex-wrap:wrap;gap:6px}
.kw{display:inline-flex;flex-wrap:wrap;align-items:center;gap:4px;max-width:100%;padding:3px 4px 3px 10px;border:1px solid var(--line);border-radius:14px;background:var(--paper);font-size:14px}
.kw-t{overflow-wrap:anywhere;margin-right:2px}
.kv-empty{font-size:14px;color:var(--ink-3)}
.mx-h{margin-top:22px}
.mx-wrap{overflow-x:auto;margin:0 0 12px;max-width:100%}
table.mx{border-collapse:collapse;font-size:13px;min-width:0}
table.mx caption{caption-side:top;text-align:left;font-weight:600;padding:4px 0}
table.mx caption .dot{margin-right:6px;vertical-align:-1px}
table.mx th,table.mx td{border-bottom:1px solid var(--line);padding:4px 6px;text-align:center}
.md table.mx th{text-transform:none;letter-spacing:0;font-size:13px;color:var(--ink);border-bottom:1px solid var(--line)}
table.mx th[scope="row"],table.mx thead th:first-child{text-align:left;font-weight:600;white-space:nowrap}
table.mx thead a{color:var(--ink-2);font:600 11px ui-monospace,Menlo,monospace;text-decoration:none}
.mx-on{text-decoration:none;color:var(--c,var(--green))}.mx-n{display:none}
.md .kv table.mx{display:table;width:auto}
@media (max-width:640px){
.kv-chips{flex-wrap:nowrap;overflow-x:auto;padding-bottom:2px;max-width:100%}
.kv-q{flex-basis:100%}
.kv-cards{grid-template-columns:1fr}
table.mx,table.mx tbody,table.mx tr,table.mx th,table.mx td{display:block}
.md .kv table.mx{display:block}
table.mx thead{display:none}
table.mx tr{padding:6px 0;border-bottom:1px solid var(--line)}
table.mx th[scope="row"],table.mx td{border:0;padding:0 4px 0 0;text-align:left;white-space:normal}
table.mx td{display:inline-block}table.mx td:empty{display:none}
.mx-dot{display:none}.mx-n{display:inline-block;font:600 11px/1.6 ui-monospace,Menlo,monospace;padding:0 6px;border:1px solid var(--line);border-radius:4px;color:var(--ink-2)}
}
"""

# One filter per view: class/type chips and the search box both narrow the same items; a
# group with nothing visible hides, and so does a matrix table for a class filtered out.
JS = """
document.querySelectorAll('.kv').forEach(function(root){
  var chips=root.querySelectorAll('.kv-chip'),q=root.querySelector('.kv-q'),f='*';
  var items=root.querySelectorAll('.kv-item'),groups=root.querySelectorAll('.kv-group'),
      mx=root.querySelectorAll('.mx-wrap'),empty=root.querySelector('.kv-empty');
  function apply(){
    var s=q?q.value.trim().toLowerCase():'',any=false;
    items.forEach(function(it){var ok=(f==='*'||it.getAttribute('data-f')===f)&&(!s||it.getAttribute('data-q').indexOf(s)>=0);it.hidden=!ok;if(ok)any=true;});
    groups.forEach(function(g){g.hidden=!g.querySelector('.kv-item:not([hidden])');});
    mx.forEach(function(m){m.hidden=!(f==='*'||m.getAttribute('data-f')===f);});
    if(empty)empty.hidden=any;
  }
  chips.forEach(function(c){c.addEventListener('click',function(){
    f=c.getAttribute('data-f');chips.forEach(function(x){x.setAttribute('aria-pressed',x===c?'true':'false');});apply();
  });});
  if(q)q.addEventListener('input',apply);
});
"""
