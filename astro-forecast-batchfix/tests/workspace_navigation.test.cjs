const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(require('node:path').join(__dirname,'../static/workspace_navigation.js'),'utf8');
function run(hash,pathname='/platform'){
 const calls=[],handlers={},menu={open:true,contains:()=>false,querySelector:()=>({focus:()=>calls.push('focus-menu')}),querySelectorAll:()=>[]};
 const sandbox={window:{location:{pathname,hash},addEventListener:(name,fn)=>handlers[name]=fn},document:{querySelector:s=>s==='.workspace-menu'?menu:{focus:()=>calls.push('ask')},addEventListener:(name,fn)=>handlers[name]=fn},runAgent:(...args)=>calls.push(args),compareCharts:()=>calls.push('compatibility'),exploreGeo:()=>calls.push('geo'),openZodiacProfile:()=>calls.push('zodiac')};
 vm.runInNewContext(source,sandbox);return {calls,handlers,menu};
}
assert.equal(run('#timing').calls[0][0],'/api/agents/timing');
assert.equal(run('#natal').calls[0][0],'/api/natal');
assert.equal(run('#life-periods').calls[0][0],'/api/agents/life-periods');
for(const name of ['compatibility','geo','zodiac','ask'])assert.equal(run('#'+name).calls[0],name);
for(const name of ['merton','daath','raleigh'])assert.equal(run('#'+name).calls[0][1].specialist,name);
assert.equal(run('#timing','/natal-reading').calls.length,0);
const state=run('');state.handlers.keydown({key:'Escape'});assert.equal(state.menu.open,false);assert.equal(state.calls[0],'focus-menu');
const change=run('');change.handlers.hashchange();assert.equal(change.calls.length,0);
console.log('Workspace navigation: cross-page tools, specialist routes, page isolation and keyboard close passed.');
