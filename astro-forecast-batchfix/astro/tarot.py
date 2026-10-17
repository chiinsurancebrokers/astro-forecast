"""Native 78-card reflective tarot; no external services or stored questions.

Original editorial summaries of common tarot symbolism. Minor cards combine
rank and suit themes, transparently; this is not a predictive or AI reading.
"""
from datetime import datetime, timezone
from secrets import SystemRandom
from uuid import uuid4

# name EN, name EL, upright EN/EL, reversed EN/EL, symbolic glyph
MAJORS = [
 ('The Fool','Ο Τρελός','openness, beginnings and a willingness to explore','ανοιχτότητα, ξεκινήματα και διάθεση εξερεύνησης','pause before a leap and check what you have overlooked','μια παύση πριν από το άλμα και έλεγχο όσων παραβλέπεις','✧'),
 ('The Magician','Ο Μάγος','initiative and putting available skills into practice','πρωτοβουλία και αξιοποίηση των δεξιοτήτων σου','clarifying your intention before scattering your energy','αποσαφήνιση της πρόθεσης πριν διασκορπίσεις την ενέργειά σου','∞'),
 ('The High Priestess','Η Αρχιέρεια','quiet observation and listening to your inner response','ήρεμη παρατήρηση και ακρόαση της εσωτερικής σου απόκρισης','distinguishing intuition from assumptions and missing information','διάκριση ανάμεσα στη διαίσθηση, τις υποθέσεις και την ελλιπή πληροφόρηση','☾'),
 ('The Empress','Η Αυτοκράτειρα','care, creativity and nurturing what matters','φροντίδα, δημιουργικότητα και καλλιέργεια όσων έχουν αξία','restoring your own reserves rather than giving without limits','αποκατάσταση των δικών σου αποθεμάτων και όρια στην προσφορά','❀'),
 ('The Emperor','Ο Αυτοκράτορας','structure, responsibility and clear boundaries','δομή, ευθύνη και σαφή όρια','reconsidering rigidity, control or unclear responsibilities','επανεξέταση της ακαμψίας, του ελέγχου ή των ασαφών ευθυνών','♜'),
 ('The Hierophant','Ο Ιεροφάντης','learning, shared values and inherited traditions','μάθηση, κοινές αξίες και παραδόσεις','examining which inherited rules still fit your values','εξέταση των κανόνων που εξακολουθούν να ταιριάζουν στις αξίες σου','✥'),
 ('The Lovers','Οι Εραστές','alignment between values, choices and connection','ευθυγράμμιση αξιών, επιλογών και σύνδεσης','clarifying a mismatch between what you value and what you choose','αποσαφήνιση της απόστασης ανάμεσα σε αξίες και επιλογές','♡'),
 ('The Chariot','Το Άρμα','direction, self-discipline and coordinated effort','κατεύθυνση, αυτοπειθαρχία και συντονισμένη προσπάθεια','slowing down to regain direction instead of forcing progress','επιβράδυνση για επαναπροσδιορισμό της πορείας','➶'),
 ('Strength','Η Δύναμη','patience, compassion and steady courage','υπομονή, συμπόνια και σταθερό θάρρος','meeting self-doubt or frustration with gentleness','αντιμετώπιση της αμφιβολίας και της απογοήτευσης με επιείκεια','♌'),
 ('The Hermit','Ο Ερημίτης','solitude, perspective and considered inquiry','μοναχικότητα, προοπτική και στοχαστική αναζήτηση','noticing when reflection has become withdrawal','παρατήρηση του πότε ο στοχασμός γίνεται απόσυρση','✦'),
 ('Wheel of Fortune','Ο Τροχός της Τύχης','cycles, changing circumstances and adaptability','κύκλους, μεταβαλλόμενες συνθήκες και προσαρμοστικότητα','releasing the need to control every change','χαλάρωση της ανάγκης ελέγχου κάθε αλλαγής','☸'),
 ('Justice','Η Δικαιοσύνη','fairness, accountability and clear evaluation','δικαιοσύνη, ανάληψη ευθύνης και καθαρή αξιολόγηση','checking bias and accepting your part in a situation','έλεγχο της μεροληψίας και αναγνώριση της δικής σου συμμετοχής','⚖'),
 ('The Hanged Man','Ο Κρεμασμένος','a purposeful pause and a different perspective','συνειδητή παύση και διαφορετική οπτική','asking whether waiting is useful or simply avoidance','εξέταση του αν η αναμονή είναι χρήσιμη ή αποτελεί αποφυγή','◇'),
 ('Death','Ο Θάνατος','endings, transition and making room for renewal','ολοκλήρωση κύκλων, μετάβαση και χώρο για ανανέωση','recognizing resistance to an already-needed change','αναγνώριση της αντίστασης σε μια αλλαγή που ήδη χρειάζεται','❋'),
 ('Temperance','Η Εγκράτεια','balance, moderation and patient integration','ισορροπία, μέτρο και υπομονετική σύνθεση','restoring a sustainable rhythm where extremes have taken over','αποκατάσταση βιώσιμου ρυθμού όταν επικρατούν ακρότητες','≈'),
 ('The Devil','Ο Διάβολος','examining attachments, habits and perceived constraints','εξέταση προσκολλήσεων, συνηθειών και περιορισμών','recognizing where a habit can be loosened through deliberate choice','αναγνώριση του πώς μια συνήθεια μπορεί να αλλάξει με συνειδητή επιλογή','⛓'),
 ('The Tower','Ο Πύργος','questioning unstable assumptions and rebuilding honestly','αμφισβήτηση ασταθών παραδοχών και ειλικρινή αναδόμηση','examining a change you may be postponing','εξέταση μιας αλλαγής που ενδέχεται να αναβάλλεις','ϟ'),
 ('The Star','Το Άστρο','hope, renewal and a sense of direction','ελπίδα, ανανέωση και αίσθηση κατεύθυνσης','reconnecting with modest, achievable sources of encouragement','επανασύνδεση με μικρές, εφικτές πηγές ενθάρρυνσης','✶'),
 ('The Moon','Η Σελήνη','uncertainty, imagination and the need to verify impressions','αβεβαιότητα, φαντασία και ανάγκη ελέγχου των εντυπώσεων','separating a fear or assumption from what you actually know','διαχωρισμό φόβου ή υπόθεσης από όσα πραγματικά γνωρίζεις','☽'),
 ('The Sun','Ο Ήλιος','clarity, openness and simple enjoyment','διαύγεια, ανοιχτότητα και απλή χαρά','making room for enjoyment without demanding a perfect outcome','χώρο για χαρά χωρίς απαίτηση τέλειου αποτελέσματος','☀'),
 ('Judgement','Η Κρίση','honest review and responding to a renewed sense of purpose','ειλικρινή ανασκόπηση και απόκριση σε ανανεωμένο σκοπό','releasing harsh self-judgement while acknowledging what needs to change','αποδέσμευση από σκληρή αυτοκριτική με αναγνώριση όσων χρειάζονται αλλαγή','♬'),
 ('The World','Ο Κόσμος','completion, integration and recognizing a milestone','ολοκλήρωση, σύνθεση και αναγνώριση ενός ορόσημου','identifying the unfinished step before you can close a chapter','εντοπισμό του βήματος που απομένει για να κλείσει ένας κύκλος','◎'),
]
SUITS = {
 'wands': ('Wands','Ράβδων','initiative, creativity and purposeful action','πρωτοβουλία, δημιουργικότητα και συνειδητή δράση','ϟ'),
 'cups': ('Cups','Κυπέλλων','feelings, connection and emotional needs','συναισθήματα, σύνδεση και συναισθηματικές ανάγκες','♧'),
 'swords': ('Swords','Ξιφών','thought, communication and difficult choices','σκέψη, επικοινωνία και δύσκολες επιλογές','†'),
 'pentacles': ('Pentacles','Πεντάκτινων','practical effort, resources and daily foundations','πρακτική προσπάθεια, πόρους και καθημερινές βάσεις','✵'),
}
# rank EN/EL, upright theme EN/EL, reversed invitation EN/EL
RANKS = [
 ('Ace','Άσος','a fresh possibility','μια νέα δυνατότητα','checking readiness before a new start','έλεγχο ετοιμότητας πριν από ένα νέο ξεκίνημα'),
 ('Two','Δύο','balancing priorities and finding common ground','ισορροπία προτεραιοτήτων και κοινό έδαφος','clarifying competing priorities','αποσαφήνιση αντικρουόμενων προτεραιοτήτων'),
 ('Three','Τρία','growth through expression and collaboration','ανάπτυξη μέσα από έκφραση και συνεργασία','reviewing how you work with others','επανεξέταση του τρόπου συνεργασίας'),
 ('Four','Τέσσερα','stability, a pause and protecting a foundation','σταθερότητα, παύση και προστασία των βάσεων','noticing where stability has become stagnation','παρατήρηση του πότε η σταθερότητα γίνεται στασιμότητα'),
 ('Five','Πέντε','tension, change and learning through difficulty','ένταση, αλλαγή και μάθηση μέσα από δυσκολίες','considering how conflict can be de-escalated','εξέταση του τρόπου αποκλιμάκωσης μιας σύγκρουσης'),
 ('Six','Έξι','support, reciprocity and a transition toward balance','στήριξη, αμοιβαιότητα και μετάβαση προς ισορροπία','checking the balance between giving and receiving','έλεγχο της ισορροπίας προσφοράς και λήψης'),
 ('Seven','Επτά','assessment, patience and choosing where to invest effort','αξιολόγηση, υπομονή και επιλογή του πού αξίζει η προσπάθεια','reviewing an effort that may no longer serve its purpose','επανεξέταση μιας προσπάθειας που ίσως δεν εξυπηρετεί πλέον τον σκοπό της'),
 ('Eight','Οκτώ','focused movement, practice and sustained attention','εστιασμένη κίνηση, εξάσκηση και σταθερή προσοχή','adjusting pace or noticing a limiting pattern','προσαρμογή ρυθμού ή αναγνώριση περιοριστικού μοτίβου'),
 ('Nine','Εννέα','experience, personal boundaries and nearing a milestone','εμπειρία, προσωπικά όρια και προσέγγιση ενός ορόσημου','examining the cost of striving for an ideal','εξέταση του κόστους επιδίωξης ενός ιδανικού'),
 ('Ten','Δέκα','the culmination of a cycle and its responsibilities','κορύφωση ενός κύκλου και τις ευθύνες του','setting down a burden or redefining completion','αποφόρτιση ενός βάρους ή επαναπροσδιορισμό της ολοκλήρωσης'),
 ('Page','Ακόλουθος','curiosity, learning and a beginner’s approach','περιέργεια, μάθηση και διάθεση αρχαρίου','turning curiosity into a realistic next step','μετατροπή της περιέργειας σε ένα ρεαλιστικό επόμενο βήμα'),
 ('Knight','Ιππότης','movement, commitment and pursuit of an aim','κίνηση, δέσμευση και επιδίωξη ενός στόχου','checking impulsiveness or an unhelpful lack of movement','έλεγχο παρορμητικότητας ή αδράνειας'),
 ('Queen','Βασίλισσα','receptivity, discernment and mature care','δεκτικότητα, διάκριση και ώριμη φροντίδα','restoring boundaries while remaining receptive','αποκατάσταση ορίων με διατήρηση της δεκτικότητας'),
 ('King','Βασιλιάς','leadership, responsibility and mature direction','ηγεσία, ευθύνη και ώριμη κατεύθυνση','reviewing how authority and responsibility are expressed','επανεξέταση του τρόπου άσκησης εξουσίας και ευθύνης'),
]

# Card-specific upright themes; reversals retain the explicitly disclosed
# rank/suit reconsideration prompts rather than pretending there is one canon.
MINOR_THEMES = {
 'wands': [
  ('a creative spark and willingness to begin','δημιουργική σπίθα και διάθεση για ξεκίνημα'),
  ('planning, perspective and choosing a direction','σχεδιασμό, προοπτική και επιλογή κατεύθυνσης'),
  ('expansion, foresight and waiting for an effort to develop','διεύρυνση, προνοητικότητα και αναμονή της εξέλιξης μιας προσπάθειας'),
  ('celebration, belonging and a shared foundation','γιορτή, αίσθηση του ανήκειν και κοινές βάσεις'),
  ('competing aims and learning to handle disagreement','ανταγωνιστικές επιδιώξεις και διαχείριση διαφωνιών'),
  ('recognition and acknowledging progress without losing perspective','αναγνώριση και αποτίμηση προόδου με μέτρο'),
  ('standing your ground and choosing which challenges deserve energy','υπεράσπιση της θέσης σου και επιλογή των προκλήσεων που αξίζουν ενέργεια'),
  ('momentum, communication and events moving quickly','ορμή, επικοινωνία και γρήγορη εξέλιξη συνθηκών'),
  ('resilience, caution and protecting your remaining energy','ανθεκτικότητα, προσοχή και προστασία της ενέργειάς σου'),
  ('burdens, overcommitment and sharing responsibility','βάρη, υπερβολικές δεσμεύσεις και κατανομή ευθύνης'),
  ('enthusiasm, discovery and exploring a creative idea','ενθουσιασμό, ανακάλυψη και εξερεύνηση μιας δημιουργικής ιδέας'),
  ('adventure, bold action and managing impulsiveness','περιπέτεια, τόλμη και διαχείριση παρορμητικότητας'),
  ('warmth, confidence and independent creative expression','ζεστασιά, αυτοπεποίθηση και ανεξάρτητη δημιουργική έκφραση'),
  ('vision, leadership and directing creative energy responsibly','όραμα, ηγεσία και υπεύθυνη κατεύθυνση δημιουργικής ενέργειας'),
 ],
 'cups': [
  ('emotional openness and a new source of connection','συναισθηματικό άνοιγμα και νέα πηγή σύνδεσης'),
  ('reciprocity, partnership and mutual understanding','αμοιβαιότητα, συντροφικότητα και αλληλοκατανόηση'),
  ('friendship, shared joy and community','φιλία, κοινή χαρά και κοινότητα'),
  ('disengagement and noticing an overlooked possibility','αποστασιοποίηση και παρατήρηση μιας δυνατότητας που παραβλέπεις'),
  ('disappointment, grief and recognizing what remains','απογοήτευση, θλίψη και αναγνώριση όσων παραμένουν'),
  ('memory, familiarity and revisiting the past with perspective','μνήμη, οικειότητα και ανασκόπηση του παρελθόντος με προοπτική'),
  ('many possibilities and separating desire from realistic choice','πολλές δυνατότητες και διάκριση επιθυμίας από ρεαλιστική επιλογή'),
  ('leaving an unfulfilling pattern and seeking deeper meaning','απομάκρυνση από ένα μη ικανοποιητικό μοτίβο και αναζήτηση νοήματος'),
  ('contentment and appreciating what feels sufficient','ικανοποίηση και εκτίμηση όσων σου αρκούν'),
  ('shared belonging and the values behind an ideal of happiness','κοινή αίσθηση του ανήκειν και αξίες πίσω από ένα ιδανικό ευτυχίας'),
  ('sensitivity, imagination and an unexpected emotional insight','ευαισθησία, φαντασία και απρόσμενη συναισθηματική παρατήρηση'),
  ('idealism, expression of feeling and thoughtful invitations','ιδεαλισμό, έκφραση συναισθήματος και προσεκτικές προσκλήσεις'),
  ('empathy, inner awareness and emotional boundaries','ενσυναίσθηση, εσωτερική επίγνωση και συναισθηματικά όρια'),
  ('emotional steadiness and a compassionate response','συναισθηματική σταθερότητα και συμπονετική απόκριση'),
 ],
 'swords': [
  ('clarity, a fresh insight and honest communication','διαύγεια, νέα κατανόηση και ειλικρινή επικοινωνία'),
  ('a stalemate and the need to examine an avoided choice','αδιέξοδο και ανάγκη εξέτασης μιας επιλογής που αποφεύγεις'),
  ('hurt, disappointment and acknowledging a difficult truth','πληγή, απογοήτευση και αναγνώριση μιας δύσκολης αλήθειας'),
  ('rest, perspective and a deliberate pause','ανάπαυση, προοπτική και συνειδητή παύση'),
  ('conflict and examining the cost of needing to win','σύγκρουση και εξέταση του κόστους της ανάγκης για νίκη'),
  ('transition away from strain toward a different perspective','μετάβαση από ένταση προς διαφορετική οπτική'),
  ('strategy, discretion and questioning avoidance or hidden assumptions','στρατηγική, διακριτικότητα και εξέταση αποφυγής ή κρυφών παραδοχών'),
  ('perceived restriction and identifying the choices still available','αίσθηση περιορισμού και εντοπισμό των διαθέσιμων επιλογών'),
  ('worry, harsh self-talk and checking fears against facts','ανησυχία, σκληρό εσωτερικό διάλογο και έλεγχο φόβων απέναντι στα δεδομένα'),
  ('an exhausted pattern and recognizing when a chapter is over','εξαντλημένο μοτίβο και αναγνώριση του τέλους ενός κύκλου'),
  ('curiosity, questioning and checking information before repeating it','περιέργεια, ερωτήματα και έλεγχο πληροφοριών πριν τις επαναλάβεις'),
  ('decisive action and tempering haste with consideration','αποφασιστική δράση και εξισορρόπηση της βιασύνης με περίσκεψη'),
  ('discernment, independence and clear communication','διάκριση, ανεξαρτησία και σαφή επικοινωνία'),
  ('reason, principled judgement and responsible use of authority','λογική, κρίση με αρχές και υπεύθυνη άσκηση εξουσίας'),
 ],
 'pentacles': [
  ('a practical beginning and a tangible opportunity to develop','πρακτικό ξεκίνημα και χειροπιαστή δυνατότητα ανάπτυξης'),
  ('balancing commitments and adapting your daily rhythm','ισορροπία δεσμεύσεων και προσαρμογή καθημερινού ρυθμού'),
  ('craft, collaboration and learning from shared work','δεξιοτεχνία, συνεργασία και μάθηση μέσα από κοινό έργο'),
  ('security, holding on and examining the need for control','ασφάλεια, προσκόλληση και εξέταση της ανάγκης ελέγχου'),
  ('feeling excluded or short of support and noticing available help','αίσθηση αποκλεισμού ή έλλειψης στήριξης και αναγνώριση διαθέσιμης βοήθειας'),
  ('generosity, reciprocity and the balance of giving and receiving','γενναιοδωρία, αμοιβαιότητα και ισορροπία προσφοράς και λήψης'),
  ('patient effort, assessment and deciding what is worth cultivating','υπομονετική προσπάθεια, αξιολόγηση και επιλογή όσων αξίζει να καλλιεργείς'),
  ('practice, craftsmanship and steady improvement','εξάσκηση, δεξιοτεχνία και σταθερή βελτίωση'),
  ('self-reliance and appreciating the results of sustained effort','αυτοδυναμία και εκτίμηση των αποτελεσμάτων σταθερής προσπάθειας'),
  ('legacy, continuity and shared long-term foundations','κληρονομιά αξιών, συνέχεια και κοινές μακροπρόθεσμες βάσεις'),
  ('study, practical curiosity and a plan worth developing','μελέτη, πρακτική περιέργεια και σχέδιο που αξίζει ανάπτυξη'),
  ('reliability, routine and patient follow-through','αξιοπιστία, ρουτίνα και υπομονετική ολοκλήρωση'),
  ('practical care and creating a sustainable environment','πρακτική φροντίδα και δημιουργία βιώσιμου περιβάλλοντος'),
  ('stewardship, steadiness and responsible use of resources','υπεύθυνη διαχείριση, σταθερότητα και συνετή χρήση πόρων'),
 ],
}


def deck():
    cards=[]
    for index,row in enumerate(MAJORS):
        cards.append(dict(id=f'major-{index:02}',name_en=row[0],name_el=row[1],
                          upright_en=row[2],upright_el=row[3],reversed_en=row[4],
                          reversed_el=row[5],glyph=row[6],arcana='major'))
    for suit,(en,el,theme_en,theme_el,glyph) in SUITS.items():
        for index,rank in enumerate(RANKS,1):
            cards.append(dict(id=f'{suit}-{index:02}',name_en=f'{rank[0]} of {en}',
                              name_el=f'{rank[1]} των {el}',
                              upright_en=MINOR_THEMES[suit][index-1][0],
                              upright_el=MINOR_THEMES[suit][index-1][1],
                              reversed_en=f'{rank[4]}, in the realm of {theme_en}',
                              reversed_el=f'{rank[5]}, στο πεδίο που αφορά {theme_el}',
                              glyph=glyph,arcana='minor'))
    return cards


POSITIONS = {
 'en': {'one':['Focus for reflection'], 'three':['Past influences','Present focus','Next conscious step']},
 'el': {'one':['Θέμα για στοχασμό'], 'three':['Επιρροές του παρελθόντος','Εστίαση στο παρόν','Επόμενο συνειδητό βήμα']},
}


def draw_reading(question='',spread='three',lang='el',reversals=True,rng=None):
    if lang not in POSITIONS or spread not in ('one','three'):
        raise ValueError('Unsupported language or spread.')
    if not isinstance(question,str) or len(question)>500:
        raise ValueError('Question must be text up to 500 characters.')
    if type(reversals) is not bool:
        raise ValueError('Reversals must be true or false.')
    rng=rng or SystemRandom()
    selected=rng.sample(deck(),1 if spread=='one' else 3)
    cards=[]
    for index,card in enumerate(selected):
        reversed_card=reversals and bool(rng.getrandbits(1))
        theme=card[('reversed_' if reversed_card else 'upright_')+lang]
        if lang=='el':
            prefix=['Ως σύμβολο προηγούμενων εμπειριών, η κάρτα προσκαλεί σε ανασκόπηση με θέμα: ',
                    'Στη θέση του παρόντος, η κάρτα προσφέρει ένα θέμα για παρατήρηση: ',
                    'Ως επόμενο βήμα, η κάρτα προτείνει να εξετάσεις: '][index] if spread=='three' else 'Για τον σημερινό στοχασμό, εξέτασε: '
            prompt=['Τι από αυτή την εμπειρία αξίζει να κρατήσεις και τι να αφήσεις;',
                    'Πού αναγνωρίζεις αυτό το θέμα στην καθημερινότητά σου και πού δεν ταιριάζει;',
                    'Ποια μικρή, συγκεκριμένη πράξη βρίσκεται στον δικό σου έλεγχο;'][index] if spread=='three' else 'Ποια μικρή, συγκεκριμένη πράξη θα εξέφραζε αυτή την ιδέα;'
        else:
            prefix=['As a symbol of earlier experience, reflect on: ',
                    'In the present position, consider observing: ',
                    'As a next step, consider exploring: '][index] if spread=='three' else 'For this reflection, consider: '
            prompt=['What is worth carrying forward, and what could you leave behind?',
                    'Where does this theme fit your experience, and where does it not?',
                    'What small, concrete action is within your control?'][index] if spread=='three' else 'What small, concrete action could express this idea?'
        cards.append(dict(id=card['id'],name=card['name_'+lang],arcana=card['arcana'],
                          glyph=card['glyph'],orientation='reversed' if reversed_card else 'upright',
                          position=index,position_label=POSITIONS[lang][spread][index],
                          theme=theme,interpretation=prefix+theme+'.',reflection=prompt))
    if lang=='el':
        overall='Διάβασε τις κάρτες ως ερωτήματα, όχι ως περιγραφή του πεπρωμένου σου. '
        overall+=('Η διαδρομή συνδέει όσα ανασκοπείς, όσα παρατηρείς σήμερα και μια επιλογή για το επόμενο βήμα.' if spread=='three' else 'Διάλεξε το μέρος του συμβόλου που σου είναι χρήσιμο και άφησε ό,τι δεν ταιριάζει.')
        if spread=='three':
            overall+=' Ανασκόπησε το θέμα «'+cards[0]['theme']+'», παρατήρησε το «'+cards[1]['theme']+'» και διάλεξε αν το «'+cards[2]['theme']+'» προσφέρει μια χρήσιμη κατεύθυνση. Δεν χρειάζεται να ταιριάζουν όλα στην εμπειρία σου.'
        method='Τυχαίο τράβηγμα από 78 κάρτες. Πρωτότυπες συντακτικές περιλήψεις κοινών συμβολισμών· οι μικρές αρκάνες έχουν ειδικά όρθια θέματα και ανάστροφες προτροπές από τον βαθμό και τη σειρά τους. Η ανάστροφη θέση διαβάζεται ως πρόσκληση επανεξέτασης. Δεν χρησιμοποιείται AI ή σύνδεση με αστρολογικούς υπολογισμούς.'
        note='Για ψυχαγωγία και προσωπικό στοχασμό. Οι κάρτες δεν προβλέπουν γεγονότα, ούτε απαντούν σε ιατρικά, νομικά ή οικονομικά ζητήματα. Κάρτες όπως Θάνατος και Δικαιοσύνη είναι σύμβολα, όχι κυριολεκτικές προβλέψεις.'
    else:
        overall='Read the cards as questions, rather than a description of your fate. '
        overall+=('The sequence connects what you review, what you notice now and a choice for your next step.' if spread=='three' else 'Keep the part of the symbol that is useful and leave what does not fit.')
        if spread=='three':
            overall+=' Review the theme of '+cards[0]['theme']+'; observe '+cards[1]['theme']+'; then consider whether '+cards[2]['theme']+' offers a useful direction. Not every theme needs to fit your experience.'
        method='Random draw from 78 cards. Original editorial summaries of common symbolism; minor cards have card-specific upright themes and rank/suit reversal prompts. Reversals invite reconsideration. No AI or connection to astronomical calculations is used.'
        note='For entertainment and self-reflection. Cards do not predict events or answer medical, legal or financial questions. Cards such as Death and Justice are symbols, not literal predictions.'
    return dict(reading_id=str(uuid4()),created_at=datetime.now(timezone.utc).isoformat(),
                lang=lang,spread=spread,question=question.strip(),cards=cards,
                overall=overall,method=method,disclaimer=note)
