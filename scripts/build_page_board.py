#!/usr/bin/env python3
"""build_page_board.py <slug>
The board record → docs/artifacts/boards/<slug>.html, an Artifact with the db capability.
Thumbnails are not part of this port (board_canvas.py and board_thumbs.mjs stay in CAG),
so a section with no rendered styles renders every option as a labelled box.

A section that DOES offer styles (`styles: ["S1","S2","S3"]`) gets the real thing: the
three arrangements src/lib/boardStyles.ts defines, cut out of the built
/board-preview/<slug>/ route by scripts/build_board_previews.py and mounted here in
sandboxed srcdoc iframes at 1280 / 768 / 375. Run, in order:

    npm run build
    python3 scripts/build_board_previews.py <slug>
    python3 scripts/build_page_board.py <slug>

Publish with the Artifact tool: file_path=<html>, capabilities={"db": {}}. A project 5 board
(block 7c, infographics) also publishes the two web fonts its infographic previews load, as
Artifact `files` beside the page (IG_FONT_FILES; `main()` prints the exact map):

    files={"fonts/fraunces-latin-standard-normal.woff2":
               "public/fonts/fraunces-latin-standard-normal.woff2",
           "fonts/source-sans-3-latin-wght-normal.woff2":
               "public/fonts/source-sans-3-latin-wght-normal.woff2"}

Without them the previews still render, in the token fallback stacks (Georgia, system-ui)."""
import html as H, json, pathlib, re, sys
from urllib.parse import urlsplit
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pageboard as PB
import link_diversity as LD
import verbatim_set_check as VSC
import image_rules as IR          # block 7's image pickers (system-gaps build, Task 10b)
import image_candidates as IC      # the image slots, walked in outline order (refusal labels)
import keyword_metrics as KM       # block 4b, the ours-vs-top-5 table (parity build Task 18)
# Board v2 (plan 2026-10-02, Task 7): six blocks, on project 5 boards only.
import serp_reading as SR          # block 1b, how Google reads this page
import term_density as TD          # block 4c, per-term density against competitors
import faq_layout as FL            # block 4d, where the FAQs sit
import neighbourhoods as NB         # block 3d, the city areas and their keywords
import term_gap as TG              # block 5c, what competitors say that we do not
import infographic_plan as IP      # block 7c, infographic style trios
import original_slots as OS        # block 7d, the original-photo slots
import board_entities as BE
import page_intake as PI          # block 0, the intake (the brief's target block)
import outline_matrix as OM       # STOP 2: the outline is approved before the page board
from _kit_sections import find_sections, page_css, page_sprite, uses_sprite

OUT = PB.ROOT / "docs" / "artifacts" / "boards"
PREVIEWS = PB.ROOT / "data" / "boards" / "previews"

#: Every style preview iframe is this tall, and scrolls inside. Measuring the real height
#: would mean a Playwright pass per block; a fixed frame with `overflow:auto` shows the top
#: of every arrangement at three widths, which is what the pick is actually made on.
PREVIEW_H = 520
#: The three widths each style is shown at: desktop, tablet, phone.
PREVIEW_W = (1280, 768, 375)

#: Block 7c's previews load their web fonts from here, RELATIVE TO THE BOARD: the frames are
#: srcdoc documents, and a srcdoc document resolves relative URLs against its parent's base
#: URL, so `fonts/x.woff2` is the file published beside the board as an Artifact `file`. The
#: frames carry `sandbox="allow-same-origin"` (and nothing else, so still no script runs) for
#: exactly this: an opaque-origin frame would fetch the font cross-origin, and a font fetch is
#: CORS-checked. Opened from disk, `docs/artifacts/boards/fonts/` does not exist and the
#: previews fall back to the token stacks — never to base64 fonts inlined into the board.
IG_FONT_BASE = "fonts/"
#: The font files the previews name, read off infographic_plan's own @font-face rules so the
#: publish list can never drift from what the frames request.
IG_FONT_FILES = tuple(re.findall(r'url\("([^"]+)"\)', IP._fonts("")))
#: THE NAVIGATION BLOCK (spec §9 amendment 7). Four pieces of furniture that belong to the
#: PAGE rather than to any one section — so they are never offered as a section's three
#: styles and, before this block existed, were never shown on a board at all. They are
#: rendered from `dist/kit-preview/`, which is the one built page carrying the whole kit, and
#: each one is BAKED: the dial, the strip and the sheet were pruned to the arrangement the
#: breeder picked on the contact board (2026-09-19), so what is shown is a statement of what
#: the page wears, not a menu. Per row: the component id, what it is, the width to show it
#: at, and where it mounts.
NAV_COMPONENTS = (
    ("page-dial", "PageDial — S2, the compact numbered strip, no ring", 1280,
     "Desktop only, 1024px and up: the 196px column beside the body, following the reader down the page."),
    ("section-strip", "SectionStrip — S2, filled tab chips", 375,
     "Below 1024px: the sticky chip rail pinned directly under the site header, outside <main>."),
    ("section-sheet", "SectionSheet — S2, the full-width Sections pill", 375,
     "Below 1024px: the bottom bar, with the full section list behind the Sections control."),
    ("page-nav", "PageNav — the breadcrumb + in-page TOC, the chip row picked in build 3", 768,
     "Below the hero, mounted by PageShell on every rebuilt page, and shown below 1024px — "
     "the dial is its desktop copy, so the two are never on screen together. The trail is "
     "suppressed here because BaseLayout already renders one above <main>."),
)
#: The navigation frames are shorter than a section preview: none of these is a stretch of
#: page, and a 520px frame around a 61px chip rail is mostly empty board.
NAV_H = 300
#: The dial and the sheet are only mounted at all on a page with six or more sections. One
#: number, and it is PageShell's — a board that promised a dial on a four-section page would
#: be promising furniture the shell refuses to render.
NAV_THRESHOLD = 6

# The board wears the SITE's palette, not a second one of its own: these are the values of
# src/styles/tokens.css (steel / brass / bone), so an arrangement judged in a preview iframe
# is judged against the same ground the real page will paint. Hex is spelled here because
# this file GENERATES a standalone artifact document — the no-hex rule is about src/, which
# has exactly one colour file, and an artifact cannot import it.
CSS = """
:root{--ground:#F4F1EA;--paper:#FFFFFF;--ink:#1B2430;--ink-2:#46566B;--ink-3:#5E6B7A;--line:#DAD6CC;--green:#1F3A52;--green-soft:#E4EAF1;--clay:#C9A227;--clay-ink:#A8861C;--clay-soft:#EFE3B4;--code-bg:#FAF8F3;--mark:#EFE3B4;--warn:#9A4A2A;--on-clay:#14202B}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ground:#14202B;--paper:#1F3A52;--ink:#F4F1EA;--ink-2:#E4EAF1;--ink-3:#8FA3B8;--line:#5B7C99;--green:#8FA3B8;--green-soft:#1F3A52;--clay:#C9A227;--clay-ink:#EFE3B4;--clay-soft:#1F3A52;--code-bg:#14202B;--mark:#A8861C;--warn:#EFE3B4;--on-clay:#14202B}}
:root[data-theme="dark"]{--ground:#14202B;--paper:#1F3A52;--ink:#F4F1EA;--ink-2:#E4EAF1;--ink-3:#8FA3B8;--line:#5B7C99;--green:#8FA3B8;--green-soft:#1F3A52;--clay:#C9A227;--clay-ink:#EFE3B4;--clay-soft:#1F3A52;--code-bg:#14202B;--mark:#A8861C;--warn:#EFE3B4;--on-clay:#14202B}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font:16px/1.6 "Source Sans 3",system-ui,-apple-system,Segoe UI,sans-serif}
.wrap{max-width:1120px;margin:0 auto;padding:36px 24px 96px}
header.masthead{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;padding-bottom:18px;border-bottom:2px solid var(--green);margin-bottom:24px}
.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--green);font-weight:600;margin:0 0 6px}
h1.title{font-family:"Fraunces",Georgia,serif;font-weight:700;font-size:clamp(26px,3.6vw,38px);line-height:1.1;margin:0;text-wrap:balance}
.meta{font-size:13px;color:var(--ink-3);text-align:right;line-height:1.5}
.pill{display:inline-block;border-radius:50px;padding:2px 9px;font-size:11px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;border:1px solid var(--line);background:var(--paper)}
section.sec{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:24px 28px 26px;margin:0 0 20px;min-width:0;overflow:hidden}
section.sec h2{font-family:"Fraunces",Georgia,serif;font-weight:700;font-size:22px;margin:0 0 10px;line-height:1.2}
.md p,.md li{max-width:72ch}.md table{border-collapse:collapse;width:100%;font-size:14px;margin:10px 0 14px;display:block;overflow-x:auto}
.md th{text-align:left;font-weight:600;color:var(--ink-2);font-size:12px;text-transform:uppercase;letter-spacing:.06em;border-bottom:2px solid var(--green);padding:6px 10px;white-space:nowrap}
.md td{padding:6px 10px;border-bottom:1px solid var(--line);vertical-align:top;font-variant-numeric:tabular-nums}
.md code{font:13px/1.5 ui-monospace,Menlo,monospace;background:var(--code-bg);padding:1px 5px;border-radius:4px}
.tree{font:13px/1.65 ui-monospace,Menlo,monospace;white-space:pre-wrap;margin:0;overflow-x:auto}
.hit{color:var(--warn);font-weight:600}
.opts{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px;margin:8px 0 6px}
.opt{border:1px solid var(--line);border-radius:8px;padding:8px;background:var(--paper);display:grid;gap:6px}
.opt img,.opt .nothumb{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:5px;border:1px solid var(--line);background:var(--code-bg);display:grid;place-items:center;font-size:12px;color:var(--ink-3)}
.opt.off{opacity:.55}.opt label{display:flex;gap:8px;align-items:center;font-size:13px;font-weight:600;cursor:pointer}
.opt .why{font-size:12px;color:var(--ink-3)}
.opt .pill{justify-self:start;text-transform:none;letter-spacing:0;background:var(--green-soft);border-color:var(--green);color:var(--ink-2)}
textarea.note{width:100%;min-height:52px;font:13px/1.5 "Source Sans 3",system-ui,sans-serif;border:1px solid var(--line);border-radius:6px;padding:8px;background:var(--ground);color:var(--ink)}
.slots{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}
.slot{border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:13px}.slot .st{font-weight:700}.slot .st.missing{color:var(--warn)}
#approve{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
button.btn{font:inherit;font-size:14px;font-weight:600;padding:10px 18px;border-radius:50px;border:1px solid var(--clay-ink);background:var(--clay-ink);color:var(--on-clay);cursor:pointer}
button.btn[disabled]{opacity:.5;cursor:default}
.status{font-size:13px;color:var(--ink-2)}
#approve .status:has(ul.missing){flex-basis:100%;color:var(--ink)}
.status ul.missing{margin:6px 0 0;padding-left:20px;line-height:1.7}.status ul.missing a{color:var(--clay-ink)}
fieldset[id^="choose-"],fieldset[id^="ig-"],div.opts[id^="choose-"]{scroll-margin-top:24px}
.vtag{font-size:11px;letter-spacing:.04em;text-transform:uppercase;border:1px solid var(--clay);border-radius:3px;padding:0 4px;margin-left:6px}
button:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid var(--clay);outline-offset:2px}
.kit .opt{gap:5px}
.kit .opt b{font-size:13px;font-weight:600}
.kit .opt .pill:first-child{justify-self:start;background:var(--paper);border-color:var(--line);color:var(--ink-3);text-transform:uppercase;letter-spacing:.06em}
@media (max-width:640px){header.masthead{grid-template-columns:1fr}.meta{text-align:left}section.sec{padding:18px 16px 20px}}
.howto{margin:0 0 18px;padding:10px 14px;border-left:3px solid var(--clay);background:var(--clay-soft);color:var(--ink);font-size:14px;border-radius:0 6px 6px 0}
fieldset.styles{border:1px solid var(--line);border-radius:8px;padding:10px 12px 14px;margin:8px 0 6px;background:var(--paper);min-width:0}
fieldset.styles legend{font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);padding:0 6px}
fieldset.styles.locked{background:var(--green-soft)}
fieldset.styles.locked legend{color:var(--green)}
p.refresh{margin:6px 0 0;font-size:12.5px;line-height:1.5;color:var(--ink-3)}
p.refresh b{color:var(--green);font-weight:600}


.style{border-top:1px dashed var(--line);padding:10px 0 4px}
.style:first-of-type{border-top:0}
.style label{display:flex;gap:8px;align-items:baseline;font-size:15px;font-weight:600;cursor:pointer}
.style label .why{font-weight:400;font-size:12px;color:var(--ink-3)}
.frames{display:flex;gap:10px;overflow-x:auto;max-width:100%;padding:8px 0 2px;align-items:flex-start}
.frame{flex:none;display:grid;gap:4px}
.frame span{font-size:11px;color:var(--ink-3);letter-spacing:.04em}
.frame iframe{border:1px solid var(--line);border-radius:6px;background:var(--paper);display:block}
.noprev{font-size:13px;color:var(--warn);margin:6px 0 0}
.lk{font-size:12px;font-weight:600;letter-spacing:.03em;white-space:nowrap}
.lk-ok{color:var(--green)}
.lk-wait{color:var(--clay-ink)}
.lk-bad{color:var(--warn)}
.lk-ext{color:var(--ink-3);font-weight:400}
.lk-none{font-size:13px;color:var(--ink-3);margin:4px 0 10px}
.lk-tot{font-size:14px;font-weight:600;color:var(--ink-2)}
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
    # `<!--` is escaped too: inside a <script>, an HTML comment opener followed later by
    # `<script` switches the parser into the double-escaped state, where `</script>` no
    # longer closes the block. `<\!--` is the same string to JS.
    return json.dumps(value).replace("</", "<\\/").replace("<!--", "<\\!--")


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


def vtag(is_verbatim):
    """The `verbatim` tag the outline hangs on a heading the migrated page wrote (rule 15).

    It sits in the tree rather than only in the verbatim block below because the tree is what
    the breeder reads to judge the page: a heading that cannot be reworded on a whim is a
    different kind of heading from one that can, and the outline is where that has to show."""
    return ' <span class="vtag">verbatim</span>' if is_verbatim else ""


def verbatim_block(slug, board):
    """Working rule 15's accounting, element by element: every entry of
    data/verbatim/<slug>.json badged CARRIED, CHANGED (with the reason) or DROPPED (with the
    reason). The record's `verbatim.changed` is the only input for the last two, so a board
    cannot show a reason the gate will not read, and an element with no row is carried by
    definition — which is what makes the count at the top of the block worth reading."""
    vpath = PB.ROOT / f"data/verbatim/{slug}.json"
    applies = json.loads((PB.ROOT / "data/verbatim/applies.json").read_text(encoding="utf-8"))
    if slug in (applies.get("excluded") or {}):
        why = applies["excluded"][slug]
        return (f"**Rule 15 does not reach this page.** {md(why if isinstance(why, str) else applies['excluded']['comment'])}")
    if not vpath.exists():
        return "_No verbatim set has been extracted for this page._"
    vset = json.loads(vpath.read_text(encoding="utf-8"))
    rows = {}
    for r in (board.get("verbatim") or {}).get("changed", []):
        kind = VSC.ROW_KIND_ELEMENT.get(r["kind"], r["kind"])
        rows[(kind, r.get("src") or r["old"])] = r
    out, tally = [], {"CARRIED": 0, "CHANGED": 0, "DROPPED": 0}
    for kind, old, src in VSC.elements(vset):
        r = rows.get((kind, src if kind == "alt" else old))
        if r is None:
            badge, detail = "CARRIED", ""
        elif not r.get("new"):
            badge, detail = "DROPPED", md(r["reason"])
        else:
            badge, detail = "CHANGED", f"→ **{md(r['new'])}** · {md(r['reason'])}"
        tally[badge] += 1
        label = f"{kind} · {md(src)}" if kind == "alt" else kind
        out.append([f"`{badge}`", label, md(old), detail or "—"])
    head = (f"**{tally['CARRIED']} carried · {tally['CHANGED']} changed · {tally['DROPPED']} dropped** "
            f"of {sum(tally.values())} elements in `data/verbatim/{esc(slug)}.json`. "
            "Rule 15 carries the migrated page's H1, its keyword H2/H3s, the first paragraph under each of "
            "them, its FAQ questions and every image alt, word for word. A row here is the record's own "
            "`verbatim.changed`, and `scripts/verbatim_set_check.py` proves every one of them on the built "
            "page after P5.")
    return head + "\n\n" + md_table(["", "Kind", "The migrated page's wording", "What happens to it"], out)


def outline_block(board, hits):
    """The whole outline as one tree, H1 included — read from all_headings() so the board
    shows the same H1 the gate judged, whether it came from a pick or the recommendation."""
    hit_by = {h["heading"]: h for h in hits}
    added = {(c["section"], c["heading"]) for c in board.get("outline_changes_since_stop2") or []}
    h1 = PB.all_headings(board)[0][1]
    lines = [f"H1  {esc(h1)}" + vtag(board.get("h1", {}).get("verbatim_heading")) + flag(h1, hit_by)]
    for s in board["sections"]:
        cta = f" · CTA×{s['cta']}" if s.get("cta") else ""
        # The span is the target of every section chip in blocks 4 and 5 (board_entities).
        lines.append(f'<span class="oanchor" id="{esc(BE.anchor_id(s["id"]))}">'
                     f"├─ H2 {s['n']:02d}  {esc(s['heading'])}{vtag(s.get('verbatim_heading'))}   [{s['category']} · {GROUP_SHORT[s['group']]} · {s['shape']} · {s['framework']} · {s['words']['min']}–{s['words']['max']}w{cta}]"
                     + flag(s["heading"], hit_by) + "</span>")

        def walk(nodes, depth):
            for n in nodes:
                new = "   [added since STOP 2 — block 3e]" if (s["id"], n["heading"]) in added else ""
                lines.append("│   " * depth + f"├─ H{n['level']} {esc(n['heading'])}{vtag(n.get('verbatim_heading'))}{new}" + flag(n["heading"], hit_by))
                walk(n["children"], depth + 1)
        walk(s["tree"], 1)
        for i, q in enumerate(s.get("questions", []), 1):
            lines.append(f"│   ├─ Q{i:02d} {esc(q)}" + flag(q, hit_by))
        for l in s["links"]["internal"]:
            lines.append(f"│   → {esc(l['anchor'])} → {esc(l['href'])}")
        for l in s["links"]["external"]:
            lines.append(f"│   ↗ {esc(l['anchor'])} → {esc(l['href'])}   [{esc(l['library_row'])}]")
    return "\n".join(lines)


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


#: The built kit preview: the only page that carries every component once, and therefore the
#: only honest source for a rendering of furniture no section owns.
KIT_PREVIEW = PB.DIST / "kit-preview" / "index.html"


def load_nav_previews():
    """The four navigation components, cut out of `dist/kit-preview/index.html`.

    The cut is `scripts/_kit_sections.py`'s, the same one the Design System artifact and the
    canvas use, so the board shows the markup the build emits rather than a second rendering
    of the same description. Absence is not an error for the same reason it is not one in
    `load_previews`: a board is often built before a build has run, and the block then says
    so in the board itself.

    The route's own `<h3>` caption is dropped — it is the preview page's chrome, not the
    component — and the document sprite is pasted back in when a block references it, because
    a srcdoc frame has no document to borrow a `<symbol>` from.

    THE STUB ANCHORS DO NOT COME WITH IT. The dial, the strip and the sheet point at
    `d-a`…`d-f`, which the preview renders once for the whole page and outside every section.
    Inside these frames those links therefore lead nowhere. That is a property of the frame,
    not of the component: what the block is showing is the furniture's SHAPE, and on a real
    page the shell hands all three the page's own section list."""
    if not KIT_PREVIEW.exists():
        return {"css": "", "blocks": {}}
    html = KIT_PREVIEW.read_text(encoding="utf-8")
    by_id = {s.component: s.inner for s in find_sections(html)}
    sprite = page_sprite(html)
    blocks = {}
    for cid, _label, _w, _where in NAV_COMPONENTS:
        inner = by_id.get(cid)
        if inner is None:
            continue
        inner = re.sub(r"<h3[^>]*>.*?</h3>\s*", "", inner, count=1, flags=re.S)
        blocks[cid] = (sprite + inner) if (sprite and uses_sprite(inner)) else inner
    return {"css": page_css(html), "blocks": blocks}


def changes_block(board):
    """Block 3e: the headings this board adds to the outline approved at STOP 2. The outline
    record is not edited (its approval hash covers all of it); the rows live on the board
    record, inside its hash, so approving the board approves them."""
    rows = board.get("outline_changes_since_stop2") or []
    by_id = {s["id"]: s for s in board["sections"]}
    table = []
    for c in rows:
        s = by_id.get(c["section"], {})
        node = PB.outline_change_node(board, c) or {}
        w = node.get("words") or {}
        table.append([f"{s.get('n', 0):02d} {md(s.get('heading', c['section']))}",
                      f"H{c.get('level', node.get('level', 3))} **{md(c['heading'])}**",
                      md(c.get("keyword") or "—"),
                      f"`{md(c['slot'])}`" if c.get("slot") else "—",
                      f"{w['min']}–{w['max']}" if w else "—",
                      md(c["reason"])])
    return (f"**{len(rows)} heading(s) added since the outline was approved at STOP 2.** "
            "The approved outline record is unchanged; these rows are part of this board, so "
            "approving the board approves them. Each new heading's only image is the infographic "
            "it names, and its words come out of its section's band (the page total is unchanged).\n\n"
            + md_table(["Section", "New heading", "Keyword", "Image slot", "Words", "Why"], table))


def navigation_block(board, nav):
    """Block 3c: the four pieces of in-page navigation this page wears, rendered.

    WHY IT IS ON EVERY BOARD AND WHY IT IS NOT A PICK. Three of the four were decided on the
    contact board and pruned to one arrangement each; the fourth is the chip row build 3
    picked. What is still open on any given page is whether the set is right FOR THAT PAGE —
    which is a sentence, not a radio — so the block ends in one note box, saved with the
    approval as `notes.navigation`.

    The six-section threshold is stated out loud, per page: below it PageShell renders none
    of the sticky three, and a board that showed them anyway would be describing a page that
    does not exist."""
    n = len(board["sections"])
    mounted = n >= NAV_THRESHOLD
    rows = []
    for cid, label, width, where in NAV_COMPONENTS:
        have = cid in nav["blocks"]
        frame = (f'<div class="frames"><div class="frame"><span>{width}px</span>'
                 f'<iframe title="{esc(label)} at {width} pixels wide" sandbox="" loading="eager" '
                 f'scrolling="auto" data-nav="{esc(cid)}" width="{width}" height="{NAV_H}" '
                 f'style="width:{width}px;height:{NAV_H}px"></iframe></div></div>'
                 if have else
                 '<p class="noprev">Not rendered yet — run <code>npm run build</code>.</p>')
        rows.append(f'<div class="style"><label><b>{esc(label)}</b></label>'
                    f'<p class="why">{esc(where)}</p>{frame}</div>')
    head = (f"All four mount on this page: it has {n} sections, and PageShell's threshold for the "
            f"dial, the strip and the sheet is {NAV_THRESHOLD}."
            if mounted else
            f"**Only the TOC mounts on this page.** It has {n} sections and PageShell renders the "
            f"dial, the strip and the sheet only at {NAV_THRESHOLD} or more — below that the pair is "
            "a second, shorter route to a list the reader can already see.")
    return (head + "\n\n<fieldset class=\"styles\"><legend>Navigation on this page</legend>"
            + "".join(rows) + "</fieldset>\n\n"
            "These four are shown, not offered: the dial, the strip and the sheet were picked on the "
            "contact board on 2026-09-19 and the losing arrangements are deleted from the kit, and the "
            "TOC is build 3's chip row. What is still open is whether the set suits THIS page — say so "
            "here and it is saved with the approval.\n\n"
            "<textarea class=\"note\" name=\"note-navigation\" "
            "placeholder=\"Navigation notes (optional) — saved with the approval\"></textarea>")


def load_previews(slug):
    """The cut style blocks for this slug, or an empty payload when none were cut yet.

    ABSENCE IS NOT AN ERROR here: a board is often built before the route has been rendered
    (a record with no styled section never needs one at all). The fieldset then says, in
    the board itself, that the renderings are missing and how to produce them — a silent
    blank frame would read as a style that renders to nothing."""
    p = PREVIEWS / (PB.slug_file(slug) + ".json")
    if not p.exists():
        return {"css": "", "blocks": {}, "names": {}, "images": {}}
    data = json.loads(p.read_text(encoding="utf-8"))
    data.setdefault("names", {})
    data.setdefault("images", {})
    return data


def style_fieldset(section, previews, locked=None):
    """The three rendered arrangements this section offers, as one radio group.

    The radio group is `pick-<section id>` — the SAME name a component option uses, because
    it is the same decision in the same place: what this section is. A section that offers
    styles offers them INSTEAD of a ledger component card, so the two can never both write
    the record's pick.

    Each style shows three frames (1280 / 768 / 375). The frames are filled at load from
    one copy of the blocks and one copy of the page CSS (see BLOCKS/PREVIEW_CSS in the
    board's script): a static `srcdoc` per frame would paste the whole kit stylesheet nine
    times per section, and the board is a committed file.

    `loading="eager"`, not lazy: the three frames sit in a horizontal scroller, so the 768
    and 375 ones are off to the right of the board's own column and a lazy frame would stay
    blank until the reader scrolled it in — which reads as a style that renders to nothing.

    `sandbox=""` grants the frame NOTHING, and the one thing that matters here is what it
    therefore withholds: `allow-forms`. A `form`-shaped section embeds the kit's enquiry
    form nine times, and without the flag a click on its submit button does nothing at all
    — no navigation, no POST to Formspree. (No script runs either, so the previews are
    static renderings; that is a consequence, not the reason.)"""
    sid = section["id"]
    pick = section["options"]["pick"]
    # Working rule 16: a re-boarded record carries every pick it already had for a section it
    # is not being re-asked about (PB.locked_picks). The radios are rendered DISABLED with the
    # carried answer checked — a disabled checked radio still matches the `:checked` selector
    # the approve button reads, so the answer is submitted and cannot be changed by accident,
    # which is the whole point of carrying it. The previews still render: the breeder is
    # entitled to see what they agreed to, not only to be told they agreed to it.
    carried = (locked or {}).get(sid)
    if carried:
        # A record whose own `options.pick` disagrees with the carried one is two answers to
        # one question, and quietly preferring either is the board telling the breeder they
        # decided something they did not. It is a record fault, so it stops the build.
        if pick and pick != carried:
            raise PB.BoardError(
                f"section {sid}: the record's pick is {pick!r} and the approval it is "
                f"carrying forward says {carried!r} — two answers to one question. Clear "
                "`options.pick` to re-ask it, or drop the row from `approval_previous.picks`.")
        pick = carried
    rows = []
    for style in section["styles"]:
        key = f"{sid}|{style}"
        name = previews["names"].get(key, "")
        have = key in previews["blocks"]
        frames = "".join(
            f'<div class="frame"><span>{w}px</span>'
            f'<iframe title="{esc(style)} at {w} pixels wide" sandbox="" loading="eager" '
            f'scrolling="auto" data-block="{esc(key)}" width="{w}" height="{PREVIEW_H}" '
            f'style="width:{w}px;height:{PREVIEW_H}px"></iframe></div>'
            for w in PREVIEW_W) if have else (
            '<p class="noprev">Not rendered yet — run <code>npm run build</code>, then '
            '<code>python3 scripts/build_board_previews.py &lt;slug&gt;</code>.</p>')
        checked = " checked" if pick == style else ""
        rows.append(
            f'<div class="style"><label><input type="radio" name="pick-{esc(sid)}" '
            f'value="{esc(style)}"{checked}{" disabled" if carried else ""}> {esc(style)}'
            + (f' <span class="why">{esc(name)}</span>' if name else "")
            + f'</label><div class="frames">{frames}</div></div>')
    legend = (f'Locked — {esc(carried)}, carried from the previous approval'
              if carried else f'Pick one arrangement for {esc(section["heading"])}')
    return (f'<fieldset class="styles{" locked" if carried else ""}" id="{esc(pick_anchor(sid))}"><legend>{legend}</legend>'
            + "".join(rows) + "</fieldset>")


def refresh_line(section):
    """The section's recorded refresh delta, as one muted line under its options.

    Working rule 16 puts a delta on every section, and a delta the breeder cannot see is a
    decision taken on their behalf. It matters most under a LOCKED fieldset: a carried pick
    says "you already chose this arrangement", and the note beside it says what has changed
    about the section since — which is the difference between carrying an answer forward and
    assuming one. A section with no delta prints nothing rather than an empty row."""
    r = section.get("refresh")
    if not r:
        return ""
    return (f'<p class="refresh"><b>Refresh</b> · {esc(r["axis"])} — {esc(r["note"])}</p>')


def picked_sections(board, ledger=None, slug=None):
    """Every section id the approve button must see an answer for.

    A styled section owes its style. A section with no styles owes its ledger component, as
    it always has — but only if the board actually SHOWS it one: a `standard` section is
    offered nothing by design, and a section whose pool comes back empty is shown nothing
    either. Demanding an answer to a question the board never asked is a board nobody can
    approve, which is worse than one that guesses.

    `ledger`/`slug` are optional so a one-argument call still works; without them the
    emptiness test falls back to the `standard` rule alone."""
    out = []
    for s in board["sections"]:
        if s.get("styles"):
            out.append(s["id"])
            continue
        if s.get("component"):
            continue          # a city section: picked on the city canvas, nothing to ask here
        if s["shape"] == "standard":
            continue
        if ledger is not None and not s["options"]["pick"]:
            cands, _ = PB.candidates_for(s["shape"], ledger, slug)
            if not cands:
                continue
        out.append(s["id"])
    return out


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


LINK_HEADERS = ["Target", "Anchor", "Purpose", "Resolves", "Source"]
# What a row's `why` says when it says nothing: the link is the outline's own, not one the
# migrated page carried. Spelled out rather than left blank so a breeder re-approving a
# board can tell a link they already had from a link they are being asked to add.
LINK_SOURCE_NEW = "new in this outline"


def route_of(href):
    """An internal href → the route it lands on: query and fragment dropped, one leading and
    one trailing slash. `/x`, `/x/`, `/x/?a=1` and `/x/#faq` are one route, and the board must
    not report three of them dead because the record spelled them three ways."""
    path = urlsplit(str(href or "")).path.strip()
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path += "/"
    return re.sub(r"/{2,}", "/", path)


def load_routes():
    """What a route can be checked against: the routes the last build actually wrote, and the
    routes the page map plans.

    `built` is None — not an empty set — when there is no dist/ at all, because "nothing is
    built" and "this page is not built" have to read differently: with no build on disk the
    board falls back to the page map and says nothing about what a build would emit."""
    built = None
    if PB.DIST.exists():
        built = set()
        for p in PB.DIST.rglob("index.html"):
            rel = p.parent.relative_to(PB.DIST).as_posix()
            built.add("/" if rel == "." else route_of("/" + rel))
    mapped = set()
    pm = PB.ROOT / "data" / "page-map.json"
    if pm.exists():
        for row in json.loads(pm.read_text(encoding="utf-8")).get("pages", []):
            if row.get("url"):
                mapped.add(route_of(row["url"]))
    return {"built": built, "mapped": mapped}


def resolve_internal(href, routes):
    """(text, css class) for one internal target. A route the build wrote resolves; a route
    only the page map knows is planned but unbuilt; a route neither knows is dead, and a dead
    internal link is the one thing on this block that has to be rewritten before approval."""
    if href.strip().startswith("#"):
        # A same-page fragment: pageboard.gate_findings checks it names a section id of this
        # record (`links-fragment-dead`); there is no route to resolve.
        return ("yes", "lk-ok")
    r = route_of(href)
    built, mapped = routes["built"], routes["mapped"]
    if built is None:
        return ("yes", "lk-ok") if r in mapped else ("no (dead)", "lk-bad")
    if r in built:
        return ("yes", "lk-ok")
    if r in mapped:
        return ("no (not built yet)", "lk-wait")
    return ("no (dead)", "lk-bad")


def link_rows(section, routes, typed=False):
    """Every link row of one section, internal first, each as the four table cells.

    The record gives an internal row no purpose field of its own, so the purpose IS its
    placement rule: `nav: true` is a navigational link, anything else is required by the
    schema to start a sentence. An external row carries its library row, which is the
    purpose the link was admitted for."""
    rows = []
    for l in section["links"]["internal"]:
        text, cls = resolve_internal(l["href"], routes)
        rows.append([f"`{md(l['href'])}`", md(l["anchor"]),
                     "nav link" if l.get("nav") else "in copy, sentence start",
                     f'<span class="lk {cls}">{esc(text)}</span>',
                     md(l.get("why") or LINK_SOURCE_NEW)] + ([md(l.get("anchor_type") or "⚠ none")] if typed else []))
    for l in section["links"]["external"]:
        domain = urlsplit(l["href"]).netloc or "unknown host"
        rows.append([f"`{md(l['href'])}`", md(l["anchor"]), md(l["library_row"]),
                     f'<span class="lk lk-ext">external · {esc(domain)}</span>',
                     md(l.get("why") or LINK_SOURCE_NEW)] + ([md(l.get("anchor_type") or "⚠ none")] if typed else []))
    return rows


def links_block(board, routes):
    """Working rule 12: every internal and external link the page will carry, per section and
    then once for the page. The page table is deduplicated by target, because a link repeated
    in four sections is one destination with four placements — and the sections column is what
    tells the breeder where each one is said."""
    out, seen, order = ["## Links — every link this page will carry"], {}, []
    # System-gaps Task 5: the anchor-type column and the diversity line show on a new-family
    # page, or on any record that already types its anchors — never on the twelve built boards.
    typed = LD.shows_anchor_types(board)
    headers = LINK_HEADERS + ["Anchor type"] if typed else LINK_HEADERS
    for s in board["sections"]:
        out.append(f"### {s['n']:02d} · {md(s['heading'])}")
        rows = link_rows(s, routes, typed)
        out.append(md_table(headers, rows) if rows
                   else '<p class="lk-none">No links in this section.</p>')
        for l in s["links"]["internal"] + s["links"]["external"]:
            key = l["href"]
            if key not in seen:
                seen[key] = {"row": l, "kind": "external" if "library_row" in l else "internal",
                             "anchors": [], "sections": [], "types": []}
                order.append(key)
            e = seen[key]
            if l["anchor"] not in e["anchors"]:
                e["anchors"].append(l["anchor"])
            if (l.get("anchor_type") or "⚠ none") not in e["types"]:
                e["types"].append(l.get("anchor_type") or "⚠ none")
            label = f"{s['n']:02d} {s['heading']}"
            if label not in e["sections"]:
                e["sections"].append(label)
    page_rows = []
    for key in order:
        e = seen[key]
        l = e["row"]
        if e["kind"] == "internal":
            text, cls = resolve_internal(l["href"], routes)
            purpose = "nav link" if l.get("nav") else "in copy, sentence start"
            cell = f'<span class="lk {cls}">{esc(text)}</span>'
        else:
            purpose = md(l["library_row"])
            cell = f'<span class="lk lk-ext">external · {esc(urlsplit(l["href"]).netloc or "unknown host")}</span>'
        page_rows.append([f"`{md(key)}`", " / ".join(md(a) for a in e["anchors"]),
                          purpose, cell, md(l.get("why") or LINK_SOURCE_NEW),
                          ", ".join(md(x) for x in e["sections"])]
                         + ([" / ".join(md(t) for t in e["types"])] if typed else []))
    n_int = sum(1 for k in order if seen[k]["kind"] == "internal")
    n_ext = len(order) - n_int
    placements = sum(len(s["links"]["internal"]) + len(s["links"]["external"]) for s in board["sections"])
    out.append("### Every link on this page")
    out.append(md_table(LINK_HEADERS + ["Sections"] + (["Anchor type"] if typed else []), page_rows) if page_rows
               else '<p class="lk-none">No links on this page.</p>')
    out.append(f'<p class="lk-tot">Totals: {n_int} internal · {n_ext} external</p>')
    if typed:
        out.append(f'<p class="lk-tot">{esc(LD.diversity_line(board))}</p>')
    out.append(f"Deduplicated by target: {len(order)} distinct target(s) across {placements} placement(s). "
               "An internal target that resolves to _no_ is either a page this cluster has not built yet or a "
               "dead route — either way the board cannot be built against it as written.")
    return "\n\n".join(out)


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


REFUSAL_LINE = "Approval will be refused until the FAIL rows in 7b are fixed."
# Scoped to block 7b, and emitted only with it: a rule in CSS would change every built board.
RULES_CSS = ('<style>.rules{display:grid;grid-template-columns:minmax(0,1fr);gap:6px;margin:4px 0 10px}'
             '.rules .rule{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;font-size:14px;min-width:0}'
             '.rules .rule code{font-size:13px;overflow-wrap:anywhere}'
             '.rules .rule .msg{flex:1 1 20ch;min-width:0;overflow-wrap:anywhere}'
             '.rules .pill.fail{color:var(--warn);border-color:var(--warn);font-weight:700}'
             '.rules .pill.warn{color:var(--ink-2)}.rules .later{font-size:12px;color:var(--ink-3)}'
             '.rules-refused{color:var(--warn);font-weight:600;font-size:14px}</style>')


BACKTICK = re.compile(r"`([^`]+)`")


def rule_findings(board, ont):
    """What approval will say. board_approve runs the rules on the record AS APPROVED, where a
    rule that only WARNs on a draft FAILs, so 7b runs them the same way. `image-pick-missing`
    is left out: the approve button collects those picks, and the record cannot carry them
    before it does."""
    b = json.loads(json.dumps(board))
    b["meta"]["status"] = "approved"
    return ([f for f in PB.FR.findings(b, ont) if f[0] != "image-pick-missing"]
            + h1_variant_warnings(b, ont))


def h1_variant_warnings(b, ont):
    """The H1 is picked on the board, after 7b was rendered, so a variant that repeats a
    heading would pass here and be refused at approval. One WARN row per such variant: a WARN,
    because it refuses only IF picked, and the refusal line is kept for what WILL refuse given
    the current pick (or the recommendation the button starts on). Only while the rule itself
    runs, so a test that swaps FR.CHECKS sees exactly its own findings."""
    if PB.FR.outline_heading_repeat not in PB.FR.CHECKS:
        return []
    h1 = b.get("h1") or {}
    variants = h1.get("variants") or []
    current = h1.get("pick") if h1.get("pick") is not None else h1.get("recommended")
    base = {m for _, _, m in PB.FR.outline_heading_repeat(b, ont)}
    out = []
    for i, text in enumerate(variants):
        if i == current:
            continue
        v = json.loads(json.dumps(b))
        v["h1"]["pick"] = i
        new = [m for _, sev, m in PB.FR.outline_heading_repeat(v, ont) if sev == "FAIL" and m not in base]
        if new:
            out.append(("outline-heading-repeat", "WARN",
                        f"H1 variant {i + 1} {text!r}, if picked, is refused at approval: " + "; ".join(new)))
    return out


def code_spans(msg):
    """Escape first, then turn `inline code` into <code>: a backtick is never escaped, and
    nothing inside the span can open a tag once the text is escaped."""
    return BACKTICK.sub(r"<code>\1</code>", esc(msg))


def rules_block(findings):
    """Block 7b: every family_rules finding as a row, and whether approval will be refused.
    Build-gate ids (family_rules.APPROVAL_EXEMPT) can only pass after approval, so they are
    shown with that note and never announce a refusal."""
    if not findings:
        return RULES_CSS + '<p class="rules-pass">All new-page rules pass.</p>', False
    rows, refused = [], False
    for check, sev, msg in findings:
        exempt = check in PB.FR.APPROVAL_EXEMPT
        refused = refused or (sev == "FAIL" and not exempt)
        later = ' <span class="later">checked at build, after the image is approved</span>' if exempt else ""
        rows.append(f'<div class="rule"><span class="pill {"fail" if sev == "FAIL" else "warn"}">{esc(sev)}</span>'
                    f'<code>{esc(check)}</code><span class="msg">{code_spans(msg)}{later}</span></div>')
    return RULES_CSS + f'<div class="rules">{"".join(rows)}</div>', refused


def signature_sections(board, ledger=None, slug=None, ig_plan=None):
    """Every pick id the approve button refuses to leave empty: the sections, the image
    slots, and (project 5 boards) the infographic styles, from PB.ig_slots_required — the
    helper board_approve.py re-checks with. Original-photo slots (`og:<slot>`) are never in
    it — block 7d is a use/swap/skip proposal, not a required decision. `ig_plan`: PB.ig_plan(), if held."""
    return (picked_sections(board, ledger, slug) + IR.slots_needing_pick(board)
            + PB.ig_slots_required(board, ig_plan))


BLOCK2_LABELS = (("h1", "H1"), ("meta-title", "title tag"), ("meta-description", "meta description"))


def pick_anchor(pick_id):
    """The page id the refusal links a missing pick to: block 6's control for a section,
    block 7c's fieldset for `ig:<slot>`, block 7's fieldset for `img:<slot>` (written by
    image_rules._slot_html), block 7d's row for `og:<slot>`, block 2's radio group for the
    H1 and the meta pair."""
    if pick_id.startswith("ig:"):
        return "ig-" + pick_id[3:]
    if pick_id.startswith("og:"):
        return "og-" + pick_id[3:]
    if pick_id.startswith(IR.PICK_PREFIX):
        return "img-" + pick_id[len(IR.PICK_PREFIX):]
    return "choose-" + pick_id


def signature_labels(board, ledger=None, slug=None, ig_plan=None):
    """{pick id: {n, section, label, anchor}} for every id signature_sections() returns, plus
    the H1 and the meta pair — what the approve refusal says for each pick still open.

    `n` is the section number as block 3 prints it (two digits); a slot is charged to the
    section that owns it — an `ig:` slot to its infographic-plan section, an `img:` slot to
    the section image_candidates.iter_slots() walks it under. The H1 and meta radios are
    block 2's, so their `n` is "2" (one digit, so it never reads as section 02)."""
    by_id = {s["id"]: s for s in board["sections"]}
    owner = {}
    if PB.FR.applies(board):
        plan = PB.ig_plan(board) if ig_plan is None else ig_plan
        owner.update({"ig:" + p["slot"]: by_id.get(p["section"]) for p in plan})
        owner.update({"og:" + o["slot"]: by_id.get(o["section"])
                      for o in OS.propose(board, root=PB.ROOT)})
    for s, _n, img in IC.iter_slots(board):
        owner.setdefault(IR.PICK_PREFIX + img["slot"], s)
    out = {}
    for pid in signature_sections(board, ledger, slug, ig_plan):
        if pid.startswith("ig:"):
            sec, label = owner.get(pid), f"infographic style ({pid})"
        elif pid.startswith(IR.PICK_PREFIX):
            sec, label = owner.get(pid), f"image ({pid})"
        elif pid.startswith("og:"):          # never required today; labelled if one becomes so
            sec, label = owner.get(pid), f"original photo ({pid})"
        else:
            sec = by_id.get(pid)
            label = "component style" if sec and sec.get("styles") else "component"
        out[pid] = {"n": f"{sec['n']:02d}" if sec else "",
                    "section": sec["heading"] if sec else pid,
                    "label": label, "anchor": pick_anchor(pid)}
    for pid, label in BLOCK2_LABELS:
        out[pid] = {"n": "2", "section": "H1 and meta", "label": label, "anchor": pick_anchor(pid)}
    return out


def infographic_docs(plan):
    """{"<slot>|<style>": the standalone preview document} for block 7c's frames, rendered
    with IG_FONT_BASE so the fonts resolve beside the published board. One copy per style;
    the board's script pastes it into that style's three frames."""
    tokens = IP.load_tokens(PB.ROOT)
    return {f"{p['slot']}|{st['id']}": IP.render_preview(p, st["id"], p["facts"], tokens,
                                                          font_base=IG_FONT_BASE)
            for p in plan for st in p["styles"]}


def infographic_block(board, carried=None, plan=None):
    """Block 7c: per planned slot, its heading, IG type and why, and the three styles as one
    radio group `pick-ig:<slot>` (values plate / ruled / card), each style rendered at the
    three PREVIEW_W widths in srcdoc frames filled from IG_DOCS by the board's script.
    `carried` (PB.locked_picks) pre-checks a style answered on an earlier approval; `plan`
    is the PB.ig_plan() render() already made."""
    carried = carried or {}
    plan = PB.ig_plan(board) if plan is None else plan
    intro = ("Each infographic sits **beside the H2's existing photo**, never instead of it "
             "(working rule 11: every served image keeps its place, file and alt). Pick one "
             "style per slot; the same content is set three ways on the same tokens. "
             "A style you picked before stays selected; check it if the infographic's type "
             "changed. `python3 scripts/infographic_plan.py " + md(PB.slug_file(board["meta"]["slug"]))
             + "` prints the same plan.")
    if not plan:
        return intro + "\n\nNo section needs an infographic: no heading matched an IG trigger."
    table = md_table(["Section", "Heading", "IG type", "Why it triggered"],
                     [[md(p["section"]), md(p["node"]),
                       md(f"{p['ig']} {IP.IG_NAMES.get(p['ig'], '')}"), md(p["why"])]
                      for p in plan])
    out = [intro, table]
    for p in plan:
        slot = p["slot"]
        pending = PB.ig_pending(board, slot)
        rows = []
        for st in p["styles"]:
            key = f"{slot}|{st['id']}"
            frames = "".join(
                f'<div class="frame"><span>{w}px</span>'
                f'<iframe title="{esc(st["label"])} at {w} pixels wide" sandbox="allow-same-origin" '
                f'loading="eager" scrolling="auto" data-ig="{esc(key)}" width="{w}" height="{PREVIEW_H}" '
                f'style="width:{w}px;height:{PREVIEW_H}px"></iframe></div>' for w in PREVIEW_W)
            rows.append(f'<div class="style"><label><input type="radio" name="pick-ig:{esc(slot)}" '
                        f'value="{esc(st["id"])}"'
                        f'{" checked" if carried.get("ig:" + slot) == st["id"] else ""}> '
                        f'{esc(st["label"])}</label>'
                        f'<div class="frames">{frames}</div></div>')
        legend = (f"Optional — {esc(slot)}" if pending else f"Pick one style for {esc(slot)}")
        out.append(f"### {md(slot)} · {md(p['ig'])} {md(IP.IG_NAMES.get(p['ig'], ''))}\n\n"
                   f"**Heading:** {md(p['node'])}  \n**Why:** {md(p['why'])}"
                   + (f'\n\n<p class="rules-refused">{esc(pending)}</p>' if pending else "")
                   + f'\n\n<fieldset class="styles" id="{esc(pick_anchor("ig:" + slot))}"><legend>{legend}</legend>{"".join(rows)}</fieldset>')
    return "\n\n".join(out)


def og_block(board, carried=None):
    """Block 7d: original_slots' proposal table (4–5 of the site's real photos on the
    best-suited H2/H3s; the breeder's ruling q06, 2026-10-02), then per slot a radio group
    `pick-og:<slot>` (use / swap / skip — PB.V2_PICKS) and a note `note-og:<slot>` for
    the photo a swap should bring in. Not in the approve signature: a slot left blank is
    allowed. `carried` (PB.locked_picks) pre-checks an answer from an earlier approval."""
    carried = carried or {}
    text = OS.block(board, PB.ROOT)
    if text.startswith("### "):          # the section title already says "7d. Original photos"
        text = text.split("\n", 1)[1].lstrip("\n")
    rows = []
    for o in OS.propose(board, root=PB.ROOT):
        slot = esc(o["slot"])
        radios = "".join(
            f' <label><input type="radio" name="pick-og:{slot}" value="{v}"'
            f'{" checked" if carried.get("og:" + o["slot"]) == v else ""}> {v}</label>'
            for v in PB.V2_PICKS["og:"])
        rows.append(f'<div class="ogpick" id="{esc(pick_anchor("og:" + o["slot"]))}">'
                    f'<b>{slot}</b> <span class="why">{esc(o["photo"])}</span>{radios}'
                    f'<textarea class="note" name="note-og:{slot}" placeholder="Swap: which '
                    f'original photo instead? (optional)"></textarea></div>')
    return (text + "\n\n**Use, swap or skip each slot** — optional; a slot left blank is "
            "decided later.\n\n" + f'<div class="ogpicks">{"".join(rows)}</div>')


def render(board, ont, ledger, live, thumbs, slug, previews=None, routes=None, nav=None, images=None,
           intake=None):
    previews = previews if previews is not None else {"css": "", "blocks": {}, "names": {}, "images": {}}
    nav = nav if nav is not None else {"css": "", "blocks": {}}
    routes = routes if routes is not None else load_routes()
    hits = PB.header_hits(board, live)          # exactly what the gate will fail on
    qhits = PB.faq_hits(board, live)            # and what it will warn on
    d = PB.distribution(board)
    auth = PB.authorization_check(board, ont)
    approved = PB.approval_matches(board)
    m = board["meta"]
    parts = []

    # Block 0: the page's starting state, read from the files by scripts/page_intake.py —
    # the brief's target block, where the mode is found by looking and never assumed. Only
    # when the caller passes one, so a board rendered in a test stays exactly as it was.
    # Every key and value goes through md(): an H1 or a data row is text from a file, and a
    # pipe, an asterisk or a `</script>` in it must show literally, not end the block.
    if intake is not None:
        parts.append(("0. Intake — found by looking", PI.render_md(intake, cell=md)
                      + "\n\nRead from `data/locations.json`, `data/page-map.json`, the record, "
                        "the built page and its sitemap by `python3 scripts/page_intake.py "
                      + esc(slug) + "`. Nothing here is typed by hand."))

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

    # Board v2 blocks ride on project 5 boards only, so the twelve built boards render
    # byte-for-byte as before (tests/py/test_family_rules_on_board.py).
    new_family = PB.FR.applies(board)
    # Block 7c's plan, made ONCE (with its facts) and handed to the block, the frames and the
    # approve signature. A record fault in it is a PB.BoardError, which main() reports.
    ig_plan = PB.ig_plan(board, PB.ROOT) if new_family else []
    if new_family:
        parts.append(("1b. How Google reads this page", SR.block(board)))

    h1, ms = board["h1"], board["meta_set"]
    picked = h1["pick"] if h1["pick"] is not None else h1["recommended"]
    # The board must star the same pair the gate and the build will read, so the fallback
    # is PB.meta_pick()'s and not a second copy of it. It returns the STRINGS; the radio
    # group needs their index, and a board carrying one string twice is degenerate anyway.
    mt_s, md_s = PB.meta_pick(board)
    mt, mdn = ms["titles"].index(mt_s), ms["descriptions"].index(md_s)
    parts.append(("2. H1 and meta", "\n".join([
        f'<span class="oanchor" id="{pick_anchor("h1")}"></span>**H1** — the page\'s own promise', "",
        radio_list("h1", h1["variants"], h1["recommended"], picked), "",
        f'<span class="oanchor" id="{pick_anchor("meta-title")}"></span>'
        f"**Title tag** — ceiling {PB.title_ceiling(slug)} characters", "",
        radio_list("meta-title", ms["titles"], ms["recommended"]["title"], mt), "",
        f'<span class="oanchor" id="{pick_anchor("meta-description")}"></span>'
        f"**Meta description** — band {PB.DESC_MIN}–{PB.DESC_MAX} characters", "",
        radio_list("meta-description", ms["descriptions"], ms["recommended"]["description"], mdn),
    ])))

    parts.append(("3. Outline", f"<pre class=\"tree\">{outline_block(board, hits + qhits)}</pre>\n\n"
                  + (f"**{len(hits)} heading(s) collide with a live page.** Rewrite them before approving; "
                     "the gate fails on any." if hits else
                     "No heading collides with a live page (exact, species-template or 5-word shingle).")
                  + (f"\n\n{len(qhits)} FAQ question(s) repeat a live heading — a warning, not a refusal."
                     if qhits else "")
                  # Working rule 12 rides with the outline rather than in a block of its own:
                  # the links ARE part of the shape of the page, and the reader who has just
                  # read the tree is the reader who can judge where each one is said.
                  + "\n\n" + links_block(board, routes)))

    # Straight after the outline, because it is the outline audited: the tree says what the
    # page will be headed and this says which of those headings are not the writer's to choose.
    parts.append(("3a. Verbatim set", verbatim_block(slug, board)))

    # After the outline, because the question it asks — is this the right furniture for this
    # page — is one a reader can only answer once they have seen the page's shape.
    parts.append(("3c. Navigation on this page", navigation_block(board, nav)))
    # The breeder's question (2026-10-03): which areas of the city is this page targeting?
    # Straight after the page's furniture, before the image plan; project 5 boards only.
    if new_family:
        parts.append(("3d. Neighbourhoods", NB.block(board)))
    # Breeder q08 (2026-10-02): headings added after STOP 2 are shown as changes, not slipped
    # into the tree. Only a board that records one shows the block.
    if board.get("outline_changes_since_stop2"):
        parts.append(("3e. Changed since STOP 2", changes_block(board)))

    parts.append(("3b. Image plan", image_plan_table(board)
                  + "\n\nEvery image slot the outline plans. Infographic prompts are the generation pack; "
                    "photo prompts say what the photo has to show. Page-level files and alts are in block 7."))

    # The four optional types get a column only where they mean something: on a new-family
    # page (where family_rules requires them) or on any board that already uses one.
    kgroups = BE.group_keywords(board)
    ktypes = [k for k in PB.ALL_KEYWORD_TYPES
              if k in PB.KEYWORD_TYPES or new_family or d["totals"][k]]
    rows = [[md(r["section"])] + [r[k] for k in ktypes] + [f"{r['words_min']}–{r['words_max']}"] for r in d["rows"]]
    t = d["totals"]
    rows.append(["**totals**"] + [t[k] for k in ktypes] + [f"{t['words_min']}–{t['words_max']}"])
    c = d["h_counts"]
    why_rows = [[f"{s['n']:02d} {md(s['heading'])}", md(s["group"]), md(s["framework"]), md(s["why"]), md_with_urls(s["why_source"])]
                for s in board["sections"]]
    parts.append(("4. Distribution", md_table(["Section"] + [PB.KEYWORD_LABELS[k] for k in ktypes] + ["Words"], rows)
                  + f"\n\nHeadings: H1 {c['h1']} · H2 {c['h2']} · H3 {c['h3']} · H4 {c['h4']} · H5 {c['h5']} · H6 {c['h6']}. Counts are ceilings, not floors."
                  + "\n\n**Every keyword, by type** — a section number jumps to that section in block 3.\n\n"
                  + BE.keywords_html(kgroups, show_empty=PB.OPTIONAL_KEYWORD_TYPES if new_family else ())
                  + "\n\n**Why each section is here**\n\n"
                  + md_table(["Section", "Group", "Framework", "Why", "Source"], why_rows)))

    # parity build Task 18: CAG §7a's ours-vs-top-5 table, on a new-family page only, so the
    # twelve built boards render byte-for-byte as before.
    if new_family:
        kt = KM.table(board)
        parts.append(("4b. Keyword metrics",
                      f"Primary keyword **{md(kt['primary_keyword'])}** against the first five "
                      f"unblocked competitor pages, over the board's {kt['terms']} keyword terms. "
                      f"{md(KM.CAPTION)} `python3 scripts/keyword_metrics.py "
                      f"{md(slug)}` prints the same table.\n\n"
                      + md_table(KM.COLUMNS, [[md(c) for c in KM.cells(r)] for r in kt["rows"]])))
        parts.append(("4c. Term density against competitors", TD.table(board, ont)))
        parts.append(("4d. FAQ placement", FL.block(board)))
    ent_md = (BE.entities_html(BE.group_entities(board, ont))
              + (f"\n\n**BLOCKED referenced: {', '.join(md(e) for e in auth['blocked'])}.** The board cannot be approved." if auth["blocked"] else "")
              + (f"\n\nPROPOSED (need a source): {', '.join(md(e) for e in auth['proposed'])}." if auth["proposed"] else ""))
    parts.append(("5. Entities", ent_md))
    # Straight after the entities, because it is their mirror: what the competitors carry
    # (phrases and ontology entities) that this board does not.
    if new_family:
        parts.append(("5c. What competitors say that we do not", TG.block(board, ont)))

    parts.append(("5b. The kit", f'<div class="opts kit">{"".join(kit_cards(board, ledger, thumbs, slug))}</div>'
                  "\n\nThe page-level tuple, for reading. Picks happen in block 6; a shell that is wrong here is "
                  "a record edit, not a radio."))

    # The picks a re-boarded record carries forward, shown answered and locked (working rule 16).
    locked = PB.locked_picks(board)
    opt_html = []
    for s in board["sections"]:
        if s.get("styles"):
            # A styled section is picked by ARRANGEMENT, not by ledger shell: the fieldset
            # replaces the option cards so only one control ever writes picks[<id>].
            opt_html.append(
                f"### {s['n']:02d} · {md(s['heading'])} <span class=\"pill\">{md(s['shape'])}</span>\n\n"
                + style_fieldset(s, previews, locked)
                + refresh_line(s)
                + f"\n<textarea class=\"note\" name=\"note-{s['id']}\" placeholder=\"Note for this section (optional)\">{esc(s['options']['note'])}</textarea>")
            continue
        if s.get("component"):
            # A city section renders the component its city's design pass picked
            # (data/design/city-picks/<slug>.json). The City kit takes no style, so no trio is
            # offered: shown, never offered — a radio here would be a choice the build ignores.
            cards = [f'<div class="opt"><div class="nothumb">{esc(s["component"])}</div>'
                     f'<span class="why">picked in the city component design pass — nothing to pick here</span></div>']
        elif s["shape"] == "standard":
            dflt = standard_default(s, board)
            cards = [f'<div class="opt"><div class="nothumb">{esc(dflt)}</div>'
                     f'<span class="why">the default a standard section gets — nothing to pick</span></div>']
        else:
            cards = option_cards(s, ledger, slug, thumbs)
        # Only the option-card branch asks a question, so only it carries the anchor the
        # approve refusal links a missing component pick to.
        opts_id = (f' id="{esc(pick_anchor(s["id"]))}"'
                   if not s.get("component") and s["shape"] != "standard" else "")
        opt_html.append(f"### {s['n']:02d} · {md(s['heading'])} <span class=\"pill\">{md(s['shape'])}</span>\n\n<div class=\"opts\"{opts_id}>{''.join(cards)}</div>\n"
                        + refresh_line(s)
                        + f"<textarea class=\"note\" name=\"note-{s['id']}\" placeholder=\"Note for this section (optional)\">{esc(s['options']['note'])}</textarea>")
    parts.append(("6. Component options", "\n\n".join(opt_html) or "_No sections._"))

    slots = "".join(
        f'<div class="slot"><b>{esc(a["slot"])}</b> · {esc(a["kind"])} · {a["w"]}×{a["h"]} · {"required" if a["required"] else "optional"}'
        f'<br><span class="st {esc(a["status"])}">{esc(a["status"])}</span>{(" · " + esc(a["file"])) if a["file"] else ""}'
        f'{("<br><span class=" + chr(34) + "why" + chr(34) + ">alt: " + esc(a["alt"]) + "</span>") if a.get("alt") else ""}</div>'
        for a in board["assets"])
    parts.append(("7. Images & styles", f'<div class="slots">{slots}</div>' + IR.board_block(board, images)))

    # 7b only on the pages the new-page rules bind, so the twelve built boards render
    # byte-for-byte as they did before these rules reached the board.
    refused = False
    if PB.FR.applies(board):
        rules_html, refused = rules_block(rule_findings(board, ont))
        parts.append(("7b. Rules for new pages", rules_html))
        parts.append(("7c. Infographics", infographic_block(board, locked, ig_plan)))
        parts.append(("7d. Original photos", og_block(board, locked)))

    status = ("Approved as it stands." if approved else
              REFUSAL_LINE if refused else "Connecting to the board database…")
    approve = (f'<div id="approve"><button class="btn" id="approve-btn" disabled>Approve this board</button>'
               f'<span class="status" id="approve-status" role="status" aria-live="polite">{status}</span></div>')
    # The status span is rewritten by the database script below, so a refusal is also said
    # where no script touches it.
    refusal_note = f'\n\n<p class="rules-refused">{REFUSAL_LINE}</p>' if refused and not approved else ""
    parts.append(("8. Approve", approve + refusal_note + "\n\nWrites your H1 choice, picks, notes and the record hash to the board database. Build refuses to start without it; any later edit to the record clears it."))

    blocks = "".join(f'<script type="text/markdown" data-title="{esc(t)}">\n{b}\n</script>\n' for t, b in parts)
    record_hash = PB.record_hash(board)
    # Block 7c's infographic frames: one standalone document per slot|style, pasted into
    # that style's three frames; its fonts resolve against the board's URL (IG_FONT_BASE).
    # Emitted on project 5 boards only, so a pre-rule board's script is unchanged.
    ig_js = ("  var IG_DOCS=" + js(infographic_docs(ig_plan)) + ";\n"
             "  document.querySelectorAll('iframe[data-ig]').forEach(function(f){\n"
             "    var d=IG_DOCS[f.getAttribute('data-ig')];\n"
             "    if(d!==undefined)f.srcdoc=d;\n"
             "  });\n") if new_family else ""
    # The charset is declared: the board carries em dashes and pound signs from the record
    # and from src/lib/boardStyles.ts, and a document served without one is decoded as
    # latin-1 by any viewer that does not send a charset of its own.
    return f"""<meta charset="utf-8">
<title>Page Board: {esc(slug)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Source+Sans+3:wght@400;600&display=swap">
<style>{CSS}{BE.CSS}</style>
<div class="wrap">
<header class="masthead"><div><p class="eyebrow">BlueStaffyUK · Page Board</p><h1 class="title">/{esc(slug)}/</h1></div>
<div class="meta"><span class="pill">status: {esc(m['status'])}</span> <span class="pill">research as of {esc(m['research_as_of'])}</span><br>record <code>{record_hash[:12]}</code></div></header>
<p class="howto"><b>How to pick.</b> Read the outline in block 3, then work down block 6: each section shows its three arrangements rendered from the kit at 1280, 768 and 375 pixels. Choose the one whose SHAPE suits the section — the copy in the frames is the outline's own stub text, not the page's prose. Pick an H1 and a title/description pair in block 2, leave a note anywhere you want something changed, then approve in block 8.</p>
<div id="doc"></div>
</div>
{blocks}
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.0/marked.min.js"></script>
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
  // Blocks 4 and 5: the keyword and entity filters (scripts/board_entities.py).
  {BE.JS}
  // The style frames are filled HERE rather than carrying a static srcdoc each: the page
  // stylesheet is inlined once and pasted into every frame at load, instead of nine copies
  // per styled section inside the committed file.
  var PREVIEW_CSS={js(previews["css"])};var BLOCKS={js(previews["blocks"])};
  // The navigation block's own pair. A SECOND stylesheet, because those four renderings are
  // cut from /kit-preview/ and the style previews from /board-preview/<slug>/ — two built
  // pages, two inlined cascades, and pasting one into the other's frames would be showing a
  // component under a stylesheet it was not built with.
  var NAV_CSS={js(nav["css"])};var NAV_BLOCKS={js(nav["blocks"])};
  // A srcdoc frame is sandboxed and has NO origin, so `/images/x.webp` inside one resolves
  // to nothing. The cutter carried every photo along as a data URI; each `src` is swapped
  // for its entry as the frame is filled, once per frame rather than once per block.
  var IMAGES={js(previews.get("images", {}))};
  function withImages(html){{
    return html.replace(/src="(\\/[^"]*)"/g,function(m,u){{
      return IMAGES[u]?'src="'+IMAGES[u]+'"':m;
    }});
  }}
  document.querySelectorAll('iframe[data-block]').forEach(function(f){{
    var inner=BLOCKS[f.getAttribute('data-block')];
    if(inner===undefined)return;
    inner=withImages(inner);
    f.srcdoc='<!doctype html><meta charset="utf-8"><style>html{{overflow:auto}}'
      +'body{{margin:0;background:#F4F1EA;color:#1B2430;font-family:"Source Sans 3",system-ui,sans-serif}}'
      +PREVIEW_CSS+'</style>'+inner;
  }});
  document.querySelectorAll('iframe[data-nav]').forEach(function(f){{
    var inner=NAV_BLOCKS[f.getAttribute('data-nav')];
    if(inner===undefined)return;
    f.srcdoc='<!doctype html><meta charset="utf-8"><style>html{{overflow:auto}}'
      +'body{{margin:0;background:#F4F1EA;color:#1B2430;font-family:"Source Sans 3",system-ui,sans-serif}}'
      +NAV_CSS+'</style>'+inner;
  }});
{ig_js}  var RECORD_HASH={js(record_hash)};var BOARD_DOC={js("boards/" + slug)};
  var SIGNATURE_SECTIONS={js(signature_sections(board, ledger, slug, ig_plan))};
  var SIGNATURE_LABELS={js(signature_labels(board, ledger, slug, ig_plan))};
  var btn=document.getElementById('approve-btn'),st=document.getElementById('approve-status');
  var ref=null;                                       // the board database doc, once reached
  // 'pending' until the database answers, 'ready' once it has, 'none' when this viewer has
  // no claude.ai runtime or the call failed. Only 'none' earns the no-database message.
  var dbState='pending';
  // True while a refusal list is on screen: the database callbacks resolve on their own
  // clock, and their "Ready." or "Approved …" must never wipe the list of open picks.
  var refusing=false;
  var APPROVED={js(bool(approved))};
  function say(text){{if(!refusing)st.textContent=text;}}
  function fieldOf(id){{return SIGNATURE_LABELS[id]&&SIGNATURE_LABELS[id].n==='2'?id:'pick-'+id;}}
  // Every pick still open, in the order the breeder meets them: block 2 first, then the
  // signature in its own (section) order.
  function missingPicks(){{
    var ids=['h1','meta-title','meta-description'].concat(SIGNATURE_SECTIONS);
    return ids.filter(function(id){{
      return !document.querySelector('input[name="'+fieldOf(id)+'"]:checked');
    }});
  }}
  // One line per open pick — "§08 <section> — infographic style (ig:<slot>)" — each a link
  // to its control; then the first one is scrolled to and its first radio focused.
  function refuse(missing){{
    refusing=true;st.textContent='';
    var head=document.createElement('b');
    head.textContent=missing.length+' pick(s) still open — approve again once each is made:';
    st.appendChild(head);
    var ul=document.createElement('ul');ul.className='missing';
    missing.forEach(function(id){{
      var e=SIGNATURE_LABELS[id]||{{n:'',section:id,label:id,anchor:''}};
      var li=document.createElement('li');
      var text=(e.n?(e.n.length<2?'Block '+e.n+' ':'§'+e.n+' '):'')+e.section+' — '+e.label;
      var target=e.anchor&&document.getElementById(e.anchor);
      if(target){{
        var a=document.createElement('a');a.href='#'+e.anchor;a.textContent=text;
        a.addEventListener('click',function(ev){{ev.preventDefault();jump(id);}});
        li.appendChild(a);
      }}else{{li.textContent=text;}}
      ul.appendChild(li);
    }});
    st.appendChild(ul);
    jump(missing[0]);
  }}
  function jump(id){{
    var e=SIGNATURE_LABELS[id],target=e&&e.anchor&&document.getElementById(e.anchor);
    if(target)target.scrollIntoView({{behavior:'smooth',block:'start'}});
    var first=document.querySelector('input[name="'+fieldOf(id)+'"]:not([disabled])');
    if(first)first.focus({{preventScroll:!!target}});
  }}
  // The click handler is wired BEFORE the claude.ai and database checks: a half-picked board
  // is refused, and told what is open, in any viewer. Only the write needs the database.
  // An already-approved board keeps its button disabled until the database answers, as it
  // always has; any other board can be checked for open picks in any viewer.
  if(!APPROVED)btn.disabled=false;
  btn.addEventListener('click',function(){{
    // A half-picked board is worse than an unapproved one: the build would start and
    // then guess a component. Refuse the write and name every pick still open.
    var missing=missingPicks();
    if(missing.length){{refuse(missing);btn.disabled=false;return;}}
    refusing=false;
    if(!ref){{
      st.textContent=dbState==='pending'
        ?'Every pick is made. Connecting to the board database… click approve again in a moment.'
        :'Every pick is made. Approval writes to the board database, which only claude.ai can reach — open this board there, or approve in chat.';
      return;
    }}
    // missingPicks() already covers block 2; these guards stay so no record is ever sent
    // with a missing index, whatever SIGNATURE_LABELS says.
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
  if(!window.claude||!window.claude.use){{dbState='none';say('Open this board inside claude.ai to approve it.');return;}}
  if(!APPROVED)say('Connecting…');               // an approved board keeps saying so until the database answers
  window.claude.use("db").then(function(db){{
    if(!db){{dbState='none';say('Approval needs the board database, which this view cannot reach.');return;}}
    ref=db.doc(BOARD_DOC);dbState='ready';
    ref.get().then(function(snap){{
      if(!snap||!snap.exists){{return;}}                 // absence is not an error: never approved
      var d=snap.data()||{{}};                            // frozen body; undefined only when !exists
      if(d.record_hash===RECORD_HASH){{say('Approved '+(d.approved_at||'earlier')+'.');}}
      else{{say('An earlier version of this board was approved — this record has changed since.');}}
    }}).catch(function(e){{say('Could not read the board database: '+(e&&e.code?e.code:'error')+'. Approve in chat.');}});
    btn.disabled=false;
    if(!APPROVED)say('Ready.');
  }}).catch(function(e){{dbState='none';say('Board database unavailable: '+(e&&e.code?e.code:'error')+'. Approve in chat.');}});
}})();
</script>
"""


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: build_page_board.py <slug>")
    slug = sys.argv[1]
    # STOP 2 (docs/reference/page-run.md row 9, the user's ruling of 2026-09-29): a new page's
    # outline is approved on its own before its page board is built. The twelve pages built
    # before project 5 have no outline record and are left alone (family_rules.is_new_page).
    if PB.FR.is_new_page(slug):
        refusal = OM.approval_refusal(slug)
        if refusal:
            print(f"build-page-board REFUSED outline-unapproved: {refusal}")
            sys.exit(2)
    board = PB.load_board(slug)
    ont, ledger = PB.load_ontology(), PB.load_ledger()
    # No own-page pop: PB.header_hits() excludes it with own_live_key(), which is "/" for
    # the homepage — the pop built "//" and left the homepage colliding with itself.
    live = PB.live_headings() if PB.DIST.exists() else {}
    # No thumbnails: board_thumbs.mjs is not ported, so the map stays empty and every
    # option card renders as its labelled box.
    thumbs = {}
    previews = load_previews(slug)
    nav = load_nav_previews()
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / (PB.slug_file(slug) + ".html")
    routes = load_routes()
    # Candidates, thumbnails and generated previews only for the pages the image rule binds.
    images = IR.board_images(board) if PB.FR.applies(board) else None
    # The demo record and a record-only page the data files never name have no intake, and
    # an intake that cannot be read must not stop the board: it renders without block 0 and
    # says why.
    try:
        intake = PI.intake(slug)
    except Exception as e:  # noqa: BLE001 — any intake failure only drops block 0
        intake = None
        print(f"board: no block 0 for {slug} — {type(e).__name__}: {e}", file=sys.stderr)
    try:
        html = render(board, ont, ledger, live, thumbs, slug, previews, routes, nav, images, intake)
    except PB.BoardError as e:
        # A record fault found while rendering (e.g. an unknown infographic_style): the same
        # refusal approval gives, said plainly, and no half-written board on disk.
        print(f"build-page-board REFUSED: {e}")
        sys.exit(2)
    out.write_text(html, encoding="utf-8")
    n_int = sum(len(s["links"]["internal"]) for s in board["sections"])
    n_ext = sum(len(s["links"]["external"]) for s in board["sections"])
    unresolved = sorted({l["href"] for s in board["sections"] for l in s["links"]["internal"]
                         if resolve_internal(l["href"], routes)[0] != "yes"})
    styled = [s for s in board["sections"] if s.get("styles")]
    want = sum(len(s["styles"]) for s in styled)
    have = sum(1 for s in styled for st in s["styles"] if f"{s['id']}|{st}" in previews["blocks"])
    print("wrote %s — %d sections, %d live pages checked, %d/%d style renderings embedded"
          % (out.relative_to(PB.ROOT), len(board["sections"]), len(live), have, want))
    print("  navigation: %d/%d component(s) rendered from dist/kit-preview/"
          % (len(nav["blocks"]), len(NAV_COMPONENTS)))
    print("  links: %d internal · %d external%s"
          % (n_int, n_ext, "" if not unresolved else " — unresolved: " + ", ".join(unresolved)))
    if want and have < want:
        print("  some styles are not rendered: run npm run build, then "
              "python3 scripts/build_board_previews.py %s" % slug)
    if PB.FR.applies(board):
        plan = PB.ig_plan(board)
        n_ig = len(plan)
        files = {IG_FONT_BASE + f: f"public/fonts/{f}" for f in IG_FONT_FILES}
        print("  infographics: %d slot(s), %d previews inline; approval waits on %d"
              % (n_ig, 3 * n_ig, len(PB.ig_slots_required(board, plan))))
        print("  publish with capabilities={\"db\": {}} and files=%s" % json.dumps(files))


if __name__ == "__main__":
    main()
