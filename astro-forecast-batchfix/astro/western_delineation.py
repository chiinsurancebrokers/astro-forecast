"""Curated, non-deterministic paraphrases of White and Raphael.

Sign traits and house topics are source material. Joining those two layers,
reflection prompts and ruler-to-house links are editorial applications, not
verbatim historical planet-in-house predictions. No raw scan text is stored.
"""
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
# Raphael's convention includes Uranus as ruler of Aquarius (PDF 30-31).
RULERS = dict(zip(SIGNS, ['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Jupiter']))
HOUSE_TOPICS = {
 1: ('Your approach to life', 'personal bearing and the way you meet the world',14),
 2: ('Money and possessions', 'money, possessions and material resources',15),
 3: ('Learning and everyday contact', 'writing, siblings, neighbours and short journeys',15),
 4: ('Home and foundations', 'family origins, property and the foundations of life',15),
 5: ('Pleasure and creative expression', 'pleasure, children and speculative ventures',15),
 6: ('Daily work and responsibilities', 'service and the people involved in everyday work',15),
 7: ('Partnership and negotiation', 'marriage, business partnerships and dealings with others',15),
 8: ('Shared resources and legacies', 'a partner’s resources, wills and inheritances',15),
 9: ('Study and wider horizons', 'long journeys, religion and wider beliefs',15),
 10: ('Vocation and public standing', 'profession, honour and public standing',15),
 11: ('Friendship and aspirations', 'friends, hopes and wishes',15),
 12: ('Private pressures and boundaries', 'hidden opposition and circumstances outside public view',16),
}
# Each entry is (interpretive theme, PDF page). Printed page = PDF - 6.
SIGN_TRAITS = {
 'Moon': [
 ('restlessness, imagination and a wish for movement, alongside persistence',37),
 ('a peaceful, obliging temperament, sympathy and intuition',37),
 ('sympathy, interest in art and a preference to avoid quarrelling',37),
 ('sensitivity, sociability, kindness and attachment to both home and travel',37),
 ('ambition, perseverance, order and a wish to take the lead',37),
 ('interest in study and distinction, with a reflective temperament',37),
 ('courtesy, sociability, reasoning and a quick sense of fairness',37),
 (None,37),
 ('generosity, warmth, ambition and a capacity to forgive',37),
 ('ambition and daydreaming, contrasted with uncertainty and uneven energy',38),
 ('courtesy, inventiveness and imagination, with a pull toward changing projects',38),
 ('poetic imagination, comfort and dreaminess, alongside changing interests',38),
 ],
 'Mercury': [
 ('quick, fluent argument and an impulsive style of thinking',38),
 ('good judgment, reasoning and perseverance, alongside strong preferences',38),
 ('quick wit, ingenuity, reading, numbers and an interest in science or literature',38),
 ('discretion and good nature, alongside adaptability and a restless mind',38),
 ('ambition, confidence and determination, with a forceful speaking style',38),
 ('memory, invention, language, literature and persuasive expression',39),
 ('learning, invention, mathematical interests and a sense of fairness',39),
 ('ingenuity, study and careful attention to personal interests',39),
 ('ambition, judgment, appreciation of nature and a wish to explore',39),
 ('penetrating thought, scientific or literary interests and a need to stay occupied',39),
 ('study, reasoning and observation, with a need for solitude or learned company',39),
 ('many capabilities and ideas, enjoyment of travel and changing interests',39),
 ],
 'Venus': [
 ('strong affection and an interest in music and art',39),
 ('warmth, sympathy, sociability and enjoyment of music, art and pleasure',39),
 ('sympathy, wisdom and inventive ability',39),
 ('changeable affections; the passage also stresses modifying factors elsewhere in the chart',39),
 ('kindness, sympathy, friends and an interest in music, art or public expression',40),
 ('quiet living and deep sympathies that may be difficult to express',40),
 ('a happy, sociable disposition and enjoyment of life',40),
 ('strong desires, pride and jealousy as a relationship tension',40),
 ('friendship, social connections and an inclination toward public expression',40),
 (None,40),
 ('a calm disposition and unconventional ideas about relationships or religious life',40),
 ('wisdom, intellect and interest in knowledge',40),
 ],
 'Mars': [
 ('courage, determination, mechanical interests and readiness to defend a position',40),
 ('determination, strong will and resistance to being pushed into action',40),
 ('mental acuteness, ingenuity, ambition and generosity',40),
 ('boldness, changeability and difficulty sustaining a continuous course',40),
 ('force of character, leadership and a taste for argument and reasoning',40),
 ('originality and bold scientific interests, alongside haste and irritability',41),
 ('enterprise, scientific interests and a wish to take responsibility',41),
 ('invention, machinery and technical interests, alongside impulsiveness',41),
 ('generosity, debate, mechanical interests and dislike of being ordered about',41),
 ('courage and a taste for adventure and excitement',41),
 ('reform, invention, scientific interests and an independent line of reasoning',41),
 ('generosity and caution, with a more forceful response when provoked',41),
 ],
 'Jupiter': [
 ('ambition, determination and enterprise',41),
 ('strength of character, justice and supportive social connections',41),
 ('mathematical ability, invention, literature and dealings with organisations',41),
 ('ambition, enterprise and a wish to participate in public life',42),
 ('courage, generosity, ambition, prudence and readiness for responsibility',42),
 ('study, science, knowledge and understanding natural laws',42),
 ('an obliging temperament, justice and helpful social connections',42),
 ('ambition, resolution and a strong desire to direct matters',42),
 ('courtesy, humane conduct, sociability and leadership',42),
 ('ingenuity contrasted with a tendency toward inactivity',42),
 ('good humour, justice, industry and an interest in science',42),
 ('study, varied talents and valued friendships',42),
 ],
 'Saturn': [
 ('resolution, contemplation and reasoning, with a taste for argument',42),
 ('persistence, kindness and a preference for solitude',43),
 ('observation, ingenuity, mathematics and scientific work',43),
 ('changing opinions and dissatisfaction with surroundings',43),
 ('generosity, caution and dislike of being controlled',43),
 ('study, intuition and reserve, alongside a tendency to hold on to frustration',43),
 ('debate, science and a strong sense of personal opinion',43),
 ('anxiety and sudden resolve; this is read as a tension to examine, not a lifelong sentence',43),
 ('a wish to help others, sensitivity to insult and divided professional interests',43),
 ('caution, deep thought, seriousness and a tendency to retain anger',43),
 ('courtesy, imagination and penetrating thought, with a measured pace',43),
 ('uncertainty and changeability',43),
 ],
 'Uranus': [
 ('invention, machinery, reasoning and resistance to imposition',44),
 ('determination and intuition',44),
 ('reading, science, invention and introducing new ideas',44),
 ('original expression, restlessness and travel',44),
 ('strong will and resistance to being contradicted or directed',44),
 ('quiet independence, unusual interests and science',44),
 ('scientific interests, ambition, travel and reasoning',44),
 ('determination, privacy and mechanical invention',44),
 ('enthusiasm, generosity and a strong wish for independence',44),
 ('restlessness, independence and deep reasoning',44),
 ('ingenuity, scientific novelty, imagination and unconventional beliefs',44),
 ('quietness and a tendency to consider the more difficult side of the future',44),
 ],
 'Neptune': [
 ('original ideas, religious interests and mechanical invention',44),
 ('enthusiasm in belief, interest in old or unusual subjects and a soft heart',45),
 ('invention, mathematics, perception and sympathetic feeling',45),
 ('imagination, travel and restlessness',45),
 ('ambition, intuition and a quiet, inward depth',45),
 ('mathematical interests and unconventional relationship ideas',45),
 ('a tender heart and interest in spiritual or unusual studies',45),
 ('persistence, privacy, invention and chemical interests',45),
 ('travel, foresight, reasoning and religious interests',45),
 ('courage combined with caution, reverence and an emphasis on faith',45),
 ('travel, nature and independent religious ideas',45),
 ('quiet depth, intuition and attachment to water or travel',45),
 ],
}
PLANET_TITLES = {'Sun':'Direction and motivation','Moon':'Temperament and response','Mercury':'Thinking and communication','Venus':'Affection and what you value','Mars':'Initiative and action','Jupiter':'Opportunity and wider perspective','Saturn':'Caution and sustained effort','Uranus':'Originality and independence','Neptune':'Imagination and belief'}
# Specific usable planet-in-house passages, separately attributed from the
# editorial joining of sign traits and house topics. Coverage is intentionally
# conservative; skipped historical illness/death/moral judgments are not softened
# into fabricated favourable meanings.
HOUSE_PASSAGES = {
 ('Saturn',3): ('Raphael describes a serious, contemplative and persevering approach, with interest in unusual subjects.',51,47),
 ('Jupiter',9): ('Raphael associates this placement with sincerity, prudence and a religious turn of mind.',56,52),
 ('Jupiter',11): ('Raphael emphasizes friends and the help or advice they may offer, with the interpretation modified by Jupiter’s condition.',57,53),
 ('Sun',3): ('Raphael emphasizes scientific or artistic interests and steadiness of opinion.',63,59),
 ('Sun',9): ('Raphael emphasizes firmness and faithfulness of purpose.',63,59),
 ('Sun',10): ('Raphael gives prominence to honour and public recognition; these are themes here, not guaranteed achievements.',63,59),
 ('Venus',3): ('Raphael emphasizes a cheerful mind, reading, poetry and support from nearby connections.',66,62),
 ('Venus',9): ('Raphael emphasizes reading, poetry, enjoyable journeys and sincere belief.',66,62),
 ('Venus',10): ('Raphael emphasizes an agreeable manner and esteem in public life.',66,62),
 ('Venus',11): ('Raphael emphasizes valued friendships and friends willing to help.',67,63),
 ('Mercury',3): ('Raphael emphasizes study, scientific interests, unusual subjects and travel.',68,64),
 ('Mercury',9): ('Raphael emphasizes an alert mind, science, learning and religious studies.',69,65),
 ('Mercury',10): ('Raphael emphasizes literature, trade, original talent and speaking ability.',69,65),
 ('Mercury',11): ('Raphael emphasizes friends with scientific interests, with support depending on the planet’s condition.',69,65),
 ('Moon',3): ('Raphael emphasizes short journeys, study and nearby connections.',70,66),
 ('Moon',4): ('Raphael emphasizes movement of residence and matters of land or home.',70,66),
}


EXALTATIONS = {'Sun':'Aries','Moon':'Taurus','Mercury':'Virgo','Venus':'Pisces','Mars':'Capricorn','Jupiter':'Cancer','Saturn':'Libra','Uranus':'Scorpio'}
HOUSE_GUIDANCE = {
 1:'Notice which qualities you bring into a new situation before you have time to adapt to it.',
 2:'Consider how you earn, use and protect resources, and whether those choices reflect what you value.',
 3:'The practical expression is in how you learn, write and stay in contact with people around you.',
 4:'Consider the sort of home and foundation that allows these qualities to develop with stability.',
 5:'Make room for pleasure and expression without assuming that enjoyment must lead to a particular outcome.',
 6:'Consider how these qualities affect cooperation, everyday obligations and the way you organise your work.',
 7:'These themes become visible through negotiation and partnership; compare your expectations with the other person’s needs.',
 8:'Clarity about shared commitments and resources gives this area a constructive place in your life.',
 9:'Study, travel and a considered view of your beliefs offer ways to give these qualities a wider purpose.',
 10:'Consider the contribution you want to make, how you communicate it and the responsibilities you are willing to sustain.',
 11:'Friendships and shared aspirations provide a setting in which these qualities can be developed with others.',
 12:'Consider how you respond to private pressures and where clearer boundaries or a quieter space would help.',
}


def essential_condition(name, sign):
    labels = []
    if RULERS[sign] == name:
        labels.append('domicile')
    if RULERS[SIGNS[(SIGNS.index(sign)+6)%12]] == name:
        labels.append('detriment')
    exalted = EXALTATIONS.get(name)
    if sign == exalted:
        labels.append('exaltation')
    if exalted and sign == SIGNS[(SIGNS.index(exalted)+6)%12]:
        labels.append('fall')
    return labels


def build_western_delineation(planets, chart, aspects, cite, sun_readings):
    planet_sections = []
    for name, p in planets.items():
        if name == 'Sun':
            theme = sun_readings[p['sign']]
            refs = [cite('white_guide',SIGNS.index(p['sign'])+8,SIGNS.index(p['sign'])+2,p['sign'])]
        else:
            theme, page = SIGN_TRAITS[name][SIGNS.index(p['sign'])]
            refs = [cite('white_guide',page,page-6,f"{name} in {p['sign']}")]
            if (name,p['sign']) in {('Mercury','Virgo'),('Saturn','Taurus')}:
                refs.insert(0,cite('white_guide',page-1,page-7,f"{name} in {p['sign']}, beginning"))
            theme = ('White’s usable descriptive themes here are '+theme+'.' if theme else
                     'This sign passage consists mainly of historical moral or relationship verdicts. It is not used to assign you a character label or predict an outcome; the house and aspect evidence below provide the remaining context.')
        refs.append(cite('white_guide',45,39,'Note on the Planetary Sign Descriptions'))
        house = p.get('house')
        first = f"Your {name} is in {p['sign']} at {p['sign_deg']:.1f}°" + (f", in house {house}. " if house else '. ') + theme
        paragraphs = [first]
        condition = essential_condition(name,p['sign'])
        if condition:
            strong = any(label in {'domicile','exaltation'} for label in condition)
            paragraphs.append(f"In Raphael’s scheme, this position is called {' and '.join(condition)}. " + ('The traditional reading treats this as affinity between the planet and its sign; its expression still depends on the rest of the chart.' if strong else 'The traditional reading treats this as a mismatch between the planet and its sign; it asks for context from the other placements and aspects, rather than a judgment about your ability or prospects.'))
            refs.append(cite('raphael_guide',30,26,'Essential Dignities and Ruling Planets'))
            refs.append(cite('raphael_guide',31,27,'Essential Dignities: Exaltation, Fall and Detriment'))
        if house:
            topic = HOUSE_TOPICS[house][1]
            paragraphs.append(f"In practical terms, this brings the {PLANET_TITLES[name].lower()} theme into {topic}. "+HOUSE_GUIDANCE[house])
            refs.append(cite('raphael_guide',HOUSE_TOPICS[house][2],HOUSE_TOPICS[house][2]-4,'The Mundane Houses'))
            passage = HOUSE_PASSAGES.get((name,house))
            if passage:
                text,page,printed = passage
                paragraphs.append(text)
                refs.append(cite('raphael_guide',page,printed,f'{name} in house {house}'))
        related = [a for a in aspects if name in (a['a'],a['b'])]
        if related:
            close = sorted(related,key=lambda a:a['orb'])[:2]
            labels = ', '.join(f"{a['a']}–{a['b']} {a['aspect']} ({a['orb']:.2f}° from exact)" for a in close)
            paragraphs.append('The closest selected aspect connections are '+labels+'. They qualify the reading rather than changing it into a verdict; interpretations of verified combinations appear in the main synthesis.')
        planet_sections.append({'title':name+' · '+PLANET_TITLES[name], 'planet':name,'paragraphs':paragraphs,'evidence':dict(p,essential_condition=condition),'citations':refs})
    houses = []
    overview = None
    if chart:
        asc = chart['ascendant']['sign']
        start = SIGNS.index(asc)
        for house in range(1,13):
            sign = SIGNS[(start+house-1)%12]
            ruler = RULERS[sign]; rp = planets[ruler]
            title,topic,page = HOUSE_TOPICS[house]
            occupants = [name for name,p in planets.items() if p['house']==house]
            occupant_text = ('This house contains '+', '.join(occupants)+'. Their individual readings describe how those themes may be expressed in this area.' if occupants else
                             'No included planet occupies this house. This does not make the area absent or unimportant; the ruling planet gives another connection to examine.')
            ruler_text = f"Its sign is {sign}, ruled here by {ruler}. {ruler} is in {rp['sign']}, in house {rp['house']}, linking this topic with {HOUSE_TOPICS[rp['house']][1]}. The link is an editorial reading of the ruler’s placement, not a forecast of an event."
            houses.append({'title':f'House {house} · {title}','house':house,'sign':sign,'ruler':ruler,'occupants':occupants,'ruler_house':rp['house'],
                           'paragraphs':[f'This area concerns {topic}. '+occupant_text,ruler_text],
                           'citations':[cite('raphael_guide',page,page-4,'The Mundane Houses'),cite('raphael_guide',76,72,'How to Judge a Nativity')]})
        chart_ruler = RULERS[asc]; p = planets[chart_ruler]
        occupied = sorted((h for h in houses if h['occupants']),key=lambda h:(-len(h['occupants']),h['house']))
        prominent = occupied[:3]
        topics = '; '.join(f"{HOUSE_TOPICS[h['house']][0].lower()} (house {h['house']}: {', '.join(h['occupants'])})" for h in prominent)
        overview = {'title':'How the planets and houses come together','paragraphs':[
          f"With {asc} rising, {chart_ruler} is the chart ruler in Raphael’s convention. Its position in {p['sign']}, house {p['house']}, brings {HOUSE_TOPICS[p['house']][1]} into the way you approach life. Start with the {chart_ruler} reading below, then consider its connections to other planets.",
          'The most occupied houses are '+topics+'. This count helps organise the reading; it is not a numerical strength score. These areas connect the individual planetary themes with concrete parts of life.',
          'Consider the recurring themes together: a placement in a public or relational house describes an area of expression, while its sign and aspects can support or complicate that expression. The twelve-house analysis includes both occupied and empty houses, so the reading is not reduced to a few highlighted placements.'
        ],'citations':[cite('white_guide',45,39,'Note on the Planetary Sign Descriptions'),cite('raphael_guide',30,26,'Essential Dignities and Ruling Planets'),cite('raphael_guide',76,72,'How to Judge a Nativity'),cite('white_guide',46,40,'The Radix')]}
    return {'planet_sections':planet_sections,'house_sections':houses,'overview':overview,
            'method_note':'White qualifies sign descriptions by the planet’s role as ruler or significator and by its aspects (PDF p. 45 / printed p. 39). Secondary placements are therefore themes to examine, not nine independent personality diagnoses. House topics follow Raphael; whole-sign placement, ruler links and modern applications are platform choices. Raphael uses Uranus for Aquarius and Jupiter for Pisces. No illness, death, fertility or guaranteed wealth predictions are made.'}
