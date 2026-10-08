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
