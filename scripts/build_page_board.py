#!/usr/bin/env python3
"""build_page_board.py <slug>
The board record → docs/artifacts/boards/<slug>.html, an Artifact with the db capability.
Thumbnails are not part of this port (board_canvas.py and board_thumbs.mjs stay in CAG),
so every option renders as a labelled box.
Publish with the Artifact tool: file_path=<html>, capabilities={"db": {}}."""
import html as H, json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pageboard as PB

OUT = PB.ROOT / "docs" / "artifacts" / "boards"

CSS = """
:root{--ground:#F7F5EE;--paper:#FFFFFF;--ink:#1E2A24;--ink-2:#4B5A52;--ink-3:#7A867F;--line:#DDD9CC;--green:#2D6A4F;--green-soft:#E3EEE8;--clay:#E8604C;--clay-ink:#c8472f;--clay-soft:#FBE7E2;--code-bg:#F0EEE5;--mark:#FFF3C4;--warn:#9C3A2A;--on-clay:#FFFFFF}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ground:#151A17;--paper:#1D2420;--ink:#ECEBE3;--ink-2:#B7BDB6;--ink-3:#7F8983;--line:#2F3934;--green:#6FB48F;--green-soft:#1F2F28;--clay:#F08A78;--clay-ink:#F08A78;--clay-soft:#3A2622;--code-bg:#11161380;--mark:#4A3F16;--warn:#F2A08F;--on-clay:#191F1C}}
:root[data-theme="dark"]{--ground:#151A17;--paper:#1D2420;--ink:#ECEBE3;--ink-2:#B7BDB6;--ink-3:#7F8983;--line:#2F3934;--green:#6FB48F;--green-soft:#1F2F28;--clay:#F08A78;--clay-ink:#F08A78;--clay-soft:#3A2622;--code-bg:#11161380;--mark:#4A3F16;--warn:#F2A08F;--on-clay:#191F1C}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font:16px/1.6 "IBM Plex Sans",system-ui,-apple-system,Segoe UI,sans-serif}
.wrap{max-width:1120px;margin:0 auto;padding:36px 24px 96px}
header.masthead{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;padding-bottom:18px;border-bottom:2px solid var(--green);margin-bottom:24px}
.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--green);font-weight:600;margin:0 0 6px}
h1.title{font-family:"Source Serif 4",Georgia,serif;font-weight:700;font-size:clamp(26px,3.6vw,38px);line-height:1.1;margin:0;text-wrap:balance}
.meta{font-size:13px;color:var(--ink-3);text-align:right;line-height:1.5}
.pill{display:inline-block;border-radius:50px;padding:2px 9px;font-size:11px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;border:1px solid var(--line);background:var(--paper)}
section.sec{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:24px 28px 26px;margin:0 0 20px}
section.sec h2{font-family:"Source Serif 4",Georgia,serif;font-weight:700;font-size:22px;margin:0 0 10px;line-height:1.2}
.md p,.md li{max-width:72ch}.md table{border-collapse:collapse;width:100%;font-size:14px;margin:10px 0 14px;display:block;overflow-x:auto}
.md th{text-align:left;font-weight:600;color:var(--ink-2);font-size:12px;text-transform:uppercase;letter-spacing:.06em;border-bottom:2px solid var(--green);padding:6px 10px;white-space:nowrap}
.md td{padding:6px 10px;border-bottom:1px solid var(--line);vertical-align:top;font-variant-numeric:tabular-nums}
.md code{font:13px/1.5 "IBM Plex Mono",ui-monospace,Menlo,monospace;background:var(--code-bg);padding:1px 5px;border-radius:4px}
.tree{font:13px/1.65 "IBM Plex Mono",ui-monospace,Menlo,monospace;white-space:pre-wrap;margin:0;overflow-x:auto}
.hit{color:var(--warn);font-weight:600}
#entity-graph{height:440px;border:1px solid var(--line);border-radius:8px;background:var(--ground)}
.legend{font-size:12px;color:var(--ink-3);margin:6px 0 0}
.opts{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px;margin:8px 0 6px}
.opt{border:1px solid var(--line);border-radius:8px;padding:8px;background:var(--paper);display:grid;gap:6px}
.opt img,.opt .nothumb{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:5px;border:1px solid var(--line);background:var(--code-bg);display:grid;place-items:center;font-size:12px;color:var(--ink-3)}
.opt.off{opacity:.55}.opt label{display:flex;gap:8px;align-items:center;font-size:13px;font-weight:600;cursor:pointer}
.opt .why{font-size:12px;color:var(--ink-3)}
.opt .pill{justify-self:start;text-transform:none;letter-spacing:0;background:var(--green-soft);border-color:var(--green);color:var(--ink-2)}
textarea.note{width:100%;min-height:52px;font:13px/1.5 "IBM Plex Sans",system-ui,sans-serif;border:1px solid var(--line);border-radius:6px;padding:8px;background:var(--ground);color:var(--ink)}
.slots{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}
.slot{border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:13px}.slot .st{font-weight:700}.slot .st.missing{color:var(--warn)}
#approve{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
button.btn{font:inherit;font-size:14px;font-weight:600;padding:10px 18px;border-radius:50px;border:1px solid var(--clay-ink);background:var(--clay-ink);color:var(--on-clay);cursor:pointer}
button.btn[disabled]{opacity:.5;cursor:default}
.status{font-size:13px;color:var(--ink-2)}
button:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid var(--clay);outline-offset:2px}
.kit .opt{gap:5px}
.kit .opt b{font-size:13px;font-weight:600}
.kit .opt .pill:first-child{justify-self:start;background:var(--paper);border-color:var(--line);color:var(--ink-3);text-transform:uppercase;letter-spacing:.06em}
@media (max-width:640px){header.masthead{grid-template-columns:1fr}.meta{text-align:left}section.sec{padding:18px 16px 20px}}
"""


# Every string in the record is breeder- or agent-written text, and three of this page's
# four contexts will misread it if it is passed through raw: HTML reads a tag, markdown
# reads a pipe or an asterisk, and a `</script>` anywhere inside a text/markdown block or
# the graph's JSON ends the block early and drops the rest of the page. So: esc() for an
# HTML context, md() for a markdown one, js() for anything embedded in a <script>.
MD_PUNCT = ("|", "*", "_", "`", "~", "[", "]")


def esc(value):
    """HTML-escape one record value (None → empty), for an HTML context."""
    return H.escape("" if value is None else str(value))


def md(value):
    """Escape one record value for a MARKDOWN context: HTML first, then the punctuation
    marked would otherwise act on — a pipe ends a table column, `*`/`_` open emphasis —
    and a leading `#`, which would turn a value into a heading of its own."""
    out = esc(value).replace("\\", "\\\\")
    for ch in MD_PUNCT:
        out = out.replace(ch, "\\" + ch)
    out = " ".join(out.split())
    return "\\" + out if out.startswith("#") else out


def md_with_urls(value):
    """md() for prose that may carry bare URLs: each http(s) URL is wrapped in <…> so marked
    autolinks it verbatim, and only the text around it is escaped — md() alone would put a
    backslash inside any URL with an underscore."""
    text = "" if value is None else str(value)
    out, last = [], 0
    for m in re.finditer(r"https?://[^\s<>()]+", text):
        out.append(md(text[last:m.start()]))
        out.append("<" + H.escape(m.group(0), quote=True) + ">")
        last = m.end()
    out.append(md(text[last:]))
    return " ".join(p for p in out if p)


def js(value):
    """JSON for embedding in a <script>: `</script>` inside any string would close the
    block, so the sequence is written with the escape JSON allows and JS reads back."""
    return json.dumps(value).replace("</", "<\\/")


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def flag(heading, hit_by):
    h = hit_by.get(heading)
    if not h:
        return ""
    kind = {"exact": "exact match with", "template": "template match with", "shingle": "5-word overlap with"}[h["kind"]]
    return f'   <span class="hit">⚠ {kind} {esc(h["page"])}</span>'


def outline_block(board, hits):
    """The whole outline as one tree, H1 included — read from all_headings() so the board
    shows the same H1 the gate judged, whether it came from a pick or the recommendation."""
    hit_by = {h["heading"]: h for h in hits}
    h1 = PB.all_headings(board)[0][1]
    lines = [f"H1  {esc(h1)}" + flag(h1, hit_by)]
    for s in board["sections"]:
        cta = f" · CTA×{s['cta']}" if s.get("cta") else ""
        lines.append(f"├─ H2 {s['n']:02d}  {esc(s['heading'])}   [{s['category']} · {GROUP_SHORT[s['group']]} · {s['shape']} · {s['framework']} · {s['words']['min']}–{s['words']['max']}w{cta}]" + flag(s["heading"], hit_by))

        def walk(nodes, depth):
            for n in nodes:
                lines.append("│   " * depth + f"├─ H{n['level']} {esc(n['heading'])}" + flag(n["heading"], hit_by))
                walk(n["children"], depth + 1)
        walk(s["tree"], 1)
        for i, q in enumerate(s.get("questions", []), 1):
            lines.append(f"│   ├─ Q{i:02d} {esc(q)}" + flag(q, hit_by))
        for l in s["links"]["internal"]:
            lines.append(f"│   → {esc(l['anchor'])} → {esc(l['href'])}")
        for l in s["links"]["external"]:
            lines.append(f"│   ↗ {esc(l['anchor'])} → {esc(l['href'])}   [{esc(l['library_row'])}]")
    return "\n".join(lines)


def entity_graph_data(board, ont):
    by_id = {e["id"]: e for e in ont["entities"]}
    nodes, edges, seen = [], [], set()
    for s in board["sections"]:
        nodes.append({"data": {"id": "sec:" + s["id"], "label": f"{s['n']:02d} {s['heading'][:34]}", "kind": "section"}})
        for eid in s["entities"]:
            e = by_id.get(eid, {"name": eid, "class": "Unknown", "authorization": "PROPOSED"})
            if eid not in seen:
                seen.add(eid)
                nodes.append({"data": {"id": eid, "label": e["name"], "kind": e["class"], "auth": e["authorization"]}})
            edges.append({"data": {"source": "sec:" + s["id"], "target": eid, "auth": e["authorization"]}})
    return {"nodes": nodes, "edges": edges}


def option_cards(section, ledger, slug, thumbs):
    """One card per candidate the pool offers, plus the pick when a rename has already
    carried it out of the pool, plus a dimmed card per excluded shell.

    A `base#refresh` is the pool saying "this shell is spent, reuse it along an axis you
    have not named yet" — so the card is labelled with the BASE and badged, not titled
    with a placeholder id nobody chose. A `base#delta` shows the delta it does vary."""
    cands, excluded = PB.candidates_for(section["shape"], ledger, slug)
    pick = section["options"]["pick"]
    if pick and pick not in cands:
        cands = list(cands) + [pick]          # a renamed refresh the pool no longer offers
    cards = []
    for c in cands:
        base = PB.base_of(c)
        delta = c.split("#", 1)[1].strip() if "#" in c else ""
        badge = "REFRESH — name the axis" if delta == "refresh" else delta   # one label, board and canvas
        th = thumbs.get((section["id"], c)) or thumbs.get((section["id"], base))
        img = (f'<img src="{esc(th)}" alt="{esc(base)} option for {esc(section["id"])}">'
               if th else f'<div class="nothumb">{esc(base)}</div>')
        checked = " checked" if pick == c else ""
        cards.append(f'<div class="opt">{img}<label><input type="radio" name="pick-{section["id"]}" value="{esc(c)}"{checked}> {esc(base)}</label>'
                     + (f'<span class="pill">{esc(badge)}</span>' if badge else "") + "</div>")
    for x in excluded:
        # The schema requires `owner` and only allows `owners`, so the singular is the
        # fallback: an excluded card with no owner on it reads as a bug, not as a rule.
        owners = ", ".join(x.get("owners") or ([x["owner"]] if x.get("owner") else []))
        cards.append(f'<div class="opt off"><div class="nothumb">{esc(x["component"])}</div>'
                     f'<span class="why">owned by {esc(owners)} — excluded</span></div>')
    return cards



KIT_AXES = ("hero", "dial", "rail", "toc", "table", "stepper", "faq")


def kit_thumb(component_id, thumbs):
    """Any artboard cut for this shell, whatever section it was cut under: the canvas
    cuts chrome beneath whichever section offered it, so a section-scoped lookup would
    leave the strip blank. Exact id first, then the base."""
    base = PB.base_of(component_id)
    for wanted in (component_id, base):
        for (_section, candidate), src in thumbs.items():
            if candidate == wanted:
                return src
    return None


def _kit_card(axis, v, owned, thumbs):
    """One shell card. An empty axis is shown as worn-by-nobody rather than dropped, so a
    page without a stepper says so instead of looking like a strip with a card missing."""
    if not v:
        return (f'<div class="opt off"><span class="pill">{esc(axis)}</span><div class="nothumb">none</div>'
                f'<span class="why">this page wears no {esc(axis)}</span></div>')
    base = PB.base_of(v)
    delta = v.split("#", 1)[1].strip() if "#" in v else ""
    th = kit_thumb(v, thumbs)
    img = (f'<img src="{esc(th)}" alt="{esc(base)} — the {esc(axis)} this page wears">'
           if th else f'<div class="nothumb">{esc(base)}</div>')
    owners = owned.get(v) or owned.get(base) or []
    tracked = axis in PB.TUPLE_ID_KEYS or axis == "takeaway"
    why = ("not tracked by the component ledger yet" if not tracked
           else "also worn by " + esc(", ".join(owners)) if owners else "new to the cluster")
    return (f'<div class="opt"><span class="pill">{esc(axis)}</span>{img}<b>{esc(base)}</b>'
            + (f'<span class="pill">refresh: {esc(delta)}</span>' if delta else "")
            + f'<span class="why">{why}</span></div>')


def kit_cards(board, ledger, thumbs, slug):
    """Every tuple axis this page wears (brief §13): seven shells, each takeaway card, and the
    newsletter placement — shown, never offered. Block 6 picks per section; the tuple is the
    author's decision against the ledger, and a radio here would invite a choice the ledger
    rules decide, not the sitting."""
    t = board["tuple"]
    owned = PB.owned_components(ledger, exclude_slug=slug)
    cards = [_kit_card(axis, (t.get(axis) or "").strip(), owned, thumbs) for axis in KIT_AXES]
    cards += [_kit_card("takeaway", k.strip(), owned, thumbs) for k in (t.get("takeaway") or [""])]
    nl = t["newsletter"]
    if nl["after"]:
        sec = next((s for s in board["sections"] if s["id"] == nl["after"]), None)
        if sec is None:
            raise PB.BoardError(f"tuple.newsletter.after {nl['after']!r} is not a section id")
        cards.append(f'<div class="opt"><span class="pill">newsletter</span><div class="nothumb">variant {esc(nl["variant"])}</div>'
                     f'<b>after {sec["n"]:02d} · {esc(sec["heading"])}</b>'
                     '<span class="why">kit §11 litter-alert signup, placed in context</span></div>')
    else:
        cards.append('<div class="opt off"><span class="pill">newsletter</span><div class="nothumb">none</div>'
                     '<span class="why">this page places no newsletter</span></div>')
    return cards


STANDARD_FORM_DEFAULT = "kit two-column inquiry form (field contract by slug)"


GROUP_SHORT = {"MANDATORY": "mandatory", "COMPETITOR-BASED": "competitor", "SUGGESTED-RECOMMENDED": "ours"}


def standard_default(section, board):
    """What a standard section gets without anyone choosing anything (spec §4.6).

    A standard section still occupies the page, so the board shows it — a FAQ renders the
    shell the tuple already names, a reserve/form section renders the kit's inquiry form,
    and anything else falls back to whatever the ledger hands it. Shown, never offered:
    a breeder who sees no card for section 08 assumes the section has no component."""
    sid = section["id"].lower()
    if "faq" in sid:
        return board["tuple"].get("faq") or "ledger default"
    if "reserve" in sid or "form" in sid:
        return STANDARD_FORM_DEFAULT
    return "ledger default"


def radio_list(name, items, recommended, picked):
    """One radio group, one line per variant, the recommendation starred, every variant
    carrying its own length. The label keeps the click target on the text: three
    70-character titles are an unreasonable click target as bare radios."""
    return "\n".join(
        f'{"⭐ " if i == recommended else ""}<label><input type="radio" name="{esc(name)}" value="{i}"'
        f'{" checked" if i == picked else ""}> {esc(v)} <span class="why">({len(v)} chars)</span></label>  '
        for i, v in enumerate(items))


def angles_table(brief):
    """Angles considered, the chosen one starred. Its third column is the strategy's own
    trade-off rather than a why_not: a table where only the rejects carry a cost reads as
    one good idea and two bad ones, which is not what the sitting is for."""
    rows = []
    for a in brief["angles"]:
        taken = a["name"] == brief["strategy"]["name"]
        rows.append([("⭐ " if taken else "") + md(a["name"]), md(a["hook"]),
                     ("**taken** — trade-off: " + md(brief["strategy"]["trade_off"])) if taken
                     else md(a["why_not"])])
    return md_table(["Angle", "Hook", "Why not / trade-off"], rows)


def image_plan_table(board):
    """One row per image slot the outline plans, prompt included: the infographic prompts ARE
    the generation pack (§15c), and a photo prompt says what the photo has to show. A
    signature section with no slot gets a row of its own, so the gap is on the board rather
    than only in the gate output."""
    rows = []
    for s in board["sections"]:
        label = f"{s['n']:02d} {md(s['heading'])}"
        if not s["images"]:
            rows.append([label, "—", "—", "—",
                         "_no image slot_" if s["shape"] == "standard" else "**⚠ no image slot**"])
        for i in s["images"]:
            rows.append([label, md(i["slot"]), md(i["kind"]),
                         "required" if i["required"] else "optional", md(i["prompt"]) or "_no prompt_"])
    return md_table(["Section", "Slot", "Kind", "Required", "Prompt"], rows)


def decisions_lines(brief):
    """The page-level decisions the brief gates on (§8, §10, §14, §16d), one bold-led line
    each, so the sitting reads them beside the strategy they serve."""
    c, tool, sch = brief["cta"], brief["tool"], brief["schema"]
    return [f"**CTA plan.** One every {c['cadence']['min']}–{c['cadence']['max']} words, to {md(c['destination'])}; "
            f"anchors: {', '.join(md(a) for a in c['anchors'])}; the site-wide CTA band is "
            f"{'hidden on this page' if c['global_cta'] == 'hidden' else 'shown'}.",
            f"**Tool.** {md(tool['pick'])} — evidence: {md(tool['evidence'])}"
            + (f" Trade-off: {md(tool['trade_off'])}" if tool["trade_off"].strip() else ""),
            f"**Schema plan.** offer model {md(sch['offer_model'])}; types: {', '.join(md(t) for t in sch['types'])}."]


def render(board, ont, ledger, live, thumbs, slug):
    hits = PB.header_hits(board, live)          # exactly what the gate will fail on
    qhits = PB.faq_hits(board, live)            # and what it will warn on
    d = PB.distribution(board)
    auth = PB.authorization_check(board, ont)
    approved = PB.approval_matches(board)
    m = board["meta"]
    parts = []

    brief = board["brief"]
    parts.append(("1. Brief", "\n".join([
        f"**Goal.** {md(brief['goal'])}", f"**Scope.** {md(brief['scope'])}",
        f"**Gates.** {', '.join(md(g) for g in brief['gates'])}",
        f"**Done means.** {md(brief['done'])}",
        f"**Out of scope.** {', '.join(md(o) for o in brief['out_of_scope']) or 'nothing named'}",
        f"**Primary keyword.** {md(brief['primary_keyword'])}",
        f"**Strategy: {md(brief['strategy']['name'])}.** Why: {md(brief['strategy']['why'])}",
        *decisions_lines(brief),
        "", "**Angles considered**", angles_table(brief),
        "", "**Research used**", md_table(["Source", "Fetched"], [[md(s["path"]), md(s["fetched"])] for s in m["sources"]]) if m["sources"] else "_no sources recorded_",
    ])))

    h1, ms = board["h1"], board["meta_set"]
    picked = h1["pick"] if h1["pick"] is not None else h1["recommended"]
    # The board must star the same pair the gate and the build will read, so the fallback
    # is PB.meta_pick()'s and not a second copy of it. It returns the STRINGS; the radio
    # group needs their index, and a board carrying one string twice is degenerate anyway.
    mt_s, md_s = PB.meta_pick(board)
    mt, mdn = ms["titles"].index(mt_s), ms["descriptions"].index(md_s)
    parts.append(("2. H1 and meta", "\n".join([
        "**H1** — the page's own promise", "",
        radio_list("h1", h1["variants"], h1["recommended"], picked), "",
        f"**Title tag** — ceiling {PB.title_ceiling(slug)} characters", "",
        radio_list("meta-title", ms["titles"], ms["recommended"]["title"], mt), "",
        f"**Meta description** — band {PB.DESC_MIN}–{PB.DESC_MAX} characters", "",
        radio_list("meta-description", ms["descriptions"], ms["recommended"]["description"], mdn),
    ])))

    parts.append(("3. Outline", f"<pre class=\"tree\">{outline_block(board, hits + qhits)}</pre>\n\n"
                  + (f"**{len(hits)} heading(s) collide with a live page.** Rewrite them before approving; "
                     "the gate fails on any." if hits else
                     "No heading collides with a live page (exact, species-template or 5-word shingle).")
                  + (f"\n\n{len(qhits)} FAQ question(s) repeat a live heading — a warning, not a refusal."
                     if qhits else "")))

    parts.append(("3b. Image plan", image_plan_table(board)
                  + "\n\nEvery image slot the outline plans. Infographic prompts are the generation pack; "
                    "photo prompts say what the photo has to show. Page-level files and alts are in block 7."))

    rows = [[md(r["section"])] + [r[k] for k in PB.KEYWORD_TYPES] + [f"{r['words_min']}–{r['words_max']}"] for r in d["rows"]]
    t = d["totals"]
    rows.append(["**totals**"] + [t[k] for k in PB.KEYWORD_TYPES] + [f"{t['words_min']}–{t['words_max']}"])
    c = d["h_counts"]
    why_rows = [[f"{s['n']:02d} {md(s['heading'])}", md(s["group"]), md(s["framework"]), md(s["why"]), md_with_urls(s["why_source"])]
                for s in board["sections"]]
    parts.append(("4. Distribution", md_table(["Section"] + [PB.KEYWORD_LABELS[k] for k in PB.KEYWORD_TYPES] + ["Words"], rows)
                  + f"\n\nHeadings: H1 {c['h1']} · H2 {c['h2']} · H3 {c['h3']} · H4 {c['h4']} · H5 {c['h5']} · H6 {c['h6']}. Counts are ceilings, not floors."
                  + "\n\n**Why each section is here**\n\n"
                  + md_table(["Section", "Group", "Framework", "Why", "Source"], why_rows)))

    by_id = {e["id"]: e for e in ont["entities"]}
    ent_rows = []
    all_ents = sorted({e for s in board["sections"] for e in s["entities"]})
    for eid in all_ents:
        e = by_id.get(eid)
        cells = ["✓" if eid in s["entities"] else "" for s in board["sections"]]
        ent_rows.append([f"{md(e['name'] if e else eid)} ({md(e['authorization']) if e else 'UNKNOWN'})"] + cells + [md((e or {}).get("owner_page")) or "—"])
    ent_md = ('<div id="entity-graph"></div><p class="legend">colour = class · solid = ASSERTED · dashed = PROPOSED · red = BLOCKED (fails the board)</p>\n\n'
              + md_table(["Entity"] + [f"{s['n']:02d}" for s in board["sections"]] + ["Owner"], ent_rows)
              + (f"\n\n**BLOCKED referenced: {', '.join(md(e) for e in auth['blocked'])}.** The board cannot be approved." if auth["blocked"] else "")
              + (f"\n\nPROPOSED (need a source): {', '.join(md(e) for e in auth['proposed'])}." if auth["proposed"] else ""))
    parts.append(("5. Entities", ent_md))

    parts.append(("5b. The kit", f'<div class="opts kit">{"".join(kit_cards(board, ledger, thumbs, slug))}</div>'
                  "\n\nThe page-level tuple, for reading. Picks happen in block 6; a shell that is wrong here is "
                  "a record edit, not a radio."))

    opt_html = []
    for s in board["sections"]:
        if s["shape"] == "standard":
            dflt = standard_default(s, board)
            cards = [f'<div class="opt"><div class="nothumb">{esc(dflt)}</div>'
                     f'<span class="why">the default a standard section gets — nothing to pick</span></div>']
        else:
            cards = option_cards(s, ledger, slug, thumbs)
        opt_html.append(f"### {s['n']:02d} · {md(s['heading'])} <span class=\"pill\">{md(s['shape'])}</span>\n\n<div class=\"opts\">{''.join(cards)}</div>\n"
                        f"<textarea class=\"note\" name=\"note-{s['id']}\" placeholder=\"Note for this section (optional)\">{esc(s['options']['note'])}</textarea>")
    parts.append(("6. Component options", "\n\n".join(opt_html) or "_No sections._"))

    slots = "".join(
        f'<div class="slot"><b>{esc(a["slot"])}</b> · {esc(a["kind"])} · {a["w"]}×{a["h"]} · {"required" if a["required"] else "optional"}'
        f'<br><span class="st {esc(a["status"])}">{esc(a["status"])}</span>{(" · " + esc(a["file"])) if a["file"] else ""}'
        f'{("<br><span class=" + chr(34) + "why" + chr(34) + ">alt: " + esc(a["alt"]) + "</span>") if a.get("alt") else ""}</div>'
        for a in board["assets"])
    parts.append(("7. Asset slots", f'<div class="slots">{slots}</div>'))

    approve = (f'<div id="approve"><button class="btn" id="approve-btn" disabled>Approve this board</button>'
               f'<span class="status" id="approve-status">{"Approved as it stands." if approved else "Connecting to the board database…"}</span></div>')
    parts.append(("8. Approve", approve + "\n\nWrites your H1 choice, picks, notes and the record hash to the board database. Build refuses to start without it; any later edit to the record clears it."))

    blocks = "".join(f'<script type="text/markdown" data-title="{esc(t)}">\n{b}\n</script>\n' for t, b in parts)
    graph = js(entity_graph_data(board, ont))
    record_hash = PB.record_hash(board)
    return f"""<title>Page Board: {esc(slug)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,700&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header class="masthead"><div><p class="eyebrow">BlueStaffyUK · Page Board</p><h1 class="title">/{esc(slug)}/</h1></div>
<div class="meta"><span class="pill">status: {esc(m['status'])}</span> <span class="pill">research as of {esc(m['research_as_of'])}</span><br>record <code>{record_hash[:12]}</code></div></header>
<div id="doc"></div>
</div>
{blocks}
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.0/marked.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.30.2/cytoscape.min.js"></script>
<script>
(function(){{
  var doc=document.getElementById('doc');
  document.querySelectorAll('script[type="text/markdown"]').forEach(function(b){{
    var sec=document.createElement('section');sec.className='sec';
    var h2=document.createElement('h2');h2.textContent=b.getAttribute('data-title');sec.appendChild(h2);
    var body=document.createElement('div');body.className='md';
    body.innerHTML=window.marked?marked.parse(b.textContent.replace(/^\\n+|\\s+$/g,'')):b.textContent;
    sec.appendChild(body);doc.appendChild(sec);
  }});
  var G={graph};
  var el=document.getElementById('entity-graph');
  // Two palettes, not one: a graph drawn in ink-dark fills disappears on the dark ground
  // and a graph drawn in light fills disappears on the light one. Every fill below clears
  // 3:1 against its own theme's --ground, which is why the light section node is a mid
  // clay-brown rather than the cream the page uses for card beds.
  var PAL={{
    light:{{Organism:'#2D6A4F',Documentation:'#6b4fa0',Health:'#c8472f',Commerce:'#8a6508',Logistics:'#1f6f8b',Place:'#7a5c3e',People:'#8b1e5f',Method:'#3d7a4a',Unknown:'#6b736e',section:'#8c7a5e',edge:'#6f7a74',blocked:'#c8472f',border:'#3A3227',ink:'#1E2A24'}},
    dark:{{Organism:'#6FB48F',Documentation:'#b09ae0',Health:'#F08A78',Commerce:'#d9b44a',Logistics:'#7fc3dc',Place:'#c3a483',People:'#e08ab6',Method:'#8fd3a4',Unknown:'#9aa39d',section:'#7d8f84',edge:'#8d9a93',blocked:'#F08A78',border:'#D8DEDA',ink:'#ECEBE3'}}
  }};
  function darkMode(){{
    var a=document.documentElement.getAttribute('data-theme');
    if(a==='dark')return true;
    if(a==='light')return false;
    return !!(window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches);
  }}
  function graphStyle(){{
    var p=PAL[darkMode()?'dark':'light'];
    return [{{selector:'node',style:{{'label':'data(label)','font-size':10,'width':18,'height':18,'background-color':function(n){{return p[n.data('kind')]||p.Unknown}},'color':p.ink,'text-wrap':'wrap','text-max-width':110}}}},
            {{selector:'node[kind="section"]',style:{{'shape':'round-rectangle','width':60,'height':22,'font-weight':'bold','border-width':1,'border-color':p.border}}}},
            {{selector:'edge',style:{{'width':1.5,'line-color':p.edge,'curve-style':'bezier'}}}},
            {{selector:'edge[auth="PROPOSED"]',style:{{'line-style':'dashed'}}}},
            {{selector:'edge[auth="BLOCKED"]',style:{{'line-color':p.blocked,'width':3}}}}];
  }}
  if(el&&window.cytoscape){{
    var cy=cytoscape({{container:el,elements:G.nodes.concat(G.edges),layout:{{name:'cose',animate:false,padding:20}},style:graphStyle()}});
    if(window.matchMedia){{
      var mq=window.matchMedia('(prefers-color-scheme: dark)');
      var repaint=function(){{cy.style(graphStyle());}};
      if(mq.addEventListener)mq.addEventListener('change',repaint);else if(mq.addListener)mq.addListener(repaint);
    }}
  }}
  var RECORD_HASH={js(record_hash)};var BOARD_DOC={js("boards/" + slug)};
  var SIGNATURE_SECTIONS={js([s["id"] for s in board["sections"] if s["shape"] != "standard"])};
  var btn=document.getElementById('approve-btn'),st=document.getElementById('approve-status');
  if(!window.claude||!window.claude.use){{st.textContent='Open this board inside claude.ai to approve it.';return;}}
  window.claude.use("db").then(function(db){{
    if(!db){{st.textContent='Approval needs the board database, which this view cannot reach.';return;}}
    var ref=db.doc(BOARD_DOC);
    ref.get().then(function(snap){{
      if(!snap||!snap.exists){{return;}}                 // absence is not an error: never approved
      var d=snap.data()||{{}};                            // frozen body; undefined only when !exists
      if(d.record_hash===RECORD_HASH){{st.textContent='Approved '+(d.approved_at||'earlier')+'.';}}
      else{{st.textContent='An earlier version of this board was approved — this record has changed since.';}}
    }}).catch(function(e){{st.textContent='Could not read the board database: '+(e&&e.code?e.code:'error')+'. Approve in chat.';}});
    btn.disabled=false;st.textContent=st.textContent.indexOf('Approved')===0?st.textContent:'Ready.';
    btn.addEventListener('click',function(){{
      // A half-picked board is worse than an unapproved one: the build would start and
      // then guess a component. Refuse the write and name the sections still open.
      var missing=SIGNATURE_SECTIONS.filter(function(id){{
        return !document.querySelector('input[name="pick-'+id+'"]:checked');
      }});
      if(missing.length){{
        st.textContent=missing.length+' section(s) still need a pick: '+missing.join(', ');
        btn.disabled=false;return;
      }}
      var h1=document.querySelector('input[name="h1"]:checked');
      if(!h1){{st.textContent='Pick an H1 before approving.';btn.disabled=false;return;}}
      var mt=document.querySelector('input[name="meta-title"]:checked'),
          mdsc=document.querySelector('input[name="meta-description"]:checked');
      if(!mt||!mdsc){{st.textContent='Pick a title and a description before approving.';btn.disabled=false;return;}}
      var picks={{}},notes={{}};
      document.querySelectorAll('input[name^="pick-"]:checked').forEach(function(i){{picks[i.name.slice(5)]=i.value;}});
      // Every note box, empty included — "" is how a cleared note reaches the record.
      document.querySelectorAll('textarea[name^="note-"]').forEach(function(t){{notes[t.name.slice(5)]=t.value.trim();}});
      var rec={{approved_at:new Date().toISOString(),h1:parseInt(h1.value,10),
               meta:{{title:parseInt(mt.value,10),description:parseInt(mdsc.value,10)}},
               picks:picks,notes:notes,canvas_version:null,record_hash:RECORD_HASH}};
      btn.disabled=true;st.textContent='Saving…';
      ref.set(rec).then(function(){{st.textContent='Approved '+rec.approved_at+'. Claude reads this back before building.';}})
        .catch(function(e){{btn.disabled=false;st.textContent='Could not save: '+(e&&e.code?e.code:'error')+'. Try again, or approve in chat.';}});
    }});
  }}).catch(function(e){{st.textContent='Board database unavailable: '+(e&&e.code?e.code:'error')+'. Approve in chat.';}});
}})();
</script>
"""


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: build_page_board.py <slug>")
    slug = sys.argv[1]
    board = PB.load_board(slug)
    ont, ledger = PB.load_ontology(), PB.load_ledger()
    # No own-page pop: PB.header_hits() excludes it with own_live_key(), which is "/" for
    # the homepage — the pop built "//" and left the homepage colliding with itself.
    live = PB.live_headings() if PB.DIST.exists() else {}
    # No thumbnails: board_thumbs.mjs is not ported, so the map stays empty and every
    # option card renders as its labelled box.
    thumbs = {}
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / (slug.replace("/", "--") + ".html")
    out.write_text(render(board, ont, ledger, live, thumbs, slug), encoding="utf-8")
    print("wrote %s — %d sections, %d live pages checked"
          % (out.relative_to(PB.ROOT), len(board["sections"]), len(live)))


if __name__ == "__main__":
    main()
