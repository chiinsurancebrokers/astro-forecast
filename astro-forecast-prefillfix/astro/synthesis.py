"""
Turns the raw transit/dasha data into a compact, grounded context, then
runs a two-stage pipeline: Claude writes the primary synthesis answering
the person's question, then ChatGPT reviews that specific answer against
the same data and verifies it -- checking whether the months/dasha
periods/transits it cites actually appear in the data, flagging anything
unsupported or overstated, and giving a short verdict. This is a review
step, not a second independent opinion: ChatGPT sees Claude's answer and
is asked to check it, not to write its own from scratch.

Requires ANTHROPIC_API_KEY / OPENAI_API_KEY as environment variables
(set as Railway service variables in production). Missing keys degrade
gracefully: if Claude's key is missing there is nothing to verify, so
verification is skipped with an explanatory error; if only ChatGPT's key
is missing, the primary synthesis still returns normally.

Each SDK client gets an explicit request timeout so a slow provider can't
stall the whole response indefinitely.
"""
import os

REQUEST_TIMEOUT_SECONDS = 45

DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
DEFAULT_OPENAI_MODEL = "gpt-4o"

SYNTHESIS_SYSTEM_PROMPT = {
    "en": (
        "You are reading output from a sidereal (Lahiri) Vedic astrology "
        "transit-scoring tool for a client. The scores are RAW and "
        "UNCALIBRATED -- house-activation and dasha-weighted heuristics, "
        "never validated against real outcomes. Do not present them as "
        "settled predictions. Answer the client's specific question using "
        "the data provided: name the concrete months, dasha periods, or "
        "planetary transits that support each point, and be explicit "
        "about where the data is genuinely suggestive versus thin. Keep a "
        "grounded, practical tone -- this is a working analysis for "
        "someone using the tool to plan, not a mystical reading. Answer "
        "in English."
    ),
    "el": (
        "Διαβάζεις την έξοδο ενός εργαλείου βαθμολόγησης διαβατικών "
        "περιόδων Βεδικής αστρολογίας (sidereal, Lahiri) για έναν πελάτη. "
        "Οι τιμές είναι ΑΚΑΤΕΡΓΑΣΤΕΣ και ΜΗ ΒΑΘΜΟΝΟΜΗΜΕΝΕΣ -- ευρετικές, "
        "βασισμένες σε ενεργοποίηση οίκων και στάθμιση δάσα, χωρίς "
        "επαλήθευση σε πραγματικά αποτελέσματα. Μην τις παρουσιάζεις ως "
        "βέβαιες προβλέψεις. Απάντησε στη συγκεκριμένη ερώτηση του πελάτη "
        "χρησιμοποιώντας τα δεδομένα που δίνονται: ανέφερε συγκεκριμένους "
        "μήνες, περιόδους δάσα ή διαβατικές θέσεις πλανητών που "
        "υποστηρίζουν κάθε σημείο, και να είσαι σαφής για το πού τα "
        "δεδομένα είναι πράγματι ενδεικτικά και πού είναι αδύναμα. "
        "Διατήρησε προσγειωμένο, πρακτικό τόνο. Απάντησε στα Ελληνικά."
    ),
}

VERIFICATION_SYSTEM_PROMPT = {
    "en": (
        "You are fact-checking another AI's astrology forecast answer "
        "against the raw data it was given. You will receive the same "
        "DATA plus that ANSWER. Your job is verification, not a fresh "
        "opinion: check every month, dasha period, or transit the answer "
        "cites and confirm it actually appears in the data as claimed; "
        "flag any claim that is not supported by the data, any figure "
        "that's misquoted, and any place the answer states something "
        "with more certainty than raw, uncalibrated scores justify. "
        "Structure your reply as: a one-line verdict (well-grounded / "
        "minor issues / significant issues), then a short list of "
        "specific corrections or confirmations, then, only if truly "
        "warranted, one or two points the answer missed that the data "
        "clearly supports. Do not write a new independent forecast. "
        "Answer in English."
    ),
    "el": (
        "Ελέγχεις την απάντηση πρόβλεψης ενός άλλου AI σε σχέση με τα "
        "ακατέργαστα δεδομένα που του δόθηκαν. Θα λάβεις τα ίδια "
        "ΔΕΔΟΜΕΝΑ και την ΑΠΑΝΤΗΣΗ εκείνη. Η δουλειά σου είναι "
        "επαλήθευση, όχι μια νέα ανεξάρτητη γνώμη: έλεγξε κάθε μήνα, "
        "περίοδο δάσα ή διαβατική θέση που αναφέρει η απάντηση και "
        "επιβεβαίωσε ότι όντως εμφανίζεται στα δεδομένα όπως "
        "υποστηρίζεται· επισήμανε κάθε ισχυρισμό που δεν στηρίζεται στα "
        "δεδομένα, κάθε αριθμό που αναφέρεται λανθασμένα, και κάθε "
        "σημείο όπου η απάντηση εκφράζεται με μεγαλύτερη βεβαιότητα από "
        "όση δικαιολογούν ακατέργαστες, μη βαθμονομημένες τιμές. Δόμησε "
        "την απάντησή σου ως εξής: μία γραμμή με τελική κρίση "
        "(καλά τεκμηριωμένη / μικρά ζητήματα / σημαντικά ζητήματα), "
        "έπειτα μια σύντομη λίστα συγκεκριμένων διορθώσεων ή "
        "επιβεβαιώσεων, και τέλος, μόνο αν όντως δικαιολογείται, ένα ή "
        "δύο σημεία που παρέλειψε η απάντηση αν και τα δεδομένα τα "
        "υποστηρίζουν σαφώς. Μη γράψεις μια νέα ανεξάρτητη πρόβλεψη. "
        "Απάντησε στα Ελληνικά."
    ),
}


def _top_and_bottom(area_scores, n=3):
    ranked = sorted(area_scores.items(), key=lambda kv: kv[1], reverse=True)
    peaks = ranked[:n]
    troughs = sorted(ranked[-n:], key=lambda kv: kv[1])
    avg = round(sum(v for _, v in area_scores.items()) / len(area_scores), 1)
    return avg, peaks, troughs


def build_context(chart, dasha_info, monthly_scores, house_events, lang="en"):
    """Compact, information-dense text summary -- not the full monthly table."""
    asc = chart["ascendant"]
    lines = []
    lines.append(f"Ascendant: {asc['sign']} {asc['sign_deg']:.2f} degrees.")
    lines.append("Natal planets (sign, house, nakshatra):")
    for name, p in chart["planets"].items():
        retro = " retrograde" if p["retrograde"] else ""
        lines.append(f"  {name}: {p['sign']} {p['sign_deg']:.2f}°, house {p['house']}, "
                      f"{p['nakshatra']}{retro}")
    lines.append(f"Current Mahadasha: {dasha_info.get('current_mahadasha')}, "
                  f"current Antardasha: {dasha_info.get('current_antardasha')}.")

    months = list(monthly_scores.keys())
    if months:
        lines.append(f"Forecast window: {months[0]} to {months[-1]} "
                      f"({len(months)} months). All scores are 0-100, raw/uncalibrated.")
        area_keys = list(monthly_scores[months[0]].keys())
        lines.append("Per-area summary (average, top peak months, top trough months):")
        for area in area_keys:
            series = {m: monthly_scores[m][area] for m in months}
            avg, peaks, troughs = _top_and_bottom(series)
            peak_str = ", ".join(f"{m}={v}" for m, v in peaks)
            trough_str = ", ".join(f"{m}={v}" for m, v in troughs)
            lines.append(f"  {area}: avg={avg}, peaks=[{peak_str}], troughs=[{trough_str}]")

    if house_events:
        lines.append("Major slow-planet house changes in this window:")
        for ev in house_events:
            retro = " (retrograde)" if ev["retrograde"] else ""
            lines.append(f"  {ev['date']}: {ev['planet']} {ev['from_sign']} -> "
                          f"{ev['to_sign']}{retro}")

    return "\n".join(lines)


def call_claude_synthesis(question, context, lang="en"):
    """Primary synthesis: Claude answers the person's question from the data."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY is not set."}
    model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS)
        resp = client.messages.create(
            model=model,
            max_tokens=1400,
            system=SYNTHESIS_SYSTEM_PROMPT.get(lang, SYNTHESIS_SYSTEM_PROMPT["en"]),
            messages=[{
                "role": "user",
                "content": f"DATA:\n{context}\n\nQUESTION:\n{question}",
            }],
        )
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        return {"model": model, "text": text}
    except Exception as e:
        return {"error": str(e)}


def call_chatgpt_verification(question, context, primary_text, lang="en"):
    """Verification pass: ChatGPT checks Claude's specific answer against the data."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY is not set."}
    model = os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS)
        resp = client.chat.completions.create(
            model=model,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": VERIFICATION_SYSTEM_PROMPT.get(lang, VERIFICATION_SYSTEM_PROMPT["en"])},
                {"role": "user", "content": (
                    f"DATA:\n{context}\n\nQUESTION:\n{question}\n\nANSWER TO VERIFY:\n{primary_text}"
                )},
            ],
        )
        text = resp.choices[0].message.content
        return {"model": model, "text": text}
    except Exception as e:
        return {"error": str(e)}


def synthesize(question, chart, dasha_info, monthly_scores, house_events, lang="en"):
    context = build_context(chart, dasha_info, monthly_scores, house_events, lang)
    primary = call_claude_synthesis(question, context, lang)

    if primary.get("error"):
        no_verify_msg = {
            "en": "Skipped: no primary synthesis was produced to verify.",
            "el": "Παραλείφθηκε: δεν παρήχθη πρωτεύουσα σύνθεση για επαλήθευση.",
        }
        verification = {"error": no_verify_msg.get(lang, no_verify_msg["en"])}
    else:
        verification = call_chatgpt_verification(question, context, primary["text"], lang)

    return {
        "question": question,
        "primary": primary,
        "verification": verification,
    }
