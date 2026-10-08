"""Substantial source-grounded Western character profiles."""

def build_zodiac_profile(sign, readings, cite):
    from .bart_profiles import BART_PROFILES
    if sign not in BART_PROFILES:
        raise ValueError('Choose one of the twelve zodiac signs.')
    entry = BART_PROFILES[sign]
    refs = [cite('bart_success', page, page - 8, sign + ' character, vocation and associations')
            for page in entry['pages']]
    white = cite('white_guide', list(readings).index(sign) + 8,
                 list(readings).index(sign) + 2, sign)
    sections = [{'title': entry['core'], 'paragraphs': entry['character'],
                 'role': 'source_synthesis', 'citations': refs}]
    for key, title in [('strength', 'Your strongest resources'),
                       ('difficulty', 'Where your strengths can become difficulties'),
                       ('relationships', 'Relationships and belonging'),
                       ('vocation', 'Work, ambition and contribution'),
                       ('growth', 'How your character develops through change')]:
        sections.append({'title': title, 'paragraphs': [entry[key]],
                         'role': 'source_synthesis_with_editorial_application',
                         'citations': refs})
    supporting = [readings[sign]]
    supporting_refs = [white]
    if sign == 'Aquarius':
        supporting.append('Karma adds a distinctive social dimension: an attachment to friends and a social circle, alongside originality, interest in scientific investigation and a broad conception of human progress. This helps explain the tension between wanting to belong and thinking beyond a group’s established conventions. Time apart can give independent thought room to develop before returning to shared activity.')
        supporting_refs += [cite('karma_ancient_egyptians', 71, 59, 'The Sun in Aquarius'),
                            cite('karma_ancient_egyptians', 72, 60, 'The Sun in Aquarius continued')]
    sections.append({'title': 'Further perspective from the library', 'paragraphs': supporting,
                     'role': 'source_synthesis', 'citations': supporting_refs})
    return {'sign': sign, 'title': sign + ' · your character profile',
            'intro': 'A portrait of temperament, relationships, vocation and personal development, drawn from the library’s Western astrology texts.',
            'ruler': entry['ruler'], 'sections': sections, 'references': refs + supporting_refs,
            'method': 'Belle Bart’s checked character chapter supplies the main portrait; White supplies a second perspective, with Karma added where the relevant passage has been checked. The prose is an original synthesis, with contemporary work and relationship applications identified in the reading. This is a historical astrological portrait, not a validated personality assessment. A full natal reading also considers the calculated Moon, Ascendant, houses and aspects. Bart’s fixed birth-date boundaries are not used to calculate the Sun sign. Her disease claims and guaranteed outcomes are not adopted. Her 1923–1930 forecast tables are not shifted into modern years: current timing requires fresh planetary calculations. This profile does not calculate event dates.'}
