"""Build the answer board page — a static shell; the questions come from the board's db.

Spec: docs/superpowers/specs/2026-09-26-answer-board-design.md §3, §6, §8. Layout A: a
sticky progress rail and a wide question column (a top bar under 900px). The client
(scripts/answer_board_client.js) is inlined; the demo batch is embedded for `#demo`.

    python3 scripts/build_answer_board.py [--out docs/artifacts/bsuk-answer-board.html]

Publish with capabilities {db: {rules: [{path: "", read: "admin", write: "admin"}]},
comments: {}, downloads: true}.
"""
import argparse
import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from answer_board_batch import make_batch  # noqa: E402
from answer_sheet import parse_sheet  # noqa: E402

CLIENT_JS = ROOT / "scripts" / "answer_board_client.js"
DEMO = ROOT / "docs" / "reference" / "answer-board" / "demo.md"
OUT = ROOT / "docs" / "artifacts" / "bsuk-answer-board.html"
TITLE = "Questions for You"

CSS = """
:root{--ground:#F3F1EC;--paper:#FFFFFF;--ink:#1B2430;--ink-2:#46566B;--ink-3:#7A8797;--line:#DAD6CC;--blue:#2C4A6B;--blue-soft:#E4EAF1;--steel:#8FA3B8;--code-bg:#ECE9E1;--ok:#2F6B4F;--warn:#9A4A2A;--brass:#A8851A;--field:#FCFBF8;--on-blue:#FFFFFF}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ground:#141A21;--paper:#1B232D;--ink:#E9ECF0;--ink-2:#B4BFCC;--ink-3:#7F8C9B;--line:#2C3743;--blue:#8FB3D9;--blue-soft:#22303F;--steel:#5C7086;--code-bg:#111820;--ok:#7FC49F;--warn:#E39B7A;--brass:#D9B84A;--field:#161D26;--on-blue:#141A21}}
:root[data-theme="dark"]{--ground:#141A21;--paper:#1B232D;--ink:#E9ECF0;--ink-2:#B4BFCC;--ink-3:#7F8C9B;--line:#2C3743;--blue:#8FB3D9;--blue-soft:#22303F;--steel:#5C7086;--code-bg:#111820;--ok:#7FC49F;--warn:#E39B7A;--brass:#D9B84A;--field:#161D26;--on-blue:#141A21}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font:16px/1.6 "Source Sans 3",system-ui,-apple-system,sans-serif}
a{color:var(--blue)}
.app{display:grid;grid-template-columns:300px minmax(0,1fr);min-height:100vh}
.rail{position:sticky;top:0;height:100vh;overflow:auto;background:var(--paper);border-right:1px solid var(--line);padding:24px 18px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--blue);font-weight:600;margin:0 0 6px}
.count{font:700 30px/1.1 Fraunces,Georgia,serif;margin:4px 0 8px}.count span{font-size:15px;color:var(--ink-3);font-weight:600}
.bar{height:6px;background:var(--line);border-radius:6px;overflow:hidden}.bar i{display:block;height:100%;width:0;background:var(--ok);transition:width .2s}
.muted{font-size:12px;color:var(--ink-3);margin:6px 0}
.navbatch{display:flex;justify-content:space-between;gap:8px;margin:16px 0 4px;font-size:13px;font-weight:700;color:var(--ink);text-decoration:none}
.navbatch small{color:var(--ink-3);font-weight:600}
.new{font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;background:var(--brass);color:var(--ink);border-radius:4px;padding:1px 5px;margin-left:6px}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .new{color:var(--on-blue)}}
:root[data-theme="dark"] .new{color:var(--on-blue)}
.navq{display:flex;gap:8px;align-items:center;padding:3px 4px;border-radius:4px;font-size:13px;color:var(--ink-2);text-decoration:none}
.navq:hover{background:var(--blue-soft)}.navq b{min-width:18px;color:var(--blue)}
.dot{width:10px;height:10px;border-radius:50%;border:1.5px solid var(--ink-3);flex:none}
[data-state="answered"] .dot{background:var(--ok);border-color:var(--ok)}
[data-state="skip"] .dot{background:var(--brass);border-color:var(--brass)}
[data-state="not_yet"] .dot{border-style:dashed;border-color:var(--steel);background:var(--blue-soft)}
.main{padding:32px clamp(16px,4vw,56px) 96px;min-width:0;overflow-wrap:anywhere}.main>*{max-width:1120px}
header.mast{padding-bottom:16px;border-bottom:3px solid var(--blue);margin-bottom:16px}
h1.title{font-family:Fraunces,Georgia,serif;font-weight:700;font-size:clamp(28px,4vw,42px);line-height:1.08;margin:0}
.note{background:var(--blue-soft);border:1px solid var(--line);border-radius:6px;padding:10px 14px;font-size:15px;margin:0 0 16px}
.btn{font:inherit;font-size:13px;font-weight:600;padding:8px 14px;border-radius:6px;border:1px solid var(--blue);background:var(--blue);color:var(--on-blue);cursor:pointer;text-decoration:none;display:inline-block;text-align:center}
.btn.ghost{background:transparent;color:var(--blue)}.btn:disabled{opacity:.45;cursor:not-allowed}.btn[aria-disabled="true"]{opacity:.45;cursor:progress}.btn.big{font-size:16px;padding:12px 22px}
button:focus-visible,a:focus-visible,textarea:focus-visible,summary:focus-visible{outline:3px solid var(--steel);outline-offset:2px}
.batch{margin:0 0 34px;scroll-margin-top:16px}
.bhead{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap;margin:0 0 10px}
.bhead h2{font:700 26px/1.2 Fraunces,Georgia,serif;margin:0}
.pill{display:inline-block;border-radius:50px;padding:2px 10px;font-size:11px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;border:1px solid var(--line);background:var(--paper);color:var(--ink-2)}
section.sec{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:20px 26px 22px;margin:0 0 14px}
section.sec h3.st{font:600 21px/1.25 Fraunces,Georgia,serif;margin:0 0 10px}
.intro p,.lead p,.ctx p{max-width:78ch}
.q{border:1px solid var(--line);border-left:4px solid var(--line);border-radius:8px;padding:16px 18px;margin:0 0 14px;background:var(--paper);scroll-margin-top:16px}
.q[data-state="answered"]{border-left-color:var(--ok)}.q[data-state="skip"]{border-left-color:var(--brass)}.q[data-state="not_yet"]{border-left-color:var(--steel)}
.q h4{font:600 18px/1.3 Fraunces,Georgia,serif;margin:0 0 4px}.qn{color:var(--blue);margin-right:6px}
.ctx{color:var(--ink-2);font-size:15px}.ctx p{margin:4px 0}
.where{font-size:12px;color:var(--ink-3);margin:6px 0}
code{font:13px/1.5 "JetBrains Mono",ui-monospace,Menlo,monospace;background:var(--code-bg);padding:1px 5px;border-radius:4px}
label.lab{display:block;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--blue);margin:12px 0 4px}
textarea{width:100%;min-height:72px;resize:vertical;font:15px/1.5 "Source Sans 3",system-ui,sans-serif;color:var(--ink);background:var(--field);border:1.5px solid var(--line);border-radius:6px;padding:10px 12px}
textarea.notefield{min-height:48px}
textarea:focus{border-color:var(--blue);background:var(--paper)}
.opts{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 2px}
.opt{font:inherit;font-size:14px;text-align:left;border:1.5px solid var(--line);border-radius:8px;padding:8px 14px;background:var(--field);color:var(--ink);cursor:pointer}
.opt b{color:var(--blue);margin-right:6px}
.opt[aria-pressed="true"]{border-color:var(--ok);background:var(--blue-soft);font-weight:600}
.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:8px;font-size:13px;color:var(--ink-3)}
.chip{font:inherit;font-size:12px;border:1px solid var(--line);border-radius:50px;padding:3px 11px;background:var(--paper);color:var(--ink-2);cursor:pointer}
.chip[aria-pressed="true"]{background:var(--blue-soft);border-color:var(--blue);color:var(--blue);font-weight:600}
.tick{margin-left:auto;color:var(--ok);font-weight:600;font-size:12px}
section.send{border:2px solid var(--blue)}
.sendrow{display:flex;gap:16px;align-items:center;flex-wrap:wrap}.sendrow>div{flex:1;min-width:240px}
.sendstatus{font-size:14px;color:var(--ink-2);margin:10px 0 0}
section.additional{margin-top:8px}section.additional h2.st{font:600 21px/1.25 Fraunces,Georgia,serif;margin:0 0 10px}
.btn:disabled[aria-disabled="true"]{cursor:not-allowed}.addhelp{margin:0 0 4px;color:var(--ink-2);font-size:15px}
#additional-text{min-height:140px;overflow:hidden}
details#done{margin-top:40px}details#done>summary{cursor:pointer;font:600 20px Fraunces,Georgia,serif}
.donerow{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:10px 0}
.donerow ol{margin:8px 0 0;padding-left:22px;font-size:14px}
@media (max-width:900px){.app{display:block}.rail{position:sticky;top:0;height:auto;z-index:5;display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;padding:10px 16px;border-right:0;border-bottom:1px solid var(--line)}
.rail .eyebrow,#rail-batches,#total-detail{display:none}.rail .count{font-size:20px;margin:0}.rail .bar{flex:1;min-width:80px}#saved{flex-basis:100%;margin:0}
.main{padding:20px 16px 72px}section.sec{padding:16px}.q{padding:14px}}
@media (prefers-reduced-motion:reduce){.bar i{transition:none}}
"""


def demo_batch():
    sheet = parse_sheet(DEMO.read_text(encoding="utf-8"))
    return make_batch(sheet, "demo", "tools", "2026-09-26T12:00:00Z")


def render_shell(demo):
    blob = json.dumps(demo, ensure_ascii=False, sort_keys=True).replace("</", "<\\/").replace("<!--", "<\\u0021--")
    client = CLIENT_JS.read_text(encoding="utf-8").replace("</script", "<\\/script")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITLE)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@400&display=swap">
<style>{CSS}</style></head><body>
<div class="app">
<aside class="rail" aria-label="Progress">
<p class="eyebrow">BlueStaffyUK · answer board</p>
<p class="count"><b id="total-done">0</b> / <b id="total-all">0</b><span> answered</span></p>
<div class="bar" aria-hidden="true"><i id="bar"></i></div>
<p id="total-detail" class="muted"></p>
<nav id="rail-batches" aria-label="Open batches"></nav>
<p id="saved" class="muted" aria-live="polite"></p>
</aside>
<main class="main">
<header class="mast"><p class="eyebrow">BlueStaffyUK · for you</p><h1 class="title">{html.escape(TITLE)}</h1></header>
<p id="status-line" class="note" role="status">Connecting to the board…</p>
<div id="batches"></div>
<section class="sec additional" id="additional" aria-labelledby="additional-h" hidden>
<h2 class="st" id="additional-h">Any additional questions</h2>
<p class="addhelp" id="additional-help">Extra questions or sub-tasks for Claude Code — type or paste them here, then send.</p>
<label class="lab" for="additional-text">Your questions</label>
<textarea id="additional-text" rows="5" autocomplete="off" aria-describedby="additional-help"></textarea>
<div class="sendrow"><button type="button" class="btn big" id="additional-send" aria-describedby="additional-hint" disabled>Send to Claude Code →</button>
<p class="muted" id="additional-hint"></p></div>
<p class="sendstatus" role="status" id="additional-status"></p>
<div class="row"><span>No Claude session watching?</span>
<button type="button" class="chip" id="additional-copy">Copy text</button>
<span id="additional-fallback" aria-live="polite"></span></div>
</section>
<details id="done" hidden><summary>Done</summary><div id="done-list"></div></details>
</main></div>
<script type="application/json" id="demo-batch">{blob}</script>
<script>{client}</script>
</body></html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the answer board page.")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    page = render_shell(demo_batch())
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"{out} — {len(page.encode('utf-8'))} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
