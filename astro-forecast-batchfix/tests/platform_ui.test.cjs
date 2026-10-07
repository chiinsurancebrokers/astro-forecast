const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const nodes={};
function element(sel){return nodes[sel] ||= {textContent:'',innerHTML:'',value:'',open:false,checkValidity:()=>true,showModal(){this.open=true;},close(){this.open=false;}};}
const sandbox={document:{querySelector:element,querySelectorAll:()=>[]},Intl,Date,URLSearchParams,FormData,console};
const path=require('node:path');
const htmlSource=fs.readFileSync(path.join(__dirname,'../templates/platform.html'),'utf8');
const script=htmlSource.match(/<script>([\s\S]*?)<\/script>/)[1];
vm.createContext(sandbox);vm.runInContext(script,sandbox);
const evaluate=code=>vm.runInContext(code,sandbox);
const chart={ascendant:{sign:'Aries',sign_deg:23.7},planets:{Sun:{sign:'Capricorn',sign_deg:24.6,longitude:294.6,house:10},Moon:{sign:'Sagittarius',sign_deg:23.6,longitude:263.6,house:9}}};
sandbox.chart=chart;
let html=evaluate('renderReading(chart)');
assert(html.includes('<svg'));assert(html.includes('Lahiri specialist chart'));assert(html.includes('career and public life'));assert(!html.includes('NaN'));
sandbox.bundle={agents:[{agent:'Natal / Genethliacal Agent',evidence:[{type:'ascendant',sign:'Aries',degree:23.7},{type:'planet_placement',planet:'Sun',sign:'Capricorn',degree:24.6,house:10,condition:[]},{type:'planet_placement',planet:'Moon',sign:'Sagittarius',degree:23.6,house:9,condition:[]},{type:'natal_aspect',planets:['Sun','Moon'],aspect:'sextile',orb:2}]},{agent:'Career Agent',evidence:[{type:'career_house_placement',planet:'Sun',sign:'Capricorn',house:10}]},{agent:'Vimshottari Timing Agent',evidence:[{type:'vimshottari_current',mahadasha:'Saturn',antardasha:'Venus',antardasha_end:'2027-01-01'}]},{agent:'Multi-model Predictive Timing Agent',evidence:[{type:'timing_window',month:'2026-10',signals:[{area:'career',score:43}]}]}]};
html=evaluate('renderReading(bundle)');assert(html.includes('Major aspects'));assert(html.includes('Current major period: Saturn'));assert(html.includes('October 2026'));assert(!html.includes('evidence points'));assert(!html.includes('{"'));
sandbox.failed={answer:{primary:{error:'ANTHROPIC_API_KEY is not set.'}}};html=evaluate('renderReading(failed)');assert(html.includes('AI answer unavailable'));assert(!html.includes('ANTHROPIC_API_KEY'));assert(html.includes('Open my calculated reading'));
sandbox.attack={answer:{primary:{text:'<script>alert(1)</script>'},question:'test'}};html=evaluate('renderReading(attack)');assert(html.includes('&lt;script&gt;'));assert(!html.includes('<script>'));
evaluate('compareCharts()');assert(element('#reading-dialog').open);assert(element('#report-content').innerHTML.includes('type="date"'));assert(element('#report-content').innerHTML.includes('Birth latitude'));
evaluate('exploreGeo()');assert(element('#report-content').innerHTML.includes('Destination longitude'));
for(const [key,value] of Object.entries({year:'1975',month:'2',day:'8',hour:'11',minute:'20',latitude:'37.9838',longitude:'23.7275',offset:'2'}))element('#'+key).value=value;
let captured;sandbox.fetch=async url=>{captured=url;return {ok:true,json:async()=>chart};};
(async()=>{await evaluate("runAgent('/api/natal')");assert(element('#reading-dialog').open);assert(element('#report-content').innerHTML.includes('<svg'));assert(captured.includes('/api/natal?'));assert(element('#result').innerHTML.includes('Open reading'));element('#day').value='30';let rejected=false;try{evaluate('birthValues()')}catch{rejected=true;}assert(rejected);console.log('7 report rendering and interaction checks passed.');})().catch(err=>{console.error(err);process.exitCode=1;});


sandbox.bookReport={reading:{sections:[{title:'A coherent reading',paragraphs:['<script>unsafe</script>','Your narrative.']}],references:[{author:'Author',title:'Book',chapter:'Chapter',printed_page:12,pdf_page:18}],method:'Editorial synthesis'},basis_note:'Tropical basis',coverage:'Verified coverage',other_books:'Other methods'};
const bookHtml=evaluate('renderBookReport(bookReport)');
assert(bookHtml.indexOf('Your narrative.') < bookHtml.indexOf('Bibliography and interpretation notes'));
assert(!bookHtml.includes('<script>'));assert(bookHtml.includes('&lt;script&gt;'));
assert(bookHtml.includes('printed p. 12 / PDF p. 18'));
sandbox.career={agent:'Career Agent',evidence:[{type:'career_house_placement',planet:'Sun',sign:'Capricorn',house:10}]};
assert(evaluate('renderAgent(career)').includes('Work and public responsibility'));
sandbox.timing={agent:'Multi-model Predictive Timing Agent',evidence:[{type:'timing_window',month:'2026-10',signals:[{area:'sex_chemistry'}]}]};
assert(evaluate('renderAgent(timing)').includes('attraction and intimacy'));
assert(!evaluate('renderAgent(timing)').includes('Sex Chemistry'));

// Planet and house analysis remains readable and precedes the bibliography.
sandbox.detailedReport={reading:{sections:[],planet_sections:[{title:'Moon · Temperament',paragraphs:['Moon in Capricorn, house 9.','A considered reading.']}],house_sections:[{title:'House 9 · Study',paragraphs:['Study and wider horizons.','Ruler connection <script>unsafe</script>']}],references:[],method:'Source synthesis',delineation_note:'Whole-sign interpretation'},basis_note:'Tropical basis'};
const detailedHtml=evaluate('renderBookReport(detailedReport)');
assert(detailedHtml.includes('Your planets: character and expression'));
assert(detailedHtml.includes('Your twelve houses'));
assert(detailedHtml.includes('<summary>House 9 · Study</summary>'));
assert(detailedHtml.indexOf('A considered reading.') < detailedHtml.indexOf('Bibliography and interpretation notes'));
assert(detailedHtml.includes('&lt;script&gt;'));assert(!detailedHtml.includes('<script>'));

sandbox.life={title:'Life chapters',intro:'A dated reading.',current_chapters:[],next_transition:null,yearly:[{year:2027,topics:['Work'],preparation:['Review commitments.'],transitions:[]}],vedic:{note:'Separate Lahiri calendar',major_lord:'Saturn',sub_lord:'Venus',major_end:'2030-01-01',sub_end:'2027-01-01',lifetime:[],subperiods:[]},method:'Daily sampling',limitations:'Not a verified event forecast.',references:[{author:'Raphael',title:'Guide',chapter:'Transits',printed_page:122,pdf_page:126}]};
const lifeHtml=evaluate('renderReading({life_report:life})');
assert(lifeHtml.includes('Your year-by-year outlook'));
assert(lifeHtml.includes('Review commitments.'));
assert(lifeHtml.includes('1 January 2027'));
assert(lifeHtml.indexOf('Review commitments.') < lifeHtml.indexOf('Timing bibliography'));
assert(evaluate('renderLifeReport(life,true,false)').includes('<summary>Your life chapters · dates and preparation</summary>'));
assert(!evaluate('renderLifeReport(life,true,false)').includes('Timing bibliography'));

// Zodiac profiles separate sourced material, editorial questions and user notes.
sandbox.zodiac={sign:'Aquarius',title:'Aquarius · understanding yourself',intro:'One perspective.',sections:[{title:'Source perspective',paragraphs:['Checked source.']},{title:'Strengths',paragraphs:['Develop a skill.']},{title:'Balance',paragraphs:['Consider your habits.','Which conviction deserves review?']}],references:[{author:'White',title:'Guide',chapter:'Aquarius',printed_page:12,pdf_page:18}],method:'Source and application.'};
const zodiacHtml=evaluate('renderZodiacProfile(zodiac)');
assert(zodiacHtml.indexOf('Checked source.')<zodiacHtml.indexOf('Profile bibliography'));
assert(evaluate('zodiacChooser()').includes('Pisces'));
assert.equal((evaluate('zodiacChooser()').match(/<option/g)||[]).length,12);
sandbox.journeyNotes={turning_points:'2005 · <script>attack</script>',responses:'Studied and rebuilt a skill.',goals:'A meaningful home and work.'};
const journeyHtml=evaluate('renderJourney(zodiac,journeyNotes)');
assert(journeyHtml.includes('&lt;script&gt;attack&lt;/script&gt;'));
assert(!journeyHtml.includes('<script>'));
assert(journeyHtml.includes('your aspirations'));
assert(journeyHtml.includes('not a guaranteed outcome'));
assert(journeyHtml.includes('not correlate your history with transit dates'));
assert(!htmlSource.includes('localStorage'));
assert(!htmlSource.includes('fetch(\'/api/journey'));
