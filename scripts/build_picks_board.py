#!/usr/bin/env python3
"""build_picks_board.py — the picks board: one row per component (+ the mark), five pick
buttons, a note, Save writes {component, variant, note, at, by} to db doc picks/<id>.
Same db mechanism as docs/artifacts/boards/index.html (window.claude.use("db")).
Output: docs/artifacts/design-picks.html — published by the controller with the db capability
{"rules":[{"path":"","write":"admin"}]} and the canvas URL for the row links.

build(rows, canvas_url) returns the page as a string so the tests can exercise it without
writing to the repo; main() reads the data files and writes the committed copy.
"""
import html as H, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/artifacts/design-picks.html"


def row_html(r, canvas_url):
    btns = "".join(
        f'<label><input type="radio" name="pick-{r["id"]}" value="{v}"><span>{v.upper()}</span></label>'
        for v in "abcde"
    )
    return (f'<section class="row" data-id="{r["id"]}"><h2>{H.escape(r["title"])} '
            f'<a href="{canvas_url}" target="_blank" rel="noopener">canvas &#8599;</a></h2>'
            f'<div class="picks">{btns}</div>'
            f'<textarea name="note-{r["id"]}" placeholder="What you would change (optional)"></textarea>'
            f'<div class="bar"><button class="btn" data-save="{r["id"]}">Save pick</button>'
            f'<span class="st" id="st-{r["id"]}"></span></div></section>')


def build(rows, canvas_url):
    """rows: the component records in canvas order, WITHOUT the mark row (added here)."""
    rows = [{"id": "mark", "title": "0 &middot; The mark"}] + list(rows)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BSUK Design Picks</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700&family=Source+Sans+3:wght@400;600&display=swap">
<style>
:root{{--ground:#F4F1EA;--paper:#fff;--ink:#1B2430;--line:#DAD6CC;--brand:#1F3A52;--cta:#C9A227;--ok:#2F6B4F;--on-cta:#14202B;--on-brand:#fff}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--ground:#141A21;--paper:#1B232D;--ink:#E9ECF0;--line:#2C3743;--brand:#8FB3D9;--on-brand:#14202B}}}}
:root[data-theme="dark"]{{--ground:#141A21;--paper:#1B232D;--ink:#E9ECF0;--line:#2C3743;--brand:#8FB3D9;--on-brand:#14202B}}
body{{margin:0;background:var(--ground);color:var(--ink);font:16px/1.5 "Source Sans 3",system-ui,sans-serif}}
.wrap{{max-width:880px;margin:0 auto;padding:32px 16px 96px}} h1{{font-family:Fraunces,serif;color:var(--brand);margin:0 0 8px}}
.row{{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:14px 0}}
.row h2{{font-family:Fraunces,serif;font-size:20px;margin:0 0 10px;display:flex;justify-content:space-between;align-items:baseline;gap:12px}} .row h2 a{{font:600 13px "Source Sans 3",sans-serif;color:var(--brand)}}
.picks{{display:flex;gap:8px;flex-wrap:wrap}} .picks label{{cursor:pointer}} .picks input{{position:absolute;opacity:0}}
.picks span{{display:inline-grid;place-items:center;min-width:48px;min-height:44px;border:2px solid var(--line);border-radius:50px;font-weight:600}}
.picks input:checked+span{{background:var(--cta);border-color:var(--cta);color:var(--on-cta)}} .picks input:focus-visible+span{{outline:3px solid var(--brand);outline-offset:2px}}
textarea{{width:100%;box-sizing:border-box;margin:12px 0;padding:10px;border:1px solid var(--line);border-radius:6px;font:inherit;min-height:60px;background:var(--paper);color:var(--ink)}}
.bar{{display:flex;gap:12px;align-items:center;flex-wrap:wrap}} .btn{{font:600 14px "Source Sans 3",sans-serif;padding:10px 18px;border-radius:50px;border:0;background:var(--brand);color:var(--on-brand);cursor:pointer;min-height:44px}}
.st{{font-size:13px;color:var(--ok)}}
</style></head><body><div class="wrap">
<h1>BlueStaffyUK design picks</h1><p>Open the canvas, look at a row, pick the variant here, save. Each row saves on its own; you can come back later.</p>
{''.join(row_html(r, canvas_url) for r in rows)}
</div>
<script>
(function(){{
  var stAll=function(id,t){{document.getElementById('st-'+id).textContent=t;}};
  if(!window.claude||!window.claude.use){{document.querySelectorAll('.st').forEach(function(s){{s.textContent='Open inside claude.ai to save picks.';}});return;}}
  window.claude.use("db").then(function(db){{
    if(!db){{document.querySelectorAll('.st').forEach(function(s){{s.textContent='The board database is not reachable from this view.';}});return;}}
    document.querySelectorAll('.row').forEach(function(row){{
      var id=row.dataset.id, ref=db.doc('picks/'+id);
      ref.get().then(function(snap){{
        if(!snap||!snap.exists)return; var d=snap.data()||{{}};
        var r=row.querySelector('input[value="'+d.variant+'"]'); if(r)r.checked=true;
        row.querySelector('textarea').value=d.note||''; stAll(id,'Saved '+(d.at||'').slice(0,16).replace('T',' '));
      }}).catch(function(){{}});
      row.querySelector('[data-save]').addEventListener('click',function(){{
        var p=row.querySelector('input:checked'); if(!p){{stAll(id,'Pick a variant first.');return;}}
        var rec={{component:id,variant:p.value,note:row.querySelector('textarea').value.trim(),at:new Date().toISOString(),by:'owner'}};
        ref.set(rec).then(function(){{stAll(id,'Saved '+rec.at.slice(0,16).replace('T',' '));}}).catch(function(e){{stAll(id,'Could not save: '+(e&&e.code?e.code:'error'));}});
      }});
    }});
  }}).catch(function(e){{document.querySelectorAll('.st').forEach(function(s){{s.textContent='Board database unavailable: '+(e&&e.code?e.code:'error')+'.';}});}});
}})();
</script></body></html>"""


def main(argv=None):
    # Project 3 rows only: the board is the sheet the user picked a variant on, and a
    # component added after the picks were pulled has no five options to show.
    rows = [r for r in json.loads((ROOT / "data/design/components.json").read_text())
            if r["project"] == 3]
    arts = json.loads((ROOT / "data/design/artifacts.json").read_text())
    page = build(rows, arts["canvas"])
    OUT.write_text(page)
    print(f"{OUT.relative_to(ROOT)} {len(page)} bytes, {len(rows) + 1} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
