const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const nodes={},t={reveal:'Reveal',major:'Major',minor:'Minor',upright:'Upright',reversed:'Reversed',reading:'Reading',general:'General',reflection:'Reflect',together:'Together',next:'Next',exercise:'Exercise',method:'Method',download:'Download',ready:'Ready',drawing:'Drawing',drawn:'Drawn',draw:'Draw',error:'Error'};
function node(s){return nodes[s]||={value:'',checked:true,hidden:false,disabled:false,textContent:'',innerHTML:'',handlers:{},addEventListener(event,fn){this.handlers[event]=fn;}};}
node('#tarot-config').textContent=JSON.stringify({lang:'en',t});node('#spread').value='three';
const sandbox={document:{querySelector:node},Set,console,URLSearchParams};
vm.createContext(sandbox);vm.runInContext(fs.readFileSync(path.join(__dirname,'../static/tarot.js'),'utf8'),sandbox);
const evaluate=code=>vm.runInContext(code,sandbox);
const card=i=>({name:'Card '+i,id:'id-'+i,position:i,position_label:'Position '+i,orientation:i===1?'reversed':'upright',glyph:'✶',arcana:'major',interpretation:'<script>unsafe</script>',reflection:'A question'});
sandbox.payload={cards:[card(0),card(1),card(2)],question:'<img src=x>',overall:'Overall',method:'Method',disclaimer:'Note'};
evaluate('reading=payload');let html=evaluate('cardsMarkup()');assert(!html.includes('Card 0'));assert(!html.includes('unsafe'));
evaluate('reveal(0)');assert(node('#cards').innerHTML.includes('Card 0'));assert(node('#reading').hidden===false?node('#reading').innerHTML==='':true);assert(!node('#reading').innerHTML.includes('unsafe'));
evaluate('reveal(0)');assert.equal(evaluate('revealed.size'),1);evaluate('reveal(-1)');assert.equal(evaluate('revealed.size'),1);
evaluate('reveal(1);reveal(2)');assert.equal(node('#reading').hidden,false);assert(node('#cards').innerHTML.includes('reversed'));assert(node('#reading').innerHTML.includes('&lt;script&gt;'));assert(!node('#reading').innerHTML.includes('<script>'));assert(node('#reading').innerHTML.includes('&lt;img'));assert.equal(node('#reveal-all').hidden,true);
let sent;
sandbox.fetch=async(url,args)=>{sent={url,args};return {ok:true,json:async()=>sandbox.payload};};
node('#question').value='New question';
(async()=>{
 await node('#tarot-form').handlers.submit({preventDefault(){}});
 assert.equal(sent.args.method,'POST');assert.equal(JSON.parse(sent.args.body).question,'New question');assert.equal(sent.url,'/api/tarot/draw');assert.equal(evaluate('revealed.size'),0);assert.equal(node('#reading').hidden,true);assert.equal(node('#draw').disabled,false);
 sandbox.fetch=async()=>({ok:false,json:async()=>({error:'internal details'})});await node('#tarot-form').handlers.submit({preventDefault(){}});assert.equal(node('#status').textContent,'Error');assert.equal(node('#spread-view').hidden,true);assert.equal(node('#draw').disabled,false);
 console.log('Tarot UI passed: reveal gating, reversals, escaping, new reading reset, POST and failure recovery.');
})().catch(e=>{console.error(e);process.exitCode=1;});
