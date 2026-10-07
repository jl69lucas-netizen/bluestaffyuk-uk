"""One markdown deliverable -> one Artifact page with a copy button per section and a `.md`
download (CLAUDE.md, "Every deliverable ships as an Artifact with copy buttons, plus `.md`").

Same method as scripts/build_spec_artifact.py: the markdown is authored once and shipped
verbatim inside `<script type="text/markdown">` blocks, rendered client-side, so a section's
copy button hands back exact markdown rather than HTML scraped out of the DOM. The difference
is that this is a function the research-board and outline builders call with their own
sections, so neither of them writes HTML by hand.

    page(title, eyebrow, heading, status, date, rel, sections, md_name)
        sections: [(section title, markdown body), ...]
    markdown(heading, sections) -> the whole document, the same text the download hands back

The download goes through the viewer's `downloads` capability: the claude.ai Artifact viewer
never grants a page download permission, so a link or a blob-URL click does nothing there (the
publish warning of 2026-10-07). Publish the page with `capabilities=CAPABILITIES`
(`publish_hint` prints the step). The button stays hidden until the runtime says it can save,
and "Copy all as Markdown" is the fallback that always works, including in a saved copy.
"""
import html
import json
import re

# Pinned, from cdnjs (the artifact rules allow cdnjs scripts). Loaded before the page script.
MARKED = "https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.0/marked.min.js"
PURIFY = "https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.1.6/purify.min.js"
_CLOSE = re.compile(r"</(script)", re.I)
# What the page needs from the Artifact viewer. Pass it on every publish: a page published
# without it gets `null` from claude.use("downloads") and never shows the download button.
CAPABILITIES = {"downloads": True}

CSS = """
:root{--ground:#F4F1EA;--paper:#FFFFFF;--ink:#1B2430;--ink-2:#46566B;--ink-3:#5E6B7A;--line:#DAD6CC;--blue:#1F3A52;--blue-soft:#E4EAF1;--steel:#8FA3B8;--code-bg:#FAF8F3;--ok:#2F6B4F;--warn:#9A4A2A;--mark:#EFE3B4}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ground:#14202B;--paper:#1B2A3A;--ink:#F4F1EA;--ink-2:#E4EAF1;--ink-3:#8FA3B8;--line:#34495E;--blue:#8FB3D9;--blue-soft:#1F3A52;--steel:#5C7086;--code-bg:#111820;--ok:#7FC49F;--warn:#E39B7A;--mark:#4A3F16}}
:root[data-theme="dark"]{--ground:#14202B;--paper:#1B2A3A;--ink:#F4F1EA;--ink-2:#E4EAF1;--ink-3:#8FA3B8;--line:#34495E;--blue:#8FB3D9;--blue-soft:#1F3A52;--steel:#5C7086;--code-bg:#111820;--ok:#7FC49F;--warn:#E39B7A;--mark:#4A3F16}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font:16px/1.6 "Source Sans 3",system-ui,-apple-system,sans-serif}
.wrap{max-width:1120px;margin:0 auto;padding:36px 16px 96px}
header.mast{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;padding-bottom:18px;border-bottom:3px solid var(--blue);margin-bottom:8px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--blue);font-weight:600;margin:0 0 6px}
h1.title{font-family:Fraunces,Georgia,serif;font-weight:700;font-size:clamp(26px,4vw,40px);line-height:1.1;margin:0;text-wrap:balance}
.meta{font-size:13px;color:var(--ink-3);text-align:right;line-height:1.5;overflow-wrap:anywhere}
.pill{display:inline-block;border-radius:50px;padding:2px 10px;font-size:11px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;border:1px solid var(--line);background:var(--paper)}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:14px 0 26px;font-size:13px;color:var(--ink-2)}
button.btn{font:inherit;font-size:13px;font-weight:600;padding:7px 14px;border-radius:6px;border:1px solid var(--blue);background:var(--blue);color:#fff;cursor:pointer}
button.btn.ghost{background:transparent;color:var(--blue)}
:root[data-theme="dark"] button.btn:not(.ghost){color:var(--ground)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) button.btn:not(.ghost){color:var(--ground)}}
button:focus-visible{outline:3px solid var(--steel);outline-offset:2px}
nav.toc{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:14px;margin:0 0 26px}
nav.toc a{color:var(--blue);text-decoration:none;border-bottom:1px solid transparent}
nav.toc a:hover{border-color:var(--blue)}
section.sec{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:22px 24px 26px;margin:0 0 18px;scroll-margin-top:16px;min-width:0}
section.sec .sh{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin:0 0 10px;flex-wrap:wrap}
section.sec h2{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:22px;margin:0;line-height:1.2}
.md p,.md li{max-width:78ch}
.md h3{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-2);margin:20px 0 6px}
.md table{border-collapse:collapse;width:100%;font-size:14px;margin:10px 0 14px}
.md th{text-align:left;font-weight:600;color:var(--ink-2);font-size:12px;text-transform:uppercase;letter-spacing:.06em;border-bottom:2px solid var(--blue);padding:6px 10px}
.md td{padding:6px 10px;border-bottom:1px solid var(--line);vertical-align:top;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.md code{font:13px/1.5 "JetBrains Mono",ui-monospace,Menlo,monospace;background:var(--code-bg);padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
.md strong{color:var(--ink)}
.md a{color:var(--blue);overflow-wrap:anywhere}
.copied{color:var(--ok);font-size:12px}
.warn{color:var(--warn);font-size:12px}
[hidden]{display:none!important}
@media (max-width:640px){header.mast{grid-template-columns:1fr}.meta{text-align:left}section.sec{padding:16px 14px 20px}
.md table,.md thead,.md tbody,.md tr,.md th,.md td{display:block}.md thead{position:absolute;left:-9999px}
.md tr{border:1px solid var(--line);border-radius:6px;margin:0 0 10px;padding:6px 0}.md td{border:0;padding:4px 12px}
.md td::before{content:attr(data-label);display:block;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-3)}}
@media (prefers-reduced-motion:no-preference){button.btn{transition:opacity .15s}button.btn:hover{opacity:.85}}
"""

JS = r"""
(function(){
  var doc=document.getElementById('doc'),toc=document.getElementById('toc'),all=[];
  function un(t){return t.replace(/<\\\//g,'</');}
  var head=un(document.getElementById('md-head').textContent.trim()),name=un(document.getElementById('md-name').textContent.trim());
  function say(el,msg,cls){el.textContent=msg;el.className=cls||'copied';setTimeout(function(){if(el.textContent===msg)el.textContent='';},cls?6000:1800);}
  function copy(text,el){
    function legacy(){var t=document.createElement('textarea'),ok=false;t.value=text;t.setAttribute('readonly','');t.style.position='fixed';t.style.opacity='0';
      document.body.appendChild(t);t.select();try{ok=document.execCommand('copy');}catch(e){}t.remove();say(el,ok?'Copied':'Copying is blocked here',ok?'':'warn');}
    if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(text).then(function(){say(el,'Copied');},legacy);else legacy();}
  function labels(root){root.querySelectorAll('table').forEach(function(t){var hs=[].map.call(t.querySelectorAll('th'),function(h){return h.textContent;});
    t.querySelectorAll('tbody tr').forEach(function(r){[].forEach.call(r.children,function(c,i){c.setAttribute('data-label',hs[i]||'');});});});}
  document.querySelectorAll('script[type="text/markdown"][data-title]').forEach(function(b,i){
    var title=b.getAttribute('data-title'),md=un(b.textContent.replace(/^\n+|\s+$/g,''));
    var full='## '+title+'\n\n'+md;all.push(full);
    var id='s'+i,sec=document.createElement('section');sec.className='sec';sec.id=id;
    var sh=document.createElement('div');sh.className='sh';
    var h2=document.createElement('h2');h2.textContent=title;sh.appendChild(h2);
    var right=document.createElement('span');var st=document.createElement('span');st.style.marginRight='8px';
    var btn=document.createElement('button');btn.className='btn ghost';btn.textContent='Copy section';
    btn.addEventListener('click',function(){copy(full,st);});
    right.appendChild(st);right.appendChild(btn);sh.appendChild(right);sec.appendChild(sh);
    var body=document.createElement('div');body.className='md';
    if(window.marked&&window.DOMPurify){body.innerHTML=DOMPurify.sanitize(marked.parse(md));labels(body);}
    else{body.style.whiteSpace='pre-wrap';body.textContent=md;}
    sec.appendChild(body);doc.appendChild(sec);
    var a=document.createElement('a');a.href='#'+id;a.textContent=title;toc.appendChild(a);
  });
  var whole='# '+head+'\n\n'+all.join('\n\n')+'\n';
  document.getElementById('copy-all').addEventListener('click',function(){copy(whole,document.getElementById('all-status'));});
  // The .md download: only through the viewer's downloads capability (a link does nothing there).
  var dl=document.getElementById('dl-md'),st=document.getElementById('all-status'),downloads=null,KEEP=['bad_request','request_unknown','transform_error'];
  dl.addEventListener('click',function(){if(!downloads)return;
    downloads.save({filename:name,data:whole}).then(function(r){say(st,r&&r.status==='delivered'?'Sent':'Downloaded');},function(e){var c=(e&&e.code)||'error';
      if(c==='declined')say(st,'Download cancelled','warn');
      else if(c==='rate_limited')say(st,'A download prompt is already open','warn');
      else if(c==='too_large')say(st,'This file is too large to download here. Use Copy all as Markdown.','warn');
      else if(KEEP.indexOf(c)>=0)say(st,"Download didn't happen ("+c+'). Use Copy all as Markdown.','warn');
      // unavailable, not_granted, capability_* and any unknown code: this view cannot save.
      else{downloads=null;dl.hidden=true;say(st,'Download is unavailable here ('+c+'). Use Copy all as Markdown.','warn');}});});
  var use=window.claude&&window.claude.use;
  if(typeof use==='function')use.call(window.claude,"downloads").then(function(ns){if(ns){downloads=ns;dl.hidden=false;}},function(){});
})();
"""


def _esc(text):
    """Safe inside a <script type=text/...> block: nothing can close it early, in any case
    (`</script`, `</SCRIPT`, `</Script`). The page script turns `<\\/` back into `</` before
    it copies or renders, and what it renders goes through DOMPurify."""
    return _CLOSE.sub(lambda m: "<\\/" + m.group(1), text)


def cell(value):
    """One markdown table cell: pipes escaped, line breaks folded."""
    return " ".join(str(value).split()).replace("|", "\\|")


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def markdown(heading, sections):
    """The whole document as markdown — byte for byte what the page's download hands back."""
    return "# " + heading + "\n\n" + "\n\n".join(
        f"## {t}\n\n{b.strip()}" for t, b in sections) + "\n"


def publish_hint(html_path):
    """The publish step a generator prints after it writes the page."""
    return (f"publish {html_path} as an Artifact with "
            f"capabilities={json.dumps(CAPABILITIES)} (the .md download needs it)")


def page(title, eyebrow, heading, status, date, rel, sections, md_name):
    blocks = "\n".join(
        f'<script type="text/markdown" data-title="{html.escape(t)}">\n{_esc(b.strip())}\n</script>'
        for t, b in sections)
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="mast"><div><p class="eyebrow">{html.escape(eyebrow)}</p><h1 class="title">{html.escape(heading)}</h1></div>
<div class="meta"><span class="pill">{html.escape(status)}</span> <span class="pill">{html.escape(date)}</span><br>{html.escape(rel)}</div></header>
<div class="toolbar"><button class="btn" id="copy-all">Copy all as Markdown</button><button class="btn ghost" id="dl-md" hidden>Download .md</button><span id="all-status"></span><span>Every section has its own copy button; the copy is the exact markdown.</span></div>
<nav class="toc" id="toc" aria-label="Sections"></nav>
<main id="doc"></main>
</div>
<script type="text/plain" id="md-head">{_esc(heading)}</script>
<script type="text/plain" id="md-name">{_esc(md_name)}</script>
{blocks}
<script src="{MARKED}"></script>
<script src="{PURIFY}"></script>
<script>{JS}</script>
</body>
</html>
"""
