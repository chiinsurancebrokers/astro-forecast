"""Editorial wording for the daily horoscope (original text, el/en).

Reflective, non-predictive phrasing keyed to calculated sky values: the solar
house the Moon falls in, the Moon's sign and phase. Written for this app.
"""

# index = solar house - 1; (general EN, general EL, love EN, love EL, work EN, work EL)
HOUSE_TEXT = [
    ("Attention turns to you: how you feel in your own skin, how you come across and what you want for yourself. It is a good day to notice your own needs before answering other people's.",
     "Η προσοχή στρέφεται σε εσένα: πώς νιώθεις μέσα σου, πώς εμφανίζεσαι και τι θέλεις για τον εαυτό σου. Είναι μια καλή μέρα για να προσέξεις τις δικές σου ανάγκες πριν απαντήσεις στις ανάγκες των άλλων.",
     "In close relationships you may feel more direct than usual. Saying what you honestly feel, kindly and simply, can matter more than finding the perfect words.",
     "Στις στενές σχέσεις μπορεί να νιώθεις πιο άμεσος/η από συνήθως. Το να πεις ειλικρινά και ήρεμα τι νιώθεις μπορεί να μετράει περισσότερο από τις τέλειες λέξεις.",
     "At work, your own initiative and presence stand out. Choose one thing you can start or present yourself, rather than waiting to be asked.",
     "Στη δουλειά ξεχωρίζει η δική σου πρωτοβουλία και παρουσία. Διάλεξε ένα πράγμα που μπορείς να ξεκινήσεις ή να παρουσιάσεις μόνος/η σου, αντί να περιμένεις να σου ζητηθεί."),
    ("Themes of security and what you value come forward. Taking stock of what you already have, in money, skills and time, can steady you more than chasing something new.",
     "Έρχονται στην επιφάνεια θέματα ασφάλειας και αξιών. Μια καταγραφή όσων ήδη έχεις, σε χρήματα, δεξιότητες και χρόνο, μπορεί να σε σταθεροποιήσει περισσότερο από το κυνήγι κάτι καινούριου.",
     "Feelings may be tied to comfort and reliability today. Small, steady gestures of care can say more than big declarations.",
     "Τα συναισθήματα συνδέονται σήμερα με την άνεση και την αξιοπιστία. Μικρές, σταθερές χειρονομίες φροντίδας μπορεί να λένε περισσότερα από μεγάλες δηλώσεις.",
     "A practical day for budgets, prices and what your effort is worth. Double-check figures and avoid deciding about money purely from mood.",
     "Μια πρακτική μέρα για προϋπολογισμούς, τιμές και την αξία της προσπάθειάς σου. Έλεγξε ξανά τα νούμερα και απόφυγε να αποφασίσεις για χρήματα μόνο από διάθεση."),
    ("Your mind is busy and curious. Conversations, messages, short trips and small errands may take up more room than usual, so keep a simple list to stay clear.",
     "Το μυαλό σου είναι ζωηρό και περίεργο. Συζητήσεις, μηνύματα, μικρές διαδρομές και δουλειές μπορεί να πάρουν περισσότερο χώρο από το συνηθισμένο· κράτησε μια απλή λίστα για να μένεις καθαρός/ή.",
     "Talking things through helps feelings settle. Listen as much as you speak, and ask a real question about how the other person is doing.",
     "Η συζήτηση βοηθά τα συναισθήματα να καθίσουν. Άκου όσο μιλάς και κάνε μια ουσιαστική ερώτηση για το πώς είναι ο άλλος.",
     "Good for emails, calls, writing and learning something quick. Be precise with wording, since small misunderstandings are easy today.",
     "Καλή μέρα για emails, τηλέφωνα, γράψιμο και γρήγορη μάθηση. Να είσαι ακριβής στη διατύπωση, γιατί οι μικρές παρεξηγήσεις γίνονται εύκολα."),
    ("Home, family and your inner base ask for attention. Your space and your routines may matter more than outside demands, and a little tidying can lift your mood.",
     "Το σπίτι, η οικογένεια και η εσωτερική σου βάση ζητούν προσοχή. Ο χώρος και οι ρουτίνες σου μπορεί να μετράνε περισσότερο από τις εξωτερικές απαιτήσεις, και λίγο συγύρισμα μπορεί να σου φτιάξει τη διάθεση.",
     "Feelings run close to the surface and are tied to belonging. Time with people who feel like home, even quietly, may do you more good than going out.",
     "Τα συναισθήματα είναι κοντά στην επιφάνεια και συνδέονται με την αίσθηση του ανήκειν. Ο χρόνος με ανθρώπους που σου θυμίζουν σπίτι, ακόμη και ήσυχα, μπορεί να σε ωφελήσει περισσότερο από μια έξοδο.",
     "If you can, work from a calm corner or finish tasks that support your base, such as paperwork or household matters. Keep work boundaries clear.",
     "Αν μπορείς, δούλεψε από μια ήρεμη γωνιά ή ολοκλήρωσε εκκρεμότητες που στηρίζουν τη βάση σου, όπως χαρτιά ή οικιακά θέματα. Κράτα καθαρά τα όρια της δουλειάς."),
    ("A lighter, more playful theme. Make a little room for enjoyment, a hobby or something you create just because it feels good.",
     "Ένα πιο ανάλαφρο, παιχνιδιάρικο θέμα. Άφησε λίγο χώρο για απόλαυση, ένα χόμπι ή κάτι που δημιουργείς απλώς επειδή σε ευχαριστεί.",
     "Warmth, flirtation and affection come more easily. Let yourself enjoy company without turning every moment into a test.",
     "Η ζεστασιά, το φλερτ και η τρυφερότητα έρχονται πιο εύκολα. Άφησε τον εαυτό σου να χαρεί την παρέα χωρίς να μετατρέπεις κάθε στιγμή σε τεστ.",
     "Creative ideas and presentation get a boost. Try a fresh angle on a routine task, and share a draft instead of polishing it endlessly.",
     "Οι δημιουργικές ιδέες και η παρουσίαση ενισχύονται. Δοκίμασε μια φρέσκια οπτική σε μια ρουτίνα και μοιράσου ένα προσχέδιο αντί να το γυαλίζεις επ' άπειρον."),
    ("Daily routines, small tasks and how you look after yourself come into focus. A modest improvement to one habit may serve you better than a big overhaul.",
     "Οι καθημερινές ρουτίνες, οι μικρές δουλειές και ο τρόπος που φροντίζεις τον εαυτό σου έρχονται στο προσκήνιο. Μια μικρή βελτίωση σε μία συνήθεια μπορεί να σε εξυπηρετήσει περισσότερο από μια μεγάλη ανατροπή.",
     "Care shows up in practical help. Notice who does small things for you, and do one small thing for someone else.",
     "Η φροντίδα εκφράζεται με πρακτική βοήθεια. Πρόσεξε ποιος κάνει μικρά πράγματα για σένα και κάνε κι εσύ ένα μικρό πράγμα για κάποιον άλλον.",
     "Good for organizing, clearing a backlog and fixing process details. Pace yourself and take proper breaks so you do not wear out by evening.",
     "Καλή μέρα για οργάνωση, για να τελειώσεις εκκρεμότητες και να διορθώσεις λεπτομέρειες. Πάρε τον χρόνο σου και κάνε σωστά διαλείμματα για να μην εξαντληθείς ως το βράδυ."),
    ("Other people stand in the foreground: partners, close friends and anyone you work with one-to-one. Notice what you learn about yourself through how you respond to them.",
     "Οι άλλοι βρίσκονται στο προσκήνιο: σύντροφοι, στενοί φίλοι και όσοι συνεργάζεσαι σε τετ-α-τετ. Πρόσεξε τι μαθαίνεις για τον εαυτό σου από τον τρόπο που τους απαντάς.",
     "A day for dialogue and balance in close relationships. Try to understand before you reply, and say what you need as clearly as what you give.",
     "Μια μέρα για διάλογο και ισορροπία στις στενές σχέσεις. Προσπάθησε να καταλάβεις πριν απαντήσεις και πες τι χρειάζεσαι τόσο καθαρά όσο και τι προσφέρεις.",
     "Partnerships, negotiations and agreements are in view. Aim for terms both sides can live with, and put important points in writing.",
     "Συνεργασίες, διαπραγματεύσεις και συμφωνίες βρίσκονται στο επίκεντρο. Στόχευσε σε όρους που αντέχουν και οι δύο πλευρές και γράψε τα σημαντικά σημεία."),
    ("A deeper, more private mood. Questions of trust, shared resources and what you are ready to let go of may surface, and they do not need to be solved in a day.",
     "Μια βαθύτερη, πιο ιδιωτική διάθεση. Ερωτήματα εμπιστοσύνης, κοινών πόρων και του τι είσαι έτοιμος/η να αφήσεις μπορεί να αναδυθούν, και δεν χρειάζεται να λυθούν σε μία μέρα.",
     "Emotions run intense and you may want real closeness rather than small talk. Share one honest thing at your own pace, and respect the other person's pace too.",
     "Τα συναισθήματα είναι έντονα και μπορεί να θέλεις πραγματική εγγύτητα αντί για επιφανειακή κουβέντα. Μοιράσου κάτι ειλικρινές με τον δικό σου ρυθμό και σεβάσου και τον ρυθμό του άλλου.",
     "Shared money, debts, joint projects and confidential matters need care. Read the fine print, keep details private where needed, and avoid power struggles.",
     "Κοινά χρήματα, οφειλές, κοινά έργα και εμπιστευτικά θέματα θέλουν προσοχή. Διάβασε τα μικρά γράμματα, κράτα ιδιωτικά όσα χρειάζεται και απόφυγε τα παιχνίδια εξουσίας."),
    ("You may feel drawn to the bigger picture: learning, travel, ideas and what you believe in. Look for something that widens your view, even a book or a documentary.",
     "Μπορεί να έλκεσαι από τη μεγαλύτερη εικόνα: μάθηση, ταξίδια, ιδέες και όσα πιστεύεις. Αναζήτησε κάτι που διευρύνει την οπτική σου, ακόμη και ένα βιβλίο ή ένα ντοκιμαντέρ.",
     "Shared curiosity and honest talk about values bring you closer. A different outlook in someone close may be interesting rather than threatening.",
     "Η κοινή περιέργεια και η ειλικρινής κουβέντα για τις αξίες φέρνουν τους ανθρώπους πιο κοντά. Μια διαφορετική οπτική σε κάποιον κοντινό σου μπορεί να είναι ενδιαφέρουσα και όχι απειλητική.",
     "Good for study, planning ahead, teaching or anything involving distance or other cultures. Keep promises realistic so enthusiasm does not outrun your time.",
     "Καλή μέρα για μελέτη, προγραμματισμό, διδασκαλία ή οτιδήποτε αφορά αποστάσεις και άλλους πολιτισμούς. Κράτα ρεαλιστικές τις υποσχέσεις ώστε ο ενθουσιασμός να μην ξεπεράσει τον χρόνο σου."),
    ("Your public role and long-term direction are in view. People may notice what you do, so it helps to be clear about what you want to be known for.",
     "Ο δημόσιος ρόλος και η μακροπρόθεσμη κατεύθυνσή σου βρίσκονται στο προσκήνιο. Οι άλλοι μπορεί να προσέξουν όσα κάνεις, γι' αυτό βοηθά να είσαι σαφής για το τι θέλεις να σε χαρακτηρίζει.",
     "Responsibilities may leave less room for softness. Make a small, deliberate moment for someone you care about so work does not take the whole day.",
     "Οι ευθύνες μπορεί να αφήνουν λιγότερο χώρο για τρυφερότητα. Φτιάξε μια μικρή, συνειδητή στιγμή για κάποιον που αγαπάς ώστε η δουλειά να μην πάρει όλη τη μέρα.",
     "A day for goals, reputation and taking a visible step. Pick one priority, do it well and let the result speak, rather than overextending.",
     "Μια μέρα για στόχους, φήμη και ένα ορατό βήμα. Διάλεξε μία προτεραιότητα, κάνε την καλά και άφησε το αποτέλεσμα να μιλήσει αντί να παρατεντώνεσαι."),
    ("Friends, groups and your hopes for the future come forward. Consider which communities actually support you and where you would like to contribute.",
     "Φίλοι, ομάδες και οι ελπίδες σου για το μέλλον έρχονται στο προσκήνιο. Σκέψου ποιες κοινότητες πραγματικά σε στηρίζουν και πού θα ήθελες να συνεισφέρεις.",
     "Warmth from friends may mean as much as romance today. Reach out to someone you have not spoken to in a while, with no agenda.",
     "Η ζεστασιά των φίλων μπορεί να σημαίνει σήμερα όσο και ο έρωτας. Απευθύνσου σε κάποιον που έχεις καιρό να μιλήσεις, χωρίς σκοπιμότητα.",
     "Networking, teamwork and shared goals are favoured. Ask for input, offer yours, and keep long-term plans flexible enough to adjust.",
     "Ευνοούνται το δικτύωμα, η ομαδική δουλειά και οι κοινοί στόχοι. Ζήτησε γνώμη, πρόσφερε τη δική σου και κράτα τα μακροπρόθεσμα σχέδια αρκετά ευέλικτα για προσαρμογές."),
    ("A quieter, inward theme. You may need more rest, solitude or time to process than usual, and that is a reasonable response rather than a problem to fix.",
     "Ένα πιο ήσυχο, εσωτερικό θέμα. Μπορεί να χρειάζεσαι περισσότερη ξεκούραση, μοναχικότητα ή χρόνο για να επεξεργαστείς, και αυτό είναι λογική ανταπόκριση, όχι πρόβλημα προς διόρθωση.",
     "Feelings may be hard to put into words. Give yourself some quiet first, then share what you can, and let others have their own space too.",
     "Τα συναισθήματα μπορεί να δυσκολεύονται να γίνουν λόγια. Δώσε στον εαυτό σου λίγη ησυχία πρώτα, μετά μοιράσου ό,τι μπορείς και άφησε και τους άλλους να έχουν τον χώρο τους.",
     "Behind-the-scenes work, planning and finishing quietly suit you better than the spotlight. Avoid taking on more than you can comfortably carry.",
     "Η δουλειά στο παρασκήνιο, ο σχεδιασμός και η ήσυχη ολοκλήρωση σου ταιριάζουν περισσότερο από τη δημοσιότητα. Απόφυγε να αναλάβεις περισσότερα απ' όσα αντέχεις άνετα."),
]

# per Moon sign (index = sign order Aries..Pisces): EN / EL adjectives for "the Moon is ..."
MOON_MOOD = [
    ('quick, direct and eager to act', 'γρήγορη, άμεση και πρόθυμη για δράση'),
    ('steady, sensual and in need of comfort', 'σταθερή, αισθησιακή και με ανάγκη για άνεση'),
    ('curious, talkative and restless', 'περίεργη, ομιλητική και ανήσυχη'),
    ('protective, sensitive and drawn to home', 'προστατευτική, ευαίσθητη και με έλξη προς το σπίτι'),
    ('warm, expressive and wanting appreciation', 'ζεστή, εκφραστική και με ανάγκη για εκτίμηση'),
    ('practical, detail-minded and self-critical', 'πρακτική, προσεκτική στις λεπτομέρειες και αυστηρή με τον εαυτό της'),
    ('sociable, harmony-seeking and drawn to fairness', 'κοινωνική, με επιδίωξη αρμονίας και έλξη προς τη δικαιοσύνη'),
    ('intense, private and drawn to depth', 'έντονη, ιδιωτική και με έλξη προς το βάθος'),
    ('optimistic, restless and hungry for meaning', 'αισιόδοξη, ανήσυχη και διψασμένη για νόημα'),
    ('serious, disciplined and goal-minded', 'σοβαρή, πειθαρχημένη και προσανατολισμένη στους στόχους'),
    ('detached, original and independent', 'αποστασιοποιημένη, πρωτότυπη και ανεξάρτητη'),
    ('dreamy, empathic and quick to absorb the mood around it', 'ονειροπόλα, ενσυναισθητική και δεκτική στη διάθεση του περιβάλλοντος'),
]

# per Moon phase (same order as PHASES): what the phase symbolically invites
PHASE_INVITE = [
    ('This is a time for quiet intentions and fresh starts rather than big pushes.',
     'Είναι ώρα για ήσυχες προθέσεις και νέες αρχές, όχι για μεγάλες πιέσεις.'),
    ('This is a time for first small steps on something new.',
     'Είναι ώρα για τα πρώτα μικρά βήματα σε κάτι καινούριο.'),
    ('This is a time for decisions and for dealing with small obstacles.',
     'Είναι ώρα για αποφάσεις και για την αντιμετώπιση μικρών εμποδίων.'),
    ('This is a time for refining and adjusting before you show the result.',
     'Είναι ώρα για βελτίωση και προσαρμογές πριν δείξεις το αποτέλεσμα.'),
    ('This is a time when feelings and results are easier to see clearly.',
     'Είναι ώρα που τα συναισθήματα και τα αποτελέσματα φαίνονται πιο καθαρά.'),
    ('This is a time for sharing what you have learned and for gratitude.',
     'Είναι ώρα για να μοιραστείς όσα έμαθες και να εκφράσεις ευγνωμοσύνη.'),
    ('This is a time to let go of what no longer works.',
     'Είναι ώρα να αφήσεις ό,τι δεν λειτουργεί πια.'),
    ('This is a time to rest, reflect and close things gently.',
     'Είναι ώρα για ξεκούραση, στοχασμό και ήπιο κλείσιμο εκκρεμοτήτων.'),
]

NO_ASPECT = ('There are no strong lunar aspects today, so a steady rhythm will serve you better than pushing for results.',
             'Δεν υπάρχουν έντονες όψεις της Σελήνης σήμερα, άρα ένας σταθερός ρυθμός θα σε εξυπηρετήσει καλύτερα από το να πιέζεις για αποτελέσματα.')
TIP_EASE = ("Today's easy flow suits {theme}: take one step there while it feels natural.",
            'Η ομαλή ροή της ημέρας ταιριάζει με {theme}: κάνε ένα βήμα εκεί όσο έρχεται φυσικά.')
TIP_TENSE = ('A little friction around {theme} is a cue to slow down: pause before reacting and choose your words.',
             'Η μικρή τριβή γύρω από {theme} είναι ένδειξη να επιβραδύνεις: κάνε μια παύση πριν αντιδράσεις και διάλεξε τις λέξεις σου.')
TIP_BLEND = ('Your mood meets {theme} today: give this theme some deliberate attention.',
             'Η διάθεσή σου συναντά σήμερα {theme}: δώσε λίγη συνειδητή προσοχή σε αυτό το θέμα.')
WELLBEING = ('With the Moon {mood}, notice how your energy rises and dips through the day. '
             'Planning around your energy rather than against it tends to work better than pushing.',
             'Με τη Σελήνη {mood}, πρόσεξε πώς ανεβαίνει και πέφτει η ενέργειά σου μέσα στην ημέρα. '
             'Να οργανώνεσαι σύμφωνα με την ενέργειά σου και όχι ενάντια σε αυτήν συνήθως αποδίδει περισσότερο από την πίεση.')
VENUS_LINE = ('Venus is in {house}: your relationships and values ask for care there.{retro}',
              'Η Αφροδίτη βρίσκεται στον {house}: εκεί οι σχέσεις και οι αξίες σου ζητούν φροντίδα.{retro}')
MARS_LINE = ('Mars is in {house}: this is where your energy and initiative are most likely to go.{retro}',
             'Ο Άρης βρίσκεται στον {house}: εκεί κατευθύνεται πιο εύκολα η ενέργεια και η πρωτοβουλία σου.{retro}')
RETRO = {
    'en': ' It is retrograde, so revisiting works better than starting something new.',
    'el': {'Venus': ' Είναι ανάδρομη, άρα η επανεξέταση ταιριάζει περισσότερο από ένα νέο ξεκίνημα.',
           'Mars': ' Είναι ανάδρομος, άρα η επανεξέταση ταιριάζει περισσότερο από ένα νέο ξεκίνημα.'},
}


# Sign qualities and two element notes, paraphrased from Max Heindel, Simplified Scientific
# Astrology (1919): Cardinal p. 100, Common p. 101, Fixed p. 118, Airy p. 94, Watery p. 174.
# Heindel gives no comparable note for Fire or Earth, so none is written for them.
QUALITY = [  # (EN, EL) by sign index % 3: Cardinal, Fixed, Common
 ('The Moon is in a Cardinal sign, which Heindel describes as promoting activity: it favours getting things moving rather than waiting.',
  'Η Σελήνη βρίσκεται σε καρδινάλιο ζώδιο, που ο Heindel περιγράφει ως ζώδιο που ενισχύει τη δράση: ευνοεί το να βάλεις κάτι σε κίνηση αντί να περιμένεις.'),
 ('The Moon is in a Fixed sign, which Heindel links with steadiness and perseverance: it favours finishing what you already began.',
  'Η Σελήνη βρίσκεται σε σταθερό ζώδιο, που ο Heindel συνδέει με σταθερότητα και επιμονή: ευνοεί το να ολοκληρώσεις ό,τι έχεις ήδη ξεκινήσει.'),
 ('The Moon is in a Common sign, which Heindel calls flexible and changeable: it favours adapting plans, and it asks you not to scatter your effort.',
  'Η Σελήνη βρίσκεται σε κοινό ζώδιο, που ο Heindel χαρακτηρίζει ευέλικτο και μεταβλητό: ευνοεί την προσαρμογή των σχεδίων και ζητά να μη διασκορπίσεις την προσπάθειά σου.'),
]
ELEMENT_NOTE = {  # by sign index % 4: 2 = Air, 3 = Water
 2: ('It is an Airy sign, whose influence Heindel calls mostly mental and intellectual, so thinking and talking things through come easily.',
     'Είναι ζώδιο του Αέρα, που ο Heindel λέει ότι επιδρά κυρίως στη σκέψη και τον νου, άρα η σκέψη και η συζήτηση βγαίνουν πιο εύκολα.'),
 3: ('It is a Watery sign, which Heindel associates with the psychic, feeling side of life, so mood and sensitivity may count for more than usual.',
     'Είναι ζώδιο του Νερού, που ο Heindel συνδέει με την ψυχική, συναισθηματική πλευρά της ζωής, άρα η διάθεση και η ευαισθησία μπορεί να μετρούν περισσότερο.'),
}
