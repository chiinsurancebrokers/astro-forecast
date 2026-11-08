'use strict';
const config=JSON.parse(document.querySelector('#horoscope-config').textContent),t=config.t;
const $=s=>document.querySelector(s);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let sequence=0,selected=null;
const validSign=id=>config.signs.some(s=>s.id===id);
function localDate(){const d=new Date(),p=n=>String(n).padStart(2,'0');return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate());}
function store(sign){try{localStorage.setItem('horoscope-sign',sign);}catch(e){}}
function recall(){try{return localStorage.getItem('horoscope-sign');}catch(e){return null;}}
function horoscopeMarkup(data){
 return '<h2>'+esc(data.glyph)+' '+esc(data.sign_name)+'</h2><p class="date">'+esc(t.date_label)+': '+esc(data.date)+'</p>'
  +data.sections.map(s=>'<h3>'+esc(s.title)+'</h3><p'+(s.key==='prompt'?' class="reflection"':'')+'>'+esc(s.text)+'</p>').join('')
  +'<details><summary>'+esc(t.method)+'</summary><p class="muted">'+esc(data.method)+'</p></details>';
}
function cardMarkup(card){
 const rev=card.orientation==='reversed';
 return '<h2>'+esc(t.card_heading)+'</h2><p class="muted">'+esc(t.card_intro)+'</p><div class="card">'
  +'<div class="tarot-card'+(rev?' reversed':'')+'"><span class="symbol" aria-hidden="true">'+esc(card.glyph)+'</span><span class="title">'+esc(card.name)+'</span></div>'
  +'<div class="card-text"><p><strong>'+esc(card.name)+' · '+esc(t[card.orientation]||card.orientation)+'</strong></p><p>'+esc(card.interpretation)+'</p><p class="reflection">'+esc(card.reflection)+'</p>'
  +'<p><a href="/tarot?lang='+encodeURIComponent(config.lang)+'">'+esc(t.card_link)+'</a></p><p class="muted">'+esc(card.disclaimer)+'</p></div></div>';
}
function markSelected(){document.querySelectorAll('[data-sign]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.sign===selected)));}
async function load(sign){
 if(!validSign(sign))return;
 const request=++sequence;selected=sign;markSelected();
 $('#status').className='';$('#status').textContent=t.loading;
 try{
  const url='/api/horoscope/daily?sign='+encodeURIComponent(sign)+'&lang='+encodeURIComponent(config.lang)+'&date='+encodeURIComponent(localDate());
  const response=await fetch(url,{headers:{Accept:'application/json'}});
  const data=await response.json();
  if(request!==sequence)return;
  if(!response.ok||!data||!data.sections)throw new Error('bad response');
  $('#horoscope').innerHTML=horoscopeMarkup(data);$('#horoscope').hidden=false;
  $('#card').innerHTML=cardMarkup(data.tarot);$('#card').hidden=false;
  $('#status').textContent=t.ready;store(sign);
 }catch(error){
  if(request===sequence){$('#horoscope').hidden=true;$('#card').hidden=true;$('#status').className='error';$('#status').textContent=t.error;}
 }
}
$('#signs').addEventListener('click',event=>{const b=event.target.closest('[data-sign]');if(b)load(b.dataset.sign);});
const fromQuery=new URLSearchParams(location.search).get('sign'),first=validSign(fromQuery)?fromQuery:recall();
if(validSign(first))load(first);
