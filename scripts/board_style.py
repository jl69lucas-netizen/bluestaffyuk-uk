"""board_style.py — the presentation layer every board generator embeds.

The user's two picks of 2026-10-07 (docs/superpowers/plans/2026-10-07-board-readability.md):

  layout A      field cards with a colour per role. A long table becomes one card per row,
                its short cells chips and its long cells labelled fields; a nested
                "- **X** — idea" list with "Why:" / "Trade-off:" children becomes labelled
                fields. Recommended, why, wedge (a competitor's weakness), trade-off and
                NOT FETCHED each wear their own colour token, in the light theme and both dark
                selectors, and a legend above the board names them.
  paragraph 2   a plain summary first: 4–6 short bullets (and an optional "What it cost" and
                "Read with care" box) above the original, which sits folded in
                <details class="full">.

Only the presentation changes. The markdown stays the single source: every copy button copies
the markdown the generator wrote, and the summaries never enter it. They are data, handed to
the page as JSON (`summaries_json`) in <script type="application/json" id="board-summaries">:

    {"sections": {"<block title>": {"bullets": [...], "cost": [...], "care": [...]}},
     "items": [{"section": "<block title>", "kind": "row" | "li", "index": i,
                "bullets": [...], "care": [...]}]}

`kind: "row"` is the i-th body row of the block's first table, `kind: "li"` the i-th item of its
first top-level list; the generator that knows its own markdown computes these anchors.

The source of the CSS and JS is the approved preview (docs/artifacts/research/previews/
make_previews.py: A_CSS, A_JS, MARK_JS; docs/artifacts/research/previews/manchester-option-a.html),
renamed so it cannot collide with a board's own classes (the page board already has `.card` and
`.chip`), and guarded so a table holding a form control, an image or an anchor id (the page
board's pickers) is never rewritten.

    CSS             role tokens, legend, marks, field cards, summaries — safe on any board
    READING_CSS     the preview's type scale for the markdown boards (research, outline)
    SCRIPT          the client-side layer; run after the board has rendered its blocks
    validate_summaries(summaries, titles, item_paths=None) -> [problem, ...]
    summaries_json(data) -> JSON safe inside a <script> block
"""
import json
import re

# --- the role colours -------------------------------------------------------------------
# Light first, on bare :root; then the same set for a dark system theme (unless the page is
# forced light) and for a page forced dark. The steel / brass / bone ground of the boards is
# theirs; these are the role accents only.
_LIGHT = ("--rec-bg:#F6EBC4;--rec-line:#C9A227;--rec-ink:#6E5408;--why:#1F5A85;--why-bg:#E3EEF7;"
          "--wedge:#2F6B4F;--wedge-bg:#E2F0E8;--trade:#9A3B1E;--trade-bg:#F7E4DC;"
          "--nf:#5E4A86;--nf-bg:#EEE8F6;--cost:#2D6A4F;--cost-bg:#DCEFE4")
_DARK = ("--rec-bg:#3A3218;--rec-line:#D8B23A;--rec-ink:#E9CF7A;--why:#8FC1EA;--why-bg:#17324A;"
         "--wedge:#8FD1AE;--wedge-bg:#163428;--trade:#F0A58A;--trade-bg:#3E2219;"
         "--nf:#C9B4EC;--nf-bg:#2B2340;--cost:#7CC9A0;--cost-bg:#1D3A2C")

CSS = (
    ":root{" + _LIGHT + "}\n"
    '@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){' + _DARK + "}}\n"
    ':root[data-theme="dark"]{' + _DARK + "}\n"
    r"""
.recmark{background:var(--rec-line);color:#1B2430;font-weight:700;border-radius:99px;padding:1px 8px;white-space:nowrap}
.nf{color:var(--nf);background:var(--nf-bg);border:1px dashed var(--nf);border-radius:5px;padding:0 5px;font-weight:600;white-space:nowrap}
.legend{display:flex;gap:8px;flex-wrap:wrap;font:600 13px/1 "Source Sans 3",system-ui,sans-serif;margin:0 0 20px}
.legend span{border-radius:99px;padding:6px 10px;border:1px solid var(--line)}
.legend .l-rec{background:var(--rec-line);color:#1B2430;border-color:var(--rec-line)}
.legend .l-why{color:var(--why);background:var(--why-bg)}
.legend .l-wedge{color:var(--wedge);background:var(--wedge-bg)}
.legend .l-trade{color:var(--trade);background:var(--trade-bg)}
.legend .l-nf{color:var(--nf);background:var(--nf-bg);border-style:dashed}
.fcards{display:grid;gap:14px;margin:12px 0 6px}
.fcard{border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:var(--ground);display:grid;gap:12px;min-width:0}
.fcard .fct{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap}
.fcard h3.fcardh{font:600 20px/1.3 Fraunces,Georgia,serif;color:var(--blue,var(--green));margin:0;overflow-wrap:anywhere;text-transform:none;letter-spacing:0}
.fcard h3.fcardh a{color:inherit}
.fchips{display:flex;gap:6px;flex-wrap:wrap}
.fchip{font:600 13px/1 "Source Sans 3",system-ui,sans-serif;border:1px solid var(--line);background:var(--paper);color:var(--ink-2);padding:6px 9px;border-radius:99px;font-variant-numeric:tabular-nums}
.fchip.rec{background:var(--rec-line);border-color:var(--rec-line);color:#1B2430}
.fld{display:grid;gap:4px;max-width:72ch;border-left:3px solid var(--line);padding-left:12px;min-width:0}
.fld>.lab,.subfld>.lab{font:700 12px/1.2 "Source Sans 3",system-ui,sans-serif;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3)}
.fld.why{border-left-color:var(--why)} .fld.why>.lab{color:var(--why)}
.fld.wedge{border-left-color:var(--wedge)} .fld.wedge>.lab{color:var(--wedge)}
.fld.trade{border-left-color:var(--trade)} .fld.trade>.lab{color:var(--trade)}
.fld .lead{font-weight:600;margin:0}
.fld .v{overflow-wrap:anywhere}
.fld details{margin-top:2px}
.fld summary{cursor:pointer;color:var(--blue,var(--green));font-weight:600;font-size:15px}
.fld details p{margin:6px 0 0;color:var(--ink-2)}
.fld.ev{border-left:0;padding-left:0;font:13px/1.45 "JetBrains Mono",ui-monospace,Menlo,monospace;color:var(--ink-3);overflow-wrap:anywhere}
.fcard.isrec,.lablist>li.isrec{border:2px solid var(--rec-line);background:var(--rec-bg)}
.lablist{padding-left:0}
.lablist>li{list-style:none;margin:0 0 14px;border:1px solid var(--line);border-radius:12px;padding:16px 18px;background:var(--ground);display:grid;gap:8px;max-width:none}
.lablist>li>.lead2{display:block;font:600 19px/1.35 Fraunces,Georgia,serif;color:var(--blue,var(--green))}
.lablist>li>.fchip.rec{justify-self:start}
.subfld{display:grid;gap:3px;margin:2px 0 0;padding-left:14px;border-left:2px solid var(--line)}
.subfld.trade{border-left-color:var(--trade)} .subfld.trade>.lab{color:var(--trade)}
.subfld.why{border-left-color:var(--why)} .subfld.why>.lab{color:var(--why)}
.subfld p{margin:0}
.md td .clamp{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.md tr.open td .clamp{-webkit-line-clamp:unset;display:block}
.md tr.open td{background:var(--why-bg)}
.hint{font-size:14px;color:var(--ink-3);margin:0 0 8px}
.plain{display:grid;gap:14px;margin:0 0 14px}
.plain ul{margin:0;padding-left:0;list-style:none;display:grid;gap:8px}
.plain li{position:relative;padding-left:22px;max-width:64ch}
.plain li::before{content:"";position:absolute;left:4px;top:.68em;width:8px;height:8px;border-radius:50%;background:var(--why)}
.plain .box{border-radius:10px;padding:12px 16px;border-left:4px solid}
.plain .box h4{margin:0 0 6px;font:700 13px/1.2 "Source Sans 3",system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase}
.plain .box.cost{background:var(--cost-bg);border-color:var(--cost)} .plain .box.cost h4{color:var(--cost)} .plain .box.cost li::before{background:var(--cost)}
.plain .box.care{background:var(--trade-bg);border-color:var(--trade)} .plain .box.care h4{color:var(--trade)} .plain .box.care li::before{background:var(--trade)}
details.full{border-top:1px dashed var(--line);padding-top:12px;min-width:0}
details.full>summary{cursor:pointer;font-weight:700;color:var(--blue,var(--green));min-height:32px}
details.full[open]>summary{margin-bottom:8px}
.summed:not(.md)>details.full>:not(summary){margin-top:12px}
@media (max-width:640px){.fcard,.lablist>li{padding:14px}}
""")

# The preview's type scale, for the boards built on scripts/_md_artifact.py. The page board
# keeps its own: its blocks are already collapsible cards with a one-line summary each.
READING_CSS = r"""
body{font-size:17px;line-height:1.65}
.md p,.md li{max-width:70ch}
section.sec{padding:26px 28px 30px;border-radius:12px}
section.sec h2{font-size:26px}
.md h3{font:600 19px/1.3 Fraunces,Georgia,serif;text-transform:none;letter-spacing:0;color:var(--blue);margin:22px 0 8px}
.md table{font-size:15px}
.md td,.md th{padding:9px 12px}
@media (max-width:640px){section.sec{padding:18px 14px 22px}}
"""

SCRIPT = r"""
(function(){
  var doc=document.getElementById('doc');if(!doc)return;
  var S={sections:{},items:[]};
  var sj=document.getElementById('board-summaries');
  if(sj){try{var d=JSON.parse(sj.textContent);S.sections=d.sections||{};S.items=d.items||[];}catch(e){}}
  function el(tag,cls){var e=document.createElement(tag);if(cls)e.className=cls;return e;}
  function bodies(){return [].slice.call(doc.querySelectorAll('.md[data-title]'));}
  function bodyOf(title){var b=bodies();for(var i=0;i<b.length;i++)if(b[i].getAttribute('data-title')===title)return b[i];return null;}
  function role(label){return /weak|wedge/i.test(label)?'wedge':/trade|risk/i.test(label)?'trade':/why/i.test(label)?'why':'';}
  function rich(cell){return [].some.call(cell.childNodes,function(n){return n.nodeType===1;});}
  function split(t){
    var m=t.match(/^(.{20,220}?[.!?])(\s|$)/);if(m)return [m[1],t.slice(m[1].length).trim()];
    if(t.length>200){var c=t.lastIndexOf(' ',200);if(c<80)c=200;return [t.slice(0,c)+' …',t.slice(c).trim()];}
    return [t,''];}
  function readRest(host,lead,rest){
    if(rest.length>40){host.appendChild(lead);var det=el('details');var s=el('summary');s.textContent='Read the rest';det.appendChild(s);
      var p=el('p');p.textContent=rest;det.appendChild(p);host.appendChild(det);return true;}
    return false;}
  function fld(label,cell,cls){
    var d=el('div','fld'+(cls?' '+cls:''));var l=el('span','lab');l.textContent=label;d.appendChild(l);
    if(typeof cell!=='string'&&rich(cell)){var v=el('div','v');while(cell.firstChild)v.appendChild(cell.firstChild);d.appendChild(v);return d;}
    var t=(typeof cell==='string'?cell:cell.textContent).trim(),sp=split(t),p=el('p','lead');
    p.textContent=sp[0];if(!readRest(d,p,sp[1])){p.textContent=t;d.appendChild(p);}
    return d;}

  // 1. Where each item summary lands: the i-th body row of a block's first table, or the i-th
  //    item of its first top-level list. Marked before any transform moves the rows.
  S.items.forEach(function(it,n){
    var b=bodyOf(it.section),x=null;if(!b)return;
    if(it.kind==='row'){var t=b.querySelector('table');if(t)x=t.querySelectorAll('tbody tr')[it.index];}
    else{var l=b.querySelector(':scope > ul, :scope > ol');if(l)x=l.children[it.index];}
    if(x)x.setAttribute('data-item',String(n));});

  // 2. Field cards. A table holding a control, an image, a fold or an anchor id is left as it
  //    is: the page board's pickers are found by those, and a card is rebuilt from text.
  var KEEP='input,select,textarea,button,iframe,img,details,[id]';
  [].slice.call(doc.querySelectorAll('.md table')).forEach(function(t){
    if(t.querySelector(KEEP))return;
    var hs=[].map.call(t.querySelectorAll('thead th'),function(h){return h.textContent.trim();});
    var rows=[].slice.call(t.querySelectorAll('tbody tr'));if(!rows.length||!hs.length)return;
    var marked=rows.some(function(r){return r.hasAttribute('data-item');});
    var b=t.closest('.md'),title=(b&&b.getAttribute('data-title'))||'';
    if(!marked&&/Keyword Universe|Keyword Distribution|NOT FETCHED/.test(title)){
      // long lists stay compact tables, two lines per cell; a tap opens the row
      t.querySelectorAll('tbody td').forEach(function(td){if(td.textContent.length>90){var w=el('div','clamp');while(td.firstChild)w.appendChild(td.firstChild);td.appendChild(w);}});
      rows.forEach(function(tr){tr.addEventListener('click',function(e){if(e.target.closest('a'))return;tr.classList.toggle('open');});});
      var hint=el('p','hint');hint.textContent='Tap a row to open its full text.';t.parentNode.insertBefore(hint,t);return;}
    var long=[].concat.apply([],rows.map(function(r){return [].slice.call(r.children);}))
      .filter(function(c){return c.textContent.length>140;}).length;
    if(!marked&&long<rows.length*0.5)return;           // short tables stay tables
    var ti=hs.findIndex(function(h){return /result|competitor|section|page|source|keyword|entity|angle/i.test(h);});if(ti<0)ti=0;
    var recCol=/recommended/i.test(hs.join(' ')),wrap=el('div','fcards');
    rows.forEach(function(r){
      var c=[].slice.call(r.children),card=el('article','fcard'),isrec=!recCol&&/Recommended/.test(r.textContent);
      if(r.hasAttribute('data-item'))card.setAttribute('data-item',r.getAttribute('data-item'));
      var top=el('div','fct'),h=el('h3','fcardh'),tc=c[ti],a=tc&&tc.querySelector('a[href]');
      var tt=(tc?tc.textContent.trim():'').replace(/^https?:\/\/(www\.)?/,'').replace(/\/$/,'');
      if(a){var link=el('a');link.href=a.getAttribute('href');link.textContent=tt;h.appendChild(link);}else h.textContent=tt;
      top.appendChild(h);var chips=el('div','fchips');top.appendChild(chips);card.appendChild(top);
      c.forEach(function(cell,i){if(i===ti)return;var v=cell.textContent.trim();if(!v||v==='—')return;
        var lab=hs[i]||'';
        if(/evidence|source/i.test(lab)){var e=el('div','fld ev');e.appendChild(document.createTextNode(lab+': '));
          while(cell.firstChild)e.appendChild(cell.firstChild);card.appendChild(e);return;}
        if(v.length<=40&&!rich(cell)){var ch=el('span','fchip'+(/recommended/i.test(lab)?' rec':''));
          ch.textContent=/recommended/i.test(lab)?'Recommended: '+v:(/^#$/.test(lab)?'#':lab+' ')+v;chips.appendChild(ch);return;}
        card.appendChild(fld(lab,cell,role(lab)));});
      if(isrec||card.querySelector('.fchip.rec'))card.classList.add('isrec');
      wrap.appendChild(card);});
    t.replaceWith(wrap);});

  // 3. Labelled lists: "- **X** — idea" items whose children say "Why:" or "Trade-off:".
  var LABEL=/^(Angle|Why|Trade-off|Why it could win)\s*:\s*([\s\S]*)$/;
  [].slice.call(doc.querySelectorAll('.md > ul, .md > ol')).forEach(function(ul){
    var lis=[].slice.call(ul.children);
    if(!lis.some(function(li){var s=li.querySelector(':scope > ul');
      return s&&[].some.call(s.children,function(x){return LABEL.test(x.textContent.trim());});}))return;
    ul.classList.add('lablist');
    lis.forEach(function(li){
      var sub=li.querySelector(':scope > ul'),ht=el('div','lhead');
      [].slice.call(li.childNodes).forEach(function(n){if(n!==sub)ht.appendChild(n);});
      var txt=ht.textContent.trim(),rec=/\(Recommended\)/.test(txt),m=txt.match(/^(\S+)\s+—\s+([\s\S]*)$/);
      if(m){
        var rest=m[2].replace(/\s*\(Recommended\)\s*/,' ').trim(),name='',idea=rest,k=rest.indexOf(': ');
        if(k>0&&k<=60&&rest.slice(0,k).indexOf('. ')<0){name=rest.slice(0,k);idea=rest.slice(k+2);}
        var lead=el('span','lead2');lead.textContent=m[1]+(name?' · '+name:'');li.appendChild(lead);
        if(rec){var chip=el('span','fchip rec');chip.textContent='Recommended';li.appendChild(chip);}
        li.appendChild(fld('The idea',idea));
      }else li.appendChild(ht);
      if(rec)li.classList.add('isrec');
      if(sub){var keep=el('ul');
        [].slice.call(sub.children).forEach(function(s){var mm=s.textContent.trim().match(LABEL);
          if(!mm){keep.appendChild(s);return;}
          var d=el('div','subfld'+(/trade/i.test(mm[1])?' trade':/why/i.test(mm[1])?' why':''));
          var l=el('span','lab');l.textContent=mm[1]==='Angle'?'Hook, intro and section order':mm[1];d.appendChild(l);
          var sp=split(mm[2]),p=el('p');p.textContent=sp[0];if(!readRest(d,p,sp[1])){p.textContent=mm[2];d.appendChild(p);}
          li.appendChild(d);});
        sub.remove();if(keep.children.length)li.appendChild(keep);}
    });});

  // 4. Plain summaries first; the original folds underneath, unchanged.
  function bullets(list){var u=el('ul');list.forEach(function(t){var li=el('li');li.textContent=t;u.appendChild(li);});return u;}
  function plain(sum){var w=el('div','plain');
    if(sum.bullets&&sum.bullets.length)w.appendChild(bullets(sum.bullets));
    [['cost','What it cost'],['care','Read with care']].forEach(function(k){
      if(sum[k[0]]&&sum[k[0]].length){var b=el('div','box '+k[0]);var h=el('h4');h.textContent=k[1];b.appendChild(h);b.appendChild(bullets(sum[k[0]]));w.appendChild(b);}});
    return w;}
  function fold(label){var d=el('details','full');var s=el('summary');s.textContent=label;d.appendChild(s);return d;}
  [].slice.call(doc.querySelectorAll('[data-item]')).forEach(function(x){
    var it=S.items[+x.getAttribute('data-item')];if(!it||x.tagName==='TR')return;
    var keep=[].slice.call(x.children).filter(function(n){return n.classList.contains('fct')||n.classList.contains('lead2')||(n.classList.contains('fchip')&&n.classList.contains('rec'));});
    var det=fold('The full text');
    [].slice.call(x.childNodes).forEach(function(n){if(keep.indexOf(n)<0)det.appendChild(n);});
    x.appendChild(plain(it));x.appendChild(det);x.classList.add('summed');});
  bodies().forEach(function(b){
    var sum=S.sections[b.getAttribute('data-title')]||S.sections[b.getAttribute('data-id')||'\u0000'];if(!sum)return;
    var det=fold('Full text, with every source and file path');
    while(b.firstChild)det.appendChild(b.firstChild);
    b.appendChild(plain(sum));b.appendChild(det);b.classList.add('summed');});

  // 5. The legend, and the two marks every board carries in its text.
  var legend=el('div','legend');legend.innerHTML='<span class="l-rec">Recommended</span><span class="l-why">Why / why it ranks</span><span class="l-wedge">Weakness · our wedge</span><span class="l-trade">Trade-off · risk</span><span class="l-nf">NOT FETCHED</span>';
  doc.parentNode.insertBefore(legend,doc);
  var w=document.createTreeWalker(doc,NodeFilter.SHOW_TEXT,null),hits=[];
  while(w.nextNode()){var n=w.currentNode;
    if(/NOT FETCHED|\(Recommended\)/.test(n.nodeValue)&&!n.parentNode.closest('.nf,.recmark,button,summary,textarea,script,style,option,label'))hits.push(n);}
  hits.forEach(function(n){var f=document.createDocumentFragment();n.nodeValue.split(/(NOT FETCHED|\(Recommended\))/).forEach(function(part){
    if(part==='NOT FETCHED'){var a=el('span','nf');a.textContent=part;f.appendChild(a);}
    else if(part==='(Recommended)'){var r=el('span','recmark');r.textContent='Recommended';f.appendChild(r);}
    else if(part)f.appendChild(document.createTextNode(part));});n.parentNode.replaceChild(f,n);});
})();
"""

# --- the summaries -----------------------------------------------------------------------
KINDS = ("bullets", "cost", "care")
MAX_BULLETS = 6
MAX_WORDS = 25
# A file path: "/" followed by a word and an extension (docs/x.md, data/settings.json).
FILE_PATH = re.compile(r"/[A-Za-z0-9_-]+\.[A-Za-z][A-Za-z0-9]{0,4}\b")
BACKTICK = re.compile(r"`[^`]*`")


def _check_entry(where, entry, p):
    if not isinstance(entry, dict):
        p.append(f"{where}: an object {{bullets, cost?, care?}}")
        return
    for k in entry:
        if k not in KINDS:
            p.append(f"{where}: unknown key {k!r} (bullets, cost, care)")
    if not entry.get("bullets"):
        p.append(f"{where}.bullets: the plain summary, 1–{MAX_BULLETS} bullets")
    for k in KINDS:
        if k not in entry:
            continue
        lst = entry[k]
        if not (isinstance(lst, list) and lst and all(isinstance(x, str) and x.strip() for x in lst)):
            p.append(f"{where}.{k}: a non-empty list of short sentences")
            continue
        if len(lst) > MAX_BULLETS:
            p.append(f"{where}.{k}: {len(lst)} bullets — at most {MAX_BULLETS}")
        for i, b in enumerate(lst):
            n = len(b.split())
            if n > MAX_WORDS:
                p.append(f"{where}.{k}[{i}]: {n} words — at most {MAX_WORDS}")
            if FILE_PATH.search(b):
                p.append(f"{where}.{k}[{i}]: names a file path — the path stays in the full text")
            if BACKTICK.search(b):
                p.append(f"{where}.{k}[{i}]: a backticked field — say it in plain words")


def validate_summaries(summaries, titles, item_paths=None):
    """Every problem with a `summaries` object, as strings. `titles` are the board's block
    titles; `item_paths` the record paths an item summary may name (None: no items allowed)."""
    p = []
    if summaries is None:
        return p
    if not isinstance(summaries, dict):
        return ["summaries: an object {sections, items}"]
    for k in summaries:
        if k not in ("sections", "items"):
            p.append(f"summaries: unknown key {k!r} (sections, items)")
    secs = summaries.get("sections", {})
    if not isinstance(secs, dict):
        p.append("summaries.sections: an object keyed by block title")
        secs = {}
    titles = set(titles)
    for t, entry in secs.items():
        if t not in titles:
            p.append(f"summaries.sections[{t!r}]: no block has this title")
        _check_entry(f"summaries.sections[{t!r}]", entry, p)
    items = summaries.get("items", {})
    if not isinstance(items, dict):
        p.append("summaries.items: an object keyed by record path")
        items = {}
    allowed = set(item_paths or ())
    for path, entry in items.items():
        if path not in allowed:
            p.append(f"summaries.items[{path!r}]: not a record path this board renders as a card")
        _check_entry(f"summaries.items[{path!r}]", entry, p)
    return p


def summaries_json(data):
    """JSON for a <script type="application/json"> block: nothing in it can close the block or
    open an HTML comment, and JSON.parse reads it back unchanged."""
    return json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
