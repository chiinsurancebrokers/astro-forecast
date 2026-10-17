"""Deterministic reader edition and structural audit of the curated natal report.

This checks calculation/provenance links, not the scientific validity of
astrology or the semantic correctness of every historical paraphrase. No LLM
or untrusted plugin prose is allowed to extend the reader's interpretation.
"""
from copy import deepcopy
import math
import re
import swisseph as swe
from .book_corpus import SOURCES
from .ephemeris import SIGNS, sign_of, whole_sign_house_of
from .western_delineation import RULERS

AUTHOR_REPLACEMENTS = {
    'White’s usable descriptive themes here are ': 'The descriptive themes of this placement are ',
    'In Raphael’s scheme, ': 'In this traditional framework, ',
    'in Raphael’s convention': 'in the selected rulership convention',
    'In Karma’s account, ': 'In this interpretive framework, ',
    'Pontin’s description connects this placement with ': 'This placement is read in connection with ',
    'Belle Bart presents self-knowledge and personal agency as central to her approach: ': 'Self-knowledge and personal agency are central to this approach: ',
    'In the bibliography this combination is associated with ': 'This combination is traditionally associated with ',
    'Raphael describes ': 'This placement is traditionally associated with ',
    'Raphael associates this placement with ': 'This placement is traditionally associated with ',
    'Raphael emphasizes ': 'This placement emphasizes ',
    'Raphael gives prominence to ': 'This placement gives prominence to ',
    'White associates this placement with ': 'This placement is associated with ',
    'White emphasizes ': 'This placement emphasizes ',
    'White describes ': 'This placement describes ',
    'White links this placement with ': 'This placement is associated with ',
    'White combines ': 'This placement combines ',
}
AUTHOR_PATTERN = re.compile(r'\b(?:White|Raphael|Pontin|Karma|Belle Bart|Alan Leo)\b')


def reader_text(text):
    for before,after in AUTHOR_REPLACEMENTS.items():
        text=text.replace(before,after)
    return text


def _valid_reference(ref):
    source=SOURCES.get(ref.get('source_id'))
    return bool(source and source['system']=='WESTERN_TRADITIONAL'
                and ref.get('author')==source.get('author')
                and ref.get('title')==source.get('title')
                and type(ref.get('pdf_page')) is int and ref['pdf_page']>0
                and type(ref.get('printed_page')) is int and ref['printed_page']>0
                and ref.get('chapter') and ref.get('kind')=='verified_paraphrase')


def _chart_check(chart):
    if not chart or chart.get('zodiac')!='Tropical' or chart.get('house_system')!='Whole sign':
        raise ValueError('A calculated tropical whole-sign chart is required.')
    asc=chart['ascendant']
    coordinates=chart.get('coordinates') or {}
    if not all(type(coordinates.get(k)) in (int,float) and math.isfinite(coordinates[k])
               for k in ('latitude','longitude')):
        raise ValueError('Calculated houses require explicit finite birth coordinates.')
    if not (-89<=coordinates['latitude']<=89 and -180<=coordinates['longitude']<=180):
        raise ValueError('Invalid birth coordinates.')
    if type(chart.get('julian_day')) not in (int,float) or not math.isfinite(chart['julian_day']):
        raise ValueError('A finite birth Julian day is required.')
    from .methods import tropical_positions
    computed=tropical_positions(chart['julian_day'])
    _,axes=swe.houses_ex(chart['julian_day'],coordinates['latitude'],coordinates['longitude'],b'W',0)
    if abs((axes[0]-asc['longitude']+180)%360-180)>1e-6:
        raise ValueError('Ascendant does not match the birth instant and coordinates.')
    if sign_of(asc['longitude'])[0]!=asc['sign']:
        raise ValueError('Ascendant sign does not match longitude.')
    for name,p in chart['planets'].items():
        if name not in computed or abs((computed[name]['longitude']-p['longitude']+180)%360-180)>1e-6:
            raise ValueError('Planetary longitude does not match the ephemeris: '+name)
        if not math.isfinite(p['longitude']) or not 0<=p['longitude']<360:
            raise ValueError('Invalid planetary longitude.')
        sign,degree=sign_of(p['longitude'])
        if p['sign']!=sign or abs(degree-p['sign_deg'])>1e-6:
            raise ValueError('Planet sign/degree does not match longitude: '+name)
        if p['house']!=whole_sign_house_of(sign,asc['sign']):
            raise ValueError('Planet house does not match whole-sign geometry: '+name)


def _aspect_matches(fact,planets):
    angles={'conjunction':0,'sextile':60,'square':90,'trine':120,'opposition':180}
    try:
        a,b=planets[fact['a']],planets[fact['b']]
        delta=abs((a['longitude']-b['longitude']+180)%360-180)
        orb=abs(delta-angles[fact['aspect']])
        return orb<=5.00001 and abs(round(orb,2)-fact['orb'])<=.011
    except (KeyError,TypeError):
        return False


def build_reader_edition(report,plugin_records=None):
    """Use only source-matched sections; retain per-section provenance internally.

    plugin_records are an optional verification input for internal tooling, not
    a public upload route. Missing/ambiguous metadata is rejected, not guessed.
    """
    chart=report.get('chart')
    _chart_check(chart)
    planets=chart['planets'];reading=report['reading']
    # Rebuild approved source templates from the calculated geometry. A matching
    # citation or a correct sign cannot authorize arbitrary model-written prose.
    from .natal_books import synthesize_natal_reading
    aspects=[]
    names=list(planets)
    for index,a in enumerate(names):
        for b in names[index+1:]:
            delta=abs((planets[a]['longitude']-planets[b]['longitude']+180)%360-180)
            for label,angle in (('conjunction',0),('sextile',60),('square',90),('trine',120),('opposition',180)):
                orb=abs(delta-angle)
                if orb<=5:
                    aspects.append({'a':a,'b':b,'aspect':label,'orb':round(orb,2)})
                    break
    canonical=synthesize_natal_reading(planets,aspects,SIGNS.index(planets['Sun']['sign']),chart)
    canonical_by_group={group:{s['title']:s for s in canonical.get(group,[])}
                        for group in ('sections','planet_sections','house_sections')}
    output={'sections':[],'planet_sections':[],'house_sections':[],
            'references':[],'audit':[],'excluded':[]}
    references={}
    for group in ('sections','planet_sections','house_sections'):
        for index,original in enumerate(reading.get(group,[])):
            item=deepcopy(original);facts=[];kind='source_based_editorial_application'
            reason=None
            refs=item.get('citations',[])
            approved=canonical_by_group[group].get(item.get('title'))
            if not approved or any(item.get(k)!=approved.get(k) for k in ('paragraphs','citations','evidence')):
                reason='Text or evidence does not match the approved source-derived template.'
            elif not refs or not all(_valid_reference(ref) for ref in refs):
                reason='Source metadata is absent, incompatible or outside the curated registry.'
            elif group=='planet_sections':
                name=item.get('planet');expected=planets.get(name);actual=item.get('evidence',{})
                if not expected or any(actual.get(k)!=expected.get(k) for k in ('longitude','sign','sign_deg','house','retrograde')):
                    reason='Planetary evidence does not match the calculated chart.'
                else:
                    facts=[{'type':'planet_placement','planet':name,**expected}]
            elif group=='house_sections':
                h=item['house'];sign=SIGNS[(SIGNS.index(chart['ascendant']['sign'])+h-1)%12]
                ruler=RULERS[sign];occupants=[n for n,p in planets.items() if p['house']==h]
                if (item.get('sign')!=sign or item.get('ruler')!=ruler or item.get('occupants')!=occupants
                        or item.get('ruler_house')!=planets[ruler]['house']):
                    reason='House, occupants or ruler do not match the calculated chart.'
                else:
                    facts=[{'type':'house','house':h,'sign':sign,'ruler':ruler,
                            'occupants':occupants,'ruler_placement':planets[ruler]}]
            elif 'evidence' in item:
                if not _aspect_matches(item['evidence'],planets):
                    reason='Aspect is absent or its orb does not match the calculated chart.'
                else:
                    facts=[{'type':'aspect',**item['evidence']}]
            else:
                title=item['title']
                if title=='The central pattern of your life':
                    facts=[{'type':'planet_placement','planet':'Sun',**planets['Sun']}]
                elif title=='How the planets and houses come together':
                    ruler=RULERS[chart['ascendant']['sign']]
                    facts=[{'type':'ascendant',**chart['ascendant']},
                           {'type':'chart_ruler','planet':ruler,**planets[ruler]}]
                elif title=='How you approach life':
                    asc=chart['ascendant']
                    if asc['sign'] not in {'Taurus','Leo','Scorpio','Aquarius'} or asc['sign_deg']<7:
                        reason='The rising-sign rule predicate is not satisfied.'
                    facts=[{'type':'ascendant',**asc}]
                elif title=='How to develop your thinking and communication':
                    from .additional_books import MERCURY
                    if planets['Mercury']['sign'] not in MERCURY:
                        reason='The Mercury source rule does not cover this sign.'
                    facts=[{'type':'planet_placement','planet':'Mercury',**planets['Mercury']}]
                elif title in {'Bringing the reading together','Turning self-knowledge into preparation'}:
                    kind='editorial_reflection_not_a_chart_claim'
                else:
                    reason='No approved matching rule exists for this narrative section.'
            item['paragraphs']=[reader_text(p) for p in item.get('paragraphs',[])]
            if any(AUTHOR_PATTERN.search(p) for p in item['paragraphs']):
                reason='A source attribution remains in the reader narrative.'
            identifier=f'{group}:{index}'
            if reason:
                output['excluded'].append({'section_id':identifier,'title':item.get('title'),'reason':reason})
                continue
            # Citations are kept in audit, not in the reading paragraphs.
            item.pop('citations',None);item['section_id']=identifier
            output[group].append(item)
            output['audit'].append({'section_id':identifier,'kind':kind,'facts':facts,'sources':refs,
                                    'checks':['source_registry','rule_predicate','calculated_geometry']})
            for ref in refs:
                references[(ref['source_id'],ref['pdf_page'],ref['chapter'])]=ref
    output['references']=list(references.values())
    output['calculation']={'zodiac':'tropical','house_system':'whole_sign',
                           'ephemeris':'Moshier','julian_day':chart['julian_day'],
                           'rulership':'Declared source-specific rulership convention'}
    output['coverage']={
        'calculated_planets':len(planets),'interpreted_planets':len(output['planet_sections']),
        'interpreted_houses':len(output['house_sections']),
        'gaps':['Pluto is not interpreted because the curated natal sources do not cover it.',
                'Only selected sourced aspect combinations receive interpretations.',
                'Historical life events are not inferred from the birth chart.',
                'Dated transit analysis is separate from this natal report.'],
        'validation':'Structural source links and calculation predicates are checked; this is not independent verification of the scans or proof of astrology.'}
    output['plugins']=check_plugin_records(plugin_records or [],chart)
    output['method']='Calculated placements matched to curated, source-linked interpretation templates. No generative AI writes this reader edition. Reflection and practical applications are editorial; sources are listed only at the end.'
    return output


def check_plugin_records(records,chart):
    """Numerical cross-check only. Plugin prose never becomes report text."""
    results=[]
    for record in records:
        reason=None
        if not isinstance(record,dict):
            results.append({'provider':'unknown','status':'excluded','reason':'Malformed record.'});continue
        if (record.get('zodiac')!='tropical' or record.get('house_system')!='whole_sign'
                or record.get('time_basis')!='UTC' or not record.get('provider')):
            reason='Explicit zodiac, house system, provider and UTC time basis are required.'
        elif (type(record.get('julian_day')) not in (int,float)
              or not math.isfinite(record['julian_day'])
              or abs(record['julian_day']-chart['julian_day'])>1/86400):
            reason='Birth instant differs or is absent.'
        elif record.get('coordinates')!=chart.get('coordinates') or not chart.get('coordinates'):
            reason='Birth coordinates differ or are absent.'
        else:
            supplied=record.get('planets')
            if not isinstance(supplied,dict) or not supplied:
                reason='Numerical planetary longitudes are required; sign-only profiles are insufficient.'
            else:
                for name,value in supplied.items():
                    if name not in chart['planets'] or not isinstance(value,(int,float)) or not math.isfinite(value):
                        reason='Unknown planet or invalid longitude.';break
                    delta=abs((value-chart['planets'][name]['longitude']+180)%360-180)
                    if delta>.02:
                        reason='Planetary longitude disagrees with the local calculation.';break
        results.append({'provider':record.get('provider','unknown'),
                        'status':'excluded' if reason else 'numerical_crosscheck_only',
                        'reason':reason or 'Compatible positions agree. No plugin narrative is incorporated.'})
    return {'status':'not_connected' if not records else 'reviewed','records':results,
            'note':'ChatGPT plugins are not callable server APIs. No live provider connection is claimed. Sign-only or unverifiable plugin output cannot support personal natal interpretation.'}
