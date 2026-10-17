/* Shared navigation: deep links open the existing dashboard tools. */
(() => {
  'use strict';
  const menu=document.querySelector('.workspace-menu');
  if(menu){
    document.addEventListener('keydown',event=>{if(event.key==='Escape' && menu.open){menu.open=false;menu.querySelector('summary').focus();}});
    document.addEventListener('click',event=>{if(!menu.contains(event.target))menu.open=false;});
    menu.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{menu.open=false;}));
  }
  if(window.location.pathname!=='/platform')return;
  const endpoints={'#natal':'/api/natal','#timing':'/api/agents/timing','#life-periods':'/api/agents/life-periods','#career':'/api/agents/career'};
  function openView(){
    const hash=window.location.hash;
    if(endpoints[hash]){runAgent(endpoints[hash]);return;}
    if(hash==='#compatibility')compareCharts();
    else if(hash==='#geo')exploreGeo();
    else if(hash==='#zodiac')openZodiacProfile();
    else if(['#merton','#daath','#raleigh'].includes(hash))runAgent('/api/agents/historical',{specialist:hash.slice(1)});
    else if(hash==='#ask')document.querySelector('#question').focus();
  }
  window.addEventListener('hashchange',openView);
  openView();
})();
