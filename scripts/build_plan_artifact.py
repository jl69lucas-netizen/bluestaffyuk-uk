import re, html, pathlib, sys
src = pathlib.Path('/Users/apple/Downloads/BSUK/docs/superpowers/plans/2026-09-15-foundation.md').read_text()
out = pathlib.Path('/Users/apple/Downloads/BSUK/docs/artifacts/bsuk-foundation-plan.html')
out.parent.mkdir(parents=True, exist_ok=True)

# split into sections on '## '
parts = re.split(r'^###? ', src, flags=re.M)
preamble = parts[0]
sections = []
for p in parts[1:]:
    title, _, body = p.partition('\n')
    sections.append((title.strip(), body.strip()))

def esc(s):  # safe inside <script type=text/markdown>
    return s.replace('</script', '<\\/script')

blocks = '\n'.join(
    f'<script type="text/markdown" data-title="{html.escape(t)}">\n{esc(b)}\n</script>' for t, b in sections)

page = f'''<title>BSUK Foundation Plan</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400&display=swap">
<style>
:root{{--ground:#F3F1EC;--paper:#FFFFFF;--ink:#1B2430;--ink-2:#46566B;--ink-3:#7A8797;--line:#DAD6CC;--blue:#2C4A6B;--blue-soft:#E4EAF1;--steel:#8FA3B8;--code-bg:#ECE9E1;--ok:#2F6B4F;--warn:#9A4A2A;--mark:#FBF1C7}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--ground:#141A21;--paper:#1B232D;--ink:#E9ECF0;--ink-2:#B4BFCC;--ink-3:#7F8C9B;--line:#2C3743;--blue:#8FB3D9;--blue-soft:#22303F;--steel:#5C7086;--code-bg:#111820;--ok:#7FC49F;--warn:#E39B7A;--mark:#4A3F16}}}}
:root[data-theme="dark"]{{--ground:#141A21;--paper:#1B232D;--ink:#E9ECF0;--ink-2:#B4BFCC;--ink-3:#7F8C9B;--line:#2C3743;--blue:#8FB3D9;--blue-soft:#22303F;--steel:#5C7086;--code-bg:#111820;--ok:#7FC49F;--warn:#E39B7A;--mark:#4A3F16}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font:16px/1.6 "Source Sans 3",system-ui,-apple-system,sans-serif}}
.wrap{{max-width:1040px;margin:0 auto;padding:36px 24px 96px}}
header.mast{{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;padding-bottom:18px;border-bottom:3px solid var(--blue);margin-bottom:8px}}
.eyebrow{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--blue);font-weight:600;margin:0 0 6px}}
h1.title{{font-family:Fraunces,Georgia,serif;font-weight:700;font-size:clamp(28px,4vw,42px);line-height:1.08;margin:0;text-wrap:balance}}
.meta{{font-size:13px;color:var(--ink-3);text-align:right;line-height:1.5}}
.pill{{display:inline-block;border-radius:50px;padding:2px 10px;font-size:11px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;border:1px solid var(--line);background:var(--paper)}}
.toolbar{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:14px 0 26px;font-size:13px;color:var(--ink-2)}}
button.btn{{font:inherit;font-size:13px;font-weight:600;padding:7px 14px;border-radius:6px;border:1px solid var(--blue);background:var(--blue);color:#fff;cursor:pointer}}
button.btn.ghost{{background:transparent;color:var(--blue)}}
:root[data-theme="dark"] button.btn:not(.ghost),:root:not([data-theme="light"]) button.btn:not(.ghost){{color:var(--ground)}}
button:focus-visible{{outline:3px solid var(--steel);outline-offset:2px}}
nav.toc{{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:14px;margin:0 0 26px}}
nav.toc a{{color:var(--blue);text-decoration:none;border-bottom:1px solid transparent}}
nav.toc a:hover{{border-color:var(--blue)}}
section.sec{{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:22px 28px 26px;margin:0 0 18px;scroll-margin-top:16px}}
section.sec .sh{{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin:0 0 10px}}
section.sec h2{{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:22px;margin:0;line-height:1.2}}
.md p,.md li{{max-width:72ch}}
.md h3{{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-2);margin:20px 0 6px}}
.md table{{border-collapse:collapse;width:100%;font-size:14px;margin:10px 0 14px;display:block;overflow-x:auto}}
.md th{{text-align:left;font-weight:600;color:var(--ink-2);font-size:12px;text-transform:uppercase;letter-spacing:.06em;border-bottom:2px solid var(--blue);padding:6px 10px;white-space:nowrap}}
.md td{{padding:6px 10px;border-bottom:1px solid var(--line);vertical-align:top;font-variant-numeric:tabular-nums}}
.md code{{font:13px/1.5 "JetBrains Mono",ui-monospace,Menlo,monospace;background:var(--code-bg);padding:1px 5px;border-radius:4px}}
.md pre{{background:var(--code-bg);padding:14px 16px;border-radius:6px;overflow-x:auto;font:13px/1.55 "JetBrains Mono",ui-monospace,Menlo,monospace}}
.md pre code{{background:none;padding:0}}
.md strong{{color:var(--ink)}}
.md a{{color:var(--blue)}}
.copied{{color:var(--ok);font-size:12px}}
@media (max-width:640px){{header.mast{{grid-template-columns:1fr}}.meta{{text-align:left}}section.sec{{padding:16px 16px 20px}}}}
@media (prefers-reduced-motion:no-preference){{button.btn{{transition:opacity .15s}}button.btn:hover{{opacity:.85}}}}
</style>
<div class="wrap">
<header class="mast"><div><p class="eyebrow">BlueStaffyUK rebuild · Project 1 of 6</p><h1 class="title">Foundation implementation plan</h1></div>
<div class="meta"><span class="pill">status: approved</span> <span class="pill">2026-09-15</span><br>docs/superpowers/plans/2026-09-15-foundation.md</div></header>
<div class="toolbar"><button class="btn" id="copy-all">Copy whole spec as Markdown</button><span id="all-status"></span><span>Each section has its own copy button; the copy is exact markdown, not scraped HTML.</span></div>
<nav class="toc" id="toc"></nav>
<div id="doc"></div>
</div>
<script type="text/markdown" data-title="Context">
{esc(preamble.split(chr(10),1)[1].strip() if preamble.startswith('#') else preamble.strip())}
</script>
{blocks}
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.0/marked.min.js"></script>
<script>
(function(){{
  var doc=document.getElementById('doc'),toc=document.getElementById('toc'),all=[];
  function copy(text,el){{navigator.clipboard.writeText(text).then(function(){{el.textContent='Copied';el.className='copied';setTimeout(function(){{el.textContent='';}},1800);}});}}
  document.querySelectorAll('script[type="text/markdown"]').forEach(function(b,i){{
    var title=b.getAttribute('data-title'),md=b.textContent.replace(/^\\n+|\\s+$/g,'');
    all.push('## '+title+'\\n\\n'+md);
    var id='s'+i,sec=document.createElement('section');sec.className='sec';sec.id=id;
    var sh=document.createElement('div');sh.className='sh';
    var h2=document.createElement('h2');h2.textContent=title;sh.appendChild(h2);
    var right=document.createElement('span');var st=document.createElement('span');st.style.marginRight='8px';
    var btn=document.createElement('button');btn.className='btn ghost';btn.textContent='Copy section';
    btn.addEventListener('click',function(){{copy('## '+title+'\\n\\n'+md,st);}});
    right.appendChild(st);right.appendChild(btn);sh.appendChild(right);sec.appendChild(sh);
    var body=document.createElement('div');body.className='md';body.innerHTML=window.marked?marked.parse(md):md;
    sec.appendChild(body);doc.appendChild(sec);
    var a=document.createElement('a');a.href='#'+id;a.textContent=title;toc.appendChild(a);
  }});
  document.getElementById('copy-all').addEventListener('click',function(){{copy('# BlueStaffyUK Rebuild — Project 1 of 6: Foundation\\n\\n'+all.join('\\n\\n'),document.getElementById('all-status'));}});
}})();
</script>
'''
out.write_text(page)
print(out, len(page), 'bytes,', len(sections)+1, 'sections')
