"""Daily horoscope built from the real sky for a date -- no stored data, no AI.

The text is assembled from calculated Western (tropical) positions: the Moon's
sign and phase, its closest aspects, Mercury's motion and the solar-house
placement of each of those for the chosen Sun sign. Wording is reflective, not
predictive. Positions are calculated for 12:00 UT on the requested date; the
Moon changes sign about every 2.5 days, so it may move on during the day.
"""
import random
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import swisseph as swe

from .methods import tropical_positions
from .tarot import draw_reading

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
SIGN_GLYPHS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
SIGN_EL = ['Κριός', 'Ταύρος', 'Δίδυμοι', 'Καρκίνος', 'Λέων', 'Παρθένος',
           'Ζυγός', 'Σκορπιός', 'Τοξότης', 'Αιγόκερως', 'Υδροχόος', 'Ιχθύες']
# "in <sign>" with the correct Greek article
SIGN_IN_EL = ['στον Κριό', 'στον Ταύρο', 'στους Διδύμους', 'στον Καρκίνο',
              'στο Λέοντα', 'στην Παρθένο', 'στον Ζυγό', 'στον Σκορπιό',
              'στον Τοξότη', 'στον Αιγόκερω', 'στον Υδροχόο', 'στους Ιχθύες']

MIN_DATE, MAX_DATE = date(1900, 1, 1), date(2100, 12, 31)
DEFAULT_TZ = ZoneInfo('Europe/Athens')

HOUSES = [  # (EN theme, EL theme, EN reflection, EL reflection)
    ('self, body and how you present yourself', 'εαυτός, σώμα και τρόπος που παρουσιάζεσαι',
     'What would feel like an honest way to show up today?', 'Ποιος θα ήταν ένας ειλικρινής τρόπος να εμφανιστείς σήμερα;'),
    ('money, resources and what you value', 'χρήματα, πόροι και όσα εκτιμάς',
     'What do you already have that deserves appreciation?', 'Τι ήδη διαθέτεις που αξίζει να εκτιμηθεί;'),
    ('communication, learning and your immediate surroundings', 'επικοινωνία, μάθηση και άμεσο περιβάλλον',
     'Is there a conversation or a question you have been putting off?', 'Υπάρχει μια συζήτηση ή ένα ερώτημα που αναβάλλεις;'),
    ('home, family and roots', 'σπίτι, οικογένεια και ρίζες',
     'What would make your space feel a little more settled?', 'Τι θα έκανε τον χώρο σου λίγο πιο ήρεμο;'),
    ('creativity, enjoyment and play', 'δημιουργικότητα, απόλαυση και παιχνίδι',
     'What small thing would you do just because you enjoy it?', 'Τι μικρό πράγμα θα έκανες απλώς επειδή το χαίρεσαι;'),
    ('daily routines, work and wellbeing habits', 'καθημερινές ρουτίνες, εργασία και συνήθειες φροντίδας',
     'Which routine is worth adjusting, and which is working well?', 'Ποια ρουτίνα αξίζει προσαρμογή και ποια λειτουργεί καλά;'),
    ('partnerships and close one-to-one relationships', 'συντροφικότητες και στενές σχέσεις',
     'What would you like to understand better about someone close to you?', 'Τι θα ήθελες να κατανοήσεις καλύτερα για κάποιον κοντινό σου;'),
    ('shared resources, trust and deeper change', 'κοινοί πόροι, εμπιστοσύνη και βαθύτερες αλλαγές',
     'What are you ready to let go of, or to be more open about?', 'Τι είσαι έτοιμος/η να αφήσεις ή να μοιραστείς πιο ανοιχτά;'),
    ('learning, travel and the beliefs you live by', 'μάθηση, ταξίδια και πεποιθήσεις',
     'What would widen your perspective a little today?', 'Τι θα διεύρυνε λίγο την οπτική σου σήμερα;'),
    ('career, public role and long-term goals', 'επαγγελματικός ρόλος, δημόσια εικόνα και μακροπρόθεσμοι στόχοι',
     'Which one step would move a long-term goal forward?', 'Ποιο ένα βήμα θα προχωρούσε έναν μακροπρόθεσμο στόχο;'),
    ('friends, groups and hopes for the future', 'φίλοι, ομάδες και ελπίδες για το μέλλον',
     'Who could you reach out to, or who might need to hear from you?', 'Σε ποιον θα μπορούσες να απευθυνθείς ή ποιος ίσως χρειάζεται να σε ακούσει;'),
    ('rest, reflection and what happens behind the scenes', 'ανάπαυση, στοχασμός και ό,τι συμβαίνει στο παρασκήνιο',
     'What do you need to rest from, or to quietly think through?', 'Από τι χρειάζεσαι ξεκούραση ή τι χρειάζεται να σκεφτείς με ησυχία;'),
]

PHASES = [  # EN, EL, index = nearest 45-degree step of the Sun-Moon elongation
    ('New Moon', 'Νέα Σελήνη'), ('Waxing crescent', 'Αύξων μηνίσκος'),
    ('First quarter', 'Πρώτο τέταρτο'), ('Waxing gibbous', 'Αύξουσα κυρτή'),
    ('Full Moon', 'Πανσέληνος'), ('Waning gibbous', 'Φθίνουσα κυρτή'),
    ('Last quarter', 'Τελευταίο τέταρτο'), ('Waning crescent', 'Φθίνων μηνίσκος'),
]

# (name EN, name EL, angle, EN phrase, EL phrase); the Moon is the mood of the day
ASPECTS = [
    ('conjunction', 'σύνοδο', 0, 'blends mood with', 'ενώνει το συναίσθημα με'),
    ('sextile', 'εξάγωνο', 60, 'offers an opening between mood and', 'δίνει μια ευκαιρία ανάμεσα στο συναίσθημα και'),
    ('square', 'τετράγωνο', 90, 'adds some friction between mood and', 'φέρνει λίγη τριβή ανάμεσα στο συναίσθημα και'),
    ('trine', 'τρίγωνο', 120, 'eases the flow between mood and', 'κάνει πιο ομαλή τη ροή ανάμεσα στο συναίσθημα και'),
    ('opposition', 'αντίθεση', 180, 'highlights a pull between mood and', 'τονίζει μια ένταση ανάμεσα στο συναίσθημα και'),
]
ASPECT_ORB = 5.0
ASPECT_BODIES = {  # EN name, EN theme, EL "with <planet>", EL theme (accusative)
    'Sun': ('the Sun', 'vitality and self-expression', 'τον Ήλιο', 'τη ζωντάνια και την αυτοέκφραση'),
    'Mercury': ('Mercury', 'thinking and communication', 'τον Ερμή', 'τη σκέψη και την επικοινωνία'),
    'Venus': ('Venus', 'relationships and values', 'την Αφροδίτη', 'τις σχέσεις και τις αξίες'),
    'Mars': ('Mars', 'energy and initiative', 'τον Άρη', 'την ενέργεια και την πρωτοβουλία'),
    'Jupiter': ('Jupiter', 'growth and perspective', 'το Δία', 'την ανάπτυξη και την προοπτική'),
    'Saturn': ('Saturn', 'responsibility and limits', 'τον Κρόνο', 'την υπευθυνότητα και τα όρια'),
}

TITLES = {
    'en': {'sky': 'The sky today', 'focus': 'Your focus today', 'season': 'The season you are in',
           'mood': 'The mood of the day', 'mercury': 'Mercury retrograde', 'prompt': 'A question to carry'},
    'el': {'sky': 'Ο ουρανός σήμερα', 'focus': 'Η εστίασή σου σήμερα', 'season': 'Η εποχή στην οποία βρίσκεσαι',
           'mood': 'Η διάθεση της ημέρας', 'mercury': 'Ανάδρομος Ερμής', 'prompt': 'Ένα ερώτημα για σήμερα'},
}
METHOD = {
    'en': ('Calculated from Western tropical planetary positions for 12:00 UT on the chosen date, using each '
           'Sun sign as the first house (solar houses). Templated wording; nothing is generated by AI or stored. '
           'The Moon changes sign roughly every 2.5 days and may move to the next sign during the day.'),
    'el': ('Υπολογίζεται από τις δυτικές τροπικές θέσεις των πλανητών για τις 12:00 UT της επιλεγμένης ημέρας, '
           'με κάθε ζώδιο Ήλιου ως πρώτο οίκο (ηλιακοί οίκοι). Πρότυπη διατύπωση· τίποτα δεν παράγεται από ΤΝ '
           'ούτε αποθηκεύεται. Η Σελήνη αλλάζει ζώδιο περίπου κάθε 2,5 ημέρες και ίσως περάσει στο επόμενο μέσα στην ημέρα.'),
}
DISCLAIMER = {
    'en': 'For entertainment and self-reflection. This is not a prediction and not medical, legal or financial advice.',
    'el': 'Για ψυχαγωγία και προσωπικό στοχασμό. Δεν αποτελεί πρόβλεψη ούτε ιατρική, νομική ή οικονομική συμβουλή.',
}


def today(tz=DEFAULT_TZ):
    return datetime.now(tz).date()


def parse_date(value):
    """Return a date from 'YYYY-MM-DD' (or today if empty); raise ValueError when invalid."""
    if value in (None, ''):
        return today()
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError('Use the date format YYYY-MM-DD.')
    parsed = datetime.strptime(value, '%Y-%m-%d').date()
    if not MIN_DATE <= parsed <= MAX_DATE:
        raise ValueError('Choose a date between 1900 and 2100.')
    return parsed


def sky_for(on_date):
    """Tropical positions at 12:00 UT plus Moon phase and Moon aspects."""
    jd = swe.julday(on_date.year, on_date.month, on_date.day, 12.0)
    positions = tropical_positions(jd)
    elongation = (positions['Moon']['longitude'] - positions['Sun']['longitude']) % 360
    phase = int(((elongation + 22.5) % 360) // 45)
    found = []
    for body in ASPECT_BODIES:
        separation = (positions['Moon']['longitude'] - positions[body]['longitude']) % 360
        separation = min(separation, 360 - separation)
        for index, row in enumerate(ASPECTS):
            orb = abs(separation - row[2])
            if orb <= ASPECT_ORB:
                found.append(dict(body=body, aspect=index, orb=round(orb, 1)))
    found.sort(key=lambda item: item['orb'])
    return dict(positions=positions, phase=phase, elongation=round(elongation, 1), aspects=found)


def sign_index(name):
    if name not in SIGNS:
        raise ValueError('Choose one of the twelve zodiac signs.')
    return SIGNS.index(name)


def solar_house(planet_sign, sun_sign_index):
    """Whole-sign house (1-12) counted from the chosen Sun sign."""
    return (SIGNS.index(planet_sign) - sun_sign_index) % 12 + 1


def sign_name(index, lang):
    return SIGN_EL[index] if lang == 'el' else SIGNS[index]


def sign_in(index, lang):
    return SIGN_IN_EL[index] if lang == 'el' else 'in ' + SIGNS[index]


def sign_list(lang):
    return [dict(id=name, name=sign_name(i, lang), glyph=SIGN_GLYPHS[i]) for i, name in enumerate(SIGNS)]


def _house_phrase(house, lang):
    theme = HOUSES[house - 1][1 if lang == 'el' else 0]
    return f'{house}ο οίκο σου ({theme})' if lang == 'el' else f'your {_ordinal(house)} house ({theme})'


def _ordinal(n):
    return f'{n}{"th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")}'


def _aspect_sentence(item, lang):
    name_en, theme_en, with_el, theme_el = ASPECT_BODIES[item['body']]
    row = ASPECTS[item['aspect']]
    if lang == 'el':
        return f'Η Σελήνη σε {row[1]} με {with_el}: {row[4]} {theme_el}.'
    return f'The Moon in {row[0]} with {name_en}: {row[3]} {theme_en}.'


def build_daily(sign, on_date, lang='el', sky=None):
    """Return the daily horoscope for one Sun sign on one date."""
    if lang not in TITLES:
        raise ValueError('Language must be el or en.')
    idx = sign_index(sign)
    sky = sky or sky_for(on_date)
    pos, el = sky['positions'], lang == 'el'
    titles = TITLES[lang]

    moon_house = solar_house(pos['Moon']['sign'], idx)
    sun_house = solar_house(pos['Sun']['sign'], idx)
    moon_idx, sun_idx = SIGNS.index(pos['Moon']['sign']), SIGNS.index(pos['Sun']['sign'])
    phase = PHASES[sky['phase']][1 if el else 0]

    if el:
        sky_text = (f'Η Σελήνη βρίσκεται {sign_in(moon_idx, lang)} ({phase}) και ο Ήλιος {sign_in(sun_idx, lang)}.')
        focus = (f'Η Σελήνη περνά σήμερα από τον {_house_phrase(moon_house, lang)}. '
                 f'Το συναίσθημα και η προσοχή σου ίσως στρέφονται προς αυτά τα θέματα.')
        season = (f'Ο Ήλιος βρίσκεται στον {_house_phrase(sun_house, lang)}: ένα θέμα που τις επόμενες εβδομάδες '
                  f'μπορεί να ζητά περισσότερο χώρο στη σκέψη σου.')
    else:
        sky_text = f'The Moon is {sign_in(moon_idx, lang)} ({phase}) and the Sun is {sign_in(sun_idx, lang)}.'
        focus = (f'The Moon passes through {_house_phrase(moon_house, lang)} today. '
                 f'Your mood and attention may turn towards these themes.')
        season = (f'The Sun is in {_house_phrase(sun_house, lang)}: a theme that may ask for more room '
                  f'in your thinking over the coming weeks.')

    sections = [dict(key='sky', title=titles['sky'], text=sky_text),
                dict(key='focus', title=titles['focus'], text=focus),
                dict(key='season', title=titles['season'], text=season)]

    mood = [_aspect_sentence(item, lang) for item in sky['aspects'][:2]]
    if mood:
        sections.append(dict(key='mood', title=titles['mood'], text=' '.join(mood)))

    if pos['Mercury']['retrograde']:
        mercury_house = solar_house(pos['Mercury']['sign'], idx)
        if el:
            text = (f'Ο Ερμής είναι ανάδρομος στον {_house_phrase(mercury_house, lang)}. Συμβολικά, είναι μια '
                    f'περίοδος για να ξαναδείς, να ελέγξεις και να διευκρινίσεις πριν προχωρήσεις.')
        else:
            text = (f'Mercury is retrograde in {_house_phrase(mercury_house, lang)}. Symbolically, this is '
                    f'a period for revisiting, double-checking and clarifying before moving on.')
        sections.append(dict(key='mercury', title=titles['mercury'], text=text))

    sections.append(dict(key='prompt', title=titles['prompt'], text=HOUSES[moon_house - 1][3 if el else 2]))

    tarot = draw_reading(spread='one', lang=lang, reversals=True,
                         rng=random.Random(f'daily-tarot-{on_date.isoformat()}'))
    card = tarot['cards'][0]
    return dict(
        date=on_date.isoformat(), sign=sign, sign_name=sign_name(idx, lang), glyph=SIGN_GLYPHS[idx], lang=lang,
        sky=dict(moon_sign=pos['Moon']['sign'], moon_house=moon_house, sun_sign=pos['Sun']['sign'],
                 moon_phase=phase, mercury_retrograde=pos['Mercury']['retrograde'],
                 aspects=[dict(body=a['body'], aspect=ASPECTS[a['aspect']][0], orb=a['orb'])
                          for a in sky['aspects']]),
        sections=sections,
        tarot=dict(id=card['id'], name=card['name'], glyph=card['glyph'], orientation=card['orientation'],
                   arcana=card['arcana'], theme=card['theme'], interpretation=card['interpretation'],
                   reflection=card['reflection'], disclaimer=tarot['disclaimer']),
        method=METHOD[lang], disclaimer=DISCLAIMER[lang])
