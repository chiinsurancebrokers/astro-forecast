"""Historical specialist readings from verified user-supplied scan pages.

Calculated evidence, author symbolism and editorial reflection remain separate.
No clinical interpretation or scientific validity is inferred from these books.
"""
import swisseph as swe
from .ephemeris import sign_of

REGIONS = {
 'Aries':('language and recording ideas',48,38),
 'Taurus':('reflection, reasoning and measurement',48,38),
 'Gemini':('culture, friendship and refinement of expression',48,38),
 'Cancer':('partnership and devotion',48,38),
 'Leo':('spiritual harmony and unity',49,39),
 'Virgo':('family, home and security',49,39),
 'Libra':('governance and a sense of justice',49,39),
 'Scorpio':('constructive work, cooperation and liberty',49,39),
 'Sagittarius':('resources, reserves and preservation',49,39),
 'Capricorn':('commerce, exchange and movement',50,40),
 'Aquarius':('home and sensory experience',50,40),
 'Pisces':('perception, art and appreciation of beauty',50,40),
}


def reference(source, title, author, page, printed, chapter):
 return {'source_id':source,'title':title,'author':author,'pdf_page':page,
         'printed_page':printed,'chapter':chapter,'kind':'verified_paraphrase'}


def run_historical_specialists(chart):
 jd=chart['julian_day']
 helio={}
 for name,pid in [('Earth',swe.EARTH),('Mercury',swe.MERCURY),('Venus',swe.VENUS),('Mars',swe.MARS),('Jupiter',swe.JUPITER),('Saturn',swe.SATURN)]:
  position,_=swe.calc_ut(jd,pid,swe.FLG_MOSEPH|swe.FLG_HELCTR)
  sign,degree=sign_of(position[0])
  helio[name]={'longitude':position[0],'sign':sign,'degree':degree}
 earth=helio['Earth'];theme,page,printed=REGIONS[earth['sign']]
 merton={'id':'merton','title':'Merton · A different planetary perspective',
  'basis':'Tropical heliocentric positions, calculated at your birth time',
  'paragraphs':[
   'This reading changes the viewpoint: planetary positions are measured from the Sun rather than from Earth. It adds a separate symbolic perspective to your main natal reading.',
   f"In this calculation Earth is in {earth['sign']} at {earth['degree']:.1f}°. Merton associates this zodiacal region with {theme}. This is the book’s regional symbolism; it is not a complete planet-by-planet character assessment.",
   f'As a reflection, consider the place of {theme} in your priorities. Compare that theme with your main natal reading and your experience, allowing differences between the two approaches to remain visible.'
  ],'evidence':helio,'references':[
   reference('merton_heliocentric','Heliocentric Astrology','Holmes W. Merton / Yarmo Vedra',28,18,'Astronomy'),
   reference('merton_heliocentric','Heliocentric Astrology','Holmes W. Merton / Yarmo Vedra',page,printed,'The Twelve Great Functions')],
  'scope':'Calculated heliocentric chart with verified regional symbolism. Detailed heliocentric planet-pair readings are not yet covered.'}
 # Daath's method checks several conditions together. This descriptive inspection
 # intentionally does not claim to implement his six formal strength measures.
 retro=[name for name,p in chart.get('planets', {}).items() if p.get('retrograde') and name not in ('Rahu','Ketu')]
 daath={'id':'daath','title':'Daath · Reading planetary condition in context',
  'basis':'Historical reading method applied to the separate Lahiri chart',
  'paragraphs':[
   'Daath’s useful contribution here is a method: do not judge a planet from one placement alone. His discussion considers position, aspects, motion and other kinds of strength together.',
   ('Planetary motion data is unavailable in this report. A full birth-chart calculation is needed before assessing this condition.' if not chart.get('planets') else 'The birth calculation marks '+', '.join(retro)+' as retrograde. This describes apparent motion from Earth; it does not establish a weakness, illness or outcome.' if retro else 'The birth calculation does not mark the classical planets as retrograde. This is one chart fact, not a verdict on their overall strength.'),
   'Use this specialist to understand why a balanced reading considers several factors before reaching a conclusion. The book’s physiological correspondences are kept as historical study material and are not converted into claims about your health.'
  ],'evidence':{'retrograde_planets':retro,'formal_strength_score':None},
  'references':[reference('daath_medical','Medical Astrology','Heinrich Daath',77,65,'Gauging Planetary Strength'),reference('daath_medical','Medical Astrology','Heinrich Daath',78,66,'Aspect and Positional Strength')],
  'scope':'A chart-conditioned explanation of Daath’s method; not a complete strength calculation or a medical reading.'}
 raleigh={'id':'raleigh','title':'Raleigh · Reflection on rhythm and change',
  'basis':'Hermetic philosophy; an editorial reflection exercise',
  'paragraphs':[
   'Raleigh presents motion, rhythm and number as organizing ideas in his Hermetic philosophy. This section uses that philosophical perspective to invite reflection on change and recurring patterns in life.',
   'Choose one theme from your natal reading. Record how it appears in your decisions over several weeks: what repeats, what changes, and what circumstances make a difference. Review your observations before drawing conclusions.',
   'The exercise is our application of the book’s philosophical theme. It is not a calculation of your destiny or a numerical personality score. Raleigh’s historical physical theories are not treated as modern scientific evidence.'
  ],'evidence':{'personal_numeric_score':None},
  'references':[reference('raleigh_hermetic','Hermetic Science of Motion and Number','A. S. Raleigh',9,1,'Lesson I: The Law of Motion'),reference('raleigh_hermetic','Hermetic Science of Motion and Number','A. S. Raleigh',15,7,'The Keynote')],
  'scope':'Source-based philosophical reflection. It makes no invented chart rules or numerology claims.'}
 return [merton,daath,raleigh]


def plan_catalogue():
 return {'mode':'staging_preview','billing_active':False,'currency':'EUR',
  'plans':[
   {'id':'free','name':'Free','price':0,'features':['Core Western natal reading','Natal chart and birth details','Bibliography and source notes']},
   {'id':'plus','name':'Plus','price':None,'features':['Merton heliocentric perspective','Daath planetary-condition study','Raleigh reflection guide','Lahiri specialist chart','Compatibility','Career and purpose','Location comparison','Timing outlook']}],
  'activation_note':'All implemented tools are available to review in this staging preview. Paid subscriptions and access restrictions are not active. Plus pricing has not been set.'}
