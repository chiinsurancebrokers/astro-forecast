"""Chart-matched paraphrases verified against the uploaded White/Raphael scans.

No raw book text or model-generated citations are stored. PDF page numbers are
one-based scan pages, which can differ from the printed pagination.
"""
import swisseph as swe
from datetime import datetime, timedelta
from .life_periods import build_life_period_report
from .ephemeris import PLANET_IDS, sign_of, whole_sign_house_of
from .historical_specialists import run_historical_specialists
from .western_delineation import build_western_delineation

SUN_READINGS = {
    'Aries': 'White associates this placement with independence, determination and a preference for leading. He also describes quick reactions tempered by a readiness to forgive.',
    'Taurus': 'White emphasizes patience, caution and persistence, alongside an appreciation of music, art and tangible comforts. The balancing theme is flexibility when a settled opinion is challenged.',
    'Gemini': 'White describes curiosity, investigation, an active mind and an interest in writing or scientific study. His counterpoint is continuity: sustaining an interest after the first excitement.',
    'Cancer': 'White emphasizes sensitivity, attachment to home and family, patient effort and responsiveness to surroundings. Encouragement and a harmonious environment are recurring themes.',
    'Leo': 'White describes generosity, independence, determination and a tendency to lead among associates. He stresses persistence and the importance of other planetary configurations when discussing vocation.',
    'Virgo': 'White links this placement with thoughtfulness, industriousness, quick learning and discrimination. His contrasting themes are criticism, dissatisfaction and confidence in one’s abilities.',
    'Libra': 'White emphasizes weighing alternatives, affection, imagination and an appreciation of music and art. He describes a preference for harmony and the tension between reason and intuition.',
    'Scorpio': 'White describes patience, determination, economy and strong resistance to being imposed upon. His account combines sympathy with the challenge of releasing a remembered injury.',
    'Sagittarius': 'White emphasizes generosity, ambition, perseverance and independence. He connects this placement with foresight, varied interests and a preference for directing one’s own efforts.',
    'Capricorn': 'White describes practical reasoning, sustained ambition and the ability to investigate a subject deeply. His account contrasts inward sympathy with an outward manner that may seem reserved.',
    'Aquarius': 'White emphasizes practical reasoning, generosity, sincerity and independence. He describes strong convictions and a preference for kindness over being directed by others.',
    'Pisces': 'White combines imagination and idealism with sustained study and a capacity for systematic reasoning. His counterpoint is modesty or hesitation about putting one’s abilities forward.',
}
SIGNS = list(SUN_READINGS)


def citation(source, pdf_page, printed_page, chapter):
    titles = {'white_guide': ('A Guide To Astrology', 'Fredrick White'),
              'karma_ancient_egyptians': ('Astrology of the Ancient Egyptians', 'Karma'),
              'raphael_guide': ('The Guide to Astrology', 'Raphael')}
    title, author = titles[source]
    return {'source_id': source, 'title': title, 'author': author,
            'pdf_page': pdf_page, 'printed_page': printed_page, 'chapter': chapter,
            'system': 'WESTERN_TROPICAL', 'kind': 'verified_paraphrase'}


def build_book_natal_report(chart, latitude=None, longitude=None):
    jd = chart['julian_day']
    # Explicit tropical calculations; never reinterpret sidereal sign names as
    # the seasonal signs used in these scans. Houses require an explicit birth location; absent locations never receive invented cusps.
    planets = {}
    for name, pid in {**PLANET_IDS, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE}.items():
        if name == 'Rahu':
            continue
        values, _ = swe.calc_ut(jd, pid, swe.FLG_MOSEPH | swe.FLG_SPEED)
        sign, degree = sign_of(values[0])
        planets[name] = {'longitude': values[0], 'sign': sign, 'sign_deg': degree, 'retrograde': values[3] < 0}
    tropical_chart = None
    if latitude is not None and longitude is not None:
        cusps, axes = swe.houses_ex(jd, latitude, longitude, b'W', swe.FLG_MOSEPH)
        asc_sign, asc_degree = sign_of(axes[0])
        for placement in planets.values():
            placement['house'] = whole_sign_house_of(placement['sign'], asc_sign)
        tropical_chart = {'julian_day': jd, 'zodiac': 'Tropical', 'house_system': 'Whole sign',
                          'ascendant': {'longitude': axes[0], 'sign': asc_sign, 'sign_deg': asc_degree},
                          'midheaven': {'longitude': axes[1], 'sign': sign_of(axes[1])[0], 'sign_deg': sign_of(axes[1])[1]},
                          'house_cusps': list(cusps),
                          'planets': planets}
    sun = planets['Sun']
    index = SIGNS.index(sun['sign'])
    sections = [{
        'title': 'Identity and motivation',
        'fact': f"Tropical Sun in {sun['sign']} at {sun['sign_deg']:.1f}°.",
        'interpretation': SUN_READINGS[sun['sign']],
        'reflection': 'Where do these themes fit your experience, and where do they not?',
        'citations': [citation('white_guide', index + 8, index + 2, sun['sign'])],
    }]
    for title, name, interpretation, reflection in [
        ('Mind and communication', 'Mercury', 'White assigns Mercury to the mind and asks the reader to modify that testimony by its aspects. The placement below is calculated evidence; this section does not claim a verified sign-specific Mercury character reading.', 'Which habits help you think clearly and communicate well?'),
        ('Relationships', 'Venus', 'White treats Venus as a significator of marriage and reads it together with planetary aspects. His historical event claims are not reproduced as predictions here.', 'What qualities do you value in a partnership, and how do you express them?'),
        ('Resources and influence', 'Jupiter', 'White connects Jupiter with money and power, then considers its condition and aspects. This is a historical symbolic association, not an assessment of your financial future.', 'How do you use resources and influence in ways that fit your values?'),
        ('Ambition and action', 'Mars', 'White groups the Sun and Mars with ambition, popularity, friends and enemies, with the interpretation modified by aspects. The chart fact below identifies Mars without claiming a complete career delineation.', 'How do you turn ambition into action while managing conflict?'),
    ]:
        placement = planets[name]
        sections.append({'title': title, 'fact': f"Tropical {name} in {placement['sign']} at {placement['sign_deg']:.1f}°.",
                         'interpretation': interpretation, 'reflection': 'Reflection prompt: ' + reflection,
                         'citations': [citation('white_guide', 46, 40, 'The Radix')]})
    # Book methodology is explicitly separated from a personality delineation.
    sections.append({
        'title': 'How to read the whole chart',
        'fact': 'The Sun is one part of the chart, alongside the Ascendant, planetary condition and aspects.',
        'interpretation': 'Raphael instructs the reader to establish the Ascendant and its ruler, then consider planetary aspects, houses and dignities. White similarly brings planetary condition, houses and aspects together in his radix method. A single sign description is therefore only a starting point.',
        'reflection': 'Read the following aspect evidence alongside the Sun passage rather than treating it as a complete character assessment.',
        'citations': [citation('raphael_guide', 76, 72, 'Part Three, Chapter I: How to Judge a Nativity'), citation('white_guide', 46, 40, 'The Radix')],
    })
    aspects = []
    names = list(planets)
    for i, a in enumerate(names):
        for b in names[i+1:]:
            distance = abs(planets[a]['longitude'] - planets[b]['longitude'])
            distance = min(distance, 360-distance)
            for label, angle in [('conjunction',0), ('sextile',60), ('square',90), ('trine',120), ('opposition',180)]:
                orb = abs(distance-angle)
                if orb <= 5:
                    aspects.append({'a': a, 'b': b, 'aspect': label, 'orb': round(orb,2)})
                    break
    for aspect in sorted(aspects, key=lambda x:x['orb'])[:6]:
        label = aspect['aspect']
        meaning = {'trine': 'Raphael classifies the trine as favorable in his traditional scheme.',
                   'sextile': 'Raphael classifies the sextile as favorable in his traditional scheme.',
                   'square': 'Raphael classifies the square as adverse in his traditional scheme.',
                   'opposition': 'Raphael classifies the opposition as adverse in his traditional scheme.',
                   'conjunction': 'Raphael distinguishes conjunctions by the planets involved; a conjunction is not automatically favorable or adverse.'}[label]
        sections.append({'title': f"{aspect['a']}–{aspect['b']} {label}",
                         'fact': f"Calculated angular orb: {aspect['orb']:.2f}°.",
                         'interpretation': meaning + ' This is the author’s historical classification, not a forecast of an event.',
                         'reflection': 'This report does not yet apply the author’s detailed planet-pair delineation.',
                         'citations': [citation('raphael_guide', 10, 6, 'Of the Nature of the Aspects')]})
    reading = synthesize_natal_reading(planets, aspects, index, tropical_chart)
    birth_dt = datetime(2000,1,1,12)+timedelta(days=jd-2451545.0)
    life_report = build_life_period_report(chart,tropical_chart,birth_dt,datetime.utcnow(),citation) if tropical_chart else None
    if life_report:
        for ref in life_report['references']:
            if ref not in reading['references']:
                reading['references'].append(ref)
    return {'version': 4, 'basis': 'Western tropical, geocentric planetary positions',
            'basis_note': 'The main wheel uses the tropical zodiac with whole-sign houses as a platform display choice. Lahiri is available as a separate specialist view. House topics, selected planet-in-house passages and rulership are now interpreted. Whole-sign cusps and editorial ruler links are platform choices, not a reproduction of either book’s complete historical cusp method. The astronomical Midheaven is recorded separately from the whole-sign tenth house. Aspect selection uses a platform limit of 5°, not Raphael’s complete orb tables.',
            'planets': planets, 'chart': tropical_chart, 'sections': sections,
            'reading': reading, 'life_report':life_report,
            'specialists': run_historical_specialists(chart),
            'coverage': 'This reading currently uses checked passages from White, Raphael and, when applicable, Karma. It covers the Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus and Neptune, selected planetary combinations, all twelve house topics and their rulers when a birth location is available. Selected planet-in-house passages have been verified; an exhaustive delineation of every combination is not claimed. Pluto is not covered by these books.',
            'other_books': 'Merton, Daath and Raleigh now have separate specialist sections below the main reading. Each explains its method, calculated evidence or reflection exercise, and current coverage. Further passages from all six books are still being checked.'}


def synthesize_natal_reading(planets, aspects, sun_index, chart=None):
    """Editorial synthesis of verified passages, with explicit internal provenance.

    Match exact planet pairs before applying a delineation. Practical guidance is
    editorial and never attributed verbatim to the historical authors.
    """
    sun_sign = planets['Sun']['sign']
    text = SUN_READINGS[sun_sign]
    replacements = {
        'White associates this placement with': 'Your central pattern brings together',
        'White emphasizes': 'Your central pattern emphasizes',
        'White describes': 'Your central pattern combines',
        'White links this placement with': 'Your central pattern brings together',
        'White combines': 'Your central pattern combines',
        'He also describes': 'There is also a theme of',
        'He stresses': 'This places emphasis on',
        'He describes': 'Alongside this is a theme of',
        'He connects this placement with': 'This is accompanied by',
        'His counterpoint is': 'The corresponding challenge is',
        'His account combines': 'This combines',
        'His account contrasts': 'This contrasts',
        'His contrasting themes are': 'The balancing themes are',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    sections = [{'title': 'The central pattern of your life', 'paragraphs': [
        f"With your Sun in {sun_sign}, the natal reading begins with the way you develop a sense of direction and express your individuality. " + text,
        'These qualities become meaningful through the choices you make. The rest of this reading considers the combinations that reinforce or complicate this central pattern, rather than treating your Sun sign as a complete description of you.'
    ], 'citations': [citation('white_guide', sun_index+8, sun_index+2, sun_sign)]}]
    if chart and chart['ascendant']['sign'] in {'Taurus','Leo','Scorpio','Aquarius'} and chart['ascendant']['sign_deg'] >= 7:
        sections.append({'title':'How you approach life','paragraphs':[
            'Your rising sign adds a steadier quality to the way you approach situations. In Karma’s account, this group of rising signs is associated with patience, caution, constancy and determination. Alongside the Sun’s motivation, it describes the value of holding a course long enough to see what it can become.',
            'The constructive balance is persistence with room to adapt. Commitment can help you build something lasting, while periodically reviewing your approach keeps determination from becoming resistance to change.'
        ], 'citations':[citation('karma_ancient_egyptians',37,25,'The Rising Sign'),citation('karma_ancient_egyptians',38,26,'The Rising Sign, continued')]})
    matches = {(frozenset([a['a'], a['b']]), a['aspect']): a for a in aspects}
    # These are conservative paraphrases of the specific passages checked in the
    # uploaded Raphael scan; no house claim is imported from a different system.
    rules = [
        ('Sun', 'Mercury', {'conjunction'}, 'How you think and find your direction', 64, 60,
         'Your identity and your thinking are closely connected. This combination brings the themes of learning, comprehension and ambition into the same part of the reading. You may find your direction through understanding a subject thoroughly, communicating it or putting knowledge to practical use.',
         'A useful way to work with this pattern is to give your ideas both expression and space for reconsideration. Intellectual confidence is most productive when it remains open to another perspective.'),
        ('Venus', 'Saturn', {'trine','sextile'}, 'What gives relationships substance', 54, 50,
         'The relationship pattern contains a theme of steadiness: attachment is supported by care, perseverance and attention to feelings. This adds substance to affection and suggests that consistency may matter as much as the first excitement of a connection.',
         'In practice, the constructive expression of this pattern is reliability that remains warm. Making time, keeping commitments and showing care in ordinary circumstances can give a relationship room to deepen.'),
        ('Venus', 'Mars', {'trine','sextile'}, 'Affection, attraction and social life', 61, 57,
         'There is also a more sociable and expressive thread in the relationship pattern. Affection and the desire to engage with others can work together, bringing an appreciation of company, attraction and shared enjoyment.',
         'Read together with the other relationship factors, this describes a capacity for connection rather than a promise about a particular partner. It is worth giving both companionship and personal desire an honest place in your relationships.'),
        ('Moon', 'Jupiter', {'conjunction','trine','sextile'}, 'Support, confidence and emotional security', 58, 54,
         'The Moon and Jupiter add a supportive thread to the reading. In the bibliography this combination is associated with favorable conditions for partnership, prosperity and prudent conduct. Read as a natal theme, it points toward the value of supportive relationships and thoughtful judgment when building a secure life.',
         'The practical emphasis is to recognize and cultivate sources of support. Encouragement is most useful when it is accompanied by decisions you have considered carefully.'),
    ]
    for a,b,kinds,title,page,printed,interpretation,guidance in rules:
        found = next((matches[(frozenset([a,b]),kind)] for kind in sorted(kinds) if (frozenset([a,b]),kind) in matches), None)
        if found:
            sections.append({'title': title, 'paragraphs': [interpretation, guidance],
                             'evidence': found,
                             'citations': [citation('raphael_guide',page,printed, 'Conjunctions and Aspects of ' + {64:'Sun',54:'Saturn',61:'Mars',58:'Jupiter'}[page])]})
    sections.append({'title':'Bringing the reading together','paragraphs':[
        'The overall picture should be read as a pattern of capacities and tensions, not a fixed script. Start with the central motivation described above, then consider how the intellectual, relational and supportive combinations fit your lived experience. Where two themes differ, the task is to find a way for both to be expressed rather than allowing one to dominate.',
        'This is a natal reading of enduring themes. A forecast for a specific period requires a separate timing analysis tied to dates; the birth chart alone does not establish when a development will occur.'
    ],'citations':[citation('raphael_guide',76,72,'How to Judge a Nativity'),citation('white_guide',46,40,'The Radix')]})
    delineation = None
    if all('sign_deg' in p for p in planets.values()):
        delineation = build_western_delineation(planets, chart, aspects, citation, SUN_READINGS)
        if delineation['overview']:
            sections.insert(1,delineation['overview'])
    references = []
    reference_sections = sections + (delineation['planet_sections'] + delineation['house_sections'] if delineation else [])
    for section in reference_sections:
        for c in section['citations']:
            if c not in references:
                references.append(c)
    return {'sections': sections, 'references': references,
            'planet_sections': delineation['planet_sections'] if delineation else [],
            'house_sections': delineation['house_sections'] if delineation else [],
            'delineation_note': delineation['method_note'] if delineation else '',
            'method': 'Source-based editorial synthesis. Matched sign traits, house topics, selected planet-in-house descriptions and aspect combinations paraphrase historical material. Their synthesis, practical guidance and ruler-to-house connections are editorial applications. Historical claims of guaranteed events, illness or moral character are excluded. A missing or unsuitable source passage is disclosed instead of replaced by an invented interpretation. This is not a complete reproduction of either author’s methods.'}
