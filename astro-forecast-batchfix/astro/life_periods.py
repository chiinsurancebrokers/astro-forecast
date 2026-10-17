"""Dated planning chapters, with Western and Lahiri methods kept distinct.

Transit boundaries are sampled at noon UTC each day, hence date resolution,
not exact ingress instants. Preparation prompts are editorial applications of
verified natal house topics, not forecasts or professional advice.
"""
from datetime import datetime, timedelta
import swisseph as swe
from .dasha import build_mahadashas, current_period
from .ephemeris import sign_of, whole_sign_house_of
from .western_delineation import HOUSE_TOPICS, RULERS, SIGNS, SIGN_TRAITS

PREPARATION = {
 1:['Write down the commitments you want to keep and the roles you want to reconsider.','Choose one manageable change to test before making it part of your routine.'],
 2:['Make an inventory of ongoing commitments, resources and deadlines.','Clarify your priorities and review them against your actual circumstances.'],
 3:['Identify a skill or subject to study steadily.','Review how you communicate and maintain contact with people around you.'],
 4:['Discuss the practical needs of your home and family.','Set aside time to organise property or household records and responsibilities.'],
 5:['Make space for a creative activity or pleasure that matters to you.','Review how you balance enjoyment with your other responsibilities.'],
 6:['List recurring tasks and decide which need clearer routines or shared responsibility.','Agree expectations with the people involved in your daily work.'],
 7:['Discuss expectations, roles and boundaries in an important partnership.','Put shared responsibilities and unresolved questions into clear language.'],
 8:['Clarify the records, agreements and responsibilities connected to shared resources.','Discuss expectations openly before making a shared commitment.'],
 9:['Choose a study, travel or learning goal that broadens your perspective.','Review the assumptions behind a major decision and seek another informed view.'],
 10:['Define the contribution you want your work to make.','Identify a skill, responsibility or conversation that could help you develop that contribution.'],
 11:['Reconnect with people whose interests or aims you share.','Select one longer-term aspiration and identify the next practical step with others.'],
 12:['Notice private pressures that take more energy than they receive.','Create time to review unfinished matters and clarify personal boundaries.'],
}


def _date(value):
    return value.strftime('%Y-%m-%d')


def transit_chapters(start, end, asc_sign, planets):
    chapters = []
    for name,pid in [('Jupiter',swe.JUPITER),('Saturn',swe.SATURN)]:
        cursor = start
        segment_start = start
        active = None
        seen = set()
        while cursor <= end:
            jd = swe.julday(cursor.year,cursor.month,cursor.day,12.0)
            pos,_ = swe.calc_ut(jd,pid,swe.FLG_MOSEPH|swe.FLG_SPEED)
            sign,_ = sign_of(pos[0])
            house = whole_sign_house_of(sign,asc_sign)
            key = (sign,house)
            if active is None:
                active = key
            elif key != active:
                chapters.append(_chapter(name,active,segment_start,cursor,planets,active in seen))
                seen.add(active)
                segment_start = cursor
                active = key
            cursor += timedelta(days=1)
        if segment_start < end:
            chapters.append(_chapter(name,active,segment_start,end,planets,active in seen))
    return sorted(chapters,key=lambda c:(c['start'],c['planet']))


def _chapter(name,key,start,end,planets,revisited):
    sign,house = key
    topic = HOUSE_TOPICS[house][1]
    natal = planets[name]
    natal_theme,_ = SIGN_TRAITS[name][SIGNS.index(natal['sign'])]
    present = [p for p,v in planets.items() if v['house']==house]
    paragraphs = [
      f"This dated chapter places {name} in {sign}, passing through your natal house {house}. The area to examine is {topic}. Changes between chapters mark calculated house boundaries; they do not establish that a life event will occur.",
      f"Your natal {name} is in {natal['sign']}, house {natal['house']}. White’s descriptive themes there include {natal_theme}. Read the current chapter through that birth-chart context, rather than treating a passing planet as a separate prediction.",
    ]
    if present:
        paragraphs.append('The natal house also contains '+', '.join(present)+'. Revisit those planetary readings when reviewing this area of life; house occupation alone does not mean an exact transit aspect is taking place.')
    if revisited:
        paragraphs.append('The planet has returned to a house it already visited in this timeline. Retrograde motion can create several entries into the same area. Use the return as a review point for an existing plan rather than assuming that every entry starts a new life event.')
    return {'planet':name,'sign':sign,'house':house,'start':_date(start),'end':_date(end),
            'title':HOUSE_TOPICS[house][0], 'paragraphs':paragraphs,'preparation':PREPARATION[house],
            'revisited':revisited,'end_is_horizon':False}


def build_life_period_report(lahiri_chart, western_chart, birth_dt, start, cite, years=5):
    if not western_chart:
        return None
    if not 1 <= years <= 5:
        raise ValueError('Choose a horizon from one to five years.')
    start = datetime(start.year,start.month,start.day)
    try:
        end = start.replace(year=start.year+years)
    except ValueError:
        end = start.replace(year=start.year+years,day=28)
    planets = western_chart['planets']
    chapters = transit_chapters(start,end,western_chart['ascendant']['sign'],planets)
    for chapter in chapters:
        chapter['start_is_report_boundary'] = chapter['start']==_date(start)
        chapter['end_is_horizon'] = chapter['end']==_date(end)
    for name in ['Jupiter','Saturn']:
        previous = None
        for chapter in [c for c in chapters if c['planet']==name]:
            chapter['from_house'] = previous['house'] if previous else None
            chapter['from_title'] = previous['title'] if previous else None
            if previous:
                chapter['paragraphs'].insert(1, f"Compared with the preceding chapter, the focus moves from {HOUSE_TOPICS[previous['house']][1]} toward {HOUSE_TOPICS[chapter['house']][1]}. Carry forward what you have learned or organised in the earlier area, then decide which commitments in the new area deserve attention. A date boundary does not require an abrupt life change.")
            previous = chapter
    current = [c for c in chapters if c['start']==_date(start)]
    forthcoming = sorted([c for c in chapters if c['start']>_date(start)],key=lambda c:c['start'])
    yearly = []
    for year in range(start.year,end.year+1):
        windows = [c for c in chapters if c['start'] < f'{year+1}-01-01' and c['end'] > f'{year}-01-01']
        if not windows:
            continue
        houses = sorted({c['house'] for c in windows})
        yearly.append({'year':year,'topics':[HOUSE_TOPICS[h][0] for h in houses],
                       'preparation':[PREPARATION[h][0] for h in houses],
                       'transitions':[c for c in forthcoming if c['start'][:4]==str(year)]})
    periods = build_mahadashas(birth_dt,lahiri_chart['planets']['Moon']['longitude'])
    md,ad = current_period(periods,start)
    # A lifetime reference, clipped at age 100, rather than claims about past events.
    life_end = birth_dt+timedelta(days=round(100*365.2425))
    lifetime = []
    subperiods = []
    for p in periods:
        if p['start']>=life_end:
            continue
        finish = min(p['end'],life_end)
        lifetime.append({'lord':p['lord'],'start':_date(p['start']),'end':_date(finish),
                         'age_start':round((p['start']-birth_dt).days/365.2425,1),
                         'age_end':round((finish-birth_dt).days/365.2425,1),
                         'current':p is md,'end_is_horizon':finish==life_end})
        for sub in p['antardashas']:
            if sub['end']>start and sub['start']<end:
                subperiods.append({'major_lord':p['lord'],'lord':sub['lord'],'start':_date(sub['start']),
                                  'end':_date(sub['end']),'current':sub is ad})
    refs = [cite('raphael_guide',126,122,'Transits in the Context of the Nativity'),
            cite('raphael_guide',127,123,'Transit Interpretation and Natal Condition'),
            cite('raphael_guide',15,11,'The Mundane Houses'),
            cite('raphael_guide',16,12,'The Twelfth House'),
            cite('white_guide',46,40,'The Radix'),cite('white_guide',45,39,'Note on the Planetary Sign Descriptions')]
    for name in ['Jupiter','Saturn']:
        p = planets[name];_,page = SIGN_TRAITS[name][SIGNS.index(p['sign'])]
        refs.append(cite('white_guide',page,page-6,name+' in '+p['sign']))
    refs.append(cite('bart_success',18,10,'How Astrology Helps: Personal Agency'))
    next_transition = forthcoming[0] if forthcoming else None
    return {'title':'Your life chapters and preparation','start':_date(start),'end':_date(end),
      'intro':'The natal reading describes enduring themes. This timeline adds dates for reviewing how those themes may be expressed as planetary periods change. Use it alongside your actual choices, commitments and circumstances. Following Belle Bart’s emphasis on personal agency, prepare by naming one pattern to keep, one response to change and one manageable action; review what actually happened afterwards. This preparation exercise is an editorial application, not a forecast of an event.',
      'current_chapters':current,'next_transition':next_transition,'chapters':chapters,'yearly':yearly,
      'vedic':{'major_lord':md['lord'] if md else None,'sub_lord':ad['lord'] if ad else None,
               'major_end':_date(md['end']) if md else None,'sub_end':_date(ad['end']) if ad else None,
               'lifetime':lifetime,'subperiods':subperiods,
               'note':'Separate Lahiri / Vimshottari calendar, calculated from the sidereal Moon’s nakshatra and the remaining period at birth. Dates are shown in UTC, with the birth-time offset applied, and ages are approximate; the Western bibliography is not used to invent Vedic period meanings. No dedicated Vimshottari interpretation source has yet been verified in the uploaded books.'},
      'references':refs,
      'method':'Western tropical Jupiter and Saturn, mapped to the natal whole-sign houses and sampled once per day at noon UTC. Boundaries have day-level resolution, not exact ingress times. Repeated entries caused by retrograde motion are retained. Periods beginning on the report start are clipped current periods; endings at the report horizon are not ingress dates. Preparation prompts are editorial applications of house topics.',
      'limitations':'Raphael asks readers to interpret transits in the context of the nativity and other timing methods. His complete directions, solar returns and declination methods are not implemented here. This timeline cannot establish particular future events, event probabilities or why a past event occurred. Astronomical dates are calculable; the personal interpretations are not scientifically validated predictions.'}
