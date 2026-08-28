"""
English / Greek translations for the UI and generated PDF reports.
Keys stay in English internally (area codes, planet/sign names) --
only display strings are translated.
"""

TRANSLATIONS = {
    "en": {
        "app_title": "Vimshottari Transit Monitor",
        "app_subtitle": "Sidereal (Lahiri) · Whole Sign houses · raw, uncalibrated activation scores",
        "birth_data": "Birth Data",
        "date": "Date",
        "time_local": "Time (local, 24h)",
        "utc_offset": "UTC offset (hours)",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "forecast_months": "Forecast months",
        "run_forecast": "Run forecast",
        "download_pdf": "Download PDF report",
        "natal_chart": "Natal Chart",
        "ascendant": "Ascendant",
        "current_dasha": "Current Dasha",
        "mahadasha": "Mahadasha",
        "antardasha": "Antardasha",
        "monthly_scores": "Monthly Activation Scores",
        "area": "Area",
        "disclaimer": (
            "These are raw transit-pressure scores derived from house activation and "
            "dasha weighting — not run through outcome calibration. Treat as where "
            "astrological pressure clusters, not as a prediction, until logged against "
            "real events."
        ),
        "report_title": "5-Year Forecast Report",
        "report_subtitle_prefix": "Coverage",
        "birth_particulars": "Birth Particulars",
        "planet_positions": "Planet Positions",
        "house": "House",
        "sign": "Sign",
        "nakshatra": "Nakshatra",
        "retrograde_short": "R",
        "house_change_calendar": "Major Planet House-Change Calendar",
        "date_col": "Date",
        "planet_col": "Planet",
        "change_col": "Change",
        "analysis_title": "Second-Opinion Analysis",
        "question_label": "Your question",
        "question_placeholder": "e.g. What does this look like for my career this year?",
        "ask_button": "Ask Claude & ChatGPT",
        "preset_career": "Career outlook",
        "preset_annual": "Annual forecast",
        "preset_love": "Love / relationships",
        "preset_money": "Money outlook",
        "claude_label": "Claude",
        "chatgpt_label": "ChatGPT",
        "analysis_note": (
            "Both models see the same underlying raw scores and are asked "
            "independently — treat them as two separate second opinions, "
            "not a consensus."
        ),
        "areas": {
            "career": "Career",
            "money": "Money",
            "sudden_gain": "Sudden Gain",
            "financial_risk": "Financial Risk",
            "business": "Business",
            "love": "Love",
            "marriage_commitment": "Marriage / Commitment",
            "sex_chemistry": "Sex / Chemistry",
            "travel_foreign": "Travel / Foreign",
            "home_property": "Home / Property",
            "luxury_assets": "Luxury Assets",
            "major_change": "Major Change",
            "socialization": "Socialization",
            "earned_income": "Earned Income",
            "claims_settlements": "Claims / Settlements",
            "external_money": "External Money",
            "spending_loss_risk": "Spending / Loss Risk",
            "social_isolation": "Social Isolation",
            "social_friction": "Social Friction",
        },
        "planets": {
            "Sun": "Sun", "Moon": "Moon", "Mercury": "Mercury", "Venus": "Venus",
            "Mars": "Mars", "Jupiter": "Jupiter", "Saturn": "Saturn",
            "Rahu": "Rahu", "Ketu": "Ketu",
        },
        "signs": {
            "Aries": "Aries", "Taurus": "Taurus", "Gemini": "Gemini", "Cancer": "Cancer",
            "Leo": "Leo", "Virgo": "Virgo", "Libra": "Libra", "Scorpio": "Scorpio",
            "Sagittarius": "Sagittarius", "Capricorn": "Capricorn", "Aquarius": "Aquarius",
            "Pisces": "Pisces",
        },
    },
    "el": {
        "app_title": "Παρακολούθηση Διαβατικών Περιόδων (Βιμσοτάρι)",
        "app_subtitle": "Sidereal (Lahiri) · Οίκοι Ολόκληρου Ζωδίου · ακατέργαστες, μη βαθμονομημένες τιμές ενεργοποίησης",
        "birth_data": "Στοιχεία Γέννησης",
        "date": "Ημερομηνία",
        "time_local": "Ώρα (τοπική, 24ωρη)",
        "utc_offset": "Διαφορά από UTC (ώρες)",
        "latitude": "Γεωγραφικό πλάτος",
        "longitude": "Γεωγραφικό μήκος",
        "forecast_months": "Μήνες πρόβλεψης",
        "run_forecast": "Εκτέλεση πρόβλεψης",
        "download_pdf": "Λήψη αναφοράς PDF",
        "natal_chart": "Γενέθλιος Χάρτης",
        "ascendant": "Ωροσκόπος",
        "current_dasha": "Τρέχουσα Δάσα",
        "mahadasha": "Μαχαντάσα",
        "antardasha": "Ανταρντάσα",
        "monthly_scores": "Μηνιαίες Τιμές Ενεργοποίησης",
        "area": "Τομέας",
        "disclaimer": (
            "Πρόκειται για ακατέργαστες τιμές διαβατικής πίεσης, βασισμένες στην "
            "ενεργοποίηση οίκων και στη στάθμιση δάσα — δεν έχουν περάσει από "
            "βαθμονόμηση με πραγματικά αποτελέσματα. Αντιμετωπίστε τις ως ένδειξη "
            "συγκέντρωσης αστρολογικής πίεσης, όχι ως πρόβλεψη, μέχρι να καταγραφούν "
            "σε σχέση με πραγματικά γεγονότα."
        ),
        "report_title": "Αναφορά Πρόβλεψης 5ετίας",
        "report_subtitle_prefix": "Περίοδος",
        "birth_particulars": "Στοιχεία Γέννησης",
        "planet_positions": "Θέσεις Πλανητών",
        "house": "Οίκος",
        "sign": "Ζώδιο",
        "nakshatra": "Νακσάτρα",
        "retrograde_short": "Α",
        "house_change_calendar": "Ημερολόγιο Αλλαγής Οίκων Αργών Πλανητών",
        "date_col": "Ημερομηνία",
        "planet_col": "Πλανήτης",
        "change_col": "Αλλαγή",
        "analysis_title": "Ανάλυση Δεύτερης Γνώμης",
        "question_label": "Η ερώτησή σας",
        "question_placeholder": "π.χ. Πώς διαμορφώνεται η καριέρα μου φέτος;",
        "ask_button": "Ρώτησε Claude & ChatGPT",
        "preset_career": "Προοπτική καριέρας",
        "preset_annual": "Ετήσια πρόβλεψη",
        "preset_love": "Έρωτας / σχέσεις",
        "preset_money": "Προοπτική χρημάτων",
        "claude_label": "Claude",
        "chatgpt_label": "ChatGPT",
        "analysis_note": (
            "Και τα δύο μοντέλα βλέπουν τα ίδια ακατέργαστα δεδομένα και "
            "ερωτώνται ανεξάρτητα — αντιμετωπίστε τα ως δύο ξεχωριστές "
            "δεύτερες γνώμες, όχι ως κοινή συναίνεση."
        ),
        "areas": {
            "career": "Καριέρα",
            "money": "Χρήμα",
            "sudden_gain": "Ξαφνικό Κέρδος",
            "financial_risk": "Οικονομικός Κίνδυνος",
            "business": "Επιχείρηση",
            "love": "Έρωτας",
            "marriage_commitment": "Γάμος / Δέσμευση",
            "sex_chemistry": "Σεξ / Χημεία",
            "travel_foreign": "Ταξίδι / Εξωτερικό",
            "home_property": "Σπίτι / Ακίνητα",
            "luxury_assets": "Πολυτελή Περιουσιακά Στοιχεία",
            "major_change": "Μεγάλη Αλλαγή",
            "socialization": "Κοινωνικοποίηση",
            "earned_income": "Εισόδημα από Εργασία",
            "claims_settlements": "Απαιτήσεις / Διακανονισμοί",
            "external_money": "Εξωτερικό Χρήμα",
            "spending_loss_risk": "Κίνδυνος Δαπανών / Απώλειας",
            "social_isolation": "Κοινωνική Απομόνωση",
            "social_friction": "Κοινωνική Τριβή",
        },
        "planets": {
            "Sun": "Ήλιος", "Moon": "Σελήνη", "Mercury": "Ερμής", "Venus": "Αφροδίτη",
            "Mars": "Άρης", "Jupiter": "Δίας", "Saturn": "Κρόνος",
            "Rahu": "Ράχου", "Ketu": "Κέτου",
        },
        "signs": {
            "Aries": "Κριός", "Taurus": "Ταύρος", "Gemini": "Δίδυμοι", "Cancer": "Καρκίνος",
            "Leo": "Λέων", "Virgo": "Παρθένος", "Libra": "Ζυγός", "Scorpio": "Σκορπιός",
            "Sagittarius": "Τοξότης", "Capricorn": "Αιγόκερως", "Aquarius": "Υδροχόος",
            "Pisces": "Ιχθύες",
        },
    },
}


def get_translations(lang):
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])


def translate_area_scores(monthly_scores, lang):
    """Rewrite area keys in a monthly_scores dict to the localized label."""
    labels = get_translations(lang)["areas"]
    out = {}
    for month, areas in monthly_scores.items():
        out[month] = {labels.get(k, k): v for k, v in areas.items()}
    return out
