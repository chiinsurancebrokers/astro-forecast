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

FRAME = {
 'en': {'focus': 'A theme to reflect on around {t}:',
        'past': 'What has shaped {t}:',
        'present': 'Where you stand with {t}:',
        'future': 'The direction that shows for {t} if things continue as they are:',
        'answer': 'The stance the card suggests for {t}:'},
 'el': {'focus': 'Ένα θέμα για στοχασμό γύρω από {t}:',
        'past': 'Τι έχει διαμορφώσει {t}:',
        'present': 'Πού βρίσκεσαι σε σχέση με {t}:',
        'future': 'Η κατεύθυνση που διαφαίνεται για {t}, αν τα πράγματα συνεχίσουν όπως τώρα:',
        'answer': 'Η στάση που προτείνει η κάρτα για {t}:'},
}
ORIENT = {'en': {'upright': 'upright', 'reversed': 'reversed'},
          'el': {'upright': 'όρθια', 'reversed': 'ανάστροφη'}}
CARD_LINE = {'en': '{name} — theme: {theme}.', 'el': '{name} — θέμα: {theme}.'}
ORIENT_NOTE = {
 'en': {'upright': 'Upright, the theme is expressed openly and can be worked with directly.',
        'reversed': 'Reversed, the theme asks to be reconsidered, or is only partly expressed so far.'},
 'el': {'upright': 'Όρθια, το θέμα εκφράζεται ανοιχτά και μπορείς να δουλέψεις μαζί του άμεσα.',
        'reversed': 'Ανάστροφη, το θέμα ζητά επανεξέταση ή εκφράζεται μόνο εν μέρει μέχρι τώρα.'},
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

SUIT_DOMINANT = {
 'en': {'wands': 'Wands dominate: this is largely a matter of energy, action and initiative.',
        'cups': 'Cups dominate: feelings and relationships are at the heart of this.',
        'swords': 'Swords dominate: thinking, communication and decisions are central here.',
        'pentacles': 'Pentacles dominate: practical matters, routines and resources are central here.'},
 'el': {'wands': 'Κυριαρχούν οι Ράβδοι: το θέμα αφορά κυρίως ενέργεια, δράση και πρωτοβουλία.',
        'cups': 'Κυριαρχούν τα Κύπελλα: συναισθήματα και σχέσεις βρίσκονται στον πυρήνα.',
        'swords': 'Κυριαρχούν τα Ξίφη: σκέψη, επικοινωνία και αποφάσεις είναι κεντρικά.',
        'pentacles': 'Κυριαρχούν τα Πεντάκτινα: πρακτικά ζητήματα, ρουτίνες και πόροι είναι κεντρικά.'},
}
MAJORS_NOTE = {
 'en': {'many': 'With {n} Major Arcana cards, this matter seems to carry real weight and a wider meaning for you.',
        'some': 'One or two Major Arcana cards mark a meaningful thread among otherwise everyday matters.',
        'none': 'With no Major Arcana cards, this reads as a matter of everyday, practical choices rather than a turning point.'},
 'el': {'many': 'Με {n} Μεγάλες Αρκάνες, το θέμα φαίνεται να έχει πραγματική βαρύτητα και ευρύτερο νόημα για σένα.',
        'some': 'Μία ή δύο Μεγάλες Αρκάνες σημαδεύουν μια ουσιαστική κλωστή μέσα σε κατά τα άλλα καθημερινά ζητήματα.',
        'none': 'Χωρίς Μεγάλες Αρκάνες, η ανάγνωση δείχνει καθημερινές, πρακτικές επιλογές και όχι σημείο καμπής.'},
}
REVERSED_NOTE = {
 'en': {'none': 'All cards are upright: the themes are expressed openly and can be worked with directly.',
        'most': 'Most cards are reversed: the spread leans toward reviewing and reconsidering before acting.',
        'mixed': '{n} of {total} cards are reversed: some themes flow openly while others ask for a second look.'},
 'el': {'none': 'Όλες οι κάρτες είναι όρθιες: τα θέματα εκφράζονται ανοιχτά και μπορείς να δουλέψεις μαζί τους άμεσα.',
        'most': 'Οι περισσότερες κάρτες είναι ανάστροφες: η διάταξη γέρνει προς την επανεξέταση πριν από τη δράση.',
        'mixed': '{n} από {total} κάρτες είναι ανάστροφες: κάποια θέματα ρέουν ανοιχτά και άλλα ζητούν δεύτερη ματιά.'},
}
ARC = {'en': 'The sequence reads: ', 'el': 'Η αφήγηση διαβάζεται έτσι: '}
QUESTION = {'en': 'Your question: “{q}”.', 'el': 'Το ερώτημά σου: «{q}».'}
TOPIC_ONLY = {'en': 'Theme: {t}.', 'el': 'Θέμα: «{t}».'}
FUTURE_NOTE = {
 'en': 'The future position is read as a tendency if you continue as you are, not as a fixed outcome — your choices can change it.',
 'el': 'Η θέση του μέλλοντος διαβάζεται ως τάση αν συνεχίσεις όπως τώρα, όχι ως δεδομένο αποτέλεσμα — οι επιλογές σου μπορούν να την αλλάξουν.'}
ANSWER_NOTE = {
 'en': 'The answer card is {name} ({o}). It does not say yes or no; it suggests a stance to take: {theme}.',
 'el': 'Η κάρτα-απάντηση είναι {name} ({o}). Δεν λέει ναι ή όχι· προτείνει μια στάση: {theme}.'}
CLOSE = {
 'en': 'Read the cards as questions, not as a description of your fate. Keep what fits and leave the rest.',
 'el': 'Διάβασε τις κάρτες ως ερωτήματα, όχι ως περιγραφή του πεπρωμένου σου. Κράτα ό,τι ταιριάζει και άφησε τα υπόλοιπα.'}

METHOD = {
 'en': 'Random draw from 78 cards, without repeats. Each card is read by its position in the spread, the topic you chose, its suit (or Major Arcana status) and whether it is upright or reversed. The overall reading is computed from your actual draw: number of Major Arcana, reversals and dominant suit. All text is original editorial writing; no AI is used, nothing is predicted and your question is not stored.',
 'el': 'Τυχαίο τράβηγμα από 78 κάρτες, χωρίς επαναλήψεις. Κάθε κάρτα διαβάζεται με βάση τη θέση της στη διάταξη, το θέμα που επέλεξες, το σετ της (ή το ότι είναι Μεγάλη Αρκάνα) και το αν είναι όρθια ή ανάστροφη. Η συνολική ανάγνωση υπολογίζεται από το δικό σου τράβηγμα: πλήθος Μεγάλων Αρκάνων, ανάστροφες και κυρίαρχο σετ. Όλα τα κείμενα είναι πρωτότυπα συντακτικά· δεν χρησιμοποιείται AI, δεν προβλέπεται τίποτα και η ερώτησή σου δεν αποθηκεύεται.',
}


def interpret(card, kind, topic, lang, orientation, theme, major_lens=True):
    """Return (interpretation, reflection) for one drawn card."""
    t = TOPIC_PHRASE[lang][topic]
    o = ORIENT[lang][orientation]
    if card['arcana'] == 'major':
        lens = MAJOR_LENS[lang][topic]
    else:
        lens = SUIT_LENS[lang][card['id'].split('-')[0]][topic]
    parts = [FRAME[lang][kind].format(t=t),
             CARD_LINE[lang].format(name=card['name_' + lang], o=o, theme=theme)]
    # The Major Arcana sentence is generic; say it once per reading, not per card.
    if card['arcana'] == 'minor' or major_lens:
        parts.append(lens)
    # An upright note is filler; only a reversal changes how the card is read.
    if orientation == 'reversed':
        parts.append(ORIENT_NOTE[lang][orientation])
    return ' '.join(parts), REFLECTION[lang][kind].format(t=t)


def synthesis(cards, kinds, topic, question, lang):
    """Compute the overall reading from the actual draw."""
    out = []
    q = ' '.join(question.split())
    if len(q) > 140:
        q = q[:137].rstrip() + '…'
    out.append(QUESTION[lang].format(q=q) if q else TOPIC_ONLY[lang].format(t=TOPIC_LABEL[lang][topic]))
    if len(cards) > 1:
        arc = ' → '.join(f"{c['position_label']}: {c['name']} ({ORIENT[lang][c['orientation']]})" for c in cards)
        out.append(ARC[lang] + arc + '.')
        majors = sum(c['arcana'] == 'major' for c in cards)
        key = 'many' if majors >= 3 else 'some' if majors else 'none'
        out.append(MAJORS_NOTE[lang][key].format(n=majors))
        rev = sum(c['orientation'] == 'reversed' for c in cards)
        key = 'none' if rev == 0 else 'most' if rev * 2 > len(cards) else 'mixed'
        out.append(REVERSED_NOTE[lang][key].format(n=rev, total=len(cards)))
        suits = [c['id'].split('-')[0] for c in cards if c['arcana'] == 'minor']
        ranked = sorted(((suits.count(x), x) for x in set(suits)), reverse=True)
        # Dominant only if one suit leads outright with at least two cards (no ties).
        if ranked and ranked[0][0] >= 2 and (len(ranked) == 1 or ranked[0][0] > ranked[1][0]):
            out.append(SUIT_DOMINANT[lang][ranked[0][1]])
    if 'future' in kinds:
        out.append(FUTURE_NOTE[lang])
    if 'answer' in kinds:
        c = cards[kinds.index('answer')]
        out.append(ANSWER_NOTE[lang].format(name=c['name'], o=ORIENT[lang][c['orientation']], theme=c['theme']))
    out.append(CLOSE[lang])
    out[0]=out[0].rstrip()
    return ' '.join(out)


def guide(labels, kinds, lang):
    return [dict(label=label, meaning=KIND_MEANING[lang][kind]) for label, kind in zip(labels, kinds)]
