"""Chart-matched paraphrases verified against the uploaded White/Raphael scans.

No raw book text or model-generated citations are stored. PDF page numbers are
one-based scan pages, which can differ from the printed pagination.
"""
import swisseph as swe
from .ephemeris import PLANET_IDS, sign_of, whole_sign_house_of

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
              'raphael_guide': ('The Guide to Astrology', 'Raphael')}
    title, author = titles[source]
    return {'source_id': source, 'title': title, 'author': author,
            'pdf_page': pdf_page, 'printed_page': printed_page, 'chapter': chapter,
            'system': 'WESTERN_TROPICAL', 'kind': 'verified_paraphrase'}


def build_book_natal_report(chart, latitude=None, longitude=None):
    jd = chart['julian_day']
    # Explicit tropical calculations; never reinterpret sidereal sign names as
    # the seasonal signs used in these scans. Houses remain absent on purpose.
    planets = {}
    for name, pid in PLANET_IDS.items():
        if name == 'Rahu':
            continue
        values, _ = swe.calc_ut(jd, pid, swe.FLG_MOSEPH | swe.FLG_SPEED)
        sign, degree = sign_of(values[0])
        planets[name] = {'longitude': values[0], 'sign': sign, 'sign_deg': degree}
    tropical_chart = None
    if latitude is not None and longitude is not None:
        _, axes = swe.houses_ex(jd, latitude, longitude, b'W', swe.FLG_MOSEPH)
        asc_sign, asc_degree = sign_of(axes[0])
        for placement in planets.values():
            placement['house'] = whole_sign_house_of(placement['sign'], asc_sign)
        tropical_chart = {'julian_day': jd, 'zodiac': 'Tropical', 'house_system': 'Whole sign',
                          'ascendant': {'longitude': axes[0], 'sign': asc_sign, 'sign_deg': asc_degree},
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
    return {'version': 1, 'basis': 'Western tropical, geocentric planetary positions',
            'basis_note': 'The main wheel uses the tropical zodiac with whole-sign houses as a platform display choice. Lahiri is available as a separate specialist view. House-specific book interpretations have not been applied. Aspect selection uses a platform limit of 5°, not Raphael’s complete orb tables.',
            'planets': planets, 'chart': tropical_chart, 'sections': sections,
            'coverage': 'Verified Sun passages for all twelve signs, natal reading method and major-aspect classifications from White and Raphael. Detailed Moon, Ascendant, house and planet-pair delineations are not yet curated.',
            'other_books': 'Karma, Merton, Daath and Raleigh remain in the knowledge catalog but are not cited in this report. Heliocentric, medical and Hermetic material require separate interpretation methods.'}
