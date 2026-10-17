/* The wheel is a view of the supplied tropical chart, never a second calculator. */
(() => {
  'use strict';
  const data=document.getElementById('natal-chart-data');
  const svg=document.getElementById('natal-wheel');
  if (!data || !svg) return;
  const chart=JSON.parse(data.textContent);
  const ns='http://www.w3.org/2000/svg';
  const glyphs=['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'];
  const symbols={Sun:'☉',Moon:'☽',Mercury:'☿',Venus:'♀',Mars:'♂',Jupiter:'♃',Saturn:'♄',Uranus:'♅',Neptune:'♆',Pluto:'♇'};
  const xy=(lon,r)=>{const a=(180+chart.ascendant.longitude-lon)*Math.PI/180;return [300+Math.cos(a)*r,300-Math.sin(a)*r];};
  function node(tag,attrs,text){const el=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))el.setAttribute(k,v);if(text!==undefined)el.textContent=text;svg.append(el);return el;}
  const line=(a,b,color='var(--line)')=>node('line',{x1:a[0],y1:a[1],x2:b[0],y2:b[1],stroke:color});
  const label=(p,text,color,size=16)=>node('text',{x:p[0],y:p[1],fill:color,'font-size':size,'text-anchor':'middle','dominant-baseline':'middle'},text);
  let selected='Sun';
  function draw(){
    svg.replaceChildren();node('title',{},'Computed tropical natal chart');
    for(const r of [225,190,150])node('circle',{cx:300,cy:300,r,fill:'none',stroke:'var(--line)'});
    for(let i=0;i<12;i++){
      line(xy(i*30,150),xy(i*30,225));
      label(xy(i*30+15,207),glyphs[i],'var(--gold)',23);
      const house=(i-Math.floor(chart.ascendant.longitude/30)+12)%12+1;
      label(xy(i*30+15,172),String(house),'var(--muted)',12);
    }
    line(xy(chart.ascendant.longitude,150),xy(chart.ascendant.longitude,235),'var(--gold)');
    label(xy(chart.ascendant.longitude,256),'ASC','var(--gold)',12);
    line(xy(chart.midheaven.longitude,150),xy(chart.midheaven.longitude,190),'var(--gold)');
    label(xy(chart.midheaven.longitude,136),'MC','var(--gold)',12);
    const items=Object.entries(chart.planets).map(([name,p])=>{const point=xy(p.longitude,147);return {name,p,point,right:point[0]>=300,y:point[1]};});
    for(const right of [false,true]){
      const group=items.filter(x=>x.right===right).sort((a,b)=>a.y-b.y);
      let last=95;
      for(const item of group){item.y=Math.max(item.y,last+29);last=item.y;}
      if(last>490)for(const item of group)item.y-=last-490;
    }
    for(const item of items){
      const color=item.name===selected?'var(--gold)':'var(--muted)';
      line(item.point,[item.right?530:70,item.y],color);
      node('circle',{cx:item.point[0],cy:item.point[1],r:item.name===selected?5:3,fill:color});
      const el=node('text',{x:item.right?590:10,y:item.y+5,fill:color,'font-size':14,'text-anchor':item.right?'end':'start'},`${symbols[item.name]||item.name} ${item.p.sign_deg.toFixed(1)}°${item.p.retrograde?' R':''}`);
      node('title',{},`${item.name}: ${item.p.sign}, ${item.p.sign_deg.toFixed(2)} degrees, house ${item.p.house}`);
      el.setAttribute('aria-hidden','true');
    }
    label([300,288],'YOUR NATAL CHART','var(--ink)',14);
    label([300,314],'Tropical · Whole sign','var(--muted)',12);
  }
  document.querySelectorAll('[data-planet]').forEach(button=>button.addEventListener('click',()=>{
    selected=button.dataset.planet;const p=chart.planets[selected];
    document.querySelectorAll('[data-planet]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    const target=document.getElementById('selected-placement');
    target.querySelector('h3').textContent=`${selected} · ${p.sign}`;
    target.querySelector('p').textContent=`${p.sign_deg.toFixed(2)}° · House ${p.house} · ${p.retrograde?'Retrograde':'Direct'}`;
    draw();
  }));
  draw();
})();
