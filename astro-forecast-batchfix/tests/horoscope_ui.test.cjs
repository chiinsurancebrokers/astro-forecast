const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const nodes={},buttons=[];
const t={date_label:'Date',card_heading:'Card',card_intro:'Intro',upright:'Upright',reversed:'Reversed',card_link:'Tarot',method:'Method',loading:'Loading',ready:'Ready',error:'Error'};
const signs=[{id:'Aries',name:'Aries',glyph:'A'},{id:'Taurus',name:'Taurus',glyph:'T'}];
function node(s){return nodes[s]||={textContent:'',innerHTML:'',hidden:true,className:'',handlers:{},addEventListener(event,fn){this.handlers[event]=fn;}};}
node('#horoscope-config').textContent=JSON.stringify({lang:'en',t,signs});
const stored={};
const sandbox={document:{querySelector:node,querySelectorAll:()=>buttons},Set,console,URLSearchParams,
 location:{search:''},localStorage:{getItem:k=>stored[k]??null,setItem:(k,v)=>{stored[k]=v;}},encodeURIComponent,Date,String,Number};
vm.createContext(sandbox);vm.runInContext(fs.readFileSync(path.join(__dirname,'../static/horoscope.js'),'utf8'),sandbox);
const evaluate=code=>vm.runInContext(code,sandbox);
const payload={sign:'Aries',sign_name:'Aries',glyph:'A',date:'2026-11-08',method:'M<b>',
 sections:[{key:'sky',title:'<script>x</script>',text:'Sky'},{key:'prompt',title:'Q',text:'Ask'}],
 tarot:{name:'<img src=x>',glyph:'✶',orientation:'reversed',interpretation:'I',reflection:'R',disclaimer:'D'}};
let html=evaluate('horoscopeMarkup('+JSON.stringify(payload)+')');
assert(!html.includes('<script>'));assert(html.includes('&lt;script&gt;'));assert(html.includes('class="reflection"'));
html=evaluate('cardMarkup('+JSON.stringify(payload.tarot)+')');
assert(!html.includes('<img'));assert(html.includes('tarot-card reversed'));assert(html.includes('/tarot?lang=en'));
assert.equal(evaluate("validSign('Aries')"),true);assert.equal(evaluate("validSign('Nope')"),false);
assert.match(evaluate('localDate()'),/^\d{4}-\d{2}-\d{2}$/);
let sent;
sandbox.fetch=async url=>{sent=url;return {ok:true,json:async()=>payload};};
(async()=>{
 await evaluate("load('Aries')");
 assert(sent.startsWith('/api/horoscope/daily?sign=Aries&lang=en&date='));
 assert.equal(node('#horoscope').hidden,false);assert.equal(node('#card').hidden,false);
 assert.equal(node('#status').textContent,'Ready');assert.equal(stored['horoscope-sign'],'Aries');
 sent=undefined;await evaluate("load('Nope')");assert.equal(sent,undefined);
 sandbox.fetch=async()=>({ok:false,json:async()=>({error:'internal details'})});
 await evaluate("load('Taurus')");
 assert.equal(node('#horoscope').hidden,true);assert.equal(node('#status').textContent,'Error');assert.equal(node('#status').className,'error');
 assert(!node('#status').textContent.includes('internal'));
 console.log('Horoscope UI passed: escaping, sign validation, fetch URL, storage and failure recovery.');
})().catch(e=>{console.error(e);process.exitCode=1;});
