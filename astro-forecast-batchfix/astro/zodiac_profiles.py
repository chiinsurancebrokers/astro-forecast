"""Twelve Western Sun-sign profiles with source and editorial roles separated."""

# These prompts apply the checked White descriptions to self-reflection. They
# are editorial questions, not additional claims attributed to the author.
PROMPTS = {
 'Aries':('initiative and independence','patience and cooperation','Where does taking the lead help, and when would sharing responsibility help more?','How can you express a need directly while leaving room for another person?','Which project needs a first step, and which needs steady follow-through?'),
 'Taurus':('patience and persistence','flexibility when circumstances change','Which foundations are worth protecting, and which familiar approach needs review?','How do you provide consistency without expecting another person to remain unchanged?','Where does sustained effort bring value, and what evidence would make you adapt?'),
 'Gemini':('curiosity and investigation','continuity beyond the first excitement','Which interests have helped you grow, and which deserve deeper attention?','How do you listen as carefully as you exchange ideas?','Which skill will you practise long enough to turn curiosity into competence?'),
 'Cancer':('sensitivity, patient effort and attachment to home','supportive surroundings and clear needs','What helps you feel supported, and what can you ask for more clearly?','How do you balance care for others with expressing your own needs?','Which surroundings help you work steadily, and which need a practical change?'),
 'Leo':('generosity, independence and determination','persistence and shared contribution','When has leading helped, and when has contributing alongside others helped?','How can you show generosity while giving another person room to express themselves?','What contribution will you sustain even when recognition takes time?'),
 'Virgo':('thoughtfulness, industry and discrimination','confidence alongside constructive criticism','Which careful habit serves you, and when does criticism interrupt progress?','How do you offer useful feedback without making care feel conditional?','What is good enough to test now, and what truly needs further refinement?'),
 'Libra':('weighing alternatives and appreciation of harmony','balancing reason and intuition','Which decision needs careful comparison, and which needs a clear choice?','How can you preserve kindness while speaking about a disagreement?','What criteria will help you choose between appealing alternatives?'),
 'Scorpio':('patience, determination and resistance to imposition','releasing a remembered injury','What boundary protects you, and what past conflict still takes energy?','How can you express a boundary without carrying every past disagreement into the present?','Which long effort remains worthwhile, and which conflict needs a different response?'),
 'Sagittarius':('ambition, foresight and varied interests','independence with considered commitments','Which wider goal matters enough to translate into everyday steps?','How do you make space for independence and shared expectations?','Which broad interest can become a concrete, sustained contribution?'),
 'Capricorn':('practical reasoning and sustained ambition','expressing inward sympathy more openly','What have you built through steady effort, and what support would help you continue?','How do you make care visible when your manner is reserved?','Which long-term aim needs a realistic sequence of responsibilities?'),
 'Aquarius':('practical reasoning, generosity and independence','strong convictions with kindness and openness','Which convictions have helped you rebuild, and which deserve another perspective?','What makes a group or partnership feel meaningful: shared values, kindness, contribution or recognition?','How can you use independent thinking to create a contribution others can understand and trust?'),
 'Pisces':('imagination, idealism and sustained study','confidence in putting abilities forward','Which ideal can you develop through study and a practical next step?','How can you make your feelings and expectations easier for another person to understand?','Where would showing your work help others recognise an ability you have developed?'),
}

def build_zodiac_profile(sign,readings,cite):
    if sign not in PROMPTS:
        raise ValueError('Choose one of the twelve zodiac signs.')
    strength,balance,self_question,relationship,work=PROMPTS[sign]
    index=list(readings).index(sign)
    ref=cite('white_guide',index+8,index+2,sign)
    bart=cite('bart_success',18,10,'How Astrology Helps: Personal Agency')
    return {'sign':sign,'title':sign+' · understanding yourself',
      'intro':'A Western tropical Sun-sign profile is one perspective on identity. It does not describe your entire personality or determine your experiences. Your Moon, Ascendant, other planets and lived circumstances add context.',
      'sections':[
       {'title':'The source perspective','paragraphs':[readings[sign]],'role':'verified_paraphrase','citations':[ref]},
       {'title':'Strengths to develop','paragraphs':[f'The themes to explore are {strength}. Compare them with specific examples from your life: where have these qualities helped, and where do they not fit your experience?'],'role':'editorial_application'},
       {'title':'The balance to practise','paragraphs':[f'The balancing theme is {balance}. This is an invitation to examine a habit, rather than a label that must be true of you.',self_question],'role':'editorial_application'},
       {'title':'Belonging and relationships','paragraphs':[relationship,'A Sun sign cannot identify the person you will meet, their birthplace or the home you will share. Use this question to clarify what you want to build with another person.'],'role':'editorial_application'},
       {'title':'Work, purpose and contribution','paragraphs':[work,'Connect the theme with a skill, contribution or responsibility you can demonstrate. Career achievement comes through your actions, opportunities and circumstances; a sign is not proof of future wealth or status.'],'role':'editorial_application'},
       {'title':'Making sense of turning points','paragraphs':['Keep three things distinct: what happened, how you responded and what you hope to build next. Belle Bart’s personal-agency principle supports using self-knowledge constructively. It does not make a sign the cause of bereavement, family conflict or financial loss.','For each turning point, ask what changed, what support was available, what you learned and what you would handle differently now. These review questions are editorial applications.'],'role':'editorial_application','citations':[bart]},
      ],'references':[ref,bart],
      'method':'White’s checked Sun-sign passage supplies the source perspective. The development, relationship, work and life-review questions are platform editorial applications. The profile does not calculate event dates or infer a person’s history from their sign.'}
