"""Historical-source guidance for the LLM interpretation layer.

These notes summarize principles from the user-supplied historical astrology
books. They are NOT a replacement for the deterministic sidereal/Lahiri
calculations and must never silently override the Vedic chart data.

The sources mix traditions (classical Western, heliocentric, and material that
references Indian/Jataka concepts), so they are used as a comparative
interpretive corpus rather than as one mathematically unified doctrine.
"""

SOURCE_GUIDANCE = {
    "en": """
SOURCE-GUIDED INTERPRETIVE RULES:
1. Treat the deterministic sidereal/Lahiri chart, Vimshottari timing and
   calculated transit data as primary evidence. Historical source material is
   secondary interpretive context only.
2. Do not infer an event from one isolated transit. Evaluate the natal/radix
   condition, house relevance, active dasha timing, and corroborating
   indications together.
3. Aspect exactness matters: when geometric aspects are supplied, tighter
   orbs carry more interpretive weight than loose ones.
4. Planetary condition matters before judging a transit: distinguish own-sign,
   exalted, debilitated, angular/trinal/difficult-house placement,
   retrograde/motional condition, and relevant aspects.
5. Use a strength checklist inspired by the historical source discussion of
   aspect strength, positional strength, natural strength, motional strength,
   directional strength and temporal strength. Only discuss dimensions that
   the supplied data actually supports.
6. House activation can be more informative than a bare statement that a
   transiting planet crosses a natal degree. Explain which life area is being
   activated and why.
7. The uploaded heliocentric source belongs to a different system. Do not mix
   heliocentric positions into the geocentric Lahiri calculations unless a
   separate heliocentric comparison is explicitly requested.
8. Historical medical-astrology material may be used only as historical
   context. Never use astrology to diagnose illness, predict death, replace
   medical care, or make medical claims.
9. Never turn historical statements into certainty. Use language such as
   "supports", "adds weight", "is consistent with", "raises attention to", or
   "is a secondary indication".
""".strip(),
    "el": """
ΚΑΝΟΝΕΣ ΕΡΜΗΝΕΙΑΣ ΜΕ ΒΑΣΗ ΤΙΣ ΙΣΤΟΡΙΚΕΣ ΠΗΓΕΣ:
1. Πρωτεύον τεκμήριο είναι ο υπολογισμένος sidereal/Lahiri χάρτης, ο
   χρονισμός Vimshottari και τα υπολογισμένα transit δεδομένα. Οι ιστορικές
   πηγές λειτουργούν μόνο ως δευτερογενές ερμηνευτικό πλαίσιο.
2. Μην εξάγεις γεγονός από μία μεμονωμένη διέλευση. Συνδύαζε την κατάσταση
   του γενέθλιου χάρτη, τον σχετικό οίκο, την ενεργή dasha και τυχόν
   επιβεβαιωτικές ενδείξεις.
3. Η ακρίβεια της όψης έχει σημασία: όταν δίνονται γεωμετρικές όψεις, όσο
   μικρότερο το orb τόσο μεγαλύτερο το ερμηνευτικό βάρος.
4. Αξιολόγησε πρώτα την κατάσταση του πλανήτη: δικό του ζώδιο, έξαρση,
   πτώση/εξασθένηση, γωνιακή/τριγωνική/δύσκολη θέση, ανάδρομη κίνηση και
   σχετικές όψεις.
5. Χρησιμοποίησε ως checklist ισχύος: ισχύ όψης, θέσης, φυσική, κινητική,
   κατευθυντική και χρονική ισχύ. Αν τα δεδομένα δεν υποστηρίζουν κάποια
   διάσταση, μην την επινοείς.
6. Η ενεργοποίηση οίκου μπορεί να είναι πιο χρήσιμη από μια απλή αναφορά ότι
   ένας διελαύνων πλανήτης περνά από μία γενέθλια μοίρα. Εξήγησε ποιος τομέας
   ζωής ενεργοποιείται και γιατί.
7. Η heliocentric πηγή ανήκει σε διαφορετικό σύστημα. Μην αναμιγνύεις
   ηλιοκεντρικές θέσεις με τους γεωκεντρικούς Lahiri υπολογισμούς, εκτός αν
   ζητηθεί ρητά ξεχωριστή συγκριτική ανάλυση.
8. Το υλικό medical astrology χρησιμοποιείται μόνο ως ιστορικό πλαίσιο.
   Ποτέ διάγνωση, πρόβλεψη θανάτου, αντικατάσταση ιατρικής φροντίδας ή
   ιατρικός ισχυρισμός μέσω αστρολογίας.
9. Μην μετατρέπεις ιστορικές διατυπώσεις σε βεβαιότητες. Προτίμησε
   "ενισχύει", "προσθέτει βάρος", "είναι συμβατό με", "αυξάνει την προσοχή"
   ή "αποτελεί δευτερογενή ένδειξη".
""".strip(),
}

def get_source_guidance(lang="en"):
    return SOURCE_GUIDANCE.get(lang, SOURCE_GUIDANCE["en"])
