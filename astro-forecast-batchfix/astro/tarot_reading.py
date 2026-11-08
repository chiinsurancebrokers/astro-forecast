"""Position-, topic- and question-aware wording for the tarot reading.

Original editorial text. A reading is composed from: where the card sits in the
spread (past / present / future tendency / answer), the topic the person chose,
the suit (or Major Arcana) lens for that topic, and the card's own theme. The
synthesis is computed from the actual draw (majors, reversals, dominant suit).
Nothing here predicts events or gives yes/no answers; no AI is involved.
"""

TOPICS = ('general', 'love', 'work', 'money', 'self')

TOPIC_LABEL = {
 'en': {'general': 'General', 'love': 'Love & relationships', 'work': 'Work & career',
        'money': 'Money', 'self': 'Personal growth'},
 'el': {'general': 'Γενικά', 'love': 'Αισθηματικά', 'work': 'Εργασία',
        'money': 'Οικονομικά', 'self': 'Προσωπική εξέλιξη'},
}
# Phrase used after a preposition (EL: accusative).
TOPIC_PHRASE = {
 'en': {'general': 'this situation', 'love': 'your love life', 'work': 'your work life',
        'money': 'your finances', 'self': 'your personal growth'},
 'el': {'general': 'την κατάστασή σου', 'love': 'τα αισθηματικά σου',
        'work': 'την επαγγελματική σου ζωή', 'money': 'τα οικονομικά σου',
        'self': 'την προσωπική σου εξέλιξη'},
}

# Position kinds per spread. 'three' keeps its original labels.
KINDS = {'one': ['focus'], 'three': ['past', 'present', 'answer'],
         'four': ['past', 'present', 'future', 'answer']}

ORIENT = {'en': {'upright': 'upright', 'reversed': 'reversed'},
          'el': {'upright': 'όρθια', 'reversed': 'ανάστροφη'}}
# One complete sentence per card: what it points to (upright) or asks to be reconsidered (reversed).
MEANING = {
 'en': {'up': '{name} points to {t}.',
        'rev_major': '{name}, reversed, asks for a closer look: {t}.',
        'rev_minor': '{name}, reversed, asks you to reconsider its theme: {t}.'},
 'el': {'up': '{name}: δείχνει {t}.',
        'rev_major': '{name} (ανάστροφη): ζητά {t}.',
        'rev_minor': '{name} (ανάστροφη): ζητά επανεξέταση του θέματος: {t}.'},
}
# What the position adds to the card's meaning.
POSITION_SENTENCE = {
 'en': {'focus': 'This is the theme to reflect on.',
        'past': 'This is something that has shaped you so far.',
        'present': 'This is what asks for your attention right now.',
        'future': 'If you continue as you are, this is the tendency that shows — not a fixed outcome.',
        'answer': 'This is the stance the card suggests for your question.'},
 'el': {'focus': 'Αυτό είναι το θέμα για στοχασμό.',
        'past': 'Αυτό είναι κάτι που σε έχει διαμορφώσει μέχρι τώρα.',
        'present': 'Αυτό ζητά την προσοχή σου αυτή τη στιγμή.',
        'future': 'Αν συνεχίσεις όπως τώρα, αυτή είναι η τάση που διαφαίνεται — όχι δεδομένο αποτέλεσμα.',
        'answer': 'Αυτή είναι η στάση που προτείνει η κάρτα για το ερώτημά σου.'},
}

SUIT_LENS = {
 'en': {
  'wands': {'general': 'Wands bring energy, initiative and what draws you to begin into focus.',
            'love': 'In love, Wands speak of attraction, spontaneity and how much initiative each person is taking.',
            'work': 'At work, Wands highlight drive, new projects and where your energy is best spent.',
            'money': 'With money, Wands suggest ventures and ideas, and ask whether enthusiasm is matched by a plan.',
            'self': 'For personal growth, Wands point to what energizes you and the courage to express it.'},
  'cups': {'general': 'Cups bring feelings, relationships and emotional needs into focus.',
           'love': 'In love, Cups speak directly of feeling, closeness and how openly it is shared.',
           'work': 'At work, Cups point to relationships with colleagues and whether the work feels meaningful.',
           'money': 'With money, Cups ask what security and “enough” actually feel like for you.',
           'self': 'For personal growth, Cups invite you to listen to what you feel and need.'},
  'swords': {'general': 'Swords bring thinking, honest communication and decisions into focus.',
             'love': 'In love, Swords point to what is said and left unsaid, and to a conversation or decision that clarity would help.',
             'work': 'At work, Swords point to communication, analysis and a decision that needs clear criteria.',
             'money': 'With money, Swords ask for facts and figures before conclusions, and for clear-headed decisions.',
             'self': 'For personal growth, Swords point to your inner dialogue and the beliefs worth checking.'},
  'pentacles': {'general': 'Pentacles bring practical matters, daily routines and resources into focus.',
                'love': 'In love, Pentacles point to reliability, shared routines and the practical ways care is shown.',
                'work': 'At work, Pentacles point to steady effort, skills and building something that lasts.',
                'money': 'With money, Pentacles speak most directly: budget, resources and patient, realistic planning.',
                'self': 'For personal growth, Pentacles point to habits, daily routines and steady practice.'},
 },
 'el': {
  'wands': {'general': 'Οι Ράβδοι στρέφουν την προσοχή στην ενέργεια, την πρωτοβουλία και σε ό,τι σε τραβά να ξεκινήσεις.',
            'love': 'Στα αισθηματικά, οι Ράβδοι μιλούν για έλξη, αυθορμητισμό και για το πόση πρωτοβουλία παίρνει ο καθένας.',
            'work': 'Στη δουλειά, οι Ράβδοι τονίζουν κίνητρο, νέα έργα και το πού αξίζει να επενδύσεις την ενέργειά σου.',
            'money': 'Στα οικονομικά, οι Ράβδοι παραπέμπουν σε πρωτοβουλίες και ιδέες, και ρωτούν αν ο ενθουσιασμός συνοδεύεται από σχέδιο.',
            'self': 'Στην προσωπική εξέλιξη, οι Ράβδοι δείχνουν τι σε ενεργοποιεί και το θάρρος να το εκφράσεις.'},
  'cups': {'general': 'Τα Κύπελλα φέρνουν στο προσκήνιο συναισθήματα, σχέσεις και συναισθηματικές ανάγκες.',
           'love': 'Στα αισθηματικά, τα Κύπελλα μιλούν άμεσα για συναίσθημα, οικειότητα και το πόσο ανοιχτά μοιράζεται.',
           'work': 'Στη δουλειά, τα Κύπελλα δείχνουν τις σχέσεις με τους συναδέλφους και το αν η δουλειά σού φαίνεται ουσιαστική.',
           'money': 'Στα οικονομικά, τα Κύπελλα ρωτούν τι σημαίνει για σένα ασφάλεια και «αρκετά».',
           'self': 'Στην προσωπική εξέλιξη, τα Κύπελλα σε καλούν να ακούσεις τι νιώθεις και τι χρειάζεσαι.'},
  'swords': {'general': 'Τα Ξίφη φέρνουν στο προσκήνιο τη σκέψη, την ειλικρινή επικοινωνία και τις αποφάσεις.',
             'love': 'Στα αισθηματικά, τα Ξίφη δείχνουν όσα λέγονται και όσα σιωπούνται, και μια συζήτηση ή απόφαση που θα βοηθούσε να γίνει με καθαρότητα.',
             'work': 'Στη δουλειά, τα Ξίφη δείχνουν επικοινωνία, ανάλυση και μια απόφαση που χρειάζεται καθαρά κριτήρια.',
             'money': 'Στα οικονομικά, τα Ξίφη ζητούν στοιχεία και νούμερα πριν από συμπεράσματα, και ψύχραιμες αποφάσεις.',
             'self': 'Στην προσωπική εξέλιξη, τα Ξίφη δείχνουν τον εσωτερικό σου διάλογο και τις πεποιθήσεις που αξίζει να ελέγξεις.'},
  'pentacles': {'general': 'Τα Πεντάκτινα φέρνουν στο προσκήνιο πρακτικά ζητήματα, καθημερινότητα και πόρους.',
                'love': 'Στα αισθηματικά, τα Πεντάκτινα δείχνουν αξιοπιστία, κοινή καθημερινότητα και τους πρακτικούς τρόπους που εκφράζεται η φροντίδα.',
                'work': 'Στη δουλειά, τα Πεντάκτινα δείχνουν σταθερή προσπάθεια, δεξιότητες και το χτίσιμο κάτι διαρκούς.',
                'money': 'Στα οικονομικά, τα Πεντάκτινα μιλούν πιο άμεσα: προϋπολογισμό, πόρους και υπομονετικό, ρεαλιστικό σχεδιασμό.',
                'self': 'Στην προσωπική εξέλιξη, τα Πεντάκτινα δείχνουν συνήθειες, καθημερινές ρουτίνες και σταθερή εξάσκηση.'},
 },
}
MAJOR_LENS = {
 'en': {'general': 'As a Major Arcana card, it marks a theme that carries weight beyond the everyday.',
        'love': 'As a Major Arcana card in matters of the heart, it suggests this theme shapes the relationship more deeply than daily events do.',
        'work': 'As a Major Arcana card about work, it points to a theme about your direction, not only today’s tasks.',
        'money': 'As a Major Arcana card about money, it points to your values and attitudes toward resources, beyond a single transaction.',
        'self': 'As a Major Arcana card about yourself, it marks a meaningful chapter in how you see yourself and grow.'},
 'el': {'general': 'Ως Μεγάλη Αρκάνα, σηματοδοτεί ένα θέμα με βαρύτητα πέρα από την καθημερινότητα.',
        'love': 'Ως Μεγάλη Αρκάνα στα αισθηματικά, υποδηλώνει ότι το θέμα επηρεάζει τη σχέση βαθύτερα από τα καθημερινά γεγονότα.',
        'work': 'Ως Μεγάλη Αρκάνα για τη δουλειά, δείχνει ένα θέμα που αφορά την κατεύθυνσή σου και όχι μόνο τις σημερινές εργασίες.',
        'money': 'Ως Μεγάλη Αρκάνα για τα οικονομικά, δείχνει τις αξίες και τη στάση σου απέναντι στους πόρους, πέρα από μία μεμονωμένη συναλλαγή.',
        'self': 'Ως Μεγάλη Αρκάνα για τον εαυτό σου, σηματοδοτεί ένα ουσιαστικό κεφάλαιο στον τρόπο που βλέπεις τον εαυτό σου και εξελίσσεσαι.'},
}

REFLECTION = {
 'en': {'focus': 'What small, concrete action around {t} could express this idea?',
        'past': 'What from your experience of {t} is worth carrying forward, and what could you leave behind?',
        'present': 'Where do you recognize this theme in {t} today, and where does it not fit?',
        'future': 'If you continue as you are, what could develop around {t} — and what would you like to influence?',
        'answer': 'What small, concrete step regarding {t} is within your control and would express this stance?'},
 'el': {'focus': 'Ποια μικρή, συγκεκριμένη πράξη σχετικά με {t} θα εξέφραζε αυτή την ιδέα;',
        'past': 'Τι από όσα έζησες σχετικά με {t} αξίζει να κρατήσεις και τι να αφήσεις;',
        'present': 'Πού αναγνωρίζεις αυτό το θέμα σε σχέση με {t} σήμερα και πού δεν ταιριάζει;',
        'future': 'Αν συνεχίσεις όπως τώρα, τι θα μπορούσε να αναπτυχθεί σχετικά με {t} — και τι θέλεις να επηρεάσεις;',
        'answer': 'Ποιο μικρό, συγκεκριμένο βήμα σχετικά με {t} βρίσκεται στο χέρι σου και θα εξέφραζε αυτή τη στάση;'},
}

# Meaning of each position, shown to the reader as the method guide.
KIND_MEANING = {
 'en': {'focus': 'one theme to reflect on, nothing more.',
        'past': 'what has shaped the matter and what you carry from it.',
        'present': 'how the matter shows up now and what needs attention.',
        'future': 'a tendency that shows if things continue as they are — a possibility, never a certain event.',
        'answer': 'the stance or direction the card suggests for your question. It is not a yes/no verdict.'},
 'el': {'focus': 'ένα θέμα για στοχασμό, τίποτα παραπάνω.',
        'past': 'τι έχει διαμορφώσει το θέμα και τι κουβαλάς από εκεί.',
        'present': 'πώς εμφανίζεται το θέμα τώρα και τι χρειάζεται προσοχή.',
        'future': 'μια τάση που διαφαίνεται αν τα πράγματα συνεχίσουν όπως τώρα — πιθανότητα, όχι βέβαιο γεγονός.',
        'answer': 'η στάση ή η κατεύθυνση που προτείνει η κάρτα για το ερώτημά σου. Δεν είναι απάντηση ναι/όχι.'},
}

QUESTION = {'en': 'Your question: “{q}”.', 'el': 'Το ερώτημά σου: «{q}».'}
TOPIC_ONLY = {'en': 'Theme: {t}.', 'el': 'Θέμα: «{t}».'}
MOVEMENT = {
 'en': {'smooth': 'The journey is steady: the themes are expressed openly from start to finish.',
        'opening': 'Something that has been blocked or unclear so far looks set to open up toward the end.',
        'closing': 'What flows today may need a second look later, so the step you choose deserves care.',
        'mixed': 'The journey has ups and downs: some themes are open, others ask for a second look.'},
 'el': {'smooth': 'Η διαδρομή είναι ομαλή: τα θέματα εκφράζονται ανοιχτά από την αρχή ως το τέλος.',
        'opening': 'Κάτι που ως τώρα ήταν μπλοκαρισμένο ή ασαφές φαίνεται να ανοίγει προς το τέλος.',
        'closing': 'Ό,τι ρέει σήμερα ίσως χρειαστεί δεύτερη ματιά αργότερα· γι’ αυτό το βήμα που θα επιλέξεις αξίζει προσοχή.',
        'mixed': 'Η διαδρομή έχει εναλλαγές: κάποια θέματα είναι ανοιχτά και άλλα ζητούν δεύτερη ματιά.'},
}
ANSWER_INTRO = {'en': 'The answer card does not say yes or no; it shows a stance.',
                'el': 'Η κάρτα-απάντηση δεν λέει ναι ή όχι· δείχνει μια στάση.'}
PRACTICE = {'en': 'In practice: ', 'el': 'Στην πράξη: '}
FUTURE_NOTE = {
 'en': 'A tendency is not a fixed outcome — your choices can change it.',
 'el': 'Μια τάση δεν είναι δεδομένο αποτέλεσμα — οι επιλογές σου μπορούν να την αλλάξουν.'}

METHOD = {
 'en': 'Random draw from 78 cards, without repeats. Each card is read by its position in the spread, the topic you chose, its suit (or Major Arcana status) and whether it is upright or reversed. The overall reading is built from your actual draw: the keyword of each card in its position and how open or reversed the cards are from start to end. All text is original editorial writing; no AI is used, nothing is predicted and your question is not stored.',
 'el': 'Τυχαίο τράβηγμα από 78 κάρτες, χωρίς επαναλήψεις. Κάθε κάρτα διαβάζεται με βάση τη θέση της στη διάταξη, το θέμα που επέλεξες, το σετ της (ή το ότι είναι Μεγάλη Αρκάνα) και το αν είναι όρθια ή ανάστροφη. Η συνολική ανάγνωση χτίζεται από το δικό σου τράβηγμα: τη λέξη-κλειδί κάθε κάρτας στη θέση της και το πόσο ανοιχτές ή ανάστροφες είναι οι κάρτες από την αρχή ως το τέλος. Όλα τα κείμενα είναι πρωτότυπα συντακτικά· δεν χρησιμοποιείται AI, δεν προβλέπεται τίποτα και η ερώτησή σου δεν αποθηκεύεται.',
}


def meaning(card, orientation, lang):
    """One complete sentence about the card in its orientation."""
    name = card['name_' + lang]
    if orientation == 'upright':
        return MEANING[lang]['up'].format(name=name, t=card['upright_' + lang])
    if card['arcana'] == 'major':
        return MEANING[lang]['rev_major'].format(name=name, t=card['reversed_' + lang])
    return MEANING[lang]['rev_minor'].format(name=name, t=card['upright_' + lang])


def interpret(card, kind, topic, lang, orientation, theme=None, major_lens=True):
    """Return (interpretation, reflection, meaning) for one drawn card."""
    t = TOPIC_PHRASE[lang][topic]
    text = meaning(card, orientation, lang)
    parts = [text, POSITION_SENTENCE[lang][kind]]
    if card['arcana'] == 'minor':
        parts.append(SUIT_LENS[lang][card['id'].split('-')[0]][topic])
    elif major_lens:  # the generic Major Arcana sentence is said once per reading
        parts.append(MAJOR_LENS[lang][topic])
    return ' '.join(parts), REFLECTION[lang][kind].format(t=t), text


def synthesis(cards, kinds, topic, question, lang):
    """Short plain-language wrap-up computed from the actual draw."""
    q = ' '.join(question.split())
    if len(q) > 140:
        q = q[:137].rstrip() + '…'
    out = [QUESTION[lang].format(q=q) if q else TOPIC_ONLY[lang].format(t=TOPIC_LABEL[lang][topic])]
    if len(cards) > 1:
        half = len(cards) // 2
        early = sum(c['orientation'] == 'reversed' for c in cards[:half])
        late = sum(c['orientation'] == 'reversed' for c in cards[half:])
        key = ('smooth' if early + late == 0 else 'opening' if early > late
               else 'closing' if late > early else 'mixed')
        out.append(MOVEMENT[lang][key])
    last = cards[-1]
    if 'answer' in kinds:
        out.append(ANSWER_INTRO[lang] + ' ' + last['meaning'])
    if 'future' in kinds:
        out.append(FUTURE_NOTE[lang])
    return ' '.join(out)


def guide(labels, kinds, lang):
    return [dict(label=label, meaning=KIND_MEANING[lang][kind]) for label, kind in zip(labels, kinds)]
