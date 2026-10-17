'use strict';
const config=JSON.parse(document.querySelector('#tarot-config').textContent),t=config.t;
const $=s=>document.querySelector(s);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let reading=null,revealed=new Set(),sequence=0;
function cardsMarkup(){
 return reading.cards.map((card,index)=>{
  const shown=revealed.has(index);
  return '<article class="slot"><p>'+esc(card.position_label)+'</p><button type="button" class="tarot-card '+(shown?'revealed ':'')+(shown&&card.orientation==='reversed'?'reversed':'')+'" data-card="'+index+'" '+(shown?'disabled':'')+' aria-label="'+esc(shown?card.name+' · '+t[card.orientation]:t.reveal+' '+(index+1))+'"><span class="position">'+(shown?esc(t[card.arcana]):'✧ · ✧ · ✧')+'</span><span class="symbol" aria-hidden="true">'+(shown?esc(card.glyph):'☾')+'</span><span class="title">'+esc(shown?card.name:t.reveal)+'</span><span class="muted">'+esc(shown?t[card.orientation]:String(index+1))+'</span></button></article>';
 }).join('');
}
function interpretationMarkup(){
 return '<h2>'+esc(t.reading)+'</h2><p>'+esc(reading.question||t.general)+'</p>'+reading.cards.map(card=>'<article class="interpretation"><p class="muted">'+esc(card.position_label)+'</p><h3>'+esc(card.name)+' · '+esc(t[card.orientation])+'</h3><p>'+esc(card.interpretation)+'</p><p class="reflection"><strong>'+esc(t.reflection)+':</strong> '+esc(card.reflection)+'</p></article>').join('')+'<article class="interpretation"><h3>'+esc(t.together)+'</h3><p>'+esc(reading.overall)+'</p><h3>'+esc(t.next)+'</h3><p>'+esc(t.exercise)+'</p></article><details><summary>'+esc(t.method)+'</summary><p>'+esc(reading.method)+'</p></details><p class="muted">'+esc(reading.disclaimer)+'</p><button id="download" type="button">'+esc(t.download)+'</button>';
}
function reveal(index){
 if(!reading||!Number.isInteger(index)||index<0||index>=reading.cards.length)return;
 revealed.add(index);$('#cards').innerHTML=cardsMarkup();
 if(revealed.size===reading.cards.length){$('#reveal-all').hidden=true;$('#reading').innerHTML=interpretationMarkup();$('#reading').hidden=false;$('#status').textContent=t.ready;}
}
$('#tarot-form').addEventListener('submit',async event=>{
 event.preventDefault();const request=++sequence;
 reading=null;revealed=new Set();$('#spread-view').hidden=true;$('#reading').hidden=true;$('#reading').innerHTML='';$('#cards').innerHTML='';$('#draw').disabled=true;$('#draw').textContent=t.drawing;$('#status').className='';$('#status').textContent=t.drawing;
 const body={question:$('#question').value.trim(),spread:$('#spread').value,lang:config.lang,reversals:$('#reversals').checked};
 try{const response=await fetch('/api/tarot/draw',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(body)});const result=await response.json();if(!response.ok)throw Error();if(request!==sequence)return;reading=result;$('#cards').className='cards'+(reading.cards.length===1?' single':'');$('#cards').innerHTML=cardsMarkup();$('#spread-view').hidden=false;$('#reveal-all').hidden=false;$('#status').textContent=t.drawn;}
 catch(error){if(request===sequence){$('#status').className='error';$('#status').textContent=t.error;}}
 finally{if(request===sequence){$('#draw').disabled=false;$('#draw').textContent=t.draw;}}
});
$('#cards').addEventListener('click',event=>{const button=event.target.closest('[data-card]');if(button)reveal(Number(button.dataset.card));});
$('#reveal-all').addEventListener('click',()=>{if(reading)reading.cards.forEach((_,i)=>revealed.add(i));if(reading)reveal(0);});
function readingText(){return [t.reading,reading.created_at,reading.question||t.general,...reading.cards.flatMap(c=>['',c.position_label,c.name+' · '+t[c.orientation],c.interpretation,c.reflection]),'',t.together,reading.overall,t.next,t.exercise,'',reading.method,reading.disclaimer].join('\n');}
$('#reading').addEventListener('click',event=>{
 if(!event.target.closest('#download')||!reading||revealed.size!==reading.cards.length)return;
 const url=URL.createObjectURL(new Blob(['\uFEFF'+readingText()],{type:'text/plain;charset=utf-8'})),anchor=document.createElement('a');anchor.href=url;anchor.download='tarot-'+reading.reading_id+'.txt';anchor.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
