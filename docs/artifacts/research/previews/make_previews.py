import pathlib,re
ROOT=pathlib.Path('/Users/apple/Downloads/BSUK')
src=(ROOT/'docs/artifacts/research/blue-staffy-puppies-manchester-uk.html').read_text()

COMMON_CSS = r"""
:root{--rec-bg:#F6EBC4;--rec-line:#C9A227;--rec-ink:#6E5408;--why:#1F5A85;--why-bg:#E3EEF7;--wedge:#2F6B4F;--wedge-bg:#E2F0E8;--trade:#9A3B1E;--trade-bg:#F7E4DC;--nf:#5E4A86;--nf-bg:#EEE8F6}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--rec-bg:#3A3218;--rec-line:#D8B23A;--rec-ink:#E9CF7A;--why:#8FC1EA;--why-bg:#17324A;--wedge:#8FD1AE;--wedge-bg:#163428;--trade:#F0A58A;--trade-bg:#3E2219;--nf:#C9B4EC;--nf-bg:#2B2340}}
:root[data-theme="dark"]{--rec-bg:#3A3218;--rec-line:#D8B23A;--rec-ink:#E9CF7A;--why:#8FC1EA;--why-bg:#17324A;--wedge:#8FD1AE;--wedge-bg:#163428;--trade:#F0A58A;--trade-bg:#3E2219;--nf:#C9B4EC;--nf-bg:#2B2340}
.recmark{background:var(--rec-line);color:#1B2430;font-weight:700;border-radius:99px;padding:1px 8px;white-space:nowrap}
.nf{color:var(--nf);background:var(--nf-bg);border:1px dashed var(--nf);border-radius:5px;padding:0 5px;font-weight:600;white-space:nowrap}
.legend{display:flex;gap:8px;flex-wrap:wrap;font:600 13px/1 "Source Sans 3",sans-serif;margin:0 0 20px}
.legend span{border-radius:99px;padding:6px 10px;border:1px solid var(--line)}
.legend .l-rec{background:var(--rec-line);color:#1B2430;border-color:var(--rec-line)}
.legend .l-why{color:var(--why);background:var(--why-bg)} .legend .l-wedge{color:var(--wedge);background:var(--wedge-bg)}
.legend .l-trade{color:var(--trade);background:var(--trade-bg)} .legend .l-nf{color:var(--nf);background:var(--nf-bg);border-style:dashed}

body{font-size:17px;line-height:1.65}
.preview-bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:var(--blue);color:var(--ground);padding:10px 16px;font:600 14px/1.4 "Source Sans 3",system-ui,sans-serif;display:flex;gap:10px;flex-wrap:wrap;align-items:center;justify-content:center}
.preview-bar b{background:#C9A227;color:#1B2430;border-radius:99px;padding:3px 10px}
.md p,.md li{max-width:70ch}
"""

A_CSS = COMMON_CSS + r"""
section.sec{padding:26px 28px 30px;border-radius:12px}
section.sec h2{font-size:26px}
.md h3{font:600 19px/1.3 Fraunces,Georgia,serif;text-transform:none;letter-spacing:0;color:var(--blue);margin:22px 0 8px}
.cards{display:grid;gap:14px;margin:12px 0 6px}
.card{border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:var(--ground);display:grid;gap:12px;min-width:0}
.card .ct{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap}
.card h3.cardh{font:600 20px/1.3 Fraunces,Georgia,serif;color:var(--blue);margin:0;overflow-wrap:anywhere;text-transform:none;letter-spacing:0}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{font:600 13px/1 "Source Sans 3",sans-serif;border:1px solid var(--line);background:var(--paper);color:var(--ink-2);padding:6px 9px;border-radius:99px;font-variant-numeric:tabular-nums}
.chip.rec{background:var(--rec-line);border-color:var(--rec-line);color:#1B2430}
.fld{display:grid;gap:4px;max-width:72ch}
.fld>.lab{font:700 12px/1.2 "Source Sans 3",sans-serif;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3)}
.fld{border-left:3px solid var(--line);padding-left:12px}
.fld.why{border-left-color:var(--why)} .fld.why>.lab{color:var(--why)}
.fld.wedge{border-left-color:var(--wedge)} .fld.wedge>.lab{color:var(--wedge)}
.fld.trade{border-left-color:var(--trade)} .fld.trade>.lab{color:var(--trade)}
.fld.ev{border-left:0;padding-left:0}
.card.isrec,.lablist>li.isrec{border:2px solid var(--rec-line);background:var(--rec-bg);border-radius:12px;padding:16px 18px}
.lablist>li{border:1px solid var(--line);border-radius:12px;padding:16px 18px;background:var(--ground)}
.fld .lead{font-weight:600;margin:0}
.fld details{margin-top:2px}
.fld summary{cursor:pointer;color:var(--blue);font-weight:600;font-size:15px}
.fld details p{margin:6px 0 0;color:var(--ink-2)}
.fld.ev{font:13px/1.45 "JetBrains Mono",ui-monospace,monospace;color:var(--ink-3);overflow-wrap:anywhere}
.lablist>li{list-style:none;margin:0 0 14px}
.lablist{padding-left:0}
.lablist>li>.lead2{display:block;font:600 19px/1.35 Fraunces,Georgia,serif;color:var(--blue)}
.subfld{display:grid;gap:3px;margin:10px 0 0;padding-left:14px;border-left:2px solid var(--line)}
.subfld>.lab{font:700 12px/1.2 "Source Sans 3",sans-serif;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3)}
.subfld.trade{border-left-color:var(--trade)} .subfld.trade>.lab{color:var(--trade)}
.subfld.why{border-left-color:var(--why)} .subfld.why>.lab{color:var(--why)}
.md table{font-size:15px}
.md td{padding:9px 12px} .md th{padding:9px 12px}
.md td .clamp{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.md tr.open td .clamp{-webkit-line-clamp:unset;display:block}
.md tr{cursor:default} .md tr.open td{background:var(--why-bg)}
.hint{font-size:14px;color:var(--ink-3);margin:0 0 8px}
@media (max-width:640px){section.sec{padding:18px 14px 22px}.card{padding:14px}}
"""

A_JS = r"""
(function(){
  function firstSentence(t){var m=t.match(/^(.{20,220}?[.!?])(\s|$)/);return m?m[1]:(t.length>200?t.slice(0,200)+'…':t);}
  function fld(label,text,cls){
    var d=document.createElement('div');d.className='fld'+(cls?' '+cls:'');
    var l=document.createElement('span');l.className='lab';l.textContent=label;d.appendChild(l);
    var lead=firstSentence(text);var p=document.createElement('p');p.className='lead';p.textContent=lead;d.appendChild(p);
    var rest=text.slice(lead.length).trim();
    if(rest.length>40){var det=document.createElement('details');var s=document.createElement('summary');s.textContent='Read the rest';det.appendChild(s);
      var pp=document.createElement('p');pp.textContent=rest;det.appendChild(pp);d.appendChild(det);}
    else if(rest){p.textContent=text;}
    return d;}
  document.querySelectorAll('.md table').forEach(function(t){
    var hs=[].map.call(t.querySelectorAll('thead th'),function(h){return h.textContent.trim();});
    var rows=[].slice.call(t.querySelectorAll('tbody tr'));if(!rows.length)return;
    var cells=[].concat.apply([],rows.map(function(r){return [].slice.call(r.children);}));
    var long=cells.filter(function(c){return c.textContent.length>140;}).length;
    var secTitle=(t.closest('section')||document).querySelector('h2').textContent;
    if(/Keyword Universe|Keyword Distribution|NOT FETCHED/.test(secTitle)){ // long lists stay compact tables, two lines per cell
      t.querySelectorAll('tbody td').forEach(function(td){if(td.textContent.length>90){var w=document.createElement('div');w.className='clamp';while(td.firstChild)w.appendChild(td.firstChild);td.appendChild(w);}});
      t.querySelectorAll('tbody tr').forEach(function(tr){tr.addEventListener('click',function(e){if(e.target.closest('a'))return;tr.classList.toggle('open');});});
      var hint=document.createElement('p');hint.className='hint';hint.textContent='Tap a row to open its full text.';t.parentNode.insertBefore(hint,t);return;}
    if(long<rows.length*0.5)return; // short tables stay tables
    var wrap=document.createElement('div');wrap.className='cards';
    rows.forEach(function(r){
      var c=[].slice.call(r.children),card=document.createElement('article');card.className='card';
      var ti=hs.findIndex(function(h){return /result|competitor|section group|page|source|keyword|entity|angle/i.test(h);});if(ti<0)ti=0;
      var top=document.createElement('div');top.className='ct';var h=document.createElement('h3');h.className='cardh';
      var tt=c[ti]?c[ti].textContent.trim():'';h.textContent=tt.replace(/^https?:\/\/(www\.)?/,'').replace(/\/$/,'');top.appendChild(h);
      var chips=document.createElement('div');chips.className='chips';top.appendChild(chips);card.appendChild(top);
      c.forEach(function(cell,i){if(i===ti)return;var v=cell.textContent.trim();if(!v||v==='—')return;
        var lab=hs[i]||'';
        if(v.length<=40&&!/evidence|source/i.test(lab)){var ch=document.createElement('span');ch.className='chip'+(/recommended/i.test(lab)?' rec':'');
          ch.textContent=(/^#$/.test(lab)?'#':lab+' ')+v;if(/recommended/i.test(lab))ch.textContent='Recommended: '+v;chips.appendChild(ch);return;}
        if(/evidence|source/i.test(lab)){var e=document.createElement('div');e.className='fld ev';e.textContent=lab+': '+v;card.appendChild(e);return;}
        card.appendChild(fld(lab,v,/weak|wedge/i.test(lab)?'wedge':/trade|risk/i.test(lab)?'trade':/why/i.test(lab)?'why':''));});
      if(/Recommended/.test(r.textContent)&&!/recommended/i.test(hs.join(' ')))card.classList.add('isrec');
      if(card.querySelector('.chip.rec'))card.classList.add('isrec');
      wrap.appendChild(card);});
    t.replaceWith(wrap);});
  // nested "- **X** — text" lists with "Label: text" children
  document.querySelectorAll('.md > ul').forEach(function(ul){
    var lis=[].slice.call(ul.children);if(!lis.some(function(li){return li.querySelector(':scope > ul');}))return;
    ul.classList.add('lablist');
    lis.forEach(function(li){
      var sub=li.querySelector(':scope > ul');
      var head=[].slice.call(li.childNodes).filter(function(n){return n!==sub;});
      var ht=document.createElement('div');head.forEach(function(n){ht.appendChild(n);});
      var txt=ht.textContent.trim();var m=txt.match(/^(\S+)\s+—\s+([^:]+):\s*([\s\S]*)$/);
      var lead=document.createElement('span');lead.className='lead2';
      if(m){lead.textContent=m[1]+' · '+m[2];li.appendChild(lead);var f=fld('The idea',m[3].replace(/\*\*\(Recommended\)\*\*|\(Recommended\)/,'').trim());li.appendChild(f);
        if(/\(Recommended\)/.test(txt)){li.classList.add('isrec');var c=document.createElement('span');c.className='chip rec';c.textContent='Recommended';c.style.justifySelf='start';li.insertBefore(c,f);}}
      else{li.appendChild(ht);}
      if(sub){[].slice.call(sub.children).forEach(function(s){var st=s.textContent.trim();var mm=st.match(/^(Angle|Why|Trade-off|Why it could win)\s*:\s*([\s\S]*)$/);
        if(mm){var d=document.createElement('div');d.className='subfld'+(/trade/i.test(mm[1])?' trade':/why/i.test(mm[1])?' why':'');
          var l=document.createElement('span');l.className='lab';l.textContent=mm[1]==='Angle'?'Hook, intro and section order':mm[1];d.appendChild(l);
          var lead=firstSentence(mm[2]);var p=document.createElement('p');p.style.margin='0';p.textContent=lead;d.appendChild(p);
          var rest=mm[2].slice(lead.length).trim();if(rest.length>40){var det=document.createElement('details');var sm=document.createElement('summary');sm.textContent='Read the rest';det.appendChild(sm);var pp=document.createElement('p');pp.textContent=rest;det.appendChild(pp);d.appendChild(det);}
          li.appendChild(d);} else {li.appendChild(s.cloneNode(true));}});sub.remove();}
    });});
})();
"""

B_CSS = COMMON_CSS + r"""
@media (min-width:1100px){.wrap{max-width:1320px;display:grid;grid-template-columns:240px minmax(0,1fr);column-gap:28px}
 header.mast,.toolbar{grid-column:1/-1} nav.toc{grid-column:1;position:sticky;top:60px;align-self:start;flex-direction:column;flex-wrap:nowrap;gap:8px;max-height:calc(100vh - 80px);overflow:auto;border-right:1px solid var(--line);padding-right:12px} main#doc{grid-column:2;min-width:0}}
.md table{font-size:15px}
.md td{padding:10px 12px;cursor:pointer} .md th{padding:9px 12px}
.md td .clamp{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.md tr.open td .clamp{-webkit-line-clamp:unset;display:block}
.md tr.open td{background:var(--why-bg)}
.md tr.isrec td{background:var(--rec-bg)} .md tr.isrec td:first-child{box-shadow:inset 4px 0 0 var(--rec-line)}
.md th.c-why{color:var(--why);border-bottom-color:var(--why)} .md th.c-wedge{color:var(--wedge);border-bottom-color:var(--wedge)} .md th.c-trade{color:var(--trade);border-bottom-color:var(--trade)} .md th.c-rec{color:var(--rec-ink);border-bottom-color:var(--rec-line)}
.md li.isrec{background:var(--rec-bg);border-left:4px solid var(--rec-line);padding:6px 10px;border-radius:6px}
.md td .more{color:var(--blue);font-weight:600;font-size:13px}
.md li .clamp{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;cursor:pointer}
.md li .clamp.open{-webkit-line-clamp:unset;display:block}
.hint{font-size:14px;color:var(--ink-3);margin:0 0 8px}
"""

B_JS = r"""
(function(){
  document.querySelectorAll('.md table').forEach(function(t){t.querySelectorAll('thead th').forEach(function(th){var x=th.textContent;th.classList.add(/weak|wedge/i.test(x)?'c-wedge':/trade|risk/i.test(x)?'c-trade':/recommended/i.test(x)?'c-rec':/why/i.test(x)?'c-why':'x');});
    t.querySelectorAll('tbody tr').forEach(function(tr){if(/\(Recommended\)|Recommended/.test(tr.textContent)&&!/recommended/i.test(t.querySelector('thead').textContent))tr.classList.add('isrec');});});
  document.querySelectorAll('.md > ul > li').forEach(function(li){if(/\(Recommended\)/.test(li.textContent))li.classList.add('isrec');});
  document.querySelectorAll('.md table').forEach(function(t){
    var any=false;
    t.querySelectorAll('tbody td').forEach(function(td){if(td.textContent.length>90){any=true;var w=document.createElement('div');w.className='clamp';while(td.firstChild)w.appendChild(td.firstChild);td.appendChild(w);}});
    if(any){var h=document.createElement('p');h.className='hint';h.textContent='Tap a row to open its full text.';t.parentNode.insertBefore(h,t);
      t.querySelectorAll('tbody tr').forEach(function(tr){tr.addEventListener('click',function(e){if(e.target.closest('a'))return;tr.classList.toggle('open');});});}});
  document.querySelectorAll('.md li').forEach(function(li){if(li.querySelector('ul'))return;if(li.textContent.length>260){var w=document.createElement('span');w.className='clamp';while(li.firstChild)w.appendChild(li.firstChild);li.appendChild(w);w.addEventListener('click',function(){w.classList.toggle('open');});}});
})();
"""

MARK_JS = r'''
(function(){
  var legend=document.createElement('div');legend.className='legend';legend.innerHTML='<span class="l-rec">Recommended</span><span class="l-why">Why / why it ranks</span><span class="l-wedge">Weakness · our wedge</span><span class="l-trade">Trade-off · risk</span><span class="l-nf">NOT FETCHED</span>';
  var doc=document.getElementById('doc');doc.parentNode.insertBefore(legend,doc);
  var w=document.createTreeWalker(doc,NodeFilter.SHOW_TEXT,null);var hits=[];
  while(w.nextNode()){var n=w.currentNode;if(/NOT FETCHED|\(Recommended\)/.test(n.nodeValue)&&!n.parentNode.closest('.nf,.recmark,button,summary'))hits.push(n);}
  hits.forEach(function(n){var f=document.createDocumentFragment();n.nodeValue.split(/(NOT FETCHED|\(Recommended\))/).forEach(function(part){
    if(part==='NOT FETCHED'){var a=document.createElement('span');a.className='nf';a.textContent=part;f.appendChild(a);}
    else if(part==='(Recommended)'){var b=document.createElement('span');b.className='recmark';b.textContent='Recommended';f.appendChild(b);}
    else f.appendChild(document.createTextNode(part));});n.parentNode.replaceChild(f,n);});
})();
'''

def build(css, js, label, out, title):
    js = js + MARK_JS
    h=src
    h=re.sub(r'<title>.*?</title>', '<title>'+title+'</title>', h, count=1, flags=re.S)
    h=h.replace('</style>', css+'\n</style>',1)
    h=h.replace('<div class="wrap">','<div class="preview-bar">'+label+'</div>\n<div class="wrap">',1)
    h=h.replace('</body>','<script>\n'+js+'\n</script>\n</body>',1)
    (ROOT/out).write_text(h)
    print('wrote',out,len(h))

build(A_CSS,A_JS,'<b>Option A · field cards · Recommended</b> Preview of the real Manchester board. Only the layout changes; copy buttons copy the same markdown.','docs/artifacts/research/previews/manchester-option-a.html','Board Layout Option A')
build(B_CSS,B_JS,'<b>Option B · summary table + drawer</b> Preview of the real Manchester board. Long cells show two lines; tap a row to open it.','docs/artifacts/research/previews/manchester-option-b.html','Board Layout Option B')
