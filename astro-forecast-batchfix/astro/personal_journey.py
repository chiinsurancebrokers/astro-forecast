"""User-authored chronology compared with calculated Western transit intervals."""
import re
import swisseph as swe
from datetime import datetime,timedelta
from .life_periods import transit_chapters
from .natal_books import build_book_natal_report,citation


def date_window(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}(?:-\d{2}(?:-\d{2})?)?',value):
        raise ValueError('Use YYYY, YYYY-MM or YYYY-MM-DD for a turning point.')
    parts=list(map(int,value.split('-')))
    start=datetime(parts[0],parts[1] if len(parts)>1 else 1,parts[2] if len(parts)>2 else 1)
    if len(parts)==1:end=datetime(parts[0]+1,1,1)
    elif len(parts)==2:end=datetime(parts[0]+(parts[1]==12),parts[1]%12+1,1)
    else:end=start+timedelta(days=1)
    return start,end,['year','month','day'][len(parts)-1]


def aspect_crossings(start,end,targets):
    """All daily-bracketed major contacts, retaining retrograde repetitions."""
    angles={0:'conjunction',60:'sextile',-60:'sextile',90:'square',-90:'square',120:'trine',-120:'trine',180:'opposition'}
    previous={};out=[];day=start-timedelta(days=1)
    while day<end:
        for planet,pid in [('Jupiter',swe.JUPITER),('Saturn',swe.SATURN)]:
            values,_=swe.calc_ut(swe.julday(day.year,day.month,day.day,12),pid,swe.FLG_MOSEPH|swe.FLG_SPEED)
            for target,longitude in targets.items():
                for angle,label in angles.items():
                    key=(planet,target,angle)
                    difference=(values[0]-longitude-angle+180)%360-180
                    last=previous.get(key)
                    if day>=start and last is not None and last*difference<0 and abs(difference-last)<180:
                        out.append({'date':day.strftime('%Y-%m-%d'),'planet':planet,'target':target,'aspect':label,'bracket_start':(day-timedelta(days=1)).strftime('%Y-%m-%d')})
                    previous[key]=difference
        day+=timedelta(days=1)
    return sorted(out,key=lambda c:(c['date'],c['planet'],c['target']))


def build_personal_journey(chart,latitude,longitude,payload,now=None):
    now=now or datetime.utcnow()
    events=payload.get('events')
    if not isinstance(events,list) or not 1<=len(events)<=12:raise ValueError('Enter between one and twelve turning points.')
    notes={}
    for key,limit in [('responses',3000),('goals',2000)]:
        value=payload.get(key,'')
        if not isinstance(value,str) or not 1<=len(value.strip())<=limit:raise ValueError('Enter your responses and goals within the displayed limits.')
        notes[key]=value.strip()
    report=build_book_natal_report(chart,latitude,longitude)
    western=report['chart'];comparisons=[];total_days=0
    targets={name:western['planets'][name]['longitude'] for name in ['Sun','Saturn']}
    birth=datetime(2000,1,1,12)+timedelta(days=chart['julian_day']-2451545.0)
    for event in events:
        if not isinstance(event,dict):raise ValueError('Each turning point needs a date and description.')
        description=event.get('description','')
        if not isinstance(description,str) or not 1<=len(description.strip())<=600:raise ValueError('Turning point descriptions must contain 1–600 characters.')
        start,end,precision=date_window(event.get('date'))
        finish,_,_=date_window(event.get('end_date') or event.get('date'))
        if event.get('end_date'):end=date_window(event['end_date'])[1]
        if finish.date()>now.date() or finish<start or start.date()<birth.date() or start.date()>now.date() or end-start>timedelta(days=365*30):raise ValueError('Turning points must follow birth, begin in the past and span no more than thirty years.')
        end=min(end,now.replace(hour=0,minute=0,second=0,microsecond=0)+timedelta(days=1))
        total_days+=(end-start).days
        if total_days>60*366:raise ValueError('The combined timeline exceeds sixty years.')
        chapters=transit_chapters(start,end,western['ascendant']['sign'],western['planets'])
        saturn=[c for c in chapters if c['planet']=='Saturn']
        summary='Saturn’s calculated house themes in this interval: '+ '; '.join(dict.fromkeys(c['title'].lower() for c in saturn))+'. These are subjects for comparison, not explanations of the event.'
        comparisons.append({'context_summary':summary,'date':event['date'],'end_date':event.get('end_date') or '', 'precision':precision,'description':description.strip(),
          'chapters':chapters,'contacts':aspect_crossings(start,end,targets),'interpretation':'Your account establishes what happened. The intervals below show all Jupiter and Saturn house phases within the period you supplied. Compare the house themes with your experience, including differences; their overlap does not establish the cause of an event.',
          'precision_note':('A year or range supplies broad context, not an exact event match.' if precision=='year' or event.get('end_date') else 'The comparison uses the date precision you supplied; an overlapping transit is not an event prediction.')})
    comparisons.sort(key=lambda e:e['date'])
    refs=[citation('raphael_guide',10,6,'Of the Nature of the Aspects'),citation('raphael_guide',126,122,'Transits in the Context of the Nativity'),citation('raphael_guide',127,123,'Transit Interpretation and Natal Condition'),citation('raphael_guide',15,11,'The Mundane Houses'),citation('raphael_guide',16,12,'The Twelfth House'),citation('bart_success',18,10,'How Astrology Helps: Personal Agency')]
    natal_context=report['reading']['sections'][:2]
    for section in natal_context:
        for ref in section.get('citations',[]):
            if ref not in refs:refs.append(ref)
    for ref in report['life_report']['references']:
        if ref not in refs:refs.append(ref)
    return {'title':'Your journey and the years ahead','natal_context':natal_context,'events':comparisons,'notes':notes,'zodiac_profile':report['zodiac_profile'],'life_report':report['life_report'],'future_contacts':aspect_crossings(datetime.fromisoformat(report['life_report']['start']),datetime.fromisoformat(report['life_report']['end']),targets),
      'preparation':['Choose one goal and define what progress would look like.','Identify a skill, conversation or source of support that would help.','Set one manageable action and a review date.','Compare the outcome with your real circumstances and revise the plan.'],
      'method':'Western tropical Jupiter and Saturn through natal whole-sign houses, sampled daily at noon UTC. All overlapping house intervals are included, without scoring how well they fit an event. Historical descriptions and responses are user-authored; preparation is editorial. Major Jupiter and Saturn contacts to the natal Sun and Saturn are also included using daily brackets; dates are approximate, not exact ingress times. Trines and sextiles are traditionally favourable, squares and oppositions adverse, while conjunctions require the planets involved to be considered; none establishes an event. Directions and solar returns are not included.',
      'privacy':'This preview processes the submitted notes to calculate this response. It does not write them to a database or send them to a language-model provider. Reloading clears the page; infrastructure logs may retain request metadata.', 'references':refs}
