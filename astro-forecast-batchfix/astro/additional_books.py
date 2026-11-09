"""Selected, page-checked paraphrases from the three October uploads.

Pontin PDF 7/8 = printed 4/5; Leo PDF 48 = printed 26;
Bart PDF 18 = printed 10. No complete scanned text is redistributed.
"""
MERCURY = {
 'Leo': ('enthusiasm, independent opinions and a wish to encourage others',7,4),
 'Virgo': ('analysis, discrimination and attention to practical details',7,4),
 'Libra': ('diplomacy, refined expression and considering both sides of a question',7,4),
 'Sagittarius': ('direct expression, intuition and an active interest in wider questions',7,4),
 'Aquarius': ('imagination, flexible thinking and interests in culture and science',8,5),
 'Pisces': ('seeking underlying causes, intuitive understanding and adaptability',8,5),
}

def additional_natal_sections(planets, cite):
    sections=[]
    mercury=planets.get('Mercury',{})
    if mercury.get('sign') in MERCURY:
        themes,page,printed=MERCURY[mercury['sign']]
        sections.append({'title':'How to develop your thinking and communication',
          'paragraphs':[f"Your Mercury is in {mercury['sign']}. Pontin’s description connects this placement with {themes}. Read alongside the other planets and houses, this offers a way to examine how you learn, explain an idea and respond to another person’s viewpoint.",
          'To put this theme to use, choose a real conversation or learning goal. Notice what helps you understand it, ask for feedback and revise your approach. This exercise is an editorial application, not a prediction or a fixed judgment of your abilities.'],
          'citations':[cite('pontin_manual',page,printed,'Mercury in '+mercury['sign'])]})
    sections.append({'title':'Turning self-knowledge into preparation',
      'paragraphs':['A reading is most useful when it helps you recognise a strength, notice a recurring difficulty and decide what you can do about it. Belle Bart presents self-knowledge and personal agency as central to her approach: planetary symbolism does not remove your ability to choose.',
      'Before the next dated chapter, write down one pattern you want to keep, one response you want to change and one practical step you can take. After the transition, review what actually changed in your circumstances. The exercise is our application of that principle; the date itself does not guarantee a life event.'],
      'citations':[cite('bart_success',18,10,'How Astrology Helps')]})
    return sections

def esoteric_sections(planets,cite):
    saturn=planets.get('Saturn')
    if not saturn:
        return []
    ref=cite('leo_esoteric',48,26,'Spheres of Influence: Saturn')
    ref['system']='ESOTERIC_HISTORICAL'
    return [{'title':'Alan Leo · responsibility and inner development',
      'paragraphs':['This is a separate historical esoteric perspective. Leo describes Saturn as a symbol of duty, limits, perseverance and the gradual development of stability and self-control. His spiritual framework is not a method for calculating future events.',
      f"Your calculated Western Saturn is in {saturn['sign']}"+(f", house {saturn['house']}" if saturn.get('house') else '')+'. As an editorial reflection, use the Saturn section of your natal reading to identify a responsibility that needs patience, then choose a sustainable commitment. The checked passage supplies general Saturn symbolism, not a sign-specific or house-specific esoteric delineation.',
      'Consider: which limit can I work within constructively, and which habit would help me become more consistent? The report does not infer past lives, karmic debts, spiritual rank or deservingness from a chart.'],
      'citations':[ref]}]


# Max Heindel, Simplified Scientific Astrology (1919). Printed p. -> PDF p. is +8.
HEINDEL_HOUSE = {
 1: 'the body, early surroundings and the home of childhood',
 2: 'finances',
 3: 'practical intelligence, the useful arts, short journeys and brothers and sisters',
 4: 'the home and the conditions of later life',
 5: 'amusement, courtship, children and speculation',
 6: 'health, work and the people who help you',
 7: 'partnership, marriage and dealings with the public',
 8: 'inheritance and endings',
 9: 'religion, idealism, justice and long journeys',
 10: 'profession, social position and ambition',
 11: 'friends, hopes and wishes',
 12: 'solitude, confinement and hard times, which Heindel treats as lessons',
}
HEINDEL_QUALITY = {
 'Cardinal': ('Cardinal', 'promote activity and getting things started', 108, 100),
 'Fixed': ('Fixed', 'give steadiness and perseverance', 126, 118),
 'Common': ('Common', 'are flexible and changeable', 109, 101),
}
_QUALITY_OF = {s: ['Cardinal', 'Fixed', 'Common'][i % 3] for i, s in enumerate(
    ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'])}


def heindel_sections(planets, cite):
    """A separate historical esoteric perspective; computed facts first, paraphrase second."""
    core = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    present = [n for n in core if n in planets and planets[n].get('sign') in _QUALITY_OF]
    if not present:
        return []
    sections = []
    counts = {}
    for n in present:
        counts.setdefault(_QUALITY_OF[planets[n]['sign']], []).append(n)
    ranked = sorted(counts.items(), key=lambda kv: -len(kv[1]))
    # A lean needs a clear majority of the seven planets (4+), not just a plurality.
    lead = ranked[0] if len(ranked[0][1]) >= 4 else None
    facts = '; '.join(f"{q}: {', '.join(v)}" for q, v in sorted(counts.items()))
    if lead:
        q, who = lead
        name, text, pdf, printed = HEINDEL_QUALITY[q]
        para = (f"Your seven classical planets fall by quality as follows: {facts}. {len(who)} of {len(present)} are in {name} signs, "
                f"which Heindel says {text}. Read this as a leaning in how you tend to act, not a verdict.")
        cites = [cite('heindel_simplified', pdf, printed, name + ' Signs')]
    else:
        para = (f"Your seven classical planets fall by quality as follows: {facts}. No single quality leads, so this chart "
                "does not lean strongly toward starting, persevering or adapting; the mix is the point.")
        cites = [cite('heindel_simplified', 108, 100, 'Cardinal, Fixed and Common Signs')]
    sections.append({'title': 'Heindel · quality of your signs', 'paragraphs': [para], 'citations': cites})
    lines = []
    for n in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']:
        house = planets.get(n, {}).get('house')
        if house in HEINDEL_HOUSE:
            lines.append(f"Your {n} is in house {house}; Heindel lists {HEINDEL_HOUSE[house]} under this house.")
    if lines:
        sections.append({'title': 'Heindel · where your personal planets sit',
                         'paragraphs': lines + ['These are traditional topics of each house, not predictions. Use them to ask where '
                                                'in life each planet\'s theme is most likely to show up.'],
                         'citations': [cite('heindel_simplified', 39, 31, 'The Twelve Houses')]})
    sections.append({'title': 'Heindel · how to read difficult aspects',
                     'paragraphs': ['Heindel rejects the habit of calling aspects good or evil. He compares hard aspects to the grinding '
                                    'that polishes a stone: uncomfortable while it happens, and part of how a person develops. '
                                    'This is a spiritual-philosophical stance, not a statistical claim.'],
                     'citations': [cite('heindel_simplified', 84, 76, 'The Aspects')]})
    return sections
